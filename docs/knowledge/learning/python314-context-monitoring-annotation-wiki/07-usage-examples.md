---
id: python314-context-monitoring-annotation-wiki-07-usage-examples
title: "Python 3.14 标准库教程 — 综合使用示例"
date: "2026-08-18"
category: "learning"
tags: ["python", "python-3.14", "stdlib", "examples", "tutorial"]
---

# Python 3.14 标准库教程 — 综合使用示例

> 一句话摘要：本章给出三个多模块组合的可运行示例——「ExitStack 管理多资源 + contextvars 记录请求级状态」「Token 上下文管理器 + annotationlib 内省注解」「sys.monitoring 统计调用 + contextvars 按任务归因」，把前几章的零散能力串成真实用法。

## 示例一：ExitStack 管理多个资源 + contextvars 记录请求级状态（兼容 3.7+）

**场景说明**：在一个"请求处理"函数里，我们希望：① 用 `ContextVar` 记录"当前请求 ID"，让并发的多个请求互不串扰；② 用 `ExitStack` 一次性管理多个资源（重定向输出 + 打开多个记录文件），统一在退出时清理。本例刻意用 `try/finally` 还原 `Token`，保证在 3.7 及以上版本都能运行。

```python
import io
import contextvars
from contextlib import ExitStack, redirect_stdout

# 在模块顶层声明上下文变量（切勿在闭包中创建）
request_id = contextvars.ContextVar("request_id", default="<none>")


def process_request(rid):
    """模拟处理一个请求：记录请求级状态 + 统一管理一组资源"""
    # 用 try/finally 还原，兼容 3.7+（3.14 可改写为 with request_id.set(rid)）
    token = request_id.set(rid)
    try:
        with ExitStack() as stack:
            # 1) 把 print 输出临时重定向到一个内存缓冲
            buffer = io.StringIO()
            stack.enter_context(redirect_stdout(buffer))

            # 2) 打开"按请求隔离"的多个记录文件，统一由 ExitStack 自动关闭
            handlers = [
                stack.enter_context(open(f"req-{request_id.get()}-part{i}.txt", "w"))
                for i in range(2)
            ]
            for h in handlers:
                h.write(f"part handled by {request_id.get()}\n")

            # 3) 这里的 print 会被写进 buffer，而不是 stdout
            print(f"处理请求 {request_id.get()}")
            return buffer.getvalue()
    finally:
        request_id.reset(token)


print(process_request("R-1001").splitlines()[-1])
print(process_request("R-2002").splitlines()[-1])
print("主上下文中的 request_id =", request_id.get())
```

**预期输出**：

```text
处理请求 R-1001
处理请求 R-2002
主上下文中的 request_id = <none>
```

**逐段注解**：

- `request_id = ContextVar(..., default="<none>")`：声明一个"请求级"变量，未设置时读到默认值。
- `token = request_id.set(rid)` / `request_id.reset(token)`：进出请求时设置/还原，保证请求结束后不残留；`finally` 确保即使抛异常也还原。
- `ExitStack`：把 `redirect_stdout`（重定向）和多个 `open(...)`（文件）的清理动作登记进同一个栈，`with` 结束时按"后进先出"统一执行。
- `redirect_stdout` 让函数内的 `print` 落到 `buffer`，从而能被 `getvalue()` 取回。

## 示例二：Token 上下文管理器 + annotationlib 内省注解（需要 Python 3.14）

**场景说明**：一个带"应用名"上下文的工具，需要内省某个函数的类型注解，并以不同格式展示。本例同时用到 3.14 的两个新能力：`Token` 直接作为上下文管理器（`with app_name.set(...)`），以及 `annotationlib` 的 `get_annotations` 多种 `Format`。**此示例必须运行在 Python 3.14 上**。

```python
import contextvars
from annotationlib import get_annotations, Format

app_name = contextvars.ContextVar("app_name", default="unknown")


def describe(x: int, y: list[str]) -> dict[str, float]:
    """仅为演示注解，函数体无实质逻辑。"""
    return {}


def show(fmt):
    # 3.14：Token 可直接用于 with，退出时自动还原 app_name
    with app_name.set("demo-app"):
        print(f"[{app_name.get()}] format={fmt.name}:")
        print(get_annotations(describe, format=fmt))


show(Format.VALUE)       # 求值后的真实类型对象
show(Format.STRING)      # 接近源码文本的字符串
show(Format.FORWARDREF)  # 此处无前向引用，等价于 VALUE

print("退出所有 with 后 app_name =", app_name.get())
```

**预期输出**（大意，字典顺序以 CPython 实际为准）：

```text
[demo-app] format=VALUE:
{'x': <class 'int'>, 'y': list[str], 'return': dict[str, float]}
[demo-app] format=STRING:
{'x': 'int', 'y': 'list[str]', 'return': 'dict[str, float]'}
[demo-app] format=FORWARDREF:
{'x': <class 'int'>, 'y': list[str], 'return': dict[str, float]}
退出所有 with 后 app_name = unknown
```

**逐段注解**：

- `with app_name.set("demo-app")` 是 3.14 的 `Token` 上下文管理器写法，等价于 `token = app_name.set(...)` + `try/finally: app_name.reset(token)`，进入时设置、退出时自动还原。
- `get_annotations(describe, format=...)` 用三种格式内省同一函数的注解：`VALUE` 返回真实类型对象，`STRING` 返回源码文本，`FORWARDREF` 对未定义名字才返回代理（本例名字都已定义，故与 `VALUE` 一致）。
- 最后一个 `print` 在 `with` 之外执行，验证 `app_name` 已被自动还原为默认值。

## 示例三：sys.monitoring 统计函数调用 + contextvars 按任务归因（需要 Python 3.14）

**场景说明**：用 `sys.monitoring` 的 `PY_START` 事件统计某个目标函数的调用次数，同时用 `ContextVar` 标记"当前属于哪个任务"，从而把计数按任务拆分，而不是混进一个全局数字。`sys.monitoring` 需 3.12+，`Token` 上下文管理器需 3.14，故**此示例标注为 Python 3.14**。

```python
import sys
import contextvars

events = sys.monitoring.events

current_job = contextvars.ContextVar("current_job", default="<idle>")
counts = {}  # 任务名 -> 调用次数


def on_start(code, instruction_offset):
    # 只统计我们关心的目标函数，过滤掉其它内部/C 函数噪声
    if code.co_name == "step":
        job = current_job.get()
        counts[job] = counts.get(job, 0) + 1


sys.monitoring.use_tool_id(4, "job-profiler")
sys.monitoring.register_callback(4, events.PY_START, on_start)
sys.monitoring.set_events(4, events.PY_START)


def step():
    return 1


def compute():
    return step() + step()


# 用 3.14 的 Token 上下文管理器做"任务隔离"，退出自动还原
with current_job.set("job-A"):
    compute()          # 触发 2 次 step

with current_job.set("job-B"):
    compute()          # 再 2 次 step
    compute()          # 再 2 次 step

sys.monitoring.free_tool_id(4)
print(counts)
```

**预期输出**：

```text
{'job-A': 2, 'job-B': 4}
```

**逐段注解**：

- 回调 `on_start` 用 `code.co_name == "step"` 过滤，只统计目标函数的 `PY_START` 事件，避免把 `compute`、内置函数等也计入。
- `PY_START` 为全局事件，会覆盖整个解释器进程；本例用过滤 + 短小的监控区间控制噪声。
- 回调里调用 `current_job.get()` 读取"当前任务名"，这正是 [06 跨模块分析](06-cross-module-analysis.md) 中"`sys.monitoring` 负责触发、`contextvars` 负责归属"的落地。
- 结束后 `free_tool_id(4)` 释放工具 ID，避免占用 0~5 的有限名额。

> 说明：`sys.monitoring` 的回调在复杂/异步场景下可能在不同线程被调用，且监控是解释器进程级的。生产环境建议只在关心的代码对象上使用**局部事件**（`set_local_events`）以降低噪声，并谨慎处理回调的重入，详见 [04 sys.monitoring](04-sys-monitoring.md)。

## 章节导航

- [上一章：跨模块综合分析](06-cross-module-analysis.md) ←
- [下一章：FAQ 与排错](08-faq-troubleshooting.md) →