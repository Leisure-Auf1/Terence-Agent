# Hermes Registry Namespace Schema Amendment

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** C.3.1 — Registry Namespace Schema Amendment
**Audience:** Governance Reviewer (Human) · Registry Schema Maintainer
**Purpose:** Formally amend B.0 Registry Schema v1.0 to add namespace, scope, and ownership fields per C.3 namespace model

**Dependencies (completed):**
- Hermes Skill Registry Schema v1.0 (Phase B.0)
- Hermes Skill Policy v1.0 §9
- Hermes Project Namespace Boundary Review (Phase C.3)

**This document is:**
- A formal amendment to `hermes-skill-registry-schema.md` (B.0)
- A field-level specification for `namespace`, `scope`, `ownership`
- A definition of namespace rules and field relationships
- A compatibility plan for existing Skills during migration

**This document does NOT:**
- Modify the Registry implementation
- Modify any Skill
- Execute migration
- Replace B.0 — it supplements B.0

---

## 1. Amendment Objective

### 1.1 Why This Amendment Exists

Phase B.0 Registry Schema v1.0 defines **14 fields** for Skill metadata. Those fields cover **identity** (`name`, `version`, `capability`) and **operational metadata** (`owner`, `permissions`, `dependencies`, `validation`), but they do NOT capture:

| Gap | Problem | Caused By |
|:-----|:-----|:-----|
| **No ecosystem location** | `name` alone cannot distinguish `hermes.core.*` from `project.a3.*` | Flat namespace in original design |
| **No architectural boundary** | Nothing prevents a Project Skill from being loaded as if it were Core | No scope field |
| **No ownership tier** | `owner: "agent-team"` is the same string whether the Skill is Core or Project | Owner field is flat text, not tiered |
| **No layer enforcement** | Registry cannot reject `hermes.core.a3.*` — nothing in schema forbids it | No namespace validation rules |

**This amendment adds 3 fields that solve all 4 gaps simultaneously.**

### 1.2 Relationship to B.0

```
B.0 Registry Schema v1.0 (14 fields)
        +
C.3.1 Namespace Amendment (this document — 3 new fields)
        =
Registry Schema v1.1 (17 fields)
```

This document is a **supplement**, not a replacement. All 14 existing fields in B.0 remain unchanged. The 3 new fields are defined with the same structure (type, required, format, description, example, validation) as the existing B.0 fields.

### 1.3 Position in Governance Stack (Updated)

```
Governance Protocol (rules, constraints)
        │
        ▼
Skill Policy §9 (parent — 9-section spec)
        │
        ▼
Registry Schema B.0 (14 fields — identity + operational)
        │
        ▼
C.3.1 Amendment (this document — 3 namespace fields)
        │
        ▼
Registry Schema v1.1 (17 fields — complete contract)
        │
        ▼
Registry Implementation (skill-registry.json/yaml — data)
        │
        ▼
Individual Skills (SKILL.md — implementation)
```

---

## 2. New Field Definitions

### 2.1 Summary

| # | Field | Type | Required (Phase B) | Required (Phase A) | Purpose |
|:--|:------|:-----|:------------------|:------------------|:-----|
| 15 | `namespace` | `string` | OPTIONAL | ✅ YES | Ecosystem location within the three-layer model |
| 16 | `scope` | `string (enum)` | OPTIONAL | ✅ YES | Architectural boundary classification |
| 17 | `ownership` | `object` | OPTIONAL | ✅ YES | Tiered ownership metadata |

### 2.2 Field #15: `namespace`

#### 2.2.1 Specification

| Property | Value |
|:---------|:------|
| **Name** | `namespace` |
| **Type** | `string` |
| **Required** | OPTIONAL (Phase B), YES (Phase A) |
| **Format** | Dot-separated hierarchical identifier: `<layer>.<domain>[.<subdomain>]*` |
| **Description** | Fully qualified namespace identifier that positions this Skill within the Hermes three-layer ecosystem. The namespace is the Skill's **ecosystem address** — it tells the Registry and loading system where this Skill belongs, what layer governs it, and what dependency rules apply to it. Unlike `name` (which identifies the Skill), `namespace` identifies the Skill's **position** in the architecture. |
| **Example** | `"project.a3.workflow"` |
| **Validation** | See §3.1 Namespace Rules below |

#### 2.2.2 Layer Prefixes

| Prefix | Layer | Scope | Examples |
|:------|:-----|:-----|:-----|
| `hermes.core` | Core | `core` | `hermes.core.governance`, `hermes.core.registry`, `hermes.core.preflight` |
| `adapter` | Adapter | `adapter` | `adapter.browser`, `adapter.github`, `adapter.cli` |
| `project.<id>` | Project | `project` | `project.a3.workflow`, `project.veritas.core`, `project.ucampus.automation` |

#### 2.2.3 Valid Namespace Pattern

```
Pattern: ^((hermes\.core)|(adapter)|(project\.[a-z0-9-]+))\.[a-z0-9-]+(\.[a-z0-9-]+)*$

Matching:
  ✅ hermes.core.governance
  ✅ hermes.core.registry
  ✅ adapter.browser.automation
  ✅ adapter.github.pr
  ✅ project.a3.workflow
  ✅ project.veritas.core
  ✅ project.ucampus.automation
  ✅ project.my-project.ci.cd            (deeply nested allowed)

Not matching:
  ❌ hermes.core.a3.workflow              (Core cannot contain project prefix)
  ❌ hermes.core.veritas.core             (Core cannot contain project prefix)
  ❌ adapter.project.a3                   (Adapter cannot contain project prefix)
  ❌ project..a3                          (double dot)
  ❌ a3.workflow                          (missing layer prefix)
  ❌ hermes.core                          (must have sub-domain)
  ❌ adapter                              (must have sub-domain)
  ❌ project.a3                           (must have sub-domain)
```

#### 2.2.4 Field Semantics

`namespace` is:

| ✅ IS | Description |
|:------|:------------|
| **Ecosystem location** | Where this Skill sits in the three-layer architecture |
| **Loading path qualifier** | Prefix that determines loading behavior and dependency rules |
| **Unique identifier** | Each namespace maps to exactly one Skill (no two Skills share a namespace) |
| **Immutable after registration** | Changing namespace requires deprecation + re-registration |

`namespace` is NOT:

| ❌ IS NOT | Description |
|:----------|:------------|
| **A replacement for `name`** | `name` = capability identity; `namespace` = ecosystem location |
| **A filesystem path** | `path` (field #14) remains the filesystem location |
| **A version identifier** | `version` (field #2) remains the version tracking mechanism |
| **A capability descriptor** | `capability` (field #4) remains the capability domain |

#### 2.2.5 Field Relationship: `namespace` ↔ `name`

```
Skill: a3-multi-agent-pipeline

name:      multi-agent-pipeline        ← "What is this Skill?"
namespace: project.a3.workflow          ← "Where does this Skill live?"

Together, they form the full identity:
  project.a3.workflow/multi-agent-pipeline

In Registry queries:
  namespace = "project.a3"  →  all A3 project Skills
  name       = "pipeline"   →  partial match across all namespaces
```

#### 2.2.6 Field Relationship: `namespace` ↔ `scope`

The `namespace` prefix MUST match the `scope` value:

| namespace prefix | scope MUST be | Violation example |
|:-----|:-----|:-----|
| `hermes.core.*` | `core` | `namespace: hermes.core.governance` + `scope: project` → REJECTED |
| `adapter.*` | `adapter` | `namespace: adapter.browser` + `scope: core` → REJECTED |
| `project.<id>.*` | `project` | `namespace: project.a3.workflow` + `scope: adapter` → REJECTED |

This cross-field validation is enforced at registration time.

---

### 2.3 Field #16: `scope`

#### 2.3.1 Specification

| Property | Value |
|:---------|:------|
| **Name** | `scope` |
| **Type** | `string` (enum) |
| **Required** | OPTIONAL (Phase B), YES (Phase A) |
| **Format** | One of: `core`, `adapter`, `project` |
| **Description** | The architectural scope of this Skill within the three-layer model. Scope determines (a) which layer governs this Skill, (b) what dependency rules apply, and (c) which Skills it may depend on and be depended on by. Scope is **immutable after initial registration** — changing scope requires deprecation of the old entry and full REVIEW→ACCEPT for the new scope. |
| **Example** | `"project"` |
| **Values** | `core`, `adapter`, `project` |
| **Validation** | Must be one of the three defined values. Must match the namespace prefix (see §2.2.6). Immutable after first `active` lifecycle transition. |

#### 2.3.2 Scope Definitions

| Scope | Definition | Governance | Dependency Rules |
|:-----|:-----|:-----|:-----|
| `core` | Defines Hermes' own operational behavior — governance protocol, registry, workflow orchestration, error handling, session tracking. Loaded into every Hermes session. | Hermes Governance Team | Depends ONLY on other `core` Skills. NEVER on `adapter` or `project`. |
| `adapter` | Bridges Hermes to external systems — browsers, GitHub, desktop, CLI tools, email, media, MCP servers. Available to all Projects. Must be **neutral** — contains zero project-specific logic or paths. | Hermes Platform Team | May depend on `core` Skills. NEVER on `project` Skills. |
| `project` | Owned by a specific consuming project — A3 multi-agent workflows, Veritas-Core development patterns, UCampus course automation. Contains project-specific knowledge that would lose meaning if genericized. | Project team | May depend on `core` and `adapter` Skills. May depend on other `project` Skills within the same namespace. Cross-project dependencies require explicit declaration. |

#### 2.3.3 Scope Immutability Rule

```
Scope is set at registration and CANNOT be changed after activation.

To change a Skill's scope:
  1. Deprecate the old entry (lifecycle: deprecated)
  2. Register a new entry with the new scope
  3. Set replaced_by on the old entry → new entry

Rationale: Scope determines dependency rules across the entire ecosystem.
Changing scope silently would break dependency validation for all dependents.
```

#### 2.3.4 Scope Decision Flow

```
New Skill proposed → Answer these questions in order:

Q1: "Does this Skill define how Hermes itself operates?"
    YES → scope = core, namespace = hermes.core.<domain>
    NO  → Q2

Q2: "Does this Skill bridge Hermes to an external system?"
    YES → scope = adapter, namespace = adapter.<domain>
    NO  → Q3

Q3: "Is this Skill owned by a specific consuming project?"
    YES → scope = project, namespace = project.<id>.<domain>
    NO  → REJECTED — Skill without clear scope is ambiguous
```

---

### 2.4 Field #17: `ownership`

#### 2.4.1 Specification

| Property | Value |
|:---------|:------|
| **Name** | `ownership` |
| **Type** | `object` |
| **Required** | OPTIONAL (Phase B), YES (Phase A) |
| **Format** | Object with `tier` (integer), `owner` (string), `namespace` (string), `promoted_from` (string|null), `delegated_to` (string|null) |
| **Description** | Tiered ownership metadata that defines **who is responsible** for this Skill and **what authority** they have. Unlike the flat `owner` field (field #5, which identifies the maintainer), `ownership` captures the structured responsibility model: tier (0=Core, 1=Adapter, 2=Project), owning team, namespace binding, and ownership transfer history. |
| **Example** | `{"tier": 2, "owner": "a3-team", "namespace": "project.a3", "promoted_from": null, "delegated_to": null}` |

#### 2.4.2 Ownership Field: `tier`

| Property | Value |
|:---------|:------|
| **Name** | `ownership.tier` |
| **Type** | `integer` |
| **Required** | YES (within the `ownership` object) |
| **Format** | Integer: 0, 1, or 2 |
| **Description** | Ownership tier that determines authority level. Must match the Skill's `scope`. |
| **Values** | `0` = Core (hermes-governance), `1` = Adapter (hermes-platform), `2` = Project (project-team) |
| **Validation** | `tier: 0` ↔ `scope: core`. `tier: 1` ↔ `scope: adapter`. `tier: 2` ↔ `scope: project`. |

#### 2.4.3 Ownership Field: `owner`

| Property | Value |
|:---------|:------|
| **Name** | `ownership.owner` |
| **Type** | `string` |
| **Required** | YES (within the `ownership` object) |
| **Format** | Team or individual identifier |
| **Description** | The team or individual responsible for this Skill's maintenance, deprecation decisions, and quality. Must match the tier's canonical owner for Core and Adapter tiers. |
| **Values** | `"hermes-governance"` (tier 0), `"hermes-platform"` (tier 1), free-form team name (tier 2) |
| **Validation** | tier 0 → `"hermes-governance"`. tier 1 → `"hermes-platform"`. tier 2 → any non-empty string. |

#### 2.4.4 Ownership Field: `namespace`

| Property | Value |
|:---------|:------|
| **Name** | `ownership.namespace` |
| **Type** | `string` |
| **Required** | YES (within the `ownership` object) |
| **Format** | The owning namespace prefix (e.g., `"project.a3"`, `"hermes.core"`, `"adapter"`) |
| **Description** | The namespace this Skill is owned under. Must match the Skill's `namespace` field prefix. For Core Skills: `"hermes.core"`. For Adapter Skills: `"adapter"`. For Project Skills: `"project.<id>"`. |
| **Validation** | Must be a prefix of the Skill's `namespace` field. `namespace: project.a3.workflow` → `ownership.namespace: project.a3`. |

#### 2.4.5 Ownership Field: `promoted_from`

| Property | Value |
|:---------|:------|
| **Name** | `ownership.promoted_from` |
| **Type** | `string` or `null` |
| **Required** | NO (null for non-promoted Skills) |
| **Format** | Previous namespace, or `null` |
| **Description** | If this Skill was promoted from Project to Adapter (proven reusable across ≥2 Projects), this field records the original namespace. Used for audit trail and to track promotion history. |
| **Example** | `"project.a3.browser"` (promoted to `adapter.browser`) |
| **Validation** | Required when `tier=1` and previously `tier=2`. Must reference a namespace that exists (or existed) in the Registry. |

#### 2.4.6 Ownership Field: `delegated_to`

| Property | Value |
|:---------|:------|
| **Name** | `ownership.delegated_to` |
| **Type** | `string` or `null` |
| **Required** | NO (null when no delegation) |
| **Format** | New owner identifier, or `null` |
| **Description** | If ownership has been transferred to another team, this records the new owner. Used when a Project Skill is adopted by another project or when maintenance responsibility shifts. |
| **Example** | `"new-team"` |
| **Validation** | Must be a valid team identifier when set. `owner` field (field #5) should be updated to match. |

#### 2.4.7 Field Relationship: `ownership` ↔ `owner`

```
ownership.owner  =  structured responsibility identity (tiered, validated)
owner (field #5) =  flat display name for queries and deprecation notices

They MUST match in value:
  ownership.owner: "hermes-governance"  →  owner: "hermes-governance"  ✅
  ownership.owner: "a3-team"            →  owner: "agent-team"         ❌ MISMATCH

If they diverge, the audit CLI must flag this as a Warning.
```

#### 2.4.8 Field Relationship: `ownership` ↔ `scope`

| ownership.tier | scope MUST be |
|:-------------|:-------------|
| 0 | `core` |
| 1 | `adapter` |
| 2 | `project` |

Cross-field validation enforces this at registration. A Skill with `ownership.tier: 0` and `scope: project` would be rejected.

---

## 3. Namespace Rules

### 3.1 Namespace Validation Rules

| # | Rule | Enforcement | Rationale |
|:--|:-----|:-----|:-----|
| **R1** | Namespace must match pattern `^(hermes\.core\|adapter\|project\.[a-z0-9-]+)\.[a-z0-9-]+(\.[a-z0-9-]+)*$` | Registration rejection | Enforces hierarchical layer format |
| **R2** | No two Skills may share the same namespace | Registration rejection | Namespace is the unique ecosystem address |
| **R3** | Namespace must match scope: `hermes.core.*` → `core`, `adapter.*` → `adapter`, `project.<id>.*` → `project` | Registration rejection | Prevents scope/namespace mismatch |
| **R4** | Namespace is immutable after `active` lifecycle state | Update rejection | Preserves ecosystem stability |
| **R5** | `hermes.core.*` must not contain project identifiers in sub-domains | Registration rejection | Core must not be project-coupled |
| **R6** | `adapter.*` must not contain project identifiers in sub-domains | Registration rejection | Adapter must be project-neutral |
| **R7** | `project.<id>.*` must use the project's registered identifier | Registration rejection | Prevents namespace squatting |
| **R8** | Project namespace `<id>` must be registered before Skills can use it | Registration rejection | Ensures project identity exists before Skills |

### 3.2 Prohibited Namespace Patterns

| Pattern | Reason | Example |
|:-----|:-----|:-----|
| `hermes.core.a3.*` | Core cannot contain project namespace | `hermes.core.a3.workflow` ❌ |
| `hermes.core.veritas.*` | Core cannot contain project namespace | `hermes.core.veritas.runtime` ❌ |
| `hermes.core.ucampus.*` | Core cannot contain project namespace | `hermes.core.ucampus.course` ❌ |
| `adapter.a3.*` | Adapter cannot contain project namespace | `adapter.a3.browser` ❌ |
| `adapter.veritas.*` | Adapter cannot contain project namespace | `adapter.veritas.cli` ❌ |
| `project.*` (without sub-domain) | Project namespace requires sub-domain | `project.a3` ❌ (need `project.a3.workflow`) |
| Duplicate `<id>` namespaces | Each project has one namespace root | `project.a3` and `project.a3-alt` ❌ |

### 3.3 Allowed Namespace Patterns

| Pattern | Description | Example |
|:-----|:-----|:-----|
| `hermes.core.<domain>` | Core operational Skills | `hermes.core.governance` ✅ |
| `hermes.core.<domain>.<sub>` | Deeply nested Core Skills (rare) | `hermes.core.audit.cli` ✅ |
| `adapter.<domain>` | External system bridges | `adapter.browser` ✅ |
| `adapter.<domain>.<sub>` | Sub-domain adapters | `adapter.github.pr` ✅ |
| `project.<id>.<domain>` | Project-specific Skills | `project.a3.workflow` ✅ |
| `project.<id>.<domain>.<sub>` | Deeply nested project Skills | `project.a3.pipeline.content` ✅ |
| `project.<new-id>.*` | Future project namespaces | `project.projectx.ci` ✅ |

### 3.4 Namespace ↔ Dependency Rules

| Dependency | Allowed | Condition |
|:-----|:----:|:-----|
| `hermes.core.*` → `hermes.core.*` | ✅ | Core-to-Core dependency is valid |
| `hermes.core.*` → `adapter.*` | ❌ | Core must not depend on Adapter |
| `hermes.core.*` → `project.*` | ❌ | Core must not depend on Project |
| `adapter.*` → `hermes.core.*` | ✅ | Adapter may use Core infrastructure |
| `adapter.*` → `adapter.*` | ✅ | Adapter-to-Adapter dependency is valid |
| `adapter.*` → `project.*` | ❌ | Adapter must not depend on Project |
| `project.<A>.*` → `hermes.core.*` | ✅ | Project may use Core infrastructure |
| `project.<A>.*` → `adapter.*` | ✅ | Project may use Adapter bridges |
| `project.<A>.*` → `project.<A>.*` | ✅ | Same-project dependency is valid |
| `project.<A>.*` → `project.<B>.*` | ⚠️ | Cross-project dependency requires `dependencies.justification` |

### 3.5 Cross-Project Dependency Declaration

When `project.<A>.*` depends on `project.<B>.*`, the dependency entry must include:

```yaml
dependencies:
  skills:
    - name: project.veritas.core
      version: ">= 1.0"
      cross_project: true              # ← triggers review gate
      justification: >
        A3 workflow uses Veritas StateMachine pattern for agent orchestration.
        This is a deliberate architectural choice, not accidental coupling.
```

Without `cross_project: true` + `justification`, a cross-project dependency is treated as an error at audit time.

---

## 4. Field Summary — 17 Fields (B.0 + C.3.1)

### 4.1 Updated Complete Field Reference

| # | Field | Type | Phase B | Phase A | Source |
|:--|:------|:-----|:------|:------|:-----|
| 1 | `name` | `string` | REQUIRED | REQUIRED | B.0 |
| 2 | `version` | `string` | REQUIRED | REQUIRED | B.0 |
| 3 | `description` | `string` | REQUIRED | REQUIRED | B.0 |
| 4 | `capability` | `string` | REQUIRED | REQUIRED | B.0 |
| 5 | `owner` | `string` | OPTIONAL | REQUIRED | B.0 |
| 6 | `lifecycle` | `string (enum)` | REQUIRED | REQUIRED | B.0 |
| 7 | `dependencies` | `object` | OPTIONAL | REQUIRED | B.0 |
| 8 | `permissions` | `object` | OPTIONAL | REQUIRED | B.0 |
| 9 | `validation` | `object` | OPTIONAL | REQUIRED | B.0 |
| 10 | `compatibility` | `object` | OPTIONAL | REQUIRED | B.0 |
| 11 | `status` | `string` | REQUIRED | REQUIRED | B.0 |
| 12 | `registered` | `string (date)` | REQUIRED | REQUIRED | B.0 |
| 13 | `updated` | `string (date)` | REQUIRED | REQUIRED | B.0 |
| 14 | `path` | `string` | REQUIRED | REQUIRED | B.0 |
| **15** | **`namespace`** | **`string`** | **OPTIONAL** | **REQUIRED** | **C.3.1** |
| **16** | **`scope`** | **`string (enum)`** | **OPTIONAL** | **REQUIRED** | **C.3.1** |
| **17** | **`ownership`** | **`object`** | **OPTIONAL** | **REQUIRED** | **C.3.1** |

### 4.2 Updated Field Maturity Model

| Level | Fields |
|:-----|:-----|
| **REQUIRED** (Phase B) | `name`, `version`, `description`, `capability`, `lifecycle`, `status`, `registered`, `updated`, `path` (9 fields) |
| **OPTIONAL** (Phase B) | `owner`, `permissions`, `compatibility`, `validation`, `dependencies`, `namespace`, `scope`, `ownership` (8 fields) |
| **REQUIRED** (Phase A) | All 17 fields |

### 4.3 Field Dependency Diagram

```
┌──────────────────────────────────────────────────┐
│                 IDENTITY LAYER                    │
│                                                  │
│  name ───────────── "What is this Skill?"        │
│  capability ─────── "What does it do?"            │
│  version ────────── "Which version?"             │
│  description ────── "When to use it?"            │
│                                                  │
├──────────────────────────────────────────────────┤
│               NAMESPACE LAYER (NEW)               │
│                                                  │
│  namespace ──────── "Where in the ecosystem?"    │
│  scope ──────────── "Which architectural layer?" │
│  ownership.tier ─── "What authority level?"      │
│  ownership.owner ── "Who is responsible?"        │
│  ownership.namespace "Which namespace owns it?"  │
│                                                  │
├──────────────────────────────────────────────────┤
│             OPERATIONAL LAYER                    │
│                                                  │
│  owner ──────────── "Who maintains it?"          │
│  lifecycle ──────── "What lifecycle state?"      │
│  status ─────────── "Is it healthy?"             │
│  dependencies ───── "What does it need?"         │
│  permissions ────── "What can it access?"        │
│  validation ─────── "How to verify it?"          │
│  compatibility ──── "Where does it run?"         │
│                                                  │
├──────────────────────────────────────────────────┤
│               BOOKKEEPING LAYER                  │
│                                                  │
│  registered ─────── "When was it created?"       │
│  updated ────────── "When was it last changed?"  │
│  path ───────────── "Where are the files?"       │
│  ownership.promoted_from "Where did it come from?"│
│  ownership.delegated_to "Where did ownership go?"│
│                                                  │
└──────────────────────────────────────────────────┘
```

---

## 5. Policy §9 Mapping Update

### 5.1 Before (B.0 Policy Mapping)

Policy §9.3 defined 12 fields. B.0 added 2 more (`lifecycle`, `status` → separate from lifecycle state). Total: 14 fields.

### 5.2 After (C.3.1 Policy Mapping)

Policy §9.3 now maps to 17 fields:

| Policy §9 Field | B.0 Field | C.3.1 Extension | Notes |
|:-----|:-----|:-----|:-----|
| `name` | `name` (#1) | — | Unchanged |
| `version` | `version` (#2) | — | Unchanged |
| `owner` | `owner` (#5) | `ownership.owner` (#17) | Flat owner retained for Policy §9 compliance; structured ownership added |
| `capability` | `capability` (#4) | — | Unchanged |
| `permissions` | `permissions` (#8) | — | Unchanged |
| `dependencies` | `dependencies` (#7) | — | Extended: cross_project flag added |
| `compatibility` | `compatibility` (#10) | — | Unchanged |
| `status` | `lifecycle` (#6) + `status` (#11) | — | Unchanged |
| `registered` | `registered` (#12) | — | Unchanged |
| `updated` | `updated` (#13) | — | Unchanged |
| `path` | `path` (#14) | — | Unchanged |
| `replaced_by` | (implied by lifecycle) | — | Unchanged |
| *(new)* | — | `namespace` (#15) | New: ecosystem location |
| *(new)* | — | `scope` (#16) | New: architectural boundary |
| *(new)* | — | `ownership` (#17) | New: structured ownership |

### 5.3 Policy §9 Coverage

| Metric | Before (B.0) | After (C.3.1) |
|:-----|:-----|:-----|
| Registry fields | 14 | 17 |
| Policy §9 coverage | 12/14 (86%) | 12/14 existing + 3 new = 15 concepts |
| Namespace concept | ❌ Absent | ✅ Full namespace model |
| Scope concept | ❌ Absent | ✅ Three-scope model |
| Structured ownership | ❌ Flat string only | ✅ Tiered + promotion history |

---

## 6. Compatibility Strategy

### 6.1 Backward Compatibility Principle

```
All existing Skills remain valid.
No existing Registry entry is invalidated.
No existing Skill loading breaks.
```

The 3 new fields are **additive only**. They provide additional metadata that was previously absent. No existing data needs to be deleted or modified.

### 6.2 Phase B Compatibility (Current State)

```
Field: namespace    → OPTIONAL, null allowed
Field: scope        → OPTIONAL, null allowed
Field: ownership    → OPTIONAL, null allowed

All 146 existing Skills: no namespace, no scope, no ownership.
→ Registry accepts them (Phase B)
→ Skill Manager loads them (unchanged behavior)
→ Audit CLI reports them as "namespace: UNDEFINED"
```

### 6.3 Phase A Compatibility (Target State)

```
Field: namespace    → REQUIRED for new registrations
Field: scope        → REQUIRED for new registrations
Field: ownership    → REQUIRED for new registrations

Existing Skills migrated via Wave 3 (Metadata Completion):
  → namespace backfilled from audit data
  → scope derived from namespace prefix
  → ownership.tier derived from scope
  → ownership.owner derived from existing owner field
```

### 6.4 Skill Name Compatibility During Migration

During Wave 2 namespace isolation, some Skill names will change. The `namespace` field preserves identity continuity:

```
Before migration:
  name:  a3-runtime-infrastructure
  namespace:  null
  scope:      null

After migration:
  name:        runtime-infrastructure          ← shortened (project prefix moved to namespace)
  namespace:   project.a3.infrastructure       ← NEW — ecosystem location
  scope:       project                         ← NEW — architectural boundary
  replaced_by: (deprecated entry) a3-runtime-infrastructure → project.a3.infrastructure/runtime-infrastructure
```

**Identity continuity rule:**

```
Old identity:  a3-runtime-infrastructure          (flat name)
New identity:  project.a3.infrastructure/runtime-infrastructure  (namespace + name)

The old name is preserved as a DEPRECATED alias with replaced_by pointing
to the new namespace + name compound identity.

Any query for "a3-runtime-infrastructure" → resolved to "project.a3.infrastructure/runtime-infrastructure"
```

### 6.5 Registry File Format Compatibility

```
Before (B.0):
  skill-registry.json → 14 fields per entry

After (C.3.1):
  skill-registry.json → 17 fields per entry (3 new, all optional in Phase B)
  → Same format, extended fields
  → JSON parser ignores unknown fields (forward-compatible)
  → Old parsers reading new registry: ignore namespace/scope/ownership (safe)
  → New parsers reading old registry: treat missing fields as null (safe)
```

### 6.6 Audit CLI Compatibility

The existing audit CLI (`hermes skill audit`) gains three new report sections but existing checks remain unchanged:

```
New sections:
  hermes skill audit namespace     ← Reports namespace violations (R1-R8)
  hermes skill audit scope          ← Reports scope mismatches
  hermes skill audit ownership      ← Reports ownership inconsistencies

Existing sections (unchanged):
  hermes skill audit all            ← Now includes namespace/scope/ownership in report
  hermes skill audit registry       ← Extended to check 17 fields instead of 14
  hermes skill audit deps           ← Extended to check cross-project dependency rules
```

---

## 7. Complete Registry Entry Examples

### 7.1 Core Skill Example

```yaml
skills:
  - name: agent-governance-protocol
    namespace: hermes.core.governance          # NEW
    scope: core                                # NEW
    ownership:                                 # NEW
      tier: 0
      owner: hermes-governance
      namespace: hermes.core
      promoted_from: null
      delegated_to: null
    version: 1.0.0
    description: "Use when Hermes needs to execute under governance rules. Defines Phase 0/1/2 workflow, change classification, and stop conditions."
    capability: governance-execution
    owner: hermes-governance
    lifecycle: active
    status: ok
    dependencies:
      skills: []                               # Core depends only on Core
      runtime: []
    permissions:
      allow:
        - filesystem.read
        - memory.read
      deny:
        - secret.read
    compatibility:
      platforms: [linux]
      providers: [openai, anthropic, deepseek]
    registered: "2026-06-01"
    updated: "2026-07-18"
    path: skills/hermes-core/governance/
```

### 7.2 Adapter Skill Example

```yaml
skills:
  - name: browser-automation
    namespace: adapter.browser.automation      # NEW
    scope: adapter                              # NEW
    ownership:                                 # NEW
      tier: 1
      owner: hermes-platform
      namespace: adapter
      promoted_from: null
      delegated_to: null
    version: 2.1.0
    description: "Use when performing browser automation tasks. Provides a 4-layer framework."
    capability: browser-automation
    owner: hermes-platform
    lifecycle: active
    status: ok
    dependencies:
      skills:
        - hermes.core.registry                 # Adapter → Core dependency (allowed)
      runtime:
        - python >= 3.11
        - playwright >= 1.40
    permissions:
      allow:
        - filesystem.read
        - network.external_api
    compatibility:
      platforms: [linux, macos]
      providers: [openai, anthropic, deepseek]
    registered: "2026-06-01"
    updated: "2026-07-18"
    path: skills/adapter/browser/
```

### 7.3 Project Skill Example

```yaml
skills:
  - name: multi-agent-pipeline
    namespace: project.a3.workflow             # NEW
    scope: project                              # NEW
    ownership:                                 # NEW
      tier: 2
      owner: a3-team
      namespace: project.a3
      promoted_from: null
      delegated_to: null
    version: 3.6.0
    description: "A3 multi-agent personalized teaching system — 12 Agents + Workflow Orchestrator."
    capability: multi-agent-orchestration
    owner: a3-team
    lifecycle: active
    status: ok
    dependencies:
      skills:
        - hermes.core.registry                 # Project → Core (allowed)
        - adapter.browser.automation           # Project → Adapter (allowed)
        - name: project.a3.infrastructure      # Same-project dependency
      runtime: []
    permissions:
      allow:
        - filesystem.read
        - network.external_api
    compatibility:
      platforms: [linux]
    registered: "2026-07-18"
    updated: "2026-07-18"
    path: skills/project/a3/workflow/
```

### 7.4 Cross-Project Dependency Example

```yaml
skills:
  - name: a3-workflow
    namespace: project.a3.workflow
    scope: project
    ownership:
      tier: 2
      owner: a3-team
      namespace: project.a3
    version: 3.6.0
    dependencies:
      skills:
        - hermes.core.registry
        - adapter.browser.automation
        - name: project.veritas.core            # ← Cross-project dependency
          version: ">= 2.0"
          cross_project: true                   # ← EXPLICIT declaration
          justification: >
            A3 workflow uses Veritas StateMachine pattern for agent
            orchestration. This is architectural, not accidental.
    # ... rest of fields
```

---

## 8. Verification

### 8.1 Architecture Boundary Verification

| Claim | Verification Mechanism | Status |
|:-----|:-----|:----:|
| **Hermes ≠ Project** | `namespace` field: `hermes.core.*` ≠ `project.*` — enforced at registration | ✅ Design constraint |
| **Project Skill 不污染 Core** | Dependency rule: `hermes.core.*` → `project.*` is REJECTED | ✅ Design constraint |
| **Project Skill 不污染 Adapter** | Dependency rule: `adapter.*` → `project.*` is REJECTED | ✅ Design constraint |
| **多项目扩展能力** | `project.<new-id>.*` can be registered at any time without Core changes | ✅ Design constraint |
| **Namespace immutability** | Scope cannot change after `active`; namespace cannot change after `active` | ✅ Design constraint |
| **Cross-project safety** | Cross-project dependencies require explicit `cross_project: true` + justification | ✅ Design constraint |
| **Backward compatible** | Phase B: all 3 new fields OPTIONAL; old Registry entries still valid | ✅ Compatibility guarantee |

### 8.2 Document Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-registry-namespace-schema-amendment.md` |
| No executable code | ✅ Pure documentation |
| No Registry modification | ✅ Design only |
| No Skill modification | ✅ 0 SKILL.md changes |
| No file movement | ✅ |
| Consistent with B.0 | ✅ Same field definition format; 14 existing fields unchanged |
| Consistent with C.3 | ✅ Three-layer model preserved; namespace rules match C.3 §2-4 |
| Consistent with Policy §9 | ✅ All Policy §9 fields accounted; 3 new fields as extensions |

---

## 9. Next Gate Decision

### 9.1 Phase C.3.1 Status

```
✅ COMPLETE — Read-Only Schema Amendment Document

Created File: docs/hermes-registry-namespace-schema-amendment.md

Contents:
  §1 Amendment Objective               ← Why this exists, relationship to B.0
  §2 New Field Definitions             ← namespace, scope, ownership (full spec)
  §3 Namespace Rules                   ← 8 validation rules, prohibited/allowed patterns
  §4 Field Summary — 17 Fields         ← Updated complete reference table
  §5 Policy §9 Mapping Update          ← From 14 to 17 fields
  §6 Compatibility Strategy            ← Phase B → Phase A migration path
  §7 Complete Registry Entry Examples  ← Core, Adapter, Project, Cross-project
  §8 Verification                      ← Architecture boundaries confirmed
  §9 Next Gate Decision                ← This section

Verification:
  ✅ 17 field specifications (14 existing + 3 new)
  ✅ 8 namespace validation rules (R1-R8)
  ✅ 10 dependency rules (4 allowed, 3 prohibited, 3 conditional)
  ✅ 3 complete Registry entry examples
  ✅ Phase B backward compatibility preserved
  ✅ No executable code
  ✅ No Registry/Skill modification
```

### 9.2 Governance Decision Required

```
Phase C.3.1 → NEXT GATE

Decision:
  [ ] Approve namespace, scope, ownership fields as Registry Schema extensions
  [ ] Approve namespace validation rules (R1-R8)
  [ ] Approve dependency enforcement rules
  [ ] Approve cross-project dependency declaration model
  [ ] Approve Phase B (OPTIONAL) → Phase A (REQUIRED) migration path

If approved:
  → B.0 Registry Schema is now v1.1 (17 fields)
  → Namespace model is formally encoded in schema
  → Phase A migrations have a complete field contract
  → Ready for Phase C.4 (Updated Execution Review)

If rejected:
  → B.0 remains at v1.0 (14 fields)
  → Namespace model remains at C.3 design level only
  → Migration Wave 2 cannot proceed with namespace isolation
```

### 9.3 Updated Governance Document Stack

```
Completed (Read-Only Design):
  B.0 hermes-skill-registry-schema.md                     ← 14 fields (FROZEN)
  B.1 hermes-skill-audit-cli.md                           ← Audit CLI design
  B.2 hermes-auditor-agent-design.md                      ← Auditor agent design
  B.3 hermes-skill-migration-specification.md             ← Migration spec (⚠️ Wave 2 needs revision)
  B.4 hermes-skill-validation-specification.md            ← Validation spec
  C.0 hermes-skill-migration-execution-review.md           ← Execution review
  C.1 hermes-skill-migration-approval-checklist.md         ← Approval checklist
  C.2 hermes-wave0-dry-run-specification.md               ← Dry run spec
  C.3 hermes-project-namespace-boundary-review.md          ← Namespace model
  C.3.1 hermes-registry-namespace-schema-amendment.md     ← Schema amendment ✨ NEW

FROZEN (Committed):
  hermes-skill-policy.md v1.0                             ← Tier 1 Governance
  TA-0-architecture-audit.md                              ← Historical
  universal-agent-framework-rfc.md                        ← Abstract framework

Next:
  → Revise B.3 §5 (Wave 2 namespace isolation)
  → Revise B.0 (absorb C.3.1 amendments into schema doc)
  → Phase C.4 (Updated Migration Execution Review)
```

---

> **Phase:** C.3.1 — Registry Namespace Schema Amendment
> **Status:** Complete — Ready for Governance Review
> **Registry Schema:** v1.0 (14 fields) → v1.1 (17 fields) after approval
> **Next Gate:** Human Review → Revise B.3 Wave 2 → Revise B.0 Schema → Phase C.4
