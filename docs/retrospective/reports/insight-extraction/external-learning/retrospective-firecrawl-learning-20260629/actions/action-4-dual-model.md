---
id: "firecrawl-action-4-dual-model"
title: "行动4：LLM 调用层增加双模型切换能力"
source: "insight-extraction.md#洞察7"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/insight-extraction/external-learning/retrospective-firecrawl-learning-20260629/actions/action-4-dual-model.toml"
---
# 行动4：LLM 调用层增加双模型切换能力

**优先级**：🟡 中
**预计工作量**：中

## 目标

参考 Firecrawl 的 spark-1-mini/pro 双模型策略，在 LLM 调用层提供成本-质量弹性选择。

## 落地步骤

1. 梳理 SpecWeave 中所有 LLM 调用场景
2. 为每个场景标注"必须高质量"vs"可用快速模型"
3. 实现模型选择参数（类似 `model: "mini" | "pro"`）
4. 默认使用经济模型，关键路径（架构决策、代码审查）使用高质量模型

## 备注

受限于 Trae 平台，可能只能在 prompt 层面引导，无法实际切换模型 API。对应架构评估 P2模块7。

## 关联模式

- [洞察7：Dual-Model Cost-Quality Switch](../../insights/insight-7-dual-model.md)
- [架构优先级评估 P2模块7](../../retrospective-architecture-priority-20260629/README.md#重构模块-7模型路由层洞察7落地)
