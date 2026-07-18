---
id: "law-spec-driven-planning"
title: "规律3：Spec 驱动重构的\"规划收益\""
source: "../insight-extraction.md#规律-3spec-驱动重构的规划收益"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/tools-and-automation/retrospective-scripts-shared-lib-extraction-20260626/insights/law-03-spec-driven-planning.toml"
---
# 规律3：Spec 驱动重构的"规划收益"

## 观察

本次重构通过 spec.md/tasks.md/checklist.md 三件套规划 10 项任务和 29 项检查点，全部按计划完成。

## 规律

对于涉及 **10+ 文件**的重构任务，Spec 驱动（先规划后执行）相比直接重构有显著收益：

| 维度 | 直接重构 | Spec 驱动重构 |
|------|---------|-------------|
| 遗漏风险 | 高（凭记忆） | 低（检查点兜底） |
| 验证完整性 | 主观判断 | 客观勾选 |
| 可追溯性 | 无 | spec 文档可归档 |
| 并行协作 | 难（分工不清晰） | 易（任务明确） |

规划成本（1个Agent约10分钟）远低于返工成本（遗漏修复、冲突解决、重复审计）。

## 适用边界

- 文件数 < 5：直接重构即可，规划开销大于收益
- 文件数 5-10：建议使用简单TODO列表
- 文件数 ≥ 10：Spec三件套必选

## 关联洞察

- [meta-02-audit-scale-economy.md](meta-02-audit-scale-economy.md) — 审计先行与规划收益是同一规模效应的体现

---
*来源：[脚本共享库提取复盘](../README.md)*
