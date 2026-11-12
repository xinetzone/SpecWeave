---
type: Concept
title: "模型客户端：OpenAI 兼容层的重试、降级与脱敏"
description: "OpenAiCompatibleClient 如何把统一的 ChatRequest 映射到 /chat/completions：工具调用、JSON 模式、图片 base64、408/409/429/5xx 退避重试、response_format 不支持的自动降级，以及 API Key 的全程脱敏"
tags: [phonepal, llm, openai, retry, json-mode, redaction]
generated:
  by: specweave-agent
  at: "2026-11-12T00:00:00+08:00"
verified:
  by: process:seven-concepts-v
  at: "2026-11-12T00:00:00+08:00"
status: stable
stale_after: "2027-05-12"
sources:
  - id: S-01
    resource: ../references/00-source-inventory.md
    title: 信源登记：PhonePal 源码快照
---

# 模型客户端：OpenAI 兼容层的重试、降级与脱敏

PhonePal 只实现一个模型客户端：任何兼容 `POST /chat/completions` 的服务都能用。它不追求覆盖所有厂商特性，而是把「不稳定」处理干净：超时、限流、服务端不认 JSON 模式、图片编码、密钥泄露。

## 1. 统一的请求模型

上层只认识 `core-api` 里的类型 [F-015]：

```kotlin
data class ChatRequest(
    val messages: List<ChatMessage>,
    val tools: List<ToolSpec> = emptyList(),
    val jsonMode: Boolean = false,
)
```

`ChatMessage` 由 `ChatRole` + `List<ContentPart>` 组成；`ContentPart` 只有 `Text` 与 `ImagePng` 两种；工具调用用 `toolCalls` / `toolCallId` 表达。这样上层不需要知道 OpenAI 的 `content` 数组、`tool_calls` 结构或 base64 细节。

## 2. 请求编码

`buildBody` 做四件事 [F-060]：

| 场景 | 编码 |
|---|---|
| 纯文本消息 | `content` 是字符串 |
| 带图消息 | `content` 是数组：`{"type":"text","text":...}` + `{"type":"image_url","image_url":{"url":"data:image/png;base64,..."}}` |
| assistant + 工具调用 | `content` 为 `null`，`tool_calls` 为 `[{id, type:"function", function:{name, arguments}}]` |
| 工具结果 | `role = "tool"`，带 `tool_call_id` |

`jsonMode = true` 时加 `{"response_format": {"type": "json_object"}}`；`temperature` 与 `max_tokens` 只在配置里给了值时才写 [F-059]。

## 3. 重试：哪些错误值得再试

```kotlin
fun isRetryable(code: Int) = code == 408 || code == 409 || code == 429 || code in 500..599
```

重试参数 [F-058]：

- 最多 `maxRetries = 2` 次（总共最多 3 次请求）；
- 退避从 `baseDelayMillis = 500` 开始，按 2 的幂增长（500 → 1000 → …）；
- 服务端给了 `Retry-After` 就优先用它（秒 × 1000）；
- IO 异常（连接断开、超时）也重试；
- 400、401、403、404 这类不重试，直接抛 `LlmException`。

上层还会再包一层：操作循环的 `completeWithRetry` 对 `LlmException` 再试一次 [F-026]，所以最坏情况是 6 次请求。这是「手机操作任务失败一次代价很高」的取舍。

## 4. JSON 模式降级

并非所有 OpenAI 兼容服务都支持 `response_format`。客户端的处理是 [F-059]：

```text
请求带 response_format
  → 服务端返回 400 且响应体包含 "response_format"
  → 置 jsonModeUnsupported = true，本次立即重发（不带 response_format）
  → 之后该客户端实例的所有请求都不再带 response_format
```

注意它是**按客户端实例记忆**的：聊天模型与操作模型各自独立，一个不支持不会影响另一个。降级后模型仍可能输出非 JSON，所以解析器必须是宽容的 [F-036]。

## 5. 图片与超时

- 截图 PNG 直接 base64 进 `data:` URL，不先上传对象存储 [F-060]；
- `OkHttpClient` 同时设置 `callTimeout` 与 `readTimeout`，默认 120 秒 [F-061]；
- 请求在 `Dispatchers.IO` 上执行，协程取消会 `call.cancel()`，避免「用户点了停止但请求还在跑」。

## 6. 脱敏：三道防线

| 层 | 做法 | 依据 |
|---|---|---|
| `ModelConfig.toString()` | apiKey 固定显示 `***` | [F-014] |
| `OpenAiCompatibleClient.redact` | 抛出前把响应体/异常消息中的 Key 替换为 `***` | [F-061] |
| `TraceWriter.mask` | 写轨迹与日志前，把长度 ≥ 4 的 Key 替换为 `***` | [F-071] |

配置存储也分开：普通设置进普通 SharedPreferences，API Key 只进 `EncryptedSharedPreferences`（AES256_SIV / AES256_GCM）[F-068]。

## 7. 换一个模型供应商要改什么

| 情况 | 工作量 |
|---|---|
| 兼容 OpenAI `/chat/completions` + 工具调用 | 只改设置里的 Base URL、模型名、Key；默认值是火山方舟 [F-079] |
| 兼容但返回结构略有差异 | 改 `parseResponse` 的字段读取（已对 `content` 的字符串/数组/对象三种形态做兼容）[F-060] |
| 不兼容 OpenAI 协议 | 实现 `LlmClient.complete`，在 `AppGraph.agent()` 里替换实现 [F-068] |
| 需要额外请求头 | `ModelConfig.extraHeaders` 已支持 [F-014] |

## 8. 什么时候会看到这些错误

| 现象 | 根因 | 客户端行为 |
|---|---|---|
| 「模型服务暂时不可用（错误码 429）」 | 限流 | 自动重试 2 次后抛出 |
| 「HTTP 400 ... response_format」但不报错 | 服务不支持 JSON 模式 | 自动降级重发，用户无感 |
| 「Malformed response」 | 服务返回非 JSON 或代理页 | 抛 `LlmException`，消息截断到 200 字符 |
| 「Request to ... failed: timeout」 | 网络/服务端慢 | 重试后抛出 |

聊天层收到 `LlmException` 会发 `Failed` 事件并回复「抱歉，模型服务暂时不可用，请稍后再试」[F-037]；操作层则直接中止任务并写轨迹 [F-028]。

## 相关概念

- [一轮聊天：`LlmClient` 的上层用法](02-chat-and-tools.md)
- [操作循环：模型失败如何影响任务](03-operator-loop.md)
- [工程模式：宽容解析与降级](10-engineering-patterns.md)
- [关键类型与签名索引](../references/01-api-map.md)
