---
type: Glossary
title: OKF 术语表
description: OKF v0.2 核心术语的中英对照与定义（知识包、概念、溯源、可信度信号、信任层级、可认证计算等）。
tags: [okf, spec, glossary]
generated: { by: reference_agent/trae-glm, at: 2026-08-20T08:00:00Z }
verified: { by: process:seven-concepts-V, at: 2026-08-20T09:00:00Z }
status: stable
stale_after: 2027-12-31
sources:
  - id: okf-spec
    resource: ../../../vendor/knowledge-catalog/okf/SPEC.md
    title: Open Knowledge Format (OKF) SPEC v0.2
---

# 术语表

下表列出 OKF v0.2 规范 §2 的全部核心术语。[^okf-spec]

| 英文术语 | 中文译名 | 定义 |
|---|---|---|
| Knowledge Bundle | 知识包 | 一个自包含、层级化的知识文档集合，是分发的单元。 |
| Concept | 概念 | 知识包内的单个知识单元，表示为一个 markdown 文档；可描述有形资产（表、API）、抽象想法（指标、业务流程）或介于两者之间的任何事物。 |
| Concept ID | 概念 ID | 概念文件在知识包内的路径，去掉 `.md` 后缀。 |
| Frontmatter | 前置元数据 | markdown 文件顶部以 `---` 分隔的 YAML 元数据块。 |
| Body | 正文 | 文件中 frontmatter 之后的全部内容。 |
| Link | 链接 | 从一个概念到另一个概念的标准 markdown 链接，用于表达超出隐含父子层级的关系。 |
| Source | 信源 | 概念据以派生的材料，可为知识包外部或内部，记录在 `sources` frontmatter 字段中。 |
| Provenance | 溯源 | 概念据以派生的一组信源。 |
| Credibility signal | 可信度信号 | 每个信源的客观事实（`author`、`usage_count`、`last_modified`），用于推断信任；OKF 记录信号而非裁决（见 §5.1）。 |
| Actor | 参与者 | 标识谁或什么执行了某个动作的字符串：智能体使用 `<producer>/<version>` 约定，人使用 `human:<id>`，自动化流程使用 `process:<id>`（见 §7）。 |
| Trust tier | 信任层级 | 从概念的 `verified` 字段派生的层级：未验证（unverified）、机器确认（machine-confirmed）或人工复核（human-reviewed）（见 §5.3）。 |
| Attested Computation | 可认证计算 | 一种概念（`type: Attested Computation`），携带计算某个值的受认可方式，使消费者能通过实际运行来确认该值确为此方式产生（见 §10）。 |
| Executor | 执行器 | 执行计算并返回回执（receipt）的运行指令或代码（见 §10.2）。 |
| Receipt | 回执 | 一次运行返回的证据，其形状由 `executor.receipt` 指定；是运行时产物，不存储在知识包中（见 §10）。 |
| Attester | 认证器 | 检查回执并返回裁决的确定性（无 LLM）代码（见 §10.2）。 |

## 相关概念

- [溯源与信源](./provenance-sources.md)
- [信任：generated 与 verified](./trust-generated-verified.md)
- [信任层级](./trust-generated-verified.md)
- [可认证计算](./attested-computations.md)

[^okf-spec]: Open Knowledge Format (OKF) SPEC v0.2，见 vendor/knowledge-catalog/okf/SPEC.md。