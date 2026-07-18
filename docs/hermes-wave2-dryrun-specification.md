# Hermes Wave 2 — Namespace Isolation Dry Run Specification

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T07:25:00Z
**Phase:** A.2.1 — Wave 2 Dry Run Specification
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Define isolated dry-run procedure to validate namespace isolation before touching production

**Governance Authority:**
- Project Namespace Boundary Review v1.0 (C.3)
- Registry Namespace Schema Amendment v1.0 (C.3.1)
- Wave 2 Namespace Isolation Assessment v1.0 (A.2.0)
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions (completed):**
- Wave 0: ✅ Registry 15→11, 8 Class C relocated
- Wave 1: ✅ 8→3 canonical + 6 aliases
- Wave 2 Assessment: ✅ 70+ skills classified across 3 layers

**This document does NOT:**
- Modify any SKILL.md
- Modify the Registry
- Execute migration
- Move or delete files

---

## 1. Objective

### 1.1 What This Dry Run Answers

> **"If we assign C.3 namespaces to every skill, will any namespace rule be violated, any dependency broken, or any project identity lost?"**

### 1.2 Dry Run ≠ Migration

| Dry Run | Real Migration |
|:-----|:-----|
| Simulated namespace map in `/tmp/` | Namespace metadata embedded in skills |
| Simulated registry in `/tmp/` | Real Registry updated (Wave 4) |
| Namespace rules verified in isolation | Namespace rules enforced in production |
| Rollback: delete `/tmp/` directory | Rollback: remove namespace metadata |
| Pass → ready for execution | Pass → complete |

### 1.3 Success Criteria

```
✅ All 19+ equivalence tests pass
✅ 0 namespace collisions detected
✅ 0 dependency violations detected
✅ 0 project identity loss
✅ Rollback simulation restores original state
✅ C.3 namespace model fully validated
```

---

## 2. Isolation Test Environment

### 2.1 Environment Layout

```
Production                          Dry Run (Shadow)
─────────────────────────────────────────────────────────────────
~/.hermes/skills/                   /tmp/hermes-wave2-dryrun/skills/          (copy)
skill-registry.json (11 entries)    /tmp/hermes-wave2-dryrun/registry.baseline.json
—                                   /tmp/hermes-wave2-dryrun/registry.simulated.json
—                                   /tmp/hermes-wave2-dryrun/namespace-map.json
—                                   /tmp/hermes-wave2-dryrun/dependency-graph.json
—                                   /tmp/hermes-wave2-dryrun/report/
```

### 2.2 Setup Procedure

```
Step 1: Create shadow directory
  mkdir -p /tmp/hermes-wave2-dryrun/{skills,report}

Step 2: Copy production state (post-Wave 0+1)
  cp -r ~/.hermes/skills/ /tmp/hermes-wave2-dryrun/skills/
  cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
     /tmp/hermes-wave2-dryrun/registry.baseline.json

Step 3: Generate simulated namespace map
  → For each of 70+ skills: assign C.3 namespace
  → Output: namespace-map.json

Step 4: Generate dependency graph
  → Map all inter-skill dependencies
  → Classify each dependency by layer (core→core, adapter→core, etc.)
  → Output: dependency-graph.json

Step 5: Verify isolation
  → Production Registry: 0 changes
  → Production Skills: 0 changes
```

### 2.3 Namespace Map Schema

```json
{
  "version": "1.0",
  "generated": "2026-07-18",
  "skills": [
    {
      "name": "a3-content-pipeline",
      "category": "software-development",
      "namespace": "project.a3.pipeline",
      "scope": "project",
      "ownership": {"tier": 2, "owner": "a3-team", "namespace": "project.a3"}
    },
    {
      "name": "browser-automation",
      "category": "browser-automation",
      "namespace": "adapter.browser",
      "scope": "adapter",
      "ownership": {"tier": 1, "owner": "hermes-platform", "namespace": "adapter"}
    }
  ]
}
```

---

## 3. Migration Simulation Matrix

### 3.1 Core Layer — hermes.core.*

**Classification:** Defines Hermes' own operational behavior. Project-agnostic.

| # | Skill | Namespace | Scope | Owner |
|:--|:-----|:-----|:-----|:-----|
| 1 | `agent-governance-protocol` | `hermes.core.governance` | `core` | `hermes-governance` |
| 2 | `architecture-constraints` | `hermes.core.constraints` | `core` | `hermes-governance` |
| 3 | `guidance-agent` | `hermes.core.guidance` | `core` | `hermes-platform` |
| 4 | `error-registry` | `hermes.core.errors` | `core` | `hermes-governance` |
| 5 | `skill-manager` | `hermes.core.registry` | `core` | `hermes-platform` |
| 6 | `harness-preflight` | `hermes.core.preflight` | `core` | `hermes-platform` |
| 7 | `task-progress` | `hermes.core.tracker` | `core` | `hermes-governance` |
| 8 | `agent-logger` | `hermes.core.logger` | `core` | `hermes-platform` |
| 9 | `agent-debugger` | `hermes.core.debugger` | `core` | `hermes-platform` |
| 10 | `agent-developer` | `hermes.core.developer` | `core` | `hermes-platform` |
| 11 | `agent-executor` | `hermes.core.executor` | `core` | `hermes-platform` |
| 12 | `skill-ecosystem-audit` | `hermes.core.auditor` | `core` | `hermes-governance` |
| 13 | `webhook-subscriptions` | `hermes.core.webhooks` | `core` | `hermes-platform` |
| 14 | `coding-agent-orchestration` | `hermes.core.coding` | `core` | `hermes-platform` |

**Verification Targets:**
- ✅ 0 project identifiers in namespace (no `a3`, `veritas`, `ucampus`)
- ✅ 0 project dependencies (no `→ project.*` in dependency graph)
- ✅ 0 project-specific paths in skill bodies
- ✅ `scope: core` for all 14 skills
- ✅ `ownership.tier: 0` (governance) or `1` (platform)

### 3.2 Adapter Layer — adapter.*

**Classification:** Bridges Hermes to external systems. Project-neutral.

Representative subset (35+ skills):

| # | Skill | Namespace | Scope | Owner |
|:--|:-----|:-----|:-----|:-----|
| 1 | `browser-automation` | `adapter.browser` | `adapter` | `hermes-platform` |
| 2 | `layer1-playwright` | `adapter.browser.playwright` | `adapter` | `hermes-platform` |
| 3 | `computer-use-mcp` | `adapter.desktop` | `adapter` | `hermes-platform` |
| 4 | `cli-anything` | `adapter.cli` | `adapter` | `hermes-platform` |
| 5 | `github-pr-workflow` | `adapter.github.pr` | `adapter` | `hermes-platform` |
| 6 | `himalaya` | `adapter.email` | `adapter` | `hermes-platform` |
| 7 | `content-review-pipeline` | `adapter.review.pipeline` | `adapter` | `hermes-platform` |
| 8 | `academic-writing` | `adapter.writing.academic` | `adapter` | `hermes-platform` |
| 9 | `jupyter-live-kernel` | `adapter.jupyter` | `adapter` | `hermes-platform` |
| 10 | `arxiv` | `adapter.research.arxiv` | `adapter` | `hermes-platform` |

**Verification Targets:**
- ✅ 0 project identifiers in namespace
- ✅ 0 project dependencies
- ✅ 0 project-specific paths in body (no `~/A3-*`, `~/Veritas-*`, `~/Terence-Agent/`)
- ✅ `scope: adapter` for all skills
- ✅ `ownership.tier: 1`

### 3.3 Project Layer — project.<id>.*

#### project.a3 — 7 Skills

| # | Skill | Namespace | Scope | Owner |
|:--|:-----|:-----|:-----|:-----|
| 1 | `a3-multi-agent-pipeline` | `project.a3.workflow` | `project` | `a3-team` |
| 2 | `a3-agent-team-pipeline` | `project.a3.workflow` (alias) | `project` | `a3-team` |
| 3 | `a3-multi-agent-content-pipeline` | `project.a3.workflow` (alias) | `project` | `a3-team` |
| 4 | `a3-content-pipeline` | `project.a3.pipeline` | `project` | `a3-team` |
| 5 | `a3-runtime-infrastructure` | `project.a3.infrastructure` | `project` | `a3-team` |
| 6 | `acp-coding-agent` | `project.a3.coding` | `project` | `a3-team` |
| 7 | `kanban-codex-lane` | `project.a3.kanban` | `project` | `a3-team` |

#### project.veritas — 1 Skill

| # | Skill | Namespace | Scope | Owner |
|:--|:-----|:-----|:-----|:-----|
| 1 | `veritas-core` | `project.veritas.core` | `project` | `veritas-team` |

#### project.ucampus — 4 Skills

| # | Skill | Namespace | Scope | Owner |
|:--|:-----|:-----|:-----|:-----|
| 1 | `ucampus-auto-complete` | `project.ucampus.automation` | `project` | `ucampus-team` |
| 2 | `u-campus-course-automation` | `project.ucampus.course` | `project` | `ucampus-team` |
| 3 | `chaoxing-homework` | `project.ucampus.chaoxing` | `project` | `ucampus-team` |
| 4 | `lab-report-execution` | `project.ucampus.lab` | `project` | `ucampus-team` |

**Verification Targets:**
- ✅ `namespace` prefix matches project ID (`project.a3.*`, `project.veritas.*`, `project.ucampus.*`)
- ✅ `scope: project` for all 12 skills
- ✅ `ownership.tier: 2` for all project skills
- ✅ `ownership.owner` matches project team
- ✅ Project identity preserved (not genericized)

---

## 4. Test Cases

### 4.1 Core Layer Tests (5 tests)

#### T1 — Core Namespace Integrity

| Field | Value |
|:-----|:-----|
| **ID** | CORE-NS-001 |
| **Purpose** | Verify all core skills have `hermes.core.*` namespace with 0 project identifiers |
| **Input** | namespace-map.json — all `scope: core` entries |
| **Expected** | All 14 core skills: namespace matches `^hermes\.core\.[a-z-]+$`. 0 contain `a3`, `veritas`, `ucampus`. |
| **Failure** | Any core skill has project ID in namespace |

#### T2 — Core Dependency Direction

| Field | Value |
|:-----|:-----|
| **ID** | CORE-DEP-001 |
| **Purpose** | Verify core skills have 0 dependencies on project or adapter skills |
| **Input** | dependency-graph.json — edges originating from `hermes.core.*` |
| **Expected** | All dependencies are `hermes.core.* → hermes.core.*`. 0 edges to `project.*` or `adapter.*`. |
| **Failure** | Any core→project or core→adapter edge detected |

#### T3 — Core Body Content Scan

| Field | Value |
|:-----|:-----|
| **ID** | CORE-BODY-001 |
| **Purpose** | Verify core skill bodies contain 0 project-specific paths |
| **Input** | All 14 core SKILL.md files |
| **Expected** | 0 occurrences of `~/A3-Multi-Agent-System/`, `~/Veritas-Core/`, `~/Terence-Agent/` in core skill bodies |
| **Failure** | Any project path found in core skill body |

#### T4 — Core Ownership Tier

| Field | Value |
|:-----|:-----|
| **ID** | CORE-OWN-001 |
| **Purpose** | Verify core skills have correct ownership tiers |
| **Input** | namespace-map.json — all `scope: core` entries |
| **Expected** | Governance skills: `tier: 0, owner: hermes-governance`. Platform skills: `tier: 1, owner: hermes-platform`. |
| **Failure** | Core skill with `tier: 2` (project ownership) |

#### T5 — Core Scope Immutability

| Field | Value |
|:-----|:-----|
| **ID** | CORE-IMM-001 |
| **Purpose** | Verify core skill scope cannot be changed after assignment |
| **Input** | namespace-map.json — attempt scope change on existing core skill |
| **Expected** | Scope change rejected. `scope` is immutable after initial assignment. |
| **Failure** | Scope changed without deprecation + re-registration |

---

### 4.2 Adapter Layer Tests (5 tests)

#### T6 — Adapter Namespace Neutrality

| Field | Value |
|:-----|:-----|
| **ID** | ADAPTER-NS-001 |
| **Purpose** | Verify all adapter skills have `adapter.*` namespace with 0 project identifiers |
| **Input** | namespace-map.json — all `scope: adapter` entries |
| **Expected** | All 35+ adapter skills: namespace matches `^adapter\.[a-z.]+$`. 0 contain `a3`, `veritas`, `ucampus`. |
| **Failure** | Any adapter skill has project ID in namespace |

#### T7 — Adapter Dependency Direction

| Field | Value |
|:-----|:-----|
| **ID** | ADAPTER-DEP-001 |
| **Purpose** | Verify adapter skills have 0 dependencies on project skills |
| **Input** | dependency-graph.json — edges originating from `adapter.*` |
| **Expected** | Dependencies: `adapter.* → hermes.core.*` (allowed) or `adapter.* → adapter.*` (allowed). 0 edges to `project.*`. |
| **Failure** | Any adapter→project edge detected |

#### T8 — Adapter Body Content Scan

| Field | Value |
|:-----|:-----|
| **ID** | ADAPTER-BODY-001 |
| **Purpose** | Verify adapter skill bodies contain 0 project-specific paths |
| **Input** | All 35+ adapter SKILL.md files |
| **Expected** | 0 occurrences of `~/A3-*`, `~/Veritas-*`, `~/Terence-Agent/` in adapter bodies |
| **Failure** | Any project path found in adapter skill body |

#### T9 — Adapter Cross-Project Neutrality

| Field | Value |
|:-----|:-----|
| **ID** | ADAPTER-CROSS-001 |
| **Purpose** | Verify adapter skills work for ALL projects, not just one |
| **Input** | Simulated project.skill dependency: `project.a3.* → adapter.*` and `project.veritas.* → adapter.*` |
| **Expected** | Both project namespaces can depend on same adapter. No adapter code keyed on project identity. |
| **Failure** | Adapter has conditional logic based on which project called it |

#### T10 — Adapter Ownership Tier

| Field | Value |
|:-----|:-----|
| **ID** | ADAPTER-OWN-001 |
| **Purpose** | Verify all adapter skills have `tier: 1, owner: hermes-platform` |
| **Input** | namespace-map.json — all `scope: adapter` entries |
| **Expected** | All adapter skills: `ownership.tier: 1`. All: `ownership.owner: hermes-platform`. |
| **Failure** | Adapter skill with `tier: 2` or non-platform owner |

---

### 4.3 Project Layer Tests (9 tests)

#### T11 — Project Namespace Assignment (A3)

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-A3-001 |
| **Purpose** | Verify all 7 A3 skills have correct `project.a3.*` namespace |
| **Input** | namespace-map.json — all `scope: project` entries with `a3` |
| **Expected** | 5 active + 2 aliases: all `namespace` starts with `project.a3.`. Sub-domains: workflow, pipeline, infrastructure, coding, kanban. |
| **Failure** | Any A3 skill assigned to non-A3 namespace or generic namespace |

#### T12 — Project Namespace Assignment (Veritas)

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-VER-001 |
| **Purpose** | Verify `veritas-core` has correct `project.veritas.core` namespace |
| **Input** | namespace-map.json — `veritas-core` entry |
| **Expected** | `namespace: project.veritas.core`. `scope: project`. `owner: veritas-team`. |
| **Failure** | Veritas skill assigned to generic or wrong namespace |

#### T13 — Project Namespace Assignment (UCampus)

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-UC-001 |
| **Purpose** | Verify all 4 UCampus skills have correct `project.ucampus.*` namespace |
| **Input** | namespace-map.json — all `scope: project` entries with `ucampus` |
| **Expected** | All 4: `namespace` starts with `project.ucampus.`. Sub-domains: automation, course, chaoxing, lab. |
| **Failure** | Any UCampus skill assigned to wrong namespace |

#### T14 — Project Ownership Tier

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-OWN-001 |
| **Purpose** | Verify all project skills have `tier: 2` with correct project owner |
| **Input** | namespace-map.json — all `scope: project` entries |
| **Expected** | A3 skills: `tier: 2, owner: a3-team`. Veritas: `tier: 2, owner: veritas-team`. UCampus: `tier: 2, owner: ucampus-team`. |
| **Failure** | Project skill with `tier: 0` or `tier: 1` |

#### T15 — Project Identity Preservation

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-ID-001 |
| **Purpose** | Verify project identity is preserved in namespace — NOT genericized |
| **Input** | Compare original B.3 Wave 2 plan (generic names) vs C.3 current assignment |
| **Expected** | `a3-runtime-infrastructure` → `project.a3.infrastructure` (NOT `agent-runtime-infrastructure`). `veritas-core` → `project.veritas.core` (NOT `agent-runtime-development`). |
| **Failure** | Any project skill assigned to generic namespace without project ID |

#### T16 — Project Dependency (allowed directions)

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-DEP-001 |
| **Purpose** | Verify project skills can depend on core and adapter |
| **Input** | dependency-graph.json — edges from `project.*` |
| **Expected** | All dependencies are `project.* → hermes.core.*` or `project.* → adapter.*`. No blocked directions. |
| **Failure** | Legitimate project→core dependency flagged as violation |

#### T17 — Cross-Project Dependency Control

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-CROSS-001 |
| **Purpose** | Verify cross-project dependency requires explicit declaration |
| **Input** | Simulated `project.a3.workflow → project.veritas.core` dependency |
| **Expected** | Dependency flagged as ⚠️ WARNING without `cross_project: true`. Accepted with `cross_project: true` + `justification`. |
| **Failure** | Cross-project dependency silently accepted without declaration |

#### T18 — Project Namespace Uniqueness

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-UNIQ-001 |
| **Purpose** | Verify no two skills share the same namespace |
| **Input** | namespace-map.json — all namespaces |
| **Expected** | All 70+ namespaces are unique. 0 duplicates. |
| **Failure** | Two skills with identical `namespace` value |

#### T19 — Project Scope Consistency

| Field | Value |
|:-----|:-----|
| **ID** | PROJECT-SCOPE-001 |
| **Purpose** | Verify namespace prefix matches scope value |
| **Input** | namespace-map.json — cross-field validation |
| **Expected** | `hermes.core.*` → `scope: core`. `adapter.*` → `scope: adapter`. `project.<id>.*` → `scope: project`. |
| **Failure** | Mismatch — e.g., `namespace: project.a3.*` with `scope: adapter` |

---

## 5. Dependency Boundary Tests

### 5.1 Allowed Directions

```
✅ Core → Core:
   hermes.core.governance → hermes.core.constraints
   Test: All core→core edges in dependency graph are valid

✅ Adapter → Core:
   adapter.browser → hermes.core.registry
   Test: adapter skills may use core infrastructure

✅ Adapter → Adapter:
   adapter.browser.playwright → adapter.browser
   Test: internal adapter hierarchy

✅ Project → Core:
   project.a3.workflow → hermes.core.registry
   Test: project skills may use core infrastructure

✅ Project → Adapter:
   project.ucampus.automation → adapter.browser
   Test: project skills may use adapter bridges

✅ Project → Project (same namespace):
   project.a3.workflow → project.a3.infrastructure
   Test: same-project internal dependency
```

### 5.2 Prohibited Directions

```
❌ Core → Project:
   hermes.core.governance → project.a3.workflow
   Test: BLOCK — must be rejected. Core must not depend on any project.

❌ Core → Adapter:
   hermes.core.registry → adapter.browser
   Test: BLOCK — must be rejected. Core must not depend on adapter.

❌ Adapter → Project:
   adapter.browser → project.a3.workflow
   Test: BLOCK — must be rejected. Adapter must be project-neutral.

❌ Project → Project (cross-namespace, undeclared):
   project.a3.workflow → project.veritas.core (no cross_project flag)
   Test: WARNING — must require explicit declaration.
```

### 5.3 Conditional Direction

```
⚠️ Project_A → Project_B (declared):
   project.a3.workflow → project.veritas.core (with cross_project: true)
   Test: ACCEPTED — valid with justification. Triggers review gate.
```

---

## 6. Rollback Simulation

### 6.1 Namespace Metadata Rollback

```
Trigger: Any namespace rule violation detected

Step 1: STOP all dry run tests
Step 2: Delete namespace-map.json
Step 3: Delete dependency-graph.json
Step 4: Verify: no namespace artifacts remain in /tmp/
Step 5: Re-generate from scratch → confirm identical output
```

### 6.2 Registry Rollback

```
Trigger: Simulated registry corruption

Step 1: Restore registry from baseline
  cp /tmp/hermes-wave2-dryrun/registry.baseline.json \
     /tmp/hermes-wave2-dryrun/registry.simulated.json

Step 2: Verify 0 differences
  diff baseline.json simulated.json → 0 differences

Step 3: Re-run namespace map generation → identical output
```

### 6.3 Alias Rollback

```
Trigger: Alias namespace mismatch

Step 1: Clear alias entries from namespace map
Step 2: Re-add aliases with correct namespace (from Wave 1 manifest)
Step 3: Verify alias namespaces match canonical namespaces
```

### 6.4 Rollback Verification Summary

| Artifact | Rollback Method | Verification |
|:-----|:-----|:-----|
| `namespace-map.json` | Delete + regenerate | Identical output |
| `dependency-graph.json` | Delete + regenerate | Identical graph structure |
| `registry.simulated.json` | Restore from baseline | 0 diff |
| Alias entries | Clear + re-add | Match Wave 1 manifest |

---

## 7. Failure Conditions

### 7.1 BLOCK Conditions — Halt Dry Run

| # | Condition | Test | Severity |
|:--|:-----|:----:|:----:|
| **B1** | **Namespace Collision** — Two skills share the same namespace | T18 | **CRITICAL** |
| **B2** | **Ownership Mismatch** — Core skill has `tier: 2` (project ownership) | T4, T10, T14 | **CRITICAL** |
| **B3** | **Core Pollution** — Project ID in core namespace | T1, T3 | **CRITICAL** |
| **B4** | **Adapter Pollution** — Project path or dependency in adapter | T6, T7, T8 | **CRITICAL** |
| **B5** | **Dependency Violation** — Core→Project or Adapter→Project edge | T2, T7 | **CRITICAL** |
| **B6** | **Project Identity Loss** — Project skill assigned to generic namespace | T15 | **CRITICAL** |
| **B7** | **Scope Mismatch** — Namespace prefix doesn't match scope | T19 | **CRITICAL** |

### 7.2 WARNING Conditions — Proceed with Caution

| # | Condition | Test | Severity |
|:--|:-----|:----:|:----:|
| **W1** | **Missing Metadata** — Skill has no namespace/scope/ownership assigned | All | MEDIUM |
| **W2** | **Unclear Owner** — Project skill with ambiguous owner | T14 | MEDIUM |
| **W3** | **Undocumented Cross-Project** — Project_A→Project_B without justification | T17 | LOW |
| **W4** | **Namespace Depth** — Excessively deep namespace (>4 levels) | T18 | LOW |

---

## 8. Human Approval Gate

### 8.1 Pre-Dry-Run Approval

```
☐ Governance Reviewer confirms:

  ☐ Dry run environment isolated from production (/tmp/hermes-wave2-dryrun/)
  ☐ Namespace map schema defined (3 layers, 70+ skills)
  ☐ Test matrix defined: 5 core + 5 adapter + 9 project = 19 tests
  ☐ Dependency boundary rules specified (allowed/prohibited/conditional)
  ☐ Rollback procedures defined (namespace + registry + alias)
  ☐ C.3 namespace model applied:
      ☐ Project identity preserved (project.a3, project.veritas, project.ucampus)
      ☐ Core neutrality enforced
      ☐ Adapter neutrality enforced
  ☐ Migration Operator designated
  ☐ Validator designated
```

### 8.2 Post-Dry-Run Approval

```
☐ Governance Reviewer confirms:

  ☐ All 19+ equivalence tests PASS
  ☐ 0 Critical Failures (B1-B7)
  ☐ Namespace isolation validated — project identity preserved
  ☐ Core neutrality confirmed — 0 project dependencies
  ☐ Adapter neutrality confirmed — 0 project paths
  ☐ Rollback simulation successful
  ☐ Dry run report produced
```

---

## 9. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   WAVE 2 — NAMESPACE ISOLATION DRY RUN SPECIFICATION          ║
║                                                              ║
║   Test plan:                                                  ║
║     Core layer:      5 tests                                  ║
║     Adapter layer:   5 tests                                  ║
║     Project layer:   9 tests                                  ║
║     Boundary:        4 direction checks                       ║
║     ─────────────────────                                    ║
║     TOTAL:           19 tests + 4 boundary checks             ║
║                                                              ║
║   7 BLOCK conditions (B1-B7)                                  ║
║   4 WARNING conditions (W1-W4)                                ║
║   3 rollback procedures                                       ║
║                                                              ║
║   Dry run environment: /tmp/hermes-wave2-dryrun/              ║
║   Production: untouched (0 Registry, 0 Skill changes)         ║
║                                                              ║
║   🟢 READY FOR WAVE 2 DRY RUN                                ║
║                                                              ║
║   Pre-condition: §8 Human Approval Gate signed                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-wave2-dryrun-specification.md` |
| 9 chapters complete | ✅ §1-9 |
| 19 test cases defined | ✅ 5 core + 5 adapter + 9 project |
| 4 dependency boundary checks | ✅ Allowed/prohibited/conditional |
| 7 BLOCK conditions | ✅ B1-B7 |
| 4 WARNING conditions | ✅ W1-W4 |
| 3 rollback procedures | ✅ Namespace + Registry + Alias |
| Namespace map schema | ✅ JSON format defined |
| C.3 model applied | ✅ All 3 layers |
| 0 executable code | ✅ |
| Registry unchanged | ✅ 11 entries |
| Skills unchanged | ✅ |
| No PII | ✅ |
| Git diff | ✅ Only this new file |

---

> **Phase:** A.2.1 — Wave 2 Dry Run Specification
> **Status:** ✅ COMPLETE
> **Decision:** 🟢 READY FOR WAVE 2 DRY RUN
> **Tests:** 19 defined (5 core + 5 adapter + 9 project) + 4 boundary checks
> **Next:** Phase A.2.2 — Wave 2 Dry Run Execution (awaiting authorization)
