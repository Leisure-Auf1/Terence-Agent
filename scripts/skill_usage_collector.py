#!/usr/bin/env python3
"""Phase P.1.2 — Skill Usage Collector.

三源合并生成技能使用画像（真实数据，非模拟）：
  源1  ~/.hermes/skills/.usage.json     — Hermes 平台使用统计 (use/view/patch counts)
  源2  ~/.hermes/runtime/telemetry/     — Kernel workflow 执行遥测
  源3  Registry v1.1                    — 149 技能 namespace/scope/lifecycle/status

输出:
  production/analytics/skill-usage-YYYY-MM-DD.json   — 全量画像
  production/analytics/skill-usage-YYYY-MM-DD.md     — 汇总报告
"""

import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

KERNEL = os.path.expanduser("~/.hermes/kernel")
REPO = os.path.expanduser("~/Terence-Agent")
USAGE_JSON = os.path.expanduser("~/.hermes/skills/.usage.json")
REG_PATH = os.path.expanduser(
    "~/.hermes/skills/devops/skill-manager/references/skill-registry.json")
OUT_DIR = os.path.join(REPO, "production", "analytics")

sys.path.insert(0, KERNEL)
from telemetry.event_store import query_events  # noqa: E402


def collect():
    today = time.strftime("%Y-%m-%d")
    now = datetime.now(timezone.utc)

    registry = json.load(open(REG_PATH))["skills"]
    usage = json.load(open(USAGE_JSON)) if os.path.exists(USAGE_JSON) else {}
    events = query_events(limit=10000)

    # Kernel 遥测按技能聚合
    tele = {}
    for e in events:
        sid = e.get("skill_id")
        if not sid:
            continue
        t = tele.setdefault(sid, {"exec_count": 0, "success": 0, "failed": 0,
                                  "last_exec": None})
        t["exec_count"] += 1
        if e.get("result") == "SUCCESS":
            t["success"] += 1
        else:
            t["failed"] += 1
        ts = e.get("timestamp", "")
        if not t["last_exec"] or ts > t["last_exec"]:
            t["last_exec"] = ts

    profiles = []
    for s in registry:
        name = s["name"]
        u = usage.get(name, {})
        t = tele.get(name, {})
        last_used = u.get("last_used_at")
        days_idle = None
        if last_used:
            try:
                dt = datetime.fromisoformat(last_used.replace("Z", "+00:00"))
                days_idle = (now - dt).days
            except ValueError:
                pass
        profiles.append({
            "name": name,
            "namespace": s.get("namespace", ""),
            "scope": s.get("scope", ""),
            "lifecycle": s.get("lifecycle", ""),
            "status": s.get("status", ""),
            "owner": s.get("owner", ""),
            # 源1 平台统计
            "use_count": u.get("use_count", 0),
            "view_count": u.get("view_count", 0),
            "patch_count": u.get("patch_count", 0),
            "last_used_at": last_used,
            "days_idle": days_idle,
            "platform_state": u.get("state"),
            # 源2 kernel 遥测
            "kernel_exec_count": t.get("exec_count", 0),
            "kernel_success": t.get("success", 0),
            "kernel_failed": t.get("failed", 0),
            "kernel_last_exec": t.get("last_exec"),
            # 综合活跃度
            "total_activity": u.get("use_count", 0) + t.get("exec_count", 0),
        })

    profiles.sort(key=lambda p: -p["total_activity"])

    active = [p for p in profiles if p["total_activity"] > 0]
    never_used = [p for p in profiles if p["total_activity"] == 0
                  and p["view_count"] == 0]
    idle_30d = [p for p in profiles if p["days_idle"] is not None
                and p["days_idle"] >= 30 and p["total_activity"] > 0]
    deprecated_active = [p for p in profiles
                         if p["lifecycle"] == "deprecated" and p["total_activity"] > 0]

    by_scope = {}
    for p in profiles:
        sc = by_scope.setdefault(p["scope"], {"n": 0, "active": 0, "activity": 0})
        sc["n"] += 1
        sc["activity"] += p["total_activity"]
        if p["total_activity"] > 0:
            sc["active"] += 1

    report = {
        "date": today,
        "generated_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {
            "registry_entries": len(registry),
            "platform_usage_entries": len(usage),
            "kernel_telemetry_events": len(events),
        },
        "summary": {
            "total_skills": len(profiles),
            "active_skills": len(active),
            "never_used_skills": len(never_used),
            "idle_30d_skills": len(idle_30d),
            "deprecated_but_active": len(deprecated_active),
            "coverage_pct": round(len(active) / len(profiles) * 100, 1),
            "by_scope": by_scope,
        },
        "top10_most_used": [
            {k: p[k] for k in ("name", "namespace", "use_count",
                               "kernel_exec_count", "total_activity")}
            for p in profiles[:10]],
        "never_used": [p["name"] for p in never_used],
        "idle_30d": [{"name": p["name"], "days_idle": p["days_idle"]}
                     for p in idle_30d],
        "profiles": profiles,
    }

    os.makedirs(OUT_DIR, exist_ok=True)
    jpath = os.path.join(OUT_DIR, f"skill-usage-{today}.json")
    with open(jpath, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")

    mpath = os.path.join(OUT_DIR, f"skill-usage-{today}.md")
    with open(mpath, "w") as f:
        f.write(f"# Skill Usage Report — {today}\n\n")
        f.write(f"**数据源:** Registry {len(registry)} 条 · 平台统计 {len(usage)} 条 · "
                f"Kernel 遥测 {len(events)} 事件\n\n")
        s = report["summary"]
        f.write(f"| 指标 | 值 |\n|:--|:--|\n")
        f.write(f"| 技能总数 | {s['total_skills']} |\n")
        f.write(f"| 活跃技能 (有使用记录) | {s['active_skills']} "
                f"({s['coverage_pct']}%) |\n")
        f.write(f"| 从未使用 | {s['never_used_skills']} |\n")
        f.write(f"| 30天+ 闲置 | {s['idle_30d_skills']} |\n")
        f.write(f"| deprecated 仍活跃 | {s['deprecated_but_active']} |\n\n")
        f.write("## 分层活跃度\n\n| Scope | 技能数 | 活跃 | 总活动量 |\n|:--|--:|--:|--:|\n")
        for sc, v in sorted(by_scope.items()):
            f.write(f"| {sc} | {v['n']} | {v['active']} | {v['activity']} |\n")
        f.write("\n## Top 10 使用最多\n\n| # | 技能 | namespace | 平台 use | kernel exec | 合计 |\n"
                "|--:|:--|:--|--:|--:|--:|\n")
        for i, p in enumerate(report["top10_most_used"], 1):
            f.write(f"| {i} | {p['name']} | {p['namespace']} | {p['use_count']} | "
                    f"{p['kernel_exec_count']} | {p['total_activity']} |\n")
        f.write(f"\n## 从未使用 ({len(never_used)})\n\n")
        f.write(", ".join(f"`{n}`" for n in report["never_used"]) or "无")
        f.write("\n")

    print(f"✅ 画像: {jpath}")
    print(f"✅ 报告: {mpath}")
    print(f"   {s['total_skills']} 技能 | 活跃 {s['active_skills']} "
          f"({s['coverage_pct']}%) | 从未使用 {s['never_used_skills']} | "
          f"30d+ 闲置 {s['idle_30d_skills']}")
    return report


if __name__ == "__main__":
    collect()
