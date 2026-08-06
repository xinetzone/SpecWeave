---
id: "orca-wiki-agents"
title: "支持的 Agent 清单"
source: "https://www.onorca.dev/ 官网「Supported Agents」+ d:\AI\external\tools\orca\README.md 本地开源源码"
category: "learning"
tags: ["orca", "stablyai", "ai-orchestrator", "agent-ide", "cli-agent", "claude-code", "codex", "opencode", "bring-your-own-agent", "multi-agent"]
date: "2026-08-03"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "Orca 支持任意 CLI Agent 的核心能力：25+ 款官方适配 Agent 清单、归属厂商与一句话说明、自带 Agent / 订阅理念、兼容性边界与排查建议。"
last_verified: "2026-08-03"
wiki_version: "1.0"
orca_version_target: "1.4.165-rc.0"

---

# 04 支持的 Agent 清单

## 核心能力：任意 CLI Agent 均可运行

Orca 的核心能力不在于"预装"某个固定的 Agent，而在于**适配任何 CLI Agent**——只要能在终端里运行，就能在 Orca 里运行。

> **一句话原则**：Orca 不做选择，而是让你决定用哪个 Agent。官方维护了一份覆盖 25+ 款主流 Agent 的适配清单（含每个 Agent 的终端状态识别、生命周期 Hook 事件归一化、会话追踪），同时以"能跑任何 CLI Agent"作为兜底，保证生态的开放性。

这意味着：

- **不必迁移**：你已有的 Claude Code、Codex、OpenCode 等工作流可以原样保留，Orca 负责把它们组织进并行 worktree 编排。
- **自由组合**：同一个任务可以同时分发给不同类型的 Agent，比较不同模型的输出，择优合并。
- **持续演进**：Agent 生态每天都有新工具出现，Orca 的"任意 CLI Agent"兜底能力让新工具无需等待官方适配即可接入。

## 官方适配 Agent 清单

以下清单基于 Orca 官方 README「Supported Agents」章节整理，覆盖主流厂商与开源社区的代表性 CLI Agent。

| Agent 名称 | 归属厂商 | 一句话说明 |
|-----------|---------|-----------|
| Claude Code | Anthropic | 官方 CLI 编程 Agent，以终端内交互式编程与长任务执行为核心能力 |
| Codex | OpenAI | OpenAI 的命令行编程 Agent，支持在终端中执行代码与多步任务 |
| Grok | xAI | xAI 推出的 CLI 编程 Agent，面向终端场景的智能助手 |
| Cursor | Anysphere | Cursor 编辑器的 CLI 版本，将编辑器能力下沉到终端使用 |
| GitHub Copilot | GitHub / Microsoft | 命令行版编程助手，与 GitHub 生态深度集成 |
| OpenCode | SST | 开源终端编程 Agent，支持 BYOK（自带模型密钥）的多模型接入 |
| MiMo Code | 小米 | 小米出品的开源编程 Agent，兼容 OpenCode 生命周期事件 |
| Amp | Ampcode | 轻量级终端编程 Agent，主打快速上手与低配置 |
| OpenClaude | Gitlawb | 开源实现的 Claude Code 兼容终端 Agent |
| Antigravity | Google | Google 的 CLI 编程 Agent，与 Gemini 模型生态联动 |
| Pi | Pi.dev | 终端编程 Agent，主打简洁的交互式编辑体验 |
| oh-my-pi | Pi | Pi 的增强版配置/脚本发行版，提供更丰富的开箱即用功能 |
| Hermes Agent | Nous Research | 基于开源模型的终端 Agent，强调可本地化部署 |
| Devin | Cognition | Autonomy 代表型 Agent，支持长期任务自主推进 |
| Goose | Block | 开源可扩展的终端 Agent，支持 MCP 与本地化模型接入 |
| Auggie | Augment | Augment 的 CLI Agent，面向企业级代码生成 |
| Autohand Code | Autohand | 开源编程 Agent，可自定义工作流与工具链 |
| Charm | Charmbracelet | 终端生态厂商推出的编程 Agent，主打 CLI 美学与效率 |
| Cline | Cline | 开源 VS Code 扩展同源的 CLI Agent，支持多模型 |
| Codebuff | Codebuff | 面向快速原型的终端编程 Agent |
| Command Code | Command Code | 面向命令行命令生成的编程 Agent |
| Continue | Continue | 开源 AI 编程助手，提供 CLI 版本并支持本地模型 |
| Droid | Factory | 工厂出品的终端 Agent，面向自动化任务调度 |
| Kilocode | Kilo | 开源编程 Agent，支持多模型与多语言 |
| Kimi | Moonshot | 月之暗面的 Kimi 编程 CLI Agent，面向中文场景优化 |
| Kiro | Kiro.dev | 轻量级终端编程 Agent，强调个人工作流定制 |
| Mistral Vibe | Mistral | 开源灵感式编程 Agent，可与 Mistral 模型联动 |
| Qwen Code | 阿里 / Qwen | 通义千问团队的终端编程 Agent，支持中文生态与多模型 |
| Rovo Dev | Atlassian | Atlassian 的 Rovo 开发 Agent CLI，面向企业协同开发 |

> 上表共收录 **29 款**官方适配 Agent。清单末尾还有一句"**+ any CLI agent**"（+ 任何 CLI Agent），代表 Orca 以"能跑任何 CLI Agent"为兜底承诺，不局限于上表。

## 自带 Agent / 订阅（Bring your own Agent / Subscription）

Orca 奉行 **"自带 Agent / 自带订阅"**（Bring your own Agent / Subscription）理念，这也是它区别于"全家桶式" IDE 的差异化定位：

- **自带 Agent**：Orca 不锁定你到某一款 Agent，而是让你自由选择并自带你信任的工具。你已有的 Agent 配置、登录态、模型偏好全部保留，Orca 只负责编排与调度。
- **自带订阅**：Agent 的模型用量、额度与订阅均由你自己的账号承担。Orca 提供**账号切换与用量追踪**能力，可查看 Claude、Codex 等 Agent 的用量与限额重置时间，并支持无需重新登录的热切换账号，方便你管理多账号与多订阅边界。
- **零迁移成本**：因为用你自己的 Agent 与订阅，切换工具或同时使用多个 Agent 都不会产生新的绑定关系，也无需把会话数据迁移到某个固定平台。

> 该理念的延伸价值在于：你可以把"最强的模型"与"最顺手的工具"自由组合，并让它们在 Orca 的并行 worktree 中协同工作，从而最大化多 Agent 协作的收益。

## 兼容性边界与排查建议

- **识别依赖终端状态**：Orca 通过识别 Agent 的终端标题与生命周期事件（如准备好的 `idle`、工作中的 `working`、完成的 `done`）来跟踪会话状态。社区/开源 Agent（如 MiMo Code 兼容 OpenCode 事件）一般可被自动识别。
- **未适配的 Agent 也能跑**：对于不在官方清单内的 Agent，Orca 仍可通过"任意 CLI Agent"兜底能力运行，只是可能缺少精细的状态识别与事件归一化。
- **排查建议**：若某 Agent 状态显示异常，优先确认其 CLI 版本是否过新/过旧、是否在终端中可正常启动、以及是否为官方已适配的版本；必要时参考 Orca 更新日志与 GitHub Releases 确认最新适配情况。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [03 Orca CLI 与多 Agent 编排](./03-orca-cli-orchestration.md) | [README](./README.md) | → [05 快速上手指南](./05-quickstart.md) |