---
okf_version: "0.2"
type: Index
title: OKF 生态系统知识包
description: OKF（Open Knowledge Format）生态——Bundle 数据模型、爬取构建流水线、增量同步与桌面阅读器
tags: [okf, knowledge-format, bundle, cli, desktop]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
stale_after: 2027-08-23
---

# OKF 生态系统知识包

本知识包（bundle）系统梳理 OKF（Open Knowledge Format）生态系统的架构与实现，涵盖 okf-kit（Python CLI 核心，版本 0.3.3）与 okf-desktop（桌面阅读器，版本 0.1.0）两个项目。内容包括 Bundle 数据模型、网站爬取构建流水线、增量同步机制、MCP/Chat/HTTP 三模服务架构、桌面同进程打包等核心概念，遵循 OKF v0.2 规范。

## 目录分组

* [concepts/](concepts/index.md) - 核心概念：6 篇概念文档，按编号排列，覆盖从数据模型到服务架构到桌面打包的完整知识体系
  * [OKF 知识包生态概览](concepts/00-okf-overview.md)
  * [Bundle 数据模型与语义边](concepts/01-bundle-data-model.md)
  * [网站爬取与 Bundle 构建流水线](concepts/02-crawl-build-pipeline.md)
  * [增量同步与安全阀门](concepts/03-sync-incremental.md)
  * [MCP/Chat/HTTP 三模服务架构](concepts/04-service-modes.md)
  * [桌面应用同进程架构与打包](concepts/05-desktop-architecture.md)
* [examples/](examples/index.md) - 使用示例：CLI 命令实际用法
  * [CLI 命令使用示例](examples/cli-usage.md)
* [references/](references/index.md) - 信源登记簿：5 篇信源文件，含 R 阶段事实清单、I 阶段洞察与源码登记
  * [okf-kit 事实清单](references/facts-okf-kit.md)
  * [okf-desktop 事实清单](references/facts-okf-desktop.md)
  * [架构洞察](references/insights.md)
  * [okf-kit 源码](references/okf-kit-source.md)
  * [okf-desktop 源码](references/okf-desktop-source.md)
