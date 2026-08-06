---
id: "intelligent-terminal-ch03-wta-master"
title: "第3章 - WTA Rust 核心 - Master 多路复用器"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# 第3章 WTA Rust 核心 - Master 多路复用器

## 3.1 wta-master 概述

`wta-master` 是 Helper+Master 架构的核心单例进程，承担 ACP（Agent Client Protocol）多路复用器的角色。它由 C++ 侧的 `SharedWta` 单例延迟 spawn，在整个 Windows Terminal 进程生命周期中唯一存在，负责所有 `wta-helper` 与 Agent CLI 之间的消息路由。

**核心职责**：

1. **Agent CLI 子进程管理**：spawn Agent CLI 子进程（copilot/claude/gemini/codex 等），将其 stdio 包装为 ACP 客户端连接（master 扮演 Agent CLI 的 client 角色）
2. **命名管道服务**：监听指定命名管道，接受每个 wta-helper 的连接
3. **ACP 消息多路复用**：对每个 helper 连接运行 ACP Agent 侧连接（master 扮演 helper 的 agent 角色），实现双向消息路由
4. **Session 路由表**：维护 `SessionId → Helper` 映射，确保 agent 通知准确送达所属 helper
5. **崩溃检测与恢复**：检测 agent CLI 或 helper 断开，触发自动恢复机制

> **来源**：[tools/wta/src/master/mod.rs 头部注释](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1-L38)、[OVERVIEW.md §wta-master](../../../../../external/libs/intelligent-terminal/tools/wta/OVERVIEW.md#L42-L59)

**单例模式要点**：

- 由 `SharedWta` 通过引用计数管理生命周期：第一个 Agent Pane 请求时 spawn，最后一个 Pane 关闭时通过 Job Object 终止
- Agent CLI 采用**延迟 spawn**策略：不再启动时立即 spawn，而是在第一个 helper 的 `initialize` 握手时根据请求的 agent_id 懒加载
- 支持**多 Agent CLI 池**：不同 helper 可选择不同 agent（如一个 Tab 用 Gemini，另一个用 Claude），master 维护 agent 进程池

---

## 3.2 源码结构

`tools/wta/src/master/` 目录结构简洁：

| 文件 | 职责 | 代码行数 |
|------|------|----------|
| [`mod.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs) | Master 核心实现：启动流程、连接处理、消息路由、Session 管理 | ~3400 行 |
| [`config.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/config.rs) | Master 配置结构体：agent 命令、agent_id、允许列表 | 6 行 |
| [`tests.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/tests.rs) | 单元测试（内嵌于 mod.rs 末尾） | 集成于 mod.rs |

**关键依赖模块**：

| 模块 | 位置 | 用途 |
|------|------|------|
| ACP 连接兼容层 | [`protocol/acp/conn.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs) | `ClientLink`/`AgentLink` 封装，提供旧版连接 API |
| Agent spawn | [`protocol/acp/spawn.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/spawn.rs) | `spawn_agent_process_for_source` 跨平台 agent 进程启动 |
| Session Registry | [`session_registry.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/session_registry.rs) | 内存中 Session 注册表，维护会话元数据 |

> **来源**：[tools/wta/src/master/ 目录](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/)

---

## 3.3 Master 启动流程

Master 启动遵循严格的顺序：日志初始化 → hooks 自动升级 → CliChannel 连接 → 状态初始化 → 命名管道监听 → accept 循环。

### 启动时序图

```mermaid
sequenceDiagram
    participant SW as SharedWta(C++)
    participant Master as wta-master
    participant Hooks as agent_hooks_installer
    participant WT as wtcli/COM
    participant Watcher as session_watcher
    participant Pipe as NamedPipe
    
    SW->>Master: CREATE_SUSPENDED spawn<br/>wta.exe --master &lt;pipe&gt;
    SW->>SW: Assign to Job Object
    SW->>Master: ResumeThread()
    
    Note over Master: run_master_mode()
    Master->>Master: tracing 初始化（main中已完成）
    Master->>Master: 验证 --agent 参数非空
    
    par hooks 自动升级（后台）
        Master->>Hooks: spawn_blocking<br/>upgrade_installed_hooks()
        Hooks-->>Master: 完成（~10ms 缓存快路径）
    end
    
    Master->>Master: LocalSet::new() 创建本地任务集
    Master->>Master: run_master_loop()
    
    Master->>WT: CliChannel::connect()
    alt 连接成功
        WT-->>Master: CliChannel 实例
        Master->>WT: subscribe_events()
        Master->>WT: start_reader()
    else WT 不可用
        Master->>Master: wt = None，降级运行
    end
    
    Master->>Master: 构建 MasterStateInner<br/>初始化所有 HashMap/OnceLock
    Master->>Master: normalize_allowed_agent_ids()<br/>解析 GPO 允许列表
    
    par Session Watcher（后台线程）
        Master->>Watcher: thread::spawn(watch)
        Watcher->>Master: bridge thread → mpsc 转发事件
        Master->>Master: apply_watcher_event() 处理
    end
    
    par WT 事件订阅（后台）
        Master->>WT: recv() 事件循环
        WT-->>Master: connection_state 事件
        Master->>Master: handle_master_wt_event()
    end
    
    Master->>Master: build_pipe_security_attributes()<br/>构建安全 DACL（仅当前用户+SYSTEM）
    Master->>Pipe: create_master_pipe_instance(first_instance=true)
    Pipe-->>Master: NamedPipeServer
    
    Master->>Master: MasterPipeDiscoveryGuard::write()<br/>写入 master-pipe.txt
    Master->>Master: 进入 accept loop
    
    loop accept 循环
        Master->>Pipe: connect().await
        Pipe-->>Master: 新 helper 连接
        Master->>Master: 分配 HelperId(单调递增)
        Master->>Pipe: create follow-up instance
        Master->>Master: spawn_local(serve_helper)
    end
```

> **来源**：[`run_master_mode()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1507-L1568)、[`run_master_loop()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1808-L2034)

**关键启动要点**：

1. **延迟 Agent Spawn**：Master 启动时**不**立即 spawn Agent CLI，而是在第一个 helper 的 `initialize` 请求到达时，通过 `get_or_spawn_agent()` 懒加载
2. **安全加固**：命名管道使用自定义 SDDL 安全描述符 `D:P(A;;GA;;;SY)(A;;GA;;;<user>)S:(ML;;NW;;;ME)`，仅授予 SYSTEM 和当前用户完全控制，添加中等完整性级别标签阻止低完整性进程访问
3. **管道发现文件**：Master 启动时写入 `master-pipe.txt` 到运行时路径，退出时（通过 Drop guard）自动清理
4. **后台任务并行**：hooks 升级、session watcher、WT 事件订阅均在独立任务/线程中运行，不阻塞主 accept 循环

---

## 3.4 Agent CLI 子进程管理

Agent CLI 采用**池化懒加载**策略：master 维护 `AgentCmdKey → Arc<OnceCell<Arc<AgentCli>>>` 映射，相同命令行的 helper 共享同一个 Agent CLI 进程。

### Spawn 流程

[`get_or_spawn_agent()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2164-L2195) 实现了安全的并发 spawn：

1. **键计算**：通过 `agent_cmd_key(command, source)` 生成 `"{source}\0{command}"` 格式的唯一键
2. **OnceCell 竞争**：两个 helper 同时请求相同 agent 时，在 per-key `OnceCell` 上序列化，只有一个执行 spawn，另一个 await 同一个 `AgentCli`
3. **不同 Agent 并行**：不同 agent 的 spawn 完全并行，外层 `Mutex` 仅在 get/insert `OnceCell` 时持有，绝不跨 await

### [`spawn_one_agent()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2202-L2479) 详细步骤

```rust
async fn spawn_one_agent(state, key, agent_cmd, agent_id, source) -> Result<Arc<AgentCli>> {
    // 1. spawn 子进程（npx/直接命令）
    let spawn_result = spawn_agent_process_for_source(agent_cmd, None, source)?;
    
    // 2. 获取 stdin/stdout/stderr
    let stdin = child.stdin.take().ok_or(...) ?;
    let stdout = child.stdout.take().ok_or(...) ?;
    let stderr_log = AgentStderrLog::new(key.to_string());
    let stderr_task = stderr.map(|stderr| stderr_log.drain(stderr));
    
    // 3. 构建 MasterClient（处理 agent→master 请求）
    let client = MasterClient { state: Arc::clone(state) };
    let builder = acp::Client.builder()
        .name("wta-master")
        .on_receive_request(...)  // request_permission/create_terminal/...
        .on_receive_notification(...)  // session_notification
    
    // 4. 通过 conn 兼容层 spawn client 连接
    let (conn, handle_io) = conn::spawn_client(builder, conn::byte_streams(stdin, stdout));
    
    // 5. spawn I/O 循环任务 + reaper
    tokio::task::spawn_local(async move {
        match handle_io.await {
            Ok(()) => info!("agent I/O ended cleanly"),
            Err(e) => error!("agent I/O error: {e}"),
        }
        reap_agent(&state, &key).await;  // 从池中移除
    });
    
    // 6. ACP initialize 握手（带超时：npx 60s，其他 15s）
    let init_resp = tokio::time::timeout(init_timeout, conn.initialize(req)).await?;
    
    // 7. 安装子进程 wait reaper
    tokio::task::spawn_local(async move {
        let status = child.wait().await;
        error!("agent CLI exited: {status:?}");
        reap_agent(&state, &key).await;
    });
    
    // 8. 缓存 initialize 响应，触发历史 seed
    let _ = state.cached_init_resp.set(init_resp.clone());
    if state.agent_conn.set(conn.clone()).is_ok() {
        tokio::task::spawn_local(async move {
            seed_host_and_broadcast(&state).await;
            spawn_wsl_seed(&state);
        });
    }
    
    Ok(Arc::new(AgentCli { conn, cached_init_resp, cli_source, source, cmd_key }))
}
```

### 生命周期管理

| 机制 | 实现位置 | 说明 |
|------|----------|------|
| **I/O 循环 reaper** | [`spawn_one_agent` L2347-L2366](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2347-L2366) | ACP 连接 I/O 循环结束时调用 `reap_agent` 从池中移除 |
| **子进程 wait reaper** | [`spawn_one_agent` L2424-L2437](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2424-L2437) | `child.wait().await` 返回时调用 `reap_agent` |
| **池清理** | [`reap_agent()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2486-L2500) | 从 `state.agents` 移除，清空该 agent 的 orphaned_sessions |
| **初始化失败清理** | [`spawn_one_agent` L2402-L2418](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2402-L2418) | init 失败/超时时 kill 子进程，stderr 日志提升为 warning |

**关键设计决策**：Agent CLI 死亡**不**终止 master 进程，仅从池中移除该 agent。其他 agent 的 helper 继续正常工作；下一个请求该 agent 的 helper 将触发重新 spawn。

> **来源**：[`AgentCli` 结构体](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L343-L365)、[`spawn_one_agent` 完整实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2202-L2479)

---

## 3.5 命名管道服务

Master 通过 Windows 命名管道接收 helper 连接，管道名称由 C++ 侧通过 `--master <pipe-name>` 参数传入。

### 管道名称格式

```
\\.\pipe\wta-master-<GUID>
```

GUID 由 C++ 侧 `SharedWta` 生成，确保每个 WT 进程唯一。

### 管道安全

[`build_pipe_security_attributes()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1748-L1785) 实现了纵深防御安全机制：

1. **获取当前用户 SID**：`current_user_sid_string()` 通过 Win32 API `OpenProcessToken` → `GetTokenInformation` → `ConvertSidToStringSidW` 获取
2. **构建 SDDL 字符串**：
   - `D:P`：Protected DACL（不继承）
   - `(A;;GA;;;SY)`：SYSTEM 拥有 GENERIC_ALL
   - `(A;;GA;;;<user>)`：当前用户拥有 GENERIC_ALL
   - `S:(ML;;NW;;;ME)`：中等完整性级别标签，No-Write-Up（阻止低完整性/ AppContainer 同用户代码）
3. **拒绝远程连接**：`ServerOptions::reject_remote_clients(true)` 强制仅本地连接
4. **优雅降级**：安全描述符构建失败时回退到默认 ACL，不阻止 master 启动

### Accept 循环

[`run_master_loop` L1987-L2033](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1987-L2033) 实现标准 Windows 命名管道 accept 模式：

```rust
loop {
    server.connect().await?;  // 等待连接
    
    let helper_id = HelperId(next_helper_id);
    next_helper_id = next_helper_id.wrapping_add(1);
    
    // 立即创建 follow-up 实例，允许下一个 helper 并发连接
    let connected = std::mem::replace(
        &mut server,
        create_master_pipe_instance(&pipe_name, false, pipe_security.as_ref())?,
    );
    
    // spawn 独立任务处理该 helper 连接
    tokio::task::spawn_local(async move {
        let result = serve_helper(helper_id, connected, inner).await;
        // 记录 live_helpers 计数
    });
}
```

**关键实现要点**：
- `first_pipe_instance(true)` 仅用于第一个实例，后续实例传 `false`
- 连接建立后**立即**创建新的管道实例，实现并发连接接受
- 每个 helper 连接在独立的 `spawn_local` 任务中处理，互不阻塞
- `live_helpers` 原子计数器跟踪并发连接数，connect/disconnect 均打日志

> **来源**：[`create_master_pipe_instance()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1791-L1806)、[`PipeSecurity` 结构体](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1654-L1677)

---

## 3.6 MuxConnection 处理

每个 helper 连接由独立的 [`serve_helper()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2505-L2712) 任务处理，构成 master 的 per-helper 多路复用连接。

### serve_helper 流程

```rust
async fn serve_helper(helper_id: HelperId, pipe: NamedPipeServer, state: Arc<MasterStateInner>) -> Result<()> {
    // 1. 创建通知通道（bounded mpsc，容量 1024）
    let (notif_tx, mut notif_rx) = mpsc::channel(NOTIF_CHANNEL_CAPACITY);
    
    // 2. 创建 ExtNotification 通道（unbounded）
    let (ext_tx, mut ext_rx) = mpsc::unbounded_channel();
    state.helper_ext_subscribers.lock().await.insert(helper_id, ext_tx);
    
    // 3. 创建 AgentLink slot（OnceLock + Weak 打破循环引用）
    let agent_side_slot: Arc<OnceLock<conn::AgentLink>> = Arc::new(OnceLock::new());
    
    // 4. 构建 HelperHandler
    let handler = HelperHandler {
        helper_id,
        agent: Arc::new(OnceLock::new()),  // initialize 时填充
        state: Arc::clone(&state),
        notif_tx,
        agent_side_slot: Arc::clone(&agent_side_slot),
    };
    
    // 5. 拆分管道为 read/write half
    let (read_half, write_half) = tokio::io::split(pipe);
    
    // 6. 构建 ACP Agent builder + spawn_agent
    let builder = acp::Agent.builder()
        .name("wta-master-helper")
        .on_receive_request(...)  // initialize/new_session/prompt/...
        .on_receive_notification(...);  // cancel
    
    let (agent_side_conn, handle_io) = conn::spawn_agent(builder, byte_streams(outgoing, incoming));
    let _ = agent_side_slot.set(agent_side_conn.clone());
    
    // 7. tokio::select! 主循环
    let result = loop {
        tokio::select! {
            io_result = &mut handle_io => break io_result.map_err(|e| anyhow!(e)),
            Some(notif) = notif_rx.recv() => {
                // 转发 agent session_notification 到 helper
                agent_side_conn.session_notification(notif).await?;
            }
            Some(ext) = ext_rx.recv() => {
                // 转发 ExtNotification 到 helper
                agent_side_conn.ext_notification(ext).await?;
            }
            else => break Ok(()),
        }
    };
    
    // 8. 清理：取消 ext 订阅
    state.helper_ext_subscribers.lock().await.remove(&helper_id);
    
    // 9. 清理该 helper 的所有 session 路由
    let victims = drop_sessions_for_helper(&state, helper_id).await;
    
    // 10. 记录 orphan sessions（shared CLI 仍加载着）
    if !victims.is_empty() {
        if let Some(agent) = handler.agent.get() {
            // 仅当该 CLI 仍是 live 池实例时记录
            if still_live {
                state.orphaned_sessions.lock().await
                    .entry(agent.cmd_key.clone())
                    .or_default()
                    .extend(victims.clone());
            }
        }
    }
    
    // 11. 崩溃恢复：发送 restart_agent_pane 事件
    if let Some(recovery) = state.helper_meta.lock().await.remove(&helper_id) {
        if let Some(tab_id) = recovery.owner_tab_id {
            emit_restart_agent_pane(&tab_id, recovery.last_session_id.as_ref());
        }
    }
    
    result
}
```

### 双通道设计

每个 helper 连接维护两个独立的通知通道：

| 通道 | 类型 | 用途 |
|------|------|------|
| `notif_tx`/`notif_rx` | bounded mpsc (1024) | 转发 Agent CLI 的 `session_notification`（消息 chunk、tool call 等高吞吐流量） |
| `ext_tx`/`ext_rx` | unbounded mpsc | 转发 master 发起的 `ExtNotification`（session_added/removed/changed 等控制面通知） |

分离设计的原因：
- 防止高吞吐的 chunk streaming 阻塞低频率的 live-set 广播
- `tokio::select!` 可以直接分派到对应写入方法，无需 enum 判别

> **来源**：[`serve_helper()` 完整实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2505-L2712)、[`NOTIF_CHANNEL_CAPACITY` 常量](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L44-L50)

---

## 3.7 ACP 消息路由

Master 是一个**透明双向代理**，在 helper 和 Agent CLI 之间路由所有 ACP 消息，但做少量关键拦截和增强。

### 路由路径总览

```
┌─────────────┐                      ┌─────────────┐                      ┌─────────────┐
│   Helper    │                      │   Master    │                      │  Agent CLI  │
│  (client)   │                      │  (mux)      │                      │  (server)   │
└──────┬──────┘                      └──────┬──────┘                      └──────┬──────┘
       │                                    │                                    │
       │  initialize ─────────────────────> │  ── resolve_agent_selection ──>   │
       │                                    │  ── get_or_spawn_agent ──────>    │
       │  <─── cached_init_resp ──────────  │  <─── init resp (cache) ────────  │
       │                                    │                                    │
       │  new_session ────────────────────> │  ── forward to agent ─────────>   │
       │                                    │    (pre-route or post-route?)      │
       │  <─── session_id ────────────────  │  <─── new SessionId ────────────  │
       │    (route recorded atomically)     │  ── insert session_to_helper ──    │
       │                                    │  ── upsert registry ──────────    │
       │                                    │  ── broadcast session_added ──    │
       │                                    │                                    │
       │  prompt ────────────────────────> │  ── prompt_forwarding ────────>   │
       │    (non-blocking, no await)        │    (注册 on_response callback)     │
       │                                    │                                    │
       │  <─── session/update chunks ─────  │  <─── session_notification ─────  │
       │    (via notif_tx channel)          │  ── lookup session_to_helper ──    │
       │                                    │  ── try_send to notif_tx ─────    │
       │                                    │                                    │
       │                                    │  ──── request_permission ──────>  │
       │  <─── permission UI request ─────  │  <─── route_for(sid) ──────────   │
       │    (TUI弹窗，用户确认/拒绝)          │  ── forward to helper AgentLink    │
       │  ──── permission response ──────>  │  ──── response to agent ──────>   │
       │                                    │                                    │
       │                                    │  ──── create_terminal ─────────>  │
       │  <─── terminal create request ───  │  <─── route_for(sid) ──────────   │
       │    (ShellManager → wtcli/COM)      │  ── forward to helper              │
       │  ──── terminal response ────────>  │  ──── response to agent ──────>   │
```

### Helper→Agent 方向（请求转发）

由 [`HelperHandler`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L813-L946) 处理，每个 helper 拥有独立实例：

| ACP 方法 | 处理方式 | 关键增强 |
|----------|----------|----------|
| `initialize` | 不转发到 agent！解析 `_meta.wta`，调用 `resolve_agent_selection` + `get_or_spawn_agent`，返回 agent 的 `cached_init_resp` | 安全：从不执行管道传来的命令字符串，仅从已知 agent_id 重建命令；agent 懒加载 |
| `authenticate` | 直转发到 `agent.conn.authenticate()` | - |
| `new_session` | 带超时（120s）转发到 agent，**响应返回前**原子性插入 `session_to_helper` + registry | 原子路由记录防止竞态：agent 可能在响应前就发 `session_notification`；超时保护防止 agent 挂起导致 helper 死锁 |
| `load_session` | **预注册路由**（已知 SessionId），支持 orphan 快速路径重绑定 | 预注册解决"resume 时历史 chunk 丢失"问题；孤儿会话检测避免 "already loaded" 错误 |
| `prompt` | 使用 `prompt_forwarding` **非阻塞**转发，注册 `on_response` callback | 关键：await 会阻塞 dispatch 循环导致 agent 中途的 `request_permission` 无法读回，造成跨循环死锁 |
| `cancel` | 直转发 | - |
| `set_session_mode`/`set_session_config_option` | 直转发 | - |
| `list_sessions` | **不转发**！直接从 master 自己的 `registry.snapshot()` 回答 | 合并 live sessions + host history + WSL sessions，返回 master 视角的权威列表 |
| `ext_method` | 本地处理 `_intellterm.wta/*` 方法，未知方法转发到 agent | 编译时穷举匹配，新方法必须显式处理否则编译错误 |

### Agent→Helper 方向（通知/请求路由）

由 [`MasterClient`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L392-L790) 处理，全局唯一实例：

| ACP 方法 | 路由方式 | 关键保护 |
|----------|----------|----------|
| `session_notification` | 查 `session_to_helper`，`try_send` 到 `notif_tx`（不 await！） | 背压控制：队列满时**丢弃 chunk + 日志限流**（首次丢打 warn，恢复时打 info 汇总），绝不阻塞 agent I/O 循环导致所有 helper 冻结 |
| `request_permission` | 查 `session_to_helper`，调用 `forwarder.request_permission()` | 孤儿会话返回 `Cancelled`（而非错误），防止 agent 断连整个共享连接 |
| `create_terminal`/`terminal_*`/`read_text_file`/`write_text_file`/`kill_terminal` | 同上，转发到 helper 的 `AgentLink` | 所有终端/文件操作在 helper 侧执行（TUI 权限弹窗、ShellManager），master 仅路由 |

### 背压与流控设计

[`session_notification`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L513-L665) 的背压处理是 master 最关键的可靠性设计之一：

1. **使用 `try_send` 而非 `send().await`**：helper 管道慢时绝不阻塞 agent CLI 的 I/O 循环——队头阻塞会冻结所有共享该 master 的 helper
2. **有界队列（1024）**：防止 helper 完全卡住时内存无限制增长
3. **日志限流**：每个 stall 周期只打两条日志（开始 warn + 恢复 info），避免日志风暴
4. **`consecutive_drops` 计数器**：跟踪连续丢弃的 chunk 数，恢复时汇总报告
5. **rebind 竞态保护**：`try_send` 返回 `Closed` 时，先检查 `helper_id` 是否仍匹配再删除路由，防止 helper A 断开→helper B 用相同 SessionId rebind 时误删新路由

> **来源**：[`HelperHandler` 实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L948-L1505)、[`MasterClient` 实现](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L465-L790)、[`notification_kind()` 日志标签](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L795-L808)

---

## 3.8 SessionId 路由表

Session 路由是 master 的核心状态，由 `MasterStateInner.session_to_helper: Mutex<HashMap<SessionId, HelperRoute>>` 维护。

### HelperRoute 结构

[`HelperRoute`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L91-L115) 是 per-session 路由条目：

```rust
struct HelperRoute {
    helper_id: HelperId,                     // 所属 helper 标识（单调递增 u64）
    notif_tx: mpsc::Sender<SessionNotification>,  // 通知发送端
    forwarder: Option<conn::AgentLink>,      // helper 的 AgentLink（用于 agent→helper 请求）
    consecutive_drops: Arc<AtomicU64>,       // 背压丢包计数器
}
```

两个反向路径共享此条目：
- `notif_tx`：`session_notification` 发往此通道，helper 的 serve 循环排出并写回管道
- `forwarder`：`request_permission`/`create_terminal`/`fs/*` 直接调用此连接上的方法，作为 RPC 重新发给 helper

### 路由原子性保证

**new_session 原子记录**（[`HelperHandler::new_session` L1061-L1075](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1061-L1075)）：

```rust
// 响应返回给 helper BEFORE 记录路由？NO！
// 在返回响应前插入路由表，消除竞态窗口
let resp = self.forward_new_session_to_agent(args, timeout).await?;
let forwarder = self.forwarder_for_route("new_session")?;
{
    let mut map = self.state.session_to_helper.lock().await;
    map.insert(resp.session_id.clone(), HelperRoute { ... });  // 先插入
}
self.state.registry.upsert(info.clone()).await;
// 然后才返回响应给 helper
```

**为什么必须先记录再返回？** Agent 实现可能在 `session/new` 响应返回前就开始发送 `session_notification`（例如立即发送 "thinking" chunk）。如果先返回响应再记录路由，这些早期通知会命中"unknown SessionId" 被丢弃——用户可见症状是"恢复会话时看不到历史回滚"。

**load_session 预注册**（[`HelperHandler::load_session` L1187-L1200](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1187-L1200)）更激进——因为 SessionId 是请求输入（已知），在**发送 load 请求之前**就预注册路由，解决 agent 回放历史 burst 通知的竞态：

```rust
// 与 new_session 不同，load_session 的 SessionId 已知——预注册！
{
    let mut map = self.state.session_to_helper.lock().await;
    map.insert(session_id.clone(), HelperRoute { ... });  // 先发请求前就注册
}
// 然后才发 load_session 给 agent
```

### Orphan Session 机制

当 helper 断开（Tab 关闭）但其共享 Agent CLI 仍加载着该会话时，该会话成为"孤儿"：

1. [`serve_helper` L2666-L2684](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2666-L2684) 断开清理时，将 victims 记录到 `orphaned_sessions[agent.cmd_key]`
2. 仅当该 agent CLI 实例**仍是**池中的 live 实例（`Arc::ptr_eq` 检查）时记录——崩溃后重启的 CLI 不继承孤儿
3. 下次 `load_session` 时，[`is_orphan_rebind` 快速路径](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L1211-L1216)直接重绑定，**不**重新发 `session/load`——因为 CLI 已经加载了，重发会被拒绝 "already loaded" 或（中途有 turn 时）卡在 "Resuming…" 挂起
4. 未跟踪的孤儿（早于此 master 版本）通过错误消息子串匹配 [`is_already_loaded_error()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L453-L463) 兜底

### Helper 断开清理

[`drop_sessions_for_helper()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2751-L2789) 在 helper 断开时执行完整清理：

1. 收集该 helper 所有 SessionId（持有 `session_to_helper` 锁一次遍历）
2. 从 `session_to_helper` 中移除（`retain`）
3. 释放锁后（遵循锁顺序），逐个从 `registry.remove(sid)`
4. 对每个移除的 sid 广播 `session_removed` + `sessions_changed` ExtNotification 给其他 helper

锁顺序文档：始终先拿 `session_to_helper` 锁再碰 `registry`，保持 helper-disconnect 清理路径单线程化。registry 内部是 sub-µs 的同步 HashMap 操作，不会重入 `session_to_helper`，因此持锁跨 await 是安全的。

> **来源**：[`MasterStateInner` 文档注释](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L120-L158)、[`HelperRoute` 结构体](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L91-L115)、[`drop_sessions_for_helper()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2751-L2789)

---

## 3.9 Master 崩溃检测与恢复机制

Master 实现了多层崩溃检测与自动恢复机制。

### Master 自身崩溃（C++ 侧检测）

Master 进程生命周期由 C++ [`SharedWta`](../../../../../external/libs/intelligent-terminal/src/cascadia/TerminalApp/SharedWta.cpp) 管理：

1. **Job Object  containment**：master 通过 `AssignToJobObject` 分配到 Job Object，配置 `KILL_ON_JOB_CLOSE`，确保 WT 退出时 master 被强制清理
2. **进程退出回调**：`_OnProcessExited` 处理 master 进程退出事件
3. **下次 AcquirePane 时 respawn**：master 崩溃后不立即重启，而是在下一次 `AcquirePane()` 请求时延迟 respawn——给系统时间稳定，避免崩溃循环
4. **Helper 侧检测**：helper 通过 [`conn.rs` 中 `TransportDeath` 机制](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs#L287-L310) 检测管道断开，显示重连 banner，用户可 `/restart` 恢复

### Agent CLI 崩溃恢复

由 master 自身处理（C++ 侧无感知）：

1. **双重 reaper**：
   - I/O 循环 reaper（[`spawn_one_agent` L2347-L2366](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2347-L2366)）：ACP 连接 I/O 结束时触发
   - 子进程 wait reaper（[L2424-L2437](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2424-L2437)）：进程退出时触发
2. **`reap_agent()`**：从 agents 池中移除，清空该 agent 的 orphaned_sessions
3. **幂等重试**：持有旧 `Arc<AgentCli>` 的 helper 下次请求时出错（pane 重建）；新 helper 请求该 agent 时 `get_or_spawn_agent` 发现空槽，重新 spawn
4. **Master 不退出**：单个 agent 崩溃不影响其他 agent 的 helper——多 Agent 池设计保证故障隔离

### Helper 崩溃恢复

[`serve_helper` 末尾的恢复逻辑](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2693-L2709)：

```rust
// 崩溃恢复：如果 helper 有 owner_tab_id，通知 C++ 重新预热
let recovery = state.helper_meta.lock().await.remove(&helper_id);
if let Some(recovery) = recovery {
    if let Some(tab_id) = recovery.owner_tab_id {
        emit_restart_agent_pane(&tab_id, recovery.last_session_id.as_ref());
    }
}
```

1. **`HelperRecoveryMeta`**：在 `new_session`/`load_session` 时记录 `owner_tab_id`（WT Tab StableId）和 `last_session_id`
2. **WT 协议事件**：`emit_restart_agent_pane()` 通过 `wt_protocol_events::send()` 发送 OSC 协议事件给 WT
3. **C++ 侧响应**：`OnAgentPaneRestartRequested` 处理该事件，重新 spawn 一个新的 helper，传递 `--initial-load-session-id` 自动恢复会话
4. **优雅退出 vs 崩溃统一处理**：管道断开信号对崩溃和正常退出是相同的——C++ 侧区分是用户主动关闭（Tab 关闭、Ctrl+C×2）还是意外断开，主动关闭时抑制重启

### Transport Death 检测

[`conn.rs` 中 `DeathWatchRead`](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs#L314-L342) 解决 ACP 1.0 SDK 的一个关键缺陷：

- **问题**：ACP 1.0 `connect_with` 在 clean EOF（如 `taskkill` 杀进程）时不返回，只在读错误时返回，导致 `handle_io` 永远不 resolve，pane 卡在 "Connected" 状态
- **方案**：包装 `AsyncRead`，第一次读到 `Ok(0)`（非空 buffer 上的 0 字节读 = 真 EOF）或 `Err(_)` 时触发 `TransportDeath` latch，`main_fn` 中 `death.wait().await` 完成，`connect_with` 返回，`handle_io` resolve
- **良性空读保护**：`!buf.is_empty()` 检查防止 0 长度 buffer 上的 `Ok(0)` 误判为死亡

```rust
// DeathWatchRead::poll_read
fn poll_read(...) -> Poll<io::Result<usize>> {
    let poll = inner.poll_read(cx, buf);
    if let Ready(Ok(0)) = &poll if !buf.is_empty() {
        this.death.signal();  // 真 EOF
    }
    if let Ready(Err(_)) = &poll {
        this.death.signal();  // 读错误
    }
    poll
}
```

> **来源**：[`emit_restart_agent_pane()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L2718-L2727)、[`TransportDeath` 测试](../../../../../external/libs/intelligent-terminal/tools/wta/src/protocol/acp/conn.rs#L498-L595)、[`HelperRecoveryMeta`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L369-L378)

---

## 3.10 关键数据结构

### MasterConfig

[`config.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/config.rs)：

```rust
#[derive(Debug)]
pub(crate) struct MasterConfig {
    pub(crate) agent: String,              // 默认 agent 命令行（trusted，来自 argv）
    pub(crate) agent_id: Option<String>,   // 默认 agent id
    pub(crate) allowed_agent_ids: Vec<String>,  // GPO 允许的 agent id 列表
}
```

### HelperId

[`mod.rs:70-71`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L70-L71)：

```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub(crate) struct HelperId(u64);  // 单调递增计数器，仅用于日志和路由身份校验
```

### MasterStateInner

核心共享状态（[`mod.rs:120-327`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L120-L327)）：

| 字段 | 类型 | 用途 |
|------|------|------|
| `session_to_helper` | `Mutex<HashMap<SessionId, HelperRoute>>` | Session→Helper 路由表，核心多路复用状态 |
| `registry` | `Arc<dyn SessionRegistry>` | 权威活会话集 + 历史会话，`InMemoryRegistry` 实现 |
| `helper_ext_subscribers` | `Mutex<HashMap<HelperId, UnboundedSender<ExtNotification>>>` | per-helper ExtNotification 广播订阅者 |
| `wt` | `Option<Arc<dyn WtChannel>>` | wtcli/COM 通道，用于 `focus_session` 和 PaneClosed 桥接 |
| `agents` | `Mutex<HashMap<AgentCmdKey, Arc<OnceCell<Arc<AgentCli>>>>>` | Agent CLI 池，懒加载，per-key OnceCell 并发安全 |
| `default_agent_cmd` | `String` | 受信任的默认 agent 命令（来自 argv，非管道） |
| `default_agent_id` | `Option<String>` | 默认 agent id |
| `allowed_agent_ids` | `Option<HashSet<String>>` | GPO 允许列表，`None`=无限制，`Some(set)`=fail-closed |
| `cached_init_resp` | `OnceLock<InitializeResponse>` | 第一个 agent 的 initialize 响应缓存 |
| `agent_conn` | `OnceLock<ClientLink>` | 第一个 agent 的连接（用于 history seed） |
| `cli_source` | `Option<CliSource>` | CLI 提供者标签（Copilot/Claude/Gemini） |
| `helper_meta` | `Mutex<HashMap<HelperId, HelperRecoveryMeta>>` | per-helper 崩溃恢复元数据 |
| `hook_owned` | `Mutex<HashSet<SessionId>>` | PowerShell hook 权威绑定的会话（watcher 不重复跟踪） |
| `orphaned_sessions` | `Mutex<HashMap<AgentCmdKey, HashSet<SessionId>>>` | per-agent 孤儿会话集（helper 断开但 CLI 仍加载） |
| `born_bound` | `Mutex<HashSet<SessionId>>` | WTA 启动的 delegate/resume 会话（仅绑定，watcher 可补状态） |
| `host_list_cache` | `Mutex<Option<(Instant, Option<Arc<[SessionInfo]>>)>>` | host `session/list` 短 TTL 缓存（2s） |
| `wsl_titles_seed_at` | `Mutex<Option<Instant>>` | WSL 标题 seed 节流时间戳（30s） |
| `wsl_seed_in_flight` | `AtomicBool` | WSL 扫描互斥守卫，防止重叠扫描 |

### AgentCli

[`mod.rs:343-365`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L343-L365)：

```rust
struct AgentCli {
    conn: ClientLink,                      // master→agent 的 ACP 客户端连接
    cached_init_resp: InitializeResponse,  // 该 agent 的 initialize 响应（per-agent 缓存）
    cli_source: Option<CliSource>,         // CLI 类型标签
    source: AgentSource,                   // agent 来源（Host/WSL）
    cmd_key: AgentCmdKey,                  // 池键（命令行+source）
}
```

### HelperRecoveryMeta

[`mod.rs:369-378`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L369-L378)：

```rust
#[derive(Debug, Clone, Default)]
pub(crate) struct HelperRecoveryMeta {
    pub(crate) owner_tab_id: Option<String>,   // WT Tab StableId
    pub(crate) last_session_id: Option<SessionId>,  // 最近会话（恢复目标）
}
```

### 常量

| 常量 | 值 | 用途 |
|------|-----|------|
| `NOTIF_CHANNEL_CAPACITY` | 1024 | per-helper 通知通道容量，为突发 chunk 流预留 |
| `SESSION_NEW_TIMEOUT_SECS` | 120 | session/new 超时（秒），防止 agent 挂起死锁 helper |
| `MASTER_PIPE_DISCOVERY_FILE` | `"master-pipe.txt"` | 管道发现文件名 |

### AgentCmdKey

类型别名：`type AgentCmdKey = String;`，格式为 `"{source}\0{command}"`，由 [`agent_cmd_key()`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs#L336-L338) 生成。使用空字节分隔确保不会与命令行参数中的字符冲突。

> **来源**：所有结构体定义均位于 [`tools/wta/src/master/mod.rs`](../../../../../external/libs/intelligent-terminal/tools/wta/src/master/mod.rs)

---

## 本章导航

- [上一章：整体架构设计](02-architecture.md)
- [返回目录](README.md)
- [下一章：WTA Helper TUI 实现](04-wta-helper-tui.md)
