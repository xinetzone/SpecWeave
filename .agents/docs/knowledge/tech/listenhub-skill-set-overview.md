---
id: listenhub-skill-set-overview
title: ListenHub 技能集总览——asr/tts/podcast/image-gen/content-parser/explainer 设计模式与共享规范
category: tech
tags: ["listenhub", "skill", "ai-skill", "api-integration", "design-pattern", "marswave"]
date: 2026-08-07
last_updated: 2026-08-07
status: active
author: specweave-archiver
summary: 沉淀 flexloop chaos 技能库中 6 个内容生成类 AI 技能（asr/tts/podcast/image-gen/content-parser/explainer）的触发词、能力定位、API 依赖与共享通用模式（异步轮询/错误处理/@file/交互式参数收集），并说明已废弃的 listenhub 单体技能状态。
security_level: public
knowledge_type: procedural
validation_status: verified
reuse_count: 0
integrity: unchecked
---

# ListenHub 技能集总览

本条目沉淀 flexloop 技能库中 6 个「内容生成 / 内容解析」类 AI 技能的设计模式与能力清单。这些技能统一调用 ListenHub（`api.marswave.ai`）开放平台 API，并共享 `shared/` 目录下的通用模式。技能库已从早期的单一 `listenhub` 单体技能重构为按能力拆分的独立技能。

> 注：本条目只沉淀「模式 / 规范 / 能力清单」，不复制 SKILL.md 整树内容。所有 API Key 一律用占位符（`$LISTENHUB_API_KEY` / `<API_KEY>`）。

## 技能能力总览

| 技能 | Emoji | 触发词（示例） | 能力定位 | 核心 API |
|------|-------|---------------|----------|----------|
| `asr` | 🎙️ | 转录 / transcribe / 语音转文字 / ASR / 识别音频 | 本地离线语音转文字（`coli asr`），无需 API Key；支持中英日韩粤（sensevoice）或仅英文（whisper） | 无（本地 CLI，非 ListenHub API） |
| `tts` | 🔊 | 朗读 / 配音 / TTS / 语音合成 / read aloud | 文本转自然语音。Quick 模式（单声、低延迟、同步 MP3 流）+ Script 模式（多角色、每段指定声音） | `/v1/tts`、`/v1/speech`、`/speakers/list` |
| `podcast` | 🎙️ | 做播客 / podcast / 播客 / 录一期节目 / discuss | 生成 1-2 个 AI 主播的播客节目；支持 quick/deep/debate 模式、one-step/two-step 生成 | `/podcast/episodes`（含文本/音频两段式）、`/speakers/list` |
| `image-gen` | 🖼️ | 生成图片 / 画一张 / AI图 / generate image / 配图 | 文本生成 AI 图片（Labnana/Gemini），支持多分辨率、多宽高比、参考图（URL 或 base64）；同步返回 base64 | `/images/generation` |
| `content-parser` | 🔗 | 解析链接 / 提取内容 / parse this URL / extract content | 从 URL 提取并规范化跨平台内容，返回正文、元数据、引用；可作为生成类技能的预处理 | `/v1/content/extract` |
| `explainer` | 🎬 | 解说视频 / explainer video / tutorial video | 生成解说视频（单主播配音 + AI 视觉）；支持仅文本脚本或文本+视频 | `/storybook/episodes`（含 video 端点）、`/speakers/list` |

### 组合关系（Composability）

- `explainer` 可被内容生成编排类技能（如 content-planner Phase 3）调用。
- `podcast`、`explainer`、`tts` 均调用 `/speakers/list` 获取主播。
- `tts` 可被 `explainer` 用于配音（voiceover）。
- `content-parser` 提取的正文可作为 `podcast` / `tts` 的输入来源。

## 共享通用模式（shared/ 目录）

所有调用 ListenHub API 的技能统一遵循 `shared/` 下的通用模式，是本次沉淀的关键「设计模式」资产：

1. **异步轮询（Async Polling）**：多数生成端点异步执行，采用「前台提交 + 后台轮询」两步法。提交 POST 请求提取 task/episode ID（前台，快），再用 `run_in_background: true` 的 Bash 轮询循环直到完成（后台）。默认间隔 10s（content-parser 为 5s）、最大 30 次、Bash timeout 600000。用 `jq` 解析，禁止 python3/awk。
2. **统一响应结构**：所有响应形如 `{"code":0,"message":"","data":{...}}`；`code:0` 为成功，非零为错误。
3. **错误处理（Error Handling）**：HTTP 状态码（401 无效 key、402 余额不足、429 限流、5xx 服务器错误等）+ 应用错误码（21007 无效 key、25429 限流）。429 等 15s 重试（指数退避）、5xx 重试至多 3 次。
4. **@file 长文本输入**：当 `sources` 内容过长可能超 shell 参数长度限制时，将请求体写入临时文件并用 `-d @/tmp/...` 引用，绕开 shell 参数限制；用后清理。
5. **交互式参数收集（Interactive Parameter Collection）**：枚举参数用 AskUserQuestion 工具逐步提问（一次一问、收集后汇总确认、允许回退）；独立参数（如分辨率+宽高比）可批量问；自由文本（主题/URL/prompt）用普通消息收集。主播选择例外：展示文本表格后用自由文本匹配。
6. **配置模式（Config Pattern）**：每技能在 `.listenhub/{skill}/config.json` 存配置；首次运行「零问题引导」（Zero-Question Boot）静默创建默认配置；API Key 检查前置；配置更新用 `jq '. + {...}'` 合并，不覆盖未改动键。
7. **输出模式（Output Mode）**：`outputMode` 取值 `inline`（默认）/`download`/`both`，控制结果是对话内展示还是保存到当前工作目录（友好主题命名 + 去重）。
8. **主播选择（Speaker Selection）**：提供内置默认主播（zh/en 各主/副），仅当用户明确要求换声音时才拉取 `/speakers/list` 并展示完整列表；禁止在 API 调用中硬编码 speakerId。
9. **硬约束（Hard Constraints / HARD-GATE）**：禁止 shell 脚本（用 curl）；使用生成 API 前必须收集全部参数并获用户确认；一次只问一个问题；不保存到 `~/Downloads/`/`/tmp/` 作为主要产物（image-gen 例外保存到 `.listenhub/image-gen/`）。

## 认证与基础 URL

- 环境变量：`LISTENHUB_API_KEY`（以 `lh_sk_` 开头），在 shell profile 中配置。
- 基础 URL：`https://api.marswave.ai/openapi/v1`（所有端点共用）。
- 必备请求头：`Authorization: Bearer $LISTENHUB_API_KEY`、`Content-Type: application/json`、`X-Source: skills`（标识来自 CLI 技能）。
- 详见 [listenhub-api-authentication.md](listenhub-api-authentication.md)。

## listenhub 已废弃（DEPRECATED）

`listenhub` 单体技能已于 2026-03-04（MARS-3517）拆分为 `podcast` / `explainer` / `tts` / `image-gen` / `content-parser` 五个独立技能。其 `DEPRECATED.md` 明确提示：

- 该技能已过期，应通过 `npx skills add marswaveai/skills` 升级并重启 agent。
- 升级前**不要尝试执行原始任务**。
- 触发词映射：make a podcast → `/podcast`；explainer video → `/explainer`；read aloud/TTS → `/tts`；generate image → `/image-gen`；extract URL → `/content-parser`。
- 共享基础设施（API 参考、认证、通用模式）统一收敛到 `shared/` 目录。

> 本条目与 6 个 API 规范条目（listenhub-api-tts / podcast / image / speakers / storybook / authentication）共同构成该技能集的完整沉淀。

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2026-08-07 | 首次沉淀：创建技能集总览，记录 6 技能能力清单、共享通用模式与 listenhub 废弃状态 |
