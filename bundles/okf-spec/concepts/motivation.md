---
type: Rationale
title: OKF 规范动机
description: OKF 的动机：人可读、可解析、可 diff、可移植，以及溯源、信任、新鲜度、生命周期、认证成为一级字段的理由。
tags: [okf, spec, rationale]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 动机

面向 AI 智能体的知识表示领域正在迅速演进，许多互不兼容的约定不断涌现。OKF 的立场是：知识最好以普遍可达、既有的格式来表示，这些格式应当：[^okf-spec]

- **可读**：人类无需任何工具即可阅读。
- **可解析**：智能体无需专属 SDK 即可解析。
- **可 diff**：可在版本控制中做差异比较。
- **可移植**：可跨工具、跨组织、跨时间移植。

如今，知识语料越来越多地不再是「一次编写、然后被阅读」，而是**被智能体持续编写与维护**。当大多数概念都由机器生成时，消费者需要一些答案，而这些答案是朴素的「markdown + frontmatter」约定所无法作为一级内容回答的：[^okf-spec]

1. 它是从什么创建的，又是如何被验证的？（**溯源 provenance**）
2. 我应该在多大程度上信任它？（**信任 trust**）
3. 它还成立（为真）吗？（**新鲜度 freshness**）
4. 它是当前版本吗？（**生命周期 lifecycle**）
5. 这个数字是按我们声明的方式产生的吗？（**认证 attestation**）

OKF v0.2 将 provenance、trust、lifecycle 与 attestation 提升为一级内容，同时保持格式的最小约束。该格式只标准化使知识语料自描述所需的一小部分结构约定——其余一概交由生产者决定。[^okf-spec]

## 目标（Goals）

1. 定义一个通用格式，供**生产者**（人、智能体、导出流水线）写入。[^okf-spec]
2. 指引**消费者**（智能体、UI、搜索索引、确定性代码）应当如何读取与遍历该格式。
3. 促进知识在系统与组织之间的**交换**。
4. 标准化一小组 frontmatter 字段，使智能体维护的语料**可信**，而不规定任何运行时。

## 非目标（Non-goals）

- 定义一套固定的概念类型分类法。[^okf-spec]
- 规定存储、服务或查询基础设施。
- 取代领域专用 schema（Avro、Protobuf、OpenAPI 等）。OKF *引用*它们，而非吞并它们。
- 规定执行器（executor）或认证器（attester）所指向代码的打包或调用标准。OKF 固定接口，不固定打包方式。

## 相关概念

- [溯源与信源](./provenance-sources.md)
- [信任：generated 与 verified](./trust-generated-verified.md)
- [生命周期：status 与 stale_after](./lifecycle-status-stale.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。