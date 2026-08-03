---
id: "orca-wiki-quickstart"
title: "快速上手指南"
source: "https://www.onorca.dev/download 官网 + d:\AI\external\tools\orca 本地开源源码（docs/readme/README.zh-CN.md、skill-guides/orca-cli.md）"
category: "learning"
tags: ["orca", "stablyai", "quickstart", "安装", "worktree", "claude-code", "codex", "并行", "多agent", "入门"]
date: "2026-08-03"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Orca 五步快速上手流程：第一种安装 Orca（macOS Homebrew / Arch AUR / Windows .exe）、第二步启动并登录接入 Agent 订阅、第三步添加连接 Agent（Claude Code、Codex 等）、第四步创建并分发 worktree（一个提示分发到多个隔离 worktree）、第五步并行监控与择优合并（终端分屏、移动端监控、diff 注释），全部命令可直接复制执行。"
last_verified: "2026-08-03"
wiki_version: "1.0"
orca_version_target: "1.4.165-rc.0"

---

# 05 快速上手指南

本章带领你用 **五步** 完成 Orca 从零到能跑：安装 → 启动登录 → 添加 Agent → 创建并分发 worktree → 并行监控与择优合并。所有命令均以代码块呈现，可直接复制到终端执行。本章是初次体验 Orca 的最佳入口，建议与 [01 核心架构](./01-core-architecture.md)、[03 Orca CLI 与多 Agent 编排](./03-orca-cli-orchestration.md) 配合阅读。

> **📌 前置条件**：一个可用的 Git 仓库（本地或远程均可）、至少一个已安装到本机的 CLI Agent（如 Claude Code、Codex）。Orca 支持 macOS / Windows / Linux 三平台桌面端，以及 iOS / Android 移动 Companion。

## 第一步：安装 Orca

Orca 桌面端支持 macOS、Windows、Linux，并可通过包管理器安装。

### macOS（Homebrew）

```bash
brew install --cask stablyai/orca/orca
```

如需手动安装，可下载官方安装包：macOS Apple Silicon（arm64）或 macOS Intel（x64）的 `.dmg` 文件。

### Arch Linux（AUR）

```bash
# 直接安装预编译二进制
yay -S stably-orca-bin

# 或从源码构建（较慢）
yay -S stably-orca-git
```

### Windows

Windows 用户直接下载官方 `.exe` 安装包即可：

```text
orca-windows-setup.exe
```

安装包可从官网下载页（https://www.onorca.dev/download）或 GitHub Releases 获取。Linux 用户亦可下载 `.AppImage` 运行。

### 移动 Companion（可选）

完成桌面端安装后，可在手机上安装 Companion 应用用于远程监控：

- **iOS**：App Store 搜索 Orca（或 TestFlight）
- **Android**：下载官方 APK

## 第二步：启动并登录，接入已有 Agent 订阅

安装完成后启动 Orca 桌面应用。首次启动需完成登录/授权，以便接入你已有的 Agent 付费订阅（Claude、Codex 等）。

```bash
# 启动 Orca（若已安装为 CLI 可执行）
orca open --json

# 确认 Orca 已就绪
orca status --json
```

> **提示**：Orca 内置**账号切换与用量追踪**功能，可查看 Claude 和 Codex 的用量与限额重置时间，并支持无需重新登录即可热切换账号。

## 第三步：添加 / 连接 Agent

Orca 适配**任何 CLI Agent**——只要能在终端里运行，就能在 Orca 中运行。以 Claude Code、Codex 为例，其 CLI 已内置在 Orca 的 Agent 启动器中，使用已知 id：`claude`、`codex`、`grok`、`omp`、`pi` 等。

在 Orca 中连接 Agent 的本质是**在 Orca 托管的终端里启动对应 Agent CLI**。两种典型方式：

**方式一：在已有 worktree 的当前终端启动 Agent**（不新建 worktree）

```bash
orca terminal create --worktree active --command "codex" --json
```

**方式二：新建 worktree 并直接启动 Agent**（Agent 进入第一个终端，配合 `--prompt` 发送初始工作）

```bash
orca worktree create --name my-task --agent claude --prompt "帮我重构这个模块" --json
```

> **👀 延伸**：除内置 Agent 外，任何安装了 CLI 的 Agent（如 OpenCode、Cursor CLI、GitHub Copilot、Qwen Code 等）均可通过 `orca terminal create --command "<agent>"` 方式接入。Agent 清单详见 [04 支持的 Agent 清单](./04-supported-agents.md)。

## 第四步：创建并分发 worktree（一个提示分发到多个隔离 worktree）

Orca 的核心能力是**并行 Worktree**：把一个提示同时分发给多个智能体，每个都在自己**隔离的 git worktree** 中运行，随后比较结果、合并最佳方案。

**创建单个 worktree 并分发提示**：

```bash
orca worktree create --name fix-login --agent codex --prompt "修复登录超时问题" --json
```

**一个提示分发到多个隔离 worktree**（如分别用 Claude Code 与 Codex 并行处理同一任务）：

```bash
orca worktree create --name fix-login-claude --agent claude --prompt "修复登录超时问题" --json
orca worktree create --name fix-login-codex  --agent codex  --prompt "修复登录超时问题" --json
```

**创建独立（顶层）worktree**（不继承当前分支，走仓库默认基线）：

```bash
orca worktree create --name independent-task --no-parent --json
```

> **关键规则**：`orca worktree create` 返回的 `worktree.id` 是两段式地址 `<repoId>::<worktreePath>`，如 `repo-123::/Users/me/orca/fix-login`。后续命令需**复制完整 id**，仅 `repo-123` 只能定位仓库而非 worktree。选择器支持 `id:<repoId>::<worktreePath>`、`name:<displayName>`、`branch:<branchName>` 等。

## 第五步：并行监控与择优合并

多个 Agent 在各自 worktree 中并行运行后，Orca 提供多种方式监控与择优合并。

### 终端分屏

在单个 worktree 或工作区内，用 Ghostty 级终端分屏同时观察多个 Agent 的输出：

```bash
# 垂直分屏（上下）
orca terminal split --terminal <handle> --direction vertical --json

# 水平分屏（左右），并指定命令
orca terminal split --terminal <handle> --direction horizontal --command "npm test" --json
```

### 移动端监控

用手机 Companion 应用监控各 Agent 运行状态——智能体完成时收到通知，可随时随地发送后续指令，无需守在电脑前。

### 查看并行 worktree 状态

```bash
orca worktree ps --json
orca worktree set --worktree active --comment "修复完成；正在跑集成测试" --json
```

### diff 注释与择优合并

对不同 Agent 产出的 diff 逐行比对，在任意 diff 行上添加评论并发回给智能体，评审、编辑、提交全程无需离开 Orca：

```bash
# 查看当前 worktree 的 diff 上下文
orca worktree show --worktree active --json
```

评审后选定最优方案，将其 worktree 的变更合并回主分支即可完成择优合并。

> **💡 最佳实践**：用 `orca worktree set --worktree <selector> --workspace-status in-review` 标记评审中的 worktree，卡片状态默认值为 `todo`、`in-progress`、`in-review`、`completed`，便于在众多并行 worktree 中快速定位进度。

---

## 小结

| 步骤 | 动作 | 关键命令 / 操作 |
|------|------|----------------|
| 第一步 | 安装 Orca | `brew install --cask stablyai/orca/orca` / `yay -S stably-orca-bin` / Windows `.exe` |
| 第二步 | 启动并登录 | `orca open --json` 接入已有 Agent 订阅 |
| 第三步 | 添加 / 连接 Agent | `orca terminal create` / `orca worktree create --agent` |
| 第四步 | 创建并分发 worktree | 一个提示分发到多个隔离 worktree（`--agent` + `--prompt`） |
| 第五步 | 并行监控与择优合并 | 终端分屏、移动端监控、`orca worktree ps`、diff 注释 |

至此，你已完成 Orca 的快速上手，能够并行运行多个 Agent 并择优合并。后续可深入学习 [06 核心价值总结与行业趋势](./06-value-and-trends.md) 理解其行业定位，或查阅 [07 FAQ 与术语表](./07-faq-glossary.md) 解决常见问题。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [04 支持的 Agent 清单](./04-supported-agents.md) | [README](./README.md) | [06 核心价值总结与行业趋势](./06-value-and-trends.md) → |