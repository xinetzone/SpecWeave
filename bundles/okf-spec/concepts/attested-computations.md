---
type: Specification
title: 可认证计算（Attested Computations）
description: OKF v0.2 可认证计算概念：runtime/parameters/computation/executor/attester 契约字段、内联与文件两种计算方式、消费者的用法，以及 verification 与 attestation 之别。
tags: [okf, spec, computation]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 可认证计算（Attested Computations）

可认证计算（Attested Computation）概念不仅承载一个值*意味着什么*，还承载一种受认可的*计算*它的方式，从而消费者能够确认智能体运行的是受认可的计算，而非自行临场发挥的计算。[^okf-spec] 溯源（§5.1，见 [溯源与信源](./provenance-sources.md)）回答"这条主张从何而来"；认证回答"这个数字是否正是按我们声明必须采用的方式产生的"。OKF 记录计算本身及其核验手段；它自身不执行任何东西。

## 计算作为独立概念（§10.1）

一套受认可的计算是一个独立的 `type: Attested Computation` 概念。需要该值的概念（一个 `Metric`、一个 `BigQuery Table`）用普通 markdown 链接（§6）指到它（链接语法见 [交叉链接与路径](./cross-linking-paths.md)）。三条动机支撑这种独立概念：

- **`runtime` 定义了 `parameters` 的含义。** 一个参数是 SQL 绑定变量、dbt var 还是 Python 实参，取决于运行时。把 `runtime` 与 `parameters` 放在同一个 frontmatter 中，使绑定语义不言自明。
- **一套计算，多个消费者。** 同一套计算可以为指标、仪表盘概念和报告共同背书；作为一个概念，它被引用一次、复用多次。
- **信任状态按计算单元隔离。** `verified`、`stale_after` 与单个 `attester` 描述的是同一件事。收入、利润与毛利各自独立核验与认证——即三个概念，而非一个 frontmatter 里的三条条目。

## 契约字段（§10.2）

契约即概念的顶层 frontmatter。除溯源、信任与生命周期字段族（§5，见 [溯源与信源](./provenance-sources.md) 与 [信任：generated 与 verified](./trust-generated-verified.md)）外，可认证计算概念还携带：

- `runtime`：此类型**必填**（REQUIRED）。唯一说明如何运行计算的字段，因此也说明执行器与认证器如何解读它，以及 `parameters` 的含义为何。示例值：`bigquery`、`postgres`、`dbt`、`python`、`Looker`。
- `parameters`：一个带类型、带名字的"洞"的列表，供智能体填写。每条：`{ name, type, required }`。绑定语义遵循 `runtime`。
- `computation`：可选。指向存放计算的文件路径（§6.2，见 [交叉链接与路径](./cross-linking-paths.md)），用于替代内联正文围栏（见下文"计算本身"）。缺省 ⇒ 正文 `# Computation` 围栏即计算本身。
- `executor`：计算如何运行。`resource` 指明运行指令或代码；运行器（一个智能体，或确定性消费者代码）遵循它。`receipt` 声明一次运行必须返回的字段，即认证器所检查的证据（例如一个 BigQuery 的 `job_id` 与该作业实际执行的 SQL）。
- `attester`：确定性检查。`resource` 指明代码（无 LLM），它接收回执并返回裁决。它被设计为在消费者侧运行。

`resource` 背后是什么（一个 Skill、一个脚本、一个容器）属于打包选择；OKF 约定的是接口，而非打包方式（§1）。[^okf-spec]

```markdown
---
type: Attested Computation
title: Revenue for fiscal year
description: Recognized revenue for a fiscal year, per Finance's definition.
status: stable
runtime: bigquery
parameters:
  - { name: year, type: integer, required: true }
executor:
  resource: references/skills/run-on-bq.md
  receipt: [job_id, executed_sql, result]
attester:
  resource: references/attesters/revenue.py
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
stale_after: 2026-09-23
sources:
  - id: rev-policy
    resource: https://wiki.acme/finance/revenue-recognition
    title: Revenue recognition policy
---

# Computation

    SELECT SUM(amount) AS revenue
    FROM finance.recognized_revenue
    WHERE fiscal_year = @year

The computation binds only the declared `parameters`, per the recognition
policy.[^rev-policy]

[^rev-policy]: Revenue recognition policy
```

## 计算本身（§10.3）

以两种方式之一提供计算：[^okf-spec]

- **内联：** 正文 `# Computation` 之下的单个围栏代码块。适合与契约一并审阅的短计算。
- **文件：** 将 `computation` 设为路径（§6.2），并省略正文围栏。适合长计算或生成型计算，或已作为真实文件与非 OKF 工具共用的计算。

```yaml
runtime: bigquery
computation: references/computations/lib/revenue.sql
parameters:
  - { name: year, type: integer, required: true }
```

智能体**可以**（MAY）仅为已声明的 `parameters` 提供*值*；它**必须不得**（MUST NOT）编写或改写计算。[^okf-spec] 将 `computation` 与参数值绑定为可执行产物是消费者的职责，而认证器独立地重新推导出同一绑定，以与实际运行的内容比对。由于比对对象是回执所携带的、展开编译后的产物（`executed_sql`、`compiled_sql`），被重写的查询、被掉包的计算文件、或被篡改的依赖都会导致检查失败。一个仅有类型、只暴露参数的接口，才使"受认可的事是否运行了"成为一次机械化比对，而非一次主观判断。

## 使用计算的概念（§10.4）

一份文档很少是单一计算。一份讨论收入、利润与毛利的利润表概览仍是一个可读概念，并为每个数字链接到一个可认证计算：[^okf-spec]

```markdown
---
type: Metric
title: Revenue
description: Recognized revenue for a fiscal year.
tags: [finance, revenue]
status: stable
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
---

# Definition

Recognized revenue sums `amount` over rows booked to the fiscal year,
computed by [the revenue computation](../computations/revenue.md).
```

由于每套计算都是独立概念，收入可以仍保持新鲜，而利润已超过其 `stale_after`，且各自在自己的运行上认证。将它们同置是目录选择（一个带 `index.md` 的 `computations/` 文件夹），而非 frontmatter 选择。

## 消费者如何使用（信息性）（§10.5）

本小节为信息性（informative），非规范性。下述运行时产物**不**存储在 bundle 中。

1. **发现（Discover）**：通过 `type: Attested Computation` 发现——这是一个可提升进 `index.md` 的 frontmatter 信号；消费者可直接到达，或跟随一个使用该计算的概念的链接而来。
2. **加载（Load）**：从 frontmatter 加载契约，从正文（或 `computation` 所指向的文件）加载计算。
3. **参数化（Parameterize）**：智能体为已声明的参数提供值。
4. **执行（Execute）**：执行器运行绑定后的计算，并返回由 `executor.receipt` 塑造的回执。
5. **认证（Attest）**：消费者对回执运行认证器。它确认溯源（实际运行的计算等于 `computation` 绑定声明参数后的结果，而非智能体编写的 SQL）与保真度（展示值等于回执的权威来源——按 job id 重新读取，而非取自智能体的文本）。
6. **门禁（Gate）**：认证失败则拒绝展示；当 `today >= stale_after` 时警告或拒绝。成功时呈现裁决（例如指向作业日志的链接），使信任可见。

## 核验（verification）对比认证（attestation）（§10.6）

`verified`（§5.2，见 [信任：generated 与 verified](./trust-generated-verified.md)）与认证是两回事，二者并存：[^okf-spec]

- `verified` 确认*定义*仍符合策略。它是文档级、慢速、且记录在 bundle 中的。
- 认证确认某一次*运行*以受认可的方式产生了该值。它是逐次调用、运行时、且不存储在 bundle 中的。

一个定义过期的概念仍可通过认证，而一个刚刚核验过的定义在每次运行时仍需认证——这正是二者都必要的原因。

## 相关概念

- [信任：generated 与 verified](./trust-generated-verified.md)
- [交叉链接与路径](./cross-linking-paths.md)
- [溯源与信源](./provenance-sources.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。