---
id: "intelligent-terminal-ch11-logging"
title: "第11章 - 日志系统与调试"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第11章 日志系统与调试

Intelligent Terminal 采用**结构化、多写入器、按版本隔离**的日志系统设计。Rust WTA 进程、C++ Terminal 端、PowerShell hooks 三个独立的写入器共享同一个按版本划分的日志目录，配合完善的级别控制、轮转策略和结构化 target 字段，让问题定位和端到端追踪变得高效可追溯。

---

## 11.1 日志系统概述

WTA 日志系统有三个核心设计原则：

| 原则 | 实现方式 | 目的 |
|------|---------|------|
| **按生命周期分离存储** | State root vs Local/cache root 双根目录 | 持久化数据与临时诊断数据分离，避免诊断数据漫游/备份 |
| **按版本隔离** | `logs\&lt;pkgver&gt;\` 子目录 | 升级后旧版本日志可整体清理，无锁并发安全 |
| **多写入器共享目录** | Rust/C++/PowerShell 写入同一版本目录 | 问题排查时无需跨目录查找所有相关日志 |
| **结构化 tracing** | 统一使用 `target` + key=value 字段 | 支持按流程、会话、组件精确 grep 过滤 |

所有 Rust 进程（master/helper/cli/delegate/probe 等）使用 `tracing` + `tracing-appender` 非阻塞写入器，保证即使高并发场景下也不会阻塞主流程。

---

## 11.2 WTA 运行时数据布局（package-private store）

WTA 运行时数据全部存放在**包私有存储**（package-private store）中，卸载时自动清理，开发侧载包（dev-sideload）和商店包（store）之间完全隔离。

两个数据根目录均在 [`runtime_paths.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/runtime_paths.rs) 中解析，无包身份时（开发构建直接从 cargo target 运行、测试）回退到同一个传统裸路径。

---

## 11.3 STATE root vs LOCAL/cache root 分离

运行时数据按**生命周期**严格分为两个根目录：

### 11.3.1 STATE root（持久化状态）

**路径**：
- 打包环境：`…\Packages\&lt;PackageFamilyName&gt;\LocalState\IntelligentTerminal\`
- 非打包环境：`%LOCALAPPDATA%\IntelligentTerminal\`

**对应函数**：[`intelligent_terminal_root()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/runtime_paths.rs#L30-L33)

**存储内容**（必须持久化、包私有）：

| 内容 | 说明 |
|------|------|
| `prompts\` | Prompt 覆盖目录 |
| `agent-pane-sessions.jsonl` | Agent 窗格会话来源索引 |
| `master-pipe.txt` | helper ↔ master 命名管道 rendezvous 文件 |
| (WT 自有) | `settings.json`、`state.json` 等 WT 自身状态文件 |

STATE root 位于 `LocalState`，与 WT 应用自身的 `settings.json`/`state.json` 并列存放，会随包数据漫游/备份。

### 11.3.2 LOCAL/cache root（临时缓存/诊断）

**路径**：
- 打包环境：`…\Packages\&lt;PackageFamilyName&gt;\LocalCache\Local\IntelligentTerminal\`
- 非打包环境：`%LOCALAPPDATA%\IntelligentTerminal\`（与 STATE 回退到同一路径）

**对应函数**：[`intelligent_terminal_local_root()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/runtime_paths.rs#L41-L45)

**存储内容**（可重新生成的临时诊断数据）：

| 内容 | 说明 |
|------|------|
| `logs\&lt;pkgver&gt;\` | 所有日志文件（Rust/C++/PS） |
| `hook-bundle-staging\` | Hooks 安装器暂存目录 |
| `hooks-upgrade-state.json` | Hooks 自动升级快速路径的 per-CLI bundle 版本缓存 |

LOCAL/cache root 位于 `LocalCache\Local`，这是**不漫游、不备份**的缓存存储，适合存放可重新生成的日志和临时文件。

### 11.3.3 包家族名称（Package Family Name）

两个包家族相互隔离，数据完全分开：

| 家族类型 | Package Family Name 示例 |
|---------|-------------------------|
| 开发侧载（Dev-sideload） | `IntelligentTerminal_rd9vj3e6a2mbr` |
| 商店正式版（Store） | `Microsoft.IntelligentTerminal_8wekyb3d8bbwe` |

通过 Windows API [`GetCurrentPackageFamilyName`](../../../../../external/libs/intelligent-terminal/tools/wta/src/runtime_paths.rs#L74-L101) 运行时获取，无需编译时同步版本。

---

## 11.4 Per-version 日志目录 `logs\&lt;pkgver&gt;\`

**所有三个写入器共享同一个按版本划分的日志子目录**，版本号是**包版本**（`GetCurrentPackageId`，例如 `0.8.0.2`）：

- Rust 进程：通过 [`logging::log_dir()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L68-L74) 解析
- C++ 端：通过 `IntelligentTerminal::PackageVersionDir()` 解析
- PowerShell hooks：通过 C++/Rust 设置的 `WTA_HOOK_LOG_DIR` 环境变量传入

**为什么按版本隔离？**

1. **无锁清理安全**：当前版本的目录永远不会被删除，多进程并发启动时只会竞争删除旧版本目录，`remove_dir_all` 是幂等的，不需要进程间锁
2. **升级即清理**：升级后首次启动，旧版本日志目录被整体删除，无需逐个文件判断
3. **三个写入器自动对齐**：Rust/C++/PS 在运行时读取同一个包版本，不需要编译时版本同步

非打包环境（dev-from-cargo/测试）无包身份 → 所有日志直接写入扁平的 `logs\` 目录，没有版本子目录。

---

## 11.5 日志目录结构图

### 11.5.1 打包环境完整结构（Production）

```
%LOCALAPPDATA%\Packages\&lt;PackageFamilyName&gt;\
├── LocalState\IntelligentTerminal\                          ← STATE root
│   ├── prompts\
│   │   └── (prompt override files)
│   ├── agent-pane-sessions.jsonl
│   └── master-pipe.txt
│
└── LocalCache\Local\IntelligentTerminal\                    ← LOCAL/cache root
    ├── hooks-upgrade-state.json
    ├── hook-bundle-staging\
    │   └── (hook installer temp files)
    └── logs\
        ├── LogDir (root, no version — used by bug-report zip only)
        └── 0.8.0.2\                                         ← per-version dir (current)
            ├── wta-main_master.log
            ├── wta-main_helper-12345.log
            ├── wta-main_helper-67890.log
            ├── wta-cli.log
            ├── wta-cli.log.2026-08-02
            ├── wta-cli.log.2026-08-01
            ├── wta-delegate.log
            ├── wta-probe.log
            ├── wta-install-hooks.log
            ├── wta-ensure-host.log
            ├── wta-acp-debug.log
            ├── wta-panic.log                    ← (if any panics occurred)
            ├── terminal-agent-pane.log          ← C++ side
            └── hook-trace.log                   ← PowerShell hooks
```

### 11.5.2 非打包环境（Dev builds / Tests）

```
%LOCALAPPDATA%\IntelligentTerminal\             ← BOTH roots collapse here
├── prompts\
├── agent-pane-sessions.jsonl
├── master-pipe.txt
├── hooks-upgrade-state.json
└── logs\                                        ← flat, no version subdir
    └── (same log files as above)
```

---

## 11.6 日志文件清单

以下是 `logs\&lt;pkgver&gt;\` 目录下的所有日志文件：

| 文件名 | 写入方 | 内容说明 | 轮转策略 |
|--------|--------|---------|---------|
| **wta-main_master.log** | Rust (wta-master) | Master 进程生命周期：agent CLI 启动、命名管道 accept 循环、per-helper 路由、`session_to_helper` 映射更新、agent CLI 退出检测、连接失败 | 单文件，进程退出后关闭，不轮转 |
| **wta-main_helper-{pid}.log** | Rust (wta-helper) | 每个 helper 进程独立文件（避免并发交错）：管道连接、ACP initialize、session/new、prompts、agent 响应、TUI 生命周期、连接失败 | 单文件 per-PID，3 天后清理 |
| **wta-cli.log** | Rust (wtcli 短命令) | 短生命周期 wtcli 风格命令（list-*、capture-pane、listen、sessions 等） | **每日轮转**，保留 3 天（`max_log_files=3`） |
| **wta-delegate.log** | Rust (`?&lt;prompt&gt;` 委托) | 后台委托流程（独立于 agent pane 的 `?` 前缀命令） | 单文件 |
| **wta-probe.log** | Rust (`probe-models`) | ACP 模型列表探测 | 单文件 |
| **wta-install-hooks.log** | Rust (`hooks install`) | Agent hook 桥接安装 | 单文件 |
| **wta-ensure-host.log** | Rust (WT 后台) | WT 侧后台 ensure-running 诊断（从 M3-M6 时代保留，SharedWta 生命周期排查依然有用）；常出现在 `%TEMP%` 下 | 单文件 |
| **wta-acp-debug.log** | Rust | 底层 ACP JSON-RPC 线协议追踪（需要显式启用 trace 级别） | 单文件 |
| **wta-panic.log** | Rust (panic hook) | **同步写入**的 panic  backstop（独立于异步 appender），保证致命 panic 也能落盘 | 追加写入，永不轮转 |
| **terminal-agent-pane.log** | C++ (`AgentPaneLog.h`) | C++ 侧 Agent 窗格日志：SharedWta 生命周期、master 退出检测、跨窗口路由事件 | 单文件 |
| **hook-trace.log** | PowerShell (`send-event.ps1`) | PowerShell hooks 事件追踪 | 单文件 |

&gt; **注意**：`terminal-agent-pane.log` 和 `hook-trace.log` 不是 Rust wta 二进制写入的，但它们与 Rust 日志存放在同一个 `logs\&lt;pkgver&gt;\` 目录中，版本清理时会一起删除。

---

## 11.7 日志级别控制

### 11.7.1 环境变量

日志级别通过环境变量控制，优先级如下：

1. **`WTA_LOG`**（WTA 专用，优先）
2. **`RUST_LOG`**（标准 Rust 日志环境变量，fallback）
3. **构建时默认值**（两个都没设置时使用）

### 11.7.2 默认级别

默认级别由构建类型决定（[`default_filter_directive()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L29-L53)）：

| 构建类型 | 默认级别 | 说明 |
|---------|---------|------|
| **Debug 构建** | `debug,agent_client_protocol=info` | 开发时详细日志，但将 `agent_client_protocol` crate 限制在 `info` 级别——这个 crate 在 debug 级别会dump每个 JSON-RPC 消息体，一次 `sessions/list` 轮询就能产生 ~27KB 日志，常规调试会让 master log 膨胀到几 GB |
| **Release 构建** | `info` | 开箱即可追踪生命周期和连接流程，无冗余 debug trace |

### 11.7.3 常用级别设置

```powershell
# 最安静：只显示警告和错误
$env:WTA_LOG="warn"

# Release 构建启用 debug 追踪
$env:WTA_LOG="debug"

# 最详细：启用所有 trace（包括 ACP 线协议）
$env:WTA_LOG="trace"

# 单独打开 agent_client_protocol 的 debug 级别（默认 info 会抑制）
$env:WTA_LOG="debug,agent_client_protocol=debug"

# 只看特定模块
$env:WTA_LOG="info,master=debug,helper=trace"
```

&gt; 💡 **提示**：修改环境变量后需要重启所有 wta 进程（关闭所有 Terminal Dev 窗口，再重新打开）才会生效。日志级别在 `main()` 参数解析后立即初始化，之后不可更改。

### 11.7.4 日志初始化时机

日志在 [`logging::init()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L76-L137) 中初始化，时机是：

1. **main() 入口参数解析之后立即执行**
2. **在 locale/ETW 设置之前**
3. 即使早期启动失败，日志也已经落盘

每个进程启动时，包括短生命周期的 `wtcli` 命令，都会写入日志文件（之前只有 6 个入口点写入，现在所有 launch mode 都写）。

### 11.7.5 退出时日志刷新

非阻塞 appender 的 `WorkerGuard` 保存在全局 `OnceLock&lt;Mutex&lt;Option&lt;WorkerGuard&gt;&gt;&gt;` 中，通过 [`shutdown_flush()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L184-L190) 在每个退出路径显式 drop：

- 正常 main() 结束
- 所有 `std::process::exit` 调用之前
- Console control handler 中（CTRL_CLOSE/CTRL_LOGOFF/CTRL_SHUTDOWN）
- Panic hook 中（额外同步写 panic.log 作为 backstop）

**Console control handler**（[`install_ctrl_handler()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L231-L295)）专门处理 helper 作为 ConPTY 子进程被关闭的场景——此时 OS 会先发控制事件再终止进程，handler 记录是哪个事件导致关闭并刷新日志，避免"helper 突然没反应但日志没记录最后状态"的诊断盲区。

---

## 11.8 日志 retention 策略

日志清理由 [`housekeeping()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L374-L385) 在每次进程启动、打开 appender **之前**执行：

### 11.8.1 按版本目录清理（Per-version cleanup）

[`prune_old_version_dirs()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L395-L411)：

- **只保留当前版本的目录**
- 删除 `logs\` 下所有其他版本子目录（整体 `remove_dir_all`）
- **永不删除当前版本目录** → 无锁、并发安全（多进程竞争删除同一个死目录，幂等）
- 扁平的非目录文件不碰（例如升级前遗留的扁平日志文件）

### 11.8.2 3天轮转策略

1. **Per-PID helper 日志**：[`prune_stale_helper_logs()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L417-L441)
   - 只在 `main_master` 或 `main_helper*` 进程启动时扫描（高频 `cli` 路径不扫描，避免每次命令都扫目录）
   - 删除 mtime 超过 **3天**（`HELPER_RETENTION_DAYS = 3`）的 `wta-main_helper-{pid}.log` 文件
   - 因为 helper 是 per-tab 的，标签页打开/关闭会不断累积新 PID 文件

2. **wta-cli.log 每日轮转**：由 `tracing-appender` 原生处理
   - `Rotation::DAILY` 每日轮转
   - `max_log_files(3)` 保留 3 天的文件
   - 轮转文件命名：`wta-cli.log.YYYY-MM-DD`

### 11.8.3 清理执行时机

| 进程类型 | 执行版本目录清理 | 执行旧 helper 日志清理 |
|---------|----------------|---------------------|
| `wta-main_master` | ✅ 是 | ✅ 是 |
| `wta-main_helper-{pid}` | ✅ 是（无包身份时跳过） | ✅ 是 |
| `wta-cli` | ✅ 是 | ❌ 否（高频路径不扫目录） |
| 其他进程（delegate/probe 等） | ✅ 是 | ❌ 否 |

---

## 11.9 使用 target 字段追踪流程

所有 tracing 事件都带有结构化 `target` 字段和 key=value 上下文。以下是常见排查场景的 grep 模式表：

| 排查目标 | Grep 模式 | 日志文件 | 说明 |
|---------|----------|---------|------|
| Master 进程生命周期 | `target=master` | `wta-main_master.log` | master 启动、停止、关键状态变更 |
| 当前有哪些 helper 连接到 master | `live_helpers=` | `wta-main_master.log` | 连接时数值上升，断开时下降 |
| 某个 SessionId 属于哪个 helper | `step="helper→agent" op="new_session" session_id=` | `wta-main_master.log` | 找到 `session_id=X` 对应的 `helper_id=` |
| **端到端追踪一个 prompt** | `session_id="X"` | master + helper 日志 | 先找 `step="helper→agent" op="prompt"`（发送），再找 `step="master→helper" op="session_notification"`（响应分块） |
| Helper 管道连接生命周期 | `target=master helper_id=` | `wta-main_master.log` | 显示连接建立和退出 |
| Agent CLI stderr 输出 | `target=agent_stderr` | master/helper 日志 | agent CLI 进程的标准错误输出（启动失败、崩溃等） |
| 连接失败（任意一侧） | `"exiting with error"` | master 或 helper 日志 | master 中 target=master，helper 中 target=helper；配合 `step="acp_initialize"` / `step="pipe_connect"` 看 helper 握手阶段 |
| 控制台控制事件（关闭/登出/关机） | `target=lifecycle ctrl_type=` | 任意 wta 日志 | 记录是 CTRL_CLOSE/CTRL_LOGOFF/CTRL_SHUTDOWN 哪个事件导致进程退出 |
| Panic 事件 | `target=panic` | 对应进程日志 + `wta-panic.log` | 包含 message、location、thread name；wta-panic.log 同步写入保证不丢 |
| Hooks 安装/升级决策 | `target=agent_hooks` | `wta-main_master.log` + `wta-install-hooks.log` | `upgrade decision` 行携带 `installed_version`、`bundle_version`、`action` 字段 |
| Copilot hooks 升级 | `target=copilot_hooks` | `wta-main_master.log` | Copilot 专用升级流程追踪 |
| Gemini hooks 升级 | `target=gemini_hooks` | `wta-main_master.log` | Gemini 专用升级流程追踪 |
| Autofix 触发流程 | (看 wta-ensure-host.log) | `wta-ensure-host.log` | 事件流、分类、autofix 触发记录 |
| 内部控制路由 | `target=internal_control` | 对应日志 | 遗留 target，Z 版本后基本为空 |

&gt; **实用技巧**：先确定问题发生在哪个组件（master/helper/cli/C++/hooks），再去对应日志文件用上面的模式 grep。跨组件问题用 `session_id` 串联端到端。

---

## 11.10 端到端 prompt trace 示例

以下是一个用户 prompt 从 helper 发送到 agent CLI，再流式响应返回 helper 的完整日志序列示例（摘自 AGENTS.md）：

```log
[helper]  target=acp_client                      — 管道已连接到 master
[helper]  target=acp_client                      — ACP initialize 已发送
[helper]  target=acp_client                      — session/new → session_id=abc-123
[master]  step=helper→agent op=new_session       — 注册 abc-123 → helper_id=2
[helper]                                        — 用户按下回车，发送 prompt
[master]  step=helper→agent op=prompt            — 转发到 agent CLI (sid=abc-123)
[master]  step=agent→helper kind=agent_message_chunk — agent CLI 流式返回第一个 chunk
[master]  step=master→helper                     — 将 chunk 写回 helper_id=2 的管道
[helper]                                        — chunk 应用到 TabSession.messages
[master]  step=helper→agent op=prompt elapsed_ms=842 stop_reason=…  — 轮次结束
```

**排查口诀**：如果某一步缺失，故障就在上一步。例如：

- 没有 `op=prompt` → helper 根本没发送 prompt（检查 TUI 输入）
- 有 `op=prompt` 但没有 `agent_message_chunk` → agent CLI 没响应（检查 `target=agent_stderr` 看 agent 是否崩溃）
- 有 `agent_message_chunk` 但没有 `master→helper` → master 到 helper 的管道断了（检查 helper 日志的 "exiting with error"）
- 有 `master→helper` 但 helper 没有后续日志 → helper 进程被终止了（检查 `target=lifecycle` ctrl_type）

---

## 11.11 Bug报告日志收集（Report a bug (collect logs)）

提交 Bug 报告时需要收集完整的日志包。

### 11.11.1 日志根目录定位

**打包环境（商店/侧载正式使用）**：

```powershell
# Dev-sideload
$logRoot = "$env:LOCALAPPDATA\Packages\IntelligentTerminal_rd9vj3e6a2mbr\LocalCache\Local\IntelligentTerminal\logs"

# Store (Microsoft.IntelligentTerminal_8wekyb3d8bbwe)
$pfn = Get-AppxPackage Microsoft.IntelligentTerminal | Select-Object -ExpandProperty PackageFamilyName
$logRoot = "$env:LOCALAPPDATA\Packages\$pfn\LocalCache\Local\IntelligentTerminal\logs"
```

**非打包环境（便携版/开发构建）**：

```powershell
$logRoot = "$env:LOCALAPPDATA\IntelligentTerminal\logs"
```

### 11.11.2 快速收集脚本

```powershell
# 1. 先关闭所有 Intelligent Terminal 窗口，确保日志 flush
Get-Process WindowsTerminal -ErrorAction SilentlyContinue | Where-Object {
    $_.Path -like "*IntelligentTerminal*"
} | Stop-Process -Force

# 2. 定位日志根
$pfn = Get-AppxPackage IntelligentTerminal -ErrorAction SilentlyContinue |
    Select-Object -First 1 -ExpandProperty PackageFamilyName
if ($pfn) {
    $logRoot = "$env:LOCALAPPDATA\Packages\$pfn\LocalCache\Local\IntelligentTerminal\logs"
} else {
    $logRoot = "$env:LOCALAPPDATA\IntelligentTerminal\logs"
}

# 3. 打包到桌面 ZIP
$desktop = [Environment]::GetFolderPath("Desktop")
$zipPath = "$desktop\intelligent-terminal-logs-$(Get-Date -Format yyyyMMdd-HHmmss).zip"
Compress-Archive -Path "$logRoot\*" -DestinationPath $zipPath -Force

# 4. 也检查 %TEMP% 下的 wta-ensure-host.log
$tempLog = "$env:TEMP\wta-ensure-host.log"
if (Test-Path $tempLog) {
    $tempDir = "$env:TEMP\it-bug-extra"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    Copy-Item $tempLog $tempDir -Force
    Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Update
    Remove-Item $tempDir -Recurse -Force
}

Write-Host "日志包已生成: $zipPath"
explorer /select,$zipPath
```

### 11.11.3 Bug 报告 ZIP 内容清单

一个完整的 Bug 报告日志包应该包含：

| 内容 | 说明 |
|------|------|
| `&lt;pkgver&gt;\wta-main_master.log` | Master 日志（必选） |
| `&lt;pkgver&gt;\wta-main_helper-*.log` | 出问题的 tab 对应的 helper 日志（看 PID 或时间戳） |
| `&lt;pkgver&gt;\wta-cli.log*` | CLI 命令日志（如使用了 wtcli） |
| `&lt;pkgver&gt;\wta-ensure-host.log` | SharedWta 生命周期日志 |
| `&lt;pkgver&gt;\terminal-agent-pane.log` | C++ 侧日志（必选，包含 window/tab 路由事件） |
| `&lt;pkgver&gt;\hook-trace.log` | PowerShell hooks 日志（如涉及 hooks/shell integration） |
| `%TEMP%\wta-ensure-host.log` | TEMP 下的早期启动诊断日志 |
| `wta-panic.log` | 如果有 panic 发生的话 |
| (设置) `settings.json` | 可选，有助于复现配置相关问题 |

&gt; **UI 入口**：Intelligent Terminal 设置界面应该有 "Report a bug" 或 "Collect logs" 按钮，会自动打包所有版本的日志（使用无版本的 `LogDir()` 根目录，而不是单个版本目录），见 [`IntelligentTerminal::LogDir()`](../../../../../external/libs/intelligent-terminal/src/cascadia/inc/IntelligentTerminalPaths.h)。

---

## 11.12 调试技巧与常见问题

### 11.12.1 实时 tail 日志

开发时最常用的操作——开一个 PowerShell 窗口实时跟踪日志：

```powershell
# 先定位日志目录
$pfn = "IntelligentTerminal_rd9vj3e6a2mbr"  # dev-sideload
$logDir = "$env:LOCALAPPDATA\Packages\$pfn\LocalCache\Local\IntelligentTerminal\logs"
$ver = Get-ChildItem $logDir -Directory | Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 -ExpandProperty Name
$logDir = "$logDir\$ver"

# 实时 tail master 日志
Get-Content "$logDir\wta-main_master.log" -Wait

# 同时看 master + 最新 helper 日志
$latestHelper = Get-ChildItem "$logDir\wta-main_helper-*.log" |
    Sort-Object LastWriteTime -Descending | Select-Object -First 1
Get-Content $latestHelper.FullName -Wait
```

### 11.12.2 快速定位"哪个日志文件对应我的 tab"

每个 tab 对应一个独立的 helper PID：

**方法 1：从 helper 日志找 tab**

```powershell
# 搜索所有 helper 日志中的 initialize 记录，找你打开的时间
Select-String -Path "$logDir\wta-main_helper-*.log" -Pattern "acp_initialize|owner_tab_id|window_id" |
    Select-Object -First 20
```

**方法 2：从 master 日志看 session 映射**

```powershell
# live_helpers 行显示当前所有 helper 连接
Select-String -Path "$logDir\wta-main_master.log" -Pattern "live_helpers=" | Select-Object -Last 1

# new_session 行显示 session 到 helper_id 的映射
Select-String -Path "$logDir\wta-main_master.log" -Pattern "new_session" | Select-Object -Last 5
```

### 11.12.3 启用详细 trace 排查疑难问题

遇到需要看 ACP 线协议或深层逻辑的问题：

```powershell
# 1. 设置环境变量（先关闭所有 IT 窗口）
$env:WTA_LOG="trace"
# 或者只开特定模块的 trace
$env:WTA_LOG="debug,acp_client=trace,master=trace,agent_stderr=trace"

# 2. 从同一个 PowerShell 窗口启动 IT（或 F5 调试）
# 这样启动的 wta 进程继承这个环境变量

# 3. 复现问题

# 4. 查看 wta-acp-debug.log（ACP 线协议）和 wta-main_master.log
```

&gt; ⚠️ **注意**：`trace` 级别日志量极大，复现问题后立即关闭（移除环境变量重启 IT），否则日志文件会快速膨胀到几 GB。

### 11.12.4 常见日志相关问题

**Q: 日志目录在哪里？我找不到 `Packages\IntelligentTerminal_*`？**

A: 确认你安装的是哪个版本：
- 开发侧载：`IntelligentTerminal_rd9vj3e6a2mbr`（后缀是证书的 hash）
- 商店版：`Microsoft.IntelligentTerminal_8wekyb3d8bbwe`
- 便携版：直接在 `%LOCALAPPDATA%\IntelligentTerminal\logs`
- 用 `Get-AppxPackage *IntelligentTerminal*` 命令查找已安装的包

**Q: 为什么我的 debug 日志里没有 ACP JSON-RPC 消息内容？**

A: Debug 默认将 `agent_client_protocol` crate 限制在 `info` 级别（防止日志膨胀）。需要显式启用：
```powershell
$env:WTA_LOG="debug,agent_client_protocol=debug"
```

**Q: wta.exe 从 cargo target 直接运行，日志在哪里？**

A: 没有包身份时 STATE 和 LOCAL 根都回退到 `%LOCALAPPDATA%\IntelligentTerminal\`，日志直接在 `logs\` 下（没有版本子目录）。注意：这种方式运行会有 `0x80073D54` COM 错误，COM 功能（autofix、agent pane、wtcli）无法正常工作，仅用于早期启动调试。

**Q: helper 日志里最后几行经常丢失，看不到怎么退出的？**

A: 正常情况下这是因为：
1. wta-master 被 Job Object `KILL_ON_JOB_CLOSE` 终止（C++ SharedWta 关闭 job）→ 类似 TerminateProcess，**没有**控制台控制事件，进程来不及 flush
2. 这种情况会在 C++ 端的 `terminal-agent-pane.log` 中记录（"master exited" 相关条目）
3. wta-helper 作为 ConPTY 子进程被关闭时应该能收到 CTRL_CLOSE 事件，如果连这个都没收到，说明是被强杀（Task Manager、taskkill /F、资源耗尽 kill）

检查 `terminal-agent-pane.log` 中 SharedWta 对 master 退出的记录，以及 wta-helper 日志末尾是否有 `target=lifecycle` 的 CTRL_CLOSE 行——有这行说明正常收到了关闭事件并 flush 了。

**Q: 升级后旧版本日志不见了？**

A: 这是**设计行为**——每个版本的日志存在独立子目录，新版本首次启动时 `prune_old_version_dirs` 会删除所有非当前版本的目录。如果需要保留旧版本日志，升级前手动备份整个 `logs\` 目录。

**Q: 日志文件占用空间太大怎么办？**

A:
1. 正常情况下 retention 策略会自动清理：旧版本目录升级即删，helper 日志保留 3 天，cli 日志保留 3 天
2. 如果 trace 级别开太久导致膨胀：关闭 IT → 设置 `WTA_LOG=info` 或删除环境变量 → 重启 IT → 手动删除对应 `logs\&lt;pkgver&gt;\` 下过大的日志文件
3. 不要删除**当前正在使用**的日志文件（wta 进程还开着文件句柄）

**Q: 提交 Bug 时需要所有 helper 日志吗？**

A: 不需要。只需要：
1. 问题发生时间对应的 helper 日志（按文件修改时间排序找最近的几个）
2. wta-main_master.log（必选）
3. terminal-agent-pane.log（必选）
4. 如果涉及 hooks/autofix，对应补充 hook-trace.log 和 wta-ensure-host.log

如果不确定，把整个 `logs\&lt;pkgver&gt;\` 目录打包就行（通常几 MB 到几十 MB，除非开了 trace）。

### 11.12.5 日志相关源码速查

| 功能 | 文件 | 关键函数/行 |
|------|------|-----------|
| 路径解析（STATE/LOCAL root） | [`runtime_paths.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/runtime_paths.rs) | `intelligent_terminal_root()`、`intelligent_terminal_local_root()`、`resolve_root()` |
| 日志初始化与 appender 配置 | [`logging.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs) | `init()`、`log_dir()`、`package_version()` |
| 日志级别默认值 | [`logging.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L29-L53) | `default_filter_directive()` |
| Retention/清理策略 | [`logging.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L367-L441) | `housekeeping()`、`prune_old_version_dirs()`、`prune_stale_helper_logs()` |
| 退出 flush 与 panic hook | [`logging.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L175-L365) | `shutdown_flush()`、`install_ctrl_handler()`、`install_panic_hook()` |
| C++ Agent 窗格日志 | [`AgentPaneLog.h`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneLog.h) | C++ 侧日志写入 |
| C++ 路径定义 | [`IntelligentTerminalPaths.h`](../../../../../external/libs/intelligent-terminal/src/cascadia/inc/IntelligentTerminalPaths.h) | `LogDir()`、`LogDirVersioned()`、`PackageVersionDir()` |

---

## 源码溯源

| 来源 | 内容 |
|------|------|
| [`AGENTS.md:178-321 Logs &amp; runtime data layout 章节`](../../../../../external/libs/intelligent-terminal/AGENTS.md#L178-L321) | 双根目录分离、per-version 日志目录、日志文件清单、target grep 表、端到端 trace 示例、日志级别控制 |
| [`runtime_paths.rs:1-183`](../../../../../external/libs/intelligent-terminal/tools/wta/src/runtime_paths.rs#L1-L183) | STATE/LOCAL 双根路径解析、包身份检测、无包身份回退逻辑、log 路径拼接 |
| [`logging.rs:1-519`](../../../../../external/libs/intelligent-terminal/tools/wta/src/logging.rs#L1-L519) | 日志初始化、非阻塞 appender、级别默认值、daily 轮转、housekeeping 清理、per-version 目录删除、3天 helper 日志清理、shutdown flush、ctrl handler、panic hook、单元测试 |
| [`AgentPaneLog.h`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneLog.h) | C++ 侧 terminal-agent-pane.log 写入实现 |
| [`IntelligentTerminalPaths.h`](../../../../../external/libs/intelligent-terminal/src/cascadia/inc/IntelligentTerminalPaths.h) | C++ 侧日志路径定义、包版本读取 |

---

## 本章导航

- [上一章：构建系统与开发环境](10-build-system.md)
- [返回目录](README.md)
- [下一章：配置系统](12-configuration.md)
