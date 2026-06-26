+++
id = "mermaid-retro-insights-index"
date = "2026-06-26"
type = "index"
scope = "mermaid-rendering-fix-insights"
source = "../insight-extraction.md"
+++

# Mermaid 渲染兼容性修复洞察索引

> 本目录存放从 Mermaid 渲染问题修复复盘中萃取的核心洞察。五规则已合并为单一文件，两条方法论发现独立成文，另附陷阱速查卡。
>
> 📖 **正式模式归档**：五规则完整规范见 [mermaid-safe-coding-rules.md](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（L4 标准化），陷阱速查见 [mermaid-trap-cheatsheet.md](../../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)。
>
> 母文件：[insight-extraction.md](../insight-extraction.md)

## 洞察清单

| 文件 | 核心命题 | 类型 |
|------|---------|------|
| [insight-five-safe-coding-rules.md](insight-five-safe-coding-rules.md) | Mermaid 安全编码五规则（禁止空行/文本加引号/规避列表/Subgraph格式/边标签格式） | 规则集合 |
| [insight-06-layered-verification.md](insight-06-layered-verification.md) | 修复验证分层法——先修结构、后验内容，预期错误层层暴露（分层错误屏蔽效应） | 发现+方法 |
| [insight-07-renderer-tolerance.md](insight-07-renderer-tolerance.md) | 渲染器容错度差异导致"本地正常、线上失败"，应遵循最严规范 | 发现 |
| [trap-cheatsheet.md](trap-cheatsheet.md) | 8 类常见 Mermaid 陷阱速查表 | 参考卡片 |

## 五规则速记

| 规则 | 一句话总结 |
|------|-----------|
| 规则1 | 代码块内禁止空行（空行是语法元素，不是排版留白） |
| 规则2 | 中文/特殊字符/空格文本一律双引号包裹 |
| 规则2b | 不用「数字.空格」「- 空格」，改用「1：」「①」避免列表触发 |
| 规则3 | Subgraph 用 `ID ["标题"]` 格式，ID 必须纯英文 |
| 规则4 | 边标签用 `-->|"标签"|` 格式 |
| 规则5 | 按「结构→Subgraph→文本→标签→Style」五层排查 |

---
*数据来源：[Mermaid 渲染问题修复复盘](../README.md)*
