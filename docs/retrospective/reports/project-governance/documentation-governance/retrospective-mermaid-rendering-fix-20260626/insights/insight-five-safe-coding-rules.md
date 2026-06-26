+++
id = "mermaid-insight-five-safe-coding-rules"
date = "2026-06-26"
type = "insight"
scope = "mermaid"
source = "../insight-extraction.md#二"
merged_from = ["insight-01-no-blank-lines", "insight-02-quote-principle", "insight-03-markdown-list-avoidance", "insight-04-subgraph-format", "insight-05-edge-label-format"]
+++

# 洞察：Mermaid 安全编码五规则

> 📖 **正式规范文档（含完整正反例与检查清单）**：[mermaid-safe-coding-rules.md](../../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（L4 标准化模式）
>
> 本文件记录本次故障修复中萃取的五条核心编码规则，保留事件特有的事实支撑和深层分析。完整编码规范请查阅正式模式文档。

## 背景

本次 Mermaid 渲染故障中，3 个图表因空行导致完全渲染失败，1 个图表因节点文本触发 Markdown 列表解析而显示错误提示框。三条编码规则（空行、引号、Subgraph 格式）在第一轮修复中识别，第四条规则（边标签格式）在空行修复后暴露，第五条规则（列表规避）在第二轮修复错误后才定位真正根因。五条规则共同构成 Mermaid 安全编码的核心防线。

---

## 规则 1：禁止空行

**核心命题**：Mermaid 代码块内的空行是**语法元素**而非排版元素，会被解析器误判为图表结束。

**事实支撑**：本次修复中 3 个图表的渲染失败均由空行导致——Subgraph 块之间的空行、边定义与 `style` 语句之间的空行。空行在人眼看来是"排版留白"，但 Mermaid 解析器采用"空行即结束"设计，与 Markdown 段落分隔规则一致，在代码块场景下反直觉。

**深层含义**：开发者习惯用空行提升代码可读性（分隔逻辑块），但在 Mermaid 中空行具有语法含义。统一禁止空行是最简单可靠的策略。

---

## 规则 2：文本引号原则

**核心命题**：非纯英文单词的节点/边标签一律用双引号 `"..."` 包裹。双引号解决 Mermaid **语法层**的特殊字符解析问题，但不能阻止引号内文本的 Markdown 解析（见规则 2b）。

**必须加引号**：含中文、特殊字符（`@`、`:`、空格等）、复合短语的文本。
**可省略引号**：纯英文标识符（`A[Start]`、`O[orchestrator]`）。

---

## 规则 2b：规避 Markdown 列表触发

**核心命题**：双引号仅保证语法层解析正确，引号内文本仍会经过 Mermaid 内置 Markdown 渲染器。`1. ` 等模式仍会触发有序列表识别，导致 "Unsupported markdown: list" 错误。

**事实支撑**：第一轮修复将 `[1. 启动协议]` 改为 `["1. 启动协议"]`（加双引号），但飞书仍报错。最终方案是将 `1. 启动协议` 改为 `1：启动协议`（中文冒号替代英文句点），从内容层面消除触发模式。

**深层含义**：Mermaid 文本解析分两阶段——语法解析阶段（引号帮助识别边界）和 Markdown 渲染阶段（引号无穿透效果）。两阶段独立运作。

**替代格式**：需编号时使用中文冒号（`1：`）、全角句点（`1．`）或圈号数字（`①`）。

---

## 规则 3：Subgraph 安全格式

**核心命题**：Subgraph 必须使用 `subgraph EN_ID ["中文标题"]` 格式，ID 必须为纯英文标识符，中文标题放在双引号内。

**格式要点**：
- ID 为英文标识符（字母开头，不含中文、全角字符、全角冒号 `：`）
- 中文标题格式为 `["标题文本"]`，ID 与方括号间有空格
- Subgraph 块之间禁止空行

**错误写法**：`subgraph 感知层`（裸中文ID）、`subgraph 角色：架构师`（全角冒号在ID中）。

---

## 规则 4：边标签安全格式

**核心命题**：边标签统一使用 `-->|"标签"|目标` 格式，中文/特殊字符标签双引号包裹，纯英文标识符可省略。

**格式要点**：标签与箭头之间无空格（`-->|"标签"|` 正确，`--> |"标签"|` 错误）。

**错误对照**：
- `-->|数据|B` → `-->|"数据"|B`（中文标签加引号）
- `-->|@role|B` → `-->|"@role"|B`（特殊字符加引号）
- `--> |"标签"| B` → `-->|"标签"|B`（去除多余空格）

---

## 关联洞察

- [insight-06-layered-verification.md](insight-06-layered-verification.md) — 分层验证法（规则5：排查顺序）
- [insight-07-renderer-tolerance.md](insight-07-renderer-tolerance.md) — 渲染器容错度差异
- [trap-cheatsheet.md](trap-cheatsheet.md) — 8 类陷阱速查表

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
