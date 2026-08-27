---
type: Concept
title: LLM 配置与可插拔体系
description: LLMConfig层级模型、9个提供商工厂、主备fallback机制、JSONC配置文件加载与深度合并、环境变量凭据
tags: [mobile-use, llm, config, fallback, openai, google, anthropic, pydantic]
generated: { by: source-code-to-okf-wiki/E, at: 2026-08-23T00:00:00Z }
verified: { by: source-code-to-okf-wiki/V, at: 2026-08-23T00:00:00Z }
status: verified
stale_after: 2027-08-23
sources:
  - id: mobile-use-source
    resource: "/references/mobile-use-source.md"
    title: mobile-use 源码
  - id: facts
    resource: "/references/facts.md"
    title: mobile-use 事实清单
---

# LLM 配置与可插拔体系

mobile-use 的 LLM 配置体系设计精细：每个 Agent 节点可独立选择提供商和模型，每个节点配备主模型和 fallback 模型，配置通过 JSONC 文件分层加载并深度合并。系统支持 9 个 LLM 提供商，运行时通过统一的工厂函数创建 LLM 实例，并通过异步泛型函数实现主备自动切换。

## 配置模型层级

LLM 配置由四个 Pydantic 模型构成嵌套结构 [F-033~F-036]：

```text
LLMConfig
├── planner: LLMWithFallback
├── orchestrator: LLMWithFallback
├── contextor: LLMWithFallback
├── cortex: LLMWithFallback
├── executor: LLMWithFallback
└── utils: LLMConfigUtils
    ├── outputter: LLMWithFallback
    ├── hopper: LLMWithFallback
    └── video_analyzer: LLMWithFallback | None
```

### LLM

`LLM` 继承 `BaseModel`，是最基础的配置单元 [F-033]：

- `provider: LLMProvider`：提供商标识
- `model: str`：模型名称
- `validate_provider(name: str)` 方法：根据 provider 检查对应环境变量是否已设置，缺失时抛出异常

`__str__` 返回 `provider/model` 格式字符串。

### LLMWithFallback

`LLMWithFallback` 继承 `LLM`，新增 `fallback: LLM` 字段 [F-034]。这意味着每个节点有一个主模型和一个备用模型，备用模型可以是不同提供商的不同模型。`__str__` 返回 `provider/model (fallback: fallback_provider/fallback_model)`。

### LLMConfigUtils

工具节点的配置容器 [F-035]：

- `outputter: LLMWithFallback`：必需
- `hopper: LLMWithFallback`：必需
- `video_analyzer: LLMWithFallback | None = None`：可选，未配置时视频分析功能不可用

### LLMConfig

顶层配置模型，包含 5 个图节点和 1 个 utils 容器 [F-036]。核心方法：

- `validate_providers()`：逐一验证所有 8 个节点（5 个 agent + 3 个 utils）的 provider 凭据 [F-037]
- `get_agent(item: AgentNode) -> LLMWithFallback`：按节点名获取 agent LLM 配置 [F-038]
- `get_utils(item: LLMUtilsNode) -> LLMWithFallback`：按节点名获取 utils LLM 配置，未配置时抛出 ValueError

### 类型字面量

```python
LLMProvider = Literal[
    "openai", "google", "openrouter", "xai", "vertexai",
    "minitap", "anthropic", "azure", "minimax"
]
AgentNode = Literal["planner", "orchestrator", "contextor", "cortex", "executor"]
LLMUtilsNode = Literal["outputter", "hopper", "video_analyzer"]
```

9 个提供商覆盖了主流 LLM 服务 [F-030]。注意 `cerebras` 作为依赖存在（langchain-cerebras），但未出现在 LLMProvider 字面量中。

## 提供商工厂函数

`services/llm.py` 为每个提供商提供了独立的工厂函数 [F-173]：

| 函数 | 提供商 | 底层 LangChain 类 |
|------|--------|------------------|
| `get_openai_llm` | OpenAI / OpenRouter / MiniMax / Minitap | `ChatOpenAI` |
| `get_google_llm` | Google Gemini | `ChatGoogleGenerativeAI` |
| `get_anthropic_llm` | Anthropic Claude | `ChatAnthropic` |
| `get_vertex_llm` | Google Vertex AI | `ChatVertexAI` |
| `get_grok_llm` | xAI Grok | `ChatXAI` |
| `get_azure_llm` | Azure AI | `AzureChatOpenAI` |
| `get_minimax_llm` | MiniMax | `ChatOpenAI`（兼容端点） |
| `get_minitap_llm` | Minitap 平台 | `ChatOpenAI`（自定义 base_url） |

### get_llm 统一入口

`get_llm(ctx, name, is_utils=False, use_fallback=False, temperature=0)` 是运行时获取 LLM 实例的统一函数 [F-172]：

1. 根据 `name` 从 `ctx.llm_config` 获取 `LLMWithFallback`（agent 节点调 `get_agent`，utils 节点调 `get_utils`）
2. 若 `use_fallback=True`，取 fallback LLM；否则取主 LLM
3. 根据 provider 字段调用对应工厂函数
4. 返回配置好的 LangChain BaseChatModel 实例

### Google 模型特殊处理

Google 模型（`ChatGoogleGenerativeAI` 和 `ChatVertexAI`）有两个特殊配置 [F-175]：

- `max_retries=2`：比默认重试次数更保守
- 不支持 `parallel_tool_calls`：ExecutorNode 在绑定工具时检测 provider，对 Google 模型跳过该参数 [F-063]

### Minitap 提供商

`get_minitap_llm` 返回的 `ChatOpenAI` 实例配置特殊 [F-174]：

- `base_url` 为 `{MINITAP_BASE_URL}/api/v1`（默认 `https://platform.minitap.ai/api/v1`）
- 通过 `default_query` 传递 `sessionId` 和 `traceOnlyUsage`
- 通过 `default_headers` 传递 `X-Agent-Name` 和 `X-Project-Name`

Minitap 本质是 OpenAI 兼容的代理平台，用户只需配置 `MINITAP_API_KEY`，无需为每个底层提供商单独配置密钥。

## Fallback 机制

### with_fallback 泛型函数

`with_fallback[T]` 是异步泛型函数，实现主备 LLM 自动切换 [F-171]：

```python
async def with_fallback[T](
    main_call: Callable[[], Coroutine[Any, Any, T]],
    fallback_call: Callable[[], Coroutine[Any, Any, T]],
    none_should_fallback: bool = True,
) -> T:
    try:
        result = await main_call()
        if result is None and none_should_fallback:
            return await fallback_call()
        return result
    except Exception:
        return await fallback_call()
```

逻辑：先执行 main_call，若抛出异常或返回 None（且 none_should_fallback 为 True），则执行 fallback_call。fallback_call 的异常会直接向上抛出。

### Agent 中的使用模式

每个 Agent 节点的 LLM 调用遵循统一模式 [F-054]：

```python
main_llm = get_llm(ctx=self.ctx, name="cortex")
fallback_llm = get_llm(ctx=self.ctx, name="cortex", use_fallback=True)

main_chain = main_llm.with_structured_output(CortexOutput)
fallback_chain = fallback_llm.with_structured_output(CortexOutput)

result = await with_fallback(
    main_call=lambda: main_chain.ainvoke(messages),
    fallback_call=lambda: fallback_chain.ainvoke(messages),
)
```

`with_structured_output` 确保不同提供商的 LLM 返回相同的 Pydantic 模型类型，这是 fallback 可以跨提供商工作的前提——输出结构统一，底层模型可替换。

### LLM 调用超时

`invoke_llm_with_timeout_message[T]` 异步泛型函数包装 LLM 调用，超过 `timeout_seconds`（默认 10 秒）后显示 "Waiting for LLM call response..." 消息 [F-170]，避免用户在长耗时调用时无反馈。

## 配置文件加载

### 默认配置文件

`llm-config.defaults.jsonc` 内置三组预设 [F-013]：

- **default**：使用 OpenAI 提供商。planner/orchestrator/contextor/executor 使用 `gpt-5-nano`（fallback `gpt-5-mini`），cortex 使用 `gpt-5`（fallback `o4-mini`），utils 节点使用 nano/mini [F-014]
- **minimax**：使用 MiniMax 提供商的配置
- **recommended**：使用 Minitap 平台。cortex 使用 `google/gemini-3-pro-preview`（fallback `google/gemini-2.5-pro`），video_analyzer 使用 `google/gemini-3-flash-preview` [F-015]

### 加载链路

配置加载经历四个函数 [F-039~F-043]：

1. **`get_default_llm_config()`**：尝试从 `llm-config.defaults.jsonc` 读取 `default` 配置；文件不存在或解析失败时回退到硬编码的 OpenAI 配置
2. **`deep_merge_llm_config(default, override)`**：深度合并两个配置字典，override 中的未知键会被忽略并打印警告 [F-041]
3. **`parse_llm_config()`**：加载默认配置，若存在 `llm-config.override.jsonc` 则深度合并；验证失败时回退到默认配置 [F-042]
4. **`initialize_llm_config()`**：调用 parse_llm_config() 并执行 validate_providers()，返回可用的 LLMConfig [F-043]

CLI 入口 `run_automation` 和 SDK 默认配置都调用 `initialize_llm_config()` 获取配置 [F-023]。

### JSONC 格式

配置文件使用 JSONC（JSON with Comments）格式，支持注释。通过 `load_jsonc()` 工具函数解析（先移除注释再解析 JSON）。用户应从 `llm-config.override.template.jsonc` 复制创建 `llm-config.override.jsonc`，只需填写需要覆盖的字段，其余继承默认值。

## 环境变量与凭据

### Settings 类

`Settings` 继承 `pydantic_settings.BaseSettings`，从环境变量和 `.env` 文件加载配置 [F-027~F-029]：

| 环境变量 | 用途 |
|---------|------|
| `OPENAI_API_KEY` | OpenAI API 密钥 |
| `GOOGLE_API_KEY` | Google Gemini API 密钥 |
| `ANTHROPIC_API_KEY` | Anthropic API 密钥 |
| `XAI_API_KEY` | xAI Grok API 密钥 |
| `OPEN_ROUTER_API_KEY` | OpenRouter API 密钥 |
| `AZURE_API_KEY` | Azure AI API 密钥 |
| `MINIMAX_API_KEY` | MiniMax API 密钥 |
| `MINITAP_API_KEY` | Minitap 平台 API 密钥 |
| `OPENAI_BASE_URL` | OpenAI 兼容端点覆盖 |
| `AZURE_BASE_URL` | Azure 端点覆盖 |
| `MINITAP_BASE_URL` | Minitap 平台地址（默认 `https://platform.minitap.ai`） |
| `ADB_HOST` / `ADB_PORT` | ADB 服务器地址 |
| `MOBILE_USE_TELEMETRY_ENABLED` | 遥测开关 |
| `PROJECT_NAME` | 项目名（发送给 Minitap 平台） |

API Key 字段类型为 `SecretStr | None`，在日志和 repr 中自动脱敏。模块加载时通过 `load_dotenv(verbose=True)` 自动加载 `.env` 文件。全局单例 `settings = Settings()` 在模块导入时初始化。

### Provider 验证

`LLM.validate_provider(name)` 方法使用 match 语句检查每个 provider 所需的环境变量 [F-033]。例如，provider 为 "openai" 时检查 `OPENAI_API_KEY`，为 "vertexai" 时调用 `validate_vertex_ai_credentials()` 检查 Google Application Default Credentials，为 "azure" 时检查 `AZURE_BASE_URL`。

验证在 `LLMConfig.validate_providers()` 中批量执行，任何一个节点缺少凭据都会抛出异常并终止启动——这是一种快速失败设计，避免在任务执行中途才发现配置问题。

## 每节点模型选择策略

默认配置体现了成本与能力的精细平衡：

| 节点 | 主模型 | Fallback | 选择理由 |
|------|--------|----------|---------|
| planner | gpt-5-nano | gpt-5-mini | 结构化子目标分解，轻量模型足够 |
| orchestrator | gpt-5-nano | gpt-5-mini | 状态推进逻辑简单 |
| contextor | gpt-5-nano | gpt-5-mini | 应用锁定验证，判断简单 |
| cortex | gpt-5 | o4-mini | 核心决策需最强推理能力 |
| executor | gpt-5-nano | gpt-5-mini | 工具调用，结构化输出 |
| outputter | gpt-5-nano | gpt-5-mini | 输出生成 |
| hopper | gpt-5-nano | gpt-5-mini | 信息提取 |
| video_analyzer | gemini-3-flash | — | 需要视觉理解能力 |

Cortex 使用最强模型，其余节点使用 nano/mini 级模型，这种配置可显著降低单次任务的 LLM 调用成本。用户可通过 override 配置自由调整每个节点的模型。

## 相关概念

- [多 Agent 协作架构](/concepts/01-multi-agent-architecture.md)
- [SDK 双层 API 与生命周期](/concepts/05-sdk-layer.md)
- [mobile-use 项目概览](/concepts/00-overview.md)
- [CLI 命令使用示例](/examples/cli-usage.md)
