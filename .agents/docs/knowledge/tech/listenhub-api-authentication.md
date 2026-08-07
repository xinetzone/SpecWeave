---
id: listenhub-api-authentication
title: ListenHub API 规范——Authentication（认证与基础 URL）
category: tech
tags: ["listenhub", "api", "authentication", "security", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 ListenHub 开放平台的统一认证规范：环境变量 LISTENHUB_API_KEY、基础 URL、必备请求头（Authorization/Content-Type/X-Source）、curl 模板与安全注意事项。所有 Key 均以占位符表示。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub API 规范——Authentication

所有 ListenHub API 调用都要求有效的 API Key。本条目沉淀统一认证规范，供全部技能（tts/podcast/image-gen/content-parser/explainer）共享。

## API Key

**环境变量：** `LISTENHUB_API_KEY`（以 `lh_sk_` 开头）。

- 存储位置：macOS `~/.zshrc`、Linux `~/.bashrc`（`export LISTENHUB_API_KEY="<API_KEY>"`），改后 `source` 生效。
- 获取方式：在 https://listenhub.ai/settings/api-keys 获取（需 Pro 订阅）。
- 格式校验：必须以 `lh_sk_` 开头，否则重新提示。
- 缺失时的交互式配置：引导用户获取 → AskUserQuestion 收集 → 校验格式 → 写入 shell profile → 继续后续流程（不要求用户重跑）。

## 基础 URL

| 服务 | 基础 URL |
|------|----------|
| ListenHub API | `https://api.marswave.ai/openapi/v1` |
| 图片生成 | `https://api.marswave.ai/openapi/v1` |
| Staging | `https://staging-api.marswave.ai/openapi/v1` |

## 必备请求头

每次请求必须包含：

```
Authorization: Bearer $LISTENHUB_API_KEY
Content-Type: application/json
X-Source: skills
```

`X-Source: skills` 标识请求来自 CLI 技能（区别于 web/openapi 等来源），服务端据此区分流量。

## curl 模板

```bash
curl -sS -X POST "https://api.marswave.ai/openapi/v1/{endpoint}" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  -d '{ ... }'
```

GET 请求省略 `-d`，并把 `-X POST` 改为 `-X GET`。

## 安全注意事项

- 永远不要在输出中记录或展示完整 API Key（本文档一律使用占位符 `$LISTENHUB_API_KEY` / `<API_KEY>`）。
- API Key 仅通过 HTTPS 传输。
- 不要把敏感或机密信息作为内容输入——它会发送到外部 API 处理。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：记录认证环境变量、基础 URL、必备请求头与安全注意事项 |
