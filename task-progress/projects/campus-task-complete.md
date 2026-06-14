# 任务进度: CampusTask 全部 8 实验

- 任务ID: campus-task-8exp
- 创建: 2026-06-14 09:22
- 更新: 2026-06-14 09:35
- 阶段: ✅ 全部完成

## ☑️ 已完成

- [x] 实验1: MVP (main.py + 5 用户故事) → ✅
- [x] 实验2: 模块化设计 (model/storage/service/main) → ✅
- [x] 实验3: 测试 (20 pytest 用例 + bug 引入修复) → ✅
- [x] 实验4: Git (2 分支 × 3 commits + 冲突 + 评审) → ✅
- [x] 实验5: 迭代 (3 反馈 + deadline排序 + CSV导出) → ✅
- [x] 实验6: CI (pyproject.toml + GitHub Actions) → ✅
- [x] 实验7: 发布 (包结构 + argparse + 日志 + bug修复) → ✅
- [x] 实验8: AI Harness (7 模块 + 10 eval + trace) → ✅
- [x] 框架合规: 项目结构重构 (SPEC + exec-plans + decisions) → ✅

## 🧠 关键决策

- JSON 文件存储 (零依赖) — ADR-001
- 4 模块拆分 — ADR-002
- done = 状态标记，非删除 — ADR-003
- mock_model 关键词匹配 (可替换为真实 API) — ADR-004
- 空标题拒绝 (ValueError) — 实验 3 要求严格
- 空文件不崩溃 (返回空列表) — 实验 7 bug 修复
