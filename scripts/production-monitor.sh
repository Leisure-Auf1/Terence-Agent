#!/usr/bin/env bash
# Phase P.0.4 — Hermes Production Monitor
# 运行监控：遥测汇总 + 健康状态 + workflow 运行记录 + 治理队列的实时视图。
#
# 用法: bash scripts/production-monitor.sh
set -uo pipefail
REPO="$HOME/Terence-Agent"
cd "$REPO"

echo "=============================================="
echo " 📡 Hermes Production Monitor — $(date '+%Y-%m-%d %H:%M')"
echo "=============================================="

python3 - <<'PYEOF'
import json, os, sys, time
KERNEL = os.path.expanduser("~/.hermes/kernel")
RUNTIME = os.path.expanduser("~/.hermes/runtime")
REPO = os.path.expanduser("~/Terence-Agent")
sys.path.insert(0, KERNEL)

from telemetry.metrics_aggregator import generate_snapshot, aggregate_skill
from telemetry.event_store import query_events, validate_integrity
from health.health_engine import evaluate

today = time.strftime("%Y-%m-%d")

# ── 遥测汇总 ──
print("\n─── 📊 遥测汇总 (rolling) ───")
snap = generate_snapshot()
for layer in ("system", "core", "adapter", "project"):
    s = snap[layer]
    print(f"  {layer:8s} exec={s['total_executions']:4d}  success={s['success_rate']:5.1f}%  skills={s.get('skills_tracked',0)}")
integ = validate_integrity()
print(f"  完整性: {integ['total_events']} events, {integ['corrupt']} corrupt → {'✅' if integ['healthy'] else '❌'}")

# ── 活跃技能健康 ──
print("\n─── 💚 活跃技能健康 ───")
events = query_events(limit=5000)
skills = sorted({e.get("skill_id") for e in events if e.get("skill_id")})
if not skills:
    print("  (今日暂无技能执行)")
for sid in skills:
    h = evaluate(sid)
    m = aggregate_skill(sid)
    icon = {"HEALTHY":"💚","WARNING":"💛","DEGRADED":"🧡","FAILED":"❤️","QUARANTINED":"🖤"}.get(h["state"],"❓")
    print(f"  {icon} {sid:28s} {h['state']:11s} score={h['score']:3d}  exec={m['execution_count']}  sr={m['success_rate']}%  p95={m['p95_latency_ms']}ms")

# ── Workflow 运行记录 ──
print("\n─── 🏃 Workflow 运行记录 (最近5次) ───")
run_dir = os.path.join(REPO, "production", "runs")
runs = sorted(os.listdir(run_dir))[-5:] if os.path.isdir(run_dir) else []
if not runs:
    print("  (无运行记录)")
for rf in runs:
    r = json.load(open(os.path.join(run_dir, rf)))
    icon = "✅" if r["verdict"] == "SUCCESS" else "🔴"
    print(f"  {icon} {r['run_id']}  {r['workflow']:30s} {r['steps_success']}/{r['steps_total']} steps  {r['elapsed_ms']}ms")

# ── 治理队列 ──
print("\n─── ⚖️ 治理队列 ───")
pfile = os.path.join(RUNTIME, "governance", "proposals", "proposals.jsonl")
pending = []
if os.path.exists(pfile):
    for line in open(pfile):
        if line.strip():
            try:
                p = json.loads(line)
                if p.get("status") in ("pending", "open", "PENDING"):
                    pending.append(f"{p.get('proposal_id')} ({p.get('type')})")
            except Exception:
                pass
print(f"  待处理提案: {len(pending)}" + (f" — {', '.join(pending)}" if pending else " — 队列干净 ✅"))

qdir = os.path.join(RUNTIME, "health", "quarantine")
qn = len(os.listdir(qdir)) if os.path.isdir(qdir) else 0
print(f"  隔离区: {qn} 条记录" + (" ✅" if qn == 0 else " ⚠️"))

print(f"\n══ Monitor 完成 — {today} ══")
PYEOF
