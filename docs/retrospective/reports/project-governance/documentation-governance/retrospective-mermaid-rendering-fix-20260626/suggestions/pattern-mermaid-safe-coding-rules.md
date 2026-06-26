+++
id = "pattern-mermaid-safe-coding-rules"
date = "2026-06-26"
type = "pattern-candidate"
maturity = "L1"
scope = "mermaid"
source = "../export-suggestions.md#3.1"
+++

# 模式候选：Mermaid 安全编码五规则

## 模式概述

在 Markdown 文档中使用 Mermaid 图表时，遵循五条安全编码规则可系统性避免 95% 以上的渲染失败问题。该模式从一次大规模渲染故障修复中萃取，覆盖空行、文本引号、列表触发、Subgraph 格式、边标签等核心陷阱。

## 成熟度

**L1（首次发现，需更多验证）** - 已在 SpecWeave 项目 653 个 Markdown 文件上验证有效，但需在 GitHub、飞书、VS Code 等多渲染器环境中进一步测试。

## 核心规则

### 规则 1：禁止空行

Mermaid 代码块（```mermaid ... ```）内部**禁止使用任何空行**。空行会被部分渲染器解析为代码块结束，导致后续内容渲染失败。

**错误示例：**
```
flowchart LR
    A --> B

    B --> C
```

**正确示例：**
```
flowchart LR
    A --> B
    B --> C
```

### 规则 2：文本引号原则

包含以下情况的节点标签、边标签、subgraph 标题，一律用双引号 `"..."` 包裹：

- 含中文字符
- 含特殊字符（`:`、`.`、`(`、`)`、`-`、空格等）
- 含英文短语（超过一个单词）

**正确示例：**
```
A["中文节点"] --> B{"判断节点"}
A -->|"带标签的边"| C
subgraph S1 ["子图标题"]
```

### 规则 3：避免 Markdown 列表触发

节点文本中避免使用「数字 + 英文句点 + 空格」格式（如 `1. 步骤`），这会触发部分 Markdown 渲染器的有序列表解析，破坏 Mermaid 语法。

**替代方案：** 使用中文冒号 `1：` 或中文顿号 `、`，或将整个文本用双引号包裹。

### 规则 4：Subgraph 安全格式

Subgraph 必须使用英文 ID + 显式中文标题格式：

```
subgraph EN_ID ["中文标题"]
    ...
end
```

禁止直接使用裸中文作为 subgraph ID（如 `subgraph 感知层`）。

### 规则 5：边标签格式

边标签使用 `-->|"标签"|目标` 格式，标签文本双引号包裹：

```
A -->|"条件成立"| B
A -->|"条件不成立"| C
```

## 验证方法

采用「分层验证法」逐步排查：
1. 第一层：复制到 Mermaid Live Editor 验证基本语法
2. 第二层：在本地 Markdown 预览器中验证
3. 第三层：在目标平台（GitHub/飞书等）中验证
4. 第四层：运行自动化检查脚本 `check-mermaid.py`

## 相关资产

- 检查脚本：`python .agents/scripts/check-mermaid.py`
- 安全模板：[.agents/templates/mermaid-templates/](../../../../../../../.agents/templates/mermaid-templates/)
- 开发规范：[docs/development-standards.md](../../../../../../development-standards.md)

---
*来源：[Mermaid 渲染问题修复复盘](../README.md)*
