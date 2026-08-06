---
id: open-code-review-wiki-07-session-telemetry
title: "Open Code Review 完全指南 — 会话持久化、遥测与查看器"
source: "https://open-codereview.ai/docs/telemetry"
date: "2026-08-05"
category: "learning"
tags: ["open-code-review", "session", "manifest", "telemetry", "opentelemetry", "viewer", "resume", "observability"]
---

# Open Code Review 完全指南 — 会话持久化、遥测与查看器

> 本章深入解析 Open Code Review（以下简称 OCR）的可观测性三件套——会话持久化、Manifest 可追溯性与遥测系统，以及配套的本地查看器。涵盖 JSONL 会话日志、Manifest 双边界状态机、会话恢复重放规则、评论查询、OpenTelemetry Span/Metric 体系、以及带 DNS rebinding 防护的嵌入式查看器。

---

## 1. 会话持久化（internal/session/）

OCR 在每次审查运行时记录一份完整的会话日志（JSONL 格式），用于事后审计、断点恢复与查看器渲染。

### 1.1 存储路径与权限

```
~/.opencodereview/sessions/<encodeRepoPath(repoDir)>/<sessionID>.jsonl
```

- **目录权限** `0700`：仅属主可读写执行，防止其他用户窥探会话内容。
- **文件权限** `0600`：仅属主可读写，防止会话日志泄露代码与 LLM 交互。

`sessionID` 由 `generateUUID` 生成（UUID v4 实现）。每次运行一个独立的 `.jsonl` 文件，逐行追加，不覆盖。

### 1.2 encodeRepoPath 编码

仓库路径不能直接作为目录名（含 `/`、`\`、`:` 等非法字符），需编码：

| 原字符 | 编码后 |
|--------|--------|
| `/` | `-` |
| `\` | `-` |
| `:` | `_` |

例如：

- `/home/user/my-project` → `-home-user-my-project`
- `C:\Users\alice\repo` → `C_\-Users-alice-repo`（`\` → `-`，`:` → `_`）

这一编码保证同一仓库的会话集中在一个目录下，且跨平台路径可安全地作为文件系统路径片段。

### 1.3 generateUUID v4 实现

`generateUUID` 生成 RFC 4122 v4 UUID（随机版本）。v4 UUID 形如 `xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx`，其中 `y` 为 `8`/`9`/`a`/`b`。v4 保证时空唯一性，无需中心化协调，适合会话标识。

### 1.4 9 种记录类型

JSONL 每行一个 JSON 对象，`type` 字段区分记录类型：

| 记录类型 | 写入时机 | 用途 |
|----------|----------|------|
| `session_start` | 会话开始 | 记录起始时间、options、repoDir |
| `review_item_done` | 文件审查完成 | 记录该文件的评论、rule、token 消耗 |
| `review_item_reused` | 复用历史结果 | 缓存命中时记录复用 |
| `review_item_failed` | 文件审查失败 | 记录错误，便于 resume 时跳过 |
| `llm_request` | LLM 请求发出 | 记录 prompt、model、参数 |
| `llm_response` | LLM 响应返回 | 记录响应内容与 usage |
| `llm_error` | LLM 调用出错 | 记录错误类型与消息 |
| `tool_call` | 工具调用 | 记录工具名、参数、结果 |
| `session_end` | 会话结束 | 记录终止时间、终态 |

### 1.5 parentUuid 链式结构

每条记录携带 `parentUuid` 字段，指向前一条记录的 UUID，形成**链式结构**。这使得会话日志可重建为树/链，便于：

- 追踪请求-响应配对（`llm_request` → `llm_response`）
- 还原 Agent 的工具调用序列（`tool_call` 间的父子关系）
- 在查看器中渲染任务卡片的调用链

```mermaid
flowchart LR
    SS["session_start<br/>uuid=A"] --> RID1["review_item_done<br/>uuid=B, parent=A"]
    RID1 --> LR1["llm_request<br/>uuid=C, parent=B"]
    LR1 --> LSP1["llm_response<br/>uuid=D, parent=C"]
    LSP1 --> TC1["tool_call<br/>uuid=E, parent=D"]
    TC1 --> RID2["review_item_done<br/>uuid=F, parent=A"]
    RID2 --> SE["session_end<br/>uuid=G, parent=A"]
```

### 1.6 WriteLLMResponse 的 usage 字段

`llm_response` 记录的 `usage` 字段是 token 计费与预算追踪的核心：

```go
// internal/session/session.go
type LLMResponseRecord struct {
    Type     string    `json:"type"`      // "llm_response"
    UUID     string    `json:"uuid"`
    ParentUuid string  `json:"parent_uuid"`
    // ...
    Usage    Usage     `json:"usage"`
}

type Usage struct {
    PromptTokens        int `json:"prompt_tokens"`         // 输入 token
    CompletionTokens    int `json:"completion_tokens"`     // 输出 token
    CacheReadTokens    int `json:"cache_read_tokens"`     // 缓存命中读取
    CacheWriteTokens   int `json:"cache_write_tokens"`     // 写入缓存
}
```

`cache_read_tokens` / `cache_write_tokens` 反映 prompt cache 的使用——缓存命中可大幅降低成本与延迟，是预算优化的关键观测点。

---

## 2. Manifest 系统（manifest.go）

Manifest 是 OCR 可追溯性的核心：它以结构化、版本化的方式记录一次审查运行的输入、覆盖与结果，是"可复现审查"的凭证。

### 2.1 Schema 与操作

```go
// internal/manifest/manifest.go
const ManifestSchemaVersion = "ocr.run-manifest/v1"
```

v1 唯一支持的 `Operation` 是 `OperationReview`（`"review"`）。未来若有新操作（如 `scan`、`explain`），通过 schema 版本演进。

### 2.2 InputMode 三种

| InputMode | 含义 | 触发方式 |
|-----------|------|----------|
| `range` | 审查一个 ref 范围 | `--from <base> --to <head>` |
| `commit` | 审查单个提交 | `--commit <sha>` |
| `workspace` | 审查工作区未提交变更 | 默认（无 ref 参数） |

### 2.3 FailureClass 八类

文件级失败分类，记录在 `review_item_failed`：

| FailureClass | 场景 |
|---------------|------|
| `Provider` | LLM Provider 返回错误（鉴权、限流） |
| `Timeout` | 请求超时 |
| `Cancelled` | 用户/CI 取消 |
| `Configuration` | 配置错误（缺 endpoint、规则无效） |
| `Input` | 输入问题（diff 解析失败） |
| `Budget` | 预算耗尽 |
| `Panic` | OCR 内部 panic |
| `Unknown` | 未知错误 |

### 2.4 RunFailureClass 七类

运行级失败分类，记录在 Manifest 的 run 级摘要：

`input` / `configuration` / `timeout` / `cancelled` / `budget` / `internal` / `unknown`

`RunFailureClass` 与 `FailureClass` 类似但更粗粒度——它描述整个 run 为何未正常完成，而非单文件失败原因。

### 2.5 TerminalState 四态

| TerminalState | 含义 |
|---------------|------|
| `complete` | 全部选定文件审查完成 |
| `partial` | 部分完成（部分失败或被跳过） |
| `failed` | 整体失败 |
| `skipped` | 整体被跳过（如无文件变更） |

### 2.6 ItemID 派生

`ItemID` 是每个审查项的稳定标识，由输入参数哈希派生：

```
ItemID = SHA-256(operation + mode + oldPath + newPath)
```

- `operation`：如 `review`
- `mode`：InputMode（range/commit/workspace）
- `oldPath` / `newPath`：变更前/后路径

由于基于内容而非时间，相同输入产生相同 ItemID，是缓存复用与 resume 的关键。

### 2.7 Coverage 五集合

Manifest 用五个集合描述覆盖情况：

```mermaid
graph TB
    SEL["Selected<br/>= Completed ∪ Reused ∪ Failed ∪ Waived"]
    COM["Completed"]
    REU["Reused"]
    FAL["Failed"]
    WAI["Waived"]

    SEL --- COM
    SEL --- REU
    SEL --- FAL
    SEL --- WAI

    style SEL fill:#e3f2fd
    style COM fill:#c8e6c9
    style REU fill:#fff9c4
    style FAL fill:#ffcdd2
    style WAI fill:#e0e0e0
```

**关键恒等式**：`Selected = Completed ∪ Reused ∪ Failed ∪ Waived`。这五集合互不相交（一个文件只属于其一），且并集等于选定集。这让覆盖审计一目了然——任何"消失"的文件都会破坏恒等式，立刻被发现。

### 2.8 ManifestBuilder 双边界

`ManifestBuilder` 有两个不可逆的"封印"状态：

| 边界 | 触发方法 | 之后不可变内容 |
|------|----------|----------------|
| sealed | `SealSelected()` | 选定文件集（不能再新增 selected） |
| frozen | `Finalize()` | 全部结果（不能再写入 completed/failed/reused） |

```mermaid
flowchart LR
    OPEN["开放<br/>可添加 selected"] -->|SealSelected| SEALED["sealed<br/>selected 锁定"]
    SEALED -->|写入结果| WRITING["写入中<br/>completed/failed/reused"]
    WRITING -->|Finalize| FROZEN["frozen<br/>全量锁定"]
    FROZEN --> MANIFEST["输出 Manifest"]

    style OPEN fill:#e8f5e9
    style SEALED fill:#fff3e0
    style WRITING fill:#fffde7
    style FROZEN fill:#ffcdd2
    style MANIFEST fill:#e3f2fd
```

双边界防止"事后篡改"——一旦选定集 sealed，不能再悄悄加入文件；一旦 Finalize frozen，不能再修改结果。这是可审计性的硬约束。

### 2.9 sanitizeReason 脱敏

`sanitizeReason` 在写入 Manifest 前对 reason 文本脱敏，防止 secret 泄露到 Manifest。三类正则：

| 类别 | 正则目标 | 示例 |
|------|----------|------|
| URL 凭证 | `https://user:pass@host` 中的 `user:pass` | `https://alice:s3cr3t@api.x` → `https://***@api.x` |
| Bearer token | `Authorization: Bearer xxx` | → `Authorization: Bearer ***` |
| secret 赋值 | `key=value` 形式的疑似 secret | `API_KEY=abc123` → `API_KEY=***` |

脱敏发生在 reason 写入前，保证 Manifest 可安全分享/归档。

---

## 3. 会话恢复（resume.go）

OCR 支持从已有会话日志恢复审查，跳过已完成的文件，仅重跑失败或未完成的文件。

### 3.1 ResumeState 结构

```go
// internal/session/resume.go
type ResumeState struct {
    SessionID    string
    Completed    map[string]bool   // 已完成的文件路径
    Reused       map[string]bool   // 已复用的文件
    Failed       map[string]bool   // 失败的文件（需重跑）
    Options      SessionOptions    // 原会话的 options（用于校验）
}
```

### 3.2 LoadResumeState 重放规则

`LoadResumeState` 重放 JSONL 日志，按记录类型更新状态：

| 记录类型 | 重放动作 |
|----------|----------|
| `session_start` | 提取 Options 用于校验 |
| `review_item_done` | 写入 `Completed` |
| `review_item_reused` | 写入 `Reused` |
| `review_item_failed` | **删除**（从 Completed/Reused 移除，标记需重跑） |

`review_item_failed` 的"删除"语义很关键：失败的文件在 resume 时会被重跑，而非跳过。这保证 resume 不会"继承失败"。

### 3.3 ValidateOptions 校验

resume 时必须校验当前 options 与原会话一致，否则拒绝：

```mermaid
flowchart TD
    START["resume 请求"] --> CHK1{"InputMode == workspace?"}
    CHK1 -->|是| REJ1["拒绝: workspace 模式不支持 resume<br/>（工作区内容易变化）"]
    CHK1 -->|否| CHK2{"InputMode == range?"}
    CHK2 -->|是| CHK3{"DiffFrom/DiffTo 与原会话匹配?"}
    CHK3 -->|否| REJ2["拒绝: range 范围不一致"]
    CHK3 -->|是| OK["通过校验，继续 resume"]
    CHK2 -->|否 commit| CHK4["校验 commit 一致"]
    CHK4 -->|否| REJ3["拒绝: commit 不一致"]
    CHK4 -->|是| OK

    style REJ1 fill:#ffcdd2
    style REJ2 fill:#ffcdd2
    style REJ3 fill:#ffcdd2
    style OK fill:#c8e6c9
```

**关键限制**：workspace 模式**不支持 resume**。因为工作区内容随时变化，恢复点与当前状态可能不一致。range 模式要求 `DiffFrom`/`DiffTo` 与原会话完全匹配。

### 3.4 ValidateScanOptions 路径作用域校验

若 resume 涉及 scan 选项，`ValidateScanOptions` 校验路径作用域（`Paths`）与原会话一致，避免"恢复时换了审查范围"导致覆盖集错乱。

---

## 4. 评论查询（comments.go）

`LoadComments` 从会话日志加载评论，按文件完成顺序排列。

### 4.1 加载逻辑

```go
// internal/session/comments.go
func LoadComments(sessionPath string) (map[string][]Comment, error) {
    // 按 review_item_done 顺序读取
    // 后续记录覆盖前次（同一文件多次审查，取最后）
}
```

**后续覆盖前次**：若同一文件在会话中出现多条 `review_item_done`（如重跑），后续的评论覆盖前次。这保证最终评论集反映最新结果，而非历史中间态。

---

## 5. 遥测系统（internal/telemetry/）

OCR 集成 OpenTelemetry，提供 Span 与 Metric 两类可观测信号。遥测**默认关闭**，需显式启用。

### 5.1 启用与导出器

遥测支持两种导出器：

| 导出器 | 用途 | 启用方式 |
|--------|------|----------|
| `console` | 调试，输出到 stdout | `OCR_ENABLE_TELEMETRY=true` + console 配置 |
| `otlp` | 集成，发送到 OTLP collector | `OCR_ENABLE_TELEMETRY=true` + OTLP endpoint |

### 5.2 Span 树结构

```mermaid
graph TB
    RUN["review.run<br/>根 Span"]
    RUN --> DIFF["diff.parse<br/>解析变更"]
    RUN --> SUB1["subtask.execute.fileA<br/>文件 A 审查"]
    RUN --> SUB2["subtask.execute.fileB<br/>文件 B 审查"]
    RUN --> EV1["event.review.started"]
    RUN --> EV2["event.no.files.changed"]
    RUN --> EV3["event.plan.skipped"]
    RUN --> EV4["event.plan.failed"]
    RUN --> EV5["event.token.threshold.exceeded"]
    RUN --> EV6["event.subtask.error"]

    SUB1 --> EV7["event.* 子事件"]

    style RUN fill:#e3f2fd
    style SUB1 fill:#fff3e0
    style SUB2 fill:#fff3e0
    style EV1 fill:#f3e5f5
```

根 Span `review.run` 之下挂载 `diff.parse` 与各文件的 `subtask.execute.<file>` 子 Span，以及一系列 `event.*` 事件。事件以 Span 形式记录，便于在 trace 视图中按时间线查看。

### 5.3 事件列表

| 事件 | 触发时机 |
|------|----------|
| `review.started` | 审查开始 |
| `no.files.changed` | 无文件变更 |
| `plan.skipped` | 跳过 Plan 阶段 |
| `plan.failed` | Plan 阶段失败 |
| `token.threshold.exceeded` | token 阈值超限 |
| `subtask.error` | 子任务出错 |

### 5.4 8 个 Metric

| Metric | 类型 | 含义 |
|--------|------|------|
| `ocr.review.duration_seconds` | histogram | 审查总耗时 |
| `ocr.files_reviewed_total` | counter | 已审查文件数 |
| `ocr.comments_generated_total` | counter | 生成评论数 |
| `ocr.llm.requests_total` | counter | LLM 请求总数 |
| `ocr.llm.request_duration_seconds` | histogram | LLM 请求耗时 |
| `ocr.llm.tokens_used` | histogram | token 用量（含 cache 维度） |
| `ocr.tool.calls_total` | counter | 工具调用总数 |
| `ocr.tool.execution_duration_seconds` | histogram | 工具执行耗时 |

### 5.5 配置优先级

```mermaid
flowchart LR
    DEF["defaults<br/>内置默认"] -->|被覆盖| CFG["config.json<br/>配置文件"]
    CFG -->|被覆盖| ENV["env vars<br/>环境变量"]
    ENV --> RESULT["生效配置"]

    style ENV fill:#c8e6c9
    style RESULT fill:#e3f2fd
```

优先级从低到高：`defaults < config.json < env vars`。环境变量优先级最高，适合 CI 中用 secret 覆盖。

### 5.6 环境变量

| 环境变量 | 作用 |
|----------|------|
| `OCR_ENABLE_TELEMETRY` | 启用遥测（`true`/`false`） |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP collector 地址 |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | 协议（`grpc`/`http/protobuf`） |
| `OTEL_SERVICE_NAME` | 服务名（标识 OCR 实例） |
| `OCR_CONTENT_LOGGING` | 是否记录内容（prompt/response，默认关闭以保护隐私） |

### 5.7 OTLP 端口

| 协议 | 默认端口 |
|------|----------|
| gRPC | 4317 |
| HTTP | 4318 |

### 5.8 无采样配置

OCR 遥测**不配置采样**，导出全部 Span 与 Metric。这与"可复现审查"理念一致——任何采样都可能丢失关键证据。代价是大数据量下需 collector 端做聚合/采样。

---

## 6. 查看器（internal/viewer/）

OCR 内置一个嵌入式 HTTP 查看器，用于浏览会话日志与 Manifest，无需外部工具。

### 6.1 基本配置

- **默认地址**：`localhost:5483`
- **绑定**：仅 localhost，不对外暴露
- **启动**：`ocr viewer`（或自动在 review 后启动）

### 6.2 DNS rebinding 防护

查看器防御 DNS rebinding 攻击（恶意网站通过 DNS 重绑定访问 localhost 服务）：

```mermaid
flowchart LR
    REQ["HTTP 请求"] --> HG["hostGuard<br/>Host 头校验"]
    HG --> WL{"Host 在白名单?"}
    WL -->|是| OK["允许访问"]
    WL -->|否| REJ["拒绝 403"]

    style WL fill:#fff3e0
    style OK fill:#c8e6c9
    style REJ fill:#ffcdd2
```

`hostGuard` 校验 `Host` 头，仅允许白名单内的 host（如 `localhost`、`127.0.0.1`、`[::1]`），拒绝其他域名解析到本机的请求。这防止恶意网页通过 `Host: evil.com`（DNS 解析到 127.0.0.1）访问查看器读取会话内容。

### 6.3 三条 URL 路由

| URL | 页面 | 内容 |
|-----|------|------|
| `/` | 仓库列表 | 所有有会话的仓库 |
| `/r/{repo}` | 会话列表 | 该仓库下所有 session |
| `/r/{repo}/{sessionID}` | 会话详情 | 单次会话的任务卡片 |

### 6.4 5 种任务类型通道

会话详情页按任务类型分通道展示：

| 任务类型 | 含义 |
|----------|------|
| `plan_task` | Plan 阶段任务 |
| `main_task` | Main Loop 主任务 |
| `review_filter_task` | 审查过滤任务 |
| `memory_compression_task` | 内存压缩任务 |
| `re_location_task` | 重新定位任务 |

### 6.5 任务卡片结构

每张任务卡片包含：

```mermaid
graph TB
    CARD["任务卡片"]
    CARD --> HEAD["Header"]
    CARD --> BODY["Body"]

    HEAD --> H1["请求号"]
    HEAD --> H2["model"]
    HEAD --> H3["token"]
    HEAD --> H4["duration"]
    HEAD --> H5["error 徽章（若有）"]

    BODY --> RESP["Response<br/>LLM 响应内容"]
    BODY --> TOOLS["Tool calls<br/>工具调用列表"]

    style HEAD fill:#e3f2fd
    style BODY fill:#fff3e0
```

Header 展示请求号、model、token 消耗、耗时，以及错误徽章（若失败）。Body 展示 LLM 响应内容与工具调用列表。

### 6.6 template FuncMap

查看器使用 Go `html/template`，注册 FuncMap 提供格式化函数：

| 函数 | 作用 |
|------|------|
| `formatDuration` | 格式化耗时（如 `1.2s`） |
| `formatTime` | 格式化时间戳 |
| `truncate` | 截断长文本（如响应内容预览） |
| `formatNumber` | 数字千分位 |
| `add` | 加法（用于序号） |
| `cardCount` | 卡片计数 |
| `taskTypeClass` | 任务类型 CSS class |
| `orderedTasks` | 任务排序 |

### 6.7 orderedTasks 固定顺序

`orderedTasks` 按固定顺序排列任务卡片，便于阅读：

```
PlanTask → MainTask → ReLocationTask → MemoryCompressionTask
```

这一顺序反映审查的执行流程：先 Plan，再 Main，必要时 ReLocation（重新定位评论位置），最后 MemoryCompression（压缩上下文）。

---

## 7. 配置示例

### 7.1 启用 OTLP 导出

`~/.opencodereview/config.json`：

```json
{
  "telemetry": {
    "enabled": true,
    "exporter": "otlp",
    "otlp_endpoint": "http://localhost:4317",
    "otlp_protocol": "grpc",
    "service_name": "ocr-prod",
    "content_logging": false
  }
}
```

或用环境变量（CI 推荐）：

```bash
export OCR_ENABLE_TELEMETRY=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_SERVICE_NAME=ocr-ci
export OCR_CONTENT_LOGGING=false
```

### 7.2 Jaeger 集成

Jaeger 原生支持 OTLP，是最简单的 trace 后端：

```mermaid
flowchart LR
    OCR["OCR<br/>otel SDK"] -->|OTLP gRPC:4317| COLL["Jaeger Collector<br/>内置 OTLP"]
    COLL --> STORE["Jaeger Storage"]
    STORE --> UI["Jaeger UI<br/>:16686"]

    style OCR fill:#e3f2fd
    style COLL fill:#fff3e0
    style UI fill:#c8e6c9
```

启动 Jaeger（all-in-one，OTLP 接收）：

```bash
docker run -d --name jaeger \
  -p 4317:4317 \
  -p 16686:16686 \
  jaegertracing/all-in-one:latest
```

配置 OCR：

```bash
export OCR_ENABLE_TELEMETRY=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc
export OTEL_SERVICE_NAME=ocr
```

随后在 `http://localhost:16686` 查看 `review.run` Span 树。

### 7.3 Datadog Agent 集成

Datadog Agent 的 OTLP ingestion 端口同样为 4318（HTTP）：

```mermaid
flowchart LR
    OCR["OCR"] -->|OTLP HTTP:4318| DD["Datadog Agent"]
    DD -->|forward| DDOG["Datadog 后端"]
    DDOG --> DASH["Dashboards<br/>APM/Traces/Logs"]

    style OCR fill:#e3f2fd
    style DD fill:#732bbb
    style DASH fill:#c8e6c9
```

Datadog Agent `datadog.yaml` 启用 OTLP：

```yaml
otlp_config:
  receiver:
    protocols:
      http:
        endpoint: 0.0.0.0:4318
```

OCR 配置：

```bash
export OCR_ENABLE_TELEMETRY=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_SERVICE_NAME=ocr-prod
```

随后在 Datadog APM 中按 `service:ocr-prod` 过滤，查看 `ocr.review.duration_seconds`、`ocr.llm.tokens_used` 等指标与 trace。

---

## 8. 小结与设计哲学

OCR 的可观测性三件套体现了"可审计性优先"的设计哲学：

1. **会话日志全量持久化**：JSONL 逐行追加，9 种记录类型 + parentUuid 链式结构，保证审查过程完整可重放。
2. **Manifest 双边界状态机**：sealed/frozen 两个不可逆封印，杜绝事后篡改；Coverage 五集合恒等式让覆盖审计一目了然。
3. **resume 重放而非续跑**：失败文件重跑，已完成文件跳过，且强制 options 一致校验，保证恢复点的语义正确。
4. **遥测默认关闭、无采样**：尊重隐私（content_logging 默认关闭），但一旦启用即全量导出，不丢失证据。
5. **查看器 localhost-only + DNS rebinding 防护**：便利与安全兼顾，hostGuard 白名单防止跨站访问。

这套可观测性体系是 OCR"确定性工程"的延伸——不仅审查结果确定，审查过程本身也可被完整观测、审计与复现。这为下一章的集成与扩展（CI/CD、Claude Code、Delegation Mode）提供了被信任的基础。
