"""task_model — 任务数据模型"""

from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class Task:
    """表示一个待办任务"""

    title: str
    deadline: str = ""
    id: int = 0
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def to_dict(self):
        """转换为字典（用于 JSON 序列化）"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data):
        """从字典创建 Task 实例"""
        return cls(
            id=data["id"],
            title=data["title"],
            deadline=data.get("deadline", ""),
            status=data.get("status", "pending"),
            created_at=data.get("created_at", ""),
        )

    def is_done(self):
        """判断任务是否已完成"""
        return self.status == "done"

    def mark_done(self):
        """标记为已完成"""
        self.status = "done"
