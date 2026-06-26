+++
id = "mermaid-retro-insights-index"
date = "2026-06-26"
type = "index"
scope = "mermaid-rendering-fix-insights"
source = "../insight-extraction.md"
+++

# Mermaid 渲染兼容性修复洞察索引

> 本目录存放从 Mermaid 渲染问题修复复盘中萃取的 7 条核心洞察和 1 份陷阱速查表，每条洞察均已拆分为独立原子文件。
> 母文件：[insight-extraction.md](../insight-extraction.md)

## 洞察清单

| 编号 | 文件 | 核心命题 | 类型 |
|------|------|---------|------|
| 01 | [insight-01-no-blank-lines.md](insight-01-no-blank-lines.md) | Mermaid 代码块内禁止空行——空行是语法元素而非排版元素 | 规则 |
| 02 | [insight-02-quote-principle.md](insight-02-quote-principle.md) | 非纯英文单词的节点/边标签一律用双引号包裹 | 规则 |
| 03 | [insight-03-markdown-list-avoidance.md](insight-03-markdown-list-avoidance.md) | 双引号不能阻止 Markdown 解析，须从内容层面避免列表触发模式 | 发现+规则 |
| 04 | [insight-04-subgraph-format.md](insight-04-subgraph-format.md) | Subgraph 统一使用英文 ID + `["中文标题"]` 格式 | 规则 |
| 05 | [insight-05-edge-label-format.md](insight-05-edge-label-format.md) | 边标签使用 `-->|"标签"|` 格式，中文/特殊字符双引号包裹 | 规则 |
| 06 | [insight-06-layered-verification.md](insight-06-layered-verification.md) | 修复验证分层法——先修结构、后验内容，预期错误层层暴露 | 发现+方法 |
| 07 | [insight-07-renderer-tolerance.md](insight-07-renderer-tolerance.md) | 渲染器容错度差异导致"本地正常、线上失败"，应遵循最严规范 | 发现 |
| 参考 | [trap-cheatsheet.md](trap-cheatsheet.md) | 8 类常见 Mermaid 陷阱速查表 | 参考卡片 |

## 五规则速查

| 规则 | 一句话总结 |
|------|-----------|
| 规则1 | 代码块内禁止空行 |
| 规则2 | 非纯英文文本双引号包裹 |
| 规则2b | 避免「数字.空格」「- 空格」等列表触发模式 |
| 规则3 | Subgraph 用 `ID ["标题"]` 格式 |
| 规则4 | 边标签用 `-->|"标签"|` 格式 |
| 规则5 | 按「结构→Subgraph→文本→标签→Style」五层排查 |

---
*数据来源：[Mermaid 渲染问题修复复盘](../README.md)*
