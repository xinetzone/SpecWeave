---
id: "echobird-wiki-quickstart"
title: "快速上手指南"
source: "echobird-source-wiki-learning"
category: "learning"
tags: ["echobird", "quickstart", "install", "model-nexus", "app-manager"]
date: "2026-08-04"
status: "stable"
author: "seven-concepts knowledge-scenario"
summary: "EchoBird 四步快速上手：安装 EchoBird→安装 Agent→配置模型中心→绑定模型并启动，含可复制命令与易错点提示"
last_verified: "2026-08-04"
wiki_version: "1.0"
---

# 09 快速上手指南

本章面向第一次接触 EchoBird 的用户，用**四步**带你从零把一个 AI Agent 跑起来。全程不需要碰终端、不需要改配置文件、不需要查环境变量——这正是 EchoBird 的核心设计：它把"安装工具、配置模型、切换模型"这些通常要手工折腾的环节，全部收敛到图形界面里，并**直接写入每个工具的原生配置文件**（如 `~/.grok/config.toml`、`~/.kimi-code/config.toml`），让你在模型中心配好一处 provider，任意支持的工具都能一键指向它。

先厘清贯穿本章的两个概念：

- **Agent（智能体）** 是一种能自主调用工具、完成复杂任务的 AI 程序。在 EchoBird 语境下，它指 Claude Code、Codex CLI、OpenClaw、Hermes Agent 等编程命令行工具或桌面应用。
- **模型中心（Model Nexus）** 是 EchoBird 的**统一模型数据中枢**：四个场景共享同一份模型配置，一处配置、四处生效。这是本章"配一次模型、到处使用"的关键。

## 9.1 第一步：安装 EchoBird

EchoBird 支持 Windows、macOS、Linux 三大平台（x64 + arm64），推荐使用**一行命令安装**。安装脚本会自动检测你的操作系统、下载对应的安装包，如果你已经是最新版会自动跳过，无需手动干预。

**Windows（PowerShell）**，在 PowerShell 中直接执行：

```powershell
irm https://echobird.ai/install.ps1 | iex
```

**macOS / Linux**，在终端中直接执行：

```sh
curl -fsSL https://echobird.ai/install.sh | sh
```

> **补充说明**：`irm` 是 PowerShell 的 `Invoke-RestMethod` 简写，`iex` 是 `Invoke-Expression` 简写，整行命令即"下载安装脚本并立即执行"；`curl -fsSL` 表示静默跟随重定向下载脚本。

**手动下载备选**：如果不想用命令行，也可直接下载安装包：

- 最新版本发布页：https://github.com/edison7009/EchoBird/releases/latest

| 平台 | 安装包 |
|------|--------|
| Windows x64 | `EchoBird_<ver>_Windows_x64-setup.exe` |
| macOS（Apple Silicon） | `EchoBird_<ver>_macOS_arm64.dmg` |
| Linux x64 · Debian/Ubuntu | `EchoBird_<ver>_Linux_x64.deb` |
| Linux arm64 · Debian/Ubuntu | `EchoBird_<ver>_Linux_arm64.deb` |
| Linux x64 · Fedora/RHEL | `EchoBird_<ver>_Linux_x64.rpm` |
| Linux arm64 · Fedora/RHEL | `EchoBird_<ver>_Linux_arm64.rpm` |

安装完成后打开 EchoBird，即可看到包含"应用管理""模型中心""安装与修复""本地大模型""我的 AI 项目"等场景的主界面。

## 9.2 第二步：安装一个 Agent

进入**应用管理（App Manager）**页面，这里是 EchoBird 所有 AI / Agent 应用的一键启动与管理入口。页面以卡片网格展示可供选择的工具，顶部有分类页签（`ALL` / `IDE` / `CLI Code` / `AutoTrading` / `Game` / `Desktop` / `Utility` / `Science`），其中：

- **CLI Code / 编程命令行**：Claude Code、Codex CLI（OpenAI）、Grok Build（xAI）、Kimi Code（月之暗面）、Qwen Code、Aider、OpenCode、MiMo Code（小米）、ZCode（Z.AI）、OpenClaw、Pi、OpenScience、Vibe-Trading 等——这些工具**同时支持**一键安装与一键切换模型，是 EchoBird 的核心能力；
- **桌面应用**：Claude Desktop（第三方 profile）、ChatGPT 桌面版、OpenCode Desktop、WorkBuddy（腾讯 CodeBuddy 办公版）等；
- **仅安装与启动**：Hermes Desktop、Claude Science、Trae / Trae CN、Cursor、VS Code、Gemini Desktop、Coffee CLI 等——由 EchoBird 检测、安装、管理，但模型切换由应用自身负责。

选择你实际想用的 Agent 卡片，点击其安装入口即可。安装脚本由 EchoBird 内置，会直接写入该工具的原生配置文件。

> **⚠️ 重要提示**：**不要一次装一堆**。先选一个最常用的 Agent，成功安装并启动之后，再回到这里扩展其他工具。一次只装一个可以让任何问题都能被快速定位——如果一次装了十来个再报错，你很难判断是哪一个环节出了问题。先跑通一个，再逐步铺开，是排障成本最低的路径。

## 9.3 第三步：配置模型中心（Model Nexus）

进入**模型中心（Model Nexus）**页面，添加你的模型服务商。模型中心是 EchoBird 的**统一模型数据中枢**，支持 OpenAI / Anthropic / 本地 LLM / API Router 四类来源，还内置了丰富的一键测速能力，使用前能看清真实延迟。

在右侧的 **Providers / Relays** 面板中，列出了大量预置服务商（DeepSeek、OpenAI、Anthropic、Qwen 千问、Kimi 月之暗面、GLM 智谱、MiniMax、Google Gemini、xAI Grok、火山引擎、腾讯混元、百度千帆、StepFun 阶跃星辰等），以及一批中转/聚合站（OpenRouter、WorldRouter、B.ai、CC Vibe 等）。点击某个服务商行左侧的 **+** 即可自动填充对应的 Base URL 与默认模型 ID，你只需补上 API Key。也可以直接点击"添加模型"卡片手动填写。

添加模型时，需要填写以下字段（对应源码 `src/api/types.ts` 中的 `ModelConfig` 结构）：

| 字段 | 作用 | 易错点 |
|------|------|--------|
| **Name（名称）** | 模型的显示名称，用于在卡片/列表中辨识 | 建议填厂商名，如 `DeepSeek`、`Kimi` 等 |
| **Base URL（Endpoint）** | OpenAI 协议的服务端点地址，如 `https://api.deepseek.com` | 只需填**基底地址**，粘贴完整的 `/v1/chat/completions` 会被自动规整为 base；填错会导致请求 404 |
| **anthropicUrl** | Anthropic 协议端点（可选），仅当厂商原生支持 `/v1/messages` 时填写 | 若厂商不支持 Anthropic 原生协议，留空即可，不要随意填 |
| **Model Name（modelId）** | 模型 ID，如 `deepseek-v4-pro`、`gpt-4o`、`glm-5.2` | 必须与厂商实际提供的模型名完全一致，否则调用报错；若厂商预置了多个 ID，可从下拉快速选择 |
| **Protocol（协议）** | 请求走 OpenAI 还是 Anthropic 协议 | 由你填的是 `baseUrl` 还是 `anthropicUrl` 决定；两者都填时前端会提供 ⇄ 切换器 |
| **API Key** | 服务商提供的密钥，用于鉴权 | 不要在开头/结尾粘贴多余空格；填写后点击右侧锁图标可**加密存储**（保存为 `enc:v1:` 前缀）；本地模型（URL 含 `localhost`/`127.0.0.1`）可自动填 `not-needed` |

> 提示：填写完成后，可点击模型卡片上的"一键测速"（`ping`）验证连通性与延迟，确认无误后再进入下一步。若卡片显示"Error"，说明密钥或地址有误，回到本步修正即可。

## 9.4 第四步：绑定模型到 Agent，然后启动

回到**应用管理**页面，把刚才在模型中心配置好的模型**分配**给 Agent：

1. 点击左侧的 Agent 卡片，选中它；
2. 在右侧面板的**模型列表**中，选择你要绑定的模型（单选，一个工具只绑一个模型）；
3. 勾选底部"应用并启动"复选框（默认已勾选），并确认"通过官方配置写入"的配置策略；
4. 点击底部大按钮 **启动**。

点击后，EchoBird 会先执行 `applyModelConfig`，把模型的 Base URL、API Key、Model ID、协议等价于写入该工具的原生配置文件（如 Claude Code 的 `~/.claude/settings.json`、Codex 的 `~/.codex/config.toml`、Grok Build 的 `~/.grok/config.toml`、Kimi Code 的 `~/.kimi-code/config.toml`），随后 `startTool` 启动对应进程。几秒钟后，你的 AI Agent 即可运行。

> 对于 CLI 类工具，首次启动时会弹出工作目录选择器，请选择你希望 Agent 在其中工作的文件夹；若取消则中止启动。对无需工作目录的工具（如 OpenClaw）则直接启动。

**到此，四步完成，你的 AI Agent 已经跑起来了。** 以后想换模型，只需要回到模型中心改配置，再回到应用管理重新绑定并启动即可，全程不需要碰终端、不需要改配置文件、不需要查环境变量——这正是 EchoBird 相比"手改 TOML / JSON、逐个 CLI 重新登录"的最大价值。

---

| 上一章 | 返回目录 | 下一章 |
|--------|---------|--------|
| ← [08 高级功能模块](./08-advanced-pages.md) | [README](./README.md) | → [10 对比与趋势洞察](./10-comparison-trends.md) |