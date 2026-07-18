---
id: "finding-skill-description-seo"
title: "发现2：Skill description是\"触发广告\"而非\"功能文档\""
source: "../insight-extraction.md#发现2skill-description-是触发广告而非功能文档"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/finding-02-skill-description-seo.toml"
---
# 发现2：Skill description是"触发广告"而非"功能文档"

→ 整合进：[skill-five-elements-model.md](../../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) 要素1（Trigger-Ready Description）

## 事件发现

初版 description 简洁但触发词不足，存在严重 undertrigger 风险。优化后的description增加了完整触发词、同义词，并显式声明"必须使用此技能"，解决了undertrigger问题。

## 根因分析

不了解 Claude skill 触发机制：模型倾向于"谨慎触发"（undertrigger），description 需要包含足够的触发关键词和强制性措辞才能可靠触发。传统API文档思维——只写"这个skill做什么"，不考虑"让模型想到要用这个skill"。

## 深层含义

Skill description 的首要目标是**让模型在合适场景下想到使用这个 skill**，其次才是告诉用户这个 skill 做什么。这类似于搜索引擎优化（SEO），需要考虑模型的"触发决策过程"。

## Description写作原则

description 应该包含：
1. 所有可能的触发关键词和同义词（如"发帖"、"发论坛"、"discourse操作"、"forum-bot"）
2. 明确说"必须使用此技能"等强制措辞
3. 简要说明核心能力和优势
4. 控制长度但不要过于简洁

模板结构：`{领域/平台}操作。当用户需要{触发词列表}时，必须使用此技能。支持{核心能力}，{核心优势}。覆盖{功能范围}。`

## 关联洞察

- [law-01-skill-five-elements-model.md](law-01-skill-five-elements-model.md) — Skill五要素模型
- [finding-03-why-explanation-principle.md](finding-03-why-explanation-principle.md) — Why解释原则

---
*来源：[forum-posting Skill优化复盘](../README.md)*
