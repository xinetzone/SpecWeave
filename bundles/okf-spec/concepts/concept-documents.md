---
type: Specification
title: 概念文档
description: OKF v0.2 概念文档结构：YAML frontmatter（必填 type，推荐 title/description/resource/tags）与正文约定标题。
tags: [okf, spec, document]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 概念文档

每个概念都是一个 UTF-8 markdown 文件，由两部分组成：[^okf-spec]

1. 一个 **YAML frontmatter 块**，以文件开头单独一行的 `---` 起始，以单独一行的 `---` 闭合。
2. 一个 **markdown 正文（body）**，含自由格式内容。

## Frontmatter

```yaml
---
type: <Type name>                  # 必需
title: <Optional display name>
description: <Optional one-line summary>
resource: <Optional canonical URI for the underlying asset>
tags: [<tag>, <tag>, ...]          # 可选
# ... trust、lifecycle、provenance 与 computation 字段族（见 §5、§10）
# ... 其他生产者定义的键值对
---
```

**必填（Required）：**

- `type`：标识概念类型的短字符串。消费者用它做路由、过滤与展示。示例值：`BigQuery Table`、`BigQuery Dataset`、`API Endpoint`、`Metric`、`Playbook`、`Reference`、`Attested Computation`。[^okf-spec]

  类型值**不做**集中注册。生产者应当（SHOULD）选取描述性且自解释的值；消费者必须（MUST）优雅地容忍未知类型，通常将其作为通用概念处理。

  `type` 是唯一始终必填的键；只携带 `type` 一条的概念即完全合规（§11）。

**推荐（Recommended）：**

- `title`：人类可读的显示名称。若省略，消费者可以（MAY）从文件名派生标题。
- `description`：概括概念的单句话。供 `index.md` 生成器、搜索摘要与预览使用。
- `resource`：唯一标识概念所描述底层资产的 URI。若概念描述的是抽象想法而非物理资源，则缺省。
- `tags`：用于横向分类的短字符串 YAML 列表。

可选的 **provenance**、**trust**、**lifecycle** 字段族（§5）以及可认证计算概念的 **computation** 字段（§10）也可出现。

**扩展（Extensions）：** 生产者可以（MAY）包含任意额外键。消费者在往返处理时应当（SHOULD）保留未知键，且必须（MUST NOT）不得拒绝含未识别字段的文档。[^okf-spec]

## 正文（Body）

正文是标准 markdown。生产者应当（SHOULD）优先使用结构化 markdown（标题、列表、表格、围栏代码块）而非自由散文，因为结构同时有助于人类阅读与智能体检索。[^okf-spec]

正文不存在必填小节。以下标题具有**约定**含义，适用时应当（SHOULD）使用：

| 标题 | 用途 |
|---|---|
| `# Schema` | 资产列/字段的结构化描述。 |
| `# Examples` | 具体使用示例，通常为围栏代码块。 |
| `# Computation` | 可认证计算的受认可计算。见 §10。 |

对信源的逐条归因使用以 `sources` 条目为键的 markdown 脚注，而非正文中的引用列表（§5.1）。

## 示例：绑定资源的概念

以下示例对应规范 §4.3，展示一个绑定到资源的 `BigQuery Table` 概念（示例代码块中字段与值保持英文原文）：[^okf-spec]

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

## 示例：不绑定资源的概念

以下示例对应规范 §4.4，展示一个不绑定资源的 `Playbook` 概念：[^okf-spec]

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

## 相关概念

- [溯源与信源](./provenance-sources.md)
- [信任：generated 与 verified](./trust-generated-verified.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。