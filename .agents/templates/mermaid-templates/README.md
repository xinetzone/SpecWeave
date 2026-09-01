---
id: "mermaid-templates"
title: "Mermaid 安全编码模板"
source: "AGENTS.md#模板"
x-toml-ref: "../../../.meta/toml/.agents/templates/mermaid-templates/README.toml"
---
# Mermaid 安全编码模板

本目录提供遵循项目 Mermaid 安全编码规范的常用图表模板，内置安全格式，从生产端杜绝渲染问题。

## 模板列表

| 模板文件 | 适用场景 |
|---------|---------|
| **[safe-starter.md](safe-starter.md)** | **⭐ 推荐起步模板**：代码块内用 `%%` 注释内嵌六规则安全提醒，含完整填写指南和陷阱速查 |
| [flowchart-left-right.md](flowchart-left-right.md) | 流程图（左→右布局） |
| [flowchart-top-bottom.md](flowchart-top-bottom.md) | 流程图（上→下布局） |
| [flowchart-with-subgraphs.md](flowchart-with-subgraphs.md) | 分层流程图（含 subgraph 分组） |
| [flowchart-decision.md](flowchart-decision.md) | 决策/判断流程图（含菱形判断节点） |
| [sequence-diagram.md](sequence-diagram.md) | 时序图 |
| [state-diagram.md](state-diagram.md) | 状态图 |
| [mindmap.md](mindmap.md) | 思维导图/径向图 |

## 使用方法

1. **首选 [safe-starter.md](safe-starter.md)**：复制代码块内容，内置的 `%%` 注释会在编辑时提醒安全规则，完成后删除注释段即可
2. 或选择对应布局的专用模板，替换占位符文本（保持双引号包裹格式）
3. 修改节点连接关系
4. 运行 `python .agents/scripts/check-mermaid.py --fix` 自动检测并修复语法问题

## 安全编码六规则速查

### 规则 1：禁止空行
代码块内禁止任何空行（含仅含空格的行）。空行会导致部分渲染器中断解析。

### 规则 2：文本加引号
含中文、特殊字符（`@#:()-`+空格）、英文短语的节点/标签/subgraph标题，一律用双引号包裹：
- `id["中文节点"]` ✅ `id{"判断"}` ✅ `subgraph ID ["标题"]` ✅
- `id[中文节点]` ❌ `id{判断}` ❌
- 纯英文单词/标识符可省略：`A[Start]` ✅

### 规则 2b：避免列表触发
引号不能穿透Markdown层，以下模式即使被引号包裹仍会触发列表解析：
| 禁止 | 正确 |
|------|------|
| `"1. 步骤"` | `"1：步骤"` 或 `"①步骤"` |
| `"- 项目"` | `"-项目"` 或 `"·项目"` |
| `"* 注意"` | `"*注意"` 或 `"⚠ 注意"` |

### 规则 2c：换行用 `<br/>`
节点文本内换行**统一使用 HTML 的 `<br/>` 标签**，禁止使用 `\n` 转义字符：
- `\n` 在 flowchart/stateDiagram 节点中不会被解释为换行
- 统一使用 `<br/>` 可避免记忆不同图表类型的差异
- `A["第一行<br/>第二行"]` ✅ `A["第一行\n第二行"]` ❌

### 规则 3：Subgraph 安全格式
`subgraph EN_ID ["中文标题"]` — ID为纯英文标识符，中文标题放在方括号内双引号中。

### 规则 4：边标签格式
`-->|"标签"|目标` — 含中文/特殊字符的边标签用双引号包裹，标签与箭头之间无空格。

### 规则 5：分层排查
修复时按 语法结构→Subgraph→节点文本→边标签→Style 顺序逐层排查，表层错误修复后暴露深层错误是正常现象。

### 规则 6：完成后检查
写完图后务必运行 `python .agents/scripts/check-mermaid.py --fix` 自动检测修复。

> 完整规则与正反例见 [mermaid-safe-coding-rules.md](../../../docs/retrospective/patterns/code-patterns/mermaid-safe-coding-rules.md)
