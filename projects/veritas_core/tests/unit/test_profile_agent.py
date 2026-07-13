"""Tests for ProfileAgent — rule engine + LLM dual-mode extraction."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from agents.base import AgentContext, AgentTask
from agents.profile_agent import ProfileAgent
from memory.manager import MemoryManager
from providers.mock import MockLLMProvider


@pytest.fixture
def ctx():
    return AgentContext(
        session_id="test-session",
        student_id="test-student",
        llm_provider=MockLLMProvider(),
        memory_manager=MemoryManager(),
    )


@pytest.fixture
def profile_agent(ctx):
    return ProfileAgent(ctx)


class TestProfileAgentRuleMode:
    """ProfileAgent rule engine tests."""

    def test_extract_junior_profile(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我是零基础小白，刚开始学编程，想学多智能体系统，喜欢看视频学习"},
        )
        result = profile_agent.run(task)
        profile = result.result
        assert profile.knowledge_base == "junior_dev"
        assert profile.cognitive_style == "visual_dominant"
        assert "Multi-Agent" in profile.learning_goal
        assert result.confidence > 0.4

    def test_extract_mid_level(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我有Python基础，写过一段时间，想进阶学习Agent开发"},
        )
        result = profile_agent.run(task)
        profile = result.result
        assert profile.knowledge_base == "mid_level"

    def test_extract_senior_profile(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我是资深架构师，多年的Python和Java开发经验，经常写大型系统，想学多智能体架构设计"},
        )
        result = profile_agent.run(task)
        profile = result.result
        assert profile.knowledge_base == "senior"

    def test_extract_visual_style(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我是视觉型学习，喜欢看图解和思维导图"},
        )
        result = profile_agent.run(task)
        assert result.result.cognitive_style == "visual_dominant"

    def test_extract_code_habit(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我喜欢动手写代码练习，经常敲代码"},
        )
        result = profile_agent.run(task)
        assert result.result.learning_habit == "code_sandbox"

    def test_extract_weak_points(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我有Python基础，但对异步编程搞不太懂，装饰器经常用错，async和并发也有问题"},
        )
        result = profile_agent.run(task)
        weak_points = result.result.weak_points
        assert len(weak_points) >= 1

    def test_empty_input(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": ""},
        )
        result = profile_agent.run(task)
        assert result.confidence == 0.0

    def test_profile_output_structure(self, profile_agent, ctx):
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "我是网络工程学生，有Python基础，想学多智能体"},
        )
        result = profile_agent.run(task)
        profile = result.result
        # All 8 dimensions should be set
        assert profile.knowledge_base != ""
        assert profile.cognitive_style != ""
        assert profile.learning_habit != ""
        assert profile.resource_preference != ""
        assert profile.learning_motivation != ""
        assert profile.time_budget != ""


class TestProfileAgentLLMMode:
    """ProfileAgent LLM-enhanced extraction tests."""

    def test_llm_mode_activated(self, ctx):
        agent = ProfileAgent(ctx)
        task = AgentTask(
            task_type="profile_extract",
            payload={"text": "I have intermediate Python skills and want to learn multi-agent AI systems as a visual learner"},
        )
        result = agent.run(task)
        profile = result.result
        # With MockLLMProvider, should get the mock response
        assert profile.knowledge_base == "mid_level"
        assert profile.cognitive_style == "visual_dominant"
