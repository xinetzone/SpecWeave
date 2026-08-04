---
id: "eve-wiki-01"
title: "产品介绍与核心概念"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "nextjs-for-agents", "产品定位"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 产品定位（Next.js for Agents）、与 AI SDK/Agent Loop 的层次区分、以及'一个 Agent 就是一个目录'（filesystem-first）设计哲学。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 01 产品介绍与核心概念

## 什么是 Eve

Eve 是 Vercel 于 2026 年 6 月 17 日在年度 Ship 大会上发布的开源 AI Agent 框架（Apache 2.0 许可证）。官方定位是 **"Next.js for Agents"** ——就像 Next.js 简化了全栈 Web 开发，Eve 要简化 Agent 的开发、部署和运维。

Eve 的核心设计哲学是**文件系统优先（filesystem-first）**：一个 Agent 就是一个目录。在这个目录里，用 Markdown 定义指令（instructions）和技能（skills），用 TypeScript 定义工具（tools），框架会自动编译目录、接线持久化工作流、并连接多渠道。

Eve 官方称 "The filesystem is the authoring interface"——直译为「文件系统即创作接口」。这背后的主张是：**不要再把 Agent 藏在某个控制台的一堆配置项里，把它当成一个正常的软件项目来管理。**

## 关键区分：Eve 不是 AI SDK，也不是 Agent Loop

很多开发者会困惑：Vercel 已有 AI SDK，为什么还要做一个 Eve？两者解决的问题层次不同：

| 层次 | 主要解决的问题 |
|------|-------------|
| 模型与 AI SDK | 怎么调用模型、流式输出、结构化数据、Tool Calling |
| Agent Loop | 怎么观察、行动、获得反馈并继续 |
| **Eve** | **这个 Agent 如何持久运行、安全执行、接入业务并进入生产** |

Eve 底层本身也在使用 Vercel 的 AI Gateway、Workflow、Sandbox 和 Connect 等能力。它不是推翻现有 AI 开发栈，而是把这些原语组合成一个约定更完整的 Agent 框架。

借用业界流行的说法，**Eve 的重点不只是 Agent Loop，更接近一套生产级 Agent Harness**。模型负责推理，但模型之外还需要状态、权限、工具、执行环境、反馈、审计和验证——Eve 想把这层 Harness 产品化。

## 要解决的问题：Agent Demo 很多，真正能上线的却不多

现在做一个 Agent Demo 已经不难：写系统提示词、准备几个工具、调用模型，让它在「思考—调用工具—读取结果—继续思考」之间循环就能跑起来。但一旦放进真实业务，问题马上就来：

- 一个任务跑了半小时，中途进程重启怎么办？
- Agent 等用户批准时，连接要一直挂着吗？
- 模型生成的脚本，敢不敢直接在应用服务器上执行？
- 同一个 Agent 要接 Web、Slack 和 API，是不是每个入口都要重写一套？
- Agent 做错以后，怎么知道它当时看到了什么、调用了什么工具？
- 改了一句 instructions，怎么确认旧能力没有悄悄退化？

这些问题没有一个能靠"再优化一下 Prompt"解决。过去大家通常要自己把模型 SDK、工作流引擎、任务队列、状态存储、沙箱、OAuth、审批页面、日志系统和评测框架拼起来——Demo 的代码可能只有几百行，包住它的生产基础设施却很容易膨胀成另一个项目。

Eve 选择切入的位置正是这里：**把过去需要开发者自己拼装的 Durable Workflow、Sandbox、人工审批、子 Agent、渠道接入、Tracing 和 Evals 等能力，收进一个文件系统优先的框架里。**

## 核心设计哲学：目录即 Agent

Eve 最显眼的设计是 filesystem-first。一个典型项目大致长这样：

```
my-agent/
└── agent/
    ├── agent.ts          # 模型与运行时配置
    ├── instructions.md   # 始终生效的系统指令
    ├── tools/            # Agent 可以调用的类型化工具
    ├── skills/           # 按需加载的操作手册
    ├── subagents/        # 可委派任务的子 Agent
    ├── channels/         # HTTP、Slack、Discord 等入口
    └── schedules/        # 定时任务
```

最小的 Eve Agent，甚至可以从一份 `instructions.md` 开始。需要选择模型时增加 `agent.ts`；需要调用业务接口时在 `tools/` 中增加 TypeScript 文件；需要一套可复用的操作流程时写进 `skills/`；需要接入 Slack 就增加一个 channel 文件。

因为 Agent 的角色、工具、技能和入口都落在普通文件里，它们可以：
- 进入 Git 做版本管理；
- 通过 Pull Request 审查；
- 看到 instructions 修改前后的 diff；
- 对不同版本建立 Preview 环境；
- 出问题时回滚到上一个提交。

这也是它和很多低代码 Agent 平台最不一样的地方——**Eve 不是把 Agent 藏在配置项里，而是把它当成一个正常的软件工程来管理。**

## 本章小结

本章界定了 Eve 作为「Next.js for Agents」开源 Agent 框架的定位，区分了它与 AI SDK（模型调用层）、Agent Loop（观察行动层）的层次差异，指出它解决的是「Agent 如何持久运行、安全执行、接入业务并进入生产」的 Harness 层问题，并剖析了「一个 Agent 就是一个目录」的 filesystem-first 设计哲学。

下一章将进入目录结构，逐一详解 agent.ts / instructions.md / tools / skills / sandbox 五大核心能力。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [00 教程总览](./00-overview.md) | [README](./README.md) | → [02 目录结构与核心能力](./02-directory-core-capabilities.md) |