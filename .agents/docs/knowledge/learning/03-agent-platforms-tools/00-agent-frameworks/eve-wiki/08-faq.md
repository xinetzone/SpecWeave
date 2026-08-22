---
id: "eve-wiki-08"
title: "FAQ、适用范围与局限性"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "faq", "limitations", "scope"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve 常见问题解答、适用团队范围与当前局限性。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 08 FAQ、适用范围与局限性

本章以问答形式汇总 Eve 使用过程中的常见问题、适用团队范围与当前局限性，帮助读者快速判断 Eve 是否适合自身项目，以及如何正确看待其能力边界。

## 常见问题 FAQ

### Q：Eve 和 AI SDK / Agent SDK 的区别是什么？

**A：** Vercel AI SDK 是底层开发工具，帮助应用调用不同模型、处理流式输出、生成结构化数据、完成 Tool Calling；Eve 站在更外面一层，它假设 Agent 不只会调用一次模型，而是一个可能运行很久、调用真实系统、等待人类输入、跨多个渠道工作的完整应用。Eve 底层本身也在使用 Vercel 的 AI Gateway、Workflow、Sandbox 和 Connect 等能力，不是推翻现有 AI 开发栈，而是把这些原语组合成约定更完整的 Agent 框架。

### Q：Eve 是不是"又一个 Agent Loop"框架？

**A：** 不是。Eve 想解决的不是"怎么让模型多思考几轮"，而是"怎么把一个已经能工作的 Agent，变成可以部署、可以暂停恢复、可以控制权限、可以观察和评测的生产系统"。重点不只是 Agent Loop，更接近一套生产级 Agent Harness（模型之外还需要状态、权限、工具、执行环境、反馈、审计和验证）。

### Q：Eve 是免费的吗？许可证是什么？

**A：** Eve 是开源框架，采用 Apache 2.0 许可证。

### Q：Eve 目前支持哪些平台部署？

**A：** 目前默认仅支持 Vercel 原生部署，其他平台"即将支持"（coming soon）。部署在 Vercel 时，沙箱会自动切换为 Vercel Sandbox。

### Q：Eve 用什么语言开发？

**A：** TypeScript。Agent 的工具用 TypeScript 文件定义，非 TS 团队需要适配。

### Q：Eve 当前处于什么阶段？

**A：** public preview / beta。官方 README 明确提示：在正式可用之前，框架、API、文档和行为都可能发生变化。

## 适用范围

### Q：哪些团队适合现在尝试 Eve？

**A：** 适合以下场景的团队：

- 任务会持续较长时间、需要暂停恢复的团队；
- Agent 需要运行脚本或处理文件的团队；
- 需要接入 GitHub、Slack、Linear 等团队系统的团队；
- 存在必须人工确认的高风险动作的团队；
- 希望用 Git、Preview、CI 管理 Agent 变更的团队；
- 项目本身已使用 Vercel 技术栈的团队。

### Q：哪些情况不适合用 Eve？

**A：** 以下情况需谨慎评估：

- 如果只是给现有接口增加一次简单模型问答，直接使用 AI SDK 或模型 SDK 更轻；
- 强依赖私有化部署的团队；
- 已有成熟工作流平台的团队；
- 暂时无法接受 beta API 变化的团队，不适合急着把核心业务押上去。

## 局限性与认知澄清

### Q：durable execution 是不是免费的魔法？

**A：** 不是。工具有没有副作用、恢复后会不会重复执行、操作是否幂等，仍然需要开发者设计。框架能保存执行状态，却不能替业务代码决定"这笔退款到底能不能再调用一次"。

### Q：子 Agent 是不是越多越好？

**A：** 不是。能拆不等于应该拆。子 Agent 会增加模型调用、延迟和结果汇总成本。如果一个工具调用就能完成的任务，没必要为了"多 Agent"三个字绕上一圈。

### Q：Agent 真上生产会用在哪里？

**A：** Vercel 内部已有超过 100 个 Agent 在生产环境运行，例如数据分析 Agent 每月处理超过 30000 个问题、销售 Agent 自动跟进线索、支持 Agent 处理工单、内容 Agent 做文章审核、路由 Agent 负责把请求分发给合适的 Agent。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [07 工程化理念与趋势洞察](./07-engineering-philosophy-trends.md) | [README](./README.md) | → [09 术语表与参考资源](./09-glossary-resources.md) |