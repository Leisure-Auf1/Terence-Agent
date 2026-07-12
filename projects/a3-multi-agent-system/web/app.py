"""
A3 个性化教学系统 — Streamlit Web Demo v2

完整面板:
  1. 对话式画像采集 (completeness bar)
  2. 动态画像卡片 (来源标注)
  3. 学习路径可视化 (状态: completed/weak/next)
  4. 推荐资源卡片 (ResourceRecommendationAgent)
  5. Agent Trace 面板 (EventBus timeline)
"""

import streamlit as st
import sys, time
from pathlib import Path

_project_root = Path(__file__).resolve().parent.parent
if str(_project_root / "src") not in sys.path:
    sys.path.insert(0, str(_project_root / "src"))

from core.agent_router import DynamicProfile, AgentRouter
from core.event_bus import AgentEventBus
from agents.profile_agent import ProfileAgent
from agents.planner_agent import PlannerAgent, PlanNode
from agents.resource_recommendation_agent import ResourceRecommendationAgent, RESOURCE_TYPES
from agents.conversation_profile_agent import ConversationProfileAgent, PROFILE_DIMENSIONS
from memory.memory_manager import MemoryManager

# ──────────────────────────────────────────────
# 页面配置
# ──────────────────────────────────────────────
st.set_page_config(page_title="A3 智能学习平台", page_icon="🎓", layout="wide")
st.title("🎓 A3 个性化智能学习平台")
st.caption("Multi-Agent System — 可展示 · 可解释 · 可评测")

# ── EventBus ──
bus = AgentEventBus.get_instance()

# ── Agents ──
@st.cache_resource
def get_agents():
    return {
        "profile": ProfileAgent(),
        "planner": PlannerAgent(),
        "router": AgentRouter(),
        "memory": MemoryManager(auto_seed=True),
        "conversation": ConversationProfileAgent(),
        "recommender": ResourceRecommendationAgent(),
    }

agents = get_agents()

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.header("👤 学生输入")
    student_id = st.text_input("学生ID", "demo_student")
    student_text = st.text_area(
        "描述你的学习情况",
        value="我是编程小白，零基础。看视频学，看到@装饰器就头大。容易放弃。想快速上手写代码。",
        height=120,
    )
    course = st.selectbox("课程", ["python_advanced", "python_basics"])
    extract_btn = st.button("🚀 开始分析", use_container_width=True)

    st.divider()
    st.caption("🟢 EventBus active — events tracked below")

# ──────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────
if not extract_btn and "pipeline_done" not in st.session_state:
    # Landing page
    st.info("👈 输入学生描述，点击「开始分析」")
    st.markdown("""
    ### 📐 架构
    ```
    Student → ProfileAgent → StudentMemory
    → PlannerAgent → ResourceRecommendationAgent
    → ContentAgent → ReviewGate → UserSim → FeedbackLoop
    ```
    """)
    st.stop()

if extract_btn or "pipeline_done" in st.session_state:
    if extract_btn:
        bus.start_session(student_id)
        st.session_state["pipeline_done"] = False
        st.rerun()

    # ──────────────────────────────────────────
    # Panel 1: 对话式画像采集 (Completeness)
    # ──────────────────────────────────────────
    st.header("📊 Panel 1: 画像采集进度")

    t0 = time.time()
    result = agents["profile"].extract(student_text)
    profile = result.profile
    profile_data = profile.to_dict()
    bus.emit("ProfileAgent", "extract", input_summary=student_text[:100],
             output_summary=f"confidence={result.confidence:.2f}", duration_ms=(time.time()-t0)*1000)

    agents["memory"].update_student_memory(student_id, profile=profile_data)

    # Completeness: 检查哪些维度是非默认值
    defaults = ProfileAgent.DEFAULTS
    filled = sum(1 for k, v in profile_data.items() if v != defaults.get(k))
    total = len(defaults)
    pct = filled / total

    cols = st.columns([2, 1])
    with cols[0]:
        st.progress(pct, text=f"画像完整度: {filled}/{total} ({pct:.0%})")
    with cols[1]:
        st.metric("置信度", f"{result.confidence:.0%}")

    # 已获得 vs 待补充
    col_a, col_b = st.columns(2)
    dim_labels_cn = {
        "knowledge_base": "知识基础", "cognitive_style": "认知风格",
        "error_prone_bias": "易错倾向", "learning_pace": "学习节奏",
        "interaction_preference": "交互偏好", "frustration_threshold": "抗挫能力",
    }
    with col_a:
        st.caption("✅ 已获得")
        for dim, label in dim_labels_cn.items():
            v = profile_data.get(dim, "")
            if v and v != defaults.get(dim):
                st.markdown(f"- ✓ {label}: {v}")
    with col_b:
        st.caption("○ 待补充")
        for dim, label in dim_labels_cn.items():
            v = profile_data.get(dim, "")
            if not v or v == defaults.get(dim):
                st.markdown(f"- ○ {label}")

    # ──────────────────────────────────────────
    # Panel 2: 动态画像卡片
    # ──────────────────────────────────────────
    st.header("📊 Panel 2: 动态画像")
    col_labels = list(profile_data.keys())
    cols = st.columns(len(col_labels))
    emoji_map = {
        "knowledge_base": {"junior_dev": "🔰", "mid_level": "📗", "senior": "🎖️"},
        "cognitive_style": {"visual_dominant": "👁️", "text_linear": "📖", "auditory": "👂"},
        "error_prone_bias": {"magic_syntax_blind": "🔮", "indentation_errors": "📐", "variable_scoping": "🔍", "type_mismatch": "🔢", "import_issues": "📦"},
        "learning_pace": {"fast_track": "⚡", "normal": "🚶", "deep_dive": "🔬"},
        "interaction_preference": {"code_sandbox": "💻", "quiz_first": "📝", "passive_read": "📚"},
        "frustration_threshold": {"low": "🫣", "medium": "😐", "high": "😤"},
    }
    for i, (key, label_cn) in enumerate(dim_labels_cn.items()):
        val = profile_data.get(key, "")
        emoji = emoji_map.get(key, {}).get(val, "❓")
        cols[i].metric(label_cn, f"{emoji} {val}")
    st.caption(f"来源: {result.source} | 关键词: {', '.join(result.raw_keywords[:5])}")

    # ──────────────────────────────────────────
    # Panel 3: 学习路径可视化
    # ──────────────────────────────────────────
    st.header("🗺️ Panel 3: 学习路径")

    t0 = time.time()
    mem = agents["memory"].get_student_memory(student_id)
    plan = agents["planner"].plan(profile, course_id=course, student_memory=mem)
    bus.emit("PlannerAgent", "generate_plan",
             input_summary=f"course={course}, profile={profile.knowledge_base}",
             output_summary=f"nodes={len(plan.nodes)}, minutes={plan.total_minutes}",
             duration_ms=(time.time()-t0)*1000)

    st.info(plan.strategy_rationale)

    # 节点状态: 根据 mastery 标记
    mastery = getattr(mem, "mastery_map", {})
    for i, node in enumerate(plan.nodes):
        m = mastery.get(node.node_id, -1)
        if m >= 0.8:
            status = "✅ completed"
            status_color = "green"
        elif 0 < m < 0.3:
            status = "⚠️ weak"
            status_color = "orange"
        elif i == 0:
            status = "▶️ next"
            status_color = "blue"
        else:
            status = "⬜ pending"
            status_color = "gray"

        cols = st.columns([1, 3, 1, 1, 1])
        cols[0].metric("", f"#{i+1}")
        cols[1].markdown(f"**{node.title}**  \n_{node.core_concept[:40]}_")
        cols[2].metric("深度", "🟢"*node.depth)
        cols[3].metric("练习", f"{node.exercise_count}题")
        cols[4].markdown(f":{status_color}[{status}]")
        if node.notes:
            st.caption(f"  📝 {node.notes}")

    st.metric("📊 总时长", f"{plan.total_minutes}分钟", f"{len(plan.nodes)}节点")

    # ──────────────────────────────────────────
    # Panel 4: 推荐资源卡片
    # ──────────────────────────────────────────
    st.header("📦 Panel 4: 推荐资源")

    t0 = time.time()
    resource_plan = agents["recommender"].recommend(student_id, mem, learning_plan_nodes=plan.nodes)
    bus.emit("ResourceRecommendationAgent", "recommend",
             input_summary=f"student={student_id}, mastery={len(mastery)}concepts",
             output_summary=f"resources={len(resource_plan.recommended_resources)}, minutes={resource_plan.total_minutes}",
             duration_ms=(time.time()-t0)*1000)

    st.info(f"🎯 今日目标: **{resource_plan.today_goal}**")
    st.caption(resource_plan.reasoning)

    resource_cols = st.columns(min(len(resource_plan.recommended_resources), 3) or 1)
    for i, res in enumerate(resource_plan.recommended_resources):
        c = resource_cols[i % len(resource_cols)]
        with c:
            info = RESOURCE_TYPES.get(res.resource_type, {"icon": "📄", "label": res.resource_type})
            st.markdown(f"### {info['icon']} {res.title}")
            st.caption(f"**类型:** {info['label']} | **优先级:** {'⭐'*min(res.priority//2, 5)}")
            st.caption(f"**原因:** {res.reason}")
            st.caption(f"**预计:** {res.estimated_minutes}分钟")

    # ──────────────────────────────────────────
    # Panel 5: Agent Trace
    # ──────────────────────────────────────────
    st.header("🔍 Panel 5: Agent Trace")
    events = bus.get_timeline()

    with st.expander("查看执行时间线", expanded=False):
        if not events:
            st.caption("(无事件)")
        for evt in events:
            icon = "✅" if evt.status == "success" else "❌"
            st.markdown(
                f"`{evt.timestamp[11:19]}` {icon} **{evt.agent}** → `{evt.action}` "
                f"({evt.duration_ms:.0f}ms)"
            )
            if evt.input_summary:
                st.caption(f"  ↳ {evt.input_summary[:120]}")
            if evt.output_summary:
                st.caption(f"  ↳ {evt.output_summary[:120]}")

    st.success(f"✅ Pipeline 完成 — {len(events)} 个事件, {resource_plan.total_minutes}分钟推荐")

    if not st.session_state.get("pipeline_done"):
        st.session_state["pipeline_done"] = True
