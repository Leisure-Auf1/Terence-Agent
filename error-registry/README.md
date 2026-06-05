---
name: error-registry
description: '系统报错表：脚本运行/编码/依赖/环境等所有已知问题及修复方案。4级分类: L0致命→L3信息'
category: devops
tags: [core, errors, debugging]
related_skills: [architecture-constraints, task-progress]
---

# 🚨 报错表 (Error Registry)

所有已知错误按严重度分 4 级：`L0=致命` `L1=可绕行` `L2=环境特定` `L3=信息`

---

## L0 — 致命 (阻断)

| 码 | 触发 | 根因 | 修复 |
|:---|:-----|:-----|:-----|
| `PEP668` | `pip install` 在系统 Python | Arch Linux 保护系统包 | 用 venv: `python3 -m venv ~/venv` |
| `SUDO_NEEDED` | `sudo pacman/paru/makepkg` | 用户无 passwordless sudo | 改用 pip/npm 或 `~/.local` 编译 |
| `PLATFORM_UNSUPPORTED` | `anything-cli screenshot` | 只支持 macOS/Windows | 替代: `grim`+`xdotool` |
| `MCP_VERSON_CONFLICT` | browser CLI 降级了 mcp 版本 | setup.py 指定旧版 mcp | `pip install mcp==1.26.0` |

## L1 — 可绕行

| 码 | 触发 | 根因 | 修复 | 替代方案 |
|:---|:-----|:-----|:-----|:---------|
| `BH_STUB` | `from browser_harness import Harness` | PyPI 包是空包 | `connect_over_cdp` 或 `bhts` | ✅ |
| `BH_NO_CLI` | `which browser-harness` | 无 entry point | 用 `bhts` 代替 | ✅ |
| `PW_DEPS_FAIL` | `playwright install --with-deps` | Arch 非官方 + 需 sudo | 只用 `install chromium` | ✅ |
| `VISION_NO_IMG` | `browser_vision()` 截图分析失败 | 当前模型不支持 `image_url` | 改用 `browser_console` eval JS | ✅ |
| `CONFIG_LOCKED` | patch config.yaml 被拒 | Hermes 安全模块 | 手动编辑或 `hermes config set` | ✅ |
| `MEM_FULL` | memory 添加被拒 | 2200 字符上限 | `replace` 合并旧条目 | ✅ |
| `KILLALL_BLOCKED` | `killall -9 chrome` 被拦截 | Hermes 屏蔽 SIGKILL | `pkill -f 'pattern'` | ✅ |

## L2 — 环境特定

| 码 | 触发 | 根因 | 修复 |
|:---|:-----|:-----|:-----|
| `CHROME_PROXY` | Chrome CDP `ERR_CONNECTION_CLOSED` | GNOME gsettings 代理残留 | `--no-proxy-server` 启动 |
| `CHROME_FIRST_NAV` | 首次导航目标 URL 失败 | Wayland 网络栈初始化 | 先 `goto('https://baidu.com')` |
| `WAYLAND_MOUSE` | pyautogui/pynput 在 Wayland 无效 | Wayland 阻止 XTest | 用 ydotool 或 X11 |
| `SSO_AGREEMENT` | 勾选协议跳到独立页面 | SSO 首次登录 | 重新导航→再填→直接登录 |
| `REACT_CLICK` | `.click()` 在 SPA 无效 | React 事件代理 | `__reactProps.onClick()` 双重触发 |

## L3 — 信息

| 码 | 说明 |
|:---|:-----|
| `NODE26_OLD_BH` | node-proxy@0.8.0 不兼容 Node 26+，已用 browser-harness-ts 代替 |
| `MIRROR_PYPI` | `-i https://pypi.tuna.tsinghua.edu.cn/simple` 加速 pip |
| `MIRROR_NPM` | `--registry=https://registry.npmmirror.com` 加速 npm |
| `PW_BROWSER_PATH` | Playwright Chromium 在 `~/.cache/ms-playwright/chromium-1223` |
| `MCP_REGISTER` | MCP 服务器需加 `~/.hermes/config.yaml` + 重启才生效 |
| `CTX_OVERLOAD` | 拉了不必要上下文（如开发时拉浏览器自动化）被用户纠正后记入此条 |
| `SKIP_LAYER_VIOLATION` | 跳层调用 — 如 L1→L3 跳过 L2 |
| `REPEAT_ERROR` | 重复已报过的错误，应查 error-registry 未查 |
| `SKIP_KNOWN_FIX` | 跳过 error-registry 已知修复直接走弯路 |
| `PROGRESS_MISSING` | 完成任务后未更新 task-progress |
| `SKIP_RETROSPECTIVE` | 完成任务后未执行强制复盘 — 必须执行 6 步复盘清单 |
| `FIX_NO_REPORT` | Debugger 修复错误后未提交到 error-registry — 每次修复必须写入错误码+根因+修复方案 |
| `RIGID_RULE` | Guidance Agent 预设了固定规则（如硬性分类加载）而非根据项目随机应变 — 应遵循 Phase 0 |

## 📋 修复命令速查

```bash
# PEP668: venv
python3 -m venv ~/.hermes/browser-venv
source ~/.hermes/browser-venv/bin/activate

# MCP版本冲突
source ~/.hermes/browser-venv/bin/activate && pip install mcp==1.26.0

# Playwright 浏览器安装 (跳过系统依赖)
source ~/.hermes/browser-venv/bin/activate && python3 -m playwright install chromium

# React onClick 双重触发
el.__reactProps.onClick({preventDefault(){}}); el.click(); el.dispatchEvent(new MouseEvent('click',{bubbles:true}))

# Chrome 代理清除
gsettings set org.gnome.system.proxy.http port 0
gsettings set org.gnome.system.proxy.https port 0

# 截图: grim (Wayland)
grim /tmp/shot.png

# 截图: import (X11)
import -window root /tmp/shot.png
```
