The `AgentConfigBuilder` provides a fluent interface for configuring agent behavior, device connections, and server settings.

## Import

```python
from minitap.mobile_use.sdk.builders import Builders

# Access the builder
config_builder = Builders.AgentConfig
```

## Methods

### for\_device

Specify a target device instead of auto-detection.

```python
def for_device(
    self, 
    platform: DevicePlatform, 
    device_id: str
) -> AgentConfigBuilder
```platform

DevicePlatform

required

Device platform (`DevicePlatform.ANDROID` or `DevicePlatform.IOS`)device\_id

str

required

Device identifier (from `adb devices` or `idevice_id -l`)

```python
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .build()
)
```

---

### for\_cloud\_mobile

Configure the agent to use a cloud mobile (virtual device hosted on Minitap Platform).

When using a cloud mobile, all agentic logic runs in the cloud, and tasks are executed remotely via the Platform API.

```python
def for_cloud_mobile(
    self,
    cloud_mobile_id_or_ref: str
) -> AgentConfigBuilder
```cloud\_mobile\_id\_or\_ref

str

required

The cloud mobile identifier. Can be either:

- UUID (e.g., `"550e8400-e29b-41d4-a716-446655440000"`)
- Reference name (e.g., `"my-test-device"`)

#### Example with UUID

```python
config = (
    Builders.AgentConfig
    .for_cloud_mobile(cloud_mobile_id_or_ref="550e8400-e29b-41d4-a716-446655440000")
    .build()
)

agent = Agent(config=config)
await agent.init(api_key="your-minitap-api-key")
```

#### Example with Reference Name

```python
config = (
    Builders.AgentConfig
    .for_cloud_mobile(cloud_mobile_id_or_ref="my-test-device")
    .build()
)

agent = Agent(config=config)
await agent.init(api_key="your-minitap-api-key")
```

**Important Notes:**

- `for_cloud_mobile()` and `for_device()` are mutually exclusive
- Cloud mobiles require a Minitap API key (passed to `agent.init()` or via `MINITAP_API_KEY` env var)
- Cloud mobiles only support `PlatformTaskRequest` (not `TaskRequest`)
- No local setup required - no ADB, idb, or local servers needed

Cloud mobiles are ideal when you want:

- No local device setup or maintenance
- Centralized execution and monitoring via Minitap Platform
- Scalable automation without managing infrastructure

---

### add\_profile

Add a single agent profile.

```python
def add_profile(self, profile: AgentProfile) -> AgentConfigBuilder
```

```python
from minitap.mobile_use.sdk.types import AgentProfile

profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
config = Builders.AgentConfig.add_profile(profile).build()
```

---

### add\_profiles

Add multiple agent profiles at once.

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

### with\_default\_profile

Set the default agent profile used for tasks.

```python
def with_default_profile(
    self, 
    profile: str | AgentProfile
) -> AgentConfigBuilder
```

Profile name (if already added) or AgentProfile instance

```python
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)
```

---

### with\_adb\_server

Set the ADB server host and port.

```python
def with_adb_server(
    self, 
    host: str, 
    port: int | None = None
) -> AgentConfigBuilder
```host

str

required

ADB server host addressport

int

default:5037

ADB server port (default: 5037)

```python
config = (
    Builders.AgentConfig
    .with_adb_server(host="localhost", port=5037)
    .build()
)
```

---

### with\_default\_task\_config

Set default configuration for all tasks created by the agent.

```python
def with_default_task_config(
    self, 
    config: TaskRequestCommon
) -> AgentConfigBuilder
```

```python
# Create task defaults
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

# Apply to agent
config = (
    Builders.AgentConfig
    .with_default_task_config(task_defaults)
    .build()
)
```

---

### with\_video\_recording\_tools

Enable video recording tools (`start_video_recording`, `stop_video_recording`).

When enabled, the agent can record the device screen and analyze video content using Gemini models. This is useful for transcribing video content playing on the screen.

```python
def with_video_recording_tools(self) -> AgentConfigBuilder
```

**Requirements:**

1. **ffmpeg** must be installed on the system (for video compression)
2. A **video-capable model** must be configured in `utils.video_analyzer`

**Supported models for video\_analyzer:**

- `gemini-3-flash-preview` (recommended)
- `gemini-3-pro-preview`
- `gemini-2.5-flash`
- `gemini-2.5-pro`
- `gemini-2.0-flash`

```python
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback

# Create profile with video_analyzer configured
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
            # Required for video recording tools
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

Raises `FFmpegNotInstalledError` if ffmpeg is not installed. Raises `ValueError` at runtime if any profile lacks `video_analyzer` config.

---

### build

Build and return the final `AgentConfig` object.

```python
def build(self) -> AgentConfig
```

```python
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

## Complete Example

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile, DevicePlatform

# Create profiles
fast_profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
accurate_profile = AgentProfile(name="accurate", from_file="accurate-config.jsonc")

# Configure task defaults
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

# Build comprehensive agent configuration
config = (
    Builders.AgentConfig
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .with_adb_server(host="localhost", port=5037)
    .with_default_task_config(task_defaults)
    .build()
)

# Create agent with configuration
agent = Agent(config=config)
```

## TaskDefaults Builder

Configure default settings for all tasks:

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

## Server Configuration Shortcut

Use `with_servers()` as a shortcut for configuring ADB server settings:

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

## Next Steps

## Agent SDK

Learn about the Agent class

## Types

Explore configuration types
