+++
id = "ai-skill-judgment-layer"
domain = "methodology"
layer = "methodology"
maturity = "L2"
validation_count = 1
reuse_count = 0
documentation_level = "basic"
source = "docs/retrospective/reports/competitive-analysis/retrospective-ian-xiaohei-illustrations-learning-20260625/insight-extraction.md#洞察5"
+++

> **来源**：从 Ian Xiaohei Illustrations 核心反思"工具负责生产，判断负责选择"中提炼

# AI Skill 判断层设计模式

## 核心概念

AI 生成内容的能力已经过剩，但"判断力"仍然是稀缺的。好的 AI Skill 的核心价值不在于"用了什么模型"，而在于**把判断力编码进工作流中**——先分析再生成，先理解再表达。

## 三层能力模型

| 层次 | 描述 | 当前 AI 能力 | 价值持续性 |
|------|------|-------------|-----------|
| 生产层 | 生成内容 | 已成熟（DALL-E、Midjourney 等） | 低（快速贬值） |
| 判断层 | 决定在哪里、用什么、怎么用 | 尚不成熟 | 中高 |
| 选择层 | 从多个候选中选择最优 | 需要人类参与 | 高 |

## 判断层的关键能力

| 能力 | 描述 | Ian Xiaohei 的实现 |
|------|------|-------------------|
| 上下文理解 | 理解输入内容的语义结构 | 分析文章，识别认知锚点 |
| 决策制定 | 在特定上下文下做出最优选择 | 决定在哪里配图、配什么样的图 |
| 风格控制 | 确保输出符合预期风格 | 小黑角色系统、手绘线稿风格 |
| 质量评估 | 判断输出是否符合标准 | shot list 供用户选择 |

## 核心价值

"工具负责生产，判断负责选择。"——Ian Xiaohei 的核心反思

AI Skill 的竞争力不应建立在底层模型能力上（这会快速贬值），而应建立在**判断层和风格层**上，这是持续竞争优势的来源。

## 适用场景

- AI Skill 产品化设计
- AI 应用的差异化竞争定位
- 内容生成工具的价值评估
- 任何需要"AI + 判断力"的产品设计

## 设计启示

一个好的 AI Skill 设计应该向上堆叠判断层和风格层，而非仅在能力层竞争。判断层的价值在于：
1. **上下文感知**：理解当前场景的需求
2. **智能决策**：在多个选项中做出最优选择
3. **风格统一**：确保输出符合预期的视觉/内容风格
