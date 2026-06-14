# 代跑代课·校园互助 — 实现规范文档

> **项目定位**：移动端优先的轻量级校园互助 SPA，基于 HTML + CSS + Vanilla JS 实现，数据全部存储在 localStorage。
>
> **项目目录**：`/home/Terence/.hermes/tasks/agent-team-demo-2/`
>
> **引用关系**：`index.html` → `style.css`（`<link>`）、`app.js`（`<script defer>`）

---

## 一、数据模型（localStorage JSON Schema）

### 1.1 `campus_tasks` — 需求列表

```json
[
  {
    "id": "task_1717500000000_xxxx",
    "type": "errand",           // "errand"=代跑, "class"=代课
    "typeLabel": "代跑",
    "courseName": "高等数学",
    "dateTime": "2025-06-10T14:30",
    "location": "二教 301",
    "price": "15",
    "contact": "微信: student123",
    "note": "麻烦跑快点",
    "publisher": "小宇宙",       // 发布者昵称
    "status": "open",           // "open"=可接单, "taken"=已被接
    "takenBy": null,            // 接单者昵称，未接时为 null
    "createdAt": 1717500000000  // 时间戳
  }
]
```

### 1.2 `campus_nickname` — 当前用户昵称

```json
"小宇宙"
```

值类型：字符串，为空字符串 `""` 表示未设置。

### 1.3 首次加载逻辑

在 `app.js` 的初始化函数中检测 `campus_tasks` 是否存在。若**不存在或为空数组**，则写入以下 4 条预置演示数据（id 用实际时间戳生成）：

| 类型 | 课程 | 日期时间 | 地点 | 价格 | 联系方式 | 备注 | 发布者 | 状态 |
|------|------|----------|------|------|----------|------|--------|------|
| 代跑 | 高等数学作业 | 2025-06-10 14:30 | 二教 301 | 15 元 | 微信: help1 | 帮忙去老师办公室交作业 | 校园跑腿侠 | open |
| 代课 | 大学英语 | 2025-06-11 08:00 | 外语楼 205 | 25 元 | QQ: 123456 | 需要回答问题 | 代课达人 | open |
| 代跑 | 体育打卡 | 2025-06-12 06:30 | 北区操场 | 10 元 | 短信: 138xxxx | 跑步 2 公里配速不限 | 早起鸟 | open |
| 代课 | 毛概 | 2025-06-13 14:00 | 阶梯教室 A | 20 元 | 微信: maogai | 坐后排不提问 | 热心同学 | taken (被接) |

> **⚠️ 隐私要求**：以上演示数据发布者昵称为虚构角色名，不得出现任何真实姓名或硬编码用户名。用户昵称由用户在界面上自行输入。

---

## 二、文件职责边界

| 文件 | 职责范围 | 禁止做的事 |
|------|----------|-----------|
| **index.html** | 页面结构骨架、所有 DOM 元素声明、外部资源引用 | 不包含任何样式（`<style>`）、不包含任何业务逻辑（`<script> inline`） |
| **style.css** | 所有视觉样式、动画、响应式布局 | 不定义任何布局结构、不写任何 JS 逻辑 |
| **app.js** | 所有业务逻辑、数据读写、DOM 操作、事件绑定 | 不写任何 HTML 标签、不写样式规则 |

---

## 三、index.html — 页面结构规范

### 3.1 整体骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>代跑代课·校园互助</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <!-- 所有内容容器 -->
  <div id="app">
    <!-- 1. 导航栏 -->
    <!-- 2. 昵称设置栏 -->
    <!-- 3. Tab 导航 -->
    <!-- 4. 页面内容区 -->
    <!-- 5. Toast 容器 -->
  </div>
  <script defer src="app.js"></script>
</body>
</html>
```

### 3.2 导航栏（`#app > header#main-header`）

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 容器 | `<header id="main-header" class="main-header">` | 固定顶部，flex 布局 |
| 标题 | `<h1 id="site-title">代跑代课·校园互助</h1>` | 站点主标题 |
| 昵称设置按钮 | `<button id="nickname-btn" class="nickname-btn">设置昵称</button>` | 点击弹出昵称输入 |

### 3.3 昵称输入弹窗（`#app > div#nickname-modal`）

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 遮罩层 | `<div id="nickname-modal" class="modal-overlay hidden">` | 半透明黑色遮罩 |
| 弹窗卡片 | `<div class="modal-card">` | 白色圆角卡片 |
| 标题 | `<h3>设置昵称</h3>` | — |
| 输入框 | `<input type="text" id="nickname-input" class="modal-input" placeholder="请输入你的昵称" maxlength="12">` | — |
| 确认按钮 | `<button id="nickname-confirm" class="btn btn-primary">确认</button>` | 保存并关闭 |
| 取消按钮 | `<button id="nickname-cancel" class="btn btn-secondary">取消</button>` | 仅关闭 |

### 3.4 Tab 导航（`#app > nav#tab-nav`）

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 容器 | `<nav id="tab-nav" class="tab-nav">` | flex 三栏 |
| Tab 1 | `<button class="tab-btn active" data-tab="publish">发布需求</button>` | — |
| Tab 2 | `<button class="tab-btn" data-tab="list">需求列表</button>` | — |
| Tab 3 | `<button class="tab-btn" data-tab="mine">我的发布</button>` | — |

### 3.5 页面内容区（`#app > main#main-content`）

三个面板以 `class="tab-panel"` + `data-panel` 区分，一次只显示一个。

**3.5.1 发布表单面板** `#panel-publish`

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 容器 | `<div class="tab-panel active" id="panel-publish" data-panel="publish">` | — |
| 表单 | `<form id="publish-form">` | — |
| 类型选择容器 | `<div class="form-group">` | — |
| 类型标签 | `<label>需求类型</label>` | — |
| 代跑按钮 | `<button type="button" class="type-btn active" data-type="errand">🏃 代跑</button>` | 选中态 class="type-btn active" |
| 代课按钮 | `<button type="button" class="type-btn" data-type="class">📚 代课</button>` | 普通态 class="type-btn" |
| 课程名称 | `<input type="text" id="form-course" class="form-input" placeholder="课程名称 / 作业描述" required>` | — |
| 日期时间 | `<input type="datetime-local" id="form-datetime" class="form-input" required>` | — |
| 地点 | `<input type="text" id="form-location" class="form-input" placeholder="上课 / 交接地点" required>` | — |
| 价格 | `<input type="number" id="form-price" class="form-input" placeholder="酬劳（元）" min="0" step="0.5" required>` | — |
| 联系方式 | `<input type="text" id="form-contact" class="form-input" placeholder="微信 / QQ / 手机号" required>` | — |
| 备注 | `<textarea id="form-note" class="form-textarea" placeholder="其他要求（可选）" rows="3"></textarea>` | — |
| 提交按钮 | `<button type="submit" id="form-submit" class="btn btn-primary btn-block">确认发布</button>` | — |

**3.5.2 需求列表面板** `#panel-list`

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 容器 | `<div class="tab-panel" id="panel-list" data-panel="list">` | — |
| 筛选栏 | `<div class="filter-bar" id="filter-bar">` | — |
| 全部按钮 | `<button class="filter-btn active" data-filter="all">全部</button>` | — |
| 代跑按钮 | `<button class="filter-btn" data-filter="errand">代跑</button>` | — |
| 代课按钮 | `<button class="filter-btn" data-filter="class">代课</button>` | — |
| 卡片列表 | `<div id="task-list" class="task-list">` | JS 动态渲染卡片至此 |

**3.5.3 我的发布面板** `#panel-mine`

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 容器 | `<div class="tab-panel" id="panel-mine" data-panel="mine">` | — |
| 标题 | `<h2 class="panel-title">我的发布</h2>` | — |
| 卡片列表 | `<div id="mine-list" class="task-list">` | JS 动态渲染 |

### 3.6 Toast 通知容器（`#app > div#toast-container`）

| 元素 | 标签 / id / class | 说明 |
|------|-------------------|------|
| 容器 | `<div id="toast-container" class="toast-container"></div>` | 固定在底部居中，JS 动态插入 `.toast` 元素 |

---

### 3.7 任务卡片模板（JS 动态生成）

以下结构由 `app.js` 的 `renderTaskCard()` 函数生成，此处仅约定 HTML 结构：

```html
<div class="task-card" data-task-id="task_xxx">
  <div class="task-card__header">
    <span class="task-type-badge task-type--errand">代跑</span>
    <span class="task-status-badge task-status--open">可接单</span>
    <!-- or: <span class="task-status-badge task-status--taken">已被接</span> -->
    <span class="task-publisher">发布者：小宇宙</span>
  </div>
  <div class="task-card__body">
    <h3 class="task-course">高等数学作业</h3>
    <div class="task-detail">
      <span class="task-detail__item">📅 2025-06-10 14:30</span>
      <span class="task-detail__item">📍 二教 301</span>
      <span class="task-detail__item">💰 15 元</span>
      <span class="task-detail__item">📞 微信: student123</span>
    </div>
    <p class="task-note">备注：麻烦跑快点</p>
  </div>
  <div class="task-card__footer">
    <button class="btn btn-accept" data-task-id="task_xxx">接单</button>
    <!-- 或（已被接 / 自己的单时禁用）:
    <button class="btn btn-accept btn-accept--disabled" disabled>不可接单</button> -->
  </div>
</div>
```

---

## 四、style.css — 样式规范

### 4.1 CSS 变量（`:root`）

```css
:root {
  --color-primary: #4f46e5;
  --color-primary-light: #818cf8;
  --color-primary-dark: #3730a3;
  --color-primary-bg: #eef2ff;
  --color-accent: #f59e0b;
  --color-success: #10b981;
  --color-danger: #ef4444;
  --color-text: #1e293b;
  --color-text-secondary: #64748b;
  --color-bg: #f8fafc;
  --color-card: #ffffff;
  --color-border: #e2e8f0;
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
  --shadow-md: 0 4px 14px rgba(0,0,0,0.10);
  --transition: all 0.25s ease;
}
```

### 4.2 响应式断点

| 断点 | 说明 |
|------|------|
| `320px - 480px` | 小屏手机，padding: 12px |
| `481px - 768px` | 大屏手机 / 小平板，padding: 20px，字号微调 |
| `768px+` | 桌面端，max-width: 720px 居中容器 |

### 4.3 组件样式约定

| 组件 | class / 选择器 | 关键样式 |
|------|---------------|----------|
| 导航栏 | `.main-header` | 固定顶部（`position: sticky; top:0`），z-index 100，紫色渐变背景（`linear-gradient(135deg, #4f46e5, #7c3aed)`），白色文字，flex 布局 |
| 昵称按钮 | `.nickname-btn` | 圆角，浅色背景，hover 变亮 |
| 弹窗遮罩 | `.modal-overlay` | fixed 全屏，半透明黑底（`rgba(0,0,0,0.4)`），居中 flex，z-index 200 |
| 弹窗卡片 | `.modal-card` | 白色圆角卡片，`max-width: 340px`，动画 `scale(0.9)→scale(1)` 入场 |
| Tab 导航 | `.tab-nav` | 贴紧导航栏下方，flex 三栏等宽，底部有指示条（`border-bottom: 2px solid var(--color-border)`），选中态 `.tab-btn.active` 有紫色下划线 `border-bottom-color: var(--color-primary)` |
| 面板 | `.tab-panel` | 默认 `display: none`，`.active` 时 `display: block`，带淡入动画 |
| 表单 | `.form-group` | 纵向排列，`margin-bottom: 16px` |
| 表单输入 | `.form-input` / `.form-textarea` | 全宽，`border: 1px solid var(--color-border)`，focus 时紫色边框 + `box-shadow` |
| 类型选择按钮 | `.type-btn` | 内联块，选中态 `.type-btn.active` 紫色实心背景白色文字，非选中态浅灰边框 |
| 主按钮 | `.btn-primary` | 紫色渐变背景，白色文字，圆角，hover 加深 |
| 块级按钮 | `.btn-block` | `width: 100%` |
| 筛选按钮 | `.filter-btn` | 小圆角胶囊形，`.active` 紫色实心，非选中态浅灰 |
| 卡片列表 | `.task-list` | 纵向 `gap: 16px`，flex 列 |
| 任务卡片 | `.task-card` | 白色卡片，`border-radius: var(--radius-md)`，`box-shadow: var(--shadow-sm)`，hover 时 `shadow-md` 上移 2px 过渡 |
| 类型标签 | `.task-type-badge` | 小圆角标签，`.task-type--errand` 紫色，`.task-type--class` 橙色 |
| 状态标签 | `.task-status-badge` | 小圆角标签，`.task-status--open` 绿色（`#10b981`），`.task-status--taken` 灰色（`#94a3b8`） |
| 接单按钮 | `.btn-accept` | 绿色背景，白色文字，禁用态 `.btn-accept--disabled` 灰色不可点击 |
| Toast 容器 | `.toast-container` | `position: fixed; bottom: 80px; left: 50%; transform: translateX(-50%);`，z-index 300 |
| Toast 元素 | `.toast` | 最小宽度 200px，暗色背景白色文字，圆角，入场 `translateY(20px)→0` + `opacity` 过渡，2.5s 后自动消失 |

### 4.4 过渡动画

| 场景 | 过渡属性 |
|------|---------|
| Tab 切换 | `opacity 0.3s ease` |
| 卡片 hover | `transform 0.25s ease, box-shadow 0.25s ease` |
| 弹窗显示 | `transform 0.25s ease, opacity 0.25s ease` |
| Toast 出现/消失 | `transform 0.35s ease, opacity 0.35s ease` |
| 按钮 hover | `background-color 0.2s ease, transform 0.15s ease` |

---

## 五、app.js — 逻辑规范

### 5.1 函数签名总表

| 函数 | 签名 | 返回值 | 说明 |
|------|------|--------|------|
| `initApp()` | `() => void` | `undefined` | 应用入口：检查 localStorage → 初始化数据 → 绑定事件 → 渲染 |
| `initDemoData()` | `() => void` | `undefined` | 首次加载时写入 4 条预置演示数据到 `campus_tasks` |
| `getTasks()` | `() => Array` | `Task[]` | 从 localStorage 读取 `campus_tasks`，返回数组（空则 `[]`） |
| `saveTasks(tasks)` | `(Array) => void` | `undefined` | 将任务数组序列化写入 `campus_tasks` |
| `getNickname()` | `() => string` | 昵称或 `""` | 从 localStorage 读取 `campus_nickname` |
| `saveNickname(name)` | `(string) => void` | `undefined` | 保存昵称到 `campus_nickname` |
| `isLoggedIn()` | `() => boolean` | `true/false` | 昵称非空即已登录 |
| `generateId()` | `() => string` | `"task_时间戳_随机4位"` | 生成唯一任务 ID |
| `switchTab(tabName)` | `(string) => void` | `undefined` | 切换 Tab：更新 `.tab-btn` 选中态 + `.tab-panel` 显示隐藏 |
| `handlePublish(e)` | `(Event) => void` | `undefined` | 发布表单提交处理：验证 → 构造 Task → 存入 → Toast → 刷新 |
| `validateForm()` | `() => string/true` | `true` 或错误消息 | 表单验证：全部必填字段非空 |
| `renderAllTasks(filter?)` | `(string?) => void` | `undefined` | 渲染全部/筛选后的任务卡片到 `#task-list` |
| `renderTaskCard(task)` | `(Task) => string` | HTML 字符串 | 生成单张任务卡片的 HTML |
| `renderMineTasks()` | `() => void` | `undefined` | 渲染当前用户发布的任务到 `#mine-list` |
| `handleAccept(taskId)` | `(string) => void` | `undefined` | 接单逻辑：校验 → 更新状态 → 保存 → Toast → 刷新 |
| `canAccept(task, currentUser)` | `(Task, string) => boolean` | `true/false` | 判定：状态必须为 open，且发布者 !== 当前用户，且 takenBy === null |
| `showToast(message, type?)` | `(string, string?) => void` | `undefined` | 显示 Toast 通知，type 取值 `"success"` / `"error"` / `"info"`，2.5s 后自动移除 |
| `openNicknameModal()` | `() => void` | `undefined` | 打开昵称设置弹窗，预填当前昵称 |
| `closeNicknameModal()` | `() => void` | `undefined` | 关闭弹窗 |
| `confirmNickname()` | `() => void` | `undefined` | 读取输入 → 保存 → 关闭 → 刷新昵称显示 → Toast |
| `updateNicknameDisplay()` | `() => void` | `undefined` | 更新导航栏昵称显示文字 |

### 5.2 事件绑定清单

所有事件绑定在 `initApp()` 中完成，采用 `addEventListener`，不使用 `onclick` 属性：

| DOM 元素 | 事件 | 处理函数 | 备注 |
|----------|------|---------|------|
| `#nickname-btn` | `click` | `openNicknameModal` | — |
| `#nickname-confirm` | `click` | `confirmNickname` | — |
| `#nickname-cancel` | `click` | `closeNicknameModal` | — |
| `#nickname-modal`（遮罩） | `click` | 点击遮罩本身（非卡片内）关闭 | 阻止卡片内冒泡 |
| `.tab-btn` | `click` | `(e) => switchTab(e.target.dataset.tab)` | 委托到 `#tab-nav` |
| `#publish-form` | `submit` | `handlePublish` | — |
| `.type-btn` | `click` | 切换 `.active` 类 | 单选互斥 |
| `.filter-btn` | `click` | 切换筛选 + 重新渲染 | 委托到 `#filter-bar` |
| `#task-list` | `click` | 委托 `.btn-accept` 点击 → `handleAccept` | — |

### 5.3 本地存储键名

| 键名 | 数据类型 | 默认值 | 说明 |
|------|---------|--------|------|
| `campus_tasks` | `Task[]` (JSON) | `[]` | 全部需求数据 |
| `campus_nickname` | `string` | `""` | 当前用户昵称 |

---

## 六、交互流程

### 6.1 页面初始化

```
用户打开页面
  → initApp()
    → 检测 campus_tasks 是否存在 / 为空
      → 若为空 → initDemoData() 写入 4 条预置数据
    → 读取 campus_nickname
    → updateNicknameDisplay() 更新导航栏
    → 绑定所有事件
    → renderAllTasks('all') 渲染需求列表
    → 默认显示第一个 Tab（发布需求 / 需求列表？约定：显示"需求列表"作为首页）
```

> **约定**：默认显示的 Tab 为"需求列表"（`data-tab="list"`），因为用户进入页面最想看到现有需求。

### 6.2 设置昵称

```
用户点击"设置昵称"
  → openNicknameModal()
    → 弹窗显示（移除 hidden 类）
    → 输入框聚焦

用户输入昵称后点击"确认"
  → confirmNickname()
    → 校验非空
    → saveNickname(name)
    → updateNicknameDisplay() 更新导航栏
    → closeNicknameModal()
    → showToast('昵称设置成功', 'success')

用户点击"取消"或遮罩
  → closeNicknameModal()
    → 弹窗添加 hidden 类
```

### 6.3 发布需求

```
用户切换到"发布需求"Tab → 填写表单 → 点击"确认发布"
  → submit 事件 → handlePublish(e)
    → e.preventDefault()
    → 校验是否已设置昵称（!isLoggedIn() → 提示先设置昵称）
    → validateForm() → 若失败 → showToast(错误信息, 'error') → return
    → 构造 Task 对象
      {
        id: generateId(),
        type: 选中的 type-btn 的 data-type,
        typeLabel: type === 'errand' ? '代跑' : '代课',
        courseName: form-course.value,
        dateTime: form-datetime.value,
        location: form-location.value,
        price: form-price.value,
        contact: form-contact.value,
        note: form-note.value || '',
        publisher: getNickname(),
        status: 'open',
        takenBy: null,
        createdAt: Date.now()
      }
    → getTasks() → push → saveTasks()
    → 重置表单
    → showToast('发布成功！', 'success')
    → 切换到"需求列表"Tab
    → renderAllTasks()
```

### 6.4 浏览与筛选需求

```
用户切换到"需求列表"Tab
  → switchTab('list')
    → 激活 #panel-list
    → renderAllTasks(当前选中的 filter)

用户点击筛选按钮（全部/代跑/代课）
  → click 切换 .filter-btn 的 active 类
  → renderAllTasks(选中的 data-filter)
    → getTasks()
    → 根据 filter 过滤
    → 按 createdAt 降序排列（最新的在前）
    → 遍历生成卡片 HTML → 插入 #task-list
```

### 6.5 接单

```
用户点击某张卡片上的"接单"按钮
  → 委托事件 → handleAccept(taskId)
    → 校验 isLoggedIn() → 否则 Toast '请先设置昵称'
    → getTasks() → find task by id
    → canAccept(task, currentUser)
      → task.status !== 'open' → Toast '该需求已被接' → return
      → task.publisher === currentUser → Toast '不能接自己的单' → return
      → task.takenBy !== null → Toast '该需求已被接' → return
    → 确认弹窗？简单场景直接执行 →
      task.status = 'taken'
      task.takenBy = getNickname()
    → saveTasks(tasks)
    → showToast('接单成功！', 'success')
    → renderAllTasks() / renderMineTasks() 刷新
```

> **UI 反馈**：接单后的卡片，"接单"按钮变为灰色禁用态，显示"已被接"文字；状态标签变为灰色"已被接"。

### 6.6 查看我的发布

```
用户切换到"我的发布"Tab
  → switchTab('mine')
    → 校验 isLoggedIn() → 否则 Toast '请先设置昵称' 并切回列表
    → renderMineTasks()
      → getTasks().filter(task => task.publisher === currentUser)
      → 按 createdAt 降序排列
      → 遍历生成卡片 HTML → 插入 #mine-list
```

### 6.7 Toast 通知生命周期

```
调用 showToast(message, type)
  → 创建 div.toast
    → 添加 .toast--success / .toast--error / .toast--info
    → 设置内联文字
  → 追加到 #toast-container
  → 下一个 animation frame 触发 opacity / transform 过渡
  → 2.5 秒后 → 添加淡出类 → 过渡结束 removeChild
```

---

## 七、命名规范速查表

### 7.1 ID 命名（全小写 kebab-case）

| ID | 所属元素 |
|----|---------|
| `#app` | 根容器 |
| `#main-header` | 导航栏 |
| `#site-title` | 站点标题 |
| `#nickname-btn` | 昵称设置按钮 |
| `#nickname-modal` | 昵称弹窗遮罩 |
| `#nickname-input` | 昵称输入框 |
| `#nickname-confirm` | 昵称确认按钮 |
| `#nickname-cancel` | 昵称取消按钮 |
| `#tab-nav` | Tab 导航栏 |
| `#main-content` | 主内容区 |
| `#panel-publish` | 发布需求面板 |
| `#panel-list` | 需求列表面板 |
| `#panel-mine` | 我的发布面板 |
| `#publish-form` | 发布表单 |
| `#form-course` | 表单-课程名称 |
| `#form-datetime` | 表单-日期时间 |
| `#form-location` | 表单-地点 |
| `#form-price` | 表单-价格 |
| `#form-contact` | 表单-联系方式 |
| `#form-note` | 表单-备注 |
| `#form-submit` | 表单-提交按钮 |
| `#filter-bar` | 筛选栏 |
| `#task-list` | 需求卡片列表容器 |
| `#mine-list` | 我的发布卡片列表容器 |
| `#toast-container` | Toast 容器 |

### 7.2 Class 命名（全小写 BEM 风格）

| Class | 用途 |
|-------|------|
| `.main-header` | 导航栏样式 |
| `.nickname-btn` | 昵称按钮 |
| `.modal-overlay` | 弹窗遮罩 |
| `.modal-card` | 弹窗卡片 |
| `.modal-input` | 弹窗输入框 |
| `.hidden` | 隐藏元素（`display: none`） |
| `.tab-nav` | Tab 导航栏容器 |
| `.tab-btn` | Tab 按钮 |
| `.tab-btn.active` | 选中 Tab |
| `.tab-panel` | 面板容器 |
| `.tab-panel.active` | 选中面板 |
| `.form-group` | 表单字段组 |
| `.form-input` | 表单输入框 |
| `.form-textarea` | 表单文本框 |
| `.type-btn` | 类型选择按钮 |
| `.type-btn.active` | 选中类型 |
| `.btn` | 基础按钮 |
| `.btn-primary` | 主按钮 |
| `.btn-secondary` | 次要按钮 |
| `.btn-block` | 全宽按钮 |
| `.filter-bar` | 筛选栏容器 |
| `.filter-btn` | 筛选按钮 |
| `.filter-btn.active` | 选中筛选 |
| `.task-list` | 卡片列表容器 |
| `.task-card` | 任务卡片 |
| `.task-card__header` | 卡片头部 |
| `.task-card__body` | 卡片主体 |
| `.task-card__footer` | 卡片底部 |
| `.task-type-badge` | 类型标签 |
| `.task-type--errand` | 代跑类型 |
| `.task-type--class` | 代课类型 |
| `.task-status-badge` | 状态标签 |
| `.task-status--open` | 可接单状态 |
| `.task-status--taken` | 已被接状态 |
| `.task-publisher` | 发布者文字 |
| `.task-course` | 课程名称 |
| `.task-detail` | 详情容器 |
| `.task-detail__item` | 详情项 |
| `.task-note` | 备注文字 |
| `.btn-accept` | 接单按钮 |
| `.btn-accept--disabled` | 禁用接单按钮 |
| `.toast-container` | Toast 容器 |
| `.toast` | Toast 元素 |
| `.toast--success` | 成功 Toast |
| `.toast--error` | 错误 Toast |
| `.toast--info` | 信息 Toast |
| `.panel-title` | 面板标题 |

### 7.3 data 属性

| 属性 | 值 | 用途 |
|------|----|------|
| `data-tab` | `"publish"` / `"list"` / `"mine"` | Tab 按钮标识 |
| `data-panel` | `"publish"` / `"list"` / `"mine"` | 面板标识 |
| `data-type` | `"errand"` / `"class"` | 类型按钮标识 |
| `data-filter` | `"all"` / `"errand"` / `"class"` | 筛选按钮标识 |
| `data-task-id` | `"task_xxx"` | 任务卡片/接单按钮关联 ID |

---

## 八、开发约束

| 类别 | 约束 |
|------|------|
| 纯前端 | 无后端、无 npm、无 webpack、无任何构建工具 |
| 兼容性 | 现代浏览器（Chrome/Firefox/Safari/Edge 近 2 个版本） |
| 编码 | UTF-8，中文界面，所有 UI 文字为简体中文 |
| 存储 | 全部使用 `localStorage`，键名以 `campus_` 为前缀 |
| 隐私 | **不得在代码中硬编码任何真实姓名**，所有用户昵称来自用户输入 |
| 安全 | XSS 防御：所有用户输入通过 `textContent` 或 `innerText` 插入，不使用 `innerHTML` 插入用户可控内容 |
| 模块化 | 全局函数 + 函数注释，不分模块文件，单文件 `app.js` |
| 代码风格 | 使用 `'use strict'`，`const`/`let` 而非 `var`，分号结尾 |
| 无依赖 | 不引入任何第三方库（无 jQuery、无 Vue/React 等） |
