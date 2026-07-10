---
id: "mermaid-trap-cheatsheet"
source: "external: 不存在-docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/insights/trap-cheatsheet.md"
x-toml-ref: "../../../../.meta/toml/docs/retrospective/patterns/code-patterns/mermaid-trap-cheatsheet.toml"
---
# Mermaid 常见陷阱速查表

## 模式概述

Mermaid 语法在不同 Markdown 渲染器中存在兼容性陷阱，速查表模式将高频陷阱整理为可快速查阅的卡片形式，供编写时即时参考，避免重复踩坑。配合 [mermaid-safe-coding-rules.md](mermaid-safe-coding-rules.md) 五规则使用效果最佳。

## 成熟度

**L4（标准化）** - 与安全编码五规则同步验证，已通过 check-mermaid.py 自动化检测覆盖。

## 陷阱速查表

| # | 陷阱 | 错误示例 | 正确写法 | 错误现象 |
|---|------|---------|---------|---------|
| 1 | Subgraph 间空行 | `end\n\nsubgraph` | `end\nsubgraph` | 渲染失败，后续内容丢失 |
| 2 | 节点文本"数字.空格"触发列表 | `A[1. 启动]` 或 `A["1. 启动"]` | `A["1：启动"]`（中文冒号） | "Unsupported markdown: list" |
| 3 | 边标签含 @ 未加引号 | `-->|@role|` | `-->|"@role"|` | 语法解析错误 |
| 4 | 中文 Subgraph 裸 ID | `subgraph 感知层` | `subgraph S1 ["感知层"]` | Subgraph 无法渲染/连线失效 |
| 5 | Style 前有空行 | `--> E\n\nstyle A` | `--> E\nstyle A` | Style 被忽略或解析失败 |
| 6 | 边标签含中文无引号 | `-->|数据|` | `-->|"数据"|` | 部分渲染器解析失败 |
| 7 | 全角冒号在 ID 中 | `subgraph 角色：架构师` | `subgraph ARCH ["角色：架构师"]` | Subgraph 渲染失败 |
| 8 | Mermaid 代码块内任意空行 | 任意空行 | 不使用空行 | 解析器误判图表结束 |
| 9 | flowchart/stateDiagram 节点内用 `\n` 换行 | `A["第一行\n第二行"]` | `A["第一行<br/>第二行"]` | 换行符显示为字面文本或不换行 |

> ⚠️ **陷阱9注意**：`\n` 在 sequenceDiagram 中可正常换行（Note over 和消息文本），仅 flowchart/stateDiagram 节点需用 `<br/>`。

## 快速排查流程

遇到渲染问题时，按以下顺序检查：

1. 代码块内有无空行？→ 删除所有空行
2. Subgraph ID 是否为纯英文？→ 改为 `ID ["标题"]` 格式
3. 节点文本是否含「数字.空格」「- 空格」「* 空格」？→ 改用中文冒号或去除空格
4. 节点内换行是否用了 `\n` 而非 `<br/>`？→ flowchart/stateDiagram 统一用 `<br/>`
5. 边标签含中文/特殊字符是否加引号？→ 使用 `-->|"标签"|`
6. Style 语句前是否有空行？→ 删除空行
7. 运行自动化检查：`python .agents/scripts/check-mermaid.py`

## 五规则速查

| 规则 | 一句话总结 |
|------|-----------|
| 规则1 | 代码块内禁止空行 |
| 规则2 | 非纯英文文本双引号包裹 |
| 规则2b | 避免「数字.空格」「- 空格」等列表触发模式 |
| 规则2c | flowchart/stateDiagram 节点换行用 `<br/>` 不用 `\n` |
| 规则3 | Subgraph 用 `ID ["标题"]` 格式 |
| 规则4 | 边标签用 `-->|"标签"|` 格式 |
| 规则5 | 按「结构→Subgraph→文本→标签→Style」五层排查 |

详细规则说明见 [mermaid-safe-coding-rules.md](mermaid-safe-coding-rules.md)。

## 相关资产

- **五规则详细说明**：[mermaid-safe-coding-rules.md](mermaid-safe-coding-rules.md)
- **分层可视化模式**：[mermaid-layered-visualization.md](../methodology-patterns/document-architecture/mermaid-layered-visualization.md)
- **安全模板**：`.agents/templates/mermaid-templates/`
- **自动化检查**：`python .agents/scripts/check-mermaid.py`

> 来源：Mermaid 渲染兼容性问题修复复盘（retrospective-mermaid-rendering-fix-20260626），Mermaid 渲染回归治理失效复盘（retrospective-mermaid-rendering-regression-20260629）补充陷阱9和规则2c。
