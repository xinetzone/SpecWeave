# CozeLoop Python SDK - 事实提取

> 来源：`d:/spaces/SpecWeave/external/libs/ai/coze-dev/cozeloop-python/`
> 版本：pyproject.toml 中声明 0.1.28，internal/version.py 中 VERSION = 'v0.1.27'
> 提取日期：2026-08-23

## 包元数据与依赖

- F-cl-001: 包名（PyPI）为 `cozeloop`，在 pyproject.toml 的 `[tool.poetry].name` 中声明。
- F-cl-002: pyproject.toml 版本号为 `0.1.28`，但 internal/version.py 中 VERSION 常量为 `'v0.1.27'`（运行时上报版本为 v0.1.27）。
- F-cl-003: Python 版本要求 `>=3.8,<4.0`。
- F-cl-004: 核心运行时依赖：httpx (>=0.23.0,<1.0.0)、pydantic (>=1.10.12,<3.0.0)、cachetools (>=5.5.2,<7.0.0)、apscheduler (^3.11.0)、jinja2 (^3.1.6)、authlib (^1.2.0)。
- F-cl-005: 许可证为 MIT。
- F-cl-006: 构建系统使用 poetry-core。

## 公共 API 导出（cozeloop/__init__.py）

- F-cl-007: 顶层导出的类：`Client`（抽象基类）、`Span`、`SpanContext`、`Prompt`、`Message`。
- F-cl-008: 顶层导出的工厂函数：`new_client()` 创建客户端实例。
- F-cl-009: 顶层导出的默认客户端函数：`set_default_client()`、`close()`、`workspace_id()`、`flush()`。
- F-cl-010: 顶层导出的 Tracing 模块级函数：`start_span()`、`get_span_from_context()`、`get_span_from_header()`。
- F-cl-011: 顶层导出的 Prompt 相关函数：`get_prompt()`、`prompt_format()`、`execute_prompt()`、`aexecute_prompt()`（异步版本）。
- F-cl-012: 顶层导出的日志函数：`set_log_level()`、`add_log_handler()`。
- F-cl-013: 顶层导出的常量：`CN_BASE_URL`（值为 `"https://api.coze.cn"`）。
- F-cl-014: 顶层导出的环境变量常量：`ENV_API_BASE_URL`、`ENV_WORKSPACE_ID`、`ENV_API_TOKEN`、`ENV_JWT_OAUTH_CLIENT_ID`、`ENV_JWT_OAUTH_PRIVATE_KEY`、`ENV_JWT_OAUTH_PUBLIC_KEY_ID`。
- F-cl-015: 所有 error 模块中的异常类通过 `from .internal.consts.error import *` 通配导出。

## 客户端架构

- F-cl-016: `Client` 是抽象基类（ABC），继承自 `PromptClient` 和 `TraceClient`，声明为线程安全，文档建议不要创建多个实例。
- F-cl-017: `Client` 抽象属性 `workspace_id` 返回工作空间 ID；抽象方法 `close()` 关闭客户端。
- F-cl-018: `TraceClient` 是抽象基类，定义 `start_span()`、`get_span_from_context()`、`get_span_from_header()`、`flush()` 四个抽象方法。
- F-cl-019: `PromptClient` 是抽象基类，定义 `get_prompt()`、`prompt_format()`、`execute_prompt()`、`aexecute_prompt()` 四个抽象方法。
- F-cl-020: `_LoopClient` 是 `Client` 的具体实现，内部组合 `TraceProvider` 和 `PromptProvider`。
- F-cl-021: `_NoopClient` 是 Client 的空实现，所有方法记录 warning 并返回 NOOP_SPAN 或抛出异常，在客户端初始化失败或已关闭时使用。
- F-cl-022: 客户端使用缓存机制（`_client_cache` 字典 + MD5 缓存键），相同参数重复调用 `new_client()` 返回缓存实例。
- F-cl-023: 首次成功创建客户端时自动注册 `atexit` 钩子执行优雅关闭（`_graceful_shutdown`）。
- F-cl-024: 客户端实现了默认 header 注入器，自动从当前 context 中的 span 获取 `to_header()` 结果注入 HTTP 请求头。

## 认证体系

- F-cl-025: 支持两种认证方式：PAT Token（`TokenAuth`）和 JWT OAuth（`JWTAuth`）。
- F-cl-026: `TokenAuth` 使用固定的 API Token，构造时传入 token 字符串。
- F-cl-027: `JWTAuth` 使用 JWT OAuth 流程，需要 `client_id`、`private_key`、`public_key_id` 三个参数，通过 `JWTOAuthApp` 自动获取和刷新 access token。
- F-cl-028: JWT Token 默认 TTL 为 900 秒（DEFAULT_OAUTH_REFRESH_TTL），提前 60 秒（OAUTH_REFRESH_ADVANCE_TIME）刷新。
- F-cl-029: 认证优先级：如果提供了 JWT OAuth 参数则使用 JWTAuth，否则如果提供了 api_token 则使用 TokenAuth，都没有则抛出 AuthInfoRequiredError。
- F-cl-030: HTTP 请求通过 `Authorization: Bearer <token>` 头传递认证信息。

## Tracing 模型

- F-cl-031: `SpanContext` 抽象接口包含三个属性：`span_id`（str）、`trace_id`（str）、`baggage`（Dict[str, str]）。
- F-cl-032: `CommonSpanSetter` 抽象接口定义了系统预定义字段的 setter 方法：`set_input`、`set_output`、`set_error`、`set_status_code`、`set_user_id`、`set_user_id_baggage`、`set_message_id`、`set_message_id_baggage`、`set_thread_id`、`set_thread_id_baggage`、`set_prompt`、`set_model_provider`、`set_model_name`、`set_model_call_options`、`set_input_tokens`、`set_output_tokens`、`set_start_time_first_resp`、`set_runtime`、`set_service_name`、`set_log_id`、`set_system_tags`、`set_deployment_env`、`set_finish_time`。
- F-cl-033: `Span` 抽象接口继承 `CommonSpanSetter` 和 `SpanContext`，额外定义 `set_tags()`、`set_baggage()`、`finish()`、`discard()`、`start_time` 属性、`to_header()`、上下文管理器协议（`__enter__`/`__exit__`）。
- F-cl-034: 内部 `Span` 实现类（cozeloop/internal/trace/span.py）使用 pydantic BaseModel 不，是普通 Python 类，包含 span_type、name、space_id、trace_id、span_id、parent_span_id、start_time、finish_time、duration、tag_map、system_tag_map、status_code 等字段。
- F-cl-035: Span ID 由 `gen_16char_id()` 生成 16 字符十六进制字符串；Trace ID 由 `gen_32char_id()` 生成 32 字符十六进制字符串。
- F-cl-036: 根 span 的 parent_span_id 为 `"0"`。
- F-cl-037: Span 完成（`finish()`）时自动计算 duration（微秒）、自动汇总 tokens（input_tokens + output_tokens）、自动计算 latency_first_resp、设置 runtime 系统标签（含 SDK 版本、语言=python）。
- F-cl-038: `discard()` 方法将 span 从上下文中移除但不报告。
- F-cl-039: `NoopSpan` 是 Span 的空实现，所有方法为空操作，在客户端关闭或创建 span 失败时返回。
- F-cl-040: Span 支持 `with` 语句（上下文管理器），退出时自动调用 `finish()`。
- F-cl-041: 默认 status_code 为 0（成功），错误时通过 `set_error()` 设置 error 标签会自动将 status_code 设为 -1（STATUS_CODE_ERROR_DEFAULT）。
- F-cl-042: 单个 Span 最多支持 50 个 tag 键值对（MAX_TAG_KV_COUNT_IN_ONE_SPAN）。
- F-cl-043: 单个 tag value 默认最大 1024 字节（MAX_BYTES_OF_ONE_TAG_VALUE_DEFAULT），input/output 字段默认最大 1MB（MAX_BYTES_OF_ONE_TAG_VALUE_OF_INPUT_OUTPUT）。
- F-cl-044: Tag 值按类型分为四类上报：tags_string（字符串）、tags_long（整数）、tags_double（浮点数）、tags_bool（布尔值）。
- F-cl-045: flags 字段默认为 1，表示默认采样。

## 上下文传播

- F-cl-046: Span 上下文使用 Python `contextvars.ContextVar`（变量名 `loop_span`）管理，内部维护一个双向链表（`DoublyLinkedList`）支持嵌套 span。
- F-cl-047: `set_span_to_context()` 将新 span 追加到链表尾部；`get_newest_span_from_context()` 获取链表尾部（最新的）span；`delete_span_in_context()` 从链表中删除指定 span。
- F-cl-048: `start_span()` 时自动从 context 获取当前 span 作为父 span（除非指定 `child_of` 或 `start_new_trace=True`），新 span 自动写入 context。
- F-cl-049: 跨进程/跨服务传播使用 HTTP header：`X-Cozeloop-Traceparent`（格式 `{version:02x}-{trace_id}-{span_id}-{flags:02x}`）和 `X-Cozeloop-Tracestate`（baggage 的 URL 编码逗号分隔 k=v 对）。
- F-cl-050: `to_header()` 方法返回包含这两个 header 的字典；`from_header()` / `get_span_from_header()` 从 header 字典解析出 SpanContext。
- F-cl-051: Baggage 通过 `set_baggage()` 设置后自动传递给子 span；通过 `set_user_id_baggage()`/`set_message_id_baggage()`/`set_thread_id_baggage()` 设置的 baggage 同时设置对应 tag。
- F-cl-052: Baggage 的 key 不能包含 `=` 和 `,` 特殊字符（BAGGAGE_SPECIAL_CHARS）。

## TraceProvider 与批量上报

- F-cl-053: `TraceProvider` 是 tracing 核心提供者，内部持有 `BatchSpanProcessor`。
- F-cl-054: `BatchSpanProcessor` 管理四个队列：span 主队列、span 重试队列、file 主队列、file 重试队列，每个队列由独立的 `BatchQueueManager` + 后台 daemon 线程管理。
- F-cl-055: Span 队列默认最大长度 1024（DEFAULT_MAX_QUEUE_LENGTH），重试队列 512；批量上报默认每 1000ms（DEFAULT_SCHEDULE_DELAY）或攒满 100 条（DEFAULT_MAX_EXPORT_BATCH_LENGTH）或达到 4MB 触发。
- F-cl-056: File 队列用于上传大文本/多模态数据，默认最大长度 512，每 5000ms（FILE_SCHEDULE_DELAY）上报，单批 1 个文件，最大 100MB。
- F-cl-057: Span 上报路径默认为 `/v1/loop/traces/ingest`（PATH_INGEST_TRACE），文件上传路径为 `/v1/loop/files/upload`（PATH_UPLOAD_FILE）。
- F-cl-058: 上报失败的 span 进入重试队列，重试队列导出失败则丢弃；文件上报失败同理。
- F-cl-059: `flush()` 方法强制排空所有队列并上报（阻塞等待）；`close()`/`shutdown()` 设置停止事件、等待 worker 线程结束并排空队列。
- F-cl-060: `start_new_trace=True` 参数强制创建新 trace（不继承 context 中的父 span）。
- F-cl-061: `child_of` 参数允许显式指定父 SpanContext，用于跨线程/跨服务场景。

## 数据模型（spec/tracespec）

- F-cl-062: `ModelInput` 包含 messages（List[ModelMessage]）、tools（List[ModelTool]）、tool_choice（ModelToolChoice）。
- F-cl-063: `ModelOutput` 包含 choices（List[ModelChoice]），每个 choice 有 finish_reason、index、message。
- F-cl-064: `ModelMessage` 包含 role、content、reasoning_content、parts（多模态）、name、tool_calls、tool_call_id、metadata。
- F-cl-065: `ModelMessagePart` 支持三种类型：text（ModelMessagePartType.TEXT）、image_url（IMAGE）、file_url（FILE），以及内部使用的 multi_part_variable。
- F-cl-066: `ModelCallOption` 包含 temperature、max_tokens、stop、top_p、n、top_k、presence_penalty、frequency_penalty、reasoning_effort。
- F-cl-067: `Runtime` 系统标签包含 language、library、scene、library_version、loop_sdk_version、extra 字段。
- F-cl-068: 预定义 span_type 值：prompt、model、retriever、tool、chain、graph、custom 等。
- F-cl-069: 预定义角色值：user、system、assistant、tool。
- F-cl-070: 预定义场景值：custom、prompt_hub、prompt_template、integration。
- F-cl-071: 多模态数据（base64 编码的图片/文件）和超大型文本（>1MB 且 ultra_large_report=True）通过单独的文件上传接口上传，span 中只存储对象存储 key（ObjectStorage）。

## HTTP 客户端层

- F-cl-072: HTTP 层封装在 `internal/httpclient/` 中，底层使用 httpx 同步客户端。
- F-cl-073: `httpclient.Client` 类提供 `get()`、`post()`、`upload_file()`、`post_stream()`、`arequest()`、`apost_stream()` 方法。
- F-cl-074: 默认请求超时 3 秒（DEFAULT_TIMEOUT），上传超时 30 秒（DEFAULT_UPLOAD_TIMEOUT），Prompt 执行默认超时 600 秒。
- F-cl-075: 响应统一解析为 `BaseResponse`（含 code 和 msg 字段），code != 0 抛出 RemoteServiceError。
- F-cl-076: 支持通过环境变量 `x_tt_env` 和 `x_use_ppe` 设置特殊请求头（用于内部环境路由）。
- F-cl-077: User-Agent 头由 `user_agent_header()` 生成。

## 装饰器（@observe）

- F-cl-078: `cozeloop.decorator` 模块导出 `observe` 装饰器和 `to_runnable` 装饰器（从单例 `coze_loop_decorator` 获取）。
- F-cl-079: `@observe` 装饰器支持参数：name（span 名，默认函数名）、span_type（默认 'custom'）、tags（静态标签）、baggage（静态 baggage）、client（指定客户端）、process_inputs、process_outputs、process_iterator_outputs。
- F-cl-080: `@observe` 自动检测函数类型：同步函数、异步函数（async def）、生成器函数、异步生成器函数，并分别使用对应的 wrapper。
- F-cl-081: 对于流式迭代器（指定了 process_iterator_outputs），装饰器返回 `_CozeLoopTraceStream`（同步）或 `_CozeLoopAsyncTraceStream`（异步）包装器，在迭代结束时自动上报 span 并记录首包延迟（span_type 为 "model" 时）。
- F-cl-082: `@to_runnable` 装饰器将普通函数包装为 LangChain RunnableLambda，需要调用时传入 RunnableConfig 参数。
- F-cl-083: 装饰器在异常时自动调用 `span.set_error(e)` 并重新抛出异常；finally 块中设置 input、tags 并调用 `span.finish()`。

## 框架集成

- F-cl-084: OpenAI 集成通过 `cozeloop.integration.wrapper.openai_wrapper(client, chat_name="ChatOpenAI")` 函数实现，它 monkey-patch `client.chat.completions.create` 和 `client.responses.create` 方法。
- F-cl-085: openai_wrapper 支持 OpenAI、AsyncOpenAI、AzureOpenAI、AsyncAzureOpenAI 四种客户端类型；Azure 客户端 model_provider 自动设为 "azure"。
- F-cl-086: openai_wrapper 内部使用 @observe 装饰器包装原始 create 方法，span_type 为 "model"，自动提取 model_provider、model_name、call_options（temperature、max_tokens、stop、top_p、n、frequency_penalty、presence_penalty）、stream 标签。
- F-cl-087: openai_wrapper 支持流式输出（stream=True），通过 process_iterator_outputs 聚合所有 chunk 重建完整响应，自动从 usage 字段提取 token 数。
- F-cl-088: openai_wrapper 支持 OpenAI Responses API（`client.responses.create`）的流式和非流式调用。
- F-cl-089: LangChain 集成通过 `LoopTracer.get_callback_handler()` 获取 `LoopTraceCallbackHandler`（继承自 langchain_core 的 `BaseCallbackHandler`），作为 callback 传入 LangChain LCEL 链。
- F-cl-090: LoopTraceCallbackHandler 实现了 on_llm_start、on_chat_model_start、on_llm_new_token、on_llm_end、on_llm_error、on_chain_start、on_chain_end、on_chain_error、on_tool_start、on_tool_end、on_tool_error 等回调方法。
- F-cl-091: LoopTraceCallbackHandler 为每个 LangChain run_id 创建一个 span，通过 run_map 字典维护 run_id → Run（含 span 和 span_type）的映射，根据 parent_run_id 构建父子关系。
- F-cl-092: LangChain 回调自动将 span_type 映射：ChatPromptTemplate → prompt、model/AzureChatOpenAI → model、ReActSingleInputOutputParser → parser、tool → tool、LangGraph → graph。
- F-cl-093: LoopTracer.get_callback_handler() 支持参数：client、modify_name_fn（自定义 span 名）、add_tags_fn（自定义标签）、tags（全局标签）、child_of（父 span）、state_span_ctx_key（在 LangGraph state 中传递 span context）。
- F-cl-094: 没有内置 LlamaIndex、AutoGen、CrewAI 等框架的直接集成代码（这些在 cozeloop-examples 中以 OpenInference/OTel 方式提供示例，而非 SDK 内置）。

## Prompt 功能

- F-cl-095: `get_prompt(prompt_key, version='', label='')` 从 Prompt Hub 获取 Prompt，返回 Optional[Prompt]。
- F-cl-096: `prompt_format(prompt, variables)` 使用 Jinja2 模板引擎格式化 prompt，返回 List[Message]。
- F-cl-097: `execute_prompt()` 和 `aexecute_prompt()` 执行 PTaaS（Prompt as a Service），支持同步/异步、流式/非流式，返回 ExecuteResult 或 StreamReader[ExecuteResult]。
- F-cl-098: Prompt 实体包含 workspace_id、prompt_key、version、prompt_template（含 template_type[NORMAL/JINJA2]、messages、variable_defs）、tools、tool_call_config、llm_config。
- F-cl-099: Prompt 缓存默认最大 100 条（DEFAULT_PROMPT_CACHE_MAX_COUNT），默认刷新间隔 60 秒（DEFAULT_PROMPT_CACHE_REFRESH_INTERVAL，注意文档示例中写的是 10 分钟）。
- F-cl-100: Prompt 相关类型：TemplateType（NORMAL/JINJA2）、Role（SYSTEM/USER/ASSISTANT/TOOL/PLACEHOLDER）、ContentType（TEXT/IMAGE_URL/BASE64_DATA/MULTI_PART_VARIABLE）、VariableType（STRING/PLACEHOLDER/BOOLEAN/INTEGER/FLOAT/OBJECT/ARRAY_*/MULTI_PART）。

## 配置与环境变量

- F-cl-101: 环境变量 `COZELOOP_API_BASE_URL` 对应 api_base_url 参数，默认 CN_BASE_URL（https://api.coze.cn）。
- F-cl-102: 环境变量 `COZELOOP_WORKSPACE_ID` 对应 workspace_id 参数（必填）。
- F-cl-103: 环境变量 `COZELOOP_API_TOKEN` 对应 PAT Token 认证。
- F-cl-104: 环境变量 `COZELOOP_JWT_OAUTH_CLIENT_ID`、`COZELOOP_JWT_OAUTH_PRIVATE_KEY`、`COZELOOP_JWT_OAUTH_PUBLIC_KEY_ID` 对应 JWT OAuth 认证。
- F-cl-105: 环境变量 `COZELOOP_SCENE` 可覆盖 runtime.scene 值。
- F-cl-106: `new_client()` 支持高级配置：`tag_truncate_conf`（TagTruncateConf，自定义 normal_field_max_byte 和 input_output_field_max_byte）、`trace_queue_conf`（QueueConf，自定义 span_queue_length 和 span_max_export_batch_length）、`api_base_path`（APIBasePath，自定义 span 和 file 上传路径）、`trace_finish_event_processor`（自定义完成事件回调）、`http_client`（自定义 httpx.Client）。
- F-cl-107: `ultra_large_report` 参数（默认 False）控制超过 1MB 的 input/output 是否截断（False=截断到 1000 字符）或上传为文件（True=单独文件上传）。
- F-cl-108: Logger 默认名称为 'cozeloop'，默认级别 WARN，输出到 stdout，格式为 `%(asctime)s %(name)s %(filename)s:%(lineno)d [%(levelname)s] [cozeloop] %(message)s`。

## 异常体系

- F-cl-109: 所有自定义异常继承自 `LoopError` 基类。
- F-cl-110: 具体异常类：`InvalidParamError`（参数无效）、`AuthInfoRequiredError`（缺少认证信息）、`InternalError`（内部错误）、`ParsePrivateKeyError`（私钥解析失败）、`HeaderParentError`（traceparent header 无效）、`NetworkError`（网络错误）、`ClientClosedError`（客户端已关闭）、`RemoteServiceError`（远端服务错误，含 http_code/error_code/error_message/log_id）、`AuthError`（认证错误）。
