---
id: "five-layer-document-architecture"
source: "docs/retrospective/reports/insight-extraction/external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/insights/doc-five-layer-architecture.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/architecture-patterns/five-layer-document-architecture.toml"
---
# 文档五层架构：规格→决策→质量→交付→萃取

## 模型概述

AI 协作项目的通用文档骨架，从内向外五层递进，对应 AI 协作中的五个核心风险点。该架构不是预先设计的，而是在竹简悟道十四轮迭代中自然演化出来的。

## 五层详解

| 层级 | 核心问题 | 文档形态 | AI 协作中的角色 |
|------|---------|---------|----------------|
| L1 规格层 | 我们要做什么？ | Spec 九节结构 | 为所有后续决策提供锚点，防止范围蔓延 |
| L2 决策层 | 为什么这样做？ | 洞察库（分层编号） | 让 AI 在修改代码前能追溯设计意图 |
| L3 质量层 | 现在一致吗？ | 滚动复盘报告 | 防止多轮迭代后文档间出现矛盾 |
| L4 交付层 | 能交出去了吗？ | 交付专项复盘 | 验证对外材料与内部设计的一致性 |
| L5 萃取层 | 下次怎么更好？ | 可迁移资产 | 将项目经验转化为可复用方法论 |

## 风险-对策映射

```
范围模糊 → L1规格层锚定
决策无据 → L2决策层追溯
版本漂移 → L3质量层校验
交付脱节 → L4交付层验证
经验流失 → L5萃取层沉淀
```

## 最小可行版本

不需要一开始就建全五层，最小可行版本只需 L1+L2+L3：
1. L1：写一份产品Spec（不需要很长，但要回答核心问题）
2. L2：记录关键设计决策（为什么选这个方案）
3. L3：每2-3次变更后跑一轮轻量复盘

L4（交付层）在需要对外发布/路演/参赛时添加，L5（萃取层）在项目结束或阶段性里程碑时添加。

## 与三层治理模型的关系

本模式是文档的**内容层级架构**，定义每层放什么类型的文档；`three-tier-governance` 是文档的**治理流程架构**，定义如何维护质量。两者互补：

| 维度 | five-layer-document-architecture | three-tier-governance |
|------|----------------------------------|-----------------------|
| 关注点 | 文档内容分层（What/Why） | 文档治理流程（How） |
| 层级 | 5层（规格/决策/质量/交付/萃取） | 3层（原子化/自动化/验证） |
| 阶段 | 项目启动即建立 | 文档累积到一定规模后引入 |

## 适用场景

- AI 协作的产品型项目（极高适用性）
- 需要多轮迭代的创意类项目
- 需要沉淀方法论的知识型项目
- 最小适用规模：≥5个文档或≥3轮迭代

> 来源：竹简悟道 Specs 文档体系十四轮迭代自然演化
> 关联模式：`three-tier-governance`、`spec-nine-section-narrative`、`rolling-retro-eight-steps`
