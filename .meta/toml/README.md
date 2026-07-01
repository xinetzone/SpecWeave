---
id: "meta-toml-directory"
title: ".meta/toml 外部TOML元数据存储"
---
# .meta/toml 外部TOML元数据存储

本目录存储从原Markdown文件frontmatter中提取的完整TOML元数据。

## 结构

目录结构镜像项目根目录，例如：
- `.agents/global-core-rules.md` → `.meta/toml/.agents/global-core-rules.toml`
- `docs/knowledge/mdi-spec-v1.0.md` → `.meta/toml/docs/knowledge/mdi-spec-v1.0.toml`

## 字段说明

- `id`：文档唯一标识符（必填，同时存在于YAML和TOML中）
- `category`：文档分类
- `source`：派生产物溯源（标注来源文档）
- `title`/`description`：标题和描述
- `tags`：标签数组
- `domain`/`layer`：模式/知识领域归属
- 其他自定义字段...

## 维护规则

- 新增.md文件时，若需要复杂元数据，创建对应的.toml文件并在YAML中添加x-toml-ref
- 修改元数据时优先修改对应.toml文件；仅id/source等核心字段保留在YAML中
- 禁止在.md文件中重新使用+++ TOML格式frontmatter
