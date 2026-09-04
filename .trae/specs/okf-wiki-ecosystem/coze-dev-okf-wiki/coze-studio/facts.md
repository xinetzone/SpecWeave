# coze-studio R阶段事实清单

> 采集时间：2026-08-23
> 源码路径：`d:/spaces/SpecWeave/external/libs/ai/coze-dev/coze-studio/`
> 采集策略：架构级分层抽样——关注结构、接口、模式，非逐行阅读
> 事实数量：115条可验证事实

---

## 一、项目总览（F-cs-001 ~ F-cs-010）

F-cs-001: 项目名称为 Coze Studio，定位是一站式 AI Agent 开发平台（all-in-one AI agent development tool）(source: `README.md` L18-20)

F-cs-002: 项目采用 Apache 2.0 许可证 (source: `README.md` L96-97, `frontend/apps/coze-studio/package.json` L7)

F-cs-003: README 标注 Go 版本要求 >= 1.23.4，go.mod 声明 go 1.24.0 (source: `README.md` L11, `backend/go.mod` L3)

F-cs-004: 后端使用 Go 语言 + Hertz HTTP 框架，遵循 DDD（领域驱动设计）分层架构 (source: `README.md` L27, `backend/go.mod` L33)

F-cs-005: 前端使用 React 18 + TypeScript，Rush.js 管理单仓库（monorepo）(source: `README.md` L27, `frontend/apps/coze-studio/package.json` L46-50)

F-cs-006: 最低系统要求：2核 CPU、4GB 内存，需预安装 Docker 和 Docker Compose (source: `README.md` L43-44)

F-cs-007: 支持 Docker Compose 一键部署（`make web`）和 Helm Chart 部署到 Kubernetes (source: `Makefile` L75-77, `helm/charts/opencoze/Chart.yaml` L1-24)

F-cs-008: 源自服务了数万企业和数百万开发者的"扣子开发平台"（Coze Development Platform），核心引擎完全开源 (source: `README.md` L25)

F-cs-009: Agent 和工作流运行时引擎使用 Eino 框架（cloudwego/eino v0.4.8）(source: `README.md` L129, `backend/go.mod` L20)

F-cs-010: 前端工作流画布编辑器使用 FlowGram 引擎（@flowgram.ai）(source: `README.md` L130, `rush.json` L94-99)

---

## 二、后端架构（F-cs-011 ~ F-cs-045）

F-cs-011: 后端入口文件 main.go 按顺序执行：setCrashOutput → loadEnv → setLogLevel → application.Init → startHttpServer (source: `backend/main.go` L19-156)

F-cs-012: HTTP 框架使用 cloudwego/hertz v0.10.2 (source: `backend/go.mod` L33)

F-cs-013: DDD 分层目录结构为：api/（接口层）、application/（应用层）、domain/（领域层）、infra/（基础设施层）、crossdomain/（跨域层）(source: `CLAUDE.md` L89-94, 目录结构)

F-cs-014: api/ 层包含 handler/coze/（请求处理器）、middleware/（中间件）、model/（请求/响应模型）、router/（路由注册）四个子目录 (source: 目录结构)

F-cs-015: application/ 层包含 20+ 应用服务模块：app、connector、conversation、knowledge、memory、modelmgr、openauth、permission、plugin、prompt、search、shortcutcmd、singleagent、template、upload、user、workflow、base (source: 目录结构)

F-cs-016: domain/ 层每个限界上下文包含 entity/（实体）、repository/（仓储接口+实现）、service/（领域服务）、internal/dal/（数据访问层，含 gen.go 代码生成和 query/）(source: `backend/domain/app/entity/app.go` L17-32, 目录结构)

F-cs-017: domain/ 层包含的限界上下文有：agent/singleagent、app、connector、conversation（agentrun/conversation/message）、datacopy、knowledge、memory（database/variables）、openauth、permission、plugin、prompt、search、shortcutcmd、template、upload、user、workflow (source: 目录结构)

F-cs-018: infra/ 层包含基础设施模块：cache、checkpoint、coderunner、document（messages2query/nl2sql/ocr/parser/progressbar/rerank/searchstore）、dynconf、embedding、es、eventbus、idgen、imagex、oceanbase、orm、rdb、sqlparser、sse、storage (source: 目录结构)

F-cs-019: crossdomain/ 层为每个领域定义 contract.go 接口和 impl/ 实现，包含 16 个跨域模块：agent、agentrun、app、connector、conversation、database、datacopy、knowledge、message、permission、plugin、search、upload、user、variables、workflow (source: 目录结构)

F-cs-020: crossdomain/agent/contract.go 定义 SingleAgent 接口，包含 StreamExecute、ObtainAgentByIdentity、GetSingleAgentDraft 三个方法 (source: `backend/crossdomain/agent/contract.go` L32-37)

F-cs-021: crossdomain 层使用 cloudwego/eino/schema 包的 StreamReader 和 Message 类型作为跨域通信模型 (source: `backend/crossdomain/agent/contract.go` L22, L34, L50-51)

F-cs-022: bizpkg/ 目录包含 config/（配置管理）、llm/modelbuilder/（LLM模型构建器）、fileutil/（文件工具）、debugutil/（调试工具）(source: 目录结构)

F-cs-023: pkg/ 通用工具包包含：ctxcache（上下文缓存）、envkey（环境变量键）、errorx/code（错误码注册）、execute（执行器）、goutil（Go工具）、hertzutil（Hertz工具）、i18n（国际化）、kvstore（KV存储）、lang（语言工具集：conv/crypto/maps/ptr/sets/signal/slices/sqlutil/ternary）、logs（日志）、saasapi、safego（安全goroutine）、sonic（JSON）、taskgroup（任务组）、urltobase64url (source: 目录结构)

F-cs-024: types/ 目录包含 consts/（常量）、errno/（错误码）、ddl/（DDL生成）(source: 目录结构)

F-cs-025: errno/ 目录为每个模块定义错误码文件：agent.go、app.go、connector.go、conversation.go、knowledge.go、memory.go、modelmgr.go、permission.go、plugin.go、prompt.go、search.go、shortcutcmd.go、upload.go、user.go、workflow.go (source: 目录结构)

F-cs-026: 代码由 hz（Hertz 代码生成工具）v0.9.7 生成，配置 handlerDir=api/handler, modelDir=api/model, routerDir=api/router (source: `backend/.hz` L1-6)

F-cs-027: 路由注册文件 register.go 注册生成的路由和静态文件路由 (source: `backend/api/router/register.go` L19-88)

F-cs-028: Coze API 路由文件 api.go 定义大量路由，覆盖 /api/conversation、/api/draftbot、/api/knowledge、/api/workflow、/api/passport、/api/playground、/api/resource、/api/upload、/api/plugin、/api/config、/api/memory 等 (source: `backend/api/router/coze/api.go` L19-1761)

F-cs-029: 中间件包含 7 个：host.go（主机/方案注入上下文）、i18n.go（国际化语言设置）、log.go（访问日志和LogID）、session.go（会话认证）、openapi_auth.go（OpenAPI认证）、request_inspector.go（请求检查）、ctx_cache.go（上下文缓存）(source: 目录结构)

F-cs-030: SessionAuthMW 中间件通过 Cookie 中的 SessionKey 验证会话，白名单路径为 /api/passport/web/email/login/ 和 /api/passport/web/email/register/v2/ (source: `backend/api/middleware/session.go` L37-40, L55-68)

F-cs-031: AdminAuthMW 中间件通过 AdminEmails 配置（来自 baseConf.AdminEmails 或环境变量 ALLOW_REGISTRATION_EMAIL）验证管理员权限 (source: `backend/api/middleware/session.go` L78-112)

F-cs-032: 错误码系统使用 code.Register() 注册，支持 WithAffectStability(bool) 标记是否影响稳定性 (source: `backend/types/errno/knowledge.go` L63-276)

F-cs-033: 知识库模块错误码范围为 105000000 ~ 105999999，定义了 38 个错误码（无效参数、权限、DB、SearchStore、Embedding、IDGen、MQ、重复、不存在、文档过大、解析失败、检索失败、NL2SQL失败等）(source: `backend/types/errno/knowledge.go` L21-61)

F-cs-034: 基础处理器 base.go 定义 invalidParam 和 internalError 响应函数 (source: `backend/api/handler/coze/base.go` L17-33)

F-cs-035: 日志中间件 log.go 记录访问日志并设置 LogID 到上下文 (source: `backend/api/middleware/log.go` L17-97)

F-cs-036: i18n 中间件 i18n.go 从请求头或参数中提取语言设置 (source: `backend/api/middleware/i18n.go` L17-53)

F-cs-037: host 中间件 host.go 将请求的 Host 和 Scheme 存入上下文 (source: `backend/api/middleware/host.go` L17-34)

F-cs-038: safego 包提供带 panic recovery 的安全 goroutine 启动方法 Go() (source: `backend/pkg/safego/safego.go` L17-31)

F-cs-039: errorx 包定义 StatusError 接口，支持错误码、键值对参数、堆栈信息 (source: `backend/pkg/errorx/error.go` L17-90)

F-cs-040: 应用初始化 application.go 按顺序初始化基础服务（infra、eventbus、modelMgr、connector、user、prompt、template、openAuth、upload、permission）→ 主要服务 → 复杂服务，并设置 crossdomain 默认实现 (source: `backend/application/application.go` L17-398)

F-cs-041: App 应用服务 app.go 包含项目创建、更新、删除、发布、复制等方法（文件长度 1443 行）(source: `backend/application/app/app.go` L17-1443)

F-cs-042: User 应用服务 user.go 包含注册、登录、登出、更新个人信息、验证会话等方法 (source: `backend/application/user/user.go` L17-352)

F-cs-043: 领域层 App 实体定义 APP、PublishRecord 等结构体 (source: `backend/domain/app/entity/app.go` L17-32)

F-cs-044: build.sh 是 Hertz 标准构建脚本，编译输出到 output/bin/hertz_service (source: `backend/build.sh` L1-6)

F-cs-045: 常量文件 consts.go 定义运行模式、数据库连接、缓存地址、SessionKey 等常量（146行）(source: `backend/types/consts/consts.go` L17-146)

---

## 三、前端架构（F-cs-046 ~ F-cs-070）

F-cs-046: Rush.js 版本为 5.147.1，pnpm 版本为 8.15.8 (source: `rush.json` L3-4)

F-cs-047: rush.json 声明 nodeSupportedVersionRange 为 ">=21"，但 .nvmrc 指定 lts/iron（Node 20.x）(source: `rush.json` L5, `.nvmrc` L1)

F-cs-048: Rush 项目目录深度限制：projectFolderMinDepth=3, projectFolderMaxDepth=6 (source: `rush.json` L6-7)

F-cs-049: Rush 配置 postRushInstall 钩子执行 scripts/hooks/post-rush-install.sh (source: `rush.json` L16)

F-cs-050: allowedProjectTags 包含团队标签（team-arch/team-builder/team-community/team-data/team-devops/team-automation/team-studio/team-qa/team-fullcode-app）、级别标签（level-1/2/3/4）和功能标签（rush-x/rush-tools/core/enabled-bundle-diff/phase-prebuild/channel-coze）(source: `rush.json` L21-41)

F-cs-051: 前端包按 4 级依赖层次组织：arch/（level-1 核心基础）、common/（level-2 共享组件）、agent-ide/workflow/studio/（level-3 功能域）、apps/coze-studio（level-4 主应用）(source: `CLAUDE.md` L76-84, 目录结构)

F-cs-052: 主应用包名为 @coze-studio/app，版本 0.0.1，私有包 (source: `frontend/apps/coze-studio/package.json` L1-4)

F-cs-053: 构建系统使用 Rsbuild（基于 Rspack）~1.1.0，构建命令设置 IS_OPEN_SOURCE=true 环境变量 (source: `frontend/apps/coze-studio/package.json` L12, L69)

F-cs-054: 前端核心依赖：react ~18.2.0、react-dom ~18.2.0、react-router-dom ^6.11.1、zustand ^4.4.7、react-error-boundary ^4.0.9 (source: `frontend/apps/coze-studio/package.json` L46-50)

F-cs-055: UI 框架使用 Semi Design（@coze-arch/coze-design 0.0.6-alpha.346d77）+ Tailwind CSS ~3.3.3 (source: `frontend/apps/coze-studio/package.json` L25, L77)

F-cs-056: 测试框架使用 Vitest ~3.0.5，支持覆盖率报告（@vitest/coverage-v8）(source: `frontend/apps/coze-studio/package.json` L75, L79)

F-cs-057: TypeScript 版本 ~5.8.2 (source: `frontend/apps/coze-studio/package.json` L78)

F-cs-058: 前端 Dockerfile 使用两阶段构建：node:22-alpine 构建阶段 → nginx:1.25-alpine 生产阶段 (source: `frontend/Dockerfile` L2, L40)

F-cs-059: 前端 Dockerfile 支持中国镜像加速（aliyun alpine mirror、npmmirror.com）(source: `frontend/Dockerfile` L7, L13)

F-cs-060: 前端 Docker 构建命令为 `rush build --to @coze-studio/app`，构建产物从 frontend/apps/coze-studio/dist 复制到 nginx 的 /usr/share/nginx/html (source: `frontend/Dockerfile` L37, L49)

F-cs-061: 前端开发服务器配置代理：/api 和 /v1 路径代理到 http://localhost:8888（后端服务）(source: `frontend/apps/coze-studio/rsbuild.config.ts` L29-42)

F-cs-062: HTML 标题设置为"扣子 Studio"（中文品牌名）(source: `frontend/apps/coze-studio/rsbuild.config.ts` L45)

F-cs-063: 源码构建配置 include 了 packages/ 目录、flags-devtool 以及 node_modules 中的 marked、@dagrejs、@tanstack（这些包含未降级的ES 2022语法）(source: `frontend/apps/coze-studio/rsbuild.config.ts` L107-112)

F-cs-064: 支持 decorators legacy 模式（用于 inversify 的 @injectable() 和 @inject 装饰器）(source: `frontend/apps/coze-studio/rsbuild.config.ts` L122-124)

F-cs-065: 代码分割策略：split-by-size，minSize 3MB，maxSize 6MB (source: `frontend/apps/coze-studio/rsbuild.config.ts` L127-131)

F-cs-066: packages/arch/ 目录包含 20+ 基础包：api-schema、bot-api、bot-env、bot-error、bot-flags、bot-hooks、bot-http、bot-space-api、bot-store、bot-tea、bot-typings、bot-utils、fetch-stream、hooks、i18n、idl、logger、pdfjs-shadow、report-events、report-tti、tea、tea-adapter、tea-interface、utils、web-context (source: 目录结构)

F-cs-067: infra/idl/ 目录包含完整的 Thrift IDL → TypeScript 代码生成工具链：idl-parser、idl2ts-cli、idl2ts-generator、idl2ts-helper、idl2ts-plugin、idl2ts-runtime (source: 目录结构)

F-cs-068: packages/workflow/ 目录包含工作流编辑器模块：base、nodes、render、sdk、history、test-run、variable、setters (source: 目录结构)

F-cs-069: packages/agent-ide/ 目录包含 Agent IDE 模块：context、entry、layout、navigate、prompt、tool、workflow、commons (source: 目录结构)

F-cs-070: config/ 目录包含共享配置包：eslint-config、postcss-config、rsbuild-config、stylelint-config、tailwind-config、ts-config、vitest-config (source: 目录结构)

---

## 四、IDL / API 契约层（F-cs-071 ~ F-cs-085）

F-cs-071: Thrift IDL 文件按业务域组织在 12 个子目录中：admin/、app/、conversation/、data/、marketplace/、passport/、permission/、playground/、plugin/、resource/、upload/、workflow/ (source: 目录结构)

F-cs-072: api.thrift 通过 include 引入各域的 thrift 文件，并使用 service extends 聚合定义 18 个服务 (source: `idl/api.thrift` L1-41)

F-cs-073: api.thrift 聚合的 18 个服务为：IntelligenceService、ConversationService、MessageService、AgentRunService、OpenAPIAuthService、MemoryService、PluginDevelopService、PublicProductService、DeveloperApiService、PlaygroundService、DatabaseService、ResourceService、PassportService、WorkflowService、KnowledgeService（映射为 DatasetService）、BotOpenApiService、UploadService、ConfigService (source: `idl/api.thrift` L24-41)

F-cs-074: base.thrift 定义 Base 请求基结构体（LogID、Caller、Addr、Client、TrafficEnv、Extra map）和 BaseResp 响应基结构体（StatusMessage、StatusCode i32、Extra map）(source: `idl/base.thrift` L5-23)

F-cs-075: base.thrift 定义 EmptyReq、EmptyData、EmptyResp、EmptyRpcReq（含 optional Base 字段号255）、EmptyRpcResp（含 optional BaseResp 字段号255）(source: `idl/base.thrift` L25-42)

F-cs-076: Thrift 命名空间配置：namespace py base、namespace go base/coze/passport等、namespace java com.bytedance.thrift.base (source: `idl/base.thrift` L1-3, `idl/passport/passport.thrift` L1)

F-cs-077: Passport 服务使用邮箱/密码认证，定义了注册（PassportWebEmailRegisterV2Post）、登录（PassportWebEmailLoginPost）、登出（PassportWebLogoutGet）、密码重置、账户信息查询、头像更新等接口 (source: `idl/passport/passport.thrift` L22-79)

F-cs-078: User 结构体中 user_id 字段使用 i64 类型并标注 (agw.js_conv="str", api.js_conv="true") 以确保 JS 端大数精度 (source: `idl/passport/passport.thrift` L9)

F-cs-079: IDL 中约定响应格式使用字段号 253 为 code（i32）、254 为 msg（string）(source: `idl/passport/passport.thrift` L32-33, L42-43, L55-56)

F-cs-080: app/ 子目录包含 bot_common.thrift、bot_open_api.thrift、developer_api.thrift、intelligence.thrift、project.thrift、publish.thrift、search.thrift、task.thrift 和 common_struct/ 子目录 (source: 目录结构)

F-cs-081: conversation/ 子目录包含 agentrun_service.thrift、common.thrift、conversation.thrift、conversation_service.thrift、message.thrift、message_service.thrift、run.thrift (source: 目录结构)

F-cs-082: data/ 子目录分为 database/（database_svc.thrift、table.thrift）、knowledge/（common/document/knowledge/knowledge_svc/review/slice）、variable/（kvmemory/project_memory/variable_svc）三个子域 (source: 目录结构)

F-cs-083: data/knowledge 子目录包含文档处理相关 IDL：common.thrift、document.thrift、knowledge.thrift、knowledge_svc.thrift、review.thrift、slice.thrift (source: 目录结构)

F-cs-084: workflow/ 子目录包含 workflow.thrift、workflow_svc.thrift、trace.thrift (source: 目录结构)

F-cs-085: 后端 handler 目录下的文件与 IDL 服务一一对应：agent_run_service.go、bot_open_api_service.go、config_service.go、conversation_service.go、database_service.go、developer_api_service.go、intelligence_service.go、knowledge_service.go、memory_service.go、message_service.go、open_apiauth_service.go、passport_service.go、playground_service.go、resource_service.go、upload_service.go、workflow_service.go (source: 目录结构)

---

## 五、基础设施与部署（F-cs-086 ~ F-cs-115）

F-cs-086: Docker Compose 定义 11 个服务：mysql、redis、elasticsearch、minio、etcd、milvus、nsqlookupd、nsqd、nsqadmin、coze-server、coze-web，使用 coze-network 桥接网络 (source: `docker/docker-compose.yml` L5-438)

F-cs-087: MySQL 服务使用 mysql:8.4.5 镜像，配置 utf8mb4 字符集和 utf8mb4_unicode_ci 排序规则，通过 Atlas CLI 进行 schema 迁移 (source: `docker/docker-compose.yml` L7-8, L26, L48-63)

F-cs-088: Redis 服务使用 bitnamilegacy/redis:8.0 镜像，默认禁用 AOF，配置 4 个 IO 线程，允许空密码 (source: `docker/docker-compose.yml` L84-94)

F-cs-089: Elasticsearch 服务使用 bitnamilegacy/elasticsearch:8.18.0 镜像，安装 analysis-smartcn 中文分词插件，自动初始化索引 schema (source: `docker/docker-compose.yml` L117-201)

F-cs-090: MinIO 服务使用 minio/minio:RELEASE.2025-06-13T11-33-47Z-cpuv1 镜像，默认创建 opencoze 和 milvus 两个 bucket，自动复制 default_icon 和 official_plugin_icon 资源 (source: `docker/docker-compose.yml` L204-242)

F-cs-091: etcd 服务使用 bitnamilegacy/etcd:3.5 镜像，配置 revision 自动压缩（保留1000修订版），配额 4GB，允许无认证访问 (source: `docker/docker-compose.yml` L257-290)

F-cs-092: Milvus 服务使用 milvusdb/milvus:v2.5.10 镜像，以 standalone 模式运行，依赖 etcd 和 MinIO，配置 seccomp:unconfined (source: `docker/docker-compose.yml` L293-334)

F-cs-093: NSQ 消息队列使用 nsqio/nsq:v1.2.1 镜像，包含 nsqlookupd（4160/4161端口）、nsqd（4150/4151端口）、nsqadmin（4171端口）三个组件 (source: `docker/docker-compose.yml` L336-383)

F-cs-094: coze-server 服务镜像为 cozedev/coze-studio-server:latest，命令为 /app/opencoze，挂载 .env 和 backend/conf 目录 (source: `docker/docker-compose.yml` L386-415)

F-cs-095: coze-web 服务镜像为 cozedev/coze-studio-web:latest，使用 Nginx 提供前端静态文件，端口映射 ${WEB_LISTEN_ADDR:-8888}:80 (source: `docker/docker-compose.yml` L418-434)

F-cs-096: 所有 Docker 服务均配置了 healthcheck（mysqladmin ping、redis-cli ping、curl ES:9200、mc ready、etcdctl endpoint health、curl milvus:9091/healthz、nsqd --version）(source: `docker/docker-compose.yml` L65-78, L108-113, L136-144, L244-252, L283-288, L319-324, L345-350, L365-370)

F-cs-097: 环境变量配置文件 .env.example 定义了 270+ 配置项，覆盖 Server、MySQL、Redis、Storage（minio/tos/s3）、Elasticsearch、EventBus、VectorStore、Embedding、Rerank、OCR、Parser、Model、注册控制、Plugin AES (source: `docker/.env.example` L1-273)

F-cs-098: Event Bus 支持 5 种消息中间件：nsq（默认）、kafka、rmq（RocketMQ）、pulsar、nats（支持JetStream）(source: `docker/.env.example` L81-111)

F-cs-099: Vector Store 支持 3 种向量数据库：milvus（默认）、vikingdb（火山引擎）、oceanbase (source: `docker/.env.example` L114-136)

F-cs-100: Storage 后端支持 3 种对象存储：minio（默认）、tos（火山引擎TOS）、s3（AWS S3）(source: `docker/.env.example` L46-70)

F-cs-101: Embedding 支持 5 种接入方式：ark（火山引擎，默认）、openai、ollama、gemini、http（自定义）(source: `docker/.env.example` L137-177)

F-cs-102: OCR 支持 ve（火山引擎OCR，默认）和 paddleocr 两种 (source: `docker/.env.example` L190-198)

F-cs-103: Document Parser 支持 builtin（内置，默认）和 paddleocr 两种 (source: `docker/.env.example` L200-204)

F-cs-104: Rerank 支持 vikingdb 和 rrf（Reciprocal Rank Fusion，默认）两种 (source: `docker/.env.example` L180-187)

F-cs-105: 后端 Dockerfile 使用两阶段构建：golang:1.24-alpine 构建阶段（编译 -ldflags="-s -w"）→ alpine:3.22.0 运行阶段 (source: `backend/Dockerfile` L2, L17, L21)

F-cs-106: 后端 Docker 运行时安装 Python 3 venv 及依赖：urllib3==1.26.16、h11==0.16.0、httpx==0.28.1、pillow==11.2.1、pdfplumber==0.11.7、python-docx==1.2.0、numpy==2.3.1 (source: `backend/Dockerfile` L33-43)

F-cs-107: 后端 Docker 安装 Deno 并运行 `deno run -A jsr:@langchain/pyodide-sandbox` 预初始化 Python 沙箱环境 (source: `backend/Dockerfile` L28-30)

F-cs-108: 后端 Docker 将 parse_pdf.py、parse_docx.py、sandbox.py 三个 Python 脚本复制到 /app/ 目录用于文档处理和代码沙箱 (source: `backend/Dockerfile` L50-52)

F-cs-109: 后端默认监听地址为 :8888，前端 Nginx 监听 80 端口 (source: `docker/.env.example` L2, `backend/Dockerfile` L72)

F-cs-110: Makefile 定义的主要 target 包括：debug（启动调试环境）、fe（构建前端）、server（构建运行后端）、build_server（构建后端二进制）、sync_db（同步数据库schema）、dump_db（导出数据库schema）、middleware（启动中间件Docker环境）、web（启动全栈Docker环境）、down（停止容器）、clean（清理容器和数据）、python（设置Python环境）、atlas-hash（重哈希迁移文件）、setup_es_index（设置ES索引）(source: `Makefile` L1-157)

F-cs-111: 用户注册控制：DISABLE_USER_REGISTRATION 可禁用注册，ALLOW_REGISTRATION_EMAIL 可设置邮箱白名单（逗号分隔）(source: `docker/.env.example` L260-262)

F-cs-112: Plugin OAuth 使用 AES 加密，定义三个密钥：PLUGIN_AES_AUTH_SECRET、PLUGIN_AES_STATE_SECRET、PLUGIN_AES_OAUTH_TOKEN_SECRET，密钥长度必须为 16/24/32 字节 (source: `docker/.env.example` L265-273)

F-cs-113: LLM 模型配置使用序号后缀模式（MODEL_PROTOCOL_0/MODEL_ID_0/MODEL_API_KEY_0 等），支持添加多个模型；内置 ChatModel 支持 openai、ark、deepseek、ollama、qwen、gemini 六种协议 (source: `docker/.env.example` L207-255)

F-cs-114: Helm Chart 名为 opencoze v0.0.1，appVersion 0.0.3，类型为 application；coze-server 使用 LoadBalancer Service 暴露 8888（HTTP）和 8889（MinIO代理）端口；支持 MySQL 和 OceanBase 切换（OceanBase 默认 enabled: false）(source: `helm/charts/opencoze/Chart.yaml` L1-24, `helm/charts/opencoze/values.yaml` L5-100)

F-cs-115: infra/ 层 searchstore（搜索存储）支持 4 种后端：elasticsearch、milvus、oceanbase、vikingdb，通过工厂模式注册 (source: 目录结构, `docker/.env.example` L114-128)

---

## 六、Go 依赖关键库（F-cs-116 ~ F-cs-125）

F-cs-116: ORM 使用 GORM（gorm.io/driver/mysql v1.5.7、gorm.io/driver/sqlite v1.4.3）(source: `backend/go.mod` L79-80)

F-cs-117: Redis 客户端使用 go-redis/v9 v9.7.3 (source: `backend/go.mod` L58)

F-cs-118: 对象存储客户端包含 minio-go/v7 v7.0.90、ve-tos-golang-sdk/v2 v2.7.17、aws-sdk-go-v2/service/s3 v1.84.1 (source: `backend/go.mod` L13-16, L49, L65)

F-cs-119: 向量数据库客户端使用 milvus-io/milvus/client/v2 (source: `backend/go.mod` L48)

F-cs-120: 消息队列客户端包含 nsqio/go-nsq v1.1.0、IBM/sarama v1.45.1（Kafka）、apache/rocketmq-client-go/v2 (source: `backend/go.mod` L9, L11, L52)

F-cs-121: Elasticsearch 客户端同时支持 v7（go-elasticsearch/v7 v7.17.10）和 v8（go-elasticsearch/v8 v8.19.0）(source: `backend/go.mod` L35-36)

F-cs-122: Eino 扩展库包含 ark、claude、deepseek、gemini、ollama、openai、qwen 七种模型接入 (source: `backend/go.mod` L21-31)

F-cs-123: JSON 序列化使用 bytedance/sonic v1.15.0（高性能JSON库）(source: `backend/go.mod` L19)

F-cs-124: 文档处理依赖：excelize/v2（XLSX）、tealeg/xlsx/v3、extrame/xls（旧版XLS）、pdfplumber（Python端PDF）、python-docx（Python端DOCX）、goldmark（Markdown）(source: `backend/go.mod` L37, L63, L68, L69)

F-cs-125: CORS 中间件使用 hertz-contrib/cors v0.1.0，SSE 使用 hertz-contrib/sse v0.1.0 (source: `backend/go.mod` L41-42)

---

## 事实统计

| 类别 | 事实数量 | 编号范围 |
|------|---------|---------|
| 项目总览 | 10 | F-cs-001 ~ F-cs-010 |
| 后端架构 | 35 | F-cs-011 ~ F-cs-045 |
| 前端架构 | 25 | F-cs-046 ~ F-cs-070 |
| IDL/API契约 | 15 | F-cs-071 ~ F-cs-085 |
| 基础设施/部署 | 30 | F-cs-086 ~ F-cs-115 |
| Go依赖库 | 10 | F-cs-116 ~ F-cs-125 |
| **合计** | **125** | |
