---
id: "frontmatter-validation-related"
title: "验证方式与关联文档"
source: "frontmatter-metadata-standard.md#05-validation-related"
x-toml-ref: "../../../.meta/toml/.agents/rules/frontmatter-metadata-standard/05-validation-related.toml"
---
# 验证方式与关联文档

## 验证方式

提交前运行以下检查确保 frontmatter 合规：

1. **frontmatter 格式检查**：确认所有 `---` 分隔的 frontmatter 只包含允许的字段
2. **x-toml-ref 路径验证**：所有引用的 TOML 文件必须存在
3. **链接有效性检查**：
   ```bash
   python .agents/scripts/check-links.py --path <目标目录>
   ```


## 关联文档

- [开发规范 Frontmatter 章节](../../docs/development-standards.md#frontmatter-格式规范)
- [派生产物溯源约定](../../docs/development-standards.md#派生产物溯源约定)
- [.meta 目录说明](../../../.meta/README.md)
- [submodule-metadata-externalization 模式](../../docs/retrospective/patterns/architecture-patterns/submodule-metadata-externalization.md)


---

## 相关模式

- - [硬编码识别标准](../identification-standards.md)
- - [派生产物溯源脚本](../../scripts/check-source-traceability.py)
- - [半结构化解析复杂度预算](../../docs/retrospective/patterns/methodology-patterns/tools-automation/semi-structured-parsing-complexity-budget.md)

← 上一章: [文档类型模板与常见错误修复](04-templates-errors.md) | **[返回索引](../frontmatter-metadata-standard.md)**
