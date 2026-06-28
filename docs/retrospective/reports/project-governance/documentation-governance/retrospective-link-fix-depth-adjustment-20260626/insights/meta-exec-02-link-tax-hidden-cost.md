+++
id = "retrospective-link-fix-depth-adjustment-20260626-meta-exec-02"
type = "meta-insight"
date = "2026-06-26"
parent = "retrospective-link-fix-depth-adjustment-20260626-meta-execution"
source = "meta-insights-execution.md#元洞察-2原子化的隐性成本链接税的发现"
maturity = "L1"
tags = ["原子化", "隐性成本", "工具链", "架构决策"]
pattern = "best-practice-hidden-cost"
+++

# 元洞察 2：原子化的隐性成本 — "链接税"的发现

> ✅ 本洞察已归档为全局方法论模式：[best-practice-hidden-cost](../../../../../patterns/methodology-patterns/tools-automation/best-practice-hidden-cost.md)（L1）

原子化拆分并非"百利无一害"，存在被忽略的隐性成本"链接税"：相对路径断链、导航表更新、看板漂移、引用复杂度上升。每深一层平均产生1-3个断链。核心启示：推广最佳实践时必须同时提供吸收隐性成本的工具链，否则实践变成负担。应对策略：工具吸收成本（finalize-atomization）+事前评估（build-ref-index）+事后验证（check-links）。
