---
id: "python314-stdlib-wiki-10"
title: "Python 3.14 标准库教程 — FAQ 与排错"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/10-faq-troubleshooting.toml"
---
# Python 3.14 标准库教程 — FAQ 与排错

> 一句话摘要：本章以问答形式，分"运行时动态机制""`dataclasses`""`traceback`"三组，集中解答六模块在使用中的高频疑问，并给出常见错误信息与对策表，帮助你快速定位并解决问题。

## 一、运行时动态机制（`contextlib` / `contextvars` / `sys.monitoring` / `annotationlib`）常见问题

### Q1：`sys.monitoring` 有哪些线程/数量限制？性能开销到底大不大？

**A：** 需要从"数量"与"开销"两方面理解（均源自 04 章）：

**数量/线程限制：**

- **工具 ID 上限**：一套程序同一时刻最多 6 个工具（ID 取 0~5 闭区间）。用完应 `free_tool_id` 释放，否则会长时间占用有限的 ID。
- **每工具每事件仅一个回调**：同一 `tool_id` 的同一 `event` 重复注册会"替换"旧回调（旧回调作为返回值返回），而不会叠加执行。
- **线程**：监控是**解释器进程级**的，全局开启的事件回调可能在不同线程中被调用；回调期间是否会再次触发同一工具事件，官方文档未给出明确的重入保证。

**性能开销：**

- 关键是"按需 + `DISABLE`"：只要只开你关心的事件（尤其用**局部事件**而非全局事件），并在回调中返回 `sys.monitoring.DISABLE` 关闭已探测位置，官方指出当调试器把除少数断点外的监控全部禁用时，**程序运行可做到零额外开销**。
- 最昂贵的是 `INSTRUCTION` 事件——它会在每条 VM 指令执行前触发，属最细粒度监控，非必要不要开启。全局开启 `CALL`/`INSTRUCTION` 等高频事件会产生海量回调（连 `print` 也会被计入）。

### Q2：在 asyncio 中如何正确使用 `contextvars`？`Token` 忘了 `reset` 会怎样？

**A：** 正确用法归纳为四条：

1. **在模块顶层声明 `ContextVar`**，绝不要在闭包中创建（`Context` 持有强引用，闭包内创建会导致变量无法被 GC 回收）。
2. **不必手动"传播"**：`asyncio` 中每个 Task 创建/调度时会**自动复制当前上下文**，因此 Task 内的 `ctx.set()` 不会泄漏到其他 Task，也不影响创建它的协程。
3. **务必还原**：`set()` 返回的 `Token` 是用来还原的凭据。若忘了 `reset()`（又未使用 3.14 的 `with` 写法），旧值会残留在当前上下文；对长生命周期任务尤其危险。**推荐写法**（3.14 起）是 `with var.set(value):`，或退而求其次用 `try/finally`。
4. **同一个 `Token` 只能 `reset` 一次**，重复使用会出错；另外，进入一个"已经被进入"的上下文会抛 `RuntimeError`。

> 典型坑：把 `ContextVar` 当线程局部用、在闭包里创建、或用 `threading.local()` 替代——后者无法按 asyncio 任务隔离（多协程跑在同一线程）。

### Q3：`annotationlib` 与 `typing.get_type_hints` 有什么区别？

**A：** 官方指出 `get_type_hints()` **通常与 `get_annotations()` 相同**，但会额外做四件"类型系统语义"加工：

1. **解析前向引用**：把字符串/代理形式的前向引用在 `globalns`/`localns`（及类型形参命名空间）中求值；
2. **替换 `None`**：把 `None` 换成 `types.NoneType`；
3. **合并基类注解**：若 `obj` 是类，沿 `__mro__` 合并各基类与自身的注解；
4. **递归展开特殊结构**：把 `Annotated`/`Required`/`NotRequired`/`ReadOnly` 展开为内层 `T`（除非 `include_extras=True`）。

定位差异：`annotationlib.get_annotations()` 是**底层、格式可控、不做类型系统加工**的内省原语（支持 VALUE/FORWARDREF/STRING 三种格式，每次返回新字典）；`get_type_hints()` 是**其上的便捷封装**。需要最原始注解数据用前者的 `get_annotations()`；需要可直接用于类型检查的整理结果用 `get_type_hints()`。二者作为内省入口都可能执行注解中的代码，安全风险相同。

### Q4：`ExitStack` 和嵌套 `with` 该选哪个？

**A：** 按场景选择：

- **数量固定且已知**：直接用嵌套 `with` 或 `with A(), B()`，可读性最好。
- **数量可变/由输入驱动**（如打开用户指定的一组文件）、**需要"全有或全无"**、或**需要在 `__enter__` 失败时也清理已分配资源**：用 `ExitStack`。
- `ExitStack` 还能接纳**不原生支持上下文协议**的资源（用 `stack.callback(cleanup, ...)`），以及借助 `pop_all()` 实现"先全部注册、失败自动回滚、成功则延后统一关闭"。

注意：`ExitStack` 是**可重用但不可重入**的——不要嵌套使用同一个实例（内层 `with` 结束会提前清空栈），嵌套场景应各自创建新实例。

### Q5：在旧版本误用 `sys.monitoring` 或 `annotationlib` 会怎样？

**A：** 主要变现为两类异常：

- `import annotationlib` 在 **<3.14** 环境抛 `ModuleNotFoundError: No module named 'annotationlib'`。
- `sys.monitoring` 在 **<3.12** 环境不存在——`sys.monitoring` 会抛 `AttributeError: module 'sys' has no attribute 'monitoring'`。
- 更隐蔽的是 `sys.monitoring.events.BRANCH_LEFT`/`BRANCH_RIGHT`：它们在 **<3.14** 中不存在，访问会抛 `AttributeError`（3.13 及以前只有 `BRANCH`）。
- `contextvars.Token` 作为上下文管理器是 3.14 才有的能力，在旧版本中把它用于 `with` 会抛异常。

对策：动手前先跑 `sys.version_info` 检查版本（见 [01 版本背景](01-version-prerequisites.md)）；或对 `annotationlib` 使用 `typing-extensions` 的 `get_annotations()` 向后移植。

## 二、`dataclasses` 常见问题

### Q1：为什么给字段写 `x: list = []` 会报错？

**现象**：

```python
from dataclasses import dataclass

@dataclass
class C:
    x: list = []   # ValueError: mutable default <class 'list'> for field x is not allowed
```

**原因**：普通 Python 会把默认值存在类属性里，导致所有实例共享同一个可变对象；`@dataclass` 在检测到不可哈希（通常即"可变"）的默认值时直接抛出 `ValueError`（3.11 起统一按"不允许不可哈希对象"判断）。

**对策**：改用 `field(default_factory=list)`，让每个实例在需要默认值时都调用一次工厂函数，生成全新的对象。

```python
from dataclasses import dataclass, field

@dataclass
class C:
    x: list = field(default_factory=list)
```

### Q2：为什么我的 `frozen=True` 数据类在 `__post_init__` 里赋值会报错？

**现象**：`frozen=True` 会生成只读的 `__setattr__`，普通赋值抛 `FrozenInstanceError`。

**对策**：在 `__post_init__` 内用 `object.__setattr__(self, name, value)` 完成一次性初始化（绕过冻结限制）。这是官方文档推荐的写法。

### Q3：为什么我定义了 `hash=False` 的字段，但比较仍然用到了它？

**原因**：`hash=False` 只影响字段是否参与生成 `__hash__()`，**不影响** `__eq__` 等比较方法；只要 `compare=True`，该字段仍参与比较。要同时排除比较与哈希，应同时设置 `compare=False`。

### Q4：`slots=True` 之后，为什么 `__slots__` 里看不到继承来的字段？

**现象**：某字段名若已包含在基类的 `__slots__` 中，它不会出现在派生子类新生成的 `__slots__` 里（3.11 起），以避免覆写。

**对策**：不要用 `__slots__` 读取字段名，一律改用 `fields()`。

### Q5：`replace()` 对 `init=False` 字段的行为是什么？

**说明**：`replace()` 新对象通过调用 `__init__()` 创建，`init=False` 的字段不在参数列表里，也不会从源对象拷贝，而是在 `__post_init__`（若有）里初始化。若 `changes` 里出现 `init=False` 的字段名，会抛 `ValueError`。建议尽量少用 `init=False` 字段。

### Q6：`order=True` 时为什么报 `ValueError` / `TypeError`？

- `order=True` 且 `eq=False` → 抛 `ValueError`。
- 类里已经定义了 `__lt__` 等任一比较方法 → 抛 `TypeError`。

### Q7：`dataclasses` 什么时候会真正检查字段的类型注解？

**说明**：仅在识别 `ClassVar` 与 `InitVar` 这两类伪字段时会检查注解；除此之外，`@dataclass` 不校验你写的是 `int` 还是别的什么——类型标注主要供类型检查器与 IDE 使用。

## 三、`traceback` 常见问题

### Q1：`print_tb` 的 `limit` 和 `sys.tracebacklimit` 是一个东西吗？

**不是**。`print_tb`/`print_stack` 的 `limit`：正数表示"从调用点起至多 N 条"，负数表示"最后 N 条"；而 `sys.tracebacklimit` 的语义与之不同（负的 `limit` 对应于正的 `sys.tracebacklimit`，正的 `limit` 的效果无法用 `sys.tracebacklimit` 表达）。不要想当然互相套用。

### Q2：为什么我把异常对象存进列表，一段时间后内存涨得厉害？

**原因**：异常对象通过 `__traceback__` 链到整条栈帧，栈帧又引用局部变量，形成庞大的对象图；长期持有异常对象会拖住这些对象不被回收。

**对策**：需要"稍后再打印"时，用 `TracebackException.from_exception(exc)`（配 `compact=True` 更省）保存轻量表示，而非保存异常对象本身。

### Q3：`capture_locals=True` 时为什么偶尔报异常或结果异常？

**原因**：`capture_locals=True` 会对每个局部变量调用 `repr()`，某些对象的 `__repr__` 可能抛异常。3.12 起这些异常不再传播，但更稳妥的做法是按需开启。

### Q4：在不处于 `except` 块时调用 `print_exc()` 会怎样？

**原因**：`print_exc()`/`format_exc()` 依赖 `sys.exception()`（当前正在处理的异常），在 `except` 块之外调用可能输出空或产生非预期结果。

**对策**：此时应改用 `print_stack()`/`format_stack()`/`extract_stack()` 获取当前调用栈。

### Q5：`TracebackException.exc_type` 还能用吗？

**已弃用**：3.13 起 `exc_type` 已弃用，请改用 `exc_type_str`（字符串形式），这样也避免了持有异常类对象引用带来的额外成本。

### Q6：为什么回溯输出里冒出了 ANSI 颜色代码？

**原因**：3.13 起 `traceback` 输出默认带颜色。

**对策**：写入日志文件或非终端环境时，可用环境变量（如 `PYTHON_COLORS=0`）或 `NO_COLOR` 关闭。

### Q7：异常组（ExceptionGroup）的内容为什么被截断了？

**原因**：`TracebackException` 的 `max_group_width`（默认 15）与 `max_group_depth`（默认 10）会截断异常组的格式化输出。

**对策**：诊断深层嵌套异常组时，可按需调大这两个参数。

## 四、常见错误信息与对策表

| 报错 / 症状 | 常见成因 | 对策 |
|---|---|---|
| `ModuleNotFoundError: No module named 'sys.monitoring'` | 误用 `import sys.monitoring` 或 `from sys.monitoring import events` | 改为 `import sys` 后使用 `sys.monitoring` / `sys.monitoring.events` |
| `ModuleNotFoundError: No module named 'annotationlib'` | Python 版本 < 3.14 | 升级到 3.14，或用 `typing-extensions` 的 `get_annotations()` |
| `AttributeError: module 'sys' has no attribute 'monitoring'` | Python < 3.12 | 升级到 3.12+ |
| `AttributeError: ... 'BRANCH_LEFT'` | Python < 3.14（该事件不存在） | 升级，或在 3.13 用 `BRANCH` |
| `ValueError`（调 `set_events`/`set_local_events`） | 工具 ID 未登记、超 0~5 范围、或被占用 | 先 `use_tool_id`，用 0~5 内空闲 ID |
| `TypeError: use_tool_id expected 2 arguments, got 1` | 漏填必填的 `name` 参数 | 传入 `name` 字符串 |
| `RuntimeError: generator didn't yield` | `@contextmanager` 生成器 yield 次数不对，或单次使用实例被复用 | 确保恰好 `yield` 一次；不要复用实例 |
| `RuntimeError`（进入已进入的上下文） | 对同一 `Context` 重复 `run()` | 退出后再进入，或各任务用独立上下文 |
| `LookupError` | `ContextVar.get()` 无默认值且变量未设置 | 提供 `default` 或先 `set` |
| `KeyError`（`context[var]`） | `Context` 中无该变量 | 用 `context.get(var, default)` |
| `NameError`（注解 `VALUE` 求值） | 前向引用名字尚未定义 | 改用 `Format.FORWARDREF` 或待名字就绪后再求值 |
| `ValueError: mutable default ... for field ... is not allowed` | 字段默认可变对象 | 改用 `field(default_factory=...)` |
| `FrozenInstanceError` | 对 `frozen=True` 实例赋值 | 用 `object.__setattr__` 在 `__post_init__` 初始化 |
| `TypeError: non-default argument follows default argument` | 无默认值字段排在默认值字段之后 | 调整字段顺序或用 `kw_only` |
| `ValueError` / `TypeError`（order 相关） | `order=True` 但 `eq=False` 或类已有比较方法 | 检查 `eq` 与已有方法 |
| 回溯为空 / `print_exc` 无输出 | 在 `except` 块之外调用 | 改用 `print_stack` / `extract_stack` |
| 回溯输出带 ANSI 颜色 | 3.13 起默认彩色 | 设 `PYTHON_COLORS=0` 或 `NO_COLOR` |
| 异常组内容被截断 | 超过 `max_group_width`/`max_group_depth` | 调大对应参数 |

> 更多反模式与注意事项，见各章"注意事项 / 反模式"小节：`contextlib`（02 章第九节）、`contextvars`（03 章第八节）、`sys.monitoring`（04 章第十一节）、`annotationlib`（05 章末）、`dataclasses`（06 章第十三节）、`traceback`（07 章末）。

## 五、章节导航

- [上一章：综合使用示例](09-usage-examples.md) ←
- [下一章：总结与资源](11-summary-resources.md) →