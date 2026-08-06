---
title: "Orca 多代理 AI 编排器学习与 Wiki 教程文档"
source: "https://www.onorca.dev/ 官网 + d:\AI\external\tools\orca 本地开源源码"
x-toml-ref: "../../../../.meta/toml/.trae/specs/retrospectives-insights/create-orca-wiki-tutorial/spec.toml"
date: "2026-08-03"
tags: ["orca", "stablyai", "ai-orchestrator", "agent-ide", "worktree", "claude-code", "codex", "opencode", "electron", "parallel-agents", "multi-agent", "yc"]
---
# Orca 多代理 AI 编排器学习与 Wiki 教程文档 - 产品需求文档

## Overview
- **Summary**: 系统学习 Orca（Stably.ai 出品，YC 背书）的官网（https://www.onorca.dev/）与本地开源源码（d:\AI\external\tools\orca），理解其作为"AI 编排器（AI Orchestrator）"的核心定位——并排运行 Codex、Claude Code、OpenCode、Pi 等多个 AI Agent，每个 Agent 运行在隔离的 git worktree 中并在一个地方统一跟踪。基于学习成果创建一份原子化目录式 wiki 教程文档，覆盖产品定位、核心架构、八大特色功能、支持 Agent 列表、Orca CLI 与编排、快速上手、FAQ 与术语表。
- **Purpose**: 为项目团队提供 Orca 项目的完整学习资料，帮助需要同时运行多个 AI 编程 Agent（Claude Code、Codex、OpenCode 等）的开发者了解如何通过 Orca 实现并行工作区隔离、多 Agent 编排、手机远程监控、终端分屏与设计模式等能力，理解"IDE 从代码编辑器向代理编排器"演进的行业趋势。
- **Target Users**: AI 辅助开发实践者、多 Agent 协作研究者、IDE 工具选型决策者、并行开发流程优化者、开源工具爱好者。

## Goals
- 创建包含目录导航系统的原子化目录式 wiki 教程文档（orca-wiki/）
- 解释 Orca 项目背景与核心定位（面向 100x 构建者的 AI 编排器）
- 梳理核心架构与技术栈（Electron + TypeScript、xterm.js WebGL 终端、node-pty、ssh2、移动端 Expo）
- 详解八大核心功能：移动 Companion、并行 Worktree、终端分屏、设计模式、GitHub & Linear 原生集成、SSH Worktree、注释 AI Diff、拖拽文件
- 提供 Orca CLI 命令参考与多 Agent 编排（orchestration）机制解析
- 整理支持的 Agent 清单（25+ CLI Agent）
- 提供快速上手指南（安装、添加 Agent、创建 worktree、并行分发）
- 整理常见问题解答（FAQ）与关键术语表
- 更新分类索引（03-agent-platforms-tools/README.md）添加本教程入口

## Non-Goals (Out of Scope)
- 不包含 Orca 源码的逐行代码级深度解析
- 不涉及 Electron/React 框架的完整教学
- 不提供 Claude Code、Codex、OpenCode 等单个 Agent 工具的详细使用教程
- 不进行 Orca 项目的代码贡献
- 不替代官方文档，仅作为学习导航与概念入门
- 不进行 Orca 与所有同类产品的全面功能对比（可适度提及但非重点）

## Background & Context
- **项目来源**：Stably.ai 出品，YC（Y Combinator）背书，MIT 协议开源
- **GitHub**：https://github.com/stablyai/orca（约 35.2k Star，每日更新频繁）
- **官网**：https://www.onorca.dev/
- **核心定位**：面向 100x 构建者的 AI 编排器——并排运行 Codex、Claude Code、OpenCode 或 Pi，每个都在自己的 worktree 中运行，并在一个地方统一跟踪
- **技术栈**（据本地源码 package.json 与目录结构确认）：
  - 桌面端：Electron + Electron-vite + React 19 + TypeScript（非 Tauri）
  - 终端：xterm.js（@xterm/addon-webgl 提供 WebGL 渲染，Ghostty-class）、node-pty 管理伪终端
  - 远程：ssh2（SSH Worktree）、WSL 支持、Windows 原生注册表
  - 集成：@linear/sdk（Linear）、GitHub/GitLab/Gitea/Bitbucket/Azure DevOps/Jira 客户端
  - 移动端：React Native / Expo（mobile/ 目录，含 iOS/Android）
  - 语音：sherpa-onnx（本地语音转文字 STT）
  - 其他：i18next 本地化、@xterm/addon-serialize 终端序列化、agent-browser（内置浏览器）
- **支持的 Agent**（README 所列，均可与任意 CLI Agent 配合）：Claude Code、Codex、Grok、Cursor、GitHub Copilot、OpenCode、MiMo Code、Amp、OpenClaude、Antigravity、Pi、oh-my-pi、Hermes Agent、Devin、Goose、Auggie、Autohand Code、Charm、Cline、Codebuff、Command Code 等
- **平台支持**：macOS、Windows、Linux 桌面端 + iOS/Android 移动端
- **官方定位**：ADI/ADE（Agent Development Environment）/ Agent IDE——强调"Agent 编排"而非传统"代码编辑"

## Functional Requirements
- **FR-1**: 创建原子化目录式 wiki 教程（orca-wiki/），含 README.md 索引与分章文件，完整目录导航系统
- **FR-2**: 编写项目概述章节，介绍 Orca 核心定位（AI Orchestrator for 100x builders）、YC 背书、Star 数、MIT 协议
- **FR-3**: 编写核心架构章节，解析技术栈（Electron+TypeScript、xterm.js WebGL、node-pty、ssh2、Expo 移动端）与"工作区/编排/终端/浏览器"分层
- **FR-4**: 编写八大核心功能详解章节
  - FR-4.1: 移动 Companion——手机监控/指挥 Agent，任务完成通知，随处发送后续指令
  - FR-4.2: 并行 Worktree——一个提示分发给多个 Agent，各自隔离 git worktree，比较结果择优合并
  - FR-4.3: 终端分屏——Ghostty-class 终端、WebGL 渲染、无限分屏、重启后滚动保留
  - FR-4.4: 设计模式——在真实 Chromium 窗口点击任意 UI 元素，将 HTML/CSS/截图送入 Agent 提示
  - FR-4.5: GitHub & Linear 原生集成——应用内浏览 PR/Issue/看板，从任务打开 worktree，无上下文切换
  - FR-4.6: SSH Worktree——在远程高配机器运行 Agent，支持文件编辑/git/终端、自动重连、端口转发
  - FR-4.7: 注释 AI Diff——在任意 diff 行留言并回传 Agent，应用内完成评审/编辑/提交
  - FR-4.8: 拖拽文件到 Agent——带自动保存的编辑器，拖文件/图片进 Agent 提示
- **FR-5**: 编写 Orca CLI 与编排章节，解析 `orca` CLI 命令面（worktree/terminal/repo/automations/browser/linear/computer/orchestration）与多 Agent 编排机制（Run/Task/Dispatch/worker_done）
- **FR-6**: 编写支持的 Agent 清单章节，列出 25+ CLI Agent 及简要说明
- **FR-7**: 编写快速上手指南章节，提供安装（macOS/Windows/Linux）、添加 Agent、创建 worktree、并行分发提示的完整流程
- **FR-8**: 编写移动端与生态接入章节（可选并入 FR-4），说明 iOS/Android 卡配对、远程监控
- **FR-9**: 编写核心价值总结与行业趋势章节，阐释"IDE 从代码编辑器向代理编排器"演进
- **FR-10**: 编写 FAQ 与术语表章节
- **FR-11**: 更新分类索引（03-agent-platforms-tools/README.md）添加本教程入口

## Non-Functional Requirements
- **NFR-1**: 文档语言通俗易懂，逻辑严谨，适合不同技术水平的读者（AI 编程新手 / 软件开发者 / 多 Agent 研究者）
- **NFR-2**: 在适当位置引用官网与本地源码作为参考依据
- **NFR-3**: 文档结构清晰，便于阅读和导航
- **NFR-4**: 文档格式符合项目规范（Markdown 格式、kebab-case 命名、YAML frontmatter 作为唯一标准格式，遵循 MDI v1.0 规范）
- **NFR-5**: 技术术语准确（如 worktree、orchestration、task/dispatch、worker_done、parallel worktrees、WebGL 终端），关键概念提供清晰解释
- **NFR-6**: 子代理产出物必须符合《子代理 Wiki 交付清单》的 5 项快速验收点

## Constraints
- **Technical**: 文档必须使用 Markdown 格式，遵循项目命名规范，放置在 .agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/ 目录下，原子化拆分多文件
- **Business**: 基于官网公开内容与本地开源源码创建，不得添加未验证的信息，客观说明项目当前状态
- **Dependencies**: 依赖已获取的官网内容与本地源码（README.md、skill-guides、package.json、目录结构），无需额外网络请求

## Assumptions
- 用户具备基本的命令行操作经验（PowerShell / curl / git）
- 用户了解基本的 AI Agent 概念（如 Claude Code、Codex 是 AI 编程工具）
- 用户了解基本的 git 概念（分支、工作区）
- 用户可以访问互联网下载 Orca 安装包与相应 Agent 工具

## Acceptance Criteria

### AC-1: Wiki 教程文档创建完成
- **Given**: spec.md 中定义的所有功能需求已明确
- **When**: 所有任务完成并通过验证
- **Then**: 原子化 wiki 教程包含 README.md 索引、目录导航、项目概述、核心架构、核心功能详解、CLI 与编排、Agent 清单、快速上手、FAQ 与术语表等完整章节
- **Verification**: `human-judgement`
- **Notes**: 文档应放置在 .agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/ 目录下，多文件原子化

### AC-2: 目录导航系统可用
- **Given**: 用户打开 wiki 教程 README.md
- **When**: 用户查看文档顶部的目录导航
- **Then**: 目录导航包含所有章节文件的链接，点击可跳转到对应章节
- **Verification**: `programmatic`
- **Notes**: 使用 Markdown 相对链接实现（禁止 file:/// 绝对路径）

### AC-3: 项目定位与核心价值阐述清晰
- **Given**: 用户阅读项目概述章节
- **When**: 用户理解 Orca 要解决的问题
- **Then**: 用户能够说明 Orca 是"面向 100x 构建者的 AI 编排器"，核心价值是"并排运行多个 Agent、各自在隔离 worktree 中、一个地方统一跟踪"
- **Verification**: `human-judgement`
- **Notes**: 引用官网"Ship 100x With The Agent IDE"定位与 YC 背书背景

### AC-4: 核心架构与技术栈阐述完整
- **Given**: 用户阅读核心架构章节
- **When**: 用户理解 Orca 的技术实现
- **Then**: 用户能够说明关键技术栈（Electron+TypeScript、xterm.js WebGL 终端、node-pty、ssh2、移动端 Expo）与整体分层
- **Verification**: `human-judgement`
- **Notes**: 解析设计思路而非源码细节，技术栈准确性以本地源码为准

### AC-5: 八大核心功能详解完整
- **Given**: 用户阅读核心功能详解章节
- **When**: 用户理解每个功能的能力边界
- **Then**: 用户能够说明：
  - 移动 Companion：手机监控/指挥、完成通知、随处发送后续指令
  - 并行 Worktree：一个提示分发多个 Agent、隔离 git worktree、比较择优
  - 终端分屏：Ghostty-class、WebGL 渲染、无限分屏、滚动保留
  - 设计模式：真实 Chromium 窗口点击 UI 元素、送 HTML/CSS/截图
  - GitHub & Linear 原生集成：应用内浏览 PR/Issue/看板、任务打开 worktree
  - SSH Worktree：远程运行、自动重连、端口转发
  - 注释 AI Diff：diff 行留言、回传 Agent、应用内评审
  - 拖拽文件到 Agent：自动保存编辑器、拖文件/图片进提示
- **Verification**: `human-judgement`
- **Notes**: 每个功能需包含功能说明、操作流程与应用价值

### AC-6: Orca CLI 与编排机制解析完整
- **Given**: 用户阅读 CLI 与编排章节
- **When**: 用户理解 Orca CLI 与多 Agent 编排
- **Then**: 用户能够说明 `orca` CLI 主要命令面（worktree/terminal/repo/automations/browser/linear/computer/orchestration）以及编排核心概念（Run/Task/Dispatch/worker_done）
- **Verification**: `human-judgement`
- **Notes**: 引用本地 skill-guides/orca-cli.md 与 orchestration.md 内容

### AC-7: 支持的 Agent 清单完整
- **Given**: 用户阅读 Agent 清单章节
- **When**: 用户了解 Orca 支持的 Agent
- **Then**: 用户能够列出至少 15 款 CLI Agent 及简要说明
- **Verification**: `human-judgement`
- **Notes**: 强调"适用于任意 CLI Agent——只要能在终端运行，就能在 Orca 运行"

### AC-8: 快速上手指南步骤明确
- **Given**: 用户按照快速上手指南执行
- **When**: 用户完成所有步骤
- **Then**: 用户能够完成：安装 Orca（macOS/Windows/Linux）、启动、添加 Agent、创建并分发 worktree、并行监控
- **Verification**: `human-judgement`
- **Notes**: 包含安装命令与核心操作流程代码块

### AC-9: 核心价值总结与行业趋势阐释清晰
- **Given**: 用户阅读核心价值总结章节
- **When**: 用户理解 Orca 的产品哲学
- **Then**: 用户能够用"IDE 从代码编辑器向代理编排器演进"概括 Orca 的行业意义，并说明"Bring your own Agent / Subscription"理念
- **Verification**: `human-judgement`
- **Notes**: 与开篇定位呼应

### AC-10: FAQ 章节实用
- **Given**: 用户遇到问题
- **When**: 用户查阅 FAQ 章节
- **Then**: 用户能够找到对应的解决方案或解释
- **Verification**: `human-judgement`
- **Notes**: FAQ 应覆盖常见问题（是否免费、支持哪些 Agent、支持哪些平台、是否支持移动端、是否需要自备 AI 订阅、并行 worktree 的隔离与磁盘占用等）

### AC-11: 资源链接有效
- **Given**: 用户点击资源链接章节中的链接
- **When**: 用户访问链接
- **Then**: 链接指向正确的资源页面
- **Verification**: `programmatic`
- **Notes**: 至少包含 GitHub 地址（https://github.com/stablyai/orca）、官网（https://www.onorca.dev/）、下载页（https://www.onorca.dev/download）

### AC-12: 分类索引更新完成
- **Given**: wiki 文档创建完成
- **When**: 查看 03-agent-platforms-tools/README.md
- **Then**: Agent 平台分类中新增 orca 教程条目，包含标题、摘要、文件数
- **Verification**: `programmatic`
- **Notes**: 遵循现有索引格式

## Open Questions
- [ ] 是否需要补充官网 docs 中更详细的特性文档分析？（建议在执行阶段视情况补充）
- [ ] 是否需要为 25+ Agent 整理一张对照表？（建议在 Agent 清单章节以列表+简短说明呈现）

## Impact
- **Affected specs**: 无直接影响的其他 spec（新建独立学习教程）
- **Affected code**: 仅新增文档文件，不涉及代码改动
- **Affected docs**: .agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/（新建原子化目录）、.agents/docs/knowledge/learning/03-agent-platforms-tools/README.md（更新索引）