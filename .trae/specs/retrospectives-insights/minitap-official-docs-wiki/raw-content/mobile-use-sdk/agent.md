The `Agent` class is the primary entry point for the SDK. It coordinates all components required for mobile automation.

## Responsibilities

## Device Management

Initializes and manages connections to Android/iOS devices

## Server Lifecycle

Starts and stops the Device Controller server

## Task Execution

Creates and executes automation tasks

## Resource Cleanup

Handles proper cleanup and resource release

## Basic Usage

### Creating an Agent

- Local Development

With the platform, simply create an agent - no configuration needed:

```python
from minitap.mobile_use.sdk import Agent

# Create agent (uses MINITAP_API_KEY from environment)
agent = Agent()
```

All profiles and task configurations are managed on [platform.mobile-use.ai](https://platform.mobile-use.ai/).

For local development, configure the agent with profiles:

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile

# Create profile from config file
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

# Configure agent
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

### Agent Lifecycle

## Configuration Options

The agent can be configured using the `AgentConfigBuilder`:

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile, DevicePlatform

# Create profiles
default_profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

# Configure the agent
config = (
    Builders.AgentConfig
    .with_default_profile(default_profile)
    .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
    .build()
)

agent = Agent(config=config)
```

## Initialization Options

The `init()` method accepts several parameters for robust initialization:

```python
agent.init(
    server_restart_attempts=3,  # Retry server startup if it fails
    retry_count=5,              # Number of API call retries
    retry_wait_seconds=5        # Seconds between retries
)
```

If you have zombie servers from previous runs, use `agent.clean(force=True)` before initializing.

## Device Selection

By default, the agent connects to the first available device. You can specify a device explicitly:

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

## Server Configuration

The agent manages the Device Controller server which handles all device interactions:

Device Controller Server

Executes device actions and captures screen state using native platform tools:

- **Android**: Uses ADB (Android Debug Bridge) with UIAutomator2 for UI automation
- **iOS**: Uses IDB (iOS Development Bridge) for simulator and device control

Capabilities include:

- Screenshots and UI hierarchy capture
- Tap, swipe, scroll gestures
- App launching and navigation
- Key press events and text input

## Complete Example

- Platform
- Local

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

async def main():
    # Create agent (uses MINITAP_API_KEY from .env)
    agent = Agent()
    
    try:
        # Initialize
        if not agent.init():
            print("Failed to initialize agent")
            return
        
        # Run platform task (configured on platform.mobile-use.ai)
        result = await agent.run_task(
            request=PlatformTaskRequest(task="check-notifications")
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always clean up
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

async def main():
    # Configure agent with local profile
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)
    
    try:
        # Initialize
        if not agent.init():
            print("Failed to initialize agent")
            return
        
        # Run local task
        result = await agent.run_task(
            goal="Check my notifications",
            name="check_notifications"
        )
        print(f"Result: {result}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always clean up
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## Best Practices

Always use try-finally

Ensure `agent.clean()` is called even if errors occur

```python
try:
    agent.init()
    await agent.run_task(...)
finally:
    agent.clean()
```

Handle initialization failures

Check the return value of `init()`

```python
if not agent.init():
    print("Failed to initialize")
    return
```

Use context managers

Consider wrapping in a context manager for automatic cleanup

## Next Steps

## Tasks

Learn about task creation and execution

## SDK Reference

Detailed Agent SDK documentation
