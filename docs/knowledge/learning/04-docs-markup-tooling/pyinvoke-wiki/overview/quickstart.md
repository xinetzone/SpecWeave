---
type: "Tutorial"
title: "PyInvoke 5 分钟快速上手"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/overview/quickstart.toml"
description: "创建第一个任务文件、通过 CLI 和 Python API 调用任务"
tags: ["invoke", "quickstart", "getting-started", "tutorial"]
date: "2026-08-21"
status: "stable"
author: "SpecWeave"
sources:
  - id: invoke-tasks
    resource: "https://github.com/pyinvoke/invoke/blob/main/invoke/tasks.py"
    title: "PyInvoke tasks.py - @task decorator and Task class"
  - id: invoke-program
    resource: "https://github.com/pyinvoke/invoke/blob/main/invoke/program.py"
    title: "PyInvoke program.py - CLI entry point"
---
# 5 分钟快速上手

## 第一步：创建任务文件

在项目根目录创建 `tasks.py`：

```python
from invoke import task

@task
def hello(c):
    """打印 Hello, World!"""
    print("Hello, World!")

@task
def greet(c, name="World"):
    """向指定的人打招呼"""
    print(f"Hello, {name}!")

@task
def build(c, clean=False):
    """构建项目，--clean 选项表示先清理"""
    if clean:
        c.run("rm -rf build/ dist/")
        print("已清理构建目录")
    c.run("echo 'Building...'")
    print("构建完成")
```

## 第二步：查看可用任务

```bash
$ inv --list
Available tasks:

  build    构建项目，--clean 选项表示先清理
  greet    向指定的人打招呼
  hello    打印 Hello, World!
```

## 第三步：运行任务

```bash
# 运行 hello 任务
$ inv hello
Hello, World!

# 运行 greet 任务，默认参数
$ inv greet
Hello, World!

# 运行 greet 任务，指定参数
$ inv greet --name Alice
Hello, Alice!

# 短形式参数名（函数参数名中的下划线自动映射为 dash）
$ inv greet -n Bob
Hello, Bob!

# 运行带布尔 flag 的任务
$ inv build --clean
已清理构建目录
Building...
构建完成

# 链式执行多个任务
$ inv hello greet --name Charlie build
Hello, World!
Hello, Charlie!
Building...
构建完成
```

## 第四步：使用命名空间

创建更复杂的项目结构，将任务分组到不同模块中：

**`tasks/db.py`**：
```python
from invoke import task

@task
def migrate(c):
    """执行数据库迁移"""
    c.run("echo 'Running migrations...'")

@task
def seed(c):
    """填充测试数据"""
    c.run("echo 'Seeding database...'")
```

**`tasks/__init__.py`**（Collection 配置）：
```python
from invoke import Collection
from . import db

ns = Collection()
ns.add_collection(db, name="db")
```

调用命名空间下的任务：

```bash
$ inv --list
Available tasks:

  db.migrate    执行数据库迁移
  db.seed       填充测试数据

$ inv db.migrate
Running migrations...
```

## 第五步：编程式调用（Python API）

除了 CLI，还可以从 Python 代码中直接调用 Invoke：

```python
from invoke import Context, Config, Executor, Collection, task

@task
def hello(c):
    print("Hello from Python API!")

ns = Collection(hello)
config = Config()
executor = Executor(ns, config=config)
executor.execute("hello")
```

或者更简单地，使用 `run()` 快捷函数：

```python
from invoke import run

result = run("echo hello", hide=True)
print(result.stdout)  # 'hello\n'
print(result.ok)      # True（exit code 为 0）
```

## 核心要点速记

| 概念 | 关键字 | 一句话说明 |
|------|--------|-----------|
| 任务定义 | `@task` | 装饰普通 Python 函数 |
| 上下文 | `c` | 第一个参数，提供 `c.run()` 执行命令 |
| CLI 入口 | `inv`/`invoke` | 命令行调用 |
| 任务发现 | `tasks.py` | 默认加载当前目录的 tasks.py |
| 参数映射 | `--name` ↔ `name` | 函数参数自动映射为 CLI flag |
| 命名空间 | `Collection` | 任务分组和组织 |
| 上下文管理器 | `c.cd()`, `c.prefix()` | 目录切换和环境前缀 |
