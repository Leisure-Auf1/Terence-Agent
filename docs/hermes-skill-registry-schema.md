# Hermes Skill Registry Schema v1.0

**Status:** Active
**Type:** Governance Documentation — Schema Contract
**Version:** 1.0.0
**Applies to:** Hermes Skill Policy §9 — Skill Registry Design
**Created:** 2026-07-18
**Phase:** B.0 — Registry Schema Specification

---

## 1. Purpose

### 1.1 Registry Responsibility

The Skill Registry is the **canonical metadata catalog** for all Skills registered under Hermes Agent. It serves as the single source of truth for Skill identity, capability discovery, lifecycle tracking, and validation reference — distinct from Skill implementations which live in their own directories.

### 1.2 Registry IS

| ✅ IS | Description |
|:------|:------------|
| **Skill metadata catalog** | Stores structured metadata for every registered Skill |
| **Lifecycle tracking** | Records each Skill's current lifecycle state and transition history |
| **Capability discovery** | Enables querying Skills by capability domain, owner, or status |
| **Validation reference** | Provides canonical field values against which Skill implementations are validated |
| **Dependency graph** | Maintains declared dependencies between Skills for resolution |
| **Migration source of truth** | Serves as the authoritative record for migration mapping |

### 1.3 Registry IS NOT

| ❌ IS NOT | Rationale |
|:----------|:----------|
| **Runtime** | The Registry does not execute Skills, load them into sessions, or manage active processes |
| **Skill executor** | The Registry does not run validation checks, activate/deactivate Skills at runtime, or enforce permissions |
| **Permission authority** | The Registry records declared permissions; the Governance Layer owns permission enforcement |
| **Workflow controller** | The Registry does not drive Phase 0/1/2 workflow execution or agent orchestration |
| **Agent manager** | The Registry does not spawn, monitor, or control agents |
| **Skill implementation** | The Registry stores metadata, not code, instructions, or procedural logic |

### 1.4 Position in Governance Stack

```
Governance Protocol (rules, constraints)
        │
        ▼
Skill Policy (this doc's parent — §9)
        │
        ▼
Registry Schema (this document — contract)
        │
        ▼
Registry Implementation (skill-registry.json — data)
        │
        ▼
Individual Skills (SKILL.md — implementation)
```

---

## 2. Schema Definition

### 2.1 Complete Field Reference

The Registry Schema defines **14 fields** per Skill entry. Together they form the complete metadata contract for every registered Skill.

#### 2.1.1 `name`

| Property | Value |
|:---------|:------|
| **Name** | `name` |
| **Type** | `string` |
| **Required** | ✅ YES |
| **Format** | Lowercase, hyphens, ≤ 64 chars. Must match the Skill's directory name. |
| **Description** | Unique identifier for the Skill. Immutable after registration — renaming requires a new registration with migration path. |
| **Example** | `"browser-automation"` |
| **Validation** | `^[a-z0-9]+(-[a-z0-9]+)*$`, length ≤ 64 |

#### 2.1.2 `version`

| Property | Value |
|:---------|:------|
| **Name** | `version` |
| **Type** | `string` |
| **Required** | YES |
| **Format** | Semantic versioning (MAJOR.MINOR.PATCH) |
| **Description** | Current active version of the Skill. MAJOR bump = breaking interface change (incompatible dependency updates, removed capabilities). MINOR bump = backward-compatible new capability. PATCH bump = backward-compatible bug fix. |
| **Example** | `"2.1.0"` |
| **Validation** | `^\d+\.\d+\.\d+$` |

#### 2.1.3 `description`

| Property | Value |
|:---------|:------|
| **Name** | `description` |
| **Type** | `string` |
| **Required** | YES |
| **Format** | Free text, ≤ 1024 chars. Starts with "Use when…" trigger condition. |
| **Description** | Human-readable summary of what the Skill does and when to use it. Used by the Skill Manager for trigger matching and by operators for discovery. |
| **Example** | `"Use when performing browser automation tasks. Provides a 4-layer framework from Playwright DOM to Screenshot Vision."` |
| **Validation** | Length ≤ 1024, starts with "Use when" or equivalent trigger clause |

#### 2.1.4 `capability`

| Property | Value |
|:---------|:------|
| **Name** | `capability` |
| **Type** | `string` |
| **Required** | YES |
| **Format** | Single capability category. Format: `domain.action` or `domain.category`. |
| **Description** | The single capability domain this Skill provides. One Skill = one capability. Combined with the capability list (detailed sub-actions), this field is the primary discovery key. |
| **Example** | `"browser-automation"` |
| **Validation** | Must not be a comma-separated list — single capability only. Must match at least one entry in the Skill's own `capabilities` array. |

#### 2.1.5 `owner`

| Property | Value |
|:---------|:------|
| **Name** | `owner` |
| **Type** | `string` |
| **Required** | OPTIONAL (Phase B) |
| **Format** | Free text identifier for the responsible author or team. |
| **Description** | The author or team accountable for the Skill's maintenance. Used for ownership queries and deprecation notifications. |
| **Example** | `"agent-team"` |
| **Validation** | Non-empty string when present |

#### 2.1.6 `lifecycle`

| Property | Value |
|:---------|:------|
| **Name** | `lifecycle` |
| **Type** | `string` (enum) |
| **Required** | YES |
| **Format** | One of the defined lifecycle states (see §4). |
| **Description** | The Skill's current position in the lifecycle state machine. Drives availability, deprecation warnings, and archival decisions. Note: this field encodes the lifecycle state; `status` (§2.1.11) encodes the operational sub-status. |
| **Example** | `"active"` |
| **Values** | `proposed`, `review`, `accepted`, `registered`, `active`, `deprecated`, `archived` |
| **Validation** | Must be one of the seven defined lifecycle states |

#### 2.1.7 `dependencies`

| Property | Value |
|:---------|:------|
| **Name** | `dependencies` |
| **Type** | `object` |
| **Required** | OPTIONAL (Phase B) |
| **Format** | Object with `skills` (array of skill names with optional version constraints) and `runtime` (array of package constraints). |
| **Description** | Declared dependencies this Skill requires. Includes both other Skills and runtime packages. See §6 for the full dependency model. |
| **Example** | `{"skills": ["browser-safety >= 1.0"], "runtime": ["python >= 3.11", "playwright >= 1.40"]}` |
| **Validation** | No project-path dependencies allowed. All dependency names must refer to registered Skills or known packages. |

#### 2.1.8 `permissions`

| Property | Value |
|:---------|:------|
| **Name** | `permissions` |
| **Type** | `object` |
| **Required** | OPTIONAL (Phase B) |
| **Format** | Object with `allow` (array of permission strings/scoped objects) and `deny` (array of explicit deny rules). |
| **Description** | Declared permissions this Skill requests at runtime. The Registry records the declaration; the Governance Layer enforces it. See §5 for the full permission metadata model. |
| **Example** | `{"allow": ["filesystem.read", "network.external_api"], "deny": ["secret.read"]}` |
| **Validation** | No Tier 3 permissions allowed. Allow/deny must be disjoint. |

#### 2.1.9 `validation`

| Property | Value |
|:---------|:------|
| **Name** | `validation` |
| **Type** | `object` |
| **Required** | OPTIONAL (Phase B) |
| **Format** | Object with `command` (verification command), `expected_result` (expected output), `last_verified` (ISO date). |
| **Description** | Declares how to verify the Skill is functional. The Registry records the declaration; it does NOT execute validation. See §7. |
| **Example** | `{"command": "playwright --version", "expected_result": "Version 1.", "last_verified": "2026-07-15"}` |
| **Validation** | `command` must be a non-empty string; `last_verified` must be ISO date format when present |

#### 2.1.10 `compatibility`

| Property | Value |
|:---------|:------|
| **Name** | `compatibility` |
| **Type** | `object` |
| **Required** | OPTIONAL (Phase B) |
| **Format** | Object with `platforms` (array of OS identifiers), `providers` (array of LLM provider keys), `runtime` (array of runtime constraints). |
| **Description** | Declared environment compatibility for this Skill. See §8 for the full compatibility model. |
| **Example** | `{"platforms": ["linux", "macos"], "providers": ["openai", "anthropic", "deepseek"], "runtime": ["hermes >= 2.0"]}` |
| **Validation** | Must not bind to a single project path. Platform values from controlled vocabulary. |

#### 2.1.11 `status`

| Property | Value |
|:---------|:------|
| **Name** | `status` |
| **Type** | `string` |
| **Required** | YES |
| **Format** | Operational sub-status within the lifecycle. |
| **Description** | Indicates operational readiness within the current lifecycle state. An `active` lifecycle Skill may have status `ok`, `degraded`, or `error`. A `deprecated` Skill may have status `grace_period` or `migrating`. |
| **Example** | `"ok"` |
| **Values** | For `active` lifecycle: `ok`, `degraded`, `error`. For `deprecated`: `grace_period`, `migrating`. For other states: `null`. |
| **Validation** | Must be a valid value for the current lifecycle state, or `null`. |

#### 2.1.12 `registered`

| Property | Value |
|:---------|:------|
| **Name** | `registered` |
| **Type** | `string` (ISO 8601 date) |
| **Required** | YES |
| **Format** | `YYYY-MM-DD` |
| **Description** | Date the Skill was first registered in the Registry. Immutable after creation. Used for audit trails and age-based policy decisions. |
| **Example** | `"2026-06-01"` |
| **Validation** | ISO 8601 date format, must be ≤ current date |

#### 2.1.13 `updated`

| Property | Value |
|:---------|:------|
| **Name** | `updated` |
| **Type** | `string` (ISO 8601 date) |
| **Required** | YES |
| **Format** | `YYYY-MM-DD` |
| **Description** | Date the Skill entry was last modified (version bump, metadata change, lifecycle transition). Updated on every Registry write operation. |
| **Example** | `"2026-07-15"` |
| **Validation** | ISO 8601 date format, must be ≥ `registered` |

#### 2.1.14 `path`

| Property | Value |
|:---------|:------|
| **Name** | `path` |
| **Type** | `string` |
| **Required** | YES |
| **Format** | Relative path from skills root to the Skill's directory. |
| **Description** | Filesystem location of the Skill implementation. Used by the Skill Manager to locate and load Skill content. Must correspond to an existing directory. |
| **Example** | `"skills/browser-automation/"` |
| **Validation** | Must start with `skills/` or equivalent configured skills root. Must be a valid relative path. |

### 2.2 Summary Table

| # | Field | Type | Required (Phase B) | Phase A (Target) |
|:--|:------|:-----|:-------------------|:-----------------|
| 1 | `name` | `string` | ✅ YES | ✅ YES |
| 2 | `version` | `string` | ✅ YES | ✅ YES |
| 3 | `description` | `string` | ✅ YES | ✅ YES |
| 4 | `capability` | `string` | ✅ YES | ✅ YES |
| 5 | `owner` | `string` | OPTIONAL | ✅ YES |
| 6 | `lifecycle` | `string (enum)` | ✅ YES | ✅ YES |
| 7 | `dependencies` | `object` | OPTIONAL | ✅ YES |
| 8 | `permissions` | `object` | OPTIONAL | ✅ YES |
| 9 | `validation` | `object` | OPTIONAL | ✅ YES |
| 10 | `compatibility` | `object` | OPTIONAL | ✅ YES |
| 11 | `status` | `string` | ✅ YES | ✅ YES |
| 12 | `registered` | `string (date)` | ✅ YES | ✅ YES |
| 13 | `updated` | `string (date)` | ✅ YES | ✅ YES |
| 14 | `path` | `string` | ✅ YES | ✅ YES |

---

## 3. Required vs Optional Policy

### 3.1 Phase Strategy

The Registry Schema is deployed in **two phases** to avoid a single-shot migration of 146+ Skills:

| Phase | Scope | Fields Required |
|:------|:------|:----------------|
| **Phase B** (current) | Schema definition + contract | 7 fields: `name`, `version`, `description`, `capability`, `lifecycle`, `status`, `registered`, `updated`, `path` |
| **Phase A** (target) | Full enforcement | All 14 fields required for new registrations |

### 3.2 Phase B Required Fields (Bootstrapping)

These fields are required from Day 1 because they are **essential for identity and discovery**:

| Field | Rationale for Phase B requirement |
|:------|:----------------------------------|
| `name` | Unique identification — no Registry without names |
| `version` | Version tracking for dependency resolution |
| `description` | Human-readable discovery — operators need to find Skills |
| `capability` | Capability-based routing — Skill Manager's primary query key |
| `lifecycle` | Availability gating — deprecated Skills must be identifiable |
| `status` | Operational health — active Skills must signal readiness |
| `registered` | Audit trail — required for governance review |
| `updated` | Staleness detection — required for maintenance scheduling |
| `path` | Filesystem location — required for Skill loading |

### 3.3 Phase B Optional Fields (Progressive Migration)

These fields are optional in Phase B because existing Skills lack them and backfilling all 146 at once would block the migration:

| Field | Rationale for deferral |
|:------|:-----------------------|
| `owner` | Many existing Skills lack explicit ownership metadata; backfill requires audit |
| `permissions` | Permission model is defined in Policy §4 but not yet encoded in existing Skills |
| `compatibility` | Platform/provider data not present in current `skill-registry.json` |
| `validation` | Validation commands not yet standardized across Skills |
| `dependencies` | Dependency graph construction requires cross-Skill audit |

### 3.4 Field Maturity Model

Fields progress through maturity levels:

```
UNDEFINED  →  OPTIONAL (Phase B)  →  REQUIRED (Phase A)  →  ENFORCED (Runtime)
```

| Level | Meaning | Registry Behavior |
|:------|:--------|:------------------|
| UNDEFINED | Field not yet in schema | Not tracked |
| OPTIONAL | Field exists in schema; may be null or absent | Schema accepts null; no validation failure on absence |
| REQUIRED | Field must be present with valid value | Schema rejects null/absent at registration time |
| ENFORCED | Field value is actively checked at runtime | Governance Layer rejects Skills that violate declared values |

**Current Maturity:**

| Field | Maturity |
|:------|:---------|
| `name`, `version`, `description`, `capability`, `registered`, `updated`, `path` | REQUIRED |
| `lifecycle`, `status` | REQUIRED (default: `active` / `ok` for existing) |
| `owner`, `permissions`, `compatibility`, `validation`, `dependencies` | OPTIONAL |

---

## 4. Lifecycle Model

### 4.1 State Machine

```
                  ┌─────────────┐
                  │  PROPOSED   │  ← Author proposes new Skill
                  └──────┬──────┘
                         │  Approval: Governance Review
                         ▼
                  ┌─────────────┐
                  │   REVIEW    │  ← Governance evaluation (checklist §6 of Policy)
                  └──────┬──────┘
                         │
            ┌────────────┼────────────┐
            │            │            │
       ┌────▼───┐   ┌───▼────┐   ┌───▼────┐
       │ REJECT │   │REVISE  │   │ACCEPT  │
       └────────┘   └───┬────┘   └───┬────┘
         Terminal        │            │
                    ┌────┘            │
                    │  Approval:       │  Approval: All gates passed
                    │  Changes made    │
                    └──────┬───────────┘
                           │
                    ┌──────▼──────┐
                    │ REGISTERED  │  ← Added to Registry
                    └──────┬──────┘
                           │  Approval: System auto-transition
                           ▼
                    ┌──────────────┐
                    │   ACTIVE     │  ← Available for session use
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼───┐   ┌───▼────┐   ┌───▼───────┐
         │UPDATE  │   │PATCH   │   │DEPRECATE  │
         └────┬───┘   └───┬────┘   └─────┬─────┘
              │            │              │  Approval: Deprecation gate
         ┌────┘       ┌────┘              ▼
         ▼            ▼            ┌──────────────┐
    ┌──────────┐ ┌──────────┐     │  DEPRECATED  │
    │  ACTIVE  │ │  ACTIVE  │     └──────┬───────┘
    │(new ver) │ │(patched) │            │  Approval: Grace period elapsed
    └──────────┘ └──────────┘     ┌──────▼───────┐
                                  │  ARCHIVED    │
                                  └──────────────┘
                                     Terminal
```

### 4.2 State Definitions

#### PROPOSED

| Property | Value |
|:---------|:------|
| **Purpose** | Initial submission — a Skill idea has been documented and submitted for review |
| **Allowed Transitions** | → REVIEW (after submission) |
| **Approval Requirement** | None (any author can propose) |
| **Registry Visibility** | Internal only; not visible to Skill Manager for loading |

#### REVIEW

| Property | Value |
|:---------|:------|
| **Purpose** | Under active governance evaluation against the Skill Quality Checklist (Policy §6) |
| **Allowed Transitions** | → ACCEPT (gates passed), → REVISE (changes requested), → REJECT (does not meet policy) |
| **Approval Requirement** | Governance reviewer; all Quality Checklist items must be assessed |
| **Registry Visibility** | Internal only; not visible to Skill Manager |

#### ACCEPT

| Property | Value |
|:---------|:------|
| **Purpose** | Approved for registration; pending system registration |
| **Allowed Transitions** | → REGISTERED (automatic) |
| **Approval Requirement** | All governance gates passed (Quality + Permission + Dependency) |
| **Registry Visibility** | Internal only; pending write to Registry |

#### REGISTERED

| Property | Value |
|:---------|:------|
| **Purpose** | Metadata written to Registry; pending activation |
| **Allowed Transitions** | → ACTIVE (automatic system transition) |
| **Approval Requirement** | System (automatic — no human gate) |
| **Registry Visibility** | Visible; not yet loadable by Skill Manager |

#### ACTIVE

| Property | Value |
|:---------|:------|
| **Purpose** | Available for use in Hermes sessions. Skill Manager can load and activate this Skill. |
| **Allowed Transitions** | → DEPRECATED, → (UPDATE → ACTIVE new version), → (PATCH → ACTIVE patched) |
| **Approval Requirement** | None for continued operation. UPDATE requires re-registration of new version. DEPRECATE requires deprecation gate. |
| **Registry Visibility** | Fully visible and loadable |

#### DEPRECATED

| Property | Value |
|:---------|:------|
| **Purpose** | Replaced or obsolete; grace period before archival. Skill Manager shows deprecation warning on load. |
| **Allowed Transitions** | → ARCHIVED (after grace period) |
| **Approval Requirement** | Deprecation gate: replacement Skill identified, migration path documented, grace period announced (≥ 14 days), dependent Skills updated |
| **Registry Visibility** | Visible with deprecation warning; loadable during grace period |

#### ARCHIVED

| Property | Value |
|:---------|:------|
| **Purpose** | Removed from active use. Metadata retained for audit trail. Skill Manager will not load this Skill. |
| **Allowed Transitions** | None (Terminal) |
| **Approval Requirement** | Grace period elapsed; no active dependents |
| **Registry Visibility** | Visible for audit; not loadable |

#### REJECT (Terminal)

| Property | Value |
|:------|:------|
| **Purpose** | Does not meet Skill Policy requirements |
| **Allowed Transitions** | None (Terminal). Can be re-proposed as a new PROPOSED entry. |
| **Approval Requirement** | Governance reviewer |
| **Registry Visibility** | Internal only (audit trail) |

#### REVISE (Transient)

| Property | Value |
|:------|:------|
| **Purpose** | Changes requested by reviewer; returned to author |
| **Allowed Transitions** | → REVIEW (after changes made) |
| **Approval Requirement** | Author makes changes; reviewer re-evaluates |
| **Registry Visibility** | Internal only |

### 4.3 Transition Rules Summary

| From | To | Trigger | Gate |
|:-----|:---|:--------|:-----|
| PROPOSED | REVIEW | Author submits for review | — |
| REVIEW | ACCEPT | All checklist items pass | Quality + Permission + Dependency gates |
| REVIEW | REVISE | Reviewer requests changes | — |
| REVIEW | REJECT | Skill does not meet policy | Reviewer decision |
| REVISE | REVIEW | Author submits revised version | — |
| ACCEPT | REGISTERED | System writes to Registry | Automatic |
| REGISTERED | ACTIVE | System activates | Automatic |
| ACTIVE | DEPRECATED | Replacement available or obsolete | Deprecation gate |
| DEPRECATED | ARCHIVED | Grace period elapsed | No active dependents |

---

## 5. Permission Metadata Model

### 5.1 Principle

The Registry **records permission declarations**. It does NOT enforce them. Permission enforcement belongs to the Governance Layer (Hermes Governance Protocol).

### 5.2 Registry Role

```
Permission declaration → Registry (stores metadata)
                               │
                               ▼
Permission enforcement  → Governance Layer (validates at runtime)
```

The Registry is a **passive record**. A Skill's `permissions` field declares what the Skill *claims* it needs. The Governance Layer verifies this claim against actual runtime behavior.

### 5.3 Schema

```yaml
permissions:
  allow:                          # Permission grants (Tier 0-2)
    - filesystem.read             # Tier 0 — read-only file access
    - filesystem.write:           # Tier 1 — scoped write
        paths: ["/workspace/**", "/tmp/hermes-skill-*"]
        exclude: [".env", "*.key", "*.pem"]
    - tool.exec:                  # Tier 1 — whitelist commands
        allow_list: ["pylint", "pytest", "bandit"]
    - network.external_api:       # Tier 1 — domain-scoped
        domains: ["api.github.com", "pypi.org"]
  deny:                           # Explicit denies (override allow globs)
    - filesystem.write:
        paths: ["~/.ssh/**", "~/.hermes/config.yaml"]
    - secret.read                 # Never allowed
```

### 5.4 Permission Tiers

| Tier | Scope | Registry Behavior |
|:-----|:------|:------------------|
| Tier 0 | Read-only, no side effects | Always accepted |
| Tier 1 | Read + write within declared scope | Accepted if scope is declared |
| Tier 2 | Cross-agent, system config | Flagged for review |
| Tier 3 | Governance modification, runtime control | **Prohibited — rejected at registration** |

### 5.5 Permission Authority

| Question | Answer |
|:---------|:-------|
| Who defines permissions? | Skill author (in Skill metadata) |
| Who records permissions? | Registry (this schema) |
| Who enforces permissions? | Governance Layer (Protocol) |
| Who can override permissions? | Governance reviewer (at registration time) |
| Where are permissions checked? | At Skill activation (runtime), not in Registry |

---

## 6. Dependency Model

### 6.1 Principle

Dependencies **must be declared** and **must refer to registered Skills or known packages**. Hidden dependencies and project-path dependencies are forbidden.

### 6.2 Schema

```yaml
dependencies:
  skills:                         # Other Skills this Skill depends on
    - "browser-safety >= 1.0"     # With version constraint
    - "layer1-playwright"         # Without constraint (any version)
  runtime:                        # Runtime packages
    - "python >= 3.11"
    - "playwright >= 1.40"
```

### 6.3 Allowed Dependencies

| ✅ Allowed | Example |
|:-----------|:--------|
| Registered Skill with version constraint | `"browser-safety >= 1.0"` |
| Registered Skill without version constraint | `"layer1-playwright"` |
| Known runtime package with constraint | `"playwright >= 1.40"` |
| Known system tool | `"git >= 2.40"` |

### 6.4 Forbidden Dependencies

| ❌ Forbidden | Example | Why |
|:-------------|:--------|:----|
| Hidden dependency (undeclared) | Skill uses another Skill's output without declaring it | Violates isolation rules |
| Project path dependency | `"depends on ~/A3-Multi-Agent-System"` | Binds to a specific project layout; breaks portability |
| Absolute path dependency | `"/home/user/projects/tools/"` | Not portable across environments |
| Unregistered Skill | `"my-custom-helper"` (not in Registry) | Skill Manager cannot resolve it |
| Governance modification | `"governance-protocol"` | Governance is not a Skill dependency |

### 6.5 Dependency Validation Rules

| Rule | Enforcement |
|:-----|:------------|
| All `skills` entries must exist in Registry | Schema validation |
| All `runtime` entries must match known package patterns | Schema validation |
| No entries may contain paths (absolute or relative with `~` or `/`) | Schema validation |
| Circular dependencies detected and rejected | Schema validation |
| Dependency on deprecated Skill → warning, not error | Schema validation |

---

## 7. Validation Model

### 7.1 Principle

The Schema defines **validation metadata** — how to verify a Skill is functional. The Registry stores these declarations. Validation is **executed externally** (not by the Registry).

### 7.2 Schema

```yaml
validation:
  command: "playwright --version"       # Command to verify functionality
  expected_result: "Version 1."         # Expected output pattern
  last_verified: "2026-07-15"          # ISO date of last successful verification
  test_command: "pytest tests/"         # Comprehensive test command (optional)
```

### 7.3 Field Definitions

| Field | Required | Description |
|:------|:---------|:------------|
| `command` | OPTIONAL | A shell command that verifies the Skill's environment is functional |
| `expected_result` | OPTIONAL | A substring or regex that must appear in the command's output for success |
| `last_verified` | OPTIONAL | ISO 8601 date when validation was last run successfully |
| `test_command` | OPTIONAL | A more comprehensive test command (e.g., pytest suite) |

### 7.4 Validation Authority

| Question | Answer |
|:---------|:-------|
| Who defines validation? | Skill author (in Skill metadata) |
| Who stores validation metadata? | Registry (this field) |
| Who executes validation? | Validation tooling (external to Registry) |
| Who updates `last_verified`? | Validation tooling after successful run |
| When is validation run? | On registration, on update, on schedule, on demand |

---

## 8. Compatibility Model

### 8.1 Principle

Skills declare their **environment compatibility** — which platforms, providers, and runtimes they support. This enables capability discovery that filters by the user's actual environment.

### 8.2 Schema

```yaml
compatibility:
  platforms:                          # Supported operating systems
    - linux
    - macos
  providers:                          # Supported LLM providers
    - openai
    - anthropic
    - deepseek
  runtime:                            # Required runtime version
    - "hermes >= 2.0"
  tools:                              # Required external tools (optional)
    - "chromium >= 120"
    - "node >= 20"
```

### 8.3 Field Definitions

| Field | Required | Description |
|:------|:---------|:------------|
| `platforms` | OPTIONAL | Array of OS identifiers: `linux`, `macos`, `windows` |
| `providers` | OPTIONAL | Array of LLM provider keys the Skill is compatible with |
| `runtime` | OPTIONAL | Array of Hermes runtime version constraints |
| `tools` | OPTIONAL | Array of external tool version constraints |

### 8.4 Constraints

| Rule | Rationale |
|:-----|:----------|
| Must NOT bind to a single project path | Skills are environment-portable, not project-specific |
| Must NOT reference project-specific config files | `~/.hermes/config.yaml` is Hermes config, not project config — but Skills should not depend on specific config values |
| Platform values from controlled vocabulary | Prevents typos like `"ubuntu"` vs `"linux"` |
| Provider values from known provider keys | Prevents references to non-existent providers |

### 8.5 Compatibility Mismatch Behavior

When a Skill's `compatibility` field conflicts with the user's environment:

| Mismatch | Behavior |
|:---------|:---------|
| Platform mismatch | Skill Manager skips the Skill; logs warning |
| Provider mismatch | Skill Manager skips the Skill; suggests alternatives |
| Runtime too old | Skill Manager warns; Skill may still load (best-effort) |
| Tool missing | Skill activation fails; error reported |

---

## 9. Migration Mapping

### 9.1 Current Registry Structure

The existing `skill-registry.json` has 6 fields per entry + 2 top-level fields + 2 global config sections:

**Per-Skill Fields (current):**

| Current Field | Type | Example |
|:--------------|:-----|:--------|
| `name` | `string` | `"browser-automation"` |
| `category` | `string` | `"browser-automation"` |
| `tags` | `array[string]` | `["umbrella"]` |
| `mount` | `string` | `"routed"` |
| `description` | `string` | `"浏览器自动化伞技能"` |
| `trigger` | `array[string]` | `["webpage", "browser", "login"]` |
| `parent` | `string` (optional) | `"browser-automation"` |
| `fallback` | `string` (optional) | `"ucampus-auto-complete"` |

**Top-Level Fields (current):**

| Current Field | Example |
|:--------------|:--------|
| `version` | `"1.0.0"` |
| `updated` | `"2026-06-05"` |

**Global Config (current):**

| Current Section | Purpose |
|:----------------|:--------|
| `mount_strategies` | Defines mount behavior for `always`/`auto`/`routed` |
| `forbidden_pairs` | Declares mutually exclusive Skill combinations |

### 9.2 Mapping Table

| Current Field | New Field | Mapping Strategy |
|:--------------|:----------|:-----------------|
| `name` | `name` | **Direct** — identical value |
| `version` (top-level) | `version` (per-entry) | **Hoist** — top-level version becomes per-entry; initially all entries share the same version |
| `updated` (top-level) | `updated` (per-entry) | **Hoist** — top-level date becomes per-entry; initially all entries share the same date |
| `description` | `description` | **Direct** — identical value |
| `category` | `capability` | **Rename** — category becomes the capability value. Multi-word categories map directly (e.g., `"browser-automation"` → `"browser-automation"`). |
| `tags` | *(absorbed)* | **Remove** — tags are absorbed into `capability` and description. No direct mapping; tags served as ad-hoc categorization that the `capability` field formalizes. |
| `mount` | *(absorbed)* | **Remove** — mount strategy moves out of the Registry entry. The `mount` field was a Skill Manager operational concern, not a Registry metadata concern. It lives in the Skill Manager's own configuration, not in the Schema. |
| `trigger` | *(absorbed)* | **Remove** — trigger patterns are a Skill Manager routing concern, not a Registry metadata concern. Triggers belong to the Skill's own SKILL.md frontmatter, referenced by the Skill Manager at load time, not stored in the Registry. |
| `parent` | `dependencies.skills` | **Migrate** — parent Skill name becomes a dependency entry: `"parent": "browser-automation"` → `"dependencies": {"skills": ["browser-automation"]}` |
| `fallback` | *(absorbed)* | **Remove** — fallback is a Skill Manager routing concern. When a Skill cannot be loaded, the Skill Manager decides the fallback based on its own configuration, not the Registry entry. |
| (new) | `lifecycle` | **Default** — all existing Skills default to `"active"` |
| (new) | `status` | **Default** — all existing Skills default to `"ok"` |
| (new) | `registered` | **Default** — set to current `updated` date on migration |
| (new) | `path` | **Derive** — constructed from `name`: `"skills/<name>/"` |
| (new) | `owner` | **Default** — `null` (backfilled later) |
| (new) | `permissions` | **Default** — `null` (backfilled later) |
| (new) | `validation` | **Default** — `null` (backfilled later) |
| (new) | `compatibility` | **Default** — `null` (backfilled later) |
| (new) | `dependencies` | **Default** — `null` unless `parent` is present |
| `mount_strategies` | *(removed)* | **Remove** — global config moves to Skill Manager configuration |
| `forbidden_pairs` | *(removed)* | **Remove** — global config moves to Skill Manager or Governance Layer configuration |

### 9.3 What Changes

| Aspect | Change |
|:-------|:-------|
| Structure | From flat + global config → per-entry records + no global config in Registry |
| Fields | From 6 → 14 (9 required, 5 optional in Phase B) |
| Top-Level | `version` and `updated` hoisted to per-entry |
| Routing Concerns | `mount`, `trigger`, `fallback`, `mount_strategies`, `forbidden_pairs` removed from Registry |
| Ownership | New `owner`, `lifecycle`, `status`, `registered`, `path`, `permissions`, `validation`, `compatibility`, `dependencies` fields |

### 9.4 What Stays the Same

| Aspect | Preserved |
|:-------|:----------|
| `name` | Identical field, identical value |
| `description` | Identical field, identical value |
| Skill count | All 146 Skills remain registered |
| Forbidden pairs | Logic preserved; location moves to Governance Layer |

---

## 10. Backward Compatibility

### 10.1 Phase B Strategy: Schema First

Phase B does NOT modify the existing `skill-registry.json`. The Schema is defined as a **contract document** — the target specification that future migration tooling will implement.

```
Current State (Phase B):
  ┌─────────────────────────┐
  │ skill-registry.json     │  ← Unchanged (2/12 fields)
  │ (oldschema — 6 fields)  │
  └───────────┬─────────────┘
              │
              │  Schema Validation (future)
              │
              ▼
  ┌─────────────────────────┐
  │ Registry Schema v1.0    │  ← This document (contract)
  │ (newschema — 14 fields) │
  └───────────┬─────────────┘
              │
              │  Migration Tool (future — Phase A)
              │
              ▼
  ┌─────────────────────────┐
  │ skill-registry.json     │  ← Migrated (12/12 fields)
  │ (newschema — 14 fields) │
  └─────────────────────────┘
```

### 10.2 Compatibility Guarantees

| Guarantee | How |
|:----------|:----|
| Existing Registry untouched | Phase B is read-only — no writes to `skill-registry.json` |
| Existing Skills continue to work | Skill Manager reads the old Registry format until migration |
| New registrations follow new schema | New Skills registered after migration use the full 14-field schema |
| Old Registry validates against schema | Migration tool validates old entries before writing new entries |
| Rollback path exists | Old `skill-registry.json` backed up before migration; revert by restoring backup |

### 10.3 Transition Path

| Step | Action | Impact |
|:-----|:-------|:-------|
| 1 | Schema document published (this doc) | Zero impact on runtime |
| 2 | Migration tool developed (Phase A) | Zero impact until run |
| 3 | Migration tool run against old Registry | Old file backed up; new file written |
| 4 | Skill Manager updated to read new schema | Skills continue to load; legacy `mount`/`trigger` fields read from SKILL.md |
| 5 | Old Registry format retired | Only new schema accepted |

---

## 11. Architecture Boundary Check

### 11.1 Registry vs Runtime

| Boundary | Registry | Runtime |
|:---------|:---------|:--------|
| **Function** | Stores metadata | Executes Skills |
| **When active** | On registration, query, migration | During Hermes sessions |
| **State** | Persistent (file) | Ephemeral (memory) |
| **Modifies** | Skill entries (metadata) | Files, network, tools |
| **Governed by** | Policy §9 + this Schema | Governance Protocol |

**Registry ≠ Runtime.** The Registry is a catalog, not an execution engine.

### 11.2 Registry vs Governance Engine

| Boundary | Registry | Governance Engine |
|:---------|:---------|:------------------|
| **Function** | Records declarations | Enforces rules |
| **Permission model** | Stores `permissions` field | Validates actual behavior against declared permissions |
| **Lifecycle** | Stores `lifecycle` field | Gates lifecycle transitions (REVIEW → ACCEPT → …) |
| **Approval** | Records outcomes | Executes approval flows |

**Registry ≠ Governance Engine.** The Registry is a passive record; Governance is an active enforcer.

### 11.3 Registry vs Skill Executor

| Boundary | Registry | Skill Executor |
|:---------|:---------|:---------------|
| **Function** | Catalogs Skills | Loads and runs Skills |
| **Content** | Metadata only | Full Skill implementation (SKILL.md + code) |
| **Trigger** | Registration events | Session requests |
| **Output** | Query results | Task outputs, files, events |

**Registry ≠ Skill Executor.** The Registry does not load or run Skills.

### 11.4 Registry vs Agent

| Boundary | Registry | Agent |
|:---------|:---------|:------|
| **Function** | Skill catalog | Autonomous task execution |
| **Identity** | Data store | Active process |
| **Decision-making** | None (passive) | Full (active) |
| **Dependencies** | None (standalone file) | Skills, tools, memory |

**Registry ≠ Agent.** The Registry is a data structure, not an agent.

### 11.5 Boundary Summary

```
┌──────────────────────────────────────────────────────────┐
│                    Hermes System                          │
│                                                          │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │  Governance  │  │   Registry    │  │    Agent      │  │
│  │   Engine     │  │   (this doc)  │  │               │  │
│  │              │  │               │  │               │  │
│  │ Enforces     │  │ Catalogs      │  │ Executes      │  │
│  │ rules        │  │ metadata      │  │ tasks         │  │
│  └──────┬───────┘  └───────┬───────┘  └───────┬───────┘  │
│         │                  │                   │          │
│         │    ┌─────────────┼───────────────────┘          │
│         │    │             │                              │
│         ▼    ▼             ▼                              │
│  ┌──────────────────────────────────┐                     │
│  │        Skill Executor            │                     │
│  │  Loads Skills → Runs → Reports   │                     │
│  └──────────────────────────────────┘                     │
│                                                          │
│  ┌──────────────────────────────────┐                     │
│  │        Skill Implementations     │                     │
│  │  SKILL.md files in skills/ dir   │                     │
│  └──────────────────────────────────┘                     │
└──────────────────────────────────────────────────────────┘
```

The Registry touches exactly one thing: **Skill metadata**. It does not govern, execute, or decide.

---

## 12. Verification Checklist

### 12.1 Schema Completeness

| # | Check | Status |
|:--|:------|:-------|
| 1 | All 14 fields defined with Name, Type, Required, Description, Example | ✅ |
| 2 | Required vs Optional policy documented (§3) | ✅ |
| 3 | Lifecycle model: 7 states with purpose, transitions, approval requirements (§4) | ✅ |
| 4 | Permission metadata model: schema, tiers, authority (§5) | ✅ |
| 5 | Dependency model: allowed/forbidden, validation rules (§6) | ✅ |
| 6 | Validation model: schema, fields, authority (§7) | ✅ |
| 7 | Compatibility model: schema, fields, constraints (§8) | ✅ |
| 8 | Migration mapping: old → new field table, what changes/stays (§9) | ✅ |
| 9 | Backward compatibility: Phase B strategy, guarantees, transition path (§10) | ✅ |
| 10 | Architecture boundary check: Registry vs Runtime/Governance/Executor/Agent (§11) | ✅ |

### 12.2 Boundary Compliance

| # | Check | Status |
|:--|:------|:-------|
| 1 | Does this document modify `skill-registry.json`? | ✅ NO — read-only reference |
| 2 | Does this document implement a runtime? | ✅ NO — contract only |
| 3 | Does this document define governance rules? | ✅ NO — references Policy, does not extend it |
| 4 | Does this document implement a validator? | ✅ NO — defines schema for validation, not implementation |
| 5 | Does this document contain code? | ✅ NO — YAML examples are illustrative |
| 6 | Does this document depend on a specific project? | ✅ NO — no project paths referenced |
| 7 | Does this document modify Hermes Runtime? | ✅ NO — documentation only |
| 8 | Does this document modify Governance Protocol? | ✅ NO — child document under Policy §9 |
| 9 | Does this document modify Skill Policy v1.0? | ✅ NO — extends §9, does not modify it |

### 12.3 Migration Safety

| # | Check | Status |
|:--|:------|:-------|
| 1 | Existing Registry remains unchanged during Phase B? | ✅ YES — contract only |
| 2 | Migration path documented (old → new mapping)? | ✅ YES — §9 |
| 3 | Default values defined for existing entries? | ✅ YES — lifecycle=`active`, status=`ok`, etc. |
| 4 | Backward compatibility window defined? | ✅ YES — Phase B precedes migration |
| 5 | Forbidden pairs logic preserved? | ✅ YES — moves to Governance Layer |

### 12.4 Rollback Safety

| # | Check | Status |
|:--|:------|:-------|
| 1 | Can Phase B be rolled back? | ✅ YES — this document can be superseded; no data was modified |
| 2 | Does rollback break existing Skills? | ✅ NO — existing Registry format is unchanged |
| 3 | Is a backup strategy defined? | ✅ YES — backup before migration (Phase A) |
| 4 | Is the transition path reversible? | ✅ YES — restore old file, point Skill Manager at old format |

### 12.5 Document Completeness

| # | Check | Status |
|:--|:------|:-------|
| 1 | All 12 required sections present? | ✅ YES |
| 2 | Section numbering consistent? | ✅ YES |
| 3 | No TODO markers or placeholders? | ✅ YES |
| 4 | Examples use real data (not `xxx` or `TODO`)? | ✅ YES |

---

> **Schema Status:** Active v1.0
> **Governance Stack:** Protocol → Workflow → Skill Policy §9 → Registry Schema (this doc) → Registry Implementation
> **Phase:** B.0 — Specification Complete
> **Next:** Wave 0 (migration tooling) — Phase A
> **Amendment Process:** Type D change (requires explicit architecture approval)
> **Parent Document:** Hermes Skill Governance Policy v1.0, §9 — Skill Registry Design
