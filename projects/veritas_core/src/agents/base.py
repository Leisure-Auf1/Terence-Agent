"""
Veritas_Core — BaseAgent with Runtime State Machine.

All 6 cognitive agents inherit from BaseAgent.
Agent lifecycle: IDLE → REASONING → PLANNING → (TOOL_CALLING|EXECUTING) → VALIDATING → COMPLETED
"""

from __future__ import annotations
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum, auto
from typing import Any, Dict, List, Optional

from core.event_bus import AgentEventBus
from core.contracts import DynamicProfile, KnowledgeContext


class AgentState(Enum):
    IDLE = "idle"
    REASONING = "reasoning"
    PLANNING = "planning"
    TOOL_CALLING = "tool_calling"
    EXECUTING = "executing"
    VALIDATING = "validating"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    REFLECTION = "reflection"


@dataclass
class AgentRuntime:
    """Agent runtime state — tracks lifecycle transitions."""
    agent_name: str
    state: AgentState = AgentState.IDLE
    current_task: Optional[Any] = None
    retry_count: int = 0
    max_retries: int = 3
    state_history: List[Dict[str, str]] = field(default_factory=list)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    tool_calls: int = 0
    token_used: int = 0

    def transition(self, new_state: AgentState, reason: str = "") -> None:
        old = self.state
        self.state = new_state
        self.state_history.append({
            "from": old.value, "to": new_state.value,
            "reason": reason,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        if new_state == AgentState.RETRYING:
            self.retry_count += 1
        if new_state == AgentState.COMPLETED:
            self.completed_at = datetime.now(timezone.utc).isoformat()

    def can_retry(self) -> bool:
        return self.retry_count < self.max_retries

    def reset(self) -> None:
        self.state = AgentState.IDLE
        self.retry_count = 0


@dataclass
class AgentContext:
    """Context injected into every agent by the Orchestrator."""
    session_id: str = ""
    student_id: str = ""
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    event_bus: Optional[AgentEventBus] = None
    llm_provider: Optional[Any] = None  # LLMProvider
    memory_manager: Optional[Any] = None  # MemoryManager
    rag_retriever: Optional[Any] = None  # BaseRetriever

    def get_event_bus(self) -> AgentEventBus:
        return self.event_bus or AgentEventBus.get_instance()


@dataclass
class AgentTask:
    """Task dispatched by Orchestrator to an Agent."""
    task_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    task_type: str = ""
    payload: Dict[str, Any] = field(default_factory=dict)
    constraints: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentOutput:
    """Structured output from any agent."""
    agent: str = ""
    task_id: str = ""
    result: Any = None
    confidence: float = 1.0
    evidence: List[str] = field(default_factory=list)
    reasoning: str = ""
    state_trace: List[Dict[str, str]] = field(default_factory=list)
    trace_id: str = ""
    duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        result_dict = self.result.to_dict() if hasattr(self.result, "to_dict") else str(self.result)
        return {
            "agent": self.agent, "task_id": self.task_id,
            "result": result_dict, "confidence": self.confidence,
            "evidence": self.evidence, "reasoning": self.reasoning,
            "duration_ms": self.duration_ms,
        }


class BaseAgent(ABC):
    """Base class for all Veritas_Core cognitive agents.

    Subclasses must implement:
        execute(input_data) → AgentOutput

    The run() method handles the full state machine lifecycle:
        IDLE → REASONING → PLANNING → EXECUTING → VALIDATING → COMPLETED
    """

    agent_name: str

    def __init__(self, ctx: AgentContext):
        self.ctx = ctx
        self.runtime = AgentRuntime(agent_name=self.agent_name)

    def run(self, task: AgentTask) -> AgentOutput:
        """Full lifecycle execution with state machine."""
        start = time.time()
        bus = self.ctx.get_event_bus()

        try:
            # IDLE → REASONING
            self.runtime.transition(AgentState.REASONING, f"task: {task.task_type}")

            # Load context
            self._load_context(task)

            # REASONING → PLANNING
            self.runtime.transition(AgentState.PLANNING)

            # Execute (subclass logic)
            self.runtime.transition(AgentState.EXECUTING)
            output = self.execute(task.payload)

            # VALIDATING
            self.runtime.transition(AgentState.VALIDATING)
            output = self._validate(output)

            # COMPLETED
            self.runtime.transition(AgentState.COMPLETED)
            duration = (time.time() - start) * 1000

            bus.emit(
                source_agent=self.agent_name,
                action=task.task_type,
                input_summary=str(task.payload.get("text", ""))[:200],
                output_summary=str(output.result)[:300],
                duration_ms=round(duration, 1),
                permission_level="read",
            )

            output.agent = self.agent_name
            output.task_id = task.task_id
            output.state_trace = self.runtime.state_history
            output.trace_id = self.ctx.trace_id
            output.duration_ms = round(duration, 1)
            return output

        except Exception as e:
            duration = (time.time() - start) * 1000
            if self.runtime.can_retry():
                self.runtime.transition(AgentState.RETRYING, f"error: {e}")
                # Retry once more
                try:
                    return self.run(task)
                except Exception:
                    pass

            self.runtime.transition(AgentState.FAILED, str(e))
            bus.emit(
                source_agent=self.agent_name,
                action=task.task_type,
                input_summary=str(task.payload)[:200],
                output_summary=f"Error: {e}",
                status="error",
                duration_ms=round(duration, 1),
            )
            raise

    @abstractmethod
    def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        """Subclass implementation — the core agent logic."""
        ...

    def _load_context(self, task: AgentTask) -> None:
        """Load memory/rag context before reasoning."""
        pass

    def _validate(self, output: AgentOutput) -> AgentOutput:
        """Basic validation — override in subclasses for Trust checks."""
        return output
