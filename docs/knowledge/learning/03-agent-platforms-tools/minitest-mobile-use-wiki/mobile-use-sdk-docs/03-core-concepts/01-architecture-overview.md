---
title: "架构概览"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/overview"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "architecture", "langgraph"]
summary: "Mobile Use SDK分层架构详解，包括Agent层、任务层、LangGraph集成和设备交互层的设计。"
---
# 架构概览

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/overview

Mobile Use SDK采用分层架构设计，既为常见用例提供简洁性，又为高级场景提供灵活性。核心概念同时适用于**Platform**和**Local**两种模式。

## 关键组件

| 组件 | 描述 |
|---|---|
| **Agent** | 移动自动化的中央协调器 |
| **Tasks** | 基于目标的自动化工作流，支持结构化输出 |
| **Profiles** | 自定义Agent行为和LLM配置 |
| **Builders** | 用于配置Agent和任务的流式API |

---

## 组件概览

### Agent层

`Agent`类是主要入口点，协调以下工作：

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
- **动态适应** - 根据屏幕上的内容响应

### 设备交互

两个关键组件处理设备控制：

**Device Controller**

使用原生平台工具在设备上执行物理操作：

- **Android**：使用ADB（Android Debug Bridge）配合UIAutomator2实现可靠的UI自动化
- **iOS**：使用IDB（iOS Development Bridge）控制模拟器和设备

功能包括：

- 点击、滑动、滚动手势
- 应用启动和导航
- 按键事件
- 文本输入

---

## 多Agent架构

Mobile Use SDK采用多Agent架构，每个Agent组件负责特定职责：

| Agent组件 | 职责 | 模型要求 |
|---|---|---|
| **Planner** | 将自然语言目标分解为高级子目标 | 快速推理模型 |
| **Orchestrator** | 协调执行流程，管理状态转换 | 快速决策模型 |
| **Contextor** | 收集设备上下文，执行应用锁约束 | 快速文本模型 |
| **Cortex** | 高级推理和决策（系统的"眼睛"） | **需要视觉能力** |
| **Executor** | 将决策转换为具体设备操作 | 指令遵循模型 |
| **Utils - Hopper** | 从大量数据中提取相关信息 | 大上下文窗口（256k+） |
| **Utils - Outputter** | 提取结构化输出 | 结构化输出能力 |
| **Utils - Video Analyzer** | 分析视频内容（可选） | Gemini视频模型 |

---

## 执行流程

典型的任务执行流程如下：

1. **初始化**：Agent连接设备，启动Device Controller服务器
2. **规划**：Planner将目标分解为子目标
3. **执行循环**：
   - Orchestrator决定下一步
   - Cortex分析截图和UI层次结构，做出决策
   - Executor将决策转换为设备操作
   - Device Controller执行操作
   - 捕获新的截图，循环继续
4. **输出**：任务完成后，Outputter提取结构化结果
5. **清理**：Agent释放资源

---

## Platform vs Local架构对比

| 方面 | Platform模式 | Local模式 |
|---|---|---|
| LLM配置 | Platform集中管理 | 本地配置文件 |
| 任务定义 | Platform UI管理 | 代码中定义 |
| 可观测性 | 内置Platform追踪 | 本地追踪文件 |
| API密钥管理 | Platform统一管理 | 用户自行配置 |
| 模型访问 | OpenRouter所有模型 | 用户自行配置提供商 |

---

## 下一步

- [Agent核心类](02-agent.md) - 了解Agent类的详细用法
- [Agent配置](05-agent-profiles.md) - 学习如何配置LLM模型
- [任务与任务请求](06-tasks.md) - 深入了解任务定义
