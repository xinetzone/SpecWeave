---
id: veadk-python-glossary
title: VeADK-Python 术语表
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 火山引擎
- AI Agent
- Python
- 术语表
- glossary
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 核心术语表，包含20+个常用术语的中英文对照和通俗解释
wiki_version: '1.0'
---


# VeADK-Python 术语表

本术语表收录 VeADK-Python 开发中常用的核心术语，以通俗易懂的方式解释其含义，适合有 Python 基础但初次接触 AI Agent 开发的开发者阅读。

---

## 核心概念

### Agent（智能体）
**中文译名**：智能体  
智能体是 VeADK 的核心概念，你可以把它理解为一个"能思考、会做事"的 AI 助手——它接收用户输入，调用大模型思考，使用工具完成任务，最后给出回答。

**相关文档**：[modules/agent.md](modules/agent.md)

### LlmAgent（大模型智能体）
**中文译名**：大模型智能体  
基于大语言模型（LLM）驱动的智能体基类，VeADK 的 Agent 直接继承自 Google ADK 的 LlmAgent，是所有智能体的基础。

**相关文档**：[modules/agent.md](modules/agent.md)

### Runner（运行器）
**中文译名**：运行器  
驱动 Agent 执行对话的"发动机"，负责管理会话、调度事件、集成记忆、链路追踪等底层工作，让你不用关心复杂的执行流程。

**相关文档**：[modules/runner.md](modules/runner.md)

### Sub-agent（子智能体）
**中文译名**：子智能体  
被主智能体调用的专用智能体，就像团队里的 specialist——主智能体负责任务分发，子智能体负责完成特定领域的子任务。

**相关文档**：[modules/agent.md](modules/agent.md)、[examples/multi-agent.md](examples/multi-agent.md)

### Runtime（运行时）
**中文译名**：运行时  
Agent 执行的底层引擎，VeADK 支持三种运行时：`adk`（默认，Google ADK 原生）、`codex`（Codex SDK 桥接）、`piagent`（PiAgent 本地二进制）。

---

## 记忆与知识

### Memory（记忆）
**中文译名**：记忆  
让 Agent "记住"信息的机制，分为短期记忆和长期记忆两类，就像人类的工作记忆和长期记忆。

**相关文档**：[modules/memory.md](modules/memory.md)

### ShortTermMemory（短期记忆）
**中文译名**：短期记忆  
保存当前对话上下文的记忆，就像你聊天时记得刚才说过什么；支持内存、SQLite、MySQL、PostgreSQL 等后端存储。

**相关文档**：[modules/memory.md](modules/memory.md)、[examples/memory.md](examples/memory.md)

### LongTermMemory（长期记忆）
**中文译名**：长期记忆  
跨会话保存用户偏好、历史信息的记忆，就像你长期记得朋友的喜好；支持 OpenSearch、VikingDB、Redis、Mem0 等多种后端。

**相关文档**：[modules/memory.md](modules/memory.md)、[examples/memory.md](examples/memory.md)

### KnowledgeBase（知识库）
**中文译名**：知识库（RAG）  
基于 RAG（检索增强生成）技术的知识管理模块，让 Agent 能"查阅"外部文档和资料，回答时有据可依；支持 VikingDB、Milvus、OpenSearch 等向量数据库。

**相关文档**：[modules/knowledgebase.md](modules/knowledgebase.md)、[examples/knowledgebase.md](examples/knowledgebase.md)

### Knowledge Profile（知识配置）
**中文译名**：知识配置文件  
描述知识库配置的元数据，定义知识库的数据源、检索策略、切片方式等参数。

**相关文档**：[modules/knowledgebase.md](modules/knowledgebase.md)

---

## 工具与技能

### Tool（工具）
**中文译名**：工具  
Agent 可以调用的外部能力，比如搜索网页、读写文件、调用 API 等——工具让 Agent 不只是"纸上谈兵"，而是真的能做事。

**相关文档**：[modules/tools.md](modules/tools.md)、[examples/custom-tools.md](examples/custom-tools.md)

### Skill（技能）
**中文译名**：技能  
封装好的、可复用的复杂能力包，比单个 Tool 粒度更大；一个 Skill 可能包含多个工具、提示词和配置，类似"插件"。

**相关文档**：[modules/skills.md](modules/skills.md)

### MCP（Model Context Protocol）
**中文译名**：模型上下文协议  
一种开放协议标准，让 Agent 能标准化地连接外部工具和数据源，类似 AI 世界的"USB 接口"。

**相关文档**：[modules/tools.md](modules/tools.md)

### A2UI（Agent to User Interface）
**中文译名**：智能体到用户界面  
让 Agent 能生成和操作用户界面的协议，实现对话式 UI 交互，而不只是返回纯文本。

**相关文档**：[examples/a2ui.md](examples/a2ui.md)、[modules/multimodal.md](modules/multimodal.md)

---

## 多智能体协作

### A2A（Agent-to-Agent）
**中文译名**：智能体间通信协议  
Agent 与 Agent 之间互相发现、互相调用的开放协议标准，让多个不同厂商、不同框架的 Agent 可以协同工作。

**相关文档**：[modules/a2a.md](modules/a2a.md)、[examples/multi-agent.md](examples/multi-agent.md)

### AgentCard（智能体名片）
**中文译名**：智能体名片  
Agent 的能力自描述文档，包含名称、描述、技能列表、输入输出模式等信息，就像 Agent 的"身份证"，用于 A2A 服务发现。

**相关文档**：[modules/a2a.md](modules/a2a.md)

### Hub（注册中心）
**中文译名**：注册中心（A2A Hub）  
A2A 架构中的中心化注册服务，多个 Agent 启动时在 Hub 注册，调用方通过 Hub 查询发现其他 Agent。

**相关文档**：[modules/a2a.md](modules/a2a.md)

---

## 执行与监控

### Flow（流程编排）
**中文译名**：流程编排  
定义多步骤任务的执行逻辑，比如顺序执行、并行执行、监督式执行等，控制多个 Agent 或工具的协作顺序。

**相关文档**：[architecture/design-patterns.md](architecture/design-patterns.md)

### Callback（回调）
**中文译名**：回调函数  
在 Agent 或 Tool 执行前后自动触发的钩子函数，比如执行前做权限检查、执行后做日志记录，支持单个函数或函数列表。

**相关文档**：[modules/agent.md](modules/agent.md)

### RunProcessor（运行处理器）
**中文译名**：运行处理器  
类似中间件的装饰器机制，可以在事件流执行前后插入横切逻辑（如认证、监控、重试），实现非业务逻辑与核心逻辑分离。

**相关文档**：[extensions/custom-run-processor.md](extensions/custom-run-processor.md)

### Tracer（链路追踪器）
**中文译名**：链路追踪器  
用于记录和监控 Agent 执行过程的组件，支持 OpenTelemetry、APMPlus、CozelLoop 等多种追踪后端，方便调试和性能分析。

**相关文档**：[modules/tracing.md](modules/tracing.md)、[examples/tracing.md](examples/tracing.md)

### Session（会话）
**中文译名**：会话  
一次完整的用户与 Agent 交互过程，包含多轮对话历史，由 Session ID 唯一标识。

**相关文档**：[modules/runner.md](modules/runner.md)、[modules/memory.md](modules/memory.md)

### Event（事件）
**中文译名**：事件  
Agent 执行过程中产生的流式消息单元，比如思考中、工具调用、文本输出、错误等，Runner 通过事件流实时反馈执行状态。

**相关文档**：[modules/runner.md](modules/runner.md)

---

## 模型与云服务

### LiteLLM
**中文译名**：LiteLLM 客户端  
VeADK 默认的通用 LLM 客户端，兼容 OpenAI API 格式，支持接入多种大模型服务。

**相关文档**：[modules/models.md](modules/models.md)、[examples/model-config.md](examples/model-config.md)

### ArkLlm
**中文译名**：方舟大模型客户端  
火山引擎方舟（Ark）平台的原生 LLM 客户端，支持豆包 Responses API、多轮缓存等平台特有能力。

**相关文档**：[modules/models.md](modules/models.md)

### Fallbacks（降级备用模型）
**中文译名**：降级备用模型  
模型容错机制——当主模型（如 doubao-pro）限流或故障时，自动切换到备用模型（如 doubao-lite），提升服务可用性。

**相关文档**：[modules/models.md](modules/models.md)

### PromptManager（提示词管理器）
**中文译名**：提示词管理器  
统一管理 Agent 提示词模板的模块，支持提示词版本控制、动态加载和优化。

**相关文档**：[modules/prompts.md](modules/prompts.md)

---

## 火山引擎云服务

### VeFaaS
**中文译名**：火山引擎函数计算  
火山引擎的 Serverless 函数计算服务，VeADK 支持一键将 Agent 部署到 VeFaaS，实现弹性伸缩。

**相关文档**：[modules/cloud.md](modules/cloud.md)

### TOS（Tinder Object Storage）
**中文译名**：火山引擎对象存储  
火山引擎的对象存储服务，VeADK 用它存储知识库文档、上下文文件、向量数据等资源。

**相关文档**：[modules/cloud.md](modules/cloud.md)、[modules/multimodal.md](modules/multimodal.md)

### VikingDB
**中文译名**：维京数据库  
火山引擎自研的向量数据库，VeADK 用它做长期记忆后端和知识库向量检索，支持高性能相似度搜索。

**相关文档**：[modules/memory.md](modules/memory.md)、[modules/knowledgebase.md](modules/knowledgebase.md)、[modules/cloud.md](modules/cloud.md)

---

## 构建与配置

### Pydantic
**中文译名**：Pydantic 数据验证库  
Python 中广泛使用的数据验证和设置管理库，VeADK 使用 Pydantic 定义配置类、数据模型和 Agent 属性，提供类型检查和自动序列化。

### asyncio
**中文译名**：异步 I/O 库  
Python 标准库中的异步编程框架，VeADK 的核心 API（如 `Runner.run()`）都是异步的，需要在 `asyncio` 事件循环中运行。

### Google ADK
**中文译名**：Google Agent Development Kit  
Google 开源的 Agent 开发框架，VeADK 基于 Google ADK 进行扩展，继承其核心的 Agent、Runner、Tool 抽象和执行引擎。

### AgentBuilder（构建器）
**中文译名**：Agent 构建器  
通过 YAML 配置文件声明式构建 Agent 及子 Agent 树的工具类，支持动态加载工具和子智能体。

**相关文档**：[modules/agent-builder.md](modules/agent-builder.md)

### Config（配置）
**中文译名**：配置系统  
VeADK 的多级配置管理体系，支持环境变量、配置文件、代码参数等多种配置方式，遵循"代码参数 > 环境变量 > 默认值"的优先级。

**相关文档**：[modules/config.md](modules/config.md)、[getting-started/configuration.md](getting-started/configuration.md)

### VeCredentialService（凭证服务）
**中文译名**：凭证服务  
VeADK 提供的凭证管理服务，支持按 app_name/user_id 存储和获取认证凭证，集成 OAuth2 等多种认证方式。

**相关文档**：[modules/auth.md](modules/auth.md)

---

> 返回 [文档首页](index.md) | 查看 [API 索引](references/api-index.md)
