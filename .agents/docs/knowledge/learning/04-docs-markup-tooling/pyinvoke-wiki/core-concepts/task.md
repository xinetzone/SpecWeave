---
type: wiki
title: Task 与 @task 装饰器
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/task.toml"
description: PyInvoke 核心 Task 类与 @task 装饰器的完整 API 参考，涵盖参数映射规则、Call 对象与自动短标志生成。
tags: [pyinvoke, task, decorator, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/tasks.py
---
# Task 与 @task 装饰器

## 概述

`Task` 是 PyInvoke 中表示可执行任务及其参数规范的核心对象。`@task` 装饰器是将普通 Python 函数标记为 Invoke 任务的便捷方式。每个 Task 对象封装了一个可调用体（body）、名称、别名、参数提示信息以及前置/后置任务链。

相关文档：[Collection](collection.md)、[Executor](executor.md)、[Parser](parser.md)

---

## @task 装饰器

`@task` 装饰器用于将函数标记为 Invoke 任务。它支持无括号和带括号两种调用形式。

### 基本用法

```python
from invoke import task

# 最简形式：无参数
@task
def build(c):
    c.run("echo Building...")

# 带参数形式
@task(
    name="compile",
    aliases=["c"],
    help={"clean": "Whether to clean before building"},
)
def build(c, clean=False):
    if clean:
        c.run("rm -rf build/")
    c.run("echo Building...")
```

### 完整参数列表

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `name` | `str` | `None` | 绑定到 Collection 时使用的名称，默认取函数的 `__name__` |
| `aliases` | `Iterable[str]` | `()` | 任务的别名列表，允许通过多个名称调用 |
| `positional` | `Iterable[str]` | `None` | 指定哪些参数按位置传递；`None` 表示无默认值的参数自动成为位置参数；空列表 `[]` 强制所有参数使用显式标志 |
| `optional` | `Iterable[str]` | `()` | 指定哪些参数具有可选值（即可作为布尔标志或带值选项） |
| `iterable` | `Iterable[str]` | `None` | 指定哪些参数构建为可迭代列表值（可多次指定累加） |
| `incrementable` | `Iterable[str]` | `None` | 指定哪些参数为可递增类型（如 `-vvv` 对应 verbosity=3） |
| `default` | `bool` | `False` | 是否为所在 Collection 的默认任务 |
| `auto_shortflags` | `bool` | `True` | 是否自动为选项生成短标志（如 `--verbose` → `-v`） |
| `help` | `Dict[str, str]` | `None` | 参数名到帮助文本的映射，用于 `--help` 输出 |
| `pre` | `List[Task/Call]` 或 `str` | `None` | 前置任务列表，在当前任务执行前运行 |
| `post` | `List[Task/Call]` 或 `str` | `None` | 后置任务列表，在当前任务执行后运行 |
| `autoprint` | `bool` | `False` | CLI 直接调用时是否自动打印返回值 |
| `klass` | `Type[Task]` | `Task` | 实例化时使用的类，默认为 `Task`，可用于子类扩展 |

> **注意**：`@task` 的位置参数会被当作 `pre` 的值。即 `@task(setup_task, other_task)` 等价于 `@task(pre=[setup_task, other_task])`。但不能同时给位置参数和 `pre` 关键字参数。

### 前置/后置任务参数化

前置/后置任务可通过 `call()` 函数预设参数：

```python
from invoke import task, call

@task
def setup(c, clean=False):
    if clean:
        c.run("rm -rf target/")
    c.run("mkdir -p target/")

# 无参数的前置任务
@task(pre=[setup])
def build(c):
    c.run("build command here")

# 带参数的前置任务
@task(pre=[call(setup, clean=True)])
def clean_build(c):
    c.run("build assuming clean slate")
```

---

## Task 类

`Task` 是泛型类 `Task(Generic[T])`，其中 `T` 绑定到被包装的可调用类型。

### 构造函数签名

```python
Task(
    body: Callable,
    name: Optional[str] = None,
    aliases: Iterable[str] = (),
    positional: Optional[Iterable[str]] = None,
    optional: Iterable[str] = (),
    default: bool = False,
    auto_shortflags: bool = True,
    help: Optional[Dict[str, Any]] = None,
    pre: Optional[Union[List[str], str]] = None,
    post: Optional[Union[List[str], str]] = None,
    autoprint: bool = False,
    iterable: Optional[Iterable[str]] = None,
    incrementable: Optional[Iterable[str]] = None,
)
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `body` | `Callable` | 被包装的原始可调用对象（实际执行的函数） |
| `name` | `str` | 任务名称（property），返回 `_name` 或 `__name__` |
| `aliases` | `Iterable[str]` | 别名元组 |
| `is_default` | `bool` | 是否为 Collection 默认任务 |
| `positional` | `Iterable[str]` | 位置参数列表 |
| `optional` | `Tuple[str, ...]` | 可选值参数元组 |
| `iterable` | `List[str]` | 可迭代参数列表 |
| `incrementable` | `List[str]` | 可递增参数列表 |
| `auto_shortflags` | `bool` | 是否自动生成短标志 |
| `help` | `Dict[str, str]` | 参数帮助文本 |
| `pre` | `List` | 前置任务列表 |
| `post` | `List` | 后置任务列表 |
| `times_called` | `int` | 被调用次数计数器 |
| `called` | `bool` | property，`times_called > 0` 时返回 `True` |
| `autoprint` | `bool` | 是否自动打印返回值 |
| `__doc__` | `str` | 从 body 复制的文档字符串 |
| `__name__` | `str` | 从 body 复制的函数名 |
| `__module__` | `str` | 从 body 复制的模块名 |

### 核心方法

#### `__call__(*args, **kwargs) -> T`

执行任务体。第一个参数必须是 `Context` 实例，否则抛出 `TypeError`。执行后递增 `times_called` 计数器。

```python
@task
def hello(c, name="world"):
    print(f"Hello, {name}!")

# 直接调用（需要 Context）
from invoke import Context
ctx = Context()
hello(ctx, name="Alice")  # 输出: Hello, Alice!
print(hello.times_called)  # 1
```

#### `argspec(body: Callable) -> inspect.Signature`

返回去掉第一个 Context 参数后的函数签名（`inspect.Signature`）。如果函数没有参数会抛出 `TypeError: Tasks must have an initial Context argument!`。

```python
@task
def mytask(c, verbose=False, count=1):
    pass

sig = mytask.argspec(mytask.body)
# sig.parameters 包含 'verbose' 和 'count'，不包含 'c'
for name, param in sig.parameters.items():
    print(name, param.default)
# verbose False
# count 1
```

#### `get_arguments(ignore_unknown_help: Optional[bool] = None) -> List[Argument]`

返回表示此任务参数签名的 `Argument` 对象列表（详见 [Parser](parser.md)）。这些 Argument 对象包含：
- 位置/可选/可迭代/可递增标志
- 自动生成的短标志
- 帮助文本
- 下划线到短横线的名称转换

位置参数会被排列到列表前端，以保持正确的解析顺序。

#### `fill_implicit_positionals(positional) -> Iterable[str]`

当 `positional=None` 时，自动将所有无默认值的参数标记为位置参数。这是默认行为。

#### `arg_opts(name: str, default, taken_names: Set[str]) -> Dict[str, Any]`

为单个参数构建选项字典，是 `get_arguments` 的内部辅助方法。处理：
- 位置参数标记
- 可选值标记
- 可迭代类型设置（`kind=list`，默认空列表）
- 可递增标记
- 下划线→短横线转换（`attr_name` 保留下划线原名，`names` 使用横线版本）
- 自动短标志生成（取名称中第一个未被占用的字符）
- 默认值类型推导
- 帮助文本关联

---

## 自动参数映射规则

Task 自动从 Python 函数签名推导出 CLI 参数映射，遵循以下规则：

### 1. 下划线 → 短横线转换

函数参数名中的下划线会自动转换为 CLI 中的短横线。原始下划线名称保留为 `attr_name` 用于属性访问：

```python
@task
def my_task(c, output_dir="./build"):
    pass

# CLI 调用: inv my-task --output-dir ./dist
# Python 访问: c.config... 中使用 output_dir
```

转换函数为 `translate_underscores()`（见 [parser/context.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/parser/context.py#L12-L13)），它会去除首尾下划线并将内部下划线替换为短横线。

### 2. 布尔默认值 → 标志参数

当参数默认值为 `bool` 类型时，自动推导为不需要值的 CLI 标志：

```python
@task
def build(c, clean=False, verbose=False):
    pass

# CLI: inv build --clean --verbose
# clean=True, verbose=True
```

对于默认值为 `True` 的布尔参数，会自动生成 `--no-<name>` 反向标志：

```python
@task
def deploy(c, force=True):
    pass

# CLI: inv deploy --no-force
# force=False
```

### 3. 无默认值 → 位置参数

没有默认值的参数自动成为位置参数（除非 `positional=[]` 显式禁用）：

```python
@task
def deploy(c, env, branch="main"):
    pass

# CLI: inv deploy production
# env="production", branch="main"
```

### 4. 自动短标志

当 `auto_shortflags=True`（默认）时，每个参数自动分配一个短标志，取参数名中第一个未被其他参数占用的字符：

```python
@task
def build(c, clean=False, verbose=False):
    pass
# --clean → -c (first available char)
# --verbose → -v (first available char)
```

### 5. 可迭代参数（iterable）

标记为 `iterable` 的参数可多次指定，值会累加到列表中：

```python
@task(iterable=["tag"])
def release(c, tag=()):
    print(list(tag))

# CLI: inv release --tag v1.0 --tag v1.1
# tag = ["v1.0", "v1.1"]
```

### 6. 可递增参数（incrementable）

标记为 `incrementable` 的参数每次出现时值加 1：

```python
@task(incrementable=["verbose"])
def build(c, verbose=0):
    print(f"Verbosity: {verbose}")

# CLI: inv build -vvv
# verbose = 3
```

### 7. 可选值参数（optional）

标记为 `optional` 的参数既可以作为布尔标志（不带值时为 `True`），也可以带值：

```python
@task(optional=["log"])
def run(c, log=None):
    print(log)

# CLI: inv run --log          # log = True
# CLI: inv run --log=debug    # log = "debug"
```

---

## Call 类

`Call` 类表示一个 Task 的具体调用（带参数），类似于 `functools.partial`，但增加了别名跟踪和 Context 生成能力。

### 构造函数

```python
Call(
    task: Task,
    called_as: Optional[str] = None,
    args: Optional[Tuple[str, ...]] = None,
    kwargs: Optional[Dict[str, Any]] = None,
)
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `task` | `Task` | 要执行的 Task 对象 |
| `called_as` | `Optional[str]` | 调用时使用的名称（可能是别名） |
| `args` | `Tuple[str, ...]` | 位置参数元组 |
| `kwargs` | `Dict[str, Any]` | 关键字参数字典 |

### 核心方法

#### `__getattr__(name) -> Any`

属性访问委托给内部的 `task` 对象，因此可以直接通过 Call 访问 Task 的属性：

```python
c = Call(my_task, called_as="mt")
print(c.name)  # 等价于 c.task.name
```

#### `make_context(config: Config, core_parse_result: ParseResult) -> Context`

生成适合此调用的 Context 对象，传入配置和核心解析结果。这是执行器在运行任务前创建 Context 的方法。

```python
from invoke import Config
config = Config()
call_obj = Call(my_task)
ctx = call_obj.make_context(config, core_parse_result=ParseResult())
my_task(ctx)
```

#### `clone(into: Optional[Type[Call]] = None, with_: Optional[Dict[str, Any]] = None) -> Call`

返回 Call 的独立副本。可指定子类 `into` 和额外参数 `with_`（会覆盖原始数据）：

```python
original = Call(build_task, kwargs={"clean": False})
modified = original.clone(with_={"kwargs": {"clean": True}})
```

#### `clone_data() -> Dict[str, Any]`

返回适合克隆的关键字参数字典（包含 task、called_as、深拷贝的 args 和 kwargs）。

### 等价性比较

两个 Call 对象相等当且仅当它们的 `task`、`args`、`kwargs` 都相等（不比较 `called_as`，因为同一任务的不同别名/名称调用应视为相同）。

---

## call() 便捷函数

```python
def call(task: Task, *args: Any, **kwargs: Any) -> Call
```

创建 Call 对象的便捷包装器，将位置参数和关键字参数映射到 Call 的 `args` 和 `kwargs`：

```python
from invoke import task, call

@task
def setup(c, clean=False, target="debug"):
    pass

@task(pre=[call(setup, clean=True, target="release")])
def build(c):
    pass
```

---

## 完整示例

```python
from invoke import task, call, Collection

@task(
    aliases=["cl"],
    iterable=["include"],
    incrementable=["verbose"],
    help={
        "target": "Build target directory",
        "clean": "Clean before building",
        "include": "Include additional modules (can repeat)",
    },
)
def compile(c, target="build", clean=False, include=None, verbose=0):
    """Compile the project."""
    if clean:
        c.run(f"rm -rf {target}")
    if verbose > 0:
        print(f"Verbosity level: {verbose}")
    for mod in (include or []):
        print(f"Including: {mod}")
    c.run(f"mkdir -p {target}")
    c.run(f"echo Compiling to {target}...")

@task
def test(c, coverage=False):
    """Run tests."""
    cmd = "pytest"
    if coverage:
        cmd += " --cov=myapp"
    c.run(cmd)

@task(pre=[call(compile, clean=True)], post=[test], default=True)
def all(c):
    """Default task: clean build + test."""
    print("All done!")

ns = Collection(compile, test, all)
```

CLI 调用示例：

```bash
inv all                     # 运行默认任务 (clean compile + test)
inv compile --clean -vv     # 清理编译，verbosity=2
inv compile --include=foo --include=bar  # 包含多个模块
inv cl                      # 使用别名
inv test --coverage         # 带覆盖率测试
```
