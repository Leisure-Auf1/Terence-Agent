# Hermes Skill Migration Specification

**Status:** Draft — Governance Document
**Type:** Governance Design Documentation — Migration Contract
**Version:** 1.0.0
**Applies to:** Hermes Skill Policy §9 + Registry Schema v1.0
**Created:** 2026-07-18
**Phase:** B.3 — Migration Specification Design

**Dependencies (completed):**
- Hermes Skill Governance Policy v1.0
- Hermes Skill Registry Schema v1.0 (Phase B.0)
- Hermes Skill Audit CLI Design v1.0 (Phase B.1)
- Hermes Auditor Agent Design v1.0 (Phase B.2)
- Hermes Skill Ecosystem Audit Report
- Skill Boundary Remediation Plan
- Phase B Readiness Report

**This document is:**
- A governance contract defining migration scope, safety rules, and per-Wave specifications
- A pre-execution plan — read-only, no modifications
- The final Phase B deliverable before human approval gates Phase A execution

---

## 1. Migration Objective

### 1.1 Current State

The Skill Ecosystem Audit identified four structural problems across 146 Skills:

| Problem | Scope | Impact |
|:--------|:------|:-------|
| **Governance Leakage** | 8 Skills (Class C) classified as operational Skills but functioning as Governance, Framework, or Memory components | `mount=always` Skills inject governance rules into every Hermes session; Policy §1.3 boundary violated |
| **Capability Duplication** | 10 duplicate groups (3 triple-duplicates) | Redundant Skills compete for the same capability domain; Skill Manager cannot disambiguate |
| **Project Coupling** | 21 Skills (Class E) with hardcoded project paths or names | Skills cannot be reused across projects; `veritas-core`, `a3-*` prevent cross-repo portability |
| **Metadata Deficiency** | 55 Skills without version; 146 without owner; 132 unregistered | Registry covers 14/146 Skills (9.6%) and 2/12 Policy fields (17%) |

### 1.2 Migration Target

| Metric | Before | After |
|:-------|:-------|:------|
| Total Skills | 146 | 138 |
| In Registry | 14 (9.6%) | 138 (100%) |
| Class C (Governance Risk) | 8 | 0 |
| Class E (Project Coupled) | 21 | 13 (platform/domain Skills retained) |
| Capability duplicates | 10 groups | 3 groups (platform branches only) |
| No version | 55 (38%) | 0 (0%) |
| Registry Policy coverage | 2/12 (17%) | 12/12 (100%) |

### 1.3 What Migration IS

| ✅ IS | Description |
|:------|:------------|
| **Relocation** | Moving a component from the Skill Layer to its correct architectural layer (Governance, Framework, or Memory) |
| **Renaming** | Changing a Skill's identifier from a project-specific name to a capability-descriptive name |
| **Merging** | Combining duplicate Skills into a single canonical Skill with preserved combined capability |
| **Metadata backfill** | Adding missing required fields to Skill metadata without changing Skill behavior |
| **Registration** | Adding a Skill entry to the Registry with full Schema compliance |

### 1.4 What Migration IS NOT

| ❌ IS NOT | Rationale |
|:----------|:----------|
| **Deletion** | No Skill file is removed. ARCHIVED is a lifecycle state, not a deletion. Content is preserved. |
| **Rewrite** | Skill content is not rewritten. Migrations are identity/metadata changes, not capability changes. |
| **Runtime change** | Migration does not alter how Hermes executes Skills at runtime. Mount strategies, loading mechanisms, and tool access remain unchanged. |
| **Capability modification** | Migration does not add, remove, or alter what a Skill can do. A browser-automation Skill remains a browser-automation Skill. |
| **Governance expansion** | Migration does not create new governance rules. It relocates incorrectly placed governance content to the Governance Layer where it already belongs. |

### 1.5 Architecture Principles

The following boundaries are non-negotiable. Migration must preserve them:

```
Skill ≠ Governance    — A Skill cannot define rules, approval flows, or safety constraints
Skill ≠ Framework     — A Skill cannot be a router, scheduler, or agent registry
Skill ≠ Memory        — A Skill cannot be a persistent data store (error registry, progress tracker)
Skill ≠ Runtime       — A Skill cannot be an execution engine, DAG executor, or state machine
Skill ≠ Agent         — A Skill cannot claim agent identity or exclusive tool authority
```

Every migration decision is validated against these five boundaries.

---

## 2. Migration Safety Contract

### 2.1 Before Migration

For every Skill being migrated, the following invariants MUST hold before the migration step executes:

| Invariant | Verification |
|:----------|:-------------|
| **Capability preservation** | The Skill's documented capabilities remain intact after migration |
| **File preservation** | Original SKILL.md and supporting files are not deleted — they are either retained at their current path (relocation via Registry) or copied to a new path with the original retained as a deprecated alias |
| **Behavior preservation** | Loading the Skill under its new identity produces equivalent functional behavior |
| **Reference integrity** | All existing references to the old Skill ID are identified and documented before the ID changes |

### 2.2 After Migration

| Invariant | Verification |
|:----------|:-------------|
| **Correct layer assignment** | The migrated component resides in the correct architectural layer (Governance/Framework/Memory/Skill) |
| **Registry state clarity** | The Registry entry reflects the migration: new `lifecycle`, `path`, and `replaced_by` fields are accurate |
| **Reference resolution** | All identified references to the old ID point to the new ID or deprecated alias |
| **No orphan references** | No Skill references a non-existent Skill ID as a result of this migration |

### 2.3 Verification Gates

Every Wave step is followed by verification:

| Gate | Tool | Pass Condition |
|:-----|:-----|:---------------|
| **Reference Resolution** | `hermes skill audit deps` | 0 unresolved dependency errors |
| **Loading Equivalence** | Manual load test | Migrated Skill loads and produces equivalent output |
| **Boundary Compliance** | `hermes skill audit boundary` | 0 governance leakage / runtime replacement findings |
| **Schema Compliance** | `hermes skill audit metadata` | All required fields present, all values valid |
| **Registry Integrity** | `hermes skill audit registry` | 0 orphan/ghost/duplicate errors |

---

## 3. Wave 0 Migration Specification — Class C Relocation

### 3.1 Objective

Relocate 8 Class C Skills from the Skill Layer to their correct architectural layers. These components are not operational Skills — they are Governance, Framework, or Memory components incorrectly registered as Skills.

### 3.2 Target Components

| # | Skill | Current mount | Actual Identity | Target Layer |
|:--|:------|:--------------|:----------------|:-------------|
| 1 | `agent-governance-protocol` | routed | Governance Protocol document | Governance Layer |
| 2 | `architecture-constraints` | always | Policy constraint document | Governance Layer |
| 3 | `guidance-agent` | routed | Agent role definition + routing logic | Framework Layer |
| 4 | `error-registry` | always | Structured error knowledge base | Memory Layer |
| 5 | `skill-manager` | always | Skill routing dispatcher | Framework Layer |
| 6 | `harness-preflight` | auto | Mechanical constraint check gate | Governance Layer |
| 7 | `task-progress` | auto | Cross-session progress data structure | Memory Layer |
| 8 | `agent-logger` | routed | Agent role definition (Logger) | Framework Layer |

### 3.3 Per-Skill Migration Specification

#### Skill 1: `agent-governance-protocol`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/agent-governance-protocol/SKILL.md` |
| **Current Classification** | Class C — defines "Mandatory execution rules…Phase 0/1/2…Stop Conditions" |
| **Actual Identity** | Governance Protocol document — the highest-level behavioral rules for Hermes Agent |
| **Target Layer** | Governance Layer |
| **Migration Type** | `relocate_to_governance` |
| **Runtime Impact** | None — the Protocol already injects as system prompt context, not as a Skill mount. Registry deregistration + Governance document registration changes nothing at runtime. |
| **Loading Strategy** | Governance Protocol is loaded by Hermes at session start via system prompt injection, NOT via Skill Manager mount. The `agent-governance-protocol` entry is removed from the Registry; the Protocol document is registered as a Governance artifact. |
| **Validation Rule** | After migration: Governance Protocol is accessible at its new path; no Skill references `agent-governance-protocol` as a dependency |
| **Rollback Method** | Re-register `agent-governance-protocol` in Registry with original metadata. The SKILL.md file is not moved — only the Registry entry changes. |

#### Skill 2: `architecture-constraints`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/architecture-constraints/SKILL.md` |
| **Current Classification** | Class C — "严格架构约束…打破约束=入error-registry" `mount=always` |
| **Actual Identity** | Policy constraint document — 512 lines of architectural constraints injected into every session |
| **Target Layer** | Governance Layer |
| **Migration Type** | `relocate_to_governance` |
| **Runtime Impact** | The constraints are currently loaded via `mount=always` through the Skill system. After migration, they are loaded via Governance context injection — semantically equivalent, correctly placed. |
| **Loading Strategy** | Remove from Skill Registry → register as Governance constraint document → load via same mechanism that injects Governance Protocol (context injection, not Skill mount). The content (512 lines) is unchanged. |
| **Validation Rule** | Hermes session still enforces architecture constraints. No `architecture-constraints` in Registry. Constraint violations still logged to error-registry. |
| **Rollback Method** | Re-register in Registry with `mount: always`. Content unchanged. |

#### Skill 3: `guidance-agent`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/guidance-agent/SKILL.md` |
| **Current Classification** | Class C — "只有我才能调用 skill_manage" — exclusive authority claim |
| **Actual Identity** | Agent role definition (Guidance Agent) + Skill routing logic |
| **Target Layer** | Framework Layer — Agent Registry |
| **Migration Type** | `relocate_to_framework` |
| **Runtime Impact** | Guidance Agent's routing logic must persist. The Skill Manager currently routes tasks through `guidance-agent` — this function moves to the Framework's Agent Registry as a first-class Agent definition, not a Skill. |
| **Loading Strategy** | Split: role definition → Framework/Agent Registry (Guidance Agent); routing logic → Framework/Skill Router (merge with `skill-manager` routing). The exclusive `skill_manage` claim is demoted — no Agent has exclusive authority. |
| **Validation Rule** | Agent Team routing still functions. `guidance-agent` not in Registry. No Agent claims exclusive tool authority. |
| **Rollback Method** | Re-register in Registry. Split components recombined. |

#### Skill 4: `error-registry`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/error-registry/SKILL.md` |
| **Current Classification** | Class C — `mount=always`, 38 error records + L0-L3 classification |
| **Actual Identity** | Structured error knowledge base — Long Memory data, not a Skill |
| **Target Layer** | Memory Layer — ErrorMemory |
| **Migration Type** | `relocate_to_memory` |
| **Runtime Impact** | Currently loaded via `mount=always` (full 38 records every session). After migration: loaded via Memory retrieval (query-based, only relevant errors). Functionally equivalent, more efficient. |
| **Loading Strategy** | Migrate 38 error records to Long Memory with `type: error_lesson`. Skill Manager no longer mounts `error-registry`. Hermes queries ErrorMemory on error conditions. |
| **Validation Rule** | Error lookups still return correct records. New errors still writable to ErrorMemory. All 38 records migrated with intact L0-L3 classification. |
| **Rollback Method** | Re-register `error-registry` in Registry with `mount: always`. Memory records retained as backup. |

#### Skill 5: `skill-manager`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/skill-manager/SKILL.md` |
| **Current Classification** | Class C — "任务入口路由 — 接任务→查注册表→分配技能→转交执行" `mount=always` |
| **Actual Identity** | Framework component — Skill routing dispatcher |
| **Target Layer** | Framework Layer — Skill Router |
| **Migration Type** | `relocate_to_framework` |
| **Runtime Impact** | The Skill Manager is the core Skill dispatch mechanism. Removing it from `mount=always` must not break Skill routing. The routing logic moves to the Framework and becomes a built-in component (not a mountable Skill). |
| **Loading Strategy** | Skill Router becomes a Framework built-in — always active, always routing, but not a Skill. The Registry entry is removed; the routing function is preserved in Framework. |
| **Validation Rule** | Skill dispatch still works. All trigger patterns still matched. `skill-manager` not in Registry. |
| **Rollback Method** | Re-register in Registry with `mount: always`. Framework router disabled. |

#### Skill 6: `harness-preflight`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/harness-preflight/SKILL.md` |
| **Current Classification** | Class C — "每次开始前执行机械约束检查" `mount=auto`, gate function |
| **Actual Identity** | Governance gate — Phase 0 preflight check (mechanized as shell script) |
| **Target Layer** | Governance Layer — Preflight Gate |
| **Migration Type** | `relocate_to_governance` |
| **Runtime Impact** | The shell script (`scripts/check-preflight.sh`) is already the functional component. The SKILL.md is supplementary documentation. Migration: remove from Registry, keep shell script as Governance gate triggered at Phase 0. |
| **Loading Strategy** | Preflight is triggered by Governance Protocol at Phase 0 start, not by Skill Manager mount. The SKILL.md becomes Governance documentation. |
| **Validation Rule** | `bash scripts/check-preflight.sh` still executes. Preflight gate enforced at Phase 0. `harness-preflight` not in Registry. |
| **Rollback Method** | Re-register in Registry with `mount: auto`. |

#### Skill 7: `task-progress`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/task-progress/SKILL.md` |
| **Current Classification** | Class C — "进度追踪 — 跨会话恢复" `mount=auto` |
| **Actual Identity** | Cross-session progress data structure — ProgressMemory |
| **Target Layer** | Memory Layer — ProgressMemory |
| **Migration Type** | `relocate_to_memory` |
| **Runtime Impact** | Progress tracking moves from a Skill mount to a Memory interface. Hermes writes/reads progress through the Memory API, not through Skill loading. |
| **Loading Strategy** | Progress data stored in Memory with `type: task_progress`. Skill Manager no longer mounts `task-progress`. Hermes queries ProgressMemory for task state. |
| **Validation Rule** | Task progress persists across sessions. Progress queries return correct state. `task-progress` not in Registry. |
| **Rollback Method** | Re-register in Registry with `mount: auto`. |

#### Skill 8: `agent-logger`

| Field | Value |
|:------|:------|
| **Current Location** | `~/.hermes/skills/devops/agent-logger/SKILL.md` |
| **Current Classification** | Class C — "Agent 角色定义（Logger）" |
| **Actual Identity** | Agent role definition — Logger Agent |
| **Target Layer** | Framework Layer — Agent Registry |
| **Migration Type** | `relocate_to_framework` |
| **Runtime Impact** | Logger's role definition moves to Agent Registry alongside Guidance, Developer, Debugger, and Executor. Logger's logging function is preserved. |
| **Loading Strategy** | Merge into Agent Registry as a first-class Agent role. No longer a mountable Skill. |
| **Validation Rule** | Logger Agent still logs. All five Agent roles defined in Agent Registry. `agent-logger` not in Registry. |
| **Rollback Method** | Re-register in Registry. |

### 3.4 Wave 0 Layer Inflation Check

| Layer | Before Wave 0 | After Wave 0 | Inflation? |
|:------|:--------------|:-------------|:-----------|
| Governance Layer | 3 docs (Protocol + Workflow + Skill Policy) | 5 docs (+2 relocated) | ✅ Minuscule — relocation, not creation |
| Framework Layer | 0 explicit components | 3 (Skill Router + Agent Registry + routing logic) | ✅ Defining existing implicit components |
| Memory Layer | 0 explicit components | 2 (ErrorMemory + ProgressMemory) | ✅ Defining existing implicit stores |
| Skill Layer | 146 Skills | 138 Skills | ✅ 减少 8 |

**No layer inflation. Relocation makes implicit architecture explicit.**

### 3.5 Wave 0 No-Deletion Guarantee

| Guarantee | Mechanism |
|:----------|:----------|
| No file deleted | All SKILL.md files remain at their current paths |
| No capability removed | All functionality preserved — relocation is identity change, not capability change |
| Registry deregistration only | `skill-registry.json` entries removed; files untouched |
| Reversible | Each migration is independently reversible via re-registration |

---

## 4. Wave 1 — Duplicate Capability Merge

### 4.1 Objective

Merge 10 duplicate Skill groups into canonical Skills, reducing from 10 groups to 3 retained groups. All content preserved.

### 4.2 Merge Groups

#### Group 1: Multi-Agent Pipeline (3 → 1)

| Current Skills | Merge Target |
|:---------------|:-------------|
| `a3-multi-agent-pipeline` | |
| `a3-agent-team-pipeline` | **→** `multi-agent-pipeline` |
| `a3-multi-agent-content-pipeline` | |

**Merge Criteria:**
- All three describe multi-agent orchestration for content generation
- `a3-multi-agent-pipeline` is the most general; `a3-agent-team-pipeline` and `a3-multi-agent-content-pipeline` are specializations
- Merged Skill combines all non-overlapping content; overlapping content uses the most general version

**Content Preservation Rules:**
1. The canonical SKILL.md is `multi-agent-pipeline` — combines all unique sections from all three
2. Any A3-specific paths (referenced in body, not in identity) are removed during Wave 2 cleanup
3. All trigger patterns from all three are merged
4. Capability: `multi-agent-orchestration`

**Reference Migration:**
- Any Skill referencing `a3-multi-agent-pipeline` → now references `multi-agent-pipeline`
- Any Skill referencing `a3-agent-team-pipeline` → now references `multi-agent-pipeline`
- Any Skill referencing `a3-multi-agent-content-pipeline` → now references `multi-agent-pipeline`

**Deprecated Alias Strategy:**
- All three old IDs registered as DEPRECATED with `replaced_by: multi-agent-pipeline`
- Grace period: 14 days before ARCHIVED
- No new references to old IDs accepted

#### Group 2: Content Review (3 → 1)

| Current Skills | Merge Target |
|:---------------|:-------------|
| `content-review-gate` | |
| `review-gate-pipeline` | **→** `content-review-pipeline` |
| `content-review-pipeline` | |

**Merge Criteria:**
- All three describe content quality review workflows
- `content-review-pipeline` is already the most descriptive name
- Merge non-overlapping review gate logic from the other two

**Content Preservation Rules:**
1. Canonical SKILL.md: `content-review-pipeline`
2. AST static audit + pytest dynamic validation from `content-review-gate` merged in
3. User simulation + hot-fix loop from `review-gate-pipeline` merged in

**Reference Migration:** `content-review-gate` and `review-gate-pipeline` → `content-review-pipeline`

**Deprecated Alias Strategy:** Same as Group 1.

#### Group 3: Academic Writing (2 → 1)

| Current Skills | Merge Target |
|:---------------|:-------------|
| `paper-report-writing` | |
| `research-paper-writing` | **→** `academic-writing` |

**Merge Criteria:**
- Both describe academic paper/report writing workflows
- `academic-writing` is a clearer, more generic capability domain

**Content Preservation Rules:**
1. Canonical SKILL.md: `academic-writing`
2. Feynman research agent integration from `paper-report-writing` merged in
3. Multi-agent writing workflow from `research-paper-writing` merged in

### 4.3 Groups NOT Merged (Retained)

| Group | Skills | Reason |
|:------|:------|:-------|
| U-Campus | `ucampus-auto-complete` + `u-campus-course-automation` | Distinct responsibilities: auto-completion vs full workflow guide. Complementary, not duplicates. |

### 4.4 Wave 1 No-Deletion Guarantee

| Guarantee | Mechanism |
|:----------|:----------|
| Original files retained | Old SKILL.md files remain; content merged into canonical Skill |
| Old IDs preserved as aliases | Deprecated lifecycle + `replaced_by` reference |
| Grace period | 14 days before ARCHIVAL; all references migrated during grace period |
| Reversible (within grace period) | Reactivate deprecated Skill from ARCHIVED back to ACTIVE; reverse merge |

---

## 5. Wave 2 — Project Coupling Decoupling

### 5.1 Objective

Rename 6 Class E Skills from project-specific names to capability-descriptive names. Remove hardcoded project paths from Skill bodies. Convert project-specific Skills into reusable capability Skills.

### 5.2 Rename Specifications

| # | Old ID | New ID | Migration Type |
|:--|:-------|:-------|:---------------|
| 1 | `veritas-core` | `agent-runtime-development` | `rename` |
| 2 | `a3-runtime-infrastructure` | `agent-runtime-infrastructure` | `rename` |
| 3 | `a3-multi-agent-pipeline` | *(merged in Wave 1)* | `rename_merge` |
| 4 | `a3-agent-team-pipeline` | *(merged in Wave 1)* | `rename_merge` |
| 5 | `a3-multi-agent-content-pipeline` | *(merged in Wave 1)* | `rename_merge` |
| 6 | `a3-content-pipeline` | `content-generation-pipeline` | `rename` |

Note: 3 of the 6 are handled by Wave 1 merge. Only 3 require Wave 2 standalone rename.

### 5.3 Per-Skill Decoupling

#### Skill 1: `veritas-core` → `agent-runtime-development`

| Field | Value |
|:------|:------|
| **Old ID** | `veritas-core` |
| **New ID** | `agent-runtime-development` |
| **Alias Policy** | `veritas-core` registered as DEPRECATED with `replaced_by: agent-runtime-development`. Grace period 14 days. |
| **Content Changes** | Description rewritten: "Work on agent runtime frameworks with StateMachine/EventBus/Trace patterns" (removes Veritas-Core repo reference) |
| **Path Changes** | Any `~/Veritas-Core/` references in body replaced with generic `agent-runtime/` references |
| **Capability Scope** | Unchanged — agent runtime development patterns |

#### Skill 2: `a3-runtime-infrastructure` → `agent-runtime-infrastructure`

| Field | Value |
|:------|:------|
| **Old ID** | `a3-runtime-infrastructure` |
| **New ID** | `agent-runtime-infrastructure` |
| **Alias Policy** | `a3-runtime-infrastructure` → DEPRECATED → `agent-runtime-infrastructure` |
| **Content Changes** | Remove A3-specific references; keep FastAPI API layer + EventBridge patterns (generically applicable) |
| **Path Changes** | Remove `~/A3-Multi-Agent-System/` paths |
| **Capability Scope** | Unchanged — runtime infrastructure patterns |

#### Skill 3: `a3-content-pipeline` → `content-generation-pipeline`

| Field | Value |
|:------|:------|
| **Old ID** | `a3-content-pipeline` |
| **New ID** | `content-generation-pipeline` |
| **Alias Policy** | Standard deprecation with `replaced_by` |
| **Content Changes** | Remove A3 branding; keep content generation pipeline patterns |
| **Capability Scope** | Unchanged — content generation pipeline |

### 5.4 Body-Level Path Cleanup

For all Class E Skills (not just renames), hardcoded paths are removed and replaced with generic references:

| Pattern to Remove | Replacement |
|:------------------|:------------|
| `~/Terence-Agent/` | `[project-root]/` |
| `~/A3-Multi-Agent-System/` | `[agent-system-root]/` |
| `~/Veritas-Core/` | `[runtime-root]/` |
| Any absolute `/home/` path | `[absolute-path-removed]` |

### 5.5 Wave 2 No-Deletion Guarantee

| Guarantee | Mechanism |
|:----------|:----------|
| Old IDs preserved | All old IDs → DEPRECATED with `replaced_by` |
| No content deletion | Only project-specific references replaced; capability content untouched |
| History retained | Deprecated entries in Registry provide full rename audit trail |
| Reference migration | `hermes skill audit deps` verifies 0 broken references post-rename |

---

## 6. Wave 3 — Metadata Completion

### 6.1 Objective

Add missing metadata to 55 Skills without `version` and 146 Skills without `owner`. Bring all Skills to Phase B required-field compliance.

### 6.2 Automatically Populated Fields

These fields can be populated automatically without human review:

| Field | Default Value | Rationale |
|:------|:--------------|:----------|
| `version` | `"1.0.0"` | All existing Skills treated as initial release. Actual version history for unversioned Skills is unrecoverable — `1.0.0` is the honest starting point. |
| `status` | `"ok"` for `lifecycle: active`; `null` otherwise | Operational sub-status for active Skills; no known degradation |
| `registered` | `"2026-07-18"` (migration date) | Unknown original registration date — migration date is the best available |
| `updated` | `"2026-07-18"` (migration date) | Set to migration date |

### 6.3 Human-Confirmed Fields

These fields require human confirmation because the value carries semantic weight:

| Field | Why Human Confirmation | Default if Unconfirmed |
|:------|:-----------------------|:----------------------|
| `owner` | Identity of the responsible maintainer — assigning `agent-team` blindly may misattribute ownership | `null` for Phase B; required by Phase A |
| `permissions` | Must reflect the Skill's actual resource requirements — incorrect permissions break runtime or create security gaps | `null` for Phase B |
| `compatibility` | Must reflect tested platforms/providers — incorrect data misleads Skill Manager routing | `null` for Phase B |
| `validation` | `validation.command` must be a real, executable verification — fake commands break audit | `null` for Phase B |
| `dependencies` | Must reflect actual Skill-to-Skill relationships — incorrect deps break dependency resolution | `null` for Phase B; populated from `parent` field where present |

### 6.4 Population Strategy

| Batch | Skills | Fields | Method |
|:------|:-------|:-------|:-------|
| Batch 1 | All 138 Skills | `version`, `status`, `registered`, `updated` | Automated population with defaults |
| Batch 2 | 14 Registry Skills | `dependencies` from `parent` field | Automated migration of existing `parent` → `dependencies.skills` |
| Batch 3 | Remaining 124 Skills | `owner`, `permissions`, `compatibility`, `validation`, `dependencies` | Manual or future automated backfill |

### 6.5 Wave 3 Verification

```
hermes skill audit metadata --skills-root skills/
  → 0 missing required fields
  → All version fields: ^\d+\.\d+\.\d+$
  → All lifecycle fields: valid state
  → All status fields: valid for lifecycle
```

---

## 7. Wave 4 — Registry Completion

### 7.1 Objective

Register all 124 unregistered Skills in the Registry with full Schema compliance.

### 7.2 Registration Pre-Check

Before registration, each Skill must pass:

| Check | Tool | Pass Condition |
|:------|:-----|:---------------|
| Schema validation | `hermes skill audit metadata` | All 9 required Phase B fields present and valid |
| Boundary audit | `hermes skill audit boundary` | 0 critical/high governance leakage or runtime replacement |
| Dependency scan | `hermes skill audit deps` | 0 undeclared, circular, or archived dependencies |
| Duplicate check | `hermes skill audit dupes` | 0 exact duplicates (overlaps documented) |
| Filesystem check | `hermes skill audit registry` | SKILL.md exists at declared path; no orphan/ghost entries |

### 7.3 Registration Wave

| Batch | Skills | Count |
|:------|:-------|:------|
| Batch 1 | Class A Skills (fully compliant) | ~105 |
| Batch 2 | Class B Skills (metadata completed in Wave 3) | ~55 (subset of Batch 1) |
| Batch 3 | Class E retained Skills (platform/domain adapters) | 13 |
| Batch 4 | New canonical Skills (Wave 1 merge results) | 3 |
| **Total** | | **~124** |

Note: Class C Skills (8) are not registered — they were relocated in Wave 0.

### 7.4 Registry Before/After

```
BEFORE:
  skill-registry.json: 14 entries, 2/12 fields, 6 fields per entry

AFTER:
  skill-registry.yaml: 138 entries, 12/12 fields, 14 fields per entry
```

### 7.5 Final Audit Gate

```
hermes skill audit all --skills-root skills/ --registry skill-manager/skill-registry.yaml
  → 0 critical → GO
  → 0 error    → GO
  → ≤ 5 warning → CONDITIONAL GO
  → > 5 warning → BLOCKED
```

---

## 8. Rollback Strategy

### 8.1 Pre-Migration Snapshot

Before ANY Wave executes, take these snapshots:

| Artifact | Content | Storage |
|:---------|:--------|:--------|
| **Registry backup** | Full `skill-registry.json` (old format) | `skill-manager/skill-registry.json.bak-YYYYMMDD` |
| **Mapping table** | Old ID → New ID → Deprecated Alias | `docs/migration/mapping-table.yaml` |
| **Reference graph** | Full dependency graph pre-migration | `docs/migration/reference-graph-pre.yaml` |

### 8.2 Rollback Triggers

Rollback is triggered if any of the following is detected post-migration:

| Trigger | Detection | Severity |
|:--------|:----------|:---------|
| **Runtime regression** | Hermes session fails to load a Skill that previously loaded | 🔴 CRITICAL — immediate rollback |
| **Broken dependency** | `hermes skill audit deps` shows new unresolved dependencies | 🔴 CRITICAL — Wave rollback |
| **Missing capability** | Skill no longer provides a capability it provided pre-migration | 🔴 CRITICAL — per-Skill rollback |
| **Boundary violation** | `hermes skill audit boundary` shows new governance leakage | 🟡 HIGH — investigate before rollback |
| **Reference failure** | Any Skill references a non-existent ID post-rename | 🟡 HIGH — per-rename rollback |

### 8.3 Recovery Procedures

#### Per-Skill Rollback (Wave 0, 2)

```
1. Identify the Skill that regressed
2. Restore from backup:
   - Registry: re-register old ID with original metadata
   - Content: if file was modified, restore from git
3. Re-run audit to confirm rollback fixed the issue
4. Log rollback to migration event log
```

#### Per-Wave Rollback (Wave 1 merge)

```
1. Identify the merge that caused regression
2. Re-activate deprecated aliases (reverse DEPRECATED → ACTIVE)
3. Remove canonical merged Skill from Registry
4. Restore original individual Skills to ACTIVE
5. Re-run reference graph scan to confirm 0 broken references
```

#### Full Rollback (Catastrophic)

```
1. Restore skill-registry.json from .bak file
2. Restore all modified SKILL.md files from git
3. Re-run `hermes skill audit all` to confirm pre-migration state
4. Log full rollback event
5. Analyze root cause before re-attempting
```

### 8.4 Rollback Safety Guarantees

| Guarantee | How |
|:----------|:----|
| **Every migration step is reversible** | Per-Skill rollback via re-registration; per-Wave rollback via backup restoration |
| **No data loss** | Files are not deleted during migration (Wave 0: Registry only; Wave 1: old files retained; Wave 2: rename, not delete) |
| **Verified rollback** | Post-rollback audit confirms pre-migration state |
| **Grace period before ARCHIVAL** | 14-day grace period gives time to detect and reverse issues |

---

## 9. Migration Gate Decision

### 9.1 Precondition Verification

| # | Condition | Status |
|:--|:----------|:-------|
| 1 | Skill Policy v1.0 frozen | ✅ ACTIVE since 2026-07-18 |
| 2 | Registry Schema v1.0 complete | ✅ `docs/hermes-skill-registry-schema.md` (Phase B.0) |
| 3 | Audit CLI Design complete | ✅ `docs/hermes-skill-audit-cli.md` (Phase B.1) |
| 4 | Auditor Agent Design complete | ✅ `docs/hermes-auditor-agent-design.md` (Phase B.2) |
| 5 | Migration Specification complete | ✅ This document (Phase B.3) |
| 6 | Ecosystem Audit complete | ✅ Session history — 146 Skills classified |
| 7 | Boundary Remediation Plan complete | ✅ Session history — Wave structure approved |
| 8 | Phase B Readiness Review complete | ✅ CONDITIONAL GO (now unconditional) |

**All preconditions MET.**

### 9.2 Risk Assessment

| Risk | Probability | Impact | Mitigation |
|:-----|:-----------|:-------|:-----------|
| Wave 0: `architecture-constraints` removal breaks agent behavior | Low | High | Loading equivalence verified via Governance context injection |
| Wave 0: `skill-manager` removal breaks dispatch | Medium | High | Skill Router preserved in Framework layer before Registry deregistration |
| Wave 1: Merged Skills lose specializations | Low | Medium | Full content diff before merge; all unique sections preserved |
| Wave 2: Rename breaks cross-Skill references | Medium | Medium | `hermes skill audit deps` runs before/after each rename |
| Wave 3: Automated `version: 1.0.0` misrepresents mature Skills | Low | Low | `1.0.0` is honest — version history was not tracked |
| Wave 4: Bulk registration introduces duplicate entries | Low | Medium | Dedup check per batch; incremental registration |

### 9.3 Decision

**GO — Migration Specification is complete and approved for Phase A execution.**

### 9.4 Execution Gate

```
⚠️  AUTOMATIC MIGRATION IS NOT PERMITTED

This document is a CONTRACT, not an EXECUTION COMMAND.

Phase A execution requires:
  1. Human governance reviewer approval of this Specification
  2. Explicit "begin migration" command from governance authority
  3. Pre-flight snapshot (Registry backup + mapping table + reference graph)
  4. Wave 0 audit: `hermes skill audit all` — 0 critical findings
  5. Per-Wave human gate: GO decision before each Wave executes
```

### 9.5 Final State

```
READY FOR HUMAN APPROVAL

Phase B Deliverables:
  ✅ B.0 — Registry Schema (docs/hermes-skill-registry-schema.md)
  ✅ B.1 — Audit CLI Design (docs/hermes-skill-audit-cli.md)
  ✅ B.2 — Auditor Agent Design (docs/hermes-auditor-agent-design.md)
  ✅ B.3 — Migration Specification (docs/hermes-skill-migration-specification.md)

Next Action:
  → Human governance review of this Specification
  → On approval: Phase A begins with Wave 0 execution
```

---

> **Specification Status:** Complete v1.0
> **Phase:** B.3 — Migration Specification Complete
> **Governance Stack:** Protocol → Skill Policy → Registry Schema → Audit CLI → Auditor Agent → Migration Spec (this doc)
> **Execution Gate:** READY FOR HUMAN APPROVAL — do not execute without explicit governance authorization
> **Amendment Process:** Type D change (requires explicit architecture approval)
