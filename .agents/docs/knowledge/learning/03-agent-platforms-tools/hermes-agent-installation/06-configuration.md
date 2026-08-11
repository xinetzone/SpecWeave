---
title: "Hermes Agent 安装方案 - 配置说明"
chapter: 6
source:
  - external/libs/hermes-agent/.env.example
  - external/libs/hermes-agent/cli-config.yaml.example
  - external/libs/hermes-agent/hermes_cli/setup.py
  - external/libs/hermes-agent/hermes_cli/models.py
  - external/libs/hermes-agent/hermes_cli/config.py
  - external/libs/hermes-agent/hermes_cli/config_defaults.py
  - external/libs/hermes-agent/hermes_cli/auth.py
  - external/libs/hermes-agent/hermes_cli/subcommands/tools.py
  - external/libs/hermes-agent/.gitignore
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/docker/stage2-hook.sh
---

# 6. 配置说明

本章详细说明 Hermes Agent 的配置体系，包括 `.env` 环境变量文件、`config.yaml` 行为配置文件、交互式配置向导、模型与工具管理命令，以及终端后端选择。所有配置文件均存放于 `~/.hermes/` 目录下。

> Hermes Agent 采用**密钥与行为分离**的配置策略：`.env` 文件存储 API Key 等敏感信息，`config.yaml` 存储模型选择、工具开关、终端后端等非敏感行为配置。两者协同工作，互不替代。

---

## 6.1 .env 文件

### 6.1.1 文件作用

`.env` 文件用于存储所有敏感凭据，包括：

- LLM 提供商的 API Key（如 `OPENROUTER_API_KEY`、`ANTHROPIC_API_KEY`）
- 工具服务的 API Key（如 `EXA_API_KEY`、`FIRECRAWL_API_KEY`）
- 远程服务的连接凭据（如 SSH 密钥路径、Modal Token）
- 平台集成 Token（如 Slack Bot Token、Telegram Bot Token）

该文件遵循 dotenv 格式，每行一个 `KEY=VALUE` 键值对，以 `#` 开头的行为注释。Hermes Agent 启动时自动加载 `~/.hermes/.env`，无需手动 `source`。

### 6.1.2 创建方法

安装脚本会自动从模板创建 `.env` 文件。如需手动创建，在 Hermes 数据目录下执行：

```bash
# 进入 Hermes 配置目录
cd ~/.hermes

# 从模板复制
cp .env.example .env

# 设置文件权限（仅所有者可读写）
chmod 600 .env
```

Windows（PowerShell）环境：

```powershell
# 进入 Hermes 配置目录
cd $env:USERPROFILE\.hermes

# 从模板复制
Copy-Item .env.example .env
```

> **注意**：安装脚本（`install.sh`、`setup-hermes.sh`）和 Docker 初始化钩子（`stage2-hook.sh`）在创建 `.env` 后会自动执行 `chmod 600 .env`，确保文件权限安全。手动复制时也应执行此操作。

### 6.1.3 配置文件位置

| 文件 | 路径 | 用途 |
|---|---|---|
| `.env` | `~/.hermes/.env` | 活跃的密钥配置（不提交版本控制） |
| `.env.example` | 安装目录下 | 模板文件，列出所有支持的环境变量 |
| `config.yaml` | `~/.hermes/config.yaml` | 行为配置文件 |

可通过以下命令快速查看配置文件位置：

```bash
hermes config
```

---

## 6.2 LLM 提供商配置

Hermes Agent 支持多家 LLM 提供商。你只需配置**至少一家**提供商的 API Key 即可开始使用。推荐新手使用 OpenRouter（一个 Key 访问数百种模型）或 Nous Portal OAuth（免费登录，无需 API Key）。

### 6.2.1 主流提供商一览

| 提供商 | 环境变量 | 获取地址 | 说明 |
|---|---|---|---|
| **OpenRouter** | `OPENROUTER_API_KEY` | <https://openrouter.ai/keys> | 聚合平台，一个 Key 访问 GPT、Claude、Gemini 等数百种模型 |
| **Fireworks AI** | `FIREWORKS_API_KEY` | <https://app.fireworks.ai/settings/users/api-keys> | 高速推理平台，支持 Kimi、GLM 等模型直连 |
| **OpenAI** | `OPENAI_API_KEY` | <https://platform.openai.com/api-keys> | 直连 OpenAI API（GPT-4o、GPT-5 等） |
| **Google/Gemini** | `GOOGLE_API_KEY` 或 `GEMINI_API_KEY` | <https://aistudio.google.com/app/apikey> | Google AI Studio 原生 Gemini API |
| **Anthropic** | `ANTHROPIC_API_KEY` | <https://console.anthropic.com/> | 直连 Anthropic Claude API |
| **Kimi/Moonshot** | `KIMI_API_KEY` | <https://platform.kimi.ai> | Moonshot AI 编程模型（Kimi K2/K3 系列） |
| **DeepInfra** | `DEEPINFRA_API_KEY` | <https://deepinfra.com/dash/api_keys> | 100+ 开源模型，按用量付费 |
| **z.ai/GLM** | `GLM_API_KEY` | <https://z.ai> 或 <https://open.bigmodel.cn> | 智谱 AI GLM 模型 |
| **NovitaAI** | `NOVITA_API_KEY` | <https://novita.ai/settings/key-management> | 90+ 模型，按用量付费 |
| **MiniMax** | `MINIMAX_API_KEY` | <https://www.minimax.io> | MiniMax 国际版 |
| **MiniMax 中国版** | `MINIMAX_CN_API_KEY` | <https://www.minimaxi.com> | MiniMax 国内端点 |
| **Hugging Face** | `HF_TOKEN` | <https://huggingface.co/settings/tokens> | HF Inference Providers，需勾选 "Make calls to Inference Providers" 权限 |
| **Ollama Cloud** | `OLLAMA_API_KEY` | <https://ollama.com/settings> | Ollama 云端开源模型 |
| **xAI/Grok** | `XAI_API_KEY` | <https://console.x.ai/> | xAI Grok 模型 |
| **Xiaomi MiMo** | `XIAOMI_API_KEY` | <https://platform.xiaomimimo.com> | 小米 MiMo 模型 |
| **Upstage** | `UPSTAGE_API_KEY` | <https://console.upstage.ai/api-keys> | Upstage Solar 模型 |
| **Arcee AI** | `ARCEEAI_API_KEY` | <https://chat.arcee.ai/> | Arcee Trinity 模型 |
| **NVIDIA NIM** | `NVIDIA_API_KEY` | <https://build.nvidia.com/> | NVIDIA NIM 推理服务 |

### 6.2.2 各提供商配置详解

#### OpenRouter（推荐新手）

OpenRouter 是最简便的选择——一个 API Key 即可访问所有主流模型：

```bash
# .env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

默认模型在 `config.yaml` 的 `model.default` 中配置，默认为 `anthropic/claude-opus-4.6`。可通过 `hermes model` 命令切换。

可选的 Base URL 覆盖（一般不需要修改）：

```bash
# config.yaml
model:
  provider: "openrouter"
  base_url: "https://openrouter.ai/api/v1"
```

#### Fireworks AI

Fireworks 提供高速推理，可直接按目录 ID 寻址模型：

```bash
# .env
FIREWORKS_API_KEY=fw_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

模型寻址示例：`accounts/fireworks/models/kimi-k2p6`、`accounts/fireworks/models/glm-5p2`。

#### Google/Gemini

通过 Google 的 OpenAI 兼容端点访问 Gemini：

```bash
# .env
GOOGLE_API_KEY=AIzaSyxxxxxxxxxxxxxxxxxxxxxxxxxxx
# GEMINI_API_KEY 是 GOOGLE_API_KEY 的别名，二者选一即可
```

可选的 Base URL 覆盖：

```bash
# GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai
```

#### Anthropic

直连 Anthropic 原生 API：

```bash
# .env
ANTHROPIC_API_KEY=sk-ant-api03-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

也支持 `ANTHROPIC_TOKEN` 和 `CLAUDE_CODE_OAUTH_TOKEN` 作为备选环境变量名。

#### Kimi/Moonshot

Kimi Code 提供 Moonshot AI 编程模型：

```bash
# .env
KIMI_API_KEY=sk-kimi-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

- 以 `sk-kimi-` 开头的 Key 默认使用 Kimi Code API（`https://api.kimi.com/coding/v1`）
- 旧版 Moonshot Key 需覆盖 Base URL：

```bash
# 旧版 Moonshot 国际版
KIMI_BASE_URL=https://api.moonshot.ai/v1

# Moonshot 中国版
KIMI_CN_API_KEY=your_moonshot_cn_key
KIMI_BASE_URL=https://api.moonshot.cn/v1
```

#### DeepInfra

```bash
# .env
DEEPINFRA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 可选：覆盖默认 Base URL
# DEEPINFRA_BASE_URL=https://api.deepinfra.com/v1/openai
```

#### NovitaAI

```bash
# .env
NOVITA_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
# 可选：覆盖默认 Base URL
# NOVITA_BASE_URL=https://api.novita.ai/openai/v1
```

### 6.2.3 本地/自托管模型

Hermes Agent 也支持本地运行的模型服务，通过 OpenAI 兼容端点接入：

```bash
# .env — 指向本地 LM Studio / Ollama / vLLM / llama.cpp
OPENAI_BASE_URL=http://127.0.0.1:1234/v1
OPENAI_API_KEY=not-needed-for-local
```

在 `config.yaml` 中设置 provider 为 `custom`（或别名 `ollama`、`vllm`、`llamacpp`）：

```yaml
model:
  provider: "custom"
  base_url: "http://127.0.0.1:1234/v1"
  default: "your-model-name"
```

LM Studio 有一等公民支持，使用 `provider: "lmstudio"`，默认端点 `http://127.0.0.1:1234/v1`。

---

## 6.3 工具 API Key 配置

除 LLM 提供商外，Hermes Agent 的各类工具（网页搜索、浏览器自动化、图像生成等）也需要相应的 API Key。以下列出主要工具的配置方式。**这些 Key 均为可选**——不配置时对应工具不可用，但不影响核心对话功能。

### 6.3.1 工具 Key 一览表

| 工具 | 环境变量 | 获取地址 | 启用的工具 |
|---|---|---|---|
| **Exa** | `EXA_API_KEY` | <https://exa.ai/> | AI 原生网页搜索与内容提取 |
| **Parallel** | `PARALLEL_API_KEY` | <https://parallel.ai/> | AI 原生网页搜索与提取 |
| **Firecrawl** | `FIRECRAWL_API_KEY` | <https://firecrawl.dev/> | 网页搜索、抓取与爬取 |
| **Tavily** | `TAVILY_API_KEY` | <https://app.tavily.com/home> | AI 原生网页搜索与提取 |
| **Browserbase** | `BROWSERBASE_API_KEY` | <https://browserbase.com/> | 云端浏览器自动化 |
| **FAL.ai** | `FAL_KEY` | <https://fal.ai/> | 图像与视频生成 |
| **GitHub Token** | `GITHUB_TOKEN` | <https://github.com/settings/tokens> | Skills Hub 搜索/安装/发布（提升 API 速率限制） |
| **Browser Use** | `BROWSER_USE_API_KEY` | （Browser Use 服务） | 浏览器自动化备选后端 |
| **Honcho** | `HONCHO_API_KEY` | <https://app.honcho.dev> | 跨会话用户建模（可选） |
| **Groq** | `GROQ_API_KEY` | <https://console.groq.com/> | Whisper 语音转文字（免费额度） |
| **ElevenLabs** | `ELEVENLABS_API_KEY` | <https://elevenlabs.io/> | 云端语音识别与合成 |
| **OpenAI Voice** | `VOICE_TOOLS_OPENAI_KEY` | <https://platform.openai.com/api-keys> | Whisper 转录与 OpenAI TTS 语音 |

### 6.3.2 网页搜索工具

Hermes Agent 支持多家网页搜索提供商，配置**任意一家**即可启用网页搜索功能：

```bash
# .env — 三选一（或多家并存，Hermes 自动选择可用项）

# Exa（推荐）
EXA_API_KEY=exa-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Parallel
PARALLEL_API_KEY=par-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Firecrawl
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Tavily
TAVILY_API_KEY=tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 6.3.3 浏览器自动化

浏览器工具支持多种后端：

```bash
# .env — Browserbase 云端浏览器
BROWSERBASE_API_KEY=bb-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
BROWSERBASE_PROJECT_ID=your-project-id-here

# 可选：住宅代理（默认开启，提升验证码成功率）
BROWSERBASE_PROXIES=true

# 可选：高级隐身模式（需 Scale 套餐）
BROWSERBASE_ADVANCED_STEALTH=false
```

不配置 Browserbase 也可使用本地浏览器（需安装 `agent-browser`）：

```bash
npm install -g agent-browser
agent-browser install --with-deps
```

或使用 Camofox 本地反检测浏览器：

```bash
# .env
CAMOFOX_URL=http://localhost:9377
```

### 6.3.4 图像生成

```bash
# .env — FAL.ai
FAL_KEY=your-fal-key-here
```

图像生成也可通过 Nous 订阅托管，无需配置 FAL Key。

### 6.3.5 GitHub Token（Skills Hub）

```bash
# .env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

创建 Token 时建议使用 **Fine-grained token**，仅授予必要的仓库权限。此 Token 用于 Skills Hub 的搜索、安装和发布功能，可显著提升 GitHub API 速率限制。

---

## 6.4 config.yaml 与 .env 的区别

Hermes Agent 的配置系统严格区分**密钥**与**行为**两类配置：

### 6.4.1 职责划分

| 维度 | `.env` | `config.yaml` |
|---|---|---|
| **存储内容** | API Key、密码、Token 等敏感凭据 | 模型选择、工具开关、终端后端、压缩策略等行为设置 |
| **文件格式** | dotenv（`KEY=VALUE`） | YAML |
| **文件路径** | `~/.hermes/.env` | `~/.hermes/config.yaml` |
| **版本控制** | **绝不提交**（已在 `.gitignore` 中排除） | 可提交（不含密钥） |
| **文件权限** | `0600`（仅所有者可读写） | `0644`（默认） |
| **修改方式** | 文本编辑器 / `hermes config set KEY VALUE` | 文本编辑器 / `hermes config set section.key value` / `hermes setup` |
| **敏感性** | 高 | 低 |

### 6.4.2 config.yaml 主要配置段

`config.yaml` 使用 YAML 层级结构，主要配置段包括：

```yaml
# ~/.hermes/config.yaml — 结构概览

model:                    # 模型配置
  default: "anthropic/claude-opus-4.6"  # 默认模型
  provider: "auto"        # 推理提供商：auto/openrouter/anthropic/gemini/...
  base_url: "https://openrouter.ai/api/v1"

terminal:                 # 终端工具配置
  backend: "local"        # 后端：local/docker/ssh/modal/singularity/daytona/vercel_sandbox
  cwd: "."                # 工作目录
  timeout: 180            # 命令超时（秒）
  container_cpu: 1        # 容器 CPU 核数
  container_memory: 5120  # 容器内存（MB）
  container_persistent: true  # 容器文件系统是否持久化

compression:              # 上下文压缩配置
  enabled: true
  threshold: 0.50         # 在上下文 50% 时触发压缩
  target_ratio: 0.20      # 保留 20% 的最近对话

agent:                    # Agent 行为配置
  max_turns: 500          # 最大工具调用轮次
  reasoning_effort: "medium"  # 推理强度：none/minimal/low/medium/high/xhigh/max

browser:                  # 浏览器工具配置
  inactivity_timeout: 120

skills:                   # 技能配置
  creation_nudge_interval: 15

platform_toolsets:        # 各平台工具集配置
  cli: [hermes-cli]
  telegram: [hermes-telegram]
```

### 6.4.3 配置修改方式

**方式一：命令行设置**

```bash
# 设置 config.yaml 中的值
hermes config set model.provider openrouter
hermes config set terminal.backend docker
hermes config set agent.max_turns 100

# 设置 .env 中的密钥（不含点号的键名自动路由到 .env）
hermes config set OPENROUTER_API_KEY sk-or-v1-xxxxx

# 查看当前配置
hermes config get model.provider
hermes config

# 删除配置项
hermes config unset agent.reasoning_effort
```

**方式二：编辑器直接编辑**

```bash
hermes config edit
```

**方式三：交互式向导**

```bash
hermes setup
```

### 6.4.4 环境变量黑名单

出于安全考虑，Hermes Agent 禁止通过 `hermes config set` 写入以下危险环境变量（防止子进程注入攻击）：

- 动态链接器变量：`LD_PRELOAD`、`LD_LIBRARY_PATH`、`DYLD_INSERT_LIBRARIES` 等
- Python 变量：`PYTHONPATH`、`PYTHONHOME`、`PYTHONSTARTUP` 等
- Node 变量：`NODE_OPTIONS`、`NODE_PATH`
- 通用变量：`PATH`、`SHELL`、`EDITOR`
- Hermes 运行时位置：`HERMES_HOME`、`HERMES_PROFILE`、`HERMES_CONFIG`、`HERMES_ENV`

如需设置这些变量，必须手动编辑 `~/.hermes/.env` 文件。

---

## 6.5 hermes setup 交互式配置向导

`hermes setup` 是 Hermes Agent 的全功能交互式配置向导，通过方向键导航的菜单引导你完成所有配置。

### 6.5.1 启动方式

```bash
# 完整配置向导
hermes setup

# 仅配置模型和提供商
hermes setup model

# 仅配置终端后端
hermes setup terminal

# 仅配置消息平台（Telegram/Discord/Slack 等）
hermes setup gateway

# 仅配置工具
hermes setup tools

# 仅配置 Agent 设置
hermes setup agent

# 仅配置语音（TTS）
hermes setup tts

# 仅配置遥测
hermes setup telemetry

# Nous Portal 一键设置（OAuth 登录，无需 API Key）
hermes setup --portal

# 快速模式（仅填充缺失项）
hermes setup --quick

# 重置为默认配置
hermes setup --reset
```

### 6.5.2 向导配置区段

完整向导按以下顺序执行（参见 `hermes_cli/setup.py` 中的 `SETUP_SECTIONS`）：

| 区段 | 命令 | 配置内容 |
|---|---|---|
| **Model & Provider** | `hermes setup model` | 选择 LLM 提供商、模型、输入 API Key、配置推理强度 |
| **Text-to-Speech** | `hermes setup tts` | 配置 TTS 语音提供商和声音 |
| **Terminal Backend** | `hermes setup terminal` | 选择命令执行环境（local/docker/ssh/modal 等） |
| **Messaging Platforms** | `hermes setup gateway` | 配置 Telegram、Discord、Slack、WhatsApp 等消息平台 |
| **Tools** | `hermes setup tools` | 配置网页搜索、浏览器、图像生成等工具 |
| **Shared Metrics** | `hermes setup telemetry` | 本地共享指标配置 |
| **Agent Settings** | `hermes setup agent` | 最大轮次、压缩策略、会话重置等 |

### 6.5.3 首次安装流程

首次运行 `hermes setup` 时，向导提供三种设置模式：

1. **Quick Setup (Nous Portal)** — 推荐。通过 OAuth 登录 Nous Portal，免费使用，无需 API Key。自动配置模型和工具。
2. **Full setup** — 完整配置。自行配置每个提供商、工具和选项（需自备 API Key）。
3. **Blank Slate** — 空白模式。仅启用最低限度功能，逐项手动开启所需能力。

### 6.5.4 已有安装的重配置

对于已配置的安装，`hermes setup` 默认进入**全量重配置**模式。每个提示项显示当前值作为默认值，直接按 Enter 保持不变。也可使用 `--quick` 仅填充缺失项。

向导开始前会自动备份现有 `config.yaml` 为带时间戳的 `.bak` 文件，防止配置丢失。

### 6.5.5 非交互环境

在无 TTY 的环境（CI/CD、Docker、headless SSH）中，`hermes setup` 会自动检测并输出非交互配置指引，提示使用以下方式配置：

```bash
hermes config set model.provider custom
hermes config set model.base_url http://localhost:8080/v1
hermes config set model.default your-model-name
```

或设置环境变量 `HERMES_NONINTERACTIVE=1` 显式声明非交互模式。

---

## 6.6 hermes model 模型选择命令

`hermes model` 命令提供交互式模型选择界面，用于切换 LLM 提供商和默认模型。

### 6.6.1 基本用法

```bash
# 启动交互式模型选择器
hermes model
```

该命令会：
1. 显示当前配置的提供商和模型
2. 引导选择提供商（方向键导航）
3. 从提供商的 `/v1/models` 端点拉取可用模型列表（网络不可用时使用内置回退列表）
4. 设置选定的模型为默认模型（写入 `config.yaml` 的 `model.default`）

### 6.6.2 刷新模型缓存

```bash
# 清除模型选择器缓存，强制重新拉取模型列表
hermes model --refresh
```

模型列表会缓存到本地，当提供商发布新模型时使用此命令刷新。

### 6.6.3 直接通过 config 命令设置

也可不经过交互式界面，直接设置模型：

```bash
# 设置提供商和模型
hermes config set model.provider openrouter
hermes config set model.default anthropic/claude-sonnet-5

# 单次调用指定模型（不修改默认配置）
hermes --model openai/gpt-5.4 "你好"

# 单次调用指定提供商
hermes --provider anthropic "你好"
```

### 6.6.4 内置模型回退列表

当网络不可用无法拉取实时模型列表时，Hermes Agent 内置了各提供商的常用模型回退列表（定义于 `hermes_cli/setup.py` 的 `_DEFAULT_PROVIDER_MODELS`），包括：

- **Gemini**: gemini-3.1-pro-preview、gemini-3.6-flash 等
- **z.ai/GLM**: glm-5.2、glm-5.1、glm-5、glm-4.7 等
- **Kimi**: kimi-k3、kimi-k2.6、kimi-k2.5 等
- **MiniMax**: MiniMax-M2.7、MiniMax-M2.5、MiniMax-M2 等
- **OpenRouter**: claude-opus-5、gpt-5.6、gemini-3.1-pro、kimi-k3、glm-5.2 等（含免费模型）

---

## 6.7 hermes tools 工具配置命令

`hermes tools` 命令用于管理各平台上启用/禁用的工具集。

### 6.7.1 交互式配置

```bash
# 不带子命令时启动交互式工具配置界面
hermes tools
```

### 6.7.2 命令行子命令

```bash
# 列出所有工具及其启用状态（默认 CLI 平台）
hermes tools list
hermes tools list --platform telegram

# 启用工具
hermes tools enable web
hermes tools enable browser --platform cli
hermes tools enable web terminal file memory

# 禁用工具
hermes tools disable image
hermes tools disable browser --platform telegram

# 查看启用工具摘要
hermes tools --summary
```

### 6.7.3 工具集名称

内置工具集使用纯名称标识：

| 工具集 | 功能 |
|---|---|
| `web` | 网页搜索与内容提取 |
| `terminal` | 终端命令执行 |
| `file` | 文件读写操作 |
| `browser` | 浏览器自动化 |
| `image` | 图像生成 |
| `memory` | 持久化记忆 |
| `skills` | 技能系统 |
| `todo` | 任务规划 |
| `tts` | 语音合成 |
| `cronjob` | 定时任务 |

MCP 工具使用 `server:tool` 格式（如 `github:create_issue`）。

### 6.7.4 平台指定

`--platform` 参数支持以下平台：

- `cli` — 命令行界面（默认）
- `telegram` — Telegram
- `discord` — Discord
- `slack` — Slack
- `whatsapp` — WhatsApp
- `qqbot` — QQ 机器人
- `teams` — Microsoft Teams
- `google_chat` — Google Chat

可使用预设组合（如 `hermes-cli`、`hermes-telegram`）或自定义工具集列表。

### 6.7.5 工具后端安装钩子

某些工具后端需要额外的依赖安装步骤：

```bash
# 运行工具后端的安装/引导钩子
hermes tools post-setup agent_browser   # 安装 agent-browser
hermes tools post-setup camofox         # 安装 Camofox
hermes tools post-setup kittentts       # 安装 KittenTTS
hermes tools post-setup piper           # 安装 Piper TTS
hermes tools post-setup ddgs            # 安装 DuckDuckGo 搜索
hermes tools post-setup spotify         # Spotify 集成
hermes tools post-setup langfuse        # Langfuse 可观测性
hermes tools post-setup xai_grok        # xAI Grok 设置
```

---

## 6.8 终端后端配置

终端工具决定 Hermes Agent 在何处执行 shell 命令和代码。通过 `hermes setup terminal` 或直接编辑 `config.yaml` 的 `terminal` 段进行配置。

### 6.8.1 支持的后端

| 后端 | config.yaml 值 | 说明 | 适用场景 |
|---|---|---|---|
| **Local** | `local` | 直接在本机执行命令（默认） | 开发机、个人使用 |
| **Docker** | `docker` | 在隔离的 Docker 容器中执行 | 可复现环境、安全隔离 |
| **SSH** | `ssh` | 在远程服务器上通过 SSH 执行 | 远程硬件、代码沙箱隔离 |
| **Modal** | `modal` | Modal 云端无服务器沙箱 | GPU 访问、弹性计算 |
| **Daytona** | `daytona` | Daytona 持久化云开发环境 | 团队协作、持久化工作区 |
| **Vercel Sandbox** | `vercel_sandbox` | Vercel 云端 microVM | 快照文件系统持久化 |
| **Singularity** | `singularity` | Singularity/Apptainer 容器 | HPC 集群、共享计算环境（仅 Linux） |

### 6.8.2 Local 后端（默认）

```yaml
terminal:
  backend: "local"
  cwd: "."              # CLI 模式下为当前目录；Gateway 模式下默认为用户主目录
  timeout: 180
  home_mode: "auto"     # auto: 主机用真实 HOME，容器用 HERMES_HOME/home
```

### 6.8.3 Docker 后端

```yaml
terminal:
  backend: "docker"
  cwd: "/workspace"     # 容器内路径
  timeout: 180
  docker_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  docker_mount_cwd_to_workspace: true  # 将主机当前目录挂载到容器 /workspace
  docker_run_as_host_user: true        # 以主机用户身份运行（避免 root 写文件）
  container_cpu: 1
  container_memory: 5120    # 5 GB
  container_disk: 51200     # 50 GB
  container_persistent: true
  # 可选：传递环境变量到容器
  docker_forward_env:
    - "GITHUB_TOKEN"
    - "NPM_TOKEN"
  # 可选：额外的 docker run 参数
  docker_extra_args:
    - "--cap-add"
    - "SETUID"
```

Docker 后端还支持出口凭证防火墙（Egress Credential Firewall），通过 iron-proxy 路由容器流量，使容器内只看到代理 Token 而非真实 API Key。可在 `hermes setup terminal` 中启用。

可通过 `HERMES_DOCKER_BINARY` 环境变量指定容器运行时（如使用 Podman 替代 Docker）：

```bash
HERMES_DOCKER_BINARY=/usr/local/bin/podman
```

### 6.8.4 SSH 后端

SSH 后端将命令发送到远程服务器执行，Agent 代码保留在本地。这提供了额外的安全隔离——Agent 无法读取本地的 `.env` 文件，也无法修改自身代码。

```yaml
terminal:
  backend: "ssh"
  cwd: "/home/myuser/project"  # 远程服务器上的路径
  timeout: 180
  ssh_host: "my-server.example.com"
  ssh_user: "myuser"
  ssh_port: 22
  ssh_key: "~/.ssh/id_rsa"     # 可选，不指定则使用 ssh-agent
```

安全优势：
- Agent 无法读取本地 `.env` 文件（API Key 受保护）
- Agent 无法修改自身代码
- 远程服务器充当隔离沙箱
- 可在远程安全配置免密 sudo

### 6.8.5 Modal 后端

Modal 提供无服务器云端沙箱，每个会话获得独立容器：

```yaml
terminal:
  backend: "modal"
  cwd: "/workspace"
  timeout: 180
  modal_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  modal_mode: "direct"   # "direct": 用自己的 Modal 账户；"managed": 使用 Nous 订阅
```

使用自己的 Modal 账户需先安装 SDK 并认证：

```bash
pip install modal
modal setup
```

Modal 通过 CLI 认证（浏览器跳转），凭据存储在本地，无需在 `.env` 中配置 API Key。也可手动配置 Token：

```bash
MODAL_TOKEN_ID=your-token-id
MODAL_TOKEN_SECRET=your-token-secret
```

### 6.8.6 Daytona 后端

```yaml
terminal:
  backend: "daytona"
  cwd: "~"
  daytona_image: "nikolaik/python-nodejs:python3.11-nodejs20"
  container_disk: 10240   # Daytona 每个沙箱最大 10 GB
```

需要安装 Daytona SDK 并配置 `DAYTONA_API_KEY`：

```bash
pip install daytona
```

### 6.8.7 Singularity/Apptainer 后端（仅 Linux）

```yaml
terminal:
  backend: "singularity"
  cwd: "/workspace"
  timeout: 180
  singularity_image: "docker://nikolaik/python-nodejs:python3.11-nodejs20"
```

适用于 HPC 集群环境，使用 Apptainer/Singularity 运行时。

### 6.8.8 通用容器资源配置

以下资源配置适用于所有容器后端（docker、singularity、modal、daytona），local 和 ssh 后端忽略这些设置：

```yaml
terminal:
  container_cpu: 1              # CPU 核数
  container_memory: 5120        # 内存（MB），5120 = 5 GB
  container_disk: 51200         # 磁盘（MB），51200 = 50 GB
  container_persistent: true    # 文件系统跨会话持久化（false = 临时）
  lifetime_seconds: 300         # 非活动环境清理时间（秒）
```

### 6.8.9 Sudo 支持

所有后端均支持 sudo 命令。在 `terminal` 段配置 `sudo_password`：

```yaml
terminal:
  sudo_password: "your-password"  # 通过 sudo -S 传递密码
```

> **安全警告**：密码以明文存储。推荐的替代方案：
> - SSH 后端：在远程服务器配置免密 sudo
> - 容器后端：在容器内以 root 运行（无需 sudo）
> - Local 后端：在 `/etc/sudoers` 中为特定命令配置免密
>
> 若不设置 `sudo_password`，CLI 模式下会交互式提示输入密码（45 秒超时，输入隐藏，会话内缓存）。

### 6.8.10 快速切换后端

```bash
# 使用配置命令快速切换
hermes config set terminal.backend docker
hermes config set terminal.backend local
hermes config set terminal.backend ssh

# 或通过环境变量临时覆盖（不修改 config.yaml）
TERMINAL_ENV=docker hermes
```

---

## 6.9 安全提示

### 6.9.1 不要提交 .env 到版本控制

`.env` 文件包含 API Key 等敏感信息，**绝不能**提交到 Git 仓库。Hermes Agent 的 `.gitignore` 已默认排除以下文件：

```gitignore
.env
.env.local
.env.development.local
.env.test.local
.env.production.local
.env.development
.env.test
```

验证 `.env` 未被追踪：

```bash
git check-ignore .env
# 应输出: .env
```

如果 `.env` 曾被意外提交，需立即**轮换所有泄露的 API Key**，并使用 `git filter-repo` 或 BFG Repo-Cleaner 清理历史记录。

### 6.9.2 文件权限

安装脚本自动将 `.env` 权限设为 `0600`（仅所有者可读写）。手动验证：

```bash
ls -la ~/.hermes/.env
# 应显示: -rw------- 1 user group ... .env
```

如权限不正确，手动修复：

```bash
chmod 600 ~/.hermes/.env
```

`config.yaml` 不含密钥，使用默认权限 `0644` 即可。`~/.hermes/` 目录本身也应限制访问权限：

```bash
chmod 700 ~/.hermes/
```

### 6.9.3 密钥管理最佳实践

1. **使用最小权限原则**：创建 GitHub Token 等凭据时，仅授予必要的最小权限范围。
2. **定期轮换密钥**：定期在各提供商控制台轮换 API Key。
3. **不要在日志或对话中暴露密钥**：Hermes Agent 的工具输出可能包含环境变量，注意不要将日志分享给不可信方。
4. **使用 SSH 后端隔离**：对安全要求高的场景，使用 SSH 后端将命令执行与密钥存储分离。Agent 在远程服务器执行命令，无法读取本地 `.env`。
5. **Docker 出口防火墙**：使用 Docker 后端时启用 Egress Credential Firewall，容器内只看到代理 Token 而非真实 Key。
6. **环境变量黑名单**：Hermes Agent 禁止通过 `hermes config set` 写入 `LD_PRELOAD`、`PYTHONPATH`、`PATH` 等危险变量，防止子进程注入攻击。
7. **Sudo 密码**：避免在 `config.yaml` 中明文存储 sudo 密码，优先使用免密 sudo 配置。

### 6.9.4 配置备份与恢复

备份配置时，`.env` 文件应加密存储：

```bash
# 加密备份
tar czf - ~/.hermes/.env ~/.hermes/config.yaml | gpg -c > hermes-config-backup.tar.gz.gpg

# 恢复
gpg -d hermes-config-backup.tar.gz.gpg | tar xzf - -C ~/
```

### 6.9.5 Dashboard 安全

如果启用 Dashboard（Web 界面），注意：

- Dashboard 默认仅绑定 `127.0.0.1`，不要暴露到公网
- 如需远程访问，使用 SSH 端口转发或反向代理加身份认证
- Dashboard 可以读取和修改配置，包括 `.env` 中的密钥，务必做好访问控制

---

## 6.10 配置验证

完成配置后，运行以下命令验证：

```bash
# 系统诊断
hermes doctor

# 查看当前配置
hermes config

# 查看模型提供商状态
hermes model

# 查看工具启用状态
hermes tools list

# 快速对话测试
hermes "你好，请用一句话确认你已正常工作"
```

`hermes doctor` 会检查配置完整性、API Key 可用性、依赖安装状态等，并给出具体的修复建议。
