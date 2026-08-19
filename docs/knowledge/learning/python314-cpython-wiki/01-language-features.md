---
id: python314-cpython-wiki-01-language-features
title: "Python 3.14 语言新特性"
source: "https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html, https://peps.python.org/pep-0758/, https://peps.python.org/pep-0765/, https://peps.python.org/pep-0649/, https://peps.python.org/pep-0749/, https://peps.python.org/pep-0750/"
date: "2026-08-19"
category: "learning"
tags: ["python314", "t-strings", "annotations", "except", "finally", "pep", "language-features", "typing", "types", "union"]
---

# Python 3.14 语言新特性

本章介绍 Python 3.14 的语言层面变更——包括语法变化、类型注解机制重构、模板字符串等。这些变化直接影响你写每一行 Python 代码的方式。

---

## 1. PEP 758：无括号 except 和 except* 表达式

### 背景

Python 的 `try/except` 语法从 Python 2 时代起就要求异常类型必须用括号包裹多个类型：

```python
# Python 3.13 及之前，必须使用括号
try:
    risky_call()
except (ValueError, TypeError):  # ← 括号是必须的
    handle_error()
```

这与 Python 的其他语法不一致——例如 `return a, b` 和 `import os, sys` 都不需要括号。

### 新语法

PEP 758 允许在 `except` 和 `except*` 中省略括号，使用元组展开语法直接列出多个异常类型：

```python
# Python 3.14 新写法：无需括号
try:
    risky_call()
except ValueError, TypeError:  # ← 注意这里是逗号，不是 as！
    handle_error()

# except* 同样支持
try:
    async_risky_call()
except* ValueError, TypeError:
    handle_errors()
```

> ⚠️ **语法注意**：`except ValueError, TypeError:` 中的逗号是分隔多个异常类型，不是给异常起别名。如果需要同时捕获多个异常**并**绑定到变量，仍然使用括号形式：
>
> ```python
> try:
>     risky_call()
> except (ValueError, TypeError) as e:  # 多个类型+as，需要括号
>     print(f"错误: {e}")
> ```

### 单异常的 as 绑定

单异常的 `as` 绑定仍然与之前一致：

```python
try:
    risky_call()
except ValueError as e:  # 单个异常+as，无需括号
    print(e)
```

### 代码示例：新旧对比

```python
# === 旧写法 ===
try:
    data = json.loads(raw)
except (json.JSONDecodeError, KeyError, TypeError) as e:
    logger.error(f"解析失败: {e}")
    data = None

# === 新写法（无括号，多个异常类型）===
try:
    data = json.loads(raw)
except json.JSONDecodeError, KeyError, TypeError:
    data = None

# 如果需要 as e，仍需括号
try:
    data = json.loads(raw)
except (json.JSONDecodeError, KeyError, TypeError) as e:
    logger.error(f"解析失败: {e}")
    data = None
```

### 源码实现

此语法变更涉及 Python 语法解析器的修改。核心改动在 [Grammar/python.gram](https://github.com/python/cpython/blob/v3.14.0/Grammar/python.gram) 中的 `except_clause` 规则，以及 [Parser/parser.c](https://github.com/python/cpython/blob/v3.14.0/Parser/parser.c) 中的 AST 构建逻辑。

---

## 2. PEP 765：finally 块中的控制流警告

### 问题背景

`finally` 块中的 `return`、`break`、`continue` 语句会**静默吞掉**异常，这是 Python 长期以来一个臭名昭著的"暗坑"：

```python
def problematic():
    try:
        raise ValueError("这个异常会被吞掉！")
    finally:
        return 42  # ← finally 中的 return 吞掉了异常

result = problematic()  # 返回 42，异常消失了！
print(result)  # 42，没有任何异常
```

同样的问题也存在于 `break` 和 `continue`：

```python
for i in range(3):
    try:
        if i == 1:
            raise ValueError("异常")
    finally:
        if i == 1:
            break  # ← break 吞掉异常，循环安静退出
```

### 新行为

Python 3.14 中，`finally` 块中使用 `return`、`break`、`continue` 会产生 `SyntaxWarning`：

```
SyntaxWarning: 'return' in 'finally' may swallow exceptions
SyntaxWarning: 'break' in 'finally' may swallow exceptions
SyntaxWarning: 'continue' in 'finally' may swallow exceptions
```

### 修复方法

如果你确实需要在 finally 中返回，有两种清晰的方式：

**方式1：将 return 移到 finally 外面（推荐）**

```python
def fixed():
    try:
        risky_call()
        return success_value
    except ValueError:
        return fallback_value
    finally:
        cleanup()  # cleanup 中没有 return/break/continue
```

**方式2：使用标志变量明确意图**

```python
def explicit():
    result = None
    try:
        result = risky_call()
    finally:
        cleanup()
    return result
```

### 为什么不直接报错？

PEP 765 选择了 `SyntaxWarning` 而非 `SyntaxError`，因为：
1. 向后兼容——大量现有代码（包括标准库）中存在这种模式
2. 在极少数场景下这确实是有意为之
3. Python 的弃用周期通常先警告再报错

### 代码示例

```python
# ❌ 3.14 中会产生 SyntaxWarning
def bad_example():
    try:
        raise ValueError("oops")
    finally:
        return "swallowed"  # SyntaxWarning!

# ✅ 正确写法：将 return 放在 finally 外面
def good_example():
    try:
        raise ValueError("oops")
    except ValueError as e:
        return f"caught: {e}"
    finally:
        cleanup_resources()  # 只做清理，不做控制流跳转
```

---

## 3. PEP 649 / PEP 749：延迟注解求值

### 问题：注解求值的困境

Python 的类型注解自 PEP 484（3.0）引入以来，一直存在一个根本矛盾：

1. **前向引用问题**：类型注解在类定义体内无法引用尚未定义的类名
2. **运行时开销**：注解在定义时立即求值，对于大型项目有显著开销
3. **`from __future__ import annotations` 的局限**：PEP 563 将注解转为字符串，但破坏了运行时反射（无法用 `typing.get_type_hints()` 获取实际类型对象）

```python
# === 前向引用的经典问题 ===
class Node:
    def __init__(self, next: Node | None = None):  # ❌ NameError: Node 还未定义
        self.next = next
```

PEP 563 的解决方案（`from __future__ import annotations`）将所有注解转为字符串：

```python
from __future__ import annotations  # 所有注解变成字符串

class Node:
    def __init__(self, next: Node | None = None):  # 现在可以了，但运行时是字符串
        self.next = next

Node.__init__.__annotations__  # {'next': 'Node | None'}  ← 字符串，不是类型对象！
```

这导致：`typing.get_type_hints()` 必须手动解析字符串，而直接访问 `__annotations__` 得到的是字符串而非真实类型，引发了大量运行时问题。

### PEP 649 的解决方案：延迟注解

PEP 649 引入了一种全新的注解求值策略：**注解定义时不立即求值，而是存储为特殊的"注解值"对象，在需要时按需求值并缓存**。

核心变化：
- 注解存储为 `types.AnnotationValue` 描述符对象，而非直接求值
- 首次访问时惰性求值（lazy evaluation）
- 求值结果会被缓存
- 前向引用自然工作——求值发生在模块完全加载后
- `__annotations__` 在普通访问时返回已求值的真实类型对象

```python
# Python 3.14：不需要 __future__ import，前向引用自然工作
class Node:
    def __init__(self, next: Node | None = None):  # ✅ 直接工作！
        self.next = next

# 首次访问 __annotations__ 时触发求值
print(Node.__init__.__annotations__)
# {'next': Node | None}  ← 真实类型对象，不是字符串！
```

### PEP 749：annotationlib 模块与三种格式

PEP 749 在 PEP 649 的基础上，引入了 `annotationlib` 模块，提供三种注解格式：

| 格式 | 说明 | 适用场景 |
|------|------|---------|
| `annotationlib.Format.VALUE` | 已求值的真实类型对象（默认） | 运行时类型检查、序列化 |
| `annotationlib.Format.FORWARDREF` | `ForwardRef` 对象（含已解析的引用） | 需要延迟求值但又要处理前向引用 |
| `annotationlib.Format.STRING` | 字符串形式（类似 PEP 563 行为） | 代码生成、静态分析工具 |

```python
import annotationlib
from annotationlib import Format, get_annotations

class MyClass:
    value: int
    name: str
    ref: MyClass | None  # 前向引用

# 默认格式 (VALUE)：返回已求值的类型对象
ann = get_annotations(MyClass)
# {'value': int, 'name': str, 'ref': MyClass | None}

# STRING 格式：返回字符串（兼容 PEP 563 行为）
ann_str = get_annotations(MyClass, format=Format.STRING)
# {'value': 'int', 'name': 'str', 'ref': 'MyClass | None'}

# FORWARDREF 格式：返回 ForwardRef 对象
ann_fwd = get_annotations(MyClass, format=Format.FORWARDREF)
# {'value': ForwardRef('int'), 'name': ForwardRef('str'), 'ref': ForwardRef('MyClass | None')}
```

### `from __future__ import annotations` 的弃用路径

随着 PEP 649 的实现，PEP 563 的 `from __future__ import annotations` 在 Python 3.14 中开始**软弃用**（Soft Deprecation）：

- 在 3.14 中使用不会产生警告，但官方推荐迁移
- 未来版本（预计 3.15 或 3.16）会产生 `DeprecationWarning`
- 最终将被完全移除

**迁移策略**：直接删除 `from __future__ import annotations` 这一行即可。PEP 649 的延迟求值已经提供了同样（或更好）的行为。

```python
# ❌ 旧方式（PEP 563，已弃用）
from __future__ import annotations

def process(items: list[Item]) -> Result:
    ...

# ✅ 新方式（PEP 649，直接工作）
def process(items: list[Item]) -> Result:
    ...
```

### `typing.get_type_hints()` 的变化

`typing.get_type_hints()` 在 3.14 中底层使用 `annotationlib.get_annotations()`，行为更加可靠：

```python
import typing

class Container:
    items: list[int]

# 在 3.14 中，get_type_hints 可靠地返回已求值的类型
hints = typing.get_type_hints(Container)
# {'items': list[int]}  ← 始终是真实类型对象
```

### 源码实现

延迟注解的核心实现位于：
- [Objects/annotationobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/annotationobject.c) — `AnnotationValue` 描述符实现
- [Python/compile.c](https://github.com/python/cpython/blob/v3.14.0/Python/compile.c) — 编译器生成注解代码对象
- [Lib/annotationlib.py](https://github.com/python/cpython/blob/v3.14.0/Lib/annotationlib.py) — `annotationlib` 标准库模块

---

## 3.5 类型系统重要变更

PEP 649/749 不仅重构了注解求值机制，还带来了以下类型系统层面的重要变更。

### `types.UnionType` 与 `typing.Union` 统一

Python 3.10 引入了 `X | Y` 联合类型语法（即 `types.UnionType`），但它与 `typing.Union[X, Y]` 是两个不同的类。Python 3.14 将二者**完全统一**：

```python
import typing
import types

# 3.14 中 types.UnionType 是 typing.Union 的别名
assert types.UnionType is typing.Union  # True!

# repr() 输出变化：Union[int, str] 现在显示为 int | str
print(typing.Union[int, str])  # int | str（旧版输出: typing.Union[int, str]）

# 可以用 isinstance 检查
assert isinstance(int | str, typing.Union)  # True!
```

**关键行为变化：**

| 行为 | Python 3.13 | Python 3.14 |
|------|------------|------------|
| `repr(Union[int, str])` | `typing.Union[int, str]` | `int \| str` |
| `isinstance(int \| str, Union)` | `TypeError` | `True` |
| `Union.__args__` | 包含嵌套 Union | 完全扁平化 |
| Union 缓存 | 同一参数组合缓存 | 不再缓存（性能优化） |
| 对 Union 对象设属性 | 可能 | 不可（frozen） |

**迁移注意：**
- 不要依赖 `typing._UnionGenericAlias` 这个内部类型
- 使用 `typing.get_origin()` 和 `typing.get_args()` 获取 Union 的来源和参数
- 测试中如果有对 `repr()` 输出的断言，需要更新

### `typing.TypeAliasType` 支持星号解包

`TypeAliasType` 是 PEP 695（Python 3.12）引入的新类型别名语法。Python 3.14 新增对星号解包的支持，可以在类型别名中解包 TypeVarTuple：

```python
from typing import TypeAliasType

# 3.14 支持在 TypeAliasType 中使用星号解包
# 这对于泛型变长元组类型特别有用
type Point[T, *Rest] = tuple[T, *Rest]  # 星号解包类型变量元组

# 也可以解包已有的类型别名
type IntPair = tuple[int, int]
type WithStr[*Ts] = tuple[str, *Ts]      # str 在前，后跟 Ts 展开
```

### `io.Reader` / `io.Writer` 新协议类型

Python 3.14 在 `io` 模块中新增了 `Reader` 和 `Writer` 协议类（Protocol），作为 `typing.IO`、`typing.TextIO`、`typing.BinaryIO` 这些"伪协议"的现代替代：

```python
from io import Reader, Writer

# Reader 协议：只需实现 read() 方法
def process_data(source: Reader[bytes]) -> bytes:
    return source.read()

# Writer 协议：只需实现 write() 方法
def write_data(dest: Writer[str], data: str) -> None:
    dest.write(data)

# 对比旧方式：typing.IO 过于宽泛（包含 read/write/seek/close 等全部方法）
# from typing import IO, TextIO, BinaryIO  # 3.14 软弃用方向
```

**为什么新增？**
- `typing.IO`/`TextIO`/`BinaryIO` 是类而非 `Protocol`，不符合结构子类型
- 它们强制要求实现 `seek()`、`tell()`、`close()` 等方法，但很多类只需要 `read()` 或 `write()`
- `io.Reader`/`io.Writer` 是真正的 `Protocol`，只要求核心方法，更符合 Python 鸭子类型精神

### `inspect` 增强：注解格式控制

配合 PEP 749 的 `annotationlib`，`inspect` 模块新增了注解格式控制能力：

```python
import inspect
from annotationlib import Format

def example(x: int, y: str) -> bool:
    return True

# inspect.signature() 新增 annotation_format 参数
sig_value = inspect.signature(example, annotation_format=Format.VALUE)
# 参数注解为真实类型对象：<class 'int'>, <class 'str'>

sig_string = inspect.signature(example, annotation_format=Format.STRING)
# 参数注解为字符串形式：'int', 'str'

# Signature.format() 新增 unquote_annotations 参数
print(sig_value.format(unquote_annotations=True))
# 字符串注解显示时不包裹引号，更易读

# inspect.ispackage() 新增函数
import inspect
import os, json, concurrent
print(inspect.ispackage(os))         # False（模块）
print(inspect.ispackage(json))       # False（模块）
print(inspect.ispackage(concurrent)) # True（命名空间包）
```

---

## 4. PEP 750：t-strings 模板字符串

t-strings（Template Strings）是自 Python 3.6 引入 f-strings 以来最重要的字符串语法扩展。

### 核心区别：f-strings vs t-strings

| 特性 | f-strings | t-strings |
|------|-----------|-----------|
| **前缀** | `f"..."` / `f'...'` | `t"..."` / `t'...'` |
| **求值时机** | 立即求值，返回字符串 | 返回 `Template` 对象，延迟求值 |
| **结果类型** | `str` | `string.templatelib.Template` |
| **插值访问** | 直接拼接为字符串 | 可以逐段访问静态文本和插值表达式 |
| **安全性** | 容易产生 SQL 注入等问题 | 可自定义转义/验证逻辑 |
| **用途** | 普通字符串格式化 | 安全模板（SQL/HTML/Shell）、DSL、代码生成 |

### 基本用法

```python
from string.templatelib import Template

# t-string 创建 Template 对象
name = "World"
t = t"Hello, {name}!"

print(type(t))  # <class 'string.templatelib.Template'>
print(str(t))   # "Hello, World!" — 转换为字符串时求值
```

### Template 对象结构

`Template` 对象是可迭代的，每个元素要么是静态字符串，要么是 `Interpolation` 对象：

```python
name = "Python"
version = 3.14
t = t"Welcome to {name} {version}!"

for part in t:
    print(repr(part))
# 'Welcome to '
# Interpolation(value='Python', expr='name', conv=None, format_spec=None)
# ' '
# Interpolation(value=3.14, expr='version', conv=None, format_spec=None)
# '!'
```

每个 `Interpolation` 对象包含：
- `value`：插值表达式的求值结果
- `expr`：表达式的源码字符串
- `conv`：转换标志（`!s`/`!r`/`!a`）
- `format_spec`：格式说明符（`:.2f` 等）

### 安全 SQL 查询构建（t-strings 杀手级应用）

f-strings 最大的安全隐患是 SQL 注入：

```python
# ❌ 危险！SQL 注入！
user_input = "'; DROP TABLE users; --"
query = f"SELECT * FROM users WHERE name = '{user_input}'"
# SELECT * FROM users WHERE name = ''; DROP TABLE users; --'
```

使用 t-strings，你可以构建一个安全的 SQL 构建器：

```python
class SafeSQL:
    def __init__(self, template: Template):
        self.parts = []
        self.params = []
        for part in template:
            if isinstance(part, str):
                self.parts.append(part)
            else:
                self.parts.append("?")
                self.params.append(part.value)

    def execute(self, cursor):
        sql = "".join(self.parts)
        return cursor.execute(sql, self.params)

# 使用：自动参数化
username = input("用户名: ")
query = SafeSQL(t"SELECT * FROM users WHERE name = {username}")
# query.parts = ['SELECT * FROM users WHERE name = ', '?', '']
# query.params = ['user_input_value']  ← 自动参数化，无注入风险
query.execute(cursor)
```

### HTML 安全转义

```python
import html
from string.templatelib import Template

class SafeHTML:
    def __init__(self, template: Template):
        parts = []
        for part in template:
            if isinstance(part, str):
                parts.append(part)  # 静态部分不转义（模板作者控制）
            else:
                parts.append(html.escape(str(part.value)))  # 动态部分转义
        self._html = "".join(parts)

    def __str__(self):
        return self._html

user_input = "<script>alert('xss')</script>"
page = SafeHTML(t"<div>Hello, {user_input}</div>")
# <div>Hello, &lt;script&gt;alert('xss')&lt;/script&gt;</div>
```

### 与 f-strings 的格式语法兼容

t-strings 支持与 f-strings 相同的格式说明符和转换标志：

```python
import datetime
now = datetime.datetime.now()

# 格式说明符
t1 = t"Today is {now:%Y-%m-%d}"
str(t1)  # "Today is 2025-10-07"

# 转换标志
data = {"key": "value"}
t2 = t"Data: {data!r}"
str(t2)  # "Data: {'key': 'value'}"
```

### 自定义模板处理器

你可以创建自定义函数来处理 t-strings，类似"标签模板字面量"（JavaScript Tagged Templates）：

```python
def i18n(template: Template) -> str:
    """简单的国际化模板处理器"""
    parts = []
    for part in template:
        if isinstance(part, str):
            # 翻译静态文本部分
            parts.append(translate(part))
        else:
            # 插值部分保持原样
            parts.append(str(part.value))
    return "".join(parts)

# 使用
name = "World"
message = i18n(t"Hello, {name}!")  # 如果是中文环境，"Hello, " 可能翻译为 "你好，"
```

### 源码实现

t-strings 的实现涉及编译器和运行时两部分：
- [Parser/string_parser.c](https://github.com/python/cpython/blob/v3.14.0/Parser/string_parser.c) — t-string 解析
- [Python/compile.c](https://github.com/python/cpython/blob/v3.14.0/Python/compile.c) — 编译器生成 Template 构造代码
- [Objects/interpolationobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/interpolationobject.c) — `Interpolation` 对象 C 实现
- [Objects/stringtemplateobject.c](https://github.com/python/cpython/blob/v3.14.0/Objects/stringtemplateobject.c) — `Template` 对象 C 实现
- [Lib/string/templatelib.py](https://github.com/python/cpython/blob/v3.14.0/Lib/string/templatelib.py) — Python 层辅助 API

---

## 5. 内置函数变更

### `map()` 新增 `strict` 参数

`map()` 函数新增 `strict` 关键字参数（类似 `zip()` 的 `strict`），当多个可迭代对象长度不一致时抛出 `ValueError`：

```python
# 旧行为：静默截断到最短
list(map(lambda x, y: x + y, [1, 2, 3], [10, 20]))
# [11, 22]  ← 3 被静默丢弃！

# 新行为（strict=True）：长度不一致时报错
list(map(lambda x, y: x + y, [1, 2, 3], [10, 20], strict=True))
# ValueError: map() has arguments of different lengths
```

### `float.from_number()`

新增 `float.from_number(x)` 类方法，将数字转换为浮点数，对非有限值（NaN、inf）抛出 `OverflowError`：

```python
float.from_number(3)      # 3.0
float.from_number(3.14)   # 3.14
float.from_number(10**400)  # OverflowError: cannot convert infinity to float
float.from_number(float('nan'))  # OverflowError: cannot convert NaN to float
```

### `NotImplemented` 在布尔上下文中抛出 TypeError

`NotImplemented` 单例现在在布尔上下文中会抛出 `TypeError`，防止常见错误：

```python
# 旧行为：NotImplemented 被当作 truthy，导致隐蔽 bug
result = NotImplemented
if result:  # 旧版本中这是 True，可能导致错误分支
    print("unexpected")

# Python 3.14：
if NotImplemented:
    pass  # TypeError: NotImplemented cannot be used in a boolean context
```

这主要影响富比较方法（`__eq__`、`__lt__` 等）的实现。

### `memoryview` 下标支持

`memoryview` 现在支持使用整数元组进行多维下标访问，与 NumPy 行为一致：

```python
import array
# 创建二维数据
data = array.array('i', range(6))
mv = memoryview(data).cast('i', shape=(2, 3))
# mv 现在是 2x3 的二维 memoryview
print(mv[1, 2])  # 5  ← 元组下标
```

### 其他内置变更

| 变更 | 说明 |
|------|------|
| `__debug__` 静态检测 | 优化器现在可以在 `-O` 模式下静态移除 `if __debug__:` 块中的代码 |
| `-O` 模式语法检测 | `-O` 模式下对 `assert` 语句和 `__debug__` 的使用进行更严格的静态检查 |
| C99 复数运算 | 复数运算现在遵循 C99 标准（如 `infj * 0` 的行为） |

---

## 6. 字节码变更概览

Python 3.14 对字节码指令集进行了调整以支持新特性和优化：

### 新增操作码

| 操作码 | 用途 |
|--------|------|
| `LOAD_FAST_AND_CLEAR` | 加载局部变量并将其设为 NULL（用于优化） |
| `JUMP_IF_FALSE_OR_POP` / `JUMP_IF_TRUE_OR_POP` | 优化的条件跳转 |
| `INTERPOLATION_*` | t-strings 相关的插值处理指令 |
| `SET_FUNCTION_ATTRIBUTE` | 统一设置函数属性 |

### 移除/废弃操作码

| 操作码 | 替代方案 |
|--------|---------|
| 部分特化指令的重构 | Tier 2 uop 替代 |

### 查看字节码

你可以使用 `dis` 模块查看 Python 3.14 的字节码：

```python
import dis

def greet(name):
    return t"Hello, {name}!"

dis.dis(greet)
# 可以看到 INTERPOLATION 相关指令
```

字节码变更主要影响代码生成工具、反汇编工具和字节码操作库。对于普通应用开发者，字节码变更是透明的。

### 源码引用

字节码定义位于 [Include/opcode_ids.h](https://github.com/python/cpython/blob/v3.14.0/Include/opcode_ids.h)，执行逻辑在 [Python/ceval.c](https://github.com/python/cpython/blob/v3.14.0/Python/ceval.c) 和 [Python/generated_cases.c.h](https://github.com/python/cpython/blob/v3.14.0/Python/generated_cases.c.h)（自动生成）。

---

## 8. 本章小结

| 特性 | PEP/来源 | 对日常编码的影响 |
|------|-----|----------------|
| 无括号 except | PEP 758 | 语法更简洁，多个异常类型无需括号 |
| finally 控制流警告 | PEP 765 | 帮助发现隐蔽 bug，注意清理代码中的 return/break |
| 延迟注解求值 | PEP 649/749 | 前向引用自然工作，可删除 `__future__ annotations` |
| **UnionType = Union** | - | `int \| str` 与 `Union[int, str]` 完全统一，repr 改变 |
| **TypeAliasType 星号解包** | - | PEP 695 type 语句支持 `*Ts` 解包 |
| **io.Reader/Writer 协议** | - | 替代 typing.IO，更符合结构子类型 |
| t-strings | PEP 750 | 安全模板、SQL/HTML 防注入、DSL 构建 |
| map(strict=True) | - | 防止静默截断 |
| float.from_number() | - | 安全数值转换 |
| NotImplemented TypeError | - | 防止富比较中的隐蔽 bug |

下一章将深入解析 Python 3.14 最具革命性的变化：**自由线程（无 GIL 模式）**。

---

- [上一章：概述](00-overview.md) ←
- [下一章：自由线程（无 GIL）深度解析](02-free-threading.md) →
