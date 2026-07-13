"""
Veritas_Core — Shared Data Contracts.

Centralized dataclass definitions for all agents.
Every agent input/output uses typed contracts from this module.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


# ═══════════════════════════════════════════
# Student Profile
# ═══════════════════════════════════════════

@dataclass
class DynamicProfile:
    """8-dimension student profile — the core identity model."""
    student_id: str = ""
    # 8 dimensions
    knowledge_base: str = "junior_dev"       # junior_dev | mid_level | senior
    learning_goal: str = ""                   # e.g. "Multi-Agent Systems"
    cognitive_style: str = "text_linear"      # visual_dominant | text_linear | auditory
    learning_habit: str = "exploratory"       # code_sandbox | quiz_first | exploratory
    resource_preference: str = "text+code"    # text+code | diagram+code | video+quiz
    learning_motivation: str = "academic"     # career_advancement | academic | hobby
    time_budget: str = "flexible"             # flexible | 5h/week | 10h/week | 20h/week
    frustration_threshold: str = "medium"     # low | medium | high

    # Weak points
    weak_points: List[Dict[str, Any]] = field(default_factory=list)
    # [{"concept": "async_io", "error_type": "syntax", "occurrence_count": 3}]

    # Metadata
    source: str = "rule"                     # rule | llm | hybrid
    confidence: float = 0.7
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "knowledge_base": self.knowledge_base,
            "learning_goal": self.learning_goal,
            "cognitive_style": self.cognitive_style,
            "learning_habit": self.learning_habit,
            "resource_preference": self.resource_preference,
            "learning_motivation": self.learning_motivation,
            "time_budget": self.time_budget,
            "frustration_threshold": self.frustration_threshold,
            "weak_points": self.weak_points,
            "source": self.source,
            "confidence": self.confidence,
        }


# ═══════════════════════════════════════════
# Knowledge
# ═══════════════════════════════════════════

@dataclass
class KnowledgeGap:
    """Result of knowledge diagnosis — what student needs to learn."""
    target_course: str = ""
    known_concepts: List[str] = field(default_factory=list)
    gap_concepts: List[str] = field(default_factory=list)
    recommended_start: str = ""               # Starting chapter/node
    prerequisite_chain: List[str] = field(default_factory=list)
    difficulty_map: Dict[str, float] = field(default_factory=dict)  # concept → mastery

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_course": self.target_course,
            "known_concepts": self.known_concepts,
            "gap_concepts": self.gap_concepts,
            "recommended_start": self.recommended_start,
            "prerequisite_chain": self.prerequisite_chain,
            "difficulty_map": self.difficulty_map,
        }


@dataclass
class KnowledgeContext:
    """RAG-retrieved knowledge context for resource generation."""
    query: str = ""
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    assembled_text: str = ""
    sources: List[str] = field(default_factory=list)
    relevance_scores: List[float] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "chunks": self.chunks,
            "assembled_text": self.assembled_text,
            "sources": self.sources,
            "relevance_scores": self.relevance_scores,
        }


# ═══════════════════════════════════════════
# Learning Plan
# ═══════════════════════════════════════════

@dataclass
class PlanNode:
    """A single node in the learning path."""
    title: str = ""
    level: int = 1                            # 1-5 depth level
    concepts: List[str] = field(default_factory=list)
    depth: str = "standard"                   # fast_track | standard | deep_dive | intensive
    resource_types: List[str] = field(default_factory=list)
    exercises_count: int = 3
    estimated_minutes: int = 45
    teaching_strategy: str = ""               # e.g. "visual_diagram_focus"
    rationale: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "level": self.level,
            "concepts": self.concepts,
            "depth": self.depth,
            "resource_types": self.resource_types,
            "exercises_count": self.exercises_count,
            "estimated_minutes": self.estimated_minutes,
            "teaching_strategy": self.teaching_strategy,
            "rationale": self.rationale,
        }


@dataclass
class LearningPlan:
    """Complete personalized learning plan."""
    nodes: List[PlanNode] = field(default_factory=list)
    total_minutes: int = 0
    strategy_rationale: str = ""
    profile_snapshot: Optional[DynamicProfile] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "total_minutes": self.total_minutes,
            "strategy_rationale": self.strategy_rationale,
        }


# ═══════════════════════════════════════════
# Resources
# ═══════════════════════════════════════════

@dataclass
class LearningResource:
    """Unified resource protocol — all resource types use this."""
    resource_id: str = ""
    resource_type: str = ""                   # notes | ppt | mindmap | exercises | codelab
    title: str = ""
    content: str = ""                         # Main content (markdown/mermaid/code)
    difficulty: str = "intermediate"          # beginner | intermediate | advanced
    estimated_minutes: int = 30
    target_concepts: List[str] = field(default_factory=list)
    profile_params: Dict[str, Any] = field(default_factory=dict)
    trust_report: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "title": self.title,
            "content": self.content,
            "difficulty": self.difficulty,
            "estimated_minutes": self.estimated_minutes,
            "target_concepts": self.target_concepts,
        }


# ═══════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════

@dataclass
class EvaluationResult:
    """Learning evaluation result."""
    student_id: str = ""
    session_id: str = ""
    overall_score: float = 0.0
    correctness: float = 0.0
    knowledge_gain: Dict[str, Dict[str, float]] = field(default_factory=dict)
    engagement: float = 0.0
    resource_quality: float = 0.0
    weak_points_updated: List[Dict[str, Any]] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "student_id": self.student_id,
            "session_id": self.session_id,
            "overall_score": self.overall_score,
            "correctness": self.correctness,
            "knowledge_gain": self.knowledge_gain,
            "engagement": self.engagement,
            "resource_quality": self.resource_quality,
            "weak_points_updated": self.weak_points_updated,
            "suggestions": self.suggestions,
        }


# ═══════════════════════════════════════════
# Trust
# ═══════════════════════════════════════════

@dataclass
class MemoryRecord:
    """Secure memory record with validation metadata."""
    record_id: str = ""
    student_id: str = ""
    memory_type: str = ""                     # profile | mastery | preference | weak_point
    content: Dict[str, Any] = field(default_factory=dict)
    source: str = "user_statement"            # user_statement | exercise_result | system_inference
    confidence: float = 0.5
    evidence: List[str] = field(default_factory=list)
    status: str = "candidate"                 # candidate | confirmed | rejected
    created_by: str = ""
    trace_id: str = ""
    expires_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "record_id": self.record_id,
            "student_id": self.student_id,
            "memory_type": self.memory_type,
            "content": self.content,
            "source": self.source,
            "confidence": self.confidence,
            "evidence": self.evidence,
            "status": self.status,
            "created_by": self.created_by,
        }
