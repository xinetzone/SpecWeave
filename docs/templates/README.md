---
id: "docs-templates-index"
title: "文档模板索引"
x-toml-ref: "../../.meta/toml/docs/templates/README.toml"
---
# 文档模板索引

面向人类读者的可复用文档模板集合，位于 `docs/templates/` 目录。
AI智能体专用模板位于 [.agents/templates/](../../.agents/templates/)。

## 模板清单

| 模板 | 文件 | 用途 | 来源 |
|------|------|------|------|
| 文档治理Checklist | [document-governance-checklist.md](document-governance-checklist.md) | 新建文档/原子化拆分/批量迁移时的质量门禁检查（frontmatter合规+工具清单+原则速查） | [frontmatter元数据统一复盘](../retrospective/reports/insight-extraction/retrospective-frontmatter-metadata-unification-20260702/insight-extraction.md) |

## 与 .agents/templates/ 的关系

| 维度 | docs/templates/ | .agents/templates/ |
|------|----------------|-------------------|
| 面向对象 | 人类读者/开发者 | AI智能体 |
| 内容侧重 | 使用说明、操作指引、可直接复制的Checklist | 结构化输出格式、角色提示词模板 |
| 链接风格 | 跨目录完整相对路径 | 同目录短链 |
| 更新频率 | 稳定后更新 | 跟随AI能力迭代频繁更新 |
