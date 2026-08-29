---
id: "python314-stdlib-wiki-03"
title: "Python 3.14 标准库 contextvars 全面详解"
source: "https://docs.python.org/3.14/"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/04-docs-markup-tooling/python314-stdlib-wiki/03-contextvars.toml"
---
# Python 3.14 标准库 contextvars 全面详解

> 一句话摘要：`contextvars` 模块提供了一组"上下文局部变量"的管理 API，让每个异步任务（或每次 `Context.run()` 执行）都能持有彼此隔离的状态，从根本上避免并发代码中状态意外串扰的问题。

## 1. 模块定位与用途

在编写并发代码（尤其是使用 `asyncio` 的协程并发，或使用线程池、任务队列的混合模型）时，一个经典难题是：**如何在不把参数层层传递的情况下，让"当前执行单元"拥有自己的局部状态？**

传统上人们用以下手段，但它们各有缺陷：

- **全局变量**：所有执行单元共享同一份状态，无法隔离，任务之间会互相覆盖。
- **`threading.local()` 线程局部变量**：按"线程"隔离，但无法按"异步任务"隔离。在 `asyncio` 中，多个协程任务会运行在同一个线程里、不断切换执行，`threading.local()` 无法区分它们。
- **层层传参**：把状态作为参数一路传递下去，代码侵入性强、可读性差，且无法覆盖"第三方代码中途调用你"的场景。

`contextvars` 模块正是为这个场景设计的。它提供**上下文变量（Context Variable）**机制：一个 `ContextVar` 是全局唯一的"变量声明"，但它的**取值**绑定在"当前上下文"上。每个异步任务在创建时都会获得一份当前上下文的副本，因此不同任务对同一个 `ContextVar` 的赋值彼此隔离、互不影响。

官方文档特别提示：**在有状态的并发代码中，应当使用上下文变量而不是 `threading.local()`**，以防止状态意外"泄漏"到其他代码中。

## 2. 核心术语表

| 术语 | 一句话平实解释 |
|---|---|
| 上下文变量（Context Variable） | 由 `ContextVar` 声明的变量声明；声明本身是全局唯一的，但其"取值"在不同上下文里可以各自不同。 |
| 上下文（Context） | 一个记录"每个上下文变量当前取值"的映射对象；不同的上下文之间取值互不干扰。 |
| 当前上下文（current context） | 每个线程都有一个上下文栈，栈顶那个就是"当前上下文"，所有 `ContextVar` 的读写都作用于它。 |
| Token | `ContextVar.set()` 返回的一个"还原凭据"；用它可以随时把变量恢复到设置之前的值。 |
| MISSING | 一个占位标记，表示"这个变量在设置之前还没有任何值"。 |
| 上下文栈 | 每个线程内部维护的一组相继"进入"的上下文；`run()` 进入一个上下文时把它压栈，退出时弹栈。 |
| 上下文传播 | 异步任务或 `Context.run()` 启动时，自动"复制"一份当前上下文带过去的机制。 |

## 3. 核心类与函数详解

### 3.1 `contextvars.ContextVar` —— 上下文变量

```python
class contextvars.ContextVar(name[, *, default])
```

`ContextVar` 用于声明一个新的上下文变量。通常这样创建：

```python
var: ContextVar[int] = ContextVar('var', default=42)
```

- **`name`（必需参数）**：字符串，仅用于内省和调试，必须提供。
- **`default`（可选，仅限关键字参数）**：当在当前上下文中找不到该变量的值时，由 `get()` 返回这个默认值。

> **重要提示（官方强调）**：上下文变量应当在**模块顶层**创建，**永远不要**在闭包中创建。因为 `Context` 对象会对上下文变量持有**强引用**，若在闭包里创建，会导致这些变量无法被垃圾回收器正确回收。

自 Python 3.14 起，`ContextVar` 可以对所容纳的值类型作泛型标注（如 `ContextVar[int]`）。

**`name` 属性**（只读）：返回该上下文变量的名称字符串。该属性自 Python 3.7.1 加入。

**`get([default])`**：返回当前上下文中此上下文变量的值。如果当前上下文没有该变量的值，方法按以下优先级依次处理：

1. 若调用时提供了 `default` 参数，返回该参数的值；
2. 否则，若创建变量时提供了默认值，返回创建时的默认值；
3. 否则，抛出 `LookupError` 异常。

**`set(value)`**：在当前上下文中为该变量设置一个新值。必选参数 `value` 是新值。方法返回一个 `Token` 对象，之后可通过 `reset(token)` 把变量恢复到 `set()` 之前的状态。

自 Python 3.14 起，返回的 `Token` 对象可以直接用作上下文管理器（详见 3.2 节），从而免去手动调用 `reset()`：

```python
var = ContextVar('var', default='default value')
with var.set('new value'):
    assert var.get() == 'new value'
assert var.get() == 'default value'
```

上面这段代码等价于：

```python
token = var.set('new value')
try:
    assert var.get() == 'new value'
finally:
    var.reset(token)
assert var.get() == 'default value'
```

**`reset(token)`**：把上下文变量还原到"创建 `token` 的那次 `set()` 调用之前"的状态。例如：

```python
var = ContextVar('var')
token = var.set('new value')
# 此处使用 'var' 的代码中，var.get() 会返回 'new value'。
var.reset(token)
# 重置之后，'var' 不再有值，
# 因此 var.get() 会抛出 LookupError。
```

**需要特别注意**：同一个 `token` **不能使用两次**（一个 token 只能重置一次）。

### 3.2 `contextvars.Token` —— 还原凭据

```python
class contextvars.Token
```

`Token` 对象由 `ContextVar.set()` 方法返回，可以传给 `ContextVar.reset()`，把变量值还原为对应 `set()` 调用之前的状态。自 Python 3.14 起，`Token` 还支持**上下文管理器协议**，进入 `with` 块时自动完成设置、退出时自动完成重置。

`Token` 有三个属性：

- **`var`**（只读）：指向创建该 token 的那个 `ContextVar` 对象。
- **`old_value`**（只读）：记录"创建该 token 的 `set()` 调用发生之前"该变量的值。如果调用前变量尚未被设置过值，则该属性指向 `Token.MISSING`。
- **`MISSING`**：一个占位标记对象，专供 `Token.old_value` 使用，用来表示"此前无值"。

### 3.3 `contextvars.copy_context()` —— 拷贝当前上下文

```python
contextvars.copy_context()
```

返回当前上下文（`Context` 对象）的一份**拷贝**。例如，下面的代码抓取当前上下文的拷贝并打印其中设置的所有变量及值：

```python
ctx: Context = copy_context()
print(list(ctx.items()))
```

该函数具有 **O(1) 复杂度**——无论上下文中只有几个变量还是有非常多变量，运行速度都相同。

### 3.4 `contextvars.Context` —— 上下文对象

```python
class contextvars.Context
```

`Context` 是"上下文变量到其取值"的映射。`Context()` 会创建一个**不含任何值**的空上下文；若要拿到当前上下文的拷贝，应使用 `copy_context()` 函数，而不是直接构造。

关于 `Context` 的工作机制，官方文档给出了如下关键描述：

- 每个线程都有**自己的一套 `Context` 对象栈**。当前上下文就是当前线程栈顶的那个 `Context`。
- **进入（entering）**一个上下文：通过调用它的 `run()` 方法实现，会把它压入当前线程的上下文栈顶，使之成为当前上下文。
- **退出（exiting）**当前上下文：通过让传给 `run()` 的回调函数返回实现，会把它从栈顶弹出，使当前上下文恢复为进入之前的状态。
- 由于每个线程各自有上下文栈，`ContextVar` 在不同线程中赋值时的行为类似于 `threading.local()`。
- 尝试进入一个**已经被进入**的上下文（包括在其他线程中被进入的上下文），会抛出 `RuntimeError`。
- 一个上下文退出后，之后可以从任意线程**重新进入**。
- 对 `ContextVar` 值的一切修改（通过 `ContextVar.set()`）都会记录在**当前上下文**中；`get()` 返回与当前上下文关联的值。**退出一个上下文必然撤销进入该上下文期间对上下文变量所做的修改**（如有需要，重新进入该上下文即可恢复这些值）。

`Context` 实现了 `collections.abc.Mapping` 接口，因此支持下列操作：

- **`run(callable, *args, **kwargs)`**：进入该 Context，执行 `callable(*args, **kwargs)`，然后退出该 Context。返回 `callable` 的返回值；若执行中发生异常，则向外传播该异常。
- **`copy()`**：返回该上下文对象的一份**浅拷贝**。
- **`var in context`**（对应 `__contains__`）：若上下文中有变量 `var` 的值，返回 `True`，否则返回 `False`。
- **`context[var]`**（对应 `__getitem__`）：返回变量 `var` 的值；若上下文中不包含该变量，抛出 `KeyError`。
- **`get(var[, default])`**：若 `var` 在上下文对象中有值，返回该值；否则返回 `default`；若未提供 `default`，返回 `None`。
- **`iter(context)`**（对应 `__iter__`）：返回一个迭代器，依次产出存储在该上下文对象中的变量。
- **`len(context)`**（对应 `__len__`）：返回该上下文对象中所设置变量的数量。
- **`keys()`**：返回该上下文对象中所有变量的列表。
- **`values()`**：返回该上下文对象中所有变量值的列表。
- **`items()`**：返回一个二元组列表，每个二元组含有一个变量及其值。

> **澄清说明**：`Context` 作为一个只读的映射集合，**本身并不提供 `set()` / `reset()` 方法**（这两个方法属于 `ContextVar`）；对变量取值的写入一律通过 `ContextVar.set()` 完成，并记录在当前上下文中。同理，`MISSING` 是 `Token.MISSING` 的标记对象，而**不是** `Context` 的属性。

## 4. 上下文传播机制

`contextvars` 的核心威力在于**上下文传播**，其要点有三：

1. **`copy_context()` 制造快照**：`copy_context()` 以 O(1) 复杂度取得当前上下文的一份独立拷贝，是"隔离"与"恢复"的基础。
2. **`Context.run()` 在指定上下文中执行**：把任意上下文通过 `run()` 压入当前线程的上下文栈，让其中的可调用对象在**那份上下文**中运行；运行期间的变量修改被限制在该上下文内，退出后自动回到原上下文。
3. **asyncio 任务自动继承上下文副本**：在 `asyncio` 中，每个 Task 被创建/调度时会**自动复制当前上下文**。因此无需任何额外配置，Task 内部对上下文变量的设置就不会泄漏到其他 Task，也不会影响创建它的协程。

简言之：变量声明是全局的，变量取值是随上下文传播的；"谁在哪个上下文里跑，看到的（以及改动的）就是那个上下文里的值"。

## 5. 手动管理上下文的示例

下面的示例展示了同一个 `ContextVar` 在多个 `Context` 之间各自 `set`、互不干扰的效果。这是理解 `Context.run()` 隔离语义最直接的演示：

```python
import contextvars

var = contextvars.ContextVar('var')
var.set('spam')

print(var.get())          # 输出 'spam'

# 抓取当前上下文的快照
ctx = contextvars.copy_context()

def main():
    # 在调用 copy_context() 与 ctx.run(main) 之前，
    # 'var' 已被设为 'spam'，因此快照中继承了这个值：
    print(var.get())      # 输出 'spam'
    print(ctx[var])       # 输出 'spam'

    # 在 ctx 上下文内把 'var' 改为 'ham'
    var.set('ham')
    print(var.get())      # 输出 'ham'
    print(ctx[var])       # 输出 'ham'

# 在 'ctx' 这个上下文中运行 main()，
# 因此对 'var' 的修改被包含在 ctx 里：
ctx.run(main)

print(ctx[var])           # 输出 'ham'   （修改留在了 ctx 快照中）
print(var.get())          # 输出 'spam'  （主上下文中的值并未改变）
```

要点：`ctx.run(main)` 期间对 `var` 的赋值只写在 `ctx` 里；`main()` 结束后，主上下文中的 `var` 仍然是 `'spam'`，而 `ctx` 快照中则是 `'ham'`。

## 6. 可运行代码示例

### 6.1 基本用法：set / get / reset 与 Token

```python
import contextvars

# 声明两个上下文变量
user_id = contextvars.ContextVar('user_id', default='anonymous')
request_id = contextvars.ContextVar('request_id')

print(user_id.get())                     # 输出 'anonymous'（用创建时的默认值）

token = user_id.set('u-1001')
print(user_id.get())                     # 输出 'u-1001'

request_id.set('req-42')
print(request_id.get())                  # 输出 'req-42'
print(request_id.get('fallback'))        # 输出 'req-42'（已有值，忽略 default 参数）

# 用 token 还原 user_id
user_id.reset(token)
print(user_id.get())                     # 输出 'anonymous'

# request_id 从未被重置，其值仍在
print(request_id.get())                  # 输出 'req-42'

# Python 3.14：token 可直接作为上下文管理器使用
with user_id.set('u-2002'):
    print(user_id.get())                 # 输出 'u-2002'
print(user_id.get())                     # 输出 'anonymous'（退出 with 后自动 reset）
```

### 6.2 asyncio 并发任务隔离

```python
import asyncio
import contextvars

current_user = contextvars.ContextVar('current_user', default='<none>')


async def worker(name: str, delay: float):
    # 每个 Task 都持有自己的一份上下文副本，
    # 这里的 set() 不会影响其他 Task。
    current_user.set(name)
    await asyncio.sleep(delay)
    print(f'{name}: 醒来后看到的 current_user = {current_user.get()}')


async def main():
    await asyncio.gather(
        worker('alice', 0.2),
        worker('bob', 0.1),
        worker('carol', 0.3),
    )
    # 主协程的上下文从未被 worker 修改过
    print(f'main: current_user = {current_user.get()}')


asyncio.run(main())
```

运行结果（任务完成顺序取决于各自 `sleep` 时长，但**每个任务看到的都是自己设置的值**）：

```text
bob: 醒来后看到的 current_user = bob
alice: 醒来后看到的 current_user = alice
carol: 醒来后看到的 current_user = carol
main: current_user = <none>
```

> 若改用 `threading.local()` 之类的线程局部存储，由于这些协程可能运行在同一线程中，就无法实现上述任务级隔离——这正是 `contextvars` 的价值所在。

## 7. 版本可用性与参考说明

- 本模块自 **Python 3.7** 引入，规范详见 [PEP 567](https://peps.python.org/pep-0567/)。
- `ContextVar.name` 属性自 **Python 3.7.1** 加入。
- 自 **Python 3.14** 起，`Token` 对象新增了对**上下文管理器协议**的支持（可直接用 `with var.set(...)`），并且 `ContextVar` 与 `Token` 均支持对容器值类型的泛型标注。
- 官方文档（中文）：https://docs.python.org/zh-cn/3.14/library/contextvars.html
- 官方文档（英文）：https://docs.python.org/3.14/library/contextvars.html

## 8. 注意事项 / 反模式

- **不要在闭包中创建 `ContextVar`**：`Context` 持有上下文变量的强引用，闭包内创建会导致变量无法被垃圾回收。
- **禁止在无 `ContextVar` 支持的环境中使用**：`contextvars` 依赖运行时的"当前上下文"概念；在不理解上下文传播的第三方框架，或 Python 3.7 之前的环境中，无法获得预期效果（模块于 3.7 才引入）。
- **同一个 `Token` 只能使用一次**：`token` 被 `reset()` 后即失效，重复使用同一 token 会出错。
- **警惕 Token 泄漏**：若 `set()` 之后忘了 `reset()`（又未使用 3.14 提供的 `with` 写法），在当前上下文中会残留旧值。对于长生命周期的上下文（如长期运行的任务），建议总是用 `with var.set(...)` 或 `try/finally` 保证还原。
- **进入已进入的上下文会抛 `RuntimeError`**：包括在其他线程中已被进入的上下文，也不能重复 `run()`。
- **注意 GC 机制**：因为存在强引用，务必在模块顶层创建上下文变量，避免内存隐患。
- **性能考量**：`copy_context()` 为 O(1)，但 `Context.run()` 仍涉及上下文栈的压入/弹出；`set()` 会触发写时复制（copy-on-write）。在极端高频的读写路径上，仍应避免不必要的变量设置。
- **`get()` 的默认值优先级**：方法参数 `default` > 创建时的默认值 > 抛 `LookupError`；请勿混淆二者的先后顺序。

## 9. 与 contextlib 的简要关系

`contextvars` 与 `contextlib` 都含"上下文"二字，但关注点不同，二者是**互补**关系：

- `contextlib` 服务于 `with` 语句，即**上下文管理器协议**（`__enter__` / `__exit__`），解决"资源的进入与退出"问题，典型如 `contextlib.contextmanager`、`contextlib.suppress`、`contextlib.asynccontextmanager`。
- `contextvars` 解决的是**并发执行上下文中的状态隔离**问题，与 `with` 语法本身无直接关系。

二者的交汇点出现在 **Python 3.14**：`ContextVar.set()` 返回的 `Token` 开始实现上下文管理器协议，于是可以用 `with var.set(value):` 的写法在代码块退出时自动还原变量——把 `contextvars` 的状态还原能力"挂接"到了 `with` 语法上。

## 10. 章节导航

- [上一章：contextlib](02-contextlib.md) →
- [下一章：sys.monitoring](04-sys-monitoring.md) →