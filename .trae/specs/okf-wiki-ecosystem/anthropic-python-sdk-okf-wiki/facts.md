# Anthropic Python SDK - R阶段事实采集

> 采集时间：2026-08-27
> 源码版本：基于 external/libs/anthropics/anthropic-sdk-python/src/anthropic/
> 事实数量：90条

## 1. 客户端体系

F-001: __init__.py 从 _client 模块导入 Client, Stream, Timeout, Anthropic, AsyncClient, AsyncStream, AsyncAnthropic, RequestOptions
  - 源码：src/anthropic/__init__.py:8

F-002: __init__.py 导出 Anthropic, AsyncAnthropic, Client, AsyncClient, Stream, AsyncStream 等类到 __all__ 列表
  - 源码：src/anthropic/__init__.py:49-107

F-003: 类 Anthropic 继承自 SyncAPIClient，定义在 _client.py
  - 源码：src/anthropic/_client.py:124

F-004: 类 AsyncAnthropic 继承自 AsyncAPIClient，定义在 _client.py
  - 源码：src/anthropic/_client.py:546

F-005: Anthropic.__init__ 接受参数 api_key, auth_token, credentials, config, profile, webhook_key, base_url, timeout, max_retries, default_headers, default_query, http_client, middleware, _strict_response_validation, _token_cache
  - 源码：src/anthropic/_client.py:133-162

F-006: Client 是 Anthropic 的别名，AsyncClient 是 AsyncAnthropic 的别名
  - 源码：src/anthropic/_client.py:1112-1114

F-007: Anthropic 类通过 @cached_property 定义 messages, models, files, skills, beta 等懒加载属性
  - 源码：src/anthropic/_client.py:284-312

F-008: Anthropic.default_headers 返回包含 "anthropic-version": "2023-06-01" 和 "X-Stainless-Async": "false" 的字典
  - 源码：src/anthropic/_client.py:354-360

F-009: AsyncAnthropic.default_headers 返回包含 "anthropic-version": "2023-06-01" 和 "X-Stainless-Async": f"async:{get_async_library()}" 的字典
  - 源码：src/anthropic/_client.py:776-782

F-010: 类 AnthropicWithRawResponse 包含 messages, models, files, skills, beta 等属性，返回对应的 WithRawResponse 包装类
  - 源码：src/anthropic/_client.py:964-998

F-011: 类 AnthropicWithStreamedResponse 包含 messages, models, files, skills, beta 等属性，返回对应的 WithStreamingResponse 包装类
  - 源码：src/anthropic/_client.py:1038-1072

F-012: DEFAULT_TIMEOUT 常量值为 httpx2.Timeout(timeout=600, connect=5.0)（10分钟超时）
  - 源码：src/anthropic/_constants.py:9

F-013: DEFAULT_MAX_RETRIES 常量值为 2
  - 源码：src/anthropic/_constants.py:10

F-014: DEFAULT_CONNECTION_LIMITS 常量值为 httpx2.Limits(max_connections=1000, max_keepalive_connections=100)
  - 源码：src/anthropic/_constants.py:11

F-015: INITIAL_RETRY_DELAY 常量值为 0.5，MAX_RETRY_DELAY 常量值为 8.0
  - 源码：src/anthropic/_constants.py:13-14

## 2. Messages API

F-016: 类 Messages 继承自 SyncAPIResource，定义在 resources/messages/messages.py
  - 源码：src/anthropic/resources/messages/messages.py:96

F-017: Messages.create 方法接受必填参数 max_tokens: int, messages: Iterable[MessageParam], model: ModelParam
  - 源码：src/anthropic/resources/messages/messages.py:121-146

F-018: Messages.create 方法可选参数包括 cache_control, container, inference_geo, metadata, output_config, service_tier, stop_sequences, stream, system, thinking, tool_choice, tools, user_profile_id
  - 源码：src/anthropic/resources/messages/messages.py:127-139

F-019: Messages 类通过 @cached_property 定义 batches 属性，返回 Batches 实例
  - 源码：src/anthropic/resources/messages/messages.py:97-99

F-020: Messages.create 在 stream: Literal[False] 时返回 Message 类型
  - 源码：src/anthropic/resources/messages/messages.py:146

F-021: DEPRECATED_MODELS 字典包含 "claude-1.3", "claude-instant-1.2", "claude-3-sonnet-20240229", "claude-3-opus-20240229" 等已废弃模型及对应废弃日期
  - 源码：src/anthropic/resources/messages/messages.py:72-91

F-022: MODELS_TO_WARN_WITH_THINKING_ENABLED 列表包含 "claude-opus-4-6", "claude-mythos-preview"
  - 源码：src/anthropic/resources/messages/messages.py:93

F-023: MODEL_NONSTREAMING_TOKENS 字典定义了 "claude-opus-4-20250514" 等模型的非流式token限制为8192
  - 源码：src/anthropic/_constants.py:16-24

F-024: Messages 类通过 @cached_property 定义 with_raw_response 属性，返回 MessagesWithRawResponse 实例
  - 源码：src/anthropic/resources/messages/messages.py:101-109

F-025: Messages 类通过 @cached_property 定义 with_streaming_response 属性，返回 MessagesWithStreamingResponse 实例
  - 源码：src/anthropic/resources/messages/messages.py:111-118

## 3. 流式处理

F-026: 泛型类 Stream[_T] 定义在 _streaming.py，提供同步流响应迭代接口
  - 源码：src/anthropic/_streaming.py:22

F-027: 泛型类 AsyncStream[_T] 定义在 _streaming.py，提供异步流响应迭代接口
  - 源码：src/anthropic/_streaming.py:169

F-028: Stream.__init__ 接受参数 cast_to: type[_T], response: httpx2.Response, client: Anthropic, options: Optional[FinalRequestOptions]
  - 源码：src/anthropic/_streaming.py:29-36

F-029: Stream 类支持上下文管理器协议（__enter__/__exit__）和迭代器协议（__iter__/__next__）
  - 源码：src/anthropic/_streaming.py:44-49,149-158

F-030: Stream.__stream__ 方法处理的SSE事件类型包括 "message_start", "message_delta", "message_stop", "content_block_start", "content_block_delta", "content_block_stop"
  - 源码：src/anthropic/_streaming.py:74-81

F-031: Stream.__stream__ 方法处理的SSE事件类型还包括 "agent.message", "agent.thinking", "agent.tool_use", "agent.tool_result", "agent.mcp_tool_use"
  - 源码：src/anthropic/_streaming.py:87-94

F-032: Stream.__stream__ 方法处理 "error" 事件时调用 self._client._make_status_error 抛出异常
  - 源码：src/anthropic/_streaming.py:131-144

F-033: 类 ServerSentEvent 包含属性 event, data, id, retry, raw
  - 源码：src/anthropic/_streaming.py:317-359

F-034: 类 SSEDecoder 实现 SSE 协议解码，包含 iter_bytes, aiter_bytes, decode 方法
  - 源码：src/anthropic/_streaming.py:369-478

F-035: 类 MessageStream[ResponseFormatT] 定义在 lib/streaming/_messages.py，包含 text_stream 属性
  - 源码：src/anthropic/lib/streaming/_messages.py:33-53

F-036: MessageStream 类包含 get_final_message(), get_final_text(), until_done() 方法
  - 源码：src/anthropic/lib/streaming/_messages.py:93-124

F-037: 类 MessageStreamManager[ResponseFormatT] 作为上下文管理器包装 MessageStream
  - 源码：src/anthropic/lib/streaming/_messages.py:150-182

## 4. 工具系统

F-038: 类 ToolError 继承自 Exception，包含 content: BetaFunctionToolResultType 属性
  - 源码：src/anthropic/lib/tools/_beta_functions.py:30-61

F-039: 抽象类 BetaBuiltinFunctionTool 包含抽象方法 to_dict() 和 call(input: object)
  - 源码：src/anthropic/lib/tools/_beta_functions.py:71-77

F-040: 泛型类 BaseFunctionTool[CallableT] 包含属性 func, name, description, input_schema, close
  - 源码：src/anthropic/lib/tools/_beta_functions.py:107-143

F-041: 类 BetaFunctionTool 继承自 BaseFunctionTool[FunctionT]，包含 call(input: object) 方法
  - 源码：src/anthropic/lib/tools/_beta_functions.py:271-282

F-042: 类 BetaAsyncFunctionTool 继承自 BaseFunctionTool[AsyncFunctionT]，包含 async call(input: object) 方法
  - 源码：src/anthropic/lib/tools/_beta_functions.py:285-296

F-043: beta_tool 装饰器支持带参数和不带参数两种用法，将普通函数包装为 BetaFunctionTool
  - 源码：src/anthropic/lib/tools/_beta_functions.py:348-475

F-044: beta_async_tool 装饰器将异步函数包装为 BetaAsyncFunctionTool
  - 源码：src/anthropic/lib/tools/_beta_functions.py:478-620

F-045: 类型别名 BetaRunnableTool = Union[BetaFunctionTool[Any], BetaBuiltinFunctionTool]
  - 源码：src/anthropic/lib/tools/_beta_functions.py:623

F-046: 泛型类 BaseToolRunner[AnyFunctionToolT, ResponseFormatT] 包含 _tools_by_name, _params, _options, _max_iterations, _iteration_count 属性
  - 源码：src/anthropic/lib/tools/_beta_runner.py:96-121

F-047: _STOP_REASON_STEPS 字典将 BetaStopReason 映射为下一步动作："tool_use"→"run_tools", "end_turn"→"stop", "max_tokens"→"stop"
  - 源码：src/anthropic/lib/tools/_beta_runner.py:63-73

F-048: BaseToolRunner 包含 append_messages(*messages) 方法，方法接受 BetaMessageParam 或 ParsedBetaMessage 类型参数
  - 源码：src/anthropic/lib/tools/_beta_runner.py:138-150

## 5. Beta API

F-049: 类 Beta 继承自 SyncAPIResource，定义在 resources/beta/beta.py
  - 源码：src/anthropic/resources/beta/beta.py:132

F-050: Beta 类通过 @cached_property 定义 agents 属性，返回 Agents 实例
  - 源码：src/anthropic/resources/beta/beta.py:141-143

F-051: Beta 类通过 @cached_property 定义 sessions 属性，返回 Sessions 实例
  - 源码：src/anthropic/resources/beta/beta.py:149-151

F-052: Beta 类通过 @cached_property 定义 memory_stores 属性，返回 MemoryStores 实例
  - 源码：src/anthropic/resources/beta/beta.py:165-167

F-053: Beta 类通过 @cached_property 定义 skills, environments, vaults, deployments, dreams, tunnels, organization, webhooks, user_profiles, models, messages, files 等属性
  - 源码：src/anthropic/resources/beta/beta.py:133-195

F-054: 类 Agents 继承自 SyncAPIResource，包含 versions 子资源属性
  - 源码：src/anthropic/resources/beta/agents/agents.py:47-50

F-055: Agents.create 方法接受必填参数 model: agent_create_params.Model, name: str
  - 源码：src/anthropic/resources/beta/agents/agents.py:71-90

F-056: Agents.create 方法可选参数包括 description, mcp_servers, metadata, multiagent, skills, system, tools, betas
  - 源码：src/anthropic/resources/beta/agents/agents.py:76-83

F-057: Agents.create 方法 POST 到 "/v1/agents?beta=true" 端点
  - 源码：src/anthropic/resources/beta/agents/agents.py:144-145

F-058: Agents.create 方法默认添加 "anthropic-beta": "managed-agents-2026-04-01" 请求头
  - 源码：src/anthropic/resources/beta/agents/agents.py:143

## 6. 多云后端

F-059: 类 AnthropicAWS 继承自 Anthropic，定义在 lib/aws/_client.py
  - 源码：src/anthropic/lib/aws/_client.py:25

F-060: 类 AsyncAnthropicAWS 继承自 AsyncAnthropic，定义在 lib/aws/_client.py
  - 源码：src/anthropic/lib/aws/_client.py:233

F-061: AnthropicAWS.__init__ 接受参数 aws_access_key, aws_secret_key, aws_region, aws_profile, aws_session_token, workspace_id, skip_auth
  - 源码：src/anthropic/lib/aws/_client.py:35-57

F-062: AnthropicAWS._prepare_request 方法使用 SigV4 签名，调用 get_auth_headers 生成 AWS 认证头
  - 源码：src/anthropic/lib/aws/_client.py:145-166

F-063: 类 AnthropicBedrock 继承自 BaseBedrockClient[httpx2.Client, Stream[Any]] 和 SyncAPIClient，定义在 lib/bedrock/_client.py
  - 源码：src/anthropic/lib/bedrock/_client.py:132

F-064: 类 AsyncAnthropicBedrock 继承自 BaseBedrockClient[httpx2.AsyncClient, AsyncStream[Any]] 和 AsyncAPIClient
  - 源码：src/anthropic/lib/bedrock/_client.py:310

F-065: AnthropicBedrock 默认 base_url 为 f"https://bedrock-runtime.{self.aws_region}.amazonaws.com"
  - 源码：src/anthropic/lib/bedrock/_client.py:189-190

F-066: DEFAULT_VERSION 常量（Bedrock）值为 "bedrock-2023-05-31"
  - 源码：src/anthropic/lib/bedrock/_client.py:31

F-067: 类 AnthropicVertex 继承自 BaseVertexClient[httpx2.Client, Stream[Any]] 和 SyncAPIClient，定义在 lib/vertex/_client.py
  - 源码：src/anthropic/lib/vertex/_client.py:92

F-068: 类 AsyncAnthropicVertex 继承自 BaseVertexClient[httpx2.AsyncClient, AsyncStream[Any]] 和 AsyncAPIClient
  - 源码：src/anthropic/lib/vertex/_client.py:256

F-069: DEFAULT_VERSION 常量（Vertex）值为 "vertex-2023-10-16"
  - 源码：src/anthropic/lib/vertex/_client.py:33

F-070: AnthropicVertex 根据 region 选择 base_url："global"→"https://aiplatform.googleapis.com/v1"，"us"→"https://aiplatform.us.rep.googleapis.com/v1"
  - 源码：src/anthropic/lib/vertex/_client.py:123-130

F-071: __init__.py 从 lib.aws 导入 AnthropicAWS 和 AsyncAnthropicAWS
  - 源码：src/anthropic/__init__.py:112

F-072: __init__.py 通过 from .lib.vertex import * 和 from .lib.bedrock import * 导入 Vertex 和 Bedrock 客户端
  - 源码：src/anthropic/__init__.py:114-115

F-073: __init__.py 从 lib.google_cloud 导入 AnthropicGoogleCloud 和 AsyncAnthropicGoogleCloud
  - 源码：src/anthropic/__init__.py:119-122

## 7. 中间件与扩展

F-074: 类 Middleware 定义在 _middleware.py，包含 handle(request, call_next) 和 handle_async(request, call_next) 方法
  - 源码：src/anthropic/_middleware.py:46-58

F-075: 类型别名 CallNext = Callable[[APIRequest], "APIResponse[Any]"]
  - 源码：src/anthropic/_middleware.py:21

F-076: 类型别名 AsyncCallNext = Callable[[APIRequest], Awaitable["AsyncAPIResponse[Any]"]]
  - 源码：src/anthropic/_middleware.py:33

F-077: 类型别名 MiddlewareInput = Union[Middleware, MiddlewareCallable, AsyncMiddlewareCallable]
  - 源码：src/anthropic/_middleware.py:63

F-078: validate_sync_middleware 函数验证同步中间件，拒绝异步中间件和未实现 handle() 的 Middleware 子类
  - 源码：src/anthropic/_middleware.py:85-104

F-079: validate_async_middleware 函数验证异步中间件，拒绝同步中间件和未实现 handle_async() 的 Middleware 子类
  - 源码：src/anthropic/_middleware.py:107-126

F-080: 类 BetaRefusalFallbackMiddleware 继承自 Middleware，定义在 lib/middleware/_fallbacks.py
  - 源码：src/anthropic/lib/middleware/_fallbacks.py:104

F-081: 类 BetaFallbackState 包含 index: int | None 属性，支持上下文管理器协议（__enter__/__exit__）
  - 源码：src/anthropic/lib/middleware/_fallbacks.py:62-89

F-082: DEFAULT_BETAS 元组默认包含 ("fallback-credit-2026-07-01",)
  - 源码：src/anthropic/lib/middleware/_fallbacks.py:49

F-083: 类 SyncAPIResource 包含 _client: SyncAPIClient 属性，在 __init__ 中绑定 _get, _post, _patch, _put, _delete, _get_api_list 方法
  - 源码：src/anthropic/_resource.py:12-25

F-084: 类 AsyncAPIResource 包含 _client: AsyncAPIClient 属性，_sleep 方法使用 anyio.sleep
  - 源码：src/anthropic/_resource.py:28-41

## 8. 异常体系

F-085: 类 AnthropicError 继承自 Exception，是所有SDK异常的基类
  - 源码：src/anthropic/_exceptions.py:30-31

F-086: 类 APIError 继承自 AnthropicError，包含属性 message: str, request: httpx2.Request, body: object | None
  - 源码：src/anthropic/_exceptions.py:34-53

F-087: 类 APIStatusError 继承自 APIError，包含属性 response: httpx2.Response, status_code: int, request_id: str | None, type: ErrorType | None, workspace_id: str | None
  - 源码：src/anthropic/_exceptions.py:70-91

F-088: 类 APIConnectionError 继承自 APIError；类 APITimeoutError 继承自 APIConnectionError
  - 源码：src/anthropic/_exceptions.py:94-104

F-089: 类 RetryableError 继承自 AnthropicError，类体为空（pass语句）
  - 源码：src/anthropic/_exceptions.py:107-114

F-090: HTTP状态码对应的异常类映射：400→BadRequestError, 401→AuthenticationError, 403→PermissionDeniedError, 404→NotFoundError, 409→ConflictError, 413→RequestTooLargeError, 422→UnprocessableEntityError, 429→RateLimitError, 503→ServiceUnavailableError, 504→DeadlineExceededError, 529→OverloadedError, 5xx→InternalServerError
  - 源码：src/anthropic/_exceptions.py:116-160
