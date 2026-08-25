---
okf_version: "0.2"
type: Index
title: mobile-use 知识包
description: 基于 LangGraph 的 AI 多智能体移动端自动化框架——Android/iOS 设备自然语言控制
tags: [mobile-automation, ai-agent, langgraph, android, ios]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
stale_after: 2027-08-23
---

# mobile-use 知识包

本知识包（bundle）系统梳理 minitap-mobile-use（版本 3.6.3）的架构与实现。mobile-use 是一个基于 LangGraph 的 AI 多智能体系统，通过底层控制实现真实 Android 和 iOS 设备的自然语言自动化。内容涵盖多 Agent 协作架构、设备控制抽象层、工具系统、LLM 可插拔配置、SDK 双层 API 和图状态管理，遵循 OKF v0.2 规范。

## 目录分组

* [concepts/](concepts/) - 核心概念：7 篇概念文档，按编号排列，覆盖从项目概览到多 Agent 架构到 SDK 接口的完整知识体系
  * [mobile-use 项目概览](concepts/00-overview.md)
  * [多 Agent 协作架构](concepts/01-multi-agent-architecture.md)
  * [设备控制抽象层](concepts/02-device-control.md)
  * [工具系统与执行节点](concepts/03-tools-system.md)
  * [LLM 配置与可插拔体系](concepts/04-llm-configuration.md)
  * [SDK 双层 API 与生命周期](concepts/05-sdk-layer.md)
  * [图结构与状态管理](concepts/06-graph-state.md)
* [examples/](examples/) - 使用示例：CLI 命令实际用法
  * [CLI 命令使用示例](examples/cli-usage.md)
* [references/](references/) - 信源登记簿：4 篇信源文件，含 R 阶段事实清单、I 阶段洞察、源码登记与验证报告
  * [事实清单](references/facts.md)
  * [架构洞察](references/insights.md)
  * [mobile-use 源码](references/mobile-use-source.md)
  * [验证报告](references/verification-report.md)
