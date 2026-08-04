---
id: "eve-wiki-03"
title: "生产级能力详解"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "durable-execution", "sandbox", "approvals", "connections", "channels", "tracing", "evals"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 六大生产级能力详解：durable execution（持久化执行）、人工审批（human-in-the-loop approvals）、connections（安全连接）、channels（多渠道）、tracing（可观测）、evals（评测）。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 03 生产级能力详解

Eve 内置了六大生产级能力，它们共同回答了真实 Agent 在生产中面临的持久运行、安全执行、权限控制、多渠道接入、可观测与回归验证问题。这些能力在 Demo 阶段往往被忽略，却是生产系统的关键。

## Durable Execution：Agent 不应该害怕重启

普通聊天接口通常是一问一答，请求结束任务也就结束。但 Agent 经常不是这样——它可能需要等待一个慢查询，可能要等用户补充材料，也可能在执行危险操作前等待审批，一次任务持续几个小时甚至几天并不奇怪。

如果把这种任务绑在一个普通 HTTP 请求上，超时、断线和进程重启迟早会找上门。Eve 的做法是把**每段会话作为一个 durable workflow 运行**：

- 工作流步骤会被 checkpoint（检查点）；
- 任务等待消息时可以暂停，收到新消息后从原来的位置恢复；
- 即使中间发生崩溃或重新部署，会话也可以继续推进。

它基于 Vercel Workflow SDK 实现，是 Eve 最重要的生产特性之一。**真实 Agent 的核心问题，从来不是能不能循环，而是这个循环能不能在失败、等待和发布过程中保持正确状态。**

> ⚠️ 注意：durable 也不是免费的魔法。工具是否有副作用、恢复后会不会重复执行、操作是否幂等，仍然需要开发者设计。框架能保存执行状态，却不能替业务代码决定"这笔退款到底能不能再调用一次"。

## 人工审批：成熟的 Agent 要知道什么时候停手

Agent 能调用工具，不代表每个工具都应该自动执行。查询订单和取消订单不是一回事，查看部署记录和回滚生产版本也不是一回事。

Eve 内置了 **human-in-the-loop approval**。Agent 遇到需要人工确认的动作时，工作流可以暂停；用户批准或拒绝后，再从当前状态继续。更重要的是，审批不只存在于某个专用后台——Eve 的 channel 可以把审批映射到实际交互界面，例如在 Slack 中显示按钮。

```ts
// tools/delete-database.ts
export const config = { requireApproval: true };

export default async function deleteDatabase({ confirm }: { confirm: boolean }) {
  // 执行前会暂停，等待人工在 Vercel Dashboard 批准
  if (!confirm) throw new Error("Approval required");
  return db.delete();
}
```

这会迫使开发者认真回答一个问题：**Agent 的自动化边界究竟画在哪里？** 一个实用的起点是：
- 读取与分析操作可以自动执行；
- 会修改外部系统的操作需要审批；
- 删除数据、回滚生产和大额付费等高风险操作需要更严格确认。

真正成熟的 Agent，不是什么都敢做，而是知道什么时候必须停下来等人。

## Connections：安全连接，模型不接触凭证

连接外部系统时，Eve 通过 Vercel Connect 处理 OAuth 授权、同意页面和 token 刷新，让模型不直接看到连接地址和凭据。

```json
// connections/slack.json
{
  "type": "mcp",
  "server": "https://mcp-slack.example.com",
  "auth": "vercel-connect"
}
```

服务端也可以使用 `defineMcpClientConnection` 定义 MCP 客户端连接：

```ts
import { connect } from "@vercel/connect/eve";
import { defineMcpClientConnection } from "eve/connections";

export default defineMcpClientConnection({
  url: "https://mcp.linear.app/sse",
  description: "Linear workspace: issues, projects, cycles, and comments.",
  auth: connect("linear"),
});
```

模型永远看不到 URL 或凭证，Vercel Connect 自动处理 OAuth 和 token 刷新。支持 Slack、GitHub、Snowflake、Salesforce、Notion、Linear 等服务。

## Channels：多渠道接入

Eve 默认提供 HTTP API，也可以通过 channel adapter 接入 Slack、Discord、Teams、Telegram、GitHub、Linear 等入口。它希望**同一份 Agent 逻辑能够服务多个渠道**，而不是每接一个聊天工具就重写一遍业务流。

```ts
import { connectSlackCredentials } from "@vercel/connect/eve";
import { slackChannel } from "eve/channels/slack";

export default slackChannel({
  credentials: connectSlackCredentials("slack/my-agent"),
});
```

官方支持 8+ 通道：Web Chat、Slack、Google Chat、Discord、Microsoft Teams、WhatsApp、API、Twilio、Cron、Linear 等，多层复用了 Vercel Chat SDK 与 Connect。

## Tracing：可观测性

Agent 运行后，每次模型调用、工具调用以及沙箱命令都可以进入 trace。Eve 使用 **OpenTelemetry** 标准，因此可以接入现有可观测平台（Braintrust、Honeycomb、Datadog 等）；部署在 Vercel 上时，还可以在 Agent Runs 中查看会话执行过程。

这解决了长期问题：**AI Agent 的行为不可解释**。Eve 通过结构化日志和执行流程展示，让整个系统变得更接近传统软件调试体验。

## Evals：评测与回归

instructions、skills 和 tools 都是代码库中的文件，一次看似无害的修改也可能改变 Agent 行为。Eve 提供评测能力（`eve eval`），可以在本地运行，也可以接入 CI，把行为回归挡在部署之前。

```ts
// 定义带评分标准的测试套件
// 每次部署和按计划运行评测
```

它能回答：改了一句 instructions，怎么确认旧能力没有悄悄退化？Eve 把评测当作回归测试来管。

## 六大能力如何共同回答生产问题

这六个能力共同回答了一个经常被 Demo 忽略的问题：

> Agent 上线之后，用户从哪里找到它（Channels），出错以后怎么复盘（Tracing），升级之前又怎么验证（Evals）？

能回答这三个问题，才算真正开始把 Agent 当软件工程来做。

## 本章小结

本章详解了 Eve 的六大生产级能力：`durable execution`（持久化执行、checkpoint、暂停/恢复）、`human-in-the-loop approvals`（人工审批、审批边界）、`connections`（安全连接、OAuth）、`channels`（多渠道接入）、`tracing`（OpenTelemetry 可观测）、`evals`（评测回归）。这些能力对应了生产系统的非功能性需求：可靠性、安全性、可观测性、可维护性、可扩展性。

下一章将进入进阶能力，详解 subagents、schedules 与多 Agent 协作实战。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [02 目录结构与核心能力](./02-directory-core-capabilities.md) | [README](./README.md) | → [04 进阶能力](./04-advanced-capabilities.md) |