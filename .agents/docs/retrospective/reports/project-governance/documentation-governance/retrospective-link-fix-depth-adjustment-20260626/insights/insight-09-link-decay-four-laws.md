---
id: "retrospective-link-fix-depth-adjustment-20260626-insight-09"
title: "发现 9：文档系统中的链接衰变四条规律"
source: "insight-extraction.md#三、规律认知"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/insight-09-link-decay-four-laws.toml"
---
# 发现 9：文档系统中的链接衰变四条规律

> ✅ 本洞察已归档为全局方法论模式：[link-decay-laws](../../../../../patterns/methodology-patterns/document-architecture/link-decay-laws.md)（L1）

Markdown文档系统中链接稳定性遵循四条规律：(1)移动越深断链越多，(2)向浅移动影响小（多余../可容忍），(3)跨目录引用最脆弱，(4)同目录引用最稳定。这指导了自动修复算法优先增加深度、原子化收尾工具重点处理跨目录链接、build-ref-index事前评估影响面。
