"""
Veritas_Core — PlannerAgent: Personalized Learning Path Generation.

Knowledge-gap-driven: uses student profile + knowledge diagnosis to generate
adaptive learning plan with personalized node sequence.
"""

from __future__ import annotations
from typing import Any, Dict, List

from .base import BaseAgent, AgentContext, AgentOutput
from core.contracts import DynamicProfile, KnowledgeGap, LearningPlan, PlanNode


class PlannerAgent(BaseAgent):
    """Generate personalized learning paths from profile + knowledge gap."""

    agent_name = "PlannerAgent"

    # Course knowledge map (simplified — in production, loaded from KnowledgeAgent)
    COURSE_MAP: Dict[str, List[Dict[str, Any]]] = {
        "Multi-Agent Systems": [
            {"title": "AI与LLM基础回顾", "level": 1, "concepts": ["ai_basics", "llm_intro"], "depth": "fast_track"},
            {"title": "Prompt Engineering", "level": 2, "concepts": ["prompt_design", "few_shot", "chain_of_thought"], "depth": "standard"},
            {"title": "RAG系统原理", "level": 3, "concepts": ["retrieval", "embedding", "vector_db"], "depth": "deep_dive"},
            {"title": "Agent通信机制", "level": 4, "concepts": ["message_passing", "shared_memory", "event_driven"], "depth": "deep_dive"},
            {"title": "多Agent架构设计", "level": 4, "concepts": ["orchestration", "task_delegation", "agent_patterns"], "depth": "deep_dive"},
            {"title": "综合项目实践", "level": 5, "concepts": ["multi_agent_project"], "depth": "intensive"},
        ],
        "LLM Engineering": [
            {"title": "LLM基础架构", "level": 1, "concepts": ["transformer", "attention", "tokenization"], "depth": "deep_dive"},
            {"title": "Prompt Engineering", "level": 2, "concepts": ["prompt_design"], "depth": "standard"},
            {"title": "RAG系统", "level": 3, "concepts": ["retrieval", "embedding"], "depth": "deep_dive"},
            {"title": "模型微调", "level": 4, "concepts": ["fine_tuning", "lora"], "depth": "deep_dive"},
        ],
    }

    # Cognitive style → teaching strategy mapping
    STYLE_STRATEGY = {
        "visual_dominant": "visual_diagram_focus",
        "text_linear": "text_step_by_step",
        "auditory": "analogy_and_explanation",
    }

    # Knowledge base → default depth
    KB_DEPTH = {
        "junior_dev": {"fast_track": 1, "standard": 2, "deep_dive": 2, "intensive": 3},
        "mid_level": {"fast_track": 1, "standard": 2, "deep_dive": 3, "intensive": 4},
        "senior": {"fast_track": 0, "standard": 1, "deep_dive": 2, "intensive": 3},
    }

    def execute(self, input_data: Dict[str, Any]) -> AgentOutput:
        profile: DynamicProfile = input_data.get("profile")
        knowledge_gap: KnowledgeGap = input_data.get("knowledge_gap") or KnowledgeGap()

        # Detect target course
        course = self._detect_course(profile.learning_goal)

        # Get course nodes
        course_nodes = self.COURSE_MAP.get(course, self.COURSE_MAP.get("Multi-Agent Systems", []))

        # Apply personalization
        plan_nodes = []
        for node_data in course_nodes:
            node = PlanNode(**node_data)
            node = self._personalize_node(node, profile, knowledge_gap)
            plan_nodes.append(node)

        # Filter: skip already-mastered concepts
        plan_nodes = self._filter_mastered(plan_nodes, knowledge_gap)

        # Calculate resource types and exercises per node
        plan_nodes = self._assign_resources(plan_nodes, profile)

        # Build plan
        total_minutes = sum(n.estimated_minutes for n in plan_nodes)
        plan = LearningPlan(
            nodes=plan_nodes,
            total_minutes=total_minutes,
            strategy_rationale=self._build_rationale(profile, knowledge_gap),
            profile_snapshot=profile,
        )

        return AgentOutput(
            result=plan,
            confidence=0.80,
            evidence=[f"course={course}", f"nodes={len(plan_nodes)}", f"total={total_minutes}min"],
            reasoning=self._build_rationale(profile, knowledge_gap),
        )

    # ── helpers ──

    def _detect_course(self, goal: str) -> str:
        goal_lower = goal.lower()
        if "multi-agent" in goal_lower or "多智能体" in goal_lower or "agent" in goal_lower:
            return "Multi-Agent Systems"
        if "llm" in goal_lower or "大模型" in goal_lower:
            return "LLM Engineering"
        return "Multi-Agent Systems"  # default

    def _personalize_node(self, node: PlanNode, profile: DynamicProfile,
                          gap: KnowledgeGap) -> PlanNode:
        """Apply profile constraints to node."""
        # Depth adjustment
        depth_factor = self.KB_DEPTH.get(profile.knowledge_base, {}).get(node.depth, 2)
        if depth_factor == 0:
            # Skip node for senior students
            node.estimated_minutes = 0

        # Teaching strategy from cognitive style
        strategy = self.STYLE_STRATEGY.get(profile.cognitive_style, "standard")
        node.teaching_strategy = strategy

        # Time adjustment
        time_factors = {"junior_dev": 1.5, "mid_level": 1.0, "senior": 0.6}
        tf = time_factors.get(profile.knowledge_base, 1.0)
        node.estimated_minutes = int(node.estimated_minutes * tf * depth_factor)

        # Rationale
        node.rationale = f"{profile.cognitive_style} learner → {strategy} strategy, depth={node.depth}"

        return node

    def _filter_mastered(self, nodes: List[PlanNode], gap: KnowledgeGap) -> List[PlanNode]:
        """Remove nodes where mastery ≥ 0.8."""
        filtered = []
        for node in nodes:
            all_mastered = all(
                gap.difficulty_map.get(c, 0.0) >= 0.8
                for c in node.concepts
            )
            if not all_mastered:
                filtered.append(node)
        return filtered

    def _assign_resources(self, nodes: List[PlanNode],
                          profile: DynamicProfile) -> List[PlanNode]:
        """Assign resource types and exercise counts per node."""
        base_resources = ["notes"]  # Always include notes
        if profile.cognitive_style == "visual_dominant":
            base_resources.append("mindmap")
        if profile.learning_habit == "code_sandbox":
            base_resources.append("codelab")
        base_resources.append("exercises")

        for node in nodes:
            node.resource_types = list(base_resources)
            if node.depth in ("deep_dive", "intensive"):
                node.resource_types.append("mindmap")
                node.exercises_count = 5
            elif node.depth == "fast_track":
                node.exercises_count = 1

        return nodes

    def _build_rationale(self, profile: DynamicProfile,
                         gap: KnowledgeGap) -> str:
        return (
            f"Student (cognitive={profile.cognitive_style}, "
            f"level={profile.knowledge_base}, habit={profile.learning_habit}). "
            f"Course: {gap.target_course or profile.learning_goal}. "
            f"Gap concepts: {gap.gap_concepts[:3] if gap.gap_concepts else 'none detected'}."
        )
