---
type: wiki
title: Loader 任务加载
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/loader.toml"
description: PyInvoke Loader 任务加载器的完整 API 参考，涵盖 FilesystemLoader 的递归向上搜索、tasks.py/包发现、模块导入与 sys.path 管理。
tags: [pyinvoke, loader, filesystem-loader, module-loading, tasks-discovery, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/loader.py
---
# Loader 任务加载

## 概述

`Loader` 是 Invoke 中负责查找和导入任务集合（Collection）的抽象基类。`FilesystemLoader` 是其唯一内置实现，从文件系统递归向上搜索 `tasks.py` 文件或 `tasks/` 包，并通过 Python 的 importlib 机制加载为模块，供 Collection 自动构建任务命名空间。

相关文档：[Collection](collection.md)、[Program](program.md)、[Config](config.md)

---

## Loader 抽象基类

### 构造函数

```python
Loader(config: Optional[Config] = None)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `config` | `Config` | `Config()` | 配置对象，用于读取加载相关配置（如 `tasks.collection_name`、`tasks.search_root`） |

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `config` | `Config` | 关联的配置对象 |

### 抽象方法：find

```python
find(name: str) -> Optional[ModuleSpec]
```

查找指定名称的集合模块，必须由子类实现：
- 返回一个 `importlib.machinery.ModuleSpec` 对象（用于 `module_from_spec` 和 `exec_module`）
- 找不到时返回 `None` 或抛出 `CollectionNotFound`

`FilesystemLoader` 的实现见下文。

### load 方法

```python
load(name: Optional[str] = None) -> Tuple[ModuleType, str]
```

加载并返回指定名称的集合模块。如果 `name` 为 `None`，使用 `config.tasks.collection_name`（默认 `"tasks"`）。

#### 返回值

返回二元组 `(module, directory)`：
- `module`：加载后的 Python 模块对象
- `directory`：模块所在目录的父目录路径（用于查找项目级配置文件）

#### 加载流程

1. 调用 `find(name)` 获取 ModuleSpec
2. 确定源文件路径和包围目录：
   - 单文件模块（`tasks.py`）：`enclosing_dir` = 文件所在目录，`module_parent` = `enclosing_dir`
   - 包模块（`tasks/__init__.py`）：`enclosing_dir` = `__init__.py` 所在目录，`module_parent` = 包的父目录
3. 将 `enclosing_dir` 插入 `sys.path` 开头（确保模块内的本地 import 正常工作）
4. 通过 `module_from_spec(spec)` 创建模块对象
5. 在 `sys.modules` 中注册模块（确保 `from . import xxx` 相对导入工作）
6. 调用 `spec.loader.exec_module(module)` 执行模块代码
7. 返回 `(module, str(module_parent))`

> **sys.path 管理**：Loader 会自动将任务文件所在目录添加到 `sys.path`，确保任务模块可以导入同目录下的其他 Python 模块。这避免了用户需要手动修改 PYTHONPATH。

---

## FilesystemLoader 类

`FilesystemLoader` 从文件系统搜索并加载任务模块，是 Invoke 默认使用的加载器。

### 构造函数

```python
FilesystemLoader(start: Optional[str] = None, **kwargs)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `start` | `str` | `config.tasks.search_root` | 搜索起始目录；None 时使用 CWD |
| `**kwargs` | — | — | 传递给父类 `Loader.__init__`（即 `config`） |

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `start` | `str` | property，搜索起始目录；配置值为空时使用 `os.getcwd()` |

### find 方法实现

```python
find(name: str) -> Optional[ModuleSpec]
```

从 `start` 目录开始，**递归向上**搜索直到文件系统根目录，查找以下两种形式的任务模块：

#### 1. 单文件模块

查找 `<name>.py` 文件（默认 `tasks.py`）：
```
start/
  tasks.py        ← 找到！
  src/
```
通过 `spec_from_file_location(name, path)` 创建 ModuleSpec。

#### 2. 包模块

查找 `<name>/__init__.py` 目录包（默认 `tasks/__init__.py`）：
```
start/
  tasks/
    __init__.py   ← 找到！
    db.py
```
通过 `spec_from_file_location(name, path, submodule_search_locations=[basepath])` 创建 ModuleSpec，设置 `submodule_search_locations` 以支持包内导入。

#### 搜索算法

```python
paths = self.start.split(os.sep)
for x in reversed(range(len(paths) + 1)):
    path = os.sep.join(paths[0:x])
    # 检查单文件: path/<name>.py
    if module in os.listdir(path):
        return spec_from_file_location(name, os.path.join(path, module))
    # 检查包: path/<name>/__init__.py
    elif name in os.listdir(path) and os.path.exists(os.path.join(path, name, "__init__.py")):
        return spec_from_file_location(name, os.path.join(basepath, "__init__.py"),
                                       submodule_search_locations=[basepath])
```

即从起始目录开始，逐级向上检查每一级目录，直到找到匹配的模块或到达根目录。

#### 异常处理

- `FileNotFoundError` / `ModuleNotFoundError`：目录列表失败时，抛出 `CollectionNotFound` 异常，包含 `name` 和 `start` 属性

### 搜索示例

假设目录结构：
```
/home/user/projects/myapp/
├── invoke.yaml
├── tasks.py
├── src/
│   └── main.py
└── tests/
    └── test_main.py
```

在 `/home/user/projects/myapp/tests/` 目录下运行 `inv`：

1. `start` = `/home/user/projects/myapp/tests/`
2. 检查 `/home/user/projects/myapp/tests/` → 无 tasks.py
3. 检查 `/home/user/projects/myapp/` → 找到 `tasks.py`！
4. 返回 ModuleSpec，加载 `/home/user/projects/myapp/tasks.py`
5. `module_parent` = `/home/user/projects/myapp/`（用于查找 `invoke.yaml` 项目配置）

---

## 配置项

Loader 行为受以下 `tasks.*` 配置项影响：

| 配置键 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `tasks.collection_name` | `str` | `"tasks"` | 任务模块/包名（可通过 `--collection`/`-c` 覆盖） |
| `tasks.search_root` | `str` | `None`（→ CWD） | 搜索起始目录（可通过 `--search-root`/`-r` 覆盖） |

---

## CollectionNotFound 异常

当找不到任务模块时抛出，包含：

| 属性 | 说明 |
|------|------|
| `name` | 查找的集合名称 |
| `start` | 搜索起始目录 |

Program 在 `run()` 中捕获此异常并友好提示。

---

## 自定义 Loader

可以通过继承 `Loader` 或 `FilesystemLoader` 实现自定义加载逻辑：

```python
from invoke import FilesystemLoader, Program
from importlib.util import spec_from_file_location
import os

class CustomLoader(FilesystemLoader):
    """自定义加载器，支持从 .invoke/ 子目录加载任务"""
    
    def find(self, name):
        # 先尝试标准 FilesystemLoader 搜索
        spec = super().find(name)
        if spec:
            return spec
        
        # 自定义：搜索 .invoke/ 子目录
        for x in reversed(range(len(self.start.split(os.sep)) + 1)):
            path = os.sep.join(self.start.split(os.sep)[:x])
            invoke_dir = os.path.join(path, ".invoke")
            task_file = os.path.join(invoke_dir, f"{name}.py")
            if os.path.exists(task_file):
                return spec_from_file_location(name, task_file)
        
        return None

# 使用自定义加载器
program = Program(loader_class=CustomLoader)
program.run()
```

---

## 任务文件格式

Loader 加载的模块可以是单文件或包形式：

### 单文件（tasks.py）

```python
# tasks.py
from invoke import task, Collection

@task
def build(c):
    c.run("echo building")

@task
def test(c):
    c.run("pytest")

# 可选：显式命名空间
ns = Collection(build, test)
```

### 包（tasks/__init__.py）

```
tasks/
├── __init__.py
├── db.py       # 数据库相关任务
├── docs.py     # 文档相关任务
└── deploy.py   # 部署相关任务
```

```python
# tasks/__init__.py
from invoke import Collection
from . import db, docs, deploy

ns = Collection()
ns.add_collection(db)
ns.add_collection(docs)
ns.add_collection(deploy)
```

```python
# tasks/db.py
from invoke import task

@task
def migrate(c):
    c.run("alembic upgrade head")
```

CLI 调用：`inv db.migrate`、`inv docs.build`、`inv deploy.production`。

---

## 完整使用示例

```python
from invoke import Config, FilesystemLoader

# 基本使用
config = Config()
loader = FilesystemLoader(config=config)

try:
    module, directory = loader.load()  # 默认查找 "tasks"
    print(f"Loaded tasks from: {directory}")
    print(f"Module: {module}")
    # 模块中的 ns/namespace 属性或 Task 对象会被 Collection.from_module 处理
except CollectionNotFound as e:
    print(f"Could not find task collection '{e.name}' starting from {e.start}")

# 指定集合名称
module, directory = loader.load(name="deploy_tasks")
# 搜索 deploy_tasks.py 或 deploy_tasks/__init__.py

# 指定搜索起点
loader = FilesystemLoader(start="/path/to/project", config=config)
module, directory = loader.load()
```
