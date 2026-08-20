---
type: Example
title: 不绑定资源的概念示例：数据新鲜度告警（Playbook）
description: 一个不绑定具体资源的概念示例，无 resource 字段，正文含指向其他概念的链接。
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

这是不绑定具体资源的概念示例（源自 OKF v0.2 规范 §4.4）。此类概念描述抽象想法而非物理资产，因此无 `resource` 字段；正文含指向其他概念的链接（如 `orders` 表、`ingestion` 作业仪表盘）。[^okf-spec]

```markdown
---
type: Playbook
title: "Incident response: data freshness alert"
description: Steps to triage a freshness alert on the orders pipeline.
tags: [oncall, incident]
generated: { by: human:ahormati, at: 2026-04-12T09:00:00Z }
---

# Trigger

A freshness alert fires when `orders` lags more than 30 minutes behind its
expected SLA. See the [orders table](/tables/orders.md).

# Steps

1. Check the [ingestion job dashboard](https://example.com/dash).
2. ...
```

## 相关规范概念

* [概念文档（§4）](../concepts/concept-documents.md)
* [信任：generated 与 verified（§5）](../concepts/trust-generated-verified.md)
* [可认证计算（§10）](../concepts/attested-computations.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。