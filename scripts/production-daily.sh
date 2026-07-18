#!/usr/bin/env bash
# Phase P.0.2 — Hermes Production Daily Entry
# 每日生产入口：一条命令完成 预检 → Kernel 健康 → 日报。
#
# 用法:
#   bash scripts/production-daily.sh            # 完整每日检查
#   bash scripts/production-daily.sh --quick    # 跳过 preflight，只跑 Kernel 检查
set -uo pipefail

REPO="$HOME/Terence-Agent"
cd "$REPO"

echo "=============================================="
echo " 🏭 Hermes Production Daily — $(date '+%Y-%m-%d %H:%M')"
echo "=============================================="

# ── [1/3] 仓库状态 ──
echo ""
echo "─── [1/3] 📦 仓库状态 ───"
BRANCH=$(git rev-parse --abbrev-ref HEAD)
SHA=$(git rev-parse --short HEAD)
DIRTY=$(git status --porcelain | wc -l)
echo "  分支: $BRANCH @ $SHA"
echo "  未提交变更: $DIRTY 个文件"
if [ "$BRANCH" != "main" ]; then
  echo "  ⚠️  当前不在 main — 生产日检建议在 main 上运行"
fi

# ── [2/3] Harness Preflight ──
if [ "${1:-}" != "--quick" ]; then
  echo ""
  echo "─── [2/3] 🔍 Harness Preflight ───"
  if bash scripts/check-preflight.sh > /dev/null 2>&1; then
    echo "  ✅ preflight 通过 — 摘要: .hermes/preflight-$(date '+%Y-%m-%d').md"
  else
    echo "  ❌ preflight 失败 — 先运行 bash scripts/check-preflight.sh 查看详情"
    exit 1
  fi
else
  echo ""
  echo "─── [2/3] 🔍 Harness Preflight ─── (--quick 跳过)"
fi

# ── [3/3] Kernel 每日检查 ──
echo ""
echo "─── [3/3] 🧠 Kernel Daily Check ───"
python3 scripts/production_daily.py
RC=$?

echo ""
if [ $RC -eq 0 ]; then
  echo "✅ Production Daily 完成 — 系统 🟢 ALL GREEN"
else
  echo "🔴 Production Daily 发现异常 — 查看 production/reports/daily-$(date '+%Y-%m-%d').md"
fi
exit $RC
