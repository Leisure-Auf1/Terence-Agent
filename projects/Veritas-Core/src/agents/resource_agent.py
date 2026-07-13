"""
Veritas_Core — ResourceAgent: Personalized Resource Recommendation.

Analyzes learner profile + knowledge gap + learning goal to recommend:
  - Documents (text-based learning materials)
  - Videos (conceptual explanations)
  - Code examples (hands-on practice)

Follows the same BaseAgent pattern as ProfileAgent and PlannerAgent.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .base import BaseAgent, AgentContext, AgentOutput
from core.contracts import DynamicProfile, KnowledgeGap


# ── Resource type definitions ──

@dataclass
class ResourceItem:
    """A single recommended resource."""
    resource_type: str = ""      # document | video | code_example
    title: str = ""
    description: str = ""
    priority: int = 5            # 1-10, higher = more recommended
    estimated_minutes: int = 30
    target_concepts: List[str] = field(default_factory=list)
    reason: str = ""             # Why this resource was chosen

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resource_type": self.resource_type,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "estimated_minutes": self.estimated_minutes,
            "target_concepts": self.target_concepts,
            "reason": self.reason,
        }


@dataclass
class ResourcePlan:
    """Complete resource recommendation plan."""
    resources: List[ResourceItem] = field(default_factory=list)
    total_minutes: int = 0
    strategy: str = ""
    profile_snapshot: Optional[DynamicProfile] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "resources": [r.to_dict() for r in self.resources],
            "total_minutes": self.total_minutes,
            "strategy": self.strategy,
        }


class ResourceAgent(BaseAgent):
    """Recommend personalized learning resources.

    Input: learner profile + knowledge gap + learning goal
    Output: ResourcePlan with prioritized resources
    """

    agent_name = "ResourceAgent"

    # Priority weights by resource type and profile match
    TYPE_BASE_PRIORITY = {
        "document": 8,
        "video": 7,
        "code_example": 9,
    }

    def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        profile: Optional[DynamicProfile] = input_data.get("profile")
        knowledge_gap: KnowledgeGap = input_data.get("knowledge_gap") or KnowledgeGap()
        goal: str = input_data.get("goal", "")

        if profile is None:
            return AgentOutput(
                result=ResourcePlan(strategy="no profile provided"),
                confidence=0.0,
                evidence=["missing_profile"],
                reasoning="Cannot recommend resources without a learner profile",
            )

        resources = self._build_recommendations(profile, knowledge_gap, goal)
        total = sum(r.estimated_minutes for r in resources)
        strategy = self._build_strategy(profile, knowledge_gap)

        plan = ResourcePlan(
            resources=resources,
            total_minutes=total,
            strategy=strategy,
            profile_snapshot=profile,
        )

        return AgentOutput(
            result=plan,
            confidence=0.80,
            evidence=[
                f"resources={len(resources)}",
                f"total={total}min",
                f"style={profile.cognitive_style}",
            ],
            reasoning=strategy,
        )

    # ── recommendation engine ──

    def _build_recommendations(
        self,
        profile: DynamicProfile,
        gap: KnowledgeGap,
        goal: str,
    ) -> List[ResourceItem]:
        resources: List[ResourceItem] = []

        # Documents — always included
        resources.append(ResourceItem(
            resource_type="document",
            title=f"Core Concepts: {goal or profile.learning_goal}",
            description="Comprehensive learning document with structured explanations",
            priority=self.TYPE_BASE_PRIORITY["document"],
            estimated_minutes=45,
            target_concepts=list(gap.gap_concepts[:3]),
            reason="Foundation knowledge — essential for all learners",
        ))

        # Videos — for visual learners
        if profile.cognitive_style == "visual_dominant":
            resources.append(ResourceItem(
                resource_type="video",
                title=f"Visual Guide: {goal or profile.learning_goal}",
                description="Video walkthrough with diagrams and visual explanations",
                priority=9,
                estimated_minutes=30,
                target_concepts=list(gap.gap_concepts[:2]),
                reason="Visual learner — video format boosts comprehension",
            ))

        # Code examples — for hands-on learners
        if profile.learning_habit == "code_sandbox":
            resources.append(ResourceItem(
                resource_type="code_example",
                title=f"Hands-on Lab: {goal or profile.learning_goal}",
                description="Interactive code exercises with sandbox environment",
                priority=self.TYPE_BASE_PRIORITY["code_example"],
                estimated_minutes=60,
                target_concepts=list(gap.gap_concepts),
                reason="Code-sandbox learner — hands-on practice is optimal",
            ))

        # Gap-based recommendations
        for concept in gap.gap_concepts[:3]:
            mastery = gap.difficulty_map.get(concept, 0.5)
            if mastery < 0.3:
                resources.append(ResourceItem(
                    resource_type="document",
                    title=f"Foundations: {concept.replace('_', ' ').title()}",
                    description=f"Beginner-friendly explanation of {concept}",
                    priority=10,
                    estimated_minutes=20,
                    target_concepts=[concept],
                    reason=f"Critical gap (mastery={mastery:.1f}) — requires dedicated focus",
                ))
            elif mastery < 0.8:
                resources.append(ResourceItem(
                    resource_type="code_example",
                    title=f"Practice: {concept.replace('_', ' ').title()}",
                    description=f"Practice exercises to strengthen {concept}",
                    priority=7,
                    estimated_minutes=30,
                    target_concepts=[concept],
                    reason=f"Partial mastery ({mastery:.1f}) — practice will solidify",
                ))

        # Sort by priority descending, limit to 8
        resources.sort(key=lambda r: r.priority, reverse=True)
        return resources[:8]

    def _build_strategy(
        self,
        profile: DynamicProfile,
        gap: KnowledgeGap,
    ) -> str:
        parts = [
            f"Learner profile: {profile.knowledge_base} level,",
            f"{profile.cognitive_style} style,",
            f"{profile.learning_habit} habit.",
        ]
        if gap.gap_concepts:
            parts.append(f"Target gaps: {', '.join(gap.gap_concepts[:3])}.")
        else:
            parts.append("No specific gaps detected — exploratory recommendation.")
        return " ".join(parts)
