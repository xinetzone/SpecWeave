---
type: Changelog
title: 相对 v0.1 的变更
description: OKF v0.2 相对 v0.1 的两处破坏性变更（timestamp 与 # Citations 的取代）与全部增量变更（新字段族、Attested Computation、# Computation、actor 约定）。
tags: [okf, spec, changelog]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 相对 v0.1 的变更

v0.2 取代（supersede）OKF v0.1；按 §12 属于次版本（minor）升级，唯下列两处刻意为之的破坏性变更例外——它们重命名或退役了 v0.1 字段。在下面注明的回退（fallback）约定下，v0.1 知识包可被 v0.2 消费者消费。[^okf-spec]

## 破坏性变更（Breaking changes）

- **`timestamp` 被 `generated.at` 取代。** 概念的最后一次内容变更现记为 `generated: { by, at }`（§5.2）。当 `generated` 缺省时，消费者可以（MAY）回退（fall back）到遗留的 `timestamp`。
- **正文 `# Citations` 列表被 `sources` 取代。** 溯源移至 frontmatter（§5.1）。消费者应当（SHOULD）读取 `sources`，且可以（MAY）对 v0.1 文档仍解析遗留的正文 `# Citations` 列表。

## 增量变更（Additive changes）

以下全部为增量（additive）变更：新增可选键、一个新概念类型与一个新约定标题。它们缺省时，得到的便是一个朴素的 v0.1 概念。[^okf-spec]

- 新 frontmatter 字段族：`sources` 及其逐信源可信度信号（`author`、`usage_count`、`last_modified`）与同级 `usage_window`；`generated`、`verified`；`status`、`stale_after`（§5）。
- 新概念类型 `Attested Computation` 及其计算键 `runtime`、`parameters`、`computation`、`executor`、`attester`（§10）。
- 新约定正文标题 `# Computation`（§4.2）。
- 用于 `generated.by` 与 `verified[].by` 的 actor 约定（§7）。

其余（知识包结构、保留文件名、必填 `type`、推荐 `title`/`description`/`resource`/`tags`、交叉链接、index 文件、log 文件、宽松合规）原样保留不变。

## 相关概念

- [信任：generated 与 verified](./trust-generated-verified.md)
- [溯源与信源](./provenance-sources.md)
- [可认证计算](./attested-computations.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。