"""
CampusTask 测试 — 覆盖实验 3 要求的 10+ 个测试用例

运行方式：
    pytest tests/ -v
"""

import json
import os
import sys

import pytest

# 将项目目录加入 sys.path，确保可以导入 campus_task 模块
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_DIR)

import task_service
import task_storage


# ── 夹具 ──────────────────────────────────────────────────────

@pytest.fixture(autouse=True)
def _chdir_tmp(tmp_path):
    """每个测试都在独立临时目录中运行，避免污染真实 tasks.json"""
    orig = os.getcwd()
    os.chdir(tmp_path)
    yield
    os.chdir(orig)


# ── 测试用例 ────────────────────────────────────────────────────

class TestAdd:
    """添加任务"""

    def test_add_success(self):
        """添加任务成功"""
        task = task_service.add("完成软件工程实验1")
        assert task.title == "完成软件工程实验1"
        assert task.status == "pending"
        assert task.id == 1
        # 验证已保存到文件
        tasks = task_service.list_all()
        assert len(tasks) == 1
        assert tasks[0].title == "完成软件工程实验1"

    def test_add_empty_title(self):
        """添加空标题失败（验证拒绝空标题）"""
        import pytest
        with pytest.raises(ValueError, match="不能为空"):
            task_service.add("")


class TestList:
    """查看任务列表"""

    def test_list_empty(self):
        """查看空任务列表"""
        tasks = task_service.list_all()
        assert len(tasks) == 0

    def test_list_multiple(self):
        """添加多个任务后列表正确"""
        task_service.add("任务A")
        task_service.add("任务B")
        task_service.add("任务C")
        tasks = task_service.list_all()
        assert len(tasks) == 3
        titles = [t.title for t in tasks]
        assert titles == ["任务A", "任务B", "任务C"]


class TestDone:
    """完成任务"""

    def test_done_existing(self):
        """完成存在的任务"""
        task_service.add("可完成的任务")
        result = task_service.done(1)
        assert "已完成" in result
        tasks = task_service.list_all()
        assert tasks[0].is_done()

    def test_done_nonexistent(self):
        """完成不存在的任务"""
        result = task_service.done(999)
        assert "未找到" in result

    def test_done_already_done(self):
        """已完成任务不重复完成"""
        task_service.add("已完成的任务")
        task_service.done(1)
        result = task_service.done(1)
        assert "已经是完成状态" in result


class TestIdIncrement:
    """任务编号递增"""

    def test_ids_auto_increment(self):
        """连续添加任务，编号依次递增"""
        t1 = task_service.add("第一个")
        t2 = task_service.add("第二个")
        t3 = task_service.add("第三个")
        assert t1.id == 1
        assert t2.id == 2
        assert t3.id == 3


class TestPersistence:
    """数据持久化"""

    def test_file_created_after_add(self):
        """添加任务后自动创建 tasks.json"""
        assert not os.path.exists(task_storage._get_path())
        task_service.add("新任务")
        assert os.path.exists(task_storage._get_path())

    def test_file_auto_create_empty(self):
        """JSON 文件不存在时自动创建空列表"""
        tasks = task_service.list_all()
        assert tasks == []
        # 文件仍不存在（惰性创建）
        assert not os.path.exists(task_storage._get_path())

    def test_save_and_reload(self):
        """任务保存后重新读取仍然存在"""
        task_service.add("持久化任务")
        task_service.add("另一个任务")

        # 模拟程序重启：重新从文件加载
        loaded = task_service.list_all()
        assert len(loaded) == 2
        assert loaded[0].title == "持久化任务"
        assert loaded[1].title == "另一个任务"

    def test_corrupted_file(self):
        """JSON 文件损坏时给出友好错误"""
        path = task_storage._get_path()
        with open(path, "w") as f:
            f.write("这不是合法的 JSON 内容{[[")
        with pytest.raises(json.JSONDecodeError):
            task_storage.load_all()


class TestModel:
    """数据模型测试"""

    def test_task_default_status(self):
        """新建任务默认状态为 pending"""
        from task_model import Task
        t = Task(title="默认状态测试")
        assert t.status == "pending"
        assert not t.is_done()

    def test_task_mark_done(self):
        """调用 mark_done 后状态变为 done"""
        from task_model import Task
        t = Task(title="标记完成")
        t.mark_done()
        assert t.is_done()


class TestFilter:
    """按状态过滤"""

    def test_filter_pending(self):
        """过滤出待处理任务"""
        task_service.add("已完成任务")
        task_service.done(1)
        task_service.add("待处理任务")
        pending = task_service.list_all(status="pending")
        assert len(pending) == 1
        assert pending[0].title == "待处理任务"

    def test_filter_done(self):
        """过滤出已完成任务"""
        task_service.add("任务A")
        task_service.done(1)
        task_service.add("任务B")
        done_tasks = task_service.list_all(status="done")
        assert len(done_tasks) == 1
        assert done_tasks[0].title == "任务A"

    def test_filter_no_match(self):
        """过滤条件无匹配时返回空列表"""
        tasks = task_service.list_all(status="done")
        assert tasks == []


class TestIteration:
    """实验 5：迭代功能"""

    def test_sort_by_deadline(self):
        """按 deadline 排序，空 deadline 排最后"""
        task_service.add("无截止日期")
        task_service.add("急任务", deadline="2026-06-15")
        task_service.add("普通任务", deadline="2026-06-30")
        sorted_tasks = task_service.list_sorted_by_deadline()
        assert sorted_tasks[0].title == "急任务"
        assert sorted_tasks[1].title == "普通任务"
        assert sorted_tasks[2].title == "无截止日期"

    def test_export_csv(self):
        """导出 CSV 文件格式正确"""
        import csv, os
        task_service.add("测试导出", deadline="2026-06-20")
        csv_path = "test_export.csv"
        task_service.export_csv(csv_path)
        assert os.path.exists(csv_path)
        with open(csv_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["编号", "标题", "deadline", "状态", "创建时间"]
        assert rows[1][1] == "测试导出"
        os.remove(csv_path)

    def test_empty_file_does_not_crash(self):
        """空 tasks.json 不会崩溃（v0.2.1 bug 修复）"""
        import os
        # 创建一个空文件
        with open("tasks.json", "w") as f:
            pass
        tasks = task_service.list_all()
        assert tasks == []
        os.remove("tasks.json")
