---
title: "SDK介绍"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/introduction"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/01-introduction-installation/01-introduction.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "introduction", "sdk"]
summary: "Mobile Use SDK基本介绍，了解SDK的核心功能和用途。"
---
# SDK介绍

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/introduction

Mobile Use SDK是一个由Minitap提供的移动端自动化SDK，它允许开发者使用自然语言指令控制Android和iOS设备，实现智能化的移动应用自动化操作。

## 核心特性

- **自然语言驱动**：使用自然语言描述任务目标，无需编写复杂的UI自动化脚本
- **多平台支持**：支持Android和iOS双平台，包括物理设备、模拟器和云设备
- **结构化输出**：通过Pydantic模型获取类型安全的结构化结果
- **多Agent架构**：采用多Agent协作架构（Planner、Cortex、Executor等），实现智能决策
- **可观测性**：内置执行追踪功能，支持GIF录制和平台可视化
- **灵活部署**：支持本地部署、Minitap平台部署、云设备和BrowserStack等多种运行方式

## 主要使用方式

| 使用方式 | 说明 | 适用场景 |
|---|---|---|
| 本地开发 | 完全控制LLM配置，本地设备连接 | 开发调试、自定义环境 |
| 平台模式 | 云端管理任务和LLM配置 | 团队协作、快速上手 |
| 云设备 | Minitap托管的虚拟Android设备 | 零配置、按需使用 |
| BrowserStack | BrowserStack真实iOS云设备 | iOS真机测试、CI/CD |

## 下一步

完成SDK介绍后，请继续阅读[安装指南](02-installation.md)了解如何配置开发环境。
