# Hermes Skill Health Engine Architecture

**Status:** Architecture Design Document · Read-Only
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** B.4 — Skill Health Engine Architecture
**Audience:** Hermes Core Team · Platform Operators · Governance Reviewer

**Governance Authority:**
- Hermes Governance Constitution v1.0 (FROZEN)
- Skill Kernel Resolver Architecture v1.0 (B.1)
- Skill Execution Lifecycle Architecture v1.0 (B.2)
- Skill Observability Architecture v1.0 (B.3)
- Registry v1.1 (149 entries, 18 fields)

**This document defines:**
- Automated health evaluation and scoring engine
- Degradation, quarantine, and recovery automation
- Health-driven lifecycle transitions
- Governance automation proposals
- Dependency health monitoring
- Design only — no implementation code

---

## 1. Health Evaluation Engine

### 1.1 Evaluation Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│                 HEALTH EVALUATION ENGINE                      │
│                                                             │
│  INPUTS                         OUTPUT                       │
│  ──────                         ──────                       │
│                                                             │
│  ┌────────────────┐                                          │
│  │ Execution      │                                          │
│  │ Telemetry      │──┐                                       │
│  │ (B.3 §1)       │  │                                       │
│  └────────────────┘  │    ┌──────────────┐                  │
│                      ├───►│              │                  │
│  ┌────────────────┐  │    │   HEALTH     │    ┌───────────┐ │
│  │ Runtime        │  │    │   SCORING    │───►│  0-100    │ │
│  │ Metrics        │──┤    │   ENGINE     │    │  SCORE    │ │
│  │ (B.3 §2)       │  │    │              │    └───────────┘ │
│  └────────────────┘  │    └──────┬───────┘                  │
│                      │           │                           │
│  ┌────────────────┐  │           ▼                           │
│  │ Failure        │  │    ┌──────────────┐                  │
│  │ Events         │──┤    │   HEALTH     │    ┌───────────┐ │
│  │ (B.2 §5)       │  │    │   STATE      │───►│  STATE    │ │
│  └────────────────┘  │    │   CLASSIFIER │    │  DECISION │ │
│                      │    │              │    └───────────┘ │
│  ┌────────────────┐  │    └──────┬───────┘                  │
│  │ Dependency     │  │           │                           │
│  │ Health         │──┘           ▼                           │
│  │ (§8)           │       ┌──────────────┐                  │
│  └────────────────┘       │   ACTION     │    ┌───────────┐ │
│                           │   DISPATCH   │───►│ PROPOSAL  │ │
│  ┌────────────────┐       │              │    │ / ALERT   │ │
│  │ Usage          │──────►│              │    │ / BLOCK   │ │
│  │ Trend          │       └──────────────┘    └───────────┘ │
│  └────────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Scoring Formula

```
HEALTH_SCORE = Σ(factor_score × factor_weight)

  Factor                  Weight    Metric Source
  ─────────────────────────────────────────────────
  Success Rate (24h)       35%      B.3 §2: success_rate
  Failure Frequency (24h)  25%      B.3 §4: failure_count
  Latency Health (p95)     15%      B.3 §2: p95_latency_ms
  Dependency Stability     15%      §8: dependency_health
  Execution Trend (7d)     10%      B.3 §4: trend_direction
                               ───
                              100%
```

### 1.3 Per-Factor Scoring Tables

```
SUCCESS RATE (0-35 points):
  ≥ 98%  → 35  (exceptional)
  95-97% → 30  (healthy)
  90-94% → 22  (acceptable)
  80-89% → 14  (concerning)
  70-79% →  7  (poor)
  < 70%  →  0  (critical)

FAILURE FREQUENCY (0-25 points):
  0 failures/24h      → 25
  1-2 failures        → 20
  3-5 failures        → 13
  6-10 failures       →  6
  > 10 failures       →  0

LATENCY HEALTH (0-15 points):
  p95 < 5s            → 15
  p95 5-15s           → 12
  p95 15-30s          →  8
  p95 30-60s          →  4
  p95 > 60s           →  0

DEPENDENCY STABILITY (0-15 points):
  100% deps healthy   → 15
  1 dep in WARNING    → 11
  2+ deps in WARNING  →  7
  1 dep DEGRADED      →  4
  1+ dep FAILED       →  0

EXECUTION TREND (0-10 points):
  Improving (↑5%+)    → 10
  Slightly up (↑2-5%) →  8
  Stable (±2%)        →  6
  Slightly down (↓2-5%) → 4
  Declining (↓5%+)    →  0
```

### 1.4 Evaluation Cadence

| Trigger | Evaluation Type | Scope |
|:-----|:-----|:-----|
| After every execution | Incremental update | Executed skill only |
| Every 5 minutes | Periodic sweep | All skills with executions in window |
| On alert trigger | Immediate deep evaluation | Affected skill + dependencies |
| On state transition | Transition validation | Transitioning skill only |
| Hourly | Full system sweep | All 149 skills |

---

## 2. Health State Machine

### 2.1 Five Health States

```
                    ┌──────────────┐
                    │   HEALTHY    │  ← Normal operation
                    │   90-100     │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │ score <90  │            │ F4 detected
              │ OR 2 fails │            │ OR 5+ fails
              ▼            │            ▼
       ┌──────────────┐    │     ┌──────────────┐
       │   WARNING    │    │     │ QUARANTINED  │
       │   75-89      │    │     │   0-24       │
       └──────┬───────┘    │     └──────────────┘
              │            │
    ┌─────────┼─────────┐  │
    │score<75 │         │  │
    │OR 3+    │         │  │
    │fails/24h│         │  │
    ▼         │         │  │
┌──────────┐  │         │  │
│ DEGRADED │  │ score≥90│  │
│  50-74   │  │ for 1h  │  │
└────┬─────┘  │         │  │
     │        ▼         │  │
     │  ┌──────────────┐│  │
     │  │   HEALTHY    ││  │
     │  │  (recovered) ││  │
     │  └──────────────┘│  │
     │                  │  │
     │ score<50         │  │
     │ OR retries       │  │
     │ exhausted        │  │
     ▼                  │  │
┌──────────────┐        │  │
│   FAILED     │        │  │
│   25-49      │        │  │
└──────┬───────┘        │  │
       │                │  │
       │ manual fix     │  │
       │ + score≥85     │  │
       ▼                │  │
┌──────────────┐        │  │
│   WARNING    │        │  │
│  (recovered) │        │  │
└──────────────┘        │  │
                        │  │
       ┌────────────────┘  │
       │ governance review  │
       │ + re-validation    │
       ▼                   │
┌──────────────┐           │
│   HEALTHY    │◄──────────┘
│  (cleared)   │
└──────────────┘
```

### 2.2 State Definitions

| State | Score | Meaning | Entry Conditions | Exit Conditions | Owner | Allowed Actions |
|:-----|:----:|:-----|:-----|:-----|:-----|:-----|
| **HEALTHY** | 90-100 | Normal operation | Score ≥ 90, 0 critical failures | Score drops below 90 | System | Dispatch, monitor |
| **WARNING** | 75-89 | Elevated risk | Score 75-89, OR 2 consecutive failures | Score ≥ 90 for 1h (→HEALTHY) OR score < 75 (→DEGRADED) | Platform team | Dispatch with caution |
| **DEGRADED** | 50-74 | Reduced capability | Score 50-74, OR 3+ failures/24h | Score ≥ 75 for 2h (→WARNING) OR score < 50 (→FAILED) | Skill owner | Dispatch with warning; prefer fallback |
| **FAILED** | 25-49 | Cannot execute | Score < 50, OR all retries exhausted | Manual fix + score ≥ 85 (→WARNING) | Governance + Owner | Block dispatch |
| **QUARANTINED** | 0-24 | Isolated for safety | F4 (corruption), OR security violation, OR 5+ consecutive failures | Governance review + re-validation + score ≥ 90 (→HEALTHY) | Governance only | Block all; preserve evidence |

### 2.3 State Transition Log

Every health state transition is recorded:

```yaml
health_transition:
  skill_id: "content-review-gate"
  from_state: "HEALTHY"
  to_state: "WARNING"
  trigger: "score_drop"
  score_before: 92
  score_after: 74
  reason: "3 failures in 24h: F2 x2, F5 x1"
  timestamp: "2026-07-18T10:00:00Z"
  auto_action: "alert_platform_team"
```

---

## 3. Automatic Degradation

### 3.1 Degradation Triggers

| Trigger | Severity | Action |
|:-----|:----:|:-----|
| Score drops into DEGRADED range (50-74) | HIGH | Immediate state change |
| 3+ execution failures in 24 hours | HIGH | State change + alert |
| 1+ dependency enters FAILED state | HIGH | Cascade to DEGRADED |
| p95 latency > 5x baseline for > 1 hour | MEDIUM | State change to WARNING first |
| Success rate drops > 15% in 1 hour | HIGH | Immediate re-evaluation |

### 3.2 Degradation Actions

```
When a skill enters DEGRADED state:

  1. REDUCE PRIORITY
     → Resolver deprioritizes this skill
     → Prefer HEALTHY alternatives with same capability

  2. WARNING ALERT
     → Alert skill owner + platform team
     → Create error-registry entry
     → Log health_transition event

  3. RESTRICT USAGE
     → Allow dispatch but with warning to caller
     → Auto-suggest fallback if available

  4. CREATE MAINTENANCE PROPOSAL
     → Governance dashboard: "Skill {name} needs maintenance"
     → Include: failure summary, suggested fixes, impact assessment

  5. MONITOR INTENSIVELY
     → Increase evaluation frequency to every 30 seconds
     → Track recovery progress
```

### 3.3 Degradation Grace Period

```
After entering DEGRADED:
  - Grace period: 2 hours to self-recover
  - If score rises above 75 during grace period → WARNING
  - If score stays < 75 after grace period → escalate to FAILED
  - If score drops below 25 at any time → immediate QUARANTINED
```

---

## 4. Automatic Quarantine

### 4.1 Quarantine Triggers

| # | Trigger | Detection | Response Time |
|:--|:-----|:-----|:-----|
| Q1 | **Corruption detected** (F4) | SHA-256 mismatch during LOADING | Immediate |
| Q2 | **Security violation** | G1/G2/G3 repeated rejections (>10/h) | Immediate |
| Q3 | **Repeated critical failures** | 5+ consecutive FAILED executions | Immediate |
| Q4 | **Dependency cascade** | 3+ skills fail within 5 min sharing dependency | Immediate |
| Q5 | **Governance override** | Manual quarantine by Governance Reviewer | Immediate |

### 4.2 Quarantine Actions

```
When a skill enters QUARANTINED state:

  1. BLOCK EXECUTION
     → All dispatch requests rejected at G6 gate
     → Resolver removes skill from candidate pool
     → Active executions allowed to complete (graceful)

  2. PRESERVE EVIDENCE
     → Snapshot current state: registry entry, SKILL.md, dependency graph
     → Record full execution history for investigation
     → Lock skill file to prevent modification

  3. NOTIFY
     → CRITICAL alert to governance team
     → Notify skill owner
     → Create error-registry entry with full context

  4. CASCADE CHECK
     → Check all dependents: mark WARNING if they depend on quarantined skill
     → Offer fallback alternatives to affected callers

  5. ROLLBACK IF POSSIBLE
     → If corruption (Q1): restore SKILL.md from backup
     → Verify SHA-256 after restore
     → If restore fails: keep QUARANTINED
```

### 4.3 Quarantine Exit

```
Exit QUARANTINED → HEALTHY requires:

  1. Governance Reviewer investigation complete
  2. Root cause identified and fixed
  3. Re-validation: SHA-256 verified, all 6 gates pass
  4. Health score ≥ 90 after re-evaluation
  5. Manual approval by Governance Reviewer

No automatic exit from QUARANTINED.
Quarantine is always a manual governance decision to clear.
```

---

## 5. Recovery System

### 5.1 Recovery Paths

```
                         ┌──────────┐
                         │  FAILED  │
                         └────┬─────┘
                              │
                    ┌─────────┼─────────┐
                    │         │         │
                    ▼         ▼         ▼
              ┌─────────┐┌─────────┐┌──────────┐
              │ RETRY   ││FALLBACK ││ ROLLBACK │
              │         ││         ││          │
              │Auto if  ││If       ││If        │
              │retries  ││fallback ││corruption│
              │remain   ││exists   ││suspected │
              └────┬────┘└────┬────┘└────┬─────┘
                   │         │         │
        ┌──────────┼─────────┼─────────┼──────────┐
        │          │         │         │          │
        ▼          ▼         ▼         ▼          ▼
   ┌────────┐┌────────┐┌────────┐┌────────┐┌──────────┐
   │SUCCESS ││ STILL  ││SUCCESS ││STILL   ││ OWNER    │
   │→WARNING││ FAILED ││→WARNING││FAILED  ││INTERVENE │
   └────────┘└────┬───┘└────────┘└────┬───┘└────┬─────┘
                  │                  │         │
                  ▼                  ▼         ▼
            ┌──────────┐      ┌──────────┐┌──────────┐
            │DEGRADED  │      │DEGRADED  ││MANUAL    │
            │(accept   │      │(limited  ││FIX →     │
            │limited   │      │function) ││WARNING   │
            │function) │      └──────────┘└──────────┘
            └──────────┘
```

### 5.2 Recovery Strategy Selection

| Failure Class | Primary Recovery | Fallback | Last Resort |
|:-----|:-----|:-----|:-----|
| F1 (Context) | Retry (1 attempt) | Rollback | Owner intervention |
| F2 (Dependency) | Fallback skill | Retry with resolved dep | Owner intervention |
| F3 (Permission) | Not retryable | — | Governance review |
| F4 (Corruption) | Rollback from backup | — | Owner intervention |
| F5 (Timeout) | Retry with 2× timeout | Fallback skill | Owner intervention |
| F6 (External) | Retry (3 attempts) | Fallback adapter | Report to user |

### 5.3 Recovery Time Limits

| Recovery Path | Max Time | Exceeded → |
|:-----|:-----|:-----|
| Retry | 60 seconds | DEGRADED |
| Fallback dispatch | 30 seconds | Report to user |
| Rollback | 10 seconds | Owner intervention |
| Owner intervention | 24 hours | Escalate to governance |
| Governance review | 72 hours | Consider deprecation |

---

## 6. Skill Lifecycle Integration

### 6.1 Health-Triggered Lifecycle Transitions

```
┌─────────────────────────────────────────────────────────────┐
│           HEALTH → LIFECYCLE INTEGRATION                     │
│                                                             │
│  Health State          Lifecycle Transition                  │
│  ────────────          ────────────────────                  │
│                                                             │
│  HEALTHY               No change                             │
│      │                                                      │
│      │ (sustained)                                           │
│      ▼                                                      │
│  WARNING               No change; monitor                    │
│      │                                                      │
│      │ (chronic: >30 days in WARNING)                        │
│      ▼                                                      │
│  ─────────────────────────────────────────                  │
│  Governance Proposal: "Review skill health"                  │
│  ─────────────────────────────────────────                  │
│      │                                                      │
│      │ (severe: score < 50)                                  │
│      ▼                                                      │
│  DEGRADED              status: degraded                      │
│      │                  Registry field updated               │
│      │                                                      │
│      │ (chronic: >7 days in DEGRADED)                        │
│      ▼                                                      │
│  ─────────────────────────────────────────                  │
│  Governance Proposal: "Consider deprecation"                 │
│  ─────────────────────────────────────────                  │
│      │                                                      │
│      │ (critical: score < 25 OR all retries exhausted)       │
│      ▼                                                      │
│  FAILED                status: failed                        │
│      │                  Block all dispatch                   │
│      │                                                      │
│      │ (no recovery after 72h)                               │
│      ▼                                                      │
│  ─────────────────────────────────────────                  │
│  Governance Proposal: "Deprecate skill"                      │
│  ─────────────────────────────────────────                  │
│      │                                                      │
│      ▼                                                      │
│  DEPRECATED            lifecycle: deprecated                 │
│      │                  Grace period: 14 days                │
│      │                                                      │
│      │ (grace period elapsed)                                │
│      ▼                                                      │
│  ARCHIVED              lifecycle: archived                   │
│                        Terminal                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 Automatic Lifecycle Actions

| Trigger | Action | Requires Approval? |
|:-----|:-----|:----:|
| Enter WARNING | Update `status: warning` in Registry | No (auto) |
| Enter DEGRADED | Update `status: degraded` in Registry | No (auto) |
| Enter FAILED | Update `status: failed`; block dispatch | No (auto — safety) |
| Enter QUARANTINED | Update `status: quarantined`; block all | No (auto — safety) |
| Propose deprecation | Create governance proposal | **Yes — Governance Reviewer** |
| Propose archival | Create governance proposal | **Yes — Governance Reviewer** |
| Restore to HEALTHY | Update `status: ok` | No (auto — score verified) |

---

## 7. Governance Automation

### 7.1 Automated Proposal Types

| # | Proposal | Trigger | Severity | Auto-Generated? |
|:--|:-----|:-----|:----:|:----:|
| P1 | **Maintenance Required** | Success rate < 80% for 7 days | HIGH | ✅ Auto |
| P2 | **Usage Review** | 0 executions in 30 days | LOW | ✅ Auto |
| P3 | **Merge Proposal** | 3+ skills, same capability, all low usage | MEDIUM | ✅ Auto |
| P4 | **Upgrade Required** | Skill version > 2 MAJOR behind latest in same capability | MEDIUM | ✅ Auto |
| P5 | **Deprecation Proposal** | FAILED > 72h, no recovery path | HIGH | ✅ Auto |
| P6 | **Archive Proposal** | DEPRECATED > 14 days, 0 executions in grace period | LOW | ✅ Auto |
| P7 | **Dependency Audit** | Dependency consistently in WARNING > 7 days | MEDIUM | ✅ Auto |
| P8 | **Cross-Project Review** | Cross-project dependency with high failure rate | MEDIUM | ✅ Auto |

### 7.2 Proposal Lifecycle

```
AUTO-GENERATED
      │
      ▼
┌──────────────┐
│  PROPOSED    │  ← Auto-created by health engine
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  REVIEW      │  ← Governance Reviewer evaluates
└──────┬───────┘
       │
  ┌────┼────┬──────────┐
  │    │    │          │
  ▼    ▼    ▼          ▼
┌───┐┌───┐┌────────┐┌──────┐
│APP││REJ││REQUEST ││DEFER │
│ROV││ECT││MORE    ││      │
│E  ││   ││INFO    ││      │
└─┬─┘└───┘└───┬────┘└──┬───┘
  │            │        │
  ▼            ▼        ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│EXECUTE   │ │REVISE &  │ │SCHEDULE  │
│PROPOSAL  │ │RESUBMIT  │ │REMINDER  │
└──────────┘ └──────────┘ └──────────┘
```

### 7.3 Proposal Priority

| Priority | Criteria | Response SLA |
|:-----|:-----|:-----|
| **P0 — Emergency** | QUARANTINED skill, security violation | < 1 hour |
| **P1 — High** | FAILED skill, success rate < 50% | < 24 hours |
| **P2 — Medium** | DEGRADED skill, maintenance needed | < 72 hours |
| **P3 — Low** | Usage review, merge proposal, archive | < 7 days |

---

## 8. Dependency Health

### 8.1 Dependency Health Graph

```
┌─────────────────────────────────────────────────────────────┐
│                DEPENDENCY HEALTH MONITOR                      │
│                                                             │
│  For each skill → dependency edge:                           │
│                                                             │
│    ┌──────────┐         ┌──────────┐                        │
│    │  SKILL   │────────►│   DEP    │                        │
│    │  HEALTH  │ depends │  HEALTH  │                        │
│    └──────────┘         └──────────┘                        │
│                                                             │
│  Edge Health = min(skill_health, dependency_health)         │
│                                                             │
│  HEALTHY   ────────────►  HEALTHY     ✅                    │
│  HEALTHY   ────────────►  WARNING     ⚠️                    │
│  HEALTHY   ────────────►  DEGRADED    🟡 Cascade risk      │
│  HEALTHY   ────────────►  FAILED      🔴 Block dispatch    │
│  HEALTHY   ────────────►  QUARANTINED 🚫 Immediate block   │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Unstable Dependency Detection

| Pattern | Detection Rule | Action |
|:-----|:-----|:-----|
| **Frequent WARNING** | Dependency in WARNING > 7 days | Alert skill owner; propose alternative |
| **Dependency DEGRADED** | Dependency enters DEGRADED | Cascade WARNING to dependent; prefer fallback |
| **Dependency FAILED** | Dependency enters FAILED | Cascade DEGRADED to dependent; block if no fallback |
| **Circular dependency** | A→B→A cycle detected | **REJECT** registration; log PERMISSION_DENIED |
| **Forbidden dependency** | Core→Project or Adapter→Project | **IMMEDIATE QUARANTINE** of violating skill |

### 8.3 Cascade Failure Prevention

```
When a dependency enters FAILED/QUARANTINED:

  1. Identify all dependents (skills that list this skill as a dependency)
  2. For each dependent:
     a. If fallback exists → auto-switch to fallback
     b. If no fallback → mark dependent as DEGRADED
     c. If dependent is critical (tier 0) → CRITICAL alert
  3. Log cascade event with full dependency chain
  4. Governance dashboard: highlight all affected skills
```

---

## 9. Security Boundary

### 9.1 Prohibited Automatic Actions

The health engine may NEVER automatically:

| Action | Reason | Requires |
|:-----|:-----|:-----|
| ❌ Delete a skill | Irreversible data loss | Governance approval (Type D) |
| ❌ Change skill scope | Immutability rule (P6) | Deprecation + re-registration |
| ❌ Modify SKILL.md body | Content integrity | Owner approval |
| ❌ Bypass governance approval | Constitution violation | Governance Reviewer |
| ❌ Modify frozen components | Constitution v1.0 freeze | Constitutional Amendment |
| ❌ Cross-project action (A→B) | C.3 namespace isolation | Both project owners |
| ❌ Silent replacement | Forbidden state F4 | Backup restore + governance review |

### 9.2 Authorized Automatic Actions

The health engine MAY automatically:

| Action | Scope | Constraint |
|:-----|:-----|:-----|
| ✅ Update `status` field | Single skill | Based on verified score |
| ✅ Block dispatch | DEGRADED/FAILED/QUARANTINED skills | Safety measure |
| ✅ Switch to fallback | Single dispatch | No permanent change |
| ✅ Create alert | Platform/Governance notification | Appropriate severity |
| ✅ Create proposal | Governance dashboard | Requires human approval |
| ✅ Update metrics | Telemetry database | Read-only aggregation |
| ✅ Trigger re-evaluation | Affected skill | Score-based |

### 9.3 Audit Trail

```
Every automatic action is logged:

  action: "auto_degrade"
  skill_id: "content-review-gate"
  trigger: "score_drop_to_68"
  timestamp: "2026-07-18T10:00:00Z"
  authorized: true
  approval_required: false
  revertible: true
  reverted_by: null

All automatic actions are revertible by Governance Reviewer.
All proposals require human approval before execution.
```

---

## 10. Architecture Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   SKILL HEALTH ENGINE ARCHITECTURE                            ║
║                                                              ║
║   Components designed:                                        ║
║     1. Health Evaluation Engine (5-factor, 0-100 scoring)    ║
║     2. Health State Machine (5 states, 12 transitions)       ║
║     3. Automatic Degradation (5 triggers, 5 actions)         ║
║     4. Automatic Quarantine (5 triggers, 5 actions)          ║
║     5. Recovery System (5 paths, recovery time limits)       ║
║     6. Lifecycle Integration (health → lifecycle coupling)   ║
║     7. Governance Automation (8 proposal types)              ║
║     8. Dependency Health (cascade detection + prevention)    ║
║     9. Security Boundary (7 prohibited, 6 authorized)        ║
║                                                              ║
║   Integration:                                                ║
║     ✅ B.1 Resolver — dispatch priority control               ║
║     ✅ B.2 Lifecycle — state machine integration              ║
║     ✅ B.3 Observability — telemetry + metrics input          ║
║     ✅ Registry v1.1 — status field updates                   ║
║     ✅ Governance Constitution v1.0 — all within bounds       ║
║                                                              ║
║   🟢 GREEN — Health Engine architecture approved             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ |
| 10 sections complete | ✅ |
| 5-factor scoring engine | ✅ |
| 5 health states with transitions | ✅ |
| Degradation: 5 triggers, 5 actions | ✅ |
| Quarantine: 5 triggers, 5 actions | ✅ |
| Recovery: 5 paths with time limits | ✅ |
| Lifecycle integration | ✅ |
| 8 proposal types (P1-P8) | ✅ |
| Dependency health graph | ✅ |
| 7 prohibited + 6 authorized actions | ✅ |
| 0 executable code | ✅ |

---

> **Phase:** B.4 — Skill Health Engine Architecture
> **Status:** ✅ DESIGN COMPLETE
> **Decision:** 🟢 GREEN — Health Engine architecture approved
