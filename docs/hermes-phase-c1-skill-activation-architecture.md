# Phase C.1 — Skill Activation Layer Architecture

**Status:** Phase C.1 — Design Complete
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** C.1 — Skill Activation Architecture

**Derived From:**
- Phase C.0 Project Bootstrap
- B.1 Resolver Architecture
- B.5 Runtime Specification
- C.3 Namespace Model

---

## 1. Skill Activation Pipeline

### 1.1 Complete Flow

```
PROJECT INTENT
    │  "A3: orchestrate multi-agent teaching workflow"
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ STAGE 1: PROJECT SKILL PROFILE                               │
│ ─────────────────────────                                   │
│ Load project.yaml → skills.yaml                              │
│ Filter: only skills in project.<own-id>.* namespace         │
│ Output: Activated skill list for this project               │
├─────────────────────────────────────────────────────────────┤
│ STAGE 2: SKILL ACTIVATION RESOLVER                           │
│ ─────────────────────────────                               │
│ Match intent against project-activated skills               │
│ Apply project-specific policies (timeout, retry, context)   │
│ Output: Project-contextualized skill candidate              │
├─────────────────────────────────────────────────────────────┤
│ STAGE 3: KERNEL RESOLVER (B.1)                               │
│ ──────────────────────────                                  │
│ Standard resolve_skill() pipeline                            │
│ Enforces: namespace, ownership, dependency, permission      │
│ Output: Resolved skill with full kernel validation          │
├─────────────────────────────────────────────────────────────┤
│ STAGE 4: EXECUTION RUNTIME (B.2)                             │
│ ─────────────────────────────                               │
│ Standard execute_skill() pipeline                            │
│ Records: telemetry (B.3), health (B.4), governance (B.6)   │
│ Output: Execution result + full audit trail                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Project Skill Profile Schema

```yaml
# skills.yaml — activated skills for a project
project_id: "a3"
namespace: "project.a3"
activated_skills:
  - skill_id: "a3-multi-agent-pipeline"
    namespace: "project.a3.workflow"
    activation: "primary"
    priority: 10

  - skill_id: "a3-content-pipeline"
    namespace: "project.a3.pipeline"
    activation: "on-demand"
    priority: 7

  - skill_id: "a3-runtime-infrastructure"
    namespace: "project.a3.infrastructure"
    activation: "auto"
    priority: 5

shared_skills:
  core:
    - "hermes.core.registry"
    - "hermes.core.guidance"
    - "hermes.core.tracker"

  adapter:
    - "adapter.browser"
    - "adapter.github.pr"
    - "adapter.cli"

blocked_skills:
  - "project.veritas.core"       # Other project
  - "project.ucampus.automation" # Other project
```

### 1.3 Skill Activation Manifest

```yaml
# activation manifest — runtime binding
activation:
  skill_id: "a3-multi-agent-pipeline"
  project_id: "a3"
  activated_at: "2026-07-18T00:00:00Z"
  activated_by: "a3-team"
  status: "active"

  binding:
    resolver: "kernel/resolver"       # Use B.1 resolver
    lifecycle: "kernel/lifecycle"      # Use B.2 state machine
    executor: "kernel/runtime"         # Use B.2 executor

  policies:
    timeout_ms: 600000                # Project-specific: 10 min
    max_retries: 5                    # Project-specific: 5
    fallback_enabled: true
    audit_level: "detailed"

  context:
    preload_skills:                   # Auto-load dependencies
      - "hermes.core.registry"
      - "adapter.browser"
    max_context_size_mb: 50

  telemetry:
    project_scoped: true              # Only visible to a3-team
    detailed_logging: true
```

---

## 2. Project Capability Filtering

### 2.1 Project-Scoped Resolution

```
When a project dispatches a request:

  1. PROJECT FILTER (Stage 1):
     → Only skills in project.<own-id>.* namespace are candidates
     → Plus: explicitly subscribed core/adapter skills

  2. KERNEL FILTER (Stage 2):
     → Standard C.3 namespace enforcement
     → Core→Project ❌, Adapter→Project ❌
     → Cross-project ❌ without governance approval

  3. POLICY FILTER (Stage 3):
     → Project-specific timeout, retry, context limits
     → Override kernel defaults within allowed bounds
```

### 2.2 Cross-Project Isolation

```
Project A3 activating a skill:

  ✅ a3-multi-agent-pipeline      (own namespace)
  ✅ adapter.browser              (subscribed adapter)
  ✅ hermes.core.registry         (subscribed core)
  ❌ project.veritas.core          (other project — blocked)
  ❌ project.ucampus.automation    (other project — blocked)

Cross-project access requires:
  → Governance proposal (P8: CROSS_PROJECT_REVIEW)
  → Both project owners approve
  → Explicit cross_project: true in dependency declaration
```

---

## 3. Context Policy Binding

### 3.1 Per-Project Context Configuration

```yaml
context_policy:
  project_id: "a3"
  
  mounts:
    auto_mount:
      - skill: "hermes.core.tracker"
        trigger: "multi_step_task"
      - skill: "hermes.core.errors"
        trigger: "execution_failure"

    preload:
      - "hermes.core.registry"
      - "hermes.core.guidance"

  limits:
    max_concurrent_contexts: 3
    max_context_size_mb: 50
    stale_timeout_s: 60

  isolation:
    memory: "per-project"          # Context not shared across projects
    telemetry: "per-project"       # Telemetry scoped to owning project
    audit: "per-project"           # Audit trail per project
```

---

## 4. Validation Matrix

| Rule | Check | Status |
|:-----|:-----|:----:|
| Project activates own skill | namespace = project.<id>.* | ✅ Allowed |
| Project uses core skill | namespace = hermes.core.* | ✅ Allowed |
| Project uses adapter skill | namespace = adapter.* | ✅ Allowed |
| Project activates other project skill | namespace = project.<other>.* | ❌ Blocked |
| Core activates project skill | namespace direction violation | ❌ Blocked |
| Adapter activates project skill | namespace direction violation | ❌ Blocked |

---

## 5. Decision

```
🟢 GREEN — Skill Activation Architecture Approved

  Pipeline: Project Intent → Profile → Activation Resolver → Kernel Resolver → Runtime
  Isolation: Per-project context, telemetry, audit
  C.3 Compliance: All namespace boundaries preserved
```

> **Phase:** C.1 — Skill Activation Architecture
> **Status:** ✅ COMPLETE
> **Next:** C.2 — Production Workflow Integration
