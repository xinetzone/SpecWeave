---
type: wiki
title: Config 配置系统
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/config.toml"
description: PyInvoke Config 配置系统的完整 API 参考，涵盖七层合并优先级、DataProxy 属性代理、配置文件加载（YAML/JSON/Python）、环境变量集成与配置文件查找路径。
tags: [pyinvoke, config, dataproxy, merge, yaml, json, environment-variables, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/config.py
  - external/libs/pyinvoke/invoke/invoke/env.py
---
# Config 配置系统

## 概述

`Config` 是 Invoke 的配置管理核心，实现了一个多层级合并的配置系统。配置值从七个来源按优先级顺序合并，用户可以通过字典语法（`config['key']`）或属性语法（`config.key`）访问。嵌套字典自动包装为 `DataProxy` 对象，支持链式属性访问（`config.run.echo`）。

相关文档：[Context](context.md)、[Runner](runner.md)、[Collection](collection.md)

---

## 七层配置优先级

配置按以下顺序从低到高合并，后加载的层覆盖前面的层：

| 优先级 | 层级 | 属性 | 说明 | 加载时机 |
|--------|------|------|------|----------|
| 1（最低） | 默认值 | `_defaults` | 内置全局默认值，由 `global_defaults()` 返回 | 构造时 |
| 2 | Collection 配置 | `_collection` | 通过 `ns.configure()` 设置的命名空间配置 | 每个任务执行前 |
| 3 | 系统级配置文件 | `_system` | `/etc/invoke.yaml`（或 yml/json/py） | 构造时（非 lazy） |
| 4 | 用户级配置文件 | `_user` | `~/.invoke.yaml`（或 yml/json/py） | 构造时（非 lazy） |
| 5 | 项目级配置文件 | `_project` | 任务文件所在目录的 `invoke.yaml` | 项目加载后 |
| 6 | 环境变量 | `_env` | `INVOKE_*` 前缀的环境变量 | 每个任务执行前 |
| 7 | 运行时配置文件 | `_runtime` | `--config` 指定的配置文件 | CLI 指定后 |
| 8 | CLI 覆盖 | `_overrides` | 命令行标志（如 `--echo`、`--warn`） | CLI 解析后 |
| 9（最高） | 运行时修改 | `_modifications` | 代码中直接设置 `c.config.key = value` | 动态 |

> **注意**：还有一个特殊的 `_deletions` 层，记录通过 `del config['key']` 或 `pop()` 删除的键，在合并的最后一步应用。

### 合并顺序（merge 方法）

```python
def merge(self):
    self._config = {}
    merge_dicts(self._config, self._defaults)       # 1. 默认值
    merge_dicts(self._config, self._collection)     # 2. Collection 配置
    self._merge_file("system", "System-wide")       # 3. 系统配置文件
    self._merge_file("user", "Per-user")            # 4. 用户配置文件
    self._merge_file("project", "Per-project")      # 5. 项目配置文件
    merge_dicts(self._config, self._env)            # 6. 环境变量
    self._merge_file("runtime", "Runtime")          # 7. 运行时配置文件
    merge_dicts(self._config, self._overrides)      # 8. CLI 覆盖
    merge_dicts(self._config, self._modifications)  # 9. 运行时修改
    obliterate(self._config, self._deletions)       # 删除操作
```

---

## DataProxy 属性代理

`DataProxy` 是 `Config` 的基类，实现了嵌套字典+属性访问的混合模式。

### 核心特性

- **双重访问**：支持 `config['key']` 和 `config.key` 两种语法
- **自动嵌套代理**：字典值自动递归包装为 `DataProxy`，支持 `config.foo.bar.baz`
- **字典协议**：完整实现 `keys()`、`values()`、`items()`、`get()`、`pop()`、`update()`、`clear()`、`setdefault()`、`__contains__`、`__iter__`、`__len__`、`__eq__`
- **属性优先**：真实属性（类和实例方法）优先于配置键，不会被配置值覆盖
- **修改追踪**：通过 `__setitem__`、`__delitem__`、`pop` 等的修改会被追踪到 `_modifications` 和 `_deletions`

### 访问示例

```python
config = Config()

# 属性语法
print(config.run.echo)       # False
print(config.sudo.password)  # None

# 字典语法
print(config['run']['echo'])
print(config['sudo']['password'])

# 混合语法
print(config.run['echo'])
print(config['run'].echo)

# 存在性检查
if 'run' in config:
    print("run config exists")

# 迭代
for key in config:
    print(key)

# 字典方法
config_keys = list(config.keys())
run_items = dict(config.run.items())
```

### 重要注意事项

> **方法名冲突**：如果配置键名与 DataProxy/Config 的方法名相同（如 `keys`、`values`、`update`、`merge`、`load` 等），**必须使用字典语法**访问：
> ```python
> config['keys']      # 访问配置键 'keys'
> config.keys()       # 调用 dict 方法 keys()
> ```

### _set 方法

由于 `__setattr__` 被重写为配置键赋值，设置真实实例属性必须使用 `_set()`：

```python
# 正确：设置真实属性
self._set(_config={})
self._set(my_attr=value)

# 错误：这会设置配置键而非实例属性
self.my_attr = value  # → self['my_attr'] = value
```

---

## Config 构造函数

```python
Config(
    overrides: Optional[Dict[str, Any]] = None,
    defaults: Optional[Dict[str, Any]] = None,
    system_prefix: Optional[str] = None,
    user_prefix: Optional[str] = None,
    project_location: Optional[PathLike] = None,
    runtime_path: Optional[PathLike] = None,
    lazy: bool = False,
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `overrides` | `Dict` | `{}` | 最高优先级的覆盖配置（通常来自 CLI 标志） |
| `defaults` | `Dict` | `global_defaults()` | 最低优先级的默认值 |
| `system_prefix` | `str` | `/etc/`（Unix）/`None`（Windows） | 系统级配置文件路径前缀 |
| `user_prefix` | `str` | `~/.` | 用户级配置文件路径前缀 |
| `project_location` | `PathLike` | `None` | 项目配置文件所在目录（通常是 tasks.py 所在目录） |
| `runtime_path` | `PathLike` | `None` | 运行时配置文件的完整路径（`--config` 指定） |
| `lazy` | `bool` | `False` | 是否延迟加载（不自动加载系统/用户配置文件） |

### 类属性（可被子类覆盖）

| 属性 | 默认值 | 说明 |
|------|--------|------|
| `prefix` | `"invoke"` | 配置文件和环境变量的基础前缀 |
| `file_prefix` | `None`（→ 使用 `prefix`） | 配置文件基础名 |
| `env_prefix` | `None`（→ 使用 `prefix.upper()`） | 环境变量前缀，默认 `"INVOKE_"` |

---

## 全局默认值

`global_defaults()` 返回 Invoke 的内置默认配置：

```python
{
    "run": {
        "asynchronous": False,
        "disown": False,
        "dry": False,
        "echo": False,
        "echo_stdin": None,
        "encoding": None,
        "env": {},
        "err_stream": None,
        "fallback": True,
        "hide": None,
        "in_stream": None,
        "out_stream": None,
        "echo_format": "\033[1;37m{command}\033[0m",  # 粗体白色
        "pty": False,
        "replace_env": False,
        "shell": "bash"（Unix）/ "cmd.exe"（Windows）,
        "warn": False,
        "watchers": [],
    },
    "runners": {"local": Local},
    "sudo": {
        "password": None,
        "prompt": "[sudo] password: ",
        "user": None,
    },
    "tasks": {
        "auto_dash_names": True,
        "collection_name": "tasks",
        "dedupe": True,
        "executor_class": None,
        "ignore_unknown_help": False,
        "search_root": None,
    },
    "timeouts": {"command": None},
}
```

---

## 配置文件加载

### 支持的文件格式

按优先级顺序搜索以下后缀（`_file_suffixes`）：
1. `.yaml` / `.yml` — 使用 `yaml.safe_load()` 解析
2. `.json` — 使用 `json.load()` 解析
3. `.py` — 作为 Python 模块执行，提取非 `__` 开头的变量（不支持模块类型值）

每个层级只加载找到的第一个文件。

### 配置文件查找路径

| 层级 | 默认路径模式 | 示例（Unix） |
|------|-------------|-------------|
| 系统级 | `{system_prefix}{file_prefix}.{ext}` | `/etc/invoke.yaml` |
| 用户级 | `{user_prefix}{file_prefix}.{ext}` | `~/.invoke.yaml` |
| 项目级 | `{project_location}{file_prefix}.{ext}` | `/home/user/project/invoke.yaml` |
| 运行时 | `{runtime_path}`（完整路径） | `/path/to/custom-config.yaml` |

### 加载方法

| 方法 | 说明 |
|------|------|
| `load_system(merge=True)` | 加载系统级配置文件 |
| `load_user(merge=True)` | 加载用户级配置文件 |
| `load_project(merge=True)` | 加载项目级配置文件 |
| `load_runtime(merge=True)` | 加载运行时配置文件 |
| `load_base_conf_files()` | 依次加载系统和用户配置（非 lazy 时自动调用） |
| `load_shell_env()` | 加载环境变量配置 |
| `load_collection(data, merge=True)` | 加载 Collection 配置数据 |
| `load_defaults(data, merge=True)` | 设置/替换默认值层 |
| `load_overrides(data, merge=True)` | 设置/替换覆盖层 |

每个 `load_*` 方法的 `merge` 参数控制是否在加载后立即调用 `merge()` 更新合并视图。

### Python 配置文件

`.py` 配置文件会被作为模块执行，提取顶层变量（排除 `__` 开头的特殊成员和模块类型）：

```python
# invoke.py
run = {
    "echo": True,
    "shell": "/bin/zsh",
}
sudo = {
    "password": "secret",
}
```

### 设置项目位置

```python
set_project_location(path: Union[PathLike, str, None]) -> None
```

设置项目配置文件的搜索目录，会自动追加路径分隔符。Loader 在发现 tasks.py 后调用此方法。

### 设置运行时路径

```python
set_runtime_path(path: Optional[PathLike]) -> None
```

设置运行时配置文件的完整路径（对应 CLI 的 `--config`/`-c` 选项）。

---

## 环境变量集成

环境变量通过 `Environment` 类（`env.py`）加载，遵循以下规则：

1. **前缀匹配**：只加载以 `INVOKE_` 开头的环境变量（前缀可通过 `env_prefix` 配置）
2. **已知键映射**：环境变量名映射为配置键路径，通过 `_` 分隔嵌套层级
3. **类型转换**：基于已有配置值的类型进行类型转换：
   - `bool` 类型：`"0"` 或 `""` → `False`，其他 → `True`
   - `str` 类型：直接使用字符串值
   - `None`：直接使用字符串值
   - 数值类型（`int`/`float` 等）：调用类型构造器转换
   - `list`/`tuple`：抛出 `UncastableEnvVar`（不支持从环境变量设置列表）
4. **歧义检测**：如果两个不同路径映射到同一个环境变量名，抛出 `AmbiguousEnvVar`

### 环境变量示例

```bash
# 配置 run.echo = True
INVOKE_RUN_ECHO=1 inv build

# 配置 sudo.password = "mypass"
INVOKE_SUDO_PASSWORD=mypass inv setup

# 配置 tasks.dedupe = False
INVOKE_TASKS_DEDUPE=0 inv deploy

# 配置 run.shell = "/bin/zsh"
INVOKE_RUN_SHELL=/bin/zsh inv build
```

映射规则：`INVOKE_RUN_ECHO` → `_crawl` 递归遍历配置树 → 找到 `config.run.echo` → 设置值。

---

## clone 方法

```python
clone(into: Optional[Type[Config]] = None) -> Config
```

创建配置对象的副本：

- 递归重建所有字典值（使用浅拷贝 `copy.copy`，避免 `deepcopy` 的问题）
- 非字典叶值使用 `copy.copy` 复制
- 列表、元组等复合非字典对象保持共享引用
- `into` 参数允许升级为 Config 子类（如 Fabric 的 Config 子类）
- 新对象自动加载系统和用户配置文件

```python
from invoke import Config

config = Config(overrides={"run": {"echo": True}})
cloned = config.clone()
print(cloned.run.echo)  # True
```

---

## merge_dicts 函数

```python
merge_dicts(base: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]
```

递归合并两个字典（修改 `base`）：

- 两边都是字典的键：递归合并
- 一边是字典另一边不是：抛出 `AmbiguousMergeError`
- 非字典叶值：使用 `copy.copy` 复制后覆盖
- 返回修改后的 `base`

```python
from invoke.config import merge_dicts

base = {"a": 1, "b": {"c": 2}}
updates = {"b": {"d": 3}, "e": 4}
merge_dicts(base, updates)
# base = {"a": 1, "b": {"c": 2, "d": 3}, "e": 4}
```

---

## 配置示例

### YAML 配置文件

```yaml
# invoke.yaml
run:
  echo: true
  warn: true
  shell: /bin/zsh

sudo:
  password: "my-sudo-password"  # nosec - 示例占位符，非真实密码

tasks:
  auto_dash_names: true
  dedupe: true

# 自定义命名空间配置
sphinx:
  target: _build
  opts: -W -n
```

### JSON 配置文件

```json
{
  "run": {
    "echo": true,
    "pty": true
  },
  "sudo": {
    "user": "deploy"
  }
}
```

### 代码中使用配置

```python
from invoke import task, Config, Collection

# 在 tasks.py 中通过 Collection.configure() 设置
ns = Collection()
ns.configure({
    "sphinx": {
        "target": "_build/html",
        "opts": "-W -b html",
    },
    "docker": {
        "image": "myapp:latest",
        "registry": "registry.example.com",
    },
})

@task
def docs(c):
    # 访问配置
    target = c.sphinx.target
    opts = c.sphinx.opts
    c.run(f"sphinx-build {opts} docs {target}")

@task
def build_image(c):
    image = c.docker.image
    registry = c.docker.registry
    tag = f"{registry}/{image}"
    
    # 运行时修改配置（影响后续 run 调用）
    c.config.run.echo = True
    c.run(f"docker build -t {tag} .")
    c.run(f"docker push {tag}")
```

### 手动创建 Config

```python
from invoke import Config

# 基本用法
config = Config()
print(config.run.echo)  # False（默认值）

# 带覆盖
config = Config(overrides={"run": {"echo": True, "warn": True}})
print(config.run.echo)  # True

# 自定义默认值
config = Config(defaults={
    "run": {"shell": "/bin/zsh"},
    "myapp": {"env": "development"},
})

# 延迟加载（不自动加载系统/用户配置）
config = Config(lazy=True)
# ... 手动控制加载时机 ...
config.load_user()
config.merge()
```
