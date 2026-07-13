---
id: "seven-concepts-prompt-index"
title: "七概念驱动的GPT-5.6时代Prompt Engineering Wiki教程"
category: "learning"
date: "2026-07-13"
version: "1.0"
status: "in-progress"
---

# 七概念驱动的GPT-5.6时代Prompt Engineering Wiki教程

> **L2级Prompt工程方法论知识库，融合SpecWeave七概念方法论与OpenAI最新GPT-5.6 Prompting指南**。本Wiki针对"模型能力升级但Prompt写法未跟上"的行业痛点，将SpecWeave R-I-E-C-A-F-V七概念方法论系统映射到GPT-5.6时代的Prompt Engineering实践，覆盖范式变革→概念映射→GCOB框架→核心规则→Before/After对照→多场景实战→检查清单→反模式→术语表→FAQ→速查表的完整体系。所有内容以工程实践为导向，提供可直接复用的模板和检查清单。

<!-- README_INDEX_START -->
## 📄 文档索引

| 文档 | 说明 | 标签 |
|------|------|------|
| [README.md](README.md) | 本索引文件，文档导航入口 | 索引 |
| [00、概述与背景](00-overview.md) | 项目简介、资料概览、可信度评级说明、分层次阅读路径、文件导航 | 入门 |
| [01、GPT-5.6范式变革](01-paradigm-shift.md) | GPT-5.6能力跃迁、旧范式失效场景、新范式核心特征、迁移路线图 | 入门 |
| [02、七概念与Prompt Engineering映射](02-seven-concepts-mapping.md) | R-I-E-C-A-F-V七概念详解、每个概念在Prompt工程中的映射关系、协同效应 | 进阶 |
| [03、GCOB四要素框架详解](03-gcob-framework.md) | Goal(目标)/Context(上下文)/Obstacles(障碍)/Behavior(行为)四要素框架、要素拆解、组合策略 | 进阶 |
| [04、新范式核心规则](04-new-paradigm-rules.md) | 简洁优先、结构化表达、负向约束、迭代优化、元认知提示等核心规则详解 | 进阶 |
| [05、6组Before/After对照](05-before-after-examples.md) | 6组典型场景新旧写法对照、改写思路分析、效果对比、可复用模式提炼 | 入门-进阶 |
| [06、Chat场景实战指南](06-chat-scenarios.md) | 对话场景Prompt策略、多轮上下文管理、角色设定、澄清追问、知识问答模式 | 入门-进阶 |
| [07、Work场景实战指南](07-work-scenarios.md) | 工作场景（文档/邮件/报告/会议纪要等）Prompt模板、结构化输出、格式控制 | 进阶 |
| [08、Codex开发场景指南](08-codex-scenarios.md) | 代码生成/重构/调试/审查场景策略、TDD引导、上下文窗口管理、技术债务识别 | 进阶 |
| [09、检查清单与模板库](09-checklists-templates.md) | Prompt质量检查清单、各场景可直接复用模板、Prompt迭代记录模板、效果评估表 | 进阶 |
| [10、反模式识别与修正](10-anti-patterns.md) | 20+常见反模式（冗长指令/角色过载/模糊约束/过度嵌套等）识别、危害分析、修正方案 | 进阶 |
| [11、核心术语表](11-glossary.md) | Prompt Engineering相关术语定义、中英文对照、七概念/GCOB框架术语说明 | 参考 |
| [12、FAQ与资源索引](12-faq-resources.md) | 常见问题解答、官方文档链接、推荐学习资源、工具推荐、社区资源 | 参考 |
| [13、快速参考速查表](13-quick-reference.md) | GCOB框架速查、核心规则速查、反模式速查、场景模板速查、检查清单速查 | 速查 |

<!-- README_INDEX_END -->

## 🗺️ 分层次阅读路径

根据不同读者背景和目标，推荐以下阅读路径：

### 🌱 路径一：入门初学者
**适合人群**：刚开始使用AI、Prompt经验较少的读者
**阅读目标**：建立正确认知，快速上手有效Prompt写法

```
README.md（索引入口）
→ 00-overview.md（本文件，建立全局认知）
→ 01-paradigm-shift.md（理解为什么旧写法失效）
→ 05-before-after-examples.md（通过对照建立直观感受）
→ 06-chat-scenarios.md（最常用的对话场景）
→ 13-quick-reference.md（速查表，随时查阅）
→ 09-checklists-templates.md（直接复用模板）
```

### 👨‍💻 路径二：AI开发者
**适合人群**：日常使用AI辅助开发、需要提升代码生成质量的工程师
**阅读目标**：掌握Codex场景深度技巧，提升开发效率和代码质量

```
00-overview.md（本文件，概览）
→ 01-paradigm-shift.md 第2-3章（能力跃迁+新范式特征）
→ 02-seven-concepts-mapping.md（理解底层方法论）
→ 03-gcob-framework.md（掌握结构化框架）
→ 04-new-paradigm-rules.md（核心规则）
→ 08-codex-scenarios.md（重点研读开发场景）
→ 09-checklists-templates.md（代码场景模板）
→ 10-anti-patterns.md（避开常见陷阱）
→ 13-quick-reference.md（速查）
```

### 🧠 路径三：Prompt工程师/研究者
**适合人群**：专业Prompt工程师、AI产品经理、研究Prompt优化的从业者
**阅读目标**：系统掌握方法论，构建自己的Prompt工程体系，能够指导他人

```
README.md（索引入口）
→ 00-overview.md（本文件，了解Wiki定位）
→ 01-paradigm-shift.md（范式变革的深层逻辑）
→ 02-seven-concepts-mapping.md（七概念完整映射，方法论核心）
→ 03-gcob-framework.md（框架深度解析）
→ 04-new-paradigm-rules.md（规则背后的原理）
→ 05-before-after-examples.md（模式提炼）
→ 06/07/08-scenarios（全场景覆盖）
→ 09-checklists-templates.md（系统化工具）
→ 10-anti-patterns.md（防御性知识）
→ 12-faq-resources.md（拓展视野）
→ 11-glossary.md（统一术语）
→ 13-quick-reference.md（最终沉淀速查）
```

---

## 🔗 相关资源

- [🏠 返回上级：Agent工程方法论](../README.md)
- [📚 知识库首页](../../../README.md)
- [🧬 七概念方法论：七概念指令集](../../../../../.agents/commands/seven-concepts.md)
- [🔄 方法论模式库：Prompt工程模式](../../../../retrospective/patterns/README.md)
- [📖 对抗性审查Wiki：提升Prompt质量](../adversarial-review-wiki/README.md)

---

*本Wiki版本：v1.0 | 创建日期：2026-07-13 | 状态：🚧 建设中*
