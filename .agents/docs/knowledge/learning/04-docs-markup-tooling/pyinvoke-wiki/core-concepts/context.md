---
type: wiki
title: Context 执行上下文
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/pyinvoke-wiki/core-concepts/context.toml"
description: PyInvoke Context 执行上下文的完整 API 参考，涵盖 run/sudo 方法、cd/prefix 上下文管理器、Config 代理访问与 MockContext 测试替身。
tags: [pyinvoke, context, run, sudo, cd, prefix, mockcontext, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/context.py
---
# Context 执行上下文

## 概述

`Context` 是 Invoke 任务函数的第一个参数（通常命名为 `c`），它是状态传递和命令执行的核心入口。Context 封装了配置访问、Shell 命令执行（本地和 sudo）、工作目录管理、命令前缀管理等功能，并通过 `DataProxy` 代理机制直接访问配置值。

相关文档：[Config](config.md)、[Runner](runner.md)、[Task](task.md)、[Watcher](watchers.md)

---

## Context 继承关系

```
DataProxy → Context
DataProxy → Context → MockContext
```

Context 继承自 [DataProxy](config.md#dataproxy-属性代理)，因此可以通过属性访问和字典访问两种方式读取配置。

---

## 构造函数

```python
Context(
    config: Optional[Config] = None,
    remainder: str = "",
)
```

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `config` | `Config` | `Config()` | 基础配置对象，默认创建匿名空配置 |
| `remainder` | `str` | `""` | CLI 中 `--` 之后的剩余文本 |

通常不需要手动创建 Context——它由执行器在任务调用时自动创建。但在测试或库代码中可以手动实例化。

### 核心属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `config` | `Config` | 完整合并后的配置对象（可读写） |
| `cwd` | `str` | property，当前工作目录路径（考虑 cd 嵌套） |
| `command_prefixes` | `List[str]` | 待执行命令的前缀列表（由 `prefix` 上下文管理器维护） |
| `command_cwds` | `List[str]` | 工作目录栈（由 `cd` 上下文管理器维护） |
| `remainder` | `str` | CLI `--` 后的剩余参数 |

### 配置代理访问

Context 通过 DataProxy 机制代理到 `config` 属性，可以用属性语法或字典语法访问配置：

```python
@task
def deploy(c):
    # 以下三种方式等价
    print(c.config.run.echo)
    print(c["run"]["echo"])
    print(c.run.echo)
```

---

## run 方法

```python
run(command: str, **kwargs) -> Result
```

执行本地 Shell 命令，是 Invoke 最常用的方法。内部使用配置中 `runners.local` 指定的 Runner 类（默认为 `Local`）执行命令。

### 常用参数

所有 `**kwargs` 传递给 `Runner.run()`，常用参数包括：

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `warn` | `bool` | `False` | 命令失败时是否只警告不抛出异常 |
| `hide` | `bool`/`str`/`None` | `None` | 隐藏输出：`True`/`"both"` 隐藏全部，`"stdout"`/`"stderr"` 隐藏对应流 |
| `echo` | `bool` | `False` | 执行前是否打印命令本身 |
| `pty` | `bool` | `False` | 是否通过伪终端 (PTY) 执行（适合交互式程序） |
| `fallback` | `bool` | `True` | PTY 模式失败时是否回退到非 PTY 模式 |
| `watchers` | `List[StreamWatcher]` | `[]` | 流监控器列表，用于自动响应密码提示等 |
| `env` | `Dict[str, str]` | `{}` | 子进程环境变量 |
| `replace_env` | `bool` | `False` | 是否用给定 env 替换整个环境（而非合并） |
| `encoding` | `str` | `"utf-8"` | 输出编码 |
| `out_stream` | 文件对象 | `None` | 实时标准输出目标 |
| `err_stream` | 文件对象 | `None` | 实时标准错误目标 |
| `in_stream` | 文件对象 | `None` | 标准输入源 |
| `asynchronous` | `bool` | `False` | 是否异步执行（返回 Promise 而非 Result） |
| `disown` | `bool` | `False` | 是否完全脱离进程（后台运行） |
| `echo_stdin` | `bool` | `True` | 是否回显标准输入 |
| `encoding_errors` | `str` | `"strict"` | 编码错误处理策略 |

### 返回值：Result

`run()` 返回 `Result` 对象（详见 [Runner](runner.md)），包含：

```python
result = c.run("ls -la", hide=True)
print(result.exited)     # 退出码 (0 表示成功)
print(result.stdout)     # 标准输出文本
print(result.stderr)     # 标准错误文本
print(result.ok)         # 是否成功 (exited == 0)
print(result.failed)     # 是否失败 (exited != 0)
print(result.command)    # 执行的命令字符串
print(result.return_code)  # 退出码别名
```

### 异步执行

设置 `asynchronous=True` 返回 `Promise` 对象，非阻塞：

```python
promise = c.run("long-running-command", asynchronous=True)
# ... 做其他事情 ...
result = promise.join()  # 等待完成并获取结果
```

### 异常处理

默认情况下，命令退出码非 0 时抛出 `Failure` 异常：

```python
from invoke.exceptions import Failure

try:
    c.run("exit 1")
except Failure as f:
    print(f"Command failed: {f.result.command}")
    print(f"Exit code: {f.result.exited}")
    print(f"Stderr: {f.result.stderr}")

# 使用 warn=True 避免抛出
result = c.run("exit 1", warn=True)
if result.failed:
    print("Command failed but continuing...")
```

### 基本示例

```python
@task
def build(c):
    # 简单执行
    c.run("echo Hello World")
    
    # 隐藏输出并捕获结果
    result = c.run("git rev-parse --short HEAD", hide=True)
    commit = result.stdout.strip()
    print(f"Building commit {commit}")
    
    # 回显命令
    c.run("pip install -r requirements.txt", echo=True)
    
    # 失败不中断
    c.run("rm -rf build/", warn=True)
    
    # 设置环境变量
    c.run("echo $MY_VAR", env={"MY_VAR": "hello"})
    
    # PTY 模式（适合需要 TTY 的命令如 sudo、docker run -it）
    c.run("docker run -it ubuntu bash", pty=True)
```

---

## sudo 方法

```python
sudo(command: str, **kwargs) -> Result
```

以 `sudo` 执行命令，内置密码自动响应功能。

### sudo 特殊参数

| 参数 | 类型 | 默认配置 | 说明 |
|------|------|----------|------|
| `password` | `str` | `sudo.password` 配置项 | sudo 密码（运行时覆盖配置） |
| `user` | `str` | `sudo.user` 配置项（默认 `None`，即 root） | 以哪个用户执行 |

### 配置项

sudo 行为通过 `sudo.*` 配置树控制：

| 配置键 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `sudo.password` | `str` | `""` | sudo 密码 |
| `sudo.prompt` | `str` | `r"\[sudo\] password:"` | 匹配 sudo 密码提示的正则模式 |
| `sudo.user` | `Optional[str]` | `None` | 目标用户，None 表示 root |

### 工作机制

`sudo()` 内部执行以下操作：

1. 构建 sudo 命令字符串：`sudo -S -p '<prompt>' [-H -u <user>] <command>`
   - `-S`：从 stdin 读取密码
   - `-p`：自定义密码提示，方便监控器匹配
   - `-H`：设置目标用户的 `$HOME`（指定 `-u` 时自动添加）
2. 添加一个 `FailingResponder` 流监控器：
   - 匹配密码提示模式
   - 自动输入配置的密码
   - 检测认证失败消息 `"Sorry, try again.\n"`，失败时抛出 `AuthFailure`
3. 合并用户提供的其他 watchers
4. 调用 `run()` 执行

### 使用示例

```python
@task
def setup(c):
    # 使用配置中的密码
    c.sudo("apt-get update")
    
    # 运行时指定密码
    c.sudo("apt-get install -y nginx", password="mypassword")
    
    # 以其他用户执行
    c.sudo("whoami", user="www-data")
    
    # 如果想手动输入密码，直接用 run
    c.run("sudo apt-get update")
```

---

## cd 上下文管理器

```python
@contextmanager
cd(path: Union[PathLike, str]) -> Generator[None, None, None]
```

维护工作目录状态。在 `with c.cd(path)` 块内的所有 `run`/`sudo` 调用都会自动添加 `cd <path> &&` 前缀。

### 特性

- **解决了 Shell 命令的状态丢失问题**：由于每个 `run()` 都是独立子进程，`c.run("cd /tmp")` 不会影响后续命令；使用 `c.cd()` 上下文管理器可以模拟目录切换
- **支持嵌套**：相对路径基于外层 cd 的路径解析
- **支持 Path 对象**：v1.5+ 接受任何定义了 `__str__` 的对象（如 `pathlib.Path`）
- **自动转义空格**：路径中的空格会自动转义

### 示例

```python
@task
def build(c):
    # 基本用法
    with c.cd("/var/www"):
        c.run("ls")  # 实际执行: cd /var/www && ls
    
    # 嵌套使用
    with c.cd("/var/www"):
        c.run("ls")  # cd /var/www && ls
        with c.cd("site1"):
            c.run("ls")  # cd /var/www/site1 && ls
    
    # 使用 pathlib
    from pathlib import Path
    with c.cd(Path.home() / "project"):
        c.run("make")
    
    # 包含空格的路径
    with c.cd("/path/to/my project"):
        c.run("ls")  # cd /path/to/my\ project && ls
```

### cwd 属性

`c.cwd` 属性返回当前工作目录的完整路径，考虑 cd 嵌套和绝对/相对路径：

```python
@task
def show_cwd(c):
    print(f"Current cwd: {c.cwd}")  # "" (空，即当前目录)
    with c.cd("/var/www"):
        print(f"Current cwd: {c.cwd}")  # "/var/www"
        with c.cd("site"):
            print(f"Current cwd: {c.cwd}")  # "/var/www/site"
```

路径解析逻辑：从 `command_cwds` 栈中找到最后一个以 `/` 或 `~` 开头的绝对路径，然后拼接其后的所有相对路径。

---

## prefix 上下文管理器

```python
@contextmanager
prefix(command: str) -> Generator[None, None, None]
```

为块内所有 `run`/`sudo` 调用添加命令前缀（通过 `&&` 连接）。常用于设置 shell 环境，如激活虚拟环境、设置环境变量等。

### 特性

- **嵌套支持**：多个 prefix 可以嵌套，内层 prefix 会叠加在外层之上
- **与 cd 兼容**：cd 命令始终在最前面
- **状态维护**：退出 with 块时自动移除前缀

### 示例

```python
@task
def migrate(c):
    # 激活虚拟环境后执行命令
    with c.prefix("workon myvenv"):
        c.run("./manage.py migrate")
        # 实际执行: workon myvenv && ./manage.py migrate
    
    # cd + prefix 组合
    with c.cd("/opt/myapp"):
        with c.prefix("source .env/bin/activate"):
            c.run("pip install -r requirements.txt")
            # cd /opt/myapp && source .env/bin/activate && pip install ...
            c.run("python manage.py collectstatic --noinput")
            # cd /opt/myapp && source .env/bin/activate && python manage.py ...
    
    # 嵌套 prefix
    with c.prefix("export APP_ENV=production"):
        c.run("echo $APP_ENV")
        with c.prefix("export DEBUG=0"):
            c.run("echo $APP_ENV $DEBUG")
            # export APP_ENV=production && export DEBUG=0 && echo ...
```

### _prefix_commands 内部方法

```python
_prefix_commands(command: str) -> str
```

将 `command_cwds`（如果有）和 `command_prefixes` 与目标命令用 `&&` 连接：

1. 如果 `cwd` 非空，先添加 `cd <cwd>`
2. 然后追加所有 `command_prefixes`
3. 最后追加目标命令

```python
# 最终命令格式: cd <dir> && prefix1 && prefix2 && command
```

---

## MockContext（测试替身）

```python
MockContext(
    config: Optional[Config] = None,
    run: Any = None,
    sudo: Any = None,
    repeat: bool = True,
    **kwargs,
)
```

`MockContext` 是 Context 的子类，用于在单元测试中替代真实 Context，预先设定 `run` 和 `sudo` 的返回值，避免实际执行 Shell 命令。

### 核心特性

- `run` 和 `sudo` 方法被 `unittest.mock.Mock` 包装，支持断言调用
- 未预设返回值的方法调用会抛出 `NotImplementedError`
- 支持多种返回值格式
- 默认 `repeat=True`（v2.0+），返回值会循环使用

### 返回值格式

`run` 和 `sudo` 参数接受以下格式：

| 格式 | 说明 |
|------|------|
| 单个 `Result` 对象 | 每次调用返回该 Result |
| `bool` | `True` 返回 `Result(exited=0)`，`False` 返回 `Result(exited=1)` |
| `str` | 返回 `Result(stdout=<str>)` |
| 上述类型的可迭代对象 | 按顺序依次返回，耗尽后抛 `NotImplementedError`（除非 repeat=True） |
| `Dict` | 键为命令字符串或编译后的正则，值为上述格式；精确匹配优先于正则匹配 |

### 使用示例

```python
from invoke import MockContext, Result
import pytest

@task
def check_git(c):
    result = c.run("git status --porcelain", hide=True)
    if result.stdout.strip():
        return "dirty"
    return "clean"

def test_check_git_clean():
    # 预设 run 返回空输出（干净状态）
    c = MockContext(run=Result(""))
    assert check_git(c) == "clean"

def test_check_git_dirty():
    # 预设 run 返回非空输出（有未提交更改）
    c = MockContext(run=Result(" M src/app.py\n"))
    assert check_git(c) == "dirty"

def test_multiple_calls():
    # 按顺序返回不同结果
    c = MockContext(run=[Result(""), Result(" M file.py")])
    assert check_git(c) == "clean"
    assert check_git(c) == "dirty"

def test_dict_mapping():
    # 按命令映射结果
    c = MockContext(run={
        "git status --porcelain": Result(" M file.py"),
        "git rev-parse --short HEAD": Result("abc1234\n"),
    })
    assert c.run("git status --porcelain").stdout == " M file.py"
    assert c.run("git rev-parse --short HEAD").stdout == "abc1234\n"

def test_regex_matching():
    import re
    c = MockContext(run={
        re.compile(r"git (status|rev-parse)"): Result("matched\n"),
    })
    assert c.run("git status").stdout == "matched\n"
    assert c.run("git rev-parse HEAD").stdout == "matched\n"

# 使用 Mock 包装进行断言
def test_run_called():
    c = MockContext(run=Result("output"))
    c.run("mycommand")
    c.run.assert_called_once_with("mycommand")
```

### set_result_for 方法

```python
set_result_for(attname: str, command: str, result: Result) -> None
```

在创建后动态修改预设返回值。`attname` 为 `'run'` 或 `'sudo'`：

```python
c = MockContext(run={"cmd1": Result("out1")})
c.set_result_for("run", "cmd2", Result("out2"))
assert c.run("cmd1").stdout == "out1"
assert c.run("cmd2").stdout == "out2"
```

---

## 完整使用示例

```python
from invoke import task, call

@task
def clean(c):
    """Clean build artifacts."""
    c.run("rm -rf build/ dist/ *.egg-info", warn=True)
    print("Cleaned up.")

@task(pre=[clean])
def build(c, target="debug"):
    """Build the project."""
    # 根据参数设置环境变量前缀
    build_env = "production" if target == "release" else "development"
    
    with c.prefix(f"export BUILD_ENV={build_env}"):
        with c.cd("src"):
            c.run("make", echo=True)
            result = c.run("make test", warn=True, hide=True)
            if result.failed:
                print(f"Tests failed! (exit code {result.exited})")
                print(result.stderr)
            else:
                print("Build succeeded.")

@task
def deploy(c, env="staging"):
    """Deploy to environment."""
    config = c.config.deploy
    host = config[env].host
    user = config[env].user
    
    # 构建并部署
    build(c)
    
    with c.prefix(f"export DEPLOY_ENV={env}"):
        c.sudo(f"systemctl stop myapp-{env}")
        c.run(f"rsync -avz dist/ {user}@{host}:/opt/myapp/")
        c.sudo(f"systemctl start myapp-{env}")
    
    print(f"Deployed to {env} at {host}")
```
