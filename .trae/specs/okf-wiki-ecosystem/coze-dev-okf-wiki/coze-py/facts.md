# coze-py 源码事实清单（R阶段）

> 从 `d:/spaces/SpecWeave/external/libs/ai/coze-dev/coze-py/cozepy/` 源码中直接可观测的事实。不含推断、不含"用于"、不含"设计为"。

## 1. 版本与基础配置

F-cp-001: `VERSION = "0.20.0"` 定义在 `cozepy/version.py` 第6行。
(source: `cozepy/version.py` L6)

F-cp-002: `COZE_COM_BASE_URL = "https://api.coze.com"`，默认 base_url。
(source: `cozepy/config.py` L4)

F-cp-003: `COZE_CN_BASE_URL = "https://api.coze.cn"`，中国区 base_url。
(source: `cozepy/config.py` L6)

F-cp-004: `DEFAULT_TIMEOUT = httpx.Timeout(timeout=600.0, connect=5.0)`，默认超时600秒（10分钟），连接超时5秒。
(source: `cozepy/config.py` L9)

F-cp-005: `DEFAULT_CONNECTION_LIMITS = httpx.Limits(max_connections=1000, max_keepalive_connections=100)`。
(source: `cozepy/config.py` L10)

F-cp-006: `user_agent()` 函数使用 `@lru_cache(maxsize=1)` 装饰，返回格式为 `cozepy/{VERSION} python/{python_version} {os_name}/{os_version}` 的小写字符串。
(source: `cozepy/version.py` L31-L38)

F-cp-007: `coze_client_user_agent()` 函数使用 `@lru_cache(maxsize=1)` 装饰，返回 JSON 格式字符串，包含 version/lang/lang_version/os_name/os_version 字段。
(source: `cozepy/version.py` L41-L51)

F-cp-008: `get_os_version()` 函数支持 darwin(macOS)/windows/linux 三种平台检测，linux 平台优先使用 `distro.version()`，ImportError 时回退到 `platform.release()`。
(source: `cozepy/version.py` L9-L28)

## 2. 日志系统

F-cp-009: 日志器名称为 `"cozepy"`，通过 `logging.getLogger("cozepy")` 获取。
(source: `cozepy/log.py` L3)

F-cp-010: 日志格式为 `[cozepy][%(levelname)s][%(asctime)s] %(message)s`，日期格式为 `%Y-%m-%d %H:%M:%S`。
(source: `cozepy/log.py` L6)

F-cp-011: `logger.propagate = False`，日志不向上传播。
(source: `cozepy/log.py` L9)

F-cp-012: `setup_logging(level)` 函数接受 logging level 参数，默认 WARNING，校验 level 是否在 FATAL/ERROR/WARNING/INFO/DEBUG/NOTSET 中，不在则抛出 ValueError。
(source: `cozepy/log.py` L13-L24)

F-cp-013: 模块级别导出 `log_fatal`/`log_error`/`log_warning`/`log_info`/`log_debug` 快捷函数，分别绑定 logger 的对应方法。
(source: `cozepy/log.py` L27-L31)

## 3. 异常体系

F-cp-014: `CozeError` 继承自 `Exception`，是所有 coze 错误的基类，类体为 `pass`。
(source: `cozepy/exception.py` L5-L10)

F-cp-015: `CozeAPIError` 继承自 `CozeError`，构造函数接受 `code: Optional[int]`、`msg: str`、`logid: Optional[str]`、`debug_url: Optional[str]` 四个参数，code>0 时在错误消息中包含 code 字段。
(source: `cozepy/exception.py` L13-L30)

F-cp-016: `CozePKCEAuthErrorType` 继承自 `str, Enum`，包含四个枚举值：AUTHORIZATION_PENDING、SLOW_DOWN、ACCESS_DENIED、EXPIRED_TOKEN。
(source: `cozepy/exception.py` L33-L38)

F-cp-017: `CozePKCEAuthError` 继承自 `CozeError`，构造函数接受 `error: CozePKCEAuthErrorType` 和 `logid: Optional[str]`，错误消息格式为 `pkce auth error: {error.value}`。
(source: `cozepy/exception.py` L43-L47)

F-cp-018: `CozeInvalidEventError` 继承自 `CozeError`，构造函数接受 `field: str`、`data: str`、`logid: str` 三个参数。
(source: `cozepy/exception.py` L50-L58)

F-cp-019: 模块级常量 `COZE_PKCE_AUTH_ERROR_TYPE_ENUMS = set(e.value for e in CozePKCEAuthErrorType)`，将枚举值转为集合。
(source: `cozepy/exception.py` L40)

## 4. 客户端入口类

F-cp-020: `Coze` 类（同步客户端）构造函数接受 `auth: Auth`、`base_url: str = COZE_COM_BASE_URL`、`http_client: Optional[SyncHTTPClient] = None` 三个参数。
(source: `cozepy/coze.py` L33-L39)

F-cp-021: `Coze.__init__` 中使用 `remove_url_trailing_slash(base_url)` 处理 base_url，创建 `Requester(auth=auth, sync_client=http_client)`。
(source: `cozepy/coze.py` L40-L42)

F-cp-022: `Coze` 类通过懒加载 property 模式提供20个服务客户端属性：bots、workspaces、conversations、chat、connectors、files、workflows、knowledge（deprecated）、datasets、audio、templates、users、websockets、variables、apps、enterprises、api_apps、folders、benefit_limitations、benefits、bill_tasks。
(source: `cozepy/coze.py` L45-L65, L67-L239)

F-cp-023: `Coze.knowledge` property 访问时会发出 `DeprecationWarning`，提示使用 `coze.datasets` 替代。
(source: `cozepy/coze.py` L116-L127)

F-cp-024: `AsyncCoze` 类（异步客户端）构造函数接受 `auth: Auth`、`base_url: str = COZE_COM_BASE_URL`、`http_client: Optional[AsyncHTTPClient] = None` 三个参数。
(source: `cozepy/coze.py` L242-L248)

F-cp-025: `AsyncCoze.__init__` 中若传入 `SyncAuth` 类型的 auth，会发出 `DeprecationWarning`，提示使用 `AsyncAuth`。
(source: `cozepy/coze.py` L251-L257)

F-cp-026: `AsyncCoze` 类同样通过懒加载 property 模式提供20个异步服务客户端属性，与 `Coze` 一一对应但均为 Async 版本。
(source: `cozepy/coze.py` L261-L282, L284-L456)

## 5. 数据模型基类

F-cp-027: `CozeModel` 是所有数据模型的基类（基于 Pydantic），被所有 Resp/Config/Info 等数据类继承。
(source: `cozepy/model.py`, 引用见 `cozepy/audio/rooms/__init__.py` L5, L10, L19, L49, L54, L69)

F-cp-028: `DynamicStrEnum` 是一个动态字符串枚举基类，被 MessageRole、ChatStatus、ChatEventType、RoomMode、BotMode、PublishStatus、VoiceState、VoiceModelType、AudioFormat、LanguageCode、MessageType、MessageContentType、MessageObjectStringType、ChatRequiredActionType、ChatToolCallType、WorkspaceRoleType、WorkspaceType、FolderType、TemplateEntityType、DatasetStatus、DocumentStatus、DocumentFormatType、DocumentSourceType、DocumentUpdateType、DocumentChunkStrategy、FeedbackType、EnterpriseMemberRole、PhotoStatus、LiveType、VariableType、VariableChannel、UserInputType、SuggestReplyMode、AppType 等枚举继承。
(source: `cozepy/__init__.py` L139, L200, L338; `cozepy/chat/__init__.py` L26)

## 6. 分页模式

F-cp-029: SDK 提供三种分页基类：`NumberPaged`（页码分页）、`TokenPaged`（令牌分页）、`LastIDPaged`（最后ID分页），每种均有对应的 Async 版本。
(source: `cozepy/model.py`, 导出见 `cozepy/__init__.py` L330-L352)

F-cp-030: 分页相关的响应模型包括 `NumberPagedResponse`、`TokenPagedResponse`、`LastIDPagedResponse`、`ListResponse`。
(source: `cozepy/__init__.py` L344-L351)

F-cp-031: 分页基类 `PagedBase` 和 `AsyncPagedBase` 是所有分页类的公共基类。
(source: `cozepy/__init__.py` L348, L334)

## 7. 流式响应

F-cp-032: `Stream[T]` 和 `AsyncStream[T]` 是流式响应的泛型包装类。
(source: `cozepy/__init__.py` L349, L335)

F-cp-033: `Stream` 类构造函数接受 `raw_response`、`data`（Iterator[str]）、`fields: List[str]`、`handler: Callable` 参数。
(source: `cozepy/workflows/chat/__init__.py` L123-L128)

F-cp-034: `IteratorHTTPResponse[T]` 和 `AsyncIteratorHTTPResponse[T]` 是 HTTP 流式响应的泛型包装类。
(source: `cozepy/__init__.py` L342, L331)

F-cp-035: `FileHTTPResponse` 用于文件下载响应。
(source: `cozepy/__init__.py` L339)

## 8. HTTP 请求层

F-cp-036: `SyncHTTPClient` 和 `AsyncHTTPClient` 分别是同步和异步 HTTP 客户端类，封装 httpx 客户端。
(source: `cozepy/request.py`, 导出见 `cozepy/__init__.py` L353-L357)

F-cp-037: `Requester` 类统一封装请求逻辑，构造函数接受 `auth`、`sync_client`、`async_client` 参数，提供 `request()` 同步方法和 `arequest()` 异步方法。
(source: `cozepy/request.py`, 引用见 `cozepy/coze.py` L42, L259)

F-cp-038: `HTTPRequest` 和 `HTTPResponse` 是 HTTP 请求/响应的基础模型类。
(source: `cozepy/__init__.py` L340-L341)

## 9. 认证体系

F-cp-039: 认证基类为 `Auth`，派生 `SyncAuth` 和 `AsyncAuth`。
(source: `cozepy/auth/__init__.py`, 导出见 `cozepy/__init__.py` L89-L113)

F-cp-040: 同步 Token 认证类为 `TokenAuth`（继承 SyncAuth），异步 Token 认证类为 `AsyncTokenAuth`（继承 AsyncAuth）。
(source: `cozepy/__init__.py` L110, L95)

F-cp-041: JWT 认证类包括 `JWTAuth`（同步）和 `AsyncJWTAuth`（异步），以及 `JWTOAuthApp` 和 `AsyncJWTOAuthApp`。
(source: `cozepy/__init__.py` L100, L93, L101, L93)

F-cp-042: OAuth 认证包含四种应用类型：`OAuthApp`（基类）、`WebOAuthApp`/`AsyncWebOAuthApp`、`PKCEOAuthApp`/`AsyncPKCEOAuthApp`、`DeviceOAuthApp`/`AsyncDeviceOAuthApp`。
(source: `cozepy/__init__.py` L102-L105, L96, L91, L94, L99)

F-cp-043: OAuth 相关数据模型包括 `OAuthToken`、`DeviceAuthCode`、`Scope`、`ScopeAccountPermission`、`ScopeAttributeConstraint`、`ScopeAttributeConstraintConnectorBotChatAttribute`。
(source: `cozepy/__init__.py` L98, L103, L105-L108)

F-cp-044: 模块提供 `load_oauth_app_from_config` 工厂函数，从配置加载 OAuth 应用。
(source: `cozepy/__init__.py` L112, L929)

## 10. Chat（对话）模块

F-cp-045: Chat 模块包含 `ChatClient`（同步）和 `AsyncChatClient`（异步）两个客户端类。
(source: `cozepy/__init__.py` L183, L185)

F-cp-046: `Chat` 模型包含 `id`、`conversation_id`、`bot_id`、`status`、`created_at`、`completed_at`、`failed_at`、`meta_data`、`last_error`、`required_action`、`usage` 等字段。
(source: `cozepy/chat/__init__.py`)

F-cp-047: `ChatStatus` 枚举（DynamicStrEnum）包含对话状态值，`ChatEvent`/`ChatEventType` 枚举定义流式事件类型。
(source: `cozepy/__init__.py` L187-L188, L192)

F-cp-048: `MessageRole` 枚举（DynamicStrEnum）包含 USER = "user" 和 ASSISTANT = "assistant" 两个值。
(source: `cozepy/chat/__init__.py` L26-L30)

F-cp-049: `Message` 模型包含 role、type、content、content_type、meta_data 等字段，`MessageType`、`MessageContentType`、`MessageObjectStringType` 为相关枚举。
(source: `cozepy/__init__.py` L199-L204)

F-cp-050: `MessageObjectString` 模型表示消息对象字符串，包含 type 和 text 字段。
(source: `cozepy/__init__.py` L201-L202)

F-cp-051: Chat 工具调用相关模型包括 `ChatToolCall`、`ChatToolCallFunction`、`ChatToolCallType`、`ChatRequiredAction`、`ChatRequiredActionType`、`ChatSubmitToolOutputs`、`ToolOutput`。
(source: `cozepy/__init__.py` L190-L196, L205)

F-cp-052: `ChatUsage` 模型记录 token 使用量，`ChatPoll` 用于轮询对话状态，`ChatError` 表示对话错误，`InsertedMessage` 表示插入的消息。
(source: `cozepy/__init__.py` L186, L189, L197-L198)

F-cp-053: Chat 消息子模块包含 `ChatMessagesClient`（同步）和 `AsyncChatMessagesClient`（异步）。
(source: `cozepy/__init__.py` L207-L210)

F-cp-054: 模块级函数 `_chat_stream_handler` 用于解析 SSE 流中的 chat 事件，在 workflows/chat 中被复用。
(source: `cozepy/workflows/chat/__init__.py` L6, L127)

## 11. Bots（智能体）模块

F-cp-055: Bots 模块包含 `BotsClient`（同步）和 `AsyncBotsClient`（异步）两个客户端类。
(source: `cozepy/__init__.py` L134, L145)

F-cp-056: `Bot` 模型包含智能体的完整信息，子模型包括 `BotModelInfo`、`BotPromptInfo`、`BotKnowledge`、`BotPluginInfo`/`BotPluginAPIInfo`、`BotOnboardingInfo`、`BotVoiceInfo`、`BotWorkflowInfo`、`BotSuggestReplyInfo`、`BotVariable`、`BotBackgroundImageInfo`/`BackgroundImageInfo`。
(source: `cozepy/__init__.py` L135-L161)

F-cp-057: Bot 相关枚举包括 `BotMode`、`PublishStatus`、`SuggestReplyMode`、`UserInputType`、`VariableType`、`VariableChannel`、`PluginIDList`（类型别名）、`WorkflowIDList`（类型别名）、`CanvasPosition`、`GradientPosition`。
(source: `cozepy/__init__.py` L139, L153-L160, L150-L151)

F-cp-058: Bots 操作响应模型包括 `SimpleBot`、`UpdateBotResp`、`UnpublishBotResp`。
(source: `cozepy/__init__.py` L154, L156-L157)

F-cp-059: Bots 子模块包含 collaborators（协作者）、collaboration_modes（协作模式）、versions（版本）三个子客户端。
(source: `cozepy/__init__.py` L163-L181)

## 12. Workflows（工作流）模块

F-cp-060: Workflows 模块包含 `WorkflowsClient`（同步）和 `AsyncWorkflowsClient`（异步）两个客户端类。
(source: `cozepy/__init__.py` L466-L470)

F-cp-061: 工作流模型包括 `WorkflowBasic`、`WorkflowInfo`，枚举 `WorkflowMode`。
(source: `cozepy/__init__.py` L467-L469)

F-cp-062: Workflows 子模块包含 chat（对话流）、collaborators（协作者）、versions（版本）、runs（运行记录）四个子客户端。
(source: `cozepy/__init__.py` L472-L510)

F-cp-063: `WorkflowsChatClient`（同步）和 `AsyncWorkflowsChatClient`（异步）提供 `stream()` 方法执行对话流，POST 到 `/v1/workflows/chat` 端点，返回 `Stream[ChatEvent]` 或 `AsyncIterator[ChatEvent]`。
(source: `cozepy/workflows/chat/__init__.py` L13-L128, L131-L247)

F-cp-064: WorkflowsChatClient.stream() 接受 workflow_id、additional_messages（List[Message]）、parameters（Dict[str, Any]）、app_id、bot_id、conversation_id、ext 参数，使用 `fields=["event", "data"]` 和 `_chat_stream_handler` 解析 SSE 流。
(source: `cozepy/workflows/chat/__init__.py` L18-L66, L107-L128)

F-cp-065: Workflows runs 子模块包含 `WorkflowsRunsClient`/`AsyncWorkflowsRunsClient`，事件模型包括 `WorkflowEvent`、`WorkflowEventError`、`WorkflowEventInterrupt`/`WorkflowEventInterruptData`、`WorkflowEventMessage`，枚举 `WorkflowEventType`，结果模型 `WorkflowRunResult`。
(source: `cozepy/__init__.py` L481-L490)

F-cp-066: Workflows run_histories 子模块包含 `WorkflowsRunsRunHistoriesClient`，模型 `WorkflowRunHistory`、`WorkflowRunHistoryNodeExecuteStatus`，枚举 `WorkflowExecuteStatus`、`WorkflowRunMode`。
(source: `cozepy/__init__.py` L492-L498)

F-cp-067: Workflows versions 子模块包含 `WorkflowsVersionsClient`，模型 `WorkflowVersionInfo`、`WorkflowUserInfo`。
(source: `cozepy/__init__.py` L505-L509)

## 13. Conversations（会话）模块

F-cp-068: Conversations 模块包含 `ConversationsClient`（同步）和 `AsyncConversationsClient`（异步）两个客户端类。
(source: `cozepy/__init__.py` L231-L237)

F-cp-069: 会话模型包括 `Conversation`、`Section`、`DeleteConversationResp`。
(source: `cozepy/__init__.py` L233-L236)

F-cp-070: Conversations 子模块包含 message（消息）和 message/feedback（消息反馈）两个子客户端。
(source: `cozepy/__init__.py` L238-L248)

F-cp-071: 消息客户端为 `MessagesClient`/`AsyncMessagesClient`，反馈客户端为 `ConversationsMessagesFeedbackClient`/`AsyncMessagesFeedbackClient`，反馈模型包括 `CreateConversationMessageFeedbackResp`、`DeleteConversationMessageFeedbackResp`，枚举 `FeedbackType`。
(source: `cozepy/__init__.py` L239-L248)

## 14. WebSocket 模块

F-cp-072: WebSocket 顶层客户端为 `WebsocketsClient`（同步）和 `AsyncWebsocketsClient`（异步），包含 `chat` 和 `audio` 两个子属性。
(source: `cozepy/websockets/__init__.py`, 导出见 `cozepy/__init__.py` L376-L383)

F-cp-073: WebSocket 基类 `WebsocketsBaseClient` 和 `AsyncWebsocketsBaseClient` 定义在 `cozepy/websockets/ws.py`，构造函数接受 base_url、requester、path、event_factory、on_event、wait_events 参数，内部使用 `_input_queue` 队列管理待发送事件。
(source: `cozepy/websockets/ws.py`, 引用见 `cozepy/websockets/audio/speech/__init__.py` L8-L17)

F-cp-074: WebSocket 事件基类为 `WebsocketsEvent`，通过 `WebsocketsEventFactory` 将 event_type 字符串映射到具体事件类，`WebsocketsEventType` 为枚举类定义所有事件类型。
(source: `cozepy/websockets/ws.py`, 导出见 `cozepy/__init__.py` L450-L464)

F-cp-075: WebSocket 事件处理器基类为 `WebsocketsBaseEventHandler` 和 `AsyncWebsocketsBaseEventHandler`，提供 `to_dict()` 方法将处理器方法转为 dict 映射，子类通过定义 `on_xxx` 方法处理具体事件。
(source: `cozepy/websockets/ws.py`, 引用见 `cozepy/websockets/audio/speech/__init__.py` L148-L167)

F-cp-076: WebSocket 音频配置模型包括 `InputAudio`、`OutputAudio`、`OpusConfig`、`PCMConfig`、`LimitConfig`。
(source: `cozepy/__init__.py` L453-L457, L455-L457)

F-cp-077: `WebsocketsErrorEvent` 表示 WebSocket 错误事件。
(source: `cozepy/__init__.py` L460)

F-cp-078: WebSocket Chat 子模块路径为 `v1/chat`，包含 `WebsocketsChatClient`/`AsyncWebsocketsChatClient`、`WebsocketsChatBuildClient`/`AsyncWebsocketsChatBuildClient`，事件类型超过20种（ChatCreatedEvent、ConversationChatCompletedEvent、ConversationMessageDeltaEvent、ConversationAudioDeltaEvent 等）。
(source: `cozepy/websockets/chat/__init__.py`, 导出见 `cozepy/__init__.py` L418-L449)

F-cp-079: WebSocket Chat 客户端等待 `wait_events=[WebsocketsEventType.CONVERSATION_CHAT_COMPLETED]` 作为对话完成信号。
(source: `cozepy/websockets/chat/__init__.py`)

F-cp-080: WebSocket Audio 子模块包含 `WebsocketsAudioClient`/`AsyncWebsocketsAudioClient`，下设 `speech` 和 `transcriptions` 两个子客户端。
(source: `cozepy/websockets/audio/__init__.py` L7-L44)

F-cp-081: WebSocket Audio Speech 路径为 `v1/audio/speech`，等待事件为 `SPEECH_AUDIO_COMPLETED`，上行事件包括 InputTextBufferAppendEvent、InputTextBufferCompleteEvent、SpeechUpdateEvent；下行事件包括 SpeechCreatedEvent、SpeechUpdatedEvent、InputTextBufferCompletedEvent、SpeechAudioUpdateEvent、SpeechAudioCompletedEvent。
(source: `cozepy/websockets/audio/speech/__init__.py` L21-L145, L183)

F-cp-082: `SpeechAudioUpdateEvent.Data.delta` 字段类型为 bytes，使用 `@field_validator("delta", mode="before")` 将 base64 字符串解码为 bytes，使用 `@field_serializer("delta")` 将 bytes 编码为 base64 字符串。
(source: `cozepy/websockets/audio/speech/__init__.py` L109-L120)

F-cp-083: WebSocket Audio Transcriptions 路径为 `v1/audio/transcriptions`，等待事件为 `TRANSCRIPTIONS_MESSAGE_COMPLETED`，上行事件包括 TranscriptionsUpdateEvent、InputAudioBufferAppendEvent、InputAudioBufferCompleteEvent、InputAudioBufferClearEvent；下行事件包括 TranscriptionsCreatedEvent、TranscriptionsUpdatedEvent、InputAudioBufferCompletedEvent、InputAudioBufferClearedEvent、TranscriptionsMessageUpdateEvent、TranscriptionsMessageCompletedEvent。
(source: `cozepy/websockets/audio/transcriptions/__init__.py` L21-L175, L225)

F-cp-084: `InputAudioBufferAppendEvent.Data.delta` 字段类型为 bytes，使用 `@field_serializer("delta")` 进行 base64 编码；该事件有 `_dump_without_delta()` 方法在日志中输出 delta 长度而非实际数据。
(source: `cozepy/websockets/audio/transcriptions/__init__.py` L44-L65)

## 15. Audio（音频）模块

F-cp-085: Audio 顶层客户端为 `AudioClient`（同步）和 `AsyncAudioClient`（异步），下设 speech、transcriptions、voices、rooms、live、voiceprint_groups 等子客户端。
(source: `cozepy/audio/__init__.py`, 导出见 `cozepy/__init__.py` L29-L88)

F-cp-086: Speech 子模块包含 `SpeechClient`/`AsyncSpeechClient`，枚举 `AudioFormat`、`LanguageCode`，提供文本转语音功能。
(source: `cozepy/__init__.py` L50-L55)

F-cp-087: Voices 子模块包含 `VoicesClient`/`AsyncVoicesClient`，模型 `Voice`、`VoiceEmotionInfo`/`VoiceEmotionInfoInterval`，枚举 `VoiceState`、`VoiceModelType`。
(source: `cozepy/__init__.py` L80-L88)

F-cp-088: Rooms 子模块包含 `RoomsClient`/`AsyncRoomsClient`，提供 `create()` 方法 POST 到 `/v1/audio/rooms`，返回 `CreateRoomResp`（包含 token、uid、room_id、app_id 字段）。
(source: `cozepy/audio/rooms/__init__.py` L80-L128, L131-L179)

F-cp-089: Rooms 配置模型包括 `RoomConfig`（含 audio_config、video_config、prologue_content、room_mode、translate_config、prologue_delay_duration_ms）、`RoomAudioConfig`（codec 字段）、`RoomVideoConfig`（codec、stream_video_type、video_frame_rate、video_frame_expire_duration 字段）、`TranslateConfig`（from_、to 字段，from_ 使用 Field(alias="from")）。
(source: `cozepy/audio/rooms/__init__.py` L10-L67)

F-cp-090: `RoomMode` 枚举包含 DEFAULT = "default"、S2S = "s2s"、PODCAST = "podcast"、TRANSLATE = "translate" 四个值。
(source: `cozepy/audio/rooms/__init__.py` L34-L38)

F-cp-091: RoomsClient.create() 接受 bot_id（必选）、voice_id、conversation_id、uid、workflow_id、config 参数。
(source: `cozepy/audio/rooms/__init__.py` L89-L99)

F-cp-092: Transcriptions 子模块包含 `TranscriptionsClient`/`AsyncTranscriptionsClient`，提供 `create(file)` 方法 POST 到 `/v1/audio/transcriptions`（multipart 文件上传），返回 `CreateTranscriptionsResp`（含 text 字段）。
(source: `cozepy/audio/transcriptions/__init__.py` L14-L66)

F-cp-093: Transcriptions create 方法使用 `_try_fix_file(file)` 处理文件上传，支持 ogg、mp3、wav 格式，限制10MB、30分钟。
(source: `cozepy/audio/transcriptions/__init__.py` L3, L19-L35)

F-cp-094: Live 子模块包含 `LiveClient`/`AsyncLiveClient`，提供 `retrieve(live_id)` 方法 GET 到 `/v1/audio/live/{live_id}`，返回 `LiveInfo`（含 app_id、stream_infos 字段）。
(source: `cozepy/audio/live/__init__.py` L25-L64)

F-cp-095: Live 模块模型包括 `LiveType` 枚举（ORIGIN = "origin"、TRANSLATION = "translation"）、`StreamInfo`（stream_id、name、live_type）、`LiveInfo`（app_id、stream_infos: List[StreamInfo]）。
(source: `cozepy/audio/live/__init__.py` L9-L22)

F-cp-096: VoiceprintGroups 子模块包含 `VoiceprintGroupsClient`/`AsyncVoiceprintGroupsClient` 和 VoiceprintGroupsFeaturesClient/AsyncVoiceprintGroupsFeaturesClient，模型包括 VoicePrintGroup、VoicePrintGroupFeature、FeatureScore、SpeakerIdentifyResp、UserInfo，响应类型包括 Create/Update/DeleteVoicePrintGroup[Feature]Resp。
(source: `cozepy/__init__.py` L61-L79)

## 16. Files（文件）模块

F-cp-097: Files 模块包含 `FilesClient`（同步）和 `AsyncFilesClient`（异步）两个客户端类，模型 `File`。
(source: `cozepy/__init__.py` L310-L314)

F-cp-098: Files 模块定义了 `FileTypes` 类型别名和 `_try_fix_file()` 函数用于处理文件上传，被 transcriptions 等模块引用。
(source: `cozepy/audio/transcriptions/__init__.py` L3)

## 17. Datasets（数据集）模块

F-cp-099: Datasets 模块包含 `DatasetsClient`（同步）和 `AsyncDatasetsClient`（异步）两个客户端类。
(source: `cozepy/__init__.py` L253-L262)

F-cp-100: Datasets 模型包括 `Dataset`、`DocumentProgress`，枚举 `DatasetStatus`，响应类型包括 `CreateDatasetResp`、`UpdateDatasetRes`、`DeleteDatasetRes`。
(source: `cozepy/__init__.py` L255-L261)

F-cp-101: Datasets 子模块包含 documents（文档）和 images（图片）两个子客户端。
(source: `cozepy/__init__.py` L263-L284)

F-cp-102: Documents 子模块模型包括 Document、DocumentBase、DocumentSourceInfo，枚举 DocumentStatus、DocumentFormatType、DocumentSourceType、DocumentUpdateType、DocumentChunkStrategy，模型 DocumentUpdateRule，响应类型包括 UpdateDocumentRes、DeleteDocumentRes。
(source: `cozepy/__init__.py` L263-L277)

F-cp-103: Images 子模块模型包括 Photo，枚举 PhotoStatus，响应类型 UpdateImageRes。
(source: `cozepy/__init__.py` L278-L283)

## 18. Knowledge（知识库）模块（已废弃）

F-cp-104: Knowledge 模块包含 `KnowledgeClient`（同步）和 `AsyncKnowledgeClient`（异步），被标记为 deprecated，建议使用 datasets 模块。
(source: `cozepy/knowledge/__init__.py`, `cozepy/coze.py` L116-L127; 导出见 `cozepy/__init__.py` L321-L328)

F-cp-105: Knowledge 子模块包含 documents 子客户端（DocumentsClient/AsyncDocumentsClient）。
(source: `cozepy/__init__.py` L325-L328)

## 19. Workspaces（工作空间）模块

F-cp-106: Workspaces 模块包含 `WorkspacesClient`（同步）和 `AsyncWorkspacesClient`（异步）两个客户端类。
(source: `cozepy/__init__.py` L511-L517)

F-cp-107: Workspaces 模型为 `Workspace`，枚举 `WorkspaceRoleType`、`WorkspaceType`。
(source: `cozepy/__init__.py` L513-L516)

F-cp-108: Workspaces 子模块包含 members（成员）子客户端，模型 WorkspaceMember，响应类型 CreateWorkspaceMemberResp、DeleteWorkspaceMemberResp。
(source: `cozepy/__init__.py` L518-L524)

## 20. 工具函数

F-cp-109: `remove_url_trailing_slash(url)` 函数用于移除 URL 末尾的斜杠。
(source: `cozepy/util.py`, 引用见 `cozepy/coze.py` L7, L41; `cozepy/audio/rooms/__init__.py` L7, L86)

F-cp-110: `http_base_url_to_ws(url)` 函数将 HTTP URL 转换为 WebSocket URL（http→ws, https→wss）。
(source: `cozepy/util.py`)

F-cp-111: `base64_encode_string(s)` 函数对字符串进行 base64 编码。
(source: `cozepy/util.py`)

F-cp-112: `gen_s256_code_challenge(code_verifier)` 函数生成 S256 代码挑战，用于 PKCE OAuth 流程。
(source: `cozepy/util.py`)

F-cp-113: `remove_none_values(d)` 函数从字典中移除值为 None 的键值对，在 RoomsClient.create() 和 WorkflowsChatClient._create() 等方法中被使用。
(source: `cozepy/audio/rooms/__init__.py` L7, L118; `cozepy/workflows/chat/__init__.py` L10, L109)

F-cp-114: `dump_exclude_none(obj)` 函数在序列化对象时排除 None 值，被 `InputAudioBufferAppendEvent._dump_without_delta()` 使用。
(source: `cozepy/util.py`; `cozepy/websockets/audio/transcriptions/__init__.py` L7, L56)

## 21. 模块组织结构

F-cp-115: `__init__.py` 的 `__all__` 列表包含 300+ 个公开导出符号，涵盖所有客户端类、模型类、枚举、异常、配置常量、工具函数。
(source: `cozepy/__init__.py` L526-L931)

F-cp-116: 包目录下包含 py.typed 文件，标记为 PEP 561 类型提示包。
(source: `cozepy/py.typed`)

F-cp-117: 除核心模块外，SDK 还包含以下子模块：api_apps（含 events）、apps（含 collaborators）、benefit_limitations、benefits、bill_tasks、connectors（含 bots）、enterprises（含 members、organizations）、folders、templates、users、variables。
(source: `cozepy/__init__.py` L1-L524)

F-cp-118: 所有服务客户端类均遵循同步/异步成对出现的模式：Sync 版本名称为 `XxxClient`，Async 版本名称为 `AsyncXxxClient`，均在 `__init__` 中接受 `base_url: str` 和 `requester: Requester` 两个参数。
(source: `cozepy/audio/rooms/__init__.py` L80-L87, L131-L138; `cozepy/audio/live/__init__.py` L25-L32, L46-L53; `cozepy/audio/transcriptions/__init__.py` L14-L17, L38-L45)

F-cp-119: WebSocket 子客户端采用 Build 模式：通过 `XxxBuildClient.create(on_event=...)` 方法创建实际的 WebSocket 客户端实例，BuildClient 持有 base_url 和 requester。
(source: `cozepy/websockets/audio/__init__.py` L12-L24, L32-L44; `cozepy/websockets/audio/speech/__init__.py` L203-L216, L278-L294)

F-cp-120: 所有客户端方法均接受 `**kwargs`，从中提取 `headers: Optional[dict]` 用于自定义请求头。
(source: `cozepy/audio/rooms/__init__.py` L98, L117; `cozepy/audio/live/__init__.py` L34, L42)
