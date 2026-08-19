---
id: "deepseek-v4-api-free-tier"
title: "02 API新用户免费额度详解"
version: "1.0"
source: "platform.deepseek.com + api-docs.deepseek.com + costgoat.com + 51CTO实测 + gitcode实战教程"
type: "Wiki Document"
description: "DeepSeek API新用户500万tokens免费额度的完整说明：领取方式、有效期、适用模型、消耗估算"
tags: ["DeepSeek", "API", "免费额度", "500万tokens", "开发者", "platform.deepseek.com"]
category: "learning/07-vendor-product-learning"
date: "2026-08-19"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "注册DeepSeek开发者平台即赠500万tokens（无需信用卡），有效期约30天，覆盖V4-Pro和V4-Flash所有API功能，足够独立开发者做2-4周原型验证。"
last_verified: "2026-08-19"
---

# 02 API新用户免费额度详解

## 2.1 免费额度概览

| 项目 | 详情 |
|------|------|
| **赠送额度** | 500万tokens（输入+输出合计） |
| **注册条件** | 邮箱注册 + 手机号验证 |
| **信用卡要求** | ❌ 不需要 |
| **有效期** | 约30天（以控制台Billing页面显示为准） |
| **适用模型** | deepseek-v4-pro、deepseek-v4-flash |
| **可用功能** | Chat Completions、Responses API、Anthropic API、Tool Calls、JSON Output、FIM补全等全部API功能 |
| **到账方式** | 注册后自动到账，无需手动领取 |
| **扣费优先级** | 赠送余额优先消耗，用完后使用充值余额 |

> **注意**：网上流传的"每日50次API调用+每月100万tokens免费额度"是不实信息。实际为**一次性赠送500万tokens**，有效期约30天，无每日调用次数限制（受并发限制约束）。

## 2.2 注册与领取流程（约3分钟）

1. 打开 [platform.deepseek.com](https://platform.deepseek.com)
2. 点击「Sign Up」注册账号
   - 支持邮箱注册
   - 需要手机号验证（+86中国手机号可用）
3. 登录后进入 Dashboard
4. 左侧菜单进入「API Keys」页面
5. 点击「Create API Key」生成密钥（格式：`sk-...`）
6. 进入「Usage / Billing」页面，可看到500万免费余额已到账

**不需要邀请码，不需要绑定信用卡，注册即送。**

## 2.3 API接入配置

### OpenAI兼容格式（推荐）

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-api-key-here",
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-v4-pro",  # 或 deepseek-v4-flash
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "你好，请介绍一下自己"}
    ],
    # 可选：开启思考模式
    # extra_body={"thinking": "high"}  # 或 "max"
)

print(response.choices[0].message.content)
```

### Anthropic兼容格式

```python
import anthropic

client = anthropic.Anthropic(
    api_key="sk-your-api-key-here",
    base_url="https://api.deepseek.com"
)

message = client.messages.create(
    model="deepseek-v4-pro",
    max_tokens=4096,
    messages=[{"role": "user", "content": "你好"}]
)
print(message.content[0].text)
```

## 2.4 500万tokens能做什么？

tokens是模型处理文本的基本单位。1个token约等于0.75个中文字，或0.3个英文单词。

| 任务类型 | 典型输入tokens | 典型输出tokens | 500万能调用约多少次 |
|---------|--------------|--------------|-------------------|
| 短对话问答 | 300 | 200 | ~10,000次 |
| 代码生成/补全 | 500 | 400 | ~5,500次 |
| 文档摘要（短文档） | 2,000 | 500 | ~2,000次 |
| 内容写作（短文） | 200 | 1,000 | ~4,000次 |
| 数据抽取/分类 | 1,000 | 300 | ~3,800次 |
| RAG知识库问答 | 3,000 | 500 | ~1,400次 |
| 长文档分析（10万字） | 150,000 | 2,000 | ~33次 |
| Agent复杂任务（多轮） | 10,000 | 5,000 | ~330次 |

**实际使用经验参考**：
- 独立开发者做原型：约 **2-4周**
- 3-5人小团队并发实验：约 **1-2周**
- 持续CI测试每天跑：约 **3-7天**

> **Token消耗陷阱**：如果不设置`max_tokens`限制输出长度，模型可能生成非常长的回答，快速消耗额度。建议根据场景设置合理的max_tokens。

## 2.5 免费阶段限制

### 并发限制

| 模型 | 并发上限 |
|------|---------|
| deepseek-v4-pro | 500 |
| deepseek-v4-flash | 2500 |

并发限制以账号为粒度，与API Key数量无关。超出并发会收到HTTP 429错误。

如需更高并发，可提交[扩容申请工单](https://trtgsjkv6r.feishu.cn/share/base/form/shrcnda9jNKvhyYr8xb843xLEzc)，扩容不额外收费。

### 其他说明

- 免费阶段与付费阶段享有相同的并发限制
- 免费阶段支持所有API功能（Tool Calls、JSON Output、思考模式等）
- 无每日调用次数限制（受并发限制约束）
- 支持流式响应（Streaming SSE）

## 2.6 额度用完后怎么办？

1. **不充值**：赠送余额用完且无充值余额时，API调用返回错误，不会自动扣费
2. **充值继续使用**：在Billing页面充值，支持信用卡和PayPal
3. **切换到网页版**：网页/App继续免费使用，不受API额度影响

> **充值余额永久有效**，充值后按实际用量从余额扣费。建议按需充值，避免大额预存。

## 2.7 省Token技巧

1. **优化Prompt**：减少不必要的system prompt长度
2. **设置max_tokens**：避免输出过长
3. **利用缓存**：相同前缀的请求自动命中缓存，缓存命中输入价格极低（峰谷时0.05-0.30元/百万tokens vs 未命中1.5-9元/百万tokens）
4. **选对模型**：简单任务用V4-Flash，复杂推理才用V4-Pro
5. **错峰调用**：空闲时段价格减半（详见[03 API定价](03-api-pricing-comparison.md)）
6. **善用思考模式**：不是所有任务都需要Think Max，简单问题关闭思考模式可节省输出tokens
