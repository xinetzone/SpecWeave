---
type: Concept
title: 配置系统
description: VeADKConfig 全局配置、ModelConfig 模型配置、config.yaml 结构、环境变量前缀映射与加载流程
tags: [veadk, configuration, environment-variables, pydantic-settings, dotenv]
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

# 配置系统

veadk-python 的配置系统以 `VeADKConfig` 为核心，结合 `pydantic-settings`、`python-dotenv` 和 OmegaConf，实现多源配置合并：环境变量优先，`.env` 文件次之，`config.yaml` 提供结构化默认值。模块导入时自动完成配置加载，全局单例 `settings` 可供所有组件读取。

## 配置加载流程

配置加载在 `veadk/config.py` 模块导入时自动执行 [F-051]：

1. **加载 .env 文件**：通过 `find_dotenv` 查找当前工作目录的 `.env` 文件，使用 `load_dotenv` 将其中的键值对加载到环境变量
2. **查找 config.yaml**：通过 `find_dotenv(filename="config.yaml", usecwd=True)` 在当前工作目录查找配置文件
3. **设置环境变量**：使用 `set_envs` 处理 config.yaml 中的环境变量段
4. **实例化配置**：创建全局单例 `settings = VeADKConfig()`

CLOUD_PROVIDER 适配：当环境变量 `CLOUD_PROVIDER=byteplus` 时，自动将 `BYTEPLUS_ACCESS_KEY`/`BYTEPLUS_SECRET_KEY` 映射到 `VOLCENGINE_ACCESS_KEY`/`VOLCENGINE_SECRET_KEY` [F-052]。这使得同一份代码可以在火山引擎国内站和 BytePlus 海外站之间切换。

## VeADKConfig 全局配置

`VeADKConfig` 继承自 Pydantic `BaseModel`，是所有子配置的聚合根 [F-053]：

```python
class VeADKConfig(BaseModel):
    model: ModelConfig
    tool: BuiltinToolConfigs
    prompt_pilot: PromptPilotConfig
    opentelemetry_config: OpenTelemetryConfig
    apmplus_config: APMPlusConfig
    cozeloop_config: CozeloopConfig
    tls_config: TLSConfig
    prometheus_config: PrometheusConfig
    tos: TOSConfig
    opensearch: OpensearchConfig
    mysql: MysqlConfig
    redis: RedisConfig
    milvus: MilvusConfig
    viking_knowledgebase: VikingKnowledgebaseConfig
    veidentity: VeIdentityConfig
    realtime_model: RealtimeModelConfig
```

每个子配置对应一个外部服务或功能模块，按需配置。未配置的子项使用各自的默认值。

## ModelConfig 模型配置

`ModelConfig` 定义于 `veadk/configs/model_configs.py`，继承 `BaseSettings`，环境变量前缀为 `MODEL_AGENT_` [F-054]：

| 字段 | 类型 | 默认值 | 环境变量 |
|------|------|--------|---------|
| `name` | `str` | `"doubao-seed-2-1-pro-260628"` | `MODEL_AGENT_NAME` |
| `provider` | `str` | `"openai"` | `MODEL_AGENT_PROVIDER` |
| `api_base` | `str` | `"https://ark.cn-beijing.volces.com/api/v3/"` | `MODEL_AGENT_API_BASE` |
| `api_key_name` | `str` | `""` | `MODEL_AGENT_API_KEY_NAME` |
| `api_key` | `str` | （缓存属性，动态解析） | `MODEL_AGENT_API_KEY` |

`api_key` 是一个 `@cached_property`，按以下优先级解析 [F-054]：

1. `MODEL_AGENT_API_KEY` 环境变量
2. `get_ark_token(api_key_name=...)`（按名称解析 ARK Key）
3. `get_ark_token()`（账户首个 ARK Key）

Agent 构造时的 `model_api_key` 字段有独立的四级解析逻辑（见 [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)），优先于全局配置 [F-024]。

## EmbeddingModelConfig 嵌入模型配置

`EmbeddingModelConfig` 环境变量前缀为 `MODEL_EMBEDDING_` [F-055]：

| 字段 | 默认值 |
|------|--------|
| `name` | `"doubao-embedding-vision-250615"` |
| `dim` | `2048` |
| `api_base` | 同 Agent 模型 |

`api_key` 优先级：`MODEL_EMBEDDING_API_KEY` > `MODEL_AGENT_API_KEY` > `get_ark_token()` [F-055]。

## RealtimeModelConfig 实时模型配置

`RealtimeModelConfig` 环境变量前缀为 `MODEL_REALTIME_` [F-056]：

| 字段 | 默认值 |
|------|--------|
| `name` | `"doubao_realtime_voice_model"` |
| `api_base` | `"wss://openspeech.bytedance.com/api/v3/realtime/dialogue"` |

`api_key` 为 `MODEL_REALTIME_API_KEY` 环境变量或 `get_speech_token()` 的返回值 [F-056]。

## config.yaml 结构

### 简化版（config.yaml.simple）

```yaml
model:
  agent:
    provider: openai
    name: doubao-seed-1-6-250615
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:
    encrypted: true
    caching: enabled
    max_llm_calls: 100
```

来源：`config.yaml.simple:1-9` [F-058]

### 完整版（config.yaml.full）顶层结构

完整配置文件包含以下顶层段 [F-059]：

| 段 | 子配置 |
|----|--------|
| `model` | agent、judge、embedding、video、image、edit |
| `volcengine` | access_key、secret_key |
| `agentkit` | tool_id、tool_id_script、tool_id_skills、tool_host、service_code、region、scheme |
| `tool` | vesearch、web_scraper、text_to_speech、lark、feishu_channel、mobile_use、vod、las、mcp_router、code_sandbox、browser_sandbox、computer_sandbox、llm_shield |
| `observability` | opentelemetry（apmplus、cozeloop、tls）、prometheus |
| `database` | opensearch、mysql、postgresql、redis、milvus、viking、tos、mem0、openviking、tos_vector、tos_context |
| `nacos` | endpoint、password |
| `prompt_pilot` | api_key |
| `logging` | level |
| `veadk` | tracer（apmplus、cozeloop、tls） |

## getenv 工具函数

`veadk/config.py` 提供 `getenv` 函数统一处理环境变量读取 [F-057]：

```python
def getenv(env_name: str, default_value: Any = "", allow_false_values: bool = False) -> str
```

特性：
- BytePlus 提供商下自动映射 AK/SK 环境变量
- 非 `allow_false_values` 模式下，值为空字符串时抛出 `ValueError`，强制必填项配置
- `allow_false_values=True` 时允许空值返回默认值

## 核心环境变量汇总

### 模型与认证

| 环境变量 | 用途 | 默认值 |
|---------|------|--------|
| `MODEL_AGENT_API_KEY` | Agent 模型 API Key | 空 |
| `MODEL_AGENT_API_KEY_NAME` | ARK API Key 名称 | 空 |
| `MODEL_AGENT_MAX_LLM_CALLS` | 最大 LLM 调用次数 | `100` |
| `MODEL_AGENT_ENCRYPTED` | 请求加密 | `"true"` |
| `MODEL_AGENT_CACHING` | 缓存开关 | `"enabled"` |
| `MODEL_AGENT_CLIENT_REQ_ID` | 客户端请求 ID | 自动生成 |
| `CLOUD_PROVIDER` | 云提供商 | `volcengine` |

### Tracing

| 环境变量 | 用途 |
|---------|------|
| `ENABLE_APMPLUS` | 启用 APMPlus exporter（`"true"`） |
| `ENABLE_COZELOOP` | 启用 CozeLoop exporter |
| `ENABLE_TLS` | 启用 TLS exporter |

来源：[F-130]

### 技能与工具

| 环境变量 | 用途 |
|---------|------|
| `AGENTKIT_TOOL_ID` | AgentKit 工具 ID |
| `AGENTKIT_TOOL_SERVICE_CODE` | 服务代码（默认 `"agentkit"`） |
| `AGENTKIT_TOOL_REGION` | 区域（默认 `"cn-beijing"`） |
| `AGENTKIT_SKILL_HOST` | 技能主机 |
| `VOLCENGINE_ACCESS_KEY` | 火山引擎 AK |
| `VOLCENGINE_SECRET_KEY` | 火山引擎 SK |
| `VEADK_MEDIA_STORAGE` | 多媒体存储类型（默认 `"local"`） |

来源：[F-131]

## 默认常量

`veadk/consts.py` 定义了不可通过配置覆盖的编译时常量 [F-060~F-064]：

- `DEFAULT_AGENT_NAME = "veAgent"` [F-060]
- Tracing 默认端点：
  - APMPlus：`http://apmplus-cn-beijing.volces.com:4317`
  - CozeLoop：`https://api.coze.cn/v1/loop/opentelemetry/v1/traces`
  - TLS：`https://tls-cn-beijing.volces.com:4318/v1/traces`

BytePlus 提供商下的模型常量覆盖见 [F-062]。

## 配置优先级总结

从高到低：

1. Agent 构造函数显式参数（如 `model_api_key`）
2. 操作系统环境变量（含 `.env` 文件加载的）
3. `config.yaml` 中的配置值
4. 代码中的默认值（`VeADKConfig` 字段默认值、`consts.py` 常量）

## 相关概念

- [Agent 核心类与生命周期](/concepts/01-agent-lifecycle.md)
- [AgentBuilder 与 YAML 配置驱动](/concepts/02-agent-builder.md)
- [LLM 模型抽象](/concepts/07-llm-models.md)
- [CLI 工具集](/concepts/10-cli-tools.md)
