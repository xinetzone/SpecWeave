---
type: wiki
title: Runner 命令执行
description: PyInvoke Runner 抽象类与 Local 本地执行器的完整 API 参考，涵盖 Result/Promise 对象、PTY 模式、I/O 线程模型与异常类型。
tags: [pyinvoke, runner, result, promise, local, pty, io-threads, core-api]
date: 2026-08-21
status: stable
author: SpecWeave
sources:
  - external/libs/pyinvoke/invoke/invoke/runners.py
---

# Runner 命令执行

## 概述

`Runner` 是 Invoke 中执行 Shell 命令的抽象基类，定义了命令启动、等待、I/O 处理、超时控制等核心逻辑。`Local` 是其内置的本地执行实现，使用 `subprocess.Popen` 和可选的 PTY（伪终端）执行命令。通常不直接使用 Runner，而是通过 `Context.run()` 间接调用。

相关文档：[Context](context.md)、[Config](config.md)、[Watcher](watchers.md)

---

## Runner 抽象基类

### 类常量

| 常量 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `read_chunk_size` | `int` | `1000` | 每次流读取的最大字节数 |
| `input_sleep` | `float` | `0.01` | stdin 读取循环的休眠秒数 |

### 构造函数

```python
Runner(context: Context)
```

- `context`：关联的 Context 实例，提供配置默认值（如 `run.echo`、`run.warn` 等）

### 核心实例属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `context` | `Context` | 关联的 Context 对象 |
| `program_finished` | `threading.Event` | 程序完成信号，IO 线程据此退出循环 |
| `using_pty` | `bool` | 是否使用 PTY 模式 |
| `opts` | `Dict[str, Any]` | 合并配置后的运行选项 |
| `streams` | `Dict[str, Any]` | 流映射：`out`、`err`、`in` |
| `watchers` | `List[StreamWatcher]` | 流监控器列表 |
| `env` | `Dict[str, str]` | 子进程环境变量 |
| `encoding` | `str` | 输出编码 |
| `threads` | `Dict[Callable, ExceptionHandlingThread]` | IO 工作线程字典 |
| `stdout` / `stderr` | `List[str]` | 输出缓冲区列表 |

---

## run 方法（核心执行逻辑）

```python
run(command: str, **kwargs) -> Result
```

执行命令并返回 `Result` 对象（同步）或 `Promise`（异步）。

### 执行流程

```
run(command, **kwargs)
  → _run_body(command, **kwargs)
    → _setup()                    # 合并配置与 kwargs，准备环境
    → 若 dry=True，返回空 Result
    → start(command, shell, env)  # 启动子进程
    → 若 disown=True，返回轻量 Result
    → start_timer(timeout)        # 启动超时计时器
    → create_io_threads()         # 创建 IO 线程
    → 启动所有 IO 线程
    → 若 asynchronous → 返回 Promise
    → 否则 → _finish()            # 等待并收集结果
```

### 完整参数列表

| 参数 | 类型 | 默认值（config 键） | 说明 |
|------|------|---------------------|------|
| `command` | `str` | — | 要执行的 Shell 命令（必填） |
| `asynchronous` | `bool` | `run.asynchronous` (False) | 异步执行，返回 Promise |
| `disown` | `bool` | `run.disown` (False) | 完全脱离进程，后台运行 |
| `dry` | `bool` | `run.dry` (False) | 空跑模式，不实际执行（仅回显命令） |
| `echo` | `bool` | `run.echo` (False) | 执行前打印命令 |
| `echo_format` | `str` | `run.echo_format` | 回显格式字符串，支持 `{command}` 占位符 |
| `echo_stdin` | `bool`/`None` | `run.echo_stdin` (None) | 是否回显 stdin；None 为自动检测 TTY |
| `encoding` | `str` | `run.encoding` (None) | 输出编码，None 使用 locale 默认 |
| `encoding_errors` | `str` | `run.encoding_errors` | 编码错误处理策略 |
| `env` | `Dict[str, str]` | `run.env` ({}) | 子进程环境变量（合并模式） |
| `replace_env` | `bool` | `run.replace_env` (False) | True 则用 env 替换整个环境 |
| `fallback` | `bool` | `run.fallback` (True) | PTY 失败时是否回退到非 PTY |
| `hide` | `bool`/`str`/`None` | `run.hide` (None) | 隐藏输出：True/“both”隐藏全部，“out”/“stdout”、“err”/“stderr” |
| `in_stream` | 文件对象/`False` | `run.in_stream` (None→sys.stdin) | stdin 源；False 禁用 stdin |
| `out_stream` | 文件对象 | `run.out_stream` (None→sys.stdout) | stdout 实时输出目标 |
| `err_stream` | 文件对象 | `run.err_stream` (None→sys.stderr) | stderr 实时输出目标 |
| `pty` | `bool` | `run.pty` (False) | 使用伪终端执行 |
| `shell` | `str` | `run.shell` | Shell 二进制路径（Unix 默认 `/bin/bash`，Windows 默认 `cmd.exe`） |
| `timeout` | `float`/`None` | `timeouts.command` (None) | 超时秒数，超时抛出 `CommandTimedOut` |
| `warn` | `bool` | `run.warn` (False) | 非零退出码时只警告不抛异常 |
| `watchers` | `List[StreamWatcher]` | `run.watchers` ([]) | 流监控器列表 |

### 互斥约束

- `asynchronous=True` 和 `disown=True` 不能同时使用，会抛出 `ValueError`
- `asynchronous=True` 会强制设置 `hide=True` 和 `in_stream=False`
- `disown=True` 不启动 IO 线程，不检查退出码
- `dry=True` 强制 `echo=True`
- `hide=True` 覆盖 `echo=True`

### 异常

| 异常类 | 触发条件 |
|--------|----------|
| `TypeError` | 传入了未知的关键字参数 |
| `UnexpectedExit` | 命令非零退出且 `warn=False` |
| `CommandTimedOut` | 命令执行超过 `timeout` 秒 |
| `Failure` | StreamWatcher 检测到错误（如密码认证失败） |
| `ThreadException` | IO 工作线程内部异常 |
| `SubprocessPipeError` | 子进程管道操作失败 |

---

## Result 对象

`Result` 封装了命令执行的完整结果。

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `stdout` | `str` | 标准输出文本（PTY 模式下 stderr 合并到此） |
| `stderr` | `str` | 标准错误文本（PTY 模式下为空字符串） |
| `command` | `str` | 执行的命令字符串 |
| `shell` | `str` | 使用的 Shell 路径 |
| `env` | `Dict[str, str]` | 子进程环境变量 |
| `exited` | `int`/`None` | 退出码；0 表示成功；None 表示未正常完成（watcher 错误/超时） |
| `return_code` | `int`/`None` | `exited` 的别名（property） |
| `pty` | `bool` | 是否在 PTY 模式下执行 |
| `hide` | `Tuple[str, ...]` | 被隐藏的流名元组（如 `('stdout',)`、`('stdout','stderr')`、`()`） |
| `encoding` | `str` | 使用的编码 |
| `pid` | `int`/`None` | 子进程 ID（v3.0+） |
| `disowned` | `bool` | 是否以脱离模式运行（v3.0+） |

### 便捷属性

| 属性 | 返回 | 说明 |
|------|------|------|
| `ok` | `bool` | `exited == 0`，命令是否成功 |
| `failed` | `bool` | `not ok`，命令是否失败 |

### 布尔求值

`Result` 的布尔值等于 `ok` 属性，因此可以简洁地判断：

```python
if c.run("some command", warn=True):
    print("Success!")
else:
    print("Failed!")
```

### 方法

#### tail(stream: str, count: int = 10) -> str

返回指定流的最后 `count` 行，格式化为带缩进的字符串，方便错误展示：

```python
result = c.run("failing-command", warn=True, hide=True)
if result.failed:
    print(f"Command failed! Last stderr lines:{result.tail('stderr')}")
```

### 字符串表示

- `__str__` 格式化输出退出状态、stdout 和 stderr
- `__repr__` 返回 `<Result cmd='command' exited=0>` 格式

---

## Promise 对象（异步执行）

`Promise` 继承自 `Result` 和 `AbstractContextManager`，表示异步执行的未来结果。

### 核心方法

#### join() -> Result

阻塞直到子进程退出，返回最终的 `Result` 或抛出异常。行为与同步 `run()` 的结果收集阶段完全一致。

```python
# 异步执行
promise = c.run("long-build-command", asynchronous=True)
# ...做其他工作...
result = promise.join()  # 等待完成
print(result.stdout)
```

#### 上下文管理器

Promise 支持 `with` 语句，退出时自动调用 `join()`：

```python
with c.run("background-task", asynchronous=True) as p:
    c.run("parallel-task")
# 退出 with 块时自动 join p
```

### 构造时复制的属性

Promise 从 Runner 复制以下 `result_kwargs` 属性（执行前已知）：
- `command`、`shell`、`env`、`pty`、`hide`、`encoding`
- 执行后才有的属性（stdout、stderr、exited 等）需要 `join()` 后才能访问

---

## Local 执行器

`Local` 是 `Runner` 的具体子类，实现了本地 Shell 命令执行。

### 核心实现机制

#### 非 PTY 模式（默认）

使用 `subprocess.Popen` 创建子进程，stdout/stderr/stdin 均通过管道连接：

```python
self.process = Popen(
    command,
    shell=True,
    executable=shell,
    env=env,
    stdout=PIPE,
    stderr=PIPE,
    stdin=PIPE,
)
```

- stdout 和 stderr 各自有独立的 IO 线程读取
- stdin 线程负责将用户输入转发到子进程
- 可以区分 stdout 和 stderr 输出

#### PTY 模式（pty=True）

使用 `pty.fork()` 创建伪终端：

1. 通过 `pty.fork()` 创建子进程
2. 子进程中使用 `os.execvpe(shell, [shell, "-c", command], env)` 执行命令
3. 父进程通过 PTY 文件描述符与子进程通信
4. 设置终端窗口大小（通过 `fcntl.ioctl` + `termios.TIOCSWINSZ`）

PTY 模式特点：
- stdout 和 stderr 合并为单一输出流（stderr 属性始终为空）
- 许多程序（如 sudo、docker -it）需要 PTY 才能正常交互
- 不支持关闭 stdin（`close_proc_stdin()` 抛出 `SubprocessPipeError`）
- 依赖 `pty`、`fcntl`、`termios` 模块（Windows 上不可用）
- 退出码通过 `os.waitpid` + `os.WIFEXITED/WIFSIGNALED/WEXITSTATUS/WTERMSIG` 获取
- 信号终止的退出码为负数（与 subprocess 行为一致）

#### 启动方法

```python
start(command: str, shell: str, env: Dict[str, Any]) -> None
```

- PTY 模式：调用 `pty.fork()`，子进程 `os.execvpe()`，设置 winsize
- 非 PTY 模式：调用 `Popen()`

#### 进程管理方法

| 方法 | 说明 |
|------|------|
| `get_pid() -> int` | 返回子进程 PID |
| `wait() -> None` | 等待子进程完成（PTY 模式轮询，非 PTY 调用 `process.wait()`） |
| `returncode() -> Optional[int]` | 返回退出码；PTY 模式通过 waitpid 获取，信号终止返回负数 |
| `kill() -> None` | 发送 SIGKILL 终止进程（忽略 ProcessLookupError） |
| `process_is_finished -> bool` | 检查进程是否已结束（PTY 用 WNOHANG waitpid，非 PTY 用 poll()） |
| `send_interrupt(exception) -> None` | 向子进程发送中断信号 |
| `stop() -> None` | 清理资源（关闭 PTY fd 等） |

---

## I/O 线程模型

Runner 使用多线程处理子进程的 I/O，避免管道阻塞：

### 线程结构

```
create_io_threads()
  ├── handle_stdout 线程    # 始终存在：读取 stdout → 缓冲区 + out_stream + watchers
  ├── handle_stderr 线程    # 非 PTY 模式存在：读取 stderr → 缓冲区 + err_stream + watchers
  └── handle_stdin 线程     # in_stream 非 False 时存在：从 in_stream 读取 → 写入子进程 stdin
```

每个线程都是 `ExceptionHandlingThread`，能捕获并存储内部异常。

### stdout/stderr 处理线程

`handle_stdout`/`handle_stderr` 的核心循环：
1. 通过 `ready_for_reading()` 检查文件描述符是否可读
2. 使用 `read_proc_output()` 读取数据块（最多 `read_chunk_size` 字节）
3. 解码为字符串，追加到对应缓冲区列表
4. 如果未隐藏，写入对应的输出流
5. 调用 `respond(buffer_)` 让 StreamWatcher 处理累积数据
6. 重复直到 `program_finished` 被设置

### stdin 处理线程

`handle_stdin` 的核心循环：
1. 使用 `character_buffered()` 设置输入流为字符缓冲模式
2. 循环读取 `bytes_to_read()` 指定的字节数
3. 通过 `_write_proc_stdin()` 写入子进程 stdin
4. 如果 `echo_stdin=True`，同时回显到输出流
5. 退出时调用 `close_proc_stdin()` 关闭子进程 stdin

### respond 方法

```python
respond(buffer_: List[str], stream_type: str) -> None
```

将累积的缓冲区内容提交给所有 `StreamWatcher`，如果 watcher 返回响应字符串，则写入子进程 stdin。PTY 模式下只对 stdout buffer 调用（因为 stderr 合并到 stdout）。

### 线程异常处理

`_finish()` 方法在等待子进程结束后：
1. 设置 `program_finished` 信号
2. 依次 join 所有线程
3. 如果对端线程已死亡，给当前线程 1 秒超时（防止管道满导致死锁）
4. 收集线程异常，区分为 `WatcherError`（预期错误）和其他异常（非预期错误）

---

## 超时机制

```python
start_timer(timeout: Optional[float]) -> None
```

如果指定了 `timeout`，创建一个 `threading.Timer`，到期时：
1. 调用 `kill()` 发送 SIGKILL 终止子进程
2. 设置 `self.timed_out = True`

在 `_finish()` 中检测到超时后抛出 `CommandTimedOut` 异常。

---

## normalize_hide 函数

```python
normalize_hide(
    val: Any,
    out_stream: Optional[str] = None,
    err_stream: Optional[str] = None,
) -> Tuple[str, ...]
```

将 `hide` 参数规范化为流名元组：

| 输入 | 输出 |
|------|------|
| `None` / `False` | `()` |
| `True` / `"both"` | `("stdout", "stderr")` |
| `"out"` / `"stdout"` | `("stdout",)` |
| `"err"` / `"stderr"` | `("stderr",)` |

如果指定了自定义 `out_stream`/`err_stream`，对应流从 hide 元组中移除（因为用户显式指定了输出目标）。

---

## default_encoding 函数

```python
default_encoding() -> str
```

使用 `locale.getpreferredencoding(False)` 获取系统默认编码，作为输出编码的兜底值。

---

## generate_env 方法

```python
generate_env(env: Dict[str, str], replace_env: bool) -> Dict[str, str]
```

构建子进程环境：
- `replace_env=False`（默认）：基于 `os.environ.copy()` 合并 `env`
- `replace_env=True`：直接使用 `env` 作为完整环境

---

## 异常类型层级

```
Exception
├── ThreadException           # IO 线程异常集合
├── WatcherError              # StreamWatcher 错误
│   └── ResponseNotAccepted   # 自动响应失败（如密码错误）
│       └── AuthFailure       # sudo 认证失败
├── Failure                  # 命令执行失败（包含 Result 和原因）
│   └── UnexpectedExit       # 命令非零退出
│       └── CommandTimedOut  # 命令超时
└── SubprocessPipeError      # 管道操作错误
```

---

## 使用示例

```python
from invoke import Context, Local
from invoke.runners import Result, Promise
from invoke.exceptions import UnexpectedExit, CommandTimedOut

# 基本使用
c = Context()

# 同步执行，捕获输出
result = c.run("echo hello", hide=True)
assert result.ok
assert result.stdout.strip() == "hello"

# 失败处理
try:
    c.run("exit 1")
except UnexpectedExit as e:
    print(f"Exit code: {e.result.exited}")

# 超时控制
try:
    c.run("sleep 10", timeout=2)
except CommandTimedOut as e:
    print(f"Timed out after {e.timeout}s")

# 异步执行
import time
p = c.run("sleep 2 && echo done", asynchronous=True)
print("Doing other work...")
time.sleep(1)
result = p.join()
print(result.stdout.strip())  # "done"

# 异步 + 上下文管理器
with c.run("sleep 2", asynchronous=True) as p:
    print("While waiting...")
# 自动 join

# PTY 模式（适合交互式命令）
c.run("sudo apt-get install -y nginx", pty=True, watchers=[...])

# 脱离模式（后台运行）
c.run("nohup python server.py &", disown=True)

# 干跑模式
c.run("rm -rf /", dry=True)  # 只打印命令，不执行

# 自定义输出流
import sys
c.run("ls", out_stream=sys.stderr)  # 输出到 stderr
```
