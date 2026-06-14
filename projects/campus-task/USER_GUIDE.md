# CampusTask 用户手册

## 安装

```bash
git clone <仓库地址>
cd campus-task
```

无需额外安装依赖，Python >= 3.10 即可运行。

## 基本命令

### 添加任务

```bash
python -m campus_task add "任务标题"
python -m campus_task add "有截止日期的任务" --deadline 2026-06-20
```

### 查看任务列表

```bash
# 所有任务
python -m campus_task list

# 仅待处理
python -m campus_task list --filter pending

# 仅已完成
python -m campus_task list --filter done

# 按截止日期排序
python -m campus_task list --sort deadline
```

### 完成任务

```bash
python -m campus_task done <编号>
```

### 导出 CSV

```bash
python -m campus_task export tasks.csv
```

CSV 文件使用 UTF-8 编码（带 BOM），可用 Excel/WPS 直接打开。

## 参数

| 参数 | 说明 |
|------|------|
| `--version` | 显示版本号 |
| `--help` | 显示帮助信息 |

## 日志

程序运行日志写入 `campus_task.log`，包含：
- 操作记录（添加/完成任务、导出等）
- 错误和警告（如空文件、文件损坏等）

## 数据结构

任务数据保存在 `tasks.json`（当前目录）：

```json
{
  "id": 1,
  "title": "完成软件工程实验",
  "deadline": "2026-06-20",
  "status": "pending",
  "created_at": "2026-06-14 09:30:47"
}
```

## 故障排除

| 问题 | 原因 | 解决方法 |
|------|------|---------|
| `tasks.json` 是空文件 | 文件被意外清空 | 已自动修复，返回空列表 |
| `tasks.json` 损坏 | 手动编辑导致格式错误 | 删除或修复 JSON 文件 |
| 日志文件过大 | 长期使用积累 | 删除 `campus_task.log` 即可 |
