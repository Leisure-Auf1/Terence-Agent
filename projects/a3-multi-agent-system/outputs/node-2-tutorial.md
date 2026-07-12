# Node 2: 带参数装饰器、functools.wraps 与高级装饰器模式

> **难度**: 进阶 · **前置**: 已掌握 Node 1（闭包 + 无参装饰器）

---

## 一、回顾：无参装饰器 = 两层结构

Node 1 中学到的标准模板：

```python
def logger(func):                     # 第 1 层：接收被装饰函数
    def wrapper(*args, **kwargs):     # 第 2 层：替换后的函数
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logger
def say_hello(): ...
```

问题来了：如果想写 `@logger("DEBUG")`——装饰器带参数，两层结构就不够用了。

---

## 二、带参装饰器：为什么必须三层？

### ❌ 直觉写法（行不通）

```python
def retry(func, max_tries=3):    # 想同时接收 func 和参数？
    def wrapper(*args, **kwargs):
        for i in range(max_tries):
            try:
                return func(*args, **kwargs)
            except Exception:
                if i == max_tries - 1:
                    raise
    return wrapper

@retry(3)          # ❌ TypeError! retry() missing 1 required positional argument: 'func'
def fetch(): ...
```

**原因**：`@retry(3)` 首先执行 `retry(3)`，此时 Python 还没有把 `fetch` 传给 `retry`。所以 `retry` 的第一个参数必须是 `max_tries`，不能是 `func`。

### ✅ 正确写法：三层嵌套

```python
import functools, time

def retry(max_tries=3, delay=1):          # 第 1 层：工厂 — 接收装饰器参数
    def decorator(func):                   # 第 2 层：真正的装饰器 — 接收函数
        @functools.wraps(func)
        def wrapper(*args, **kwargs):      # 第 3 层：替换 — 接收调用参数
            for i in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_tries - 1:
                        raise
                    print(f"[RETRY] {i+1}/{max_tries} 失败: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_tries=3, delay=1)              # retry(3,1) → 返回 decorator → decorator(fetch) → 返回 wrapper
def fetch(url):
    return "数据获取成功"
```

**执行顺序拆解**：

```
@retry(max_tries=3, delay=1)
def fetch(url): ...

# 等价于:
#   ① factory_result = retry(3, 1)        ← 第 1 层被执行，返回 decorator
#   ② fetch = factory_result(fetch)        ← 第 2 层接收函数，返回 wrapper
```

| 层级 | 接收什么 | 返回什么 | 何时执行 |
|------|----------|----------|----------|
| 第 1 层（工厂） | `max_tries`, `delay` | 真正的装饰器 | `@retry(...)` 定义时 |
| 第 2 层（装饰器） | `func` | wrapper | 紧接上一步 |
| 第 3 层（wrapper） | `*args, **kwargs` | 原函数返回值 | 每次调用时 |

---

## 三、functools.wraps：不能省略的"身份证"

### ❌ 不加 @wraps

```python
def bad_logger(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_logger
def greet():
    """问候语"""
    pass

print(greet.__name__)  # ❌ 'wrapper' — 原函数名丢失！
print(greet.__doc__)   # ❌ None — 文档字符串丢失！
```

后果：调试工具、文档生成器、IDE 智能提示全部失效。

### ✅ 加上 @wraps

```python
import functools

def good_logger(func):
    @functools.wraps(func)          # ← 把 func 的元信息复制到 wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_logger
def greet():
    """问候语"""
    pass

print(greet.__name__)  # ✅ 'greet'
print(greet.__doc__)   # ✅ '问候语'
```

`@functools.wraps(func)` 内部调用 `functools.update_wrapper`，复制了 `__name__`、`__doc__`、`__module__`、`__qualname__` 以及 `__dict__`，还设置了 `__wrapped__` 属性指向原函数。**铁律：每个装饰器的 wrapper 上都必须加 @wraps。**

---

## 四、带参装饰器通用模板

```python
import functools

def your_decorator(param1, param2="default"):   # ① 工厂：接收配置
    def decorator(func):                          # ② 装饰器：接收函数
        @functools.wraps(func)                    # ③ 必须加！
        def wrapper(*args, **kwargs):             # ④ 替换逻辑
            # 前置操作（可使用 param1, param2）
            result = func(*args, **kwargs)
            # 后置操作
            return result
        return wrapper
    return decorator
```

---

## 五、类装饰器：用 __call__ 实现

当需要**跨调用维护状态**（如计数器、缓存）时，类装饰器比闭包更自然。

### 无参类装饰器

```python
class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"[{self.count}] 调用 {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def hello(name):
    return f"你好, {name}!"

hello("小明")  # [1] 调用 hello
hello("小红")  # [2] 调用 hello
print(hello.count)  # 2 — 状态跨调用持久化
```

### 带参类装饰器

```python
class Retry:
    def __init__(self, max_tries=3, delay=1):    # __init__ 接收配置参数
        self.max_tries = max_tries
        self.delay = delay

    def __call__(self, func):                     # __call__ 接收被装饰函数
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(self.max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == self.max_tries - 1:
                        raise
                    print(f"[RETRY] {i+1}/{self.max_tries}")
                    time.sleep(self.delay)
        return wrapper

@Retry(max_tries=5, delay=0.5)                    # Retry(5, 0.5) → 实例 → 实例(fetch) → wrapper
def fetch(url):
    return "数据获取成功"
```

执行流程：`@Retry(5, 0.5)` → `__init__(5, 0.5)` 创建实例 → `__call__(fetch)` 返回 wrapper。

---

## 六、小结 ❌ vs ✅

| 场景 | ❌ | ✅ |
|------|----|----|
| 带参装饰器 | 两层嵌套，参数和 func 混在一起 | 三层：工厂 → 装饰器 → wrapper |
| 元信息保留 | 忘记 @wraps | 每个 wrapper 都加 @wraps |
| 跨调用状态 | 全局变量 | 类装饰器或外层闭包变量 |
| 缓存/重试 | 每个函数重复实现 | 抽取为 @cache_ttl / @retry |

---

## 配套练习

- **ex-2-1**: 实现 `retry(max_tries, delay)` — 失败自动重试
- **ex-2-2**: 实现 `cache_ttl(seconds)` — TTL 过期缓存

运行 `python outputs/node-2-tests.py` 验证你的实现。
