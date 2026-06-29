+++
id = "finding-multi-doc-single-task-granularity"
date = "2026-06-29"
type = "insight"
scope = "anti-pattern,task-planning,granularity,delivery"
source = "../insight-extraction.md#反模式2多文档合并为单任务"
archived_to = "已落地修正：Task拆分遵循一个交付物=一个Task"
+++

# 发现3（反模式2）：多文档合并为单任务

→ 已落地修正：任务拆分遵循"一个交付物=一个Task"原则

## 表现

初期将多个独立文档合并为一个任务组：
- 将出境评估+脱敏+加密合并为一个Task
- 将供应商准入+审计合并为一个Task

导致单任务验收标准过于复杂，无法独立追踪进度和验证。

## 根因分析

1. **按逻辑层次划分任务而非按交付物划分**：五层架构的"层"成为任务划分依据，但一个层内可能有多个独立文档
2. **任务分解时追求"任务数量少"**：错误认为任务少=效率高，实际上任务过大导致无法管理
3. **低估了每个文档的独立复杂度**：每个规则文档都有Mermaid图、矩阵表、checklist，不是简单的段落

## 错误的任务划分示例

| 错误划分 | 正确拆分 |
|---------|---------|
| Task: 技术防护层文档（含脱敏+加密+出境评估） | Task 1: 数据脱敏规范<br/>Task 2: 数据加密规范<br/>Task 3: 数据出境评估流程 |
| Task: 供应商管理文档（含准入+审计） | Task 1: 供应商准入规范<br/>Task 2: 供应商持续审计规范 |

## 改进方向

任务分解遵循**"一个交付物=一个Task"原则**：
- 每个独立的文档/脚本/配置文件对应一个Task
- 每个Task有独立的验收标准和测试要求
- 经验法则：如果一个Task的验收标准超过5条，考虑拆分
- 按交付物划分而非按逻辑层次划分——同一层的多个文档应该是多个Task

## 关联洞察

- [law-01-five-layer-governance-architecture.md](law-01-five-layer-governance-architecture.md) — 五层架构是文档组织方式，不是任务划分方式
- [law-04-vendor-lifecycle-governance.md](law-04-vendor-lifecycle-governance.md) — 准入和审计是两个独立交付物
- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 步骤④逐文档编写，一个文档=一个Task

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
