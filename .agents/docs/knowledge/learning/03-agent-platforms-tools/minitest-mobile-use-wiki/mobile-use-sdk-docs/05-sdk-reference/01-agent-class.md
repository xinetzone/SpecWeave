---
title: "Agent 类"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/01-agent-class.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "sdk", "agent", "api"]
summary: "Agent 类是 mobile-use SDK 的主入口点，负责管理设备交互和执行任务。"
---
# Agent 类

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent

`Agent` 类是 mobile-use SDK 的主入口点，负责管理设备交互和执行任务。

## 导入

```python
from minitap.mobile_use.sdk import Agent
```

## 构造函数

```python
Agent(config: AgentConfig | None = None)
```

### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `config` | `AgentConfig` | 自定义 Agent 配置。如果未提供，使用默认配置。 |

### 示例

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile

# 使用默认配置
agent = Agent()

# 使用自定义配置
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

## 方法

### init

通过连接设备并启动所需服务来初始化 Agent。

```python
async def init(
    self,
    api_key: str | None = None,
    server_restart_attempts: int = 3,
    retry_count: int = 5,
    retry_wait_seconds: int = 5,
) -> bool
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `api_key` | `str` | `None` | 用于平台功能（平台任务、云设备）的 Minitap API Key。也可通过 `MINITAP_API_KEY` 环境变量设置。 |
| `server_restart_attempts` | `int` | `3` | 服务器启动失败时的最大重试次数 |
| `retry_count` | `int` | `5` | API 调用的重试次数 |
| `retry_wait_seconds` | `int` | `5` | 重试之间等待的秒数 |

#### 返回值

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `success` | `bool` | 初始化成功返回 `True`，否则返回 `False` |

#### 示例

```python
import asyncio

async def main():
    agent = Agent()

    # 不使用 API Key 初始化（仅本地模式）
    if not await agent.init():
        print("Failed to initialize agent")
        exit(1)

    print("Agent initialized successfully")

asyncio.run(main())
```

#### 使用 API Key 的示例

```python
import asyncio

async def main():
    agent = Agent()

    # 使用 API Key 初始化以支持平台功能
    if not await agent.init(api_key="your-minitap-api-key"):
        print("Failed to initialize agent")
        exit(1)

    print("Agent initialized successfully with Platform support")

asyncio.run(main())
```

> **重要**：在运行任务之前始终检查 `init()` 的返回值。注意 `init()` 现在是异步方法，必须使用 await 调用。

---

### run_task

异步执行移动自动化任务。

```python
async def run_task(
    self,
    *,
    goal: str | None = None,
    output: type[TOutput] | str | None = None,
    profile: str | AgentProfile | None = None,
    name: str | None = None,
    request: TaskRequest[TOutput] | PlatformTaskRequest[TOutput] | None = None,
) -> str | dict | TOutput | None
```

#### 参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `goal` | `str` | 要完成的任务的自然语言描述 |
| `output` | `type[TOutput] \| str` | 输出类型：Pydantic 模型类用于结构化输出，字符串描述用于输出格式 |
| `profile` | `str \| AgentProfile` | 要使用的 Agent Profile（名称或实例） |
| `name` | `str` | 任务的可选名称（用于日志/调试） |
| `request` | `TaskRequest[TOutput] \| PlatformTaskRequest[TOutput]` | 预构建的 TaskRequest 或 PlatformTaskRequest（替代单独参数） |

#### 返回值

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `result` | `str \| dict \| TOutput \| None` | 任务结果：`str`（简单文本输出）、`dict`（非结构化字典）、`TOutput`（指定的 Pydantic 模型实例）、`None`（任务失败或无输出） |

#### 示例

```python
result = await agent.run_task(
    goal="Open calculator and compute 5 * 7"
)
print(result)  # 字符串输出
```

> **注意**：对于平台任务，**Locked App Package** 在平台任务本身上配置，不在 `PlatformTaskRequest` 中。对于使用 `TaskRequest` 的本地任务，在 Builder 中使用 `.with_locked_app_package()`。

---

### new_task

创建新的任务请求 Builder 用于流式任务配置。

```python
def new_task(self, goal: str) -> TaskRequestBuilder[None]
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `goal` | `str` | 是 | 要完成的任务的自然语言描述 |

#### 返回值

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `builder` | `TaskRequestBuilder[None]` | 用于流式配置的 TaskRequestBuilder 实例 |

#### 示例

```python
from pathlib import Path

task = (
    agent.new_task("Open Gmail and count unread emails")
    .with_name("email_count")
    .with_max_steps(400)
    .with_trace_recording(enabled=True, path=Path("/tmp/traces"))
    .build()
)

result = await agent.run_task(request=task)
```

---

### clean

清理资源、停止服务器并重置 Agent 状态。

```python
async def clean(self, force: bool = False) -> None
```

#### 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `force` | `bool` | `False` | 设置为 `True` 以清理僵尸/预先存在的 mobile-use 服务器 |

#### 示例

```python
import asyncio

async def main():
    agent = Agent()

    try:
        await agent.init()
        await agent.run_task(goal="Some task")
    finally:
        await agent.clean()  # 始终清理

asyncio.run(main())
```

如果有之前运行留下的僵尸服务器，使用 `force=True`：

```python
await agent.clean(force=True)  # 终止任何现有服务器
await agent.init()              # 重新启动
```

> **注意**：`clean()` 现在是异步方法，必须使用 await 调用。

---

### install_apk

在连接的 Android 设备上安装 APK。

```python
async def install_apk(self, apk_path: str | Path) -> None
```

此方法同时支持本地设备和云设备：

- **本地设备**：使用 ADB 直接安装 APK
- **云设备**：通过 API 在云设备上安装

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `apk_path` | `str \| Path` | 是 | 要安装的本地 APK 文件路径 |

#### 异常

- `FileNotFoundError`：APK 文件不存在
- `AgentNotInitializedError`：Agent 未初始化（本地模式）
- `AgentError`：设备不是 Android 设备或 ADB 客户端未初始化
- `CloudMobileServiceUninitializedError`：云移动服务未初始化（云模式）
- `AgentTaskRequestError`：云移动 ID 未配置（云模式）

> **注意**：APK 安装仅支持 Android 设备。尝试在 iOS 设备上安装 APK 将引发 `AgentError`。
>
> 对于云设备，APK 必须是 **x86_64 兼容**的。
>
> 对于云设备，`install_apk` 方法会在云设备未运行时自动启动，因此无需在安装前手动启动。

---

### get_screenshot

从移动设备捕获屏幕截图。

```python
async def get_screenshot(self) -> Image.Image
```

此方法同时支持本地设备和云设备：

- **本地设备**：使用 ADB（Android）或 xcrun（iOS）直接捕获屏幕截图
- **云设备**：通过平台 API 从云设备获取屏幕截图

#### 返回值

| 返回值 | 类型 | 说明 |
|--------|------|------|
| `screenshot` | `Image.Image` | 作为 PIL Image 对象的屏幕截图 |

#### 异常

- `AgentNotInitializedError`：Agent 未初始化
- `CloudMobileServiceUninitializedError`：未正确初始化使用云设备
- `Exception`：屏幕截图捕获失败

#### 示例

```python
import asyncio
from minitap.mobile_use.sdk import Agent

async def main():
    agent = Agent()

    try:
        await agent.init()

        # 捕获屏幕截图
        screenshot = await agent.get_screenshot()

        # 保存屏幕截图
        screenshot.save("device_screenshot.png")
        print("Screenshot saved!")

    finally:
        await agent.clean()

asyncio.run(main())
```

#### 云设备示例

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    # 配置云设备
    config = Builders.AgentConfig.for_cloud_mobile("my-cloud-device").build()
    agent = Agent(config=config)

    try:
        await agent.init(api_key="your-minitap-api-key")

        # 从云设备捕获屏幕截图
        screenshot = await agent.get_screenshot()
        screenshot.save("cloud_device_screenshot.png")

    finally:
        await agent.clean()

asyncio.run(main())
```

在自动化工作流中使用 `get_screenshot()` 进行调试、监控或从移动设备提取视觉数据。

## 完整示例

```python
import asyncio
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

class WeatherInfo(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition")

async def main():
    # 配置 Agent
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)

    try:
        # 初始化
        if not await agent.init():
            print("Failed to initialize")
            return

        # 使用结构化输出运行任务
        weather = await agent.run_task(
            goal="Open weather app and check current temperature",
            output=WeatherInfo,
            name="weather_check"
        )

        if weather:
            print(f"Temperature: {weather.temperature}°C")
            print(f"Condition: {weather.condition}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## 异常处理

Agent 可能引发以下异常：

- `AgentNotInitializedError`：在初始化前调用 Agent 方法
- `DeviceNotFoundError`：未找到设备或设备断开连接
- `AgentProfileNotFoundError`：指定的 Profile 未找到
- `ServerStartupError`：启动所需服务器失败
- `ExecutableNotFoundError`：未找到所需的可执行文件（adb、idb、xcrun）
- `AgentTaskRequestError`：无效的任务请求配置
- `PlatformServiceUninitializedError`：平台服务未初始化（缺少 API Key）
- `CloudMobileServiceUninitializedError`：云移动服务未初始化（缺少 API Key 或云设备未配置）
- `AgentInvalidApiKeyError`：无效的 Minitap API Key

详见 [异常处理](05-exceptions.md)。

## 下一步

- **Task Request Builder**：使用 Builder 模式配置任务
- **Agent Config Builder**：配置 Agent 行为
