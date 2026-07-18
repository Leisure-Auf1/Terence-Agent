# Hermes Project Namespace Boundary Review

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** C.3 — Project Namespace Boundary Review
**Audience:** Governance Reviewer (Human)
**Purpose:** Define the namespace, ownership, and scope model that separates Hermes Core from its consuming projects

**Dependencies (completed):**
- Hermes Skill Governance Policy v1.0
- Hermes Skill Registry Schema v1.0 (Phase B.0)
- Hermes Skill Migration Specification v1.0 (Phase B.3)
- Hermes Wave 0 Dry Run Specification v1.0 (Phase C.2)

**This document is:**
- A response to the architecture correction: Hermes is a **general Agent Framework**, NOT a system bound to any single project
- A definition of namespace boundaries between Hermes Core and consuming projects
- A revision to Wave 2 migration strategy: from "project name removal" to "namespace isolation"
- An extension proposal for the Registry Schema: `namespace`, `ownership`, `scope`

**This document does NOT:**
- Execute migration
- Modify any Skill
- Modify any Registry
- Move files

---

## Executive Summary

The user identified a critical architecture flaw in the current governance documents: they implicitly treat Hermes as an A3 / Veritas-Core / UCampus system rather than a **general-purpose Agent Framework** that supports those projects as validation targets.

**Current flawed assumption (implicit in B.3 §5 Wave 2):**
```
"Rename project-specific Skills to capability-descriptive names"
→ veritas-core → agent-runtime-development
→ a3-runtime-infrastructure → agent-runtime-infrastructure
→ a3-content-pipeline → content-generation-pipeline
```

**Corrected architecture:**
```
Hermes = general Agent Framework
├── Supports A3 as a consuming project
├── Supports Veritas-Core as a consuming project
├── Supports UCampus as a consuming project
└── Supports future projects
```

This document defines the **namespace boundary model** that:
1. Preserves project-specific Skills in their own namespaces
2. Separates Core capabilities from Project capabilities
3. Introduces Adapter layer for cross-cutting external integrations
4. Revises Wave 2 to "namespace isolation" instead of "project name removal"

---

## 1. Architecture Correction

### 1.1 Before (Flawed)

```
Hermes Skills (flat)
├── veritas-core          ← project-coupled (Class E)
├── a3-runtime-*          ← project-coupled (Class E)
├── a3-content-*          ← project-coupled (Class E)
├── browser-automation    ← generic capability
├── github-*              ← generic capability
└── ...
```

**Problem:** The migration plan's Wave 2 proposes to remove project identifiers entirely — renaming `veritas-core` to `agent-runtime-development`, `a3-runtime-infrastructure` to `agent-runtime-infrastructure`. This **erases project ownership** and implicitly declares that project-specific Skills are "bad."

**This is wrong because:**
- A3-specific workflow knowledge IS valid and valuable — it just belongs in a project namespace
- Veritas-Core development patterns ARE specific to that codebase — genericizing them loses context
- Removing project identifiers makes it impossible to know which Skills serve which projects
- Future projects (Project X, Project Y) will need their own Skills — and they need a namespace to put them in

### 1.2 After (Corrected)

```
Hermes Core Layer
├── hermes.core.governance          ← agent-governance-protocol
├── hermes.core.registry            ← skill-manager
├── hermes.core.auditor             ← auditor-agent
├── hermes.core.preflight           ← harness-preflight
├── hermes.core.constraints         ← architecture-constraints
├── hermes.core.logger              ← agent-logger
├── hermes.core.guidance            ← guidance-agent
└── hermes.core.tracker             ← task-progress

Adapter Layer
├── adapter.browser                 ← browser-automation (4-layer)
├── adapter.github                  ← github-* (PR, issues, auth)
├── adapter.computer-use            ← computer-use-mcp / desktop
├── adapter.cli                     ← cli-anything / cli-hub
├── adapter.email                   ← himalaya
├── adapter.mcp                     ← native-mcp
├── adapter.media                   ← youtube, spotify, gif
└── ...

Project Layer
├── project.a3.workflow             ← a3-multi-agent-pipeline
├── project.a3.infrastructure       ← a3-runtime-infrastructure
├── project.a3.pipeline             ← a3-content-pipeline
├── project.a3.team                 ← a3-agent-team-pipeline
├── project.veritas.core            ← veritas-core
├── project.veritas.development     ← (future)
├── project.ucampus.automation      ← ucampus-*
├── project.ucampus.course          ← u-campus-course-automation
└── project.<future>.*              ← extensible
```

### 1.3 Key Principle

```
Hermes ≠ A3
Hermes ≠ Veritas
Hermes ≠ UCampus

Hermes supports A3
Hermes supports Veritas
Hermes supports future projects
```

**Decision:** Skills that encapsulate project-specific knowledge (A3 workflow orchestration, Veritas runtime patterns, UCampus course automation) are **not bugs to be fixed by renaming**. They are **valid project-layer Skills** that must be namespace-isolated from Core Skills.

---

## 2. Namespace Model

### 2.1 Three-Layer Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    Hermes Skill Namespace                    │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Core Layer (hermes.core.*)              │    │
│  │                                                     │    │
│  │  Definition: Skills that define Hermes' own         │    │
│  │  operational behavior — governance, registry,       │    │
│  │  workflow, constraints, orchestration.              │    │
│  │                                                     │    │
│  │  Dependency Rule: Core Skills depend ONLY on        │    │
│  │  other Core Skills. They NEVER depend on Adapter    │    │
│  │  or Project Skills.                                 │    │
│  │                                                     │    │
│  │  Lifecycle: Hermes-wide. Deprecation requires       │    │
│  │  Governance Review + all-Project impact assessment. │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Adapter Layer (adapter.*)                 │    │
│  │                                                     │    │
│  │  Definition: Skills that bridge Hermes to external  │    │
│  │  systems — browsers, GitHub, desktop, CLI tools,    │    │
│  │  email, media, MCP servers.                         │    │
│  │                                                     │    │
│  │  Dependency Rule: Adapter Skills MAY depend on      │    │
│  │  Core Skills but NEVER on Project Skills.           │    │
│  │                                                     │    │
│  │  Lifecycle: Hermes-wide. Any Project can use any    │    │
│  │  Adapter. Deprecation requires impact assessment    │    │
│  │  across all consuming Projects.                     │    │
│  └─────────────────────────────────────────────────────┘    │
│                            │                                │
│                            ▼                                │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Project Layer (project.<id>.*)            │    │
│  │                                                     │    │
│  │  Definition: Skills owned by a specific consuming   │    │
│  │  project — workflow orchestration, project-specific │    │
│  │  patterns, project infrastructure.                  │    │
│  │                                                     │    │
│  │  Dependency Rule: Project Skills MAY depend on      │    │
│  │  Core and Adapter Skills. They MUST NOT depend on   │    │
│  │  other Projects' Skills without explicit cross-     │    │
│  │  project dependency declaration.                    │    │
│  │                                                     │    │
│  │  Lifecycle: Project-scoped. Project owner controls  │    │
│  │  deprecation. Core team reviews for safety only.    │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Namespace Format

```
Namespace format: <layer>.<domain>.<capability>

Where:
  layer     ∈ {hermes.core, adapter, project}
  domain    ∈ {governance, registry, audit, browser, github, a3, veritas, ucampus, ...}
  capability ∈ {specific skill identifier, unique within domain}

Examples:
  hermes.core.governance          ← Governance Protocol
  hermes.core.registry            ← Skill Manager / Registry
  adapter.browser.automation      ← Browser automation framework
  adapter.github.pr               ← GitHub PR workflow
  project.a3.workflow             ← A3 multi-agent workflow
  project.veritas.core            ← Veritas-Core development
  project.ucampus.automation      ← UCampus course automation
```

### 2.3 Namespace Transition Map

| Current Skill Name | Current Classification | Target Namespace | Layer |
|:-----|:-----|:-----|:-----|
| `agent-governance-protocol` | Class C — Governance Risk | `hermes.core.governance` | Core |
| `architecture-constraints` | Class C — Governance Risk | `hermes.core.constraints` | Core |
| `guidance-agent` | Class C — Governance Risk | `hermes.core.guidance` | Core |
| `error-registry` | Class C — Governance Risk | `hermes.core.errors` | Core |
| `skill-manager` | Class C — Governance Risk | `hermes.core.registry` | Core |
| `harness-preflight` | Class C — Governance Risk | `hermes.core.preflight` | Core |
| `task-progress` | Class C — Governance Risk | `hermes.core.tracker` | Core |
| `agent-logger` | Class C — Governance Risk | `hermes.core.logger` | Core |
| `browser-automation` | Class A — Compliant | `adapter.browser.automation` | Adapter |
| `github-pr-workflow` | Class A — Compliant | `adapter.github.pr` | Adapter |
| `computer-use-mcp` | Class A — Compliant | `adapter.computer` | Adapter |
| `a3-multi-agent-pipeline` | Class E — Project Coupled | `project.a3.workflow` | Project |
| `a3-runtime-infrastructure` | Class E — Project Coupled | `project.a3.infrastructure` | Project |
| `a3-content-pipeline` | Class E — Project Coupled | `project.a3.pipeline` | Project |
| `veritas-core` | Class E — Project Coupled | `project.veritas.core` | Project |
| `ucampus-auto-complete` | Class E — Project Coupled | `project.ucampus.automation` | Project |

---

## 3. Ownership Model

### 3.1 Ownership Tiers

| Tier | Layer | Owner | Authority |
|:-----|:-----|:-----|:-----|
| **Tier 0** | Core | `hermes-governance` | Hermes Governance Team. All changes require Governance Review (Type D). |
| **Tier 1** | Adapter | `hermes-platform` | Hermes Platform Team. Changes reviewed for cross-Project compatibility. |
| **Tier 2** | Project | `<project>-team` | Project team. Project owner controls deprecation. Core team reviews for safety boundary only. |

### 3.2 Ownership Rules

| Rule | Description | Enforcement |
|:-----|:-----|:-----|
| **Single Owner** | Each Skill has exactly one owner. No shared ownership. | Registry rejects duplicate `owner` claims. |
| **Core Immunity** | Core Skills cannot be forked, duplicated, or overridden by Adapter or Project Skills. | Loading system enforces: `hermes.core.*` only from core source. |
| **Adapter Neutrality** | Adapter Skills must not favor any specific Project. An Adapter that hardcodes Project paths is a Class E violation. | Audit CLI checks: Adapter body must contain 0 project-specific paths. |
| **Project Isolation** | Project A's Skills must not modify Project B's Skills or their behavior. Cross-project interaction is through declared dependencies only. | Registry enforces: `project.a3.*` cannot depend on `project.veritas.*` without explicit declaration. |
| **Ownership Transfer** | A Project Skill may be promoted to Adapter if proven reusable across ≥2 Projects. Requires Governance Review. | Adapter Skill promotion goes through full REVIEW → ACCEPT gate. |

### 3.3 Ownership in Registry

```yaml
# Registry extension: ownership field
ownership:
  tier: 2                    # 0=Core, 1=Adapter, 2=Project
  owner: a3-team             # responsible team/individual
  namespace: project.a3      # owning namespace
  promoted_from: null        # if promoted from Project→Adapter, original namespace
  delegated_to: null         # if ownership transferred
```

---

## 4. Skill Scope Classification

### 4.1 Three Scopes

| Scope | Namespace Pattern | Description | Examples |
|:-----|:-----|:-----|:-----|
| **Core Skill** | `hermes.core.*` | Defines Hermes' own operational behavior. Loaded into every session. Governed by Governance Protocol. | Governance, Registry, Workflow, Constraints, Preflight |
| **Adapter Skill** | `adapter.*` | Bridges Hermes to external systems. Available to all Projects. Neutral — contains no project-specific logic. | Browser, GitHub, Desktop, CLI, Email, MCP |
| **Project Skill** | `project.<id>.*` | Owned by a specific consuming project. Contains project-specific workflows, patterns, and infrastructure. | A3 pipeline, Veritas dev, UCampus automation |

### 4.2 Scope Decision Matrix

When creating a new Skill, determine its scope by answering:

```
Q1: Does this Skill define how Hermes itself operates (not what it does for a project)?
    YES → Core Skill (hermes.core.*)
    NO  → Continue to Q2

Q2: Does this Skill bridge Hermes to an external system or tool that any project might need?
    YES → Adapter Skill (adapter.*)
    NO  → Continue to Q3

Q3: Is this Skill specific to one consuming project's workflows, patterns, or infrastructure?
    YES → Project Skill (project.<id>.*)
    NO  → Re-evaluate — a Skill without clear scope should not be created
```

### 4.3 Scope Violations

| Violation | Example | Fix |
|:-----|:-----|:-----|
| **Core containing Project logic** | `hermes.core.governance` references A3 pipeline steps | Extract A3 logic → `project.a3.governance`; keep generic governance in Core |
| **Adapter containing Project paths** | `adapter.browser` hardcodes `~/A3-Multi-Agent-System/` paths | Remove project paths; make configurable |
| **Project masquerading as Core** | Skill named `agent-runtime` but contains only Veritas-Core patterns | Rename to `project.veritas.runtime` |
| **Cross-project hidden dependency** | `project.a3.workflow` silently depends on `project.veritas.core` without declaration | Add `dependencies.skills: [project.veritas.core]` with justification |

---

## 5. Wave 2 Revision: From "Project Name Removal" to "Namespace Isolation"

### 5.1 Current Wave 2 (Flawed — B.3 §5)

The existing migration specification's Wave 2 proposes:

```
Objective: Rename 6 Class E Skills from project-specific names to
capability-descriptive names. Remove hardcoded project paths from
Skill bodies. Convert project-specific Skills into reusable capability Skills.
```

| # | Old ID | New ID (CURRENT) | Problem |
|:--|:-------|:-------|:-----|
| 1 | `veritas-core` | `agent-runtime-development` | Erases Veritas ownership; every runtime project would need a "veritas" adapter anyway |
| 2 | `a3-runtime-infrastructure` | `agent-runtime-infrastructure` | Generic name loses A3 context; what if another project has runtime infra? |
| 3 | `a3-content-pipeline` | `content-generation-pipeline` | Loses A3-specific pipeline knowledge |
| 4 | `a3-multi-agent-pipeline` | (merged) | Merging project-specific orchestration into generic loses A3 workflow |
| 5 | `a3-agent-team-pipeline` | (merged) | Same as above |
| 6 | `a3-multi-agent-content-pipeline` | (merged) | Same as above |

**Root cause of this flaw:** The migration spec treated "project coupling" as a defect to be eliminated rather than a legitimate architectural layer to be isolated.

### 5.2 Revised Wave 2 — Namespace Isolation

```
Objective: Move 21 Class E Skills into their correct Project namespaces.
Preserve all project-specific knowledge. Isolate project boundaries so
that Project Skills cannot leak into Core or Adapter layers.

This is NOT "remove project names."
This is "put project names where they belong — in the Project Layer."
```

| # | Current Name | Target Namespace | Action | Rationale |
|:--|:-----|:-----|:-----|:-----|
| 1 | `veritas-core` | `project.veritas.core` | Relocate | Veritas-Core development patterns belong in Veritas namespace |
| 2 | `a3-runtime-infrastructure` | `project.a3.infrastructure` | Relocate | A3 runtime infra is A3-specific |
| 3 | `a3-content-pipeline` | `project.a3.pipeline` | Relocate | A3 content pipeline is A3-specific |
| 4 | `a3-multi-agent-pipeline` | `project.a3.workflow` | Relocate + consolidate | A3 agent orchestration; consolidate duplicates within namespace |
| 5 | `a3-agent-team-pipeline` | `project.a3.workflow` | Merge into `project.a3.workflow` | Duplicate within A3 namespace |
| 6 | `a3-multi-agent-content-pipeline` | `project.a3.workflow` | Merge into `project.a3.workflow` | Duplicate within A3 namespace |
| 7 | `ucampus-auto-complete` | `project.ucampus.automation` | Relocate | UCampus automation is UCampus-specific |
| 8 | `u-campus-course-automation` | `project.ucampus.course` | Relocate | UCampus course handling |
| 9 | `chaoxing-homework` | `project.ucampus.chaoxing` | Relocate | 超星 is a UCampus sub-component |
| 10 | `lab-report-execution` | `project.ucampus.lab` | Relocate | Lab reports are university-specific |
| 11-21 | Remaining Class E Skills | `project.<id>.<domain>` | Relocate | Each to its owning project namespace |

### 5.3 What Changes (Namespace Isolation)

| Aspect | Before (B.3 Wave 2) | After (C.3 Revised) |
|:-----|:-----|:-----|
| **Action** | Rename to generic capability names | Relocate into project namespaces |
| **Project identity** | Erased ("project coupling is bad") | Preserved in namespace prefix |
| **Duplicates** | Merged across projects into generic Skills | Merged only within same project namespace |
| **Portability** | Forced genericization (loses context) | Namespace-isolated (context preserved, boundary clear) |
| **Extensibility** | Every new project must genericize its Skills | New project gets its own `project.<id>.*` namespace |
| **Discovery** | All Skills compete in flat namespace | Layer-prefixed: `hermes.core.*`, `adapter.*`, `project.*` |

### 5.4 Wave 2 Safety Guarantees (Unchanged)

| Guarantee | Mechanism |
|:-----|:-----|
| **Old names preserved** | All old names → DEPRECATED with `replaced_by: project.<id>.<name>` |
| **No content deletion** | Project-specific knowledge preserved; only path hardcoding removed |
| **History retained** | Deprecated Registry entries provide rename audit trail |
| **Reference migration** | `hermes skill audit deps` verifies 0 broken references post-relocation |

### 5.5 Body-Level Cleanup (Revised)

For all relocated Skills, project-specific hardcoded paths in Skill bodies are replaced with namespace-relative references — but project identity is preserved:

| Before (Remove) | After (Namespace-Relative) |
|:-----|:-----|
| `~/Terence-Agent/` | `{core-root}/` (for Core Skills) or `{project-root}/` (for Project Skills) |
| `~/A3-Multi-Agent-System/` | `{project.a3-root}/` |
| `~/Veritas-Core/` | `{project.veritas-root}/` |
| Any absolute `/home/` path | `{absolute-path-removed}` |
| Hardcoded `a3-*` references in Adapter Skills | Removed (Adapter must be neutral) |
| Hardcoded `a3-*` references in `project.a3.*` Skills | Preserved (this IS A3's namespace) |

---

## 6. Registry Schema Extension Proposals

### 6.1 New Fields

The current Registry Schema (B.0) defines 14 fields. Three new fields are proposed to support namespace isolation:

| # | Field | Type | Maturity | Description |
|:--|:-----|:-----|:-----|:-----|
| 15 | `namespace` | `string` | REQUIRED (Phase A) | Fully qualified namespace: `hermes.core.governance`, `adapter.browser`, `project.a3.workflow` |
| 16 | `ownership` | `object` | REQUIRED (Phase A) | Ownership metadata: `{tier, owner, namespace, promoted_from, delegated_to}` |
| 17 | `scope` | `string (enum)` | REQUIRED (Phase A) | `core`, `adapter`, or `project` |

### 6.2 Namespace Field Specification

```yaml
namespace:
  type: string
  pattern: "^((hermes\\.core)|(adapter)|(project\\.[a-z0-9-]+))\\.[a-z0-9-]+(\\.[a-z0-9-]+)*$"
  required: true                    # Phase A
  description: >
    Fully qualified namespace identifier following the three-layer model.
    - Core:   hermes.core.<domain>
    - Adapter: adapter.<domain>
    - Project: project.<id>.<domain>
  examples:
    - hermes.core.governance
    - adapter.browser.automation
    - project.a3.workflow
    - project.veritas.core
    - project.ucampus.automation
  validation:
    - "Must match layer prefix (hermes.core | adapter | project.<id>)"
    - "Must have at least one sub-domain after the layer prefix"
    - "Must be unique across all Skills"
```

### 6.3 Ownership Field Specification

```yaml
ownership:
  type: object
  required: true                    # Phase A
  properties:
    tier:
      type: integer
      enum: [0, 1, 2]
      description: "0=Core, 1=Adapter, 2=Project"
    owner:
      type: string
      description: "Responsible team or individual identifier"
    namespace:
      type: string
      description: "Owning namespace (must match skill's namespace prefix)"
    promoted_from:
      type: string | null
      description: "If promoted from Project→Adapter, the original namespace"
    delegated_to:
      type: string | null
      description: "If ownership has been transferred, the new owner"
  validation:
    - "tier 0 requires owner='hermes-governance'"
    - "tier 1 requires owner='hermes-platform'"
    - "tier 2 allows project-specific owner"
    - "promoted_from required when tier=1 and previously tier=2"
```

### 6.4 Scope Field Specification

```yaml
scope:
  type: string
  enum: [core, adapter, project]
  required: true                    # Phase A
  description: >
    The architectural scope of the Skill within the three-layer model.
    - core:    Defines Hermes' own operational behavior
    - adapter: Bridges Hermes to external systems
    - project: Owned by a specific consuming project
  validation:
    - "Must match namespace prefix: core ↔ hermes.core.*, adapter ↔ adapter.*, project ↔ project.*"
    - "Scope is immutable after initial registration (changing scope requires full REVIEW→ACCEPT)"
```

### 6.5 Updated Registry Schema Maturity Model

| Field | Current Maturity | Proposed Maturity |
|:-----|:-----|:-----|
| Existing 14 fields | As per B.0 Schema §3.4 | Unchanged |
| `namespace` (new) | UNDEFINED | REQUIRED (Phase A) |
| `ownership` (new) | UNDEFINED | REQUIRED (Phase A) |
| `scope` (new) | UNDEFINED | REQUIRED (Phase A) |

### 6.6 Migration Path for New Fields

```
Phase B (current):   Schema defined, fields UNDEFINED
Phase A (target):    Fields REQUIRED for new registrations
Migration Wave:      Wave 3 (Metadata Completion) — backfill namespace, ownership, scope for all existing Skills
```

### 6.7 Updated Registry Entry Example

```yaml
# Fully qualified Registry entry with namespace model
skills:
  - name: a3-multi-agent-pipeline
    version: 3.6.0
    description: "A3 multi-agent personalized teaching system — 12 Agents + Workflow Orchestrator"
    capability: multi-agent-orchestration
    namespace: project.a3.workflow          # ← NEW
    scope: project                           # ← NEW
    ownership:                               # ← NEW
      tier: 2
      owner: a3-team
      namespace: project.a3
    owner: a3-team
    lifecycle: active
    status: ok
    permissions:
      allow:
        - filesystem.read
        - network.external_api
    dependencies:
      skills:
        - hermes.core.registry              # Core dependency
        - adapter.browser.automation        # Adapter dependency
        - project.a3.infrastructure         # Same-project dependency
      runtime: []
    compatibility:
      platforms: [linux]
    registered: 2026-07-18
    updated: 2026-07-18
    path: skills/project/a3/workflow/
```

---

## 7. Architecture Boundary Verification

### 7.1 Hermes ≠ Project Boundary

| Claim | Verification | Status |
|:-----|:-----|:----:|
| Hermes Core does not import A3 code | Core Skills contain 0 references to `a3-*`, `~/A3-Multi-Agent-System/` | ✅ Design constraint |
| Hermes Core does not import Veritas code | Core Skills contain 0 references to `veritas-*`, `~/Veritas-Core/` | ✅ Design constraint |
| Hermes Core does not import UCampus code | Core Skills contain 0 references to `ucampus-*` | ✅ Design constraint |
| Hermes Core works without any Project | Core Skills have no project Skill dependencies | ✅ Design constraint |
| Project Skills can depend on Core | `project.a3.*` → `hermes.core.*` dependency is valid | ✅ Allowed |
| Project Skills cannot modify Core | Project Skill body contains no Core file path writes | ✅ Audit enforcement |

### 7.2 "Supports" Boundary

| Hermes supports A3 by... | Mechanism |
|:-----|:-----|
| Providing Core orchestration | `hermes.core.registry`, `hermes.core.guidance` available to A3 workflows |
| Providing Adapter bridges | `adapter.browser`, `adapter.github`, `adapter.cli` available to A3 |
| Providing Project namespace | `project.a3.*` reserved for A3-specific Skills |
| NOT by... | |
| Hardcoding A3 paths in Core | ❌ Prohibited |
| Requiring A3 Skills to boot | ❌ Prohibited |
| Merging A3 logic into Core | ❌ Prohibited |

### 7.3 Cross-Project Dependency Rules

```
Allowed:
  project.a3.workflow → hermes.core.registry       ✅ Project depends on Core
  project.a3.workflow → adapter.browser             ✅ Project depends on Adapter
  project.a3.workflow → project.a3.infrastructure   ✅ Same-project dependency

Allowed with declaration:
  project.a3.workflow → project.veritas.core         ⚠️ Cross-project dependency — must declare in dependencies with justification

Prohibited:
  hermes.core.governance → project.a3.workflow      ❌ Core must not depend on Project
  adapter.browser → project.a3.infrastructure        ❌ Adapter must not depend on Project
  project.a3.* → project.veritas.* (undeclared)      ❌ Implicit cross-project dependency
```

### 7.4 Boundary Enforcement

| Enforcement Point | Mechanism |
|:-----|:-----|
| **Skill Creation** | Scope Decision Matrix (§4.2) must be answered before registration |
| **Dependency Declaration** | Registry rejects `hermes.core.*` depending on `project.*` |
| **Audit CLI** | `hermes skill audit scope` flags misclassified Skills |
| **Body Content** | Adapter Skill body must contain 0 project-specific paths |
| **Cross-Project** | Undeclared cross-project dependency triggers Warning (not Block) at audit, but Block at runtime loading |

---

## 8. Impact on Existing Governance Documents

### 8.1 Documents Requiring Revision

| Document | Phase | Section | Impact |
|:-----|:-----|:-----|:-----|
| `hermes-skill-migration-specification.md` | B.3 | §5 Wave 2 | **HIGH** — Revise from "project name removal" to "namespace isolation" |
| `hermes-skill-registry-schema.md` | B.0 | §2 Schema Fields | **MEDIUM** — Add `namespace`, `ownership`, `scope` fields |
| `hermes-wave0-dry-run-specification.md` | C.2 | §2 Target Matrix | **MEDIUM** — Wave 0 (Core relocation) unchanged; Wave 2 references become "namespace isolation" |
| `hermes-skill-validation-specification.md` | B.4 | Class E validation | **LOW** — Add scope-based validation rules |
| `hermes-skill-migration-approval-checklist.md` | C.1 | Human sign-off | **LOW** — Add namespace boundary verification item |
| `hermes-auditor-agent-design.md` | B.2 | Classification rules | **LOW** — Update Class E definition from "project coupling" to "namespace misplacement" |

### 8.2 Documents NOT Requiring Revision

| Document | Reason |
|:-----|:-----|
| `hermes-skill-policy.md` | IS/IS NOT definitions remain correct; Skill Policy already enforces isolation |
| `hermes-skill-audit-cli.md` | Audit CLI design is generic; scope filter can be added as parameter |
| `hermes-skill-migration-execution-review.md` | Review scope unchanged; Wave 2 revision is a pre-execution correction |
| `TA-0-architecture-audit.md` | Historical audit document — not modified by governance phases |
| `universal-agent-framework-rfc.md` | RFC is abstract framework; namespace model is Hermes-specific instantiation |

### 8.3 Revision Order

```
C.3 (this document) → defines namespace model
    ↓
B.3 revision        → Wave 2 updated to "namespace isolation"
    ↓
B.0 revision        → Schema extended with namespace/ownership/scope fields
    ↓
C.2 revision        → Wave 0 matrix references updated
    ↓
B.4 revision        → Scope validation rules added
    ↓
C.1 revision        → Namespace boundary sign-off item added
    ↓
B.2 revision        → Class E definition updated
```

---

## 9. Gate Decision

### 9.1 Phase C.3 Status

```
✅ COMPLETE — Read-Only Design Document

Created File: docs/hermes-project-namespace-boundary-review.md

Sections:
  1. Architecture Correction         ← Hermes ≠ Project boundary
  2. Namespace Model                 ← Three-layer hierarchy
  3. Ownership Model                 ← Tier 0/1/2 ownership
  4. Skill Scope Classification      ← Core / Adapter / Project
  5. Wave 2 Revision                 ← From "removal" to "isolation"
  6. Registry Schema Extension       ← namespace, ownership, scope fields
  7. Architecture Boundary Verification  ← Dependency rules enforcement
  8. Impact Assessment               ← Documents requiring revision
  9. Gate Decision                   ← Next steps

Verification:
  ✅ No executable code
  ✅ No Registry modification
  ✅ No Skill modification
  ✅ No file movement
  ✅ git status: only this new file (untracked)
  ✅ Hermes boundary clearly separated from A3/Veritas/UCampus
  ✅ Project namespaces preserved (not erased)
  ✅ Wave 2 strategy corrected
```

### 9.2 Next Gate Decision

```
Phase C.3 → NEXT GATE

Decision Required:
  [ ] Approve namespace model and Wave 2 revision
  [ ] Authorize B.3 Wave 2 section revision
  [ ] Authorize B.0 Registry Schema field extension
  [ ] Authorize B.4 validation rules update

Recommended Order:
  1. Review C.3 (this document) — architecture decision
  2. If approved: Revise B.3 §5 (Wave 2 namespace isolation)
  3. If approved: Revise B.0 §2 (Registry schema extension)
  4. If approved: Revise C.2 (Wave 0 references)
  5. Then: Proceed to Phase C.4 (Execution Authorization)

Proposed Phase:
  C.4 — Updated Migration Execution Review (incorporating namespace model)
    ↓
  C.5 — Final Approval Gate (all revisions complete)
    ↓
  Phase A — Execution (gated by human approval)
```

---

> **Phase:** C.3 — Project Namespace Boundary Review
> **Status:** Complete — Ready for Governance Review
> **Next Gate:** Human Review → Revise B.3 Wave 2 → Revise B.0 Schema → Proceed to C.4
> **Architecture Principle:** Hermes is a general Agent Framework. Projects are consumers. Namespaces separate them.
