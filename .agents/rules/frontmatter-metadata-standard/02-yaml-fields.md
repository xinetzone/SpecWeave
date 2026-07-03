---
id: "frontmatter-yaml-fields"
title: "YAML frontmatter 字段规范"
source: "frontmatter-metadata-standard.md#02-yaml-fields"
x-toml-ref: "../../../.meta/toml/.agents/rules/frontmatter-metadata-standard/02-yaml-fields.toml"
---
# YAML frontmatter 字段规范


### 字段分类

| 字段 | 必填 | 适用场景 | 说明 |
|------|------|---------|------|
| `id` | 是 | 所有文档 | kebab-case 唯一标识符，如 `myst-migration-02-concept-adaptability` |
| `x-toml-ref` | 是 | 所有文档 | 外部 TOML 元数据文件的相对路径 |
| `source` | 条件必填 | 派生产物 | 来源溯源，格式见下文 |
| `title` | 可选 | 所有文档 | 文档标题（通常从 H1 标题推断，可选） |
| 内容配置字段 | 按需 | 特殊文档 | 如 MCP PoC 的 name/version/description，是文档内容的一部分 |

### id 命名规范

- 使用 **kebab-case**（小写字母+数字+连字符）
- 索引页使用简短 ID：`<topic>-readme`、`<topic>-index`、`<topic>-wiki`
- 章节文件使用带序号的 ID：`<topic>-NN-<section-name>`
- 报告文件使用语义 ID：`<topic>-analysis`、`<topic>-retro-YYYYMMDD`

**示例**：
```yaml
id: "executablebooks-myst-guide-readme"        # 索引页
id: "myst-migration-02-concept-adaptability"  # 章节页
id: "frontmatter-metadata-standard"           # 规则文档
```

### source 溯源字段

从其他文档派生出的结构化产物，**必须**携带 `source` 字段建立溯源链路：

- **格式**：`source: "<文件路径>#<章节锚点>"` 或 `source: "<URL>"`
- **多来源**：多个来源用逗号+空格分隔
- **索引页**：非派生的索引/入口页可省略 source 字段

**示例**：
```yaml
source: "report.md#2-核心概念适配性分析"
source: "https://mystmd.org/guide/syntax-overview, https://mystmd.org/guide/directives"
source: "README.md#自我迭代机制"
```

### 内容配置字段

当文档 frontmatter 中包含**内容定义元数据**（而非文档索引元数据）时，这些字段保留在 YAML 中：

- MCP Server PoC 示例：`name`、`version`、`description`
- MyST 文档中的内容级配置
- 文档正文中直接引用的 frontmatter 变量

判断标准：**如果一个字段是文档"内容的一部分"而非"关于文档的元数据"，则保留在 YAML 中。**

### 禁止的 YAML 写法

```yaml
---
# ❌ 禁止：多行缩进数组
tags:
  - "myst"
  - "directives"
  - "roles"

# ❌ 禁止：多行嵌套对象
config:
  enabled: true
  level: 2

# ❌ 禁止：多行 changelog（描述性文字，应放入TOML）
changelog:
  - "2026-07-02 | initial | 初始版本"
  - "2026-07-02 | expanded | 新增分析"

# ❌ 禁止：单独使用 category/date/tags/version 等字段（应放入TOML）
category: "learning"
date: "2026-07-02"
tags: ["myst", "syntax"]
---
```


---

## 相关模式

- - [硬编码识别标准](../identification-standards.md)
- - [派生产物溯源脚本](../../scripts/check-source-traceability.py)
- - [半结构化解析复杂度预算](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/semi-structured-parsing-complexity-budget.md)

← 上一章: [目的、适用范围与基本规则](01-purpose-scope-rules.md) | **[返回索引](../frontmatter-metadata-standard.md)** | 下一章 → [TOML 外部元数据规范](03-toml-external.md)
