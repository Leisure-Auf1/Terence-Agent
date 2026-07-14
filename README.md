# Terence-Agent — AI Agent Research Portfolio

> Building trustworthy, personalized, and production-grade multi-agent AI systems.

---

## 🔗 Project Navigation

This repository is the portfolio hub. The actual projects live in their own repositories:

| Role | Repository | Status |
|:-----|:-----------|:------:|
| 🧪 Research Foundation | [A3-Multi-Agent-System](https://github.com/Leisure-Auf1/A3-Multi-Agent-System) | 241/245 tests |
| 🏗️ Engineering Evolution | [Veritas-Core](https://github.com/Leisure-Auf1/Veritas-Core) | 44/44 tests |

---

## Projects

### [A3 — Multi-Agent Personalized Learning System](https://github.com/Leisure-Auf1/A3-Multi-Agent-System)

> **Research Prototype**

A research prototype exploring **multi-agent collaboration for personalized learning**. Instead of a single LLM, A3 deploys a **team of 12 specialized agents** — each with a focused role — collaborating through shared memory and an EventBus.

- **12 specialized agents** with EventBus-driven communication
- **6-dimension student profiling** from natural language
- **6 resource types**: notes, mindmaps, exercises, code labs, video scripts, extended reading
- **Self-improvement loop**: evaluate → reflect → improve
- **3-gate content safety**: AST static check → Pytest dynamic validation → LLM judge
- **241/245 tests** | Streamlit dashboard

→ [Repository →](https://github.com/Leisure-Auf1/A3-Multi-Agent-System)

---

### [Veritas-Core — Trustworthy Agentic AI Platform](https://github.com/Leisure-Auf1/Veritas-Core)

> **Engineering Evolution**

The architectural evolution from A3 toward **production-grade agent infrastructure** — designed for reliability, security, and observability.

- **Agent Runtime State Machine** — IDLE→REASONING→PLANNING→TOOL_CALLING→VALIDATING→COMPLETED
- **Secure EventBus** — trace_id + permission + audit per event
- **3-Tier Memory** — Conversation(Redis) + Profile(PostgreSQL) + History(ChromaDB)
- **Trust Layer** — Memory validation, agent permissions, injection defense
- **Agent+Tool Architecture** — 6 cognitive agents + 5 generator tools
- **StorageBackend Abstraction** — MemoryStorage MVP + Redis/PostgreSQL extension points
- **44/44 tests** | Phase 1 MVP

→ [Repository →](https://github.com/Leisure-Auf1/Veritas-Core)

---

## Project Evolution

```
A3-Multi-Agent-System
        │
        │  Research Foundation
        │  Multi-agent experimentation
        │  Prototype validation
        ↓
Veritas-Core
        │
        │  Engineering Evolution
        │  Production-oriented Agent Infrastructure
        │  Runtime + Trust + Memory
```

**A3 is the research foundation. Veritas-Core is the architectural evolution — not a replacement, but a continuation into production-grade engineering.**

---

## Tech Stack

| Layer | A3 | Veritas-Core |
|:------|:---|:-------------|
| Language | Python 3.11+ | Python 3.11+ |
| LLM | Xunfei Spark / Mock | LLMProvider (multi-model) |
| Memory | JSON files | PostgreSQL + Redis + ChromaDB |
| Communication | AgentEventBus | SecureAgentEventBus |
| Frontend | Streamlit | Streamlit (planned: FastAPI) |
| Testing | pytest (241/245) | pytest (44/44) |
| Deployment | pip install | Docker Compose (planned) |

---

## Repository Map

```
Leisure-Auf1/
│
├── Terence-Agent/                          ← This repo (portfolio hub)
│   ├── README.md                           ← Project index & evolution story
│   ├── scripts/                            ← Utility scripts
│   └── event-report/                       ← Development logs
│
├── A3-Multi-Agent-System/                  ← Research prototype
│   └── 12 agents, EventBus, Memory, Streamlit
│
└── Veritas-Core/                           ← Engineering framework
    └── Runtime, Trust Layer, RAG, Storage
```

---

## License

MIT
