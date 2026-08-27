---
type: wiki
title: Executor 执行器
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/executor.toml"
description: PyInvoke Executor 执行器的完整 API 参考，涵盖任务归一化、前置/后置任务展开、去重与执行流程。
tags: [pyinvoke, executor, task-execution, pre-post, deduplication, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/executor.py
---
# Executor 执行器

## 概述

`Executor` 是 Invoke 中负责任务执行策略的核心类。它接收已解析的任务列表，将其归一化为 `Call` 对象，展开前置/后置任务链，去重后按顺序执行，并管理配置加载与 Context 创建。Executor 设计为可扩展的——子类可以覆盖其扩展点来改变、添加或移除行为。

相关文档：[Task](task.md)、[Call](task.md#call-类)、[Collection](collection.md)、[Config](config.md)、[Context](context.md)

---

## 构造函数

```python
Executor(
    collection: Collection,
    config: Optional[Config] = None,
    core: Optional[ParseResult] = None,
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `collection` | `Collection` | — | 任务集合，用于按名称查找任务及其默认配置 |
| `config` | `Config` | `Config()` | 配置对象，默认创建空配置 |
| `core` | `ParseResult` | `ParseResult()` | 核心程序参数解析结果（v3.0 默认为空 ParseResult） |

```python
from invoke import Collection, Config, Executor

ns = Collection()
# ... 添加任务 ...
config = Config()
executor = Executor(collection=ns, config=config)
```

---

## execute 方法

```python
execute(*tasks: Union[str, Tuple[str, Dict[str, Any]], ParserContext]) -> Dict[Task, Any]
```

按顺序执行一个或多个任务，返回任务对象到返回值的映射字典。返回字典包含前置和后置任务的结果。

### 任务参数形式

每个任务参数可以是以下三种形式之一：

#### 1. 字符串（任务名）

```python
executor.execute("build")
# 等价于：build()（无参数）

executor.execute("db.migrate")
# 支持点分路径的命名空间任务
```

#### 2. 二元组（任务名 + 参数字典）

```python
executor.execute(
    ("build", {"clean": True}),
    ("deploy", {"env": "production"}),
)
# 等价于：
# build(clean=True)
# deploy(env="production")
```

#### 3. ParserContext 对象

Parser 解析 CLI 参数后生成的 `ParserContext` 实例，其 `.name` 为任务名，`.as_kwargs` 为关键字参数。

#### 无参数调用

如果不传入任何任务，且 Collection 设置了默认任务，则执行默认任务：

```python
# 如果 ns.default == 'all'
executor.execute()  # 执行 all 任务
```

### 返回值

返回 `Dict[Task, Any]`，将 Task 对象映射到其返回值。前置/后置任务如果被执行也会出现在字典中。

```python
results = executor.execute("build")
build_task = ns["build"]
print(results[build_task])  # build 任务的返回值
```

### 执行流程

```
execute(*tasks)
  │
  ├─ 1. normalize(tasks)          # 归一化为 Call 对象列表
  ├─ 2. 保存 direct 列表（直接调用的任务，用于 autoprint 判断）
  ├─ 3. expand_calls(calls)       # 递归展开前置/后置任务
  ├─ 4. dedupe(expanded)          # 去重（如果 config.tasks.dedupe=True，默认 True）
  ├─ 5. 遍历去重后的 Call 列表：
  │    ├─ 5a. 加载 Collection 配置（config.load_collection）
  │    ├─ 5b. 加载 Shell 环境配置（config.load_shell_env）
  │    ├─ 5c. call.make_context(config, core) 创建 Context
  │    ├─ 5d. call.task(context, *call.args, **call.kwargs) 执行任务
  │    ├─ 5e. 如果是直接调用且 autoprint=True，打印返回值
  │    └─ 5f. 将结果存入 results 字典
  └─ 6. 返回 results
```

---

## normalize 方法

```python
normalize(tasks: Tuple[...]) -> List[Call]
```

将任意形式的任务列表转换为 `Call` 对象列表。

转换规则：
- 字符串 `name` → `Call(collection[name], kwargs={}, called_as=name)`
- `ParserContext` → `Call(collection[pc.name], kwargs=pc.as_kwargs, called_as=pc.name)`
- `(name, kwargs)` 元组 → `Call(collection[name], kwargs=kwargs, called_as=name)`
- 空输入 + Collection 有默认任务 → `[Call(collection[default])]`

```python
# 内部行为示例
calls = executor.normalize(("build",))
# [Call(build_task, called_as="build")]

calls = executor.normalize(("build", {"clean": True}))
# [Call(build_task, kwargs={"clean": True}, called_as="build")]

# 空输入 + 默认任务
calls = executor.normalize(())
# [Call(default_task)]  如果 collection.default 不为 None
```

---

## expand_calls 方法

```python
expand_calls(calls: List[Call]) -> List[Call]
```

递归展开任务的前置/后置任务列表，生成完整的执行序列。

### 展开逻辑

对于每个 Call：
1. 如果传入的是原始 `Task` 对象（而非 `Call`），先包装为 `Call(task)`
2. 递归展开 `call.pre`（前置任务列表）
3. 添加当前 Call
4. 递归展开 `call.post`（后置任务列表）

```python
# 假设有以下任务关系：
# setup → (无前置/后置)
# build → pre=[setup], post=[]
# deploy → pre=[build], post=[test]
# test → (无前置/后置)

# 执行 deploy 时的展开过程：
# expand_calls([deploy])
#   → expand_calls(deploy.pre) = expand_calls([build])
#       → expand_calls(build.pre) = expand_calls([setup])
#           → expand_calls(setup.pre) = []
#           → [setup]
#           → expand_calls(setup.post) = []
#         → [setup, build]
#         → expand_calls(build.post) = []
#     → [setup, build, deploy]
#     → expand_calls(deploy.post) = expand_calls([test])
#         → [setup, build, deploy, test]
```

### 支持嵌套的前置/后置

前置/后置任务自身也可以有前置/后置任务，展开会递归处理。`pre` 和 `post` 中的元素可以是 `Task` 对象或 `Call` 对象（通过 `call()` 预设参数）。

```python
from invoke import task, call

@task
def setup(c, clean=False):
    pass

@task(pre=[call(setup, clean=True)])
def build(c):
    pass

# expand_calls([build]) → [Call(setup, clean=True), Call(build)]
```

---

## dedupe 方法

```python
dedupe(calls: List[Call]) -> List[Call]
```

对 Call 列表进行去重，保留首次出现。

### 去重规则

两个 Call 相等当且仅当它们的 `task`、`args`、`kwargs` 都相等（`called_as` 不参与比较）。这意味着：

- 同一任务以不同名称/别名调用，如果参数相同，会被去重
- 同一任务以不同参数调用，**不会**被去重（会分别执行）

```python
# 去重示例：setup 作为 build 和 deploy 的前置，只执行一次
calls = [Call(setup), Call(build), Call(setup), Call(deploy)]
deduped = executor.dedupe(calls)
# → [Call(setup), Call(build), Call(deploy)]

# 不同参数不会去重
calls = [
    Call(setup, kwargs={"clean": True}),
    Call(build),
    Call(setup, kwargs={"clean": False}),
]
deduped = executor.dedupe(calls)
# → 保留全部三个，因为两个 setup 调用参数不同
```

### 配置控制

去重行为由配置项 `tasks.dedupe` 控制，默认为 `True`。设置为 `False` 会跳过去重，同一任务可能被多次执行。

---

## 配置加载

在执行每个 Call 之前，Executor 会执行两个配置加载步骤：

### load_collection(collection_config)

```python
config.load_collection(collection_config)
```

加载当前任务路径上的 Collection 配置。`collection_config` 通过 `collection.configuration(call.called_as)` 获取，包含从根集合到目标任务路径上所有命名空间配置的合并结果。

### load_shell_env()

```python
config.load_shell_env()
```

加载 Shell 环境变量配置（`INVOKE_*` 前缀的环境变量）。

> **重要**：这两个配置加载会重置 task-sensitive 配置层级，确保每个任务执行时看到正确的配置视图，但用户在任务中对 config 的修改（如 `c.config.run.echo = True`）会在任务间保留。

---

## Context 创建与任务调用

```python
context = call.make_context(config, core_parse_result=self.core)
args = (context, *call.args)
result = call.task(*args, **call.kwargs)
```

1. 通过 `Call.make_context()` 创建适合当前调用的 Context 对象
2. Context 作为第一个位置参数传入任务函数
3. 额外的位置参数和关键字参数从 Call 的 `args` 和 `kwargs` 传入

### autoprint 机制

如果任务是直接调用的（在 `direct` 列表中）且任务的 `autoprint=True`，执行后自动打印返回值：

```python
@task(autoprint=True)
def version(c):
    return "1.0.0"

# CLI: inv version
# 输出: 1.0.0
```

---

## 扩展点（子类覆盖）

Executor 设计为可扩展，子类可以覆盖以下方法来自定义行为：

| 方法 | 扩展用途 |
|------|----------|
| `normalize()` | 改变任务输入形式的解析方式 |
| `expand_calls()` | 添加额外的展开逻辑（如参数矩阵、条件执行） |
| `dedupe()` | 自定义去重策略 |
| `execute()` | 完全改变执行流程（如并行执行） |

```python
from invoke import Executor

class ParallelExecutor(Executor):
    """示例：并行执行无依赖关系的任务"""
    def execute(self, *tasks):
        # 自定义并行执行逻辑
        ...
```

---

## 执行示例

```python
from invoke import task, call, Collection, Config, Executor

@task
def clean(c):
    c.run("rm -rf build/")
    print("Cleaned")

@task
def setup(c, env="dev"):
    c.run(f"echo Setting up for {env}")
    print(f"Setup for {env}")

@task(pre=[clean, call(setup, env="prod")])
def build(c, target="debug"):
    c.run(f"echo Building {target}")
    print(f"Built {target}")
    return f"build-{target}"

@task(pre=[build])
def test(c, coverage=False):
    c.run("echo Running tests")
    print("Tests passed")

@task(post=[test])
def deploy(c):
    c.run("echo Deploying")
    print("Deployed")

ns = Collection(clean, setup, build, test, deploy)
config = Config()
executor = Executor(collection=ns, config=config)

# 执行单个任务
results = executor.execute("build")
# 执行顺序：clean → setup(env="prod") → build
# results 包含三个 Task → 返回值的映射

# 执行多个任务
results = executor.execute(("build", {"target": "release"}), "deploy")
# 执行顺序：clean → setup(env="prod") → build(target="release") → test → deploy
# 注意：clean 和 setup 是 build 的前置，test 是 deploy 的后置
# build 是 deploy 的前置（通过 pre=[build]）
# dedupe 确保 clean 和 setup 只执行一次
```
