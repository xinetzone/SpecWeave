---
id: veadk-python-configuration
title: 配置指南
source: 'seven-concepts: veadk-python-wiki'
category: learning
tags:
- VeADK
- 火山引擎
- AI Agent
- 配置
- API Key
- config.yaml
- 环境变量
date: '2026-08-05'
status: stable
author: seven-concepts knowledge-scenario
summary: VeADK-Python 配置指南，涵盖配置优先级、最小配置、config.yaml参考、环境变量列表、API Key获取及配置降级策略
wiki_version: '1.0'
---


# VeADK-Python 配置指南

本文档介绍 VeADK-Python 的配置体系，包括配置方式优先级、最小配置示例、完整配置参考、环境变量列表以及配置降级策略。

---

## 配置方式优先级

VeADK 采用**四级优先级**配置体系，高优先级配置会覆盖低优先级配置：

```
参数直接传递 > 环境变量 > config.yaml 配置文件 > 默认值
```

### 优先级详解

| 优先级 | 配置方式 | 适用场景 | 示例 |
|--------|----------|----------|------|
| 1（最高） | 代码中直接传参 | 多租户、动态切换配置 | `Agent(model_api_key="sk-xxx")` |
| 2 | 环境变量 | 容器化部署、CI/CD、生产环境 | `export MODEL_AGENT_API_KEY=sk-xxx` |
| 3 | config.yaml 文件 | 项目级配置、本地开发 | 在项目根目录创建 `config.yaml` |
| 4（最低） | 框架默认值 | 快速原型、零配置启动 | 默认模型、默认API端点等 |

配置加载逻辑定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L64-L146](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L64-L146)。

---

## 最小配置示例

运行一个最小化的 Agent，只需要配置模型和 API Key。以下是三种配置方式的最小示例。

### 方式一：使用 config.yaml（推荐）

在项目根目录创建 `config.yaml` 文件（[file:///d:/AI/.chaos/libs/veadk-python/README.md#L56-L65](file:///d:/AI/.chaos/libs/veadk-python/README.md#L56-L65)）：

```yaml
model:
  agent:
    provider: openai
    name: doubao-seed-2-1-pro-260628
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key: "your-ark-api-key-here"
```

> **注意**：
> - 默认模型名称定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L22-L24](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L22-L24)，当前版本默认模型为 `doubao-seed-2-1-pro-260628`
> - 默认 API 端点为 `https://ark.cn-beijing.volces.com/api/v3/`
> - 简单配置示例见 [file:///d:/AI/.chaos/libs/veadk-python/config.yaml.simple](file:///d:/AI/.chaos/libs/veadk-python/config.yaml.simple)

### 方式二：使用 .env 文件

在项目根目录创建 `.env` 文件：

```env
MODEL_AGENT_API_KEY=your-ark-api-key-here
MODEL_AGENT_NAME=doubao-seed-2-1-pro-260628
MODEL_AGENT_PROVIDER=openai
MODEL_AGENT_API_BASE=https://ark.cn-beijing.volces.com/api/v3/
```

.env 文件会在启动时自动加载（[file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L45-L52](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L45-L52)）。

### 方式三：代码中直接传参

```python
from veadk import Agent, Runner

agent = Agent(
    name="my_agent",
    instruction="你是一个有帮助的AI助手",
    model_name="doubao-seed-2-1-pro-260628",
    model_provider="openai",
    model_api_base="https://ark.cn-beijing.volces.com/api/v3/",
    model_api_key="your-ark-api-key-here",
)
```

---

## config.yaml 完整配置参考

VeADK 提供了完整的配置文件示例 [file:///d:/AI/.chaos/libs/veadk-python/config.yaml.full](file:///d:/AI/.chaos/libs/veadk-python/config.yaml.full)。以下是各配置模块的详细说明。

### 模型配置（model）

```yaml
model:
  # [必填] Agent 推理主模型
  agent:
    provider: openai                    # 模型提供商，默认 openai（OpenAI 兼容接口）
    name: doubao-seed-2-1-pro-260628    # 模型名称
    api_base: https://ark.cn-beijing.volces.com/api/v3/  # API 端点
    api_key:                            # API Key（可留空，通过环境变量或ARK服务获取）
    encrypted: true                     # 是否加密传输，默认 true
    caching: enabled                    # 是否启用缓存，enabled/disabled
    max_llm_calls: 100                  # 单次对话最大 LLM 调用次数

  # [可选] LLM-as-a-judge 评估模型
  judge:
    name: doubao-seed-2-1-pro-260628
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:

  # [可选] 知识库 Embedding 模型
  embedding:
    name: doubao-embedding-vision-250615
    dim: 2048                           # Embedding 维度
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:

  # [可选] 视频生成模型
  video:
    name: doubao-seedance-2-0-260128
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:

  # [可选] 图片生成模型
  image:
    name: doubao-seedream-5-0-260128
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:

  # [可选] 图片编辑模型
  edit:
    name: doubao-seededit-3-0-i2i-250628
    api_base: https://ark.cn-beijing.volces.com/api/v3/
    api_key:
```

模型默认值定义在 [file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L20-L94](file:///d:/AI/.chaos/libs/veadk-python/veadk/consts.py#L20-L94)。

### 火山引擎凭证配置（volcengine）

```yaml
volcengine:
  # [可选] 火山引擎 AK/SK，用于 VikingDB 和 web_search 工具等
  access_key:
  secret_key:
```

### AgentKit 配置（agentkit）

```yaml
agentkit:
  tool_id:                    # 默认 AgentKit 工具 ID
  tool_id_script:             # 代码执行工具专用 ID
  tool_id_skills:             # 技能执行工具专用 ID
  tool_id_opencode:           # 编码工具专用 ID
  tool_host:                  # AgentKit 端点
  tool_service_code: agentkit # 服务代码
  tool_region: cn-beijing     # 区域
  tool_scheme: https
  top_scheme: https
```

### 工具配置（tool）

```yaml
tool:
  # [可选] 火山引擎智能搜索
  vesearch:
    endpoint:                 # bot_id
    api_key:

  # [可选] 网页抓取工具
  web_scraper:
    endpoint:
    api_key:                  # token

  # [可选] 语音合成 TTS
  text_to_speech:
    app_id:                   # app_id
    api_key:                  # app_secret
    speaker:                  # 音色

  # [可选] 飞书集成
  lark:
    endpoint:                 # app_id
    api_key:                  # app_secret
    token:                    # user_token

  # [可选] 飞书机器人渠道
  feishu_channel:
    app_id:
    app_secret:
    transport: ws             # ws 或 webhook

  # [可选] 移动应用使用
  mobile_use:
    tool_id:
      - product_id-pod_id_1

  # [可选] 视频点播 VOD
  vod:
    groups:
    timeout: 10.0

  # LAS 数据服务
  las:
    url:                      # MCP SSE URL
    dataset_id:

  # MCP 路由
  mcp_router:
    url:                      # MCP SSE/streamable-http URL
    api_key:

  # 沙箱工具
  code_sandbox:
    url:
    api_key:
  browser_sandbox:
    url:
    api_key:
  computer_sandbox:
    url:
    api_key:

  # LLM 内容安全
  llm_shield:
    app_id:
```

### 可观测性配置（observability）

```yaml
observability:
  opentelemetry:
    trace_content: true       # 是否收集 Agent/LLM/工具的输入输出内容
    apmplus:
      endpoint: http://apmplus-cn-beijing.volces.com:4317
      api_key:
      service_name:
    cozeloop:
      endpoint: https://api.coze.cn/v1/loop/opentelemetry/v1/traces
      api_key:
      service_name:           # Coze Loop space_id
    tls:
      endpoint: https://tls-cn-beijing.volces.com:4318/v1/traces
      service_name:           # TLS topic_id
      region: cn-beijing

  # Prometheus 评估数据导出
  prometheus:
    pushgateway_url:
    username:
    password:
```

### 数据库配置（database）

```yaml
database:
  # [可选] OpenSearch
  opensearch:
    host:                     # 不带 http:// 或 https://
    port: 9200
    username:
    password:

  # [可选] MySQL
  mysql:
    host:
    user:
    password:
    database:
    charset: utf8

  # [可选] PostgreSQL
  postgresql:
    host:
    user:
    password:
    database:

  # [可选] Redis
  redis:
    host:
    port: 6379
    password:
    db: 0

  # [可选] Milvus 向量数据库
  milvus:
    uri: ./milvus.db          # 本地 Milvus Lite 或远程 URI
    # token:
    # user:
    # password:

  # [可选] 火山引擎 VikingDB
  viking:
    project: default
    region: cn-beijing

  # [可选] TOS 对象存储
  tos:
    endpoint: tos-cn-beijing.volces.com
    region: cn-beijing
    bucket:

  # Mem0 长期记忆
  mem0:
    base_url: https://api.mem0.ai/v1
    api_key:

  # OpenViking 知识库和记忆
  openviking:
    url: http://127.0.0.1:1933
    api_key: your-openviking-api-key

  # TOS 向量存储
  tos_vector:
    endpoint: tosvectors-cn-beijing.volces.com
    region: cn-beijing
    bucket:
    account_id:

  # TOS ContextBucket 长期记忆
  tos_context:
    account_id:
    control_endpoint:
    bucket_name:
    endpoint: tos-cn-beijing.volces.com
    region: cn-beijing
```

### 其他配置

```yaml
# Nacos 动态配置
nacos:
  endpoint:
  password:

# Prompt Pilot 提示词优化
prompt_pilot:
  api_key:

# 日志级别
logging:
  level: DEBUG               # ERROR | WARNING | INFO | DEBUG

# VeADK Tracer 开关
veadk:
  tracer:
    apmplus: true
    cozeloop: true
    tls: true
```

---

## API Key 获取方式

VeADK 使用火山引擎方舟（ARK）平台的大模型服务。以下是获取 API Key 的步骤：

### 步骤一：注册火山引擎账号

1. 访问 [火山引擎官网](https://www.volcengine.com/) 注册账号
2. 完成实名认证

### 步骤二：开通方舟平台服务

1. 登录 [火山引擎方舟控制台](https://console.volcengine.com/ark/)
2. 开通方舟（ARK）服务
3. 创建推理接入点（Endpoint），获取对应的模型接入地址和 API Key

### 步骤三：获取 API Key

在方舟控制台的「API Key 管理」页面创建 API Key，格式通常为 `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`。

### 步骤四：配置 API Key

根据配置优先级选择合适的配置方式：

- **本地开发**：使用 `.env` 文件或 `config.yaml`
- **生产环境**：使用环境变量注入，不要硬编码到代码中

---

## 环境变量列表

VeADK 使用 `pydantic-settings` 管理环境变量，模型配置的环境变量前缀为 `MODEL_AGENT_`（[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L32-L32](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L32-L32)）。

### 核心环境变量

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `MODEL_AGENT_API_KEY` | Agent 模型 API Key（最高优先级） | 无 |
| `MODEL_AGENT_API_KEY_NAME` | ARK API Key 名称（用于从 ARK 服务获取 token） | 空 |
| `MODEL_AGENT_NAME` | 模型名称 | `doubao-seed-2-1-pro-260628` |
| `MODEL_AGENT_PROVIDER` | 模型提供商 | `openai` |
| `MODEL_AGENT_API_BASE` | 模型 API 端点 | `https://ark.cn-beijing.volces.com/api/v3/` |
| `MODEL_AGENT_MAX_LLM_CALLS` | 单次对话最大 LLM 调用次数 | `100` |
| `MODEL_AGENT_ENCRYPTED` | 是否加密传输 | `true` |
| `MODEL_AGENT_CACHING` | 是否启用缓存 | `enabled` |

### Embedding 模型环境变量

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `MODEL_EMBEDDING_API_KEY` | Embedding 模型 API Key | 复用 `MODEL_AGENT_API_KEY` |
| `MODEL_EMBEDDING_NAME` | Embedding 模型名称 | `doubao-embedding-vision-250615` |
| `MODEL_EMBEDDING_DIM` | Embedding 维度 | `2048` |

### 火山引擎云服务环境变量

| 环境变量 | 说明 |
|----------|------|
| `VOLCENGINE_ACCESS_KEY` | 火山引擎 Access Key |
| `VOLCENGINE_SECRET_KEY` | 火山引擎 Secret Key |
| `CLOUD_PROVIDER` | 云提供商，`volcengine`（默认）或 `byteplus` |
| `BYTEPLUS_ACCESS_KEY` | BytePlus Access Key（自动映射到 VOLCENGINE_ACCESS_KEY） |
| `BYTEPLUS_SECRET_KEY` | BytePlus Secret Key（自动映射到 VOLCENGINE_SECRET_KEY） |

### Tracing 环境变量

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `ENABLE_APMPLUS` | 是否启用 APMPlus 追踪 | `false` |
| `ENABLE_COZELOOP` | 是否启用 CozeLoop 追踪 | `false` |
| `ENABLE_TLS` | 是否启用 TLS 日志追踪 | `false` |

### AgentKit 环境变量

| 环境变量 | 说明 |
|----------|------|
| `AGENTKIT_TOOL_ID` | AgentKit 工具 ID（自动探测 skills_mode） |
| `AGENTKIT_TOOL_SERVICE_CODE` | AgentKit 服务代码 |
| `AGENTKIT_TOOL_REGION` | AgentKit 区域 |
| `AGENTKIT_TOOL_HOST` | AgentKit 主机地址 |
| `AGENTKIT_SKILL_HOST` | AgentKit 技能服务主机 |

### 飞书渠道环境变量

| 环境变量 | 说明 |
|----------|------|
| `FEISHU_APP_ID` | 飞书应用 ID（用于 AgentKit 飞书渠道） |
| `FEISHU_APP_SECRET` | 飞书应用 Secret |
| `TOOL_FEISHU_CHANNEL_APP_ID` | 飞书机器人 App ID |
| `TOOL_FEISHU_CHANNEL_APP_SECRET` | 飞书机器人 App Secret |

### 运行时环境变量

| 环境变量 | 说明 | 默认值 |
|----------|------|--------|
| `HOST` | 服务监听地址 | `0.0.0.0` |
| `PORT` | 服务监听端口 | `8000` |
| `LITELLM_LOCAL_MODEL_COST_MAP` | LiteLLM 本地模型成本映射（自动设为 True 加速导入） | `True` |

---

## 配置降级策略

VeADK 采用容错设计理念，在配置缺失时提供多级降级策略，确保 Agent 尽可能可用。

### API Key 四级降级链

模型 API Key 的解析遵循严格的优先级链（[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L217-L232](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L217-L232)）：

```
1. 显式传入 model_api_key 参数
   ↓ 未设置
2. MODEL_AGENT_API_KEY 环境变量
   ↓ 未设置
3. model_api_key_name → 通过 ARK Token 服务获取（get_ark_token）
   ↓ 未设置或失败
4. settings.model.api_key → get_ark_token() 获取账户第一个可用 Key
```

**设计意图**：
- 覆盖多种使用场景：代码动态传参、容器环境变量、企业级密钥轮换、快速原型开发
- 云端部署时可通过 IAM 角色自动获取凭证，无需显式配置 Key
- 每一级降级都会尝试让 Agent 正常工作，而非直接报错

**相关代码**（[file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L48-L54](file:///d:/AI/.chaos/libs/veadk-python/veadk/configs/model_configs.py#L48-L54)）：
```python
@cached_property
def api_key(self) -> str:
    if explicit := os.getenv("MODEL_AGENT_API_KEY"):
        return explicit
    if self.api_key_name:
        return get_ark_token(api_key_name=self.api_key_name)
    return get_ark_token()
```

### 模型 Fallback 策略

当 `model_name` 配置为列表时，VeADK 自动实现模型故障转移（[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L257-L273](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L257-L273)）：

- 列表第一个元素作为主模型
- 剩余元素作为 fallback 模型
- 主模型限流或故障时自动切换到下一个模型

示例：
```python
agent = Agent(
    model_name=["doubao-pro", "doubao-lite", "doubao-lite-4k"],
)
```

### BytePlus 自动映射

当 `CLOUD_PROVIDER=byteplus` 时，框架自动将 BytePlus 凭证映射为火山引擎凭证（[file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L54-L61](file:///d:/AI/.chaos/libs/veadk-python/veadk/config.py#L54-L61)）：

- `BYTEPLUS_ACCESS_KEY` → `VOLCENGINE_ACCESS_KEY`
- `BYTEPLUS_SECRET_KEY` → `VOLCENGINE_SECRET_KEY`
- 默认模型和 API 端点自动切换为 BytePlus 环境

### 会话服务降级

Runner 初始化时的会话服务降级策略（[file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L422-L434](file:///d:/AI/.chaos/libs/veadk-python/veadk/runner.py#L422-L434)）：

```
1. 显式传入 session_service
   ↓ 未提供
2. short_term_memory.session_service
   ↓ 未提供
3. 自动创建内存版 ShortTermMemory() 作为兜底
```

确保即使没有配置任何数据库，Agent 也能正常运行（使用内存会话）。

### 默认配置合并

`model_extra_config` 使用字典合并策略（[file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L239-L252](file:///d:/AI/.chaos/libs/veadk-python/veadk/agent.py#L239-L252)）：

- 框架默认注入 `veadk-version`、`veadk-source`、加密头等标识
- 用户配置通过 `|=` 运算符合并，优先级高于默认值
- 避免用户误操作导致必要头信息丢失

---

## 配置最佳实践

### 1. 本地开发

使用 `.env` 文件管理本地配置，不要将 `.env` 提交到版本控制：

```env
# .env 文件
MODEL_AGENT_API_KEY=your-local-api-key
VOLCENGINE_ACCESS_KEY=your-ak
VOLCENGINE_SECRET_KEY=your-sk
```

确保 `.gitignore` 中包含：
```
.env
config.yaml
```

### 2. 生产环境

- 使用环境变量注入敏感信息（API Key、AK/SK等）
- 不要在代码或 config.yaml 中硬编码密钥
- 推荐使用 `model_api_key_name` + ARK Token 服务实现密钥自动轮换
- 启用 TLS/APMPlus/Cozeloop 追踪便于问题排查

### 3. 多环境部署

通过 `CLOUD_PROVIDER` 环境变量区分环境：
- 国内火山引擎：`CLOUD_PROVIDER=volcengine`（默认）
- BytePlus 海外：`CLOUD_PROVIDER=byteplus`

### 4. 配置排查

当配置不生效时，按优先级反向排查：
1. 是否在代码中显式传参覆盖了配置？
2. 是否设置了相关环境变量？
3. config.yaml 文件格式是否正确（YAML 缩进）？
4. 默认值是否符合预期？

---

## 下一步

配置完成后，建议继续阅读：

- [快速入门](quickstart.md) - 5 分钟创建你的第一个 Agent
- [examples/08_model_config/](file:///d:/AI/.chaos/libs/veadk-python/examples/08_model_config/) 目录查看模型配置示例
- [examples/11_tracing/](file:///d:/AI/.chaos/libs/veadk-python/examples/11_tracing/) 目录查看链路追踪配置示例

---

> **版本说明**：本文档基于 VeADK-Python 代码库分析生成，对应 Wiki 版本 1.0。如发现文档内容与实际代码不符，请参考源代码为准。
