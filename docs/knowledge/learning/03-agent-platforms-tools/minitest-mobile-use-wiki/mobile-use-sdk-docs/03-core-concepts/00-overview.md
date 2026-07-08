---
title: "核心概念"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/overview"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/00-overview.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "core-concepts", "architecture"]
summary: "Mobile Use SDK核心概念章节总览，介绍分层架构、Agent、任务、配置文件和Builder模式等核心组件。"
---
# 核心概念

Mobile Use SDK采用分层架构设计，既为常见用例提供简洁性，又为高级场景提供灵活性。

这些核心概念同时适用于**Platform**和**Local**两种方式。Platform通过集中管理配置文件和任务来简化配置，而本地开发让您完全控制所有组件。

## 章节导航

| 序号 | 标题 | 内容概要 | 文件 |
|---|---|---|---|
| 1 | 架构概览 | SDK分层架构、组件总览、执行流程 | [01-architecture-overview.md](01-architecture-overview.md) |
| 2 | Agent核心类 | Agent职责、生命周期、配置选项 | [02-agent.md](02-agent.md) |
| 3 | Builder模式 | 流式API配置、类型安全配置 | [03-builder-pattern.md](03-builder-pattern.md) |
| 4 | 可观测性与追踪 | 本地追踪、Platform GIF上传、调试工具 | [04-observability.md](04-observability.md) |
| 5 | Agent配置 | LLM配置、多配置文件切换、组件角色说明 | [05-agent-profiles.md](05-agent-profiles.md) |
| 6 | 任务与任务请求 | 目标定义、结构化输出、任务配置 | [06-tasks.md](06-tasks.md) |

## 核心组件概览

| 组件 | 职责 |
|---|---|
| **Agent** | 移动自动化的中央协调器，管理设备连接、服务器生命周期、任务执行 |
| **Tasks** | 基于自然语言目标的自动化工作流，支持结构化输出 |
| **Profiles** | 自定义Agent行为和LLM模型配置 |
| **Builders** | 用于配置Agent和任务的流式API |

## 架构层次

### Agent层

`Agent`类作为主要入口点，协调以下工作：
- 设备连接（Android/iOS）
- 服务器生命周期管理
- 任务创建和执行
- 资源清理

### 任务层

任务代表由以下内容定义的自动化工作流：
- **自然语言目标** - 您想要完成什么
- **结构化输出** - 使用Pydantic的类型安全结果
- **追踪** - 记录执行过程用于调试

### LangGraph集成

SDK利用[LangGraph](https://github.com/langchain-ai/langgraph)实现：
- **Agent推理** - 透明的决策过程
- **分步执行** - 将复杂任务分解为可管理的步骤
- **动态适应** - 根据屏幕内容响应

### 设备交互

两个关键组件处理设备控制：
- **Device Controller** - 使用原生平台工具执行物理操作
  - **Android**：使用ADB（Android Debug Bridge）配合UIAutomator2
  - **iOS**：使用IDB（iOS Development Bridge）控制模拟器和设备

---

> **学习路径**：建议从[架构概览](01-architecture-overview.md)开始，了解整体架构设计。
