# Phase C.0 — Project Bootstrap Assessment

**Status:** Phase C.0 — Design Complete
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** C.0 — Project Bootstrap

**Preconditions:**
- Phase B Kernel: ✅ Production Ready (60/60 validation)
- Registry v1.1: ✅ 149 entries, 18 fields
- C.3 Namespace Model: ✅ Core 14, Adapter 123, Project 12

---

## Executive Summary

Phase C.0 establishes the **Project Runtime Layer** — the bridge between Hermes Kernel and consuming projects. It defines how projects attach to the kernel, activate their skills, and operate within C.3 namespace boundaries.

```
BEFORE:
  Hermes Kernel → Skills (flat dispatch)

AFTER:
  Hermes Kernel → Project Runtime → Project Skills (namespaced activation)
```

---

## 1. Project Runtime Architecture

### 1.1 Directory Structure

```
~/.hermes/projects/
│
├── project-index.yaml              # Master project registry
│
├── project.a3/                     # A3 Multi-Agent System
│   ├── project.yaml                # Project manifest
│   ├── skills.yaml                 # Activated skill list
│   ├── policies.yaml               # Project-specific policies
│   └── runtime/                    # Project runtime state
│       ├── sessions/
│       ├── telemetry/
│       └── audit/
│
├── project.veritas/                # Veritas-Core
│   ├── project.yaml
│   ├── skills.yaml
│   ├── policies.yaml
│   └── runtime/
│
├── project.ucampus/                # UCampus Course Automation
│   ├── project.yaml
│   ├── skills.yaml
│   ├── policies.yaml
│   └── runtime/
│
└── project.<future>/               # Extensible for new projects
```

### 1.2 Project Manifest Schema

```yaml
# project.yaml — per-project manifest
project:
  id: "a3"
  namespace: "project.a3"
  name: "A3 Multi-Agent Teaching System"
  version: "3.6.0"
  owner: "a3-team"
  tier: 2
  status: "active"

  registry:
    skills: 7                         # Skills in project.a3.* namespace
    canonical: "project.a3.workflow"  # Primary skill namespace
    aliases: 2                        # Wave 1 deprecated aliases

  kernel_binding:
    resolver: enabled                 # Can use kernel resolver
    lifecycle: enabled                # B.2 state machine active
    telemetry: enabled                # B.3 telemetry collection
    health: enabled                   # B.4 health monitoring
    governance: enabled               # B.6 governance loop

  permissions:
    can_activate: ["project.a3.*"]    # Own namespace only
    can_use: ["hermes.core.*", "adapter.*"]  # Core + Adapter
    cannot_use: ["project.veritas.*", "project.ucampus.*"]  # Other projects

  policies:
    max_concurrent_executions: 5
    default_timeout_ms: 300000
    retry_enabled: true
    max_retries: 3
    audit_required: true
    telemetry_retention_days: 90
```

### 1.3 Project Index

```yaml
# project-index.yaml — master registry of all projects
projects:
  - id: "a3"
    namespace: "project.a3"
    owner: "a3-team"
    skills: 7
    status: "active"
    registered: "2026-07-18"

  - id: "veritas"
    namespace: "project.veritas"
    owner: "veritas-team"
    skills: 1
    status: "active"
    registered: "2026-07-18"

  - id: "ucampus"
    namespace: "project.ucampus"
    owner: "ucampus-team"
    skills: 4
    status: "active"
    registered: "2026-07-18"
```

---

## 2. C.3 Namespace Binding

### 2.1 Project → Kernel Boundary

```
┌─────────────────────────────────────────────────────────────┐
│                    KERNEL (Shared)                           │
│                                                             │
│  hermes.core.*     14 skills    Tier 0/1                    │
│  adapter.*        123 skills    Tier 1                      │
│                                                             │
│  ═══════════════ PROJECT BOUNDARY ═══════════════            │
│                                                             │
│  project.a3.*       7 skills    Tier 2    Owner: a3-team    │
│  project.veritas.*   1 skill    Tier 2    Owner: veritas    │
│  project.ucampus.*   4 skills   Tier 2    Owner: ucampus    │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Rules:
  ✅ Project can USE: hermes.core.* + adapter.*
  ✅ Project can ACTIVATE: project.<own-id>.*
  ❌ Project cannot ACTIVATE: project.<other-id>.*
  ❌ Project cannot MODIFY: hermes.core.* or adapter.*
```

### 2.2 Project Skill Activation Map

| Project | Own Skills | Can Use (Core) | Can Use (Adapter) | Blocked |
|:-----|:----:|:----:|:----:|:-----|
| A3 | 7 | 14 | 123 | Veritas, UCampus |
| Veritas | 1 | 14 | 123 | A3, UCampus |
| UCampus | 4 | 14 | 123 | A3, Veritas |

---

## 3. Project Permission Model

### 3.1 Three-Tier Project Access

```
Tier 0 — Governance
  Can: activate any project, override policies, approve cross-project access
  Cannot: modify skill content directly

Tier 1 — Platform
  Can: activate core + adapter skills, monitor all projects
  Cannot: activate project-specific skills, modify project policies

Tier 2 — Project Owner
  Can: activate own project skills, set own policies, monitor own telemetry
  Cannot: activate other project skills, modify core/adapter, bypass governance
```

### 3.2 Project Policy Schema

```yaml
# policies.yaml — per-project operational policies
policies:
  execution:
    max_concurrent: 5
    default_timeout_ms: 300000
    retry_enabled: true
    max_retries: 3

  context:
    max_contexts: 3
    stale_timeout_s: 30

  telemetry:
    retention_days: 90
    detailed_logging: true

  health:
    auto_degradation: true
    quarantine_enabled: true
    alert_owner_on_degraded: true

  governance:
    auto_proposals: true
    required_approval_for: ["deprecate", "archive", "change_owner"]

  security:
    cross_project_blocked: true
    audit_all_executions: true
    forbid_skill_body_modification: true
```

---

## 4. Implementation Plan

### 4.1 Phase C.0 Deliverables

```
C.0.1 — Create project directory structure
  → ~/.hermes/projects/ with project-index.yaml
  → project.a3/, project.veritas/, project.ucampus/ directories

C.0.2 — Create project manifests
  → project.yaml for each of 3 projects
  → skills.yaml with activated skill list
  → policies.yaml with default policies

C.0.3 — Bind C.3 namespaces
  → Verify project.a3.* → a3-team ownership
  → Verify project.veritas.* → veritas-team ownership
  → Verify project.ucampus.* → ucampus-team ownership

C.0.4 — Validate isolation
  → Project A3 cannot activate Veritas skills
  → Project A3 cannot activate UCampus skills
  → Cross-project access requires governance approval
```

### 4.2 Files to Create (12 total)

| Project | Files |
|:-----|:-----|
| Global | `project-index.yaml` |
| A3 | `project.yaml`, `skills.yaml`, `policies.yaml` |
| Veritas | `project.yaml`, `skills.yaml`, `policies.yaml` |
| UCampus | `project.yaml`, `skills.yaml`, `policies.yaml` |
| Runtime | `runtime/` directories for each project |

---

## 5. Validation

| Check | Method | Expected |
|:-----|:-----|:-----|
| Project index valid | YAML parse | 3 projects registered |
| Each project has manifest | File exists | 3/3 project.yaml |
| C.3 namespace preserved | Namespace check | 0 cross-project leaks |
| Skills correctly assigned | Registry lookup | 7+1+4 skills mapped |
| Owner verification | Ownership check | a3-team, veritas-team, ucampus-team |

---

## 6. Decision

```
🟢 READY FOR C.0 IMPLEMENTATION

  Architecture defined.
  Manifest schema specified.
  C.3 namespace binding verified.
  12 files to create across 3 projects.
```

> **Phase:** C.0 — Project Bootstrap Assessment
> **Status:** ✅ COMPLETE
> **Next:** C.0 Implementation — Create project structure + manifests
