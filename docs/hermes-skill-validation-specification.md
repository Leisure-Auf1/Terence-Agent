# Hermes Skill Validation Specification

**Status:** Draft — Governance Document
**Type:** Governance Design Documentation — Validation Contract
**Version:** 1.0.0
**Applies to:** Hermes Skill Migration Specification v1.0
**Created:** 2026-07-18
**Phase:** B.4 — Validation Specification Design

**Dependencies (completed):**
- Hermes Skill Governance Policy v1.0
- Hermes Skill Registry Schema v1.0 (Phase B.0)
- Hermes Skill Audit CLI Design v1.0 (Phase B.1)
- Hermes Auditor Agent Design v1.0 (Phase B.2)
- Hermes Skill Migration Specification v1.0 (Phase B.3)

**This document is:**
- A governance contract defining how migration correctness is verified
- A pre-execution specification — read-only, no modifications
- The final Phase B deliverable completing the governance toolchain

---

## 1. Validation Objective

### 1.1 Purpose

The Validation Specification defines how every migration step is verified before, during, and after execution. It ensures that the Migration Specification's safety contract (§2) is mechanically enforced — that every guarantee claimed by the migration is independently confirmed.

### 1.2 What Validation IS

| ✅ IS | Description |
|:------|:------------|
| **Correctness confirmation** | Proves that a migration step achieved its stated objective without regression |
| **Gate enforcement** | Blocks migration progression when verification fails |
| **Evidence collection** | Produces auditable proof that migration invariants hold |
| **Rollback trigger** | Provides objective criteria for when rollback is required |

### 1.3 What Validation IS NOT

| ❌ IS NOT | Distinction |
|:----------|:------------|
| **Audit** | Audit *detects* problems in the current state. Validation *confirms* that a migration resolved those problems correctly. Audit runs before migration; Validation runs after each migration step. |
| **Migration** | Migration *applies* changes. Validation *verifies* that the changes were correct. They are distinct phases separated by a gate. |
| **Runtime test** | Validation checks metadata, references, and boundary integrity. It does not execute Skills in a Hermes session or test functional behavior. Runtime testing is a separate concern. |
| **Governance authority** | Validation reports pass/fail. It does not approve or reject — the Governance Layer makes decisions based on validation output. |
| **Executor** | Validation is a verification step, not an action. It does not modify files, Registry, or Skill content. |

### 1.4 Relationship to Other Tools

```
                    ┌──────────────────┐
                    │      AUDIT       │  ← "What problems exist?"
                    │  (detection)     │
                    └────────┬─────────┘
                             │ findings
                             ▼
                    ┌──────────────────┐
                    │ AUDITOR AGENT    │  ← "What should we do about them?"
                    │  (classification)│
                    └────────┬─────────┘
                             │ recommendations
                             ▼
                    ┌──────────────────┐
                    │    MIGRATION     │  ← "Apply the approved changes"
                    │  (execution)     │
                    └────────┬─────────┘
                             │
                    ┌────────▼─────────┐
                    │   VALIDATION     │  ← "Did the changes work correctly?"
                    │  (verification)  │
                    └────────┬─────────┘
                             │ pass/fail
                             ▼
                    ┌──────────────────┐
                    │ GOVERNANCE GATE  │  ← "Proceed or rollback?"
                    │  (decision)      │
                    └──────────────────┘
```

Audit → Auditor → Migration → Validation → Gate. Each step is distinct and sequential.

---

## 2. Validation Architecture

### 2.1 Position in Governance Stack

```
┌──────────────────────────────────────────────────────────────┐
│                    GOVERNANCE LAYER                           │
│         (approval authority, rollback decisions)              │
└──────────────────────────┬───────────────────────────────────┘
                           │
┌──────────────────────────▼───────────────────────────────────┐
│                   VALIDATION LAYER                            │
│              (correctness verification)                       │
│                                                               │
│  ┌─────────────────┐  ┌──────────────┐  ┌──────────────────┐ │
│  │ Registry Check  │  │Boundary Check│  │Dependency Check  │ │
│  │                 │  │              │  │                  │ │
│  │ Schema valid?   │  │ Governance   │  │ References       │ │
│  │ Fields present? │  │ leakage = 0? │  │ resolved?        │ │
│  │ Lifecycle ok?   │  │ Runtime      │  │ No circular      │ │
│  │ No orphans?     │  │ replace = 0? │  │ deps?            │ │
│  └────────┬────────┘  └──────┬───────┘  └────────┬─────────┘ │
│           │                  │                    │           │
│           └──────────────────┼────────────────────┘           │
│                              │                                │
│                    ┌─────────▼──────────┐                     │
│                    │  MIGRATION GATE    │                     │
│                    │  GO / NO-GO        │                     │
│                    └────────────────────┘                     │
└──────────────────────────────────────────────────────────────┘
```

### 2.2 Validation Layer Boundaries

```
Validation ≠ Governance Authority
  → Validation reports pass/fail. Governance decides GO/NO-GO.

Validation ≠ Executor
  → Validation reads and checks. It never writes, moves, or modifies.

Validation ≠ Migration Tool
  → Validation verifies migration output. It never executes migration steps.
```

---

## 3. Pre-Migration Validation

### 3.1 Objective

Before ANY migration Wave executes, capture a complete snapshot of the current state. This snapshot is the **baseline** against which all post-migration validation is measured.

### 3.2 Registry Snapshot

#### Capture

```yaml
# docs/migration/snapshots/registry-pre.yaml
# Generated before Wave 0 execution

before_state:
  timestamp: "2026-07-18T00:00:00Z"
  registry:
    file: "skill-manager/skill-registry.json"
    format: "json"
    entries: 14
    fields_per_entry: 6
    policy_coverage: "2/12 (17%)"
  skills_on_disk:
    total: 146
    categories: 41
    with_version: 91
    without_version: 55
    registered: 14
    unregistered: 132
  critical_findings:
    class_c_governance_leakage: 8
    class_e_project_coupled: 21
    duplicate_groups: 10
```

#### Validation Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| R1 | Registry backup exists | `stat skill-manager/skill-registry.json.bak-*` | File exists and is non-empty |
| R2 | Backup is valid JSON | `jq . skill-manager/skill-registry.json.bak-*` | Parses without error |
| R3 | Backup entry count matches current | Compare entry counts | Equal |
| R4 | Schema compatibility documented | Read migration spec §9 (migration mapping) | Mapping table exists |

### 3.3 Dependency Snapshot

#### Capture

Before migration, capture the full dependency graph:

```yaml
# docs/migration/snapshots/dependency-graph-pre.yaml

dependency_graph:
  skills:
    - id: "browser-automation"
      parent: null
      children: ["layer1-playwright", "layer2-cdp-harness", "layer3-browser-use", "layer4-screenshot-vision"]
      references_to: []
      referenced_by: ["layer1-playwright", "layer2-cdp-harness"]
    - id: "ucampus-auto-complete"
      parent: null
      children: []
      fallback: null
      references_to: ["uai.unipus.cn"]
    # ... 146 entries
  trigger_mappings:
    - trigger: "webpage"
      skills: ["browser-automation"]
    - trigger: "ucampus"
      skills: ["ucampus-auto-complete", "u-campus-course-automation"]
  alias_mappings: []  # None pre-migration
```

#### Validation Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| D1 | All `parent` references resolve | For each `parent` field, verify target exists | 0 unresolved parents |
| D2 | All `fallback` references resolve | For each `fallback` field, verify target exists | 0 unresolved fallbacks |
| D3 | No circular parent chains | Graph traversal: parent → parent → ... | No cycles |
| D4 | Reference graph is complete | Every Skill referenced by another exists | 0 dangling references |

### 3.4 Boundary Baseline

#### Capture

Run the full audit suite and save the output:

```bash
hermes skill audit all --format json --output docs/migration/snapshots/audit-pre.json
```

Extract and record:

```yaml
# docs/migration/snapshots/boundary-baseline-pre.yaml

boundary_baseline:
  class_c_findings:
    count: 8
    skills:
      - agent-governance-protocol
      - architecture-constraints
      - guidance-agent
      - error-registry
      - skill-manager
      - harness-preflight
      - task-progress
      - agent-logger
  class_e_findings:
    count: 21
    groups:
      veritas_core: 1
      a3_project: 5
      ucampus: 2
      other: 13
  duplicate_groups:
    count: 10
    triple_duplicates: 3
  metadata_gaps:
    no_version: 55
    no_owner: 146
    no_permissions: 146
    no_validation: 146
```

#### Validation Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| B1 | Audit output saved | File exists at snapshot path | Non-empty JSON |
| B2 | Class C count matches known | Compare with Ecosystem Audit Report | 8 Class C findings |
| B3 | Duplicate groups match known | Compare with Ecosystem Audit Report | 10 groups (3 triple) |
| B4 | Metadata gaps match known | Compare with Ecosystem Audit Report | 55 no-version, 146 no-owner |

---

## 4. Wave Validation Gates

### 4.1 Gate Structure

Every Wave follows the same gate structure:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PRE-GATE    │────▶│   EXECUTE    │────▶│  POST-GATE   │
│  Validation  │     │   Wave N     │     │  Validation  │
└──────────────┘     └──────────────┘     └──────┬───────┘
                                                 │
                                          ┌──────▼───────┐
                                          │  Gate Decision│
                                          │ GO / NO-GO    │
                                          └──────────────┘
```

If POST-GATE fails → ROLLBACK → re-run PRE-GATE to confirm restoration.

### 4.2 Wave 0 Gate — Class C Relocation

#### Pre-Gate Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| W0.1 | All 8 Class C Skills exist in Registry | Registry lookup confirms all 8 entries |
| W0.2 | All 8 Class C Skills have `mount` values | `always` (3), `auto` (2), `routed` (3) |
| W0.3 | Governance, Framework, Memory target layers documented | Migration Spec §3.2 table complete |
| W0.4 | Backup snapshot taken | Pre-migration validation (§3) complete |

#### Post-Gate Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| W0.5 | 8 Class C Skills removed from Registry | `hermes skill audit registry` | 0 Class C Skills in Registry |
| W0.6 | Governance loading preserved | Check constraints enforcement | Architecture constraints still enforced |
| W0.7 | Framework routing preserved | Check Skill dispatch | Skills still route correctly |
| W0.8 | Memory retrieval preserved | Check error lookup | Error records retrievable via Memory |
| W0.9 | No files deleted | `stat` each original SKILL.md path | All 8 files still exist |
| W0.10 | No capability lost | Compare pre/post capability list | All capabilities preserved |
| W0.11 | No behavior changed | Load test each relocated component | Equivalent output |
| W0.12 | Registry entry count | Count entries | 14 → 6 (8 Class C removed) |

#### Gate Decision

```
GO if:
  ✅ W0.5-W0.12 all pass
  ✅ No new critical findings from `hermes skill audit boundary`

NO-GO if:
  ❌ Any check fails
  ❌ Governance loading regression detected
  ❌ Skill dispatch broken
  → ROLLBACK via re-registration
```

### 4.3 Wave 1 Gate — Duplicate Merge

#### Pre-Gate Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| W1.1 | All 10 duplicate groups documented | Migration Spec §4.2 table complete |
| W1.2 | Merge targets defined | 3 canonical Skill names chosen |
| W1.3 | Content diff completed | Unique sections identified across all source Skills |
| W1.4 | Reference scan complete | All references to old IDs identified |

#### Post-Gate Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| W1.5 | Canonical Skills exist in Registry | Registry lookup | 3 new Skills registered |
| W1.6 | Canonical Skills contain all unique content | Content comparison | No unique section lost |
| W1.7 | Old IDs are DEPRECATED | Registry lifecycle field | `lifecycle: deprecated` |
| W1.8 | `replaced_by` points to canonical Skill | Registry field | `replaced_by: multi-agent-pipeline` etc. |
| W1.9 | Old IDs still loadable | Skill Manager load test | DEPRECATED Skills load with warning |
| W1.10 | All references updated | `hermes skill audit deps` | 0 references to old IDs |
| W1.11 | Alias chain works: old → alias → new | Reference resolution test | `old_id → replaced_by → canonical` resolves |
| W1.12 | No duplicate capability findings remain | `hermes skill audit dupes` | 0 exact duplicates |

#### Gate Decision

```
GO if:
  ✅ W1.5-W1.12 all pass
  ✅ Alias chain resolves for all old IDs
  ✅ No capability loss detected

NO-GO if:
  ❌ Any check fails
  ❌ Content lost in merge
  ❌ Reference chain broken
  → ROLLBACK: re-activate DEPRECATED Skills to ACTIVE
```

### 4.4 Wave 2 Gate — Project Decoupling

#### Pre-Gate Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| W2.1 | 6 rename targets documented | Migration Spec §5.3 table complete |
| W2.2 | New capability names follow naming convention | `^[a-z0-9]+(-[a-z0-9]+)*$` |
| W2.3 | All hardcoded paths identified | Path scan complete |

#### Post-Gate Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| W2.5 | New IDs exist in Registry | Registry lookup | All renamed Skills registered |
| W2.6 | Old IDs are DEPRECATED with `replaced_by` | Registry lifecycle + replaced_by | All old IDs point to new IDs |
| W2.7 | No hardcoded project paths in Skill bodies | Content scan: `~/Terence-Agent`, `~/A3-`, `~/Veritas-Core` | 0 matches |
| W2.8 | No hardcoded project paths in Skill names | Name scan: `a3-*`, `veritas-*` | 0 matches (except ucampus — platform adapter) |
| W2.9 | New names are descriptive of capability | Name inspection | `agent-runtime-development` describes capability, not project |
| W2.10 | All references to old IDs resolved | `hermes skill audit deps` | 0 broken references |
| W2.11 | Capability scope unchanged | Compare pre/post description and triggers | Triggers match; capability domain unchanged |

#### Gate Decision

```
GO if:
  ✅ W2.5-W2.11 all pass
  ✅ 0 hardcoded project paths in names or bodies
  ✅ All references migrated

NO-GO if:
  ❌ Any check fails
  ❌ Hardcoded paths persist
  ❌ Reference broken
  → ROLLBACK: re-activate old IDs; re-insert paths if needed
```

### 4.5 Wave 3 Gate — Metadata Completion

#### Pre-Gate Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| W3.1 | 55 no-version Skills identified | Audit output confirms count |
| W3.2 | Auto-populated field defaults documented | Migration Spec §6.2 table complete |
| W3.3 | Human-confirmed fields identified | Migration Spec §6.3 table complete |

#### Post-Gate Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| W3.5 | All Skills have `version` field | `hermes skill audit metadata` | 0 missing `version` |
| W3.6 | All `version` values are valid semver | Schema validation: `^\d+\.\d+\.\d+$` | All pass |
| W3.7 | Auto-populated fields present and valid | Field check | `status`, `registered`, `updated` all valid |
| W3.8 | Auto-generated fields marked | Metadata annotation | `source: auto-generated` on auto fields |
| W3.9 | Human-confirmed fields marked | Metadata annotation | `source: human-confirmed` or `source: pending` |
| W3.10 | No auto-population overwrote existing data | Diff pre/post for Skills that had versions | Existing version values unchanged |

#### Field Source Tracking

| Field | Source | Marked |
|:------|:-------|:-------|
| `version` | auto-generated (default: `1.0.0`) or human-confirmed (if pre-existing) | ✅ |
| `status` | auto-generated (default: `ok`) | ✅ |
| `registered` | auto-generated (migration date) | ✅ |
| `updated` | auto-generated (migration date) | ✅ |
| `owner` | human-confirmed (default: `null`) | ✅ |
| `permissions` | human-confirmed (default: `null`) | ✅ |
| `compatibility` | human-confirmed (default: `null`) | ✅ |
| `validation` | human-confirmed (default: `null`) | ✅ |

#### Gate Decision

```
GO if:
  ✅ W3.5-W3.10 all pass
  ✅ 0 Skills without version
  ✅ Auto vs human source clearly distinguished

NO-GO if:
  ❌ Any Skill still missing version
  ❌ Auto-population corrupted existing data
  → ROLLBACK: restore pre-Wave 3 metadata state
```

### 4.6 Wave 4 Gate — Registry Completion

#### Pre-Gate Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| W4.1 | All unregistered Skills pass Schema validation | `hermes skill audit metadata` per Skill | 0 required field errors |
| W4.2 | All unregistered Skills pass Boundary audit | `hermes skill audit boundary` per Skill | 0 critical/high findings |
| W4.3 | All unregistered Skills pass Dependency scan | `hermes skill audit deps` per Skill | 0 undeclared/circular/archived deps |
| W4.4 | No duplicate capabilities in registration batch | `hermes skill audit dupes` | 0 exact duplicates |

#### Post-Gate Checks

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| W4.5 | Registry entry count = 138 | Count entries | 138 entries |
| W4.6 | All required fields present on all entries | `hermes skill audit metadata --skills-root skills/` | 0 missing required fields |
| W4.7 | No duplicate Skill names | `hermes skill audit registry` | 0 duplicate name errors |
| W4.8 | No orphan entries (Registry entry without file) | `hermes skill audit registry` | 0 orphans |
| W4.9 | No ghost Skills (file without Registry entry) | `hermes skill audit registry` | 0 ghosts |
| W4.10 | Registry Schema coverage = 12/12 | Field coverage check | All Policy §9 fields present |
| W4.11 | All boundary violations resolved | `hermes skill audit boundary` | 0 critical/high Class C findings |
| W4.12 | Full audit clean | `hermes skill audit all` | 0 critical, 0 error |

#### Gate Decision

```
GO if:
  ✅ W4.5-W4.12 all pass
  ✅ Registry: 138/138 entries, 12/12 fields
  ✅ `hermes skill audit all` returns exit code 0

NO-GO if:
  ❌ Any check fails
  ❌ Entry count != 138
  ❌ Audit not clean
  → ROLLBACK: restore pre-Wave 4 Registry state
```

---

## 5. Post-Migration Validation

### 5.1 Objective

After all Waves complete, run a comprehensive validation suite to confirm the migration achieved its objectives.

### 5.2 Registry Validation

#### Target

```
Before: 14/146 registered, 2/12 fields
After:  138/138 registered, 12/12 fields
```

#### Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| P1 | Registered Skills = total Skills on disk (minus relocated Class C) | 138 entries |
| P2 | Missing required fields = 0 | `hermes skill audit metadata` clean |
| P3 | Invalid references = 0 | `hermes skill audit deps` clean |
| P4 | Schema coverage = 12/12 | All Policy §9 fields present |
| P5 | Registry format migrated (JSON → YAML if applicable) | `skill-registry.yaml` is valid YAML |

### 5.3 Boundary Validation

#### Target

Four boundary violations must be zero:

| Boundary | Pre-Migration | Post-Migration Target |
|:---------|:-------------|:----------------------|
| Skill → Governance leakage | 8 Skills | **0** |
| Skill → Runtime expansion | 0 Skills (no Class D found) | **0** (preserved) |
| Skill → Agent authority claim | 1 Skill (guidance-agent) | **0** |
| Skill → Framework ownership confusion | 2 Skills (skill-manager, agent-logger) | **0** |

#### Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| P6 | Governance leakage = 0 | `hermes skill audit boundary` — 0 SKILL-B001/B002/B003 findings |
| P7 | Runtime expansion = 0 | `hermes skill audit boundary` — 0 SKILL-B004 findings |
| P8 | Agent authority = 0 | No Skill claims exclusive tool access |
| P9 | Framework confusion = 0 | No Skill implements routing/dispatch/agent registration |

### 5.4 Capability Preservation Validation

#### Target

Every capability available pre-migration must remain available post-migration.

#### Method

1. Extract capability list from pre-migration snapshot
2. Extract capability list from post-migration Registry
3. Diff: pre ∖ post must be empty (no capability lost)
4. Diff: post ∖ pre must contain ONLY merged/renamed capabilities (expected additions)

#### Checks

| # | Check | Pass Condition |
|:--|:------|:---------------|
| P10 | Same triggers as pre-migration | Trigger mapping diff = 0 unexpected changes |
| P11 | Same capability domains | Capability list pre ∖ post = ∅ |
| P12 | Same usage paths | Skill Manager resolves same trigger → same capability path |
| P13 | Merged Skills provide all original capabilities | Canonical Skill capability list ⊇ union of merged Skill capability lists |

### 5.5 Reference Integrity Validation

| # | Check | Pass Condition |
|:--|:------|:---------------|
| P14 | No dangling parent references | All `parent` fields resolve |
| P15 | No dangling fallback references | All `fallback` fields resolve |
| P16 | All `replaced_by` chains terminate at ACTIVE Skill | Deprecated → ... → ACTIVE chain complete |
| P17 | No references to archived Skills (beyond grace period) | All references to ARCHIVED Skills resolved or documented |

---

## 6. Rollback Validation

### 6.1 Rollback Triggers

Rollback is triggered when post-migration validation detects any of the following:

| Trigger | Detection Method | Severity |
|:--------|:-----------------|:---------|
| **Runtime behavior regression** | Load test fails — Skill that loaded pre-migration fails post-migration | 🔴 CRITICAL |
| **Missing capability** | Capability preservation check (P10-P13) fails | 🔴 CRITICAL |
| **Broken reference** | Reference integrity check (P14-P17) fails | 🔴 CRITICAL |
| **Boundary violation** | Boundary check (P6-P9) shows NEW governance leakage | 🔴 CRITICAL |
| **Registry corruption** | Registry validation (P1-P5) fails | 🔴 CRITICAL |
| **Unexpected file modification** | File checksum differs from pre-migration snapshot | 🟡 HIGH |
| **Duplicate entry** | Two Skills with same name in Registry | 🟡 HIGH |

### 6.2 Rollback Validation Procedure

After rollback executes, validate that the pre-migration state is restored:

| # | Check | Method | Pass Condition |
|:--|:------|:-------|:---------------|
| RB1 | Registry restored to pre-migration state | `diff skill-registry.json skill-registry.json.bak-*` | No diff |
| RB2 | Alias mappings restored | DEPRECATED Skills → ACTIVE | All old IDs active |
| RB3 | All references resolve | `hermes skill audit deps` | 0 broken refs |
| RB4 | Audit matches pre-migration baseline | `diff audit-pre.json audit-post-rollback.json` | No new findings |
| RB5 | File integrity preserved | Checksum comparison | All files match pre-migration checksums |
| RB6 | Loading equivalence restored | Load test | All Skills load correctly |

### 6.3 Rollback Decision Gate

```
After rollback:
  → RB1-RB6 all pass → ROLLBACK SUCCESSFUL
  → Any check fails → ROLLBACK FAILED → escalate to manual recovery
```

---

## 7. Human Approval Checklist

### 7.1 Before Migration Execution

| # | Check | Status |
|:--|:------|:-------|
| H1 | Migration Specification reviewed and approved | ☐ |
| H2 | Validation Specification reviewed and approved | ☐ |
| H3 | Pre-migration snapshots taken (Registry + Dependency + Boundary) | ☐ |
| H4 | Rollback procedures documented and tested | ☐ |
| H5 | Migration scope understood (146 → 138, Waves 0-4) | ☐ |
| H6 | Risk assessment reviewed and accepted | ☐ |
| H7 | Wave 0 execution authorization granted | ☐ |

### 7.2 Before Each Wave

| # | Check | Status |
|:--|:------|:-------|
| H8 | Pre-gate validation passed for this Wave | ☐ |
| H9 | Rollback plan for this Wave reviewed | ☐ |
| H10 | Wave execution authorization granted | ☐ |

### 7.3 After Each Wave

| # | Check | Status |
|:--|:------|:-------|
| H11 | Post-gate validation passed for this Wave | ☐ |
| H12 | Audit report reviewed | ☐ |
| H13 | No unexpected findings | ☐ |
| H14 | Next Wave authorized | ☐ |

### 7.4 After Full Migration

| # | Check | Status |
|:--|:------|:-------|
| H15 | Post-migration validation suite passed (§5) | ☐ |
| H16 | `hermes skill audit all` clean (0 critical, 0 error) | ☐ |
| H17 | Registry: 138/138 entries, 12/12 fields | ☐ |
| H18 | Capability preservation confirmed | ☐ |
| H19 | Boundary integrity confirmed | ☐ |
| H20 | Migration event logged to Governance record | ☐ |

---

## 8. Validation Metrics

### 8.1 Target Metrics

| # | Metric | Pre-Migration | Post-Migration Target |
|:--|:-------|:-------------|:----------------------|
| M1 | Registry Schema Compliance | 17% (2/12 fields) | **100%** (12/12 fields) |
| M2 | Skills Registered | 14 (9.6%) | **138** (100%) |
| M3 | Critical Boundary Violations | 8 Class C Skills | **0** |
| M4 | Broken References | Unknown (not measured) | **0** |
| M5 | Capability Loss | N/A (baseline) | **0** |
| M6 | Rollback Availability | N/A | **100%** (all Waves reversible) |
| M7 | Duplicate Canonicalization | 10 groups unresolved | **Complete** (3 retained) |
| M8 | Metadata Completeness (version) | 62% (91/146) | **100%** (138/138) |
| M9 | Project Path Coupling | 21 Skills | **13** (platform/domain retainers only) |
| M10 | Governance Boundary Integrity | Violated (8 Skills) | **Preserved** (0 violations) |

### 8.2 Metric Tracking

Each metric is tracked per-Wave:

| Metric | Wave 0 | Wave 1 | Wave 2 | Wave 3 | Wave 4 | Final |
|:-------|:------:|:------:|:------:|:------:|:------:|:-----:|
| M1 (Schema) | 17% | 17% | 17% | 100% | 100% | 100% |
| M2 (Registered) | 14 | 17 | 20 | 20 | 138 | 138 |
| M3 (Boundary) | 8→0 | 0 | 0 | 0 | 0 | 0 |
| M4 (Broken Refs) | 0 | 0 | 0 | 0 | 0 | 0 |
| M5 (Capability) | 146→146 | 146→138 | 138 | 138 | 138 | 0 loss |
| M8 (Version) | 62% | 62% | 62% | 100% | 100% | 100% |
| M9 (Coupling) | 21 | 21 | 21→15 | 15 | 13 | 13 |

---

## 9. Final Gate Decision

### 9.1 Phase B Deliverables Status

| # | Deliverable | Document | Status |
|:--|:------------|:---------|:-------|
| 1 | Skill Policy | `docs/hermes-skill-policy.md` | ✅ ACTIVE v1.0 |
| 2 | Registry Schema | `docs/hermes-skill-registry-schema.md` | ✅ B.0 Complete |
| 3 | Audit CLI Design | `docs/hermes-skill-audit-cli.md` | ✅ B.1 Complete |
| 4 | Auditor Agent Design | `docs/hermes-auditor-agent-design.md` | ✅ B.2 Complete |
| 5 | Migration Specification | `docs/hermes-skill-migration-specification.md` | ✅ B.3 Complete |
| 6 | Validation Specification | `docs/hermes-skill-validation-specification.md` | ✅ B.4 Complete |

### 9.2 Gate Decision

```
✅ Registry Schema Ready          — 14-field contract defined
✅ Audit CLI Ready                — 45 rules, 5 modules designed
✅ Auditor Agent Ready            — Inspection intelligence layer defined
✅ Migration Specification Ready  — Waves 0-4, 146→138 execution plan
✅ Validation Specification Ready — Pre/post/Wave gates, rollback, metrics

All Phase B deliverables COMPLETE.
```

### 9.3 Final State

```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   READY FOR MIGRATION EXECUTION REVIEW                       ║
║                                                              ║
║   Phase B complete: 6 governance documents                   ║
║   Phase A execution: pending human governance approval       ║
║                                                              ║
║   Next step:                                                 ║
║     1. Human governance review of all Phase B deliverables   ║
║     2. Explicit "begin Phase A" authorization                ║
║     3. Pre-migration snapshot capture (§3)                   ║
║     4. Wave 0 execution                                      ║
║                                                              ║
║   ⚠️  DO NOT execute migration without authorization         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
```

---

> **Specification Status:** Complete v1.0
> **Phase:** B.4 — Final Phase B deliverable
> **Governance Stack:** Protocol → Policy → Registry → Audit → Auditor → Migration → Validation (this doc)
> **Execution Gate:** READY FOR MIGRATION EXECUTION REVIEW
> **Amendment Process:** Type D change (requires explicit architecture approval)
