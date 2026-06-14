# AGENTS.md — Terence-Agent 仓库入口

> **原则**: Repository as System of Record (OpenAI Harness Engineering, 2026)
> "What the Agent can't see, doesn't exist."
>
> 本文件是仓库的目录索引，按 Progressive Disclosure 引导 Agent 读取必要内容。

## 快速导航

| 你要做什么 | 入口 |
|:-----------|:-----|
| 了解仓库结构和规矩 | [README.md](README.md) |
| 开始新项目前必须做的 | [scripts/check-preflight.sh](scripts/check-preflight.sh) |
| 查看今日操作日志 | [event-report/2026-06-14.md](event-report/2026-06-14.md) |
| 查看架构约束 | [architecture-constraints/README.md](architecture-constraints/README.md) |
| 查看报错表（已知问题和修复） | [error-registry/README.md](error-registry/README.md) |
| 使用论文/报告写作体系 | [paper-writing/README.md](paper-writing/README.md) |

## 体系结构

```
Terence-Agent/
├── AGENTS.md                       ← 本文件（入口目录）
├── .hermes/
│   ├── risk-contract.json          ← 风险合同（机器可读）
│   ├── checkpoint.template.md      ← Context Checkpoint 模板
│   └── preflight-YYYY-MM-DD.md     ← Preflight 检查摘要（自动生成）
│
├── scripts/
│   └── check-preflight.sh          ← Preflight 机械检查脚本（Fedforward Guide）
│
├── event-report/                   ← 📋 每日事件报告（操作日志）
├── error-registry/                 ← 🚨 报错表（错误码+修复方案）
├── architecture-constraints/       ← 🏗️ 架构约束
├── paper-writing/                  ← 📝 论文/报告写作体系
│
├── agent-team/                     ← 🤖 Agent 角色定义
│   ├── guidance-agent/             ← 总指挥
│   ├── agent-developer/            ← 开发者
│   ├── agent-debugger/             ← 调试器
│   ├── agent-executor/             ← 执行器
│   ├── agent-logger/               ← 日志记录
│   ├── paper-agent-coordinator/    ← 论文写作总指挥
│   ├── paper-agent-researcher/     ← 文献研究
│   ├── paper-agent-writer/         ← 写作排版
│   └── paper-agent-reviewer/       ← 审稿验证
│
├── task-progress/                  ← 📊 进度追踪
├── skill-manager/                  ← 🔧 技能注册表
├── projects/                       ← 📂 项目工作区
└── sync.sh                         ← 🔄 Git 同步脚本
```

## Pre-flight 流程（强制）

```
每次开始新项目前必须执行:

1. bash scripts/check-preflight.sh    ← 机械检查（feedforward guide）
2. cat .hermes/preflight-YYYY-MM-DD.md ← 读取摘要
3. 根据需要创建或更新 checkpoint
4. 开始项目工作
```

## 引用

- Harness Engineering: https://openai.com/index/harness-engineering/
- Martin Fowler on Harness: https://martinfowler.com/articles/harness-engineering.html
- Control-Plane Pattern: Ryan Carson (2026)
