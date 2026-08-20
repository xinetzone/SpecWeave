---
type: Specification
title: 日志文件
description: `log.md` 的层级位置、日期分组扁平列表（最新在前）、`YYYY-MM-DD` 日期标题与前导粗体词约定。
tags: [okf, spec, log]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 日志文件

`log.md` 可以（MAY）出现在层级中的任一层，以记录该作用域（scope）的变更历史。格式是一个按日期分组的扁平列表，最新在前：[^okf-spec]

```markdown
# Directory Update Log

## 2026-05-22
* **Update**: Added a BigQuery table reference for [Customer Metrics](/tables/customer-metrics.md).
* **Creation**: Established the [Dataplex Playbook](/playbooks/dataplex.md).

## 2026-05-15
* **Initialization**: Created foundational directory structure.
```

日期标题必须（MUST）使用 ISO 8601 `YYYY-MM-DD` 形式。日志条目为自由行文（prose）；前导粗体词（`**Update**`、`**Creation**`、`**Deprecation**`）是一项约定，而非要求。[^okf-spec]

## 相关概念

- [知识包结构](./bundle-structure.md)
- [交叉链接与路径](./cross-linking-paths.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。