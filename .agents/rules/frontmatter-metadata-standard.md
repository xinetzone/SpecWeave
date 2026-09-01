---
id: "frontmatter-metadata-standard"
title: "Markdown 文档 Frontmatter 元数据规范"
x-toml-ref: "../../.meta/toml/.agents/rules/frontmatter-metadata-standard.toml"
---
# Markdown 文档 Frontmatter 元数据规范

本规范定义 Markdown 文档 YAML frontmatter 与 TOML 外部元数据的字段标准、文档类型模板、常见错误修复与验证方式，支撑派生产物溯源。

## 文档导航

| 章节 | 说明 |
|------|------|
| [目的、适用范围与基本规则](frontmatter-metadata-standard/01-purpose-scope-rules.md) | 规范目的、适用范围边界、YAML格式、扁平结构、必填字段、x-toml-ref外部化等基本规则 |
| [YAML frontmatter 字段规范](frontmatter-metadata-standard/02-yaml-fields.md) | id/title/source/x-toml-ref等核心字段定义、必填/可选字段清单、字段格式约定 |
| [TOML 外部元数据规范](frontmatter-metadata-standard/03-toml-external.md) | x-toml-ref引用机制、.meta/toml目录结构、TOML文件字段定义、路径计算规则 |
| [文档类型模板与常见错误修复](frontmatter-metadata-standard/04-templates-errors.md) | 各类文档模板、常见错误（缩进/数组/换行/重复字段等）及修复示例 |
| [验证方式与关联文档](frontmatter-metadata-standard/05-validation-related.md) | check-source-traceability.py验证脚本、CI集成、关联文档引用 |
