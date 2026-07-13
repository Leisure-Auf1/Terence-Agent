"""
Veritas_Core — Memory Layer Models.

Three-tier memory:
  1. ConversationMemory (Redis) — short-term session context
  2. ProfileMemory (PostgreSQL) — long-term student profile
  3. HistoryMemory (PostgreSQL + ChromaDB) — learning records + experience
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════
# Conversation Memory
# ═══════════════════════════════════════════

@dataclass
class ConversationTurn:
    """A single turn in the learning conversation."""
    turn_id: str = ""
    session_id: str = ""
    role: str = "student"                   # student | agent | resource
    content: str = ""
    agent_name: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "turn_id": self.turn_id, "session_id": self.session_id,
            "role": self.role, "content": self.content,
            "agent_name": self.agent_name, "timestamp": self.timestamp,
        }


# ═══════════════════════════════════════════
# Profile Memory (PostgreSQL)
# ═══════════════════════════════════════════

@dataclass
class MasteryRecord:
    """Concept-level mastery tracking with EMA α=0.5."""
    student_id: str = ""
    concept: str = ""
    mastery_score: float = 0.5              # EMA: new = old×0.5 + new_score×0.5
    attempts: int = 0
    source: str = "initial"                 # user_statement | exercise_result | system_inference
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    status: str = "candidate"               # candidate | confirmed
    last_practiced: str = ""
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    @staticmethod
    def ema_update(old: float, new_score: float) -> float:
        return old * 0.5 + new_score * 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept, "mastery_score": self.mastery_score,
            "source": self.source, "confidence": self.confidence,
            "status": self.status, "attempts": self.attempts,
        }


@dataclass
class WeakPoint:
    """Student weak point record."""
    student_id: str = ""
    concept: str = ""
    error_type: str = ""
    occurrence_count: int = 1
    resolved: bool = False
    last_error: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "concept": self.concept, "error_type": self.error_type,
            "occurrence_count": self.occurrence_count, "resolved": self.resolved,
        }


@dataclass
class ProfileEvolution:
    """Record of a single profile change — audit trail."""
    student_id: str = ""
    session_id: str = ""
    change_type: str = ""                   # mastery_update | weak_point_add | preference_shift
    change_detail: Dict[str, Any] = field(default_factory=dict)
    reason: str = ""
    evaluation_ref: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# ═══════════════════════════════════════════
# History Memory
# ═══════════════════════════════════════════

@dataclass
class LearningRecord:
    """A single learning action record."""
    student_id: str = ""
    session_id: str = ""
    plan_node_id: str = ""
    concept: str = ""
    resource_types: List[str] = field(default_factory=list)
    action: str = "started"                 # started | completed | skipped
    time_spent_sec: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ExerciseError:
    """Wrong answer record — student mistake log."""
    student_id: str = ""
    exercise_id: str = ""
    concept: str = ""
    student_answer: str = ""
    correct_answer: str = ""
    error_type: str = ""                    # concept | syntax | logic | careless
    attempt_count: int = 1
    resolved: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ResourceFeedback:
    """Student feedback on a learning resource."""
    student_id: str = ""
    resource_id: str = ""
    resource_type: str = ""
    difficulty_rating: int = 3              # 1-5
    quality_rating: int = 3                 # 1-5
    comment: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class ExperienceRecord:
    """Cross-student experience lesson — stored in ChromaDB."""
    problem: str = ""
    cause: str = ""
    solution: str = ""
    source: str = "ReflectionAgent"
    success_count: int = 0
    failure_count: int = 0
    keywords: List[str] = field(default_factory=list)
    severity: str = "MEDIUM"

    def to_text(self) -> str:
        return f"Problem: {self.problem}\nCause: {self.cause}\nSolution: {self.solution}"
