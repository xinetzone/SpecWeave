---
id: "zleap-agent-wiki-gateway-tasks"
title: "IM 网关与定时任务"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "gateway", "feishu", "wechat", "im", "channel-supervisor", "cron", "tasks", "worker"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent IM 网关与定时任务：飞书/微信/飞书 CLI 适配器、ChannelSupervisor、worker、dedup；定时任务服务（cron/queue/worker/service）；二者如何接入 ConversationService。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 06 IM 网关与定时任务

本章讲 Zleap-Agent 如何接入外部渠道（飞书/微信）以及如何定时触发 Agent 运行，两者都汇入 `ConversationService`。

## 6.1 IM 网关：飞书 / 微信

`packages/gateway` 提供 IM 网关 worker，让外部即时通讯渠道能驱动 Agent。

### 平台适配器

| 适配器 | 类 | 说明 |
|--------|-----|------|
| 飞书 | `FeishuAdapter` | 处理飞书消息并转为 internal Conversation 对象 |
| 微信 | `WeChatAdapter` | 微信接入（含 `ILinkClient`、`DbWeChatSessionStore`） |
| 飞书 CLI | `FeishuCliAdapter` | 通过飞书 CLI（Lark cli）接入，含 `LarkCliClient` |

- `base.ts` 定义 `BasePlatformAdapter`，含 `MAX_MESSAGE_LENGTH`、`SPLIT_THRESHOLD`、`SEND_ATTEMPTS` 等消息处理常量。
- `feishu/normalize.ts` 提供消息归一化：`acceptGroupMessage`、`extractText`、`flattenPost`、`mentionsBot`、`stripMentions`。

### 关键组件

| 组件 | 职责 |
|------|------|
| `ChannelSupervisor` | 管理各渠道（channel）的生命周期 |
| `worker.ts` | 网关 worker 运行入口 |
| `runner.ts` | 运行编排 |
| `dedup.ts` | 消息去重，避免重复消息触发重复处理 |

### 数据流

```text
飞书/微信消息
  → 平台适配器（归一化 → internal Conversation）
  → dedup 去重
  → ConversationService.handle()
  → agent 回复
  → 渠道 REST sender 回传
```

## 6.2 定时任务服务

`packages/tasks` 提供定时任务服务与 worker：

| 文件 | 职责 |
|------|------|
| `cron.ts` | cron 表达式解析与调度 |
| `queue.ts` | 任务队列 |
| `execution.ts` | 任务执行 |
| `worker.ts` | 任务 worker（轮询、后台任务、异步调度） |
| `service.ts` | 任务服务 |
| `registry.ts` | 任务注册 |

### 定时任务如何触发 Agent

定时任务通过 `ConversationService` 的 inbound（`kind: 'schedule'`）触发一次 Agent 运行，或通过 `deliver` 主动向会话推送内容。历史策略对 schedule 默认 `historySource: 'none'`（`defaultHistorySource`）。

### 架构洞察

> **洞察 10：网关与定时任务都只是"ConversationService 的外部触发器"。** 它们不重复实现 Agent 调用，而是把外部消息 normalize 成 inbound、或把定时触发包装成一次 run，再汇入统一的会话层——这正是多入口单智能架构的体现（来源：`packages/gateway/src/`、`packages/tasks/src/`）。

## 6.3 开发命令

| 命令 | 作用 |
|------|------|
| `pnpm dev:gateway` | 仅启动 IM 网关 worker |
| `pnpm dev:tasks` | 仅启动任务 worker |
| `pnpm dev` | Web UI + 任务 worker + 网关开发循环 |

## 本章小结

- **IM 网关**（飞书/微信/飞书 CLI）通过平台适配器把外部消息归一化为 internal Conversation，经 ChannelSupervisor 管理、dedup 去重后汇入 `ConversationService`。
- **定时任务**（cron/queue/worker/service）按 cron 触发 Agent 运行，或通过 `deliver` 主动推送。
- 网关与任务都是 ConversationService 的薄触发器，不重复实现 Agent 逻辑。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [05 模型提供方与运行时入口](./05-model-providers-runtime.md) | [README](./README.md) | → [07 快速上手指南](./07-quickstart.md) |