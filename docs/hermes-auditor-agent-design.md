# Hermes Auditor Agent Design Specification

**Status:** Draft — Design Document
**Type:** Governance Design Documentation — Agent Contract
**Version:** 1.0.0
**Applies to:** Hermes Skill Policy §6, §8, §9
**Created:** 2026-07-18
**Phase:** B.2 — Auditor Agent Design Specification

**Dependencies:**
- Hermes Skill Governance Policy v1.0
- Hermes Skill Registry Schema v1.0 (Phase B.0)
- Hermes Skill Audit CLI Design v1.0 (Phase B.1)
- Hermes Architecture Constraints (boundary violation catalog)

---

## 1. Auditor Agent Positioning

### 1.1 Architectural Layer

The Auditor Agent occupies a distinct architectural layer: **Inspection Intelligence**. It is not a Skill, not a Framework component, and not a Governance authority.

```
═══════════════════════════════════════════════════════════════
                   GOVERNANCE LAYER
                   (rules + authority)
═══════════════════════════════════════════════════════════════
                          │
         ┌────────────────┼────────────────┐
         │                │                │
         ▼                ▼                ▼
    Governance       Human Review      Policy Engine
    Protocol          Authority         (enforcement)
                          │
═══════════════════════════┼═══════════════════════════════════
           INSPECTION LAYER│(read-only)
═══════════════════════════┼═══════════════════════════════════
                          │
                          ▼
              ┌───────────────────────┐
              │   AUDITOR AGENT       │  ← THIS DOCUMENT
              │                       │
              │  Classification       │
              │  Prioritization       │
              │  Recommendation       │
              │  Report Generation    │
              └───────────┬───────────┘
                          │
                          │ reads
                          ▼
              ┌───────────────────────┐
              │     AUDIT CLI         │
              │   (mechanical scan)   │
              └───────────┬───────────┘
                          │
                          │ reads
                          ▼
═══════════════════════════╤═══════════════════════════════════
              DATA LAYER   │
═══════════════════════════╪═══════════════════════════════════
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
         Registry     SKILL.md      Skill Files
       (metadata)   (content)    (implementations)
═══════════════════════════════════════════════════════════════
```

### 1.2 What the Auditor Agent IS

| ✅ IS | Description |
|:------|:------------|
| **Inspection intelligence** | Reads raw audit findings and applies classification logic that raw CLI cannot (context-aware, cross-finding correlation, pattern recognition) |
| **Triage layer** | Prioritizes findings by governance impact, not just severity — maps SKILL-B001 (governance leakage) above SKILL-M003 (description too long) regardless of CLI severity |
| **Recommendation engine** | Produces actionable, specific governance recommendations with required approval levels |
| **Report generator** | Produces structured Governance Finding Reports formatted for human review |
| **Gate advisor** | Evaluates Wave readiness based on multi-dimensional criteria (not just "zero critical") |
| **Read-only agent** | All operations are reads — reads findings, reads Skills, reads Registry. Never writes. |

### 1.3 What the Auditor Agent IS NOT

| ❌ IS NOT | Rationale |
|:----------|:----------|
| **Skill** | The Auditor does not extend Hermes with a reusable capability domain. It is a governance inspection function, not a capability extension. Skills are operational; the Auditor is regulatory. |
| **Framework component** | The Auditor is not part of the UAF or any abstract framework. It is a concrete Hermes governance tool. |
| **Governance authority** | The Auditor recommends; it does not decide. Governance authority belongs to the Governance Protocol and human reviewers. |
| **Executor** | The Auditor does not run Skills, execute commands, or perform operations. It reads and reports. |
| **Migration Tool** | The Auditor identifies and classifies; it never performs migration actions (rename, merge, move, delete). |
| **Policy Engine** | The Auditor applies policy in analysis; it does not enforce policy at runtime. Enforcement is the Governance Engine's domain. |
| **Registry Writer** | The Auditor never modifies `skill-registry.json`, never adds/removes entries, never changes lifecycle states. |

### 1.4 Why No Migration Authority

| Reason | Explanation |
|:-------|:------------|
| **Inspection ≠ Action** | The Auditor's role is to *understand* the problem, not *fix* it. Migration is a separate concern executed by a separate tool under human supervision. |
| **Classification ≠ Decision** | The Auditor classifies findings; the Governance Layer decides what to do about them. |
| **Analysis Independence** | If the Auditor could also migrate, its analysis would be compromised by execution bias — it would classify findings to minimize its own migration workload. |
| **Rollback Safety** | Migration decisions must be reversible; audit analysis is inherently non-destructive. Separating them ensures clean rollback semantics. |
| **Audit Trail Integrity** | The Auditor's output is evidence for governance decisions. If it also performed migrations, the evidence and the action would be conflated. |

### 1.5 Relationship to Audit CLI

| Aspect | Audit CLI | Auditor Agent |
|:-------|:----------|:--------------|
| **Nature** | Mechanical tool | Intelligent agent |
| **Input** | Registry + Skill files | Audit CLI output (raw findings) |
| **Processing** | Rule-based pattern matching | Context-aware classification + correlation |
| **Output** | Raw findings (rule triggered → finding) | Governance recommendations (classified + prioritized + actionable) |
| **Intelligence** | Deterministic — same input → same output | Interpretive — same input may produce different recommendations based on context |
| **False positive handling** | Reports `false_positive_risk: low/medium/high` | Cross-references findings, reduces false positives through correlation |

---

## 2. Input Contract

### 2.1 Source

The Auditor Agent receives its input from the Audit CLI's structured output. The canonical format is JSON (`hermes skill audit --format json`).

### 2.2 Input Schema

Each finding from the Audit CLI is a structured object:

```yaml
finding:
  finding_id:   "20260718-001"           # Unique finding identifier (CLI-generated)
  rule_id:      "SKILL-B001"             # Audit rule that triggered
  module:       "boundary"               # Audit module: metadata|boundary|deps|dupes|registry
  skill_id:     "browser-automation"     # Skill name (null for Registry-level findings)
  category:     "governance_leakage"     # Finding category (see §2.3)
  severity:     "critical"               # CLI severity: critical|error|warning|info
  evidence:                              # What triggered the rule
    file:       "skills/browser-automation/SKILL.md"
    line:       42
    content:    "governance_rules: allow_auto_approve"
    match:      "governance_rules"
  confidence:   0.95                     # 0.0–1.0 confidence in this finding
  false_positive_risk: "low"            # low|medium|high
  policy_ref:   "Policy §2.3"            # Policy reference
  recommendation: "Remove governance..."  # CLI's mechanical recommendation
```

### 2.3 Finding Categories

The Audit CLI categorizes findings into these domains. The Auditor Agent receives these as-is:

| Category | Description | Source Rules |
|:---------|:------------|:-------------|
| `governance_leakage` | Skill contains governance rules, workflow overrides, or system prompt injection | SKILL-B001, B002, B003 |
| `runtime_replacement` | Skill implements alternative execution engine | SKILL-B004 |
| `permission_overreach` | Skill requests Tier 3 permissions or wildcard grants | SKILL-B005, M012 |
| `mega_skill` | Skill has too many capability domains | SKILL-B006 |
| `metadata_gap` | Required field missing or invalid | SKILL-M001–M014 |
| `hidden_dependency` | Skill uses another Skill or project path without declaring | SKILL-D001, D002, D003 |
| `invalid_dependency` | Dependency on unregistered, deprecated, or archived Skill | SKILL-D004–D007 |
| `circular_dependency` | Dependency graph contains cycles | SKILL-D005 |
| `duplicate_capability` | Two Skills share the same capability domain | SKILL-P001–P005 |
| `registry_integrity` | Registry contains orphans, ghosts, or invalid references | SKILL-R001–R010 |
| `project_coupling` | Skill hardcodes project-specific paths | SKILL-D002, D003 |
| `scope_creep` | Skill version history indicates expanding scope | SKILL-B008 |
| `excessive_coupling` | Skill has > 10 dependencies | SKILL-D008 |

### 2.4 Bulk Input (All-Module Audit)

When running `hermes skill audit all`, the Auditor receives a findings array:

```yaml
audit_result:
  metadata:
    timestamp: "2026-07-18T15:30:00Z"
    schema_version: "1.0.0"
    scope:
      skills_count: 14
      rules_executed: 45
  findings:                    # Array of finding objects (see §2.2)
    - finding_id: "20260718-001"
      rule_id: "SKILL-B001"
      ...
    - finding_id: "20260718-002"
      rule_id: "SKILL-M006"
      ...
```

---

## 3. Output Contract

### 3.1 Governance Finding Report

The Auditor Agent produces a **Governance Finding Report** — a structured, classified, and prioritized document intended for human governance review.

### 3.2 Report Schema

```yaml
governance_finding:
  finding_id:          "GF-20260718-001"        # Unique governance finding ID
  source_finding_ids:                            # Audit CLI findings this is based on
    - "20260718-001"
    - "20260718-007"
  classification:      "governance_leakage"      # Governance classification (see §3.3)
  severity:            "critical"                # Governance severity (see §4)
  affected_skills:                                # Skills involved
    - "browser-automation"
  rule_ids:                                      # Rules triggered
    - "SKILL-B001"
    - "SKILL-B003"
  
  # Core recommendation fields
  recommendation:      >
    Browser-automation Skill contains two governance declarations
    ('governance_rules' in SKILL.md:42 and 'system_prompt reference'
    in SKILL.md:156). These must be relocated to the Governance
    Protocol or removed entirely before Wave 0 migration.
  required_action:     "relocate_governance"     # Action type (see §3.4)
  approval_level:      "governance_reviewer"     # Who must approve (see §3.5)
  rollback_requirement: "none"                   # Rollback strategy (see §3.6)
  
  # Evidence and analysis
  evidence_summary:    >
    Two governance declarations found in browser-automation SKILL.md.
    First: 'governance_rules: allow_auto_approve' at line 42.
    Second: 'system_prompt: "Always use CDP first"' at line 156.
    Both are prohibited by Policy §2.3.
  false_positive_assessment: "confirmed"          # confirmed|likely|possible|ruled_out
  cross_finding_correlation:                      # Related findings
    - related_finding: "GF-20260718-003"
      relationship: "same_skill"
  
  # Migration impact
  wave_blocking:        true                     # Blocks which Wave
  blocks_wave:          0                        # Wave number blocked (null if none)
  
  # Metadata
  generated_at:         "2026-07-18T16:00:00Z"
  auditor_version:      "1.0.0"
```

### 3.3 Governance Classifications

The Auditor Agent maps raw finding categories to governance classifications. Classifications indicate the **governance significance**, not just technical severity:

| Classification | Definition | From Categories |
|:---------------|:-----------|:----------------|
| `governance_leakage` | Skill contains governance authority it must not possess | `governance_leakage`, `runtime_replacement` |
| `permission_violation` | Skill requests or implies permissions it must not have | `permission_overreach` |
| `structural_violation` | Skill structure violates isolation or single-responsibility rules | `mega_skill`, `scope_creep`, `excessive_coupling` |
| `dependency_anomaly` | Dependency declaration is missing, invalid, or problematic | `hidden_dependency`, `invalid_dependency`, `circular_dependency` |
| `project_coupling` | Skill is coupled to a specific project or file layout | `project_coupling` |
| `capability_conflict` | Two Skills compete for the same capability domain | `duplicate_capability` |
| `metadata_deficiency` | Required metadata field is missing or malformed | `metadata_gap` |
| `registry_anomaly` | Registry contains structural integrity issues | `registry_integrity` |

### 3.4 Required Action Types

| Action | Description | Example Trigger |
|:-------|:------------|:----------------|
| `relocate_governance` | Move governance declarations out of Skill, into Governance Protocol | Governance leakage finding |
| `remove_declaration` | Delete prohibited metadata or content from Skill | Permission overreach, system prompt injection |
| `declare_dependency` | Add missing dependency declaration to Skill metadata | Hidden dependency finding |
| `remove_dependency` | Remove invalid or project-specific dependency | Project coupling, unregistered dependency |
| `split_skill` | Split a Mega Skill into multiple single-responsibility Skills | Mega Skill finding |
| `merge_skills` | Merge two Skills with duplicate capabilities | Duplicate capability finding |
| `clarify_boundary` | Update capability descriptions to resolve overlap | Ambiguous capability overlap |
| `backfill_metadata` | Add missing optional field values | Metadata gap for Phase A fields |
| `fix_registry_entry` | Correct a Registry integrity issue | Orphan, ghost, or schema violation |
| `deprecate_skill` | Begin deprecation process for obsolete Skill | Replaced by another Skill |
| `no_action` | Finding is informational; no remediation needed | INFO-severity with ruled-out false positive |
| `human_review_required` | Finding requires human judgment beyond automated analysis | Ambiguous boundary violation, novel pattern |

### 3.5 Approval Levels

| Level | Who | Required For |
|:------|:----|:-------------|
| `automated` | No human approval needed | INFO findings with `no_action` |
| `skill_author` | Original Skill author | Metadata backfill, dependency declaration |
| `governance_reviewer` | Designated governance reviewer | Governance leakage, permission changes, Skill merges |
| `architecture_approval` | Architecture decision authority (Type D change) | Skill deletion, capability domain changes, lifecycle transitions |
| `full_review_board` | Multi-stakeholder review | Structural violations affecting > 3 Skills, Wave-go decision escalations |

### 3.6 Rollback Requirements

| Requirement | When Applied |
|:------------|:-------------|
| `none` | Read-only findings (no action taken) |
| `git_revert` | Changes that can be reverted via `git revert` |
| `registry_backup` | Registry modifications require backup before execution |
| `skill_backup` | Skill content modifications require backup before execution |
| `full_snapshot` | Multi-Skill changes require full `skills/` directory snapshot |
| `staged_rollback` | Changes must be applied in stages with validation between each stage |

---

## 4. Severity Model

### 4.1 Governance Severity Levels

The Auditor Agent applies its own severity classification, which may differ from the Audit CLI's mechanical severity. Governance severity reflects **impact on the migration and governance process**, not just technical correctness.

| Governance Severity | Meaning | Blocks Wave | CLI Severity Mapping |
|:--------------------|:--------|:------------|:---------------------|
| **Critical** | Must be resolved before ANY Wave can proceed. Represents a governance integrity threat. | YES — blocks Wave 0 | Always maps from CLI `critical` |
| **High** | Must be resolved before the current Wave can complete. Represents a structural issue. | YES — blocks current Wave | CLI `error` + certain classifications |
| **Medium** | Should be resolved but does not block Wave progression. Can be addressed in a subsequent Wave. | NO — deferred to later Wave | CLI `warning` + most classifications |
| **Low** | Nice-to-fix; no timeline pressure. | NO — backlog | CLI `warning` + informational classifications |
| **Info** | Observation only; may be a false positive. | NO — informational | CLI `info`, or upgraded from `warning` after false positive assessment |

### 4.2 Classification → Severity Mapping

| Governance Classification | Default Severity | Escalation Conditions |
|:--------------------------|:-----------------|:----------------------|
| `governance_leakage` | **Critical** | Always critical — no downgrade possible |
| `permission_violation` | **High** | Escalates to Critical if Tier 3 permission requested |
| `structural_violation` | **High** | Escalates to Critical if > 3 Skills affected |
| `dependency_anomaly` | **High** for circular; **Medium** for undeclared; **Low** for excessive count | Escalates to Critical if dep on archived Skill |
| `project_coupling` | **Medium** | Escalates to High if coupled to governance/config path |
| `capability_conflict` | **Medium** | Escalates to High if both Skills are `mount: always` |
| `metadata_deficiency` | **Low** for optional fields; **Medium** for required fields | Escalates to High if `name` or `lifecycle` missing |
| `registry_anomaly` | **Medium** | Escalates to High if orphan count > 5 |

### 4.3 Severity Downgrade Rules

The Auditor Agent may downgrade a CLI severity under specific, documented conditions:

| Condition | Downgrade | Rationale |
|:----------|:----------|:----------|
| `false_positive_assessment == "ruled_out"` | Any → Info | Finding is a confirmed false positive |
| `false_positive_assessment == "likely"` + no cross-finding correlation | Error → Warning | Single finding, likely spurious |
| Single keyword match in comment/example context | Critical → High | Governance keyword in "IS NOT" or documentation context |
| Duplicate finding (same issue, different rule) | One kept at original severity; duplicates → Info | Avoid double-counting one issue |

### 4.4 Multi-Finding Severity Escalation

When multiple findings affect the same Skill, the overall governance severity escalates:

| Pattern | Escalation |
|:--------|:-----------|
| 2+ Critical findings | → "CRITICAL — compound" |
| Critical + 3+ High | → "CRITICAL — compound" |
| 5+ High findings on one Skill | → "CRITICAL — structural" |
| 10+ findings of any severity on one Skill | → "HIGH — needs redesign" |

---

## 5. Decision Boundary

### 5.1 What the Auditor Agent CAN Do

| ✅ Permitted | Scope |
|:-------------|:------|
| **Read** audit findings, Registry, Skill files | Full read access to all governance data sources |
| **Classify** findings by governance significance | Classification logic + severity mapping |
| **Correlate** findings across Skills | Cross-finding correlation and deduplication |
| **Interpret** evidence context | Distinguish governance leakage from documentation references |
| **Recommend** actions with approval levels | `required_action` + `approval_level` + `rollback_requirement` |
| **Prioritize** by Wave impact | `wave_blocking` + `blocks_wave` |
| **Generate** Governance Finding Reports | Structured output per §3 |
| **Advise** on Wave gate decisions | GO / CONDITIONAL GO / BLOCKED recommendation |
| **Assess** false positive likelihood | `false_positive_assessment` field |
| **Output** to stdout, file, or structured channel | Same output paths as Audit CLI (`--format`, `--output`) |

### 5.2 What the Auditor Agent CANNOT Do

| ❌ Prohibited | Reason |
|:--------------|:-------|
| **Modify Registry** (`skill-registry.json`) | Write authority belongs to Migration Tool under governance supervision |
| **Delete Skill** (remove directory or file) | Destruction authority belongs to Governance Layer |
| **Merge Skills** (combine two into one) | Structural change — requires human design decision |
| **Move Skill** (relocate directory) | Filesystem change with dependency implications |
| **Rename Skill** (change `name` field) | Identity change — breaks all dependency references |
| **Change lifecycle state** (active → deprecated) | Lifecycle authority belongs to Governance Protocol |
| **Modify Skill content** (edit SKILL.md) | Content authority belongs to Skill author |
| **Execute migration** (any Wave action) | Migration execution belongs to Migration Tool |
| **Approve or reject** (make governance decisions) | Decision authority belongs to Governance Layer |
| **Add to Registry** (register new Skill) | Registration requires REVIEW → ACCEPT gate |

### 5.3 Decision Boundary Table

| Action | Audit CLI | Auditor Agent | Governance Layer | Migration Tool |
|:-------|:----------|:--------------|:-----------------|:---------------|
| Detect issues | ✅ | — | — | — |
| Classify by governance impact | — | ✅ | — | — |
| Recommend actions | — | ✅ | — | — |
| Approve actions | — | — | ✅ | — |
| Execute actions | — | — | — | ✅ |
| Verify results | ✅ (re-audit) | ✅ (re-classify) | ✅ (sign-off) | — |

---

## 6. Wave Gate Rules

### 6.1 Gate Decision Model

Each Wave gate is an **Auditor Agent recommendation**, not an automatic decision. The Auditor evaluates quantitative and qualitative criteria and outputs a gate recommendation: `GO`, `CONDITIONAL GO`, or `BLOCKED`.

### 6.2 Wave 0 Gate: Schema Compliance

**Gate Question:** Can we begin migration given the current Registry state?

#### Quantitative Criteria

| Criterion | Threshold for GO | Threshold for CONDITIONAL GO | BLOCKED If |
|:----------|:-----------------|:-----------------------------|:-----------|
| Critical findings | 0 | 0 | > 0 |
| Governance leakage findings | 0 | 0 | > 0 |
| High-severity findings | ≤ 2 | ≤ 5 | > 5 |
| Skills with `name` missing | 0 | 0 | > 0 |
| Skills with `lifecycle` invalid | 0 | ≤ 2 | > 2 |
| Registry orphans | 0 | ≤ 3 | > 3 |
| Required fields missing (total) | ≤ 5% of Skills | ≤ 15% of Skills | > 15% |

#### Qualitative Criteria

| Criterion | Requirement |
|:----------|:------------|
| All Critical findings reviewed by human | ✅ Required |
| All governance leakage findings assessed (even if confirmed false positive) | ✅ Required |
| Rollback plan exists for all proposed changes | ✅ Required |
| Migration Tool design complete and approved | ✅ Required |
| Backup strategy for `skill-registry.json` documented | ✅ Required |

#### Gate Output Example

```
Wave 0 Gate Assessment:
  Quantitative: CONDITIONAL GO (3 High findings, 0 Critical)
  Qualitative:  PASS (all reviews complete, rollback plan exists)
  Auditor Recommendation: CONDITIONAL GO
  Blockers: None
  Conditions:
    - Resolve 3 High-severity metadata gaps before proceeding
    - Re-run audit after fixes to confirm 0 High findings
```

### 6.3 Wave 1 Gate: Duplicate Resolution

**Gate Question:** Are capability conflicts resolved sufficiently to proceed?

#### Quantitative Criteria

| Criterion | Threshold for GO | Threshold for CONDITIONAL GO | BLOCKED If |
|:----------|:-----------------|:-----------------------------|:-----------|
| Exact duplicate capabilities | 0 | 0 | > 0 |
| Overlapping capabilities (> 80% similarity) | 0 | ≤ 2 | > 2 |
| Ambiguous overlaps (50-80% similarity) | ≤ 3 | ≤ 10 | > 10 |
| Merged Skills with unresolved references | 0 | 0 | > 0 |
| Deprecated Skills without replacement | 0 | ≤ 1 | > 1 |

#### Confidence Thresholds

| Finding Type | Auto-classify Threshold | Human Review Required Below |
|:-------------|:------------------------|:----------------------------|
| Exact duplicate (same `capability` value) | ≥ 0.95 confidence | < 0.95 |
| Strong overlap (> 80% description similarity) | ≥ 0.90 confidence | < 0.90 |
| Weak overlap (50-80% similarity) | Never auto-classified | Always human review |

#### Qualitative Criteria

| Criterion | Requirement |
|:----------|:------------|
| Merge decisions approved by governance reviewer | ✅ Required |
| Deprecation paths documented with replacement Skills | ✅ Required |
| No merge creates a dependency cycle | ✅ Required |
| Umbrella-child relationships validated (no false duplicate) | ✅ Required |

### 6.4 Wave 2 Gate: Decoupling

**Gate Question:** Are Skill dependencies clean enough to proceed?

#### Quantitative Criteria

| Criterion | Threshold for GO | Threshold for CONDITIONAL GO | BLOCKED If |
|:----------|:-----------------|:-----------------------------|:-----------|
| Project path dependencies | 0 | 0 | > 0 |
| Undeclared dependencies (confirmed) | 0 | ≤ 2 | > 2 |
| Circular dependencies | 0 | 0 | > 0 |
| Dependencies on archived Skills | 0 | 0 | > 0 |
| Dependencies on deprecated Skills | 0 | ≤ 3 | > 3 |
| Skills with > 10 dependencies | 0 | ≤ 2 | > 2 |

#### Dependency Graph Validation

| Check | Method |
|:------|:-------|
| Graph is acyclic | Dependency graph traversal |
| All leaf nodes are resolvable | Registry lookup for all `dependencies.skills` entries |
| No cross-category hidden coupling | Scan for `skill:<category>` patterns in body without declaration |
| Replacement chain integrity | For each deprecated Skill, replacement → replacement → ... terminates at active Skill |

### 6.5 Wave 3 Gate: Metadata Completion

**Gate Question:** Are all Skills ready for Phase A (full 14-field enforcement)?

#### Quantitative Criteria

| Criterion | Threshold for GO |
|:----------|:-----------------|
| `owner` present | ≥ 90% of Skills |
| `permissions` declared | ≥ 90% of Skills |
| `compatibility` declared | ≥ 80% of Skills |
| `validation` declared | ≥ 70% of Skills |
| `dependencies` declared (where applicable) | ≥ 85% of Skills with deps |
| All required Phase B fields valid | 100% of Skills |

#### Metadata Completion Thresholds

| Field | Rationale for < 100% Threshold |
|:------|:-------------------------------|
| `owner` | Some legacy Skills have unknown original authors — 90% acceptable |
| `compatibility` | Skills that are `mount: always` may not need platform-specific declarations |
| `validation` | Some Skills are declarative (reference material only) — no executable validation |

### 6.6 Cross-Wave Gate Dependencies

```
Wave 0 (Schema) ───── BLOCKED if any Critical finding
    │
    │ GO / CONDITIONAL GO
    ▼
Wave 1 (Dedup) ───── BLOCKED if exact duplicates unresolved
    │
    │ GO / CONDITIONAL GO
    ▼
Wave 2 (Decouple) ─── BLOCKED if circular deps or project paths exist
    │
    │ GO / CONDITIONAL GO
    ▼
Wave 3 (Metadata) ─── GO only when all Phase A fields ≥ threshold
    │
    ▼
Phase A Migration Execution
```

---

## 7. Human Approval Boundary

### 7.1 Actions Requiring Human Approval

The following actions can be *recommended* by the Auditor Agent but must be *approved* by a human:

| Action | Approver | Rationale |
|:-------|:---------|:----------|
| **Skill rename** | Governance Reviewer | Identity change breaks all references — irreversible without cascading fix |
| **Skill merge** | Governance Reviewer + Architecture Approval | Structural change combining two capability domains |
| **Skill split** | Governance Reviewer + Architecture Approval | Creates new Skills from one — requires new registrations |
| **Skill deprecation** | Governance Reviewer | Lifecycle state change with migration path implications |
| **Skill archival** | Architecture Approval | Permanent removal from active use |
| **Governance relocation** (moving rules from Skill to Protocol) | Architecture Approval (Type D change) | Modifies governance layer — highest sensitivity |
| **Permission change** (adding or removing Skill permissions) | Governance Reviewer | Changes what a Skill can do at runtime |
| **Dependency addition** (adding a new Skill dependency) | Skill Author + Governance Reviewer | Introduces coupling that may propagate |
| **Capability domain change** | Architecture Approval | Changes the Skill's core identity |
| **Registry structural change** (schema version bump, field addition) | Architecture Approval (Type D change) | Modifies the Registry contract |
| **Wave gate decision** (GO / CONDITIONAL GO / BLOCKED) | Governance Reviewer | Auditor recommends; human decides |

### 7.2 Actions NOT Requiring Human Approval

These can proceed automatically based on Auditor Agent recommendation:

| Action | Rationale |
|:-------|:----------|
| `no_action` findings | No change to approve |
| `backfill_metadata` for non-controversial fields (`compatibility`, `validation` with defaults) | Low-risk data population |
| `declare_dependency` that already exists in Skill body (making implicit explicit) | No new coupling introduced |
| `fix_registry_entry` for formatting issues (date format, whitespace) | Mechanical corrections |
| INFO-severity findings with `false_positive_assessment: "ruled_out"` | Confirmed non-issues |

### 7.3 Approval Escalation Path

```
Auditor recommends action
        │
        ▼
┌───────────────────┐
│ Auto-approved?    │─── YES ──▶ Execute
│ (§7.2)            │
└───────┬───────────┘
        │ NO
        ▼
┌───────────────────┐
│ Skill Author      │─── Metadata backfill, dependency declaration
│ approval?         │
└───────┬───────────┘
        │ ESCALATES
        ▼
┌───────────────────┐
│ Governance        │─── Renames, merges, deprecations, permissions
│ Reviewer approval?│
└───────┬───────────┘
        │ ESCALATES
        ▼
┌───────────────────┐
│ Architecture      │─── Splits, archivals, governance relocations,
│ Approval?         │    capability changes, schema changes
└───────┬───────────┘
        │ ESCALATES
        ▼
┌───────────────────┐
│ Full Review Board │─── Multi-Skill structural changes,
│                   │    Wave gate escalations
└───────────────────┘
```

---

## 8. Architecture Boundary Verification

### 8.1 Framework ≠ Runtime

| Check | Auditor Agent | Verdict |
|:------|:--------------|:--------|
| Does it execute Skills? | No — reads only | ✅ PASS |
| Does it run within Hermes sessions? | No — standalone invocation | ✅ PASS |
| Does it produce side effects? | No — output files only via `--output` | ✅ PASS |
| Does it modify filesystem state? | No — read-only except report output | ✅ PASS |

**Verdict: Auditor Agent ≠ Runtime.** The Auditor is a static analysis agent, not a runtime execution environment.

### 8.2 Governance ≠ Skill

| Check | Auditor Agent | Verdict |
|:------|:--------------|:--------|
| Is it a reusable capability extension? | No — governance inspection function | ✅ PASS |
| Does it have a single capability domain? | Yes, but it's regulatory, not operational | ⚠️ EDGE CASE |
| Does it conform to Skill Policy §1 (IS/IS NOT)? | Does not match Skill IS criteria (not a tool orchestration guide, not domain knowledge) | ✅ PASS |
| Does it violate Skill isolation rules? | No — no cross-Skill modification | ✅ PASS |

**Analysis:** The Auditor Agent is borderline — it has a clear purpose (inspection) but is regulatory rather than operational. It is correctly placed in the **Inspection Layer**, not the Skill Layer. If it were a Skill, it would violate Policy §1.3 (Skills IS NOT governance rules). It is explicitly NOT a governance authority (§1.3), so it does not create a governance-over-skill paradox.

**Verdict: Auditor Agent ≠ Skill.** It is an Inspection Layer agent, not a Skill.

### 8.3 Skill ≠ Agent

| Check | Auditor Agent | Verdict |
|:------|:--------------|:--------|
| Does it extend Hermes with domain knowledge? | No — applies governance knowledge, not domain knowledge | ✅ PASS |
| Does it have a SKILL.md with frontmatter? | No — design document, not a Skill | ✅ PASS |
| Is it registered in the Registry? | No — inspection layer, not in Registry | ✅ PASS |
| Does the Skill Manager load it? | No — standalone agent | ✅ PASS |

**Verdict: Auditor Agent ≠ Skill.** It is an agent, not a Skill. Agents are functional processes; Skills are capability extensions.

### 8.4 Migration ≠ Audit

| Check | Auditor Agent | Verdict |
|:------|:--------------|:--------|
| Does it modify the Registry? | No — §5.2 explicitly prohibits | ✅ PASS |
| Does it modify Skill files? | No — §5.2 explicitly prohibits | ✅ PASS |
| Does it execute Wave migration actions? | No — Wave gates are recommendations only (§6) | ✅ PASS |
| Does it change lifecycle states? | No — §5.2 explicitly prohibits | ✅ PASS |

**Verdict: Auditor Agent ≠ Migration Tool.** The Auditor recommends; the Migration Tool executes. Clean separation.

### 8.5 Cross-Boundary Integrity

| Boundary Pair | Conflict? | Resolution |
|:--------------|:----------|:-----------|
| Auditor reads Registry → could it cache stale data? | No | Auditor reads Registry at invocation time; no persistent cache |
| Auditor recommends action → could Governance blindly follow? | Governance risk | §7 defines human approval boundary; Auditor output is advisory |
| Auditor classifies governance leakage → could it miss edge cases? | Yes (inherent) | `human_review_required` action type (§3.4) for ambiguous cases |
| Auditor correlates findings → could correlation create false severity? | Yes (inherent) | §4.3 downgrade rules + §4.4 escalation conditions are conservative |

### 8.6 Boundary Compliance Summary

| Document | Constraint | Auditor Agent Compliance |
|:---------|:-----------|:-------------------------|
| Skill Policy §1.3 | Skills IS NOT governance rules | ✅ Auditor is Inspection Layer, not Skill |
| Skill Policy §2.3 | Prohibited metadata fields | ✅ N/A — Auditor has no skill.yaml |
| Registry Schema §1.3 | Registry IS NOT runtime | ✅ Auditor reads Registry, does not execute |
| Architecture Constraints §0 | Layer N cannot skip Layer N-1 | ✅ Auditor uses CLI output, not raw files |
| Architecture Constraints §0.3.3 | Repository as system of record | ✅ Design documented in repo; no chat-history dependence |

---

## 9. Final Decision

### 9.1 Phase B.2 Readiness Assessment

| Criterion | Status |
|:----------|:-------|
| Auditor Agent positioning defined (§1) | ✅ Inspection Layer — not Skill, not Governance, not Runtime |
| Input contract defined (§2) | ✅ Complete schema from Audit CLI output |
| Output contract defined (§3) | ✅ Governance Finding Report with 16 fields |
| Severity model defined (§4) | ✅ 5 governance severity levels + escalation/downgrade rules |
| Decision boundary defined (§5) | ✅ Permitted actions vs prohibited actions explicitly enumerated |
| Wave gate rules defined (§6) | ✅ Per-Wave quantitative/qualitative criteria + gate output format |
| Human approval boundary defined (§7) | ✅ 11 actions requiring approval + escalation path |
| Architecture boundary verified (§8) | ✅ All 4 boundary checks pass; edge cases analyzed |
| No executable code | ✅ Pure design document |
| No Registry modification | ✅ Read-only design |
| No Skill modification | ✅ Read-only design |

### 9.2 Risk Assessment

| Risk | Severity | Mitigation |
|:-----|:---------|:-----------|
| Auditor over-classification (false severity escalation) | Medium | §4.3 downgrade rules; human review for all Critical findings |
| Auditor under-classification (missed governance leakage) | High | §4.4 multi-finding escalation; §7.3 escalation path for ambiguous cases |
| Governance blind trust (human defers entirely to Auditor) | Medium | §5.2 prohibits automatic actions; §7 requires human approval for all structural changes |
| Auditor scope creep (gradually absorbing Migration Tool functions) | Low | §1.4 explicitly documents why no migration authority; §5.2 lists prohibited actions |
| Wave gate false GO (Auditor recommends GO when BLOCKED is correct) | High | §6 qualitative criteria always require human sign-off; gate decision requires Governance Reviewer approval |

### 9.3 GO / NO-GO Decision

**Decision: GO — Phase B.2 is complete.**

**Rationale:**

1. **Design Completeness:** All 9 sections defined with no TODOs or placeholders.
2. **Boundary Integrity:** Auditor Agent correctly positioned in Inspection Layer — no violation of Framework, Governance, Skill, or Migration boundaries.
3. **Contract Clarity:** Input contract (from Audit CLI) and output contract (to Governance Layer) are fully specified with concrete schemas.
4. **Safety:** Decision boundary (§5) explicitly prohibits all mutation actions; human approval boundary (§7) gates all structural changes.
5. **Wave Readiness:** Wave gate rules (§6) provide quantitative + qualitative criteria sufficient for Migration Specification.

**Conditions for Phase B.2 → Migration Specification:**

- Auditor Agent design is reviewed by governance stakeholder — ✅ design is documented for review
- No critical design gaps identified — ✅ all 9 sections complete
- Architecture boundary verification passes — ✅ §8 confirms all checks

### 9.4 Next Phase Recommendation

**Phase A — Migration Specification** can now begin. The Migration Specification will define:

- How to execute the actions recommended by the Auditor Agent
- The Migration Tool's command interface
- Per-Wave execution plans
- Rollback procedures
- Verification checkpoints

The Auditor Agent provides the **decision intelligence**; the Migration Specification will provide the **execution mechanism**.

---

> **Design Status:** Complete v1.0
> **Phase:** B.2 — Auditor Agent Design Specification Complete
> **Governance Stack:** Protocol → Skill Policy → Registry Schema → Audit CLI → Auditor Agent (this doc)
> **Layer:** Inspection Layer (between Data and Governance)
> **Next:** Phase A — Migration Specification
> **Implementation Gate:** Do not implement Auditor Agent until Migration Specification is approved and Wave 0 audit passes.
> **Amendment Process:** Type D change (requires explicit architecture approval)
