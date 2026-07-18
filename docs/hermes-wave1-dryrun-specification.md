# Hermes Wave 1 — Duplicate Merge Dry Run Specification

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T06:50:00Z
**Phase:** A.1.1 — Wave 1 Dry Run Specification
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Define isolated dry-run procedure to validate Wave 1 merges before touching production

**Governance Authority:**
- Wave 1 Duplicate Merge Assessment v1.0 (A.1.0)
- Wave 0 Dry Run Protocol v1.0 (C.2 — pattern reference)
- Validation Specification v1.0 (B.4)
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions (completed):**
- Wave 0: ✅ SUCCESS — Registry 15→11 entries
- Wave 1 Assessment: ✅ 3 merge groups identified (8 skills → 3 canonical)
- Registry current state: 11 entries (post-Wave 0)
- Skill files: 147 SKILL.md — all unchanged

**This document does NOT:**
- Modify the Registry
- Modify any SKILL.md
- Execute any merge
- Move or delete files

---

## 1. Dry Run Objective

### 1.1 Purpose

The Wave 1 Dry Run answers three questions:

> **1. "If we merge these 8 skills into 3 canonical skills, will any capability be lost?"**
>
> **2. "Will deprecated aliases correctly redirect to the canonical skill?"**
>
> **3. "Does the merge respect C.3 namespace boundaries (project identity preserved)?**

### 1.2 Dry Run ≠ Merge

| Dry Run | Real Merge |
|:-----|:-----|
| Simulated canonical SKILL.md files in `/tmp/` | Real canonical SKILL.md files in `~/.hermes/skills/` |
| Simulated alias map in `/tmp/` | Real Registry entries updated |
| Original files UNTOUCHED | Original SKILL.md files RETAINED (never deleted) |
| Rollback: delete `/tmp/` | Rollback: restore registry + remove canonical file |
| Pass: proceed to execution | Pass: complete |

### 1.3 Success Criteria

```
Wave 1 Dry Run is SUCCESSFUL when:

  ✅ All 12 equivalence tests pass
  ✅ All 5 deprecated aliases resolve correctly
  ✅ 0 capability loss detected
  ✅ 0 namespace violations detected
  ✅ Rollback simulation restores original state (0-diff)
  ✅ All 3 canonical skills contain complete merged content
```

---

## 2. Test Environment

### 2.1 Isolation Model

```
Production                          Dry Run (Shadow)
─────────────────────────────────────────────────────────────
~/.hermes/skills/                   /tmp/hermes-wave1-dryrun/skills/       (copy)
skill-registry.json (11 entries)    /tmp/hermes-wave1-dryrun/registry.baseline.json
—                                   /tmp/hermes-wave1-dryrun/registry.simulated.json
—                                   /tmp/hermes-wave1-dryrun/canonical/    (3 new SKILL.md)
—                                   /tmp/hermes-wave1-dryrun/aliases/      (5 alias files)
—                                   /tmp/hermes-wave1-dryrun/report/       (test results)
```

### 2.2 Environment Setup

```
Step 1: Create shadow directory
  mkdir -p /tmp/hermes-wave1-dryrun/{skills,canonical,aliases,report}

Step 2: Copy current production state (post-Wave 0)
  cp -r ~/.hermes/skills/ /tmp/hermes-wave1-dryrun/skills/
  cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
     /tmp/hermes-wave1-dryrun/registry.baseline.json

Step 3: Create simulated post-merge registry
  cp /tmp/hermes-wave1-dryrun/registry.baseline.json \
     /tmp/hermes-wave1-dryrun/registry.simulated.json

Step 4: Verify isolation
  diff /tmp/hermes-wave1-dryrun/registry.simulated.json \
       ~/.hermes/skills/devops/skill-manager/references/skill-registry.json
  → MUST show 0 differences (dry run starts from identical state)
```

### 2.3 Content Snapshot

```
Source skill SHA-256 fingerprints (pre-merge):

  Group 1:
    a3-multi-agent-pipeline           SHA: <verify at dry run time>
    a3-agent-team-pipeline            SHA: <verify at dry run time>
    a3-multi-agent-content-pipeline   SHA: <verify at dry run time>

  Group 2:
    content-review-pipeline           SHA: <verify at dry run time>
    content-review-gate               SHA: <verify at dry run time>
    review-gate-pipeline              SHA: <verify at dry run time>

  Group 3:
    paper-report-writing              SHA: <verify at dry run time>
    research-paper-writing            SHA: <verify at dry run time>
```

---

## 3. Merge Simulation Matrix

### 3.1 Group 1 — project.a3.workflow

```
Source Skills (3):
  ├── a3-multi-agent-pipeline          ← canonical candidate
  ├── a3-agent-team-pipeline           ← absorbed
  └── a3-multi-agent-content-pipeline  ← absorbed

Canonical Skill:
  Path:   /tmp/hermes-wave1-dryrun/canonical/a3-multi-agent-pipeline.SKILL.md
  Name:   a3-multi-agent-pipeline
  Namespace: project.a3.workflow
  Scope:  project

Content Merge:
  Base:   a3-multi-agent-pipeline/SKILL.md (most comprehensive)
  Merge:  a3-agent-team-pipeline/SKILL.md → agent team routing sections
  Merge:  a3-multi-agent-content-pipeline/SKILL.md → content generation sections

Absorbed Skills (2):
  ├── a3-agent-team-pipeline           → alias → canonical
  └── a3-multi-agent-content-pipeline  → alias → canonical

Alias Mapping:
  a3-agent-team-pipeline            → replaced_by: project.a3.workflow/a3-multi-agent-pipeline
  a3-multi-agent-content-pipeline   → replaced_by: project.a3.workflow/a3-multi-agent-pipeline

Expected Result:
  - Canonical contains ALL unique content from all 3 sources
  - No A3-specific content removed (project identity preserved)
  - Trigger patterns merged (union of all 3 trigger sets)
  - Namespace: project.a3.workflow (NOT genericized)
```

### 3.2 Group 2 — adapter.review.pipeline

```
Source Skills (3):
  ├── content-review-pipeline          ← canonical candidate
  ├── content-review-gate             ← absorbed
  └── review-gate-pipeline            ← absorbed

Canonical Skill:
  Path:   /tmp/hermes-wave1-dryrun/canonical/content-review-pipeline.SKILL.md
  Name:   content-review-pipeline
  Namespace: adapter.review.pipeline
  Scope:  adapter

Content Merge:
  Base:   content-review-pipeline/SKILL.md (pipeline orchestration)
  Merge:  content-review-gate/SKILL.md → AST static audit + pytest validation
  Merge:  review-gate-pipeline/SKILL.md → user simulation + hot-fix loop

Absorbed Skills (2):
  ├── content-review-gate             → alias → canonical
  └── review-gate-pipeline            → alias → canonical

Alias Mapping:
  content-review-gate    → replaced_by: adapter.review.pipeline/content-review-pipeline
  review-gate-pipeline   → replaced_by: adapter.review.pipeline/content-review-pipeline

Expected Result:
  - Canonical contains all three review layers in one skill
  - AST audit, user simulation, and pipeline orchestration all present
  - Adapter-neutral — no project-specific paths or references
  - Trigger patterns merged (union of all 3 trigger sets)
```

### 3.3 Group 3 — adapter.writing.academic

```
Source Skills (2):
  ├── paper-report-writing             ← absorbed
  └── research-paper-writing           ← absorbed

Canonical Skill:
  Path:   /tmp/hermes-wave1-dryrun/canonical/academic-writing.SKILL.md
  Name:   academic-writing
  Namespace: adapter.writing.academic
  Scope:  adapter

Content Merge:
  Merge:  paper-report-writing/SKILL.md → Feynman research agent integration
  Merge:  research-paper-writing/SKILL.md → multi-agent writing workflow
  Note:   No single "base" — both are equally important; canonical is new

Absorbed Skills (2):
  ├── paper-report-writing    → alias → canonical
  └── research-paper-writing  → alias → canonical

Alias Mapping:
  paper-report-writing    → replaced_by: adapter.writing.academic/academic-writing
  research-paper-writing  → replaced_by: adapter.writing.academic/academic-writing

Expected Result:
  - Canonical combines both writing methodologies
  - Feynman research agent + multi-agent workflow both present
  - Adapter-neutral — no project-specific paths
  - Trigger patterns merged (union of both trigger sets)
```

---

## 4. Equivalence Test Plan

### 4.1 Test Matrix — 12 Tests Total

| # | Test ID | Group | Type | Description |
|:--|:-----|:----:|:-----|:-----|
| T1 | G1-CAP | 1 | Capability | Canonical contains all unique content from 3 sources |
| T2 | G1-TRIG | 1 | Trigger | All trigger patterns from 3 sources available in canonical |
| T3 | G1-DEP | 1 | Dependency | Deprecated aliases resolve to canonical |
| T4 | G1-ROLL | 1 | Rollback | Restore → original 3 skills independently loadable |
| T5 | G2-CAP | 2 | Capability | Canonical contains AST + user-sim + pipeline content |
| T6 | G2-TRIG | 2 | Trigger | All trigger patterns from 3 sources available in canonical |
| T7 | G2-DEP | 2 | Dependency | Deprecated aliases resolve to canonical |
| T8 | G2-ROLL | 2 | Rollback | Restore → original 3 skills independently loadable |
| T9 | G3-CAP | 3 | Capability | Canonical contains Feynman + multi-agent writing content |
| T10 | G3-TRIG | 3 | Trigger | All trigger patterns from both sources available |
| T11 | G3-DEP | 3 | Dependency | Deprecated aliases resolve to canonical |
| T12 | G3-ROLL | 3 | Rollback | Restore → original 2 skills independently loadable |

### 4.2 Per-Group Test Details

#### Group 1 — project.a3.workflow (Tests T1-T4)

**T1 — Capability Test (G1-CAP)**

| Field | Value |
|:-----|:-----|
| **Pre-condition** | 3 source SKILL.md files accessible |
| **Action** | Read canonical SKILL.md at `/tmp/hermes-wave1-dryrun/canonical/a3-multi-agent-pipeline.SKILL.md` |
| **Expected** | All unique sections from all 3 sources present. Agent team routing from `a3-agent-team-pipeline`. Content generation from `a3-multi-agent-content-pipeline`. Multi-agent orchestration from `a3-multi-agent-pipeline`. |
| **Pass Condition** | Content coverage ≥ 100% (every unique section from all 3 sources found in canonical). 0 sections lost. |
| **Failure** | Any unique section from a source skill is missing from canonical |

**T2 — Trigger Resolution Test (G1-TRIG)**

| Field | Value |
|:-----|:-----|
| **Pre-condition** | Trigger patterns extracted from all 3 source skills |
| **Action** | Extract trigger patterns from canonical. Compare with union of source triggers. |
| **Expected** | Canonical triggers = union of all 3 source trigger sets. No trigger lost. |
| **Pass Condition** | 100% trigger coverage |
| **Failure** | Any source trigger pattern not present in canonical |

**T3 — Dependency/Alias Test (G1-DEP)**

| Field | Value |
|:-----|:-----|
| **Pre-condition** | Alias map: `a3-agent-team-pipeline` → canonical, `a3-multi-agent-content-pipeline` → canonical |
| **Action** | Simulate `skill_view('a3-agent-team-pipeline')` → check alias resolution → load canonical |
| **Expected** | Alias resolves to `project.a3.workflow/a3-multi-agent-pipeline`. Canonical loads successfully. |
| **Pass Condition** | Both aliases resolve with deprecation warning; canonical content loaded |
| **Failure** | Alias returns 404 or loads wrong content |

**T4 — Rollback Test (G1-ROLL)**

| Field | Value |
|:-----|:-----|
| **Pre-condition** | Canonical + aliases active in simulated state |
| **Action** | Remove canonical SKILL.md. Remove aliases. Restore original 3 skills. |
| **Expected** | All 3 original skills load independently. No capability loss. |
| **Pass Condition** | Original skills load; content matches pre-merge SHA-256 |
| **Failure** | Any original skill fails to load or content differs |

#### Group 2 — adapter.review.pipeline (Tests T5-T8)

**T5 — Capability Test (G2-CAP)**

| Field | Value |
|:-----|:-----|
| **Pre-condition** | 3 source SKILL.md files accessible |
| **Action** | Read canonical at `/tmp/hermes-wave1-dryrun/canonical/content-review-pipeline.SKILL.md` |
| **Expected** | AST static audit + pytest validation from `content-review-gate`. User simulation + hot-fix loop from `review-gate-pipeline`. Pipeline orchestration from `content-review-pipeline`. |
| **Pass Condition** | All review gate layers present in canonical |
| **Failure** | Any review layer missing |

**T6 — Trigger Resolution Test (G2-TRIG)**

| Field | Value |
|:-----|:-----|
| **Action** | Extract triggers from canonical. Compare with union of 3 source triggers. |
| **Expected** | 100% trigger coverage |
| **Pass Condition** | No trigger lost |

**T7 — Dependency/Alias Test (G2-DEP)**

| Field | Value |
|:-----|:-----|
| **Action** | Simulate `skill_view('content-review-gate')` → alias → canonical |
| **Expected** | Alias resolves with deprecation warning |
| **Pass Condition** | Both aliases resolve correctly |

**T8 — Rollback Test (G2-ROLL)**

| Field | Value |
|:-----|:-----|
| **Action** | Remove canonical. Restore original 3. |
| **Expected** | All 3 original skills load independently |
| **Pass Condition** | Content matches pre-merge SHA-256 |

#### Group 3 — adapter.writing.academic (Tests T9-T12)

**T9 — Capability Test (G3-CAP)**

| Field | Value |
|:-----|:-----|
| **Pre-condition** | 2 source SKILL.md files accessible |
| **Action** | Read canonical at `/tmp/hermes-wave1-dryrun/canonical/academic-writing.SKILL.md` |
| **Expected** | Feynman research agent integration from `paper-report-writing`. Multi-agent writing workflow from `research-paper-writing`. |
| **Pass Condition** | Both writing methodologies present in canonical |
| **Failure** | Either methodology missing |

**T10 — Trigger Resolution Test (G3-TRIG)**

| Field | Value |
|:-----|:-----|
| **Action** | Extract triggers from canonical. Compare with union of 2 source triggers. |
| **Expected** | 100% trigger coverage |
| **Pass Condition** | No trigger lost |

**T11 — Dependency/Alias Test (G3-DEP)**

| Field | Value |
|:-----|:-----|
| **Action** | Simulate `skill_view('paper-report-writing')` → alias → canonical |
| **Expected** | Both aliases resolve correctly |
| **Pass Condition** | Deprecation warning; canonical loads |

**T12 — Rollback Test (G3-ROLL)**

| Field | Value |
|:-----|:-----|
| **Action** | Remove canonical. Restore original 2. |
| **Expected** | Both original skills load independently |
| **Pass Condition** | Content matches pre-merge SHA-256 |

---

## 5. Namespace Validation

### 5.1 Per-Group Namespace Checks

| Group | Check | Expected | Method |
|:-----|:-----|:-----|:-----|
| **G1** | Canonical namespace = `project.a3.workflow` | `project.a3.*` — project identity preserved | Verify namespace prefix in simulated registry |
| **G1** | No A3 content in adapter namespace | A3 content stays in `project.a3` | Search canonical for project reference location |
| **G2** | Canonical namespace = `adapter.review.pipeline` | `adapter.*` — project-neutral | Verify namespace prefix |
| **G2** | No project paths in canonical body | 0 project-specific paths | Body scan for `~/A3-*`, `~/Veritas-*` |
| **G3** | Canonical namespace = `adapter.writing.academic` | `adapter.*` — project-neutral | Verify namespace prefix |
| **G3** | No project paths in canonical body | 0 project-specific paths | Body scan |

### 5.2 Cross-Group Namespace Violation Check

```
Check: Does Group 1 canonical (project.a3.workflow) depend on Group 2/3 canonicalls (adapter.*)?
  Expected: Allowed ✅ — Project → Adapter dependency is valid

Check: Does Group 2 canonical (adapter.review) depend on Group 1 canonical (project.a3)?
  Expected: PROHIBITED ❌ — Adapter → Project is forbidden

Check: Do any 2 canonicalls have the same namespace?
  Expected: No — all 3 have unique namespaces
```

### 5.3 Alias Namespace Integrity

```
Check: Does a3-agent-team-pipeline alias change the namespace?
  Expected: No — alias only redirects; namespace is set on canonical

Check: Do deprecated aliases have a valid replaced_by path?
  Expected: All 5 aliases point to existing canonical namespaces

Check: Can aliases be resolved without namespace confusion?
  Expected: a3-agent-team-pipeline → project.a3.workflow (same project)
           content-review-gate → adapter.review.pipeline (same domain)
```

---

## 6. Failure Conditions

### 6.1 BLOCK Conditions — Halt Dry Run

| # | Condition | Test | Severity |
|:--|:-----|:----:|:----:|
| **B1** | **Capability Loss** — Any unique content section from a source skill is missing from canonical | T1, T5, T9 | **CRITICAL** |
| **B2** | **Broken Alias** — Any deprecated alias returns 404 or loads wrong content | T3, T7, T11 | **CRITICAL** |
| **B3** | **Namespace Violation** — Project identity leaks into adapter/core namespace | §5 checks | **CRITICAL** |
| **B4** | **Adapter-Pollution** — Adapter canonical contains project-specific paths | §5 checks | **CRITICAL** |
| **B5** | **Content Divergence** — Canonical content differs from source content after merge | T1, T5, T9 | **CRITICAL** |
| **B6** | **Rollback Failure** — Original skills cannot be restored after simulated merge | T4, T8, T12 | **CRITICAL** |

### 6.2 WARNING Conditions — Proceed with Caution

| # | Condition | Test | Severity |
|:--|:-----|:----:|:----:|
| **W1** | **Duplicate Metadata** — Canonical has conflicting version/owner from merged skills | All CAP | MEDIUM |
| **W2** | **Unclear Ownership** — Canonical ownership ambiguous between merged skills | All CAP | MEDIUM |
| **W3** | **Trigger Overlap** — Merged triggers conflict (same trigger → different behaviors) | All TRIG | LOW |
| **W4** | **Excessive Canonical Size** — Merged SKILL.md is 3x+ the size of largest source | All CAP | LOW |

---

## 7. Rollback Simulation

### 7.1 Simulated Rollback Procedure

```
Trigger: Any Critical Failure (B1-B6) detected during dry run

Step 1: STOP all dry run tests immediately

Step 2: Remove canonical SKILL.md files
  rm /tmp/hermes-wave1-dryrun/canonical/*.SKILL.md

Step 3: Remove alias entries from simulated registry
  (aliases were only in simulated state — discard)

Step 4: Restore simulated registry from baseline
  cp /tmp/hermes-wave1-dryrun/registry.baseline.json \
     /tmp/hermes-wave1-dryrun/registry.simulated.json

Step 5: Verify restoration — 0 differences from baseline
  diff /tmp/hermes-wave1-dryrun/registry.baseline.json \
       /tmp/hermes-wave1-dryrun/registry.simulated.json

Step 6: Re-run failing test against original skills
  → Test should now PASS (confirms rollback works)

Step 7: Record failure in dry run report
  - Which test failed
  - What was expected
  - What was observed
  - Was rollback successful
```

### 7.2 Per-Group Rollback Verification

| Group | Rollback Action | Verification | Test |
|:-----|:-----|:-----|:----:|
| G1 | Remove canonical + aliases → restore 3 originals | All 3 originals load independently | T4 |
| G2 | Remove canonical + aliases → restore 3 originals | All 3 originals load independently | T8 |
| G3 | Remove canonical + aliases → restore 2 originals | Both originals load independently | T12 |

---

## 8. Human Approval Gate

### 8.1 Pre-Dry-Run Approval

```
☐ Governance Reviewer confirms:

  ☐ Dry run environment isolated from production (/tmp/hermes-wave1-dryrun/)
  ☐ All 8 source skills accessible and content-verified
  ☐ 3 merge groups correctly identified per A.1.0 assessment
  ☐ C.3 namespace model applied (Group 1 preserves project identity)
  ☐ Migration Operator designated
  ☐ Validator designated
```

### 8.2 Post-Dry-Run Approval

```
☐ Governance Reviewer confirms:

  ☐ All 12 equivalence tests PASS
  ☐ 0 Critical Failures (B1-B6)
  ☐ All 5 deprecated aliases resolve correctly
  ☐ Rollback simulation completed successfully (0-diff restore)
  ☐ Namespace validation passed (0 violations)
  ☐ 0 capability loss detected
  ☐ Dry run report produced
```

### 8.3 Decision After Dry Run

```
☐ Wave 1 Cleared — Proceed to Wave 1 execution
☐ Wave 1 Cleared with Warnings — (list warnings, proceed)
☐ Wave 1 BLOCKED — (list critical failures, return to assessment)
```

---

## 9. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   WAVE 1 — DUPLICATE MERGE DRY RUN SPECIFICATION              ║
║                                                              ║
║   3 merge groups specified                                    ║
║   12 equivalence tests defined (4 per group)                  ║
║   6 Critical failure conditions (B1-B6)                       ║
║   4 Warning conditions (W1-W4)                                ║
║   3 per-group rollback procedures                             ║
║                                                              ║
║   Dry run environment: /tmp/hermes-wave1-dryrun/              ║
║   Production: untouched (0 Registry changes, 0 Skill changes) ║
║                                                              ║
║   🟢 READY FOR WAVE 1 EXECUTION                              ║
║                                                              ║
║   Pre-condition: §8 Pre-Dry-Run Approval completed            ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-wave1-dryrun-specification.md` |
| 9 chapters complete | ✅ §1-9 |
| 3 merge groups specified | ✅ With namespace + content merge plan |
| 12 equivalence tests defined | ✅ 4 per group: CAP, TRIG, DEP, ROLL |
| 6 BLOCK conditions | ✅ B1-B6 with severity |
| 4 WARNING conditions | ✅ W1-W4 |
| Rollback simulation | ✅ §7 — per-group + full |
| Namespace validation | ✅ §5 — per-group + cross-group + alias |
| 0 executable code | ✅ Pure specification |
| Registry unchanged | ✅ 11 entries (post-Wave 0) |
| Skills unchanged | ✅ 0 modifications |
| No PII | ✅ |
| Git diff | ✅ Only this new file |

---

> **Phase:** A.1.1 — Wave 1 Dry Run Specification
> **Status:** ✅ COMPLETE
> **Decision:** 🟢 READY FOR WAVE 1 EXECUTION
> **Tests:** 12 defined (4 per merge group)
> **Next:** Phase A.1.2 — Wave 1 Dry Run Execution (awaiting authorization)
