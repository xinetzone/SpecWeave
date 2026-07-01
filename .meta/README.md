---
id: "meta-directory"
title: ".meta 目录说明"
---
# .meta 目录说明

本目录存储项目的元数据文件和迁移产物。

## 目录结构

- `toml/` — 外部TOML元数据存储目录（纳入Git版本控制）
  - 镜像项目源文件目录结构
  - 每个文件对应源.md文件的完整元数据
  - 通过YAML frontmatter中的`x-toml-ref`字段引用
- `backup/` — 迁移前原始文件备份（不纳入Git版本控制，仅用于回滚）

## x-toml-ref 使用规范

每个Markdown文件的YAML frontmatter通过`x-toml-ref`字段引用对应的外部TOML文件：

```yaml
---
id: "document-id"
x-toml-ref: "../.meta/toml/path/to/file.toml"
---
```

路径规则：
- 相对于当前.md文件所在目录
- 从.md所在目录到.meta/toml/的相对路径
- YAML字段优先于TOML同名字段

## 迁移记录

2026-07-01：完成833个文件从TOML frontmatter(+++)到YAML frontmatter(---)+x-toml-ref的迁移。
