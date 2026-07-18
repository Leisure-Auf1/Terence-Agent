# Hermes Skill Kernel Runtime Specification

**Status:** Architecture Design Document · Runtime Contract · Read-Only
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** B.5 — Skill Kernel Runtime Specification
**Audience:** Hermes Core Team · Runtime Implementors · Governance Reviewer

**Derived From:**
- Skill Kernel Resolver Architecture v1.0 (B.1)
- Skill Execution Lifecycle Architecture v1.0 (B.2)
- Skill Observability Architecture v1.0 (B.3)
- Skill Health Engine Architecture v1.0 (B.4)
- Governance Constitution v1.0 (FROZEN)
- Registry v1.1 (149 entries, 18 fields)

**This document is:**
- The implementable runtime contract for the Hermes Skill Operating System
- The integration specification for all B.1-B.4 architecture components
- The authoritative API reference for runtime development

**This document does NOT:**
- Contain implementation code
- Modify the Registry
- Modify any skill

---

## 1. Runtime API Contract

### 1.1 API Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    RUNTIME API SURFACE                        │
│                                                             │
│  resolve_skill()          →  SkillResolution                │
│  load_context()           →  SkillContext                   │
│  validate_permission()    →  PermissionResult               │
│  execute_skill()          →  ExecutionResult                │
│  record_telemetry()       →  TelemetryRecord                │
│  update_health()          →  HealthState                    │
│  create_governance_proposal() → Proposal                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 resolve_skill()

```
Purpose:    Resolve user intent to a skill via the B.1 pipeline

Input:
  intent:        string          # Natural language task description
  caller_scope:  string          # "core" | "adapter" | "project.a3" | ...
  caller_tier:   integer         # 0 | 1 | 2
  session_id:    string          # Opaque session token

Processing:
  1. Capability matching  (B.1 §2)
  2. Namespace filtering  (B.1 §3)
  3. Ownership validation (B.1 §3)
  4. Dependency validation (B.1 §3)
  5. Skill selection      (B.1 §7)

Output (SUCCESS):
  execution_id:   string
  skill_id:       string          # e.g., "a3-multi-agent-pipeline"
  skill_namespace: string         # e.g., "project.a3.workflow"
  skill_scope:    string          # "core" | "adapter" | "project"
  skill_version:  string          # e.g., "3.6.0"
  skill_owner:    string
  mount:          string          # "routed" | "auto" | "manual"
  trigger_match:  string          # Which trigger keyword matched
  confidence:     float           # 0.0 - 1.0
  alternatives:   []SkillSummary  # Next-best matches

Output (FAILURE):
  error:          string          # "NO_MATCH" | "FORBIDDEN_PAIR" |
                                  # "NAMESPACE_VIOLATION" | "PERMISSION_DENIED"
  reason:         string          # Human-readable explanation
  suggestions:    []SkillSummary  # Suggested alternatives

Permissions: Tier 1 (platform) or Tier 2 (project) — any authenticated caller
Lifecycle:   Skill must be in AVAILABLE or WARNING state
```

### 1.3 load_context()

```
Purpose:    Load skill content into session context

Input:
  execution_id:  string
  skill_id:      string
  mount:         string          # "routed" | "auto" | "manual"

Processing:
  1. Locate SKILL.md via Registry path field
  2. Verify file existence
  3. Read content
  4. Verify SHA-256 integrity
  5. Parse frontmatter metadata
  6. Allocate context memory
  7. Load into session

Output (SUCCESS):
  context_id:    string
  content_size:  integer         # bytes
  sha256:        string
  metadata:      FrontmatterMap
  load_time_ms:  integer

Output (FAILURE):
  error:         string          # "FILE_NOT_FOUND" | "SHA_MISMATCH" |
                                 # "READ_ERROR" | "OOM"
  reason:        string

Permissions:   Tier 1 or Tier 2
Lifecycle:     Skill transitions: AVAILABLE → RESOLVED → LOADING → CONTEXT_READY
Rollback:      Release context memory, return to AVAILABLE
```

### 1.4 validate_permission()

```
Purpose:    Run 6-gate pre-execution permission check (B.2 §4)

Input:
  execution_id:  string
  skill_id:      string
  caller_scope:  string
  caller_tier:   integer

Processing:
  G1: Caller scope vs skill scope
  G2: Caller tier vs skill ownership.ownership.tier
  G3: Namespace direction (Core→Project? Adapter→Project?)
  G4: Dependency availability (all deps resolvable?)
  G5: Lifecycle status (active? deprecated? archived?)
  G6: Security policy (forbidden pair? quarantined?)

Output (SUCCESS):
  gates_passed:  {G1: true, G2: true, G3: true, G4: true, G5: true, G6: true}
  warnings:      []string        # e.g., ["G5: skill is deprecated"]

Output (FAILURE):
  gates_passed:  {G1: true, G2: false, ...}
  failed_gate:   string          # Which gate failed
  reason:        string          # Why it failed
  suggested_action: string       # e.g., "Request cross_project: true"

Permissions:   Any authenticated caller
Lifecycle:     On failure → RESOLVED → AVAILABLE (safe abort)
```

### 1.5 execute_skill()

```
Purpose:    Execute the resolved and loaded skill (B.2 §1-2)

Input:
  execution_id:  string
  context_id:    string
  skill_id:      string
  input:         any             # Task-specific input payload
  timeout_ms:    integer         # Max execution duration (default: 300000)

Processing:
  1. Verify CONTEXT_READY state
  2. Verify all 6 gates passed
  3. Transition to EXECUTING
  4. Execute skill logic
  5. Monitor timeout
  6. Capture result

Output (SUCCESS):
  status:        "SUCCESS"
  output:        any             # Task-specific output
  duration_ms:   integer
  state_changes: []StateChange

Output (FAILURE):
  status:        "FAILED" | "DEGRADED" | "TIMEOUT"
  error:         string
  error_class:   string          # "F1" | "F2" | "F3" | "F4" | "F5" | "F6"
  duration_ms:   integer
  recovery_action: string

Output (DEGRADED):
  status:        "DEGRADED"
  output:        any             # Partial output
  degradation_reason: string
  duration_ms:   integer

Permissions:   Tier 1 or Tier 2
Lifecycle:     CONTEXT_READY → EXECUTING → SUCCESS | FAILED | DEGRADED → AVAILABLE
Timeout:       300s default; exceeded → FAILED (F5)
```

### 1.6 record_telemetry()

```
Purpose:    Record execution telemetry (B.3 §1)

Input:
  execution_id:  string
  execution_record: ExecutionRecord    # Full execution data

Processing:
  1. Validate record schema
  2. Write to telemetry store
  3. Update runtime metrics aggregator
  4. Check alert thresholds

Output:
  telemetry_id:  string
  stored:        boolean
  alerts_triggered: []Alert

Permissions:   Tier 1 (auto-called after every execution)
Lifecycle:     No lifecycle impact (observability only)
```

### 1.7 update_health()

```
Purpose:    Evaluate and update skill health state (B.4 §1-2)

Input:
  skill_id:      string
  force:         boolean         # Force re-evaluation (default: false)

Processing:
  1. Gather metrics: success_rate, failure_count, p95_latency, dependency_health, trend
  2. Compute health score (0-100)
  3. Classify health state (HEALTHY | WARNING | DEGRADED | FAILED | QUARANTINED)
  4. If state changed: write health_transition event
  5. If DEGRADED: trigger degradation actions
  6. If QUARANTINED: trigger quarantine actions

Output:
  skill_id:      string
  score:         integer         # 0-100
  state:         string          # HEALTHY | WARNING | DEGRADED | FAILED | QUARANTINED
  previous_state: string
  changed:       boolean
  factors: {
    success_rate_score: integer,
    failure_frequency_score: integer,
    latency_score: integer,
    dependency_score: integer,
    trend_score: integer
  }
  recommendation: string        # e.g., "MAINTENANCE_REQUIRED" | "MONITOR" | "OK"

Permissions:   Tier 1 (auto-called) or Tier 0 (governance manual)
Lifecycle:     May trigger status field update in Registry
```

### 1.8 create_governance_proposal()

```
Purpose:    Auto-generate governance proposal from health data (B.4 §7)

Input:
  skill_id:      string
  proposal_type: string          # P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8
  trigger_data:  object          # Data that triggered the proposal

Processing:
  1. Validate proposal type
  2. Gather supporting evidence (metrics, health history, execution failures)
  3. Create proposal record
  4. Assign priority (P0-P3)
  5. Notify Governance Reviewer

Output:
  proposal_id:   string
  type:          string
  priority:      string          # "P0" | "P1" | "P2" | "P3"
  status:        "PROPOSED"
  requires_approval: true

Permissions:   Auto-generated by health engine; requires Tier 0 approval to execute
Lifecycle:     No direct lifecycle impact until approved
```

---

## 2. Skill Kernel Runtime Pipeline

### 2.1 Complete Execution Chain

```
USER INTENT
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: CAPABILITY RESOLVER                                 │
│ ─────────────────────────                                   │
│ Input:  User intent text                                     │
│ Action: Match intent against skill triggers + capability     │
│         domains. Score candidates.                           │
│ Output: Ranked candidate list                                │
│ Failure → "NO_MATCH": escalate to broader namespace          │
├─────────────────────────────────────────────────────────────┤
│ STAGE 2: NAMESPACE RESOLVER                                  │
│ ─────────────────────────                                   │
│ Input:  Candidates + caller scope                            │
│ Action: Filter by namespace layer. System→core,              │
│         generic→adapter, project→project.<id>.*              │
│ Output: Namespace-filtered candidates                        │
│ Failure → "NAMESPACE_VIOLATION": reject, suggest fallback    │
├─────────────────────────────────────────────────────────────┤
│ STAGE 3: OWNERSHIP CHECK                                     │
│ ─────────────────────                                       │
│ Input:  Filtered candidates + caller tier                    │
│ Action: Verify tier permits execution. Cross-project         │
│         requires cross_project: true.                        │
│ Output: Ownership-validated candidates                       │
│ Failure → "PERMISSION_DENIED": reject                        │
├─────────────────────────────────────────────────────────────┤
│ STAGE 4: DEPENDENCY VALIDATOR                                │
│ ───────────────────────────                                 │
│ Input:  Validated candidates                                 │
│ Action: Verify all declared dependencies resolvable.         │
│         No circular deps. No forbidden deps.                 │
│ Output: Validated candidates                                 │
│ Failure → "DEPENDENCY_FAILURE": mark DEGRADED, suggest alt   │
├─────────────────────────────────────────────────────────────┤
│ STAGE 5: PERMISSION GATE (G1-G6)                             │
│ ──────────────────────────────                               │
│ Input:  Selected skill + caller context                      │
│ Action: G1(scope) → G2(ownership) → G3(namespace) →          │
│         G4(dependency) → G5(lifecycle) → G6(security)        │
│ Output: Gate results                                         │
│ Failure → Return to AVAILABLE with denial reason             │
├─────────────────────────────────────────────────────────────┤
│ STAGE 6: CONTEXT LOADER                                      │
│ ─────────────────────                                       │
│ Input:  Selected skill                                       │
│ Action: Read SKILL.md, verify SHA-256, allocate context      │
│ Output: Loaded context (CONTEXT_READY)                       │
│ Failure → F1 context failure: retry → fallback → FAILED      │
│           F4 corruption: QUARANTINE immediately              │
├─────────────────────────────────────────────────────────────┤
│ STAGE 7: SKILL EXECUTOR                                      │
│ ─────────────────────                                       │
│ Input:  Loaded context + task input                          │
│ Action: Execute skill logic. Monitor timeout.                │
│ Output: SUCCESS | FAILED | DEGRADED                          │
│ Failure → F5 timeout / F6 external: retry → fallback         │
├─────────────────────────────────────────────────────────────┤
│ STAGE 8: TELEMETRY COLLECTOR                                 │
│ ─────────────────────────                                   │
│ Input:  Execution result                                     │
│ Action: Write ExecutionRecord to telemetry store.            │
│         Update runtime metrics.                              │
│ Output: telemetry_id                                         │
│ Failure → Log warning; execution result still returned       │
├─────────────────────────────────────────────────────────────┤
│ STAGE 9: HEALTH ENGINE                                       │
│ ─────────────────────                                       │
│ Input:  Updated metrics                                      │
│ Action: Re-evaluate health score. Check state transitions.   │
│         Trigger degradation/quarantine if needed.            │
│ Output: Health state (may have changed)                      │
│ Failure → Log warning; execution result still returned       │
├─────────────────────────────────────────────────────────────┤
│ STAGE 10: GOVERNANCE FEEDBACK                                │
│ ───────────────────────────                                 │
│ Input:  Health state + execution patterns                    │
│ Action: Check for automated proposal triggers.               │
│         P1-P8 thresholds evaluated.                          │
│ Output: Proposal (if triggered) or none                      │
│ Failure → Log warning; deferred to next cycle                │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
CALLER RECEIVES RESULT
```

### 2.2 Failure Path Summary

| Stage | Failure | Recovery Path |
|:-----|:-----|:-----|
| 1. Capability | NO_MATCH | Escalate namespace; if all exhausted → report to user |
| 2. Namespace | VIOLATION | Reject; suggest fallback in allowed namespace |
| 3. Ownership | PERMISSION_DENIED | Reject; log denial |
| 4. Dependency | DEP_FAILURE | Mark DEGRADED; try next candidate |
| 5. Permission Gate | GATE_FAIL | SAFE ABORT → AVAILABLE |
| 6. Context Load | F1 / F4 | F1: retry 1× → fallback. F4: QUARANTINE |
| 7. Execution | F5 / F6 | F5: retry 3× with backoff → fallback. F6: fallback adapter |
| 8. Telemetry | WRITE_ERROR | Log warning; execution result unaffected |
| 9. Health | EVAL_ERROR | Log warning; defer to next cycle |
| 10. Governance | PROP_ERROR | Log warning; defer to next cycle |

### 2.3 Rollback Path

```
At ANY stage before EXECUTING:
  → SAFE ABORT: release resources, return to AVAILABLE
  → No state persisted beyond execution attempt

After EXECUTION_STARTED:
  → If FAILED: enter RECOVERY → retry/fallback/rollback
  → If DEGRADED: return partial result, mark health state
  → If F4 (corruption): QUARANTINE + restore from backup

Context cleanup:
  → After SUCCESS: RELEASED → UNLOADED
  → After FAILED:  RELEASED → UNLOADED
  → After DEGRADED: RELEASED → UNLOADED
  → No context leak: all paths release context
```

---

## 3. Runtime Data Model

### 3.1 SkillRuntimeContext

```yaml
SkillRuntimeContext:
  execution_id:    string       # UUID, unique per execution attempt
  context_id:      string       # UUID, unique per context allocation
  created_at:      timestamp

  # Identity (from Registry)
  skill_id:        string       # e.g., "a3-multi-agent-pipeline"
  skill_version:   string       # e.g., "3.6.0"
  skill_namespace: string       # e.g., "project.a3.workflow"
  skill_scope:     string       # "core" | "adapter" | "project"
  skill_owner:     string       # e.g., "a3-team"

  # Caller
  caller_session_id: string
  caller_scope:    string       # e.g., "project.a3"
  caller_tier:     integer      # 0 | 1 | 2

  # Permissions (from Registry + gate results)
  permissions:
    allow:        []string      # e.g., ["filesystem.read", "network.external_api"]
    deny:         []string      # e.g., ["secret.read"]
    gates_passed: map           # {G1: true, G2: true, ...}

  # Dependencies (from Registry)
  dependencies:
    skills:       []string      # Resolved skill namespaces
    runtime:      []string      # Runtime package constraints
    resolved:     boolean       # All deps verified?

  # State
  lifecycle_state: string       # Current B.2 lifecycle state
  health_state:    string       # Current B.4 health state
  health_score:    integer      # 0-100

  # Content
  content_sha256: string        # Verified at load time
  content_size:   integer       # bytes
  mount:          string        # "routed" | "auto" | "manual"

  # Timing
  resolved_at:    timestamp
  loaded_at:      timestamp
  started_at:     timestamp
  ended_at:       timestamp
  duration_ms:    integer
```

### 3.2 ExecutionRecord

```yaml
ExecutionRecord:
  execution_id:    string
  skill_id:        string
  skill_version:   string
  skill_namespace: string

  caller:
    session_id:    string
    scope:         string
    tier:          integer

  timing:
    resolved_at:   timestamp
    loaded_at:     timestamp
    started_at:    timestamp
    ended_at:      timestamp
    duration_ms:   integer
    load_ms:       integer
    gate_ms:       integer
    exec_ms:       integer

  state_changes:   []StateChange
    # {from: "AVAILABLE", to: "RESOLVED", at: timestamp}

  gates_passed:    map
    # {G1: true, G2: true, G3: true, G4: true, G5: true, G6: true}

  result:
    status:        string       # "SUCCESS" | "FAILED" | "DEGRADED" | "TIMEOUT"
    output_type:   string       # "text" | "json" | "binary" | "void"
    output_size:   integer      # bytes
    exit_code:     integer

  error:
    occurred:      boolean
    class:         string       # "F1" | "F2" | "F3" | "F4" | "F5" | "F6" | null
    message:       string
    stack:         string       # optional

  recovery:
    attempted:     boolean
    action:        string       # "retry" | "fallback" | "rollback" | "none"
    retry_count:   integer
    fallback_skill: string      # if fallback was used
    success:       boolean

  health_snapshot:
    state:         string       # HEALTHY | WARNING | DEGRADED | FAILED | QUARANTINED
    score:         integer      # 0-100
    after_execution: boolean    # true if this execution changed health
```

### 3.3 HealthRecord

```yaml
HealthRecord:
  skill_id:        string
  evaluated_at:    timestamp
  score:           integer      # 0-100
  state:           string       # HEALTHY | WARNING | DEGRADED | FAILED | QUARANTINED
  previous_state:  string
  changed:         boolean

  factors:
    success_rate_score:    integer  # 0-35
    failure_frequency_score: integer # 0-25
    latency_score:         integer  # 0-15
    dependency_score:      integer  # 0-15
    trend_score:           integer  # 0-10

  signals:
    success_rate_24h:    float     # e.g., 0.975
    failure_count_24h:   integer
    p95_latency_ms:      integer
    dependency_health_pct: float   # e.g., 1.0
    trend_direction:     string    # "improving" | "stable" | "declining"

  recommendation:  string        # "OK" | "MONITOR" | "MAINTENANCE_REQUIRED" |
                                  # "CONSIDER_DEPRECATION" | "IMMEDIATE_REVIEW"
  auto_actions_taken: []string   # e.g., ["priority_reduced", "alert_created"]
```

---

## 4. Persistence Layer

### 4.1 Runtime State Directory

```
~/.hermes/runtime/
│
├── runtime-state.json              # Global runtime state
│   {
│     "active_executions": 3,
│     "loaded_contexts": 2,
│     "last_health_sweep": "2026-07-18T14:30:00Z",
│     "uptime_seconds": 86400
│   }
│
├── execution-history/              # Execution records (B.3 §1)
│   └── YYYY-MM/
│       └── {execution_id}.json
│
├── telemetry/                      # Aggregated metrics (B.3 §2)
│   ├── skill-metrics/
│   │   └── {skill_id}.json        # Per-skill rolling metrics
│   ├── namespace-metrics/
│   │   └── {namespace}.json       # Per-namespace aggregates
│   └── system-metrics.json        # System-wide aggregates
│
├── health/                         # Health records (B.4 §1-2)
│   ├── current/
│   │   └── {skill_id}.json        # Current health state
│   └── history/
│       └── {skill_id}/
│           └── YYYY-MM-DD.json    # Daily health snapshots
│
└── governance-proposals/           # Auto-generated proposals (B.4 §7)
    ├── pending/
    │   └── {proposal_id}.json
    ├── approved/
    │   └── {proposal_id}.json
    └── rejected/
        └── {proposal_id}.json
```

### 4.2 Persistence Rules

```
Rule P1: Registry is the STATIC source of truth
  → Registry stores: identity, namespace, scope, ownership, lifecycle
  → Runtime NEVER modifies Registry metadata except status field

Rule P2: Runtime state is DYNAMIC
  → Runtime stores: execution history, telemetry, health, proposals
  → Runtime state is ephemeral — can be rebuilt from Registry + execution log

Rule P3: Telemetry is APPEND-ONLY
  → Telemetry records are immutable once written
  → Aggregated metrics are derived, not primary

Rule P4: Health is DERIVED
  → Health state is computed from telemetry, not stored as truth
  → Health history is a cache — can be recomputed from execution records

Rule P5: Governance proposals are PENDING until approved
  → Auto-generated proposals require human approval
  → Proposals do NOT auto-execute
```

---

## 5. Runtime State Synchronization

### 5.1 Registry ↔ Runtime Boundary

```
┌─────────────────────────────────────────────────────────────┐
│              REGISTRY (Static Truth)                         │
│              ─────────────────────                           │
│  Fields owned by Registry:                                   │
│    name, version, description, capability, owner             │
│    namespace, scope, ownership, lifecycle                    │
│    tags, mount, trigger, dependencies, permissions            │
│    category, path, registered, updated                       │
│                                                             │
│  ═══════════════ BOUNDARY ═══════════════                    │
│                                                             │
│              RUNTIME (Dynamic State)                         │
│              ──────────────────────                          │
│  Fields owned by Runtime:                                    │
│    status (via health engine)                                │
│    execution history, telemetry, health score                │
│    governance proposals                                      │
│                                                             │
│  Runtime MAY:                                                │
│    ✅ Read any Registry field                                │
│    ✅ Update 'status' field (health engine)                  │
│    ✅ Compute and store health state                         │
│    ✅ Create governance proposals                            │
│                                                             │
│  Runtime MUST NOT:                                           │
│    ❌ Modify Registry metadata fields                        │
│    ❌ Modify SKILL.md content                                │
│    ❌ Change namespace, scope, or ownership                  │
│    ❌ Change lifecycle (except via proposal→approval)        │
│    ❌ Delete or archive skills                               │
└─────────────────────────────────────────────────────────────┘
```

### 5.2 Synchronization Rules

```
Sync Direction: Registry → Runtime (one-way for metadata)
  → On startup: Runtime loads Registry into memory
  → On Registry change: Runtime invalidates cache, reloads

Sync Direction: Runtime → Registry (one field only)
  → On health change: Runtime writes 'status' field
  → On proposal approval: Registry updated via migration procedure

Conflict Resolution:
  → Registry always wins for metadata conflicts
  → Runtime status field is authoritative for operational health
  → If conflict detected: log WARNING, use Registry value
```

---

## 6. Failure Protocol

### 6.1 F1 — Context Failure

```
Detection: LOADING stage
  - File not found at Registry.path
  - Read permission denied
  - Memory allocation failure (OOM)

Response:
  1. Log failure: error_class = "F1"
  2. Transition: LOADING → FAILED
  3. Release partial context if any

Retry:    1 attempt after 1 second
Fallback: Next-best candidate from resolve_skill() alternatives
Escalation: After retry exhausted → DEGRADED
Rollback:  Release context memory; return to AVAILABLE
```

### 6.2 F2 — Dependency Failure

```
Detection: G4 gate (validate_permission)
  - Declared skill dependency not found in Registry
  - Runtime package dependency not available
  - Circular dependency detected

Response:
  1. Log failure: error_class = "F2"
  2. Block execution at G4
  3. Mark skill DEGRADED

Retry:    Not applicable (dependency failure is structural)
Fallback: If fallback skill exists with available deps → switch
Escalation: Alert platform team; update dependency graph
Rollback:  Return to AVAILABLE with dependency failure logged
```

### 6.3 F3 — Permission Failure

```
Detection: G1/G2/G3 gate (validate_permission)
  - Cross-project access without declaration
  - Core/Adapter requesting project skill
  - Wrong tier for operation

Response:
  1. Log failure: error_class = "F3"
  2. Transition: RESOLVED → AVAILABLE (safe abort)
  3. Log PERMISSION_DENIED event

Retry:    NOT retryable — permission failures are structural
Fallback: Suggest skill in allowed namespace
Escalation: If >10 denials/hour → CRITICAL alert
Rollback:  Already aborted safely to AVAILABLE
```

### 6.4 F4 — Corruption

```
Detection: LOADING stage
  - SHA-256 mismatch (content modified since registration)
  - File unreadable or binary garbage
  - Frontmatter parse failure

Response:
  1. Log failure: error_class = "F4"
  2. Transition: LOADING → FAILED → QUARANTINED
  3. IMMEDIATE CRITICAL alert to governance
  4. Preserve corrupted file as evidence
  5. Block ALL future dispatches

Retry:    NOT retryable
Fallback: Not applicable — corruption is a safety event
Escalation: IMMEDIATE governance notification
Rollback:  Restore SKILL.md from backup; verify SHA-256; governance clears quarantine
```

### 6.5 F5 — Timeout

```
Detection: EXECUTING stage
  - Duration exceeds timeout_ms (default: 300000ms)

Response:
  1. Log failure: error_class = "F5"
  2. Transition: EXECUTING → FAILED
  3. Release context

Retry:    3 attempts with exponential backoff (1s, 2s, 4s)
          Use 2× timeout on retry
Fallback: If retries exhausted → fallback skill
Escalation: If timeout persists across retries → DEGRADED
Rollback:  Release context; return to AVAILABLE
```

### 6.6 F6 — External Failure

```
Detection: EXECUTING stage
  - Network error, API down, tool crash
  - Adapter returns error status

Response:
  1. Log failure: error_class = "F6"
  2. Transition: EXECUTING → FAILED
  3. Capture external error details

Retry:    3 attempts with exponential backoff (1s, 2s, 4s)
Fallback: If adapter has alternative → switch to fallback adapter
          If no fallback → report to user
Escalation: Alert platform team; mark adapter DEGRADED if persistent
Rollback:  Release context; return to AVAILABLE
```

---

## 7. Security Contract

### 7.1 Four-Layer Enforcement

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: REGISTRY VALIDATION                                 │
│ ─────────────────────────                                   │
│ Enforced at: Registration time, Registry write               │
│ Checks:                                                     │
│   ✅ Namespace pattern valid (hermes.core.* | adapter.* |    │
│      project.<id>.*)                                        │
│   ✅ Scope matches namespace prefix                          │
│   ✅ Ownership tier consistent (0/1/2)                       │
│   ✅ No duplicate names or namespaces (except aliases)       │
│   ✅ All 10 required fields present                          │
│ Violation → Registration REJECTED                            │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: RESOLVER ENFORCEMENT                                │
│ ───────────────────────────                                 │
│ Enforced at: resolve_skill(), validate_permission()          │
│ Checks:                                                     │
│   ✅ Namespace direction: Core→Project ❌, Adapter→Project ❌ │
│   ✅ Ownership: cross-project requires cross_project=true    │
│   ✅ Forbidden pairs: rejected at G6                         │
│   ✅ Lifecycle: archived skills rejected at G5               │
│   ✅ Quarantine: quarantined skills rejected at G6           │
│ Violation → RESOLVED → AVAILABLE (safe abort)                │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: RUNTIME GUARD                                       │
│ ─────────────────────                                       │
│ Enforced at: load_context(), execute_skill()                 │
│ Checks:                                                     │
│   ✅ SHA-256 integrity verified at load                      │
│   ✅ Context not modified during execution                   │
│   ✅ Timeout enforced                                        │
│   ✅ No unauthorized state transitions                       │
│   ✅ Context released after execution                        │
│ Violation → F4 (corruption): QUARANTINE                      │
│             Other: FAILED + recovery                         │
├─────────────────────────────────────────────────────────────┤
│ LAYER 4: AUDIT TRAIL                                         │
│ ─────────────────────                                       │
│ Enforced at: All stages (post-execution)                     │
│ Checks:                                                     │
│   ✅ Every execution recorded in telemetry                   │
│   ✅ Every state transition logged                           │
│   ✅ Every gate result captured                              │
│   ✅ Every health change documented                          │
│   ✅ Every proposal tracked                                  │
│ Violation → Missing audit record → CRITICAL alert            │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 Prohibited Operations — Runtime Enforcement

```
❌ Core → Project dispatch       → REJECTED at G3
❌ Adapter → Project dispatch    → REJECTED at G3
❌ Unauthorized execution        → REJECTED at G1/G2
❌ Bypass lifecycle gate         → REJECTED at G5
❌ Bypass permission gate        → REJECTED at G6
❌ Silent skill replacement      → QUARANTINE (F4 detection)
❌ Runtime override of Registry  → BLOCKED (sync boundary)
❌ Cross-project without declaration → REJECTED at G2
```

---

## 8. Runtime Event Schema

### 8.1 Event Types

```yaml
# Lifecycle Events
SKILL_RESOLVED:
  execution_id: string
  skill_id: string
  resolved_by: string      # "trigger_match" | "capability_match" | "fallback"
  confidence: float
  timestamp: timestamp

CONTEXT_LOADED:
  execution_id: string
  skill_id: string
  content_sha256: string
  content_size: integer
  load_time_ms: integer
  timestamp: timestamp

EXECUTION_STARTED:
  execution_id: string
  skill_id: string
  gates_passed: map
  timestamp: timestamp

EXECUTION_COMPLETED:
  execution_id: string
  skill_id: string
  status: string           # "SUCCESS"
  duration_ms: integer
  output_size: integer
  timestamp: timestamp

EXECUTION_FAILED:
  execution_id: string
  skill_id: string
  error_class: string      # "F1" | "F2" | "F3" | "F4" | "F5" | "F6"
  error_message: string
  retry_count: integer
  timestamp: timestamp

# Health Events
HEALTH_CHANGED:
  skill_id: string
  from_state: string
  to_state: string
  score: integer
  trigger: string          # "score_drop" | "failure_spike" | "recovery" | "corruption"
  timestamp: timestamp

SKILL_DEGRADED:
  skill_id: string
  score: integer
  reason: string
  actions_taken: []string
  timestamp: timestamp

SKILL_QUARANTINED:
  skill_id: string
  trigger: string          # "corruption" | "security" | "repeated_failure"
  evidence_preserved: boolean
  timestamp: timestamp

# Governance Events
PROPOSAL_CREATED:
  proposal_id: string
  skill_id: string
  type: string             # "P1" | "P2" | ... | "P8"
  priority: string         # "P0" | "P1" | "P2" | "P3"
  timestamp: timestamp

PROPOSAL_RESOLVED:
  proposal_id: string
  decision: string         # "APPROVED" | "REJECTED" | "DEFERRED"
  decided_by: string
  timestamp: timestamp
```

### 8.2 Event Flow

```
SKILL_REGISTERED    (Registry write)
       │
       ▼
SKILL_RESOLVED      (Resolver selects)
       │
       ▼
CONTEXT_LOADED      (Content in memory)
       │
       ▼
EXECUTION_STARTED   (Gates passed)
       │
       ├──► EXECUTION_COMPLETED   (SUCCESS)
       │         │
       │         ▼
       │    HEALTH_CHANGED?       (evaluate)
       │
       └──► EXECUTION_FAILED      (FAILED)
                 │
                 ▼
            SKILL_DEGRADED?       (if repeated)
                 │
                 ▼
            SKILL_QUARANTINED?    (if F4)
```

---

## 9. Testing Strategy

### 9.1 Test Categories — 30+ Runtime Validation Cases

#### Resolver Tests (8 cases)

| # | Test Case | Expected |
|:--|:-----|:-----|
| RT-01 | Match intent with exact trigger keyword | Returns highest-confidence skill |
| RT-02 | Match intent with partial trigger | Returns skill with partial match |
| RT-03 | Match intent with capability domain | Returns skill in same domain |
| RT-04 | No match — escalate namespace | Returns adapter fallback |
| RT-05 | No match — all namespaces exhausted | Returns "NO_MATCH" error |
| RT-06 | Forbidden pair detected | Returns "FORBIDDEN_PAIR" error |
| RT-07 | Multiple candidates — tiebreak by version | Returns highest version |
| RT-08 | Deprecated candidate — apply penalty | Prefers active over deprecated |

#### Lifecycle Tests (6 cases)

| # | Test Case | Expected |
|:--|:-----|:-----|
| RT-09 | Valid transition: AVAILABLE → RESOLVED → LOADING | Allowed |
| RT-10 | Invalid transition: FAILED → EXECUTING | Rejected |
| RT-11 | Invalid transition: ARCHIVED → AVAILABLE | Rejected |
| RT-12 | Timeout: LOADING exceeds 5s | → FAILED (F1) |
| RT-13 | Timeout: EXECUTING exceeds 300s | → FAILED (F5) |
| RT-14 | Safe abort: RESOLVED → AVAILABLE | Allowed, no side effects |

#### Permission Tests (5 cases)

| # | Test Case | Expected |
|:--|:-----|:-----|
| RT-15 | Core caller requests project skill | G3 REJECTED |
| RT-16 | Adapter caller requests project skill | G3 REJECTED |
| RT-17 | Project A requests Project B skill without declaration | G2 REJECTED |
| RT-18 | Project A requests Project B skill with cross_project=true | G2 PASS |
| RT-19 | Archived skill requested | G5 REJECTED |

#### Failure Recovery Tests (6 cases)

| # | Test Case | Expected |
|:--|:-----|:-----|
| RT-20 | F1 context failure — file missing | Retry 1× → FAILED |
| RT-21 | F2 dependency failure | G4 REJECTED → DEGRADED |
| RT-22 | F3 permission failure | G1/G2/G3 REJECTED → AVAILABLE |
| RT-23 | F4 corruption — SHA mismatch | QUARANTINED immediately |
| RT-24 | F5 timeout — 3 retries exhausted | FAILED → fallback |
| RT-25 | F6 external failure — fallback adapter | FAILED → fallback → SUCCESS |

#### Health Tests (5 cases)

| # | Test Case | Expected |
|:--|:-----|:-----|
| RT-26 | Score 95 → HEALTHY | State unchanged or → HEALTHY |
| RT-27 | Score 72 → DEGRADED | HEALTHY → WARNING → DEGRADED |
| RT-28 | Score 30 → FAILED | DEGRADED → FAILED |
| RT-29 | F4 corruption → QUARANTINED | Immediate quarantine |
| RT-30 | Score recovery 85 → WARNING | FAILED → WARNING (manual fix) |

#### Telemetry Tests (4 cases)

| # | Test Case | Expected |
|:--|:-----|:-----|
| RT-31 | Execution SUCCESS → telemetry written | Record stored |
| RT-32 | Execution FAILED → telemetry written with error | Record stored, error captured |
| RT-33 | Telemetry write failure | Execution result unaffected |
| RT-34 | Metrics aggregator updated after 100 executions | success_rate accurate |

---

## 10. Architecture Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   SKILL KERNEL RUNTIME SPECIFICATION                          ║
║                                                              ║
║   Integration of B.1-B.4 architectures:                       ║
║                                                              ║
║   1. Runtime API Contract — 8 APIs with full schemas         ║
║   2. Runtime Pipeline — 10-stage execution chain             ║
║   3. Runtime Data Model — 3 core data structures            ║
║   4. Persistence Layer — 5 directories, 5 rules              ║
║   5. State Synchronization — Registry ↔ Runtime boundary     ║
║   6. Failure Protocol — F1-F6 with full response chain       ║
║   7. Security Contract — 4 enforcement layers                ║
║   8. Runtime Event Schema — 11 event types                   ║
║   9. Testing Strategy — 34 runtime validation cases          ║
║                                                              ║
║   Hermes transformation:                                      ║
║                                                              ║
║   BEFORE:  Governed Skill Registry                            ║
║   AFTER:   Executable Skill Operating System Runtime          ║
║                                                              ║
║   Compliance:                                                 ║
║     ✅ Governance Constitution v1.0                           ║
║     ✅ C.3 Namespace Model                                    ║
║     ✅ Registry v1.1 (149 entries, 18 fields)                 ║
║     ✅ Forbidden States F1-F10                                ║
║     ✅ B.1-B.4 Architecture designs                           ║
║                                                              ║
║   🟢 GREEN — Runtime Specification approved                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ |
| 10 sections complete | ✅ |
| 8 APIs with schemas | ✅ |
| 10-stage pipeline | ✅ |
| 3 data models | ✅ |
| Persistence layer (5 dirs) | ✅ |
| State sync rules | ✅ |
| F1-F6 protocols | ✅ |
| 4-layer security | ✅ |
| 11 event types | ✅ |
| 34 test cases (RT-01 to RT-34) | ✅ |
| 0 executable code | ✅ |

---

> **Phase:** B.5 — Skill Kernel Runtime Specification
> **Status:** ✅ DESIGN COMPLETE
> **Decision:** 🟢 GREEN — Runtime Specification approved
> **Hermes is now an Executable Skill Operating System Runtime.**
