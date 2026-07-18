---
id: "retrospective-link-fix-depth-adjustment-20260626-insight-07"
title: "发现 7：工具组合效应大于单个工具之和"
source: "insight-extraction.md#发现-7工具组合效应大于单个工具之和"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/insight-07-tool-composition-effect.toml"
---
# 发现 7：工具组合效应大于单个工具之和

> ✅ 本洞察已归档为全局方法论模式：[tool-workflow-composition](../../../../../patterns/methodology-patterns/tools-automation/tool-workflow-composition.md)（L1）

四个工具形成协作链：build-ref-index（事前评估影响面）→ 执行操作 → finalize-atomization（事后自动收尾）→ check-links（验证零断链）→ CI门禁（提交守门）。单个工具解决单点问题，工具组合形成工作流闭环，价值大于单个工具之和。设计工具时应考虑它在工作流中的位置以及与上下游的协作关系。
