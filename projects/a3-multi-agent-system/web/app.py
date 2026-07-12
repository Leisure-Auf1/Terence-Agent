"""
A3 个性化教学系统 — Streamlit Web Demo

流程:
  学生输入 → ProfileAgent → 画像展示
  → PlannerAgent → 学习路径
  → ContentAgent → 资源卡片 (Markdown/Mermaid)
  → ReviewGate 评分
  → FeedbackLoop 优化
"""

import streamlit as st
import sys
from pathlib import Path

# 添加项目根路径
_project_root = Path(__file__).resolve().parent.parent
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

from core.agent_router import DynamicProfile, AgentRouter
from agents.profile_agent import ProfileAgent
from agents.planner_agent import PlannerAgent, LearningPlan
from memory.memory_manager import MemoryManager


# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────

st.set_page_config(
    page_title="A3 个性化教学系统",
    page_icon="🎓",
    layout="wide",
)

st.title("🎓 A3 个性化教学资源生成系统")
st.caption("Multi-Agent System — 从学生画像到个性化学习路径")

# ──────────────────────────────────────────────
# Sidebar — 学生输入
# ──────────────────────────────────────────────

with st.sidebar:
    st.header("👤 学生描述")
    student_text = st.text_area(
        "用自然语言描述你的学习情况",
        value="我是编程小白，零基础。看视频学，看到@装饰器就头大。容易放弃，需要多鼓励。想快速上手写代码。",
        height=150,
    )

    col1, col2 = st.columns(2)
    with col1:
        extract_btn = st.button("🎯 提取画像", use_container_width=True)
    with col2:
        course = st.selectbox(
            "课程",
            ["python_advanced", "python_basics"],
            label_visibility="collapsed",
        )

# ──────────────────────────────────────────────
# 初始化 Agents
# ──────────────────────────────────────────────

@st.cache_resource
def get_agents():
    return {
        "profile": ProfileAgent(),
        "planner": PlannerAgent(),
        "router": AgentRouter(),
        "memory": MemoryManager(auto_seed=True),
    }

agents = get_agents()

# ──────────────────────────────────────────────
# Step 1: 画像提取
# ──────────────────────────────────────────────

if extract_btn or "profile" in st.session_state:
    if extract_btn or "profile" not in st.session_state:
        with st.spinner("🔍 正在分析学生画像..."):
            result = agents["profile"].extract(student_text)
            st.session_state["profile"] = result
            st.session_state["profile_result"] = result

    if "profile_result" in st.session_state:
        result = st.session_state["profile_result"]
        profile = result.profile

        # ── 保存到 Memory ──
        student_id = st.session_state.get("student_id", "demo_student")
        mm = agents["memory"]
        mm.update_student_memory(
            student_id,
            profile=profile.to_dict(),
        )
        st.session_state["student_id"] = student_id

        st.header("📊 学生六维画像")
        profile_data = profile.to_dict()

        cols = st.columns(6)
        labels = {
            "knowledge_base": ("知识基础", {"junior_dev": "🔰 初级", "mid_level": "📗 中级", "senior": "🎖️ 高级"}),
            "cognitive_style": ("认知风格", {"visual_dominant": "👁️ 视觉型", "text_linear": "📖 文本型", "auditory": "👂 听觉型"}),
            "error_prone_bias": ("易错倾向", {"magic_syntax_blind": "🔮 语法糖盲", "indentation_errors": "📐 缩进错误", "variable_scoping": "🔍 作用域混淆", "type_mismatch": "🔢 类型错误", "import_issues": "📦 导入问题"}),
            "learning_pace": ("学习节奏", {"fast_track": "⚡ 快速", "normal": "🚶 正常", "deep_dive": "🔬 深潜"}),
            "interaction_preference": ("交互偏好", {"code_sandbox": "💻 动手实操", "quiz_first": "📝 做题优先", "passive_read": "📚 先阅读"}),
            "frustration_threshold": ("挫败阈值", {"low": "🫣 低", "medium": "😐 中", "high": "😤 高"}),
        }

        for i, (key, (label, mapping)) in enumerate(labels.items()):
            value = profile_data.get(key, "")
            display = mapping.get(value, value)
            cols[i].metric(label, display)

        # 置信度
        st.progress(result.confidence, text=f"提取置信度: {result.confidence:.0%}")
        st.caption(f"来源: {result.source} | 关键词: {', '.join(result.raw_keywords[:5])}")

    # ──────────────────────────────────────────
    # Step 2: 学习路径规划
    # ──────────────────────────────────────────

    with st.spinner("🗺️ 正在生成学习路径..."):
        plan = agents["planner"].plan(profile, course_id=course)
        st.session_state["plan"] = plan

    st.header("🗺️ 个性化学习路径")
    st.info(f"**路线:** {plan.strategy_rationale}")

    # 备选路径
    if plan.alternative_paths:
        with st.expander("🔀 备选路径"):
            for alt in plan.alternative_paths:
                st.markdown(f"- {alt}")

    # 节点展示
    for i, node in enumerate(plan.nodes):
        with st.container():
            cols = st.columns([1, 4, 1, 1, 1])
            cols[0].metric("顺序", f"#{i + 1}")
            cols[1].markdown(f"### {node.title}")
            cols[1].caption(node.core_concept)
            cols[2].metric("深度", "🟢" * node.depth)
            cols[3].metric("练习", f"{node.exercise_count}题")
            cols[4].metric("时长", f"{node.estimated_minutes}分钟")

            if node.notes:
                st.caption(f"📝 {node.notes}")
            st.divider()

    # 总览
    st.metric("📊 总学习时长", f"{plan.total_minutes} 分钟", f"{len(plan.nodes)} 个节点")

    # ── Student Memory 面板 ──
    with st.expander("🧠 学生长期记忆 (Memory)", expanded=False):
        student_id = st.session_state.get("student_id", "demo_student")
        mm = agents["memory"]
        summary = mm.get_learning_summary(student_id)

        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.metric("总交互次数", summary["total_interactions"])
            st.metric("平均评分", f"{summary['avg_score']}/100")
        with col_m2:
            st.metric("学习会话", summary["total_sessions"])
            st.metric("偏好风格", summary.get("preferred_style", "-"))
        with col_m3:
            st.metric("学习节奏", summary.get("avg_pace", "-"))

        # 优势
        if summary["strengths"]:
            st.subheader("💪 优势概念")
            for s in summary["strengths"]:
                stars = "⭐⭐⭐" if s["mastery"] >= 0.8 else "⭐⭐"
                st.text(f"{stars} {s['concept']} ({s['mastery']:.0%})")

        # 薄弱
        if summary["weaknesses_mastery"] or summary["weaknesses_reported"]:
            st.subheader("🔧 薄弱环节")
            for w in summary["weaknesses_mastery"][:3]:
                st.text(f"⚠️ {w['concept']}: {w['mastery']:.0%}")
            for w in summary["weaknesses_reported"][:3]:
                st.text(f"📋 {w['concept']}: {w['count']}次错误")

        # 历史
        if summary["recent_feedback"]:
            st.subheader("📝 最近学习记录")
            for fb in summary["recent_feedback"]:
                st.text(f"  {fb['node_id']}: {fb['score']}分")

    # ──────────────────────────────────────────
    # Step 3: 资源生成预览 (预留)
    # ──────────────────────────────────────────

    st.header("📦 教学资源预览")
    selected_node = st.selectbox(
        "选择节点查看资源",
        [n.title for n in plan.nodes],
    )

    for node in plan.nodes:
        if node.title == selected_node:
            st.markdown(f"### 🎯 资源一: {node.title} 讲解")
            st.info("💡 ContentAgent 将在此处生成个性化讲解文档（含 ❌/✅ 对比、代码示例）")

            st.markdown("### 📊 资源二: 思维导图")
            st.code(f"graph TD\n    A[{node.title}] --> B[{node.core_concept[:15]}...]\n    A --> C[练习{node.exercise_count}题]", language="mermaid")

            st.markdown("### 📝 资源三: 自适应题库")
            st.info(f"将生成 {node.exercise_count} 道题（辨析、排错、沙箱设计）")

            st.markdown("### 📚 资源四: 拓展阅读")
            st.code("[MULTI_MODAL_SLOT: 视觉卡片待生成]", language="json")

            st.markdown("### 💻 资源五: 沙箱实操")
            st.info("代码框架 + 预期输出 + 防幻觉排错桩")

    # ──────────────────────────────────────────
    # Step 4: Review Gate + Feedback (预留)
    # ──────────────────────────────────────────

    st.header("🚪 Review Gate 评分")
    st.metric("预计通过率", "≥70%", "目标阈值")
    st.caption("三道门禁: AST 静态审计 → Pytest 双向验证 → Judge 内容语义")
    st.progress(0.75, text="评分模拟: 75/100")

    st.caption("🔄 FeedbackLoop 就绪 — 评分 < 70 时自动触发 MetaReflector → Prompt 优化")

else:
    # 初始页面
    st.info("👈 在左侧输入你的学习情况，点击「提取画像」开始")
    st.image(
        "https://raw.githubusercontent.com/Leisure-Auf1/Terence-Agent/main/projects/a3-multi-agent-system/docs/arch.png"
        if False else None,
    )
    st.markdown("""
    ### 🚀 系统能力

    | 阶段 | Agent | 功能 |
    |------|-------|------|
    | 画像提取 | ProfileAgent | 自然语言 → 六维画像 |
    | 学生记忆 | StudentMemory | 长期学习状态追踪 |
    | 路径规划 | PlannerAgent | 画像 + 记忆 → 个性化路径 |
    | 资源生成 | ContentAgent | 5 大教学资产 |
    | 质量把关 | ReviewGate | 三道门禁 |
    | 反馈优化 | FeedbackLoop | UserSim → MetaReflector |
    | 经验记忆 | ExperienceMemory | Agent 失败经验库 |

    ### 📐 架构

    ```
    Student → ProfileAgent → StudentMemory
    → DynamicProfile → PlannerAgent → LearningPlan
    → ContentAgent → ReviewGate → UserSim
    → FeedbackRecord → MetaReflector → ExperienceMemory
    → Profile更新 → 下一轮生成
    ```
    """)
