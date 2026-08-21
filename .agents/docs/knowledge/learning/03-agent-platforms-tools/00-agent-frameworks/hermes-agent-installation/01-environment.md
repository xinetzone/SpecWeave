---
title: "Hermes Agent 安装方案 - 环境要求与前置准备"
chapter: 1
source:
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/scripts/install.ps1
  - external/libs/hermes-agent/Dockerfile
  - external/libs/hermes-agent/package.json
  - external/libs/hermes-agent/.python-version
  - external/libs/hermes-agent/.nvmrc
  - external/libs/hermes-agent/constraints-termux.txt
  - external/libs/hermes-agent/website/docs/getting-started/platform-support.md
  - external/libs/hermes-agent/website/docs/getting-started/installation.md
  - external/libs/hermes-agent/README.md
---

# 1. 环境要求与前置准备

本章列出安装 Hermes Agent 前必须满足的操作系统、硬件、系统依赖与运行时版本要求。所有信息均以项目源码中的 `pyproject.toml`、安装脚本、`Dockerfile`、`package.json` 及官方平台支持文档为准。

---

## 1.1 支持的操作系统及版本

Hermes Agent 将平台分为 Tier 1（主力支持，回归问题优先修复）和 Tier 2（尽力维护）。架构方面，官方构建覆盖 `x86_64` 与 `aarch64`（Apple Silicon / ARM64）。

### 1.1.1 Tier 1（主力支持）

| 操作系统 | 架构 | 安装方式 | 说明 |
|---|---|---|---|
| **macOS**（Apple Silicon） | `arm64` | Hermes Desktop、`install.sh` | 不支持 Intel（x86_64）Mac |
| **Windows 10 / 11** | `x86_64`、`aarch64` | Hermes Desktop、`install.ps1` | 原生运行，无需 WSL；少量功能受限 |
| **Linux / WSL2** | `x86_64`、`aarch64` | `install.sh` | 在最新 Ubuntu 与 WSL2 上测试；需 glibc、systemd 并遵循 FHS |
| **Docker 容器** | `x86_64`、`aarch64` | `docker pull` | 基于 Debian 13（trixie），使用 s6-overlay 进程管理；不支持 `hermes update`，更新需拉取新镜像 |

Linux 发行版方面，安装脚本内置了对 **Ubuntu / Debian**（`apt`）、**Fedora**（`dnf`）、**Arch**（`pacman`）的包管理器适配。其他具备 glibc、systemd 且遵循文件系统层次标准（FHS）的现代发行版通常也可正常运行。

### 1.1.2 Tier 2（尽力维护）

| 操作系统 | 架构 | 安装方式 | 说明 |
|---|---|---|---|
| **Android（Termux）** | `aarch64` | `install.sh` | 手机端部分功能不可用；安装脚本会切换到 stdlib `venv` + `pip` 路径，并使用精心挑选的 `[termux]` extra |
| **Nix / NixOS** | macOS、Linux、NixOS | `install.sh`（Nix flake） | 因 Node.js 打包问题可能频繁损坏，仅尽力支持 |

### 1.1.3 明确不支持

以下平台/安装方式**不受支持**，相关兼容代码可能随时被移除：

- macOS on Intel（x86_64）处理器
- 通过 AUR 安装
- 通过 PyPI 安装（`pip install hermes-agent`、`uv tool install hermes-agent` 等）
- 通过 Homebrew 安装（`brew install hermes-agent`）

> **Windows 与 WSL2 的选择**：原生 Windows（PowerShell `install.ps1`）已为 Tier 1，CLI、网关、TUI 与工具链均可原生运行，默认安装到 `%LOCALAPPDATA%\hermes`。若偏好 Linux 工具链，可在 WSL2 中使用 `install.sh`，此时安装位置为 `~/.hermes`（与 Linux 一致）。

---

## 1.2 硬件要求

Hermes Agent 核心是 LLM API 客户端——模型推理在云端完成，因此本地 CPU 与内存门槛较低。磁盘占用主要来自 Python 虚拟环境、Node.js 运行时、`node_modules` 以及 Playwright 自带的 Chromium 浏览器。

> 以下为**基于组件实际占用的推荐配置**，项目源码未声明硬性硬件下限。若启用本地语音转写（faster-whisper）、唤醒词（openWakeWord/ONNX）或本地大模型等可选功能，资源需求会显著上升。

### 1.2.1 基础配置（CLI / TUI + 云端模型）

| 资源 | 最低可运行 | 推荐 |
|---|---|---|
| CPU | 64 位双核（x86_64 或 aarch64） | 现代多核处理器 |
| 内存 | 2 GB | 4 GB 及以上 |
| 磁盘 | 3 GB 可用空间 | 5 GB 及以上 SSD |

适用场景：仅使用终端界面、文件工具、终端工具，不启用浏览器自动化与本地语音。

### 1.2.2 完整功能配置（含浏览器工具 / TTS）

| 资源 | 推荐 |
|---|---|
| CPU | 4 核及以上 |
| 内存 | 8 GB 及以上 |
| 磁盘 | 8 GB 及以上 SSD |

适用场景：启用 Playwright/Chromium 浏览器自动化、音视频处理（ffmpeg）、TTS 语音消息、消息网关（Telegram/Discord/Slack 等）。

### 1.2.3 可选本地 AI 功能的额外开销

以下功能按需懒加载（lazy-install），**不计入基础安装**，但启用后需额外资源：

- **本地语音转写**（`faster-whisper`、`ctranslate2`、`onnxruntime`）：建议 4 GB+ 内存，模型文件数百 MB 至 1 GB+。
- **本地唤醒词**（`openWakeWord`、`sherpa-onnx`、`pvporcupine`）：额外数百 MB 磁盘，常驻内存约 200–500 MB。
- **本地大模型推理**（通过 Actual Computer 等本地后端）：内存/显存需求取决于所选模型，通常需 8–32 GB 以上。
- **桌面应用构建**（`--include-desktop`）：需额外磁盘空间编译 Electron / 原生 Node 模块。

---

## 1.3 系统依赖清单

官方安装脚本会自动探测并安装 `uv`、Python、Node.js、ripgrep、ffmpeg，但**部分底层依赖仍需用户或系统包管理器预先提供**。下面按平台列出完整清单与安装命令。

### 1.3.1 依赖用途说明

| 依赖 | 用途 | 必需性 |
|---|---|---|
| `git` | 克隆/更新仓库 | **必需**（非 Windows 平台唯一硬性前置） |
| `curl` | 下载 uv、Node.js 等安装物料 | Linux 必需 |
| `xz-utils` | 解压 Node.js 的 `.tar.xz` 归档 | Linux 必需 |
| `gcc` / `g++` / `make` | 编译 Python/Node 原生扩展 | 推荐（桌面 App 必需 `g++`） |
| `python3-dev` | 编译含 C 扩展的 Python 包（头文件） | 源码编译时需要 |
| `python3-venv` | Python 标准库 venv 模块 | Termux 路径需要 |
| `libffi-dev` | `cryptography`、`cffi` 等外部函数接口库 | 编译 `cryptography` 时需要 |
| `libolm-dev` | Matrix 网关端到端加密（`python-olm`） | 可选，Matrix 功能需要 |
| `libatomic1` | GCC 原子运行时库 | 部分原生扩展运行时需要 |
| `ripgrep`（`rg`） | 高速文件/代码搜索 | 推荐（缺失时回退到 grep/findstr） |
| `ffmpeg` | TTS 语音消息的音频格式转换 | 推荐（缺失时语音功能受限） |
| `cmake` | 部分原生扩展的构建系统 | 编译期需要 |
| `pkg-config` | 定位系统库 | Termux/源码编译需要 |
| `openssl` / `ca-certificates` | TLS 根证书与加密库 | 必需（网络访问） |
| `procps` | 进程查看（`ps` 等） | 运行时需要 |
| `openssh-client` | SSH 相关工具 | 可选 |
| `docker-cli` | Docker 容器内使用 | 仅 Docker 镜像内置 |

### 1.3.2 Linux（Debian / Ubuntu）

官方 Dockerfile 基于 Debian 13（trixie），其 `apt` 依赖清单可作为最完整的参考：

```bash
sudo apt update
sudo apt install -y \
  ca-certificates curl iputils-ping \
  python3 python-is-python3 python3-dev python3-venv \
  ripgrep ffmpeg \
  gcc g++ make cmake \
  libffi-dev libolm-dev libatomic1 \
  procps git openssh-client xz-utils
```

日常使用最小前置（脚本会自动补齐其余项）：

```bash
sudo apt update && sudo apt install -y git curl xz-utils
```

若计划构建桌面应用，还需安装编译工具链：

```bash
sudo apt install -y build-essential
```

### 1.3.3 Linux（Fedora / RHEL / CentOS）

```bash
sudo dnf install -y \
  git curl xz \
  gcc gcc-c++ make cmake \
  python3-devel python3-virtualenv \
  libffi-devel libolm-devel libatomic \
  ripgrep ffmpeg \
  procps-ng openssh-clients ca-certificates
```

> 注：Fedora/RHEL 不支持 Playwright 的 `--with-deps` 自动装库，Chromium 所需的系统库需管理员另行安装（安装脚本会打印对应的 `dnf` 命令）。

### 1.3.4 Linux（Arch）

```bash
sudo pacman -S --needed --noconfirm \
  git curl xz \
  gcc make cmake \
  python libffi libolm \
  ripgrep ffmpeg \
  procps-ng openssh ca-certificates
```

### 1.3.5 macOS

前置要求：

- **Apple Silicon（M1 及后续机型）**，Intel Mac 不受支持。
- 安装 [Homebrew](https://brew.sh/)（推荐，脚本会优先使用它安装 ripgrep/ffmpeg）。
- 安装 Git 与命令行编译工具：

```bash
xcode-select --install
```

该命令会弹出系统对话框，安装 Apple Command Line Tools（同时提供 `git`、`clang`、`make` 等）。若已安装 Homebrew，也可直接：

```bash
brew install git ripgrep ffmpeg
```

> macOS 上 Matrix 加密依赖 `python-olm` 无原生构建路径，相关功能通过懒加载在首次使用时按需安装。

### 1.3.6 Windows（原生，PowerShell）

Windows 原生安装通过 `install.ps1` 完成，**无需预先安装 Git**——若系统未检测到 Git，脚本会自动下载一份约 45 MB 的 MinGit/PortableGit 到 Hermes 目录，不会干扰系统已有的 Git。

脚本会自动处理：

- **Git**：自动下载 MinGit（或使用系统已安装的 Git）。
- **Node.js**：若系统版本过低，自动安装 Hermes 托管的 Node.js。
- **ripgrep**：通过 `winget`（`BurntSushi.ripgrep.MSVC`）、`choco` 或 `scoop` 自动安装。
- **ffmpeg**：同样通过上述包管理器自动安装。

若需手动预装，可使用：

```powershell
winget install --id BurntSushi.ripgrep.MSVC
winget install --id Gyan.FFmpeg
```

构建桌面应用（`--include-desktop`）时，原生 Node 模块（如 `node-pty`）的编译需要 **Visual Studio Build Tools**（含 C++ 桌面开发工作负载）。若缺失，桌面阶段会报错并提示安装。Python 侧的 `cryptography`、`pydantic-core` 等在 Windows 上均有预编译 wheel，通常无需本地编译。

> Windows 10/11 支持 x86_64 与 ARM64（Snapdragon X 等）。在 ARM64 设备上，脚本会检测真实架构并安装对应版本，避免 Prism x64 仿真导致的架构误判。

### 1.3.7 WSL2（Windows Subsystem for Linux）

WSL2 内运行的是完整 Linux 环境，按 [1.3.2 节](#132-linuxdebian--ubuntu)的 Debian/Ubuntu 命令安装即可。建议使用较新的 Windows 11 22H2+ 以获得镜像网络模式（mirrored mode），方便 WSL2 访问 Windows 宿主机上的本地模型服务。

```bash
sudo apt update && sudo apt install -y git curl xz-utils build-essential
```

### 1.3.8 Android（Termux）

Termux 路径**不使用 uv**，而是使用 Python 标准库 `venv` + `pip`，并需要 Android 上的编译工具链来构建带原生扩展的包。安装脚本会自动执行以下 `pkg` 安装：

```bash
pkg update
pkg install -y \
  clang rust make pkg-config \
  libffi openssl \
  ca-certificates curl \
  git \
  ripgrep ffmpeg
```

Python 本身由 Termux 提供：

```bash
pkg install -y python
```

> Termux 仅支持 `aarch64`。由于 Android 使用 Bionic libc（而非 glibc/musl），`nemo-relay` 等仅发布 manylinux/musllinux wheel 的原生包会被标记为不可用，安装脚本会自动降级到无 Relay 路径。Termux 上还需使用 `constraints-termux.txt` 约束 `ipython`、`jedi`、`parso` 等包版本，以保证经过测试的安装路径稳定。

---

## 1.4 Python 版本要求

### 1.4.1 版本范围

```
>=3.11,<3.14
```

即支持 **Python 3.11、3.12、3.13**，明确排除 Python 3.14 及以上版本。该约束定义在 `pyproject.toml` 中：

```toml
requires-python = ">=3.11,<3.14"
```

项目内 `.python-version` 文件固定为 `3.11`，而官方 Docker 镜像使用 **Python 3.13**（`ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie`），说明 3.11–3.13 均在 CI/发布覆盖范围内。

### 1.4.2 为什么不支持 Python 3.14

`pyproject.toml` 中对该上限有明确的"承重"注释（load-bearing，非装饰性约束）：

- `uv` 会根据 `requires-python` 解析项目 Python；若存在继承的 `UV_PYTHON` 环境变量，或全新发行版的最新解释器被 uv 自动选中，解析器可能选到 3.14。
- Python 3.14 尚新，部分 **Rust 编写的传递依赖**（以 `pydantic-core` 为代表）尚未发布 `cp314` 预编译 wheel。
- 缺少 wheel 时，pip/uv 会回退到通过 **maturin 从源码构建** Rust 扩展，这一过程在标准安装环境中会失败。
- 将上限设为 `<3.14` 可让 uv 在遇到 3.14 时**直接报出清晰的错误并拒绝**，而不是尝试一次注定失败的源码编译。待 Rust 传递依赖发布 cp314 wheel 后，该上限会被提升。

### 1.4.3 Python 安装方式

**用户通常无需手动安装 Python。** 安装脚本的处理逻辑为：

- **Linux / macOS / WSL2**：由 `uv` 负责自动下载与管理 Python（`uv python find 3.11` → 未找到则 `uv python install 3.11`），无需 sudo。uv 管理的 Python 默认位于 `$HERMES_HOME` 或（Linux root FHS 安装时）`/usr/local/share/uv/python`。
- **Termux**：通过 `pkg install python` 安装 Termux 源中的 Python，并要求版本 ≥ 3.11。
- **Windows**：由 `uv` 自动下载托管 Python。

> 若希望手动指定解释器，可设置 `UV_PYTHON` 环境变量，但需确保其版本落在 `>=3.11,<3.14` 区间内，否则 uv 会拒绝解析。

---

## 1.5 Node.js 版本要求

### 1.5.1 版本范围

```
>=22.22.0
```

该下限定义在根目录 `package.json` 的 `engines` 字段中，由 `react-router` 8.3.0 的 `engines.node` 约束传导而来：

```json
"engines": {
  "node": ">=22.22.0",
  "npm": "<11.10.0 || >=11.17.0"
}
```

项目 `.nvmrc` 与官方 Docker 镜像均使用 **Node 26**（`node:26-bookworm-slim`），这是当前推荐的 LTS 主版本；但 22.22.0+ 仍满足最低构建要求。安装脚本中的 `node_satisfies_build` 函数按主版本号 + 次版本号进行判定：主版本 ≥ 22，且当主版本恰为 22 时次版本 ≥ 22。

### 1.5.2 npm 版本限制

`package.json` 同时限定了 npm 版本：

```
<11.10.0  ||  >=11.17.0
```

原因是 npm **11.10.0 至 11.16.x** 存在缺陷：能识别 `.npmrc` 中的 `min-release-age`（14 天新版保护期），却忽略 `min-release-age-exclude`（豁免清单），导致本应豁免的新发布依赖被 14 天门槛拦截，安装以 `ETARGET` 失败。配合 `engine-strict=true`，该版本区间的 npm 无法完成本仓库安装。安装脚本会检测到此情况并改用 Hermes 托管的 Node.js（其内置的 npm 不受影响）。

### 1.5.3 Node.js 安装方式

- **Linux / macOS / WSL2**：若系统 Node 版本不足，脚本会从 `https://nodejs.org/dist/latest-v22.x/` 下载官方预编译二进制（`.tar.xz`），解压到 `$HERMES_HOME/node/`，并将 `node`/`npm`/`npx` 软链到命令目录（`~/.local/bin` 或 root FHS 模式下的 `/usr/local/bin`）。
- **Termux**：通过 `pkg install nodejs` 安装。
- **Windows**：若系统 Node 不满足要求，脚本通过 `winget`（在 ARM64 上强制获取 ARM64 安装包）或下载官方安装包进行安装。

Node.js 主要用于浏览器自动化（Playwright / agent-browser）、WhatsApp 桥接、TUI 前端构建以及桌面应用打包。基础 CLI 交互本身不直接依赖 Node，但默认安装会包含它以支持浏览器工具。

---

## 1.6 uv 包管理器

### 1.6.1 为什么使用 uv

Hermes Agent 使用 [uv](https://docs.astral.sh/uv/)（Astral 出品的 Rust 高性能 Python 包管理器）完成 Python 解释器管理、虚拟环境创建与依赖同步。相较于 `pip` + `venv`，uv 速度更快、解析更确定，且能自动下载受管 Python 版本，避免污染系统 Python。

### 1.6.2 安装方式

**方式一：由安装脚本自动安装（推荐）**

`install.sh` 会将一份**Hermes 托管的 uv**安装到 `$HERMES_HOME/bin/uv`（非 `~/.local/bin`，也不探测 PATH 中已有的 uv），以确保安装脚本与运行时 `hermes update` 路径（`hermes_cli/managed_uv.py`）保持一致。其内部逻辑等价于：

```bash
curl -LsSf https://astral.sh/uv/install.sh -o /tmp/uv-installer.sh
UV_UNMANAGED_INSTALL="$HOME/.hermes/bin" sh /tmp/uv-installer.sh
```

`UV_UNMANAGED_INSTALL` 环境变量指示 Astral 官方安装器将二进制直接放入指定目录。脚本还会设置 `UV_NO_CONFIG=1`，以避免在 `sudo -u` 等场景下读取到错误用户主目录中的 uv 配置。

**方式二：手动独立安装**

若希望在手动/源码安装前自行准备 uv，可使用官方方式：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows（PowerShell）：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

或通过 pip 安装：

```bash
pip install uv
```

安装后验证：

```bash
uv --version
```

> 官方 Docker 镜像直接从 `ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie` 拷贝 uv 二进制（版本 0.11.6），这是经发布验证的版本基线。

### 1.6.3 Termux 例外

在 Termux 上，安装脚本**不安装也不使用 uv**，而是回退到 Python 标准库 `venv` + `pip`：

```bash
python -m venv venv
source venv/bin/activate
pip install -e '.[termux]' -c constraints-termux.txt
```

这是因为 Termux/Android 的 Bionic libc 环境与 uv 的自包含 Python 发行版存在兼容性问题。

### 1.6.4 uv 常用命令参考

手动源码安装时会用到以下命令：

```bash
# 创建虚拟环境（指定 Python 版本）
uv venv venv --python 3.11

# 激活虚拟环境
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 同步依赖（按 uv.lock 锁定版本）
uv sync

# 安装额外功能组
uv sync --extra all
uv sync --extra messaging
uv pip install -e ".[dev]"

# 运行项目内命令
uv run hermes --help
```

---

## 1.7 前置准备检查清单

正式运行安装脚本前，建议逐项确认：

- [ ] 操作系统在 [1.1 节](#11-支持的操作系统及版本) 支持范围内，架构为 x86_64 或 aarch64。
- [ ] 磁盘可用空间 ≥ 3 GB（完整功能建议 ≥ 8 GB）。
- [ ] 内存 ≥ 2 GB（完整功能建议 ≥ 8 GB）。
- [ ] 已安装 `git` 并可执行 `git --version`（Windows 可由脚本自动补齐）。
- [ ] Linux 上已安装 `curl` 与 `xz-utils`。
- [ ] 能访问 `github.com`、`pypi.org`、`nodejs.org`、`astral.sh`（或已配置可用镜像源）。
- [ ] 未设置会干扰安装的 `PYTHONPATH` / `PYTHONHOME`（脚本会主动清除它们）。
- [ ] （可选）构建桌面应用前，Linux 已装 `build-essential`，Windows 已装 Visual Studio Build Tools。
- [ ] （可选）需要 Matrix 端到端加密时，Linux 已装 `libolm-dev`。
- [ ] （Termux）已通过 `pkg install python clang rust make pkg-config libffi openssl` 准备好编译工具链。

完成本章准备后，即可进入第 2 章「安装步骤」。
