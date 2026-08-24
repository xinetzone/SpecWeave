# FastAPI v0.141.1 架构洞察与 OKF Wiki 知识结构设计

> 基于 158 条源码事实（F-001 ~ F-158）提炼，所有洞察均引用具体事实编号，不含凭空推断。
> 源码根目录：`external/libs/fastapi/fastapi/fastapi/`

---

## 1. 核心洞察

### 洞察 1：双层 AsyncExitStack 是依赖注入生命周期的 ASGI 基石

- **陈述**：FastAPI 在 `request_response` 中建立 request 级（`fastapi_inner_astack`）和 function 级（`fastapi_function_astack`）两层 `AsyncExitStack`，将 `yield` 依赖的清理逻辑编织进 Starlette 的 ASGI 调用链，而非在端点函数返回后简单回调。
- **证据**：
  - F-018：`request_response` 内部建立两层 AsyncExitStack，分别绑定 `request_stack` 和 `function_stack`，response 未 await 时抛 FastAPIError
  - F-019：`websocket_session` 同样设置两层 stack 并包裹 `wrap_app_handling_exceptions`
  - F-064：`solve_dependencies` 中生成器依赖按 scope 进入对应 stack——`"function"` 进入 `function_astack`，`"request"` 进入 `request_astack`
  - F-056：`_get_computed_scope` 对生成器/异步生成器 callable 自动返回 `"request"`，其余返回 `None`（即 function 级）
  - F-048：`Depends` 数据类显式声明 `scope: Literal["function","request"]|None` 字段
  - F-011：中间件栈包含 `AsyncExitStackMiddleware`，位于 ExceptionMiddleware 与 router 之间
- **反常识**：多数框架的依赖注入是"调用前解析参数、返回后丢弃"的纯函数模型；但 FastAPI 的 `yield` 依赖需要在响应完全发送后才执行清理（如关闭数据库连接），因此必须侵入 ASGI 中间件层建立异步上下文管理器链。两层栈的区分更反直觉——request 级栈的生命周期跨越整个请求（含后台任务），而 function 级栈在端点返回时即关闭。
- **行动**：文档必须用序列图展示请求进入→request_stack 建立→function_stack 建立→端点执行→function_stack 关闭→响应发送→request_stack 关闭的完整时序；明确区分 `scope="request"` 与默认 `scope="function"` 的清理时机差异；解释为何 `yield` 依赖不能用普通 `return` 替代。

### 洞察 2：Param 继承 Pydantic FieldInfo 实现"声明即校验、校验即文档"

- **陈述**：FastAPI 的参数类（`Path`/`Query`/`Header`/`Cookie`）继承 Pydantic 的 `FieldInfo`，使参数默认值、校验约束、JSON Schema 元数据和 OpenAPI 文档生成共用同一个元数据对象，配合 `Annotated[..., Doc(...)]` 实现类型注解即文档。
- **证据**：
  - F-039：`class Param(FieldInfo)`，`__init__` 支持 default/alias/gt/ge/lt/le/min_length/max_length/pattern/examples/json_schema_extra 等全部 Pydantic 字段参数
  - F-041~F-044：`Path`/`Query`/`Header`/`Cookie` 均继承 `Param`，仅通过类属性 `in_` 区分参数位置
  - F-045：`Body(FieldInfo)` 不继承 `Param`（因为 body 没有 `in_` 位置语义），但同样复用 FieldInfo 元数据
  - F-046~F-047：`Form(Body)` 和 `File(Form)` 通过继承链复用 Body 的 embed/media_type 机制
  - F-133：`ModelField` 在 `__post_init__` 中通过 `asdict(field_info)` 构造 `Annotated` 并创建 Pydantic v2 的 `TypeAdapter`，validate/serialize/serialize_json 三个方法委托给 TypeAdapter
  - F-051：`param_functions` 中每个函数签名使用 `Annotated[..., Doc(...)]` 为参数附加文档字符串，部分参数附加 `deprecated(...)` 装饰器
  - F-061：`analyze_param` 解析 `Annotated[..., FieldInfo/Depends]`，无显式注解时按规则自动推断（路径参数→Path、UploadFile→File、非标量→Body、标量→Query）
- **反常识**：多数 Web 框架的参数校验和 API 文档是两套独立系统（如装饰器声明校验 + 手写 schema），开发者需要重复维护。FastAPI 让类型注解本身成为唯一真相源——一个 `Query(gt=0)` 同时是默认值声明、运行时校验器、OpenAPI schema 生成器和 IDE 类型提示。更反直觉的是，即使不写 `Query()`，FastAPI 也能根据参数类型自动推断参数位置（F-061）。
- **行动**：文档应以"声明一次，四处生效"为主线组织参数章节；强调 `Annotated` 写法是 v0.141 的推荐风格（F-051）；用对比表展示显式声明与自动推断（F-061）的等价关系；解释 `Body` 为何不继承 `Param`（位置语义差异）。

### 洞察 3：Dependant 树是递归求解的依赖图，缓存与覆盖按子树粒度运作

- **陈述**：`get_dependant` 为每个端点构建一棵 `Dependant` 树（子依赖嵌套在 `dependencies: list[Dependant]` 中），`solve_dependencies` 以后序递归求解整棵树，通过 `dependency_cache` 按 `use_cache` 去重，并支持 `dependency_overrides` 在任意节点替换子树。
- **证据**：
  - F-054：`Dependant` 数据类包含 `path_params`/`query_params`/`header_params`/`cookie_params`/`body_params` 五个参数列表和 `dependencies: list["Dependant"]` 子依赖树
  - F-058：`get_dependant` 遍历签名参数，对 `Depends` 类型递归调用自身构建子 `Dependant`，非字段参数调 `add_non_field_param_to_dependency`
  - F-064：`solve_dependencies` 是 async 递归函数，先求解子依赖（支持 `dependency_overrides` 替换），按 `use_cache` 和 `_get_cache_key` 缓存，再求解当前节点的 path/query/header/cookie/body 参数
  - F-063：`SolvedDependency` 聚合 values/errors/background_tasks/response/dependency_cache 五个求解结果
  - F-055：`_is_gen_callable`/`_is_async_gen_callable`/`_is_coroutine_callable` 均经 `@lru_cache(maxsize=4096)` 缓存，使用 `_CallIdentity`（按 `id(call)` 哈希）作为键
  - F-059：`add_non_field_param_to_dependency` 按类型依次识别 Request/WebSocket/HTTPConnection/Response/BackgroundTasks/SecurityScopes 并注入对应参数名
  - F-062：`add_param_to_fields` 按 `field.field_info.in_` 分发到 path_params/query_params/header_params/cookie_params
  - F-065：`request_params_to_args` 处理单字段 BaseModel 展开、Headers 下划线转换、序列类型 getlist、未声明键透传
- **反常识**：依赖注入常被简化理解为"字典查找单例"，但 FastAPI 的依赖是一棵树而非一个扁平字典。同一个依赖函数在不同子树中被多次引用时，`use_cache=True` 确保只执行一次（缓存键含 call/dependency/cache_key），但缓存粒度是请求级而非全局单例。`dependency_overrides` 替换发生在求解时的任意节点，不需要重建路由树——这使得测试替换极其轻量。
- **行动**：文档必须用树形图展示嵌套依赖的求解顺序（深度优先、后序）；用表格对比 `use_cache=True/False` 的行为差异；解释 `dependency_overrides` 的运行时替换机制（F-064）和 `dependency_overrides_provider` 的传递链（F-009 中 `self.dependency_overrides = {}`）；说明非字段参数（Request/Response/BackgroundTasks）的特殊注入路径（F-059）。

### 洞察 4：APIRouter 组合模式的合并语义有方向性，OR/AND/拼接各不相同

- **陈述**：`APIRouter` 通过 prefix/tags/dependencies/responses 的合并实现模块化路由组合，但各字段的合并操作符不同——tags/responses/dependencies/callbacks 做列表拼接，`deprecated` 用逻辑 OR，`include_in_schema` 用逻辑 AND，这种方向性使父路由配置能"向下传染"。
- **证据**：
  - F-034：`APIRouter(routing.Router)` `__init__` 接收 prefix/tags/dependencies/default_response_class/responses/callbacks/deprecated/include_in_schema 等组合参数
  - F-036：`add_api_route` 合并逻辑明确：`self.responses`/`tags`/`dependencies`/`callbacks` 与路由级参数合并；`deprecated=deprecated or self.deprecated`（OR）；`include_in_schema=include_in_schema and self.include_in_schema`（AND）；创建后调 `_mark_routes_changed()`
  - F-009：`FastAPI.__init__` 中 `self.router = routing.APIRouter(...)`、`self.webhooks = APIRouter()`，FastAPI 本身不直接持有路由列表而是委托给内部 APIRouter
  - F-015：`FastAPI.add_api_route` 直接委托给 `self.router.add_api_route(...)`
  - F-035：`APIRouter.__init__` 初始化 `self._routes_version=0`，`_DefaultLifespan(self)` 包装 lifespan，维护 `_low_priority_routes` 和 `_frontend_routes`
  - F-037：`frontend()` 方法首次调用创建 `_FrontendRouteGroup` 加入 `_low_priority_routes`，实现低优先级路由
- **反常识**：直觉认为 `include_router` 是简单的路由表复制，但实际上父路由的配置会以不同语义向下传播。最反直觉的是 `deprecated` 的 OR 语义——父路由标记 `deprecated=True` 后，所有子路由即使自身未标记废弃也会被标记为废弃；而 `include_in_schema` 的 AND 语义则相反——父路由设为 `False` 会隐藏整个子树，无论子路由如何设置。tags/dependencies/responses 的列表拼接则可能导致重复项。
- **行动**：文档必须用表格列出每个可合并字段的操作语义（拼接/OR/AND/覆盖）；用示例展示父级 `deprecated=True` 和 `include_in_schema=False` 的非直觉传播效果；解释 `_routes_version` 与 OpenAPI 缓存失效的关系（F-012、F-036）；说明 webhooks router 与主 router 的对等关系（F-009）。

### 洞察 5：OpenAPI schema 是路由状态的纯函数派生，带版本号增量缓存

- **陈述**：FastAPI 的 OpenAPI document 完全从路由列表和 Pydantic 模型自动推导，通过 `_routes_version` 版本号跟踪路由变更，仅在 schema 为空或版本不匹配时重新生成，实现"修改即更新"的声明式文档。
- **证据**：
  - F-008：`__init__` 设置 `self.openapi_version = "3.1.0"`、`self.openapi_schema = None`、`self._openapi_routes_version = None`
  - F-012：`openapi()` 调用 `self.router._get_routes_version()`，当 `openapi_schema` 为空或版本不匹配时调 `get_openapi(...)` 并缓存
  - F-036：`add_api_route` 创建路由后调用 `_mark_routes_changed()` 递增版本号
  - F-070：`get_openapi` 组装 info 字典后执行管线：`get_fields_from_routes`→`get_flat_models_from_fields`→`get_model_name_map`→`get_definitions`，遍历 routes 和 webhooks 调 `get_openapi_path`，最终 `jsonable_encoder(OpenAPI(**output))`
  - F-069：`get_fields_from_routes` 从每个路由收集 flat_params/body_field/response_field/stream_item_field/response_fields
  - F-068：`get_openapi_path` 遍历 route.methods，对 METHODS_WITH_BODY 方法生成 request_body，递归处理 callbacks，返回 (path, security_schemes, definitions)
  - F-134：`get_definitions` 使用 Pydantic v2 的 `GenerateJsonSchema(ref_template=REF_TEMPLATE)`，按 validation/serialization 模式拆分字段，截断 description 中 `\f` 之后内容
  - F-076~F-079：`openapi/models.py` 定义 40 个 Pydantic 模型类，`Schema` 类覆盖 JSON Schema 2020-12 全部核心词汇
  - F-013：`setup()` 注册 openapi_url/docs_url/redoc_url 等文档路由，均 `include_in_schema=False`
- **反常识**：OpenAPI 文档在传统框架中通常是手写 YAML 或通过装饰器附加元数据维护的静态资产，但在 FastAPI 中它是端点签名的"编译产物"——任何路由参数、response_model、状态码的修改都会自动反映到 schema 中。版本缓存机制更反直觉：添加/删除路由时 `_mark_routes_changed()` 递增版本号，但修改已有路由的处理函数不会触发版本变更（因为路由对象本身未增删）。
- **行动**：文档应以"schema 生成管线"为主线，用流程图展示 routes→fields→models→definitions→paths 的数据流；解释 `separate_input_output_schemas` 参数如何拆分输入/输出 schema（F-134）；说明 `_routes_version` 缓存的触发条件和失效边界；文档 UI 章节应覆盖 Swagger UI/ReDoc/OAuth2 redirect 三个内置路由（F-073~F-075）。

### 洞察 6：流式响应基于返回类型注解自动检测，SSE 用 anyio 内存流实现背压与保活

- **陈述**：FastAPI 通过检测端点是否为生成器函数及 `response_class` 类型自动选择 SSE 或 JSONL 流式模式，SSE 使用 `anyio.create_memory_object_stream(max_buffer_size=1)` 实现生产者-消费者背压，配合 15 秒超时的 keepalive 任务防止代理超时断开。
- **证据**：
  - F-031：`_populate_api_route_state` 中生成器端点检测——`_is_async_gen_callable` 或 `_is_gen_callable` 为真时，`response_class` 是 `EventSourceResponse` 子类则 `is_sse_stream=True`，是 `DefaultPlaceholder` 则 `is_json_stream=True`；返回注解经 `get_stream_item_type` 提取 item 类型
  - F-023：`get_request_handler` 通过 `lenient_issubclass(actual_response_class, EventSourceResponse)` 判断 `is_sse_stream`
  - F-025：SSE 流式分支——调用端点得到生成器，通过 `anyio.create_memory_object_stream[bytes](max_buffer_size=1)` 创建内存流，任务组中 `_producer` 拉取生成器并 `_serialize_sse_item`，`_keepalive_inserter` 在 `anyio.fail_after(_PING_INTERVAL)` 超时时发送 `KEEPALIVE_COMMENT`；返回 `StreamingResponse` media_type="text/event-stream"，设置 `Cache-Control: no-cache` 和 `X-Accel-Buffering: no`
  - F-026：JSONL 流式分支——`is_json_stream` 为真时每个 item 经 `_serialize_data(item) + b"\n"` 序列化，异步生成器调用 `anyio.sleep(0)` 支持取消，返回 media_type="application/jsonl"
  - F-066：`get_stream_item_type` 检查 `get_origin(annotation)` 是否在 `_STREAM_ORIGINS` 中，返回第一个类型参数
  - F-123：`EventSourceResponse(StreamingResponse)` 类属性 `media_type = "text/event-stream"`
  - F-124：`ServerSentEvent(BaseModel)` 字段 data/event/id/retry/comment，含 AfterValidator 校验和 data 与 raw_data 互斥校验
  - F-125：`format_sse_event` 按 SSE 线格式拼装 comment/event/data/id/retry 行，末尾追加两个空行
  - F-126：`KEEPALIVE_COMMENT = b": ping\n\n"`，`_PING_INTERVAL = 15.0`
- **反常识**：流式响应在大多数框架中需要显式返回 `StreamingResponse` 并手动管理迭代器，但 FastAPI 能从 `async def` 生成器端点 + 返回类型注解（如 `AsyncIterator[Item]`）自动推断流式模式，开发者无需直接构造 StreamingResponse。更反直觉的是 SSE 的背压实现——`max_buffer_size=1` 意味着生产者每次只能放一条消息，消费者未取走时生产者会被 anyio 自动暂停，这是无界队列的常见内存泄漏问题的内置防护。
- **行动**：文档应分三层组织流式章节：自动检测条件（F-031）、SSE 架构（F-025 的 anyio 任务组模型）、JSONL 模式（F-026）；用序列图展示 producer/consumer/keepalive 三个任务的协作；解释 `ServerSentEvent` 模型的校验规则（F-124）和线格式（F-125）；说明 15 秒 keepalive 的设计目的（防止反向代理超时）。

### 洞察 7：Pydantic v2 兼容层将类型系统抽象为 ModelField 协议，隔离核心与 Pydantic 版本

- **陈述**：FastAPI 通过 `_compat` 层将 Pydantic v2 的 `TypeAdapter` 包装为统一的 `ModelField` 接口，核心 routing/dependencies 代码只依赖 `ModelField.validate/serialize/serialize_json` 方法签名，不直接调用 Pydantic API，从而隔离框架与 Pydantic 版本差异。
- **证据**：
  - F-131：`_compat/__init__` 是纯再导出模块，从 `.shared` 导入类型判断函数，从 `.v2` 导入 ModelField/RequiredParam/Undefined/create_body_model/get_definitions 等
  - F-133：`class ModelField` 含 field_info/name/mode/config 属性，`__post_init__` 通过 `asdict(field_info)` 构造 Annotated 并创建 `TypeAdapter`；方法 validate 返回 (value, errors)、serialize 调 dump_python、serialize_json 返回 bytes
  - F-132：`RequiredParam = PydanticUndefined`，`Undefined = PydanticUndefined`，统一未定义值表示
  - F-134：`get_definitions` 使用 `GenerateJsonSchema(ref_template=REF_TEMPLATE)`，按 mode 拆分 validation/serialization 字段
  - F-117：`create_model_field` 检测 `pydantic.v1` 抛 `PydanticV1NotSupportedError`，捕获 `PydanticSchemaGenerationError` 转 `FastAPIError`
  - F-136：`lenient_issubclass` 对 `WithArgs` 类型（如 `List[int]`）返回 False 而非抛 TypeError
  - F-137：`_compat/shared` 定义 field_annotation_is_scalar/is_sequence/is_uploadfile_annotation 等类型判断函数，供依赖分析使用
  - F-104：`PydanticV1NotSupportedError(FastAPIError)` 显式声明不支持 Pydantic v1
- **反常识**：从 API 表面看 FastAPI 深度耦合 Pydantic（参数校验、模型序列化全部依赖它），但源码中实际有一层薄兼容层隔离——核心代码只认 `ModelField` 协议，Pydantic 版本升级只需修改 `_compat/v2.py`。更反直觉的是 `ModelField.validate` 返回 `(value, errors)` 元组而非抛异常，这是因为 FastAPI 需要聚合多个参数的校验错误后一次性返回 `RequestValidationError`，而非首个错误即中断。
- **行动**：文档应在参数声明章节解释 `ModelField` 作为内部桥接的角色，但将 `_compat` 目录标记为内部实现（非公开 API）；在响应模型章节说明 validate 返回 (value, errors) 而非抛异常的聚合校验设计；提醒用户 v0.141 已不支持 Pydantic v1（F-104、F-117）。

---

## 2. 知识地图与学习路径

### 阶段一：入门篇

#### 00-introduction.md — FastAPI 简介与公开 API 全景

- **覆盖事实**：F-001, F-002, F-003, F-004, F-005, F-006, F-095, F-128
- **核心内容要点**：
  1. 版本定位：`__version__ = "0.141.1"`（F-001），基于 Starlette 和 Pydantic v2 构建（F-006, F-132）
  2. 公开 API 全景：从 `__init__.py` 导出的核心类与函数——FastAPI/BackgroundTasks/UploadFile/HTTPException（F-003）、九个参数函数 Body/Cookie/Depends/File/Form/Header/Path/Query/Security（F-004）、Request/Response/APIRouter/WebSocket（F-005）
  3. Starlette 再导出策略：`status` 模块直接重新导出（F-002），Response/Request/WebSocket/TestClient/CORSMiddleware 等均从 starlette 再导出（F-095, F-128）
  4. 框架定位：`class FastAPI(Starlette)`（F-006），FastAPI 是 Starlette 的超集而非替代

#### 01-application.md — FastAPI 应用类与生命周期

- **覆盖事实**：F-007, F-008, F-009, F-010, F-011, F-012, F-013, F-014, F-015, F-016, F-017
- **核心内容要点**：
  1. 应用构造：`FastAPI.__init__` 接收 40+ 关键字参数（F-007），内部创建 `self.router = APIRouter(...)`、`self.webhooks = APIRouter()`、`self.dependency_overrides = {}`（F-009）
  2. 中间件栈构建顺序：ServerErrorMiddleware→user_middleware→ExceptionMiddleware→AsyncExitStackMiddleware→router，反向包裹（F-011）
  3. 默认异常处理器：HTTPException、RequestValidationError、WebSocketRequestValidationError 三个处理器在构造时注册（F-010）
  4. OpenAPI 缓存机制：`openapi_version="3.1.0"`，`openapi_schema` 基于 `_get_routes_version()` 懒加载缓存（F-008, F-012）
  5. 文档路由自动注册：`setup()` 注册 openapi_url/docs_url/redoc_url/swagger_ui_oauth2_redirect_url，均 `include_in_schema=False`（F-013）
  6. 路由委托：`add_api_route`/`websocket`/`frontend` 均委托给 `self.router`（F-015, F-016, F-017）

### 阶段二：核心机制篇

#### 02-routing-system.md — 路由系统与请求处理管线

- **覆盖事实**：F-018, F-019, F-029, F-032, F-033, F-034, F-035, F-036, F-037, F-116
- **核心内容要点**：
  1. `request_response` 双层 AsyncExitStack：request_stack（`fastapi_inner_astack`）和 function_stack（`fastapi_function_astack`）（F-018），WebSocket 会话同样设置两层栈（F-019）
  2. `APIRoute` 类结构：类级注解声明 response_model/dependant/body_field/response_field/is_sse_stream/is_json_stream 等全部路由状态（F-032），`__init__` 调 `_populate_api_route_state` 后设置 `self.app = request_response(self.get_route_handler())`（F-033）
  3. `APIRouter` 组合：`__init__` 接收 prefix/tags/dependencies/responses 等组合参数（F-034），`add_api_route` 合并 self 与路由级配置（F-036）
  4. 路由版本与生命周期：`_routes_version=0` 初始值，`_DefaultLifespan` 包装 lifespan，`_low_priority_routes`/`_frontend_routes` 支持前端路由（F-035, F-037）
  5. 路径参数提取：`get_path_param_names` 用正则 `{(.*?)}` 提取路径参数名集合（F-116）
  6. WebSocket 路由：`APIWebSocketRoute` 构造时构建 dependant，设置 `self.app = websocket_session(get_websocket_app(...))`（F-029）

#### 03-path-operations.md — 路径操作与端点执行

- **覆盖事实**：F-021, F-022, F-027, F-030, F-031, F-113, F-115, F-118, F-120, F-127
- **核心内容要点**：
  1. `get_request_handler` 工厂：接收 dependant/body_field/response_field/response_class/stream_item_field/is_json_stream 等参数，返回内部 `app(request)` 协程（F-022）
  2. 端点执行：`run_endpoint_function` 对协程直接 await，对同步函数调 `run_in_threadpool`（F-021）
  3. 路由状态填充：`_populate_api_route_state` 设置全部属性，methods 默认 `["GET"]`，description 从 `inspect.cleandoc(endpoint.__doc__)` 提取并按 `\f` 截断（F-030）
  4. 生成器端点自动检测：async gen/sync gen + EventSourceResponse→SSE，+ DefaultPlaceholder→JSONL，返回注解经 `get_stream_item_type` 提取 item 类型（F-031）
  5. 非流式响应处理：返回 Response 实例直接使用（注入 background_tasks），否则经 `serialize_response` 序列化；状态码不允许 body 时设 `response.body = b""`（F-027, F-115）
  6. DefaultPlaceholder 占位符：`Default(value)` 返回 `DefaultPlaceholder`，`get_value_or_default` 按优先级解析默认值链（F-113, F-120）
  7. 唯一 ID 生成：`generate_unique_id` 用正则将路由名和路径格式中非单词字符替换为下划线（F-118）
  8. BackgroundTasks：重写 `add_task` 委托 Starlette 实现，使用 ParamSpec 保留类型签名（F-127）

#### 04-dependency-injection.md — 依赖注入系统

- **覆盖事实**：F-048, F-049, F-054, F-055, F-056, F-058, F-059, F-060, F-063, F-064, F-065, F-130
- **核心内容要点**：
  1. `Depends`/`Security` 数据类：`Depends` 字段为 dependency/use_cache/scope（F-048），`Security` 继承 Depends 新增 scopes（F-049）
  2. Dependant 树结构：五类参数列表（path/query/header/cookie/body）+ dependencies 子依赖列表 + 各类特殊参数名 + use_cache/scope（F-054）
  3. 依赖树构建：`get_dependant` 遍历签名参数，Depends 类型递归构建子 Dependant，非字段参数调 `add_non_field_param_to_dependency`（F-058, F-059）
  4. 递归求解：`solve_dependencies` 后序递归求解子依赖，支持 dependency_overrides 替换，按 use_cache 缓存，生成器依赖按 scope 进入 AsyncExitStack（F-064）
  5. 可调用类型检测缓存：`_is_gen_callable`/`_is_async_gen_callable`/`_is_coroutine_callable` 经 `lru_cache(maxsize=4096)` 缓存，按 `id(call)` 哈希（F-055）
  6. scope 自动推断：生成器 callable 默认 scope="request"，其余默认 None（function 级）（F-056）
  7. 参数求解细节：`request_params_to_args` 处理 BaseModel 单字段展开、Headers 下划线转换、序列 getlist（F-065）；`ParamDetails` 封装 type_annotation/depends/field（F-060）
  8. 线程池上下文管理：`contextmanager_in_threadpool` 用 CapacityLimiter(1) 在线程池中执行同步上下文管理器（F-130）

#### 05-parameter-declaration.md — 参数声明与类型系统

- **覆盖事实**：F-038, F-039, F-040, F-041, F-042, F-043, F-044, F-045, F-050, F-051, F-061, F-062, F-117, F-132, F-133, F-135, F-136
- **核心内容要点**：
  1. 参数类型体系：`ParamTypes` 枚举 query/header/path/cookie（F-038），`Param(FieldInfo)` 基类携带 `in_` 类属性（F-039），四个子类 Path/Query/Header/Cookie 仅通过 `in_` 区分（F-041~F-044）
  2. Body 独立分支：`Body(FieldInfo)` 不继承 Param，独有 embed 和 media_type（F-045）；Form/File 继承 Body（F-046, F-047）
  3. 工厂函数与文档注解：九个工厂函数返回对应类实例（F-050），函数签名使用 `Annotated[..., Doc(...)]` 为每个参数附加文档（F-051）
  4. 参数分析：`analyze_param` 解析 Annotated 中的 FieldInfo/Depends，无显式注解时自动推断（path 参数→Path、UploadFile→File、非标量→Body、标量→Query）（F-061）
  5. 字段分发：`add_param_to_fields` 按 `field.field_info.in_` 分发到对应参数列表（F-062）
  6. ModelField 桥接：`create_model_field` 创建 v2.ModelField（F-117），ModelField 在 `__post_init__` 中构造 Annotated 并创建 TypeAdapter，提供 validate/serialize/serialize_json（F-133）
  7. 弃用警告：`example` 参数和 `regex` 参数均发出 FastAPIDeprecationWarning，regex 映射到 pattern（F-040）
  8. 兼容工具：`Undefined = PydanticUndefined`（F-132），`sequence_types` 元组和 `sequence_annotation_to_type` 映射（F-135），`lenient_issubclass` 安全处理泛型类型（F-136）

#### 06-request-body.md — 请求体与表单/文件处理

- **覆盖事实**：F-024, F-046, F-047, F-057, F-111, F-112, F-114
- **核心内容要点**：
  1. 请求体解析逻辑：is_body_form 时 `await request.form()` 并注册 body.close 回调；非 form 时读取 body_bytes，按 content-type 判断是否解析 JSON；strict_content_type=True 时无 content-type 不解析（F-024）
  2. Form 参数：`Form(Body)` 默认 media_type="application/x-www-form-urlencoded"，无 embed 参数（F-046）
  3. File 参数：`File(Form)` 默认 media_type="multipart/form-data"（F-047）
  4. multipart 依赖检测：`ensure_multipart_is_installed` 优先尝试 `python_multipart`（断言版本 > "0.0.12"），失败时尝试 `multipart`，检测到错误包抛 RuntimeError（F-057）
  5. UploadFile 增强：继承 StarletteUploadFile，声明类注解 file/filename/size/headers/content_type，提供 `__get_pydantic_json_schema__` 和 `__get_pydantic_core_schema__` 集成 Pydantic 校验（F-112）
  6. 数据结构再导出：URL/Address/FormData/Headers/QueryParams/State 从 starlette 再导出（F-111）
  7. 版本差异说明：v0.141 中不存在 StreamUploadFile 类和 _Wrapper 类（F-114）

### 阶段三：高级功能篇

#### 07-response-model.md — 响应模型与序列化

- **覆盖事实**：F-020, F-096, F-097, F-098, F-107, F-108, F-109, F-110, F-152, F-153
- **核心内容要点**：
  1. 响应序列化：`serialize_response` 有 field 时调 `field.validate`（协程在线程池执行），errors 非空抛 ResponseValidationError，按 dump_json 选择 serialize_json 或 serialize；无 field 时返回 `jsonable_encoder`（F-020）
  2. JSON 引擎可选：模块级尝试导入 ujson 和 orjson，失败时置 None（F-096）
  3. 弃用响应类：UJSONResponse 和 ORJSONResponse 均标记 `@deprecated`，render 方法分别调用对应库（F-097, F-098）
  4. 类型编码器注册表：`ENCODERS_BY_TYPE` 注册 bytes/datetime/Decimal/Enum/IPv4/UUID/SecretStr 等类型的编码器（F-107），Decimal 编码器按 exponent 判断返回 int 或 float（F-108）
  5. 编码器反转索引：`generate_encoders_by_class_tuples` 将 type→encoder 映射反转为 encoder→tuple(types)（F-109）
  6. jsonable_encoder 管线：按优先级处理 custom_encoder→BaseScript model_dump→dataclass→Enum→PurePath→原始类型→dict→list/set/序列→ENCODERS_BY_TYPE，兜底尝试 dict(obj)/vars(obj)，pydantic.v1 实例抛异常（F-110）
  7. BackgroundTasks 类型增强：使用 ParamSpec 保留 add_task 的参数类型，重写方法仅添加 Annotated 文档注解后委托 super（F-152, F-153）

#### 08-openapi-generation.md — OpenAPI 文档生成

- **覆盖事实**：F-067, F-068, F-069, F-070, F-071, F-072, F-073, F-074, F-075, F-076, F-077, F-078, F-079, F-119, F-134
- **核心内容要点**：
  1. 生成管线：`get_openapi` 组装 info→get_fields_from_routes→get_flat_models_from_fields→get_model_name_map→get_definitions→遍历 routes/webhooks 调 get_openapi_path→jsonable_encoder(OpenAPI)（F-070）
  2. 路径项生成：`get_openapi_path` 遍历 methods，调 metadata/security/parameters 生成，METHODS_WITH_BODY 方法生成 request_body，递归处理 callbacks（F-068）
  3. 字段收集：`get_fields_from_routes` 从路由收集 flat_params/body_field/response_field/stream_item_field/response_fields（F-069）
  4. Schema 定义生成：`get_definitions` 使用 GenerateJsonSchema，按 validation/serialization 模式拆分，截断 description 中 `\f` 后内容（F-134），核心工具从 `_compat` 导入（F-067）
  5. OpenAPI 模型层：40 个 Pydantic 模型类（F-076），Schema 类覆盖 JSON Schema 2020-12 全部核心/验证/语义/元数据词汇（F-077），Parameter 类用 `Field(alias="in")` 处理保留字（F-078），OpenAPI/Components 为顶层容器（F-079）
  6. 文档 UI：Swagger UI HTML 渲染（F-073）含默认参数（F-072）、ReDoc HTML（F-074）、OAuth2 redirect 页面（F-075），`_html_safe_json` 转义 `<>&` 防 XSS（F-071）
  7. 字典合并：`deep_dict_update` 递归合并 dict，list 拼接，其余键覆盖（F-119）

#### 09-security.md — 安全与认证

- **覆盖事实**：F-080, F-081, F-082, F-083, F-084, F-085, F-086, F-087, F-088, F-089, F-090, F-091
- **核心内容要点**：
  1. SecurityBase 基类：声明 `model: SecurityBaseModel` 和 `scheme_name: str` 两个类属性，无 `__init__`（F-080）
  2. HTTP 认证体系：HTTPBase 提供 `__call__` 提取 Authorization 头并返回凭证（F-083）；HTTPBasic 解析 base64 编码的 username:password（F-084）；HTTPBearer 校验 bearer scheme（F-085）；HTTPDigest 校验 digest scheme（F-086）
  3. 凭证模型：HTTPBasicCredentials 含 username/password（F-081），HTTPAuthorizationCredentials 含 scheme/credentials（F-082）
  4. OAuth2 密码模式：OAuth2PasswordRequestForm 用 Annotated 声明 grant_type/username/password/scope/client_id/client_secret 六个 Form 字段（F-087），Strict 版本将 grant_type 改为必填（F-088）
  5. OAuth2 方案：OAuth2 基类返回 Authorization 头原值（F-089），OAuth2PasswordBearer 构造 password flow dict，校验 scheme.lower()=="bearer" 并返回 token（F-090）
  6. Authorization 头解析：`get_authorization_scheme_param` 用 `str.partition(" ")` 按首个空格分割，空输入返回 ("","") 而非抛异常（F-091）

#### 10-middleware-cors.md — 中间件与 CORS

- **覆盖事实**：F-092, F-093, F-094, F-138, F-139, F-140, F-141, F-142, F-143
- **核心内容要点**：
  1. CORS 中间件：单行 `from starlette.middleware.cors import CORSMiddleware` 再导出（F-092），无 `__all__` 定义，文件仅 1 行（F-138, F-139）
  2. GZip 中间件：同样单行再导出 Starlette 实现（F-093, F-140, F-141）
  3. WSGI 中间件：跨多行括号导入，标注 `# pragma: no cover # noqa`（F-094, F-142, F-143）
  4. 设计模式：FastAPI 中间件模块全部是薄再导出层，不在本地重写 Starlette 中间件，保持与上游同步
  5. 中间件栈位置：在 FastAPI.build_middleware_stack 中 user_middleware 位于 ServerErrorMiddleware 与 ExceptionMiddleware 之间（F-011 交叉引用）

#### 11-exception-handling.md — 异常处理与校验错误

- **覆盖事实**：F-100, F-101, F-102, F-103, F-104, F-105, F-106
- **核心内容要点**：
  1. 异常层级：`FastAPIError(RuntimeError)` 为框架错误基类，子类含 `DependencyScopeError` 和 `PydanticV1NotSupportedError`（F-104）
  2. HTTP 异常：`HTTPException(StarletteHTTPException)` 接收 status_code/detail/headers（F-101）；`WebSocketException` 接收 code/reason（F-102）
  3. 校验异常体系：`ValidationException(Exception)` 含 _errors/endpoint_ctx 属性和 errors() 方法（F-105）；三个子类——RequestValidationError（含 body）、WebSocketRequestValidationError、ResponseValidationError（含 body）
  4. 错误模型：模块级 `RequestErrorModel` 和 `WebSocketErrorModel` 经 `create_model` 动态创建（F-103）
  5. EndpointContext：TypedDict 含 function/path/file/line，用于错误信息中的端点定位（F-100）
  6. 弃用警告：`FastAPIDeprecationWarning(UserWarning)` 用于 example/regex/UJSONResponse/ORJSONResponse 等弃用标记（F-106, F-040, F-097, F-098）

#### 12-streaming-websocket.md — 流式响应与 WebSocket

- **覆盖事实**：F-023, F-025, F-026, F-028, F-066, F-121, F-122, F-123, F-124, F-125, F-126, F-150, F-151
- **核心内容要点**：
  1. SSE 检测与架构：`is_sse_stream` 通过 `lenient_issubclass(response_class, EventSourceResponse)` 判断（F-023）；SSE 分支用 anyio memory_object_stream(max_buffer_size=1) + 任务组（producer + keepalive_inserter）（F-025）
  2. JSONL 流式：is_json_stream 时每个 item 序列化为 `_serialize_data(item) + b"\n"`，异步生成器调 `anyio.sleep(0)` 支持取消，media_type="application/jsonl"（F-026）
  3. WebSocket 应用：`get_websocket_app` 求解依赖后 `await dependant.call(**values)`，errors 非空抛 WebSocketRequestValidationError（F-028）
  4. 流式 item 类型提取：`get_stream_item_type` 检查注解 origin 是否在 `_STREAM_ORIGINS` 中，返回首个类型参数（F-066）
  5. SSE 数据模型：`ServerSentEvent(BaseModel)` 含 data/event/id/retry/comment，event/id 经 AfterValidator 校验单行，data 与 raw_data 互斥（F-124）；`_SSE_EVENT_SCHEMA` 定义 JSON schema（F-122）
  6. SSE 线格式：`format_sse_event` 拼装 comment(`: `)/event/data/id/retry 行，末尾两个空行，UTF-8 编码（F-125）；`EventSourceResponse(StreamingResponse)` media_type="text/event-stream"（F-123）
  7. Keepalive：`KEEPALIVE_COMMENT = b": ping\n\n"`，`_PING_INTERVAL = 15.0`（F-126），超时时由 keepalive_inserter 发送
  8. WebSocket 再导出：WebSocket/WebSocketDisconnect/WebSocketState 从 starlette 再导出（F-121, F-150, F-151）

#### 13-testing-advanced.md — 测试与高级并发

- **覆盖事实**：F-021, F-129, F-130, F-137, F-146, F-147, F-148, F-149, F-154
- **核心内容要点**：
  1. TestClient：单行 `from starlette.testclient import TestClient` 再导出，不做子类化或扩展（F-128 交叉引用, F-148, F-149）
  2. 并发工具：从 starlette.concurrency 再导出 iterate_in_threadpool/run_in_threadpool/run_until_first_complete（F-129），从 contextlib 导入 asynccontextmanager
  3. 线程池上下文管理：`contextmanager_in_threadpool` 使用 anyio CapacityLimiter(1) 和 `anyio.to_thread.run_sync` 在线程池中执行同步上下文管理器的 `__enter__`/`__exit__`（F-130, F-154）
  4. 端点执行模型：`run_endpoint_function` 协程直接 await，同步函数 `run_in_threadpool`（F-021）
  5. 类型判断工具集：`_compat/shared` 提供 field_annotation_is_scalar/is_sequence/is_uploadfile_annotation/is_bytes_annotation 等类型判断函数（F-137）
  6. Request 再导出：HTTPConnection 和 Request 从 starlette.requests 再导出，带 `# noqa: F401`（F-146, F-147）

---

## 3. references 信源规划

以下 8 个信源文件按源码模块组织，覆盖全部 158 条事实。

| 信源文件 | 覆盖事实范围 | 事实数 | 内容说明 |
|---|---|---|---|
| **applications.md** | F-001~F-017, F-099, F-111, F-112, F-127, F-128, F-146~F-149, F-152, F-153 | 28 | `__init__.py` 公开 API 导出；`applications.py` FastAPI 类（构造、中间件栈、OpenAPI 缓存、setup、路由委托、frontend、websocket）；`requests.py` 再导出；`datastructures.py`（UploadFile、再导出）；`background.py` BackgroundTasks；`testclient.py` 再导出 |
| **routing.md** | F-018~F-037, F-066, F-115, F-116, F-118, F-120, F-121, F-129, F-130, F-150, F-151, F-154 | 31 | `routing.py` 全部内容（request_response/websocket_session 双栈、serialize_response、run_endpoint_function、get_request_handler、SSE/JSONL 流式分支、APIRoute/APIWebSocketRoute、APIRouter 组合、_populate_api_route_state、frontend）；`utils.py` 中路由相关工具（is_body_allowed_for_status_code、get_path_param_names、generate_unique_id、get_value_or_default）；`websockets.py` 再导出；`concurrency.py` 并发工具 |
| **dependencies.md** | F-054~F-065, F-117 | 13 | `dependencies/models.py` Dependant 数据类与可调用类型检测缓存；`dependencies/utils.py` 依赖求解（get_dependant、analyze_param、solve_dependencies、request_params_to_args、ParamDetails、SolvedDependency）；`utils.py` 中 create_model_field |
| **params.md** | F-038~F-053, F-131~F-137, F-155, F-156 | 25 | `params.py` 参数类定义（ParamTypes、Param、Path、Query、Header、Cookie、Body、Form、File、Depends、Security）；`param_functions.py` 九个工厂函数与 Annotated+Doc 文档注解；`_compat/` 全部内容（v2.ModelField、RequiredParam、get_definitions、shared 类型判断、lenient_issubclass、sequence_types、纯再导出 __init__） |
| **openapi.md** | F-067~F-079, F-119 | 14 | `openapi/utils.py`（get_openapi、get_openapi_path、get_fields_from_routes）；`openapi/docs.py`（Swagger UI/ReDoc/OAuth2 redirect HTML、_html_safe_json、默认参数）；`openapi/models.py` 40 个 OpenAPI 模型类（Schema、Parameter、OpenAPI、Components 等）；`utils.py` 中 deep_dict_update |
| **security.md** | F-080~F-091, F-144, F-145, F-157, F-158 | 16 | `security/base.py` SecurityBase；`security/http.py`（HTTPBase、HTTPBasic、HTTPBearer、HTTPDigest、凭证模型）；`security/oauth2.py`（OAuth2、OAuth2PasswordBearer、OAuth2PasswordRequestForm/Strict）；`security/utils.py` get_authorization_scheme_param |
| **middleware-exceptions.md** | F-092~F-094, F-100~F-106, F-138~F-143 | 16 | `middleware/cors.py`、`middleware/gzip.py`、`middleware/wsgi.py` 三个薄再导出模块及薄模块细节事实；`exceptions.py` 全部异常类（HTTPException、WebSocketException、FastAPIError 层级、ValidationException 层级、EndpointContext、FastAPIDeprecationWarning、动态错误模型） |
| **responses-encoders.md** | F-095~F-098, F-107~F-110, F-113, F-114, F-122~F-126 | 15 | `responses.py` 响应类再导出与 UJSONResponse/ORJSONResponse 弃用类；`encoders.py`（ENCODERS_BY_TYPE、decimal_encoder、jsonable_encoder 管线、encoders_by_class_tuples）；`datastructures.py` 中 DefaultPlaceholder 与 StreamUploadFile 不存在声明；`sse.py` 全部内容（EventSourceResponse、ServerSentEvent、format_sse_event、KEEPALIVE_COMMENT、_PING_INTERVAL） |

**覆盖统计**：28 + 31 + 13 + 25 + 14 + 16 + 16 + 15 = **158 条事实，覆盖率 100%**。

---

## 4. examples 示例规划

### 01-basic-crud-api.md — 基础 CRUD API

- **关联概念文档**：01-application、02-routing-system、03-path-operations、05-parameter-declaration、06-request-body、07-response-model
- **核心 API**：
  - `FastAPI()` 构造与 `@app.get/post/put/delete` 装饰器（F-015）
  - `Path`/`Query`/`Body` 参数声明与 `Annotated` 写法（F-039, F-041, F-042, F-045, F-051）
  - `response_model` 与 `status_code` 参数（F-030, F-015）
  - Pydantic BaseModel 作为请求体和响应模型（F-061 自动推断非标量→Body）
  - `jsonable_encoder` 的 BaseModel 处理路径（F-110）
- **示例内容**：内存数据库实现的 Item CRUD，展示路径参数、查询参数、请求体、响应模型过滤、状态码设置

### 02-dependency-injection.md — 依赖注入实践

- **关联概念文档**：04-dependency-injection、05-parameter-declaration
- **核心 API**：
  - `Depends(dependency, use_cache, scope)` 工厂函数（F-048, F-052）
  - `yield` 依赖与 AsyncExitStack 生命周期（F-064, F-056, F-018）
  - `dependency_overrides` 测试替换机制（F-064, F-009）
  - 类作为依赖（可调用对象）
  - 子依赖嵌套树与 `use_cache=True` 缓存去重（F-054, F-058, F-064）
- **示例内容**：数据库会话依赖（yield）、分页查询参数依赖、鉴权依赖嵌套、测试中 override 数据库为内存版本

### 03-security-oauth2.md — OAuth2 密码模式认证

- **关联概念文档**：09-security、04-dependency-injection
- **核心 API**：
  - `OAuth2PasswordBearer(tokenUrl=...)` 作为依赖（F-090）
  - `OAuth2PasswordRequestForm` 表单参数（F-087）
  - `HTTPBearer`/`HTTPBasic` 认证方案（F-084, F-085）
  - `Security(dependency, scopes=[...])` 与 SecurityScopes 注入（F-049, F-053, F-059）
  - `get_authorization_scheme_param` 凭证提取（F-091）
- **示例内容**：登录端点签发 token、受保护端点校验 bearer token、基于 scope 的权限控制、Security 依赖与 Depends 的区别

### 04-streaming-sse.md — 流式响应与 SSE

- **关联概念文档**：12-streaming-websocket、07-response-model
- **核心 API**：
  - `EventSourceResponse` 与 `ServerSentEvent` 模型（F-123, F-124）
  - `async def` 生成器端点自动检测为流式（F-031）
  - `AsyncIterator[Item]` 返回类型注解触发 JSONL 流式（F-031, F-066）
  - `StreamingResponse` 手动流式响应（F-095 再导出）
  - `format_sse_event` 线格式与 keepalive 机制（F-125, F-126）
- **示例内容**：实时日志 SSE 推送（async generator + EventSourceResponse）、JSONL 数据流（AsyncIterator 注解自动检测）、手动 StreamingResponse 分块传输、ServerSentEvent 模型校验

### 05-middleware-testing.md — 中间件与测试

- **关联概念文档**：10-middleware-cors、11-exception-handling、13-testing-advanced
- **核心 API**：
  - `CORSMiddleware` 添加与配置（F-092, F-011 中间件栈位置）
  - `HTTPException` 与 `RequestValidationError` 异常处理（F-101, F-105）
  - 自定义异常处理器注册（F-010 默认处理器模式）
  - `TestClient` 发送请求与断言（F-128, F-148）
  - `dependency_overrides` 在测试中的应用（F-009, F-064）
- **示例内容**：CORS 配置、自定义异常处理器返回统一错误格式、TestClient 测试端点（含异常和校验错误）、测试中替换认证依赖

---

## 附：事实覆盖矩阵

| 概念文档 | 覆盖事实数 | 主要事实范围 |
|---|---|---|
| 00-introduction | 8 | F-001~F-006, F-095, F-128 |
| 01-application | 11 | F-007~F-017 |
| 02-routing-system | 10 | F-018, F-019, F-029, F-032~F-037, F-116 |
| 03-path-operations | 10 | F-021, F-022, F-027, F-030, F-031, F-113, F-115, F-118, F-120, F-127 |
| 04-dependency-injection | 12 | F-048, F-049, F-054~F-056, F-058~F-060, F-063~F-065, F-130 |
| 05-parameter-declaration | 17 | F-038~F-045, F-050, F-051, F-061, F-062, F-117, F-132, F-133, F-135, F-136 |
| 06-request-body | 7 | F-024, F-046, F-047, F-057, F-111, F-112, F-114 |
| 07-response-model | 10 | F-020, F-096~F-098, F-107~F-110, F-152, F-153 |
| 08-openapi-generation | 15 | F-067~F-079, F-119, F-134 |
| 09-security | 12 | F-080~F-091 |
| 10-middleware-cors | 9 | F-092~F-094, F-138~F-143 |
| 11-exception-handling | 7 | F-100~F-106 |
| 12-streaming-websocket | 13 | F-023, F-025, F-026, F-028, F-066, F-121~F-126, F-150, F-151 |
| 13-testing-advanced | 9 | F-021, F-129, F-130, F-137, F-146~F-149, F-154 |
