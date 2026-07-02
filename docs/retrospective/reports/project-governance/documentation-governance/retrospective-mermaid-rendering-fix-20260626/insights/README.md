---
id: "mermaid-retro-insights-index"
title: "Mermaid 渲染兼容性修复洞察索引"
source: "../insight-extraction.md"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/insights/README.toml"
---
# Mermaid 渲染兼容性修复洞察索引

> 本目录存放从 Mermaid 渲染问题修复复盘中萃取的核心洞察。所有通用规范已归档至正式模式库，本目录文件仅保留事件发现叙事。
>
> 📖 **正式模式**：
> - 五规则+五层排查+兼容性表：[mermaid-safe-coding-rules.md](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（L4 标准化）
> - 陷阱速查表：[mermaid-trap-cheatsheet.md](../../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)（L4 标准化）
> - 分层屏蔽元概念：[root-cause-diagnosis.md](../../../../../patterns/methodology-patterns/governance-strategy/root-cause-diagnosis.md)（L2）

## 洞察清单（事件叙事）

| 文件 | 核心事件 | 归档至 |
|------|---------|--------|
| [insight-five-safe-coding-rules.md](insight-five-safe-coding-rules.md) | 五规则如何在三轮修复中逐层暴露 | mermaid-safe-coding-rules 规则1-4 |
| [insight-06-layered-verification.md](insight-06-layered-verification.md) | 分层屏蔽效应如何催生五层排查法 | mermaid-safe-coding-rules 规则5 + root-cause-diagnosis 第七章 |
| [insight-07-renderer-tolerance.md](insight-07-renderer-tolerance.md) | 飞书零容忍 vs 本地宽容的故障发现 | mermaid-safe-coding-rules 渲染器兼容性说明 |

---
*数据来源：[Mermaid 渲染问题修复复盘](../README.md)*
