---
title: "Hermes Agent 安装方案 - 手动源码安装指南"
chapter: 4
source:
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/package.json
  - external/libs/hermes-agent/web/package.json
  - external/libs/hermes-agent/ui-tui/package.json
  - external/libs/hermes-agent/setup-hermes.sh
  - external/libs/hermes-agent/README.md
  - external/libs/hermes-agent/README.zh-CN.md
  - external/libs/hermes-agent/AGENTS.md
  - external/libs/hermes-agent/website/docs/developer-guide/contributing.md
  - external/libs/hermes-agent/website/docs/getting-started/installation.md
  - external/libs/hermes-agent/scripts/install.sh
---

# 4. 手动源码安装指南

本章面向希望完全掌控安装过程的开发者、贡献者以及 CI/CD 环境，详细说明如何从 Git 仓库手动克隆并安装 Hermes Agent。内容涵盖仓库克隆、uv 与 venv+pip 两种 Python 环境方案、完整的依赖说明（核心依赖与可选 extras）、Node.js 前端依赖安装与构建、开发者模式、Playwright 浏览器安装、`hermes` 命令的 PATH 配置，以及 `setup-hermes.sh` 一键脚本的使用。所有信息均以项目源码中的 `pyproject.toml`、`package.json`、`setup-hermes.sh`、`README.md` 与 `AGENTS.md` 为准。

> 手动源码安装适用于以下场景：为项目贡献代码、需要在特定分支或 commit 上运行、CI/CD 流水线、需要完全自定义虚拟环境位置，或不希望使用官方托管安装布局。普通用户推荐使用第 2 章的 `install.sh`（Linux/macOS/WSL2）或第 3 章的 `install.ps1`（Windows）。

---

## 4.1 克隆仓库

### 4.1.1 前置要求

克隆仓库前，请确保已安装：

- **Git**（建议 2.0+，并安装 `git-lfs` 扩展）
- **Git LFS**：仓库中部分二进制资源通过 Git LFS 管理，贡献者必须安装

验证 Git 可用性：

```bash
git --version
git lfs version    # 贡献者必需
```

若尚未安装 Git LFS：

```bash
# Debian/Ubuntu
sudo apt install git-lfs

# macOS (Homebrew)
brew install git-lfs

# 安装后初始化（全局一次）
git lfs install
```

### 4.1.2 HTTPS 克隆（推荐，无需 SSH 密钥）

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

若需要浅克隆以减少下载量（CI/CD 场景）：

```bash
git clone --depth 1 --branch main https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
```

### 4.1.3 SSH 克隆（已配置 GitHub SSH 密钥的开发者）

```bash
git clone git@github.com:NousResearch/hermes-agent.git
cd hermes-agent
```

浅克隆形式：

```bash
git clone --depth 1 --branch main git@github.com:NousResearch/hermes-agent.git
cd hermes-agent
```

> 官方安装脚本 `install.sh` 的克隆策略为：先尝试 SSH（`BatchMode=yes`，5 秒超时快速失败），失败后回退到 HTTPS，并使用 `--depth 1` 浅克隆。手动克隆时可按需选择。

### 4.1.4 检出特定分支或 Commit

```bash
# 检出开发分支
git checkout develop

# 检出固定 commit（可复现构建）
git checkout --detach abc1234def5678...
```

### 4.1.5 虚拟环境位置建议

官方贡献者文档明确建议：**将虚拟环境创建在克隆的源码树之外**。原因是 Hermes Agent 自身拥有终端工具，可能执行相对路径命令（如 `rm -rf venv`、`uv venv venv`），若 venv 位于工作目录内，Agent 运行时可能误删自身的运行时环境。

推荐做法：

```bash
# venv 放在源码树外
uv venv ~/.hermes/venvs/hermes-dev --python 3.11
```

若使用 `setup-hermes.sh` 脚本，它会自动在仓库内创建 `venv/` 目录——这适合一次性使用，但在长期开发环境中建议将 venv 放在外部。

---

## 4.2 使用 uv 创建虚拟环境并安装依赖（推荐）

[uv](https://docs.astral.sh/uv/) 是 Astral 出品的 Rust 高性能 Python 包管理器，也是 Hermes Agent 官方推荐的方式。它能自动管理 Python 解释器、创建虚拟环境，并利用 `uv.lock` 实现哈希验证的确定性安装。

### 4.2.1 安装 uv

若系统尚未安装 uv：

```bash
# Linux / macOS / WSL2
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 或通过 pip
pip install uv
```

安装后验证：

```bash
uv --version
```

> `setup-hermes.sh` 脚本会自动检测并安装 uv 到 `~/.local/bin/uv`（或 `~/.cargo/bin/uv`），无需手动预装。

### 4.2.2 创建虚拟环境

Hermes Agent 要求 Python `>=3.11,<3.14`（即 3.11、3.12、3.13，不支持 3.14+）。推荐使用 Python 3.11。

**在源码树内创建（与 setup-hermes.sh 一致）：**

```bash
cd hermes-agent
uv venv venv --python 3.11
```

**在源码树外创建（推荐用于长期开发）：**

```bash
uv venv ~/.hermes/venvs/hermes-dev --python 3.11
```

uv 会自动下载并管理对应版本的 Python 解释器，无需系统预装。若指定版本的 Python 已存在，uv 会直接复用。

激活虚拟环境：

```bash
# Linux / macOS / WSL2
source venv/bin/activate
# 或外部 venv：
source ~/.hermes/venvs/hermes-dev/bin/activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
# 或外部 venv：
~\.hermes\venvs\hermes-dev\Scripts\Activate.ps1
```

### 4.2.3 使用 uv.lock 哈希验证安装（首选）

仓库根目录提供 `uv.lock` 锁文件，记录了所有依赖（含传递依赖）的精确版本与 SHA256 哈希。使用锁文件安装可防御 PyPI 包被投毒的供应链攻击，这是**唯一具备传递依赖哈希保护的安装路径**。

```bash
# 安装 [all] extra 并严格按 uv.lock 解析
uv sync --extra all --locked
```

参数说明：
- `--extra all`：安装 `pyproject.toml` 中精选的 `[all]` extra（详见 4.4 节）；
- `--locked`：要求锁文件与 `pyproject.toml` 保持一致，若不一致则报错而非自动更新。

> `setup-hermes.sh` 在检测到 `uv.lock` 存在时，优先使用 `UV_PROJECT_ENVIRONMENT="$PWD/venv" uv sync --extra all --locked` 进行安装。

### 4.2.4 不使用锁文件的安装

若锁文件过期或需要重新解析依赖，可使用 `uv pip install`：

```bash
# 安装核心 + [all] extra（可编辑模式）
uv pip install -e ".[all]"

# 仅安装核心依赖
uv pip install -e "."

# 安装指定 extras 组合
uv pip install -e ".[all,dev]"
```

`-e`（`--editable`）表示以可编辑模式安装，源码修改后无需重新安装即可生效，这对开发者至关重要。

### 4.2.5 uv 常用命令速查

```bash
# 查找/安装 Python
uv python find 3.11
uv python install 3.11

# 创建虚拟环境
uv venv venv --python 3.11

# 同步依赖（按锁文件）
uv sync --extra all

# 安装额外包
uv pip install <package>

# 运行项目内命令（自动激活 venv）
uv run hermes --help
uv run python -m pytest tests/ -q
```

---

## 4.3 备选方案：标准 venv + pip

若无法使用 uv（如 Termux 环境、受限 CI 环境、或偏好标准库工具），可使用 Python 内置的 `venv` + `pip` 完成安装。

### 4.3.1 确认 Python 版本

```bash
python3 --version
# 必须输出 3.11.x、3.12.x 或 3.13.x
```

若系统 Python 版本不满足要求，需通过系统包管理器、[pyenv](https://github.com/pyenv/pyenv) 或 [python.org](https://www.python.org/downloads/) 安装合适版本。

### 4.3.2 创建并激活虚拟环境

```bash
cd hermes-agent

# 创建虚拟环境
python3 -m venv venv

# 激活（Linux / macOS / WSL2）
source venv/bin/activate

# 激活（Windows PowerShell）
venv\Scripts\Activate.ps1
```

### 4.3.3 升级 pip 与构建工具

```bash
pip install --upgrade pip setuptools wheel
```

### 4.3.4 安装依赖

```bash
# 安装核心 + [all] extra（可编辑模式）
pip install -e ".[all]"

# 仅安装核心依赖（最小安装）
pip install -e "."

# 开发者模式：核心 + [all] + [dev]
pip install -e ".[all,dev]"
```

> **注意**：`pip install` 不具备 `uv.lock` 的哈希验证能力，传递依赖会从 PyPI 实时解析。在安全敏感环境中，建议使用 `uv sync --locked`。

### 4.3.5 Termux（Android）特殊路径

Termux 环境**不使用 uv**，而是使用标准 `venv` + `pip`，并配合 `constraints-termux.txt` 约束文件保证经过测试的依赖版本：

```bash
pkg install python clang rust make pkg-config libffi openssl \
    ca-certificates curl git ripgrep ffmpeg

cd hermes-agent
python -m venv venv
source venv/bin/activate

pip install --upgrade pip setuptools wheel
pip install -e ".[termux]" -c constraints-termux.txt
```

若 `[termux]` bundle 安装失败，回退到基础安装：

```bash
pip install -e "." -c constraints-termux.txt
```

> Termux 仅支持 `aarch64`，且因 Bionic libc 不兼容 manylinux/musllinux wheel，`nemo-relay` 等原生包会自动跳过。

---

## 4.4 Python 依赖说明

Hermes Agent 的 Python 依赖在 `pyproject.toml` 中声明，采用**核心依赖精确锁定 + 可选 extras 懒加载**的策略。版本为 `0.20.0`，要求 Python `>=3.11,<3.14`。

### 4.4.1 依赖设计原则

- **核心依赖全部精确锁定**（`==X.Y.Z`，无版本范围），防止 PyPI 在未经代码审查的情况下推送新版本。这一策略在 2026 年 5 月 Mini Shai-Hulud 蠕虫事件后加固。
- **只有每个会话都会用到的包**才进入核心依赖；提供商特定的包（如 `anthropic`、`firecrawl-py`）放入 optional extras，通过 `tools/lazy_deps.py` 在用户选择对应后端时**懒加载安装**。
- **`[all]` extra 是精心策划的子集**，只包含无法懒加载的依赖（CLI、MCP、Web 等），并非所有 extras 的总和。提供商后端（anthropic、exa、firecrawl、voice、messaging 等）有意排除在 `[all]` 之外，以防某个被隔离的 PyPI 版本破坏所有全新安装。

### 4.4.2 核心依赖（dependencies）

核心依赖约 30 个，每个 Hermes 会话都会加载。关键依赖包括：

| 包 | 版本 | 用途 |
|---|---|---|
| `openai` | 2.24.0 | OpenAI 兼容 API 客户端（支持多家推理提供商） |
| `pydantic` | 2.13.4 | 数据模型与校验（需 pydantic-core 2.46.4+ 修复非主线程段错误） |
| `httpx[socks]` | 0.28.1 | 异步 HTTP 客户端（含 SOCKS 代理支持） |
| `requests` | 2.33.0 | 同步 HTTP 客户端（CVE-2026-25645 修复版） |
| `urllib3` | >=2.7.0,<3 | HTTP 底层库（修复 GHSA-mf9v-mfxr-j63j 解压炸弹绕过） |
| `cryptography` | 48.0.1 | 加密库（CVE-2026-39892、CVE-2026-34073 修复版） |
| `PyJWT[crypto]` | 2.13.0 | JWT 令牌（Skills Hub GitHub App 认证） |
| `rich` | 14.3.3 | 终端富文本渲染 |
| `prompt_toolkit` | 3.0.52 | 交互式 CLI 输入与自动补全 |
| `fastapi` | >=0.104.0,<1 | Web 框架（Dashboard/API 服务） |
| `uvicorn[standard]` | >=0.24.0,<1 | ASGI 服务器 |
| `python-multipart` | >=0.0.9,<1 | 文件上传支持（Dashboard 文件管理器） |
| `jinja2` | 3.1.6 | 模板引擎 |
| `pyyaml` | 6.0.3 | YAML 配置解析 |
| `ruamel.yaml` | 0.18.17 | YAML  Round-trip 解析 |
| `Markdown` | 3.10.2 | Markdown→HTML 转换（消息投递） |
| `croniter` | 6.0.0 | Cron 表达式解析（内置定时调度器） |
| `packaging` | 26.0 | 版本号解析 |
| `Pillow` | 12.3.0 | 图像处理（视觉工具图片缩放恢复） |
| `websockets` | 15.0.1 | WebSocket（浏览器 CDP 监管） |
| `psutil` | 7.2.2 | 跨平台进程管理 |
| `pathspec` | 1.1.1 | .gitignore 感知的文件匹配 |
| `tenacity` | 9.1.4 | 重试库 |
| `python-dotenv` | 1.2.2 | .env 文件加载 |
| `fire` | 0.7.1 | Google Fire CLI 库 |
| `certifi` | 2026.5.20 | CA 证书包 |

**平台特定核心依赖：**

| 包 | 平台 | 用途 |
|---|---|---|
| `tzdata` | Windows | IANA 时区数据库（Windows 不内置） |
| `pywinpty` | Windows | Windows PTY 支持 |
| `pywin32` | Windows | Win32 API（SSH 运行时等） |
| `concurrent-log-handler` | Windows | 跨进程日志轮转（修复 WinError 32） |
| `ptyprocess` | 非 Windows | POSIX PTY |
| `nemo-relay` | macOS arm64 / Linux x86_64+aarch64 / Windows x64+ARM64 | 第一方生命周期与共享指标运行时（仅发布 wheel，无 sdist） |

### 4.4.3 可选 Extras 总览

`pyproject.toml` 的 `[project.optional-dependencies]` 定义了以下 extras。标注为**懒加载**的 extras 不会在安装时拉取，而是在用户首次使用对应功能时由 `tools/lazy_deps.py` 自动安装。

#### 推理提供商后端

| Extra | 包 | 版本 | 安装方式 | 说明 |
|---|---|---|---|---|
| `anthropic` | `anthropic` | 0.87.0 | 懒加载 | 原生 Anthropic API（CVE-2026-34450/34452 修复版） |
| `bedrock` | `boto3` | 1.42.89 | 懒加载 | AWS Bedrock |
| `vertex` | `google-auth` | 2.55.1 | 懒加载 | Google Vertex AI |
| `azure-identity` | `azure-identity` | 1.25.3 | 懒加载 | Azure 身份认证 |
| `mistral` | `mistralai` | 2.4.8 | 懒加载 | Mistral Voxtral STT/TTS（2026-05 蠕虫事件后清洁版） |

#### 搜索与数据获取

| Extra | 包 | 版本 | 安装方式 | 说明 |
|---|---|---|---|---|
| `exa` | `exa-py` | 2.10.2 | 懒加载 | Exa AI 搜索引擎 |
| `firecrawl` | `firecrawl-py` | 4.17.0 | 懒加载 | Firecrawl 网页抓取 |
| `parallel-web` | `parallel-web` | 0.4.2 | 懒加载 | Parallel Web 搜索 |

#### 图像与媒体

| Extra | 包 | 版本 | 安装方式 | 说明 |
|---|---|---|---|---|
| `fal` | `fal-client` | 0.13.1 | 懒加载 | FAL 图像生成 |
| `edge-tts` | `edge-tts` | 7.2.7 | 懒加载 | Edge TTS（默认 TTS 提供商） |
| `tts-premium` | `elevenlabs` | 1.59.0 | 懒加载 | ElevenLabs 高质量 TTS |

#### 语音与唤醒词

| Extra | 主要包 | 安装方式 | 说明 |
|---|---|---|---|
| `voice` | `faster-whisper==1.2.1`、`sounddevice==0.5.5`、`numpy==2.4.3` | 懒加载 | 本地语音转写（STT），含 ctranslate2、onnxruntime |
| `wake` | `openwakeword==0.6.0`、`onnxruntime==1.27.0`、`sherpa-onnx==1.13.4`、`sentencepiece==0.2.2`、`pvporcupine==4.0.3`、`sounddevice`、`numpy` | 懒加载 | "Hey Hermes" 本地唤醒词检测；macOS 额外安装 `ai-edge-litert==2.1.6`（tflite 运行时） |

#### 消息平台

| Extra | 主要包 | 安装方式 | 说明 |
|---|---|---|---|
| `messaging` | `python-telegram-bot[webhooks]==22.6`、`discord.py[voice]==2.7.1`、`aiohttp==3.14.3`、`brotlicffi`、`slack-bolt==1.29.0`、`slack-sdk==3.43.0`、`qrcode==7.4.2` | 懒加载 | Telegram + Discord + Slack 合集 |
| `slack` | `slack-bolt`、`slack-sdk`、`aiohttp` | 懒加载 | Slack 独立包 |
| `matrix` | `mautrix[encryption]==0.21.0`、`aiosqlite`、`asyncpg`、`aiohttp-socks`、`aiohttp` | 懒加载 | Matrix 端到端加密（`python-olm` 仅 Linux wheel，Windows/macOS 需工具链） |
| `dingtalk` | `dingtalk-stream==0.24.3`、`alibabacloud-dingtalk==2.2.42`、`qrcode` | 懒加载 | 钉钉 |
| `feishu` | `lark-oapi==1.6.8`、`qrcode` | 懒加载 | 飞书 |
| `wecom` | `defusedxml==0.7.1` | 懒加载 | 企业微信回调（防 XXE） |
| `teams` | `microsoft-teams-apps==2.0.13.4`、`aiohttp` | 懒加载 | Microsoft Teams |
| `sms` | `aiohttp` | 懒加载 | SMS 网关 |
| `homeassistant` | `aiohttp` | 懒加载 | Home Assistant |

#### 开发与工具链

| Extra | 主要包 | 安装方式 | 说明 |
|---|---|---|---|
| `dev` | `debugpy==1.8.20`、`pytest==9.1.1`、`pytest-asyncio==1.3.0`、`mcp==1.28.1`、`starlette==1.3.1`、`ty==0.0.21`、`ruff==0.15.10`、`setuptools==83.0.0` | 手动安装 | 调试、测试、类型检查、Lint |
| `cli` | `simple-term-menu==1.6.6` | `[all]` 包含 | 终端菜单（非 Windows 平台） |
| `mcp` | `mcp==1.28.1`、`starlette==1.3.1` | `[all]` 包含 | MCP 服务器/客户端（Starlette 修复 CVE-2026-48710 BadHost） |
| `acp` | `agent-client-protocol==0.9.0` | `[all]` 包含 | Agent Client Protocol（Zed/JetBrains 集成） |
| `web` | `fastapi==0.133.1`、`uvicorn[standard]==0.41.0`、`starlette==1.3.1`、`python-multipart==0.0.32` | `[all]` 包含 | Dashboard Web UI（`hermes dashboard`） |

#### 云服务与沙箱

| Extra | 包 | 版本 | 安装方式 | 说明 |
|---|---|---|---|---|
| `modal` | `modal` | 1.3.4 | 懒加载 | Modal Serverless 沙箱 |
| `daytona` | `daytona` | 0.155.0 | 懒加载 | Daytona Serverless 沙箱 |
| `vercel` | `vercel` | 0.7.2 | 懒加载 | Vercel 集成 |

#### 记忆与认知

| Extra | 包 | 版本 | 安装方式 | 说明 |
|---|---|---|---|---|
| `honcho` | `honcho-ai` | 2.2.0 | 懒加载 | Honcho 辩证式用户建模 |
| `hindsight` | `hindsight-client` | 0.6.1 | 懒加载 | Hindsight 记忆 |
| `supermemory` | `supermemory` | 3.50.0 | 懒加载 | Supermemory 云记忆 |
| `mem0` | `mem0ai` | 2.0.10 | 懒加载 | Mem0 云记忆 |

#### Google 与生产力

| Extra | 主要包 | 安装方式 | 说明 |
|---|---|---|---|
| `google` | `google-api-python-client==2.194.0`、`google-auth==2.55.1`、`google-auth-oauthlib==1.3.1`、`google-auth-httplib2==0.3.1`、`httplib2==0.32.0`、`pyasn1==0.6.4` | `[all]` 包含 | Gmail/Calendar/Drive/Contacts/Sheets/Docs |
| `youtube` | `youtube-transcript-api==1.2.4` | `[all]` 包含 | YouTube 字幕获取 |

#### 其他

| Extra | 说明 |
|---|---|
| `cron` | 空 extra（向后兼容别名，`croniter` 已移入核心依赖） |
| `pty` | 空 extra（向后兼容别名，`ptyprocess`/`pywinpty` 已移入核心依赖） |
| `vision` | 空 extra（向后兼容别名，`Pillow` 已移入核心依赖） |
| `nemo-relay` | 空 extra（向后兼容别名，Relay 在支持平台上为核心依赖） |
| `computer-use` | `mcp` + `starlette`（macOS 桌面控制，cua-driver 二进制通过 `hermes tools` 另行安装） |
| `otlp` | `opentelemetry-sdk==1.39.1` + `opentelemetry-exporter-otlp-proto-http==1.39.1`（OTLP 监控导出，懒加载） |

### 4.4.4 `[all]` Extra 详解

`[all]` **不是**所有 extras 的总和，而是经过策划的子集，仅包含无法懒加载的依赖：

```toml
all = [
  "hermes-agent[cron]",       # 空别名（croniter 在核心）
  "hermes-agent[cli]",        # simple-term-menu
  "hermes-agent[pty]",        # 空别名
  "hermes-agent[mcp]",        # MCP 服务器
  "hermes-agent[homeassistant]",
  "hermes-agent[sms]",
  "hermes-agent[acp]",        # Agent Client Protocol
  "hermes-agent[google]",     # Google Workspace
  "hermes-agent[web]",        # Dashboard
  "hermes-agent[youtube]",
]
```

**有意排除在 `[all]` 之外**的 extras（通过懒加载在首次使用时安装）：

- 提供商后端：`anthropic`、`bedrock`、`vertex`、`azure-identity`、`mistral`
- 搜索：`exa`、`firecrawl`、`parallel-web`
- 图像/TTS：`fal`、`edge-tts`、`tts-premium`
- 语音/唤醒：`voice`、`wake`
- 消息平台：`messaging`、`matrix`、`slack`、`dingtalk`、`feishu`、`teams`、`wecom`
- 沙箱：`modal`、`daytona`、`vercel`
- 记忆：`honcho`、`hindsight`、`supermemory`、`mem0`
- 监控：`otlp`

设计原因：Matrix extra 依赖 `python-olm`（仅 Linux wheel，Windows/macOS 需 `make` 源码构建），若放入 `[all]` 会导致 Windows 上 `uv sync --locked` 失败。将其隔离到懒加载路径，可让用户在具备工具链时才安装。

### 4.4.5 安装命令示例

```bash
# 完整功能安装（推荐）
uv pip install -e ".[all]"

# 开发者完整安装
uv pip install -e ".[all,dev]"

# 最小核心安装（仅 CLI，无 Dashboard/MCP/Google）
uv pip install -e "."

# 核心 + 消息平台
uv pip install -e ".[messaging]"

# 核心 + 语音功能
uv pip install -e ".[voice]"

# 组合多个 extras
uv pip install -e ".[mcp,web,google,dev]"

# Termux 精选 bundle
uv pip install -e ".[termux]"
```

---

## 4.5 Node.js 依赖安装与前端构建

Hermes Agent 的部分功能依赖 Node.js 生态：浏览器自动化（Playwright/agent-browser）、TUI 终端界面（Ink/React）、Dashboard Web 前端（Vite/React）。根目录 `package.json` 定义了 npm workspaces，统一管理 `web/`、`ui-tui/`、`apps/` 等子包。

### 4.5.1 Node.js 版本要求

```
Node.js >= 22.22.0
npm < 11.10.0 或 >= 11.17.0
```

- `.nvmrc` 指定 Node 26（推荐 LTS 主版本）；
- npm 11.10.0–11.16.x 存在缺陷（忽略 `min-release-age-exclude` 豁免清单），无法完成本仓库安装；
- 验证版本：

```bash
node --version   # 应 >= v22.22.0
npm --version    # 应 < 11.10.0 或 >= 11.17.0
```

### 4.5.2 安装根目录 Node 依赖

根目录依赖主要是浏览器工具相关：

```bash
cd hermes-agent
npm install
```

根目录 `package.json` 的关键依赖：

| 包 | 版本 | 用途 |
|---|---|---|
| `agent-browser` | 0.26.0 | 浏览器自动化工具（基于 Playwright） |
| `@streamdown/math` | 1.0.2 | Markdown 数学渲染 |

`npm install` 后会自动触发 `postinstall` 脚本，输出浏览器工具就绪提示。

> 若网络环境受限，可使用 `npm install --workspaces=false` 仅安装根目录依赖，跳过子包。

### 4.5.3 安装 TUI 终端界面依赖（ui-tui）

TUI 是基于 Ink（React for CLI）的终端 UI，通过 `hermes --tui` 启动。

```bash
cd ui-tui
npm install
```

ui-tui 的关键依赖：React 19.2.7、Ink（通过 `@hermes/ink` 本地包）、nanostores、esbuild、tsx、vitest 等。

### 4.5.4 安装 Web Dashboard 依赖（web）

Dashboard 是基于 Vite + React 的 Web 界面，通过 `hermes dashboard` 启动。

```bash
cd web
npm install
```

web 的关键依赖：React 19.2.7、Vite 8.2.0、TailwindCSS 4.3.3、xterm.js（终端模拟）、Three.js（3D 可视化）、react-router 8.3.0 等。

### 4.5.5 构建 Web Dashboard

```bash
cd web
npm run build
```

构建命令为 `tsc -b && vite build`，产物输出到 `web/dist/`。Hermes 运行 `hermes dashboard` 时会自动挂载该目录。若 `web/dist/` 不存在，Dashboard 会以 API-only 模式启动。

开发模式（热重载）：

```bash
cd web
npm run dev
```

### 4.5.6 构建 TUI

```bash
cd ui-tui
npm run build
```

构建命令为 `node scripts/build.mjs`，会先构建 `packages/hermes-ink`，再通过 esbuild 打包 TUI 入口。

TUI 开发模式（监听文件变化自动重建）：

```bash
cd ui-tui
npm run dev
```

### 4.5.7 使用 npm workspaces 统一操作

根目录 `package.json` 声明了 workspaces：`apps/*`、`ui-tui`、`web`、`tests-js`。可在根目录统一执行：

```bash
# 安装所有 workspace 依赖
npm install

# 在所有 workspace 中运行 check（typecheck + test + lint）
npm run check

# 在所有 workspace 中运行 lint:fix
npm run fix

# 仅安装根目录依赖（跳过 workspaces）
npm run install:root

# 仅安装 web workspace
npm run install:web

# 仅安装 ui-tui workspace
npm run install:tui
```

### 4.5.8 前端构建检查清单

若需要使用 Dashboard 或 TUI，完成以下步骤：

- [ ] `npm install`（根目录，含 agent-browser）
- [ ] `cd web && npm install && npm run build`（Dashboard 前端）
- [ ] `cd ui-tui && npm install && npm run build`（TUI 终端界面）

若仅使用经典 CLI（prompt_toolkit 界面），Node.js 依赖只需执行根目录 `npm install`（浏览器工具需要），可不构建 web/ui-tui。

---

## 4.6 开发者模式安装

开发者模式在标准安装基础上增加测试、调试、类型检查和 Lint 工具，并以可编辑模式安装源码，使修改即时生效。

### 4.6.1 一键开发者安装（uv）

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 创建虚拟环境（推荐放在源码树外）
uv venv ~/.hermes/venvs/hermes-dev --python 3.11
source ~/.hermes/venvs/hermes-dev/bin/activate

# 安装所有功能 + 开发工具（可编辑模式）
uv pip install -e ".[all,dev]"

# 安装 Node.js 依赖
npm install

# 可选：构建前端
cd web && npm install && npm run build && cd ..
cd ui-tui && npm install && npm run build && cd ..
```

### 4.6.2 开发者 extra 包含的工具

`[dev]` extra 包含：

| 包 | 版本 | 用途 |
|---|---|---|
| `pytest` | 9.1.1 | 单元测试框架 |
| `pytest-asyncio` | 1.3.0 | 异步测试支持 |
| `debugpy` | 1.8.20 | 调试器（VS Code 等 IDE 集成） |
| `mcp` | 1.28.1 | MCP SDK（测试 MCP 服务器） |
| `starlette` | 1.3.1 | ASGI 工具（测试 Web 端点，CVE-2026-48710 修复版） |
| `ty` | 0.0.21 | Astral 高性能 Python 类型检查器 |
| `ruff` | 0.15.10 | Python Linter/Formatter |
| `setuptools` | 83.0.0 | 构建后端（torch>=2.13 需要 83+） |

### 4.6.3 运行测试

```bash
# 使用项目提供的测试脚本（自动探测 .venv/venv/托管路径）
scripts/run_tests.sh

# 或直接使用 pytest
python -m pytest tests/ -q

# 运行特定测试文件
python -m pytest tests/test_toolsets.py -v

# 跳过集成测试（需要外部服务的测试默认已跳过）
python -m pytest tests/ -q -m "not integration"
```

项目测试套件约 17,000 个测试，分布在约 900 个文件中。

### 4.6.4 类型检查与 Lint

```bash
# 类型检查（ty）
ty check

# Lint（ruff，仅启用 PLW1514 编码规则）
ruff check .

# 自动修复
ruff check . --fix
```

### 4.6.5 开发沙箱

项目提供 `scripts/dev-sandbox.sh`，可在隔离的临时 `HERMES_HOME` 中运行 Hermes，避免污染个人配置：

```bash
# 临时沙箱（退出后清除）
scripts/dev-sandbox.sh python -m hermes_cli.main

# 持久化沙箱（状态保留在 worktree 中）
scripts/dev-sandbox.sh --persistent python -m hermes_cli.main
```

### 4.6.6 基于标准安装器的开发路径

README 推荐的贡献者快速开始路径是先运行标准安装器，再在其克隆的仓库中追加 dev extras：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
cd "${HERMES_HOME:-$HOME/.hermes}/hermes-agent"
uv pip install -e ".[all,dev]"
npm install
scripts/run_tests.sh
```

这与 `hermes update`、托管 venv、lazy dependencies、gateway 和文档工具使用的布局一致。

---

## 4.7 Playwright 浏览器安装

浏览器自动化工具（`browser_navigate` 等）基于 Playwright，需要下载 Chromium 浏览器二进制文件。根目录 `npm install` 安装了 `agent-browser`（Playwright 的封装），但 Chromium 浏览器本身需要单独安装。

### 4.7.1 安装 Chromium

```bash
cd hermes-agent
npx playwright install chromium
```

这会将 Chromium 下载到 Playwright 缓存目录（通常为 `~/.cache/ms-playwright/` 或 Windows 的 `%LOCALAPPDATA%\ms-playwright\`）。

### 4.7.2 安装系统依赖（Linux）

Chromium 在 Linux 上需要若干系统共享库（`libnss3`、`libxkbcommon` 等）。在基于 apt 的发行版（Ubuntu/Debian/Pop!_OS/Mint/Kali）上：

```bash
sudo npx playwright install-deps chromium
```

这会通过 `apt` 自动安装所需的系统库。其他发行版：

| 发行版 | 系统库安装方式 |
|---|---|
| Fedora/RHEL/CentOS/Rocky/Alma | Playwright 不支持自动安装，需管理员手动 `dnf install` 对应库（安装脚本会打印具体命令） |
| Arch | `pacman -S` 安装 Chromium 系统库 |
| openSUSE | `zypper install` 对应库 |

### 4.7.3 一条命令完成（apt 系）

```bash
# 同时安装 Chromium 二进制和系统依赖
sudo npx playwright install --with-deps chromium
```

### 4.7.4 使用系统已有的浏览器

若已安装非 Snap 版的 Chromium/Chrome，可通过环境变量跳过下载：

```bash
export AGENT_BROWSER_EXECUTABLE_PATH=/usr/bin/google-chrome
```

> **注意**：Snap 版 Chromium 因沙箱限制会被明确拒绝。请使用官方 .deb 包或从源码编译的版本。

### 4.7.5 跳过浏览器安装

若不需要浏览器自动化（如纯 CLI/API 使用、无头服务器），可跳过 Playwright 安装以节省约 150 MB 磁盘空间：

```bash
# 安装时不执行 npx playwright install
# 浏览器工具将不可用，其余功能正常
```

后续需要时再手动执行 4.7.1 节的命令即可。

### 4.7.6 agent-browser 与 Playwright 的关系

`agent-browser@0.26.0` 是 Hermes 使用的浏览器自动化封装包，它依赖 Playwright。官方安装脚本 `install.sh` 的 Node 依赖阶段会：

1. `npm install`（安装 agent-browser 及其依赖的 Playwright）；
2. 执行 `npx playwright install chromium`（下载浏览器二进制）；
3. 在 `ui-tui/` 目录执行 `npm install`（TUI 依赖）。

手动安装时需按此顺序自行执行。

---

## 4.8 配置 hermes 命令 PATH

安装完成后，需要让系统能找到 `hermes` 命令。`pyproject.toml` 声明了三个入口脚本：

```toml
[project.scripts]
hermes = "hermes_cli.main:main"
hermes-agent = "run_agent:main"
hermes-acp = "acp_adapter.entry:main"
```

这些脚本在 `pip install -e .` 后会生成在虚拟环境的 `bin/` 目录（Linux/macOS）或 `Scripts\` 目录（Windows）。

### 4.8.1 激活虚拟环境后直接使用（最简单）

虚拟环境激活后，`venv/bin/hermes` 自动在 PATH 上：

```bash
source venv/bin/activate
hermes --version
```

此方式无需额外配置，但每次新开终端都需要先激活 venv。

### 4.8.2 创建符号链接到用户级 bin 目录（推荐）

```bash
mkdir -p ~/.local/bin
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
ln -sf "$(pwd)/venv/bin/hermes-agent" ~/.local/bin/hermes-agent
ln -sf "$(pwd)/venv/bin/hermes-acp" ~/.local/bin/hermes-acp
```

确保 `~/.local/bin` 在 PATH 上：

```bash
# Bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Zsh
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc

# Fish
fish_add_path ~/.local/bin
```

验证：

```bash
which hermes
# 预期：/home/youruser/.local/bin/hermes

hermes --version
```

### 4.8.3 Windows PATH 配置

在 PowerShell 中，将虚拟环境的 `Scripts` 目录添加到用户 PATH：

```powershell
# 假设 venv 位于仓库内
$env:PATH += ";$PWD\venv\Scripts"

# 永久添加到用户 PATH
[Environment]::SetEnvironmentVariable(
    "PATH",
    [Environment]::GetEnvironmentVariable("PATH", "User") + ";$PWD\venv\Scripts",
    "User"
)
```

重启终端后生效。也可直接使用完整路径：

```powershell
.\venv\Scripts\hermes.exe --version
```

### 4.8.4 Termux PATH 配置

Termux 上 `$PREFIX/bin` 已默认在 PATH 上，直接链接：

```bash
ln -sf "$(pwd)/venv/bin/hermes" $PREFIX/bin/hermes
```

### 4.8.5 启动脚本的安全设计

官方安装器创建的 `hermes` 启动脚本（而非简单符号链接）会在执行前 `unset PYTHONPATH` 和 `unset PYTHONHOME`，防止外部 Python 环境污染。手动创建符号链接时，若系统存在全局 `PYTHONPATH`，可能导致导入错误。解决方法是在 shell 配置中取消这些变量：

```bash
unset PYTHONPATH
unset PYTHONHOME
```

或直接使用 venv 内的 Python 运行：

```bash
./venv/bin/python -m hermes_cli.main --help
```

### 4.8.6 使用仓库内启动脚本

仓库根目录有一个 `hermes` shell 脚本，可直接调用而无需配置 PATH：

```bash
./hermes --help
```

该脚本会自动使用仓库内的 venv（若存在）。

---

## 4.9 setup-hermes.sh 脚本使用

`setup-hermes.sh` 是项目自带的快速设置脚本，面向手动克隆仓库的开发者。它自动完成 uv 检测/安装、Python 3.11 准备、虚拟环境创建、依赖安装、.env 初始化、`hermes` 命令链接、技能同步等步骤。

### 4.9.1 基本用法

```bash
cd hermes-agent
chmod +x setup-hermes.sh
./setup-hermes.sh
```

脚本无需任何参数即可运行。它会：

1. **检测平台**：区分桌面/服务器与 Termux（Android）；
2. **安装 uv**：若未找到 uv，自动从 `astral.sh` 下载安装（Termux 跳过，使用 stdlib venv+pip）；
3. **准备 Python 3.11**：通过 `uv python find 3.11` 查找，未找到则 `uv python install 3.11`；
4. **创建虚拟环境**：`uv venv venv --python 3.11`（若 `venv/` 已存在，先删除重建）；
5. **安装依赖**：优先 `uv sync --extra all --locked`（哈希验证），失败后回退到 `uv pip install -e ".[all]"` → `.[安全子集]` → `.`；
6. **安装 ripgrep**（可选，交互式询问）；
7. **创建 .env**：从 `.env.example` 复制，权限设为 0600；
8. **链接 hermes 命令**：符号链接到 `~/.local/bin/hermes`（Termux 为 `$PREFIX/bin/hermes`）；
9. **配置 PATH**：自动检测 shell（bash/zsh），向对应 rc 文件追加 `~/.local/bin`；
10. **同步捆绑技能**：执行 `tools/skills_sync.py` 将内置技能复制到 `~/.hermes/skills/`；
11. **运行设置向导**（可选，交互式询问）：执行 `hermes setup`。

### 4.9.2 Termux 路径

在 Termux 上，脚本自动切换到 stdlib venv + pip 路径：

```bash
python -m venv venv
pip install --upgrade pip setuptools wheel
pip install -e ".[termux]" -c constraints-termux.txt
```

若 `[termux]` bundle 失败，回退到 `pip install -e "." -c constraints-termux.txt`。

### 4.9.3 关键环境变量

脚本中设置了以下环境变量：

| 变量 | 值 | 说明 |
|---|---|---|
| `UV_NO_CONFIG` | `1` | 防止 uv 读取错误用户主目录下的配置文件（sudo -u 场景） |
| `VIRTUAL_ENV` | `$SCRIPT_DIR/venv` | 固定虚拟环境路径 |
| `UV_PROJECT_ENVIRONMENT` | `$SCRIPT_DIR/venv` | 让 `uv sync` 安装到指定 venv |

### 4.9.4 依赖安装回退策略

非 Termux 平台上，脚本采用三级回退：

```bash
# Tier 0: 哈希验证安装（首选）
uv sync --extra all --locked

# Tier 1: [all] extra 重新解析
uv pip install -e ".[all]"

# Tier 2: 安全子集（排除当前不可用的 extras）
uv pip install -e ".[modal,daytona,vercel,messaging,matrix,...]"

# Tier 3: 仅核心依赖
uv pip install -e "."
```

`_BROKEN_EXTRAS` 数组在脚本中默认为空，当某个 extra 暂时不可用时可填入其中跳过。

### 4.9.5 安装后的下一步

脚本结束时会打印：

```bash
# 1. 重新加载 shell
source ~/.bashrc    # 或 ~/.zshrc

# 2. 运行设置向导
hermes setup

# 3. 开始对话
hermes
```

其他常用命令：

```bash
hermes status          # 查看配置状态
hermes gateway install # 安装网关服务（消息 + cron）
hermes cron list       # 查看定时任务
hermes doctor          # 诊断问题
```

### 4.9.6 setup-hermes.sh 与 install.sh 的区别

| 特性 | `setup-hermes.sh` | `install.sh` |
|---|---|---|
| 定位 | 已克隆仓库后的快速设置 | 完整安装器（含克隆、系统依赖、Node.js） |
| 仓库克隆 | 不处理（假设已在仓库内） | 自动克隆到 `~/.hermes/hermes-agent` |
| 系统依赖 | 仅处理 uv、Python、ripgrep | 处理 git、Node.js、ripgrep、ffmpeg、编译工具链 |
| Node.js/Playwright | **不安装** | 自动安装 Node.js、npm 依赖、Chromium |
| 前端构建 | 不构建 | 不构建（Dashboard 按需构建） |
| PATH 配置 | 仅 `~/.local/bin` | 完整的 shell 检测与 FHS 布局支持 |
| 适用场景 | 开发者/CI 已手动克隆 | 终端用户一键安装 |

> **重要**：`setup-hermes.sh` **不安装 Node.js 依赖和 Playwright**。若需要浏览器工具、TUI 或 Dashboard，需在脚本运行后手动执行第 4.5 节和第 4.7 节的步骤。

---

## 4.10 完整手动安装流程示例

以下是一个从零开始的完整手动安装流程，整合了本章所有步骤，适用于 Linux/macOS/WSL2。

### 4.10.1 步骤总览

```bash
# 1. 克隆仓库
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

# 2. 安装 uv（若未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="$HOME/.local/bin:$PATH"

# 3. 创建虚拟环境
uv venv venv --python 3.11
source venv/bin/activate

# 4. 安装 Python 依赖（哈希验证）
uv sync --extra all --locked

# 5. 安装开发者工具（可选）
uv pip install -e ".[dev]"

# 6. 安装 Node.js 依赖
npm install

# 7. 安装 Playwright Chromium
npx playwright install chromium
# Linux 上还需系统依赖：
sudo npx playwright install-deps chromium

# 8. 构建 Dashboard（可选）
cd web && npm install && npm run build && cd ..

# 9. 构建 TUI（可选）
cd ui-tui && npm install && npm run build && cd ..

# 10. 配置 hermes 命令
ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 11. 初始化配置
cp .env.example ~/.hermes/.env
chmod 600 ~/.hermes/.env
mkdir -p ~/.hermes/{cron,sessions,logs,memories,skills}

# 12. 验证安装
hermes doctor
hermes --version
```

### 4.10.2 最小化安装（仅 CLI）

若只需要核心 CLI 功能，不需要浏览器、Dashboard、TUI：

```bash
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent

uv venv venv --python 3.11
source venv/bin/activate
uv pip install -e "."

ln -sf "$(pwd)/venv/bin/hermes" ~/.local/bin/hermes
hermes doctor
```

### 4.10.3 验证清单

安装完成后，逐项验证：

- [ ] `hermes --version` 正常输出版本号
- [ ] `hermes doctor` 无严重错误
- [ ] `python -c "import hermes_cli; print('OK')"` 无导入错误
- [ ] `node --version` >= 22.22.0（若安装了 Node 依赖）
- [ ] `npx playwright install --dry-run chromium` 能找到浏览器（若安装了 Playwright）
- [ ] `~/.hermes/.env` 文件存在且权限为 0600
- [ ] `hermes status` 显示配置状态
- [ ] `hermes` 能进入交互式 CLI

---

## 4.11 小结

手动源码安装为开发者提供了完全的控制权，核心要点如下：

- **Python 环境**：推荐使用 `uv venv` + `uv sync --extra all --locked`，利用 `uv.lock` 的哈希验证保障供应链安全；备选方案为标准 `venv` + `pip install -e ".[all]"`。
- **依赖策略**：核心依赖精确锁定，提供商/平台特定依赖通过 extras 懒加载；`[all]` 是策划子集而非全部 extras 的总和。
- **Node.js 前端**：根目录 `npm install` 安装浏览器工具，`web/` 和 `ui-tui/` 子目录需单独 `npm install` 并 `npm run build`。
- **开发者模式**：`uv pip install -e ".[all,dev]"` 安装测试/调试/Lint 工具，可编辑模式使源码修改即时生效。
- **Playwright**：`npx playwright install chromium` 下载浏览器，Linux 还需 `install-deps` 安装系统库。
- **PATH 配置**：将 `venv/bin/hermes` 符号链接到 `~/.local/bin/` 并确保该目录在 PATH 上。
- **setup-hermes.sh**：自动完成 Python 侧设置，但不处理 Node.js/Playwright，适合作为手动安装的起点。

下一章将介绍 Docker 容器化部署方案。
