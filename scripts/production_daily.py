#!/usr/bin/env python3
"""Phase P.0.2 — Hermes Production Daily Check Engine.

每日生产入口的核心检查器。真实调用 Kernel 模块（非模拟）：
  1. Kernel Boot   — 导入全部 6 个运行时模块
  2. Registry      — 部署版 v1.1 校验 + 与仓库副本一致性
  3. Runtime Store — 运行时存储目录完整性
  4. Telemetry     — 事件存储完整性 + 系统快照
  5. Health        — 活跃技能健康评估 + 隔离区清点
  6. Governance    — 待处理提案清点

输出: production/reports/daily-YYYY-MM-DD.md
退出码: 0 = ALL GREEN, 1 = 有 FAIL 项
"""

import hashlib
import json
import os
import sys
import time

KERNEL = os.path.expanduser("~/.hermes/kernel")
RUNTIME = os.path.expanduser("~/.hermes/runtime")
REPO = os.path.expanduser("~/Terence-Agent")
DEPLOYED_REG = os.path.expanduser(
    "~/.hermes/skills/devops/skill-manager/references/skill-registry.json")
REPO_REG = os.path.join(REPO, "skill-manager", "skill-registry.json")
REPORT_DIR = os.path.join(REPO, "production", "reports")

sys.path.insert(0, KERNEL)

RESULTS = []  # (section, check, status, detail)


def record(section, check, ok, detail=""):
    RESULTS.append((section, check, "✅ PASS" if ok else "❌ FAIL", detail))
    return ok


def sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_kernel_boot():
    modules = [
        ("resolver", "resolver.capability_resolver"),
        ("lifecycle", "lifecycle.state_machine"),
        ("runtime", "runtime.executor"),
        ("telemetry", "telemetry.metrics_aggregator"),
        ("health", "health.health_engine"),
        ("governance", "governance.proposal_engine"),
    ]
    all_ok = True
    for name, mod in modules:
        try:
            __import__(mod)
            record("Kernel Boot", f"import {name}", True)
        except Exception as e:
            record("Kernel Boot", f"import {name}", False, str(e))
            all_ok = False
    manifest = os.path.join(KERNEL, "kernel-manifest.json")
    try:
        m = json.load(open(manifest))
        record("Kernel Boot", "kernel-manifest.json",
               m.get("compatibility", {}).get("registry") == "v1.2",
               f"kernel {m.get('kernel_version')}")
    except Exception as e:
        record("Kernel Boot", "kernel-manifest.json", False, str(e))
        all_ok = False
    return all_ok


def check_registry():
    ok = True
    try:
        d = json.load(open(DEPLOYED_REG))
        n = len(d.get("skills", []))
        ok &= record("Registry", "deployed v1.2 loads",
                     d.get("version") == "1.2.0" and n == 149,
                     f"version={d.get('version')} entries={n}")
        ok &= record("Registry", "forbidden_pairs intact",
                     len(d.get("forbidden_pairs", [])) == 5)
        ok &= record("Registry", "mount_strategies intact",
                     len(d.get("mount_strategies", {})) == 3)
        scopes = {}
        for s in d["skills"]:
            scopes[s.get("scope", "?")] = scopes.get(s.get("scope", "?"), 0) + 1
        ok &= record("Registry", "C.3 scope distribution",
                     scopes.get("core") == 14 and scopes.get("adapter") == 123
                     and scopes.get("project") == 12, str(scopes))
    except Exception as e:
        return record("Registry", "deployed registry", False, str(e))
    try:
        ok &= record("Registry", "repo copy in sync",
                     sha256(DEPLOYED_REG) == sha256(REPO_REG),
                     "sha256 match" if sha256(DEPLOYED_REG) == sha256(REPO_REG)
                     else "DRIFT — repo != deployed")
    except Exception as e:
        ok &= record("Registry", "repo copy in sync", False, str(e))
    return ok


def check_runtime_store():
    ok = True
    for d in ["state", "executions", "telemetry", "health",
              "proposals", "audit", "contexts", "governance"]:
        p = os.path.join(RUNTIME, d)
        ok &= record("Runtime Store", f"dir {d}/", os.path.isdir(p))
    return ok


def check_telemetry():
    from telemetry.event_store import validate_integrity, count_events
    from telemetry.metrics_aggregator import generate_snapshot
    integ = validate_integrity()
    ok = record("Telemetry", "event store integrity", integ["healthy"],
                f"{integ['total_events']} events, {integ['corrupt']} corrupt")
    snap = generate_snapshot()
    record("Telemetry", "system snapshot", True,
           f"total={snap['system']['total_executions']} "
           f"success_rate={snap['system']['success_rate']}%")
    today = time.strftime("%Y-%m-%d")
    tfile = os.path.join(RUNTIME, "telemetry", "events", f"{today}.jsonl")
    n_today = 0
    if os.path.exists(tfile):
        n_today = sum(1 for line in open(tfile) if line.strip())
    record("Telemetry", "today's events", True, f"{n_today} events on {today}")
    return ok, snap


def check_health():
    from telemetry.event_store import query_events
    from health.health_engine import evaluate
    ok = True
    events = query_events(limit=5000)
    skills = sorted({e.get("skill_id") for e in events if e.get("skill_id")})
    states = {}
    worst = []
    for sid in skills:
        h = evaluate(sid)
        states[h["state"]] = states.get(h["state"], 0) + 1
        if h["state"] not in ("HEALTHY", "WARNING"):
            worst.append(f"{sid}={h['state']}({h['score']})")
    record("Health", "active skills evaluated", True,
           f"{len(skills)} skills → {states or 'no data'}")
    qdir = os.path.join(RUNTIME, "health", "quarantine")
    quarantined = [f for f in os.listdir(qdir)] if os.path.isdir(qdir) else []
    active_q = []
    for qf in quarantined:
        try:
            q = json.load(open(os.path.join(qdir, qf)))
            if q.get("status", "active") in ("active", "quarantined"):
                active_q.append(qf)
        except Exception:
            active_q.append(qf)
    record("Health", "quarantine zone", True,
           f"{len(quarantined)} records ({len(active_q)} flagged)")
    if worst:
        record("Health", "degraded skills", False, "; ".join(worst[:5]))
        ok = False
    return ok, states


def check_governance():
    pfile = os.path.join(RUNTIME, "governance", "proposals", "proposals.jsonl")
    pending = []
    if os.path.exists(pfile):
        for line in open(pfile):
            if not line.strip():
                continue
            try:
                p = json.loads(line)
                if p.get("status") in ("pending", "open", "PENDING"):
                    pending.append(p.get("proposal_id", "?"))
            except Exception:
                pass
    record("Governance", "pending proposals", True,
           f"{len(pending)} pending" + (f": {', '.join(pending[:5])}" if pending else ""))
    return True


def main():
    t0 = time.time()
    today = time.strftime("%Y-%m-%d")
    print(f"══ Hermes Production Daily Check — {today} ══")

    check_kernel_boot()
    check_registry()
    check_runtime_store()
    _, snap = check_telemetry()
    _, health_states = check_health()
    check_governance()

    fails = [r for r in RESULTS if "FAIL" in r[2]]
    verdict = "🟢 ALL GREEN" if not fails else f"🔴 {len(fails)} FAILURE(S)"
    elapsed = round((time.time() - t0) * 1000)

    # 控制台输出
    cur = None
    for sec, chk, st, det in RESULTS:
        if sec != cur:
            print(f"\n─── {sec} ───")
            cur = sec
        print(f"  {st}  {chk}" + (f" — {det}" if det else ""))
    print(f"\n══ Verdict: {verdict} ({len(RESULTS)} checks, {elapsed}ms) ══")

    # 写入日报
    os.makedirs(REPORT_DIR, exist_ok=True)
    rpt = os.path.join(REPORT_DIR, f"daily-{today}.md")
    with open(rpt, "w") as f:
        f.write(f"# Hermes Production Daily Report — {today}\n\n")
        f.write(f"**Verdict:** {verdict}\n")
        f.write(f"**Checks:** {len(RESULTS)} ({len(RESULTS)-len(fails)} pass, "
                f"{len(fails)} fail) · {elapsed}ms\n")
        f.write(f"**Generated:** {time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}\n\n")
        f.write("| Section | Check | Status | Detail |\n|:--|:--|:--:|:--|\n")
        for sec, chk, st, det in RESULTS:
            f.write(f"| {sec} | {chk} | {st} | {det} |\n")
        f.write(f"\n## System Snapshot\n\n```json\n{json.dumps(snap, indent=2)}\n```\n")
        f.write(f"\n## Health States\n\n`{json.dumps(health_states)}`\n")
    print(f"📝 日报: {rpt}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
