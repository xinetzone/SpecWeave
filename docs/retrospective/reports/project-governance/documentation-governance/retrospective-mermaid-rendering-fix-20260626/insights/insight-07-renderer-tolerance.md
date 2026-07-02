---
id: "mermaid-insight-renderer-tolerance"
title: "洞察07：渲染器容错度差异导致\"本地正常、线上失败\"（已归档）"
source: "../insight-extraction.md#一、发现4"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/insights/insight-07-renderer-tolerance.toml"
---
# 洞察07：渲染器容错度差异导致"本地正常、线上失败"（已归档）

→ 正式模式：[mermaid-safe-coding-rules.md 渲染器兼容性说明](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md#渲染器兼容性说明)（平台容错度表格+实践原则）

## 事件发现

本次故障中，4个出错的流程图在本地 VS Code 预览中看似正常，但粘贴到飞书文档后全部渲染失败。GitHub 和 VS Code 的 Mermaid 渲染器对空行、列表触发等问题相对宽容，飞书渲染器则零容忍。"在我机器上能跑"（Works on my machine）问题同样存在于文档渲染领域。

这一发现直接确立了"遵循最严格规范"的实践原则——不依赖任何渲染器的容错能力，编写时就按最严格标准来。

## 关联洞察

- [insight-five-safe-coding-rules.md](insight-five-safe-coding-rules.md) — 五规则合集（最严格渲染器的共同要求）
- [insight-06-layered-verification.md](insight-06-layered-verification.md) — 分层验证法包含目标平台验证步骤

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
