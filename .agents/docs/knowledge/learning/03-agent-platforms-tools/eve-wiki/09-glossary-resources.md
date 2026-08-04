---
id: "eve-wiki-09"
title: "术语表与参考资源"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "glossary", "resources", "references"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 核心术语表（≥15 个）与参考资源清单（5 个来源 + 官方文档 + 知识库交叉引用）。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 09 术语表与参考资源

本章汇总 Eve 的核心术语表与参考资源清单，帮助读者快速建立概念框架，并获取进一步学习的官方与社区材料。

## 术语表

| 术语 | 通俗解释 |
|------|----------|
| Eve / Agent 框架 | Vercel 推出的开源 Agent 生产级框架，通过文件系统管理 Agent 的完整生命周期。 |
| Next.js for Agents | 一个定位类比：如同 Next.js 提供 Web 工程化的约定与脚手架，Eve 为 Agent 应用提供类似的生产级工程约定。 |
| filesystem-first（文件系统优先） | 以文件系统作为 Agent 定义与配置的主要载体，让 Agent 可被 Version Control 管理、可被 Git 追踪。 |
| 一个 Agent 就是一个目录（An agent is a directory） | Agent 的全部配置与能力都存放在一个独立目录中，便于复制、迁移与版本管理。 |
| instructions.md（系统指令） | 定义 Agent 系统提示词与行为边界的 Markdown 文件，是 Agent 的"大脑说明书"。 |
| agent.ts（模型与运行时配置） | 声明 Agent 使用哪个模型、运行在哪个运行时等配置的 TypeScript 文件。 |
| tools（TypeScript 工具文件） | 用 TypeScript 文件编写并注册的 Agent 可调用工具，是 Agent 与外部世界交互的接口。 |
| skills（Markdown 操作手册） | 用 Markdown 编写的操作手册，为 Agent 提供可复用的技能指导。 |
| subagents（子 Agent） | 可被主 Agent 委派子任务的独立 Agent，用于拆分复杂工作。 |
| channels（渠道/入口） | Agent 接入外部世界的入口，例如 Slack、GitHub、Web 等渠道。 |
| schedules（定时任务） | 按计划自动触发 Agent 运行的定时调度机制。 |
| connections（外部服务连接） | Agent 与外部服务（如 GitHub、Slack、Linear）建立的连接配置。 |
| durable execution（持久化执行） | 记录并保存执行状态，使 Agent 在暂停后可恢复继续执行的能力。 |
| checkpoint（检查点） | 保存 Agent 执行状态的快照，用于中断后恢复。 |
| sandbox（沙箱） | 隔离 Agent 执行环境的容器，限制其访问与副作用，保障安全。 |
| human-in-the-loop approvals（人工审批） | 高风险动作需等待人工确认后才执行的机制，将人纳入决策闭环。 |
| MCP（Model Context Protocol，模型上下文协议） | 开放标准协议，用于标准化模型与工具/数据源之间的交互方式。 |
| Vercel Connect（安全连接） | Vercel 提供的安全连接机制，用于 Agent 与外部服务的安全集成。 |
| OpenTelemetry（可观测性标准） | 业界通用的可观测性标准，用于指标、日志与链路追踪的采集与导出。 |
| evals（评测） | 用于评估 Agent 输出质量与任务完成度的评测体系。 |
| Agent Loop（智能体循环） | 模型反复思考、调用工具、观察结果、再决策的循环过程。 |
| Agent Harness（智能体运行底座） | 支撑 Agent 运行所需的模型之外的全部基础设施（状态、权限、工具、执行环境、反馈、审计、验证）。 |
| AI Gateway（AI 网关） | 统一管理模型供应商调用、路由与观测的网关层。 |
| provider fallback（模型供应商回退） | 当主模型供应商不可用时，自动切换到备用供应商的容错机制。 |

## 参考资源

### 学习来源

| 来源 | 链接 |
|------|------|
| nixapi 深度解析 | https://blog.nixapi.com/blog/vercel-eve-agent-framework-2026/ |
| 知乎分析一 | https://zhuanlan.zhihu.com/p/2051780593944416346 |
| 知乎分析二 | https://zhuanlan.zhihu.com/p/2050951746332124853 |
| 掘金工程化解读 | https://juejin.cn/post/7657863114352754726 |
| Vercel 官方产品页 | https://vercel.com/eve |

### 官方资源

| 资源 | 链接 |
|------|------|
| 官方产品页 | https://vercel.com/eve |
| 官方发布博客 | https://vercel.com/blog/introducing-eve |
| 官方文档 | https://beta.eve.dev/docs |
| GitHub 仓库 | https://github.com/vercel/eve |

### 知识库交叉引用

- 上级索引：[`../README.md`](../README.md)（03-agent-platforms-tools 生态调研）
- 同类 Agent 框架/平台 Wiki：
  - [`../orca-wiki/README.md`](../orca-wiki/README.md)（Orca 多代理编排器）
  - [`../volcengine-agentkit-wiki/README.md`](../volcengine-agentkit-wiki/README.md)（火山引擎 AgentKit 企业级 AI Agent 基础设施）

---

| 上一章 | 返回目录 |
|--------|---------|
| ← [08 FAQ 与适用范围](./08-faq.md) | [README](./README.md) |