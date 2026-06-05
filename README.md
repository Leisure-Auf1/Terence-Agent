# 🤖 Terence-Agent

> Hermes Agent 日志体系 — 持久化记录、跨会话恢复

## 目录结构

```
├── error-registry/            ← 报错表（L0致命→L3信息，24条+违规代码）
├── architecture-constraints/  ← 架构约束（LangChain + SDC 参考）
├── task-progress/             ← 进度追踪（tasks/ 目录存放所有任务）
├── skill-manager/             ← 技能注册表 + 路由规则
└── agent-team/                ← Agent Team 定义
    ├── guidance-agent/        ← 指挥官
    ├── agent-developer/       ← 开发工程师
    ├── agent-debugger/        ← 调试工程师
    ├── agent-executor/        ← 实操工程师
    └── agent-logger/          ← 日志工程师
```

## 同步方式

```bash
# 每次修复/复盘后
cd ~/Terence-Agent
cp ~/.hermes/skills/devops/error-registry/SKILL.md error-registry/README.md
cp ~/.hermes/skills/devops/task-progress/SKILL.md task-progress/README.md
git add . && git commit -m "📝 sync: $(date)" && git push
```
