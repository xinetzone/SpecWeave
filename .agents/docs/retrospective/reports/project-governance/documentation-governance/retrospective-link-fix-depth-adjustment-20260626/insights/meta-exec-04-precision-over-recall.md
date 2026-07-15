---
id: "retrospective-link-fix-depth-adjustment-20260626-meta-exec-04"
title: "元洞察 4：精确-模糊权衡的设计智慧 — \"宁可不修，不可错修\""
source: "meta-insights-execution.md#元洞察-4精确-模糊权衡的设计智慧宁可不修不可错修"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/meta-exec-04-precision-over-recall.toml"
---
# 元洞察 4：精确-模糊权衡的设计智慧 — "宁可不修，不可错修"

> ✅ 本洞察已归档为全局方法论模式：[precision-over-recall](../../../../../patterns/methodology-patterns/tools-automation/precision-over-recall.md)（L1）

自动修复工具面临精度vs召回率权衡，设计选择是精度优先到极致：策略按精确度排序（精确→模糊）、调整范围±3、必须验证文件存在、失败显式报告。全量1424链接正确状态下dry-run输出零误修改。核心哲学：破坏性工具"做错"比"不做"代价大10倍，零误报是信任基础。与dry-run-first（流程层）和fix-priority-chain（代码层）形成三层安全保障。
