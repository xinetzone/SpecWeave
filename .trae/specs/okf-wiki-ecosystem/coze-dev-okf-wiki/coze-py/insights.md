# coze-py 架构洞察（I阶段）

> 基于 R 阶段 120 条源码事实（F-cp-001~F-cp-120）提炼的核心架构洞察。

## 核心架构洞察

### I-cp-01：同步/异步双客户端对称架构
- **陈述**：SDK 采用严格的 Sync/Async 双轨对称设计——`Coze` 与 `AsyncCoze` 两个入口类、20 个服务模块每个都有 `XxxClient`/`AsyncXxxClient` 成对出现，构造参数和方法签名一一对应。
- **证据**：F-cp-020~F-cp-026（Coze/AsyncCoze 入口）、F-cp-118（成对模式）、F-cp-045/F-cp-055/F-cp-060/F-cp-068 等各模块客户端。
- **反常识**：不是通过基类继承或 mixin 实现代码复用，而是两套几乎平行的类层次——Sync 用 httpx.Client，Async 用 httpx.AsyncClient，共享 Requester 的请求逻辑但各自维护独立的 HTTP 客户端。这种"代码重复"换来了类型安全和零抽象开销。
- **行动**：学习时先掌握同步 API，异步版本方法名完全一致，只需在调用时加 `await` 并使用 `async for` 处理流。

### I-cp-02：懒加载 Property 服务组合模式
- **陈述**：`Coze`/`AsyncCoze` 主类通过 20 个 `@property` 懒加载属性按需创建子服务客户端，而非在 `__init__` 中一次性实例化所有服务。
- **证据**：F-cp-022/F-cp-026（20 个懒加载 property）。
- **反常识**：这不是简单的"组合优于继承"——每个 property 在首次访问时才 new 出对应的 XxxClient，意味着用户只用到 chat 和 bots 时，不会初始化 workflows/audio/websockets 等无关客户端，减少内存和导入开销。
- **行动**：理解 SDK 入口是"服务门户"而非"上帝对象"——它持有 auth 和 requester，按需组装子客户端。

### I-cp-03：SSE 流式事件驱动模型
- **陈述**：对话和工作流执行采用 Server-Sent Events (SSE) 流式响应，通过 `Stream[T]`/`AsyncStream[T]` 泛型迭代器暴露事件流，`ChatEventType`/`WorkflowEventType` 枚举定义事件类型，handler 函数解析 SSE data 字段。
- **证据**：F-cp-032~F-cp-035（Stream/AsyncStream）、F-cp-047/F-cp-065（事件枚举）、F-cp-054（_chat_stream_handler 复用）、F-cp-063~F-cp-064（WorkflowsChatClient.stream）。
- **反常识**：Workflow Chat 复用 Chat 的 `_chat_stream_handler`，说明工作流对话和 Bot 对话在流式协议层共享同一套 SSE 事件格式，而非独立的协议。
- **行动**：所有流式接口统一使用 `for event in stream:` 模式，通过 `event.event` 判断事件类型，`event.message`/`event.chat` 等获取数据。

### I-cp-04：WebSocket Build 模式与事件处理器
- **陈述**：WebSocket 实时通信采用 Builder 模式——`WebsocketsChatBuildClient.create(on_event=...)` 构建可调用客户端，配合继承 `AsyncWebsocketsChatEventHandler` 的事件处理器类，通过重写 `on_xxx` 回调方法处理事件；二进制音频数据自动 base64 编解码。
- **证据**：F-cp-072~F-cp-084（WebSocket 架构）、F-cp-119（Build 模式）、F-cp-082/F-cp-084（base64 编解码）。
- **反常识**：Build 模式的使用不是为了复杂对象构造，而是因为 WebSocket 连接需要先注册事件处理器再 `async with connect()` 建立连接，create() 返回的是可调用的 factory 对象，调用时才建立实际连接。
- **行动**：使用 WebSocket 时继承 EventHandler 基类重写回调，通过 BuildClient 创建客户端，`async with client() as ws:` 管理连接生命周期。

### I-cp-05：三种分页策略统一抽象
- **陈述**：SDK 统一抽象了三种分页模式——`NumberPaged`（页码分页）、`TokenPaged`（令牌分页）、`LastIDPaged`（最后ID分页），每种都有 Sync/Async 版本，支持 `for item in page:` 直接迭代和 `for page in page.iter_pages()` 按页迭代两种模式。
- **证据**：F-cp-029~F-cp-031（三种分页基类）。
- **反常识**：三种分页策略不是通过一个通用 Paginator 类参数化实现，而是三套独立的类层次，但对外暴露相同的迭代协议（`__iter__`/`__aiter__`/`iter_pages()`），用户代码可以无缝切换分页方式。
- **行动**：列表操作返回 Paged 对象时，直接 `for item in paged:` 遍历元素即可，无需手动处理分页；需要逐页处理时用 `iter_pages()`。

## 知识地图

```
coze-py 知识结构
├── references/（信源登记，5篇）
│   ├── coze-client.md      → Coze/AsyncCoze 入口、Requester、配置、版本
│   ├── auth-model.md       → Auth体系：TokenAuth/JWT/OAuth(App/Web/PKCE/Device)
│   ├── chat-workflow.md    → Chat/Workflow 流式对话、SSE事件、Message模型
│   ├── websockets-audio.md → WebSocket架构、Chat/Audio实时通信、EventHandler
│   └── data-pagination.md → 数据模型(CozeModel/DynamicStrEnum)、分页、文件/数据集
│
├── concepts/（概念文档，10篇，三批次）
│   ├── 入门篇（3篇）
│   │   ├── 00-overview-architecture.md  → 整体架构：Sync/Async双轨、懒加载服务组合、模块组织
│   │   ├── 01-auth-system.md            → 认证体系：PAT/JWT/OAuth四种模式
│   │   └── 02-client-init.md            → 客户端初始化：Coze()/AsyncCoze()、base_url、http_client配置
│   │
│   ├── 核心篇（4篇）
│   │   ├── 03-chat-streaming.md         → 对话与流式：ChatClient、SSE事件、ChatEventType、Message模型
│   │   ├── 04-bot-management.md         → Bot管理：CRUD、发布/下线、版本、协作者
│   │   ├── 05-workflows.md              → 工作流：运行、对话流、异步执行、中断恢复
│   │   └── 06-conversations.md          → 会话管理：创建/列表/删除、消息、反馈
│   │
│   └── 高级篇（3篇）
│   │   ├── 07-websockets-realtime.md    → WebSocket实时通信：Build模式、EventHandler、Chat/Audio WS
│   │   ├── 08-audio-voice.md            → 音频处理：TTS/语音识别/房间/直播/声纹
│   │   └── 09-pagination-resources.md   → 分页模式与资源管理：三种分页、文件/数据集/工作空间
│
└── examples/（实战示例，4篇）
    ├── basic-chat.md            → 基础对话：初始化→流式对话→事件处理
    ├── workflow-execution.md    → 工作流执行：同步/异步/流式/中断恢复
    ├── websocket-voice-chat.md  → WebSocket语音对话：EventHandler继承→音频流→实时对话
    └── oauth-pkce-auth.md       → OAuth PKCE认证：设备流程/Token管理
```
