---
id: "seven-concepts-prompt-overview"
title: "00、概述与背景"
category: "knowledge"
date: "2026-07-13"
version: "1.0"
status: "completed"
---

# 七概念驱动的GPT-5.6 Prompt Engineering Wiki：概述与背景

---

## 1. 项目简介

本Wiki是SpecWeave七概念方法论（R-I-E-C-A-F-V）与OpenAI最新GPT-5.6 Prompting指南深度整合的系统化教程，旨在解决AI行业普遍存在的痛点：**模型能力快速迭代升级，但大多数人的Prompt写作方法仍停留在GPT-3.5/GPT-4时代**。

### 1.1 教程定位

本教程不是Prompt技巧的零散堆砌，而是一套**可复用、可验证、可迁移**的工程化方法论体系：
- **理论与实践结合**：既有七概念方法论的底层逻辑，又有可直接复制使用的实战模板
- **面向GPT-5.6时代**：针对新模型的长上下文、强推理、工具调用等能力优化写法
- **工程化导向**：提供检查清单、反模式识别、效果评估等工程化工具
- **分层适配**：为初学者、开发者、专业Prompt工程师分别设计阅读路径

### 1.2 核心特色

| 特色 | 说明 |
|------|------|
| **七概念方法论驱动** | 将SpecWeave R(复盘)-I(洞察)-E(萃取)-C(原子提交)-A(原子化)-F(第一性原理)-V(对抗性审查)七概念系统映射到Prompt工程 |
| **GCOB四要素框架** | OpenAI官方Goal-Context-Output-Boundaries四要素结构化框架，替代零散的"技巧清单" |
| **GPT-5.6新范式** | 摒弃"越详细越好"的旧思维，拥抱"简洁即正义"的新范式，适配新模型理解能力 |
| **Before/After对照** | 6组典型场景的新旧写法对照，直观展示范式迁移的效果 |
| **全场景覆盖** | Chat对话/Work办公/Codex开发三大核心场景完整指南 |
| **工程化工具** | 检查清单、模板库、反模式识别、速查表等可直接落地的工具 |

---

## 2. 资料概览

本Wiki共包含 **16个核心文件**（00-13共15篇文档 + README索引），覆盖从范式变革到工程实践的完整体系：

**建设进度说明**（截至2026-07-13）：

| 模块 | 文件数 | 状态 | 说明 |
|------|--------|------|------|
| 索引与概述 | 2个（README+00） | ✅ 完成 | 导航入口与全局介绍 |
| 理论基础 | 4个（01-04） | 🚧 待编写 | 范式变革、七概念映射、GCOB框架、核心规则 |
| 实战指南 | 5个（05-08b） | 🚧 待编写 | Before/After对照、三大场景实战（含8个Codex场景模板） |
| 工具资源 | 5个（09-13） | 🚧 待编写 | 检查清单、反模式、术语表、FAQ、速查表 |

**覆盖范围**：GPT-5.6范式变革→七概念方法论映射→GCOB四要素框架→新范式核心规则→Before/After实战对照→三大场景（Chat/Work/Codex）指南→检查清单模板库→反模式识别修正→术语表→FAQ资源→速查表，形成完整的"理论→框架→实践→工具"闭环。

---

## 3. 可信度评级说明

本Wiki参考对抗性审查Wiki的四级可信度评级体系，并配合异常标记如实标注资料的不确定性。

### 3.1 可信度评级

| 标记 | 等级 | 判定标准 | 使用建议 |
|------|------|---------|---------|
| 🟢 | **A级** | OpenAI官方文档明确说明；SpecWeave七概念方法论已在多个项目验证；多来源交叉验证一致 | 核心原则，可直接作为工程标准采用 |
| 🔵 | **B级** | 基于官方指南的合理推导；社区共识度高的最佳实践；经过实战验证但尚未大规模推广 | 推荐采用，鼓励在自身场景中验证效果 |
| 🟡 | **C级** | 经验性总结；特定场景有效但普适性待验证；存在不同观点 | 建议尝试，需根据具体场景调整 |
| 🔴 | **D级** | 已被新模型/新范式证伪；存在明显反例；来源不可追溯 | 仅作为反模式记录，不推荐使用 |

### 3.2 异常标记

| 标记 | 类型 | 含义 |
|------|------|------|
| ⚠️ | 模型版本相关 | 该条规则/技巧可能随模型版本更新而变化，需关注最新动态 |
| ❓ | 场景依赖 | 该条仅适用于特定场景，泛化使用可能失效 |
| ⚖️ | 风格选择 | 存在多种合理写法，无绝对对错，属于风格偏好范畴 |
| 🔍 | 待验证 | 该条基于有限观察，需要更多实战案例验证 |

---

## 4. 分层次阅读路径

根据不同读者背景和目的，推荐以下阅读路径：

### 🌱 路径一：入门初学者
**适合人群**：刚开始使用AI、Prompt经验较少、希望快速上手的读者
**阅读目标**：建立正确认知，避开常见陷阱，写出明显更有效的Prompt
**预计耗时**：2-3小时核心内容 + 1周实践

```
README.md（索引入口，了解整体结构）
→ 00-overview.md（本文件，建立全局认知，理解为什么需要新方法）
→ 01-paradigm-shift.md（理解GPT-5.6带来的范式变革，知道旧写法为什么失效）
→ 05-before-after-examples.md（通过6组对照建立直观感受，先模仿再理解）
→ 06-chat-scenarios.md（最常用的对话场景，立即能用）
→ 09-checklists-templates.md 快速上手部分（直接复制模板开始用）
→ 13-quick-reference.md（打印速查表放在手边）
→ 实践中遇到问题再回来读 04-new-paradigm-rules.md 和 10-anti-patterns.md
```

### 👨‍💻 路径二：AI开发者
**适合人群**：日常使用AI辅助编码、需要提升代码生成质量和开发效率的工程师
**阅读目标**：掌握Codex场景深度技巧，建立结构化Prompt思维，显著提升开发效率
**预计耗时**：4-6小时核心内容 + 2周刻意练习

```
00-overview.md（本文件，快速概览定位）
→ 01-paradigm-shift.md 第2-3章（重点理解新模型能力跃迁带来的写法变化）
→ 02-seven-concepts-mapping.md（理解七概念底层方法论，建立系统思维）
→ 03-gcob-framework.md（掌握GCOB四要素框架，这是结构化Prompt的核心）
→ 04-new-paradigm-rules.md（理解新范式核心规则，知其然知其所以然）
→ 05-before-after-examples.md（重点看开发相关的Before/After对照）
→ 08-codex-scenarios.md（重点研读：安全原则、标准结构、完整模板）
→ 08b-codex-examples.md（8个实战场景模板，直接复制使用）
→ 09-checklists-templates.md（代码场景专属模板，直接复用）
→ 10-anti-patterns.md（重点看开发场景常见反模式，避免踩坑）
→ 07-work-scenarios.md（文档/技术方案等工作场景也值得一看）
→ 13-quick-reference.md（开发时速查）
```

### 🧠 路径三：Prompt工程师/研究者
**适合人群**：专业Prompt工程师、AI产品经理、需要设计Prompt系统、研究Prompt优化的从业者
**阅读目标**：系统掌握完整方法论，能独立设计高质量Prompt体系，能指导团队使用
**预计耗时**：8-12小时完整研读 + 1个月项目实践沉淀

```
README.md（索引入口，了解完整知识体系）
→ 00-overview.md（本文件，理解Wiki的设计思路和定位）
→ 01-paradigm-shift.md（完整理解范式变革的技术背景和深层逻辑）
→ 02-seven-concepts-mapping.md（核心章节：七概念与Prompt工程的完整映射，方法论基石）
→ 03-gcob-framework.md（框架深度解析，理解每个要素的设计原理和组合策略）
→ 04-new-paradigm-rules.md（核心规则逐条理解，包括规则背后的认知科学原理）
→ 05-before-after-examples.md（不仅看例子，更要提炼可迁移的改写模式）
→ 06-chat-scenarios.md（对话场景完整覆盖）
→ 07-work-scenarios.md（办公场景完整覆盖）
→ 08-codex-scenarios.md（开发场景基础：安全原则与结构）
→ 08b-codex-examples.md（开发场景实战：8个模板）
→ 09-checklists-templates.md（系统化工具：检查清单、模板库、评估方法）
→ 10-anti-patterns.md（防御性知识：20+反模式的识别、危害、修正）
→ 12-faq-resources.md（拓展视野，了解社区前沿和官方资源）
→ 11-glossary.md（统一术语体系，便于团队沟通）
→ 13-quick-reference.md（最终沉淀为自己的速查手册）
→ 实践后结合对抗性审查Wiki，建立自己的Prompt质量保障体系
```

---

## 5. 文件导航表

| 序号 | 文件名 | 标题 | 内容简介 | 难度等级 | 建议阅读顺序 |
|------|--------|------|---------|---------|-------------|
| - | [README.md](README.md) | 文档索引 | 本Wiki索引入口，包含主题概述、15个文件索引表、3条分层次阅读路径、相关资源链接。 | 入门 | 0（入口） |
| 00 | [00-overview.md](00-overview.md) | 概述与背景 | 项目简介、核心特色、资料概览、可信度评级说明、3条详细阅读路径、文件导航表、快速链接。 | 入门 | 1（先读） |
| 01 | [01-paradigm-shift.md](01-paradigm-shift.md) | GPT-5.6范式变革 | GPT-5.6核心能力跃迁（长上下文/强推理/工具调用/指令遵循）、旧范式3大失效场景、新范式5大核心特征、从旧到新迁移路线图、常见误区。 | 入门 | 2 |
| 02 | [02-seven-concepts-mapping.md](02-seven-concepts-mapping.md) | 七概念与Prompt Engineering映射 | R(复盘)/I(洞察)/E(萃取)/C(原子提交)/A(原子化)/F(第一性原理)/V(对抗性审查)七概念逐个详解、每个概念在Prompt工程中的具体映射、七概念协同效应、实战案例。 | 进阶 | 3 |
| 03 | [03-gcob-framework.md](03-gcob-framework.md) | GCOB四要素框架详解 | Goal(目标)/Context(上下文)/Output(输出)/Boundaries(边界)四要素框架、每个要素的拆解方法、要素组合策略、不同场景权重调整、GCOB与七概念的对应关系。 | 进阶 | 4 |
| 04 | [04-new-paradigm-rules.md](04-new-paradigm-rules.md) | 新范式核心规则 | 简洁优先规则、结构化表达规则、负向约束规则、示例驱动规则、迭代优化规则、元认知提示规则、工具调用规则等10条核心规则详解，每条包含原理说明+正反示例。 | 进阶 | 5 |
| 05 | [05-before-after-examples.md](05-before-after-examples.md) | 6组Before/After对照 | 内容分析、代码生成、翻译、研究分析、Agent工具调用、日常任务6组典型场景新旧写法对照、改写思路逐步分析、效果对比、可复用模式提炼。 | 入门-进阶 | 6 |
| 06 | [06-chat-scenarios.md](06-chat-scenarios.md) | Chat场景实战指南 | 日常对话、知识问答、头脑风暴、学习辅导、多轮上下文管理、角色设定、澄清追问、话题引导等对话场景Prompt策略、模板、注意事项。 | 入门-进阶 | 7 |
| 07 | [07-work-scenarios.md](07-work-scenarios.md) | Work场景实战指南 | 邮件写作、文档撰写、报告生成、会议纪要、PPT大纲、数据总结、方案设计、翻译校对等办公场景Prompt模板、结构化输出控制、格式规范要求。 | 进阶 | 8 |
| 08 | [08-codex-scenarios.md](08-codex-scenarios.md) | Codex开发场景基础 | Codex/Agent安全四原则、Prompt六要素结构、完整安全模板、常见事故预防、Steer/Queue交互指南。 | 进阶 | 9 |
| 08b | [08b-codex-examples.md](08b-codex-examples.md) | Codex开发场景实战模板 | 8个最高频Codex场景（新页面/修Bug/重构/写测试/加API/写文档/依赖升级/改配置）完整可复制Prompt模板，每个含安全注意事项。 | 进阶 | 9.5 |
| 09 | [09-checklists-templates.md](09-checklists-templates.md) | 检查清单与模板库 | Prompt质量10项检查清单、三大场景可直接复用Prompt模板库、Prompt迭代记录模板、效果评估表格、最小可行Prompt设计指南。 | 进阶 | 10 |
| 10 | [10-anti-patterns.md](10-anti-patterns.md) | 反模式识别与修正 | 冗长指令、角色过载、模糊约束、过度嵌套、指令矛盾、缺乏示例、忽略边界、单一Prompt通吃、不验证输出、不迭代优化等20+常见反模式的识别特征、危害分析、修正方案、正反示例。 | 进阶 | 11 |
| 11 | [11-glossary.md](11-glossary.md) | 核心术语表 | Prompt Engineering、七概念方法论、GCOB框架相关术语定义、中英文对照、相关概念辨析、索引。 | 参考 | 随时查阅 |
| 12 | [12-faq-resources.md](12-faq-resources.md) | FAQ与资源索引 | 常见问题解答（为什么我的Prompt效果不稳定？长Prompt真的更好吗？等等）、OpenAI官方文档链接、推荐学习资源、Prompt工具推荐、社区资源、延伸阅读。 | 参考 | 进阶后阅读 |
| 13 | [13-quick-reference.md](13-quick-reference.md) | 快速参考速查表 | GCOB四要素速查、10条核心规则速查、20+反模式速查、三大场景模板要点速查、10项检查清单速查、关键数字速查。 | 入门 | 随时查阅 |

---

## 6. 快速链接表

| 用途 | 链接 | 状态 |
|------|------|------|
| 🔄 范式变革理解 | [01-paradigm-shift.md](01-paradigm-shift.md) | 🚧 待编写 |
| 🧬 七概念映射（核心） | [02-seven-concepts-mapping.md](02-seven-concepts-mapping.md) | 🚧 待编写 |
| 🏗️ GCOB框架详解 | [03-gcob-framework.md](03-gcob-framework.md) | 🚧 待编写 |
| 📜 新范式核心规则 | [04-new-paradigm-rules.md](04-new-paradigm-rules.md) | 🚧 待编写 |
| ⚖️ Before/After对照 | [05-before-after-examples.md](05-before-after-examples.md) | 🚧 待编写 |
| 💬 Chat场景指南 | [06-chat-scenarios.md](06-chat-scenarios.md) | 🚧 待编写 |
| 💼 Work场景指南 | [07-work-scenarios.md](07-work-scenarios.md) | 🚧 待编写 |
| 💻 Codex开发场景 | [08-codex-scenarios.md](08-codex-scenarios.md) | 🚧 待编写 |
| 📋 Codex实战模板 | [08b-codex-examples.md](08b-codex-examples.md) | ✅ 完成 |
| ✅ 检查清单模板 | [09-checklists-templates.md](09-checklists-templates.md) | 🚧 待编写 |
| ⚠️ 反模式识别 | [10-anti-patterns.md](10-anti-patterns.md) | 🚧 待编写 |
| 🔤 术语表 | [11-glossary.md](11-glossary.md) | 🚧 待编写 |
| ⚡ 速查表 | [13-quick-reference.md](13-quick-reference.md) | 🚧 待编写 |

---

## 7. 相关项目文档

本Wiki是Agent工程方法论体系的组成部分，相关参考文档：

- 七概念方法论原始指令集：[seven-concepts.md](../../../../../.agents/commands/seven-concepts.md)
- 对抗性审查Wiki（提升Prompt质量保障能力）：[adversarial-review-wiki/README.md](../adversarial-review-wiki/README.md)
- Agent工程方法论目录：[02-agent-engineering-methodology/README.md](../README.md)
- SpecWeave知识库首页：[docs/README.md](../../../README.md)
- 方法论模式库（可复用Prompt模式）：[retrospective/patterns/README.md](../../../../retrospective/patterns/README.md)

---

*本文件版本：v1.0 | 创建日期：2026-07-13 | 状态：🚧 建设中*
