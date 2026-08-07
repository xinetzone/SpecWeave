---
id: listenhub-api-podcast
title: ListenHub API 规范——Podcast（播客节目生成）
category: tech
tags: ["listenhub", "api", "podcast", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 ListenHub 播客生成接口规范：POST /podcast/episodes 创建节目、GET /podcast/episodes/{episodeId} 查询状态结果，记录接口用途、关键参数（speakers/query/sources/language/mode）与调用要点（异步轮询、两段式生成）。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub API 规范——Podcast

基础 URL：`https://api.marswave.ai/openapi/v1`；认证见 [listenhub-api-authentication.md](listenhub-api-authentication.md)。本条目为 `podcast` 技能使用的播客生成接口。

## POST /podcast/episodes（创建节目）

创建播客节目，返回 `episodeId` 后异步生成。

**请求参数：**

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `speakers` | **是** | array | 1-2 个主播对象 `[{speakerId:"..."}]`（最多 2 个） |
| `query` | 否 | string | 主题或提示文本 |
| `sources` | 否 | array | 内容来源（见 Sources 格式） |
| `language` | 否 | string | `en` 或 `zh` |
| `mode` | 否 | string | `deep` 或 `quick` |

**Sources 格式：**

```json
[
  {"type":"url","content":"https://example.com/article"},
  {"type":"text","content":"主题描述或参考文本..."}
]
```

**curl 示例：**

```bash
curl -sS -X POST "https://api.marswave.ai/openapi/v1/podcast/episodes" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  -d '{"query":"AI 发展趋势","sources":[{"type":"text","content":"..."}],"speakers":[{"speakerId":"cozy-man-english"}],"language":"en","mode":"deep"}'
```

**响应：** `data.episodeId`（24 字符 hex）。

## GET /podcast/episodes/{episodeId}（查询状态与结果）

**路径参数：** `episodeId`（24 字符 hex）。

**关键响应字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `processStatus` | string | `pending` / `success` / `failed` |
| `audioUrl` | string | 音频直接下载 URL |
| `audioStreamUrl` | string | M3U8 流媒体 URL |
| `scripts` | array | 脚本段（含 speakerId/speakerName/content） |
| `title` | string | 生成的节目标题 |
| `outline` | string | 生成的节目大纲 |
| `cover` | string | 封面图 URL |
| `credits` | integer | 消耗积分 |

## 调用要点

- **异步轮询**：提交后提取 `episodeId`（前台），再用后台轮询循环等待 `processStatus=success`；间隔 10s、最大 30 次、Bash timeout 600000。
- **两段式生成（two-step）**：先 `POST /podcast/episodes/text-content` 生成文本草稿 → 轮询取草稿 → 保存 `draft.md` / `draft.json` 到当前目录并等待用户确认 → 再 `POST /podcast/episodes/{episodeId}/audio`（可传修改后的 `scripts`）→ 再轮询生成音频。
- **一步生成（one-step）**：直接提交全部参数 → 轮询直到完成。
- **输入校验**：最多 2 个主播；`language` 仅 `zh`/`en`；`mode` 仅 `deep`/`quick`。
- **输出**：`inline`/`both` 展示 `audioUrl` 为可点击链接；`download`/`both` 按主题 slug 下载到当前工作目录（去重）。
- 主播必须来自 `/speakers/list`，禁止硬编码 speakerId。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：记录播客创建/查询接口参数与两段式生成调用要点 |
