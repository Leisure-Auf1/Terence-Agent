"""task_service — 业务逻辑层：添加、查询、完成任务"""

import csv

from .task_model import Task
from .task_storage import load_all, save_all


def _next_id(tasks_dicts):
    """计算下一个可用编号"""
    return max((t["id"] for t in tasks_dicts), default=0) + 1


def add(title, deadline=""):
    """添加新任务，返回添加后的 Task"""
    if not title or not title.strip():
        raise ValueError("任务标题不能为空")
    tasks = load_all()
    task = Task(title=title, deadline=deadline, id=_next_id(tasks))
    tasks.append(task.to_dict())
    save_all(tasks)
    return task


def list_all(status=None):
    """返回所有 Task 对象列表，可按状态过滤"""
    tasks = [Task.from_dict(d) for d in load_all()]
    if status:
        tasks = [t for t in tasks if t.status == status]
    return tasks


def done(task_id):
    """标记指定编号的任务为已完成，返回操作结果消息"""
    tasks = load_all()
    for t in tasks:
        if t["id"] == task_id:
            if t["status"] == "done":
                return f"[!] 任务 {task_id} 已经是完成状态"
            t["status"] = "done"
            save_all(tasks)
            return f"[✓] 任务已完成：{t['title']}"
    return f"[✗] 错误：未找到编号为 {task_id} 的任务"


def list_sorted_by_deadline():
    """按 deadline 升序返回任务列表，无 deadline 排最后"""
    tasks = [Task.from_dict(d) for d in load_all()]
    return sorted(tasks, key=lambda t: t.deadline if t.deadline else "9999-99-99")


def export_csv(filepath):
    """将所有任务导出为 CSV 文件"""
    tasks = list_all()
    with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["编号", "标题", "deadline", "状态", "创建时间"])
        for t in tasks:
            writer.writerow([t.id, t.title, t.deadline, t.status, t.created_at])
