+++
id = "law-governance-building-five-steps"
date = "2026-06-29"
type = "insight"
scope = "governance-methodology,process,project-execution"
source = "../insight-extraction.md#治理规则体系建设五步法"
archived_to = "docs/retrospective/patterns/methodology-patterns/governance-strategy/five-layer-governance-architecture.md#端到端建设流程五步法"
integration_note = "已整合为five-layer-governance-architecture模式的「端到端建设流程（五步法）」章节，不独立入库"
+++

# 规律5：治理规则体系建设五步法（综合方法论）

→ 正式模式：[five-layer-governance-architecture.md](../../../../../patterns/methodology-patterns/governance-strategy/five-layer-governance-architecture.md)（L2，端到端建设流程章节）

**整合说明**：经审核，本洞察作为"端到端建设流程（五步法）"章节整合进五层架构模式，不独立入库。理由：步骤③风格确认已被convention-driven-creation（L2）覆盖，步骤②架构选择即五层架构本身，作为实施流程章节纳入L2模式可增强落地指导、避免模式库碎片化。

## 核心逻辑摘要

五步法是从零构建治理体系的端到端项目流程：①需求解构 → ②架构设计 → ③风格确认 → ④逐文档编写 → ⑤集成验证，发现问题回溯到②。其中步骤③（风格确认，读取3-5份同类文档）是高杠杆环节（2-3分钟成本避免30分钟返工）。

## 整合映射

| 五步法步骤 | 整合位置 | 关联模式 |
|---|---|---|
| ①需求解构 | 端到端建设流程步骤① | compliance-driven-rule-building（合规场景） |
| ②架构设计 | 端到端建设流程步骤② | five-layer-governance-architecture本身 |
| ③风格确认 | 端到端建设流程步骤③ | convention-driven-creation（L2） |
| ④逐文档编写 | 端到端建设流程步骤④ | 层间构建步骤（自底向上） |
| ⑤集成验证 | 端到端建设流程步骤⑤ | 标准化操作（链接检查/索引同步） |

## 关联洞察

- [law-01-five-layer-governance-architecture.md](law-01-five-layer-governance-architecture.md) — 整合目标模式
- [law-02-compliance-driven-rule-building.md](law-02-compliance-driven-rule-building.md) — 步骤①的合规驱动子方法
- [meta-01-convention-over-configuration-docs.md](meta-01-convention-over-configuration-docs.md) — 步骤③风格确认的元认知
- [finding-02-rules-doc-frontmatter-mismatch.md](finding-02-rules-doc-frontmatter-mismatch.md) — 跳过步骤③导致的问题案例

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
