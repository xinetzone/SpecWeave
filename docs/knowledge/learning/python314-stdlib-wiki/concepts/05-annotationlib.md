---
id: python314-stdlib-wiki-05-annotationlib
title: "Python 3.14 标准库 annotationlib 全面详解"
date: "2026-08-18"
category: "learning"
tags: ["python", "python-3.14", "stdlib", "annotationlib", "annotations", "type-hints", "pep-749", "tutorial"]
type: "Reference"
description: "annotationlib是Python 3.14新增的标准库模块，提供底层工具用于在惰性求值注解存在前向引用时，仍以可靠可控方式内省模块、类和函数上的注解。"
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
status: "stable"
stale_after: "2027-08-22"
---

# Python 3.14 标准库 annotationlib 全面详解

> 一句话摘要：`annotationlib` 是 Python 3.14 新增的标准库模块，提供一组底层工具，用于在惰性求值的注解存在前向引用等极端情况时，仍然以可靠、可控的方式（通过 VALUE / FORWARDREF / STRING 三种格式）内省模块、类和函数上的注解，取代了直接解析 `__annotations__` 属性的脆弱做法。

## 模块定位与用途

`annotationlib` 模块（源代码为 `Lib/annotationlib.py`）在 Python 3.14 中新增，用于在**模块、类和函数**上内省注解（annotation）。

在 Python 3.14 中，类型注解是**延迟求值**（lazily evaluated）的，并且经常包含对"在注解创建时尚且未定义"的对象的前向引用（forward reference）。例如，在类体内部把本类用作返回值注解、或引用后面才定义的类，都属于前向引用。在这种背景下，直接读取并解析对象的 `__annotations__` 属性往往不可靠——它可能触发求值异常、前向引用无法解析，或依赖于 `from __future__ import annotations` 是否生效而呈现出完全不同的形态。

`annotationlib` 提供了一组**底层、内建式**的工具来解决这一问题：

- 以**三种主要格式**检索注解（见 `Format` 枚举）：`VALUE`（求值并返回值）、`FORWARDREF`（对无法解析的名称返回 `ForwardRef` 代理）、`STRING`（以字符串形式返回，接近源代码原貌）。
- `get_annotations()` 是检索注解的主要入口点。
- 提供直接操纵"注解函数"（annotate function）的工具：`get_annotate_from_class_namespace()`、`call_annotate_function()`，以及处理"求值函数"（evaluate function）的 `call_evaluate_function()`。

> **小心**：此模块中的大多数功能都可能执行任意代码，请务必阅读本文末尾的安全说明。

该模块依据 [PEP 649](https://peps.python.org/pep-0649/)（提出当前注解工作模型）与 [PEP 749](https://peps.python.org/pep-0749/)（在 PEP 649 基础上扩展并引入 `annotationlib` 模块）设计实现。[typing-extensions](https://pypi.org/project/typing-extensions/) 提供了 `get_annotations()` 的向后移植版本，可在早期 Python 版本上使用。

## 核心术语表

下表列出了理解本章所需的核心术语，均以平实的语言解释，避免用术语解释术语。

| 术语 | 一句话解释 |
|---|---|
| 注解（annotation） | 依附在模块、类、函数、变量上的额外标签，最常见的是类型提示格式，例如 `def f(a: int) -> str` 中的 `int` 和 `str`。 |
| 格式（Format） | 一个枚举，用来指定"注解该以什么样子被取出来"，是求值后的值、前向引用代理，还是源码字符串。 |
| 惰性求值（lazy evaluation） | 注解表达式不在一开始就执行，而是等到有人真正访问注解时才去执行。 |
| 前向引用（forward reference） | 注解中引用了一个"当下还没定义、稍后才出现"的名字，例如类体里提前引用本类自身。 |
| 字符串化注解（stringized annotations） | 通过 `from __future__ import annotations` 打开的一种旧模式下，注解被直接存成字符串而不求值。 |
| 注解函数（annotate function） | 编译器为函数、类、模块自动生成的一个内部函数，负责在被调用时把注解表达式求值成字典，可通过 `__annotate__` 属性访问。 |
| 求值函数（evaluate function） | 与注解函数类似，但只求值"单个"表达式并返回一个值，常见于类型别名、类型变量的边界/约束/默认值。 |
| 伪全局环境（fake globals） | `annotationlib` 内部使用的一种特殊执行环境，用来在不真正求值的情况下倒推注解的源码文本或前向引用结构。 |
| STRING 格式 | 把注解按"它在源代码里写出来的样子"以字符串返回，服务文档生成器等需要可读展示的场景。 |

## 惰性注解求值语义（PEP 749 的动机）

理解 `annotationlib` 必须先理解 Python 3 历史中注解**执行模型**的三次演变：

1. **标准语义**（Python 3.0–3.13 默认，PEP 3107 / PEP 526）：注解在源代码中被**遇到时立即求值**。
2. **字符串化注解**（Python 3.7 起可用，`from __future__ import annotations` 开启，PEP 563）：注解**只以字符串形式存储**，不求值。
3. **延迟求值**（Python 3.14 起默认，PEP 649 / PEP 749）：注解**延迟求值，仅在被访问时才执行**。

以一个例子说明三种模型的差异：

```python
def func(a: Cls) -> None:
    print(a)

class Cls: pass

print(func.__annotations__)
```

- 在**标准语义**下，程序会在定义 `func` 的那一行抛出 `NameError`，因为此刻 `Cls` 还是未定义的名字。
- 在**字符串化注解**下，程序打印 `{'a': 'Cls', 'return': 'None'}`（注解被存成字符串）。
- 在**延迟求值**（Python 3.14）下，程序打印 `{'a': <class 'Cls'>, 'return': None}`（访问时才求值，此时 `Cls` 已定义）。

### 为什么需要延迟求值与 `annotationlib`

标准语义有两个明显缺点：其一，注解里引用尚未定义的名字会报错；其二，在模块导入时就执行注解会带来性能开销。字符串化注解（PEP 563 计划长期作为默认）虽然解决了这两个问题，但它对**运行时内省注解的人**很不友好——拿到手的是没有求值的字符串，难以直接使用。

PEP 649 因此提出第三种执行模型：**把注解表达式打包进一个 `__annotate__` 函数，而不是在定义函数/类的时候就执行它们**。这样：

- 定义函数、类或模块时，注解表达式**不会**立即求值，避免了前向引用报错与导入时的性能损耗；
- 只有当有人访问注解（例如读取 `__annotations__` 或调用 `__annotate__`）时，注解表达式才会真正执行；
- 如果此时相关名字已经定义，前向引用就能被正常解析。

PEP 749 在 PEP 649 基础上做了多方面扩展，并正式引入了 `annotationlib` 模块，把这套机制暴露为可直接使用的公共 API。需要注意的是，如果源码中仍然显式使用了 `from __future__ import annotations`，Python 3.14 仍会沿用字符串化注解行为（但这一行为最终会被移除）。

## 核心类与函数详解

本节按官方文档逐一讲解所有公开的类型与函数，签名均以文档为准。

### 类：`annotationlib.Format`

`Format` 是一个 `enum.IntEnum` 枚举，用于描述注解可以返回的格式。它的成员（或与其等价的整数值）既可以传给 `get_annotations()` 及本模块其他函数，也可以传给 `__annotate__` 函数。

其成员及取值如下：

| 成员 | 数值 | 含义 |
|---|---|---|
| `Format.VALUE` | 1 | 值是对注解表达式求值后的结果。使用最直接，但当注解包含未定义名称的引用时可能报错。 |
| `Format.VALUE_WITH_FAKE_GLOBALS` | 2 | 特殊值，表示注解函数正在具有**伪全局变量**的特殊环境中求值。注解函数应返回与 `VALUE` 格式相同的值，或抛出 `NotImplementedError` 表示不支持此环境。**此格式仅为内部使用，不应传给本模块中的函数。** |
| `Format.FORWARDREF` | 3 | 对已定义的值使用真实注解值（等同于 `VALUE`）；对未定义的值使用 `ForwardRef` 代理。真实对象内部可能包含对 `ForwardRef` 代理对象的引用。 |
| `Format.STRING` | 4 | 值是注解在源代码中呈现的文本字符串，可能经过（但不限于）空白符规范化、常量值优化等修改。这些字符串的确切值可能在未来的 Python 版本中发生变化。 |

> 说明：官方文档中 `Format` 只有上述四个成员（`VALUE`、`VALUE_WITH_FAKE_GLOBALS`、`FORWARDREF`、`STRING`），**并不存在名为 `SOURCE` 的成员**。切不可按臆测使用不存在的枚举成员。

### 类：`annotationlib.ForwardRef`

`ForwardRef` 是用于注解中前向引用的**代理对象**。当以 `FORWARDREF` 格式检索注解、且注解中含有无法解析的名字时，就会得到该类的实例（常见于在类定义之前引用该类自身的情况）。

**属性 `__forward_arg__`**：一个字符串，内容是生成该 `ForwardRef` 所执行的代码。该字符串可能与原始源代码并不完全等同。

**方法 `evaluate(*, owner=None, globals=None, locals=None, type_params=None, format=Format.VALUE)`**：对前向引用求值并返回其值。

- 若 `format` 为 `VALUE`（默认值），遇到无法解析的前向引用名字时可能抛出 `NameError` 等异常；可通过参数为那些原本未定义的名字提供绑定。
- 若 `format` 为 `FORWARDREF`，此方法**绝不会抛出异常**，但可能返回一个 `ForwardRef` 实例。例如当前向引用代码为 `list[undefined]`（`undefined` 未定义）时，以 `FORWARDREF` 格式求值会返回 `list[ForwardRef('undefined')]`。
- 若 `format` 为 `STRING`，此方法返回 `__forward_arg__`（即源码字符串）。

参数含义：

- `owner`：向此方法传递作用域信息的**首选机制**，即该 `ForwardRef` 所源自注解的归属对象（模块对象、类型对象或函数对象）。
- `globals` / `locals`：更精细地控制求值时可见的名字，它们会被传递给 `eval()`，作为求值该名字时的全局/局部命名空间。
- `type_params`：与泛型类、泛型函数相关，是表示"当前作用域内类型形参"的元组。例如对从泛型类 `C` 的类命名空间中取出的 `ForwardRef` 求值时，应设为 `C.__type_params__`。

需要注意：由 `get_annotations()` 返回的 `ForwardRef` 实例会**保留其来源作用域的信息**，因此调用 `evaluate()` 时无需额外传参即可求值。而通过其他方式创建的 `ForwardRef` 可能不含任何作用域信息，此时若不传 `owner` / `globals` / `locals` / `type_params`，则会使用**空的全局与局部字典**，可能导致求值失败。

### 函数：`annotationlib.get_annotations(obj, *, globals=None, locals=None, eval_str=False, format=Format.VALUE)`

计算一个对象的注解字典，是**访问任何对象注解字典的最佳实践入口**。

- `obj`：可以是可调用对象、类、模块，或其他具有 `__annotate__` 或 `__annotations__` 属性的对象。传入其他对象会抛出 `TypeError`。
- `format`：控制返回格式，必须是 `Format` 枚举成员或其整数值。不同格式的具体工作方式与回退策略见官方文档，要点如下：
  - `VALUE`：先尝试 `object.__annotations__`；若不存在，则调用 `object.__annotate__`（若存在）。
  - `FORWARDREF`：若 `object.__annotations__` 存在且能成功求值则用之；否则调用 `object.__annotate__`；再不行则重新尝试 `object.__annotations__` 并重新抛出访问错误。调用 `__annotate__` 时会先以 `FORWARDREF` 调用，未实现则检查 `VALUE_WITH_FAKE_GLOBALS`（在伪全局环境中使用），都不支持则回退到 `VALUE`，`VALUE` 失败则抛出该错误。
  - `STRING`：若 `object.__annotate__` 存在则先调用它；否则用 `object.__annotations__` 并配合 `annotations_to_string()` 做字符串化。调用 `__annotate__` 时依次尝试 `STRING`、`VALUE_WITH_FAKE_GLOBALS`，最后回退到 `VALUE` + `annotations_to_string()`。
- **返回值**：`get_annotations()` 每次调用都返回一个**新字典**；对同一对象调用两次会得到两个内容等价但互不相同的字典。
- `eval_str`：当为 true 时，会对 `str` 类型的值调用 `eval()` 进行"反字符串化"，用于配合字符串化注解（如 `from __future__ import annotations`）。**将 `eval_str=True` 与非 `Format.VALUE` 格式一起使用是错误的。** 注意 `get_annotations()` 不会捕获 `eval()` 抛出的异常。
- 其他细节：若 `obj` 不含注解字典则返回空字典（函数和方法总含注解字典；类、模块及其他可调用对象可能没有）；忽略类上的继承注解与元类注解；出于安全考虑，对象成员与字典值的访问都通过 `getattr()` 和 `dict.get()` 完成。
- `globals` / `locals`：传给内部 `eval()`；当二者为 `None` 时会依据 `type(obj)` 采用上下文相关的默认值——`obj` 为模块时 `globals` 默认为 `obj.__dict__`；为类时 `globals` 默认为 `sys.modules[obj.__module__].__dict__`、`locals` 默认为类的命名空间；为可调用对象时 `globals` 默认为 `obj.__globals__`（若为 `functools.update_wrapper` 包装函数或 `functools.partial` 对象，会逐层解包直到找到未包装的函数）。

```python
>>> def f(a: int, b: str) -> float:
...     pass
>>> get_annotations(f)
{'a': <class 'int'>, 'b': <class 'str'>, 'return': <class 'float'>}
```

### 函数：`annotationlib.annotations_to_string(annotations)`

把"包含运行时值的注解字典"转换为"仅含字符串的字典"：值若已是字符串则保持不变，否则用 `type_repr()` 转换。这是为用户提供的、支持 `STRING` 格式但无法访问注解创建代码的注解函数准备的工具。

它用于实现功能性语法创建的 `typing.TypedDict` 类的 `STRING` 格式：

```python
>>> from typing import TypedDict
>>> Movie = TypedDict("movie", {"name": str, "year": int})
>>> get_annotations(Movie, format=Format.STRING)
{'name': 'str', 'year': 'int'}
```

### 函数：`annotationlib.call_annotate_function(annotate, format, *, owner=None)`

用给定的 `format`（`Format` 枚举成员）调用注解函数 `annotate`，并返回它生成的注解字典。

之所以需要这个辅助函数，是因为编译器为函数、类、模块生成的注解函数在**直接调用时仅支持 `VALUE` 格式**。为了支持其他格式，此函数会在一个特殊环境中调用注解函数，使其能够生成其他格式的注解。它是在类构建过程中"部分求值注解"这类功能的有用构件。`owner` 是拥有注解函数的对象（通常是函数、类或模块），提供后会在 `FORWARDREF` 格式下用于生成携带更多信息的 `ForwardRef`。

### 函数：`annotationlib.call_evaluate_function(evaluate, format, *, owner=None)`

用给定 `format` 调用**求值函数**（evaluate function）`evaluate` 并返回它生成的值。与 `call_annotate_function()` 不同：后者始终返回"字符串到注解"的字典，而本函数返回**单个值**。

它主要服务于类型别名与类型形参的延迟求值元素，例如 `typing.TypeAliasType.evaluate_value()`（类型别名的值）、`typing.TypeVar.evaluate_bound()` / `evaluate_constraints()` / `evaluate_default()`、`typing.ParamSpec.evaluate_default()`、`typing.TypeVarTuple.evaluate_default()`。`owner` 是拥有求值函数的对象（如类型别名或类型变量对象）。

```python
>>> type Alias = undefined
>>> call_evaluate_function(Alias.evaluate_value, Format.VALUE)
Traceback (most recent call last):
...
NameError: name 'undefined' is not defined
>>> call_evaluate_function(Alias.evaluate_value, Format.FORWARDREF)
ForwardRef('undefined')
>>> call_evaluate_function(Alias.evaluate_value, Format.STRING)
'undefined'
```

### 函数：`annotationlib.get_annotate_from_class_namespace(namespace)`

从类命名空间字典 `namespace` 中检索注解函数（annotate function）；若命名空间中不含注解函数则返回 `None`。这在类完全创建之前（例如在元类中）特别有用；类创建完成后，可通过 `cls.__annotate__` 直接取得注解函数。

### 函数：`annotationlib.type_repr(value)`

将任意 Python 值转换为适合 `STRING` 格式使用的形式。对大多数对象会调用 `repr()`，但对某些对象（如类型对象）有特殊处理，例如把 `int` 转换为字符串 `'int'`。它同样是为支持 `STRING` 格式但无法访问注解创建代码的用户注解函数准备的辅助工具，也可用于为注解中常见的值提供更友好的字符串表示。

### 关于异常：本模块未定义专属异常类

需要特别说明：官方文档**并没有**为 `annotationlib` 定义任何专属异常类（不存在诸如 `AnnotationLibError`、`GetAnnotationsError`、`WrongFormat`、`ForwardRefError` 之类的异常）。本模块的错误都直接来自**内置异常**，例如：

- `TypeError`：向 `get_annotations()` 传入既不具 `__annotate__` 也不具 `__annotations__` 属性的对象；
- `NameError`：以 `VALUE` 格式求值时引用未定义名字；
- `NotImplementedError`：注解函数收到 `VALUE_WITH_FAKE_GLOBALS` 但不支持该环境时抛出；
- 以及 `eval()` 可能抛出的各种异常（如示例中的 `ZeroDivisionError`）。

因此，使用本模块时无需 `import` 任何自定义异常类，直接用标准异常做 `try/except` 即可。

## 四种格式的对比与适用场景

`Format` 的四个取值对同一段注解会产生不同的返回结果，其对比与适用场景如下表：

| 格式 | 返回内容 | 求值是否可能报错 | 典型适用场景 |
|---|---|---|---|
| `VALUE`（1） | 注解表达式的实际求值结果 | 可能（含未定义名字时抛 `NameError`） | 需要拿到真实的类型对象/值直接使用 |
| `VALUE_WITH_FAKE_GLOBALS`（2） | 在伪全局环境下的求值结果（内部） | 注解函数可能抛 `NotImplementedError` | 仅供内部实现，**不应**由用户传入 |
| `FORWARDREF`（3） | 已定义的用真实值，未定义的用 `ForwardRef` 代理 | 不会因未定义名字而报错 | 需要安全地检查可能含未解析前向引用的注解 |
| `STRING`（4） | 注解在源代码中的文本字符串（可能被规范化） | 一般不涉及求值 | 文档生成器、把注解以可读形式展示 |

一句话概括选择策略：**要值用 `VALUE`，怕报错想检查结构用 `FORWARDREF`，要展示原文用 `STRING`**。

## 代码示例

以下示例均在 Python 3.14 下验证可运行。

### 示例一：`format=Format.VALUE` 求值

```python
from annotationlib import get_annotations, Format

def build(a: int, b: list[str]) -> dict[str, float]:
    """把输入转换成浮点数字典。"""
    return {}

# 默认 format 即为 Format.VALUE，返回求值后的真实类型对象
print(get_annotations(build))
# {'a': <class 'int'>, 'b': list[str], 'return': dict[str, float]}

# 也可显式指定
print(get_annotations(build, format=Format.VALUE))
```

### 示例二：`format=Format.STRING` 取原始字符串

```python
from annotationlib import get_annotations, Format

def build(a: int, b: list[str]) -> dict[str, float]:
    return {}

# STRING 格式返回接近源码文本的字符串字典
print(get_annotations(build, format=Format.STRING))
# {'a': 'int', 'b': 'list[str]', 'return': 'dict[str, float]'}
```

### 示例三：`ForwardRef` 的求值

```python
from annotationlib import get_annotations, Format

# 此刻名字 Under 尚未定义，注解中的 Under 就是一个前向引用
def describe(x: Under) -> None:
    pass

# 用 FORWARDREF 格式安全地拿到前向引用代理，而不是抛 NameError
annotations = get_annotations(describe, format=Format.FORWARDREF)
forward_ref = annotations["x"]
print(repr(forward_ref))                            # ForwardRef('Under', owner=<function describe ...>)
print(forward_ref.__forward_arg__)                  # 'Under'（生成该引用的源码串）
print(forward_ref.evaluate(format=Format.STRING))   # 'Under'（以字符串返回，不求值）

# 定义 Under 之后，即可真正求值
Under = int
print(forward_ref.evaluate())                       # <class 'int'>
```

> 说明：若在 `Under` 定义之前就调用 `forward_ref.evaluate()`（默认 `VALUE` 格式），会抛出 `NameError`；而 `evaluate(format=Format.FORWARDREF)` 则绝不会因未定义名字而抛异常。这是前向引用代理最典型的用法——先安全地拿到代理对象检查结构，待相关名字就绪后再求值。

## 与 `typing.get_type_hints` 的差异

`annotationlib.get_annotations()` 与 `typing.get_type_hints()` 都可用于获取注解，官方文档指出 `get_type_hints()` **通常与 `get_annotations()` 相同**，但会额外对注解字典做如下处理：

1. **解析前向引用**：以字符串字面量或代理对象形式编码的前向引用，会在 `globalns` / `localns` 以及（如适用）对象的类型形参命名空间中被求值；未传入命名空间时从 `obj` 推断。
2. **替换 `None`**：把 `None` 替换为 `types.NoneType`。
3. **合并基类注解**：若 `obj` 是类 `C`，返回的字典会把 `C` 各基类的注解与 `C` 自身的注解合并（沿 `C.__mro__` 遍历、迭代合并，MRO 中靠前的类的注解优先）。
4. **递归替换特殊结构**：把所有 `Annotated[T, ...]`、`Required[T]`、`NotRequired[T]`、`ReadOnly[T]` 递归替换为 `T`（除非 `include_extras=True`）。

两者关系在 3.14 中进一步靠拢：

- `typing.get_type_hints()` 自 3.14 起新增了 `format` 参数，其文档直接指向 `annotationlib.get_annotations()`。
- `typing.ForwardRef` 自 3.14 起成为 `annotationlib.ForwardRef` 的**别名**。
- `typing.evaluate_forward_ref()` 自 3.14 起新增，行为类似 `annotationlib.ForwardRef.evaluate()` 但会递归地求值嵌套在类型提示中的前向引用。

可以这样理解二者的定位：`annotationlib` 是**底层、格式可控、不做类型系统加工**的内省原语；`typing.get_type_hints()` 是在其之上做了一层"类型系统语义"的**便捷封装**（合并基类、展开 `Annotated`、`None → NoneType` 等）。若你只需要拿到最原始的注解数据，用 `get_annotations()`；若要拿到经过 typing 语义整理的、可直接用于类型检查的结果，用 `get_type_hints()`。二者作为内省入口都可能执行注解中的代码，安全风险相同。

## 版本与稳定性说明

- 本模块整体标记为 **Added in version 3.14**，即 Python 3.14 新增。
- 官方文档**并未**将 `annotationlib` 标注为 "provisional"（暂定/不稳定）——至少在本章抓取的 3.14 官方文档页面中没有任何 provisional 标记。但文档在两处给出了稳定性预警：
  - `Format.STRING` 返回的字符串文本值"可能经过空白符规范化、常量值优化等修改，其确切值可能在未来的 Python 版本中发生变化"；
  - STRING 格式与 FORWARDREF 格式各自存在明确的**局限性**（见下一节）。
- 若源码仍显式使用 `from __future__ import annotations`，会继续得到字符串化注解，但该行为最终将被移除。因此新代码应优先面向 3.14 的惰性求值模型编写。

结论：`annotationlib` 是 3.14 起的标准能力，可正常使用，但依赖 `STRING` 格式的确切字符串内容或依赖上述局限场景时应保持谨慎。

## 注意事项 / 反模式

1. **安全是首要问题**：本模块大部分功能都会执行与注解相关的代码，可能引发任意系统调用、无限循环等。`get_annotations()` 可能调用任意的注解函数，`eval_str=True` 会对任意字符串调用 `eval()`。同理，任何访问 `__annotations__` 属性、以及 `typing.get_type_hints()` 等 typing 内省函数也无差别地具有此风险。**绝不要**把不受信任来源的字符串或输入交给任何注解内省 API（例如通过编辑 `__annotations__` 字典或直接构造 `ForwardRef` 对象）。
2. **不要使用 `Format.SOURCE` 或臆想的别名**：官方文档的 `Format` 只有 `VALUE`、`VALUE_WITH_FAKE_GLOBALS`、`FORWARDREF`、`STRING` 四个成员，不存在 `SOURCE`；也不要使用不存在的异常类（如 `AnnotationLibError` 等）。
3. **不要直接传 `VALUE_WITH_FAKE_GLOBALS`**：该值是内部实现专用的特殊值，文档明确要求"不应传递给本模块中的函数"。
4. **`eval_str=True` 只能与 `Format.VALUE` 搭配**，与非 VALUE 格式混用是错误的。
5. **不要假设 `STRING` 格式与源码逐字一致**：它无法恢复编译后已丢失的注释、空白符、括号结构与被编译器简化的操作，且常量表示可能被改写（如十六进制转十进制、字符串转义丢失）。
6. **`FORWARDREF` 格式并非永不报错**：对"字面值运算"或不被支持的表达式（如 `1 / 0`、`x if y else z` 等）依然会抛出异常。
7. **不要缓存 `get_annotations()` 的返回值做长期复用而不理解其每次新建字典**：每次调用都会返回新字典。
8. **忽略继承与元类注解是有意行为**：若类自身没有注解字典，`get_annotations()` 返回空字典，而不会像 `get_type_hints()` 那样合并基类；需要合并语义时改用 `get_type_hints()`。

## 章节导航

- [上一章：sys.monitoring](/concepts/04-sys-monitoring.md) →
- [下一章：dataclasses](/concepts/06-dataclasses.md) →