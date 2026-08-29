---
id: "python314-stdlib-wiki-01"
title: "Python 3.14 标准库教程 — 版本背景与模块可用性"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/01-version-prerequisites.toml"
---
# Python 3.14 标准库教程 — 版本背景与模块可用性

> 一句话摘要：本教程覆盖的六个模块"年龄"差异很大——`contextlib` 长期存在、`dataclasses`/`contextvars` 于 3.7 引入、`traceback` 关键 API 于 3.4/3.5 引入、`sys.monitoring` 于 3.12 引入、`annotationlib` 为 3.14 全新模块；在动手前先确认所用 Python 版本，能避免绝大多数 `ImportError` / `AttributeError`。

## 一、六模块的版本可用性对比

| 模块 | 引入版本 | 规范/动机 | 在 3.14 的关键变化 |
|---|---|---|---|
| `contextlib` | 长期存在（多数 API 在 3.2–3.11 陆续加入） | 围绕 `with` 语句的上下文管理器协议 | 官方文档未标注 3.14 新增 API；在 3.14 中可与新特性（如 `Token` 上下文管理器）协作 |
| `contextvars` | **3.7** | [PEP 567](https://peps.python.org/pep-0567/) | ① `Token` 对象支持上下文管理器协议，可用 `with var.set(...)`；② `ContextVar`/`Token` 支持泛型标注（如 `ContextVar[int]`） |
| `sys.monitoring` | **3.12** | [PEP 669](https://peps.python.org/pep-0669/) | 新增 `BRANCH_LEFT` 与 `BRANCH_RIGHT` 两个分支事件，并将旧的 `BRANCH` 标记为弃用 |
| `annotationlib` | **3.14 新增** | [PEP 649](https://peps.python.org/pep-0649/) + [PEP 749](https://peps.python.org/pep-0749/) | 整个模块即为 3.14 新增能力 |
| `dataclasses` | **3.7** | [PEP 557](https://peps.python.org/pep-0557/) | `field()` 新增 `doc` 参数；`make_dataclass()` 新增 `decorator` 参数 |
| `traceback` | 早期即存在（关键 API 于 3.4/3.5 陆续加入） | 栈回溯的标准化提取/格式化/打印 | `walk_stack` 生成器语义改变（反映调用那一刻的栈状态） |

补充说明（均源自各章节的版本信息）：

- `contextlib` 中各 API 并非同时出现：`ContextDecorator` 为 3.2，`ExitStack` 为 3.3，`suppress`/`redirect_stdout` 为 3.4，`redirect_stderr` 为 3.5，`AbstractContextManager` 为 3.6，`@asynccontextmanager`/`nullcontext`/`AsyncExitStack`/`AbstractAsyncContextManager` 为 3.7，`aclosing`/`AsyncContextDecorator` 为 3.10，`chdir` 为 3.11。完整清单见 [02 contextlib](02-contextlib.md) 的"版本可用性说明"。
- `contextvars` 的 `ContextVar.name` 属性自 **3.7.1** 加入；`Token` 上下文管理器与泛型标注自 **3.14** 加入。
- `sys.monitoring` 在 3.11 及更早版本中**不存在**；3.13 及以前只有 `BRANCH` 一个条件分支事件。
- `annotationlib` 整体标记为 "Added in version 3.14"；`typing.get_type_hints()` 自 3.14 起新增 `format` 参数，`typing.ForwardRef` 自 3.14 起成为 `annotationlib.ForwardRef` 的别名。
- `dataclasses` 关键里程碑：3.10 新增 `match_args`/`kw_only`/`slots`/`KW_ONLY`；3.11 新增 `weakref_slot`；3.13 `__eq__` 改为逐字段比较；3.14 新增 `field(doc=)` 与 `make_dataclass(decorator=)`。详见 [06 dataclasses](06-dataclasses.md)。
- `traceback` 关键里程碑：`clear_frames` 为 3.4；面向对象三件套为 3.5；直接传异常对象为 3.10；异常组/注释支持为 3.11；`exc_type_str`/`show_group` 为 3.13；`walk_stack` 语义变化为 3.14。详见 [07 traceback](07-traceback.md)。

## 二、如何检查当前 Python 版本

在终端中：

```bash
python --version
# 或
python3 --version
```

在 Python 代码内：

```python
import sys

print(sys.version)             # 完整版本串，例如 3.14.7 (......)
print(sys.version_info)        # sys.version_info(major=3, minor=14, micro=7, ...)

# 判断是否满足某模块的最低版本
if sys.version_info >= (3, 14):
    print("可用 annotationlib 与 3.14 新特性")
elif sys.version_info >= (3, 12):
    print("可用 sys.monitoring，但 annotationlib 不可用")
elif sys.version_info >= (3, 7):
    print("可用 contextvars 与 dataclasses，但 sys.monitoring 不可用")
else:
    print("本教程六个模块的多数能力均不可用")
```

`sys.version_info` 是一个命名元组，可通过 `.major`、`.minor`、`.micro` 等字段做精确比较。

## 三、各模块的 import 语句与最低版本提示

### `contextlib`（几乎无版本门槛）

```python
from contextlib import contextmanager, ExitStack, redirect_stdout, suppress, nullcontext, chdir
from contextlib import asynccontextmanager, aclosing, AsyncExitStack
```

> 极早期版本即提供 `contextlib` 模块；个别 API（如 `chdir` 需 3.11、`aclosing` 需 3.10）注意对应版本。

### `contextvars`（需 3.7+）

```python
import contextvars

var = contextvars.ContextVar("var", default=42)   # 需 3.7+
# 3.14 新增：Token 作为上下文管理器
with var.set(100):
    ...
```

### `sys.monitoring`（需 3.12+）

```python
import sys

events = sys.monitoring.events          # 需 3.12+
sys.monitoring.use_tool_id(4, "my-tool")
sys.monitoring.set_events(4, events.PY_START)
# 3.14 新增：
#   events.BRANCH_LEFT  /  events.BRANCH_RIGHT
```

> **易错点**：`sys.monitoring` 是 `sys` 内部的一个命名空间，`import sys.monitoring` 或 `from sys.monitoring import events` 都会抛出 `ModuleNotFoundError`。必须 `import sys` 后使用 `sys.monitoring`。

### `annotationlib`（需 3.14+）

```python
from annotationlib import get_annotations, Format, ForwardRef
from annotationlib import annotations_to_string, call_annotate_function, call_evaluate_function
```

> 在早于 3.14 的环境中，`import annotationlib` 会抛 `ModuleNotFoundError`。官方指出 [typing-extensions](https://pypi.org/project/typing-extensions/) 提供了 `get_annotations()` 的向后移植版本，可在旧版本上使用。

### `dataclasses`（需 3.7+）

```python
from dataclasses import dataclass, field, fields, asdict, astuple, replace

@dataclass
class C:
    x: int = 0
# 3.14 新增：field(doc=...) 与 make_dataclass(decorator=...)
```

> `dataclasses` 自 3.7 引入，但 `slots`/`kw_only`/`match_args`（3.10）、`weakref_slot`（3.11）、`doc`/`decorator`（3.14）等较新参数需注意对应版本。

### `traceback`（早期即存在，关键 API 3.4/3.5+）

```python
import traceback

traceback.print_exc()                      # 打印当前异常
tb = traceback.TracebackException.from_exception(exc)  # 3.5+
# 3.13 起默认彩色输出；3.14 变更 walk_stack 生成器语义
```

> `traceback` 模块自 Python 早期版本即存在，但面向对象三件套（`TracebackException`/`StackSummary`/`FrameSummary`）需 3.5+。

## 四、小结：先查版本，再写代码

把这六个模块按"引入版本"排序（由旧到新）：`contextlib` → `traceback`（3.4/3.5 补全）→ `contextvars`/`dataclasses`（3.7）→ `sys.monitoring`（3.12）→ `annotationlib`（3.14）。动手前先用 `sys.version_info` 确认环境；一旦遇到 `ModuleNotFoundError` 或 `AttributeError`，首先怀疑版本不足，再排查 import 写法，可参考 [10 FAQ 与排错](10-faq-troubleshooting.md) 中的错误对策表。

## 五、章节导航

- [上一章：概述](00-overview.md) ←
- [下一章：contextlib](02-contextlib.md) →