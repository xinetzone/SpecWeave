---
okf_version: "0.2"
type: Index
title: Tuya IoT 知识包
description: TuyaOpen 跨平台 IoT SDK——TAL/TKL 双层抽象、组件化构建、全栈 IoT 能力与 AI 开发技能
tags: [tuya, iot, embedded, tal, sdk, smart-home]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
stale_after: 2027-08-23
---

# Tuya IoT 知识包

本知识包（bundle）系统梳理 TuyaOpen 跨平台 IoT SDK 及其生态的架构与实现，涵盖 TAL/TKL 双层抽象、Kconfig+CMake 组件化构建、全栈 IoT 能力（系统服务/网络/安全/存储/P2P/AI）、BSP 板级支持、13 类外设驱动、10 个 AI 开发技能、OpenClaw 云 API 与 Home Assistant 集成。TuyaOpen 支持 T2/T3/T5AI/ESP32/LN882H/BK7231N/GD32/Linux 共 8 款芯片平台，是面向下一代 AI-agent 硬件的 C/C++ SDK。内容遵循 OKF v0.2 规范。

## 目录分组

* [concepts/](concepts/) - 核心概念：15 篇概念文档，分两批排列，覆盖从架构基础到应用生态的完整知识体系
  * [TuyaOpen IoT 框架概览](concepts/00-overview.md)
  * [TAL 抽象层架构](concepts/01-tal-architecture.md)
  * [系统服务](concepts/02-system-services.md)
  * [网络栈](concepts/03-network-stack.md)
  * [安全与 KV 存储](concepts/04-security-kv.md)
  * [第三方库集成](concepts/05-third-party-libs.md)
  * [构建系统](concepts/06-build-system.md)
  * [P2P 通信](concepts/07-p2p-communication.md)
  * [AI 组件](concepts/08-ai-components.md)
  * [BSP 板级支持](concepts/09-board-support.md)
  * [外设驱动](concepts/10-peripherals.md)
  * [AI 开发技能体系](concepts/11-dev-skills.md)
  * [OpenClaw 云 API](concepts/12-openclaw-api.md)
  * [Home Assistant 集成](concepts/13-ha-integration.md)
  * [IoT 开发完整工作流](concepts/14-iot-workflow.md)
* [examples/](examples/) - 使用示例：固件项目完整创建示例
  * [TuyaOpen 固件快速入门](examples/firmware-quickstart.md)
* [references/](references/) - 信源登记簿：5 篇信源文件，含 R 阶段事实清单、I 阶段洞察与源码登记
  * [TuyaOpen 核心框架事实清单](references/facts-tuyaopen-core.md)
  * [TuyaOpen 技能与生态事实清单](references/facts-tuya-skills-ecosystem.md)
  * [架构洞察](references/insights.md)
  * [TuyaOpen 核心框架源码](references/tuyaopen-core-source.md)
  * [TuyaOpen 技能与生态源码](references/tuya-skills-source.md)
