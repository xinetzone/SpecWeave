---
id: listenhub-api-image
title: ListenHub API 规范——Image Generation（AI 图片生成）
category: tech
tags: ["listenhub", "api", "image-gen", "image-generation", "gemini", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 ListenHub AI 图片生成接口规范：POST /images/generation，记录请求参数（provider/prompt/model/imageConfig/referenceImages）、宽高比表、参考图 URL/base64 两种格式、同步 base64 返回与调用要点。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub API 规范——Image Generation

基础 URL：`https://api.marswave.ai/openapi/v1`；认证见 [listenhub-api-authentication.md](listenhub-api-authentication.md)。本条目为 `image-gen` 技能使用的图片生成接口。

## POST /images/generation

文本生成 AI 图片，**同步**返回 base64 编码的图片数据（无需轮询）。

**请求参数：**

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `provider` | 是 | string | 模型提供方，使用 `"google"` |
| `prompt` | 是 | string | 图片描述（建议英文） |
| `model` | 否 | string | `"gemini-3-pro-image-preview"`（默认）或 `"gemini-3.1-flash-image-preview"` |
| `imageConfig` | 否 | object | 尺寸与宽高比配置 |
| `imageConfig.imageSize` | 否 | string | `"1K"` / `"2K"`（默认）/ `"4K"` |
| `imageConfig.aspectRatio` | 否 | string | `"1:1"`（默认），见下表 |
| `referenceImages` | 否 | array | 至多 14 张参考图（见格式） |

**宽高比：**

| 比例 | 说明 | 模型 |
|------|------|------|
| 1:1 | 方形 | 全部 |
| 2:3 / 3:2 / 3:4 / 4:3 / 9:16 / 16:9 / 21:9 | 常见横竖/海报/超宽 | 全部 |
| 1:4 / 4:1 / 1:8 / 8:1 | 极端窄/宽、全景 | 仅 `gemini-3.1-flash-image-preview` |

**参考图格式：** 每项必须含 `fileData`（URL）或 `inlineData`（base64）之一（不能同时），可在同一数组内混用：

```json
{ "fileData": { "fileUri": "https://example.com/photo.png", "mimeType": "image/png" } }
{ "inlineData": { "data": "<base64-encoded>", "mimeType": "image/png" } }
```

- URL 模式按后缀推断 mimeType：`.jpg/.jpeg`→`image/jpeg`、`.png`→`image/png`、`.webp`→`image/webp`、`.gif`→`image/gif`。
- base64 模式支持 mimeType：`image/png`、`image/jpeg`、`image/webp`、`image/heic`、`image/heif`。
- 本地文件 base64 编码：macOS `base64 -i file`；Linux `base64 -w 0 file`。

**curl 示例（纯文本）：**

```bash
RESPONSE=$(curl -sS -X POST "https://api.marswave.ai/openapi/v1/images/generation" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  --max-time 600 \
  -d '{"provider":"google","model":"gemini-3-pro-image-preview","prompt":"cyberpunk city at night","imageConfig":{"imageSize":"2K","aspectRatio":"16:9"}}')
```

**响应：** `candidates[0].content.parts[0].inlineData.data` 为 base64 图片数据，提取方式：

```bash
BASE64_DATA=$(echo "$RESPONSE" | jq -r '.candidates[0].content.parts[0].inlineData.data // .data')
```

## 调用要点

- 必须使用 `--max-time 600`（生成最长可达 10 分钟）。
- **限流重试**：429 时等 15s 重试，最多 3 次（指数退避）。
- 解码 base64：Linux `base64 -d`；macOS `base64 -D`（或 `--decode`）。
- 输出模式：`inline`/`both` 解码到临时文件后用 Read 工具对话内展示；`download`/`both` 保存到 `.listenhub/image-gen/{YYYY-MM-DD}-{jobId}/`。
- 提示词处理：短 prompt（<10 词）可主动提供润色；长/结构化 prompt 或用户要求原样时不得修改。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：记录图片生成接口参数、宽高比表、参考图两种格式与调用要点 |
