# Node 1: 从函数是一等公民到第一个装饰器

> **难度**: 入门  |  **预计阅读**: 15 分钟

---

## §1.1 函数是对象 — 给函数「贴标签」

Python 里，函数跟整数、字符串一样，就是个普普通通的对象。你可以给同一个函数对象贴好几个标签——就像一个人可以有中文名和英文名，但指的都是同一个人。

```python
def greet(name):
    return f"你好, {name}!"

print(type(greet))        # <class 'function'> — 看，它就是个对象

# 给同一个函数对象再贴一张标签
say_hello = greet         # ← 「贴标签」，不是复制函数
print(say_hello("Alice")) # 你好, Alice!
```

> 💡 `greet` 只是一张贴在内存中函数对象上的标签。`say_hello = greet` 就是又贴了一张标签上去，它们指向同一个东西。

既然是对象，自然可以塞进列表、当参数传、甚至作为返回值。下面是 **❌ vs ✅** 对比：

```python
# ❌ 如果你不知道函数是对象 — 你会写死调用
print(greet("张三"))
print(greet("李四"))

# ✅ 知道函数是对象 — 你可以这样玩
tasks = [greet, greet, greet]       # 把函数塞进列表
for task in tasks:
    print(task("王五"))              # 循环调用，想调几次调几次
```

**本节新概念（3 个）**: 函数是对象 / 赋值贴标签 / 函数放进列表。

---

## §1.2 闭包 — 函数随身带的「隐形背包」

把函数当返回值返回时，内部函数会偷偷背一个「隐形背包」——里面装着它出生时看到的所有外部变量。

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor     # ← factor 不在 multiply 里定义，但能用！
    return multiply

times_3 = make_multiplier(3)
print(times_3(7))             # 21 — factor=3 活在 multiply 的「隐形背包」里
```

可以翻一下这个背包：

```python
print(times_3.__closure__)                       # 背包存在
print(times_3.__closure__[0].cell_contents)      # 3 ← 就是 factor!
```

如果需要修改背包里的变量，要用 `nonlocal` 声明：

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count        # ← 告诉 Python: 我要改背包里的 count
        count += 1
        return count
    return counter

c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3 — 背包里的 count 在默默累积
```

> 🎒 **闭包 = 内部函数 + 它背着的隐形背包**（里面装着创建时捕获的外部变量）。

**本节新概念（3 个）**: 闭包 / 隐形背包 / nonlocal。

---

## §1.3 装饰器 — 给函数「穿衣服」

好，现在把前两节串起来：**装饰器 = 一个接受函数、返回函数的闭包**。它做的事情就是——给原始函数外面「穿一件衣服」，不改动原函数内部，却增加了新行为。

### ❌ 没穿衣服的写法（手动加日志）

```python
def add(a, b):
    print("[LOG] 开始执行 add")      # 每处都要写
    result = a + b
    print("[LOG] add 执行结束")      # 每处都要写
    return result

def subtract(a, b):
    print("[LOG] 开始执行 subtract")  # 又写一遍…
    result = a - b
    print("[LOG] subtract 执行结束")  # 又写一遍…
    return result
```

问题：日志逻辑跟业务逻辑搅在一起，修一处要改 N 处。

### ✅ 穿上装饰器（手写版，不用 @ 语法糖）

```python
def logger(func):                       # ① 接收原函数
    def wrapper(*args, **kwargs):       # ② 穿一件「外套」— 闭包
        print(f"[LOG] 开始执行 {func.__name__}")
        result = func(*args, **kwargs) # ③ *args/**kwargs 收集所有参数 → 原样透传给原函数
        print(f"[LOG] {func.__name__} 执行结束")
        return result                  # ④ 返回原函数的结果
    return wrapper

# 手动「穿衣服」
add = logger(add)

print(add(3, 5))
# [LOG] 开始执行 add
# [LOG] add 执行结束
# 8
```

> 🧥 **`*args, **kwargs` 的作用**: 收集调用 wrapper 时传入的所有参数（位置参数→元组，关键字参数→字典），然后一模一样地转发给原始函数。这样无论原函数接受什么参数，wrapper 都能正确透传。

### ✅ 用 @ 语法糖（穿衣服的快捷方式）

```python
@logger            # ← 等价于 add = logger(add)，像给函数穿了一件衣服
def add(a, b):
    return a + b

@logger
def subtract(a, b):
    return a - b

# 调用时自动带日志 —— 衣服穿上了就不用管了
print(add(3, 5))
print(subtract(8, 2))
```

> 🍬 `@decorator` 不是什么魔法，它就是 `func = decorator(func)` 的简写。Python 看到 `@logger`，就自动帮你把下一行定义的函数穿进 `logger` 这件衣服里。

**本节新概念（4 个）**: 装饰器 / wrapper 函数 / @语法糖（穿衣服） / *args/**kwargs 透传。

---

## §1.4 带参数装饰器 — 「工厂」生产「衣服」

如果想让装饰器接收参数，比如 `@repeat(3)` ——"把函数重复执行 3 次"——就需要套三层。

你可以把 **最外层函数** 理解为「工厂」：`repeat(n)` 这个工厂接收参数 `n`，然后 **生产** 出一个装饰器（衣服），再由这个装饰器去包裹原始函数。这就是「套娃」结构：

```python
def repeat(n):                           # 🏭 第一层：工厂函数
    def actual_decorator(func):          # 🧥 第二层：真正的装饰器（衣服）
        def wrapper(*args, **kwargs):    # 🎁 第三层：替换后的函数
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return actual_decorator              # ← 工厂返回一个装饰器

@repeat(3)
def say_hi(name):
    return f"你好, {name}"

print(say_hi("Alice"))
# ['你好, Alice', '你好, Alice', '你好, Alice']
```

三层「套娃」拆解：

| 层级 | 谁 | 干了什么 | 何时执行 |
|------|-----|---------|---------|
| 第一层 `repeat(n)` | 工厂 | 接收参数，生产装饰器 | `@repeat(3)` 时立即调用 |
| 第二层 `actual_decorator` | 衣服 | 接收原函数，返回 wrapper | 紧接着，接收 `say_hi` |
| 第三层 `wrapper` | 成品 | 真正被调用的函数 | 每次调用 `say_hi(...)` 时 |

等效手动写法：`say_hi = repeat(3)(say_hi)` —— 先调工厂拿到衣服，再给函数穿衣服。

**本节新概念（3 个）**: 装饰器工厂 / 三层套娃 / 带参装饰器。

---

## §1.5 functools.wraps — 别让衣服把名字藏起来

装饰器有一个暗坑：衣服穿上去之后，函数的「身份证」丢了。

```python
# ❌ 不加 @wraps 的后果
def add(a, b):
    """返回两数之和"""
    return a + b

decorated_add = logger(add)
print(decorated_add.__name__)   # wrapper   ← 名字丢了！
print(decorated_add.__doc__)    # None      ← 文档也没了！

# 这会导致什么？调试时 traceback 里显示的是 wrapper，你根本不知道是哪个函数崩的。
# 更糟的是，某些框架（如 Flask）靠 __name__ 注册路由，名字错了路由就挂了。
```

```python
# ✅ 加上 @wraps — 把身份证从原函数复制过来
from functools import wraps

def logger(func):
    @wraps(func)                 # ← 这一行，把 func 的 __name__/__doc__ 等信息全搬到 wrapper 上
    def wrapper(*args, **kwargs):
        print(f"[LOG] 开始执行 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} 执行结束")
        return result
    return wrapper

@logger
def add(a, b):
    """返回两数之和"""
    return a + b

print(add.__name__)   # add        ← 名字保留！
print(add.__doc__)    # 返回两数之和  ← 文档保留！
```

> 🛡️ **铁律**: 写装饰器时，永远在 `def wrapper(...)` 上面加一行 `@wraps(func)`。不加的后果不是报错，而是调试地狱。

**本节新概念（2 个）**: @functools.wraps / 元信息保留。

---

## 总结 — 一张图串起全部

```
函数是对象（给函数贴标签）
       ↓
闭包（内部函数背着「隐形背包」，记住外部变量）
       ↓
装饰器（接受函数、返回函数的闭包 → 给原函数「穿衣服」）
       ↓
@语法糖（func = decorator(func) 的简写）
       ↓
带参数装饰器（「工厂」生产「衣服」→ 三层套娃）
       ↓
@wraps（别让衣服藏起函数的身份证）
```

装饰器最常用的场景：**日志、计时、权限检查、缓存、重试**。这些「横切」逻辑——跟业务无关但到处需要——用装饰器写一次，到处穿，干净利落。

---

> 🎯 **搞定！** 现在你已经把装饰器的每一块积木都摸过一遍了。接下来动手写两道练习题，把知识焊进手指里。
