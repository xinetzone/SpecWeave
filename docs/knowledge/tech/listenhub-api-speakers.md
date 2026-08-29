---
id: listenhub-api-speakers
title: ListenHub API 规范——Speakers（主播列表）
category: tech
tags: ["listenhub", "api", "speakers", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 ListenHub 主播列表接口规范：GET /speakers/list，记录查询参数（language/status）、响应字段（name/speakerId/demoAudioUrl/gender/language）与调用要点；含内置默认主播表。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub API 规范——Speakers

基础 URL：`https://api.marswave.ai/openapi/v1`；认证见 [listenhub-api-authentication.md](listenhub-api-authentication.md)。本条目为 `tts` / `podcast` / `explainer` 技能共享的主播（语音）查询接口。

## GET /speakers/list

获取可用语音主播，可按语言过滤。

**查询参数：**

| 参数 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `language` | 否 | string | 按语言过滤：`zh` 或 `en` |
| `status` | 否 | integer | 主播状态：`1`（active，默认）或 `2` |

**curl 示例：**

```bash
curl -sS "https://api.marswave.ai/openapi/v1/speakers/list?language=en" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "X-Source: skills"
```

**响应字段（`data.items[]`）：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `name` | string | 展示名 |
| `speakerId` | string | 传给创建端点的 ID |
| `demoAudioUrl` | string | 试听音频 URL |
| `gender` | string | `male` 或 `female` |
| `language` | string | `zh` 或 `en` |

## 调用要点

- **内置默认主播**（无用户偏好时的兜底，勿重复询问）：

| 语言 | 角色 | 名称 | 说明 |
|------|------|------|------|
| `zh` | 主（男） | 原野 | 主声 |
| `zh` | 副（女） | 高晴 | 副声 |
| `en` | 主（男） | Mars | 主声 |
| `en` | 副（女） | Mia | 副声 |

  - 单主播：用该语言主声；双主播：主声 + 副声。
  - 先查 `config.defaultSpeakers.{language}`，未设置再用内置默认。
- **禁止硬编码 speakerId**：仅在无用户偏好时用内置默认兜底；用户要求换声音时才调用 `/speakers/list` 拉取并展示完整列表。
- **主播选择交互**：展示 markdown 文本表格（名称/性别/ID），等用户自由文本输入匹配（序号 / 精确 ID / 名称子串）；不用 AskUserQuestion（与其他枚举参数不同）。
- 用户明确选择后，将 `defaultSpeakers.{language}` 持久化到技能配置（`jq` 合并，不覆盖未改动键）。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：记录主播列表接口、内置默认主播表与选择/持久化要点 |
