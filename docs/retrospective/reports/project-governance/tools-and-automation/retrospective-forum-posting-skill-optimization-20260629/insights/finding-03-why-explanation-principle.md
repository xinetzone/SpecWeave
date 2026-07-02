---
id: "finding-why-explanation-principle"
title: "发现3：Skill文档的\"解释Why\"原则"
source: "../insight-extraction.md#发现3skill-文档的解释why原则"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/finding-03-why-explanation-principle.toml"
---
# 发现3：Skill文档的"解释Why"原则

→ 整合进：[skill-five-elements-model.md](../../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) 要素4（Why-Explanation）

## 事件发现

初版 SKILL.md 主要是操作步骤列表（MUST 规则），缺乏设计决策的解释。例如只写了"不能用 :has-text()"，但没解释为什么，导致Agent在遇到类似选择器时可能犯同样错误。

## 根因分析

传统 API 文档思维——只告诉你"怎么做"，不告诉你"为什么这么做"。但Skill文档的读者是 AI 模型，模型在面对边界情况时需要理解规则背后的**意图**才能做出正确判断。

## 深层含义

- 如果只知道"不能用 :has-text()"而不知道"为什么"（因为它不是标准DOM API，browser_evaluate 中不可用），模型在遇到类似非标准选择器时可能犯同样错误
- 纯规则列表无法覆盖所有边界情况，理解了Why才能举一反三

## 实施方式

在关键规则后加 `> **为什么？**` 引用块，解释设计决策的原因：
- 为什么需要双方案？（不同运行环境需求不同）
- 为什么要多信号检测？（单一选择器不稳定）
- 为什么dry-run是最重要防线？（写操作不可逆）
- 为什么要先做资产盘点？（避免重复造轮子、错过成熟方法论）

## 关联洞察

- [law-01-skill-five-elements-model.md](law-01-skill-five-elements-model.md) — Skill五要素模型
- [finding-02-skill-description-seo.md](finding-02-skill-description-seo.md) — Description SEO原则

---
*来源：[forum-posting Skill优化复盘](../README.md)*
