# 🏫 U校园 AI 版自动化项目

> 自动完成U校园AI版课程的通用脚本工具集
> 仓库位置: `Terence-Agent/projects/ucampus/`

---

## 📁 项目结构

```
projects/ucampus/
├── README.md                          ← 本文件：项目总览
├── USAGE.md                           ← 使用手册（给用户的完整操作指南）
├── task-progress/
│   ├── 2026-06-05-session-log.md      ← 会话日志（课程进度）
│   └── 2026-06-05-runtime-logs.md     ← 运行日志（报错+脚本开发记录）
└── scripts/
    ├── ucampus-driver.js              ← ⭐ 通用驱动引擎（推荐使用）
    ├── ucampus-auto-runner.js          ← 旧版两阶段脚本
    ├── uc-show-status.js               ← 查看课程状态
    ├── uc-check-page.js                ← 页面检测
    ├── uc-info.js                      ← 页面信息提取
    ├── uc-catalog.js                   ← 课程目录提取
    ├── uc-record.js                    ← 学习记录提取
    ├── uc-u3-task12.js                 ← Unit 3 Task 1+2
    ├── uc-u3-task2d.js                 ← Unit 3 Task 2调试
    ├── uc-u3-expr-retry.js             ← Expressions in use重试
    └── uc-u3-reading-exec.js           ← Reading Prac执行
```

## 🚀 快速开始

### 前置条件

| 条件 | 检查命令 |
|:-----|:---------|
| Node.js ≥ 18 | `node --version` |
| Puppeteer | `ls /tmp/node_modules/puppeteer` |
| Chrome/Chromium | `which google-chrome-stable` |

### 一键启动 Chrome

```bash
google-chrome-stable --remote-debugging-port=9222 \
  --user-data-dir=/tmp/chrome-cdp \
  --no-first-run --no-default-browser-check \
  --no-sandbox --disable-gpu --no-proxy-server &
```

> ⚠️ **Arch Linux + Wayland 用户注意**：
> - `--no-proxy-server` 是**必须的**，否则 GNOME gsettings 代理残留导致 `ERR_CONNECTION_CLOSED`
> - 如果首次导航目标 URL 失败，先手动访问 `https://www.baidu.com` 再跳转

### 查看课程状态

```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js status \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

### 完整两阶段工作流

**第1步 — 提取题目**：进入第一个未开始任务，读取全部题目数据
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js extract \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

**第2步 — 模型分析**：将提取出的 JSON 题目数据交给 AI 模型分析，得出答案数组

**第3步 — 执行提交**：填入分析好的答案并提交
```bash
NODE_PATH=/tmp/node_modules node projects/ucampus/scripts/ucampus-driver.js execute \
  '{"answers":["word1","word2",...],"taskName":"任务名称"}' \
  --courseUrl=https://ucloud.unipus.cn/app/cmgt/resource-detail/你的课程ID
```

---

## 📊 已完成进度

| Unit | 名称 | 状态 | 得分 |
|:----:|:----|:----:|:----:|
| 1 | Urban development | ✅ 已完成 | 85.6 |
| 2 | Secrets to beauty | ✅ 已完成 | 96.1 |
| 3 | Business success in the new age | ✅ 已完成 | 93.9 |
| 4 | Man and nature | ⬜ 未开始 | — |
| 5 | Passion guides life choices | ⬜ 未开始 | — |
| 6 | Energy and food crises | ⬜ 未开始 | — |

---

## 📚 更多文档

- [使用手册 USAGE.md](./USAGE.md) — 面向用户的完整操作指南
- `task-progress/2026-06-05-runtime-logs.md` — 开发过程中的报错和修复记录
- `.hermes/skills/u-campus-course-automation/` — U校园自动化技能（含参考答案库）
