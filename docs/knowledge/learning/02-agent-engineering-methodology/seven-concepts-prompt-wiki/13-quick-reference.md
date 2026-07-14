---
id: "seven-concepts-quickref"
title: "13、快速参考速查表（一页纸）"
category: "reference"
date: "2026-07-13"
version: "1.0"
status: "completed"
source: "七概念Prompt Wiki精华汇总"
---

# 快速参考速查表（一页纸）

---

## 1. 使用说明

本文是整份Wiki的精华浓缩，建议打印出来贴在显示器旁，写Prompt时快速查阅。

---

## 2. 🎯 一句话核心原则

> **明确目标，说清上下文，规定输出格式，划清边界，设置停止条件——不要教模型怎么思考。**

---

## 3. 📐 GCOB四要素速查表

| 要素 | 一句话说明 | 关键问题 |
|------|-----------|---------|
| **G**oal | 要什么 | 模型知道我要什么吗？完成标准是什么？ |
| **C**ontext | 知道什么 | 哪些背景必须给？哪些信息不能猜？ |
| **O**utput | 怎么给 | 什么格式？多长？给谁看？ |
| **B**oundaries | 不能做什么 | 哪些操作禁止？哪些话不能说？ |

→ 详解：[03-gcob-framework.md](03-gcob-framework.md)

---

## 4. 🔢 Prompt长度选择速查表

| 级别 | 长度 | 适用场景 | 结构 |
|------|------|---------|------|
| 简单 | 1-2句话 | 翻译、润色、简单问答 | 直说需求 |
| 普通 | 3段 | 写文案、解释概念、简单总结 | Context + Request + Format |
| 复杂 | 五段式 | 研究报告、长文档、专业内容 | Context + Request + Format + Constraints + Checkpoint |
| Agent | 六段+白名单 | Codex写代码、多工具任务 | 上述+文件白名单+工具权限+先计划后动手 |

→ 场景详解：[06-chat-scenarios.md](06-chat-scenarios.md) | [07-work-scenarios.md](07-work-scenarios.md) | [08-codex-scenarios.md](08-codex-scenarios.md)

---

## 5. ✅ 写完必查5问

1. **知道要什么吗？** → 目标具体，不用形容词
2. **知道怎么算完吗？** → 输出格式、完成标准明确
3. **知道不能猜吗？** → 关键背景给了，信息不足有处理方式
4. **知道不能越界吗？** → 红线说清楚了（特别是Codex）
5. **知道该停吗？** → Checkpoint设置了，什么情况停下来问

→ 扩展版：[09-checklists-templates.md](09-checklists-templates.md)

---

## 6. 🚫 5个最容易犯的错

| # | 错误 | 正确做法 |
|---|------|---------|
| 1 | 用形容词（深入/全面/专业/高质量） | 说具体要什么、回答哪几个问题 |
| 2 | 教模型思考（三轮反思/专家辩论/第一步A第二步B） | 说清目标和验收标准，让模型自己找路径 |
| 3 | 没有明确的完成标准 | 说清楚输出格式、长度、给谁看 |
| 4 | 没有Checkpoint停止条件（Agent场景） | 列出"遇到这些情况停下来问我" |
| 5 | 不设边界（特别是Codex改代码） | 用白名单：哪些文件/操作允许，其他都不行 |

→ 更多反模式：[10-anti-patterns.md](10-anti-patterns.md)

---

## 7. 🔗 七概念映射速查表

| 七概念 | 中文 | Prompt对应环节 |
|--------|------|---------------|
| **F**irst Principles | 第一性原理 | Goal目标定义——想清楚你真正要什么 |
| **A**tomization | 原子化 | Output结构设计——拆分成清晰的小任务 |
| **V**erification（Adversarial Review）| 对抗性审查 | Boundaries边界+Checkpoint——找漏洞设红线 |
| **C**ommit（Atomic Commit）| 原子提交 | 分步迭代、Steer/Queue交互——每次只做一步 |
| **R**etrospective | 复盘 | 输出Review、效果分析——总结哪些有效哪些无效 |
| **I**nsight | 洞察 | 问题根因分析——找到效果不好的核心原因 |
| **E**xtraction | 萃取 | 模板沉淀、模式复用——把好的Prompt变成模板 |

→ 详解：[02-seven-concepts-mapping.md](02-seven-concepts-mapping.md)

---

## 8. 📁 文件导航速查表

| 文件 | 内容 | 适用场景 |
|------|------|---------|
| [00-overview.md](00-overview.md) | 方法论总览 | 第一次了解看这个 |
| [01-paradigm-shift.md](01-paradigm-shift.md) | 范式转变：为什么旧写法过时了 | 理解为什么要改 |
| [02-seven-concepts-mapping.md](02-seven-concepts-mapping.md) | 七概念与Prompt映射关系 | 理解底层方法论 |
| [03-gcob-framework.md](03-gcob-framework.md) | GCOB四要素框架详解 | 核心框架，必看 |
| [04-new-paradigm-rules.md](04-new-paradigm-rules.md) | 新范式10条核心规则 | 具体规则条目 |
| [05-before-after-examples.md](05-before-after-examples.md) | Before/After对照示例 | 看对比找感觉 |
| [06-chat-scenarios.md](06-chat-scenarios.md) | Chat场景实战 | 日常聊天、简单问答 |
| [07-work-scenarios.md](07-work-scenarios.md) | Work场景实战 | 写报告、文档、专业内容 |
| [08-codex-scenarios.md](08-codex-scenarios.md) | Codex/Agent场景基础 | AI写代码安全原则、标准结构 |
| [08b-codex-examples.md](08b-codex-examples.md) | Codex/Agent场景实战 | 8个高频场景完整Prompt模板 |
| [09-checklists-templates.md](09-checklists-templates.md) | 检查清单+6个可复用模板 | 直接复制填空 |
| [10-anti-patterns.md](10-anti-patterns.md) | 25个反模式避坑指南 | 踩坑时回来查 |
| [11-glossary.md](11-glossary.md) | 术语表 | 遇到不懂的术语查 |
| [12-faq-resources.md](12-faq-resources.md) | 12个常见问题+资源索引 | 有问题先查FAQ |
| [13-quick-reference.md](13-quick-reference.md) | 本页·一页纸速查表 | 日常快速查阅 |
| [README.md](README.md) | 目录与导读 | Wiki入口 |

---

## 9. 🎓 学习路径

- **入门路径**（1小时）：00→01→04→05→13
- **开发者路径**（3小时）：00→01→02→03→04→05→08→08b→09→10→13
- **精通路径**：全部通读 + 大量实践 + 每次Prompt后复盘改进

---

## 10. Wiki结束语

> **提示词工程不是"骗"模型说正确的话，而是清晰地表达你的需求。**
>
> 好的Prompt本质上是清晰的思考——当你能把一个需求用GCOB四要素清晰描述出来时，你自己对问题的理解也更深了。模型能力越来越强，你不需要学各种"魔法咒语"，你只需要学会**想清楚、说明白**。
>
> 少即是多，慢即是快。

---

*本文件版本：v1.0 | 创建日期：2026-07-13 | 状态：✅ 已完成 | 祝使用愉快 🎉*
