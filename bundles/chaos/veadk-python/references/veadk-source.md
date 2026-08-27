---
type: Reference
title: veadk-python 源码
description: veadk-python 源码仓库登记，包含核心模块文件清单、依赖信息与许可证
tags: [veadk, source, reference, volcengine]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: pending, at: pending }
status: draft
stale_after: 2027-08-23
sources:
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# veadk-python 源码

## 仓库信息

| 属性 | 值 |
|------|-----|
| 包名 | `veadk-python` |
| 描述 | Volcengine agent development kit, integrations with Volcengine cloud services |
| 版本 | 动态字段，由 `setuptools-scm` 从 git tag 派生；回退 `0.0.0` |
| 许可证 | Apache License 2.0 |
| Python 要求 | `>=3.10` |
| 构建后端 | `setuptools.build_meta`（`setuptools>=64`, `setuptools-scm>=8`） |
| 控制台入口 | `veadk = "veadk.cli.cli:veadk"` |
| 运行时版本获取 | `importlib.metadata.version("veadk-python")`，未安装回退 `"0.0.0+unknown"` |

## 核心依赖

| 依赖 | 版本约束 | 用途 |
|------|---------|------|
| `google-adk` | `>=1.34.0` | 基础 Agent 架构（LlmAgent、Runner、Flow） |
| `pydantic-settings` | `==2.10.1` | 配置管理 |
| `a2a-sdk` | `==0.3.7` | Google Agent2Agent 协议 |
| `litellm` | `>=1.83.7` | LiteLlm 模型统一网关 |
| `sqlalchemy` | `>=2,<3` | 会话存储 |
| `python-dotenv` | `>=1.1.0` | .env 文件加载 |
| `volcengine-python-sdk` | `>=5.0.36` | 火山引擎 API 与 Ark Responses |
| `volcengine` | `>=1.0.193` | 火山引擎签名与 AgentKit Runtime API |
| `omegaconf` | `==2.3.0` | AgentBuilder YAML 配置解析 |
| `fastmcp` / `mcp` | `>=2.12.3` / `==1.26.0` | MCP 协议支持 |
| `cookiecutter` | `==2.6.0` | 云部署项目模板生成 |
| `jinja2` | `==3.1.6` | 模板引擎（Prompt、监督者指令） |
| `vikingdb-python-sdk` | `>=0.1.3` | Viking DB 向量数据库 |
| `tos` | `>=2.8.4` | TOS 对象存储 |

### 可选依赖组

| 组名 | 主要内容 |
|------|---------|
| `codex` | `openai-codex`, `openai-codex-cli-bin` |
| `extensions` | redis, cozeloop, llama-index 系列, opensearch-py, pymilvus, lark SDK |
| `database` | redis, pymysql, volcengine, mem0ai |
| `a2ui` | `a2ui-agent-sdk>=0.2.1` |
| `eval` | prometheus-client, deepeval>=3.2.6, google-adk[eval] |
| `harness` | headroom |
| `dev` | pre-commit, pytest, pytest-asyncio, pytest-xdist |

## 关键源文件清单

源码根路径：`d:\AI\.chaos\libs\veadk-python\veadk\`

### 核心模块

| 文件路径 | 职责 |
|---------|------|
| `__init__.py` | 包初始化，`Agent`/`Runner` 懒加载，`__all__` 导出 |
| `version.py` | 版本号动态获取与回退 |
| `agent.py` | `Agent` 核心类（继承 LlmAgent），生命周期、模型实例化、工具挂载 |
| `agent_builder.py` | `AgentBuilder`，YAML 配置驱动的 Agent 递归构建 |
| `runner.py` | `Runner` 运行器，消息拦截、多模态转换、Tracing |
| `config.py` | `VeADKConfig` 全局配置，环境变量加载与 CSP 适配 |
| `consts.py` | 默认常量（Agent 名、模型端点、Tracing URL） |
| `types.py` | 公共类型定义 |
| `harness.py` | Harness 扩展插件构建入口 |

### Agent 类型（`agents/`）

| 文件路径 | 职责 |
|---------|------|
| `loop_agent.py` | `LoopAgent`，继承 ADK LoopAgent |
| `parallel_agent.py` | `ParallelAgent`，继承 ADK ParallelAgent |
| `sequential_agent.py` | `SequentialAgent`，继承 ADK SequentialAgent |
| `supervise_agent.py` | 监督者模式：`Advice` 模型、`build_supervisor`、`generate_advice` |

### 流程控制（`flows/`）

| 文件路径 | 职责 |
|---------|------|
| `supervise_auto_flow.py` | `SupervisorAutoFlow`，LLM 调用前注入监督建议 |
| `supervise_single_flow.py` | `SupervisorSingleFlow`，单 Agent 监督流程基类 |

### 配置子系统（`configs/`）

| 文件路径 | 职责 |
|---------|------|
| `model_configs.py` | `ModelConfig`、`EmbeddingModelConfig`、`RealtimeModelConfig` |
| `auth_configs.py` | 认证配置 |
| `database_configs.py` | 数据库配置 |
| `tool_configs.py` | 内置工具配置 |
| `tracing_configs.py` | Tracing 配置 |
| `dynamic_config_manager.py` | 动态配置管理 |

### 记忆系统（`memory/`）

| 文件路径 | 职责 |
|---------|------|
| `short_term_memory.py` | `ShortTermMemory`，会话状态、Profile 生成、历史压缩 |
| `long_term_memory.py` | `LongTermMemory`，跨会话持久化、后端工厂 |
| `types.py` | `MemoryProfile` 数据模型 |
| `save_session_callback.py` | 会话保存回调 |
| `short_term_memory_processor.py` | 短期记忆处理器 |
| `short_term_memory_backends/` | MySQL、PostgreSQL、SQLite 后端 |
| `long_term_memory_backends/` | local、opensearch、redis、viking、mem0、openviking、tos_context 后端 |

### 模型层（`models/`）

| 文件路径 | 职责 |
|---------|------|
| `ark_llm.py` | `ArkLlm`（继承 Gemini），Ark Responses API、fallback 机制 |
| `ark_embedding.py` | `ArkEmbedding`（继承 llama_index BaseEmbedding） |

### 知识库（`knowledgebase/`）

| 文件路径 | 职责 |
|---------|------|
| `knowledgebase.py` | `KnowledgeBase` 统一接口，8 种后端工厂、Profile 生成 |
| `entry.py` | `KnowledgebaseEntry` 数据模型 |
| `types.py` | `KnowledgebaseProfile` 数据模型 |
| `backends/` | local、opensearch、redis、milvus、tos_vector、vikingdb、context_search、openviking 后端 |

### 评估系统（`evaluation/`）

| 文件路径 | 职责 |
|---------|------|
| `base_evaluator.py` | `BaseEvaluator`、`EvalTestCase`、`MetricResult`、`EvalResultData` |
| `types.py` | `EvalResultCaseData`、`EvalResultMetadata` |
| `eval_set_file_loader.py` | 评估集文件加载 |
| `eval_set_recorder.py` | 评估结果记录 |
| `adk_evaluator/` | ADK 原生评估器 |
| `deepeval_evaluator/` | DeepEval 评估器 |

### CLI 工具（`cli/`）

| 文件路径 | 职责 |
|---------|------|
| `cli.py` | Click 命令组入口，16 个子命令注册 |
| `cli_create.py` | `create` 命令，生成 Agent 项目 |
| `cli_init.py` | `init` 命令，交互式部署配置 |
| `cli_deploy.py` | `deploy` 命令，FaaS/APIG 部署 |
| `cli_eval.py` | `eval` 命令，运行评估 |
| `cli_web.py` | `web` 命令，启动 Web 服务（OAuth2 补丁） |
| `cli_prompt.py` | `prompt` 命令 |
| `cli_kb.py` | `kb` 命令，知识库管理 |
| `cli_pipeline.py` | `pipeline` 命令 |
| `cli_frontend.py` | `frontend` 命令 |
| `cli_agentkit.py` | `agentkit` 命令 |
| `cli_harness.py` | `harness` 命令 |
| `cli_rl.py` | `rl_group` 命令组 |
| `cli_clean.py` | `clean` 命令 |
| `cli_update.py` | `update` 命令 |
| `cli_uploadevalset.py` | `uploadevalset` 命令 |

### A2A 协议（`a2a/`）

| 文件路径 | 职责 |
|---------|------|
| `agent_card.py` | `get_agent_card`，生成 AgentCard |
| `remote_ve_agent.py` | `RemoteVeAgent`，远程 Agent 代理 |
| `ve_a2a_server.py` | A2A 服务端 |
| `ve_agent_executor.py` | Agent 执行器 |
| `registry_client.py` | A2A 注册表客户端 |

### 多模态（`multimodal/`）

| 文件路径 | 职责 |
|---------|------|
| `models.py` | `MediaRef`、`MediaRecord` 数据类 |
| `api.py` | `mount_media_routes`，FastAPI 媒体端点 |
| `service.py` | 媒体服务 |
| `storage.py` | 存储抽象 |
| `plugin.py` | 多模态插件 |

### 运行时抽象（`runtime/`）

| 文件路径 | 职责 |
|---------|------|
| `base_runtime.py` | `BaseRuntime` 抽象类，系统提示词构建 |
| `codex/` | Codex 运行时（基于 Claude Code SDK） |
| `piagent/` | PiAgent 运行时 |

### 其他重要模块

| 路径 | 职责 |
|------|------|
| `prompts/` | Prompt 管理（`BasePromptManager`、`CozeloopPromptManager`、默认 Prompt） |
| `auth/` | 认证体系（`BaseAuth`、OAuth2 中间件、VeCredentialService） |
| `tracing/` | OpenTelemetry Tracing（APMPlus、Cozeloop、TLS exporter） |
| `tools/` | 内置工具集（知识库、记忆、网页搜索、代码沙箱、图像/视频生成等） |
| `skills/` | 技能系统（注册、物化、检查清单回调） |
| `extensions/harness/` | Harness 扩展（调用上下文、压缩、响应验证插件） |
| `integrations/` | 火山引擎服务集成（FaaS、APIG、TOS、VikingDB、CozeLoop、VeIdentity） |
| `tunnel/` | 隧道工具（MCP 协议、连接器、服务端） |
| `a2ui/` | Agent 驱动 UI（Catalog、Toolset） |
| `realtime/` | 实时语音模型 |
| `reflector/` | 反射器 |
