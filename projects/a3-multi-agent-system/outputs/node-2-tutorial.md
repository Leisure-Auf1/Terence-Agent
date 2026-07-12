# Node 2: 带参装饰器 · 套娃工厂 · 身份证 · 实战套路

> **难度**: 进阶 · **前置**: 搞定了 Node 1（闭包 + 无参装饰器）

---

## §2.1 回顾：无参装饰器就两层，很简单

Node 1 我们搞清楚了——装饰器本质上就是"把函数塞进另一个函数里加工一下再吐出来"。标准模板长这样：

```python
def logger(func):                     # 第 1 层：接收被装饰函数
    def wrapper(*args, **kwargs):     # 第 2 层：替换后的函数
        print(f"调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@logger
def say_hello():
    print("你好!")
```

`@logger` 等价于 `say_hello = logger(say_hello)`——就这一句话，没别的魔法。

❌ **新手踩坑**: 忘了 `return wrapper`，装饰器返回 `None`，调用时报 `TypeError: 'NoneType' object is not callable`。
✅ **正确做法**: 装饰器必须返回一个可调用对象（通常就是 wrapper）。

可现在问题来了——我想写 `@retry(max_tries=3)`，装饰器自己也要接收参数。两层不够用了，怎么办？

**本节新概念 (3个)**：无参装饰器两层结构 · @语法糖等价写法 · 必须 return wrapper

---

## §2.2 套娃登场：为什么必须三层？

### ❌ 直觉写法——行不通！

你可能会想："把参数加到第一层不就行了？"

```python
def retry(func, max_tries=3):    # 想一口气接收 func 和参数？
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

Python 看到 `@retry(3)`，**先执行 `retry(3)`**——此时 `func` 根本还没传进来！`max_tries` 拿到了 3，`func` 没着落，直接炸。

### ✅ 三层套娃——工厂→装饰器→替换

想象一个套娃玩具：打开最外层，里面还有一层，再打开，最里面才是核心。带参装饰器就是这个结构：

```python
import functools, time

def retry(max_tries=3, delay=1):          # 最外层：工厂——接收配置参数
    def decorator(func):                   # 中间层：真正的装饰器——接收函数
        @functools.wraps(func)
        def wrapper(*args, **kwargs):      # 最内层：替换后的函数——干活的
            for i in range(max_tries):
                try:
                    return func(*args, **kwargs)

```python
# 💡 快速对比: 没有装饰器 vs 用装饰器
# 完整代码见讲义上下文
```

                except Exception as e:
                    if i == max_tries - 1:
                        raise
                    print(f"[RETRY] {i+1}/{max_tries} 失败: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_tries=3, delay=1)
def fetch(url):
    return "数据获取成功"
```

**执行顺序拆一下**：

```
@retry(max_tries=3, delay=1)    ← retry(3,1) 执行，返回 decorator
def fetch(url): ...             ← decorator(fetch) 执行，返回 wrapper
                                ← fetch 这个名字现在指向 wrapper
```

把 `retry` 的外层想象成**工厂**：你告诉工厂"我要生产一个 `max_tries=3` 的重试装饰器"，工厂把真正的装饰器 `decorator` 生产出来，`decorator` 再包装你的函数。

| 层级 | 叫什么 | 接收什么 | 返回什么 | 何时执行 |
|------|--------|----------|----------|----------|
| 第 1 层 | 工厂 | `max_tries`, `delay` | 装饰器 | `@retry(...)` 时 |
| 第 2 层 | 装饰器 | `func` | wrapper | 紧接上一步 |
| 第 3 层 | wrapper | `*args, **kwargs` | 原函数返回值 | 每次调用时 |

❌ **两层不够**：参数和 func 挤在同一层，`@decorator(arg)` 语法根本解析不了。
✅ **三层各行其是**：外层管配置，中层管包装，内层管执行——职责清晰，互不打架。

**本节新概念 (3个)**：三层套娃/工厂模式 · 执行顺序两步走 · 闭包捕获外层参数

---

## §2.3 @wraps：给 wrapper 办张身份证

### ❌ 不加 @wraps——wrapper 是黑户

```python
def bad_logger(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@bad_logger
def greet():
    """问候语"""
    return "你好"

print(greet.__name__)  # ❌ 'wrapper' —— 我是谁？我在哪？
print(greet.__doc__)   # ❌ None —— 文档字符串凭空消失！
```

你的 `greet` 函数被 wrapper 替换之后，`__name__` 变成了 `wrapper`，`__doc__` 丢了。调试时看日志全是 `wrapper`，根本不知道哪个函数在跑。IDE 的智能提示、文档生成器也全废了——wrapper 是个"黑户"，没身份。

### ✅ 加上 @wraps——正儿八经的身份

```python
import functools

def good_logger(func):
    @functools.wraps(func)          # ← 把 func 的"身份证信息"复制给 wrapper
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@good_logger
def greet():
    """问候语"""
    return "你好"

print(greet.__name__)  # ✅ 'greet' —— 身份对上了！
print(greet.__doc__)   # ✅ '问候语' —— 文档回来了！
```

`@functools.wraps(func)` 做了什么？它把 `func` 的 `__name__`、`__doc__`、`__module__`、`__qualname__` 这些元信息全部复制到 wrapper 上，还额外加了 `__wrapped__` 属性，指向原始函数。相当于给 wrapper 办了一张**身份证**——看起来是 wrapper，但名字、出身都继承了原函数。

❌ **不加 @wraps**：wrapper 是个无名氏，调试地狱，文档工具全瞎。
✅ **加了 @wraps**：wrapper 顶着原函数的身份干活，谁都认得出。

> **铁律**：每个装饰器的 wrapper 上都必须加 `@functools.wraps(func)`，没有例外。

**本节新概念 (3个)**：元信息丢失 · @wraps 复制身份 · __wrapped__ 指向原函数

---

## §2.4 实战：@retry + @cache_ttl 两个轮子

光说不练假把式。来看两个实际场景，把上面的套路用起来。

### @retry：失败了自动重试

```python
import functools, time, random

def retry(max_tries=3, delay=1):
    """工厂：生产一个重试 N 次的装饰器"""
    def decorator(func):
        @functools.wraps(func)              # ← 身份证不能忘！
        def wrapper(*args, **kwargs):
            for i in range(max_tries):
                try:

```python
# 💡 快速对比: 没有装饰器 vs 用装饰器
# 完整代码见讲义上下文
```

                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_tries - 1:
                        raise               # 最后一次了，放弃
                    print(f"[RETRY] {func.__name__} 第{i+1}次失败: {e}")
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_tries=3, delay=0.5)
def unstable_api():
    if random.random() < 0.7:
        raise ConnectionError("网络波动")
    return "数据到手!"
```

❌ **不用装饰器**：每个需要重试的函数里塞一套 `for + try/except`，代码臭不可闻。
✅ **用 @retry**：一行装饰器搞定，重试逻辑和业务逻辑彻底分离。

### @cache_ttl：带过期时间的缓存

```python
import functools, time

def cache_ttl(seconds=60):
    """工厂：生产一个 TTL 缓存的装饰器"""
    def decorator(func):
        cache = {}                           # 闭包里的缓存字典
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:

```python
# 💡 快速对比: 没有装饰器 vs 用装饰器
# 完整代码见讲义上下文
```

                value, expire_at = cache[key]
                if now < expire_at:
                    print(f"[CACHE HIT] {func.__name__}{args}")
                    return value
            result = func(*args, **kwargs)
            cache[key] = (result, now + seconds)
            return result
        return wrapper
    return decorator

@cache_ttl(seconds=30)
def fetch_price(stock_id):
    print(f"[FETCH] 查询 {stock_id} 价格...")
    return random.randint(10, 500)
```

可以看到 @cache_ttl 和 @retry 结构一模一样：工厂接收参数 → 装饰器接收函数 → wrapper 干正事。**套娃模板复用了**。

❌ **不用装饰器**：手动管理缓存字典 + 过期逻辑，散落在各处，改一个漏十个。
✅ **用 @cache_ttl**：缓存策略集中在一处，哪个函数需要就挂上，干净利落。

**本节新概念 (4个)**：@retry 自动重试模式 · @cache_ttl TTL缓存 · 闭包存状态 · 装饰器模板复用

---

## §2.5 类装饰器：当闭包不够用了

闭包写装饰器很好，但有时候你需要**跨调用维护状态**（比如统计调用次数、累积数据）。这时用类来实现装饰器更直观——状态存在 `self` 上，清晰明了。

### 无参类装饰器：__init__ 收函数，__call__ 替换它

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)   # ← 类装饰器的 @wraps 等价写法
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        print(f"[第{self.count}次] 调用 {self.func.__name__}")
        return self.func(*args, **kwargs)

@CountCalls
def hello(name):
    return f"你好, {name}!"

hello("小明")  # [第1次] 调用 hello
hello("小红")  # [第2次] 调用 hello
print(hello.count)  # 2 —— 状态跨调用一直活着
```

`@CountCalls` 等价于 `hello = CountCalls(hello)`。实例的 `self.count` 在两次调用之间保持——这就是类的天然优势。

❌ **闭包存状态**：得用 `nonlocal` 或者可变容器（如 `[0]`），别扭。
✅ **类装饰器**：`self.xxx` 直截了当，状态管理一目了然。

### 带参类装饰器：__init__ 收参数，__call__ 收函数

```python
class Retry:
    def __init__(self, max_tries=3, delay=1):    # 工厂角色：接收配置参数
        self.max_tries = max_tries
        self.delay = delay

    def __call__(self, func):                     # 装饰器角色：接收被装饰函数
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

@Retry(max_tries=5, delay=0.5)                    # ① Retry(5,0.5) → 实例
def fetch(url):                                   # ② 实例(fetch) → wrapper
    return "数据获取成功"
```

`@Retry(5, 0.5)` → `__init__(5, 0.5)` 创建实例 → `__call__(fetch)` 返回 wrapper。和函数式三层套娃的对应关系一模一样：

| 函数式 | 类式 |
|--------|------|
| 最外层工厂 `retry(max_tries, delay)` | `__init__(self, max_tries, delay)` |
| 中间层 `decorator(func)` | `__call__(self, func)` |
| 最内层 `wrapper(*args, **kwargs)` | 同上，在 `__call__` 里定义 |

❌ **函数式 vs 类式**：不是"哪个更好"的问题——需要维护复杂状态（计数器、统计、连接池）就上类；简单的日志/计时/重试用函数式足够。
✅ **两者都掌握**：该用哪个用哪个，不纠结。

**本节新概念 (3个)**：__init__ + __call__ 模式 · 无参/带参类装饰器 · self 维护跨调用状态

---

## 全章小结

| 问题 | ❌ | ✅ |
|------|----|----|
| 装饰器要带参数 | 两层嵌套，func 和参数打架 | 三层套娃：工厂→装饰器→wrapper |
| wrapper 身份不明 | 忘了 `@wraps`，调试信息全丢 | 每个 wrapper 都加 `@functools.wraps(func)` |
| 需要跨调用状态 | 全局变量满天飞 | 类装饰器，`self` 存状态 |
| 重试/缓存逻辑重复 | 每个函数里手写一套 | 抽出 `@retry` / `@cache_ttl`，一次编写到处复用 |

---

## 配套练习

- **ex-2-1**: 实现 `retry(max_tries, delay)` —— 失败自动重试
- **ex-2-2**: 实现 `cache_ttl(seconds)` —— TTL 过期缓存

运行 `python outputs/node-2-tests.py` 验证你的实现。
