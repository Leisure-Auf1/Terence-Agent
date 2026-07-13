"""Integration test — full learning loop with EventBus + Memory."""

import pytest
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from core.event_bus import AgentEventBus
from core.contracts import DynamicProfile, KnowledgeGap
from agents.base import AgentContext, AgentTask
from agents.profile_agent import ProfileAgent
from agents.planner_agent import PlannerAgent
from memory.manager import MemoryManager
from providers.mock import MockLLMProvider


@pytest.fixture(autouse=True)
def reset_bus():
    """Reset EventBus between tests."""
    AgentEventBus.reset_instance()
    yield
    AgentEventBus.reset_instance()


@pytest.fixture
def bus():
    return AgentEventBus.get_instance()


@pytest.fixture
def memory():
    return MemoryManager()


@pytest.fixture
def ctx(bus, memory):
    session_id = uuid.uuid4().hex[:8]
    bus.start_session(session_id)
    return AgentContext(
        session_id=session_id,
        student_id="student-001",
        event_bus=bus,
        llm_provider=MockLLMProvider(),
        memory_manager=memory,
    )


class TestLearningLoop:
    """End-to-end: Profile → Plan → (next steps)."""

    def test_profile_then_plan(self, ctx, bus):
        """Full flow: extract profile → generate plan."""
        # Step 1: Profile extraction
        profile_agent = ProfileAgent(ctx)
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我是网络工程大三学生，有Python基础，视觉型学习，想学多智能体系统开发"},
        )
        profile_result = profile_agent.run(task)
        profile = profile_result.result
        assert profile.knowledge_base != ""

        # Step 2: Save to memory
        ctx.memory_manager.save_profile(ctx.student_id, profile)
        loaded = ctx.memory_manager.get_profile(ctx.student_id)
        assert loaded.knowledge_base == profile.knowledge_base

        # Step 3: Planning
        planner = PlannerAgent(ctx)
        plan_task = AgentTask(
            task_type="plan",
            payload={
                "profile": profile,
                "knowledge_gap": KnowledgeGap(
                    target_course="Multi-Agent Systems",
                    gap_concepts=["async_io", "agent_patterns"],
                ),
            },
        )
        plan_result = planner.run(plan_task)
        plan = plan_result.result

        assert len(plan.nodes) > 0
        assert plan.total_minutes > 0

        # Step 4: Verify EventBus recorded both agents
        timeline = bus.get_timeline()
        events = [e for e in timeline if e.source_agent != "System"]
        assert len(events) >= 2, f"Expected >=2 agent events, got {len(events)}"
        agent_names = [e.source_agent for e in events]
        assert "ProfileAgent" in agent_names
        assert "PlannerAgent" in agent_names

    def test_event_bus_trace_complete(self, ctx, bus):
        """Verify EventBus captures complete agent execution."""
        profile_agent = ProfileAgent(ctx)
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "零基础小白想学AI"},
        )
        profile_agent.run(task)

        events = bus.get_timeline()
        # Should have: session_start + profile_extract
        assert len(events) == 2
        assert events[0].action == "session_start"
        assert events[1].action == "profile_extract"
        assert events[1].source_agent == "ProfileAgent"
        assert events[1].status == "success"
        assert events[1].duration_ms > 0

    def test_memory_mastery_tracking(self, ctx, memory):
        """Memory: mastery EMA update works."""
        memory.update_mastery(
            "student-001", "async_io", 0.3,
            source="exercise_result", evidence=["ex_001"],
        )
        record = memory.get_mastery("student-001", "async_io")
        assert record.mastery_score == 0.4  # EMA: 0.5*0.5 + 0.3*0.5 = 0.4
        assert record.source == "exercise_result"
        assert record.status == "confirmed"

        # Second update
        memory.update_mastery(
            "student-001", "async_io", 0.8,
            source="exercise_result", evidence=["ex_002"],
        )
        record2 = memory.get_mastery("student-001", "async_io")
        # assert mastery correctness (allow float rounding)
        assert record2.mastery_score == pytest.approx(0.6, abs=1e-9)

    def test_memory_weak_concepts(self, ctx, memory):
        """Memory: weak concept detection — uses ctx.memory_manager."""
        mem = ctx.memory_manager  # Use same instance as agents
        mem.update_mastery("student-001", "async_io", 0.0, source="exercise_result")
        mem.update_mastery("student-001", "prompt_eng", 0.9, source="exercise_result")
        weak = mem.get_weak_concepts("student-001")
        assert len(weak) >= 1
        assert "async_io" in weak
        assert "prompt_eng" not in weak
