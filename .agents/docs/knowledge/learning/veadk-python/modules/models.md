---
id: models-module
title: 模型配置
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 模型配置

## 概述

VeADK 提供了灵活的模型配置系统，支持火山引擎方舟（Ark）大模型服务和通过 LiteLLM 接入的多种模型提供商。系统内置了多模型 Fallback 降级策略、Responses API 支持、Embedding 模型配置和实时语音模型配置，并遵循 API Key 四级优先级机制进行认证。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/models/](file:///d:/AI/.chaos/libs/veadk-python/veadk/models/)

---

## 支持的模型提供商

VeADK 通过两种方式接入大模型：

### 1. ArkLLM - 火山引擎方舟原生接入

`ArkLlm` 类是 VeADK 对火山引擎方舟（Ark）服务的原生实现，基于 `volcenginesdkarkruntime` SDK，支持方舟的 Responses API 和完整的流式输出、工具调用、推理过程等特性。

**支持的特性：**
- Responses API（OpenAI 兼容的新接口）
- 流式输出（Streaming）
- 工具调用（Function Calling）
- 并行工具调用
- 推理过程（Thinking/Reasoning）
- 上下文缓存（Caching）
- 多模态输入（图片、视频、文件）
- 多模型 Fallback

> 源码位置：[models/ark_llm.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/models/ark_llm.py)

### 2. LiteLLM - 统一多模型接口

VeADK 同时集成 Google ADK 的 `LiteLlm` 类，通过 LiteLLM 统一接口接入上百种模型提供商。

**Provider 标识：**
- `openai/`: OpenAI 兼容接口（默认，用于方舟接入）
- `anthropic/`: Anthropic Claude
- `gemini/`: Google Gemini
- `bedrock/`: AWS Bedrock
- 其他 LiteLLM 支持的 provider...

**默认配置：**
```python
DEFAULT_MODEL_AGENT_PROVIDER = "openai"
DEFAULT_MODEL_AGENT_API_BASE = "https://ark.cn-beijing.volces.com/api/v3/"
```

> 源码位置：[consts.py#L22-L24](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L22-L24)

---

## 默认模型

VeADK 内置了经过验证的默认模型配置：

| 模型类型 | 默认模型名称 | API Base |
|---------|------------|----------|
| Agent 推理 | `doubao-seed-2-1-pro-260628` | `https://ark.cn-beijing.volces.com/api/v3/` |
| Embedding | `doubao-embedding-text-240715` | `https://ark.cn-beijing.volces.com/api/v3/` |
| 图片生成 | `doubao-seedream-5-0-260128` | `https://ark.cn-beijing.volces.com/api/v3/` |
| 图片编辑 | `doubao-seededit-3-0-i2i-250628` | `https://ark.cn-beijing.volces.com/api/v3/` |
| 视频生成 | `doubao-seedance-2-0-260128` | `https://ark.cn-beijing.volces.com/api/v3/` |
| 实时语音 | `doubao_realtime_voice_model` | `wss://openspeech.bytedance.com/api/v3/realtime/dialogue` |

> 源码位置：[consts.py#L22-L72](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L22-L72)

---

## 模型配置参数

### ModelConfig - Agent 模型配置

`ModelConfig` 类使用 Pydantic Settings，支持从环境变量自动加载配置。

> 源码位置：[configs/model_configs.py#L31-L55](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L31-L55)

```python
class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_AGENT_")

    name: str = DEFAULT_MODEL_AGENT_NAME
    provider: str = DEFAULT_MODEL_AGENT_PROVIDER
    api_base: str = DEFAULT_MODEL_AGENT_API_BASE
    api_key_name: str = ""
```

| 字段 | 环境变量 | 类型 | 默认值 | 说明 |
|------|---------|------|--------|------|
| `name` | `MODEL_AGENT_NAME` | str | `doubao-seed-2-1-pro-260628` | 模型名称（方舟 endpoint ID 或模型名） |
| `provider` | `MODEL_AGENT_PROVIDER` | str | `openai` | LiteLLM provider 前缀 |
| `api_base` | `MODEL_AGENT_API_BASE` | str | 方舟 API 地址 | API 基础 URL |
| `api_key_name` | `MODEL_AGENT_API_KEY_NAME` | str | "" | 指定 ARK API Key 名称（按名称查找） |
| `api_key` | `MODEL_AGENT_API_KEY` | str | 自动获取 | API Key（cached_property，四级优先级） |

### EmbeddingModelConfig - 嵌入模型配置

```python
class EmbeddingModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_EMBEDDING_")

    name: str = DEFAULT_MODEL_EMBEDDING_NAME
    dim: int = DEFAULT_MODEL_EMBEDDING_DIM
    api_base: str = DEFAULT_MODEL_AGENT_API_BASE
```

| 字段 | 环境变量 | 默认值 | 说明 |
|------|---------|--------|------|
| `name` | `MODEL_EMBEDDING_NAME` | `doubao-embedding-text-240715` | 嵌入模型名称 |
| `dim` | `MODEL_EMBEDDING_DIM` | 2560 | 嵌入向量维度 |
| `api_base` | - | 方舟 API 地址 | API 基础 URL |
| `api_key` | `MODEL_EMBEDDING_API_KEY` | 自动回退 | API Key（回退到 Agent 模型 Key → ARK 默认 Key） |

> 源码位置：[configs/model_configs.py#L57-L75](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L57-L75)

### RealtimeModelConfig - 实时语音模型配置

```python
class RealtimeModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_REALTIME_")

    name: str = "doubao_realtime_voice_model"
    api_base: str = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"
```

| 字段 | 环境变量 | 默认值 | 说明 |
|------|---------|--------|------|
| `name` | `MODEL_REALTIME_NAME` | `doubao_realtime_voice_model` | 实时语音模型名称 |
| `api_base` | - | WSS 地址 | WebSocket 端点 |
| `api_key` | `MODEL_REALTIME_API_KEY` | Speech Token | API Key（回退到语音服务 Token） |

> 源码位置：[configs/model_configs.py#L93-L104](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L93-L104)

---

## Fallbacks 降级策略

VeADK 支持配置多模型降级链，当主模型失败时自动尝试备用模型。

### 配置方式

通过给 `model_name` 传入列表来配置 Fallback 链：

```python
from veadk import Agent

agent = Agent(
    name="my-agent",
    model_name=[
        "doubao-seed-2-1-pro-260628",     # 主模型
        "doubao-1-5-pro-256k-250115",      # 备用模型 1
        "doubao-1-5-lite-32k-250115",      # 备用模型 2
    ],
    model_provider="openai",
)
```

### Fallback 逻辑

```python
if isinstance(self.model_name, list):
    if self.model_name:
        model_name = self.model_name[0]
        fallbacks = [
            f"{self.model_provider}/{m}" for m in self.model_name[1:]
        ]
        logger.info(
            f"Using primary model: {model_name}, with fallbacks: {self.model_name[1:]}"
        )
```

- 列表第一个元素为主模型
- 后续元素按顺序作为 Fallback
- Fallback 自动添加 provider 前缀
- 日志会输出 Fallback 链配置

### ArkLlm Fallback 实现

`ArkLlm` 类实现了 `_generate_content_with_fallbacks()` 方法处理降级：

```python
async def _generate_content_with_fallbacks(
    self,
    request: Optional[LlmRequest],
    **kwargs: Any,
) -> AsyncGenerator[LlmResponse, None]:
    """Try the primary Ark model and configured fallbacks in order.

    A fallback is safe only before an attempt has yielded output. Once a
    model has started streaming tokens, switching models would produce
    garbled output, so we fail fast in that case.
    """
    models = [self.model, *(self.fallbacks or [])]
    # 按顺序尝试每个模型
    # 在输出任何 token 之前失败 → 安全切换到下一个 fallback
    # 已输出 token 后失败 → 不切换（避免输出混乱），直接报错
```

**安全降级原则：**
1. ✅ 请求阶段失败（如 429 限流、503 服务不可用、认证错误）→ 安全切换到下一个模型
2. ❌ 已开始输出 token 后失败 → 不切换，直接报错（避免内容混乱）
3. Fallback 链按顺序遍历，直到成功或全部失败

> 源码位置：[ark_llm.py#L777-L827](file:///d:/AI/.chaos/libs/veadk-python/veadk/models/ark_llm.py#L777-L827)
> 源码位置：[agent.py#L256-L293](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L256-L293)

---

## Responses API 支持

ArkLLM 完整支持火山引擎方舟的 Responses API（类 OpenAI Responses 接口），相比传统 Chat Completions 提供更丰富的能力。

### 启用 Responses API

```python
agent = Agent(
    name="my-agent",
    model_name="doubao-seed-2-1-pro-260628",
    enable_responses=True,           # 启用 Responses API
    enable_responses_cache=True,     # 启用响应缓存
)
```

### 支持的参数

ArkLlm 支持的 Responses API 参数：

| 参数 | 说明 |
|------|------|
| `input` | 输入消息列表 |
| `model` | 模型名称 |
| `stream` | 是否流式输出 |
| `instructions` | 系统指令 |
| `max_output_tokens` | 最大输出 token 数 |
| `temperature` | 温度参数 |
| `top_p` | Top P 采样 |
| `parallel_tool_calls` | 并行工具调用 |
| `tool_choice` | 工具选择策略 |
| `tools` | 工具定义列表 |
| `previous_response_id` | 前一个响应 ID（上下文延续） |
| `thinking` / `reasoning` | 推理过程配置 |
| `store` | 是否存储对话历史 |
| `caching` | 缓存配置 |
| `context_management` | 上下文管理 |
| `expire_at` | 缓存过期时间 |

> 源码位置：[ark_llm.py#L85-L115](file:///d:/AI/.chaos/libs/veadk-python/veadk/models/ark_llm.py#L85-L115)

### 默认额外配置

```python
DEFAULT_MODEL_EXTRA_CONFIG = {
    "extra_headers": {
        "x-is-encrypted": "true",
        "veadk-source": "veadk",
        "veadk-version": VERSION,
        "User-Agent": f"VeADK/{VERSION}",
        "X-Client-Request-Id": f"veadk/{VERSION}",
    },
    "extra_body": {
        "caching": {"type": "enabled"},
        "expire_at": int(time.time()) + 3600,  # 1小时后过期
    },
}
```

> 源码位置：[consts.py#L25-L42](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L25-L42)

---

## 模型初始化流程

```
Agent(model_name=...)
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 1. 解析 model_name                                          │
│    - 单字符串 → model_name = 该值, fallbacks = None         │
│    - 列表 → [0]为主模型，[1:]为fallbacks列表                 │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. 解析 api_key（四级优先级）                                │
│    1) MODEL_AGENT_API_KEY 环境变量                          │
│    2) MODEL_AGENT_API_KEY_NAME → 按名称从 ARK 获取           │
│    3) get_ark_token() → 默认第一个 ARK Key                  │
│    4) VeFaaS IAM 角色临时凭证                               │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. 合并 extra_config                                        │
│    - 默认 headers（veadk-source/version 等）                 │
│    - 默认 body（caching/expire_at）                         │
│    - 用户自定义 extra_headers/extra_body 覆盖               │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. 创建模型实例                                             │
│    enable_responses=True → ArkLlm(...)                      │
│    enable_responses=False → LiteLlm(...)                     │
│    传入 fallbacks、api_key、api_base、extra_config           │
└─────────────────────────────────────────────────────────────┘
    │
    ▼
  模型就绪 ✓
```

---

## 多模态输入支持

ArkLlm 通过 Responses API 支持多模态输入，包括：

### 图片输入

```python
ResponseInputImageParam(
    type="input_image",
    detail="auto",  # auto/low/high
    image_url="https://example.com/image.jpg",  # 或 file_id="xxx"
)
```

### 视频输入

```python
ResponseInputVideoParam(
    type="input_video",
    video_url="https://example.com/video.mp4",  # 或 file_id="xxx"
    fps=1.0,  # 帧率
)
```

### 文件输入

```python
ResponseInputFileParam(
    type="input_file",
    file_url="https://example.com/doc.pdf",  # 或 file_id="xxx"
)
```

文件 URI 支持两种格式：
- `https://...`：公网 URL
- `file_id://xxx`：方舟文件 ID

> 源码位置：[ark_llm.py#L165-L200](file:///d:/AI/.chaos/libs/veadk-python/veadk/models/ark_llm.py#L165-L200)

---

## 模型选择建议

### 按场景选择

| 场景 | 推荐模型 | 理由 |
|------|---------|------|
| 通用 Agent | `doubao-seed-2-1-pro-260628` | 默认模型，能力均衡，支持工具调用 |
| 长上下文 | `doubao-1-5-pro-256k-250115` | 256K 上下文窗口 |
| 轻量快速 | `doubao-1-5-lite-32k-250115` | 速度快，成本低，简单任务 |
| 高可靠生产 | 配置 Fallback 链 | 主模型 + 备用模型，避免单点故障 |
| 嵌入向量 | `doubao-embedding-text-240715` | 2560 维，中文效果好 |
| 图片生成 | `doubao-seedream-5-0-260128` | 豆包文生图模型 |
| 视频生成 | `doubao-seedance-2-0-260128` | 豆包视频生成模型 |

### 配置最佳实践

1. **显式指定 API Key**：生产环境设置 `MODEL_AGENT_API_KEY` 避免运行时查找开销
2. **配置 Fallback 链**：生产环境建议至少配置一个备用模型
3. **启用缓存**：默认启用 caching 可降低延迟和成本
4. **合理设置超时**：根据任务复杂度调整 `timeout` 参数
5. **使用 IAM 角色**：VeFaaS 部署时使用 IAM 角色而非长期 AK/SK

---

## 使用示例

### 基础配置（.env 文件）

```bash
# 最简配置：直接设置 API Key
MODEL_AGENT_API_KEY=ark-xxxxxxxxxxxxxxxxxxxxxxxx

# 或通过 AK/SK 自动获取
# VOLCENGINE_ACCESS_KEY=AKLTxxxxxxxx
# VOLCENGINE_SECRET_KEY=xxxxxxxxxxxx
# MODEL_AGENT_API_KEY_NAME=my-production-key
```

### 单模型 Agent

```python
from veadk import Agent, tool

@tool
def search(query: str) -> str:
    """搜索互联网"""
    return f"搜索结果 for: {query}"

agent = Agent(
    name="search-assistant",
    description="搜索助手",
    model_name="doubao-seed-2-1-pro-260628",
    tools=[search],
)
```

### 多模型 Fallback 配置

```python
agent = Agent(
    name="reliable-agent",
    model_name=[
        "doubao-seed-2-1-pro-260628",
        "doubao-1-5-pro-256k-250115",
    ],
    model_provider="openai",
    api_base="https://ark.cn-beijing.volces.com/api/v3/",
)
```

### 启用 Responses API

```python
agent = Agent(
    name="responses-agent",
    model_name="doubao-seed-2-1-pro-260628",
    enable_responses=True,
    enable_responses_cache=True,
    model_extra_config={
        "temperature": 0.7,
        "max_output_tokens": 4096,
    },
)
```

### Embedding 配置（用于知识库）

```python
from veadk.knowledgebase import KnowledgeBase
from veadk.memory import InMemoryLongTermMemory

kb = KnowledgeBase(
    index="my-docs",
    embedding_model_name="doubao-embedding-text-240715",
)
```

---

## 目录结构

```
veadk/models/
├── __init__.py
├── ark_llm.py              # Ark 大模型原生实现（含 Fallback）
└── ark_embedding.py        # Ark Embedding 模型实现
```
