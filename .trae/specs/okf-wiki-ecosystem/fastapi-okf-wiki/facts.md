# FastAPI v0.141.1 源码事实清单

> 源码根目录：`external/libs/fastapi/fastapi/fastapi/`
> 事实格式：`F-XXX: [模块名] 事实描述（源码路径:行号范围）`
> 仅描述代码中客观存在的结构，不含推断性词汇。

## 1. `__init__.py` — 公开 API 导出列表

- F-001: [__init__] 定义 `__version__ = "0.141.1"`（__init__.py:3）
- F-002: [__init__] `from starlette import status as status` 重新导出 starlette.status（__init__.py:5）
- F-003: [__init__] 从 `.applications` 导入 `FastAPI`，从 `.background` 导入 `BackgroundTasks`，从 `.datastructures` 导入 `UploadFile`，从 `.exceptions` 导入 `HTTPException`、`WebSocketException`（__init__.py:7-11）
- F-004: [__init__] 从 `.param_functions` 导入 Body/Cookie/Depends/File/Form/Header/Path/Query/Security 九个函数（__init__.py:12-20）
- F-005: [__init__] 从 `.requests` 导入 `Request`，从 `.responses` 导入 `Response`，从 `.routing` 导入 `APIRouter`，从 `.websockets` 导入 `WebSocket`、`WebSocketDisconnect`（__init__.py:21-25）

## 2. `applications.py` — FastAPI 应用类

- F-006: [applications] 定义 `AppType = TypeVar("AppType", bound="FastAPI")`；`class FastAPI(Starlette)`（applications.py:39-42）
- F-007: [applications] `__init__` 关键字参数包含 debug/routes/title/summary/description/version/openapi_url/openapi_tags/servers/dependencies/default_response_class/redirect_slashes/docs_url/redoc_url/swagger_ui_oauth2_redirect_url/swagger_ui_init_oauth/middleware/exception_handlers/on_startup/on_shutdown/lifespan/terms_of_service/contact/license_info/openapi_prefix/root_path/root_path_in_servers/responses/callbacks/webhooks/deprecated/include_in_schema/swagger_ui_parameters/generate_unique_id_function/separate_input_output_schemas/openapi_external_docs/strict_content_type，以及 `**extra`（applications.py:58-872）
- F-008: [applications] `__init__` 中设置 `self.openapi_version = "3.1.0"`、`self.openapi_schema = None`、`self._openapi_routes_version = None`（applications.py:923-925）
- F-009: [applications] `__init__` 中 `self.webhooks = webhooks or routing.APIRouter()`；`self.dependency_overrides = {}`；`self.router = routing.APIRouter(...)`（applications.py:937-999）
- F-010: [applications] `__init__` 注册三个默认异常处理器：HTTPException→http_exception_handler、RequestValidationError→request_validation_exception_handler、WebSocketRequestValidationError→websocket_request_validation_exception_handler（applications.py:1003-1012）
- F-011: [applications] `build_middleware_stack` 构建顺序：ServerErrorMiddleware → self.user_middleware → ExceptionMiddleware → AsyncExitStackMiddleware → self.router，反向包裹（applications.py:1020-1068）
- F-012: [applications] `openapi()` 调用 `self.router._get_routes_version()`，当 `self.openapi_schema` 为空或版本不匹配时调用 `get_openapi(...)` 并缓存到 `self.openapi_schema`（applications.py:1070-1103）
- F-013: [applications] `setup()` 注册四个路由：openapi_url（JSONResponse）、docs_url（swagger_ui_html）、swagger_ui_oauth2_redirect_url（swagger_ui_redirect）、redoc_url（redoc_html），均 `include_in_schema=False`（applications.py:1105-1158）
- F-014: [applications] `__call__` 在 `self.root_path` 非空时设置 `scope["root_path"] = self.root_path`，再 await super().__call__（applications.py:1160-1163）
- F-015: [applications] `add_api_route(path, endpoint, *, response_model=Default(None), status_code, tags, dependencies, summary, description, response_description="Successful Response", responses, deprecated, methods, operation_id, response_model_include, response_model_exclude, response_model_by_alias=True, response_model_exclude_unset, response_model_exclude_defaults, response_model_exclude_none, include_in_schema=True, response_class=Default(JSONResponse), name, openapi_extra, generate_unique_id_function=Default(generate_unique_id))` 委托给 `self.router.add_api_route(...)`（applications.py:1165-1220）
- F-016: [applications] `frontend(path, *, directory, fallback="auto", check_dir="auto")` 调用 `routing._resolve_frontend_check_dir(...)` 后委托 `self.router.frontend(...)`（applications.py:1222-1299）
- F-017: [applications] 定义 `add_api_websocket_route(path, endpoint, name=None, *, dependencies=None)` 和 `websocket(path, name=None, *, dependencies=None)` 装饰器方法（applications.py:1361-1439）

## 3. `routing.py` — 路由与请求处理

- F-018: [routing] `request_response(func)` 是 Starlette 同名函数的修改副本，在内部 app 中建立两层 AsyncExitStack：`scope["fastapi_inner_astack"]`（request_stack）和 `scope["fastapi_function_astack"]`（function_stack），response 未 await 时抛 FastAPIError（routing.py:121-160）
- F-019: [routing] `websocket_session(func)` 同样设置 `fastapi_inner_astack` 和 `fastapi_function_astack`，包裹 `wrap_app_handling_exceptions`（routing.py:165-186）
- F-020: [routing] `serialize_response(*, field=None, response_content, include=None, exclude=None, by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False, is_coroutine=True, endpoint_ctx=None, dump_json=False)` 有 field 时调用 `field.validate`（协程在线程池执行），errors 非空抛 `ResponseValidationError`，按 dump_json 选择 `field.serialize_json` 或 `field.serialize`；无 field 时返回 `jsonable_encoder(response_content)`（routing.py:301-342）
- F-021: [routing] `run_endpoint_function(*, dependant, values, is_coroutine)` 断言 `dependant.call` 非空，协程直接 `await dependant.call(**values)`，非协程 `await run_in_threadpool(dependant.call, **values)`（routing.py:344-354）
- F-022: [routing] `get_request_handler(...)` 参数含 dependant/body_field/status_code/response_class/response_field/response_model_include/exclude/by_alias/exclude_unset/exclude_defaults/exclude_none/dependency_overrides_provider/embed_body_fields/strict_content_type/stream_item_field/is_json_stream，返回内部 `app(request)` 协程（routing.py:375-392）
- F-023: [routing] `get_request_handler` 内部通过 `lenient_issubclass(actual_response_class, EventSourceResponse)` 判断 `is_sse_stream`（routing.py:400）
- F-024: [routing] 请求体解析逻辑：is_body_form 时 `await request.form()` 并注册 `body.close` 回调；非 form 时读取 body_bytes，按 content-type 主类型 application 且子类型 json 或 +json 才解析 JSON；strict_content_type=True 时无 content-type 不解析 JSON（routing.py:426-473）
- F-025: [routing] SSE 流式分支：调用 `dependant.call(**values)` 得到生成器，通过 `anyio.create_memory_object_stream[bytes](max_buffer_size=1)` 和任务组（`_producer` 拉取并 `_serialize_sse_item`，`_keepalive_inserter` 在 `anyio.fail_after(_PING_INTERVAL)` 超时时发送 `KEEPALIVE_COMMENT`），返回 `StreamingResponse` media_type="text/event-stream"，设置 Cache-Control: no-cache 和 X-Accel-Buffering: no（routing.py:520-646）
- F-026: [routing] JSONL 流式分支：`is_json_stream` 为真时，每个 item 经 `_serialize_data(item) + b"\n"` 序列化，异步生成器调用 `anyio.sleep(0)` 以支持取消，返回 `StreamingResponse` media_type="application/jsonl"（routing.py:647-682）
- F-027: [routing] 非流式分支：调用 `run_endpoint_function`，返回 Response 实例直接使用（注入 background_tasks），否则经 `serialize_response` 序列化，dump_json 路径返回 `Response(content=content, media_type="application/json")`；状态码不允许 body 时设置 `response.body = b""`（routing.py:705-750）
- F-028: [routing] `get_websocket_app(dependant, dependency_overrides_provider=None, embed_body_fields=False)` 求解依赖，errors 非空抛 `WebSocketRequestValidationError`，然后 `await dependant.call(**solved_result.values)`（routing.py:764-798）
- F-029: [routing] `class APIWebSocketRoute(routing.WebSocketRoute)` 构造时调用 `_build_dependant_with_parameterless_dependencies`，并设置 `self.app = websocket_session(get_websocket_app(...))`；matches 时在 child_scope 写入 `route=self`（routing.py:801-837）
- F-030: [routing] `_populate_api_route_state(route, path, endpoint, *, ...)` 接收 response_model/status_code/tags/dependencies/summary/description/response_description/responses/deprecated/name/methods/operation_id/response_model_*/include_in_schema/response_class/dependency_overrides_provider/callbacks/openapi_extra/generate_unique_id_function/strict_content_type/stream_item_type，设置 route 全部属性；methods 为 None 时默认 `["GET"]`；description 从 `inspect.cleandoc(endpoint.__doc__)` 提取并按 `\f` 截断（routing.py:961-1037）
- F-031: [routing] `_populate_api_route_state` 中生成器端点检测：`_is_async_gen_callable` 或 `_is_gen_callable` 为真时，response_class 是 EventSourceResponse 子类则 `is_sse_stream=True`，是 DefaultPlaceholder 则 `is_json_stream=True`；返回注解经 `get_stream_item_type` 提取流式 item 类型（routing.py:1071-1098）
- F-032: [routing] `class APIRoute(routing.Route)` 声明类级注解 stream_item_type/response_model/summary/response_description/deprecated/operation_id/response_model_*/include_in_schema/response_class/dependency_overrides_provider/callbacks/openapi_extra/generate_unique_id_function/strict_content_type/tags/responses/unique_id/status_code/response_field/stream_item_field/dependencies/description/response_fields/dependant/_embed_body_fields/body_field/is_sse_stream/is_json_stream（routing.py:1126-1159）
- F-033: [routing] `APIRoute.__init__` 调用 `_populate_api_route_state` 后设置 `self.app = request_response(self.get_route_handler())`；`get_route_handler` 读取 `_effective_route_context_var` 并调用 `get_request_handler(...)`（routing.py:1161-1249）
- F-034: [routing] `class APIRouter(routing.Router)` `__init__` 关键字参数含 prefix/tags/dependencies/default_response_class/responses/callbacks/routes/redirect_slashes/default/dependency_overrides_provider/route_class(默认 APIRoute)/on_startup/on_shutdown/lifespan/deprecated/include_in_schema/generate_unique_id_function/strict_content_type（routing.py:2282-2519）
- F-035: [routing] `APIRouter.__init__` 中 lifespan 为 None 时使用 `_DefaultLifespan(self)`，asyncgen 函数经 `asynccontextmanager` 包装，普通 generator 经 `_wrap_gen_lifespan_context` 包装；初始化 `self._routes_version=0`、`self._low_priority_routes=[]`、`self._frontend_routes=None`（routing.py:2520-2568）
- F-036: [routing] `APIRouter.add_api_route(...)` 含 `route_class_override` 参数，使用 `route_class_override or self.route_class`；合并 self.responses/tags/dependencies/callbacks，`deprecated=deprecated or self.deprecated`，`include_in_schema=include_in_schema and self.include_in_schema`，创建 route 后 append 到 self.routes 并调用 `_mark_routes_changed()`（routing.py:2889-2971）
- F-037: [routing] `APIRouter.frontend(path, *, directory, fallback="auto", check_dir="auto")` 调用 `_resolve_frontend_check_dir` 和 `_normalize_frontend_path`，首次调用时创建 `_FrontendRouteGroup` 并加入 `_low_priority_routes`，然后调用 `add_frontend_route(...)`（routing.py:2630-2717）

## 4. `params.py` — 参数类定义

- F-038: [params] `class ParamTypes(Enum)` 成员 query/header/path/cookie，值均为字符串（params.py:19-23）
- F-039: [params] `class Param(FieldInfo)` 声明类属性 `in_: ParamTypes`；`__init__` 支持 default/default_factory/annotation/alias/alias_priority/validation_alias/serialization_alias/title/description/gt/ge/lt/le/min_length/max_length/pattern/regex/discriminator/strict/multiple_of/allow_inf_nan/max_digits/decimal_places/examples/example/openapi_examples/deprecated/include_in_schema/json_schema_extra 及 **extra（params.py:26-134）
- F-040: [params] `Param.__init__` 中 `example` 非 _Unset 时发出 `FastAPIDeprecationWarning`；`regex` 非空时同样发出弃用警告；kwargs["pattern"] = pattern or regex（params.py:74-127）
- F-041: [params] `class Path(Param)` 设置 `in_ = ParamTypes.path`，`__init__` 中断言 `default is ...`（"Path parameters cannot have a default value"）（params.py:137-218）
- F-042: [params] `class Query(Param)` 设置 `in_ = ParamTypes.query`，default 默认 Undefined（params.py:221-300）
- F-043: [params] `class Header(Param)` 设置 `in_ = ParamTypes.header`，独有参数 `convert_underscores: bool = True`，在 __init__ 中存为 `self.convert_underscores`（params.py:303-384）
- F-044: [params] `class Cookie(Param)` 设置 `in_ = ParamTypes.cookie`（params.py:387-466）
- F-045: [params] `class Body(FieldInfo)` 不继承 Param，独有 `embed: bool | None = None` 和 `media_type: str = "application/json"`；__init__ 结构与 Param 类似但无 in_（params.py:469-578）
- F-046: [params] `class Form(Body)` 默认 `media_type = "application/x-www-form-urlencoded"`，无 embed 参数（params.py:581-660）
- F-047: [params] `class File(Form)` 默认 `media_type = "multipart/form-data"`（params.py:663-742）
- F-048: [params] `@dataclass(frozen=True) class Depends` 字段 `dependency: Callable|None = None`、`use_cache: bool = True`、`scope: Literal["function","request"]|None = None`（params.py:745-749）
- F-049: [params] `@dataclass(frozen=True) class Security(Depends)` 新增字段 `scopes: Sequence[str] | None = None`（params.py:752-754）

## 5. `param_functions.py` — 参数工厂函数

- F-050: [param_functions] 定义 Path()/Query()/Header()/Cookie()/Body()/Form()/File()/Depends()/Security() 九个函数，每个函数返回对应 `params.*` 类实例（param_functions.py:13-2460）
- F-051: [param_functions] Path/Query/Header/Cookie/Body/Form/File 函数签名使用 `Annotated[..., Doc(...)]` 为每个参数附加文档字符串，部分参数附加 `deprecated(...)` 装饰器（param_functions.py:13-2280）
- F-052: [param_functions] `Depends(dependency=None, *, use_cache=True, scope=None)` 返回 `params.Depends(dependency=dependency, use_cache=use_cache, scope=scope)`（param_functions.py:2283-2369）
- F-053: [param_functions] `Security(dependency=None, *, scopes=None, use_cache=True)` 返回 `params.Security(dependency=dependency, scopes=scopes, use_cache=use_cache)`（param_functions.py:2372-2460）

## 6. `dependencies/models.py` — Dependant 模型

- F-054: [dependencies/models] `@dataclass(slots=True) class Dependant` 字段：path_params/query_params/header_params/cookie_params/body_params（均 list[ModelField]）、dependencies(list["Dependant"])、name、call、request_param_name、websocket_param_name、http_connection_param_name、response_param_name、background_tasks_param_name、security_scopes_param_name、own_oauth_scopes、parent_oauth_scopes、use_cache=True、path、scope（models.py:31-51）
- F-055: [dependencies/models] `_is_gen_callable`/`_is_async_gen_callable`/`_is_coroutine_callable` 均经 `@lru_cache(maxsize=4096)` 缓存，使用 `_CallIdentity`（按 `id(call)` 哈希和 `is` 比较）作为缓存键（models.py:58-226）
- F-056: [dependencies/models] `_get_computed_scope(*, dependant)`：dependant.scope 非空返回该值；否则 call 为生成器/异步生成器时返回 "request"；否则返回 None（models.py:229-234）

## 7. `dependencies/utils.py` — 依赖求解

- F-057: [dependencies/utils] `ensure_multipart_is_installed()` 尝试导入 `python_multipart.__version__`（断言 > "0.0.12"），失败时尝试 `multipart`，检测到错误包抛 RuntimeError（utils.py:103-129）
- F-058: [dependencies/utils] `get_dependant(*, path, call, name=None, own_oauth_scopes=None, parent_oauth_scopes=None, use_cache=True, scope=None)` 遍历 `get_typed_signature(call).parameters`，对每个参数调用 `analyze_param`；Depends 类型递归构建子 Dependant；非字段参数调 `add_non_field_param_to_dependency`；Body 加入 body_params，其余调 `add_param_to_fields`（utils.py:271-347）
- F-059: [dependencies/utils] `add_non_field_param_to_dependency(*, param_name, type_annotation, dependant)` 按 lenient_issubclass 依次识别 Request/WebSocket/HTTPConnection/Response/StarletteBackgroundTasks/SecurityScopes 并设置对应 param_name，返回 True；均不匹配返回 None（utils.py:350-371）
- F-060: [dependencies/utils] `@dataclass class ParamDetails` 字段 type_annotation/depends/field（utils.py:374-378）
- F-061: [dependencies/utils] `analyze_param(*, param_name, annotation, value, is_path_param) -> ParamDetails` 解析 Annotated[..., FieldInfo/Depends]；从默认值识别 Depends/FieldInfo；无显式注解时按规则自动推断：is_path_param→Path、UploadFile 注解→File、非标量→Body、标量→Query；Form 类型调用 ensure_multipart_is_installed（utils.py:381-547）
- F-062: [dependencies/utils] `add_param_to_fields(*, field, dependant)` 按 `field.field_info.in_` 分发到 path_params/query_params/header_params，最后 assert 为 cookie 并加入 cookie_params（utils.py:550-563）
- F-063: [dependencies/utils] `@dataclass class SolvedDependency` 字段 values/errors/background_tasks/response/dependency_cache（utils.py:577-583）
- F-064: [dependencies/utils] `async solve_dependencies(*, request, dependant, body=None, background_tasks=None, response=None, dependency_overrides_provider=None, dependency_cache=None, async_exit_stack, embed_body_fields, _uses_scopes_cache=None)` 递归求解子依赖（支持 dependency_overrides 替换），按 use_cache 和 `_get_cache_key` 缓存，生成器依赖按 scope（function→function_astack，request→request_astack）进入 AsyncExitStack，然后调用 request_params_to_args 求解 path/query/header/cookie，body_params 调 request_body_to_args，注入 Request/WebSocket/BackgroundTasks/Response/SecurityScopes（utils.py:586-731）
- F-065: [dependencies/utils] `request_params_to_args(fields, received_params)` 单字段 BaseModel 时展开为模型字段；Headers 类型按 convert_underscores 转换别名；序列类型在 ImmutableMultiDict/Headers 上调用 getlist；未在 fields 中出现的键透传到 params_to_process；返回 (values, errors)（utils.py:780-868）
- F-066: [dependencies/utils] `get_stream_item_type(annotation)` 检查 get_origin(annotation) 是否在 `_STREAM_ORIGINS` 中，是则返回第一个类型参数（无参数返回 Any），否则返回 None（utils.py:261-268）

## 8. `openapi/utils.py` — OpenAPI 生成

- F-067: [openapi/utils] `get_definitions`/`get_flat_models_from_fields`/`get_model_name_map`/`get_schema_from_model_field` 等从 `fastapi._compat` 导入（openapi/utils.py:10-17）
- F-068: [openapi/utils] `get_openapi_path(*, route, operation_ids, model_name_map, field_mapping, separate_input_output_schemas=True)` 返回 `tuple[dict, dict, dict]`（path/security_schemes/definitions）；遍历 route.methods，调用 `get_openapi_operation_metadata`、`_get_openapi_security_definitions`、`_get_openapi_operation_parameters`，METHODS_WITH_BODY 方法调用 `get_openapi_operation_request_body`，递归处理 callbacks（openapi/utils.py:311-402）
- F-069: [openapi/utils] `get_fields_from_routes(...)` 从路由收集 flat_params/body_field/response_field/stream_item_field/response_fields 等字段（openapi/utils.py:551-583）
- F-070: [openapi/utils] `get_openapi(*, title, version, openapi_version="3.1.0", summary=None, description=None, routes, webhooks=None, tags=None, servers=None, terms_of_service=None, contact=None, license_info=None, separate_input_output_schemas=True, external_docs=None)` 组装 info 字典，调用 get_fields_from_routes→get_flat_models_from_fields→get_model_name_map→get_definitions，遍历 routes 和 webhooks 调 get_openapi_path，最后返回 `jsonable_encoder(OpenAPI(**output), by_alias=True, exclude_none=True)`（openapi/utils.py:585-679）

## 9. `openapi/docs.py` — 文档 HTML

- F-071: [openapi/docs] `_html_safe_json(value)` 对 `json.dumps(value)` 结果替换 `<`→`\u003c`、`>`→`\u003e`、`&`→`\u0026`（docs.py:9-19）
- F-072: [openapi/docs] `swagger_ui_default_parameters` 字典含 dom_id="#swagger-ui"、layout="BaseLayout"、deepLinking=True、showExtensions=True、showCommonExtensions=True（docs.py:22-37）
- F-073: [openapi/docs] `get_swagger_ui_html(*, openapi_url, title, swagger_js_url=jsdelivr swagger-ui-dist@5 bundle, swagger_css_url=同版本 css, swagger_favicon_url=fastapi favicon, oauth2_redirect_url=None, init_oauth=None, swagger_ui_parameters=None)` 返回 HTMLResponse，合并默认参数后渲染 SwaggerUIBundle 初始化脚本（docs.py:40-194）
- F-074: [openapi/docs] `get_redoc_html(*, openapi_url, title, redoc_js_url=jsdelivr redoc@2 standalone, redoc_favicon_url=fastapi favicon, with_google_fonts=True)` 返回 HTMLResponse，渲染 `<redoc spec-url=...>`（docs.py:197-298）
- F-075: [openapi/docs] `get_swagger_ui_oauth2_redirect_html()` 返回内嵌 OAuth2 回调处理 JS 的 HTMLResponse（docs.py:301-389）

## 10. `openapi/models.py` — OpenAPI 模型

- F-076: [openapi/models] 文件定义 40 个类，包括 BaseModelWithConfig/Contact/License/Info/ServerVariable/Server/Reference/Discriminator/XML/ExternalDocumentation/Schema/Example/ParameterInType/Encoding/MediaType/ParameterBase/Parameter/Header/RequestBody/Link/Response/Operation/PathItem/SecuritySchemeType/SecurityBase/APIKeyIn/APIKey/HTTPBase/HTTPBearer/OAuthFlow*/OAuthFlows/OAuth2/OpenIdConnect/Components/Tag/OpenAPI（models.py:57-419）
- F-077: [openapi/models] `class Schema(BaseModelWithConfig)` 声明 JSON Schema 2020-12 核心词汇（$schema/$id/$ref/$defs/allOf/anyOf/oneOf/not/properties/items 等）、结构验证词汇（type/enum/const/multipleOf/maximum/minimum/maxLength/minLength/pattern/maxItems/required 等）、语义内容词汇（format/contentEncoding/contentMediaType/contentSchema）、元数据词汇（title/description/default/deprecated/readOnly/writeOnly/examples）以及 OpenAPI 3.1.0 的 discriminator/xml/externalDocs/example 字段（models.py:123-204）
- F-078: [openapi/models] `class Parameter(ParameterBase)` 新增 `name: str` 和 `in_: ParameterInType = Field(alias="in")`；`class Header(ParameterBase)` 为空类（models.py:258-264）
- F-079: [openapi/models] `class OpenAPI(BaseModelWithConfig)` 为顶层文档模型；`class Components(BaseModelWithConfig)` 包含 schemas/responses/parameters/securitySchemes/requestBases/headers 等字段（models.py:399-419）

## 11. `security/base.py` — 安全基类

- F-080: [security/base] 从 `fastapi.openapi.models` 导入 `SecurityBase as SecurityBaseModel`；`class SecurityBase` 声明类属性 `model: SecurityBaseModel` 和 `scheme_name: str`（base.py:1-6）

## 12. `security/http.py` — HTTP 安全

- F-081: [security/http] `class HTTPBasicCredentials(BaseModel)` 字段 `username: str`、`password: str`（http.py:16-26）
- F-082: [security/http] `class HTTPAuthorizationCredentials(BaseModel)` 字段 `scheme: str`、`credentials: str`（http.py:29-66）
- F-083: [security/http] `class HTTPBase(SecurityBase)` __init__ 接受 scheme/scheme_name/description/auto_error=True；方法 make_authenticate_headers 返回 `{"WWW-Authenticate": scheme.title()}`；make_not_authenticated_error 返回 401 HTTPException；`__call__(request)` 通过 get_authorization_scheme_param 提取凭证返回 HTTPAuthorizationCredentials（http.py:69-102）
- F-084: [security/http] `class HTTPBasic(HTTPBase)` model.scheme 固定 "basic"，__init__ 支持 realm；`__call__` 校验 scheme.lower()=="basic"，使用 b64decode 解析后按 `:` 分割 username/password（http.py:105-219）
- F-085: [security/http] `class HTTPBearer(HTTPBase)` __init__ 接受 bearerFormat/scheme_name/description/auto_error；`__call__` 校验 scheme.lower()=="bearer"（http.py:222-316）
- F-086: [security/http] `class HTTPDigest(HTTPBase)` model.scheme 固定 "digest"，`__call__` 校验 scheme.lower()=="digest"（http.py:319-417）

## 13. `security/oauth2.py` — OAuth2

- F-087: [security/oauth2] `class OAuth2PasswordRequestForm` 用 Annotated 声明 `grant_type: str|None = Form(pattern="^password$")`、`username: str = Form()`、`password: str = Form(json_schema_extra={"format":"password"})`、`scope: str = Form()`、`client_id: str|None = Form()`、`client_secret: str|None = Form()`（oauth2.py:59-327）
- F-088: [security/oauth2] `class OAuth2PasswordRequestFormStrict(OAuth2PasswordRequestForm)` 将 grant_type 改为无默认值的必填 `Form(pattern="^password$")`（oauth2.py:226-327）
- F-089: [security/oauth2] `class OAuth2(SecurityBase)` __init__ 接受 flows(默认 OAuthFlowsModel())/scheme_name/description/auto_error=True；make_not_authenticated_error 返回 401 带 `WWW-Authenticate: Bearer`；`__call__(request)` 返回 Authorization 头原值（oauth2.py:330-430）
- F-090: [security/oauth2] `class OAuth2PasswordBearer(OAuth2)` __init__ 接受 tokenUrl/scheme_name/scopes=None/description/auto_error=True/refreshUrl=None，构造 password flow dict 传入 super().__init__；`__call__` 校验 scheme.lower()=="bearer" 并返回 param（oauth2.py:433-544）

## 14. `security/utils.py` — 安全工具

- F-091: [security/utils] `get_authorization_scheme_param(authorization_header_value: str|None) -> tuple[str, str]`：空值返回 ("","")；否则按首个空格 partition，返回 (scheme, param.strip())（utils.py:1-7）

## 15. `middleware/cors.py` — CORS 中间件

- F-092: [middleware/cors] 单行模块：`from starlette.middleware.cors import CORSMiddleware as CORSMiddleware  # noqa`（cors.py:1）

## 16. `middleware/gzip.py` — GZip 中间件

- F-093: [middleware/gzip] 单行模块：`from starlette.middleware.gzip import GZipMiddleware as GZipMiddleware  # noqa`（gzip.py:1）

## 17. `middleware/wsgi.py` — WSGI 中间件

- F-094: [middleware/wsgi] 从 `starlette.middleware.wsgi` 导入 `WSGIMiddleware as WSGIMiddleware`，标注 `# pragma: no cover`（wsgi.py:1-3）

## 18. `responses.py` — 响应类

- F-095: [responses] 从 starlette.responses 重新导出 FileResponse/HTMLResponse/JSONResponse/PlainTextResponse/RedirectResponse/Response/StreamingResponse；从 fastapi.sse 重新导出 EventSourceResponse（responses.py:5-12）
- F-096: [responses] 模块级尝试 `importlib.import_module("ujson")` 和 `importlib.import_module("orjson")`，ModuleNotFoundError 时置 None（responses.py:27-36）
- F-097: [responses] `@deprecated(...) class UJSONResponse(JSONResponse)` 标记 FastAPIDeprecationWarning；render 方法断言 ujson 已安装，返回 `ujson.dumps(content, ensure_ascii=False).encode("utf-8")`（responses.py:39-66）
- F-098: [responses] `@deprecated(...) class ORJSONResponse(JSONResponse)` 标记 FastAPIDeprecationWarning；render 返回 `orjson.dumps(content, option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY)`（responses.py:69-98）

## 19. `requests.py` — 请求类

- F-099: [requests] 从 starlette.requests 重新导出 `HTTPConnection as HTTPConnection` 和 `Request as Request`（requests.py:1-2）

## 20. `exceptions.py` — 异常定义

- F-100: [exceptions] `class EndpointContext(TypedDict, total=False)` 字段 function/path/file/line（exceptions.py:10-14）
- F-101: [exceptions] `class HTTPException(StarletteHTTPException)` __init__(status_code: int, detail: Any = None, headers: Mapping[str,str]|None = None)，调用 super().__init__（exceptions.py:17-83）
- F-102: [exceptions] `class WebSocketException(StarletteWebSocketException)` __init__(code: int, reason: str|None = None)（exceptions.py:86-154）
- F-103: [exceptions] 模块级 `RequestErrorModel = create_model("Request")`、`WebSocketErrorModel = create_model("WebSocket")`（exceptions.py:157-158）
- F-104: [exceptions] `class FastAPIError(RuntimeError)`；`class DependencyScopeError(FastAPIError)`；`class PydanticV1NotSupportedError(FastAPIError)`（exceptions.py:161-171,246-249）
- F-105: [exceptions] `class ValidationException(Exception)` 含 _errors/endpoint_ctx 属性、errors() 方法、_format_endpoint_context() 方法、__str__() 方法；子类 `RequestValidationError`（额外 body 属性）、`WebSocketRequestValidationError`、`ResponseValidationError`（额外 body 属性）（exceptions.py:174-243）
- F-106: [exceptions] `class FastAPIDeprecationWarning(UserWarning)`（exceptions.py:252-256）

## 21. `encoders.py` — JSON 编码器

- F-107: [encoders] `ENCODERS_BY_TYPE: dict[type, Callable]` 注册类型→编码器映射，包含 bytes/Color/PyExtraColor/datetime.date/datetime.datetime/datetime.time/datetime.timedelta/Decimal/Enum/frozenset/deque/GeneratorType/IPv4Address/IPv4Interface/IPv4Network/IPv6*/NameEmail/Path/Pattern/SecretBytes/SecretStr/set/UUID/Url/AnyUrl（encoders.py:84-112）
- F-108: [encoders] `decimal_encoder(Decimal)` 根据 as_tuple().exponent 判断：int 类型且 >=0 返回 int，否则返回 float（encoders.py:59-81）
- F-109: [encoders] `generate_encoders_by_class_tuples(type_encoder_map)` 反转映射为 encoder→tuple(types)；模块级 `encoders_by_class_tuples = generate_encoders_by_class_tuples(ENCODERS_BY_TYPE)`（encoders.py:115-126）
- F-110: [encoders] `jsonable_encoder(obj, *, include=None, exclude=None, by_alias=True, exclude_unset=False, exclude_defaults=False, exclude_none=False, custom_encoder=None, sqlalchemy_safe=True)` 按顺序处理 custom_encoder、BaseModel（model_dump mode="json"）、dataclass、Enum、PurePath、原始类型、PydanticUndefinedType、dict、list/set/frozenset/GeneratorType/tuple/deque、ENCODERS_BY_TYPE/encoders_by_class_tuples；pydantic.v1 实例抛 PydanticV1NotSupportedError；兜底尝试 dict(obj) 和 vars(obj)（encoders.py:129-366）

## 22. `datastructures.py` — 数据结构

- F-111: [datastructures] 从 starlette.datastructures 重新导出 URL/Address/FormData/Headers/QueryParams/State，并导入 `UploadFile as StarletteUploadFile`（datastructures.py:12-18）
- F-112: [datastructures] `class UploadFile(StarletteUploadFile)` 声明类注解 file/filename/size/headers/content_type；提供 async write/read/seek/close（委托 super）；类方法 `_validate` 断言 isinstance(..., StarletteUploadFile)；`__get_pydantic_json_schema__` 返回 `{"type":"string","contentMediaType":"application/octet-stream"}`；`__get_pydantic_core_schema__` 调用 `with_info_plain_validator_function(cls._validate)`（datastructures.py:21-150）
- F-113: [datastructures] `class DefaultPlaceholder` 含 `value` 属性、`__bool__` 返回 bool(value)、`__eq__` 比较 value；`Default(value)` 函数返回 `DefaultPlaceholder(value)`；`_Unset = Default(None)`（datastructures.py:153-186）
- F-114: [datastructures] 该版本文件中不存在 StreamUploadFile 类和 _Wrapper 类（经全目录 grep 确认）（datastructures.py 全文）

## 23. `utils.py` — 通用工具

- F-115: [utils] `is_body_allowed_for_status_code(status_code)`：None/"default"/"1XX"/"2XX"/"3XX"/"4XX"/"5XX" 返回 True；int 状态码 <200 或属于 {204,205,304} 返回 False，其余返回 True（utils.py:26-40）
- F-116: [utils] `get_path_param_names(path)` 返回 `set(re.findall("{(.*?)}", path))`（utils.py:43-44）
- F-117: [utils] `create_model_field(name, type_, default=Undefined, field_info=None, alias=None, mode="validation")` 检测 pydantic.v1 抛 PydanticV1NotSupportedError；调用 `v2.ModelField(mode=mode, name=name, field_info=field_info)`；捕获 PydanticSchemaGenerationError 转 FastAPIError（utils.py:58-77）
- F-118: [utils] `generate_unique_id(route)` 返回 `re.sub(r"\W","_",f"{route.name}{route.path_format}") + "_" + list(route.methods)[0].lower()`（utils.py:95-100）
- F-119: [utils] `deep_dict_update(main_dict, update_dict)` 递归合并 dict，list 拼接，其余键覆盖（utils.py:103-118）
- F-120: [utils] `get_value_or_default(first_item, *extra_items)` 按优先级返回首个非 DefaultPlaceholder 项，否则返回 first_item（utils.py:121-136）

## 24. `websockets.py` — WebSocket

- F-121: [websockets] 从 starlette.websockets 重新导出 `WebSocket`、`WebSocketDisconnect`、`WebSocketState`（websockets.py:1-3）

## 25. `sse.py` — Server-Sent Events

- F-122: [sse] `_SSE_EVENT_SCHEMA` 字典定义 type=object，properties 含 data/event/id（string）和 retry（integer, minimum 0）（sse.py:9-17）
- F-123: [sse] `class EventSourceResponse(StreamingResponse)` 类属性 `media_type = "text/event-stream"`（sse.py:20-33）
- F-124: [sse] `class ServerSentEvent(BaseModel)` 字段 data(Any=None)/raw_data(str|None=None)/event(str|None，AfterValidator 校验单行)/id(str|None，AfterValidator 校验单行且无 null 字符)/retry(int|None，Field(ge=0))/comment(str|None)；model_validator(mode="after") 校验 data 与 raw_data 互斥（sse.py:52-156）
- F-125: [sse] `format_sse_event(*, data_str=None, event=None, id=None, retry=None, comment=None) -> bytes` 按 SSE 线格式拼装 comment(以 `: ` 前缀)/event/data/id/retry 行，末尾追加两个空行，以 `\n` 连接并 UTF-8 编码（sse.py:165-233）
- F-126: [sse] `KEEPALIVE_COMMENT = b": ping\n\n"`；`_PING_INTERVAL: float = 15.0`（sse.py:237-241）

## 26. `background.py` — 后台任务

- F-127: [background] `class BackgroundTasks(StarletteBackgroundTasks)` 重写 `add_task(func, *args, **kwargs)`，方法体直接 `return super().add_task(func, *args, **kwargs)`（background.py:11-61）

## 27. `testclient.py` — 测试客户端

- F-128: [testclient] 单行模块：`from starlette.testclient import TestClient as TestClient  # noqa`（testclient.py:1）

## 28. `concurrency.py` — 并发工具

- F-129: [concurrency] 从 starlette.concurrency 重新导出 iterate_in_threadpool/run_in_threadpool/run_until_first_complete；从 contextlib 导入 asynccontextmanager（concurrency.py:3-12）
- F-130: [concurrency] `@asynccontextmanager async def contextmanager_in_threadpool(cm: AbstractContextManager)` 使用 `CapacityLimiter(1)`，yield `await run_in_threadpool(cm.__enter__)`，异常和正常退出时均通过 `anyio.to_thread.run_sync(cm.__exit__, ..., limiter=exit_limiter)` 执行 __exit__（concurrency.py:17-41）

## 29. `_compat/` — Pydantic v2 兼容层

- F-131: [_compat/__init__] 从 `.shared` 导入 PYDANTIC_VERSION_MINOR_TUPLE/annotation_is_pydantic_v1/field_annotation_is_scalar/field_annotation_is_scalar_sequence/field_annotation_is_sequence/is_bytes_*/is_pydantic_v1_model_instance/is_uploadfile_*/lenient_issubclass/sequence_types/value_is_sequence；从 `.v2` 导入 ModelField/PydanticSchemaGenerationError/RequiredParam/Undefined/Url/copy_field_info/create_body_model/evaluate_forwardref/get_cached_model_fields/get_definitions/get_flat_models_from_fields/get_missing_field_error/get_model_name_map/get_schema_from_model_field/is_scalar_field/serialize_sequence_value/with_info_plain_validator_function（__init__.py:1-40）
- F-132: [_compat/v2] `RequiredParam = PydanticUndefined`；`Undefined = PydanticUndefined`（v2.py:39-40）
- F-133: [_compat/v2] `class ModelField` 含 field_info/name/mode/config 属性，alias/validation_alias/serialization_alias/default 只读属性；`__post_init__` 通过 asdict(field_info) 构造 Annotated 并创建 `TypeAdapter`；方法 validate（返回 (value, errors)）、serialize（dump_python）、serialize_json（dump_json 返回 bytes）、get_default、__hash__ 返回 id(self)（v2.py:114-244）
- F-134: [_compat/v2] `get_definitions(*, fields, model_name_map, separate_input_output_schemas=True)` 使用 `GenerateJsonSchema(ref_template=REF_TEMPLATE)`，按 mode 拆分 validation/serialization 字段，生成 flat model fields，调用 `schema_generator.generate_definitions(inputs=inputs)` 返回 (field_mapping, definitions)，并截断 description 中的 `\f` 之后内容（v2.py:285-346）
- F-135: [_compat/shared] `sequence_annotation_to_type` 映射 Sequence/list/tuple/set/frozenset/deque→list/list/tuple/set/frozenset/list；`sequence_types` 为其键元组（shared.py:34-43）
- F-136: [_compat/shared] `lenient_issubclass(cls, class_or_tuple)` try 中执行 isinstance(cls,type) and issubclass，捕获 TypeError：WithArgsTypes 实例返回 False，其余重新抛出（shared.py:47-55）
- F-137: [_compat/shared] 定义 field_annotation_is_scalar/field_annotation_is_scalar_sequence/field_annotation_is_sequence/is_bytes_or_nonable_bytes_annotation/is_bytes_sequence_annotation/is_uploadfile_or_nonable_uploadfile_annotation/is_uploadfile_sequence_annotation/is_pydantic_v1_model_instance/annotation_is_pydantic_v1 等类型判断函数（shared.py:58-210）

## 30. 补充事实（薄模块细节）

- F-138: [middleware/cors] 模块不含 `__all__` 定义，仅通过 `as CORSMiddleware` 别名重新导出 Starlette 类（cors.py:1）
- F-139: [middleware/cors] 文件无其他 import 语句、类定义或函数定义，整文件长度为 1 行（cors.py:1）
- F-140: [middleware/gzip] 模块仅含 `from starlette.middleware.gzip import GZipMiddleware as GZipMiddleware  # noqa`（gzip.py:1）
- F-141: [middleware/gzip] GZipMiddleware 类本身不在本模块定义，直接复用 starlette.middleware.gzip 中的实现（gzip.py:1）
- F-142: [middleware/wsgi] 导入语句跨多行用括号包裹，行尾标注 `# pragma: no cover # noqa`（wsgi.py:1-3）
- F-143: [middleware/wsgi] 模块无 `__all__` 定义，WSGIMiddleware 为唯一公开名称（wsgi.py:1-3）
- F-144: [security/base] 模块首行 `from fastapi.openapi.models import SecurityBase as SecurityBaseModel`（base.py:1）
- F-145: [security/base] `SecurityBase` 类无 `__init__` 方法，类体仅声明 `model: SecurityBaseModel` 和 `scheme_name: str` 两个类属性注解（base.py:4-6）
- F-146: [requests] 两行导入均带 `# noqa: F401` 注释以抑制未使用导入警告（requests.py:1-2）
- F-147: [requests] 模块从 starlette.requests 导入 HTTPConnection 和 Request 两个名称并以同名重新导出，无其他代码（requests.py:1-2）
- F-148: [testclient] 模块仅含 `from starlette.testclient import TestClient as TestClient  # noqa`（testclient.py:1）
- F-149: [testclient] TestClient 类实现位于 starlette.testclient，本模块不做子类化或扩展（testclient.py:1）
- F-150: [websockets] 模块重新导出三个名称：WebSocket、WebSocketDisconnect、WebSocketState，均来自 starlette.websockets（websockets.py:1-3）
- F-151: [websockets] 三行导入均带 `# noqa` 注释，模块无 `__all__` 定义（websockets.py:1-3）
- F-152: [background] 模块顶部从 typing_extensions 导入 `ParamSpec` 并定义 `P = ParamSpec("P")`；add_task 方法签名中 `*args: P.args`/`**kwargs: P.kwargs` 引用该 ParamSpec（background.py:6-8,40-53）
- F-153: [background] `BackgroundTasks` 类未新增字段或重写 __init__，仅重写 add_task 方法并为参数添加 `Annotated[..., Doc(...)]` 文档注解（background.py:11-61）
- F-154: [concurrency] 模块导入 `anyio.to_thread` 和 `anyio.CapacityLimiter`；contextmanager_in_threadpool 函数中调用 `anyio.to_thread.run_sync` 在线程池中执行同步上下文管理器的 __enter__/__exit__（concurrency.py:6-7,17-41）
- F-155: [_compat/__init__] 该文件是纯再导出模块，无任何函数或类定义，共 40 行 import 语句（__init__.py:1-40）
- F-156: [_compat/__init__] 从 `.v2` 导入的名称包括 ModelField/PydanticSchemaGenerationError/RequiredParam/Undefined/Url/copy_field_info/create_body_model/evaluate_forwardref/get_cached_model_fields/get_definitions/get_flat_models_from_fields/get_missing_field_error/get_model_name_map/get_schema_from_model_field/is_scalar_field/serialize_sequence_value/with_info_plain_validator_function（\_\_init\_\_.py:22-40）
- F-157: [security/utils] 模块无任何 import 语句，仅定义一个函数 `get_authorization_scheme_param`（utils.py:1-7）
- F-158: [security/utils] 函数内使用 `str.partition(" ")` 按第一个空格分割 Authorization 头值，对 param 调用 `.strip()`，空输入直接返回 `("", "")` 而非抛异常（utils.py:4-6）

---

**统计**：共 158 条事实，覆盖全部 29 个指定模块，每个模块不少于 3 条事实。
