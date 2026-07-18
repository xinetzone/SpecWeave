---
id: "law-compliance-driven-rule-building"
title: "规律2：合规驱动规则建设五步法"
source: "../insight-extraction.md#洞察2合规驱动的规则建设方法论"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/process-and-compliance/retrospective-ai-agent-data-security-governance-20260629/insights/law-02-compliance-driven-rule-building.toml"
---
# 规律2：合规驱动规则建设五步法

→ 正式模式：[compliance-driven-rule-building.md](../../../../../patterns/methodology-patterns/governance-strategy/compliance-driven-rule-building.md)（已入库L1）

## 事件事实

本次建设以国家AI智能体互联国标为起点，从法规条文出发推导规则体系，而非从零设计。具体路径：国标要求→场景映射→规则编写→检查清单→门禁集成。

## 对比分析

对比"竞品锚定"（阶段守卫借鉴SpecForge）和"经验驱动"（硬编码治理从实践中总结），合规驱动有其独特优势：

- **有明确的外部基线**：法规条文是"必须满足"而非"可以借鉴"，减少了设计上的摇摆
- **有审计视角**：每一条规则都能追溯到法规条款，合规审计时有据可查
- **有完整框架**：法规通常覆盖全生命周期（分类→保护→监测→处置→问责），避免遗漏关键环节
- **有时效约束**：法规有实施日期，形成天然的项目deadline

## 合规驱动五步法

1. **法规解构**：提取法规中的强制性要求和推荐性要求
2. **场景映射**：将法规要求映射到本系统的具体场景（如"数据出境"映射到"调用GPT/Claude API"）
3. **规则编写**：将法规语言转化为可执行的操作规则和技术规范
4. **检查清单**：为每条规则设计可验证的检查项（checklist格式）
5. **门禁集成**：将检查项嵌入开发流程守卫点，实现自动化/半自动化合规门禁

## 适用边界

- 适用于有明确法规/标准/合规要求的治理领域
- 不适用于纯内部规范、技术最佳实践等无外部强制要求的场景（这些场景更适合经验驱动或竞品锚定）
- 与law-05治理建设五步法互补：合规驱动是从法规到规则的路径，建设五步法是从零构建治理体系的完整项目流程

## 关联洞察

- [law-05-governance-building-five-steps.md](law-05-governance-building-five-steps.md) — 完整治理体系建设流程
- [finding-01-ai-data-security-three-specifics.md](finding-01-ai-data-security-three-specifics.md) — AI场景特殊性影响场景映射步骤

---
*来源：[AI智能体数据安全治理复盘](../README.md)*
