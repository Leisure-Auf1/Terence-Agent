# AGENTS.md — Terence-Agent 入口索引

> **任何 Agent 进入本仓库工作前，先读这份文件。**
> 铁律第 0 步：`bash scripts/check-preflight.sh` — 不跑 preflight 不允许开始。

## 这是什么仓库

Terence-Agent 是 **Hermes Skill Operating System** 的治理与生产运营仓库：
- **治理体系**: Governance Constitution v1.0 (FROZEN) · Registry v1.1 (149 skills) · C.3 三层命名空间 (Core/Adapter/Project)
- **Kernel**: 6 个运行时模块 (resolver → lifecycle → executor → telemetry → health → governance)，部署于 `~/.hermes/kernel/`，仓库 `kernel/` 为版本控制镜像
- **Agent Team**: guidance → developer → debugger → executor → logger

## 每日生产入口 (Phase P)

```bash
bash scripts/production-daily.sh          # 完整: preflight + kernel 检查 + 日报
bash scripts/production-daily.sh --quick  # 快速: 只跑 kernel 检查
python3 scripts/production_workflow.py <workflow>   # 执行生产 workflow（走 Kernel 全管道）
```

日报输出: `production/reports/daily-YYYY-MM-DD.md`

## 目录地图

| 目录 | 用途 |
|:-----|:-----|
| `AGENTS.md` | 本文件 — Agent 入口 |
| `scripts/` | preflight / 每日生产入口 / workflow 运行器 |
| `kernel/` | Hermes Kernel 镜像（source of truth，部署至 `~/.hermes/kernel/`） |
| `skill-manager/skill-registry.json` | **Registry v1.1 正本**（149 entries · 与部署版 `~/.hermes/skills/devops/skill-manager/references/` 保持同步） |
| `production/` | 生产运营: 项目 runtime 配置 · workflow 定义 · 每日报告 |
| `governance-archive/` | Wave 0-4 迁移快照存档（从 /tmp 抢救固化） |
| `docs/` | 治理文档全集 (Phase A/B/C/P 报告、架构、规范) |
| `projects/` | 项目工作区（SPEC + exec-plans + decisions + outputs） |
| `agent-team/` | 5 个 Agent 角色定义 |
| `event-report/` | 每日事件日志（复盘必写） |
| `error-registry/` | 已知错误及修复方案 |
| `architecture-constraints/` | 架构约束（层级/级联/命名） |

## 强制工作流（跳过 = 违规）

```
① bash scripts/check-preflight.sh
② projects/<name>/ 标准结构 (SPEC.md + exec-plans/ + decisions/ + outputs/)
③ git checkout -b feat/<name> main
④ commit（清晰分型: feat/fix/docs）
⑤ push → ⑥ gh pr create → 自审 → squash merge → 删分支
⑦ event-report/YYYY-MM-DD.md 更新
⑧ 复盘（Feedforward + Feedback 配对）
```

## 关键规则

- 🔴 **PII 零容忍** — 任何持久化文件不得含真实姓名/学号/电话；用 `[姓名]`/`[学号]` 占位
- 🔴 **Registry 修改** — 只用 Python json.load/dump，先备份到 /tmp，改后验证 149 条 + forbidden_pairs=5
- 🔴 **命名空间边界** — Core→Project ❌ · Adapter→Project ❌ · Project→Core/Adapter ✅
- 🟡 **生产资产不落 /tmp** — /tmp 只作临时备份，正本必须入 git
- 🟡 **可见执行** — 用户需要看到过程的任务走 terminal，不走 delegate_task

## Phase 索引

| Phase | 状态 | 关键文档 |
|:------|:----:|:---------|
| A — Governance Migration (Wave 0-4) | ✅ | `docs/hermes-registry-v1.1-release-report.md` |
| B — Kernel Runtime (B.6.0-6.5) | ✅ | `docs/hermes-phaseB6.5-production-validation-result.md` |
| C — Production Readiness (C.0-C.4) | ✅ | `docs/hermes-phase-c-production-readiness-report.md` |
| P — Production Operation | 🟢 运行中 | `docs/hermes-phase-p0-production-bootstrap-assessment.md` |
