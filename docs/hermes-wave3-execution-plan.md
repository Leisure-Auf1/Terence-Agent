# Hermes Wave 3 — Metadata Completion Execution Plan

**Status:** Phase A.3.3 — Execution Plan Complete · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T08:15:00Z
**Phase:** A.3.3 — Wave 3 Execution Plan
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Define exact procedure for production metadata backfill of 148 skills

**Governance Authority:**
- Wave 3 Metadata Completion Assessment v1.0 (A.3.0)
- Wave 3 Dry Run Specification v1.0 (A.3.1)
- Wave 3 Dry Run Result v1.0 (A.3.2) — 25/25 PASS
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions (completed):**
- Wave 0: ✅ Registry 15→11
- Wave 1: ✅ 8→3 canonical + 6 aliases
- Wave 2: ✅ 148 skills namespace-mapped
- Wave 3 Dry Run: ✅ 25/25 PASS

**This document does NOT:**
- Execute production backfill
- Modify files now
- Change runtime behavior

---

## 1. Execution Objective

### 1.1 What Wave 3 Does

```
Wave 3 = Production Metadata Backfill

  MODIFY: 148 SKILL.md frontmatter blocks
    + version  (55 skills — where missing)
    + owner    (65 skills — where missing)
    + lifecycle (147 skills — where implicit)
    + status   (148 skills — where implicit)

  PRESERVE:
    ✅ All existing frontmatter values (91 versions, 83 owners)
    ✅ All SKILL.md body content (SHA-256 verified)
    ✅ All namespace/scope/ownership assignments (Wave 2)
    ✅ Registry (0 changes — deferred to Wave 4)

  DO NOT:
    ❌ Modify body content
    ❌ Rename skills
    ❌ Move files
    ❌ Delete files
    ❌ Change namespaces
```

### 1.2 Target State

```
BEFORE:  148 skills with incomplete metadata
          93 have version, 83 have owner, 1 explicit lifecycle

AFTER:   148 skills with complete Phase B metadata
          148 have version, 148 have owner, 148 have lifecycle, 148 have status
```

---

## 2. Pre-Execution Backup

### 2.1 Snapshot Plan

```
Step 1: Create snapshot directory
  mkdir -p /tmp/hermes-wave3-snapshots/{registry,skills,inventory}

Step 2: Registry backup
  cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
     /tmp/hermes-wave3-snapshots/registry/registry.backup.json
  sha256sum → record fingerprint

Step 3: SHA-256 all 148 SKILL.md (frontmatter + body)
  For each skill: sha256sum → /tmp/hermes-wave3-snapshots/inventory/pre-backfill-sha256.txt
  For each skill: extract body SHA-256 → /tmp/hermes-wave3-snapshots/inventory/pre-backfill-body-sha256.txt

Step 4: Metadata baseline
  For each skill: record current version/owner/lifecycle/status
  → /tmp/hermes-wave3-snapshots/inventory/metadata-baseline.json

Step 5: Verify all 148 skills accessible
  For each: test -f <path>/SKILL.md → MUST be YES
```

---

## 3. Migration Matrix

### 3.1 Per-Scope Backfill Summary

| Scope | Skills | Version Backfill | Owner Backfill | Lifecycle | Status |
|:-----|:----:|:----:|:----:|:-----|:-----|
| **Core tier 0** | 6 | 6 → `1.0.0` | 6 → `hermes-governance` | `active` | `ok` |
| **Core tier 1** | 8 | 7 → `1.0.0` | 7 → `hermes-platform` | `active` | `ok` |
| **Adapter** | 122 | ~35 → `1.0.0` | ~43 → `hermes-platform` | `active` | `ok` |
| **Project A3** | 7 | 5 → `1.0.0` / `3.6.0` | 5 → `a3-team` | `active` / `deprecated` | `ok` / `grace_period` |
| **Project Veritas** | 1 | 1 → `1.0.0` | 1 → `veritas-team` | `active` | `ok` |
| **Project UCampus** | 4 | 4 → `1.0.0` | 4 → `ucampus-team` | `active` | `ok` |

### 3.2 Core Skills — Detail

| Skill | Tier | Version | Owner | Lifecycle | Status |
|:-----|:----:|:-----|:-----|:-----|:----:|
| `agent-governance-protocol` | 0 | `1.0.0` | `hermes-governance` | `active` | `ok` |
| `architecture-constraints` | 0 | `1.0.0` | `hermes-governance` | `active` | `ok` |
| `error-registry` | 0 | `1.0.0` | `hermes-governance` | `active` | `ok` |
| `task-progress` | 0 | `1.0.0` | `hermes-governance` | `active` | `ok` |
| `skill-ecosystem-audit` | 0 | `1.0.0` | `hermes-governance` | `active` | `ok` |
| `guidance-agent` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `skill-manager` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `harness-preflight` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `agent-logger` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `agent-debugger` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `agent-developer` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `agent-executor` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `coding-agent-orchestration` | 1 | `1.0.0` | `hermes-platform` | `active` | `ok` |
| `webhook-subscriptions` | 1 | preserve `1.1.0` | `hermes-platform` | preserve | `ok` |

### 3.3 Project Skills — Detail

| Skill | Namespace | Version | Owner | Lifecycle | Status |
|:-----|:-----|:-----|:-----|:-----|:----:|
| `a3-multi-agent-pipeline` | `project.a3.workflow` | `3.6.0` | `a3-team` | `active` | `ok` |
| `a3-agent-team-pipeline` | `project.a3.workflow` | `1.0.0` | `a3-team` | `deprecated` | `grace_period` |
| `a3-multi-agent-content-pipeline` | `project.a3.workflow` | `1.0.0` | `a3-team` | `deprecated` | `grace_period` |
| `a3-content-pipeline` | `project.a3.pipeline` | `1.0.0` | `a3-team` | `active` | `ok` |
| `a3-runtime-infrastructure` | `project.a3.infrastructure` | `1.0.0` | `a3-team` | `active` | `ok` |
| `acp-coding-agent` | `project.a3.coding` | preserve | preserve | `active` | `ok` |
| `kanban-codex-lane` | `project.a3.kanban` | preserve | preserve | `active` | `ok` |
| `veritas-core` | `project.veritas.core` | `1.0.0` | `veritas-team` | `active` | `ok` |
| `ucampus-auto-complete` | `project.ucampus.automation` | `1.0.0` | `ucampus-team` | `active` | `ok` |
| `u-campus-course-automation` | `project.ucampus.course` | `1.0.0` | `ucampus-team` | `active` | `ok` |
| `chaoxing-homework` | `project.ucampus.chaoxing` | `1.0.0` | `ucampus-team` | `active` | `ok` |
| `lab-report-execution` | `project.ucampus.lab` | `1.0.0` | `ucampus-team` | `active` | `ok` |

### 3.4 Adapter Skills — Summary

```
122 adapter skills:
  Version:   preserve 80 existing; backfill ~35 → "1.0.0"
  Owner:     preserve 69 existing; backfill ~43 → "hermes-platform"
  Lifecycle: set all 122 → "active" (unless deprecated alias)
  Status:    set all 122 → "ok" (except aliases → "grace_period")

Wave 1 aliases in adapter: content-review-gate, review-gate-pipeline,
                           paper-report-writing, research-paper-writing
  → lifecycle: deprecated, status: grace_period
```

---

## 4. Execution Procedure

### 4.1 Ordered Steps

```
Step 1: PRE-EXECUTION BACKUP (§2)
  ☐ Create snapshot directory
  ☐ Backup registry
  ☐ SHA-256 all 148 SKILL.md (frontmatter + body separately)
  ☐ Record metadata baseline
  ☐ Human Reviewer signs Wave 3 approval

Step 2: CORE SKILLS (14 skills — HIGH priority)
  ☐ Backfill version/owner/lifecycle/status for 14 core skills
  ☐ Verify: all 14 have version/owner/lifecycle/status
  ☐ Verify: body SHA-256 unchanged for all 14
  ☐ Verify: 0 project owners assigned to core
  → HALT on failure; rollback Step 2 only

Step 3: PROJECT SKILLS (12 skills — HIGH priority)
  ☐ Backfill version/owner/lifecycle/status for 12 project skills
  ☐ Verify: all 12 have version/owner/lifecycle/status
  ☐ Verify: body SHA-256 unchanged for all 12
  ☐ Verify: project identity preserved (A3, Veritas, UCampus)
  → HALT on failure; rollback Step 3 only

Step 4: REGISTERED ADAPTER SKILLS (9 skills — MEDIUM priority)
  ☐ Backfill for 9 skills currently in Registry
  ☐ Verify: all 9 have version/owner/lifecycle/status
  ☐ Verify: body SHA-256 unchanged
  → HALT on failure; rollback Step 4 only

Step 5: REMAINING ADAPTER SKILLS (~113 skills — LOW priority)
  ☐ Batch backfill for remaining adapter skills
  ☐ Process in groups of 20; verify after each group
  ☐ Verify: all have version/owner/lifecycle/status
  ☐ Verify: body SHA-256 unchanged for all
  → HALT on failure; rollback Step 5 only

Step 6: POST-EXECUTION VALIDATION (§5)
  ☐ Run 6-gate validation
  ☐ All gates must PASS before Wave 3 complete
```

### 4.2 Backfill Algorithm (Per Skill)

```
For each SKILL.md file:
  1. Read entire file
  2. Parse YAML frontmatter (between --- delimiters)
  3. If no frontmatter exists: create one
  4. Apply rules:
     a. version: if missing → assign per §3 matrix
     b. owner:   if missing → assign per §3 matrix
     c. lifecycle: if missing or implicit → assign per §3 matrix
     d. status: if missing → assign per §3 matrix
  5. Preserve: ALL existing frontmatter keys not being backfilled
  6. Reconstruct: new frontmatter + original body
  7. Write back to file
  8. Verify: body SHA-256 == pre-backfill body SHA-256
```

### 4.3 Special Cases

| Skill | Special Handling |
|:-----|:-----|
| `webhook-subscriptions` | Has explicit lifecycle — preserve |
| `acp-coding-agent` | Has version + owner — preserve |
| `kanban-codex-lane` | Has version + owner — preserve |
| `academic-writing` | Correct `status: active` → `status: ok` |
| 6 Wave 1 aliases | `lifecycle: deprecated`, `status: grace_period` |
| `a3-multi-agent-pipeline` | Version `3.6.0` (not default 1.0.0) |

---

## 5. Validation Gates

### 5.1 Six-Gate Validation

| Gate | Name | What It Checks | Method |
|:----:|:-----|:-----|:-----|
| **G1** | Metadata Completeness | 148/148 have version, owner, lifecycle, status | Field presence scan |
| **G2** | Namespace Consistency | Scope matches namespace prefix | Cross-field validation |
| **G3** | Ownership Correctness | Owner matches namespace-model tier | Owner-tier cross-check |
| **G4** | Registry v1.1 Compatibility | All required fields present | Schema validation |
| **G5** | Runtime Safety | Hermes session active; no dispatch regression | Session health check |
| **G6** | Rollback Verification | Full restore produces 0-diff | SHA-256 comparison |

### 5.2 Gate Pass Criteria

```
All 6 gates must PASS:
  [ ] G1 — 148/148 have version, owner, lifecycle, status
  [ ] G2 — 0 namespace-scope mismatches
  [ ] G3 — 0 owner-tier mismatches
  [ ] G4 — 0 missing required v1.1 fields
  [ ] G5 — Session active, skills discoverable
  [ ] G6 — Rollback 0-diff confirmed
```

---

## 6. Rollback Procedure

### 6.1 Rollback Triggers

| # | Condition | Severity | Action |
|:--|:-----|:----:|:-----|
| R1 | Body content modified (SHA-256 mismatch) | **CRITICAL** | HALT — full rollback |
| R2 | Wrong owner assigned to core skill | **CRITICAL** | HALT — full rollback |
| R3 | Existing metadata overwritten | **HIGH** | HALT — scope rollback |
| R4 | File corrupted (unreadable after write) | **CRITICAL** | HALT — full rollback |
| R5 | Gate G1-G4 failure | **HIGH** | HALT — scope rollback |

### 6.2 Rollback Commands

```bash
# Full rollback — restore all 148 SKILL.md from pre-execution backups
cp -r /tmp/hermes-wave3-snapshots/skills-backup/* ~/.hermes/skills/

# Scope rollback — restore only one scope
cp -r /tmp/hermes-wave3-snapshots/skills-backup/devops/* ~/.hermes/skills/devops/
# (repeat for each affected category)

# Verify
sha256sum all 148 SKILL.md → compare with pre-backfill inventory
```

### 6.3 Rollback Authority

| Who | Can Trigger | Can Execute | Status |
|:-----|:----:|:----:|:-----|
| Governance Reviewer | ✅ | ❌ | Pending |
| Migration Operator | ✅ | ✅ | Ready |
| Validator | ✅ (on failure) | ❌ | Ready |

---

## 7. Risk Assessment

### 7.1 BLOCK Conditions

| # | Risk | Severity | Mitigation |
|:--|:-----|:----:|:-----|
| B1 | Body content modified during backfill | CRITICAL | BF-006 in dry run; SHA-256 verify per skill |
| B2 | Core skill gets project owner | CRITICAL | NS-003 gate; halt on detection |
| B3 | File write error corrupts SKILL.md | CRITICAL | Write-then-verify pattern; backup before each scope |
| B4 | Existing metadata accidentally overwritten | HIGH | Rule: only backfill MISSING fields; dry run BF-001 verified |
| B5 | Registry modified (outside Wave 3 scope) | HIGH | Registry backup verified; 0 changes to skill-registry.json |

### 7.2 WARNING Conditions

| # | Risk | Severity | Mitigation |
|:--|:-----|:----:|:-----|
| W1 | 148 file writes — high volume | MEDIUM | Batch processing (20 per group); verify after each |
| W2 | `academic-writing` status correction | LOW | Single known fix; documented in dry run |
| W3 | 57 skills get default version 1.0.0 | LOW | Acceptable; version reflects governance maturity |

---

## 8. Human Approval Gate

### 8.1 Pre-Execution Approval

```
☐ Governance Reviewer confirms:

  ☐ Pre-execution backup completed (§2)
  ☐ All 148 skills SHA-256 recorded
  ☐ Backfill matrix reviewed (§3)
  ☐ Execution procedure reviewed (§4 — 6 steps)
  ☐ 6 validation gates defined (§5)
  ☐ Rollback procedure verified (§6 — full + per-scope)
  ☐ Risks accepted (§7 — 5 BLOCK, 3 WARNING)
  ☐ Migration Operator designated
  ☐ Validator designated
```

### 8.2 Execution Authorization

```
☐ Governance Reviewer signature:

    "I authorize Wave 3 metadata backfill per this plan.
     Migration Operator may modify 148 SKILL.md frontmatter blocks
     to add version, owner, lifecycle, and status fields.

     Migration Operator may NOT:
       - Modify body content
       - Rename skills
       - Move or delete files
       - Modify the Registry

     Validator shall verify per §5 (6 gates).
     Any critical trigger (§6.1) requires immediate rollback."

  Signature: ________________________    Date: ______________
```

---

## 9. Final Decision

```
🟢 READY FOR HUMAN APPROVAL

  148 skills in scope
  6 execution steps
  6 validation gates
  Full + per-scope rollback
  Dry run: 25/25 PASS
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ |
| 9 sections | ✅ |
| 148 skills in scope | ✅ |
| Core/Adapter/Project matrix | ✅ |
| 6 execution steps | ✅ |
| 6 validation gates | ✅ |
| Rollback (full + per-scope) | ✅ |
| 5 BLOCK + 3 WARNING | ✅ |
| 0 executable code | ✅ |
| Registry unchanged | ✅ |
| Skills unchanged | ✅ |

---

> **Phase:** A.3.3 — Wave 3 Execution Plan
> **Status:** ✅ COMPLETE
> **Decision:** 🟢 READY FOR HUMAN APPROVAL
> **Next:** Human signs §8.2 → Execute §4 → Validate §5 → Wave 3 Complete
