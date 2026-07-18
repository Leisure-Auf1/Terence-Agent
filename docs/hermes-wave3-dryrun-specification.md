# Hermes Wave 3 — Metadata Completion Dry Run Specification

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T08:00:00Z
**Phase:** A.3.1 — Wave 3 Dry Run Specification
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Define isolated dry-run procedure to validate metadata backfill before production execution

**Governance Authority:**
- Wave 3 Metadata Completion Assessment v1.0 (A.3.0)
- Registry Namespace Schema Amendment v1.0 (C.3.1)
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions (completed):**
- Wave 0: ✅ Registry 15→11
- Wave 1: ✅ 8→3 canonical + 6 aliases
- Wave 2: ✅ 148 skills namespace-mapped
- Wave 3 Assessment: ✅ Gaps quantified (57 version, 66 owner, 147 lifecycle)

**This document does NOT:**
- Modify the Registry
- Modify SKILL.md files
- Execute backfill
- Move or delete files

---

## 1. Dry Run Objective

### 1.1 What This Dry Run Answers

> **"If we backfill version, owner, lifecycle, and status into all 148 SKILL.md frontmatter blocks, will any metadata be corrupted, any existing values overwritten, any namespace rules violated, or any governance forbidden state triggered?"**

### 1.2 Dry Run ≠ Backfill

| Dry Run | Real Backfill |
|:-----|:-----|
| Simulated SKILL.md copies in `/tmp/` | Real SKILL.md files modified |
| Registry unchanged | Registry unchanged (Wave 4) |
| 25 tests in isolated environment | 6-gate production validation |
| Rollback: delete `/tmp/` | Rollback: restore from backup |

### 1.3 Success Criteria

```
✅ All 25 tests pass
✅ 0 metadata corruption (existing values preserved)
✅ 0 namespace violations
✅ 0 governance forbidden states triggered
✅ Rollback simulation restores original state
✅ Body content unchanged (SHA-256 verified)
```

---

## 2. Test Environment

### 2.1 Isolation Layout

```
Production                          Dry Run (Shadow)
─────────────────────────────────────────────────────────────────
~/.hermes/skills/                   /tmp/hermes-wave3-dryrun/skills/          (copy)
skill-registry.json (11 entries)    /tmp/hermes-wave3-dryrun/registry.json     (copy)
namespace-map.json                  /tmp/hermes-wave3-dryrun/namespace-map.json
—                                   /tmp/hermes-wave3-dryrun/metadata-report.json
—                                   /tmp/hermes-wave3-dryrun/report/
```

### 2.2 Setup Procedure

```
Step 1: Create shadow directory
  mkdir -p /tmp/hermes-wave3-dryrun/{skills,report}

Step 2: Copy production state
  cp -r ~/.hermes/skills/ /tmp/hermes-wave3-dryrun/skills/
  cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
     /tmp/hermes-wave3-dryrun/registry.json
  cp /tmp/hermes-wave2-snapshots/namespace-map.json \
     /tmp/hermes-wave3-dryrun/namespace-map.json

Step 3: Verify isolation
  diff /tmp/hermes-wave3-dryrun/registry.json \
       ~/.hermes/skills/devops/skill-manager/references/skill-registry.json
  → MUST be 0 differences (environment starts from identical state)
```

---

## 3. Test Matrix — 25 Tests

### 3.1 Overview

| Category | Tests | IDs |
|:-----|:----:|:-----|
| Metadata Completeness | 6 | MC-001 to MC-006 |
| Namespace Consistency | 6 | NS-001 to NS-006 |
| Backfill Simulation | 6 | BF-001 to BF-006 |
| Governance | 4 | GV-001 to GV-004 |
| Rollback | 3 | RB-001 to RB-003 |
| **Total** | **25** | |

---

### 3.2 Metadata Completeness Tests (6)

#### MC-001 — Version Presence

| Field | Value |
|:-----|:-----|
| **Purpose** | All 148 skills have non-empty version field |
| **Input** | All SKILL.md frontmatter blocks |
| **Expected** | 148/148 skills: `version` field present, non-empty, semantic format |
| **Pre-backfill** | 91 have version → 57 need backfill |
| **Post-backfill** | 148/148 have version |
| **Failure** | Any skill with empty/missing version after backfill |

#### MC-002 — Owner Presence

| Field | Value |
|:-----|:-----|
| **Purpose** | All 148 skills have non-empty owner field |
| **Input** | All SKILL.md frontmatter blocks |
| **Expected** | 148/148 skills: `owner` field present, non-empty |
| **Pre-backfill** | 82 have owner → 66 need backfill |
| **Post-backfill** | 148/148 have owner |
| **Failure** | Any skill with empty/missing owner after backfill |

#### MC-003 — Lifecycle Validity

| Field | Value |
|:-----|:-----|
| **Purpose** | All skills have valid lifecycle field |
| **Input** | All SKILL.md frontmatter blocks |
| **Expected** | 148/148: `lifecycle` ∈ {proposed, review, active, deprecated, archived}. Aliases: `deprecated`. Non-aliases: `active`. |
| **Pre-backfill** | 1 explicit, 147 implicit |
| **Post-backfill** | 148/148 explicit |
| **Failure** | Invalid lifecycle value or missing field |

#### MC-004 — Status Validity

| Field | Value |
|:-----|:-----|
| **Purpose** | All skills have valid status field |
| **Input** | All SKILL.md frontmatter blocks |
| **Expected** | 148/148: `status` ∈ {ok, degraded, error, grace_period}. Active: `ok`. Aliases: `grace_period`. |
| **Pre-backfill** | 0 explicit |
| **Post-backfill** | 148/148 explicit |
| **Failure** | Invalid status value or missing field |

#### MC-005 — Version Format

| Field | Value |
|:-----|:-----|
| **Purpose** | All version fields follow semantic versioning |
| **Input** | All version values after backfill |
| **Expected** | All match `^\d+\.\d+\.\d+$` (MAJOR.MINOR.PATCH) |
| **Failure** | Non-semantic version string (e.g., "latest", "v1", "1.0") |

#### MC-006 — No Frontmatter Corruption

| Field | Value |
|:-----|:-----|
| **Purpose** | Backfill does not corrupt existing frontmatter fields |
| **Input** | Diff pre/post backfill for all 148 SKILL.md |
| **Expected** | Only `version`, `owner`, `lifecycle`, `status` changed. All other frontmatter keys unchanged. |
| **Failure** | Any non-target field modified or deleted |

---

### 3.3 Namespace Consistency Tests (6)

#### NS-001 — Namespace ↔ Scope Matching

| Field | Value |
|:-----|:-----|
| **Purpose** | Namespace prefix matches scope value |
| **Input** | All 148 skills: cross-field namespace + scope |
| **Expected** | `hermes.core.*` → scope: core. `adapter.*` → scope: adapter. `project.<id>.*` → scope: project. |
| **Failure** | Mismatch (e.g., `namespace: project.a3.*` with `scope: adapter`) |

#### NS-002 — Ownership Tier ↔ Scope Matching

| Field | Value |
|:-----|:-----|
| **Purpose** | Ownership tier matches scope |
| **Input** | All 148 skills: cross-field ownership.tier + scope |
| **Expected** | core → tier 0 or 1. adapter → tier 1. project → tier 2. |
| **Failure** | Core skill with tier 2 (project ownership) or project skill with tier 0/1 |

#### NS-003 — Core Independence

| Field | Value |
|:-----|:-----|
| **Purpose** | Core skills have no project identifiers in namespace or owner |
| **Input** | All 14 core skills |
| **Expected** | Namespace: `hermes.core.*` (0 `a3`, `veritas`, `ucampus`). Owner: `hermes-governance` or `hermes-platform` (not `a3-team`, etc.) |
| **Failure** | Core skill assigned to project owner or project namespace |

#### NS-004 — Adapter Neutrality

| Field | Value |
|:-----|:-----|
| **Purpose** | Adapter skills have no project identifiers |
| **Input** | All 122 adapter skills |
| **Expected** | Namespace: `adapter.*` (0 project IDs). Owner: `hermes-platform`. 0 project dependencies. |
| **Failure** | Adapter skill with project owner or project namespace |

#### NS-005 — Project Identity Preservation

| Field | Value |
|:-----|:-----|
| **Purpose** | Project skills retain project identity in namespace |
| **Input** | All 12 project skills |
| **Expected** | `a3-*` → `project.a3.*`. `veritas-*` → `project.veritas.*`. `ucampus-*` → `project.ucampus.*`. |
| **Failure** | Project skill assigned to generic or wrong namespace |

#### NS-006 — Owner Consistency with Namespace Model

| Field | Value |
|:-----|:-----|
| **Purpose** | Owner value matches namespace-model tier assignment |
| **Input** | Cross-field: ownership.owner + namespace-model tier |
| **Expected** | Tier 0 → `hermes-governance`. Tier 1 → `hermes-platform`. Tier 2 → project team. |
| **Failure** | Mismatch between tier and owner string |

---

### 3.4 Backfill Simulation Tests (6)

#### BF-001 — Existing Version Preserved

| Field | Value |
|:-----|:-----|
| **Purpose** | Skills that already have a version keep it unchanged |
| **Input** | 91 skills with existing version |
| **Expected** | Post-backfill version == pre-backfill version. 0 overwrites. |
| **Failure** | Any existing version changed by backfill |

#### BF-002 — Missing Version Defaults

| Field | Value |
|:-----|:-----|
| **Purpose** | Skills without version get correct default |
| **Input** | 57 skills with no version |
| **Expected** | All assigned `1.0.0` except `a3-multi-agent-pipeline` → `3.6.0` |
| **Failure** | Wrong default assigned or exception missed |

#### BF-003 — Owner Inference Correctness

| Field | Value |
|:-----|:-----|
| **Purpose** | Inferred owners match namespace-model rules |
| **Input** | 66 skills with no owner |
| **Expected** | Core tier 0 → `hermes-governance`. Core tier 1 → `hermes-platform`. Adapter → `hermes-platform`. Project → team from namespace. |
| **Failure** | Wrong owner assigned to any skill |

#### BF-004 — Lifecycle Assignment Correctness

| Field | Value |
|:-----|:-----|
| **Purpose** | Lifecycle values follow rules |
| **Input** | 147 skills with implicit lifecycle |
| **Expected** | 141 active → `lifecycle: active, status: ok`. 6 aliases → `lifecycle: deprecated, status: grace_period`. |
| **Failure** | Active skill gets deprecated or alias gets active |

#### BF-005 — Alias Deprecated State Preserved

| Field | Value |
|:-----|:-----|
| **Purpose** | Wave 1 aliases retain deprecated state |
| **Input** | 6 Wave 1 alias skills |
| **Expected** | All 6: `lifecycle: deprecated`, `status: grace_period`, `replaced_by` preserved |
| **Failure** | Alias lifecycle changed to active or replaced_by removed |

#### BF-006 — Body Content Unchanged

| Field | Value |
|:-----|:-----|
| **Purpose** | Backfill only modifies frontmatter, never body |
| **Input** | SHA-256 of body text (after `---` frontmatter delimiter) for all 148 skills |
| **Expected** | Pre-backfill body SHA == post-backfill body SHA. 0 body changes. |
| **Failure** | Any body text modified |

---

### 3.5 Governance Tests (4)

#### GV-001 — Registry v1.1 Schema Compatibility

| Field | Value |
|:-----|:-----|
| **Purpose** | Backfilled skills compatible with Registry v1.1 17-field schema |
| **Input** | All 148 skills with v1.1 metadata |
| **Expected** | All required fields (name, version, description, capability, namespace, scope, ownership, lifecycle, status) present. Optional fields null-tolerant. |
| **Failure** | Required field missing or invalid type |

#### GV-002 — No Forbidden States Triggered

| Field | Value |
|:-----|:-----|
| **Purpose** | Backfill does not trigger any F1-F10 forbidden states from C.5 |
| **Input** | All 148 skills + registry |
| **Expected** | F1 (core project logic): 0. F4 (silent replacement): 0. F8 (core→project dep): 0. F9 (no ownership): 0. |
| **Failure** | Any forbidden state triggered |

#### GV-003 — Governance Stack Integrity

| Field | Value |
|:-----|:-----|
| **Purpose** | Constitution v1.0 + Skill Policy v1.0 rules still hold |
| **Input** | Post-backfill metadata + governance rules |
| **Expected** | No governance rule violation. All P1-P7 principles intact. |
| **Failure** | Governance rule broken by backfill |

#### GV-004 — Zero Runtime Behavior Change

| Field | Value |
|:-----|:-----|
| **Purpose** | Backfill is metadata-only — no runtime impact |
| **Input** | Hermes session behavior pre/post backfill |
| **Expected** | Skill discovery unchanged. Dispatch unchanged. Session startup unchanged. |
| **Failure** | Runtime behavior regression |

---

### 3.6 Rollback Tests (3)

#### RB-001 — Full Rollback Restoration

| Field | Value |
|:-----|:-----|
| **Purpose** | Full rollback restores all 148 skills to pre-backfill state |
| **Input** | Restore all SKILL.md from pre-backfill shadow copy |
| **Expected** | SHA-256 all 148 skills match pre-backfill. 0 differences. |
| **Failure** | Any skill differs from pre-backfill after restore |

#### RB-002 — Per-Scope Rollback

| Field | Value |
|:-----|:-----|
| **Purpose** | Each scope can be independently rolled back |
| **Input** | Restore core (14), adapter (122), project (12) independently |
| **Expected** | Rolled-back scope matches pre-backfill. Other scopes retain backfill. |
| **Failure** | Cross-scope contamination during partial rollback |

#### RB-003 — Rollback Verification Time

| Field | Value |
|:-----|:-----|
| **Purpose** | Rollback is fast and reliable |
| **Input** | Execute full rollback |
| **Expected** | <2 seconds (148 file copies). 0 errors. |
| **Failure** | Rollback takes >5 seconds or produces errors |

---

## 4. Dry Run Procedure

### 4.1 Execution Steps

```
Step 1: Snapshot baseline
  → SHA-256 all 148 SKILL.md files (frontmatter + body separately)
  → Record existing metadata state (91 version, 82 owner, 1 lifecycle)

Step 2: Run backfill simulation
  → For each skill: extract frontmatter, add/update version/owner/lifecycle/status
  → Write back to shadow copy
  → Rules: BF-001 through BF-006

Step 3: Run completeness tests (MC-001 to MC-006)
  → Verify all 148 have version, owner, lifecycle, status
  → Verify format, no corruption

Step 4: Run namespace tests (NS-001 to NS-006)
  → Cross-field validation
  → Core independence, adapter neutrality, project identity

Step 5: Run governance tests (GV-001 to GV-004)
  → Schema compatibility, forbidden states, runtime

Step 6: Run rollback simulation (RB-001 to RB-003)
  → Full + per-scope restore

Step 7: Generate dry run report
```

### 4.2 Environment Cleanup

```
After dry run complete:
  Preserve: /tmp/hermes-wave3-dryrun/report/ (audit trail)
  Discard:  /tmp/hermes-wave3-dryrun/skills/ (shadow copies)
```

---

## 5. Failure Conditions

### 5.1 BLOCK Conditions

| # | Condition | Test | Severity |
|:--|:-----|:----:|:----:|
| **B1** | Metadata corruption — existing field overwritten or deleted | MC-006 | CRITICAL |
| **B2** | Ownership mismatch — core skill assigned project owner | NS-003 | CRITICAL |
| **B3** | Namespace violation — project ID in core/adapter namespace | NS-003, NS-004 | CRITICAL |
| **B4** | Schema incompatibility — required field missing after backfill | GV-001 | CRITICAL |
| **B5** | Forbidden state triggered — F1-F10 detected | GV-002 | CRITICAL |
| **B6** | Body content modified — SHA-256 mismatch | BF-006 | CRITICAL |
| **B7** | Rollback failure — cannot restore pre-backfill state | RB-001 | CRITICAL |

### 5.2 WARNING Conditions

| # | Condition | Test | Severity |
|:--|:-----|:----:|:----:|
| **W1** | Inferred owner — skill had no owner, assigned default | BF-003 | MEDIUM |
| **W2** | Default version — skill had no version, assigned 1.0.0 | BF-002 | LOW |
| **W3** | Missing optional metadata — dependencies, permissions, validation not backfilled | MC-001 | LOW |
| **W4** | Implicit lifecycle — 147 skills had no explicit lifecycle | BF-004 | LOW |

---

## 6. Rollback Plan

### 6.1 Rollback Triggers

```
Any Critical Failure (B1-B7) → HALT dry run → execute rollback
```

### 6.2 Rollback Procedure

```
Full Rollback:
  1. Stop all dry run tests
  2. Restore all SKILL.md from /tmp/hermes-wave3-dryrun/skills/ baseline
  3. Verify SHA-256 all 148 match pre-backfill
  4. Report: rollback successful (0-diff) or failed

Per-Scope Rollback:
  1. Identify failed scope (core/adapter/project)
  2. Restore only that scope's SKILL.md files
  3. Verify scope SHA-256 matches pre-backfill
  4. Verify other scopes unaffected
```

---

## 7. Human Approval Gate

### 7.1 Pre-Dry-Run Approval

```
☐ Governance Reviewer confirms:

  ☐ Dry run environment isolated from production
  ☐ 148 SKILL.md shadow copies created
  ☐ Test matrix: 25 tests (6 MC + 6 NS + 6 BF + 4 GV + 3 RB)
  ☐ Backfill rules: preserve existing, default 1.0.0, owner inference
  ☐ 7 BLOCK conditions + 4 WARNING conditions defined
  ☐ Rollback: full + per-scope procedures
  ☐ Migration Operator + Validator designated
```

### 7.2 Post-Dry-Run Approval

```
☐ All 25 tests PASS
☐ 0 Critical Failures
☐ Body content unchanged (BF-006)
☐ Rollback verified (RB-001 to RB-003)
☐ Dry run report produced
```

---

## 8. Final Decision

```
🟢 READY FOR WAVE 3 DRY RUN

  25 tests defined
  7 BLOCK + 4 WARNING conditions
  Environment: /tmp/hermes-wave3-dryrun/
  Production: untouched
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ |
| 8 sections complete | ✅ |
| 25 tests defined | ✅ 6+6+6+4+3 |
| 7 BLOCK + 4 WARNING | ✅ |
| Dry run environment specified | ✅ |
| Rollback plan (full + per-scope) | ✅ |
| 0 executable code | ✅ |
| Registry unchanged | ✅ |
| Skills unchanged | ✅ |

---

> **Phase:** A.3.1 — Wave 3 Dry Run Specification
> **Status:** ✅ COMPLETE
> **Decision:** 🟢 READY FOR WAVE 3 DRY RUN
> **Next:** Phase A.3.2 — Wave 3 Dry Run Execution
