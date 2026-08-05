---
source: d:\AI\.chaos\libs\mobile-use
---

# SDK 使用指南

## Agent 类：SDK 核心入口

`Agent` 类是 mobile-use SDK 的门面（Facade），封装了设备初始化、任务执行、资源管理的全部复杂度。

### 生命周期

```python
from minitap.mobile_use import Agent

agent = Agent()              # 1. 创建实例（轻量，不连接设备）
await agent.init()           # 2. 初始化（探测设备、启动服务、连接客户端）
result = await agent.run_task(goal="...")  # 3. 执行任务（可多次调用）
await agent.clean()          # 4. 清理资源（断开连接、停止服务）
```

> **重要**: `init()` 和 `clean()` 必须配对调用，建议使用 `try/finally` 或上下文管理模式。

### Agent 初始化参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `config` | `AgentConfig \| None` | `None`（使用默认配置） | Agent 配置，通过 Builder 创建 |
| `api_key` | `str \| None` | `None` | Minitap Platform API Key（云平台模式） |
| `server_restart_attempts` | `int` | `3` | 服务启动失败重试次数 |
| `retry_count` | `int` | `5` | 客户端连接重试次数 |
| `retry_wait_seconds` | `int` | `5` | 重试间隔秒数 |

## 任务执行：run_task()

`run_task()` 是最常用的方法，支持多种调用方式（通过 `@overload` 提供类型安全）：

### 方式一：最简调用（自然语言）

```python
result = await agent.run_task(
    goal="Open Settings and tell me the battery percentage"
)
# 返回: str（自然语言描述的结果）
```

### 方式二：带输出描述

```python
result = await agent.run_task(
    goal="Find first 3 unread emails in Gmail",
    output="A JSON list of objects with 'sender' and 'subject' keys"
)
# 返回: str | dict（根据描述生成的结构化结果）
```

### 方式三：结构化输出（Pydantic 模型）

```python
from pydantic import BaseModel

class Contact(BaseModel):
    name: str
    phone: str

class ContactList(BaseModel):
    contacts: list[Contact]

result = await agent.run_task(
    goal="Search contacts for 'Alice' and return her phone number",
    output=ContactList  # 传入 Pydantic 模型类
)
# 返回: ContactList（自动解析为 Pydantic 对象）
for contact in result.contacts:
    print(f"{contact.name}: {contact.phone}")
```

### 方式四：锁定 App 包名

```python
result = await agent.run_task(
    goal="Send 'Hello' to the first chat",
    locked_app_package="com.whatsapp",  # 只在 WhatsApp 内操作，防止跳出
    output="Confirmation message"
)
```

### 方式五：使用 TaskRequest Builder（推荐复杂场景）

```python
task = (
    agent.new_task("Open WhatsApp and send 'Meeting at 3pm' to Bob")
    .with_locked_app_package("com.whatsapp")
    .with_max_steps(30)
    .with_name("send_message_to_bob")
    .with_output_description("Status of message sending")
    .build()
)

result = await agent.run_task(request=task)
```

### run_task() 参数全表

| 参数 | 类型 | 说明 |
|---|---|---|
| `goal` | `str` | 自然语言任务目标 |
| `output` | `type[BaseModel] \| str \| None` | 输出格式：Pydantic类/JSON描述/None |
| `profile` | `str \| AgentProfile \| None` | 使用的LLM配置Profile名称 |
| `name` | `str \| None` | 任务名称（用于日志和追踪） |
| `locked_app_package` | `str \| None` | 锁定的App包名，禁止跳出 |
| `app_path` | `str \| Path \| None` | 要安装的App路径（APK/.app） |
| `request` | `TaskRequest \| PlatformTaskRequest` | 使用Builder构建的任务请求 |

## Builder 模式详解

### AgentConfigBuilder：配置 Agent

```python
from minitap.mobile_use import Builders

config = (
    Builders.AgentConfig()
    # 添加LLM配置Profile
    .add_profile(
        name="fast",
        llm_config={  # 每个Agent可独立配置LLM
            "planner": {"provider": "openai", "model": "gpt-4o"},
            "cortex": {"provider": "openai", "model": "gpt-4o-mini"},  # 决策用快模型
            "executor": {"provider": "openai", "model": "gpt-4o-mini"},
        }
    )
    .add_profile(
        name="smart",
        llm_config={
            "planner": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
            "cortex": {"provider": "anthropic", "model": "claude-haiku-3-5-20241022"},
        }
    )
    .with_default_profile("fast")  # 默认使用fast profile
    .with_default_task_config(max_steps=50)  # 默认最大步数
    .with_video_recording_tools()  # 启用视频录制工具
    .build()
)

agent = Agent(config=config)
await agent.init()
```

**AgentConfigBuilder 方法列表**：

| 方法 | 说明 |
|---|---|
| `add_profile(name, llm_config)` | 添加一个LLM配置Profile |
| `add_profiles(profiles)` | 批量添加Profile |
| `with_default_profile(name)` | 设置默认Profile |
| `with_default_task_config(max_steps, ...)` | 设置默认任务参数 |
| `with_video_recording_tools()` | 启用视频录制工具 |
| `for_cloud_mobile(cloud_mobile_id_or_ref)` | 配置云手机模式 |
| `build()` | 构建最终配置 |

### TaskRequestBuilder：配置单个任务

```python
task = (
    agent.new_task("Your goal here")
    .with_output_format(MyPydanticModel)    # Pydantic结构化输出
    .with_output_description("JSON format") # 或自然语言描述
    .with_locked_app_package("com.example.app")  # 锁定App
    .using_profile("smart")                # 指定使用某个Profile
    .with_max_steps(100)                   # 最大执行步数
    .with_trace_recording()                # 启用Trace录制
    .with_name("my_task")                  # 任务名称
    .with_app_path("./my_app.apk")         # 安装并启动指定App
    .build()
)
```

## 设备模式

### 本地设备模式（默认）

自动探测第一个连接的设备：
```python
agent = Agent()
await agent.init()  # 自动找ADB设备或iOS模拟器
```

指定设备：
```python
config = (
    Builders.AgentConfig()
    .with_default_profile()
    # 指定设备ID和平台
    # （需要直接修改config的device_id和device_platform字段）
    .build()
)
```

### 云手机模式

#### Minitap Cloud Mobile
```python
config = (
    Builders.AgentConfig()
    .for_cloud_mobile(cloud_mobile_id_or_ref="your-cloud-id")
    .with_default_profile()
    .build()
)

agent = Agent(config=config)
await agent.init(api_key="your-minitap-api-key")

# 云手机模式必须使用 PlatformTaskRequest
from minitap.mobile_use.sdk.types.task import PlatformTaskRequest

request = PlatformTaskRequest(task="Your task here")
result = await agent.run_task(request=request)
```

#### Limrun 云设备
```python
# Limrun 设备通过 limrun_config 或预配置 controller 初始化
# 详见 controllers/limrun_controller.py
```

#### BrowserStack
```python
# 通过 browserstack_config 配置
```

## 多任务与任务取消

### 执行多个任务

```python
agent = Agent()
await agent.init()

try:
    # 任务1：查看电量
    battery = await agent.run_task(goal="Check battery level")
    print(battery)
    
    # 任务2：发送消息（自动排队，任务锁保证串行）
    msg = await agent.run_task(
        goal="Send 'Hi' to Alice",
        locked_app_package="com.whatsapp"
    )
    print(msg)
finally:
    await agent.clean()
```

> **注意**: Agent 内部有 `asyncio.Lock`，同一时间只能执行一个任务。并发调用 `run_task()` 会自动等待当前任务完成。

### 取消当前任务

```python
# 在另一个协程中取消
agent.stop_current_task()
```

## 辅助 API

### 获取截图

```python
from PIL import Image

screenshot: Image.Image = await agent.get_screenshot()
screenshot.save("screenshot.png")
```

### 安装 APK

```python
await agent.install_apk("./my_app.apk")
```

### 安装 App（跨平台）

```python
# Android: 安装APK
# iOS (Limrun): 安装.app bundle并返回bundle ID
bundle_id = await agent.install_app("./build/MyApp.app")
```

## 异常处理

SDK 定义了完整的异常体系：

| 异常类 | 触发场景 |
|---|---|
| `AgentNotInitializedError` | 调用方法前未调用 `init()` |
| `DeviceNotFoundError` | 未找到连接的设备 |
| `ExecutableNotFoundError` | ADB/Xcode 等必需工具未安装 |
| `ServerStartupError` | 设备服务启动失败 |
| `AgentProfileNotFoundError` | 指定的Profile不存在 |
| `AgentTaskRequestError` | 任务请求参数错误 |
| `CloudMobileServiceUninitializedError` | 云手机服务未初始化 |
| `PlatformServiceUninitializedError` | Platform服务未初始化 |

```python
from minitap.mobile_use.sdk.types.exceptions import (
    AgentNotInitializedError,
    DeviceNotFoundError,
    ServerStartupError,
)

try:
    await agent.init()
    result = await agent.run_task(goal="...")
except DeviceNotFoundError:
    print("请连接设备并开启USB调试")
except ServerStartupError as e:
    print(f"服务启动失败: {e}")
except AgentNotInitializedError:
    print("请先调用 agent.init()")
finally:
    await agent.clean()
```

## 完整示例：多 Profile + 结构化输出

```python
import asyncio
from pydantic import BaseModel
from minitap.mobile_use import Agent, Builders

class EmailInfo(BaseModel):
    sender: str
    subject: str
    date: str

class EmailSummary(BaseModel):
    unread_count: int
    emails: list[EmailInfo]

async def main():
    # 配置两个Profile：fast用于简单任务，smart用于复杂任务
    config = (
        Builders.AgentConfig()
        .add_profile(
            name="fast",
            llm_config={
                "planner": {"provider": "openai", "model": "gpt-4o-mini"},
                "cortex": {"provider": "openai", "model": "gpt-4o-mini"},
                "executor": {"provider": "openai", "model": "gpt-4o-mini"},
                "contextor": {"provider": "openai", "model": "gpt-4o-mini"},
                "orchestrator": {"provider": "openai", "model": "gpt-4o-mini"},
            }
        )
        .with_default_profile("fast")
        .with_default_task_config(max_steps=30)
        .build()
    )
    
    agent = Agent(config=config)
    
    try:
        await agent.init()
        print("Agent initialized!")
        
        # 执行任务：获取未读邮件摘要
        result = await agent.run_task(
            goal="Open Gmail, find unread emails from today, summarize them",
            output=EmailSummary,
            locked_app_package="com.google.android.gm",
            name="daily_email_summary"
        )
        
        print(f"\nFound {result.unread_count} unread emails:")
        for email in result.emails:
            print(f"  [{email.date}] {email.sender}: {email.subject}")
            
    finally:
        await agent.clean()
        print("\nAgent cleaned up.")

if __name__ == "__main__":
    asyncio.run(main())
```

## SDK 示例索引

| 示例文件 | 场景 | 学习要点 |
|---|---|---|
| [platform_minimal_example.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/platform_minimal_example.py) | Minitap云平台最小示例 | 云平台API Key认证 |
| [simple_photo_organizer.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/simple_photo_organizer.py) | 本地设备基础用法 | 最简模式+Pydantic输出 |
| [app_lock_messaging.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/app_lock_messaging.py) | 锁定App发消息 | Builder链式调用+lock_app_package |
| [smart_notification_assistant.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/smart_notification_assistant.py) | 多Profile高级用法 | 自定义AgentProfile+fallback配置 |
| [video_transcription_example.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/examples/video_transcription_example.py) | 视频录制分析 | with_video_recording_tools()+video_analyzer配置 |
