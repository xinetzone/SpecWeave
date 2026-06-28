+++
id = "insight-two-tier-structure"
domain = "methodology"
layer = "methodology"
maturity = "L2"
validation_count = 2
reuse_count = 0
documentation_level = "standard"
source = "docs/retrospective/reports/insight-extraction/retrospective-zhujian-wudao-specs-analysis-20260625/insights/insight-two-tier-structure.md"

[bindings]
rules = []
references = ["insight-iceberg-model", "review-insight-export-loop"]
skills = []
+++

# 洞察两档结构：基础档/完整档双轨写作

## 模式概述

解决洞察写作中"写太简单未来看不懂，写太详细当下耗时间"的两难问题。竹简悟道65条洞察验证：仅10.8%的洞察需要完整展开（7条），但这7条承担了60%以上的解释力（帕累托法则）。

## 两档切换标准

| 使用档位 | 判断标准 | 结构 | 典型行数 |
|---------|---------|------|---------|
| 基础档 | 单次设计决策、单点命名、局部架构选择 | 来源 + 核心内容（1-3段） | ~13行 |
| 完整档 | 需要反复使用的操作手册、跨场景复用的方法论、哲学核心概念 | 来源 + 核心内容 + 七节子结构 | ~53行 |

## 七节标准结构（完整档）

```
一、概念定位        —— 它是什么，不是什么
二、哲学/理论根基   —— 从哪来，为什么成立
三、当前实现分析    —— 现在产品里是怎么做的
四、核心机制        —— 怎么运作的，关键步骤
五、边界与约束      —— 什么情况下不适用
六、演进方向        —— 未来可能怎么发展
七、战略位置/协同   —— 与其他概念的关系
```

## 写作决策树

```
是新洞察吗？
  ├─ 是 → 先用基础档快速记录（1-3段）
  │      ↓
  │      这个洞察会被反复引用吗？
  │        ├─ 否 → 保持基础档
  │        └─ 是 → 升级为完整档（七节结构）
  └─ 否 → 判断是否需要补充完善
```

## 适用场景

- 任何洞察驱动的项目（高适用性）
- 设计决策记录系统
- 架构决策记录（ADR）
- 产品原则库建设

## 关键经验

- 不要一开始就追求写完整档——先用基础档快速捕获，避免"写作阻塞"
- 帕累托分布是正常的：10-20%的核心概念承担80%的解释力
- 升级为完整档的时机：发现自己第3次引用同一条洞察时

> 来源：竹简悟道65条洞察的写作实践（基础档58条/完整档7条）
> 关联模式：`insight-iceberg-model`、`review-insight-export-loop`、`insight-library-evolution`
