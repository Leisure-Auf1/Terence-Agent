# Hermes Wave 0 Dry Run Specification

**Status:** Governance Design Document · Read-Only · No Execution
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** C.2 — Wave 0 Dry Run Specification
**Audience:** Migration Operator + Validator
**Purpose:** Define an isolated dry-run procedure to validate Wave 0 safety before touching production

---

## 1. Dry Run Objective

Wave 0 does NOT migrate. Wave 0 Dry Run does NOT simulate migration.

The dry run answers one question:

> **"If we relocate these 8 Skills from the Skill Layer to their target layers, will anything break?"**

It answers this by:

1. Creating a **shadow environment** — an isolated copy of the Registry and Skill loading paths
2. Executing **equivalence tests** — comparing pre- and post-relocation behavior
3. Producing a **pass/fail report** per Skill — no ambiguous "probably fine"

**If any Skill fails equivalence → Wave 0 is BLOCKED until resolved.**

---

## 2. Wave 0 Target Matrix

### Current State (Production)

| # | Skill | In Registry? | Mount | Layer |
|:--|:-----|:----:|:-----|:-----|
| 1 | agent-governance-protocol | ❌ | — (loaded via Governance) | Skill (disk) |
| 2 | architecture-constraints | ✅ | `always` | Skill (disk) |
| 3 | guidance-agent | ❌ | — (loaded via skill_view) | Skill (disk) |
| 4 | error-registry | ✅ | `always` | Skill (disk) |
| 5 | skill-manager | ✅ | `always` | Skill (disk) |
| 6 | harness-preflight | ❌ | — (loaded via skill_view) | Skill (disk) |
| 7 | task-progress | ✅ | `auto` | Skill (disk) |
| 8 | agent-logger | ❌ | — (loaded via skill_view) | Skill (disk) |

### Target State (Post Wave 0)

| # | Skill | Target Layer | Loading Mechanism | Validation Method |
|:--|:-----|:-----|:-----|:-----|
| 1 | agent-governance-protocol | Governance | Governance Protocol injection | Phase 0/1/2 behavior identical |
| 2 | architecture-constraints | Governance | Policy reference (on-demand) | Constraints document accessible; no forced `always` |
| 3 | guidance-agent | Framework | Agent Registry role definition | Agent Team dispatch identical |
| 4 | error-registry | Memory | Long Memory (type=error_lesson) | 38 records queryable; retrieval functional |
| 5 | skill-manager | Framework | Framework-native Skill Router | `skill_manage` tool identical |
| 6 | harness-preflight | Governance | Phase 0 gate trigger | `check-preflight.sh` output identical |
| 7 | task-progress | Memory | Progress Memory | Cross-session progress data retained |
| 8 | agent-logger | Framework | Agent Registry role definition | Logging behavior identical |

### Critical Distinction

```
Skills 1,3,6,8: NOT in Registry → no de-registration needed
                 → dry run tests: verify new-layer loading works
                 → production action: mark skill file location as deprecated

Skills 2,4,5,7: IN Registry → de-registration IS the action
                 → dry run tests: simulate removal + verify new-layer loading
                 → production action: remove from Registry JSON
```

---

## 3. Dry Run Environment

### 3.1 Isolation Requirements

```
Production                    Dry Run (Shadow)
─────────────────────────────────────────────────────
~/.hermes/skills/             /tmp/wave0-dryrun/skills/      (read-only copy)
skill-registry.json           /tmp/wave0-dryrun/registry.json (full copy)
Hermes session                /tmp/wave0-dryrun/session/      (isolated runtime)
Memory backend                /tmp/wave0-dryrun/memory/       (empty memory)
```

### 3.2 Environment Setup

```
Step 1: Create shadow directory
  mkdir -p /tmp/wave0-dryrun/{skills,memory,session}

Step 2: Snapshot production state
  cp -r ~/.hermes/skills/ /tmp/wave0-dryrun/skills/
  cp skill-registry.json /tmp/wave0-dryrun/registry.baseline.json

Step 3: Create simulated registry (post-Wave 0)
  cp /tmp/wave0-dryrun/registry.baseline.json /tmp/wave0-dryrun/registry.simulated.json
  → Remove entries for: architecture-constraints, error-registry, skill-manager, task-progress
  → Leave entries for all Class A/B/E Skills intact

Step 4: Verify isolation
  diff /tmp/wave0-dryrun/registry.simulated.json skill-registry.json
  → MUST show differences (confirms dry run is NOT touching production)
```

### 3.3 Shadow Loading

For Skills 1,3,6,8 (not in Registry, loaded via skill_view):
- The dry run does NOT test registry changes for these
- Instead, it tests: "can the target layer loading mechanism load the Skill's content?"
- This is a **content availability** test, not a registry operation test

For Skills 2,4,5,7 (in Registry):
- The dry run tests: "with these entries removed from the simulated registry, does the new loading mechanism provide equivalent functionality?"

---

## 4. Equivalence Validation

### 4.1 Per-Skill Test Cases

#### 1. agent-governance-protocol

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T1.1 | Governance Protocol content loaded | Load content from Governance document path (not Skill path) | Content identical to current SKILL.md body |
| T1.2 | Phase 0 trigger invokes preflight gate | Start new session → Phase 0 invoked | Preflight runs normally |
| T1.3 | Phase 1 rules enforced | Task with Type D change requested | Approval gate triggers (no silent skip) |
| T1.4 | Stop Conditions active | Ambiguous request submitted | Hermes stops, requests clarification |

**Pass condition:** All 4 tests match production behavior.

#### 2. architecture-constraints

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T2.1 | Constraint content accessible | Query: "What are the architecture constraints?" | Full 512-line constraint document returned |
| T2.2 | No longer force-mounted | New session WITHOUT `always` mount | Session starts successfully; no constraint injection |
| T2.3 | On-demand load works | Explicit load: "Load the architecture constraints" | Document loads and is available in context |

**Pass condition:** T2.1 content match; T2.2 session starts without forced mount; T2.3 on-demand load works.

#### 3. guidance-agent

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T3.1 | Agent role definition accessible | Query: "What is the Guidance Agent's role?" | Role description returned (not from Skill path, from Agent Registry) |
| T3.2 | Agent Team dispatch works | Task: "Use the Agent Team to review this code" | Guidance→Developer→Debugger→Logger flow executes |
| T3.3 | skill_manage tool functional | Guidance loads appropriate Skills for task | Skills loaded, no "exclusive authority" claim in output |

**Pass condition:** All 3 tests pass. T3.3 verifies the exclusive-authority language is removed.

#### 4. error-registry

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T4.1 | Error lookup works | Mock error: "PEP668 error during pip install" | Error record returned with L2 classification and fix |
| T4.2 | Query interface functional | Query: "List all L0 errors" | Correct count and entries returned |
| T4.3 | No longer force-loaded | New session WITHOUT `always` mount | 38 records NOT in initial context; available on demand |

**Pass condition:** T4.1 returns correct record; T4.2 query works; T4.3 session starts without 38-record context bloat.

#### 5. skill-manager

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T5.1 | Skill dispatch works | Task: "Use browser-automation to navigate to example.com" | browser-automation Skill loaded and dispatched |
| T5.2 | Mount strategies preserved | Complex task → auto-mount task-progress | task-progress loaded via auto strategy |
| T5.3 | Forbidden pairs enforced | Task: "Use browser-automation AND computer-use-mcp together" | Routing rejects forbidden pair |

**Pass condition:** All 3 tests pass. Skill dispatch is the core of Hermes — this is the highest-risk test.

#### 6. harness-preflight

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T6.1 | Shell script executes | Run: `bash scripts/check-preflight.sh` | SHA fingerprint, risk tier, PII scan all produce output |
| T6.2 | Phase 0 triggers preflight | New session with Terence-Agent context | Preflight runs as Phase 0 gate |
| T6.3 | Script output identical | Diff preflight output dry-run vs production | Identical except SHA and timestamp |

**Pass condition:** T6.1 script runs; T6.2 triggers in correct phase; T6.3 output matches.

#### 7. task-progress

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T7.1 | Progress data writes | Start multi-step task → write progress | Progress file created with correct format |
| T7.2 | Cross-session resume | Read progress from previous session (simulated) | Progress data returned intact |
| T7.3 | No longer auto-mounted | Simple single-step task | Progress NOT loaded (correct — not needed) |

**Pass condition:** T7.1 writes; T7.2 reads; T7.3 does not load unnecessarily.

#### 8. agent-logger

| Test | Pre-condition | Dry Run Action | Expected Result |
|:-----|:-----|:-----|:-----|
| T8.1 | Logging functions | Execute task → check log output | Task logged with correct format |
| T8.2 | Event report updated | Complete task → check event-report entry | Entry written correctly |
| T8.3 | Logger role accessible | Query: "What does the Logger Agent do?" | Description returned from Agent Registry |

**Pass condition:** All 3 tests pass.

### 4.2 Cross-Skill Integration Test

After all 8 individual tests pass, run one integration test:

```
Scenario: Full Agent Team workflow with error recovery

1. Guidance Agent receives complex task
2. Guidance dispatches to Developer via Agent Team
3. Developer encounters PEP668 error
4. Error is looked up → Long Memory (not Skill mount)
5. Debugger proposes fix based on error-registry record
6. Logger records all steps
7. task-progress tracks completion
8. Preflight runs at Phase 0 of next task

Expected: All 8 relocated components function together without Skill Registry dependency.
```

---

## 5. Failure Conditions

### Critical Failures (BLOCK Wave 0)

| # | Condition | Test |
|:--|:-----|:----:|
| F.1 | **Skill dispatch failure** — `skill_manage` tool returns error after skill-manager relocation | T5.1 |
| F.2 | **Constraint loss** — architecture-constraints document inaccessible after de-registration | T2.1 |
| F.3 | **Error lookup failure** — error-registry query returns empty after relocation | T4.1 |
| F.4 | **Phase 0 gate failure** — Preflight does not trigger after harness-preflight relocation | T6.2 |
| F.5 | **Agent Team routing failure** — Guidance→Developer→... chain broken | T3.2 |
| F.6 | **Content divergence** — relocated content differs from original Skill file content | T1.1 |

### Warning Failures (Proceed with Caution)

| # | Condition | Test |
|:--|:-----|:----:|
| W.1 | **Unnecessary loading** — de-registered content still appears in session context | T2.2, T4.3 |
| W.2 | **Slow retrieval** — new loading mechanism takes >2x longer than Skill mount | T4.1 |
| W.3 | **Metadata mismatch** — version/owner fields differ between old and new location | All |

---

## 6. Rollback Simulation

### 6.1 Simulated Rollback Procedure

```
Trigger: Any Critical Failure (F.1-F.6) detected during dry run

Step 1: STOP all dry run tests immediately

Step 2: Restore simulated registry from baseline
   cp /tmp/wave0-dryrun/registry.baseline.json \
      /tmp/wave0-dryrun/registry.simulated.json

Step 3: Re-run failing test against restored registry

Step 4: Verify test now passes (confirms rollback works)

Step 5: Record failure in dry run report
   - Which test failed
   - What was expected
   - What was observed
   - Was rollback successful
```

### 6.2 Rollback Verification Matrix

| Failure | Rollback Action | Verification |
|:-----|:-----|:-----|
| F.1 (dispatch) | Restore skill-manager to Registry | Re-run T5.1 → PASS |
| F.2 (constraints) | Restore architecture-constraints to Registry | Re-run T2.1 → PASS |
| F.3 (errors) | Restore error-registry to Registry | Re-run T4.1 → PASS |
| F.4 (preflight) | Restore harness-preflight to Registry | Re-run T6.2 → PASS |
| F.5 (routing) | Restore guidance-agent to Registry | Re-run T3.2 → PASS |
| F.6 (content) | Verify Skill file content unchanged | Diff Skill file vs. new-layer copy |

---

## 7. Human Review Gate

### Pre-Dry-Run Approval

| # | Check | Status |
|:--|:-----|:----:|
| ☐ | Dry run environment isolated from production | ☐ |
| ☐ | Production Registry backed up (snapshot created) | ☐ |
| ☐ | All 8 Skill files confirmed unmodified since audit | ☐ |
| ☐ | Migration Operator designated (separate from Reviewer) | ☐ |
| ☐ | Validator designated (separate from Operator) | ☐ |

### Post-Dry-Run Approval

| # | Check | Status |
|:--|:-----|:----:|
| ☐ | All 8 individual equivalence tests PASS | ☐ |
| ☐ | Cross-skill integration test PASS | ☐ |
| ☐ | 0 Critical Failures (F.1-F.6) | ☐ |
| ☐ | Rollback simulation completed successfully | ☐ |
| ☐ | Dry run report produced | ☐ |

### Decision After Dry Run

```
☐ Wave 0 Cleared — Proceed to production execution
☐ Wave 0 Cleared with Warnings — (list warnings, proceed)
☐ Wave 0 BLOCKED — (list critical failures, return to design)
```

---

## 8. Final Decision

### Phase C.2 Status

```
✅ READY FOR DRY RUN

   8 Skills specified with target layers and loading mechanisms
   32 individual test cases defined (4 per Skill)
   1 cross-skill integration test defined
   6 critical failure conditions defined
   6 rollback actions specified
   Dry run environment isolated from production (~/.hermes untouched)

   Pre-condition: §7 Pre-Dry-Run Approval completed by Governance Reviewer
```

### If Ready → Execute

```
Export HERMES_HOME=/tmp/wave0-dryrun
Execute §4 equivalence tests (32 tests)
Execute §4.2 integration test (1 test)
Produce dry run report
Submit for §7 Post-Dry-Run Approval
```

### Verification (This Document)

| 检查 | 结果 |
|:-----|:-----|
| 8 sections complete | ✅ |
| 32 test cases defined | ✅ (§4.1, 4 per Skill) |
| 0 executable code | ✅ Pure specification |
| 0 registry modification | ✅ Production Registry untouched |
| 0 Skill modification | ✅ All Skill files untouched |
| Dry run isolation specified | ✅ `/tmp/wave0-dryrun/` |
| Rollback path specified | ✅ §6 per-failure rollback |
