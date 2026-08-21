---
title: "云设备快速开始"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/cloud-quickstart"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/02-quickstarts/03-cloud-quickstart.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "quickstart", "cloud-devices"]
summary: "Minitap云设备快速开始指南，使用托管的虚拟Android设备，零本地设置，所有智能体逻辑在云端运行。"
---
# 云设备快速开始

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/cloud-quickstart

本指南介绍使用**云手机**（Minitap平台托管的虚拟设备），所有智能体逻辑均在云端运行。

**想要使用本地设备？** 请查看[本地快速开始](01-local-quickstart.md)了解如何使用自己的设备进行设置。

## 什么是云手机？

云手机是Minitap平台托管的虚拟Android设备。主要优势：

### 零本地设置

无需ADB、idb或本地服务器

### 持久化状态

设备状态在重启和会话之间保持不变

### 随时可用

设备按需就绪，无需维护

### 集中监控

通过Minitap平台内置可观测性

---

## 前置条件

新用户可获得**10美元免费额度**开始使用！

**当前可用性**：目前仅提供Android v11（API级别30）云设备。iOS支持暂不可用。

---

## 创建您的第一个云手机自动化

让我们编写一个简单的脚本，在云手机上运行任务。

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import PlatformTaskRequest

async def main():
    # 配置云手机Agent
    config = (
        Builders.AgentConfig
        .for_cloud_mobile("my-test-device")  # 或使用UUID
        .build()
    )

    agent = Agent(config=config)

    try:
        # 使用API密钥初始化
        await agent.init(api_key="your-minitap-api-key")

        # 创建Platform任务请求
        task_request = PlatformTaskRequest(
            task="calculator-demo",  # Platform中定义的任务
        )

        # 在云手机上运行任务
        result = await agent.run_task(request=task_request)
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

### 与本地模式有何不同？

**配置方式**

使用`.for_cloud_mobile()`替代`.for_device()`：

```python
# 云手机
config = Builders.AgentConfig.for_cloud_mobile("my-device").build()

# 本地设备
config = Builders.AgentConfig.for_device(DevicePlatform.ANDROID, "emulator-5554").build()
```

**需要API密钥**

将API密钥传递给`init()`或设置`MINITAP_API_KEY`环境变量：

```python
# 方式1：直接传递
await agent.init(api_key="your-key")

# 方式2：环境变量
# export MINITAP_API_KEY=your-key
await agent.init()
```

**仅支持Platform任务**

云手机仅支持`PlatformTaskRequest`（不支持直接的`goal`参数）：

```python
# ✅ 支持 - 预配置任务
request = PlatformTaskRequest(task="my-task")
await agent.run_task(request=request)

# ✅ 支持 - 使用ManualTaskConfig的一次性任务
from minitap.mobile_use.sdk.types import PlatformTaskRequest, ManualTaskConfig

task = ManualTaskConfig(
    goal="Open calculator and compute 5 * 7",
    output_description="The calculation result"
)
request = PlatformTaskRequest(task=task, profile="default")
await agent.run_task(request=request)

# ❌ 不支持 - 直接goal参数
await agent.run_task(goal="Do something")  # 将引发错误
```

使用`ManualTaskConfig`可以在Platform中无需预配置即可运行一次性任务！

**无需本地服务器**

无需ADB、idb或本地设备设置。一切都在云端运行！

---

## 如何在Platform中创建云手机

使用引用名称便于识别：`my-test-device`比`550e8400-e29b-41d4-a716-446655440000`更容易记住！

---

## 使用ManualTaskConfig运行一次性任务

您可以使用`ManualTaskConfig`在云手机上运行一次性任务，无需在Platform中预配置：

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import PlatformTaskRequest, ManualTaskConfig

async def main():
    # 配置云手机
    config = (
        Builders.AgentConfig
        .for_cloud_mobile("my-device")
        .build()
    )

    agent = Agent(config=config)

    try:
        # 使用API密钥初始化
        await agent.init(api_key="your-minitap-api-key")

        # 使用ManualTaskConfig创建一次性任务
        task = ManualTaskConfig(
            goal="Open the calculator app, calculate 123 * 456, and tell me the result",
            output_description="The calculation result as a number"
        )

        # 运行任务
        result = await agent.run_task(
            request=PlatformTaskRequest(
                task=task,
                profile="default"  # Platform中定义的LLM配置文件
            )
        )

        print(f"Result: {result}")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

`ManualTaskConfig`非常适合一次性任务或快速测试，无需先在Platform中创建任务！

---

## 带结构化输出的完整示例

以下是一个更完整的示例，使用`ManualTaskConfig`进行结构化输出：

```python
import asyncio
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import PlatformTaskRequest, ManualTaskConfig

class WeatherInfo(BaseModel):
    temperature: float = Field(..., description="Temperature in Celsius")
    condition: str = Field(..., description="Weather condition")
    location: str = Field(..., description="Location name")

async def main():
    # 配置云手机
    config = (
        Builders.AgentConfig
        .for_cloud_mobile("my-weather-device")
        .build()
    )

    agent = Agent(config=config)

    try:
        # 从环境变量或直接初始化API密钥
        await agent.init(api_key="your-minitap-api-key")

        # 定义带结构化输出的一次性任务
        task = ManualTaskConfig(
            goal="Open the weather app and check the current temperature",
            output_description="Extract temperature, weather condition, and location"
        )

        # 创建带结构化输出的请求
        task_request = PlatformTaskRequest(
            task=task,
            profile="default"  # Platform中定义的LLM配置文件
        )

        # 在云手机上运行
        weather = await agent.run_task(request=task_request)

        if weather:
            print(f"Location: {weather['location']}")
            print(f"Temperature: {weather['temperature']}°C")
            print(f"Condition: {weather['condition']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 安装自定义APK

您可以使用`install_apk()`方法在云手机上安装自己的APK文件：

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    config = Builders.AgentConfig.for_cloud_mobile("my-device").build()
    agent = Agent(config=config)

    try:
        await agent.init(api_key="your-minitap-api-key")

        # 安装自定义APK
        await agent.install_apk("/path/to/your-app.apk")
        print("APK installed successfully!")

        # 现在运行使用您应用的任务
        # ...

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

**需要x86_64兼容性**：云手机运行在x86_64架构上。您的APK必须包含x86_64原生库或与架构无关。仅为ARM设备构建的APK将无法工作。

有关`install_apk()`方法的完整文档，请参阅[Agent SDK参考](../05-sdk-reference/01-agent-class.md#install_apk)。

---

## 从云手机捕获截图

您可以使用`get_screenshot()`从云手机捕获截图：

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    config = Builders.AgentConfig.for_cloud_mobile("my-device").build()
    agent = Agent(config=config)

    try:
        await agent.init(api_key="your-minitap-api-key")

        # 从云手机捕获截图
        screenshot = await agent.get_screenshot()

        # 本地保存
        screenshot.save("cloud_device_screenshot.png")
        print("Screenshot captured and saved!")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

`get_screenshot()`方法在云和本地设备上均可无缝工作！

---

## 环境变量

为方便起见，将您的API密钥设置为环境变量：

```shellscript
MINITAP_API_KEY=your_api_key_here
```

然后简化您的代码：

```python
# 无需显式传递api_key
await agent.init()
```

切勿将`.env`文件提交到版本控制。请将其添加到`.gitignore`中。

---

## 监控任务执行

使用云手机时，您可以通过Minitap平台实时监控任务执行：

1. 导航到Platform中的**Task Runs**
2. 按云手机筛选任务，仅查看在特定设备上运行的任务
3. 找到您正在运行的任务
4. 查看：
    - 实时状态更新
        - Agent思考和决策
        - 子目标进展
        - 每步截图
        - LLM成本和使用情况

使用云手机筛选器快速找到在特定虚拟设备上运行的任务！

---

## 本地设备 vs 云手机对比

| 功能 | 本地设备 | 云手机 |
| --- | --- | --- |
| **设置** | 需要ADB/idb、本地服务器 | 零设置 |
| **设备访问** | 必须有物理/模拟器设备 | 按需虚拟设备 |
| **可扩展性** | 受本地资源限制 | 轻松扩展到多个设备 |
| **监控** | 仅本地日志 | 内置Platform可观测性 |
| **成本** | 免费（您的硬件） | 按使用付费 |
| **任务类型** | `TaskRequest`或`PlatformTaskRequest` | `PlatformTaskRequest`（预配置任务或`ManualTaskConfig`） |
| **离线支持** | 是 | 否（需要互联网） |

---

## 最佳实践

### 使用引用名称

命名您的云手机以便于管理：`test-device`、`prod-android-1`

### 监控成本

查看Platform仪表板了解使用情况和成本

### 错误处理

始终使用try/finally确保清理

### 环境变量

将API密钥存储在环境变量中，而不是代码中

---

## 故障排除

**CloudMobileServiceUninitializedError**

**原因**：未提供API密钥或无效。

**解决方案**：

```python
await agent.init(api_key="your-key")
# 或设置MINITAP_API_KEY环境变量
```

**任务立即失败**

**原因**：云手机未处于"Ready"状态。

**解决方案**：检查Platform仪表板确保设备正在运行且就绪。SDK会自动启动并等待设备。

**无法使用直接goal参数**

**原因**：云手机不直接支持`run_task(goal="...")`。

**解决方案**：使用`PlatformTaskRequest`配合预配置任务或`ManualTaskConfig`：

```python
# 方式1：Platform中的预配置任务
request = PlatformTaskRequest(task="my-task")
await agent.run_task(request=request)

# 方式2：使用ManualTaskConfig的一次性任务
from minitap.mobile_use.sdk.types import ManualTaskConfig

task = ManualTaskConfig(goal="Your task here")
request = PlatformTaskRequest(task=task, profile="default")
await agent.run_task(request=request)
```

---

## 下一步

- [本地快速开始](01-local-quickstart.md) - 了解本地设备设置
- [SDK参考](../05-sdk-reference/00-overview.md) - 完整Agent API文档
- [使用示例](../04-examples/00-overview.md) - 更多自动化示例
- [Platform文档](02-platform-quickstart.md) - 深入了解Platform功能
