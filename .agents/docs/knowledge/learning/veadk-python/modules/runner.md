---
id: runner-module
title: Runner 类 API 参考
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# Runner 类 API 参考

## 类签名与继承关系

```python
class Runner(ADKRunner):
```

**继承链**：`Runner` → `ADKRunner`（google.adk.runners）

`Runner` 类是 VeADK 的对话运行器，在 Google ADK 的 `Runner` 基础上扩展了会话管理、记忆集成、追踪、媒体上传等功能。它是驱动 Agent 执行对话的核心入口。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L329-L789](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L329-L789)

---

## 公开属性

| 属性名 | 类型 | 说明 |
|--------|------|------|
| `user_id` | `str` | 默认用户 ID |
| `long_term_memory` | `Optional[LongTermMemory]` | 长期记忆服务实例，未设置则为 `None` |
| `short_term_memory` | `Optional[ShortTermMemory]` | 短期记忆实例，用于自动创建/管理会话 |
| `upload_inline_data_to_tos` | `bool` | 运行时是否将内联媒体上传到 TOS |
| `session_service` | `SessionService` | 会话服务实例（可能来自短期记忆） |
| `memory_service` | `MemoryService` | 记忆服务实例（可能来自 Agent 的长期记忆） |
| `app_name` | `str` | 应用名称，用于会话管理和对象路径 |
| `run_processor` | `BaseRunProcessor` | 运行处理器实例 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L355-L466](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L355-L466)

---

## 类型定义

### `RunnerMessage`

```python
RunnerMessage = Union[
    str,                     # 单轮文本提示
    list[str],               # 多轮文本提示
    MediaMessage,            # 单轮带媒体的提示
    list[MediaMessage],      # 多轮带媒体的提示
    list[MediaMessage | str],# 多轮混合媒体和文本提示
]
```

支持的输入消息类型：
- `str`：单轮文本提示
- `MediaMessage`：单轮多模态提示（文本 + 图片/视频）
- `list`：上述类型的列表（支持多轮混合文本和多模态）

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L46-L52](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L46-L52)

---

## `__init__` 构造函数

```python
def __init__(
    self,
    agent: BaseAgent | Agent | None = None,
    short_term_memory: ShortTermMemory | None = None,
    app_name: str | None = None,
    user_id: str = "veadk_default_user",
    upload_inline_data_to_tos: bool = False,
    run_processor: "BaseRunProcessor | None" = None,
    *args,
    **kwargs,
) -> None
```

### 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `agent` | `BaseAgent \| Agent \| None` | `None` | 用于运行交互的 Agent 实例 |
| `short_term_memory` | `ShortTermMemory \| None` | `None` | 可选的短期记忆；若未提供且未提供外部 `session_service`，将创建内存会话服务 |
| `app_name` | `str \| None` | `None` | 应用名称，默认为 `"veadk_default_app"` |
| `user_id` | `str` | `"veadk_default_user"` | 默认用户 ID |
| `upload_inline_data_to_tos` | `bool` | `False` | 是否启用内联媒体上传到 TOS |
| `run_processor` | `BaseRunProcessor \| None` | `None` | 可选的运行处理器，用于拦截 Agent 执行。若未提供，将尝试从 Agent 获取；若 Agent 也没有，则使用 `NoOpRunProcessor` |
| `*args` | | | 传递给 `ADKRunner` 的位置参数 |
| `**kwargs` | | | 传递给 `ADKRunner` 的关键字参数，可包含 `session_service` 和 `memory_service` 以覆盖默认值 |

### 初始化流程

1. **会话服务选择**：根据提供的短期记忆或外部 `session_service` 选择会话服务
2. **记忆服务选择**：优先使用传入的 `memory_service`，否则使用 Agent 的长期记忆
3. **RunProcessor 优先级**：Runner 参数 > Agent.run_processor > NoOpRunProcessor
4. **消息拦截层注入**：在父类 `run_async` 外包裹消息拦截层，支持内联媒体上传和运行后处理

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L355-L466](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L355-L466)

---

## 核心方法

### `run`

```python
async def run(
    self,
    messages: RunnerMessage,
    user_id: str = "",
    session_id: str = f"tmp-session-{formatted_timestamp()}",
    run_config: RunConfig | None = None,
    save_tracing_data: bool = False,
    upload_inline_data_to_tos: bool = False,
    run_processor: "BaseRunProcessor | None" = None,
) -> str
```

运行多轮文本和多模态输入的对话。这是最常用的入口方法。

#### 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `messages` | `RunnerMessage` | **必填** | 输入消息（`str`、`MediaMessage` 或它们的列表） |
| `user_id` | `str` | `""` | 覆盖默认用户 ID；若为空，使用构造时的 `user_id` |
| `session_id` | `str` | `f"tmp-session-{formatted_timestamp()}"` | 会话 ID，默认为基于时间戳的临时 ID |
| `run_config` | `RunConfig \| None` | `None` | 运行配置；若为 `None`，使用环境变量 `MODEL_AGENT_MAX_LLM_CALLS` 创建默认配置（默认 100） |
| `save_tracing_data` | `bool` | `False` | 运行后是否将追踪数据转储到磁盘 |
| `upload_inline_data_to_tos` | `bool` | `False` | 是否仅为此运行启用媒体上传（不改变 Runner 的全局设置） |
| `run_processor` | `BaseRunProcessor \| None` | `None` | 可选的运行处理器，用于此运行；若未提供，使用 Runner 的默认 run_processor |

#### 返回值

`str`：最后一个事件的文本输出，如果没有则返回空字符串。

#### 执行流程

1. 若 `upload_inline_data_to_tos=True`，临时启用媒体上传
2. 创建默认 `RunConfig`（若未提供），设置 `max_llm_calls`
3. 若 Agent 有 skills，初始化会话路径
4. 确定最终 user_id
5. 将输入消息转换为 ADK 消息格式（`_convert_messages`）
6. 若配置了短期记忆，自动创建会话
7. 遍历转换后的消息，逐条发送给 Agent：
   - 使用 `run_processor.process_run` 装饰器包装事件生成器
   - 遍历 `run_async` 产生的事件流
   - 提取最后一个非思考的文本部分作为最终输出
8. 捕获 `LlmCallsLimitExceededError` 超限异常
9. 若 `save_tracing_data=True`，保存追踪文件
10. 打印 Trace ID
11. 恢复媒体上传设置（如果临时修改过）
12. 返回最终输出文本

#### 异常

- `ValueError`：输入包含不支持或无法识别的媒体类型
- `AssertionError`：媒体 MIME 类型不在 `image/*` 或 `video/*` 中
- `Exception`：底层 ADK/Agent 执行可能抛出的异常

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L468-L576](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L468-L576)

---

### `run_async`（继承自 ADKRunner，被装饰器包装）

```python
async def run_async(
    self,
    *,
    user_id: str,
    session_id: str,
    new_message: types.Content,
    **kwargs,
) -> AsyncGenerator[Event, None]
```

> **注意**：此方法在 `__init__` 中被 `intercept_new_message` 装饰器包装，用于预处理消息和后处理事件流。通常用户应使用 `run()` 方法而非直接调用此方法。

被装饰后的 `run_async` 执行流程：
1. 调用 `pre_run_process` 预处理消息（上传内联媒体到 TOS）
2. 遍历底层事件流，聚合思考内容并批量记录日志
3. 对每个非 partial 事件：
   - 记录函数调用
   - 记录函数响应
   - 记录文本输出（区分思考内容和最终回答）
4. 刷新剩余的思考内容
5. 调用 `post_run_process`（当前为空操作）

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L107-L198](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L107-L198)（装饰器定义）

---

### `get_trace_id`

```python
def get_trace_id(self) -> str
```

获取当前 Agent 追踪器的 Trace ID。

#### 返回值

`str`：Trace ID；如果 Agent 不是 VeADK Agent 实例或未配置追踪器，返回 `"<unknown_trace_id>"`。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L578-L607](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L578-L607)

---

### `save_tracing_file`

```python
def save_tracing_file(self, session_id: str) -> str
```

将追踪数据转储到磁盘并返回最后写入的路径。

#### 参数说明

| 参数名 | 类型 | 说明 |
|--------|------|------|
| `session_id` | `str` | 用于关联追踪与会话的会话 ID |

#### 返回值

`str`：追踪文件路径；失败或无追踪器时返回空字符串。

#### 支持的 Agent 类型

仅当 Agent 是以下类型之一时有效：
- `Agent`
- `SequentialAgent`
- `ParallelAgent`
- `LoopAgent`

#### 使用示例

```python
import asyncio
from veadk import Agent, Runner

agent = Agent()
runner = Runner(agent=agent)

session_id = "session"
asyncio.run(runner.run(messages="Hi!", session_id=session_id))

path = runner.save_tracing_file(session_id=session_id)
print(path)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L640-L694](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L640-L694)

---

### `save_eval_set`

```python
async def save_eval_set(self, session_id: str, eval_set_id: str = "default") -> str
```

将当前会话保存为评估集的一部分并返回其路径。

#### 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `session_id` | `str` | **必填** | 会话 ID |
| `eval_set_id` | `str` | `"default"` | 评估集标识符 |

#### 返回值

`str`：导出的评估集文件路径。

#### 使用示例

```python
import asyncio
from veadk import Agent, Runner

agent = Agent()
runner = Runner(agent=agent)

session_id = "session"
asyncio.run(runner.run(messages="Hi!", session_id=session_id))

path = asyncio.run(runner.save_eval_set(session_id=session_id))
print(path)
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L696-L729](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L696-L729)

---

### `save_session_to_long_term_memory`

```python
async def save_session_to_long_term_memory(
    self,
    session_id: str,
    user_id: str = "",
    app_name: str = "",
    **kwargs,
) -> None
```

将指定会话保存到长期记忆。

#### 参数说明

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `session_id` | `str` | **必填** | 会话 ID |
| `user_id` | `str` | `""` | 可选，覆盖默认用户 ID；若为空，使用 `self.user_id` |
| `app_name` | `str` | `""` | 可选，覆盖默认应用名称；若为空，使用 `self.app_name` |

#### 说明

如果未配置 `long_term_memory`，函数记录警告并返回。它从会话服务获取会话，然后调用长期记忆的 `add_session_to_memory` 进行持久化。

#### 使用示例

```python
import asyncio
from veadk import Agent, Runner
from veadk.memory import LongTermMemory

APP_NAME = "app"

agent = Agent(long_term_memory=LongTermMemory(backend="local", app_name=APP_NAME))
runner = Runner(agent=agent, app_name=APP_NAME)

session_id = "session"
asyncio.run(runner.run(messages="Hi!", session_id=session_id))
asyncio.run(runner.save_session_to_long_term_memory(session_id=session_id))
```

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L731-L789](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L731-L789)

---

## Runner 工作机制

### 会话管理

1. **自动会话创建**：当配置了 `short_term_memory` 时，`run()` 方法会在需要时自动调用 `short_term_memory.create_session()` 创建会话
2. **会话持久化**：通过 `save_session_to_long_term_memory()` 可以将会话持久化到长期记忆
3. **会话标识**：通过 `app_name` + `user_id` + `session_id` 三元组唯一标识一个会话

### 事件流处理

`Runner` 采用异步生成器模式处理事件流：

```
用户输入 → 消息转换 → RunProcessor装饰器链 → run_async → 事件流 → 输出提取
                          ↓
                     媒体上传预处理
                          ↓
                     思考内容聚合日志
                          ↓
                     函数调用/响应日志
```

### 装饰器链执行流程

`RunProcessor` 装饰器链在 `run()` 方法中的执行位置：

```python
@(run_processor or self.run_processor).process_run(runner=self, message=converted_message)
async def event_generator():
    async for event in self.run_async(...):
        yield event

async for event in event_generator():
    # 处理最终输出
```

装饰器链的嵌套结构允许多个处理器按顺序执行（类似洋葱模型）：

1. 最外层：用户自定义的 RunProcessor
2. 中间层：Runner 内置的 intercept_new_message 装饰器（媒体上传 + 日志）
3. 最内层：ADKRunner.run_async 实际执行

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L541-L562](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L541-L562)

---

## 模块级辅助函数

### `intercept_new_message`

```python
def intercept_new_message(process_func) -> Callable
```

创建装饰器，在 `run_async` 调用前后插入前置/后置钩子。这是 Runner 内部使用的装饰器工厂。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L107-L198](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L107-L198)

### `_convert_messages`

```python
def _convert_messages(
    messages: RunnerMessage,
    app_name: str,
    user_id: str,
    session_id: str,
) -> list
```

将 VeADK `RunnerMessage` 转换为 Google ADK 消息列表。支持文本和多模态输入转换。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L201-L277](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L201-L277)

---

## 完整使用示例

### 基础对话示例

```python
import asyncio
from veadk import Agent, Runner

async def main():
    agent = Agent(
        name="assistant",
        instruction="You are a helpful assistant.",
    )

    runner = Runner(agent=agent, app_name="my-app")

    # 单轮对话
    answer = await runner.run(
        messages="你好，请介绍一下自己。",
        session_id="session-001",
    )
    print(f"Answer: {answer}")

    # 多轮对话（同一个 session_id 保持上下文）
    answer2 = await runner.run(
        messages="我刚才问了你什么问题？",
        session_id="session-001",  # 同一个 session_id
    )
    print(f"Answer 2: {answer2}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 多模态输入示例（图片）

```python
import asyncio
from veadk import Agent, Runner
from veadk.types import MediaMessage

async def main():
    agent = Agent(
        name="vision-assistant",
        instruction="You are a vision assistant. Describe images in detail.",
    )

    runner = Runner(
        agent=agent,
        app_name="vision-app",
        upload_inline_data_to_tos=True,  # 启用媒体上传
    )

    message = MediaMessage(
        text="请描述这张图片。",
        media="./path/to/image.jpg",
    )

    answer = await runner.run(
        messages=message,
        session_id="vision-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

### 带短期记忆和追踪示例

```python
import asyncio
from veadk import Agent, Runner
from veadk.memory import ShortTermMemory

async def main():
    # 启用 OpenTelemetry 追踪（通过环境变量）
    import os
    os.environ["ENABLE_APMPLUS"] = "true"

    agent = Agent(
        name="memory-agent",
        instruction="You are a helpful assistant with memory.",
    )

    # 使用 SQLite 短期记忆
    stm = ShortTermMemory(backend="sqlite", db_path="./sessions.db")

    runner = Runner(
        agent=agent,
        short_term_memory=stm,
        app_name="memory-app",
    )

    session_id = "persistent-session"

    # 第一轮
    await runner.run(
        messages="记住：我的名字是张三，我喜欢Python编程。",
        session_id=session_id,
    )

    # 第二轮（同一会话，能记住上文）
    answer = await runner.run(
        messages="我叫什么名字？我喜欢什么编程语言？",
        session_id=session_id,
        save_tracing_data=True,
    )
    print(answer)

    # 获取 Trace ID
    trace_id = runner.get_trace_id()
    print(f"Trace ID: {trace_id}")

    # 保存追踪文件
    trace_path = runner.save_tracing_file(session_id)
    print(f"Tracing saved to: {trace_path}")

if __name__ == "__main__":
    asyncio.run(main())
```

### 多轮消息列表示例

```python
import asyncio
from veadk import Agent, Runner

async def main():
    agent = Agent(instruction="You are a helpful assistant.")
    runner = Runner(agent=agent, app_name="multi-turn")

    # 一次性发送多轮历史消息
    messages = [
        "你好，我是李四。",
        "我是一名软件工程师。",
        "请问我叫什么名字？我的职业是什么？",
    ]

    answer = await runner.run(
        messages=messages,
        session_id="multi-turn-session",
    )
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```
