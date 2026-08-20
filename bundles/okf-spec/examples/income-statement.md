---
type: Example
title: 损益表工作示例：v0.1 → v0.2 迁移
description: 展示同一张损益表（收入与毛利）从 v0.1 单文档形态迁移到 v0.2 可认证计算拆分形态。
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

本示例（源自 OKF v0.2 规范附录 A）展示同一张损益表（含收入与毛利两个指标）在 v0.1 与 v0.2 两种形态下的写法差异：

* **v0.1 形态**是单文档：两个指标放在一个概念里、SQL 直接写进散文、引文是一条扁平列表、唯一的时间戳字段是 `timestamp`。
* **v0.2 形态**把收入与毛利拆成两个独立的可认证计算（Attested Computation）概念，由一个叙事型 `Metric` 概念链接二者。

> 注意：v0.1 形态是历史形态，已被 v0.2 取代——`timestamp` 被 `generated.at` 取代，正文 `# Citations` 列表被 frontmatter 的 `sources` 取代。[^okf-spec]

# v0.1 形态

```markdown
---
type: Metric
title: Income statement (fiscal year)
description: Headline income-statement figures for a fiscal year.
tags: [finance, income-statement]
timestamp: '2026-05-28T22:53:05+00:00'
---

# Definition
The income statement reports revenue and gross profit for a fiscal year.

# Revenue
Recognized revenue sums `amount` over rows booked to the fiscal year:

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = <year>

# Gross profit
Gross profit by segment, per the cost-allocation standard:

    SELECT gross_profit FROM fct_income_statement
    WHERE fiscal_year = <year> AND segment = <segment>

# Citations
- https://wiki.acme/finance/fpa-handbook
- https://wiki.acme/finance/revenue-recognition
- https://wiki.acme/finance/cost-allocation
```

# v0.2 形态

收入与毛利被拆成两个独立的可认证计算概念，由叙事型 `Metric` 概念链接；目录布局如下（`bundles/finance/`）：

```text
bundles/finance/
  metrics/income-statement.md      type: Metric  (narrates, links both)
  computations/revenue.md          type: Attested Computation  (runtime: bigquery)
  computations/profit.md           type: Attested Computation  (runtime: dbt)
  references/skills/run-on-bq.md, run-dbt.md
  references/attesters/sql-equality.py, dbt-binding.py
```

其中 `metrics/income-statement.md` 是可读的叙事文档，信任状态落在它所链接的计算概念上，而非自身：

```markdown
---
type: Metric
title: Income statement (fiscal year)
description: Headline income-statement figures for a fiscal year.
tags: [finance, income-statement]
status: stable
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-12-31
sources:
  - id: fpa-handbook
    resource: https://wiki.acme/finance/fpa-handbook
    title: FP&A reporting handbook
---

# Definition
The income statement reports [revenue](../computations/revenue.md) and
[gross profit](../computations/profit.md) for a fiscal year, per the FP&A
reporting handbook.[^fpa-handbook] Each figure is produced by a sanctioned,
attestable computation; this concept only narrates them.

[^fpa-handbook]: FP&A reporting handbook
```

`computations/revenue.md` 是 BigQuery SQL，人工验证、未过期，并由一个携带可信度信号的实时仪表盘信源佐证：

```markdown
---
type: Attested Computation
title: Revenue for fiscal year
description: Recognized revenue for a fiscal year, per Finance's definition.
tags: [finance, revenue]
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/sql-equality.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-28T14:00:00Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-12-31
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
    author: team:finance-fpa
    last_modified: 2026-04-02
  - id: exec-rev-dash
    resource: dashboards/exec-revenue
    title: Executive revenue dashboard
    author: team:finance-fpa
    usage_count: 5000
    last_modified: 2026-06-18
usage_window: { from: 2026-06-01, to: 2026-06-30 }
---

# Computation

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = @year

Recognized revenue per the recognition policy,[^rev-policy] corroborated by
the executive revenue dashboard.[^exec-rev-dash]

[^rev-policy]: Revenue recognition policy
[^exec-rev-dash]: Executive revenue dashboard
```

`computations/profit.md` 是 dbt 模型，由流程验证，且已超过其 `stale_after`：

```markdown
---
type: Attested Computation
title: Gross profit for fiscal year
description: Gross profit by segment for a fiscal year, per the cost-allocation standard.
tags: [finance, profit]
status: stable
runtime: dbt
parameters:
  - { name: year, type: integer, required: true }
  - { name: segment, type: string, required: true }
executor:
  resource: references/skills/run-dbt.md
  receipt: [run_id, compiled_sql, result]
attester:
  resource: references/attesters/dbt-binding.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-14T14:00:00Z }
verified: { by: process:finance-nightly, at: 2026-06-12T08:00:00Z }
stale_after: 2026-06-15
sources:
  - id: cost-alloc
    resource: https://wiki.acme/finance/cost-allocation
    title: Cost allocation standard
---

# Computation

    SELECT gross_profit
    FROM {{ ref('fct_income_statement') }}
    WHERE fiscal_year = {{ var('year') }}
      AND segment = {{ var('segment') }}

Gross profit by segment per the cost-allocation standard.[^cost-alloc]

[^cost-alloc]: Cost allocation standard
```

## 相关规范概念

* [概念文档（§4）](../concepts/concept-documents.md)
* [信任：generated 与 verified（§5）](../concepts/trust-generated-verified.md)
* [可认证计算（§10）](../concepts/attested-computations.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。