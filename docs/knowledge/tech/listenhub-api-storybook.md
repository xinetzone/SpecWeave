---
id: listenhub-api-storybook
title: ListenHub API 规范——Storybook（解说视频/故事本）
category: tech
tags: ["listenhub", "api", "storybook", "explainer", "video", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 ListenHub 解说视频（Storybook）接口规范：POST /v1/storybook/episodes 创建、GET 查询状态结果、POST /v1/storybook/episodes/{episodeId}/video 触发视频生成，记录参数（sources/speakers/language/mode）、mode 取值与调用要点。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub API 规范——Storybook

基础 URL：`https://api.marswave.ai/openapi/v1`；认证见 [listenhub-api-authentication.md](listenhub-api-authentication.md)。本条目为 `explainer` 技能使用的解说视频（故事本）接口。

> 使用方：`/explainer`（mode=`info` 信息展示 / `story` 故事叙述）；`/slides`（mode=`slides` PPT 式演示）。explainer 只能用 `info` 或 `story`，禁止用 `slides`。

## POST /v1/storybook/episodes（创建 episode）

创建故事本 episode，立即返回 `episodeId`，生成异步执行。

**请求参数：**

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `sources` | **是** | array | **恰好 1 个**来源对象 |
| `sources[].type` | **是** | string | `"text"` 或 `"url"` |
| `sources[].content` | **是** | string | 主题文本或 URL |
| `speakers` | **是** | array | **恰好 1 个**主播：`[{"speakerId":"..."}]` |
| `language` | 否 | string | `"en"` 或 `"zh"` |
| `mode` | 否 | string | `"info"`（默认）/ `"story"` / `"slides"` |
| `style` | 否 | string | 视觉风格提示（可选，自由文本） |

**约束：** 恰好 1 个来源；最多 1 个主播。

**curl 示例：**

```bash
curl -sS -X POST "https://api.marswave.ai/openapi/v1/storybook/episodes" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  -d '{"sources":[{"type":"text","content":"..."}],"speakers":[{"speakerId":"cozy-man-english"}],"language":"en","mode":"info"}'
```

**响应：** `data.episodeId`（24 字符 hex）。

## GET /v1/storybook/episodes/{episodeId}（查询状态与结果）

**路径参数：** `episodeId`（24 字符 hex）。

**关键响应字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `processStatus` | string | `"pending"` / `"success"` / `"failed"` |
| `mode` | string | `"info"` / `"story"` / `"slides"` |
| `pages` | array | 页面数组，每页含 `text`、`pageNumber`、`imageUrl`、`audioTimestamp` |
| `audioUrl` | string | 旁白音频 URL |
| `audioDuration` | number | 音频长度（秒） |
| `videoUrl` | string | 视频 URL（未生成时为 null） |
| `videoStatus` | string | `"not_generated"` / `"pending"` / `"success"` / `"failed"` |
| `credits` | integer | 消耗积分 |
| `failCode` | number | 失败时非零 |

## POST /v1/storybook/episodes/{episodeId}/video（触发视频生成）

对已完成（`processStatus=success`）的 episode 触发视频生成，视频由页面图片 + 旁白音频合成。

**路径参数：** `episodeId`（必须 `processStatus=success`）。

**curl 示例：**

```bash
curl -sS -X POST "https://api.marswave.ai/openapi/v1/storybook/episodes/688c9a27348f001e707ba331/video" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "X-Source: skills"
```

**响应：** `data.success: true`。随后轮询 `GET /v1/storybook/episodes/{episodeId}` 等待 `videoStatus=success`，此时 `videoUrl` 即有值。

## 调用要点

- **异步轮询**：文本生成轮询 `processStatus`；视频生成轮询 `videoStatus`（不同字段）。间隔 10s、最大 30 次、Bash timeout 600000。
- **explainer 使用 1 个主播**，主播必须来自 `/speakers/list`，禁止硬编码 speakerId。
- **输出模式**：`inline`/`both` 展示视频 URL + 音频 URL 为可点击链接；`download`/`both` 在 `{slug}-explainer/` 目录保存 `script.md` 与 `audio.mp3`。
- **在线查看**：https://listenhub.ai/app/explainer/{episodeId}
- 估计耗时：仅文本脚本 2-3 分钟；文本+视频 3-5 分钟。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：记录 Storybook 创建/查询/视频触发接口参数与轮询要点 |
