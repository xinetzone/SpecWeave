---
id: deepseek-harness-wiki-00
title: DeepSeek Harness Wiki - 总览导航
source:
  - .temp/deepseek-harness-sources/02-tonybai.md
  - .temp/deepseek-harness-sources/09-deepseekagent-io.md
  - .temp/deepseek-harness-sources/05-sina-finance.md
  - .temp/deepseek-harness-sources/06-qq-news.md
date: 2026-08-16
tags:
  - deepseek
  - agent
  - harness
  - dsh
  - cordis
category: learning
maturity: L1
---

# DeepSeek Harness Wiki 总览导航

## 教程简介

本教程系统介绍 DeepSeek Harness（dsh）—— DeepSeek 于 2026 年 8 月 13 日开源的 Agent 驾驭框架。与 Claude Code、Codex 等成品 Agent 不同，dsh 以「一切皆插件」为设计哲学，基于 Cordis 元框架构建，没有特权内核，模型适配器、工具注册表、会话日志乃至 Agent 循环本身均可替换。

本教程基于 v0.1.0-rc.6 版本实测编写，数据统计截止至 2026 年 8 月 15 日。

## 目标读者

- **开发者**：希望使用或扩展 DeepSeek 官方 Agent 运行时的工程师
- **架构师**：研究 Agent Harness 设计模式与插件化架构的技术决策者
- **插件开发者**：计划为 dsh 生态开发插件或自定义能力的开发者
- **评测人员**：需要干净可控工具面进行模型基准测试的研究人员

## 章节导航

| 章节 | 文件 | 摘要 | 学习顺序 |
|------|------|------|----------|
| 00 | [00-overview.md](00-overview.md) | 总览导航、核心概念、学习路径 | 1 |
| 01 | [01-introduction-background.md](01-introduction-background.md) | 项目介绍与背景、Harness 重要性、竞品对比、战略定位 | 2 |
| 02 | [02-installation-setup.md](02-installation-setup.md) | 环境准备（Node.js/API Key）、安装方法、配置目录结构 | 3 |
| 03 | [03-quickstart-first-task.md](03-quickstart-first-task.md) | Web UI 概览、工作区选择、模型配置、第一个任务 | 4 |
| 04 | [04-four-modes.md](04-four-modes.md) | 四种运行模式详解（Standard/Code/Minimal/Creator） | 5 |
| 05 | [05-architecture-everything-plugin.md](05-architecture-everything-plugin.md) | 核心架构："一切皆插件"、Cordis 元框架、Profile 与 Bundle 机制 | 6 |
| 06 | [06-agent-loop-events.md](06-agent-loop-events.md) | Agent 循环与事件模型：Turn/Step、三类事件、瀑布型拦截 | 7 |
| 07 | [07-session-log-observability.md](07-session-log-observability.md) | 会话日志可观测性、Trajectory 轨迹视图、分叉/恢复/回放 | 8 |
| 08 | [08-model-configuration.md](08-model-configuration.md) | 模型配置、多 Provider 支持、三档思考强度、自定义模型 | 9 |
| 09 | [09-tools-capability-seam.md](09-tools-capability-seam.md) | 工具系统与 Capability Seam 抽象、三角色模型、一次替换全局生效 | 10 |
| 10 | [10-plugin-development.md](10-plugin-development.md) | 插件开发入门、事件监听、可逆效应、社区生态 | 11 |
| 11 | [11-ecosystem-interop.md](11-ecosystem-interop.md) | 与 Claude Code/Codex/MCP 生态互操作、hooks 桥接、任务委托 | 12 |
| 12 | [12-headless-sdk.md](12-headless-sdk.md) | 无头模式、Python SDK（自带 Node 运行时）、JSON-RPC、ACP | 13 |
| 13 | [13-faq-troubleshooting.md](13-faq-troubleshooting.md) | 10+ 常见问题与故障排查、配置文件速查、帮助渠道 | 14 |
| 14 | [14-use-cases-limitations.md](14-use-cases-limitations.md) | 适用/不适用场景决策表、⚠️ 预览版风险提示、平台限制 | 15 |
| 15 | [15-ecosystem-resources.md](15-ecosystem-resources.md) | 官方资源、社区插件、推荐阅读、生态动态新闻 | 16 |
| 16 | [16-appendix-core-services.md](16-appendix-core-services.md) | 附录：核心服务速查表、ctx.* API 速查、事件模式速查 | — |

## 学习路径

### 快速上手路径（1-2 小时）

适合希望立即体验的用户：
1. 阅读 [01 项目介绍与背景](01-introduction-background.md)
2. 完成 [02 环境准备与安装](02-installation-setup.md)
3. 跟随 [03 快速上手](03-quickstart-first-task.md) 跑通第一个任务
4. 了解 [04 四种运行模式](04-four-modes.md)

### 使用者路径（1 天）

适合日常使用 dsh 完成开发任务的用户：
- 完成快速上手路径
- 深入理解 [05 核心架构](05-architecture-everything-plugin.md)
- 掌握 [07 会话日志与可观测性](07-session-log-observability.md) 调试技巧
- 熟悉 [08 模型配置](08-model-configuration.md) 与 [09 工具系统](09-tools-capability-seam.md)
- 阅读 [11 生态互操作](11-ecosystem-interop.md) 了解兼容能力
- 查阅 [13 FAQ](13-faq-troubleshooting.md) 与 [14 适用场景](14-use-cases-limitations.md) 规避风险

### 架构理解路径（2-3 天）

适合希望深入理解 dsh 设计的开发者：
- 完成使用者路径
- 深入 [06 Agent 循环与事件模型](06-agent-loop-events.md)
- 研究 [09 Capability Seam](09-tools-capability-seam.md) 可替换能力设计
- 学习 [10 插件开发入门](10-plugin-development.md)

### 高级开发者路径（1 周）

适合计划扩展 dsh 生态或嵌入自有系统的开发者：
- 完成架构理解路径
- 学习 [12 无头模式与 SDK](12-headless-sdk.md) 进行程序化集成
- 开发时随时查阅 [16 附录：核心服务速查表](16-appendix-core-services.md)
- 参考 [15 生态资源](15-ecosystem-resources.md) 跟踪社区进展
- 阅读官方源码与示例插件

## 核心概念速览

| 概念 | 定义 |
|------|------|
| **Cordis** | dsh 底层元框架，源自时空可组合性编程范式论文，核心五概念：Plugin（插件三种形态）、Context（服务容器）、Inject（依赖注入）、Events（五种分发模式：emit/bail/parallel/serial/waterfall）、Reversible Effects（可逆效应四种disposer），无特权内核 |
| **Context（上下文）** | Cordis 的服务容器，每个服务占据稳定的 `ctx.<key>`（如 `ctx.tools`、`ctx.llm`），通过 key 查找而非模块导入，是插件间通信的唯一通道 |
| **Plugin（插件）** | dsh 的基本扩展单元，有三种等价形态：带 `inject`/`apply` 的函数、Service 子类、普通对象；模型、工具、循环、UI 均为插件，可自由挂载卸载 |
| **Reversible Effect（可逆效应）** | 通过 `ctx.effect()` 或 `ctx.on()` 注册的副作用，卸载时自动按 LIFO 逆序执行 disposer（支持函数/Generator/Promise/AsyncGenerator 四种形式），保证无残留；热重载依赖此机制 |
| **Event Dispatch（事件分发）** | Cordis 类型化事件五种模式：`emit`（同步纯通知）、`bail`（同步早退，第一个非null结果获胜）、`parallel`（并行等待全部完成）、`serial`（顺序执行有返回）、`waterfall`（链式中间件，必须调用 `next()` 否则短路） |
| **Profile（配置档案）** | 存放在 `~/.dsh/profiles/` 下的命名组合清单，罗列叠加的 bundle 与用户自定义补丁，内置 web/headless/cordis 模板 |
| **Bundle（能力捆绑包）** | 打包一组 Cordis 配置与代码的分发格式，叠加顺序：dsh-base → profile bundles → profile patch → home patch → CLI --patch overlay，可被上层继续打补丁 |
| **Turn（回合）** | 从认领输入开始到无欠账结束的一次完整对话轮次，包含零到多个 Step |
| **Step（步骤）** | 一次模型请求加上其触发的工具调用，是 Agent 循环的最小执行单元 |
| **SessionLog（会话日志）** | 仅追加（append-only）的 SessionEvent 流，硬性不变量（invariant）：模型看到的一切必须可从日志重建，支持分叉、回放、检查点；由 invariants 包运行时断言强制执行 |
| **CapabilitySeam（能力接缝）** | 由 Service Definition（声明接口）、Service Provider（实现接口，可多实现切换）、Consumer（消费方）三角色组成的可替换能力抽象；基于依赖注入实现解耦，"一次替换，全局生效" |

## 版本说明

- **基于版本**：v0.1.0-rc.6（开发者预览版）
- **数据截止**：2026-08-15，源码交叉验证：2026-08-17（基于 `external/libs/deepseek-harness`、`external/libs/cordis` 本地源码）
- **协议**：MIT
- **重要提示**：当前为开发者预览版本，官方明确声明核心插件与基础接口会快速迭代，可能存在破坏兼容的变更，不建议直接用于生产环境。

---

→ [01 项目介绍与背景](01-introduction-background.md)
