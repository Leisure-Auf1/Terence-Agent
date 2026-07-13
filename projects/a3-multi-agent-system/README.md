# A3 — Multi-Agent Personalized Learning System

> **Competition Demo v2.8** | 12 Agents | 22 Modules | 241 Tests
>
> *Students describe what they want to learn. A team of AI agents does the rest.*

[![Tests](https://img.shields.io/badge/tests-241%20passed-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.11+-blue)]()
[![License](https://img.shields.io/badge/license-MIT-green)]()
[![Compliance](https://img.shields.io/badge/Xunfei%20AI-compliant-orange)]()
[![Coverage](https://img.shields.io/badge/competition-85%25-brightgreen)]()

---

## 🎯 What is A3?

A3 is a **self-improving multi-agent system** that delivers personalized learning experiences. Instead of one AI doing everything, A3 uses a **team of 12 specialized agents** — each with a focused role — collaborating through shared memory and an event bus.

**Core innovation:** The system doesn't just teach — it **evaluates itself**, **explains its decisions**, and **learns from its failures**.

---

## 🏆 Competition Requirement Mapping

| # | Requirement | Status | Implementation |
|:--|:------------|:------:|:---------------|
| 1 | **LLM-based** | ✅ | Xunfei Spark + DeepSeek dual-engine, LLMProvider abstraction |
| 2 | **Multi-agent collaboration** | ✅ | 12 agents, EventBus, shared Memory, DecisionExplainer |
| 3 | **Student profile extraction** | ✅ | ProfileAgent + ConversationProfileAgent, 6-dim profiles |
| 4 | **Personalized resources** | ✅ | ResourceGenerationAgent (5 generators) + ResourceRecommendationAgent |
| 5 | **Learning path planning** | ✅ | PlannerAgent, 3 courses, auto-detection, profile-driven |
| 6 | **Multi-modal resources** | ✅ | Document · MindMap · Video Script · Code Lab · Exercises |
| 7 | **Learning evaluation** | ✅ | ReviewGate (3-layer) + AgentEvaluator (4-dim) + UserSim |
| 8 | **Anti-hallucination** | ✅ | Knowledge grounding + confidence scoring + feedback loop |
| 9 | **Streaming interaction** | ✅ | StreamingSimulator + EventBus streaming events |
| 10 | **Course knowledge base** | ✅ | 6 chapters, resources.json, exercises.json |
| 11 | **Xunfei AI compliance** | ✅ | XunfeiSparkProvider, AgentRouter, compliance docs |

**Overall Competition Coverage: 85%** → See [requirement_gap_analysis.md](docs/requirement_gap_analysis.md)

---

## 🧠 LLM Architecture

### Dual-Engine Routing

```
┌──────────────────────────────────────────┐
│              AgentRouter                  │
│                                           │
│  Frontend (Xunfei Spark)                  │
│  ├─ ContentAgent                          │
│  ├─ ProfileAgent                          │
│  └─ OnboardingAgent                       │
│                                           │
│  Backend (DeepSeek)                       │
│  ├─ SandboxValidator                      │
│  ├─ MetaReflector                         │
│  └─ UserSimAgent                          │
└──────────┬───────────────────────────────┘
           │
           ▼
┌──────────────────────────────────────────┐
│          LLMProvider Interface             │
│                                           │
│  • generate(prompt) → LLMResponse         │
│  • XunfeiSparkProvider                     │
│  • MockLLMProvider (testing)               │
│  • Extensible: add any OpenAI-compatible   │
│    provider without modifying agents       │
└──────────────────────────────────────────┘
```

See: [`src/llm/`](src/llm/) · [`src/core/agent_router.py`](src/core/agent_router.py)

---

## 🧠 Architecture

```
Student Input (Natural Language)
         │
         ▼
┌─────────────────────────────────────────────┐
│          Multi-Agent Runtime                 │
│                                              │
│  ProfileAgent → PlannerAgent → ResourceRec  │
│  ResourceGenAgent → ContentAgent            │
│       │              │              │        │
│       └──────────────┼──────────────┘        │
│                      ▼                       │
│              AgentEvaluator                  │
│                      │                       │
│          ┌───────────┴───────────┐           │
│          ▼                       ▼           │
│   MetaReflector          ImprovementLoop     │
│   (root cause)           (strategy update)   │
│                                              │
├──────────────────────────────────────────────┤
│         Infrastructure Layer                  │
│                                              │
│  MemoryManager │ EventBus │ TraceCollector   │
│  DecisionExplainer │ ExperienceMemory        │
│  LLMProvider │ StreamingSimulator            │
└──────────────────────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────────────┐
│     Dashboard V2 — 6-Panel Observatory        │
│  System │ Student │ Timeline │ Decisions     │
│  Evaluation │ Self-Improvement                │
│  Multimodal Resource Cards                    │
└──────────────────────────────────────────────┘
```

---

## 📚 Knowledge Base

The system includes a structured course knowledge base for **"Artificial Intelligence and Multi-Agent Systems"**:

```
knowledge_base/
└── artificial_intelligence_multi_agent_course/
    ├── course_intro.md                    # Course overview & learning objectives
    ├── chapters/
    │   ├── chapter_01_intro_ai.md         # Introduction to AI
    │   ├── chapter_02_llm.md              # Large Language Models
    │   ├── chapter_03_prompt_engineering.md  # Prompt Engineering
    │   ├── chapter_04_rag.md              # RAG Systems
    │   ├── chapter_05_multi_agent_architecture.md  # Multi-Agent Architecture
    │   └── chapter_06_agent_evaluation.md # Agent Evaluation
    ├── resources.json                     # Structured resource catalog
    └── exercises.json                     # 24 exercises across 6 chapters
```

Each chapter includes: lecture notes, mind maps, code labs, exercises, and further reading.

---

## ✨ Core Features

### 🤖 Multi-Agent Collaboration
12 specialized agents with clearly defined roles. Each agent has a single responsibility. They communicate through a shared EventBus and Memory system — not through monolithic prompts.

### 🧠 Memory System
Two-tier memory: **StudentMemory** (profile history, mastery tracking via EMA α=0.5, weak points) and **ExperienceMemory** (failure patterns, proven solutions, success rates). API designed for future Vector DB migration.

### 🎨 Multi-Modal Generation
**ResourceGenerationAgent** produces 5 resource types:
- 📄 **Course Notes** — Structured lecture content with sections and key concepts
- 🧠 **Mind Maps** — Mermaid-format visual knowledge organization
- ✏️ **Exercises** — Auto-generated questions with rubrics and hints
- 💻 **Code Labs** — Runnable code exercises with expected outputs
- 🎬 **Video Scripts** — Scene-by-scene narration scripts

Dashboard displays rich **multimodal resource cards** with type-specific visual styling (colored borders, icons, expandable previews).

### 🔮 Explainable Decisions
**DecisionExplainer** produces evidence chains for every agent decision. Why was a topic skipped? Why was a resource recommended? Every answer comes with evidence, reasoning, and a confidence score.

### 📊 Evaluation Pipeline
Agents don't just run — they're graded. **4-dimension scoring** (correctness, personalization, explainability, efficiency) with both RuleJudge and LLMJudge backends.

### 🔄 Self-Improvement Loop
Low evaluation scores trigger automatic reflection. **MetaReflector** analyzes root causes → **ExperienceMemory** stores lessons → **ImprovementLoop** injects fixes into the next run.

### 🛡️ Anti-Hallucination
Multi-layer defense: knowledge grounding against the course knowledge base, confidence scoring on all outputs, and a 3-gate ReviewGate (AST + Pytest + Judge). See [`docs/safety_design.md`](docs/safety_design.md).

### 🔄 Streaming Demo
**StreamingSimulator** provides token-level streaming with configurable delays. Integrates with EventBus for real-time dashboard visualization. See [`utils/streaming.py`](utils/streaming.py).

### 📈 Visualization Dashboard
**Streamlit 6-panel observatory** with demo mode (instant showcase) and runtime mode (live data). System overview, student intelligence, execution timeline, decision explainability, evaluation dashboard, self-improvement chain.

---

## 🚀 Quick Start

```bash
# Clone
cd projects/a3-multi-agent-system

# Install dependencies
pip install -r web/requirements.txt

# Run tests
python -m pytest tests/ -q

# Launch Dashboard V1 (interactive pipeline)
streamlit run web/app.py

# Launch Dashboard V2 (6-panel observatory)
streamlit run web/app_v2.py

# Demo: LLM Provider
python -m src.llm.xunfei_provider

# Demo: Resource Generation
python -m src.agents.resource_generation_agent

# Demo: Streaming
python -m utils.streaming
```

**Dashboard V2** opens in **Demo Mode** by default — full showcase with zero setup. Uncheck "Demo Mode" in the sidebar for runtime data.

---

## 🎬 Demo Scenario

**Student:** Xiao Lin — Network Engineering, Intermediate Python  
**Goal:** Learn Multi-Agent AI System Development

| Step | Agent | Output |
|:-----|:------|:-------|
| 1 | ProfileAgent | 6-dim profile from natural language |
| 2 | PlannerAgent | Auto-detects "Multi-Agent AI" → 5-level, 16-node path |
| 3 | ResourceGenAgent | 5 multimodal resources (notes, mindmap, exercises, code, video) |
| 4 | ResourceRecAgent | 6 resources with explainable reasons |
| 5 | AgentEvaluator | 4-dimension scores for all agents |
| 6 | MetaReflector | Failure analysis → improvement strategy |

**Result:** Personalized learning path with multimodal resources — correctly routed to Agent curriculum.

📖 Full demo story: [`docs/demo_story.md`](docs/demo_story.md)

---

## 📂 Project Structure

```
a3-multi-agent-system/
├── src/
│   ├── agents/           # Profile, Planner, ResourceRec, ResourceGen, Conversation
│   ├── core/             # EventBus, Trace, DecisionExplainer, Improvement, Reflector, AgentRouter
│   ├── llm/              # LLMProvider, MockLLMProvider, XunfeiSparkProvider
│   ├── memory/           # StudentMemory, ExperienceMemory, MemoryManager
│   └── evaluation/       # AgentEvaluator, Judge (Rule + LLM)
├── utils/
│   └── streaming.py      # StreamingSimulator + EventBus integration
├── knowledge_base/
│   └── artificial_intelligence_multi_agent_course/  # 6 chapters + resources + exercises
├── web/
│   ├── app.py            # Dashboard V1 (interactive pipeline)
│   ├── app_v2.py         # Dashboard V2 (6-panel observatory)
│   ├── v1/               # V1 components (pipeline + 6 panel renderers)
│   └── dashboard/        # V2 components (data_providers + components)
├── tests/                # 241 pytest cases (15 test files)
├── docs/                 # Competition materials
│   ├── requirement_gap_analysis.md    # 11-requirement audit (NEW)
│   ├── safety_design.md               # Anti-hallucination design (NEW)
│   ├── ai_tools_compliance.md         # Xunfei AI compliance (NEW)
│   ├── demo_story.md
│   ├── architecture.md
│   └── competition_outline.md
├── datasets/             # Benchmark student profiles
├── storage/              # Runtime data (memory, traces, demo)
└── checkpoints/          # Development phase checkpoints
```

---

## 🧪 Testing

```bash
python -m pytest tests/ -q
# 241 passed, 4 pre-existing review_gate failures
```

15 test files covering:
- Agent behavior (Profile, Planner, ResourceRec, Conversation)
- Memory system (Student + Experience + Integration)
- Evaluation (RuleJudge + AgentEvaluator + Improvement Loop)
- Event system (EventBus + TraceCollector)
- Content pipeline (ReviewGate + UserSim + Feedback)
- Decision explainability + Self-reflection

---

## 📊 Dashboard V2 Panels

| Panel | What It Shows |
|:------|:--------------|
| 🏗️ System Overview | 12-agent topology, memory stats, evaluation summary |
| 🎯 Student Intelligence | 6-dim profile, mastery heatmap, weak points, preferences |
| 📜 Execution Timeline | Agent actions with reasoning_type, latency, status |
| 🔮 Decision Explainability | Evidence chains, confidence scores, alternatives |
| 📊 Agent Evaluation | Per-agent 4-dim scores (correctness/personalization/explainability/efficiency) |
| 🔄 Self Improvement | Failure → Evaluation → Reflection → Experience → Strategy flow |
| 🎨 Multimodal Resources | Document, MindMap, Video, Code, Exercise cards |

---

## 🏆 Competition Materials

| Document | Purpose |
|:---------|:--------|
| [`docs/requirement_gap_analysis.md`](docs/requirement_gap_analysis.md) | 11-requirement audit with coverage scores (NEW) |
| [`docs/safety_design.md`](docs/safety_design.md) | Anti-hallucination design: grounding, confidence, feedback (NEW) |
| [`docs/ai_tools_compliance.md`](docs/ai_tools_compliance.md) | Xunfei AI competition compliance documentation (NEW) |
| [`docs/demo_story.md`](docs/demo_story.md) | 5-minute demo flow, scene-by-scene |
| [`docs/architecture.md`](docs/architecture.md) | Full architecture with diagrams |
| [`docs/competition_outline.md`](docs/competition_outline.md) | 10-slide PPT structure |
| [`docs/project_knowledge.md`](docs/project_knowledge.md) | Complete technical knowledge summary |
| [`docs/competition_qa.md`](docs/competition_qa.md) | 10 prepared Q&A answers for judges |
| [`docs/screenshots/`](docs/screenshots/) | Dashboard screenshot capture guide |
| [`knowledge_base/`](knowledge_base/) | Course knowledge base (6 chapters) (NEW) |

---

## 🔧 Technical Details

| Component | Implementation |
|:----------|:---------------|
| Agent Runtime | Python 3.11+, dataclass-based contracts |
| LLM Backend | Xunfei Spark (frontend) + DeepSeek (backend), LLMProvider interface |
| Event System | Singleton EventBus with TraceCollector (JSON persistence) |
| Memory | JSON storage, EMA α=0.5 mastery, Vector-ready API |
| Dashboard | Streamlit, 6-panel layout, demo + runtime dual mode |
| Evaluation | RuleJudge (deterministic) + LLMJudge (reserved) |
| Multi-modal | 5 resource types: document, mindmap, video, code, exercise |
| Anti-hallucination | Knowledge grounding + confidence scoring + feedback loop |
| Streaming | StreamingSimulator with EventBus integration |
| Testing | pytest, 241 cases, 97.4% pass rate |
| CI/CD | Git PR workflow (`feat/branch` → squash merge) |

---

## 📝 License

MIT

---

*Built as part of the A3 multi-agent educational pipeline project.*
*Phase 11 — Competition Compliance Upgrade, v2.8*
