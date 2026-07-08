This guide covers using **cloud mobiles** (virtual devices hosted on Minitap Platform) where all agentic logic runs in the cloud.

**Want to use a local device instead?** Check out the [Local Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/quickstart) for setting up with your own devices.

## What are Cloud Mobiles?

Cloud mobiles are virtual Android devices hosted on Minitap Platform. Key benefits:

## Zero Local Setup

No ADB, idb, or local servers required

## Persistent State

Device state is preserved across restarts and sessions

## Always Available

Devices ready on-demand, no maintenance

## Centralized Monitoring

Built-in observability via Minitap Platform

---

## Prerequisites

New users get **$10 in free credits** to get started!

**Current Availability**: Only Android v11 (API level 30) is currently available as a cloud mobile. iOS support is not yet available.

---

## Creating Your First Cloud Mobile Automation

Let’s write a simple script that runs a task on a cloud mobile.

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import PlatformTaskRequest

async def main():
    # Configure agent for cloud mobile
    config = (
        Builders.AgentConfig
        .for_cloud_mobile("my-test-device")  # Or use UUID
        .build()
    )

    agent = Agent(config=config)

    try:
        # Initialize with API key
        await agent.init(api_key="your-minitap-api-key")

        # Create a Platform task request
        task_request = PlatformTaskRequest(
            task="calculator-demo",  # Task defined in Platform
        )

        # Run task on cloud mobile
        result = await agent.run_task(request=task_request)
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

### What’s Different from Local Mode?

Configuration

Use `.for_cloud_mobile()` instead of `.for_device()`:

```python
# Cloud mobile
config = Builders.AgentConfig.for_cloud_mobile("my-device").build()

# Local device
config = Builders.AgentConfig.for_device(DevicePlatform.ANDROID, "emulator-5554").build()
```

API Key Required

Pass API key to `init()` or set `MINITAP_API_KEY` environment variable:

```python
# Option 1: Pass directly
await agent.init(api_key="your-key")

# Option 2: Environment variable
# export MINITAP_API_KEY=your-key
await agent.init()
```

Platform Tasks Only

Cloud mobiles only support `PlatformTaskRequest` (not direct `goal` parameter):

```python
# ✅ Supported - Pre-configured task
request = PlatformTaskRequest(task="my-task")
await agent.run_task(request=request)

# ✅ Supported - One-off task with ManualTaskConfig
from minitap.mobile_use.sdk.types import PlatformTaskRequest, ManualTaskConfig

task = ManualTaskConfig(
    goal="Open calculator and compute 5 * 7",
    output_description="The calculation result"
)
request = PlatformTaskRequest(task=task, profile="default")
await agent.run_task(request=request)

# ❌ Not supported - Direct goal parameter
await agent.run_task(goal="Do something")  # Will raise error
```

Use `ManualTaskConfig` for one-off tasks without pre-configuring them in the Platform!

No Local Servers

No need for ADB, idb, or local device setup. Everything runs in the cloud!

---

## How to Create a Cloud Mobile in Platform

Use reference names for easier identification: `my-test-device` is easier to remember than `550e8400-e29b-41d4-a716-446655440000`!

---

## One-Off Tasks with ManualTaskConfig

You can run one-off tasks on cloud mobiles without pre-configuring them in the Platform by using `ManualTaskConfig`:

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import PlatformTaskRequest, ManualTaskConfig

async def main():
    # Configure for cloud mobile
    config = (
        Builders.AgentConfig
        .for_cloud_mobile("my-device")
        .build()
    )

    agent = Agent(config=config)

    try:
        # Initialize with API key
        await agent.init(api_key="your-minitap-api-key")

        # Create a one-off task with ManualTaskConfig
        task = ManualTaskConfig(
            goal="Open the calculator app, calculate 123 * 456, and tell me the result",
            output_description="The calculation result as a number"
        )

        # Run the task
        result = await agent.run_task(
            request=PlatformTaskRequest(
                task=task,
                profile="default"  # LLM profile defined in Platform
            )
        )

        print(f"Result: {result}")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

`ManualTaskConfig` is perfect for one-off tasks or quick testing without having to create a task in the Platform first!

---

## Complete Example with Structured Output

Here’s a more complete example that uses structured output with `ManualTaskConfig`:

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
    # Configure for cloud mobile
    config = (
        Builders.AgentConfig
        .for_cloud_mobile("my-weather-device")
        .build()
    )

    agent = Agent(config=config)

    try:
        # Initialize with API key from environment or directly
        await agent.init(api_key="your-minitap-api-key")

        # Define a one-off task with structured output
        task = ManualTaskConfig(
            goal="Open the weather app and check the current temperature",
            output_description="Extract temperature, weather condition, and location"
        )

        # Create request with structured output
        task_request = PlatformTaskRequest(
            task=task,
            profile="default"  # LLM profile defined in Platform
        )

        # Run on cloud mobile
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

## Installing Custom APKs

You can install your own APK files on cloud mobiles using the `install_apk()` method:

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    config = Builders.AgentConfig.for_cloud_mobile("my-device").build()
    agent = Agent(config=config)

    try:
        await agent.init(api_key="your-minitap-api-key")

        # Install your custom APK
        await agent.install_apk("/path/to/your-app.apk")
        print("APK installed successfully!")

        # Now run tasks that use your app
        # ...

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

**x86\_64 Compatibility Required**: Cloud mobiles run on x86\_64 architecture. Your APK must include x86\_64 native libraries or be architecture-independent. APKs built only for ARM devices will not work.

See the [Agent SDK Reference](https://www.minitap.ai/docs/mobile-use-sdk/sdk-reference/agent#install_apk) for full documentation on the `install_apk()` method.

---

## Capturing Screenshots from Cloud Mobiles

You can capture screenshots from cloud mobiles using `get_screenshot()`:

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    config = Builders.AgentConfig.for_cloud_mobile("my-device").build()
    agent = Agent(config=config)

    try:
        await agent.init(api_key="your-minitap-api-key")

        # Capture screenshot from cloud mobile
        screenshot = await agent.get_screenshot()

        # Save locally
        screenshot.save("cloud_device_screenshot.png")
        print("Screenshot captured and saved!")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

The `get_screenshot()` method works seamlessly with both cloud and local devices!

---

## Environment Variables

For convenience, set your API key as an environment variable:

```shellscript
MINITAP_API_KEY=your_api_key_here
```

Then simplify your code:

```python
# No need to pass api_key explicitly
await agent.init()
```

Never commit your `.env` file to version control. Add it to `.gitignore`.

---

## Monitoring Task Execution

When using cloud mobiles, you can monitor task execution in real-time via Minitap Platform:

1. Navigate to **Task Runs** in the Platform
2. Filter tasks by cloud mobile to see only tasks running on specific devices
3. Find your running task
4. View:
	- Real-time status updates
		- Agent thoughts and decisions
		- Subgoal progress
		- Screenshots at each step
		- LLM costs and usage

Use the cloud mobile filter to quickly find tasks running on a specific virtual device!

---

## Comparing Local vs Cloud Mobiles

| Feature | Local Device | Cloud Mobile |
| --- | --- | --- |
| **Setup** | Requires ADB/idb, local servers | Zero setup required |
| **Device Access** | Must have physical/emulator device | On-demand virtual devices |
| **Scalability** | Limited by local resources | Easily scale to multiple devices |
| **Monitoring** | Local logs only | Built-in Platform observability |
| **Cost** | Free (your hardware) | Pay per usage |
| **Task Types** | `TaskRequest` or `PlatformTaskRequest` | `PlatformTaskRequest` (with pre-configured tasks or `ManualTaskConfig`) |
| **Offline Support** | Yes | No (requires internet) |

---

## Best Practices

## Use Reference Names

Name your cloud mobiles for easier management: `test-device`, `prod-android-1`

## Monitor Costs

Check Platform dashboard for usage and costs

## Error Handling

Always use try/finally to ensure cleanup

## Environment Variables

Store API keys in environment variables, not code

---

## Troubleshooting

CloudMobileServiceUninitializedError

**Cause**: API key not provided or invalid.

**Solution**:

```python
await agent.init(api_key="your-key")
# Or set MINITAP_API_KEY environment variable
```

Task fails immediately

**Cause**: Cloud mobile not in “Ready” state.

**Solution**: Check Platform dashboard to ensure device is running and ready. The SDK automatically starts and waits for the device.

Can't use direct goal parameter

**Cause**: Cloud mobiles don’t support `run_task(goal="...")` directly.

**Solution**: Use `PlatformTaskRequest` with either a pre-configured task or `ManualTaskConfig`:

```python
# Option 1: Pre-configured task from Platform
request = PlatformTaskRequest(task="my-task")
await agent.run_task(request=request)

# Option 2: One-off task with ManualTaskConfig
from minitap.mobile_use.sdk.types import ManualTaskConfig

task = ManualTaskConfig(goal="Your task here")
request = PlatformTaskRequest(task=task, profile="default")
await agent.run_task(request=request)
```

---

## Next Steps

## Local Quickstart

Learn about local device setup

## SDK Reference

Complete Agent API documentation

## Examples

More automation examples

## Platform Docs

Deep dive into Platform features
