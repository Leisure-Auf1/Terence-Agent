# Post-Task 复盘 — CampusTask 全部 8 实验

> 任务ID: campus-task-8exp
> 复盘时间: 2026-06-14 09:35

## 复盘清单

### 0. 事件报告
- ✅ 已记录到 `event-report/2026-06-14.md` (09:35 条目)

### 1. 读日志 — 有报错吗？
- ✅ 无系统性报错
- 修复了 1 个偏离框架的问题：实验 3 "添加空标题"原实现允许空标题 → 改为 `ValueError` 拒绝
- 修复了 1 个 bug：空 `tasks.json` 文件崩溃 → 返回空列表

### 2. 读产出 — 结果符合预期？
- ✅ 20/20 pytest 通过
- ✅ 10/10 eval 通过 (accuracy 100%)
- ✅ 所有 8 实验功能正常
- ✅ 框架合规项目结构已建立

### 3. 查重复 — 这个错以前犯过吗？
- ⚠️ 主要偏差：未按 Agent Team 框架执行，直接单 Agent 工作
  - 违反 `CTX_OVERLOAD` (本应分 Agent 但未分)
  - 违反 `PROGRESS_MISSING` (未及时创建 task-progress)
  - 违反 `PREFLIGHT_SKIPPED` (未先跑 preflight 就开工)
  - 已在当前轮次全部修复

### 4. 机械检查 — 有可写成脚本的检查项吗？
- ✅ 可补充：`scripts/check-project-structure.sh` 检查 projects/ 下的项目是否包含必需文件 (SPEC.md, exec-plans, decisions)

### 5. PR 检查 — 需走 PR 吗？
- ✅ 已走 PR 流程：`feat/campus-task-8exp` 分支已推送
- 🔗 [创建 PR](https://github.com/Leisure-Auf1/Terence-Agent/pull/new/feat/campus-task-8exp)

### 6. 学教训
- 下次大规模多步骤任务：必须走 Phase 0-5 流程，先跑 preflight
- 多 Agent 协作：Guidance → delegate_task → Logger 全程跟踪
- 框架优先：先问"框架要求什么"再动手

### 7. 固化 — 需要保存为 skill 吗？
- 否 — 该任务是一次性课程实验，非重复性工作流
- 框架本身已有 guidance-agent 技能覆盖流程

### 8. 收尾 — 更新 task-progress
- ✅ `task-progress/projects/campus-task-complete.md` 已创建
