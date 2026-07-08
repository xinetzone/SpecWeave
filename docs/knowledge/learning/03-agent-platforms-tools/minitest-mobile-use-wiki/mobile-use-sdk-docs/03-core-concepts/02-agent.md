---
title: "Agent核心类"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/agent"
x-toml-ref: "../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/03-core-concepts/02-agent.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "agent", "sdk"]
summary: "Agent类详解，作为SDK的主要入口点，负责设备管理、服务器生命周期、任务执行和资源清理。"
---
# Agent核心类

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/agent

`Agent`类是SDK的主要入口点。它协调移动自动化所需的所有组件。

## 职责

### 设备管理
初始化和管理与Android/iOS设备的连接

### 服务器生命周期
启动和停止Device Controller服务器

### 任务执行
创建和执行自动化任务

### 资源清理
处理适当的清理和资源释放

---

## 基本用法

### 创建Agent

**Platform模式：**

使用Platform时，只需创建agent即可 - 无需配置：

```python
from minitap.mobile_use.sdk import Agent

# 创建agent（从环境变量使用MINITAP_API_KEY）
agent = Agent()
```

所有配置文件和任务配置都在[platform.mobile-use.ai](https://platform.mobile-use.ai/)上管理。

**本地开发模式：**

对于本地开发，使用配置文件配置agent：

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile

# 从配置文件创建配置文件
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

# 配置agent
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

### Agent生命周期

Agent生命周期包含三个阶段：
1. **创建**：实例化Agent对象
2. **初始化**：调用`init()`连接设备、启动服务器
3. **清理**：调用`clean()`释放资源

---

## 配置选项

可以使用`AgentConfigBuilder`配置agent：

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile, DevicePlatform

# 创建配置文件
default_profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

# 配置agent
config = (
    Builders.AgentConfig
    .with_default_profile(default_profile)
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .build()
)

agent = Agent(config=config)
```

## 初始化选项

`init()`方法接受多个参数以实现健壮的初始化：

```python
agent.init(
    server_restart_attempts=3,  # 服务器启动失败时的重试次数
    retry_count=5,              # API调用重试次数
    retry_wait_seconds=5        # 重试间隔秒数
)
```

如果之前的运行存在僵尸服务器，请在初始化前使用`agent.clean(force=True)`。

## 设备选择

默认情况下，agent连接到第一个可用设备。您可以显式指定设备：

```python
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(
        platform=DevicePlatform.ANDROID,
        device_id="your_device_id"
    )
    .build()
)
```

如何查找设备ID：

```shellscript
# Android
adb devices

# iOS
idevice_id -l
```

## 服务器配置

Agent管理处理所有设备交互的Device Controller服务器：

**Device Controller服务器**

使用原生平台工具执行设备操作并捕获屏幕状态：

- **Android**：使用ADB（Android Debug Bridge）配合UIAutomator2进行UI自动化
- **iOS**：使用IDB（iOS Development Bridge）控制模拟器和设备

功能包括：

- 截图和UI层次结构捕获
- 点击、滑动、滚动手势
- 应用启动和导航
- 按键事件和文本输入

---

## 完整示例

### Platform模式

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

async def main():
    # 创建agent（从.env使用MINITAP_API_KEY）
    agent = Agent()
    
    try:
        # 初始化
        if not agent.init():
            print("Failed to initialize agent")
            return
        
        # 运行platform任务（在platform.mobile-use.ai上配置）
        result = await agent.run_task(
            request=PlatformTaskRequest(task="check-notifications")
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 始终清理
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

### 本地模式

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

async def main():
    # 使用本地配置文件配置agent
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)
    
    try:
        # 初始化
        if not agent.init():
            print("Failed to initialize agent")
            return
        
        # 运行本地任务
        result = await agent.run_task(
            goal="Check my notifications",
            name="check_notifications"
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 始终清理
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 最佳实践

### 始终使用try-finally

即使发生错误，也要确保调用`agent.clean()`

```python
try:
    agent.init()
    await agent.run_task(...)
finally:
    agent.clean()
```

### 处理初始化失败

检查`init()`的返回值

```python
if not agent.init():
    print("Failed to initialize")
    return
```

### 使用上下文管理器

考虑使用上下文管理器包装以自动清理

---

## 下一步

- [任务与任务请求](06-tasks.md) - 了解任务创建和执行
- [SDK参考 - Agent类](../05-sdk-reference/01-agent-class.md) - 详细的Agent SDK文档
- [Builder模式](03-builder-pattern.md) - 学习流式配置API
