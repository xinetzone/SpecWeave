---
id: "mermaid-insight-five-safe-coding-rules"
title: "洞察：Mermaid 安全编码五规则的发现过程（已归档）"
source: "../insight-extraction.md#二"
x-toml-ref: "../../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/insights/insight-five-safe-coding-rules.toml"
---
# 洞察：Mermaid 安全编码五规则的发现过程（已归档）

→ 正式模式：[mermaid-safe-coding-rules.md](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（L4 标准化，含完整正反例、检查清单、两阶段解析模型）

## 事件发现

五条规则并非一次性发现，而是在三轮修复中逐层暴露（印证[分层错误屏蔽效应](insight-06-layered-verification.md)）：

| 轮次 | 暴露的规则 | 触发条件 |
|------|-----------|---------|
| 第一轮 | 规则1（禁止空行）、规则3（Subgraph格式）、规则4（边标签格式） | 3个图表完全渲染失败，空行是最表层错误 |
| 第二轮 | 规则2b（规避列表触发） | 空行修复后，9.2图表暴露出"Unsupported markdown: list"错误 |
| 认知纠正 | 规则2（引号原则）的边界 | 误用双引号试图阻止Markdown解析，失败后才理解引号仅作用于语法层 |

### 最耗时的发现：双引号不能穿透Markdown层

第一轮修复将 `[1. 启动协议]` 改为 `["1. 启动协议"]`（加双引号），但飞书仍报错。这是本次修复中最耗时的认知纠正——双引号仅保证语法层边界识别，引号内文本仍会被Mermaid内置Markdown渲染器处理。最终方案是将英文句点改为中文冒号（`"1：启动协议"`），从内容层面消除触发模式。此发现催生了正式模式中的[两阶段解析模型](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md#规则-2b避免-markdown-列表触发)。

### 反直觉的空行规则

3个失败图表（3.1时间线、7.1协作模式、9.2方法论）的共同特征是 subgraph 块之间有空行。最初排查时注意力集中在Subgraph语法本身，后来才发现空行是根因——开发者习惯用空行分隔逻辑块提升可读性，但Mermaid作为Markdown内嵌DSL继承了宿主语言"空行即段落结束"的语义。

## 关联洞察

- [insight-06-layered-verification.md](insight-06-layered-verification.md) — 分层排查法与分层错误屏蔽效应
- [insight-07-renderer-tolerance.md](insight-07-renderer-tolerance.md) — 渲染器容错度差异

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
