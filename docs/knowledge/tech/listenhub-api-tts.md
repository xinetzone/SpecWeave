---
id: listenhub-api-tts
title: ListenHub API 规范——TTS / Speech（文本转语音）
category: tech
tags: ["listenhub", "api", "tts", "speech", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 ListenHub 文本转语音（TTS）两套接口规范：/v1/tts（单声、低延迟、同步 MP3 流）与 /v1/speech（多角色脚本转音频），记录接口用途、关键参数与调用要点。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub API 规范——TTS / Speech

基础 URL：`https://api.marswave.ai/openapi/v1`；认证见 [listenhub-api-authentication.md](listenhub-api-authentication.md)。本条目为 `tts` 技能使用的文本转语音接口，含两种调用路径。

## 概述

| 接口 | 路径 | 用途 | 返回方式 |
|------|------|------|----------|
| Quick 模式 | `POST /v1/tts` | 单声、低延迟、即兴朗读/阅读片段 | 同步二进制 MP3 流（非 JSON） |
| Script 模式 | `POST /v1/speech` | 多角色、每段指定声音（对话/有声书/脚本化内容） | 同步返回音频 URL |

## POST /v1/tts（Quick 模式）

低延迟单声 TTS，返回**流式二进制 MP3**（非 JSON）。

**请求参数：**

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `input` | 是 | string | 待转换文本 |
| `voice` | 是 | string | 主播 ID（`speakerId`，来自 `/speakers/list`） |
| `model` | 否 | string | 模型名，默认 `flowtts` |

**curl 示例：**

```bash
curl -sS -X POST "https://api.marswave.ai/openapi/v1/tts" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  -d '{"input":"Hello","voice":"EN-Man-General-01"}' \
  --output /tmp/tts-output.mp3
```

**调用要点：**
- 响应为二进制 MP3 流；出错时回退为 JSON 错误对象（先检查 HTTP 状态码）。
- `input` 最大约 10,000 字符。
- `voice` 必须是有效的 `speakerId`，禁止硬编码——无用户偏好时用内置默认主播兜底（见 [listenhub-api-speakers.md](listenhub-api-speakers.md)）。
- 同步返回无 `audioUrl`；`inline` 输出模式将音频写入临时文件后用 Read 工具展示。

## POST /v1/speech（Script 模式）

多角色脚本转音频，每段脚本用不同声音，同步返回音频 URL。

**请求参数：**

| 字段 | 必填 | 类型 | 说明 |
|------|------|------|------|
| `scripts` | 是 | array | 有序脚本段数组 |
| `scripts[].content` | 是 | string | 该段文本 |
| `scripts[].speakerId` | 是 | string | 该段主播 ID |
| `title` | 否 | string | 自定义标题（缺省自动生成） |

**响应字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `audioUrl` | string | MP3 音频文件 URL |
| `audioDuration` | integer | 时长（毫秒） |
| `subtitlesUrl` | string | SRT 字幕文件 URL |
| `taskId` | string | 任务标识 |
| `credits` | integer | 消耗积分 |

**调用要点：**
- 长脚本建议将请求体写入临时文件后用 `-d @/tmp/...` 提交（见总览「@file 长文本输入」）。
- 多角色配音时按脚本唯一角色顺序分配声音；无用户偏好时用内置默认（Primary 给首个角色、Secondary 给第二角色）。
- 输出模式：`inline`/`both` 展示 `audioUrl`、`subtitlesUrl` 为可点击链接；`download`/`both` 按主题 slug 命名下载到当前工作目录（去重）。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：记录 /v1/tts 与 /v1/speech 的用途、参数与调用要点 |
