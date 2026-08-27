---
type: wiki
title: Program CLI 入口
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/program.toml"
description: PyInvoke Program CLI 入口类的完整 API 参考，涵盖核心 CLI 选项、任务发现、--list/--help/--complete 行为、执行流程与二进制分发。
tags: [pyinvoke, program, cli, entrypoint, binary, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/program.py
---
# Program CLI 入口

## 概述

`Program` 是 Invoke 的顶层 CLI 入口管理器，负责协调整个命令行执行流程：配置初始化、参数解析、任务集合加载、任务执行。它既用于内置的 `inv`/`invoke` 命令，也支持将 Invoke 任务集合打包为独立的命令行程序分发。

相关文档：[Parser](parser.md)、[Loader](loader.md)、[Collection](collection.md)、[Executor](executor.md)、[Config](config.md)

---

## 两种运行模式

Program 支持两种运行模式：

### 1. 任务运行器模式（默认）

不指定 `namespace` 参数时，Program 像 `invoke` 命令一样工作：
- 从文件系统搜索并加载 tasks.py（或指定的 `--collection`）
- 暴露 `--list`、`--collection`、`--search-root`、`--no-dedupe` 等任务相关选项
- 用户可以调用任意发现的任务

### 2. 绑定命名空间模式（二进制分发）

指定 `namespace=Collection(...)` 参数时，Program 将该集合作为固定子命令集：
- 不加载外部 tasks 文件
- 移除任务相关的核心选项（`--collection`、`--no-dedupe`、`--search-root`）
- `--help` 显示内置子命令列表
- 适合将任务集打包为独立 CLI 工具

---

## 构造函数

```python
Program(
    version: Optional[str] = None,
    namespace: Optional[Collection] = None,
    name: Optional[str] = None,
    binary: Optional[str] = None,
    loader_class: Optional[Type[Loader]] = None,
    executor_class: Optional[Type[Executor]] = None,
    config_class: Optional[Type[Config]] = None,
    binary_names: Optional[List[str]] = None,
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `version` | `str` | `"unknown"` | 程序版本号，用于 `--version` 输出 |
| `namespace` | `Collection` | `None` | 绑定的任务集合；None 表示从文件系统加载 |
| `name` | `str` | argv[0] 的首字母大写形式 | 程序显示名称（如 "Invoke"） |
| `binary` | `str` | argv[0] | 帮助文本中显示的二进制名（如 "inv[oke]"） |
| `binary_names` | `List[str]` | `[argv[0]]` | 补全脚本使用的二进制名列表（如 `["inv", "invoke"]`） |
| `loader_class` | `Type[Loader]` | `FilesystemLoader` | 任务加载器类 |
| `executor_class` | `Type[Executor]` | `Executor` | 任务执行器类（也可通过 `tasks.executor_class` 配置覆盖） |
| `config_class` | `Type[Config]` | `Config` | 配置类 |

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `argv` | `List[str]` | 归一化后的命令行参数 |
| `config` | `Config` | 配置对象 |
| `collection` | `Collection` | 加载的任务集合 |
| `tasks` | `List` | 待执行的任务列表 |
| `core` | `ParseResult` | 核心参数解析结果 |
| `parser` | `Parser` | 参数解析器 |

### 格式化常量

| 常量 | 值 | 说明 |
|------|----|------|
| `leading_indent_width` | `2` | 前导缩进宽度 |
| `leading_indent` | `"  "` | 前导缩进字符串 |
| `indent_width` | `4` | 缩进宽度 |
| `indent` | `"    "` | 缩进字符串 |
| `col_padding` | `3` | 列间距 |

---

## 核心 CLI 选项

通过 `core_args()` 定义的全局选项（始终可用）：

| 长标志 | 短标志 | 类型 | 默认值 | 说明 |
|--------|--------|------|--------|------|
| `--command-timeout` | `-T` | `int` | `None` | 全局命令执行超时（秒） |
| `--complete` | — | `bool` | `False` | 打印 Tab 补全候选 |
| `--config` | `-f` | `str` | `None` | 指定运行时配置文件路径 |
| `--debug` | `-d` | `bool` | `False` | 启用调试输出 |
| `--dry` | `-R` | `bool` | `False` | 干跑模式（只回显命令） |
| `--echo` | `-e` | `bool` | `False` | 执行前回显命令 |
| `--help` | `-h` | 可选值 | `None` | 显示帮助（可指定任务名显示任务帮助） |
| `--hide` | — | `str` | `None` | 设置 `run()` 的 hide 默认值 |
| `--list` | `-l` | 可选值 | `None` | 列出可用任务（可指定命名空间限制范围） |
| `--list-depth` | `-D` | `int` | `0` | 列出任务时显示的层级深度 |
| `--list-format` | `-F` | `str` | `"flat"` | 列表格式：`flat`（默认）、`nested`、`json` |
| `--print-completion-script` | — | `str` | `""` | 打印指定 shell 的补全脚本（bash/zsh/fish） |
| `--prompt-for-sudo-password` | — | `bool` | `False` | 启动时提示输入 sudo 密码 |
| `--pty` | `-p` | `bool` | `False` | 使用 PTY 执行命令 |
| `--version` | `-V` | `bool` | `False` | 显示版本并退出 |
| `--warn-only` | `-w` | `bool` | `False` | 命令失败时只警告不退出 |
| `--write-pyc` | — | `bool` | `False` | 允许生成 .pyc 文件（默认禁用） |

### 任务运行器专用选项

仅在无绑定命名空间时可用（通过 `task_args()` 定义）：

| 长标志 | 短标志 | 类型 | 默认值 | 说明 |
|--------|--------|------|--------|------|
| `--collection` | `-c` | `str` | `None` | 指定要加载的集合名称（替代默认的 "tasks"） |
| `--no-dedupe` | — | `bool` | `False` | 禁用任务去重 |
| `--search-root` | `-r` | `str` | `None` | 指定查找任务模块的根目录 |

---

## run 方法（主入口）

```python
run(argv: Optional[List[str]] = None, exit: bool = True) -> None
```

执行主 CLI 逻辑。

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `argv` | `List[str]`/`str`/`None` | `None`（→ `sys.argv`） | 命令行参数 |
| `exit` | `bool` | `True` | 出错时是否调用 `sys.exit()` |

### 执行流程

```
run(argv)
  │
  ├─ 1. create_config()          # 创建初始 Config 对象
  ├─ 2. parse_core(argv)         # 解析核心 CLI 参数
  │    ├─ normalize_argv()       # 归一化 argv
  │    ├─ parse_core_args()      # 用 Parser 解析核心参数
  │    ├─ 设置 sys.dont_write_bytecode
  │    ├─ 启用 debug 日志（如果 --debug）
  │    ├─ --version → print_version() → Exit
  │    └─ --print-completion-script → 打印补全脚本 → Exit
  │
  ├─ 3. parse_collection()       # 加载任务集合
  │    ├─ 如果有绑定 namespace → 直接使用
  │    ├─ 无 namespace 且裸 --help → print_help() → Exit
  │    └─ load_collection()      # 使用 Loader 从文件系统加载
  │
  ├─ 4. parse_tasks()            # 解析任务名和任务参数
  ├─ 5. parse_cleanup()          # 解析后处理
  │    ├─ 裸 --help → print_help() → Exit
  │    ├─ --help <task> → print_task_help() → Exit
  │    ├─ --list / --list <ns> → list_tasks() → Exit
  │    ├─ --complete → 补全候选
  │    └─ 无任务且无默认 → print_help() → Exit
  │
  ├─ 6. update_config()          # 更新配置（运行时配置 + CLI 覆盖）
  └─ 7. execute()                # 创建 Executor 并执行任务
```

### 异常处理

`run()` 捕获以下异常并决定退出行为：

| 异常 | 处理方式 |
|------|----------|
| `ParseError` | 打印错误到 stderr，退出码 1 |
| `Exit` | 如果有消息则打印，使用 `e.code` 作为退出码 |
| `UnexpectedExit` | 如果结果被隐藏，打印到 stderr，使用退出码 |
| `KeyboardInterrupt` | 退出码 1 |

当 `exit=False` 时，这些异常不会导致 sys.exit()，主要用于测试。

---

## normalize_argv 方法

```python
normalize_argv(argv: Optional[List[str]]) -> None
```

将 argv 归一化为字符串列表：
- `None` → 使用 `sys.argv`
- 字符串 → 按空格 `split()`
- 列表 → 直接使用

结果设置到 `self.argv`。

---

## parse_core_args 方法

```python
parse_core_args() -> None
```

使用 Parser 解析核心参数：
1. 创建包含 `initial_context`（核心参数）的 Parser，设置 `ignore_unknown=True`
2. 解析 `argv[1:]`（跳过程序名）
3. 结果存到 `self.core`
4. 未解析部分存起来供后续任务解析使用

---

## load_collection 方法

```python
load_collection() -> None
```

使用 Loader 从文件系统加载任务集合：

1. 根据 `--collection`/`-c` 参数确定集合名称（默认 "tasks"）
2. 根据 `--search-root`/`-r` 参数确定搜索根目录（默认 CWD）
3. 创建 Loader 实例并加载集合
4. 设置项目配置位置并加载项目级配置文件
5. 加载的集合存到 `self.collection`

如果找不到集合文件，抛出 `CollectionNotFound`（在 `run()` 中被捕获处理）。

---

## parse_tasks 方法

```python
parse_tasks() -> None
```

解析任务名和任务参数：

1. 使用 Collection 生成任务 ParserContexts（`collection.to_contexts()`）
2. 创建包含核心参数上下文和任务上下文的 Parser
3. 解析核心解析后的剩余参数
4. 结果存到 `self.tasks`（ParserContext 列表，供 Executor.execute() 使用）

---

## parse_cleanup 方法

处理解析后的各种退出场景：

### --help 行为

- `--help`（无值）：在绑定命名空间模式下或已加载集合后，打印全局帮助并退出
- `--help <taskname>`：打印指定任务的帮助信息并退出
- 无命名空间 + 裸 --help：在加载集合前打印核心帮助

### --list 行为

- `--list` / `-l`：列出所有任务
- `--list <namespace>` / `-l <ns>`：列出指定命名空间下的任务
- `--list-format flat|nested|json`：设置输出格式
  - `flat`：扁平列表，点分路径（默认）
  - `nested`：嵌套缩进显示
  - `json`：JSON 格式（使用 `collection.serialized()`）
- `--list-depth N` / `-D N`：限制显示深度

### --complete 行为

调用 `complete()` 函数生成 Shell 补全候选。

### 无任务处理

如果没有指定任何任务且集合没有默认任务，打印全局帮助作为回退。

---

## update_config 方法

```python
update_config(merge: bool = True) -> None
```

将解析结果更新到配置对象：

1. 从核心参数构建覆盖配置：
   - `--warn-only` → `run.warn = True`
   - `--pty` → `run.pty = True`
   - `--hide` → `run.hide = <value>`
   - `--echo` → `run.echo = True`
   - `--dry` → `run.dry = True`
   - `--no-dedupe` → `tasks.dedupe = False`
   - `--command-timeout` → `timeouts.command = <value>`
   - `--prompt-for-sudo-password` → 调用 `getpass.getpass()` 获取密码
2. 设置运行时配置路径（`--config` 或 `INVOKE_RUNTIME_CONFIG` 环境变量）
3. 加载运行时配置
4. 调用 `config.merge()` 更新合并视图

---

## execute 方法

```python
execute() -> None
```

创建 Executor 并执行任务：

1. 确定 Executor 类：构造函数的 `executor_class` 参数，或配置中 `tasks.executor_class`（格式为 `"module.path:ClassName"` 或 `"module.path.ClassName"`，使用 `rpartition(".")` 分割）
2. 创建 Executor 实例，传入 collection、config 和 core 解析结果
3. 调用 `executor.execute(*self.tasks)` 执行任务

---

## 输出方法

### print_version

打印 `"{name} {version}"` 格式的版本信息。

### print_help

打印使用方法和核心选项帮助：

```
Usage: {binary} [--core-opts] {task1 [--task1-opts] ... taskN [--taskN-opts]}

Core options:
  ... 格式化的选项列表 ...
```

绑定命名空间模式下，usage 后缀为 `<subcommand> [--subcommand-opts] ...`，并追加任务列表。

### print_task_help

打印指定任务的详细帮助（文档字符串、参数列表、别名等）。

### list_tasks

根据 `list_format` 输出任务列表：
- `flat`：两列格式，左列为任务名（含别名），右列为帮助文本
- `nested`：嵌套缩进显示命名空间和任务
- `json`：调用 `collection.serialized()` 输出 JSON

### print_columns

将 `(flag, help_text)` 元组列表格式化为对齐的两列输出。

---

## 作为独立二进制分发

使用 Program 的 `namespace` 参数可以将任务集合打包为独立 CLI 工具：

```python
# mytool.py 或 setup.py 入口点
from invoke import Program, Collection, task

@task
def build(c, clean=False):
    """Build the project."""
    if clean:
        c.run("rm -rf dist/")
    c.run("python -m build")

@task
def test(c, coverage=False):
    """Run tests."""
    cmd = "pytest"
    if coverage:
        cmd += " --cov=myapp"
    c.run(cmd)

@task(pre=[build], post=[test], default=True)
def all(c):
    """Build and test everything."""
    print("All done!")

ns = Collection(build, test, all)

program = Program(
    version="1.0.0",
    namespace=ns,
    name="MyTool",
    binary="mytool",
    binary_names=["mytool"],
)

if __name__ == "__main__":
    program.run()
```

在 `setup.py`/`pyproject.toml` 中注册入口点：

```toml
[project.scripts]
mytool = "mymodule:program.run"
```

---

## 完整使用示例

```python
from invoke import Program, Collection, task, Config

# 使用自定义 Config 子类
class MyConfig(Config):
    @staticmethod
    def global_defaults():
        defaults = Config.global_defaults()
        defaults["run"]["echo"] = True  # 默认回显命令
        defaults["myapp"] = {"env": "development"}
        return defaults

@task
def hello(c, name="world"):
    """Say hello."""
    print(f"Hello, {name}!")

ns = Collection(hello)

# 创建程序实例
program = Program(
    version="2.0.0",
    namespace=ns,
    name="GreetingTool",
    binary="greet",
    config_class=MyConfig,
)

# 命令行调用:
# greet hello                   # Hello, world!
# greet hello --name Alice      # Hello, Alice!
# greet --help                  # 显示帮助
# greet --version               # GreetingTool 2.0.0
# greet --list                  # 列出任务
```
