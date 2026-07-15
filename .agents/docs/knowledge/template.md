---
id: "template"
title: ""
x-toml-ref: "../../../.meta/toml/docs/knowledge/template.toml"
category: ""
tags: []
date: ""
status: draft
author: ""
summary: ""
---
# [标题]

> **frontmatter 必填字段说明**（缺失将导致 `generate_index.py` 告警并降级）：
>
> | 字段 | 类型 | 说明 | 缺失后果 |
> |------|------|------|---------|
> | `title` | string | 条目标题 | 使用文件名作为标题 |
> | `category` | string | 分类（如 operations/learning/platform/troubleshooting/best-practices/decisions） | 归入 unknown 分类 |
> | `tags` | list | 标签列表（如 `["powershell", "html"]`） | 无标签索引 |
> | `date` | string | 创建或更新日期（YYYY-MM-DD） | 不出现在最近更新列表 |
> | `status` | string | 状态（draft/stable/deprecated） | 默认 draft |
> | `author` | string | 作者 | 无作者信息 |
> | `summary` | string | 一句话摘要 | 无摘要展示 |
>
> 模板示例（复制后替换占位符）：
> ```yaml
> ---
> id: "my-knowledge-entry"
> title: "我的知识条目标题"
> category: "operations"
> tags: ["tag1", "tag2"]
> date: "2026-07-03"
> status: "stable"
> author: "SpecWeave"
> summary: "一句话摘要，用于索引展示"
> ---
> ```

## 背景

[描述知识产生的背景、上下文]

## 问题/场景

[描述具体遇到的问题或场景]

## 解决方案/经验

[描述解决方案、操作步骤、经验总结]

## 参考

- [相关链接或文档]
