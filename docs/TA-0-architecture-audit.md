# Phase TA-0 架构审查报告 — Terence-Agent

> **审查日期**: 2026-07-18
> **审查 SHA**: 004f90c
> **分支**: main (clean working tree)
> **审查类型**: 只读架构审计（架构冻结前）
> **报告作者**: AI Agent (Hermes)

---

## 1. Current State — 当前状态

### 1.1 仓库定位

Terence-Agent 是一个 **Prompt Repository + 架构治理中枢 (Architecture Governance Hub)**。它不是运行时框架（不包含可执行 Agent 代码），而是定义规则、角色、流程和约束的元级别仓库。核心运行时代码分散在 Veritas-Core（框架）和 A3-Multi-Agent-System（应用），但治理逻辑 100% 以 Markdown 提示词形式存在于此仓库中。

### 1.2 标注目录树

```
Terence-Agent/  (SHA: 004f90c, main, clean)
├── README.md                                 [DOC] 仓库入口，185行，架构全景图
│
├── architecture-constraints/                 [CORE] 架构治理核心
│   └── README.md                           512行 — 层级约束/上下文裁剪/错误级联/复盘流程/隐私规则
│
├── error-registry/                           [CORE] 错误知识库
│   └── README.md                           132行 — 38条错误记录 (L0致命/L1可绕行/L2环境/L3信息)
│
├── agent-team/                               [CORE] Agent角色定义
│   ├── guidance-agent/README.md            1010行 — 指挥官：5阶段推理 + Agent间通信协议(JSON)
│   ├── agent-developer/README.md            176行 — 开发工程师：编码+PR流程
│   ├── agent-debugger/README.md             190行 — 调试工程师：纠错+error-registry联动
│   ├── agent-executor/README.md              82行 — 实操工程师：浏览器/桌面/CLI
│   └── agent-logger/README.md               186行 — 日志工程师：preflight→progress→复盘
│
├── skill-manager/                            [TOOL] 技能路由
│   ├── README.md                           188行 — 技能管理器Agent定义
│   └── skill-registry.json                  14技能 + mount策略 + forbidden_pairs
│
├── event-report/                             [MEMORY] 操作历史
│   ├── README.md                            76行 — 规范定义
│   ├── 2026-06-14.md                       344行 — 首日日志
│   ├── 2026-06-26.md                        67行
│   ├── 2026-07-12.md                       156行
│   ├── 2026-07-13.md                       181行
│   ├── 2026-07-16.md                        29行
│   └── 2026-07-17.md                       470行 — 最活跃日 (Phase 5.4-5.7 等)
│
├── task-progress/                            [MEMORY] 跨会话进度
│   ├── README.md                           252行 — 进度追踪系统规范
│   ├── projects/ucampus/                     ucampus进度快照
│   └── tasks/                                3个历史任务进度目录
│
├── projects/                                 [EXPERIMENT/WORKFLOW] 项目快照
│   ├── a3-multi-agent-system/               A3系统文档+spec+checkpoints+outputs+test
│   │   ├── docs/                           23个设计/规划/报告文档 (竞争相关)
│   │   ├── checkpoints/                    12个阶段检查点
│   │   └── outputs/                        教程+测试代码产出
│   ├── campus-task/                         **独立Git仓库** — Python包 (含CI/CD/.git/)
│   │   ├── src/                            Py包: ai_harness, task_model, task_service, task_storage
│   │   ├── tests/                          pytest测试
│   │   ├── .github/workflows/              CI配置
│   │   └── SPEC.md, DESIGN.md, CI_SETUP.md 完整工程文档
│   ├── computer-setup/                      硬件配置脚本 (udev规则+热插拔)
│   ├── lab-report/                          实验报告docx输出+ADR+SPEC
│   │   ├── outputs/                        8个.docx实验报告
│   │   └── decisions/                      ADR-001
│   └── ucampus/                             U校园自动化脚本 (.js) + 进度
│
├── scripts/                                  [TOOL] 可执行检查
│   └── check-preflight.sh                 355行 — 9步preflight门控 (SHA/风险/PII/熵/...)
│
├── sync.sh                                   [TOOL] Skills→Git同步脚本 (cp ~/.hermes/skills→repo)
│
├── .hermes/                                  [WORKFLOW] Preflight缓存 (预生成，不入Git)
│
└── .gitignore                                [CONFIG] 排除preflight日志+campus-task子仓库
```

### 1.3 关键指标

| 指标 | 数值 |
|:-----|:-----|
| 顶层目录/文件 | 12 entries |
| Markdown 文件 | ~98 个 |
| Python 文件 | ~82 个（主要来自 projects/campus-task） |
| 总 Markdown 行数 | ~7,132 行（不含 a3/campus-task 项目子目录） |
| Agent 定义 | 5 个（guidance/developer/debugger/executor/logger） |
| 错误记录 | 38 条（L0:4, L1:8, L2:5, L3:21） |
| Skill 注册 | 14 个（JSON registry） |
| 架构约束 | 13 项核心原则 + 6 项 Harness 附加 + 层级/级联/复盘规则 |
| Event 记录 | 6 个日期文件，总计 ~1,323 行 |
| Projects | 5 个子目录（1个含独立.git） |

### 1.4 仓库演化时间线

```
2026-06-05  → 仓库创建，第一批event-report/error-registry/skill-manager
2026-06-14  → Agent Team框架导入（architecture-constraints成形）
2026-06-26  → computer-setup项目加入
2026-07-12  → sync.sh 出现，A3 pipeline开始
2026-07-16  → Docker/Deployment 阶段
2026-07-17  → 高产出日：Runtime Recovery/Lifecycle/Benchmark/Explainability
2026-07-18  → [STOP] 架构冻结 — 本审查执行
```

---

## 2. Architecture Diagram — 架构全景图

### 2.1 当前架构 (As-Is)

```
                              ┌──────────────────────────────────────┐
                              │          Terence-Agent               │
                              │      Architecture Governance Hub     │
                              │                                      │
                              │  ┌────────────────────────────────┐  │
                              │  │   architecture-constraints     │  │
                              │  │   (13 核心原则 + 层级/级联)     │  │
                              │  └──────────┬─────────────────────┘  │
                              │             │  governs               │
                              │  ┌──────────▼─────────────────────┐  │
                              │  │        agent-team/              │  │
                              │  │  ┌─────────────────────────┐   │  │
                              │  │  │   Guidance Agent         │   │  │
                              │  │  │   Phase -1→0→1→2→3→4→5  │   │  │
                              │  │  └───┬───┬───┬───┬─────────┘   │  │
                              │  │      │   │   │   │              │  │
                              │  │  ┌───▼─┐ ┌▼───▼─┐ ┌▼──────┐   │  │
                              │  │  │ Dev │ │ Debug│ │Execute │   │  │
                              │  │  └──┬──┘ └──┬───┘ └───┬───┘   │  │
                              │  │     │       │         │       │   │
                              │  │  ┌──▼───────▼─────────▼───┐   │  │
                              │  │  │      Logger            │   │  │
                              │  │  └────────────────────────┘   │  │
                              │  └───────────────────────────────┘  │
                              │                                      │
                              │  ┌────────────┐  ┌────────────────┐  │
                              │  │  error-    │  │  skill-manager │  │
                              │  │  registry  │  │  + JSON reg.   │  │
                              │  │  (38条)    │  │  (14 skills)   │  │
                              │  └─────┬──────┘  └───────┬────────┘  │
                              │        │                  │          │
                              │  ┌─────▼──────────────────▼───────┐  │
                              │  │         event-report/          │  │
                              │  │     (6 日期文件, ~1323行)       │  │
                              │  └──────────────┬─────────────────┘  │
                              │                 │                    │
                              └─────────────────┼────────────────────┘
                                                │
                         ┌──────────────────────┼──────────────────────┐
                         │                      │                      │
                    ┌────▼─────┐          ┌─────▼──────┐      ┌───────▼───────┐
                    │ projects/│          │   scripts/ │      │ .hermes/      │
                    │  (5个)   │          │ preflight  │      │ preflight     │
                    │          │          │   .sh      │      │ cache + cp    │
                    └──────────┘          └────────────┘      └───────────────┘

                             EXTERNAL DEPENDENCIES
                         ┌──────────────────────────────┐
                         │                              │
                    ┌────▼──────┐              ┌───────▼────────┐
                    │Veritas-   │              │ A3-Multi-Agent  │
                    │Core       │◄─────────────│ System          │
                    │(Framework)│  depends on  │ (Application)   │
                    │558 tests  │              │ 1130 tests      │
                    │pip install│              │                 │
                    └───────────┘              └─────────────────┘

       LEGEND:
       ─── 治理/约束关系 (Governance)
       ─── 依赖关系 (Dependency)
       所有 Terence-Agent 内部组件均为纯 Markdown 提示词 — 无运行时代码
```

### 2.2 关键架构特征

```
[v] 角色分离: Guidance → Developer/Debugger/Executor/Logger 5个Agent清晰分工
[v] 错误知识库: error-registry 38条，L0-L3四级分类 + 修复方案
[v] 约束体系: 13核心原则 + Harness Engineering附加约束 + 层级/级联规则
[v] Preflight门控: 9步机械检查（SHA/风险/PII/熵/...）
[v] Sync机制: sync.sh 从 ~/.hermes/skills → Git repo 同步
[x] 零运行时: 所有规则以Markdown提示词形式存在，无可执行约束引擎
[x] 无状态机: Guidance Agent 5阶段纯文本推理，无程序化状态管理
[x] Skills在别处: skill-manager仅注册表，实际skill定义在 ~/.hermes/skills/
```

---

## 3. Workflow Analysis — 工程Agent Workflow分析

### 3.1 已有能力

| 能力 | 状态 | 实现方式 |
|:-----|:----:|:---------|
| 阶段定义 | [v] | guidance-agent Phase -1~5 推理框架 + Preflight |
| 角色分工 | [v] | 5个Agent README，明确角色边界+技能映射 |
| 错误管理 | [v] | error-registry 38条 L0-L3 |
| 约束治理 | [v] | architecture-constraints 512行 |
| Preflight门控 | [v] | check-preflight.sh 355行 |
| 操作日志 | [v] | event-report/ 6个日期文件 |
| 进度追踪 | [v] | task-progress/ 跨会话恢复 |
| 技能路由 | [v] | skill-manager + skill-registry.json |
| Agent间通信协议 | [v] | JSON消息格式定义 (guidance-agent S2.1.1) |
| 上下文重置 | [v] | architecture-constraints S0.3.2 |
| PR流程约束 | [v] | architecture-constraints S0.3.4 |
| 复盘流程 | [v] | architecture-constraints S7 9步清单 |

### 3.2 缺失能力

| 能力 | 状态 | 影响 | 说明 |
|:-----|:----:|:-----|:-----|
| 状态机实现 | [x] | HIGH | 无 AgentState enum/RuntimeEngine class — 阶段靠文本描述 |
| Workflow引擎 | [x] | HIGH | 无可编程DAG/节点编排器 |
| Phase运行时管理 | [x] | HIGH | Phase变迁无强制执行 — 完全依赖Agent自觉 |
| 权限约束执行 | [x] | HIGH | 角色边界仅文本约束，无代码级gateway |
| Trace系统 | [x] | HIGH | 无结构化trace收集 — event-report是自由文本 |
| 通信协议执行 | [x] | MEDIUM | JSON消息格式已定义但无实际消息队列管理 |
| CI/CD (本仓库) | [x] | MEDIUM | 无GitHub Actions |
| Skill规范验证 | [x] | MEDIUM | registry无schema验证，一致性靠sync.sh |
| TEST阶段 | [x] | MEDIUM | 本仓库无可执行测试 |
| DESIGN文档化 | [x] | LOW | 无docs/decisions/目录 |
| RELEASE管理 | [x] | LOW | 无版本号/CHANGELOG |
| SCAN自动化 | [x] | LOW | Preflight靠手动运行 |

### 3.3 核心缺口总结

Terence-Agent 在 **概念设计层面** 覆盖了工程 Agent Workflow 的大部分阶段，但所有实现均为提示词文本，缺少：
1. **Runtime State Machine** — 阶段强制执行
2. **Workflow Engine** — 节点编排与DAG
3. **Trace System** — 结构化执行记录
4. **Permission Gateway** — 代码级权限约束

当前模式 = **"宪法式治理"**（写在纸上，靠自觉）而非"运行时治理"（写在代码里，自动执行）。

---

## 4. Veritas-Core Comparison — 参照分析

### 4.1 Veritas-Core 概览

Veritas-Core (v7.0.0) 是从 A3-Multi-Agent-System 提取的独立 Agent Runtime Framework。Python 可安装包 (`pip install veritas-core`)，77 模块，558 测试。核心组件：RuntimeEngine + StateMachine + Recovery + Lifecycle + Plugins + Distributed + Security + Memory + Benchmark + CLI。

### 4.2 能力对比矩阵

| 维度 | Veritas-Core | Terence-Agent 当前 | 可迁移 | 原因 |
|:-----|:------------|:-------------------|:------:|:-----|
| **Runtime State Machine** | AgentState(Enum) + RuntimeEngine + TransitionTable — 9状态自动流转 | 无代码 — Guidance 5阶段文本推理 | [v] | Phase定义直接映射到State；统一入口可行 |
| **Trace System** | DecisionTrace + ExplanationRecorder + DistributedTraceCollector | event-report 自由文本 | [v] | Trace取代自由文本，提供可查询历史 |
| **Permission/Scope Control** | PermissionMatrix + ToolGateway + PromptGuard + AuditLogger | 文本规则 + forbidden_pairs JSON | [v] | 代码级enforcement替代文本约束 |
| **Memory** | MemoryManager + StudentMemory + ExperienceMemory + Extractor | error-registry + task-progress + event-report (分散三系统) | [v] | 统一结构化Memory替代分散系统 |
| **Event Driven Comms** | RuntimeEventBus + DistributedEventBus + RuntimeEvent | JSON消息协议（仅文本定义） | [v] | EventBus替代手动JSONL维护 |
| **Recovery** | RecoveryManager + CheckpointManager + 5种Strategy | error-registry修复方案（手动查表） | [v] | 自动化替代手动查表 |
| **Plugin System** | RuntimePlugin + PluginRegistry + Loader + Manager | skill-manager JSON registry | [!] | 部分可迁移，skill在~/.hermes与repo分离 |
| **Distributed** | RuntimeNode + NodeRegistry + RemoteExec | 无 | [x] | 暂不需要，单用户单机 |
| **CLI** | veritas run/status/trace/plugins/demo | sync.sh (单脚本) | [v] | CLI替代sync.sh，提供统一入口 |

### 4.3 复用路径建议

```
Terence-Agent v2 Workflow Runtime 建设路径:

  Veritas-Core (已有)          ->  Terence-Agent v2 (新建)
  ----------------------------------------------------------
  RuntimeEngine + StateMachine ->  Workflow Engine (Phase Machine)
  DecisionTrace + Recorder     ->  Trace Collector
  PermissionMatrix + Gateway   ->  Scope Manager
  MemoryManager + Extractor    ->  Memory (统一 error + progress + event)
  RuntimeEventBus              ->  Event Bus (Agent间通信)
  PluginRegistry + Loader      ->  Skill Registry (程序化)
  RecoveryManager              ->  Policy Engine (自动错误恢复)

  策略: 不复用Veritas代码 — 复用其架构思想，在Terence-Agent中实现适配层
```

---

## 5. Technical Debt — 技术债务报告

### 5.1 债务清单

| # | 问题 | 影响 | 等级 |
|:--|:-----|:-----|:----:|
| TD-1 | 零运行时执行 — 全是提示词。512行 constraints/1010行 guidance 均为手工阅读的Markdown规则，无可执行代码 | 人为错误率高、不可自动化验证、"依赖自觉"不可靠 | HIGH |
| TD-2 | 无统一入口 AGENTS.md。constraints S0.3.3明确要求但文件不存在 | 上下文加载不完整、Agent漏读关键约束 | HIGH |
| TD-3 | event-report 职责膨胀。2026-07-17.md达470行 — 既是操作日志又是设计文档又是产出物清单 | 信息混杂、难查询、边界模糊 | MEDIUM |
| TD-4 | architecture-constraints 过重。512行单一文件含13项原则+Harness+层级+级联+命名+隐私+复盘+LangChain+成熟度 | 难维护、难增量更新、"全有或全无"加载 | MEDIUM |
| TD-5 | skill-manager与实际技能脱节。registry在repo，实际skill在~/.hermes/skills/ | 注册表过期风险、两套维护成本 | MEDIUM |
| TD-6 | projects/结构不一致。5个项目5种结构（独立git vs docx输出 vs scripts集合） | 无统一模板、无法批量操作 | MEDIUM |
| TD-7 | scripts功能单一。仅check-preflight.sh独占scripts/目录 | 目录命名暗示多功能 | LOW |
| TD-8 | 无docs/目录。文档散落各子目录README | 难找文档入口 | LOW |
| TD-9 | sync.sh紧紧耦合~/.hermes。直接cp home目录文件 | 不可移植、可能泄露配置 | LOW |
| TD-10 | 无版本号或CHANGELOG | 无法快速了解"版本" | LOW |
| TD-11 | task-progress与event-report信息重叠 | 同信息写两处，不一致风险 | LOW |
| TD-12 | Agent定义文件差异大。guidance 1010行 vs executor 82行 | 关键逻辑可能遗漏 | LOW |

### 5.2 债务热力图

```
严重度分布:
  HIGH:   2 项 (TD-1, TD-2)
  MEDIUM: 4 项 (TD-3, TD-4, TD-5, TD-6)
  LOW:    6 项 (TD-7 to TD-12)

核心矛盾: 高等级债务均源于"纯文本治理"模型 — 所有规则以提示词形式存在，
          无运行时强制执行。这是 Terence-Agent v2 重构的核心驱动器。
```

---

## 6. Future Direction — v2 目标架构

### 6.1 设计原则

```
1. 机械化约束优先 — 能写成代码的规则绝不靠提示词
2. 分层渐进 — v2 不追求一步到位，从 Workflow Runtime 核心开始
3. 兼容过渡 — v2 运行时与现有 prompt 仓库共存，逐步迁移
4. 复用 Veritas 思想 — 架构参考而非代码 fork
```

### 6.2 目标架构图

```
+-------------------------------------------------------------------+
|                      Terence-Agent v2                              |
|                   Workflow Runtime Core                            |
|                                                                    |
|  +-----------------+   +-----------------+   +-----------------+  |
|  |  Workflow Engine |   |  State Machine  |   |  Policy Engine  |  |
|  |                  |   |                 |   |                 |  |
|  | * DAG 编排       |-->| * Phase 自动    |-->| * 约束执行      |  |
|  | * Node 调度      |   |   流转          |   | * 违规检测      |  |
|  | * 依赖解析       |   | * Transition    |   | * 自动纠错      |  |
|  | * 并行/串行      |   |   Guards        |   | * 降级策略      |  |
|  +--------+---------+   +--------+--------+   +--------+--------+  |
|           |                     |                     |            |
|  +--------v---------+   +------v---------+   +------v----------+  |
|  |  Scope Manager   |   | Trace Collector|   |  Skill Registry  |  |
|  |                  |   |                |   |                  |  |
|  | * 权限矩阵       |   | * 结构化事件   |   | * Skill 加载器   |  |
|  | * 工具Gateway    |   | * Decision     |   | * 版本管理       |  |
|  | * 上下文裁剪     |   |   Chain        |   | * Schema 验证    |  |
|  | * PII Guard      |   | * 执行时间线   |   | * 依赖解析       |  |
|  +--------+---------+   +-------+--------+   +-------+----------+  |
|           |                     |                     |            |
|  +--------v---------------------v---------------------v----------+  |
|  |                       Event Bus                               |  |
|  |         发布/订阅 * Agent间消息 * 异步通知                     |  |
|  +----------------------------+----------------------------------+  |
|                               |                                    |
|  +----------------------------v----------------------------------+  |
|  |                     Memory Layer                              |  |
|  |  * Error Memory (升级 error-registry)                        |  |
|  |  * Progress Memory (升级 task-progress)                      |  |
|  |  * Event Memory (升级 event-report) -> Trace                 |  |
|  +---------------------------------------------------------------+  |
|                                                                    |
|  +---------------------------------------------------------------+  |
|  |                   Project Adapter                             |  |
|  |  * 项目模板 * 初始化器 * SPEC验证 * 结构检查                   |  |
|  +---------------------------------------------------------------+  |
|                                                                    |
+-----------------------------------+--------------------------------+
                                    |
                       +------------+------------+
                       |                         |
                  +----v-----+            +------v------+
                  | Veritas-  |            |   External   |
                  | Core      |            |   Projects   |
                  | (Runtime  |            |   (A3, etc.) |
                  |  Engine)  |            |              |
                  +-----------+            +--------------+
```

### 6.3 目标目录结构

```
Terence-Agent/
├── core/                          # v2 运行时核心 (新增，Python包)
│   ├── __init__.py
│   ├── workflow/                  # Workflow Engine
│   │   ├── engine.py              # DAG编排器
│   │   ├── node.py                # 节点定义
│   │   └── scheduler.py           # 并行/串行调度
│   ├── state/                     # State Machine
│   │   ├── machine.py             # 状态机 (AgentState + TransitionTable)
│   │   ├── guards.py              # Transition Guards
│   │   └── context.py             # RuntimeContext
│   ├── policy/                    # Policy Engine
│   │   ├── engine.py              # 约束执行引擎
│   │   ├── rules.py               # 规则定义 (从constraints迁移)
│   │   └── detector.py            # 违规检测器
│   ├── trace/                     # Trace Collector
│   │   ├── collector.py           # 结构化事件收集
│   │   ├── chain.py               # DecisionChain
│   │   └── exporter.py            # Markdown/JSON导出
│   ├── scope/                     # Scope Manager
│   │   ├── permission.py          # 权限矩阵
│   │   ├── gateway.py             # 工具Gateway
│   │   └── guard.py               # PII Guard
│   ├── event/                     # Event Bus
│   │   ├── bus.py                 # 发布/订阅总线
│   │   └── messages.py            # 标准化消息类型
│   └── memory/                    # Memory
│       ├── error_memory.py        # 结构化错误存储
│       ├── progress_memory.py     # 进度追踪
│       └── manager.py             # MemoryManager统一接口
│
├── skills/                        # Skill定义 (从~/.hermes迁入)
│   ├── registry.yaml              # 统一注册表
│   ├── browser-automation/
│   ├── devops/
│   └── ...
│
├── adapters/                      # 外部项目适配器
│   ├── a3_adapter.py
│   ├── campus_task_adapter.py
│   └── template/
│       ├── SPEC.md.tmpl
│       └── DESIGN.md.tmpl
│
├── memory/                        # 持久化记忆
│   ├── traces/                    # 结构化trace日志
│   ├── errors/                    # 错误知识库(YAML替代Markdown表)
│   └── decisions/                 # ADR
│
├── reports/                       # 自动生成报告
│   └── daily/
│
├── docs/                          # 文档
│   ├── TA-0-architecture-audit.md # 本报告
│   ├── architecture.md
│   └── decisions/
│
├── projects/                      # 保留 — 项目快照 (统一模板)
├── scripts/                       # 保留 — 工具脚本
├── architecture-constraints/      # 逐步迁移到 core/policy/
├── error-registry/                # 逐步迁移到 memory/errors/
├── agent-team/                    # 保留 — Agent定义
├── event-report/                  # 逐步迁移到 memory/traces/
├── task-progress/                 # 逐步迁移到 memory/
├── .github/workflows/             # 新增 — CI/CD
├── AGENTS.md                      # 新增 — 统一入口
├── CHANGELOG.md                   # 新增
└── README.md                      # 更新
```

### 6.4 v2 关键设计决策

| 决策 | 选择 | 理由 |
|:-----|:----:|:-----|
| 运行时语言 | Python | 与 Veritas-Core 同生态，与 Hermes 兼容 |
| 包结构 | monorepo子目录 (core/) | 保持单一仓库，渐进迁移 |
| State Machine | 自实现（参考 Veritas） | 避免外部依赖，Terence 场景更轻量 |
| Trace存储 | JSONL (P1) -> SQLite (P2) | 初期简单，后期可查询 |
| 与现有prompt共存 | 并行 — core/新增，旧文件渐进废弃 | 零风险迁移，可随时回退 |

---

## 7. Migration Risk — 迁移风险评估

### 7.1 风险矩阵

| 风险 | 概率 | 影响 | 等级 | 缓解措施 |
|:-----|:----:|:----:|:----:|:---------|
| v2运行时与Hermes工具链冲突 | 中 | 高 | HIGH | 独立Python进程，通过标准化接口(JSON/CLI)通信 |
| 现有prompt规则迁移遗漏 | 高 | 中 | MEDIUM | 逐条对照迁移 + TA-0作为checklist |
| Agent Team在新运行时中的适配 | 中 | 中 | MEDIUM | 先实现Guidance->Engine桥接层 |
| 用户习惯变更阻力 | 低 | 低 | LOW | v2提供CLI命令，v1 prompt照常可用 |
| Veritas版本升级导致参考失效 | 低 | 低 | LOW | 仅参考架构思想，不依赖API |
| skill从~/.hermes迁移丢失 | 中 | 中 | MEDIUM | 迁移前备份+diff验证 |
| projects统一模板破坏现有项目 | 低 | 中 | LOW | 新模板仅对新项目强制 |

### 7.2 推荐迁移阶段

```
Phase TA-0 (当前):    架构审计 -> 冻结 -> 本报告                [COMPLETED]
Phase TA-1:           core/骨架搭建 (WorkflowEngine + StateMachine)
                      不迁移任何现有逻辑，纯新增代码
Phase TA-2:           Policy Engine (迁移constraints到可执行规则)
                      Scope Manager (权限矩阵 + Gateway)
Phase TA-3:           Trace Collector + Memory Layer
                      替代 event-report + task-progress
Phase TA-4:           Skill Registry 程序化
                      从~/.hermes迁入 skills/ + registry.yaml
Phase TA-5:           Project Adapter + CLI
                      统一projects/模板 + veritas-style CLI
Phase TA-6:           旧文件归档 (constraints/* -> docs/archive/)
                      保留为只读参考
```

### 7.3 不可变约束

```
1. 单报告文件写入 — 仅 docs/TA-0-architecture-audit.md
2. 禁止 git 写操作 — 不 commit/push/branch
3. 禁止修改 ~/Veritas-Core
4. PII 零容忍 — 报告中已使用占位符
5. 现有 Agent Team 定义保持可用 — v2 增强而非替代
```

---

## Appendix A — 审查方法论

```
审查流程:
  Step 1: find + tree 扫描目录结构 (200+ 文件)
  Step 2: 精读重点文件 (~15 个核心 .md 文件)
  Step 3: 对照 Veritas-Core 源码结构评估差距
  Step 4: 统计指标 (行数/文件数/类型分布)
  Step 5: 技术债务三角评估 (问题->影响->等级)
  Step 6: v2架构设计 (仅设计，不实现)

工具: find / git / wc / grep (只读)
时间: ~15 次文件读取 + 5 次目录扫描
```

## Appendix B — 关键文件清单（本次审查精读）

```
architecture-constraints/README.md    (512 行)
error-registry/README.md              (132 行)
agent-team/guidance-agent/README.md   (1010 行)
agent-team/agent-developer/README.md  (176 行)
agent-team/agent-executor/README.md   (82 行)
agent-team/agent-debugger/README.md   (190 行)
agent-team/agent-logger/README.md     (186 行)
skill-manager/README.md               (188 行)
skill-manager/skill-registry.json     (141 行)
event-report/README.md                (76 行)
event-report/2026-07-17.md            (470 行)
task-progress/README.md               (252 行)
scripts/check-preflight.sh            (355 行)
sync.sh                               (34 行)
projects/lab-report/SPEC.md           (29 行)
Veritas-Core/README.md                (216 行)
Veritas-Core/veritas/__init__.py      (106 行)
Veritas-Core/veritas/runtime/state.py (58 行)
Veritas-Core/veritas/runtime/runtime.py (343 行)
```

---

> **报告结论**: Terence-Agent 是一个设计完善的"宪法式"Agent治理仓库，拥有成熟的角色分工、错误管理、约束体系和操作流程，但所有治理逻辑以提示词文本形式存在，缺乏运行时强制执行。最大的架构债务是"零代码治理"——512行架构约束需要Agent手动阅读理解，而非程序化执行。Veritas-Core 提供了关键参考架构（State Machine、Trace、Permission、Memory、EventBus），可指导 Terence-Agent v2 的 Workflow Runtime 建设，实现从"宪法式治理"到"运行时治理"的跃迁。

> *"By enforcing invariants, not micromanaging implementations, we let agents ship fast without undermining the foundation."* — OpenAI Harness Engineering (2026)
