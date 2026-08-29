---
id: "python314-cpython-wiki-05"
title: "Python 3.14 标准库重大改进"
source: "https://docs.python.org/zh-cn/3.14/whatsnew/3.14.html#improved-modules"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/10-foundational-knowledge/python314-cpython-wiki/05-stdlib-improvements.toml"
---
# Python 3.14 标准库重大改进

除了新增模块外，Python 3.14 对许多已有标准库模块进行了重要改进。本章精选对开发者影响最大的改进，按模块分类介绍。

---

## 1. REPL 增强：语法高亮与自动补全

### 新 REPL 成为默认

Python 3.13 引入了基于 `_pyrepl` 的新 REPL，但默认使用旧版。Python 3.14 将**新 REPL 设为默认**，提供：

- **语法高亮**：关键字、字符串、数字、注释等使用不同颜色
- **自动补全**：按 Tab 键补全变量名、属性、模块名
- **多行编辑**：更好的多行代码编辑体验
- **历史搜索**：Ctrl+R 反向搜索历史命令
- **括号匹配**：自动匹配括号/引号

```python
# 启动 Python 3.14 REPL
$ python3.14
Python 3.14.0 (main, Oct  7 2025, ...) [GCC ...] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>> # 试试：输入 imp[TAB] 会自动补全
>>> # 彩色输出：关键字如 def/for/if 会有不同颜色
```

### 回退到旧 REPL

如果需要使用传统 REPL（例如在不支持 ANSI 颜色的终端中）：

```bash
# 方式1：环境变量
PYTHON_BASIC_REPL=1 python3.14

# 方式2：启动参数
python3.14 -P  # 或检查是否有 --basic-repl 参数
```

### REPL 代码示例

```python
# 在新 REPL 中体验补全和高亮
>>> import math
>>> math.sq[TAB]    # Tab 补全：sqrt
>>> math.sqrt(16)
4.0
>>> # 历史命令：按上/下箭头浏览
```

---

## 2. asyncio 增强

Python 3.14 对 asyncio 进行了多项重要改进，包括命令行内省、任务调用图捕获、`create_task` 关键字参数、自由线程一等支持，以及底层任务管理性能优化。

### 内省 CLI 工具：ps / pstree

Python 3.14 的 asyncio 提供了命令行内省工具，可以附加到运行中的 Python 进程，查看 asyncio 任务状态：

```bash
# 平面列表：显示所有任务、名称、协程栈、awaiter 链
python -m asyncio ps <pid>

# 树形展示：显示协程调用层级关系（调试阻塞/死锁首选）
python -m asyncio pstree <pid>
```

`ps` 输出示例（任务表格式）：

```
tid      task id          task name   coroutine stack                              awaiter chain                               awaiter name  awaiter id
-----------------------------------------------------------------------------------------------------------------------------------------------------
1935500  0x7fc930c18050   Task-1      TaskGroup._aexit -> main                                                              0x0
1935500  0x7fc930c18230   Sundowning  TaskGroup._aexit -> album   TaskGroup._aexit -> main  Task-1         0x7fc930c18050
1935500  0x7fc93173fdf0   TNDNBTG     sleep -> play             TaskGroup._aexit -> album Sundowning     0x7fc930c18230
```

`pstree` 输出示例（树形格式）：

```
└── (T) Task-1
    └──  main example.py:13
        └──  TaskGroup.__aexit__ Lib/asyncio/taskgroups.py:72
            ├── (T) Sundowning
            │   └──  album example.py:8
            │       └──  TaskGroup._aexit Lib/asyncio/taskgroups.py:121
            │           ├── (T) TNDNBTG
            │           │   └──  play example.py:4
            │           │       └──  sleep Lib/asyncio/tasks.py:702
            │           └── (T) Levitate
            │               └──  play example.py:4
            └── (T) TMBTE
                └──  album example.py:8
```

**循环检测**：如果 await 图中存在循环（通常表示编程错误），`pstree` 会报错并列出循环路径：

```
$ python -m asyncio pstree 12345
ERROR: await-graph contains cycles - cannot print a tree!
cycle: Task-2 → Task-3 → Task-2
```

这个功能对于调试"卡住"的异步程序特别有用——可以快速定位哪个协程阻塞了、哪些任务在等待什么。

### 编程式调用图捕获

除了 CLI 工具，Python 3.14 还新增了两个函数用于在代码中捕获任务调用图：

```python
import asyncio

async def worker():
    await asyncio.sleep(1)

async def main():
    # capture_call_graph() 返回调用图数据结构
    graph = asyncio.capture_call_graph()

    # print_call_graph() 直接打印调用树（类似 pstree CLI 输出）
    asyncio.print_call_graph()

    async with asyncio.TaskGroup() as tg:
        tg.create_task(worker(), name="worker-1")
        tg.create_task(worker(), name="worker-2")

# 典型调试用法：在异常处理中打印调用图
try:
    asyncio.run(main())
except Exception:
    asyncio.print_call_graph()  # 打印崩溃时的任务状态
    raise
```

### `create_task` 支持任意关键字参数

`asyncio.create_task()` 和 `TaskGroup.create_task()` 现在接受任意关键字参数，这些参数会传递给 `Task` 构造器（或自定义的 task factory）：

```python
import asyncio

async def my_coro():
    await asyncio.sleep(0.1)
    return "done"

async def main():
    # 3.14 之前：只能传 name、context 等有限参数
    # 3.14：任意 kwargs 会传递给 Task 构造器
    task = asyncio.create_task(
        my_coro(),
        name="my-task",
        # 以下是 3.14 新增的能力——kwarg 透传到 task factory
        eager_start=True,       # 如果 loop 支持 eager task start
        context=my_context,     # 自定义 contextvars 上下文
    )

    # TaskGroup.create_task 同样支持
    async with asyncio.TaskGroup() as tg:
        tg.create_task(my_coro(), name="tg-task", eager_start=True)
```

这使得自定义 Task 子类和 task factory 可以接收自定义配置参数，不再需要通过全局变量或闭包传递。

### 自由线程一等支持

asyncio 在自由线程（free-threaded，`python3.14t`）构建中获得了一等支持：

```bash
# 无 GIL 模式运行 asyncio 应用
PYTHON_GIL=0 python3.14t your_async_app.py
```

关键改进：
- **多事件循环并行**：多个线程可以各自运行独立的事件循环，不再有全局锁竞争
- **线程安全调度**：`loop.call_soon_threadsafe()` 在自由线程模式下经过重新设计，性能更好
- **任务双向链表**：原生 Task 对象改用双向链表实现，支持 O(1) 的跨线程任务遍历（为 `ps/pstree` 内省提供基础）
- **性能提升**：I/O 密集型 asyncio 应用在自由线程模式下可获得 10-20% 的吞吐量提升

### 底层优化：原生任务双向链表

asyncio 的原生 Task 对象内部从集合（set）改为双向链表（doubly-linked list）管理：

```python
# 这个底层变化带来两个直接好处：
# 1. 任务创建/销毁从 O(n) 变为 O(1)
# 2. 跨线程内省（ps/pstree）可以安全遍历任务列表而不需要暂停世界
```

对于大量短命任务的场景（如 HTTP 服务器每秒创建数千个 Task），这个优化可以显著减少 GC 压力和事件循环延迟。

---

## 2.5 concurrent.futures 增强

### InterpreterPoolExecutor：子解释器池

Python 3.14 新增 `InterpreterPoolExecutor`，利用多解释器（PEP 734）实现真正的并行执行（每个解释器有独立的 GIL）：

```python
from concurrent.futures import InterpreterPoolExecutor

# 使用子解释器池执行 CPU 密集任务——绕过 GIL 限制
# 与 ProcessPoolExecutor 不同，子解释器在同一进程内，启动更快
with InterpreterPoolExecutor(max_workers=4) as pool:
    results = list(pool.map(cpu_bound_function, data_list))
```

> **注意**：这与 `concurrent.interpreters` 模块（PEP 734 的底层 API）是不同层次的接口。`InterpreterPoolExecutor` 是高层的执行器，符合 `Executor` 接口规范。

### ProcessPoolExecutor 默认启动方式改为 forkserver

在 Linux 上（非 macOS），`ProcessPoolExecutor` 默认的多进程启动方式从 `fork` 改为 `forkserver`，更安全：

```python
from concurrent.futures import ProcessPoolExecutor

# Linux 默认现在使用 forkserver（更安全，避免 fork+thread 死锁）
# Windows/macOS 保持 spawn 不变
with ProcessPoolExecutor() as pool:
    results = list(pool.map(func, data))

# 如果确实需要 fork 方式，显式指定：
import multiprocessing
ctx = multiprocessing.get_context("fork")
with ProcessPoolExecutor(mp_context=ctx) as pool:
    results = list(pool.map(func, data))
```

### ProcessPoolExecutor 新增 `terminate_workers()` / `kill_workers()`

```python
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as pool:
    future = pool.submit(slow_task)
    # ... 需要快速关闭时 ...

    # 优雅终止所有 worker（发送 SIGTERM）
    pool.terminate_workers()

    # 强制杀死所有 worker（发送 SIGKILL，用于无响应场景）
    pool.kill_workers()
```

### Executor.map 新增 `buffersize` 参数

```python
from concurrent.futures import ThreadPoolExecutor

# buffersize 限制已提交但未产出结果的任务数量
# 防止一次性提交过多任务导致内存爆炸
with ThreadPoolExecutor(max_workers=4) as pool:
    for result in pool.map(process_item, huge_dataset, buffersize=100):
        handle(result)  # 缓冲区满时暂停提交，避免内存溢出
```

---

## 3. pathlib 增强

### 递归 copy 和 move

```python
from pathlib import Path

# 递归复制目录（类似 shutil.copytree）
src = Path("/path/to/source_dir")
dest = Path("/path/to/dest_dir")
src.copy(dest)           # 复制文件或目录
src.copy(dest, recursive=True)  # 递归复制目录

# 移动/重命名
src.move(dest)
```

### `Path.info` 缓存元数据

```python
p = Path("some_file.txt")

# stat() 结果被缓存
info = p.info
print(info.size)     # 文件大小
print(info.mtime)    # 修改时间
print(info.is_file)  # 是否为文件

# 刷新缓存
p.info.refresh()
```

### 无缓冲读取加速

```python
# 更高效的小文件读取
content = Path("config.json").read_text(encoding="utf-8")
# 内部优化减少了系统调用次数
```

### 代码示例

```python
from pathlib import Path

# 递归复制并处理冲突
def backup_directory(src: Path, dest: Path):
    """备份目录，跳过已存在且相同的文件"""
    src.copy(dest, recursive=True, dirs_exist_ok=True)
    print(f"Backup complete: {src} -> {dest}")

# 使用 Path.info 快速过滤大文件
large_files = [
    p for p in Path(".").rglob("*.log")
    if p.info.size > 100 * 1024 * 1024  # > 100MB
]
```

---

## 4. uuid：v6/v7/v8 支持（RFC 9562）

### 新 UUID 版本

Python 3.14 新增对 UUID v6、v7、v8 的支持，这些版本是 RFC 9562 定义的新一代时间排序 UUID：

| 版本 | 特点 | 适用场景 |
|------|------|---------|
| v1 | 基于时间+MAC地址 | 传统应用（已有） |
| v4 | 完全随机 | 通用唯一标识（已有） |
| **v6** | 时间排序（v1 的改进版） | 数据库主键（按时间排序） |
| **v7** | 基于 Unix 时间戳的时间排序 | 现代数据库主键、日志追踪 |
| **v8** | 实验性/自定义格式 | 特殊用途 |

```python
import uuid

# UUID v7：基于 Unix 毫秒时间戳，按时间排序
id7 = uuid.uuid7()
print(id7)        # e.g. 0193f3a3-7c80-7b1c-9d0a-4e8b0c1d2e3f
print(id7.time)   # 嵌入的时间戳

# UUID v6：v1 的字段重排版本，按时间排序
id6 = uuid.uuid6()
print(id6)

# NIL 和 MAX 常量
print(uuid.NIL)   # 00000000-0000-0000-0000-000000000000
print(uuid.MAX)   # ffffffff-ffff-ffff-ffff-ffffffffffff
```

### UUID v7 的优势

UUID v7 相比 UUID v4 的优势：
1. **数据库索引友好**：按时间生成，索引插入不随机，B-tree 性能更好
2. **可排序**：UUID 本身包含时间信息，可以直接排序
3. **仍保持唯一性**：随机部分保证同一毫秒内的唯一性

```python
import uuid
import time

# UUID v7 按时间排序
ids = [uuid.uuid7() for _ in range(5)]
time.sleep(0.001)
ids.append(uuid.uuid7())

# 按生成顺序排序（字符串排序即可，因为时间在前）
for id in sorted(ids):
    print(id)
# 输出按生成顺序排列，因为前几位是时间戳
```

---

## 5. pdb：远程调试与增强

### 远程附加调试（PEP 768）

Python 3.14 的 pdb 支持附加到正在运行的 Python 进程进行远程调试：

```bash
# 附加到运行中的 Python 进程
python -m pdb -p <PID>
```

```python
# 在代码中设置断点等待远程附加
import pdb
pdb.set_trace()  # 程序暂停，等待调试器连接

# 或使用 PEP 768 的远程调试接口
import sys
sys.audit("pdb.attach", ...)
```

### Inline 模式

```python
# 在代码中插入内联断点
x = 42
breakpoint()  # Python 3.14 中可以在更上下文中工作
y = x + 1
```

### 语法高亮和 async 支持

pdb 的交互界面现在支持语法高亮，并且可以正确调试 async 函数：

```python
import pdb

async def fetch_data():
    result = await api_call()
    pdb.set_trace()  # 现在在 async 函数中可以正常工作
    return result
```

---

## 6. argparse 增强

### 彩色输出

```python
import argparse

parser = argparse.ArgumentParser(description="My tool")
parser.add_argument("--name", help="Your name")
parser.add_argument("--verbose", action="store_true", help="Verbose output")
args = parser.parse_args()
# 帮助信息和错误信息现在支持彩色输出（终端支持时）
```

### 错误建议（suggest_on_error）

```python
parser = argparse.ArgumentParser(suggest_on_error=True)
parser.add_argument("--verbose", action="store_true")
parser.add_argument("--config", type=str)

# 如果用户输入了错误参数：
# $ myapp --verbos
# error: unrecognized arguments: --verbos
# 提示：did you mean --verbose?
```

### 程序名自动反映

argparse 现在自动从 `sys.argv[0]` 获取程序名，无需手动设置 `prog`。

---

## 7. inspect 增强

`inspect` 模块在 3.14 中配合 PEP 649/749 增加了注解格式控制能力（详见[第 1 章 §3.5](01-language-features.md#35-类型系统重要变更)），此处补充其他增强：

```python
import inspect

# Signature.format() 新增 unquote_annotations 参数
def foo(x: 'int', y: 'str') -> 'bool': ...
sig = inspect.signature(foo)

# 默认：字符串注解带引号
print(sig.format())  # "(x: 'int', y: 'str') -> 'bool'"

# unquote_annotations=True：去掉引号更易读
print(sig.format(unquote_annotations=True))  # "(x: int, y: str) -> bool"

# ispackage() 检查模块是否为命名空间包
import os, json, concurrent
print(inspect.ispackage(os))         # False
print(inspect.ispackage(json))       # False
print(inspect.ispackage(concurrent)) # True
```

---

## 8. 其他精选改进

### json 命令行与彩色输出

```bash
# 命令行格式化 JSON（彩色输出）—— python -m json 是首选方式
python -m json mydata.json

# python -m json.tool 已软弃用，推荐使用上面的方式
echo '{"name": "test", "value": 42}' | python -m json
```

```python
import json

# 序列化错误现在附带异常注释（exception notes），可追溯错误路径
data = {"name": "test", "nested": {"bad_value": object()}}
try:
    json.dumps(data)
except TypeError as e:
    print(e.__notes__)  # 包含 'Circular reference' 或字段路径信息
```

### unittest 新断言方法

```python
import unittest

class MyTests(unittest.TestCase):
    def test_new_assertions(self):
        obj = MyClass()
        # 属性存在/不存在检查
        self.assertHasAttr(obj, "expected_attr")
        self.assertNotHasAttr(obj, "deprecated_attr")

        # issubclass 检查
        self.assertIsSubclass(MyClass, BaseClass)
        self.assertNotIsSubclass(MyClass, UnrelatedClass)

        # 字符串前缀/后缀
        self.assertStartsWith("hello world", "hello")
        self.assertNotStartsWith("hello world", "goodbye")
        self.assertEndsWith("hello world", "world")
        self.assertNotEndsWith("hello world", "moon")
```

### `logging.handlers.QueueListener` 上下文管理器

```python
import logging
import logging.handlers
import queue

# QueueListener 现在支持上下文管理器协议
log_queue = queue.Queue(-1)
handler = logging.StreamHandler()

with logging.handlers.QueueListener(log_queue, handler) as listener:
    # 退出 with 块时自动 stop()
    # 重复 start() 现在会抛出 RuntimeError（防止错误使用）
    logger = logging.getLogger()
    logger.addHandler(logging.handlers.QueueHandler(log_queue))
    logger.info("safe logging")
```

### pickle 协议 5 默认

```python
import pickle

# Python 3.14 默认使用 pickle 协议 5
# 协议 5 支持带外缓冲区（out-of-band buffers），适合大数组
data = {"key": "value"}
pickled = pickle.dumps(data)  # 默认 protocol=5
```

### unittest 彩色输出

```bash
# unittest 输出现在默认彩色
python -m unittest test_module.py
# PASSED 绿色，FAILED 红色，SKIPPED 黄色
```

```python
import unittest

class MyTests(unittest.TestCase):
    def test_new_assertions(self):
        # 新断言方法
        self.assertIsNone(None)
        self.assertIsNotNone(42)
```

### heapq 原生大顶堆支持

```python
import heapq

# 传统小顶堆（原有功能）
min_heap = []
heapq.heappush(min_heap, 3)
heapq.heappush(min_heap, 1)
heapq.heappush(min_heap, 4)
print(heapq.heappop(min_heap))  # 1（最小）

# Python 3.14 新增：原生大顶堆函数
max_heap = [3, 1, 4, 1, 5, 9]
heapq.heapify_max(max_heap)      # 原地建大顶堆
print(heapq.heappop_max(max_heap))  # 9（最大）
print(heapq.heappop_max(max_heap))  # 5

# 其他大顶堆操作
heapq.heappush_max(max_heap, 7)     # 推入大顶堆
heapq.heapreplace_max(max_heap, 8)  # 弹出最大并推入新值
heapq.heappushpop_max(max_heap, 6)  # 先推再弹（效率更高）
```

以前实现大顶堆需要手动对元素取负数，现在有了原生 API，代码更清晰且不易出错。

### operator 新函数

```python
import operator

# 新增 is_none 和 is_not_none
print(operator.is_none(None))       # True
print(operator.is_none(0))          # False
print(operator.is_not_none(""))     # True（因为 "" is not None）

# 使用场景：在 map/filter/sort 中替代 lambda
values = [1, None, 3, None, 5]
non_none = list(filter(operator.is_not_none, values))
# [1, 3, 5]
```

### struct 复数类型

```python
import struct

# 新增 F/D 格式符用于复数
# F = complex64（两个 float，共 8 字节）
# D = complex128（两个 double，共 16 字节）

data = struct.pack("F", 1.0 + 2.0j)
print(struct.unpack("F", data))  # (1+2j,)

data = struct.pack("D", 3.14 + 2.718j)
print(struct.unpack("D", data))  # (3.14+2.718j,)
```

### unicodedata 16.0.0

`unicodedata` 模块已更新到 Unicode 16.0.0，新增了新字符和属性。

### http.server 深色模式与 HTTPS

```bash
# 简单 HTTP 服务器现在支持深色模式主题
python -m http.server

# HTTPS 支持（需要证书）
python -m http.server --certificate cert.pem
```

### imaplib IDLE 命令

```python
import imaplib

# IDLE 命令支持：实时接收新邮件通知
with imaplib.IMAP4_SSL("imap.example.com") as imap:
    imap.login("user@example.com", "password")
    imap.select("INBOX")

    # 使用 IDLE 等待新邮件
    imap.idle_start()
    # ... 等待服务器推送新邮件通知 ...
    responses = imap.idle_check(timeout=30)
    imap.idle_done()
```

### faulthandler C 栈追踪

```python
import faulthandler

# 现在可以打印 C 级别的栈追踪（帮助诊断 C 扩展崩溃）
faulthandler.enable()
faulthandler.dump_traceback(all_threads=True)
# 输出包括 C 栈帧信息
```

---

## 10. 本章速查表

| 模块 | 关键改进 | 最实用场景 |
|------|---------|-----------|
| **REPL** | 语法高亮+自动补全默认 | 日常交互开发 |
| **asyncio** | ps/pstree CLI、capture/print_call_graph、create_task kwargs、自由线程、双向链表 | 调试异步程序、无 GIL 并发 |
| **concurrent.futures** | InterpreterPoolExecutor、forkserver 默认、terminate/kill_workers、buffersize | CPU 并行、进程池管理 |
| **pathlib** | copy/move、info 缓存 | 文件操作现代化 |
| **uuid** | v6/v7/v8、NIL/MAX | 数据库主键、分布式 ID |
| **pdb** | 远程附加、async 支持 | 调试运行中进程 |
| **argparse** | 彩色输出、错误建议 | CLI 工具开发体验 |
| **inspect** | annotation_format、unquote_annotations、ispackage | 框架开发、反射 |
| **json** | CLI（python -m json）、异常注释 | 命令行数据查看、序列化调试 |
| **unittest** | 彩色输出、assertHasAttr/IsSubclass/StartsWith/EndsWith | 测试断言更完整 |
| **logging** | QueueListener 上下文管理器 | 日志配置安全 |
| **heapq** | heapify_max/heappop_max 等大顶堆函数 | Top-K、优先队列 |
| **operator** | is_none/is_not_none | 函数式编程 |
| **struct** | F/D 复数类型 | 科学计算数据交换 |
| **imaplib** | IDLE 支持 | 邮件客户端开发 |
| **faulthandler** | C 栈追踪 | C 扩展调试 |

下一章将深入 **CPython 源码架构**，带你理解 Python 解释器内部是如何组织的。

---

- [上一章：新模块详解](04-new-modules.md) ←
- [下一章：CPython 源码架构总览](06-cpython-architecture.md) →
