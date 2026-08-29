---
type: Concept
title: LLM 模型抽象
description: ArkLlm 与 LiteLlm 双轨模型层、Ark Responses API 调用、fallback 回退机制与 ArkEmbedding 嵌入模型
tags: [veadk, llm, ark, litellm, embedding, fallback]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: veadk-source
    resource: "/references/veadk-source.md"
    title: veadk-python 源码
  - id: facts
    resource: "/references/facts.md"
    title: veadk-python 事实清单
---

# LLM 模型抽象

veadk-python 提供两条 LLM 调用路径：基于火山引擎 Ark Responses API 的 `ArkLlm` 和基于 LiteLLM 统一网关的 `LiteLlm`。Agent 在 `model_post_init` 中根据 `enable_responses` 开关选择实例化哪一个。此外，`ArkEmbedding` 提供文本嵌入能力，供知识库和记忆系统使用。

## 双轨制模型选择

Agent 的 `model_post_init` 方法根据 `enable_responses` 字段决定 LLM 实现 [F-025]：

```python
if self.enable_responses:
    self.model = ArkLlm(...)
else:
    self.model = LiteLlm(...)
```

| 特性 | ArkLlm | LiteLlm |
|------|--------|---------|
| 触发条件 | `enable_responses=True` | 默认（`enable_responses=False`） |
| API 协议 | 火山引擎 Ark Responses API | LiteLLM 统一网关（OpenAI 兼容） |
| 继承基类 | Google ADK `Gemini` | Google ADK `LiteLlm` |
| 多轮缓存 | `previous_response_id` 复用 | 无原生缓存 |
| 流式事件 | Ark SSE 事件流 | OpenAI 兼容流 |
| fallback | 内置主备切换 | LiteLLM Router 管理 |

模型名统一格式为 `f"{model_provider}/{model_name}"`，例如 `"openai/doubao-seed-2-1-pro-260628"` [F-025]。

## ArkLlm 类

`ArkLlm` 定义于 `veadk/models/ark_llm.py`，继承自 Google ADK 的 `Gemini` 类 [F-090]。

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model` | `str` | 必填 | 模型名（含 provider 前缀） |
| `fallbacks` | `Optional[List[str]]` | `None` | 备用模型列表 |
| `llm_client` | `ArkLlmClient` | `ArkLlmClient()` | Ark API 客户端 |
| `use_interactions_api` | `bool` | `True` | 使用 Interactions API |
| `enable_responses_cache` | `bool` | `True` | 启用多轮缓存 |

构造时检查 `google-adk>=1.34.0`，因为需要 `previous_interaction_id` 字段支持 [F-090]。

### generate_content_async 方法

```python
async def generate_content_async(
    self, llm_request: LlmRequest, stream: bool = False
) -> AsyncGenerator[LlmResponse, None]
```

执行流程 [F-091]：

1. 从 `LlmRequest` 提取 instructions、input_param、tools、text_format、generation_params
2. 若 `enable_responses_cache`，从 `get_previous_interaction_id` 获取 `previous_response_id`
3. 调用 `_generate_content_with_fallbacks` 执行带 fallback 的请求

### fallback 回退机制

`_generate_content_with_fallbacks` 按顺序尝试主模型和 fallback 模型列表 [F-092]：

- 按列表顺序逐个尝试模型
- **关键约束**：一旦已经 yield 输出 chunk，后续发生错误不再进行 fallback。这是为了避免两个不同模型的响应片段混合在一起，导致输出不一致
- 遇到 `PreviousResponseNotFound` 错误时，移除 `previous_response_id` 后重试（缓存失效的降级处理）

这种设计确保了流式输出的一致性——用户看到的输出始终来自同一个模型。

### Responses API 调用

`generate_content_via_responses` 方法实现 Ark Responses API 的调用 [F-093]：

1. 调用 `request_reorganization_by_ark` 重组请求参数（将 ADK 的 LlmRequest 转换为 Ark API 格式）
2. **流式模式**：通过 `llm_client.aresponses(stream=True)` 获取事件流，使用 `event_to_generate_content_response` 将 Ark SSE 事件转换为 ADK LlmResponse
3. **非流式模式**：通过 `aresponses` 获取完整响应，使用 `ark_response_to_generate_content_response` 转换

### supported_models

```python
@classmethod
def supported_models(cls) -> list[str]:
    return [r"openai/.*"]
```

`ArkLlm` 声明支持所有 `openai/` 前缀的模型，因为 Ark API 兼容 OpenAI 接口格式 [F-094]。

## API Key 四级优先级

Agent 的 API Key 解析遵循严格优先级 [F-024]：

1. **显式参数**：构造 Agent 时传入的 `model_api_key`
2. **环境变量**：`MODEL_AGENT_API_KEY`
3. **Key 名称**：`model_api_key_name` 或 `MODEL_AGENT_API_KEY_NAME` 环境变量，通过 `get_ark_token` 按名称解析
4. **全局配置**：`settings.model.api_key`（账户首个 ARK Key）

这种设计允许不同 Agent 使用不同的 API Key，同时提供合理的全局默认值。

## 默认请求头与 Body

Agent 自动为 LLM 请求添加默认 headers 和 body [F-026]：

**extra_headers**：
- `x-is-encrypted`：请求加密标志
- `veadk-source`：来源标识
- `veadk-version`：版本号
- `User-Agent`：用户代理
- `X-Client-Request-Id`：客户端请求 ID（用于链路追踪）

**extra_body**：
- `caching.type`：缓存类型，默认 `"enabled"`
- `expire_at`：缓存过期时间（当前时间 + 3600 秒）

用户自定义的 `model_extra_config` 通过 `|=` 运算符合并到默认值，用户配置优先级更高。

## ArkEmbedding 嵌入模型

`ArkEmbedding` 定义于 `veadk/models/ark_embedding.py`，继承自 llama_index 的 `BaseEmbedding` [F-095]。

### 核心字段

| 字段 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `model_name` | `str` | `"doubao-embedding-vision-250615"` | 嵌入模型名 [F-096] |
| `api_key` | `str` | 必填 | API Key |
| `api_base` | `Optional[str]` | `None` | API 基础 URL |
| `max_retries` | `int` | `10` | 最大重试次数 |
| `timeout` | `float` | `60.0` | 超时秒数 |
| `reuse_client` | `bool` | `True` | 复用 HTTP 客户端 |
| `dimensions` | `Optional[int]` | `None` | 嵌入维度 |
| `embed_batch_size` | `int` | `100` | 批量嵌入大小 |

私有属性包括同步/异步 Ark 客户端和 HTTP 客户端 [F-095]。

### ArkEmbeddingModel 枚举

```python
class ArkEmbeddingModel(Enum):
    DOUBAO_EMBEDDING_VISION_251215 = "doubao-embedding-vision-251215"
    DOUBAO_EMBEDDING_VISION_250615 = "doubao-embedding-vision-250615"
```

来源：[F-097]

### Embedding API Key 优先级

`EmbeddingModelConfig` 的 `api_key` 解析优先级 [F-055]：

1. `MODEL_EMBEDDING_API_KEY` 环境变量
2. `MODEL_AGENT_API_KEY` 环境变量（复用 Agent 模型 Key）
3. `get_ark_token()`（账户首个 ARK Key）

## 模型更新

Agent 提供 `update_model(self, model_name: str)` 方法在运行时切换模型 [F-034]：

```python
self.model = self.model.model_copy(
    update={"model": f"{self.model_provider}/{model_name}"}
)
```

这使用 Pydantic 的 `model_copy` 创建新模型实例，替换 Agent 的 `model` 字段，无需重建整个 Agent。

## 默认模型常量

`veadk/consts.py` 定义了火山引擎环境的默认模型 [F-061][F-063]：

| 用途 | 默认模型 |
|------|---------|
| Agent 对话 | `doubao-seed-2-1-pro-260628` |
| Embedding | `doubao-embedding-vision-250615`（2048 维） |
| 图像编辑 | `doubao-seededit-3-0-i2i-250628` |
| 视频生成 | `doubao-seedance-2-0-260128` |
| 图像生成 | `doubao-seedream-5-0-260628` |

BytePlus 环境下自动切换为海外版模型（如 `dola-seed-2-1-turbo-260628`）[F-062]。

## LiteLlm 路径

当 `enable_responses=False`（默认）时，Agent 使用 Google ADK 内置的 `LiteLlm` 类 [F-025]。LiteLLM 是一个统一 LLM 网关，支持 100+ 模型提供商。veadk 通过 `litellm>=1.83.7` 依赖使用此路径 [F-006]。

导入时设置 `LITELLM_LOCAL_MODEL_COST_MAP=True` 可减少约 10 秒的导入延迟 [F-127]。

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [配置系统](/concepts/04-configuration.md)
- [知识库](/concepts/08-knowledgebase.md)
- [记忆系统](/concepts/06-memory-system.md)
- [veadk-python 概览](/concepts/00-overview.md)
