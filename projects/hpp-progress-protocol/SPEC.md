# SPEC — Hermes Progress Protocol (HPP v0.1) W1–W3

## 背景
长任务（docker build / test suite / deployment / migration）执行期间零遥测
（collector.py 仅终态记录）→ black-box execution problem。
实证：2026-07-18 Docker Release 构建 ~60min 全程人工采样。

## Human Gate 决议（2026-07-18）
APPROVED WITH CONDITIONS：W1/W2/W3 批准；W4（executor 钩子）PAUSED，
待 W1-W3 验证后另行提案。范围仅 Hermes Framework，禁止 A3/VC/业务仓库改动。
不自动 merge，每 Wave 汇报（files/tests/telemetry evidence/rollback）。

## 交付物
- W1: kernel/telemetry/progress_tracker.py + progress_watchdog.py
      + progress store (~/.hermes/runtime/telemetry/progress[-events]/)
      + kernel-manifest capability 注册 + 单元测试
      + execution_id 生命周期校验: started → updated* → terminal
- W2: scripts/progress-watch.sh（docker_build/pytest/migration/download 探针）
      + kernel/telemetry/progress_cli.py + production-monitor 集成
- W3: Registry schema v1.2（可选 observability: heartbeat/progress/eta）
      + 149 skills 零迁移兼容 + daily 校验脚本同步

## 兼容性红线
1. progress 事件走独立流 progress-events/（不混入 events/，避免污染
   metrics_aggregator 的 success_rate 统计）— 对提案 §3.2 的兼容性修正。
2. event_store.py / collector.py / metrics_aggregator.py 零修改。
3. executor.py 零修改（W4 PAUSED）。
4. Registry 149 条目字节不动，仅顶层元数据 bump。

## 验收
- 单测全绿（tmp store 隔离，不污染真实 runtime）
- 真实 telemetry 证据：progress 快照 + progress-events JSONL
- production_daily.py 26 项检查在 W3 后仍 ALL GREEN
- 回滚：删除新增文件 + 还原 manifest/registry 顶层字段（每 Wave 独立）
