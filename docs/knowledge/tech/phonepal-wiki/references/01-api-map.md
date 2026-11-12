---
type: Reference
title: "关键类型与签名索引（可 Grep 核验）"
description: "PhonePal 快照中 40 余个核心类型、方法签名与常量的位置索引，按模块分组，正文引用 API 时可回到本表核对存在性与行号"
tags: [phonepal, api-map, kotlin, signatures, reference]
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
    resource: ./00-source-inventory.md
    title: 信源登记（commit 与路径口径）
---

# 关键类型与签名索引

本表只收录正文会引用的类型、方法与常量。路径相对仓库根，行号对应 commit `580fdf7`。表中每一项都在源码中存在，可作为「无虚构 API」的对照表。

## 1. core-api（契约层）

| 类型 / 成员 | 签名或取值 | 位置 |
|---|---|---|
| `AgentEvent` | sealed class，10 个子类型 | `core-api/.../api/Agent.kt:4-28` |
| `AgentConfig` | `maxSteps=30, stuckRepeats=3, historyWindow=8, maxNodes=120, learnFromSuccess=true` | `core-api/.../api/Agent.kt:39-49` |
| `Agent` | `suspend fun handle(userMessage, listener, stop)` / `suspend fun runPhoneTask(goal, skillName, listener, stop): PhoneTaskFinished` | `core-api/.../api/Agent.kt:56-62` |
| `StopSignal` | `val stopped: Boolean` | `core-api/.../api/Agent.kt:52-54` |
| `UserChannel` | `suspend fun ask(taskId, question, takeover): String` | `core-api/.../api/Agent.kt:35-37` |
| `Point` | `x,y ∈ 0..1000`；`NORM = 1000` | `core-api/.../api/Device.kt:10-19` |
| `UiNode` | `id/text/description/resourceId/className/bounds/clickable/editable/scrollable/focused/password` | `core-api/.../api/Device.kt:28-42` |
| `ScreenState` | `screenshotPng/widthPx/heightPx/packageName/activityName/nodes/secure/capturedAtMillis` | `core-api/.../api/Device.kt:45-59` |
| `ScreenState.fingerprint()` | 包名 + Activity + 节点文本/中心坐标 → 十六进制串 | `core-api/.../api/Device.kt:61-64` |
| `Action` | sealed，11 种：`tap`、`long_press`、`swipe`、`type`、`back`、`home`、`launch`、`deeplink`、`wait`、`ask_user`、`finish` | `core-api/.../api/Device.kt:67-110` |
| `Device` | `observe()` / `perform(action)` / `installedApps()` | `core-api/.../api/Device.kt:118-126` |
| `ModelRole` | `CHAT`、`OPERATOR` | `core-api/.../api/Llm.kt:8` |
| `ModelConfig` | `role/baseUrl/model/apiKey/temperature/maxTokens/timeoutSeconds=120/extraHeaders` | `core-api/.../api/Llm.kt:15-27` |
| `ChatRole` | `SYSTEM/USER/ASSISTANT/TOOL` | `core-api/.../api/Llm.kt:30` |
| `ContentPart` | `Text`、`ImagePng` | `core-api/.../api/Llm.kt:32-35` |
| `ChatRequest` | `messages/tools/jsonMode` | `core-api/.../api/Llm.kt:60-65` |
| `LlmClient` | `val config` / `suspend fun complete(request): ChatResponse` | `core-api/.../api/Llm.kt:79-84` |
| `Note` | `title/permalink/type/tags/extraFrontmatter/body/observations/relations/updatedAtMillis` | `core-api/.../api/Memory.kt:26-39` |
| `MemoryStore` | `write/read/search/appendObservation/delete/list` | `core-api/.../api/Memory.kt:47-64` |
| `Decision` | `Allow(reason)` / `Ask(prompt, reason)` / `Deny(reason)` | `core-api/.../api/Sentinel.kt:14-23` |
| `ApprovalScope` | `ONCE`、`TASK` | `core-api/.../api/Sentinel.kt:25` |
| `AuditRecord` | `timeMillis/taskId/stepIndex/action/decision/approved` | `core-api/.../api/Sentinel.kt:36-43` |
| `Sentinel` | `guard(context, action)` / `authorize(context, action)` | `core-api/.../api/Sentinel.kt:53-61` |
| `Skill` | `name/description/apps/channel/confirmBefore/memoryRefs/deeplinks/instructions/flow/source` | `core-api/.../api/Skills.kt:21-34` |
| `SkillChannel` | 6 值：`api/cli/deeplink/gui/deeplink-then-gui/mixed` | `core-api/.../api/Skills.kt:36-42` |
| `FlowStep` | 8 种：`Launch/Deeplink/Ai/Confirm/Tap/Type/Wait/Assert` | `core-api/.../api/Skills.kt:58-69` |

## 2. core-agent（编排层）

| 类型 / 成员 | 签名或取值 | 位置 |
|---|---|---|
| `PhonePalAgent` | 构造参数：chat/operator/device/memory/skills/sentinel/users/config/persona/clock/idFactory | `core-agent/.../agent/PhonePalAgent.kt:33-45` |
| `MAX_TOOL_ROUNDS` | `8` | `core-agent/.../agent/PhonePalAgent.kt:193` |
| `HISTORY_LIMIT` | `20` | `core-agent/.../agent/PhonePalAgent.kt:194` |
| `MEMORY_HITS` | `5` | `core-agent/.../agent/PhonePalAgent.kt:195` |
| `HOWTO_TYPE` / `PATH_CATEGORY` | `"howto"` / `"path"` | `core-agent/.../agent/PhonePalAgent.kt:196-197` |
| `howtoPermalink(key)` | `"howto/$key"` | `core-agent/.../agent/PhonePalAgent.kt:200` |
| `OperatorLoop.run` | `(task, subGoal?, constraint?, maxSteps=config.maxSteps): LoopOutcome` | `core-agent/.../agent/OperatorLoop.kt:37-42` |
| `OperatorLoop.execute` | `(task, action, screen?): Executed`（内部经 Sentinel） | `core-agent/.../agent/OperatorLoop.kt:152-173` |
| `OperatorLoop.check` | `(task, expectation): LoopOutcome` | `core-agent/.../agent/OperatorLoop.kt:176-199` |
| `PARSE_FAILURE_LIMIT` | `3` | `core-agent/.../agent/OperatorLoop.kt:239` |
| `AgentTools` | 6 个工具：`memory_search/memory_read/memory_write/memory_forget/list_skills/phone_task` | `core-agent/.../agent/AgentTools.kt:12-66` |
| `ChatTools.execute` | `suspend fun execute(call, taskId, emit): String` | `core-agent/.../agent/ChatTools.kt:32-49` |
| `FlowRunner.run` | `(task, flow): LoopOutcome` | `core-agent/.../agent/FlowRunner.kt:18-44` |
| `FlowRunner.fill` | `(task, template, urlEncode): String` | `core-agent/.../agent/FlowRunner.kt:64-88` |
| `FlowRunner.isYes` | 中文/英文肯定词判定 | `core-agent/.../agent/FlowRunner.kt:97-102` |
| `SINGLE_STEP_TRIES` | `3` | `core-agent/.../agent/FlowRunner.kt:94` |
| `OperatorReplyParser.parse` | `(reply): ParsedReply` | `core-agent/.../agent/OperatorReplyParser.kt:44-64` |
| `typeSynonyms` | 约 50 个别名 → 11 种 Action | `core-agent/.../agent/OperatorReplyParser.kt:30-42` |
| `Prompts` | 所有面向模型的中文文本 | `core-agent/.../agent/Prompts.kt:6-94` |
| `TaskRun` | `steps/path/references/howto/values/launchedPackage/lastPackage` | `core-agent/.../agent/TaskRun.kt:11-36` |

## 3. core-sentinel / core-memory / core-skills

| 类型 / 成员 | 签名或取值 | 位置 |
|---|---|---|
| `PolicySentinel` | `(approvals, audit, launcherPackages=DEFAULT_LAUNCHERS, selfPackage="dev.phonepal.app", extraConfirmWords, clock)` | `core-sentinel/.../sentinel/PolicySentinel.kt:44-51` |
| `PolicySentinel.authorize` | TASK 级批准缓存 + 审计 | `core-sentinel/.../sentinel/PolicySentinel.kt:61-87` |
| `endTask(taskId)` | 清空任务级批准 | `core-sentinel/.../sentinel/PolicySentinel.kt:90-92` |
| `ConfirmWords.BUILT_IN` | 17 个确认词 | `core-sentinel/.../sentinel/ConfirmWords.kt:11-14` |
| `ConfirmWords.longestIn` | 最长命中词 | `core-sentinel/.../sentinel/ConfirmWords.kt:25-26` |
| `DEFAULT_LAUNCHERS` | 12 个启动器包名 | `core-sentinel/.../sentinel/PolicySentinel.kt:223-236` |
| `BasicMemoryFormat.parse` | `(text, permalink, mtime): Note` | `core-memory/.../memory/BasicMemoryFormat.kt:40-57` |
| `BasicMemoryFormat.render` | `(note): String` | `core-memory/.../memory/BasicMemoryFormat.kt:63-72` |
| `MemoryIndex.search` | `(query, limit): List<SearchHit>` | `core-memory/.../memory/MemoryIndex.kt:68-106` |
| BM25 常量 | `K1=1.2, B=0.75, TITLE_BOOST=3.0, TAG_BOOST=2.0` | `core-memory/.../memory/MemoryIndex.kt:121-128` |
| `Tokenizer.WEAK_WEIGHT` | `0.3` | `core-memory/.../memory/Tokenizer.kt:13` |
| `FileMemoryStore` | `(root, clock)`；写入原子替换 | `core-memory/.../memory/FileMemoryStore.kt:25-33` |
| `DirectorySkillRepository` | `(roots: List<File>, io)`；后者覆盖前者 | `core-skills/.../skills/DirectorySkillRepository.kt:25-28` |
| `SkillParser.KEYS` | 7 个键 | `core-skills/.../skills/SkillParser.kt:20` |
| `SkillParser.NAME` | `^[a-z0-9-]+$` | `core-skills/.../skills/SkillParser.kt:18` |
| `FlowParser.STEP_KINDS` | 8 种步骤 | `core-skills/.../skills/FlowParser.kt:19` |
| `FlowParser.MAX_WAIT_MILLIS` | `600_000` | `core-skills/.../skills/FlowParser.kt:17` |
| `YamlDoc` | 保留行号的 YAML 节点访问 | `core-skills/.../skills/Yaml.kt:18-101` |

## 4. core-llm / hands / app

| 类型 / 成员 | 签名或取值 | 位置 |
|---|---|---|
| `OpenAiCompatibleClient` | `(config, http, maxRetries=2, baseDelayMillis=500, sleep)` | `core-llm/.../llm/OpenAiCompatibleClient.kt:48-55` |
| 重试状态码 | `408/409/429/5xx` | `core-llm/.../llm/OpenAiCompatibleClient.kt:242` |
| JSON 模式降级 | 400 + 响应含 `response_format` → 关闭并重发 | `core-llm/.../llm/OpenAiCompatibleClient.kt:79-83` |
| `AccessibilityDevice` | `(serviceProvider, context, maxNodes=200, settleDelayMs=600, overlay)` | `hands/.../hands/AccessibilityDevice.kt:48-54` |
| 截屏节流 / 尝试次数 | `1050 ms` / `3` | `hands/.../hands/AccessibilityDevice.kt:366-367` |
| `NodeCompactor` | `DEFAULT_MAX_NODES=200`、`DEFAULT_MAX_TEXT=200`、`maxDepth=64` | `hands/.../hands/NodeCompactor.kt:41-45,103-105` |
| `Coordinates.normalize/denormalize` | 像素 ↔ 0..1000 | `hands/.../hands/Geometry.kt:21-45` |
| `ScreenshotScaling.DEFAULT_LONG_EDGE` | `1280` | `hands/.../hands/Geometry.kt:50` |
| `ScreenshotScaling.looksAllBlack` | 16×16 采样 | `hands/.../hands/Geometry.kt:66-76` |
| `AppGraph` | 手写依赖容器；memory/skills/traces/bundled-skills 目录 | `app/.../app/AppGraph.kt:39-74` |
| `AgentSession` | 单任务串行；`MAX_ITEMS=500` | `app/.../app/session/AgentSession.kt:57-67,255-257` |
| `TraceFormat` | 8 个固定键 | `app/.../app/trace/TraceFormat.kt:13-17,54-100` |
| `TraceWriter` | `trace.jsonl` / `audit.jsonl` / `step-<n>.png`；密钥掩码 | `app/.../app/trace/TraceWriter.kt:10-17,89-98` |
| `SettingsStore` | 普通偏好 + `EncryptedSharedPreferences` 存 Key | `app/.../app/settings/SettingsStore.kt:75-97` |
| `AppSettings.MAX_STEPS_RANGE` | `1..200` | `app/.../app/settings/AppSettings.kt:47` |

## 5. CLI

| 成员 | 取值 / 位置 |
|---|---|
| 顶层命令 | `lint`、`push`、`run`、`stop`、`logs`、`traces`（`cli/phonepal_cli/main.py:207-232`） |
| `traces` 子命令 | `pull`、`show`（`cli/phonepal_cli/main.py:233-242`） |
| run id 正则 | `^[A-Za-z0-9._-]+$`（`cli/phonepal_cli/main.py:19`） |
| lint 常量 | `CHANNELS`(6)、`KEYS`(7)、`STEP_KINDS`(8)、`MAX_WAIT_MILLIS=600000`（`cli/phonepal_cli/lint.py:18-27`） |
| YAML 子集 | 支持块/流式集合、引号、块标量；不支持锚点/别名/标签（`cli/phonepal_cli/yamlsub.py:1-16`） |
| 调试广播常量 | `ACTION_RUN/ACTION_STOP/ACTION_RELOAD`（`cli/phonepal_cli/adb.py:18-21`） |
| logcat 终止事件 | `PhoneTaskFinished`、`Failed`（`cli/phonepal_cli/logcat.py:16`） |

## 相关概念

- [信源登记](./00-source-inventory.md)
- [对抗审查记录](./02-adversarial-review.md)
- [分层与依赖](../concepts/01-architecture.md)
