---
title: "SDK 参考"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "sdk", "reference", "api"]
summary: "Mobile Use SDK 完整 API 参考文档，包含核心类、Builder、类型定义和异常处理。"
---

# SDK 参考

本章提供 Mobile Use SDK 的完整 API 参考文档，详细介绍所有核心类、配置选项、数据类型和异常类。

## 参考章节

| 章节 | 说明 | 文件 |
|------|------|------|
| Agent 类 | SDK 的主入口点，负责设备管理和任务执行 | [01-agent-class.md](01-agent-class.md) |
| AgentConfigBuilder | 用于配置 Agent 行为的流式 Builder | [02-agent-config-builder.md](02-agent-config-builder.md) |
| TaskRequestBuilder | 用于配置任务请求的流式 Builder | [03-task-request-builder.md](03-task-request-builder.md) |
| 类型定义 | 核心类型和数据结构参考 | [04-types.md](04-types.md) |
| 异常处理 | SDK 异常类层次结构和处理指南 | [05-exceptions.md](05-exceptions.md) |

## 快速导入参考

```python
# 核心类
from minitap.mobile_use.sdk import Agent

# Builder
from minitap.mobile_use.sdk.builders import Builders

# 类型
from minitap.mobile_use.sdk.types import (
    AgentProfile,
    TaskRequest,
    PlatformTaskRequest,
    AgentConfig,
    DevicePlatform,
    ServerConfig,
)

# 配置类
from minitap.mobile_use.config import (
    LLM,
    LLMConfig,
    LLMConfigUtils,
    LLMWithFallback,
)

# 异常
from minitap.mobile_use.sdk.types.exceptions import (
    MobileUseError,
    AgentError,
    AgentNotInitializedError,
    AgentProfileNotFoundError,
    AgentTaskRequestError,
    AgentInvalidApiKeyError,
    DeviceError,
    DeviceNotFoundError,
    ServerError,
    ServerStartupError,
    ExecutableNotFoundError,
    PlatformServiceUninitializedError,
    PlatformServiceError,
)
```

## 命名空间概览

| 模块 | 用途 |
|------|------|
| `minitap.mobile_use.sdk` | SDK 主入口，包含 `Agent` 类 |
| `minitap.mobile_use.sdk.builders` | Builder 模式类，用于流式配置 |
| `minitap.mobile_use.sdk.types` | 核心数据类型和结构 |
| `minitap.mobile_use.sdk.types.exceptions` | 异常类定义 |
| `minitap.mobile_use.config` | LLM 配置相关类 |
