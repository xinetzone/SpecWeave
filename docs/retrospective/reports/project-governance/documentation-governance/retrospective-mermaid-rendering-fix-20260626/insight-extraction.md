+++
id = "insight-extraction"
source = "retrospective-mermaid-rendering-fix-20260626/README.md"
insights_dir = "insights/"
+++

# 洞察萃取：Mermaid 安全编码规则

> 洞察存放在 [insights/](insights/) 目录，正式模式已归档至 [patterns/code-patterns/](../../../../patterns/code-patterns/)。
>
> 📖 [mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（L4 标准化）

## 核心洞察

| 洞察 | 文件 | 类型 |
|------|------|------|
| Mermaid 安全编码五规则（禁止空行/文本加引号/规避列表/Subgraph格式/边标签格式） | [insights/insight-five-safe-coding-rules.md](insights/insight-five-safe-coding-rules.md) | 规则集合 |
| 修复验证分层法与分层错误屏蔽效应 | [insights/insight-06-layered-verification.md](insights/insight-06-layered-verification.md) | 发现+方法 |
| 渲染器容错度差异导致"本地正常、线上失败" | [insights/insight-07-renderer-tolerance.md](insights/insight-07-renderer-tolerance.md) | 发现 |
| 8 类常见陷阱速查表 | [insights/trap-cheatsheet.md](insights/trap-cheatsheet.md) | 参考卡片 |

完整索引：[insights/README.md](insights/README.md)

## 与现有模式的关系

本次洞察补充了 [mermaid-layered-visualization.md](../../../../patterns/methodology-patterns/mermaid-layered-visualization.md) 中未覆盖的语法安全层规则（该模式侧重图表结构设计），两者互补。分层错误屏蔽概念已补充至 [root-cause-diagnosis.md](../../../../patterns/methodology-patterns/root-cause-diagnosis.md)（第七章）。

---
*所属报告：[Mermaid 渲染问题修复复盘](README.md)*
