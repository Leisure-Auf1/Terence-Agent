# Hermes Wave 1 — Duplicate Merge Assessment

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T06:45:00Z
**Phase:** A.1.0 — Wave 1 Duplicate Merge Assessment
**Audience:** Governance Reviewer (Human) · Migration Operator
**Purpose:** Assess duplicate skill groups, define merge decisions respecting C.3 namespace model, and establish dry run procedure

**Governance Authority:**
- Governance Constitution v1.0 (FROZEN per C.5)
- Project Namespace Boundary Review v1.0 (C.3)
- Migration Specification v1.0 (B.3)
- Wave 0 Execution Result v1.0 — SUCCESS (registry 15→11)

**This document is:**
- A pre-execution assessment of skill duplication
- A merge decision model respecting the three-layer namespace model
- A C.3-correction to the original B.3 Wave 1 plan

**This document does NOT:**
- Modify any SKILL.md
- Modify the Registry
- Execute any merge
- Move or delete files

---

## Executive Summary

### Wave 1 Objective

Wave 1 merges duplicate Skills into canonical Skills. **Merge ≠ Delete.** All content is preserved. All original files remain. Deprecated aliases maintain backward compatibility.

### C.3 Namespace Model Impact

The original B.3 Wave 1 plan was written **before** the C.3 namespace correction. It proposed merging all duplicate groups into generic capability names — including A3 project skills. This violates the namespace model.

**Critical Correction:**

```
B.3 Plan (FLAWED):
  a3-multi-agent-pipeline + a3-agent-team-pipeline + a3-multi-agent-content-pipeline
    → "multi-agent-pipeline" (generic, project identity erased)

C.3 Correction:
  Same 3 skills → merge WITHIN project.a3 namespace
    → project.a3.workflow
    → name: workflow
    → Project identity PRESERVED in namespace prefix
```

### Assessment Result

```
3 merge groups identified (8 skills → 3 canonical)

  Group 1 (project.a3):  3 → 1  ✅ Merge within project namespace
  Group 2 (adapter):     3 → 1  ✅ Merge generic content review skills
  Group 3 (adapter):     2 → 1  ✅ Merge generic academic writing skills

  Skills affected:        8
  New canonical skills:   3
  Skills deprecated:      5 (aliased to canonical)
  Zero deletions:         All original files preserved
```

---

## 1. Wave 1 Objective

### 1.1 What Wave 1 Does

```
Wave 1 = Duplicate Capability Merge

  MERGE:  Combine duplicate Skills into a single canonical Skill
          → All non-overlapping content preserved
          → Overlapping content uses the most general version

  ALIAS:  Old Skill IDs → DEPRECATED with replaced_by → canonical Skill
          → 14-day grace period before archival
          → All existing references redirected

  KEEP:   Non-duplicate Skills → untouched

  DELETE: ❌ NOT IN WAVE 1 — no files are ever deleted
```

### 1.2 Merge ≠ Delete

| Merge | Delete |
|:-----|:-----|
| ✅ Content preserved in canonical Skill | ❌ Content lost |
| ✅ Old file retained at original path | ❌ File removed |
| ✅ Old ID → deprecated alias → canonical | ❌ Old ID → 404 |
| ✅ Reversible (reactivate deprecated Skill) | ❌ Irreversible |
| ✅ Capability continuity guaranteed | ❌ Capability gap |

### 1.3 What Constitutes a "Duplicate"

Two or more Skills are duplicates when:

1. **Same capability domain** — they serve the same purpose
2. **Overlapping triggers** — they would be dispatched for the same tasks
3. **Redundant content** — significant overlap in instructions/workflows
4. **Same namespace scope** — they belong to the same layer (core/adapter/project)

**NOT duplicates:**
- Skills with different scopes (one is project, one is adapter) — NOT merged
- Skills with complementary responsibilities (e.g., auto-complete vs full guide) — NOT merged
- Skills in different project namespaces (project.a3 vs project.veritas) — NEVER merged across projects

---

## 2. Duplicate Inventory

### 2.1 Group 1 — A3 Multi-Agent Pipeline

| # | Skill | Category | Current Namespace | Lines | Triggers |
|:--|:-----|:-----|:-----|:----:|:-----|
| 1 | `a3-multi-agent-pipeline` | autonomous-ai-agents | `project.a3` (implicit) | ~200+ | A3 multi-agent workflow |
| 2 | `a3-agent-team-pipeline` | software-development | `project.a3` (implicit) | ~150+ | A3 agent team pipeline |
| 3 | `a3-multi-agent-content-pipeline` | software-development | `project.a3` (implicit) | ~200+ | A3 content pipeline |

**Similarity Analysis:**

| Aspect | Finding |
|:-----|:-----|
| **Capability domain** | All three describe multi-agent orchestration for content generation within the A3 system |
| **Overlap level** | HIGH — `a3-multi-agent-pipeline` is the most comprehensive; the other two are variants/specializations |
| **Content uniqueness** | `a3-agent-team-pipeline`: agent team routing details; `a3-multi-agent-content-pipeline`: content generation specifics |
| **Target audience** | A3 project exclusively — all three serve `project.a3` |

**C.3 Namespace Classification:** `project.a3` — These are project skills, NOT generic capabilities.

**Duplicate Verdict:** ✅ TRUE DUPLICATE — Merge within `project.a3` namespace.

**Canonical Candidate:** `a3-multi-agent-pipeline` (most comprehensive, already the umbrella).

**Target Namespace:** `project.a3.workflow`

**Risk Level:** 🟢 LOW — All in same project namespace; no cross-project impact.

---

### 2.2 Group 2 — Content Review

| # | Skill | Category | Current Namespace | Lines | Triggers |
|:--|:-----|:-----|:-----|:----:|:-----|
| 1 | `content-review-gate` | software-development | generic (adapter) | ~150+ | Content quality review gate |
| 2 | `review-gate-pipeline` | devops | generic (adapter) | ~200+ | Review gate pipeline |
| 3 | `content-review-pipeline` | content-review-pipeline | generic (adapter) | ~250+ | Content review pipeline |

**Similarity Analysis:**

| Aspect | Finding |
|:-----|:-----|
| **Capability domain** | All three describe content quality review workflows — gate checking, pipeline stages, validation |
| **Overlap level** | MEDIUM-HIGH — each adds a different review layer (AST audit, user simulation, pipeline orchestration) |
| **Content uniqueness** | `content-review-gate`: AST static audit + pytest validation; `review-gate-pipeline`: user simulation + hot-fix loop; `content-review-pipeline`: pipeline orchestration |
| **Target audience** | Generic — applicable to any content review task |

**C.3 Namespace Classification:** `adapter` — These are generic capability skills, NOT project-specific.

**Duplicate Verdict:** ✅ TRUE DUPLICATE — Merge into single canonical adapter skill.

**Canonical Candidate:** `content-review-pipeline` (most comprehensive, already the best name).

**Target Namespace:** `adapter.review.pipeline`

**Risk Level:** 🟢 LOW — All generic; merge preserves all review gate logic.

---

### 2.3 Group 3 — Academic Writing

| # | Skill | Category | Current Namespace | Lines | Triggers |
|:--|:-----|:-----|:-----|:----:|:-----|
| 1 | `paper-report-writing` | research | generic (adapter) | ~250+ | Paper/report writing |
| 2 | `research-paper-writing` | research | generic (adapter) | ~200+ | Research paper writing |

**Similarity Analysis:**

| Aspect | Finding |
|:-----|:-----|
| **Capability domain** | Both describe academic paper and report writing workflows |
| **Overlap level** | HIGH — significant overlap in writing methodology, structure, and review process |
| **Content uniqueness** | `paper-report-writing`: Feynman research agent integration; `research-paper-writing`: multi-agent writing workflow |
| **Target audience** | Generic — applicable to any academic writing task |

**C.3 Namespace Classification:** `adapter` — These are generic capability skills.

**Duplicate Verdict:** ✅ TRUE DUPLICATE — Merge into single canonical adapter skill.

**Canonical Candidate:** `academic-writing` (clearer, more comprehensive capability name).

**Target Namespace:** `adapter.writing.academic`

**Risk Level:** 🟢 LOW — Both generic; merge preserves all writing methodology.

---

### 2.4 Groups NOT Merged

The original B.3 spec mentioned 10 duplicate groups. After C.3 namespace review, the remaining groups are:

| Group | Skills | Reason NOT Merged |
|:-----|:-----|:-----|
| U-Campus | `ucampus-auto-complete` + `u-campus-course-automation` | Complementary, not duplicates: auto-completion vs full workflow guide |
| Platform Branches | `baoyu-*`, `a3-*` variants | Platform-specific adaptations — may be Wave 2 namespace isolation |
| Domain Variants | `cli-anything` vs `cli-anything-hermes` | Different purposes: integration vs builder |
| Browser Layer | `layer1-*` through `layer4-*` | Hierarchical, not duplicates — each layer has distinct capability |

**Only 3 groups (8 skills) qualify as true duplicates under C.3 rules.**

---

## 3. Merge Decision Model

### 3.1 Decision Types

| Decision | Symbol | Meaning | Action |
|:-----|:----:|:-----|:-----|
| **KEEP** | ✅ | No duplication; Skill is unique | No change |
| **MERGE** | 🔀 | Skill is a duplicate → content merged into canonical | Content merged; old ID deprecated |
| **ALIAS** | 🔗 | Old ID preserved as redirect to canonical | Set `lifecycle: deprecated` + `replaced_by` |
| **DEPRECATE** | ⏸️ | Skill is obsolete; grace period before archival | 14-day grace period; then archived |
| **DELETE** | ❌ | Never used in Wave 1 | PROHIBITED |

### 3.2 Merge Decision Matrix

| Group | Skill | Decision | Target |
|:-----|:-----|:----:|:-----|
| **Group 1** | `a3-multi-agent-pipeline` | 🔀 MERGE (canonical) | `project.a3.workflow` |
| | `a3-agent-team-pipeline` | 🔀 MERGE → canonical | Content absorbed into canonical |
| | `a3-multi-agent-content-pipeline` | 🔀 MERGE → canonical | Content absorbed into canonical |
| **Group 2** | `content-review-pipeline` | 🔀 MERGE (canonical) | `adapter.review.pipeline` |
| | `content-review-gate` | 🔀 MERGE → canonical | Content absorbed into canonical |
| | `review-gate-pipeline` | 🔀 MERGE → canonical | Content absorbed into canonical |
| **Group 3** | `paper-report-writing` | 🔀 MERGE → `academic-writing` | Content absorbed into canonical |
| | `research-paper-writing` | 🔀 MERGE → `academic-writing` | Content absorbed into canonical |
| | — | — | `adapter.writing.academic` (new) |

### 3.3 Content Merge Rules

```
Rule 1: Non-overlapping content → ALL PRESERVED
  → Every unique section from every merged Skill is included in canonical

Rule 2: Overlapping content → MOST GENERAL VERSION KEPT
  → If two Skills describe the same thing, the broader/more complete version wins

Rule 3: Project-specific content → STAYS IN PROJECT NAMESPACE
  → A3-specific workflow details stay in project.a3 namespace
  → NOT genericized into adapter

Rule 4: Conflicts → HUMAN REVIEW REQUIRED
  → If two Skills give contradictory instructions, mark for human resolution
  → Do not silently choose one over the other

Rule 5: Triggers → UNION
  → Canonical Skill inherits all trigger patterns from all merged Skills
```

---

## 4. Canonical Selection Rules

### 4.1 Selection Criteria

| # | Criterion | Weight | Description |
|:--|:-----|:----:|:-----|
| C1 | **Content Completeness** | HIGH | Which Skill has the most comprehensive content? |
| C2 | **Namespace Fit** | HIGH | Which Skill best fits the target namespace? |
| C3 | **Name Clarity** | MEDIUM | Which name best describes the capability? |
| C4 | **Lifecycle Maturity** | MEDIUM | Which Skill has the most stable version/lifecycle? |
| C5 | **Dependency Impact** | LOW | Which Skill has the fewest dependents to update? |
| C6 | **Ownership Clarity** | LOW | Which Skill has the clearest ownership? |

### 4.2 Per-Group Selection

#### Group 1 — Canonical: `a3-multi-agent-pipeline`

| Criterion | Assessment |
|:-----|:-----|
| C1 — Completeness | **BEST** — Most comprehensive A3 workflow description |
| C2 — Namespace | Fits `project.a3.workflow` |
| C3 — Name | `a3-multi-agent-pipeline` — clear project ownership |
| C4 — Maturity | v3.6 — most mature version |
| C5 — Dependencies | Referenced by A3 ecosystem; update scope is within project.a3 |
| C6 — Ownership | `a3-team` |

**Decision:** `a3-multi-agent-pipeline` → canonical. Other two → content merged in.

#### Group 2 — Canonical: `content-review-pipeline`

| Criterion | Assessment |
|:-----|:-----|
| C1 — Completeness | **BEST** — Pipeline orchestration is most comprehensive |
| C2 — Namespace | Fits `adapter.review.pipeline` |
| C3 — Name | `content-review-pipeline` — descriptive and already canonical-sounding |
| C4 — Maturity | All three are active; `content-review-pipeline` is the longest-established |
| C5 — Dependencies | Cross-referenced by other skills; update scope is limited |
| C6 — Ownership | Generic — `hermes-platform` |

**Decision:** `content-review-pipeline` → canonical. Other two → content merged in.

#### Group 3 — Canonical: `academic-writing`

| Criterion | Assessment |
|:-----|:-----|
| C1 — Completeness | New name — content merged from both sources |
| C2 — Namespace | `adapter.writing.academic` |
| C3 — Name | `academic-writing` — clearer than either original; broader domain |
| C4 — Maturity | New canonical — inherits maturity from merged skills |
| C5 — Dependencies | Both are research category skills; limited cross-references |
| C6 — Ownership | Generic — `hermes-platform` |

**Decision:** Create new `academic-writing` as canonical. Both old skills → content merged in.

---

## 5. Namespace Compliance Check

### 5.1 C.3 Three-Layer Model Compliance

| Group | Canonical Namespace | Scope | Layer | Compliant? |
|:-----|:-----|:-----|:-----|:----:|
| Group 1 | `project.a3.workflow` | `project` | Project Layer | ✅ Project identity preserved |
| Group 2 | `adapter.review.pipeline` | `adapter` | Adapter Layer | ✅ Generic, project-neutral |
| Group 3 | `adapter.writing.academic` | `adapter` | Adapter Layer | ✅ Generic, project-neutral |

### 5.2 Dependency Direction Verification

```
After Wave 1 merge:

  project.a3.workflow
    → depends on: hermes.core.* (Core — allowed ✅)
    → depends on: adapter.* (Adapter — allowed ✅)
    → does NOT depend on: project.veritas.* or project.ucampus.* ❌ (correct)

  adapter.review.pipeline
    → depends on: hermes.core.* (Core — allowed ✅)
    → does NOT depend on: project.* (correct — Adapter neutral ✅)

  adapter.writing.academic
    → depends on: hermes.core.* (Core — allowed ✅)
    → does NOT depend on: project.* (correct — Adapter neutral ✅)
```

### 5.3 Forbidden Patterns — None Detected

| Pattern | Detected? | Status |
|:-----|:----:|:----:|
| Project identity in Core namespace | ❌ | ✅ |
| Project identity in Adapter namespace | ❌ | ✅ |
| Core → Project dependency | ❌ | ✅ |
| Adapter → Project dependency | ❌ | ✅ |
| Cross-project merge (project.a3 ← project.veritas) | ❌ | ✅ |

---

## 6. Alias Compatibility Strategy

### 6.1 Deprecated Alias Model

```
For each merged (non-canonical) Skill:

  1. Set lifecycle: deprecated
  2. Set replaced_by: <canonical-namespace>/<canonical-name>
  3. Set status: grace_period
  4. Grace period: 14 days
  5. After grace period: lifecycle: archived

During grace period:
  - Old name still resolves → redirects to canonical
  - All existing references continue to work
  - New references to old name generate a deprecation warning
```

### 6.2 Per-Group Alias Mapping

#### Group 1

| Old Name | Alias → Canonical | Grace Period |
|:-----|:-----|:----:|
| `a3-agent-team-pipeline` | → `project.a3.workflow` (canonical: `a3-multi-agent-pipeline`) | 14 days |
| `a3-multi-agent-content-pipeline` | → `project.a3.workflow` (canonical: `a3-multi-agent-pipeline`) | 14 days |

#### Group 2

| Old Name | Alias → Canonical | Grace Period |
|:-----|:-----|:----:|
| `content-review-gate` | → `adapter.review.pipeline` (canonical: `content-review-pipeline`) | 14 days |
| `review-gate-pipeline` | → `adapter.review.pipeline` (canonical: `content-review-pipeline`) | 14 days |

#### Group 3

| Old Name | Alias → Canonical | Grace Period |
|:-----|:-----|:----:|
| `paper-report-writing` | → `adapter.writing.academic` (canonical: `academic-writing`) | 14 days |
| `research-paper-writing` | → `adapter.writing.academic` (canonical: `academic-writing`) | 14 days |

### 6.3 Backward Compatibility Guarantee

```
✅ All 5 deprecated aliases resolve to their canonical Skill
✅ 14-day grace period for reference migration
✅ Old SKILL.md files preserved at original paths
✅ No capability loss — all content merged into canonical
✅ Reversible — deprecated Skills can be reactivated within grace period
```

---

## 7. Dry Run Specification

### 7.1 Dry Run Environment

```
Isolated environment:  /tmp/hermes-wave1-dryrun/

Step 1: Create shadow directory
  mkdir -p /tmp/hermes-wave1-dryrun/{skills,registry}

Step 2: Copy current state
  cp -r ~/.hermes/skills/ /tmp/hermes-wave1-dryrun/skills/
  cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
     /tmp/hermes-wave1-dryrun/registry/baseline.json

Step 3: Create simulated post-merge state
  → Create 3 canonical SKILL.md files (merged content)
  → Mark 5 deprecated aliases
  → Verify content equivalence
```

### 7.2 Equivalence Tests

#### Group 1 — A3 Pipeline (3 tests)

| Test | Description | Expected |
|:-----|:-----|:-----|
| T1.1 | Canonical Skill contains all content from 3 sources | All unique sections from `a3-agent-team-pipeline` + `a3-multi-agent-content-pipeline` present in canonical |
| T1.2 | Trigger union complete | All trigger patterns from all 3 sources available |
| T1.3 | Deprecated aliases resolve | `skill_view('a3-agent-team-pipeline')` → redirects to canonical |

#### Group 2 — Content Review (3 tests)

| Test | Description | Expected |
|:-----|:-----|:-----|
| T2.1 | AST audit logic from `content-review-gate` present | Static analysis + pytest validation sections in canonical |
| T2.2 | User simulation from `review-gate-pipeline` present | User simulation + hot-fix loop sections in canonical |
| T2.3 | Pipeline orchestration intact | Pipeline stage definitions from original `content-review-pipeline` unchanged |

#### Group 3 — Academic Writing (2 tests)

| Test | Description | Expected |
|:-----|:-----|:-----|
| T3.1 | Feynman agent from `paper-report-writing` present | Feynman research agent integration in canonical |
| T3.2 | Multi-agent workflow from `research-paper-writing` present | Multi-agent writing pipeline in canonical |

### 7.3 Rollback Simulation

```
Trigger: Any equivalence test fails

Step 1: Stop dry run
Step 2: Restore registry from baseline
Step 3: Remove canonical SKILL.md files
Step 4: Re-run failing test against original Skills
Step 5: Verify original behavior restored
```

---

## 8. Human Approval Gate

### 8.1 Pre-Merge Approval Items

```
☐ Governance Reviewer confirms:

  ☐ Group 1 merge: 3 A3 skills → project.a3.workflow (within project namespace)
  ☐ Group 2 merge: 3 review skills → adapter.review.pipeline
  ☐ Group 3 merge: 2 writing skills → adapter.writing.academic
  ☐ All 5 deprecated aliases have 14-day grace period
  ☐ No skill files deleted — content merged, not removed
  ☐ C.3 namespace model respected (project identity preserved in Group 1)
  ☐ No cross-project merges
```

### 8.2 Post-Merge Approval Items

```
☐ Governance Reviewer confirms:

  ☐ All 3 canonical Skills contain complete merged content
  ☐ All 5 deprecated aliases resolve correctly
  ☐ Equivalence tests pass (8/8)
  ☐ Dry run rollback simulation successful
  ☐ Registry entries updated (5 deprecated + 3 canonical)
```

---

## 9. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   WAVE 1 — DUPLICATE MERGE ASSESSMENT                        ║
║                                                              ║
║   3 merge groups identified                                   ║
║   8 skills → 3 canonical                                      ║
║   5 deprecated aliases                                        ║
║   0 deletions                                                 ║
║                                                              ║
║   C.3 Compliance:                                             ║
║     Group 1: project.a3 namespace preserved ✅                ║
║     Group 2: adapter.review — project-neutral ✅              ║
║     Group 3: adapter.writing — project-neutral ✅             ║
║                                                              ║
║   🟢 READY FOR WAVE 1 DRY RUN                                ║
║                                                              ║
║   Next: Phase A.1.1 — Wave 1 Dry Run                         ║
║          (8 equivalence tests in isolated environment)        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-wave1-duplicate-merge-assessment.md` |
| 9 chapters complete | ✅ Executive Summary + §1-9 |
| 3 merge groups assessed | ✅ With namespace classification |
| C.3 namespace model applied | ✅ Group 1 preserves project.a3 identity |
| Merge ≠ Delete principle | ✅ §1.2 |
| No executable code | ✅ Pure documentation |
| Registry unchanged | ✅ 11 entries (post-Wave 0) |
| Skills unchanged | ✅ 0 SKILL.md modifications |
| No PII | ✅ |
| Git diff | ✅ Only this new file |
| Decision issued | ✅ READY FOR WAVE 1 DRY RUN |

---

> **Phase:** A.1.0 — Wave 1 Duplicate Merge Assessment
> **Status:** ✅ COMPLETE
> **Decision:** 🟢 READY FOR WAVE 1 DRY RUN
> **Merge Groups:** 3 (8 skills → 3 canonical)
> **C.3 Namespace Correction:** Applied — project identity preserved
> **Next:** Phase A.1.1 — Wave 1 Dry Run (awaiting authorization)
