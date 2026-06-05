---
name: skill-manager
description: '技能管理器 Agent — 任务入口路由。接任务→查注册表→分配技能→加载上下文→转交执行。是整个技能体系的调度中枢'
tags: [core, router, orchestrator, manager]
related_skills: [architecture-constraints, error-registry, task-progress, browser-automation, cli-anything, computer-use-mcp]
---

# 🧠 技能管理器 Agent (Skill Manager)

> **角色**: 技能注册表 + 参考路由。我是**信息源**，不是**决策者**。
> **决策者**: `guidance-agent` 根据 Phase 0 "随机应变"原则做最终路由决策。
> **我的职责**: 提供完整的技能列表、用途描述、挂载策略供 guidance-agent 参考。

---

## 1. 技能注册表 (Master Registry)

以下注册表列出了所有可用的技能及其路由规则。**必须**按此表分配。

### 📗 核心管理 (全时挂载)

| 技能 | 位置 | 用途 | 挂载策略 |
|:-----|:-----|:-----|:---------|
| `architecture-constraints` | `devops/` | 架构约束、层级规则、错误级联、复盘流程 | **全时挂载** |
| `error-registry` | `devops/` | 报错表——所有已知错误及修复方案 | **全时挂载** |
| `task-progress` | `devops/` | 进度追踪——跨会话恢复上下文 | **复杂任务自动挂载** |

### 📘 浏览器自动化 (仅网页任务)

| 技能 | 位置 | 用途 | 触发条件 |
|:-----|:-----|:-----|:---------|
| `browser-automation` | `browser-automation/` | 伞技能——决策树，判断用哪层 | 任何网页交互任务 |
| `layer1-playwright` | `browser-automation/` | Playwright DOM 自动化 | 标准网页表单/点击 |
| `layer2-cdp-harness` | `browser-automation/` | CDP 连接 + bhts | React SPA/登录态保留 |
| `layer3-browser-use` | `browser-automation/` | AI 驱动浏览器自动化 | 复杂/动态页面 |
| `layer4-screenshot-vision` | `browser-automation/` | 截图视觉流 | CAPTCHA/Canvas/DOM 失败 |

### 📙 CLI-Anything 生态 (软件封装任务)

| 技能 | 位置 | 用途 | 触发条件 |
|:-----|:-----|:-----|:---------|
| `cli-anything` | `browser-automation/` | CLI-Anything 集成总览 | 用户要求操控桌面软件 |
| `cli-anything-hermes` | `(root)` | Harness 构建/测试/验证 | 为 GUI 软件建 CLI 包装层 |
| `cli-hub-meta-skill` | `(root)` | CLI-Hub 浏览/安装 | 需要搜索/安装新 CLI |

### 📕 桌面操控 (仅桌面任务)

| 技能 | 位置 | 用途 | 触发条件 |
|:-----|:-----|:-----|:---------|
| `computer-use-mcp` | `browser-automation/` | 鼠标/键盘/截图/剪贴板 MCP | 用户要求操控桌面 |

### 🎯 特定领域

| 技能 | 位置 | 用途 | 触发条件 |
|:-----|:-----|:-----|:---------|
| `ucampus-auto-complete` | `u-campus/` | U校园 AI版 自动答题 | U校园作业任务 |
| (其他 U校园) | `u-campus-course-automation/` | U校园全流程指南 | 同上 |

### 🤖 Agent Team (团队编排)

| 技能 | 位置 | 角色 | 触发条件 |
|:-----|:-----|:-----|:---------|
| `guidance-agent` | `devops/` | **指挥官** — 倾听/推理/分配技能 | **始终先加载** |
| `agent-developer` | `devops/` | 开发工程师 — 编码实现 | Guidance 分配后 |
| `agent-debugger` | `devops/` | 调试工程师 — 纠错修复 | 遇到错误时 |
| `agent-executor` | `devops/` | 实操工程师 — 浏览器/桌面/CLI | Guidance 分配后 |
| `agent-logger` | `devops/` | 日志工程师 — 进度/复盘 | 始终后台运行 |

---

## 2. 路由参考 (Routing Reference)

> **⚠️ 重要**: 以下路由规则是**参考性指引**，不是硬性规则。
> 实际路由必须由 `guidance-agent` 按 Phase 0 "随机应变"原则动态判断。
> 关键词匹配仅供参考，不应替代倾听用户的实际需求。

```yaml
核心原则: 先倾听，再判断，不预设分类。

正确做法:
  ├─ 听用户说完 → 理解具体需求 → 按需选技能
  ├─ 不确定时 → 加载最少必要技能 → 逐步补充
  ├─ 用户纠正 → 立即调整 → 记入 error-registry (CTX_OVERLOAD)
  └─ 每次独立判断 → 同一个用户的不同请求可能不同

不正确的做法:
  ├─ "浏览器任务必须加载X、编码任务必须加载Y" → ❌ 太刚性
  ├─ 大段的 "if 关键词匹配...elif...else" → ❌ 替代了倾听
  └─ "禁止加载" 写死 → ❌ 同一个工具在不同场景都有用
```

### 常见场景参考 (仅做参考，不是规则)

```yaml
接任务 → 判断任务类型 → 查注册表 → 分配技能 → 加载 → 执行

任务类型判断规则:
  if 关键词匹配 "U校园" or "uai.unipus" or "读写教程" or "英语":
    → 路由: u-campus 相关技能
    → 禁止加载: computer-use-mcp, cli-anything

  elif 关键词匹配 "打开网页" or "爬取" or "自动登录" or "浏览器" or "网页":
    → 路由: browser-automation (伞) + error-registry
    → Layer 选择: 
        标准 DOM → L1 Playwright
        React/SPA → L2 CDP
        未知结构 → L3 browser-use
        CAPTCHA → L4 Screenshot Vision
    → 禁止加载: computer-use-mcp, cli-anything

  elif 关键词匹配 "桌面" or "鼠标" or "截图" or "键盘" or "操控电脑":
    → 路由: computer-use-mcp + error-registry
    → 禁止加载: browser-automation, cli-anything

  elif 关键词匹配 "CLI" or "命令行" or "harness" or "封装" + "软件":
    → 路由: cli-anything + cli-anything-hermes + error-registry
    → 禁止加载: browser-automation, computer-use-mcp

  elif 关键词匹配 "实验报告" or "操作系统" or "[用户姓名]" or "[学号]":
    → 路由: 实验报告流程 (阅兵时看 memory)
    → 禁止加载: L2-L4 全部自动化工具

  else:  # 纯开发/编码/未分类
    → 路由: error-registry (仅查历史错误)
    → 不加载任何 L2-L4 自动化技能
```

---

## 3. 执行前检查 (Pre-Execution)

路由完成后，执行前快速确认：

```yaml
☐ 加载了 guidance-agent?               (任务指挥官)
☐ 加载了 error-registry?                (查历史错误)
☐ 加载的技能是否确实必要?                (不是越多越好)
☐ 有进行中的任务? → 查 task-progress    (避免重复)
☐ 有相关历史错误? → 查 error-registry   (避免 REPEAT_ERROR)
```

---

## 4. 调用方法

```bash
# 方法1: 直接加载本技能
skill_view(name='skill-manager')
# → 会自动加载注册表中 marked 为"全时挂载"的技能

# 方法2: 查注册表
# → 看完这个 SKILL.md 就知道所有可用技能及其用途

# 方法3: 更新注册表
# → 新技能创建后，同步更新本文件的 "技能注册表" 部分
```

---

## 5. 路由示例 (仅供参考)

> ⚠️ 以下示例只是"过去某个任务这么路由过"，不是"以后同类任务必须这么路由"。

| 用户说 | 过去的一次路由结果 |
|:-------|:-----------------|
|:-------|:---------|
| "去U校园做Unit 3" | `ucampus-auto-complete`, `error-registry`, `task-progress` |
| "帮我打开百度" | `browser-automation`(伞) → L1 Playwright, `error-registry` |
| "操控屏幕截图" | `computer-use-mcp`, `error-registry` |
| "给Blender建个CLI" | `cli-anything`, `cli-anything-hermes`, `error-registry` |
| "写个Python爬虫" | `error-registry` 仅查错, 不加载自动化 |
| "做操作系统实验报告" | 实验报告技能 + `error-registry`, 不加载自动化 |

---

## 6. 注册表维护规则

```
添加新技能时:
  1. 创建 SKILL.md (frontmatter: name, description, category, tags, related_skills)
  2. 更新本文件 "技能注册表" 部分
  3. 添加到对应层的路由规则

删除技能时:
  1. 从本文件移除注册表条目
  2. 从路由规则移除
  3. 记入 error-registry "废弃技能"
```
