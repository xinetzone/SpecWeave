# CozeLoop Python SDK - 架构洞察

> 基于 Phase R 事实提取的分析，日期：2026-08-23

## 洞察 1：基于 ContextVar + 双向链表的隐式上下文传播模型

CozeLoop 的 tracing 核心是一个**隐式上下文栈**模型，不同于 OpenTelemetry 显式传递 Context 的方式。内部使用 `contextvars.ContextVar('loop_span')` 存储一个**双向链表**（DoublyLinkedList），每次 `start_span()` 将新 Span 追加到链表尾部作为"当前 span"，`finish()` 时从链表中删除。

**关键设计决策：**
- `start_span()` 自动从 context 获取链尾 span 作为父 span，无需开发者手动传递 parent。
- 双向链表而非单纯栈结构，支持中间 span 提前 finish（非 LIFO 顺序）时正确维护上下文。
- 跨线程场景通过 `child_of=SpanContext` 参数显式传递上下文（如 parent_child.py 示例中的 threading 用法）。
- 跨服务传播通过 `to_header()`/`from_header()` 序列化为 HTTP header（X-Cozeloop-Traceparent + X-Cozeloop-Tracestate），格式受 W3C Trace Context 启发但使用自定义前缀避免冲突。

**对开发者的影响：** 在同步/异步代码中，嵌套 `start_span()` 自动建立父子关系，开发者无需手动管理 span 引用，极大简化了手动埋点的复杂度。但跨线程时必须显式传递 SpanContext。

## 洞察 2：三层集成模式——装饰器、Monkey-Patch、Callback Handler

CozeLoop 提供三种递进式 LLM 集成模式，覆盖从简单到复杂的使用场景：

1. **@observe 装饰器（通用函数追踪）**：最基础的集成方式，自动检测同步/异步/生成器/异步生成器四种函数类型，分别生成对应 wrapper。支持 process_inputs/process_outputs/process_iterator_outputs 钩子来自定义输入输出处理。对于流式返回，包装为 `_CozeLoopTraceStream`/`_CozeLoopAsyncTraceStream`，在迭代过程中收集所有 chunk，迭代结束时聚合并上报 span，同时为 model 类型 span 自动记录首包延迟（TTFT）。

2. **openai_wrapper（Monkey-Patch 自动埋点）**：通过 `openai_wrapper(client)` 直接替换 OpenAI 客户端的 `chat.completions.create` 和 `responses.create` 方法。内部用 @observe 装饰器包装原方法，自动提取 model_provider、model_name、call_options（temperature/max_tokens/stop/top_p 等），自动聚合流式 chunk 重建完整响应并提取 token 用量。支持 OpenAI/AsyncOpenAI/AzureOpenAI/AsyncAzureOpenAI 四种客户端。这是"零侵入"集成——只需一行代码包装现有 OpenAI 客户端。

3. **LoopTracer Callback Handler（LangChain/LangGraph 集成）**：实现 LangChain 的 `BaseCallbackHandler` 接口，通过 callbacks 参数注入 LCEL 链。为每个 LangChain run_id 创建对应 span，自动映射 span_type（model/chain/tool/prompt/graph/parser），自动从 LLMResult 提取 token 用量，支持 modify_name_fn/add_tags_fn 自定义。支持 state_span_ctx_key 在 LangGraph state 中传递 span context 供异步节点使用。还提供 `@to_runnable` 装饰器将普通函数包装为 RunnableLambda 参与 LangChain 链追踪。

**关键设计决策：** 三种模式不是互斥的，而是可以叠加——@observe 是基础，openai_wrapper 基于 @observe，LoopTracer 直接调用 client.start_span()。

## 洞察 3：四队列批量上报引擎与大文件分离策略

Span 上报采用**四队列两级重试**架构，由 `BatchSpanProcessor` 管理：

```
┌─────────────┐     失败重试    ┌──────────────────┐
│  span 队列   │ ──────────────→ │ span 重试队列     │
│  (1024/批)   │                 │ (512/批, 50条/批) │
└──────┬──────┘                  └────────┬─────────┘
       │ 成功，含大文件                   │ 二次失败→丢弃
       ↓                                  │
┌─────────────┐     失败重试    ┌──────────────────┐
│  file 队列   │ ──────────────→ │ file 重试队列     │
│  (512/批)    │                 │ (512/批, 1条/批)  │
└─────────────┘                  └─────────────────┘
```

- Span 队列每 1 秒或攒满 100 条/4MB 触发上报；File 队列每 5 秒或单文件达 100MB 触发。
- 每个队列运行在独立 daemon 线程中，使用 Condition 变量等待/唤醒。
- 大文本/多模态数据与 span 数据分离：当 `ultra_large_report=True` 时，超过 1MB 的 input/output 截断到 1000 字符，完整数据通过文件接口上传；base64 编码的图片/文件自动提取为独立附件上传，span 中只存储对象存储 key（ObjectStorage）。
- Tag 值按 JSON 类型自动分类为 string/long/double/bool 四组上报，预定义保留字段（user_id/message_id/thread_id/input_tokens 等）有类型校验。

## 洞察 4：接口-实现分离的 ABC 抽象与 Noop 降级模式

SDK 采用严格的**抽象基类（ABC）→ 具体实现**分离模式：

- 公开 API 全部定义为 ABC：`Client`(ABC)、`Span`(ABC)、`SpanContext`(ABC)、`TraceClient`(ABC)、`PromptClient`(ABC)、`CommonSpanSetter`(ABC)、`Auth`(ABC)、`SpanProcessor`(ABC)、`QueueManager`(ABC)、`Exporter`(ABC)。
- 具体实现类全部位于 `internal/` 包下，不作为公共 API 导出：`_LoopClient`、内部 `Span`（internal/trace/span.py）、`TokenAuth`/`JWTAuth`、`BatchSpanProcessor`、`SpanExporter`、`BatchQueueManager`。
- **Noop 降级模式**贯穿全局：`NoopSpan` 实现所有 Span 接口但方法为空操作；`_NoopClient` 在初始化失败或客户端关闭后返回 NoopSpan 并记录 warning。这确保即使 tracing 系统故障也不会影响业务逻辑——start_span() 异常时返回 NOOP_SPAN 而非抛出异常。
- 客户端缓存：相同参数的 new_client() 返回缓存实例，避免重复创建；全局默认客户端通过 `get_default_client()` 懒初始化，首次调用模块级函数（如 `cozeloop.start_span()`）时自动创建，无需显式初始化。

## 洞察 5：双功能 Client——Tracing + Prompt Hub/PTaaS

`Client` 同时承担两个相对独立的功能域：

1. **Tracing/Observability**（TraceClient）：span 创建、上下文管理、批量上报——这是 SDK 的核心功能。
2. **Prompt Hub & PTaaS**（PromptClient）：`get_prompt()` 从 Prompt Hub 获取提示词模板、`prompt_format()` 使用 Jinja2 渲染模板变量、`execute_prompt()`/`aexecute_prompt()` 直接调用远端 LLM 执行（Prompt as a Service），支持流式和非流式。

Prompt 功能自带本地 LRU 缓存（基于 cachetools）、定时刷新（基于 APScheduler），且支持 `prompt_trace=True` 在获取/格式化 prompt 时自动创建 trace span。

两个功能共享同一个 HTTP 客户端和认证体系，但内部通过 `TraceProvider` 和 `PromptProvider` 分离。PromptProvider 持有 TraceProvider 引用以便在 prompt 操作时创建 trace span。

**关键设计决策：** SDK 的 tracing 部分是自主的——不依赖 OpenTelemetry，实现了自己的 span 模型、上下文传播和上报协议。这使得 SDK 零外部依赖（除 httpx/pydantic 等基础库）即可工作，但也意味着它不直接兼容 OpenTelemetry 生态系统（cozeloop-examples 中其他框架的集成通过 OTel/OpenInference bridge 实现，不在 SDK 核心内）。
