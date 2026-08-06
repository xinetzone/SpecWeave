---
source: d:\AI\.chaos\libs\mobile-use
---

# 配置体系

## 三层配置架构

mobile-use 采用**默认配置 + 用户覆盖 + 代码级**三层配置体系，优先级从低到高：

```
┌─────────────────────────────────────────┐
│ 1. llm-config.defaults.jsonc  (默认)    │  内置默认LLM配置
├─────────────────────────────────────────┤
│ 2. llm-config.override.jsonc  (用户覆盖)│  用户自定义配置（可选）
├─────────────────────────────────────────┤
│ 3. 代码级 AgentConfig/AgentProfile      │  SDK Builder动态配置
│    + .env 环境变量 (API Key等)          │  最高优先级
└─────────────────────────────────────────┘
```

## LLM 配置结构

### 完整配置模型（LLMConfig）

每个Agent节点可以独立配置使用的LLM Provider和模型，支持Fallback降级：

```python
class LLMConfig(BaseModel):
    planner: LLMWithFallback          # 规划Agent
    orchestrator: LLMWithFallback     # 编排Agent
    contextor: LLMWithFallback        # 上下文Agent
    cortex: LLMWithFallback           # 决策Agent
    executor: LLMWithFallback         # 执行Agent
    utils: LLMConfigUtils             # 工具类Agent配置

class LLMWithFallback(BaseModel):
    provider: str                     # Provider名称（openai/google/anthropic/...）
    model: str                        # 模型名称
    fallback: LLM | None = None       # 降级模型（可选）

class LLM(BaseModel):
    provider: str
    model: str

class LLMConfigUtils(BaseModel):
    outputter: LLM | None = None      # 输出格式化
    hopper: LLM | None = None         # 导航跳转
    video_analyzer: LLM | None = None # 视频分析（需视频模型）
```

### 配置示例（JSONC格式）

`llm-config.defaults.jsonc` 中的默认配置结构：

```jsonc
{
  "planner": {
    "provider": "openai",
    "model": "gpt-4o",
    "fallback": { "provider": "minimax", "model": "MiniMax-M2.7" }
  },
  "orchestrator": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  },
  "contextor": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  },
  "cortex": {
    "provider": "openai",
    "model": "gpt-4o",
    "fallback": { "provider": "minimax", "model": "MiniMax-M2.7-highspeed" }
  },
  "executor": {
    "provider": "openai",
    "model": "gpt-4o-mini"
  },
  "utils": {
    "outputter": { "provider": "openai", "model": "gpt-4o-mini" },
    "video_analyzer": null  // 默认不启用视频分析
  }
}
```

## 支持的 LLM Providers

| Provider | 环境变量 | 模型示例 | 特点 |
|---|---|---|---|
| **openai** | `OPENAI_API_KEY` | `gpt-4o`, `gpt-4o-mini` | 通用，速度快 |
| **google** | `GOOGLE_API_KEY` | `gemini-2.0-flash`, `gemini-2.5-pro` | 多模态强，Flash性价比高 |
| **vertex** | Google ADC | `gemini-2.0-flash` | GCP企业级 |
| **anthropic** | `ANTHROPIC_API_KEY` | `claude-sonnet-4-20250514`, `claude-haiku-3-5-20241022` | 长上下文，推理强 |
| **minimax** | `MINIMAX_API_KEY` | `MiniMax-M2.7`, `MiniMax-M2.7-highspeed` | 国产高性价比，200K上下文 |
| **openrouter** | `OPEN_ROUTER_API_KEY` | 路由到多种模型 | 聚合平台 |
| **grok** | `XAI_API_KEY` | `grok-2` | xAI模型 |
| **azure** | `AZURE_API_KEY` + `AZURE_BASE_URL` | Azure OpenAI部署 | 企业Azure |
| **cerebras** | CEREBRAS_API_KEY | `llama-3.3-70b` | 超快推理 |
| **minitap** | `MINITAP_API_KEY` | Minitap托管模型 | 平台默认，开箱即用 |

### 使用本地/兼容OpenAI接口的模型

```jsonc
{
  "cortex": {
    "provider": "openai",
    "model": "your-local-model-name"
  }
}
```

同时在 `.env` 中设置：
```env
OPENAI_BASE_URL=http://localhost:8000/v1
OPENAI_API_KEY=not-needed
```

## 环境变量配置

通过 `.env` 文件或系统环境变量配置敏感信息：

### API Keys

```env
# 至少配置一个
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
ANTHROPIC_API_KEY=sk-ant-...
MINIMAX_API_KEY=...
XAI_API_KEY=...
OPEN_ROUTER_API_KEY=...
AZURE_API_KEY=...
MINITAP_API_KEY=...
```

### 自定义Endpoint

```env
# OpenAI兼容接口（本地模型、代理等）
OPENAI_BASE_URL=https://your-proxy/v1
AZURE_BASE_URL=https://your-resource.openai.azure.com/
MINITAP_BASE_URL=https://platform.minitap.ai  # 默认
```

### 遥测配置

```env
# 启用/禁用遥测（默认：未设置时首次运行询问）
MOBILE_USE_TELEMETRY_ENABLED=true
```

## Profile 机制：多套LLM配置切换

Profile 允许定义多套命名的LLM配置，在不同任务间切换使用：

```python
from minitap.mobile_use import Builders

config = (
    Builders.AgentConfig()
    # Profile 1: 快速模式（全用gpt-4o-mini，成本低速度快）
    .add_profile(
        name="fast",
        llm_config={
            "planner": {"provider": "openai", "model": "gpt-4o-mini"},
            "cortex": {"provider": "openai", "model": "gpt-4o-mini"},
            "executor": {"provider": "openai", "model": "gpt-4o-mini"},
            "contextor": {"provider": "openai", "model": "gpt-4o-mini"},
            "orchestrator": {"provider": "openai", "model": "gpt-4o-mini"},
        }
    )
    # Profile 2: 智能模式（Planner/Cortex用强模型）
    .add_profile(
        name="smart",
        llm_config={
            "planner": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
            "cortex": {"provider": "anthropic", "model": "claude-sonnet-4-20250514"},
            "executor": {"provider": "openai", "model": "gpt-4o-mini"},
            "contextor": {"provider": "openai", "model": "gpt-4o-mini"},
            "orchestrator": {"provider": "openai", "model": "gpt-4o-mini"},
            "utils": {
                "video_analyzer": {"provider": "google", "model": "gemini-2.0-flash"}
            }
        }
    )
    # Profile 3: 视频模式（启用视频分析）
    .add_profile(
        name="video",
        llm_config={
            "planner": {"provider": "openai", "model": "gpt-4o"},
            "cortex": {"provider": "openai", "model": "gpt-4o"},
            "executor": {"provider": "openai", "model": "gpt-4o-mini"},
            "contextor": {"provider": "openai", "model": "gpt-4o-mini"},
            "orchestrator": {"provider": "openai", "model": "gpt-4o-mini"},
            "utils": {
                "video_analyzer": {"provider": "google", "model": "gemini-2.0-flash"}
            }
        }
    )
    .with_default_profile("fast")
    .build()
)

# 使用指定Profile执行任务
result = await agent.run_task(
    goal="Complex task requiring deep reasoning",
    profile="smart"  # 切换到smart profile
)

# 视频任务
result = await agent.run_task(
    goal="Record the screen while scrolling and describe what happens",
    profile="video"
)
```

### Profile 配置策略建议

| 场景 | Planner/Orchestrator | Cortex | Executor/Contextor | video_analyzer |
|---|---|---|---|---|
| 简单任务（查信息、点按钮） | gpt-4o-mini | gpt-4o-mini | gpt-4o-mini | 不需要 |
| 复杂任务（多步骤、跨App） | gpt-4o / claude-sonnet | gpt-4o / claude-sonnet | gpt-4o-mini | 不需要 |
| 视频分析任务 | gpt-4o | gpt-4o | gpt-4o-mini | gemini-2.0-flash |
| 成本敏感 | minimax | minimax | minimax-highspeed | 不需要 |

## Fallback 降级机制

每个Agent节点可以配置 `fallback` 模型，当主模型调用失败时自动切换：

```python
{
  "cortex": {
    "provider": "openai",
    "model": "gpt-4o",
    "fallback": {
      "provider": "minimax",
      "model": "MiniMax-M2.7"
    }
  }
}
```

降级逻辑在 `services/llm.py` 的 `with_fallback()` 中实现：
1. 尝试调用主模型
2. 如果失败（网络错误、速率限制、模型错误），自动调用fallback模型
3. 如果fallback也失败，抛出异常

> **注意**：Fallback只处理"调用失败"（异常），不处理"返回质量差"。如果模型返回了结果但结果错误，不会触发fallback。

## LLM 服务工厂函数

`services/llm.py` 提供了统一的LLM客户端工厂：

| 函数 | 返回类型 | 用途 |
|---|---|---|
| `get_llm(node_config)` | `BaseChatModel` | 根据LLMConfig自动选择Provider |
| `with_fallback(primary, fallback)` | `BaseChatModel` | 包装带fallback的模型 |
| `invoke_llm_with_timeout_message(llm, messages, timeout)` | `AIMessage` | 带超时的LLM调用 |
| `get_openai_llm(model)` | `ChatOpenAI` | 直接创建OpenAI客户端 |
| `get_google_llm(model)` | `ChatGoogleGenerativeAI` | 直接创建Gemini客户端 |
| `get_anthropic_llm(model)` | `ChatAnthropic` | 直接创建Claude客户端 |
| `get_minimax_llm(model)` | `ChatOpenAI` | MiniMax（OpenAI兼容接口） |

## 遥测配置

mobile-use 使用 PostHog 进行匿名遥测，可以通过配置关闭：

```python
from minitap.mobile_use.services.telemetry import telemetry

# 禁用遥测
telemetry.set_consent(False)
```

遥测收集的事件类型（非敏感）：
- 任务开始/完成（成功/失败/步数/时长）
- Agent初始化（平台、设备ID哈希）
- Cortex决策、Executor动作
- 异常信息（不包含用户数据）
- 不收集：屏幕内容、输入文本、个人信息

## 配置最佳实践

1. **开发阶段**：使用默认配置或fast profile（gpt-4o-mini），快速迭代
2. **生产/复杂任务**：Planner和Cortex使用强模型（gpt-4o / claude-sonnet），Executor/Contextor用快模型
3. **多Profile**：预定义fast/smart/video等Profile，任务级切换
4. **Fallback必配**：关键节点配置fallback，避免单一Provider故障导致任务失败
5. **本地模型**：通过OPENAI_BASE_URL接入vLLM/Ollama等本地部署，注意模型能力需支持tool calling
6. **不要手动修改llm-config.defaults.jsonc**：创建llm-config.override.jsonc覆盖

> **源码参考**:
> - [config.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/config.py) - 配置模型定义
> - [llm-config.defaults.jsonc](file:///d:/AI/.chaos/libs/mobile-use/llm-config.defaults.jsonc) - 默认LLM配置
> - [services/llm.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/services/llm.py) - LLM工厂与fallback
> - [sdk/builders/agent_config_builder.py](file:///d:/AI/.chaos/libs/mobile-use/minitap/mobile_use/sdk/builders/agent_config_builder.py) - AgentConfig Builder
