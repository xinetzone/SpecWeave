---
id: "retrospective-mermaid-rendering-regression-20260629"
title: "Mermaid 渲染回归问题复盘：规范存在但未执行的治理失效"
version: "1.2"
scenario: "B-single-day-medium"
template_upgrade: "2026-07-06（模板v1.2轻量升级）"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-regression-20260629/README.toml"
---
# Mermaid 渲染回归问题复盘：规范存在但未执行的治理失效

> **报告类型**：故障修复复盘（Incident Retrospective）—— 回归问题
> **复盘日期**：2026-06-29
> **问题范围**：3 个文件中共约 70 处 Mermaid 节点换行符错误 + 9 处空行/引号问题
> **触发方式**：用户连续两轮反馈渲染异常（"Unsupported markdown: list" → "\\n 未正确渲染"）
> **前置事件**：3 天前（2026-06-26）刚完成同类问题修复并建立 L4 规范与自动化检查

## 问题概述

在 2026-06-26 的 Mermaid 渲染兼容性修复后，项目已建立：
- **L4 标准化模式**：[mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)（五条安全编码规则）
- **陷阱速查表**：[mermaid-trap-cheatsheet.md](../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)（8类陷阱）
- **自动化检查脚本**：`.agents/scripts/check-mermaid.py`（空行、引号、列表触发检测）
- **安全模板**：`.agents/templates/mermaid-templates/`（5种常用图表骨架）

然而在 2026-06-29 编写新的 Mermaid 图（vendor集成方案决策树、三区域模型架构图、四不原则纵深防御图）时，**同样的渲染错误再次发生**：

| 轮次 | 用户反馈 | 错误类型 | 违反规则 | 问题数 |
|------|---------|---------|---------|-------|
| 第一轮 | "Unsupported markdown: list" | 节点文本以「数字. 空格」开头触发Markdown列表解析 | 规则2b（规避列表触发） | ~5处 |
| 第二轮 | "\\n 没有正确渲染" | flowchart/stateDiagram 节点内使用 `\n` 而非 `<br/>` 换行 | 规则2（文本格式，速查表遗漏项） | ~70处 |
| 检查后发现 | — | Mermaid代码块内空行、participant别名未加引号 | 规则1（禁止空行）、规则4（边标签引号） | 9处 |

**这不是知识缺失问题，而是治理失效问题——规范、工具、模板全部存在，但没有一个在执行环节被触发。**

## 核心发现

### 1. 规范落地的"最后一公里"断裂

L4 级别的规范文件存在于 `docs/retrospective/patterns/` 中，但在编写新 Mermaid 图时没有被查阅：
- 开发者（我自己）凭记忆和直觉编写，而非查阅规范
- 没有强制读取机制触发规范查阅
- 检查脚本存在但未在提交前运行

### 2. 检查工具的覆盖盲区

`check-mermaid.py` 能检测空行、引号、列表触发，但**未覆盖 `\n` 换行符问题**：
- `\n` 在 sequenceDiagram 中合法（有独立渲染逻辑）
- `\n` 在 flowchart/stateDiagram 节点中不被渲染为换行（需用 `<br/>`）
- 脚本对这一上下文敏感的规则未做区分检测

### 3. "先写后修"的被动模式

两次修复都是**用户反馈后才修复**，而非编写时主动预防：
- 第一轮修复 list 问题后，未对全部新增文件运行检查脚本
- 第二轮修复 `\n` 问题时，才首次运行检查脚本，又发现空行/引号问题
- 形成"用户发现bug→修复→遗漏同类问题→用户再发现"的恶性循环

### 4. 模式速查表存在知识盲区

[mermaid-trap-cheatsheet.md](../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md) 列出了8类陷阱，但**未收录 `\n` vs `<br/>` 换行问题**——这是一个明确的知识遗漏。

---

## 目录结构

```
retrospective-mermaid-rendering-regression-20260629/
├── README.md                    # 本文件（问题概述 + 核心发现）
├── execution-retrospective.md   # 执行复盘（时间线、根因分析）
├── insight-extraction.md        # 洞察萃取（治理失效模式）
├── export-suggestions.md        # 改进建议与行动计划
└── insight-action-backlog.md    # 洞察行动项Backlog（v1.2新增）
```
