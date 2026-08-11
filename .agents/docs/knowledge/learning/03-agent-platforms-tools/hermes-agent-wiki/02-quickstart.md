---
id: "hermes-agent-wiki-02-quickstart"
title: "02 Hermes Agent 快速安装与上手"
source: "NousResearch/hermes-agent 本地源码仓库（README.zh-CN.md / website/docs/getting-started/installation.md / getting-started/quickstart.md / scripts/ 安装脚本）"
type: "Wiki Tutorial"
description: "Hermes Agent 快速上手：安装、初始化、第一个对话、升级的完整可复制命令与预期"
status: "stable"
category: "learning"
tags: ["hermes", "quickstart", "install", "setup", "onboarding"]
date: "2026-08-10"
author: "hermes-agent-wiki knowledge-scenario"
summary: "从安装脚本到首次对话的完整命令流，覆盖 install.sh/install.ps1、hermes setup/model/tools、启动 TUI 与 hermes update"
last_verified: "2026-08-10"
wiki_version: "1.0"
---
# 02 Hermes Agent 快速安装与上手

本章带你从零到可用：安装 → 初始化 → 第一个对话 → 升级。所有命令以源码仓库（README.zh-CN.md、installation.md、quickstart.md）为准；个别不确定处标注"示例/需验证"。

## 2.1 安装 Hermes

### 安装脚本位置

安装脚本位于源码仓库 `scripts/` 目录下：

- `scripts/install.sh` — Linux / macOS / WSL2 / Android（Termux）
- `scripts/install.ps1` — Windows 原生（PowerShell）
- `scripts/install.cmd` — Windows 命令提示符

> 安装程序会**自动处理一切**：Python、Node.js、ripgrep、ffmpeg 等依赖、仓库克隆、虚拟环境、全局 `hermes` 命令、LLM 提供商配置。唯一需要你确保的预备条件是 **git**（Linux 还需 `curl`、`xz-utils`）。

### 一键安装命令（官方 README / installation.md 原文）

**Linux / macOS / WSL2 / Android（Termux）：**
```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

**Windows（PowerShell 中运行）：**
```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

安装完成后，重载 shell 并开始对话：
```bash
source ~/.bashrc   # 或: source ~/.zshrc
hermes             # 开始对话！
```

> **Windows 提示**：安装完成后可能需要重启终端，再运行 `hermes` 开始对话。
> **Termux 提示**：在手机（Termux）上 Hermes 会安装精选的 `.[termux]` 扩展，而非完整的 `.[all]`（后者会拉取 Android 不兼容的语音依赖）。

### 安装目录布局（了解即可）

| 安装方式 | 代码位置 | `hermes` 命令 | 数据目录 |
|---------|---------|--------------|---------|
| 普通用户 | `~/.hermes/hermes-agent/` | `~/.local/bin/hermes`（软链） | `~/.hermes/` |
| root 模式 | `/usr/local/lib/hermes-agent/` | `/usr/local/bin/hermes` | `/root/.hermes/`（或 `$HERMES_HOME`） |

## 2.2 初始化配置

安装完成后需选择模型提供商。最省事、也最推荐的路径是 **Nous Portal**（一个订阅覆盖 300+ 模型 + Tool Gateway，无需逐项收集 API Key）：

```bash
hermes setup --portal     # OAuth 登录、把 Nous 设为提供商、启用 Tool Gateway
```

初始化常用命令：

| 命令 | 作用 |
|------|------|
| `hermes setup` | 完整设置向导，一次性配置所有内容（首次运行启动向导；老用户直接进入重配向导） |
| `hermes model` | 交互式选择 LLM 提供商与模型（在**终端**里运行，可新增提供商、跑 OAuth、填 API Key） |
| `hermes tools` | 配置启用的工具（按平台开关工具集） |
| `hermes config set <key> <value>` | 设置单个配置项 |
| `hermes doctor` | 诊断问题（配置/依赖缺失时运行） |

**模型提供商**：Hermes 支持任意模型——Nous Portal、OpenRouter（200+ 模型）、NVIDIA NIM（Nemotron）、小米 MiMo、z.ai/GLM、Kimi/Moonshot、MiniMax、Hugging Face、OpenAI、DeepSeek，或自定义端点（OpenAI 兼容 API）。用 `hermes model` 即可随时切换，无需改代码、无锁定。

> **⚠️ 最低上下文要求**：模型至少需要 **64,000 tokens** 的上下文窗口，否则无法维持多步工具调用的工作记忆，启动时会被拒绝。本地模型请把上下文设为至少 64K。

### 配置存储位置

- **密钥/令牌** → `~/.hermes/.env`
- **非敏感配置** → `~/.hermes/config.yaml`

```bash
hermes config set model anthropic/claude-opus-4.6
hermes config set terminal.backend docker
# 密钥请写入 ~/.hermes/.env（如 OPENROUTER_API_KEY=...），不要写入 config.yaml（见 04 章）
```

## 2.3 第一个对话

```bash
hermes          # 经典 CLI
hermes --tui    # 现代 TUI（推荐）
```

你将看到欢迎横幅（banner），显示模型、可用工具与技能。建议用一个具体、易验证的 prompt：

```
Summarize this repo in 5 bullets and tell me what the main entrypoint is.
```

**成功的标志**：
- 横幅显示你所选的模型/提供商
- Hermes 无错误回复
- 需要时能调用工具（终端、文件读取、网页搜索）
- 对话能连续多轮进行

> **经验法则**：如果 Hermes 连一次正常对话都无法完成，先别加更多功能。先把一条干净的对话跑通，再叠加网关、cron、技能、语音等。

### 斜杠命令上手

在 CLI 中输入 `/` 会弹出自动补全菜单。常用命令：

| 命令 | 作用 |
|------|------|
| `/help` | 显示所有可用命令 |
| `/model` | 交互式切换模型（仅能在已配置的提供商间切换） |
| `/new`（别名 `/reset`） | 开始新会话 |
| `/skills` | 浏览/安装/管理技能 |
| `/compress` | 手动压缩对话上下文 |
| `/personality pirate` | 试试趣味人格 |
| `/save` | 保存当前对话 |

> **`hermes model` vs `/model` 的差别**：`hermes model` 在终端（会话外）运行，是**完整的提供商设置向导**（可新增提供商、OAuth、填 Key）；`/model` 在会话内运行，**只能**在已配置好的提供商/模型间切换。要新增提供商需先退出会话再跑 `hermes model`。

### 验证会话可续

```bash
hermes --continue    # 恢复最近会话
hermes -c            # 简写
```

## 2.4 升级 Hermes

```bash
hermes update        # 拉取最新代码并重装依赖，然后重跑后置钩子（MCP、技能同步、补全安装）
```

`hermes update` 常用选项：
- `--check`：只检查是否有可用更新，不安装
- `--backup`：拉取前对 `HERMES_HOME` 做完整备份快照
- 成功后会自动重启正在运行的各 profile 网关，以加载新代码

> **安装方式自动检测**：Hermes 会按安装布局自动检测是 git 安装、Docker 还是 NixOS，并打印对应的更新命令。

## 2.5 疑难速查

| 症状 | 排查 |
|------|------|
| `hermes: command not found` | 重载 shell（`source ~/.bashrc`）或检查 PATH |
| `API key not set` | 运行 `hermes model` 配置提供商，或 `hermes config set <KEY> <value>` |
| 更新后配置缺失 | `hermes config check` 再 `hermes config migrate` |
| 界面打开但回复为空/损坏 | 提供商认证或模型选择错误 → 重跑 `hermes model` |
| 网关没人能发消息 | 机器人 token/allowlist 未配好 → 重跑 `hermes gateway setup` 并查 `hermes gateway status` |

诊断兜底顺序：`hermes doctor` → `hermes model` → `hermes setup` → `hermes sessions list` → `hermes --continue` → `hermes gateway status`。

下一步：[03 CLI 与斜杠命令详解](03-cli-commands.md)。
