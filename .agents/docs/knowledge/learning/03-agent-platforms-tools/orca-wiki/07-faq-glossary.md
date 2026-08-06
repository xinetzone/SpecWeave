---
id: "orca-wiki-faq"
title: "FAQ 与术语表"
source: "https://www.onorca.dev/ 官网 FAQ + d:\AI\external\tools\orca 本地开源源码（README.md / skill-guides/orchestration.md）"
category: "learning"
tags: ["orca", "stablyai", "ai-orchestrator", "faq", "glossary", "worktree", "orchestration", "multi-agent", "wiki教程"]
date: "2026-08-03"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Orca 常见问题解答（9 个覆盖开源协议/系统支持/Agent 支持/自带订阅/磁盘隔离/移动端/IDE 对比/中文本地化）+ 18 个核心术语一张表通俗解释，作为本教程速查手册。"
last_verified: "2026-08-03"
wiki_version: "1.0"

---

# 07 FAQ 与术语表

> 本章是本教程的速查手册：第一部分汇总新手最常问的 9 个问题，第二部分为 18 个核心术语提供一句话通俗解释。术语对应的底层机制详见第 01 章（架构）、第 02 章（核心功能）、第 03 章（CLI 与编排）。

## 7.1 常见问题 FAQ

### Q1：Orca 是免费的吗？开源协议是什么？

**是免费的。** Orca 采用 **MIT 开源许可证**，可自由使用、修改与分发，无论是个人还是商业场景均无授权费用。它由 Stably.ai 团队开发，已通过 Y Combinator（YC）孵化，源码托管在 GitHub（stablyai/orca）。作为"面向 100x 构建者的 AI 编排器"，Orca 遵循"自带 Agent / 自带订阅"理念——应用本身免费，但运行它需要你自备所调用的 AI Agent 服务。

### Q2：Orca 支持哪些操作系统？

**桌面端覆盖三大主流桌面系统，移动端覆盖两大移动平台：**

- **桌面端**：macOS（Apple Silicon 与 Intel 均有构建）、Windows（.exe 安装包）、Linux（AppImage），亦可通过 Homebrew（macOS）、AUR（Arch Linux）安装。
- **移动端**：iOS（App Store / TestFlight）、Android（APK 安装包），作为桌面端的 Companion 配套应用。

### Q3：Orca 支持哪些 AI Agent 工具？

**几乎支持任意 CLI Agent。** 只要某个 Agent 能在终端里运行，它就能在 Orca 中运行。官方清单已覆盖 **25+ 款**常见 Agent，包括 Claude Code、Codex、Grok、Cursor、GitHub Copilot、OpenCode、MiMo Code、Amp、OpenClaude、Antigravity、Pi、oh-my-pi、Hermes Agent、Devin、Goose、Auggie、Autohand Code、Charm、Cline、Codebuff、Command Code、Continue、Droid、Kilocode、Kimi、Kiro、Mistral Vibe、Qwen Code、Rovo Dev 等，清单外仍可扩展接入。

### Q4：是否需要自备 AI 订阅（Claude / Codex 等）？

**是的，这是 Orca 的设计理念。** Orca 应用本身是免费开源的，但本质是一个"编排器"而非"模型供应方"——它不内置模型额度，而是调用你已订阅的 Agent 服务（如 Claude Code 对应的 Claude 订阅、Codex 对应的 OpenAI 订阅）。Orca 内置 **账户切换与用量追踪**，可查看各账号的用量与限流重置时间，并免重新登录快速热切换账号。

### Q5：并行 worktree 会占用多少磁盘空间？如何隔离？

**依赖仓库与缓存情况，但 git worktree 天然轻量。** 每个 worktree 是 git 的"工作树"（worktree），通过符号链接共享同一份仓库对象库（`.git`），因此**不会为每个分支复制整份仓库**，仅新增工作区文件与差异对象，磁盘占用显著小于多个独立克隆。隔离机制由 git worktree 保证：每个 Agent 在自己的工作目录中独立读写，互不干扰，可放心并行运行多个 Agent 后择优合并结果。

### Q6：是否支持移动端远程监控？

**支持。** Orca 提供 **移动 Companion**（iOS / Android），与桌面端配对后即可在手机上监控并指挥 Agent：Agent 完成时收到推送通知，随时随地发送后续指令，无需守在电脑前。配对通过桌面端扫码完成（详见 Q7）。

### Q7：移动端如何配对？

**在桌面端完成配对。** 在桌面 Orca 应用中打开移动 Companion 的配对码/二维码，用手机上的 Orca Companion App 扫码即可建立连接。配对后手机成为桌面端的安全远程控制端，可查看 Agent 状态、收通知、发指令。

### Q8：与 VS Code / Cursor 等传统 IDE 有什么区别？

**核心理念不同：编排器 vs 编辑器。** 传统 IDE（VS Code、Cursor）以"代码编辑"为核心，把 AI 作为辅助写代码的插件；而 Orca 以"**多 Agent 编排**"为核心，把 AI Agent 当作并行的"执行者"，你像项目经理一样把任务分发给多个 Agent（各自在不同 worktree 中并排运行），再统一比较、评审、合并结果。Orca 也内置了编辑器能力（拖拽文件、处处自动保存），但它更强调"调度与监控"而非"手写代码"。

### Q9：是否支持中文界面？

**支持国际化。** Orca 基于 **i18next 本地化框架**实现多语言界面，官方已提供简体中文等多个语言包（README 亦附中文版）。本地化框架（i18next）是行业标准方案，可灵活扩展语言与动态切换，中文用户可正常使用。

---

## 7.2 核心术语表

| 术语 | 英语 | 一句话通俗解释 |
|------|------|---------------|
| 工作树 | worktree | git 的"工作副本"，一个分支对应一个独立可读写的工作目录，Orca 用它隔离每个 Agent 的改动 |
| 并行工作树 | parallel worktrees | 把同一个提示同时分发给多个 Agent，各自在互不干扰的独立 worktree 中运行，便于对比结果择优合并 |
| 编排 | orchestration | 像指挥官一样协调多个 Agent 的协作机制，负责消息、任务归属、分发与完成追踪 |
| 运行（Run） | Run | 编排中的"命名空间与收件箱"，承载一次协调会话的持久化上下文，本身不调度执行者 |
| 任务（Task） | Task | 编排中的"工作项"，描述某个 Agent 要干的具体活，可带依赖关系（DAG） |
| 分发（Dispatch） | Dispatch | 把某个 Task 的一次尝试分配给某个 Agent 终端，并注入运行前说明（preamble）的机制 |
| 工作完成上报 | worker_done | Agent 干完活后主动发送给协调者的"完工信号"，需携带成功/失败结果与改动文件列表 |
| 完整交接 | full handoff | 把任务的完全所有权转移给另一个 Agent（不再监控），与"受监督的编排"相对 |
| 决策门 | decision gate | 协调者控制的任务分支决策点，让用户在多个选项间做选择再继续推进 |
| WebGL 终端 | WebGL terminal | 用 GPU 渲染的终端，滚动流畅、支持无限分屏，Orca 用它承载 Agent 的终端会话 |
| Ghostty 级 | Ghostty-class | 达到 Ghostty（高性能现代终端）水准的终端体验——渲染快、分屏多、滚动历史重启后仍保留 |
| 设计模式 | design mode | 在真实 Chromium 窗口中点击任意 UI 元素，把其 HTML/CSS 与裁剪截图直接注入 Agent 提示的工作方式 |
| SSH 工作树 | SSH worktree | 在远程高性能机器上运行 Agent 的工作树，支持完整文件编辑、git 与终端，含自动重连与端口转发 |
| 注释 AI Diff | annotate AI diff | 在 AI 生成的代码差异（diff）行上直接加评论并回传给 Agent，实现不离开 Orca 的评审-编辑-提交闭环 |
| 自动化 | automation | 用 `orca` CLI 把重复工作流脚本化（如 worktree create、snapshot、click、fill），让 Agent 反过来驱动 Orca |
| 计算机使用 | computer use | 让 Agent 操作真实桌面应用与可见 UI，用于需要真实交互的场景 |
| 移动伴侣 | mobile companion | 与桌面端配对的手机 App，用于远程监控 Agent、收通知、发指令 |
| 快速打开 | quick open | 在一个输入框内跨 worktree、文件、Agent、命令与仓库上下文搜索，切换不打断当前流程 |
| 代理 IDE | agent IDE | "AI 编排器"式的 IDE 演进方向——从"代码编辑器"转向"多 Agent 调度与监控中心" |

---

## 7.3 参考资源

| 资源 | 链接 |
|------|------|
| Orca 官网 | https://www.onorca.dev/ |
| 官方文档 | https://www.onorca.dev/docs/mobile 等 |
| GitHub 仓库 | https://github.com/stablyai/orca |
| 下载页 | https://www.onorca.dev/download |
| Discord 社区 | https://discord.gg/fzjDKHxv8Q |
| 隐私与遥测 | https://www.onorca.dev/docs/telemetry |

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [06 核心价值总结与行业趋势](./06-value-and-trends.md) | [README](./README.md) | → 本章为末尾章节 |