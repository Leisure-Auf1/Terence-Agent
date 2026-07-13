"""
Veritas_Core — MemoryManager: Unified Memory Access Layer.

Three-tier memory:
  1. ConversationMemory — Redis (TTL=24h)
  2. ProfileMemory — PostgreSQL
  3. HistoryMemory — PostgreSQL + ChromaDB

For MVP: In-memory dict storage (PostgreSQL-ready schema included).
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from memory.models import (
    ConversationTurn, MasteryRecord, WeakPoint, ProfileEvolution,
    LearningRecord, ExerciseError, ResourceFeedback, ExperienceRecord,
)
from core.contracts import DynamicProfile, MemoryRecord


class MemoryManager:
    """Unified memory access — all agents use this interface.

    MVP: In-memory dicts (json-serializable).
    Production: PostgreSQL + Redis + ChromaDB.
    """

    def __init__(self):
        # Conversation
        self._conversations: Dict[str, List[ConversationTurn]] = {}

        # Profile
        self._profiles: Dict[str, DynamicProfile] = {}
        self._mastery: Dict[str, Dict[str, MasteryRecord]] = {}
        self._weak_points: Dict[str, List[WeakPoint]] = {}
        self._evolutions: Dict[str, List[ProfileEvolution]] = {}

        # History
        self._learning_records: List[LearningRecord] = []
        self._exercise_errors: List[ExerciseError] = []
        self._resource_feedback: List[ResourceFeedback] = []
        self._experience: List[ExperienceRecord] = []

    # ═══ Conversation ═══

    def add_turn(self, session_id: str, role: str, content: str,
                 agent_name: str = None) -> ConversationTurn:
        turn = ConversationTurn(
            session_id=session_id, role=role,
            content=content, agent_name=agent_name,
        )
        if session_id not in self._conversations:
            self._conversations[session_id] = []
        self._conversations[session_id].append(turn)
        return turn

    def get_context(self, session_id: str, last_n: int = 10
                    ) -> List[ConversationTurn]:
        turns = self._conversations.get(session_id, [])
        return turns[-last_n:]

    # ═══ Profile ═══

    def get_profile(self, student_id: str) -> DynamicProfile:
        return self._profiles.get(student_id, DynamicProfile(student_id=student_id))

    def save_profile(self, student_id: str,
                     profile: DynamicProfile) -> DynamicProfile:
        self._profiles[student_id] = profile
        return profile

    # ═══ Mastery ═══

    def get_mastery(self, student_id: str, concept: str) -> MasteryRecord:
        return self._mastery.get(student_id, {}).get(
            concept, MasteryRecord(student_id=student_id, concept=concept),
        )

    def update_mastery(self, student_id: str, concept: str,
                       new_score: float, source: str,
                       evidence: List[str] = None) -> MasteryRecord:
        old = self.get_mastery(student_id, concept)
        updated_score = MasteryRecord.ema_update(old.mastery_score, new_score)

        record = MasteryRecord(
            student_id=student_id, concept=concept,
            mastery_score=updated_score,
            attempts=old.attempts + 1,
            source=source,
            confidence=0.8 if source == "exercise_result" else 0.5,
            evidence=evidence or [],
            status="confirmed" if source == "exercise_result" else "candidate",
        )
        if student_id not in self._mastery:
            self._mastery[student_id] = {}
        self._mastery[student_id][concept] = record
        return record

    def get_weak_concepts(self, student_id: str) -> List[str]:
        """Get concepts with mastery < 0.3."""
        concepts = self._mastery.get(student_id, {})
        return [c for c, r in concepts.items() if r.mastery_score < 0.3]

    # ═══ History ═══

    def record_learning(self, student_id: str, plan_node_id: str,
                        concept: str, action: str = "started") -> LearningRecord:
        r = LearningRecord(
            student_id=student_id, plan_node_id=plan_node_id,
            concept=concept, action=action,
        )
        self._learning_records.append(r)
        return r

    def add_exercise_error(self, student_id: str, concept: str,
                           student_answer: str, correct_answer: str) -> ExerciseError:
        e = ExerciseError(
            student_id=student_id, concept=concept,
            student_answer=student_answer, correct_answer=correct_answer,
        )
        self._exercise_errors.append(e)
        return e

    def add_resource_feedback(self, student_id: str, resource_id: str,
                              resource_type: str, rating: int = 3) -> ResourceFeedback:
        f = ResourceFeedback(
            student_id=student_id, resource_id=resource_id,
            resource_type=resource_type, quality_rating=rating,
        )
        self._resource_feedback.append(f)
        return f

    # ═══ Experience ═══

    def recall_experience(self, query: str, limit: int = 5
                          ) -> List[ExperienceRecord]:
        """Keyword-based recall (MVP). ChromaDB semantic search in production."""
        results = []
        q_lower = query.lower()
        for exp in self._experience:
            if any(kw in q_lower for kw in exp.keywords):
                results.append(exp)
        return results[:limit]

    def store_experience(self, problem: str, cause: str,
                         solution: str) -> ExperienceRecord:
        exp = ExperienceRecord(problem=problem, cause=cause, solution=solution)
        self._experience.append(exp)
        return exp

    # ═══ Stats ═══

    def get_stats(self) -> Dict[str, Any]:
        return {
            "profiles": len(self._profiles),
            "mastery_entries": sum(len(m) for m in self._mastery.values()),
            "learning_records": len(self._learning_records),
            "exercise_errors": len(self._exercise_errors),
            "experience_lessons": len(self._experience),
        }
