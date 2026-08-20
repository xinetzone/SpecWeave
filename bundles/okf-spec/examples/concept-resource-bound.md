---
type: Example
title: 绑定资源的概念示例：Customer Orders（BigQuery 表）
description: 一个绑定到具体 BigQuery 资源的概念示例，frontmatter 含 resource、tags、generated 字段。
tags: [okf, spec, example]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

这是绑定到具体资源的概念示例（源自 OKF v0.2 规范 §4.3）。frontmatter 含 `resource`、`tags`、`generated` 字段：`resource` 用规范 URI 唯一标识概念所描述的底层资产，`tags` 用于跨切面分类，`generated` 记录内容的产生方式与时间。[^okf-spec]

```markdown
---
type: BigQuery Table
title: Customer Orders
description: One row per completed customer order across all channels.
resource: https://console.cloud.google.com/bigquery?p=acme&d=sales&t=orders
tags: [sales, orders, revenue]
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-05-28T14:30:00Z }
---

# Schema

| Column        | Type      | Description                              |
|---------------|-----------|------------------------------------------|
| `order_id`    | STRING    | Globally unique order identifier.        |
| `customer_id` | STRING    | Foreign key into [customers](/tables/customers.md). |
| `total_usd`   | NUMERIC   | Order total in US dollars.               |
| `placed_at`   | TIMESTAMP | When the customer submitted the order.   |

# Joins

Joined with [customers](/tables/customers.md) on `customer_id`.
```

## 相关规范概念

* [概念文档（§4）](../concepts/concept-documents.md)
* [信任：generated 与 verified（§5）](../concepts/trust-generated-verified.md)
* [可认证计算（§10）](../concepts/attested-computations.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。