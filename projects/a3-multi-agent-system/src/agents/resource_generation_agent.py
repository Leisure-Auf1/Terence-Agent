"""
Phase 11 — ResourceGenerationAgent

Generates 5 types of learning resources from course content:
1. Course Notes — Structured lecture notes with key concepts
2. Mind Map — Mermaid-format visual knowledge maps
3. Exercises — Auto-generated questions with rubrics
4. Code Labs — Runnable code exercises with expected outputs
5. Video Scripts — Narration scripts for educational videos

Design:
- Each generator is a separate method with a clear input/output contract
- All generators are rule-based (no LLM dependency for generation)
- LLM enrichment is optional via provider injection
- Outputs follow the ContentAgent 5-asset contract format
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.llm.provider import LLMProvider, LLMResponse


# ──────────────────────────────────────────────
# Resource Data Models
# ──────────────────────────────────────────────

@dataclass
class CourseNotes:
    """Generated course notes resource."""
    title: str
    topic: str
    sections: List[Dict[str, str]] = field(default_factory=list)
    key_concepts: List[str] = field(default_factory=list)
    summary: str = ""
    estimated_read_minutes: int = 15

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", "", f"**Topic:** {self.topic}", ""]
        for s in self.sections:
            lines.append(f"## {s['heading']}")
            lines.append(s["content"])
            lines.append("")
        lines.append("## Key Concepts")
        for c in self.key_concepts:
            lines.append(f"- **{c}**")
        lines.append("")
        if self.summary:
            lines.append(f"> {self.summary}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "document",
            "title": self.title,
            "topic": self.topic,
            "sections": self.sections,
            "key_concepts": self.key_concepts,
            "summary": self.summary,
            "estimated_read_minutes": self.estimated_read_minutes,
            "format": "markdown",
        }


@dataclass
class MindMap:
    """Generated mind map resource (Mermaid format)."""
    title: str
    central_topic: str
    branches: List[Dict[str, Any]] = field(default_factory=list)
    mermaid_code: str = ""

    def to_markdown(self) -> str:
        if not self.mermaid_code:
            self._build_mermaid()
        return f"```mermaid\n{self.mermaid_code}\n```"

    def _build_mermaid(self):
        lines = ["mindmap", f"  root(({self.central_topic}))"]
        for branch in self.branches:
            lines.append(f"    {branch['name']}")
            for child in branch.get("children", []):
                lines.append(f"      {child}")
        self.mermaid_code = "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        if not self.mermaid_code:
            self._build_mermaid()
        return {
            "type": "mindmap",
            "title": self.title,
            "central_topic": self.central_topic,
            "branches": self.branches,
            "mermaid_code": self.mermaid_code,
            "format": "mermaid",
        }


@dataclass
class Exercise:
    """Generated exercise resource."""
    title: str
    questions: List[Dict[str, Any]] = field(default_factory=list)
    total_points: int = 0
    estimated_minutes: int = 15

    def to_markdown(self) -> str:
        lines = [f"# {self.title}", ""]
        for i, q in enumerate(self.questions, 1):
            lines.append(f"## Question {i} ({q.get('points', 0)} pts)")
            lines.append(q["question"])
            lines.append("")
            if "hint" in q:
                lines.append(f"*Hint: {q['hint']}*")
            if "rubric" in q:
                lines.append("**Grading Rubric:**")
                for r in q["rubric"]:
                    lines.append(f"- {r}")
            lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "exercise",
            "title": self.title,
            "questions": self.questions,
            "total_points": self.total_points,
            "estimated_minutes": self.estimated_minutes,
            "format": "markdown",
        }


@dataclass
class CodeLab:
    """Generated code lab resource."""
    title: str
    description: str
    language: str = "python"
    starter_code: str = ""
    expected_output: str = ""
    hints: List[str] = field(default_factory=list)
    solution: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            "",
            self.description,
            "",
            "## Starter Code",
            f"```{self.language}",
            self.starter_code,
            "```",
            "",
            "## Expected Output",
            "```",
            self.expected_output,
            "```",
        ]
        if self.hints:
            lines.append("")
            lines.append("## Hints")
            for i, h in enumerate(self.hints, 1):
                lines.append(f"{i}. {h}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "code",
            "title": self.title,
            "language": self.language,
            "description": self.description,
            "starter_code": self.starter_code,
            "expected_output": self.expected_output,
            "hints": self.hints,
            "format": "markdown",
        }


@dataclass
class VideoScript:
    """Generated video script resource."""
    title: str
    duration_seconds: int = 300
    scenes: List[Dict[str, str]] = field(default_factory=list)
    narration: str = ""

    def to_markdown(self) -> str:
        lines = [
            f"# {self.title}",
            f"**Duration:** {self.duration_seconds // 60}:{self.duration_seconds % 60:02d}",
            "",
        ]
        for i, scene in enumerate(self.scenes, 1):
            lines.append(f"## Scene {i}: {scene.get('title', '')} ({scene.get('duration', '')})")
            lines.append(f"**Visual:** {scene.get('visual', '')}")
            lines.append(f"**Narration:** {scene.get('narration', '')}")
            lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "video",
            "title": self.title,
            "duration_seconds": self.duration_seconds,
            "scenes": self.scenes,
            "format": "markdown",
        }


# ──────────────────────────────────────────────
# Resource Generation Agent
# ──────────────────────────────────────────────

class ResourceGenerationAgent:
    """
    Generates 5 types of learning resources from structured input.

    The agent is primarily rule-based — it structures and formats content
    without requiring LLM calls. An optional LLM provider can enrich outputs.

    Usage:
        agent = ResourceGenerationAgent()
        notes = agent.generate_course_notes(
            title="Intro to AI",
            topic="AI Fundamentals",
            concepts=["Machine Learning", "Neural Networks", "Transformers"],
        )
        print(notes.to_markdown())
    """

    # ── Resource Type Registry ──
    RESOURCE_TYPES = {
        "document": {"icon": "📄", "label": "Course Notes"},
        "mindmap": {"icon": "🧠", "label": "Mind Map"},
        "exercise": {"icon": "✏️", "label": "Exercises"},
        "code": {"icon": "💻", "label": "Code Lab"},
        "video": {"icon": "🎬", "label": "Video Script"},
    }

    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        self.llm = llm_provider
        self._generation_history: List[Dict[str, Any]] = []

    # ── Generator 1: Course Notes ──

    def generate_course_notes(
        self,
        title: str,
        topic: str,
        concepts: List[str],
        content_blocks: Optional[List[Dict[str, str]]] = None,
        enrich: bool = False,
    ) -> CourseNotes:
        """
        Generate structured course notes.

        Args:
            title: The notes title.
            topic: The main topic area.
            concepts: List of key concepts to cover.
            content_blocks: Optional pre-written content blocks with headings.
            enrich: If True, use LLM to expand content blocks.

        Returns:
            CourseNotes dataclass with structured sections.
        """
        sections = []
        if content_blocks:
            for block in content_blocks:
                content = block.get("content", "")
                if enrich and self.llm:
                    enriched = self._enrich_content(content, topic)
                    content = enriched if enriched else content
                sections.append({
                    "heading": block.get("heading", "Section"),
                    "content": content,
                })
        else:
            # Default: one section per concept
            for concept in concepts:
                sections.append({
                    "heading": concept,
                    "content": self._default_section_content(concept, topic),
                })

        notes = CourseNotes(
            title=title,
            topic=topic,
            sections=sections,
            key_concepts=concepts,
            summary=self._generate_summary(concepts, topic),
            estimated_read_minutes=max(5, len(sections) * 3),
        )

        self._record("course_notes", notes.to_dict())
        return notes

    def _default_section_content(self, concept: str, topic: str) -> str:
        return (
            f"{concept} is a fundamental concept in {topic}. "
            f"Understanding {concept} provides the foundation for "
            f"advanced topics in this field."
        )

    def _generate_summary(self, concepts: List[str], topic: str) -> str:
        concept_list = ", ".join(concepts[:5])
        if len(concepts) > 5:
            concept_list += f", and {len(concepts) - 5} more"
        return (
            f"This module covers {len(concepts)} key concepts in {topic}: "
            f"{concept_list}. Each section provides detailed explanations "
            f"with examples and exercises."
        )

    def _enrich_content(self, content: str, topic: str) -> Optional[str]:
        """Use LLM to enrich a content block."""
        if not self.llm:
            return None
        try:
            response = self.llm.generate(
                prompt=(
                    f"Expand this educational content about {topic}. "
                    f"Add concrete examples and clear explanations. "
                    f"Keep it concise (2-3 paragraphs):\n\n{content}"
                ),
                system_prompt="You are an expert educator. Be clear and engaging.",
                temperature=0.5,
                max_tokens=500,
            )
            return response.content if response.success else None
        except Exception:
            return None

    # ── Generator 2: Mind Map ──

    def generate_mind_map(
        self,
        title: str,
        central_topic: str,
        subtopics: List[Dict[str, Any]],
    ) -> MindMap:
        """
        Generate a mind map as Mermaid code.

        Args:
            title: Mind map title.
            central_topic: The root topic.
            subtopics: List of {"name": str, "children": [str]} dicts.

        Returns:
            MindMap dataclass with Mermaid code.
        """
        mindmap = MindMap(
            title=title,
            central_topic=central_topic,
            branches=subtopics,
        )
        mindmap._build_mermaid()

        self._record("mind_map", mindmap.to_dict())
        return mindmap

    # ── Generator 3: Exercises ──

    def generate_exercises(
        self,
        title: str,
        topic: str,
        num_questions: int = 3,
        difficulty: str = "intermediate",
    ) -> Exercise:
        """
        Generate exercises for a topic.

        Args:
            title: Exercise set title.
            topic: The topic area.
            num_questions: Number of questions to generate (1-5).
            difficulty: beginner | intermediate | advanced.

        Returns:
            Exercise dataclass with questions.
        """
        templates = self._get_question_templates(difficulty)
        questions = []
        for i in range(min(num_questions, len(templates))):
            tmpl = templates[i]
            questions.append({
                "question": tmpl["template"].format(topic=topic),
                "points": tmpl.get("points", 10),
                "hint": tmpl.get("hint", ""),
                "rubric": tmpl.get("rubric", []),
                "type": tmpl.get("type", "short_answer"),
            })

        exercise = Exercise(
            title=title,
            questions=questions,
            total_points=sum(q["points"] for q in questions),
            estimated_minutes=num_questions * 5,
        )

        self._record("exercises", exercise.to_dict())
        return exercise

    def _get_question_templates(self, difficulty: str) -> List[Dict[str, Any]]:
        return [
            {
                "template": "Explain {topic} in your own words. Include a concrete example.",
                "points": 10,
                "type": "explanation",
                "rubric": ["Accurate definition", "Concrete example", "Clarity of explanation"],
            },
            {
                "template": "What are the three most important aspects of {topic}? Justify each with a real-world scenario.",
                "points": 15,
                "type": "analysis",
                "rubric": ["3 aspects identified", "Justification per aspect", "Real-world scenarios"],
            },
            {
                "template": "Compare and contrast two different approaches to {topic}. Which is more suitable for beginners and why?",
                "points": 12,
                "type": "comparison",
                "rubric": ["Two approaches identified", "Accurate comparison", "Beginner suitability reasoning"],
            },
            {
                "template": "Implement a minimal example of {topic} in Python. Include comments explaining each step.",
                "points": 20,
                "type": "implementation",
                "hint": "Focus on clarity over completeness. 20-30 lines is sufficient.",
                "rubric": ["Runnable code", "Comments explain steps", "Minimal but complete example"],
            },
            {
                "template": "Identify a common misconception about {topic} and explain why it's wrong.",
                "points": 8,
                "type": "debugging",
                "rubric": ["Correctly identifies misconception", "Clear explanation of error", "Correct understanding demonstrated"],
            },
        ]

    # ── Generator 4: Code Labs ──

    def generate_code_lab(
        self,
        title: str,
        description: str,
        language: str = "python",
        starter_code: str = "",
        expected_output: str = "",
        hints: Optional[List[str]] = None,
    ) -> CodeLab:
        """
        Generate a code lab exercise.

        Args:
            title: Lab title.
            description: What the student needs to implement.
            language: Programming language.
            starter_code: Initial code scaffold.
            expected_output: What a correct solution should output.
            hints: Progressive hints (most general first).

        Returns:
            CodeLab dataclass.
        """
        lab = CodeLab(
            title=title,
            description=description,
            language=language,
            starter_code=starter_code,
            expected_output=expected_output,
            hints=hints or [],
        )

        self._record("code_lab", lab.to_dict())
        return lab

    # ── Generator 5: Video Scripts ──

    def generate_video_script(
        self,
        title: str,
        topic: str,
        key_points: List[str],
        duration_seconds: int = 300,
    ) -> VideoScript:
        """
        Generate a video narration script.

        Args:
            title: Video title.
            topic: Main topic.
            key_points: Key points to cover.
            duration_seconds: Target video length in seconds.

        Returns:
            VideoScript dataclass with scene descriptions.
        """
        scene_duration = max(15, duration_seconds // len(key_points))
        scenes = []
        for i, point in enumerate(key_points, 1):
            scenes.append({
                "title": f"Point {i}: {point[:40]}",
                "duration": f"{scene_duration}s",
                "visual": f"Slide {i}: {point} — diagram, code, or animation",
                "narration": f"Now let's explore {point}. {self._expand_point(point, topic)}",
            })

        script = VideoScript(
            title=title,
            duration_seconds=duration_seconds,
            scenes=scenes,
            narration="\n\n".join(s["narration"] for s in scenes),
        )

        self._record("video_script", script.to_dict())
        return script

    def _expand_point(self, point: str, topic: str) -> str:
        return (
            f"This is a critical concept in {topic}. "
            f"Understanding {point} will help you build a solid foundation "
            f"for more advanced topics."
        )

    # ── Batch Generation ──

    def generate_all(
        self,
        topic: str,
        concepts: List[str],
    ) -> Dict[str, Any]:
        """Generate all 5 resource types for a topic."""
        return {
            "document": self.generate_course_notes(
                title=f"{topic} — Course Notes",
                topic=topic,
                concepts=concepts,
            ).to_dict(),
            "mindmap": self.generate_mind_map(
                title=f"{topic} — Mind Map",
                central_topic=topic,
                subtopics=[{"name": c, "children": []} for c in concepts[:6]],
            ).to_dict(),
            "exercise": self.generate_exercises(
                title=f"{topic} — Exercises",
                topic=topic,
                num_questions=3,
            ).to_dict(),
            "code": self.generate_code_lab(
                title=f"{topic} — Code Lab",
                description=f"Implement a simple {topic} example.",
                language="python",
                starter_code=f"# TODO: implement {topic} example\n",
                expected_output="Expected output: [your result here]",
            ).to_dict(),
            "video": self.generate_video_script(
                title=f"{topic} — Video Script",
                topic=topic,
                key_points=concepts[:4],
            ).to_dict(),
        }

    # ── History ──

    def _record(self, resource_type: str, data: Dict[str, Any]):
        self._generation_history.append({
            "type": resource_type,
            "title": data.get("title", ""),
            "timestamp": __import__("time").time(),
        })

    @property
    def history(self) -> List[Dict[str, Any]]:
        return self._generation_history

    @classmethod
    def resource_type_info(cls, resource_type: str) -> Dict[str, str]:
        return cls.RESOURCE_TYPES.get(resource_type, {"icon": "❓", "label": "Unknown"})


# ──────────────────────────────────────────────
# CLI Demo
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("╔══════════════════════════════════════════╗")
    print("║  ResourceGenerationAgent — Demo         ║")
    print("╚══════════════════════════════════════════╝")
    print()

    agent = ResourceGenerationAgent()

    # Demo 1: Course Notes
    notes = agent.generate_course_notes(
        title="Introduction to Multi-Agent Systems",
        topic="Multi-Agent AI",
        concepts=["Agent Architecture", "EventBus", "Shared Memory", "Role Specialization"],
    )
    print("─── Course Notes ───")
    print(notes.to_markdown()[:500])
    print("...\n")

    # Demo 2: Mind Map
    mindmap = agent.generate_mind_map(
        title="Multi-Agent System Overview",
        central_topic="Multi-Agent System",
        subtopics=[
            {"name": "Architecture", "children": ["Pipeline", "Router", "Blackboard"]},
            {"name": "Communication", "children": ["EventBus", "Messages", "Memory"]},
            {"name": "Evaluation", "children": ["RuleJudge", "LLMJudge", "UserSim"]},
        ],
    )
    print("─── Mind Map ───")
    print(mindmap.to_markdown())
    print()

    # Demo 3: Generate all
    all_resources = agent.generate_all(
        topic="Prompt Engineering",
        concepts=["Zero-shot", "Few-shot", "Chain-of-Thought", "System Prompts"],
    )
    print("─── All Resources Generated ───")
    for rtype, data in all_resources.items():
        info = agent.resource_type_info(data["type"])
        print(f"  {info['icon']} {info['label']}: {data['title']}")

    print(f"\nGeneration history: {len(agent.history)} items")
