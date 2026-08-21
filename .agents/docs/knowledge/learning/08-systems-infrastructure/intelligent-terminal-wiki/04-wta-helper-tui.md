---
id: "intelligent-terminal-ch04-helper-tui"
title: "第4章 - WTA Rust 核心 - Helper 与 TUI"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第4章 WTA Rust 核心 - Helper 与 TUI

## 4.1 wta-helper 概述

`wta-helper` 是 Helper+Master 架构中**每个 Pane 独立运行的 TUI 进程**，由 Windows Terminal 为每个 Agent Pane 单独 spawn，负责提供用户交互界面。它不直接管理 Agent CLI 子进程，而是通过命名管道连接到全局单例的 `wta-master`，将所有 ACP（Agent Client Protocol）流量通过 master 路由转发。

**核心定位**：

1. **per-pane TUI**：每个 Agent Pane 对应一个独立的 helper 进程，拥有自己的终端 UI、输入框、聊天历史
2. **终端原生界面**：基于 Ratatui（tui-rs 继任者）构建的 TUI，运行在 ConPTY 伪终端中，与普通终端 pane 视觉风格一致
3. **无 Agent 生命周期管理权**：helper 不 spawn Agent CLI，master 是唯一的 Agent 生命周期管理者
4. **ACP 透明代理客户端**：helper 通过命名管道连接 master，在 helper 视角中 **master 就是 agent**

**与 master 的关系**：

```
┌─────────────────────────────────────────────────────────────────┐
│                     Windows Terminal 进程                        │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                  SharedWta (C++ 单例)                      │  │
│  │  - 管理 master 生命周期                                     │  │
│  │  - 创建命名管道                                            │  │
│  └─────────────────────┬─────────────────────────────────────┘  │
│                        │ 命名管道 \\.\pipe\wta-master-<GUID>     │
│  ┌─────────────────────▼─────────────────────────────────────┐  │
│  │                    wta-master (单例)                        │  │
│  │  - 维护 Agent CLI 进程池                                    │  │
│  │  - ACP 消息多路复用                                        │  │
│  │  - Session 路由表                                          │  │
│  └──┬──────────┬──────────┬──────────┬──────────┬──────────┬───┘  │
│     │          │          │          │          │          │      │
│  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  ┌──▼───┐  │
│  │Helper│  │Helper│  │Helper│  │Helper│  │Helper│  │Helper│  │
│  │Pane 1│  │Pane 2│  │Pane 3│  │Pane N│  │ ...  │  │Pane M│  │
│  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  └──────┘  │
│     每个 Pane 独立进程，各自拥有 TUI 状态                          │
└─────────────────────────────────────────────────────────────────┘
```

**崩溃隔离设计**：

- helper 是独立进程，单个 helper 崩溃**不影响** master 和其他 helper
- master 检测到 helper 断开后，通过 WT 协议事件 `restart_agent_pane` 通知 C++ 侧重新 spawn helper
- master 崩溃时，helper 检测到管道断开进入 `transport_lost` 状态，仅保留 `/restart` 命令可用，用户可通过 `/restart` 触发整个栈重启

> **来源**：[`tools/wta/src/helper/mod.rs` 头部注释](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/mod.rs#L1-L12)、[`app.rs` 中 `transport_lost` 字段](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs#L905-L915)

---

## 4.2 源码结构

Helper 与 TUI 相关代码分布在以下位置：

| 路径 | 职责 | 主要内容 |
|------|------|----------|
| [`helper/mod.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/mod.rs) | Helper 模块入口 | `run_helper_mode()` 入口函数，导出 `HelperConfig` |
| [`helper/runtime.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs) | Helper 运行时实现 | TUI 初始化、事件循环启动、ACP 管道连接、WT 协议连接 |
| [`helper/config.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/config.rs) | Helper 配置 | `HelperConfig` 结构体，解析命令行参数 |
| [`app.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs) | TUI 应用核心 | `App` 状态结构体、事件处理、slash command 分发 |
| [`app/tab_state.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/tab_state.rs) | Tab 会话状态 | `TabSession`、`ChatMessage`、`Scroll`、`PermissionState` |
| [`app/turn_state.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/turn_state.rs) | Turn 生命周期状态机 | `TurnState` 枚举、`SubmittedPrompt`、`TurnOutcome` |
| [`app/input_edit.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/input_edit.rs) | 输入编辑器 | 光标移动、文本编辑、输入历史 |
| [`app/autofix.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/autofix.rs) | Autofix 状态机 | 错误检测、自动修复触发 |
| [`ui/mod.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/mod.rs) | UI 模块入口 | 模块声明、导出 render 函数 |
| [`ui/layout.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/layout.rs) | 布局渲染 | 主布局函数 `render()`、区域分割 |
| [`ui/chat.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/chat.rs) | 聊天视图 | 消息渲染、滚动、spinner |
| [`ui/input.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/input.rs) | 输入框 | 输入编辑器渲染、光标 |
| [`ui/permission.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/permission.rs) | 权限弹窗 | 工具调用权限确认卡片 |
| [`ui/command_popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/command_popup.rs) | Slash command 弹窗 | 自动补全候选列表、`/help` 覆盖层 |
| [`ui/agents_view.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/agents_view.rs) | Session 管理视图 | `/sessions` 列表渲染 |
| [`ui/model_popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/model_popup.rs) | Model 选择弹窗 | `/model` picker |
| [`ui/agent_popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/agent_popup.rs) | Agent 选择弹窗 | `/agent` picker |
| [`ui/recommendations.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/recommendations.rs) | 推荐卡片 | 修复建议选择面板 |
| [`ui/setup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/setup.rs) | 安装/设置向导 | 首次运行、agent 缺失时的向导 |
| [`ui/auth.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/auth.rs) | 认证界面 | Copilot device-code 登录 |
| [`ui/debug_panel.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/debug_panel.rs) | 调试面板 | 内部调试信息展示 |
| [`ui/popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/popup.rs) | 弹窗基元 | 通用弹窗渲染辅助函数 |
| [`ui/card.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/card.rs) | 卡片组件 | 带边框的卡片基元 |
| [`ui/shimmer.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/shimmer.rs) | 加载动画 | shimmer 骨架屏动画 |
| [`commands.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs) | Slash command 注册表 | 命令定义、解析、前缀匹配 |
| [`event.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/event.rs) | 输入事件读取 | crossterm 事件循环、tick 定时器 |

> **来源**：[`ui/mod.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/mod.rs#L1-L24)、[`app.rs` 模块声明](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs#L54-L69)

---

## 4.3 Helper 启动流程

Helper 启动遵循严格的顺序：ConPTY 初始化 → 终端 raw mode → WT COM 协议连接 → Pane 身份发现 → 命名管道连接 → ACP initialize 握手 → 事件循环启动。

### 启动时序图

```mermaid
sequenceDiagram
    participant WT as Windows Terminal
    participant ConPTY as ConPTY
    participant Helper as wta-helper
    participant CT as crossterm
    participant RT as ratatui
    participant WTChan as wtcli/COM
    participant Pipe as NamedPipe
    participant Master as wta-master
    
    WT->>ConPTY: CreatePseudoConsole()
    WT->>Helper: spawn wta.exe --connect-master &lt;pipe-name&gt;<br/>--owner-tab-id &lt;guid&gt;
    ConPTY->>Helper: attach stdin/stdout/stderr
    
    Note over Helper: run_helper_mode()<br/>helper/mod.rs:25
    Helper->>Helper: tracing 初始化（main中完成）
    Helper->>Helper: resolve agent_source / cwd
    
    par WT 协议连接（尝试）
        Helper->>WTChan: CliChannel::connect()
        alt 连接成功
            WTChan-->>Helper: CliChannel 实例
            Helper->>WTChan: subscribe_events()
            Helper->>Helper: discover_pane_identity()<br/>通过 wt_list_panes 匹配 PID
            Helper->>Helper: pane_id / tab_id / window_id
        else WT 不可用
            Helper->>Helper: wt_connected = false，降级运行
        end
    end
    
    Note over Helper: run_acp_tui_mode()<br/>helper/runtime.rs:168
    Helper->>CT: enable_raw_mode()
    Helper->>CT: EnterAlternateScreen
    Helper->>CT: EnableMouseCapture
    Helper->>CT: SetCursorStyle::SteadyBlock
    Helper->>RT: Terminal::new(CrosstermBackend::new(stdout))
    
    Note over Helper: run_acp_app()<br/>helper/runtime.rs:260
    Helper->>Helper: LocalSet::new() 创建本地任务集
    Helper->>Helper: 创建所有 mpsc channel<br/>(event_tx, prompt_tx, cancel_tx, ...)
    
    par crossterm 事件读取（后台）
        Helper->>CT: EventStream::new()
        loop
            CT-->>Helper: Key/Mouse/Resize/Focus 事件
            Helper->>Helper: map_crossterm_event() → AppEvent
            Helper->>Helper: event_tx.send(AppEvent)
        end
    end
    
    par Tick 定时器（两个频率）
        loop
            Note over Helper: 120ms Tick → spinner 动画<br/>33ms RevealTick → 打字机效果
            Helper->>Helper: event_tx.send(Tick/RevealTick)
        end
    end
    
    par WT 事件订阅（后台，如果连接成功）
        loop
            WTChan-->>Helper: WT 事件 JSON<br/>(connection_state / agent_event / vt_sequence)
            Helper->>Helper: 解析为 AppEvent::WtEvent
            Helper->>Helper: event_tx.send(WtEvent)
        end
    end
    
    Helper->>Helper: App::new() 初始化应用状态
    Helper->>Helper: set_master_pipe_acp_params()<br/>预存管道名用于重连
    
    alt 正常模式（非 auth/setup）
        par ACP 客户端（后台任务）
            Helper->>Pipe: 连接命名管道 \\.\pipe\&lt;pipe-name&gt;
            Pipe-->>Helper: 连接成功
            Helper->>Master: ACP initialize 请求
            Master-->>Helper: initialize 响应<br/>(agent_name, models, capabilities)
            loop
                Master-->>Helper: session/update chunks / notifications
                Helper->>Master: prompt / cancel / new_session 请求
            end
        end
    else FRE 初始认证模式
        Helper->>Helper: show_copilot_auth_screen()<br/>显示登录界面
        Note over Helper: 登录完成后 LoginComplete<br/>触发 try_start_acp() 再连接
    end
    
    Note over Helper: 进入主事件循环
    loop 主循环
        Helper->>Helper: terminal.draw(|f| ui::render(f, &amp;mut app))
        Helper->>Helper: event_rx.recv() 等待事件
        alt Key/Mouse 事件
            Helper->>Helper: app.handle_event()
        else ACP 消息
            Helper->>Helper: app.apply_acp_event()
        else WT 事件
            Helper->>Helper: app.handle_wt_event()
        else Tick 事件
            Helper->>Helper: app.tick() 更新动画
        end
    end
```

**关键启动要点**：

1. **Pane 身份自发现**：[`discover_pane_identity()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L86-L134) 通过 `wt_list_windows` → `wt_list_tabs` → `wt_list_panes` 枚举所有 pane，匹配自身 PID 找到 `pane_id`/`window_id`
2. **TUI 恢复守卫**：[`TuiRestoreGuard`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L136-L166) RAII guard 确保 panic/错误时正确恢复终端（disable raw mode、leave alternate screen、恢复光标）
3. **错误直接退出**：TUI 启动失败时 [`process::exit(1)`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L227)，不返回 Err——因为此时终端状态可能已被破坏
4. **管道重连预置**：启动时即调用 [`set_master_pipe_acp_params()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L723-L732) 预存管道名，认证后重连无需重新解析命令行

> **来源**：[`run_default_tui_over_pipe()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L26-L83)、[`run_acp_tui_mode()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L168-L230)

---

## 4.4 App 状态机

`App` 结构体是 helper 进程的**全局状态根**，包含所有 UI 状态、会话状态、通道发送端。核心状态通过嵌套模块化设计：全局字段 + per-tab `TabSession`。

### App 核心字段（全局）

[`App` 结构体](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs#L825-L1048) 关键字段：

| 字段 | 类型 | 用途 |
|------|------|------|
| `mode` | `AppMode` | 应用模式：Chat/Setup/Auth |
| `state` | `ConnectionState` | ACP 连接状态：Disconnected/Connecting/Connected/Failed |
| `tab_sessions` | `HashMap<String, TabSession>` | per-Tab 会话状态，key 是 WT Tab StableId |
| `tab_id` | `Option<String>` | 当前活动 Tab ID |
| `owner_tab_id` | `Option<String>` | helper 所属 Tab ID（不随焦点切换变化） |
| `current_agent_id` | `String` | 当前选择的 agent ID |
| `available_agents` | `Vec<AvailableAgent>` | 可用 agent 列表（预检测+GPO过滤） |
| `available_models` | `Vec<AcpModelInfo>` | agent 广告的可用模型列表 |
| `session_to_tab` | `HashMap<String, String>` | ACP SessionId → TabId 反向查找表 |
| `transport_lost` | `bool` | master 管道断开标记（仅 `/restart` 可用） |
| `autofix_enabled` | `bool` | 自动修复全局开关 |
| `agent_sessions` | `AgentSessionRegistry` | 全局 session 注册表（live + history） |
| `*_tx` | `mpsc::UnboundedSender<...>` | 各功能通道发送端（prompt/cancel/new_session/restart等） |

### TabSession 状态（per-Tab）

[`TabSession` 结构体](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/tab_state.rs#L185-L300) 包含单个 Tab 的所有状态：

```rust
pub struct TabSession {
    // 对话历史
    pub messages: Vec<ChatMessage>,
    pub completed_turns: Vec<CompletedTurn>,
    pub chat_scroll: Scroll,
    
    // 流式状态
    pub pending_agent_response: String,
    pub pending_user_replay: String,
    pub loading_session: bool,
    pub turn: TurnState,  // 核心 turn 状态机
    
    // 工具调用 / 权限
    pub tool_calls: HashMap<String, (String, String)>,
    pub permission: VecDeque<PermissionState>,
    
    // 推荐卡片
    pub selected_recommendation: usize,
    pub rec_scroll: Scroll,
    
    // 输入编辑器
    pub input: String,
    pub cursor_pos: usize,
    pub input_history: InputHistory,
    pub command_popup_candidates: Vec<&'static CommandSpec>,
    
    // 视图状态
    pub current_view: View,  // Chat / Agents
    pub agents_list_state: ListState,
    
    // Autofix
    pub autofix: TabAutofixState,
    
    // 模型/Agent 选择弹窗
    pub model_override: Option<String>,
    pub model_picker_open: bool,
    pub agent_picker_open: bool,
    
    // Pane 可见性
    pub pane_open: bool,
}
```

### Turn 状态机

[`TurnState` 枚举](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/turn_state.rs#L16-L34) 是显式的 per-turn 生命周期状态机：

```mermaid
stateDiagram-v2
    [*] --> Idle
    
    Idle --> Submitted: 用户提交 prompt<br/>/fix 触发自动修复
    Submitted --> Streaming: 收到第一个 agent message chunk
    Streaming --> Surfaced: AgentMessageEnd 到达
    Submitted --> Surfaced: 被取消 / 空响应
    Surfaced --> Idle: end_pending = false<br/>(用户可发送下一条)
    
    state Submitted {
        [*] --> AwaitingFirstChunk
        note right of Submitted
            prompt: SubmittedPrompt
            (id, text, submitted_at,
             context, autofix)
        end note
    }
    
    state Streaming {
        [*] --> AccumulatingChunks
        note right of Streaming
            prompt: SubmittedPrompt
            buf: String (累计响应)
        end note
    }
    
    state Surfaced {
        [*] --> ShowOutcome
        note right of Surfaced
            prompt: SubmittedPrompt
            outcome: TurnOutcome<br/>  - Recommendation(card)<br/>  - ChatTurn<br/>  - Empty
            end_pending: bool
        end note
    }
```

**TurnOutcome 变体**：

| 变体 | 含义 |
|------|------|
| `Recommendation(RecommendationSet)` | 显示推荐卡片（autofix / planner 模式） |
| `ChatTurn` | 普通对话已提交到历史 |
| `Empty` | 空响应（取消或无可解析内容） |

### ChatMessage 类型

[`ChatMessage` 枚举](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/tab_state.rs#L14-L42) 表示聊天区域中的单条消息：

- `User(String)`：用户消息
- `Agent(String)`：agent 回复
- `System(String)`：系统消息（会话开始、错误提示等）
- `ToolCall { id, title, status, location, location_is_command }`：工具调用记录
- `Plan(Vec<PlanEntry>)`：计划模式的执行计划
- `Error(String)`：错误消息
- `AgentEvent(String)`：WT agent 事件内联显示
- `Disclaimer`：AI 使用免责声明（每次启动显示）

### 输入编辑器状态

输入编辑器状态在 [`app/input_edit.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/input_edit.rs) 中实现，核心状态存储在 `TabSession` 中：

- `input: String`：当前输入文本
- `cursor_pos: usize`：光标位置（字节偏移）
- `input_history: InputHistory`：输入历史循环（Up/Down 导航）
- `command_popup_candidates`：slash command 自动补全候选列表
- `INPUT_HISTORY_MAX_ENTRIES`：历史最大条数

> **来源**：[`App::new()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs#L1124-L1200)、[`TabSession` 完整定义](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/tab_state.rs#L185-L300)、[`TurnState` 状态转换方法](../../../../../external/libs/intelligent-terminal/tools/wta/src/app/turn_state.rs#L80-L169)

---

## 4.5 TUI 视图层架构

UI 采用分层模块化设计，[`ui::render()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/layout.rs#L9-L258) 是唯一的渲染入口，根据 `AppMode` 和 `current_view` 分派到对应子模块。

### 组件关系图

```mermaid
graph TD
    subgraph "UI Layer (ui/)"
        L[layout::render<br/>ui/layout.rs:9]
    end
    
    subgraph "Mode Dispatch"
        L -->|AppMode::Auth| A[auth::render<br/>ui/auth.rs]
        L -->|AppMode::Setup| S[setup::render<br/>ui/setup.rs]
        L -->|AppMode::Chat + View::Agents| AV[agents_view::render<br/>ui/agents_view.rs]
        L -->|AppMode::Chat + View::Chat| C[Chat Layout]
    end
    
    subgraph "Chat Mode Components"
        C --> CH[chat::render<br/>ui/chat.rs]
        C --> RC[recommendations::render<br/>ui/recommendations.rs]
        C --> PM[permission::render<br/>ui/permission.rs]
        C --> AC[chat::render_activity<br/>Activity row]
        C --> IN[input::render<br/>ui/input.rs]
    end
    
    subgraph "Popups (anchored to input)"
        C --> CP[command_popup::render_popup<br/>/command autocomplete]
        C --> MP[model_popup::render_popup<br/>/model picker]
        C --> AP[agent_popup::render_popup<br/>/agent picker]
    end
    
    subgraph "Overlays (full-screen)"
        C --> HO[command_popup::render_help_overlay<br/>/help]
        L --> DBG[debug_panel::render<br/>ui/debug_panel.rs<br/>(right 40% when enabled)]
    end
    
    subgraph "State"
        APP[App struct<br/>app.rs]
        APP --> TS[TabSession<br/>per-tab state]
        TS --> TURN[TurnState<br/>turn lifecycle]
        TS --> INP[Input state<br/>editor + history]
        TS --> AUTOFIX[TabAutofixState]
    end
    
    L --> APP
    CH --> TS
    IN --> INP
    RC --> TURN
    
    style L fill:#f9f,stroke:#333,stroke-width:2px
    style APP fill:#9f9,stroke:#333,stroke-width:2px
```

### 主布局结构（Chat 模式）

[`layout.rs` 中主分割逻辑](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/layout.rs#L150-L162) 使用 Ratatui 的 `Layout` 垂直分割：

```
┌─────────────────────────────────────────────────────────┐
│  Chat area (chat::render)                               │
│  高度自适应：min(estimated_height, max_available)        │
│  [1 cell padding left/right]                             │
├─────────────────────────────────────────────────────────┤
│  Recommendations panel (recommendations::render)        │
│  0 高度当无推荐时                                         │
├─────────────────────────────────────────────────────────┤
│  Permission panel (permission::render)                  │
│  0 高度当无待确认权限时                                   │
├─────────────────────────────────────────────────────────┤
│  Filler (弹性区域，填充空白)                              │
├─────────────────────────────────────────────────────────┤
│  Hint row (welcome / transient hint)                    │
│  0 或 1 行                                               │
├─────────────────────────────────────────────────────────┤
│  Recommendation nav hint                                 │
│  0 或 1 行                                               │
├─────────────────────────────────────────────────────────┤
│  Activity row (chat::render_activity)                   │
│  1 行固定：spinner / 状态文本                             │
├─────────────────────────────────────────────────────────┤
│  Input box (input::render)                              │
│  自适应高度（多行输入支持）                               │
└─────────────────────────────────────────────────────────┘
```

### 关键视图组件说明

| 组件 | 文件 | 职责 |
|------|------|------|
| **chat** | [`ui/chat.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/chat.rs) | 渲染 `completed_turns` + 流式响应，处理滚动、spinner 动画、打字机 reveal 效果 |
| **input** | [`ui/input.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/input.rs) | 渲染输入框、光标、slack command 前缀高亮、粘贴指示 |
| **permission** | [`ui/permission.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/permission.rs) | 工具调用权限确认卡片，显示 Allow/Deny/AlwaysAllow 选项，支持 y/n 快捷键 |
| **command_popup** | [`ui/command_popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/command_popup.rs) | Slash command 自动补全下拉框，紧贴输入框上方；`/help` 全屏覆盖层 |
| **model_popup** | [`ui/model_popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/model_popup.rs) | `/model` 模型选择弹窗，列出 agent 广告的模型 |
| **agent_popup** | [`ui/agent_popup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/agent_popup.rs) | `/agent` agent 选择弹窗，显示已安装且策略允许的 agent |
| **agents_view** | [`ui/agents_view.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/agents_view.rs) | `/sessions` 全屏幕 session 管理列表，显示 live/history sessions，支持搜索、过滤、resume |
| **recommendations** | [`ui/recommendations.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/recommendations.rs) | 推荐选择卡片，显示 autofix 修复建议，支持键盘导航和执行 |
| **setup** | [`ui/setup.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/setup.rs) | 首次运行/agent 缺失设置向导，提供安装、登录、重试选项 |
| **auth** | [`ui/auth.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/auth.rs) | Copilot device-code 认证界面，显示验证码和 URL |
| **shimmer** | [`ui/shimmer.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/shimmer.rs) | 加载骨架屏动画，session list 刷新时显示 |

**设计要点**：

1. **弹窗锚定**：所有弹窗（command/model/agent）都锚定在输入框上方（`chunks[7]`），而不是屏幕固定位置——短聊天时弹窗不会飘到屏幕中间
2. **Help 覆盖层最高**：`/help` 覆盖层最后渲染，位于所有组件之上，Esc 始终可关闭
3. **宽度感知截断**：[`truncate_to_width()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/layout.rs#L265-L293) 使用 `unicode-width` 按显示宽度截断 CJK 字符，避免宽字符越界
4. **双频动画**：120ms `Tick` 驱动 spinner（~8fps），33ms `RevealTick` 驱动打字机效果（~30fps），分离频率减少不必要的全屏重绘

> **来源**：[`ui::render()` 完整实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/layout.rs#L9-L258)、[`render_activity()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/ui/chat.rs)

---

## 4.6 Slash Commands 实现

Slash command 系统由三部分组成：注册表（[`commands.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs)）、输入时前缀匹配（自动补全弹窗）、Enter 时分发执行（[`App::handle_slash_command()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs)）。

### 命令注册表

[`commands::REGISTRY`](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs#L83-L135) 是静态数组，定义所有支持的命令：

| 命令 | 类型 | 功能 | 参数 |
|------|------|------|------|
| `/help` | `Help` | 显示帮助覆盖层 | 无 |
| `/clear` | `Clear` | 清空当前 Tab 聊天历史 | 无 |
| `/new` | `New` | 创建新会话（ACP session/new） | 无 |
| `/fix` | `Fix` | 手动触发自动修复 | 可选：额外提示文本 |
| `/restart` | `Restart` | 重启整个 agent 栈（master+所有helper） | 无 |
| `/stop` | `Stop` | 取消当前 in-flight 请求（ACP cancel） | 无 |
| `/sessions` | `Sessions` | 打开 session 管理视图（View::Agents） | 无 |
| `/agent` | `Agent` | 选择/切换 agent | 可选：agent id |
| `/model` | `Model` | 选择/切换 ACP 模型 | 可选：model id/name |
| `/move` | `Move` | 移动当前 Tab 的 agent pane 位置 | 位置：left/right/up/down (l/r/u/d) |

### 解析流程

[`commands::classify()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs#L245-L264) 是 Enter 键处理入口，返回三分类结果：

```
输入文本 → trim_start() → strip_prefix('/')?
    ├─ 以 '//' 开头 → NotCommand（转义：//etc/hosts 作为普通文本）
    ├─ 匹配注册表 → Command(ParsedCommand { kind, rest })
    ├─ 形如 /xxx 但未注册 → Unknown("/xxx")（发送为普通 prompt + 提示未知命令）
    └─ 无 '/' 前缀 → NotCommand（普通 prompt）
```

**解析规则**：

- 忽略前导空白：`"  /stop"` 合法
- 大小写不敏感：`/HELP`、`/StOp` 均可识别
- 参数通过空白分隔，`rest` 字段捕获命令名后的所有 trimmed 文本
- 空 `/` 不是命令（斜杠后直接空白/结束）

### 自动补全机制

输入时通过 [`commands::is_command_prefix()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs#L339-L348) 判断是否显示补全弹窗：

1. 输入以 `/` 开头，且斜杠后**没有空白**时触发
2. 使用 [`commands::matches(prefix)`](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs#L277-L283) 前缀过滤注册表（大小写不敏感）
3. 候选列表显示在输入框上方，Tab/Shift+Tab 导航，Enter 或空格选中
4. `/agent ` 和 `/move ` 有二级补全：agent id 列表和位置列表

### Transport Lost 特殊处理

[`app.rs` 中 `transport_lost` 逻辑](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs#L905-L915)：当 master 管道断开时，自动补全候选列表**仅显示 `/restart`**，其他命令隐藏而非灰显——输入其他命令会被拒绝并显示重连提示。这是因为除了 `/restart` 走 wtcli→COM 通道（不经过已断开的管道），其他命令都需要与 master 通信。

### `/restart` 跨进程机制

Helper 模式下 `/restart` 不重启自身，而是通过 [`spawn_restart_agent_stack_forwarder()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L240-L258) 发送 WT 协议事件：

```rust
let evt = serde_json::json!({
    "type": "event",
    "method": "restart_agent_stack",
    "params": {},
});
crate::wt_protocol_events::send(evt.to_string());
```

C++ 侧 `SharedWta::Restart()` 收到后：
1. 终止 master 进程（Job Object 连带所有 helper）
2. 在同一管道名上重新 spawn master
3. 重新 toggle 活动 Tab 的 agent pane，新 helper 自动连接到新 master

> **来源**：[`commands.rs` 完整定义](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs#L1-L500+)、[`CommandKind` 文档注释](../../../../../external/libs/intelligent-terminal/tools/wta/src/commands.rs#L12-L58)

---

## 4.7 Event Loop 与消息处理

Helper 使用基于 `tokio::select!` 的异步事件循环，所有事件先转化为统一的 `AppEvent` 枚举，再由 `App::handle_event()` 集中处理。

### 事件源

多个并发任务向 `event_tx` 发送 `AppEvent`：

| 事件源 | 任务位置 | 事件类型 |
|--------|----------|----------|
| **crossterm 输入** | [`event::read_crossterm_events()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/event.rs#L43-L137) | `Key(KeyEvent)` / `Mouse(MouseEvent)` / `Resize(w,h)` / `FocusChanged(bool)` |
| **Tick 定时器** | 同上（120ms 间隔） | `Tick` |
| **RevealTick 定时器** | 同上（33ms 间隔） | `RevealTick` |
| **WT 协议事件** | [`helper/runtime.rs` 后台 reader](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L313-L395) | `WtEvent { method, pane_id, tab_id, params }` |
| **ACP 客户端** | [`run_acp_client_over_pipe()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/client.rs) 后台任务 | `AgentConnected` / `AgentMessageChunk` / `AgentMessageEnd` / `AgentError` / `PermissionRequest` 等 |
| **Debug 管道** | debug_rx 转发任务 | `DebugPipeMessage(DebugMessage)` |
| **推荐执行器** | recommendation executor 后台任务 | `RecommendationExecuted` 等 |

### Crossterm 事件过滤

[`map_crossterm_event()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/event.rs#L16-L41) 做关键过滤：

- **只处理 `KeyEventKind::Press`**：release 和 repeat 事件被丢弃，否则每个按键会触发两次
- **鼠标事件白名单**：只转发滚轮、左键按下/拖动/释放，用于聊天区滚动，不窃取 Up/Down 给输入历史
- **Paste 事件丢弃**：WT 通过 `agent_paste_text` WT 事件专门处理粘贴（支持剪贴板图片），不使用 crossterm 的 paste
- **Focus 事件**：xterm focus-in/out（CSI I / CSI O）用于 pane 失去焦点时隐藏光标

### 错误恢复：crossterm 流重建

[`read_crossterm_events()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/event.rs#L80-L108) 实现了 ConPTY 瞬态错误恢复：

- ConPTY 在 pane 隐藏/恢复、OS 回收伪控制台缓冲时可能返回瞬态读错误
- 连续错误计数 < 8 时：记录 warn，继续循环（不杀死 TUI）
- 连续错误 ≥ 8 时：重建 `EventStream`（重新打开输入句柄），重置计数
- 真正的 EOF（`None`）才退出循环

### 主事件循环结构

```rust
// helper/runtime.rs 中（概念性结构）
loop {
    // 1. 渲染
    terminal.draw(|f| ui::render(f, &mut app))?;
    
    // 2. 等待并处理事件
    tokio::select! {
        maybe_event = event_rx.recv() => {
            match maybe_event {
                Some(event) => {
                    let requires_redraw = app.handle_event(event);
                    // 根据事件类型决定是否需要立即重绘
                    // Tick/RevealTick 只在有动画时重绘
                }
                None => break,  // channel 关闭，退出
            }
        }
    }
}
```

**事件处理核心方法**：

- [`App::handle_event()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app_events.rs)：主事件分发
- [`App::handle_key()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app_keys.rs)：按键处理（输入编辑、快捷键、导航）
- [`App::handle_slash_command()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs)：slash command 执行
- [`App::apply_acp_event()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs)：ACP 消息处理（chunk、permission、plan 等）
- [`App::handle_wt_event()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs)：WT 协议事件处理（tab_changed、connection_state、agent_event 等）

> **来源**：[`event.rs` 完整实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/event.rs#L1-L200)、[`AppEvent` 定义](../../../../../external/libs/intelligent-terminal/tools/wta/src/app_contracts/event.rs)

---

## 4.8 Helper 崩溃隔离设计

Helper 架构实现了多层崩溃检测与隔离，确保单点故障不蔓延到整个终端。

### 进程隔离边界

| 组件 | 进程边界 | 崩溃影响范围 | 恢复机制 |
|------|----------|--------------|----------|
| **wta-helper** | 独立进程（每个 Pane 一个） | 仅该 Pane TUI 冻结/退出 | master 检测断开 → 发送 `restart_agent_pane` → C++ respawn 新 helper |
| **wta-master** | 独立单例进程 | **所有** helper 失去 agent 连接，进入 `transport_lost` 状态 | 用户执行 `/restart` → C++ `SharedWta::Restart()` → 重启整个栈 |
| **Agent CLI** (copilot/claude/...) | master 的子进程 | 共享该 CLI 的 helper 会话中断 | master 双重 reaper 检测 → 从池中移除 → 下次请求时重新 spawn |
| **Windows Terminal** (C++) | 宿主进程 | 所有子进程随 Job Object 终止 | 用户重启 WT（不可恢复） |

### Helper 侧 Master 崩溃检测

Helper 依赖 ACP 连接层的 `TransportDeath` 机制检测 master 断开：

1. **DeathWatchRead**：[`DeathWatchRead`](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs#L314-L342) 包装管道读端，第一次检测到真 EOF（`Ok(0)` on non-empty buffer）或错误时触发 `TransportDeath` latch
2. **AgentError 传播**：ACP 客户端任务检测到传输死亡，发送 `AppEvent::AgentError { failure: TransportLost, ... }`
3. **状态转移**：`App::handle_event` 将 `transport_lost` 设为 `true`，重绘 UI 显示断开横幅
4. **命令过滤**：slash command 补全列表过滤为仅 `/restart`，其他命令输入被拒绝并提示

### Master 侧 Helper 崩溃恢复

[`serve_helper()` 末尾的恢复逻辑](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2693-L2709)：

```rust
// helper 断开时（正常退出或崩溃）
let recovery = state.helper_meta.lock().await.remove(&helper_id);
if let Some(recovery) = recovery {
    if let Some(tab_id) = recovery.owner_tab_id {
        emit_restart_agent_pane(&tab_id, recovery.last_session_id.as_ref());
    }
}
```

1. **元数据记录**：`new_session`/`load_session` 时记录 `HelperRecoveryMeta { owner_tab_id, last_session_id }`
2. **断开清理**：`drop_sessions_for_helper()` 从路由表移除该 helper 的所有 session
3. **孤儿会话处理**：如果 Agent CLI 仍在运行（共享实例），session 加入 `orphaned_sessions` 供后续快速 rebind
4. **重启通知**：通过 WT 协议发送 `restart_agent_pane` 事件给 C++，携带 `owner_tab_id` 和可选的 `last_session_id`

### C++ 侧 Respawning

C++ 侧 `OnAgentPaneRestartRequested` 处理：

1. 检查关闭原因：用户主动关闭（Tab关闭、Ctrl+C×2）**不**重启
2. 意外断开时，调用 `AcquirePane(tabId, /*initialLoadSessionId=*/last_session_id)`
3. 新 helper spawn 时携带 `--initial-load-session-id` 参数
4. Helper 启动时合成 `WtEvent { method: "load_session" }`，自动恢复之前的会话内容

### Ctrl+C×2 优雅关闭

用户主动关闭路径（非崩溃）：

1. 第一次 Ctrl+C（输入框空且无 in-flight 请求）：设置 `close_pane_armed_at`，显示提示
2. 第二次 Ctrl+C 在 1500ms 窗口内：请求 WT 关闭 pane
3. WT 关闭 ConPTY → helper 收到 EOF → 正常退出 → master 清理路由但**不**触发重启

### TUI 终端状态保护

[`TuiRestoreGuard`](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L136-L166) RAII guard 确保即使 panic 也恢复终端：

```rust
impl Drop for TuiRestoreGuard {
    fn drop(&mut self) {
        if !self.armed { return; }
        let _ = disable_raw_mode();
        let mut stdout = io::stdout();
        let _ = execute!(stdout,
            DisableMouseCapture,
            SetCursorStyle::DefaultUserShape,
            LeaveAlternateScreen,
            Show
        );
    }
}
```

- 正常退出路径主动调用 `disarm()` 后手动清理（按正确顺序）
- panic/unwind 时 Drop 自动执行，用户不会留在损坏的 raw mode/alt screen

> **来源**：[`TuiRestoreGuard` 实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/helper/runtime.rs#L136-L166)、[`transport_lost` 处理](../../../../../external/libs/intelligent-terminal/tools/wta/src/app.rs#L905-L915)、[Master helper 恢复逻辑](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2693-L2709)

---

## 本章导航

- [上一章：WTA Master 多路复用器](03-wta-master.md)
- [返回目录](README.md)
- [下一章：C++ 集成](05-cpp-integration.md)
