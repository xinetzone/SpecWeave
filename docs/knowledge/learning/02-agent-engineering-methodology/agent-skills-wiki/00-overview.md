---
id: "agent-skills-overview"
title: "Agent Skills 项目概述与背景"
category: learning
tags: [ai-agent, engineering-workflow, google-engineering, agent-skills, best-practices]
date: "2026-07-08"
status: stable
version: "1.0"
source: "https://cloud.tencent.com/developer/article/2658842"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/agent-skills-wiki/00-overview.toml"
summary: "谷歌Gemini团队主管Addy Osmani开源的AI编程代理人生产级工程技能库，GitHub星标1.9万+，围绕6阶段生命周期定义20个核心技能，配套7个斜杠命令，深度融入Google工程文化。"
---
# Agent Skills 项目概述与背景

## 项目介绍

Agent Skills是谷歌Gemini团队主管Addy Osmani开源的AI编程代理人生产级工程技能库，GitHub星标1.9万+。

项目核心理念是将资深工程师的工作流质量门禁和最佳实践封装为结构化技能，强制AI在开发各阶段遵循高标准，而非选择跳过需求测试评审的最短路径。

## 核心设计

围绕软件开发生命周期六个核心阶段（Define/Plan/Build/Verify/Review/Ship）定义规划构建验证评审发布设计，共提供20个核心技能，配套7个斜杠触发命令，深度融入Hyrum定律、测试金字塔、Chesterton栅栏、左移等Google工程文化，支持Claude Code、Cursor、Gemini CLI等多种工具。

## 文档导航

| 章节 | 内容 |
|------|------|
| [01 - 六阶段生命周期模型](01-lifecycle-model.md) | Define/Plan/Build/Verify/Review/Ship各阶段设计逻辑与顺序必然性 |
| [02 - 20个核心技能索引](02-skills-index.md) | 按阶段分组的全部技能详解、设计意图与AI天然缺陷对应 |
| [03 - 7个触发命令机制](03-slash-commands.md) | 斜杠命令设计机制、核心理念口诀与阶段转换信号 |
| [04 - Google工程文化术语](04-google-engineering-culture.md) | Hyrum定律、Beyonce规则、Chesterton栅栏等8个核心术语详解 |
| [05 - 与SpecWeave对比分析](05-specweave-comparison.md) | 理念异同分析、可借鉴设计模式、潜在不足与改进方向 |
| [06 - 潜在应用场景](06-application-scenarios.md) | 遗留系统重构、新功能开发、紧急Bug修复等5个实战场景 |
| [07 - 延伸学习资源](07-resources.md) | Google工程实践文档、Addy Osmani著作、相关书籍与项目 |
