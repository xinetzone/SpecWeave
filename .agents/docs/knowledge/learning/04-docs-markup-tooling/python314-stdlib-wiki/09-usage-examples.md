---
id: "python314-stdlib-wiki-09"
title: "Python 3.14 标准库教程 — 综合使用示例"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/09-usage-examples.toml"
---
# Python 3.14 标准库教程 — 综合使用示例

> 一句话摘要：本章给出七个多模块组合的可运行示例——前三个围绕"运行时动态机制"（`ExitStack` 管理多资源 + `contextvars` 请求级状态、`Token` 上下文管理器 + `annotationlib` 内省注解、`sys.monitoring` 统计调用 + `contextvars` 按任务归因），后四个围绕"数据结构与诊断"（`dataclasses` 建模、`traceback` 日志化、结构化栈上报、二者组合），把六模块能力串成真实用法。

## 一、示例总览

| 示例 | 主题 | 覆盖要点 | 版本要求 |
|---|---|---|---|
| 示例一 | ExitStack 管理多资源 + contextvars 请求级状态 | `ExitStack`、`redirect_stdout`、`ContextVar` | 3.7+ |
| 示例二 | Token 上下文管理器 + annotationlib 内省注解 | `ContextVar.set`、`get_annotations`、`Format` | 3.14 |
| 示例三 | sys.monitoring 统计调用 + contextvars 按任务归因 | `PY_START`、`ContextVar`、`Token` | 3.14 |
| 示例四 | 用 dataclasses 建模配置与商品 | `@dataclass`、`field`、`asdict`、`replace`、`__post_init__` | 3.7+ |
| 示例五 | 把回溯格式化为日志 | `format_exception`、`TracebackException` | 3.7+ |
| 示例六 | 结构化栈信息用于自定义上报 | `extract_stack`、`StackSummary`、`FrameSummary` | 3.5+ |
| 示例七 | 组合：校验数据类 + 捕获构造期异常 | `dataclasses` + `traceback` 协同 | 3.7+ |

## 二、示例一：ExitStack 管理多个资源 + contextvars 记录请求级状态（兼容 3.7+）

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

## 三、示例二：Token 上下文管理器 + annotationlib 内省注解（需要 Python 3.14）

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

## 四、示例三：sys.monitoring 统计函数调用 + contextvars 按任务归因（需要 Python 3.14）

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
- 回调里调用 `current_job.get()` 读取"当前任务名"，这正是 [08 跨模块分析](08-cross-module-analysis.md) 中"`sys.monitoring` 负责触发、`contextvars` 负责归属"的落地。
- 结束后 `free_tool_id(4)` 释放工具 ID，避免占用 0~5 的有限名额。

> 说明：`sys.monitoring` 的回调在复杂/异步场景下可能在不同线程被调用，且监控是解释器进程级的。生产环境建议只在关心的代码对象上使用**局部事件**（`set_local_events`）以降低噪声，并谨慎处理回调的重入，详见 [04 sys.monitoring](04-sys-monitoring.md)。

## 五、示例四：用 `dataclasses` 建模配置与商品

```python
from dataclasses import dataclass, field, asdict, replace
from typing import ClassVar

@dataclass
class InventoryItem:
    """库存商品。"""
    name: str
    unit_price: float
    quantity_on_hand: int = 0
    category: ClassVar[str] = "general"

    def total_cost(self) -> float:
        return self.unit_price * self.quantity_on_hand


@dataclass(frozen=True)
class Point:
    """二维坐标，冻结后可作为字典键。"""
    x: float
    y: float


@dataclass
class Order:
    """订单：total 由小计派生，note 在初始化后统一规范化。"""
    items: list[InventoryItem] = field(default_factory=list)
    total: float = field(init=False)
    note: str = ""

    def __post_init__(self):
        self.total = sum(item.total_cost() for item in self.items)
        self.note = self.note.strip()


if __name__ == "__main__":
    item = InventoryItem("widget", 3.0, 10)
    print(item)                     # InventoryItem(name='widget', unit_price=3.0, quantity_on_hand=10)
    print(asdict(item))             # {'name': 'widget', 'unit_price': 3.0, 'quantity_on_hand': 10}
    print(replace(item, quantity_on_hand=25).total_cost())   # 75.0

    order = Order(items=[item], note="  加急订单  ")
    print(order.total, repr(order.note))   # 30.0 '加急订单'

    # frozen 实例可哈希，可作为字典键
    positions = {Point(0, 0): "origin", Point(1, 2): "target"}
    print(positions[Point(1, 2)])   # target
```

## 六、示例五：把回溯格式化为日志

```python
import traceback
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)


def outer():
    return inner()


def inner():
    raise ValueError("配置项 name 缺失")


try:
    outer()
except ValueError:
    # 方式一：直接打印到 stderr（带异常链）
    print("=== print_exception ===")
    traceback.print_exception(limit=5, chain=True)

    # 方式二：格式化为单个字符串，写入日志
    print("=== format_exception ===")
    text = "".join(traceback.format_exception(limit=3))
    log.error("业务处理失败：\n%s", text)

    # 方式三：用 TracebackException 捕获"轻量表示"，稍后渲染
    print("=== TracebackException ===")
    import sys
    tb_exc = traceback.TracebackException.from_exception(sys.exception())
    print("".join(tb_exc.format()))
```

> 说明：`sys.exception()`（3.11 起）返回当前正在处理的异常，是 `sys.exc_info()[1]` 的更直接替代；在 `except` 块外调用会返回 `None`。

## 七、示例六：结构化栈信息用于自定义上报

```python
import traceback


def analyze_stack(limit: int = 10):
    """把当前调用栈转成结构化对象的列表，便于序列化到监控/告警系统。"""
    summary = traceback.extract_stack(limit=limit)
    rows = []
    for fs in summary:
        rows.append({
            "file": fs.filename,
            "line": fs.lineno,
            "end_line": fs.end_lineno,
            "func": fs.name,
            "code": fs.line,
        })
    return rows


def nested():
    inner()


def inner():
    stack = analyze_stack(limit=5)
    for row in stack:
        print(row)


# 直接运行：打印从脚本入口到当前行之间的若干帧
from pathlib import Path
print(Path(__file__).name)

nested()
```

> 提示：若只是想拿到"行号"而不需要读入源文本行，可用 `StackSummary.extract(gen, lookup_lines=False)` 降低开销，详见 [07 traceback](07-traceback.md) 的 `StackSummary` 一节。

## 八、示例七：组合——校验数据类 + 捕获构造期异常

```python
from dataclasses import dataclass, field
import traceback


@dataclass
class Config:
    """应用配置：构造后校验数值合法性。"""
    host: str
    port: int = 8080
    tag: str = field(default="", repr=False)

    def __post_init__(self):
        if not (0 < self.port < 65536):
            raise ValueError(f"端口非法: {self.port}")


def load_config(raw: dict) -> Config | None:
    """从一个外部字典加载配置；失败时记录结构化回溯并返回 None。"""
    try:
        return Config(host=raw["host"], port=raw.get("port", 8080))
    except Exception:
        # 捕获当前异常的轻量表示，写入日志而非让进程崩溃
        tb_exc = traceback.TracebackException.from_exception(
            __import__("sys").exception(),
            compact=True,
        )
        print("配置加载失败：")
        print("".join(tb_exc.format()))
        return None


print(load_config({"host": "localhost", "port": 99999}))   # 触发端口校验失败
print(load_config({"host": "localhost", "port": 8080}))    # 正常加载
```

> `compact=True` 让 `TracebackException` 只保存 `format()` 真正需要的数据，在异常链很长时节省内存，适合上述"捕获即渲染"的场景。这正是 [08 跨模块分析](08-cross-module-analysis.md) 中"`dataclasses` 校验抛异常 + `traceback` 结构化渲染"的落地。

## 九、章节导航

- [上一章：跨模块综合分析](08-cross-module-analysis.md) ←
- [下一章：FAQ 与排错](10-faq-troubleshooting.md) →