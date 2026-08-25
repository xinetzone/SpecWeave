---
type: Concept
title: Runner 运行器
description: Runner 类的 run 方法、消息拦截装饰器、多模态消息转换、Tracing 保存与会话管理机制
tags: [veadk, runner, async, multimodal, tracing, session]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# Runner 运行器

`Runner` 是 veadk-python 中驱动 Agent 执行的运行时编排核心，定义于 `veadk/runner.py`，继承自 Google ADK 的 `Runner`（`ADKRunner`）[F-065]。它负责消息格式转换、会话管理、消息拦截、多模态处理、Tracing 数据收集，以及通过 `run_processor` 实现横切关注点。用户通过 `Runner(agent=agent).run(messages=...)` 与 Agent 交互。

## 类定义与构造函数

```python
class Runner(ADKRunner):
```

### __init__ 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `agent` | `BaseAgent \| Agent \| None` | `None` | 要运行的 Agent |
| `short_term_memory` | `ShortTermMemory \| None` | `None` | 短期记忆，覆盖 Agent 自带的 |
| `app_name` | `str \| None` | `None` | 应用名，默认 `"veadk_default_app"` |
| `user_id` | `str` | `"veadk_default_user"` | 用户 ID |
| `upload_inline_data_to_tos` | `bool` | `False` | 是否将内联媒体上传到 TOS |
| `run_processor` | `BaseRunProcessor \| None` | `None` | 运行处理器 |
| `*args, **kwargs` | | | 传入 ADK Runner（`session_service`、`memory_service`、`credential_service`） |

来源：[F-067]

### 初始化逻辑

Runner 在 `__init__` 中完成以下装配 [F-068]：

1. **run_processor 优先级**：Runner 参数 > `agent.run_processor` > `NoOpRunProcessor`
2. **短期记忆解析**：无显式传入时从 `agent.short_term_memory` 获取；均无则创建内存版 `ShortTermMemory`
3. **长期记忆解析**：无 `memory_service` 时从 `agent.long_term_memory` 获取
4. **app_name 默认值**：`"veadk_default_app"`
5. **方法绑定**：使用 `MethodType` 将 `intercept_new_message(_upload_image_to_tos)(super().run_async)` 绑定为实例方法。这是一种猴子补丁——在实例级别替换父类的 `run_async` 方法，使其经过消息拦截装饰器

## RunnerMessage 类型

Runner 接受多种消息格式，通过类型别名 `RunnerMessage` 统一定义 [F-066]：

```python
RunnerMessage = Union[
    str,                        # 单轮文本
    list[str],                  # 多轮文本
    MediaMessage,               # 单轮多模态
    list[MediaMessage],         # 多轮多模态
    list[MediaMessage | str],   # 混合
]
```

这意味着 `run()` 方法可以接受纯文本、多模态消息或它们的列表，Runner 内部统一转换为 ADK 的 Content 格式。

## run 方法

`run` 是高层异步方法，返回最终文本答案 [F-069]：

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

### 执行流程

1. **RunConfig**：默认 `RunConfig(max_llm_calls=int(getenv("MODEL_AGENT_MAX_LLM_CALLS", 100)))` [F-070]
2. **消息转换**：通过 `_convert_messages` 将输入消息转为 ADK Content 列表
3. **会话管理**：若 short_term_memory 存在，自动创建或获取会话
4. **处理器包装**：通过 run_processor 的 `process_run` 装饰器包装事件生成器
5. **事件遍历**：遍历 Agent 产出的事件流，提取最后一条非 thought 的文本作为 `final_output`
6. **限制捕获**：捕获 `LlmCallsLimitExceededError`（超过最大 LLM 调用次数）
7. **Tracing 保存**：`save_tracing_data=True` 时保存追踪文件

返回值是字符串类型的最终文本回答。

## 消息拦截：intercept_new_message

`intercept_new_message` 是一个装饰器工厂，包装 ADK Runner 的 `run_async` 方法 [F-072]：

```python
def intercept_new_message(process_func):
```

在 Agent 执行前后插入处理逻辑：

- **pre_run_process**：在 `run_async` 前调用，处理 inline_data（如将 base64 图片上传到 TOS）
- **流式遍历**：遍历事件生成器，累积 thought 部分并批量日志记录
- **日志记录**：记录 function call、function response、文本输出
- **post_run_process**：结束后调用（当前为空操作）

这个装饰器通过 `MethodType` 绑定到 Runner 实例，使得每次 `run_async` 调用都经过拦截逻辑。

## 消息转换：_convert_messages

```python
def _convert_messages(messages, app_name, user_id, session_id) -> list
```

该函数将 `RunnerMessage` 转换为 ADK 的 Content 列表 [F-073]：

- **str 输入**：包装为单条 user Content
- **MediaMessage 输入**：转换为多模态 Content
- **list 输入**：逐项转换，保持顺序
- **MIME 检测**：使用 `filetype` 库检测媒体 MIME 类型，仅支持 `image/*` 和 `video/*`

## 其他核心方法

| 方法 | 说明 |
|------|------|
| `get_trace_id() -> str` | 从 `agent.tracers[0].trace_id` 获取当前追踪 ID [F-071] |
| `save_tracing_file(session_id: str) -> str` | 保存 Tracing 数据到文件，仅支持 Agent/SequentialAgent/ParallelAgent/LoopAgent [F-071] |
| `async save_eval_set(session_id: str, eval_set_id: str = "default") -> str` | 将会话保存为评估集 [F-071] |
| `async save_session_to_long_term_memory(session_id, user_id="", app_name="") -> None` | 手动保存会话到长期记忆 [F-071] |

## 多模态支持

Runner 通过 `MediaMessage` 类型支持图像和视频输入。当 `upload_inline_data_to_tos=True` 时，拦截器会在 Agent 执行前将内联媒体数据上传到火山引擎 TOS 对象存储，替换为 TOS URI 后再传给 LLM。这避免了将大量 base64 数据直接发送给模型 API。

多模态媒体的管理通过 `veadk/multimodal/` 模块实现：`MediaRef` 使用 `veadk-media://` URI scheme 标识媒体资源，`MediaRecord` 记录文件元数据（文件名、MIME、大小、SHA256），`mount_media_routes` 为 FastAPI 挂载媒体上传/下载/删除端点 [F-116~F-118]。

## Tracing 与可观测性

Runner 与 Agent 的 tracers 协作，收集完整的执行追踪：

- Tracing 数据包含 LLM 请求/响应、工具调用、Agent 转移等事件
- 通过 `save_tracing_file` 可导出为 JSON 文件，供评估系统使用
- 支持三个 exporter：APMPlus、CozeLoop、TLS，通过环境变量启用
- `save_eval_set` 可将 tracing 数据转化为评估测试用例

## run_processor 横切关注点

`BaseRunProcessor` 提供了 `process_run` 装饰器和 `pre_run_process`/`post_run_process` 钩子，用于实现：

- OAuth2 认证流程（如 `AuthRequestProcessor`）
- 请求/响应日志
- 错误处理与重试
- 性能监控

Runner 构造时按优先级选择 run_processor，也可在 `run()` 调用时临时传入覆盖。

## 基本用法

```python
import asyncio
from veadk import Agent, Runner

async def main():
    agent = Agent(
        name="my_agent",
        instruction="You are a helpful assistant.",
    )
    runner = Runner(agent=agent, app_name="my_app")
    answer = await runner.run(
        messages="你好，请介绍一下火山引擎。",
        session_id="session-001",
    )
    print(answer)

asyncio.run(main())
```

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [Agent 类型体系](/concepts/03-agent-types.md)
- [记忆系统](/concepts/06-memory-system.md)
- [评估系统](/concepts/09-evaluation.md)
- [高级特性](/concepts/11-advanced.md)
