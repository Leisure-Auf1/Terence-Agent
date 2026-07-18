# Hermes Wave 1 — Production Merge Execution Plan

**Status:** Phase A.1.3 — Execution Plan Complete · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T07:05:00Z
**Phase:** A.1.3 — Wave 1 Execution Plan
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Define exact step-by-step procedure for Wave 1 production merge execution

**Governance Authority:**
- Wave 1 Duplicate Merge Assessment v1.0 (A.1.0)
- Wave 1 Dry Run Specification v1.0 (A.1.1)
- Wave 1 Dry Run Result v1.0 (A.1.2) — 12/12 PASS
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions Verified:**
- Wave 0: ✅ SUCCESS — Registry 15→11 entries
- Wave 1 Assessment: ✅ 3 merge groups (8 skills → 3 canonical)
- Wave 1 Dry Run: ✅ 12/12 equivalence tests PASS
- Registry current state: 11 entries (post-Wave 0)
- Skill files: 147 SKILL.md — all SHA-256 verified

**This document is:**
- An execution plan — defines HOW to merge, not what to merge
- A pre-execution artifact — no merge performed yet
- The final gate before Wave 1 production execution

---

## 1. Execution Objective

### 1.1 What Wave 1 Does

```
Wave 1 = Duplicate Capability Merge (Production)

  3 merge groups:
    Group 1: 3 A3 pipeline skills → 1 canonical (project.a3.workflow)
    Group 2: 3 content review skills → 1 canonical (adapter.review.pipeline)
    Group 3: 2 academic writing skills → 1 canonical (adapter.writing.academic)

  Result:
    8 source skills → 3 canonical skills
    5 deprecated aliases → 14-day grace period → archive
    0 files deleted
    0 capabilities lost
```

### 1.2 Merge ≠ Delete

| ✅ MERGE (Wave 1) | ❌ DELETE (Never) |
|:-----|:-----|
| Content from absorbed skills → merged into canonical | Content deleted |
| Original SKILL.md files → retained at original paths | Files removed from disk |
| Old skill names → deprecated aliases → canonical redirect | Names go dark (404) |
| Registry → alias entries added | Entries removed |
| Reversible (reactivate deprecated skill) | Irreversible |

### 1.3 Alias Compatibility

```
Each absorbed skill gets a DEPRECATED alias:

  lifecycle: deprecated
  replaced_by: <canonical-namespace>/<canonical-name>
  status: grace_period
  grace_period_ends: <today + 14 days>

During grace period:
  - Old name → resolves to canonical (with deprecation warning)
  - All existing references continue to work
  - New references to old names emit deprecation warning

After grace period:
  - lifecycle: archived
  - Old name → still resolves (historical reference)
  - New references to old names rejected
```

---

## 2. Pre-Execution Snapshot

### 2.1 Production State Freeze

Before any merge action, take **immutable snapshots** of current state:

```
Snapshot Directory: /tmp/hermes-wave1-snapshots/

Step 2.1: Registry snapshot
  cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
     /tmp/hermes-wave1-snapshots/registry.baseline.json
  sha256sum → record fingerprint

Step 2.2: Skill inventory
  For each of 8 source skills:
    sha256sum ~/.hermes/skills/<category>/<name>/SKILL.md
    → /tmp/hermes-wave1-snapshots/skill-inventory.txt

Step 2.3: Alias state snapshot
  Current alias state: NONE (no deprecated aliases exist for these 8 skills)
  → /tmp/hermes-wave1-snapshots/alias-state.baseline.md

Step 2.4: Verify snapshot integrity
  diff registry.baseline.json <production-registry>
  → MUST be 0 differences
```

### 2.2 Source Skill Fingerprints (Pre-Merge)

| # | Skill | Category | Lines | SHA-256 (pre-merge) |
|:--|:-----|:-----|:----:|:-----|
| S1 | `a3-multi-agent-pipeline` | autonomous-ai-agents | 1,445 | `<record at snapshot>` |
| S2 | `a3-agent-team-pipeline` | software-development | 136 | `<record at snapshot>` |
| S3 | `a3-multi-agent-content-pipeline` | software-development | 125 | `<record at snapshot>` |
| S4 | `content-review-pipeline` | content-review-pipeline | 133 | `<record at snapshot>` |
| S5 | `content-review-gate` | software-development | 111 | `<record at snapshot>` |
| S6 | `review-gate-pipeline` | devops | 162 | `<record at snapshot>` |
| S7 | `paper-report-writing` | research | 124 | `<record at snapshot>` |
| S8 | `research-paper-writing` | research | 2,377 | `<record at snapshot>` |

---

## 3. Merge Execution Matrix

### 3.1 Group 1 — project.a3.workflow

| Role | Skill | Action | Target |
|:-----|:-----|:-----|:-----|
| **Canonical** | `a3-multi-agent-pipeline` | KEEP — enriched with merged content | `~/.hermes/skills/autonomous-ai-agents/a3-multi-agent-pipeline/SKILL.md` (updated) |
| **Absorbed** | `a3-agent-team-pipeline` | Content merged into canonical. Original RETAINED. | DEPRECATED alias → canonical |
| **Absorbed** | `a3-multi-agent-content-pipeline` | Content merged into canonical. Original RETAINED. | DEPRECATED alias → canonical |

**Namespace:** `project.a3.workflow`
**Scope:** `project`
**Owner:** `a3-team` (Tier 2)

**Content Merge Strategy:**
```
Canonical base: a3-multi-agent-pipeline/SKILL.md (1,445 lines)
  + Agent team routing sections from a3-agent-team-pipeline/SKILL.md
  + Content pipeline specifics from a3-multi-agent-content-pipeline/SKILL.md

Merge method: APPEND non-overlapping sections to canonical.
Overlapping content: keep most comprehensive version (canonical base).
```

### 3.2 Group 2 — adapter.review.pipeline

| Role | Skill | Action | Target |
|:-----|:-----|:-----|:-----|
| **Canonical** | `content-review-pipeline` | KEEP — enriched with merged content | `~/.hermes/skills/content-review-pipeline/SKILL.md` (updated) |
| **Absorbed** | `content-review-gate` | Content merged into canonical. Original RETAINED. | DEPRECATED alias → canonical |
| **Absorbed** | `review-gate-pipeline` | Content merged into canonical. Original RETAINED. | DEPRECATED alias → canonical |

**Namespace:** `adapter.review.pipeline`
**Scope:** `adapter`
**Owner:** `hermes-platform` (Tier 1)

**Content Merge Strategy:**
```
Canonical base: content-review-pipeline/SKILL.md (133 lines)
  + AST static audit + pytest validation from content-review-gate/SKILL.md
  + User simulation + hot-fix loop from review-gate-pipeline/SKILL.md

Merge method: APPEND complementary review layers to canonical.
```

### 3.3 Group 3 — adapter.writing.academic

| Role | Skill | Action | Target |
|:-----|:-----|:-----|:-----|
| **Canonical** | `academic-writing` | CREATE new canonical skill | `~/.hermes/skills/research/academic-writing/SKILL.md` (NEW) |
| **Absorbed** | `paper-report-writing` | Content merged into canonical. Original RETAINED. | DEPRECATED alias → canonical |
| **Absorbed** | `research-paper-writing` | Content merged into canonical. Original RETAINED. | DEPRECATED alias → canonical |

**Namespace:** `adapter.writing.academic`
**Scope:** `adapter`
**Owner:** `hermes-platform` (Tier 1)

**Content Merge Strategy:**
```
Canonical: NEW academic-writing/SKILL.md
  Base: research-paper-writing/SKILL.md (2,377 lines — comprehensive)
  + Feynman research agent integration from paper-report-writing/SKILL.md
  + Citation verification from paper-report-writing/SKILL.md

Merge method: CREATE new file using research-paper-writing as base,
  APPEND unique sections from paper-report-writing.
```

---

## 4. Execution Steps

### 4.1 Step 1 — Backup & Verification

```
☐ 1.1: Create snapshot directory
     mkdir -p /tmp/hermes-wave1-snapshots/

☐ 1.2: Registry backup (DEFENSE IN DEPTH)
     cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
        /tmp/hermes-wave1-snapshots/registry.pre-merge-backup.json

☐ 1.3: Skill inventory (SHA-256 all 8 source skills)
     For each skill in {S1..S8}:
       sha256sum ~/.hermes/skills/<category>/<name>/SKILL.md
     → /tmp/hermes-wave1-snapshots/skill-inventory.txt

☐ 1.4: Verify all 8 skills exist and are readable
     For each skill: test -f <path>/SKILL.md → MUST be YES

☐ 1.5: Human Reviewer signs Wave 1 approval (C.1 §2 Wave 1)
```

### 4.2 Step 2 — Create/Update Canonical Skills

```
☐ 2.1: Group 1 — Update canonical
     Target: ~/.hermes/skills/autonomous-ai-agents/a3-multi-agent-pipeline/SKILL.md
     Action: APPEND non-overlapping sections from absorbed skills
     Content to append:
       - Agent team routing from a3-agent-team-pipeline
       - Content generation pipeline from a3-multi-agent-content-pipeline
     Update metadata:
       - Increment version (MAJOR.MINOR → bump MINOR for content expansion)
       - Add merge note: "Content merged from a3-agent-team-pipeline and
         a3-multi-agent-content-pipeline per Wave 1 merge"

☐ 2.2: Group 2 — Update canonical
     Target: ~/.hermes/skills/content-review-pipeline/SKILL.md
     Action: APPEND complementary review layers from absorbed skills
     Content to append:
       - AST static audit + pytest validation from content-review-gate
       - User simulation + hot-fix loop from review-gate-pipeline
     Update metadata:
       - Increment version
       - Add merge note

☐ 2.3: Group 3 — Create canonical
     Target: ~/.hermes/skills/research/academic-writing/SKILL.md (NEW)
     Action: CREATE new file
     Content:
       - Base: research-paper-writing/SKILL.md content
       - Append: Feynman agent + citation verification from paper-report-writing
     Metadata:
       - name: academic-writing
       - version: 1.0.0
       - namespace: adapter.writing.academic
       - scope: adapter
       - owner: hermes-platform
       - description: "Use when writing academic papers, reports, or research documents.
         Combines multi-agent writing workflow with Feynman research agent integration."
```

### 4.3 Step 3 — Verify Canonical Content

```
☐ 3.1: SHA-256 all 3 canonical skills
     Record fingerprints for post-merge audit

☐ 3.2: Content coverage check
     Group 1: Canonical contains sections from all 3 sources? → Verify
     Group 2: Canonical contains all 3 review layers? → Verify
     Group 3: Canonical contains both writing methodologies? → Verify

☐ 3.3: No content regression
     Original skill files UNCHANGED (SHA-256 match pre-merge inventory)
```

### 4.4 Step 4 — Create Deprecated Aliases

```
☐ 4.1: Create alias manifest
     /tmp/hermes-wave1-snapshots/alias-manifest.json
     Contains 5 alias entries with:
       - old_name
       - replaced_by (canonical namespace + name)
       - lifecycle: deprecated
       - status: grace_period
       - grace_period_ends: <today + 14 days>

☐ 4.2: Register aliases
     For each absorbed skill, add alias entry to tracking document
     (Aliases are metadata records — they don't modify original SKILL.md files)

  Alias Map:
    a3-agent-team-pipeline            → project.a3.workflow/a3-multi-agent-pipeline
    a3-multi-agent-content-pipeline   → project.a3.workflow/a3-multi-agent-pipeline
    content-review-gate               → adapter.review.pipeline/content-review-pipeline
    review-gate-pipeline              → adapter.review.pipeline/content-review-pipeline
    paper-report-writing              → adapter.writing.academic/academic-writing
    research-paper-writing            → adapter.writing.academic/academic-writing
```

### 4.5 Step 5 — Update Metadata

```
☐ 5.1: Update canonical skill metadata
     All 3 canonicalls:
       - updated: 2026-07-18
       - Add changelog entry: "Wave 1 merge — absorbed <list of skills>"

☐ 5.2: Update alias tracking
     All 5 absorbed skills:
       - lifecycle: deprecated
       - replaced_by: <canonical reference>
       - status: grace_period
```

### 4.6 Step 6 — Post-Merge Validation

```
☐ 6.1: Canonical skills loadable
     skill_view('a3-multi-agent-pipeline') → loads correctly
     skill_view('content-review-pipeline') → loads correctly
     skill_view('academic-writing')        → loads correctly

☐ 6.2: Deprecated aliases resolve
     skill_view('a3-agent-team-pipeline')  → redirects to canonical (deprecation warning)
     skill_view('content-review-gate')     → redirects to canonical (deprecation warning)
     skill_view('paper-report-writing')    → redirects to canonical (deprecation warning)
     skill_view('a3-multi-agent-content-pipeline') → redirects to canonical
     skill_view('review-gate-pipeline')    → redirects to canonical
     skill_view('research-paper-writing')  → redirects to canonical

☐ 6.3: Original files intact
     SHA-256 all 8 source skills → match pre-merge inventory (Step 1.3)

☐ 6.4: Registry unchanged
     Registry still has 11 entries (Wave 1 does not modify registry)
     diff with pre-merge backup → 0 differences

☐ 6.5: Namespace verification
     G1: project.a3.workflow — project identity preserved
     G2: adapter.review.pipeline — project-neutral
     G3: adapter.writing.academic — project-neutral
```

---

## 5. Alias Compatibility

### 5.1 Alias Resolution Model

```
BEFORE MERGE:
  skill_view('a3-agent-team-pipeline')
    → Loads a3-agent-team-pipeline/SKILL.md directly
    → No deprecation warning

AFTER MERGE:
  skill_view('a3-agent-team-pipeline')
    → Alias detected → lifecycle: deprecated
    → Resolves to: project.a3.workflow/a3-multi-agent-pipeline
    → Shows deprecation warning: "a3-agent-team-pipeline is deprecated.
      Use a3-multi-agent-pipeline instead. Grace period ends <date>."
    → Loads canonical content

AFTER GRACE PERIOD (14 days):
  skill_view('a3-agent-team-pipeline')
    → Alias detected → lifecycle: archived
    → Still resolves (historical reference)
    → Shows stronger warning: "archived"
    → New references to this name should not be created
```

### 5.2 Grace Period Timeline

```
Day 0:    Merge executed. 5 aliases created. lifecycle: deprecated.
Day 1-13: Grace period. Aliases resolve with deprecation warning.
Day 14:   Grace period ends. lifecycle: archived.
          Aliases still resolve but with archive warning.
```

### 5.3 Deprecation Markers

```yaml
# Per absorbed skill alias
old_name: a3-agent-team-pipeline
canonical_name: a3-multi-agent-pipeline
canonical_namespace: project.a3.workflow
lifecycle: deprecated
status: grace_period
replaced_by: project.a3.workflow/a3-multi-agent-pipeline
deprecated_date: 2026-07-18
grace_period_ends: 2026-08-01
```

---

## 6. Rollback Plan

### 6.1 Rollback Trigger Conditions

| # | Condition | Severity |
|:--|:-----|:----:|
| R1 | Canonical SKILL.md fails to load | **CRITICAL** |
| R2 | Any absorbed skill's original file accidentally modified | **CRITICAL** |
| R3 | Deprecated alias returns 404 | **HIGH** |
| R4 | Alias resolves to wrong canonical | **HIGH** |
| R5 | Namespace violation detected (project in adapter) | **CRITICAL** |
| R6 | Content regression (canonical missing merged sections) | **MEDIUM** |

### 6.2 Full Rollback Procedure

```
Step 1: STOP — halt all Wave 1 operations immediately

Step 2: Restore canonical skills
  Group 1: Restore a3-multi-agent-pipeline/SKILL.md from pre-merge backup
  Group 2: Restore content-review-pipeline/SKILL.md from pre-merge backup
  Group 3: Remove academic-writing/SKILL.md (new file)

Step 3: Clear alias entries
  Remove all 5 alias records from tracking

Step 4: Verify original state
  SHA-256 all 8 source skills → match pre-merge inventory
  Registry → unchanged (0 diff from baseline)

Step 5: Confirm
  All 8 source skills load independently
  No alias resolution active
  No canonical files remain (except originals)
```

### 6.3 Partial Rollback (Per-Group)

```
If only one group fails:
  → Rollback that group only
  → Other 2 groups remain merged

Example: Group 2 merge fails
  → Restore content-review-pipeline from backup
  → Clear content-review-gate and review-gate-pipeline aliases
  → Groups 1 and 3 remain merged
```

---

## 7. Post-Merge Validation

### 7.1 Gate Checklist

| # | Gate | Check | Method |
|:--|:-----|:-----|:-----|
| G1 | **Capability** | All 3 canonicalls contain complete merged content | Content coverage scan |
| G2 | **Trigger** | All trigger patterns from absorbed skills present in canonicalls | Trigger extraction + comparison |
| G3 | **Dependency** | All 5 deprecated aliases resolve correctly | Alias resolution test |
| G4 | **Namespace** | project.a3 preserved; adapter skills project-neutral | Namespace prefix verification |
| G5 | **Integrity** | All 8 original SKILL.md files SHA-256 unchanged | SHA-256 fingerprint compare |
| G6 | **Rollback** | Per-group + full rollback verified | Simulated restore + verify |

### 7.2 Gate Pass/Fail

```
All 6 gates must PASS before Wave 1 is complete:
  [ ] G1 Capability    — PASS
  [ ] G2 Trigger       — PASS
  [ ] G3 Dependency    — PASS
  [ ] G4 Namespace     — PASS
  [ ] G5 Integrity     — PASS
  [ ] G6 Rollback      — PASS
```

---

## 8. Human Approval Gate

### 8.1 Pre-Execution Approval

```
☐ Governance Reviewer confirms:

  ☐ Pre-execution snapshot created (§2)
  ☐ All 8 source skills SHA-256 recorded
  ☐ Merge strategy reviewed for all 3 groups
  ☐ Alias model understood: 14-day grace period
  ☐ Rollback plan reviewed: per-group + full
  ☐ Migration Operator designated
  ☐ Validator designated
  ☐ Wave 1 scope confirmed: 8 skills → 3 canonical, 0 deletions
  ☐ C.3 namespace model respected (Group 1 preserves project identity)
```

### 8.2 Execution Authorization

```
☐ Governance Reviewer signature:

    "I authorize Wave 1 production merge per this plan.
     Migration Operator may:
       - Update 2 canonical SKILL.md files (G1, G2)
       - Create 1 new canonical SKILL.md file (G3)
       - Create 5 deprecated aliases

     Migration Operator may NOT:
       - Delete any SKILL.md file
       - Modify original absorbed skill files
       - Modify the Registry

     Validator shall verify per §7.
     Any critical trigger (§6.1) requires immediate rollback."

  Signature: ________________________    Date: ______________
```

---

## 9. Final Decision

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   WAVE 1 — PRODUCTION MERGE EXECUTION PLAN                    ║
║                                                              ║
║   3 merge groups                                              ║
║   8 source skills → 3 canonical skills                        ║
║   5 deprecated aliases → 14-day grace period                  ║
║   0 deletions                                                 ║
║                                                              ║
║   Files to modify:      3 canonical SKILL.md                  ║
║   Files to create:      1 (academic-writing)                  ║
║   Files to delete:      0                                     ║
║   Registry changes:     0                                     ║
║   Alias entries:        5                                     ║
║                                                              ║
║   Rollback:              Per-group + full                     ║
║   Backups:               Pre-execution snapshots              ║
║                                                              ║
║   🟢 READY FOR EXECUTION                                     ║
║                                                              ║
║   Pre-condition: §8 Human Approval Gate signed                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-wave1-execution-plan.md` |
| 9 chapters complete | ✅ §1-9 |
| 3 merge groups specified | ✅ With canonical/absorbed assignments |
| 6 execution steps defined | ✅ Backup → Canonical → Verify → Alias → Metadata → Validate |
| Alias compatibility model | ✅ §5 — resolution + grace period + markers |
| Rollback plan | ✅ §6 — full + per-group |
| Post-merge validation gates | ✅ §7 — 6 gates |
| Human approval gate | ✅ §8 |
| 0 executable code | ✅ Pure documentation |
| Registry unchanged | ✅ 11 entries |
| Skills unchanged | ✅ 0 modifications |
| No PII | ✅ |
| Git diff | ✅ Only this new file |

---

> **Phase:** A.1.3 — Wave 1 Execution Plan
> **Status:** ✅ EXECUTION PLAN COMPLETE
> **Decision:** 🟢 READY FOR EXECUTION
> **Next:** Human Approval → Execute §4 → Validate §7 → Wave 1 Complete
