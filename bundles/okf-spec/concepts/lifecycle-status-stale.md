---
type: Specification
title: 生命周期：status 与 stale_after
description: OKF v0.2 §5.4-§5.5：`status` 标记概念状态（draft/stable/deprecated），`stale_after` 以绝对日期标记过期。
tags: [okf, spec, lifecycle]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 生命周期：status 与 stale_after

## 状态（status）

```yaml
status: stable        # draft | stable | deprecated
```

- `draft`：尚未评审；可能不完整。[^okf-spec]
- `stable`：默认值；可供消费。
- `deprecated`：为链接与历史保留；不再为当前最新。

`status` 缺省（未提供）⇒ `stable`。

## 过期（stale_after）

```yaml
stale_after: 2026-09-23   # absolute date; content is stale on/after this day
```

可选。一个绝对日期（`YYYY-MM-DD`）。当 `today >= stale_after` 时，概念视为过期。采用绝对日期而非相对 TTL（存活时长），使"是否过期"的判定保持为一次平凡的日期比较，而不依赖概念是何时被读取的。[^okf-spec]

## 相关概念

- [溯源与信源（sources）](./provenance-sources.md)
- [信任：generated 与 verified 及信任层级](./trust-generated-verified.md)
- [参与者约定](./actor-convention.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。