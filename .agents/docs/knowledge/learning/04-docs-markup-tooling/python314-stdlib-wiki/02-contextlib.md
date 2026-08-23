---
id: "python314-stdlib-wiki-02"
title: "Python 3.14 标准库 contextlib 全面详解"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/02-contextlib.toml"
---
# Python 3.14 标准库 contextlib 全面详解

> 一句话摘要：`contextlib` 是围绕 `with` 语句和"上下文管理器协议"的一整套工具库，用最少的样板代码完成资源的获取与释放、标准输出重定向、工作目录切换、异常抑制等常见任务。

## 一、模块定位与用途

在日常 Python 编程中，有一类非常常见且容易出错的模式：**先获取某个资源（打开文件、建立连接、加锁），用完后再释放它（关闭文件、断开连接、解锁）**。如果释放逻辑被遗忘，或者代码在获取之后、释放之前抛出了异常，资源就会泄漏。

Python 通过 `with` 语句和**上下文管理器协议**为这类模式提供了语法级别的支持：

```python
with open("data.txt") as f:
    content = f.read()
# 无论代码块是否抛出异常，文件都会被关闭
```

`with` 语句会自动、可靠地在代码块结束时执行"清理"动作，即使代码块内部抛出异常也不例外。

`contextlib` 模块就是围绕这套机制提供的一批通用工具。它解决的问题可以归纳为几类：

1. **少写样板代码**：借助 `@contextmanager` 装饰器，一个普通的生成器函数就能变成一个上下文管理器，无需手写 `__enter__` / `__exit__` 两个方法、也无需定义类。
2. **动态组合上下文管理器**：`ExitStack` 允许你在运行时按数据决定要打开多少个上下文管理器，例如打开用户指定的一组文件。
3. **临时改变全局状态**：`redirect_stdout` / `redirect_stderr` 临时改道输出流，`chdir` 临时切换工作目录。
4. **有意忽略特定异常**：`suppress` 让你在一小段代码里静默地忽略指定异常。
5. **优雅处理"可选的"上下文管理器**：`nullcontext` 充当"什么都不做"的占位上下文管理器。

该模块位于 CPython 标准库的 `Lib/contextlib.py` 源码文件中。更多背景信息可参见 Python 官方文档中的"上下文管理器类型"（`stdtypes` 中的 contextmanager 条目）以及数据模型中的"with 语句上下文管理器"。

## 二、核心术语表

| 术语 | 一句话平实解释 |
|---|---|
| 上下文管理器（Context Manager） | 定义了"进入前"和"退出后"两个动作的对象，配合 `with` 语句使用，负责资源的安全回收 |
| `with` 语句 | Python 的语法糖，自动在代码块前后调用上下文管理器的进入与退出动作 |
| 上下文管理协议 | 约定对象只要实现 `__enter__` 和 `__exit__` 两个方法，就能被 `with` 使用 |
| 异步上下文管理器 | 为 `async with` 服务的版本，对应实现 `__aenter__` 和 `__aexit__` 两个方法 |
| 生成器（Generator） | 用 `yield` 写成的、可以中途暂停并再次恢复执行的函数 |
| 异步生成器 | 用 `async def` 加 `yield` 写成的生成器，用于异步场景 |
| 装饰器（Decorator） | 接收一个函数并返回增强后函数的工具，可用来改造函数的行为 |
| 回调（Callback） | 预先登记、稍后由某个机制调用的一段可执行代码 |
| 单次使用（Single-use） | 指某个上下文管理器实例只能有效用于一次 `with`，第二次使用会出错 |
| 可重进入（Reentrant） | 同一个实例可以同时被嵌套在多个 `with` 语句中使用 |
| 可重用（Reusable） | 同一个实例可以先后多次用于不同的 `with` 语句，但不能嵌套在同一实例里 |

## 三、上下文管理器协议

一个对象要能被 `with` 使用，需要实现两个方法：

- **`__enter__(self)`**：在进入 `with` 代码块时被调用。它的返回值会绑定到 `with ... as x` 中的 `x`（如果没有 `as` 子句则丢弃返回值）。
- **`__exit__(self, exc_type, exc, tb)`**：在离开 `with` 代码块时被调用（无论正常离开还是抛出异常）。三个参数分别描述代码块中发生的异常：异常类型、异常实例、traceback；如果代码块正常结束，三者都是 `None`。

`__exit__` 的返回值决定了异常如何继续传播：

- 返回 `False` 或 `None`：表示"我没有处理异常"，异常继续向外传播。
- 返回真值（如 `True`）：表示"我已处理异常"，该异常被压制，程序从 `with` 语句之后继续执行。

下面是一个最小实现：

```python
class Managed:
    def __enter__(self):
        print("进入")
        return "资源"
    def __exit__(self, exc_type, exc, tb):
        print("退出")
        return False  # 不抑制异常

with Managed() as r:
    print("拿到了", r)
# 输出：
# 进入
# 拿到了 资源
# 退出
```

异步版本使用 `__aenter__` 和 `__aexit__` 两个异步方法，配合 `async with` 使用，方法签名与同步版对应。

## 四、完整 API 详解

下面逐个讲解 `contextlib` 提供的全部函数与类。

### 4.1 `AbstractContextManager` 与 `AbstractAsyncContextManager`

- `class contextlib.AbstractContextManager`
- `class contextlib.AbstractAsyncContextManager`

这是两个**抽象基类**，为你自己定义的上下文管理器提供一个标准骨架：

- `AbstractContextManager`：面向同步上下文管理器。它提供了 `__enter__` 的默认实现——直接返回 `self`；而 `__exit__` 是抽象方法，需要子类自己实现。
- `AbstractAsyncContextManager`：面向异步上下文管理器。它提供了 `__aenter__` 的默认实现——返回 `self`；`__aexit__` 是抽象方法。

继承它们可让类型检查器（如外部类型检查工具）明确识别出你的类是上下文管理器，也能省去手写 `__enter__` 的重复代码。

- `AbstractContextManager` 于 **3.6** 版本加入。
- `AbstractAsyncContextManager` 于 **3.7** 版本加入。

### 4.2 `@contextmanager` 装饰器

签名：`@contextlib.contextmanager`

这是一个**函数装饰器**：把它套在一个生成器函数上，就能得到一个上下文管理器工厂函数，无需手写类和 `__enter__` / `__exit__` 方法。

核心规则（务必理解）：

1. **被装饰的函数必须返回一个生成器迭代器**，即函数体中用 `yield` 产出值。
2. **生成器必须恰好 `yield` 一个值**。这个值会被绑定到 `with ... as` 后面的变量。
3. 执行到 `yield` 时，`with` 代码块开始运行；代码块结束后，生成器恢复执行，`yield` 之后的代码做清理动作。
4. **异常处理**：如果 `with` 代码块抛出未处理的异常，该异常会被"抛回"生成器的 `yield` 点。因此你可以在生成器里用 `try/except/finally` 捕获它或保证清理执行。
   - 如果你捕获异常只是为了记录日志等，**必须重新抛出该异常**（`raise`），否则会被视为"异常已处理"，程序将从 `with` 之后继续执行。
5. 该装饰器内部使用了 `ContextDecorator`，因此生成的上下文管理器**既可以用于 `with` 语句，也可以作装饰器使用**。当作为装饰器使用时，每次函数调用都会隐式地创建一个新的生成器实例。

典型写法：

```python
from contextlib import contextmanager

@contextmanager
def managed_resource(*args, **kwds):
    # 获取资源的代码，例如：
    resource = acquire_resource(*args, **kwds)
    try:
        yield resource
    finally:
        # 释放资源的代码，例如：
        release_resource(resource)
```

版本说明：该装饰器本身很早就存在；**3.2** 版本起引入 `ContextDecorator` 的使用，使其产出的上下文管理器能作为装饰器使用。

### 4.3 `@asynccontextmanager` 装饰器

签名：`@contextlib.asynccontextmanager`

与 `@contextmanager` 类似，但生成的是**异步上下文管理器**。它必须应用在一个**异步生成器函数**（`async def` + `yield`）上，配合 `async with` 使用。

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def get_connection():
    conn = await acquire_db_connection()
    try:
        yield conn
    finally:
        await release_db_connection(conn)

async def get_all_users():
    async with get_connection() as conn:
        return conn.query('SELECT ...')
```

由 `@asynccontextmanager` 定义的上下文管理器既能作为装饰器，也能用于 `async with` 语句：

```python
import time
from contextlib import asynccontextmanager

@asynccontextmanager
async def timeit():
    now = time.monotonic()
    try:
        yield
    finally:
        print(f'it took {time.monotonic() - now}s to run')

@timeit()
async def main():
    ...  # 异步代码
```

与同步版相同，作为装饰器使用时，每次函数调用都会隐式创建新的生成器实例。

版本说明：**3.7** 版本加入；**3.10** 版本起由它创建的异步上下文管理器可以作为装饰器使用。

### 4.4 `closing` 与 `aclosing`

- `contextlib.closing(thing)`

返回一个在语句块结束时调用 `thing.close()` 的上下文管理器。它本质上等价于：

```python
from contextlib import contextmanager

@contextmanager
def closing(thing):
    try:
        yield thing
    finally:
        thing.close()
```

用法：

```python
from contextlib import closing
from urllib.request import urlopen

with closing(urlopen('https://www.python.org')) as page:
    for line in page:
        print(line)
```

即使代码块发生错误，`page.close()` 也会在退出时被调用。

> **注意**：大多数管理资源的类型本身已支持上下文管理协议。因此 `closing()` 对**不支持上下文管理协议**的第三方类型最有用。上面的 `urlopen` 示例纯粹是为了说明问题，因为它本身已支持上下文管理器用法。

- `contextlib.aclosing(thing)`

异步版本，返回一个在语句块结束时调用 `await thing.aclose()` 的异步上下文管理器。本质上等价于：

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def aclosing(thing):
    try:
        yield thing
    finally:
        await thing.aclose()
```

它尤其重要的一点是：**支持异步生成器因 `break` 或异常而被提前退出时做确定性清理**：

```python
from contextlib import aclosing

async with aclosing(my_generator()) as values:
    async for value in values:
        if value == 42:
            break
```

这种模式确保生成器的异步退出代码在与其迭代相同的上下文中执行（异常和上下文变量能正确传播，退出代码也不会在其依赖的任务生命周期结束后继续运行）。

`aclosing` 于 **3.10** 版本加入。`closing` 为早期版本即提供的工具（官方文档未标注新增版本号）。

### 4.5 `nullcontext`

签名：`contextlib.nullcontext(enter_result=None)`

返回一个"什么都不做"的占位上下文管理器。它的 `__enter__` 会返回传给它的 `enter_result`（默认 `None`），除此之外不做任何事。它的用途是**充当可选的上下文管理器**：

```python
def myfunction(arg, ignore_exceptions=False):
    if ignore_exceptions:
        # 使用 suppress 来忽略所有异常。
        cm = contextlib.suppress(Exception)
    else:
        # 不忽略任何异常，cm 将没有影响。
        cm = contextlib.nullcontext()
    with cm:
        # 执行某些操作
```

使用 `enter_result` 的例子：

```python
def process_file(file_or_path):
    if isinstance(file_or_path, str):
        cm = open(file_or_path)          # 自己负责打开、负责关闭
    else:
        cm = nullcontext(file_or_path)   # 调用方负责关闭，这里只管"借"一下

    with cm as file:
        # 在 file 上执行处理
```

它也可以替代异步上下文管理器：

```python
async def send_http(session=None):
    if not session:
        cm = aiohttp.ClientSession()
    else:
        cm = nullcontext(session)
    async with cm as session:
        # 使用 session 发送 http 请求
```

版本说明：**3.7** 版本加入；**3.10** 版本起增加对异步上下文管理器的支持。

### 4.6 `suppress`

签名：`contextlib.suppress(*exceptions)`

返回一个能屏蔽指定异常的上下文管理器：当 `with` 代码块中抛出指定异常时，异常被吞掉，程序从 `with` 之后继续执行。

```python
from contextlib import suppress

with suppress(FileNotFoundError):
    os.remove('somefile.tmp')

with suppress(FileNotFoundError):
    os.remove('someotherfile.tmp')
```

等价于两个 `try/except FileNotFoundError: pass` 块。

**重要**：与任何完全吞掉异常的机制一样，`suppress` 应当只用来屏蔽非常具体、且"静默继续是正确的"那种错误，不要滥用。

该上下文管理器是**可重进入（reentrant）**的。

特殊行为：如果 `with` 代码块中的代码抛出了 `BaseExceptionGroup`，被抑制的异常会从异常分组中被移除；分组中其余未被抑制的异常会在一个由原分组 `derive()` 产生的新异常分组中被重新抛出。

版本说明：**3.4** 版本加入；**3.12** 版本起支持抑制作为 `BaseExceptionGroup` 组成部分的异常。

### 4.7 `redirect_stdout` 与 `redirect_stderr`

- `contextlib.redirect_stdout(new_target)`

把 `sys.stdout` 临时重定向到一个文件或类文件对象（如 `io.StringIO`）。它给那些"把输出硬编码写进 stdout"的既有函数或类提供了灵活性。

例如，`help()` 的输出默认写入 `sys.stdout`，可以重定向到 `io.StringIO` 来捕获为字符串：

```python
with redirect_stdout(io.StringIO()) as f:
    help(pow)
s = f.getvalue()
```

还可以重定向到磁盘文件：

```python
with open('help.txt', 'w') as f:
    with redirect_stdout(f):
        help(pow)
```

或重定向到 `sys.stderr`：

```python
with redirect_stdout(sys.stderr):
    help(pow)
```

**警告**：因为修改的是 `sys.stdout` 这样的全局状态，该上下文管理器不适合在库代码和大多数多线程程序里使用；它对子进程的输出也没有影响。但对许多工具脚本来说仍然很有用。

该上下文管理器是**可重进入（reentrant）**的，于 **3.4** 版本加入。

- `contextlib.redirect_stderr(new_target)`

与 `redirect_stdout` 类似，但重定向的是 `sys.stderr`。同样是**可重进入**的，于 **3.5** 版本加入。

### 4.8 `chdir`

签名：`contextlib.chdir(path)`

临时改变当前工作目录，退出时恢复原目录。它是对 `os.chdir()` 的简单包装——进入时切换目录，退出时还原。

```python
import os
from contextlib import chdir

with chdir("/tmp"):
    print("当前目录:", os.getcwd())
# 离开 with 后自动回到原目录
```

**非并行安全的警告**：因为它修改的是"当前工作目录"这一全局状态，所以不适合在大多数多线程或异步上下文中使用；也不适合生成器等非线性的执行流（当该上下文管理器处于激活状态时不应执行 `yield`）。

该上下文管理器是**可重进入**的，于 **3.11** 版本加入。

### 4.9 `ContextDecorator` 与 `AsyncContextDecorator`

- `class contextlib.ContextDecorator`

一个让你自定义的上下文管理器能**同时作为装饰器使用**的基类。继承它的上下文管理器仍需照常实现 `__enter__` 与 `__exit__`（`__exit__` 即使在作装饰器使用时也保留异常处理能力）。

```python
from contextlib import ContextDecorator

class mycontext(ContextDecorator):
    def __enter__(self):
        print('Starting')
        return self

    def __exit__(self, *exc):
        print('Finishing')
        return False
```

随后它既可用作装饰器，也可用作 `with`：

```python
@mycontext()
def function():
    print('The bit in the middle')

function()
# Starting / The bit in the middle / Finishing

with mycontext():
    print('The bit in the middle')
# Starting / The bit in the middle / Finishing
```

`ContextDecorator` 只是 `with cm():` 写法的语法糖，使意图（`cm` 作用于整个函数）更加清晰。它还可以作为混合类（mixin）与已有基类一起使用：

```python
class mycontext(ContextBaseClass, ContextDecorator):
    def __enter__(self):
        return self
    def __exit__(self, *exc):
        return False
```

> **注意**：因为被装饰的函数必须能被多次调用，对应的上下文管理器必须支持在多个 `with` 语句中使用；否则应改用显式 `with` 的形式。

`@contextmanager` 内部就使用了 `ContextDecorator`，因此用 `@contextmanager` 得到的上下文管理器自动获得装饰器能力。

于 **3.2** 版本加入。

- `class contextlib.AsyncContextDecorator`

与 `ContextDecorator` 类似，但用于异步函数（对应实现 `__aenter__` / `__aexit__`）。于 **3.10** 版本加入。

```python
from asyncio import run
from contextlib import AsyncContextDecorator

class mycontext(AsyncContextDecorator):
    async def __aenter__(self):
        print('Starting')
        return self
    async def __aexit__(self, *exc):
        print('Finishing')
        return False

@mycontext()
async def function():
    print('The bit in the middle')

run(function())
```

### 4.10 `ExitStack`

`class contextlib.ExitStack`

`ExitStack` 的目标是**把多个上下文管理器和清理函数组合起来管理**，尤其适合"个数可选"或"由输入数据驱动"的上下文管理器。

典型场景：一次 `with` 处理一组文件：

```python
with ExitStack() as stack:
    files = [stack.enter_context(open(fname)) for fname in filenames]
    # 所有已打开的文件都会在 with 结束时被自动关闭，
    # 即使中途某个 open 失败，之前已打开的文件也会被关闭
```

关键机制：

- 它的 `__enter__` 返回 `ExitStack` 实例本身，不做额外操作。
- 每个实例维护一个**回调栈**；关闭实例时（显式调用或 `with` 隐式在末尾），栈中的回调按**注册的相反顺序（后进先出）**被调用。
- **注意**：实例被垃圾回收时，回调**不会**被隐式调用——你必须确保它被关闭。
- 由于按相反顺序调用，最终行为等价于把这些回调用多个嵌套的 `with` 包起来；这种等价性也延伸到异常处理：内部回调若抑制或替换了异常，外部回调收到的参数是基于更新后的状态。

这是一个相对底层的 API，负责正确处理栈展开的细节，适合作为高层上下文管理器的基础。

`ExitStack` 于 **3.3** 版本加入。它提供以下方法：

#### `enter_context(cm)`

进入一个新的上下文管理器 `cm`，并把它的 `__exit__` 方法加入回调栈。返回 `cm.__enter__()` 的结果。

这些上下文管理器屏蔽异常的方式，与它们直接作为 `with` 一部分使用时一致。

版本说明：**3.11** 起，若 `cm` 不是上下文管理器，抛出 `TypeError`（此前为 `AttributeError`）。

#### `push(exit)`

把一个上下文管理器的 `__exit__` 方法加入回调栈。因为 `__enter__` **不会**被调用，所以可以用它来"推迟"或"接管"一部分 `__enter__` 的实现。

如果传入的不是上下文管理器，它会假设这是具有与 `__exit__` 相同签名的回调，并直接加入栈。

这些回调可以通过返回真值来抑制异常。传入的对象会被返回，因此该方法**可作为函数装饰器使用**。

#### `callback(callback, /, *args, **kwds)`

接受任意回调函数及参数并加入回调栈。与其他方法不同，以此方式加入的回调**无法抑制异常**（异常细节不会传给它们）。传入的回调会被返回，因此也可作为函数装饰器使用。

#### `pop_all()`

把整个回调栈转移到**一个新的 `ExitStack` 实例**并返回它。此操作**不会触发任何回调**；这些回调会改由新栈在被关闭时触发（显式或 `with` 结束隐式触发）。

典型用途——"全有或全无"地打开一组文件：

```python
with ExitStack() as stack:
    files = [stack.enter_context(open(fname)) for fname in filenames]
    close_files = stack.pop_all().close  # 持有 close 方法，但暂不调用
    # 若有文件打开失败，之前打开的会全部自动关闭；
    # 若全部成功，则 with 结束后它们仍保持打开，
    # 之后可显式调用 close_files() 一次全部关闭。
```

#### `close()`

立即展开回调栈，按注册的相反顺序调用所有回调。对已注册的上下文管理器和退出回调，传入的参数表示"没有异常发生"。

### 4.11 `AsyncExitStack`

`class contextlib.AsyncExitStack`

一个**异步上下文管理器**，类似 `ExitStack`，支持同时组合同步与异步上下文管理器，并可为清理逻辑使用协程。

它的 `close()` 方法未实现，必须改用 `aclose()` 代替。

于 **3.7** 版本加入。方法如下：

#### `async enter_async_context(cm)`

类似 `enter_context()`，但要求传入一个异步上下文管理器。

版本说明：**3.11** 起，若 `cm` 不是异步上下文管理器，抛出 `TypeError`（此前为 `AttributeError`）。

#### `push_async_exit(exit)`

类似 `push()`，但要求传入异步上下文管理器或协程函数。

#### `push_async_callback(callback, /, *args, **kwds)`

类似 `callback()`，但要求传入协程函数。

#### `async aclose()`

类似 `close()`，但能正确处理可等待对象。

用法示例：

```python
async with AsyncExitStack() as stack:
    connections = [await stack.enter_async_context(get_connection())
                   for i in range(5)]
    # 所有连接都会在 async with 结束时自动关闭，
    # 即使中途某个连接建立失败
```

## 五、官方"例子和配方"中的典型用法

官方文档提供了五个典型的应用配方，此处逐一说明。

### 5.1 支持可变数量的上下文管理器

`ExitStack` 最主要的应用就是在一条 `with` 语句中管理**数量不定**的上下文管理器。数量变化可能来自用户输入（如打开用户指定的一组文件），或来自"某些资源是可选的"：

```python
with ExitStack() as stack:
    for resource in resources:
        stack.enter_context(resource)
    if need_special_resource():
        special = acquire_special_resource()
        stack.callback(release_special_resource, special)
    # 执行使用所获资源的操作
```

可见，`ExitStack` 还能让不原生支持上下文管理协议的资源也纳入 `with` 管理。

### 5.2 捕获 `__enter__` 产生的异常

有时你只想捕获来自 `__enter__` 实现的异常，而**不想误伤** `with` 代码块或 `__exit__` 的异常。借助 `ExitStack` 可以稍作拆分来实现：

```python
stack = ExitStack()
try:
    x = stack.enter_context(cm)
except Exception:
    # 处理 __enter__ 异常
else:
    with stack:
        # 处理正常情况
```

实际需要这样做，通常说明底层 API 本应提供一个可直接配合 `try/except/finally` 的资源管理接口；但在只有上下文管理器这一种管理手段时，`ExitStack` 能帮你应对 `with` 不好直接处理的情形。

### 5.3 在 `__enter__` 实现中做清理

如果在 `__enter__` 里的后续步骤失败，可以用 `ExitStack` 清理已分配的资源。下面是官方给出的一个例子——一个可接受"获取函数、释放函数、可选校验函数"并把它们映射到上下文管理协议的通用资源管理器：

```python
from contextlib import contextmanager, AbstractContextManager, ExitStack

class ResourceManager(AbstractContextManager):
    def __init__(self, acquire_resource, release_resource, check_resource_ok=None):
        self.acquire_resource = acquire_resource
        self.release_resource = release_resource
        if check_resource_ok is None:
            def check_resource_ok(resource):
                return True
        self.check_resource_ok = check_resource_ok

    @contextmanager
    def _cleanup_on_error(self):
        with ExitStack() as stack:
            stack.push(self)
            yield
            # 校验通过且未抛异常时，保留资源并回传给调用方
            stack.pop_all()

    def __enter__(self):
        resource = self.acquire_resource()
        with self._cleanup_on_error():
            if not self.check_resource_ok(resource):
                msg = "Failed validation for {!r}"
                raise RuntimeError(msg.format(resource))
        return resource

    def __exit__(self, *exc_details):
        # 无需复制释放逻辑
        self.release_resource()
```

### 5.4 替代 try/finally 与旗标变量

有时你会看到这样的模式：用 `try-finally` 加一个布尔"旗标"来决定 `finally` 是否执行清理：

```python
cleanup_needed = True
try:
    result = perform_operation()
    if result:
        cleanup_needed = False
finally:
    if cleanup_needed:
        cleanup_resources()
```

`ExitStack` 提供更清晰的替代：先登记回调，之后根据需要决定是否跳过它：

```python
from contextlib import ExitStack

with ExitStack() as stack:
    stack.callback(cleanup_resources)
    result = perform_operation()
    if result:
        stack.pop_all()
```

如果频繁使用这种模式，可以封装一个辅助类：

```python
from contextlib import ExitStack

class Callback(ExitStack):
    def __init__(self, callback, /, *args, **kwds):
        super().__init__()
        self.callback(callback, *args, **kwds)

    def cancel(self):
        self.pop_all()

with Callback(cleanup_resources) as cb:
    result = perform_operation()
    if result:
        cb.cancel()
```

如果清理逻辑尚未独立成函数，也可以用装饰器形式提前声明：

```python
from contextlib import ExitStack

with ExitStack() as stack:
    @stack.callback
    def cleanup_resources():
        ...
    result = perform_operation()
    if result:
        stack.pop_all()
```

> 注意：以装饰器形式声明的回调**不能接收任何形参**（受装饰器协议限制），要释放的资源须作为闭包变量访问。

### 5.5 将上下文管理器作为函数装饰器

`ContextDecorator` 让上下文管理器既能用于 `with`，也能作装饰器。例如想追踪一段代码的进出时间，只需继承 `ContextDecorator`，一个定义同时获得两种能力：

```python
from contextlib import ContextDecorator
import logging

logging.basicConfig(level=logging.INFO)

class track_entry_and_exit(ContextDecorator):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        logging.info('Entering: %s', self.name)

    def __exit__(self, exc_type, exc, exc_tb):
        logging.info('Exiting: %s', self.name)
```

既可用作上下文管理器：

```python
with track_entry_and_exit('widget loader'):
    print('Some time consuming activity goes here')
    load_widget()
```

也可用作函数装饰器：

```python
@track_entry_and_exit('widget loader')
def activity():
    print('Some time consuming activity goes here')
    load_widget()
```

> 注意：把上下文管理器作装饰器用时有一个额外限制——**无法访问 `__enter__` 的返回值**。如果需要该返回值，仍应使用显式的 `with` 语句。

## 六、单个使用 / 可重用 / 可重进入的区别

上下文管理器按"可复用程度"可划分为三类，理解它们能避免大量难以排查的 bug。

### 6.1 单次使用（Single-use）

大多数上下文管理器只能在一个 `with` 中有效使用**一次**；第二次使用会抛异常或行为错误。因此惯例是**在使用处（`with` 语句开头）直接创建**它们。

文件对象就是典型的单次使用上下文管理器——第一个 `with` 会关闭文件，之后对该文件对象的任何 IO 都会失败。

用 `@contextmanager` 创建的也是单次使用的；第二次使用会因底层生成器"没有 yield"而报错：

```python
>>> from contextlib import contextmanager
>>> @contextmanager
... def singleuse():
...     print("Before")
...     yield
...     print("After")
>>> cm = singleuse()
>>> with cm:
...     pass
Before
After
>>> with cm:        # 第二次使用
...     pass
Traceback (most recent call last):
    ...
RuntimeError: generator didn't yield
```

### 6.2 可重进入（Reentrant）

"可重进入"的上下文管理器不仅可用于多个 `with`，还可在**已经使用了同一实例的 `with` 内部**再次使用。

`threading.RLock` 是可重入的例子；`suppress()`、`redirect_stdout()`、`redirect_stderr()`（以及 `chdir()`）也都是可重进入的。简单示例：

```python
>>> from contextlib import redirect_stdout
>>> from io import StringIO
>>> stream = StringIO()
>>> write_to_stream = redirect_stdout(stream)
>>> with write_to_stream:
...     print("这条被写进 stream 而非 stdout")
...     with write_to_stream:
...         print("这条也被写进 stream")
>>> print("这条直接写进 stdout")
这条直接写进 stdout
>>> print(stream.getvalue())
这条被写进 stream 而非 stdout
这条也被写进 stream
```

现实中的可重入场景往往涉及多个函数互相调用，比这个例子复杂得多。

> 提示：**可重入 ≠ 线程安全**。例如 `redirect_stdout` 肯定不是线程安全的，因为它通过把 `sys.stdout` 绑定到不同流，对系统状态做了全局修改。

### 6.3 可重用（Reusable，但不可重入）

介于两者之间的是"可重用、但不可重入"：实例支持**多次使用**，但若某个实例已处于包含它的 `with` 语句中、又嵌套使用就失败（或不正确）。

`threading.Lock` 是"可重用但不可重入"的例子（要可重入得用 `threading.RLock`）。

`ExitStack` 也是一个"可重用但不可重入"的例子：因为它在**离开任意 `with` 时都会调用当前已注册的全部回调**，不论回调是在哪一层注册的。嵌套使用同一实例会在最内层 `with` 结束时提前清空栈，一般不符合预期：

```python
>>> from contextlib import ExitStack
>>> stack = ExitStack()
>>> with stack:
...     stack.callback(print, "Callback: from first context")
...     print("Leaving first context")
Leaving first context
Callback: from first context
>>> with stack:                # 复用没问题
...     stack.callback(print, "Callback: from second context")
...     print("Leaving second context")
Leaving second context
Callback: from second context
>>> with stack:                # 但嵌套会提前清空
...     stack.callback(print, "Callback: from outer context")
...     with stack:
...         stack.callback(print, "Callback: from inner context")
...         print("Leaving inner context")
...     print("Leaving outer context")
Leaving inner context
Callback: from inner context
Callback: from outer context
Leaving outer context
```

上例输出显示：嵌套时最内层 `with` 结束时就把两个回调都触发掉了。需要嵌套时应使用**各自独立的实例**：

```python
>>> with ExitStack() as outer_stack:
...     outer_stack.callback(print, "Callback: from outer context")
...     with ExitStack() as inner_stack:
...         inner_stack.callback(print, "Callback: from inner context")
...         print("Leaving inner context")
...     print("Leaving outer context")
Leaving inner context
Callback: from inner context
Leaving outer context
Callback: from outer context
```

## 七、可运行示例

下面给出几个完整、可直接运行的示例。

### 示例 1：用 `@contextmanager` 模拟一对"操作前/操作后"配对

```python
from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>")
    yield
    print(f"</{name}>")

with tag("h1"):
    print("这是一段正文")

# 输出：
# <h1>
# 这是一段正文
# </h1>
```

### 示例 2：用 `ExitStack` 一次性管理多个文件，并捕获 `__enter__` 异常

```python
import os
from contextlib import ExitStack, suppress

filenames = ["a.txt", "b.txt", "c.txt"]

# 打开多个文件并写入，之后自动全部关闭
with ExitStack() as stack:
    files = [stack.enter_context(open(fn, "w")) for fn in filenames]
    for f in files:
        f.write("hello\n")

# 删除不存在的文件也不报错
with suppress(FileNotFoundError):
    os.remove("not_exist.tmp")

print("已写入文件:", filenames)
```

### 示例 3：捕获 `help()` 输出并临时切换工作目录

```python
import io
import os
from contextlib import redirect_stdout, chdir

# 把 help() 的输出捕获到字符串
buf = io.StringIO()
with redirect_stdout(buf):
    help(pow)
print("捕获的 help 输出长度:", len(buf.getvalue()))

# 临时切换工作目录，退出后自动还原
original = os.getcwd()
with chdir("C:/"):
    print("切换后目录:", os.getcwd())
print("已还原目录:", os.getcwd() == original)
```

## 八、版本可用性说明

下表汇总各 API 的新增版本（以官方文档标注为准）：

| API | 新增版本 | 备注 |
|---|---|---|
| `closing` | 早期版本即提供 | 官方文档未标注具体版本号 |
| `ContextDecorator` | 3.2 | — |
| `@contextmanager` | 早期版本即提供 | 3.2 起引入 `ContextDecorator` 使用，可作为装饰器 |
| `ExitStack` | 3.3 | `enter_context` 于 3.11 变更（抛 `TypeError`） |
| `suppress` | 3.4 | 3.12 起支持 `BaseExceptionGroup` |
| `redirect_stdout` | 3.4 | — |
| `redirect_stderr` | 3.5 | — |
| `AbstractContextManager` | 3.6 | — |
| `AbstractAsyncContextManager` | 3.7 | — |
| `@asynccontextmanager` | 3.7 | 3.10 起可作为装饰器 |
| `nullcontext` | 3.7 | 3.10 起支持异步上下文管理器 |
| `AsyncExitStack` | 3.7 | `enter_async_context` 于 3.11 变更（抛 `TypeError`） |
| `aclosing` | 3.10 | — |
| `AsyncContextDecorator` | 3.10 | — |
| `chdir` | 3.11 | — |

> 说明：本章节标题为"Python 3.14 标准库 contextlib"，指的是基于 Python 3.14 官方文档撰写；官方文档中未标注 contextlib 在 3.14 版本的新增 API。

## 九、注意事项与反模式

1. **`@contextmanager` 的生成器必须且只能 `yield` 一次**。yield 零次或多次都会在 `with` 结束时抛出异常（多次 yield 会报"generator yielded more than once"之类错误；零次则报"generator didn't yield"）。
2. **在 `@contextmanager` 中捕获异常后，若不打算吞掉它，必须重新 `raise`**。忘记重抛会让异常被"意外吞掉"，程序静默继续运行。
3. **`ExitStack` 被垃圾回收时回调不会执行**。一定要确保它被关闭——通常用 `with ExitStack() as stack:` 包裹。
4. **`redirect_stdout` / `redirect_stderr` / `chdir` 会修改全局状态**，不是线程安全的，不要用在库代码或并发程序中。
5. **`suppress` 不要用来吞掉范围过宽的异常**（如裸 `suppress(Exception)`），这会让真正的 bug 被掩盖。应只抑制具体、且可安全忽略的错误。
6. **单次使用与可重用的边界**：`@contextmanager` 产出的实例只能使用一次，不要复用同一个实例进入第二次 `with`。
7. **`ExitStack` 是可重用但不可重入**：不要嵌套使用同一个 `ExitStack` 实例，嵌套场景应各自创建新实例。
8. **`closing()` 只对有 `close()` 方法的对象有用**；若对象本身就是上下文管理器，直接用 `with obj:` 更简洁。
9. **装饰器形式的 `stack.callback` 无法接收参数**：需要传参时改用显式调用 `stack.callback(cb, *args, **kwds)`。

## 十、与 contextvars 的简要关系

`contextvars` 模块（下一章详解）提供 `ContextVar`，用于在异步、并发代码中传播"上下文局部"的变量值，是对**进程级全局状态**的一种更安全替代。它与 `contextlib` 的关系主要体现在两点：

1. **互补而非替代**：`contextlib` 中的 `redirect_stdout`、`chdir` 修改的是真正的全局状态（`sys.stdout`、进程工作目录），天然不是并发安全的；而 `contextvars` 用 `ContextVar` 在每个上下文（任务/线程）里维护独立的变量值，恰好适合解决"需要临时改变某个设定、又不想破坏全局状态"的场景。
2. **清理回调的执行上下文**：官方文档在 `aclosing` 中特别指出，其保证"生成器的异步退出代码在与迭代相同的上下文中执行，这样异常和**上下文变量**将能按预期工作"。这说明 `contextlib` 的清理机制（含 `ExitStack`/`@contextmanager` 的回调）尊重并延续了 `contextvars` 建立的上下文，二者协作良好。

简言之：`contextlib` 解决"进入/退出时做什么"，`contextvars` 解决"如何在并发的各个上下文中各自持有某个值"。

## 十一、章节导航

- [上一章：版本背景与模块可用性](01-version-prerequisites.md) →
- [下一章：contextvars](03-contextvars.md) →