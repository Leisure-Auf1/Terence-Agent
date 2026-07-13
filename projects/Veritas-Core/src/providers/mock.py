"""
Veritas_Core — MockLLMProvider for testing.

Provides deterministic responses without real API calls.
"""

from __future__ import annotations
import json
from typing import Any, Dict

from .base import LLMProvider, LLMResponse


class MockLLMProvider(LLMProvider):
    """Mock LLM — returns pre-seeded deterministic responses for testing."""

    def __init__(self):
        super().__init__(api_key="mock", model="mock-v1")

    def generate(
        self, prompt: str, system_prompt: str = "",
        temperature: float = 0.7, max_tokens: int = 2048, **kwargs,
    ) -> LLMResponse:
        content = self._mock_response(prompt)
        return LLMResponse(
            content=content, model="mock-v1",
            usage={"prompt_tokens": len(prompt)//4, "completion_tokens": len(content)//4, "total_tokens": len(prompt)//2},
        )

    def _mock_response(self, prompt: str) -> str:
        """Return mock JSON or markdown based on prompt content."""
        if "student profile" in prompt.lower() or "knowledge_base" in prompt.lower():
            return json.dumps({
                "knowledge_base": "mid_level",
                "learning_goal": "Multi-Agent Systems",
                "cognitive_style": "visual_dominant",
                "learning_habit": "code_sandbox",
                "resource_preference": "diagram+code",
                "learning_motivation": "career_advancement",
                "time_budget": "10h/week",
            })
        if "resource" in prompt.lower() or "content" in prompt.lower():
            return """## Learning Resource

### Key Concepts

This is a mock resource generated for testing purposes.

#### Summary
Mock content for Veritas_Core tests."""
        return json.dumps({"response": "mock"})


class ProviderFactory:
    """LLM Provider factory — env-configurable."""

    @staticmethod
    def create(provider: str = "mock", **kwargs) -> LLMProvider:
        if provider == "mock" or not provider:
            return MockLLMProvider()
        # Add other providers as needed
        return MockLLMProvider()
