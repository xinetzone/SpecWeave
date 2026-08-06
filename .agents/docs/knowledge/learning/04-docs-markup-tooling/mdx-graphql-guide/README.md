---
title: "MDX + GraphQL 可查询文档快速入门指南"
source: "insight:retrospective-sphinx-graphql-okf-combination-insights-20260805"
x-toml-ref: "../../../../../../.meta/toml/.agents/docs/knowledge/learning/04-docs-markup-tooling/mdx-graphql-guide/README.toml"
date: "2026-08-05"
tags: [mdx, graphql, documentation, nextjs, api-docs, queryable-docs]
category: "learning"
status: "stable"
author: "SpecWeave"
summary: "面向JS项目的MDX+GraphQL可查询文档快速入门：5分钟搭建可查询API文档站，文档既是人可读网页也是机器可查询GraphQL API"
---
# MDX + GraphQL 可查询文档快速入门指南

> 本指南基于 [Sphinx × GraphQL × OKF 组合洞察分析](../../../../retrospective/reports/insight-extraction/external-learning/retrospective-sphinx-graphql-okf-combination-insights-20260805/insight-extraction.md) 的结论，面向 JS 项目开发者，提供从零搭建「可查询文档」的完整快速入门路径。

## 为什么需要 MDX + GraphQL？

传统文档是**静态 HTML 页面**——人能读，但程序很难查询。MDX + GraphQL 的组合让文档**既是人可读的网页，也是机器可查询的 API**：

- 📝 **MDX** = Markdown + JSX，用熟悉的 Markdown 写内容，用 JSX 组件嵌入交互逻辑（包括 GraphQL 查询）
- 🔍 **GraphQL** = 类型安全的查询语言，让文档内容变成可遍历、可筛选的知识图谱
- ⚡ **组合价值**：在文档中直接写 `<Query>` 组件，运行时获取数据渲染；IDE/CLI 工具也可以通过同一个 GraphQL 端点查询文档元数据

**一句话定义**：可查询文档（Queryable Docs）是文档的下一代形态——不只是给人看的页面，更是给程序查的 API。

## 目标读者

- **JS/TS 项目维护者**：需要为库/框架/API 编写高质量文档，希望文档可被工具程序查询
- **开发者体验（DX）工程师**：正在构建 API 平台或开发者门户，需要动态文档能力
- **前端开发者**：熟悉 React/Next.js，想了解如何将 GraphQL 集成到文档工作流

## 前置知识

- 基础 React/Next.js 知识
- 了解 Markdown 语法
- GraphQL 基础概念（Schema/Query/Resolver）——不熟悉也没关系，[01-quickstart.md](01-quickstart.md) 会边做边讲

## 阅读路径

| 路径 | 章节 | 时间 | 目标 |
|------|------|------|------|
| 🚀 **快速上手** | [00 概述](00-overview.md) → [01 快速上手](01-quickstart.md) | 15 分钟 | 从零搭建可运行的最小可查询文档站 |
| 🔧 **组件开发** | [02 查询组件开发](02-query-components.md) | 20 分钟 | 掌握 GraphQL 查询组件的编写模式 |
| 📚 **生产实践** | [03 最佳实践与FAQ](03-best-practices.md) | 15 分钟 | 了解性能优化、缓存策略、OKF 开放文档集成方向 |

## 目录导航

| 章节 | 核心内容 | 预估时间 |
|------|---------|---------|
| [00 - 概述与核心概念](00-overview.md) | 可查询文档理念、技术栈选型、架构总览 | 8 分钟 |
| [01 - 5分钟快速上手](01-quickstart.md) | 从零创建 Next.js 项目→配置 MDX→定义 GraphQL Schema→嵌入查询组件→运行验证，含完整代码 | 15 分钟 |
| [02 - GraphQL 查询组件开发](02-query-components.md) | 文档元数据 Schema 设计、Query 组件模式、静态生成 vs 运行时查询、Fragment 复用 | 20 分钟 |
| [03 - 最佳实践与FAQ](03-best-practices.md) | 性能优化、缓存策略、常见陷阱、与 OKF 开放知识协议集成方向、FAQ | 15 分钟 |

> 总计约 58 分钟。若只读路径 A（00+01），约 23 分钟即可获得可运行的可查询文档站。

## 技术栈

本指南选用以下技术组合（均为 2026 年 JS 生态主流方案）：

| 层 | 技术选型 | 替代方案 |
|----|---------|---------|
| 框架 | **Next.js 14+** (App Router) | Astro, Remix, Docusaurus |
| MDX | **next/mdx** + @mdx-js/react | contentlayer, fumadocs |
| GraphQL 服务器 | **GraphQL Yoga** (Next.js Route Handler) | Apollo Server, graphql-http |
| GraphQL 客户端 | **urql** (轻量) / Apollo Client | React Query + graphql-request |
| Schema 构建 | **Pothos** (代码优先) | graphql-js, Nexus, TypeGraphQL |

## Changelog

<!-- changelog -->
- 2026-08-05 | create | 初始版本（v1.0）：完整4章指南，含从零搭建的完整代码示例

---

← 上一章：无 | [返回目录](README.md) | 下一章：[概述与核心概念](00-overview.md) →
