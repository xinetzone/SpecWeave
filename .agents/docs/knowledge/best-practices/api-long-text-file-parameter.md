---
id: "api-long-text-file-parameter"
title: "用 @file 传长文本请求体"
category: "best-practices"
tags: ["API", "curl", "长文本", "@file", "临时文件", "shell参数限制"]
date: "2026-08-07"
last_updated: "2026-08-07"
status: "stable"
author: "SpecWeave"
summary: "当请求体文本过长（如整篇文章）时，用 curl 的 -d @file 从临时文件读取请求体，绕过 shell 命令行参数长度限制。含何时使用、临时文件写法与用后清理。"
security_level: "public"
knowledge_type: "procedural"
validation_status: "verified"
reuse_count: 0
integrity: "unchecked"
---

# 用 `@file` 传长文本请求体

> 当请求体中的文本内容很长（例如整篇文章作为 `sources`），直接内联在 `-d '{...}'` 中可能撞上 shell 命令行参数长度限制。此时用 `@file` 让 curl 从临时文件读取请求体，可完全绕过 shell 参数限制。来源为 ListenHub 系列 skill 的共享实现。

**沉淀来源**：`chaos/flexloop/.agents/skills/shared/common-patterns.md`

---

## 一、何时使用 `@file`

- **文本内容超过几 KB 时**始终使用该方式（安全阈值）。
- 典型场景：`sources` 里放整篇文章、长播报稿、长 prompt。
- `@` 前缀告诉 curl 从文件读取请求体，**完全绕过 shell 参数长度限制**。

**反例（不推荐）**：短文本、仅 `query`/少量字段时，可直接内联 `-d '{...}'`，无需建临时文件。

---

## 二、临时文件写法

把请求 JSON 写入临时文件，再用 `@` 引用：

```bash
# 将请求 JSON 写入临时文件
cat > /tmp/lh-request.json << 'ENDJSON'
{
  "sources": [{"type": "text", "content": "Very long text content goes here..."}],
  "speakers": [{"speakerId": "cozy-man-english"}],
  "language": "en"
}
ENDJSON

# 用 @ 引用文件
curl -sS -X POST "https://api.example.com/openapi/v1/podcast/episodes" \
  -H "Authorization: Bearer $LISTENHUB_API_KEY" \
  -H "Content-Type: application/json" \
  -H "X-Source: skills" \
  -d @/tmp/lh-request.json
```

**注意**：`<< 'ENDJSON'`（带引号）表示 here-doc 内不做变量展开，避免 JSON 内容被 shell 误解。

---

## 三、用后清理

请求完成后删除临时文件，避免残留：

```bash
rm /tmp/lh-request.json
```

---

## 四、变更历史

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-08-07 | 初始版本：沉淀 @file 传长文本请求体模式（适用场景、临时文件写法、用后清理） |
