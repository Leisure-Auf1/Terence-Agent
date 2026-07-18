#!/usr/bin/env bash
# Phase P.1.4 — Hermes Production Nightly Pipeline
# 无人值守生产管道（systemd timer 每日调度）：
#   [1] 每日检查 → [2] 项目执行矩阵 → [3] 使用数据收集 → [4] 优化循环
# 全程遥测落盘；任何失败在日志与 monitor 中可见，绝不静默。
set -uo pipefail
REPO="$HOME/Terence-Agent"
cd "$REPO"
TODAY=$(date '+%Y-%m-%d')
LOG_DIR="$REPO/production/reports"
LOG="$LOG_DIR/nightly-$TODAY.log"
mkdir -p "$LOG_DIR"
FAIL=0

{
echo "════════════════════════════════════════════════"
echo " 🌙 Hermes Production Nightly — $(date '+%Y-%m-%d %H:%M:%S')"
echo "════════════════════════════════════════════════"

echo ""
echo "━━ [1/4] Daily Check ━━"
if python3 scripts/production_daily.py; then
  echo "→ daily: 🟢"
else
  echo "→ daily: 🔴 (详见 production/reports/daily-$TODAY.md)"
  FAIL=1
fi

echo ""
echo "━━ [2/4] 项目执行矩阵 ━━"
for wf in daily-production-report veritas-test-run a3-test-run ucampus-readiness; do
  echo ""
  if python3 scripts/production_workflow.py "$wf"; then
    echo "→ $wf: 🟢"
  else
    echo "→ $wf: 🔴"
    FAIL=1
  fi
done

echo ""
echo "━━ [3/4] Skill 使用数据收集 ━━"
python3 scripts/skill_usage_collector.py || FAIL=1

echo ""
echo "━━ [4/4] 优化循环 (仅生成 pending 提案) ━━"
python3 scripts/optimization_loop.py || FAIL=1

echo ""
if [ $FAIL -eq 0 ]; then
  echo "🟢 NIGHTLY COMPLETE — $(date '+%H:%M:%S')"
else
  echo "🔴 NIGHTLY FINISHED WITH FAILURES — 检查上方日志"
fi
} 2>&1 | tee "$LOG"

exit $FAIL
