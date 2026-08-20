---
type: Specification
title: 知识包结构
description: OKF v0.2 知识包的目录树结构、三种分发方式，以及保留文件名（index.md、log.md）。
tags: [okf, spec, structure]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 知识包结构

一个知识包（bundle）是 markdown 文件的目录树。目录结构与领域无关：生产者按对所捕获知识最有意义的方式组织概念。[^okf-spec]

```
path/to/bundle/
  index.md                      # 可选。用于渐进披露的目录列表。
  log.md                        # 可选。按时间顺序的更新历史。
  <concept>.md                  # 位于知识包根目录的概念。
  <subdirectory>/               # 子目录用于把概念组织成组。
    index.md
    <concept>.md
    <subdirectory>/
      ...
```

知识包可以（MAY）以下列方式分发：[^okf-spec]

- 一个 git 仓库（推荐，因为它提供历史、归属与差异）。
- 该目录的 tarball 或 zip 归档。
- 更大仓库中的一个子目录。

## 保留文件名

以下文件名在层级任一层都有既定含义，**不得（MUST NOT）用作概念文档**：[^okf-spec]

| 文件名 | 用途 |
|---|---|
| `index.md` | 目录列表。见 §8。 |
| `log.md` | 更新历史。见 §9。 |

所有其他 `.md` 文件都是概念文档。

标签（tags）通过 `tags` frontmatter 字段保持为一级概念（§4.1）。OKF 不规定用单独的文件格式按标签聚合文档；需要标签浏览视图的消费者可在消费时通过扫描 frontmatter 自行合成。[^okf-spec]

## 相关概念

- [概念文档](./concept-documents.md)
- [溯源与信源](./provenance-sources.md)
- [索引文件](./index-files.md)
- [日志文件](./log-files.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。