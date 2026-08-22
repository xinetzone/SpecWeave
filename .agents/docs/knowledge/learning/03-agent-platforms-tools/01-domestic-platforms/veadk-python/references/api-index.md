---
id: veadk-python-api-index
title: VeADK-Python API 索引
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- API
- 索引
- 参考
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 核心公开类与函数快速索引表
wiki_version: '1.0'
---


# VeADK-Python API 索引

本页提供 VeADK-Python 所有公开类与函数的快速索引，方便开发者快速定位到对应模块文档。

---

## 核心类

| 类名 | 所在模块 | 文档链接 | 功能简述 |
|------|----------|----------|----------|
| Agent | `veadk.agent` | [modules/agent.md](../modules/agent.md) | 智能体基类，继承自 Google ADK LlmAgent，集成记忆、知识库、工具、追踪等能力 |
| Runner | `veadk.runner` | [modules/runner.md](../modules/runner.md) | 运行器，驱动 Agent 执行对话，管理会话状态、事件流、记忆集成和链路追踪 |
| AgentBuilder | `veadk.agent_builder` | [modules/agent-builder.md](../modules/agent-builder.md) | Agent 构建器，支持从 YAML 配置文件构建 Agent 及子 Agent 树 |
| ShortTermMemory | `veadk.memory` | [modules/memory.md](../modules/memory.md) | 短期记忆，保存当前对话上下文，支持 SQLite/MySQL/PostgreSQL/内存后端 |
| LongTermMemory | `veadk.memory` | [modules/memory.md](../modules/memory.md) | 长期记忆，跨会话持久化用户信息，支持 VikingDB/OpenSearch/Redis/Mem0/TOS 后端 |
| KnowledgeBase | `veadk.knowledgebase` | [modules/knowledgebase.md](../modules/knowledgebase.md) | 知识库 RAG 模块，支持多后端向量检索，自动挂载知识库工具实现检索增强生成 |
| BaseTracer | `veadk.tracing.base_tracer` | [modules/tracing.md](../modules/tracing.md) | 链路追踪器抽象基类，定义追踪数据收集和导出接口 |
| BaseRunProcessor | `veadk.processors.base_run_processor` | [extensions/custom-run-processor.md](../extensions/custom-run-processor.md) | 运行处理器抽象基类，类似中间件机制，支持在事件流执行前后插入横切逻辑 |
| BasePromptManager | `veadk.prompts.prompt_manager` | [modules/prompts.md](../modules/prompts.md) | 提示词管理器抽象基类，定义提示词获取接口 |
| CozeloopPromptManager | `veadk.prompts.prompt_manager` | [modules/prompts.md](../modules/prompts.md) | Cozeloop 平台提示词管理器，支持从 Cozeloop 服务动态加载提示词 |
| VeA2AServer | `veadk.a2a.ve_a2a_server` | [modules/a2a.md](../modules/a2a.md) | A2A 服务器，将 Agent 暴露为 A2A 协议服务，基于 FastAPI 构建 |
| AgentCard | `a2a.types` | [modules/a2a.md](../modules/a2a.md) | 智能体名片，Agent 能力自描述文档，用于 A2A 服务发现 |
| A2AHubServer | `veadk.a2a.hub.a2a_hub_server` | [modules/a2a.md](../modules/a2a.md) | A2A 注册中心服务器，提供 Agent 注册、发现、分组管理功能 |
| VeCredentialService | `veadk.auth.ve_credential_service` | [modules/auth.md](../modules/auth.md) | 凭证服务，支持按 app_name/user_id 直接管理认证凭证，扩展自 ADK BaseCredentialService |
| VeSkillRegistry | `veadk.skills.registry` | [modules/skills.md](../modules/skills.md) | 技能注册表，管理技能的注册、发现和动态加载 |

---

## 核心函数

| 函数名 | 所在模块 | 文档链接 | 功能简述 |
|--------|----------|----------|----------|
| init_app | `veadk.a2a.ve_a2a_server` | [modules/a2a.md](../modules/a2a.md) | 初始化 A2A FastAPI 应用的便捷函数 |
| get_agent_card | `veadk.a2a.agent_card` | [modules/a2a.md](../modules/a2a.md) | 根据 Agent 实例生成标准 AgentCard 对象 |
| list_builtin_tools | `veadk.tools` | [modules/tools.md](../modules/tools.md) | 列出所有可用内置工具的名称列表 |
| get_builtin_tool | `veadk.tools` | [modules/tools.md](../modules/tools.md) | 根据工具名称解析并返回对应的工具 callable |
| get_city_weather | `veadk.tools.demo_tools` | [modules/tools.md](../modules/tools.md) | 示例工具：根据城市名称获取天气 |
| get_location_weather | `veadk.tools.demo_tools` | [modules/tools.md](../modules/tools.md) | 示例工具：根据经纬度获取天气 |

---

## 异常类

| 异常类名 | 所在模块 | 文档链接 | 功能简述 |
|----------|----------|----------|----------|
| SkillLoadError | `veadk.skills.exceptions` | [modules/skills.md](../modules/skills.md) | 技能加载失败异常 |
| SkillMaterializeError | `veadk.skills.exceptions` | [modules/skills.md](../modules/skills.md) | 技能物化（实例化）失败异常 |

---

## 模块索引

| 模块 | 文档链接 | 核心内容 |
|------|----------|----------|
| Agent | [modules/agent.md](../modules/agent.md) | Agent 类定义、初始化参数、生命周期、子 Agent 管理 |
| Runner | [modules/runner.md](../modules/runner.md) | Runner 类、会话管理、事件流处理、消息类型 |
| AgentBuilder | [modules/agent-builder.md](../modules/agent-builder.md) | 配置驱动的 Agent 构建、YAML 配置格式 |
| Config | [modules/config.md](../modules/config.md) | 全局配置管理、环境变量、配置优先级 |
| Memory | [modules/memory.md](../modules/memory.md) | 短期记忆、长期记忆、各后端存储配置 |
| KnowledgeBase | [modules/knowledgebase.md](../modules/knowledgebase.md) | RAG 知识库、向量检索、文档切片、后端配置 |
| Tools | [modules/tools.md](../modules/tools.md) | 内置工具列表、MCP 工具、沙箱工具、工具调用 |
| Skills | [modules/skills.md](../modules/skills.md) | 技能系统、技能注册、动态加载、沙箱技能 |
| CLI | [modules/cli.md](../modules/cli.md) | 命令行工具、项目脚手架、部署命令 |
| A2A | [modules/a2a.md](../modules/a2a.md) | A2A 协议、AgentCard、Hub 注册中心、远程 Agent 调用 |
| Cloud | [modules/cloud.md](../modules/cloud.md) | VeFaaS 部署、云原生集成、IAM 认证 |
| Auth | [modules/auth.md](../modules/auth.md) | 认证授权、OAuth2、凭证服务、API Key 管理 |
| Models | [modules/models.md](../modules/models.md) | 模型配置、LiteLLM、Ark 大模型、降级备用模型 |
| Tracing | [modules/tracing.md](../modules/tracing.md) | 链路追踪、OpenTelemetry、APMPlus、CozelLoop |
| Multimodal | [modules/multimodal.md](../modules/multimodal.md) | 多模态处理、语音、图片、视频、文件上传 |
| Prompts | [modules/prompts.md](../modules/prompts.md) | 提示词管理、模板、版本控制、Cozeloop 集成 |

---

> **说明**：本索引仅列出 VeADK-Python 扩展的公开 API，Google ADK 原生 API 请参考 [Google ADK 官方文档](https://google.github.io/adk-docs/)。
