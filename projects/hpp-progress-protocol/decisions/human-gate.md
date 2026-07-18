# Decision Record — HPP v0.1 Human Gate（2026-07-18/19）

## Gate 1 — 提案批准（APPROVED WITH CONDITIONS）

- W1 kernel progress capability：批准（tracker/watchdog/store/manifest/单测 + execution_id 生命周期校验 started→updated*→terminal）
- W2 wrappers + monitor：批准（progress-watch.sh + docker_build/pytest/migration/download 探针 + production-monitor 集成）
- W3 registry v1.2：批准（可选 observability: heartbeat/progress/eta；149 skills 兼容，零迁移）
- **W4 executor 钩子：PAUSED** — 明令禁止修改 executor hooks，W1-W3 验证后单独提案
- 边界：仅 Hermes Framework；禁止 A3 / Veritas-Core / 业务仓库改动
- 流程：每 Wave 汇报 files/tests/telemetry evidence/rollback；不自动 merge，PR 等 Human Gate

## 实施中的工程决断（在授权框架内）

1. **独立事件流**：progress 事件写 progress-events/（非 events/）。
   理由：metrics_aggregator 把 events/ 每条当 ExecutionRecord 统计成功率，
   混流将污染 daily 指标——以"Maintain existing telemetry compatibility"条款优先。
2. **watchdog 直写快照**：属主进程可能已死，监督者不能依赖 tracker 实例守卫；
   escalation 事件带 emitted_by=progress_watchdog 以示来源。
3. **daily 校验重定向属 W3 范围**：production_daily.py 硬编码 v1.1/1.1.0，
   registry bump 后不改校验 = 人为制造 daily 红灯，故一并更新（框架内脚本）。

## 回滚路径

- W1/W2：删除新增文件（tracker/watchdog/cli/watch.sh）+ 还原 manifest + monitor 区块
- W3：registry 顶层字段还原 1.1.0/1.1 + fields 去掉 observability + daily 校验还原 + 双副本同步
- 每 Wave 独立 commit（cb7ca7d / 2e057c2 / 5330914），可逐个 revert
