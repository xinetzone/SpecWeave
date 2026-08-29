---
id: "api-async-polling-pattern"
title: "异步生成接口'两段式'轮询模式"
category: "best-practices"
tags: ["API", "异步", "轮询", "后台任务", "curl", "jq", "两段式"]
date: "2026-08-07"
last_updated: "2026-08-07"
status: "stable"
author: "SpecWeave"
summary: "通用异步生成接口的'两段式'调用模式：前台提交任务获取 task/episode ID，后台轮询直到完成。涵盖执行模型、提交/轮询示例脚本、轮询参数表与完成/失败/超时处理。"
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: 0
integrity: "unchecked"
---

# 异步生成接口"两段式"轮询模式

> 大部分生成型接口（播客、故事书、视频等）都是**异步**的：先提交一个任务并得到一个 ID，然后轮询该 ID 的状态直到完成。本条目沉淀这一通用可复用模式，来源为 ListenHub 系列 skill 的共享实现。

**沉淀来源**：`chaos/flexloop/.agents/skills/shared/common-patterns.md` 及 `api-podcast.md`、`api-storybook.md`

---

## 一、执行模型

所有轮询必须在后台执行（Bash `run_in_background: true`），保持终端可响应，不阻塞后续交互。

**两段式核心流程：**

1. **提交（前台）**：POST 创建请求，从响应中提取 `task`/`episode` ID。此步骤快速，在前台执行。
2. **轮询（后台）**：以 `run_in_background: true` 运行轮询循环。完成后自动收到通知——**不要手动 sleep 或轮询**。

```
POST /{resource}/episodes   →  得到 episodeId
        │
        ▼
GET  /{resource}/episodes/{episodeId}   ← 后台循环轮询 processStatus
        │
        ├── success/completed → 返回结果
        ├── failed/error     → 报告失败
        └── 超时              → 报告超时
```

---

## 二、步骤 1：提交（前台）

```bash
RESPONSE=$(curl -sS -X POST "https://api.example.com/openapi/v1/podcast/episodes" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  -d '{ ... }')

EPISODE_ID=$(echo "$RESPONSE" | jq -r '.data.episodeId')
echo "Submitted: $EPISODE_ID"
```

提交返回后，告知用户任务已提交，轮询将在后台运行。

---

## 三、步骤 2：轮询（后台）

作为**独立的 Bash 调用**，以 `run_in_background: true` 运行：

```bash
# 轮询直到完成——后台运行
EPISODE_ID="<id-from-step-1>"
for i in $(seq 1 30); do
  RESULT=$(curl -sS "https://api.example.com/openapi/v1/podcast/episodes/$EPISODE_ID" \
    -H "Authorization: Bearer $LISTENHUB_API_KEY" \
    -H "X-Source: skills" 2>/dev/null)

  STATUS=$(echo "$RESULT" | tr -d '\000-\037\177' | jq -r '.data.processStatus // "pending"')

  case "$STATUS" in
    success|completed) echo "$RESULT"; exit 0 ;;
    failed|error) echo "FAILED: $RESULT" >&2; exit 1 ;;
    *) sleep 10 ;;
  esac
done
echo "TIMEOUT" >&2; exit 2
```

> 说明：`tr -d '\000-\037\177'` 用于剔除响应中可能混入的控制字符，保证 `jq` 能正常解析。

---

## 四、轮询参数表

| 参数 | 默认值 | 说明 |
|------|--------|------|
| 间隔 (Interval) | 10s | 仅 content-parser 用 5s |
| 最大轮询次数 (Max polls) | 30 | 10s 间隔下约等于 300s 超时 |
| Bash 超时 (Timeout) | 600000 | 在 Bash 工具调用上设置 `timeout: 600000` |

**关键点**：间隔、最大次数与超时三者需联动设置——默认 10s × 30 次 ≈ 300s；后台 Bash 调用超时放宽到 600000ms，避免轮询循环被工具超时打断。

---

## 五、完成 / 失败 / 超时处理

| 结果 | 处理方式 |
|------|----------|
| **成功** (`success`/`completed`) | 后台任务结束时收到包含完整结果的通知；解析结果并呈现给用户 |
| **失败** (`failed`/`error`) | 将错误（含原始响应）输出到 stderr 并退出码 1；向用户报告失败原因 |
| **超时** | 输出 `TIMEOUT` 到 stderr 并退出码 2；告知用户任务超时，可提示重新提交或检查服务状态 |

**注意事项：**

- 完成后**不要立即**把音频/图片 URL 当成本地文件——先按各自输出模式（inline/download/both）处理。
- 状态字段 `processStatus` 取值通常为 `pending` / `success` / `failed`。
- 部分接口还有二级状态（如视频的 `videoStatus`），提交二级任务后需继续轮询直到该状态为 `success`。

---

## 六、变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-08-07 | 初始版本：沉淀异步接口两段式轮询模式（执行模型、提交/轮询脚本、参数表、完成/失败/超时处理） |
