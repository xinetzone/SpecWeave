---
title: "Hermes Agent 安装方案 - 官方脚本安装指南（Linux/macOS/WSL2）"
chapter: 2
source:
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/setup-hermes.sh
  - external/libs/hermes-agent/README.md
---

# 2. 官方脚本安装指南（Linux/macOS/WSL2）

本章面向 Linux、macOS 与 WSL2 用户，详细说明如何使用官方 `install.sh` 脚本完成 Hermes Agent 的一键安装，包括命令参数、安装阶段、目录布局以及安装后的验证方法。所有内容均以项目源码中的 `scripts/install.sh`、`setup-hermes.sh` 与 `README.md` 为准。

> 本章不涉及 Windows 原生安装（PowerShell `install.ps1`）、Docker 部署与 Termux 特殊路径，这些内容分别在后续章节中说明。

---

## 2.1 一键安装命令

### 2.1.1 标准一键安装

在终端中执行以下命令即可启动安装：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

该命令会下载安装脚本并通过 `bash` 执行。脚本会自动完成：

1. 检测操作系统与发行版；
2. 安装 `uv`（Python 包管理器）；
3. 准备 Python 3.11 运行时；
4. 检查并安装 Git、Node.js、ripgrep、ffmpeg 等依赖；
5. 克隆 `hermes-agent` 仓库；
6. 创建 Python 虚拟环境并安装全部依赖；
7. 安装 Node.js 依赖与 Playwright Chromium（浏览器工具所需）；
8. 将 `hermes` 命令链接到用户级 bin 目录；
9. 生成配置文件与初始技能；
10. 启动交互式设置向导（配置 API 密钥等）。

### 2.1.2 向安装脚本传递参数

当需要自定义安装行为时，通过 `bash -s --` 把参数传递给脚本：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-setup --skip-browser
```

`-s` 让 `bash` 从标准输入读取脚本，`--` 之后的所有内容都会作为脚本参数解析。

### 2.1.3 先下载再执行（便于审计与重试）

若希望在执行前审查脚本内容，或在网络不稳定时避免重复下载，可分两步执行：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh -o install.sh
less install.sh          # 可选：审查脚本内容
bash install.sh [选项]
```

### 2.1.4 安装完成后的第一步

脚本结束后，`hermes` 命令会被链接到 `~/.local/bin`（或 root FHS 布局下的 `/usr/local/bin`）。若当前 shell 尚未包含该路径，需要重新加载 shell 配置：

```bash
source ~/.bashrc    # Bash 用户
# 或
source ~/.zshrc     # Zsh 用户
# 或
source ~/.config/fish/config.fish   # Fish 用户
```

随后即可启动 Hermes：

```bash
hermes              # 进入交互式 CLI
```

---

## 2.2 安装脚本参数详解

`install.sh` 支持以下命令行参数。参数可单独使用，也可自由组合。

### 2.2.1 参数总览

| 参数 | 简写 | 说明 |
|---|---|---|
| `--no-venv` | — | 不创建 Python 虚拟环境，直接使用系统 Python |
| `--skip-setup` | — | 跳过安装末尾的交互式设置向导 |
| `--skip-browser` | `--no-playwright` | 跳过 Playwright/Chromium 安装（浏览器工具将不可用） |
| `--no-skills` | — | 空白启动：不植入任何捆绑技能，并写入禁用标记 |
| `--branch NAME` | `-Branch` | 指定要安装的 Git 分支（默认 `main`） |
| `--commit SHA` | `-Commit` | 将检出固定到指定 commit |
| `--force-commit` | `-ForceCommit` | 配合 `--commit` 使用，即使会回滚版本也强制检出 |
| `--dir PATH` | — | 指定代码安装目录 |
| `--hermes-home PATH` | — | 指定数据目录（配置、会话、日志等） |
| `--include-desktop` | `-IncludeDesktop` | 同时构建桌面应用（Electron） |
| `--non-interactive` | `-NonInteractive` | 跳过所有需要用户输入的阶段 |
| `--ensure DEPS` | — | 仅安装指定的系统依赖，不克隆仓库、不创建 venv |
| `--manifest` | `-Manifest` | 以 JSON 格式打印桌面引导阶段清单后退出 |
| `--stage NAME` | `-Stage` | 仅运行指定的桌面引导阶段 |
| `--json` | `-Json` | 配合 `--stage` 使用，输出 JSON 格式的阶段结果 |
| `-h`, `--help` | — | 显示帮助信息 |

### 2.2.2 环境与虚拟环境相关

#### `--no-venv`

不创建独立的 Python 虚拟环境，而是将 Hermes 安装到当前系统 Python 环境中。

```bash
bash install.sh --no-venv
```

适用场景：
- 你正在自行管理 Python 环境（如 conda、系统包管理器）；
- 容器化部署中希望复用基础镜像已有的 Python 环境。

注意事项：
- 使用该选项可能导致依赖冲突，Hermes 的依赖版本可能与系统中其他 Python 包冲突；
- 官方推荐始终使用虚拟环境安装，除非你明确知道自己在做什么。

#### `--hermes-home PATH`

指定 Hermes 的**数据目录**，存放配置、会话、日志、技能、缓存等用户数据。

```bash
bash install.sh --hermes-home /data/hermes
```

默认值：
- 普通用户：`$HOME/.hermes`（即 `~/.hermes`）；
- root 用户：`/root/.hermes`；
- 也可通过环境变量 `HERMES_HOME` 在安装前预设。

该选项**只影响数据目录**，不影响代码仓库的位置（代码位置由 `--dir` 控制）。

#### `--dir PATH`

指定 Hermes **代码仓库**的克隆与安装位置。

```bash
bash install.sh --dir /opt/hermes-agent
```

默认值：
- 非 root 用户：`$HERMES_HOME/hermes-agent`（通常为 `~/.hermes/hermes-agent`）；
- Linux root 用户（新安装）：`/usr/local/lib/hermes-agent`（FHS 布局）；
- Termux：`$HERMES_HOME/hermes-agent`。

一旦通过 `--dir` 显式指定，脚本绝不会自动覆盖该选择。注意代码目录与数据目录（`--hermes-home`）是分离的两个概念。

### 2.2.3 安装范围与组件控制

#### `--skip-setup`

跳过安装末尾自动启动的交互式设置向导（`hermes setup`）。

```bash
bash install.sh --skip-setup
```

适用场景：
- 自动化部署、CI/CD、Docker 构建等无 TTY 的环境；
- 你希望稍后手动运行 `hermes setup` 完成配置。

跳过设置向导后，可随时手动启动：

```bash
hermes setup
```

#### `--skip-browser`（别名 `--no-playwright`）

跳过 Playwright Chromium 浏览器的下载与系统依赖安装。

```bash
bash install.sh --skip-browser
```

影响：
- `browser_navigate` 等浏览器自动化工具将不可用；
- 可显著减少安装体积与下载时间（Chromium 约 150 MB）。

后续如需启用浏览器工具，手动执行：

```bash
cd ~/.hermes/hermes-agent    # 或你的 --dir 路径
npx playwright install chromium
# 在基于 apt 的系统上，管理员还需运行：
sudo npx playwright install-deps chromium
```

#### `--no-skills`

以"空白状态"启动：不植入任何捆绑技能（bundled skills），并在数据目录写入 `.no-bundled-skills` 标记文件。

```bash
bash install.sh --no-skills
```

行为说明：
- 安装后 `~/.hermes/skills/` 目录为空；
- 写入 `~/.hermes/.no-bundled-skills` 标记；
- 后续执行 `hermes update` 时也不会注入捆绑技能。

适用场景：
- 你只想要核心 CLI，不需要任何预置技能；
- 希望完全自定义技能集合。

如需恢复捆绑技能同步，删除标记文件后执行更新：

```bash
rm ~/.hermes/.no-bundled-skills
hermes update
```

#### `--include-desktop`

在 CLI 安装之外，额外构建 Hermes 桌面应用（基于 Electron）。

```bash
bash install.sh --include-desktop
```

该选项会：
1. 在仓库根目录执行 `npm ci`（安装 Electron 等桌面依赖，约 150 MB）；
2. 执行 `npm run pack` 构建当前平台的未打包应用；
3. Linux 上配置 `chrome-sandbox` 的 setuid 位；
4. macOS 上执行临时签名（ad-hoc signing）。

默认的 CLI 一键安装**不包含**桌面应用。Electron 桌面应用自身的首次启动引导会按需触发桌面构建，因此普通 CLI 用户无需使用此选项。

### 2.2.4 版本与源码控制

#### `--branch NAME`

指定要克隆的 Git 分支。

```bash
bash install.sh --branch develop
```

默认值为 `main`。更新已有安装时，脚本会将远端分支引用限定为该分支，避免拉取仓库中数千个自动生成分支导致的漫长下载。

#### `--commit SHA`

在克隆或更新后，将检出固定到指定的 commit SHA。

```bash
bash install.sh --commit abc1234def5678...
```

安全机制：
- 对于**已有安装**，如果指定的 commit 是当前 HEAD 的祖先（即会导致版本回滚），脚本默认**忽略**该参数并输出警告，避免旧版安装程序意外把新安装回滚到古老版本；
- 如需强制回滚，需同时传递 `--force-commit`；
- 对于**全新克隆**，不存在祖先关系，正常固定到指定 commit。

#### `--force-commit`

配合 `--commit` 使用，即使目标 commit 会导致版本回滚也强制执行检出。

```bash
bash install.sh --commit abc1234 --force-commit
```

### 2.2.5 自动化与桌面引导协议

#### `--non-interactive`

跳过所有需要用户交互的阶段（当前为 `setup` 与 `gateway` 两个阶段）。

```bash
bash install.sh --non-interactive
```

该选项与 `curl | bash` 的管道模式不同：管道模式下脚本会尝试通过 `/dev/tty` 读取输入，而 `--non-interactive` 会直接跳过交互式阶段。适用于完全无人值守的自动化安装。

#### `--manifest`

打印桌面引导阶段清单（JSON 格式）后退出，不执行实际安装。

```bash
bash install.sh --manifest
```

输出示例（结构）：

```json
{
  "protocol_version": 1,
  "stages": [
    {"name": "prerequisites", "title": "System prerequisites", "category": "runtime", "needs_user_input": false},
    {"name": "repository",    "title": "Download Hermes Agent",  "category": "runtime", "needs_user_input": false},
    {"name": "venv",          "title": "Create Python virtual environment", "category": "runtime", "needs_user_input": false},
    {"name": "python-deps",   "title": "Install Python dependencies", "category": "runtime", "needs_user_input": false},
    {"name": "node-deps",     "title": "Install browser-tool dependencies", "category": "runtime", "needs_user_input": false},
    {"name": "path",          "title": "Install hermes command", "category": "runtime", "needs_user_input": false},
    {"name": "config",        "title": "Prepare config and skills", "category": "configuration", "needs_user_input": false},
    {"name": "setup",         "title": "Configure API keys and settings", "category": "configuration", "needs_user_input": true},
    {"name": "gateway",       "title": "Configure gateway service", "category": "configuration", "needs_user_input": true},
    {"name": "desktop",       "title": "Build desktop app", "category": "runtime", "needs_user_input": false},
    {"name": "complete",      "title": "Finish install", "category": "runtime", "needs_user_input": false}
  ]
}
```

> `desktop` 阶段仅在传递 `--include-desktop` 时才会出现在清单中。

#### `--stage NAME`

仅运行指定的单个引导阶段，而非完整安装流程。

```bash
bash install.sh --stage python-deps
bash install.sh --stage setup
```

每个阶段在独立的子 shell 中运行，阶段失败不会阻止 JSON 结果帧输出。该机制主要供 Electron 桌面引导程序调用，用于展示结构化进度。

#### `--json`

配合 `--stage` 使用，以 JSON 格式输出阶段执行结果。

```bash
bash install.sh --stage python-deps --json
```

输出格式：

```json
{"ok":true,"stage":"python-deps","skipped":false}
```

失败时：

```json
{"ok":false,"stage":"python-deps","skipped":false,"reason":"exit code 1"}
```

#### `--ensure DEPS`

仅安装指定的系统依赖，**不克隆仓库、不创建虚拟环境、不安装 Python 包**。

```bash
bash install.sh --ensure node
bash install.sh --ensure ripgrep,ffmpeg
bash install.sh --ensure browser
```

支持的依赖项（逗号分隔）：

| 依赖 | 说明 |
|---|---|
| `node` | 安装 Hermes 托管的 Node.js 22 LTS |
| `browser` | 安装 Node.js 后，安装 `agent-browser` 与 Chromium |
| `ripgrep` | 通过系统包管理器安装 ripgrep（文件搜索） |
| `ffmpeg` | 通过系统包管理器安装 ffmpeg（TTS 语音消息） |

适用场景：已有安装损坏，需要单独修复某个依赖组件。

### 2.2.6 帮助

```bash
bash install.sh --help
```

显示完整的参数列表与默认路径说明。

---

## 2.3 安装过程详解

`install.sh` 的主流程（`main` 函数）按固定顺序执行以下步骤。理解每个阶段有助于诊断安装问题。

### 2.3.1 环境检测阶段

#### 操作系统检测（`detect_os`）

脚本通过 `uname -s` 判断操作系统：

- `Linux*`：进一步检测是否为 Termux（通过 `TERMUX_VERSION` 或 `$PREFIX` 路径）；普通 Linux 读取 `/etc/os-release` 获取发行版 ID（如 `ubuntu`、`debian`、`fedora`、`arch`）与版本号；
- `Darwin*`：识别为 macOS；
- `CYGWIN*`/`MINGW*`/`MSYS*`：识别为 Windows，脚本直接报错退出并提示使用 PowerShell 安装程序。

发行版信息用于后续选择正确的包管理器（`apt`/`dnf`/`pacman`/`brew`）。

#### 安装布局解析（`resolve_install_layout`）

根据用户身份与操作系统决定代码目录、命令链接目录：

- **普通用户（任意 OS）**：代码位于 `$HERMES_HOME/hermes-agent`，命令链接到 `~/.local/bin`；
- **Termux**：代码位于 `$HERMES_HOME/hermes-agent`，命令链接到 `$PREFIX/bin`（已在 PATH 上）；
- **Linux root（新安装）**：代码位于 `/usr/local/lib/hermes-agent`，命令链接到 `/usr/local/bin`（FHS 布局）；
- **Linux root（已有旧版安装）**：保留 `$HERMES_HOME/hermes-agent` 旧布局；
- **macOS root**：不使用 FHS 布局，沿用用户级目录（避免与 Homebrew 冲突）。

### 2.3.2 依赖安装阶段

#### uv 安装（`install_uv`）

Hermes 使用 [uv](https://docs.astral.sh/uv/) 作为 Python 包管理器。脚本将 uv 安装到 `$HERMES_HOME/bin/uv`（Hermes 自托管位置），而非系统 PATH，避免与用户已有的 uv 冲突。

- Termux 例外：不使用 uv，改用 Python 标准库 `venv` + `pip`；
- 若 `$HERMES_HOME/bin/uv` 已存在，直接复用；
- 安装采用两阶段下载（先下载安装脚本到临时文件，再执行），避免 `curl | sh` 掩盖网络错误。

#### Python 检测与安装（`check_python`）

目标版本为 **Python 3.11**。

- 非 Termux：先通过 `uv python find 3.11` 查找系统已有 Python；未找到则由 `uv python install 3.11` 自动下载安装（无需 sudo）；
- Termux：检查系统 Python 是否 ≥ 3.11，不满足则通过 `pkg install python` 安装。

脚本还会清除继承的 `PYTHONPATH` 与 `PYTHONHOME` 环境变量，并设置 `UV_NO_CONFIG=1`，防止外部环境污染安装过程。

#### Git 检测与安装（`check_git`）

Git 是克隆仓库的必需工具。脚本会：

1. 检查 `git --version` 是否可用（注意：macOS 全新系统上 `/usr/bin/git` 是一个桩程序，需安装 Xcode CLT 后才能真正使用）；
2. 若不可用，尝试自动安装：
   - **macOS**：优先 `brew install git`；否则触发 `xcode-select --install`（会弹出系统对话框）并轮询等待完成；
   - **Linux**：根据发行版调用 `apt`/`dnf`/`pacman` 安装；
   - **Termux**：`pkg install git`；
3. 自动安装失败时，输出对应平台的手动安装命令并退出。

#### Node.js 检测与安装（`check_node`）

Node.js 用于浏览器工具与 TUI 构建，最低版本要求为 **Node.js ≥ 22.22.0**（由 `react-router` 的 `engines.node` 决定）。

检测逻辑：
1. 若系统 Node 满足版本要求且 npm 不在有缺陷的版本带（npm 11.10–11.16），直接使用系统 Node；
2. 否则使用 Hermes 托管的 Node.js 22 LTS，安装到 `$HERMES_HOME/node/`，并将 `node`/`npm`/`npx` 符号链接到命令目录；
3. Termux 通过 `pkg install nodejs` 安装。

托管 Node 的架构支持 `x64`、`arm64`、`armv7l`。

#### 网络连通性检查（`check_network_prerequisites`）

并行探测 `https://pypi.org/simple/` 与 `https://duckduckgo.com/`（各 8 秒超时）。检查失败仅输出警告，不中断安装——因为安装本身可能使用内部镜像，但后续 Web 搜索与依赖下载可能受影响。

#### 系统包安装（`install_system_packages`）

检测并安装两个可选但推荐的系统工具：

| 工具 | 用途 | 缺失时的影响 |
|---|---|---|
| `ripgrep`（`rg`） | 快速文件搜索 | 回退到 `grep`，大代码库中较慢 |
| `ffmpeg` | TTS 语音消息处理 | 语音功能受限 |

安装策略按平台与权限分级：
- **macOS**：通过 Homebrew 安装；
- **Linux root**：直接通过包管理器安装；
- **Linux 普通用户 + 免密 sudo**：通过 sudo 安装；
- **Linux 普通用户 + 需密码 sudo**：交互式询问是否安装；
- **ripgrep 兜底**：若系统包管理器失败，尝试 `cargo install ripgrep`；
- **Termux**：一次性安装 `clang rust make pkg-config libffi openssl ca-certificates curl` 等编译工具链。

### 2.3.3 仓库克隆阶段（`clone_repo`）

仓库地址：
- SSH：`git@github.com:NousResearch/hermes-agent.git`
- HTTPS：`https://github.com/NousResearch/hermes-agent.git`

克隆策略：
1. **全新安装**：先尝试 SSH 克隆（`BatchMode=yes`，5 秒超时，无密钥则快速失败），失败后回退到 HTTPS；使用 `--depth 1 --branch "$BRANCH"` 浅克隆；
2. **已有安装**：
   - 丢弃 npm lockfile 的非确定性改动；
   - 若有未提交的本地改动，先 `git stash`（包含未跟踪文件）；
   - 仅拉取目标分支（`git remote set-branches`），避免下载数千个自动生成分支；
   - `git pull --ff-only`，若无法快进（本地有分叉）则 `git reset --hard origin/$BRANCH`；
   - 更新后交互式询问是否恢复 stash 的本地改动；
3. **中断的克隆**：若 `.git` 存在但无 HEAD（上次克隆中断），将目录重命名为 `.broken-<时间戳>` 后重新克隆，不删除用户数据；
4. **Commit 固定**：若指定了 `--commit`，克隆后执行 `git checkout --detach <sha>`（受祖先检查保护，见 2.2.4 节）。

### 2.3.4 虚拟环境创建阶段（`setup_venv`）

- 若传递了 `--no-venv`，跳过此阶段；
- Termux：使用 `python -m venv venv`；
- 其他平台：使用 `uv venv venv --python 3.11`；
- 若 `venv/` 已存在，先删除再重建（确保干净状态）；
- 创建后将 `UV_PYTHON` 环境变量固定到 venv 解释器，防止继承的 `UV_PYTHON`（如 3.14）导致 uv 在后续安装中重建 venv。

### 2.3.5 Python 依赖安装阶段（`install_deps`）

依赖安装采用多层级回退策略，兼顾供应链安全与鲁棒性：

**Tier 0：哈希验证安装（首选）**

当仓库中存在 `uv.lock` 时，执行：

```bash
uv sync --extra all --locked
```

`uv.lock` 记录了每个传递依赖的 SHA256 哈希，可防御 PyPI 包被投毒的供应链攻击。这是唯一具备传递依赖哈希保护的安装路径。

**Tier 1–3：PyPI 重新解析（回退）**

若 lockfile 同步失败（lockfile 过期或与 extras 不同步），依次尝试：

1. `uv pip install -e ".[all]"`：安装 `pyproject.toml` 中精选的 `[all]` extra；
2. `uv pip install -e ".[all-minus-broken]"`：从 `[all]` 中排除当前不可用的 extras；
3. `uv pip install -e "."`：仅安装核心包，确保至少 CLI 能启动。

Termux 使用专门的 `.[termux-all]` → `.[termux]` → `.` 三级回退，并配合 `constraints-termux.txt` 约束版本。

Debian/Ubuntu（含 WSL）上，脚本还会检测并安装 `build-essential python3-dev libffi-dev`，以编译需要原生扩展的 Python 包。

### 2.3.6 Node.js 依赖与浏览器安装阶段（`install_node_deps`）

1. 在仓库根目录执行 `npm install`（600 秒超时），安装浏览器工具所需的 Node 依赖；
2. 安装 Playwright Chromium：
   - **apt 系发行版**（Ubuntu/Debian/Pop!_OS/Mint/Kali 等）：`npx playwright install --with-deps chromium`（root 或免密 sudo 时自动安装系统库；否则仅安装 Chromium 二进制，提示管理员手动运行 `install-deps`）；
   - **Arch 系**：通过 `pacman` 安装 Chromium 系统库后再安装浏览器；
   - **Fedora/RHEL/CentOS/Rocky/Alma**：提示手动 `dnf install` 系统库；
   - **openSUSE**：提示手动 `zypper install` 系统库；
   - 对于 Playwright 尚不识别的过新 apt 发行版（如 Ubuntu 26.04、Debian 14），自动使用 `PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64` 回退；
3. 在 `ui-tui/` 目录执行 `npm install`，安装 TUI 终端界面依赖；
4. 恢复被 npm 非确定性修改的 lockfile，保持仓库干净。

若设置了 `AGENT_BROWSER_EXECUTABLE_PATH` 环境变量且指向有效的非 Snap 浏览器，则跳过 Chromium 下载，使用指定浏览器。Snap 版 Chromium 因沙箱限制会被明确拒绝。

### 2.3.7 PATH 配置与命令链接（`setup_path`）

在命令链接目录创建三个启动脚本（而非简单符号链接）：

| 命令 | 用途 |
|---|---|
| `hermes` | 主 CLI 入口 |
| `hermes-agent` | 直接运行 agent 入口（`run_agent.py`） |
| `hermes-acp` | 以 ACP（Agent Client Protocol）模式启动，供 Zed/JetBrains 等编辑器集成 |

每个启动脚本都会在执行前 `unset PYTHONPATH` 和 `unset PYTHONHOME`，防止外部环境污染。

若命令目录不在 PATH 上，脚本会自动检测用户的登录 shell（bash/zsh/fish）并向对应配置文件追加 PATH 导出语句：
- bash：`~/.bashrc`、`~/.bash_profile`、`~/.profile`
- zsh：`~/.zshrc`、`~/.zprofile`
- fish：`~/.config/fish/config.fish`（使用 `fish_add_path`）

RHEL/CentOS/Rocky/Alma 上的 root 用户可能在非登录 shell 中丢失 `/usr/local/bin`，脚本会专门向 `/root/.bashrc` 写入 PATH 守护行。

### 2.3.8 配置文件与技能初始化（`copy_config_templates`）

在 `$HERMES_HOME` 下创建标准目录结构并初始化配置文件（详见 2.4 节）。

- `.env`：从仓库的 `.env.example` 复制，权限设为 `0600`（仅所有者可读写），存储 API 密钥与令牌；
- `config.yaml`：从 `cli-config.yaml.example` 复制，存储 CLI 行为配置；
- `SOUL.md`：全局人格文件，包含默认的 agent 人设，可编辑自定义；
- 同步捆绑技能到 `skills/`（受 `--no-skills` 控制）。

### 2.3.9 设置向导与网关（可选）

- **设置向导**（`run_setup_wizard`）：若未指定 `--skip-setup` 且 `/dev/tty` 可用，运行 `hermes setup`，引导用户配置 LLM 提供商、API 密钥等。向导从 `/dev/tty` 读取输入，因此即使脚本通过 `curl | bash` 管道执行也能正常交互；
- **网关配置**（`maybe_start_gateway`）：若检测到 `.env` 中配置了 Telegram/Discord/Slack/WhatsApp 等消息平台令牌，询问是否将网关安装为 systemd 服务（或在无 systemd 时以后台进程启动）。

### 2.3.10 完成标记

安装成功后，脚本会：

1. 在代码目录写入 `.hermes-bootstrap-complete`（JSON 格式，包含 `schemaVersion`、`pinnedCommit`、`pinnedBranch`、`completedAt`），告知桌面应用"首次引导已完成"；
2. 在代码目录写入 `.install_method`（内容为 `git`），供 `hermes update` 识别安装方式；
3. 打印安装完成横幅，列出配置文件位置与常用命令。

---

## 2.4 安装后目录结构说明（`~/.hermes/`）

Hermes 将**用户数据**与**代码仓库**分离存储。默认布局（普通用户）如下：

```
~/.hermes/                          # HERMES_HOME — 用户数据根目录
├── .env                            # API 密钥与令牌（权限 0600）
├── config.yaml                     # CLI 行为配置
├── SOUL.md                         # 全局人格定义（可编辑）
├── .no-bundled-skills              # 存在时表示禁用捆绑技能（仅 --no-skills 安装时）
├── cron/                           # 定时任务定义与状态
├── sessions/                       # 对话会话记录（FTS5 全文索引）
├── logs/                           # 运行日志（含 gateway.log）
├── pairing/                        # 设备/平台配对信息
├── hooks/                          # 生命周期钩子脚本
├── image_cache/                    # 图片缓存
├── audio_cache/                    # 音频/语音缓存
├── memories/                       # Agent 持久化记忆
├── skills/                         # 用户技能库（捆绑技能 + 自建技能）
├── bin/
│   └── uv                          # Hermes 自托管的 uv 二进制
├── node/                           # Hermes 托管的 Node.js 运行时
│   ├── bin/
│   │   ├── node
│   │   ├── npm
│   │   └── npx
│   └── etc/
│       └── npmrc                   # 托管 Node 的 npm 全局前缀配置
└── hermes-agent/                   # 代码仓库（INSTALL_DIR）
    ├── venv/                       # Python 虚拟环境
    │   └── bin/
    │       ├── python
    │       ├── hermes              # uv 生成的 console script
    │       ├── hermes-agent
    │       └── hermes-acp
    ├── .git/                       # Git 仓库元数据
    ├── pyproject.toml              # Python 项目定义与依赖声明
    ├── uv.lock                     # 依赖锁文件（哈希验证）
    ├── package.json                # Node.js 依赖声明
    ├── .env.example                # 环境变量模板
    ├── cli-config.yaml.example     # CLI 配置模板
    ├── hermes                      # 仓库内启动入口脚本
    ├── run_agent.py                # agent 直接入口
    ├── skills/                     # 捆绑技能源目录
    ├── tools/                      # 工具实现
    ├── hermes_cli/                 # CLI 主模块
    ├── gateway/                    # 消息网关
    ├── ui-tui/                     # 终端 UI（Node.js）
    ├── apps/
    │   └── desktop/                # Electron 桌面应用（仅 --include-desktop 构建）
    ├── .hermes-bootstrap-complete  # 引导完成标记
    └── .install_method             # 安装方式标记（值为 git）
```

### 2.4.1 关键文件说明

| 路径 | 用途 | 备注 |
|---|---|---|
| `~/.hermes/.env` | 存储所有 API 密钥与令牌 | 权限 `0600`，不要提交到版本控制 |
| `~/.hermes/config.yaml` | CLI 行为配置（模型、工具、个性等） | 可通过 `hermes config` 命令编辑 |
| `~/.hermes/SOUL.md` | Agent 的系统人设/人格定义 | 用户可自由编辑 |
| `~/.hermes/sessions/` | 历史对话记录 | 支持 FTS5 全文搜索 |
| `~/.hermes/memories/` | Agent 自主沉淀的长期记忆 | 由记忆系统自动管理 |
| `~/.hermes/skills/` | 技能库 | 兼容 [agentskills.io](https://agentskills.io) 标准 |
| `~/.hermes/logs/gateway.log` | 消息网关日志 | 排查 Telegram/Discord 等问题时查看 |
| `~/.hermes/hermes-agent/venv/` | Python 虚拟环境 | 所有 Python 依赖隔离于此 |

### 2.4.2 数据目录与代码目录的分离

`HERMES_HOME`（数据）与 `INSTALL_DIR`（代码）是两个独立概念：

- **数据目录**（`~/.hermes/`）包含配置、会话、密钥等用户私有数据，不会在 `hermes update` 时被覆盖；
- **代码目录**（`~/.hermes/hermes-agent/`）是 Git 仓库，更新时通过 `git pull`/`git reset` 同步。

这种分离使得：
- Docker 容器可以 bind-mount 数据目录而保持代码在镜像内；
- root FHS 安装可以将代码放在系统目录而数据保留在 `/root/.hermes`；
- 卸载时只需删除代码目录即可保留用户数据。

---

## 2.5 root 用户 FHS 布局说明

### 2.5.1 什么是 FHS 布局

在 Linux 上以 `root` 用户身份运行安装脚本时，Hermes 采用符合**文件系统层次标准（FHS, Filesystem Hierarchy Standard）**的安装布局，与 Claude Code、Codex CLI 等工具的布局一致：

| 组件 | 路径 | 说明 |
|---|---|---|
| 代码 | `/usr/local/lib/hermes-agent` | 仓库克隆与虚拟环境位置 |
| 命令 | `/usr/local/bin/hermes` | 全局可用的启动脚本 |
| 数据 | `/root/.hermes` | HERMES_HOME，配置与会话（不变） |
| uv Python | `/usr/local/share/uv/python` | uv 管理的 Python 解释器（全局可读） |
| uv 二进制 | `/usr/local/share/uv/bin` | uv 相关二进制 |

### 2.5.2 触发条件

FHS 布局仅在**同时满足**以下条件时启用：

1. 操作系统为 Linux（macOS root 不启用，因为 `/usr/local/` 是 Homebrew 的领地）；
2. 当前用户为 root（`id -u` 等于 0）；
3. 不存在旧版安装：`/root/.hermes/hermes-agent/.git` 目录不存在。

若检测到旧版安装已存在于 `/root/.hermes/hermes-agent`，脚本会保留旧布局，仅输出提示信息，不会强制迁移。

### 2.5.3 为什么需要 FHS 布局

1. **命令全局可用**：`/usr/local/bin` 默认在所有用户的 PATH 上，无需修改 shell 配置；
2. **Docker 卷轻量化**：数据目录 `/root/.hermes` 可被 bind-mount，而代码在镜像层中，保持挂载卷小巧；
3. **多用户共享**：系统中所有用户都能执行 `hermes` 命令（但数据仍各自隔离在自己的 `$HOME/.hermes`）；
4. **权限正确性**：uv 管理的 Python 安装在 `/usr/local/share/uv/python`，对所有用户可读可执行。若放在默认的 `/root/.local/share/uv`，非 root 用户无法遍历目录，导致 `/usr/local/bin/hermes` 无法执行 venv 中的 Python 解释器。

### 2.5.4 PATH 处理

FHS 布局下 `/usr/local/bin` 通常已在登录 shell 的 PATH 上（通过 `/etc/profile` 的 `pathmunge`）。但在 RHEL/CentOS/Rocky/Alma 8+ 上，非登录交互式 root shell（如 `su`、`sudo -s`、tmux 窗格、部分 Web 终端）只 source `/etc/bashrc` 而不 source `/etc/profile`，可能丢失 `/usr/local/bin`。

脚本会通过 `bash -i -c 'command -v hermes'` 探测这种情况，若发现 `hermes` 不在 PATH 上，会向 `/root/.bashrc` 和 `/root/.bash_profile` 写入：

```bash
# Hermes Agent — ensure /usr/local/bin is on PATH (RHEL non-login shells)
export PATH="/usr/local/bin:$PATH"
```

### 2.5.5 强制使用非 FHS 布局

若你是 root 用户但希望在 Linux 上使用旧的用户级布局，可通过 `--dir` 显式指定：

```bash
bash install.sh --dir /root/.hermes/hermes-agent
```

一旦显式指定 `--dir`，脚本不会覆盖该选择。

---

## 2.6 安装后验证

安装完成后，按以下步骤验证 Hermes Agent 是否正常工作。

### 2.6.1 重新加载 Shell

若 `hermes` 命令尚未生效，重新加载 shell 配置：

```bash
source ~/.bashrc     # Bash
# 或
source ~/.zshrc      # Zsh
# 或
source ~/.config/fish/config.fish   # Fish
```

root FHS 布局下通常无需此步骤，`/usr/local/bin` 已在 PATH 上。

### 2.6.2 验证命令可用性

```bash
command -v hermes
```

预期输出类似：

```
/home/youruser/.local/bin/hermes
```

或 root FHS 布局：

```
/usr/local/bin/hermes
```

### 2.6.3 运行诊断命令

```bash
hermes doctor
```

`hermes doctor` 会检查：
- Python 环境与依赖完整性；
- Node.js 与浏览器工具状态；
- 配置文件与 API 密钥；
- 网络连通性；
- 系统依赖（ripgrep、ffmpeg、git）；
- 权限与目录结构。

根据输出修复任何标记为错误的项目。

### 2.6.4 检查配置状态

```bash
hermes status
```

查看当前配置的模型提供商、启用的工具、网关状态等信息。

### 2.6.5 配置 API 密钥

若安装时跳过了设置向导（`--skip-setup`），手动运行：

```bash
hermes setup
```

向导会引导你：
1. 选择 LLM 提供商（Nous Portal、OpenRouter、OpenAI、自定义端点等）；
2. 输入 API 密钥；
3. 配置可选工具（Web 搜索、图片生成、TTS 等）；
4. 设置消息平台（可选）。

也可以使用 Nous Portal 一键配置：

```bash
hermes setup --portal
```

### 2.6.6 启动首次对话

```bash
hermes
```

这会进入交互式终端界面（TUI）。输入一条简单消息（如"你好"）验证模型是否正常响应。使用 `/new` 开始新对话，`Ctrl+C` 中断当前输出。

### 2.6.7 验证浏览器工具（可选）

若安装时未跳过浏览器，在 Hermes 会话中尝试：

```
/browser_navigate https://example.com
```

若浏览器正常启动并加载页面，说明 Playwright Chromium 安装成功。

### 2.6.8 验证消息网关（可选）

若在设置向导中配置了 Telegram/Discord 等平台令牌，安装并启动网关：

```bash
hermes gateway install     # 安装为 systemd 服务（Linux）
hermes gateway start       # 启动服务
hermes gateway status      # 查看运行状态
```

Termux 或无 systemd 的环境使用：

```bash
hermes gateway             # 前台运行
# 或后台运行
nohup hermes gateway > ~/.hermes/logs/gateway.log 2>&1 &
```

### 2.6.9 验证文件结构

确认关键文件已正确生成：

```bash
ls -la ~/.hermes/.env ~/.hermes/config.yaml ~/.hermes/SOUL.md
ls -d ~/.hermes/hermes-agent/venv ~/.hermes/skills ~/.hermes/sessions
```

`.env` 文件权限应为 `-rw-------`（0600）：

```bash
stat -c '%a %n' ~/.hermes/.env
# 预期输出：600 /home/youruser/.hermes/.env
```

### 2.6.10 更新与卸载提示

后续更新到最新版本：

```bash
hermes update
```

如需卸载，删除代码目录与命令链接即可保留用户数据：

```bash
rm -rf ~/.hermes/hermes-agent
rm -f ~/.local/bin/hermes ~/.local/bin/hermes-agent ~/.local/bin/hermes-acp
```

若要彻底清除所有数据（包括配置、会话、记忆），额外删除 `~/.hermes`：

```bash
rm -rf ~/.hermes
```

---

## 2.7 小结

官方 `install.sh` 脚本为 Linux、macOS 与 WSL2 提供了全自动的安装体验，核心设计要点包括：

- **零 root 依赖**：普通用户即可完成全部安装，uv 与 Node.js 均安装在用户目录下；
- **供应链安全**：优先使用 `uv.lock` 进行哈希验证的依赖安装，多层级回退保证鲁棒性；
- **数据与代码分离**：`$HERMES_HOME` 存储用户数据，Git 仓库存储代码，便于更新与备份；
- **root FHS 布局**：Linux root 安装自动采用 `/usr/local/lib` + `/usr/local/bin` 的标准布局；
- **幂等可重入**：重复运行脚本会更新已有安装，自动处理本地改动 stash 与 lockfile 清理；
- **自动化友好**：`--non-interactive`、`--skip-setup`、`--ensure` 等参数支持无人值守部署。

下一章将介绍 Windows 平台的 PowerShell 安装脚本（`install.ps1`）。
