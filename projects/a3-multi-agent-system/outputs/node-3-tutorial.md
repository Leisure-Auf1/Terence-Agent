# Node 3: 堆叠 · 描述符 · 框架实战

> **难度**: 攻坚  |  **预计阅读**: 20 分钟  |  **前置**: Node 1 & Node 2

---

## §3.1 装饰器堆叠 — 洋葱剥皮 🧅

多个 `@` 叠在一起的时候，最让我困惑的就是——谁先执行？来看：

```python
@A
@B
@C
def foo():
    pass
# 等价于: foo = A(B(C(foo)))
```

❌ **直觉误导**: 从上往下读，以为 A 先执行。
✅ **真相**: **从下往上应用，从上往下执行**。就像穿衣服——先穿最贴身的 C，再套 B，最后披上 A。别人看到你时，先看到 A（最外层）。

我写一个具体例子验证：

```python
def make_decorator(name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            print(f"{name} 进入")             # ① 进场
            result = func(*args, **kwargs)    # ② 调用内层
            print(f"{name} 退出")             # ③ 退场
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
    print("--- 核心执行 ---")

test()
# A 进入           ← 最外层先触发
# B 进入           ← 往里走
# C 进入           ← 最内层最后进入
# --- 核心执行 ---  ← 真正的函数
# C 退出           ← 最内层先退出
# B 退出           ← 往外走
# A 退出           ← 最外层最后退出
```

> 🧅 **洋葱剥皮**: 剥的时候从外到内（A→B→C），咬到核心，咀嚼完从内到外吐出来（C→B→A）。wrapper 套 wrapper，每一层都在进出时做自己的事情。

❌ **常见翻车**: 把 `@timer` 放在 `@retry` 里面——timer 只测单词调用，不算重试时间。
✅ **正确姿势**: `@timer` 在最外层 → 它包裹 `@retry` → timer 测量的就是"包含所有重试的总耗时"。

```python
@timer                          # ③ 最外层：计时整个调用（含重试）
@retry(max_tries=3, delay=1)    # ② 中间层：失败就重试
def fetch_data():
    time.sleep(0.1)
    return {"status": "ok"}
```

**本节新概念 (3个)**: 堆叠语法/等价转换 · 下→上应用 + 上→下执行 · 洋葱剥皮模型

---

## §3.2 描述符入门 — `__get__` 的本质

描述符不是什么高深魔法——一个对象只要定义了 `__get__`，它就是描述符。Python 通过这套协议来"拦截"属性访问。

❌ **不用描述符**: 每个属性手动写 getter/setter 调用，啰嗦。
✅ **用描述符**: 属性访问自动触发 `__get__`，透明拦截。

先看最简描述符长什么样：

```python
class UpperCase:
    """把值自动转大写"""
    def __get__(self, instance, owner):
        # instance: 哪个实例访问的（p）
        # owner:    描述符所在的类（Person）
        return self._value.upper() if hasattr(self, '_value') else ''

    def __set__(self, instance, value):
        self._value = value

class Person:
    name = UpperCase()    # ← name 是一个描述符对象

p = Person()
p.name = "alice"          # 触发 UpperCase.__set__
print(p.name)             # 触发 UpperCase.__get__ → "ALICE"
```

Python 访问属性时按这条链查找——优先级从上到下：

```
① 数据描述符（有 __get__ + __set__/__delete__）  ← 最高优先级
② 实例的 __dict__                               ← 普通实例属性
③ 非数据描述符（只有 __get__）                    ← @classmethod 等
④ 类的 __dict__                                 ← 类属性
```

❌ **把数据存描述符自身的 `_value`**: 多个实例共享同一个描述符对象，后写的会覆盖前面的——数据全串了。
✅ **正确做法**: 数据存在 `instance.__dict__` 里，描述符只负责拦截和转换。

```python
class UpperCase:
    def __init__(self, attr_name):
        self.attr_name = attr_name         # 存属性名，不存值

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.attr_name, '').upper()

    def __set__(self, instance, value):
        instance.__dict__[self.attr_name] = value  # 存到实例上
```

**本节新概念 (3个)**: 描述符协议(__get__) · 数据描述符 vs 非数据描述符 · 属性查找优先级链

---

## §3.3 手写 @property — 自动门 🚪

你走进商场，门自动感应打开——你没推门，但它开了。`@property` 就是这个感觉：你写 `c.area`，看起来像读属性，实际上 Python 替你调了 `area()` 方法。

❌ **手动 getter**: `c.get_area()` — 每次都要写括号，一看就是"函数调用"。
✅ **@property**: `c.area` — 像普通属性一样自然，但其实背后跑了逻辑。

Python 内置的 `property` 就是数据描述符。我自己实现一个简化版：

```python
class custom_property:
    """简化版 @property——自动门"""
    def __init__(self, fget=None, fset=None):
        self.fget = fget          # 读的时候调这个
        self.fset = fset          # 写的时候调这个

    def __get__(self, instance, owner):
        if instance is None:             # 类访问 → 返回描述符本身
            return self
        if self.fget is None:
            raise AttributeError("不可读")
        return self.fget(instance)       # 实例访问 → 推自动门

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("只读属性，不可设置")
        self.fset(instance, value)

    def setter(self, func):
        """返回一个新的 custom_property，带上 setter"""
        return type(self)(self.fget, func)   # 不可变——新建，不改旧
```

用起来跟内置 `@property` 一模一样：

```python
class User:
    def __init__(self, name):
        self._name = name

    @custom_property
    def name(self):                    # ① name = custom_property(name_getter)
        return self._name

    @name.setter                       # ② name = custom_property(getter, setter)
    def name(self, value):             #    返回新实例，fget 和 fset 都配齐了
        if not value.strip():
            raise ValueError("名字不能为空")
        self._name = value.strip()

u = User("Alice")
print(u.name)    # Alice — 像属性一样自然
u.name = "Bob"   # 触发校验
# u.name = ""    # ValueError: 名字不能为空
```

> 🚪 **自动门**: `c.area` 是走过去的动作（属性访问），门感应到你自动打开（`__get__` 调 fget），你不用伸手推（不用写括号）。`setter` 返回全新实例——老的门不拆，新门装上去。这是不可变设计，避免改了正在用的描述符出诡异 bug。

**本节新概念 (3个)**: property 是数据描述符 · __get__/__set__ 协作实现自动门 · setter 不可变返回新实例

---

## §3.4 Flask 路由 — 门牌号 📍

前面学的装饰器都是「包装模式」——wrapper 裹住原函数加行为。Flask 的 `@app.route("/hello")` 不走这条路——它是**注册模式**：装饰器只把函数记录到路由表，原函数纹丝不动。

❌ **包装模式**: wrapper 替换原函数，调用 wrapper 就是调用装饰过的版本。
✅ **注册模式**: 装饰器回头就走，函数还是那个函数——只是地址被登记到了路由表。

我把 Flask 路由的核心理念浓缩成一个 20 行的 MiniFlask：

```python
class MiniFlask:
    def __init__(self):
        self._routes = {}               # 路由表: {门牌号: 函数}

    def route(self, path):
        """路由注册——给函数家门口钉门牌号"""
        def decorator(func):
            self._routes[path] = func   # ① 登记: "/hello" → hello 函数
            return func                 # ② 不包装！原样返回
        return decorator

    def handle(self, path):
        """有人敲门牌号——找到对应函数执行"""
        handler = self._routes.get(path)
        if handler:
            return handler()
        return "404 — 这个门牌号不存在"

app = MiniFlask()

@app.route("/hello")           # ← 给 hello 家门口钉门牌号 "/hello"
def hello():
    return "你好，世界！"

@app.route("/about")
def about():
    return "关于我们"

print(app.handle("/hello"))    # 你好，世界！
print(app.handle("/about"))    # 关于我们
print(app.handle("/secret"))   # 404 — 这个门牌号不存在
```

> 📍 **门牌号**: 每个 `@app.route("/xxx")` 就是给函数家门口钉一块门牌。请求来了，框架敲对应的门牌号，函数出来应答。装饰器在这里不是"给函数穿衣服"，而是"给函数分配地址"。

❌ **误以为装饰器一定要包装**: 如果你以为装饰器必须 `return wrapper`，看到 Flask 的 `return func` 就会懵。
✅ **装饰器 = 函数加工厂**: 加工方式不限于"包裹"——注册、标记、收集……都是合法操作。

**本节新概念 (3个)**: 注册模式 vs 包装模式 · 路由表(门牌号→函数) · 装饰器不包装只登记

---

## §3.5 权限装饰器 — 前置拦截 🛡️

Web 开发里，权限校验是最自然的装饰器场景——在函数执行前设一道关卡，不符合条件就直接挡回去。

```python
import functools

current_user = {"name": "Alice", "role": "editor"}

def require_role(role):
    """只有特定角色才能进门"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if current_user.get("role") != role:       # ① 前置检查
                raise PermissionError(f"需要 {role} 权限！")
            return func(*args, **kwargs)               # ② 放行
        return wrapper
    return decorator

@require_role("admin")
def delete_all_users():
    return "所有用户已删除！"

@require_role("editor")
def edit_article(article_id):
    return f"文章 {article_id} 编辑完成"

# delete_all_users()   # ❌ PermissionError — Alice 是 editor 不是 admin
print(edit_article(42))  # ✅ 文章 42 编辑完成
```

❌ **手动在每个函数里写权限检查**: `if role != "admin": raise...` 散落各处，改角色名要全局搜索替换。
✅ **用装饰器守卫**: 一行 `@require_role("admin")` 挂上去，守卫逻辑集中管理——改一处生效全局。

更进一步——多个权限装饰器可以堆叠（回到 §3.1 的洋葱！）：

```python
def log_access(func):
    """记录每次访问"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"[AUDIT] {current_user['name']} 调用 {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_access                    # ② 外层: 记录日志
@require_role("admin")         # ① 内层: 先查权限，不通过日志也不记
def delete_all_users():
    return "所有用户已删除！"
```

洋葱堆叠的意义此刻完全体现：**内层守卫拦截 → 外层日志才能记录合法访问**。顺序反过来，非法请求也会被记下来——审计日志就脏了。

**本节新概念 (3个)**: 前置拦截模式 · 权限校验闭包 · 守卫+日志洋葱堆叠

---

## 速查卡

| 来源 | 核心概念（一句话） |
|------|-------------------|
| **Node 1** | 函数是对象→闭包(隐形背包)→装饰器=穿衣服→@语法糖→三层套娃工厂→@wraps 身份证 |
| **Node 2** | 带参装饰器=工厂→装饰器→wrapper 三层；类装饰器用 `__init__`+`__call__` 管状态；`@retry`/`@cache_ttl` 模板复用 |
| **Node 3（本章）** | 堆叠=洋葱剥皮(下→上应用,上→下执行)；描述符=属性拦截器；@property=自动门；Flask 路由=门牌号(注册模式)；权限装饰器=前置守卫 |
