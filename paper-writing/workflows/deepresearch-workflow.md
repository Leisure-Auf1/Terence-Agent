# 🔬 Deep Research 工作流

> **参考**: Feynman `/deepresearch` — 多Agent并行深度研究
> **用途**: 对一个课题进行多角度的深度研究，输出结构化研究报告

## 流程

```
Phase 1: 需求分析 (Coordinator)
  ├─ 拆解研究问题为多个子方向
  └─ 确定搜索策略
      │
Phase 2: 并行搜索 (Researcher × N)
  ├─ Researcher-A: 方法/技术角度
  ├─ Researcher-B: 应用/场景角度
  ├─ Researcher-C: 最新进展 (近6个月)
  └─ 每2小时内完成
      │
Phase 3: 综合与交叉验证 (Coordinator)
  ├─ 合并搜索发现
  ├─ 交叉验证关键结果
  ├─ 识别共识与分歧
  └─ 标记待深入的问题
      │
Phase 4: 深度分析 (Researcher)
  └─ 对标记的问题做第二轮深入研究
      │
Phase 5: 写作 (Writer)
  ├─ 按报告模板组织内容
  ├─ 生成图表（如有数据）
  └─ 标记引用位置
      │
Phase 6: 审稿 (Reviewer)
  ├─ 验证每条引用
  ├─ 内容完整性检查
  └─ 返回审稿报告
      │
Phase 7: 迭代 (Coordinator)
  ├─ 根据 Reviewer 反馈 → Writer 修改
  └─ 最多3轮迭代
      │
Phase 8: 交付 (Coordinator)
  └─ 最终研究报告
      │
Post-Task: 日志记录
  ├─ event-report 记录
  └─ 是否保存为新 skill？
```

## 适用场景

- 新课题的快速入门研究
- 技术选型的多维度评估
- 竞品/领域分析
- 论文开题前的文献摸底
