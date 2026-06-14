---
name: architecture-constraints
description: '严格架构约束 — 技能/工具/上下文的层级依赖、调用规则、错误级联。打破约束=入error-registry'
category: devops
tags: [core, governance, architecture]
related_skills: [error-registry, task-progress, browser-automation, computer-use-mcp, cli-anything]
---

# 🏗️ 严格架构约束 (Strict Architecture Constraints)

> 以下约束**必须遵守**。违反即记入 error-registry，下次同类任务自动加载纠正记录。

---

## 0. 核心原则

```
1. Layer N 不能跳过 Layer N-1 直接调用 Layer N+1
2. 失败必须沿 Error Cascade 降级，不能跳过
3. 每种任务类型只能由指定技能处理
4. 上下文必须按 Scope 裁剪，不能超载
5. 治理在基础设施层实现，不靠提示词约束 [Harness]
6. Agent 由事件触发，不靠手动输入启动
7. 每次执行都在隔离沙箱中运行
8. 仓库即系统记录 — 所有文档/规范/决策进 Git，不进聊天记录 [Harness]
9. 机械约束优先 — 可写的规则写成脚本/linter，不可写的才放提示词 [Harness]
10. 上下文重置 — 大步骤间做 context checkpoint，不拖大 context [Harness]
11. 生成vs评估分离 — 创造者不审自己产出 [Harness]
12. 实现项目必须走 PR 流程 — 分支→提交→PR→合并 [PR]
13. Agent 之间不得互调工具 — 所有 Agent 间通信通过 Guidance 中继 [Agent Team]
```

## 0.3 Harness Engineering 附加约束

> 这些约束直接来自 Harness Engineering 2026 最佳实践，与上面的核心原则互补。

### 0.3.1 机械约束优先 (Mechanical Enforcement)

```
原则: 用 linter/CI/结构性测试 替代提示词约束
依据: OpenAI Harness Engineering (2026) — "By enforcing invariants,
       not micromanaging implementations, we let agents ship fast
       without undermining the foundation."

约束:
  1. 每个代码项目必须有 spec → 同时生成验证脚本
  2. Reviewer 必须优先运行机械检查 → 再审核逻辑
  3. 机械检查脚本本身必须受版本控制 (进 Git)
  4. 任何重复发生的错误 → 先写成检查脚本 → 再写修复

禁止:
  ❌ 用提示词约束代替脚本检查
  ❌ Reviewer 跳过检查脚本直接人工审核
  ❌ 调试器修复后不补充检查脚本
```

### 0.3.2 上下文重置 (Context Reset)

```
原则: 长会话积累噪声和错误假设，定期重置上下文更可靠
依据: Kypros Vassiliou (2026) — "Fresh runs with clear artifacts +
       next steps + compact state outperform dragging one giant
       context window."

约束:
  1. 每 3+ 个工具调用后做 context checkpoint
  2. 每个大阶段 (Design/Impl/Review) 后做上下文重置
  3. 重置时写入 artifact: 已完成摘要 + 未完成清单 + 关键决策
  4. 禁止跳过多步后才做 checkpoint

例子:
  Phase 1: 写 spec → artifact: spec.md + spec-validate.sh
  → 上下文重置 →
  Phase 2: 实现 Worker Agent → 读取 spec.md 即可，不用看 Phase 1 的整个对话
```

### 0.3.3 仓库即系统记录 (Repository as System of Record)

```
原则: 所有知识进 Git，不进聊天记录
依据: OpenAI Harness Engineering (2026) — "Give Codex a map,
       not a 1,000-page instruction manual."
约束:
  1. 每个项目必须在 projects/ 下有独立目录
  2. 必须包含 README.md + 至少一个规范文档 (SPEC.md / DESIGN.md / USAGE.md)
  3. 所有架构决策写入 docs/decisions/*.md
  4. **🆕 AGENTS.md 作为入口目录** — 约 100 行，指向结构化文档知识库
  5. 禁止依赖聊天历史作为知识来源

```

### 0.3.4 PR 流程约束 (PR Workflow Gate)

```
原则: 任何产生代码/配置/文档的实现项目，交付必须走 PR
依据: OpenAI (2026) — "Corrections are cheap, and waiting is expensive."

约束:
  1. 批量文件变更 (>3文件) → 必须提 PR
  2. PR 必须用 conventional commit 格式
  3. PR 必须包含: Summary + Changes + Test Plan
  4. PR 自审通过后才可合并
  5. 合并必须用 squash (保持 main 历史干净)

禁止:
  ❌ 批量文件变更直接 push 到 main
  ❌ PR 没有自审就合并
  ❌ PR 标题不含 type(scope)
```

### 0.3.5 Agent 间协作约束 (Inter-Agent Communication)

```
原则: Agent 之间不直接对话 — 所有通信通过 Guidance Agent 协调。
依据: guidance-agent S2.1 — 消息总线模式

约束:
  1. Developer 不调用 Executor 的浏览器/桌面/CLI 工具
  2. Executor 不调用 Developer 的编码工具
  3. 所有 Agent 的产出通过 Guidance 中继给 Logger
  4. Debugger 修复错误后必须通知 Guidance 更新 error-registry
  5. 每个 Agent 完成关键步骤后必须通知 Logger

禁止:
  ❌ Agent 之间互调工具 (CROSS_AGENT_TOOL_CALL)
  ❌ 完成关键步骤后不通知 Logger (LOGGER_MISSING)
  ❌ 移交时传全部上下文而非 artifact 摘要 (CTX_CHECKPOINT_MISSING)
```

---

## 0.5 LangChain 架构映射 (参考)

LangChain 的设计模式可以直接映射到我们的架构约束中。

| LangChain 概念 | 我们的实现 | 约束 |
|:---------------|:-----------|:-----|
| **Chain** (链) | Layer 级联 (L1→L2→L3→L4) | 不能跳链，只能沿 error cascade 降级 |
| **Agent + Tools** | 任务类型路由到对应 Layer | 上下文裁剪 = 只加载当前任务的 tools |
| **Memory** (持久记忆) | `task-progress` + `error-registry` | 每个任务结束后必须更新 memory |
| **Callback** (回调) | Post-Task Retrospective | `SKIP_RETROSPECTIVE` 记错 |
| **Evaluator** (评估器) | 复盘第2步"结果是否符合预期" | 不符合 → 分析差距 → 更新 progress |
| **Retriever** (检索器) | 开始前查 error-registry 已知错误 | `SKIP_KNOWN_FIX` / `REPEAT_ERROR` 记错 |
| **Router** (路由) | 上下文裁剪 = 按类型路由到正确 Layer | `CTX_OVERLOAD` 记错 |
| **Tool** (工具) | 各 Layer 的具体能力 (Playwright/CDP/AI/截图) | 只通过所在 Layer 暴露，不能跨层调用 |
| **Chain-of-Thought** | 每步先思考 → 查记录 → 再执行 | 体现在复盘的"先查重复再动手" |

### 执行流程 (参照 LangChain Agent 模式)

```
Input (用户请求)
  │
  ├─ Router: 判断任务类型 → 只加载对应 Layer 的 tools
  │
  ├─ Retriever: 查 error-registry → 加载相关错误记录
  │
  ├─ Agent (思考):
  │   ├─ 当前进度? → 查 task-progress
  │   ├─ 已知坑?   → 查 error-registry
  │   └─ 正确路径? → 查 architecture-constraints
  │
  ├─ Chain (执行):
  │   Layer 1 → 失败 → Layer 2 → 失败 → Layer 3...
  │   每步结果 → 更新 task-progress
  │   每步错误 → 记入 error-registry
  │
  ├─ Evaluator (复盘):
  │   1. 读日志 → 有错? → 记入 error-registry
  │   2. 读产出 → 符合预期? → 更新 progress
  │   3. 查重复 → 这次错以前犯过?
  │   4. 学教训 → 更新修复方案
  │   5. 固化 → 需要创建 skill?
  │   6. 收尾 → 标记完成
  │
  └─ Output (结果 + 复盘报告)
```

## 0.6 Self-Driving Codebase 成熟度模型 (参考)

参照 Self-Driving Codebase 的三阶段进化，我们的自动化能力也分三级：

| 阶段 | 特征 | 对应我们的实现 |
|:-----|:------|:---------------|
| **1. Copilot** (补全+对话) | 单步执行，人在回路 | 标准工具调用，每次手动下发指令 |
| **2. Agent** (多步执行+监督) | 多步推理，人审批高风险 | `task-progress` 追踪 + `error-registry` 审计 |
| **3. Autonomous** (事件触发+自动) | 后台运行，事件驱动，批量并行 | 目标态：cron/webhook 触发 Hermes 技能 |

**约束**: 当前我们在阶段 1→2 的过渡期。阶段 3 是目标，三要素缺一不可:
- 事件触发 (webhook/cron → skill)
- 治理层 (IAM/审计/credential scoping → error-registry)
- 隔离执行 (sandbox → 独立 venv/workspace)


---

## 1. 能力层级 (Strict Stack)

```
Layer  ┌──────────────────────────────────────┐
 7     │  task-progress       进度追踪系统      │ ← 任何复杂任务自动挂载
 6     │  error-registry      报错表            │ ← 全时挂载
 5     │  architecture-constraints 本文件      │ ← 全时挂载
───────┼──────────────────────────────────────┼────────
 4     │  computer-use-mcp    桌面操控(MCP)     │ ← 仅桌面操控任务
 3     │  cli-anything        软件原生CLI       │ ← 仅软件封装任务
 2     │  browser-automation  浏览器自动化(4层)  │ ← 仅网页任务
 1     │  标准工具 (terminal/read_file/...)     │ ← 全时可用
 0     │  memory              持久记忆          │ ← 全时注入
```

**约束**: 上层可以调用下层，下层不能调用上层。
**约束**: 同层之间不能交叉调用 (2层不能调3层的方法)。

---

## 2. 上下文裁剪规则 (Context Scoping)

| 任务类型 | 必须加载 | 禁止加载 |
|:---------|:---------|:---------|
| browser automation (U校园/爬虫) | L2 browser-automation, L5 error-registry, L6 task-progress | L4 computer-use-mcp, L3 cli-anything |
| 桌面操控 (截图/鼠标/键盘) | L4 computer-use-mcp, L5 error-registry | L2 browser-automation, L3 cli-anything |
| 软件CLI封装 (Blender/Obsidian CLI) | L3 cli-anything, cli-anything-hermes, L5 error-registry | L2, L4 |
| 纯开发/编码 (写代码/改bug) | L1 标准工具, L5 error-registry | L2, L3, L4 |
| **🆕 实验报告 (OS/文档类)** | **os-lab-report-automation, docx-raw-xml, lab-report-execution, L5 error-registry** | L2 browser-automation, L4 computer-use-mcp |
| 操作系统实验报告 | 实验报告相关技能 (ucampus 等) | L2-L4 全部自动化工具 |

**约束**: 加载禁止项 = `CTX_OVERLOAD` 错误，记入 error-registry。

---

## 3. 错误级联 (Error Cascade)

```
Layer N 调用失败
  → 查 error-registry 是否有已知修复
    → 有 → 应用修复 → 重试 Layer N
    → 无 → 降级到 Layer N-1 替代方案
      → 成功 → 记入 task-progress "使用替代方案"
      → 失败 → 继续降级到 Layer N-2
        → 直到 Layer 0 (标准工具) 仍失败 → 报告用户
```

**具体级联路径**:

```
browser-automation (L2) 内部:
  L1 Playwright 失败
    → L2 CDP Harness (bhts) 失败
      → L3 browser-use AI 失败
        → L4 Screenshot Vision 失败
          → 报告用户 + 记入 error-registry

computer-use-mcp (L4) 失败:
  → 查 error-registry → 确认 native binding 是否存在
  → 尝试 pip 替代 (pyautogui/pynput)
  → 尝试 Linux 原生 (ydotool/grim)
  → 报告用户
```

**约束**: 不能跳过级联中的任何一层直接报错。

---

## 4. 文件/命名约束

```
技能目录:   ~/.hermes/skills/<category>/<name>/
类别:       browser-automation | devops | software-development | ...
进度文件:   ~/.hermes/tasks/<task-id>/progress.md
产出物:     ~/.hermes/tasks/<task-id>/artifacts/
错误表:     ~/.hermes/skills/devops/error-registry/SKILL.md

命名规则:
  - 技能名: kebab-case (browser-automation)
  - 任务ID: YYYYMMDD_HHMMSS_<简短描述>
  - 产出物: <step-number>_<描述>.<ext>
```

---

## 4.5 Feedforward/Feedback 体系 — Harness Engineering 分类

> **参考**: Martin Fowler — "A coding agent has none of the tacit knowledge that human developers bring."
>
> Harness 机制分两轴：方向 (Feedforward → Feedback) × 类型 (Computational → Inferential)

| 方向 | 类型 | 我们的实现 | 作用时机 |
|:-----|:-----|:-----------|:---------|
| **Feedforward (Guide)** 🧭 | Computational | `scripts/check-preflight.sh` | 项目开始前 |
| **Feedforward (Guide)** 🧭 | Inferential | `AGENTS.md` + `architecture-constraints` | 上下文加载时 |
| **Feedback (Sensor)** 📡 | Computational | `error-registry` + `event-report` 违反检测 | 项目完成后 |
| **Feedback (Sensor)** 📡 | Inferential | Post-Task 复盘 (第0步事件报告检查) | 项目完成后 |

**约束**:
- Feedforward 和 Feedback 必须配对使用，缺一不可
- 只有 Feedforward 没有 Feedback → 无法自我纠错
- 只有 Feedback 没有 Feedforward → 重复犯同样的错
- Computational 优先于 Inferential（机械约束 > 提示词约束）
- **🆕 隐私审查优先** — 任何涉及用户个人信息的内容必须有隐私审查步骤

---

## 4.6 隐私规则 — PII 零容忍

> **规则**: 仓库中**严禁**出现任何真实用户个人信息（姓名、学号、电话、地址等）。
> 违反即记入 error-registry `PII_LEAK` — **严重违规**。

### 约束

```
1. 所有示例/演示/模板中的人名 → [姓名] 或 [已脱敏]
2. 所有示例中的学号 → [学号]
3. 班级信息 → [班级]
4. 联系方式 → [联系方式]
5. delegate_task 上下文中必须过滤真实姓名
6. 代码、注释、测试用例、日志文件 → 同样适用上述规则
7. 遇到用户提供个人信息的场景：
   a. 使用时脱敏（日志/输出中用占位符替代）
   b. 不写入任何持久化文件（event-report / error-registry / skill 等）
   c. 仅在必要时传入内存变量，使用后清除
```

### 例外

仅用户**明确要求**在产出物中包含个人信息时（如实验报告 docx 需显示姓名学号），可以在用户指定的最终产出中使用，但：
- 中间过程（日志、代码、skill）不得包含
- 使用后立即清理

---

## 5. 技能调用约束

### 5.1 机械约束优先（Harness Engineering）

将 pre-flight 检查从"提示词清单"升级为**可执行脚本**：

```bash
# 每次开始新项目前，必须先运行 preflight 检查脚本
cd ~/Terence-Agent && bash scripts/check-preflight.sh
```

脚本产出 `.hermes/preflight-YYYY-MM-DD.md`，作为项目的 **context checkpoint** 入口。

**约束**:
- ❌ 不能用"我检查过了"代替脚本执行
- ❌ 不能跳过 preflight 直接开始工作
- ❌ 不能依赖聊天记忆中的旧仓库状态 — **必须实时查看当前状态**
- ✅ 脚本输出 = 当前仓库状态的唯一权威来源

**🆕 跨会话仓库状态检查**:
```bash
# 每次新开始/跨会话工作前，必须执行：
cd ~/Terence-Agent && \
  git status && \
  git log --oneline -5 && \
  ls projects/

# 确保不依赖旧对话中看到的旧状态
```

### 5.2 提示词清单（作为脚本的补充说明）

```yaml
# 调用前必须执行
pre-check:
  - "当前任务类型是什么?" → 对照上下文裁剪规则
  - "之前报过什么错?" → 查 error-registry 对应条目
  - "是否有进行中的任务?" → 查 task-progress
  - "仓库当前状态是什么?" → git status + 查看最近修改的文件（确保基于最新状态）
  - "当前可用技能和模板有哪些?" → skills_list + 查看 paper-writing/ agent-team/ 目录

# 调用后必须执行
post-check:
  - "执行成功?" → 更新 task-progress
  - "遇到新错误?" → 记入 error-registry
  - "有产出物?" → 记入 task-progress artifacts
```

---

## 6. 违反后果

| 违反 | 后果 |
|:-----|:-----|
| 跳层调用 (L1→L3) | 记入 error-registry `SKIP_LAYER_VIOLATION` |
| 加载禁止上下文 | 记入 error-registry `CTX_OVERLOAD` |
| 重复已报过的错误 | 记入 error-registry `REPEAT_ERROR` |
| 跳过 error-registry 检查 | 记入 error-registry `SKIP_KNOWN_FIX` |
| 未更新 task-progress | 记入 error-registry `PROGRESS_MISSING` |
| 🆕 实现项目前跳过 preflight 检查 | 记入 error-registry `PREFLIGHT_SKIPPED` |
| 🆕 项目完成后未记录到 event-report | 记入 error-registry `EVENT_REPORT_MISSING` |
| **🆕 批量文件变更未走 PR** | 记入 error-registry `SKIP_PR_GATE` |
| **🆕 跳过机械检查直接审核** | 记入 error-registry `SKIP_MECHANICAL_CHECK` |
| **🆕 大步骤间未做 context checkpoint** | 记入 error-registry `CTX_CHECKPOINT_MISSING` |
| **🆕 关键步骤后未写入 JSON 消息** | 记入 error-registry `JSON_MESSAGE_MISSING` |
| **🆕 JSON 消息格式无效** | 记入 error-registry `JSON_INVALID` |
| **🆕 Agent 之间互调工具** | 记入 error-registry `CROSS_AGENT_TOOL_CALL` |
| **🆕 完成关键步骤后未通知 Logger** | 记入 error-registry `LOGGER_MISSING` |

---

## 7. Post-Task 强制复盘 (Post-Task Retrospective)

每个任务完成后**必须**执行以下复盘流程:

### 复盘清单 (必须逐条执行)

```yaml
复盘步骤:
  0. 事件报告: "这次操作是否已记录到 event-report?"
     → 未记录 → 立即写入 event-report/YYYY-MM-DD.md
     → 已记录 → 确认
  1. 读日志: "这次执行有没有报错?"
     → 有 → 分析根因 → 记入 error-registry
     → 无 → 跳过
  2. 读产出: "结果是否符合预期?"
     → 不符合 → 分析差距 → 更新 task-progress "待修复"
     → 符合 → 确认
  3. 查重复: "这个错以前犯过吗?"
     → 查 error-registry 对应条目
     → 重复了 → 记入 REPEAT_ERROR → 强化修复
  4. 机械检查: "有可写成脚本的检查项吗?"
     → 有 → 创建/更新检查脚本 [Harness 强化]
     → 无 → 跳过
  5. PR 检查: "产出是否需要走 PR?"
     → 批量变更/新功能 → 走 PR 流程 [PR 门控]
     → 不需要 → 确认
  6. 学教训: "下次如何避免?"
     → 更新 error-registry 的修复方案
     → 更新 architecture-constraints (如果需要加新约束)
  7. 固化: "需要保存为 skill 吗?"
     → 如果这个工作流是重复性的 → 创建/更新 skill
  8. 收尾: 更新 task-progress → 标记阶段完成 + 记录复盘结果
```

### 复盘触发时机

```
每个任务完成后 → 强制复盘
  遇到错误修复后 → 强化复盘 (重点查修复是否有效)
  用户纠正后 → 记录纠正内容 → 更新 error-registry
  新对话开始时 → 加载 error-registry → 查历史高发错误
```

### 强化机制 (Reinforcement Loop)

```
犯错 → 记入 error-registry
   → 下次同类型任务前自动加载对应条目
     → 预判可能的错误
       → 主动规避
         → 成功了 → 强化成功
           → 失败了 (又犯了) → REPEAT_ERROR
             → 更显式的修复方案
               → 下次一定不会再犯
```

**约束**: 每个任务完成到下一任务开始之间，必须有复盘间隙。连续执行多个任务时，复盘中发现的阻塞必须先修复再进入下一个。

