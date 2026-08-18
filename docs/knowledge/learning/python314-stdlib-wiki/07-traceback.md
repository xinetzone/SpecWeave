---
id: python314-stdlib-wiki-07-traceback
title: "Python 3.14 标准库 traceback 全面详解"
date: "2026-08-18"
category: "learning"
tags: ["python", "python-3.14", "stdlib", "traceback", "exception", "stack", "debugging", "tutorial"]
---

# Python 3.14 标准库 traceback 全面详解

> 一句话摘要：`traceback` 是 Python 标准库中用于提取、格式化与打印程序栈回溯信息的标准接口，它比解释器默认的回溯显示更灵活，并且能够在不持有异常对象引用的情况下捕获足够多的异常信息供稍后渲染，从而显著提升内存管理效率。

## 模块定位与用途

当一个 Python 程序抛出异常且未被捕获时，解释器会打印一段类似下面的回溯信息（traceback，也常被译为"栈回溯""堆栈跟踪"或"栈跟踪"）：

```
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    1 / 0
ZeroDivisionError: division by zero
```

这段输出告诉开发者"错误发生在哪个文件的哪一行、调用链是如何一步步到达出错点的"。`traceback` 模块就是对这一能力的标准化封装——它提供了提取、格式化和打印栈回溯信息的标准接口。与解释器默认的自动回溯显示相比，`traceback` 具有以下优势：

1. **可配置性更强**：能够只打印回溯中的特定部分（例如限制条目数量、指定输出目标文件）。
2. **交互式检查友好**：提供返回结构化数据（列表、字符串）的格式化函数，便于程序在 `except` 块内自行处理错误信息。
3. **轻量的"稍后打印"能力**：可以捕获关于异常的足够信息以供稍后打印，而无需保存对实际异常对象的引用。由于异常可能充当大型对象图的根对象（异常链会牵住整棵对象树），这一能力能显著降低内存占用、避免内存泄漏。

本模块操作的核心对象是**回溯对象**（traceback object），其类型为 `types.TracebackType`，它们被赋值给 `BaseException` 实例的 `__traceback__` 字段。

本模块的 API 可划分为两个层次：

- **模块级函数**：提供基本功能，适合对异常和回溯做交互式检查。
- **面向对象类**：`TracebackException` 及其辅助类 `StackSummary`、`FrameSummary`，它们在生成输出上更灵活，并能在不持有实际异常与回溯对象引用的前提下存储信息，供后续格式化。

> 相关模块：`faulthandler`（在错误、超时或用户信号发生时显式转储回溯）、`pdb`（交互式源代码调试器）。

> 自 3.13 版本起，`traceback` 的输出默认带颜色，并可使用环境变量控制（参见 `PYTHON_COLORS` 等命令行相关控制项）。

## 核心术语表

| 术语 | 一句话平实解释 |
|---|---|
| 栈回溯（traceback） | 程序出错时，从出错位置一路回溯到调用起点的函数调用链记录。 |
| 回溯对象（traceback object） | 表示"异常发生时调用栈"的数据结构，类型为 `types.TracebackType`，可通过 `tb_next` 逐层向前追溯。 |
| 栈帧（frame） | 一次函数调用所对应的执行环境，记录了"正在执行哪个文件的哪一行、函数叫什么名字、有哪些局部变量"。 |
| 栈摘要（StackSummary） | 把一整个调用栈整理成有序的帧摘要列表，是栈的"可格式化"表示。 |
| 帧摘要（FrameSummary） | 栈中的单个帧的轻量描述，记录文件名、行号、函数名、源代码行等信息。 |
| 链式异常（chained exception） | 一个异常在处理另一个异常的过程中被引发，两者之间形成的"前因后果"关联，通过 `__cause__` 与 `__context__` 表达。 |
| 异常组（exception group） | 一个容器型异常，内部可包裹多个子异常，用于在一次操作中同时报告多个错误。 |
| 别名异常（alias exceptions） | 多个不同的异常名称实际指向同一个异常类的现象，例如 `IOError`、`EnvironmentError`、`WindowsError`、`socket.error` 等名称都是 `OSError`（或其子类）的别名。 |

> 术语表说明：首行的"栈回溯"与第二行的"回溯对象"分别指"一段输出文本"和"承载这段文本的运行时数据结构"，二者常被混用，但前者是表象、后者是机制。

## 模块级函数详解

### 打印类函数

#### `traceback.print_tb(tb, limit=None, file=None)`

打印回溯对象 `tb` 中的栈回溯条目。

- 如果 `limit` 为正值，则至多打印 `limit` 个条目（从调用方的帧开始）。
- 如果 `limit` 为负值，则打印最后 `abs(limit)` 个条目。
- 如果 `limit` 被省略或为 `None`，则打印所有条目。
- 如果 `file` 被省略或为 `None`，则输出到 `sys.stderr`；否则 `file` 应为一个打开的文件对象或类文件对象（用于接收输出）。

> 注意：`limit` 形参的含义与 `sys.tracebacklimit` 不同。负的 `limit` 值对应于正的 `sys.tracebacklimit` 值；而正的 `limit` 值所能达到的效果无法用 `sys.tracebacklimit` 来表达。

> 3.5 版本变更：添加了对负数 `limit` 的支持。

#### `traceback.print_exception(exc, /, [value, tb, ]limit=None, file=None, chain=True)`

将从回溯对象 `tb` 得到的异常信息和栈跟踪条目打印到 `file`。它与 `print_tb()` 的区别在于：

- 如果 `tb` 不为 `None`，则先打印头部 `Traceback (most recent call last):`。
- 在栈回溯之后打印异常的**类型**和 `value`（异常值）。
- 如果 `type(value)` 是 `SyntaxError` 且 `value` 格式适当，它会打印发生语法错误的源代码行，并用一个脱字符（`^`）指明错误的大致位置。

参数约定：

- 从 Python 3.10 起，可以不再传递 `value` 和 `tb`，而是直接传递一个异常对象作为第一个参数 `exc`。若同时提供了 `value` 和 `tb`，则第一个参数会被忽略，以保持向后兼容（旧的签名是 `print_exception(etype, value, tb, ...)`）。
- 可选的 `limit` 参数含义与 `print_tb()` 相同。
- 如果 `chain` 为真值（默认），则链式异常（异常的 `__cause__` 或 `__context__` 属性）也会被打印，就像解释器自行打印未处理异常时那样。

> 3.5 版本变更：`etype` 参数会被忽略，并由 `value` 推断出来。
> 3.10 版本变更：`etype` 形参被重命名为 `exc`，并且现在是一个仅限位置（positional-only）形参（`/` 标记之后）。

#### `traceback.print_exc(limit=None, file=None, chain=True)`

这是 `print_exception(sys.exception(), limit=limit, file=file, chain=chain)` 的快捷方式。它读取当前正在处理的异常（`sys.exception()`）并打印，通常在 `except` 块内直接调用即可，无需显式传异常对象。

#### `traceback.print_last(limit=None, file=None, chain=True)`

这是 `print_exception(sys.last_exc, limit=limit, file=file, chain=chain)` 的快捷方式。通常它只在异常到达交互式提示符之后才会起作用（参见 `sys.last_exc`——它保存交互式会话中最后一次未捕获的异常）。

#### `traceback.print_stack(f=None, limit=None, file=None)`

打印当前调用栈（而非异常回溯栈）。

- 如果 `limit` 为正数，则至多打印 `limit` 个栈跟踪条目（从唤起点开始）。
- 如果 `limit` 为负数，则打印最后 `abs(limit)` 个条目。
- 如果 `limit` 被省略或为 `None`，则打印所有条目。
- 可选的 `f` 参数可指定一个替代的栈帧作为起始位置（默认从调用点开始）。
- 可选的 `file` 参数含义与 `print_tb()` 相同。

> 3.5 版本变更：添加了对负数 `limit` 的支持。

### 格式化类函数

#### `traceback.format_exc(limit=None, chain=True)`

与 `print_exc(limit)` 类似，但不输出到文件，而是返回一个字符串。它等价于格式化当前正在处理的异常。

#### `traceback.format_exception(exc, /, [value, tb, ]limit=None, chain=True)`

格式化一个栈跟踪和异常信息。参数含义与 `print_exception()` 的相应参数完全相同。返回值是一个字符串**列表**，其中每个字符串都以换行符结束，有些还包含内部换行符。把列表中的字符串拼接起来打印，得到的文本与 `print_exception()` 的输出完全一致。

> 3.5 版本变更：`etype` 参数会被忽略并由 `value` 推断出来。
> 3.10 版本变更：此函数的行为与签名已被修改，以与 `print_exception()` 相匹配（即支持直接传入异常对象作为首个位置参数）。

#### `traceback.format_exception_only(exc, /, [value, ]*, show_group=False)`

只格式化回溯中的"异常部分"（不含栈），使用一个异常值（如 `sys.last_exc` 给出的值）作为输入。返回值是一个字符串列表，每个都以换行符结束：

- 列表包含异常的消息（message），通常是一条单独的字符串。
- 对于 `SyntaxError` 异常，则会包含多行，打印时能展示语法错误发生位置的详细信息。
- 在消息之后，列表还包含该异常所关联的"注释"（notes，见 `BaseException.__notes__`）。

参数约定：

- 从 Python 3.10 起，可以不传入 `value`，而是传入一个异常对象作为第一个参数；若提供了 `value`，则第一个参数会被忽略以保持向后兼容。
- 当 `show_group` 为 `True` 且异常为 `BaseExceptionGroup` 的实例时，还会递归地包含嵌套的异常，并根据它们的嵌套深度添加缩进。

> 3.10 版本变更：`etype` 形参被重命名为 `exc` 并成为仅限位置形参。
> 3.11 版本变更：返回的列表现在会包含关联到异常的任何"注释"。
> 3.13 版本变更：增加了 `show_group` 形参。

#### `traceback.format_list(extracted_list)`

给定一个由元组组成的列表，或由 `extract_tb()` / `extract_stack()` 返回的 `FrameSummary` 对象组成的列表，返回一个可打印的字符串列表。结果列表中的每个字符串对应于参数列表中相同索引的条目。每个字符串都以换行符结束；对于那些源文本行不为 `None` 的条目，字符串内部还可能包含换行符。

#### `traceback.format_stack(f=None, limit=None)`

这是 `format_list(extract_stack(f, limit))` 的简写形式，用于格式化当前调用栈并返回字符串列表。

> 补充：本模块还提供 `format_tb(tb, limit=None)`，它是 `format_list(extract_tb(tb, limit))` 的简写形式，用于格式化异常回溯栈。

### 提取类函数

#### `traceback.extract_tb(tb, limit=None)`

返回一个 `StackSummary` 对象，表示从回溯对象 `tb` 提取出的"预处理之后"的栈跟踪条目列表。它适合用于对栈跟踪做**替代性格式化**（即不按默认格式打印）。可选的 `limit` 参数含义与 `print_tb()` 相同。

所谓"预处理之后的栈跟踪条目"，实际上是一个 `FrameSummary` 对象，其属性保存了通常会为栈跟踪打印出来的那类信息（文件名、行号、函数名、源代码行等）。

#### `traceback.extract_stack(f=None, limit=None)`

从当前调用栈帧提取"原始回溯"（即当前执行位置的调用栈，而非异常栈）。返回值的格式与 `extract_tb()` 相同（一个 `StackSummary`）。可选的 `f` 和 `limit` 参数含义与 `print_stack()` 相同。

#### `traceback.walk_stack(f)`

从给定的帧 `f` 开始，沿着 `f.f_back` 向前方向遍历调用栈，产出一个由 `(帧, 行号)` 元组构成的序列（生成器）。如果 `f` 为 `None`，则使用当前栈。这个辅助函数需要与 `StackSummary.extract()` 配合使用。

> 3.5 版本新增。
> 3.14 版本变更：此函数之前返回一个"推迟到首次迭代时才遍历栈"的生成器；现在返回的生成器反映的是 `walk_stack` 被调用那一刻的栈状态。

#### `traceback.walk_tb(tb)`

沿着 `tb_next` 遍历回溯 `tb`，产出一个由 `(帧, 行号)` 元组构成的序列（生成器）。这个辅助函数需要与 `StackSummary.extract()` 配合使用。

> 3.5 版本新增。

#### `traceback.clear_frames(tb)`

通过调用回溯 `tb` 中每个帧对象的 `clear()` 方法，清除所有栈帧中的局部变量。这常用于在处理异常后主动释放被栈帧局部变量引用的大对象，避免内存驻留。

> 3.4 版本新增。

> 补充（打印类）：本模块还提供 `print_list(extracted_list, file=None)`，用于把 `extract_tb()` 或 `extract_stack()` 返回的列表以带格式的栈回溯形式打印到给定文件；若 `file` 为 `None` 则输出到 `sys.stderr`。

## 类详解

模块级函数适合即时打印，但若你需要"先捕获、稍后再渲染"，或者需要更精细地控制输出格式，则应使用下面三个类。

### `TracebackException`

> 3.5 版本新增。

`TracebackException` 对象基于实际异常创建，用于捕获数据供稍后打印。它们通过**避免持有对回溯对象和帧对象的引用**，提供了一种更轻量的存储方式。此外，相比模块级函数，它们公开了更多用于配置输出的选项。

#### 构造方法

```
class TracebackException(exc_type, exc_value, exc_traceback, *, limit=None, lookup_lines=True, capture_locals=False, compact=False, max_group_width=15, max_group_depth=10)
```

捕获异常以供稍后渲染。其中 `limit`、`lookup_lines` 和 `capture_locals` 的含义与 `StackSummary` 类的同名参数相同。

- 如果 `compact` 为真值，则只有 `TracebackException.format()` 方法真正需要的数据会被保存在类属性中。特别地，`__context__` 字段只有在 `__cause__` 为 `None` 且 `__suppress_context__` 为假值时才会被计算（这能在异常链很长时节省内存）。
- 当局部变量被捕获（`capture_locals=True`）时，它们也会被显示在回溯输出中。
- `max_group_width` 和 `max_group_depth` 控制**异常组**的格式化（参见 `BaseExceptionGroup`）。`depth` 指分组的嵌套层级，`width` 指一个异常组中异常数组的大小。格式化输出在达到这些限制时会被截断。

> 3.10 版本变更：增加了 `compact` 形参。
> 3.11 版本变更：添加了 `max_group_width` 和 `max_group_depth` 形参。

#### 属性

| 属性 | 说明 | 版本 |
|---|---|---|
| `__cause__` | 原始异常 `__cause__` 所对应的 `TracebackException`（即显式原因的表示）。 | 3.5 |
| `__context__` | 原始异常 `__context__` 所对应的 `TracebackException`（即隐式上下文的表示）。 | 3.5 |
| `exceptions` | 若当前对象代表一个 `ExceptionGroup`，此字段保存由代表被嵌套异常的 `TracebackException` 实例组成的列表；否则为 `None`。 | 3.11 新增 |
| `__suppress_context__` | 来自原始异常的 `__suppress_context__` 值。 | 3.5 |
| `__notes__` | 来自原始异常的 `__notes__` 值；若异常没有任何注释则为 `None`。不为 `None` 时会在异常字符串之后被格式化输出。 | 3.11 新增 |
| `stack` | 代表该回溯的 `StackSummary` 对象。 | 3.5 |
| `exc_type` | 原始异常的类。**自 3.13 起弃用**（请改用 `exc_type_str`）。 | 3.5（3.13 弃用） |
| `exc_type_str` | 原始异常类的字符串显示形式。 | 3.13 新增 |
| `filename` | 针对语法错误——出错所在的文件名。 | 3.5 |
| `lineno` | 针对语法错误——出错所在的行号。 | 3.5 |
| `end_lineno` | 针对语法错误——出错所在的末尾行号；如不存在则为 `None`。 | 3.10 新增 |
| `text` | 针对语法错误——出错所在的源代码文本。 | 3.5 |
| `offset` | 针对语法错误——出错位置在文本内的偏移量。 | 3.5 |
| `end_offset` | 针对语法错误——出错位置在文本内的末尾偏移量；如不存在则为 `None`。 | 3.10 新增 |
| `msg` | 针对语法错误——编译器给出的错误消息。 | 3.5 |

#### 方法

`classmethod from_exception(exc, *, limit=None, lookup_lines=True, capture_locals=False, compact=False, max_group_width=15, max_group_depth=10)`

- 这是一个类方法，从一个异常对象 `exc` 捕获数据，构造 `TracebackException` 实例。参数 `limit`、`lookup_lines`、`capture_locals` 含义与 `StackSummary` 类相同。
- 局部变量被捕获时也会显示在回溯中。

`print(*, file=None, chain=True)`

- 将 `format()` 所返回的异常信息打印到 `file`（默认为 `sys.stderr`）。

> 3.11 版本新增。

`format(*, chain=True)`

- 格式化异常。如果 `chain` 不为 `True`，则 `__cause__` 和 `__context__` 不会被格式化（即不打印异常链）。
- 返回值是一个字符串**生成器**，每个字符串都以换行符结束，有些还包含内部换行符。
- `print_exception()` 实际上是此方法的一个包装器，它只是把这些行打印到文件。

`format_exception_only(*, show_group=False)`

- 只格式化回溯的"异常部分"。返回值是一个字符串生成器，每个字符串都以换行符结束。
- 当 `show_group` 为 `False`（默认）时，生成器输出异常消息及其注释（若有）。异常消息通常是一条字符串；但对于 `SyntaxError`，它由多行组成，打印时能展示语法错误发生位置的详细信息。
- 当 `show_group` 为 `True` 且异常为 `BaseExceptionGroup` 实例时，还会递归包含嵌套异常，并按嵌套深度添加缩进。

> 3.11 版本变更：异常的"注释"现在会被包含在输出中。
> 3.13 版本变更：增加了 `show_group` 形参。

### `StackSummary`

> 3.5 版本新增。

`StackSummary` 对象表示一个**可被格式化的调用栈**。

类本身没有显式的构造方法文档（通常通过下面两个类方法构造）。

#### `classmethod extract(frame_gen, *, limit=None, lookup_lines=True, capture_locals=False)`

根据一个**帧生成器**（例如 `walk_stack()` 或 `walk_tb()` 所返回的对象）构造 `StackSummary` 对象。

- 如果提供了 `limit`，则只从 `frame_gen` 中提取指定数量的帧。
- 如果 `lookup_lines` 为 `False`，则返回的 `FrameSummary` 对象将不会读入它们的源代码行，这可以降低创建 `StackSummary` 的开销（当它不会被实际格式化时很有价值，例如只想拿到行号）。
- 如果 `capture_locals` 为 `True`，则每个 `FrameSummary` 中的局部变量会被捕获为对象表示形式（`repr()` 结果）。

> 3.12 版本变更：当 `capture_locals` 为 `True` 时，局部变量的 `repr()` 若抛出异常，该异常不再被传播给调用方。

#### `classmethod from_list(a_list)`

从所提供的 `FrameSummary` 对象列表**或旧式的元组列表**构造一个 `StackSummary` 对象。每个元组应当是以 `(文件名, 行号, 名称, 行)` 为元素的 4 元组。

#### `format()`

返回一个可打印的字符串列表。结果列表中的每个字符串各自对应栈中的一个单独帧。每个字符串都以换行符结束；对于带有源文本行的条目，字符串内部还可能包含换行符。

> 对于同一帧与行的长序列（例如递归导致的重复），只会显示前几个重复项，后面跟一行摘要，指出之后的实际重复次数。
> 3.6 版本变更：重复帧的长序列现在会被缩减。

#### `format_frame_summary(frame_summary)`

返回用于打印栈中某个单独帧的字符串。`StackSummary.format()` 会为每个要打印的 `FrameSummary` 调用此方法；如果它返回 `None`，则该帧会从输出中被省略（可借此自定义隐藏某些帧）。

> 3.11 版本新增。

### `FrameSummary`

> 3.5 版本新增。

`FrameSummary` 对象表示回溯或栈中的一个单独帧。

#### 构造方法

```
class FrameSummary(filename, lineno, name, *, lookup_line=True, locals=None, line=None, end_lineno=None, colno=None, end_colno=None)
```

表示回溯或栈中被格式化、打印的一个单独帧。它还可以携带该帧局部变量的字符串化版本。

- 如果 `lookup_line` 为 `False`，则源代码不会被查找，直到 `FrameSummary` 的 `line` 属性被访问（在把它转换为 `tuple` 时也会触发查找）。
- `line` 可以被直接提供，一旦提供就会完全阻止行查找的发生。
- `locals` 是一个可选的局部变量映射；如果提供，这些变量的表示形式将被存储在概要中供随后显示。

#### 属性

| 属性 | 说明 |
|---|---|
| `filename` | 对应该帧的源代码文件名，等价于帧对象 `f` 的 `f.f_code.co_filename`。 |
| `lineno` | 对应该帧的源代码行号。 |
| `name` | 等价于访问帧对象 `f` 的 `f.f_code.co_name`（即函数名）。 |
| `line` | 代表该帧源代码的字符串，头尾空白会被去除；若源代码不可用则为 `None`。 |
| `end_lineno` | 该帧源代码的末尾行号。默认值为 `lineno`，索引从 1 开始。 |
| `colno` | 该帧源代码的列号。默认值为 `None`，索引从 0 开始。 |
| `end_colno` | 该帧源代码的末尾列号。默认值为 `None`，索引从 0 开始。 |

> 3.13 版本变更：`end_lineno` 的默认值从 `None` 改为 `lineno`。

## 异常上下文与 `__cause__` / `__context__` / `__suppress_context__`

Python 异常支持"链式异常"机制。当一个异常 A 正在被处理（位于 `except`、`finally` 子句或 `with` 语句中）时，如果又引发了新异常 B，那么解释器会自动做两件事：

1. 把 B 的 `__context__` 属性设为 A。
2. 隐式异常上下文由此建立。

此外，你可以用 `from` 关键字**显式**指定原因：

```python
raise new_exc from original_exc
```

此时 `raise` 之后 `from` 后面的表达式（必须是一个异常或 `None`）会被设为 `new_exc` 的 `__cause__` 属性。设置 `__cause__` 还会**隐式**地把 `new_exc` 的 `__suppress_context__` 属性设为 `True`。这种特性使得 `raise new_exc from None` 能"在显示层面用新异常替换旧异常"（例如把 `KeyError` 转化为 `AttributeError` 展示），同时旧异常仍保留在 `__context__` 中供调试时内省。

回溯显示规则（`traceback` 模块严格遵守，与解释器一致）：

- **显式链接的异常**（`__cause__`）只要存在，就**始终**会被显示。
- **隐式链接的异常**（`__context__`）只有在 `__cause__` 为 `None` 且 `__suppress_context__` 为假值时才会被显示。
- 无论哪种情况，异常本身总是显示在任何链式异常**之后**，因此回溯的最后一行始终是最后被引发的那个异常。

在 `traceback` 模块中，这些关系体现为：

- `print_exception(..., chain=True)` 与 `format_exception(..., chain=True)` / `TracebackException.format(chain=True)`：控制是否递归打印异常链。设 `chain=False` 可只打印最外层异常。
- `TracebackException.__cause__`、`__context__`、`__suppress_context__`：分别是从原始异常复制过来的对应成员（类型也是 `TracebackException` 或布尔值）。

## 代码示例

### 示例 1：在 `except` 块中格式化并捕获当前异常

```python
import traceback

def inner():
    return 1 / 0  # 触发 ZeroDivisionError

def outer():
    inner()

try:
    outer()
except ZeroDivisionError:
    # 方式一：直接打印到 stderr（或指定文件）
    print("=== print_exc ===")
    traceback.print_exc(limit=3)

    # 方式二：格式化为一个字符串，可写入日志
    print("=== format_exc ===")
    text = traceback.format_exc()
    # 只展示首尾两行，验证内容
    lines = text.splitlines()
    print("首行:", lines[0])
    print("末行:", lines[-1])

    # 方式三：格式化为字符串列表，便于逐行处理
    print("=== format_exception ===")
    import sys
    parts = traceback.format_exception(sys.exception())
    print(parts[-1].strip())  # 最后一段是异常类型与消息
```

### 示例 2：用 `TracebackException` 捕获后稍后打印

```python
import traceback

def fail():
    raise ValueError("配置项非法")

try:
    fail()
except ValueError as exc:
    # 捕获异常的轻量表示，不持有对回溯/帧对象的引用
    tb_exc = traceback.TracebackException.from_exception(exc)

# 注意：此处已离开 except 块，异常对象 exc 已超出作用域，
# 但 tb_exc 仍保留足够信息供打印。
print("".join(tb_exc.format()))
```

### 示例 3：提取并打印当前调用栈

```python
import traceback

def level_two():
    # 提取当前调用栈（含本函数内的调用点）
    summary = traceback.extract_stack()
    print("=== extract_stack ===")
    for fs in summary:
        print(f"{fs.filename}:{fs.lineno} in {fs.name}")

    # 使用 walk_stack + StackSummary.extract 得到等价结果
    print("=== walk_stack + StackSummary.extract ===")
    gen = traceback.walk_stack(None)
    summary2 = traceback.StackSummary.extract(gen)
    print("".join(summary2.format()))

def level_one():
    level_two()

level_one()
```

## 版本可用性说明

以下汇总各类、函数与属性在进入标准库时的版本（均以官方文档为准）：

| API | 首次可用版本 | 备注 |
|---|---|---|
| `clear_frames()` | 3.4 | — |
| `walk_stack()` / `walk_tb()` | 3.5 | `walk_stack` 在 3.14 改变了生成器语义 |
| `TracebackException` / `StackSummary` / `FrameSummary` | 3.5 | 面向对象 API 的统一引入 |
| `print_tb` / `print_stack` 的负数 `limit` | 3.5 | — |
| `format_list` / `format_stack` 等 | 3.5 之前已存（随模块早期版本） | 属基础 API |
| `StackSummary.format()` 缩减重复帧 | 3.6 | 行为变更 |
| `print_exception` / `format_exception` 支持直接传异常对象 | 3.10 | `etype` → `exc`（仅限位置） |
| `format_exception_only` 支持直接传异常对象 | 3.10 | 同上 |
| `TracebackException(compact=...)` | 3.10 | — |
| `TracebackException.end_lineno` / `end_offset` | 3.10 | 语法错误定位 |
| `TracebackException.print()` 方法 | 3.11 | — |
| `TracebackException.exceptions` 属性 | 3.11 | 异常组支持 |
| `TracebackException.__notes__` 属性 | 3.11 | 异常注释支持 |
| `format_exception_only` 包含注释 | 3.11 | 行为变更 |
| `TracebackException(max_group_width=..., max_group_depth=...)` | 3.11 | 异常组格式化控制 |
| `StackSummary.format_frame_summary()` | 3.11 | — |
| `StackSummary.extract()` 不传播 `repr()` 异常 | 3.12 | 行为变更 |
| 输出默认带颜色 | 3.13 | 可用环境变量控制 |
| `TracebackException.exc_type_str` | 3.13 | `exc_type` 同时被弃用 |
| `format_exception_only(show_group=...)` | 3.13 | — |
| `FrameSummary.end_lineno` 默认值改为 `lineno` | 3.13 | 之前为 `None` |
| `walk_stack` 生成器反映调用时栈状态 | 3.14 | 行为变更 |

> 说明：`FrameSummary` 的 `colno` / `end_colno` 属性在官方文档中未标注单独版本号，属于该类自 3.5 引入后即具备的属性；`TracebackException` 的 `filename` / `lineno` / `text` / `offset` / `msg` 亦未标注单独版本号（自 3.5 起可用）。`traceback` 模块本身自 Python 早期版本即存在。

## 注意事项与反模式

1. **`limit` 符号语义要分清**：`print_tb` / `print_stack` 的 `limit` 与 `sys.tracebacklimit` 的语义不同。正的 `limit` 是"从调用点起至多 N 条"，负的是"最后 N 条"。不要想当然地把 `sys.tracebacklimit` 的取值直接套用过来。

2. **长期持有异常对象可能导致内存驻留**：异常对象会通过 `__traceback__` 链接到整条栈帧，而栈帧又引用局部变量，形成庞大的对象图。若需要在日志收集、异步任务队列等场景"稍后再打印"，应使用 `TracebackException`（配合 `compact=True` 效果更好）而非保存原始异常对象，这正是该类的设计初衷。

3. **`repr()` 捕获局部变量可能抛异常**：`capture_locals=True` 时会对每个局部变量调用 `repr()`，某些对象的 `__repr__` 可能抛异常。3.12 起这些异常不再传播，但更稳妥的做法是按需开启 `capture_locals`。

4. **不要用 `print_exc` 处理根本没有异常的场景**：`print_exc()` / `format_exc()` 依赖 `sys.exception()`（当前正在处理的异常），若在 `except` 块之外调用可能输出空或产生非预期结果；此时应改用 `print_stack()` / `format_stack()` 或 `extract_stack()`。

5. **`exc_type` 已弃用**：3.13 起 `TracebackException.exc_type` 已弃用，请改用 `exc_type_str`（字符串形式），避免依赖类对象引用带来额外持有成本。

6. **异常组的展示受宽度/深度限制**：`max_group_width`（默认 15）和 `max_group_depth`（默认 10）会截断异常组的格式化输出，诊断深层嵌套异常组时可按需调大。

7. **颜色输出可控但可能污染日志**：3.13 起输出默认带色，写入日志文件或非终端环境时可能混入 ANSI 转义序列，需注意用环境变量（如 `PYTHON_COLORS=0`）或 `NO_COLOR` 关闭。

## 与 dataclasses 的简要关系

`dataclasses` 用于以声明式方式构建轻量的数据容器类，而 `traceback` 用于诊断运行期错误；两者同属 Python 3.14 标准库，本系列教程将二者并列，恰好覆盖了"定义数据结构"与"排查运行时异常"这组互补的日常任务。

## 章节导航

- [上一章：dataclasses](06-dataclasses.md) →
- [下一章：跨模块综合分析](08-cross-module-analysis.md) →