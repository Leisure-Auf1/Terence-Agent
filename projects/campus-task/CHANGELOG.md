# Changelog

## v0.2.1 (2026-06-14) — 当前版本

### 🐛 Bug 修复

- **空 tasks.json 崩溃**：当 `tasks.json` 是空文件时，程序不再崩溃，改为返回空列表并记录警告日志

### 🚀 增强

- **包化改造**：支持 `python -m campus_task` 运行
- **argparse 命令行**：统一参数解析，支持 `--version`、`--help`
- **日志系统**：操作记录写入 `campus_task.log`
- **用户手册**：新增 `USER_GUIDE.md`
- **错误处理增强**：文件 I/O 操作增加健壮性

### 📁 文件变更

| 文件 | 变更 |
|------|------|
| `campus_task/__main__.py` | **新增** — 包入口，argparse CLI |
| `campus_task/__init__.py` | **新增** — 包初始化 |
| `campus_task/__version__.py` | **新增** — 版本号 |
| `campus_task/task_storage.py` | **修复** — 空文件返回空列表 |
| `campus_task/task_service.py` | **改** — 相对导入 |
| `USER_GUIDE.md` | **新增** — 用户手册 |
| `pyproject.toml` | **更新** — 版本号至 0.2.1 |

---

## v0.2.0 (迭代一)

### 🚀 新增功能

- **按 deadline 排序**：`python main.py list --sort deadline`
- **导出 CSV**：`python main.py export <文件名.csv>`

### 🔧 改进

- 任务列表新增 `deadline` 列显示
- 测试覆盖增至 19 个用例
