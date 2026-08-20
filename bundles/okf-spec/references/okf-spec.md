---
type: Reference
title: Open Knowledge Format (OKF) 规范 v0.2
description: OKF 开放知识格式 v0.2 英文规范，本 bundle 的唯一权威信源。
tags: [okf, spec, reference]
resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
---

# Open Knowledge Format (OKF) 规范 v0.2

OKF（Open Knowledge Format，开放知识格式）v0.2 是一份开放、对人机均友好的知识表示格式规范，采用「markdown 文件目录 + YAML frontmatter」的极简载体。本规范定义了知识包（bundle）的目录结构与保留文件名、概念文档的 frontmatter 结构（`type`、`title`、`description`、`resource`、`tags` 等）、溯源／信任／生命周期字段族（`sources`、`generated`、`verified`、`status`、`stale_after`）、跨概念链接与路径规范、actor 约定、索引文件与日志文件约定，以及可认证计算（Attested Computation）概念类型。

本文件是 vendored 第三方规范（英文原版），位于 `vendor/knowledge-catalog/okf/SPEC.md`，只读、禁止修改。当前版本为 v0.2，是对 v0.1 的向后兼容升级（新增溯源／信任／生命周期字段族与可认证计算概念类型）。

本 bundle 中的所有概念（`concepts/`、`examples/` 下的规范概念与工作示例）均以本文件为唯一权威信源，其溯源信息经 `sources` 字段指向本 Reference 概念或本文件。