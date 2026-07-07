---
title: "Agent配置"
category: "learning"
source: "https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/profiles"
date: "2026-07-07"
tags: ["mobile-use", "mobile-automation", "profiles", "llm-configuration"]
summary: "Agent配置文件详解，自定义LLM模型配置，为不同Agent组件配置不同模型，支持多配置文件切换。"
---
# Agent配置

> **来源**: https://www.minitap.ai/docs/mobile-use-sdk/core-concepts/profiles

Agent配置文件允许您通过配置哪些LLM模型为不同组件提供支持，来自定义自动化Agent的行为和能力。

## 什么是Agent配置文件？

Agent配置文件定义了为mobile-use提供支持的各个子Agent的LLM配置：

- **Planner** - 从目标创建高级计划
- **Orchestrator** - 协调执行步骤
- **Contextor** - 收集设备上下文并强制执行应用锁约束（可选，条件调用LLM）
- **Cortex** - 高级推理和决策（需要视觉能力）
- **Executor** - 执行特定操作
- **Utils** - 辅助Agent（outputter、hopper、[视频分析器](../04-examples/05-video-recording-analysis.md)）

---

## Platform配置文件

**使用Platform？** 在[platform.mobile-use.ai/llm-profiles](https://platform.mobile-use.ai/llm-profiles)上创建和管理配置文件，然后在任务中按名称引用它们。

### 创建Platform配置文件

1. 转到Platform上的[**LLM Profiles**](https://platform.mobile-use.ai/llm-profiles)
2. 点击**Create Profile**
3. 使用您偏好的模型配置每个Agent组件
4. 所有OpenRouter模型都可用（无需管理API密钥）
5. 在代码中按名称引用配置文件：

```python
from minitap.mobile_use.sdk.types import PlatformTaskRequest

result = await agent.run_task(
    request=PlatformTaskRequest(
        task="check-notifications",
        profile="your-profile-name"  # 在Platform上配置的配置文件
    )
)
```

Platform配置文件可以随时更新，无需更改代码 - 非常适合对不同模型进行A/B测试！

---

## 本地配置文件

对于本地开发，配置文件在配置文件或代码中定义：

### 从配置文件

本地生产环境的推荐方法：

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
    // 重要：需要视觉能力！
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
      // 至少需要256k上下文窗口。
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
    // video_analyzer是可选的 - 仅在使用视频录制工具时需要
    // 需要支持视频的模型（Google）。要启用，取消下面的注释：
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

### 编程式配置

用于动态配置：

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
            model="gpt-4o",  # 需要视觉模型
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

不能同时指定`llm_config`和`from_file` - 它们是互斥的。

---

## 使用配置文件

### 设置默认配置文件

使用默认配置文件配置Agent：

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

### 多个配置文件

注册多个配置文件并在它们之间切换：

```python
# 创建配置文件
fast_profile = AgentProfile(name="fast", from_file="fast-config.jsonc")
accurate_profile = AgentProfile(name="accurate", from_file="accurate-config.jsonc")

# 使用多个配置文件配置Agent
config = (
    Builders.AgentConfig
    .add_profiles([fast_profile, accurate_profile])
    .with_default_profile(fast_profile)
    .build()
)

agent = Agent(config=config)

# 为不同任务使用不同配置文件
await agent.run_task(
    goal="Quick notification check",
    profile="fast"
)

await agent.run_task(
    goal="Detailed financial analysis",
    profile="accurate"
)
```

---

## 配置文件用例

- **速度 vs 准确性**
- **成本优化**
- **提供商多样性**

**快速配置文件** - 快速任务，简单UI导航

```jsonc
{
  "cortex": {
    "provider": "openai",
    "model": "gpt-5-nano"
  }
}
```

**精确配置文件** - 复杂分析，详细提取

```jsonc
{
  "cortex": {
    "provider": "openai",
    "model": "o4-mini"
  }
}
```

**预算配置文件** - 尽可能使用更便宜的模型

```jsonc
{
  "planner": {"provider": "openai", "model": "gpt-5-nano"},
  "cortex": {"provider": "openai", "model": "gpt-5"}
}
```

**高级配置文件** - 关键任务的最佳模型

```jsonc
{
  "planner": {"provider": "openai", "model": "o3"},
  "cortex": {"provider": "openai", "model": "o4-mini"}
}
```

**多提供商** - 使用不同提供商实现冗余

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

---

## 组件角色

### Contextor（应用锁执行）

收集设备上下文并强制执行应用锁约束。

- 始终收集当前设备状态（UI层次结构、焦点应用、屏幕尺寸、日期/时间）
- 启用应用锁时：验证用户保持在指定应用中
- 判断应用偏离是否是故意的（例如OAuth流程）
- 必要时重新启动应用
- **模型类型：** 非视觉（纯文本）
- **调用LLM：** 仅当应用锁激活且检测到应用不匹配时
- **推荐：** 使用快速、决策导向的模型（例如`gpt-5-nano`、`meta-llama/llama-3.1-8b-instruct`）
- **上下文窗口：** 标准（不需要扩展上下文）

Contextor是可选的，仅在您计划使用应用锁功能时需要。禁用或没有应用锁时，它作为简单的数据收集节点运行，不进行LLM推理。

### Cortex（高级推理）

Cortex处理高级推理和决策。

- 做出关于任务执行的战略决策
- 在planner和executor之间协调
- 处理复杂推理任务
- 分析UI层次结构和截图以完整理解设备
- **重要：** 需要支持视觉的模型（例如`gpt-4o`、`gpt-5`）
- **上下文窗口：** 至少需要128k tokens和图像输入支持

### Planner

从自然语言目标创建高级计划。

- 将目标分解为子目标
- 评估复杂度
- **推荐：** 使用快速、能力强的文本模型（例如`gpt-5-nano`）

### Orchestrator

协调执行并决定何时复制。

- 管理任务流
- 处理错误和重试
- **推荐：** 使用快速模型（例如`gpt-5-nano`）

### Executor

将决策转换为设备操作。

- 使用原生平台API生成设备命令
- 处理操作格式化
- **推荐：** 使用快速、指令遵循模型

### Utils - Hopper

挖掘大量数据以提取达成目标最相关的信息。

- 处理大量历史上下文和屏幕数据
- 提取相关信息而不修改它
- **上下文窗口：** 至少需要256k tokens（处理巨大数据批次）
- **推荐：** 使用大上下文模型（例如`gpt-4.1`）

### Utils - Outputter

从最终结果中提取结构化输出。

- 将数据格式化为Pydantic模型
- 确保类型安全
- **推荐：** 使用能力强的文本模型

### Utils - Video Analyzer（可选）

分析从屏幕录制捕获的视频内容。

- 描述视觉事件和操作
- 根据自定义提示提取信息
- 识别UI元素、屏幕和工作流
- **重要：** 需要支持视频的Gemini模型
- **支持的模型：** `gemini-3-flash-preview`（推荐）、`gemini-3-pro-preview`、`gemini-2.5-flash`、`gemini-2.5-pro`、`gemini-2.0-flash`
- **提供商：** 必须为`google`

Video Analyzer是可选的，仅在通过`with_video_recording_tools()`使用视频录制工具时需要。有关使用详情，请参阅[视频转录示例](../04-examples/05-video-recording-analysis.md)。

---

## 支持的提供商

在`.env`文件中配置API密钥：

```shellscript
# OpenAI
OPENAI_API_KEY=sk-...

# Google (Gemini)
GOOGLE_API_KEY=...

# xAI (Grok)
XAI_API_KEY=...

# OpenRouter (访问多个模型)
OPEN_ROUTER_API_KEY=...
```

---

## 回退配置

Cortex支持回退模型以提高可靠性：

```python
cortex=LLMWithFallback(
    provider="openai",
    model="o4-mini",
    fallback=LLM(provider="openai", model="gpt-5")
)
```

如果主模型失败或不可用，自动使用回退模型。

---

## 最佳实践

### 优化Cortex

为Cortex投资最佳的视觉能力模型 - 它影响最大

### Planner使用快速模型

Planner和Orchestrator不需要最强大的模型

### Hopper使用大上下文

确保Hopper至少有256k上下文窗口

### 测试配置文件性能

为您的用例基准测试不同的配置文件配置

---

## 示例：任务特定配置文件

```python
import asyncio

# 定义专用配置文件
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
    # 使用fast配置文件进行简单导航
    await agent.run_task(
        goal="Open settings",
        profile="fast"
    )
    
    # 使用vision配置文件进行复杂视觉任务
    result = await agent.run_task(
        goal="Analyze all icons on the home screen and describe their purpose",
        profile="vision"
    )
    
finally:
    agent.clean()
```

---

## 下一步

- [Builder模式](03-builder-pattern.md) - 了解builder模式
- [使用示例](../04-examples/00-overview.md) - 查看配置文件的实际应用
