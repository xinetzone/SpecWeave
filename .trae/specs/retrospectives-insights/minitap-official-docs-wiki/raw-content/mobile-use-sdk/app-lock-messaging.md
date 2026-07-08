This example demonstrates how to use the app lock feature to keep automation within a specific app (WhatsApp in this case). The app lock ensures the agent stays in the messaging app even if the user accidentally navigates away.

This example is available on GitHub: [app\_lock\_messaging.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/app_lock_messaging.py)

## What This Example Does

## Key Concepts

## App Lock

Restricts execution to a specific app package/bundle ID

## Automatic Relaunch

Agent relaunches app if user accidentally navigates away

## Builder Pattern

Uses TaskRequestBuilder for advanced configuration

## Structured Output

Returns typed results with Pydantic

## Complete Code

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

class MessageResult(BaseModel):
    """Structured result from messaging task."""

    messages_sent: int = Field(..., description="Number of messages successfully sent")
    contacts: List[str] = Field(..., description="List of contacts messaged")
    success: bool = Field(..., description="Whether all messages were sent successfully")

async def main() -> None:
    # Create agent with default configuration
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)

    try:
        await agent.init()

        # Use app lock to keep execution in WhatsApp
        # This ensures the agent stays in the app and relaunches if needed
        task = (
            agent.new_task(
                "Send 'Happy New Year!' message to Alice, Bob, and Charlie on WhatsApp"
            )
            .with_name("send_new_year_messages")
            .with_locked_app_package("com.whatsapp")  # Lock to WhatsApp
            .with_output_format(MessageResult)
            .with_max_steps(600)  # Messaging tasks may need more steps
            .build()
        )

        print("Sending messages with app lock enabled...")
        print("The agent will stay in WhatsApp and relaunch if needed.\n")

        result = await agent.run_task(request=task)

        if result:
            print("\n=== Messaging Complete ===")
            print(f"Messages sent: {result.messages_sent}")
            print(f"Contacts: {', '.join(result.contacts)}")
            print(f"Success: {result.success}")
        else:
            print("Failed to send messages")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## Code Breakdown

### 1\. Define Output Structure

```python
class MessageResult(BaseModel):
    messages_sent: int = Field(..., description="Number of messages successfully sent")
    contacts: List[str] = Field(..., description="List of contacts messaged")
    success: bool = Field(..., description="Whether all messages were sent successfully")
```

Clear field descriptions help the LLM extract accurate data.

### 2\. Create Agent Configuration

```python
profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
config = Builders.AgentConfig.with_default_profile(profile).build()
agent = Agent(config=config)
```

Make sure your `llm-config.defaults.jsonc` includes the Contextor agent configuration for app lock support.

### 3\. Build Task with App Lock

```python
task = (
    agent.new_task("Send 'Happy New Year!' message to Alice, Bob, and Charlie on WhatsApp")
    .with_name("send_new_year_messages")
    .with_locked_app_package("com.whatsapp")  # Lock to WhatsApp
    .with_output_format(MessageResult)
    .with_max_steps(600)
    .build()
)
```

Key points:

- `with_locked_app_package()` activates app lock with the WhatsApp package name
- Use the full package name (Android: `com.whatsapp` or iOS: `com.whatsapp`)
- Consider increasing `max_steps` for complex tasks with multiple interactions

### 4\. Run Task and Handle Results

```python
result = await agent.run_task(request=task)

if result:
    print(f"Messages sent: {result.messages_sent}")
    print(f"Contacts: {', '.join(result.contacts)}")
```

The result is typed as `MessageResult | None` for type safety.

## Finding Your App Package Name

- Android
- iOS

**WhatsApp:**

```shellscript
adb shell pm list packages | grep whatsapp
# Output: package:com.whatsapp
```

**Other apps:**

```shellscript
adb shell pm list packages | grep [app-name]
```

**Common bundle IDs:**

- WhatsApp: `com.whatsapp`
- Telegram: `ph.telegra.Telegraph`
- Messages: `com.apple.MobileSMS`
- Instagram: `com.burbn.instagram`

## LLM Configuration

Make sure your `llm-config.defaults.jsonc` includes Contextor configuration:

```jsonc
{
  "contextor": {
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  // ... other agents
}
```

## Running the Example

## Expected Output

```text
Sending messages with app lock enabled...
The agent will stay in WhatsApp and relaunch if needed.

=== Messaging Complete ===
Messages sent: 3
Contacts: Alice, Bob, Charlie
Success: True
```

## How App Lock Works

When you enable app lock:

1. **Initial Launch**: Agent verifies WhatsApp is open, launches it if needed
2. **Runtime Monitoring**: Contextor agent monitors app changes at each step
3. **Smart Decisions**: If user leaves WhatsApp, Contextor decides:
	- Allow the deviation (e.g., OAuth flows, system dialogs)
		- Relaunch the app (e.g., accidental navigation)
4. **Completion**: Task continues until goal is achieved

---

## Platform App Lock

Instead of configuring app lock in code, you can configure it on the platform:

### Configure on Platform

When creating a task on [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks):

```text
Name: send-whatsapp-message
Agent Prompt: Send "<message>" to <contact> on WhatsApp
Locked App Package: com.whatsapp
```

The task will display a 🔒 indicator showing the locked package.

### Execute via SDK

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

# The app lock configured on the platform is automatically applied
result = await agent.run_task(
    request=PlatformTaskRequest(task="send-whatsapp-message")
)
```

`PlatformTaskRequest` does **not** support overriding `locked_app_package` via SDK. To change the locked app, update the platform task configuration.

### Execute via Cloud (No Code)

You can also run tasks with app lock directly from the platform UI:

1. Go to [**Tasks**](https://platform.mobile-use.ai/tasks)
2. Click **Run** on the task card (shows 🔒 indicator)
3. Select **Cloud Execution** tab
4. Choose LLM profile and cloud device
5. Click **Run Task**

Platform app lock is ideal when you want consistent app restriction across all executions without code changes.

## Customization Ideas

Lock to different app

```python
# Telegram
.with_locked_app_package("org.telegram.messenger")

# Signal
.with_locked_app_package("org.signal.android")
```

Send to many contacts

```python
contacts = ["Alice", "Bob", "Charlie", "Diana", "Eve"]
contact_list = ", ".join(contacts)

task = agent.new_task(
    f"Send 'Happy New Year!' to {contact_list} on WhatsApp"
).with_locked_app_package("com.whatsapp")
```

Handle with profile

```python
# Use a specific profile for better accuracy
task = (
    agent.new_task("Send messages to Alice, Bob, Charlie")
    .with_locked_app_package("com.whatsapp")
    .using_profile("accurate")  # Use a more capable model
)
```

## Troubleshooting

### App Fails to Launch

```text
Error: Failed to launch com.whatsapp after 3 attempts
```

**Solutions:**

- Verify WhatsApp is installed: `adb shell pm list packages | grep whatsapp`
- Ensure device is unlocked
- Check package name is correct
- Try launching manually: `adb shell monkey -p com.whatsapp 1`

### Agent Repeatedly Relaunches App

If the agent keeps relaunching WhatsApp:

- Check agent thoughts to understand why it’s leaving
- The task may require actions outside WhatsApp (e.g., verification)
- Consider removing app lock for that specific action

## What’s Next

## Tasks and Task Requests

Learn more about task configuration options

## Agent Profiles

Configure Contextor agent settings

## Smart Notification Assistant

Explore more advanced examples
