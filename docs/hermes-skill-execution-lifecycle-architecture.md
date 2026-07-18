# Hermes Skill Execution Lifecycle Architecture

**Status:** Architecture Design Document · Read-Only
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** B.2 — Skill Execution Lifecycle Architecture
**Audience:** Hermes Core Team · Framework Contributors

**Governance Authority:**
- Hermes Governance Constitution v1.0 (FROZEN)
- Skill Kernel Resolver Architecture v1.0 (B.1)
- Registry v1.1 (149 entries, 18 fields)
- C.3 Namespace Model

**This document defines:**
- Complete 13-state execution lifecycle with transition rules
- Context allocation, loading, and cleanup model
- Execution permission gate matrix
- Failure classification, retry, and recovery system
- Skill health states and audit trail schema
- Design only — no implementation code

---

## 1. Execution Lifecycle Model

### 1.1 Complete 13-State Lifecycle

```
                    ┌──────────────┐
                    │  PROPOSED    │  ← Skill idea submitted for review
                    └──────┬───────┘
                           │ Governance review passes
                           ▼
                    ┌──────────────┐
                    │ REGISTERED   │  ← In Registry, not yet active
                    └──────┬───────┘
                           │ System activation
                           ▼
                    ┌──────────────┐
              ┌─────│  AVAILABLE   │  ← Ready for dispatch, idle
              │     └──────┬───────┘
              │            │ Resolver selects (B.1 pipeline)
              │            ▼
              │     ┌──────────────┐
              │     │  RESOLVED    │  ← Selected by resolver, pre-load
              │     └──────┬───────┘
              │            │ Begin context load
              │            ▼
              │     ┌──────────────┐
              │     │  LOADING     │  ← SKILL.md being read, SHA verified
              │     └──────┬───────┘
              │            │ Load complete + SHA-256 OK
              │            ▼
              │     ┌──────────────┐
              │     │CONTEXT_READY │  ← Content in session, ready to run
              │     └──────┬───────┘
              │            │ Execution begins
              │            ▼
              │     ┌──────────────┐
              │     │  EXECUTING   │  ← Skill actively running
              │     └──────┬───────┘
              │            │
              │     ┌──────┼──────┬──────────┐
              │     │      │      │          │
              │     ▼      ▼      ▼          ▼
              │  ┌────┐┌──────┐┌───────┐┌─────────┐
              │  │ OK ││PARTIAL││ERROR  ││TIMEOUT  │
              │  └──┬─┘└──┬───┘└──┬────┘└────┬────┘
              │     │     │       │          │
              │     ▼     ▼       ▼          ▼
              │  ┌──────┐┌──────────┐┌──────────┐
              │  │SUCCESS││ DEGRADED ││  FAILED  │
              │  └──┬───┘└────┬─────┘└────┬─────┘
              │     │         │           │
              │     │         │           ▼
              │     │         │    ┌──────────────┐
              │     │         │    │   RECOVERY   │  ← Retry or fallback
              │     │         │    └──────┬───────┘
              │     │         │           │
              │     │         │     ┌─────┼─────┐
              │     │         │     │     │     │
              │     │         │     ▼     ▼     ▼
              │     │         │  ┌────┐┌────┐┌──────┐
              │     │         │  │ OK ││FAIL││FALL- │
              │     │         │  │    ││    ││BACK  │
              │     │         │  └──┬─┘└──┬─┘└──┬───┘
              │     │         │     │     │     │
              │     ◄─────────┼─────┘     │     │
              │               │           │     │
              │     (return   │     (quarantine) │
              │      to       │                  │
              │      AVAILABLE│                  │
              │               │                  │
              │               ▼                  │
              │        ┌──────────────┐          │
              │        │  QUARANTINED │          │
              │        └──────────────┘          │
              │                                  │
              ◄──────────────────────────────────┘
              │
              │ (all paths return to AVAILABLE after execution)
              │
              │ Deprecation gate
              ▼
       ┌──────────────┐
       │  DEPRECATED  │  ← Grace period (14 days)
       └──────┬───────┘
              │ Grace period elapsed
              ▼
       ┌──────────────┐
       │  ARCHIVED    │  ← Terminal
       └──────────────┘
```

### 1.2 State Definitions

| State | Meaning | Entry Condition | Exit Condition | Owner |
|:-----|:-----|:-----|:-----|:-----|
| **PROPOSED** | Skill submitted for review | Author submits proposal | Review accepted or rejected | Author |
| **REGISTERED** | In Registry, pending activation | Governance review passes | System activation | Governance |
| **AVAILABLE** | Ready for dispatch, idle | Activation complete | Resolver selects skill | System |
| **RESOLVED** | Selected by resolver | Resolver pipeline completes | Context load begins | Resolver |
| **LOADING** | SKILL.md being read | Context load initiated | Load complete or error | System |
| **CONTEXT_READY** | Content in session | Load complete + SHA OK | Execution begins | System |
| **EXECUTING** | Actively running | Execution triggered | Completion or failure | Executor |
| **SUCCESS** | Completed successfully | All steps completed OK | Return to AVAILABLE | Executor |
| **FAILED** | Terminated with error | Unrecoverable error | Enter RECOVERY or DEGRADED | Executor |
| **DEGRADED** | Running with reduced capability | Partial failure or warning | Return to AVAILABLE or QUARANTINE | System |
| **RECOVERY** | Attempting retry or fallback | FAILED or DEGRADED state | Recovery OK, FAIL, or FALLBACK | System |
| **DEPRECATED** | Grace period before archival | Deprecation gate passed | Grace period elapsed | Governance |
| **ARCHIVED** | Terminal — no longer usable | Grace period elapsed | None (terminal) | Governance |

### 1.3 Allowed Transitions

| From → To | Allowed? | Condition |
|:-----|:----:|:-----|
| PROPOSED → REGISTERED | ✅ | Review passes |
| PROPOSED → (terminal) | ✅ | Rejected |
| REGISTERED → AVAILABLE | ✅ | Auto-activation |
| AVAILABLE → RESOLVED | ✅ | Resolver selects |
| AVAILABLE → DEPRECATED | ✅ | Deprecation gate |
| RESOLVED → LOADING | ✅ | Load initiated |
| RESOLVED → AVAILABLE | ✅ | Pre-load check fails (safe abort) |
| LOADING → CONTEXT_READY | ✅ | Load OK + SHA verified |
| LOADING → DEGRADED | ✅ | Load OK with warnings |
| LOADING → FAILED | ✅ | File missing or corrupt |
| CONTEXT_READY → EXECUTING | ✅ | Execution starts |
| CONTEXT_READY → AVAILABLE | ✅ | Execution cancelled (safe abort) |
| EXECUTING → SUCCESS | ✅ | All steps complete |
| EXECUTING → DEGRADED | ✅ | Partial completion |
| EXECUTING → FAILED | ✅ | Error or timeout |
| SUCCESS → AVAILABLE | ✅ | Auto-return |
| FAILED → RECOVERY | ✅ | Retry possible |
| FAILED → DEGRADED | ✅ | No retry; accept degradation |
| DEGRADED → RECOVERY | ✅ | Attempt fix |
| DEGRADED → AVAILABLE | ✅ | Accept degraded; return |
| DEGRADED → QUARANTINED | ✅ | Repeated failures |
| RECOVERY → AVAILABLE | ✅ | Recovery succeeded |
| RECOVERY → FAILED | ✅ | Recovery exhausted |
| RECOVERY → DEGRADED | ✅ | Fallback skill activated |
| DEPRECATED → ARCHIVED | ✅ | Grace period elapsed |
| QUARANTINED → AVAILABLE | ✅ | Manual intervention + re-validation |

### 1.4 Forbidden Transitions

| From → To | Reason |
|:-----|:-----|
| FAILED → EXECUTING | ❌ Must go through RECOVERY or AVAILABLE first |
| ARCHIVED → AVAILABLE | ❌ Terminal state; must re-register as new PROPOSED |
| ARCHIVED → any | ❌ Terminal — no exits |
| QUARANTINED → EXECUTING | ❌ Must go through AVAILABLE + re-validation |
| PROPOSED → EXECUTING | ❌ Bypasses registration and activation |
| DEGRADED → SUCCESS | ❌ Degraded execution cannot retroactively succeed |
| RECOVERY → SUCCESS | ❌ Recovery returns to AVAILABLE, not directly to SUCCESS |

---

## 2. Execution State Machine

### 2.1 Transition Enforcement Rules

```
Rule T1: Every transition must pass through defined gates
  → No direct jumps between non-adjacent states

Rule T2: Pre-execution gate must pass before EXECUTING
  → Permission check, dependency check, namespace check (§4)

Rule T3: Post-execution audit must record before return to AVAILABLE
  → Execution record written to audit trail (§8)

Rule T4: Degradation threshold triggers quarantine
  → 3 DEGRADED events in 24h → QUARANTINED

Rule T5: Recovery attempts are bounded
  → Max 3 retries; then fallback or FAILED

Rule T6: Context cleanup on state exit
  → LOADING→FAILED: release partial context
  → EXECUTING→FAILED: release context after error logged
  → SUCCESS→AVAILABLE: release context cleanly
```

### 2.2 State Duration Limits

| State | Max Duration | Exceeded → Action |
|:-----|:-----|:-----|
| LOADING | 5 seconds | FAILED (file access timeout) |
| CONTEXT_READY | 30 seconds | AVAILABLE (stale context; reload) |
| EXECUTING | 300 seconds (5 min) | TIMEOUT → FAILED |
| RECOVERY | 60 seconds | FAILED (recovery timeout) |

---

## 3. Context Lifecycle

### 3.1 Context Allocation Model

```
┌─────────────────────────────────────────────────────────────┐
│                    CONTEXT LIFECYCLE                         │
│                                                             │
│  UNLOADED                                                    │
│  ────────                                                    │
│  Skill not in session. 0 memory allocation.                  │
│       │                                                     │
│       │ Mount trigger fires (routed/auto/manual)             │
│       ▼                                                     │
│  ┌──────────────┐                                           │
│  │  LOADING     │  ← Reading SKILL.md, allocating context   │
│  └──────┬───────┘                                           │
│         │ Load complete, SHA-256 verified                    │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │   READY      │  ← Content in session, awaiting execution │
│  └──────┬───────┘                                           │
│         │ Execution begins                                   │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │  IN_USE      │  ← Skill actively executing               │
│  └──────┬───────┘                                           │
│         │ Execution complete (SUCCESS/FAILED/DEGRADED)       │
│         ▼                                                   │
│  ┌──────────────┐                                           │
│  │  RELEASED    │  ← Context freed, memory reclaimed        │
│  └──────────────┘                                           │
│         │                                                   │
│         ▼                                                   │
│  UNLOADED  (ready for next dispatch)                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Context Ownership

| Context State | Owner | Responsibility |
|:-----|:-----|:-----|
| UNLOADED | System | None |
| LOADING | Loader | Read file, allocate memory, verify SHA-256 |
| READY | Resolver | Verify pre-execution gates, prepare arguments |
| IN_USE | Executor | Execute skill, monitor health, handle errors |
| RELEASED | System | Free memory, log execution, update metrics |

### 3.3 Cleanup Rules

```
Rule C1: Context MUST be released after every execution
  → No lingering context after SUCCESS, FAILED, or DEGRADED

Rule C2: Failed load MUST release partial context
  → LOADING→FAILED: free any allocated memory before transition

Rule C3: Stale context detection
  → READY > 30s without execution → auto-release, mark STALE

Rule C4: Emergency cleanup on system shutdown
  → All IN_USE contexts → force-release with WARNING log

Rule C5: Memory budget enforcement
  → Max 5 concurrent contexts (configurable)
  → Exceeded → queue or reject new dispatches
```

### 3.4 Context Failure Recovery

| Failure | Detection | Response |
|:-----|:-----|:-----|
| File not found | LOADING: read error | → FAILED; mark skill DEGRADED; log to error-registry |
| SHA-256 mismatch | LOADING: hash check | → FAILED; restore from backup; log CORRUPTION |
| Memory allocation failure | LOADING: OOM | → FAILED; reduce concurrent limit; retry |
| Stale context | READY: timer | → RELEASED; re-dispatch if needed |

---

## 4. Execution Permission Check

### 4.1 Pre-Execution Gate Matrix

Before EXECUTING, all 6 gates must pass:

| Gate | Check | Failure Response |
|:-----|:-----|:-----|
| **G1 — Caller Scope** | Caller's namespace layer compatible with skill scope | REJECT; log PERMISSION_DENIED |
| **G2 — Skill Ownership** | Caller authorized to execute this skill (tier check) | REJECT if cross-project without declaration |
| **G3 — Namespace Boundary** | Skill namespace direction valid | REJECT if Core→Project or Adapter→Project |
| **G4 — Dependency Availability** | All declared dependencies resolvable | DEGRADED if runtime dep missing; FAILED if skill dep missing |
| **G5 — Lifecycle Status** | Skill lifecycle is `active` | WARN if `deprecated`; REJECT if `archived` |
| **G6 — Security Policy** | No forbidden pair active; no quarantine state | REJECT; suggest alternatives |

### 4.2 Gate Execution Order

```
RESOLVED state
    │
    ▼
G1: Caller Scope ──────► REJECT ──► AVAILABLE (log denial)
    │ PASS
    ▼
G2: Skill Ownership ───► REJECT ──► AVAILABLE (log denial)
    │ PASS
    ▼
G3: Namespace Boundary ─► REJECT ──► AVAILABLE (log violation)
    │ PASS
    ▼
G4: Dependency Check ───► FAIL ────► DEGRADED or FAILED
    │ PASS
    ▼
G5: Lifecycle Check ────► WARN ────► Proceed with deprecation warning
    │ PASS              ► REJECT ──► AVAILABLE (archived)
    ▼
G6: Security Policy ────► REJECT ──► AVAILABLE (forbidden)
    │ PASS
    ▼
LOADING → CONTEXT_READY → EXECUTING
```

---

## 5. Failure Handling System

### 5.1 Failure Classification

| Class | Name | Detection | Severity |
|:-----|:-----|:-----|:----:|
| **F1** | Context Failure | LOADING: file missing, SHA mismatch, OOM | HIGH |
| **F2** | Dependency Failure | G4: skill dep missing, runtime dep unavailable | HIGH |
| **F3** | Permission Failure | G1/G2/G3/G6: scope, ownership, namespace, policy violation | MEDIUM |
| **F4** | Skill Corruption | LOADING: SHA-256 mismatch; file unreadable | CRITICAL |
| **F5** | Timeout | EXECUTING: exceeds max duration (300s) | MEDIUM |
| **F6** | External Adapter Failure | EXECUTING: network error, API down, tool crash | MEDIUM |

### 5.2 Per-Class Response Matrix

| Class | Detection Point | Immediate Response | Recovery Action | Escalation |
|:-----|:-----|:-----|:-----|:-----|
| **F1** | LOADING | → FAILED | Retry load (1 attempt); if still fails → DEGRADED | Log to error-registry; mark skill DEGRADED |
| **F2** | G4 gate | → FAILED or DEGRADED | Resolve dependency; if unresolvable → fallback skill | Alert platform team; update dependency graph |
| **F3** | G1/G2/G3/G6 | → REJECT | Return to AVAILABLE; log denial | Alert if repeated denials (>5/24h) |
| **F4** | LOADING | → FAILED → QUARANTINED | Restore from backup; re-validate SHA-256 | **IMMEDIATE** alert to governance; block all dispatches |
| **F5** | EXECUTING | → FAILED | Retry with longer timeout (2x); if still fails → DEGRADED | Log to error-registry; adjust timeout config |
| **F6** | EXECUTING | → FAILED | Retry with fallback adapter; if unavailable → report to user | Log to error-registry; mark adapter DEGRADED |

---

## 6. Retry and Recovery Model

### 6.1 Retry Policy

| Parameter | Value | Rationale |
|:-----|:----:|:-----|
| Max retry count | 3 | Prevent infinite loops |
| Backoff strategy | Exponential: 1s, 2s, 4s | Avoid thundering herd |
| Retryable failures | F1, F2, F5, F6 | Transient errors only |
| Non-retryable failures | F3, F4 | Permission and corruption — retry won't help |
| Total recovery window | 60 seconds | Hard cap on all retry attempts |

### 6.2 Fallback Strategy

```
When retries exhausted or failure is non-retryable:

  1. Identify fallback skill from same capability domain
     → Query Registry: same capability, different skill
     → Prefer: same namespace > broader namespace > any

  2. If fallback exists:
     → Dispatch fallback skill
     → Mark original as DEGRADED
     → Log: "FALLBACK: {original} → {fallback}"

  3. If no fallback:
     → Report to user: "Skill {name} unavailable. No alternative found."
     → Mark original as FAILED
     → Log to error-registry

  4. After fallback execution:
     → Original skill stays DEGRADED until manual review
     → Fallback execution result returned to caller
```

### 6.3 Rollback Triggers

| Trigger | Action |
|:-----|:-----|
| F4 (corruption) detected | Restore skill from backup → re-validate SHA |
| 3 DEGRADED in 24h | QUARANTINE skill → manual review required |
| Forbidden state detected during execution | HALT execution → rollback to AVAILABLE → log violation |
| Cross-project access without declaration | HALT → REJECT → log PERMISSION_DENIED |

---

## 7. Skill Health State

### 7.1 Health Classification

```
┌─────────────────────────────────────────────────────────────┐
│                    SKILL HEALTH STATES                       │
│                                                             │
│  HEALTHY      — All metrics green, no recent failures       │
│  ───────                                                    │
│  Entry:  0 failures in 24h, success_rate ≥ 95%              │
│  Action: Normal dispatch                                    │
│                                                             │
│  WARNING      — Elevated failure rate, monitor closely      │
│  ───────                                                    │
│  Entry:  1-2 failures in 24h, OR success_rate 90-94%        │
│  Action: Dispatch with caution; increased logging           │
│                                                             │
│  DEGRADED     — Reduced capability, limited functionality   │
│  ────────                                                   │
│  Entry:  3+ failures in 24h, OR success_rate <90%           │
│  Action: Dispatch with warning; prefer fallback if available │
│                                                             │
│  FAILED       — Cannot execute, all attempts exhausted      │
│  ──────                                                     │
│  Entry:  All retries exhausted, no fallback available        │
│  Action: BLOCK dispatch; manual intervention required        │
│                                                             │
│  QUARANTINED  — Isolated for safety review                  │
│  ───────────                                                │
│  Entry:  F4 (corruption) detected, OR 5+ DEGRADED/24h       │
│  Action: BLOCK all dispatches; governance review required   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Health Transition Rules

```
HEALTHY ──(1-2 failures/24h)──► WARNING
WARNING ──(0 failures/24h)────► HEALTHY
WARNING ──(3+ failures/24h)───► DEGRADED
DEGRADED ──(0 failures/48h)───► WARNING
DEGRADED ──(5+ /24h)──────────► QUARANTINED
FAILED ──(manual fix)─────────► WARNING
QUARANTINED ──(governance review)──► HEALTHY (if cleared) or ARCHIVED
```

### 7.3 Health Check Frequency

| Health State | Check Interval | Action |
|:-----|:-----|:-----|
| HEALTHY | Every 5 minutes | Log metrics |
| WARNING | Every 1 minute | Alert platform team |
| DEGRADED | Every 30 seconds | Alert platform team + skill owner |
| FAILED | Continuous | Alert governance; block dispatch |
| QUARANTINED | Continuous | Alert governance; manual review |

---

## 8. Audit Trail

### 8.1 Execution Record Schema

```yaml
execution_id: "exec-20260718-143000-a3b2c1"
skill_id: "a3-multi-agent-pipeline"
skill_namespace: "project.a3.workflow"
skill_version: "3.6.0"
skill_scope: "project"
skill_owner: "a3-team"

caller:
  session_id: "sess-d4e5f6"
  scope: "project.a3"
  tier: 2

execution:
  resolved_at: "2026-07-18T14:30:00Z"
  loaded_at: "2026-07-18T14:30:01Z"
  started_at: "2026-07-18T14:30:02Z"
  completed_at: "2026-07-18T14:30:15Z"
  duration_ms: 13000

state_changes:
  - {from: "AVAILABLE", to: "RESOLVED", at: "14:30:00"}
  - {from: "RESOLVED", to: "LOADING", at: "14:30:00"}
  - {from: "LOADING", to: "CONTEXT_READY", at: "14:30:01"}
  - {from: "CONTEXT_READY", to: "EXECUTING", at: "14:30:02"}
  - {from: "EXECUTING", to: "SUCCESS", at: "14:30:15"}

gates_passed:
  - G1: {caller_scope: "project", result: "PASS"}
  - G2: {skill_owner: "a3-team", result: "PASS"}
  - G3: {namespace: "project.a3", result: "PASS"}
  - G4: {dependencies: 3, resolved: 3, result: "PASS"}
  - G5: {lifecycle: "active", result: "PASS"}
  - G6: {forbidden_pairs: 0, result: "PASS"}

result:
  status: "SUCCESS"
  output_type: "text"
  output_size_bytes: 4096

health_after:
  state: "HEALTHY"
  success_rate_24h: 98.5

error: null
recovery_action: null
```

### 8.2 Audit Trail Storage

```
Execution records stored in:
  ~/.hermes/audit/executions/{YYYY-MM}/{execution_id}.json

Retention:
  Active: 90 days (full detail)
  Archive: 365 days (summary only)
  Purge: after 365 days

Query interface:
  hermes audit execution <execution_id>
  hermes audit skill <skill_id> --last 24h
  hermes audit namespace <namespace> --since YYYY-MM-DD
```

---

## 9. Runtime Safety

### 9.1 Safety Verification Matrix

| # | Safety Rule | Verification Point | Response |
|:--|:-----|:-----|:-----|
| S1 | No unauthorized execution | G1 + G2: caller scope + ownership | REJECT at gate |
| S2 | No cross-namespace violation | G3: namespace boundary check | REJECT at gate |
| S3 | No silent replacement | LOADING: SHA-256 verification | FAILED → QUARANTINED |
| S4 | No untracked execution | All transitions: audit record written | BLOCK transition without record |
| S5 | No failed rollback | RECOVERY: backup integrity check | Alert governance if backup corrupt |
| S6 | No context leak | Post-execution: context RELEASED | Force-release on timeout |
| S7 | No forbidden pair execution | G6: forbidden_pairs check | REJECT at gate |
| S8 | No deprecated execution without warning | G5: lifecycle check | WARN but allow (grace period) |
| S9 | No archived execution | G5: lifecycle = archived | REJECT at gate |
| S10 | No quarantine bypass | QUARANTINED: all gates fail | REJECT all dispatches |

### 9.2 Safety Enforcement Layers

```
┌─────────────────────────────────────────┐
│ LAYER 1: Pre-execution Gates (§4)       │
│   G1-G6: All must PASS before LOADING   │
├─────────────────────────────────────────┤
│ LAYER 2: Loading Integrity              │
│   SHA-256 verification, file existence  │
├─────────────────────────────────────────┤
│ LAYER 3: Runtime Monitoring             │
│   Timeouts, health checks, state bounds │
├─────────────────────────────────────────┤
│ LAYER 4: Post-execution Audit           │
│   Record written, context released      │
└─────────────────────────────────────────┘
```

---

## 10. Architecture Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   SKILL EXECUTION LIFECYCLE ARCHITECTURE                      ║
║                                                              ║
║   Components designed:                                        ║
║     1. 13-state lifecycle with transition rules               ║
║     2. State machine with enforcement (valid + forbidden)     ║
║     3. Context lifecycle (5 states + cleanup rules)           ║
║     4. 6-gate pre-execution permission check                  ║
║     5. 6 failure classes (F1-F6) with response matrix        ║
║     6. Retry/recovery model (3 retries, exponential backoff)  ║
║     7. 5 health states with degradation thresholds            ║
║     8. Audit trail schema (execution record)                  ║
║     9. 10 runtime safety rules (S1-S10)                       ║
║                                                              ║
║   Compliance:                                                 ║
║     ✅ Governance Constitution v1.0                           ║
║     ✅ B.1 Resolver Architecture                              ║
║     ✅ C.3 Namespace Model                                    ║
║     ✅ Registry v1.1                                          ║
║     ✅ Forbidden states F1-F10                                ║
║                                                              ║
║   🟢 GREEN — Execution lifecycle approved                    ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ |
| 10 sections complete | ✅ |
| 13 states defined | ✅ |
| 7 forbidden transitions | ✅ |
| Context lifecycle (5 states) | ✅ |
| 6-gate permission check | ✅ |
| 6 failure classes (F1-F6) | ✅ |
| Retry model (3 attempts) | ✅ |
| 5 health states | ✅ |
| Audit trail schema | ✅ |
| 10 safety rules (S1-S10) | ✅ |
| 0 executable code | ✅ |

---

> **Phase:** B.2 — Skill Execution Lifecycle Architecture
> **Status:** ✅ DESIGN COMPLETE
> **Decision:** 🟢 GREEN — Execution lifecycle approved
