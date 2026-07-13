"""
Veritas_Core — SecureAgentEventBus: upgraded event bus with security fields.

All agents communicate through this singleton bus.
Events carry trace_id + permission + audit_id for security tracking.
"""

from __future__ import annotations
import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class SecureAgentEvent:
    """Security-enhanced agent event."""
    event_id: str = field(default_factory=lambda: uuid.uuid4().hex[:12])
    event_type: str = "agent_action"
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    # Agent info
    source_agent: str = ""
    target_agent: Optional[str] = None
    action: str = ""
    status: str = "success"  # success | error | unauthorized

    # Security fields
    trace_id: str = ""
    session_id: str = ""
    permission_level: str = "read"
    authorization: str = "granted"
    audit_id: str = ""

    # Content
    input_summary: str = ""
    output_summary: str = ""
    duration_ms: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "timestamp": self.timestamp,
            "source_agent": self.source_agent,
            "target_agent": self.target_agent,
            "action": self.action,
            "status": self.status,
            "trace_id": self.trace_id,
            "session_id": self.session_id,
            "permission_level": self.permission_level,
            "authorization": self.authorization,
            "audit_id": self.audit_id,
            "input_summary": self.input_summary,
            "output_summary": self.output_summary,
            "duration_ms": self.duration_ms,
            "metadata": self.metadata,
        }


class AgentEventBus:
    """Singleton Agent Event Bus with security-aware events."""

    _instance: Optional["AgentEventBus"] = None

    def __init__(self):
        self._events: List[SecureAgentEvent] = []
        self._session_id: str = ""
        self._trace_id: str = ""

    @classmethod
    def get_instance(cls) -> "AgentEventBus":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset_instance(cls) -> None:
        cls._instance = cls()

    def start_session(self, session_id: str) -> None:
        self._session_id = session_id
        self._trace_id = uuid.uuid4().hex[:16]
        self._events.clear()
        self.emit("System", "session_start",
                  input_summary=f"Session: {session_id}",
                  output_summary="Session started")

    def emit(
        self,
        source_agent: str,
        action: str,
        input_summary: str = "",
        output_summary: str = "",
        status: str = "success",
        duration_ms: float = 0.0,
        target_agent: Optional[str] = None,
        permission_level: str = "read",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SecureAgentEvent:
        event = SecureAgentEvent(
            source_agent=source_agent,
            target_agent=target_agent,
            action=action,
            status=status,
            trace_id=self._trace_id,
            session_id=self._session_id,
            permission_level=permission_level,
            input_summary=input_summary[:300],
            output_summary=output_summary[:500],
            duration_ms=duration_ms,
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def get_timeline(self) -> List[SecureAgentEvent]:
        return list(self._events)

    def get_recent(self, n: int = 20) -> List[SecureAgentEvent]:
        return self._events[-n:]

    def to_json(self) -> str:
        return json.dumps([e.to_dict() for e in self._events], ensure_ascii=False, indent=2)

    def clear(self) -> None:
        self._events.clear()

    @property
    def event_count(self) -> int:
        return len(self._events)

    @property
    def latest_event(self) -> Optional[SecureAgentEvent]:
        return self._events[-1] if self._events else None

    @property
    def current_trace_id(self) -> str:
        return self._trace_id
