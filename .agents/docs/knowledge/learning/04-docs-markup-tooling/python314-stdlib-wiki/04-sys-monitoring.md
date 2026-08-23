---
id: "python314-stdlib-wiki-04"
title: "Python 3.14 标准库 sys.monitoring 全面详解"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/04-sys-monitoring.toml"
---

# Python 3.14 标准库 sys.monitoring 全面详解

> 一句话摘要：`sys.monitoring` 是 Python 3.12 起提供的低开销、事件驱动的运行时监控命名空间，它用「工具标识符 + 事件集合 + 回调」三要素让调试器、覆盖率工具、性能分析器等按需订阅执行事件，相比传统的 `sys.settrace`/`sys.setprofile` 在性能与可控粒度上都有本质提升。

## 1. 模块定位与用途

`sys.monitoring` 并不是一个独立的模块，而是内嵌于 [`sys`](https://docs.python.org/3.14/library/sys.html) 模块内部的一个**命名空间**。这一点极其关键：`import sys.monitoring` 与 `from sys.monitoring import events` 都会抛出 `ModuleNotFoundError`。正确的使用方式永远是：

```python
import sys

events = sys.monitoring.events   # 先取命名空间，再使用其属性
```

该命名空间提供了激活和控制「执行事件监控」所需的函数与常量。当程序运行时会不断发生各类事件（函数调用、返回、行号推进、虚拟字节码指令执行、异常抛出等），`sys.monitoring` 允许工具在感兴趣的事件发生时收到回调。

监控 API 由三个组成部分构成：

| 组成部分 | 作用 |
|---|---|
| 工具标识符（Tool identifiers） | 一个 0~5 的整数及其关联名称，用于隔离不同工具，防止互相干扰 |
| 事件（Events） | 用 2 的幂整数常量表示的可订阅运行时事件 |
| 回调（Callbacks） | 事件触发时被调用的 Python 可调用对象 |

### 相对 `sys.settrace` / `sys.setprofile` 的优势

`sys.monitoring` 是 [PEP 669](https://peps.python.org/pep-0669/) 的产物，其设计目标是取代旧有的跟踪/分析机制，主要优势在于：

- **按需注册的事件**：旧机制里 `sys.settrace` 的跟踪函数会对每一行、每一次调用都被调用，哪怕你只关心函数返回；新机制只在你显式开启的事件上触发回调。
- **局部事件关闭**：通过从回调返回 `sys.monitoring.DISABLE`，可以在「特定代码位置」永久关闭事件，已探测过的位置不再产生任何开销。
- **事件的可组合位掩码**：事件用 2 的幂整数表示，可用按位或（`|`）自由组合出需要的事件集合。
- **中断安全 / 开销可控**：官方文档明确写了这样一句话——如果调试器把除少数断点之外的所有监控都禁用，那么「程序在调试器下运行将不产生额外开销」。这是旧机制无法做到的。
- **独立于 `sys.settrace`**：二者可以共存，`sys.monitoring` 不会被 `sys.settrace` 的全局跟踪所干扰（反之亦然，语义上彼此独立）。

## 2. 核心术语表

以下术语均用平实语言解释，避免用术语解释术语：

| 术语 | 一句话平实解释 |
|---|---|
| 事件（event） | 程序运行到某个位置、执行某个动作时产生的信号，例如「某个函数开始执行」「某行代码即将执行」。 |
| 工具（tool） | 使用这套监控能力的一个程序或组件，例如调试器、覆盖率统计器、性能分析器。 |
| 工具 ID（tool identifier） | 一个 0~5 之间的整数编号，还带一个名称，用来让不同工具各用各的编号、互不打架。 |
| 回调（callback） | 你写的一段函数；当某个已开启的事件发生时，解释器会调用它，并传入该事件相关的参数。 |
| 全局事件（global event） | 对整个程序都开启的事件，无论代码在哪，触发时都会调用回调。 |
| 局部事件（local event） | 只对某个特定的代码对象开启的事件，只在那个函数/代码执行时才触发。 |
| 中断（discontinuity） | 通过回调返回 `DISABLE` 后，某个具体代码位置的事件被关闭，形成监控流中的一个「断点」；可再通过 `restart_events()` 统一恢复。 |
| 事件集合（event set） | 用按位或把多个事件整数拼起来得到的一把「开关位图」，用于一次性开启/关闭多个事件。 |
| 辅助事件（ancillary event） | 自身能被订阅、但受另一个事件控制才可见的事件，例如 `C_RETURN` 只有 `CALL` 被监控时才可见。 |

## 3. 工具 ID 管理

工具 ID 是 0（含）到 5（含）闭区间内的整数。**同一时间最多只能有 6 个工具**。在使用任何工具 ID 之前，都必须先「登记」它。

### `use_tool_id(tool_id, name, /)` → None

```python
sys.monitoring.use_tool_id(tool_id: int, name: str, /) -> None
```

- 在 `tool_id` 可被使用之前**必须**调用。
- `tool_id` 必须在 0~5 闭区间内。
- **`name` 是必填参数**（本教程依据 3.14.7 实测：省略会抛出 `TypeError: use_tool_id expected 2 arguments, got 1`）。它作为该工具的名称，可在后续通过 `get_tool()` 查询，便于调试与协作。
- 如果 `tool_id` **已被占用**，抛出 `ValueError`。
- 错误处理要点：尝试占用一个已登记的 ID，或传入超出 0~5 范围的 ID，都会得到 `ValueError`。

### `clear_tool_id(tool_id, /)` → None

```python
sys.monitoring.clear_tool_id(tool_id: int, /) -> None
```

注销与该 `tool_id` 关联的**所有**事件与回调函数（但不清除名称，也不释放 ID 本身）。

### `free_tool_id(tool_id, /)` → None

```python
sys.monitoring.free_tool_id(tool_id: int, /) -> None
```

应在工具不再需要该 `tool_id` 时调用。在释放 `tool_id` 之前，它会**先自动调用 `clear_tool_id()`**。

### `get_tool(tool_id, /)` → str | None

```python
sys.monitoring.get_tool(tool_id: int, /) -> str | None
```

- 如果 `tool_id` 已被使用，返回其名称（字符串）；否则返回 `None`。
- `tool_id` 必须在 0~5 闭区间内。

### 预定义的工具 ID

虚拟机处理事件时对所有 ID 一视同仁，但为便于工具之间协作，预定义了以下 ID：

```python
sys.monitoring.DEBUGGER_ID  = 0   # 调试器
sys.monitoring.COVERAGE_ID  = 1   # 覆盖率工具
sys.monitoring.PROFILER_ID  = 2   # 性能分析器
sys.monitoring.OPTIMIZER_ID = 5   # 优化器
```

> 编号 3 与 4 留给自定义工具。本教程的示例统一使用 `3` 或 `4`，避免与预定义 ID 冲突。

## 4. 事件类型详解

以下逐一解释 `sys.monitoring.events` 命名空间中受支持的事件。全部名称与语义均以 Python 3.14 官方文档为准。

需要先行理解的两条通用规则：

1. 每个事件都是 **2 的幂整数常量**，多个事件可用按位或组合，例如 `PY_START | PY_RETURN` 表示同时选中两个事件。
2. 事件的完整状态用「事件集合」表示——某个事件是否开启，取决于该事件对应的二进制位是否被置位。

### 4.1 Python 函数事件

| 事件 | 含义（文档原文语义） | 触发时机补充 |
|---|---|---|
| `PY_START` | 开始一个 Python 函数 | 在函数被调用之后**立即**发生，此时被调用方的帧已在调用栈中 |
| `PY_RETURN` | 从一个 Python 函数返回 | 在 return 之前**立即**发生，被调用方的帧仍在栈中 |
| `PY_YIELD` | 从一个 Python 函数产出数据 | 在 yield 之前**立即**发生，被调用方的帧仍在栈中 |
| `PY_RESUME` | 恢复执行一个 Python 函数（用于生成器与协程函数） | 不含 `throw()` 调用引发的恢复 |
| `PY_THROW` | 一个 Python 函数由 `throw()` 调用恢复执行 | 与 `PY_RESUME` 互补，专指 `throw()` 路径 |
| `PY_UNWIND` | 在异常展开期间从一个 Python 函数退出 | 包括在该函数内直接引发、且被允许继续向外传播的异常 |

### 4.2 指令级事件（VM 指令与控制流）

| 事件 | 含义（文档原文语义） |
|---|---|
| `LINE` | 一条**与上一条指令行号不同**的指令即将被执行（即实际推进到了新的一行） |
| `INSTRUCTION` | 一条虚拟机（VM）指令即将被执行 |
| `JUMP` | 在控制流图中发生一次**无条件**跳转 |
| `BRANCH_LEFT` | 条件分支向左（3.14 新增） |
| `BRANCH_RIGHT` | 条件分支向右（3.14 新增） |
| `BRANCH` | 条件分支（**3.14 已弃用**，请改用 `BRANCH_LEFT`/`BRANCH_RIGHT`） |

关于 `BRANCH` 的说明：它虽然仍存在于命名空间中，但已在 3.14 被标记弃用。官方文档指出，改用 `BRANCH_LEFT` 与 `BRANCH_RIGHT` 能获得更好性能，因为这两个事件「可以分别独立禁用」。

关于「左 / 右」的约定：如何呈现「左」「右」分支由工具自行决定；无法保证哪个分支是「左」、哪个是「右」，唯一保证的是**在程序运行的整个持续时间里它是一致的**。

### 4.3 关于 `MARKER` 事件的重要澄清

一些资料可能提到 `sys.monitoring.events.MARKER`（标记事件）。**在 Python 3.14 的官方文档中并不存在该事件**，本教程在 3.14.7 上实测 `sys.monitoring.events` 的属性列表也不包含 `MARKER`。因此编写针对 3.14 的监控代码时，请不要依赖 `MARKER`；若有需要，请查阅你所用具体版本的最新文档确认其是否已加入。

### 4.4 调用与 C 边界事件

| 事件 | 类别 | 含义（文档原文语义） |
|---|---|---|
| `CALL` | 局部事件 | Python 代码中的一次调用（事件在调用**之前**发生） |
| `C_RETURN` | 辅助事件 | 从任意可调用对象返回，**Python 函数除外**（事件在返回**之后**发生） |
| `C_RAISE` | 辅助事件 | 从任意可调用对象引发异常，**Python 函数除外**（事件在退出**之后**发生） |

`C_RETURN` 与 `C_RAISE` 属于**辅助事件**：它们虽然能像其他事件一样被监控，但受 `CALL` 事件控制——只有当对应的 `CALL` 事件正在被监控时，`C_RETURN` / `C_RAISE` 才会被看到。

### 4.5 异常事件

| 事件 | 含义（文档原文语义） |
|---|---|
| `RAISE` | 一个异常被引发（**排除**那些会导致 `STOP_ITERATION` 事件的异常） |
| `RERAISE` | 一个异常被重新引发，例如在 `finally` 代码块结束时 |
| `EXCEPTION_HANDLED` | 一个异常被处理 |
| `STOP_ITERATION` | 一个人工的 `StopIteration` 被引发（见下节详解） |

### 4.6 `STOP_ITERATION` 事件的来龙去脉

[PEP 380](https://peps.python.org/pep-0380/#use-of-stopiteration-to-return-values) 规定：从生成器或协程返回值时，会天然地引发 `StopIteration` 异常。但这种返回值方式非常低效，因此包括 CPython 3.12+ 在内的部分实现，只在该异常「对外可见」时才真正引发它。

为了让工具在不拖慢生成器/协程的前提下仍能监控到真实异常，就有了 `STOP_ITERATION` 事件。它的特点是：

- **可以被局部禁用**（`RAISE` 事件则不能）。
- `STOP_ITERATION` 事件与 `StopIteration` 异常的 `RAISE` 事件**等价**，在生成事件时被视为可互换。实现出于性能考虑会优先选择 `STOP_ITERATION`，但也可能用 `StopIteration` 生成 `RAISE` 事件。

### 4.7 特殊值：`NO_EVENTS`、`DISABLE`、`MISSING`

| 特殊值 | 含义 |
|---|---|
| `sys.monitoring.events.NO_EVENTS` | 整数 `0` 的别名，方便写出 `if get_events(id) == NO_EVENTS:` 这样的显式比较；把它设为事件集合会**撤销所有事件的激活** |
| `sys.monitoring.DISABLE` | 可从回调函数返回的特殊值，用于**禁用当前代码位置**的事件 |
| `sys.monitoring.MISSING` | 传给回调函数的特殊值，表示「本次调用不附带任何参数」 |

**`DISABLE` 的特殊语义**：只有**局部事件**能在指定代码位置被禁用。从回调返回 `DISABLE` 不会改变已设置的事件集合，也不会影响同一事件在其他代码位置的状态；它只是让「这一处位置」之后不再触发。可从回调返回 `DISABLE` 即可实现高性能监控。

**`MISSING` 的特殊语义**：它只出现在 `CALL`/`C_RETURN`/`C_RAISE` 的回调签名里，用于「被调用对象没有参数」的情形（详见第 6 节）。

## 5. 事件集合与查询

### `events` 命名空间

所有事件常量都是 `sys.monitoring.events` 命名空间的属性。**请注意**：该命名空间**并没有** `__version__` 属性（3.14.7 实测 `hasattr(sys.monitoring.events, '__version__')` 为 `False`），一切以事件常量本身为准。

### `get_events(tool_id, /)` → int

```python
sys.monitoring.get_events(tool_id: int, /) -> int
```

返回代表该工具**所有活跃事件**的整数（位掩码）。可用 `&` 判断某个事件是否已开启，或用 `== events.NO_EVENTS` 判断「一个事件都没开」。

### `set_events(tool_id, event_set, /)` → None

```python
sys.monitoring.set_events(tool_id: int, event_set: int, /) -> None
```

激活 `event_set` 中所有已置位的事件。如果 `tool_id` **未在 use_tool_id 中登记**，抛出 `ValueError`。默认情况下没有任何事件被激活。

### `get_local_events(tool_id, code, /)` → int

```python
sys.monitoring.get_local_events(tool_id: int, code: types.CodeType, /) -> int
```

返回对 `code` 生效的**所有局部事件**（位掩码）。

### `set_local_events(tool_id, code, event_set, /)` → None

```python
sys.monitoring.set_local_events(tool_id: int, code: types.CodeType, event_set: int, /) -> None
```

为 `code` 激活 `event_set` 中所有已置位的**局部事件**。如果 `tool_id` 未登记，抛出 `ValueError`。

### `restart_events()` → None

```python
sys.monitoring.restart_events() -> None
```

**重新启用**之前被 `DISABLE` 针对所有工具关闭的所有事件。

> 注意：官方文档与 3.14.7 实测中，查询/设置局部事件只提供 `get_local_events` / `set_local_events` 两个函数，**不存在**名为 `local_events` 的独立属性。

### 事件分类速查

| 分类 | 包含的事件 | 能否用 `DISABLE` 逐个关闭 |
|---|---|---|
| 局部事件（local） | `PY_START`、`PY_RESUME`、`PY_RETURN`、`PY_YIELD`、`CALL`、`LINE`、`INSTRUCTION`、`JUMP`、`BRANCH_LEFT`、`BRANCH_RIGHT`、`STOP_ITERATION` | 可以 |
| 辅助事件（ancillary） | `C_RETURN`、`C_RAISE` | 受 `CALL` 控制 |
| 其他事件（other） | `PY_THROW`、`PY_UNWIND`、`RAISE`、`EXCEPTION_HANDLED` | 不能 |

> `RERAISE` 是受支持的事件之一，其回调签名与 `RAISE` 等异常事件一致（见下节）；官方文档在「其他事件」小节只列出了上述四个名称，这里按文档原文如实呈现。

## 6. 回调注册与回调签名

### `register_callback(tool_id, event, func, /)` → Callable | None

```python
sys.monitoring.register_callback(tool_id: int, event: int, func: Callable | None, /) -> Callable | None
```

- 用给定的 `tool_id` 为 `event` 注册可调用对象 `func`。
- 如果同一 `tool_id` + 同一 `event` **已经注册过另一个回调**，旧回调会被注销并**作为返回值返回**；其他情况下返回 `None`。这等价于「同一工具的同一事件**只能有一个回调**，重复注册会替换，而非叠加」。
- 该调用会触发审计事件 `sys.monitoring.register_callback`，附带参数 `func`。
- 传入 `func=None` 可注销：`register_callback(tool_id, event, None)`。
- 回调可以在**任何时刻**注册或注销。
- 一个事件**只会触发一次**，即使它在全局与局部同时开启。因此若你的代码可能同时全局、局部开启某个事件，回调要写成能同时处理两种触发来源。

### 回调函数参数

当一个已激活的事件发生时，已注册的回调会被调用。回调返回**除 `DISABLE` 之外**的任何对象都没有任何效果。各事件的回调签名如下：

**（1）`PY_START` 与 `PY_RESUME`**

```python
func(code, instruction_offset)
```

**（2）`PY_RETURN` 与 `PY_YIELD`**

```python
func(code, instruction_offset, retval)
```

**（3）`CALL`、`C_RAISE` 与 `C_RETURN`**（其中 `arg0` 可为 `MISSING`）

```python
func(code, instruction_offset, callable, arg0)
```

- `code`：发起调用的那个代码对象；
- `callable`：即将被调用的对象（即触发事件的那个对象）；
- `arg0`：被调用对象的第一个参数；**若调用没有参数，则 `arg0` 为 `sys.monitoring.MISSING`**；
- 对实例方法而言，`callable` 是类上找到的函数对象，`arg0` 是该实例（即方法的 `self` 参数）。

**（4）`RAISE`、`RERAISE`、`EXCEPTION_HANDLED`、`PY_UNWIND`、`PY_THROW` 与 `STOP_ITERATION`**

```python
func(code, instruction_offset, exception)
```

**（5）`LINE`**

```python
func(code, line_number)
```

**（6）`BRANCH_LEFT`、`BRANCH_RIGHT` 与 `JUMP`**

```python
func(code, instruction_offset, destination_offset)
```

> `destination_offset` 是代码**下一步将执行的位置**。

**（7）`INSTRUCTION`**

```python
func(code, instruction_offset)
```

## 7. 代码对象相关

凡接收 `types.CodeType` 参数的函数（`get_local_events`、`set_local_events`），应当做好接受「并非由 Python 定义、但长得类似」对象的准备（参见 CPython 的 [Monitoring C API](https://docs.python.org/3.14/c-api/monitoring.html)）。也就是说，编码时不要把 `code` 严格假定为 `types.CodeType` 的实例。

在纯 Python 场景下，最常用的做法是通过函数的 `__code__` 属性拿到代码对象：

```python
def foo():
    pass

foo.__code__            # 函数的代码对象
C.method.__code__       # 绑定方法对应的函数代码对象
```

而对于属性（property）、描述符等，可借助其底层函数对象取得代码对象，例如：

```python
type(C).prop.fget.__code__   # property 的 getter 函数代码对象
type(C).prop.fset.__code__   # property 的 setter 函数代码对象
```

> 简言之：任何有 `__code__` 的函数对象，其 `.__code__` 都能直接作为局部事件 API 的 `code` 参数。

## 8. 可运行示例

以下示例在 Python 3.14.7 上运行通过，代码为完整可执行片段。

### 8.1 最小监控：统计 `PY_START` / `PY_RETURN`

```python
import sys

events = sys.monitoring.events

counts = {"start": 0, "return": 0}

def on_start(code, instruction_offset):
    counts["start"] += 1

def on_return(code, instruction_offset, retval):
    counts["return"] += 1

# 1. 登记工具 ID（用 4，避开预定义的 0/1/2/5）
sys.monitoring.use_tool_id(4, "quick-profiler")

# 2. 全局开启 PY_START | PY_RETURN 事件
sys.monitoring.set_events(4, events.PY_START | events.PY_RETURN)

# 3. 分别注册两个事件的回调
sys.monitoring.register_callback(4, events.PY_START, on_start)
sys.monitoring.register_callback(4, events.PY_RETURN, on_return)

def add(a, b):
    return a + b

add(1, 2)
print(counts)   # {'start': 1, 'return': 1}

# 4. 用完释放工具 ID
sys.monitoring.free_tool_id(4)
```

### 8.2 按代码对象开启局部事件 + `DISABLE` 优化

```python
import sys

events = sys.monitoring.events

hits = []

def on_line(code, line_number):
    hits.append(line_number)
    return sys.monitoring.DISABLE   # 该行只报告一次，之后本地关闭

sys.monitoring.use_tool_id(3, "line-tracer")
sys.monitoring.register_callback(3, events.LINE, on_line)

def target():
    x = 1
    y = 2
    return x + y

# 只对 target 的代码对象开启 LINE 局部事件（不污染其他代码）
sys.monitoring.set_local_events(3, target.__code__, events.LINE)

target()
print(hits)                     # [36, 37, 38]  （行号取决于源码位置）

target()                        # 由于上一轮被 DISABLE 关闭，不再触发
print(hits)                     # 仍是 [36, 37, 38]

sys.monitoring.restart_events() # 重新启用被 DISABLE 的事件
target()                        # 再次触发三行
print(hits)                     # [36, 37, 38, 36, 37, 38]

sys.monitoring.free_tool_id(3)
```

### 8.3 `CALL` 事件与 `MISSING`，以及工具管理

```python
import sys

events = sys.monitoring.events

seen = []

def on_call(code, instruction_offset, callable, arg0):
    seen.append((getattr(callable, "__name__", repr(callable)), arg0))

sys.monitoring.use_tool_id(4, "call-watcher")
print(sys.monitoring.get_tool(4))   # 'call-watcher'

sys.monitoring.register_callback(4, events.CALL, on_call)
sys.monitoring.set_events(4, events.CALL)

def foo(x=42):
    return x

foo()        # 无实参：arg0 为 sys.monitoring.MISSING
foo(7)       # 有实参：arg0 为 7

result = seen[:]                     # 切片不触发 CALL，先取出记录
sys.monitoring.free_tool_id(4)

print([(name, arg) for name, arg in result])
# [('foo', <MISSING 对象>), ('foo', 7)]
print(result[0][1] is sys.monitoring.MISSING)   # True
```

> 示例 3 里刻意用 `seen[:]` 切片（而非函数调用）在释放工具前取出记录，是因为全局开启 `CALL` 后，所有 Python 代码中的调用（包括对 `print`、`free_tool_id` 等内置/绑定对象的调用）都会触发回调；若在监控区间内调用函数，这些调用本身也会被记录，从而「污染」输出。

## 9. 版本可用性与演进

- **3.12 引入**：`sys.monitoring` 随 [PEP 669](https://peps.python.org/pep-0669/) 进入标准库，提供了低开销的监视事件框架与工具 ID 机制。
- **3.13**：事件集合与 3.12 基本保持一致（仍只有 `BRANCH` 一个条件分支事件），主要是在底层补充了生成 PEP 669 监控事件的 `PyMonitoring` C API。
- **3.14**：新增 `BRANCH_LEFT` 与 `BRANCH_RIGHT` 两个事件，用于替代旧的 `BRANCH` 事件，并将 `BRANCH` 标记为弃用（由 Mark Shannon 在 gh-122548 中贡献）。弃用理由是可以分别独立禁用这两个新事件，从而获得更好性能。

> 使用前请确认运行环境为 Python 3.12 及以上；在 3.11 及更早版本中该 API 不存在。

## 10. 性能与限制

- **开销可控、可趋近于零**：官方文档指出，只要调试器把除少数断点外的监控全部禁用，程序在调试器下运行即可做到「零额外开销」。关键在于善用局部事件与 `DISABLE`。
- **`INSTRUCTION` 开销最大**：它会在每条 VM 指令执行前触发，属于最细粒度的监控，仅应在确有必要时开启。
- **工具数量上限**：仅 6 个工具 ID（0~5），用完必须 `free_tool_id` 释放；忘记释放会长时间占用有限的 ID。
- **同一事件只能有一个回调**：同一 `tool_id` 的同一 `event` 重复注册会替换旧回调（并返回旧回调），不会叠加执行。
- **全局事件回调不能返回 `DISABLE`**：为「全局事件」返回 `DISABLE` 会让解释器在**非特定位置**抛出 `ValueError`（不提供 traceback）。`DISABLE` 只对局部事件有效。
- **回调返回值**：返回除 `DISABLE` 之外的任意对象均无任何效果。
- **回调的重入与安全**：回调期间执行的代码是否会再次触发同一工具的事件，官方文档未给出明确的重入保证。编写回调时应保持逻辑简单、无副作用，避免在回调中做昂贵或有状态的操作；并注意全局开启的事件回调可能在不同线程中被调用（监控是解释器进程级的）。

## 11. 注意事项 / 反模式

- ❌ 不要写 `import sys.monitoring` 或 `from sys.monitoring import events`：二者都会 `ModuleNotFoundError`。正确写法是 `import sys` 后使用 `sys.monitoring` 与 `sys.monitoring.events`。
- ❌ 不要在未 `use_tool_id` 登记的情况下调用 `set_events` / `set_local_events`：会抛 `ValueError`。
- ❌ 不要忘记 `use_tool_id` 的 `name` 是必填参数（3.14.7 实测省略即报 `TypeError`）。
- ❌ 不要依赖 3.14 中不存在的 `MARKER` 事件或 `events.__version__` 属性。
- ❌ 不要在全局事件的回调里返回 `DISABLE`。
- ❌ 不要依赖「同一事件的多个回调」：重复注册只保留最后一个（前一个被替换返回）。
- ⚠️ 全局开启 `CALL`/`INSTRUCTION` 等高频事件会产生大量回调（连 `print` 也会被计入），仅对关心的函数使用**局部事件**以降低噪声。
- ⚠️ 用完工具后 `free_tool_id`，避免耗尽 6 个 ID。
- ⚠️ 事件若全局与局部同时开启，仍**只触发一次**，回调要能处理两种来源。

## 12. 与 contextvars 在异步监控场景的关系

`sys.monitoring` 的事件与回调是「全局 / 代码对象」维度的，它本身**不区分异步任务**。在 `asyncio` 场景中，多个协程任务可能在同一条执行流上交错运行，同一个监控回调会在不同任务的上下文中被反复触发。

若希望「按任务」归因或隔离监控状态，可结合上一章的 [`contextvars`](https://docs.python.org/3.14/library/contextvars.html) 使用：`asyncio` 为每个任务维护独立的 context，回调被调用时可通过 `ContextVar.get()` 读取当前任务专属的状态，从而把监控数据正确归因到对应的逻辑流，而不是混在同一个全局计数里。二者互补：`sys.monitoring` 负责「何时、何地触发」，`contextvars` 负责「当前属于谁的上下文」。

## 13. 章节导航

- [上一章：contextvars](03-contextvars.md) →
- [下一章：annotationlib](05-annotationlib.md) →