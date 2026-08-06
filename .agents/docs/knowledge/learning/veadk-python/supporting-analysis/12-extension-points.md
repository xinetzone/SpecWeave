---
id: 12-extension-points
title: VeADK扩展点清单与注册机制
source: veadk-python codebase analysis
---

# VeADK 扩展点清单与注册机制

本文档系统梳理 VeADK 框架中所有公开扩展点，包括基类/接口路径、需要实现的抽象方法、注册方式及代码示例位置。

---

## 一、公开扩展点清单

### 1. 自定义Tool（工具）

| 项 | 说明 |
|---|---|
| **扩展点名称** | 自定义Tool |
| **基类/接口路径** | `google.adk.tools.base_tool.BaseTool`（Google ADK 原生） |
| **需要实现的方法** | 继承 `BaseTool` 并实现工具调用逻辑；或直接使用函数装饰器 `@tool` |
| **注册方式** | 在构造 `Agent` 时通过 `tools=[...]` 参数传入；或在 `model_post_init` 中 `self.tools.append()` |
| **代码示例位置** | `veadk/tools/builtin_tools/` 目录下所有工具实现，如 `web_search.py`、`run_code.py` |
| **使用示例** | 见 `examples/02_custom_tools/main.py` |

---

### 2. 自定义RunProcessor（运行处理器）

| 项 | 说明 |
|---|---|
| **扩展点名称** | RunProcessor（横切关注点处理器） |
| **基类/接口路径** | `veadk/processors/base_run_processor.py:27` - `BaseRunProcessor` |
| **需要实现的方法** | `process_run(self, runner, message, **kwargs) -> Callable` - 返回装饰器函数，包装事件生成器 |
| **注册方式** | 在构造 `Agent` 时通过 `run_processor=MyProcessor()` 参数传入 |
| **代码示例位置** | 基类示例见 `base_run_processor.py:46-57`；默认实现 `NoOpRunProcessor` 见第91-120行 |
| **参考实现** | `veadk/auth/middleware/oauth2_auth.py`（OAuth2认证中间件） |

**核心机制说明**：RunProcessor 使用装饰器模式（类似中间件），可以：
- 拦截事件流（pre-processing/post-processing）
- 修改或注入事件（如认证请求事件）
- 控制执行流程（如重试循环）
- 适用于认证、日志、监控、错误处理等横切关注点

---

### 3. 自定义Tracer（追踪器）

| 项 | 说明 |
|---|---|
| **扩展点名称** | Tracer（链路追踪/遥测） |
| **基类/接口路径** | `veadk/tracing/base_tracer.py:22` - `BaseTracer` |
| **需要实现的方法** | `dump(self, user_id: str, session_id: str, path: str) -> str` - 导出追踪数据到文件 |
| **注册方式** | 在构造 `Agent` 时通过 `tracers=[MyTracer(name="...")]` 参数传入列表 |
| **代码示例位置** | `veadk/tracing/telemetry/` 目录下的实现：`inmemory_exporter.py`、`tls_exporter.py`、`apmplus_exporter.py`、`cozeloop_exporter.py` |
| **使用示例** | 见 `examples/11_tracing/main.py` |

---

### 4. 自定义PromptManager（提示词管理器）

| 项 | 说明 |
|---|---|
| **扩展点名称** | PromptManager（提示词动态管理） |
| **基类/接口路径** | `veadk/prompts/prompt_manager.py:26` - `BasePromptManager` |
| **需要实现的方法** | `get_prompt(self, context: ReadonlyContext, **kwargs) -> str` - 根据上下文返回提示词字符串 |
| **注册方式** | 在构造 `Agent` 时通过 `prompt_manager=MyPromptManager(...)` 参数传入 |
| **代码示例位置** | `CozeloopPromptManager` 参考实现见 `prompt_manager.py:33-79`（从 CozeLoop 平台获取提示词） |

---

### 5. 自定义记忆后端（Memory Backend）

记忆系统分为短期记忆（会话级）和长期记忆（跨会话）两类后端：

#### 5.1 短期记忆后端（ShortTermMemory）

| 项 | 说明 |
|---|---|
| **扩展点名称** | 短期记忆后端 |
| **基类/接口路径** | `veadk/memory/short_term_memory_backends/base_backend.py:23` - `BaseShortTermMemoryBackend` |
| **需要实现的方法** | `session_service(self) -> BaseSessionService` - cached_property，返回 ADK 的 BaseSessionService 实例 |
| **注册方式** | 在构造 `ShortTermMemory` 时通过 `backend=MyBackend(...)` 参数传入 |
| **内置实现** | `sqlite_backend.py`、`postgresql_backend.py`、`mysql_backend.py` |
| **代码位置** | `veadk/memory/short_term_memory_backends/` |

#### 5.2 长期记忆后端（LongTermMemory）

| 项 | 说明 |
|---|---|
| **扩展点名称** | 长期记忆后端 |
| **基类/接口路径** | `veadk/memory/long_term_memory_backends/base_backend.py:20` - `BaseLongTermMemoryBackend` |
| **需要实现的方法** | 1. `precheck_index_naming(self)` - 索引名校验<br>2. `save_memory(self, user_id, event_strings, **kwargs) -> bool` - 保存记忆<br>3. `search_memory(self, user_id, query, top_k, **kwargs) -> list[str]` - 检索记忆 |
| **注册方式** | 在构造 `LongTermMemory` 时通过 `backend=MyBackend(index="...")` 参数传入 |
| **内置实现** | `in_memory_backend.py`、`redis_backend.py`、`opensearch_backend.py`、`mem0_backend.py`、`vikingdb_memory_backend.py`、`openviking_backend.py`、`tos_context_bucket_backend.py` |
| **代码位置** | `veadk/memory/long_term_memory_backends/` |
| **使用示例** | 见 `examples/03_short_term_memory/main.py`、`examples/09_long_term_memory/main.py` |

---

### 6. 自定义知识库后端（KnowledgeBase Backend）

| 项 | 说明 |
|---|---|
| **扩展点名称** | 知识库后端 |
| **基类/接口路径** | `veadk/knowledgebase/backends/base_backend.py:20` - `BaseKnowledgebaseBackend` |
| **需要实现的方法** | 1. `precheck_index_naming(self) -> None` - 索引名校验<br>2. `add_from_directory(self, directory, *args, **kwargs) -> bool` - 从目录导入<br>3. `add_from_files(self, files, *args, **kwargs) -> bool` - 从文件导入<br>4. `add_from_text(self, text, *args, **kwargs) -> bool` - 从文本导入<br>5. `search(self, *args, **kwargs) -> list` - 向量检索 |
| **注册方式** | 在构造 `KnowledgeBase` 时通过 `backend=MyBackend(index="...")` 参数传入 |
| **内置实现** | `in_memory_backend.py`、`milvus_backend.py`、`opensearch_backend.py`、`redis_backend.py`、`vikingdb_knowledge_backend.py`、`openviking_backend.py`、`tos_vector_backend.py`、`context_search_backend.py` |
| **代码位置** | `veadk/knowledgebase/backends/` |
| **使用示例** | 见 `examples/05_knowledgebase_rag/main.py` |

---

### 7. A2UI组件（Agent-to-UI 组件）

| 项 | 说明 |
|---|---|
| **扩展点名称** | A2UI 交互组件 |
| **基类/接口路径** | 前端 TypeScript 侧：`frontend/src/a2ui/` 目录，核心为 `registry.ts` 组件注册机制 |
| **注册方式** | 前端通过 `registry.ts` 注册自定义组件，后端通过工具调用返回组件描述 |
| **代码位置** | `veadk/a2ui/`（后端）和 `frontend/src/a2ui/`（前端） |
| **核心文件** | `veadk/a2ui/catalog.py`、`veadk/a2ui/toolset.py`、`frontend/src/a2ui/components/` |
| **使用示例** | 见 `examples/a2ui_agent/` |

---

### 8. Tunnel扩展（隧道协议）

| 项 | 说明 |
|---|---|
| **扩展点名称** | Tunnel 协议扩展（本地资源隧道） |
| **基类/接口路径** | `veadk/tunnel/protocol/base.py:36` - `BaseProtocol` |
| **需要实现的方法** | 1. `type: ClassVar[str]` - 协议类型标识符（类变量）<br>2. `get_tools(self, readonly_context=None) -> list[BaseTool]` - 返回隧道暴露的ADK工具列表<br>3. `close(self) -> None`（可选）- 释放连接 |
| **注册方式** | 通过 `veadk/tunnel/protocol/__init__.py` 中的 `get_protocol` 工厂函数注册，根据 `descriptor.protocol` 字段分派 |
| **内置实现** | `veadk/tunnel/protocol/mcp.py` - MCP（Model Context Protocol）协议 |
| **代码位置** | `veadk/tunnel/` |
| **使用示例** | 见 `examples/12_mcp-tunnel/` |

**核心架构**：TunnelRegistry（进程级单例）管理所有在线连接器连接，每个连接器可注册多个ServerDescriptor，每个ServerDescriptor根据protocol类型实例化对应的BaseProtocol处理器，在每轮Agent执行时动态挂载工具。

---

### 9. Channel扩展（消息渠道）

| 项 | 说明 |
|---|---|
| **扩展点名称** | Channel（消息渠道扩展，如飞书、钉钉等） |
| **参考实现路径** | `veadk/extensions/feishu_channel.py:269` - `FeishuChannelExtension` |
| **需要实现的核心方法** | 1. `__init__(self, runner, ...)` - 接收Runner实例和渠道配置<br>2. `connect(self)` - 启动渠道连接<br>3. `disconnect(self)` - 断开连接<br>4. `_on_message(self, message)` - 消息处理回调，调用 `runner.run()` 或 `runner.run_async()`<br>5. `build_message_context(self, message)` - 构建消息上下文（映射user_id/session_id） |
| **注册方式** | 直接实例化后调用 `connect()` 启动；无需框架级注册，作为独立桥接层 |
| **代码示例位置** | `veadk/extensions/feishu_channel.py` 完整实现（780行） |
| **关键设计** | - `SessionIdFactory`/`UserIdFactory` 可自定义ID映射策略<br>- 支持thread历史上下文收集<br>- 支持streaming流式响应<br>- 支持message reactions表情反馈 |

---

### 10. CLI子命令扩展

| 项 | 说明 |
|---|---|
| **扩展点名称** | CLI 子命令 |
| **框架路径** | `veadk/cli/cli.py:64` - Click 命令组 `veadk` |
| **注册方式** | 使用 `@click.command()` 装饰器定义命令，然后通过 `veadk.add_command(cmd)` 注册到主命令组 |
| **现有命令示例** | `cli_init.py`（init）、`cli_create.py`（create）、`cli_deploy.py`（deploy）、`cli_web.py`（web）、`cli_kb.py`（kb）、`cli_eval.py`（eval）等15+子命令 |
| **代码位置** | `veadk/cli/` 目录下所有 `cli_*.py` 文件 |
| **命令注册点** | `cli.py:77-92` 行集中注册所有子命令 |

---

## 二、云部署集成模块清单

| 模块路径 | 功能描述 | 依赖SDK |
|---|---|---|
| `veadk/integrations/ve_faas/` | 火山引擎函数计算（VeFaaS）部署集成<br>- 代码打包上传<br>- 函数创建/更新<br>- 应用创建/发布<br>- 容器镜像部署<br>- APIG网关自动配置 | `volcenginesdkvefaas`、`cookiecutter`、`requests` |
| `veadk/integrations/ve_apig/` | API网关（APIG）集成<br>- Serverless网关管理<br>- 服务/路由/上游配置<br>- 网关查询与创建 | `volcenginesdkapig`、`volcenginesdkapig20221112` |
| `veadk/integrations/ve_cr/` | 容器镜像仓库（CR）集成<br>- VPC隧道配置（容器镜像拉取网络打通） | 通过 `ve_faas.py` 中的 `query_user_cr_vpc_tunnel()` 调用 |
| `veadk/integrations/ve_tos/` | 对象存储（TOS）集成<br>- 媒体文件上传<br>- 内联数据托管 | `ve_tos.py` 提供TOS客户端封装 |
| `veadk/integrations/ve_tls/` | 日志服务（TLS）集成<br>- 日志导出<br>- Trace数据上报 | `ve_tls.py`、`utils.py`，配合 `tracing/telemetry/exporters/tls_exporter.py` |
| `veadk/integrations/ve_identity/` | 身份认证服务（VeIdentity）集成<br>- IAM凭证获取<br>- OAuth2认证流程<br>- MCP工具认证<br>- Function Tool认证 | `identity_client.py`、`token_manager.py`、`auth_mixins.py`、`mcp_tool.py`、`function_tool.py` |
| `veadk/integrations/agentkit/` | AgentKit平台集成<br>- 应用托管<br>- 会话能力管理<br>- 评估反馈客户端 | `app.py`、`session_capabilities.py`、`evaluation/` |
| `veadk/integrations/ve_cozeloop/` | CozeLoop提示词平台集成<br>- 提示词版本管理<br>- PromptManager后端 | `ve_cozeloop.py` |
| `veadk/integrations/ve_prompt_pilot/` | PromptPilot提示词优化集成 | `ve_prompt_pilot.py` |
| `veadk/integrations/ve_viking_db_memory/` | VikingDB向量数据库记忆后端 | `ve_viking_db_memory.py` |
| `veadk/integrations/ve_code_pipeline/` | 代码流水线集成 | `ve_code_pipeline.py` |

---

## 三、扩展点架构分层

```
┌─────────────────────────────────────────────────────────────┐
│                   应用层（User Extensions）                   │
│  自定义Channel、自定义CLI命令、业务Tool、A2UI自定义组件         │
├─────────────────────────────────────────────────────────────┤
│                   扩展层（VeADK Extension Points）            │
│  RunProcessor、Tracer、PromptManager、                       │
│  Memory Backend、KnowledgeBase Backend、                     │
│  Tunnel Protocol、A2A Middleware                             │
├─────────────────────────────────────────────────────────────┤
│                   核心层（VeADK Core）                        │
│  Agent、Runner、Session、Event、Config、                     │
│  CredentialService、Auth                                     │
├─────────────────────────────────────────────────────────────┤
│                   基础层（Google ADK + Volcengine SDK）       │
│  LlmAgent、BaseTool、BaseSessionService、                    │
│  volcenginesdkcore、a2a-sdk、lark_oapi                       │
└─────────────────────────────────────────────────────────────┘
```
