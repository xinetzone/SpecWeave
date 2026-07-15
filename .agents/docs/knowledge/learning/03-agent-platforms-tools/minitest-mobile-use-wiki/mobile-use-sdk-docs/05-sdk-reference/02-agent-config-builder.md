---
title: "AgentConfigBuilder"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent-config-builder"
x-toml-ref: "../../../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/02-agent-config-builder.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "sdk", "builder", "configuration", "api"]
summary: "AgentConfigBuilder 提供流式接口用于配置 Agent 行为、设备连接和服务器设置。"
---
# AgentConfigBuilder

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent-config-builder

`AgentConfigBuilder` 提供流式接口用于配置 Agent 行为、设备连接和服务器设置。

## 导入

```python
from minitap.mobile_use.sdk.builders import Builders

# 访问 Builder
config_builder = Builders.AgentConfig
```

## 方法

### for_device

指定目标设备而非自动检测。

```python
def for_device(
    self, 
    platform: DevicePlatform, 
    device_id: str
) -> AgentConfigBuilder
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `platform` | `DevicePlatform` | 是 | 设备平台（`DevicePlatform.ANDROID` 或 `DevicePlatform.IOS`） |
| `device_id` | `str` | 是 | 设备标识符（来自 `adb devices` 或 `idevice_id -l`） |

```python
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .build()
)
```

---

### for_cloud_mobile

配置 Agent 使用云设备（托管在 Minitap 平台上的虚拟设备）。

使用云设备时，所有代理逻辑在云端运行，任务通过平台 API 远程执行。

```python
def for_cloud_mobile(
    self,
    cloud_mobile_id_or_ref: str
) -> AgentConfigBuilder
```

#### 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `cloud_mobile_id_or_ref` | `str` | 是 | 云设备标识符。可以是：UUID（例如 `"550e8400-e29b-41d4-a716-446655440000"`）或引用名称（例如 `"my-test-device"`） |

#### UUID 示例

```python
config = (
    Builders.AgentConfig
    .for_cloud_mobile(cloud_mobile_id_or_ref="550e8400-e29b-41d4-a716-446655440000")
    .build()
)

agent = Agent(config=config)
await agent.init(api_key="your-minitap-api-key")
```

#### 引用名称示例

```python
config = (
    Builders.AgentConfig
    .for_cloud_mobile(cloud_mobile_id_or_ref="my-test-device")
    .build()
)

agent = Agent(config=config)
await agent.init(api_key="your-minitap-api-key")
```

**重要说明：**

- `for_cloud_mobile()` 和 `for_device()` 是互斥的
- 云设备需要 Minitap API Key（传递给 `agent.init()` 或通过 `MINITAP_API_KEY` 环境变量）
- 云设备仅支持 `PlatformTaskRequest`（不支持 `TaskRequest`）
- 无需本地设置 - 不需要 ADB、idb 或本地服务器

云设备适用于以下场景：
- 无需本地设备设置或维护
- 通过 Minitap 平台集中执行和监控
- 无需管理基础设施的可扩展自动化

---

### add_profile

添加单个 Agent Profile。

```python
def add_profile(self, profile: AgentProfile) -> AgentConfigBuilder
```

```python
from minitap.mobile_use.sdk.types import AgentProfile

profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
config = Builders.AgentConfig.add_profile(profile).build()
```

---

### add_profiles

一次添加多个 Agent Profile。

```python
def add_profiles(self, profiles: list[AgentProfile]) -> AgentConfigBuilder
```

```python
profiles = [
    AgentProfile(name="fast", from_file="fast.jsonc"),
    AgentProfile(name="accurate", from_file="accurate.jsonc")
]

config = Builders.AgentConfig.add_profiles(profiles).build()
```

---

### with_default_profile

设置用于任务的默认 Agent Profile。

```python
def with_default_profile(
    self, 
    profile: str | AgentProfile
) -> AgentConfigBuilder
```

Profile 名称（如果已添加）或 AgentProfile 实例。

```python
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)
```

---

### with_adb_server

设置 ADB 服务器主机和端口。

```python
def with_adb_server(
    self, 
    host: str, 
    port: int | None = None
) -> AgentConfigBuilder
```

#### 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `host` | `str` | 是 | - | ADB 服务器主机地址 |
| `port` | `int` | 否 | `5037` | ADB 服务器端口 |

```python
config = (
    Builders.AgentConfig
    .with_adb_server(host="localhost", port=5037)
    .build()
)
```

---

### with_default_task_config

设置 Agent 创建的所有任务的默认配置。

```python
def with_default_task_config(
    self, 
    config: TaskRequestCommon
) -> AgentConfigBuilder
```

```python
# 创建任务默认配置
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

# 应用到 Agent
config = (
    Builders.AgentConfig
    .with_default_task_config(task_defaults)
    .build()
)
```

---

### with_video_recording_tools

启用视频录制工具（`start_video_recording`、`stop_video_recording`）。

启用后，Agent 可以录制设备屏幕并使用 Gemini 模型分析视频内容。这对于转录屏幕上播放的视频内容非常有用。

```python
def with_video_recording_tools(self) -> AgentConfigBuilder
```

**要求：**

1. 系统上必须安装 **ffmpeg**（用于视频压缩）
2. 必须在 `utils.video_analyzer` 中配置**支持视频的模型**

**video_analyzer 支持的模型：**

- `gemini-3-flash-preview`（推荐）
- `gemini-3-pro-preview`
- `gemini-2.5-flash`
- `gemini-2.5-pro`
- `gemini-2.0-flash`

```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback

# 创建配置了 video_analyzer 的 Profile
profile = AgentProfile(
    name="video_capable",
    llm_config=LLMConfig(
        planner=LLMWithFallback(...),
        orchestrator=LLMWithFallback(...),
        cortex=LLMWithFallback(...),
        executor=LLMWithFallback(...),
        utils=LLMConfigUtils(
            outputter=LLMWithFallback(...),
            hopper=LLMWithFallback(...),
            # 视频录制工具必需
            video_analyzer=LLMWithFallback(
                provider="google",
                model="gemini-3-flash-preview",
                fallback=LLM(provider="google", model="gemini-2.5-flash"),
            ),
        ),
    ),
)

config = (
    Builders.AgentConfig
    .add_profile(profile)
    .with_video_recording_tools()
    .build()
)
```

如果未安装 ffmpeg，会引发 `FFmpegNotInstalledError`。如果任何 Profile 缺少 `video_analyzer` 配置，运行时会引发 `ValueError`。

---

### build

构建并返回最终的 `AgentConfig` 对象。

```python
def build(self) -> AgentConfig
```

```python
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

## 完整示例

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile, DevicePlatform

# 创建 Profile
fast_profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
accurate_profile = AgentProfile(name="accurate", from_file="accurate-config.jsonc")

# 配置任务默认设置
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

# 构建综合 Agent 配置
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .with_adb_server(host="localhost", port=5037)
    .with_default_task_config(task_defaults)
    .build()
)

# 使用配置创建 Agent
agent = Agent(config=config)
```

## TaskDefaults Builder

配置所有任务的默认设置：

```python
defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .with_trace_recording(enabled=True)
    .build()
)

config = (
    Builders.AgentConfig
    .with_default_task_config(defaults)
    .build()
)
```

## 服务器配置快捷方式

使用 `with_servers()` 作为配置 ADB 服务器设置的快捷方式：

```python
from minitap.mobile_use.sdk.types import ServerConfig

servers = ServerConfig(
    adb_server_host="localhost",
    adb_server_port=5037
)

config = (
    Builders.AgentConfig
    .with_servers(servers)
    .build()
)
```

## 下一步

- **Agent SDK**：了解 Agent 类
- **类型**：探索配置类型
