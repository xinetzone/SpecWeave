---
id: deepseek-harness-wiki-15
title: DeepSeek Harness Wiki - 生态与资源链接
source:
  - .temp/deepseek-harness-sources/01-tencent-cloud.md
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/03-deepseek-official.md
  - .temp/deepseek-harness-sources/04-deepseek-official-www.md
  - .temp/deepseek-harness-sources/05-sina-finance.md
  - .temp/deepseek-harness-sources/06-qq-news.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - resources
  - ecosystem
  - links
  - community
  - articles
category: learning
maturity: L1
---

# 15 生态与资源链接

恭喜你读完了整个教程！最后一章我们整理了 DeepSeek Harness 相关的所有官方资源、社区内容、深度阅读文章和生态动态，方便你继续学习、跟踪进展、参与社区。

建议你收藏几个核心链接，有空的时候回去看看更新。

---

## 官方资源

这些是 DeepSeek 官方维护的资源，是最权威的信息来源。

### 源码与仓库

| 资源 | 链接 | 说明 |
|------|------|------|
| **GitHub 主仓库** | [github.com/deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness) | dsh 源码、Issue、Releases、Discussions 都在这里 |
| **Cordis 元框架** | [github.com/cordiverse/cordis](https://github.com/cordiverse/cordis) | dsh 底层的插件化元框架，理解 Cordis 才能真正理解 dsh 的架构 |
| **Python SDK** | 主仓库内 `sdk/python/` 目录 | Python SDK 源码和示例 |
| **官方示例插件** | 主仓库内 `examples/` 目录 | 各种插件开发示例，写插件时参考 |

**GitHub 仓库建议操作**：
- 点个 ⭐ Star 关注项目
- 开启 Watch → Releases 通知，新版本发布时会收到邮件
- 看看 Issues 里别人遇到的问题
- 有使用问题去 Discussions 提问

### 官方网站与文档

| 资源 | 链接 | 说明 |
|------|------|------|
| **官方网站** | [deepseek.com/harness](https://deepseek.com/harness) | 产品介绍页、功能展示、快速开始 |
| **官方文档** | 官网 Docs 板块（持续更新中） | 官方文档、API 参考、配置指南 |
| **DeepSeek API 平台** | [platform.deepseek.com](https://platform.deepseek.com) | 申请 API Key、查看用量、计费信息 |
| **Cordis 论文** | 可在 GitHub 或 arXiv 获取 | Cordis 元框架的设计论文，讲「上下文作为效应代数」的核心思想，想深入理解架构一定要读 |

### API 相关资源

| 资源 | 链接 | 说明 |
|------|------|------|
| **DeepSeek API 文档** | [platform.deepseek.com/docs](https://platform.deepseek.com/docs) | DeepSeek 模型 API 的完整文档 |
| **DeepSeek 模型介绍** | [deepseek.com/models](https://deepseek.com/models) | V4 Pro、V4 Flash 等模型的能力介绍、定价、上下文窗口 |

---

## 社区与第三方资源

官方之外，社区也在快速产出各种内容和工具。

### 第三方指南与教程

| 资源 | 链接 | 说明 |
|------|------|------|
| **deepseekagent.io 指南** | [deepseekagent.io](https://deepseekagent.io) | 社区维护的非官方 dsh 指南网站，包含技巧、最佳实践、插件列表，更新比较及时 |
| **GitHub Discussions** | [主仓库 Discussions 板块](https://github.com/deepseek-ai/deepseek-harness/discussions) | 官方社区论坛，提问、分享经验、展示插件都在这里，核心开发者经常回复 |

### 插件生态

dsh 的插件生态刚起步，但已经有一些有意思的插件了：

| 资源 | 说明 |
|------|------|
| **GitHub `dsh-plugin` 标签** | 在 GitHub 搜索 `dsh-plugin` 标签，能找到社区开发的各种插件 |
| **官方插件市场** | v0.2 版本会推出内置的插件市场，现在还在开发中，可以关注进展 |
| **MCP 服务器生态** | dsh 原生支持 MCP，所以所有 MCP 服务器都可以直接在 dsh 里用，不需要专门为 dsh 开发 |

如果你开发了插件，建议给仓库打上 `dsh-plugin` 标签，方便别人找到。

---

## 推荐深度阅读文章

这些文章能帮你从不同角度理解 dsh 的架构设计、产品定位和行业意义，比简单的使用教程更有深度。

### 技术架构分析

| 文章 | 作者 | 推荐理由 |
|------|------|----------|
| **《DeepSeek Harness 架构深度解析》** | Tony Bai | Tony Bai 是 Go 语言圈知名的技术作者，这篇文章从架构师视角深入分析了 dsh 的「一切皆插件」设计、Cordis 元框架、Capability Seam 抽象，是理解 dsh 设计思想最好的第三方文章。写插件或做架构研究必读。 |
| **《Cordis 论文》** | DeepSeek Cordis 团队 | 官方技术论文，从效应代数（Effect Algebra）的角度讲插件组合的数学基础，比较偏理论，但能帮你理解为什么 dsh 敢说自己「没有特权内核」。 |

### 产品评测与体验

| 文章 | 来源 | 推荐理由 |
|------|------|----------|
| **《我们测了 DeepSeek Harness：这可能是最灵活的开源 Agent 运行时》** | 极客公园 | 极客公园做的实际体验评测，从产品角度对比了 dsh 和 Claude Code、Codex 的差异，有实际的任务测试案例，适合想快速了解它实际用起来怎么样的读者。 |

### 商业与行业分析

| 文章 | 来源 | 推荐理由 |
|------|------|----------|
| **《DeepSeek 开源自研 Agent 框架 Harness：AI 编程生态的关键一步》** | 新浪财经 | 从商业和行业竞争角度分析 dsh 的定位和意义，讲了为什么 DeepSeek 做 Harness 不是重复造轮子，以及它对整个 AI 编程生态可能的影响。适合关心行业趋势的读者。 |

---

## 同类 Harness 对比参考

理解一个工具最好的方式之一是对比它的同类产品。这里列几个主要的竞品/同类项目，你可以都试试，找到最适合自己的。

| 项目 | 出品方 | 开源 | 核心特点 | 适合场景 | 和 dsh 的主要差异 |
|------|--------|------|----------|----------|------------------|
| **Claude Code** | Anthropic | ❌ 闭源 | 开箱即用、稳定、体验流畅 | 日常编程、生产使用 | 闭源、扩展能力有限（hooks/MCP）、主要优化 Claude 模型、终端 UI |
| **Codex CLI** | OpenAI | 🟡 半开源 | 官方 Responses API 支持、和 OpenAI 生态深度集成 | OpenAI 生态用户 | 扩展能力中等、主要优化 OpenAI 模型、终端 UI |
| **Cursor** | Cursor Inc | ❌ 闭源 | IDE 深度集成、体验最丝滑 | 写代码的日常使用 | 是 IDE 不是独立运行时、扩展能力有限、闭源 SaaS |
| **Continue.dev** | Continue 团队 | ✅ 完全开源 | VS Code/JetBrains 开源插件、可定制 | IDE 内 AI 辅助 | 重点在 IDE 集成、不是独立的 Agent Harness、可观测性弱于 dsh |
| **OpenHands (原 OpenDevin)** | 社区 | ✅ 完全开源 | 自主编程 Agent、Web UI | 研究自主 Agent | 偏向「完全自主」的 Agent 设计、不是框架/SDK、定制能力不如 dsh |
| **LangChain / LangGraph** | LangChain | ✅ 完全开源 | 工作流编排、灵活的 Agent 链 | 自定义工作流、数据场景 | 是编排框架不是现成的编程 Harness、需要大量胶水代码、缺少内置工具和运行时 |

### 对比总结

简单说：
- 想要**开箱即用、稳定省心**：Claude Code / Cursor / Codex
- 想要**IDE 内体验**：Cursor / Continue
- 想要**自主 Agent 研究**：OpenHands
- 想要**工作流编排、做数据/业务 Agent**：LangGraph
- 想要**可控、可扩展、可观测、能嵌入、能换模型、能改 Agent 循环本身**：DeepSeek Harness

没有谁比谁更好，只是定位不同。你完全可以几个都装，根据任务选最合适的用——它们可以共存，互不干扰，甚至可以通过 hooks/MCP/ACP 互相调用。

---

## 生态动态与新闻

dsh 开源时间不长，但生态已经开始有一些有意思的进展了。

### 已落地的集成

| 动态 | 说明 |
|------|------|
| **腾讯 QQ Bot 接入 dsh** | 腾讯 QQ 官方机器人平台已经接入 dsh 作为执行引擎，QQ Bot 开发者可以直接用 dsh 给机器人加编程和复杂任务能力。这说明 dsh 的嵌入能力已经得到了大厂的验证。 |
| **DeepSeek V4 Pro 上线国家超算互联网** | DeepSeek V4 Pro 模型（dsh 默认优化最好的模型）已经上线国家超算互联网平台，国内企业用户可以通过超算互联网稳定调用 V4 Pro，配合 dsh 使用。 |

### 未来值得关注的方向

根据官方透露的信息和代码里的线索，这些方向值得关注：

1. **v0.2 版本**：重点优化 Token 消耗、性能、插件市场
2. **VS Code 插件**：官方 IDE 插件在开发中，以后可以在 VS Code 里直接用 dsh
3. **ACP 生态成熟**：Agent 间通信协议落地后，多 Agent 协同会变得容易
4. **更多官方插件**：官方会陆续推出更多官方插件（记忆、长上下文、团队协作等）
5. **稳定版 v1.0**：等核心接口稳定后，会发布生产可用的 1.0 版本

生态才刚刚开始，未来几个月应该会有很快的演化。

---

## 本教程说明

### 关于本教程

本教程是 DeepSeek Harness v0.1 版本的社区中文指南，基于官方文档、源码分析、实际使用体验和公开资料编写。

- **教程版本**：基于 v0.1.0-rc.6 版本编写
- **数据截止日期**：2026-08-15
- **适用版本**：v0.1.x 系列的 rc 版本
- **协议**：本教程采用 CC BY-NC-SA 4.0 协议共享

### 来源说明

本教程参考了以下公开资料：

| 来源 | 内容 |
|------|------|
| DeepSeek 官方 GitHub 仓库 | 源码、README、文档、Issue、Discussions |
| DeepSeek 官方网站 deepseek.com/harness | 产品介绍、官方文档 |
| Tony Bai 架构分析文章 | Cordis 架构、插件设计、Capability Seam 解析 |
| 极客公园评测文章 | 实际使用体验、竞品对比 |
| 新浪财经商业分析 | 行业定位、生态意义 |
| QQ 新闻/腾讯云公告 | QQ Bot 集成、国家超算上线新闻 |
| deepseekagent.io 社区指南 | 最佳实践、常见技巧 |
| 实际使用测试 | 安装、配置、四个模式、插件开发、SDK 使用的第一手体验 |

### 反馈与勘误

如果你在阅读过程中发现错误、过时的内容、或者有建议：
- 可以在 SpecWeave 仓库提 Issue
- 或者在 dsh 官方 Discussions 指出
- 也欢迎你直接修改补充，本教程本身也是开源的

---

## 写在最后

DeepSeek Harness 不是一个完美的工具——它还是 v0.1 预览版，有 bug，会变，文档不全，Token 效率还有待优化，Windows 体验不够好。

但它打开了一扇门：在它之前，好用的编程 Agent 大多是闭源黑盒；在它之后，我们有了一个真正开源、真正可控、一切皆可扩展的 Agent 运行时，你不仅能用它，还能看它怎么工作，改它的任何一个部分，把它嵌入到你自己的系统里。

AI Agent 生态还在非常早期的阶段，今天我们看到的工具可能一两年后会完全不一样。但「开放、可控、可扩展、本地优先」这些设计原则，我相信是对的方向。

希望这个教程帮你快速上手了 dsh。接下来，去用它解决实际问题吧——工具的价值永远是在使用中体现的。如果你写了有意思的插件，或者用它做了酷的东西，记得去社区分享。

祝你玩得开心 🚀

---

← [14 适用场景](14-use-cases-limitations.md) | 回到 [00 总览](00-overview.md)
