"""Tests for DocumentGenerator — markdown learning document generation."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "src"))

from core.contracts import DynamicProfile, LearningPlan, PlanNode
from tools.document_generator import (
    DocumentGenerator,
    GeneratedDocument,
    DocumentSection,
)


@pytest.fixture
def doc_gen():
    return DocumentGenerator()


@pytest.fixture
def single_node_plan():
    return LearningPlan(
        nodes=[
            PlanNode(
                title="Introduction to AI",
                level=1,
                concepts=["ai_basics", "machine_learning"],
                depth="standard",
                resource_types=["notes", "exercises"],
                exercises_count=3,
                estimated_minutes=45,
                teaching_strategy="text_step_by_step",
                rationale="Foundation knowledge required",
            ),
        ],
        total_minutes=45,
        strategy_rationale="Beginner-friendly introduction",
    )


@pytest.fixture
def multi_node_plan():
    return LearningPlan(
        nodes=[
            PlanNode(
                title="AI Foundations",
                level=1,
                concepts=["ai_basics"],
                depth="standard",
                resource_types=["notes", "exercises"],
                exercises_count=3,
                estimated_minutes=30,
                teaching_strategy="text_step_by_step",
            ),
            PlanNode(
                title="Prompt Engineering",
                level=2,
                concepts=["prompt_design", "few_shot"],
                depth="deep_dive",
                resource_types=["notes", "mindmap", "codelab", "exercises"],
                exercises_count=5,
                estimated_minutes=60,
                teaching_strategy="visual_diagram_focus",
            ),
        ],
        total_minutes=90,
        strategy_rationale="Two-stage learning: foundation → specialization",
    )


class TestDocumentGenerator:
    """DocumentGenerator — document generation tests."""

    def test_generates_document(self, doc_gen, single_node_plan):
        doc = doc_gen.generate(single_node_plan, title="Test Document")

        assert doc is not None
        assert isinstance(doc, GeneratedDocument)
        assert doc.title == "Test Document"

    def test_document_has_title_section(self, doc_gen, single_node_plan):
        doc = doc_gen.generate(single_node_plan, title="AI Learning Guide")

        markdown = doc.to_markdown()
        assert "# AI Learning Guide" in markdown

    def test_document_has_overview(self, doc_gen, multi_node_plan):
        doc = doc_gen.generate(multi_node_plan, title="Test")

        markdown = doc.to_markdown()
        assert "## Overview" in markdown
        assert "90 minutes" in markdown

    def test_document_has_learning_path_table(self, doc_gen, multi_node_plan):
        doc = doc_gen.generate(multi_node_plan, title="Test")

        markdown = doc.to_markdown()
        assert "## Learning Path" in markdown
        assert "| # | Module |" in markdown

    def test_document_has_node_sections(self, doc_gen, multi_node_plan):
        doc = doc_gen.generate(multi_node_plan, title="Test")

        markdown = doc.to_markdown()
        assert "## Module 1: AI Foundations" in markdown
        assert "## Module 2: Prompt Engineering" in markdown

    def test_empty_plan_generates_minimal_document(self, doc_gen):
        plan = LearningPlan(
            nodes=[],
            total_minutes=0,
            strategy_rationale="No nodes available",
        )
        doc = doc_gen.generate(plan, title="Empty Plan")

        assert doc.metadata["node_count"] == 0
        markdown = doc.to_markdown()
        assert "# Empty Plan" in markdown
        assert "## Overview" in markdown

    def test_document_metadata(self, doc_gen, multi_node_plan):
        doc = doc_gen.generate(multi_node_plan, title="Test")

        assert doc.metadata["node_count"] == 2
        assert doc.metadata["total_minutes"] == 90
        assert doc.metadata["strategy"] == "Two-stage learning: foundation → specialization"
        assert doc.generated_at != ""

    def test_document_section_has_required_fields(self, doc_gen, single_node_plan):
        doc = doc_gen.generate(single_node_plan, title="Test")

        for section in doc.sections:
            assert section.heading != ""
            assert section.level >= 1

    def test_document_serializable(self, doc_gen, single_node_plan):
        doc = doc_gen.generate(single_node_plan, title="Test")

        d = doc.to_dict()
        assert d["title"] == "Test"
        assert "sections" in d
        assert "metadata" in d
        assert "generated_at" in d

    def test_profile_context_stored(self, doc_gen, single_node_plan):
        context = {"student_id": "s1", "knowledge_base": "junior_dev"}
        doc = doc_gen.generate(single_node_plan, title="Test", profile_context=context)

        assert doc.metadata["profile_context"]["student_id"] == "s1"
        assert doc.metadata["profile_context"]["knowledge_base"] == "junior_dev"

    def test_node_section_includes_concepts(self, doc_gen, multi_node_plan):
        doc = doc_gen.generate(multi_node_plan, title="Test")

        markdown = doc.to_markdown()
        assert "ai_basics" in markdown
        assert "prompt_design" in markdown

    def test_node_section_includes_strategy(self, doc_gen, single_node_plan):
        doc = doc_gen.generate(single_node_plan, title="Test")

        markdown = doc.to_markdown()
        assert "text_step_by_step" in markdown
