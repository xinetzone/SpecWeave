---
id: "eve-wiki-06"
title: "竞品对比与选型"
source: "eve-framework-wiki-learning"
category: "learning"
tags: ["eve", "vercel", "agent-framework", "mastra", "langgraph", "comparison", "selection"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Eve vs Mastra vs LangGraph 多维对比、关键差异与适用团队边界、选型决策树与不适合的场景。"
last_verified: "2026-08-04"
wiki_version: "1.0"
eve_version_target: "2026 public preview"
---

# 06 竞品对比与选型

本章将 Eve 与当前主流的两大开源 Agent 框架——Mastra 与 LangGraph——进行多维对比，帮助读者判断"何时该选择 Eve、何时该选择其他框架"。Mastra 是一个跨平台的 TypeScript Agent 框架；LangGraph 则是以 Python 生态为核心、最成熟的图结构（Graph）工作流框架。三者都内置持久化（延续 Agent 执行状态的能力），但在部署边界、生产级能力开箱程度与生态成熟度上差异明显。

## 1. 多维对比表（Eve vs Mastra vs LangGraph）

以下对比数据来自 nixapi 博客的深度解析，覆盖语言、部署、持久化、沙箱、人工审批、MCP 支持、多通道、追踪、许可证与生产验证十个维度。

| 维度 | Eve | Mastra | LangGraph |
|------|-----|--------|-----------|
| 语言 | TypeScript | TypeScript | Python-first |
| 部署 | Vercel 原生（其他平台"即将支持"） | 任何平台 | 任何平台 |
| 持久化 | ✅ 内置（Workflow SDK） | ✅ 内置 | ✅ 内置 |
| 沙箱 | ✅ 内置（Vercel Sandbox） | ⚠️ 需配置 | ⚠️ 需配置 |
| 人工审批 | ✅ 内置 | ⚠️ 需配置 | ⚠️ 需配置 |
| MCP 支持 | ✅ 内置（Vercel Connect） | ✅ 支持 | ✅ 支持 |
| 多通道 | ✅ 内置 8+ 通道 | ⚠️ 需配置 | ⚠️ 需配置 |
| 追踪 | ✅ OpenTelemetry 内置 | ⚠️ 需配置 | ⚠️ 需配置 |
| 许可证 | Apache 2.0 | MIT | MIT |
| 生产验证 | Vercel 内部 100+ Agent | YC 支持，v1.0 已发布 | LangChain 生态，最成熟 |

简要解读：

- **持久化**：三者均内置，是 Agent 框架的标配能力，不构成差异化。
- **沙箱 / 人工审批 / 多通道 / 追踪**：Eve 均为"内置、零配置启用"，而 Mastra 与 LangGraph 需要自行配置或接入第三方方案，这是 Eve 最突出的差异点。
- **部署**：Eve 目前默认仅支持 Vercel，其他平台标注"即将支持"；Mastra 与 LangGraph 可部署到任意平台。
- **生态成熟度**：LangGraph 依托 LangChain 生态最成熟，已获 YC 支持并发布 v1.0 的 Mastra 次之，Eve 则处于刚发布、生态早期的阶段。

## 2. 关键差异与适用团队边界

### 2.1 Eve 的优势

- **开箱即用**：沙箱、人工审批、多通道、追踪、连接、持久化等六大生产级能力零配置启用，减少从 Demo 到生产的工程成本。
- **Vercel 生态深度整合**：部署、沙箱、连接（Connect）、追踪在 Vercel 体系内一键搞定，与现有的 Vercel 项目天然衔接。
- **真实生产验证**：Vercel 内部已在运行 100+ Agent，且约 29% 的部署由 Agent 触发，说明其能力经受住了内部生产环境的检验。

### 2.2 Eve 的局限

- **平台锁定**：目前默认仅支持 Vercel，其他平台仍在"coming soon"阶段，跨平台诉求需要等待。
- **生态早期**：刚发布不久，社区插件与第三方集成较少，可复用的成熟生态不如 LangGraph。
- **TypeScript 限定**：仅面向 TypeScript 团队，非 TS 团队需要额外的适配成本。

### 2.3 适合现在尝试 Eve 的团队特征（来自知乎）

如果团队满足以下大部分特征，Eve 值得现在尝试：

- 任务会持续较长时间，需要暂停和恢复（依赖持久化执行）。
- Agent 需要运行脚本或处理文件。
- 需要接入 GitHub、Slack、Linear 等团队系统。
- 存在必须人工确认的高风险动作。
- 希望用 Git、Preview 和 CI 管理 Agent 变更。
- 项目本身已经使用 Vercel 技术栈。

### 2.4 不适合的场景

- **仅需简单模型问答**：如果需求只是给现有接口增加一次简单的模型问答，直接使用 AI SDK（面向 AI 应用的轻量工具库）或模型 SDK 可能更轻，为一个两步流程引入完整 Agent 框架未必划算。
- **强依赖私有化部署**：需要自有服务器或私有化部署的团队，Eve 当前的 Vercel 绑定难以满足。
- **已有成熟工作流平台**：内部已存在成熟的编排/工作流平台时，重复引入框架收益有限。
- **无法接受 beta API 变化**：暂时无法接受 public preview / beta 阶段 API 频繁变化的团队，不宜急着把核心业务押上去。

## 3. 选型决策树

以下用缩进列表形式呈现选型决策分支，按问题优先级自上而下判断：

```
是否需要开箱即用的生产级能力（沙箱/审批/多通道/追踪）？
├─ 是 → 优先考虑 Eve
└─ 否 → 继续向下判断

是否已使用 Vercel 技术栈？
├─ 是 → Eve 最省心（部署/沙箱/连接/追踪一体化）
└─ 否 → 继续向下判断

是否必须跨平台 / 私有化部署，或团队非 TypeScript？
├─ 是 → Mastra（TypeScript 跨平台）或 LangGraph（Python 生态）
└─ 否 → 继续向下判断

是否需要最成熟的图 / 工作流生态？
├─ 是 → LangGraph（LangChain 生态最成熟）
└─ 否 → 继续向下判断

是否只是简单模型问答？
├─ 是 → 直接用 AI SDK / 模型 SDK，不需要框架
└─ 否 → 综合上面各因素，在 Eve / Mastra / LangGraph 中权衡
```

决策要点可归纳为：**先判断需求复杂度，再匹配技术栈与生态偏好**。简单问答不必上框架；需要生产级能力且已用 Vercel 则 Eve 优先；追求跨平台或 Python 生态则转向 Mastra / LangGraph。

## 4. 本章小结

- **Eve 的优势**在于"开箱即用 + Vercel 生态整合 + 真实生产验证"。
- **Eve 的局限**在于"平台锁定 + 生态早期 + TypeScript 限定"。
- **选型应综合判断**：基于团队技术栈、是否依赖 Vercel 生态、是否需要生产级能力三个维度综合决策。
- **核心提醒**：新框架最容易让人兴奋的是"它什么都有"，最容易被忽略的是"这些能力是否正好是你需要的"。选型应回归业务需求本身，而非被框架的功能清单牵着走。

下一章将进入工程化理念与趋势洞察。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [05 快速上手指南](./05-quickstart.md) | [README](./README.md) | → [07 工程化理念与趋势洞察](./07-engineering-philosophy-trends.md) |