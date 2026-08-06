---
id: okf-ecosystem-infrastructure-index
title: "OKF 生态基建知识"
version: "1.0"
source: "四个 OKF 相关文件夹系统学习（R→I→E→V→C 知识沉淀）"
type: "Wiki Tutorial"
description: "OKF 生态基建层系统知识：生态资源图谱、bundle 分发注册机制、bundle 工程化发布模板"
tags: ["OKF", "生态基建", "ecosystem", "bundle", "registry", "template", "okf-kit"]
category: "learning"
date: "2026-08-06"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "OKF 生态的消费/发布/工程化全链路知识：上游生态图谱、分发注册机制、工程化模板，以及如何上手 okf-kit 工具链"
last_verified: "2026-08-06"
wiki_version: "1.0"
okf_version_target: "v0.1/v0.2"
---

# OKF 生态基建知识

> 本系列系统沉淀 OKF 生态的**基建层**知识，回答三个问题：**OKF 有哪些资源？如何消费现成 bundle？如何把网站发布为自更新 bundle？**

## 🎯 本系列定位

okf-wiki 主教程（00-07）覆盖 OKF **规范层**（格式、概念、用法），knowledge-catalog-wiki 覆盖官方**工具链层**，awesome-okf-analysis 覆盖中文生态**项目实践**。本系列补充的是介于规范与项目之间的**生态基建层**——让 OKF 从"一门格式"变成"一个可用的生态"的机制与工具。

| 系列 | 覆盖 | 关键词 |
|------|------|--------|
| okf-wiki 主教程 | OKF v0.2 规范 | 格式、概念、快速入门 |
| knowledge-catalog-wiki | 官方工具链 | Reference Agent、enrichment、mdcode |
| awesome-okf-analysis | 中文项目实践 | producer 插件、Skill、扩展提案 |
| **本系列（生态基建）** | **生态资源 + 分发 + 工程化** | **图谱、registry、template、okf-kit** |

## 📄 文档索引（3篇）

| 文档 | 说明 | 标签 |
|------|------|------|
| [01 OKF 生态资源图谱](01-ecosystem-map.md) | 上游 awesome-okf 生态九大分类、官方/社区工具清单、`build-okf-bundle.mjs` 批转实现原理（dogfooding） | `OKF` `ecosystem` `build-okf-bundle` |
| [02 OKF Bundle 分发注册机制](02-bundle-registry.md) | `registry.yaml` 字段 Schema、`okf get` 消费流程、`validate_registry.py` 校验规则、发布与许可政策 | `OKF` `bundle` `registry` |
| [03 OKF Bundle 工程化模板](03-bundle-template.md) | `build.yml`/`sync.yml` 两个 GitHub Actions 工作流、okf-kit CLI 命令速查、NOTICE.md 许可 | `OKF` `template` `github-actions` |

## 📖 阅读建议

- **想知道 OKF 生态有哪些资源** → [01 生态资源图谱](01-ecosystem-map.md)
- **想直接用现成知识库对话** → [02 分发注册机制](02-bundle-registry.md)（`okf get <name>` + `okf chat`）
- **想把自己的网站发布成 OKF bundle** → [03 工程化模板](03-bundle-template.md)
- **想完整理解生态全链路** → 建议按 01 → 02 → 03 顺序阅读

## 🔗 相关资源

- [📚 OKF 开放知识格式完整指南](../README.md) - OKF 规范层主教程
- [🛠️ Knowledge Catalog 工具链](../../knowledge-catalog-wiki/README.md) - 官方参考实现与工具链
- [📊 Awesome OKF 深度案例分析](../awesome-okf-analysis/README.md) - 中文生态项目实践
- [🏠 返回上级：Agent协议与接口技术栈](../README.md)
- [🏠 知识库首页](../../../../README.md)