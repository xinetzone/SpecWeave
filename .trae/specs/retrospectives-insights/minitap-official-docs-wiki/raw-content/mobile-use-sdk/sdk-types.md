Reference for core types and data structures used in the mobile-use SDK.

## AgentProfile

Represents a profile for the mobile-use agent with LLM configuration.

```python
from minitap.mobile_use.sdk.types import AgentProfile
```

### Constructor

```python
AgentProfile(
    *,
    name: str,
    llm_config: LLMConfig | None = None,
    from_file: str | None = None,
)
```name

str

required

Name of the profilellm\_config

LLMConfig

LLM configuration for the agentfrom\_file

str

Path to a file containing LLM configuration (JSONC format)

`llm_config` and `from_file` are mutually exclusive - use only one.

### Examples

```python
# From file
profile = AgentProfile(
    name="default",
    from_file="llm-config.defaults.jsonc"
)

# Programmatic
from minitap.mobile_use.config import LLM, LLMConfig

profile = AgentProfile(
    name="custom",
    llm_config=LLMConfig(
        planner=LLM(provider="openai", model="gpt-5-nano"),
        cortex=LLM(provider="openai", model="gpt-5"),
        # ... other components
    )
)
```

---

## TaskRequest

Represents a mobile automation task request.

```python
from minitap.mobile_use.sdk.types import TaskRequest
```

### Attributesgoal

str

Natural language description of the task goal

Name of the agent profile to usetask\_name

str | None

Name of the task for loggingoutput\_description

str | None

Description of the expected output formatoutput\_format

type\[TOutput\] | None

Pydantic model class for typed outputmax\_steps

int

Maximum number of steps the agent can takerecord\_trace

bool

Whether to record execution tracestrace\_path

Path

Directory to save trace datallm\_output\_path

Path | None

Path to save LLM outputsthoughts\_output\_path

Path | None

Path to save agent thoughts

### Usage

TaskRequest objects are typically created via `TaskRequestBuilder`:

```python
task_request = (
    agent.new_task("Your goal")
    .with_name("task_name")
    .build()
)
```

---

## PlatformTaskRequest

Task request for execution via the Minitap Platform.

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest
```

With `PlatformTaskRequest`, you only reference a task by name. The SDK automatically fetches the task configuration (goal, max\_steps, output format) and LLM profile from the platform, then executes the task and streams observability data back.

It also automatically upload **animated GIF traces at the end of the task** to cloud storage for easy viewing. See [Observability & Tracing](https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/observability) for details.

### Constructor

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

### Attributestask

str

Name of the task configured on the Minitap Platform.

Must exactly match a task name from [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks).

Name of the LLM profile to use for this task.

If not specified, uses the Minitap-managed default profile.api\_key

str | None

API key for authentication with the Minitap Platform.

If not provided, uses the `MINITAP_API_KEY` environment variable.record\_trace

bool

default:true

When enabled, an animated GIF of the task execution is saved locally. In case of `PlatformTaskRequest`, the GIF is also uploaded to Minitap cloud storage for viewing in the platform.trace\_path

Path

Directory to save local trace files (steps and GIF run trajectory). Defaults to system temp directory.llm\_output\_path

Path | None

Path to save the final LLM output locally.thoughts\_output\_path

Path | None

Path to save agent thoughts/reasoning locally.max\_steps

int

Maximum number of steps (overridden by platform configuration).

`PlatformTaskRequest` does **not** support `locked_app_package` as a parameter. The app lock must be configured on the platform task itself at [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks).

### Usage

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

agent = Agent()
agent.init()

# Simple task execution
result = await agent.run_task(
    request=PlatformTaskRequest(task="check-notifications")
)

agent.clean()
```

---

## AgentConfig

Configuration for the agent.

```python
from minitap.mobile_use.sdk.types import AgentConfig
```

Created via `AgentConfigBuilder`:

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

Enum for device platforms.

```python
from minitap.mobile_use.sdk.types import DevicePlatform

# Available values
DevicePlatform.ANDROID
DevicePlatform.IOS
```

### Usage

```python
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .build()
)
```

---

## ServerConfig

Configuration for agent servers.

```python
from minitap.mobile_use.sdk.types import ServerConfig
```

### Attributesadb\_server\_host

str

ADB server hostadb\_server\_port

int

ADB server port

### Usage

```python
servers = ServerConfig(
    adb_server_host="localhost",
    adb_server_port=5037
)

config = Builders.AgentConfig.with_servers(servers).build()
```

---

## LLMConfig

Configuration for LLM models used by different agent components.

```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
```

### Structure

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

### Components

## planner

Creates high-level plans from goals

## orchestrator

Coordinates execution steps

## cortex

Visual understanding and decision-making

## executor

Performs specific actions

## hopper

Extracts relevant information from large data batches

## outputter

Extracts structured output

---

## LLM

Basic LLM configuration.

```python
from minitap.mobile_use.config import LLM

llm = LLM(provider="openai", model="gpt-5")
```provider

str

required

Provider name: `openai`, `google`, `xai`, `openrouter`model

str

required

Model identifier (e.g., `gpt-5`, `gemini-2.5-flash`)

---

## LLMWithFallback

LLM configuration with a fallback model.

```python
from minitap.mobile_use.config import LLM, LLMWithFallback

llm = LLMWithFallback(
    provider="openai",
    model="o4-mini",
    fallback=LLM(provider="openai", model="gpt-5")
)
```

If the primary model fails, the fallback is used automatically.

---

## TaskRequestCommon

Common configuration shared across tasks.

```python
from minitap.mobile_use.sdk.types import TaskRequestCommon
```

Created via `TaskDefaults` builder:

```python
defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)
```

## Next Steps

## Agent SDK

Core Agent class reference

## Exceptions

Error handling reference
