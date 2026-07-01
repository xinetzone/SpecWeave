---
id: "finding-progressive-disclosure"
source: "../insight-extraction.md#发现4渐进式披露progressive-disclosure的上下文节省效应"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-forum-posting-skill-optimization-20260629/insights/finding-04-progressive-disclosure.toml"
---
# 发现4：渐进式披露（Progressive Disclosure）的上下文节省效应

→ 整合进：[skill-five-elements-model.md](../../../../../patterns/methodology-patterns/ai-collaboration/skill-five-elements-model.md) 要素3（Progressive Disclosure）

## 事件发现

skill-creator 建议控制在500行以内，但 SKILL.md 需要覆盖双方案、参数表、操作步骤、错误处理、选择器速查等大量内容。最终通过引用外部文档，将主文档控制在307行（<500行阈值）。

## 解决方案

将详细参数表、完整故障排查、@discourse/mcp 长期方案配置等**引用**到知识库文档，SKILL.md 只保留最常用的速查内容和决策逻辑：
- 常用内容（操作步骤、工具函数、检查清单）→ 内联在SKILL.md中
- 低频但必要的内容（完整参数、故障排查树）→ 引用外部文档按需加载

## 深层含义

这不是简单的"内容搬家"，而是**按使用频率分层**：
1. 核心决策逻辑和高频操作直接呈现，减少上下文跳转
2. 低频但必要的内容通过链接引用，不占用主文档上下文窗口
3. 主文档控制在500行以内，确保Agent能抓住重点，关键规则不被淹没

## 关联洞察

- [law-01-skill-five-elements-model.md](law-01-skill-five-elements-model.md) — Skill五要素模型
- [template-variance-control.md](../../../../../patterns/methodology-patterns/ai-collaboration/template-variance-control.md) — 模板降方差模式

---
*来源：[forum-posting Skill优化复盘](../README.md)*
