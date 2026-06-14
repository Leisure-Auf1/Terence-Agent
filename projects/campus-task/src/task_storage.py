"""task_storage — JSON 存储层，负责任务的持久化"""

import json
import os

TASKS_FILE = "tasks.json"


def _get_path():
    """获取 tasks.json 的路径（当前工作目录，便于测试隔离）"""
    return os.path.join(os.getcwd(), TASKS_FILE)


def load_all():
    """从文件加载所有任务字典列表。

    文件不存在时返回空列表。
    文件为空时返回空列表（已修复 bug）。
    文件损坏时抛出 JSONDecodeError。
    """
    path = _get_path()
    if not os.path.exists(path):
        return []

    # Bug 修复：空文件时返回空列表而不是崩溃
    if os.path.getsize(path) == 0:
        return []

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_all(tasks_dicts):
    """将任务字典列表写入文件"""
    path = _get_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(tasks_dicts, f, ensure_ascii=False, indent=2)
