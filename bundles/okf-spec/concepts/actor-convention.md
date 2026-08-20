---
type: Specification
title: 参与者约定
description: 记录身份字段所用的统一参与者约定：`<producer>/<version>`、`human:<id>`、`process:<id>` 三种形态及其信任分类用途。
tags: [okf, spec, actor]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 参与者约定

记录身份的字段（`generated.by`、`verified[].by`）使用统一的参与者（actor）约定：[^okf-spec]

- `<producer>/<version>` 用于智能体与工具，例如 `reference_agent/gemini-2.5-pro`。
- `human:<id>` 用于人，例如 `human:ahormati`。
- `process:<id>` 用于自动化进程，例如 `process:finance-nightly`。

对信任（trust）分类的消费者（§5.3，见 [信任：generated 与 verified](./trust-generated-verified.md)）按 `human:` 前缀区分，因此生产者在人工撰写或人工确认的内容上必须（MUST）使用它。[^okf-spec]

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。