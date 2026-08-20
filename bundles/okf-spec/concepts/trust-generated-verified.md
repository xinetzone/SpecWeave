---
type: Specification
title: 信任：generated 与 verified 及信任层级
description: OKF v0.2 §5.2-§5.3：`generated` 记录内容如何产生，`verified` 记录核验事件，并由此派生三级信任层级。
tags: [okf, spec, trust]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 信任：generated 与 verified 及信任层级

`generated` 记录当前内容是如何被产生的。`verified` 记录谁或什么已针对其信源或 `resource` 核验过该内容。二者保持分立，因为*编写*概念的人未必是*核验*它的那个人。[^okf-spec]

```yaml
generated: { by: reference_agent/gemini-2.5-pro, at: 2026-06-20T22:53:05Z }
```

- `generated.by`：`generated` 内**必填（REQUIRED）**。一个参与者（actor，§7）。
- `generated.at`：一个 ISO 8601 日期时间，标记内容最后一次有意义改动的时间。消费者用它来区分"最近的编辑"与"过期的事实"。

```yaml
verified:
  - { by: human:ahormati, at: 2026-06-25T09:00:00Z }
  - { by: process:finance-nightly, at: 2026-06-26T02:00:00Z }
```

- `verified`：核验事件列表，每条含 `by`（一个参与者）与 `at`（一个 ISO 8601 日期时间）。多条 entry 记录相互独立的检查——例如一次人工签署加一个夜间进程。"核验于多久之前"即最晚的 `at`。
- `verified` 独立于 `generated.at`：内容可以在不重新核验的情况下改变，事实也可以在不重新生成的情况下被重新核验。
- 单个核验者可以（MAY）写成单个 `{ by, at }` 映射而不带列表短横线。消费者必须（MUST）将裸映射视为单元素列表：[^okf-spec]

```yaml
verified: { by: human:ahormati, at: 2026-06-25T09:00:00Z }
```

## 信任层级

消费者从 `verified` 派生信任层级（trust tier），自低至高：[^okf-spec]

- 无 `verified` 键 ⇒ **未验证（unverified）**。
- `verified` 仅由非 `human:` 参与者构成 ⇒ **机器确认（machine-confirmed）**。
- `verified` 由某个 `human:<id>` 参与者构成 ⇒ **人工复核（human-reviewed）**。

分层判定以 `human:` 前缀为依据：只要任一核验者的 `by` 带 `human:` 前缀，即属人工复核；全为非 `human:` 参与者则为机器确认（§7）。没有任何信任前置元数据（trust frontmatter）的概念依然可被消费；消费者不得（MUST NOT）拒绝它（§11）。信任层级是咨询性信号，而非访问控制。[^okf-spec]

## 相关概念

- [溯源与信源（sources）](./provenance-sources.md)
- [生命周期：status 与 stale_after](./lifecycle-status-stale.md)
- [参与者约定](./actor-convention.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。