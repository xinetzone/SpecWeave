---
type: "Architecture"
title: "PyInvoke 核心架构总览"
description: "Task→Collection→Parser→Executor→Context→Runner 的完整调用链"
tags: ["invoke", "architecture", "call-chain", "internals"]
date: "2026-08-21"
status: "stable"
author: "SpecWeave"
sources:
  - id: invoke-program
    resource: "d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/program.py"
    title: "PyInvoke program.py"
  - id: invoke-executor
    resource: "d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/executor.py"
    title: "PyInvoke executor.py"
  - id: invoke-context
    resource: "d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/context.py"
    title: "PyInvoke context.py"
  - id: invoke-runners
    resource: "d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/runners.py"
    title: "PyInvoke runners.py"
---

# 核心架构总览

Invoke 的架构可以理解为一条清晰的调用链：**Program → Parser → Collection → Executor → Context → Runner**。

## 调用链路

```
用户命令行输入 (inv build --clean)
        │
        ▼
┌─────────────────────────────────────────────┐
│  Program (program.py)                       │
│  - CLI 入口点，协调各组件                     │
│  - 加载配置 (Config)                         │
│  - 加载任务 (Loader→Collection)              │
│  - 创建解析器 (Parser)                       │
└─────────────┬───────────────────────────────┘
              │ ParseResult
              ▼
┌─────────────────────────────────────────────┐
│  Parser (parser.py)                         │
│  - 解析命令行参数                             │
│  - 识别任务名和任务参数                        │
│  - 处理短标志、布尔 flag、iterable 值         │
└─────────────┬───────────────────────────────┘
              │ tasks_to_call
              ▼
┌─────────────────────────────────────────────┐
│  Collection (collection.py)                 │
│  - 任务命名空间                              │
│  - 按 dotted name 查找任务                   │
│  - 提供任务配置上下文                         │
└─────────────┬───────────────────────────────┘
              │ Task objects
              ▼
┌─────────────────────────────────────────────┐
│  Executor (executor.py)                     │
│  - 展开 pre/post 任务链                      │
│  - 任务去重                                  │
│  - 按顺序执行任务                             │
│  - 处理 Call 对象（参数化调用）               │
└─────────────┬───────────────────────────────┘
              │ for each task
              ▼
┌─────────────────────────────────────────────┐
│  Task (tasks.py) + Context (context.py)     │
│  - Task.body(ctx, **kwargs) 执行函数体       │
│  - Context 提供 run/sudo/cd/prefix          │
│  - c.run() 委托给 Runner                     │
└─────────────┬───────────────────────────────┘
              │ c.run("command")
              ▼
┌─────────────────────────────────────────────┐
│  Runner (runners.py)                        │
│  - 创建子进程执行 shell 命令                  │
│  - 管理 stdout/stderr/stdin                  │
│  - 处理 PTY、Watcher、异步 Promise            │
│  - 返回 Result 对象                          │
└─────────────────────────────────────────────┘
```

## 核心模块职责

### Program（CLI 入口）

[program.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/program.py) 是 Invoke 的 CLI 协调者。`Program.run()` 方法执行完整的启动流程：

1. 解析 `core_args()`（定义全局选项如 `--help`、`--list`、`--config`、`--echo` 等）
2. 创建 `Config` 对象，加载多层配置
3. 使用 `FilesystemLoader` 发现并加载 `tasks.py`（或 `tasks/` 包）
4. 创建 `Parser` 解析命令行参数
5. 根据解析结果决定是列出任务（`--list`）、显示帮助（`--help`）还是执行任务
6. 创建 `Executor` 执行指定任务

### Parser（参数解析）

[parser.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/parser.py) 负责将命令行字符串解析为结构化的 `ParseResult`。

- `Argument`：定义单个参数（名称、类型、默认值、短标志、是否为 iterable/incrementable/optional value）
- `ParserContext`：跟踪解析状态
- `Parser`：管理初始上下文和任务上下文的切换

关键行为：
- Python 函数参数名中的下划线 `_` 自动映射为命令行中的 dash `-`（如 `my_arg` → `--my-arg`）
- 第一个位置参数（Context 除外）映射为位置 CLI 参数
- 布尔默认值的参数自动成为 flag（不需要值）

### Collection（命名空间）

[collection.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/collection.py) 是任务的组织容器。

- `add_task(task, name=None, aliases=(), default=False)`：添加任务
- `add_collection(collection, name=None)`：嵌套子命名空间
- `__getitem__(name)`：按 name 查找任务或子集合
- `task_with_config(task)`：返回绑定了集合配置的 Task 副本

### Executor（执行器）

[executor.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/executor.py) 管理任务执行流程。

- `execute(*tasks)`：核心执行入口，展开 pre/post 链、去重、依次执行
- `expand_calls(calls)`：展开每个 Call 的 pre/post 依赖
- `dedupe(calls)`：去重（同一名任务在同一参数下只执行一次）
- 参数化：使用 `call(task, arg=value)` 可以为 pre/post 任务传递特定参数

### Task（任务）

[tasks.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/tasks.py) 定义任务对象。

- `@task` 装饰器将普通函数包装为 `Task` 实例
- `Task.body`：原始函数
- `Task.pre` / `Task.post`：前置/后置任务列表
- `Task.get_arguments()`：从函数签名提取参数定义，供 Parser 使用
- `Call`：参数化的任务引用，在 pre/post 中使用

### Context（上下文）

[context.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/context.py) 是任务执行时传递给函数的第一个参数 `c`。

- `c.run(command, **kwargs)`：执行本地 shell 命令，委托给 `self.config.runners.local`（默认 `Local` runner）
- `c.sudo(command, **kwargs)`：以 sudo 执行命令
- `c.cd(path)`：返回上下文管理器，在其中执行的命令都在指定目录下
- `c.prefix(command)`：返回上下文管理器，在其中执行的命令都以指定命令为前缀
- `c.config[key]`：访问配置（DataProxy 代理，支持属性访问 `c.config.key`）

### Runner（命令执行）

[runners.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/runners.py) 负责实际的子进程创建和管理。

- `Runner`：抽象基类，定义 `run()` 模板方法
- `Local`：本地子进程实现（使用 pty 或 subprocess）
- `Result`：命令执行结果（stdout、stderr、exit_code、ok、command 等）
- `Promise`：异步执行时返回的 future 对象
- `Watcher`：流监控器，用于自动应答（如输入密码）

## Config（配置）

[config.py](file:///d:/spaces/SpecWeave/external/libs/pyinvoke/invoke/invoke/config.py) 是配置管理核心。

- 七层配置合并：defaults → system → user → project → env → runtime → overrides
- `DataProxy`：提供属性风格的配置访问（`config.run.echo`）
- `merge_dicts(base, updates)`：深度合并字典

## 配置数据流

```
system file (/etc/invoke.yaml)
    ↓ merge
user file (~/.invoke.yaml)
    ↓ merge
project file (./invoke.yaml)
    ↓ merge
env vars (INVOKE_*)
    ↓ merge
CLI flags (--echo, --warn, etc.)
    ↓ merge
runtime overrides (Collection-level config)
    ↓
最终 Config → Context.config → Runner kwargs
```

## 扩展点

Invoke 的每个核心类都设计为可继承扩展：

| 基类 | 扩展示例 | 用途 |
|------|---------|------|
| `Runner` | Fabric 的 Remote | SSH 远程执行 |
| `Executor` | 自定义执行器 | 并行执行、重试、条件跳过 |
| `Program` | 自定义 CLI | Binary 模式分发、自定义子命令 |
| `Config` | 自定义配置 | 添加自定义配置层级 |
| `StreamWatcher` | 自定义应答器 | 特定交互式命令的自动应答 |
