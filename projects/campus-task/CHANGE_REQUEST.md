# 实验 5 — 迭代开发与变更管理

## 用户反馈收集

### 用户 A（大三计算机系学生）

> **原话**："每次作业 deadline 都不一样，我想按截止时间排序，先做最急的。现在列表是按添加时间排的，没法一眼看出来哪个最急。"

| 项目 | 内容 |
|------|------|
| 问题描述 | 任务列表按创建时间排序，无法按截止日期优先级查看 |
| 建议功能 | 按 deadline 排序任务 |
| 优先级 | **高** — 核心功能缺失 |
| 验收标准 | `python main.py list --sort deadline` 按 deadline 升序排列，空 deadline 排最后 |
| 风险 | 低 |
| 预计工作量 | 1 小时 |

### 用户 B（大二软件工程学生）

> **原话**："我想把任务清单导出来发给小组同学看，但要一个一个复制粘贴好麻烦。能不能直接导出成 Excel 或者 CSV？"

| 项目 | 内容 |
|------|------|
| 问题描述 | 无法将任务数据导出为通用格式分享 |
| 建议功能 | 导出任务为 CSV 文件 |
| 优先级 | **中** — 提升协作效率 |
| 验收标准 | `python main.py export tasks.csv` 生成 CSV 文件，可用 Excel/WPS 打开 |
| 风险 | 低 |
| 预计工作量 | 1 小时 |

### 用户 C（大一新生）

> **原话**："有时候我记不清任务是'复习高数'还是'高数复习'，要是有个搜索功能就好了，输入关键字就能找到。"

| 项目 | 内容 |
|------|------|
| 问题描述 | 任务较多时无法快速搜索特定任务 |
| 建议功能 | 按关键字搜索任务 |
| 优先级 | **中** — 提升使用体验 |
| 验收标准 | `python main.py search "高数"` 返回标题包含"高数"的所有任务 |
| 风险 | 低 |
| 预计工作量 | 0.5 小时 |

---

## 变更选择理由

**选中实现的两个功能：**

| 序号 | 功能 | 理由 |
|:----:|------|------|
| 1 | **按 deadline 排序** | 用户 A 反馈优先级"高"——deadline 是用户最紧迫的需求；已有 deadline 字段，实现成本低 |
| 2 | **导出任务为 CSV** | 用户 B 反馈的协作场景涉及多人，且导出功能在实验 7 中也会用到，提前实现便于后续迭代 |

**未选中的功能及理由：**
- 搜索关键字 — 有价值但优先级中等，实验资源有限

## 实现记录

### 功能 1：按 deadline 排序

**修改文件：** `task_service.py` — 新增 `list_sorted_by_deadline()` 函数

```python
def list_sorted_by_deadline():
    """按 deadline 升序返回任务列表，无 deadline 排最后"""
    tasks = [Task.from_dict(d) for d in load_all()]
    return sorted(tasks, key=lambda t: t.deadline if t.deadline else "9999-99-99")
```

**新增测试：** `test_sort_deadline` — 验证 deadline 排序正确性

### 功能 2：导出任务为 CSV

**新增文件：** 无，在 `task_service.py` 新增 `export_csv()` 函数

```python
def export_csv(filepath):
    """将所有任务导出为 CSV 文件"""
    tasks = list_all()
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["编号", "标题", "deadline", "状态", "创建时间"])
        for t in tasks:
            writer.writerow([t.id, t.title, t.deadline, t.status, t.created_at])
```

**新增测试：** `test_export_csv` — 验证 CSV 文件格式和内容正确
