---
id: "intelligent-terminal-ch08-hooks"
title: "第8章 - wt-agent-hooks Shell 集成"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第8章 wt-agent-hooks Shell 集成

`wt-agent-hooks` 是 Windows Terminal Agent (WTA) 的插件/扩展捆绑系统，负责将各类 Agent CLI（Copilot、Claude、Gemini、Codex、OpenCode）的生命周期事件通过钩子桥接到 Windows Terminal COM 服务器，实现跨窗格的 Agent 会话实时追踪、工具调用可视化和 Autofix 自动修复触发。

---

## 8.1 wt-agent-hooks 概述

### 8.1.1 插件系统定位

wt-agent-hooks 在 WTA 架构中扮演**事件采集层**的角色：它不是一个独立进程，而是一套静态插件/扩展文件，被各个 Agent CLI 在钩子触发时加载执行，通过 PowerShell 桥接脚本将事件转发给 `wtcli send-event`，最终经由 COM 协议到达 wta-master 的会话注册表。

**核心设计原则**：

| 原则 | 实现方式 |
|------|----------|
| **单一可信源** | 所有可安装内容完全位于 `tools/wta/wt-agent-hooks/` 目录，运行时不生成 JSON、不嵌入文件到 wta.exe |
| **CLI 自管理** | 始终通过各 CLI 自身的插件市场命令（`plugin marketplace add` / `extensions install`）注册，永不直接编辑 settings.json |
| **幂等安全** | 启动时自动安装是最佳努力（best-effort），失败仅打 warn 日志，永不崩溃启动 |
| **字节一致** | 所有 CLI 的 `send-event.ps1` 字节完全相同，单元测试强制校验 |
| **无副作用** | 钩子脚本必须无条件退出码 0，禁止向 stdout/stderr 输出任何内容 |

> **源码来源**：[`tools/wta/wt-agent-hooks/README.md:1-45`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/README.md#L1-L45)、[`tools/wta/src/agent_hooks_installer.rs:1-101 模块文档`](../../../../../external/libs/intelligent-terminal/tools/wta/src/agent_hooks_installer.rs#L1-L101)

### 8.1.2 支持的 Agent CLI 列表

wt-agent-hooks 当前支持 5 种主流 Agent CLI，采用 per-CLI 独立子树结构：

| CLI | 安装命令 | 插件目录名 | 钩子数量 | 特殊说明 |
|-----|----------|-----------|----------|----------|
| **Copilot CLI** | `copilot plugin marketplace add` + `copilot plugin install` | `copilot/` | 10 events | ACP 模式下不触发插件钩子（仅交互模式生效） |
| **Claude Code** | `claude plugin marketplace add` + `claude plugin install` | `claude/` | 10 events | 两级目录嵌套（marketplace → plugin） |
| **Gemini CLI** | `gemini extensions install --consent --skip-settings` | `gemini-extension/` | 7 events | 需要 `GEMINI_CLI_TRUST_WORKSPACE=true` 环境变量 |
| **Codex CLI** | `codex plugin marketplace add` + `codex plugin add` | `codex/` | 10 events | 安装后需在 Codex 内运行 `/hooks` 信任插件 |
| **OpenCode** | 直接文件复制（无插件市场） | `opencode/` | V1 plugin API | 使用托管标记防止覆盖用户同名插件 |

> **来源**：[`tools/wta/src/agent_hooks_installer.rs:173-267 CliKind 枚举`](../../../../../external/libs/intelligent-terminal/tools/wta/src/agent_hooks_installer.rs#L173-L267)

---

## 8.2 支持的 Agent CLI

### 8.2.1 Claude Code 与 Copilot CLI（插件市场模式）

Claude 和 Copilot 共享相同的插件清单格式和钩子模式，仅 `-CliSource` 参数不同（单元测试强制两者 parity）。安装流程采用两步法：

1. **marketplace add**：向 CLI 注册本地插件源目录
2. **plugin install**：从已注册的 marketplace 安装插件到用户目录

**Claude/Copilot 钩子事件映射**：

| WTA 事件主题 | Claude 钩子 | Copilot 钩子 |
|--------------|-------------|--------------|
| `agent.session.start` | `SessionStart` | `SessionStart` |
| `agent.session.end` | `SessionEnd` | `SessionEnd` |
| `agent.notification` | `Notification` | `Notification` |
| `agent.prompt.submit` | `UserPromptSubmit` | `UserPromptSubmit` |
| `agent.tool.starting` | `PreToolUse` | `PreToolUse` |
| `agent.tool.finished` | `PostToolUse` | `PostToolUse` |
| `agent.tool.failed` | `PostToolUseFailure` | `PostToolUseFailure` |
| `agent.error` | `StopFailure` | `StopFailure` |
| `agent.stop` | `Stop` | `Stop` |
| `agent.subagent.stop` | `SubagentStop` | `SubagentStop` |

> **注意**：Claude 的 `StopFailure` 是官方文档中记载的"API 错误导致轮次结束"事件名，早期 wta 版本使用的未文档化 `ErrorOccurred` 已废弃。

### 8.2.2 Gemini CLI（扩展模式）

Gemini 没有插件市场概念，直接使用 `extensions install` 命令安装扩展目录。Gemini 的钩子事件集相对精简：

| WTA 事件主题 | Gemini 钩子 |
|--------------|-------------|
| `agent.session.start` | `SessionStart` |
| `agent.session.end` | `SessionEnd` |
| `agent.notification` | `Notification` |
| `agent.prompt.submit` | `BeforeAgent` |
| `agent.tool.starting` | `BeforeTool` |
| `agent.tool.finished` | `AfterTool` |
| `agent.stop` | `AfterAgent` |

Gemini 不原生支持 `PostToolUseFailure` 和 `StopFailure` 等价事件，因此失败类事件在 Gemini 上静默。

### 8.2.3 Codex CLI（插件市场模式）

Codex CLI 采用与 Claude/Copilot 类似的插件市场模式，但子命令命名有差异：
- 使用 `codex plugin add` 而非 `plugin install`
- 使用 `codex plugin remove` 而非 `plugin uninstall`
- Marketplace 元数据位于 `.agents/plugins/marketplace.json`（而非 `.claude-plugin/`）

安装完成后，用户必须在 Codex 交互界面内运行 `/hooks` 命令来信任插件，事件才会触发。

### 8.2.4 OpenCode（直接文件复制模式）

OpenCode 没有独立的钩子市场机制，采用 V1 JavaScript 插件 API。`wta hooks install --cli opencode` 直接将文件复制到用户插件目录：

| 文件 | 目标路径 |
|------|----------|
| `wt-agent-hooks.js` | `%XDG_CONFIG_HOME%\opencode\plugins\wt-agent-hooks.js` |
| `send-event.ps1` | `%XDG_CONFIG_HOME%\opencode\plugins\wt-agent-hooks\send-event.ps1` |
| `plugin.json` | `%XDG_CONFIG_HOME%\opencode\plugins\wt-agent-hooks\plugin.json` |

OpenCode 插件映射以下事件到 WTA 统一主题：`session.created/updated`、`chat.message`、`tool.execute.before/after`、`permission.*`、`question.*`、`session.idle/error/deleted`、`dispose`。带有 `parentID` 的子会话被忽略，防止内部子代理创建额外行。

**安全机制**：复制前检查目标 JS 文件是否包含 `Managed by Intelligent Terminal: wt-agent-hooks` 标记，拒绝覆盖非托管的同名插件。

> **来源**：[`tools/wta/wt-agent-hooks/README.md:96-124 Event vocabulary`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/README.md#L96-L124)

---

## 8.3 Hooks 插件结构

### 8.3.1 目录布局

wt-agent-hooks 目录采用 per-CLI 自包含子树设计，每个子树原封不动地传递给对应 CLI 的市场/扩展命令：

```
wt-agent-hooks/
├── claude/                                 # → claude plugin marketplace add
│   ├── .claude-plugin/marketplace.json     # 市场声明：source 指向 wt-agent-hooks/
│   └── wt-agent-hooks/                     # Claude 复制到 ~/.claude/ 的插件文件夹
│       ├── .claude-plugin/plugin.json      # 插件元数据
│       └── hooks/
│           ├── hooks.json                  # 10 个事件定义，-CliSource claude
│           └── send-event.ps1              # 所有 CLI 字节一致
├── copilot/                                # → copilot plugin marketplace add
│   └── (与 claude/ 布局相同，仅 -CliSource 不同)
├── codex/                                  # → codex plugin marketplace add
│   ├── .agents/plugins/marketplace.json    # Codex 强制哨兵位置
│   └── wt-agent-hooks/
│       ├── .codex-plugin/plugin.json
│       └── hooks/
│           ├── hooks.json
│           └── send-event.ps1
├── gemini-extension/                       # → gemini extensions install
│   ├── gemini-extension.json               # 扩展清单
│   └── hooks/
│       ├── hooks.json                      # 7 个事件，-CliSource gemini
│       └── send-event.ps1
├── opencode/                               # 直接复制到 ~/.config/opencode/plugins/
│   ├── plugin.json                          # 托管 bundle 版本
│   ├── wt-agent-hooks.js                    # OpenCode V1 插件
│   └── send-event.ps1
└── hook-debug/                             # 开发工具，不属于安装 bundle
    └── state-logger.ps1
```

> **为什么两级嵌套？** Claude/Copilot 的 `marketplace add` 读取 `<source>/.claude-plugin/marketplace.json`，其中声明 `"source": "./wt-agent-hooks"`，然后 CLI 将 `<source>/wt-agent-hooks/`（内部插件文件夹）复制到用户可写插件目录。磁盘结构镜像了 CLI 的期望：外层 market 文件夹通过相对路径指向内层 plugin 文件夹。Gemini 没有 market 概念，直接读取扩展文件夹。

### 8.3.2 plugin.json / gemini-extension.json

插件清单文件声明插件名称、版本、入口点等元数据。以 Claude 的 `plugin.json` 为例：

```json
{
  "name": "wt-agent-hooks",
  "version": "1.0.0",
  "description": "Windows Terminal Agent hooks bridge",
  "hooks": "./hooks/hooks.json"
}
```

关键常量（在 Rust 安装器中硬编码）：
- `PLUGIN_NAME = "wt-agent-hooks"` — 插件名称，必须与 plugin.json 的 `name` 字段一致
- `MARKETPLACE_NAME = "wt-local"` — kebab-case 市场名（Copilot 拒绝下划线，早期 `_direct` 导致插件永不加载）

### 8.3.3 hooks.json

钩子定义文件声明要监听的事件和对应的命令。每个条目包含 `matcher`（正则匹配，`.*` 表示所有）和 `hooks` 数组：

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": ".*",
        "hooks": [{
          "type": "command",
          "command": "powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File \"${CLAUDE_PLUGIN_ROOT}/hooks/send-event.ps1\" -CliSource claude agent.session.start"
        }]
      }
    ]
  }
}
```

**关键参数**：
- `-NoProfile -NonInteractive`：不加载用户 PowerShell profile，保证执行速度和一致性
- `-ExecutionPolicy Bypass`：绕过执行策略限制
- `-CliSource <name>`：**唯一可靠的 CLI 来源标识**（环境变量启发式不可靠，因为 Copilot 继承 Claude 的插件形状并设置 `CLAUDE_PLUGIN_ROOT`）
- 位置参数 `agent.session.start`：事件类型

> **源码来源**：[`tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/hooks.json`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/hooks.json)

### 8.3.4 send-event.ps1（桥接脚本）

`send-event.ps1` 是所有 CLI 共用的 PowerShell 桥接脚本，字节完全一致。它的职责是：

1. **退出码契约**：无条件 `exit 0`，通过顶部 `trap { exit 0 }` 和外层 try/catch 双重保障
   - 退出码 2 → 阻塞工具调用 / 擦除用户提示 / 强制越过 Stop
   - 其他非零 → 在 transcript 中显示 hook 错误
2. **标准输出纪律**：不向 stdout/stderr 写任何内容（防止 token 泄漏和 prompt 注入）
3. **诊断日志**：仅写入 `%LOCALAPPDATA%\IntelligentTerminal\logs\hook-trace.log`
4. **事件包装**：从 stdin 读取钩子 JSON，包装为统一格式：
   ```powershell
   @{
     cli_source       = $cliSource
     agent_session_id = $agentSessionId
     payload          = $parsed
   }
   ```
5. **字段裁剪**：移除大字段（tool_result、prompt、transcript、messages 等）防止 CreateProcess argv 溢出（Windows 限制约 32768 字符）
6. **异步分发**：通过 `UseShellExecute = $true` 启动 wtcli，使父 PowerShell 立即退出不等待 COM 往返
7. **窗格绑定**：通过 `-p $env:WT_SESSION` 传递窗格 GUID，确保事件路由到正确窗格

> **源码来源**：[`tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/send-event.ps1`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/send-event.ps1)

---

## 8.4 PowerShell Shell Integration（OSC 133 marks 工作原理）

### 8.4.1 FinalTerm OSC 133 序列

OSC 133（FinalTerm Command Status）是终端 Shell 集成的行业标准序列，Windows Terminal 内部完整实现了该协议，用于标记命令的生命周期边界：

| 序列 | 含义 | 触发时机 |
|------|------|----------|
| `ESC ] 133 ; A ST` | **Prompt Start** — 命令提示符开始 | Shell 显示 prompt 前 |
| `ESC ] 133 ; B ST` | **Command Start** — 命令执行开始 | 用户按下 Enter 后 |
| `ESC ] 133 ; C ST` | **Command Output Start** | 命令开始产生输出前 |
| `ESC ] 133 ; D ; <exitcode> ST` | **Command Finish** — 命令完成，携带退出码 | 命令退出后 |

Windows Terminal 内部处理流程：

```
Shell 发送: ESC]133;D;1 ST
  → adaptDispatch.cpp:3688 (DoFinalTermAction, case 'D')
  → 解析退出码字符串
  → textBuffer.cpp:3501 (EndCurrentCommand(error=1))
  → Row.cpp:1271 (EndOutput 设置 exitCode=1, category=Error)
  → ScrollbarData 存储在 prompt 行上
```

退出码存储在 `ScrollbarData.exitCode`，category 映射规则：0 = `Success`，非 0 = `Error`。

> **来源**：[`terminal-acp-shell-integration.md:227-240 OSC 133;D 流水线`](../../../../../external/libs/intelligent-terminal/tools/wta/terminal-acp-shell-integration.md#L227-L240)

### 8.4.2 PowerShell Shell Integration 注入

Windows Terminal 为 PowerShell 提供自动 Shell Integration 注入。PowerShell 配置文件通过 `PowerShellShellIntegration.h` 中定义的钩子注入 FTCS 序列：

- **OSC 9;9**：CWD 通知（ConEmu 格式，PowerShell 原生支持）
- **OSC 133 A/B/C/D**：命令标记，包括退出码
- **OSC 9001;ShellType**：Shell 类型自报告（pwsh/powershell）

注入后的 PowerShell prompt 函数会在适当的时机发出这些序列，使得即使没有 Agent CLI 钩子，Windows Terminal 也能追踪命令执行状态。

### 8.4.3 退出码与 Autofix 的关联

OSC 133;D 携带的退出码是 Autofix 功能的核心触发信号。当 PowerShell Shell Integration 启用时：

1. 每个命令完成后 shell 发送 `OSC 133;D;<exitcode>`
2. TerminalCore 解析序列并将退出码存储在 ScrollbarData
3. `CommandCompleted` 事件（计划中）或标记扫描将退出码传递给 wta
4. 当退出码 ≠ 0 时，触发 Autofix 链路分析错误并提供修复建议

> **注意**：cmd.exe 无法发送 OSC 133;D（没有 post-command 钩子机制），因此 cmd.exe 中的命令错误无法被可靠检测，降级为文本启发式（高误报率）。

> **来源**：[`terminal-acp-shell-integration.md:319-329 Shell 错误检测矩阵`](../../../../../external/libs/intelligent-terminal/tools/wta/terminal-acp-shell-integration.md#L319-L329)

---

## 8.5 Hooks 自动升级机制

### 8.5.1 自动安装入口点

`wta.exe` 启动时通过 `agent_hooks_installer::ensure_installed()` 自动为所有检测到的 CLI 安装/更新 hooks。这是一个幂等操作——每次 wta 启动都会运行，失败时静默跳过。

### 8.5.2 Bundle 版本解析链

安装器按以下优先级链查找 `wt-agent-hooks/` bundle 目录（首次命中获胜）：

1. **`WTA_HOOKS_BUNDLE_DIR` 环境变量** — 显式覆盖（最高优先级，供分销商无需重编译即可 patch bundle）
2. **`<wta.exe 所在目录>/wt-agent-hooks/`** — MSIX 包将 bundle 部署在 wta.exe 旁边（由 `CascadiaPackage.wapproj` 的 Content glob 配置）
3. **向上遍历父目录查找 `tools/wta/wt-agent-hooks/`** — 开发树回退，用于 `cargo build` 运行
4. **无嵌入回退** — 如果以上都未找到，打 warn 日志并跳过（不使用 `include_str!` 嵌入，因为打包构建中 bundle 缺失是构建/部署 bug，应该暴露而非掩盖）

```mermaid
flowchart TD
    Start([wta 启动]) --> Ensure[ensure_installed()]
    Ensure --> HomeCheck{HOME/USERPROFILE 存在?}
    HomeCheck -->|否| Skip[跳过安装]
    HomeCheck -->|是| Loop[遍历 CliKind::ALL]
    
    Loop --> CheckCLI{CLI 二进制在 PATH?}
    CheckCLI -->|否| NextCLI[下一个 CLI]
    CheckCLI -->|是| Cleanup[清理遗留/陈旧条目]
    
    Cleanup --> ResolveBundle[解析 Bundle 目录]
    ResolveBundle --> EnvCheck{WTA_HOOKS_BUNDLE_DIR 设置?}
    EnvCheck -->|是| EnvPath[使用环境变量路径]
    EnvCheck -->|否| ExeSibling{wta.exe 旁有 wt-agent-hooks/?}
    ExeSibling -->|是| ExePath[使用 exe-sibling 路径]
    ExeSibling -->|否| DevTree[向上遍历父目录查找 tools/wta/wt-agent-hooks/]
    
    EnvPath --> StageCheck{在 WindowsApps 下?}
    ExePath --> StageCheck
    DevTree --> Found{找到?}
    Found -->|否| WarnBundle[打 warn 日志: 无 bundle]
    Found -->|是| StageCheck
    WarnBundle --> NextCLI
    
    StageCheck -->|是 (Claude/Codex)| Stage[复制到 LOCALAPPDATA hook-bundle-staging]
    StageCheck -->|否| Register[执行 marketplace add]
    Stage --> Register
    
    Register --> AddCmd["<cli> plugin marketplace add <bundle>"]
    AddCmd --> InstallCmd["<cli> plugin install wt-agent-hooks@wt-local"]
    InstallCmd --> LogResult[记录结果到 wta-install-hooks.log]
    LogResult --> NextCLI
    
    NextCLI -->|还有 CLI| Loop
    NextCLI -->|完成| Done([安装完成])
    
    style Start fill:#90EE90
    style Done fill:#90EE90
    style WarnBundle fill:#FFB6C1
    style Skip fill:#D3D3D3
```

> **源码来源**：[`tools/wta/src/agent_hooks_installer.rs:418-569 bundle 模块`](../../../../../external/libs/intelligent-terminal/tools/wta/src/agent_hooks_installer.rs#L418-L569)

### 8.5.3 Per-CLI 安装策略

每个 CLI 有专门的安装函数，处理其独特的命令行参数和清理需求：

| CLI | 安装函数 | 特殊处理 |
|-----|----------|----------|
| **Claude** | `install_for_claude()` | 1) 清理 settings.json 中旧的 wta 标记 hooks 块（防止双重触发）<br>2) WindowsApps EPERM 问题：从 `\WindowsApps\` 复制到 staging 目录再安装（Node.js `fs.cpSync` 递归扫描 MSIX 路径失败） |
| **Copilot** | `install_for_copilot()` | 1) 清理陈旧的 wt-local marketplace 条目（工作区移动/重命名导致 path 失效）<br>2) 清理旧的 `_direct/` 目录（Copilot 拒绝下划线市场名时的遗留）<br>3) "already registered" 被视为成功 |
| **Gemini** | `install_for_gemini()` | 1) `--consent --skip-settings` 绕过交互安全同意和配置提示<br>2) `GEMINI_CLI_TRUST_WORKSPACE=true` 绕过文件夹信任提示<br>3) 容忍 "already installed" 和 libuv 崩溃断言（文件已落地即算成功） |
| **Codex** | `install_for_codex()` | 1) 与 Claude 类似的 WindowsApps staging<br>2) 使用 `plugin add` 而非 `install` |
| **OpenCode** | `install_for_opencode()` | 1) 直接文件复制，无 CLI 命令<br>2) 检查托管标记，拒绝覆盖非托管插件<br>3) 原子提交顺序：manifest 最后复制（失败可回滚） |

### 8.5.4 为什么每次启动都重装？

- **MSIX 安装路径包含版本号**：每次升级路径都会变化，旧的 marketplace 条目指向失效路径
- **陈旧路径清理**：开发树移动/重命名、`WTA_HOOKS_BUNDLE_DIR` 变化都会遗留失效条目
- **幂等安全**：`<cli> plugin marketplace add` 对已存在条目静默 no-op；`<cli> plugin install` 也是 exit-0 幂等
- **遗留清理**：每次启动都清理旧版本 wta 留下的 settings.json 直接编辑条目、`_direct/` 目录等

> **来源**：[`tools/wta/wt-agent-hooks/README.md:199-202 Caveats`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/README.md#L199-L202)

---

## 8.6 OSC 133;D 退出码检测 → Autofix 触发链路

### 8.6.1 错误检测置信度模型

WTA/Autofix 采用分层置信度模型决定是否触发自动修复：

| 置信层级 | 置信度 | 信号源 | Agent 行为 |
|----------|--------|--------|------------|
| **Certain** | 95-100% | OSC 133;D 退出码 ≠ 0 | 果断行动："该命令失败了。" |
| **High** | 75-94% | 退出码 + 错误文本模式 | 果断行动并提供细节 |
| **Medium** | 50-74% | autoMarkPrompts + 文本启发式 | "看起来可能有问题。" |
| **Low** | 25-49% | 仅文本模式，无退出码 | 不主动提及，被问到时再回应 |
| **Blind** | 0-24% | TUI/SSH/无标记 | 视为原始文本，绝不猜测 |

### 8.6.2 触发链路完整流程

```mermaid
sequenceDiagram
    participant Shell as Shell (pwsh)
    participant TermCore as TerminalCore
    participant TermControl as TermControl
    participant WTCOM as TerminalProtocolComServer
    participant WTA as wta-master
    participant Autofix as Autofix 模块

    Note over Shell: 用户输入命令并执行
    Shell->>TermCore: OSC 133;B (命令开始)
    Shell->>TermCore: 命令输出...
    Shell->>TermCore: OSC 133;D;1 ST (退出码=1)
    
    TermCore->>TermCore: 解析退出码 → EndCurrentCommand(error=1)
    TermCore->>TermCore: ScrollbarData.exitCode = 1
    TermCore->>TermCore: category = Error
    
    alt CommandCompleted 事件 (已实现)
        TermCore->>WTCOM: 触发 CommandCompleted(exitCode=1)
    else 标记扫描 (当前路径)
        WTA->>WTCOM: wtcli capture-pane --last-prompt
        WTCOM-->>WTA: 输出包含标记信息
    end
    
    Note over WTA: 通过 hook 事件或 OSC 标记收到退出码
    WTA->>WTA: route_one_hook / 处理退出码
    WTA->>Autofix: 触发 Autofix 分析
    
    Note over Autofix: 1) 读取最近命令输出<br/>2) 分析错误类型<br/>3) 生成修复建议<br/>4) 在 Agent 窗格展示
    Autofix-->>WTA: 修复建议/自动修复命令
    WTA->>TermControl: 在 Agent 窗格显示 Autofix 卡片
    
    opt 用户确认修复
        WTA->>WTCOM: wtcli send-keys 注入修复命令
    end
```

### 8.6.3 关键实现要点

1. **Shell Integration 是前提**：Autofix 可靠触发依赖 PowerShell Shell Integration 启用（默认开启 `autoMarkPrompts`），这样才能获得 OSC 133;D 退出码
2. **双路径来源**：
   - **Agent CLI hooks 路径**：Agent 自己运行的工具失败通过 `PostToolUseFailure` 钩子立即通知（Class A 会话）
   - **OSC 133 路径**：用户在普通 shell 窗格运行的命令失败通过 shell integration marks 检测（Class B 会话）
3. **退出码 ≠ 0 是触发必要条件**：文本模式匹配仅作为低置信度补充，不单独触发 Autofix
4. **cmd.exe 无支持**：cmd.exe 无法发出 OSC 133;D，Autofix 在 cmd.exe 中不自动触发

> **来源**：[`terminal-acp-shell-integration.md:307-317 置信度模型`](../../../../../external/libs/intelligent-terminal/tools/wta/terminal-acp-shell-integration.md#L307-L317)、[`tools/wta/src/app/autofix.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/autofix.rs)

---

## 8.7 hook-trace.log 诊断日志

### 8.7.1 日志位置与轮转

`send-event.ps1` 在每次钩子触发时写入诊断日志到：

- **打包运行**：`%LOCALAPPDATA%\Packages\<PFN>\LocalCache\Local\IntelligentTerminal\logs\<pkgver>\hook-trace.log`（通过 `WTA_HOOK_LOG_DIR` 环境变量由 wta-master 传入）
- **解包/开发运行**：`%LOCALAPPDATA%\IntelligentTerminal\logs\hook-trace.log`

**轮转策略**：软 5MB 限制——当文件 ≥ 5MB 时，在下次钩子触发开始时将当前日志移动为 `hook-trace.log.1`（活动日志和 `.1` 备份可能短暂超过 5MB）。

### 8.7.2 日志格式

每次钩子调用写两行（ENTER + DISPATCHED/ERROR），格式：

```
2026-08-03 10:15:30.123 | ENTER cli=claude event=agent.tool.starting envHint=claude wt=a1b2c3d4-e5f6-... pid=12345
2026-08-03 10:15:30.456 | DISPATCHED cli=claude event=agent.tool.starting sessId=a1b2c3d4 wtcli=C:\Program Files\WindowsApps\...\wtcli.exe
```

或错误情况：
```
2026-08-03 10:15:30.789 | ERROR cli=copilot event=agent.session.start ex="wtcli.exe not found"
```

| 字段 | 含义 |
|------|------|
| `cli` | `-CliSource` 参数（claude/copilot/gemini/codex/opencode） |
| `event` | 事件类型（agent.session.start 等） |
| `envHint` | 环境变量启发式猜测的 CLI（辅助诊断） |
| `wt` | `WT_SESSION` 窗格 GUID（`<no-WT_SESSION>` 表示不在 WT 中运行，钩子会提前退出） |
| `pid` | PowerShell 进程 ID |
| `sessId` | agent_session_id 前 8 字符 |
| `wtcli` | 解析到的 wtcli.exe 路径 |
| `TRUNCATED orig=N` | 载荷超过 25000 字符被截断（防止 CreateProcess argv 溢出） |
| `ex=` | 错误消息（换行被替换为空格） |

### 8.7.3 排障指南

| 症状 | 排查位置 |
|------|----------|
| 钩子完全不触发（Claude） | `~/.claude/logs/*.log`（或 `claude --debug`）；搜索 `hook` / `wt-agent-hooks` |
| 钩子完全不触发（Copilot） | `~/.copilot/logs/process-*.log`；验证 `Loaded N hook(s) from M plugin(s)` |
| 钩子完全不触发（Gemini） | `~/.gemini/logs/*.log` 和 `gemini extensions list` |
| 钩子完全不触发（OpenCode） | 验证 `~/.config/opencode/plugins/wt-agent-hooks.js` 包含托管标记 |
| 每次调用的脚本追踪 | `hook-trace.log`——所有 CLI 的每次 `send-event.ps1` 调用一行 |
| 事件未到达 WTA | `wta-ensure-host.log`——搜索 `agent_event` |
| `cli_source` 报告错误 | 检查已安装插件文件夹中的 `hooks.json`——每个命令必须以 `-CliSource <name>` 结尾 |

> **来源**：[`tools/wta/wt-agent-hooks/README.md:167-177 Troubleshooting`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/README.md#L167-L177)、[`tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/send-event.ps1:50-96 日志写入逻辑`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/send-event.ps1#L50-L96)

---

## 源码溯源

| 来源 | 内容 |
|------|------|
| [`tools/wta/wt-agent-hooks/README.md`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/README.md) | wt-agent-hooks 官方文档（目录布局、事件词汇表、安装流程、排障） |
| [`tools/wta/src/agent_hooks_installer.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/agent_hooks_installer.rs) | Rust 自动安装器实现（bundle 解析、per-CLI 安装、状态查询、卸载） |
| [`tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/hooks.json`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/hooks.json) | Claude/Copilot 风格钩子定义示例 |
| [`tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/send-event.ps1`](../../../../../external/libs/intelligent-terminal/tools/wta/wt-agent-hooks/claude/wt-agent-hooks/hooks/send-event.ps1) | PowerShell 桥接脚本（所有 CLI 共用） |
| [`tools/wta/AGENTS.md:180-206 日志章节`](../../../../../external/libs/intelligent-terminal/tools/wta/AGENTS.md#L180-L206) | WTA 日志布局（hook-trace.log 位置说明） |
| [`tools/wta/terminal-acp-shell-integration.md:223-290 OSC 133 章节`](../../../../../external/libs/intelligent-terminal/tools/wta/terminal-acp-shell-integration.md#L223-L290) | OSC 133;D 退出码内部实现流水线 |
| [`tools/wta/src/app/autofix.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/autofix.rs) | Autofix 模块实现（错误分析、修复建议生成） |

---

## 本章导航

- [上一章：wtcli 命令参考](07-wtcli-reference.md)
- [返回目录](README.md)
- [下一章：Autofix 自动修复](09-autofix.md)
