# Terence-Agent — AI Agent Research Portfolio

> Building trustworthy, personalized, and production-grade multi-agent AI systems.

---

## Projects

### [A3 — Multi-Agent Personalized Learning System](projects/A3-Multi-Agent-System/)

A research prototype exploring multi-agent collaboration for personalized learning.

- **12 specialized agents** with EventBus-driven communication
- **6-dimension student profiling** from natural language
- **6 resource types**: notes, mindmaps, exercises, code labs, video scripts, extended reading
- **Self-improvement loop**: evaluate → reflect → improve
- **3-gate content safety**: AST static check → Pytest dynamic validation → LLM quality judge
- **241 tests** | 13k+ Python LOC | Streamlit dashboard

```
ProfileAgent → PlannerAgent → ResourceGenAgent → ResourceRecAgent
                                       ↓
                              EvaluationAgent → MetaReflector → ImprovementLoop
```

→ **[Project README →](projects/A3-Multi-Agent-System/)**

---

### [Veritas-Core — Trustworthy Agentic AI Platform](projects/Veritas-Core/)

The architectural evolution from A3 toward production-grade agent infrastructure.

- **Agent Runtime State Machine** — IDLE→REASONING→PLANNING→TOOL_CALLING→VALIDATING→COMPLETED
- **Secure EventBus** — trace_id + permission + audit per event
- **3-Tier Memory** — Conversation(Redis) + Profile(PostgreSQL) + History(ChromaDB)
- **Trust Layer** — Memory validation, agent permissions, injection defense
- **Agent+Tool Architecture** — 6 cognitive agents + generator tools
- **21/21 tests** | Phase 1 MVP

```
ProfileAgent → KnowledgeAgent → PlannerAgent → ResourceAgent
                                                    ↓
                                           EvaluationAgent → ReflectionAgent
```

→ **[Project README →](projects/Veritas-Core/)**

---

## Project Evolution

```
A3 Multi-Agent System (v2.8)     Veritas-Core (v1.0)
         │                              │
    Research Prototype          Production Architecture
    12 agents, pipeline          6 agents + tools, state machine
    JSON memory                  PostgreSQL + Redis + ChromaDB
    Rule-based generation        RAG-enhanced LLM generation
    3-Gate ReviewGate            4-Gate Trust Layer
                                      │
         └──────────── Evolution ──────┘
```

**A3 is the foundation. Veritas-Core is the architectural evolution.**

---

## Repository Structure

```
Terence-Agent/
├── README.md                          ← This file
├── projects/
│   ├── A3-Multi-Agent-System/         ← Research prototype
│   │   ├── src/                       ← 12 agents, EventBus, Memory, Evaluation
│   │   ├── tests/                     ← 241 tests
│   │   ├── web/                       ← Streamlit dashboard
│   │   └── docs/                      ← Architecture, competition materials
│   │
│   └── Veritas-Core/                  ← Production architecture
│       ├── src/                       ← Agents, RAG, Memory, Trust, Skills
│       ├── tests/                     ← 21 tests (Phase 1)
│       ├── designs/veritas_core/      ← 12 design documents
│       └── deployment/               ← Docker Compose
│
├── scripts/                           ← Utility scripts
└── event-report/                      ← Development logs
```

---

## Tech Stack

| Layer | A3 | Veritas-Core |
|:------|:---|:-------------|
| Language | Python 3.11+ | Python 3.11+ |
| LLM | Xunfei Spark / Mock | LLMProvider (multi-model) |
| Memory | JSON files | PostgreSQL + Redis + ChromaDB |
| Communication | AgentEventBus | SecureAgentEventBus |
| Frontend | Streamlit | Streamlit (planned: FastAPI) |
| Testing | pytest (241) | pytest (21) |
| Deployment | pip install | Docker Compose (planned) |
