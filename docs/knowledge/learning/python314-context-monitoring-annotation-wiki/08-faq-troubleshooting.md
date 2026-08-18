---
id: python314-context-monitoring-annotation-wiki-08-faq-troubleshooting
title: "Python 3.14 标准库教程 — FAQ 与排错"
date: "2026-08-18"
category: "learning"
tags: ["python", "python-3.14", "stdlib", "faq", "troubleshooting", "tutorial"]
---

# Python 3.14 标准库教程 — FAQ 与排错

> 一句话摘要：本章以问答形式解答 `sys.monitoring`、`contextvars`、`annotationlib`、`ExitStack` 及版本不匹配这几类高频疑问，并给出常见错误信息与对策表，帮助你快速定位并解决问题。

## FAQ

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

## 常见错误信息与对策表

| 错误信息（典型形态） | 可能原因 | 对策 |
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

> 更多反模式与注意事项，见各章"注意事项 / 反模式"小节：`contextlib`（02 章第九节）、`contextvars`（03 章第八节）、`sys.monitoring`（04 章第十一节）、`annotationlib`（05 章末）。

## 章节导航

- [上一章：综合使用示例](07-usage-examples.md) ←
- [下一章：总结与资源](09-summary-resources.md) →