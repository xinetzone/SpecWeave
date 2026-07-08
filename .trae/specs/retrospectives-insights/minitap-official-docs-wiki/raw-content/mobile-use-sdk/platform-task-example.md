This example demonstrates how to use the mobile-use SDK with [Minitap Platform](https://platform.mobile-use.ai/) for centralized task orchestration and observability.

## What This Example Does

## Key Concepts

## Platform Configuration

Tasks and profiles managed on web UI

## Unified API Keys

Single API key for all LLM providers

## Cloud Observability

View task runs, traces, and analytics online

## Type Safety

Structured output with Pydantic models

## App Lock

Restrict task execution to specific apps

## Cloud Execution

Run tasks from UI on cloud devices

## Prerequisites

Before running this example, complete the [Platform Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/platform-quickstart):

## Complete Code

```python
import asyncio
import os
from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List

from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest, DevicePlatform
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types.exceptions import PlatformServiceError

# Define output structures
class Email(BaseModel):
    sender: str = Field(..., description="Email sender name/address")
    subject: str = Field(..., description="Email subject line")
    is_unread: bool = Field(..., description="Whether email is unread")

class EmailSummary(BaseModel):
    total_emails: int = Field(..., description="Total number of emails")
    unread_count: int = Field(..., description="Number of unread emails")
    recent_emails: List[Email] = Field(
        default_factory=list,
        description="List of recent emails"
    )

class MeetingInfo(BaseModel):
    title: str = Field(..., description="Meeting title")
    date: str = Field(..., description="Meeting date")
    time: str = Field(..., description="Meeting time")
    attendees: List[str] = Field(..., description="List of attendees")
    confirmed: bool = Field(..., description="Whether meeting was confirmed")

async def main():
    """
    Main execution demonstrating Minitap Platform usage.
    
    This example shows:
    1. Using platform-configured tasks
    2. Switching between different LLM profiles
    3. Structured output with type safety
    4. Error handling for platform errors
    """
    
    # Verify API key is configured
    if not os.getenv("MINITAP_API_KEY"):
        print("❌ Error: MINITAP_API_KEY environment variable not set")
        print("   Get your API key from: https://platform.mobile-use.ai/api-keys")
        return
    
    print("🚀 Starting platform task example...\n")
    
    # Configure agent with specific device
    config = (
        Builders.AgentConfig
        .for_device(platform=DevicePlatform.ANDROID, device_id="emulator-5554")
        .build()
    )
    
    agent = Agent(config=config)
    
    try:
        # Initialize agent
        print("📱 Initializing agent...")
        if not await agent.init():
            print("❌ Failed to initialize agent")
            return
        print("✅ Agent initialized\n")
        
        # ===================================================================
        # Task 1: Email Summary (using "default" profile)
        # ===================================================================
        print("=" * 60)
        print("TASK 1: Email Summary")
        print("=" * 60)
        print("Profile: default")
        print("Task: email-summary (configured on platform)")
        print()
        
        try:
            email_result = await agent.run_task(
                request=PlatformTaskRequest[EmailSummary](
                    task="email-summary",
                    profile="default",
                    # Local trace recording (in addition to platform)
                    record_trace=True,
                    trace_path=Path(f"/tmp/platform-traces/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                )
            )
            
            if email_result:
                print("✅ Email summary retrieved:")
                print(f"   Total emails: {email_result.total_emails}")
                print(f"   Unread: {email_result.unread_count}")
                print(f"\n   Recent emails:")
                for i, email in enumerate(email_result.recent_emails[:5], 1):
                    status = "📬" if email.is_unread else "📭"
                    print(f"   {i}. {status} {email.sender}: {email.subject}")
            else:
                print("⚠️  No result returned")
        
        except PlatformServiceError as e:
            print(f"❌ Platform error: {e}")
            print("   Check that 'email-summary' task exists on platform")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()
        
        # ===================================================================
        # Task 2: Schedule Meeting (using "accurate" profile)
        # ===================================================================
        print("=" * 60)
        print("TASK 2: Schedule Meeting")
        print("=" * 60)
        print("Profile: accurate (more powerful models)")
        print("Task: schedule-meeting (configured on platform)")
        print()
        
        try:
            meeting_result = await agent.run_task(
                request=PlatformTaskRequest[MeetingInfo](
                    task="schedule-meeting",
                    profile="accurate",  # Use more powerful profile
                    record_trace=True,
                    trace_path=Path(f"/tmp/platform-traces/{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                )
            )
            
            if meeting_result:
                print("✅ Meeting scheduled:")
                print(f"   Title: {meeting_result.title}")
                print(f"   Date: {meeting_result.date}")
                print(f"   Time: {meeting_result.time}")
                print(f"   Attendees: {', '.join(meeting_result.attendees)}")
                print(f"   Confirmed: {'✅' if meeting_result.confirmed else '⏳'}")
            else:
                print("⚠️  No result returned")
        
        except PlatformServiceError as e:
            print(f"❌ Platform error: {e}")
            print("   Check that 'schedule-meeting' task exists on platform")
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
        
        print()
        
        # ===================================================================
        # Summary
        # ===================================================================
        print("=" * 60)
        print("📊 Summary")
        print("=" * 60)
        print("✓ View task runs at: https://platform.mobile-use.ai/task-runs")
        print("✓ See execution timelines, screenshots, and agent thoughts")
        print("✓ Analyze performance and debug failures")
        print()
    
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    
    finally:
        print("🧹 Cleaning up...")
        await agent.clean()
        print("✅ Done!\n")

if __name__ == "__main__":
    asyncio.run(main())
```

## Code Breakdown

### 1\. Define Output Structures

```python
class EmailSummary(BaseModel):
    total_emails: int
    unread_count: int
    recent_emails: List[Email]
```

Even though tasks are configured on the platform, you can still define Pydantic models for type-safe results.

### 2\. Verify API Key

```python
if not os.getenv("MINITAP_API_KEY"):
    print("Error: MINITAP_API_KEY not set")
    return
```

Always check that the API key is configured before running tasks.

### 3\. Use Different Profiles

```python
# Fast, cost-effective profile for simple tasks
email_result = await agent.run_task(
    request=PlatformTaskRequest[EmailSummary](
        task="email-summary",
        profile="default"
    )
)

# Powerful profile for complex tasks
meeting_result = await agent.run_task(
    request=PlatformTaskRequest[MeetingInfo](
        task="schedule-meeting",
        profile="accurate"
    )
)
```

### 4\. Handle Platform Errors

```python
try:
    result = await agent.run_task(request=PlatformTaskRequest(...))
except PlatformServiceError as e:
    print(f"Platform error: {e}")
    # Task not found, profile not found, auth error, etc.
except Exception as e:
    print(f"Other error: {e}")
```

## Running the Example

## Expected Output

```text
🚀 Starting platform task example...

📱 Initializing agent...
✅ Agent initialized

============================================================
TASK 1: Email Summary
============================================================
Profile: default
Task: email-summary (configured on platform)

✅ Email summary retrieved:
   Total emails: 23
   Unread: 5

   Recent emails:
   1. 📬 john@company.com: Project Update
   2. 📬 sarah@team.com: Meeting Tomorrow
   3. 📭 notifications@service.com: Weekly Digest
   4. 📬 boss@company.com: Urgent: Review Needed
   5. 📭 newsletter@tech.com: Latest Tech News

============================================================
TASK 2: Schedule Meeting
============================================================
Profile: accurate (more powerful models)
Task: schedule-meeting (configured on platform)

✅ Meeting scheduled:
   Title: Q4 Planning Session
   Date: 2024-10-15
   Time: 14:00
   Attendees: John, Sarah, Mike
   Confirmed: ✅

============================================================
📊 Summary
============================================================
✓ View task runs at: https://platform.mobile-use.ai/task-runs
✓ See execution timelines, screenshots, and agent thoughts
✓ Analyze performance and debug failures

🧹 Cleaning up...
✅ Done!
```

## Viewing on Platform

After running, visit the platform to see detailed execution:

- Task Runs List
- Run Details
- Analytics

- All your task runs with status
- Filter by task, status, date
- Quick status overview

- Execution timeline
- Step-by-step progression
- Agent thoughts & reasoning
- Screenshots (if tracing enabled)
- Final output
- Error details (if failed)

- Success rate
- Average execution time
- Most used tasks
- Error patterns

## Platform Task Configuration

For this example to work, create these tasks on the platform:

### Email Summary Task

```text
Name: email-summary
Description: Check and summarize recent emails

Input Prompt:
Open the Gmail app. Navigate to the inbox and check recent emails.
Count total emails and unread emails. Get details (sender, subject, 
unread status) for the 5 most recent emails.

Output Description:
JSON object with total_emails, unread_count, and a list of recent 
emails with sender, subject, and is_unread fields.

Options:
- Enable Tracing: ✅
- Max Steps: 400
```

### Schedule Meeting Task

```text
Name: schedule-meeting
Description: Schedule a calendar meeting

Input Prompt:
Open the Calendar app. Create a new event titled "Q4 Planning Session"
for tomorrow at 2 PM. Add John, Sarah, and Mike as attendees.
Confirm the meeting is created.

Output Description:
JSON object with meeting title, date, time, list of attendees,
and confirmation status.

Options:
- Enable Tracing: ✅
- Max Steps: 500
```

## Running with Locked App Package

You can lock task execution to a specific app, ensuring the agent stays within that app:

### On the Platform

When creating a task, specify the **Locked App Package** field:

```text
Name: whatsapp-message
Agent Prompt: Send a message to <contact> saying "<message>"
Locked App Package: com.whatsapp
```

### Via SDK

Execute the platform task with its configured app lock:

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

# The app lock configured on the platform is automatically applied
result = await agent.run_task(
    request=PlatformTaskRequest(task="whatsapp-message")
)
```

`PlatformTaskRequest` does **not** support overriding `locked_app_package` via SDK. The app lock must be configured on the platform task itself.

---

## Cloud Execution (No Code Required)

Instead of running tasks via SDK, you can execute directly from the platform UI:

### How It Works

### Local SDK vs Cloud Execution

| Aspect | Local SDK | Cloud Execution |
| --- | --- | --- |
| **Setup** | Python + SDK install | None |
| **Device** | Physical/Emulator | Cloud managed |
| **Best for** | Development, CI/CD | Quick tests, no-code users |
| **Customization** | Full programmatic control | UI configuration only |

Cloud Execution is ideal for non-technical team members or quick testing without local environment setup.

---

## Customization Ideas

Add more tasks

Create specialized profiles

Local + Platform hybrid

```python
# Quick local test
await agent.run_task(
    request=TaskRequest(goal="Quick test")
)

# Production via platform
await agent.run_task(
    request=PlatformTaskRequest(task="production-task")
)
```

Scheduled execution

```python
import schedule

async def check_emails():
    result = await agent.run_task(
        request=PlatformTaskRequest(task="email-summary")
    )
    # Process result...

schedule.every().hour.do(lambda: asyncio.run(check_emails()))
```

## Benefits Demonstrated

## Centralized Config

Change task prompts without code changes

## Unified API Keys

One key for all LLM providers

## Cloud Observability

View all runs in one dashboard

## Profile Switching

Easy to switch between model configurations

## Type Safety

Pydantic models ensure data integrity

## Team Collaboration

Share tasks and profiles with team

## Troubleshooting

Task not found error

```text
PlatformServiceError: Failed to get task: 404
```

**Solution:**

- Verify task name matches exactly (case-sensitive)
- Check task exists at [https://platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks)
- Ensure you’re using the correct API key

Profile not found error

```text
PlatformServiceError: Failed to get agent profile: 404
```

**Solution:**

- Check profile name spelling
- Verify profile exists at [https://platform.mobile-use.ai/llm-profiles](https://platform.mobile-use.ai/llm-profiles)
- Try using “default” profile

Authentication error

```text
PlatformServiceError: Please provide an API key
```

**Solution:**

```shellscript
# Set environment variable
export MINITAP_API_KEY="your_key"

# Or pass to agent.init()
await agent.init(api_key="your_key")
```

## Next Steps

## Platform Quickstart

Complete platform setup guide

## Types Reference

PlatformTaskRequest type documentation

## Local Examples

Compare with local approach

## Dashboard

Open Minitap Platform
