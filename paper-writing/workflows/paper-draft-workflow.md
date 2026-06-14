# ✍️ 论文撰写工作流

> **参考**: Hermes `research-paper-writing` Phase 5-7 + Feynman `/draft`
> **用途**: 从实验数据/研究笔记撰写学术论文

## 流程

```
Phase 0: 项目设置 (Coordinator)
  ├─ 明确目标会议/期刊
  ├─ 确定贡献点（一句话）
  ├─ 建立workspace结构
  │   paper/           ← LaTeX源码
  │   experiments/     ← 实验脚本
  │   code/            ← 核心实现
  │   results/         ← 实验结果
  │   figures/         ← 图表
  └─ 估算计算预算
      │
Phase 1: 文献查全 (Researcher)
  ├─ 搜索相关文献，确保基线完整
  └─ 输出：论文列表 + 引用BibTeX
      │
Phase 2: 实验验证 (如有需要)
  └─ 确认关键结果可复现
      │
Phase 3: 论文撰写 (Writer)
  ├─ 标题 + 摘要
  ├─ 引言 (背景 → 问题 → 贡献)
  ├─ 方法 (问题形式化 → 方法描述)
  ├─ 实验 (设置 → 主要结果 → 消融 → 分析)
  ├─ 讨论/结论
  └─ 参考文献（使用已验证的BibTeX）
      │
Phase 4: 自我审稿 (Reviewer)
  ├─ 严重度分级审稿
  ├─ 引用验证（强制）
  ├─ LaTeX编译检查
  └─ 提交审稿报告
      │
Phase 5: 修改迭代 (Writer)
  └─ 根据审稿报告逐条修改（最多3轮）
      │
Phase 6: 最终检查 (Reviewer)
  └─ 确认所有 Critical/Major 已解决
      │
Phase 7: 交付 (Coordinator)
  ├─ 论文PDF
  ├─ LaTeX源码
  └─ 补充材料
      │
Post-Task: 日志
```

## 项目Workspace结构

```
paper/
├── paper.tex              ← 主LaTeX文件
├── references.bib          ← 已验证的引用
├── figures/                ← 图表
├── sections/               ← 分章节 (可选)
│   ├── 01-introduction.tex
│   ├── 02-related.tex
│   ├── 03-method.tex
│   ├── 04-experiments.tex
│   └── 05-conclusion.tex
├── output/                 ← 编译产出
└── Makefile                ← 编译命令
```

## 写作原则

1. **先说贡献，再讲背景** — 读者需要先知道为什么值得读
2. **每段一个论点** — 每段的首句就是该段的主题
3. **图表自解释** — 标题+图注释应该能独立理解
4. **实验结果要讲故事** — 数字本身无意义，意义来自对比和解释
5. **从不虚构引用** — 已验证的引用才能用
