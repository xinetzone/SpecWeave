---
id: "eve-wiki-02"
title: "目录结构与核心能力"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "instructions", "tools", "skills", "sandbox"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 目录结构详解：agent.ts 模型配置、instructions.md 指令、tools 工具、skills 技能、sandbox 沙箱五大核心能力。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 02 目录结构与核心能力

## 目录结构总览

Eve 的 "一个 Agent 就是一个目录" 设计，核心体现在 `agent/` 目录下的各文件/子目录。每个文件或子目录承担一个职责，框架通过文件约定自动发现与组合，无需胶水代码。

```
my-agent/
└── agent/
    ├── agent.ts          # 模型与运行时配置
    ├── instructions.md   # 始终生效的系统指令
    ├── tools/            # TypeScript 工具（文件名即工具名）
    ├── skills/           # Markdown 操作手册（按需加载）
    ├── sandbox/          # 沙箱配置（可选）
    ├── subagents/        # 子 Agent
    ├── channels/         # 多渠道入口
    ├── connections/      # 服务认证连接
    └── schedules/        # 定时任务
```

## agent.ts：模型与运行时配置

`agent.ts` 用于选择模型或配置运行时。Eve 默认使用一个默认模型，当你需要自定义模型时添加 `agent.ts`。

```ts
import { defineAgent } from "eve";

export default defineAgent({
  model: "openai/gpt-5.4-mini",
});
```

Eve 通过 Vercel AI Gateway 调模型，天然支持 provider fallback（模型故障时自动切换）。例如在 `model.md` 中可配置：

```
anthropic/claude-sonnet-4
# fallback: openai/gpt-4o
```

## instructions.md：始终生效的系统指令

`instructions.md` 是 Agent 的"人格"与行为规则。它类似传统软件的核心配置或系统说明书，开发者在这里定义 Agent 的身份、能力边界以及行为方式。

```markdown
# Identity

You are an expert weather assistant.

You can fetch the weather for any
city in the world.
```

Eve 会在运行时读取这个文件，并作为 Agent 的基础上下文。**Agent 的"人格"和"行为规则"不再是隐式存在于 Prompt 中，而是显式地成为项目的一部分**——Prompt 不再是临时拼接的字符串，而是工程资产。

## tools/：文件即工具，TypeScript 定义

在 Eve 中，一个工具就是一个 TypeScript 文件。开发者只需要在 `tools/` 目录下创建对应文件，系统就会自动识别并注册为 Agent 可调用的能力。**文件名即工具名，自动注册，无需装饰器或配置。**

```ts
import { defineTool } from "eve/tools";
import { z } from "zod";

export default defineTool({
  description: "Get the weather for a city",
  inputSchema: z.object({
    cityName: z.string(),
  }),
  async execute(input) {
    const res = await fetch(
      `${process.env.WEATHER_API_URL}/current?city=${input.cityName}`
    );
    const data = await res.json();
    return data.current_condition[0];
  },
});
```

这种设计有两个明显特点：
1. **降低认知成本**：不需要再去注册工具、配置 schema 或维护复杂的调用链路。
2. **强化工程一致性**：工具与代码天然在同一体系中，不再是"外挂式 API"。

## skills/：可复用的行为经验层

Skills 是 Markdown 格式的"操作手册"（playbook），在 Agent 相关性被触发时按需加载。它让 Agent 获得聚焦的指导，而无需在每次 prompt 中携带全部内容。

```markdown
---
description: Research unfamiliar topics
---

When the task is novel or ambiguous,
gather evidence first, then answer.
```

Skills 的关键点在于**"可复用"和"按需加载"**。在传统 Prompt 工程中，我们常常把所有规则都堆在系统提示词里，导致上下文臃肿。而 Eve 的方式是将这些能力拆分为独立模块，在需要时再组合——更接近现代软件中的"插件机制"。

Skills 与 Tools 的职责分离是 Eve 的核心架构思想：
- **Tools（能力层）**：稳定、通用、可复用，由开发者维护，实现"能做什么"。
- **Skills（知识层）**：易变、业务相关，承载"知道什么"，由领域专家可直接编辑 Markdown。

## sandbox/：沙箱隔离，安全执行

Eve 为每个 Agent 提供隔离沙箱。模型生成的代码应被视为不可信输入，如果直接放进应用运行时执行，一次错误的路径判断、依赖安装或文件删除，都可能把 Agent 问题变成生产事故。

Eve 的沙箱设计态度是：**不是禁止 Agent 写代码，而是默认它写出的代码不值得信任。**

默认情况下，每个 Agent 都包含一个隔离沙箱和文件工具。本地开发可以使用 Docker、microsandbox 或 just-bash 等适配器；部署到 Vercel 后，执行环境可以切换到 Vercel Sandbox，而无需改写 Agent 的业务逻辑。

如需自定义沙箱后端，可添加 `sandbox/sandbox.ts`：

```ts
import { defineSandbox, vercelSandboxBackend } from "eve/sandbox";

export default defineSandbox({
  backend: vercelSandboxBackend({
    runtime: "node24",
  }),
});
```

## 本章小结

本章详解了 Eve 目录结构的五大核心能力：`agent.ts`（模型配置）、`instructions.md`（系统性指令）、`tools/`（文件即工具）、`skills/`（按需加载的 Markdown 操作手册）、`sandbox/`（隔离执行）。核心是"文件约定 + 自动发现"——开发者只需按约定放置文件，框架自动完成组合。

下一章将进入生产级能力，详解 durable execution、人工审批、connections、channels、tracing 与 evals。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [01 产品介绍与核心概念](./01-product-intro.md) | [README](./README.md) | → [03 生产级能力详解](./03-production-capabilities.md) |