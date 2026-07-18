# Proposal: HPP v0.2 — Executor Observability Hook (W4)

- ID: prop-hpp-v0.2-executor-hook
- Date: 2026-07-19
- Status: PENDING HUMAN GATE — 提案态，零实施（executor.py 至今未被触碰）
- Precondition: HPP v0.1 ACTIVE（merge `50c057d`），W1-W3 生产验证中
- Scope: 仅 `kernel/runtime/executor.py` + `kernel/config/kernel_config.yaml` + 新增 hook 模块
- Forbidden inherited: A3 / Veritas-Core / 业务仓库零接触

---

## 1. Hook Architecture

现状锚点：`executor.execute_skill()` 是四段直线管道
（permission → context_load → execute-with-retry → release），
无任何执行中遥测出口。

设计：**包裹式 ProgressScope，不改管道语义**——

```
execute_skill(...)
  ├─ permission / context_load          （不动）
  ├─ scope = ProgressScope.maybe_attach( ← 新增，唯一插入点 ×2
  │     execution_id, skill_entry, flag)
  │     · flag off        → NullScope（零对象，零开销）
  │     · obs.progress    → 立即 start()
  │     · obs.heartbeat=auto → DeferredScope：仅启动计时，
  │       越过 LONG_TASK_THRESHOLD_S(300s) 才补发 started+heartbeat
  ├─ retry 循环             （不动；attempt 变化时 scope.note_retry()）
  └─ 返回前 scope.finish(status)          ← 插入点 ×2（成功/失败路径）
```

- 新模块 `kernel/runtime/progress_scope.py`（hook 逻辑全部住在这里，
  executor.py 只加 3-4 行调用）；心跳由 daemon 线程驱动
  （interval 取 skill observability / 默认 60s），线程仅调用
  `tracker.heartbeat()`，不触碰执行状态。
- 身份来源：execution_id 复用 executor 现有生成；skill_id/namespace
  从 registry 条目取；`get_observability()`（v0.1 已交付）为唯一配置读口。

## 2. Failure Isolation

铁律：**hook 故障永不影响技能执行**（对齐 Veritas RuntimeHook 隔离原则）。

1. ProgressScope 所有公开方法整体 try/except → 吞异常 + 单次告警日志。
2. 心跳线程 daemon 化 + 内部异常吞噬；线程死亡不影响主流程，
   watchdog 会以 STALE_HEARTBEAT 兜底可见性。
3. 存储熔断：连续 3 次 emit 失败（磁盘满/权限）→ 本次执行内降级为
   NullScope，记一条 `progress.warning(EMITTER_CIRCUIT_OPEN)`（尽力而为）。
4. 生命周期违规（ProgressLifecycleError）按 bug 处理：吞掉 + 计数，
   绝不向 executor 冒泡。
5. finish() 兜底：即使 scope 内部状态损坏，执行结果照常返回。

## 3. Performance Budget

| 场景 | 预算 | 机制 |
|:--|:--|:--|
| flag=off | **0 开销**（一次 dict 读 + NullScope） | 零对象模式 |
| 短任务 (<5min, heartbeat=auto) | **0 次磁盘写** | DeferredScope 只持有计时器，阈值前不落盘 |
| 长任务 | ≤1 快照写+1 事件行 / interval(默认60s) + start/terminal 各 1 | 天花板：数 KB JSON/min |
| 单次 emit | < 5ms P95（本地 fs 原子写） | 已有 W1 实现实测 μs-ms 级 |
| 总量 | 对 >5min 任务 wall-time 开销 < 0.1% | 基准测试入库（见 §6） |

验收基准：10k 次 update 合成压测 < 3s；flag=off 路径 microbenchmark
与基线差异 < 1μs/call。

## 4. Feature Flag Strategy

三态开关，默认全暗：

```yaml
# kernel/config/kernel_config.yaml
progress:
  executor_hook: "off"        # off | shadow | on
  heartbeat_interval_s: 60
  long_task_threshold_s: 300
```

- **off**（默认，W4 合并即此态）：NullScope，行为与 v0.1 完全一致。
- **shadow**：全逻辑执行，但写入 `progress-shadow/` 隔离目录，
  不进正式 store、不被 monitor/daily 消费——纯验证态。
- **on**：正式启用。
- 覆盖链（高→低）：env `HERMES_PROGRESS_HOOK`（紧急开关）>
  kernel_config > skill observability 字段 > 内置默认。
- 升级路径即金丝雀计划：off → shadow(≥3 天，比对 shadow 流与预期) →
  on for hermes.core.*（14 skills）→ on 全量。每步 Human Gate。

## 5. Rollback Plan

| 层级 | 手段 | 时效 |
|:--|:--|:--|
| L0 行为回滚 | `HERMES_PROGRESS_HOOK=off`（env，无需部署） | 即时 |
| L1 配置回滚 | kernel_config executor_hook: off | 即时 |
| L2 代码回滚 | revert 单 commit（executor 仅 3-4 行插入 + 独立 scope 模块） | 分钟级 |
| 数据 | progress store 追加式产物无害，无需清理；shadow 目录可整删 |
| 验证 | 回滚后跑 kernel suite + production_daily，期望与 v0.1 基线一致 |

## 6. Test Strategy

1. **单元**（新增 test_progress_scope.py）：
   - NullScope 零行为；DeferredScope 阈值前零落盘（注入时钟）
   - hook 异常注入：tracker.start/update/finish 抛错 → execute_skill 结果不变
   - 熔断：连续 emit 失败 → 降级 NullScope + 单次 warning
   - flag 矩阵 off/shadow/on × observability 声明组合
2. **集成**：execute_skill 全管道 + 模拟长任务（注入时钟越阈值）→
   快照/事件断言；shadow 态断言正式 store 零写入。
3. **性能**：off 路径 microbenchmark；10k update 压测；CI 阈值断言。
4. **回归**：现有 kernel 25 测试零修改通过 + production_daily ALL GREEN
   （off 态合并后必须与 v0.1 逐字节等价的 daily 结果）。
5. **金丝雀验收**：shadow 3 天 → 比对 shadow 事件与 watch-wrapper
   人工挂载结果的一致性 → 逐级放量（见 §4）。

---

## 待 Human Gate 裁决

- [ ] 批准 v0.2 实施（默认 flag=off 合并）
- [ ] 金丝雀节奏确认（shadow ≥3 天 → core 14 → 全量）
- [ ] 性能预算阈值确认（<0.1% / P95 5ms / off 态 <1μs）
