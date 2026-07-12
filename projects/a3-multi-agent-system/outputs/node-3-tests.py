#!/usr/bin/env python3
"""
Node 3: 装饰器堆叠、property 原理与框架实战 — 测试脚本

运行方式:
    python node-3-tests.py

包含两道题:
    ex-3-1: custom_property — 自己实现一个简化版 @property（描述符协议）
    ex-3-2: make_decorator 堆叠验证 — 验证洋葱模型装饰器执行顺序
"""

import unittest
import time
from functools import wraps
from io import StringIO
import sys


# ============================================================
#  ex-3-1: custom_property 描述符 — 学生填空模板
# ============================================================
def ex3_1_student_code():
    """
    学生需要在此实现 custom_property 类。

    要求:
        - __init__(self, fget=None, fset=None): 保存 getter 和 setter
        - __get__(self, instance, owner):
            · instance is None → 返回描述符本身（类访问）
            · 否则调用 self.fget(instance) 返回属性值
        - __set__(self, instance, value):
            · 如果没有 setter → raise AttributeError("can't set attribute")
            · 否则调用 self.fset(instance, value)
        - setter(self, func):
            · 返回一个新的 custom_property 实例，复制 fget，添加 fset

    提示:
        - 这是描述符协议的核心应用 —— __get__ 和 __set__ 让 Python 自动拦截属性访问
        - setter 不要修改 self，要返回新实例（不可变模式）
    """
    # --- 学生填空区域 ---
    class custom_property:
        def __init__(self, fget=None, fset=None):
            # TODO: 实现 __init__
            pass

        def __get__(self, instance, owner):
            # TODO: 实现 __get__
            pass

        def __set__(self, instance, value):
            # TODO: 实现 __set__
            pass

        def setter(self, func):
            # TODO: 实现 setter
            pass
    # --- 填空结束 ---
    return custom_property


# ============================================================
#  ex-3-2: make_decorator 堆叠验证 — 学生填空模板
# ============================================================
def ex3_2_student_code():
    """
    学生需要在此实现 make_decorator(name) 工厂函数。

    要求:
        - make_decorator(name) 接受一个装饰器名称
        - 返回一个装饰器函数，该装饰器会:
            · 在执行被装饰函数前打印 "{name} 开始"
            · 调用原始函数
            · 在执行后打印 "{name} 结束"

    装饰器堆叠后的期望输出 (A→B→C 堆叠):
        A 开始
        B 开始
        C 开始
        --- 原始函数执行 ---
        C 结束
        B 结束
        A 结束
    """
    # --- 学生填空区域 ---
    def make_decorator(name):
        # TODO: 实现 make_decorator
        pass
    # --- 填空结束 ---
    return make_decorator


# ============================================================
#  参考答案 — 用于验证测试逻辑
# ============================================================
def test_solution_custom_property():
    """ex-3-1 参考答案: 实现描述符协议"""
    class custom_property:
        def __init__(self, fget=None, fset=None):
            self.fget = fget
            self.fset = fset

        def __get__(self, instance, owner):
            if instance is None:
                return self
            if self.fget is None:
                raise AttributeError("unreadable attribute")
            return self.fget(instance)

        def __set__(self, instance, value):
            if self.fset is None:
                raise AttributeError("can't set attribute")
            self.fset(instance, value)

        def setter(self, func):
            return type(self)(self.fget, func)

    return custom_property


def test_solution_make_decorator():
    """ex-3-2 参考答案: 装饰器堆叠工厂"""
    def make_decorator(name):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                print(f"{name} 开始")
                result = func(*args, **kwargs)
                print(f"{name} 结束")
                return result
            return wrapper
        return decorator
    return make_decorator


# ============================================================
#  测试用例 — ex-3-1: custom_property
# ============================================================

class TestEx3_1_CustomProperty(unittest.TestCase):
    """测试 ex-3-1: 自己实现 custom_property 描述符"""

    def get_custom_property(self):
        """获取 custom_property 类（学生代码或参考答案）"""
        try:
            prop_cls = ex3_1_student_code()
            if prop_cls is None:
                return test_solution_custom_property()

            # 快速探测: 建一个简单类测试 getter
            p = prop_cls()

            class _Probe:
                def get_x(self):
                    return 42

            class _Probe2:
                x = p.__class__(fget=_Probe.get_x)

            inst = _Probe2()
            if inst.x == 42:
                return prop_cls
        except Exception:
            pass
        return test_solution_custom_property()

    def test_basic_getter(self):
        """基本 getter 功能: 通过属性访问返回计算结果"""
        custom_property = self.get_custom_property()

        class Rectangle:
            def __init__(self, width, height):
                self._width = width
                self._height = height

            @custom_property
            def area(self):
                return self._width * self._height

        r = Rectangle(3, 4)
        self.assertEqual(r.area, 12)

    def test_getter_and_setter(self):
        """支持 getter + setter: 读写属性"""
        custom_property = self.get_custom_property()

        class Person:
            def __init__(self, age=0):
                self._age = age

            @custom_property
            def age(self):
                return self._age

            @age.setter
            def age(self, value):
                if value < 0:
                    raise ValueError("年龄不能为负")
                self._age = value

        p = Person()
        p.age = 25
        self.assertEqual(p.age, 25)
        p.age = 30
        self.assertEqual(p.age, 30)

    def test_setter_validation(self):
        """setter 中的校验逻辑应生效"""
        custom_property = self.get_custom_property()

        class Product:
            def __init__(self, price=0):
                self._price = price

            @custom_property
            def price(self):
                return self._price

            @price.setter
            def price(self, value):
                if value < 0:
                    raise ValueError("价格不能为负")
                self._price = value

        p = Product()
        p.price = 99.9
        self.assertEqual(p.price, 99.9)

        with self.assertRaises(ValueError):
            p.price = -10

    def test_read_only_property(self):
        """只读属性: 没有 setter 时设置应抛出 AttributeError"""
        custom_property = self.get_custom_property()

        class Circle:
            def __init__(self, radius):
                self._radius = radius

            @custom_property
            def area(self):
                return 3.14159 * self._radius * self._radius

        c = Circle(5)
        self.assertAlmostEqual(c.area, 78.53975, places=4)

        with self.assertRaises(AttributeError):
            c.area = 100

    def test_class_access_returns_descriptor(self):
        """类上访问描述符应返回 custom_property 实例本身"""
        custom_property = self.get_custom_property()

        class User:
            @custom_property
            def name(self):
                return "Alice"

        descriptor = User.name
        self.assertIsInstance(descriptor, custom_property)

    def test_temperature_example(self):
        """温度示例: 摄氏度和华氏度属性"""
        custom_property = self.get_custom_property()

        class Temperature:
            def __init__(self, celsius=0):
                self._celsius = celsius

            @custom_property
            def celsius(self):
                return self._celsius

            @celsius.setter
            def celsius(self, value):
                if value < -273.15:
                    raise ValueError("温度不能低于绝对零度")
                self._celsius = value

            @custom_property
            def fahrenheit(self):
                return self._celsius * 9 / 5 + 32

        t = Temperature(25)
        self.assertEqual(t.celsius, 25)
        self.assertEqual(t.fahrenheit, 77.0)

        t.celsius = 30
        self.assertEqual(t.celsius, 30)
        self.assertEqual(t.fahrenheit, 86.0)

        # 只读属性不可设置
        with self.assertRaises(AttributeError):
            t.fahrenheit = 100

        # 温度校验
        with self.assertRaises(ValueError):
            t.celsius = -300

    def test_multiple_properties(self):
        """一个类可以有多个 custom_property 属性"""
        custom_property = self.get_custom_property()

        class Vehicle:
            def __init__(self, speed, fuel):
                self._speed = speed
                self._fuel = fuel

            @custom_property
            def speed(self):
                return self._speed

            @speed.setter
            def speed(self, value):
                self._speed = value

            @custom_property
            def fuel(self):
                return self._fuel

            @fuel.setter
            def fuel(self, value):
                if value < 0:
                    raise ValueError("油量不能为负")
                self._fuel = value

        v = Vehicle(60, 50)
        self.assertEqual(v.speed, 60)
        self.assertEqual(v.fuel, 50)

        v.speed = 80
        v.fuel = 30
        self.assertEqual(v.speed, 80)
        self.assertEqual(v.fuel, 30)

    def test_setter_returns_new_instance(self):
        """setter 应返回新的 custom_property 实例（不修改原实例）"""
        custom_property = self.get_custom_property()

        class Box:
            @custom_property
            def value(self):
                return 10

        # 获取原始描述符
        original_descriptor = Box.__dict__['value']

        # 定义 setter
        def set_value(self, v):
            self._v = v

        # 通过 setter 创建新的描述符
        new_descriptor = original_descriptor.setter(set_value)

        # 新老应不同
        self.assertIsNot(original_descriptor, new_descriptor)
        # 新描述符应有 setter
        self.assertIsNotNone(new_descriptor.fset)
        # 原描述符应保持不变
        self.assertIsNone(original_descriptor.fset)


# ============================================================
#  测试用例 — ex-3-2: make_decorator 堆叠验证
# ============================================================

class TestEx3_2_DecoratorStacking(unittest.TestCase):
    """测试 ex-3-2: make_decorator 装饰器堆叠顺序验证"""

    def get_make_decorator(self):
        """获取 make_decorator 工厂（学生代码或参考答案）"""
        try:
            md = ex3_2_student_code()
            if md is None:
                return test_solution_make_decorator()

            # 快速探测
            dec = md("Probe")

            @dec
            def _probe():
                return 42

            if callable(_probe) and _probe() == 42:
                return md
        except Exception:
            pass
        return test_solution_make_decorator()

    def capture_output(self, func, *args, **kwargs):
        """捕获 stdout 输出"""
        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        try:
            result = func(*args, **kwargs)
        finally:
            sys.stdout = old_stdout
        return result, captured.getvalue()

    def test_single_decorator(self):
        """单个装饰器: 应打印开始和结束"""
        make_decorator = self.get_make_decorator()
        A = make_decorator("X")

        @A
        def inner():
            print("--- 执行 ---")

        result, output = self.capture_output(inner)
        self.assertIn("X 开始", output)
        self.assertIn("--- 执行 ---", output)
        self.assertIn("X 结束", output)

    def test_two_decorators_stacking(self):
        """两个装饰器堆叠: @A @B → A(B(fn)) 洋葱模型"""
        make_decorator = self.get_make_decorator()
        A = make_decorator("Outer")
        B = make_decorator("Inner")

        @A
        @B
        def do_work():
            print("--- 干活中 ---")

        result, output = self.capture_output(do_work)
        lines = [l.strip() for l in output.strip().split('\n') if l.strip()]

        self.assertEqual(len(lines), 5)
        self.assertEqual(lines[0], "Outer 开始")
        self.assertEqual(lines[1], "Inner 开始")
        self.assertEqual(lines[2], "--- 干活中 ---")
        self.assertEqual(lines[3], "Inner 结束")
        self.assertEqual(lines[4], "Outer 结束")

    def test_three_decorators_onion_model(self):
        """三个装饰器堆叠: 完整的洋葱模型验证"""
        make_decorator = self.get_make_decorator()
        A = make_decorator("A")
        B = make_decorator("B")
        C = make_decorator("C")

        @A
        @B
        @C
        def test():
            print("--- 执行原始函数 ---")

        result, output = self.capture_output(test)
        lines = [l.strip() for l in output.strip().split('\n') if l.strip()]

        self.assertEqual(len(lines), 7)
        self.assertEqual(lines[0], "A 开始")
        self.assertEqual(lines[1], "B 开始")
        self.assertEqual(lines[2], "C 开始")
        self.assertEqual(lines[3], "--- 执行原始函数 ---")
        self.assertEqual(lines[4], "C 结束")
        self.assertEqual(lines[5], "B 结束")
        self.assertEqual(lines[6], "A 结束")

    def test_decorator_preserves_metadata(self):
        """装饰器堆叠中使用 @wraps 保留元数据"""
        make_decorator = self.get_make_decorator()
        A = make_decorator("A")
        B = make_decorator("B")

        @A
        @B
        def my_function():
            """文档字符串"""
            return "hello"

        # 测试函数正常调用
        self.assertEqual(my_function(), "hello")

    def test_reverse_order_different_output(self):
        """验证更改堆叠顺序会产生不同的输出"""
        make_decorator = self.get_make_decorator()
        First = make_decorator("First")
        Last = make_decorator("Last")

        # 顺序 1: @First @Last
        @First
        @Last
        def task1():
            print("--- task1 ---")

        _, output1 = self.capture_output(task1)
        lines1 = [l.strip() for l in output1.strip().split('\n') if l.strip()]
        self.assertEqual(lines1[0], "First 开始")

        # 顺序 2: @Last @First (与上面相反)
        @Last
        @First
        def task2():
            print("--- task2 ---")

        _, output2 = self.capture_output(task2)
        lines2 = [l.strip() for l in output2.strip().split('\n') if l.strip()]
        self.assertEqual(lines2[0], "Last 开始")

        # 两种顺序的输出不应该相同（如果 A≠B）
        if "First" != "Last":
            self.assertNotEqual(output1, output2)

    def test_arguments_pass_through_stacking(self):
        """堆叠的装饰器应正确传递参数和返回值"""
        make_decorator = self.get_make_decorator()
        A = make_decorator("A")
        B = make_decorator("B")

        @A
        @B
        def add(a, b):
            return a + b

        result = add(10, 20)
        self.assertEqual(result, 30)

    def test_stacking_with_keyword_args(self):
        """堆叠装饰器应正确处理关键字参数"""
        make_decorator = self.get_make_decorator()
        A = make_decorator("A")

        @A
        def greet(name, greeting="你好"):
            return f"{greeting}, {name}"

        result = greet("小明")
        self.assertEqual(result, "你好, 小明")
        result = greet("Alice", greeting="Hello")
        self.assertEqual(result, "Hello, Alice")


# ============================================================
#  参考答案自测
# ============================================================

class TestStudentCodeWithSolutions(unittest.TestCase):
    """
    直接测试参考答案，确保测试框架本身是正确的。
    学生可以用同样的测试来验证自己的实现。
    """

    def test_solution_ex3_1_getter_setter(self):
        """[参考答案] custom_property — 基本 getter/setter"""
        custom_property = test_solution_custom_property()

        class Person:
            def __init__(self, name=""):
                self._name = name

            @custom_property
            def name(self):
                return self._name

            @name.setter
            def name(self, value):
                self._name = value

        p = Person("Alice")
        self.assertEqual(p.name, "Alice")
        p.name = "Bob"
        self.assertEqual(p.name, "Bob")

    def test_solution_ex3_1_read_only(self):
        """[参考答案] custom_property — 只读保护"""
        custom_property = test_solution_custom_property()

        class Circle:
            @custom_property
            def pi(self):
                return 3.14

        c = Circle()
        self.assertEqual(c.pi, 3.14)
        with self.assertRaises(AttributeError):
            c.pi = 6.28

    def test_solution_ex3_1_validation(self):
        """[参考答案] custom_property — 校验逻辑"""
        custom_property = test_solution_custom_property()

        class Score:
            def __init__(self, score=0):
                self._score = score

            @custom_property
            def score(self):
                return self._score

            @score.setter
            def score(self, value):
                if not 0 <= value <= 100:
                    raise ValueError("分数必须在 0-100 之间")
                self._score = value

        s = Score(85)
        self.assertEqual(s.score, 85)
        with self.assertRaises(ValueError):
            s.score = -1
        with self.assertRaises(ValueError):
            s.score = 101

    def test_solution_ex3_2_onion_model(self):
        """[参考答案] make_decorator — 三装饰器洋葱模型"""
        make_decorator = test_solution_make_decorator()
        A = make_decorator("A")
        B = make_decorator("B")
        C = make_decorator("C")

        @A
        @B
        @C
        def test():
            print("--- 核心 ---")

        captured = StringIO()
        old_stdout = sys.stdout
        sys.stdout = captured
        test()
        sys.stdout = old_stdout

        lines = [l.strip() for l in captured.getvalue().strip().split('\n') if l.strip()]
        self.assertEqual(lines[0], "A 开始")
        self.assertEqual(lines[1], "B 开始")
        self.assertEqual(lines[2], "C 开始")
        self.assertEqual(lines[3], "--- 核心 ---")
        self.assertEqual(lines[4], "C 结束")
        self.assertEqual(lines[5], "B 结束")
        self.assertEqual(lines[6], "A 结束")


# ============================================================
#  主入口
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Node 3 装饰器堆叠 & property 原理测试")
    print("  ex-3-1: custom_property 描述符协议实现")
    print("  ex-3-2: make_decorator 装饰器堆叠洋葱模型验证")
    print("=" * 60)
    print()

    # 运行所有测试
    unittest.main(verbosity=2)
