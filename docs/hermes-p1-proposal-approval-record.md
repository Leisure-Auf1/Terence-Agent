# P.1 治理提案审批执行记录

**Date:** 2026-07-18
**审批人:** 用户（人在环唯一节点）
**裁决:** 全部批准（11/11）
**执行分支:** feat/p1-proposal-execution
**Preflight:** SHA 56f8529 · 🟢 LOW

---

## 1. 裁决范围

| 组 | 提案 | 裁决 | 执行动作 |
|:---|:-----|:----:|:---------|
| P3×5 | airtable · notion · nano-pdf · maps · linear | ✅ 批准 | Registry `lifecycle→archived`（文件保留，可逆） |
| P4×6 | review-gate-pipeline · content-review-gate · a3-agent-team-pipeline · a3-multi-agent-content-pipeline · paper-report-writing · research-paper-writing | ✅ 批准 | 迁移确认（canonical 健在）+ 宽限期维持至 2026-08-01 + R5 规则上线 |

## 2. P3 执行详情（Registry 修改，按 migration 规范）

- 备份: `/tmp/hermes-p1-exec-snapshots/registry.pre-p3-archive.json` (pre-SHA `08c7b0a1…`)
- 修改: 部署版 5 条 `lifecycle: active→archived`, `status→archived`, 字节同步仓库版 (SHA `234d3d47…`)
- 验证: 149 条不变 · forbidden_pairs=5 · mount_strategies=3 · scopes 不变 (core14/adapter123/project12)
- resolver 实测: airtable/notion/maps 相关意图 **0 命中 archived 技能** ✅
- 回滚: 单命令 `cp` 还原，备份完整性已验证

## 3. P4 执行详情

- canonical 健在验证: content-review-pipeline / a3-multi-agent-pipeline / academic-writing — 全部 `active/ok` + SKILL.md 存在 ✅
- 宽限期: 维持 Wave 1 既定 2026-08-01，到期由 R5 自动转 P3 归档流程
- **R5 规则上线** (optimization_loop.py): deprecated 且 `grace_period_ends` 已过 → P3（共享队列限额 5，历史裁决排除）

## 4. 提案状态流转（权威存储 + 逐条断言）

11 条全部 `pending → approved → executable`（proposal_store.update_status，逐条检查 `updated=True`，KERNEL_DUAL_STORE 教训落实）。终态: pending=0, executable=11。

## 5. 附带修正

- 5 条系统撤回记录（限流 bug 超发）补写 `rejected_by=system-withdrawal` 标记 —— 撤回≠人工裁决，
  历史索引不再永久排除，petdex 等 5 技能恢复候选资格
- 复跑验证: 循环滚动补位下一批 5 条 P3 候选（petdex / chaoxing-homework / wps-office-cn-install /
  teams-meeting-pipeline / google-workspace），进入下轮人工审批队列

## 6. 验证

| Check | Result |
|:------|:------:|
| Registry 部署版=仓库版 (SHA-256) | ✅ |
| resolver 跳过 archived | ✅ |
| daily check 26 项 | 🟢 ALL GREEN |
| 已裁决提案不重提（幂等） | ✅ (跳过 11) |
| R5 触发数（宽限期未到） | 0 ✅ |

---

> **下一批待审:** 5 条 P3 (petdex, chaoxing-homework, wps-office-cn-install, teams-meeting-pipeline, google-workspace)
> ⚠️ 注意: chaoxing-homework 属 project.ucampus.chaoxing 且在 ucampus.runtime.yaml 技能清单中，裁决时需权衡
