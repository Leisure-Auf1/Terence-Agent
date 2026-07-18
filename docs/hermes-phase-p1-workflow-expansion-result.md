# Phase P.1 — Production Workflow Expansion Result

**Status:** Phase P.1 — Complete
**Date:** 2026-07-18
**Branch:** feat/phase-p1-workflow-expansion
**Preflight:** SHA 8e3371c · 🟢 LOW

---

## 1. Result Summary

```
🟢 P.1 PRODUCTION WORKFLOW EXPANSION — COMPLETE

  P.1.1  执行矩阵 + 3 条真实项目 workflow   ✅ veritas 558 passed · a3 1074 passed · ucampus 就绪
  P.1.2  Skill 使用数据收集 (三源)          ✅ 149 技能画像: 活跃 66 · 从未使用 83
  P.1.3  持续优化循环 (人在环中)            ✅ 11 条 pending 提案 · 幂等验证通过
  P.1.4  无人值守 (systemd timer)          ✅ nightly 全绿 · 明日 09:31 自动运行
```

## 2. 真实执行矩阵（全部真实运行验证）

| Workflow | Project | 真实结果 | 遥测 |
|:---------|:--------|:---------|:----:|
| daily-production-report | hermes-os | 26 checks 🟢 ALL GREEN | ✅ |
| veritas-test-run | veritas | **make test → 558 passed** (1.8s) | ✅ |
| a3-test-run | a3 | **pytest → 1074 passed** (6.9s) | ✅ |
| ucampus-readiness | ucampus | 技能/代理就绪 (账号操作红线排除) | ✅ |
| skill-usage-collection | hermes-os | 149 技能三源画像 | — |
| optimization-loop | hermes-os | 11 提案 pending (人批) | — |

**接入修复**: A3 `.venv` 缺 fastapi/numpy/httpx/scikit-learn 致 9 个测试文件无法收集
→ 补装后 1074 passed。Veritas 无需修复。

## 3. Skill 使用数据（首次三源画像）

数据源: `.usage.json` (128 技能平台统计) + Kernel 遥测 (15 events) + Registry v1.1 (149)

| 指标 | 值 |
|:-----|:--|
| 活跃技能 | 66/149 (44.3%) |
| 从未使用 | **83** |
| 30 天+ 闲置 | 12 |
| deprecated 仍活跃 | 6 |
| Top1 使用 | a3-multi-agent-pipeline (72 次) |

分层: project 12 技能中 11 活跃 (最健康) · core 14 中 12 活跃 · adapter 123 中仅 43 活跃

## 4. 优化循环（数据 → 提案 → 人批）

规则引擎 (R1-R4) → proposal_engine → proposals.jsonl (pending) → 人工审批：

| 规则 | 触发 | 类型 | 本轮产出 |
|:-----|:-----|:-----|:---------|
| R1 | 健康 DEGRADED/FAILED | P1 MAINTENANCE | 0 (全部 HEALTHY) |
| R4 | kernel 失败率 >20% | P2 HEALTH_REVIEW | 0 |
| R2 | 从未使用/闲置 90d+ | P3 ARCHIVE_CANDIDATE | 5 (队列限额) |
| R3 | deprecated 仍活跃 | P4 MERGE_REVIEW | 6 |

**安全边界**: requires_approval=True · P3 队列限额 5 · core 永不进 P3 · 历史裁决不重提 · 幂等（四轮复验 0 新增）

**待审批队列 (11)**: P4×6 (review-gate-pipeline, a3-agent-team-pipeline, a3-multi-agent-content-pipeline, paper-report-writing, content-review-gate, research-paper-writing) · P3×5 (airtable, notion, nano-pdf, maps, linear)

## 5. 无人值守

- `scripts/production-nightly.sh`: daily → 4 workflows → collector → loop（失败可见，绝不静默）
- systemd user units: `hermes-production-nightly.timer` (OnCalendar 09:30, Persistent, ±300s)
- **真实验证**: `systemctl --user start` → exit 0/SUCCESS → 日志 🟢 NIGHTLY COMPLETE，全部 6 环节绿
- units 镜像入仓: `production/systemd/`

## 6. 过程中发现并处理的真实缺陷

| 缺陷 | 处理 |
|:-----|:-----|
| 自研 P3 限流语义 bug（每轮新增≠队列总量，重复运行超发） | 修复 + 撤回超发 5 条 + 幂等复验 0 新增 |
| **Kernel `KERNEL_DUAL_STORE`**: approval_manager (approvals/*.json) 与 proposal_store (proposals.jsonl) 双存储不联通，reject 静默失败 | 记入 error-registry L1；状态变更统一走 `proposal_store.update_status` 并检查返回值；kernel 修复列入 P.2 候选 |
| A3 .venv 缺依赖 | 补装 4 包 → 1074 passed |

## 7. Validation Gates

| Gate | Check | Result |
|:----:|:------|:------:|
| G1 | 3 条项目 workflow SUCCESS + project.* 遥测落盘 | ✅ (6 project events) |
| G2 | 149 技能全覆盖画像 + 未使用清单 | ✅ |
| G3 | ≥1 条真实提案 pending 带 evidence | ✅ (11 条) |
| G4 | systemd timer active + 真实触发一次成功 | ✅ (NEXT 07-19 09:31) |
| G5 | PR merged + event-report | ✅ (见 PR 记录) |

## 8. 持续优化循环 — 运转方式

```
       ┌──────────── 每日 09:30 (systemd timer) ────────────┐
       │                                                     │
  daily check → 项目workflow矩阵 → 遥测落盘 → 使用画像 → 优化提案(pending)
       │                                                     │
       └────── 人工审批 (approve/reject) → 治理执行 ←────────┘
                    ↑ 唯一人在环节点，绝不自动执行
```

---

> **Phase:** P.1 — Production Workflow Expansion
> **Status:** 🟢 COMPLETE — Skill OS 持续优化循环已启动
> **Next:** P.2 候选 — kernel 双存储修复 · 提案审批 UX · adapter 层活跃度治理 (83 未使用)
