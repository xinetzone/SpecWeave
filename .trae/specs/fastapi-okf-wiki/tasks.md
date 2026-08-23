# FastAPI OKF Wiki 教程 - 实施计划（分解与优先级任务列表）

## [x] Task 1: R阶段 - 源码深度阅读与事实采集
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 逐模块阅读 FastAPI v0.141.1 核心源码，提取编号事实清单
  - 源码路径：`external/libs/fastapi/fastapi/fastapi/`
  - 核心模块清单：
    - `__init__.py` — 公开 API 导出（25个符号）
    - `applications.py` — FastAPI 主类（继承 Starlette）、__init__参数、build_middleware_stack、openapi()、setup()、add_api_route、frontend()
    - `routing.py` — APIRouter、APIRoute、APIWebSocketRoute、get_request_handler、request_response、websocket_session、serialize_response、run_endpoint_function、_populate_api_route_state、SSE/JSONL流式响应
    - `params.py` — Path/Query/Header/Cookie/Body/Form/File/Depends/Security 参数类
    - `param_functions.py` — 参数装饰器函数
    - `dependencies/` — models.py(Dependant)、utils.py(solve_dependencies/get_dependant)
    - `openapi/` — utils.py(get_openapi)、docs.py(Swagger UI/ReDoc HTML)、models.py
    - `security/` — base.py、http.py(HTTPBasic/HTTPBearer)、oauth2.py(OAuth2)
    - `middleware/` — cors.py、gzip.py、wsgi.py、asyncexitstack.py
    - `responses.py`、`requests.py`、`exceptions.py`、`encoders.py`
    - `datastructures.py`(Default/DefaultPlaceholder/UploadFile)、`utils.py`
    - `websockets.py`、`sse.py`、`background.py`、`testclient.py`、`templating.py`、`staticfiles.py`、`concurrency.py`、`cli.py`
  - 所有事实编号 F-001 起，每条指向源码文件路径和行号范围
  - 事实中禁止出现"用于"/"目的是"/"设计为"等推断词
  - 输出到 `.trae/specs/fastapi-okf-wiki/facts.md`
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-1.1: facts.md 包含≥80条编号事实（F-001到F-08x）
  - `programmatic` TR-1.2: 每条事实包含源码文件路径引用
  - `programmatic` TR-1.3: 事实中无"用于"/"目的是"/"设计为"等推断性表述（Grep检查）
  - `programmatic` TR-1.4: 覆盖上述全部核心模块（每个模块至少3条事实）
- **Notes**: 可委派 subagent 并行阅读不同模块，但事实编号需统一管理

## [x] Task 2: I阶段 - 架构洞察与知识结构设计
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于事实清单，提炼 4-5 个核心洞察四元组（陈述+证据+反常识+行动）
  - 设计知识地图：文档分组（入门篇/核心机制篇/高级功能篇）、依赖关系、学习路径
  - 确定每个概念文档覆盖哪些 F-xxx 事实
  - 规划 references/ 信源文件清单（对应核心模块）
  - 规划 examples/ 示例文档清单
  - 输出到 `.trae/specs/fastapi-okf-wiki/insights.md`
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-2.1: 洞察四元组完整（陈述+证据+反常识+行动），≥4个
  - `human-judgement` TR-2.2: 知识地图有明确的入门→核心→高级学习路径
  - `programmatic` TR-2.3: 每个规划的概念文档关联至少5条F-xxx事实
  - `programmatic` TR-2.4: references/ 规划≥6个信源文件，examples/ 规划≥4个示例
- **Notes**: 洞察应聚焦 FastAPI 区别于其他框架的设计特征

## [x] Task 3: E阶段批次1 - 创建Bundle结构和references信源
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 创建目标目录 `projects/awesome-okf-xs/bundles/fastapi/fastapi/`
  - 创建子目录 concepts/、examples/、references/
  - 生成 references/ 信源登记文件（信源先行！）：
    - `applications.md` — FastAPI 类、__init__参数、方法签名
    - `routing.md` — APIRouter/APIRoute/APIWebSocketRoute、请求处理函数
    - `dependencies.md` — Dependant模型、solve_dependencies、get_dependant
    - `params.md` — 参数类和参数函数
    - `openapi.md` — get_openapi、docs HTML生成、OpenAPI模型
    - `security.md` — HTTPBasic/HTTPBearer/OAuth2/APIKey
    - `middleware-exceptions.md` — 中间件、异常处理、CORS
    - `responses-encoders.md` — Response类、jsonable_encoder、StreamingResponse
  - 生成 references/index.md（无frontmatter）
  - 每个信源文件包含：源码路径、版本、公开API清单（类名/方法签名）
- **Acceptance Criteria Addressed**: AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-3.1: references/ 目录包含≥6个信源 .md 文件 + index.md
  - `programmatic` TR-3.2: 每个信源文件 frontmatter 含 type/title/description/tags/generated/verified/status/stale_after/sources
  - `programmatic` TR-3.3: references/index.md 无 frontmatter
  - `programmatic` TR-3.4: 信源文件中列出的类名/函数名均来自 facts.md 事实

## [x] Task 4: E阶段批次2 - 入门与核心概念文档（≤7个）
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 生成 concepts/ 目录下入门和核心概念文档：
    - `00-introduction.md` — FastAPI简介、设计哲学、安装、与Flask/Django对比、Starlette/Pydantic基座
    - `01-application.md` — FastAPI类详解、初始化参数、生命周期(lifespan)、中间件栈构建、setup()文档路由
    - `02-routing-system.md` — APIRouter、路由装饰器(get/post/put/delete)、APIRoute、路由匹配、include_router、prefix/tags/dependencies
    - `03-path-operations.md` — 路径操作函数、请求处理流程(get_request_handler)、request_response包装、同步/异步端点、run_in_threadpool
    - `04-dependency-injection.md` — Depends、Dependant树、solve_dependencies、依赖缓存(yield)、依赖覆盖(dependency_overrides)、子依赖
    - `05-parameter-declaration.md` — Path/Query/Header/Cookie参数声明、验证约束(gt/lt/regex)、Annotated类型、默认值
    - `06-request-body.md` — Body/Form/File参数、Pydantic模型验证、嵌套模型、embed_body_fields、strict_content_type
  - 每个文档含 frontmatter、概述、分节内容、代码示例、相关概念链接
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-4.1: 7个概念文件存在，文件名 kebab-case 带数字前缀
  - `programmatic` TR-4.2: 每个文件 frontmatter 完整，sources 指向 references/ 下的信源
  - `programmatic` TR-4.3: 代码块标注语言（python/bash/yaml）
  - `human-judgement` TR-4.4: 内容基于 facts.md 事实，API调用与源码一致

## [x] Task 5: E阶段批次3 - 高级功能概念文档（≤7个）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 生成 concepts/ 目录下高级功能文档：
    - `07-response-model.md` — response_model、响应过滤(include/exclude)、response_model_by_alias、separate_input_output_schemas、Response/JSONResponse/ORJSONResponse
    - `08-openapi-generation.md` — get_openapi()、OpenAPI schema自动生成、operationId、tags、responses、callbacks/webhooks、Swagger UI/ReDoc集成
    - `09-security.md` — OAuth2PasswordBearer、HTTPBasic/HTTPBearer、APIKeyHeader/Cookie/Query、Security依赖、安全方案
    - `10-middleware-cors.md` — 中间件系统(BaseHTTPMiddleware)、CORSMiddleware、GZipMiddleware、WSGIMiddleware、AsyncExitStackMiddleware、build_middleware_stack
    - `11-exception-handling.md` — HTTPException、RequestValidationError、ResponseValidationError、异常处理器注册、exception_handlers字典
    - `12-streaming-websocket.md` — StreamingResponse、SSE(EventSourceResponse/ServerSentEvent)、JSONL流、WebSocket路由、WebSocketDisconnect
    - `13-testing-advanced.md` — TestClient、dependency_overrides测试、BackgroundTasks、UploadFile、静态文件/模板、CLI(fastapi dev/run)
  - 每个文档含 frontmatter、概述、分节内容、代码示例、相关概念链接
- **Acceptance Criteria Addressed**: AC-4, AC-5, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: 7个概念文件存在，编号 07-13
  - `programmatic` TR-5.2: 每个文件 frontmatter 完整，sources 指向 references/
  - `programmatic` TR-5.3: 代码块标注语言
  - `human-judgement` TR-5.4: 内容基于 facts.md 事实，API调用与源码一致

## [x] Task 6: E阶段批次4 - 示例文档和导航索引
- **Priority**: high
- **Depends On**: Task 5
- **Description**:
  - 生成 examples/ 目录下示例文档：
    - `01-basic-crud-api.md` — 完整CRUD API示例（路径操作+请求体+响应模型+错误处理）
    - `02-dependency-injection.md` — 依赖注入实战（数据库会话、认证依赖、yield依赖、依赖覆盖测试）
    - `03-security-oauth2.md` — OAuth2密码流完整示例（登录/token获取/安全端点）
    - `04-streaming-sse.md` — SSE流式响应和WebSocket双向通信示例
    - `05-middleware-testing.md` — 自定义中间件+CORS配置+TestClient测试示例
  - 生成 examples/index.md（无frontmatter）
  - 生成 concepts/index.md（无frontmatter，列出所有概念文档）
  - 最后生成根 index.md（含 okf_version: "0.2"，完整文档清单和学习路径）
  - 生成 log.md（记录创建日期 2026-08-23 和内容概要）
- **Acceptance Criteria Addressed**: AC-3, AC-4, AC-8
- **Test Requirements**:
  - `programmatic` TR-6.1: examples/ 包含≥4个示例文件 + index.md
  - `programmatic` TR-6.2: concepts/index.md、examples/index.md 无 frontmatter
  - `programmatic` TR-6.3: 根 index.md 含 `okf_version: "0.2"` frontmatter
  - `programmatic` TR-6.4: log.md 存在且包含 2026-08-23 日期条目
  - `human-judgement` TR-6.5: 根 index.md 完整列出所有文档并按学习路径分组

## [x] Task 7: V阶段 - 独立审查与修复
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 结构检查：bundle 目录结构完整，所有必需文件存在
  - Frontmatter 检查：每个非 index.md 文件有合法 YAML frontmatter，type 字段非空
  - 链接检查：所有 `/` 开头交叉链接目标文件存在
  - Grep API 验证：对文档中引用的每个 FastAPI 公开类名/函数名，在源码中 Grep 验证存在性
  - 代码示例检查：代码示例中的 API 调用与 facts.md 事实一致
  - Index 完整性检查：index.md 列出的文件全部存在，无遗漏
  - 输出检查报告，逐一修复发现的问题
- **Acceptance Criteria Addressed**: AC-5, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有非 index .md 文件包含可解析 frontmatter 且 type 非空
  - `programmatic` TR-7.2: 所有交叉链接目标存在（无死链）
  - `programmatic` TR-7.3: 文档中引用的 FastAPI 公开 API（类/函数）100%在源码中可 Grep 到定义
  - `programmatic` TR-7.4: index.md 列出的文件数与实际文件数一致
  - `human-judgement` TR-7.5: 代码示例可运行（语法正确，API用法正确）

## [x] Task 8: C阶段 - 模式萃取与沉淀
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 回顾 FastAPI OKF Wiki 生成流程的顺利点和问题点
  - 如有新的可复用模式（如 ASGI 框架源码分析模式），萃取到 patterns/ 目录
  - 更新 log.md 记录 V 阶段验证结果
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `human-judgement` TR-8.1: 流程回顾完成，经验教训记录
