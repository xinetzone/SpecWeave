---
type: Specification
title: 交叉链接与路径
description: 概念间的两种链接形式（bundle-relative 与相对路径）、路径值字段清单，以及 references/ 子目录约定。
tags: [okf, spec, linking]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 交叉链接与路径

## 概念之间的链接

概念可以（MAY）通过标准 markdown 链接彼此链接。支持两种形式：[^okf-spec]

- **绝对链接（bundle-relative）**：以 `/` 开头，相对于知识包根目录解释。这是**推荐**形式，因为当文档在其子目录内移动时它保持稳定。

  ```markdown
  See the [customers table](/tables/customers.md) for the join key.
  ```

- **相对路径**：标准的 markdown 相对路径。

  ```markdown
  See the [neighboring concept](./other.md).
  ```

从概念 A 到概念 B 的链接断言一种*关系*。具体种类（parent/child、references、joins-with、depends-on）由周围的行文（prose）表达，而非由链接本身表达。构建图视图的消费者通常把所有链接当作无类型关系的有向边。[^okf-spec]

消费者必须（MUST）容忍断链：指向知识包中不存在目标的链接并非畸形，它可能只是代表了尚未写入的知识。[^okf-spec]

## 路径值字段

若干字段命名一个路径或 URI：`resource`、`sources[].resource`、`computation`、`executor.resource` 与 `attester.resource`（§10）。`sources[].resource` 也可以是一个范围描述符（scope descriptor，§5.1），此时它不是路径。每个路径值字段接受：[^okf-spec]

- 一个绝对 URL（例如 `https://...`），
- 一个以 `/` 开头的 bundle-relative 路径，或
- 一个相对路径（例如 `../computations/revenue.md`）。

## `references/` 约定

`references/` 子目录约定性地把外部材料、运行指令或代码作为知识包内的一级概念镜像进来。信源（sources）、执行器（executors）与认证器（attesters）通常指向其中（例如 `references/attesters/revenue.py`）。它是一项命名约定，而非要求。[^okf-spec]

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。