#!/usr/bin/env python3
"""Phase P.1.3 — Skill OS Optimization Loop.

持续优化循环的数据驱动器（人在环中，绝不自动执行变更）：

  输入:  usage 画像 (P.1.2) + health engine + registry v1.1
  规则:  R1 DEGRADED/FAILED 技能        → P1 MAINTENANCE_REQUIRED
         R2 长期未用 (90d+ 或从未) 且非 core → P3 ARCHIVE_CANDIDATE (每轮限量)
         R3 deprecated 但仍被使用       → P4 MERGE_REVIEW (提醒迁移到 canonical)
         R4 kernel 执行失败率 >20%      → P2 HEALTH_REVIEW
  输出:  ~/.hermes/runtime/governance/proposals/proposals.jsonl (status=pending)
         production/analytics/optimization-YYYY-MM-DD.md

安全边界:
  - 提案 requires_approval=True，只落 pending，等待人工 approve/reject
  - 每轮 P3 提案上限 5 条（防提案洪水）
  - core scope 技能永不进入 P3 归档候选
  - 幂等: 同一技能同类型已有 pending 提案则跳过
"""

import glob
import json
import os
import sys
import time

KERNEL = os.path.expanduser("~/.hermes/kernel")
REPO = os.path.expanduser("~/Terence-Agent")
ANALYTICS = os.path.join(REPO, "production", "analytics")

sys.path.insert(0, KERNEL)
from governance.proposal_engine import generate  # noqa: E402
from governance.proposal_store import create, list_all  # noqa: E402
from health.health_engine import evaluate  # noqa: E402
from telemetry.event_store import query_events  # noqa: E402

P3_BATCH_LIMIT = 5
IDLE_DAYS_THRESHOLD = 90


def latest_usage_report():
    files = sorted(glob.glob(os.path.join(ANALYTICS, "skill-usage-*.json")))
    if not files:
        raise FileNotFoundError("先运行 skill_usage_collector.py 生成画像")
    return json.load(open(files[-1]))


def pending_index():
    """幂等索引: {(skill_id, type)} 已有 pending 提案。"""
    return {(p.get("skill_id"), p.get("type"))
            for p in list_all(status="pending")}


def ever_proposed_index():
    """历史索引: {(skill_id, type)} 曾出现过的提案（含 approved/rejected）。
    用于 R2/R3 — 人已裁决过的归档/迁移候选不反复重提；
    R1/R4 健康类不用此索引（新降级应可再触发）。"""
    return {(p.get("skill_id"), p.get("type")) for p in list_all()}


def main():
    today = time.strftime("%Y-%m-%d")
    usage = latest_usage_report()
    profiles = {p["name"]: p for p in usage["profiles"]}
    existing = pending_index()
    ever = ever_proposed_index()
    created, skipped = [], []

    def submit(skill_id, ptype, reason, evidence, dedupe_history=False):
        if (skill_id, ptype) in existing:
            skipped.append((skill_id, ptype, "已有 pending 同类提案"))
            return
        if dedupe_history and (skill_id, ptype) in ever:
            skipped.append((skill_id, ptype, "历史已裁决过同类提案"))
            return
        prop = generate(skill_id, ptype,
                        namespace=profiles.get(skill_id, {}).get("namespace", ""),
                        evidence=evidence, reason=reason)
        create(prop)
        created.append(prop)
        existing.add((skill_id, ptype))

    # ── R1: 健康降级 → P1 ──
    active_skills = sorted({e.get("skill_id") for e in query_events(limit=10000)
                            if e.get("skill_id")})
    for sid in active_skills:
        h = evaluate(sid)
        if h["state"] in ("DEGRADED", "FAILED"):
            submit(sid, "P1",
                   f"health={h['state']} score={h['score']} (R1 健康降级)",
                   {"rule": "R1", "health": h["state"], "score": h["score"],
                    "metrics": {k: h["metrics"].get(k) for k in
                                ("execution_count", "success_rate", "failure_count")}})

    # ── R4: kernel 失败率 >20% ──
    for sid in active_skills:
        p = profiles.get(sid)
        if not p:
            continue
        total = p["kernel_exec_count"]
        if total >= 3 and p["kernel_failed"] / total > 0.2:
            submit(sid, "P2",
                   f"kernel 失败率 {p['kernel_failed']}/{total} (R4)",
                   {"rule": "R4", "exec": total, "failed": p["kernel_failed"]})

    # ── R3: deprecated 仍活跃 → P4 ──
    for p in usage["profiles"]:
        if p["lifecycle"] == "deprecated" and p["total_activity"] > 0:
            submit(p["name"], "P4",
                   f"deprecated 技能仍有 {p['total_activity']} 次活动，需引导迁移至 canonical (R3)",
                   {"rule": "R3", "activity": p["total_activity"],
                    "use_count": p["use_count"]}, dedupe_history=True)

    # ── R2: 长期未用 → P3 (队列限量, 排除 core, 排除 deprecated 已有 P4) ──
    # 语义: pending P3 提案总量 ≤ P3_BATCH_LIMIT（防提案洪水），
    # 而非每轮新增 5 条 —— 否则重复运行会绕过限流持续超发。
    p3_count = sum(1 for (sid, t) in existing if t == "P3")
    candidates = [p for p in usage["profiles"]
                  if p["scope"] != "core"
                  and p["lifecycle"] not in ("deprecated", "archived")
                  and (p["total_activity"] == 0 and p["view_count"] == 0
                       or (p["days_idle"] or 0) >= IDLE_DAYS_THRESHOLD)]
    # 最没有存在感的排前面 (0 view 优先)
    candidates.sort(key=lambda p: (p["view_count"], p["total_activity"]))
    for p in candidates:
        if p3_count >= P3_BATCH_LIMIT:
            break
        submit(p["name"], "P3",
               f"从未使用且零浏览 (R2 归档候选, 批次限{P3_BATCH_LIMIT})"
               if p["total_activity"] == 0 else
               f"闲置 {p['days_idle']} 天 (R2)",
               {"rule": "R2", "use_count": p["use_count"],
                "view_count": p["view_count"], "days_idle": p["days_idle"]},
               dedupe_history=True)
        if created and created[-1]["skill_id"] == p["name"]:
            p3_count += 1

    # ── 报告 ──
    os.makedirs(ANALYTICS, exist_ok=True)
    rpath = os.path.join(ANALYTICS, f"optimization-{today}.md")
    with open(rpath, "w") as f:
        f.write(f"# Optimization Loop Report — {today}\n\n")
        f.write(f"**输入:** usage 画像 {usage['date']} · "
                f"{len(active_skills)} 活跃遥测技能\n")
        f.write(f"**产出:** {len(created)} 条新提案 (pending, 待人工审批) · "
                f"跳过 {len(skipped)} (幂等)\n\n")
        if created:
            f.write("| Proposal | Type | Skill | Reason |\n|:--|:--|:--|:--|\n")
            for pr in created:
                f.write(f"| `{pr['proposal_id']}` | {pr['type']} {pr['type_name']} | "
                        f"{pr['skill_id']} | {pr['reason']} |\n")
        else:
            f.write("本轮无新提案 — 系统状态与既有提案队列一致。\n")
        f.write("\n## 审批方式\n\n在会话中让 Hermes 执行: approve/reject + proposal_id\n")
        f.write("(governance.approval_manager, 绝不自动执行)\n")

    all_pending = list_all(status="pending")
    print(f"══ Optimization Loop — {today} ══")
    for pr in created:
        print(f"  ➕ {pr['proposal_id']} [{pr['type']} {pr['type_name']}] "
              f"{pr['skill_id']} — {pr['reason'][:60]}")
    for s in skipped[:5]:
        print(f"  ⏭️  {s[0]} [{s[1]}] {s[2]}")
    print(f"  📊 本轮新增 {len(created)} · 跳过 {len(skipped)} · "
          f"队列 pending 总计 {len(all_pending)}")
    print(f"  📝 报告: {rpath}")


if __name__ == "__main__":
    main()
