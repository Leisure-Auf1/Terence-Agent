# Hermes Wave 2 — Namespace Isolation Production Execution Plan

**Status:** Phase A.2.3 — Execution Plan Complete · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T07:35:00Z
**Phase:** A.2.3 — Wave 2 Execution Plan
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Define exact procedure for applying C.3 namespace model to production skill metadata

**Governance Authority:**
- Wave 2 Namespace Isolation Assessment v1.0 (A.2.0)
- Wave 2 Dry Run Specification v1.0 (A.2.1)
- Wave 2 Dry Run Result v1.0 (A.2.2) — 24/24 PASS
- Project Namespace Boundary Review v1.0 (C.3)
- Registry Namespace Schema Amendment v1.0 (C.3.1)
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions (completed):**
- Wave 0: ✅ Registry 15→11, 8 Class C relocated
- Wave 1: ✅ 8→3 canonical + 6 aliases
- Wave 2 Dry Run: ✅ 24/24 PASS, 148 skills classified

**This document is:**
- An execution plan for **metadata assignment** — applying namespace/scope/ownership to skills
- A registry schema transition guide — 14 fields → 17 fields (v1.0 → v1.1)

**This document does NOT:**
- Modify the Registry (yet — deferred to Wave 4)
- Modify SKILL.md files
- Move or delete files
- Execute migration now

---

## 1. Execution Objective

### 1.1 What Wave 2 Is

```
Wave 2 = Namespace Metadata Assignment

  GOAL: Every skill gets formal namespace/scope/ownership metadata
        per the C.3 three-layer model and Registry v1.1 schema.

  This is NOT:
    ❌ Skill renaming — names stay the same
    ❌ Skill deletion — all files preserved
    ❌ Project decoupling — project identity preserved in namespace
    ❌ File movement — 0 files move
```

### 1.2 Before → After

```
BEFORE (Current — post-Wave 0+1):
  - Skills exist with flat names (e.g., "a3-runtime-infrastructure")
  - Namespace is IMPLICIT (derived from name prefix and category)
  - Registry has 14 fields (no namespace/scope/ownership)
  - No formal layer classification

AFTER (Post-Wave 2):
  - Every skill has explicit namespace (e.g., "project.a3.infrastructure")
  - Every skill has explicit scope (core | adapter | project)
  - Every skill has ownership metadata (tier + owner)
  - Registry v1.1 schema ready (17 fields, namespace pending Wave 4)
  - Full C.3 three-layer model applied
```

### 1.3 Scope

```
Skills affected:             148
Files modified (SKILL.md):   0
Files moved:                 0
Files deleted:               0
Registry entries modified:   0 (deferred to Wave 4)
New artifacts created:       namespace-map.json (metadata document)
```

---

## 2. Migration Scope

### 2.1 Layer Coverage

#### Core Layer — hermes.core.* (14 skills)

| # | Skill | Namespace | Owner | Tier |
|:--|:-----|:-----|:-----|:----:|
| 1 | `agent-governance-protocol` | `hermes.core.governance` | `hermes-governance` | 0 |
| 2 | `architecture-constraints` | `hermes.core.constraints` | `hermes-governance` | 0 |
| 3 | `guidance-agent` | `hermes.core.guidance` | `hermes-platform` | 1 |
| 4 | `error-registry` | `hermes.core.errors` | `hermes-governance` | 0 |
| 5 | `skill-manager` | `hermes.core.registry` | `hermes-platform` | 1 |
| 6 | `harness-preflight` | `hermes.core.preflight` | `hermes-platform` | 1 |
| 7 | `task-progress` | `hermes.core.tracker` | `hermes-governance` | 0 |
| 8 | `agent-logger` | `hermes.core.logger` | `hermes-platform` | 1 |
| 9 | `agent-debugger` | `hermes.core.debugger` | `hermes-platform` | 1 |
| 10 | `agent-developer` | `hermes.core.developer` | `hermes-platform` | 1 |
| 11 | `agent-executor` | `hermes.core.executor` | `hermes-platform` | 1 |
| 12 | `skill-ecosystem-audit` | `hermes.core.auditor` | `hermes-governance` | 0 |
| 13 | `webhook-subscriptions` | `hermes.core.webhooks` | `hermes-platform` | 1 |
| 14 | `coding-agent-orchestration` | `hermes.core.coding` | `hermes-platform` | 1 |

#### Adapter Layer — adapter.* (representative subset of 122)

| # | Skill | Namespace | Owner | Tier |
|:--|:-----|:-----|:-----|:----:|
| 1 | `browser-automation` | `adapter.browser` | `hermes-platform` | 1 |
| 2 | `github-pr-workflow` | `adapter.github` | `hermes-platform` | 1 |
| 3 | `cli-anything` | `adapter.cli` | `hermes-platform` | 1 |
| 4 | `himalaya` | `adapter.email` | `hermes-platform` | 1 |
| 5 | `content-review-pipeline` | `adapter.review.pipeline` | `hermes-platform` | 1 |
| 6 | `academic-writing` | `adapter.writing.academic` | `hermes-platform` | 1 |
| 7 | `jupyter-live-kernel` | `adapter.jupyter` | `hermes-platform` | 1 |
| ... | ... | ... | `hermes-platform` | 1 |

#### Project Layer — project.<id>.* (12 skills)

**project.a3 — 7 skills:**

| # | Skill | Namespace | Owner | Tier |
|:--|:-----|:-----|:-----|:----:|
| 1 | `a3-multi-agent-pipeline` | `project.a3.workflow` | `a3-team` | 2 |
| 2 | `a3-agent-team-pipeline` | `project.a3.workflow` (alias) | `a3-team` | 2 |
| 3 | `a3-multi-agent-content-pipeline` | `project.a3.workflow` (alias) | `a3-team` | 2 |
| 4 | `a3-content-pipeline` | `project.a3.pipeline` | `a3-team` | 2 |
| 5 | `a3-runtime-infrastructure` | `project.a3.infrastructure` | `a3-team` | 2 |
| 6 | `acp-coding-agent` | `project.a3.coding` | `a3-team` | 2 |
| 7 | `kanban-codex-lane` | `project.a3.kanban` | `a3-team` | 2 |

**project.veritas — 1 skill:**

| # | Skill | Namespace | Owner | Tier |
|:--|:-----|:-----|:-----|:----:|
| 1 | `veritas-core` | `project.veritas.core` | `veritas-team` | 2 |

**project.ucampus — 4 skills:**

| # | Skill | Namespace | Owner | Tier |
|:--|:-----|:-----|:-----|:----:|
| 1 | `ucampus-auto-complete` | `project.ucampus.automation` | `ucampus-team` | 2 |
| 2 | `u-campus-course-automation` | `project.ucampus.course` | `ucampus-team` | 2 |
| 3 | `chaoxing-homework` | `project.ucampus.chaoxing` | `ucampus-team` | 2 |
| 4 | `lab-report-execution` | `project.ucampus.lab` | `ucampus-team` | 2 |

---

## 3. Execution Strategy

### 3.1 Six-Step Procedure

```
Step 1: Create namespace metadata backup
  → Snapshot current state before any metadata changes

Step 2: Generate namespace-map.json
  → 148 entries with namespace/scope/ownership
  → SHA-256 fingerprinted

Step 3: Validate namespace consistency
  → No collisions, no violations, scope matches namespace prefix
  → Dependency boundaries verified

Step 4: Prepare Registry v1.1 schema mapping
  → Document how 14 fields → 17 fields
  → Namespace fields ready for Wave 4 registration

Step 5: Update alias references
  → Wave 1 aliases namespace-verified
  → Wave 2 namespace isolation documented in alias manifest

Step 6: Post-migration validation
  → 6 gates (G1-G6)
  → Rollback readiness confirmed
```

### 3.2 Files Changed — Summary

| Action | Count | Details |
|:-----|:----:|:-----|
| **Metadata documents created** | 1 | `namespace-map.json` (148 entries, Wave 2 artifact) |
| **Registry entries modified** | 0 | Deferred to Wave 4 |
| **SKILL.md files modified** | 0 | No content changes |
| **Files moved** | 0 | |
| **Files deleted** | 0 | |
| **Alias references updated** | 6 | Wave 1 aliases namespace-verified |

---

## 4. Registry Changes

### 4.1 Schema Transition — v1.0 → v1.1

```
Registry v1.0 (Current — post-Wave 0+1):
  14 fields: name, version, description, capability, owner, lifecycle,
             dependencies, permissions, validation, compatibility,
             status, registered, updated, path

Registry v1.1 (Target — post-Wave 4):
  17 fields: + namespace (string), scope (enum), ownership (object)
```

### 4.2 New Fields

| # | Field | Type | Values | Phase B | Phase A |
|:--|:-----|:-----|:-----|:----:|:----:|
| 15 | `namespace` | `string` | `hermes.core.*`, `adapter.*`, `project.<id>.*` | OPTIONAL | REQUIRED |
| 16 | `scope` | `enum` | `core`, `adapter`, `project` | OPTIONAL | REQUIRED |
| 17 | `ownership` | `object` | `{tier, owner, namespace}` | OPTIONAL | REQUIRED |

### 4.3 Example — Full v1.1 Entry

```json
{
  "name": "a3-runtime-infrastructure",
  "version": "1.0.0",
  "description": "A3 runtime infrastructure patterns",
  "capability": "runtime-infrastructure",
  "owner": "a3-team",
  "namespace": "project.a3.infrastructure",
  "scope": "project",
  "ownership": {
    "tier": 2,
    "owner": "a3-team",
    "namespace": "project.a3"
  },
  "lifecycle": "active",
  "status": "ok",
  "dependencies": {"skills": [], "runtime": []},
  "permissions": {"allow": ["filesystem.read"]},
  "validation": {},
  "compatibility": {"platforms": ["linux"]},
  "registered": "2026-06-01",
  "updated": "2026-07-18",
  "path": "skills/software-development/a3-runtime-infrastructure/"
}
```

### 4.4 Backward Compatibility

```
Old parser (14 fields) reading new registry (17 fields):
  → Ignores unknown fields (namespace, scope, ownership)
  → ✅ Backward compatible — extra fields are additive

New parser (17 fields) reading old registry (14 fields):
  → namespace, scope, ownership = null
  → ✅ Forward compatible — Phase B allows null

Phase B → Phase A transition:
  → Phase B: new fields OPTIONAL (null allowed)
  → Phase A: new fields REQUIRED (reject at registration)
  → Wave 4: Full registration populates all 17 fields
```

---

## 5. Namespace Migration Matrix

### 5.1 Project Skills — Identity Preservation

| Skill | Before (Flat) | After (Namespaced) | Action |
|:-----|:-----|:-----|:-----|
| `a3-runtime-infrastructure` | Generic name, implicit A3 identity | `namespace: project.a3.infrastructure` | Assign metadata |
| `a3-content-pipeline` | Generic name, implicit A3 identity | `namespace: project.a3.pipeline` | Assign metadata |
| `veritas-core` | Generic name, implicit Veritas identity | `namespace: project.veritas.core` | Assign metadata |
| `ucampus-auto-complete` | Generic name, implicit UCampus identity | `namespace: project.ucampus.automation` | Assign metadata |
| `chaoxing-homework` | Generic name, implicit UCampus identity | `namespace: project.ucampus.chaoxing` | Assign metadata |
| `lab-report-execution` | Generic name, implicit UCampus identity | `namespace: project.ucampus.lab` | Assign metadata |

### 5.2 Core Skills — Explicit Framework Ownership

| Skill | Before | After | Action |
|:-----|:-----|:-----|:-----|
| `agent-governance-protocol` | Implicit governance | `namespace: hermes.core.governance, tier: 0` | Assign metadata |
| `architecture-constraints` | Implicit governance | `namespace: hermes.core.constraints, tier: 0` | Assign metadata |
| `skill-manager` | Implicit framework | `namespace: hermes.core.registry, tier: 1` | Assign metadata |
| ... | ... | ... | Assign metadata |

### 5.3 Adapter Skills — Neutrality Formalized

| Skill | Before | After | Action |
|:-----|:-----|:-----|:-----|
| `browser-automation` | Implicit adapter | `namespace: adapter.browser` | Assign metadata |
| `github-pr-workflow` | Implicit adapter | `namespace: adapter.github` | Assign metadata |
| `cli-anything` | Implicit adapter | `namespace: adapter.cli` | Assign metadata |
| ... | ... | ... | Assign metadata |

---

## 6. Dependency Validation

### 6.1 Allowed Directions — Confirmed

```
✅ Core → Core:
   hermes.core.governance → hermes.core.constraints

✅ Adapter → Core:
   adapter.browser → hermes.core.registry

✅ Project → Core:
   project.a3.workflow → hermes.core.registry

✅ Project → Adapter:
   project.ucampus.automation → adapter.browser

✅ Project → Project (same namespace):
   project.a3.workflow → project.a3.infrastructure
```

### 6.2 Blocked Directions — Enforced

```
❌ Core → Project:
   Blocked by namespace rule R1. Registry must reject `hermes.core.* → project.*`

❌ Core → Adapter:
   Blocked by namespace rule R1. Core must not depend on adapter.

❌ Adapter → Project:
   Blocked by namespace rule R2. Adapter must be project-neutral.
```

### 6.3 Cross-Project Dependency (Conditional)

```
⚠️ Project_A → Project_B:

   Requires:
     cross_project: true
     justification: "explanation of why cross-project dependency is needed"

   Without declaration:
     → Audit CLI flags as WARNING

   With declaration:
     → Accepted; triggers review gate
```

---

## 7. Rollback Plan

### 7.1 Rollback Triggers

| # | Condition | Severity |
|:--|:-----|:----:|
| R1 | Namespace collision — two skills assigned same namespace | **CRITICAL** |
| R2 | Ownership mismatch — core skill assigned project ownership | **CRITICAL** |
| R3 | Dependency violation — core→project or adapter→project edge | **CRITICAL** |
| R4 | Parser failure — namespace-map.json invalid JSON | **CRITICAL** |
| R5 | Scope mismatch — namespace prefix doesn't match scope | **CRITICAL** |
| R6 | Registry corruption — skill-registry.json parse error | **CRITICAL** |

### 7.2 Rollback Procedures

```
Registry Rollback:
  cp /tmp/hermes-wave1-snapshots/registry.pre-merge.json \
     ~/.hermes/skills/devops/skill-manager/references/skill-registry.json

Metadata Rollback:
  rm namespace-map.json (Wave 2 artifact is additive — delete to rollback)

Namespace Map Rollback:
  Delete /tmp/hermes-wave2-dryrun/namespace-map.json
  Regenerate from scratch → verify identical output

Full Rollback:
  1. Restore registry from Wave 1 backup
  2. Delete Wave 2 namespace-map.json
  3. Verify: 0 namespace metadata remains
  4. Confirm: Wave 0+1 state restored
```

### 7.3 Rollback Readiness

```
✅ Registry backup: /tmp/hermes-wave1-snapshots/registry.pre-merge.json
✅ Wave 0 snapshot: /tmp/hermes-wave0-snapshots/registry.baseline.json
✅ Dry run verified: namespace-map.json regeneratable (0-diff)
✅ Skills unchanged: all 148 SKILL.md files SHA-256 match
```

---

## 8. Post-Migration Gates

### 8.1 Six-Gate Validation

| Gate | Name | Check | Method |
|:----:|:-----|:-----|:-----|
| **G1** | Namespace Integrity | All 148 skills have valid namespace | Validate `^((hermes\\.core)\|(adapter)\|(project\\.[a-z0-9-]+))\\.[a-z0-9-]+(\\.[a-z0-9-]+)*$` |
| **G2** | Ownership Integrity | Ownership tier matches scope | Core→{0,1}, Adapter→1, Project→2 |
| **G3** | Dependency Boundary | No core→project or adapter→project edges | Dependency graph scan |
| **G4** | Registry Schema | 17 fields defined, namespace/scope/ownership present | Schema validation |
| **G5** | Runtime Compatibility | Old parser ignores new fields; new parser tolerates null | Compatibility test |
| **G6** | Rollback Verification | Full rollback restores Wave 0+1 state | Restore → verify 0-diff |

### 8.2 Gate Pass/Fail

```
All 6 gates must PASS before Wave 2 is complete:
  [ ] G1 Namespace    — (all 148 valid)
  [ ] G2 Ownership    — (tier matches scope)
  [ ] G3 Dependency   — (0 prohibited edges)
  [ ] G4 Schema       — (17 fields defined)
  [ ] G5 Runtime      — (backward compatible)
  [ ] G6 Rollback     — (restore 0-diff)
```

---

## 9. Human Approval Gate

### 9.1 Pre-Execution Approval

```
☐ Governance Reviewer confirms:

  ☐ Namespace migration scope: 148 skills, 0 file moves, 0 deletions
  ☐ C.3 model applied: Core (14), Adapter (122), Project (12)
  ☐ Registry v1.1 schema: 17 fields (14 existing + namespace/scope/ownership)
  ☐ Backward compatibility: old parser ignores new fields
  ☐ Project identity preserved:
      ☐ a3-runtime-infrastructure → project.a3.infrastructure (NOT genericized)
      ☐ veritas-core → project.veritas.core (NOT genericized)
      ☐ ucampus-auto-complete → project.ucampus.automation
  ☐ Core neutrality: 0 project dependencies in hermes.core.*
  ☐ Adapter neutrality: 0 project identifiers in adapter.*
  ☐ Rollback plan verified: 3 recovery paths + Wave 0/1 backups
```

### 9.2 Execution Authorization

```
☐ Governance Reviewer signature:

    "I authorize Wave 2 namespace metadata assignment per this plan.
     Migration Operator may:
       - Generate namespace-map.json (148 entries)
       - Document Registry v1.1 schema mapping

     Migration Operator may NOT:
       - Modify any SKILL.md file
       - Modify the Registry (deferred to Wave 4)
       - Move or delete any file

     Validator shall verify per §8 (6 gates).
     Any critical trigger (§7.1) requires immediate rollback."

  Signature: ________________________    Date: ______________
```

---

## 10. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   WAVE 2 — NAMESPACE ISOLATION EXECUTION PLAN                 ║
║                                                              ║
║   Skills:          148                                        ║
║     Core:          14   (hermes.core.*)                       ║
║     Adapter:       122  (adapter.*)                           ║
║     Project:       12   (project.<id>.*)                      ║
║                                                              ║
║   Files modified:  0                                          ║
║   Files moved:     0                                          ║
║   Files deleted:   0                                          ║
║   Registry changes: 0 (deferred to Wave 4)                    ║
║                                                              ║
║   Artifact:        namespace-map.json (148 entries)           ║
║   Schema:          v1.0 (14 fields) → v1.1 (17 fields) map   ║
║                                                              ║
║   C.3 compliance:                                             ║
║     ✅ Project identity preserved                              ║
║     ✅ Core neutrality enforced                                ║
║     ✅ Adapter neutrality enforced                             ║
║     ✅ Dependency boundaries defined                           ║
║                                                              ║
║   Dry run:         24/24 PASS                                 ║
║   Rollback:        3 recovery paths + Wave 0/1 backups        ║
║                                                              ║
║   🟢 READY FOR HUMAN APPROVAL                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-wave2-execution-plan.md` |
| 10 chapters complete | ✅ §1-10 |
| 148 skills in scope | ✅ Core=14, Adapter=122, Project=12 |
| 6 execution steps | ✅ §3 |
| Registry v1.0→v1.1 schema | ✅ §4 |
| Namespace migration matrix | ✅ §5 |
| 6 dependency rules | ✅ §6 (allowed + blocked + conditional) |
| Rollback plan (3 paths) | ✅ §7 |
| 6 post-migration gates | ✅ §8 |
| Human approval gate | ✅ §9 |
| 0 executable code | ✅ |
| Registry unchanged | ✅ 11 entries |
| Skills unchanged | ✅ 148 SKILL.md |
| No PII | ✅ |
| Git diff | ✅ Only this new file |

---

> **Phase:** A.2.3 — Wave 2 Execution Plan
> **Status:** ✅ COMPLETE
> **Decision:** 🟢 READY FOR HUMAN APPROVAL
> **Next:** Human Approval → Execute §3 → Validate §8 → Wave 2 Complete
