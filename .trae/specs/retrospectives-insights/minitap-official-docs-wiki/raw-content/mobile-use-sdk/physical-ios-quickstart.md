This guide covers the one-time setup required to automate physical iOS devices connected via USB using WebDriverAgent (WDA).

**Looking for other options?** Check out the [Local Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/quickstart) for Android/iOS simulators or [Cloud Mobile Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/cloud-quickstart) for zero-setup cloud devices.

Make sure you’ve completed the [Installation](https://www.minitap.ai/docs/mobile-use-sdk/installation) steps before proceeding.

## What You’ll Need

## macOS with Xcode

Required for code signing and building WDA

## Physical iOS Device

iPhone or iPad connected via USB cable

## Node.js & npm

For installing Appium and drivers

## Apple Developer Account

Free account works - needed for code signing

---

## One-Time Setup

---

## Using Your Physical iOS Device

After the one-time setup, mobile-use handles everything automatically:

- ✅ Starts **iproxy** for USB port forwarding
- ✅ Builds and runs **WebDriverAgent** via xcodebuild
- ✅ Connects to WDA and waits for it to be ready
- ✅ Cleans up processes when your script exits

### Basic Example

```python
import asyncio
from minitap.mobile_use.sdk import Agent

async def main():
    # Create agent - automatically detects connected iOS device
    agent = Agent()
    
    # Initialize - WDA, iproxy, and xcodebuild start automatically
    await agent.init()
    
    # Run tasks on your physical device
    result = await agent.run_task(
        goal="Open Safari and search for 'mobile automation'",
    )
    
    print(f"Task completed: {result.status}")

if __name__ == "__main__":
    asyncio.run(main())
```

The agent automatically detects your connected iOS device. No UDID needed unless you have multiple devices connected!

### Multiple Devices

If you have multiple devices connected, specify which one to use:

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders

async def main():
    config = (
        Builders.AgentConfig
        .for_device("YOUR_DEVICE_UDID", platform="ios")
        .build()
    )
    
    agent = Agent(config=config)
    await agent.init()
    
    # Your automation here
```

How to find your device UDID

```shellscript
# Option 1: Using idevice_id
idevice_id -l

# Option 2: Using Xcode
# Window → Devices and Simulators → Select your device
# The UDID is shown in the device info
```

---

## Advanced Configuration

### Managing WDA Externally

For debugging or custom setups, you can disable auto-start and manage iproxy/WDA manually:

```python
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.clients.ios_client_config import IosClientConfig, WdaClientConfig

async def main():
    # Create config to disable auto-starting
    ios_config = IosClientConfig(
        wda=WdaClientConfig(
            auto_start_iproxy=False,  # Don't auto-start iproxy
            auto_start_wda=False,      # Don't auto-start WDA
            wda_url="http://localhost:8100"
        )
    )

    config = (
        Builders.AgentConfig
        .for_device("YOUR_DEVICE_UDID", platform="ios")
        .with_ios_client_config(ios_config)
        .build()
    )

    agent = Agent(config=config)
    await agent.init()
    
    # Your automation here
```

When auto-start is disabled, manually start the required processes:

```shellscript
# Start USB port forwarding
iproxy 8100 8100 -u YOUR_DEVICE_UDID
```

Available WDA Configuration Options

| Option | Type | Default | Description |
| --- | --- | --- | --- |
| `auto_start_iproxy` | `bool` | `True` | Auto-start USB port forwarding |
| `auto_start_wda` | `bool` | `True` | Auto-build and run WDA via xcodebuild |
| `wda_url` | `str` | `"http://localhost:8100"` | WDA server URL |
| `wda_project_path` | `str \| None` | `None` | Custom path to WebDriverAgent.xcodeproj |
| `wda_startup_timeout` | `float` | `120.0` | Max seconds to wait for WDA startup |

---

## How It Works

The WDA wrapper automatically manages iproxy and xcodebuild processes, cleaning them up when your script exits.

## Getting Your Device UDID

```shellscript
# List connected devices
idevice_id -l

# Or use Xcode
# Window → Devices and Simulators → Select your device
```

---

## Troubleshooting

"Untrusted Developer" error

"A valid provisioning profile was not found"

"iPhone is locked" error

Build failures or xcodebuild errors

Connection timeout or WDA not responding

**Troubleshooting**:

1. Verify WDA is running on device (you should see the WDA screen)
2. Check iproxy is running: `ps aux | grep iproxy`
3. Test WDA manually: `curl http://localhost:8100/status`
4. Restart your device and try again
5. Increase timeout in config: `wda_startup_timeout=180.0`

For more troubleshooting help, check the [Troubleshooting Guide](https://www.minitap.ai/docs/mobile-use-sdk/troubleshooting) or join our [Discord community](https://discord.gg/6nSqmQ9pQs).

---

## Next Steps

## Explore Examples

Check out real-world automation examples

## Learn Core Concepts

Understand tasks, profiles, and builders

## Platform Integration

Add observability with Minitap Platform

## SDK Reference

Dive into the complete API documentation
