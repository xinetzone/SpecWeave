---
type: Specification
title: 溯源与信源（sources）
description: OKF v0.2 §5.1：`sources` 字段记录概念据以派生的信源，通过客观可信度信号（而非评分）推断信任。
tags: [okf, spec, provenance]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 溯源与信源（sources）

前置元数据（frontmatter）的三组字段族——溯源（provenance）、信任（trust）、生命周期（lifecycle）——使"它从何而来""我该多信任它""它是否仍最新"都能从前置元数据中得到回答。三者均为可选，其缺省本身即携带含义：一个未核验（unverified）的概念可与已核验概念区分开来，但绝不会被拒绝（§11）。溯源由 `sources` 表达。[^okf-spec]

`sources` 记录概念据以派生的材料，可为知识包外部或内部材料。

```yaml
sources:
  - id: ga4-schema
    resource: https://developers.google.com/analytics/bigquery/export-schema
    title: GA4 BigQuery Export schema
    author: team:ga4-docs
    usage_count: 5000
    last_modified: 2026-05-30
usage_window: { from: 2026-06-01, to: 2026-06-30 }
```

每条 `sources` entry：

- `resource`：entry 内**必填（REQUIRED）**。命名一个消费者可追踪的具体工件（一个绝对 URL、一个知识包相对路径，或一个指向 `references/` 子目录的路径，§6），或一个消费者无法追踪的总体/范围描述符（例如 BigQuery 项目 X 中的所有查询）。
- `id`：可选。用于对个别断言进行归因的稳定键（见下文）。当正文引用了该信源时，应当（SHOULD）提供。
- `title`：可选。信源的人类可读标签。
- 可选的可信度信号 `author`、`usage_count`、`last_modified`，见下文描述。

## 源可信度信号

OKF 记录客观的、逐信源的可信度信号（credibility signal），使消费者能通过判断"概念据以抽取的信源"来判断在多大程度上信任该概念。OKF **不**存储可信度评分（score）：评分是主观的、无法跨消费者移植，并且会过期。可信度是从信号中*推断*出来的——与信任层级（trust tier，§5.3）的方式相同——而非被存储。每个信号均可选，位于一条 `sources` entry 上：[^okf-spec]

- `author`：谁或什么产出了该信源，采用参与者约定（actor convention，§7）。一个权威性信号。
- `usage_count`：在 `usage_window` 内，`resource` 被使用的次数（看板浏览、查询执行、页面阅读）。一个采用度与活性信号。对单个工件，它是该工件自身的使用计数；对范围描述符，它是范围内触及该概念的使用次数。
- `last_modified`：信源自身最后一次变更的时间（`YYYY-MM-DD`）。一个新近性（recency）信号，区别于 `generated.at`（§5.2）——后者记录概念被编写的时间。
- `usage_window`：作为 `sources` 的同级字段只写一次，用 `{ from, to }` 日期范围框定每一个 `usage_count`。单条 entry 可以（MAY）携带自己的 `usage_window` 来覆盖共享的那个。

`usage_count` 是一个粗粒度信号。它只在"存活 vs 消亡"（alive-versus-dead）与数量级（order-of-magnitude）层面可比，也可与信源自身随时间的历史作比较，但**不作**精确的跨类排名：一次定时查询的执行与一次人主动的看板浏览并不等价。消费者应当（SHOULD）将其解读为活性与趋势，而非评分。[^okf-spec]

谱系（lineage）通过**链接**而非专用字段表达。当一个 `resource` 指向另一个 OKF 概念时，派生边已存在于知识包图中（§6），因此消费者可以（MAY）递归进入该信源自身的 `sources` 并让可信度传播。外部叶子信源只携带它们内在的信号。更深层的谱系（显式的外部 `derived_from`，或数据谱系）超出 v0.2 范围。

## 逐断言归因

要对一个具体断言做归因，使用一个正文 markdown 脚注，其 label 为某个 `sources[].id`：[^okf-spec]

```markdown
The `events_` table is sharded daily as `events_YYYYMMDD`.[^ga4-schema]

[^ga4-schema]: GA4 BigQuery Export schema
```

脚注 label 是进入 `sources` 的连接键（join key）；消费者通过匹配的 entry 解析归因，而不是解析脚注正文。label 按键控（keyed）而非位置索引（positional，`sources[0]`）的方式使用，因为智能体会不断重写这些文档：一旦列表被重排，位置索引会在无声中错误归因，而稳定的 `id` 能在重排后依然存活。[^okf-spec]

## 相关概念

- [信任：generated 与 verified 及信任层级](./trust-generated-verified.md)
- [生命周期：status 与 stale_after](./lifecycle-status-stale.md)
- [参与者约定](./actor-convention.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。