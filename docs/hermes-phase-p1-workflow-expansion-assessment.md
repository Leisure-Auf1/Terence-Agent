# Phase P.1 — Production Workflow Expansion Assessment

**Status:** Phase P.1 — Assessment
**Date:** 2026-07-18
**Preflight:** SHA 8e3371c · Risk 🟢 LOW · workspace clean
**Baseline:** P.0 complete (PR #36) — daily entry + self-hosted workflow operational

---

## 1. Objective

P.0 建立了自托管例程（Hermes OS 检查自己）。P.1 将 Hermes 接入**真实项目生产工作流**：

1. 真实项目执行矩阵 — 3 个生产项目各接入真实业务 workflow
2. Skill 使用数据收集 — 打通 3 个数据源，形成使用画像
3. 持续优化循环 — 数据 → 治理提案 → 人工审批 → 改进
4. 无人值守 — systemd user timer 驱动每日例程

## 2. Recon Findings

### 2.1 真实 workflow 候选（已试跑验证）

| Project | Real Workflow | 试跑结果 | 修复动作 |
|:--------|:--------------|:---------|:---------|
| Veritas | `make test` (pytest) | ✅ **558 passed** (1.82s) | 无需修复 |
| A3 | `.venv/bin/pytest tests/ --ignore=tests/integration` | ✅ **1074 passed** (6.49s) | 补装 fastapi/numpy/httpx/scikit-learn（.venv 缺依赖，9 个测试文件无法收集） |
| UCampus | 环境就绪检查（CDP/技能/代理） | 待建 | 账号类操作不入无人值守管道（PII/凭据红线） |

注: A3 `tests/integration/` 需外部 API key，排除在无人值守管道外。

### 2.2 Skill 使用数据源（三源）

| Source | Path | Content |
|:-------|:-----|:--------|
| Hermes 平台使用统计 | `~/.hermes/skills/.usage.json` | **128 技能**: use_count / view_count / patch_count / last_used_at / state |
| Kernel 遥测 | `~/.hermes/runtime/telemetry/events/*.jsonl` | workflow 执行事件 (P.0 起) |
| Registry v1.1 | `skill-manager/skill-registry.json` | 149 条: namespace / scope / lifecycle / status |

### 2.3 优化循环基础设施（已存在，未接线）

- `governance.proposal_engine`: P1-P8 提案类型（P1=MAINTENANCE, P2=HEALTH_REVIEW, P3=ARCHIVE_CANDIDATE…）
- `governance.proposal_store`: create/list/update_status (JSONL)
- `governance.approval_manager`: submit/approve/reject — **requires_approval=True**（人在环中）
- 缺口: 没有从 usage/health 数据到提案的**定期驱动器**

## 3. Execution Plan

| Step | Deliverable | Risk |
|:-----|:------------|:----:|
| P.1.1 执行矩阵 | `production/execution-matrix.yaml` + 3 条项目 workflow (veritas-test-run / a3-test-run / ucampus-readiness) + 真实运行证据 | 🟢 |
| P.1.2 使用数据收集 | `scripts/skill_usage_collector.py` 三源合并 → `production/analytics/skill-usage-YYYY-MM-DD.json` + 汇总报告 | 🟢 |
| P.1.3 优化循环 | `scripts/optimization_loop.py`: usage+health → P1/P3 提案落盘 (pending, 人批) + monitor 集成 | 🟡 |
| P.1.4 无人值守 | systemd user timer: hermes-production-daily.timer (daily + collector + loop) | 🟡 |
| P.1.5 PR + 复盘 | PR → 自审 → squash merge + event-report | 🟢 |

## 4. Validation Gates

| Gate | Check |
|:----:|:------|
| G1 | 3 条项目 workflow 真实运行 SUCCESS，遥测落盘（project.* 命名空间事件首次出现） |
| G2 | usage collector 产出 149 技能全覆盖画像（含 0 使用技能清单） |
| G3 | optimization loop 产出 ≥1 条真实提案（pending 状态，附 evidence，不自动执行） |
| G4 | systemd timer active + 下次触发时间可查 |
| G5 | PR merged + event-report |

## 5. Rollback

- workflow/scripts 均为新增文件，revert PR 即回滚
- systemd timer: `systemctl --user disable --now hermes-production-daily.timer`
- 提案只落 pending，不触碰任何技能文件

---

> **Phase:** P.1 — Production Workflow Expansion
> **Status:** Assessment complete → executing P.1.1-P.1.5
