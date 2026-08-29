---
id: "open-code-review-wiki-15"
title: "会话持久化与遥测"
source: "https://open-codereview.ai/docs/telemetry"
x-toml-ref: "../../../../../../../.meta/toml/.agents/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/15-session-telemetry.toml"
---
# 会话持久化与遥测

> 本章深入解析 OCR 的会话持久化、Manifest 系统、会话恢复、评论查询、OpenTelemetry 集成与内嵌查看器。目标章节中未涉及会话日志、Manifest 和遥测的技术细节，本章提供完整参考。

---

## 1. 会话持久化：JSONL 日志

每次 `ocr review` 运行都会在 `~/.opencodereview/sessions/` 下创建一个会话目录，以 `<repo-hash>-<timestamp>-<random>` 命名。

### 1.1 目录结构

```
~/.opencodereview/sessions/
└── a1b2c3d4-20260702-153000-xyz/
    ├── manifest.json          # 会话元数据
    ├── events.jsonl           # 逐事件日志
    ├── plan.json              # Plan 阶段输出
    ├── comments.json          # 收集的评论
    └── files/
        ├── src-foo.go.json    # 每文件审查结果
        └── src-bar.go.json
```

### 1.2 events.jsonl 格式

每个事件是一行 JSON，包含事件类型、时间戳和载荷：

```json
{"type":"session_start","ts":"2026-07-02T15:30:00Z","data":{"repo":"/path/to/repo","mode":"range"}}
{"type":"file_start","ts":"...","data":{"path":"src/foo.go"}}
{"type":"tool_call","ts":"...","data":{"file":"src/foo.go","tool":"file_read","args":{"path":"src/foo.go"}}}
{"type":"tool_result","ts":"...","data":{"file":"src/foo.go","tool":"file_read","status":"success"}}
{"type":"comment","ts":"...","data":{"file":"src/foo.go","comment":{...}}}
{"type":"file_done","ts":"...","data":{"path":"src/foo.go","status":"success","tokens":1234}}
{"type":"session_done","ts":"...","data":{"files":9,"comments":1,"total_tokens":21344}}
```

| 事件类型 | 触发时机 |
|---------|---------|
| `session_start` | 评审开始 |
| `file_start` | 开始审查某文件 |
| `tool_call` | Agent 调用工具 |
| `tool_result` | 工具返回结果 |
| `comment` | Agent 提交评论 |
| `file_done` | 文件审查完成 |
| `file_failed` | 文件审查失败 |
| `compression` | 上下文压缩触发 |
| `session_done` | 评审全部完成 |

---

## 2. Manifest 系统

`manifest.json` 是会话的不可变元数据快照，在会话开始时创建，记录运行时的完整上下文。

### 2.1 Manifest 字段

```json
{
  "id": "a1b2c3d4-20260702-153000-xyz",
  "created_at": "2026-07-02T15:30:00Z",
  "repo": "/path/to/repo",
  "mode": "range",
  "from": "main",
  "to": "feature",
  "commit": null,
  "llm": {
    "provider": "anthropic",
    "model": "claude-opus-4-6",
    "protocol": "anthropic"
  },
  "config": {
    "concurrency": 8,
    "timeout_minutes": 10,
    "max_tools": 30,
    "max_git_procs": 16
  },
  "files_total": 12,
  "files_reviewed": 9,
  "files_skipped": 3,
  "skipped_reasons": {
    "binary": 1,
    "unsupported_ext": 1,
    "default_exclude": 1
  },
  "tools": ["task_done", "code_comment", "file_read", "file_read_diff", "file_find", "code_search"],
  "rules_source": "project",
  "version": "0.14.0"
}
```

### 2.2 Manifest 的设计价值

| 价值 | 说明 |
|------|------|
| 可审计 | 完整记录"谁在何时用什么模型审查了哪些文件" |
| 可恢复 | `--resume` 依赖 Manifest 验证模式兼容性 |
| 可对比 | 同仓库不同会话之间可横向对比 Token 消耗、评论数量 |
| 不可变 | 会话结束后 Manifest 不再修改，保证审计完整性 |

---

## 3. 会话恢复

`ocr review --resume <session-id>` 从中断的会话恢复，核心逻辑是**文件级去重**——已成功审查的文件不重复调用 LLM。

### 3.1 恢复流程

```
ocr review --resume <id>
  │
  ├─ 1. 读取 manifest.json
  ├─ 2. 验证模式匹配（from/to/commit 必须一致）
  ├─ 3. 扫描 files/ 目录，识别已完成文件
  ├─ 4. 重新计算待审查文件列表
  ├─ 5. 从 comments.json 加载已有评论
  └─ 6. 仅对未完成文件调用 LLM
```

### 3.2 恢复限制

- **工作区模式不可恢复**：工作区 diff 可能已变化，恢复无意义
- **模式必须严格匹配**：`--from` 和 `--to` 必须与会话创建时一致
- **`--preview` 与 `--resume` 互斥**：预览不生成会话，无法恢复
- **LLM 配置可不同**：恢复时可使用不同的 `--provider`/`--model`，但审查范围必须一致

### 3.3 恢复元数据

恢复运行时，JSON 输出的 `resume` 字段记录恢复详情：

```json
{
  "resume": {
    "resumed_from": "a1b2c3d4-...",
    "reused_files": 7,
    "rerun_files": 2,
    "reused_comments": 1
  }
}
```

---

## 4. 评论查询

`ocr session comments` 支持按严重程度和类别过滤会话中的评论。

### 4.1 过滤参数

```bash
ocr session comments <session-id>
ocr session comments --severity critical,high <session-id>
ocr session comments --category bug,security <session-id>
ocr session comments --severity high --category performance <session-id>
ocr session comments --json <session-id>
```

| 参数 | 值 | 说明 |
|------|-----|------|
| `--severity` | `critical`、`high`、`medium`、`low` 的逗号分隔列表 | 按严重程度过滤 |
| `--category` | `bug`、`security`、`performance`、`maintainability`、`test`、`style`、`documentation`、`other` 的逗号分隔列表 | 按类别过滤 |
| `--json` | — | JSON 数组输出 |

### 4.2 与 jq 组合

```bash
ocr session comments --json <id> | jq '[.[] | select(.severity=="critical")] | length'
ocr session comments --json <id> | jq '.[] | "\(.path):\(.start_line) \(.content)"'
```

---

## 5. OpenTelemetry 集成

OCR 内置 OpenTelemetry 支持，可将评审过程的 Trace 和 Metric 导出到 OTLP 兼容后端（如 Jaeger、Grafana Tempo、Datadog）。

### 5.1 环境变量配置

| 环境变量 | 默认值 | 说明 |
|---------|--------|------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | — | OTLP gRPC 端点（如 `localhost:4317`） |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` | 传输协议（`grpc` 或 `http/protobuf`） |
| `OTEL_SERVICE_NAME` | `ocr` | 服务名 |
| `OCR_OTEL_ENABLED` | `false` | 设为 `true` 启用 |

### 5.2 Span 结构

```
ocr.review (root span)
├── ocr.plan
│   ├── ocr.plan.diff_collection
│   └── ocr.plan.llm_call
├── ocr.file.review (per file, concurrent)
│   ├── ocr.tool.file_read
│   ├── ocr.tool.code_search
│   ├── ocr.tool.code_comment
│   └── ocr.llm.call (per tool round)
└── ocr.report
```

### 5.3 关键 Metrics

| Metric | 类型 | 标签 | 说明 |
|--------|------|------|------|
| `ocr_review_duration_seconds` | Histogram | `mode`、`provider` | 评审总耗时 |
| `ocr_files_reviewed_total` | Counter | `mode`、`status` | 审查文件数 |
| `ocr_comments_total` | Counter | `category`、`severity` | 评论数 |
| `ocr_tokens_total` | Counter | `type`（input/output/cache） | Token 消耗 |
| `ocr_tool_calls_total` | Counter | `tool`、`status` | 工具调用次数 |
| `ocr_compressions_total` | Counter | — | 上下文压缩次数 |

---

## 6. 内嵌 Web 查看器

`ocr viewer` 启动内嵌 HTTP 服务器，以浏览器 UI 渲染历史会话。

### 6.1 启动与绑定

```bash
ocr viewer                    # 默认 localhost:5483
ocr viewer --addr 0.0.0.0:3000  # 绑定所有接口
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--addr` | `localhost:5483` | 监听地址 |

### 6.2 DNS Rebinding 防护

查看器仅允许以下 Host 头访问：

- `localhost`
- `127.0.0.1`
- `[::1]`

其他 Host 头返回 `403 Forbidden`，防止 DNS rebinding 攻击——即恶意网站通过 DNS 配置将域名指向 `127.0.0.1:5483`，从而读取本地会话数据。

### 6.3 查看器功能

- 会话列表（按仓库、时间排序）
- 文件级评论展示（含代码上下文高亮）
- 评论按 category/severity 筛选
- Token 消耗和工具调用时序图
- Plan 阶段输出查看
- Diff 上下文展示

### 6.4 只读设计

查看器是**严格只读**的：
- 不提供任何写操作 API
- 不接受 POST/PUT/DELETE 请求
- 只读取 `~/.opencodereview/sessions/` 目录
- 不执行任何代码或命令

这保证了即使查看器被暴露到网络，攻击者也无法篡改会话数据或执行代码。

---

## 7. 会话管理 CLI 完整参考

| 命令 | 说明 |
|------|------|
| `ocr session list` | 列出最近 20 个会话 |
| `ocr session list --limit 50` | 列出最近 50 个 |
| `ocr session list --json` | JSON 输出 |
| `ocr session show <id>` | 查看会话详情 |
| `ocr session show --json <id>` | JSON 输出会话详情 |
| `ocr session comments <id>` | 查看会话评论 |
| `ocr session comments --severity critical,high <id>` | 按严重程度过滤 |
| `ocr session comments --category security <id>` | 按类别过滤 |
| `ocr session comments --json <id>` | JSON 输出评论数组 |
| `ocr review --resume <id>` | 恢复中断的评审 |
| `ocr viewer` | 启动 Web 查看器 |

会话文件存储位置：`~/.opencodereview/sessions/`（Linux/macOS）或 `%USERPROFILE%\.opencodereview\sessions\`（Windows）。
