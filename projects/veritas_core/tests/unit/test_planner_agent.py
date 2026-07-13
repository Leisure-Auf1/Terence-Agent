"""Tests for PlannerAgent — personalized learning path generation."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from agents.base import AgentContext, AgentTask
from agents.planner_agent import PlannerAgent
from core.contracts import DynamicProfile, KnowledgeGap
from memory.manager import MemoryManager


@pytest.fixture
def ctx():
    return AgentContext(
        session_id="test-plan",
        student_id="test-student",
        memory_manager=MemoryManager(),
    )


@pytest.fixture
def planner(ctx):
    return PlannerAgent(ctx)


@pytest.fixture
def mid_profile():
    return DynamicProfile(
        student_id="test-student",
        knowledge_base="mid_level",
        learning_goal="Multi-Agent Systems",
        cognitive_style="visual_dominant",
        learning_habit="code_sandbox",
        resource_preference="diagram+code",
    )


@pytest.fixture
def junior_profile():
    return DynamicProfile(
        student_id="test-student",
        knowledge_base="junior_dev",
        learning_goal="Multi-Agent Systems",
        cognitive_style="text_linear",
        learning_habit="exploratory",
    )


class TestPlannerAgent:
    """PlannerAgent — core path planning tests."""

    def test_generates_plan(self, planner, ctx, mid_profile):
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        result = planner.run(task)
        plan = result.result

        assert plan is not None
        assert len(plan.nodes) > 0
        assert plan.total_minutes > 0

    def test_visual_learner_gets_mindmaps(self, planner, ctx, mid_profile):
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        result = planner.run(task)
        plan = result.result

        assert any("mindmap" in node.resource_types for node in plan.nodes)

    def test_code_habit_gets_codelab(self, planner, ctx, mid_profile):
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        result = planner.run(task)
        plan = result.result

        assert any("codelab" in node.resource_types for node in plan.nodes)

    def test_plan_different_by_profile(self, planner, ctx,
                                        mid_profile, junior_profile):
        task1 = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        plan1 = planner.run(task1).result

        task2 = AgentTask(
            task_type="plan",
            payload={"profile": junior_profile, "knowledge_gap": KnowledgeGap()},
        )
        plan2 = planner.run(task2).result

        # Junior should have more total minutes (slower pace)
        assert plan1.total_minutes != plan2.total_minutes, \
            "Different profiles should produce different plans"

    def test_plan_has_rationale(self, planner, ctx, mid_profile):
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        result = planner.run(task)
        plan = result.result

        assert plan.strategy_rationale != ""
        assert result.reasoning != ""

    def test_mastered_concepts_skipped(self, planner, ctx, mid_profile):
        gap = KnowledgeGap(
            target_course="Multi-Agent Systems",
            difficulty_map={"ai_basics": 0.9, "llm_intro": 0.85},  # Both mastered
        )
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": gap},
        )
        result = planner.run(task)
        plan = result.result

        # The first node (AI basics) should be skipped
        first_node_titles = [n.title for n in plan.nodes]
        assert "AI与LLM基础回顾" not in first_node_titles, \
            "Mastered concepts should be filtered out"

    def test_plan_output_structure(self, planner, ctx, mid_profile):
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        result = planner.run(task)
        plan = result.result

        for node in plan.nodes:
            assert node.title != ""
            assert node.level >= 1
            assert len(node.resource_types) >= 2  # notes + exercises minimum

    def test_plan_evidence_in_output(self, planner, ctx, mid_profile):
        task = AgentTask(
            task_type="plan",
            payload={"profile": mid_profile, "knowledge_gap": KnowledgeGap()},
        )
        result = planner.run(task)
        assert len(result.evidence) > 0
        assert "Multi-Agent" in result.evidence[0]
