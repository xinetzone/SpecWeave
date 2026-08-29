---
id: "open-code-review-wiki-12"
title: "LLM 协议与 Provider 详解"
source: "https://open-codereview.ai/docs/configuration"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/12-llm-providers.toml"
---
# LLM 协议与 Provider 详解

> 本章深入解析 OCR 的 LLM 集成层——LLMClient 接口契约、三种协议实现、19 个内置 Provider、Endpoint 四策略解析链、Token 计数机制与自定义 Provider 扩展。基础 LLM 配置（`ocr config provider/model`）已在[安装与配置指南](02-installation.md)和[常见问题](09-faq.md)中介绍，本章聚焦底层协议与解析机制。

---

## 1. LLMClient 接口：极简契约

OCR 的 LLM 集成层遵循"最小接口原则"——整个 LLMClient 接口只有一个方法：

```go
// internal/llm/client.go
type LLMClient interface {
    CompletionsWithCtx(ctx context.Context, req CompletionRequest) (*CompletionResponse, error)
}
```

```go
type CompletionRequest struct {
    Model        string
    Messages     []Message
    Tools        []ToolDef
    MaxTokens    int
    Temperature  float64
    SystemPrompt string
}

type CompletionResponse struct {
    Content    string
    ToolCalls  []ToolCall
    Usage      Usage
    StopReason string
}
```

单方法接口降低了新 Provider 的实现成本，请求/响应结构体隔离了协议差异，上层 Agent 无需关心底层是 Anthropic 还是 OpenAI。

---

## 2. 三种协议详解

OCR 支持三种 LLM 协议：

| 协议 | URL 结尾 | 鉴权方式 | 特有功能 |
|------|---------|---------|---------|
| `anthropic` | `/v1/messages` | `x-api-key` | `cache_control` ephemeral |
| `openai` | `/v1/chat/completions` | `Authorization: Bearer` | streaming、reasoning_content |
| `openai-responses` | `/v1/responses` | `Authorization: Bearer` | Responses API |

协议常量定义：

```go
const (
    ProtocolAnthropic             = "anthropic"
    ProtocolOpenAIChatCompletions = "openai"
    ProtocolOpenAIResponses       = "openai-responses"
)
```

`NormalizeProtocol` 宽容归一化（接受 "claude"、"gpt" 等别名），`ValidateProtocol` 严格校验（只接受三个标准常量）。

### 2.1 OpenAIClient 实现要点

- 默认超时 5 分钟，最大重试 5 次（应对 429 限流和临时网络错误）
- 使用 `ChatCompletionAccumulator` 处理流式响应，增量累积避免内存峰值
- 自动提取 o 系列模型的 `reasoning_content`（推理过程），用于调试但不送入上下文

### 2.2 AnthropicClient 实现要点

- **URL 自动补全**：自动为 BaseURL 补全 `/v1/messages`
- **cache_control ephemeral**：自动为系统提示设置 prompt caching，系统提示缓存 5 分钟，成本可降低 50% 以上
- **MaxTokens 默认 8192**
- **Tool 消息合并**：Claude API 要求连续的 `tool` 角色消息合并为单个 `tool_result` block，Client 层自动处理
- **Usage 含 CacheReadInputTokens**：完整记录缓存读取和写入的 Token

### 2.3 三种 Client 实现对比

| 特性 | AnthropicClient | OpenAIClient | OpenAIResponsesClient |
|------|----------------|--------------|----------------------|
| 默认超时 | 5 分钟 | 5 分钟 | 5 分钟 |
| MaxTokens 默认 | 8192 | 不设上限 | 不设上限 |
| Streaming | ✅ | ✅ | ✅ |
| Prompt Caching | ✅ ephemeral | ❌ | ❌ |
| reasoning_content | ❌ | ✅ | ✅ |
| Tool 消息合并 | ✅ | ❌ | ❌ |
| CacheReadInputTokens | ✅ | ❌ | ❌ |

---

## 3. 19 个内置 Provider

OCR 内置 19 个 Provider，其中 17 个使用 OpenAI 协议——OpenAI Chat Completions 已成为事实标准。

| # | Provider 名 | BaseURL | EnvVar (Token) | 协议 |
|---|------------|---------|----------------|------|
| 1 | `anthropic` | `https://api.anthropic.com` | `ANTHROPIC_API_KEY` | anthropic |
| 2 | `openai` | `https://api.openai.com` | `OPENAI_API_KEY` | openai |
| 3 | `edenai` | `https://api.edenai.run/v1` | `EDENAI_API_KEY` | openai |
| 4 | `dashscope` | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `DASHSCOPE_API_KEY` | openai |
| 5 | `dashscope-tokenplan` | 同上 | `DASHSCOPE_API_KEY` | openai |
| 6 | `volcengine` | `https://ark.cn-beijing.volces.com/api/v3` | `VOLCENGINE_API_KEY` | openai |
| 7 | `deepseek` | `https://api.deepseek.com` | `DEEPSEEK_API_KEY` | openai |
| 8 | `tencent-tokenhub` | `https://api.hunyuan.cloud.tencent.com/v1` | `TENCENT_API_KEY` | openai |
| 9 | `hy-tokenplan` | 同上 | `TENCENT_API_KEY` | openai |
| 10 | `iflytek` | `https://spark-api-open.xf-yun.com/v1` | `IFLYTEK_API_KEY` | openai |
| 11 | `kimi` | `https://api.moonshot.cn/v1` | `KIMI_API_KEY` | openai |
| 12 | `z-ai` | `https://api.z.ai/api/paas/v4` | `Z_API_KEY` | openai |
| 13 | `z-ai-coding` | 同上 | `Z_API_KEY` | openai |
| 14 | `mimo` | `https://api.minimax.chat/v1` | `MIMO_API_KEY` | openai |
| 15 | `minimax` | `https://api.minimax.chat/v1` | `MINIMAX_API_KEY` | openai |
| 16 | `baidu-qianfan` | `https://qianfan.baidubce.com/v2` | `BAIDU_API_KEY` | openai |
| 17 | `ollama-cloud` | `https://api.olama.cloud/v1` | `OLLAMA_API_KEY` | openai |
| 18 | `litellm` | `http://localhost:4000/v1` | `LITELLM_API_KEY` | openai |
| 19 | `custom` | 用户指定 | 用户指定 | 用户指定 |

Provider 定义结构：

```go
type Provider struct {
    Name     string
    BaseURL  string
    Protocol string
    EnvVar   string   // Token 环境变量名
    Models   []string // 推荐模型列表
}
```

---

## 4. Endpoint 解析四策略链

OCR 的 Endpoint 解析按优先级尝试四种来源，**首个完整三元组（URL + Token + Model）胜出**：

| 优先级 | 策略 | 来源 | 适用场景 |
|--------|------|------|---------|
| 1 | `tryOCRConfig` | `~/.config/ocr/config.json` | 正式配置 |
| 2 | `tryOCREnv` | `OCR_LLM_*` 环境变量 | CI/CD、临时覆盖 |
| 3 | `tryCCEnv` | `ANTHROPIC_*` 环境变量 | Claude Code 用户零配置复用 |
| 4 | `tryShellRC` | `.zshrc`/`.bashrc` 等 shell 配置 | 本地开发环境 |

### 4.1 8 个 OCR 环境变量

| 环境变量 | 用途 |
|---------|------|
| `OCR_LLM_URL` | LLM API 端点 |
| `OCR_LLM_TOKEN` | 鉴权 Token |
| `OCR_LLM_MODEL` | 默认模型名 |
| `OCR_LLM_PROTOCOL` | 协议（anthropic/openai/openai-responses） |
| `OCR_LLM_MAX_TOKENS` | 最大输出 Token |
| `OCR_LLM_TEMPERATURE` | 采样温度 |
| `OCR_LLM_TIMEOUT` | 请求超时 |
| `OCR_LLM_BASE_URL` | Base URL |

### 4.2 Claude Code 环境变量复用

`tryCCEnv` 让 Claude Code 用户"零配置"使用 OCR——只要设置了 `ANTHROPIC_BASE_URL`、`ANTHROPIC_AUTH_TOKEN`、`ANTHROPIC_MODEL`，OCR 自动复用并自动补全 `/v1/messages` 路径。

### 4.3 Shell 配置文件读取

`tryShellRC` 依次读取 `~/.zshrc`、`~/.bashrc`、`~/.bash_profile`、`~/.profile`，提取 `ANTHROPIC_*` 环境变量定义。这让非交互式进程（如 cron、CI）也能自动发现配置。

---

## 5. 自定义 Provider

当 19 个内置 Provider 不够用时，支持自定义 Provider：

```json
{
  "providers": {
    "my-local-llm": {
      "url": "http://localhost:11434/v1",
      "protocol": "openai",
      "model": "llama3"
    }
  }
}
```

```bash
ocr review --provider my-local-llm
```

**关键规则**：
- 必须提供 `url` 和 `protocol`
- Token 可选（自部署场景如 Ollama 无需鉴权）
- 自定义 Provider 不参与 Endpoint 解析链，需通过 `--provider` 显式指定

---

## 6. Token 计数：tiktoken

OCR 使用 tiktoken 进行 Token 计数，用于预算控制和压缩触发：

```go
func CountTokens(model, text string) int {
    encoding := getEncoding(model)
    return len(encoding.Encode(text))
}
```

| Encoding | 适用模型 | 词表大小 |
|----------|---------|---------|
| `cl100k_base` | GPT-4/GPT-4o/Claude 等 | ~100k |
| `o200k_base` | o1/o3/o4 推理模型 | ~200k |

推理模型（模型名以 `o1`、`o3`、`o4` 开头）自动使用 `o200k_base`，其他使用 `cl100k_base`。

Token 计数的四个用途：预算前瞻（估算 Subtask 成本）、压缩触发（计算上下文占用）、Manifest 记录（实际 Token 消耗）、上下文限制（防止超出模型窗口）。

---

## 7. extra_body 和 extra_headers

OCR 支持通过 `extra_body` 和 `extra_headers` 传递厂商特有参数：

```json
{
  "llm": {
    "extra_body": {
      "thinking": { "type": "enabled", "budget_tokens": 10000 }
    },
    "extra_headers": {
      "X-Custom-Header": "value"
    }
  }
}
```

### 7.1 保留头拒绝列表

以下 HTTP 头由 OCR 自动管理，用户配置会被拒绝：

| 保留头 | 拒绝理由 |
|--------|---------|
| `authorization` | 鉴权由 Token 字段统一管理 |
| `x-api-key` | Anthropic 鉴权头 |
| `content-type` | 由协议决定 |
| `user-agent` | 用于 OCR 自身标识 |

---

## 8. 配置方式对比

| 方式 | 持久性 | 适用场景 | 优先级 |
|------|--------|---------|--------|
| `ocr config provider`（交互式 TUI） | 持久 | 首次配置 | 1（config.json） |
| `ocr config set`（命令行） | 持久 | 脚本化配置 | 1（config.json） |
| `OCR_LLM_*` 环境变量 | 临时 | CI/CD、临时切换 | 2（覆盖 config.json） |

---

## 9. 源码索引

| 模块 | 文件路径 | 核心符号 |
|------|---------|---------|
| LLMClient 接口 | `internal/llm/client.go` | `LLMClient`, `CompletionsWithCtx` |
| 协议定义 | `internal/llm/protocol.go` | `ProtocolAnthropic`, `NormalizeProtocol`, `ValidateProtocol` |
| 工厂函数 | `internal/llm/factory.go` | `NewLLMClient` |
| OpenAI Client | `internal/llm/openai_client.go` | `OpenAIClient` |
| Anthropic Client | `internal/llm/anthropic_client.go` | `AnthropicClient` |
| Provider 列表 | `internal/llm/providers.go` | `BuiltinProviders`, 19 个 Provider |
| Endpoint 解析 | `internal/llm/resolver.go` | `tryOCRConfig`, `tryOCREnv`, `tryCCEnv`, `tryShellRC` |
| Token 计数 | `internal/llm/tokens.go` | `CountTokens`, `getEncoding` |
| 头部校验 | `internal/llm/headers.go` | `reservedHeaders`, `validateHeaders` |
