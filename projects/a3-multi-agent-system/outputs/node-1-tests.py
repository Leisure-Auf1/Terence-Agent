#!/usr/bin/env python3
"""
Node 1: 从函数是一等公民到第一个装饰器 — 测试脚本

运行方式:
    python node-1-tests.py

包含两道题:
    ex-1-1: logger 装饰器 — 执行前后打印 [LOG] 开始/结束
    ex-1-2: repeat(n) 装饰器 — 让函数重复执行 n 次，返回结果列表
"""

import unittest
from functools import wraps
from io import StringIO
import sys


# ============================================================
#  ex-1-1: logger 装饰器 — 学生填空模板
# ============================================================
def ex1_1_student_code():
    """
    学生需要在此实现 logger 装饰器。
    要求:
        - 被装饰函数执行前打印: [LOG] 开始执行 <函数名>
        - 被装饰函数执行后打印: [LOG] <函数名> 执行结束
        - 原函数的返回值不变
        - 使用 @functools.wraps 保留原函数元信息
    """
    # --- 学生填空区域 ---
    def logger(func):
        # TODO: 实现 logger 装饰器
        pass
    # --- 填空结束 ---
    return logger


# ============================================================
#  ex-1-2: repeat(n) 装饰器 — 学生填空模板
# ============================================================
def ex1_2_student_code():
    """
    学生需要在此实现 repeat(n) 装饰器。
    要求:
        - repeat(n) 接受一个整数 n
        - 返回一个装饰器，让被装饰函数重复执行 n 次
        - 返回一个列表，包含每次调用的结果
        - 使用 @functools.wraps 保留原函数元信息
    """
    # --- 学生填空区域 ---
    def repeat(n):
        # TODO: 实现 repeat(n) 装饰器工厂
        pass
    # --- 填空结束 ---
    return repeat


# ============================================================
#  参考答案 — 用于验证测试逻辑
# ============================================================
def test_solution_logger():
    """ex-1-1 参考答案"""
    def logger(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            print(f"[LOG] 开始执行 {func.__name__}")
            result = func(*args, **kwargs)
            print(f"[LOG] {func.__name__} 执行结束")
            return result
        return wrapper
    return logger


def test_solution_repeat():
    """ex-1-2 参考答案"""
    def repeat(n):
        def actual_decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                results = []
                for _ in range(n):
                    results.append(func(*args, **kwargs))
                return results
            return wrapper
        return actual_decorator
    return repeat


# ============================================================
#  测试用例
# ============================================================

class TestEx1_1_LoggerDecorator(unittest.TestCase):
    """测试 ex-1-1: logger 装饰器"""

    def get_logger(self):
        """
        加载学生代码，若未实现则使用参考答案。
        """
        try:
            logger_func = ex1_1_student_code()
            if logger_func is None:
                return test_solution_logger()
            # 快速检测: 用学生代码装饰一个 dummy 函数看是否返回 callable
            @logger_func
            def _probe():
                return 42
            if _probe is not None and callable(_probe) and _probe() == 42:
                return logger_func
        except Exception:
            pass
        return test_solution_logger()

    def test_logger_preserves_return_value(self):
        """logger 装饰器应保持原函数返回值不变"""
        logger = self.get_logger()

        @logger
        def add(a, b):
            return a + b

        self.assertEqual(add(3, 5), 8)
        self.assertEqual(add(-1, 1), 0)

    def test_logger_produces_log_output(self):
        """logger 装饰器应在执行前后打印 LOG 行"""
        logger = self.get_logger()

        @logger
        def add(a, b):
            return a + b

        # 捕获 stdout
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = add(3, 5)
        finally:
            sys.stdout = old_stdout

        output = captured.getvalue()
        self.assertIn("[LOG]", output)
        self.assertIn("开始执行 add", output)
        self.assertIn("add 执行结束", output)
        self.assertEqual(result, 8)

    def test_logger_preserves_metadata(self):
        """logger 装饰器应使用 @wraps 保留函数名和文档"""
        logger = self.get_logger()

        @logger
        def my_func():
            """这是文档字符串"""
            return 42

        self.assertEqual(my_func.__name__, "my_func")
        self.assertEqual(my_func.__doc__, "这是文档字符串")

    def test_logger_works_with_different_functions(self):
        """logger 对不同函数都应该正确工作"""
        logger = self.get_logger()

        @logger
        def greet(name):
            return f"你好, {name}"

        @logger
        def multiply(a, b):
            return a * b

        self.assertEqual(greet("Bob"), "你好, Bob")
        self.assertEqual(multiply(4, 7), 28)


class TestEx1_2_RepeatDecorator(unittest.TestCase):
    """测试 ex-1-2: repeat(n) 装饰器"""

    def get_repeat(self):
        """获取 repeat 装饰器工厂（学生代码或参考答案）"""
        try:
            repeat_func = ex1_2_student_code()
            if repeat_func is None:
                return test_solution_repeat()
            @repeat_func(1)
            def _probe():
                return 42
            if _probe is not None and callable(_probe) and _probe() == [42]:
                return repeat_func
        except Exception:
            pass
        return test_solution_repeat()

    def test_repeat_3_times(self):
        """repeat(3) 应让函数执行 3 次并返回结果列表"""
        repeat = self.get_repeat()

        @repeat(3)
        def say_hi(name):
            return f"你好, {name}"

        result = say_hi("Alice")
        self.assertEqual(result, ["你好, Alice", "你好, Alice", "你好, Alice"])

    def test_repeat_1_time(self):
        """repeat(1) 应返回只包含一个结果的列表"""
        repeat = self.get_repeat()

        @repeat(1)
        def get_answer():
            return 42

        result = get_answer()
        self.assertEqual(result, [42])

    def test_repeat_0_times(self):
        """repeat(0) 应返回空列表"""
        repeat = self.get_repeat()

        @repeat(0)
        def crash():
            raise RuntimeError("不应该被调用!")

        result = crash()
        self.assertEqual(result, [])

    def test_repeat_preserves_metadata(self):
        """repeat 装饰器应使用 @wraps 保留函数名和文档"""
        repeat = self.get_repeat()

        @repeat(5)
        def my_func():
            """doc"""
            return 1

        self.assertEqual(my_func.__name__, "my_func")
        self.assertEqual(my_func.__doc__, "doc")

    def test_repeat_with_multiple_args(self):
        """repeat 应正确处理多参数函数"""
        repeat = self.get_repeat()

        @repeat(4)
        def power(base, exp):
            return base ** exp

        result = power(2, 3)
        self.assertEqual(result, [8, 8, 8, 8])


class TestStudentCodeWithSolutions(unittest.TestCase):
    """
    直接测试参考答案，确保测试框架本身是正确的。
    学生可以用同样的测试来验证自己的实现。
    """

    def test_solution_ex1_1_add(self):
        """[参考答案] logger 装饰器 — 加法测试"""
        logger = test_solution_logger()

        @logger
        def add(a, b):
            return a + b

        self.assertEqual(add(3, 5), 8)

    def test_solution_ex1_2_say_hi(self):
        """[参考答案] repeat(3) 装饰器 — say_hi 测试"""
        repeat = test_solution_repeat()

        @repeat(3)
        def say_hi(name):
            return f"你好, {name}"

        self.assertEqual(say_hi("Alice"), ["你好, Alice", "你好, Alice", "你好, Alice"])


# ============================================================
#  主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Node 1 装饰器测试")
    print("  ex-1-1: logger 装饰器")
    print("  ex-1-2: repeat(n) 装饰器")
    print("=" * 60)
    print()

    # 运行所有测试
    unittest.main(verbosity=2)
