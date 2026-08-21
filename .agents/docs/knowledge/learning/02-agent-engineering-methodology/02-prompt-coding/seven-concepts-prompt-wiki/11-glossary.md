---
id: "seven-concepts-glossary"
title: "11、术语表"
category: "reference"
date: "2026-07-13"
version: "1.0"
status: "completed"
source: "SpecWeave七概念方法论 + OpenAI官方术语"
---

# 术语表

---

## 1. 章节引言

本章按字母顺序整理本Wiki中出现的所有关键术语，提供中英文对照、简洁定义和相关章节跳转链接，方便查阅和快速理解。

> 🟢 **来源标注**：术语定义结合SpecWeave七概念方法论和OpenAI官方Prompt Engineering指南整理。

---

## 2. 术语列表（按英文字母排序）

---

### A

**Agent / 智能体**：能够自主理解目标、规划步骤、调用工具、执行任务的AI系统，而非单纯的问答模型。Codex等AI编程助手属于典型Agent场景。相关章节→[08-codex-scenarios.md](08-codex-scenarios.md)

**Atomic Commit / 原子提交（七概念C）**：七概念方法论中的"C"，指每次代码/内容变更只做一件事，提交信息清晰描述单一变更，便于回滚和Review。对应Prompt写作中的分步迭代、Steer/Queue交互模式。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

**Atomization / 原子化（七概念A）**：七概念方法论中的"A"，指将大任务拆分成独立、单一职责的小任务/文件/模块，对应Prompt中Output结构的清晰拆分。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

**对抗性审查 V（Adversarial Review）**：七概念方法论中的"V"，指从反面视角审视输出——找漏洞、找边界情况、找潜在风险，对应Prompt中的Boundaries边界约束和Checkpoint停止条件设置。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

---

### B

**Before/After 对照**：本Wiki第05章提供的新旧写法对比示例，通过反例→正例→差异分析的方式，直观展示什么写法有效什么写法无效。相关章节→[05-before-after-examples.md](05-before-after-examples.md)

**Boundaries / 边界约束（GCOB-B）**：GCOB框架四要素之一，明确告诉模型"不能做什么"——哪些操作禁止、哪些话不能说、哪些文件不能改。在Codex场景中边界是安全第一原则。相关章节→[03-gcob-framework.md](03-gcob-framework.md)

---

### C

**Chain of Thought (CoT) / 思维链**：让模型一步步思考以提高复杂推理准确率的技术。新范式认为模型会自主选择何时需要推理，简单任务无需刻意加"Let's think step by step"。相关章节→[10-anti-patterns.md](10-anti-patterns.md)

**Checkpoint / 停止检查点**：明确告诉模型遇到什么情况应该停下来询问用户，而不是自己猜测或继续执行。在复杂任务和Agent场景中必须设置，防止跑偏和死循环。相关章节→[04-new-paradigm-rules.md](04-new-paradigm-rules.md)

**Context / 上下文（GCOB-C）**：GCOB框架四要素之一，提供完成任务所必需的背景信息——你是谁、在做什么、有哪些已知数据、什么信息是模型不可能知道的。相关章节→[03-gcob-framework.md](03-gcob-framework.md)

**Context Window / 上下文窗口**：模型一次能处理的最大Token数量，对话太长早期内容会被截断。多轮对话中要注意关键信息补充，避免模型"失忆"。相关章节→[10-anti-patterns.md](10-anti-patterns.md)

**Codex / AI编程助手**：OpenAI Codex及同类AI代码助手（如Cursor、Trae等），属于Agent场景，需要特别注意文件边界、停止条件、危险操作禁止等安全约束。相关章节→[08-codex-scenarios.md](08-codex-scenarios.md)

---

### F

**First Principles / 第一性原理（七概念F）**：七概念方法论中的"F"，指回归事物本质思考问题，不被现有做法和惯性思维限制。对应Prompt中的Goal目标定义——想清楚你真正要什么，而不是照搬别人的Prompt模板。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

**Few-shot / 少样本**：在Prompt中提供几个示例让模型学习输出格式和风格，适用于输出格式要求比较特殊的场景。新范式下优先用Output Format明确描述，示例作为补充。

---

### G

**GCOB 框架**：本方法论提出的Prompt核心四要素：Goal（目标）、Context（上下文）、Output（输出格式）、Boundaries（边界约束），取代旧的RICE角色设定框架。相关章节→[03-gcob-framework.md](03-gcob-framework.md)

**Goal / 目标（GCOB-G）**：GCOB框架四要素之首，明确告诉模型"要什么"——具体、可衡量、有完成标准，不用形容词。相关章节→[03-gcob-framework.md](03-gcob-framework.md)

---

### H

**Hallucination / 幻觉**：模型生成看似合理但实际错误、不存在的信息。解决方法不是教模型"不要编"，而是明确信息核验要求——缺失信息标注[待确认]或停下来问，只用你提供的数据。相关章节→[04-new-paradigm-rules.md](04-new-paradigm-rules.md)

---

### I

**Insight / 洞察（七概念I）**：七概念方法论中的"I"，指从事实和问题中提炼本质原因和可行动的认知，对应Prompt效果不好时的根因分析——不要只改表面措辞，找到真正影响效果的核心问题。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

---

### O

**Output / 输出格式（GCOB-O）**：GCOB框架四要素之一，明确告诉模型"怎么给"——什么格式（Markdown/表格/代码/JSON）、多长、给谁看、结构要求。相关章节→[03-gcob-framework.md](03-gcob-framework.md)

---

### P

**Prompt Engineering / 提示词工程**：通过设计和优化输入提示来引导大语言模型产生期望输出的技术。本方法论认为新范式下Prompt Engineering本质是"清晰思考的表达"，而非"骗模型说正确的话"。相关章节→[00-overview.md](00-overview.md)

---

### Q

**Queue / 排队模式**：Codex/Agent交互模式之一，按Tab键让模型继续生成下一部分，适用于你确认当前方向正确、希望继续推进的场景。与Steer（转向）对应。相关章节→[08-codex-scenarios.md](08-codex-scenarios.md)

---

### R

**R (Retrospective) / 复盘**：七概念方法论中的"R"，任务完成后回顾过程——哪些Prompt有效哪些无效、为什么、下次怎么改进，对应输出Review和效果分析。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

---

### S

**Steer / 转向模式**：Codex/Agent交互模式之一，按Enter键打断模型当前方向，给出新的指令调整方向，适用于发现模型跑偏了、需要纠正或补充要求的场景。与Queue（排队）对应。相关章节→[08-codex-scenarios.md](08-codex-scenarios.md)

---

### T

**Token / 令牌**：大语言模型处理文本的基本单位，一个Token大约对应0.75个英文单词或0.5个汉字。上下文窗口长度、API计费都以Token为单位计算。

---

### Z

**Zero-shot / 零样本**：不给任何示例，直接描述任务要求让模型完成。GPT-4/Claude等新模型零样本能力已经很强，多数场景不需要给示例，清晰描述要求即可。

---

### 七概念完整列表

| 字母 | 中文 | 英文 | 对应Prompt环节 |
|------|------|------|---------------|
| R | 复盘 | Retrospective | 输出Review、效果分析 |
| I | 洞察 | Insight | 问题根因分析 |
| E | 萃取 | Extraction | 模板沉淀、模式复用 |
| C | 原子提交 | Atomic Commit | 分步迭代、Steer/Queue |
| A | 原子化 | Atomization | Output结构设计 |
| F | 第一性原理 | First Principles | Goal目标定义 |
| V | 对抗性审查 | Adversarial Review | Boundaries边界+Checkpoint |

相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

---

**萃取 E（Extraction）**：七概念方法论中的"E"，从成功案例和经验中提炼可复用的模板、模式、Checklist，沉淀为可重复使用的资产，对应本Wiki提供的模板库。相关章节→[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)、[09-checklists-templates.md](09-checklists-templates.md)

---

## 3. 本章小结

### 3.1 核心内容回顾

1. **GCOB四要素**：Goal（目标）、Context（上下文）、Output（输出）、Boundaries（边界）是Prompt写作的核心框架
2. **七概念方法论**：R-I-E-C-A-F-V七个维度覆盖从目标定义到复盘沉淀的完整闭环
3. **关键技术术语**：Checkpoint、Hallucination、Context Window、Token等是日常使用中必须理解的基础概念
4. **交互模式**：Steer（转向，Enter）和Queue（排队，Tab）是Codex场景的两种核心交互方式

### 3.2 使用建议

- 遇到不懂的术语先查本章，再去对应章节深入阅读
- 术语定义力求简洁，需要深入理解点击相关章节链接
- 本术语表会持续更新，实践中遇到新术语欢迎补充

### 3.3 下一步

术语查阅方便了，但实践中你一定会遇到很多具体问题——为什么我的Prompt按新写法写了还是效果不好？简单任务真的不需要五段结构吗？模型总是幻觉怎么办？下一章FAQ收集了最常见的12个实践问题，每个都给出简洁实用的回答。

👉 继续阅读：[12-faq-resources.md](12-faq-resources.md)（常见问题与资源索引）
👉 返回上一章：[10-anti-patterns.md](10-anti-patterns.md)（反模式：20+个Prompt写法陷阱）

---

*本文件版本：v1.0 | 创建日期：2026-07-13 | 状态：🚧 建设中 | 来源：SpecWeave七概念方法论 + OpenAI官方术语*
