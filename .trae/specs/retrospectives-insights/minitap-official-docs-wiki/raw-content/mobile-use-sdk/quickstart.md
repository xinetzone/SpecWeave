This guide covers **local development** where you configure LLMs via config files and have full control over the execution environment.

**Want a faster setup?** Check out the [Platform Quickstart](https://www.minitap.ai/docs/mobile-use-sdk/platform-quickstart) - no LLM config files needed and built-in observability!

Make sure you’ve completed the [Installation](https://www.minitap.ai/docs/mobile-use-sdk/installation) steps before proceeding.

## Configure LLM Settings

### 1\. Create LLM Config File

Create a `llm-config.override.jsonc` file to configure your LLM models. This file will override the [default configuration](https://github.com/minitap-ai/mobile-use/blob/main/llm-config.defaults.jsonc).

```jsonc
// Your custom LLM configuration
{
  "planner": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "orchestrator": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "contextor": {
    // Optional: Only needed if using app lock feature
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "cortex": {
    // IMPORTANT: Needs vision capabilities!
    // Recommended: gpt-4o, gpt-5, or equivalent vision-capable model
    "provider": "openai",
    "model": "gpt-4o",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5"
    }
  },
  "executor": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "utils": {
    "hopper": {
      // Needs at least a 256k context window
      "provider": "openai",
      "model": "gpt-5-nano"
    },
    "outputter": {
      "provider": "openai",
      "model": "gpt-5-nano"
    }
  }
}
```

### 2\. Configure Environment Variables

Create a `.env` file in your project root with necessary API keys:

```shellscript
# LLM API Keys (only include the ones you need)
OPENAI_API_KEY=your_key_here
XAI_API_KEY=your_key_here
OPEN_ROUTER_API_KEY=your_key_here
GOOGLE_API_KEY=your_key_here

# Optional: For local LLMs or custom OpenAI-compatible endpoints
# OPENAI_BASE_URL=http://localhost:1234/v1
```

Never commit your `.env` file to version control. Add it to your `.gitignore`.

---

## Creating Your First Automation

Let’s write a simple script that opens a calculator app and performs a basic calculation.

For more examples, check out the [mobile-use SDK examples directory](https://github.com/minitap-ai/mobile-use/tree/main/minitap/mobile_use/sdk/examples) on GitHub.

```python
import asyncio
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

async def main():
    # Create an agent profile
    default_profile = AgentProfile(
        name="default",
        from_file="llm-config.override.jsonc"
    )

    # Configure the agent
    agent_config = Builders.AgentConfig.with_default_profile(default_profile).build()
    agent = Agent(config=agent_config)

    try:
        # Initialize the agent (connect to the first available device)
        await agent.init()

        # Define a simple task goal
        result = await agent.run_task(
            goal="Open the calculator app, calculate 123 * 456, and tell me the result",
            name="calculator_demo"
        )

        # Print the result
        print(f"Result: {result}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # Always clean up when finished
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

### Run the script

```shellscript
python calculator_demo.py
```

## Getting Structured Output

Mobile-use SDK can return structured data using Pydantic models:

```python
import asyncio
from pydantic import BaseModel, Field
from minitap.mobile_use.sdk import Agent
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.sdk.builders import Builders

# Define a model for structured output
class CalculationResult(BaseModel):
    expression: str = Field(..., description="The mathematical expression calculated")
    result: float = Field(..., description="The result of the calculation")
    app_used: str = Field(..., description="The name of the calculator app used")

async def main():
    # Create an agent
    default_profile = AgentProfile(
        name="default",
        from_file="llm-config.override.jsonc"
    )
    agent_config = Builders.AgentConfig.with_default_profile(default_profile).build()
    agent = Agent(config=agent_config)

    try:
        await agent.init()

        # Request structured output using Pydantic model
        result = await agent.run_task(
            goal="Open the calculator app, calculate 123 * 456, and tell me the result",
            output=CalculationResult,
            name="structured_calculator"
        )

        if result:
            print(f"Expression: {result.expression}")
            print(f"Result: {result.result}")
            print(f"App used: {result.app_used}")

    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

Using Pydantic models ensures type-safe, validated output from your automation tasks.

## Understanding the Code

### Agent Profile

```python
default_profile = AgentProfile(
    name="default", 
    from_file="llm-config.override.jsonc"
)
```

The `AgentProfile` defines which LLM models power different components of the agent.

### Agent Configuration

```python
agent_config = Builders.AgentConfig.with_default_profile(default_profile).build()
```

The `Builders.AgentConfig` provides a fluent API to configure your agent.

### Running Tasks

```python
result = await agent.run_task(
    goal="Your instruction here",
    output=YourPydanticModel,  # Optional
    name="task_name"  # Optional
)
```

Tasks are executed asynchronously and can return structured output.

## Comparing Local vs Platform

## ✅ When to Use Local

## 🚀 When to Use Platform

## Next Steps

## Core Concepts

Understand the architecture and components

## Examples

Explore more practical examples

## SDK Reference

Detailed SDK documentation

## Troubleshooting

Common issues and solutions
