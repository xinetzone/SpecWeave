---
id: veadk-python-index
title: VeADK-Python Wiki
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 火山引擎
- AI Agent
- Python
- Wiki
- 文档
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 开发知识库首页，提供项目介绍、核心特性、文档导航和学习路径
wiki_version: '1.0'
---


# VeADK-Python Wiki

欢迎来到 VeADK-Python 开发知识库！VeADK（Volcano Engine Agent Development Kit）是火山引擎推出的企业级 AI Agent 开发框架，基于 Google ADK（Agent Development Kit）构建，深度集成火山引擎云服务生态，为开发者提供开箱即用、生产就绪的智能体开发体验。

VeADK-Python 在保持与 Google ADK 完全兼容的基础上，通过"继承+条件插件挂载"的渐进式扩展模式，为开发者集成了短期/长期记忆、知识库 RAG、工具与技能管理、多智能体协作（A2A 协议）、链路追踪、云部署等完整能力。框架采用容错设计理念，提供多级配置降级、自动工具依赖补全、云端凭证自动探测等特性，支持本地开发、沙箱调试、Serverless 部署等全生命周期管理，让开发者专注于业务逻辑，而非重复造轮子。

---

## 核心特性

- **🤖 Agent 与 Runner**：继承自 Google ADK LlmAgent，提供开箱即用的智能体基类和高性能运行器，自动管理会话状态、事件流和执行上下文
- **🧠 双层记忆体系**：内置短期记忆（会话上下文，支持 MySQL/PostgreSQL/SQLite）和长期记忆（跨会话持久化，支持 VikingDB/OpenSearch/Redis/Mem0）
- **📚 知识库 RAG**：支持多后端向量检索（VikingDB/Milvus/OpenSearch/TOS 向量），自动挂载知识库工具，实现检索增强生成
- **🔧 丰富工具生态**：内置网页搜索、代码执行、飞书集成、PPT生成、图片生成、视频生成等 30+ 工具，支持 MCP 协议接入外部工具
- **⚡ 技能系统**：支持本地技能和云端沙箱技能，自动探测运行环境，实现技能的动态加载和安全执行
- **👥 多智能体协作**：完整实现 A2A（Agent-to-Agent）开放协议，提供 Server-AgentCard-Hub-Client 四层架构，支持跨框架 Agent 互发现和互调用
- **🎨 A2UI 交互**：支持 Agent 生成和操作用户界面，实现对话式 UI 交互体验
- **🔌 三运行时支持**：支持 adk（默认）、codex、piagent 三种运行时引擎，桥接不同执行环境
- **📊 可观测性**：内置链路追踪（Tracer），支持 OpenTelemetry、APMPlus、CozelLoop 等多种追踪后端
- **🚀 云原生部署**：一键部署到火山引擎 VeFaaS 函数计算，支持 IAM 角色免密认证、API 网关自动配置
- **💻 命令行工具**：完整的 CLI 工具链，支持项目初始化、Agent 创建、沙箱调试、部署发布、知识库管理、Prompt 管理等
- **🔒 企业级安全**：OAuth2 认证、API Key 四级优先级解析、请求自动签名、日志凭证脱敏等安全特性

---

## 快速开始

- [安装指南](getting-started/installation.md) - 环境准备与 VeADK 安装
- [配置说明](getting-started/configuration.md) - 核心配置项详解
- [快速入门](getting-started/quickstart.md) - 5分钟创建你的第一个 Agent
- [AgentKit 应用开发](getting-started/agentkit-app.md) - 使用 AgentKit 开发完整应用

---

## 文档导航

| 章节 | 文档 | 状态 |
|------|------|------|
| **入门指南** | [安装指南](getting-started/installation.md) | ✅ 已完成 |
| | [配置说明](getting-started/configuration.md) | ✅ 已完成 |
| | [快速入门](getting-started/quickstart.md) | ✅ 已完成 |
| | [AgentKit 应用开发](getting-started/agentkit-app.md) | ✅ 已完成 |
| **架构设计** | [整体架构](architecture/overview.md) | ✅ 已完成 |
| | [Agent 生命周期](architecture/agent-lifecycle.md) | ✅ 已完成 |
| | [设计模式](architecture/design-patterns.md) | ✅ 已完成 |
| | [模块依赖关系](architecture/module-dependencies.md) | ✅ 已完成 |
| **核心模块** | [Agent 模块](modules/agent.md) | ✅ 已完成 |
| | [Runner 运行器](modules/runner.md) | ✅ 已完成 |
| | [AgentBuilder 构建器](modules/agent-builder.md) | ✅ 已完成 |
| | [Config 配置](modules/config.md) | ✅ 已完成 |
| | [Memory 记忆](modules/memory.md) | ✅ 已完成 |
| | [KnowledgeBase 知识库](modules/knowledgebase.md) | ✅ 已完成 |
| | [Tools 工具](modules/tools.md) | ✅ 已完成 |
| | [Skills 技能](modules/skills.md) | ✅ 已完成 |
| | [CLI 命令行](modules/cli.md) | ✅ 已完成 |
| | [A2A 多智能体](modules/a2a.md) | ✅ 已完成 |
| | [Cloud 云部署](modules/cloud.md) | ✅ 已完成 |
| | [Auth 认证授权](modules/auth.md) | ✅ 已完成 |
| | [Models 模型配置](modules/models.md) | ✅ 已完成 |
| | [Tracing 链路追踪](modules/tracing.md) | ✅ 已完成 |
| | [Multimodal 多模态](modules/multimodal.md) | ✅ 已完成 |
| | [Prompts 提示词管理](modules/prompts.md) | ✅ 已完成 |
| **示例代码** | [快速入门示例](examples/quickstart.md) | ✅ 已完成 |
| | [自定义工具示例](examples/custom-tools.md) | ✅ 已完成 |
| | [记忆使用示例](examples/memory.md) | ✅ 已完成 |
| | [知识库使用示例](examples/knowledgebase.md) | ✅ 已完成 |
| | [多智能体协作示例](examples/multi-agent.md) | ✅ 已完成 |
| | [结构化输出示例](examples/structured-output.md) | ✅ 已完成 |
| | [模型配置示例](examples/model-config.md) | ✅ 已完成 |
| | [A2UI 交互示例](examples/a2ui.md) | ✅ 已完成 |
| | [链路追踪示例](examples/tracing.md) | ✅ 已完成 |
| **扩展开发** | [自定义工具](extensions/custom-tool.md) | ✅ 已完成 |
| | [自定义扩展](extensions/custom-extension.md) | ✅ 已完成 |
| | [RunProcessor 中间件](extensions/custom-run-processor.md) | ✅ 已完成 |
| | [云服务集成](extensions/cloud-integration.md) | ✅ 已完成 |
| **常见问题** | [最佳实践](faq/best-practices.md) | ✅ 已完成 |
| | [故障排查](faq/troubleshooting.md) | ✅ 已完成 |
| **参考资料** | [API 索引](references/api-index.md) | ✅ 已完成 |
| | [术语表](glossary.md) | ✅ 已完成 |

---

## 阅读路径建议

### 🌱 新手路径（第一次接触 VeADK）
如果你是第一次使用 VeADK，建议按以下顺序阅读：
1. [安装指南](getting-started/installation.md) → 2. [配置说明](getting-started/configuration.md) → 3. [快速入门](getting-started/quickstart.md) → 4. [术语表](glossary.md) → 5. [快速入门示例](examples/quickstart.md)

### 🚀 进阶路径（已掌握基础，要开发生产级应用）
完成新手路径后，建议学习：
1. [整体架构](architecture/overview.md) → 2. [Agent 模块](modules/agent.md) → 3. [Memory 记忆](modules/memory.md) → 4. [KnowledgeBase 知识库](modules/knowledgebase.md) → 5. [Tools 工具](modules/tools.md) → 6. [Runner 运行器](modules/runner.md) → 7. [知识库使用示例](examples/knowledgebase.md)

### 🔧 扩展开发路径（要开发自定义插件/集成）
要进行框架扩展或深度定制时学习：
1. [设计模式](architecture/design-patterns.md) → 2. [模块依赖关系](architecture/module-dependencies.md) → 3. [自定义工具](extensions/custom-tool.md) → 4. [自定义扩展](extensions/custom-extension.md) → 5. [RunProcessor 中间件](extensions/custom-run-processor.md) → 6. [云服务集成](extensions/cloud-integration.md)

---

## 相关资源

- [火山引擎官方文档](https://www.volcengine.com/docs) - 火山引擎各云服务产品文档
- [VeADK GitHub 仓库](https://github.com/volcengine/veadk-python) - 源码托管与 Issue 反馈
- [PyPI 包地址](https://pypi.org/project/veadk/) - Python 包发布页面
- [Google ADK 官方文档](https://google.github.io/adk-docs/) - 底层框架 Google ADK 文档
- [A2A 协议规范](https://a2a-protocol.org/) - Agent-to-Agent 开放协议标准
- [MCP 协议规范](https://modelcontextprotocol.io/) - Model Context Protocol 标准

---

> **版本说明**：本文档基于 VeADK-Python 代码库分析生成，对应 Wiki 版本 1.0。如发现文档内容与实际代码不符，请参考源代码为准。
