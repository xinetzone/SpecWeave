---
id: "karpathy-llm-coding-guidelines-specweave-integration"
title: "SpecWeave 项目整合情况"
category: learning
tags: [karpathy, llm, coding, agent, guidelines, specweave, integration, rules]
date: "2026-07-02"
status: stable
author: "SpecWeave Team"
summary: "Karpathy LLM编程准则在SpecWeave项目中的整合情况：四条原则如何融入现有规范体系，对应的规范文件位置，以及团队使用方式。"
source: "SpecWeave 规范体系整合"
x-toml-ref: "../../../../../.meta/toml/docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/04-specweave-integration.toml"
---
# SpecWeave 项目整合情况

## 整合概述

SpecWeave 项目已经将 Karpathy LLM 编程四条准则**有机融入**到现有规范体系中，而不是作为独立文件添加。这样做的好处是：

- 不破坏现有规范结构
- 各原则归位到最合适的上下文中
- 与原有规范形成互补而非重复
- 保持了 SpecWeave 规范体系的系统性

---

## 整合位置对照表

| Karpathy 原则 | 整合位置 | 说明 |
|--------------|---------|------|
| **原则一：编码前先思考（歧义澄清）** | [global-core-rules.md](../../../../../.agents/global-core-rules.md) | 新增「歧义主动澄清」全局核心规则 |
| **原则二：简约至上** | [development-standards.md](../../../../development-standards.md) | 新增「简约设计原则」章节（6条具体规则） |
| **原则三：精确编辑** | [developer.md](../../../../../.agents/roles/developer.md) | 新增「外科手术式精确编辑」职责与Non-Goals约束 |
| **原则四：目标驱动** | [development-standards.md](../../../../development-standards.md) | 融入「简约设计原则」第6条 + 测试工作流 |
| **完整速查指南** | [ai-coding-guidelines.md](../../../../../.agents/rules/ai-coding-guidelines.md) | 独立规则文档，含一分钟速查表、正反例、工作流整合 |

---

## 各文件详细修改

### 1. 全局核心规则：歧义主动澄清

**文件：** [.agents/global-core-rules.md](../../../../../.agents/global-core-rules.md)

新增规则（"代码修改"规则之后）：

> - **歧义主动澄清**：遇到需求不明确、存在多种理解方式、或发现更简单方案时，必须先向用户提问澄清或列出选项供用户选择，禁止自行猜测意图并直接实施。若发现用户指定方案存在更优解，应主动提出建议而非静默修改。澄清成本远低于返工成本——提前澄清30秒，可能避免40分钟的错误分支执行。

---

### 2. 开发者角色：外科手术式精确编辑

**文件：** [.agents/roles/developer.md](../../../../../.agents/roles/developer.md)

**Responsibilities 新增：**
> - **外科手术式精确编辑**：代码修改遵循最小改动原则，只修改被要求修改的部分；每一行代码变更都应能直接追溯到用户需求或任务要求；严格匹配项目现有代码风格，即使认为现有风格可改进也不擅自变更；因自身修改导致的孤儿代码（未使用的导入、变量、函数）必须清理

**Non-Goals 新增：**
> - 不"顺手优化"或重构与当前任务无关的代码——发现遗留问题或可改进点时，仅向用户报告说明，不自行修改

---

### 3. 开发规范：简约设计原则

**文件：** [docs/development-standards.md](../../../../development-standards.md)

新增完整章节（"代码风格"之后）：

> ## 简约设计原则
>
> 代码与设计遵循"简约至上"原则，避免过度设计：
>
> 1. **不做未被要求的功能**：只实现明确要求的功能，不"顺手添加"自以为有用的额外特性。
> 2. **不提前抽象**：只用一次的代码不建立抽象层（函数、类、模块等）；当代码第二次被复用时再考虑抽象。
> 3. **不添加未要求的灵活性**：没人要求的"可配置性""扩展性""灵活性"一律不加——YAGNI（You Aren't Gonna Need It）。
> 4. **不过度处理错误**：不可能发生的异常场景不做防御性错误处理；仅处理合理可预期的错误路径。
> 5. **复杂度检验标准**：写完代码后自问——"一个资深工程师看了会不会说'这太复杂了'？"如果答案是会，立即重构简化。
> 6. **目标驱动任务描述**：描述任务时优先给出验收标准（如"先写能复现bug的测试，然后让它通过"），而非具体实现步骤；复杂任务先列出分步计划并标注每步验证方式。
>
> **核心思想**：能50行解决的问题不要写200行；明确的验收标准让AI能独立循环执行，减少不必要的人工介入。

---

### 4. 独立规则文档：AI编码行为准则

**文件：** [.agents/rules/ai-coding-guidelines.md](../../../../../.agents/rules/ai-coding-guidelines.md)

这是一份完整的独立规则文档，包含：

- ⚡ **一分钟速查表** - 四原则口诀+核心要求+一句话反例
- 📖 **详细原则说明** - 每条原则的问题根源、具体要求、反例vs正例对比表
- 🔄 **工作流整合** - Mermaid 流程图展示四条原则如何融入开发流程
- ❌ **常见陷阱速查** - 6个常见陷阱对应原则和避免方法
- 📚 **溯源与参考** - 来源说明和整合位置记录

同时更新了：
- [.agents/rules/README.md](../../../../../.agents/rules/) - 规则清单、场景导航、角色导航
- [.agents/context-routing.md](../../../../../.agents/context-routing.md) - 上下文路由表

---

## 与现有规范的协同关系

| SpecWeave 现有规范 | 与 Karpathy 准则的关系 |
|-------------------|----------------------|
| 启动协议（AGENTS.md） | 启动协议要求"先读规范再动手"，与原则一（编码前思考）形成互补——读规范是减少歧义的重要手段 |
| 前置文档强制读取协议 | 读取相关文档后再动手，本身就是"不猜测"的具体实践 |
| 阶段守卫规则 | 阶段守卫防止跨阶段操作，与原则三（精确编辑）理念一致——不在当前阶段做不该做的事 |
| 禁止重复实现 | 检查共享库、禁止重复造轮子，是原则二（简约至上）的具体体现 |
| 原子化操作规范 | 文档移动的四步闭环，本质上也是"精确编辑"在文档操作上的应用 |
| Dry-Run 原则 | 自动化修改先预览再执行，与原则四（目标驱动）的"先验证再执行"理念一致 |
| CI 检查流水线 | 8步验证流水线是"目标驱动"中验收标准的工程化落地 |
| 测试覆盖率要求（≥80%） | 测试优先是原则四（目标驱动）的核心实践 |

---

## 团队使用指南

### AI 智能体使用

所有 AI 智能体在启动时通过上下文路由表自动加载 [ai-coding-guidelines.md](../../../../../.agents/rules/ai-coding-guidelines.md)，无需手动配置。

### 人类开发者使用

1. **快速回顾**：看 [ai-coding-guidelines.md](../../../../../.agents/rules/ai-coding-guidelines.md) 开头的「一分钟速查表」
2. **遇到具体问题**：查「常见陷阱速查」或「反例 vs 正例」
3. **给 AI 描述任务时**：遵循原则四——给验收标准，别给具体步骤
4. **Review AI 代码时**：用四条原则作为检查清单

### 任务描述模板（推荐）

```
[任务描述：要做什么]

验收标准：
1. [具体可验证的标准1]
2. [具体可验证的标准2]
3. [具体可验证的标准3]

约束：
- 只修改相关文件，不要顺手改不相关的代码
- 遵循现有代码风格
- 如有疑问先提问澄清
```

---

## 验证清单

每次 AI 完成任务后，可以用这个清单快速检查：

| 检查项 | 对应原则 |
|--------|---------|
| □ AI 是否在开始前问了必要的澄清问题？ | 原则一 |
| □ 是否有未被要求的功能/抽象/配置？ | 原则二 |
| □ diff 中是否有与任务无关的改动？ | 原则三 |
| □ 是否有明确的验收标准且都通过了？ | 原则四 |
| □ 是否匹配了现有代码风格？ | 原则三 |
| □ 因修改产生的孤儿代码是否清理了？ | 原则三 |

---

## 本教程文档

除了规范整合，项目中还存放了完整的学习教程，位于：

[docs/knowledge/learning/02-agent-engineering-methodology/karpathy-llm-coding-guidelines/](./)

包含：
- [00-overview.md](00-overview.md) - 概述与背景故事
- [01-four-principles.md](01-four-principles.md) - 四条原则详解 + CLAUDE.md原文
- [02-code-examples.md](02-code-examples.md) - 真实代码正反例
- [03-quickstart.md](03-quickstart.md) - 安装使用指南
- 本文档 - SpecWeave 整合情况
- [05-resources.md](05-resources.md) - 资源链接
