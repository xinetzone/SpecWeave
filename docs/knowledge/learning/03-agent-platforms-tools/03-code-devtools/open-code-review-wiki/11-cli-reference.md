---
type: Wiki Tutorial

id: "open-code-review-wiki-11"
title: "CLI 命令完整参考"
source: "https://open-codereview.ai/docs/cli-reference"
x-toml-ref: "../../../../../../.meta/toml/docs/knowledge/learning/03-agent-platforms-tools/03-code-devtools/open-code-review-wiki/11-cli-reference.toml"
---
# CLI 命令完整参考

> 本章是 `ocr` 命令行工具的完整参考，补充[使用流程与命令详解](03-usage.md)未覆盖的全部子命令、Flag、JSON 输出格式、退出码与共享参数。基础使用（`ocr review` 与 `ocr scan` 的核心流程）已在[第 3 章](03-usage.md)介绍，本章聚焦完整命令体系。

---

## 1. 命令体系总览

OCR 采用 Cobra 框架构建命令行接口，根命令为 `ocr`，下设 10 个子命令。

### 1.1 命令树

```
ocr
├── version              显示版本信息
├── review, r            运行代码审查
│   ├── workspace 模式（默认）
│   ├── range 模式（--from --to）
│   └── commit 模式（--commit）
├── scan, s              全文件扫描
│   ├── 全仓库扫描
│   ├── 指定路径扫描（--path）
│   └── 恢复扫描（--resume）
├── delegate, d          委托模式
│   ├── preview          预览文件+规则
│   └── rule             查看特定文件规则
├── session, sessions    会话管理
│   ├── list, ls         列出会话
│   ├── show             查看会话详情
│   └── comments         查看会话评论
├── config               配置管理
│   ├── set              设置配置值
│   ├── unset            删除配置项
│   ├── provider         交互式 provider 配置
│   └── model            交互式 model 选择
├── llm                  LLM 工具
│   ├── test             连接测试
│   └── providers        列出内置 provider
├── rules                规则自查
│   └── check            查看文件命中规则
├── viewer, v            Web 查看器
└── completion           Shell 补全
```

### 1.2 命令别名表

| 完整命令 | 别名 | 说明 |
|---------|------|------|
| `ocr review` | `ocr r` | 运行代码审查 |
| `ocr scan` | `ocr s` | 全文件扫描 |
| `ocr delegate` | `ocr d` | 委托模式 |
| `ocr viewer` | `ocr v` | 启动 Web 查看器 |
| `ocr session` | `ocr sessions` | 会话管理（含复数形式） |
| `ocr session list` | `ocr session ls` | 列出会话 |
| `ocr review --commit` | `ocr review -c` | 单 commit 审查 |
| `ocr review --preview` | `ocr review -p` | 预览模式 |
| `ocr review --format` | `ocr review -f` | 输出格式 |
| `ocr review --background` | `ocr review -b` | 业务上下文 |
| `ocr version` | `ocr --version`、`ocr -V` | 版本信息 |

---

## 2. ocr review 完整 Flag 表

基础用法见[第 3 章](03-usage.md)，以下是全部 Flag：

| 参数 | 简写 | 默认值 | 说明 |
|------|------|--------|------|
| `--repo <path>` | — | 当前目录 | Git 仓库根 |
| `--from <ref>` | — | — | diff 起始 ref（如 main） |
| `--to <ref>` | — | — | diff 结束 ref。设置后计算 `merge-base(from, to)..to` |
| `--commit <sha>` | `-c` | — | 审查单个 commit（相对其父） |
| `--preview` | `-p` | `false` | 运行过滤流水线但跳过 LLM，打印文件列表与排除原因 |
| `--resume <session-id>` | — | — | 从之前兼容的区间或单 commit 评审会话恢复 |
| `--format <fmt>` | `-f` | `text` | `text`（人类可读）或 `json`（机器可读评论数组） |
| `--audience <who>` | — | `human` | `human` 流式输出进度行；`agent` 静默 stdout，只打印最终摘要/JSON |
| `--background <text>` | `-b` | — | 注入 plan + main prompt 的可选需求/业务上下文 |
| `--concurrency <n>` | — | `8` | 并行审查的最大文件数 |
| `--timeout <minutes>` | — | `10` | 每文件截止时间。`0` 关闭超时 |
| `--rule <path>` | — | — | 自定义 JSON 审查规则文件路径，覆盖项目级与全局 rule.json |
| `--max-tools <n>` | — | 模板默认 | 每文件最大工具调用轮数。`0` 用模板默认（30）；1-9 上调到 10；≥10 覆盖模板默认 |
| `--provider <name>` | — | — | 为本次运行选择已配置的 provider |
| `--model <name>` | — | — | 为本次运行覆盖已解析出的 LLM model |
| `--max-git-procs <n>` | — | `16` | 并发 git 子进程的最大数 |
| `--tools <path>` | — | 内嵌 | 自定义 JSON 工具配置文件路径，覆盖内嵌工具定义 |

### 2.1 三种审查模式互斥规则

| 组合 | 是否允许 | 说明 |
|------|---------|------|
| 不传任何模式参数 | ✅ | 工作区模式 |
| `--from` + `--to` | ✅ | 区间模式 |
| `--commit` | ✅ | Commit 模式 |
| `--from` + `--to` + `--commit` | ❌ | 报错：模式互斥 |
| `--resume` + `--preview` | ❌ | 报错：不可同时使用 |
| `--resume` + 工作区模式 | ❌ | 工作区评审不能恢复 |

### 2.2 单次运行的 LLM 选择

`review` 和 `scan` 都接受 `--provider` 与 `--model`，这些覆盖**仅作用于当前调用**，不会修改已保存的配置：

```bash
ocr review --provider anthropic --model claude-opus-4-6 --format json
ocr scan --provider openai --model gpt-5.4 --format json
```

**解析逻辑**：
- 显式 `--provider` 从已保存的 `providers` 或 `custom_providers` 中选择条目
- 不传 `--provider` 时，按已保存配置 → `OCR_LLM_*` 环境变量 → Claude Code 环境变量 → shell rc 文件顺序解析
- `--model` 覆盖最终选中来源中的 model，但不改变来源顺序

### 2.3 恢复中断的评审

每次 `ocr review` 都在 `~/.opencodereview/sessions/` 下保存本地会话日志：

```bash
ocr session list
ocr session show <session-id>
ocr session comments <session-id>
ocr review --from main --to feature-branch --resume <session-id>
ocr review --commit abc123 --resume <session-id>
```

**恢复逻辑是严格的**：
- 工作区评审不能恢复
- 区间评审必须使用相同的 `--from` 和 `--to`
- 单 commit 评审必须使用相同的 `--commit`
- `--preview` 和 `--resume` 不能同时使用

---

## 3. ocr scan 独立 Flag

`ocr scan` 的基础用法见[第 3 章](03-usage.md)，以下是其独立 Flag：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--path <path>` | 当前目录 | 指定扫描目录或文件，可多次指定 |
| `--no-plan` | `false` | 跳过 plan 阶段，直接进入审查 |
| `--no-dedup` | `false` | 禁用评论去重 |
| `--no-summary` | `false` | 不打印运行结束摘要 |
| `--batch <n>` | — | 批量扫描的批次大小 |

`ocr scan` 同样支持 `--provider`、`--model`、`--concurrency`、`--timeout`、`--rule`、`--format`、`--audience` 等共享 Flag。

---

## 4. ocr session 会话管理

列出和查看保存在 `~/.opencodereview/sessions/` 下的本地评审会话日志。

### 4.1 ocr session list

```bash
ocr session list
ocr session list --limit 50
ocr session list --json
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--repo <path>` | 当前目录 | 要列出会话的仓库 |
| `--json` | `false` | 以 JSON 输出会话摘要 |
| `--limit <n>` | `20` | 限制列出的会话数量。`0` 表示不限制 |

### 4.2 ocr session show

```bash
ocr session show <session-id>
ocr session show --json <session-id>
```

输出会话元数据和逐文件条目，渲染风格与 `ocr review` 终端输出一致。

### 4.3 ocr session comments

输出单个会话中记录的评审评论，支持按严重程度和类别过滤：

```bash
ocr session comments <session-id>
ocr session comments --severity high <session-id>
ocr session comments --severity critical,high --category bug,security <session-id>
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--json` | `false` | 以 JSON 数组输出评论 |
| `--severity <list>` | 全部 | 逗号分隔：`critical`、`high`、`medium`、`low` |
| `--category <list>` | 全部 | 逗号分隔：`bug`、`security` 等 |

---

## 5. ocr viewer

启动内嵌 HTTP 服务器，读取 `~/.opencodereview/sessions/...`，以浏览器 UI 渲染历史评审会话。

```bash
ocr viewer                    # 默认 localhost:5483
ocr viewer --addr :3000       # 绑定到所有接口的 3000 端口
ocr viewer --addr 127.0.0.1:8080
```

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--addr <address>` | `localhost:5483` | 监听地址 |

查看器具备 DNS rebinding 防护，仅允许 `localhost`、`127.0.0.1`、`[::1]` 访问。

---

## 6. ocr delegate 委托模式

委托模式让宿主 AI 编程 Agent（如 Claude Code、Cursor）使用**自己的 LLM** 执行代码审查。OCR 负责文件选择和规则解析，宿主 Agent 负责实际的 LLM 调用——**无需配置 OCR 的 API key**。

### 6.1 delegate preview

```bash
ocr delegate preview
```

预览 OCR 将交给宿主 Agent 的文件列表与对应规则，不调用任何 LLM。

### 6.2 delegate rule

```bash
ocr delegate rule src/main.go src/handler.go
```

查看特定文件将应用的审查规则，输出每个文件的路径、命中的规则来源层、glob 模式和规则文本。

---

## 7. ocr config 配置管理

将 key 持久化到 `~/.opencodereview/config.json`，并提供交互式配置 TUI。

### 7.1 子命令

| 子命令 | 说明 |
|--------|------|
| `ocr config set <key> <value>` | 非交互式写入单个配置值 |
| `ocr config unset custom_providers.<name>` | 删除一个自定义 provider |
| `ocr config provider` | 启动交互式 provider 配置 TUI |
| `ocr config model` | 启动交互式 model 选择 TUI |

### 7.2 set 用法示例

```bash
ocr config set llm.url https://api.anthropic.com/v1/messages
ocr config set llm.auth_token sk-ant-xxxxx
ocr config set llm.model claude-opus-4-6
ocr config set llm.use_anthropic true
ocr config set provider anthropic
ocr config set model claude-opus-4-6
```

`unset` 仅支持 `custom_providers.<name>`。若删除的是当前启用的 provider，则 `provider` 和 `model` 被清空。

---

## 8. ocr llm LLM 工具

### 8.1 ocr llm test

```bash
ocr llm test
```

以与 `ocr review` 完全相同的方式解析 LLM 端点，发送一条预置 chat 请求并打印结果。非零退出意味着端点未完整配置或请求失败。

### 8.2 ocr llm providers

```bash
ocr llm providers
```

以三列表格列出每个内置 LLM provider（名称、协议、Base URL）。OCR 内置 **19 个 provider**，覆盖主流 LLM 服务商。详见 [LLM 协议与 Provider](12-llm-providers.md)。

---

## 9. ocr rules 规则自查

```bash
ocr rules check src/main/java/com/example/Foo.java
ocr rules check --rule /path/to/custom.json src/main.go
```

对给定文件路径，OCR 遍历四层规则链（`custom → project → global → system`），取第一条匹配，打印**来源层**、匹配的 **glob 模式**以及解析出的**规则文本**。

| 参数 | 说明 |
|------|------|
| `--repo <path>` | Git 仓库根（默认当前目录） |
| `--rule <path>` | 自定义规则 JSON 文件路径 |

---

## 10. JSON 输出格式

使用 `--format json` 时，OCR 输出机器可读的 JSON 结构。

### 10.1 完整 JSON 示例

```json
{
  "status": "success",
  "llm": {
    "provider": "anthropic",
    "model": "claude-opus-4-6"
  },
  "summary": {
    "files_reviewed": 9,
    "comments": 1,
    "total_tokens": 21344,
    "input_tokens": 18012,
    "output_tokens": 3332,
    "elapsed": "1m12s"
  },
  "comments": [
    {
      "path": "src/foo.go",
      "content": "Concurrent map access without a lock — wrap with sync.RWMutex.",
      "start_line": 42,
      "end_line": 47,
      "existing_code": "m[k] = v",
      "suggestion_code": "mu.Lock(); defer mu.Unlock(); m[k] = v",
      "thinking": "Looking at line 42, the map …"
    }
  ],
  "warnings": [
    {
      "file": "src/bar.go",
      "error": "token budget exceeded"
    }
  ],
  "session_id": "abc123-def456-..."
}
```

### 10.2 顶层字段说明

| 字段 | 说明 |
|------|------|
| `status` | `success`、`completed_with_warnings`、`completed_with_errors` 或 `skipped` |
| `llm` | 实际解析的 LLM 标识 |
| `message` | 可选。人类可读摘要 |
| `summary` | 运行聚合：`files_reviewed`、`comments`、`total_tokens`、`input_tokens`、`output_tokens`、`cache_read_tokens`、`cache_write_tokens`、`elapsed` |
| `comments` | 评论数组，每条含 `path`、`content`、`start_line`、`end_line`、`existing_code`、`suggestion_code`、`thinking` |
| `warnings` | 可选。子 agent 失败时存在 |
| `session_id` | 可选。可传给 `--resume` 恢复 |
| `resume` | 可选。恢复运行时存在，含 `resumed_from`、`reused_files`、`rerun_files` 等 |

### 10.3 skipped 状态

当没有文件可评审时，JSON 模式返回 `skipped` 外壳：

```json
{
  "status": "skipped",
  "message": "No supported files changed.",
  "llm": { "provider": "anthropic", "model": "claude-opus-4-6" },
  "comments": []
}
```

### 10.4 CI/CD 典型用法

```bash
COMMENTS=$(ocr review --from main --to feature --format json --audience agent | jq '.comments | length')
SESSION_ID=$(ocr review --from main --to feature --format json --audience agent | jq -r '.session_id')
```

---

## 11. 退出码

| 退出码 | 含义 |
|--------|------|
| `0` | 评审完成（可能零评论，可能有非致命警告） |
| `1` | 致命错误——参数错误、无法解析 LLM 端点、所有 per-file 子 agent 失败等 |

非致命警告内联打印；JSON 模式下加入 `warnings` 数组。

---

## 12. 共享 Flag 详解

### 12.1 并发与超时类

| Flag | 默认值 | 作用 |
|------|--------|------|
| `--concurrency <n>` | `8` | 并行审查的最大文件数 |
| `--timeout <minutes>` | `10` | 每文件截止时间。`0` 关闭超时 |
| `--max-tools <n>` | `0`（模板默认 30） | 每文件最大工具调用轮数 |
| `--max-git-procs <n>` | `16` | 并发 git 子进程的最大数 |
| `--max-tokens-budget <n>` | `0`（不限制） | 整次审查的 token 预算上限 |

当某文件 diff 单独超过 `MAX_TOKENS` 的 80%（默认 `58888`）时，会在调用 LLM 前被丢弃。

### 12.2 audience 与 format 的独立性

`--audience agent` **并不**隐含 `--format json`。两者控制不同的事——屏蔽 UI vs 结构化载荷：

| 组合 | 行为 |
|------|------|
| `--audience human --format text` | 默认，流式进度 + 人类可读评论 |
| `--audience human --format json` | 流式进度 + JSON 输出 |
| `--audience agent --format text` | 静默进度 + 人类可读评论 |
| `--audience agent --format json` | 静默进度 + JSON 输出（CI/CD 推荐） |

### 12.3 --background 的重要性

`--background` 是提升评审质量最有效的参数之一，允许注入业务上下文、需求描述、PR 说明等信息：

```bash
ocr review -b "feat: 新增用户认证模块，需检查 OAuth 流程安全性"
ocr review --from main --to feature -b "$(gh pr view --json body -q .body)"
```

---

## 13. 完整命令速查

| 场景 | 命令 |
|------|------|
| 工作区审查 | `ocr review` |
| 区间审查 | `ocr review --from main --to feature` |
| Commit 审查 | `ocr review --commit abc123` |
| 预览（不调 LLM） | `ocr review --preview` |
| CI/CD 输出 | `ocr review --format json --audience agent` |
| 恢复中断 | `ocr review --resume <session-id>` |
| 全仓库扫描 | `ocr scan` |
| 指定路径扫描 | `ocr scan --path internal/agent` |
| 委托预览 | `ocr delegate preview` |
| 列出会话 | `ocr session list --limit 50` |
| 查看评论（过滤） | `ocr session comments --severity critical,high <id>` |
| 交互式配置 | `ocr config provider` / `ocr config model` |
| 非交互式设置 | `ocr config set llm.model claude-opus-4-6` |
| 连接测试 | `ocr llm test` |
| 列出 provider | `ocr llm providers` |
| 规则自查 | `ocr rules check src/main.java` |
| Web 查看器 | `ocr viewer` / `ocr viewer --addr :3000` |
| 版本信息 | `ocr version` |
