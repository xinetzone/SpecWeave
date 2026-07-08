Tasks represent automation workflows to be executed on a mobile device. They are defined using natural language goals and can return structured, type-safe results.

## Task Characteristics

## Goal-based

Define what you want using natural language

## Traceable

Record execution for debugging and visualization

## Structured Output

Return typed Pydantic models

## Platform Tasks

**Using the platform?** Create tasks on [platform.mobile-use.ai/tasks](https://platform.mobile-use.ai/tasks) and execute them with `PlatformTaskRequest`.

### Creating Platform Tasks

1. Go to [**Tasks**](https://platform.mobile-use.ai/tasks) on the platform
2. Click **Create Task**
3. Configure task details:
	- **Name**: Unique identifier (e.g., `check-notifications`)
		- **Agent Prompt**: Detailed instructions
		- **Output Description**: Optional structured output format
		- **Locked App Package**: Optional app package to restrict execution (e.g., `com.whatsapp`)
4. Use in your code:

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

result = await agent.run_task(
    request=PlatformTaskRequest(task="check-notifications")
)
```

### Platform Task with Structured Output

```python
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk.types import PlatformTaskRequest

class NotificationSummary(BaseModel):
    total: int = Field(..., description="Total notifications")
    unread: int = Field(..., description="Unread count")

result = await agent.run_task(
    request=PlatformTaskRequest[NotificationSummary](
        task="check-notifications",
        profile="fast"  # Optional: use specific platform profile
    )
)

if result:
    print(f"Total: {result.total}, Unread: {result.unread}")
```

### Platform Task with Locked App Package

When creating a task on the platform, you can specify a **Locked App Package** to restrict the agent to a specific app:

```text
Name: send-whatsapp-message
Agent Prompt: Send the message "<message>" to <contact> on WhatsApp
Locked App Package: com.whatsapp
```

The task will be displayed with a 🔒 indicator showing the locked package.

**Using the `<locked-app-package>` placeholder:**

You can reference the locked app package in your agent prompt using the `<locked-app-package>` placeholder:

```text
Open <locked-app-package> and navigate to settings
```

This placeholder will be automatically replaced with the configured package name at execution time.

### Platform Task Benefits

## Centralized Management

Update task prompts on the platform without redeploying code

## Built-in Observability

View execution details, costs, and agent thoughts on the platform

## Team Collaboration

Share tasks across your organization

## Version Control

Track changes to task configurations over time

---

## Local Tasks

For local development, define tasks directly in code:

### Simple String Output

The most basic way to run a local task:

```python
result = await agent.run_task(
    goal="Open settings and enable dark mode"
)
print(result)  # String output
```

### Structured Output with Pydantic

Get type-safe, validated output:

```python
from pydantic import BaseModel, Field

class ThemeSettings(BaseModel):
    dark_mode_enabled: bool = Field(..., description="Whether dark mode is enabled")
    theme_name: str = Field(..., description="Name of the current theme")

result = await agent.run_task(
    goal="Check the current theme settings",
    output=ThemeSettings
)

print(f"Dark mode: {result.dark_mode_enabled}")
print(f"Theme: {result.theme_name}")
```

### With Output Description

Provide guidance for unstructured output:

```python
result = await agent.run_task(
    goal="Find all my unread emails",
    output="A comma-separated list of email subjects"
)
```

## Task Options

### Naming Tasks

Give your tasks descriptive names for logging:

```python
await agent.run_task(
    goal="Send a message to John",
    name="send_message_john"
)
```

### Using Different Profiles

Switch agent profiles for specific tasks:

```python
await agent.run_task(
    goal="Analyze this complex form",
    profile="detail_oriented"  # Uses a different LLM configuration
)
```

### Maximum Steps

Control how many actions the agent can take:

```python
task = (
    agent.new_task("Complete checkout process")
    .with_max_steps(500)  # Default is 400
    .build()
)

await agent.run_task(request=task)
```

### App Lock

Restrict task execution to a specific app:

```python
task = (
    agent.new_task("Send a message to Alice")
    .with_locked_app_package("com.whatsapp")  # Android package or iOS bundle ID
    .build()
)

await agent.run_task(request=task)
```

When app lock is enabled, the agent will:

- Verify the app is open before starting
- Attempt to launch it if not in foreground
- Monitor app changes during execution
- Automatically relaunch if needed

## Task Builder Pattern

For advanced configuration, use the builder pattern:

```python
task_request = (
    agent.new_task("Open settings and check notifications")
    .with_name("check_notification_settings")
    .with_max_steps(300)
    .with_output_description("Summary of notification settings")
    .with_locked_app_package("com.android.settings")
    .with_trace_recording(enabled=True)
    .build()
)

result = await agent.run_task(request=task_request)
```

## Tracing and Debugging

Enable trace recording to capture screenshots and execution steps:

```python
from pathlib import Path

task = (
    agent.new_task("Navigate to profile settings")
    .with_trace_recording(
        enabled=True,
        path=Path("/tmp/my-traces")
    )
    .build()
)

await agent.run_task(request=task)
```

Traces include screenshots at each step, making it easy to debug failed tasks.

## Saving Output

### Save LLM Output

Save the final LLM response to a file:

```python
task = (
    agent.new_task("Extract product information")
    .with_llm_output_saving(path="/tmp/llm_output.json")
    .build()
)
```

### Save Agent Thoughts

Capture the agent’s reasoning process:

```python
task = (
    agent.new_task("Book a restaurant reservation")
    .with_thoughts_output_saving(path="/tmp/agent_thoughts.txt")
    .build()
)
```

## Complex Output Structures

Define complex, nested output structures:

```python
from pydantic import BaseModel, Field
from typing import List

class Email(BaseModel):
    sender: str
    subject: str
    preview: str
    is_unread: bool

class InboxSummary(BaseModel):
    total_emails: int = Field(..., description="Total number of emails")
    unread_count: int = Field(..., description="Number of unread emails")
    emails: List[Email] = Field(..., description="List of recent emails")

result = await agent.run_task(
    goal="Open Gmail and analyze my inbox",
    output=InboxSummary
)

for email in result.emails:
    if email.is_unread:
        print(f"Unread: {email.subject} from {email.sender}")
```

## Task Execution Flow

## Best Practices

Be specific in your goals

```python
# ✅ Good - specific
goal="Open Weather app, check temperature for New York, and tell me if it will rain tomorrow"

# ❌ Bad - vague
goal="Check weather"
```

Use Pydantic for structured output

Define clear field descriptions to help the LLM understand what to extract

```python
class WeatherInfo(BaseModel):
    temperature: float = Field(..., description="Current temperature in Celsius")
    will_rain_tomorrow: bool = Field(..., description="Whether rain is forecast for tomorrow")
```

Break complex tasks into simpler ones

Instead of one complex task, run multiple simpler tasks in sequence

```python
# Step 1: Navigate
await agent.run_task(goal="Open banking app and go to transactions")

# Step 2: Extract data
transactions = await agent.run_task(
    goal="Get the last 5 transactions",
    output=TransactionList
)
```

Enable tracing for debugging

Always enable tracing when developing or debugging tasks

```python
task = agent.new_task(goal).with_trace_recording(enabled=True).build()
```

## Example: Multi-Step Workflow

- Platform
- Local

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import PlatformTaskRequest

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

class ShoppingResults(BaseModel):
    products: List[Product]
    total_found: int

async def shop_online():
    agent = Agent()
    agent.init()
    
    try:
        # Step 1: Search (task configured on platform)
        await agent.run_task(
            request=PlatformTaskRequest(task="search-products")
        )
        
        # Step 2: Extract results (task configured on platform)
        results = await agent.run_task(
            request=PlatformTaskRequest[ShoppingResults](
                task="extract-product-results"
            )
        )
        
        # Step 3: Filter and act
        for product in results.products:
            if product.in_stock and product.price < 50:
                print(f"Good deal: {product.name} - ${product.price}")
        
    finally:
        agent.clean()
```

```python
import asyncio
from pydantic import BaseModel, Field
from typing import List
from minitap.mobile_use.sdk import Agent

class Product(BaseModel):
    name: str
    price: float
    in_stock: bool

class ShoppingResults(BaseModel):
    products: List[Product]
    total_found: int

async def shop_online():
    agent = Agent(...)  # Configure with local profile
    agent.init()
    
    try:
        # Step 1: Search
        await agent.run_task(
            goal="Open Amazon app and search for 'bluetooth headphones'",
            name="search_products"
        )
        
        # Step 2: Extract results
        results = await agent.run_task(
            goal="Get the first 5 product results with names, prices, and availability",
            output=ShoppingResults,
            name="extract_products"
        )
        
        # Step 3: Filter and act
        for product in results.products:
            if product.in_stock and product.price < 50:
                print(f"Good deal: {product.name} - ${product.price}")
        
    finally:
        agent.clean()
```

## Next Steps

## Profiles

Customize agent behavior

## Task Builder SDK

Detailed task configuration SDK
