# Phase P.0 — Production Bootstrap Assessment

**Status:** Phase P.0 — Assessment
**Version:** 1.0
**Date:** 2026-07-18
**Phase:** P — Production Operation
**Preflight:** SHA 98959b5 · Risk 🟡 MEDIUM
**Audience:** Governance Reviewer · Production Operator

**Governance Authority:**
- Governance Constitution v1.0 (FROZEN per C.5)
- Registry v1.1 Release (Wave 4)
- Phase B.6.5 Kernel Production Validation (60/60 PASS)
- Phase C.4 Production Readiness Report (🟢 GREEN GO)

---

## 1. Assessment Objective

Phase P 的目标是让 Hermes Skill Operating System 从"验证完成"进入"真实生产运营"。
P.0 Production Bootstrap 需要建立四项基础设施：

1. **每日生产入口** — 每天开始工作时的标准启动流程
2. **项目运行配置** — 各生产项目接入 Kernel 的 runtime config
3. **真实 workflow 接入** — 至少一条真实工作流通过 Kernel 管道执行
4. **运行监控** — 每日健康检查与遥测汇总

## 2. Current Production Asset Inventory

| Asset | Location | State | Persistence |
|:------|:---------|:------|:-----------:|
| Kernel runtime (6 modules, 34 files) | `~/.hermes/kernel/` | ✅ B.6.5 validated | ⚠️ 未版本控制 |
| Runtime storage | `~/.hermes/runtime/` | ✅ active (state/telemetry/health/governance) | ⚠️ 未版本控制 |
| Registry v1.1 (149 entries) | `/tmp/hermes-wave4-snapshots/registry-v1.1.json` | ✅ valid JSON, 18 fields | 🔴 **易失 (/tmp)** |
| Registry v1.0 (repo copy) | `skill-manager/skill-registry.json` | ⚠️ 15 entries, 2026-06-05 | ✅ git |
| Governance docs (Phase A/B/C) | `docs/hermes-*.md` × 55 | ✅ content complete | 🔴 **untracked, 未提交** |
| Wave snapshots/backups | `/tmp/hermes-wave*-snapshots/` | ✅ present | 🔴 **易失 (/tmp)** |

## 3. Critical Findings

### 🔴 F1 — Registry v1.1 生产副本仅存于 /tmp

Wave 4 宣布 "Registry v1.1 — PRODUCTION RELEASE"，但 149 条的 v1.1 文件只存在于
`/tmp/hermes-wave4-snapshots/registry-v1.1.json`。`/tmp` 在重启后清空 —— **一次重启即可抹掉
Phase A 全部迁移成果**。仓库内的 `skill-manager/skill-registry.json` 仍是 v1.0.0（15 条，2026-06-05）。

**Impact:** CRITICAL — 生产资产无持久化副本。
**P.0 Action:** 将 Registry v1.1 提升为仓库正式文件并同步部署到 Kernel 路径。

### 🔴 F2 — 55 份 Phase A/B/C 治理文档全部悬空（untracked）

`docs/hermes-*.md` 共 55 份（Wave 0-4、B.6.0-6.5、C.0-C.4 全部报告）从未提交。
对应 Pitfall 2/3 模式：产出悬空、event-report 缺失。

**Impact:** HIGH — 治理记录不可追溯，违反框架流程。
**P.0 Action:** 随 P.0 PR 一并纳入版本控制。

### 🟡 F3 — Kernel 代码未版本控制

`~/.hermes/kernel/` 34 个文件（含 6 个运行时模块）无 git 备份。
**P.0 Action:** 镜像至 `kernel/` 仓库目录（部署路径保持 `~/.hermes/kernel/` 不变，仓库为 source of truth）。

### 🟡 F4 — 无生产入口与监控例程

Kernel 已验证但没有"每天怎么用"的入口：无 daily bootstrap 脚本、无健康检查例程、
无遥测汇总、AGENTS.md 缺失（preflight [6/8] 确认）。
**P.0 Action:** 建立 `scripts/production-daily.sh` + AGENTS.md + 监控例程。

## 4. Production Projects (from C.0)

| Project | Namespace | Manifest | Real Workflow Candidate |
|:--------|:----------|:--------:|:------------------------|
| A3 Multi-Agent System | `project.a3.*` | C.0 defined | 教学内容生成管线 |
| Veritas-Core | `project.veritas.*` | C.0 defined | 结构化测试运行 |
| UCampus | `project.ucampus.*` | C.0 defined | 课程任务自动化 |

## 5. P.0 Execution Plan (proposed)

| Step | Deliverable | Risk |
|:-----|:------------|:----:|
| P.0.1 资产固化 | Registry v1.1 → `skill-manager/skill-registry.json`（备份旧版）；Kernel → `kernel/` 仓库镜像；快照脱离 /tmp | 🟡 |
| P.0.2 每日生产入口 | `scripts/production-daily.sh`（preflight → kernel boot check → health scan → telemetry summary）+ `AGENTS.md` | 🟢 |
| P.0.3 项目运行配置 | `production/projects/{a3,veritas,ucampus}.runtime.yaml` — 项目↔Kernel 接入配置 | 🟢 |
| P.0.4 真实 workflow 接入 + 监控 | 1 条真实 workflow 通过 resolver→lifecycle→executor→telemetry 全管道执行，产生真实遥测；`scripts/production-monitor.sh` 输出每日运行报告 | 🟡 |
| P.0.5 PR + event-report | feat/phase-p0-production-bootstrap → PR → squash merge；event-report 复盘 | 🟢 |

## 6. Validation Gates (P.0)

| Gate | Check |
|:----:|:------|
| G1 | Registry v1.1 在 git 中，`json.load` 通过，149 entries，forbidden_pairs=5 |
| G2 | Kernel 仓库镜像与 `~/.hermes/kernel/` diff = 0 |
| G3 | `production-daily.sh` 全绿运行一次（真实输出，非模拟） |
| G4 | 真实 workflow 执行产生 telemetry 事件（`~/.hermes/runtime/telemetry/events/`） |
| G5 | 监控报告生成于 `production/reports/` |
| G6 | PR merged + event-report 提交 |

## 7. Rollback

- Registry: 旧 v1.0 副本保留为 `skill-manager/skill-registry.v1.0.backup.json`，单命令还原
- Kernel: 仓库镜像为只读快照，不改动 `~/.hermes/kernel/` 现行文件
- 所有变更走 PR，可 revert

---

> **Phase:** P.0 — Production Bootstrap
> **Status:** Assessment complete — awaiting approval to execute P.0.1–P.0.5
