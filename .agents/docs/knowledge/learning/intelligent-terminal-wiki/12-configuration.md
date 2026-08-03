---
id: "intelligent-terminal-ch12-config"
title: "第12章 - 配置与设置详解"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第12章 配置与设置详解

Intelligent Terminal 提供了分层的配置系统，支持全局设置、Profile 级覆盖、组策略（GPO）管控和环境变量调节。所有配置通过 `settings.json` 文件持久化，配合设置 UI 界面进行可视化管理，同时支持企业环境通过 GPO 进行统一管控。

---

## 12.1 配置系统概述

Intelligent Terminal 的配置系统采用四层优先级模型，从高到低依次为：

| 层级 | 位置 | 用途 | 覆盖范围 |
|------|------|------|---------|
| **环境变量** | 进程环境 | 临时调试、日志级别、COM 发现 | 当前进程及其子进程 |
| **GPO 组策略** | Windows 注册表 | 企业级强制管控 | 机器级/用户级，无法被用户配置覆盖 |
| **Profile 级覆盖** | `settings.json` 的 `profiles` 节点 | WSL 等特定发行版专用 Agent | 仅对匹配的 Profile 生效 |
| **全局设置** | `settings.json` 根节点 | 用户默认配置 | 所有 Profile 默认继承 |

**设计原则**：
1. **用户可控**：除 GPO 锁定的设置外，所有配置均可通过设置 UI 或直接编辑 `settings.json` 修改
2. **策略感知**：所有 Agent 相关设置提供 `Effective*` getter，自动应用 GPO 过滤，运行时代码应优先使用这些接口
3. **可扩展**：内置 Agent 列表在编译时注册，同时支持用户通过 `custom:<cmd>` 方案添加自定义 Agent CLI

---

## 12.2 settings.json 配置位置与加载顺序

### 12.2.1 配置文件位置

与 Windows Terminal 一致，`settings.json` 位于 STATE root 目录：

| 环境 | 路径 |
|------|------|
| **打包环境（商店/侧载）** | `%LOCALAPPDATA%\Packages\<PackageFamilyName>\LocalState\settings.json` |
| **非打包环境（开发/便携）** | `%LOCALAPPDATA%\IntelligentTerminal\settings.json` |

&gt; **注意**：`settings.json` 与 WTA 的 STATE root 位于同一目录，与 `prompts\`、`agent-pane-sessions.jsonl` 等持久化数据并列存放。

### 12.2.2 加载顺序

Windows Terminal 启动时按以下顺序加载和合并配置：

1. **默认值**：编译时硬编码在 `MTSMSettings.h` 中的默认设置
2. **defaults.json**：应用内置的默认配置（不可修改）
3. **GPO 策略快照**：启动时读取注册表中的组策略设置，应用锁定标记
4. **settings.json**：用户自定义配置文件
5. **Profile 级覆盖**：对每个 Profile 应用 `profiles.list[]` 中的覆盖设置
6. **动态 Profile**：WSL、PowerShell、CMD 等动态生成的 Profile 注入
7. **运行时计算**：解析 `Effective*` 属性，应用 GPO 过滤逻辑

### 12.2.3 配置热重载

与 WT 一致，`settings.json` 支持文件系统监听热重载，保存文件后设置立即生效（部分设置如 Agent 选择需要新 Tab 才生效，运行中的 Tab 保持原有配置）。

---

## 12.3 全局 Agent 设置表格

以下是全局 Agent 核心配置项，对应 [`GlobalAppSettings.idl:117-126`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/GlobalAppSettings.idl#L117-L126)：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| **`acpAgent`** | String | `"copilot"` | Agent 窗格默认使用的 ACP Agent。可选值：<br>- 内置 Agent：`"copilot"`、`"gemini"`、`"claude"`、`"codex"`、`"opencode"`<br>- 自定义 Agent：`"custom:<command>"` 格式，配合 `acpCustomCommand` 使用 |
| **`acpModel`** | String | `""`（空 = Agent 默认模型） | ACP Agent 模型覆盖。空字符串表示使用 Agent 自身的默认模型。当 Agent 通过 `agent_status` 通告可用模型列表时，设置 UI 显示下拉选择器；否则显示自由文本框 |
| **`acpCustomCommand`** | String | `""` | 自定义 Agent 启动命令。仅当 `acpAgent` 为 `custom:...` 时生效，例如：`"my-agent --acp --stdio"` |
| **`agentPanePosition`** | String | `"bottom"` | Agent 窗格默认位置。可选值：`"bottom"`（底部）、`"right"`（右侧） |

&gt; **源码溯源**：这四个配置项的 IDL 定义见 [`GlobalAppSettings.idl:117-126`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/GlobalAppSettings.idl#L117-L126)，UI 实现见 [`AIAgents.xaml:72-179`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L72-L179)。

---

## 12.4 Delegate 设置（委托命令）

Delegate Agent 用于命令面板的 `?&lt;prompt&gt;` 快捷委托功能（见第8章），支持独立于 Agent 窗格配置不同的 Agent。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| **`delegateAgent`** | String | `"copilot"` | 命令面板委托（`?&lt;prompt&gt;`）使用的 Agent。可选值与 `acpAgent` 相同：内置 Agent ID 或 `"custom:<cmd>"` |
| **`delegateModel`** | String | `""`（空 = Agent 默认模型） | Delegate Agent 模型覆盖，语义同 `acpModel` |
| **`delegateCustomCommand`** | String | `""` | 自定义 Delegate Agent 启动命令，仅当 `delegateAgent` 为 `custom:...` 时生效 |

&gt; **UI 位置**：设置 UI 的"命令面板组"（Command palette group）子标题下，见 [`AIAgents.xaml:458-506`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L458-L506)。

---

## 12.5 Autofix 设置（自动错误修复）

Autofix 功能自动检测命令失败并建议修复，相关配置见第9章。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| **`autoErrorDetectionEnabled`** | Boolean | `true` | 启用自动错误检测父开关。关闭后整个 Autofix 管道禁用，包括错误检测和修复建议 |
| **`autoFixEnabled`** | Boolean | `true` | 自动错误建议子开关。依赖于 `autoErrorDetectionEnabled`，父开关关闭时此选项灰显不可用 |

&gt; **UI 层级**：`autoErrorDetectionEnabled` 是 Expander 头部的主开关，`autoFixEnabled` 是展开体内的嵌套子开关，UI 实现见 [`AIAgents.xaml:189-265`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L189-L265)。
&gt;
&gt; **GPO 锁定**：`autoFixEnabled` 可被组策略强制禁用（`IsAutoFixPolicyLocked`）。

---

## 12.6 AI Integration 设置（AI 协调器）

AI Integration 是实验性功能，用于配置独立的协调器进程来管理 AI 操作，相关配置使用点分命名：

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| **`aiIntegration.coordinator.enabled`** | Boolean | `false` | 启用外部 AI 协调器进程 |
| **`aiIntegration.coordinator.commandline`** | String | `"wta"` | 协调器启动命令行 |
| **`aiIntegration.coordinator.profile`** | String | `"{fd19208a-412b-4857-8a2d-9ca592b4b16e}"` | 协调器使用的 Profile GUID |
| **`aiIntegration.confirmation.readOperations`** | String | `"auto"` | 读操作（如文件读取、目录列出）确认策略：<br>- `"auto"`：自动执行不询问<br>- `"confirm"`：每次操作前询问用户确认<br>- `"deny"`：拒绝所有读操作 |
| **`aiIntegration.confirmation.createOperations`** | String | `"auto"` | 创建/写操作（如新建文件、写入内容）确认策略，可选值同上 |
| **`aiIntegration.confirmation.inputOperations`** | String | `"auto"` | 终端输入操作（如 SendInput、执行命令）确认策略，可选值同上 |

&gt; **IDL 定义**：见 [`GlobalAppSettings.idl:128-134`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/GlobalAppSettings.idl#L128-L134)。

---

## 12.7 Profile 级 Agent 覆盖（WSL distro 专用 Agent）

除全局设置外，Intelligent Terminal 支持在单个 Profile 级别覆盖 Agent 后端，主要用于 WSL 发行版等场景——例如让 Linux 下的 WSL Tab 自动使用 Linux 侧的 Agent，而 Windows 侧的 Tab 使用 Windows 侧的 Agent。

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| **`agentPaneBackend`** | String | `""`（空 = 继承全局） | Profile 专用 Agent 后端。空字符串表示继承全局 `acpAgent` 设置 |

### 12.7.1 使用示例（WSL 专用配置）

```jsonc
{
    "profiles": {
        "list": [
            {
                "guid": "{...}",
                "name": "Ubuntu",
                "source": "Windows.Terminal.Wsl",
                "agentPaneBackend": "custom:wsl-agent --acp"  // WSL 专用 Agent
            }
        ]
    }
}
```

&gt; **IDL 定义**：见 [`Profile.idl:64`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/Profile.idl#L64)。这是一个 `INHERITABLE_PROFILE_SETTING`，支持通过 `profiles.defaults` 设置全局默认覆盖。

---

## 12.8 GPO 策略（AllowedAgents）

企业环境可以通过 Windows 组策略（GPO）对 Agent 功能进行集中管控，相关策略定义在 [`policies/IntelligentTerminal.admx`](../../../../../external/libs/intelligent-terminal/policies/IntelligentTerminal.admx)。

### 12.8.1 策略列表

| 策略名称 | 注册表位置 | 类型 | 说明 |
|---------|-----------|------|------|
| **`AllowedAgents`** | `HKLM\Software\Policies\Microsoft\IntelligentTerminal\AllowedAgents` | MULTI_SZ（多行文本） | 允许的内置 Agent 白名单。每行一个 Agent ID，如 `copilot`、`gemini`、`claude`、`codex`、`opencode`。不在列表中的内置 Agent 将从下拉选择中隐藏 |
| **`AllowCustomAgents`** | `HKLM\Software\Policies\Microsoft\IntelligentTerminal\AllowCustomAgents` | DWORD | 是否允许自定义 Agent（`custom:<cmd>`）：<br>- `1`（默认）：允许自定义 Agent<br>- `0`：禁止自定义 Agent，UI 中自定义选项隐藏 |
| **`AutoFixEnabled`** | （策略锁定） | - | Autofix 可被策略强制关闭，见 `IsAutoFixPolicyLocked` |
| **`AgentSessionHooks`** | （策略锁定） | - | Agent Session Hooks 可被策略强制禁用，见 `IsAgentSessionHooksPolicyLocked` |

### 12.8.2 策略生效属性

运行时代码不应直接读取原始设置值，而应使用 `Effective*` getter，这些方法自动应用 GPO 过滤：

| 属性 | 说明 |
|------|------|
| `EffectiveAcpAgent` | 返回应用 GPO 过滤后的实际 ACP Agent。如果用户选择的 Agent 被策略禁止，自动回退到第一个允许的 Agent；无允许 Agent 时返回空 |
| `EffectiveDelegateAgent` | Delegate Agent 的生效版本，过滤逻辑同上 |
| `EffectiveAutoErrorDetectionEnabled` | 错误检测开关生效值（考虑策略锁定） |
| `EffectiveAutoFixEnabled` | Autofix 开关生效值（考虑策略锁定） |

### 12.8.3 策略锁定状态指示器

UI 中通过以下属性显示锁定状态，对应 [`GlobalAppSettings.idl:151-154`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/GlobalAppSettings.idl#L151-L154)：

| 属性 | 锁定含义 | UI 表现 |
|------|---------|---------|
| `IsAgentPolicyLocked` | `AllowedAgents` 策略已启用 | Agent 下拉框下方显示"策略已锁定"提示，列表已过滤 |
| `IsCustomAgentPolicyLocked` | `AllowCustomAgents = 0` | 自定义 Agent 相关按钮（添加/编辑/删除）禁用 |
| `IsAutoFixPolicyLocked` | Autofix 被策略强制关闭 | Autofix 开关灰显，强制关闭 |
| `IsAgentSessionHooksPolicyLocked` | Hooks 被策略禁用 | "Install hooks"按钮禁用 |

&gt; **测试参考**：策略行为的 E2E 测试见 [`test/e2e/tests/Feature.AgentPolicy.Tests.ps1`](../../../../../external/libs/intelligent-terminal/test/e2e/tests/Feature.AgentPolicy.Tests.ps1)。

---

## 12.9 设置 UI（AIAgents.xaml）

Agent 相关设置位于设置界面的"AI Agents"页面，XAML 定义见 [`AIAgents.xaml`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml)。

### 12.9.1 UI 分组结构

设置页面分为两个主要分组：

**1. Agent 窗格组（Agent pane group）** [`AIAgents.xaml:66-456`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L66-L456)

- 页面副标题 + 隐私声明链接
- **Agent (ACP CLI)**：主 Agent 选择下拉框，支持自定义 Agent 添加/编辑/删除
- **Model**：模型选择，自动判断下拉列表/自由文本框模式
- **Pane position**：Agent 窗格位置（底部/右侧）
- **Automatic error detection**：错误检测 + 自动修复（Expander 层级结构）
- **Agent session tracking (hooks)**：Hooks 安装管理，支持 GitHub Copilot、Claude Code、Gemini CLI、Codex CLI、OpenCode 逐个管理

**2. 命令面板组（Command palette group）** [`AIAgents.xaml:458-506`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L458-L506)

- **Agent (delegate / on-demand CLI)**：Delegate Agent 选择，同样支持自定义命令

### 12.9.2 自定义 Agent 编辑流程

1. **选择"Custom..."选项**：触发添加模式，显示命令输入框
2. **输入启动命令**：例如 `my-agent --acp --stdio`，Placeholder 提供示例
3. **Save/Cancel/Delete**：三个按钮控制编辑状态
4. **只读预览**：选中已有自定义 Agent 时，显示命令预览和编辑/删除按钮

&gt; **已安装标记**：下拉列表中未安装的内置 Agent 以半透明（Opacity=0.6）显示，由 [`InstalledOpacity`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L23) 转换器控制。

---

## 12.10 环境变量

Intelligent Terminal 支持多个环境变量用于调试和运行时控制：

| 环境变量 | 用途 | 取值示例 |
|---------|------|---------|
| **`WTA_LOG`** | WTA Rust 进程日志级别控制（优先级高于 `RUST_LOG`） | `trace`、`debug`、`info`、`warn`、`error`、`debug,agent_client_protocol=debug` |
| **`RUST_LOG`** | 标准 Rust 日志环境变量（fallback，当 `WTA_LOG` 未设置时使用） | 同 `WTA_LOG` |
| **`WT_COM_CLSID`** | WT COM 服务器（`IProtocolServer`）的 CLSID，用于 wtcli 和 Agent Hooks 发现 WT 协议端点 | GUID 格式，由 WT 在启动时注入每个 pane 的 shell 环境 |
| **`WTA_SESSIONS_SHOW_AGENT_PANE`** | 控制 `wtcli sessions list` 输出中是否显示 Agent 窗格会话。用于 WSL 会话管理过滤测试 | `1` = 显示，`0` = 隐藏（默认） |
| **`WTA_HOOK_LOG_DIR`** | PowerShell hooks 日志目录，由 C++/Rust 设置后传入 hooks 进程 | 日志目录路径 |
| **`WT_SESSION`** | WT 会话 ID，由 WT 注入 | 会话标识符 |
| **`WT_PROFILE_ID`** | 当前 pane 使用的 Profile GUID，由 WT 注入 | Profile GUID |

### 12.10.1 WT_COM_CLSID 发现机制

- WT 启动时将 `WT_COM_CLSID` 注入所有 pane 的 shell 环境
- Agent CLI 和 hooks 通过读取此环境变量定位 COM 服务器
- `wtcli set-env -s powershell|bash|cmd` 可输出对应的 export 语句，用于子 shell 恢复环境
- `wtcli info` 命令会打印当前继承的 `WT_COM_CLSID` 和连接状态

&gt; **安全说明**：`WT_COM_CSID` 本身不是密钥，只是路由元数据，但它允许知道它的进程调用 WT 的 COM 接口。安全模型见 [`doc/security-model.md`](../../../../../external/libs/intelligent-terminal/doc/security-model.md)。

### 12.10.2 日志级别快速设置

```powershell
# PowerShell - 启用 debug 级别（当前窗口启动的 IT 继承）
$env:WTA_LOG="debug"

# Cmd - 启用 trace 级别
set WTA_LOG=trace

# Bash/WSL - 启用特定模块 trace
export WTA_LOG=debug,master=trace,helper=trace,acp_client=trace
```

修改环境变量后需要**关闭所有 IT 窗口再重新打开**才会生效（日志在进程启动时初始化）。

---

## 12.11 完整配置示例

以下是一个包含所有 Agent 相关配置的完整 `settings.json` 示例：

```jsonc
{
    "$schema": "https://aka.ms/terminal-profiles-schema",

    // ─── 全局 Agent 窗格设置 ───
    "acpAgent": "copilot",
    "acpModel": "",
    "acpCustomCommand": "",
    "agentPanePosition": "bottom",

    // ─── 命令面板委托设置 ───
    "delegateAgent": "copilot",
    "delegateModel": "",
    "delegateCustomCommand": "",

    // ─── Autofix 设置 ───
    "autoErrorDetectionEnabled": true,
    "autoFixEnabled": true,

    // ─── AI Integration（实验性） ───
    "aiIntegration.coordinator.enabled": false,
    "aiIntegration.coordinator.commandline": "wta",
    "aiIntegration.coordinator.profile": "{fd19208a-412b-4857-8a2d-9ca592b4b16e}",
    "aiIntegration.confirmation.readOperations": "auto",
    "aiIntegration.confirmation.createOperations": "auto",
    "aiIntegration.confirmation.inputOperations": "auto",

    // ─── Profile 默认值（所有 Profile 继承） ───
    "profiles": {
        "defaults": {
            // "agentPaneBackend": ""  // 全局默认不覆盖
        },
        "list": [
            // ─── WSL Ubuntu 使用专用 Agent ───
            {
                "guid": "{2c4de342-38b7-51cf-b940-2309a097f518}",
                "name": "Ubuntu",
                "source": "Windows.Terminal.Wsl",
                "agentPaneBackend": "custom:wsl -e ~/.local/bin/wta-agent --acp --stdio"
            },
            // ─── 自定义本地 Agent 示例 ───
            {
                "guid": "{...}",
                "name": "PowerShell",
                "commandline": "pwsh.exe",
                // 不设置 agentPaneBackend，继承全局
            }
        ]
    },

    // ─── 其他 WT 设置... ───
    "defaultProfile": "{61c54bbd-c2c6-5271-96e7-009a87ff44bf}",
    "initialRows": 30,
    "initialCols": 120
}
```

### 12.11.1 自定义 Agent 示例

```jsonc
{
    "acpAgent": "custom:C:\\tools\\my-agent.exe --model gpt-4 --acp --stdio",
    "acpModel": "",
    "acpCustomCommand": "C:\\tools\\my-agent.exe --model gpt-4 --acp --stdio"
}
```

### 12.11.2 右侧 Agent 窗格配置

```jsonc
{
    "agentPanePosition": "right"
}
```

---

## 配置项速查表汇总

| 分类 | 配置项 | 类型 | 默认值 |
|------|--------|------|--------|
| **Agent 窗格** | `acpAgent` | String | `"copilot"` |
| | `acpModel` | String | `""` |
| | `acpCustomCommand` | String | `""` |
| | `agentPanePosition` | String | `"bottom"` |
| **Delegate** | `delegateAgent` | String | `"copilot"` |
| | `delegateModel` | String | `""` |
| | `delegateCustomCommand` | String | `""` |
| **Autofix** | `autoErrorDetectionEnabled` | Boolean | `true` |
| | `autoFixEnabled` | Boolean | `true` |
| **AI 协调器** | `aiIntegration.coordinator.enabled` | Boolean | `false` |
| | `aiIntegration.coordinator.commandline` | String | `"wta"` |
| | `aiIntegration.coordinator.profile` | String | 特定 GUID |
| | `aiIntegration.confirmation.readOperations` | String | `"auto"` |
| | `aiIntegration.confirmation.createOperations` | String | `"auto"` |
| | `aiIntegration.confirmation.inputOperations` | String | `"auto"` |
| **Profile 覆盖** | `agentPaneBackend` | String | `""`（继承） |
| **环境变量** | `WTA_LOG` / `RUST_LOG` | String | `info`(release) / `debug`(debug) |
| | `WT_COM_CLSID` | GUID | WT 自动注入 |
| | `WTA_SESSIONS_SHOW_AGENT_PANE` | Flag | `0` |

---

## 源码溯源

| 来源 | 内容 |
|------|------|
| [`AGENTS.md:26-45 Settings 章节`](../../../../../external/libs/intelligent-terminal/AGENTS.md#L26-L45) | 配置项 JSON 示例和默认值概览 |
| [`GlobalAppSettings.idl:117-154`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/GlobalAppSettings.idl#L117-L154) | 所有全局 Agent 配置项 IDL 定义、`Effective*` getter、GPO 锁定状态属性 |
| [`Profile.idl:64`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsModel/Profile.idl#L64) | Profile 级 `AgentPaneBackend` 覆盖设置 |
| [`AIAgents.xaml:1-510`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalSettingsEditor/AIAgents.xaml#L1-L510) | 设置 UI 完整实现：Agent 选择、模型选择、窗格位置、Autofix、Hooks、Delegate |
| [`policies/IntelligentTerminal.admx:31-45`](../../../../../external/libs/intelligent-terminal/policies/IntelligentTerminal.admx#L31-L45) | GPO 策略定义（AllowedAgents、AllowCustomAgents） |
| [`policies/en-US/IntelligentTerminal.adml:22-56`](../../../../../external/libs/intelligent-terminal/policies/en-US/IntelligentTerminal.adml#L22-L56) | GPO 策略英文说明文本 |
| [`doc/security-model.md`](../../../../../external/libs/intelligent-terminal/doc/security-model.md) | `WT_COM_CLSID` 安全模型说明 |
| [`doc/specs/wsl-session-management.md:261`](../../../../../external/libs/intelligent-terminal/doc/specs/wsl-session-management.md#L261) | `WTA_SESSIONS_SHOW_AGENT_PANE` 环境变量说明 |

---

## 本章导航

- [上一章：日志系统与调试](11-logging-debugging.md)
- [返回目录](README.md)
- [下一章：设计模式与架构](13-design-patterns.md)
