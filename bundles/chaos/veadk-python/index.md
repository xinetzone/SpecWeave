---
okf_version: "0.2"
type: Index
title: veadk-python 知识包
description: 火山引擎 Agent Development Kit——基于 Google ADK 扩展的全链路 Python Agent 工程化框架
tags: [ai-agent, adk, volcengine, llm, python, agent-framework]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
stale_after: 2027-08-23
---

# veadk-python 知识包

本知识包（bundle）系统梳理 veadk-python（Volcengine Agent Development Kit）的架构与实现。veadk-python 是火山引擎推出的 Python Agent 开发工具包，在 Google ADK 基础上扩展，深度集成火山引擎方舟大模型、VikingDB、TOS、OpenSearch 等云服务，提供从 Agent 定义、配置驱动构建、记忆管理、知识库、评估到云部署的全链路工程化能力。内容遵循 OKF v0.2 规范。

## 目录分组

* [concepts/](concepts/) - 核心概念：12 篇概念文档，分入门组（00-05）和进阶组（06-11），覆盖从核心抽象到高级特性的完整知识体系
  * [00 — veadk-python 概览](concepts/00-overview.md)
  * [01 — Agent 核心类与生命周期](concepts/01-agent-lifecycle.md)
  * [02 — AgentBuilder 与 YAML 配置驱动](concepts/02-agent-builder.md)
  * [03 — Agent 类型体系](concepts/03-agent-types.md)
  * [04 — 配置系统](concepts/04-configuration.md)
  * [05 — Runner 运行器](concepts/05-runner.md)
  * [06 — 记忆系统](concepts/06-memory-system.md)
  * [07 — LLM 模型抽象](concepts/07-llm-models.md)
  * [08 — 知识库](concepts/08-knowledgebase.md)
  * [09 — 评估系统](concepts/09-evaluation.md)
  * [10 — CLI 工具集](concepts/10-cli-tools.md)
  * [11 — 高级特性](concepts/11-advanced.md)
* [examples/](examples/) - 使用示例：快速开始与代码用法
  * [快速开始](examples/quickstart.md)
* [references/](references/) - 信源登记簿：4 篇文件，含 R 阶段事实清单、I 阶段洞察、源码登记与 V 阶段验证报告
  * [veadk-python 事实清单](references/facts.md)
  * [架构洞察](references/insights.md)
  * [veadk-python 源码](references/veadk-source.md)
  * [验证报告](references/verification-report.md)
