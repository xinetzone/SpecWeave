This example demonstrates advanced SDK features for more complex automation scenarios. It analyzes notifications and takes actions based on their content.

This example is available on GitHub: [smart\_notification\_assistant.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/simple_photo_organizer.py)

## What This Example Does

## Advanced Features

## Multiple Profiles

Uses different LLM configurations for different tasks

## TaskRequestBuilder

Advanced task configuration with builder pattern

## Trace Recording

Captures screenshots and execution steps

## Exception Handling

Robust error handling with specific exceptions

## Complete Code

```python
import asyncio
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.types.exceptions import AgentError

class NotificationPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Notification(BaseModel):
    """Individual notification details."""

    app_name: str = Field(..., description="Name of the app that sent the notification")
    title: str = Field(..., description="Title/header of the notification")
    message: str = Field(..., description="Message content of the notification")
    priority: NotificationPriority = Field(
        default=NotificationPriority.MEDIUM, description="Priority level of notification"
    )

class NotificationSummary(BaseModel):
    """Summary of all notifications."""

    total_count: int = Field(..., description="Total number of notifications found")
    high_priority_count: int = Field(0, description="Count of high priority notifications")
    notifications: list[Notification] = Field(
        default_factory=list, description="List of individual notifications"
    )

def get_agent() -> Agent:
    # Create two specialized profiles:
    # 1. An analyzer profile for detailed inspection tasks
    analyzer_profile = AgentProfile(
        name="analyzer",
        llm_config=LLMConfig(
            planner=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
            orchestrator=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
            cortex=LLMWithFallback(
                provider="openai",
                model="o4-mini",
                fallback=LLM(provider="openai", model="gpt-5"),
            ),
            executor=LLM(provider="openai", model="gpt-5-nano"),
            utils=LLMConfigUtils(
                outputter=LLM(provider="openai", model="gpt-5-nano"),
                hopper=LLM(provider="openai", model="gpt-4.1"),
            ),
        ),
    )

    # 2. An action profile for handling fast actions
    action_profile = AgentProfile(
        name="note_taker",
        llm_config=LLMConfig(
            planner=LLM(provider="openai", model="o3"),
            orchestrator=LLM(provider="google", model="gemini-2.5-flash"),
            cortex=LLMWithFallback(
                provider="openai",
                model="o4-mini",
                fallback=LLM(provider="openai", model="gpt-5"),
            ),
            executor=LLM(provider="openai", model="gpt-4o-mini"),
            utils=LLMConfigUtils(
                outputter=LLM(provider="openai", model="gpt-5-nano"),
                hopper=LLM(provider="openai", model="gpt-4.1"),
            ),
        ),
    )

    # Configure default task settings
    task_defaults = Builders.TaskDefaults.with_max_steps(200).build()

    # Configure the agent
    config = (
        Builders.AgentConfig
        .add_profiles(profiles=[analyzer_profile, action_profile])
        .with_default_profile(profile=action_profile)
        .with_default_task_config(config=task_defaults)
        .build()
    )
    return Agent(config=config)

async def main():
    # Set up traces directory with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    traces_dir = f"/tmp/notification_traces/{timestamp}"
    agent = get_agent()

    try:
        # Initialize agent
        await agent.init()

        print("Checking for notifications...")

        # Task 1: Get and analyze notifications with analyzer profile
        notification_task = (
            agent.new_task(
                goal="Open the notification panel (swipe down from top). "
                "Scroll through the first 3 unread notifications. "
                "For each notification, identify the app name, title, and content. "
                "Tag messages from messaging apps or email as high priority."
            )
            .with_output_format(NotificationSummary)
            .using_profile("analyzer")
            .with_name("notification_scan")
            .with_max_steps(400)
            .with_trace_recording(enabled=True, path=traces_dir)
            .build()
        )

        # Execute the task with proper exception handling
        try:
            notifications = await agent.run_task(request=notification_task)

            # Display the structured results
            if notifications:
                print("\n=== Notification Summary ===")
                print(f"Total notifications: {notifications.total_count}")
                print(f"High priority: {notifications.high_priority_count}")

                # Task 2: Create a note to store the notification summary
                response = await agent.run_task(
                    goal="Open my Notes app and create a new note summarizing the following "
                    f"information:\n{notifications}",
                    name="email_action",
                    profile="note_taker",
                )
                print(f"Action result: {response}")

            else:
                print("Failed to retrieve notifications")

        except AgentError as e:
            print(f"Agent error occurred: {e}")
        except Exception as e:
            print(f"Unexpected error: {type(e).__name__}: {e}")
            raise

    finally:
        # Clean up
        await agent.clean()
        print(f"\nTraces saved to: {traces_dir}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Code Breakdown

### 1\. Define Output Structures

```python
class NotificationPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Notification(BaseModel):
    app_name: str
    title: str
    message: str
    priority: NotificationPriority

class NotificationSummary(BaseModel):
    total_count: int
    high_priority_count: int
    notifications: list[Notification]
```

Using enums for priority ensures the LLM returns only valid values.

### 2\. Create Specialized Profiles

```python
analyzer_profile = AgentProfile(
    name="analyzer",
    llm_config=LLMConfig(
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",  # Powerful model for analysis
            fallback=LLM(provider="openai", model="gpt-5")
        ),
        # ... other components
    )
)

action_profile = AgentProfile(
    name="note_taker",
    llm_config=LLMConfig(
        cortex=LLMWithFallback(
            provider="openai",
            model="o4-mini",
            fallback=LLM(provider="openai", model="gpt-5")
        ),
        # ... other components
    )
)
```

**Analyzer profile**: Uses powerful models for detailed inspection  
**Action profile**: Optimized for quick actions

### 3\. Configure Agent with Multiple Profiles

```python
config = (
    Builders.AgentConfig
    .add_profiles(profiles=[analyzer_profile, action_profile])
    .with_default_profile(profile=action_profile)
    .with_default_task_config(config=task_defaults)
    .build()
)
```

### 4\. Build Task with Advanced Options

```python
notification_task = (
    agent.new_task(goal)
    .with_output_format(NotificationSummary)  # Structured output
    .using_profile("analyzer")                 # Specific profile
    .with_name("notification_scan")            # Task name
    .with_max_steps(400)                       # Step limit
    .with_trace_recording(enabled=True, path=traces_dir)  # Tracing
    .build()
)
```

### 5\. Execute with Exception Handling

```python
try:
    notifications = await agent.run_task(request=notification_task)
    # Process results...
    
except AgentError as e:
    print(f"Agent error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
    raise
```

## Running the Example

## Expected Output

```text
Checking for notifications...

=== Notification Summary ===
Total notifications: 3
High priority: 2

Action result: Note created successfully with notification summary.

Traces saved to: /tmp/notification_traces/20241009_1730
```

## Key Concepts Demonstrated

Profile Switching

Different tasks use different profiles optimized for their purpose:

```python
# Analysis task uses "analyzer" profile
await agent.run_task(goal="Analyze notifications", profile="analyzer")

# Action task uses "note_taker" profile
await agent.run_task(goal="Create note", profile="note_taker")
```

Task Builder Pattern

Complex configuration is handled elegantly:

```python
task = (
    agent.new_task(goal)
    .with_output_format(MyModel)
    .with_max_steps(400)
    .with_trace_recording(True)
    .build()
)
```

Trace Recording

Captures execution for debugging:

- Screenshots at each step
- Agent decisions
- Action results

Invaluable for understanding what went wrong!

Nested Pydantic Models

Complex data structures with validation:

```python
class NotificationSummary(BaseModel):
    notifications: list[Notification]  # List of nested models
```

## Customization Ideas

- Different Actions
- Schedule-based
- Filter by App

```python
# Reply to high-priority messages
for notif in notifications.notifications:
    if notif.priority == NotificationPriority.HIGH:
        await agent.run_task(
            goal=f"Reply to {notif.app_name} message: '{notif.title}'",
            profile="action_profile"
        )
```

```python
# Only check during work hours
from datetime import datetime

hour = datetime.now().hour
if 9 <= hour <= 17:
    notifications = await agent.run_task(request=notification_task)
```

```python
goal = (
    "Open notification panel. "
    "Find notifications from WhatsApp and Gmail only. "
    "Ignore all other apps."
)
```

## Trace Analysis

After running, examine the traces:

```shellscript
# List trace files
ls /tmp/notification_traces/20241009_1730/

# View structure
notification_scan/
├── step_001_screenshot.png
├── step_002_screenshot.png
├── step_003_screenshot.png
└── execution_log.json
```

Each screenshot shows what the agent saw at that step, helping debug issues.

## Best Practices Shown

## Separate Profiles

Use different profiles for analysis vs. action

## Descriptive Names

Name tasks for easier debugging

## Enable Tracing

Always enable tracing during development

## Specific Exceptions

Catch AgentError separately from general exceptions

## Next Steps

## Core Concepts

Deep dive into profiles and builders

## SDK Reference

Complete TaskRequestBuilder reference
