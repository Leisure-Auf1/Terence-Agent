# 🤖 Terence-Agent

> Hermes Agent 日志体系 + 项目工作区
> 仓库: `Leisure-Auf1/Terence-Agent`

## 规矩

```
1. 所有新项目默认放这里 → projects/<项目名>/
2. 每个项目独立目录，互不污染
3. 除非项目间有显式联动，否则不共享依赖/配置
4. 日志/配置/工具放在独立目录，不混入项目代码
```

## 目录结构

```
├── projects/                ← 🆕 项目工作区（每个项目独立）
│   ├── <project-a>/         ← 项目 A（独立 venv + 代码）
│   │   ├── src/
│   │   ├── venv/
│   │   └── artifacts/
│   ├── <project-b>/         ← 项目 B（独立 venv + 代码）
│   │   ├── src/
│   │   ├── venv/
│   │   └── artifacts/
│   └── computer-setup/      ← 💻 电脑维护（系统配置/驱动/维护操作）
│
├── event-report/            ← 📋 事件报告（按日操作记录）
├── error-registry/          ← 报错表（共用的认知记忆）
├── architecture-constraints/← 架构约束
├── task-progress/           ← 进度追踪
├── skill-manager/           ← 技能注册表
├── agent-team/              ← Agent 角色定义
├── sync.sh                  ← 一键同步
└── README.md
```

## 项目隔离规则

```bash
# 创建新项目
mkdir -p projects/<项目名>/src projects/<项目名>/artifacts
python3 -m venv projects/<项目名>/venv

# 激活项目环境
source projects/<项目名>/venv/bin/activate

# 项目完成后，产物放 artifacts/
# 不和其它项目共享 pip 包
```

## 同步

```bash
bash ~/Terence-Agent/sync.sh "📝 说明"
```
