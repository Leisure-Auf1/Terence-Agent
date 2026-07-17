# Terence-Agent — AI Agent Engineering Portfolio

> **Multi-Repository Orchestration** | Architecture Governance | 1573 Tests Total

*Engineering hub for the Veritas-Core Framework and A3 Learning System. Defines architecture rules, tracks development progress, and operates the Agent Team pipeline.*

---

## Repository Evolution

```
┌──────────────────────────────────────────────────────────────┐
│                   Terence-Agent                              │
│              Architecture Governance Hub                     │
│                                                              │
│  skills/ · event-report/ · error-registry/                  │
│  preflight · agent-team/ · architecture-constraints/        │
└──────────────────────────┬───────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                │
┌──────────────────┐ ┌──────────────────┐  │
│  Veritas-Core    │ │ A3-Multi-Agent   │  │
│  (Framework)     │ │ (Application)    │  │
│                  │ │                  │  │
│  pip install     │ │ depends on       │  │
│  veritas-core    │ │ veritas-core     │  │
│                  │ │                  │  │
│  558 tests       │ │  1130 tests      │  │
│  77 modules      │ │  86 modules      │  │
│  9 subsystems    │ │  9 agents        │  │
└──────────────────┘ └──────────────────┘  │
          ▲                ▲                │
          │                │                │
          └────────────────┴────────────────┘
                           │
                     Extracted from A3
                     Phase 7.0 (July 2026)
```

---

## Repository Responsibilities

### 1. Veritas-Core — Agent Runtime Framework
> [github.com/Leisure-Auf1/Veritas-Core](https://github.com/Leisure-Auf1/Veritas-Core)

| Component | Description |
|:----------|:------------|
| Runtime Engine | State machine execution with hooks, events, observers |
| SDK | Public API (RuntimeClient, TaskRequest, TaskResult) |
| Plugins | Extensible hook-based plugin system |
| Recovery | Retry, rollback, fallback, memory repair |
| Lifecycle | Agent OS: CREATED→READY→RUNNING→TERMINATED |
| Distributed | Multi-node event bus, remote execution |
| Security | Permission matrix, tool gateway, prompt guard, audit |
| Memory | Student memory, experience memory, extraction |
| Benchmark | Failure injection, scenario testing, metrics |
| CLI | `veritas run | status | trace | plugins | demo` |

**Status:** Active — independently installable via `pip install veritas-core`

### 2. A3-Multi-Agent-System — AI Learning Application
> [github.com/Leisure-Auf1/A3-Multi-Agent-System](https://github.com/Leisure-Auf1/A3-Multi-Agent-System)

| Component | Description |
|:----------|:------------|
| Agents (9) | Profile, Planner, Resource, Tutor, Evaluation, Reflection, etc. |
| Multimodal Gateway | 7 resource types, 3-level fallback |
| Product API v2 | 20 REST endpoints (auth, chat, profile, learning, resources, eval) |
| Web UI | ChatGPT-style streaming Streamlit interface |
| Data Layer | SQLite (users, profiles, resources, learning records) |

**Status:** Phase 9.5 — Multimodal generation live, product API operational

---

## This Repository Contains

```
Terence-Agent/
├── architecture-constraints/    # Stack rules, context scoping, error cascade
├── error-registry/              # 38 known error codes (L0–L3)
├── event-report/                # Daily operation logs
├── task-progress/               # Cross-session progress tracking
├── skill-manager/               # Skill registry (50+ skills)
├── agent-team/                  # 5 agent definitions (guidance, developer, debugger, executor, logger)
├── scripts/
│   └── check-preflight.sh       # 9-step preflight gate (SHA, risk, entropy, PII)
├── sync.sh                      # Skills → markdown sync
├── projects/                    # Historical project snapshots
└── .hermes/                     # Preflight cache + checkpoints
```

### What This Repo Does NOT Contain
- ❌ Runtime engine code (→ Veritas-Core)
- ❌ Application code (→ A3-Multi-Agent-System)
- ❌ Agent business logic (→ A3 agents)
- ❌ Package dependencies

---

## Key Workflows

### Preflight Gate
Every project starts with a mandatory preflight check:
```bash
cd ~/Terence-Agent && bash scripts/check-preflight.sh
```
Validates: SHA fingerprint, branch status, risk tier, event-report state, PII scan.

### Agent Team Pipeline
```
Guidance → Developer → Debugger → Executor → Logger
```
Multi-agent orchestration for complex development tasks.

### PR Workflow
All changes go through: `branch → commit → push → PR → self-review → squash merge`

---

## Getting Started

```bash
git clone https://github.com/Leisure-Auf1/Terence-Agent.git
cd Terence-Agent
bash scripts/check-preflight.sh
```

This repository is the entry point for all AI agent engineering work. Start here, then navigate to the appropriate project repository.

---

## Quick Links

| Resource | Link |
|:---------|:-----|
| Architecture Constraints | [architecture-constraints/](architecture-constraints/) |
| Error Registry | [error-registry/](error-registry/) |
| Event Reports | [event-report/](event-report/) |
| Skill Manager | [skill-manager/](skill-manager/) |
| Agent Team | [agent-team/](agent-team/) |

---

## License

MIT
