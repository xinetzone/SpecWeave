---
id: seven-concepts-deeptutor-04-reading-guide
title: 分阶段阅读路径
source: "https://mp.weixin.qq.com/s/MfTnEwjQlBJX4bf0JsqbRw"
version: 1.0
date: "2026-07-14"
tags: [阅读路径, 学习指南]
---

# 分阶段阅读路径

---

根据你的时间和目标，选择适合你的阅读路径。每条路径都有明确的阶段划分、预计耗时和核心收获。

---

## 🌱 路径1：30分钟快速入门

**适合人群**：时间有限、想快速了解七概念和DeepTutor是什么的读者
**核心目标**：建立全局认知，知道七概念大概讲什么，DeepTutor是怎么体现这些概念的

### 阅读清单（按顺序）

| 步骤 | 文件 | 预计耗时 | 阅读重点 |
|------|------|---------|---------|
| 1 | [00-overview.md](../00-overview.md) | 5分钟 | 教程定位、四段式结构、目标读者 |
| 2 | [01-seven-concepts-theory/README.md](../01-seven-concepts-theory/README.md) | 10分钟 | 只看「七概念总览」和「公理速查表」，不用看每个概念的详细文件 |
| 3 | [02-deeptutor-case/00-deeptutor-overview.md](../02-deeptutor-case/00-deeptutor-overview.md) | 8分钟 | DeepTutor是什么、核心定位、六种学习模式 |
| 4 | [03-analysis/00-framework-mapping.md](../03-analysis/00-framework-mapping.md) | 7分钟 | 映射总览表，看每个概念对应DeepTutor的哪个设计 |

### 核心收获

读完这条路径后，你应该能：
- 说出七概念的名称和大概作用
- 知道DeepTutor是一个什么样的产品
- 理解"用七概念分析系统"大概是在做什么

**如果觉得有意思，继续走路径2深入学习。**

---

## 👨‍💻 路径2：2小时系统学习

**适合人群**：开发者、产品经理、想真正学会用七概念的方法论实践者
**核心目标**：完整理解七概念的公理和要素，能识别真实系统中的方法论体现

### 第一阶段：理论基础（30分钟）

| 步骤 | 文件 | 预计耗时 | 阅读重点 |
|------|------|---------|---------|
| 1.1 | [01-seven-concepts-theory/README.md](../01-seven-concepts-theory/README.md) | 5分钟 | 五层层级模型、公理速查表（建立框架） |
| 1.2 | [01-r-retrospective.md](../01-seven-concepts-theory/01-r-retrospective.md) | 4分钟 | R的四个要素、事实与判断的区别 |
| 1.3 | [02-i-insight.md](../01-seven-concepts-theory/02-i-insight.md) | 4分钟 | I的四元组格式、好洞察的四个标准 |
| 1.4 | [03-e-extraction.md](../01-seven-concepts-theory/03-e-extraction.md) | 4分钟 | E的四层漏斗、好模式的标准 |
| 1.5 | [04-c-atomic-commit.md](../01-seven-concepts-theory/04-c-atomic-commit.md) | 4分钟 | C的四个属性、原子行动项的标准 |
| 1.6 | [05-a-atomization.md](../01-seven-concepts-theory/05-a-atomization.md) | 4分钟 | A的粒度寻优、认知负荷与导航成本平衡 |
| 1.7 | [06-f-first-principles.md](../01-seven-concepts-theory/06-f-first-principles.md) | 3分钟 | F的5Why法、假设剥离 |
| 1.8 | [07-v-adversarial-review.md](../01-seven-concepts-theory/07-v-adversarial-review.md) | 2分钟 | V的四视角攻击、证伪思维 |

**阶段提示**：第一遍不用追求记住所有细节，重点理解每个概念的核心思想和4个要素是什么。

### 第二阶段：案例解剖（30分钟）

| 步骤 | 文件 | 预计耗时 | 阅读重点 |
|------|------|---------|---------|
| 2.1 | [02-deeptutor-case/00-deeptutor-overview.md](../02-deeptutor-case/00-deeptutor-overview.md) | 5分钟 | 六种学习模式、产品定位 |
| 2.2 | [02-deeptutor-case/01-core-architecture.md](../02-deeptutor-case/01-core-architecture.md) | 10分钟 | Agent引擎设计、九个导航模块、模式切换机制（这是最核心的） |
| 2.3 | [02-deeptutor-case/02-modules/README.md](../02-deeptutor-case/02-modules/README.md) | 2分钟 | 四个模块分组概览 |
| 2.4 | [02-deeptutor-case/02-modules/01-chat-partners-myagents.md](../02-deeptutor-case/02-modules/01-chat-partners-myagents.md) | 4分钟 | 对话交互、多角色、Agent管理 |
| 2.5 | [02-deeptutor-case/02-modules/02-cowriter-book.md](../02-deeptutor-case/02-modules/02-cowriter-book.md) | 3分钟 | 协作写作、内容组织 |
| 2.6 | [02-deeptutor-case/02-modules/03-knowledge-learning.md](../02-deeptutor-case/02-modules/03-knowledge-learning.md) | 3分钟 | 知识中心、学习空间 |
| 2.7 | [02-deeptutor-case/02-modules/04-memory-settings.md](../02-deeptutor-case/02-modules/04-memory-settings.md) | 3分钟 | 记忆系统、设置 |

**阶段提示**：读架构和模块的时候，多想想"为什么要这么设计"，不用纠结具体实现细节。

### 第三阶段：融合分析（45分钟）

| 步骤 | 文件 | 预计耗时 | 阅读重点 |
|------|------|---------|---------|
| 3.1 | [03-analysis/00-framework-mapping.md](../03-analysis/00-framework-mapping.md) | 5分钟 | 映射总览表，先有全局认识 |
| 3.2 | [03-analysis/01-r-in-deeptutor.md](../03-analysis/01-r-in-deeptutor.md) | 5分钟 | 三层记忆如何对应事实→推演→因果 |
| 3.3 | [03-analysis/02-i-in-deeptutor.md](../03-analysis/02-i-in-deeptutor.md) | 5分钟 | Mastery Path如何发现学习规律 |
| 3.4 | [03-analysis/03-e-in-deeptutor.md](../03-analysis/03-e-in-deeptutor.md) | 5分钟 | Knowledge Center如何做知识精炼 |
| 3.5 | [03-analysis/04-c-in-deeptutor.md](../03-analysis/04-c-in-deeptutor.md) | 5分钟 | 模式切换如何保持上下文原子性 |
| 3.6 | [03-analysis/05-a-in-deeptutor.md](../03-analysis/05-a-in-deeptutor.md) | 5分钟 | 九大模块的粒度寻优 |
| 3.7 | [03-analysis/06-f-in-deeptutor.md](../03-analysis/06-f-in-deeptutor.md) | 5分钟 | 从"终身个性化辅导"公理出发的设计 |
| 3.8 | [03-analysis/07-v-in-deeptutor.md](../03-analysis/07-v-in-deeptutor.md) | 5分钟 | Quiz和Mastery Path如何验证学习效果 |
| 3.9 | [03-analysis/08-combined-workflows.md](../03-analysis/08-combined-workflows.md) | 5分钟 | 三个组合工作流，看概念如何协同 |

**阶段提示**：读每个分析的时候，对照理论章节的4个要素，看DeepTutor的设计是如何对应每个要素的。这是最关键的一步。

### 第四阶段：实践检验（15分钟）

| 步骤 | 文件 | 预计耗时 | 做什么 |
|------|------|---------|--------|
| 4.1 | [02-self-checklist.md](02-self-checklist.md) | 10分钟 | 快速过一遍自检清单，评估自己的掌握程度 |
| 4.2 | [01-practice-exercises.md 练习1](01-practice-exercises.md) | 5分钟 | 看一下练习1的要求，知道接下来该做什么 |

### 核心收获

读完这条路径后，你应该能：
- 不看资料说出每个概念的公理和4个基础要素
- 指出DeepTutor中至少3-5个地方体现了哪个概念
- 理解七概念不是孤立的，而是协同工作形成闭环的

**接下来，强烈建议做练习巩固。**

---

## 🧠 路径3：实战拓展

**适合人群**：已经完成路径2，想把七概念用到自己项目中的深度实践者
**核心目标**：掌握用七概念框架分析真实系统、指导设计决策的能力

### 前置要求

- 完成路径2的全部阅读
- 有一个你熟悉的系统/项目可以分析（最好是你自己参与的）

### 实战步骤

| 阶段 | 内容 | 预计耗时 | 产出物 |
|------|------|---------|--------|
| 1 | 完成[01-practice-exercises.md](01-practice-exercises.md)中的**练习1：七概念快速自检** | 30分钟 | 默写答案、DeepTutor案例对应表、自己的设计思路 |
| 2 | 完成[01-practice-exercises.md](01-practice-exercises.md)中的**练习2：开源项目分析** | 60-90分钟 | 完整的项目分析报告，含评分 |
| 3 | 阅读[03-further-reading.md](03-further-reading.md)中的七概念完整方法论文档 | 2-3小时 | 对方法论体系有更深入的理解 |
| 4 | （可选）参与[governance-strategy/exercises/](../../../../retrospective/patterns/methodology-patterns/governance-strategy/exercises/README.md)中的90分钟团队实战演练 | 90分钟-3小时 | 团队复盘实战经验 |
| 5 | 用七概念分析你自己的项目，输出分析报告和改进建议 | 2-4小时 | 你自己项目的七概念分析报告 |

### 延伸阅读顺序建议

读完整方法论文档时，按这个顺序：

1. **七概念方法论体系索引** → 了解全貌
2. **本质定位与五层层级模型** → 深化理论理解
3. **组合触发决策树** → 学会判断什么时候用什么概念
4. **五种核心组合应用流程** → 看标准工作流
5. **质量标准与检查清单（完整版33项）** → 用来验收自己的分析
6. **实战演练材料** → 做团队练习
7. **自举对抗性审查报告** → 了解方法论的局限，避免教条

### 核心收获

完成这条路径后，你应该能：
- 独立用七概念分析任意一个软件系统
- 在做设计决策时，有意识地应用七概念（如：粒度拆分用A，变更提交用C，验证用V）
- 发现自己或他人设计中的问题，用七概念的语言清晰表达
- 把七概念变成自己的思维工具，而不是纸上谈兵

---

## ⏱️ 时间不够？紧急阅读方案

如果你只有10分钟，读这三个文件：

1. [00-overview.md](../00-overview.md)（2分钟）
2. [01-seven-concepts-theory/README.md](../01-seven-concepts-theory/README.md)的公理速查表（5分钟）
3. [03-analysis/00-framework-mapping.md](../03-analysis/00-framework-mapping.md)（3分钟）

至少能建立一个基本印象。

---

**下一章**：[实践练习](01-practice-exercises.md)
