---
type: Concept
title: veadk-python 概览
description: 火山引擎 Agent 开发工具包 veadk-python 的定位、架构分层、版本依赖与生态组成总览
tags: [veadk, overview, architecture, volcengine, agent]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# veadk-python 概览

veadk-python（Volcengine Agent Development Kit）是火山引擎推出的 Python Agent 开发工具包，包描述为"Volcengine agent development kit, integrations with Volcengine cloud services" [F-001]。它在 Google ADK（Agent Development Kit）的基础上扩展，深度集成火山引擎的方舟大模型（Ark）、VikingDB 向量数据库、TOS 对象存储、OpenSearch、CozeLoop 等云服务，提供从 Agent 定义、配置驱动构建、记忆管理、知识库、评估到云部署的全链路工程化能力。

## 项目元信息

| 属性 | 值 |
|------|-----|
| Python 要求 | `>=3.10` [F-003] |
| 许可证 | Apache License 2.0 [F-004] |
| 版本管理 | `setuptools-scm` 从 git tag 动态派生，回退 `0.0.0` [F-002] |
| 构建系统 | `setuptools.build_meta`（`setuptools>=64`, `setuptools-scm>=8`）[F-009] |
| CLI 入口 | `veadk = "veadk.cli.cli:veadk"` [F-008] |

版本号在运行时通过 `importlib.metadata.version("veadk-python")` 获取；若包未安装（从源码树直接导入），回退为 `"0.0.0+unknown"` [F-002]。

## 顶层包导出

`veadk` 包通过 `__getattr__` 实现懒加载，仅导出三个名称 [F-011][F-012]：

- `Agent`：访问时从 `veadk.agent` 导入
- `Runner`：访问时从 `veadk.runner` 导入
- `VERSION`：版本号字符串

`__all__ = ["Agent", "Runner", "VERSION"]`。懒加载机制使得 `import veadk` 不会触发 Agent 和 Runner 的重型依赖加载，只有实际访问时才导入对应模块。

## 架构分层

veadk-python 的架构可分为五个层次：

### 1. 核心抽象层

- **Agent**（`veadk/agent.py`）：继承 Google ADK 的 `LlmAgent`，是所有智能体的基类，通过 Pydantic 字段声明能力组件 [F-013]
- **AgentBuilder**（`veadk/agent_builder.py`）：YAML 配置驱动的 Agent 工厂，支持递归构建子代理 [F-041]
- **Runner**（`veadk/runner.py`）：继承 ADK `Runner`，负责消息转换、会话管理、Tracing 和执行编排 [F-065]
- **Agent 类型**（`veadk/agents/`）：`LoopAgent`、`ParallelAgent`、`SequentialAgent` 分别继承 ADK 对应类 [F-046~F-048]

### 2. 模型与记忆层

- **LLM 抽象**（`veadk/models/`）：`ArkLlm`（Ark Responses API，继承 Gemini）和 `ArkEmbedding`（llama_index 嵌入）[F-090][F-095]
- **短期记忆**（`veadk/memory/short_term_memory.py`）：会话状态管理，支持 local/mysql/sqlite/postgresql 后端 [F-082]
- **长期记忆**（`veadk/memory/long_term_memory.py`）：跨会话持久化，支持 local/opensearch/redis/viking/mem0/openviking/tos_context 共 8 种后端 [F-086]
- **知识库**（`veadk/knowledgebase/`）：统一 RAG 接口，8 种可插拔后端 [F-102]

### 3. 工程化层

- **配置系统**（`veadk/config.py`、`veadk/configs/`）：`VeADKConfig` 全局配置，环境变量前缀映射 [F-053]
- **CLI 工具**（`veadk/cli/`）：16 个子命令覆盖创建、初始化、部署、评估、知识库管理等 [F-075]
- **评估系统**（`veadk/evaluation/`）：`BaseEvaluator` 基类，支持 ADK 和 DeepEval 两种评估器 [F-100]
- **Tracing**（`veadk/tracing/`）：OpenTelemetry 集成，支持 APMPlus、Cozeloop、TLS 三个 exporter [F-037]

### 4. 扩展与集成层

- **A2A 协议**（`veadk/a2a/`）：Agent-to-Agent 通信，AgentCard 生成、远程 Agent 代理 [F-113]
- **多模态**（`veadk/multimodal/`）：媒体上传、存储、FastAPI 路由挂载 [F-118]
- **认证**（`veadk/auth/`）：OAuth2 中间件、VeIdentity 集成 [F-112]
- **Harness 扩展**（`veadk/extensions/harness/`）：调用上下文、工具结果压缩、响应验证插件 [F-123]
- **运行时抽象**（`veadk/runtime/`）：支持 ADK、Codex、PiAgent 三种运行时 [F-119]
- **火山引擎集成**（`veadk/integrations/`）：FaaS、APIG、TOS、VikingDB、CozeLoop、VeIdentity

### 5. 工具与技能层

- **内置工具**（`veadk/tools/builtin_tools/`）：网页搜索、代码执行、图像/视频生成、飞书、TTS 等
- **MCP 工具**（`veadk/tools/mcp_tool/`）：可信 MCP 会话管理
- **沙箱工具**（`veadk/tools/sandbox/`）：浏览器、代码、计算机沙箱
- **技能系统**（`veadk/skills/`）：技能注册、物化、动态加载 [F-035]

## 默认配置与常量

veadk 的默认值面向火山引擎方舟（Ark）平台 [F-060][F-061]：

- 默认 Agent 名称：`"veAgent"`
- 默认模型：`"doubao-seed-2-1-pro-260628"`
- 默认提供商：`"openai"`（Ark 兼容 OpenAI 接口格式）
- 默认 API Base：`"https://ark.cn-beijing.volces.com/api/v3/"`
- 默认 Embedding 模型：`"doubao-embedding-vision-250615"`，维度 2048 [F-063]

当环境变量 `CLOUD_PROVIDER=byteplus` 时，默认模型和端点自动切换为 BytePlus 海外版本 [F-052][F-062]。

## 模块级补丁

`veadk/agent.py` 在模块导入时执行三个猴子补丁函数 [F-127]：

1. `patch_tracer()`：修补 Tracing 行为
2. `patch_asyncio()`：修补 asyncio 兼容性
3. `patch_mcp_session_retry()`：为 MCP 会话添加重试逻辑

此外，导入时设置 `LITELLM_LOCAL_MODEL_COST_MAP=True`，可减少约 10 秒的导入延迟。LoopAgent、ParallelAgent、SequentialAgent 模块也各自调用 `patch_asyncio()` [F-128]。

## 生态定位

veadk-python 不是一个孤立的 Agent 库，而是火山引擎 AI 生态的 Python 端入口：

- **向上**对接 Google ADK 的 Agent/Runner/Flow 抽象，复用其成熟的 Agent 编排框架
- **向下**对接火山引擎云服务（Ark 大模型、VikingDB、TOS、OpenSearch、FaaS、APIG）
- **向外**通过 A2A 协议（`a2a-sdk==0.3.7`）实现 Agent 间互操作，通过 MCP 协议（`mcp==1.26.0`）对接外部工具
- **向工程**提供 CLI、评估、Tracing、Harness 插件等 DevOps 能力

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [AgentBuilder 与 YAML 配置驱动](/concepts/02-agent-builder.md)
- [Agent 类型体系](/concepts/03-agent-types.md)
- [配置系统](/concepts/04-configuration.md)
- [Runner 运行器](/concepts/05-runner.md)
