---
id: "frontmatter-templates-errors"
title: "文档类型模板与常见错误修复"
source: "frontmatter-metadata-standard.md#04-templates-errors"
x-toml-ref: "../../../.meta/toml/.agents/rules/frontmatter-metadata-standard/04-templates-errors.toml"
---
# 文档类型模板与常见错误修复

## 文档类型模板

### 模板 1：索引页/入口页

```yaml
---
id: "<topic>-readme"
x-toml-ref: "<相对路径>.meta/toml/.../<name>.toml"
---
```

对应 TOML：
```toml
title = "<文档标题>"
category = "<分类>"
tags = ["tag1", "tag2"]
date = "YYYY-MM-DD"
version = "1.0"
```

### 模板 2：章节/派生内容页

```yaml
---
id: "<topic>-NN-<section>"
source: "<parent-file>.md#<章节锚点>"
x-toml-ref: "<相对路径>.meta/toml/.../<name>.toml"
---
```

### 模板 3：学习资料页

```yaml
---
source: "<URL或来源文档>"
x-toml-ref: "<相对路径>.meta/toml/.../<name>.toml"
---
```

### 模板 4：规则/规范页

```yaml
---
id: "<rule-name>"
source: "<来源spec或文档>"
x-toml-ref: "../../.meta/toml/.agents/rules/<name>.toml"
---
```

### 模板 5：带内容配置的特殊页（如MCP PoC）

```yaml
---
source: "示例说明文字"
name: "<content-name>"
version: "<content-version>"
description: "<content-description>"
x-toml-ref: "<相对路径>.meta/toml/.../<name>.toml"
---
```


## 常见错误与修复

| 错误类型 | 错误示例 | 修复方式 |
|---------|---------|---------|
| 使用 `+++` TOML frontmatter | `+++\ntitle = "..."\n+++` | 改为 `---` YAML + x-toml-ref 外部 TOML |
| 多行 tags 缩进 | `tags:\n  - "a"\n  - "b"` | tags 移至 TOML，YAML 删除 tags 字段 |
| YAML 中放 category/date | `category: "learning"\ndate: "2026-07-02"` | 这些字段移至 TOML，YAML 中删除 |
| changelog 放在 YAML | `changelog:\n  - "..."` | changelog 是描述性文字，移至 TOML |
| x-toml-ref 路径层级错误 | `../../.meta/...`（深度不够） | 按"深度参考表"计算 `../` 层数 |
| TOML 文件缺失 | x-toml-ref 指向的 .toml 不存在 | 创建对应路径的 TOML 文件 |
| YAML 内联 tags 数组 | `tags: ["a", "b"]` | 简单标签数组可用此写法，但推荐移至 TOML 以保持 YAML 最小化；若 tags 条目多或含中文长标签则必须移至 TOML |
| **source 使用 `docs/` 前缀** | `source: "docs/retrospective/reports/..."` | 改为相对路径，如 `../../retrospective/reports/...`（从当前文件目录出发计算） |
| **source 使用跨项目绝对路径** | `source: "d:/AI/docs/retrospective/..."` | 改为相对路径或标注为外部引用 |
| **source 路径层级不完整** | `source: "retrospective/reports/..."`（缺少 `../../`） | 按"深度参考表"补全 `../` 层数 |


---

## 相关模式

- - [硬编码识别标准](../identification-standards.md)
- - [派生产物溯源脚本](../../scripts/check-source-traceability.py)
- - [半结构化解析复杂度预算](../../../docs/retrospective/patterns/methodology-patterns/tools-automation/semi-structured-parsing-complexity-budget.md)

← 上一章: [TOML 外部元数据规范](03-toml-external.md) | **[返回索引](../frontmatter-metadata-standard.md)** | 下一章 → [验证方式与关联文档](05-validation-related.md)
