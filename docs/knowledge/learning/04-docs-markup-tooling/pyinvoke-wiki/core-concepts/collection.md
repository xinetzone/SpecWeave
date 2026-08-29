---
type: wiki
title: Collection 与命名空间
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/collection.toml"
description: PyInvoke Collection 类的完整 API 参考，涵盖任务注册、子命名空间、点分路径查找、命名空间配置与 from_module 自动发现。
tags: [pyinvoke, collection, namespace, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/collection.py
---
# Collection 与命名空间

## 概述

`Collection` 是 Invoke 中组织任务的命名空间容器。它负责管理任务和子集合的注册、查找、别名处理和配置合并。每个 Invoke 任务文件最终都会被加载为一个 Collection 对象。

相关文档：[Task](task.md)、[Executor](executor.md)、[Loader](loader.md)、[Config](config.md)

---

## 创建 Collection

### 构造函数

```python
Collection(
    *args: Any,
    **kwargs: Any,
)
```

构造函数支持多种初始化方式：

1. **空 Collection**：`Collection()` 创建空集合，后续通过 `add_task`/`add_collection` 添加内容
2. **命名 Collection**：第一个位置参数为字符串时作为集合名称
3. **通过位置参数添加任务/子集合**：后续位置参数自动分发到 `add_task` 或 `add_collection`
4. **通过关键字参数命名添加**：关键字参数的值为 Task/Collection，键为绑定名称
5. **特殊关键字参数**：
   - `loaded_from`：集合加载自的文件系统路径
   - `auto_dash_names`：是否自动将下划线转为短横线（默认 `True`）

### 初始化示例

```python
from invoke import Collection, task

@task
def build(c):
    c.run("echo building")

@task
def deploy(c):
    c.run("echo deploying")

# 方式1：方法式构建
ns = Collection()
ns.add_task(build)
ns.add_task(deploy)

# 方式2：命名子集合
docs = Collection('docs')
@task
def build_docs(c):
    c.run("sphinx-build docs _build")
docs.add_task(build_docs)

ns = Collection()
ns.add_task(build)
ns.add_collection(docs)
# 可用标识: 'build', 'docs.build-docs'

# 方式3：构造函数参数
ns = Collection(build, Collection('docs', build_docs))

# 方式4：关键字参数命名
ns = Collection(
    build_task=build,
    docs=Collection(build_docs)
)
# 等价于:
# ns = Collection()
# ns.add_task(build, 'build_task')
# ns.add_collection(Collection(build_docs), 'docs')
```

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `tasks` | `Lexicon` | 任务字典，键为任务名称（已做下划线/横线转换），值为 Task 对象 |
| `collections` | `Lexicon` | 子集合字典，键为集合名称，值为 Collection 对象 |
| `default` | `Optional[str]` | 默认任务名称，当调用集合自身名称时执行 |
| `name` | `Optional[str]` | 集合名称 |
| `loaded_from` | `Optional[str]` | 加载路径元数据 |
| `auto_dash_names` | `bool` | 是否自动转换下划线为短横线 |

---

## 添加任务

### add_task 方法

```python
add_task(
    task: Task,
    name: Optional[str] = None,
    aliases: Optional[Tuple[str, ...]] = None,
    default: Optional[bool] = None,
) -> None
```

将 Task 添加到集合中：

- `name`：绑定名称，默认取 `task.name`（即 `@task(name=...)` 指定的名称或函数名）
- `aliases`：额外的别名，**追加**到任务自身声明的别名之后
- `default`：是否设为集合默认任务；如未指定则使用 `task.is_default`（即 `@task(default=True)`）

```python
@task(name="compile", aliases=["c"])
def build(c):
    pass

ns = Collection()
# 以默认名称添加
ns.add_task(build)
# 任务名 'compile'，别名 'c'

# 覆盖名称并添加额外别名
ns.add_task(build, name="b", aliases=["build-all"])
# 任务名 'b'，别名 'c', 'build-all'

# 设为默认任务
@task
def all_tasks(c):
    pass
ns.add_task(all_tasks, default=True)
# ns.default == 'all-tasks'
```

> **冲突检测**：如果同名子集合已存在，抛出 `ValueError: Name conflict`。同一集合只能有一个默认任务，重复设置会抛出冲突错误。

---

## 添加子集合

### add_collection 方法

```python
add_collection(
    coll: Union[Collection, ModuleType],
    name: Optional[str] = None,
    default: Optional[bool] = None,
) -> None
```

将 Collection 添加为子命名空间：

- 如果传入的是 Python 模块，自动调用 `Collection.from_module(coll)` 转换
- `name` 默认取子集合自身的 `name` 属性；非根集合必须有名称
- `default=True` 将子集合的默认任务设为父集合的默认调用目标

```python
# 子集合作为命名空间
db_tasks = Collection('db')

@task
def migrate(c):
    c.run("alembic upgrade head")

@task
def seed(c):
    c.run("python seed.py")

db_tasks.add_task(migrate)
db_tasks.add_task(seed)

ns = Collection()
ns.add_collection(db_tasks)
# 可用标识: 'db.migrate', 'db.seed'

# 子集合默认任务
docs = Collection('docs')
@task
def build(c):
    c.run("sphinx-build")
docs.add_task(build, default=True)

ns.add_collection(docs, default=True)
# 调用 'inv docs' 等价于 'inv docs.build'
# 因为 docs 是 ns 的默认目标，直接 'inv' 也会执行 docs.build
```

---

## 任务查找

### __getitem__ 与 task_with_config

```python
__getitem__(name: Optional[str] = None) -> Task
task_with_config(name: Optional[str]) -> Tuple[Task, Dict[str, Any]]
```

通过名称查找任务，支持：

1. **直接名称**：`ns['build']` 返回对应 Task
2. **别名**：自动解析别名
3. **空名称/None**：返回默认任务（如未设置则抛出 `ValueError`）
4. **点分路径**：`ns['db.migrate']` 查找子集合中的任务
5. **子集合名**：`ns['db']` 返回子集合的默认任务

`task_with_config` 额外返回从根到目标任务路径上合并的配置字典。

```python
ns = Collection()
ns.add_task(build, default=True)
ns.add_collection(db_tasks)

# 直接查找
t = ns['build']

# 默认任务
t = ns[None]  # 返回 build
t = ns['']    # 返回 build

# 点分路径
t = ns['db.migrate']

# 子集合默认
t = ns['db']  # 如果 db 有默认任务则返回它

# 带配置查找
t, config = ns.task_with_config('db.migrate')
```

### __contains__

`name in collection` 判断任务是否存在（支持别名和子集合路径）。

### subcollection_from_path

```python
subcollection_from_path(path: str) -> Collection
```

按点分路径查找子集合（不返回任务）：

```python
db = ns.subcollection_from_path('db')
# 返回 db_tasks Collection 对象
```

---

## 从模块自动构建

### from_module 类方法

```python
@classmethod
from_module(
    cls,
    module: ModuleType,
    name: Optional[str] = None,
    config: Optional[Dict[str, Any]] = None,
    loaded_from: Optional[str] = None,
    auto_dash_names: Optional[bool] = None,
) -> Collection
```

从 Python 模块自动扫描 `Task` 实例构建 Collection：

1. 首先检查模块是否有显式命名空间 `ns` 或 `namespace` 变量（必须是 Collection 对象）
2. 如果没有显式命名空间，自动扫描模块中所有 `Task` 实例
3. 集合名称优先级：`name` 参数 > 模块 `ns`/`namespace` 的 name > 模块名的最后部分
4. 模块文档字符串 `__doc__` 会复制到 Collection
5. `config` 参数会合并到集合配置中

```python
# tasks.py
from invoke import task, Collection

@task
def build(c):
    """Build the project."""
    c.run("echo building")

@task
def test(c):
    """Run tests."""
    c.run("pytest")

# 显式命名空间（可选）
ns = Collection(build, test)
ns.configure({"sphinx": {"target": "_build"}})
```

```python
# 加载方式
import tasks
from invoke import Collection

ns = Collection.from_module(tasks)
# ns 包含 build 和 test 两个任务
```

---

## 命名空间配置

### configure 方法

```python
configure(options: Dict[str, Any]) -> None
```

将选项递归合并到集合的配置中。这些配置在任务执行时通过 [Config](config.md) 系统合并，任务可通过 `c.config.<key>` 访问。

```python
ns = Collection(build, test)
ns.configure({
    "sphinx": {
        "target": "_build",
        "opts": "-W -n",
    },
    "docker": {
        "image": "myapp:latest",
    },
})

@task
def docs(c):
    target = c.config.sphinx.target
    opts = c.config.sphinx.opts
    c.run(f"sphinx-build {opts} docs {target}")
```

> **最佳实践**：使用唯一前缀键（如 `sphinx.target` 而非 `target`），避免与其他配置冲突。

### configuration 方法

```python
configuration(taskpath: Optional[str] = None) -> Dict[str, Any]
```

获取集合（及其子集合路径上）的合并配置。如果指定 `taskpath`，返回该任务路径上的完整合并配置。

```python
# 获取本集合配置
config = ns.configuration()

# 获取子集合中任务的配置
config = ns.configuration('db.migrate')
```

---

## 名称转换

### transform 方法

```python
transform(name: str) -> str
```

根据 `auto_dash_names` 设置转换名称：

- `auto_dash_names=True`（默认）：将非首尾、非点号旁的下划线转为短横线
- `auto_dash_names=False`：反向，将短横线转为下划线

```python
ns = Collection()
print(ns.transform("my_task_name"))  # "my-task-name"
print(ns.transform("db.migrate_db")) # "db.migrate-db"
print(ns.transform("_private"))      # "_private" (首尾下划线保留)
```

这个转换会自动应用于 `add_task` 和 `add_collection` 中的名称。

---

## 任务名称列表

### task_names 属性

```python
@property
def task_names(self) -> Dict[str, List[str]]
```

返回扁平化的任务标识字典，键为主名（含点分路径前缀），值为别名列表。用于 `--list` 输出和 Parser 上下文生成。

```python
ns = Collection(build)
db = Collection('db')
db.add_task(migrate, default=True)
ns.add_collection(db)

print(ns.task_names)
# {
#     'build': ['b'],           # 假设 build 有别名 'b'
#     'db.migrate': [],         # 子集合任务带前缀
# }
```

### to_contexts 方法

```python
to_contexts(ignore_unknown_help: Optional[bool] = None) -> List[ParserContext]
```

将所有包含的任务转换为 Parser 上下文列表，供 CLI 参数解析使用。每个任务的参数通过 `task.get_arguments()` 获取。

---

## 点分路径查找规则

Collection 的点分路径查找遵循以下规则：

1. 以 `.` 分割路径，第一段是当前层级的键
2. 如果第一段在 `collections` 中，递归到子集合查找剩余路径
3. 如果第一段在 `tasks` 中，且没有剩余路径，返回该任务
4. 如果第一段在 `collections` 中且没有剩余路径，返回该子集合的默认任务
5. 空路径返回当前集合的默认任务

```
ns['db.migrate']    → 子集合 db → 任务 migrate
ns['db']            → 子集合 db → 默认任务（如已设置）
ns[''] / ns[None]   → 当前集合默认任务
ns['build']         → 当前层级任务 build
```

路径分割由内部方法 `_split_path` 实现：

```python
def _split_path(path: str) -> Tuple[str, str]:
    # "db.migrate.extra" → ("db", "migrate.extra")
    parts = path.split(".")
    coll = parts.pop(0)
    rest = ".".join(parts)
    return coll, rest
```

---

## 序列化

### serialized 方法

```python
serialized() -> Dict[str, Any]
```

返回适合 JSON 序列化的集合结构，用于 `--list-format=json` 输出：

```python
{
    "name": "collection-name",
    "help": "First line of docstring",
    "default": "default-task-name",
    "tasks": [
        {"name": "task-name", "help": "Task docstring", "aliases": ["alias1"]},
        ...
    ],
    "collections": [
        { ... 递归子集合 ... },
        ...
    ]
}
```

---

## 完整示例

```python
from invoke import Collection, task

# === 数据库子命名空间 ===
@task(aliases=["m"], help={"revision": "Revision to migrate to"})
def migrate(c, revision="head"):
    """Run database migrations."""
    c.run(f"alembic upgrade {revision}")

@task
def seed(c):
    """Seed database with initial data."""
    c.run("python -m app.db.seed")

@task
def reset(c):
    """Reset database (drop + migrate + seed)."""
    c.run("dropdb myapp && createdb myapp")
    migrate(c)
    seed(c)

db_ns = Collection('db')
db_ns.add_task(migrate)
db_ns.add_task(seed)
db_ns.add_task(reset, default=True)
db_ns.configure({"db": {"url": "postgresql://localhost/myapp"}})

# === 文档子命名空间 ===
@task
def build(c):
    """Build Sphinx documentation."""
    c.run("sphinx-build -W -b html docs _build")

@task
def clean(c):
    """Remove build artifacts."""
    c.run("rm -rf _build")

docs_ns = Collection('docs')
docs_ns.add_task(build, default=True)
docs_ns.add_task(clean)

# === 顶层命名空间 ===
@task
def test(c, coverage=False):
    """Run test suite."""
    cmd = "pytest"
    if coverage:
        cmd += " --cov=app --cov-report=term-missing"
    c.run(cmd)

@task(pre=[call(migrate, revision="head")])
def run(c, host="127.0.0.1", port=8000):
    """Run development server."""
    c.run(f"uvicorn app.main:app --host {host} --port {port}")

ns = Collection()
ns.add_task(test)
ns.add_task(run)
ns.add_collection(db_ns)
ns.add_collection(docs_ns)
ns.configure({"app": {"env": "development"}})
```

CLI 可用任务：

```
test                    # 运行测试
run                     # 运行服务器（前置执行 db migrate head）
db.migrate (db.m)       # 数据库迁移
db.seed                 # 数据库种子
db.reset                # 数据库重置（db 默认任务）
docs.build              # 构建文档（docs 默认任务）
docs.clean              # 清理文档
```
