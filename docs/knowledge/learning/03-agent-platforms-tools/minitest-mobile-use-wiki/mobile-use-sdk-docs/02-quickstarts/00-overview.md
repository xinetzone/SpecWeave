---
title: "快速开始"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/quickstart"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/00-overview.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "quickstart", "getting-started"]
summary: "Mobile Use SDK快速开始章节总览，包含本地开发、平台模式、云设备、BrowserStack和iOS真机等多种使用方式的入门指南。"
---
# 快速开始

本章节提供多种使用Mobile Use SDK的快速入门指南，根据您的需求选择合适的方式开始。

## 章节导航

| 序号 | 标题 | 内容概要 | 文件 |
|---|---|---|---|
| 1 | 本地快速开始 | 本地开发环境配置，LLM配置文件设置，完全控制执行环境 | [01-local-quickstart.md](01-local-quickstart.md) |
| 2 | 平台快速开始 | 使用Minitap平台，无需LLM配置文件，内置可观测性 | [02-platform-quickstart.md](02-platform-quickstart.md) |
| 3 | 云设备快速开始 | 使用Minitap托管的云Android设备，零本地设置 | [03-cloud-quickstart.md](03-cloud-quickstart.md) |
| 4 | BrowserStack快速开始 | 使用BrowserStack真实iOS云设备进行自动化 | [04-browserstack-quickstart.md](04-browserstack-quickstart.md) |
| 5 | iOS真机设置 | USB连接的物理iOS设备配置（WebDriverAgent） | [05-physical-ios-setup.md](05-physical-ios-setup.md) |

## 方式对比

| 方式 | 设置难度 | 设备类型 | LLM配置 | 适用场景 |
|---|---|---|---|---|
| 本地开发 | 中等 | 本地设备/模拟器 | 自行配置 | 开发调试、完全控制 |
| 平台模式 | 简单 | 本地设备 | 平台管理 | 快速上手、团队协作 |
| 云设备 | 极简 | Minitap云Android | 平台管理 | 零配置、按需使用 |
| BrowserStack | 中等 | BrowserStack云iOS | 平台管理 | iOS真机测试、CI/CD |
| iOS真机 | 复杂 | USB连接iOS | 自行配置 | iOS真机调试 |

## 推荐路径

- **🚀 新手推荐**：从[平台快速开始](02-platform-quickstart.md)入手，无需配置LLM，几分钟即可运行第一个任务
- **💻 本地开发者**：选择[本地快速开始](01-local-quickstart.md)，完全控制LLM和执行环境
- **☁️ 不想配置设备**：使用[云设备快速开始](03-cloud-quickstart.md)，无需本地设备
- **📱 iOS真机测试**：参考[iOS真机设置](05-physical-ios-setup.md)或[BrowserStack快速开始](04-browserstack-quickstart.md)

---

> **推荐新手**：[平台快速开始 →](02-platform-quickstart.md)（设置最快，内置可观测性）
