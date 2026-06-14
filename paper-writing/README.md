---
name: paper-writing
description: '📝 论文/报告写作体系 — 多Agent协作完成学术论文、研究报告、文献综述'
tags: [research, paper, report, writing, academic]
related_skills: [arxiv, research-paper-writing, agent-team/paper-agent-*]
---

# 📝 论文/报告写作体系

> **参考来源**: [Feynman](https://feynman.is) (开源AI研究Agent)、Hermes Agent `research-paper-writing` skill、LlamaIndex 多Agent报告生成

## 架构概览

```
用户提问/需求
    │
    ▼
┌─────────────────────────────────────┐
│  paper-agent-coordinator (总指挥)    │
│  • 分析需求 → 组装子Agent团队       │
│  • 按工作流分配给对应Agent          │
│  • 质量控制 → 最终交付              │
└────────┬────────┬────────┬──────────┘
         │        │        │
    ┌────┘   ┌────┘   ┌───┘
    ▼        ▼        ▼
┌────────┐ ┌────────┐ ┌────────┐
│Researcher││ Writer ││Reviewer│
│ 文献研究 ││ 撰写   ││ 审稿   │
│ 搜索/分析││ 排版   ││ 引用   │
│ 摘要/笔记││ 图表   ││ 验证   │
└────────┘ └────────┘ └────────┘
    │              │        │
    └──────────────┴────────┘
              ▼
        最终论文/报告
```

## Agent 角色

| Agent | 职责 | 对应 Feynman 等效 |
|:------|:-----|:-----------------|
| **Coordinator** | 总指挥 — 分析需求、组装子Agent、迭代控制、最终交付 | — |
| **Researcher** | 文献研究 — 搜索论文、阅读摘要、提取关键信息、发现研究空白 | `Researcher` |
| **Writer** | 写作排版 — 撰写论文/报告、生成图表、LaTeX排版 | `Writer` |
| **Reviewer** | 审稿验证 — 审阅内容、验证引用、检查格式、返回修改建议 | `Reviewer` + `Verifier` |

## 工作流

### 1️⃣ Deep Research（深度研究）— 多Agent并行
```
需求 → Coordinator 拆解研究方向
     → Researcher 并行搜索多个角度
     → Researcher2 交叉验证文献
     → Coordinator 综合 → Writer 结构化笔记
     → Reviewer 验证引用 → 产出研究报告
```

### 2️⃣ Literature Review（文献综述）
```
需求 → Researcher 多轮迭代搜索 (广度→深度→针对性)
     → 提取关键信息 → 共识/分歧分析
     → Writer 按模板撰写综述
     → Reviewer 验证每条引用 → 文献综述
```

### 3️⃣ Paper Draft（论文撰写）
```
实验数据/笔记 → Researcher 查全相关文献
     → Writer 撰写初稿 (Idea→Method→Results→Discussion)
     → Reviewer 模拟同行审稿 (严重度分级)
     → Writer 修订 → Reviewer 再验证 → 定稿
```

### 4️⃣ Report Writing（报告撰写）
```
项目数据/需求 → Researcher 查找背景资料
     → Writer 按报告模板撰写 (背景→方法→结果→结论)
     → Reviewer 检查完整性和一致性
     → 产出可交付报告
```

## 与 Feynman 的整合

Feynman 是独立于 Hermes 的开源研究Agent。两种使用方式：

### 方式 A：直接安装 Feynman CLI
```bash
curl -fsSL https://feynman.is/install | bash
# 使用 Feynman 的工作流
feynman deepresearch "your topic"
feynman lit "your topic"       # 文献综述
feynman draft "your topic"     # 论文初稿
feynman audit <arxiv-id>       # 论文审计
```

### 方式 B：Hermes Agent 通过 delegate_task 调用
Coordinator 使用 `delegate_task` 并行调用子Agent，各子Agent利用 Hermes 内置工具：
- `arxiv` skill → 论文搜索
- `web_search` / `web_extract` → 网络资料收集
- `vision_analyze` → 图片/图表分析
- `research-paper-writing` skill → 学术论文写作流程

## 引用验证规则（强制）

**引用错误率约 40%** — 必须验证每条引用：

```
1. 搜索 → Semantic Scholar / arXiv API 确认论文存在
2. 验证 → 确认引用内容确实出现在原文中
3. 检索 → 通过 DOI 获取 BibTeX
4. 添加 → 使用已验证的 BibTeX
5. 若有任何一步失败 → 标记为 [CITATION NEEDED]
```

## 目录结构

```
paper-writing/
├── README.md                       ← 本说明
├── templates/                       ← 写作模板
│   ├── paper-template.md            ← 学术论文模板
│   ├── report-template.md           ← 报告模板
│   └── literature-review-template.md← 文献综述模板
└── workflows/                       ← 工作流定义
    ├── deepresearch-workflow.md     ← 深度研究
    ├── lit-review-workflow.md       ← 文献综述
    ├── paper-draft-workflow.md      ← 论文撰写
    └── report-writing-workflow.md   ← 报告撰写
```

## 与现有体系的关系

| 体系 | 交互方式 |
|:-----|:---------|
| **agent-team** | paper-agent-* 是 agent-team 的扩展（专门面向论文/报告写作） |
| **event-report** | 每次论文写作项目完成后记录到 event-report |
| **error-registry** | 写作过程中的已知错误（引用错误、格式问题等）记入 |
| **architecture-constraints** | 遵循现有架构约束（Post-Task 复盘等） |
| **tasks-progress** | 复杂论文项目使用 task-progress 追踪进度 |
