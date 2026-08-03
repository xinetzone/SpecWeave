---
id: "orca-wiki-features"
title: "八大核心功能详解"
source: "https://www.onorca.dev/ 官网 + d:\AI\external\tools\orca 本地开源源码（README / docs/readme/README.zh-CN.md）"
category: "learning"
tags: ["orca", "stablyai", "ai-orchestrator", "agent-ide", "worktree", "mobile-companion", "ssh", "design-mode", "ai-diff", "github", "linear", "terminal-splits", "multi-agent"]
date: "2026-08-03"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Orca 八大核心功能总览：移动 Companion、并行 Worktree、终端分屏、设计模式、GitHub&Linear 原生集成、SSH Worktree、注释 AI Diff、拖拽文件，每项含功能说明/操作流程/应用价值，并附附加功能速览。"
last_verified: "2026-08-03"
wiki_version: "1.0"
orca_version_target: "1.4.165-rc.0"

---

# 02 八大核心功能详解

本章是 Orca 核心能力的总览。Orca 的定位是"面向 100x 构建者的 AI 编排器"——并排运行 Codex、Claude Code、OpenCode 或 Pi，每个都在自己的 worktree 中运行，并在一个地方统一跟踪。这八大功能共同构成了"多 Agent 并行 + 远程监控指挥 + 零上下文切换评审"的完整编排闭环。

## 功能总览表

| 序号 | 功能 | 一句话定位 | 官方文档 |
|------|------|-----------|---------|
| 1 | 移动 Companion | 手机监控/指挥 Agent | https://www.onorca.dev/docs/mobile |
| 2 | 并行 Worktree | 一个提示分发多个 Agent，择优合并 | https://www.onorca.dev/docs/model/worktrees |
| 3 | 终端分屏 | Ghostty-class 终端、无限分屏、滚动保留 | https://www.onorca.dev/docs/terminal |
| 4 | 设计模式 | 点击真实 Chromium 窗口 UI 元素送入 Agent | https://www.onorca.dev/docs/browser/design-mode |
| 5 | GitHub & Linear 原生集成 | 应用内浏览 PR/Issue/看板，无上下文切换 | https://www.onorca.dev/docs/review/linear |
| 6 | SSH Worktree | 远程高配机器运行 Agent，自动重连 | https://www.onorca.dev/docs/ssh |
| 7 | 注释 AI Diff | 任意 diff 行留言并回传 Agent | https://www.onorca.dev/docs/review/annotate-ai-diff |
| 8 | 拖拽文件到 Agent | 带自动保存的编辑器，拖文件/图片进提示 | https://www.onorca.dev/docs/editing/file-explorer |

---

## 1. 移动 Companion

### 功能说明

移动 Companion 是 Orca 的配套手机应用，用于从手机端监控并指挥你的 Agent。当 Agent 完成任务时，你会实时收到通知；无论身在何处，都能随时发送后续指令（follow-up），实现"随时随地的 Agent 指挥"。

**分发渠道**：
- **iOS**：可从 [App Store](https://apps.apple.com/us/app/orca-ide/id6766130217) 下载，或通过 [TestFlight](https://testflight.apple.com/join/YjeGMQBA) 加入测试
- **Android**：下载 [Android APK (v0.0.36)](https://github.com/stablyai/orca/releases/download/mobile-android-v0.0.36/app-release.apk)

### 操作流程

1. 在桌面端安装并登录 Orca（macOS / Windows / Linux）
2. 手机上安装移动 Companion 应用（iOS App Store / TestFlight 或 Android APK）
3. 将手机应用与桌面应用**配对**（扫描二维码或配对码）
4. 在桌面端分发 Agent 任务
5. 任务完成时手机收到**通知**，可查看结果
6. 随时在手机上输入**后续指令**，回传给桌面端正在运行的 Agent

### 应用价值

- **解除"守着电脑"的约束**：Agent 长时间运行时，无需守在桌面端，任务完成自动通知
- **移动端管控**：出差、通勤、会议间隙即可跟进任务进度、追加指令
- **与桌面端形成闭环**：桌面端负责计算与执行，手机端负责监控与指挥，分工明确

---

## 2. 并行 Worktree

### 功能说明

并行 Worktree 是 Orca 的核心编排能力：**一个提示可以同时分发给多个 Agent**，每个 Agent 都在自己**隔离的 git worktree** 中独立运行，互不干扰。完成后对比各 Agent 的产出结果，合并最优方案。

### 操作流程

1. 在 Orca 中通过 Quick open 或命令面板创建分发（Dispatch）任务
2. 输入**一个提示**（prompt），并选择要分发的多个 Agent（如 Codex、Claude Code、OpenCode 等）
3. Orca 为每个 Agent 自动创建**独立的 git worktree**，实现工作区隔离
4. 各 Agent 并行执行，Orca 统一跟踪进度
5. 各 Agent 完成后，**对比结果**（查看 diff、产物）
6. 选择**最优方案**，将其合并进主分支

### 应用价值

- **方案多样性**：同一问题让多个 Agent 各自给出实现，获得不同思路
- **隔离安全**：每个 Agent 在独立 worktree 中运行，互不污染、可安全回滚
- **并行提速**：多 Agent 同时工作，显著缩短复杂任务的完成时间
- **择优合并**：通过对比选择最佳实现，避免单一 Agent 的盲区

---

## 3. 终端分屏

### 功能说明

Orca 内置了 **Ghostty 同级别的终端**，采用 **WebGL 渲染**，性能优秀；支持**无限分屏**（infinite splits），并能在**重启后依然保留滚动历史**（scrollback）。

### 操作流程

1. 在 Orca 工作区中打开内置终端
2. 通过分屏操作（如快捷键或拖拽）创建**多个终端分屏**
3. 在多个分屏中并行运行不同命令或 Agent
4. 需要时上下滚动查看历史输出
5. **重启 Orca** 后，滚动历史与分屏布局依然保留

### 应用价值

- **高性能渲染**：WebGL 渲染带来流畅的终端体验，媲美专门终端应用
- **多任务并行**：无限分屏让你同时监控多个 Agent 或多个命令的执行
- **状态持久**：重启后滚动历史保留，避免丢失重要上下文，适合长时间开发会话

---

## 4. 设计模式

### 功能说明

设计模式（Design Mode）是 Orca 内置浏览器的一项能力：在**真实的 Chromium 窗口**中，点击**任意 UI 元素**，即可把该元素的 **HTML、CSS 以及裁剪好的截图**直接发送到 Agent 的提示中，让 Agent 理解并修改界面。

### 操作流程

1. 在 Orca 中打开内置浏览器（Chromium 内核）
2. 进入**设计模式**（Design Mode）
3. 在真实渲染的页面中**点击任意 UI 元素**
4. Orca 自动提取该元素的 **HTML、CSS** 并生成**裁剪截图**
5. 这些素材被自动注入 Agent 的提示上下文
6. Agent 依据真实 UI 代码与截图，完成样式调整或 bug 修复

### 应用价值

- **所见即所得**：直接点击真实渲染的 UI，而非抽象描述，Agent 理解更准确
- **上下文聚焦**：裁剪截图 + 精确的 HTML/CSS，避免 Agent 处理无关页面代码
- **高效前端迭代**：适合样式微调、组件修复、响应式问题定位等前端场景

---

## 5. GitHub & Linear 原生集成

### 功能说明

Orca 原生集成了 **GitHub 与 Linear**：在应用内即可浏览 **PR、issue 和项目看板**，从任意任务直接**打开一个 worktree** 进行开发，全程**无需切换上下文**即可完成代码评审。

### 操作流程

1. 在 Orca 中连接 GitHub 与 Linear 账号
2. 在应用内浏览 **Pull Request、Issue 与项目看板**
3. 从任意任务点击"打开 worktree"，Orca 自动创建对应的工作区
4. 在 worktree 中运行 Agent 完成开发
5. 提交后回到应用内**完成评审**（结合注释 AI Diff 能力）
6. 全程不离开 Orca，避免上下文切换

### 应用价值

- **零上下文切换**：开发、评审、看板操作全部在应用内完成，保持心流
- **任务驱动的开发闭环**：从 Issue/看板直接生成 worktree，开发与任务管理强关联
- **团队协作透明**：PR 与看板状态直观可见，便于团队同步进度

---

## 6. SSH Worktree

### 功能说明

SSH Worktree 允许在**远程高性能机器**上运行 Agent，完整支持**文件编辑、git 和终端**操作，并内置**自动重连**与**端口转发**能力，让本地与远程无缝协同。

### 操作流程

1. 在 Orca 中配置 SSH 连接（远程主机、凭据）
2. 在远程机器上创建 worktree
3. 在远程 worktree 中运行 Agent，执行文件编辑、git 操作与终端命令
4. 网络中断时**自动重连**，任务不受影响
5. 通过**端口转发**访问远程服务（如本地预览远程启动的开发服务器）
6. 本地体验与远程执行无缝衔接

### 应用价值

- **性能杠杆**：在远程高配机器上运行计算密集的 Agent 任务，不受本地硬件限制
- **连接韧性**：自动重连保证长任务不因网络波动中断
- **端口转发**：远程服务可直接通过本地访问，开发调试体验一致
- **资源集中**：适合需要统一算力、GPU 或专用环境的场景

---

## 7. 注释 AI Diff

### 功能说明

注释 AI Diff 允许你在**任意 diff 行**上添加评论，并**把评论回传给 Agent**——评审、编辑、提交，全程无需离开 Orca，实现"应用内闭环的人工评审"。

### 操作流程

1. Agent 生成代码后，Orca 展示其 **AI Diff**
2. 在任意 diff 行上**添加评论**（标注具体问题或修改要求）
3. 将评论与 diff **回传给 Agent**
4. Agent 依据评论进行**针对性修改**
5. 在应用内**审核更新后的 diff**，必要时继续注释
6. 满意后**提交**，全程不离开 Orca

### 应用价值

- **精确定位问题**：在具体代码行上标注，评审意见有的放矢
- **闭环迭代**：评论回传 → Agent 修改 → 再次评审，形成快速迭代循环
- **评审内嵌**：评审、编辑、提交三位一体，减少工具切换成本

---

## 8. 拖拽文件到 Agent

### 功能说明

Orca 自带 **VS Code 级别的编辑器**，且**处处自动保存**。你可把**文件或图片直接拖入 Agent 的提示**，让 Agent 直接读取或理解这些素材。

### 操作流程

1. 在 Orca 中打开内置编辑器（VS Code 级体验）
2. 编辑文件，系统**自动保存**，无需手动 Ctrl+S
3. 将**文件或图片**从文件管理器**直接拖入 Agent 提示框**
4. Agent 自动读取文件内容或识别图片
5. 在提示中附带指令，Agent 依据素材完成任务

### 应用价值

- **素材即拖即用**：文件、图片直接进入提示，省去手动输入路径
- **自动保存无忧**：自动保存避免因忘记保存导致的上下文丢失
- **丰富上下文**：图片等非文本素材让 Agent 能处理视觉相关任务

---

## 9. 附加功能速览

除八大核心功能外，Orca 还"开箱即用"地提供以下能力：

| 功能 | 说明 | 官方文档 |
|------|------|---------|
| **Quick open** | 在 worktree、文件、Agent、命令和仓库上下文之间搜索，不打断心流 | https://www.onorca.dev/docs/model/quick-open |
| **账号切换与用量追踪** | 查看 Claude 和 Codex 的用量与限额重置时间，无需重新登录即可热切换账号 | https://www.onorca.dev/docs/agents/usage-tracking |
| **富仓库预览** | 在工作区中预览 Markdown、图片、PDF 和仓库文档 | https://www.onorca.dev/docs/editing/markdown |
| **Computer Use** | 当工作流需要真实交互时，让 Agent 操作桌面应用和可见 UI | https://www.onorca.dev/docs/cli/computer-use |
| **通知与未读状态** | 第一时间知道 Agent 何时完成或需要关注，可将会话标记为未读，稍后再处理 | https://www.onorca.dev/docs/notifications |
| **Orca CLI** | Agent 也能驱动 Orca——用 `orca worktree create`、`snapshot`、`click`、`fill` 等命令把工作流脚本化 | https://www.onorca.dev/docs/cli/overview |

> **说明**：Orca 每日发布新功能，上述列表永远滞后于实际。真正的功能清单以 [更新日志](https://github.com/stablyai/orca/releases) 为准。

---

## 本章小结

| 维度 | 关键能力 |
|------|---------|
| 并行执行 | 并行 Worktree 分发多 Agent，独立隔离、择优合并 |
| 远程指挥 | 移动 Companion 手机监控、SSH Worktree 远程高配机器 |
| 界面交互 | 设计模式点击真实 UI、拖拽文件图片进提示 |
| 评审闭环 | GitHub & Linear 任务工作流、注释 AI Diff 行内评审 |
| 终端与搜索 | 终端分屏、Quick open、富仓库预览、CLI 脚本化 |

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [01 核心架构与技术栈](./01-core-architecture.md) | [README](./README.md) | → [03 Orca CLI 与多 Agent 编排](./03-orca-cli-orchestration.md) |