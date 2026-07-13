"""Tests for ResourceAgent — personalized resource recommendations."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from agents.base import AgentContext, AgentTask
from agents.resource_agent import ResourceAgent, ResourcePlan, ResourceItem
from core.contracts import DynamicProfile, KnowledgeGap
from memory.manager import MemoryManager


@pytest.fixture
def ctx():
    return AgentContext(
        session_id="test-resource",
        student_id="test-student",
        memory_manager=MemoryManager(),
    )


@pytest.fixture
def resource_agent(ctx):
    return ResourceAgent(ctx)


@pytest.fixture
def visual_profile():
    return DynamicProfile(
        student_id="test-student",
        knowledge_base="mid_level",
        learning_goal="Multi-Agent Systems",
        cognitive_style="visual_dominant",
        learning_habit="exploratory",
        resource_preference="diagram+code",
    )


@pytest.fixture
def code_profile():
    return DynamicProfile(
        student_id="test-student",
        knowledge_base="junior_dev",
        learning_goal="Python Development",
        cognitive_style="text_linear",
        learning_habit="code_sandbox",
        resource_preference="text+code",
    )


class TestResourceAgent:
    """ResourceAgent — core recommendation tests."""

    def test_generates_resources(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        assert plan is not None
        assert isinstance(plan, ResourcePlan)
        assert len(plan.resources) > 0

    def test_all_resources_have_required_fields(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        for resource in plan.resources:
            assert resource.resource_type in ("document", "video", "code_example")
            assert resource.title != ""
            assert resource.priority >= 1
            assert resource.estimated_minutes > 0
            assert resource.reason != ""

    def test_visual_learner_gets_videos(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        video_resources = [r for r in plan.resources if r.resource_type == "video"]
        assert len(video_resources) >= 1, "Visual learners should get video resources"

    def test_code_sandbox_learner_gets_code_examples(self, resource_agent, ctx, code_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": code_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Python Development",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        code_resources = [r for r in plan.resources if r.resource_type == "code_example"]
        assert len(code_resources) >= 1, "Code sandbox learners should get code examples"

    def test_gap_based_recommendations(self, resource_agent, ctx, visual_profile):
        gap = KnowledgeGap(
            target_course="Multi-Agent Systems",
            gap_concepts=["async_io", "concurrency"],
            difficulty_map={"async_io": 0.2, "concurrency": 0.1},
        )
        task = AgentTask(
            task_type="recommend",
            payload={"profile": visual_profile, "knowledge_gap": gap, "goal": "Multi-Agent Systems"},
        )
        result = resource_agent.run(task)
        plan = result.result

        # Should have gap-specific resources
        gap_resources = [
            r for r in plan.resources
            if any(c in r.target_concepts for c in gap.gap_concepts)
        ]
        assert len(gap_resources) >= 1, "Should recommend resources for knowledge gaps"

    def test_recommendations_sorted_by_priority(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        priorities = [r.priority for r in plan.resources]
        assert priorities == sorted(priorities, reverse=True), \
            "Resources should be sorted by priority descending"

    def test_no_profile_returns_empty(self, resource_agent, ctx):
        task = AgentTask(
            task_type="recommend",
            payload={"knowledge_gap": KnowledgeGap(), "goal": "test"},
        )
        result = resource_agent.run(task)
        plan = result.result

        assert len(plan.resources) == 0
        assert result.confidence == 0.0

    def test_output_has_evidence(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        assert len(result.evidence) > 0
        assert result.reasoning != ""

    def test_strategy_includes_profile_info(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        strategy = plan.strategy.lower()
        assert "visual_dominant" in strategy or "visual" in strategy

    def test_resource_plan_serializable(self, resource_agent, ctx, visual_profile):
        task = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        result = resource_agent.run(task)
        plan = result.result

        d = plan.to_dict()
        assert "resources" in d
        assert "total_minutes" in d
        assert "strategy" in d
        assert isinstance(d["resources"], list)

    def test_different_profiles_different_resources(
        self, resource_agent, ctx, visual_profile, code_profile
    ):
        task1 = AgentTask(
            task_type="recommend",
            payload={
                "profile": visual_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Multi-Agent Systems",
            },
        )
        plan1 = resource_agent.run(task1).result

        task2 = AgentTask(
            task_type="recommend",
            payload={
                "profile": code_profile,
                "knowledge_gap": KnowledgeGap(),
                "goal": "Python Development",
            },
        )
        plan2 = resource_agent.run(task2).result

        types1 = {r.resource_type for r in plan1.resources}
        types2 = {r.resource_type for r in plan2.resources}
        assert types1 != types2, \
            "Visual learner and code learner should get different resource types"
