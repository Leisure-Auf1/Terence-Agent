# Node 1: 从函数是一等公民到第一个装饰器

> **难度**: 入门  |  **预计阅读**: 15 分钟

---

## 1. 函数是一等公民 — 一切从这里开始

在 Python 中，**函数就是对象**。你可以像对待整数、字符串一样对待函数：把它赋值给变量、放进列表、甚至当作礼物送给另一个函数。

```python
def greet(name):
    return f"你好, {name}!"

# 函数本身就是一个对象 — 它有自己的 id 和 type
print(type(greet))   # <class 'function'>
print(id(greet))     # 某个内存地址, 比如 140234567890

# 把函数赋值给另一个变量
say_hello = greet
print(say_hello("Alice"))   # 你好, Alice!
```

> 💡 **关键洞察**: `greet` 只是一个标签，贴在内存中的函数对象上。当你 `say_hello = greet` 时，你只是给同一个函数对象多贴了一张标签。

---

## 2. 把函数当参数传递 — 高阶函数

既然函数是对象，那它当然可以作为另一个函数的**参数**：

```python
def apply_twice(func, value):
    """对 value 连续调用 func 两次"""
    return func(func(value))

def double(x):
    return x * 2

result = apply_twice(double, 10)
print(result)  # 40 → 因为 double(double(10)) = double(20) = 40
```

函数还能作为**返回值**返回：

```python
def make_multiplier(factor):
    def multiply(x):
        return x * factor
    return multiply   # ← 返回内部函数本身，而不是调用它!

times_3 = make_multiplier(3)
print(times_3(7))  # 21
```

---

## 3. 闭包 — 内部函数"记住"了外面的世界

上面的 `multiply` 就是一个**闭包 (closure)**。它虽然是在 `make_multiplier` 内部定义的，但被返回后依然"记得"创建它时的 `factor` 值。

```python
def make_counter():
    count = 0                              # ← 外部函数的局部变量

    def counter():
        nonlocal count                     # ← 声明要修改外层变量
        count += 1
        return count

    return counter

c = make_counter()
print(c())  # 1
print(c())  # 2
print(c())  # 3
# count 变量活在 counter 的"记忆"里 — 这就是闭包!
```

可以直观验证闭包捕获了哪些变量：

```python
times_3 = make_multiplier(3)
print(times_3.__closure__)            # 闭包存在
print(times_3.__closure__[0].cell_contents)  # 3 ← 就是 factor!
```

---

## 4. 动手之前：❌ 不好的写法

假设你想给每个函数加上日志打印。最"朴素"的做法：

```python
# ❌ 方式 A：在每个函数里手动加 print
def add(a, b):
    print("[LOG] 开始执行 add")
    result = a + b
    print("[LOG] add 执行结束")
    return result

def subtract(a, b):
    print("[LOG] 开始执行 subtract")
    result = a - b
    print("[LOG] subtract 执行结束")
    return result
```

**问题很明显**：代码重复、难以维护、修改日志格式要改 N 处。

---

## 5. ✅ 装饰器 — 优雅地给函数"穿衣服"

装饰器的本质就是：**一个接受函数、返回新函数的高阶函数**。

### 5.1 手写版 — 不用 @ 语法糖，先理解本质

```python
def logger(func):                       # ① 接受一个函数
    def wrapper(*args, **kwargs):       # ② 返回一个新函数（闭包）
        print(f"[LOG] 开始执行 {func.__name__}")
        result = func(*args, **kwargs)  # ③ 在内部调用原函数
        print(f"[LOG] {func.__name__} 执行结束")
        return result                   # ④ 返回原函数的结果
    return wrapper

def add(a, b):
    return a + b

# 关键：手动"装饰"
add = logger(add)    # ← 把 add 传给 logger, 用返回的 wrapper 替换原来的 add

print(add(3, 5))
# 输出:
# [LOG] 开始执行 add
# [LOG] add 执行结束
# 8
```

### 5.2 @ 语法糖 — 让它好看一点

```python
@logger            # ← 等价于 add = logger(add)
def add(a, b):
    return a + b

@logger
def subtract(a, b):
    return a - b

print(add(3, 5))      # 自动带日志!
print(subract(8, 2))  # 自动带日志!
```

> 🍬 **`@decorator` 不是什么魔法**，它只是 `func = decorator(func)` 的语法糖。Python 解释器看到 `@logger`，就帮你把下一行定义的函数名重新绑定到装饰器的返回值上。

---

## 6. 带参数的装饰器 — 再包一层

如果想做 `@repeat(3)` 这种带参数的装饰器，需要在外面**再套一层函数**：

```python
def repeat(n):
    def actual_decorator(func):                # ← 这才是真正的装饰器
        def wrapper(*args, **kwargs):
            results = []
            for _ in range(n):
                results.append(func(*args, **kwargs))
            return results
        return wrapper
    return actual_decorator                    # ← repeat 返回一个装饰器

@repeat(3)
def say_hi(name):
    return f"你好, {name}"

print(say_hi("Alice"))
# ['你好, Alice', '你好, Alice', '你好, Alice']
```

三层结构拆解：

| 层级 | 它是什么 | 什么时候执行 |
|------|---------|-------------|
| `repeat(n)` | 装饰器工厂 | `@repeat(3)` 时立即调用 |
| `actual_decorator` | 真正的装饰器 | 紧接着，接收 `say_hi` |
| `wrapper` | 替换后的函数 | 每次调用 `say_hi("Alice")` 时 |

等效手动写法：`say_hi = repeat(3)(say_hi)`

---

## 7. 保留函数元信息 — `@functools.wraps`

装饰器有一个小坑：被装饰后，函数的 `__name__` 和 `__doc__` 会变成 `wrapper` 的。

```python
# ❌ 没加 @wraps
def add(a, b):
    """返回两数之和"""
    return a + b

decorated_add = logger(add)
print(decorated_add.__name__)  # wrapper  ← 丢失了原名!
print(decorated_add.__doc__)   # None     ← 丢失了文档!

# ✅ 加上 @wraps
from functools import wraps

def logger(func):
    @wraps(func)               # ← 把 func 的元信息复制到 wrapper
    def wrapper(*args, **kwargs):
        print(f"[LOG] 开始执行 {func.__name__}")
        result = func(*args, **kwargs)
        print(f"[LOG] {func.__name__} 执行结束")
        return result
    return wrapper
```

> 🛡️ **好习惯**: 写装饰器时，永远加上 `@functools.wraps(func)`。

---

## 8. 总结

```
函数是对象 → 可以作为参数/返回值 → 闭包捕获外部变量
                                            ↓
                              装饰器 = 接受函数、返回函数的高阶函数
                                            ↓
                              @decorator = func = decorator(func)
                                            ↓
                              带参数装饰器 = 再包一层工厂函数
```

装饰器的核心应用场景：**日志、计时、权限检查、缓存、重试、注册**……几乎所有「横切关注点」都可以用装饰器优雅解决。

---

> 🎯 **恭喜!** 你已经理解了装饰器的全部基石。接下来动手写两个练习，巩固一下。
