# Universal Agent Engineering Framework — Architecture RFC

**Status:** Request For Comments
**Version:** 0.1.0
**Date:** 2026-07-18
**Audience:** Agent engineering teams, framework architects, governance system designers
**Classification:** Public Architecture Design

---

## Table of Contents

1. [Vision](#1-vision)
2. [Framework Architecture](#2-framework-architecture)
3. [Workflow Runtime](#3-workflow-runtime)
4. [Agent Communication Model](#4-agent-communication-model)
    - [4.8 Communication Protocol Specification](#48-communication-protocol-specification)
5. [Scope & Permission System](#5-scope--permission-system)
    - [5.8 Scope Isolation Model](#58-scope-isolation-model)
6. [Trace & Observability](#6-trace--observability)
    - [6.7 Trace Replay System](#67-trace-replay-system)
7. [Skill Registry](#7-skill-registry)
8. [Memory Architecture](#8-memory-architecture)
9. [Adapter Layer](#9-adapter-layer)
10. [Integration Patterns](#10-integration-patterns)
11. [Migration Strategy](#11-migration-strategy)
12. [Design Principles](#12-design-principles)

Appendices:
- [A: Open Design Questions](#appendix-a-open-design-questions)
- [B: Glossary](#appendix-b-glossary)
- [C: Design Decision Records](#appendix-c-design-decision-records)
- [D: References](#appendix-d-references)

---

## 1. Vision

### 1.1 The Problem: Prompt-Based Governance Has Reached Its Limit

The current generation of agent systems is overwhelmingly **prompt-governed**. An "agent" is defined by a system prompt, a set of behavioral rules written in natural language, and the expectation that a large language model will faithfully follow those rules. The governance model is **constitutional**: rules are declared, not enforced.

This approach has served as the foundation of early agent engineering, but it exhibits systemic failure modes that scale with complexity:

| Failure Mode | Manifestation | Root Cause |
|---|---|---|
| **Rule Drift** | Agent gradually deviates from constraints across long sessions | No runtime enforcement; LLM context window is the only "memory" of rules |
| **Phase Skip** | Agent omits mandatory pre/post-task checks | Text-described workflows have zero execution guarantees |
| **Permission Leak** | Agent accesses resources beyond its declared scope | Role boundaries exist only in Markdown; no gateway intercepts tool calls |
| **Observability Gap** | Error root cause is lost in free-text logs | No structured trace; reconstructing a session requires reading prose |
| **Skill Fragmentation** | Skills scattered across user directories, repo dirs, and ad-hoc scripts | No unified registry, no versioning, no dependency resolution |
| **Cross-Agent Chaos** | Multi-agent systems degrade into ad-hoc coupling | Agent A directly calls Agent B with positional args; no message contract |

The essence of the problem is captured in one observation: **when all governance is text, all enforcement is voluntary**. A prompt that says "you must not skip the validation gate" is only as effective as the model's willingness to obey it in that particular invocation.

### 1.2 The Solution: Runtime-Governed Agent Engineering

The Universal Agent Framework proposes a fundamental shift:

```
PAST:  Agent = Prompt + Rules + Human Discipline
FUTURE: Agent = Runtime + Workflow + Policy + Trace + Memory + Skills
```

In the runtime-governed model, the framework **executes** constraints, rather than **narrating** them. An agent does not "remember" to follow the workflow — the workflow engine executes each step and the agent is invoked within it. An agent does not "choose" to respect permissions — the permission gateway blocks unauthorized tool calls before they reach the agent's context. An agent does not "decide" to log its actions — every action is traced by the runtime, not by the agent.

### 1.3 Core Thesis

> **The Universal Agent Framework is to agent engineering what an operating system is to application software.** It provides the runtime guarantees — scheduling, isolation, communication, observability, resource management — that individual agents should never need to implement themselves.

### 1.4 Comparison: Two Governance Models

| Dimension | Prompt Governance (Current) | Runtime Governance (Target) |
|---|---|---|
| **Rule Storage** | Markdown documents; agents read and interpret | Structured config + code-level enforcement |
| **Constraint Enforcement** | Agent "self-discipline" — honor system | Policy Engine programmatic interception |
| **Workflow Orchestration** | Text-described phases in prompt | Workflow Engine DAG execution |
| **Permission Control** | "DO NOT do X" in system prompt | Permission Gateway code-level block |
| **Execution Record** | Free-text log files | Structured Trace Events, queryable |
| **Error Recovery** | Manual lookup in error knowledge base | Recovery Manager auto-retry/degrade |
| **Skill Management** | Scattered across user dirs and project repos | Unified Skill Registry with versioning |
| **Reproducibility** | Depends on agent's memory of context | Trace replay for exact reconstruction |

### 1.5 Framework Positioning

The Universal Agent Framework is not another application, not another prompt collection, not a refactor of any single repository. It is an independent **Agent Runtime Infrastructure** layer, positioned between LLM Providers and Agent Applications:

```
LLM Providers (OpenAI / Claude / DeepSeek / Local)
          │
          ▼
  ╔═══════════════════════════════════════╗
  ║   Universal Agent Framework          ║
  ║   (Runtime Governance Layer)         ║
  ╚═══════════════════════════════════════╝
          │
          ▼
Agent Applications (Code / Research / Automation / ...)
```

### 1.6 What This Framework Is — And Is Not

**Is:**
- A language-agnostic architecture specification for agent runtime infrastructure
- A set of abstract interfaces and contracts (not a specific implementation)
- A composable framework: every module can be used independently
- A governance upgrade path for existing prompt-based agent systems

**Is Not:**
- A wrapper around any specific LLM provider
- A prompt engineering toolkit
- A replacement for LangChain, CrewAI, or AutoGen (it operates one layer below — it is the infrastructure those frameworks could run on)
- A production deployment system (it defines the architecture; adapters handle deployment)

### 1.7 Design Analogy

| Reference System | Key Concept | Framework Equivalent |
|---|---|---|
| **LangGraph** | Workflow DAG + State | Workflow Runtime + State Machine (§3) |
| **AutoGen** | Agent communication + Roles | Event Bus + Agent Registry (§4) |
| **Temporal** | Durable workflow execution | Trace + Recovery + Policy (§3, §6) |
| **Kubernetes RBAC** | Declarative permission model | Permission Gateway (§5) |
| **OpenTelemetry** | Trace context propagation | Trace System (§6) |
| **npm / pip** | Package registry + dependency resolution | Skill Registry (§7) |
| **Agent Runtime patterns** | StateMachine, EventBus, Trace, Permission | Core architectural reference (§2-§6) |

---

## 2. Framework Architecture

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          APPLICATION LAYER                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │  │  Human   │  │ External │     │
│  │ (Planner)│  │ (Coder)  │  │(Reviewer)│  │Operator  │  │ Services │     │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘     │
│       │             │             │             │             │             │
├───────┼─────────────┼─────────────┼─────────────┼─────────────┼─────────────┤
│       │             │       SDK / CLI LAYER     │             │             │
│  ┌────┴─────────────┴─────────────┴─────────────┴─────────────┴────┐       │
│  │                    AgentSDK / Framework CLI                       │       │
│  │  • Agent Registration    • Workflow Submission   • Skill Install │       │
│  │  • Trace Query           • Policy Validation     • Memory Search │       │
│  └──────────────────────────────┬───────────────────────────────────┘       │
│                                 │                                           │
├─────────────────────────────────┼───────────────────────────────────────────┤
│                                 │          RUNTIME CORE LAYER                │
│  ┌──────────────────────────────┼───────────────────────────────────┐       │
│  │                    ┌─────────┴─────────┐                          │       │
│  │                    │  WORKFLOW RUNTIME │  ← §3                    │       │
│  │                    │  DAG Executor     │                          │       │
│  │                    │  State Machine    │                          │       │
│  │                    │  Task Lifecycle   │                          │       │
│  │                    └────────┬─────────┘                          │       │
│  │                             │                                     │       │
│  │  ┌──────────┐  ┌───────────┼───────────┐  ┌──────────────────┐  │       │
│  │  │  EVENT   │  │  POLICY   │ PERMISSION│  │  TRACE SYSTEM    │  │       │
│  │  │  BUS     │  │  ENGINE   │ GATEWAY   │  │  • Collector     │  │       │
│  │  │  Pub/Sub │  │  Rules    │ RBAC/ABAC │  │  • Timeline      │  │       │
│  │  │  Router  │  │  Validator│ Allowlist │  │  • Replay        │  │       │
│  │  │ §4       │  │  §5       │ §5        │  │  §6              │  │       │
│  │  └────┬─────┘  └─────┬─────┴─────┬─────┘  └────────┬─────────┘  │       │
│  │       │              │           │                  │            │       │
│  │  ┌────┴──────────────┴───────────┴──────────────────┴─────────┐ │       │
│  │  │                    MEMORY INTERFACE                         │ │       │
│  │  │  Short Memory  │  Long Memory  │  Knowledge Memory   §8    │ │       │
│  │  └──────────────────────────────┬──────────────────────────────┘ │       │
│  │                                 │                                 │       │
│  │  ┌──────────────────────────────┼──────────────────────────────┐ │       │
│  │  │                    SKILL REGISTRY                            │ │       │
│  │  │  Catalog • Version • Dependency • Permission  §7            │ │       │
│  │  └──────────────────────────────────────────────────────────────┘ │       │
│  └──────────────────────────────────────────────────────────────────┘       │
│                                                                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                          ADAPTER LAYER                          ← §9         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  OpenAI  │  │  Claude  │  │ DeepSeek │  │  Local   │  │  Custom  │     │
│  │ Adapter  │  │ Adapter  │  │ Adapter  │  │  Ollama  │  │ Provider │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│                                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │  Redis   │  │PostgreSQL│  │ ChromaDB │  │  Local   │  │  Custom  │     │
│  │  Memory  │  │  Memory  │  │  Memory  │  │  JSON    │  │  Memory  │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Layer Responsibilities

| Layer | Component | Responsibility | Key Abstraction |
|---|---|---|---|
| **Application** | Agents, Human Operators | Business logic, domain decisions | Agent as a function with typed I/O |
| **SDK / CLI** | AgentSDK, CLI Tools | Registration, submission, query, management | `frameworkctl` |
| **Runtime Core** | Workflow Runtime | DAG execution, state transitions, retry/recovery | `WorkflowEngine` |
| **Runtime Core** | Event Bus | Decoupled agent communication, pub/sub, routing | `EventBus` |
| **Runtime Core** | Policy Engine | Rule definition, validation, policy evaluation | `PolicyEngine` |
| **Runtime Core** | Permission Gateway | RBAC/ABAC enforcement, tool call interception | `PermissionGateway` |
| **Runtime Core** | Trace System | Structured event recording, timeline, replay | `TraceCollector` |
| **Runtime Core** | Memory Interface | Short/long/knowledge memory abstraction | `MemoryStore` (protocol) |
| **Runtime Core** | Skill Registry | Skill catalog, versioning, dependency resolution | `SkillRegistry` |
| **Adapter** | LLM Providers | Unified LLM invocation, model routing, fallback | `LLMProvider` (protocol) |
| **Adapter** | Storage Backends | Persistence for memory, trace, registry | `StorageBackend` (protocol) |

### 2.3 Core Design Decision: The Runtime Core Is a Library, Not a Service

The Runtime Core is designed as an **embeddable library** that runs in-process with the agent application. It is not a separate microservice that requires network calls. This decision is driven by:

1. **Latency**: Agent workflows involve hundreds of state transitions; crossing a network boundary on each is prohibitive
2. **Simplicity**: A library eliminates deployment complexity — no separate service to manage
3. **Portability**: Can be embedded in CLI tools, web servers, desktop apps, and CI/CD pipelines
4. **Testability**: Library APIs can be integration-tested without standing up infrastructure

The Adapter Layer is the escape hatch: when scaling requires distributed deployment, adapters bridge the library to external services (Redis for shared memory, message queues for cross-process events).

---

## 3. Workflow Runtime

### 3.1 Core Insight: Workflows Belong in the Runtime, Not in Prompts

In prompt-governed systems, workflows are described in natural language:

```
"You are a planner agent. First, analyze the user's request. Then,
break it into subtasks. Then, assign each subtask to an agent. Then,
wait for all agents to complete. Then, synthesize the results..."
```

This approach has three fatal flaws:

1. **No execution guarantee**: The model may skip steps, reorder them, or invent new ones
2. **No retry/recovery**: If step 3 fails, there is no mechanism to retry it independently
3. **No observability**: The workflow is a narrative, not a data structure — you cannot query "what step are we on?"

The Universal Agent Framework moves workflow definition **out of prompts and into code**:

```yaml
# workflows/code_review.yaml
workflow:
  name: code_review
  version: "1.0"
  schema: dag

  tasks:
    - id: static_analysis
      agent: linter
      input: "{{trigger.pr_diff}}"
      timeout: 120s
      retry:
        max: 2
        backoff: exponential

    - id: security_scan
      agent: security_scanner
      input: "{{trigger.pr_diff}}"
      timeout: 300s
      depends_on: []         # runs in parallel with static_analysis

    - id: human_review
      agent: human_gate
      input: "{{tasks.static_analysis.output}}, {{tasks.security_scan.output}}"
      depends_on: [static_analysis, security_scan]
      approval: required     # blocks until human approves

    - id: merge
      agent: pr_manager
      action: merge
      depends_on: [human_review]
      condition: "{{tasks.human_review.output.decision == 'approved'}}"
```

The prompt's role shrinks to: "You are a linter agent. Given a PR diff, produce a structured report." The workflow — ordering, parallelism, retry, human gates, conditional branching — is owned by the runtime.

### 3.2 State Machine

Every task in a workflow follows a strict state machine:

```
                    ┌─────────┐
                    │  INIT   │
                    └────┬────┘
                         │ submit
                         ▼
                    ┌─────────┐
              ┌────▶│PLANNING │
              │     └────┬────┘
              │          │ plan_complete
              │          ▼
              │     ┌─────────────┐
     replan   │     │  EXECUTION  │
              │     └──────┬──────┘
              │            │
              │     ┌──────┼──────┐
              │     │      │      │
              │     ▼      ▼      ▼
              │  ┌──────┐ ┌────┐ ┌───────┐
              │  │FAILED│ │DONE│ │WAITING│ (human approval / external signal)
              │  └──┬───┘ └──┬─┘ └───┬───┘
              │     │        │       │
              │     │ retry  │       │ approved / timeout
              │     └────────┘       │
              │                      ▼
              │               ┌──────────────┐
              └───────────────│  VALIDATION  │
                              └──────┬───────┘
                                     │
                               ┌─────┼─────┐
                               │     │     │
                               ▼     ▼     ▼
                          ┌──────┐ ┌────┐ ┌──────────┐
                          │FAILED│ │PASS│ │REFLECTION│
                          └──────┘ └──┬─┘ └────┬─────┘
                                      │        │
                                      ▼        ▼
                                  ┌──────────────┐
                                  │   COMPLETE   │
                                  └──────────────┘
```

**State Definitions:**

| State | Description | Allowed Transitions |
|---|---|---|
| `INIT` | Task created, not yet validated | → PLANNING |
| `PLANNING` | Agent is decomposing the task into subtasks | → EXECUTION, FAILED |
| `EXECUTION` | Agent is performing the work | → DONE, FAILED, WAITING |
| `WAITING` | Blocked on human approval or external signal | → EXECUTION, FAILED (timeout) |
| `DONE` | Execution complete, not yet validated | → VALIDATION |
| `VALIDATION` | Output being checked against quality gates | → PASS, FAILED, REFLECTION |
| `REFLECTION` | Agent analyzing its own output for improvement | → EXECUTION (replan), PASS, FAILED |
| `PASS` | Validation passed; task ready for next step | → COMPLETE |
| `FAILED` | Terminal failure after all retries exhausted | → COMPLETE (with error) |
| `COMPLETE` | Terminal state (success or exhausted failure) | — |

**Key Rule:** State transitions are enforced by the runtime. An agent cannot self-transition — it returns a result, and the runtime decides the next state based on the result, the retry policy, and any gate conditions.

> **State Machine as an independent component:** While illustrated here within the Workflow Runtime context, the State Machine is designed as a standalone module. Any entity with a defined lifecycle — an Agent instance (IDLE → BUSY → ERROR → IDLE), a Skill activation (INSTALLED → ACTIVATED → DEACTIVATED), or a Project validation gate (PENDING → VALIDATING → PASS/FAIL) — can use the State Machine independently of any Workflow. The State Machine provides a `TransitionTable` + `TransitionGuard` interface that accepts any state enum, not just Task states.

### 3.3 Task Lifecycle Hooks

The runtime provides hook points at every state transition. Hooks are non-intrusive: they observe and potentially veto, but never modify the agent's output.

```python
class TaskHook(Protocol):
    """Lifecycle hooks for task state transitions."""

    async def on_init(self, task: Task, ctx: TaskContext) -> None: ...
    async def on_planning_start(self, task: Task, ctx: TaskContext) -> None: ...
    async def on_planning_complete(self, task: Task, plan: Plan, ctx: TaskContext) -> None: ...
    async def on_execution_start(self, task: Task, ctx: TaskContext) -> None: ...
    async def on_execution_complete(self, task: Task, result: Any, ctx: TaskContext) -> None: ...
    async def on_validation_start(self, task: Task, ctx: TaskContext) -> GateResult: ...
    async def on_reflection(self, task: Task, ctx: TaskContext) -> ReflectionResult: ...
    async def on_error(self, task: Task, error: Exception, ctx: TaskContext) -> ErrorAction: ...
    async def on_complete(self, task: Task, ctx: TaskContext) -> None: ...

    # ErrorAction determines: RETRY | FALLBACK | ESCALATE | TERMINATE
```

### 3.4 Retry and Recovery

The retry system is configurable per task, not written into prompts:

```yaml
retry:
  strategy: exponential_backoff   # fixed | exponential | linear
  max_attempts: 3
  initial_delay: 1s
  max_delay: 60s
  multiplier: 2.0
  retry_on:                       # which errors trigger retry
    - TimeoutError
    - RateLimitError
    - TransientLLMError
  no_retry_on:                    # which errors are immediately terminal
    - PermissionDeniedError
    - InvalidInputError
    - ContentPolicyViolation

recovery:
  on_exhausted: escalate_to_human # escalate | skip | fallback_agent | terminate
  fallback_agent: backup_planner  # alternative agent if primary fails
  dead_letter_queue: true         # persist failed task for post-mortem
```

### 3.5 Human Approval Gates

Human approval is a first-class workflow primitive, not an ad-hoc "ask the user" prompt:

```yaml
- id: deploy_production
  agent: deployer
  depends_on: [integration_tests, security_audit]
  approval:
    required: true
    message: "Deploy v{{version}} to production? Changes: {{diff_summary}}"
    timeout: 24h                 # auto-reject if no response within 24h
    default: reject              # safe default
    channels:                    # where to send the approval request
      - slack: "#deploy-approvals"
      - email: "ops@example.com"
    approvers:                   # who can approve
      - role: release_manager
      - user: "ops-lead"
```

### 3.6 DAG Execution Model

Workflows are Directed Acyclic Graphs (DAGs). The runtime:

1. **Topologically sorts** tasks by their `depends_on` declarations
2. **Maximizes parallelism**: any task whose dependencies are all `COMPLETE` is eligible for execution
3. **Enforces resource limits**: configurable `max_concurrent_tasks` per workflow
4. **Propagates context**: each task receives the outputs of its dependencies via `{{tasks.<task_id>.output}}`

```yaml
workflow:
  name: research_and_report
  max_concurrency: 4

  tasks:
    - id: search_web
      agent: web_searcher
      input: "{{trigger.topic}}"

    - id: search_papers
      agent: paper_searcher
      input: "{{trigger.topic}}"

    - id: search_code
      agent: code_searcher
      input: "{{trigger.topic}}"

    # All three searches run in parallel (no dependencies)

    - id: synthesize
      agent: synthesizer
      depends_on: [search_web, search_papers, search_code]
      input:
        web_results: "{{tasks.search_web.output}}"
        papers: "{{tasks.search_papers.output}}"
        code: "{{tasks.search_code.output}}"

    - id: fact_check
      agent: fact_checker
      depends_on: [synthesize]
      input: "{{tasks.synthesize.output}}"

    - id: format
      agent: formatter
      depends_on: [fact_check]
      input: "{{tasks.synthesize.output}}"
```

---

## 4. Agent Communication Model

### 4.1 The Problem with Direct Agent-to-Agent Calls

In monolithic multi-agent systems, agents communicate by direct method invocation:

```python
# Anti-pattern: Tightly coupled agent communication
result_a = agent_a.process(input)
result_b = agent_b.process(result_a.output)
result_c = agent_c.process(result_b.summary)
```

This creates a brittle chain: changing Agent B's output schema breaks Agent C. Adding an observer between B and C requires modifying the pipeline. Debugging why C received bad input requires tracing through A → B → C manually.

### 4.2 The Event Bus Model

The Universal Agent Framework uses an **Event Bus** as the communication backbone. Agents do not call each other — they publish events and subscribe to event patterns.

```
┌──────────┐  publish("task.planner.completed", payload)   ┌──────────────┐
│  Agent   │ ─────────────────────────────────────────────▶│              │
│ Planner  │                                               │   EVENT BUS  │
└──────────┘                                               │              │
                                                           │  ┌────────┐  │
                    ┌─────────────────────────────────────▶│  │ Router │  │
                    │ subscribe("task.planner.completed")   │  └────────┘  │
                    │                                       │              │
              ┌─────┴─────┐                                 │  ┌────────┐  │
              │  Agent    │                                 │  │  Topic │  │
              │  Coder    │                                 │  │  Store │  │
              └───────────┘                                 │  └────────┘  │
                    │                                       │              │
                    │ publish("task.coder.completed", ...)  │              │
                    └──────────────────────────────────────▶│              │
                                                           └──────────────┘
```

### 4.3 Event Schema

Every event conforms to a universal schema:

```json
{
  "$schema": "https://universal-agent-framework.dev/schemas/event/1.0",
  "event_id": "evt_a1b2c3d4",
  "event_type": "task.completed",
  "timestamp": "2026-07-18T14:30:00.000Z",
  "producer": {
    "agent_id": "planner-001",
    "agent_type": "planner",
    "agent_version": "2.1.0"
  },
  "workflow": {
    "workflow_id": "wf_research_20260718_001",
    "task_id": "task_synthesize",
    "run_id": "run_x7y8z9"
  },
  "payload": {
    "status": "success",
    "summary": "Synthesized 15 sources into a 3-section report outline",
    "output_ref": "memory://run_x7y8z9/task_synthesize/output",
    "metrics": {
      "duration_ms": 3420,
      "tokens_used": 1850,
      "tool_calls": 3
    }
  },
  "metadata": {
    "correlation_id": "corr_abc123",
    "tags": ["research", "synthesis"],
    "priority": "normal"
  }
}
```

### 4.4 Event Type Taxonomy

| Event Type Pattern | Semantics | Example |
|---|---|---|
| `workflow.{action}` | Workflow-level lifecycle | `workflow.started`, `workflow.completed`, `workflow.failed` |
| `task.{action}` | Task-level lifecycle | `task.assigned`, `task.started`, `task.completed`, `task.failed`, `task.retrying` |
| `agent.{action}` | Agent-level activity | `agent.thinking`, `agent.tool_call`, `agent.tool_result` |
| `human.{action}` | Human-in-the-loop | `human.approval_requested`, `human.approved`, `human.rejected` |
| `system.{action}` | Framework-level events | `system.heartbeat`, `system.resource_warning`, `system.error` |
| `custom.{domain}.{action}` | Application-defined | `custom.evaluation.score_computed`, `custom.memory.entity_updated` |

### 4.5 Communication Patterns

The Event Bus supports four communication patterns, each appropriate for different scenarios:

**Publish/Subscribe (One-to-Many):**
```yaml
# Agent A publishes; N observers react independently
# Use for: logging, metrics, cache invalidation, notification fan-out
subscriptions:
  - pattern: "task.*.completed"
    handler: trace_collector.record
  - pattern: "task.*.completed"
    handler: metrics_service.increment
  - pattern: "task.*.failed"
    handler: alert_service.notify
```

**Request/Response (Point-to-Point over the Bus):**
```yaml
# Agent A sends a request; waits for exactly one response
# Use for: querying another agent's capability, synchronous handoffs
request:
  event_type: "query.memory.search"
  payload:
    query: "What is the user's preferred coding style?"
    top_k: 5
  response_timeout: 5s
  response_event: "query.memory.result"
```

**Broadcast (One-to-All):**
```yaml
# System-wide announcement; all agents receive it
# Use for: shutdown signals, config changes, emergency stops
broadcast:
  event_type: "system.shutdown"
  payload:
    reason: "Rate limit exceeded"
    grace_period_ms: 5000
```

**Scatter/Gather (Fan-Out + Aggregate):**
```yaml
# One request fans out to N agents; results aggregated
# Use for: parallel research, multi-perspective analysis
scatter:
  event_type: "research.query"
  payload: "{{topic}}"
  targets: [web_searcher, paper_searcher, code_searcher]
gather:
  strategy: wait_all      # wait_all | wait_any | wait_n(2)
  timeout: 60s
  aggregator: synthesizer
```

### 4.6 Event Routing Rules

The Router determines which events reach which subscribers:

```yaml
router:
  rules:
    - name: "route all task events to trace"
      match:
        event_type: "task.*"
      deliver_to: ["trace_collector"]

    - name: "route planner completions to coder"
      match:
        event_type: "task.completed"
        producer.agent_type: "planner"
      deliver_to: ["coder_pool"]

    - name: "route errors to on-call"
      match:
        event_type: "*.failed"
        payload.status: "error"
        metadata.priority: ["critical", "high"]
      deliver_to: ["alert_service", "dead_letter_queue"]

    - name: "dead letter for unmatched events"
      match:
        event_type: "*"
      deliver_to: ["dead_letter"]
      priority: -999      # lowest priority — catch-all
```

### 4.7 Why Events, Not Method Calls?

| Dimension | Direct Method Call | Event Bus |
|---|---|---|
| **Coupling** | Caller must know callee's interface | Caller only knows event schema |
| **Observability** | Must instrument each call manually | Every event is automatically traced |
| **Extensibility** | Adding a listener requires modifying the caller | New subscribers attach without touching publishers |
| **Testing** | Mock every dependency | Simulate events; test handler in isolation |
| **Recovery** | Exception propagates to caller | Failed handler doesn't affect publisher; dead letter queue catches |
| **Workflow** | Sequential only | Scatter/gather, fan-out, parallel execution natural |

### 4.8 Communication Protocol Specification

The Event Bus defines the transport layer. The Communication Protocol defines the contract layer — the formal specification of how agents exchange messages.

**Protocol versioning:**

```json
{
  "$schema": "https://universal-agent-framework.dev/schemas/event/1.0",
  "protocol_version": "1.0",                   // Negotiable at agent registration
  "supported_versions": ["1.0", "0.9"]          // Agent declares what it understands
}
```

Protocol versions are backward-compatible within the same major version. Breaking changes (schema field removal, semantic change) require a major version bump. The Event Bus rejects messages with unsupported protocol versions.

**Message serialization:**

| Format | Use Case | Requirement |
|:-----|:-----|:-----|
| **JSON** | Default wire format | All agents MUST support |
| **MessagePack** | High-throughput / binary | Optional optimization |
| **Protobuf** | gRPC-native integrations | Optional, via adapter |

**Delivery guarantees:**

| Level | Semantics | Use Case |
|:-----|:-----|:-----|
| **At-most-once** | Fire and forget; no retry | Metrics, heartbeat, `agent.idle` events |
| **At-least-once** (default) | Redeliver until acknowledged; may duplicate | `task.completed`, `approval.requested` |
| **Exactly-once** | Idempotency key; deduplication | `filesystem.write`, financial operations |

Delivery level is declared per subscription:

```yaml
subscriptions:
  - topic: "task.completed"
    handler: "handle_completion"
    delivery: at-least-once
    ack_timeout_ms: 30000
    dead_letter_topic: "dlq.task_completed"
```

**Connection lifecycle:**

```
Agent Online:
  1. Agent → Bus: REGISTER {agent_id, supported_versions, subscriptions}
  2. Bus → Agent: ACK {assigned_version, session_id}
  3. Bus → All: agent.registered event
  
Agent Offline (graceful):
  1. Agent → Bus: DEREGISTER {agent_id, reason: "shutdown"}
  2. Bus → Agent: ACK
  3. Bus → All: agent.deregistered event
  4. Bus holds pending messages for agent (TTL: configurable, default 5 min)

Agent Offline (crash):
  1. Bus detects heartbeat timeout (default: 30s)
  2. Bus → All: agent.error {reason: "heartbeat_timeout"}
  3. Bus routes pending messages to dead letter topic
```

**Heartbeat:**

All active agents MUST send heartbeat events at a configurable interval (default: 10s). Missed heartbeats trigger connection health checks. Three consecutive misses → agent marked offline.

```json
{
  "event_type": "agent.heartbeat",
  "source": {"agent_id": "planner"},
  "metadata": {"load": 0.3, "active_tasks": 2}
}
```

---

## 5. Scope & Permission System

### 5.1 From "Prompt Permission" to "Runtime Permission"

In prompt-governed systems, permissions are narrated:

```markdown
## Agent: planner
### Allowed Actions
- Read memory to understand user context
- Search knowledge base for relevant concepts
- Plan task decomposition

### Forbidden Actions
- DO NOT write files to disk
- DO NOT read secrets from environment
- DO NOT make network calls outside the knowledge base API
```

The model may follow these instructions. Or it may not. There is no enforcement.

In the Runtime-Governed model, permissions are **intercepted at the gateway layer** — before the agent's tool call reaches the system, and before the LLM provider sees the result.

### 5.2 Permission Gateway Architecture

```
┌──────────┐     ┌──────────┐     ┌─────────────────┐     ┌──────────────┐
│  Agent   │────▶│  Policy  │────▶│   PERMISSION    │────▶│  System      │
│  Tool    │     │  Engine  │     │   GATEWAY       │     │  Resources   │
│  Call    │     │ Evaluate │     │                 │     │              │
└──────────┘     │ Rules    │     │  ┌───────────┐  │     │  ┌────────┐  │
                 └──────────┘     │  │  RBAC     │  │     │  │  FS    │  │
                                  │  │  Rules    │  │     │  └────────┘  │
                                  │  └───────────┘  │     │              │
                                  │  ┌───────────┐  │     │  ┌────────┐  │
                                  │  │  ABAC     │  │     │  │  DB    │  │
                                  │  │  Policy   │  │     │  └────────┘  │
                                  │  └───────────┘  │     │              │
                                  │  ┌───────────┐  │     │  ┌────────┐  │
                                  │  │  Audit    │  │     │  │  API   │  │
                                  │  │  Logger   │  │     │  └────────┘  │
                                  │  └───────────┘  │     │              │
                                  └────────┬────────┘     └──────────────┘
                                           │
                                           │ DENY
                                           ▼
                                     ┌──────────┐
                                     │  Error:  │
                                     │  PERMISSION_
                                     │  DENIED  │
                                     └──────────┘
```

The Permission Gateway sits **between the agent's tool call and the system resource**. It is not a prompt. It is an interceptor.

### 5.3 Permission Configuration

Permissions are declared in YAML, versioned alongside agent definitions:

```yaml
# agents/planner/permissions.yaml
agent: planner
version: "1.2.0"

# Role-Based Access Control (RBAC)
rbac:
  roles:
    - planner

  roles_definition:
    planner:
      allow:
        - memory.read
        - memory.search
        - knowledge_base.query
        - knowledge_base.list_courses
        - skill.invoke:task_planner
        - skill.invoke:complexity_estimator
        - event.publish:task.planned
        - event.publish:task.assigned
        - human.request_approval

      deny:
        - filesystem.write
        - filesystem.delete
        - secret.read
        - secret.list
        - network.external_api
        - agent.impersonate
        - system.shutdown

# Attribute-Based Access Control (ABAC) — context-sensitive rules
abac:
  - name: "can only read memory for the current user"
    effect: deny
    condition:
      action: memory.read
      resource_owner_not_in: "{{context.current_user_id}}"

  - name: "can only plan within own workflow"
    effect: deny
    condition:
      action: task.assign
      target_workflow_not: "{{context.current_workflow_id}}"

  - name: "cannot access secrets after 3 failed attempts"
    effect: deny
    condition:
      action: secret.read
      context.failed_attempts_gte: 3

# Resource limits (throttling, not permission)
limits:
  max_tool_calls_per_minute: 60
  max_tokens_per_task: 100000
  max_concurrent_subtasks: 10

# Inheritance
inherits: base_agent
```

### 5.4 Policy Engine Evaluation Order

The Policy Engine evaluates rules in a defined order:

```
1. Explicit DENY  →  REJECT immediately (deny takes precedence)
2. Explicit ALLOW →  PERMIT if no deny matched
3. ABAC Rules     →  Evaluate context-conditional rules
4. Inheritance    →  Check parent agent policies
5. Default        →  REJECT (default-deny: nothing not explicitly allowed is denied)
```

**Policy evaluation is synchronous and non-LLM-dependent.** It runs as pure rule evaluation — no model call, no latency, no ambiguity.

### 5.5 Permission Context

The ABAC system receives a rich context object at evaluation time:

```python
@dataclass
class PermissionContext:
    """Context available to all permission rules."""
    agent_id: str
    agent_type: str
    agent_version: str
    workflow_id: str
    task_id: str
    run_id: str
    current_user_id: str
    current_session_id: str
    tool_name: str               # e.g., "filesystem.write"
    tool_arguments: dict         # full arguments for fine-grained checks
    resource_path: str           # e.g., "/data/users/123/profile.json"
    timestamp: datetime
    failed_attempts: int         # running counter for rate-limiting rules
    environment: str             # "development" | "staging" | "production"
```

### 5.6 Resource Types

| Resource Type | Operations | Description |
|---|---|---|
| `filesystem` | read / write / delete / list | File system access |
| `memory` | read / write / search / clear | Memory read/write |
| `secret` | read / list | API Keys / passwords / certificates |
| `network` | external_api / internal_api / download | Network calls |
| `git` | commit / push / force_push / branch | Version control |
| `tool` | exec / install / configure | Executable tools |
| `workflow` | inspect / modify / cancel / create | Workflow operations |
| `agent` | spawn / stop / configure / register | Agent lifecycle |
| `skill` | invoke / install / configure | Skill management |

### 5.7 Audit Trail

Every permission decision — allow or deny — is recorded:

```json
{
  "audit_id": "aud_9f8e7d6c",
  "timestamp": "2026-07-18T14:30:05.123Z",
  "decision": "deny",
  "rule": "planner_cannot_write_files",
  "agent_id": "planner-001",
  "agent_type": "planner",
  "tool": "filesystem.write",
  "resource": "/etc/passwd",
  "context": {
    "workflow_id": "wf_123",
    "task_id": "task_456",
    "environment": "production"
  },
  "reason": "Agent type 'planner' explicitly denied action 'filesystem.write'"
}
```

### 5.8 Scope Isolation Model

Permission controls *what an agent can do*. Scope controls *where its boundaries lie*. Scope isolation prevents:

- **Memory leakage**: Agent A's Short Memory is invisible to Agent B
- **Tool namespace pollution**: Agent A's tool results don't enter Agent B's context
- **Side-effect collision**: Two agents modifying the same file without coordination
- **Cross-agent prompt injection**: Agent B cannot seed content into Agent A's LLM context

**Isolation dimensions:**

| Dimension | Mechanism | Default |
|:-----|:-----|:-----|
| **Runtime Sandbox** | Per-agent execution context; optional subprocess/container | Same process (configurable) |
| **Memory Namespace** | `agent:<id>` prefix on all memory keys; cross-agent reads require explicit `allow: [memory.cross_agent_read]` | Isolated |
| **Tool Visibility** | Tools are registered per-agent; Agent A does not see Agent B's tool set | Isolated |
| **Context Boundary** | Event Bus messages are filtered by agent subscription; no agent receives events it didn't subscribe to | Isolated |
| **Filesystem Scope** | `filesystem.write` permissions scoped to agent-specific paths; wildcard paths forbidden without audit | Isolated |
| **LLM Provider** | Each agent can use a different provider/model; no cross-agent prompt leakage | Isolated |

**Scope configuration:**

```yaml
agent:
  planner:
    scope:
      memory_namespace: "agent:planner"
      allow_cross_agent:
        - memory.read: ["agent:reviewer"]       # Planner can read Reviewer's memory
      sandbox: process                           # process | container | subprocess
      max_concurrent_tasks: 1
```

**Default isolation policy:** All agents are fully isolated by default. Cross-agent access requires explicit `allow_cross_agent` declarations. This is the runtime equivalent of §4's principle: "Agent A does not call Agent B directly" — they communicate only through the Event Bus.

---

## 6. Trace & Observability

### 6.1 From Free-Text Event Reports to Structured Trace

The current state of agent observability is free-text log files — Markdown documents where agents (or humans) narrate what happened:

```markdown
## Session 2026-07-18
- Planner started, analyzed the request
- Planner assigned task to Coder
- Coder encountered a syntax error, retried
- Coder completed the implementation
- Reviewer approved the change
```

This is better than nothing. But it is fundamentally unqueryable: "Show me every task that took more than 30 seconds" requires reading prose. "Reconstruct the exact sequence of tool calls for the failed deploy" requires a human to manually piece together scattered log entries.

### 6.2 Unified Trace Schema

The Universal Agent Framework replaces free-text reports with structured trace events:

```json
{
  "$schema": "https://universal-agent-framework.dev/schemas/trace/1.0",
  "trace_id": "trace_a1b2c3d4",
  "span_id": "span_x7y8z9",
  "parent_span_id": "span_w6v5u4",
  "trace_type": "agent.tool_call",

  "timestamp": "2026-07-18T14:30:05.123Z",
  "duration_ms": 234,

  "workflow": {
    "workflow_id": "wf_research_20260718_001",
    "task_id": "task_synthesize",
    "run_id": "run_x7y8z9"
  },

  "agent": {
    "agent_id": "synthesizer-001",
    "agent_type": "synthesizer",
    "agent_version": "2.1.0"
  },

  "action": {
    "name": "llm.completion",
    "provider": "anthropic",
    "model": "claude-sonnet-4-6",
    "input_summary": "Synthesize 15 sources into report outline [truncated to 256 chars]",
    "input_size_bytes": 12450,
    "output_summary": "3-section outline with key findings [truncated to 256 chars]",
    "output_size_bytes": 3200
  },

  "reasoning": {
    "type": "llm",
    "confidence": 0.85,
    "evidence": [
      "source_web_results",
      "source_papers",
      "user_preference_structured_format"
    ],
    "alternatives_considered": 3
  },

  "status": "success",
  "error": null,

  "metadata": {
    "tokens_input": 8500,
    "tokens_output": 1200,
    "cost_estimate_usd": 0.034,
    "temperature": 0.3,
    "tags": ["synthesis", "llm_call"]
  }
}
```

### 6.3 Trace Architecture: Two-Tier Collection

```
┌──────────────────────────────────────────────────────────────────┐
│                        AGENT RUNTIME                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                      │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │                      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘                      │
│       │             │             │                              │
│       │    emit()   │    emit()   │    emit()                    │
│       ▼             ▼             ▼                              │
│  ┌────────────────────────────────────────────┐                  │
│  │         IN-MEMORY TRACE BUFFER             │  Tier 1: Hot    │
│  │  • Ring buffer (last 10,000 events)        │  Real-time      │
│  │  • Dashboard reads directly                │  Queryable      │
│  │  • Zero serialization overhead             │                 │
│  └──────────────────┬─────────────────────────┘                 │
└─────────────────────┼───────────────────────────────────────────┘
                      │ flush (async, batched)
                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                    PERSISTENT TRACE STORE                        │
│  ┌────────────────────────────────────────────┐  Tier 2: Cold   │
│  │  Session-organized JSON / SQLite / Remote   │  Persistent     │
│  │  • Full history, no eviction                │  Archived       │
│  │  • Query by session, agent, status, time    │  Replayable     │
│  │  • Compress on session close                │                 │
│  └────────────────────────────────────────────┘                 │
└──────────────────────────────────────────────────────────────────┘
```

**Tier 1 (In-Memory Buffer):** A ring buffer holding the most recent N events. Dashboard and real-time monitors read from this buffer. No serialization, no I/O — sub-microsecond overhead per event.

**Tier 2 (Persistent Store):** Asynchronously flushed from the buffer. Organized by session. Supports time-range queries, agent-type filters, and full-text search on summaries. Implementations: local JSON (default), SQLite (single-node), remote (adapter for Elasticsearch / ClickHouse / Datadog).

### 6.4 Execution Timeline

The trace system automatically constructs a Gantt-like execution timeline from trace events:

```
Workflow: research_and_report  |  Session: 2026-07-18  |  Duration: 4m 12s
────────────────────────────────────────────────────────────────────────────
TASK                │ 0s      30s      60s      90s     120s     150s     180s
────────────────────┼────────────────────────────────────────────────────────
search_web          │ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
search_papers       │ ██████████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
search_code         │ ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
synthesize          │          ░░░░░░░░░░░░░░░░████████████░░░░░░░░░░░░░░░░░░
fact_check          │                              ░░░░░░░░░██████░░░░░░░░░░░
format              │                                        ░░░░░░░████████░░
human_review (WAIT) │                                                  ░░░████
────────────────────┴────────────────────────────────────────────────────────
  ████ = agent active    ░░░░ = waiting (dependency)    ░░░░ = WAITING (human)
```

### 6.5 Trace-Enabled Capabilities

| Capability | How Trace Enables It |
|---|---|
| **Execution Timeline** | Expand Trace Tree by timestamp → Gantt visualization |
| **Debugging** | Locate failed Span → expand context → inspect input/output → link to error knowledge base |
| **Evaluation** | Aggregate all runs → compute success rate / latency distribution / retry frequency |
| **Replay** | Save Trace + inputs → replay in new environment → reproduce bugs |
| **Monitoring** | Real-time Trace stream → anomaly detection → `agent.error` event triggers alert |
| **Cost Tracking** | Sum `llm.call` spans per run → aggregate token consumption and cost |

### 6.6 Debugging and Replay Commands

```bash
# Replay a specific workflow run
frameworkctl trace replay --run-id run_x7y8z9

# Diff two runs of the same workflow
frameworkctl trace diff --run-id run_x7y8z9 --against run_a1b2c3

# Show all tool calls by a specific agent
frameworkctl trace query --agent-type planner --action "tool_call.*"

# Export trace for external analysis
frameworkctl trace export --run-id run_x7y8z9 --format jsonl > trace.jsonl
```

### 6.7 Trace Replay System

Trace replay enables exact reproduction of a past workflow execution. Unlike free-text logs (which describe what happened), structured traces contain sufficient data to **re-execute** the same sequence deterministically.

**Replay architecture:**

```
Past Run Trace (JSONL)          Replay Environment
        │                              │
        ▼                              │
┌───────────────┐                      │
│ Replay Engine │──────────────────────►
│               │  1. Load trace        │
│               │  2. Extract inputs    │
│               │  3. Inject inputs     │
│               │  4. Execute nodes     │
│               │  5. Compare outputs   │
└───────┬───────┘                      │
        │                              │
        ▼                              ▼
  Diff Report                   Replay Trace
  (input/output delta)          (new trace_id)
```

**Replay modes:**

| Mode | Description | Use Case |
|:-----|:-----|:-----|
| **Observational** | Replay using recorded LLM responses; no live API calls | Fast validation, CI regression testing |
| **Live** | Re-execute with real LLM calls; compare to recorded | Detecting provider/model behavior drift |
| **Deterministic** | Full replay including all tool outputs (requires tool result recording) | Bug reproduction, exact debug |
| **Differential** | Run original + modified config side-by-side; diff traces | A/B testing new prompt/model/policy |

**Prerequisites for deterministic replay:**

1. **Trace completeness**: Every node input, LLM prompt, LLM response, and tool result must be recorded
2. **Idempotent tool calls**: Tools must produce the same output given the same input (or recorded results must be injected)
3. **Isolated environment**: No external state leakage (database connections, API keys, file system drift)
4. **Snapshot support**: Environment state snapshotted at replay start; restored on completion

**Snapshot and restore:**

```yaml
replay:
  mode: deterministic
  snapshot:
    enabled: true
    paths: ["~/.skills/", "./workflows/"]
    on_complete: restore       # restore | keep | discard
  diff:
    compare: ["output", "duration", "tool_calls"]
    tolerance:
      duration_ms: 500          # ±500ms variance acceptable
```

**Replay verification:**

After replay, the system produces a diff between the original trace and the replay trace:

```json
{
  "replay_id": "replay_01HQ...",
  "original_run_id": "run_x7y8z9",
  "match": false,
  "diffs": [
    {
      "node": "lint_check",
      "field": "output.score",
      "original": 92,
      "replay": 89,
      "delta": -3,
      "severity": "warn"
    }
  ]
}
```

---

## 7. Skill Registry

### 7.1 The Skill Fragmentation Problem

Current agent systems suffer from skill fragmentation across three locations:

```yaml
# Skill Sources (configurable)
user_dir/skills/          ← User-level skills (shell scripts, custom tools)
project_dir/skills/       ← Project-level skills (MCP servers, workflows)
system_dir/skills/        ← System-level skills (built-in tools)
```

Skills exist in three different locations with no unified registry. There is no version tracking, no dependency resolution, no compatibility checking. When a skill is updated, consumers are not notified. When a skill requires another skill, that dependency is implicit and untracked.

### 7.2 The Universal Skill Registry

The Skill Registry provides a single source of truth for all skills:

```
┌─────────────────────────────────────────────────────────────┐
│                     SKILL REGISTRY                          │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                   │
│  │   CATALOG       │  │   RESOLVER      │                   │
│  │   • discover    │  │   • dependency  │                   │
│  │   • search      │  │   • version     │                   │
│  │   • list        │  │   • conflict    │                   │
│  └────────┬────────┘  └────────┬────────┘                   │
│           │                    │                             │
│  ┌────────┴────────────────────┴────────┐                   │
│  │           SKILL STORE                │                   │
│  │  ┌──────────┐ ┌──────────┐          │                   │
│  │  │  Local   │ │  Remote  │          │                   │
│  │  │  Cache   │ │  Registry│          │                   │
│  │  └──────────┘ └──────────┘          │                   │
│  └─────────────────────────────────────┘                   │
│                                                             │
│  Skill Sources:                                             │
│  • file://~/.skills/                 (user)                   │
│  • file://./skills/                  (project)                │
│  • https://registry.example.com/     (remote)                 │
│  • git+https://github.com/...        (git repo)               │
└─────────────────────────────────────────────────────────────┘
```

### 7.3 Skill Metadata Schema

```yaml
# my-skill/skill.yaml
name: code-review
version: 2.1.0
display_name: "Code Review Skill"
description: "Reviews code changes for bugs, style, and security issues"

capability:
  category: review
  actions:
    - code.analyze_diff
    - code.suggest_fix
    - code.security_scan
  input_schema:
    type: object
    properties:
      diff:
        type: string
        description: "Git diff to review"
      context:
        type: string
        description: "PR description or task context"
  output_schema:
    type: object
    properties:
      findings:
        type: array
        items:
          $ref: "#/definitions/Finding"
      summary:
        type: string

permission:
  required:
    - filesystem.read
    - memory.search
  optional:
    - network.github_api

compatibility:
  framework_version: ">=1.0.0,<3.0.0"
  requires_llm: true
  min_llm_tier: medium
  supported_providers:
    - anthropic
    - openai
    - deepseek

dependencies:
  - name: diff-parser
    version: ">=1.0.0"
  - name: code-style-checker
    version: "~2.0.0"

resources:
  memory_mb: 128
  timeout_seconds: 300
  max_tokens_per_call: 50000

lifecycle:
  maturity: stable
  deprecated_message: null
  replaced_by: null

maintainer:
  name: "Framework Community"
  contact: "community@example.com"

source:
  type: git
  url: "https://github.com/example/skill-code-review"
  ref: "v2.1.0"
```

### 7.4 Registry Commands

```bash
# Install a skill
frameworkctl skill install code-review
frameworkctl skill install code-review@2.1.0          # pin version
frameworkctl skill install git+https://...@v2.1.0     # from git
frameworkctl skill install ./local-skill/              # from local dir

# Discover available skills
frameworkctl skill search "code review"                # search remote registry
frameworkctl skill list                                # list installed
frameworkctl skill list --updates                      # check for updates
frameworkctl skill info code-review                     # show metadata

# Dependency management
frameworkctl skill deps code-review                    # show dependency tree
frameworkctl skill verify                              # check all deps satisfied
frameworkctl skill update code-review                  # update to latest compatible

# Uninstall
frameworkctl skill remove code-review
```

### 7.5 Skill Resolution

When an agent declares a skill dependency, the resolver:

1. Searches local cache first
2. Falls back to configured remote registries
3. Resolves the version constraint (semver: `^2.0.0`, `~2.1.0`, `>=1.0.0,<3.0.0`)
4. Recursively resolves transitive dependencies
5. Detects version conflicts (Diamond dependency problem)
6. Installs all dependencies into a versioned namespace (`skills/code-review/2.1.0/`)
7. Validates permissions: does the requesting agent have `skill.invoke:code-review` in its allowlist?

### 7.6 Runtime Skill Invocation

Skills are invoked through the framework, not called directly:

```python
# An agent does NOT do this:
result = code_review_skill.run(diff)     # bypasses registry, bypasses permissions

# Instead, the agent requests through the framework:
result = await framework.invoke_skill(
    name="code-review",
    version="^2.0.0",                  # framework resolves the best match
    input={"diff": diff_content},
    context=task_context               # framework injects permissions, trace, memory
)
```

The framework handles: version resolution, permission check, trace instrumentation, input validation, output validation, and error handling.

---

## 8. Memory Architecture

### 8.1 The Problem with Ad-Hoc Memory

Current agent systems have fragmented memory:

- **Conversation context** lives in the LLM context window (volatile, limited by token count)
- **User profiles** live in JSON files on disk (no query interface, no versioning)
- **Experience/failure patterns** live in markdown error registries (not machine-readable)
- **Task progress** lives in separate tracking files (no cross-referencing with memory)
- **Knowledge bases** live in project directories (no unified search)

The result: an agent cannot ask "what does the user struggle with?" and get a unified answer from all memory sources.

### 8.2 Unified Memory Interface

The framework defines an abstract **Memory Interface** with three tiers:

```
┌─────────────────────────────────────────────────────────────┐
│                    MEMORY INTERFACE                         │
│                                                             │
│  ┌─────────────────┐                                        │
│  │  MemoryManager  │   Unified entry point                  │
│  │  • store()      │   Routes to correct memory tier        │
│  │  • recall()     │   Merges results from all tiers        │
│  │  • forget()     │   Handles TTL and eviction             │
│  │  • search()     │   Cross-tier semantic search           │
│  └────────┬────────┘                                        │
│           │                                                 │
│  ┌────────┼─────────────────────────────────────────┐      │
│  │        ▼                                         │      │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │      │
│  │  │  SHORT   │  │  LONG    │  │  KNOWLEDGE   │   │      │
│  │  │  MEMORY  │  │  MEMORY  │  │  MEMORY      │   │      │
│  │  │          │  │          │  │              │   │      │
│  │  │ Session  │  │ Entity   │  │ Concepts     │   │      │
│  │  │ Context  │  │ Profiles │  │ Facts        │   │      │
│  │  │ Working  │  │ History  │  │ Procedures   │   │      │
│  │  │ State    │  │ Patterns │  │ References   │   │      │
│  │  │          │  │          │  │              │   │      │
│  │  │ TTL:     │  │ TTL:     │  │ TTL:         │   │      │
│  │  │ Session  │  │ Months   │  │ Permanent    │   │      │
│  │  └──────────┘  └──────────┘  └──────────────┘   │      │
│  └─────────────────────────────────────────────────┘      │
│                                                             │
│  ┌─────────────────────────────────────────────────┐        │
│  │              STORAGE BACKENDS (Adapters)         │        │
│  │  JSON Files  │  SQLite  │  Redis  │  ChromaDB   │        │
│  │  (default)   │          │         │  (vector)   │        │
│  └─────────────────────────────────────────────────┘        │
└─────────────────────────────────────────────────────────────┘
```

### 8.3 Memory Tier Definitions

**Short Memory (Session-scoped)**

| Property | Description |
|---|---|
| **Scope** | Current workflow run or conversation session |
| **Content** | Conversation turns, intermediate results, working hypotheses, current task state |
| **TTL** | Session duration; evicted on session close |
| **Query** | Chronological (last N turns) + keyword search |
| **Examples** | "What did the user just ask?", "What was the previous tool call result?", "What subtasks are pending?" |

```python
class ShortMemory(Protocol):
    async def append_turn(self, role: str, content: str, metadata: dict) -> None: ...
    async def get_recent_turns(self, n: int = 10) -> list[Turn]: ...
    async def get_working_state(self) -> dict: ...
    async def update_working_state(self, updates: dict) -> None: ...
    async def clear(self) -> None: ...
```

**Long Memory (Entity-scoped, persistent)**

| Property | Description |
|---|---|
| **Scope** | Cross-session, per-entity (user, project, agent) |
| **Content** | User profiles, preferences, learning history, error patterns, success patterns |
| **TTL** | Weeks to months; explicit eviction or decay |
| **Query** | Key-value (entity ID) + structured field queries |
| **Examples** | "What is the user's preferred coding style?", "What errors has this agent made in the past?" |

```python
class LongMemory(Protocol):
    async def get_entity(self, entity_id: str) -> Entity: ...
    async def update_entity(self, entity_id: str, updates: dict) -> None: ...
    async def record_experience(self, experience: Experience) -> None: ...
    async def recall_experiences(self, query: ExperienceQuery) -> list[Experience]: ...
    async def get_stats(self, entity_id: str) -> EntityStats: ...
    async def apply_decay(self, entity_id: str, decay_config: DecayConfig) -> None: ...
```

**Knowledge Memory (Global, reference)**

| Property | Description |
|---|---|
| **Scope** | Global, domain knowledge |
| **Content** | Concepts, facts, procedures, documentation, API references |
| **TTL** | Permanent; versioned updates |
| **Query** | Semantic search (vector), keyword search, graph traversal |
| **Examples** | "What is the syntax for Python async generators?", "How does OAuth 2.0 PKCE flow work?" |

```python
class KnowledgeMemory(Protocol):
    async def index(self, documents: list[Document]) -> None: ...
    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]: ...
    async def get_document(self, doc_id: str) -> Document: ...
    async def list_sources(self) -> list[Source]: ...
    async def refresh_source(self, source_id: str) -> None: ...
```

### 8.4 Unified Query Interface

The `MemoryManager` provides a unified query across all three tiers:

```python
# Cross-tier recall
results = await memory.recall(
    query="What do we know about user's Python skill level?",
    tiers=[MemoryTier.SHORT, MemoryTier.LONG, MemoryTier.KNOWLEDGE],
    top_k=10,
    merge_strategy="deduplicate_by_content"
)
# Returns: [
#   ShortMemory: "User just mentioned struggling with list comprehensions",
#   LongMemory: "User mastery_map: python_basics=0.7, python_advanced=0.3",
#   LongMemory: "User weak_points: async_await (count=5), decorators (count=3)",
#   KnowledgeMemory: "Python learning pathway: basics -> OOP -> functional -> async"
# ]
```

### 8.5 Memory as a Behavior Modifier

Memory is not a passive data store — it is an active participant in agent decision-making:

1. **Every agent declares its memory dependencies:**
   ```yaml
   agent:
     name: planner
     memory_requires:
       - short.conversation_context
       - long.user_profile
       - knowledge.course_catalog
     memory_optional:
       - long.error_patterns
   ```

2. **The runtime injects memory before agent invocation:**
   ```python
   context = await memory_manager.prefetch(agent.memory_requires)
   result = await agent.invoke(input, memory_context=context)
   ```

3. **Agent behavior changes based on memory content** — the same agent with different memory contexts produces different outputs. Memory updates from one agent affect subsequent agents. Exponential Moving Average (EMA) decay ensures stale data does not dominate decisions.

---

## 9. Adapter Layer

### 9.1 The Provider Binding Problem

Agent frameworks that bind to a specific LLM provider create a hard-to-escape dependency. The Universal Agent Framework is **provider-agnostic**. It defines abstract protocols; adapters implement them for specific providers.

### 9.2 LLM Provider Protocol

```python
class LLMProvider(Protocol):
    """Abstract interface for LLM providers."""

    @property
    def provider_name(self) -> str: ...
    @property
    def supported_models(self) -> list[str]: ...
    @property
    def capabilities(self) -> ProviderCapabilities: ...

    async def generate(
        self,
        *,
        model: str,
        messages: list[Message],
        tools: list[ToolDefinition] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stop_sequences: list[str] | None = None,
        metadata: dict | None = None,
    ) -> LLMResponse: ...

    async def generate_stream(
        self,
        *,
        model: str,
        messages: list[Message],
        **kwargs,
    ) -> AsyncIterator[LLMStreamChunk]: ...

    async def count_tokens(self, messages: list[Message], model: str) -> int: ...
    async def health_check(self) -> bool: ...

@dataclass
class ProviderCapabilities:
    supports_streaming: bool
    supports_tool_calls: bool
    supports_vision: bool
    supports_json_mode: bool
    max_context_window: int
    max_output_tokens: int

@dataclass
class LLMResponse:
    content: str
    model: str
    tool_calls: list[ToolCall] | None
    usage: TokenUsage
    finish_reason: str
    provider_raw: Any
```

### 9.3 Provider Routing

The framework supports multi-provider routing with fallback chains:

```yaml
# config/routing.yaml
routing:
  default_provider: anthropic
  default_model: claude-sonnet-4-6

  routes:
    # Route by agent type
    - agent_types: [planner, reviewer]
      provider: anthropic
      model: claude-opus-4-8

    - agent_types: [coder, formatter]
      provider: anthropic
      model: claude-sonnet-4-6

    - agent_types: [simple_classifier]
      provider: openai
      model: gpt-4o-mini

    # Route by task complexity (auto-detected)
    - complexity: [low]
      provider: local
      model: llama-3-8b

    - complexity: [medium, high]
      provider: anthropic

    # Fallback chain
    fallback_order:
      - anthropic
      - openai
      - deepseek
      - local_ollama
```

### 9.4 Adapter Implementations

```
Framework                   Adapter                      Provider
─────────                   ───────                      ────────
LLMProvider.generate()  →   OpenAIAdapter           →   OpenAI API
LLMProvider.generate()  →   AnthropicAdapter        →   Anthropic API
LLMProvider.generate()  →   DeepSeekAdapter         →   DeepSeek API
LLMProvider.generate()  →   OllamaAdapter           →   Ollama local API
```

### 9.5 Memory Backend Adapters

```python
class MemoryBackend(Protocol):
    """Abstract interface for memory storage."""
    async def store(self, key: str, value: Any, ttl: int | None = None) -> None: ...
    async def retrieve(self, key: str) -> Any | None: ...
    async def delete(self, key: str) -> None: ...
    async def search(self, query: str, top_k: int = 5) -> list[SearchResult]: ...
    async def list_keys(self, pattern: str) -> list[str]: ...
    async def clear(self) -> None: ...

# Implementations: JSONFileBackend (default), SQLiteBackend, RedisBackend, ChromaDBBackend
```

### 9.6 Event Bus Backend Adapters

For distributed deployments, the in-process Event Bus can be backed by external message queues:

```python
class EventBusBackend(Protocol):
    async def publish(self, channel: str, event: Event) -> None: ...
    async def subscribe(self, channel: str, handler: Callable) -> None: ...
    async def unsubscribe(self, channel: str, handler: Callable) -> None: ...
    async def request(self, channel: str, event: Event, timeout: float) -> Event: ...

# Implementations: InMemoryBackend (default), RedisPubSubBackend, NATSBackend, KafkaBackend
```

---

## 10. Integration Patterns

### 10.1 Universal Framework, Diverse Consumers

The Universal Agent Framework defines abstract interfaces, not concrete implementations. It integrates with downstream systems through three standard patterns:

```
┌─────────────────────────────────────────────────────────────────┐
│                 Universal Agent Framework                        │
│                 (Infrastructure Layer)                           │
│                                                                 │
│  Workflow Runtime • Event Bus • Policy Engine • Permission GW   │
│  Trace System • Memory Interface • Skill Registry • Adapters    │
└──────────┬──────────────────┬──────────────────┬────────────────┘
           │                  │                  │
           ▼                  ▼                  ▼
   ┌───────────────┐  ┌──────────────┐  ┌──────────────────┐
   │  Application  │  │   Runtime    │  │   Governance     │
   │  Adapter      │  │   Reference  │  │   Adapter        │
   │  Pattern      │  │   Pattern    │  │   Pattern        │
   └───────────────┘  └──────────────┘  └──────────────────┘
```

### 10.2 Pattern 1: Application Adapter

**Role:** An existing agent application that adopts the Framework as its runtime infrastructure.

**Characteristics:**
- Has domain-specific agents, business logic, and evaluation pipelines
- Currently implements its own workflow, memory, and communication patterns
- Wants to replace ad-hoc infrastructure with Framework primitives

**Integration approach:**
1. Register domain agents in the Agent Registry
2. Replace custom pipeline code with Workflow Runtime DAG definitions
3. Route agent communication through the Event Bus
4. Use Memory Interface instead of custom storage
5. Keep domain logic (agents, evaluation, knowledge bases) in the application

**What moves to Framework (as interfaces):** Workflow patterns, communication model, memory abstraction, LLM provider abstraction.

**What stays in Application:** Domain-specific agents, business rules, evaluation criteria, user interfaces, domain knowledge bases.

### 10.3 Pattern 2: Runtime Reference

**Role:** An existing runtime implementation that validates and can optionally back the Framework's abstractions.

**Characteristics:**
- Has a mature implementation of StateMachine, EventBus, Trace, Memory, Permission
- Serves as a validation target: "Does the Framework's abstract model cover all real-world runtime concerns?"
- May evolve into a first-party backend adapter

**Integration approach:**
1. Map existing runtime primitives to Framework interfaces
2. Implement optional backend adapters (e.g., `FrameworkCore(backend=ReferenceBackend())`)
3. Use the reference's test suite to validate Framework compliance
4. Keep specialized features (e.g., distributed runtime, decision explainability) scoped to the reference

**What moves to Framework (as patterns):** State machine design, event bus architecture, trace schema, permission model, recovery strategies.

**What stays in Reference:** Concrete implementation, specialized features (distributed mode, benchmarks, domain-specific lifecycle management).

### 10.4 Pattern 3: Governance Adapter

**Role:** A governance system that transitions from prompt-based rules to runtime-enforced policies.

**Characteristics:**
- Currently defines constraints, roles, workflows, and skills as Markdown/prompt documents
- Has a rich set of governance rules but no programmatic enforcement
- Wants to upgrade from "constitutional governance" to "runtime governance"

**Integration approach:**
1. Map governance rules to Policy Engine rule sets (YAML)
2. Register agent roles in the Framework's Agent Registry
3. Migrate workflow descriptions to Workflow Runtime DAG definitions
4. Convert skill registries to Skill Registry metadata
5. Replace free-text event logs with structured Trace events
6. Translate gate scripts to Project Adapter validation hooks

**What Framework provides:** Policy Engine enforcement, structured Trace, unified Skill Registry, Permission Gateway, Project Adapter validation.

**What stays in Governance:** Specific agent role definitions, project-level workflow templates, user preferences, environment-specific configurations.

### 10.5 Capability Attribution

```
                      Framework Core         Consumed via Adapter
                      (abstract interfaces)  (concrete config/instances)
──────────────────────────────────────────────────────────────────
Workflow Engine         ✅ DAG + scheduler     Workflow YAML definitions
State Machine           ✅ abstract states     Project-specific states
Event Bus               ✅ Pub/Sub             Project event topics
Policy Engine           ✅ rule evaluation     Project-specific rules
Permission Gateway      ✅ check/enforce       Role permission YAML
Trace System            ✅ collect/query       Trace schema extensions
Memory Interface        ✅ 3-tier API          Fact content + backends
Skill Registry          ✅ metadata/resolve    Skill implementations
LLM Provider Adapter    ✅ interface           API keys + model configs
Tool Adapter            ✅ schema/contract     Tool implementations
Project Adapter         ✅ template/validate   Project structure definitions
```

### 10.6 Reference Implementations

The Framework defines interfaces; the following reference implementations demonstrate each integration pattern (see Appendix D for project details):

| Pattern | Reference | Validates |
|:-----|:-----|:-----|
| Application Adapter | An existing multi-agent application with workflow pipelines and memory systems | DAG execution, Event Bus at scale, Memory tiering |
| Runtime Reference | A frozen, tested agent runtime library | State machine correctness, trace propagation, permission enforcement |
| Governance Adapter | A prompt-based governance repository | Policy migration from text to rules, preflight → project validation |

These references are optional. The Framework is designed to work with any downstream system that implements the Adapter interfaces defined in §9.

---

## 11. Migration Strategy

### 11.1 Guiding Principle: Incremental Extraction, Not Big-Bang Rewrite

The migration is designed as an **extraction**, not a rewrite. Each phase produces a working artifact. No phase breaks existing functionality. The Framework can be adopted incrementally by any downstream system — start with the Event Bus alone, or the Trace System alone. Every component is independently usable.

### 11.2 Phase Timeline

```
Phase 0         Phase 1         Phase 2         Phase 3         Phase 4         Phase 5
RFC & Design    Extract Core    Workflow        Policy +        Trace +         SDK + CLI
                Runtime         Engine          Permission      Memory
─────▶          ─────▶          ─────▶          ─────▶          ─────▶          ─────▶

2 weeks         4 weeks         6 weeks         6 weeks         6 weeks         8 weeks
(This doc)      (library)       (engine)        (security)      (observability) (ecosystem)
```

### 11.3 Phase Details

#### Phase 0: Architecture RFC (Current Phase)

**Output:** This document + community review

**Activities:**
- Publish RFC for community and stakeholder review
- Collect feedback on architecture decisions
- Resolve open design questions (see Appendix A)
- Prioritize Phase 1-5 based on feedback
- Define success criteria for each phase
- Establish framework repository structure

#### Phase 1: Extract Runtime Core

**Output:** `universal-agent-framework` Python package (0.1.0)

**Activities:**
- Extract and generalize the StateMachine from existing runtime patterns
- Implement `TaskLifecycle` enum and transition enforcement
- Implement `TaskContext` and `TaskHook` protocol
- Implement in-process `EventBus` with pub/sub and routing
- Extract `LLMProvider` protocol and implement OpenAI + Anthropic adapters

**Target test count:** ~200 (core abstractions only)

#### Phase 2: Workflow Engine

**Output:** Workflow DAG executor + CLI

**Activities:**
- Implement DAG parser (YAML → `WorkflowDefinition`)
- Implement DAG executor with topological sort and parallel execution
- Implement task lifecycle with all 10 states
- Implement retry strategies and human approval gates
- Implement `frameworkctl workflow run/submit/status/cancel`
- Validate: migrate A3's hardcoded pipeline to a framework YAML workflow

**Target test count:** ~150

#### Phase 3: Policy Engine + Permission Gateway

**Output:** Policy Engine + Permission Gateway + Audit Logger

**Activities:**
- Implement YAML-based permission config parser
- Implement RBAC and ABAC engines
- Implement Permission Gateway interceptor
- Implement audit trail (append-only decision log)
- Validate: migrate prompt-based agent role constraints to permission configs

**Target test count:** ~120

#### Phase 4: Trace + Memory

**Output:** Trace System + Memory Interface + Default Backends

**Activities:**
- Implement two-tier trace collector (in-memory buffer + persistent store)
- Implement trace query API and session replay
- Implement MemoryManager with Short/Long/Knowledge tiers
- Implement JSON, SQLite, and ChromaDB backends
- Validate: replace free-text event logs with structured traces

**Target test count:** ~150

#### Phase 5: SDK + CLI + Ecosystem

**Output:** Complete SDK, CLI, Skill Registry, Documentation, Examples

**Activities:**
- Implement `AgentSDK` and `frameworkctl` with all commands
- Implement Skill Registry with install/discover/version/dependency resolution
- Write comprehensive documentation and example projects
- Create migration guides for all three existing projects

**Target test count:** ~100 integration tests + example projects

### 11.4 Cumulative Test Count

| Phase | Unit Tests | Integration Tests | Cumulative |
|---|---|---|---|
| Phase 1 | 200 | 0 | 200 |
| Phase 2 | 150 | 0 | 350 |
| Phase 3 | 120 | 0 | 470 |
| Phase 4 | 150 | 0 | 620 |
| Phase 5 | 50 | 100 | 770 |

**Target total:** ~770 tests across all phases.

---

## 12. Design Principles

### 12.1 The Six Principles

Every architectural decision in the Universal Agent Framework is measured against these six principles.

---

### Principle 1: Runtime over Prompt

> **What the runtime can enforce, the prompt should not need to narrate.**

If a constraint can be expressed as a state machine transition, a permission rule, or a policy evaluation, it must be. Prompts are for the open-ended, creative, contextual reasoning that only an LLM can provide.

**Applied in:** Workflow Runtime (§3), Permission Gateway (§5), Trace System (§6).

---

### Principle 2: Explicit over Implicit

> **Contracts, schemas, and dependencies are declared, not inferred.**

An agent's inputs and outputs are defined by a schema. Its memory dependencies are declared. Its required permissions are listed. Nothing about an agent's behavior should be discovered at runtime by inspecting its prompt.

**Applied in:** Event Schema (§4), Skill Metadata (§7), Memory Dependencies (§8).

---

### Principle 3: Observable over Invisible

> **Every agent action produces a structured trace event. Debugging through prose is a last resort.**

The system's internal state must be externally visible. You should be able to answer "what happened?" without reading agent conversation logs.

**Applied in:** Trace System (§6), Event Bus (§4), Audit Trail (§5).

---

### Principle 4: Composable over Coupled

> **Every module works independently. Every module composes without modification.**

The framework is not a monolith. You can use the Trace System without the Workflow Runtime. You can use the Permission Gateway without the Event Bus.

**Applied in:** Layered architecture (§2), Adapter pattern (§9), Skill Registry (§7).

**Correct pattern:**
```python
# Each module is independently constructable
trace = TraceCollector(backend=JSONBackend("traces/"))
memory = MemoryManager(backends=[JSONBackend("memory/")])
workflow = WorkflowEngine(trace=trace, memory=memory)  # optional integration
```

---

### Principle 5: General over Project-Specific

> **The framework solves problems common to all agent systems, not problems specific to one application.**

A concept belongs in the framework only if at least two fundamentally different applications would need it.

**Decision heuristic:**
- "Would a chatbot, a code reviewer, and a research assistant all need this?" → Framework
- "Is this specific to how we teach programming concepts?" → Application

**Applied in:** Relationship with existing projects (§10), Memory Interface (§8), LLM Provider Protocol (§9).

---

### Principle 6: Testable over Assumed

> **Every abstraction must be verifiable in isolation. No framework capability ships without tests that prove it works independently of any LLM.**

The framework's core logic — state machines, permission evaluation, event routing, trace collection, memory storage — must be testable with deterministic unit tests. LLM calls are mocked.

**Applied in:** Migration Strategy test targets (§11), existing runtime test suites as reference, integration test patterns from downstream applications.

**Test design examples:**
```python
# Testing state machine without LLM
def test_task_cannot_transition_from_init_to_complete():
    task = Task(state=TaskState.INIT)
    with pytest.raises(InvalidTransitionError):
        task.transition_to(TaskState.COMPLETE)

# Testing permission evaluation with pure rule logic
def test_planner_denied_filesystem_write():
    policy = load_policy("agents/planner/permissions.yaml")
    result = policy.evaluate(
        agent_type="planner",
        action="filesystem.write",
        resource="/tmp/output.txt"
    )
    assert result.decision == "deny"
```

---

## Appendix A: Open Design Questions

These questions are flagged for community discussion during the RFC review period:

1. **Workflow DSL:** YAML vs. Python decorators (`@workflow.task()`)? YAML is language-agnostic; decorators feel more native to Python developers.

2. **Event schema versioning:** Semantic versioning (`task.completed/v1`) vs. backward-compatible-by-design (additive-only changes)?

3. **Skill sandboxing:** Same-process vs. subprocess/container isolation per skill? The metadata `resources.memory_mb` suggests isolation, but per-skill overhead may be prohibitive.

4. **Trace replay fidelity:** Observational replay (current proposal) vs. deterministic replay (record all LLM responses)?

5. **Permission inheritance model:** Hierarchical (OOP-style) vs. flat composable capabilities?

6. **Memory decay function:** EMA with alpha=0.5 (from A3) vs. configurable decay curves vs. explicit TTL?

7. **Distributed Event Bus:** Auto-detect and switch vs. explicit configuration choice?

8. **Skill registry federation:** Multiple remote registries with priority/fallback vs. single canonical registry?

---

## Appendix B: Glossary

| Term | Definition |
|---|---|
| **Agent** | A named, registered entity that performs work within a workflow. Has declared inputs, outputs, permissions, and memory dependencies. |
| **Workflow** | A Directed Acyclic Graph (DAG) of tasks, executed by the Workflow Runtime. |
| **Task** | A single node in a workflow DAG. Has a lifecycle (INIT → ... → COMPLETE) enforced by the runtime. |
| **Event** | A structured JSON message published to the Event Bus. Conforms to the universal event schema. |
| **Policy** | A YAML-defined set of rules evaluated by the Policy Engine to determine allow/deny decisions. |
| **Permission** | A specific action an agent is allowed or denied. Examples: `memory.read`, `filesystem.write`. |
| **Skill** | A reusable capability registered in the Skill Registry. Has metadata (name, version, capability, permission, dependencies). |
| **Memory** | Persistent state organized into three tiers: Short (session), Long (entity), Knowledge (reference). |
| **Trace** | A structured, queryable record of all events during a workflow execution. |
| **Adapter** | A concrete implementation of a framework protocol for a specific external system. |
| **Hook** | A non-intrusive observer that reacts to lifecycle events. Hooks can veto but not modify. |
| **Gate** | A validation checkpoint in a workflow or permission system. Returns allow/deny. |

---

## Appendix C: Design Decision Records

### ADR-001: Why Event Bus, Not Direct RPC?

- **Decision:** Agent communication uses Event Bus (Pub/Sub); no Agent-to-Agent RPC
- **Rationale:** Loose coupling (new agent doesn't affect existing), observability (all messages through Bus), extensibility (broadcast/filter/routing)
- **Cost:** Request/Response needs correlation_id (slightly more complex)
- **Rejected alternatives:** Direct RPC (tight coupling, unobservable), gRPC (too heavy for single-machine)

### ADR-002: Why Default-Deny for Permissions?

- **Decision:** No matching rule → Deny (default-deny model)
- **Rationale:** Security best practice (principle of least privilege)
- **Cost:** New agents require explicit permission config (increased setup cost)
- **Rejected alternatives:** Default-Allow (security risk), Default-Prompt (degenerates to Prompt Governance)

### ADR-003: Why Three-Tier Memory?

- **Decision:** Short/Long/Knowledge three-tier separation
- **Rationale:** Different memory types have different read/write frequency, TTL, and backend requirements
- **Specific:** Short → low latency (Dict/Redis); Long → structured query (SQL); Knowledge → semantic search (Vector)
- **Cost:** Three APIs, retrieval needs merge-sort
- **Rejected alternatives:** Single-tier memory (cannot simultaneously satisfy low latency + persistence + semantic search)

---

## Appendix D: References

> **Note:** All references in this appendix are **non-normative and optional**. The Framework architecture defined in §2-§12 does not depend on any referenced project, repository, or tool. These are provided as illustrative examples and conceptual foundations only.

### Reference Implementations (non-normative, illustrative examples)

These projects demonstrate the integration patterns described in §10. They are not required dependencies of the Framework.

| Pattern | Example | Key Concepts Demonstrated |
|:-----|:-----|:-----|
| Application Adapter | A multi-agent application with workflow pipelines, memory systems, and evaluation | DAG execution at scale, Event Bus in production, Memory tiering |
| Runtime Reference | A frozen, tested agent runtime library | State machine correctness, trace propagation, permission enforcement |
| Governance Adapter | A prompt-based governance repository | Policy migration (text→rules), preflight→project validation, skill unification |

### Conceptual Foundations

- **Harness Engineering (2026)**: Feedforward/Feedback framework, computational vs. inferential governance
- **Martin Fowler — Patterns of Enterprise Application Architecture**: Layered architecture, adapter pattern, event bus
- **OpenTelemetry**: Trace context propagation model (span_id, parent_span_id, trace_id)
- **AWS IAM Policy Language**: RBAC/ABAC policy structure and evaluation order
- **Semantic Versioning 2.0.0**: Version constraint syntax for skill dependencies
- **Kubernetes RBAC**: Permission model with explicit allow/deny and default-deny

---

*This RFC is a living document. Feedback, questions, and counter-proposals are welcome.*
*Please submit through the project's RFC process.*
