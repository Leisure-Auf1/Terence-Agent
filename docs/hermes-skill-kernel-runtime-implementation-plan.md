# Hermes Skill Kernel Runtime Implementation Plan

**Status:** Implementation Blueprint · Read-Only
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** B.6 — Skill Kernel Runtime Implementation
**Audience:** Hermes Core Team · Runtime Implementors

**Derived From:**
- Skill Kernel Runtime Specification v1.0 (B.5)
- Skill Kernel Resolver Architecture v1.0 (B.1)
- Skill Execution Lifecycle Architecture v1.0 (B.2)
- Skill Observability Architecture v1.0 (B.3)
- Skill Health Engine Architecture v1.0 (B.4)
- Registry v1.1 (149 entries, 18 fields)

**This document is:**
- The implementation blueprint for the Hermes Skill OS Kernel
- The bridge from architecture specification to executable code
- The authoritative module reference for runtime development

**This document does NOT:**
- Contain executable code
- Modify production Registry
- Modify SKILL.md files

---

## 1. Kernel Runtime Architecture

### 1.1 Module Tree

```
~/.hermes/kernel/
│
├── __init__.py                       # Kernel bootstrap + version
│
├── resolver/                         # B.1: Skill Resolution
│   ├── __init__.py
│   ├── capability_resolver.py        # Trigger matching + scoring
│   ├── namespace_resolver.py         # C.3 namespace filtering
│   ├── ownership_validator.py        # Cross-project + tier checks
│   └── dependency_validator.py       # Dependency graph resolution
│
├── lifecycle/                        # B.2: State Machine
│   ├── __init__.py
│   ├── state_machine.py              # 13-state engine
│   ├── transition_guard.py           # Valid/invalid transition enforcement
│   └── state_logger.py              # Transition audit log
│
├── runtime/                          # B.2: Execution
│   ├── __init__.py
│   ├── context_manager.py            # Memory allocation + mount
│   ├── executor.py                   # execute_skill() implementation
│   ├── permission_gate.py            # G1-G6 pre-execution checks
│   └── rollback_manager.py           # Context + state rollback
│
├── telemetry/                        # B.3: Observability
│   ├── __init__.py
│   ├── collector.py                  # Execution record writer
│   ├── event_store.py                # Append-only event log
│   └── metrics_aggregator.py         # Rolling metrics computation
│
├── health/                           # B.4: Health Engine
│   ├── __init__.py
│   ├── health_engine.py              # Score computation + state classification
│   ├── degradation_manager.py        # Auto-degradation actions
│   └── quarantine_manager.py         # Quarantine + evidence preservation
│
├── governance/                       # B.4: Governance Loop
│   ├── __init__.py
│   ├── proposal_engine.py            # P1-P8 auto-generation
│   └── proposal_store.py             # Proposal lifecycle management
│
├── audit/                            # All: Audit Trail
│   ├── __init__.py
│   ├── audit_logger.py               # Execution + state change logging
│   └── audit_query.py                # Audit record retrieval
│
└── config/
    └── kernel_config.yaml            # Runtime configuration
```

### 1.2 Module Dependency Graph

```
                    ┌─────────────┐
                    │   config    │
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ resolver │ │lifecycle │ │  audit   │
        └────┬─────┘ └────┬─────┘ └──────────┘
             │            │
             └──────┬─────┘
                    │
                    ▼
              ┌──────────┐
              │ runtime  │
              └────┬─────┘
                   │
         ┌─────────┼─────────┐
         │         │         │
         ▼         ▼         ▼
   ┌──────────┐┌──────────┐┌──────────┐
   │telemetry ││  health  ││governance│
   └──────────┘└────┬─────┘└────┬─────┘
                    │           │
                    └─────┬─────┘
                          │
                          ▼
                    ┌──────────┐
                    │  audit   │  ← All modules log to audit
                    └──────────┘
```

---

## 2. Implementation Boundary

### 2.1 Authorized Changes

```
✅ PERMITTED — Implementor may:

  1. Create new ~/.hermes/kernel/ directory with all modules
  2. Create new ~/.hermes/runtime/ directory for runtime state
  3. Write kernel bootstrap (__init__.py)
  4. Implement all 7 module groups as specified
  5. Write 50+ kernel tests
  6. Create kernel_config.yaml
```

### 2.2 Prohibited Changes

```
❌ FORBIDDEN — Implementor may NOT:

  1. Modify Governance Constitution v1.0 (FROZEN)
  2. Modify SKILL.md body content
  3. Bypass Registry v1.1 as source of truth
  4. Change C.3 namespace rules
  5. Auto-delete any skill
  6. Auto-modify skill lifecycle without governance approval
  7. Auto-change skill namespace, scope, or ownership
  8. Write directly to skill-registry.json (except `status` field)
```

---

## 3. Runtime Module Specifications

### 3.1 Resolver Module

```
Responsibility:
  Implement B.1 resolution pipeline: intent → skill selection

Input:
  intent: string, caller_scope: string, caller_tier: int

Output:
  SkillResolution {skill_id, namespace, confidence, alternatives}

Dependencies:
  Registry v1.1 (read-only), capability_resolver, namespace_resolver,
  ownership_validator, dependency_validator

Sub-modules:
  capability_resolver.py:
    - Load trigger map from Registry
    - Score candidates: exact=10, partial=7, domain=5, keyword=3
    - Return ranked list

  namespace_resolver.py:
    - Filter by namespace layer per caller scope
    - Escalate: project → adapter → core
    - Reject: core→project, adapter→project

  ownership_validator.py:
    - Verify caller tier vs skill ownership tier
    - Cross-project: require cross_project=true
    - Log PERMISSION_DENIED for rejections

  dependency_validator.py:
    - Resolve all declared skill + runtime dependencies
    - Detect circular dependencies
    - Detect forbidden dependencies (core→project, adapter→project)
    - Return resolution status

Failure handling:
  NO_MATCH → escalate namespace → if all exhausted → return error
  FORBIDDEN_PAIR → return error with alternatives
  PERMISSION_DENIED → return error, log denial

Test requirements:
  10 cases: trigger matching, namespace filtering, ownership validation,
           dependency resolution, forbidden pairs, escalation, tiebreaking
```

### 3.2 Lifecycle Engine

```
Responsibility:
  Implement B.2 13-state machine with transition enforcement

States:
  PROPOSED, REGISTERED, AVAILABLE, RESOLVED, LOADING, CONTEXT_READY,
  EXECUTING, SUCCESS, FAILED, DEGRADED, RECOVERY, DEPRECATED, ARCHIVED

Input:
  skill_id: string, target_state: string, context: SkillRuntimeContext

Output:
  TransitionResult {allowed: bool, new_state: string, reason: string}

Dependencies:
  transition_guard, state_logger, Registry v1.1 (for lifecycle field)

Sub-modules:
  state_machine.py:
    - Define state graph (nodes + edges)
    - current_state(skill_id) → string
    - transition(skill_id, target) → TransitionResult

  transition_guard.py:
    - Valid transitions map (25 allowed, 7 forbidden)
    - Duration limits per state
    - Gate checks before certain transitions

  state_logger.py:
    - Write state_change event on every transition
    - Include: from, to, trigger, timestamp, context

Failure handling:
  INVALID_TRANSITION → reject, log, return error
  DURATION_EXCEEDED → auto-transition (LOADING→FAILED, EXECUTING→TIMEOUT)
  GATE_FAILED → safe abort to AVAILABLE

Test requirements:
  10 cases: all valid transitions, all forbidden transitions,
           duration limits, gate checks, state logging
```

### 3.3 Context Manager

```
Responsibility:
  Manage skill context lifecycle: allocate, load, use, release

States:
  UNLOADED → LOADING → READY → IN_USE → RELEASED

Input:
  skill_id: string, mount: string ("routed"|"auto"|"manual")

Output:
  SkillContext {context_id, content_sha256, content_size, metadata}

Dependencies:
  Registry v1.1 (for path field), transition_guard

Operations:
  allocate(skill_id, mount) → context_id
    - Read SKILL.md from Registry.path
    - Verify file existence
    - Compute SHA-256
    - Parse frontmatter metadata
    - Transition: UNLOADED → LOADING → READY

  use(context_id) → None
    - Mark context as actively in use
    - Transition: READY → IN_USE

  release(context_id) → None
    - Free context memory
    - Transition: IN_USE → RELEASED → UNLOADED
    - Log context duration

Mount strategy handling:
  routed: load on resolver selection
  auto: load when task complexity > threshold
  manual: load on explicit skill_view()

Cleanup rules:
  Force-release on timeout (READY > 30s)
  Force-release on system shutdown
  Max 5 concurrent contexts

Failure handling:
  FILE_NOT_FOUND → FAILED (F1), mark skill DEGRADED
  SHA_MISMATCH → FAILED (F4), QUARANTINE skill
  OOM → FAILED (F1), release all, retry with reduced limit

Test requirements:
  8 cases: mount strategies, SHA verification, cleanup,
           concurrent limit, timeout release, error recovery
```

### 3.4 Executor

```
Responsibility:
  Execute resolved skill with full gate + monitoring

Input:
  execution_id: string, context_id: string, skill_id: string,
  input: any, timeout_ms: int

Output:
  ExecutionResult {status, output, duration_ms, error}

Dependencies:
  permission_gate, context_manager, rollback_manager,
  telemetry/collector, health/health_engine

Operations:
  execute(request) → ExecutionResult
    1. Verify CONTEXT_READY state
    2. Run permission_gate.check() → all 6 must pass
    3. Transition: CONTEXT_READY → EXECUTING
    4. Execute skill logic with timeout monitor
    5. Capture result
    6. Transition: EXECUTING → SUCCESS | FAILED | DEGRADED
    7. Release context
    8. Record telemetry
    9. Update health

  retry(execution_id, attempt) → ExecutionResult
    - Up to 3 retries for F1, F2, F5, F6
    - Exponential backoff: 1s, 2s, 4s
    - 2× timeout on retry for F5

  fallback(skill_id) → ExecutionResult
    - Query next-best candidate from resolver
    - Execute fallback skill
    - Log fallback event

Failure handling:
  F5 timeout: retry 3× → fallback → report
  F6 external: retry 3× → fallback adapter → report
  Gate failure: safe abort to AVAILABLE

Test requirements:
  6 cases: successful execution, timeout, retry, fallback,
           gate rejection, context release
```

### 3.5 Telemetry Collector

```
Responsibility:
  Record execution telemetry, emit events, aggregate metrics

Events:
  SKILL_RESOLVED, EXECUTION_STARTED, EXECUTION_COMPLETED,
  EXECUTION_FAILED

Input:
  ExecutionRecord (from B.5 §3.2)

Output:
  telemetry_id: string, stored: bool

Dependencies:
  event_store, metrics_aggregator, ~/.hermes/runtime/telemetry/

Sub-modules:
  collector.py:
    - Validate ExecutionRecord schema
    - Write to execution-history/{YYYY-MM}/{execution_id}.json
    - Emit event to event_store
    - Trigger metrics update

  event_store.py:
    - Append-only event log
    - Events indexed by: skill_id, namespace, timestamp
    - Query interface: by_skill(), by_namespace(), by_timerange()

  metrics_aggregator.py:
    - Compute rolling metrics per skill
    - Update: success_rate, failure_rate, p95_latency, timeout_rate
    - Store in telemetry/skill-metrics/{skill_id}.json
    - Update namespace + system aggregates

Failure handling:
  Write failure → log warning; execution result unaffected
  Aggregation failure → skip, retry on next cycle

Test requirements:
  4 cases: record storage, event emission, metrics update, write failure
```

### 3.6 Health Engine

```
Responsibility:
  Evaluate skill health, trigger degradation/quarantine, manage recovery

Input:
  skill_id: string, force: bool

Output:
  HealthState {score, state, factors, recommendation}

Dependencies:
  telemetry/metrics_aggregator, degradation_manager, quarantine_manager,
  governance/proposal_engine

Sub-modules:
  health_engine.py:
    - Gather 5 factor inputs from metrics
    - Compute score (0-100) per B.4 §1.2
    - Classify state: HEALTHY(90+) → WARNING(75-89) → DEGRADED(50-74) → FAILED(25-49) → QUARANTINED(0-24)
    - Write health record to ~/.hermes/runtime/health/
    - If state changed: emit HEALTH_CHANGED event

  degradation_manager.py:
    - On DEGRADED: reduce priority, create alert, restrict usage, create maintenance proposal
    - Grace period: 2 hours to self-recover
    - Monitor for recovery or escalation

  quarantine_manager.py:
    - On QUARANTINED: block all dispatch, preserve evidence, CRITICAL alert
    - Snapshot registry entry + SKILL.md
    - Notify governance
    - No automatic exit — requires governance review

Recovery paths:
  Retry → fallback → owner intervention → governance review

Test requirements:
  8 cases: score computation, state transitions, degradation actions,
           quarantine actions, recovery, false positive prevention
```

### 3.7 Governance Engine

```
Responsibility:
  Auto-generate governance proposals from health + usage data

Proposals: P1-P8 (B.4 §7)

Input:
  skill_id: string, trigger_data: object

Output:
  Proposal {proposal_id, type, priority, status}

Dependencies:
  proposal_store, health/health_engine, telemetry/metrics_aggregator

Sub-modules:
  proposal_engine.py:
    - Check P1-P8 trigger thresholds
    - Gather supporting evidence
    - Generate proposal with priority
    - Store as PENDING

  proposal_store.py:
    - Manage proposal lifecycle: PROPOSED → REVIEW → APPROVED/REJECTED/DEFERRED
    - Store in ~/.hermes/runtime/governance-proposals/
    - Query interface: pending(), by_skill(), by_type()

Proposal triggers:
  P1 MAINTENANCE: success_rate < 80% for 7 days
  P2 USAGE_REVIEW: 0 executions in 30 days
  P3 MERGE: 3+ skills same capability, all low usage
  P4 UPGRADE: version > 2 MAJOR behind latest
  P5 DEPRECATION: FAILED > 72h, no recovery
  P6 ARCHIVE: DEPRECATED > 14 days, 0 executions
  P7 DEPENDENCY_AUDIT: dependency in WARNING > 7 days
  P8 CROSS_PROJECT_REVIEW: cross-project dep with high failure

Test requirements:
  6 cases: trigger thresholds, evidence gathering, lifecycle,
           approval flow, rejection, deferral
```

---

## 4. Runtime Storage Implementation

### 4.1 Directory Layout

```
~/.hermes/runtime/
│
├── state/
│   ├── runtime-state.json           # Active executions, loaded contexts, uptime
│   └── kernel-config.yaml           # Runtime configuration
│
├── executions/
│   └── YYYY-MM/
│       └── {execution_id}.json      # Full ExecutionRecord per execution
│
├── telemetry/
│   ├── skill-metrics/
│   │   └── {skill_id}.json          # Rolling metrics per skill
│   ├── namespace-metrics/
│   │   └── {namespace}.json         # Aggregated namespace metrics
│   ├── system-metrics.json          # System-wide aggregates
│   └── event-log/
│       └── YYYY-MM-DD.jsonl         # Append-only event stream
│
├── health/
│   ├── current/
│   │   └── {skill_id}.json          # Current health state
│   ├── history/
│   │   └── {skill_id}/
│   │       └── YYYY-MM-DD.json      # Daily health snapshots
│   └── quarantine/
│       └── {skill_id}/              # Evidence preserved on quarantine
│           ├── registry-snapshot.json
│           └── skill-content.bak
│
├── proposals/
│   ├── pending/
│   │   └── {proposal_id}.json
│   ├── approved/
│   │   └── {proposal_id}.json
│   ├── rejected/
│   │   └── {proposal_id}.json
│   └── index.json                   # All proposals index
│
└── audit/
    ├── state-changes/
    │   └── YYYY-MM-DD.jsonl         # State transition log
    ├── permission-denials/
    │   └── YYYY-MM-DD.jsonl         # G1/G2/G3 rejection log
    └── health-events/
        └── YYYY-MM-DD.jsonl         # Health state change log
```

### 4.2 Storage Rules

```
Rule S1: Registry is STATIC truth
  → Kernel reads Registry, never modifies (except `status` field)

Rule S2: Runtime state is DYNAMIC
  → Can be rebuilt from Registry + execution log
  → Ephemeral by design

Rule S3: Telemetry is APPEND-ONLY
  → Execution records immutable once written
  → Metrics are derived, cacheable, recomputable

Rule S4: Audit is IMMUTABLE
  → State changes, permission denials, health events — never modified
  → Write-once, read-many pattern

Rule S5: Proposals are PENDING until human approval
  → Kernel auto-generates but never auto-executes
  → Governance Reviewer is the sole approver
```

---

## 5. Testing Plan — 55+ Kernel Test Cases

### 5.1 Resolver Tests (10)

| # | Test | Category |
|:--|:-----|:-----|
| RT-01 | Exact trigger match returns highest confidence | Trigger |
| RT-02 | Partial trigger match scores correctly | Trigger |
| RT-03 | Capability domain match | Capability |
| RT-04 | No match escalates namespace | Escalation |
| RT-05 | All namespaces exhausted returns NO_MATCH | Exhaustion |
| RT-06 | Forbidden pair rejects correctly | Security |
| RT-07 | Multiple candidates — tiebreak by version | Ranking |
| RT-08 | Deprecated skill penalty applied | Lifecycle |
| RT-09 | Namespace filter: system→core | Namespace |
| RT-10 | Namespace filter: project→project.<id> | Namespace |

### 5.2 Lifecycle Tests (10)

| # | Test | Category |
|:--|:-----|:-----|
| RT-11 | Valid: AVAILABLE → RESOLVED → LOADING | Positive |
| RT-12 | Valid: EXECUTING → SUCCESS → AVAILABLE | Positive |
| RT-13 | Invalid: FAILED → EXECUTING | Negative |
| RT-14 | Invalid: ARCHIVED → AVAILABLE | Negative |
| RT-15 | Timeout: LOADING > 5s → FAILED | Duration |
| RT-16 | Timeout: EXECUTING > 300s → FAILED | Duration |
| RT-17 | Safe abort: RESOLVED → AVAILABLE | Abort |
| RT-18 | State transition logged to audit | Audit |
| RT-19 | Gate check before EXECUTING | Gate |
| RT-20 | Degradation: 3 failures → DEGRADED | Health link |

### 5.3 Context Tests (8)

| # | Test | Category |
|:--|:-----|:-----|
| RT-21 | Routed mount: load on resolver selection | Mount |
| RT-22 | SHA-256 verification on load | Integrity |
| RT-23 | SHA mismatch → F4 corruption → QUARANTINE | Security |
| RT-24 | Context release after execution | Cleanup |
| RT-25 | Max 5 concurrent contexts enforced | Limit |
| RT-26 | Stale context timeout (READY > 30s) | Timeout |
| RT-27 | File not found → FAILED (F1) | Error |
| RT-28 | Context released on system shutdown | Cleanup |

### 5.4 Permission Tests (6)

| # | Test | Category |
|:--|:-----|:-----|
| RT-29 | Core→Project rejected at G3 | Security |
| RT-30 | Adapter→Project rejected at G3 | Security |
| RT-31 | Cross-project without declaration rejected at G2 | Security |
| RT-32 | Cross-project with cross_project=true passed at G2 | Security |
| RT-33 | Archived skill rejected at G5 | Lifecycle |
| RT-34 | Quarantined skill rejected at G6 | Security |

### 5.5 Failure Recovery Tests (8)

| # | Test | Category |
|:--|:-----|:-----|
| RT-35 | F1 context failure → retry 1× → FAILED | Recovery |
| RT-36 | F2 dependency failure → G4 reject → DEGRADED | Recovery |
| RT-37 | F3 permission failure → safe abort | Recovery |
| RT-38 | F4 corruption → QUARANTINE + evidence preserved | Recovery |
| RT-39 | F5 timeout → retry 3× → fallback | Recovery |
| RT-40 | F6 external failure → retry 3× → fallback adapter | Recovery |
| RT-41 | Recovery success → WARNING | Recovery |
| RT-42 | Recovery exhausted → FAILED | Recovery |

### 5.6 Telemetry Tests (4)

| # | Test | Category |
|:--|:-----|:-----|
| RT-43 | Execution record written on SUCCESS | Write |
| RT-44 | Execution record written on FAILED with error | Write |
| RT-45 | Metrics aggregator updated after 100 executions | Aggregation |
| RT-46 | Telemetry write failure doesn't affect execution | Resilience |

### 5.7 Health Tests (8)

| # | Test | Category |
|:--|:-----|:-----|
| RT-47 | Score 95 → HEALTHY | Scoring |
| RT-48 | Score 72 after 3 failures → DEGRADED | Degradation |
| RT-49 | Score 30 after exhaustion → FAILED | Degradation |
| RT-50 | F4 corruption → QUARANTINED | Quarantine |
| RT-51 | HEALTH_CHANGED event emitted on transition | Event |
| RT-52 | Health recovery: score 85 → WARNING | Recovery |
| RT-53 | False positive: 1 failure doesn't degrade | Accuracy |
| RT-54 | Health score factors computed correctly | Accuracy |

### 5.8 Governance Tests (6)

| # | Test | Category |
|:--|:-----|:-----|
| RT-55 | P1 maintenance proposal triggered (success < 80%) | Trigger |
| RT-56 | P2 usage review triggered (0 exec/30d) | Trigger |
| RT-57 | Proposal lifecycle: PROPOSED → APPROVED | Lifecycle |
| RT-58 | Proposal lifecycle: PROPOSED → REJECTED | Lifecycle |
| RT-59 | Proposal never auto-executes | Safety |
| RT-60 | Proposal priority correctly assigned | Priority |

---

## 6. Migration Strategy

### 6.1 Phased Implementation

```
Phase B.6.0 — Kernel Skeleton
  Duration:  1 session
  Deliverables:
    - ~/.hermes/kernel/ directory created
    - __init__.py bootstrap
    - ~/.hermes/runtime/ directory created
    - kernel_config.yaml
    - 0 production impact
  Gate: Directory structure valid, config parseable

Phase B.6.1 — Resolver Runtime
  Duration:  2 sessions
  Deliverables:
    - resolver/ module complete
    - capability_resolver, namespace_resolver, ownership_validator, dependency_validator
    - 10 resolver tests passing
    - Read-only from Registry
  Gate: resolve_skill() returns correct skill for known intents

Phase B.6.2 — Lifecycle + Context Runtime
  Duration:  2 sessions
  Deliverables:
    - lifecycle/ module complete (state_machine, transition_guard)
    - runtime/ module complete (context_manager, executor, permission_gate, rollback_manager)
    - 18 lifecycle + context tests passing
    - Context allocation/release verified
  Gate: Full execution pipeline works end-to-end

Phase B.6.3 — Health + Telemetry
  Duration:  2 sessions
  Deliverables:
    - telemetry/ module complete (collector, event_store, metrics_aggregator)
    - health/ module complete (health_engine, degradation_manager, quarantine_manager)
    - 12 health + telemetry tests passing
    - Metrics aggregation verified
  Gate: Health scoring accurate; degradation/quarantine trigger correctly

Phase B.6.4 — Governance Loop
  Duration:  1 session
  Deliverables:
    - governance/ module complete (proposal_engine, proposal_store)
    - 6 governance tests passing
    - P1-P8 triggers verified
  Gate: Proposals auto-generated but never auto-executed

Phase B.6.5 — Production Validation
  Duration:  1 session
  Deliverables:
    - All 60 tests passing
    - Production safety gate (7 checks)
    - Audit trail verified
    - Rollback tested
  Gate: All gates green → Kernel ready
```

### 6.2 Per-Phase Safety

```
ALL PHASES:
  ✅ Registry unchanged (read-only except status field)
  ✅ SKILL.md unchanged
  ✅ Governance Constitution unchanged
  ✅ C.3 namespace rules unchanged

PER-PHASE:
  → Gate must pass before next phase
  → Rollback: delete ~/.hermes/kernel/ and ~/.hermes/runtime/
  → No production impact until B.6.5 validation complete
```

---

## 7. Production Safety Gate

### 7.1 Seven-Gate Validation (After B.6.5)

| Gate | Check | Method |
|:----:|:-----|:-----|
| **G1** | Kernel starts | `python3 -c "from kernel import KernelRuntime; k = KernelRuntime(); assert k.healthy"` |
| **G2** | Resolver works | `resolve_skill("navigate to webpage", "adapter", 1)` → returns browser-automation |
| **G3** | Existing skills unaffected | SHA-256 all 148 SKILL.md match pre-kernel baseline |
| **G4** | Registry unchanged | diff registry.json pre/post kernel → 0 differences (except status field) |
| **G5** | Rollback works | Delete ~/.hermes/kernel/ → Hermes operates as before |
| **G6** | Runtime audit works | All state transitions logged; audit trail queryable |
| **G7** | Governance boundaries enforced | Core→Project dispatch rejected; Adapter→Project dispatch rejected |

### 7.2 Gate Decision

```
All 7 gates must PASS:
  [ ] G1 Kernel starts
  [ ] G2 Resolver works
  [ ] G3 Skills unaffected
  [ ] G4 Registry unchanged
  [ ] G5 Rollback works
  [ ] G6 Audit works
  [ ] G7 Boundaries enforced

  ALL PASS → 🟢 Kernel production ready
  ANY FAIL → 🔴 Return to implementation phase
```

---

## 8. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   SKILL KERNEL RUNTIME IMPLEMENTATION PLAN                    ║
║                                                              ║
║   Architecture:                                                ║
║     Module tree:    8 directories, 24+ files                  ║
║     Storage:        6 directories under ~/.hermes/runtime/    ║
║                                                              ║
║   Implementation:                                              ║
║     Phases:         6 (B.6.0 → B.6.5)                         ║
║     Tests:          60 kernel test cases                       ║
║     Modules:        7 runtime modules specified                ║
║                                                              ║
║   Safety:                                                      ║
║     ✅ Registry read-only during implementation                ║
║     ✅ SKILL.md files untouched                                ║
║     ✅ Governance Constitution unchanged                       ║
║     ✅ 7-gate production validation                            ║
║     ✅ Kernel deletable for rollback                           ║
║                                                              ║
║   🟢 GREEN — Implementation Ready                             ║
║                                                              ║
║   Hermes Skill OS Kernel is ready for implementation.         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ |
| 8 sections complete | ✅ |
| Module tree (8 dirs, 24+ files) | ✅ |
| 7 module specifications | ✅ |
| Storage layout (6 dirs) | ✅ |
| 55+ test cases | ✅ |
| 6-phase migration | ✅ |
| 7-gate safety check | ✅ |
| 0 executable code | ✅ |

---

> **Phase:** B.6 — Skill Kernel Runtime Implementation Plan
> **Status:** ✅ IMPLEMENTATION PLAN COMPLETE
> **Decision:** 🟢 GREEN — Implementation Ready
> **Next:** Phase B.6.0 — Kernel Skeleton (awaiting authorization)
