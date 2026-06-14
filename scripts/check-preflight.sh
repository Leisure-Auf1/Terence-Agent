#!/bin/bash
# ==============================================================================
# check-preflight.sh — Harness Engineering Pre-Flight Check
#
# 机械约束优先：用可执行脚本替代提示词约束。
# 每次开始新项目前必须运行，产出结构化摘要供项目使用。
# ==============================================================================
# 原则: OpenAI Harness Engineering (2026)
#   "By enforcing invariants, not micromanaging implementations,
#    we let agents ship fast without undermining the foundation."
#
# 参考: Ryan Carson Control-Plane Pattern — Preflight Gate
#   "Run preflight gate first → only if passes, start expensive work."
#
# Feedforward/Feedback 模型 (Martin Fowler, 2026):
#   - Guides (feedforward): 前置引导，在行动前预判行为
#   - Sensors (feedback): 后置感知，在行动后自我纠错
# ==============================================================================

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
TODAY=$(date '+%Y-%m-%d')
NOW=$(date '+%H:%M')
HEAD_SHA=$(git -C "$REPO_DIR" rev-parse --short HEAD 2>/dev/null || echo "unknown")
OUTPUT_FILE="${REPO_DIR}/.hermes/preflight-${TODAY}.md"
RISK_FILE="${REPO_DIR}/.hermes/risk-contract.json"

cd "$REPO_DIR" || { echo "❌ 无法进入仓库目录"; exit 1; }

echo "=============================================="
echo "🔍 Harness Pre-Flight Check — ${TODAY} ${NOW}"
echo "=============================================="
echo "  SHA: ${HEAD_SHA}"
echo ""

# ── 0. SHA 指纹验证 ─────────────────────────────
echo "─── [0/8] 🔒 SHA 指纹验证 ───"

LAST_PREFLIGHT=$(ls -t "${REPO_DIR}/.hermes"/preflight-*.md 2>/dev/null | head -1 || true)
LAST_SHA=""
if [ -n "$LAST_PREFLIGHT" ]; then
    LAST_SHA=$(grep "^| HEAD SHA" "$LAST_PREFLIGHT" 2>/dev/null | sed 's/.*| \`\([^`]*\)\`.*/\1/' || echo "")
    if [ -z "$LAST_SHA" ]; then
        # 旧格式 preflight 没有 SHA，尝试从其他字段获取或跳过
        echo "  旧格式 preflight — 无法验证 SHA"
    elif [ "$LAST_SHA" != "$HEAD_SHA" ]; then
        echo "⚠️  SHA 已变化: ${LAST_SHA} → ${HEAD_SHA}"
        echo "   上次 preflight 结果过期，需要重新检查"
    else
        echo "✅ SHA 一致: ${HEAD_SHA}"
    fi
else
    echo "🆕 首次 preflight 检查"
fi
echo ""

# ── 1. Git 仓库状态 ──────────────────────────────────
echo "─── [1/8] 📦 Git 仓库状态 ───"

BRANCH=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "detached")
echo "分支: $BRANCH"

STATUS=$(git status --short 2>/dev/null || true)
CHANGED=0
if [ -z "$STATUS" ]; then
    echo "工作区: ✅ 干净"
else
    CHANGED=$(echo "$STATUS" | grep -c . || true)
    echo "工作区: ⚠️  $CHANGED 个文件未提交"
    echo "$STATUS" | head -10
    TOTAL=$(echo "$STATUS" | grep -c . || true)
    if [ "$TOTAL" -gt 10 ]; then
        echo "   ... 还有 $((TOTAL - 10)) 个文件省略"
    fi
fi

echo ""
echo "最近 5 次提交:"
git log --oneline -5 2>/dev/null || echo "  (无提交历史)"

# 检测分支差异
if [ "$BRANCH" != "main" ] && [ "$BRANCH" != "master" ]; then
    BEHIND=$(git rev-list --count HEAD..main 2>/dev/null || echo 0)
    AHEAD=$(git rev-list --count main..HEAD 2>/dev/null || echo 0)
    echo "对 main: ${AHEAD} commits ahead, ${BEHIND} commits behind"
fi
echo ""

# ── 2. 风险等级检测 ──────────────────────────────
echo "─── [2/8] ⚡ 风险等级检测 ───"

detect_risk_tier() {
    local sorted_status
    sorted_status=$(git diff --name-only HEAD 2>/dev/null || echo "")

    if echo "$sorted_status" | grep -qE "(config\.yaml|\.env|credentials|secret|token|password|auth|api_key)"; then
        echo "🔴 HIGH — 涉及敏感配置/凭据"
        return
    fi
    if echo "$sorted_status" | grep -qE "(db/|schema|migration)"; then
        echo "🔴 HIGH — 涉及数据库/数据结构变更"
        return
    fi
    if echo "$sorted_status" | grep -qE "(architecture-constraints|error-registry|agent-team/(guidance|agent-developer|agent-logger))"; then
        echo "🔴 HIGH — 涉及核心体系结构"
        return
    fi
    if echo "$STATUS" | grep -qE "^\\?"; then
        echo "🟡 MEDIUM — 包含新文件（未跟踪）"
        return
    fi
    if [ "$CHANGED" -gt 5 ]; then
        echo "🟡 MEDIUM — 批量变更 (>5 文件)"
        return
    fi
    echo "🟢 LOW — 常规变更"
}

TIER=$(detect_risk_tier)
echo "$TIER"

if [ -f "$RISK_FILE" ]; then
    echo "✅ risk-contract.json 存在"
else
    echo "ℹ️  risk-contract.json 不存在 (可选)"
fi
echo ""

# ── 3. 今日事件报告 ──────────────────────────────────
echo "─── [3/8] 📋 今日事件报告 ───"

EVENT_FILE="${REPO_DIR}/event-report/${TODAY}.md"
if [ -f "$EVENT_FILE" ]; then
    echo "✅ 今日日志已存在: event-report/${TODAY}.md"
    OPERATIONS=$(grep -cE "^###" "$EVENT_FILE" 2>/dev/null || echo 0)
    echo "  今日已有 ${OPERATIONS} 条操作记录"
    if [ "$OPERATIONS" -gt 0 ]; then
        grep -E "^###" "$EVENT_FILE" | head -5
    fi
else
    echo "ℹ️  今日日志尚未创建"
fi
echo ""

# ── 4. 报错表近期错误 ──────────────────────────────
echo "─── [4/8] 🚨 报错表已知问题 ───"

ER_FILE="${REPO_DIR}/error-registry/README.md"
if [ -f "$ER_FILE" ]; then
    echo "✅ error-registry 存在"
    ERR_COUNT=$(grep -c "^| \`" "$ER_FILE" 2>/dev/null || echo 0)
    echo "  共 ${ERR_COUNT} 条错误记录"
    echo ""
    echo "L0~L2 已知错误:"
    grep "^| \`" "$ER_FILE" | grep -v ":---" | head -6
    echo ""
    echo "L3 错误码:"
    # 从 "## L3" 行开始，到下一个 "##" 行，提取所有含 code block 的行
    sed -n '/^## L3/,/^## /p' "$ER_FILE" | grep "\`[A-Z_]\+\`" | head -14
else
    echo "ℹ️  error-registry 不存在"
fi
echo ""

# ── 5. 熵检测 — 垃圾清理检查 ──────────────────────
echo "─── [5/8] 🧹 熵检测 (Entropy/GC) ───"

echo "Projects 活跃度:"
if [ -d "${REPO_DIR}/projects" ]; then
    PROJECT_COUNT=0
    for p in "${REPO_DIR}"/projects/*/; do
        [ -d "$p" ] || continue
        PROJECT_COUNT=$((PROJECT_COUNT + 1))
        pname=$(basename "$p")
        echo "  ✅ projects/${pname}"
    done
    [ "$PROJECT_COUNT" -eq 0 ] && echo "  (无项目 — 无熵)"
else
    echo "  (projects/ 不存在)"
fi

echo ""
echo "Event Report 连续性:"
MISSING_DAYS=0
for d in $(seq 1 7); do
    CHECK_DATE=$(date -d "-${d} days" '+%Y-%m-%d' 2>/dev/null || echo "")
    [ -z "$CHECK_DATE" ] && continue
    [ -f "${REPO_DIR}/event-report/${CHECK_DATE}.md" ] && continue
    MISSING_DAYS=$((MISSING_DAYS + 1))
done
if [ "$MISSING_DAYS" -gt 3 ]; then
    echo "  ⚠️  最近7天有 ${MISSING_DAYS} 天缺少日志"
elif [ "$MISSING_DAYS" -gt 0 ]; then
    echo "  📝 最近7天有 ${MISSING_DAYS} 天缺少日志 (可接受)"
else
    echo "  ✅ 连续7天均有日志"
fi
echo ""

# ── 6. 可用技能与模板 ──────────────────────────────
echo "─── [6/8] 🛠️ 可用技能与模板 ───"

echo "论文/报告写作体系:"
if [ -d "${REPO_DIR}/paper-writing" ]; then
    echo "  ✅ paper-writing/"
    for t in "${REPO_DIR}"/paper-writing/templates/*.md; do
        [ -f "$t" ] && echo "    📄 templates/$(basename "$t")"
    done
    for w in "${REPO_DIR}"/paper-writing/workflows/*.md; do
        [ -f "$w" ] && echo "    🔄 workflows/$(basename "$w")"
    done
else
    echo "  ℹ️  paper-writing/ 不存在"
fi

echo ""
echo "Agent 团队:"
for agent in "${REPO_DIR}"/agent-team/*/README.md; do
    [ -f "$agent" ] && echo "  🤖 agent-team/$(basename "$(dirname "$agent")")"
done

echo ""
echo "文档入口:"
if [ -f "${REPO_DIR}/AGENTS.md" ]; then
    echo "  ✅ AGENTS.md (仓库目录索引)"
else
    echo "  ℹ️  AGENTS.md 不存在"
fi
echo ""

# ── 7. 架构约束索引 ──────────────────────────────
echo "─── [7/8] 🏗️ 架构约束索引 ───"

AC_FILE="${REPO_DIR}/architecture-constraints/README.md"
if [ -f "$AC_FILE" ]; then
    echo "✅ architecture-constraints 存在"
    echo "关键章节:"
    grep -E "^## " "$AC_FILE" | head -12
else
    echo "ℹ️  architecture-constraints 不存在"
fi
echo ""

# ── 8. 上下文重置检查 ──────────────────────────────
echo "─── [8/8] 🔄 上下文重置建议 ───"

if [ -f "${REPO_DIR}/.hermes/checkpoint.template.md" ]; then
    echo "✅ checkpoint 模板存在"
else
    echo "ℹ️  checkpoint 模板缺失"
fi

ACTIVE_CP=$(find "${REPO_DIR}/.hermes" -maxdepth 1 -name "checkpoint-*.md" 2>/dev/null | head -1 || true)
if [ -n "$ACTIVE_CP" ]; then
    echo "📝 有活跃 checkpoint: $(basename "$ACTIVE_CP")"
else
    echo "📝 无活跃 checkpoint — 干净的起始状态"
fi

# 建议
echo ""
echo "💡 建议:"
if [ "$CHANGED" -gt 0 ]; then
    echo "  ⚡ 工作区有 ${CHANGED} 个未提交文件 — 先 commit/stash 再开始新项目"
else
    echo "  ✅ 工作区干净 — 适合基于新分支开始项目"
fi
echo ""

# ── 写入摘要文件 ──────────────────────────────────
echo "=============================================="
echo "✅ Pre-flight check 完成"
echo "  SHA: ${HEAD_SHA}"
echo "  风险等级: ${TIER}"
echo "=============================================="

mkdir -p "${REPO_DIR}/.hermes"

REPO_STRUCTURE=$(find . -maxdepth 2 -type d | grep -v '.git/' | sort 2>/dev/null || echo "")
RECENT_COMMITS=$(git log --oneline -5 2>/dev/null || echo "-")

# 收集熵检测结果
ENTROPY_LINES=""
if [ -d "${REPO_DIR}/projects" ]; then
    for p in "${REPO_DIR}"/projects/*/; do
        [ -d "$p" ] || continue
        ENTROPY_LINES="${ENTROPY_LINES}\n- ✅ projects/$(basename "$p")"
    done
fi
[ -z "$ENTROPY_LINES" ] && ENTROPY_LINES="\n- (无项目)"

cat > "$OUTPUT_FILE" << PREFLIGHTEOF
# 🔍 Pre-Flight 检查摘要 — ${TODAY}

> 自动生成于 ${NOW}，由 \`scripts/check-preflight.sh\` 执行
> HAR-2026 — Preflight Gate (Ryan Carson Control-Plane Pattern)

## SHA 指纹

| 项目 | 值 |
|:-----|:---|
| HEAD SHA | \`${HEAD_SHA}\` |
| 分支 | \`${BRANCH}\` |
| 工作区 | $([ -z "$STATUS" ] && echo "干净" || echo "${CHANGED} 个文件未提交") |
| 风险等级 | ${TIER} |
| 日期 | ${TODAY} |

## 仓库结构

\`\`\`
${REPO_STRUCTURE}
\`\`\`

## 最近提交

${RECENT_COMMITS}

## Event Report

文件: \`event-report/${TODAY}.md\` — $([ -f "$EVENT_FILE" ] && echo "存在" || echo "未创建")

## Error Registry

存在: \`error-registry/README.md\` (${ERR_COUNT:-0} 条错误记录)

## Projects

$(echo -e "${ENTROPY_LINES}")

---
*Pre-flight checks ensure we work with current state, not stale context.*
*Feedforward (Guides) + Feedback (Sensors) = Reliable Agent Behavior*
PREFLIGHTEOF

echo "📝 摘要写入: $OUTPUT_FILE"
