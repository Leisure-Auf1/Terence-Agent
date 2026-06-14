# CampusTask — 校园任务清单

> 位置: `projects/campus-task/`
> 状态: ✅ 全部 8 实验完成
> 技术栈: Python ≥ 3.10, pytest

## 快速开始

```bash
# 传统模式
cd src && python main.py add "任务"
python main.py list
python main.py done 1

# 包模式
python -m campus_task add "任务" --deadline 2026-06-20
python -m campus_task list --sort deadline
python -m campus_task --version

# AI 助手
python ai_harness.py "帮我添加一个任务"
python ai_harness.py "列出我的任务"
python ai_harness.py "删除所有任务"  # 被 guardrail 拦截
```

## 8 个实验速览

| # | 实验 | 核心产出 | 状态 |
|:-:|------|---------|:----:|
| 1 | 需求→MVP | `main.py` + 5 用户故事 | ✅ |
| 2 | 模块化设计 | 4 层架构 (model/ storage/ service/ main) | ✅ |
| 3 | 测试与验收 | 20 pytest 用例 + bug 引入修复 | ✅ |
| 4 | Git 协作 | 2 分支 × 3 commits + 冲突解决 + 评审 | ✅ |
| 5 | 迭代开发 | 3 反馈 + deadline排序 + CSV导出 + CHANGELOG | ✅ |
| 6 | CI 门禁 | pyproject.toml + GitHub Actions + 红绿灯 | ✅ |
| 7 | 发布运维 | python -m campus_task + argparse + 日志 + bug修复 | ✅ |
| 8 | AI Harness | 7 模块 + 10 eval (100%) + trace + guardrail | ✅ |

## 文档

| 文件 | 说明 |
|:-----|:-----|
| `SPEC.md` | 功能规范 |
| `USAGE.md` | 用户手册 |
| `DESIGN.md` | 模块架构设计 |
| `CHANGELOG.md` | 版本变更历史 |
| `docs/exec-plans/plan.md` | 执行计划 |
| `docs/decisions/` | 架构决策记录 (ADR) |
