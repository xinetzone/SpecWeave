The `Agent` class is the primary entry point for the mobile-use SDK, responsible for managing device interaction and executing tasks.

## Import

```python
from minitap.mobile_use.sdk import Agent
```

## Constructor

```python
Agent(config: AgentConfig | None = None)
```

### Parametersconfig

AgentConfig

Custom agent configuration. If not provided, default configuration is used.

### Example

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile

# With default configuration
agent = Agent()

# With custom configuration
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

## Methods

### init

Initialize the agent by connecting to a device and starting required servers.

```python
async def init(
    self,
    api_key: str | None = None,
    server_restart_attempts: int = 3,
    retry_count: int = 5,
    retry_wait_seconds: int = 5,
) -> bool
```

#### Parametersapi\_key

str

Minitap API key for Platform features (Platform tasks, cloud mobiles). Can also be set via `MINITAP_API_KEY` environment variable.server\_restart\_attempts

int

default:3

Maximum number of attempts to start servers if they failretry\_count

int

default:5

Number of retries for API callsretry\_wait\_seconds

int

default:5

Seconds to wait between retries

#### Returnssuccess

bool

`True` if initialization succeeded, `False` otherwise

#### Example

```python
import asyncio

async def main():
    agent = Agent()

    # Initialize without API key (local mode only)
    if not await agent.init():
        print("Failed to initialize agent")
        exit(1)

    print("Agent initialized successfully")

asyncio.run(main())
```

#### Example with API Key

```python
import asyncio

async def main():
    agent = Agent()

    # Initialize with API key for Platform features
    if not await agent.init(api_key="your-minitap-api-key"):
        print("Failed to initialize agent")
        exit(1)

    print("Agent initialized successfully with Platform support")

asyncio.run(main())
```

Always check the return value of `init()` before running tasks. Note that `init()` is now an async method and must be awaited.

---

### run\_task

Execute a mobile automation task asynchronously.

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

#### Parametersgoal

str

Natural language description of what to accomplishoutput

type\[TOutput\] | str

Type of output:

- Pydantic model class for structured output
- String description for output format

Agent profile to use (name or instance)name

str

Optional name for the task (for logging/debugging)request

TaskRequest\[TOutput\] | PlatformTaskRequest\[TOutput\]

Pre-built TaskRequest or PlatformTaskRequest (alternative to individual parameters)

#### Returnsresult

str | dict | TOutput | None

Task result:

- `str`: Simple text output
- `dict`: Unstructured dictionary
- `TOutput`: Instance of specified Pydantic model
- `None`: Task failed or no output

#### Examples

```python
result = await agent.run_task(
    goal="Open calculator and compute 5 * 7"
)
print(result)  # String output
```

For platform tasks, the **Locked App Package** is configured on the platform task itself, not in `PlatformTaskRequest`. For local tasks using `TaskRequest`, use `.with_locked_app_package()` in the builder.

---

### new\_task

Create a new task request builder for fluent task configuration.

```python
def new_task(self, goal: str) -> TaskRequestBuilder[None]
```

#### Parametersgoal

str

required

Natural language description of what to accomplish

#### Returnsbuilder

TaskRequestBuilder\[None\]

TaskRequestBuilder instance for fluent configuration

#### Example

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

Clean up resources, stop servers, and reset the agent state.

```python
async def clean(self, force: bool = False) -> None
```

#### Parametersforce

bool

default:false

Set to `True` to clean zombie/pre-existing mobile-use servers

#### Example

```python
import asyncio

async def main():
    agent = Agent()

    try:
        await agent.init()
        await agent.run_task(goal="Some task")
    finally:
        await agent.clean()  # Always clean up

asyncio.run(main())
```

Use `force=True` if you have zombie servers from previous runs:

```python
await agent.clean(force=True)  # Kill any existing servers
await agent.init()              # Start fresh
```

Note that `clean()` is now an async method and must be awaited.

---

### install\_apk

Install an APK on the connected Android device.

```python
async def install_apk(self, apk_path: str | Path) -> None
```

This method works with both local devices and cloud mobiles:

- **For local devices**: Uses ADB to install the APK directly
- **For cloud mobiles**: Installs it on the cloud mobile via the API

#### Parametersapk\_path

str | Path

required

Path to the local APK file to install

#### Raises

- `FileNotFoundError`: If the APK file does not exist
- `AgentNotInitializedError`: If the agent is not initialized (local mode)
- `AgentError`: If the device is not an Android device or ADB client is not initialized
- `CloudMobileServiceUninitializedError`: If cloud mobile service is not initialized (cloud mode)
- `AgentTaskRequestError`: If cloud mobile ID is not configured (cloud mode)

APK installation is only supported on Android devices. Attempting to install an APK on an iOS device will raise an `AgentError`.

For cloud mobiles, the APK must be **x86\_64 compatible**.

For cloud mobiles, the `install_apk` method automatically starts the cloud mobile if it’s not already running, so you don’t need to manually start it before installing.

---

### get\_screenshot

Capture a screenshot from the mobile device.

```python
async def get_screenshot(self) -> Image.Image
```

This method works with both local devices and cloud mobiles:

- **For local devices**: Uses ADB (Android) or xcrun (iOS) to capture screenshots directly
- **For cloud mobiles**: Retrieves screenshots from the cloud mobile via the Platform API

#### Returnsscreenshot

Image.Image

Screenshot as a PIL Image object

#### Raises

- `AgentNotInitializedError`: If the agent is not initialized
- `CloudMobileServiceUninitializedError`: If using cloud mobile without proper initialization
- `Exception`: If screenshot capture fails

#### Example

```python
import asyncio
from minitap.mobile_use.sdk import Agent

async def main():
    agent = Agent()

    try:
        await agent.init()

        # Capture a screenshot
        screenshot = await agent.get_screenshot()

        # Save the screenshot
        screenshot.save("device_screenshot.png")
        print("Screenshot saved!")

    finally:
        await agent.clean()

asyncio.run(main())
```

#### Example with Cloud Mobile

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    # Configure for cloud mobile
    config = Builders.AgentConfig.for_cloud_mobile("my-cloud-device").build()
    agent = Agent(config=config)

    try:
        await agent.init(api_key="your-minitap-api-key")

        # Capture screenshot from cloud mobile
        screenshot = await agent.get_screenshot()
        screenshot.save("cloud_device_screenshot.png")

    finally:
        await agent.clean()

asyncio.run(main())
```

Use `get_screenshot()` for debugging, monitoring, or extracting visual data from your mobile device during automation workflows.

## Complete Example

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
    # Configure agent
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)

    try:
        # Initialize
        if not await agent.init():
            print("Failed to initialize")
            return

        # Run task with structured output
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

## Exception Handling

The Agent may raise the following exceptions:

- `AgentNotInitializedError`: Agent methods called before initialization
- `DeviceNotFoundError`: No device found or device disconnected
- `AgentProfileNotFoundError`: Specified profile not found
- `ServerStartupError`: Failed to start required servers
- `ExecutableNotFoundError`: Required executable (adb, idb, xcrun) not found
- `AgentTaskRequestError`: Invalid task request configuration
- `PlatformServiceUninitializedError`: Platform service not initialized (missing API key)
- `CloudMobileServiceUninitializedError`: Cloud mobile service not initialized (missing API key or cloud mobile not configured)
- `AgentInvalidApiKeyError`: Invalid Minitap API key

See [Exceptions](https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/exceptions) for details.

## Next Steps

## Task Request Builder

Configure tasks with the builder pattern

## Agent Config Builder

Configure agent behavior
