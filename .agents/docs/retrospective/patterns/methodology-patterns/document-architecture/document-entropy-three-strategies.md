---
id: "document-entropy-three-strategies"
source: "../../../reports/insight-extraction/external-learning/retrospective-zhujian-wudao-specs-analysis-20260625/insights/doc-entropy-three-strategies.md"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/retrospective/patterns/methodology-patterns/document-architecture/document-entropy-three-strategies.toml"
---
# 文档声明熵增三策：移除变量是最优解

## 模式概述

物理规律：任何需要人工同步的副本字段（如文件头部的行数统计、条数声明），与原文之间必然存在"同步摩擦"，过时是熵增的必然结果。竹简悟道实测：7个文件中有6个头部统计声明过时，偏差率-21%至-44%。这不是维护者粗心，而是系统规律。

## 三策对比

| 策略 | 做法 | 成本 | 效果 | 适用场景 |
|------|------|------|------|---------|
| 第一策：勤更新 | 每次编辑后手动同步 | 低（每次+30秒） | 治标，仍会过时 | 极小项目（<5文件）、低频更新 |
| 第二策：自动化 | 提交前脚本自动更新 | 中（写脚本） | 根治 | 有CI/CD、工程化程度高 |
| 第三策：移除变量 | 头部只保留定性信息，或添加免责声明 | 零 | 零维护成本 | **大多数项目（推荐）** |

## 竹简悟道实践（第三策）

在核心文件表中添加免责声明：
> "行数为编辑时实测值，仅供量级参考。每次编辑后行数会自然增长，无需逐次同步。"

## 更激进的零成本方案

可以完全移除头部的行数/条数等统计字段，只保留"洞察N-M"这样的范围信息。统计信息需要时可以通过脚本实时计算，无需静态存储：

```bash
# 需要时实时计算，无需静态存储
wc -l docs/**/*.md
grep -c "^##" insights/*.md
```

## 决策矩阵

| 项目特征 | 推荐策略 |
|---------|---------|
| <5个文件，月更<1次 | 第一策（勤更新） |
| >20个文件，有CI/CD | 第二策（自动化） |
| 其他所有情况 | **第三策（移除变量+免责声明）** |

## 与 synthetic-stats-source-of-truth 的关系

`synthetic-stats-source-of-truth` 讲的是"如果必须维护合成统计，应该从metadata全量重算而非增量推算"（第二策的实现原则）；本模式讲的是"大多数情况下根本不需要维护合成统计，直接移除更优"（第三策）。

两者是互补关系：
- 决策层：用本模式判断"是否需要这个统计字段"
- 实现层：如果判断需要，用synthetic-stats原则实现

## 适用场景

- 所有需要维护文档的项目（极高通用性）
- README中的文件数/行数统计
- 洞察库中的条数声明
- 任何需要人工同步的副本字段

> 来源：竹简悟道头部声明过时现象实测（7个文件6个过时，偏差21-44%）
> 关联模式：`synthetic-stats-source-of-truth`、`three-tier-governance`、`tool-automation-decision-model`
