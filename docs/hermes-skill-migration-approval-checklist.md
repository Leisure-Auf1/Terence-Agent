# Hermes Skill Migration — Approval Checklist

**Status:** Governance Approval Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** C.1 — Migration Approval Readiness Review
**Audience:** Governance Reviewer (Human)
**Purpose:** Single-page sign-off authority for Phase C Migration Execution

---

## 1. Governance Approval Matrix

### Phase B Deliverable Verification

| Document | Lines | Sections | Frozen? | Gate |
|:-----|:----:|:----:|:----:|:----:|
| `hermes-skill-registry-schema.md` | 947 | 84 | ✅ | B.0 |
| `hermes-skill-audit-cli.md` | 762 | 59 | ✅ | B.1 |
| `hermes-auditor-agent-design.md` | 742 | 60 | ✅ | B.2 |
| `hermes-skill-migration-specification.md` | 683 | 67 | ✅ | B.3 |
| `hermes-skill-validation-specification.md` | 741 | 71 | ✅ | B.4 |
| `hermes-skill-migration-execution-review.md` | 322 | 31 | ✅ | C.0 |

### Contract Verification

| Check | Result | Evidence |
|:-----|:----:|:-----|
| Registry Schema frozen | ✅ | 12/12 Policy §9 fields defined; required/optional marked |
| Audit CLI contract frozen | ✅ | `hermes skill audit` command interface + classification rules |
| Auditor Agent read-only | ✅ | Spec explicitly: "Auditor does NOT execute, modify, or register" |
| Migration Specification complete | ✅ | Wave 0-4 per-Skill source→target mapping + equivalence conditions |
| Validation Specification covers rollback | ✅ | Per-Wave validation gates + rollback triggers defined |
| No implementation code in any document | ✅ | 0 Python/Shell code in any of the 6 docs |

### Matrix Decision

```
✅ CONDITIONAL GO

All 6 documents exist, are internally consistent, and cover the full
migration lifecycle (Schema → Audit → Migrate → Validate → Review).

Condition: Human Governance Reviewer completes §2 below.
```

---

## 2. Human Approval Checklist

### 2.1 Wave 0 Authorization — Class C Boundary Remediation

| # | Item | Approved? |
|:--|:-----|:----:|
| W0.1 | Allow `agent-governance-protocol` de-registration from Skill Registry | ☐ |
| W0.2 | Allow `architecture-constraints` de-registration from Skill Registry | ☐ |
| W0.3 | Allow `guidance-agent` de-registration from Skill Registry | ☐ |
| W0.4 | Allow `error-registry` de-registration from Skill Registry | ☐ |
| W0.5 | Allow `skill-manager` de-registration from Skill Registry | ☐ |
| W0.6 | Allow `harness-preflight` de-registration from Skill Registry | ☐ |
| W0.7 | Allow `task-progress` de-registration from Skill Registry | ☐ |
| W0.8 | Allow `agent-logger` de-registration from Skill Registry | ☐ |
| W0.9 | Accept target attribution: Governance Layer (2), Framework Layer (4), Memory Layer (2) | ☐ |
| W0.10 | Accept that NO Skill files are deleted — only Registry entries modified | ☐ |

### 2.2 Wave 1 Authorization — Duplicate Capability Merge

| # | Item | Approved? |
|:--|:-----|:----:|
| W1.1 | Allow 3 duplicate groups → 3 merged Skills | ☐ |
| W1.2 | Accept merge requires content diff review before execution | ☐ |
| W1.3 | Accept old Skill IDs may be aliased, not deleted | ☐ |

### 2.3 Wave 2 Authorization — Project Decoupling

| # | Item | Approved? |
|:--|:-----|:----:|
| W2.1 | Allow 6 Class E Skills to be renamed (project names removed) | ☐ |
| W2.2 | Accept rename requires dependency graph scan before execution | ☐ |
| W2.3 | Accept that platform/domain Skills (ucampus-*, lab-report-*) retain current names | ☐ |

### 2.4 Wave 3 Authorization — Metadata Completion

| # | Item | Approved? |
|:--|:-----|:----:|
| W3.1 | Allow 55 Skills to receive `version: 1.0.0` | ☐ |
| W3.2 | Allow 146 Skills to receive `owner: agent-team` | ☐ |
| W3.3 | Accept that `version` is a starting baseline, not historically accurate | ☐ |

### 2.5 Wave 4 Authorization — Full Registration

| # | Item | Approved? |
|:--|:-----|:----:|
| W4.1 | Allow remaining ~70 Class A Skills to be registered under new Schema | ☐ |
| W4.2 | Accept that Registry will grow from 14 to ~138 entries | ☐ |
| W4.3 | Accept that new Schema fields are initialized as `optional` where data unavailable | ☐ |

### 2.6 Risk Acceptance

| # | Item | Approved? |
|:--|:-----|:----:|
| R.1 | Rollback: Registry snapshot restore available for every Wave | ☐ |
| R.2 | Regression: Mount equivalence must be validated before each Wave gate | ☐ |
| R.3 | Dependency: Reference graph must be scanned before Wave 1 and Wave 2 | ☐ |
| R.4 | Operator: Migration Operator, Validator, and Reviewer are three separate entities | ☐ |

---

## 3. Wave 0 Authorization Gate — Per-Skill Detail

Only Wave 0 requires per-Skill authorization because it changes layer attribution, not just metadata.

### Skill: agent-governance-protocol

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops category) | Governance document |
| Mount | `routed` | N/A — loaded as Governance Protocol |
| Current risk | 🔴 HIGH — claims "Mandatory execution rules for Hermes Agent" | Resolved: correctly in Governance layer |
| Target layer | Governance Layer | |
| Loading mechanism | Governance Protocol injection (same as current Protocol) | |
| Verification | Governance loading produces identical Phase 0/1/2 behavior | |

### Skill: architecture-constraints

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, mount=always) | Policy document |
| Mount | `always` | N/A — loaded as Policy reference |
| Current risk | 🔴 HIGH — 512 lines injected into every session | Resolved: Policy doc, loaded on demand or via Governance |
| Target layer | Governance Layer | |
| Loading mechanism | Policy reference; available to Agent via Memory or explicit load | |
| Verification | Constraint document remains accessible; no longer forced `always` mount | |

### Skill: guidance-agent

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, routed) | Framework component |
| Mount | `routed` | Role definition in Agent Registry |
| Current risk | 🔴 HIGH — claims exclusive `skill_manage` authority | Resolved: role defined in Framework, not Skill |
| Target layer | Framework Layer — Agent Registry | |
| Loading mechanism | Agent Registry role definition; routing logic stays as Framework module | |
| Verification | Agent Team dispatch (guidance→dev→debug→exec→logger) functions identically | |

### Skill: error-registry

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, mount=always) | Memory data |
| Mount | `always` | N/A — stored in Long Memory |
| Current risk | 🟡 MEDIUM — 38 records force-loaded every session | Resolved: on-demand retrieval |
| Target layer | Memory Layer — Long Memory (type=error_lesson) | |
| Loading mechanism | MemoryManager.retrieve(type="error_lesson") on error detection | |
| Verification | Error lookup returns identical 38 records; query interface functional | |

### Skill: skill-manager

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, mount=always) | Framework component |
| Mount | `always` | Built-in Framework router |
| Current risk | 🟡 MEDIUM — core routing as Skill is fragile | Resolved: Framework-native router |
| Target layer | Framework Layer — Skill Router | |
| Loading mechanism | Framework boot; always available, not Skill-mounted | |
| Verification | `skill_manage` tool functions identically; Skill dispatch unchanged | |

### Skill: harness-preflight

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, mount=auto) | Governance gate |
| Mount | `auto` | Phase 0 trigger (shell script) |
| Current risk | 🟡 MEDIUM — ambiguous: gate vs. Skill | Resolved: correctly categorized as gate |
| Target layer | Governance Layer — Preflight Gate | |
| Loading mechanism | Triggered by Phase 0 protocol, not Skill mount | |
| Verification | `bash scripts/check-preflight.sh` produces identical output | |

### Skill: task-progress

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, mount=auto) | Memory data |
| Mount | `auto` | N/A — stored in Progress Memory |
| Current risk | 🟡 MEDIUM — progress as Skill is semantically wrong | Resolved: structured data in Memory |
| Target layer | Memory Layer — Progress Memory | |
| Loading mechanism | MemoryManager; cross-session restore via Memory interface | |
| Verification | Progress data retained; cross-session resume functional | |

### Skill: agent-logger

| Attribute | Before | After |
|:-----|:-----|:-----|
| Identity | Skill (devops, routed) | Framework component |
| Mount | `routed` | Role definition in Agent Registry |
| Current risk | 🟡 MEDIUM — Agent role as Skill, ambiguous boundary | Resolved: role in Agent Registry |
| Target layer | Framework Layer — Agent Registry | |
| Loading mechanism | Agent Registry role definition | |
| Verification | Logging behavior unchanged; Logger Agent definition accessible | |

---

## 4. Rollback Approval

### Per-Wave Rollback Contract

| Wave | Snapshot | Validation | Trigger | Recovery Owner |
|:----:|:-----|:-----|:-----|:-----|
| 0 | Registry JSON backup | Mount equivalence test for all 8 Skills | Any `always` mount Skill inaccessible post-migration | Migration Operator |
| 1 | Registry JSON backup + old Skill ID alias map | Merged Skill functionality test | Old Skill ID returns 404 | Migration Operator |
| 2 | Registry JSON backup + dependency graph snapshot | Reference scan: 0 broken links | Orphaned reference detected | Migration Operator |
| 3 | Registry JSON backup | Schema validation: 55 Skills have version+owner | Missing required field | Migration Operator |
| 4 | Registry JSON backup | Full schema validation: 138 entries | Registry parse failure | Migration Operator |

### Rollback Authority Confirmation

| Who | Can Trigger | Can Execute | Can Override |
|:-----|:----:|:----:|:----:|
| Governance Reviewer | ✅ | ❌ | ✅ (can order rollback) |
| Migration Operator | ✅ | ✅ | ❌ |
| Validator | ✅ | ❌ | ❌ |

---

## 5. Architecture Boundary Final Check

| Boundary | Before Migration | After Migration | Violation? |
|:-----|:-----|:-----|:----:|
| **Skill ≠ Governance** | ❌ 2 Skills in Governance role | ✅ 0 | Resolved |
| **Skill ≠ Framework** | ❌ 4 Skills in Framework role | ✅ 0 | Resolved |
| **Skill ≠ Runtime** | ✅ 0 | ✅ 0 | Maintained |
| **Skill ≠ Agent** | ✅ 0 | ✅ 0 | Maintained |
| **Registry ≠ Runtime** | ✅ JSON file | ✅ YAML file | No change |
| **Migration ≠ Execution** | ✅ This is approval | ✅ Execution is next phase | Maintained |

---

## 6. Explicit Forbidden Actions

The following are **prohibited** during Phase C.1 and must NOT be performed even after checklist approval:

| ❌ Action | Reason |
|:-----|:-----|
| Modify `skill-registry.json` | Registry migration is a Phase C.2+ execution action, not an approval action |
| Execute migration script | No script exists; migration is manual per-Wave execution |
| Delete any Skill file | Wave 0-4 operate on Registry, not filesystem. File moves are Phase D |
| Rename any Skill file | Same as above |
| Change any `mount` value in Registry | Mount changes are part of Wave 0 execution, not approval |
| Modify Hermes runtime | Outside Phase B/C scope entirely |

---

## 7. Final Decision

### Phase C.1 Status

```
✅ READY FOR HUMAN APPROVAL

   All 6 Phase B documents verified (947+762+742+683+741+322 lines)
   All 4 architecture boundaries maintained
   All 5 Waves have per-Skill before/after mappings
   All 5 Waves have rollback contracts
   0 blockers identified
```

### If READY → Next Phase

```
Phase C.2: Wave 0 Dry Run Specification

   Design the dry-run procedure for Wave 0:
   - Simulate Registry changes without modifying actual Registry
   - Validate mount equivalence in isolated environment
   - Produce dry-run report before live execution
```

### If BLOCKED → Blocker List

(None currently identified.)

### Signature Block

```
Governance Reviewer: ______________________   Date: __________

☐ §2.1 Wave 0  Approved
☐ §2.2 Wave 1  Approved
☐ §2.3 Wave 2  Approved
☐ §2.4 Wave 3  Approved
☐ §2.5 Wave 4  Approved
☐ §2.6 Risk   Accepted

☐ §3 Wave 0 Per-Skill Authorization (all 8)
☐ §4 Rollback Contracts Accepted
☐ §5 Architecture Boundaries Confirmed

Decision:  ☐ GO — Proceed to Phase C.2
           ☐ CONDITIONAL GO — (specify conditions)
           ☐ NO-GO — (specify blockers)
```
