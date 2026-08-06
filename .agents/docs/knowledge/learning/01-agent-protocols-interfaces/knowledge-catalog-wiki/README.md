---
id: "docs-knowledge-learning-01-agent-protocols-interfaces-knowledge-catalog-wiki-index"
title: "Knowledge Catalog 知识目录平台"
category: "knowledge"
date: "2026-08-06"
tags: ["knowledge-catalog", "dataplex", "okf", "google-cloud", "ai-agent", "data-catalog", "knowledge-graph"]
---

# Knowledge Catalog 知识目录平台完整指南

> **⚠️ 技术预览版提示**
>
> - Knowledge Catalog（原Dataplex）是Google Cloud推出的AI驱动数据目录与元数据管理平台
> - OKF开放知识格式目前处于v0.2 Draft早期阶段，生态仍在快速演进中
> - 本教程基于官方开源仓库与公开信息整理，包含规范、参考实现、工具链与示例
> - 建议结合OKF规范理解，先进行概念验证再考虑生产落地

## Knowledge Catalog 是什么

Knowledge Catalog（原Google Cloud Dataplex）是Google Cloud推出的AI驱动数据目录与知识管理平台。它为所有结构化与非结构化数据构建动态知识图谱，为AI Agent提供语义层和业务上下文。

**核心组成**：

- **OKF开放知识格式规范**：通用、厂商中立的知识表示格式，以带YAML frontmatter的纯Markdown文件组织
- **参考Agent实现**：自动从BigQuery等数据源生成OKF Bundle的生产端Agent
- **可视化工具链**：交互式知识图谱浏览器，自包含HTML无需后端
- **示例数据集**：GA4电商、Stack Overflow、比特币区块链等多个开箱即用的Bundle示例

**本质**：一套完整的知识生产-消费-可视化解决方案，让参考Agent、消费Agent与人类可以像协作源代码一样在同一套产物上协同工作。

**价值主张**：数据资产可被Git版本控制，AI Agent无需适配器即可解析，知识编审融入标准软件工程工作流，元数据不再被锁定在专有服务中。

## 适合人群

- **AI Agent开发者**：需要为Agent构建可维护、可演进知识库的工程师
- **数据工程师/数据治理专家**：负责企业数据目录、元数据管理与数据资产建设
- **知识工程师/技术写作者**：负责团队知识沉淀、语义层建设与文档体系
- **架构师/技术决策者**：评估知识层技术选型，判断Knowledge Catalog与OKF是否适合团队
- **云原生/Google Cloud技术人员**：希望了解Dataplex演进方向与AI时代数据治理方案
- **对Agent知识层标准感兴趣的技术人员**：关注开放知识格式生态发展趋势

## 📄 文档索引（9篇）

| 文档                                             | 说明                                                  | 标签                                                 |
| ---------------------------------------------- | --------------------------------------------------- | -------------------------------------------------- |
| [Knowledge Catalog概述与知识地图](00-overview.md)     | 平台背景动机、设计哲学、整体架构、9章导航、三条阅读路径                        | `knowledge-catalog` `overview` `architecture`      |
| [核心概念与平台架构](01-core-concepts.md)               | 知识图谱、动态元数据、Bundle/Concept/Frontmatter核心概念、平台组件架构    | `knowledge-catalog` `concepts` `dataplex`          |
| [OKF开放知识格式规范深度解析](02-okf-specification.md)     | OKF v0.2规范详解、frontmatter字段定义、信任层级与来源溯源、渐进式披露机制      | `knowledge-catalog` `okf` `specification`          |
| [参考Agent实现原理与运行指南](03-reference-agent.md)      | BQ Pass与Web Pass双阶段工作流、生产端配置、单概念迭代开发、凭证配置           | `knowledge-catalog` `agent` `implementation`       |
| [工具链与可视化系统](04-toolchain-and-visualization.md) | 交互式知识图谱浏览器、Cytoscape.js图渲染、Markdown实时渲染、搜索与过滤机制     | `knowledge-catalog` `visualization` `toolchain`    |
| [示例Bundle深度解析](05-samples-and-bundles.md)      | GA4电商数据集、Stack Overflow公开数据集、比特币区块链、Acme Retail示例剖析 | `knowledge-catalog` `samples` `bundles`            |
| [集成模式与最佳实践](06-integration-patterns.md)        | 企业落地四阶段路径、与现有数据目录集成、Git工作流集成、知识生产消费解耦模式             | `knowledge-catalog` `integration` `best-practices` |
| [架构决策与方案对比](07-architecture-decisions.md)      | 与Unity Catalog/Collibra等方案对比、OKF局限性分析、选型决策树、风险评估    | `knowledge-catalog` `comparison` `decision`        |
| [资源与术语表](08-resources-and-glossary.md)         | 30+核心术语定义、官方资源链接、OKF交叉引用、项目内wiki导航                  | `knowledge-catalog` `glossary` `references`        |

## 📖 阅读建议

根据学习目标选择适合的路径：

### 快速上手路径（初学者/开发者，约25分钟）

**目标**：快速了解Knowledge Catalog并运行第一个示例Bundle

```
00-overview.md → 01-core-concepts.md → 02-okf-specification.md → 05-samples-and-bundles.md → 08-resources-and-glossary.md
```

### 深度开发路径（开发者/知识工程师/数据工程师，约45分钟）

**目标**：完整掌握OKF规范、参考Agent开发、工具链使用与集成方法

```
00 → 01 → 02 → 03 → 04 → 05 → 06 → 08
```

### 架构决策路径（架构师/技术决策者/数据治理专家，约38分钟）

**目标**：判断Knowledge Catalog与OKF是否适合团队，做出技术选型决策

```
00 → 01 → 02 → 06 → 07 → 08
```

**前置知识要求**：基础Markdown/YAML知识、AI Agent基本概念、Git版本控制基础、数据目录与元数据管理基本概念。如需深入OKF细节，建议先阅读[OKF开放知识格式完整指南](../okf-wiki/README.md)。

***

## 🔗 相关资源

- [📖 OKF开放知识格式完整指南](../okf-wiki/README.md) - Knowledge Catalog核心格式规范详解
- [🏠 返回上级：Agent协议与接口技术栈](../README.md)
- [📚 知识库首页](../../../../README.md)
- [🔗 官方GitHub仓库](https://github.com/GoogleCloudPlatform/knowledge-catalog)
- [☁️ Google Cloud Knowledge Catalog](https://cloud.google.com/products/knowledge-catalog)

