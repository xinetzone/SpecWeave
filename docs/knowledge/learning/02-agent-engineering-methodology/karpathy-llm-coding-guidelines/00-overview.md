---
id: "karpathy-llm-coding-guidelines-overview"
title: "Karpathy LLM 编程准则：概述与背景"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, claude, ai-programming, agentic-engineering]
date: "2026-07-02"
status: stable
author: "新智元 & multica-ai"
summary: "源自Andrej Karpathy对LLM编程陷阱观察的四条行为准则，用一个CLAUDE.md文件管住AI编程最常犯的毛病。本教程包含背景介绍、核心原则详解、真实代码正反例、安装使用指南，以及在SpecWeave项目中的整合情况。"
source: "https://www.36kr.com/p/3774954488349441 + https://github.com/multica-ai/andrej-karpathy-skills"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/00-overview.toml"
---
# Karpathy LLM 编程准则：概述与背景

## 背景

2026年4月，一个毫无代码的 Markdown 配置文件 `CLAUDE.md` 冲爆了整个 GitHub：

- 本周新增 **44,465 颗星**，总星数 **61.6k**
- 连续三天 Trending 日榜第一
- 全网 6 万码农连夜抄作业

它就是 **andrej-karpathy-skills** 项目——源自 Andrej Karpathy 对 LLM 编程陷阱的观察，由华人开发者 Jiayuan Zhang（Multica 创始人兼 CEO）提炼为四条简洁的行为准则。

## 故事起点

故事始于 2026 年 1 月 26 日，Karpathy 在 X 上发了一条长帖，详细吐槽了 AI 编程 Agent 的各种毛病。

当天，Jiayuan Zhang 就动手了：
1. 先用 Claude Code 把这条帖子自动转化成 skills 文件，生成约 800 行描述
2. 然后让 Claude 自己审查自己
3. 最后砍成了一段约 70 行的干净指令

产物就是 `CLAUDE.md`——相当于在 Agent 脑子里装的一套行为准则。

## 核心问题：AI 编程的三大通病

Karpathy 观察到 LLM 编程时存在三个核心问题：

> "模型会代你做错误假设，然后不假思索地执行。它们不管理自身的困惑，不寻求澄清，不呈现矛盾，不展示权衡，在应该提出异议时也不反驳。"

> "它们真的很喜欢把代码和 API 搞复杂，堆砌抽象概念，不清理死代码……明明 100 行能搞定的事情，非要实现成 1000 行的臃肿架构。"

> "它们有时仍会改动或删除自己理解不足的代码和注释，即使这些内容与任务本身无关。"

开发者们的真实反馈：
- **Kraggich**："一个 Markdown 文件冲上趋势榜第一，说明现在的瓶颈不在模型，而在模型周围的脚手架。这些'胶水'才是产品本身。"
- **Surajdotdot7**："模型选错了分支，运行了 40 分钟，最后碰壁失败。而提前澄清只需要 30 秒。"

## 解决方案：四条原则

这四条原则精准对应了开发者用 AI 写代码时最常踩的坑：

| 原则 | 口诀 | 解决什么问题 |
|------|------|-------------|
| **编码前先思考** | 不确定的先问别瞎猜 | 错误假设、隐藏困惑、缺少权衡 |
| **简约至上** | 代码能简短就别写长 | 过度复杂、臃肿抽象、过度设计 |
| **精确编辑** | 没让你改的地方别碰 | 无关编辑、顺手重构、触碰不应改的代码 |
| **目标驱动** | 给目标别给步骤 | 缺乏验证、需要不断介入澄清 |

把它丢进项目根目录，AI 编程 Agent 就会自动读取并遵守里面的规则。

## 更大的图景：Agentic Engineering

在 Karpathy 看来，LLM 编程带来的不只是加速，更是一种扩展——你能做到以前不值得做的事，能碰以前碰不了的代码。

这个概念升级为 **agentic engineering**（智能体工程）：一种把 AI 当做需要明确目标、清晰边界和严格测试的协作伙伴来对待的工程学科。

Karpathy 自己的工作流转变：
- 短短几周内，从「**80% 手写 + 20% AI 辅助**」彻底翻转成了「**80% 交给 Agent + 20% 自己修补**」
- 看着 Agent 死磕一个问题整整 30 分钟，要是人类早放弃了，而它就是不停地试，最后居然过了

但他也预言了一个词——**Slopacolypse**（低质量内容灾难）：
> 2026 年 GitHub、arXiv、社交媒体上会涌出大量 AI 生成的低质量内容。生产力是真的，质量垮塌的风险也是真的。

## 为什么这个项目这么火？

它之所以炸了，核心在于它把一个顶级工程师的隐性知识，打包成了 Agent 可以直接读取的格式。

> 说到底，Karpathy 不再只是一个你读的人，而是一个你的 Agent 可以直接继承行为的人。

## 关于作者

**Jiayuan Zhang** - 开源项目 Multica 的创始人兼 CEO。

Multica 是一个把 Claude Code、OpenCode、Codex CLI 这些 AI 编程 Agent 统一管理起来的开源平台，像真正的团队成员一样分配任务、汇报进展、交付代码。就连不会用命令行的人，也能通过它用上 Claude Code 级别的编程 Agent 能力。

> Your next 10 hires won't be human.
> 你接下来招的10名员工，都不会是人类了。

他们公司的代码 100% 由 AI 编写，每天消耗的 token 量超过 1 亿。

## 文档导航

| 章节 | 内容 |
|------|------|
| [01 - 四条核心原则详解](01-four-principles.md) | 每条原则的详细说明、具体要求、检验标准 |
| [02 - 真实代码正反例](02-code-examples.md) | Python 代码示例，展示 ❌ 错误做法 vs ✅ 正确做法 |
| [03 - 快速上手指南](03-quickstart.md) | Claude Code 插件安装、CLAUDE.md 配置、Cursor 使用方法 |
| [04 - SpecWeave 项目整合](04-specweave-integration.md) | 本项目如何整合这些准则，以及对应的规范文件位置 |
| [05 - 资源与参考](05-resources.md) | 官方仓库、原帖链接、相关资源 |
