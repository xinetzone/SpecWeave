---
type: Specification
title: 索引文件
description: `index.md` 的渐进披露用途、无 frontmatter 的默认约定（仅根 index.md 可含 okf_version），以及分组标题 + 条目列表格式。
tags: [okf, spec, index]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 索引文件

`index.md` 可以（MAY）出现在任意目录，包括知识包根目录。它枚举该目录的内容以支持**渐进披露（progressive disclosure）**：让人或智能体在打开单个文档之前先看到有哪些内容可用。[^okf-spec]

索引文件不含 frontmatter，仅有一个例外：知识包根目录的 `index.md` 可以（MAY）携带一个 `okf_version` 键（§12）。正文使用一个或多个分组（section），每个分组在一个标题下聚合概念：[^okf-spec]

```markdown
# Section / Group Heading

* [Title 1](relative-url-1) - short description of item 1
* [Title 2](relative-url-2) - short description of item 2

# Another Section

* [Subdirectory](subdir/) - short description of the subdirectory
```

条目应当（SHOULD）包含所链接概念 frontmatter 中的 description。生产者可以（MAY）自动生成 `index.md`；当不存在时，消费者可以（MAY）即时合成一个。[^okf-spec]

## 相关概念

- [知识包结构](./bundle-structure.md)
- [交叉链接与路径](./cross-linking-paths.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。