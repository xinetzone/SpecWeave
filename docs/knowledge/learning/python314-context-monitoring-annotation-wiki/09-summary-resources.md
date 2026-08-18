---
id: python314-context-monitoring-annotation-wiki-09-summary-resources
title: "Python 3.14 标准库教程 — 总结与资源"
date: "2026-08-18"
category: "learning"
tags: ["python", "python-3.14", "stdlib", "summary", "resources", "tutorial"]
---

# Python 3.14 标准库教程 — 总结与资源

> 一句话摘要：本章回顾四个模块的核心要点，提供高频 API 速查表、官方资源链接与后续学习路径，作为整份教程的收束与持续学习的跳板。

## 一、核心知识点回顾

- **`contextlib`**：围绕 `with` 语句与上下文管理器协议的全套工具。`@contextmanager`/`@asynccontextmanager` 用生成器做出上下文管理器；`ExitStack`/`AsyncExitStack` 动态组合多个清理动作；`redirect_stdout`/`redirect_stderr` 改道输出、`chdir` 切换目录、`suppress` 忽略指定异常、`nullcontext` 充当占位。需分清"单次使用 / 可重用 / 可重进入"三档（`ExitStack` 可重用但不可重入）。
- **`contextvars`**：为并发执行单元提供"上下文局部"状态隔离。`ContextVar` 在模块顶层声明；`set()` 返回 `Token`，可 `reset()` 还原；`Context` 是取值映射，`copy_context()` 以 O(1) 取快照、`Context.run()` 在指定上下文中执行；asyncio Task 自动复制上下文。3.14 起 `Token` 可直接用于 `with var.set(...)`，且支持泛型标注。
- **`sys.monitoring`**：3.12 起（PEP 669）的低开销事件监控。三要素为工具 ID（0~5）+ 事件集合 + 回调；先 `use_tool_id` 登记、`set_events`/`set_local_events` 开启、`register_callback` 注册；回调返回 `DISABLE` 局部关闭实现近零开销。3.14 新增 `BRANCH_LEFT`/`BRANCH_RIGHT` 并弃用 `BRANCH`。注意它不是可独立 import 的模块。
- **`annotationlib`**：3.14 新增（PEP 649/749）的注解内省模块，面向惰性求值注解。`Format` 四种取值（`VALUE`/`VALUE_WITH_FAKE_GLOBALS`/`FORWARDREF`/`STRING`）控制返回形态；`get_annotations()` 是主入口；`ForwardRef` 代理前向引用并可用 `evaluate()` 求值；无专属异常类。它是不做类型系统加工的底层原语，位于 `typing.get_type_hints()` 之下。

一句话贯穿四章：`contextlib` 管"进入/退出"，`contextvars` 管"状态归属"，`sys.monitoring` 管"时序观测"，`annotationlib` 管"声明元数据"。

## 二、速查表（高频 API 一览）

| 模块 | 高频 API | 一句话用途 | 备注 |
|---|---|---|---|
| `contextlib` | `@contextmanager` | 生成器变上下文管理器 | 必须恰好 yield 一次 |
| `contextlib` | `@asynccontextmanager` | 异步生成器变异步上下文管理器 | 3.7 新增 |
| `contextlib` | `ExitStack` / `AsyncExitStack` | 组合多个清理动作 | 可重用但不可重入 |
| `contextlib` | `redirect_stdout` / `redirect_stderr` | 临时改道输出 | 非线程安全 |
| `contextlib` | `suppress(*exc)` | 忽略指定异常 | 3.12 起支持 BaseExceptionGroup |
| `contextlib` | `nullcontext(x)` / `chdir(path)` | 占位 / 临时切目录 | `nullcontext` 3.7、`chdir` 3.11 |
| `contextlib` | `closing` / `aclosing` | 退出时调用 `close()`/`aclose()` | — |
| `contextvars` | `ContextVar(name, *, default)` | 声明上下文变量 | 在模块顶层创建 |
| `contextvars` | `var.get(default)` / `var.set(value)` / `var.reset(token)` | 取值 / 设值 / 还原 | `set` 返回 Token |
| `contextvars` | `Token` | 还原凭据，可作 `with`（3.14） | 单 token 单次 reset |
| `contextvars` | `copy_context()` / `Context.run(callable)` | 取快照 / 在上下文中执行 | `copy_context` O(1) |
| `sys.monitoring` | `use_tool_id(id, name)` / `free_tool_id(id)` | 登记 / 释放工具 ID | name 必填，id 0~5 |
| `sys.monitoring` | `set_events(id, set)` / `set_local_events(id, code, set)` | 开启全局 / 局部事件 | 未登记会 ValueError |
| `sys.monitoring` | `register_callback(id, event, func)` | 注册 / 替换回调 | 传 None 注销 |
| `sys.monitoring` | `restart_events()` | 重新启用被 DISABLE 的事件 | — |
| `sys.monitoring` | `get_events` / `get_local_events` / `get_tool` | 查询事件 / 工具名 | — |
| `annotationlib` | `get_annotations(obj, *, format=...)` | 内省注解字典 | 每次返回新字典 |
| `annotationlib` | `Format.VALUE / FORWARDREF / STRING` | 控制返回格式 | `VALUE_WITH_FAKE_GLOBALS` 仅供内部 |
| `annotationlib` | `ForwardRef` | 前向引用代理 | `evaluate()` 求值 |

## 三、官方资源链接

各模块官方文档（均指向 Python 3.14 版本，与教程事实来源一致）：

- [contextlib 官方文档（英文）](https://docs.python.org/3.14/library/contextlib.html)
- [contextvars 官方文档（英文）](https://docs.python.org/3.14/library/contextvars.html) · [中文](https://docs.python.org/zh-cn/3.14/library/contextvars.html)
- [sys.monitoring 官方文档（含 Monitoring C API）](https://docs.python.org/3.14/library/sys.monitoring.html)
- [annotationlib 官方文档（英文）](https://docs.python.org/3.14/library/annotationlib.html)

版本与规范背景：

- [Python 3.14 What's New](https://docs.python.org/3.14/whatsnew/3.14.html)
- [PEP 567 — Context Variables](https://peps.python.org/pep-0567/)（`contextvars`）
- [PEP 669 — Low Impact Monitoring for CPython](https://peps.python.org/pep-0669/)（`sys.monitoring`）
- [PEP 649 — Deferred Evaluation of Annotations](https://peps.python.org/pep-0649/)（惰性注解求值）
- [PEP 749 — Implementing PEP 649](https://peps.python.org/pep-0749/)（引入 `annotationlib`）

相关模块与向后移植：

- [typing 官方文档](https://docs.python.org/3.14/library/typing.html)（`get_type_hints`、`ForwardRef` 别名）
- [typing-extensions（PyPI）](https://pypi.org/project/typing-extensions/)（`get_annotations()` 向后移植）

## 四、相关学习路径建议

1. **夯实管理基础**：先吃透 [02 contextlib](02-contextlib.md) 的协议与"可重用/可重进入"区别，它是其余各章最常打交道的语法规约。
2. **进阶并发**：再把 [03 contextvars](03-contextvars.md) 与 [04 sys.monitoring](04-sys-monitoring.md) 结合读，重点看懂 [06 跨模块分析](06-cross-module-analysis.md) 中的"状态归因"协作。
3. **拓展类型工具方向**：从 [05 annotationlib](05-annotationlib.md) 出发，进一步阅读 `typing.get_type_hints` 与 `typing.ForwardRef`，了解其在类型检查器/文档生成器中的角色。
4. **官方原文精读**：本教程各部分均由官方文档逐条核对，遇细节分歧请以官方文档为准（链接见上文）。

> 恭喜你学完本教程。若有具体问题，可反查 [08 FAQ 与排错](08-faq-troubleshooting.md) 或各章的"注意事项 / 反模式"小节。

## 章节导航

- [上一章：FAQ 与排错](08-faq-troubleshooting.md) ←