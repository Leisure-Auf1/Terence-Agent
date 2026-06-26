# 💻 电脑维护 — Computer Setup

> **用途**: 记录系统配置、硬件/驱动调优、桌面环境维护、软件安装等电脑操作事项。
>
> **原则**: 每次操作先加载 `harness-preflight` → 在 `projects/computer-setup/` 下按日期创建子目录 → 记录到 `event-report/`

## 目录结构

```
projects/computer-setup/
├── README.md              ← 本说明
├── 2026-06-26/
│   ├── DESIGN.md          ← 设计方案
│   ├── SPEC.md            ← 需求规格
│   ├── monitor-hotplug.sh     ← 显示器热插拔切换脚本
│   └── 99-monitor-hotplug.rules  ← udev 规则
└── ...
```

## 已有操作

| 日期 | 操作 | 状态 |
|:-----|:-----|:----:|
| 2026-06-26 | 显示器热插拔自动切换 | ✅ |
| 2026-06-26 | Arch 滚动更新（260 包） | ✅ |

## 关联

- `event-report/YYYY-MM-DD.md` — 操作日志
- `error-registry/` — 错误记录（如有）
- `scripts/` — 通用工具脚本
