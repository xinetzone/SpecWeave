---
type: Specification
title: 合规性（Conformance）
description: OKF v0.2 合规三要件，以及消费者对 trust/lifecycle/provenance/computation 字段族的处理要求与"不得拒绝"清单。
tags: [okf, spec, conformance]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 合规性（Conformance）

一个 bundle **合规**（conformant）于 OKF v0.2，当且仅当：[^okf-spec]

1. 树中每个非保留 `.md` 文件都包含一个可解析的 YAML frontmatter 块（frontmatter 结构见 [概念文档](./concept-documents.md)）。
2. 每个 frontmatter 块都包含非空的 `type` 字段。
3. 每个保留文件名（`index.md`、`log.md`）在出现时分别遵循 §8（见 [索引文件](./index-files.md)）与 §9（见 [日志文件](./log-files.md)）的结构。

当信任、生命周期、溯源或计算字段族出现时，生产者**应当**（SHOULD）遵循 §5 至 §10，而消费者：[^okf-spec]

- **必须**（MUST）将裸 `verified` 映射视为单元素列表（§5.2）。
- **必须不得**（MUST NOT）因缺少任何可选字段族而拒绝概念（§5.3）。
- **应当**（SHOULD）仅从本文规定的字段推导信任层级与过期状态，并**应当**（SHOULD）呈现而非静默丢弃失败的认证（§10.5）。

消费者**应当**（SHOULD）将其余所有约束视为软性指导。特别是，消费者**必须不得**（MUST NOT）因以下原因拒绝一个 bundle：

- 缺少可选 frontmatter 字段。
- 未知的 `type` 值。
- 未知的额外 frontmatter 键。
- 交叉链接断开。
- 缺少 `index.md` 文件。

## 相关概念

- [概念文档](./concept-documents.md)
- [索引文件](./index-files.md)
- [日志文件](./log-files.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。