---
id: "firecrawl-action-1-triangular-verification"
title: "行动1：将三角验证法纳入洞察指令集标准流程"
source: "insight-extraction.md#洞察8"
x-toml-ref: "../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/retrospective-firecrawl-learning-20260629/actions/action-1-triangular-verification.toml"
---
# 行动1：将三角验证法纳入洞察指令集标准流程

**优先级**：🔴 高
**预计工作量**：小（修改现有指令集文档）

## 目标

让后续所有外部研究/竞品分析任务自动采用三源验证法。

## 落地步骤

1. 在 [.agents/commands/insight.md](../../../../../../.agents/commands/insight.md) 的"数据采集"步骤中增加三源验证要求
2. 明确规定：研究外部产品时必须覆盖技术源、商业源、第三方源三类信息
3. 在洞察报告模板中增加"信息源覆盖度自检表"

## 验收标准

后续执行外部产品研究时，AI 自动按三源（技术源+商业源+第三方源）采集信息，关键数据点至少2个源确认。

## 关联模式

- [洞察8：三源信息三角验证法](../insights/insight-8-triangular-verification.md)
- [📘 SOP文档：三源信息三角验证法](../../../../patterns/methodology-patterns/retrospective-knowledge/triangular-source-verification.md)（标准操作流程六步法，含自检表模板）

> **SOP沉淀状态**：✅ 已沉淀为可复用模式文档（L2成熟度，2次实践验证）
