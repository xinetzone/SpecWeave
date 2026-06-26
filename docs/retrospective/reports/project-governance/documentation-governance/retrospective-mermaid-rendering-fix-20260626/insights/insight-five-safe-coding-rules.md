+++
id = "mermaid-insight-five-safe-coding-rules"
date = "2026-06-26"
type = "insight"
scope = "mermaid"
source = "../insight-extraction.md#二"
merged_from = ["insight-01-no-blank-lines", "insight-02-quote-principle", "insight-03-markdown-list-avoidance", "insight-04-subgraph-format", "insight-05-edge-label-format"]
archived_to = "docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md"
+++

# 洞察：Mermaid 安全编码五规则的发现过程

> 📖 **正式规范文档（含完整正反例与检查清单）**：[mermaid-safe-coding-rules.md](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（L4 标准化模式）
> 🪤 **陷阱速查表**：[mermaid-trap-cheatsheet.md](../../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)（L4 标准化模式）
>
> 本文件记录五条规则在本次故障修复中的**发现过程与事件特有事实**，通用编码规范请查阅正式模式文档。

## 发现时间线

本次故障中，五条规则并非一次性发现，而是在三轮修复中逐层暴露——这本身印证了[分层错误屏蔽效应](insight-06-layered-verification.md)：

| 轮次 | 暴露的规则 | 触发条件 |
|------|-----------|---------|
| 第一轮修复 | 规则1（禁止空行）、规则3（Subgraph格式）、规则4（边标签格式） | 3个图表完全渲染失败，空行是最表层错误 |
| 第二轮修复 | 规则2b（规避列表触发） | 空行修复后，9.2图表暴露出"Unsupported markdown: list"错误 |
| 错误认知纠正 | 规则2（引号原则）的边界 | 第二轮误用双引号试图阻止Markdown解析，失败后才理解引号仅作用于语法层 |

## 关键发现细节

### 规则1 的发现：空行是语法元素

3个图表（3.1时间线、7.1协作模式、9.2方法论）均因空行导致渲染完全失败。最初排查时注意力集中在Subgraph语法本身，后来发现所有失败图表的共同特征是 subgraph 块之间有空行。**反直觉之处**：开发者习惯用空行分隔逻辑块提升可读性，但Mermaid解析器采用"空行即图表结束"设计，与Markdown段落分隔规则一致。

### 规则2b 的发现：双引号不能穿透Markdown层

这是本次修复中最耗时的发现。第一轮修复将 `[1. 启动协议]` 改为 `["1. 启动协议"]`（加双引号），但飞书仍报错"Unsupported markdown: list"。

**关键认知纠正**：双引号仅保证Mermaid语法层解析正确（帮助识别文本边界），引号内文本仍会经过Mermaid内置Markdown渲染器处理，`1. ` 模式仍被识别为有序列表。Mermaid文本解析分两阶段独立运作：
1. **语法解析阶段**：引号帮助识别节点/标签边界
2. **Markdown渲染阶段**：引号无穿透效果，内部文本照常解析

最终解决方案：将英文句点 `.` 改为中文冒号 `：`（`"1：启动协议"`），从内容层面消除触发模式，而非依赖引号阻止解析。

### 规则2/3/4 的确认

边标签中 `@role` 和中文文本无引号导致解析异常、Subgraph中文裸ID导致连线失效、边与style间空行导致style被忽略——这些问题在第一轮空行修复后一并暴露，修复方案较直接。

## 关键教训

1. **分层暴露是正常现象**：修复一个错误后新错误出现，不是"越修越错"，而是深层错误被表层错误屏蔽
2. **不要假设引号的能力边界**：双引号解决语法层问题，不解决内容层的Markdown解析
3. **遵循最严规范**：在宽容渲染器（VS Code预览）中正常的代码，在严格渲染器（飞书）中可能失败（详见[insight-07](insight-07-renderer-tolerance.md)）

## 关联洞察

- [insight-06-layered-verification.md](insight-06-layered-verification.md) — 分层验证法与分层错误屏蔽效应
- [insight-07-renderer-tolerance.md](insight-07-renderer-tolerance.md) — 渲染器容错度差异

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
