---
id: "retrospective-mermaid-rendering-fix-20260626"
title: "Mermaid 渲染兼容性问题修复复盘"
x-toml-ref: "../../../../../../../.meta/toml/docs/retrospective/reports/project-governance/documentation-governance/retrospective-mermaid-rendering-fix-20260626/README.toml"
---
# Mermaid 渲染兼容性问题修复复盘

> **报告类型**：故障修复复盘（Incident Retrospective）
> **复盘日期**：2026-06-26
> **问题范围**：`docs/retrospective/reports/project-governance/retrospective-specweave-full-project-comprehensive-20260626/report.md`
> **触发方式**：用户截图报告渲染失败

## 问题概述

项目全面复盘报告 [report.md](../../comprehensive-reviews/retrospective-specweave-full-project-comprehensive-20260626/report.md) 中存在 **4 处 Mermaid 流程图渲染失败**，分两轮修复：

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

编写 Mermaid 图表时记住以下五条规则，可避免 95% 以上的渲染失败。**完整规范、正反例、质量检查清单已归档为正式模式：**

- 📖 **[mermaid-safe-coding-rules.md](../../../../patterns/code-patterns/mermaid-safe-coding-rules.md)** — 五规则完整文档（L4 标准化）
- 🪤 **[mermaid-trap-cheatsheet.md](../../../../patterns/code-patterns/mermaid-trap-cheatsheet.md)** — 8 类陷阱速查表
- 🧪 **自动化检查**：`python .agents/scripts/check-mermaid.py`
- 📋 **安全模板**：[.agents/templates/mermaid-templates/](../../../../../../templates/mermaid-templates/README.md)（5种常用图表模板）

### 规则速记（一句话版）

| # | 规则 | 核心要点 |
|---|------|---------|
| 1 | 禁止空行 | 代码块内不使用任何空行（空行是语法元素，不是排版留白） |
| 2 | 文本加引号 | 中文/特殊字符/空格短语一律双引号 `"..."` 包裹 |
| 2b | 规避列表触发 | 不用「数字.空格」「- 空格」模式，改用「1：」「①」 |
| 3 | Subgraph 格式 | 用 `subgraph EN_ID ["中文标题"]`，ID 必须为纯英文 |
| 4 | 边标签格式 | 用 `-->|"标签"|目标`，中文/特殊字符标签加引号 |
| 5 | 分层排查 | 按「结构→Subgraph→文本→标签→Style」顺序逐层验证 |

### 本报告洞察文件

- [insight-five-safe-coding-rules 五规则合集](insights/insight-five-safe-coding-rules.md)
- [insight-06 分层排查验证法](insights/insight-06-layered-verification.md)
- [insight-07 渲染器容错度差异](insights/insight-07-renderer-tolerance.md)

---

## 目录结构

```
retrospective-mermaid-rendering-fix-20260626/
├── README.md                    # 本文件（问题概述 + 规则速记）
├── execution-retrospective.md   # 执行复盘（时间线、根因分析）
├── insight-extraction.md        # 洞察索引
├── export-suggestions.md        # 改进建议与执行结果
├── insights/                    # 洞察文件（4个：3个洞察 + 1个索引）
└── suggestions/                 # 建议文件（5个：2个归档记录 + 更新记录 + 未来优化 + 索引）
```
