# Orca 多代理 AI 编排器学习与 Wiki 教程文档 - 实施计划

## 说明
本项目采用原子化目录式 wiki 结构（参考 volcengine-agentkit-wiki / wsl-wiki / ai-powershell5-hell-wiki 的原子化组织方式）。目标目录：`.agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/`。

> **格式约束（执行前必读）**：每个子代理创建文件前，必须先读取同目录 1-2 个现有同类 wiki 文件（如 `.agents/docs/knowledge/learning/03-agent-platforms-tools/volcengine-agentkit-wiki/00-overview.md`、`wsl-wiki/01-installation.md`）确认实际 frontmatter 风格、链接格式、章节结构，以现有文件为权威标准，而非仅凭本 spec 描述。

## [x] Task 1: 创建原子化 wiki 目录框架与 README 索引
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 `.agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/` 目录
  - 创建 `README.md` 作为索引页：含 YAML frontmatter（title/source/date/tags）、项目一句话定位、目录导航（所有章节文件相对链接）、各章一句话摘要
  - 明确文件命名规范（kebab-case 纯英文、NN-*.md 编号）
  - **格式约束**：frontmatter 必须使用 YAML（--- 分隔），不得使用 TOML（+++ 分隔）；目录导航使用相对链接，禁止 file:/// 绝对路径
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-11]
- **Test Requirements**:
  - `programmatic` TR-1.1: 目录存在且含 README.md 索引
  - `programmatic` TR-1.2: frontmatter 使用 YAML 格式且包含必填字段（title/source/date/tags）
  - `human-judgement` TR-1.3: 目录导航结构完整，所有章节文件链接可跳转
  - `programmatic` TR-1.4: 包含官网 URL、GitHub URL、下载 URL

## [x] Task 2: 编写项目概述与核心定位章节
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 文件：`00-overview.md`
  - 阐述 Orca 核心定位：面向 100x 构建者的 AI 编排器（AI Orchestrator for 100x builders）
  - 引用官网"Ship 100x With The Agent IDE"定位
  - 介绍背景：Stably.ai 出品、YC 背书、MIT 协议、约 35.2k Star
  - 核心价值一句话：并排运行 Codex、Claude Code、OpenCode、Pi 等多个 Agent，各自在隔离 git worktree 中运行，在一个地方统一跟踪
  - 平台支持：macOS / Windows / Linux 桌面端 + iOS / Android 移动端
  - 用"传统多 Agent 开发痛点 vs Orca 解决方案"对照表呈现核心价值
- **Acceptance Criteria Addressed**: [AC-3]
- **Test Requirements**:
  - `human-judgement` TR-2.1: 核心定位阐述清晰（AI 编排器、100x builders）
  - `human-judgement` TR-2.2: 背景信息准确（YC 背书、MIT、Star 数）
  - `human-judgement` TR-2.3: 使用表格清晰对照痛点 vs 解决方案

## [x] Task 3: 编写核心架构与技术栈章节
- **Priority**: high
- **Depends On**: Task 2
- **Description**:
  - 文件：`01-core-architecture.md`
  - 解析技术栈（依据本地源码 package.json 与目录结构，准确性以源码为准）：
    - 桌面端：Electron + Electron-vite + React 19 + TypeScript（⚠️ 非 Tauri，注意与 EchoBird 区分）
    - 终端：xterm.js（@xterm/addon-webgl WebGL 渲染，Ghostty-class）、node-pty 伪终端
    - 远程：ssh2（SSH Worktree）、WSL 支持、Windows 原生注册表
    - 集成：@linear/sdk、GitHub/GitLab/Gitea/Bitbucket/Azure DevOps/Jira 客户端
    - 移动端：React Native / Expo
    - 语音：sherpa-onnx (STT)
  - 解析整体分层：主进程（src/main）、渲染进程（src/renderer）、preload、relay（远程桥接）、shared（共享类型）、cli（命令行）
  - 提供架构示意图（Mermaid 图表可选）
- **Acceptance Criteria Addressed**: [AC-4]
- **Test Requirements**:
  - `human-judgement` TR-3.1: 技术栈说明准确（Electron+TS、xterm.js WebGL、node-pty、ssh2、Expo）
  - `human-judgement` TR-3.2: 明确标注"非 Tauri"避免与同类工具混淆
  - `human-judgement` TR-3.3: 整体分层解析清晰

## [ ] Task 4: 编写八大核心功能详解章节
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 文件：`02-core-features.md`（核心功能总览 + 每功能包含功能说明/操作流程/应用价值）
  - **移动 Companion**：手机监控/指挥 Agent，任务完成通知，随处发送后续指令（iOS App Store / Android APK / TestFlight）
  - **并行 Worktree**：一个提示分发多个 Agent，各自隔离 git worktree，比较结果择优合并
  - **终端分屏**：Ghostty-class 终端、WebGL 渲染、无限分屏、重启后滚动保留
  - **设计模式**：真实 Chromium 窗口点击任意 UI 元素，将 HTML/CSS/截图送入 Agent 提示
  - **GitHub & Linear 原生集成**：应用内浏览 PR/Issue/看板，从任务打开 worktree，无上下文切换
  - **SSH Worktree**：远程高配机器运行 Agent，文件编辑/git/终端、自动重连、端口转发
  - **注释 AI Diff**：任意 diff 行留言并回传 Agent，应用内完成评审/编辑/提交
  - **拖拽文件到 Agent**：带自动保存的编辑器，拖文件/图片进 Agent 提示
  - 附加功能速览：Quick open、账户切换与用量追踪、富仓库预览、Computer Use、通知与未读状态、Orca CLI
- **Acceptance Criteria Addressed**: [AC-5]
- **Test Requirements**:
  - `human-judgement` TR-4.1: 八大核心功能每个都有详细说明
  - `human-judgement` TR-4.2: 每个功能包含功能说明、操作流程、应用价值
  - `human-judgement` TR-4.3: 附加功能速览完整（Quick open/用量追踪/计算机使用/通知等）

## [x] Task 5: 编写 Orca CLI 与多 Agent 编排章节
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 文件：`03-orca-cli-orchestration.md`
  - 解析 `orca` CLI 命令面（参考本地 skill-guides/orca-cli.md）：
    - worktree（create/list/ps/current/set/rm）
    - terminal（create/list/read/wait/send/split/stop）
    - repo（list/add/show/set-base-ref）
    - automations（create/list/run）
    - browser（goto/snapshot/click/fill/type）
    - linear（issue/list/status/attach/comment）
    - computer（computer-use 桌面 UI 控制）
    - orchestration（编排子命令）
  - 解析多 Agent 编排机制（参考本地 skill-guides/orchestration.md）：
    - 核心概念：Run（命名空间/收件箱）、Task（工作项）、Dispatch（任务分配）、worker_done（完成回执）
    - 受监督工作流：task-create → worker-start → check --wait
    - 完整交接（full handoff）与受监督编排的区别
  - 提供常见命令代码块（可直接复制）
- **Acceptance Criteria Addressed**: [AC-6]
- **Test Requirements**:
  - `human-judgement` TR-5.1: CLI 主要命令面解析完整
  - `human-judgement` TR-5.2: 编排核心概念（Run/Task/Dispatch/worker_done）解释准确
  - `human-judgement` TR-5.3: 提供受监督工作流与完整交接的区别说明
  - `programmatic` TR-5.4: 命令以代码块形式呈现

## [x] Task 6: 编写支持的 Agent 清单章节
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 文件：`04-supported-agents.md`
  - 强调核心能力："适用于任意 CLI Agent——只要能在终端运行，就能在 Orca 运行"
  - 列出至少 15 款 CLI Agent 及简要说明：Claude Code、Codex、Grok、Cursor、GitHub Copilot、OpenCode、MiMo Code、Amp、OpenClaude、Antigravity、Pi、oh-my-pi、Hermes Agent、Devin、Goose、Auggie、Autohand Code、Charm、Cline、Codebuff、Command Code 等
  - 说明"自带 Agent / 订阅"（Bring your own Agent / Subscription）理念
- **Acceptance Criteria Addressed**: [AC-7]
- **Test Requirements**:
  - `human-judgement` TR-6.1: 至少列出 15 款 CLI Agent 及简要说明
  - `human-judgement` TR-6.2: 强调"任意 CLI Agent 皆可运行"
  - `human-judgement` TR-6.3: 说明自带 Agent/订阅理念

## [ ] Task 7: 编写快速上手指南章节
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 文件：`05-quickstart.md`
  - **第一步：安装 Orca**（macOS/Windows/Linux，参考官网下载页 https://www.onorca.dev/download）
  - **第二步：启动并登录**，接入已有 Agent 订阅
  - **第三步：添加/连接 Agent**（Claude Code、Codex 等）
  - **第四步：创建并分发 worktree**（一个提示分发到多个隔离 worktree）
  - **第五步：并行监控与择优合并**（终端分屏、移动端监控、diff 注释）
  - 所有命令以代码块形式呈现，可直接复制执行
- **Acceptance Criteria Addressed**: [AC-8]
- **Test Requirements**:
  - `human-judgement` TR-7.1: 五步流程完整
  - `programmatic` TR-7.2: 安装命令/下载链接正确
  - `human-judgement` TR-7.3: 强调"自带 Agent/订阅"与并行工作流
  - `human-judgement` TR-7.4: 代码块可直接复制

## [x] Task 8: 编写核心价值总结与行业趋势章节
- **Priority**: medium
- **Depends On**: Task 7
- **Description**:
  - 文件：`06-value-and-trends.md`
  - 阐释 Orca 的产品哲学："IDE 从代码编辑器向代理编排器演进"
  - 核心价值："一个地方统一跟踪多个 Agent、并行工作区隔离、结果择优合并"
  - 行业趋势：多 Agent 并行开发的范式变革、Git Worktree 作为一等公民
  - 阐明"Bring your own Agent / Subscription"的自带 Agent 理念
  - 与开篇定位呼应
- **Acceptance Criteria Addressed**: [AC-9]
- **Test Requirements**:
  - `human-judgement` TR-8.1: 核心价值总结到位
  - `human-judgement` TR-8.2: 行业趋势阐释清晰（编辑器→编排器）
  - `human-judgement` TR-8.3: 与开篇定位呼应

## [x] Task 9: 编写 FAQ 与术语表章节
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 文件：`07-faq-glossary.md`
  - 整理常见问题并提供解答，如：
    - Q: Orca 是免费的吗？开源协议是什么？
    - Q: Orca 支持哪些操作系统？
    - Q: Orca 支持哪些 AI Agent 工具？
    - Q: 是否需要自备 AI 订阅（Claude/Codex 等）？
    - Q: 并行 worktree 会占用多少磁盘空间？如何隔离？
    - Q: 是否支持移动端远程监控？
    - Q: 移动端如何配对？
    - Q: 与 VS Code / Cursor 等传统 IDE 有什么区别？
    - Q: 是否支持中文界面？
  - 术语表（≥15 个核心术语）：worktree、parallel worktrees、orchestration、Run、Task、Dispatch、worker_done、full handoff、WebGL 终端、Ghostty-class、design mode、SSH worktree、注输入 AI diff、automation、computer use、mobile companion、quick open、agent IDE 等
- **Acceptance Criteria Addressed**: [AC-10]
- **Test Requirements**:
  - `human-judgement` TR-9.1: 至少包含 8 个 FAQ 问题
  - `human-judgement` TR-9.2: 术语表 ≥15 个核心术语，每个有一句话通俗解释
  - `human-judgement` TR-9.3: 解答清晰准确

## [x] Task 10: 更新分类索引 03-agent-platforms-tools/README.md
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 在 `.agents/docs/knowledge/learning/03-agent-platforms-tools/README.md` 中新增 orca 教程条目
  - 在「📚 子Wiki索引」表格新增一行：`[orca-wiki/](orca-wiki/README.md)`、文件数、核心主题摘要
  - 如适用，更新「Agent平台与工具生态分类」表与「快速导航」中相关位置
  - **格式约束**：先读取现有 README.md 确认实际表格格式，再追加新行
- **Acceptance Criteria Addressed**: [AC-12]
- **Test Requirements**:
  - `programmatic` TR-10.1: 03-agent-platforms-tools/README.md 中新增 orca-wiki 条目
  - `human-judgement` TR-10.2: 摘要准确概括教程内容
  - `programmatic` TR-10.3: 表格格式与现有条目一致
  - `programmatic` TR-10.4: 链接指向 orca-wiki/README.md 正确

## [x] Task 11: 子代理产出物验收（5 项快速验收点）
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 主代理对子代理交付的 wiki 文档执行 5 项快速验收：
    1. **frontmatter 格式合规**：使用 YAML（--- 分隔）而非 TOML（+++ 分隔）
    2. **文件路径正确**：位于 .agents/docs/knowledge/learning/03-agent-platforms-tools/orca-wiki/
    3. **文件名合规**：kebab-case、纯英文、无中文字符（运行 `python .agents/scripts/check-filename-convention.py` 验证）
    4. **内容完整性**：12 个 AC 全部满足，章节结构完整
    5. **链接有效性**：目录导航相对链接可跳转、外部 URL 指向正确资源（运行 `python .agents/scripts/check-links.py` 验证）
  - 任一验收点未通过则创建修复任务并交回子代理处理
- **Acceptance Criteria Addressed**: [AC-1, AC-2, AC-11, AC-12]
- **Test Requirements**:
  - `programmatic` TR-11.1: frontmatter 使用 YAML 格式
  - `programmatic` TR-11.2: 文件路径与命名合规
  - `programmatic` TR-11.3: 文件名命名规范检查通过
  - `human-judgement` TR-11.4: 12 个 AC 全部满足
  - `programmatic` TR-11.5: 链接有效性检查通过

# Task Dependencies
- Task 1 → Task 2 → Task 3 → Task 4 → Task 5 → Task 6 → Task 7 → Task 8 → Task 9 → Task 10 → Task 11
- 大部分任务为串行依赖（内容递进），Task 2~9 可在 Task 1 完成后并行执行（各章内容相对独立，但建议按序以保持一致性）
- Task 10（更新索引）依赖 Task 9 完成后内容确定
- Task 11（验收）依赖所有前序任务完成