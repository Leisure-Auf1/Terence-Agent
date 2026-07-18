# Hermes Wave 3 — Metadata Completion Assessment

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18T07:55:00Z
**Phase:** A.3.0 — Wave 3 Metadata Completion Assessment
**Audience:** Governance Reviewer · Migration Operator · Validator
**Purpose:** Audit all 148 namespace-mapped skills for Registry v1.1 metadata gaps and define completion strategy

**Governance Authority:**
- Registry Namespace Schema Amendment v1.0 (C.3.1) — 17-field schema
- Wave 2 Execution Result v1.0 (A.2.5) — 148 skills namespace-mapped
- Governance Constitution v1.0 (FROZEN per C.5)

**Preconditions (completed):**
- Wave 0: ✅ Registry 15→11, 8 Class C relocated
- Wave 1: ✅ 8→3 canonical + 6 aliases
- Wave 2: ✅ 148 skills namespace-mapped

**This document does NOT:**
- Modify any SKILL.md
- Modify the Registry
- Execute metadata backfill
- Move or delete files

---

## Executive Summary

### Current Metadata State

```
148 skills audited for Registry v1.1 metadata completeness:

  version:    91/148 have version (61%)  → 57 missing
  owner:      82/148 have owner   (55%)  → 66 missing
  lifecycle:   1/148 explicit      (<1%)  → 147 implicit
  status:      implicit OK for all        → 148 need explicit
```

### Wave 3 Objective

```
Wave 3 = Metadata Backfill

  GOAL: Every skill has complete Phase B required metadata:
    version, owner, lifecycle, status

  0 Registry changes (deferred to Wave 4)
  0 file deletions
  0 file movements
```

---

## 1. Metadata Audit Results

| Scope | Total | Has Version | Has Owner | Missing Version | Missing Owner |
|:-----|:----:|:----:|:----:|:----:|:----:|
| **Core** | 14 | 2 (14%) | 1 (7%) | 12 | 13 |
| **Adapter** | 122 | 80 (65%) | 69 (57%) | 35 | 43 |
| **Project** | 12 | 8 (67%) | 7 (58%) | 10 | 10 |
| **Total** | **148** | **91 (61%)** | **82 (55%)** | **57** | **66** |

### Core Skills — 12 Missing Version, 13 Missing Owner

`agent-governance-protocol`, `architecture-constraints`, `guidance-agent`, `error-registry`, `skill-manager`, `harness-preflight`, `task-progress`, `agent-logger`, `agent-debugger`, `agent-developer`, `agent-executor`, `skill-ecosystem-audit`, `coding-agent-orchestration`

### Project Skills — 10 Missing Each

`a3-multi-agent-pipeline`, `a3-agent-team-pipeline`, `a3-multi-agent-content-pipeline`, `a3-content-pipeline`, `a3-runtime-infrastructure`, `veritas-core`, `ucampus-auto-complete`, `u-campus-course-automation`, `chaoxing-homework`, `lab-report-execution`

---

## 2. Backfill Matrix

### Priority 1 — Core (HIGH)

| Skill | Version | Owner |
|:-----|:-----|:-----|
| `agent-governance-protocol` | `1.0.0` | `hermes-governance` |
| `architecture-constraints` | `1.0.0` | `hermes-governance` |
| `guidance-agent` | `1.0.0` | `hermes-platform` |
| `error-registry` | `1.0.0` | `hermes-governance` |
| `skill-manager` | `1.0.0` | `hermes-platform` |
| `harness-preflight` | `1.0.0` | `hermes-platform` |
| `task-progress` | `1.0.0` | `hermes-governance` |
| `agent-logger` | `1.0.0` | `hermes-platform` |
| `agent-debugger` | `1.0.0` | `hermes-platform` |
| `agent-developer` | `1.0.0` | `hermes-platform` |
| `agent-executor` | `1.0.0` | `hermes-platform` |
| `skill-ecosystem-audit` | `1.0.0` | `hermes-governance` |
| `coding-agent-orchestration` | `1.0.0` | `hermes-platform` |
| `webhook-subscriptions` | preserve `1.1.0` | `hermes-platform` |

### Priority 2 — Project (HIGH)

| Skill | Version | Owner | Namespace |
|:-----|:-----|:-----|:-----|
| `a3-multi-agent-pipeline` | `3.6.0` | `a3-team` | `project.a3.workflow` |
| `a3-agent-team-pipeline` | `1.0.0` (deprecated) | `a3-team` | `project.a3.workflow` |
| `a3-multi-agent-content-pipeline` | `1.0.0` (deprecated) | `a3-team` | `project.a3.workflow` |
| `a3-content-pipeline` | `1.0.0` | `a3-team` | `project.a3.pipeline` |
| `a3-runtime-infrastructure` | `1.0.0` | `a3-team` | `project.a3.infrastructure` |
| `veritas-core` | `1.0.0` | `veritas-team` | `project.veritas.core` |
| `ucampus-auto-complete` | `1.0.0` | `ucampus-team` | `project.ucampus.automation` |
| `u-campus-course-automation` | `1.0.0` | `ucampus-team` | `project.ucampus.course` |
| `chaoxing-homework` | `1.0.0` | `ucampus-team` | `project.ucampus.chaoxing` |
| `lab-report-execution` | `1.0.0` | `ucampus-team` | `project.ucampus.lab` |

### Priority 3 — Adapter (MEDIUM)

35 adapter skills missing version, 43 missing owner. All assigned `hermes-platform` as owner.

---

## 3. Backfill Rules

```
V1: Skills with NO version → 1.0.0 default (exception: a3-multi-agent-pipeline → 3.6.0)
V2: Skills WITH version → PRESERVE existing
O1: Core tier 0 → hermes-governance; tier 1 → hermes-platform
O2: Project → team from namespace
O3: Adapter → hermes-platform
L1: Active skills → lifecycle: active, status: ok
L2: Deprecated aliases → lifecycle: deprecated, status: grace_period
```

---

## 4. Batches

| Batch | Scope | Skills | Priority |
|:-----|:-----|:----:|:----:|
| B1 | Core | 14 | 🔴 HIGH |
| B2 | Project | 12 | 🔴 HIGH |
| B3 | Registered adapters | 9 | 🟡 MEDIUM |
| B4 | Critical adapters | ~15 | 🟡 MEDIUM |
| B5 | Remaining adapters | ~98 | 🟢 LOW |

---

## 5. Dry Run Requirements

10 tests: version presence (T1), owner presence (T2), lifecycle presence (T3), version preserved (T4), owner preserved (T5), core owner match (T6), project owner match (T7), adapter owner match (T8), alias lifecycle (T9), body content unchanged (T10).

---

## 6. Core Independence Verification

```
✅ Core owner: hermes-governance (tier 0) or hermes-platform (tier 1)
✅ Core namespace: hermes.core.* (0 project IDs)
✅ No project owner assigned to core skill
✅ 0 Registry changes
```

---

## 7. Final Decision

```
🟢 READY FOR WAVE 3 DRY RUN

  57 skills need version
  66 skills need owner
  147 skills need explicit lifecycle
  5 batches (B1-B5)
  10 dry run tests defined
  0 Registry changes
```

---

> **Phase:** A.3.0 — Wave 3 Metadata Completion Assessment
> **Status:** ✅ COMPLETE
> **Next:** Phase A.3.1 — Wave 3 Dry Run Specification
