---
id: "retrospective-link-fix-depth-adjustment-20260626-insight-01"
title: "发现 1：目录重构后的相对路径断链是可预测的系统性问题"
source: "insight-extraction.md#发现-1目录重构后的相对路径断链是可预测的系统性问题"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-link-fix-depth-adjustment-20260626/insights/insight-01-predictable-link-breakage.toml"
---
# 发现 1：目录重构后的相对路径断链是可预测的系统性问题

> ✅ 本洞察的算法实现已归档为全局代码模式：[relative-depth-adjustment](../../../../../patterns/code-patterns/relative-depth-adjustment.md)（L2）

**事实支撑**：本次发现的 14 个断链中，71%（10 个）是原子化拆分导致的相对路径 `../` 层数不足，错误模式高度一致。规律：文件从深度D移动到D+ΔD，所有引用的相对路径中`../`数量需要+ΔD。

---

> **关联模块**：
> - [insight-02-path-suffix-invariance.md](insight-02-path-suffix-invariance.md)
> - [insight-07-tool-composition-effect.md](insight-07-tool-composition-effect.md)
> - *来源：[insight-extraction.md](../insight-extraction.md#一关键发现)*
