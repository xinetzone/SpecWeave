---
id: config-module
title: 配置系统详解
source: veadk-python codebase analysis
category: learning
date: '2026-08-05'
status: stable
wiki_version: '1.0'
---


# 配置系统详解

## 概述

VeADK 使用基于 Pydantic Settings 的分层配置系统，支持从环境变量、`.env` 文件和 `config.yaml` 文件加载配置。配置采用优先级覆盖机制，允许灵活地在不同环境中使用不同的配置。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py)

---

## 配置加载优先级

VeADK 的配置加载遵循以下优先级（从高到低）：

1. **代码参数**：直接在代码中传递给 Agent/Runner 构造函数的参数
2. **系统环境变量**：当前进程的环境变量
3. **.env 文件**：项目根目录下的 `.env` 文件
4. **config.yaml 文件**：项目根目录下的 `config.yaml` 文件
5. **默认值**：各配置类中定义的默认值

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L45-L146](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L45-L146)

### 优先级说明

- 如果环境变量已设置，`config.yaml` 中对应的值会被忽略
- `.env` 文件中的值会被加载到环境变量中，但会被已存在的系统环境变量覆盖
- `config.yaml` 中的嵌套键会被展平为大写的环境变量格式（如 `model.agent.name` → `MODEL_AGENT_NAME`）
- 所有配置最终都有代码定义的默认值作为兜底

---

## VeADKConfig 配置类

`VeADKConfig` 是根配置类，包含所有子配置模块：

```python
class VeADKConfig(BaseModel):
    model: ModelConfig = Field(default_factory=ModelConfig)
    tool: BuiltinToolConfigs = Field(default_factory=BuiltinToolConfigs)
    prompt_pilot: PromptPilotConfig = Field(default_factory=PromptPilotConfig)
    opentelemetry_config: OpenTelemetryConfig = Field(default_factory=OpenTelemetryConfig)
    apmplus_config: APMPlusConfig = Field(default_factory=APMPlusConfig)
    cozeloop_config: CozeloopConfig = Field(default_factory=CozeloopConfig)
    tls_config: TLSConfig = Field(default_factory=TLSConfig)
    prometheus_config: PrometheusConfig = Field(default_factory=PrometheusConfig)
    tos: TOSConfig = Field(default_factory=TOSConfig)
    opensearch: OpensearchConfig = Field(default_factory=OpensearchConfig)
    mysql: MysqlConfig = Field(default_factory=MysqlConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    milvus: MilvusConfig = Field(default_factory=MilvusConfig)
    viking_knowledgebase: VikingKnowledgebaseConfig = Field(default_factory=VikingKnowledgebaseConfig)
    veidentity: VeIdentityConfig = Field(default_factory=VeIdentityConfig)
    realtime_model: RealtimeModelConfig = Field(default_factory=RealtimeModelConfig)
```

全局单例 `settings = VeADKConfig()` 在模块加载时创建，可以通过 `from veadk.config import settings` 访问。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L64-L90](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L64-L90)

---

## 配置项详解

### 1. ModelConfig - 模型配置

用于配置 Agent 推理使用的模型。

```python
class ModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_AGENT_")

    name: str = DEFAULT_MODEL_AGENT_NAME
    provider: str = DEFAULT_MODEL_AGENT_PROVIDER
    api_base: str = DEFAULT_MODEL_AGENT_API_BASE
    api_key_name: str = ""

    @cached_property
    def api_key(self) -> str:
        # 优先级：MODEL_AGENT_API_KEY > api_key_name 解析 > 默认 ARK token
```

| 字段 | 类型 | 默认值 | 环境变量 | 说明 |
|------|------|--------|----------|------|
| `name` | `str` | `DEFAULT_MODEL_AGENT_NAME` | `MODEL_AGENT_NAME` | Agent 推理模型名称 |
| `provider` | `str` | `DEFAULT_MODEL_AGENT_PROVIDER` | `MODEL_AGENT_PROVIDER` | LiteLLM 初始化的模型提供商（如 `openai`） |
| `api_base` | `str` | `DEFAULT_MODEL_AGENT_API_BASE` | `MODEL_AGENT_API_BASE` | 模型 API 基础 URL |
| `api_key_name` | `str` | `""` | `MODEL_AGENT_API_KEY_NAME` | ARK API 密钥名称，用于按名称解析密钥 |
| `api_key` | `str` | 动态解析 | `MODEL_AGENT_API_KEY` | API 密钥（cached_property，运行时解析） |

**API Key 解析优先级**：
1. `MODEL_AGENT_API_KEY` 环境变量（显式值）
2. `api_key_name` 指定的命名密钥
3. 账户中第一个 ARK 密钥（默认）

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L31-L54](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L31-L54)

---

### 2. EmbeddingModelConfig - 嵌入模型配置

```python
class EmbeddingModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_EMBEDDING_")

    name: str = DEFAULT_MODEL_EMBEDDING_NAME
    dim: int = DEFAULT_MODEL_EMBEDDING_DIM
    api_base: str = DEFAULT_MODEL_AGENT_API_BASE

    @cached_property
    def api_key(self) -> str:
        # 优先级：MODEL_EMBEDDING_API_KEY > MODEL_AGENT_API_KEY > 默认 ARK token
```

| 字段 | 环境变量前缀 | 说明 |
|------|-------------|------|
| `name` | `MODEL_EMBEDDING_NAME` | 嵌入模型名称 |
| `dim` | `MODEL_EMBEDDING_DIM` | 嵌入向量维度 |
| `api_base` | `MODEL_EMBEDDING_API_BASE` | 嵌入模型 API 基础 URL |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L57-L75](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L57-L75)

---

### 3. RealtimeModelConfig - 实时语音模型配置

```python
class RealtimeModelConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MODEL_REALTIME_")

    name: str = "doubao_realtime_voice_model"
    api_base: str = "wss://openspeech.bytedance.com/api/v3/realtime/dialogue"

    @cached_property
    def api_key(self) -> str:
        # MODEL_REALTIME_API_KEY 或 get_speech_token()
```

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `name` | `MODEL_REALTIME_NAME` | `doubao_realtime_voice_model` | 实时模型名称 |
| `api_base` | `MODEL_REALTIME_API_BASE` | `wss://openspeech.bytedance.com/api/v3/realtime/dialogue` | WebSocket API 地址 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L93-L104](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L93-L104)

---

### 4. TOSConfig - 对象存储配置

```python
class TOSConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DATABASE_TOS_")

    endpoint: str = "tos-cn-beijing.volces.com"
    region: str = "cn-beijing"

    @cached_property
    def bucket(self) -> str:
        # 动态获取或创建 bucket
```

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `endpoint` | `DATABASE_TOS_ENDPOINT` | `tos-cn-beijing.volces.com` | TOS 端点（BytePlus 自动切换） |
| `region` | `DATABASE_TOS_REGION` | `cn-beijing` | TOS 区域 |
| `bucket` | `DATABASE_TOS_BUCKET` | 动态创建 | TOS bucket 名称（cached_property） |

**BytePlus 自动适配**：当 `CLOUD_PROVIDER=byteplus` 时，endpoint 自动切换为 `tos-ap-southeast-1.bytepluses.com`，region 切换为 `ap-southeast-1`。

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/database_configs.py#L158-L177](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/database_configs.py#L158-L177)

---

### 5. 数据库配置

#### OpensearchConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `host` | `DATABASE_OPENSEARCH_HOST` | `""` | OpenSearch 主机 |
| `port` | `DATABASE_OPENSEARCH_PORT` | `9200` | 端口 |
| `username` | `DATABASE_OPENSEARCH_USERNAME` | `""` | 用户名 |
| `password` | `DATABASE_OPENSEARCH_PASSWORD` | `""` | 密码 |
| `use_ssl` | `DATABASE_OPENSEARCH_USE_SSL` | `True` | 是否使用 SSL |

#### MysqlConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `host` | `DATABASE_MYSQL_HOST` | `""` | MySQL 主机 |
| `user` | `DATABASE_MYSQL_USER` | `""` | 用户名 |
| `password` | `DATABASE_MYSQL_PASSWORD` | `""` | 密码 |
| `database` | `DATABASE_MYSQL_DATABASE` | `""` | 数据库名 |
| `charset` | `DATABASE_MYSQL_CHARSET` | `"utf8"` | 字符集 |

#### RedisConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `host` | `DATABASE_REDIS_HOST` | `""` | Redis 主机 |
| `port` | `DATABASE_REDIS_PORT` | `6379` | 端口 |
| `password` | `DATABASE_REDIS_PASSWORD` | `""` | 密码 |
| `db` | `DATABASE_REDIS_DB` | `0` | 数据库编号 |

#### MilvusConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `uri` | `DATABASE_MILVUS_URI` | `""` | Milvus URI（本地文件路径或远程地址） |
| `token` | `DATABASE_MILVUS_TOKEN` | `""` | 认证 token |
| `user` | `DATABASE_MILVUS_USER` | `""` | 用户名 |
| `password` | `DATABASE_MILVUS_PASSWORD` | `""` | 密码 |
| `db_name` | `DATABASE_MILVUS_DB_NAME` | `"default"` | 数据库名 |
| `overwrite` | `DATABASE_MILVUS_OVERWRITE` | `False` | 是否覆盖 |

#### VikingKnowledgebaseConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `project` | `DATABASE_VIKING_PROJECT` | `"default"` | Viking DB 项目名 |
| `region` | `DATABASE_VIKING_REGION` | `"cn-beijing"` | 区域 |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/database_configs.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/database_configs.py)

---

### 6. 可观测性配置

#### OpenTelemetryConfig

| 字段 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `trace_content` | `OBSERVABILITY_OPENTELEMETRY_TRACE_CONTENT` | `True` | 是否在追踪中收集 Agent/LLM/工具的输入输出内容 |

#### APMPlusConfig

| 字段 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `otel_exporter_endpoint` | `OBSERVABILITY_OPENTELEMETRY_APMPLUS_ENDPOINT` | `DEFAULT_APMPLUS_OTEL_EXPORTER_ENDPOINT` | APMPlus OTLP 端点 |
| `otel_exporter_service_name` | `OBSERVABILITY_OPENTELEMETRY_APMPLUS_SERVICE_NAME` | `DEFAULT_APMPLUS_OTEL_EXPORTER_SERVICE_NAME` | 服务名称 |
| `otel_exporter_api_key` | `OBSERVABILITY_OPENTELEMETRY_APMPLUS_API_KEY` | 动态获取 | API Key（cached_property） |

#### CozeloopConfig

| 字段 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `otel_exporter_endpoint` | `OBSERVABILITY_OPENTELEMETRY_COZELOOP_ENDPOINT` | `DEFAULT_COZELOOP_OTEL_EXPORTER_ENDPOINT` | CozeLoop OTLP 端点 |
| `otel_exporter_api_key` | `OBSERVABILITY_OPENTELEMETRY_COZELOOP_API_KEY` | `""` | API Key |
| `otel_exporter_space_id` | `OBSERVABILITY_OPENTELEMETRY_COZELOOP_SERVICE_NAME` | 动态创建 | 工作空间 ID（cached_property） |

#### TLSConfig

| 字段 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `otel_exporter_endpoint` | `OBSERVABILITY_OPENTELEMETRY_TLS_ENDPOINT` | `DEFAULT_TLS_OTEL_EXPORTER_ENDPOINT` | TLS OTLP 端点 |
| `otel_exporter_region` | `OBSERVABILITY_OPENTELEMETRY_TLS_REGION` | `DEFAULT_TLS_OTEL_EXPORTER_REGION` | 区域 |
| `otel_exporter_topic_id` | `OBSERVABILITY_OPENTELEMETRY_TLS_SERVICE_NAME` | 动态获取 | Topic ID（cached_property） |

#### PrometheusConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `pushgateway_url` | `OBSERVABILITY_PROMETHEUS_PUSHGATEWAY_URL` | `""` | Pushgateway URL |
| `pushgateway_username` | `OBSERVABILITY_PROMETHEUS_PUSHGATEWAY_USERNAME` | `""` | 用户名 |
| `pushgateway_password` | `OBSERVABILITY_PROMETHEUS_PUSHGATEWAY_PASSWORD` | `""` | 密码 |

**环境变量开关**：
- `ENABLE_APMPLUS=true`：启用 APMPlus 导出器
- `ENABLE_COZELOOP=true`：启用 CozeLoop 导出器
- `ENABLE_TLS=true`：启用 TLS 导出器

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/tracing_configs.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/tracing_configs.py)

---

### 7. 工具配置

#### VeSearchConfig

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `endpoint` | `TOOL_VESEARCH_ENDPOINT` | `""` | VeSearch 端点（bot_id） |
| `api_key` | `TOOL_VESEARCH_API_KEY` | 动态获取 | API Key（cached_property） |

#### VeSpeechConfig（TTS）

| 字段 | 环境变量前缀 | 默认值 | 说明 |
|------|-------------|--------|------|
| `endpoint` | `TOOL_VESPEECH_ENDPOINT` | `""` | 语音服务端点 |
| `api_key` | `TOOL_VESPEECH_API_KEY` | 动态获取 | API Key（cached_property） |

#### PromptPilotConfig

| 字段 | 环境变量 | 默认值 | 说明 |
|------|----------|--------|------|
| `api_key` | `PROMPT_PILOT_API_KEY` | 动态获取 | PromptPilot API Key |

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/tool_configs.py](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/tool_configs.py)

---

## config.yaml 配置文件

### 加载机制

1. 使用 `find_dotenv(filename="config.yaml", usecwd=True)` 从当前工作目录向上查找 `config.yaml`
2. 使用 `yaml.safe_load()` 加载 YAML 文件
3. 使用 `flatten_dict()` 将嵌套字典展平（`{"a": {"b": 1}}` → `{"a_b": 1}`）
4. 将所有键转为大写（`a_b` → `A_B`）
5. 将这些键值对设置到环境变量中（如果环境变量中不存在同名键）
6. `.env` 文件中的值优先级高于 `config.yaml`

> 源码位置：[file:///d:/AI/.chaos/libs/veadk-python/veadk/utils/misc.py#L132-L165](file:///d:/AI/.chaos/libs/veadk-python/veadk/utils/misc.py#L132-L165)

### 完整配置示例

参考 `config.yaml.full` 文件，主要配置节包括：

```yaml
model:
  agent:
    provider: openai
    name: doubao-seed-1-6-250615
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:
    max_llm_calls: 100
  embedding:
    name: doubao-embedding-vision-250615
    dim: 2048
    api_base: https://ark.cn-beijing.volces.com/api/v3/

volcengine:
  access_key:
  secret_key:

tool:
  vesearch:
    endpoint:
    api_key:
  text_to_speech:
    app_id:
    api_key:
    speaker:
  lark:
    endpoint:
    api_key:
    token:

observability:
  opentelemetry:
    trace_content: true
    apmplus:
      endpoint: http://apmplus-cn-beijing.volces.com:4317
      api_key:
      service_name:
    cozeloop:
      endpoint: https://api.coze.cn/v1/loop/opentelemetry/v1/traces
      api_key:
      service_name:
    tls:
      endpoint: https://tls-cn-beijing.volces.com:4318/v1/traces
      service_name:
      region: cn-beijing

database:
  opensearch:
    host:
    port: 9200
    username:
    password:
  mysql:
    host:
    user:
    password:
    database:
    charset: utf8
  redis:
    host:
    port: 6379
    password:
    db: 0
  milvus:
    uri: ./milvus.db
  viking:
    project: default
    region: cn-beijing
  tos:
    endpoint: tos-cn-beijing.volces.com
    region: cn-beijing
    bucket:

veadk:
  tracer:
    apmplus: true
    cozeloop: true
    tls: true
```

> 参考文件：[file:///d:/AI/.chaos/libs/veadk-python/config.yaml.full](file:///d:/AI/.chaos/libs/veadk-python/config.yaml.full)

---

## 环境变量映射

### 模型相关

| 环境变量 | 对应配置 | 说明 |
|----------|----------|------|
| `MODEL_AGENT_NAME` | `model.name` | Agent 模型名称 |
| `MODEL_AGENT_PROVIDER` | `model.provider` | 模型提供商 |
| `MODEL_AGENT_API_BASE` | `model.api_base` | API 基础 URL |
| `MODEL_AGENT_API_KEY` | `model.api_key` | API 密钥（最高优先级） |
| `MODEL_AGENT_API_KEY_NAME` | `model.api_key_name` | API 密钥名称 |
| `MODEL_AGENT_MAX_LLM_CALLS` | Runner RunConfig | 最大 LLM 调用次数（默认 100） |
| `MODEL_EMBEDDING_NAME` | 嵌入模型 | 嵌入模型名称 |
| `MODEL_EMBEDDING_DIM` | 嵌入模型 | 向量维度 |
| `MODEL_EMBEDDING_API_KEY` | 嵌入模型 | 嵌入模型 API Key |
| `MODEL_REALTIME_API_KEY` | 实时模型 | 实时语音 API Key |

### 火山引擎凭证

| 环境变量 | 说明 |
|----------|------|
| `VOLCENGINE_ACCESS_KEY` | 火山引擎 Access Key |
| `VOLCENGINE_SECRET_KEY` | 火山引擎 Secret Key |
| `BYTEPLUS_ACCESS_KEY` | BytePlus Access Key（自动映射为 VOLCENGINE_ACCESS_KEY） |
| `BYTEPLUS_SECRET_KEY` | BytePlus Secret Key（自动映射为 VOLCENGINE_SECRET_KEY） |
| `CLOUD_PROVIDER` | 云提供商（`volces` 或 `byteplus`） |

### 追踪相关

| 环境变量 | 说明 |
|----------|------|
| `ENABLE_APMPLUS` | 设为 `true` 启用 APMPlus 导出器 |
| `ENABLE_COZELOOP` | 设为 `true` 启用 CozeLoop 导出器 |
| `ENABLE_TLS` | 设为 `true` 启用 TLS 日志导出器 |
| `OBSERVABILITY_OPENTELEMETRY_TRACE_CONTENT` | 是否追踪内容（默认 true） |

### AgentKit 相关

| 环境变量 | 说明 |
|----------|------|
| `AGENTKIT_TOOL_ID` | AgentKit 工具 ID |
| `AGENTKIT_TOOL_SERVICE_CODE` | 服务代码（默认 `agentkit`） |
| `AGENTKIT_TOOL_REGION` | 区域（默认 `cn-beijing`） |
| `AGENTKIT_SKILL_HOST` | Skill 服务主机 |

### 运行时

| 环境变量 | 说明 |
|----------|------|
| `LITELLM_LOCAL_MODEL_COST_MAP` | LiteLLM 本地模型成本映射（VeADK 默认设为 `True` 以加速导入） |

---

## getenv 工具函数

VeADK 提供了一个增强的 `getenv` 函数，支持默认值和 BytePlus 密钥自动映射：

```python
def getenv(
    env_name: str,
    default_value: Any = "",
    allow_false_values: bool = False,
) -> str
```

**参数**：
- `env_name: str` - 环境变量名称
- `default_value: Any` - 默认值（默认 `""`）
- `allow_false_values: bool` - 是否允许 None 或 false 值（默认 `False`，此时空值会抛出 ValueError）

**功能**：
1. 获取环境变量值
2. 如果是 `VOLCENGINE_ACCESS_KEY` 或 `VOLCENGINE_SECRET_KEY` 且 `CLOUD_PROVIDER=byteplus`，自动从 `BYTEPLUS_ACCESS_KEY`/`BYTEPLUS_SECRET_KEY` 映射
3. 如果 `allow_false_values=False` 且值为空，抛出 `ValueError` 提示用户设置环境变量

> 源码位置：
> - [file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L92-L130](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L92-L130)
> - [file:///d:/AI/.chaos/libs/veadk-python/veadk/utils/misc.py#L105-L129](file:///d:/AI/.chaos/libs/veadk-python/veadk/utils/misc.py#L105-L129)

---

## 配置降级策略

当某些配置项缺失时，VeADK 采用以下降级策略：

1. **模型 API Key**：显式值 → 环境变量 → 命名密钥解析 → 默认 ARK 密钥
2. **会话服务**：传入的 session_service → 短期记忆的 session_service → 内存会话服务
3. **RunProcessor**：Runner 参数 → Agent.run_processor → NoOpRunProcessor
4. **TOS endpoint/region**：根据 CLOUD_PROVIDER 自动切换（火山引擎/BytePlus）
5. **长期记忆**：Runner 参数 → Agent 配置 → 不启用
6. **追踪导出器**：环境变量开关控制是否启用，未启用则不添加导出器

---

## 使用示例

### 示例 1：使用 .env 文件配置

在项目根目录创建 `.env` 文件：

```env
# .env 文件
MODEL_AGENT_NAME=doubao-pro-32k
MODEL_AGENT_PROVIDER=openai
MODEL_AGENT_API_BASE=https://ark.cn-beijing.volces.com/api/v3/
MODEL_AGENT_API_KEY=your-api-key-here
VOLCENGINE_ACCESS_KEY=your-ak
VOLCENGINE_SECRET_KEY=your-sk
ENABLE_APMPLUS=true
```

然后在代码中直接使用：

```python
import asyncio
from veadk import Agent, Runner

async def main():
    # 自动从 .env 加载配置
    agent = Agent(name="env-demo")
    runner = Runner(agent=agent, app_name="env-app")

    answer = await runner.run(messages="你好", session_id="env-session")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

### 示例 2：使用 config.yaml 配置

在项目根目录创建 `config.yaml`：

```yaml
model:
  agent:
    name: doubao-pro-32k
    provider: openai
    api_base: https://ark.cn-beijing.volces.com/api/v3/

database:
  tos:
    region: cn-beijing
```

```python
# 代码中不需要额外配置，自动加载
from veadk.config import settings
print(f"Using model: {settings.model.name}")
```

### 示例 3：代码中显式配置（最高优先级）

```python
agent = Agent(
    name="explicit-config",
    model_name="doubao-pro-32k",
    model_provider="openai",
    model_api_base="https://ark.cn-beijing.volces.com/api/v3/",
    model_api_key="your-explicit-api-key",  # 覆盖环境变量和 config.yaml
    model_extra_config={
        "extra_headers": {"X-Custom-Header": "value"},
    },
)
```

### 示例 4：代码中访问配置

```python
from veadk.config import settings, getenv

# 访问模型配置
print(f"Model name: {settings.model.name}")
print(f"Model provider: {settings.model.provider}")

# 动态获取 API Key（会触发解析）
api_key = settings.model.api_key
print(f"API Key loaded: {bool(api_key)}")

# 使用 getenv 获取环境变量
try:
    ak = getenv("VOLCENGINE_ACCESS_KEY")
    print(f"AK: {ak[:8]}...")
except ValueError:
    print("VOLCENGINE_ACCESS_KEY not set")
```

### 示例 5：最小化配置（零配置启动）

不提供任何配置文件或环境变量，使用默认值（需要确保有默认 ARK 密钥配置）：

```python
import asyncio
from veadk import Agent, Runner

async def main():
    # 所有配置使用默认值
    agent = Agent(instruction="You are a helpful assistant.")
    runner = Runner(agent=agent, app_name="minimal")

    answer = await runner.run(messages="Hi!", session_id="minimal-session")
    print(answer)

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 配置最佳实践

1. **开发环境**：使用 `.env` 文件存储本地开发配置，不要提交到版本控制
2. **生产环境**：使用环境变量或配置中心（如 Nacos）注入配置，不要在镜像中硬编码密钥
3. **密钥管理**：
   - 不要在代码或 `config.yaml` 中硬编码 API Key
   - 使用 `MODEL_AGENT_API_KEY_NAME` 指定命名密钥，通过 IAM 角色自动获取
   - 生产环境使用 STS token 而非永久 AK/SK
4. **多环境配置**：通过 `CLOUD_PROVIDER=byteplus` 等环境变量区分不同云环境
5. **配置优先级理解**：调试时注意代码参数会覆盖所有其他配置源，排查问题时先检查是否有显式传参
6. **追踪配置**：生产环境建议启用 `ENABLE_APMPLUS` 或 `ENABLE_COZELOOP` 以便问题排查
