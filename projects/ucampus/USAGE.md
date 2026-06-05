# 📖 U校园 通用驱动引擎 · 使用手册

> 本文档教你如何使用 `ucampus-driver.js` 自动完成 U校园 AI 版课程。
> 
> **适用人群**：任何需要完成U校园AI版课程的学生
> **适用课程**：任何U校园AI版课程（只需替换 courseUrl）
> **无需修改脚本代码** —— 全部参数通过命令行传入

---

## 📋 目录

1. [前置准备](#1-前置准备)
2. [启动 Chrome](#2-启动-chrome)
3. [登录 U校园](#3-登录-u校园)
4. [模式 A — 查看课程状态](#4-模式-a--查看课程状态)
5. [模式 B — 查看学习记录](#5-模式-b--查看学习记录)
6. [模式 C — 提取题目数据](#6-模式-c--提取题目数据)
7. [模式 D — 执行答案并提交](#7-模式-d--执行答案并提交)
8. [模式 E — 完整两阶段流程](#8-模式-e--完整两阶段流程)
9. [常见问题](#9-常见问题)
10. [参数速查](#10-参数速查)

---

## 1. 前置准备

### 1.1 安装 Node.js 和 npm

**Arch Linux**:
```bash
sudo pacman -S nodejs npm
```

**Ubuntu/Debian**:
```bash
sudo apt install nodejs npm
```

验证安装:
```bash
node --version   # 需要 ≥ 18
npm --version
```

### 1.2 安装 Puppeteer

```bash
cd /tmp && npm install puppeteer
```

验证安装:
```bash
ls /tmp/node_modules/puppeteer
```

> 如果安装失败（网络问题），换国内镜像:
> ```
> npm install puppeteer --registry=https://registry.npmmirror.com
> ```

---

## 2. 启动 Chrome

### 2.1 基本启动命令

```bash
google-chrome-stable --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp \
  --no-first-run --no-default-browser-check \
  --no-sandbox --disable-gpu --no-proxy-server &
```

### 2.2 如果 Chrome 打不开

检查是否已安装:
```bash
which google-chrome-stable
```

如果没装，安装 Chromium:
```bash
sudo pacman -S chromium              # Arch
sudo apt install chromium-browser     # Ubuntu
```

然后用:
```bash
chromium --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-cdp --no-proxy-server &
```

### 2.3 验证 Chrome 已启动

```bash
curl -s http://127.0.0.1:9222/json/version | head -3
```

应该返回类似:
```json
{"Browser": "Chrome/148.0.7778.215", ...}
```

### ⚠️ 常见启动问题

**问题：ERR_CONNECTION_CLOSED**
- 原因：系统有代理设置（Clash/SSR 等）污染了 Chrome
- 解决：启动命令中必须有 `--no-proxy-server`

**问题：首次导航到 U校园不成功**
- 原因：Chrome 网络栈初始化问题（Wayland + 无代理）
- 解决：先在浏览器手动打开 `https://www.baidu.com`，再跳转到课程页

---

## 3. 登录 U校园

> ⚠️ 脚本**不会**帮你输入账号密码。必须手动登录一次，cookie 会保存在 `--user-data-dir` 指定的目录中。

### 登录步骤

1. 在启动的 Chrome 中，打开 `https://uai.unipus.cn`
2. 输入账号密码登录
3. 登录后，导航到你的课程详情页
4. 复制课程详情页的 URL

### 课程 URL 长什么样？

```
https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215
```

每个课程的 `20000975215` 这一串数字不一样。把它记下来，后面每次运行脚本都要用到。

### 如果登录后弹出"温馨提示"

点击"知道了"关闭即可。

### 如果登录时遇到 SSO 信息更新

SSO 页面的输入框使用 `id` 属性（不是 `name`）：
- 用户名: `input#username`
- 密码: `input#password`
- 协议复选框: `input#agreement`

勾选协议后如果弹出"服务协议与隐私政策"模态框，点"同 意"按钮关闭。

---

## 4. 模式 A — 查看课程状态

不答题，只看当前进度。

```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js status \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

**输出示例**:
```json
{
  "phase": "status",
  "summary": {
    "total": 44,      // 总任务数
    "completed": 20,  // 已完成
    "pending": 3,     // 未开始
    "locked": 21      // 已锁定
  },
  "tasks": [
    { "name": "Quotation", "status": "已完成" },
    { "name": "Preview", "status": "已完成" },
    { "name": "Words in use", "status": "未开始" },
    ...
  ]
}
```

---

## 5. 模式 B — 查看学习记录

查看所有单元的完成状态、得分、学习时长。

```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js progress \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

输出包含完整的学习记录表格：每个 Unit 的得分、每个任务的完成状态。

---

## 6. 模式 C — 提取题目数据

脚本会自动找到第一个"未开始"的任务，进入并提取题目的完整内容。

```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js extract \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

### 提取到的数据

脚本会检测任务类型，并提取相应的结构化数据：

**选择题 (MCQ)**:
```json
{
  "taskType": "mcq",
  "mcqQuestions": [
    {
      "index": 0,
      "stem": "The word 'costume' most likely means:",
      "options": [
        { "idx": 0, "letter": "A", "text": "吃；喝" },
        { "idx": 1, "letter": "B", "text": "服装，装束" },
        { "idx": 2, "letter": "C", "text": "姿势，仪态" },
        { "idx": 3, "letter": "D", "text": "大衣，外套" }
      ]
    }
  ]
}
```

**填空 (Words in use / Banked cloze)**:
```json
{
  "taskType": "fill_blank_dnd",
  "wordBank": ["poised", "lavish", "instantaneous", "tangible", ...],
  "droppables": [
    { "id": 0, "context": "The city is ___ for a major transformation." },
    { "id": 1, "context": "The festival was a ___ display of cultural diversity." }
  ],
  "fullText": "(页面完整文本，含每个句子的上下文)"
}
```

**后缀填空 (Collocation Practicing)**:
```json
{
  "taskType": "collocation_scoop",
  "scoops": [
    { "index": 0, "prefix": "ma", "after": " impact" },
    { "index": 1, "prefix": "mi", "after": "izing" }
  ]
}
```

---

## 7. 模式 D — 执行答案并提交

### 7.1 执行前准备

需要准备两个数据（来自模型分析结果）：
1. **`taskName`**: 任务名称（与课程树中显示的一致）
2. **`answers`**: 答案数组，格式取决于任务类型

### 7.2 不同类型的答案格式

| 任务类型 | 答案格式 | 示例 |
|:---------|:---------|:-----|
| MCQ 选择题 | 选项索引 `[0,1,2,3]` (0=A, 1=B, 2=C, 3=D) | `[2,0,0,1,3]` |
| 填空 (Words in use) | 单词字符串数组 | `["poised","lavish","instantaneous"]` |
| 拖拽填空 (Banked cloze) | 单词字符串数组 | `["capability","embedded","sustainability"]` |
| 后缀填空 (Collocation) | 后缀字符串数组 | `["ssive","nimizing","stantial"]` |
| 主观题 (textarea) | 文本字符串数组 | `["This is my answer...","Second answer..."]` |
| 讨论区 | 单个评论文本 | `["I think this is an interesting topic..."]` |
| 视频+MCQ | 选项索引数组 | `[0,1,2,3]` |

### 7.3 执行命令

**填空题示例**:
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js execute \
  '{"answers":["poised","lavish","instantaneous","tangible","hurdles","streamline","detrimental","evoke","hypothesis","escalating"],"taskName":"Words in use"}' \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

**MCQ 选择题示例**:
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js execute \
  '{"answers":[2,0,0,1,3],"taskName":"Quiz"}' \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

**视频+MCQ 示例**:
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js execute \
  '{"answers":[0,1,2,3],"taskName":"Critical thinking skill","taskType":"video_mcq"}' \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

### 7.4 执行输出

```json
{
  "phase": "result",
  "task": "Words in use",
  "type": "fill_blank_dnd",
  "passed": true,
  "score": "100",
  "hasContinue": true,
  "hasRetry": false,
  "resultSummary": true,
  "pageText": "答题小结 ..."
}
```

字段说明:
- `passed`: 是否通过（`true` 或 `false`）
- `score`: 得分（如 `"100"`、`"66.7"`、`"?"`）
- `hasContinue`: 是否有"继续学习"按钮（可进入下一任务）
- `hasRetry`: 是否需要"返回修改"（分数不够）
- `resultSummary`: 是否显示"答题小结"

---

## 8. 模式 E — 完整两阶段流程

这是最常用的模式——**先提取题目，让 AI 分析，再执行提交**。

### 完整示例：完成"Words in use"任务

**第1步 — 提取题目**:
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js extract \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215
```

**第2步 — 让 AI（或你自己）分析答案**:

从输出中看 `wordBank`（词库）和 `droppables`（每个空的上下文）。
逐题分析：

```
空1: "The city is ___ for a major transformation."
    词库匹配: "poised" (be poised for = 准备好)
空2: "The festival was a ___ display of cultural diversity."
    词库匹配: "lavish" (lavish scale/display = 大规模的)
...以此类推...
```

得出答案数组: `["poised","lavish","instantaneous","tangible","hurdles","streamline","detrimental","evoke","hypothesis","escalating"]`

**第3步 — 执行答案**:
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js execute \
  '{"answers":["poised","lavish","instantaneous","tangible","hurdles","streamline","detrimental","evoke","hypothesis","escalating"],"taskName":"Words in use"}' \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215
```

**第4步 — 检查结果**:
- 如果 `passed: true` → 通过 ✓
- 如果 `hasContinue: true` → 点"继续学习"进入下一任务
- 如果 `hasRetry: true` → 分数不够，脚本会自动重试（换一组答案）

---

## 9. 常见问题

### 9.1 Chrome 连接失败
```
Cannot connect to Chrome CDP at http://127.0.0.1:9222
```
**原因**: Chrome 没启动或 remote-debugging-port 未设置
**修复**: 
```bash
# 启动 Chrome
google-chrome-stable --remote-debugging-port=9222 --user-data-dir=/tmp/chrome-cdp --no-sandbox --no-proxy-server &
# 验证
curl -s http://127.0.0.1:9222/json/version
```

### 9.2 Puppeteer 找不到
```
Error: Cannot find module 'puppeteer'
```
**修复**:
```bash
cd /tmp && npm install puppeteer
```

### 9.3 页面白屏 / 只有 CSS
**原因**: U校园微前端加载慢
**处理**: 脚本会自动等待最多 20 秒。如果一直失败：
- 手动刷新浏览器页面
- 先导航到 `https://www.baidu.com` 再跳转到课程页

### 9.4 提交后显示"返回修改"
**原因**: 分数不够（<60%）
**处理**: 脚本会自动重试 4 次（MCQ 会换不同选项）。如果还是失败：
- 检查答案是否正确
- 手动查看题目，确认答案

### 9.5 提交后提示"还有N道题没做"
**原因**: React 的 state 没更新（脚本未正确触发 onChange）
**修复**: 联系开发者更新脚本中的 React onChange 逻辑

### 9.6 视频播放不了
**原因**: 浏览器 autoplay policy
**处理**: 脚本会自动 `video.muted = true` + `video.play()`

### 9.7 Chrome 导航时 ERR_CONNECTION_CLOSED
**原因**: 系统代理设置（Clash/SSR）污染
**修复**: 启动 Chrome 时加 `--no-proxy-server`

### 9.8 闪卡任务闪卡数量不对
**处理**: 脚本有 80 次循环上限（足够大多数任务）。如果不够，调整 `CONFIG.strategy.flashcardMax`。

### 9.9 不同课程能否使用？
**可以**。只需要更换 `--courseUrl` 参数。
但注意：如果其他课程的 DOM 结构和 class 名不同，可能需要微调选择器。

---

## 10. 参数速查

### 命令行参数

| 参数 | 说明 | 默认值 |
|:-----|:-----|:-------|
| `mode` | 运行模式: `extract`/`execute`/`status`/`progress` | `status` |
| `--courseUrl=<URL>` | 课程详情页 URL | 脚本内的 CONFIG |
| `--cdpUrl=<URL>` | Chrome CDP 地址 | `http://127.0.0.1:9222` |
| `--section=<A\|B\|C>` | 限定指定 Section | 所有 Section |
| `--verbose` | 打印调试信息 | 关闭 |
| `--dryRun` | 仅检测不执行 | 关闭 |

### 环境变量

| 变量 | 说明 | 优先级 |
|:-----|:-----|:-------|
| `U_COURSE_URL` | 课程详情页 URL | 高于 `--courseUrl` |
| `U_CDP_URL` | Chrome CDP 地址 | 高于 `--cdpUrl` |

设置后可以不用每次传入参数：
```bash
export U_COURSE_URL="https://ucloud.unipus.cn/app/cmgt/resource-detail/20000975215"
export U_CDP_URL="http://127.0.0.1:9222"
node projects/ucampus/scripts/ucampus-driver.js extract
```

### 可配置项（脚本内 CONFIG 对象）

| 配置项 | 默认值 | 说明 |
|:-------|:-------|:-----|
| `timeouts.microAppLoad` | 20000ms | 微前端加载等待 |
| `timeouts.taskNavigation` | 30000ms | 任务导航等待 |
| `timeouts.submitResult` | 10000ms | 提交后等待结果 |
| `timeouts.videoPoll` | 60000ms | 视频后 MCQ 轮询 |
| `timeouts.pageLoad` | 30000ms | 页面加载超时 |
| `strategy.maxRetries` | 4 | "返回修改"重试次数 |
| `strategy.flashcardMax` | 80 | 闪卡循环上限 |
| `strategy.pollInterval` | 500ms | 轮询间隔 |
| `viewport` | 1280x900 | 浏览器视口 |

---

## 📝 版本历史

| 版本 | 日期 | 说明 |
|:-----|:----|:-----|
| 1.0 | 2026-06-05 | 初版：通用化驱动引擎，零硬编码，5 种运行模式 |
