# Hermes Wave 0 — Execution Plan

**Status:** Phase A.2 — Execution Plan Complete
**Version:** 1.0
**Date:** 2026-07-18T06:25:00Z
**Phase:** A.2 — Wave 0 Execution Plan
**Audience:** Migration Operator · Validator · Governance Reviewer
**Purpose:** Provide exact step-by-step instructions for Wave 0 production execution

**Preconditions Verified:**
- Phase A.0 Preflight ✅ — 4 snapshots created
- Phase A.1 Dry Run ✅ — 26/26 tests PASS, rollback verified
- Governance Constitution v1.0 FROZEN (C.5)
- Human Approval PENDING (A.3)

---

## 1. Wave 0 Objective

Relocate 8 Class C Skills from the Skill Layer to their correct architecture layers (Core / Governance / Framework / Memory).

**8 Targets:**

| # | Skill | Registry? | Mount | Target Namespace |
|:--|:-----|:----:|:-----|:-----|
| 1 | `agent-governance-protocol` | ❌ | — | `hermes.core.governance` |
| 2 | `architecture-constraints` | ✅ | `always` | `hermes.core.constraints` |
| 3 | `guidance-agent` | ❌ | — | `hermes.core.guidance` |
| 4 | `error-registry` | ✅ | `always` | `hermes.core.errors` |
| 5 | `skill-manager` | ✅ | `always` | `hermes.core.registry` |
| 6 | `harness-preflight` | ❌ | — | `hermes.core.preflight` |
| 7 | `task-progress` | ✅ | `auto` | `hermes.core.tracker` |
| 8 | `agent-logger` | ❌ | — | `hermes.core.logger` |

---

## 2. Before State — Complete Inventory

### 2.1 Skills in Registry (4 entries to remove)

```json
// skill-manager — mount=always, trigger=*
{
  "name": "skill-manager",
  "category": "devops",
  "tags": ["core", "router", "orchestrator"],
  "mount": "always",
  "description": "技能管理器 — 任务入口路由",
  "trigger": ["*"]
}

// architecture-constraints — mount=always, trigger=*
{
  "name": "architecture-constraints",
  "category": "devops",
  "tags": ["core", "governance"],
  "mount": "always",
  "description": "架构约束 — 层级/级联/复盘",
  "trigger": ["*"]
}

// error-registry — mount=always, trigger=*
{
  "name": "error-registry",
  "category": "devops",
  "tags": ["core", "errors"],
  "mount": "always",
  "description": "报错表 — 所有已知错误及修复",
  "trigger": ["*"]
}

// task-progress — mount=auto, trigger=complex/multi-step
{
  "name": "task-progress",
  "category": "devops",
  "tags": ["core", "progress"],
  "mount": "auto",
  "description": "进度追踪 — 跨会话恢复",
  "trigger": ["complex", "multi-step"]
}
```

### 2.2 Skills NOT in Registry (4 entries — no action needed)

| Skill | Current Loading | File Location |
|:-----|:-----|:-----|
| `agent-governance-protocol` | System prompt injection | `~/.hermes/skills/devops/agent-governance-protocol/SKILL.md` |
| `guidance-agent` | `skill_view` on-demand | `~/.hermes/skills/devops/guidance-agent/SKILL.md` |
| `harness-preflight` | `skill_view` on-demand | `~/.hermes/skills/devops/harness-preflight/SKILL.md` |
| `agent-logger` | `skill_view` on-demand | `~/.hermes/skills/devops/agent-logger/SKILL.md` |

---

## 3. After State — Target Architecture

### 3.1 Post-Wave 0 Registry

11 entries remain (all Class A/B/E Skills):

| Name | Mount | Description |
|:-----|:-----|:-----|
| `browser-automation` | `routed` | 浏览器自动化伞技能 |
| `layer1-playwright` | `routed` | Playwright DOM 自动化 |
| `layer2-cdp-harness` | `routed` | CDP 连接 + bhts |
| `layer3-browser-use` | `routed` | AI 驱动浏览器自动化 |
| `layer4-screenshot-vision` | `routed` | 截图视觉流 |
| `computer-use-mcp` | `routed` | GitHub 桌面操控 MCP |
| `cli-anything` | `routed` | CLI-Anything 集成 |
| `cli-anything-hermes` | `routed` | Harness 构建器 |
| `cli-hub-meta-skill` | `routed` | CLI-Hub 浏览/安装 |
| `ucampus-auto-complete` | `routed` | U校园 自动答题 |
| `u-campus-course-automation` | `routed` | U校园 全流程指南 |

### 3.2 Namespace Mapping — All 8 Skills

| # | Old Name | New Namespace | Target Layer | Scope | Ownership |
|:--|:-----|:-----|:-----|:-----|:-----|
| 1 | `agent-governance-protocol` | `hermes.core.governance` | Core / Governance | `core` | Tier 0 — `hermes-governance` |
| 2 | `architecture-constraints` | `hermes.core.constraints` | Core / Governance | `core` | Tier 0 — `hermes-governance` |
| 3 | `guidance-agent` | `hermes.core.guidance` | Core / Framework | `core` | Tier 1 — `hermes-platform` |
| 4 | `error-registry` | `hermes.core.errors` | Core / Memory | `core` | Tier 0 — `hermes-governance` |
| 5 | `skill-manager` | `hermes.core.registry` | Core / Framework | `core` | Tier 1 — `hermes-platform` |
| 6 | `harness-preflight` | `hermes.core.preflight` | Core / Framework | `core` | Tier 1 — `hermes-platform` |
| 7 | `task-progress` | `hermes.core.tracker` | Core / Memory | `core` | Tier 0 — `hermes-governance` |
| 8 | `agent-logger` | `hermes.core.logger` | Core / Memory | `core` | Tier 1 — `hermes-platform` |

### 3.3 Loading Mechanism Transition

| Skill | Before | After | Change Description |
|:-----|:-----|:-----|:-----|
| `agent-governance-protocol` | System prompt injection | Same path — no change | Content ownership clarified to Core Governance |
| `architecture-constraints` | `always` mount → every session | On-demand policy reference | Removed from every-session context; loaded when needed |
| `guidance-agent` | `skill_view` on-demand | Agent Registry role definition | Loading path unchanged; ownership moved to Framework |
| `error-registry` | `always` mount → every session | On-demand memory query | 38 records no longer forced into every session |
| `skill-manager` | `always` mount (self-referencing) | Framework-native Skill Router | Integrated into Hermes runtime; Registry becomes data, not logic |
| `harness-preflight` | `skill_view` on-demand | Phase 0 gate trigger | Loading path unchanged; governance ownership clarified |
| `task-progress` | `auto` mount → complex tasks | On-demand progress memory | No longer auto-mounted; explicitly invoked |
| `agent-logger` | `skill_view` on-demand | Agent Registry role definition | Loading path unchanged; ownership moved to Framework |

---

## 4. Execution Steps

### 4.1 Pre-Execution (Operator + Validator)

```
☐ Step 0.1: Confirm snapshots exist and are valid
    ☐ /tmp/hermes-wave0-snapshots/registry.baseline.json — SHA-256 verified
    ☐ /tmp/hermes-wave0-snapshots/skill-inventory-snapshot.txt — all 8 SHAs match
    ☐ Governance Reviewer has signed C.1 §2 (Wave 0 approval)

☐ Step 0.2: Notify all stakeholders
    ☐ Wave 0 execution commencing
    ☐ Expected downtime: None (Registry-only change)
    ☐ Rollback window: Immediate (single-file restore)
```

### 4.2 Registry Modification (Operator ONLY)

```
⚠️ THIS IS THE IRREVERSIBLE STEP
⚠️ Ensure Step 0.1 is complete before proceeding

Step 1: Backup current Registry (DEFENSE IN DEPTH)
  $ cp ~/.hermes/skills/devops/skill-manager/references/skill-registry.json \
       /tmp/hermes-wave0-snapshots/registry.pre-execution-backup.json

Step 2: Remove 4 entries from Registry
  Target file: ~/.hermes/skills/devops/skill-manager/references/skill-registry.json

  Entries to remove:
    - skill-manager       (index 0)
    - architecture-constraints (index 1)
    - error-registry      (index 2)
    - task-progress       (index 3)

  Method: Edit JSON, remove the 4 objects from the "skills" array.
  Keep: forbidden_pairs, mount_strategies (unchanged).
  Keep: version, updated fields (unchanged).

Step 3: Verify modified Registry
  ☐ 11 entries remain (15 → 11)
  ☐ All 4 target entries removed
  ☐ All 11 remaining entries intact
  ☐ forbidden_pairs unchanged (5 pairs)
  ☐ mount_strategies unchanged (3 strategies)
  ☐ Valid JSON (parse without error)

Step 4: Update Registry metadata
  Set: "updated": "2026-07-18"
  Set: "version": "1.0.0" (unchanged — this is data migration, not schema change)
```

### 4.3 Post-Execution Validation (Validator)

```
☐ V1: Registry entry count = 11 (was 15)
     $ python3 -c "import json; d=json.load(open('...skill-registry.json')); print(len(d['skills']))"
     Expected: 11

☐ V2: Removed entries confirmed absent
     $ python3 -c "
     import json
     d=json.load(open('...skill-registry.json'))
     names=[s['name'] for s in d['skills']]
     for t in ['skill-manager','architecture-constraints','error-registry','task-progress']:
         assert t not in names, f'{t} still in registry!'
     print('All 4 removed — verified')
     "

☐ V3: Remaining entries intact
     Expected: browser-automation, layer1-playwright, layer2-cdp-harness, layer3-browser-use,
               layer4-screenshot-vision, computer-use-mcp, cli-anything, cli-anything-hermes,
               cli-hub-meta-skill, ucampus-auto-complete, u-campus-course-automation

☐ V4: forbidden_pairs unchanged
     $ diff <(python3 -c "import json;d=json.load(open('/tmp/hermes-wave0-snapshots/registry.baseline.json'));print(json.dumps(d['forbidden_pairs'],sort_keys=True))") \
            <(python3 -c "import json;d=json.load(open('...skill-registry.json'));print(json.dumps(d['forbidden_pairs'],sort_keys=True))")
     Expected: 0 differences

☐ V5: File integrity — all 8 SKILL.md files unchanged
     $ for s in agent-governance-protocol architecture-constraints guidance-agent error-registry skill-manager harness-preflight task-progress agent-logger; do
         sha256sum ~/.hermes/skills/devops/$s/SKILL.md
       done
     Compare with A.0 snapshot values — must match exactly

☐ V6: No accidental file modifications in ~/.hermes/skills/
     $ diff -r /tmp/hermes-wave0-snapshots/ (pre-execution backup of skills/)
     Expected: 0 differences (except registry.json)

☐ V7: Simulated registry matches production result
     $ diff /tmp/hermes-wave0-dryrun/registry.simulated.json \
            ~/.hermes/skills/devops/skill-manager/references/skill-registry.json
     Expected: 0 differences
```

---

## 5. Validation Checks — Detailed

### 5.1 Pre-Wave Validation (before Step 2)

| # | Check | Command | Expected |
|:--|:-----|:-----|:-----|
| V0.1 | Registry JSON valid | `python3 -c "import json; json.load(open('...registry.json'))"` | No error |
| V0.2 | Snapshot exists | `sha256sum /tmp/hermes-wave0-snapshots/registry.baseline.json` | Hash matches A.0 |
| V0.3 | Skills SHA match | Compare 8 SHA-256 values with A.0 report §3.1 | All 8 match |
| V0.4 | Human approval | C.1 §2 Wave 0 signed | ✅ Signed |

### 5.2 In-Wave Validation (immediately after Step 2)

| # | Check | Command | Expected |
|:--|:-----|:-----|:-----|
| V1 | 11 entries | Count skills array | 11 |
| V2 | 4 removed | Assert target names absent | All removed |
| V3 | 11 remaining | Assert expected names present | All present |
| V4 | Forbidden pairs | Diff with baseline | 0 differences |

### 5.3 Post-Wave Validation (after Step 3)

| # | Check | Command | Expected |
|:--|:-----|:-----|:-----|
| V5 | File integrity | SHA-256 all 8 SKILL.md | Match A.0 |
| V6 | No accidental changes | Diff skills/ with pre-exec backup | 0 diffs (except registry) |
| V7 | Dry run match | Diff simulated vs production registry | 0 differences |

---

## 6. Rollback Procedure

### 6.1 Trigger Conditions

Rollback is triggered if ANY of the following occur:

| Condition | Severity |
|:-----|:----:|
| Registry JSON parse error after modification | **CRITICAL** — immediately rollback |
| Entry count ≠ 11 after modification | **CRITICAL** — immediately rollback |
| Any remaining entry corrupted | **CRITICAL** — immediately rollback |
| forbidden_pairs changed from baseline | **CRITICAL** — immediately rollback |
| Any Skill file SHA mismatch detected | **HIGH** — rollback after investigation |
| Skill dispatch broken (detected in post-Wave session) | **HIGH** — rollback after confirmation |

### 6.2 Full Rollback Command

```bash
# Single command restores pre-Wave 0 state:
cp /tmp/hermes-wave0-snapshots/registry.baseline.json \
   ~/.hermes/skills/devops/skill-manager/references/skill-registry.json

# Verify:
diff /tmp/hermes-wave0-snapshots/registry.baseline.json \
     ~/.hermes/skills/devops/skill-manager/references/skill-registry.json
# Expected: 0 differences

# Confirm restoration:
python3 -c "
import json
d = json.load(open('$HOME/.hermes/skills/devops/skill-manager/references/skill-registry.json'))
print(f'Restored: {len(d[\"skills\"])} entries')
for s in d['skills']:
    print(f'  - {s[\"name\"]} ({s[\"mount\"]})')
"
# Expected: 15 entries including all 4 Wave 0 targets
```

### 6.3 Rollback Verification Steps

| # | After Rollback | Check | Expected |
|:--|:-----|:-----|:-----|
| R1 | Registry entries = 15 | Count | 15 |
| R2 | All 4 targets restored | Assert names present | skill-manager, architecture-constraints, error-registry, task-progress |
| R3 | Mount strategies intact | Check mount field | 3 always, 1 auto, 10 routed |
| R4 | Forbidden pairs intact | Diff with baseline | 0 differences |

---

## 7. Per-Skill Ownership Declaration

Per Governance Constitution v1.0 §5 (C.5):

| # | Skill | Tier | Owner | Authority |
|:--|:-----|:----:|:-----|:-----|
| 1 | `agent-governance-protocol` | 0 | `hermes-governance` | Constitutional amendment only (Type D) |
| 2 | `architecture-constraints` | 0 | `hermes-governance` | Constitutional amendment only (Type D) |
| 3 | `guidance-agent` | 1 | `hermes-platform` | Standard change control (Type C) |
| 4 | `error-registry` | 0 | `hermes-governance` | Constitutional amendment only (Type D) |
| 5 | `skill-manager` | 1 | `hermes-platform` | Standard change control (Type C) |
| 6 | `harness-preflight` | 1 | `hermes-platform` | Standard change control (Type C) |
| 7 | `task-progress` | 0 | `hermes-governance` | Constitutional amendment only (Type D) |
| 8 | `agent-logger` | 1 | `hermes-platform` | Standard change control (Type C) |

---

## 8. Risk Register — Wave 0

| # | Risk | Probability | Impact | Mitigation |
|:--|:-----|:----:|:----:|:-----|
| R1 | JSON parse error after manual edit | Low | CRITICAL | Validate JSON before save; backup immediately before edit |
| R2 | Accidental deletion of wrong entry | Low | CRITICAL | Verify entry names before deletion; count before/after |
| R3 | Forbidden pairs accidentally modified | Very Low | HIGH | Diff forbidden_pairs with baseline before save |
| R4 | Skill file accidentally modified | Very Low | HIGH | SHA-256 verify all 8 after execution |
| R5 | Skill dispatch regression | Low | HIGH | Run T5.1 after execution; rollback if broken |
| R6 | Human error (wrong file edited) | Low | CRITICAL | Use exact file path; verify path before editing |

---

## 9. Human Gate — Approval Required

### 9.1 C.1 Wave 0 Approval Items (C.1 §2)

```
☐ Governance Reviewer confirms:

  ☐ Wave 0 preflight snapshots reviewed (Phase A.0)
  ☐ Wave 0 dry run results accepted (Phase A.1 — 26/26 PASS)
  ☐ Wave 0 execution plan reviewed (Phase A.2 — this document)
  ☐ Rollback procedure verified
  ☐ Migration Operator designated
  ☐ Validator designated
  ☐ Wave 0 scope confirmed: Registry only (4 entries removed)
  ☐ No Skill file modifications in Wave 0 scope
```

### 9.2 Execution Authorization

```
☐ Governance Reviewer signature:
    "I authorize Wave 0 execution per this plan.
     Migration Operator may remove 4 entries from skill-registry.json.
     Validator shall verify per §4.3 and §5.
     Any trigger condition (§6.1) requires immediate rollback."

  Signature: ________________________    Date: ______________
```

---

## Verification

| Check | Result |
|:-----|:----:|
| File exists | ✅ `docs/hermes-wave0-execution-plan.md` |
| Before state documented | ✅ §2 — 4 Registry entries + 4 non-Registry |
| After state specified | ✅ §3 — namespace + layer + ownership |
| Execution steps numbered | ✅ §4 — 4 steps with exact commands |
| Validation checks defined | ✅ §5 — pre-Wave (4) + in-Wave (4) + post-Wave (3) |
| Rollback procedure | ✅ §6 — single-command restore + verification |
| Per-Skill ownership | ✅ §7 — Tier 0/1 with change authority |
| Risk register | ✅ §8 — 6 risks with mitigation |
| Human gate defined | ✅ §9 — C.1 Wave 0 approval items |
| No executable code in plan | ✅ Pure documentation |
| Production Registry untouched | ✅ |
| Skill files untouched | ✅ |
| Git diff | ✅ Only this new file |

---

> **Phase:** A.2 — Wave 0 Execution Plan
> **Status:** ✅ EXECUTION PLAN COMPLETE
> **Next:** Phase A.3 — Human Gate (STOP — Governance Approval Required)
> **After Approval:** Execute §4.2 Registry modification → Validate §5 → Complete Wave 0
