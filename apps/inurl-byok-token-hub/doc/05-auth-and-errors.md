---
id: "inurl-byok-auth-and-errors"
title: "鉴权与错误语义"
source: "../README.md"
---
# 鉴权与错误语义

> 内容迁移自根 README §5，逐字对齐源文档 F-085 / F-099。

| 场景 | 状态码 | 响应体 |
|---|---|---|
| 用户类接口未带/无效/过期/已撤销令牌 | **401** | `{"error": "unauthorized"}` |
| 管理员类接口越权 | **403** | `{"error": "forbidden"}` |
| 未匹配路由（含随机路径） | **401** | `{"error": "unauthorized"}` |
| 业务错误 | 4xx/5xx | OpenAI 风格 `{"error": {"message","type","code","param"}}` |

统一令牌前缀 `byok_live_`，库内**只存 SHA-256 摘要**，明文仅签发时返回一次。
