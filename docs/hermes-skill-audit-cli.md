# Hermes Skill Audit CLI Design Specification

**Status:** Draft — Design Document
**Type:** Governance Design Documentation — CLI Contract
**Version:** 1.0.0
**Applies to:** Hermes Skill Policy §6 (Quality Checklist) + Hermes Skill Registry Schema v1.0
**Created:** 2026-07-18
**Phase:** B.1 — Audit CLI Design Specification

**Dependencies:**
- Hermes Skill Governance Policy v1.0 (§6 Quality Checklist, §8 Anti-Patterns)
- Hermes Skill Registry Schema v1.0 (14-field contract)
- Architecture Constraints (boundary violation catalog)
- Error Registry (known error taxonomy)

---

## 1. Purpose

### 1.1 Audit CLI Responsibility

`hermes skill audit` is a **read-only inspection tool** that validates Skills against the Governance Policy and Registry Schema. It reads Skill metadata and implementation files, applies audit rules, and produces a structured compliance report. It never modifies anything.

### 1.2 Audit CLI IS

| ✅ IS | Description |
|:------|:------------|
| **Metadata inspector** | Reads and validates Skill metadata against the Registry Schema (14 fields) |
| **Boundary checker** | Detects governance leakage, runtime replacement, and framework authority violations |
| **Registry validator** | Verifies Schema compliance (required fields, valid lifecycle states, correct types) |
| **Compliance reporter** | Produces structured audit reports with findings, severity, evidence, and recommendations |
| **Anti-pattern detector** | Flags Policy §8 violations (Mega Skill, Hidden Governance, Permission Overreach, etc.) |
| **Quality gate assistant** | Verifies Policy §6 checklist items before registration |

### 1.3 Audit CLI IS NOT

| ❌ IS NOT | Rationale |
|:----------|:----------|
| **Skill executor** | Does not load or run Skills; only reads metadata and content |
| **Runtime** | Does not execute within Hermes sessions; is a standalone CLI tool |
| **Permission engine** | Does not enforce permissions; only validates declarations against Policy |
| **Migration executor** | Does not modify `skill-registry.json` or Skill files |
| **Registry writer** | Read-only — never writes to the Registry |
| **Auto-fixer** | Never automatically modifies Skills or Registry entries |
| **Governance gate** | Reports findings; does not approve or reject registrations |

### 1.4 Position in Governance Stack

```
Governance Protocol
        │
        ▼
Skill Policy (§6 Quality + §8 Anti-Patterns)
        │
        ▼
Registry Schema (14-field contract)
        │
        ▼
Audit CLI (this document — inspection tool)     ← READ-ONLY
        │
        ▼
Registry Implementation (skill-registry.json)
        │
        ▼
Individual Skills (SKILL.md)
```

---

## 2. Command Interface

### 2.1 Core Command

```
hermes skill audit [options]
```

### 2.2 Subcommands

| Subcommand | Purpose |
|:-----------|:--------|
| `hermes skill audit metadata <path>` | Validate a Skill's metadata against Registry Schema |
| `hermes skill audit boundary <path>` | Detect governance/runtime/framework boundary violations |
| `hermes skill audit deps <path>` | Check for hidden dependencies, project coupling, path coupling |
| `hermes skill audit dupes` | Detect duplicate capabilities across registered Skills |
| `hermes skill audit registry` | Validate entire `skill-registry.json` against Schema |
| `hermes skill audit all [--skills-root <dir>]` | Run all modules against all Skills |
| `hermes skill audit wave [0|1|2|3]` | Run Wave-specific audit (see §6) |

### 2.3 Options

| Flag | Description |
|:-----|:------------|
| `--skills-root <path>` | Root directory containing Skills (default: `skills/`) |
| `--registry <path>` | Path to `skill-registry.json` (default: `skill-manager/skill-registry.json`) |
| `--schema <path>` | Path to Registry Schema spec (default: `docs/hermes-skill-registry-schema.md`) |
| `--format <format>` | Output format: `text` (default), `json`, `markdown` |
| `--severity <level>` | Minimum severity to report: `info`, `warning`, `error`, `critical` (default: `warning`) |
| `--rule <rule-id>` | Run a single rule by ID (e.g., `--rule SKILL-B001`) |
| `--output <path>` | Write report to file instead of stdout |
| `--strict` | Treat warnings as errors (exit code 1 on any finding) |
| `--dry-run` | Validate inputs only; do not scan Skill content |

### 2.4 Input Model

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Registry Schema │     │ skill-registry.  │     │  Skill Directories│
│  (14-field spec) │     │ json (data)      │     │  (SKILL.md files)  │
└────────┬─────────┘     └────────┬─────────┘     └────────┬─────────┘
         │                        │                        │
         └────────────────────────┼────────────────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    hermes skill audit   │
                    │    (read-only scan)     │
                    └────────────┬────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │     Audit Report        │
                    │  (text / json / md)     │
                    └─────────────────────────┘
```

### 2.5 Exit Codes

| Code | Meaning |
|:-----|:--------|
| 0 | No findings above the configured severity threshold |
| 1 | At least one finding at or above the configured severity threshold (or `--strict` mode with warnings) |
| 2 | Input validation error (missing file, invalid schema, unreadable Skill directory) |
| 3 | Tool error (internal failure, not a finding in the audited Skills) |

---

## 3. Audit Modules

### 3.1 Module: Metadata Audit

**Command:** `hermes skill audit metadata <path>`

Checks a single Skill's metadata against the Registry Schema's 14-field contract.

#### 3.1.1 Checks

| # | Check | Rule ID | Applies To |
|:--|:------|:--------|:-----------|
| M01 | `name` is present and matches `^[a-z0-9]+(-[a-z0-9]+)*$` | SKILL-M001 | All Skills |
| M02 | `version` follows semver (`^\d+\.\d+\.\d+$`) | SKILL-M002 | All Skills |
| M03 | `description` is non-empty, ≤ 1024 chars | SKILL-M003 | All Skills |
| M04 | `capability` is a single domain (not comma-separated) | SKILL-M004 | All Skills |
| M05 | `owner` is present or explicitly null (Phase B optional) | SKILL-M005 | Phase A |
| M06 | `lifecycle` is a valid state from the 7-state model | SKILL-M006 | All Skills |
| M07 | `status` is valid for the current lifecycle state | SKILL-M007 | All Skills |
| M08 | `registered` is a valid ISO 8601 date | SKILL-M008 | All Skills |
| M09 | `updated` is ≥ `registered` | SKILL-M009 | All Skills |
| M10 | `path` exists and contains a SKILL.md | SKILL-M010 | All Skills |
| M11 | `dependencies` does not contain project paths or unregistered Skills | SKILL-M011 | Phase A |
| M12 | `permissions` does not include Tier 3 entries | SKILL-M012 | Phase A |
| M13 | `validation.command` is a valid shell command string | SKILL-M013 | Phase A |
| M14 | `compatibility.platforms` uses controlled vocabulary | SKILL-M014 | Phase A |

#### 3.1.2 Phase B Behavior

In Phase B, optional fields (M05, M11, M12, M13, M14) are checked with severity `info` (not `warning` or `error`). Missing optional fields are not violations — they are observations.

### 3.2 Module: Boundary Audit

**Command:** `hermes skill audit boundary <path>`

Detects governance leakage, runtime replacement, and framework authority violations per Policy §8 Anti-Patterns.

#### 3.2.1 Checks

| # | Check | Rule ID | Severity | Detection Method |
|:--|:------|:--------|:---------|:-----------------|
| B01 | Skill contains governance rules | SKILL-B001 | **CRITICAL** | Keyword scan: `governance_rules`, `workflow_override`, `phase`, `approval_gate`, `system_prompt.inject`, `auto_approve` |
| B02 | Skill implements workflow control | SKILL-B002 | **CRITICAL** | Content scan: Phase 0/1/2 references in non-governance context, DAG execution descriptions |
| B03 | Skill modifies agent behavior via side effects | SKILL-B003 | **HIGH** | Content scan: `system_prompt`, `config.yaml` write paths, `~/.hermes/config.yaml` references |
| B04 | Skill implements alternative runtime | SKILL-B004 | **CRITICAL** | Content scan: custom execution loops, agent spawning logic outside of delegate_task |
| B05 | Skill requests Tier 3 permissions | SKILL-B005 | **CRITICAL** | Metadata check: `permissions.allow` contains `agent.spawn`, `policy.modify`, `workflow.override` |
| B06 | Skill is a Mega Skill (too many capabilities) | SKILL-B006 | **HIGH** | Metadata check: capability description contains `,` (multiple domains), metadata > 50 lines |
| B07 | Skill path references governance/architecture files | SKILL-B007 | **WARNING** | File access scan: reads from `docs/hermes-skill-policy.md`, `docs/universal-agent-framework-rfc.md` beyond reference |

#### 3.2.2 Detection Heuristics

From Policy §8.2:

| Heuristic | Rule ID | Trigger |
|:----------|:--------|:--------|
| Metadata exceeds 50 lines | SKILL-B006 | Likely Mega Skill or scope creep |
| `permissions.allow` contains `*` or Tier 3 | SKILL-B005 | Permission overreach or hidden governance |
| Dependencies list > 10 other Skills | SKILL-D008 | Excessive coupling; likely monolithic |
| Version MAJOR > 5 within 6 months | SKILL-B008 | Scope unstable; needs redesign |
| Skill reads `~/.hermes/config.yaml` | SKILL-B003 | Hidden governance attempt |
| Skill uses `system_prompt.inject` | SKILL-B001 | Immediate rejection |

### 3.3 Module: Dependency Audit

**Command:** `hermes skill audit deps <path>`

Detects hidden dependencies, project coupling, and path coupling per Registry Schema §6.

#### 3.3.1 Checks

| # | Check | Rule ID | Severity | Detection Method |
|:--|:------|:--------|:---------|:-----------------|
| D01 | Undeclared dependency (uses another Skill's output without declaring it) | SKILL-D001 | **HIGH** | Cross-reference: `skill:<name>` memory references vs `dependencies.skills` |
| D02 | Project path dependency (absolute or home-relative path in dependency) | SKILL-D002 | **HIGH** | Path scan: `~` + `/` patterns in dependencies, `~/Terence-Agent`, `/home/` references |
| D03 | Hidden path coupling (hardcoded paths in Skill body) | SKILL-D003 | **WARNING** | Content scan: absolute paths, `~/A3-Multi-Agent-System`, `~/projects/` patterns |
| D04 | Dependency on unregistered Skill | SKILL-D004 | **ERROR** | Registry lookup: each `dependencies.skills` entry exists in Registry |
| D05 | Circular dependency | SKILL-D005 | **ERROR** | Graph traversal: A depends on B depends on A |
| D06 | Dependency on deprecated Skill | SKILL-D006 | **WARNING** | Registry lookup: dependency's lifecycle = `deprecated` |
| D07 | Dependency on archived Skill | SKILL-D007 | **ERROR** | Registry lookup: dependency's lifecycle = `archived` |
| D08 | Excessive coupling (> 10 Skill dependencies) | SKILL-D008 | **WARNING** | Count: `dependencies.skills` length > 10 |

#### 3.3.2 Path Coupling Patterns

The following patterns in Skill content signal project coupling:

| Pattern | Detection Regex |
|:--------|:----------------|
| Home-relative path | `~/\w+` |
| Absolute project path | `/home/\w+/[A-Z]` |
| A3 project reference | `A3-Multi-Agent-System` |
| Terence-Agent hardcode | `~/Terence-Agent/` |
| Config file assumption | `~/.hermes/config.yaml` (in write context) |

### 3.4 Module: Duplication Audit

**Command:** `hermes skill audit dupes`

Detects duplicate capabilities across registered Skills per Policy §6.1 Check #1.

#### 3.4.1 Checks

| # | Check | Rule ID | Severity | Detection Method |
|:--|:------|:--------|:---------|:-----------------|
| P01 | Two Skills share the same `capability` value | SKILL-P001 | **WARNING** | Registry scan: duplicate `capability` field |
| P02 | Two Skills have overlapping capability descriptions | SKILL-P002 | **INFO** | Similarity check: description Levenshtein distance < threshold |
| P03 | Two Skills share the same `purpose` keyword | SKILL-P003 | **INFO** | Purpose field comparison |
| P04 | Umbrella Skill duplicates child capability | SKILL-P004 | **WARNING** | Parent-child comparison: umbrella's capability vs children's capabilities |
| P05 | Skill reimplements existing Skill (not extension) | SKILL-P005 | **ERROR** | Multiple-match: capability overlap without dependency declaration |

#### 3.4.2 Duplication Resolution Rules

| Relationship | Verdict | Recommendation |
|:-------------|:--------|:---------------|
| Exact capability match | DUPLICATE | Merge or deprecate one |
| Subset capability (A is subset of B) | COMPOSITION | Declare dependency: A depends on B |
| Overlapping capability (A ∩ B non-empty) | AMBIGUOUS | Clarify boundaries or merge |
| Extension (A adds to B) | VALID | Declare dependency: A extends B |

### 3.5 Module: Registry Audit

**Command:** `hermes skill audit registry`

Validates the entire `skill-registry.json` against the Registry Schema. This is the **Schema compliance** check, not a per-Skill check.

#### 3.5.1 Checks

| # | Check | Rule ID | Severity | Detection Method |
|:--|:------|:--------|:---------|:-----------------|
| R01 | Registry `version` field is present and valid semver | SKILL-R001 | **ERROR** | Schema validation |
| R02 | Registry `updated` field is valid ISO 8601 date | SKILL-R002 | **ERROR** | Schema validation |
| R03 | Every Skill entry has the 9 required Phase B fields | SKILL-R003 | **ERROR** | Field presence check |
| R04 | No duplicate Skill `name` values | SKILL-R004 | **ERROR** | Uniqueness check |
| R05 | All `parent` references point to existing Skills | SKILL-R005 | **ERROR** | Reference integrity |
| R06 | All `fallback` references point to existing Skills | SKILL-R006 | **WARNING** | Reference integrity |
| R07 | `forbidden_pairs` entries reference existing Skills | SKILL-R007 | **WARNING** | Reference integrity |
| R08 | Schema version matches Registry Schema document version | SKILL-R008 | **INFO** | Version comparison |
| R09 | No orphan Skills (in Registry but directory missing) | SKILL-R009 | **ERROR** | Filesystem check |
| R10 | No ghost Skills (directory exists but not in Registry) | SKILL-R010 | **WARNING** | Filesystem check |

---

## 4. Rule Engine Design

### 4.1 Rule Structure

Every audit rule has the following structure:

```yaml
rule:
  id: "SKILL-B001"
  module: "boundary"
  name: "No Governance Rule Leakage"
  description: >
    A Skill must not contain governance rules, workflow overrides,
    or system prompt injection. Governance is the exclusive domain
    of the Governance Protocol.
  severity: "critical"
  policy_ref: "Skill Policy §2.3 — Prohibited Metadata"
  detection:
    type: "keyword_scan"
    targets:
      - "SKILL.md frontmatter"
      - "SKILL.md body"
    patterns:
      - "governance_rules"
      - "workflow_override"
      - "system_prompt.inject"
      - "auto_approve"
      - "system_prompt"
    exclude_patterns:
      - "this Skill does not contain governance_rules"
  recommendation: >
    Remove all governance-related declarations from Skill metadata
    and body. Governance rules belong in the Governance Protocol,
    not in operational Skills.
  false_positive_risk: "low"
```

### 4.2 Rule Catalog Summary

| ID Prefix | Module | Count | Scope |
|:----------|:-------|:------|:------|
| SKILL-Mxxx | Metadata | 14 rules | Per-Skill metadata validation |
| SKILL-Bxxx | Boundary | 8 rules | Governance/Runtime/Framework boundary |
| SKILL-Dxxx | Dependency | 8 rules | Hidden deps, coupling, circular deps |
| SKILL-Pxxx | Duplication | 5 rules | Capability overlap detection |
| SKILL-Rxxx | Registry | 10 rules | Schema compliance, integrity checks |
| **Total** | | **45 rules** | |

### 4.3 Severity Classification

| Severity | Meaning | Exit Code Impact | Example |
|:---------|:--------|:-----------------|:--------|
| **CRITICAL** | Policy violation that must block registration | Always → exit code 1 | SKILL-B001 (Hidden Governance) |
| **ERROR** | Schema violation or data integrity failure | → exit code 1 (unless `--severity critical`) | SKILL-M001 (name missing) |
| **WARNING** | Best practice deviation; should be fixed | → exit code 1 only with `--strict` | SKILL-D006 (dep on deprecated Skill) |
| **INFO** | Observation; no action required | Never → exit code 1 | SKILL-P002 (possible overlap) |

### 4.4 Detection Engine Types

| Type | Description | Used By |
|:-----|:------------|:--------|
| `field_presence` | Check if a metadata field exists | M01-M14 |
| `pattern_match` | Regex or keyword scan in content | B01, B03, D02, D03 |
| `schema_validation` | Validate value against type/format constraints | M02, M06, M08, M09 |
| `reference_integrity` | Check that references point to existing entities | D04-D07, R05-R07 |
| `graph_traversal` | Walk dependency graph for cycles | D05 |
| `similarity_check` | Compute similarity between two values | P02, P03 |
| `filesystem_check` | Verify filesystem paths exist | M10, R09, R10 |
| `count_threshold` | Check list lengths exceed threshold | D08, B06 |

### 4.5 Rule Definition Format

Each rule is a self-contained definition that can be executed independently:

```yaml
# Rule file: rules/SKILL-B001.yaml
id: SKILL-B001
name: "No Governance Rule Leakage"
module: boundary
severity: critical
policy_ref: "Policy §2.3"
detection:
  type: pattern_match
  scope:
    - metadata
    - body
  patterns:
    - "governance_rules"
    - "workflow_override"
    - "system_prompt\\.inject"
    - "auto_approve"
  exclude_patterns:
    - "this Skill does not contain"
    - "IS NOT.*Governance"
finding_template: >
  Skill '{skill.name}' contains governance declaration '{match}'
  at {location}. Skills must not modify governance behavior.
  See: Hermes Skill Policy §2.3.
recommendation: >
  Remove governance declaration from Skill. Governance rules
  belong exclusively in the Governance Protocol.
false_positive_risk: low
```

---

## 5. Report Format

### 5.1 Text Output (default)

```
══════════════════════════════════════════════════════
  HERMES SKILL AUDIT REPORT
══════════════════════════════════════════════════════

Audit:      2026-07-18T15:30:00Z
Scope:      14 Skills in skills/
Registry:   skill-manager/skill-registry.json
Schema:     Registry Schema v1.0.0
Modules:    metadata, boundary, deps, dupes, registry

──────────────────────────────────────────────────────
  SUMMARY
──────────────────────────────────────────────────────

  Passed:   38 / 45 rules
  Failed:    7 rules

  Severity breakdown:
    CRITICAL:  0
    ERROR:     2
    WARNING:   3
    INFO:      2

──────────────────────────────────────────────────────
  FINDINGS
──────────────────────────────────────────────────────

[ERROR] SKILL-M001 — Missing required field 'name'
  Skill: skills/no-name-skill/
  Field 'name' is required by Registry Schema §2.1.1.
  Recommendation: Add `name` field to SKILL.md frontmatter.

[ERROR] SKILL-D004 — Dependency on unregistered Skill
  Skill: skills/custom-workflow/
  Depends on 'my-private-helper' which is not in Registry.
  Recommendation: Register 'my-private-helper' or remove dependency.

[WARNING] SKILL-D006 — Dependency on deprecated Skill
  Skill: skills/old-browser/
  Depends on 'legacy-playwright' (lifecycle: deprecated).
  Recommendation: Migrate to replacement Skill 'layer1-playwright'.

[WARNING] SKILL-P001 — Duplicate capability detected
  Skills: 'browser-automation' and 'web-automation'
  Both declare capability 'browser-automation'.
  Recommendation: Merge or differentiate capability domains.

[INFO] SKILL-P002 — Possible capability overlap
  Skills: 'pdf-editor' and 'document-formatter'
  Description similarity: 72%
  Recommendation: Review if capabilities are distinct.

──────────────────────────────────────────────────────
  AUDIT PASSED: NO
  Exit code: 1
══════════════════════════════════════════════════════
```

### 5.2 JSON Output (`--format json`)

```json
{
  "audit": {
    "timestamp": "2026-07-18T15:30:00Z",
    "schema_version": "1.0.0",
    "scope": {
      "skills_count": 14,
      "registry_path": "skill-manager/skill-registry.json",
      "skills_root": "skills/"
    },
    "modules": ["metadata", "boundary", "deps", "dupes", "registry"]
  },
  "summary": {
    "total_rules": 45,
    "passed": 38,
    "failed": 7,
    "by_severity": {
      "critical": 0,
      "error": 2,
      "warning": 3,
      "info": 2
    }
  },
  "findings": [
    {
      "rule_id": "SKILL-M001",
      "severity": "error",
      "skill": "no-name-skill",
      "field": "name",
      "message": "Missing required field 'name'",
      "evidence": "SKILL.md frontmatter: no 'name' field found",
      "recommendation": "Add `name` field to SKILL.md frontmatter."
    }
  ],
  "exit_code": 1
}
```

### 5.3 Markdown Output (`--format markdown`)

Same structure as §5.2, rendered as a Markdown document with tables and headings. Suitable for commit to `docs/audits/` as a permanent record.

### 5.4 Finding Structure

Every finding includes:

| Field | Description |
|:------|:------------|
| `rule_id` | The rule that triggered the finding (e.g., `SKILL-B001`) |
| `severity` | `critical`, `error`, `warning`, or `info` |
| `skill` | The Skill name (or `registry` for Registry-level findings) |
| `location` | File path and line/field where the violation was detected |
| `evidence` | The actual content that triggered the rule (quoted) |
| `message` | Human-readable description of the violation |
| `recommendation` | Actionable guidance for remediation |

---

## 6. Wave Migration Support

### 6.1 Design Principle

The Audit CLI is a **detection tool**, not a migration tool. It identifies what needs to change, but never makes changes. This supports the Wave-based migration strategy by providing:

1. **Pre-migration audit** — What will break if we migrate?
2. **Post-migration verification** — Did the migration succeed?
3. **Incremental gate** — Can Wave N proceed given Wave N-1 results?

### 6.2 Wave 0: Schema Compliance Detection

**Command:** `hermes skill audit wave 0`

| Check | What it detects |
|:------|:----------------|
| Which Skills lack required Phase B fields? | M01-M10 rules |
| Which Registry entries would fail Schema validation? | R01-R10 rules |
| Which optional fields are present vs absent? | M05, M11-M14 (info only) |

**Output:** A gap report showing exactly which Skills need metadata backfill before migration.

### 6.3 Wave 1: Duplicate Detection

**Command:** `hermes skill audit wave 1`

| Check | What it detects |
|:------|:----------------|
| Which Skills have duplicate capabilities? | P01-P05 rules |
| Which Skills can be merged? | P01 + capability comparison |
| Which Skills need boundary clarification? | P02, P03 (overlap) |

**Output:** A deduplication plan showing candidate merges and boundary clarifications.

### 6.4 Wave 2: Coupling Detection

**Command:** `hermes skill audit wave 2`

| Check | What it detects |
|:------|:----------------|
| Which Skills have project path dependencies? | D02-D03 rules |
| Which Skills have undeclared dependencies? | D01 |
| Which dependency graphs are overly complex? | D05, D08 |
| Which Skill-to-Skill couplings need decoupling? | Cross-reference D02 + D03 |

**Output:** A decoupling plan showing which Skills need path references removed.

### 6.5 Wave 3: Metadata Gap Detection

**Command:** `hermes skill audit wave 3`

| Check | What it detects |
|:------|:----------------|
| Which Skills have missing optional fields? | M05, M11-M14 (Phase A required) |
| Which Skills have invalid optional field values? | M11-M14 (format validation) |
| What's the backfill estimate? | Count of null/absent fields per Skill |

**Output:** A backfill plan showing how many Skills need each optional field populated.

### 6.6 Wave Gate Integration

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│  Wave 0  │───▶│  Wave 1  │───▶│  Wave 2  │───▶│  Wave 3  │
│  Schema  │    │ Duplicate│    │ Coupling │    │ Metadata │
│Compliance│    │Detection │    │Detection │    │   Gap    │
└────┬─────┘    └────┬─────┘    └────┬─────┘    └────┬─────┘
     │               │               │               │
     ▼               ▼               ▼               ▼
  Audit:         Audit:          Audit:          Audit:
  "Can we        "Which Skills   "Which deps     "What's left
   migrate?"      overlap?"       are coupled?"   to fill?"
```

Each Wave audit produces a gate decision:
- **GO:** 0 critical/error findings → proceed to next Wave
- **CONDITIONAL GO:** ≤ N warnings, 0 critical/errors → proceed with remediation plan
- **BLOCKED:** Critical or errors present → fix before proceeding

---

## 7. Architecture Boundary

### 7.1 Audit CLI vs Registry

| Boundary | Audit CLI | Registry |
|:---------|:----------|:---------|
| **Read** | YES — reads Registry for validation | Stores data |
| **Write** | NO — never writes to Registry | Stores data |
| **Authority** | None — advisory only | Source of truth for metadata |
| **Lifecycle** | Ephemeral (per invocation) | Persistent (file) |

**Audit CLI ≠ Registry.** The CLI reads the Registry; it does not modify it.

### 7.2 Audit CLI vs Governance Engine

| Boundary | Audit CLI | Governance Engine |
|:---------|:----------|:------------------|
| **Function** | Inspects and reports | Enforces rules |
| **Permission** | Read-only | Read + write (approve/reject) |
| **Decision authority** | None — advisory | Yes — gates transitions |
| **Output** | Report (file/stdout) | State change (lifecycle transition) |

**Audit CLI ≠ Governance Engine.** The CLI reports findings; Governance acts on them.

### 7.3 Audit CLI vs Runtime

| Boundary | Audit CLI | Runtime |
|:---------|:----------|:--------|
| **When active** | On-demand (CLI invocation) | During Hermes sessions |
| **What it loads** | Metadata + SKILL.md text | Skill implementation + tools |
| **Side effects** | None (read-only) | Files, network, tool calls |
| **Process model** | Single invocation → exit | Long-running session |

**Audit CLI ≠ Runtime.** The CLI is a static analysis tool, not an execution environment.

### 7.4 Audit CLI vs Migration Tool

| Boundary | Audit CLI | Migration Tool |
|:---------|:----------|:---------------|
| **Function** | Detects issues | Fixes issues |
| **Modifies** | Nothing | Registry + Skills |
| **Output** | Report | Modified files |
| **Reversible** | N/A (no changes) | Requires backup |

**Audit CLI ≠ Migration Tool.** The CLI identifies what needs to change; the Migration Tool (Phase A, future) makes the changes.

### 7.5 Boundary Summary

```
┌─────────────────────────────────────────────────────────────┐
│                     Hermes System                            │
│                                                             │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌──────────┐ │
│  │Governance │  │ Registry  │  │  Runtime  │  │Audit CLI │ │
│  │  Engine   │  │           │  │           │  │(this doc)│ │
│  │           │  │           │  │           │  │           │ │
│  │ Enforces  │  │ Catalogs  │  │ Executes  │  │ Inspects  │ │
│  │ rules     │  │ metadata  │  │ Skills    │  │ & reports │ │
│  └───────────┘  └───────────┘  └───────────┘  └─────┬─────┘ │
│                                                     │       │
│                                            READ-ONLY│       │
│                                                     ▼       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Skill Implementations                   │   │
│  │         SKILL.md + supporting files                  │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

The Audit CLI is an **inspection layer** that reads everything, modifies nothing.

---

## 8. Security Considerations

### 8.1 Design Constraints

| Constraint | Rationale |
|:-----------|:----------|
| **No automatic modification** | The CLI must NEVER modify Skills, Registry, or any governance document. It is a pure reader. |
| **No automatic approval** | The CLI reports findings; it does not decide whether a Skill passes governance review. |
| **No hidden repair** | Audit findings must be explicit and visible. The CLI must not silently fix or suppress violations. |
| **Human approval required** | Any remediation action based on audit findings must be initiated by a human operator. |
| **No side-channel writes** | The CLI must not write log files, cache files, or state files in Skill directories. Only the explicitly requested `--output` path receives a write. |
| **No network access** | The CLI operates entirely on the local filesystem. No API calls, no telemetry, no update checks. |

### 8.2 Permissions Model

The Audit CLI requires:

| Permission | Scope | Rationale |
|:-----------|:------|:----------|
| `filesystem.read` | `skills/**`, `skill-manager/skill-registry.json`, `docs/hermes-skill-registry-schema.md` | Read Skill content, Registry, and Schema for validation |
| `filesystem.write` | `--output <path>` only | Write audit report to specified path |
| `filesystem.write` | `stdout` | Default report output |

It must NOT require:
- `network.*` — No network access
- `git.*` — No repository operations
- `skill.manage` — No Skill modification
- `memory.*` — No persistent state
- `tool.exec` — No shell command execution (except reading files)

### 8.3 Input Validation

| Input | Validation |
|:------|:-----------|
| `--skills-root` | Must be a readable directory |
| `--registry` | Must be a readable JSON file |
| `--schema` | Must be a readable markdown file |
| `--output` | Parent directory must be writable; file must not be a Skill directory |
| `--format` | Must be `text`, `json`, or `markdown` |
| `--severity` | Must be `info`, `warning`, `error`, or `critical` |
| `--rule` | Must match `^SKILL-[A-Z]\d{3}$` |

### 8.4 Sensitive Content Handling

| Scenario | Behavior |
|:---------|:---------|
| Skill contains secrets (API keys, tokens) | Report as SKILL-S001 (secrets in Skill) — severity: **CRITICAL** |
| Skill path points outside skills root | Reject: `--skills-root` boundary violation |
| Output path overlaps Skill directory | Reject: would pollute Skill with audit artifacts |

---

## 9. Verification

### 9.1 Document Completeness

| # | Section | Status |
|:--|:--------|:-------|
| 1 | Purpose (§1) — CLI responsibilities, IS/IS NOT, governance position | ✅ |
| 2 | Command Interface (§2) — subcommands, options, inputs, outputs, exit codes | ✅ |
| 3 | Audit Modules (§3) — 5 modules: Metadata, Boundary, Deps, Duplication, Registry | ✅ |
| 4 | Rule Engine (§4) — rule structure, 45 rules, severity, detection types | ✅ |
| 5 | Report Format (§5) — text, JSON, markdown outputs with finding structure | ✅ |
| 6 | Wave Migration Support (§6) — Wave 0-3 pre-audit support | ✅ |
| 7 | Architecture Boundary (§7) — CLI vs Registry, Governance, Runtime, Migration | ✅ |
| 8 | Security Considerations (§8) — constraints, permissions, input validation | ✅ |
| 9 | Verification (§9) — this checklist | ✅ |

### 9.2 Phase B Compliance

| # | Check | Status |
|:--|:------|:-------|
| 1 | Document only — no executable code? | ✅ YES — YAML examples are illustrative, not executable |
| 2 | No Registry modification? | ✅ YES — read-only design |
| 3 | No Skill modification? | ✅ YES — read-only design |
| 4 | No Migration execution? | ✅ YES — detection only, Wave support is audit-only |
| 5 | No Runtime implementation? | ✅ YES — static analysis design |
| 6 | No Governance rule modification? | ✅ YES — references Policy, does not extend it |
| 7 | No project dependencies? | ✅ YES — no hardcoded paths beyond example patterns |
| 8 | Architecture boundary explicit? | ✅ YES — §7 covers all four boundaries |

### 9.3 Cross-Reference Verification

| Document | Referenced In | Alignment |
|:---------|:--------------|:----------|
| Skill Policy §6 (Quality Checklist) | Modules: Metadata, Boundary | All 9 checklist items mapped to rules |
| Skill Policy §8 (Anti-Patterns) | Module: Boundary | All 8 anti-patterns mapped to rules |
| Registry Schema §2 (14 fields) | Module: Metadata | All 14 fields mapped to rules |
| Registry Schema §4 (Lifecycle) | Rule: SKILL-M006, M007 | Lifecycle states validated |
| Registry Schema §5 (Permissions) | Rules: SKILL-B005, M012 | Permission tiers validated |
| Registry Schema §6 (Dependencies) | Module: Deps | All dependency rules mapped |
| Architecture Constraints | Module: Boundary | Violation catalog aligned |

---

> **Design Status:** Draft v1.0 — Complete
> **Phase:** B.1 — CLI Design Specification Complete
> **Governance Stack:** Protocol → Skill Policy → Registry Schema → Audit CLI (this doc)
> **Next:** Phase B.2 — Auditor Agent Design, OR Phase A — Migration Tool Implementation
> **Implementation Gate:** Do not implement until Phase A is approved.
> **Amendment Process:** Type D change (requires explicit architecture approval)
