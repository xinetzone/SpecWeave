---
id: "zleap-agent-wiki-model-providers-runtime"
title: "模型提供方与运行时入口"
source: "https://github.com/Zleap-AI/Zleap-Agent + 本地源码 d:\spaces\SpecWeave\external\libs\Zleap-Agent"
category: "learning"
tags: ["zleap-agent", "model-provider", "openai-compatible", "anthropic", "sse", "conversation-service", "web-ui", "cli", "inbound", "outbound"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Zleap-Agent 模型提供方与运行时入口：OpenAI-compatible/Anthropic 提供方抽象、ProviderRegistry/ModelRegistry、SSE 流式；Web UI 与 CLI 入口；ConversationService 作为所有触发统一入口与 inbound→reply→流式回传数据流。"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 05 模型提供方与运行时入口

本章讲清楚"模型从哪里来"以及"所有入口如何汇聚到同一个运行时"。

## 5.1 模型提供方抽象

`packages/ai` 封装了模型提供方与模型调用抽象：

| 文件 | 职责 |
|------|------|
| `providers/openai-compatible.ts` | OpenAI-compatible 模型提供方抽象 |
| `providers/anthropic.ts` | Anthropic 提供方 |
| `providers/sse.ts` | SSE（Server-Sent Events）流式读取 |
| `registry.ts` | `ProviderRegistry` / `ModelRegistry` |
| `types.ts` | Model / ProviderAdapter / ProviderCapabilities 类型 |
| `embeddings.ts` | Embedding 提供方 |

### 注册表机制

`registry.ts`：

- `ProviderRegistry`：按 `provider.id` 注册/查找提供方。
- `ModelRegistry`：按 `model.id` 注册/查找模型。
- `resolveProviderCapabilities`：把模型能力（工具调用、缓存断点、thinking、tokenizer）与提供方能力合并，得到最终能力集。

### 能力解析

```ts
capabilities = {
  toolCalling:     model?.supportsTools ?? provider.toolCalling,
  cacheBreakpoints: model?.supportsCache ?? provider.cacheBreakpoints,
  thinking:        model?.supportsThinking ?? provider.thinking,
  tokenizer:       model?.tokenizer ?? provider.tokenizer,
  maxOutputTokens: model?.maxOutputTokens,
};
```

模型能力优先，其次才是提供方能力；`cacheBreakpoints` 与 02 章的缓存断点机制呼应。

## 5.2 Web UI 与 CLI 入口

- **Web UI**：`packages/web`（Next.js）。`app/` 下定义了大量 API 路由（chat、conversations、spaces、skills、models、mcp、memory、tasks、workspace、projects、gateway 等），`app/api/chat/route.ts` 是对话入口。
- **CLI**：`packages/cli`。与 Web 共用同一套运行时，提供 `init`、`config`、`sessions`、`connect`、`serve`、`setup`、`models`、`doctor`、`rollback`、`upgrade` 等命令。

## 5.3 ConversationService：所有触发的统一入口

`packages/agent/src/conversation/service.ts` 的 `ConversationService` 是 **L2 会话层**，也是**每个触发（Web、定时任务、IM 网关）都会调用的唯一入口**。

### 职责

- 解析会话身份（identity）。
- 从 store 加载历史（或干净运行）。
- 解析模型（store → space → default → env）。
- 按会话串行化（per-conversation mutex + 全局 semaphore）。
- 通过共享 store 的 ChatEngine 调用 agent，并流式回传回复。
- 持久化是引擎运行的副作用。

### 数据流（inbound → reply → 流式回传）

```text
inbound (Web/CLI/IM/任务)
  → ConversationService.handle()
  → 解析 actor / 会话 / 历史
  → resolveModel
  → ChatEngine.reply(messages, systemPrompt, signal)
  → 流式 yield ChatDelta（delta / space_result / error / done）
  → 回传给调用方
```

### 关键机制

- **命令拦截**：斜杠命令（如 `/stop`、`/new`）在 `handle` 内被拦截，不进入 agent。
- **`/stop`**：绕过 per-chat 锁，中止正在进行的回复。
- **`/new`**：`resetConversation` 提升历史 epoch，丢弃旧缓存引擎，开启新上下文。
- **历史 epoch**：`epochConversationId` 用 `.e` 分隔符，`/new` 后会话 id 变为 `{conversationId}.e{epoch}`，且 epoch 持久化到线程元数据，重启后仍生效。
- **引擎缓存**：稳定调用方（IM/CLI/任务）复用 LRU 缓存引擎；Web 因每次请求参数不同而新建引擎。
- **`deliver`**：无需 inbound 触发即可向会话推送消息（cron/task → IM）。

### 架构洞察

> **洞察 9（呼应洞察 1）：让"所有触发"统一走 ConversationService，是"多入口单智能"的基石。** Web、定时任务、IM 网关甚至 `deliver` 推送，都复用同一套会话/模型/历史/权限逻辑，避免每个入口各自实现一套 Agent 调用（来源：`packages/agent/src/conversation/service.ts`）。

## 5.4 运行组装（Avatar）

`packages/avatar` 负责把不同触发组装成一次运行：

- `inboundRun.ts`：inbound 触发的运行。
- `webChatRun.ts`：Web 聊天运行。
- `scheduledRun.ts`：定时运行。
- `runAssembly.ts`：通用的运行组装。

这些组装最终汇入 `ConversationService` 或 `ChatEngine`。

## 本章小结

- 模型提供方通过 `ProviderRegistry` / `ModelRegistry` 注册，支持 OpenAI-compatible 与 Anthropic，SSE 流式，模型能力优先于提供方能力。
- Web（Next.js）与 CLI 共用同一运行时。
- `ConversationService` 是所有触发的统一入口，负责身份/历史/模型/串行化/流式回传，并支持命令拦截、`/stop`、`/new`（历史 epoch）。
- `avatar` 包负责不同触发的运行组装。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [04 Skill 与工具权限](./04-skills-tools-permissions.md) | [README](./README.md) | → [06 IM 网关与定时任务](./06-gateway-tasks.md) |