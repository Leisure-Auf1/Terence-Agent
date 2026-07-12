# Node 3: 装饰器堆叠、property 原理与框架实战

> **难度**: 攻坚  |  **预计阅读**: 25 分钟  |  **前置**: Node 1 & Node 2（掌握无参/带参装饰器）

---

## 1. 回顾 — 你现在站在哪里

经过 Node 1 和 Node 2，你已经掌握了：

| 能力 | 你会写 |
|------|--------|
| 无参装饰器 | `@timer` — 两层结构，接收函数返回 wrapper |
| 带参装饰器 | `@retry(max_tries=3)` — 三层结构，参数→装饰器→wrapper |
| functools.wraps | 保留 `__name__`, `__doc__` 等元信息 |
| 高级模式 | 类装饰器（`__call__`）, 缓存（`cache_ttl`） |

但光会写单个装饰器还不够——现实中你需要的是**多个装饰器协同工作**，以及理解那些「看起来像魔法」的内置装饰器（`@property`、`@classmethod`）到底是怎么运作的。

---

## 2. 装饰器堆叠 — 洋葱模型 🧅

### 2.1 堆叠语法

最让人困惑的事情来了：多个 `@` 叠在一起时，到底谁先执行？

```python
@A
@B
@C
def foo():
    pass

# 等价于: foo = A(B(C(foo)))
```

> 💡 **关键洞察**: 多个装饰器堆叠时，**从下往上应用，从上往下执行**。就像穿衣服——先穿最贴身的 C，再穿 B，最后披上 A。出门时，别人先看到的是 A（最外层）。

### 2.2 拆解执行顺序

用一个具体例子来验证：

```python
def make_decorator(name):
    """工厂函数：生产一个带名字的装饰器"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"{name} 开始")          # ① 进场
            result = func(*args, **kwargs)  # ② 调用内层
            print(f"{name} 结束")          # ③ 退场
            return result
        return wrapper
    return decorator

A = make_decorator("A")
B = make_decorator("B")
C = make_decorator("C")

@A
@B
@C
def test():
    print("--- 执行原始函数 ---")

test()
# 输出:
# A 开始           ← 最外层先入
# B 开始           ← 往里走
# C 开始           ← 最内层最后进入
# --- 执行原始函数 ---   ← 真正的函数在这里
# C 结束           ← 最内层先出
# B 结束           ← 往外走
# A 结束           ← 最外层最后出
```

### 2.3 可视化：洋葱模型

```
         ┌─────────────────────────────┐
         │         A 的 wrapper         │  ← 最外层，最先「接客」
         │  ┌───────────────────────┐  │
         │  │     B 的 wrapper       │  │
         │  │  ┌─────────────────┐  │  │
         │  │  │  C 的 wrapper   │  │  │  ← 最内层，最靠近原始函数
         │  │  │                 │  │  │
         │  │  │   test() 原函数  │  │  │
         │  │  │                 │  │  │
         │  │  └─────────────────┘  │  │
         │  └───────────────────────┘  │
         └─────────────────────────────┘

调用流程: A 开始 → B 开始 → C 开始 → test() → C 结束 → B 结束 → A 结束
```

> 🧅 **记忆技巧**: 洋葱！剥开时从外到内（A→B→C），咬到核心（原始函数），咀嚼完从内到外（C→B→A）。

### 2.4 实战堆叠：timer + retry + cache

```python
import time
import functools

# ===== 三个装饰器 =====

def timer(func):
    """计时装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"[TIMER] {func.__name__} 耗时 {elapsed:.4f}s")
        return result
    return wrapper

def retry(max_tries=3, delay=1):
    """重试装饰器（带参）"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_tries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exc = e
                    if attempt < max_tries - 1:
                        print(f"[RETRY] 第 {attempt+1} 次失败，{delay}s 后重试...")
                        time.sleep(delay)
            raise last_exc
        return wrapper
    return decorator

# ===== 堆叠使用 =====

@timer                       # ③ 最后应用：计时整个调用
@retry(max_tries=3, delay=1) # ② 中间层：失败就重试
def fetch_data(simulate_fail=False):
    """模拟网络请求"""
    if simulate_fail:
        raise ConnectionError("网络超时")
    time.sleep(0.1)           # 模拟网络延迟
    return {"status": "ok"}

# 执行流程:
# 1. timer 开始计时
# 2.   retry 开始管理重试
# 3.     fetch_data 真正执行
# 4.   如果异常，retry 捕获并重试
# 5. timer 停止计时（包含所有重试时间）

print(fetch_data(False))
# [TIMER] fetch_data 耗时 0.1002s
# {'status': 'ok'}
```

> ⚠️ **陷阱**: 装饰器堆叠的顺序非常讲究！如果你把 `@timer` 放在 `@retry` 里面，timer 只会测量单次调用的时间（不包括重试），通常不是你想要的效果。

---

## 3. @property 的底层原理 — 描述符协议

### 3.1 你不是在调用函数，你是在访问属性

```python
class Circle:
    def __init__(self, radius):
        self._radius = radius

    @property
    def area(self):
        return 3.14159 * self._radius ** 2

c = Circle(5)
print(c.area)      # 78.53975 — 注意！没有括号 c.area 不是 c.area()
# c.area = 100     # AttributeError — 只读！
```

`@property` 把一个方法变成了「属性」。你访问 `c.area` 时，Python 悄悄调用了 `area(self)`。这个魔法背后的机制叫做**描述符协议（Descriptor Protocol）**。

### 3.2 描述符协议：三步规则

Python 在访问对象的属性时，按以下优先级查找：

```
1. 数据描述符（有 __get__ + __set__）   ← @property 属于这种
2. 实例的 __dict__                     ← 普通属性
3. 非数据描述符（只有 __get__）          ← @classmethod / @staticmethod
4. 类的 __dict__                       ← 类属性
5. 如果还没找到 → __getattr__
```

一个对象只要定义了 `__get__` 方法，它就是**描述符**。我们来看一个最简描述符：

```python
class UpperCase:
    """将属性值自动转为大写"""
    def __get__(self, instance, owner):
        return self._value.upper() if hasattr(self, '_value') else ''

    def __set__(self, instance, value):
        self._value = value

class Person:
    name = UpperCase()   # ← name 是一个描述符

p = Person()
p.name = "alice"         # 触发 UpperCase.__set__(self=name_desc, instance=p, value='alice')
print(p.name)            # 触发 UpperCase.__get__(self=name_desc, instance=p, owner=Person)
# 输出: ALICE
```

> 💡 **三个参数的含义**:
> - `self`: 描述符实例本身（上例中的 `name` 这个 `UpperCase` 实例）
> - `instance`: 拥有描述符的实例（上例中的 `p`），类访问时为 `None`
> - `owner`: 描述符所在的类（上例中的 `Person`）

### 3.3 @property 就是用描述符实现的

Python 内置的 `property` 本质上是一个**数据描述符类**：

```python
class property:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        self.__doc__ = doc

    def __get__(self, instance, owner):
        if instance is None:
            return self           # 类访问 → 返回 property 本身
        return self.fget(instance)  # 实例访问 → 调用 getter

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)
```

现在你一眼就能看懂 `@property` 的语法糖背后发生了什么：

```python
class Temperature:
    @property                    # ① celsius = property(celsius)
    def celsius(self):
        return self._celsius

    @celsius.setter              # ② celsius = property(celsius_getter).setter(celsius_setter)
    def celsius(self, value):    #    → 返回一个新的 property 实例，既带 getter 又有 setter
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度！")
        self._celsius = value
```

### 3.4 自己实现 custom_property

理解了原理之后，自己写一个 `custom_property` 就很简单了：

```python
class custom_property:
    """自己实现的简化版 @property"""
    def __init__(self, fget=None, fset=None):
        self.fget = fget
        self.fset = fset

    def __get__(self, instance, owner):
        if instance is None:
            return self                    # 类访问 → 返回描述符本身
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(instance)         # 实例访问 → 调用 getter

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)         # 调用 setter

    def setter(self, func):
        """返回一个新的 custom_property，带上 setter"""
        return type(self)(self.fget, func)  # 复制 fget，添加 fset


# ===== 使用 =====
class User:
    def __init__(self, name):
        self._name = name

    @custom_property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        if not value.strip():
            raise ValueError("名字不能为空")
        self._name = value.strip()

u = User("Alice")
print(u.name)     # Alice
u.name = "Bob"
print(u.name)     # Bob
# u.name = ""     # ValueError: 名字不能为空
```

> 🎯 **关键**: `setter` 方法没有修改当前的 `custom_property` 实例——它创建了一个**新的**实例，包含原 getter 加上新 setter。这是不可变设计模式，避免修改正在使用的描述符导致奇怪的 bug。

---

## 4. @classmethod 与 @staticmethod 的原理

### 4.1 它们也是描述符

`@classmethod` 和 `@staticmethod` 不是黑魔法——它们也是描述符：

```python
# @classmethod 的简化实现
class classmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # 无论 instance 是什么，都绑定到 owner 类上
        def bound_method(*args, **kwargs):
            return self.func(owner, *args, **kwargs)
        return bound_method

# @staticmethod 的简化实现
class staticmethod:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        # 什么都不绑定，直接返回原函数
        return self.func
```

> 💡 **总结**: `classmethod` 的 `__get__` 返回一个闭包，把类作为第一个参数传入；`staticmethod` 的 `__get__` 直接返回原函数，什么都不绑。

### 4.2 三者对比

| 装饰器 | 第一个参数 | 描述符类型 | 可以访问实例属性？ |
|--------|-----------|-----------|-----------------|
| 普通方法 | `self`（实例） | 函数描述符 | ✅ |
| `@classmethod` | `cls`（类） | 非数据描述符 | ❌ 只能访问类属性 |
| `@staticmethod` | 无特殊参数 | 非数据描述符 | ❌ 不绑任何东西 |
| `@property` | `self`（实例） | 数据描述符 | ✅ 但不能直接调用 |

---

## 5. 装饰器在框架中的实战应用

### 5.1 Flask 路由 — 最优雅的装饰器用法

Flask 的 `@app.route('/path')` 是装饰器在 Web 框架中的经典应用：

```python
# Flask 路由装饰器的简化实现
class MiniFlask:
    def __init__(self):
        self._routes = {}          # 路由表: {path: handler_func}

    def route(self, path):
        """路由注册装饰器"""
        def decorator(func):
            self._routes[path] = func   # ① 注册函数到路由表
            return func                 # ② 返回原函数，不做任何包装
        return decorator

    def handle_request(self, path):
        """模拟处理 HTTP 请求"""
        handler = self._routes.get(path)
        if handler:
            return handler()
        return "404 Not Found"


app = MiniFlask()

@app.route("/hello")
def hello():
    return "Hello, World!"

@app.route("/about")
def about():
    return "About Us"

print(app.handle_request("/hello"))   # Hello, World!
print(app.handle_request("/about"))   # About Us
print(app.handle_request("/404"))     # 404 Not Found
```

> 💡 **注意**: `@app.route` 的装饰器**没有包装**原函数，它只是把函数注册到了路由表中，然后原封不动返回。这是装饰器的另一种用法———**注册模式**，而不是包装模式。

### 5.2 权限校验装饰器

Web 开发中，权限校验用装饰器最自然不过：

```python
import functools

# 模拟当前用户信息
current_user = {"name": "Alice", "role": "editor"}

def require_role(role):
    """要求用户具备特定角色"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.get("role") != role:
                raise PermissionError(f"需要 {role} 权限，当前用户角色: {current_user.get('role')}")
            return func(*args, **kwargs)
        return wrapper
    return decorator

@require_role("admin")
def delete_all_users():
    return "所有用户已删除！"

@require_role("editor")
def edit_article(article_id):
    return f"文章 {article_id} 编辑完成"

# delete_all_users()   # PermissionError: 需要 admin 权限
print(edit_article(42))  # 文章 42 编辑完成
```

### 5.3 事务装饰器

数据库操作中，`@transactional` 装饰器可以自动管理事务：

```python
import functools

class Database:
    """模拟数据库"""
    def __init__(self):
        self._committed = False
        self._rolled_back = False

    def begin(self):
        print("[DB] 事务开始")

    def commit(self):
        self._committed = True
        print("[DB] 事务已提交")

    def rollback(self):
        self._rolled_back = True
        print("[DB] 事务已回滚")


db = Database()

def transactional(func):
    """事务装饰器 — 自动 begin/commit/rollback"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        db.begin()                    # ① 开启事务
        try:
            result = func(*args, **kwargs)
            db.commit()               # ② 成功 → 提交
            return result
        except Exception:
            db.rollback()             # ③ 失败 → 回滚
            raise                     # ④ 重新抛出异常
    return wrapper


@transactional
def transfer_money(from_user, to_user, amount):
    if amount <= 0:
        raise ValueError("转账金额必须大于 0")
    print(f"转账 {amount} 元: {from_user} → {to_user}")
    return "success"

print(transfer_money("Alice", "Bob", 100))
# [DB] 事务开始
# 转账 100 元: Alice → Bob
# [DB] 事务已提交
# success
```

### 5.4 输入校验 + 类型转换装饰器

```python
def validate_types(**type_map):
    """运行时类型校验装饰器"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # 校验位置参数
            params = list(func.__code__.co_varnames[:func.__code__.co_argcount])
            for i, (param_name, value) in enumerate(zip(params, args)):
                expected_type = type_map.get(param_name)
                if expected_type and not isinstance(value, expected_type):
                    raise TypeError(f"{param_name} 期望 {expected_type.__name__}, 实际 {type(value).__name__}")
            # 校验关键字参数
            for name, value in kwargs.items():
                expected_type = type_map.get(name)
                if expected_type and not isinstance(value, expected_type):
                    raise TypeError(f"{name} 期望 {expected_type.__name__}, 实际 {type(value).__name__}")
            return func(*args, **kwargs)
        return wrapper
    return decorator


@validate_types(a=int, b=int)
def add(a, b):
    return a + b

print(add(1, 2))      # 3
# print(add(1, "2"))  # TypeError: b 期望 int, 实际 str
```

---

## 6. 总结 — 装饰器能力的三个层次

```
┌──────────────────────────────────────────────────┐
│              装饰器能力金字塔                        │
├──────────────────────────────────────────────────┤
│                                                  │
│  L3: 设计模式                                     │
│      ├── 路由注册 (Flask @app.route)              │
│      ├── 权限校验 (@require_role)                 │
│      ├── 事务管理 (@transactional)                │
│      └── 类型检查 (@validate_types)              │
│                                                  │
│  L2: 底层原理                                     │
│      ├── 描述符协议 (__get__ / __set__)           │
│      ├── @property 实现                           │
│      └── @classmethod / @staticmethod            │
│                                                  │
│  L1: 基础应用 (Node 1 + Node 2)                   │
│      ├── 无参装饰器 (@timer, @logger)             │
│      ├── 带参装饰器 (@retry(n), @cache_ttl(s))    │
│      └── 堆叠组合                                  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 🎯 核心要点

1. **堆叠顺序**: `@A @B @C` = `A(B(C(f)))` — 从下往上应用，从上往下执行
2. **洋葱模型**: 调用时从外到内，返回时从内到外 — 就像剥洋葱
3. **描述符协议**: `@property` 不是魔法，是 `__get__` 和 `__set__` 的优雅封装
4. **注册模式**: 装饰器不一定要包装函数——Flask 路由只是注册，原函数不变
5. **实战应用**: 路由 → 权限 → 事务 → 校验，装饰器无处不在

---

> 📝 **Node 3 练习指向**: 接下来你将手写 `custom_property`（实现描述符协议）和装饰器堆叠实验（验证洋葱模型）。这两道题是本课程最难的核心关卡，攻克后你就真正「看懂了」所有装饰器。
