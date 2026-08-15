---
id: knowledge-catalog-wiki-readme
title: Google Cloud Knowledge Catalog Wiki - 入口导航
date: 2026-08-15
tags:
  - google-cloud
  - knowledge-catalog
  - dataplex
  - okf
  - metadata
  - ai-agents
  - wiki
source:
  - https://github.com/GoogleCloudPlatform/knowledge-catalog
  - vendor/knowledge-catalog/
category: knowledge/learning/07-vendor-product-learning
maturity: L1-draft
---

# Google Cloud Knowledge Catalog Wiki

> 面向AI工程师的数据目录与元数据管理知识库——理解OKF开放知识格式，掌握元数据即代码工作流，构建Agent原生的数据上下文基础设施。

## 📋 前置知识要求

阅读本Wiki前你需要：
- ✅ 基础的Markdown和YAML语法知识
- ✅ 了解Git版本控制基本概念
- ✅ 对AI Agent和RAG（检索增强生成）有基本认识
- ✅ 有BigQuery或其他数据仓库使用经验更佳
- ❌ 不需要事先了解Dataplex或Knowledge Catalog

## 📖 术语快速入门（第一次看先扫一眼）

| 术语 | 一句话解释 |
|------|-----------|
| **Knowledge Catalog** | Google Cloud的AI驱动数据目录与元数据管理平台，前身为Dataplex，为AI Agent提供数据的语义和业务上下文 |
| **OKF (Open Knowledge Format)** | 开放知识格式——用Markdown+YAML frontmatter表示知识的厂商中立格式，"知识即代码"理念的具体实现 |
| **Bundle（知识包）** | OKF的分发单元，一个自包含的目录层次结构，包含多个概念文档 |
| **Concept（概念）** | Bundle中的单个知识单元，对应一个Markdown文件，可以描述表、API、指标、业务流程等 |
| **Attested Computation（认证计算）** | OKF v0.2新增概念类型——不仅描述"值是什么意思"，还提供"如何计算这个值"的可验证方法 |
| **Metadata as Code（元数据即代码）** | 将元数据表示为源码制品（YAML/Markdown），用Git工作流管理元数据生命周期 |
| **kcmd** | Knowledge Catalog CLI工具，提供init/pull/push等git式命令管理元数据 |
| **Enrichment Agent（丰富智能体）** | 自动为数据资产查找相关信息、生成文档并发布到目录的AI智能体 |
| **Discovery Agent（发现智能体）** | 基于目录搜索API的语义搜索助手，支持复杂问题分解、多查询生成、结果重排序 |

**基于**：Knowledge Catalog (2026.08) / OKF v0.2 / kcmd CLI

---

## 📚 文档列表

| 编号 | 文档 | 内容 | 阅读时间 |
|------|------|------|----------|
| 00 | [00-overview.md](./00-overview.md) | **总览**：产品定位、核心价值主张、仓库架构全景、一页纸速查表 | 15分钟 |
| 01 | [01-okf-spec.md](./01-okf-spec.md) | **OKF开放知识格式规范（核心）**：Bundle结构、Frontmatter字段、信任/来源/生命周期、认证计算 | 40分钟 |
| 02 | [02-reference-agent.md](./02-reference-agent.md) | **参考智能体**：Python实现、两阶段运行机制（BQ+Web）、可视化器使用 | 30分钟 |
| 03 | [03-metadata-as-code.md](./03-metadata-as-code.md) | **元数据即代码（mdcode/kcmd）**：TypeScript库、CLI工作流、MCP服务器集成 | 35分钟 |
| 04 | [04-samples.md](./04-samples.md) | **示例智能体**：Discovery Agent发现智能体、Enrichment Agent丰富智能体实战 | 25分钟 |
| 05 | [05-best-practices.md](./05-best-practices.md) | **最佳实践与反模式（🔥重点）**：5个反模式、OKF编写检查清单、Agent集成模式 | 20分钟 |

---

## 🚀 快速开始指引

### 30分钟快速了解路径
> 我只想知道Knowledge Catalog是什么、OKF解决什么问题

1. 读 [00-overview.md](./00-overview.md)（15分钟）
2. 扫一眼 [01-okf-spec.md](./01-okf-spec.md) 的核心概念部分（10分钟）
3. 看 [05-best-practices.md](./05-best-practices.md) 的反模式快速避坑（5分钟）

### 2小时深度上手路径
> 我要用OKF构建知识库，或集成kcmd到我的Agent工作流

1. 完整读 [00-overview.md](./00-overview.md)
2. [01-okf-spec.md](./01-okf-spec.md) 通读OKF规范（重点理解信任和认证计算）
3. [02-reference-agent.md](./02-reference-agent.md) 了解参考实现
4. [03-metadata-as-code.md](./03-metadata-as-code.md) 跟着kcmd CLI走一遍pull/push流程
5. [04-samples.md](./04-samples.md) 看两个示例智能体如何组合使用
6. [05-best-practices.md](./05-best-practices.md) 通读所有反模式

---

## ⚠️ 最关键的7条结论（来自I阶段核心洞察）

1. **这不是传统SDK仓库，核心贡献是OKF开放标准**——Google在推动一种厂商中立的元数据交换格式，而非仅提供云API客户端
2. **"知识即代码"是核心范式**——Markdown+YAML+Git，把软件工程30年最佳实践（版本控制、PR审查、diff、CI/CD）直接迁移到知识管理
3. **面向AI Agent设计，而非仅面向人类分析师**——信任层级、来源追踪、时效标注、认证计算都是为Agent自动消费知识而设计的一等公民特性
4. **三层架构递进：标准→参考实现→生产工具**——OKF规范是核心，Python参考智能体验证可行性，mdcode/kcmd是面向生产的工具链
5. **认证计算(Attested Computation)是v0.2杀手级特性**——不仅告诉Agent"指标是什么意思"，还提供"如何验证指标计算正确"的确定性代码，防止LLM幻觉
6. **集中式目录→去中心化知识包的范式转移**——与传统数据目录（集中式存储、专有API、Web UI）不同，OKF选择文件系统+Git的去中心化思路
7. **最小约定，自由扩展**——OKF只规定最少的必填字段（仅`type`），生产者可以自由添加任意frontmatter键，消费者必须容忍未知类型

---

## 🔗 相关资源链接

- 向上导航：[../README.md](../README.md)（厂商产品学习目录）
- 官方仓库：https://github.com/GoogleCloudPlatform/knowledge-catalog
- 官方产品页：https://cloud.google.com/products/knowledge-catalog

---

## 📁 文件结构

```
knowledge-catalog-wiki/
├── README.md               ← 你在这里：入口导航
├── 00-overview.md          ← 总览与架构全景
├── 01-okf-spec.md          ← OKF开放知识格式规范（核心）
├── 02-reference-agent.md   ← 参考智能体实现
├── 03-metadata-as-code.md  ← 元数据即代码工具链
├── 04-samples.md           ← 示例智能体实战
└── 05-best-practices.md    ← 最佳实践与反模式
```

---

## 版本信息

- Knowledge Catalog仓库版本：2026.08（vendor子模块版本）
- OKF规范版本：v0.2
- 文档版本：L1-draft
- 最后更新：2026-08-15

---

**开始阅读**：[00-overview.md - 总览](./00-overview.md)
