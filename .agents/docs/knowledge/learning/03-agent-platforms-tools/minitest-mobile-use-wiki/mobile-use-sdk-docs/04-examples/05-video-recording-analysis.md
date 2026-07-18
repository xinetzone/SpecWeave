---
title: "视频录制分析"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/examples/video-transcription"
x-toml-ref: "../../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/minitest-mobile-use-wiki/mobile-use-sdk-docs/04-examples/05-video-recording-analysis.toml"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "examples", "video", "gemini", "ffmpeg"]
summary: "演示如何使用视频录制工具捕获和分析移动设备屏幕上播放的视频内容。"
---
# 视频录制分析

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/examples/video-transcription

本示例演示如何使用视频录制工具捕获和分析移动设备屏幕上播放的视频内容。

本示例代码可在 GitHub 获取：[video_transcription_example.py](https://github.com/minitap-ai/mobile-use/blob/main/minitap/mobile_use/sdk/examples/video_transcription_example.py)

## 示例功能

本示例自动完成以下任务：
1. 打开 YouTube 应用
2. 搜索 "Python tutorial"
3. 开始屏幕录制
4. 播放第一个视频
5. 等待视频播放前 30 秒
6. 停止录制并描述视频中显示的内容

## 前置条件

视频录制工具需要额外的设置：

1. 系统上必须安装 **ffmpeg**（用于视频压缩）
2. 必须在 `utils.video_analyzer` 中配置**支持视频的 Gemini 模型**

### 安装 ffmpeg

**macOS:**

```shellscript
brew install ffmpeg
```

**Linux:**

```shellscript
# Ubuntu/Debian
apt install ffmpeg

# Fedora
dnf install ffmpeg
```

**Windows:**

从 [ffmpeg.org/download.html](https://www.ffmpeg.org/download.html) 下载

### 支持的视频分析模型

`video_analyzer` 工具需要支持视频的 Gemini 模型：

| 模型 | 提供商 | 说明 |
| --- | --- | --- |
| `gemini-3-flash-preview` | google | **推荐** - 快速且能力强 |
| `gemini-3-pro-preview` | google | 更高质量，速度较慢 |
| `gemini-2.5-flash` | google | 良好的平衡 |
| `gemini-2.5-pro` | google | 优质质量 |
| `gemini-2.0-flash` | google | 快速、可靠 |

## 视频录制工具

启用视频录制后，Agent 可以访问两个工具：

### start_video_recording

在移动设备上启动后台屏幕录制。

- 录制持续到调用 `stop_video_recording` 为止
- **无时长限制** - 根据需要录制任意时长
- **音频**：不捕获（仅视频）

> **注意**：在 Android 上，原生 `screenrecord` 命令有 3 分钟限制，但 mobile-use 通过分段和无缝拼接录制自动处理此问题。您无需担心此限制。

### stop_video_recording

停止当前屏幕录制并分析视频内容。

**参数：**

- `prompt`: `str`，默认值：`"Describe what happened in the video."`

指定从视频中提取什么内容。示例：

- `"Describe what actions are shown on screen"`
- `"What happens after each 10 seconds of the video?"`
- `"List all UI elements and buttons that appear"`

## 完整代码

```python
import asyncio

from minitap.mobile_use.config import LLM, LLMConfig, LLMConfigUtils, LLMWithFallback
from minitap.mobile_use.sdk.agent import Agent
from minitap.mobile_use.sdk.builders.agent_config_builder import AgentConfigBuilder
from minitap.mobile_use.sdk.types.agent import AgentConfig
from minitap.mobile_use.sdk.types.task import AgentProfile, TaskRequest

def get_video_capable_llm_config() -> LLMConfig:
    """
    返回配置了 video_analyzer 的 LLM 配置。

    video_analyzer 必须使用支持视频的 Gemini 模型：
    - gemini-3-flash-preview（推荐 - 快速且能力强）
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
            # 重要：video_analyzer 必须使用支持视频的 Gemini 模型
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
        .with_video_recording_tools()  # 启用视频录制工具
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

## 代码详解

### 1. 在 LLMConfigUtils 中配置 video_analyzer

关键配置是在 `LLMConfigUtils` 中添加 `video_analyzer`：

```python
utils=LLMConfigUtils(
    outputter=LLMWithFallback(...),
    hopper=LLMWithFallback(...),
    # 使用 Gemini 模型添加 video_analyzer
    video_analyzer=LLMWithFallback(
        provider="google",
        model="gemini-3-flash-preview",
        fallback=LLM(provider="google", model="gemini-2.5-flash"),
    ),
)
```

`video_analyzer` 在 `LLMConfigUtils` 中是可选的。仅在使用视频录制工具时需要。

### 2. 启用视频录制工具

使用 Builder 方法启用视频工具：

```python
config = (
    AgentConfigBuilder()
    .add_profile(profile)
    .with_video_recording_tools()  # 启用 start/stop 录制工具
    .build()
)
```

如果未安装 ffmpeg，调用 `with_video_recording_tools()` 将引发 `FFmpegNotInstalledError`。

### 3. 在任务目标中使用录制

Agent 现在可以在自然语言目标中使用录制工具：

```python
goal = """
1. Start recording the screen
2. Navigate to the video
3. Wait for 30 seconds
4. Stop recording and describe what happened on screen
"""
```

## 配置文件方式

您也可以在 JSONC 配置文件中配置 `video_analyzer`：

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
    // 用于转录的视频分析器
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

然后使用它：

```python
profile = AgentProfile(name="video", from_file="llm-config.video.jsonc")

config = (
    AgentConfigBuilder()
    .add_profile(profile)
    .with_video_recording_tools()
    .build()
)
```

## 工作原理

### Android

Android 的原生 `screenrecord` 命令有 3 分钟的硬性限制。为了解决这个问题，mobile-use：

1. 在每个 3 分钟段结束前自动重新开始录制
2. 将每个段保存在本地
3. 停止录制时使用 ffmpeg 拼接所有段

**结果**：您可以根据需要录制任意时长 - 分段处理是透明的。

### iOS

iOS 使用 `idb record-video` 命令，该命令没有硬性时长限制。录制持续到调用 `stop_video_recording` 为止。

## 使用场景

### 视频分析

```python
goal = """
1. Open YouTube and play "TED Talk on AI"
2. Start recording
3. Wait 2 minutes
4. Stop recording and describe the key visual content shown
"""
```

### UI 工作流捕获

```python
goal = """
1. Open the Settings app
2. Start recording
3. Navigate through Privacy settings
4. Stop recording and list all screens and options shown
"""
```

### 应用测试

```python
goal = """
1. Open the app under test
2. Start recording
3. Perform the checkout flow
4. Stop recording and identify any UI glitches or errors shown
"""
```

## 自定义分析提示

`stop_video_recording` 工具接受 `prompt` 参数用于自定义分析：

```python
# Agent 在分析视频时将使用此提示
goal = """
Start recording, play the video for 1 minute, then stop recording 
and answer: "What are the 3 main takeaways from this video?"
"""
```

## 故障排除

### FFmpegNotInstalledError

**错误**：`ffmpeg is required for video recording but is not installed`

**解决方案**：使用系统的包管理器安装 ffmpeg：

- macOS: `brew install ffmpeg`
- Linux: `apt install ffmpeg` 或 `dnf install ffmpeg`
- Windows: 从 ffmpeg.org 下载

### video_analyzer 未配置

**错误**：`with_video_recording_tools() requires 'video_analyzer' in utils`

**解决方案**：将 `video_analyzer` 添加到 Profile 的 `LLMConfigUtils` 中：

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

### 段拼接警告

**警告**：`Concatenation failed, using last segment only`

**原因**：ffmpeg 合并视频段失败（仅 Android）。

**解决方案**：确保 ffmpeg 已正确安装并正常工作。录制仍会成功，但可能只包含最后 3 分钟的段。

### 视频分析失败

**错误**：`Recording stopped but analysis failed`

**可能原因**：

- 视频文件过大（压缩后 >14MB）
- Gemini API 速率限制
- 视频格式无效

**解决方案**：尝试更短的录制或检查您的 Google API 配额。

## 最佳实践

### 保持录制简短

较短的录制（2 分钟以内）处理更快更可靠

### 使用具体提示

告诉 Agent 具体要提取什么："列出显示的所有按钮" vs "描述工作流"

### 配置回退

始终为 video_analyzer 设置回退模型以防 API 问题

### 先测试 ffmpeg

运行前验证 ffmpeg 正常工作：`ffmpeg -version`

## 下一步

- **Agent 配置**：了解更多关于配置 video_analyzer 的信息
- **AgentConfigBuilder**：包含 with_video_recording_tools() 的完整 Builder 参考
