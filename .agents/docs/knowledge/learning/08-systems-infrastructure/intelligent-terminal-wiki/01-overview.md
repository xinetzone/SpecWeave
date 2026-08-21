---
id: "intelligent-terminal-ch01-overview"
title: "第1章 - 项目概述与快速开始"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第1章 项目概述与快速开始

## 1.1 Intelligent Terminal 是什么

Intelligent Terminal 是 [Windows Terminal](https://github.com/microsoft/terminal) 的实验性分支（experimental fork），具备原生 Agent 集成能力。

**与 Windows Terminal 的关系：**
- Intelligent Terminal 保留了 Windows Terminal 所有用户喜爱的功能：标签页、配置文件、主题、设置、Shell、键盘快捷键等，这些功能的使用方式与原版完全一致
- Intelligent Terminal 作为独立应用安装，与现有 Windows Terminal 并存，不会破坏原有 Windows Terminal 的工作流
- 如果用户不需要终端中的 Agent 功能，原有体验不会发生任何变化

**AI 原生定位：**
- Intelligent Terminal 可与任何兼容 [Agent Client Protocol (ACP)](https://agentclientprotocol.com/get-started/agents) 的 Agent CLI 协同工作
- 默认集成 GitHub Copilot CLI，用户只需在 PC 上安装偏好的 Agent CLI 即可使用
- Agent 具备 Shell 输出上下文感知能力，无需手动复制粘贴即可理解终端环境

> 来源：[README.md §What is Intelligent Terminal?](../../../../../external/libs/intelligent-terminal/README.md#L39-L48)

## 1.2 核心特性详解

### Agent Pane（Agent 窗格）

Agent Pane 是一个上下文感知的可停靠窗格，集成用户选择的 Agent CLI。该窗格可感知所有 Shell（PowerShell、Bash/WSL）的输出上下文。

- 支持多窗格激活时的焦点指示，当前 Agent 聚焦的窗格会显示 "Agent" 指示器
- Agent 需要执行多个或复杂任务时，会在新标签页中启动后台任务，保持当前活跃 Shell 专注
- 内置 Slash Commands（斜杠命令）支持快速操作

> 来源：[README.md §Agent Pane](../../../../../external/libs/intelligent-terminal/README.md#L135-L169)

### Autofix（自动修复）

Autofix 功能可检测其他窗格中的命令失败，并通过 Agent 自动建议修复方案。

**工作流程：**
1. Shell 发送 `OSC 133;D;<exit_code>` 序列标记命令退出
2. TerminalPage 触发 `ProtocolVtSequenceReceived` 事件
3. COM 服务器转发给客户端
4. WTA（通过 `wtcli listen --json`）进行分类
5. 调用 `maybe_trigger_autofix()` 触发自动修复

**要求：**
- PowerShell Shell 集成（OSC 133 标记）
- ACP 会话已达到 `Connected` 状态的 helper
- PATH 中存在 `wtcli`

> 注意：窗格无需可见——每个标签页预启动的 helper 使得 Autofix 可在隐藏窗格上工作。

> 来源：[AGENTS.md §Autofix](../../../../../external/libs/intelligent-terminal/AGENTS.md#L111-L130)、[README.md §Error Detection](../../../../../external/libs/intelligent-terminal/README.md#L179-L185)

### wtcli

WTCLI 是一个命令行客户端，通过 `CoCreateInstance(CLSCTX_LOCAL_SERVER)` 消费 `IProtocolServer` 接口。Agent 通过调用 wtcli 命令控制终端，例如：
- `wtcli list-panes` - 列出所有窗格
- `wtcli capture-pane` - 捕获窗格内容
- `wtcli listen --json` - 监听事件（JSON 格式）

> 来源：[AGENTS.md §Core Components](../../../../../external/libs/intelligent-terminal/AGENTS.md#L7-L13)

### Session Management（会话管理）

Agent Management 面板允许用户：
- 查看所有活跃 Agent 及其状态
- 查看历史会话
- 从离开的地方继续工作流
- 检查长时间运行的任务状态

点击状态栏中的 Agent 管理图标或按 `Ctrl+Shift+/` 即可打开。

> 来源：[README.md §Agent Management](../../../../../external/libs/intelligent-terminal/README.md#L171-L177)

### wt-agent-hooks

wt-agent-hooks 是随 Intelligent Terminal 打包的插件，需要安装到用户已选择加入的 Agent CLI 中。

**自动升级机制：**
- 安装或升级 IT 时，捆绑的 wt-agent-hooks 插件需要重新部署到用户已安装的 Agent CLI
- 由 `agent_hooks_installer::upgrade_installed_hooks` 静默处理，在每次 `wta-master` 启动时在阻塞池线程上触发一次
- 采用捆绑版本作为升级信号：状态文件记录每个 CLI 上次看到的捆绑版本，版本不匹配时才执行升级流程
- **仅 opt-in（选择加入）**：即使缓存未命中，未安装 wt-agent-hooks 的 CLI 会被跳过，自动升级永远不会安装到用户未接受的 CLI 中
- 支持的 CLI：Copilot、Claude、Gemini，各自有对应的升级策略

> 来源：[AGENTS.md §Hooks plugin auto-upgrade](../../../../../external/libs/intelligent-terminal/AGENTS.md#L132-L176)

## 1.3 安装方式

> **系统要求**：Intelligent Terminal 需要 Windows 10 2004（19041）或更高版本。还需要支持的 Agent CLI 和订阅，默认为 GitHub Copilot。

### Microsoft Store（推荐）

从 [Microsoft Store](https://apps.microsoft.com/detail/9NMQC2SSJX24) 安装 Intelligent Terminal。此方式支持自动升级，始终保持最新版本。

> 来源：[README.md §Microsoft Store](../../../../../external/libs/intelligent-terminal/README.md#L56-L60)

### WinGet 命令

[winget](https://github.com/microsoft/winget-cli) 用户可通过安装 `Microsoft.IntelligentTerminal` 包下载并安装最新版本：

```powershell
winget install --id Microsoft.IntelligentTerminal -e
```

> 来源：[README.md §WinGet](../../../../../external/libs/intelligent-terminal/README.md#L62-L70)

### 手动下载

| 分发格式 | 架构 | 链接 |
|---------|:----:|------|
| App Installer | x64, arm64, x86 | [下载](https://github.com/microsoft/intelligent-terminal/releases/latest) |

> 来源：[README.md §Downloads](../../../../../external/libs/intelligent-terminal/README.md#L72-L77)

## 1.4 首次使用指南

1. **首次启动选择 Agent**：Intelligent Terminal 会自动检测机器上多个兼容 ACP 的 Agent CLI（Copilot/Claude/Codex/Gemini/OpenCode）。如果未找到任何 Agent，默认使用 GitHub Copilot CLI 并通过 WinGet 自动安装。

2. **认证登录**：如果尚未认证，Agent Pane 会引导完成登录流程。

3. **开始使用**：开始提问并使用 Agent Pane 获取帮助。Agent 具备 Shell 输出上下文，无需复制粘贴。

> **PowerShell 执行策略提示**：如果在 PowerShell 中看到 "running scripts is disabled on this system" 或 `UnauthorizedAccess` 错误，说明执行策略阻止了配置文件加载，Intelligent Terminal 无法初始化 Shell 集成。运行以下命令修复：
> ```powershell
> Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
> ```

> 来源：[README.md §Get Started](../../../../../external/libs/intelligent-terminal/README.md#L81-L92)

## 1.5 键盘快捷键速查表

所有快捷键均可通过 Intelligent Terminal 设置自定义。

### 全局快捷键

| 快捷键 | 功能 |
|--------|------|
| <kbd>Ctrl+Shift+.</kbd> | 打开/关闭 Agent Pane（切换显示状态） |
| <kbd>Ctrl+Shift+I</kbd> | 切换焦点到/离开 Agent Pane |
| <kbd>Ctrl+Alt+.</kbd> | 带错误上下文打开 Agent Pane（手动触发 Autofix） |
| <kbd>Ctrl+Shift+/</kbd> | 打开 Agent 管理（会话管理） |
| <kbd>Alt+Shift+/</kbd> | 在提示模式下打开命令面板 |
| <kbd>Alt+Shift+B</kbd> | 打开无启动提示的交互式委托 Agent 标签页 |

### Agent Pane 内斜杠命令

在 Agent Pane 内输入 `/` 可查看可用命令，输入 `/help` 可随时显示命令列表。

| 命令 | 功能 |
|------|------|
| `/help` | 显示命令列表 |
| `/clear` | 清除聊天回滚（保留当前会话） |
| `/new` | 启动新的 Agent 会话（清除历史） |
| `/fix [hint]` | 诊断活跃终端并建议修复；可添加可选提示引导（如 `/fix the path looks wrong`） |
| `/restart` | 以干净会话重启 Agent |
| `/stop` | 取消正在进行的提示 |
| `/sessions` | 打开 Agent 管理（同 <kbd>Ctrl+Shift+/</kbd>） |
| `/agent [id]` | 选择此标签页的 Agent 源；在 WSL 窗格中，选择器包含 Windows 和该 WSL 发行版中安装的 Agent |
| `/model [id]` | 选择此窗格的模型；不带参数的 `/model` 打开选择器，`/model <id>` 直接切换 |

> 来源：[README.md §Keyboard Shortcuts](../../../../../external/libs/intelligent-terminal/README.md#L96-L108)、[README.md §Slash Commands](../../../../../external/libs/intelligent-terminal/README.md#L149-L163)

## 1.6 配置项概览

所有配置均可通过 Intelligent Terminal 设置中的 "Agent" 设置进行配置。

### settings.json 中 Agent 相关配置

| 配置项 | 说明 | 可选值 |
|--------|------|--------|
| `acpAgent` | Agent 选择 | `"copilot"`（默认）、`"gemini"`、或 `"custom:<cmd>"` |
| `acpModel` | 模型覆盖 | 字符串，默认为空 |
| `acpCustomCommand` | 自定义 Agent 命令 | 字符串，默认为空 |
| `agentPanePosition` | Agent Pane 位置 | `"top"`、`"bottom"`（默认）、`"left"`、`"right"` |
| `delegateAgent` | `?<prompt>` 委托使用的 Agent | `"copilot"`（默认）或其他 ACP 兼容 Agent |
| `delegateModel` | 委托模型覆盖 | 字符串，默认为空 |
| `delegateCustomCommand` | 委托自定义命令 | 字符串，默认为空 |
| `autoFixEnabled` | 是否启用自动修复 | `true`（默认）/`false` |
| `aiIntegration.coordinator.enabled` | 协调器是否启用 | `false`（默认）/`true` |
| `aiIntegration.coordinator.commandline` | 协调器命令行 | `"wta"`（默认） |
| `aiIntegration.confirmation.readOperations` | 读操作确认策略 | `"auto"`（默认） |
| `aiIntegration.confirmation.createOperations` | 创建操作确认策略 | `"auto"`（默认） |
| `aiIntegration.confirmation.inputOperations` | 输入操作确认策略 | `"auto"`（默认） |

### 设置界面可配置项

- **Agent and model**：GitHub Copilot（默认）或任何 ACP 兼容 Agent CLI，包括自定义或本地 Agent。Agent Pane 和命令面板可分别配置。每个 Agent Pane 也可通过 `/model` 随时覆盖其模型；更改全局设置会覆盖所有窗格。
- **Pane placement**：窗格位置（Top/Bottom/Left/Right）
- **Error detection**：允许 Intelligent Terminal 自动检测命令失败
- **Error suggestions**：允许 Intelligent Terminal 自动将检测到的错误发送给 Agent 获取修复建议
- **Agent session tracking (hooks)**：允许 Intelligent Terminal 在会话管理 UI 中跟踪活跃 Agent 会话及其状态

> 来源：[AGENTS.md §Settings](../../../../../external/libs/intelligent-terminal/AGENTS.md#L26-L45)、[README.md §Configuration](../../../../../external/libs/intelligent-terminal/README.md#L111-L122)

## 1.7 数据隐私说明

Intelligent Terminal 是一个**本地传输层**。它通过 stdio/ACP 将用户的提示和 Shell 上下文传递给选定的 Agent CLI。Intelligent Terminal 本身不调用任何云 API，也不持久化对话历史，但诊断日志可能写入磁盘，遥测数据可能按如下所述发送。

### 通过 Terminal 传输的数据

- 用户的提示（在 Agent Pane 或命令面板中输入的内容）
- Shell 输出上下文（与 Agent 共享以获取上下文的最近命令输出）
- 基本环境元数据（Shell 类型、OS 版本）

所有这些数据仅在活跃会话期间保存在内存中，会话结束时即被丢弃。

### 数据去向取决于 Agent CLI

| Agent CLI | 数据路由 | 条款 |
|-----------|----------|------|
| [GitHub Copilot](https://github.com/features/copilot/cli/)（默认） | GitHub 后端 | [GitHub Copilot Trust Center](https://resources.github.com/copilot-trust-center/)。符合条件的计划适用企业保护（如零数据保留）。 |
| 第三方或自定义 Agent CLI | 由 Agent 供应商决定 | 受该供应商条款约束，而非 Microsoft 或 GitHub 协议。 |

> **注意**：Terminal 无法保证第三方 Agent CLI 的数据保护。选择 Agent 时，即选择了数据的去向。使用前请查看 Agent 供应商的隐私政策。

### 控制选项

- 可随时在 Settings > Agent 中选择 Agent CLI
- 禁用自动错误检测以防止 Shell 输出被自动检测
- Intelligent Terminal 在代表用户在 Shell 中运行命令前始终会请求确认

Intelligent Terminal 仅收集使用数据并发送给 Microsoft 以帮助改进产品和服务。请阅读[隐私声明](https://go.microsoft.com/fwlink/?LinkID=824704)了解更多信息。有关如何禁用遥测的详细信息和说明，请参阅 PRIVACY.md。

> 来源：[README.md §Data & Privacy](../../../../../external/libs/intelligent-terminal/README.md#L197-L229)

---

## 本章导航

- [返回目录](README.md)
- [下一章：整体架构设计](02-architecture.md)
