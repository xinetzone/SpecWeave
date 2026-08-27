# coze-studio I阶段：架构洞察与知识地图

> 生成时间：2026-08-23
> 基于事实清单：`facts.md`（125条事实）
> 源码路径：`d:/spaces/SpecWeave/external/libs/ai/coze-dev/coze-studio/`

---

## 一、核心架构洞察（5条）

### I-cs-01：五层高内聚DDD架构，crossdomain层隔离领域耦合

Coze Studio后端采用严格的五层DDD分层：
- **api层**（接口层）：handler/coze处理HTTP请求，middleware提供横切关注点，model定义请求/响应结构，router由hz代码生成
- **application层**（应用层）：20+应用服务模块编排业务流程，application.go控制初始化顺序
- **domain层**（领域层）：每个限界上下文包含entity/repository/service/internal/dal四层结构，使用GORM gen.go代码生成
- **infra层**（基础设施层）：cache/orm/rdb/es/sse/storage/embedding等可插拔基础设施
- **crossdomain层**（跨域层）：这是本项目DDD的独特设计——通过contract.go接口定义跨域通信契约，impl/提供默认实现，使用Eino的StreamReader/Message作为跨域通信模型

crossdomain层的存在解决了经典DDD中domain层互相引用的耦合问题，使得不同限界上下文之间通过接口通信而非直接依赖实现。

```
HTTP Request
  → middleware (session/i18n/log/cors/cache)
    → handler/coze/
      → application/ (业务编排)
        → crossdomain/ contract.go (接口契约)
          → impl/ (默认实现，调用domain)
            → domain/ (entity/repository/service)
              → infra/ (DB/Cache/ES/Storage/Embedding)
```

### I-cs-02：前后端双代码生成，IDL驱动开发

Coze Studio采用IDL驱动开发模式：
- **后端**：hz工具（Hertz代码生成）从Thrift IDL自动生成router/handler/model，.hz配置文件指定目录
- **前端**：idl2ts工具链（idl-parser → idl2ts-generator → idl2ts-runtime）自动将Thrift IDL转换为TypeScript类型
- **IDL聚合**：api.thrift通过include+service extends聚合18个服务定义，base.thrift定义Base/BaseResp统一基类
- **数字精度处理**：Thrift i64字段标注agw.js_conv="str"和api.js_conv="true"确保JS端大数精度

18个服务覆盖：IntelligenceService（Agent智能）、Conversation/Message/AgentRunService（对话）、Workflow/KnowledgeService（工作流/知识库）、Plugin/PublicProduct/DeveloperApiService（插件/市场/开放API）、Passport/ConfigService（认证/配置）等。

### I-cs-03：全栈可插拔基础设施，云原生与私有化双部署

Coze Studio的基础设施层几乎所有组件都是可插拔的：
- **消息队列**：NSQ（默认）/ Kafka / RocketMQ / Pulsar / NATS（5选1）
- **向量数据库**：Milvus（默认）/ VikingDB（火山引擎）/ OceanBase（3选1）
- **对象存储**：MinIO（默认）/ TOS（火山引擎）/ AWS S3（3选1）
- **Embedding模型**：Ark（火山引擎，默认）/ OpenAI / Ollama / Gemini / HTTP自定义（5选1）
- **OCR**：火山引擎OCR（默认）/ PaddleOCR（2选1）
- **文档解析**：Builtin内置（默认）/ PaddleOCR（2选1）
- **Rerank**：VikingDB / RRF（默认）
- **LLM**：OpenAI/Ark/DeepSeek/Ollama/Qwen/Gemini（6种协议）

搜索存储（searchstore）通过工厂模式注册4种后端（ES/Milvus/OceanBase/VikingDB），实现统一接口。这种设计让平台既能运行在云环境（火山引擎全家桶），也能完全私有化部署（全开源组件栈）。

### I-cs-04：Rush.js四级包架构，Rsbuild高性能构建

前端采用Rush.js管理大型单仓库，四级包依赖层次严格：
- **Level 1 (arch/)**：20+核心基础包——api-schema/bot-http/bot-store/bot-hooks/bot-utils/idl/fetch-stream/hooks/i18n/logger/web-context等，不依赖业务
- **Level 2 (common/)**：共享组件库
- **Level 3 (feature domains)**：agent-ide/（Agent IDE：context/entry/layout/prompt/tool/workflow）、workflow/（工作流编辑器：base/nodes/render/sdk/history/variable）、studio/（Studio功能）
- **Level 4 (apps/)**：主应用@coze-studio/app，组合所有功能包

技术栈：React 18 + TypeScript 5.8 + Semi Design UI + Tailwind CSS 3 + Zustand状态管理 + React Router 6 + Rsbuild（Rspack）构建 + Vitest测试。Docker两阶段构建（node:22-alpine构建→nginx:1.25-alpine生产）。

### I-cs-05：11服务Docker Compose一键部署，Helm生产级K8s部署

本地开发/演示使用Docker Compose，包含完整的11个服务栈：
| 服务 | 镜像 | 端口 | 作用 |
|------|------|------|------|
| MySQL | mysql:8.4.5 | 3306 | 主数据存储，Atlas CLI迁移 |
| Redis | bitnamilegacy/redis:8.0 | 6379 | 缓存/会话，4 IO线程 |
| Elasticsearch | bitnamilegacy/elasticsearch:8.18.0 | 9200 | 全文检索，smartcn中文分词 |
| MinIO | minio/RELEASE.2025-06 | 9000/9001 | 对象存储，自动创建bucket |
| etcd | bitnamilegacy/etcd:3.5 | 2379 | Milvus元数据，revision压缩 |
| Milvus | milvusdb/milvus:v2.5.10 | 19530 | 向量数据库，standalone模式 |
| NSQ | nsqio/nsq:v1.2.1 | 4150-4171 | 消息队列（3组件） |
| coze-server | cozedev/coze-studio-server:latest | 8888 | Go后端Hertz服务 |
| coze-web | cozedev/coze-studio-web:latest | 8888→80 | Nginx前端 |

所有服务配置healthcheck，后端Docker内置Python文档处理（pdfplumber/python-docx/numpy）和Deno Pyodide代码沙箱。生产环境使用Helm Chart（opencoze v0.0.1）部署到K8s，LoadBalancer暴露8888/8889端口。

---

## 二、知识地图（文档结构设计）

coze-studio知识束将覆盖以下文档：

### references/（4篇信源）
1. `backend-architecture.md` — 后端DDD架构参考：五层结构、路由注册、中间件、错误码、工具包
2. `frontend-architecture.md` — 前端Rush.js架构参考：四级包结构、技术栈、构建配置
3. `idl-api-contracts.md` — Thrift IDL/API契约参考：服务定义、Base基类、代码生成
4. `deployment-infrastructure.md` — 部署与基础设施参考：Docker Compose、环境变量、可插拔组件、Helm

### concepts/（9篇概念）
1. `00-overview-ddd-architecture.md` — 总体架构：DDD五层、前后端分离、代码生成
2. `01-ddd-layers.md` — DDD分层详解：api/application/domain/infra/crossdomain职责与协作
3. `02-thrift-idl-codegen.md` — Thrift IDL与代码生成：IDL组织、hz/idl2ts工具链
4. `03-auth-middleware.md` — 认证与中间件：Session/Admin双层认证、i18n/log/cors等中间件
5. `04-pluggable-infrastructure.md` — 可插拔基础设施：MQ/向量库/存储/Embedding/OCR/Parser多后端
6. `05-llm-integration.md` — LLM模型集成：Eino框架、6种模型协议、序号配置模式
7. `06-rushjs-monorepo.md` — 前端Rush.js单仓库：四级包架构、依赖管理、Rsbuild构建
8. `07-workflow-editor.md` — 工作流与Agent编辑器：FlowGram引擎、workflow/agent-ide模块
9. `08-deployment-operations.md` — 部署与运维：Docker Compose、Helm、环境变量配置、数据迁移

### examples/（3篇实战）
1. `docker-quickstart.md` — Docker一键部署：make web启动、环境变量配置、服务验证
2. `add-llm-model.md` — 添加自定义LLM模型：配置MODEL_PROTOCOL/ID/KEY、支持的协议
3. `add-infra-backend.md` — 扩展基础设施：添加新的向量库/存储后端（工厂模式注册）
