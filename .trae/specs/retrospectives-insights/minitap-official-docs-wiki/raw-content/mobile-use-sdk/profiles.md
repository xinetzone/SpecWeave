Agent profiles allow you to customize the behavior and capabilities of the automation agent by configuring which LLM models power different components.

## What are Agent Profiles?

An agent profile defines the LLM configuration for the various sub-agents that power mobile-use:

- **Planner** - Creates high-level plans from goals
- **Orchestrator** - Coordinates execution steps
- **Contextor** - Gathers device context and enforces app lock constraints (optional, conditionally invokes LLM)
- **Cortex** - High-level reasoning and decision-making (requires vision capabilities)
- **Executor** - Performs specific actions
- **Utils** - Helper agents (outputter, hopper, [video analyzer](https://www.minitap.ai/docs/mobile-use-sdk/examples/video-transcription))

## Platform Profiles

**Using the platform?** Create and manage profiles on [platform.mobile-use.ai/llm-profiles](https://platform.mobile-use.ai/llm-profiles), then reference them by name in your tasks.

### Creating Platform Profiles

1. Go to [**LLM Profiles**](https://platform.mobile-use.ai/llm-profiles) on the platform
2. Click **Create Profile**
3. Configure each agent component with your preferred models
4. All OpenRouter models are available (no API key management needed)
5. Reference the profile by name in your code:

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

result = await agent.run_task(
    request=PlatformTaskRequest(
        task="check-notifications",
        profile="your-profile-name"  # Profile configured on platform
    )
)
```

Platform profiles can be updated anytime without changing code - perfect for A/B testing different models!

---

## Local Profiles

For local development, profiles are defined in config files or code:

### From Configuration File

The recommended approach for local production:

```python
from minitap.mobile_use.sdk.types import AgentProfile

profile = AgentProfile(
    name="default",
    from_file="llm-config.defaults.jsonc"
)
```

**llm-config.defaults.jsonc:**

```jsonc
{
  "planner": {
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "orchestrator": {
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "cortex": {
    // IMPORTANT: Needs vision capabilities!
    "provider": "openai",
    "model": "gpt-5",
    "fallback": {
      "provider": "openai",
      "model": "o4-mini"
    }
  },
  "executor": {
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "contextor": {
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "utils": {
    "hopper": {
      // Needs at least a 256k context window.
      "provider": "openai",
      "model": "gpt-5-nano",
      "fallback": {
        "provider": "openai",
        "model": "gpt-5-mini"
      }
    },
    "outputter": {
      "provider": "openai",
      "model": "gpt-5-nano",
      "fallback": {
        "provider": "openai",
        "model": "gpt-5-mini"
      }
    }
    // video_analyzer is optional - only needed when using video recording tools
    // Requires a video-capable model (Google). To enable, uncomment below:
    // "video_analyzer": {
    //   "provider": "google",
    //   "model": "gemini-3-flash-preview",
    //   "fallback": {
    //     "provider": "google",
    //     "model": "gemini-2.5-flash"
    //   }
    // }
  }
}
```

### Programmatic Configuration

For dynamic configuration:

```python
from minitap.mobile_use.sdk.types import AgentProfile
from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback

detail_oriented_profile = AgentProfile(
    name="detail_oriented",
    llm_config=LLMConfig(
        planner=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
        orchestrator=LLM(provider="openrouter", model="meta-llama/llama-4-scout"),
        contextor=LLMWithFallback(
            provider="openrouter",
            model="meta-llama/llama-3.1-8b-instruct",
            fallback=LLM(provider="openrouter", model="meta-llama/llama-3.3-70b-instruct"),
        ),
        cortex=LLMWithFallback(
            provider="openai",
            model="gpt-4o",  # Vision model required
            fallback=LLM(provider="openai", model="gpt-5"),
        ),
        executor=LLM(provider="openai", model="gpt-5-nano"),
        utils=LLMConfigUtils(
            outputter=LLM(provider="openai", model="gpt-5-nano"),
            hopper=LLM(provider="openai", model="gpt-4.1"),
        ),
    )
)
```

You cannot specify both `llm_config` and `from_file` - they are mutually exclusive.

## Using Profiles

### Setting a Default Profile

Configure an agent with a default profile:

```python
from minitap.mobile_use.sdk.builders import Builders

profile = AgentProfile(name="default", from_file="llm-config.defaults.jsonc")

config = (
    Builders.AgentConfig
    .with_default_profile(profile)
    .build()
)

agent = Agent(config=config)
```

### Multiple Profiles

Register multiple profiles and switch between them:

```python
# Create profiles
fast_profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
accurate_profile = AgentProfile(name="accurate", from_file="accurate-config.jsonc")

# Configure agent with multiple profiles
config = (
    Builders.AgentConfig
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .build()
)

agent = Agent(config=config)

# Use different profiles for different tasks
await agent.run_task(
    goal="Quick notification check",
    profile="fast"
)

await agent.run_task(
    goal="Detailed financial analysis",
    profile="accurate"
)
```

## Profile Use Cases

- Speed vs Accuracy
- Cost Optimization
- Provider Diversity

**Fast Profile** - Quick tasks, simple UI navigation

```jsonc
{
  "cortex": {
    "provider": "openai",
    "model": "gpt-5-nano"
  }
}
```

**Accurate Profile** - Complex analysis, detailed extraction

```jsonc
{
  "cortex": {
    "provider": "openai",
    "model": "o4-mini"
  }
}
```

**Budget Profile** - Use cheaper models where possible

```jsonc
{
  "planner": {"provider": "openai", "model": "gpt-5-nano"},
  "cortex": {"provider": "openai", "model": "gpt-5"}
}
```

**Premium Profile** - Best models for critical tasks

```jsonc
{
  "planner": {"provider": "openai", "model": "o3"},
  "cortex": {"provider": "openai", "model": "o4-mini"}
}
```

**Multi-Provider** - Use different providers for redundancy

```jsonc
{
  "planner": {"provider": "openai", "model": "gpt-5-nano"},
  "cortex": {
    "provider": "openai",
    "model": "o4-mini",
    "fallback": {
      "provider": "google",
      "model": "gemini-2.5-flash"
    }
  }
}
```

## Component Roles

Contextor (App Lock Enforcement)

Gathers device context and enforces app lock constraints.

- Always collects current device state (UI hierarchy, focused app, screen dimensions, date/time)
- When app lock is enabled: validates user remains in specified app
- Decides if app deviations are intentional (e.g., OAuth flows)
- Relaunches the app when necessary
- **Model Type:** Non-vision (text-only)
- **Invokes LLM:** Only when app lock is active AND app mismatch detected
- **Recommendation:** Use fast, decision-focused models (e.g., `gpt-5-nano`, `meta-llama/llama-3.1-8b-instruct`)
- **Context window:** Standard (does not need extended context)

The Contextor is optional and only needed if you plan to use the app lock feature. When disabled or when there’s no app lock, it functions as a simple data-gathering node without LLM inference.

Cortex (High-Level Reasoning)

The cortex handles high-level reasoning and decision-making.

- Makes strategic decisions about task execution
- Coordinates between planner and executor
- Handles complex reasoning tasks
- Analyzes both UI hierarchy and screenshots for complete device understanding
- **IMPORTANT:** Requires a vision-capable model (e.g., `gpt-4o`, `gpt-5`)
- **Context window:** Needs at least 128k tokens and image input support

Planner

Creates high-level plans from natural language goals.

- Breaks down goals into subgoals
- Estimates complexity
- **Recommendation:** Use fast, capable text models (e.g., `gpt-5-nano`)

Orchestrator

Coordinates execution and decides when to replicate.

- Manages task flow
- Handles errors and retries
- **Recommendation:** Use fast models (e.g., `gpt-5-nano`)

Executor

Translates decisions into device actions.

- Generates device commands using native platform APIs
- Handles action formatting
- **Recommendation:** Use fast, instruction-following models

Utils - Hopper

Digs through large batches of data to extract the most relevant information for reaching the goal.

- Processes extensive historical context and screen data
- Extracts relevant information without modifying it
- **Context window:** Needs at least 256k tokens (handles huge data batches)
- **Recommendation:** Use models with large context (e.g., `gpt-4.1`)

Utils - Outputter

Extracts structured output from final results.

- Formats data into Pydantic models
- Ensures type safety
- **Recommendation:** Use capable text models

Utils - Video Analyzer (Optional)

Analyzes video content captured from screen recordings.

- Describes visual events and actions
- Extracts information based on custom prompts
- Identifies UI elements, screens, and workflows
- **IMPORTANT:** Requires a video-capable Gemini model
- **Supported models:** `gemini-3-flash-preview` (recommended), `gemini-3-pro-preview`, `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`
- **Provider:** Must be `google`

The Video Analyzer is optional and only needed when using video recording tools via `with_video_recording_tools()`. See the [Video Transcription example](https://www.minitap.ai/docs/mobile-use-sdk/examples/video-transcription) for usage details.

## Supported Providers

Configure API keys in your `.env` file:

```shellscript
# OpenAI
OPENAI_API_KEY=sk-...

# Google (Gemini)
GOOGLE_API_KEY=...

# xAI (Grok)
XAI_API_KEY=...

# OpenRouter (access to multiple models)
OPEN_ROUTER_API_KEY=...
```

## Fallback Configuration

The cortex supports fallback models for reliability:

```python
cortex=LLMWithFallback(
    provider="openai",
    model="o4-mini",
    fallback=LLM(provider="openai", model="gpt-5")
)
```

If the primary model fails or is unavailable, the fallback is used automatically.

## Best Practices

## Optimize the Cortex

Invest in the best vision-capable model for cortex - it has the biggest impact

## Use Fast Models for Planner

Planner and orchestrator don’t need the most powerful models

## Large Context for Hopper

Ensure hopper has at least 256k context window

## Test Profile Performance

Benchmark different profile configurations for your use cases

## Example: Task-Specific Profiles

```python
import asyncio

# Define specialized profiles
fast_profile = AgentProfile(name="fast", from_file="fast.jsonc")
vision_profile = AgentProfile(name="vision", from_file="vision.jsonc")

config = (
    Builders.AgentConfig
    .add_profiles([fast_profile, vision_profile])
    .with_default_profile(fast_profile)
    .build()
)

agent = Agent(config=config)
agent.init()

try:
    # Use fast profile for simple navigation
    await agent.run_task(
        goal="Open settings",
        profile="fast"
    )
    
    # Use vision profile for complex visual task
    result = await agent.run_task(
        goal="Analyze all icons on the home screen and describe their purpose",
        profile="vision"
    )
    
finally:
    agent.clean()
```

## Next Steps

## Builders

Learn about builder patterns

## Examples

See profiles in action
