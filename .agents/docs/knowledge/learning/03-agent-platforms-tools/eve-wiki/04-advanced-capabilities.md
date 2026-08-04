---
id: "eve-wiki-04"
title: "进阶能力：子 Agent、定时任务与多 Agent 协作"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "subagents", "schedules", "multi-agent"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 进阶能力详解：subagents（子 Agent 委派）、schedules（定时任务）、以及多 Agent 协作实战模式（AI 内容运营团队案例）。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 04 进阶能力：子 Agent、定时任务与多 Agent 协作

## Subagents：子 Agent 委派

Eve 支持子 Agent。子 Agent 仍然是一个目录，可以有自己的 instructions、tools、skills、模型和沙箱。主 Agent 把它当作工具调用，子 Agent 在干净的上下文中完成任务，再把结果交还给主 Agent。

```ts
// subagents/investigator.ts
import { defineAgent } from "eve";

export default defineAgent({
  description: "Investigate questions",
  model: "openai/gpt-5.4",
});
```

**子 Agent 的价值并不是把一个头像变成五个头像，而是两个更实际的问题：**

1. **复杂任务可以拆成边界更清楚的子任务**；
2. **不同任务可以使用不同上下文和最小权限工具**。

例如在一次线上事故中：
- 日志分析 Agent 只读取日志与指标；
- 代码调查 Agent 只查看 GitHub 变更；
- 影响评估 Agent 只查询订单和用户数据；
- 主 Agent 负责综合证据并决定下一步。

这种隔离不仅能减少上下文污染，也能缩小每个 Agent 的权限范围。

> ⚠️ 不过，能拆不等于应该拆。子 Agent 会增加模型调用、延迟和结果汇总成本。如果一个工具调用就能完成的任务，没必要为了"多 Agent"三个字绕上一圈。

## Schedules：定时任务

Eve 提供 schedule 能力，使 Agent 可以定时执行任务，通过 cron 语法定义。这让 Agent 从"交互式工具"扩展为"后台运行的自动化系统"。

```markdown
---
cron: "0 8 * * *"
---

Send the user a daily weather
digest for their saved cities.
```

典型应用场景：
- 每天生成报告；
- 定期执行数据总结；
- 周期性触发外部工具；
- 每周摘要。

Schedules 基于 Vercel Workflows，工作在没有活跃会话的情况下也能持久地继续执行。

## 多 Agent 协作实战：AI 内容运营团队

只介绍功能列表，很难看出 Eve 解决的问题到底有没有价值。知乎深度解析文章提供了一个真实案例：使用 Eve 从零搭建一支 **AI 内容运营团队**，为 SpringForAll 社区（面向 Java 开发者的社区）提供内容输出。

这里最值得利用的正是 Eve 的目录设计：**一个 Agent 一个目录，一个目录对应一个岗位，多个目录组成一支团队。**

第一阶段的目标是"帮助维护 SpringForAll 社区内容"做出一个可运行的 Agent 雏形，并在实现过程中熟悉 Eve 的核心能力：

1. 先创建一个最小可运行的 Eve Agent，让它知道自己的角色和任务边界；
2. 在 Vercel AI Gateway 之外，保留切换自有 OpenAI-Compatible Provider 的能力；
3. 用 skills 沉淀选题、写作和审稿流程；
4. 用 researcher、writer、reviewer 三个 subagents 拆分内容团队职责；
5. 用 sandbox `/workspace` 承载研究笔记、草稿、审校结果和临时文件，避免污染 Agent 定义代码；
6. 最终生成可人工检查的 Markdown 内容包，而不是自动发布到公众号或其他平台。

这个案例展示了 Eve 的目录设计如何自然映射到"团队/岗位"的领域模型：每个岗位一个目录，通过 skills 沉淀流程、通过 subagents 拆分职责、通过 sandbox 隔离工作产物。

## 本章小结

本章详解了 Eve 的进阶能力：`subagents`（子 Agent 委派、上下文隔离、权限最小化）、`schedules`（定时任务、cron 语法）、以及多 Agent 协作实战模式（AI 内容运营团队，一个目录一个岗位）。核心价值是：Eve 的目录设计让"多 Agent 团队"的自然建模成为可能。

下一章将进入快速上手指南。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [03 生产级能力详解](./03-production-capabilities.md) | [README](./README.md) | → [05 快速上手指南](./05-quickstart.md) |