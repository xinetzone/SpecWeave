This guide covers using **BrowserStack** to run mobile automation on real physical iOS devices in the cloud without needing local hardware.

**Looking for other options?** Check out the [Local Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/quickstart) for local devices, [Cloud Mobile Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/cloud-quickstart) for Minitap cloud devices, or [Physical iOS Setup](https://www.minitap.ai/docs/mobile-use-sdk/physical-ios-quickstart) for USB-connected devices.

## What is BrowserStack?

BrowserStack App Automate provides access to real physical iOS devices in the cloud. Key benefits:

## Real Physical Devices

Test on actual iPhones and iPads, not simulators

## No Local Hardware

No need to own or maintain iOS devices

## CI/CD Ready

Perfect for automated testing pipelines

## Cross-Device Testing

Access multiple device models and iOS versions

---

## Prerequisites

---

## Creating Your First BrowserStack Automation

### Basic Example

```python
import asyncio
import os
from pydantic import SecretStr

from minitap.mobile_use.clients.ios_client_config import BrowserStackClientConfig
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import AgentConfigBuilder

async def main():
    # Get credentials from environment variables
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")

    if not username or not access_key:
        print("Error: Please set BROWSERSTACK_USERNAME and BROWSERSTACK_ACCESS_KEY")
        return

    # Configure BrowserStack connection
    browserstack_config = BrowserStackClientConfig(
        username=username,
        access_key=SecretStr(access_key),
        device_name="iPhone 17",              # Device to use
        platform_version="26",              # iOS version
        app_url="bs://your_app_hash_here",  # Your uploaded app
        build_name="mobile-use-demo",       # Optional: for organizing sessions
        session_name="My First Automation", # Optional: session identifier
    )

    # Build agent config for BrowserStack
    agent_config = AgentConfigBuilder().for_browserstack(browserstack_config).build()
    agent = Agent(config=agent_config)

    try:
        # Initialize the agent (creates BrowserStack session)
        print("Initializing BrowserStack session...")
        await agent.init()
        print("Session created successfully!")

        # Run your automation task
        result = await agent.run_task(
            goal="Fill the login form with test data",
        )

        print(f"Task Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Clean up (ends BrowserStack session)
        await agent.clean()
        print("Session ended.")

if __name__ == "__main__":
    asyncio.run(main())
```

### Run the Script

```shellscript
# Set your credentials
export BROWSERSTACK_USERNAME="your_username"
export BROWSERSTACK_ACCESS_KEY="your_access_key"

# Run the automation
python browserstack_demo.py
```

---

## Configuration Options

### BrowserStackClientConfig

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `username` | `str` | ✅ | Your BrowserStack username |
| `access_key` | `SecretStr` | ✅ | Your BrowserStack access key |
| `device_name` | `str` | ✅ | Device name (e.g., “iPhone 17”, “iPhone 16 Pro”) |
| `platform_version` | `str` | ✅ | iOS version (e.g., “17”, “18”, “26”) |
| `app_url` | `str` | ✅ | BrowserStack app URL (bs://…) |
| `hub_url` | `str \| None` | ❌ | Custom hub URL (defaults to BrowserStack cloud) |
| `project_name` | `str \| None` | ❌ | Project name for organizing sessions |
| `build_name` | `str \| None` | ❌ | Build name for grouping sessions |
| `session_name` | `str \| None` | ❌ | Human-readable session name |

### Available Devices

BrowserStack supports a wide range of iOS devices. Some popular options:

| Device | Example `device_name` | Available iOS Versions |
| --- | --- | --- |
| iPhone 17 Pro Max | `"iPhone 17 Pro Max"` | 26 |
| iPhone 17 Pro | `"iPhone 17 Pro"` | 26 |
| iPhone 17 | `"iPhone 17"` | 26 |
| iPhone 16 Pro Max | `"iPhone 16 Pro Max"` | 18 |
| iPhone 16 Pro | `"iPhone 16 Pro"` | 18 |
| iPhone 16 | `"iPhone 16"` | 18 |
| iPhone 15 Pro Max | `"iPhone 15 Pro Max"` | 17, 26 |
| iPhone 15 Pro | `"iPhone 15 Pro"` | 17 |
| iPhone 15 | `"iPhone 15"` | 17, 26 |
| iPad Pro 13 2025 | `"iPad Pro 13 2025"` | 26 |
| iPad Pro 11 2025 | `"iPad Pro 11 2025"` | 26 |
| iPad Air 6 | `"iPad Air 6"` | 17 |

Check [BrowserStack’s device list](https://www.browserstack.com/list-of-browsers-and-platforms/app_automate?tab=ios-listing) for the complete list of available devices.

---

## Environment Variables

For security, store your credentials as environment variables:

```shellscript
BROWSERSTACK_USERNAME=your_username
BROWSERSTACK_ACCESS_KEY=your_access_key
```

Then load them in your script:

```python
import os
from pydantic import SecretStr

username = os.environ.get("BROWSERSTACK_USERNAME")
access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")

browserstack_config = BrowserStackClientConfig(
    username=username,
    access_key=SecretStr(access_key),
    # ... other options
)
```

Never commit your `.env` file or hardcode credentials in your code. Add `.env` to your `.gitignore`.

---

## Viewing Session Results

After running your automation, you can view detailed session information in the BrowserStack dashboard:

1. Navigate to [BrowserStack App Automate Dashboard](https://app-automate.browserstack.com/)
2. Find your session by build name or session name
3. View:
	- Video recording of the session
		- Screenshots at each step
		- Device logs
		- Network logs

The session URL is also logged when the session starts:

```text
View session: https://app-automate.browserstack.com/dashboard/sessions/{session_id}
```

---

## Supported Operations

The BrowserStack client supports the following operations:

| Operation | Method | Description |
| --- | --- | --- |
| **Tap** | `tap(x, y)` | Tap at coordinates |
| **Swipe** | `swipe(x1, y1, x2, y2)` | Swipe gesture |
| **Screenshot** | `screenshot()` | Capture screen |
| **Type Text** | `text("hello")` | Type text input |
| **Launch App** | `launch(bundle_id)` | Launch app by bundle ID |
| **Terminate App** | `terminate(bundle_id)` | Close an app |
| **Open URL** | `open_url(url)` | Open a URL |
| **Press Button** | `button(type)` | Press hardware button (home, volume) |
| **UI Hierarchy** | `describe_all()` | Get UI element tree |

Some operations like `app_current()` and `install()` are not supported on BrowserStack. Apps must be pre-uploaded to BrowserStack.

---

## Complete Example with Structured Output

```python
import asyncio
import os
from pydantic import BaseModel, Field, SecretStr

from minitap.mobile_use.clients.ios_client_config import BrowserStackClientConfig
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import AgentConfigBuilder

class LoginResult(BaseModel):
    success: bool = Field(..., description="Whether login was successful")
    username_entered: str = Field(..., description="The username that was entered")
    error_message: str | None = Field(None, description="Error message if login failed")

async def main():
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")

    browserstack_config = BrowserStackClientConfig(
        username=username,
        access_key=SecretStr(access_key),
        device_name="iPhone 17",
        platform_version="26",
        app_url="bs://your_app_hash",
        build_name="structured-output-demo",
    )

    agent_config = AgentConfigBuilder().for_browserstack(browserstack_config).build()
    agent = Agent(config=agent_config)

    try:
        await agent.init()

        result = await agent.run_task(
            goal="Enter username 'testuser@example.com' and password 'Test123!' then tap the login button",
            output=LoginResult,
        )

        if result:
            print(f"Login successful: {result.success}")
            print(f"Username entered: {result.username_entered}")
            if result.error_message:
                print(f"Error: {result.error_message}")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Troubleshooting

Session fails to start

**Possible causes**:

- Invalid credentials
- Invalid app\_url
- Device/OS combination not available

**Solutions**:

1. Verify your username and access key
2. Re-upload your app and get a fresh `app_url`
3. Check [BrowserStack device list](https://www.browserstack.com/list-of-browsers-and-platforms/app_automate) for valid device/OS combinations

App not launching

**Possible causes**:

- App not properly signed
- App incompatible with selected iOS version

**Solutions**:

1. Ensure your.ipa is signed for distribution
2. Try a different iOS version that matches your app’s minimum deployment target

Timeout errors

Element not found

---

## Best Practices

## Use Environment Variables

Never hardcode credentials - use environment variables or secrets management

## Organize Sessions

Use `build_name` and `session_name` to organize and find sessions easily

## Handle Cleanup

Always use try/finally to ensure `agent.clean()` is called

## Check Device Availability

Verify device/OS combinations before running tests

---

## Next Steps

## Local Quickstart

Set up local device automation

## Cloud Mobiles

Use Minitap’s cloud devices

## SDK Reference

Complete Agent API documentation

## Examples

More automation examples
