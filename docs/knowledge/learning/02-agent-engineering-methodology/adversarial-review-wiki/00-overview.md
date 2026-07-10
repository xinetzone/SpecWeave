---
id: "adversarial-review-overview"
title: "00、概述与背景"
category: "knowledge"
date: "2026-07-10"
version: "1.0"
status: "completed"
---

# 对抗性审查知识库：概述与背景

---

## 1. 项目简介

本知识库是对抗性审查（Adversarial Review）方法论的系统化知识档案，旨在为知识研究、AI协作、代码审查、安全工程等场景提供经过验证的可信参考。

本档案最大特色在于采用**自举验证**——用对抗性审查方法自身来构建对抗性审查知识库：
- 所有内容均经过五维验证流程审查
- 主动寻找反证而非堆砌支持性证据
- 系统识别并标注认知偏差
- 明确标注资料可信度等级
- 对存在争议的观点如实呈现各方立场

---

## 2. 资料概览

本知识库共包含 **15个核心文件**（00-13共14篇文档 + README索引），覆盖从哲学起源到工程实践的完整体系：

**自举验证质量达标情况**（截至2026-07-10）：

| 验收指标 | 目标要求 | 实际结果 | 达标情况 |
|---------|---------|---------|---------|
| 核心文件数 | 15个 | 15个（00-13 + README） | ✅ 达标 |
| 一级来源占比 | ≥70% | 75.0%（42/56） | ✅ 达标 |
| 🟢A级资料占比 | ≥60% | 69.8%（187/268） | ✅ 达标 |
| 🔴D级资料占比 | =0% | 0% | ✅ 达标 |
| 关键事实交叉验证率 | 100% | 10/10 = 100% | ✅ 达标 |

**覆盖范围**：哲学起源→核心概念→两大场景方法论→认知偏差防御→检查清单→行业标准→开源工具→实战案例→学术资源→术语表→资源索引→速查表，完整闭环。

---

## 3. 可信度评级说明

本档案采用四级可信度评级体系，并配合四类异常标记如实标注资料的不确定性。

### 3.1 可信度评级

| 标记 | 等级 | 判定标准 | 使用建议 |
|------|------|---------|---------|
| 🟢 | **A级** | 多权威来源交叉验证（≥2个独立一级来源）；无利益冲突；可追溯至原始出处；方法论明确可检验 | 核心论据，可直接引用，作为推理基石 |
| 🔵 | **B级** | 单一权威一级来源；逻辑自洽；无明显偏差；领域内共识度高 | 可作为辅助论据，标注来源，鼓励交叉验证 |
| 🟡 | **C级** | 二级来源；需进一步验证；存在潜在偏差；观点非普遍共识 | 仅作参考，必须标注"待验证"，不得作为独立论据 |
| 🔴 | **D级** | 存疑；无法验证；存在明显矛盾或利益冲突；来源不可追溯 | 不纳入核心档案；仅作为反面案例或问题线索记录 |

### 3.2 异常标记

| 标记 | 类型 | 含义 |
|------|------|------|
| ⚠️ | 待验证 | 内容尚未完成多来源交叉验证，需进一步追溯确认 |
| ❓ | 存疑 | 内容与其他权威来源存在矛盾，或逻辑上存在疑问 |
| ⚖️ | 争议观点 | 学术/工程领域内存在明确学派争议，各方均有论据 |
| 🔍 | 利益冲突提示 | 来源/作者与结论存在商业、职业或立场关联，可能影响客观性 |

---

## 4. 分层次阅读路径

根据不同读者背景和目的，推荐以下阅读路径：

### 🌱 路径一：入门初学者
**适合人群**：对对抗性审查仅有耳闻、希望系统了解概念的读者
**阅读目标**：建立基本认知，理解核心价值

```
README.md（索引入口）
→ 00-overview.md（本文件，建立全局认知）
→ 01-core-concepts.md（核心概念定义，理解是什么）
→ 02-philosophy-origins.md（思想源头，理解为什么）
→ 03-methodology-framework.md（方法论框架，掌握怎么做）
→ 08-practice-cases.md（实战案例，建立直观感受）
→ 13-quick-reference.md（速查表，随时查阅）
```

### 👨‍💻 路径二：AI开发者&代码审查者
**适合人群**：使用LLM进行开发、需要做代码审查的工程师
**阅读目标**：快速上手对抗式审查Prompt模式，提升代码质量

```
00-overview.md（本文件，概览）
→ 01-core-concepts.md 第3-4章（两大应用分支+核心原则）
→ 03-methodology-framework.md（AI协作/代码审查五步法）
→ 05-checklists-templates.md（检查清单与工具模板，直接复用）
→ 07-open-source-tools.md（开源工具链，辅助自动化）
→ 08-practice-cases.md（重点看AIHOT项目案例）
→ 04-cognitive-biases-defense.md（重点看确认偏差防御）
→ 06-industry-standards.md（行业标准与合规要求）
```

### 📚 路径三：知识工程师&研究者
**适合人群**：做知识管理、学术研究、需要验证资料可信度的读者
**阅读目标**：掌握七模块验证协议，构建可信知识体系

```
README.md（索引入口）
→ 00-overview.md（本文件，了解档案定位）
→ 01-core-concepts.md 第3章（知识研究场景分支）
→ 02-philosophy-origins.md（思想源头，理解证伪主义传统）
→ 03-methodology-framework.md（知识研究七模块协议）
→ 05-checklists-templates.md（五维验证检查清单，直接复用）
→ 04-cognitive-biases-defense.md（12类审查场景偏差识别与防御）
→ 10-source-validation-log.md（来源验证日志参考，自举验证实例）
→ 09-academic-resources.md（学术资源与推荐阅读）
```

### 🔒 路径四：安全工程师
**适合人群**：安全审计、渗透测试、红队演练从业者
**阅读目标**：理解对抗性思维的方法论基础，与现有安全实践整合

```
00-overview.md（本文件，概览）
→ 01-core-concepts.md 第2章（相关概念辨析，对比红队/渗透测试）
→ 02-philosophy-origins.md 第4章（军事/安全领域红队演练起源）
→ 06-industry-standards.md（OWASP/NIST/MITRE/EU AI Act）
→ 07-open-source-tools.md（Garak/PyRIT/Promptfoo等红队工具）
→ 08-practice-cases.md（实战案例，安全相关场景）
→ 04-cognitive-biases-defense.md（安全领域认知偏差）
```

---

## 5. 文件导航表

| 序号 | 文件名 | 标题 | 内容简介 | 难度等级 | 建议阅读顺序 |
|------|--------|------|---------|---------|-------------|
| - | [README.md](README.md) | 文档索引 | 本知识库索引入口，包含完整文档列表、主题概述和相关资源链接。 | 入门 | 0（入口） |
| 00 | [00-overview.md](00-overview.md) | 概述与背景 | 项目简介、资料概览、可信度评级说明、分层次阅读路径、文件导航、快速链接。 | 入门 | 1（先读） |
| 01 | [01-core-concepts.md](01-core-concepts.md) | 核心概念定义 | 对抗性审查精确定义、相关概念辨析（vs代码审查/红队/QA/审计/渗透测试/同行评审）、两大应用分支、核心原则列表。 | 入门-进阶 | 2 |
| 02 | [02-philosophy-origins.md](02-philosophy-origins.md) | 思想源头追溯 | 科学革命怀疑主义、波普尔证伪主义、双盲同行评审、军事红队起源、认知心理学革命、LLM红队测试现代发展。 | 进阶 | 3 |
| 03 | [03-methodology-framework.md](03-methodology-framework.md) | 方法论框架 | 知识研究七模块协议、AI协作/代码审查五步法、两大场景检查维度、适用边界与7类反模式。 | 进阶 | 4 |
| 04 | [04-cognitive-biases-defense.md](04-cognitive-biases-defense.md) | 认知偏差防御 | 审查场景12类高频认知偏差（确认偏差/幸存者偏差/权威崇拜等）、识别特征、防御措施、检查项。 | 进阶 | 5 |
| 05 | [05-checklists-templates.md](05-checklists-templates.md) | 检查清单与工具模板 | 五维验证清单、四大攻击者角色Prompt模板、代码审查Checklist、验证日志模板、最小可行审查指南。 | 进阶 | 6 |
| 06 | [06-industry-standards.md](06-industry-standards.md) | 行业标准与合规要求 | OWASP LLM Top 10、NIST AI RMF、MITRE ATLAS/ATT&CK、EU AI Act、ISO/IEC 42001、Google代码审查标准。 | 专业 | 7 |
| 07 | [07-open-source-tools.md](07-open-source-tools.md) | 开源工具链指南 | Garak(NVIDIA)/PyRIT(Microsoft)/Promptfoo(OpenAI)/Inspect AI/DeepTeam/Purple Llama(Meta)六大工具详解、工具对比矩阵、CI/CD集成。 | 进阶 | 8 |
| 08 | [08-practice-cases.md](08-practice-cases.md) | 实战案例集 | AIHOT 40Agent审查案例（OOM死循环/未来时间污染/性能炸弹）、OpenAI/NVIDIA/Microsoft/Anthropic红队实践案例。 | 入门-进阶 | 9 |
| 09 | [09-academic-resources.md](09-academic-resources.md) | 学术资源与推荐阅读 | 哲学经典、认知心理学奠基文献、顶会论文（USENIX Security/AISec/ICPC/PLOS One）、推荐书籍、争议观点整理。 | 进阶 | 10 |
| 10 | [10-source-validation-log.md](10-source-validation-log.md) | 来源验证档案（自举验证） | 五维验证执行记录、来源类型统计（56个来源）、可信度分布（268个内容点）、10个关键事实交叉验证日志、偏差防御记录。 | 专业 | 最后读 |
| 11 | [11-glossary.md](11-glossary.md) | 核心术语表 | 对抗性审查相关术语定义、中英文对照、可信度/异常标记说明、相关概念索引。 | 参考 | 随时查阅 |
| 12 | [12-resources.md](12-resources.md) | 延伸阅读与资源索引 | 延伸阅读资源、外部链接汇总、相关项目索引、在线学习资源。 | 参考 | 进阶后阅读 |
| 13 | [13-quick-reference.md](13-quick-reference.md) | 快速参考速查表 | 核心原则速查、攻击者角色速查、检查清单速查、可信度等级速查、关键数字速查。 | 入门 | 随时查阅 |

---

## 6. 快速链接表

| 用途 | 链接 | 状态 |
|------|------|------|
| 📖 核心概念速查 | [01-core-concepts.md](01-core-concepts.md) | ✅ 已完成 |
| 🏛️ 思想源头追溯 | [02-philosophy-origins.md](02-philosophy-origins.md) | ✅ 已完成 |
| 🔬 方法论框架 | [03-methodology-framework.md](03-methodology-framework.md) | ✅ 已完成 |
| 🧠 认知偏差防御 | [04-cognitive-biases-defense.md](04-cognitive-biases-defense.md) | ✅ 已完成 |
| ✅ 检查清单模板 | [05-checklists-templates.md](05-checklists-templates.md) | ✅ 已完成 |
| 📋 行业标准 | [06-industry-standards.md](06-industry-standards.md) | ✅ 已完成 |
| 🛠️ 开源工具链 | [07-open-source-tools.md](07-open-source-tools.md) | ✅ 已完成 |
| 📂 实战案例集 | [08-practice-cases.md](08-practice-cases.md) | ✅ 已完成 |
| 📚 学术资源 | [09-academic-resources.md](09-academic-resources.md) | ✅ 已完成 |
| 📝 自举验证日志 | [10-source-validation-log.md](10-source-validation-log.md) | ✅ 已完成 |
| 🔤 术语表 | [11-glossary.md](11-glossary.md) | ✅ 已完成 |
| ⚡ 速查表 | [13-quick-reference.md](13-quick-reference.md) | ✅ 已完成 |

---

## 7. 相关项目文档

本知识库是Agent工程方法论体系的组成部分，相关参考文档：

- 对抗性审查标准与验证流程原始规范：[first-principles/00-adversarial-review-protocol.md](../../first-principles/00-adversarial-review-protocol.md)
- 对抗式审查Prompt模式：[adversarial-review-prompt-pattern.md](../../../../retrospective/patterns/methodology-patterns/ai-collaboration/adversarial-review-prompt-pattern.md)
- 第一性原理知识库：[first-principles/README.md](../../first-principles/README.md)

---

*本文件版本：v1.0 | 创建日期：2026-07-10 | 最后更新：2026-07-10 | 自举验证：✅ 所有质量指标达标*
