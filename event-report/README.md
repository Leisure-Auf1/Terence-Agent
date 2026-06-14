---
name: event-report
description: '📋 事件报告 — 按日记录操作日志，与 error-registry（仅记录错误）分开'
tags: [log, tracking, operations]
---

# 📋 事件报告

> **用途**: 按日记录所有操作，与 `error-registry/`（只记错误码+修复方案）完全分开。
>
> **原则**: 事件报告=发生了什么，报错表=出了什么错。

## 规则

```
1. 每天一个文件 → event-report/YYYY-MM-DD.md
2. 每条记录包含：时间 | 操作描述 | 结果 | 关联文件/链接
3. 错误本身 → 仍在 error-registry 记录
4. 事件报告追踪"我今天做了什么"，而非"我修了什么错"
5. 一条操作可同时出现在 event-report（操作记录）和 error-registry（错误记录）
```

## 目录结构

```
event-report/
├── README.md           ← 本说明
├── 2026-06-14.md       ← 今天的事件日志
└── ...
```

## 条目格式

```markdown
### HH:MM — 操作类型

**描述**: 具体做了什么

**结果**: ✅ 成功 / ❌ 失败 / ⏳ 进行中 / 🔄 中止

**产出**:
- `路径/到/文件` — 说明
- `路径/到/产出` — 说明

**关联**:
- error-registry: `错误码`（如有）
- PR/Issue: `#NN`（如有）
```

## 操作类型

| 类型 | 图标 | 说明 |
|:-----|:----:|:-----|
| 开发 | 🛠️ | 编码、调试、实现功能 |
| 执行 | ⚡ | 运行脚本、测试、自动化 |
| 配置 | ⚙️ | 安装、配置、环境调整 |
| 修复 | 🔧 | 排查并修复问题 |
| 学习 | 📖 | 查阅文档、上网搜索 |
| 管理 | 📋 | 日志、规划、仓库维护 |
| 设计 | 🎨 | 架构设计、UI/UX |
| 同步 | 🔄 | Git 提交、同步 |

## 与 error-registry 的关系

```
event-report/2026-06-14.md
├─ 09:00 — 配置 DeepSeek API       ← 操作记录
├─ 09:30 — 🔧 修复超时错误          ← 操作记录
│   └─ 关联: error-registry: `TIMEOUT_120`  ← 指向错误
└─ 10:00 — 部署上线                ← 操作记录

error-registry/README.md
├─ L0 | `TIMEOUT_120` | 根因 | 修复方案  ← 只记错误
```

⚠️ **事件报告不替代 error-registry**：发现新错误时，仍然要往 `error-registry/README.md` 追加错误码+根因+修复方案。
