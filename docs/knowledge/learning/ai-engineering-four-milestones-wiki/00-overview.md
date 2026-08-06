---
id: "ai-engineering-four-milestones-wiki-00-overview"
title: "概述与学习目标"
source: "https://mp.weixin.qq.com/s/eeB14yOtDU6akQUp0Mkauw"
x-toml-ref: "../../../../.meta/toml/docs/knowledge/learning/ai-engineering-four-milestones-wiki/00-overview.toml"
---

# 概述与学习目标

## 背景

AI 圈造新词的速度，已经超过学习速度。Prompt Engineering 刚整明白，Context Engineering 火了一年；2026 年开春 Harness Engineering 被推上风口；六月又冒出 Loop Engineering。三天一概念，五天一炸裂。

本 Wiki 基于 AllenTang 所著《AI 工程的四个路标（沿"瓶颈外移"主线）》一文，将四个看似独立的工程概念沿同一条主线串联起来，构建可迁移的认知框架。

## 核心主题

**四个概念不是四个互相换皮的赛道，而是同一条线上的四个路标。**

主线规律：每当模型变强一截，整个系统的瓶颈就被迫往外移一层——从你说的那句话，到你喂的那堆料，到它干活的环境，最后移到了你本人身上。

```
模型变强 → 原瓶颈突破 → 新瓶颈在外层暴露 → 工程重心外移
```

四站递进：

| 站点 | 工程 | 瓶颈位置 |
|---|---|---|
| 第一站 | Prompt Engineering | 怎么说 |
| 第二站 | Context Engineering | 给什么 |
| 第三站 | Harness Engineering | 干活的环境 |
| 第四站 | Loop Engineering | 你自己 |

## 学习目标

完成本 Wiki 后，你将能够：

1. 理解"瓶颈外移"作为 AI 工程演进主线规律的本质
2. 区分 Prompt、Context、Harness、Loop 四个工程阶段的核心问题与解决对象
3. 掌握"Agent = 模型 + Harness"公式及其工程含义
4. 应用"复利式环境建设"方法论到自身 AI 工程实践中
5. 识别"回合制→循环制"范式迁移对个人工作流的实际影响

## 前置知识

- 对大语言模型（LLM）的基本工作原理有概念性了解
- 使用过 ChatGPT/Claude 等对话式 AI 工具
- 了解"Agent"一词在 AI 语境下的大致含义
- 有过编写提示词的实践经历（非必需，但有助理解）

## 文档导航

| 章节 | 主题 | 链接 |
|---|---|---|
| 01 | 瓶颈外移主线 | [./01-bottleneck-migration.md](./01-bottleneck-migration.md) |
| 02 | Prompt Engineering | [./02-prompt-engineering.md](./02-prompt-engineering.md) |
| 03 | Context Engineering | [./03-context-engineering.md](./03-context-engineering.md) |
| 04 | Harness Engineering | [./04-harness-engineering.md](./04-harness-engineering.md) |
| 05 | Loop Engineering | [./05-loop-engineering.md](./05-loop-engineering.md) |
| 06 | 深度洞察与可复用方法论 | [./06-insights-patterns.md](./06-insights-patterns.md) |
| 07 | 总结、FAQ与资源 | [./07-summary-faq-resources.md](./07-summary-faq-resources.md) |

← 返回 [索引页](../ai-engineering-four-milestones-wiki.md)
