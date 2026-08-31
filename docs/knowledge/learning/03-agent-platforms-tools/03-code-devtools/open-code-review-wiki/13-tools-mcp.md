---
type: Wiki Tutorial

id: "open-code-review-wiki-13"
title: "内置工具与 MCP 集成"
source: "https://open-codereview.ai/docs/tools"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/13-tools-mcp.toml"
---
# 内置工具与 MCP 集成

> 本章深入解析 OCR 的工具系统——Registry 注册机制、Provider 接口契约、6 个内置工具详解、code_comment 评论机制、MCP 集成与工具自定义扩展。[关键技术优化](04-optimizations.md)中简要提到了 4 个工具，本章提供完整的工具系统参考。

---

## 1. 工具系统架构

OCR 的工具系统采用"Registry + Provider"双层架构，统一管理内置工具和 MCP 工具。

| 组件 | 职责 | 设计理由 |
|------|------|---------|
| **Registry** | 工具注册、查询、冻结 | 统一管理入口，支持冻结后的不可变性 |
| **Provider 接口** | 工具契约 | 内置工具和 MCP 工具实现同一接口 |
| **6 个内置工具** | 核心审查能力 | 覆盖"声明完成""评论""读取""查找""搜索"全流程 |
| **MCP 工具** | 扩展能力 | 通过 MCP 协议接入外部工具服务器 |

### 1.1 Provider 接口契约

```go
// internal/tools/provider.go
type Provider interface {
    Tool() ToolDef
    Execute(ctx context.Context, args json.RawMessage) Result
}

type ToolDef struct {
    Name        string          `json:"name"`
    Description string          `json:"description"`
    Parameters  json.RawMessage `json:"parameters"` // JSON Schema
}

type Result struct {
    Content string
    Error   string
    Meta    map[string]interface{}
}
```

`Execute` 返回 `Result` 而非 `(Result, error)`——工具执行错误被封装在 `Result.Error` 中，作为"常规工具结果"返回给模型，让模型能理解工具失败并决定下一步（重试或换工具），而非中断 Main Loop。

### 1.2 Registry 冻结机制

Registry 支持"冻结"状态，冻结后禁止注册新工具：

```go
func (r *Registry) Register(p Provider) {
    if r.frozen {
        panic("registry is frozen: cannot register new tool after Freeze()")
    }
    // ...
}
```

| 阶段 | 可注册 | 可查询 | 可执行 |
|------|--------|--------|--------|
| 初始化 | ✅ | ✅ | ❌ |
| 冻结后 | ❌ panic | ✅ | ✅ |

冻结的价值：防止 Agent 注入后门工具、保证工具集可审计（冻结后是 Manifest 的一部分）、避免并发注册问题。

---

## 2. 6 个内置工具详解

| 工具名 | Plan 阶段 | Main 阶段 | 核心功能 |
|--------|----------|----------|---------|
| `task_done` | ❌ | ✅ | 声明审查完成，state=DONE/FAILED |
| `code_comment` | ❌ | ✅ | 提交代码评论，8 类 category + 4 级 severity |
| `file_read` | ❌ | ✅ | 读取文件内容，最多 500 行 |
| `file_read_diff` | ✅ | ✅ | 读取 DiffMap 不可变快照 |
| `file_find` | ✅ | ✅ | 查找文件，最多 100 匹配 |
| `code_search` | ✅ | ✅ | 代码搜索，每文件最多 100 匹配 |

### 2.1 task_done：声明审查完成

`state` 为 `DONE` 时 Main Loop 退出并收集评论；为 `FAILED` 时退出并记录失败原因。`task_done` 只在 Main 阶段可用。

### 2.2 code_comment：提交代码评论

**8 类 category**：

| category | 描述 |
|----------|------|
| `bug` | 缺陷：可能导致错误行为 |
| `security` | 安全漏洞 |
| `performance` | 性能问题 |
| `maintainability` | 可维护性问题 |
| `test` | 测试覆盖不足 |
| `style` | 代码风格问题 |
| `documentation` | 文档问题 |
| `other` | 其他问题 |

**4 级 severity**：

| severity | 含义 | 建议处理 |
|----------|------|---------|
| `critical` | 严重：必须修复 | 阻塞合并 |
| `high` | 高：应尽快修复 | 建议合并前修复 |
| `medium` | 中等：建议修复 | 可合并后修复 |
| `low` | 低：可选修复 | 记录即可 |

Comment 结构：

```go
type Comment struct {
    Content        string `json:"content"`
    ExistingCode   string `json:"existing_code"`
    SuggestionCode string `json:"suggestion_code"`
    Thinking       string `json:"thinking"`
    Category       string `json:"category"`
    Severity       string `json:"severity"`
}
```

### 2.3 file_read：读取文件内容

单次最多返回 500 行（`MaxFileReadLines = 500`）。当文件超过 500 行时结果被截断并标记 `IS_TRUNCATED=true`，模型可据此决定是否分段读取。支持 `start_line` 和 `end_line` 参数。

### 2.4 file_read_diff：读取 Diff 快照

DiffMap 在 Agent 执行前注入，是**不可变快照**。支持 Plan 和 Main 阶段，读取不涉及 git 命令，纯内存操作。

### 2.5 file_find：查找文件

最多返回 100 个匹配（`MaxFileFindMatches = 100`）。支持两种模式：

| 模式 | 命令 | 范围 |
|------|------|------|
| `tracked` | `git ls-files` | Git 跟踪的文件 |
| `all` | `git ls-tree -r` | 工作区所有文件（含未跟踪） |

### 2.6 code_search：代码搜索

每文件最多 100 匹配（`MaxSearchMatchesPerFile = 100`）。优先使用 `git grep`，失败时回退到 `git grep --no-index`（允许在非 Git 目录搜索）。

---

## 3. code_comment 评论机制

### 3.1 CommentWorkerPool 异步收集

OCR 使用 Worker Pool（默认 8 workers，channel 缓冲 100）异步收集评论，避免阻塞 Main Loop。评论经参数解析后进入队列，Worker 异步执行锚定验证、去重和收集。

### 3.2 existing_code 锚定机制

`existing_code` 字段通过**动态滑动窗口算法**匹配到具体代码位置：

```go
func FindAnchorLine(content, existingCode string, hintLine int) (int, bool) {
    windowSizes := []int{1, 3, 5, 10, 20, 50}
    for _, window := range windowSizes {
        start := max(0, hintLine-window)
        end := min(len(fileLines), hintLine+window)
        // 在窗口内逐行匹配...
    }
}
```

窗口从小到大逐步扩大，平衡精确匹配和容错性。

### 3.3 CommentCollector 线程安全 API

| API | 使用场景 |
|-----|---------|
| `Add` | Worker Pool 收集评论（写锁） |
| `Comments` | 输出阶段获取全部评论（读锁） |
| `CommentsForPath` | 按文件处理（读锁） |
| `Snapshot` | 压缩前快照、Manifest 记录（读锁 + 深拷贝） |
| `Since` | 增量处理（读锁） |
| `ReplaceSince` | 压缩后替换评论（写锁） |
| `RemoveByPathAndIndices` | 去重删除（写锁） |

`Snapshot` 返回深拷贝，避免调用方修改内部状态。

---

## 4. MCP 集成

OCR 通过 MCP（Model Context Protocol）协议集成外部工具服务器。

### 4.1 两种传输方式

| 传输 | 适用场景 | 实现 |
|------|---------|------|
| stdio 子进程 | 本地 MCP 服务器 | `exec.Command` 启动子进程，通过 stdin/stdout 通信 |
| Streamable HTTP | 远程 MCP 服务器 | HTTP POST + SSE 流式响应 |

### 4.2 MCP 配置格式

```json
{
  "mcp_servers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/dir"],
      "env": { "NODE_ENV": "production" },
      "tools": ["read_file", "write_file"],
      "setup": ["npm", "install", "@modelcontextprotocol/server-filesystem"]
    },
    "remote-api": {
      "type": "remote",
      "url": "https://api.example.com/mcp",
      "headers": { "Authorization": "Bearer token-xxx" },
      "tools": ["query", "search"]
    }
  }
}
```

**stdio 类型字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 必须为 `"stdio"` |
| `command` | ✅ | 启动命令 |
| `args` | ❌ | 命令参数数组 |
| `env` | ❌ | 环境变量 |
| `tools` | ❌ | 白名单（不填则注册全部） |
| `setup` | ❌ | 初始化命令（首次运行前执行，5 分钟超时） |

**remote 类型字段**：

| 字段 | 必填 | 说明 |
|------|------|------|
| `type` | ✅ | 必须为 `"remote"` |
| `url` | ✅ | MCP 服务器 URL |
| `headers` | ❌ | 自定义 HTTP 头 |
| `tools` | ❌ | 白名单 |

MCP 服务器初始化握手超时 30 秒。

### 4.3 三层注册过滤

MCP 工具注册时有三层过滤：

| 过滤层 | 规则 | 理由 |
|--------|------|------|
| 白名单 | 只注册白名单中的工具 | 用户控制暴露给 Agent 的工具 |
| 保留名 | 跳过与内置工具同名的 | 防止 MCP 工具覆盖核心功能 |
| 首注册获胜 | 已注册的同名工具跳过 | 保证工具唯一性 |

"首次注册获胜"保证了内置工具（`task_done`、`code_comment` 等）的优先级——MCP 工具不能覆盖核心工具。

### 4.4 401/403 错误处理

远程 MCP 传输在收到 401 或 403 状态码时返回明确的认证错误：`authentication failed: <code>, please check your token`。

---

## 5. 工具自定义

OCR 支持通过 `--tools` flag 覆盖嵌入式 `tools.json`：

```bash
ocr review --tools /path/to/my-tools.json
```

`tools.json` 格式：

```json
{
  "tools": [
    {
      "name": "my_custom_tool",
      "description": "A custom tool for specific analysis",
      "parameters": {
        "type": "object",
        "properties": {
          "input": { "type": "string" }
        },
        "required": ["input"]
      },
      "handler": "python /path/to/handler.py"
    }
  ]
}
```

`--tools` flag 优先级高于嵌入式配置，适合特定项目需要特定工具的场景。

---

## 6. 工具错误处理

OCR 的工具错误处理遵循"错误也是结果"原则：

```go
// ✅ OCR 的设计：错误作为结果返回
func (t *Tool) Execute(args) Result {
    if err != nil {
        return Result{Error: err.Error()} // 模型能看到错误并恢复
    }
}
```

| 错误类型 | 示例 | 模型应对策略 |
|---------|------|------------|
| 文件不存在 | `file_read: /path not found` | 检查路径或用 `file_find` 查找 |
| 搜索无结果 | `code_search: no matches` | 调整查询或扩大范围 |
| 参数无效 | `code_comment: invalid category` | 修正参数后重试 |
| MCP 服务器断开 | `mcp tool: connection lost` | 放弃该工具，用其他工具 |
| 超时 | `file_read: timeout` | 缩小读取范围 |

工具错误是"可恢复的"——模型看到错误后可以调整策略，而非中断 Main Loop。

---

## 7. 源码索引

| 模块 | 文件路径 | 核心符号 |
|------|---------|---------|
| Provider 接口 | `internal/tools/provider.go` | `Provider`, `ToolDef`, `Result` |
| Registry | `internal/tools/registry.go` | `Registry`, `Register`, `Freeze` |
| task_done | `internal/tools/task_done.go` | `TaskDoneTool` |
| code_comment | `internal/tools/code_comment.go` | `CodeCommentTool`, `ParseComments` |
| file_read | `internal/tools/file_read.go` | `FileReadTool`, `MaxFileReadLines` |
| file_read_diff | `internal/tools/file_read_diff.go` | `FileReadDiffTool` |
| file_find | `internal/tools/file_find.go` | `FileFindTool`, `MaxFileFindMatches` |
| code_search | `internal/tools/code_search.go` | `CodeSearchTool` |
| CommentWorkerPool | `internal/tools/comment_worker.go` | `CommentWorkerPool` |
| CommentCollector | `internal/tools/collector.go` | `CommentCollector` |
| 锚定算法 | `internal/tools/anchor.go` | `FindAnchorLine` |
| MCP Client | `internal/mcp/client.go` | `NewClient`, `CallTool` |
| MCP Remote | `internal/mcp/remote_client.go` | `NewRemoteClient`, `headerTransport` |
| MCP 注册 | `internal/mcp/register.go` | `RegisterAll` |
| 工具加载 | `internal/tools/loader.go` | `LoadTools` |
