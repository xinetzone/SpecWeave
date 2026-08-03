---
id: "intelligent-terminal-ch05-cpp-integration"
title: "第5章 - C++ 集成层"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第5章 C++ 集成层

C++ 集成层是 Intelligent Terminal 在 Windows Terminal 原生代码中的嵌入点，负责将 WTA (Windows Terminal Agent) 的 Rust 核心进程（wta-master + wta-helper）与终端 UI、XAML 控件、设置系统、COM 协议服务器无缝连接。本章详细解析 C++ 侧的核心组件、生命周期管理、进程隔离和 UI 集成机制。

## 5.1 C++ 集成层概述

Windows Terminal 主体通过 C++/WinRT 实现 Agent 功能的深度集成，集成层不重写任何终端逻辑，而是通过**包装、复用、扩展**现有机制实现：

1. **进程生命周期管理**：`SharedWta` 单例管理全局 wta-master 进程的引用计数生命周期、Job Object 包含、崩溃检测
2. **COM 协议桥接**：`TerminalProtocolComServer` 提供进程外 COM 服务器，供 wtcli/Rust 侧通过 `CoCreateInstance(CLSCTX_LOCAL_SERVER)` 访问终端状态
3. **UI 包装**：`AgentPaneContent` 是 XAML chrome 层，包裹内部的 `TermControl`（承载 wta-helper TUI）并提供顶部状态栏、Agent 图标、状态显示
4. **Tab 级隐藏/恢复**：per-tab stash/restore 机制实现 Agent Pane 的快速显示/隐藏（不销毁进程）
5. **Pre-warm 预热**：每个新终端 Tab 创建时自动预热一个隐藏的 Agent Pane，保证 autofix 功能从 Tab 打开时即可用
6. **设置集成**：GlobalAppSettings、MTSMSettings、AIAgents.xaml 设置 UI 提供 Agent 配置入口

**集成边界**：C++ 层不解析 ACP 协议内容，不管理 Agent CLI 子进程——所有业务逻辑在 Rust 的 wta-master/wta-helper 中实现，C++ 只负责：
- 进程 spawn/terminate/monitor
- XAML UI chrome
- COM 方法分发
- 事件路由
- 窗口/标签/窗格状态查询

> **来源**：[`SharedWta.h` 头部注释](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.h#L6-L26)

---

## 5.2 源码结构

Agent 相关 C++ 代码分布在 `src/cascadia/` 下的多个目录中：

| 目录 | 文件 | 职责 |
|------|------|------|
| **TerminalApp/** | [`SharedWta.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.h) / [`SharedWta.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.cpp) | wta-master 进程单例、引用计数、Job Object、崩溃检测 |
| | [`AgentPaneContent.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneContent.h) / [`AgentPaneContent.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneContent.cpp) / `AgentPaneContent.xaml` / `AgentPaneContent.idl` | Agent Pane XAML chrome 包装器、顶部状态栏、图标、autofix 状态 |
| | [`Tab.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Tab.h) / [`Tab.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Tab.cpp) | Tab 级 Agent Pane 查找、stash/restore、per-tab agent override |
| | [`TerminalPage.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/TerminalPage.h) / [`TerminalPage.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/TerminalPage.cpp) / [`TerminalPage.Protocol.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/TerminalPage.Protocol.cpp) | 主页面逻辑、Agent Pane 创建/销毁、事件处理、Protocol 方法实现 |
| | [`TabManagement.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/TabManagement.cpp) | Tab 初始化、pre-warm 触发、跨窗口拖拽重命名 |
| | [`AppActionHandlers.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AppActionHandlers.cpp) | Agent 相关快捷键 action 处理（OpenAgentPane、FocusAgentPane 等） |
| | [`AgentPaneLog.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneLog.h) | Agent Pane 调试日志宏 |
| | [`AgentPaneDragStash.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneDragStash.h) | 跨窗口拖拽 stash 状态 |
| **WindowsTerminal/** | [`TerminalProtocolComServer.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/WindowsTerminal/TerminalProtocolComServer.h) / [`TerminalProtocolComServer.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/WindowsTerminal/TerminalProtocolComServer.cpp) | 经典 COM 进程外服务器、MTA 线程、事件 fan-out、BoundedDispatchQueue |
| **TerminalProtocol/** | [`TerminalProtocol.idl`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalProtocol/TerminalProtocol.idl) | WinRT IDL 协议结构定义（WindowInfo/TabInfo/PaneInfo 等）、`IProtocolServer` / `IProtocolEventCallback` 接口 |
| | `ProtocolParsing.h` | SendEvent 路由分类解析 |
| **TerminalSettingsModel/** | `GlobalAppSettings.idl` / `MTSMSettings.h` | 全局设置模型、Agent 相关配置属性 |
| **TerminalSettingsEditor/** | `AIAgents.xaml` / `AIAgents.cpp` / `AIAgents.h` / `AIAgentsViewModel.h` | 设置 UI 中的 AI Agents 配置页面 |

---

## 5.3 TerminalPage 与 Agent 集成事件处理

`TerminalPage` 是 XAML 主页面，是所有 Agent 相关 UI 逻辑的汇聚点，负责：

### 5.3.1 ProtocolVtSequenceReceived 事件

`ProtocolVtSequenceReceived` 是 TerminalPage 上的 typed_event，当 TermControl 从 ConPTY 接收到特殊的 WT 协议 VT 序列时触发。这是 **wta-helper → Windows Terminal** 方向的主要上行通道：

```cpp
// TerminalPage.idl 中声明
event Windows.Foundation.TypedEventHandler<Object, String> ProtocolVtSequenceReceived;
```

在 `TerminalProtocolComServer::_ensurePageEventsRegistered()` 中，每个 TerminalPage 实例的 `ProtocolVtSequenceReceived` 被连接到 COM 事件 fan-out：

```cpp
// TerminalProtocolComServer.cpp:356-359
page.ProtocolVtSequenceReceived(
    [](auto&&, const winrt::hstring& eventJson) {
        s_NotifyEventToComClients(winrt::to_string(eventJson));
    });
```

wta-helper 通过发送特殊 VT 序列（OSC 序列封装的 JSON）触发此事件，COM 服务器将事件广播给所有订阅的 wtcli 客户端（主要是 wta-master）。

### 5.3.2 Agent 相关 Action 处理

AppActionHandlers.cpp 中处理 Agent 相关快捷键：

| Action | 处理函数 | 行为 |
|--------|----------|------|
| `OpenAgentPane` (Ctrl+Shift+.) | `_HandleOpenAgentPane` | 打开/恢复 Agent Pane；已 stash 则 restore，已可见在 chat 视图则关闭 |
| `OpenAgentSessions` (Ctrl+Shift+/) | `_HandleOpenAgentSessions` | 打开/切换 sessions 视图；stashed 则 restore 到 sessions 视图，可见在 sessions 则关闭 |
| `TriggerAutofix` | `_HandleTriggerAutofix` | 手动触发自动修复；打开 Agent Pane 并发送修复请求 |
| `FocusAgentPane` | `_HandleFocusAgentPane` | 焦点移至 Agent Pane |

所有 open/toggle 路径最终调用 `_OpenOrReuseAgentPane(intoSessionsView, reason)`，该函数统一处理：
- 已有可见 Pane → 切换视图或 stash
- 已有 stashed Pane → restore
- 无 Pane → `_AutoCreateHiddenAgentPaneShared()` 创建新的

### 5.3.3 COM 回调事件路由

TerminalPage 实现多个 `On*` 回调，由 `TerminalProtocolComServer` 的 UI 线程 dispatcher 调用：

| 回调 | 触发场景 |
|------|----------|
| `OnAutofixStateChanged` | wta 发送 autofix_state_changed 事件，更新 Pane 诊断状态 |
| `OnAgentStatusChanged` | wta 发送 agent_status 事件，更新 Agent 名称/版本/状态 |
| `OnAgentSwitchRequested` | 用户在 helper 中执行 `/agent` 切换 |
| `OnCloseAgentPaneRequested` | helper 中 Ctrl+C×2 请求关闭 Pane |
| `OnAgentStateChanged` | agent_state_changed 快照，驱动 Pane 创建/销毁/视图切换 |
| `OnResumeInNewAgentTabRequested` | sessions 视图 Shift+Enter 在新 Tab 恢复会话 |
| `OnAgentChipTargetChanged` | 覆盖 "Agent" 芯片标注目标 Pane |
| `OnRestartAgentStackRequested` | `/restart` 命令，重启整个 wta 栈 |
| `OnAgentPaneRestartRequested` | master 检测到 helper 崩溃，重新 spawn helper |

> **来源**：[`TerminalProtocolComServer.cpp` 事件分发](../../../../../../external/libs/intelligent-terminal/src/cascadia/WindowsTerminal/TerminalProtocolComServer.cpp#L1120-L1442)、[`AppActionHandlers.cpp` Agent 处理](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AppActionHandlers.cpp#L1636-L1770)

---

## 5.4 SharedWta 单例

`SharedWta` 是**进程级单例**（magic static），管理 wta-master 进程的完整生命周期，采用**引用计数模型**协调多窗口/多 Tab 的 master 共享。

### 5.4.1 核心设计原则

[`SharedWta.h` 头部注释](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.h#L6-L26)明确了设计契约：

1. **单例 per Terminal 进程**：一个 Windows Terminal 进程（可包含多个窗口）只有一个 wta-master
2. **引用计数生命周期**：每个 Agent Pane `AcquirePane()` → refcount++，`ReleasePane()` → refcount--；最后一个释放时通过 Job Object 终止 master
3. **惰性 spawn**：第一次 `AcquirePane()` 时才 spawn wta-master，不提前启动
4. **崩溃检测**：通过 `RegisterWaitForSingleObject` 监控 master 进程句柄，意外退出时设置 degraded 状态
5. **稳定管道名**：master 命名管道名在首次 acquire 时生成（GUID），跨 respawn 保持不变，旧 helper 可重连

### 5.4.2 关键数据成员

```cpp
// SharedWta.h:178-225
mutable std::mutex _mtx;
wil::unique_handle _process;          // master 进程句柄
wil::unique_handle _job;              // Job Object 句柄（KILL_ON_JOB_CLOSE）
HANDLE _waitHandle{ nullptr };        // RegisterWaitForSingleObject 返回的等待句柄
DWORD _pid{ 0 };                      // master PID
size_t _refCount{ 0 };                // 引用计数（每个 Agent Pane 一个引用）
std::wstring _masterPipeName;         // 命名管道名 \\.\pipe\wta-master-<GUID>
std::wstring _cachedWtaPath;          // 缓存的 wta.exe 路径，Restart() 时复用
std::vector<std::wstring> _cachedExtraArgs; // 缓存的命令行参数
bool _degraded{ false };              // 崩溃降级锁存器
```

### 5.4.3 CREATE_SUSPENDED 竞态防护

[`_SpawnLocked()`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.cpp#L244-L433) 使用 `CREATE_SUSPENDED` 标志创建子进程，这是关键的竞态防护：

```cpp
// SharedWta.cpp:319-324
// CREATE_SUSPENDED so the child can be placed inside the Job
// Object before it executes a single instruction. Without
// this, a Terminal crash in the microseconds between
// CreateProcessW and AssignProcessToJobObject would leak wta
// (no job → no KILL_ON_JOB_CLOSE containment).
DWORD creationFlags = CREATE_NO_WINDOW | CREATE_UNICODE_ENVIRONMENT | CREATE_SUSPENDED;
```

流程：
1. `CreateProcessW(CREATE_SUSPENDED)` → 创建挂起的子进程（不执行任何指令）
2. `CreateJobObjectW()` + `SetInformationJobObject(JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)` → 创建 Job Object
3. `AssignProcessToJobObject(job, process)` → 将挂起的子进程放入 Job
4. `RegisterWaitForSingleObject()` → 注册进程退出等待（必须在 ResumeThread 前设置）
5. `ResumeThread(thread)` → 子进程开始执行

如果中间任何一步失败，立即 `TerminateProcess(process, 1)` 防止泄漏悬挂进程。

### 5.4.4 Job Object 包含

Job Object 设置 `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE` 标志：
- 当 Terminal 进程退出时（正常或崩溃），最后一个 Job 句柄关闭 → OS 自动终止 Job 内所有进程（wta-master + 所有 wta-helper + 所有 Agent CLI 子进程）
- 当 refcount 归零时 `_job.reset()` 关闭 Job 句柄 → 立即终止整个 wta 进程树
- 无需递归遍历子进程 kill，OS 保证清理

### 5.4.5 Crash Detection 与 Degraded 状态

[`_OnProcessExited()`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.cpp#L466-L523) 是线程池等待回调，在 master 意外退出时执行：

1. **Stale callback 检测**：回调携带注册时的 PID，如果与当前 `_pid` 不匹配说明是旧 master 的回调，直接返回（避免 ABA 问题）
2. **状态清理**：重置 `_process`、`_job`、`_waitHandle`
3. **设置 degraded 锁存器**：如果 `_refCount > 0`（仍有 Pane 持有引用，说明是非正常退出）→ `_degraded = true`

**Degraded 状态的作用**：
- `AcquirePane()` 检测到 `!_process && _degraded` 时**不自动 respawn**，避免分裂脑（新 Pane 连到新 master，旧孤儿 helper 连不上）
- 所有 Agent Pane 一致显示"连接断开 - 请执行 /restart"状态
- 用户必须显式执行 `/restart` 命令（调用 `Restart()` 清除 degraded 并 respawn）才能恢复

### 5.4.6 多窗口 Fan-out 去重

[`Restart()`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.cpp#L127-L192) 有 500ms 去重窗口：

`/restart` 通过 COM 广播到所有窗口，每个窗口的 UI 线程都会调用 `SharedWta::Restart()`。如果不去重，窗口 B 的 Restart 会杀死窗口 A 刚 spawn 的新 master。使用 `_lastRestartRequest` 时间戳，500ms 内的重复 Restart() 直接返回 true（no-op）。

> **来源**：[`SharedWta.cpp` 完整实现](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.cpp#L1-L524)、[`SharedWta.h` 详细注释](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.h#L1-L227)

---

## 5.5 TerminalProtocolComServer（COM 进程外服务器）

`TerminalProtocolComServer` 是经典 COM（Classic COM）本地服务器（`CLSCTX_LOCAL_SERVER`），不是 WinRT 服务器。这是为了规避 WinRT MBM（Metadata-Based Marshaling）激活目录中的崩溃问题（0xc0000005 / 0x80010105）。

### 5.5.1 品牌化 CLSID

每个发布品牌（Release/Preview/Canary/Dev）有独立的 CLSID，避免不同渠道版本的 COM 注册冲突：

```cpp
// TerminalProtocolComServer.h:19-27
#if defined(WT_BRANDING_RELEASE)
#define __CLSID_TerminalProtocolServer "A2E4F6B8-1C3D-4E5F-A6B7-C8D9E0F1A2B3"
#elif defined(WT_BRANDING_PREVIEW)
#define __CLSID_TerminalProtocolServer "B3F5A7C9-2D4E-4F6A-B7C8-D9E0F1A2B3C4"
// ...
```

客户端（wtcli）通过环境变量 `WT_COM_CLSID` 发现正确的 CLSID，不需要硬编码。

### 5.5.2 MTA 线程模型

[`s_StartListening()`](../../../../../../external/libs/intelligent-terminal/src/cascadia/WindowsTerminal/TerminalProtocolComServer.cpp#L44-L94) 在专用 MTA 线程上注册 COM 类工厂：

```cpp
// TerminalProtocolComServer.cpp:59-88
g_comMtaThread = std::thread([&ready, &regHr]() {
    auto coInit = wil::CoInitializeEx(COINIT_MULTITHREADED);
    // Classic-COM class factory (WRL) — marshaled via the OpenConsoleProxy
    // proxy/stub, not WinRT MBM.
    const auto factory = Make<SimpleClassFactory<TerminalProtocolComServer>>();
    // ... CoRegisterClassObject ...
    WaitForSingleObject(g_comMtaStop.get(), INFINITE);
});
```

关键点：
- 专用 MTA 线程保持 COM 注册存活
- 传入 COM 调用在 MTA 工作线程上执行，不阻塞 UI/STA 线程
- 每个方法内部通过 `dispatcher.RunAsync()` 封送到 UI 线程查询 XAML 状态，然后 `.get()` 等待结果——因为在 MTA 线程上，`.get()` 不会死锁 UI 线程

### 5.5.3 异步事件投递与背压（BoundedDispatchQueue）

每个 COM 订阅者有独立的**有界 FIFO 队列**和**专用 MTA 投递线程**，解决 issue #239（慢客户端阻塞 UI 线程）：

```cpp
// TerminalProtocolComServer.h:78-118
// Each connected client (= one instance) owns a bounded FIFO queue drained
// by a dedicated MTA worker thread. The producer only ever ENQUEUES and
// returns immediately. The worker resolves the agile sink reference and
// makes the SYNCHRONOUS cross-process OnEvent call on its own thread — so
// a slow or blocked subscriber can no longer stall the terminal UI thread.
static constexpr size_t s_maxQueuedEvents = 4096;

struct _DeliveryState
{
    explicit _DeliveryState(size_t cap) : queue{ cap } {}
    Microsoft::Terminal::BoundedDispatchQueue<std::string> queue;
    std::mutex mutex;
    Microsoft::WRL::ComPtr<IAgileReference> sinkRef;
    bool workerStarted{ false };
};
```

生产者-消费者模型：
- **生产者**（UI/STA 线程上的 VT 事件、COM MTA 线程上的 SendEvent 广播）调用 `_enqueueEvent()` → 入队后立即返回，永不阻塞
- **消费者**（每个订阅者一个 detached MTA 线程）调用 `wait_pop()` → 解析 agile reference → 同步跨进程调用 `sink->OnEvent()`
- **背压**：队列满（4096 个事件）时丢弃最旧事件，防止内存无限制增长
- **Subscribe gate**：未订阅时队列不激活，事件直接丢弃

### 5.5.4 Agile Reference 跨公寓封送

事件 sink 通过 `RoGetAgileReference(AGILEREFERENCE_DEFAULT, IID_PPV_ARGS)` 存储为 agile reference，可以在任意公寓（MTA/STA）解析，不需要关心调用线程。投递线程解析得到当前公寓有效的代理后再调用 OnEvent。

### 5.5.5 无阻塞 Teardown

析构和 `Unsubscribe()` 从不 join 投递线程：
- 投递线程是 detached 的
- 通过 `queue.stop()` 通知线程退出
- 线程持有自己的 `shared_ptr<_DeliveryState>`，退出时自动释放
- 避免 OnEvent 回调中重入调用 Unsubscribe 导致死锁

### 5.5.6 ITerminalProtocol 方法分类

| 分类 | 方法 | 说明 |
|------|------|------|
| **Meta** | `Authenticate` | 兼容性握手（不做权限控制，COM 激活本身是信任边界） |
| | `GetCapabilities` | 返回支持的方法列表 |
| **查询** | `GetActivePane` / `ListWindows` / `ListTabs` / `ListPanes` | 窗口/标签/窗格枚举 |
| | `ReadPaneOutput` | 读取窗格输出（scrollback 或 marks） |
| | `GetProcessStatus` | 查询窗格进程状态 |
| | `GetSessionVariable` / `SetSessionVariable` | 会话变量读写 |
| | `GetSettings` | 读取 settings.json 内容 |
| **变更** | `CreateTab` / `SplitPane` | 创建标签/分屏 |
| | `ClosePane` / `FocusPane` | 关闭/聚焦窗格 |
| | `SendInput` | 向窗格发送输入 |
| **事件** | `Subscribe` / `Unsubscribe` | 订阅/取消事件回调 |
| | `SendEvent` | 客户端→WT 发送事件（restart/autofix/agent_state 等） |

> **来源**：[`TerminalProtocolComServer.cpp` 完整实现](../../../../../../external/libs/intelligent-terminal/src/cascadia/WindowsTerminal/TerminalProtocolComServer.cpp#L1-L1443)、[`TerminalProtocolComServer.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/WindowsTerminal/TerminalProtocolComServer.h#L1-L143)、[`TerminalProtocol.idl`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalProtocol/TerminalProtocol.idl#L1-L135)

---

## 5.6 AgentPaneContent（XAML chrome 包裹）

`AgentPaneContent` 是 XAML `UserControl`，实现 `IPaneContent` 接口，是 Agent Pane 在 Pane 树中的叶子节点。它**包装**而不是继承 `TerminalPaneContent`：内部持有一个 `TerminalPaneContent`（运行 wta-helper 的 TermControl），在其上方添加 36px 高的 XAML chrome 顶栏。

### 5.6.1 包装结构

```
┌─────────────────────────────────────────────────────────┐
│  AgentPaneContent (UserControl)                         │
│  ┌───────────────────────────────────────────────────┐  │
│  │  AgentBarRoot (36px 顶栏)                         │  │
│  │  [Logo] AgentName · Backend Version/Model         │  │
│  └───────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────┐  │
│  │  InnerContent.Content = _inner.GetRoot()          │  │
│  │  (= TermControl, wta-helper TUI)                  │  │
│  │                                                   │  │
│  │  这是实际的 ConPTY 终端                           │  │
│  └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

构造函数中完成装配：

```cpp
// AgentPaneContent.cpp:50-67
AgentPaneContent::AgentPaneContent(const winrt::TerminalApp::TerminalPaneContent& inner) :
    _inner{ inner }
{
    InitializeComponent();
    if (_inner)
    {
        InnerContent().Content(_inner.GetRoot());  // TermControl 放入 ContentPresenter
    }
    _wireInnerEvents();  // 转发内部 TerminalPaneContent 的事件
    _refreshLabel();
    _refreshLogo();
}
```

### 5.6.2 事件转发

`_wireInnerEvents()` 将内部 `TerminalPaneContent` 的所有 `IPaneContent` 事件（CloseRequested、ConnectionStateChanged、BellRequested、TitleChanged 等）转发为 AgentPaneContent 自身的事件，让 Tab/TerminalPage 无需知道包装层的存在，保持对普通 TerminalPaneContent 的同构处理。

### 5.6.3 Agent 图标与标签

顶栏显示 Agent 品牌 Logo + 名称/版本/模型：

- 图标通过 `_logoForAgent()` 按名称子串匹配（不区分大小写）：claude → Claude Logo，codex/gpt/openai → Codex Logo，gemini → Gemini Logo，opencode → OpenCode Logo，默认 Copilot Logo
- 标签格式：`<name> · <backend> <version>` 或 `<name> · <model>`（无版本时显示模型）
- Sessions 视图时标签变为 "Agent sessions"（或 "<name> sessions"）并隐藏 Logo

### 5.6.4 Autofix 状态投影

AgentPaneContent 缓存 per-tab autofix 诊断状态，供窗口底栏读取渲染：

```cpp
// AgentPaneContent.h:41-64
enum class AutofixState
{
    Idle,       // 无诊断
    Detected,   // 检测到错误
    Pending,    // 分析中
    Review,     // 修复建议等待查看
};
void ApplyAutofixState(AutofixState state, const hstring& paneId,
                       const hstring& summary, const hstring& fixPreview,
                       const hstring& hotkeyHint, const hstring& suggestionTitle);
```

任何底栏相关状态变化都触发 `StateChanged` 事件，TerminalPage 刷新窗口底栏。

### 5.6.5 跨窗口拖拽 Rename 支持

通过 `SetPendingRenameFromTabId()` / `TakePendingRenameFromTabId()` 暂存跨窗口拖拽前的源 Tab StableId。拖拽完成后新窗口的 Tab 初始化完成时，发送 `tab_renamed` WT 事件让 wta-helper 更新 `--owner-tab-id` 绑定。

> **来源**：[`AgentPaneContent.cpp`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneContent.cpp#L1-L493)、[`AgentPaneContent.h`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/AgentPaneContent.h#L1-L197)

---

## 5.7 Tab stash/restore 机制

Agent Pane 不采用"关闭即销毁"模型，而是使用 **stash（隐藏）/restore（恢复）** 机制。这是实现快速 toggle（Ctrl+Shift+.）、跨 toggle 保留会话历史、pre-warm 预热的基础。

### 5.7.1 为什么是隐藏而不是销毁

如果 toggle 时销毁 Pane：
- wta-helper 进程终止 → ACP 会话丢失
- 下次 toggle 需要重新 spawn helper、重新连接 master、重新建立 ACP session
- 聊天历史丢失，体验断裂
- Autofix 无法检测新打开终端的错误

Stash 模型只修改 XAML 视觉树，**底层 ConPTY、TermControl、wta-helper 进程全部存活**：
- toggle 无延迟，即时显示
- 会话历史、ACP 连接完整保留
- wta-helper 继续在后台接收事件（autofix 正常工作）

### 5.7.2 StashAgentPane 实现

[`Tab::StashAgentPane()`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Tab.cpp#L2530-L2592)：

```cpp
void Tab::StashAgentPane()
{
    const auto agentPane = FindAgentPane();
    if (!agentPane || agentPane->IsHidden()) return;
    const auto parent = _rootPane->_FindParentOfPane(agentPane);
    if (!parent) return;  // agent pane 是 root，无法折叠
    parent->HidePane(agentPane);  // 从 XAML 视觉树移除但保留 Pane 对象

    // 焦点恢复：HidePane 后 XAML 焦点悬空，需要显式聚焦终端兄弟 Pane
    const auto sibling = (parent->_firstChild == agentPane)
        ? parent->_secondChild : parent->_firstChild;
    // ... 聚焦 sibling TermControl（低优先级 dispatcher 延迟，等 XAML 布局完成）
}
```

关键细节：
- `Pane::HidePane()` 从 Grid children 中移除但不销毁 Pane 对象、不关闭 ConPTY 连接
- Stash 后通过低优先级 `DispatcherQueue::TryEnqueue` 延迟聚焦 sibling，因为刚 re-parent 的元素同步 Programmatic 焦点会静默丢失
- 如果 agent pane 是 root pane（整个 Tab 只有 agent pane，无兄弟终端），stash 是 no-op

### 5.7.3 RestoreStashedAgentPane 实现

[`Tab::RestoreStashedAgentPane()`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Tab.cpp#L2605-L2650+)：

```cpp
bool Tab::RestoreStashedAgentPane(SplitDirection /*direction*/)
{
    const auto agentPane = FindAgentPane();
    if (!agentPane || !agentPane->IsHidden()) return false;
    const auto parent = _rootPane->_FindParentOfPane(agentPane);
    if (!parent) return false;
    parent->RestorePane(agentPane);  // 重新加入 XAML 视觉树

    // 关键：显式聚焦 agent pane 的 TermControl
    // RestorePane 清空再重建 Grid children，XAML 焦点悬空，不聚焦则所有快捷键被吞
    _rootPane->FocusPane(agentPane);
    // 同样延迟 dispatcher 聚焦
}
```

### 5.7.4 相关 Tab 方法

| 方法 | 作用 |
|------|------|
| `FindAgentPaneContent()` | 遍历 Pane 树查找 AgentPaneContent 叶子 |
| `FindAgentPane()` | 查找承载 AgentPaneContent 的 Pane 节点 |
| `StashAgentPane()` | 隐藏 Agent Pane |
| `RestoreStashedAgentPane()` | 恢复隐藏的 Agent Pane |
| `HasStashedAgentPane()` | 查询是否有 stashed agent pane |
| `SetAgentChipOverride()` | 覆盖 "Agent" 蓝色芯片标注的目标 Pane |

> **来源**：[`Tab.cpp` Stash/Restore 实现](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Tab.cpp#L2527-L2660)、[`Tab.h` Agent 相关声明](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Tab.h#L105-L166)

---

## 5.8 Per-tab Pre-warm 机制

Pre-warm（预热）是提升用户体验的关键机制：**每个新终端 Tab 创建时，自动在后台创建一个 stashed（隐藏）的 Agent Pane**。wta-helper 进程启动、连接 master、完成 ACP 初始化握手，全部在后台完成，用户无感知。

### 5.8.1 为什么需要 Pre-warm

没有 pre-warm 时：
- 用户打开新 Tab，运行命令出错
- 按 Ctrl+Shift+. 打开 Agent Pane → 需要 spawn conpty → spawn wta-helper → helper 连接 master → ACP 握手 → TUI 渲染
- 整个过程 1-3 秒延迟，autofix 在 pane 打开前无法工作

Pre-warm 后：
- Tab 打开时 Agent Pane 已经在后台运行，ACP 连接已建立
- Ctrl+Shift+. 只是 XAML visual unhide → 即时显示
- Autofix 从 Tab 创建那一刻就能检测错误

### 5.8.2 Pre-warm 触发点

[`TabManagement.cpp` `_InitializeTab` 延迟执行](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/TabManagement.cpp#L226-L375)：

Pre-warm 在 Tab 初始化的低优先级 dispatcher tick 中触发：

```cpp
// TabManagement.cpp:226-240
// Per-tab model: pre-warm a stashed agent pane on every new terminal
// tab. The helper conpty child is spawned but the pane is immediately
// stashed via `Tab::StashAgentPane`, so the user only sees the
// terminal pane. Toggling the agent pane is just a stash/restore.
// The point of pre-warming is autofix: autofix routes through the
// agent helper, and gating it on "user has opened the pane at least
// once" silently broke autofix on every fresh tab.
```

触发条件：
- `agentLeavesSeen == 0`：Tab 是新建的普通终端 Tab，不是通过跨窗口拖拽带入 agent pane 的 Tab
- `_AutoCreateHiddenAgentPaneShared(tab, false, true)`：参数 `autoStash=true` 表示创建后立即 stash

### 5.8.3 _AutoCreateHiddenAgentPaneShared

`_AutoCreateHiddenAgentPaneShared()` 是创建 agent pane 的核心共享函数，pre-warm 和用户主动 toggle 都走这个路径。它：
1. 检测 wta.exe 路径
2. 构建 helper 命令行参数（`--connect-master <pipe>`、`--owner-tab-id <stableId>`、`--start-stashed` 等）
3. 调用 `SharedWta::AcquirePane()` 获取 master 引用
4. 创建 ConptyConnection + TerminalPaneContent
5. 包装为 AgentPaneContent
6. SplitPane 加入 Tab
7. 如果 `autoStash=true`，立即调用 `tab->StashAgentPane()` 隐藏

### 5.8.4 --start-stashed 命令行标志

`--start-stashed` 传递给 wta-helper，告知它 Pane 启动时处于隐藏状态：
- helper 启动后正常连接 master、完成 ACP initialize
- 但不主动发送可见性 UI 更新，不触发某些 UI 动画
- 当用户 restore pane 时，wta 通过 `pane_open` WT 事件得到通知

### 5.8.5 持久化跳过

注意：pre-warmed agent pane **不**持久化到保存的窗口布局（[`Pane.cpp:150-162`](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Pane.cpp#L150-L162)）。

原因：
- 保存的命令行包含上次运行时 master 的管道名（已失效）
- 上次的 `--owner-tab-id` 不再存在
- 重启后每个恢复的 Tab 会自动触发新的 pre-warm
- 持久化旧 agent pane 会导致"幽灵 pane"连接到死管道（issue #275）

所以 Pane 序列化时，如果 split 的一个子节点是 agent leaf，折叠 split 只序列化另一个子节点。

> **来源**：[`TabManagement.cpp` pre-warm 逻辑](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/TabManagement.cpp#L226-L380)、[`Pane.cpp` 持久化过滤](../../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/Pane.cpp#L146-L162)

---

## 5.9 Settings 模型与设置 UI

Agent 相关设置通过标准 Windows Terminal 设置管线暴露：IDL 定义 → MTSM 设置模型 → XAML 设置 UI。

### 5.9.1 GlobalAppSettings.idl

`GlobalAppSettings.idl`（TerminalSettingsModel）定义全局 Agent 设置属性，包括：
- Agent 默认选择（acpAgent）
- 模型选择（acpModel）
- Autofix 开关
- Agent Pane 默认位置（left/right/top/bottom）
- Agent 源（host/wsl/custom-command 等）
- WSL 发行版（当源是 wsl 时）
- 自定义命令
- 语言设置

### 5.9.2 MTSMSettings.h

`MTSMSettings.h` 提供宏和生成的设置属性访问器，是 IDL 到 C++ 实现的桥梁，定义 JSON 序列化/反序列化、属性变更通知、设置继承逻辑。

### 5.9.3 AIAgents.xaml 设置页

`TerminalSettingsEditor/AIAgents.xaml` 是设置 UI 中的 "AI Agents" 页面，提供：
- Agent 提供方选择下拉框（Copilot/Claude/Gemini/Codex/OpenCode/自定义）
- 模型选择
- Autofix 全局开关
- Agent Pane 默认位置选择
- WSL 集成配置
- 自定义命令/参数配置
- 认证状态显示（Copilot device-code 登录状态）

ViewModel（`AIAgentsViewModel.h`）处理设置变更、Agent 可用性检测、GPO 策略应用、安装状态检查。

### 5.9.4 Per-tab Agent Override

除了全局设置，每个 Tab 可以运行时覆盖 Agent/模型：

```cpp
// Tab.h:138-165
const hstring& AgentIdOverride() const noexcept;
const hstring& AgentModelOverride() const noexcept;
bool HasAgentOverride() const noexcept;
void SetAgentOverride(const hstring& agentId, const hstring& model,
                      const hstring& customCommand, const hstring& source,
                      const hstring& wslDistro);
void ClearAgentOverride() noexcept;
```

用户可以通过 Agent 图标弹出菜单为当前 Tab 临时切换 Agent/模型，不影响全局设置和其他 Tab。

---

## 5.10 C++ 组件调用关系图

```mermaid
graph TD
    subgraph "Windows 终端进程 (WindowsTerminal.exe)"
        subgraph "UI 层 (STA/XAML Thread)"
            TP[TerminalPage<br/>TerminalPage.cpp/h]
            TAB[Tab<br/>Tab.cpp/h]
            PANE[Pane<br/>Pane.cpp/h]
            APC[AgentPaneContent<br/>AgentPaneContent.cpp/h<br/>(XAML chrome)]
            TPC[TerminalPaneContent<br/>(TermControl wrapper)]
            TC[TermControl<br/>(XAML 终端控件)]
            AAH[AppActionHandlers<br/>快捷键处理]
            SET[AIAgents.xaml<br/>设置 UI]
        end

        subgraph "单例管理层"
            SW[SharedWta<br/>SharedWta.cpp/h<br/>(进程单例)]
            JOB[Job Object<br/>KILL_ON_JOB_CLOSE]
        end

        subgraph "COM 层 (MTA Thread Pool)"
            CS[TerminalProtocolComServer<br/>TerminalProtocolComServer.cpp/h<br/>(Classic COM Local Server)]
            BDQ[BoundedDispatchQueue<br/>per-subscriber 4K queue]
            DW[Delivery Worker<br/>detached MTA thread x N]
            ARS[AgileReference Sink]
        end
    end

    subgraph "Rust 进程树 (Job Object 包含)"
        WM[wta-master<br/>(单例 Rust 进程)]
        PIPE[Named Pipe<br/>\\.\pipe\wta-master-GUID]
        WH1[wta-helper Pane 1<br/>(TUI Ratatui)]
        WH2[wta-helper Pane 2<br/>(TUI Ratatui)]
        WHN[wta-helper Pane N<br/>(TUI Ratatui)]
        AGENT[Agent CLI<br/>(copilot/claude/...)]
    end

    subgraph "外部客户端"
        WTCLI[wtcli.exe<br/>(COM client)]
    end

    %% ── UI 层连接 ──
    TP -->|管理| TAB
    TAB -->|包含| PANE
    PANE -->|叶子| APC
    APC -->|包装| TPC
    TPC -->|持有| TC
    TP -->|快捷键分发| AAH
    AAH -->|_OpenOrReuseAgentPane| TP
    SET -->|设置变更| TP

    %% ── Tab stash/restore ──
    TAB -.->|StashAgentPane<br/>RestoreStashedAgentPane| PANE
    TAB -->|FindAgentPaneContent| APC
    TP -->|pre-warm _AutoCreateHiddenAgentPaneShared| TAB

    %% ── SharedWta 连接 ──
    TP -->|AcquirePane/ReleasePane| SW
    TP -->|Restart| SW
    SW -->|CreateProcessW CREATE_SUSPENDED| WM
    SW -->|AssignProcessToJobObject| JOB
    JOB -.->|包含| WM
    SW -->|RegisterWaitForSingleObject<br/>crash detection| WM

    %% ── wta-master 与 helper 关系 ──
    WM -->|listen| PIPE
    WH1 -->|connect| PIPE
    WH2 -->|connect| PIPE
    WHN -->|connect| PIPE
    WM -->|spawn/管理| AGENT
    JOB -.->|包含| WH1
    JOB -.->|包含| WH2
    JOB -.->|包含| WHN
    JOB -.->|包含| AGENT

    %% ── ConPTY 连接 ──
    TC -->|ConPTY 伪终端| WH1
    note over TC,WH1:每个 Agent Pane 的 TermControl<br/>通过 ConPTY 附着到 wta-helper stdio

    %% ── COM 层连接 ──
    WTCLI -->|CoCreateInstance<br/>CLSCTX_LOCAL_SERVER| CS
    CS -->|Subscribe<br/>RoGetAgileReference| BDQ
    BDQ -->|wait_pop| DW
    DW -->|Resolve + OnEvent| ARS
    ARS -->|跨进程回调| WTCLI

    %% ── VT 协议上行 ──
    TC -->|ProtocolVtSequenceReceived<br/>(OSC JSON)| TP
    TP -->|raise event| CS
    CS -->|s_NotifyEventToComClients| BDQ

    %% ── COM 方法调用下行 ──
    WTCLI -->|ListPanes/ReadPaneOutput/SendInput/SendEvent| CS
    CS -->|RunAsync to UI thread| TP
    TP -->|查询/操作| TAB
    TP -->|查询/操作| PANE
    CS -->|SendEvent 路由| TP

    %% ── 样式高亮 ──
    style SW fill:#f96,stroke:#333,stroke-width:2px
    style CS fill:#9cf,stroke:#333,stroke-width:2px
    style APC fill:#9f9,stroke:#333,stroke-width:2px
    style WM fill:#ff9,stroke:#333,stroke-width:2px
    style JOB fill:#f96,stroke:#333,stroke-dasharray:5,5
```

### 调用关系说明

1. **UI 线程（STA）**：所有 XAML 操作、Tab/Pane 管理、快捷键处理、AgentPaneContent chrome 都在单线程 UI 公寓
2. **SharedWta 单例**：通过 mutex 保护跨线程访问，master 进程句柄、Job Object、引用计数集中管理
3. **COM MTA 线程池**：COM 注册在专用 MTA 线程，每个订阅者有独立投递线程，慢客户端不阻塞 UI
4. **VT 上行路径**：wta-helper → ConPTY → TermControl → ProtocolVtSequenceReceived → COM fan-out → wtcli/wta-master
5. **COM 下行路径**：wtcli → COM 方法调用 → MTA 接收 → RunAsync 封送到 UI 线程 → TerminalPage/Tab/Pane 查询或操作
6. **进程隔离边界**：所有 Rust 代码（wta-master/wta-helper/Agent CLI）都在 Job Object 中，WT 崩溃时 OS 自动清理
7. **Pre-warm 路径**：Tab 初始化 → 低优先级 dispatcher → 创建 stashed AgentPaneContent → AcquirePane → spawn helper → StashAgentPane 隐藏

> **来源**：本章所有 C++ 源码文件综合分析

---

## 本章导航

- [上一章：WTA Rust 核心 - Helper 与 TUI](04-wta-helper-tui.md)
- [返回目录](README.md)
- [下一章：通信协议栈](06-protocols.md)
