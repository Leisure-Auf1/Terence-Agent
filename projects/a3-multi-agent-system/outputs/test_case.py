#!/usr/bin/env python3
"""
Node 2 测试脚本：带参数装饰器
- ex-2-1: retry(max_tries, delay)  — 失败自动重试
- ex-2-2: cache_ttl(seconds)       — TTL 缓存

用法: python node-2-tests.py
"""

import unittest
import time
from functools import wraps
from io import StringIO
import sys


# ============================================================
#  ╔═══════════════════════════════════════════════════════╗
#  ║  学生填空区域  —  请在此处完成你的实现                   ║
#  ╚═══════════════════════════════════════════════════════╝
# ============================================================

# ── 练习 2-1: retry(max_tries=3, delay=1) ─────────────────────────────────
# 要求:
#   1. 三层嵌套结构（带参数装饰器）
#   2. 函数抛出异常时自动重试，最多重试 max_tries 次
#   3. 每次重试前打印 "[RETRY]"
#   4. 必须使用 @functools.wraps 装饰 wrapper
#   5. 所有重试均失败，抛出最后一次的异常
#
# 提示: @retry(3, 1) → retry(3,1) 先执行，返回 decorator → decorator(func) 再执行
#
# ==== STUDENT CODE: ex-2-1 ====
def retry(max_tries=3, delay=1):
    # TODO: 实现三层嵌套的 retry 装饰器
    pass
# ==== END STUDENT CODE ====


# ── 练习 2-2: cache_ttl(seconds=30) ───────────────────────────────────────
# 要求:
#   1. 三层嵌套结构（带参数装饰器）
#   2. 缓存 key = (args, tuple(sorted(kwargs.items())))
#   3. 在 seconds 秒内返回缓存结果，过期后重新计算
#   4. 每次真正计算时打印 "正在计算..."
#   5. 必须使用 @functools.wraps 装饰 wrapper
#
# 提示: 缓存字典放在最外层（工厂函数内），确保所有调用共享同一缓存
#
# ==== STUDENT CODE: ex-2-2 ====
def cache_ttl(seconds=30):
    # TODO: 实现三层嵌套的 cache_ttl 装饰器
    pass
# ==== END STUDENT CODE ====


# ============================================================
#  ╔═══════════════════════════════════════════════════════╗
#  ║  参考答案（仅供测试框架兜底使用，请先尝试自己实现）      ║
#  ╚═══════════════════════════════════════════════════════╝
# ============================================================

def _ref_retry(max_tries=3, delay=1):
    """参考答案: retry 装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_tries - 1:
                        print("[RETRY]")
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator


def _ref_cache_ttl(seconds=30):
    """参考答案: cache_ttl 装饰器"""
    cache = {}
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                result, expiry = cache[key]
                if now < expiry:
                    return result
                del cache[key]
            result = func(*args, **kwargs)
            cache[key] = (result, now + seconds)
            return result
        return wrapper
    return decorator


# ============================================================
#  Probe 检测 — 自动判断学生是否完成了实现
# ============================================================
def _probe():
    """
    检测学生的 retry / cache_ttl 是否已正确实现。
    - 如果实现了 → 使用学生版本
    - 如果没实现（pass / 抛出异常 / 不是三层结构）→ 使用参考答案
    """
    result = {}

    # ── 检测 retry ──
    try:
        mid = retry(max_tries=1, delay=0)
        if not callable(mid):
            raise TypeError("retry 未返回可调用对象（可能只有两层？）")
        @mid
        def _p1():
            return 42
        if callable(_p1) and _p1() == 42:
            result['retry'] = retry
            print("[PROBE] ✅ retry — 使用学生实现")
        else:
            raise RuntimeError("wrapper 不可调用")
    except Exception as e:
        print(f"[PROBE] ⚠️  retry — 未实现或有问题 ({e})，切换为参考答案")
        result['retry'] = _ref_retry

    # ── 检测 cache_ttl ──
    try:
        mid = cache_ttl(seconds=10)
        if not callable(mid):
            raise TypeError("cache_ttl 未返回可调用对象（可能只有两层？）")
        @mid
        def _p2():
            return 99
        if callable(_p2) and _p2() == 99:
            result['cache_ttl'] = cache_ttl
            print("[PROBE] ✅ cache_ttl — 使用学生实现")
        else:
            raise RuntimeError("wrapper 不可调用")
    except Exception as e:
        print(f"[PROBE] ⚠️  cache_ttl — 未实现或有问题 ({e})，切换为参考答案")
        result['cache_ttl'] = _ref_cache_ttl

    return result


_IMPLS = _probe()
retry = _IMPLS['retry']
cache_ttl = _IMPLS['cache_ttl']


# ============================================================
#  测试用例
# ============================================================

class TestRetryDecorator(unittest.TestCase):
    """ex-2-1: retry(max_tries, delay) 装饰器"""

    def test_success_no_retry(self):
        """函数成功 → 不触发重试，直接返回结果"""
        call_count = [0]

        @retry(max_tries=3, delay=0)
        def add(a, b):
            call_count[0] += 1
            return a + b

        buf = StringIO()
        sys.stdout = buf
        result = add(3, 5)
        sys.stdout = sys.__stdout__

        self.assertEqual(result, 8)
        self.assertEqual(call_count[0], 1)
        self.assertNotIn("[RETRY]", buf.getvalue())

    def test_fails_then_succeeds(self):
        """前几次失败、最终成功 → 应打印 [RETRY] 并返回正确结果"""
        call_count = [0]

        @retry(max_tries=3, delay=0)
        def flaky():
            call_count[0] += 1
            if call_count[0] < 3:
                raise ValueError("还没好")
            return "终于成功"

        buf = StringIO()
        sys.stdout = buf
        result = flaky()
        sys.stdout = sys.__stdout__

        self.assertEqual(result, "终于成功")
        self.assertEqual(call_count[0], 3)
        self.assertEqual(buf.getvalue().count("[RETRY]"), 2)

    def test_all_fail_raises(self):
        """全部重试失败 → 抛出最后一次异常"""
        call_count = [0]

        @retry(max_tries=3, delay=0)
        def always_fail():
            call_count[0] += 1
            raise RuntimeError(f"炸了 #{call_count[0]}")

        buf = StringIO()
        sys.stdout = buf
        with self.assertRaises(RuntimeError) as ctx:
            always_fail()
        sys.stdout = sys.__stdout__

        self.assertEqual(call_count[0], 3)
        self.assertIn("炸了 #3", str(ctx.exception))
        self.assertEqual(buf.getvalue().count("[RETRY]"), 2)

    def test_preserves_metadata(self):
        """装饰后的函数应保留 __name__ 和 __doc__"""
        @retry(max_tries=3, delay=0)
        def fetch_data():
            """获取数据的函数"""
            return "data"

        self.assertEqual(fetch_data.__name__, "fetch_data")
        self.assertIn("获取数据", fetch_data.__doc__ or "")

    def test_passes_kwargs(self):
        """关键字参数应正确传递"""
        captured = {}

        @retry(max_tries=2, delay=0)
        def fn(a, b=10):
            captured['a'] = a
            captured['b'] = b
            return a + b

        result = fn(5, b=20)
        self.assertEqual(result, 25)
        self.assertEqual(captured, {'a': 5, 'b': 20})


class TestCacheTTLDecorator(unittest.TestCase):
    """ex-2-2: cache_ttl(seconds) 装饰器"""

    def test_first_call_computes(self):
        """首次调用 → 执行计算，打印 '正在计算...'"""
        @cache_ttl(seconds=30)
        def expensive(n):
            print("正在计算...")
            return n * n

        buf = StringIO()
        sys.stdout = buf
        result = expensive(100)
        sys.stdout = sys.__stdout__

        self.assertEqual(result, 10000)
        self.assertIn("正在计算...", buf.getvalue())

    def test_second_call_cached(self):
        """TTL 内重复调用 → 用缓存，不重复计算"""
        call_count = [0]

        @cache_ttl(seconds=30)
        def expensive(n):
            call_count[0] += 1
            print("正在计算...")
            return n * n

        buf = StringIO()
        sys.stdout = buf
        r1 = expensive(5)
        r2 = expensive(5)
        sys.stdout = sys.__stdout__

        self.assertEqual(r1, 25)
        self.assertEqual(r2, 25)
        self.assertEqual(call_count[0], 1)
        self.assertEqual(buf.getvalue().count("正在计算..."), 1)

    def test_cache_expires(self):
        """TTL 过期 → 重新计算"""
        call_count = [0]

        @cache_ttl(seconds=0.05)
        def expensive(n):
            call_count[0] += 1
            print("正在计算...")
            return n * n

        r1 = expensive(3)
        time.sleep(0.1)
        r2 = expensive(3)

        self.assertEqual(r1, 9)
        self.assertEqual(r2, 9)
        self.assertEqual(call_count[0], 2)

    def test_different_args_separate_cache(self):
        """不同参数 → 独立缓存条目"""
        called = []

        @cache_ttl(seconds=30)
        def expensive(n):
            called.append(n)
            print("正在计算...")
            return n * n

        expensive(10)
        expensive(20)
        expensive(10)  # 缓存命中

        self.assertEqual(called, [10, 20])

    def test_kwargs_order_insensitive(self):
        """关键字参数顺序不同 → 应命中同一缓存"""
        call_count = [0]

        @cache_ttl(seconds=30)
        def fn(a, b=0, c=0):
            call_count[0] += 1
            return a + b + c

        r1 = fn(1, b=2, c=3)
        r2 = fn(1, c=3, b=2)  # 顺序不同，应缓存命中
        r3 = fn(1, b=2, c=4)  # 值不同，应重新计算

        self.assertEqual(r1, 6)
        self.assertEqual(r2, 6)
        self.assertEqual(r3, 7)
        self.assertEqual(call_count[0], 2)

    def test_preserves_metadata(self):
        """装饰后的函数应保留 __name__ 和 __doc__"""
        @cache_ttl(seconds=30)
        def heavy(x):
            """重量级计算"""
            return x + 1

        self.assertEqual(heavy.__name__, "heavy")
        self.assertIn("重量级", heavy.__doc__ or "")


# ============================================================
#  主入口
# ============================================================
if __name__ == "__main__":
    print()
    print("=" * 60)
    print("  Node 2 测试：带参数装饰器")
    print("  ex-2-1: retry(max_tries, delay)    ex-2-2: cache_ttl(seconds)")
    print("=" * 60)
    print()

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__]))

    # 汇总
    print()
    print("=" * 60)
    total = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    passed = total - failures - errors

    if failures == 0 and errors == 0:
        print(f"  ✅ 全部通过！{passed}/{total} 测试成功")
        print("  恭喜你掌握了带参数装饰器 🎉")
    else:
        print(f"  ❌ {passed}/{total} 通过  |  {failures} 失败  |  {errors} 错误")
        print("  请检查你的实现，对照讲义中的三层结构模板")
    print("=" * 60)
