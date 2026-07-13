# Veritas-Core — Trustworthy Agentic AI Platform

> *The architectural evolution from A3 toward production-grade agent infrastructure.*
>
> **Phase 1 MVP** | 21/21 tests | Runtime state machine | Core contracts

---

## What is Veritas-Core?

Veritas-Core is not a Chatbot, not a demo, and not an "agent showcase."

It's a **production-oriented agent infrastructure** designed for reliability, security, and observability — evolved from the [A3 Multi-Agent System](../A3-Multi-Agent-System/).

> **"Veritas"** = Trust. Content reliability, agent accountability, and memory integrity are first-class concerns.

---

## Architecture

```
                        ┌──────────────────────────┐
                        │         User              │
                        └─────────────┬────────────┘
                                      │
┌─────────────────────────────────────▼─────────────────────────────────────┐
│                          FastAPI + Orchestrator                             │
│                                                                             │
│   ┌──────────┐  ┌───────────────┐  ┌──────────┐  ┌──────────────────┐     │
│   │ProfileAgent│  │KnowledgeAgent │  │PlannerAgent│  │  ResourceAgent   │     │
│   │ 画像构建    │  │ RAG知识检索    │  │ 路径规划    │  │ Agent+Tool调度    │     │
│   └──────────┘  └───────────────┘  └──────────┘  └──────┬───────────┘     │
│                                                          │                  │
│   ┌──────────────────┐        ┌──────────────────┐      │                  │
│   │ EvaluationAgent  │───────▶│ ReflectionAgent  │      │                  │
│   │ 学习+Agent双评估   │        │ 画像+路径调整      │◄─────┘                  │
│   └──────────────────┘        └──────────────────┘                         │
│                                                                             │
│                    ┌─────────────────────────────┐                         │
│                    │       Skill Router           │                         │
│                    │  Intent→Match→Permission→Load│                         │
│                    └─────────────┬───────────────┘                         │
│                                  │                                          │
│   ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│   │ Document │ │   PPT    │ │   Quiz   │ │   Code   │ │ MindMap  │       │
│   │Generator │ │Generator │ │Generator │ │Generator │ │Generator │       │
│   └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└───────────────────────────────────────────────────────────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         ▼                        ▼                        ▼
┌─────────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
│   RAG Engine    │  │  Memory (3-Tier)    │  │   Trust Layer        │
│                 │  │                     │  │                      │
│ Parser→Chunker  │  │ Conversation(Redis) │  │ Memory Validation    │
│ →Embedder→VDB   │  │ Profile(PostgreSQL) │  │ Agent Permission     │
│ →Retriever      │  │ History(PG+Chroma)  │  │ Prompt Injection     │
│                 │  │                     │  │ Content Grounding    │
└─────────────────┘  └─────────────────────┘  └──────────────────────┘
```

---

## Core Design

### Agent Runtime State Machine

Every agent runs through a 10-state lifecycle:

```
IDLE → REASONING → PLANNING → TOOL_CALLING → VALIDATING → COMPLETED
  ↑                                                           │
  └─────────────────── REFLECTION ←───────────────────────────┘
```

With retry logic, checkpointing, and full state trace auditing.

### Agent + Tool Architecture

**6 Cognitive Agents** (reasoning + decision) + **5 Generator Tools** (execution):

| Agent | Responsibility |
|:------|:---------------|
| ProfileAgent | Student profiling (8-dim, rule+LLM) |
| KnowledgeAgent | RAG knowledge retrieval |
| PlannerAgent | Adaptive learning path planning |
| ResourceAgent | Resource generation orchestration |
| EvaluationAgent | Dual evaluation (learning + agent) |
| ReflectionAgent | Profile update + path adjustment |

| Tool | Output |
|:-----|:-------|
| DocumentGenerator | Markdown course notes |
| PPTGenerator | .pptx presentations |
| QuizGenerator | 3-level exercises |
| CodeLabGenerator | Runnable Python labs |
| MindMapGenerator | Mermaid diagrams |

### 3-Tier Memory

| Tier | Storage | Purpose |
|:-----|:--------|:--------|
| Conversation | Redis (TTL=24h) | Short-term session context |
| Profile | PostgreSQL | Long-term student model |
| History | PostgreSQL + ChromaDB | Learning records + vector search |

### Trust Layer

- **Memory Trust**: 6-step validation pipeline, dual-state storage (candidate/confirmed)
- **Agent Permission**: Capability matrix per agent, Tool Call Gateway
- **Prompt Injection**: 4-layer defense (Sanitize → Detect → Isolate → Validate)
- **Content Grounding**: Source check → RAG citation verification → Hallucination detection

---

## Current Status (Phase 1 MVP)

```
✅ Architecture Freeze          ✅ 12 design documents
✅ Agent Runtime State Machine  ✅ 6 agent definitions
✅ Secure EventBus              ✅ Memory models + manager
✅ Core contracts (13 types)    ✅ Provider abstraction
✅ ProfileAgent (dual-mode)     ✅ PlannerAgent
✅ 21/21 tests passing          ✅ Integration tests
```

### Quick Test

```bash
cd projects/Veritas-Core
PYTHONPATH=src:$PYTHONPATH python -m pytest tests/ -v
# 21 passed
```

---

## Relationship to A3

```
A3 Multi-Agent System (v2.8)     Veritas-Core (v1.0)
         │                              │
    12 agents, pipeline          6 agents + tools, state machine
    JSON memory                  PostgreSQL + Redis + ChromaDB
    Rule-based generation        RAG-enhanced LLM generation
    3-Gate ReviewGate            4-Gate Trust Layer
         │                              │
         └────────── Evolution ─────────┘
```

**A3 is the foundation. Veritas-Core is the architectural evolution toward production-grade agent infrastructure.**

---

## Project Structure

```
Veritas-Core/
├── src/
│   ├── agents/          # 6 cognitive agents
│   ├── tools/           # 5 generator tools
│   ├── rag/             # RAG engine (planned)
│   ├── memory/          # 3-tier memory
│   ├── trust/           # Trust layer (planned)
│   ├── skills/          # Skill router + lifecycle
│   ├── evaluation/      # Dual evaluation
│   ├── observability/   # Trace + analytics
│   ├── orchestrator/    # Pipeline DAG engine
│   ├── api/             # FastAPI REST
│   ├── providers/       # LLM abstraction
│   └── core/            # EventBus + contracts
├── tests/
│   ├── unit/            # Per-agent tests
│   ├── integration/     # End-to-end tests
│   └── security/        # Injection/poison/escalation tests
├── designs/veritas_core/ # 12 architecture design documents
├── deployment/          # Docker Compose (planned)
└── README.md
```

---

## Documentation

- [Architecture](designs/veritas_core/01_architecture.md)
- [Agent Design](designs/veritas_core/02_agent_design.md)
- [RAG Design](designs/veritas_core/03_rag_design.md)
- [Memory Design](designs/veritas_core/04_memory_design.md)
- [Security Architecture](designs/veritas_core/08_security_architecture.md)
- [Implementation Plan](designs/veritas_core/10_implementation_plan.md)
- [ADR (6 decisions)](designs/veritas_core/07_integration.md)

---

## Roadmap

| Phase | Content | Status |
|:------|:--------|:------:|
| Phase 0 | Architecture Freeze | ✅ |
| Phase 1 | Core agents + Memory + EventBus | ✅ |
| Phase 2 | RAG Engine + KnowledgeAgent | ⏳ |
| Phase 3 | Trust Layer (permissions, injection defense) | ⏳ |
| Phase 4 | Skill System + Generator Tools | ⏳ |
| Phase 5 | FastAPI + Docker + Deployment | ⏳ |

---

## License

MIT
