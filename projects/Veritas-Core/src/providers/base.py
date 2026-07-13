"""
Veritas_Core — LLMProvider Interface.

Abstract base class for LLM providers.
Migrated from A3 with Backward-compatible interface.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Iterator, Optional


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""
    content: str = ""
    model: str = ""
    usage: Dict[str, int] = field(default_factory=lambda: {
        "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0,
    })
    finish_reason: str = "stop"
    error: Optional[str] = None

    @property
    def success(self) -> bool:
        return self.error is None and len(self.content) > 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content, "model": self.model,
            "usage": self.usage, "finish_reason": self.finish_reason,
            "error": self.error,
        }


class LLMProvider(ABC):
    """Abstract LLM provider interface."""

    def __init__(self, api_key: str = "", base_url: str = "", model: str = ""):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        **kwargs,
    ) -> LLMResponse:
        """Generate a response from the LLM."""
        ...

    def generate_stream(
        self, prompt: str, system_prompt: str = "",
        temperature: float = 0.7, max_tokens: int = 2048,
        **kwargs,
    ) -> Iterator[str]:
        """Stream tokens. Default: non-streaming fallback."""
        response = self.generate(
            prompt=prompt, system_prompt=system_prompt,
            temperature=temperature, max_tokens=max_tokens, **kwargs,
        )
        for token in response.content.split(" "):
            yield token + " "

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)
