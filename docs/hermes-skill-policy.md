# Hermes Skill Governance Policy

**Version:** 1.0
**Status:** Active
**Type:** Governance Document — Tier 1 (mandatory for all Skill authors)
**Applies to:** All Skills registered under Hermes Agent

---

## 1. Skill Purpose

### 1.1 Definition

A **Skill** is a reusable capability extension that augments Hermes Agent with domain-specific operational knowledge, tool workflows, or procedural patterns. Skills are the mechanism through which Hermes learns and retains task-specific expertise across sessions.

### 1.2 What a Skill IS

| ✅ IS | Description |
|:-----|:-----|
| **Capability extension** | Adds a specific operational ability (e.g., browser automation, PDF editing, code review) |
| **Isolated functionality unit** | Has clear boundaries, declared inputs/outputs, and runs independently of other Skills |
| **Reusable workflow** | Encodes a proven procedural pattern that applies across multiple sessions and projects |
| **Tool orchestration guide** | Teaches Hermes how to use existing tools effectively for a specific domain |
| **Domain knowledge** | Provides specialized reference material (API docs, configuration patterns, error recovery steps) |

### 1.3 What a Skill IS NOT

| ❌ IS NOT | Rationale |
|:-----|:-----|
| **Governance rule** | Skills must not define or modify execution rules, approval flows, or safety constraints. Governance is the exclusive domain of the Governance Protocol. |
| **Architecture authority** | Skills must not make or redefine architectural decisions. Architecture is governed by the RFC process, not by operational skills. |
| **Workflow controller** | Skills must not create or replace the Phase 0/1/2 workflow engine. Workflow execution is the domain of the Governance Protocol. |
| **Runtime replacement** | Skills must not implement alternative execution engines, parallel runtime systems, or bypass existing Hermes infrastructure. |
| **Hidden governance** | Skills must not modify agent behavior through side effects (system prompt injection, approval bypass, context manipulation). |

### 1.4 Governance Stack

```
                    Hermes Agent
                         │
            ┌────────────┼────────────┐
            │            │            │
     ┌──────▼──────┐ ┌───▼────┐ ┌─────▼──────┐
     │ Governance  │ │Workflow│ │   Skill    │
     │  Protocol   │ │ Policy │ │  Policy    │
     │             │ │        │ │ (this doc) │
     │ Rules +     │ │Phase   │ │            │
     │ Constraints │ │0/1/2   │ │Boundaries  │
     └─────────────┘ └────────┘ └─────┬──────┘
                                      │
                              ┌───────▼───────┐
                              │ Skill Registry│
                              │ (metadata)    │
                              └───────┬───────┘
                                      │
                          ┌───────────┼───────────┐
                          │           │           │
                     ┌────▼────┐ ┌───▼────┐ ┌────▼────┐
                     │ Skill A │ │Skill B │ │ Skill C │
                     └─────────┘ └────────┘ └─────────┘
```

---

## 2. Skill Metadata Schema

### 2.1 Required Fields

Every Skill MUST declare the following metadata in its frontmatter:

```yaml
# skill.yaml — embedded in SKILL.md frontmatter
name: browser-automation              # lowercase, hyphens, ≤64 chars
version: 2.1.0                        # semantic versioning
description: >-                       # ≤1024 chars, starts with "Use when..."
  Use when performing browser automation tasks.
  Provides a 4-layer framework from Playwright DOM to Screenshot Vision.
purpose: browser-automation           # single clear capability
author: agent-team                    # owner identifier
license: MIT
status: active                        # active | deprecated | archived

permissions:                          # what this Skill requires
  allow:
    - network.external_api
    - filesystem.read

dependencies:                         # runtime + other Skills
  runtime:
    - python >= 3.11
    - playwright >= 1.40
  skills:
    - browser-safety >= 1.0

capability:                           # concrete abilities provided
  - browser.navigate
  - browser.click
  - browser.extract

limitations:                          # known constraints
  - "Requires Chromium installed (~300MB)"
  - "Not compatible with headless environments without display server"

validation:                           # how to verify the Skill works
  check: "playwright --version"
  test: "python -c 'from playwright.sync_api import sync_playwright; print(sync_playwright().__enter__().chromium.launch())'"
```

### 2.2 Field Definitions

| Field | Required | Description |
|:-----|:--------:|:-----|
| `name` | ✅ | Unique identifier. Lowercase, hyphens, ≤64 chars. Must match directory name. |
| `version` | ✅ | Semantic versioning (MAJOR.MINOR.PATCH). MAJOR bump = breaking interface change. |
| `description` | ✅ | Trigger condition + behavior. ≤1024 chars. Format: "Use when X. Does Y." |
| `purpose` | ✅ | Single capability category this Skill provides. |
| `author` | ✅ | Owner or team identifier. |
| `license` | ✅ | SPDX license identifier (MIT, Apache-2.0, etc.). |
| `status` | ✅ | `active` (production), `deprecated` (replaced, grace period), `archived` (removed). |
| `permissions` | ✅ | Resources this Skill needs. Must not request permissions outside its purpose. |
| `dependencies` | | Runtime packages and other Skills this depends on. |
| `capability` | ✅ | Concrete abilities provided. Format: `domain.action`. |
| `limitations` | | Known constraints, incompatibilities, resource requirements. |
| `validation` | | How to verify the Skill is functional (environment check + test command). |

### 2.3 Prohibited Metadata

| Field | Reason |
|:-----|:-----|
| `governance_rules` | Skills must not define rules that modify agent behavior |
| `workflow_override` | Skills must not replace or bypass Phase 0/1/2 |
| `system_prompt_injection` | Skills must not modify the agent's system prompt |
| `auto_approve` | Skills must not create self-approving execution paths |
| `hidden_dependency` | Dependencies must be declared; implicit coupling is forbidden |

---

## 3. Skill Lifecycle

### 3.1 Lifecycle States

```
                    ┌─────────────┐
                    │  PROPOSED   │  ← Author proposes new Skill
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   REVIEW    │  ← Governance review (checklist §6)
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
         ┌────▼───┐   ┌───▼────┐   ┌───▼────┐
         │ REJECT │   │REVISE  │   │ACCEPT  │
         └────────┘   └───┬────┘   └───┬────┘
                          │            │
                          └─────┬──────┘
                                │
                         ┌──────▼──────┐
                         │ REGISTERED  │  ← Added to Skill Registry
                         └──────┬──────┘
                                │
                         ┌──────▼──────┐
                         │   ACTIVE    │  ← Ready for use in sessions
                         └──────┬──────┘
                                │
                    ┌───────────┼───────────┐
                    │           │           │
               ┌────▼───┐  ┌───▼────┐  ┌───▼───────┐
               │UPDATE  │  │PATCH   │  │DEPRECATE  │
               └────┬───┘  └───┬────┘  └─────┬─────┘
                    │           │             │
                    └─────┬─────┘      ┌──────▼──────┐
                          │            │  DEPRECATED │
                          ▼            └──────┬──────┘
                    ┌──────────┐              │
                    │  ACTIVE  │       ┌──────▼──────┐
                    │(new ver) │       │  ARCHIVED   │
                    └──────────┘       └─────────────┘
```

### 3.2 State Descriptions

| State | Description | Who can transition |
|:-----|:-----|:-----|
| **PROPOSED** | Skill idea submitted for review | Anyone → REVIEW |
| **REVIEW** | Under governance evaluation | Reviewer → ACCEPT / REJECT / REVISE |
| **REVISE** | Changes requested | Author → REVIEW |
| **ACCEPT** | Approved for registration | System → REGISTERED |
| **REJECT** | Does not meet policy | Terminal (can be re-proposed) |
| **REGISTERED** | Metadata in Skill Registry | System → ACTIVE |
| **ACTIVE** | Available for use in sessions | Author → UPDATE / DEPRECATE |
| **DEPRECATED** | Replaced or obsolete; grace period before removal | Curator → ARCHIVED |
| **ARCHIVED** | Removed from active use; metadata retained | Terminal |

### 3.3 Approval Gates

| Gate | Trigger | Required |
|:-----|:-----|:-----|
| **Quality Gate** | PROPOSED → REVIEW | Skill Quality Checklist (§6) — all items pass |
| **Permission Gate** | REVIEW → ACCEPT | Permissions align with purpose; no governance overreach |
| **Dependency Gate** | REVIEW → ACCEPT | All dependencies are declared and resolvable |
| **Deprecation Gate** | ACTIVE → DEPRECATED | Migration path documented; replacement Skill identified |

---

## 4. Skill Permission Model

### 4.1 Permission Tiers

| Tier | Scope | Examples |
|:-----|:-----|:-----|
| **Tier 0 — Unrestricted** | Read-only, no side effects | `filesystem.read`, `memory.search`, `knowledge.search` |
| **Tier 1 — Standard** | Read + write within declared scope | `filesystem.write` (whitelist paths), `tool.exec` (whitelist commands) |
| **Tier 2 — Elevated** | Cross-agent access, system configuration | `memory.cross_agent_read`, `git.push`, `skill.manage` |
| **Tier 3 — Restricted** | Governance modification, runtime control | `policy.modify`, `workflow.override`, `agent.spawn` |

### 4.2 Permission Rules

| Permission | Allowed for Skills? | Condition |
|:-----|:----:|:-----|
| `filesystem.read` | ✅ | Default. All Skills can read files in their scope. |
| `filesystem.write` | ✅ | Must declare whitelist paths in `permissions.allow`. No wildcard writes to `~/.ssh/`, `~/.config/`, `.env`. |
| `memory.read` | ✅ | Within own memory namespace. Cross-agent read requires Tier 2. |
| `memory.write` | ✅ | Within own memory namespace. |
| `network.external_api` | ✅ | Must declare target domains. |
| `git.commit` | ✅ | Must declare target repository. |
| `git.push` | ⚠️ | Tier 2 — requires explicit approval. |
| `skill.manage` | ⚠️ | Tier 2 — required for Skill dependencies, not for governance. |
| `tool.exec` | ✅ | Must declare whitelist commands. |
| `agent.spawn` | ❌ | Tier 3 — prohibited for Skills. Governance-only. |
| `policy.modify` | ❌ | Tier 3 — prohibited for Skills. Governance-only. |
| `workflow.override` | ❌ | Tier 3 — prohibited for Skills. Governance-only. |
| `system_prompt.inject` | ❌ | Prohibited. No Skill may modify Hermes' system prompt. |

### 4.3 Permission Declaration Format

```yaml
permissions:
  allow:
    - filesystem.read                          # Tier 0
    - filesystem.write:                        # Tier 1 — scoped
        paths: ["/workspace/**", "/tmp/hermes-skill-*"]
        exclude: [".env", "*.key", "*.pem"]
    - tool.exec:                               # Tier 1 — whitelist
        allow_list: ["pylint", "pytest", "bandit"]
    - network.external_api:                    # Tier 1 — domain-scoped
        domains: ["api.github.com", "pypi.org"]
  deny:                                        # Explicit denies (override allow globs)
    - filesystem.write:
        paths: ["~/.ssh/**", "~/.hermes/config.yaml"]
    - secret.read
```

---

## 5. Skill Isolation Rules

### 5.1 Mandatory Isolation

Every Skill MUST:

| Rule | Requirement |
|:-----|:-----|
| **Single Responsibility** | One Skill = one capability domain. "Browser automation" is a Skill. "Do everything" is not. |
| **Declared I/O** | All inputs (dependencies, permissions, environment) and outputs (files, events, state changes) must be declared in metadata. |
| **No Global State** | Skills must not rely on or modify global Hermes state. All persistent data goes through the Memory Interface with `skill:<name>` namespace prefix. |
| **No Cross-Skill Modification** | Skill A must not modify Skill B's files, configuration, or metadata. Cross-skill interaction is through the Event Bus only. |
| **Independent Execution** | A Skill must function when activated alone. If Skill A requires Skill B, that dependency must be in `dependencies.skills`. |
| **No Governance Side-Effects** | Skill execution must not change governance rules, workflow phases, or approval gates. |

### 5.2 Namespace Convention

```
Skill files:     skills/<category>/<skill-name>/
Skill memory:    skill:<skill-name>:<key>
Skill traces:    trace source.agent_id = "skill:<skill-name>"
Skill events:    event_type prefix = "skill.<skill-name>."
```

### 5.3 Modularity Boundaries

```
✅ Allowed cross-skill interaction:
   - Skill B listed as dependency in Skill A's metadata
   - Event Bus messages with declared topic subscription
   - Shared reference data read from Memory (read-only)

❌ Prohibited cross-skill interaction:
   - Direct file access into another Skill's directory
   - Silent modification of another Skill's configuration
   - Runtime patching of another Skill's behavior
   - Implicit dependency (using another Skill's output without declaring it)
```

---

## 6. Skill Quality Checklist

### 6.1 Registration Gate

Before a Skill can transition from PROPOSED to ACCEPT, ALL of the following MUST pass:

| # | Check | Pass Condition |
|:--|:-----|:-----|
| 1 | **No Duplication** | Does NOT duplicate an existing active Skill's capability. Extension (composable layer on top) is acceptable; reimplementation is not. |
| 2 | **Clear Responsibility** | Purpose field is a single capability domain. "Code review" is clear. "Code review + deployment + monitoring" is a Mega Skill — split into three. |
| 3 | **Defined I/O** | `inputs` (permissions, dependencies) and `outputs` (files, events, state changes) are declared in metadata. |
| 4 | **Failure Cases Documented** | `limitations` field covers known failure modes, incompatibilities, and resource requirements. |
| 5 | **Independent Execution** | Skill can be activated in isolation without non-declared dependencies. |
| 6 | **Permission Alignment** | Requested permissions are the minimum necessary for the declared purpose. "Browser automation" needing `git.push` is a red flag. |
| 7 | **No Governance Overreach** | Metadata contains none of the prohibited fields (§2.3). Body contains no governance rule modification. |
| 8 | **Validation Defined** | `validation.check` and `validation.test` fields are present and executable. |
| 9 | **Versioned** | Follows semantic versioning. First public version ≥ 1.0.0. |

### 6.2 Deprecation Checklist

Before deprecating a Skill:

| # | Check |
|:--|:-----|
| 1 | Replacement Skill identified and ACTIVE |
| 2 | Migration path documented (how to switch from old → new) |
| 3 | Grace period announced (minimum 14 days before archival) |
| 4 | Dependent Skills updated to use replacement |

---

## 7. Skill Communication Protocol

### 7.1 Execution Report Format

Every Skill execution MUST produce a structured report with the following sections:

```markdown
[Skill Status]
  Skill: <skill-name> v<version>
  Status: ok | warn | error
  Duration: <N>ms

[Input]
  <declared inputs: files, parameters, dependencies loaded>

[Action]
  <step-by-step: what the Skill did>

[Output]
  <declared outputs: files created, events published, state changes>

[Verification]
  <how correctness was validated: tests passed, schema checks, manual review>
```

### 7.2 Silent Execution Rule

**A Skill MUST NOT execute silently.** If a Skill produces no visible output, it must report:

```
[Skill Status]
  Skill: <name>
  Status: ok
  Action: no operations performed
  Reason: <why nothing was done>
```

---

## 8. Anti-Patterns

### 8.1 Forbidden Patterns

| # | Anti-Pattern | Description | Example |
|:--|:-----|:-----|:-----|
| ❌ 1 | **Mega Skill** | A single Skill that does everything | `name: universal-agent` — claims to handle "code, ops, design, review, deploy" |
| ❌ 2 | **Hidden Governance** | A Skill that modifies agent behavior rules | Skill silently adds "skip preflight" to workflow configuration |
| ❌ 3 | **Runtime Replacement** | A Skill that creates an alternative execution engine | Skill implements its own DAG executor, bypassing the Phase 0/1/2 workflow |
| ❌ 4 | **Dependency Injection** | A Skill that silently depends on project-specific structure | Hardcoding `~/Terence-Agent/` path or assuming a specific repository layout |
| ❌ 5 | **Permission Overreach** | A Skill requesting permissions far beyond its purpose | `name: markdown-formatter` requesting `network.external_api` and `agent.spawn` |
| ❌ 6 | **Version Masking** | A Skill that patches another Skill without declaring dependency | Skill B modifies Skill A's `skill.yaml` to change permissions |
| ❌ 7 | **Stealth Skill** | A Skill registered without governance review | Circumventing REVIEW → ACCEPT gate by direct registry insertion |
| ❌ 8 | **Scope Creep** | A Skill gradually expanding beyond its original purpose | v1.0 = "PDF reading". v3.0 = "PDF reading + editing + OCR + file system management + cloud sync" |

### 8.2 Detection Heuristics

| Signal | Suspect |
|:-----|:-----|
| Metadata exceeds 50 lines | Likely Mega Skill or scope creep |
| `permissions.allow` contains `*` or Tier 3 | Permission overreach or hidden governance |
| Dependencies list > 10 other Skills | Excessive coupling; likely monolithic |
| Version MAJOR > 5 within 6 months | Scope unstable; needs redesign |
| Skill reads `~/.hermes/config.yaml` | Hidden governance attempt |
| Skill uses `system_prompt.inject` or equivalent | Immediate rejection |

---

## 9. Skill Registry Design

### 9.1 Registry Purpose

The Skill Registry is the canonical source of truth for all registered Skills. It tracks metadata, status, and relationships — not Skill implementations (which live in their own directories).

### 9.2 Registry Schema

```yaml
# skill-registry.yaml — one entry per Skill
skills:
  - name: browser-automation
    version: 2.1.0
    owner: agent-team
    capability: browser-automation
    permissions: [network.external_api, filesystem.read]
    dependencies:
      skills: [browser-safety]
      runtime: [python>=3.11, playwright>=1.40]
    compatibility:
      platforms: [linux, macos]
      providers: [openai, anthropic, deepseek]
    status: active
    registered: 2026-06-01
    updated: 2026-07-15
    path: skills/browser-automation/
```

### 9.3 Registry Fields

| Field | Required | Description |
|:-----|:--------:|:-----|
| `name` | ✅ | Unique Skill identifier |
| `version` | ✅ | Current active version |
| `owner` | ✅ | Responsible author or team |
| `capability` | ✅ | Single capability category |
| `permissions` | ✅ | Permissions requested (must match skill.yaml) |
| `dependencies` | ✅ | Runtime and Skill dependencies |
| `compatibility` | | Supported platforms, providers, tools |
| `status` | ✅ | Lifecycle state (§3) |
| `registered` | ✅ | First registration date |
| `updated` | ✅ | Last modification date |
| `path` | ✅ | Filesystem path relative to skills root |
| `replaced_by` | | If deprecated, name of replacement Skill |

### 9.4 Registry Operations

| Operation | Description | Requires |
|:-----|:-----|:-----|
| `register` | Add new Skill entry | REVIEW → ACCEPT gate passed |
| `query` | Search/filter by capability, owner, status | — (read-only) |
| `activate` | Mark Skill as ACTIVE for session use | Status = REGISTERED or ACTIVE |
| `deactivate` | Remove Skill from active use | Status → DEPRECATED or ARCHIVED |
| `resolve` | Resolve dependency tree for a Skill | Dependencies declared and available |
| `update` | Bump version, update metadata | Same gates as new registration |
| `archive` | Permanent removal (metadata retained) | Deprecation period elapsed |

---

## Appendix A: Relationship to Hermes Governance Protocol

This Skill Governance Policy is a **child document** of the Hermes Governance Protocol v1.0. Where conflicts arise:

1. Governance Protocol takes precedence over Skill Policy
2. Skill Policy takes precedence over individual Skill metadata
3. Individual Skill metadata takes precedence over Skill body content

Skills that violate this policy are subject to deactivation regardless of their technical functionality.

## Appendix B: Relationship to Universal Agent Framework RFC

The Skill Policy aligns with the Universal Agent Framework RFC (§7 — Skill Registry, §5 — Permission System). The framework defines abstract interfaces; this policy defines Hermes-specific governance rules for those interfaces.

Key mappings:

| UAF RFC | Skill Policy |
|:-----|:-----|
| §7.3 Skill Metadata Schema | §2 Skill Metadata Schema (this doc) |
| §7.4 Registry Commands | §9.4 Registry Operations (this doc) |
| §5 Permission Gateway | §4 Skill Permission Model (this doc) |
| §5.8 Scope Isolation | §5 Skill Isolation Rules (this doc) |

---

> **Policy Status:** Active v1.0
> **Governance Stack:** Protocol → Workflow → Skill Policy → Registry → Skills
> **Next Review:** When first Skill registration is attempted under this policy
> **Amendment Process:** Type D change (requires explicit architecture approval)
