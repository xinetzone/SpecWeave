---
id: deepseek-harness-wiki-01
title: DeepSeek Harness Wiki - 项目介绍与背景
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
category: learning
maturity: L1
---

# 01 项目介绍与背景

## 核心公式：Agent = Model + Harness

DeepSeek Harness 的核心理念可以用一个简单公式概括：

> **Agent = Model + Harness**

模型是 Agent 的灵魂，负责理解、推理和生成内容；但模型本身只能输出文字，无法独立打开文件、执行命令、记住跨轮对话的上下文。Harness 是包裹在模型外部的那一层执行框架，让模型能够真正「读懂环境、使用工具、把任务跑完」。

官方对 Harness 的定位：

> 模型是 Agent 的灵魂；harness 让它读懂环境、使用工具、把任务真正跑完。

## Harness 的定义

具体而言，Harness 为模型提供以下核心能力：

| 能力组件 | 作用 |
|----------|------|
| **工作区（Workspace）** | 管理文件系统访问、目录权限、项目上下文 |
| **工具（Tools）** | 提供 Shell 执行、文件编辑、网络搜索、代码分析等可调用能力 |
| **权限（Permissions）** | 审批敏感操作，控制模型可执行的动作范围 |
| **会话记忆（Session Memory）** | 维护对话历史、上下文窗口管理、状态持久化 |
| **循环（Loop）** | 驱动 ReAct/Plan-and-Execute 等推理-行动循环，决定任务何时终止 |

## 发布时间线与增长数据

DeepSeek Harness 于 **2026 年 8 月 13 日晚** 正式发布，关键时间节点：

| 时间 | 事件 |
|------|------|
| 2026-08-13 20:30 左右 | GitHub 仓库悄悄公开 |
| 2026-08-13 21:05 | Star 数 7,283 |
| 2026-08-13 21:51 | Star 数 15,530（公布不到两小时破万） |
| 2026-08-14 08:53 | Star 数 44,514 |
| 发布后 12 小时 | Star 突破 5 万 |
| 发布后两天 | Star 超过 10 万 |

这一增长速度创下了开源项目的新纪录——对比此前增长最快的 OpenClaw（84 天 20 万 star，平均每小时约 99 个），DSH 头两小时的涨速是其 80 倍。

同期发布的还有 DeepSeek-V4-Pro 正式版，该模型在生产环境中的 Agent 性能显著提升，其公开基准测试中的 Code Agent 任务正是使用 DeepSeek Harness 极简模式作为框架完成的。

## Harness 的重要性

为什么模型公司要亲自下场做 Harness？开发者工具公司 Composio 的对照测试给出了答案：

> 同一个 DeepSeek-V4-Flash 模型，接入八种不同的 Harness，完成三十项任务。最好的完成了二十项，最差的只有十四项。**模型一模一样，结果差出 30%。**

这一数据揭示了一个关键事实：**模型划定能力上限，Harness 决定这份能力最终能兑现多少。**

对模型厂商而言，Harness 还有三重战略价值：

1. **成本控制**：上下文组织方式、缓存命中率决定一个任务消耗多少 token、需要几次重试，这些都发生在 Harness 层
2. **数据反馈**：任务失败的完整轨迹记录是改进模型最好的训练养料，而这些数据掌握在 Harness 手中
3. **生态壁垒**：插件生态的密度、社区参与度构成真正的护城河，而非单一模型绑定

## 与竞品对比

DeepSeek Harness 并非市场上唯一的 Agent Harness，与 Claude Code、Codex 的关键差异如下：

| 维度 | Claude Code / Codex | DeepSeek Harness |
|------|---------------------|------------------|
| **产品形态** | 成品 Agent，面向终端用户 | 造 Agent 的框架，附带开箱即用界面 |
| **交互界面** | 以终端 UI 为主 | 以本地 Web UI 为主，同时支持无头模式 |
| **扩展机制** | Hooks / MCP | Cordis 插件体系，**连 Agent 循环本身都可替换** |
| **模型支持** | 自家模型为主 | 多厂商模型，DeepSeek 优先；内置 Anthropic、OpenAI、Bedrock、Azure、Vertex 等适配器 |
| **源码授权** | 闭源或半开源 | **MIT 协议完全开源** |
| **成熟度** | 生产可用 | 开发者预览版（v0.1），官方警告会有破坏兼容的变更 |

在兼容性方面，dsh 内置了 Claude Code 和 Codex 的 Hooks 桥接层，可以直接复用现成的 `hooks.json` 配置；也支持将任务委托给本机已安装的 Claude Code/Codex（默认关闭）。此外，dsh 会读取 `AGENTS.md` 和 `CLAUDE.md` 作为项目上下文，并作为客户端支持 MCP（Model Context Protocol）。

## 「Agent 界 Android」战略解读

DeepSeek Harness 选择了一条与竞品完全不同的道路：别人把 Agent 做成成品卖给你，它把 Agent 的零件全部摊开，赌开发者会用这些零件拼出官方自己都没想到的东西。

这一战略被业内解读为「Agent 界的 Android」—— Android 刚问世时同样是一副毛坯模样，粗糙、开放、只吸引动手能力强的开发者；但正是这种彻底的开放性，最终催生了庞大的移动应用生态。

「一切皆插件」的设计哲学是这一战略的技术基石：没有特权内核，没有焊死在主干里的「官方逻辑」，所有能力地位平等——模型适配器、工具注册表、会话日志、甚至驱动整个 Agent 运转的主循环本身，都是可替换的插件。开源当天就出现了约三百个社区插件，从 Windows XP 复古皮肤到表情包生成器，充分验证了这一开放架构的生态潜力。

正如文渊智库创始人王超所言：

> 开源 Agent 真正的护城河，不是单一模型的绑定，而是生态的密度、社区参与的丰富程度，以及企业服务能力。DeepSeek 这步棋走得非常漂亮：用开源把水泼出去，换回的却是中国企业在 Agent 时代规则制定的权利。

## 开源协议与发布背景

DeepSeek Harness 采用 **MIT 协议** 完全开源，这是最为宽松的开源协议之一，允许商业使用、修改、分发、私有使用，仅要求保留版权和许可声明。

值得注意的是，此次发布有两个重要的商业背景：

1. **V4 Pro 同期发布**：与 Harness 一同上线的 DeepSeek-V4-Pro 正式版，其 Agent 能力在生产环境性能显著提升，原生支持 OpenAI Responses API 格式并针对性适配 Codex，思考模式支持 low/high/max 三档强度可调。

2. **API 价格调整**：新模型上线同时，DeepSeek 宣布自 2026 年 8 月 17 日 0 时起调整 API 定价，采用峰谷定价机制：
   - 空闲时段价格为高峰时段的一半
   - 高峰时段：北京时间工作日 9:00-12:00、14:00-18:00
   - DeepSeek-V4-Pro 高峰时段输出价格调整后较此前上涨约 350%，但整体定价仍处于大模型市场低位

业界分析认为，这「一放一收」（开源 Harness + 调整 API 定价）标志着 DeepSeek 正从早期靠性价比出圈的策略，走向行业发展的「深水区」——告别补贴策略，转向可持续的商业造血模式，同时通过开源 Harness 抢占 Agent 运行底座的控制权。

---

← [00 总览](00-overview.md) | → [02 环境准备与安装](02-installation-setup.md)
