---
title: "类型定义"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/types"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/05-sdk-reference/04-types.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "sdk", "types", "pydantic", "data-structures"]
summary: "mobile-use SDK 中使用的核心类型和数据结构参考。"
---
# 类型定义

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/types

mobile-use SDK 核心类型和数据结构参考。

## AgentProfile

表示带有 LLM 配置的 mobile-use Agent 配置文件。

```python
from minitap.mobile_use.sdk.types import AgentProfile
```

### 构造函数

```python
AgentProfile(
    *,
    name: str,
    llm_config: LLMConfig | None = None,
    from_file: str | None = None,
)
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | `str` | 是 | 配置文件名称 |
| `llm_config` | `LLMConfig` | 否 | Agent 的 LLM 配置 |
| `from_file` | `str` | 否 | 包含 LLM 配置的文件路径（JSONC 格式） |

`llm_config` 和 `from_file` 是互斥的——只能使用其中一个。

### 示例

```python
# 从文件加载
profile = AgentProfile(
    name="default",
    from_file="llm-config.defaults.jsonc"
)

# 编程方式配置
from minitap.mobile_use.config import LLM, LLMConfig

profile = AgentProfile(
    name="custom",
    llm_config=LLMConfig(
        planner=LLM(provider="openai", model="gpt-5-nano"),
        cortex=LLM(provider="openai", model="gpt-5"),
        # ... 其他组件
    )
)
```

---

## TaskRequest

表示移动自动化任务请求。

```python
from minitap.mobile_use.sdk.types import TaskRequest
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `goal` | `str` | 任务目标的自然语言描述 |
| `profile` | `str` | 要使用的 Agent 配置文件名称 |
| `task_name` | `str \| None` | 用于日志记录的任务名称 |
| `output_description` | `str \| None` | 预期输出格式的描述 |
| `output_format` | `type[TOutput] \| None` | 用于类型化输出的 Pydantic 模型类 |
| `max_steps` | `int` | Agent 可以执行的最大步骤数 |
| `record_trace` | `bool` | 是否记录执行追踪 |
| `trace_path` | `Path` | 保存追踪数据的目录 |
| `llm_output_path` | `Path \| None` | 保存 LLM 输出的路径 |
| `thoughts_output_path` | `Path \| None` | 保存 Agent 思考过程的路径 |

### 使用方式

`TaskRequest` 对象通常通过 `TaskRequestBuilder` 创建：

```python
task_request = (
    agent.new_task("Your goal")
    .with_name("task_name")
    .build()
)
```

---

## PlatformTaskRequest

通过 Minitap 平台执行的任务请求。

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest
```

使用 `PlatformTaskRequest`，您只需通过名称引用任务。SDK 会自动从平台获取任务配置（目标、最大步骤数、输出格式）和 LLM 配置文件，然后执行任务并将可观测性数据流式传回。

它还会在任务结束时**自动将动画 GIF 追踪上传到云存储**，方便查看。详情请参阅 [可观测性与追踪](../03-core-concepts/04-observability.md)。

### 构造函数

```python
PlatformTaskRequest(
    task: str,
    profile: str | None = None,
    api_key: str | None = None,
    record_trace: bool = True,
    trace_path: Path = Path(tempfile.gettempdir()) / "mobile-use-traces",
    llm_output_path: Path | None = None,
    thoughts_output_path: Path | None = None,
    max_steps: int = 400
)
```

### 属性

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `task` | `str` | - | 在 Minitap 平台上配置的任务名称。必须与 [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks) 中的任务名称完全匹配 |
| `profile` | `str \| None` | `None` | 用于此任务的 LLM 配置文件名称。如果未指定，使用 Minitap 管理的默认配置文件 |
| `api_key` | `str \| None` | `None` | Minitap 平台认证的 API 密钥。如果未提供，使用 `MINITAP_API_KEY` 环境变量 |
| `record_trace` | `bool` | `True` | 启用时，在本地保存任务执行的动画 GIF。对于 `PlatformTaskRequest`，GIF 也会上传到 Minitap 云存储以便在平台中查看 |
| `trace_path` | `Path` | 系统临时目录 | 保存本地追踪文件的目录（步骤和 GIF 运行轨迹） |
| `llm_output_path` | `Path \| None` | `None` | 在本地保存最终 LLM 输出的路径 |
| `thoughts_output_path` | `Path \| None` | `None` | 在本地保存 Agent 思考/推理的路径 |
| `max_steps` | `int` | `400` | 最大步骤数（被平台配置覆盖） |

`PlatformTaskRequest` **不支持**`locked_app_package` 参数。应用锁必须在 [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks) 的平台任务本身上配置。

### 使用方式

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

agent = Agent()
agent.init()

# 简单任务执行
result = await agent.run_task(
    request=PlatformTaskRequest(task="check-notifications")
)

agent.clean()
```

---

## AgentConfig

Agent 的配置。

```python
from minitap.mobile_use.sdk.types import AgentConfig
```

通过 `AgentConfigBuilder` 创建：

```python
config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)

agent = Agent(config=config)
```

---

## DevicePlatform

设备平台枚举。

```python
from minitap.mobile_use.sdk.types import DevicePlatform

# 可用值
DevicePlatform.ANDROID
DevicePlatform.IOS
```

### 使用方式

```python
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .build()
)
```

---

## ServerConfig

Agent 服务器配置。

```python
from minitap.mobile_use.sdk.types import ServerConfig
```

### 属性

| 属性 | 类型 | 说明 |
|------|------|------|
| `adb_server_host` | `str` | ADB 服务器主机地址 |
| `adb_server_port` | `int` | ADB 服务器端口 |

### 使用方式

```python
servers = ServerConfig(
    adb_server_host="localhost",
    adb_server_port=5037
)

config = Builders.AgentConfig.with_servers(servers).build()
```

---

## LLMConfig

不同 Agent 组件使用的 LLM 模型配置。

```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
```

### 结构

```python
llm_config = LLMConfig(
    planner=LLM(provider="openai", model="gpt-5-nano"),
    orchestrator=LLM(provider="openai", model="gpt-5-nano"),
    cortex=LLMWithFallback(
        provider="openai",
        model="gpt-5",
        fallback=LLM(provider="openai", model="gpt-5")
    ),
    executor=LLM(provider="openai", model="gpt-5-nano"),
    utils=LLMConfigUtils(
        hopper=LLM(provider="openai", model="gpt-5-nano"),
        outputter=LLM(provider="openai", model="gpt-5-nano")
    )
)
```

### 组件说明

| 组件 | 职责 |
|------|------|
| `planner` | 从目标创建高级计划 |
| `orchestrator` | 协调执行步骤 |
| `cortex` | 视觉理解和决策制定 |
| `executor` | 执行特定动作 |
| `hopper` | 从大批量数据中提取相关信息 |
| `outputter` | 提取结构化输出 |

---

## LLM

基础 LLM 配置。

```python
from minitap.mobile_use.config import LLM

llm = LLM(provider="openai", model="gpt-5")
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `provider` | `str` | 是 | 提供商名称：`openai`、`google`、`xai`、`openrouter` |
| `model` | `str` | 是 | 模型标识符（例如 `gpt-5`、`gemini-2.5-flash`） |

---

## LLMWithFallback

带有回退模型的 LLM 配置。

```python
from minitap.mobile_use.config import LLM, LLMWithFallback

llm = LLMWithFallback(
    provider="openai",
    model="o4-mini",
    fallback=LLM(provider="openai", model="gpt-5")
)
```

如果主模型失败，会自动使用回退模型。

---

## TaskRequestCommon

跨任务共享的通用配置。

```python
from minitap.mobile_use.sdk.types import TaskRequestCommon
```

通过 `TaskDefaults` Builder 创建：

```python
defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)
```

## 下一步

- **Agent SDK**：核心 Agent 类参考
- **异常处理**：错误处理参考
