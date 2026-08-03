---
id: "create-intelligent-terminal-wiki-tutorial"
title: "Intelligent Terminal 完整 Wiki 教程"
source: "spec:create-intelligent-terminal-wiki-tutorial"
date: "2026-08-03"
type: "spec"
theme: "standards-tools"
maturity: "L0"
---

# Intelligent Terminal 完整 Wiki 教程 - Product Requirement Document

## Overview
- **Summary**: 基于七概念方法论编排（R-I-E-A链路），深度学习 `external/libs/intelligent-terminal`（微软 Intelligent Terminal，Windows Terminal 的 AI 原生 fork）源码，在 `docs/knowledge/learning/` 下创建原子化的 `intelligent-terminal-wiki/` 教程目录，系统讲解其架构设计、核心组件、通信协议、构建系统与扩展开发。
- **Purpose**: Intelligent Terminal 是一个将 AI Agent（Copilot/Claude/Gemini/Codex/自定义Agent）原生集成到终端的前沿项目，采用 C++/Rust/XAML 混合技术栈，helper+master 多进程架构，COM 作为唯一集成表面，ACP（Agent Client Protocol）JSON-RPC 2.0 双跳协议。当前知识库缺少对该项目架构与实现的系统性中文学习资料，需要基于源码深度阅读创建全面的 wiki 教程，为理解 AI-native 终端设计、多进程架构、COM 集成、Rust TUI 开发等提供参考。
- **Target Users**: 对终端开发、AI Agent 集成、Windows 系统编程、Rust TUI 开发感兴趣的开发者；需要理解 Intelligent Terminal 架构以进行二次开发或贡献代码的工程师。

## Goals
- 在 `docs/knowledge/learning/intelligent-terminal-wiki/` 下创建原子化 wiki 教程，遵循项目文档规范
- 系统覆盖 Intelligent Terminal 的核心领域：项目概述、架构设计、WTA（Rust）核心模块、C++ 集成层、通信协议栈（COM+ACP+ConPTY）、构建系统、wtcli 命令参考、wt-agent-hooks、日志调试、扩展开发
- 教程每章包含源码溯源引用（具体文件路径）和架构图（Mermaid）
- 使用七概念方法论（R-I-E-A链路）指导教程结构：复盘事实（源码阅读）→洞察本质（架构模式）→萃取模式（可复用设计模式）→原子化拆分（章节组织）

## Non-Goals (Out of Scope)
- 不涉及 Windows Terminal 基础功能（标签页、面板、主题等继承自上游的功能）的详细讲解
- 不修改 external/libs/intelligent-terminal/ 下的任何源码（只读学习）
- 不构建或编译 Intelligent Terminal（纯文档产出）
- 不覆盖上游 Windows Terminal 的所有内部实现细节，仅聚焦 Intelligent Terminal 的 AI 集成增量部分
- 不编写英文文档，教程仅以中文编写

## Background & Context
- Intelligent Terminal 是微软在 2025 年发布的 Windows Terminal 实验性 fork，源码位于 https://github.com/microsoft/intelligent-terminal
- 项目采用混合技术栈：C++（Windows Terminal 主体 + COM Server）、Rust（WTA 编排器 + wtcli）、XAML（设置 UI）
- 核心创新点：helper+master 多进程架构实现 per-tab Agent Pane 预启动，COM 作为进程间唯一集成表面，ACP JSON-RPC 2.0 实现双跳通信（helper↔master↔agent CLI）
- 项目已有 AGENTS.md（AI 智能体入口文档）、OVERVIEW.md、Multi-window-agent-pane.md 等高质量英文架构文档，但缺少系统性中文教程
- SpecWeave 项目已有 tvm-ffi-wiki、scikit-build-core-wiki、wsl-wiki 等 wiki 教程先例，本教程遵循相同的原子化文档模式

## Functional Requirements
- **FR-1**: 系统 SHALL 在 `docs/knowledge/learning/intelligent-terminal-wiki/` 下创建原子化 wiki 教程目录结构，包含 README.md 导航入口和多个原子化章节文档
- **FR-2**: 系统 SHALL 确保教程覆盖以下核心领域：
  - 项目定位与快速开始
  - 整体架构设计（helper+master、进程模型、数据流）
  - WTA Rust 侧详解（master、helper、TUI app、ACP client、ShellManager、session管理）
  - C++ 集成层（TerminalPage、SharedWta、COM Server、AgentPaneContent、Tab stash/restore）
  - 通信协议栈（COM IProtocolServer、ACP JSON-RPC 2.0、ConPTY、WT Protocol）
  - wtcli 命令参考
  - wt-agent-hooks PowerShell 集成
  - Autofix 自动错误检测与修复
  - 构建系统与开发环境
  - 日志与调试
  - 配置与设置
  - 架构设计模式萃取
- **FR-3**: 系统 SHALL 在教程中标注源码溯源，引用具体文件路径（相对于 intelligent-terminal 根目录），确保可验证性
- **FR-4**: 系统 SHALL 在教程中使用 Mermaid 图表可视化架构、进程关系、数据流、时序等
- **FR-5**: 系统 SHALL 遵循项目文档规范：YAML frontmatter（含 `source` 溯源字段）、相对路径引用、双向导航、原子化单文件单主题
- **FR-6**: 系统 SHALL 参考已有 wiki 教程模式（create-tvm-ffi-wiki-tutorial），保持风格一致
- **FR-7**: 系统 SHALL 应用七概念方法论（R-I-E-A链路）：R阶段系统采集源码事实，I阶段洞察架构本质，E阶段萃取可复用设计模式，A阶段原子化拆分章节

## Non-Functional Requirements
- **NFR-1**: 每个章节文档聚焦单一主题，长度控制在合理范围内（建议200-800行），避免单文件过大
- **NFR-2**: Mermaid 图表遵循安全编码六规则
- **NFR-3**: 所有源码引用使用相对路径格式，可直接点击跳转
- **NFR-4**: 文档使用中文编写，技术术语保留英文原文
- **NFR-5**: 教程应具备渐进式学习路径：从概念到实现、从整体到局部、从使用到扩展

## Constraints
- **Technical**: 只读分析 external/libs/intelligent-terminal/ 源码，不修改任何外部文件；文档产出遵循 SpecWeave 文档规范（YAML frontmatter、相对路径、原子化）
- **Business**: 无外部依赖，不要求构建或运行 Intelligent Terminal
- **Dependencies**: 依赖已有源码（external/libs/intelligent-terminal/）；依赖项目文档规范（.agents/docs/development-standards.md）；依赖七概念方法论（seven-concepts-cmd）指导教程结构

## Assumptions
- 用户已安装 Trae IDE 且可以访问 external/libs/intelligent-terminal/ 源码
- 用户希望使用七概念方法论（R-I-E链路）来指导知识沉淀过程
- 教程最终存放位置为 `docs/knowledge/learning/intelligent-terminal-wiki/`（遵循路径解析规则，docs/ → .agents/docs/）
- 源码中 AGENTS.md、ARCHITECTURE.md、OVERVIEW.md、Multi-window-agent-pane.md 等英文文档是主要参考来源

## Acceptance Criteria

### AC-1: Wiki 教程目录结构完整
- **Given**: 教程创建完成
- **When**: 检查 `docs/knowledge/learning/intelligent-terminal-wiki/` 目录
- **Then**: 目录包含 README.md 导航入口 + 至少 12 个原子化章节文档
- **Then**: 每个文档包含 YAML frontmatter（含 `id`、`title`、`source: "spec:create-intelligent-terminal-wiki-tutorial"`、`date` 字段）
- **Verification**: `programmatic`

### AC-2: 核心内容领域全覆盖
- **Given**: 开发者完整阅读教程
- **When**: 对照 FR-2 的核心领域清单
- **Then**: 教程覆盖项目概述、架构设计、WTA Rust、C++集成、通信协议、wtcli、hooks、autofix、构建、日志调试、配置、设计模式萃取共12个领域
- **Then**: 每个领域至少有一个独立章节文档
- **Verification**: `programmatic` + `human-judgment`

### AC-3: 源码溯源可追溯
- **Given**: 教程描述某个组件或功能
- **When**: 查阅相关章节
- **Then**: 每个技术细节引用对应源码文件路径（如 `src/cascadia/TerminalApp/TerminalPage.cpp`、`tools/wta/src/master/mod.rs`）
- **Then**: 关键代码段提供行号引用
- **Verification**: `human-judgment`

### AC-4: Mermaid 架构图清晰准确
- **Given**: 教程中的架构图
- **When**: 渲染 Mermaid 图表
- **Then**: 包含整体架构图、helper+master进程关系图、ACP双跳协议时序图、COM通信流程图等至少5张Mermaid图
- **Then**: 图表语法正确可渲染
- **Verification**: `programmatic` + `human-judgment`

### AC-5: 七概念方法论指导教程结构
- **Given**: 教程产出物
- **When**: 审查章节组织和内容深度
- **Then**: R阶段（事实）：系统采集源码中的组件、接口、数据流等客观事实
- **Then**: I阶段（洞察）：识别架构设计决策背后的原因（如为何选择helper+master而非单进程、为何用COM而非自定义IPC）
- **Then**: E阶段（萃取）：提炼可复用的设计模式（如per-tab pre-warm、stash/restore、COM-as-integration-surface等）
- **Then**: A阶段（原子化）：教程章节按单一职责原子化拆分
- **Verification**: `human-judgment`

### AC-6: 文档规范合规
- **Given**: 所有章节文档
- **When**: 检查格式规范
- **Then**: YAML frontmatter 完整、相对路径引用正确、章节间双向导航链接存在
- **Then**: 无 `file:///` 绝对路径引用
- **Then**: 中文为主，技术术语保留英文
- **Verification**: `programmatic`

### AC-7: 渐进式学习路径
- **Given**: 读者从README开始阅读
- **When**: 按导航顺序学习
- **Then**: 先理解整体架构，再深入各模块，最后学习扩展开发
- **Then**: README.md 提供完整的章节索引和阅读建议
- **Verification**: `human-judgment`

## Open Questions
- [ ] 是否需要包含 Windows Terminal 上游基础概念章节（如 ConPTY、TermControl 等），还是假设读者已有基础？
- [ ] 教程深度：面向入门开发者还是面向有经验的系统工程师？
- [ ] 是否需要包含实战章节（如编写一个自定义 ACP agent）？
