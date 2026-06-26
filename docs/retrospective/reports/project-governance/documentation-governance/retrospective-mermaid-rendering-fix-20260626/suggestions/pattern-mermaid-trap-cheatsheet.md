+++
id = "pattern-mermaid-trap-cheatsheet"
date = "2026-06-26"
type = "pattern-candidate"
maturity = "L1"
scope = "mermaid"
source = "../export-suggestions.md#3.1"
+++

# 模式候选：Mermaid 常见陷阱速查表

## 模式概述

Mermaid 语法在不同 Markdown 渲染器中存在兼容性陷阱，速查表模式将高频陷阱整理为可快速查阅的卡片形式，供编写时即时参考，避免重复踩坑。

## 成熟度

**L1（首次发现，需更多验证）** - 陷阱清单基于本次修复过程中遇到的问题整理，可能尚未覆盖所有边缘情况。

## 陷阱速查表

| 陷阱类型 | 触发条件 | 现象 | 修复方式 |
|---------|---------|------|---------|
| 空行截断 | 代码块内出现空行 | 空行后的内容不渲染，或渲染为纯文本 | 删除空行，确保代码块内无空白行 |
| 中文裸 ID | 直接写 `subgraph 感知层` | Subgraph 不渲染或报错 | 使用英文ID+显式标题：`subgraph SENSE ["感知层"]` |
| 未引号文本 | 含中文/特殊字符的节点未加引号 | 节点不显示、语法报错 | 双引号包裹：`A["中文节点"]` |
| 列表触发 | 节点文本含「数字+英文点+空格」如 `1. 步骤` | 触发 Markdown 列表解析，语法错乱 | 使用中文冒号 `1：步骤` 或加引号 |
| 边标签格式错误 | 使用 `-->|标签|` 无引号 | 含中文的标签渲染失败 | 使用 `-->|"标签"|` 格式 |
| 全角冒号 Subgraph | `subgraph 模块：输入` | 解析失败 | ID用英文，标题在方括号内加引号 |
| 嵌套引号冲突 | 文本内含双引号未转义 | 语法截断 | 使用单引号或转义 `\"` |

## 分层排查法（修复验证）

遇到 Mermaid 渲染问题时，按以下四层从易到难排查：

1. **第一层：Live Editor 验证** - 复制到 Mermaid Live Editor，查看是否有基础语法错误
2. **第二层：本地预览验证** - 在 VS Code 等本地 Markdown 预览器中查看
3. **第三层：目标平台验证** - 在实际部署平台（GitHub/GitLab/飞书等）中验证
4. **第四层：自动化检查** - 运行 `python .agents/scripts/check-mermaid.py` 系统性扫描

> **经验法则**：修复一个错误后，新的深层错误才会暴露。不要看到还有错误就认为修复失败，继续逐层排查直到全部通过。

## 相关资产

- 五规则详细说明：[pattern-mermaid-safe-coding-rules.md](pattern-mermaid-safe-coding-rules.md)
- 安全模板：[.agents/templates/mermaid-templates/](../../../../../../../.agents/templates/mermaid-templates/)
- 自动化检查：`python .agents/scripts/check-mermaid.py`

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
