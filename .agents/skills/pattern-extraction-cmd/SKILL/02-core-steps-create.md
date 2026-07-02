---
id: "pattern-extraction-core-steps-create"
title: "核心步骤与全新模式创建方案"
source: "SKILL.md#02-core-steps-create"
x-toml-ref: "../../../../.meta/toml/.agents/skills/pattern-extraction-cmd/SKILL/02-core-steps-create.toml"
---
# 核心步骤与全新模式创建方案

## 5. 核心步骤（快速开始）

```
步骤1：识别模式——确认是否满足可复用条件
   可复用三标准：
   □ 可命名：有清晰的问题场景和解决方案名称
   □ 可复现：在≥1个场景中成功验证
   □ 可迁移：核心机制不依赖特定上下文细节
步骤2：分类定位——确定归属目录
   □ 架构层 → architecture-patterns/
   □ 代码层 → code-patterns/
   □ 方法论层 → methodology-patterns/<子主题>/（7个子主题见L2）
步骤3：生成模式文档
   □ TOML frontmatter（id/domain/layer/maturity/validation_count等必填字段）
   □ 标准内容结构（问题→解决方案→适用场景→实际案例→反模式→相关模式）
步骤4：更新索引
   □ 更新对应目录的README.md，添加模式条目和一句话说明
   □ 更新CATEGORIES.md（如为方法论模式）
步骤5：质量验证
   □ 运行 python .agents/scripts/check-pattern-quality.py <模式文件>
   □ 运行 python .agents/scripts/pattern-maturity.py check-index --fix 更新统计
步骤6：向用户展示生成的模式文档，获得确认
```

> 完整的分类决策树、frontmatter字段说明、正反例写作要求见本文第6-8节；模式分类边界详见 [CATEGORIES.md](../../../../docs/retrospective/patterns/methodology-patterns/CATEGORIES.md)。

> **为什么必须先判断"可复用三标准"再创建模式？** 模式库的价值取决于信噪比——把一次性的特定解决方案沉淀为模式会稀释模式库质量，增加检索成本。只有同时满足"可命名+可复现+可迁移"三个条件的经验才值得沉淀，否则留在复盘报告中即可。这是从184个模式沉淀中总结出的关键质量门。


## 6. 方案一：全新模式创建（推荐）

### 6.1 模式文档标准结构

```markdown
+++
id = "<kebab-case-id>"
domain = "architecture|code|methodology"
layer = "architecture|code|methodology"
maturity = "L1"  # 新创建的模式默认L1
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "<来源文件相对路径>"

[bindings]
rules = []
references = []
skills = []
related_patterns = []
+++

# <模式名称>：<一句话核心说明>

## 模式概述
<用2-3句话说明这个模式解决什么问题、核心机制是什么>

## 问题现象
<描述这个模式解决的具体问题场景和痛点>

## 解决方案
<详细说明核心机制、关键步骤、决策逻辑>
<推荐使用表格对比、Mermaid流程图、代码示例等>

## 适用场景
<列出哪些情况应该使用这个模式>

## 实际案例
<至少1个本项目中的真实应用案例，说明如何应用、效果如何>

## 反模式
<列出1-3个常见的错误做法，说明为什么不对>

## 与其他模式的关系
<列出相关的模式，说明是前置/互补/被细化等关系>

## 边界与选型
<说明这个模式的适用边界，什么情况下不应该用，什么情况下用其他模式>
```

> **为什么需要"反模式"章节？** 只知道"怎么做正确"不足以覆盖边界场景——知道"怎么做错误"能帮助Agent在模糊情况下做出正确判断，避免把模式用在不适用的地方。每个高质量模式（L2及以上）至少应包含1个反模式。

### 6.2 目录分类速查

| 层级 | 目录 | 子主题 |
|------|------|--------|
| 架构层 | architecture-patterns/ | - |
| 代码层 | code-patterns/ | - |
| 方法论层 | methodology-patterns/ | retrospective-knowledge（复盘知识）/ document-architecture（文档架构）/ tools-automation（工具自动化）/ governance-strategy（治理策略）/ ai-collaboration（AI协作）/ creative-design（创意设计）/ product-growth（产品增长） |

> 完整的子主题边界说明见 [CATEGORIES.md](../../../../docs/retrospective/patterns/methodology-patterns/CATEGORIES.md)。


---

## 相关模式

- - [insight-cmd Skill](../../insight-cmd/SKILL.md)
- - [retrospective-cmd Skill](../../retrospective-cmd/SKILL.md)
- - [CMD-LOG日志规范](../../../rules/cmd-log-specification.md)
- - [模式成熟度管理](../../../scripts/pattern-maturity.py)
- - [模式萃取方法论](../../../../docs/retrospective/patterns/README.md)
- - [模式合并边界判断](../../../../docs/retrospective/patterns/methodology-patterns/document-architecture/pattern-merge-boundary.md)

← 上一章: [Skill概述、功能描述与方案选择决策树](01-overview-decision.md) | **[返回索引](../SKILL.md)** | 下一章 → [现有模式更新与模式合并重构方案](03-update-merge.md)
