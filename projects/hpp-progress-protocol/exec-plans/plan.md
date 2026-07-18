# Exec Plan — HPP W1–W3

## W1 Kernel Progress Capability
1. kernel/telemetry/progress_tracker.py
   - ProgressTracker: start/update/heartbeat/warning/complete/block
   - 生命周期强校验: started → updated* → terminal(COMPLETED|FAILED|BLOCKED)
     违规抛 ProgressLifecycleError
   - 快照原子写 (tmp + os.replace) → progress/<execution_id>.json
   - 事件 JSONL → progress-events/YYYY-MM-DD.jsonl (append-only, 同 event_store 模式)
   - speed: 滑动窗口样本 (snapshot.meta.samples, 最近10点) → 跨进程可续算
   - ETA: (total-done)/speed, confidence 按样本数分级
   - resume(execution_id): 跨进程恢复 (CLI/watch 脚本用)
   - get_observability(entry): W3 读端默认值兜底
2. kernel/telemetry/progress_watchdog.py
   - scan(): RUNNING/WARNING 快照心跳检查
     >2×interval → WARNING + progress.warning(STALE_HEARTBEAT)
     >5×interval → BLOCKED + progress.blocked(HEARTBEAT_LOST)
3. kernel/tests/test_progress_tracker.py / test_progress_watchdog.py
4. kernel-manifest.json: telemetry.files += 2, capabilities += hermes.core.telemetry.progress
5. 部署同步 ~/.hermes/kernel (byte-sync) + 真实 store 冒烟

## W2 Wrappers + Monitor
1. kernel/telemetry/progress_cli.py (start/update/complete/block/snapshot/list/watchdog)
2. scripts/progress-watch.sh: 通用采样循环 --probe, 内置4类探针模板
3. scripts/production-monitor.sh: 新增 Long-Task 区块 (快照列表 + watchdog.scan)
4. 真实证据: 对正在运行的 docker build 挂 watch (docker_build 探针实战)

## W3 Registry v1.2
1. skill-registry.json (repo+deployed): version 1.2.0, schema_version 1.2,
   fields += observability; 149 条目零改动
2. kernel-manifest compatibility.registry: v1.1 → v1.2 (repo+deployed)
3. scripts/production_daily.py: 校验目标改 1.2.0/v1.2
4. 回归: production_daily.py 全绿 + registry 双副本 sha256 一致

## 收尾
- event-report/2026-07-18.md 条目 + 复盘
- push → PR (base=main) → 不 merge, 等 Human Gate
