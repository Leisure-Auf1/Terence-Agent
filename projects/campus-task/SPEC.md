# CampusTask — 功能规范 (SPEC)

> 位置: `Terence-Agent/projects/campus-task/`
> 版本: 1.0.0
> 状态: ✅ 实现完成

## 1. 项目概述

CampusTask 是一个校园任务清单命令行工具，覆盖软件工程课程 8 个实验的全部要求。

## 2. 功能列表

### 2.1 实验 1 — 最小可用产品 (MVP)

| 功能 | 命令 | 说明 |
|:-----|:-----|:-----|
| 添加任务 | `python main.py add "标题"` | 自动编号，记录创建时间 |
| 列出任务 | `python main.py list` | 显示编号/状态/时间/标题 |
| 完成任务 | `python main.py done <编号>` | 标记为已完成 |
| 数据持久化 | — | JSON 文件存储，重启不丢失 |

验收标准: 5 条用户故事 + 对应验收标准写入 README。

### 2.2 实验 2 — 模块化设计

| 模块 | 职责 |
|:-----|:-----|
| `task_model.py` | 数据模型 (Task dataclass) |
| `task_storage.py` | JSON 持久化 |
| `task_service.py` | 业务逻辑 |
| `main.py` | CLI 交互 (仅命令行解析) |

约束: 每个函数 ≤ 25 行，意图命名，功能零回归。

### 2.3 实验 3 — 测试与验收

20 个 pytest 用例覆盖:
- 新增/空标题拒绝/列表/完成/编号递增
- 文件不存在/空文件/损坏
- 状态过滤/deadline 排序/CSV 导出
- Bug 引入(完成→删除)→测试失败→修复

### 2.4 实验 4 — Git 协作

| 要求 | 实现 |
|:-----|:-----|
| 2 个功能分支 | `feature-deadline`, `feature-filter` |
| 每分支 ≥ 3 commits | ✓ (各 3 次) |
| 合并冲突 | `main.py` 双重修改 → 手动解决 |
| 代码评审 | 各 2 条意见 + 响应记录 |

### 2.5 实验 5 — 迭代开发

- 3 名用户反馈 → 变更请求表
- 实现: deadline 排序 + CSV 导出
- CHANGELOG.md 记录

### 2.6 实验 6 — CI/CD

- `pyproject.toml` (项目名/版本/依赖)
- `.github/workflows/test.yml` (matrix: 3.10-3.13)
- 失败→修复记录

### 2.7 实验 7 — 发布运维

- 包结构: `campus_task/` (python -m campus_task)
- argparse CLI: `--version`, `--help`
- 日志: `campus_task.log`
- 用户手册: `USER_GUIDE.md`
- Bug 修复: 空 tasks.json 崩溃 → 返回空列表

### 2.8 实验 8 — AI Harness

7 个模块:
1. `prompt_builder(user_input, task_state)` → prompt
2. `mock_model(prompt)` → JSON output
3. `parse_model_output(output)` → action dict
4. `guardrail(action)` → pass/block
5. `execute_tool(action)` → result
6. `write_trace(event)` → trace.jsonl
7. `run_eval(eval_cases)` → accuracy

10 条 eval 用例, 100% 准确率。

## 3. 技术栈

- Python ≥ 3.10
- pytest ≥ 8.0 (测试)
- 无外部依赖

## 4. 项目结构

```
projects/campus-task/
├── README.md                      ← 项目总览
├── USAGE.md                       ← 使用手册
├── SPEC.md                        ← 功能规范 (本文件)
├── DESIGN.md                      ← 架构设计
├── CHANGELOG.md                   ← 版本变更
├── docs/
│   ├── exec-plans/plan.md         ← 执行计划
│   └── decisions/                 ← 设计决策
├── src/                           ← 源代码
│   ├── main.py                    ← CLI 入口 (兼容模式)
│   ├── campus_task/               ← 包模式
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── __version__.py
│   │   ├── task_model.py
│   │   ├── task_storage.py
│   │   └── task_service.py
│   ├── ai_harness.py              ← AI Harness
│   ├── eval_cases.json            ← 评测集
│   └── task_model.py              ← 根层模块 (兼容)
│       task_storage.py
│       task_service.py
├── tests/                         ← 测试
│   └── test_campus_task.py
└── artifacts/                     ← 构建产出
