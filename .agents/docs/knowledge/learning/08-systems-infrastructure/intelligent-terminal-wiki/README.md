---
id: "intelligent-terminal-wiki-index"
title: "Intelligent Terminal Wiki 教程索引"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
---
# Intelligent Terminal Wiki 教程索引

## 项目简介

**Intelligent Terminal** 是 AI-native 的 Windows Terminal 分支，让 AI 代理（Copilot、Claude、Gemini 及自定义代理）能够理解、修复和自动化终端工作流。

### 核心特性

- **WTA (Windows Terminal Agent)**：编排器二进制，负责启动代理、传递 Terminal Protocol 连接信息，代理通过 `wtcli` 控制终端
- **WT Protocol (IProtocolServer)**：唯一集成表面，基于 WinRT IDL + COM 进程外服务器（MBM 封送、MTA 线程），通过 `WT_COM_CLSID` 环境变量发现
- **WTCLI**：命令行客户端，通过 `CoCreateInstance(CLSCTX_LOCAL_SERVER)` 消费 `IProtocolServer`，供代理调用如 `wtcli list-panes`、`wtcli capture-pane` 等命令
- **ACP (Agent Control Protocol)**：helper+master 架构内部使用的 JSON-RPC 2.0 协议，`wta-helper` 与 `wta-master` 通过命名管道通信，`wta-master` 与代理 CLI 子进程通过 stdio 通信
- **Autofix 自动错误修复**：检测其他窗格中的命令失败，自动通过代理建议修复方案
- **Shell 集成**：支持 `wt-agent-hooks` 插件与多种代理 CLI 的集成

## 前置知识要求

在学习本教程前，建议具备以下基础知识：

1. **Windows Terminal 基础**：了解 Windows Terminal 的基本使用、配置、窗格/标签页概念
2. **COM 基础**：了解 COM（Component Object Model）的基本概念、接口、CoCreateInstance、进程外服务器等
3. **Rust/C++ 基础**：
   - Rust：熟悉 Cargo、tracing、异步编程、serde JSON 序列化
   - C++：熟悉 WinRT、C++/WinRT、MSBuild、XAML 等 Windows 开发技术

## 源码位置说明

Intelligent Terminal 源码位于本仓库的 `external/libs/intelligent-terminal/` 目录下。

主要目录结构：
- `src/cascadia/`：C++ 终端核心代码（TerminalApp、TerminalProtocol、WindowsTerminal 等）
- `tools/wta/`：Rust 编写的 WTA（Windows Terminal Agent）核心代码
  - `tools/wta/src/master/`：wta-master 多路复用器
  - `tools/wta/src/app.rs`：wta-helper / TUI 应用主逻辑
- `doc/`：项目文档目录
- `tools/wta/wt-agent-hooks/`：Shell 集成钩子插件

## 七概念方法论说明

本教程遵循七概念方法论的 **R-I-E-A 链路**（Retrospective → Insight → Extraction → Atomization）进行组织：

- **R (Retrospective - 复盘)**：通过梳理 Intelligent Terminal 的架构设计、实现细节，建立对系统的完整认知
- **I (Insight - 洞察)**：从代码和架构中提炼关键设计决策、模式和权衡
- **E (Extraction - 萃取)**：将可复用的架构模式、通信协议设计、错误处理机制等沉淀为通用模式
- **A (Atomization - 原子化)**：将复杂系统拆解为独立的、职责单一的章节，每个章节聚焦一个特定主题，便于按需学习

后续章节将按照从整体到局部、从架构到实现的顺序展开，帮助读者系统地理解 Intelligent Terminal 的设计与实现。

## 学习路径建议

建议按以下顺序阅读本教程：

1. **入门阶段**：先阅读 [01-overview.md](01-overview.md)（项目概述与快速开始），了解项目全貌、快速搭建开发环境
2. **架构理解**：接着阅读 [02-architecture.md](02-architecture.md)（整体架构设计），掌握 WTA master/helper 架构、通信模型
3. **核心 Rust 模块**：然后依次阅读 WTA Rust 核心章节：
   - [03-wta-master.md](03-wta-master.md)（WTA Rust 核心 - Master 多路复用器）
   - [04-wta-helper-tui.md](04-wta-helper-tui.md)（WTA Rust 核心 - Helper 与 TUI）
4. **集成层理解**：阅读 [05-cpp-integration.md](05-cpp-integration.md)（C++ 集成层）和 [06-protocols.md](06-protocols.md)（通信协议栈），理解跨语言集成和协议细节
5. **工具使用**：阅读 [07-wtcli-reference.md](07-wtcli-reference.md)（wtcli 命令参考）和 [08-agent-hooks.md](08-agent-hooks.md)（wt-agent-hooks Shell 集成）
6. **高级特性**：阅读 [09-autofix.md](09-autofix.md)（Autofix 自动错误检测与修复）
7. **开发与运维**：最后阅读构建、调试、配置和设计模式章节：
   - [10-build-system.md](10-build-system.md)（构建系统与开发环境）
   - [11-logging-debugging.md](11-logging-debugging.md)（日志系统与调试）
   - [12-configuration.md](12-configuration.md)（配置与设置详解）
   - [13-design-patterns.md](13-design-patterns.md)（架构设计模式萃取）

## 完整章节索引

| 章节 | 文件 | 标题 |
|------|------|------|
| 01 | [01-overview.md](01-overview.md) | 项目概述与快速开始 |
| 02 | [02-architecture.md](02-architecture.md) | 整体架构设计 |
| 03 | [03-wta-master.md](03-wta-master.md) | WTA Rust 核心 - Master 多路复用器 |
| 04 | [04-wta-helper-tui.md](04-wta-helper-tui.md) | WTA Rust 核心 - Helper 与 TUI |
| 05 | [05-cpp-integration.md](05-cpp-integration.md) | C++ 集成层 |
| 06 | [06-protocols.md](06-protocols.md) | 通信协议栈 |
| 07 | [07-wtcli-reference.md](07-wtcli-reference.md) | wtcli 命令参考 |
| 08 | [08-agent-hooks.md](08-agent-hooks.md) | wt-agent-hooks Shell 集成 |
| 09 | [09-autofix.md](09-autofix.md) | Autofix 自动错误检测与修复 |
| 10 | [10-build-system.md](10-build-system.md) | 构建系统与开发环境 |
| 11 | [11-logging-debugging.md](11-logging-debugging.md) | 日志系统与调试 |
| 12 | [12-configuration.md](12-configuration.md) | 配置与设置详解 |
| 13 | [13-design-patterns.md](13-design-patterns.md) | 架构设计模式萃取 |

## 相关链接

- [返回上级：学习资源目录](../README.md)
- [Intelligent Terminal 源码](../../../../../external/libs/intelligent-terminal/)
