---
id: okf-topic-index
title: "OKF（开放知识格式）主题知识导航"
date: "2026-08-19"
category: "learning"
tags: ["okf", "open-knowledge-format", "index", "navigation", "wiki"]
type: Reference
description: "OKF（开放知识格式）相关知识的统一导航总入口，按格式规范与工具链两大子域归类，附版本说明与推荐学习路径"
generated:
  by: "process:docs-to-okf-conversion"
  at: "2026-08-22T00:00:00Z"
verified:
  by: "process:seven-concepts-v"
  at: "2026-08-22T00:00:00Z"
status: "stable"
stale_after: "2027-08-22"
---

# OKF（开放知识格式）主题知识导航

> 本文档是项目中全部 OKF（Open Knowledge Format，开放知识格式）相关知识的**统一导航总入口**。OKF 相关知识当前散布在多个目录、横跨两套文档树与两个分类号，本文档将它们收敛到单一切入点，并按「格式规范」与「工具链」两大子域归类，附版本说明与推荐路径。

---

## 1. OKF 知识地图总览

OKF 项目知识分为两个**正交维度**，阅读前请先厘清：

| 维度 | 子域 A：OKF 格式规范 | 子域 B：OKF 工具链 |
|------|---------------------|-------------------|
| **回答的问题** | OKF「是什么」——知识该如何表示与组织 | OKF「怎么用」——如何生产/消费/校验 OKF bundle |
| **核心对象** | 规范（SPEC）、设计哲学、Bundle/Concept/Frontmatter | 工具实现（爬取→格式化→同步→校验→服务） |
| **典型读者** | 架构师、知识工程师、技术决策者 | AI 应用开发者、工具链开发者、Agent 集成者 |

> **易混淆提醒**：`okf-wiki`（讲格式规范）与 `okf-kit-wiki`（讲工具）名称相近但主体不同，后者是第三方 Python 工具 `okf-kit`（vinodborole），前者是 Google Cloud 发布的格式规范本身。

---

## 2. 子域 A：OKF 格式规范

> 权威来源为 Google Cloud 2026 年发布的 Open Knowledge Format 规范，当前目标版本 **v0.2**。

| 位置 | 内容 | 章节数 | 入口 |
|------|------|:------:|------|
| `01-agent-protocols-interfaces/okf-wiki/` | **OKF 格式规范完整教程**（设计哲学、核心概念、5 分钟快速入门、使用模式、方案对比、架构集成、FAQ、术语表） | 8 | [README](../../../.agents/docs/knowledge/learning/01-agent-protocols-interfaces/okf-wiki/README.md) |
| `01-agent-protocols-interfaces/knowledge-catalog-wiki/` | **OKF 参考实现工具链教程**（Google 官方 knowledge-catalog，含 02 章节 OKF v0.2 规范实现视角解析） | 9 | [00-overview](../../../.agents/docs/knowledge/learning/01-agent-protocols-interfaces/knowledge-catalog-wiki/00-overview.md) |
| `projects/awesome-okf-xs/` | **OKF 文档库子项目**（玄境项目「道」的载体，以 OKF bundle 组织文档/复盘/洞察/模式） | — | [README](../../../projects/awesome-okf-xs/README.md) |

---

## 3. 子域 B：OKF 工具链

> 分为第三方工具（okf-kit）与本项目自研工具（xuanspace 的 `okf`）两条脉络。

| 位置 | 内容 | 章节数 | 入口 |
|------|------|:------:|------|
| `03-agent-platforms-tools/okf-kit-wiki/` | **okf-kit 第三方工具教程**（v0.3.3，将网站转为 OKF bundle；零 Key 爬取、增量同步、Chat、MCP/HTTP 服务） | 12 | [index](03-agent-platforms-tools/okf-kit-wiki/index.md) |
| `projects/xuanspace/docs/okf/` | **本项目自研 `okf` 工具官方文档**（OKF v0.2 命令行工具链，零运行时依赖、Harness 架构） | 10 | [index](../../../projects/xuanspace/docs/okf/index.md) |
| `python314-stdlib-wiki/`（references/13 章） | **自研 `okf` 工具的 Python 3.14 标准库优化报告**（优化前后 100% 覆盖率、内存 -69.8% 等量化对比） | 2 | [13-优化报告](python314-stdlib-wiki/references/13-okf-optimization-report.md) |

---

## 4. 规范版本说明

OKF 规范当前存在两个目标版本，导航时请注意区分，避免误用旧版：

| 规范版本 | 出现在 | 状态 |
|---------|--------|------|
| **v0.1** | `okf-kit-wiki`（第三方工具当前支持） | 早期版本，仅 okf-kit 相关教程沿用 |
| **v0.2** | `okf-wiki`、`knowledge-catalog-wiki`、`projects/xuanspace/docs/okf/`、`awesome-okf-xs` | 本项目统一采用的目标版本 |

> 本项目（SpecWeave / Xuanspace）的 OKF 落地统一以 **v0.2** 为准；`okf-kit-wiki` 中涉及的 v0.1 仅为第三方工具现状说明。

---

## 5. 推荐学习路径

### 路径一：理解 OKF 是什么（30 分钟）
```
okf-wiki 00-overview → 01-core-concepts → 02-quickstart
```

### 路径二：上手生产 OKF 知识包（工具视角）
```
okf-kit-wiki 00 → 01-installation → 02-cli-reference → 03-okf-format
   → 或 自研工具 projects/xuanspace/docs/okf/quickstart
```

### 路径三：架构选型与深度集成（决策视角）
```
okf-wiki 04-limitations-and-comparison → 05-architecture-and-integration
   → knowledge-catalog-wiki（参考实现） → 自研 okf 工具架构
```

---

## 6. 相关资源（非 wiki 索引）

以下为 OKF 的工程实现与规划载体，供深入查阅时定位（非教程性质的 wiki）：

| 资源 | 路径 | 说明 |
|------|------|------|
| **OKF 源码学习知识包集合** | `docs/knowledge/learning/okf-bundles/` | 10 个自包含 OKF v0.2 知识包（TVM、tiktoken、Home Assistant、老子文献学、英语语法、veadk-python 等），concepts/examples/references 三层结构，入口 [okf-bundles/index.md](okf-bundles/index.md) |
| 自研 okf 工具源码 | `projects/xuanspace/tools/okf/` | OKF v0.2 零运行时依赖工具链实现 |
| 工具链实现规划 | `.trae/specs/okf-toolchain-implementation/` | 自研 okf 工具的 spec/tasks/checklist |
| stdlib 优化规划 | `.trae/specs/optimize-okf-python314-stdlib/` | okf 工具 Python 3.14 优化规划 |
| 导航模式沉淀规划 | `.trae/specs/okf-kit-navigation-pattern-sediment/` | okf-kit 渐进式导航洞察的模式沉淀 |

---

- [返回知识库首页](../index.md)
- [Agent 平台与工具 Wiki 索引](03-agent-platforms-tools/README.md)