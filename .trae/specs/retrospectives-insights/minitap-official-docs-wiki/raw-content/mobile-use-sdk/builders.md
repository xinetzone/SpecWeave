The mobile-use SDK provides builder classes that offer a fluent, type-safe way to configure agents and tasks. Builders make complex configurations more readable and help prevent errors.

## Why Use Builders?

## Readable

Chain methods for clear, self-documenting code

## Type-Safe

Catch configuration errors at development time

## Flexible

Easy to adjust configurations without rewriting code

## Discoverable

IDE autocomplete shows all available options

## Builders Overview

The SDK provides access to builders through the `Builders` object:

```python
from minitap.mobile_use.sdk.builders import Builders

# Agent configuration
agent_config = Builders.AgentConfig...

# Task defaults
task_defaults = Builders.TaskDefaults...
```

## Agent Config Builder

Configure how the agent connects to devices and servers:

### Basic Usage

```python
from minitap.mobile_use.sdk.builders import Builders
from minitap.mobile_use.sdk.types import AgentProfile

profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)

agent = Agent(config=config)
```

### Available Methods

with\_default\_profile

Set the default agent profile for tasks

```python
config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)
```

add\_profile / add\_profiles

Register additional profiles

```python
config = (
    Builders.AgentConfig
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .build()
)
```

for\_device

Target a specific device instead of auto-detection

```python
from minitap.mobile_use.sdk.types import DevicePlatform

config = (
    Builders.AgentConfig
    .for_device(
        platform=DevicePlatform.ANDROID,
        device_id="emulator-5554"
    )
    .build()
)
```

with\_adb\_server

Configure ADB server connection

```python
config = (
    Builders.AgentConfig
    .with_adb_server(host="localhost", port=5037)
    .build()
)
```

with\_default\_task\_config

Set default configuration for all tasks

```python
task_defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .build()
)

config = (
    Builders.AgentConfig
    .with_default_task_config(task_defaults)
    .build()
)
```

### Complete Example

```python
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

agent = Agent(config=config)
```

## Task Request Builder

Create detailed task configurations:

### Basic Usage

```python
task = (
    agent.new_task("Open settings and check notifications")
    .with_name("check_notifications")
    .build()
)

result = await agent.run_task(request=task)
```

### Available Methods

with\_name

Set a descriptive name for logging

```python
task = agent.new_task(goal).with_name("my_task").build()
```

with\_max\_steps

Limit the number of actions

```python
task = agent.new_task(goal).with_max_steps(300).build()
```

with\_output\_format

Specify Pydantic model for output

```python
task = (
    agent.new_task(goal)
    .with_output_format(MyModel)
    .build()
)
```

with\_output\_description

Describe expected output format

```python
task = (
    agent.new_task(goal)
    .with_output_description("A comma-separated list")
    .build()
)
```

using\_profile

Use a specific agent profile

```python
task = (
    agent.new_task(goal)
    .using_profile("accurate")
    .build()
)
```

with\_trace\_recording

Enable execution tracing

```python
from pathlib import Path

task = (
    agent.new_task(goal)
    .with_trace_recording(enabled=True, path=Path("/tmp/traces"))
    .build()
)
```

with\_llm\_output\_saving

Save final LLM output to file

```python
task = (
    agent.new_task(goal)
    .with_llm_output_saving(path="/tmp/output.json")
    .build()
)
```

with\_thoughts\_output\_saving

Save agent reasoning to file

```python
task = (
    agent.new_task(goal)
    .with_thoughts_output_saving(path="/tmp/thoughts.txt")
    .build()
)
```

### Complete Example

```python
from pathlib import Path
from pydantic import BaseModel, Field

class EmailSummary(BaseModel):
    total: int = Field(..., description="Total number of emails")
    unread: int = Field(..., description="Number of unread emails")

task = (
    agent.new_task("Open Gmail and analyze my inbox")
    .with_name("gmail_analysis")
    .with_max_steps(400)
    .with_output_format(EmailSummary)
    .using_profile("accurate")
    .with_trace_recording(enabled=True, path=Path("/tmp/gmail-trace"))
    .with_llm_output_saving(path="/tmp/gmail-output.json")
    .with_thoughts_output_saving(path="/tmp/gmail-thoughts.txt")
    .build()
)

result = await agent.run_task(request=task)
```

## Task Defaults Builder

Set defaults that apply to all tasks:

```python
from minitap.mobile_use.sdk.builders import Builders

# Configure defaults
defaults = (
    Builders.TaskDefaults
    .with_max_steps(500)
    .with_trace_recording(enabled=True)
    .build()
)

# Apply to agent
config = (
    Builders.AgentConfig
    .with_default_task_config(defaults)
    .build()
)

agent = Agent(config=config)

# All tasks will inherit these defaults
await agent.run_task(goal="Any task here")
```

## Method Chaining

Builders use method chaining for fluent configuration:

```python
# Each method returns the builder instance
result = (
    agent.new_task("My goal")
    .with_name("task_1")          # Returns TaskRequestBuilder
    .with_max_steps(300)          # Returns TaskRequestBuilder
    .with_trace_recording(True)   # Returns TaskRequestBuilder
    .build()                      # Returns TaskRequest
)
```

Use parentheses and line breaks for readability when chaining many methods.

## Type Safety

Builders provide compile-time type checking:

```python
from pydantic import BaseModel

class MyOutput(BaseModel):
    value: str

# Type-safe: MyOutput or None
task = agent.new_task(goal).with_output_format(MyOutput).build()
result: MyOutput | None = await agent.run_task(request=task)

# Can safely access fields
if result:
    print(result.value)  # IDE knows 'value' exists
```

## Comparison: With vs Without Builders

- Without Builders

```python
task = (
    agent.new_task("Check notifications")
    .with_name("notification_check")
    .with_max_steps(200)
    .with_trace_recording(True)
    .build()
)

result = await agent.run_task(request=task)
```

✅ Clear and readable  
✅ Type-safe  
✅ Easy to modify

```python
# Direct method call with many parameters
result = await agent.run_task(
    goal="Check notifications",
    name="notification_check",
    # max_steps needs TaskRequest...
    # trace recording needs TaskRequest...
)
```

❌ Limited options via direct call  
❌ Less discoverable  
❌ Harder to customize

## Best Practices

## Use builders for complex configs

Builders shine when you need multiple configuration options

## Simple tasks can use direct calls

For basic tasks, `agent.run_task(goal="...")` is fine

## Create reusable configurations

Build common configs once and reuse them

## Leverage IDE autocomplete

Let your IDE suggest available builder methods

## Next Steps

## Agent SDK

Detailed Agent SDK reference

## Task Builder SDK

Complete TaskRequestBuilder reference
