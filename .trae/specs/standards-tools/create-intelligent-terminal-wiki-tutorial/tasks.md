---
id: "create-intelligent-terminal-wiki-tutorial-tasks"
title: "Intelligent Terminal Wiki 教程 - 实现计划"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---

# Intelligent Terminal 完整 Wiki 教程 - The Implementation Plan (Decomposed and Prioritized Task List)

## [ ] Task 1: 创建 Wiki 目录骨架与导航入口 (README.md)
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 在 `.agents/docs/knowledge/learning/intelligent-terminal-wiki/` 下创建目录结构（遵循路径解析规则 docs/ → .agents/docs/）
  - 创建 README.md 作为导航入口，包含：
    - 项目简介与学习路径建议
    - 完整章节索引（12个核心章节）
    - 前置知识要求
    - 源码位置说明
  - README.md 包含 YAML frontmatter 和双向导航
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录 `.agents/docs/knowledge/learning/intelligent-terminal-wiki/` 存在
  - `programmatic` TR-1.2: README.md 文件存在且包含 YAML frontmatter（id、title、source、date）
  - `programmatic` TR-1.3: README.md 列出至少12个章节的链接
  - `human-judgement` TR-1.4: 学习路径建议清晰合理，从入门到进阶
- **Notes**: 使用七概念方法论的A阶段（原子化）确定章节拆分方案

## [ ] Task 2: 第1章 - 项目概述与快速开始 (01-overview.md)
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 基于 README.md、AGENTS.md 编写项目概述章节
  - 内容包括：Intelligent Terminal 是什么、与 Windows Terminal 的关系、核心特性（Agent Pane、Autofix、Command Palette、Session Management）
  - 安装方式（Microsoft Store、WinGet、手动下载）
  - 首次使用指南（选择 Agent、认证、基础操作）
  - 键盘快捷键速查表
  - 配置项概览（settings.json 中的 Agent 相关配置）
  - 数据隐私说明
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: 文件 `01-overview.md` 存在且包含 YAML frontmatter
  - `programmatic` TR-2.2: 包含键盘快捷键表格
  - `programmatic` TR-2.3: 引用源码中的 README.md、AGENTS.md 作为来源
  - `human-judgement` TR-2.4: 内容准确、新手友好
- **Notes**: R阶段（事实）：从官方文档采集客观信息

## [ ] Task 3: 第2章 - 整体架构设计 (02-architecture.md)
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 系统讲解 Intelligent Terminal 的整体架构
  - helper+master 多进程模型深度解析
  - 进程清单与生命周期（WindowsTerminal.exe、wta-master、wta-helper、agent CLI、wtcli）
  - 核心组件关系图（Mermaid flowchart）
  - 技术栈总览（C++、Rust、XAML、COM、ACP、ConPTY）
  - 为什么选择 helper+master 架构（设计决策洞察，I阶段）
  - 架构演进历史（从单进程到 helper+master 的 Z 方案选型）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-3.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-3.2: 包含至少2张 Mermaid 图（整体架构图、进程生命周期图）
  - `programmatic` TR-3.3: 引用 AGENTS.md、OVERVIEW.md、Multi-window-agent-pane.md 作为来源
  - `human-judgement` TR-3.4: 架构讲解清晰，设计决策洞察有深度
  - `human-judgement` TR-3.5: Mermaid 图表语法正确可渲染
- **Notes**: R+I阶段：事实采集+架构本质洞察

## [ ] Task 4: 第3章 - WTA Rust 核心 - Master 多路复用器 (03-wta-master.md)
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - wta-master 单例详解
  - 源码位置：`tools/wta/src/master/mod.rs`
  - 职责：Agent CLI 子进程管理、命名管道服务、ACP 多路复用、SessionId 路由表
  - master 启动流程（SharedWta 延迟 spawn → agent CLI spawn → named pipe listen → accept loop）
  - per-helper MuxConnection 处理
  - ACP 消息路由：helper → master → agent CLI，agent CLI → master → owning helper
  - initialize 缓存、session/new 原子性记录
  - master 崩溃检测与恢复机制
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-4.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-4.2: 包含 master 启动时序图（Mermaid sequenceDiagram）
  - `programmatic` TR-4.3: 源码引用到 `tools/wta/src/master/mod.rs` 具体路径
  - `human-judgement` TR-4.4: master 多路复用逻辑讲解清晰
- **Notes**: 深入 Rust 源码

## [ ] Task 5: 第4章 - WTA Rust 核心 - Helper 与 TUI (04-wta-helper-tui.md)
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - wta-helper per-pane TUI 详解
  - 源码位置：`tools/wta/src/helper/mod.rs`、`tools/wta/src/app.rs`、`tools/wta/src/ui/`
  - helper 启动流程：conpty child → crossterm event loop → ratatui render → pipe connect → ACP initialize
  - App 状态机与 TabSession（chat history、turn state、autofix state、input editor）
  - TUI 视图层（chat、input、permission、popups、agents_view、status_bar）
  - slash commands 实现（/help、/clear、/new、/fix、/restart、/stop、/sessions、/agent、/model）
  - helper 崩溃隔离设计
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-5.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-5.2: 包含 helper 组件关系图（Mermaid）
  - `programmatic` TR-5.3: 源码引用到 helper/mod.rs、app.rs、ui/ 目录
  - `human-judgement` TR-5.4: TUI 架构和状态管理讲解清晰
- **Notes**: 涵盖 ratatui TUI 的核心设计

## [ ] Task 6: 第5章 - C++ 集成层 (05-cpp-integration.md)
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - Windows Terminal C++ 侧的 Agent 集成
  - 源码位置：`src/cascadia/TerminalApp/` 目录
  - TerminalPage 与 Agent 集成事件处理（ProtocolVtSequenceReceived、agent 相关 action）
  - SharedWta 单例：refcount 生命周期管理、Job Object 包含、CREATE_SUSPENDED 竞态防护、crash detection
  - TerminalProtocolComServer：COM 进程外服务器（MTA thread、MBM marshaling）
  - AgentPaneContent：XAML chrome 包裹 helper 的 TermControl
  - Tab stash/restore 机制（StashAgentPane/RestoreStashedAgentPane）
  - per-tab pre-warm 机制（_AutoCreateHiddenAgentPaneShared、--start-stashed）
  - Settings 模型与设置 UI（GlobalAppSettings.idl、MTSMSettings.h、AIAgents.xaml）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-6.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-6.2: 包含 C++ 组件调用关系图（Mermaid）
  - `programmatic` TR-6.3: 源码引用到 TerminalPage.cpp、SharedWta.cpp、TerminalProtocolComServer.cpp、AgentPaneContent.cpp、Tab.cpp
  - `human-judgement` TR-6.4: COM 集成和 stash/restore 机制讲解清晰

## [ ] Task 7: 第6章 - 通信协议栈 (06-protocols.md)
- **Priority**: high
- **Depends On**: Task 4, Task 5, Task 6
- **Description**:
  - 三层通信协议深度解析
  - **COM IProtocolServer**：WinRT IDL 定义、out-of-process COM server、CLSCTX_LOCAL_SERVER、WT_COM_CLSID 环境变量发现
    - IDL：`src/cascadia/TerminalProtocol/TerminalProtocol.idl`
    - 关键方法：list_windows/list_tabs/list_panes、read_pane_output、create_tab、split_pane、send_input、event subscribe/publish
  - **ACP (Agent Client Protocol) 1.3.0**：JSON-RPC 2.0 双跳通信
    - master ↔ agent CLI (stdio)：master 作为 ACP client
    - helper ↔ master (named pipe)：master 作为 ACP agent (server)
    - 关键消息类型：initialize、session/new、session/prompt、session/update、request_permission、create_terminal
  - **ConPTY**：Windows 伪控制台，helper 作为 conpty child 获得 native console input
  - 协议栈对比表
  - 端到端消息流时序图（用户输入 prompt → agent 响应 chunk 回传）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-7.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-7.2: 包含 ACP 双跳协议栈图（Mermaid flowchart）
  - `programmatic` TR-7.3: 包含端到端 prompt 时序图（Mermaid sequenceDiagram）
  - `programmatic` TR-7.4: 源码引用到 TerminalProtocol.idl、TerminalProtocolComServer.cpp、protocol/acp/client.rs
  - `human-judgement` TR-7.5: 协议层次清晰，双跳路由逻辑讲解透彻
- **Notes**: 协议是理解整个系统的核心

## [ ] Task 8: 第7章 - wtcli 命令参考 (07-wtcli-reference.md)
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - wtcli 命令行工具完整参考
  - wtcli 作为 COM client 的实现原理
  - 命令分类：
    - 查询类：list-windows (lsw)、list-tabs (lst)、list-panes (lsp)、active-pane、pane-status
    - 操作类：new-tab (neww)、split-pane (splitw)、kill-pane (killp)、focus-pane
    - 读取类：capture-pane (capturep)、wait-for
    - 事件类：listen (mon)
    - 输入类：send-keys (send_input)
    - 诊断类：pipe-id、set-env
  - 每个命令的用法、参数、返回值示例
  - wta CLI helper 子命令（wta 作为 wtcli 的超集）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-8.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-8.2: 包含命令分类表格
  - `programmatic` TR-8.3: 引用 doc/wtcli-commands.md 和 AGENTS.md CLI helpers 章节
  - `human-judgement` TR-8.4: 命令参考完整实用

## [ ] Task 9: 第8章 - wt-agent-hooks Shell 集成 (08-agent-hooks.md)
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - wt-agent-hooks 插件系统
  - 支持的 Agent CLI：Copilot、Claude、Gemini、Codex、OpenCode
  - hooks 插件结构（每个 CLI 的 plugin.json / gemini-extension.json、hooks.json、send-event.ps1）
  - PowerShell shell integration（OSC 133 marks）
  - hooks 自动升级机制（agent_hooks_installer、bundle version cache、per-CLI策略）
  - OSC 133;D 退出码检测 → Autofix 触发链路
  - hook-trace.log 诊断日志
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-9.2: 包含 hooks 自动升级流程图（Mermaid）
  - `programmatic` TR-9.3: 源码引用到 wt-agent-hooks/ 目录和 agent_hooks_installer.rs
  - `human-judgement` TR-9.4: hooks 机制和 shell integration 讲解清晰

## [ ] Task 10: 第9章 - Autofix 自动错误检测与修复 (09-autofix.md)
- **Priority**: medium
- **Depends On**: Task 7, Task 9
- **Description**:
  - Autofix 功能完整解析
  - 检测管线：Shell OSC 133;D → TerminalPage ProtocolVtSequenceReceived → COM server → wtcli listen → WTA classify_wt_event → maybe_trigger_autofix
  - 前置条件：PowerShell shell integration、helper ACP session Connected、wtcli on PATH
  - pre-warmed helper 如何让 stashed pane 上的 autofix 工作
  - cold start 期间失败的 drop 策略（state != Connected 时 early return）
  - /fix slash command 手动触发
  - autofix_state 事件路由
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-10.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-10.2: 包含 Autofix 数据流管线图（Mermaid flowchart）
  - `programmatic` TR-10.3: 源码引用到 app.rs (classify_wt_event, maybe_trigger_autofix)、TerminalPage.cpp 事件处理
  - `human-judgement` TR-10.4: Autofix 触发条件和边界情况讲解清楚

## [ ] Task 11: 第10章 - 构建系统与开发环境 (10-build-system.md)
- **Priority**: medium
- **Depends On**: Task 1
- **Description**:
  - 双构建系统：Rust (Cargo) + C++ (MSBuild/Visual Studio)
  - WTA (Rust) 构建：cargo build --target x86_64-pc-windows-msvc
  - Terminal (C++) 构建：razzle.cmd + bcz / Visual Studio F5
  - 为什么必须显式 --target（wapproj 路径偏好）
  - Safe Debug deployment 脚本（Invoke-IntelligentTerminalDebugDeployment.ps1）
  - Package identity & COM 要求（0x80073D54 错误诊断）
  - 完整开发循环：kill wta → cargo build → F5 / bcz
  - MSIX 打包与自解压 EXE 安装程序
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-11.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-11.2: 包含构建流程图（Mermaid）
  - `programmatic` TR-11.3: 引用 doc/building.md、doc/quick-start-local-dev.md、AGENTS.md Build 章节
  - `human-judgement` TR-11.4: 构建步骤和常见坑点（如wta.exe锁定、package identity）讲解清楚

## [ ] Task 12: 第11章 - 日志系统与调试 (11-logging-debugging.md)
- **Priority**: medium
- **Depends On**: Task 10
- **Description**:
  - WTA 运行时数据布局（package-private store）
  - STATE root vs LOCAL/cache root 分离（LocalState vs LocalCache\Local）
  - per-version 日志目录 `logs\<pkgver>\`
  - 三类 writer 共享一个版本目录（Rust wta、C++ AgentPaneLog、PowerShell hooks）
  - 日志文件清单：
    - wta-main_master.log、wta-main_helper-{pid}.log、wta-cli.log、wta-delegate.log
    - wta-probe.log、wta-install-hooks.log、wta-ensure-host.log、wta-acp-debug.log
    - terminal-agent-pane.log (C++)、hook-trace.log (PS)
  - 日志级别控制（WTA_LOG / RUST_LOG 环境变量）
  - 日志 retention 策略（per-version 清理、3天轮转）
  - 使用 target 字段追踪流程（grep patterns 表）
  - 端到端 prompt trace 示例
  - Bug 报告日志收集（Report a bug (collect logs)）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-12.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-12.2: 包含日志目录结构图
  - `programmatic` TR-12.3: 包含 target grep patterns 表格
  - `programmatic` TR-12.4: 引用 AGENTS.md Logs & runtime data layout 章节和 runtime_paths.rs
  - `human-judgement` TR-12.5: 日志系统和调试技巧实用

## [ ] Task 13: 第12章 - 配置与设置详解 (12-configuration.md)
- **Priority**: medium
- **Depends On**: Task 2
- **Description**:
  - settings.json Agent 配置完整参考
  - 全局 Agent 设置：acpAgent、acpModel、acpCustomCommand、agentPanePosition
  - Delegate 设置：delegateAgent、delegateModel、delegateCustomCommand
  - Autofix 设置：autoFixEnabled
  - AI Integration 设置：coordinator、confirmation 策略（read/create/input operations）
  - Profile 级 Agent 覆盖（WSL distro 专用 agent）
  - GPO 策略（AllowedAgents）
  - 设置 UI（AIAgents.xaml）
  - 环境变量（WTA_LOG、WT_COM_CLSID、WTA_SESSIONS_SHOW_AGENT_PANE 等）
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-6
- **Test Requirements**:
  - `programmatic` TR-13.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-13.2: 包含完整配置表格
  - `programmatic` TR-13.3: 引用 AGENTS.md Settings 章节和 GlobalAppSettings.idl
  - `human-judgement` TR-13.4: 配置项说明准确完整

## [ ] Task 14: 第13章 - 架构设计模式萃取 (13-design-patterns.md)
- **Priority**: high
- **Depends On**: Task 3, Task 4, Task 5, Task 6, Task 7
- **Description**:
  - **E阶段（萃取）**：从 Intelligent Terminal 架构中提炼可复用的设计模式
  - 模式1：**Helper+Master Multiplexer**（多tab/多window场景下的单例Agent CLI共享模式）
    - 触发场景、核心步骤、反模式、迁移验证
  - 模式2：**COM as Integration Surface**（用COM作为唯一进程间集成面而非自定义IPC）
    - 触发场景、核心步骤、反模式
  - 模式3：**Per-tab Pre-warm**（预启动隐藏pane实现零延迟激活+后台功能）
    - 触发场景、核心步骤、反模式
  - 模式4：**Stash/Restore Toggle**（隐藏而非销毁，保留会话状态）
    - 触发场景、核心步骤、反模式
  - 模式5：**Protocol Double-hop**（helper↔master↔agent 双跳代理解耦）
    - 触发场景、核心步骤、反模式
  - 模式6：**Package-private State/Cache Split**（持久状态与临时缓存分离存储）
    - 触发场景、核心步骤、反模式
  - 每个模式包含：问题背景、解决方案、源码位置、适用场景、反模式警示
- **Acceptance Criteria Addressed**: AC-2, AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-14.1: 文件存在且包含 YAML frontmatter
  - `programmatic` TR-14.2: 包含至少6个设计模式的详细描述
  - `programmatic` TR-14.3: 每个模式引用对应源码位置
  - `human-judgement` TR-14.4: 模式萃取准确、有迁移价值、反模式有警示意义
- **Notes**: E阶段核心产出——可复用设计模式库

## [ ] Task 15: 导航更新与交叉引用完整性检查
- **Priority**: high
- **Depends On**: Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14
- **Description**:
  - 更新 README.md 中所有章节链接为有效相对路径
  - 在每个章节文档底部添加"下一章"导航链接
  - 检查所有内部交叉引用（章节间引用）的正确性
  - 检查源码引用路径格式（相对于 intelligent-terminal 根目录）
  - 运行 link-check 验证链接有效性
  - 更新 `.agents/docs/knowledge/learning/README.md` 添加 intelligent-terminal-wiki 索引条目
- **Acceptance Criteria Addressed**: AC-1, AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-15.1: README.md 中所有章节链接可点击跳转
  - `programmatic` TR-15.2: 每个章节有"下一章"导航，首尾章节有适当处理
  - `programmatic` TR-15.3: 无 `file:///` 绝对路径引用
  - `programmatic` TR-15.4: link-check 通过，无断链
  - `human-judgement` TR-15.5: 交叉引用逻辑合理
