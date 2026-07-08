The `TaskRequestBuilder` class provides a fluent interface for configuring task requests with detailed options.

## Import

```python
# Access through agent.new_task()
task_builder = agent.new_task("Your goal here")

# Or import directly
from minitap.mobile_use.sdk.builders import TaskRequestBuilder
```

## Creating a Builder

Use `agent.new_task()` to create a builder:

```python
task = agent.new_task("Open settings and check notifications")
```

## Methods

### with\_name

Set a descriptive name for the task (used in logging and tracing).

```python
def with_name(self, name: str) -> TaskRequestBuilder[TOutput]
```name

str

required

Task name for identification

```python
task = agent.new_task(goal).with_name("notification_check")
```

---

### with\_max\_steps

Set the maximum number of steps (actions) the task can take.

```python
def with_max_steps(self, max_steps: int) -> TaskRequestBuilder[TOutput]
```max\_steps

int

required

Maximum number of steps (default is 400)

```python
task = agent.new_task(goal).with_max_steps(500)
```

Each step corresponds to one action (tap, swipe, etc.) executed by the agent.

---

### with\_output\_format

Specify a Pydantic model class for structured, type-safe output.

```python
def with_output_format(
    self, 
    output_format: type[TNewOutput]
) -> TaskRequestBuilder[TNewOutput]
```output\_format

type\[BaseModel\]

required

Pydantic model class defining the output structure

```python
from pydantic import BaseModel, Field

class EmailSummary(BaseModel):
    total: int = Field(..., description="Total emails")
    unread: int = Field(..., description="Unread count")

task = (
    agent.new_task("Check my inbox")
    .with_output_format(EmailSummary)
)
```

Use detailed field descriptions to help the LLM extract correct data.

---

### with\_output\_description

Provide a natural language description of the expected output format.

```python
def with_output_description(self, description: str) -> TaskRequestBuilder[TOutput]
```description

str

required

Description of the expected output format

```python
task = (
    agent.new_task("List my contacts")
    .with_output_description("A comma-separated list of contact names")
)
```

---

### using\_profile

Specify which agent profile to use for this task.

```python
def using_profile(self, profile: str | AgentProfile) -> TaskRequestBuilder[TOutput]
```

Profile name (string) or AgentProfile instance

```python
# Using profile name
task = agent.new_task(goal).using_profile("accurate")

# Using profile instance
from minitap.mobile_use.sdk.types import AgentProfile
profile = AgentProfile(name="fast", from_file="fast.jsonc")
task = agent.new_task(goal).using_profile(profile)
```

---

### with\_trace\_recording

Enable or disable execution tracing for debugging and visualization.

```python
def with_trace_recording(
    self, 
    enabled: bool = True, 
    path: str | Path | None = None
) -> TaskRequestBuilder[TOutput]
```enabled

bool

default:true

Whether to enable trace recordingpath

str | Path

Directory path to save traces (defaults to temp directory)

```python
from pathlib import Path

task = (
    agent.new_task(goal)
    .with_trace_recording(enabled=True, path=Path("/tmp/my-traces"))
)
```

Traces include screenshots at each step, making debugging much easier.

---

### with\_llm\_output\_saving

Configure where to save the final LLM output.

```python
def with_llm_output_saving(self, path: str) -> TaskRequestBuilder[TOutput]
```path

str

required

File path where LLM output will be saved (will be overwritten)

```python
task = (
    agent.new_task(goal)
    .with_llm_output_saving(path="/tmp/llm_output.json")
)
```

---

### with\_thoughts\_output\_saving

Configure where to save the agent’s thought process.

```python
def with_thoughts_output_saving(self, path: str) -> TaskRequestBuilder[TOutput]
```path

str

required

File path where agent thoughts will be saved (will be overwritten)

```python
task = (
    agent.new_task(goal)
    .with_thoughts_output_saving(path="/tmp/agent_thoughts.txt")
)
```

Agent thoughts reveal the reasoning process, helpful for understanding decisions.

---

### without\_llm\_output\_saving

Disable LLM output saving (if it was previously enabled).

```python
def without_llm_output_saving(self) -> TaskRequestBuilder[TOutput]
```

```python
task = agent.new_task(goal).without_llm_output_saving()
```

---

### without\_thoughts\_output\_saving

Disable agent thoughts saving (if it was previously enabled).

```python
def without_thoughts_output_saving(self) -> TaskRequestBuilder[TOutput]
```

```python
task = agent.new_task(goal).without_thoughts_output_saving()
```

---

### with\_locked\_app\_package

Lock task execution to a specific app package (Android) or bundle ID (iOS).

```python
def with_locked_app_package(self, package_name: str) -> TaskRequestBuilder[TOutput]
```package\_name

str

required

The app package name (Android) or bundle ID (iOS)

Only the package name should be specified, not the full path to the app or activity name.

When enabled:

- Verifies the app is open before starting
- Attempts to launch the app if not in foreground
- Monitors app changes during execution
- Automatically relaunches if user accidentally leaves the app

**Android Example:**

```python
task = agent.new_task("Send a message")
    .with_locked_app_package("com.whatsapp")
    .build()
```

**iOS Example:**

```python
task = agent.new_task("Send a message")
    .with_locked_app_package("com.apple.MobileSMS")
    .build()
```

The app lock feature requires the Contextor agent to be configured in your LLM profile. See the [Tasks and Task Requests](https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/tasks) guide for more details.

Use `adb shell pm list packages` on Android or consult iOS documentation to find the correct package/bundle ID.

---

### build

Build and return the final `TaskRequest` object.

```python
def build(self) -> TaskRequest[TOutput]
```task\_request

TaskRequest\[TOutput\]

The constructed task request ready for execution

```python
task_request = (
    agent.new_task("Your goal")
    .with_name("my_task")
    .build()
)

# Execute the task
result = await agent.run_task(request=task_request)
```

## Complete Example

```python
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

class AppInfo(BaseModel):
    name: str = Field(..., description="App name")
    version: str = Field(..., description="App version")
    size_mb: float = Field(..., description="App size in MB")

async def main():
    # Setup agent
    profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")
    config = Builders.AgentConfig.with_default_profile(profile).build()
    agent = Agent(config=config)
    
    try:
        agent.init()
        
        # Build comprehensive task configuration
        task = (
            agent.new_task("Go to App Store, search for Instagram, and get app details")
            .with_name("instagram_info")
            .with_max_steps(500)
            .with_output_format(AppInfo)
            .using_profile("default")
            .with_locked_app_package("com.android.vending")  # Lock to Google Play Store
            .with_trace_recording(enabled=True, path=Path("/tmp/instagram-trace"))
            .with_llm_output_saving(path="/tmp/instagram-output.json")
            .with_thoughts_output_saving(path="/tmp/instagram-thoughts.txt")
            .build()
        )
        
        # Execute
        result = await agent.run_task(request=task)
        
        if result:
            print(f"App: {result.name}")
            print(f"Version: {result.version}")
            print(f"Size: {result.size_mb} MB")
        
    finally:
        agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## Method Chaining

All builder methods (except `build()`) return the builder instance, allowing fluent method chaining:

```python
task = (
    agent.new_task("Goal")
    .with_name("task_1")              # Returns TaskRequestBuilder
    .with_max_steps(400)              # Returns TaskRequestBuilder
    .with_output_format(MyModel)      # Returns TaskRequestBuilder
    .with_trace_recording(True)       # Returns TaskRequestBuilder
    .build()                          # Returns TaskRequest
)
```

## Type Safety

The builder maintains type information for output:

```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    value: str

# Builder knows output type
task_builder = agent.new_task(goal).with_output_format(MyOutput)

# TaskRequest is typed as TaskRequest[MyOutput]
task_request = task_builder.build()

# Result is typed as MyOutput | None
result: MyOutput | None = await agent.run_task(request=task_request)
```

## Comparison

- With Builder
- Direct Call

```python
task = (
    agent.new_task("Check notifications")
    .with_name("notif_check")
    .with_max_steps(300)
    .with_trace_recording(True)
    .with_output_format(NotificationSummary)
    .build()
)

result = await agent.run_task(request=task)
```

✅ Full control over all options  
✅ Type-safe  
✅ Self-documenting

```python
result = await agent.run_task(
    goal="Check notifications",
    name="notif_check",
    output=NotificationSummary
)
```

✅ Simpler for basic tasks  
❌ Limited options available  
❌ Can’t configure tracing, max steps, etc.

## Next Steps

## Agent SDK

Learn about the Agent class

## Types

Explore TaskRequest and other types
