+++
id = "retrospective-mermaid-rendering-fix-20260626"
type = "incident"
date = "2026-06-26"
scope = "mermaid-rendering-compatibility"
status = "closed"

[files]
execution = "execution-retrospective.md"
insights = "insight-extraction.md"
suggestions = "export-suggestions.md"
insights_dir = "insights/"
suggestions_dir = "suggestions/"
+++

# Mermaid 渲染兼容性问题修复复盘

> **报告类型**：故障修复复盘（Incident Retrospective）
> **复盘日期**：2026-06-26
> **问题范围**：`docs/retrospective/reports/project-governance/retrospective-specweave-full-project-comprehensive-20260626/report.md`
> **触发方式**：用户截图报告渲染失败

## 问题概述

项目全面复盘报告 [report.md](../retrospective-specweave-full-project-comprehensive-20260626/report.md) 中存在 **4 处 Mermaid 流程图渲染失败**，分两轮修复：

| 轮次 | 错误现象 | 根因 | 修复图表数 |
|------|---------|------|-----------|
| 第一轮 | "Mermaid 渲染失败，请检查代码或重试" | subgraph 间空行导致解析中断；边标签特殊字符未加引号 | 3 |
| 第二轮 | "Unsupported markdown: list" | 节点文本以 `数字. ` 开头被误解析为 Markdown 有序列表 | 1 |

## 核心发现

1. **Mermaid 解析器对空行敏感**：`subgraph` 块之间、边定义与 `style` 语句之间的空行会导致解析器误判图表结束
2. **节点文本存在隐式 Markdown 解析**：`[1. 启动协议]` 中的 `1. ` 被识别为有序列表语法，但 Mermaid 节点内不支持列表渲染
3. **特殊字符需引号保护**：边标签中含 `@` 等特殊字符、中文文本时应用双引号包裹
4. **缺乏自动化检测**：现有 CI 检查脚本（ci-check.ps1）未覆盖 Mermaid 语法校验

---

## ⚡ 快速入口：Mermaid 安全编码五规则

编写 Mermaid 图表时记住以下五条规则，可避免 95% 以上的渲染失败：

| # | 规则 | 一句话要点 | 详细 |
|---|------|-----------|------|
| 1 | **禁止空行** | 代码块内不使用任何空行（空行是语法元素） | [insight-01](insights/insight-01-no-blank-lines.md) |
| 2 | **文本加引号** | 中文/特殊字符/空格短语一律双引号包裹 | [insight-02](insights/insight-02-quote-principle.md) |
| 2b | **规避列表触发** | 不用「数字.空格」「- 空格」，改用「1：」「①」 | [insight-03](insights/insight-03-markdown-list-avoidance.md) |
| 3 | **Subgraph 格式** | 用 `subgraph EN_ID ["中文标题"]`，禁止裸中文ID | [insight-04](insights/insight-04-subgraph-format.md) |
| 4 | **边标签格式** | 用 `-->|"标签"|目标`，中文标签加引号 | [insight-05](insights/insight-05-edge-label-format.md) |
| 5 | **分层排查** | 结构→Subgraph→文本→标签→Style，预期错误层层暴露 | [insight-06](insights/insight-06-layered-verification.md) |

### 陷阱速查（最常见3类）

| 错误写法 | 为什么错 | 正确写法 |
|---------|---------|---------|
| 块之间留空行 | 空行截断解析 | 删除所有空行 |
| `A["1. 启动"]` | 引号不能阻止列表解析 | `A["1：启动"]`（中文冒号） |
| `subgraph 感知层` | 中文裸ID无法识别 | `subgraph SENSE ["感知层"]` |

### 工具链

- **自动化检查**：`python .agents/scripts/check-mermaid.py`
- **安全模板**：[.agents/templates/mermaid-templates/](../../../../../.agents/templates/mermaid-templates/README.md)（5种常用图表模板）
- **陷阱速查卡**：[insights/trap-cheatsheet.md](insights/trap-cheatsheet.md)（8类完整陷阱清单）
- **渲染器差异**：[insight-07](insights/insight-07-renderer-tolerance.md)（各平台容错度对比）

---

## 交付物

| 文件 | 内容 |
|------|------|
| [execution-retrospective.md](execution-retrospective.md) | 事实回顾、时间线、根因分析、修复过程 |
| [insight-extraction.md](insight-extraction.md) | 洞察萃取、五规则索引（已原子化至 [insights/](insights/)） |
| [export-suggestions.md](export-suggestions.md) | 改进建议、行动计划（已原子化至 [suggestions/](suggestions/)） |

### 原子化资产索引

| 目录 | 内容 | 文件数 |
|------|------|-------|
| [insights/](insights/) | 7条核心洞察 + 1份陷阱速查卡 + 1个索引 | 9 |
| [suggestions/](suggestions/) | 2个新模式候选 + 现有模式更新建议 + 未来优化方向 + 索引 | 5 |
