This example demonstrates how to use the video recording tools to capture and analyze video content playing on a mobile device screen.

This example is available on GitHub: [video\_transcription\_example.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/video_transcription_example.py)

## What This Example Does

## Prerequisites

Video recording tools require additional setup:

1. **ffmpeg** must be installed on your system (for video compression)
2. A **video-capable Gemini model** must be configured in `utils.video_analyzer`

### Install ffmpeg

- macOS
- Linux
- Windows

```shellscript
brew install ffmpeg
```

```shellscript
# Ubuntu/Debian
apt install ffmpeg

# Fedora
dnf install ffmpeg
```

Download from [ffmpeg.org/download.html](https://www.ffmpeg.org/download.html)

### Supported Video Analyzer Models

The `video_analyzer` utility requires a video-capable Gemini model:

| Model | Provider | Notes |
| --- | --- | --- |
| `gemini-3-flash-preview` | google | **Recommended** - Fast and capable |
| `gemini-3-pro-preview` | google | Higher quality, slower |
| `gemini-2.5-flash` | google | Good balance |
| `gemini-2.5-pro` | google | Premium quality |
| `gemini-2.0-flash` | google | Fast, reliable |

## Video Recording Tools

When video recording is enabled, the agent has access to two tools:

### start\_video\_recording

Starts a background screen recording on the mobile device.

- Recording continues until `stop_video_recording` is called
- **No duration limit** - recording runs as long as needed
- **Audio**: Not captured (video only)

On Android, the native `screenrecord` command has a 3-minute limit, but mobile-use automatically handles this by segmenting and concatenating recordings seamlessly. You don’t need to worry about this limit.

### stop\_video\_recording

Stops the current screen recording and analyzes the video content.prompt

str

default:"Describe what happened in the video."

Specifies what to extract from the video. Examples:

- `"Describe what actions are shown on screen"`
- `"What happens after each 10 seconds of the video?"`
- `"List all UI elements and buttons that appear"`

## Complete Code

```python
import asyncio

from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
from minitap.mobile_use.sdk.agent import Agent
from minitap.mobile_use.sdk.builders.agent_config_builder import AgentConfigBuilder
from minitap.mobile_use.sdk.types.agent import AgentConfig
from minitap.mobile_use.sdk.types.task import AgentProfile, TaskRequest

def get_video_capable_llm_config() -> LLMConfig:
    """
    Returns an LLM config with video_analyzer configured.

    The video_analyzer must use a video-capable Gemini model:
    - gemini-3-flash-preview (recommended - fast and capable)
    - gemini-3-pro-preview
    - gemini-2.5-flash
    - gemini-2.5-pro
    - gemini-2.0-flash
    """
    return LLMConfig(
        planner=LLMWithFallback(
            provider="openai",
            model="gpt-5-nano",
            fallback=LLM(provider="openai", model="gpt-5-mini"),
        ),
        orchestrator=LLMWithFallback(
            provider="openai",
            model="gpt-5-nano",
            fallback=LLM(provider="openai", model="gpt-5-mini"),
        ),
        contextor=LLMWithFallback(
            provider="openai",
            model="gpt-5-nano",
            fallback=LLM(provider="openai", model="gpt-5-mini"),
        ),
        cortex=LLMWithFallback(
            provider="openai",
            model="gpt-5",
            fallback=LLM(provider="openai", model="o4-mini"),
        ),
        executor=LLMWithFallback(
            provider="openai",
            model="gpt-5-nano",
            fallback=LLM(provider="openai", model="gpt-5-mini"),
        ),
        utils=LLMConfigUtils(
            outputter=LLMWithFallback(
                provider="openai",
                model="gpt-5-nano",
                fallback=LLM(provider="openai", model="gpt-5-mini"),
            ),
            hopper=LLMWithFallback(
                provider="openai",
                model="gpt-5-nano",
                fallback=LLM(provider="openai", model="gpt-5-mini"),
            ),
            # IMPORTANT: video_analyzer must use a video-capable Gemini model
            video_analyzer=LLMWithFallback(
                provider="google",
                model="gemini-3-flash-preview",
                fallback=LLM(provider="google", model="gemini-2.5-flash"),
            ),
        ),
    )

async def main():
    config: AgentConfig = (
        AgentConfigBuilder()
        .add_profile(
            AgentProfile(
                name="VideoCapable",
                llm_config=get_video_capable_llm_config(),
            )
        )
        .with_video_recording_tools()  # Enable video recording tools
        .build()
    )

    agent = Agent(config=config)
    try:
        await agent.init()

        result = await agent.run_task(
            request=TaskRequest(
                goal="""
                1. Open YouTube app
                2. Search for "Python tutorial"
                3. Start recording the screen
                4. Play the first video
                5. Wait for the first 30 seconds of the video to play
                6. Stop recording and describe what was shown in the video
                """,
                profile="VideoCapable",
            )
        )
        print(f"Task result: {result}")
    finally:
        await agent.clean()

if __name__ == "__main__":
    asyncio.run(main())
```

## Code Breakdown

### 1\. Configure video\_analyzer in LLMConfigUtils

The key configuration is adding `video_analyzer` to your `LLMConfigUtils`:

```python
utils=LLMConfigUtils(
    outputter=LLMWithFallback(...),
    hopper=LLMWithFallback(...),
    # Add video_analyzer with a Gemini model
    video_analyzer=LLMWithFallback(
        provider="google",
        model="gemini-3-flash-preview",
        fallback=LLM(provider="google", model="gemini-2.5-flash"),
    ),
)
```

The `video_analyzer` is optional in `LLMConfigUtils`. It’s only required when using video recording tools.

### 2\. Enable Video Recording Tools

Use the builder method to enable video tools:

```python
config = (
    AgentConfigBuilder()
    .add_profile(profile)
    .with_video_recording_tools()  # Enables start/stop recording tools
    .build()
)
```

Calling `with_video_recording_tools()` will raise `FFmpegNotInstalledError` if ffmpeg is not installed.

### 3\. Use Recording in Task Goals

The agent can now use recording tools in natural language goals:

```python
goal = """
1. Start recording the screen
2. Navigate to the video
3. Wait for 30 seconds
4. Stop recording and describe what happened on screen
"""
```

## Configuration File Approach

You can also configure `video_analyzer` in a JSONC config file:

```jsonc
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
    "provider": "openai",
    "model": "gpt-5-nano",
    "fallback": {
      "provider": "openai",
      "model": "gpt-5-mini"
    }
  },
  "cortex": {
    "provider": "openai",
    "model": "gpt-5",
    "fallback": {
      "provider": "openai",
      "model": "o4-mini"
    }
  },
  "executor": {
    "provider": "openai",
    "model": "gpt-5-nano"
  },
  "utils": {
    "hopper": {
      "provider": "openai",
      "model": "gpt-5-nano"
    },
    "outputter": {
      "provider": "openai",
      "model": "gpt-5-nano"
    },
    // Video analyzer for transcription
    "video_analyzer": {
      "provider": "google",
      "model": "gemini-3-flash-preview",
      "fallback": {
        "provider": "google",
        "model": "gemini-2.5-flash"
      }
    }
  }
}
```

Then use it:

```python
profile = AgentProfile(name="video", from_file="llm-config.video.jsonc")

config = (
    AgentConfigBuilder()
    .add_profile(profile)
    .with_video_recording_tools()
    .build()
)
```

## How It Works

- Android
- iOS

Android’s native `screenrecord` command has a 3-minute hard limit. To work around this, mobile-use:

1. Automatically restarts recording before each 3-minute segment ends
2. Saves each segment locally
3. Concatenates all segments using ffmpeg when you stop recording

**Result**: You can record for as long as you need - the segmentation is handled transparently.

iOS uses the `idb record-video` command which doesn’t have a hard duration limit.

Recording continues until `stop_video_recording` is called.

## Use Cases

- Video Analysis
- UI Workflow Capture
- App Testing

```python
goal = """
1. Open YouTube and play "TED Talk on AI"
2. Start recording
3. Wait 2 minutes
4. Stop recording and describe the key visual content shown
"""
```

```python
goal = """
1. Open the Settings app
2. Start recording
3. Navigate through Privacy settings
4. Stop recording and list all screens and options shown
"""
```

```python
goal = """
1. Open the app under test
2. Start recording
3. Perform the checkout flow
4. Stop recording and identify any UI glitches or errors shown
"""
```

## Custom Analysis Prompts

The `stop_video_recording` tool accepts a `prompt` parameter for custom analysis:

```python
# The agent will use this prompt when analyzing the video
goal = """
Start recording, play the video for 1 minute, then stop recording 
and answer: "What are the 3 main takeaways from this video?"
"""
```

## Troubleshooting

FFmpegNotInstalledError

**Error**: `ffmpeg is required for video recording but is not installed`

**Solution**: Install ffmpeg using your system’s package manager:

- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg` or `dnf install ffmpeg`
- Windows: Download from ffmpeg.org

video\_analyzer not configured

**Error**: `with_video_recording_tools() requires 'video_analyzer' in utils`

**Solution**: Add `video_analyzer` to your profile’s `LLMConfigUtils`:

```python
utils=LLMConfigUtils(
    outputter=...,
    hopper=...,
    video_analyzer=LLMWithFallback(
        provider="google",
        model="gemini-3-flash-preview",
        fallback=LLM(provider="google", model="gemini-2.5-flash"),
    ),
)
```

Segment concatenation warnings

**Warning**: `Concatenation failed, using last segment only`

**Cause**: ffmpeg failed to merge video segments (Android only).

**Solution**: Ensure ffmpeg is properly installed and working. The recording will still succeed but may only contain the last 3-minute segment.

Video analysis fails

**Error**: `Recording stopped but analysis failed`

**Possible causes**:

- Video file too large (>14MB after compression)
- Gemini API rate limits
- Invalid video format

**Solution**: Try shorter recordings or check your Google API quota.

## Best Practices

## Keep Recordings Short

Shorter recordings (under 2 minutes) process faster and more reliably

## Use Specific Prompts

Tell the agent exactly what to extract: “list all buttons shown” vs “describe the workflow”

## Configure Fallbacks

Always set a fallback model for video\_analyzer in case of API issues

## Test ffmpeg First

Verify ffmpeg works before running: `ffmpeg -version`

## Next Steps

## Agent Profiles

Learn more about configuring video\_analyzer

## AgentConfigBuilder

Full builder reference including with\_video\_recording\_tools()
