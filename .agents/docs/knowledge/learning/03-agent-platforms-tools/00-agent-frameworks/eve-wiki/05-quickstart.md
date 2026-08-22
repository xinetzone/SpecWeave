---
id: "eve-wiki-05"
title: "快速上手指南"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "quickstart", "npm", "deploy"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 快速上手指南：官方九步上手流程、五步快速开始（agent.ts 定义模型、defineTool 定义工具）、最小指令先行、部署与本地开发说明。"
last_verified: "2026-08-04"
wiki_version: "1.1"
eve_version_target: "2026 public preview"
---

# 05 快速上手指南

## 方法一：官方九步上手流程（Vercel 产品页）

Eve 官方产品页给出了从零到生产 Agent 的九步流程。核心顺序是：先从 `instructions.md` 开始，再逐步添加模型、技能、工具、沙箱、渠道、连接、子 Agent 与定时任务。

| 步骤 | 文件/目录 | 做什么 | 说明 |
|------|----------|--------|------|
| 01 | `instructions.md` | 定义 Agent 身份与行为 | 一份 Markdown 就是完整 Agent，`eve` 命令即可运行 |
| 02 | `agent.ts` | 选择模型 | 需要自定义模型/运行时才添加 |
| 03 | `skills/` | 添加可复用操作手册 | 按需加载，不携带在每次 prompt 中 |
| 04 | `tools/` | 定义 TypeScript 工具 | 文件名即工具名，无需注册 |
| 05 | `sandbox/` | 自定义沙箱 | 每个 Agent 默认含隔离沙箱与文件工具 |
| 06 | `channels/` | 接入多渠道 | Slack、Discord、Teams、Web 等 |
| 07 | `connections/` | 处理服务认证 | GitHub、Stripe、Linear 等，无需管理 token |
| 08 | `subagents/` | 委派子 Agent | 主 Agent 委派任务并合并结果 |
| 09 | `schedules/` | 定时运行 | 日报、周报等，无需活跃会话 |

## 方法二：五步快速开始（nixapi）

nixapi 博客给出了更精简的五步快速开始：

### 步骤 1：初始化项目

```bash
npx eve@latest init my-agent
cd my-agent
```

### 步骤 2：定义模型（agent/agent.ts）

> ⚠️ **注意**：早期公开资料中提到的 `model.md` 写法已废弃。当前源码中，模型配置统一放在 `agent/agent.ts`，通过 `defineAgent` 声明。

```ts title="agent/agent.ts"
import { defineAgent } from "eve";

export default defineAgent({
  model: "openai/gpt-5.4-mini",
});
```

模型 ID 走 Vercel AI Gateway 路由，例如 `anthropic/claude-sonnet-5`、`openai/gpt-5.4-mini`。若要直接调用某供应商并按代码配置，可传入供应商的 `LanguageModel`：

```ts
import { anthropic } from "@ai-sdk/anthropic";
import { defineAgent } from "eve";

export default defineAgent({
  model: anthropic("claude-opus-4-8"),
});
```

> 注意 Gateway ID 用点号（`anthropic/claude-opus-4.8`），供应商原生 ID 用连字符（`claude-opus-4-8`）。`agent.ts` 可省略（此时默认 `anthropic/claude-sonnet-5`），但一旦存在就必填 `model`。

### 步骤 3：定义工具（agent/tools/search.ts）

```ts title="agent/tools/search.ts"
import { defineTool } from "eve/tools";
import { z } from "zod";

export default defineTool({
  description: "Search the example API by query.",
  inputSchema: z.object({ query: z.string().min(1) }),
  async execute({ query }, ctx) {
    const results = await fetch(`https://api.example.com/search?q=${query}`);
    return results.json();
  },
});
```

文件名即工具名（`search.ts` → 工具 `search`），自动注册，无需装饰器或配置。工具定义需含 `description`（写给模型看的说明）、`inputSchema`（Zod schema，必填，无输入用 `z.object({})`）、`execute(input, ctx)`（实现，可同步或异步）。

### 步骤 4：部署

```bash
vercel deploy
# 同一 Agent 目录，零改动部署到生产
```

## 方法三：最小指令先行（知乎）

最小的 Eve Agent，甚至可以从一份 `instructions.md` 开始。只需描述 Agent 的角色与任务边界，然后运行 `eve`：

```markdown
# Identity

You are an expert weather assistant.

You can fetch the weather for any
city in the world.
```

之后按需递增：选择模型加 `agent.ts`，调用业务接口加 `tools/`，可复用流程加 `skills/`，接入 Slack 加 channel 文件。

## 本地开发与生产部署

- **本地开发**：`eve` 命令的 dev 模式运行 Agent，可实时观察 Agent 调用了哪些工具、每一步的执行过程、中间状态如何变化。这种可观测性让调试更接近传统软件。
- **沙箱后端**：本地可用 Docker、microsandbox 或 just-bash；生产部署到 Vercel 后自动切换为 Vercel Sandbox，无需改写业务逻辑。
- **生产部署**：`vercel deploy` 将同一 Agent 目录零改动部署到生产，所有生产级能力（持久化、沙箱、审批、连接、追踪、评测）开箱即用。

## 环境要求

- Node.js 与 npm（TypeScript 项目）
- 需要 Vercel 账号（生产部署、Vercel Sandbox、Connect 等能力依赖 Vercel 生态）
- 模型 API Key（可通过 Vercel AI Gateway 配置）

## 本章小结

本章提供了三种快速上手路径：官方九步流程（从 instructions 到 schedules 的渐进构建）、五步快速开始（init → agent.ts 定义模型 → defineTool 定义工具 → deploy）、最小指令先行（一份 instructions.md 即可运行）。并说明了本地开发（dev 模式可观测）与生产部署（vercel deploy 零改动）的差异。其中模型配置与工具定义已按源码校准为 `defineAgent` 与 `defineTool` 写法。

下一章将进入竞品对比与选型。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [04 进阶能力](./04-advanced-capabilities.md) | [README](./README.md) | → [06 竞品对比与选型](./06-comparison-selection.md) |