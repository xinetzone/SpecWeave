---
type: Report
id: "kc-insight-03-trust-first-metadata"
title: "洞察3：AI原生元数据的核心问题不是'如何表示'而是'如何建立信任'"
source: "../insight-extraction.md#洞察3ai原生元数据的核心问题不是如何表示而是如何建立信任"
date: "2026-08-15"
archived_pattern: "../../../../patterns/architecture-patterns/trust-first-metadata.md"
tags:
  - ai-agent
  - metadata
  - trust
  - provenance
maturity: "L1"
---
# 洞察3：AI原生元数据的核心问题不是"如何表示"而是"如何建立信任"

> ✅ **已萃取为模式**：[trust-first-metadata](../../../../patterns/architecture-patterns/trust-first-metadata.md)（信任优先元数据法）

## 陈述（结论）

OKF v0.2相比v0.1最大的架构变化不是新增字段类型，而是将**信任（trust）、来源（provenance）、生命周期（lifecycle）提升为一等公民**。AI Agent时代，元数据大量由LLM自动生成，"敢不敢用"比"怎么表示"是更紧迫的问题。

## 反常识（挑战默认假设）

- ❌ 默认假设："元数据主要是给人看的，人能判断可信度"
- ✅ 反常识：AI Agent时代，元数据的主要消费者从人变成Agent。Agent不会"判断"只会"使用"——没有内置信任信号的元数据，Agent要么幻觉（盲目信任机器生成内容），要么保守（拒绝使用外部知识）。
- ❌ 默认假设："元数据字段越丰富越好"
- ✅ 反常识：传统元数据格式（JSON Schema、JSON-LD、dbt schema.yml）把90%精力放在内容表示上，信任字段缺失。OKF的启示是：**信任字段比内容字段优先级更高**——内容可以慢慢补，没有信任信号Agent根本不敢用。

## 证据（来源）

OKF v0.2信任模型核心设计：
- `sources`字段要求记录每个来源的可信度信号（author、usage_count、last_modified）
- `generated`+`verified`组合推导Trust Tier：unverified → machine-confirmed → human-reviewed
- `status`+`stale_after`处理知识过期问题
- Attested Computation让机器生成的指标可独立验证

## 行动建议

1. **设计元数据格式时**：优先设计信任字段（来源、验证状态、过期时间），内容字段其次
2. **Agent生成内容标注**：Agent生成的元数据必须明确标注`generated: true`，**禁止Agent自己标记`verified: human-reviewed`**
3. **关键指标可验证**：业务KPI/关键指标必须提供可验证的计算定义（Attested Computation模式），不能只用自然语言描述
4. **知识新鲜度优先**：在Agent检索排序中，`verified`状态和`stale_after`新鲜度应该优先于关键词匹配度

## 关联模式

- **✅ 本洞察已萃取为**：[trust-first-metadata](../../../../patterns/architecture-patterns/trust-first-metadata.md)（信任优先元数据法）
- [可验证知识声明法](../../../../patterns/architecture-patterns/verifiable-knowledge-claim.md)（信任升级路径：machine-confirmed）
- [可信度双轨制](../../../../patterns/methodology-patterns/research-knowledge/credibility-dual-track.md)
