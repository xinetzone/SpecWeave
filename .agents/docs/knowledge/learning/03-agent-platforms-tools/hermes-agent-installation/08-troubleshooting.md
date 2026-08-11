---
title: "Hermes Agent 安装方案 - 常见问题与故障排除"
chapter: 8
source:
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/package.json
  - external/libs/hermes-agent/.npmrc
  - external/libs/hermes-agent/Dockerfile
  - external/libs/hermes-agent/docker-compose.yml
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/scripts/install.ps1
  - external/libs/hermes-agent/hermes_cli/doctor.py
  - external/libs/hermes-agent/hermes_cli/logs.py
  - external/libs/hermes-agent/hermes_cli/uninstall.py
  - external/libs/hermes-agent/docker/entrypoint-dispatch.sh
  - external/libs/hermes-agent/docker/stage2-hook.sh
---

# 8. 常见问题与故障排除

本章汇总 Hermes Agent 在安装、启动和运行过程中的常见问题，按问题类别组织。每个问题包含【症状】【原因】【解决方案】三部分，便于快速定位和修复。遇到问题时，建议首先运行 `hermes doctor` 进行自动诊断（详见 [第 9 节](#9-日志查看与诊断方法)）。

> **排查原则**：先运行 `hermes doctor` 获取环境全景报告；多数配置类、路径类、依赖类问题都能被 doctor 直接识别。`hermes doctor --fix` 可自动修复一部分问题（损坏的 CA 证书、缺失的符号链接、过时的配置迁移等）。

---

## 8.1 网络问题

网络问题是安装失败最常见的原因。Hermes 安装过程需要访问 GitHub（源码克隆）、PyPI（Python 包）、npm registry（Node 包）、Playwright CDN（浏览器二进制）以及模型 API 端点。

### 8.1.1 GitHub 访问慢或失败

**【症状】**

- `git clone https://github.com/NousResearch/hermes-agent.git` 超时或连接重置。
- 安装脚本在"Download Hermes Agent"阶段长时间无响应后报错。
- Docker 构建时拉取 s6-overlay、sqlite 源码或 Node 二进制失败。
- 错误信息包含 `Connection timed out`、`Failed to connect`、`Could not resolve host: github.com`。

**【原因】**

GitHub 在部分网络环境下访问不稳定。安装脚本和 Dockerfile 需要从 GitHub 拉取以下资源：

- 仓库源码（`github.com/NousResearch/hermes-agent`）
- s6-overlay 二进制包（`github.com/just-containers/s6-overlay/releases`，仅 Docker）
- uv 安装脚本（`astral.sh`，非 GitHub 但同样可能被墙）

**【解决方案】**

1. **配置 Git 代理**（推荐）：
   ```bash
   git config --global http.proxy http://127.0.0.1:7890
   git config --global https.proxy http://127.0.0.1:7890
   ```

2. **使用镜像站克隆**（如果有可用镜像）：
   ```bash
   git clone https://gitcode.com/mirrors/hermes-agent.git ~/.hermes/hermes-agent
   ```
   然后手动将远程地址改回官方仓库以便后续更新：
   ```bash
   cd ~/.hermes/hermes-agent
   git remote set-url origin https://github.com/NousResearch/hermes-agent.git
   ```

3. **Docker 构建时配置代理**：
   ```bash
   docker build \
     --build-arg HTTP_PROXY=http://host.docker.internal:7890 \
     --build-arg HTTPS_PROXY=http://host.docker.internal:7890 \
     -t hermes-agent .
   ```

4. **增大 Git 缓冲区并启用低速重试**：
   ```bash
   git config --global http.postBuffer 524288000
   git config --global http.lowSpeedLimit 1000
   git config --global http.lowSpeedTime 60
   ```

5. 检查 DNS 解析：`nslookup github.com`，必要时更换为公共 DNS（如 `8.8.8.8` 或 `223.5.5.5`）。

### 8.1.2 PyPI 下载超时

**【症状】**

- `uv sync` 或 `pip install` 阶段卡住，报 `ReadTimeoutError`、`ConnectionResetError`。
- 下载速度极慢（每秒几 KB），最终超时。
- 错误信息包含 `Failed to download`、`timed out`。

**【原因】**

PyPI 官方源（`pypi.org`）在部分地区访问速度慢。Hermes 的 Python 依赖较多（含 cryptography、pydantic、Pillow 等带原生扩展的包），下载量大。

**【解决方案】**

1. **使用国内 PyPI 镜像**（以清华镜像为例）：
   ```bash
   export UV_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple
   # 或永久配置 uv
   uv config set index-url https://pypi.tuna.tsinghua.edu.cn/simple
   ```
   安装脚本通过 uv 安装 Python 依赖，设置 `UV_INDEX_URL` 即可让安装过程使用镜像。

2. **pip 用户**：
   ```bash
   pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
   ```

3. **增大超时时间**：
   ```bash
   export UV_HTTP_TIMEOUT=300
   ```

4. Termux 用户如遇镜像过期，可执行 `termux-change-repo` 切换 Termux 包镜像。

### 8.1.3 npm 安装失败

**【症状】**

- `npm install` 或 `npm ci` 报 `ETARGET`、`EBADENGINE`、`EACCES`、`SELF_SIGNED_CERT_IN_CHAIN`。
- 安装过程在 Electron 或 node-pty 的 postinstall 阶段失败。
- 错误信息包含 `unable to get local issuer certificate`。

**【原因】**

可能的原因有多种：

1. **npm 版本不兼容**：npm `11.10.0`–`11.16.x` 存在 bug，能识别 `min-release-age` 但忽略 `min-release-age-exclude`，导致新发布的依赖被 14 天冷却期拦截（见 `.npmrc` 配置）。项目 `package.json` 的 `engines.npm` 明确排除了这个版本段。
2. **TLS 证书拦截**：企业代理或杀毒软件进行 HTTPS 中间人拦截，Node.js 不信任其根证书。
3. **网络超时**：npm registry 访问慢。
4. **权限不足**：全局安装时遇到 EACCES。

**【解决方案】**

1. **检查 npm 版本**：
   ```bash
   npm --version
   ```
   若版本在 `11.10.0`–`11.16.x` 之间，升级 npm：
   ```bash
   npm install -g npm@latest
   ```
   Hermes 托管的 Node 会在安装时自动升级 npm 到满足 `engines.npm` 要求的版本。

2. **TLS 证书问题**（企业网络常见）：
   - 从 IT 部门获取企业根 CA 证书（`.pem` 格式）。
   - 设置环境变量：
     ```powershell
     # Windows PowerShell
     setx NODE_EXTRA_CA_CERTS "C:\path\to\corp-ca.pem"
     ```
     ```bash
     # Linux/macOS
     export NODE_EXTRA_CA_CERTS=/path/to/corp-ca.pem
     ```
   - 打开**新**终端后重新运行安装。
   - 临时绕过（仅限排查，不推荐长期使用）：
     ```bash
     npm config set strict-ssl false
     # 安装完成后务必恢复
     npm config set strict-ssl true
     ```

3. **使用 npm 镜像**：
   ```bash
   npm config set registry https://registry.npmmirror.com
   ```

4. **权限问题**见 [8.5.2 节](#852-eacces-权限拒绝)。

### 8.1.4 模型 API 连接问题

**【症状】**

- 启动对话后报 `APIConnectionError`、`APITimeoutError`、`AuthenticationError`。
- `hermes doctor` 的"API Connectivity"部分显示某个提供商连接失败。
- 错误信息包含 `Connection refused`、`Name or service not known`、`401 Unauthorized`、`403 Forbidden`。

**【原因】**

1. API Key 未配置或错误。
2. 自定义 `BASE_URL` 配置错误（末尾多斜杠、域名拼写错误）。
3. 网络无法访问模型 API 端点（需代理或在中国大陆需用国内端点）。
4. API Key 已过期或额度用尽。
5. SSL CA 证书损坏（见 [8.5.1 节](#851-sudo-使用注意事项) 中证书问题的通用处理）。

**【解决方案】**

1. **检查 API Key 配置**：
   ```bash
   # 查看当前配置
   hermes config get model.provider
   # 运行交互式设置
   hermes setup
   ```
   确认 `~/.hermes/.env`（Windows 为 `%LOCALAPPDATA%\hermes\.env`）中对应的 API Key 已设置且无多余空格或引号。

2. **检查 BASE_URL**：
   若使用第三方中转或代理，确认 `OPENAI_BASE_URL`（或对应提供商的 `_BASE_URL`）格式正确：
   ```bash
   # 正确示例（末尾不要加 /v1 除非文档明确要求）
   OPENAI_BASE_URL=https://api.openai.com
   # 错误示例
   # OPENAI_BASE_URL=https://api.openai.com/v1/chat/completions
   ```

3. **测试连通性**：
   ```bash
   curl -I https://api.openai.com
   curl -I https://openrouter.ai
   ```
   若超时，配置 `HTTPS_PROXY` 环境变量。

4. **验证 Key 有效性**：
   ```bash
   curl -H "Authorization: Bearer $OPENAI_API_KEY" https://api.openai.com/v1/models
   ```
   返回 401 说明 Key 无效；返回模型列表说明网络和 Key 均正常。

5. **运行 doctor 诊断**：
   ```bash
   hermes doctor
   ```
   "Auth Providers"和"API Connectivity"两节会逐项检测各提供商的认证和连通状态。

---

## 8.2 Python 版本问题

### 8.2.1 Python 3.14 不被支持

**【症状】**

- 安装时报错：`The requested Python version >=3.11,<3.14 is not satisfied by 3.14.0`。
- uv 拒绝使用 Python 3.14 创建虚拟环境。
- 若绕过版本检查手动安装，在编译 `pydantic-core` 等 Rust 扩展时报 maturin 构建失败。

**【原因】**

`pyproject.toml` 中明确声明 `requires-python = ">=3.11,<3.14"`（pyproject.toml:15）。上界 `<3.14` 是**承重约束**，不是装饰性限制：

- Python 3.14 发布时间尚短，多个 Rust 后端的传递依赖（如 `pydantic-core`）尚未提供 cp314 的预编译 wheel。
- 在没有 wheel 的情况下，uv/pip 会回退到从源码构建，需要 maturin + Rust 工具链，且这些包的源码尚未适配 3.14 的 C API 变更，构建必然失败。
- 项目注释明确说明：等 Rust 传递依赖发布 cp314 wheel 后才会提升上界。

**【解决方案】**

1. **使用 Python 3.11、3.12 或 3.13**（推荐 3.11 或 3.13）。
2. 安装脚本默认使用 Python 3.11，会通过 uv 自动下载和管理对应版本，无需手动卸载 3.14。
3. 若系统已通过 `UV_PYTHON` 环境变量指定了 3.14，取消该变量：
   ```bash
   unset UV_PYTHON
   ```
4. 若你是开发者想在 3.14 上实验性运行，需自行安装 Rust 工具链并等待上游适配，但这**不受官方支持**。

### 8.2.2 找不到合适的 Python 版本

**【症状】**

- 安装脚本报 `Python 3.11 not found`，自动安装也失败。
- `uv python find 3.11` 返回空结果。
- Windows 上运行 `python --version` 弹出 Microsoft Store。

**【原因】**

1. 系统未安装 Python 3.11+，且 uv 自动下载失败（网络问题）。
2. Windows 上 `python` 命令指向 Microsoft Store 的 0 字节存根（`%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe`），而非真实 Python。
3. 多版本 Python 共存时，PATH 顺序导致找到错误版本。
4. uv 的 Python 安装目录权限问题。

**【解决方案】**

1. **让安装脚本自动处理**（推荐）：官方安装脚本使用 uv 自动下载 Python 到 `~/.hermes/bin/`（或 `%LOCALAPPDATA%\hermes\bin\`），不需要系统预装 Python。若自动下载失败，检查网络（见 [8.1 节](#81-网络问题)）。

2. **Windows 用户注意 Microsoft Store 存根**：
   - 转到"设置 → 应用 → 应用别名"，关闭 `python.exe` 和 `python3.exe` 的应用执行别名。
   - 或直接从 [python.org](https://www.python.org/downloads/) 安装 Python 3.11+，安装时勾选"Add Python to PATH"。

3. **手动指定 Python 路径**：
   ```bash
   # 查看 uv 能找到的所有 Python
   uv python list
   # 指定版本安装
   uv python install 3.13
   ```

4. **macOS 用户**可使用 Homebrew：
   ```bash
   brew install python@3.13
   ```

5. **Linux 用户**：
   ```bash
   # Ubuntu/Debian
   sudo apt install python3.11 python3.11-venv
   # Fedora
   sudo dnf install python3.11
   ```

### 8.2.3 多 Python 版本冲突

**【症状】**

- `hermes --version` 显示的 Python 版本与预期不符。
- 安装了依赖但运行时仍报 `ModuleNotFoundError`。
- conda/anaconda 环境与系统 Python 冲突。
- `hermes doctor` 显示的 Python 路径不是虚拟环境中的路径。

**【原因】**

1. 系统存在多个 Python（系统自带、Homebrew、pyenv、conda、uv 管理的），PATH 顺序导致 `python` 解析到错误版本。
2. 继承了 `PYTHONPATH` 或 `PYTHONHOME` 环境变量，导致导入了非虚拟环境中的包（安装脚本会主动清除这两个变量，但手动运行时可能存在）。
3. conda 环境未正确停用。
4. 虚拟环境损坏或指向了已删除的 Python。

**【解决方案】**

1. **确认使用的是正确的解释器**：
   ```bash
   which python
   python --version
   # 在虚拟环境中应指向 ~/.hermes/hermes-agent/.venv/bin/python
   ```

2. **清除污染的环境变量**：
   ```bash
   unset PYTHONPATH
   unset PYTHONHOME
   # 停用 conda
   conda deactivate
   ```

3. **重建虚拟环境**：
   ```bash
   cd ~/.hermes/hermes-agent
   rm -rf .venv
   uv venv --python 3.13
   uv sync --extra all
   uv pip install -e .
   ```

4. **使用 uv 固定 Python 版本**：
   ```bash
   uv python pin 3.13
   ```

5. Windows 上使用 PowerShell 时，注意执行策略可能阻止激活脚本（见 [8.6.5 节](#865-powershell-执行策略)）。

---

## 8.3 Node.js 版本问题

### 8.3.1 Node.js 版本过低

**【症状】**

- `npm install` 报 `EBADENGINE` 警告或错误，提示 `required: { "node": ">=22.22.0" }`。
- TUI 无法启动，报 JavaScript 语法错误。
- `hermes doctor` 显示 Node.js 版本低于 22.22.0。

**【原因】**

项目 `package.json` 要求 Node.js `>=22.22.0`（package.json:65），这是由 `react-router 8.3.0` 的 `engines.node` 字段决定的实际底线。系统自带的 Node.js 可能版本过旧（如 Debian 13 自带 Node 20，Ubuntu 22.04 自带 Node 12/14）。

**【解决方案】**

1. **让安装脚本自动安装托管 Node**（推荐）：安装脚本会检测系统 Node 版本，不满足时自动下载 Node.js 到 `~/.hermes/node/`（Linux/macOS）或 `%LOCALAPPDATA%\hermes\node\`（Windows），并创建符号链接到命令目录。无需手动卸载系统 Node。

2. **手动升级 Node.js**：
   - 使用 nvm（推荐）：
     ```bash
     curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | bash
     nvm install 22
     nvm use 22
     ```
   - Windows 使用 [nvm-windows](https://github.com/coreybutler/nvm-windows) 或 fnm。
   - macOS 使用 Homebrew：`brew install node@22`。
   - Docker 镜像已固定使用 Node 26（见 Dockerfile:51），无需手动处理。

3. **确认版本**：
   ```bash
   node --version   # 应 >= v22.22.0
   npm --version    # 应 <11.10.0 或 >=11.17.0
   ```

### 8.3.2 npm 权限问题（EACCES）

**【症状】**

- `npm install -g` 报 `EACCES: permission denied`，访问 `/usr/local/lib/node_modules` 或 `~/.npm`。
- 安装后全局命令无法执行。

**【原因】**

npm 默认全局安装目录可能需要 root 权限。Hermes 安装脚本通过将托管 Node 的 npm prefix 指向用户目录来避免此问题，但若手动使用系统 npm 安装全局包仍可能遇到。

**【解决方案】**

1. **不要使用 sudo npm**（可能导致后续权限混乱）。
2. **配置 npm 使用用户目录**：
   ```bash
   mkdir -p ~/.npm-global
   npm config set prefix '~/.npm-global'
   echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
   source ~/.bashrc
   ```
3. **使用 Hermes 托管的 Node**（安装脚本已自动配置 prefix）：
   ```bash
   export PATH="$HOME/.hermes/node/bin:$PATH"
   ```
4. Windows 上以当前用户身份运行 PowerShell，无需管理员权限。

### 8.3.3 node-pty 编译失败

**【症状】**

- `npm install` 过程中 `node-pty` 的 postinstall 失败。
- 错误信息包含 `node-gyp`、`MSBuild`、`gcc`、`g++`、`python` 相关报错。
- Windows 上报 `Visual Studio Build Tools` 未找到。

**【原因】**

`node-pty` 是原生 Node 模块，需要 C/C++ 编译工具链。`package.json` 的 `allowScripts` 中明确允许了 `node-pty@1.1.0` 的安装脚本（package.json:71）。缺少编译工具时构建失败。

**【解决方案】**

1. **Linux**：安装编译工具链：
   ```bash
   # Ubuntu/Debian
   sudo apt install build-essential python3-dev make g++
   # Fedora
   sudo dnf install gcc-c++ make python3-devel
   ```
   Docker 镜像已预装 `gcc g++ make cmake python3-dev`（Dockerfile:73）。

2. **macOS**：安装 Xcode Command Line Tools：
   ```bash
   xcode-select --install
   ```

3. **Windows**：
   - 以管理员身份安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)，勾选"Desktop development with C++"。
   - 或使用 `npm install --global windows-build-tools`（旧方法，仅旧版 Node）。
   - 确保 Python 3.x 在 PATH 中（node-gyp 需要）。

4. **Termux/Android**：
   ```bash
   pkg install clang rust make pkg-config libffi openssl
   ```

5. 若仍失败，检查是否安装了正确版本的 Node（node-pty 的预编译二进制与 Node 版本绑定）。

---

## 8.4 依赖编译失败

### 8.4.1 gcc/g++ 缺失

**【症状】**

- `uv sync` 或 `pip install` 过程中编译原生扩展失败。
- 错误信息包含 `unable to execute 'gcc': No such file or directory`、`error: command 'gcc' failed`、`Microsoft Visual C++ 14.0 is required`。

**【原因】**

部分 Python 包（如 `cryptography`、`Pillow`、`pydantic-core`）在没有预编译 wheel 的平台上需要从源码编译，需要 C/C++ 编译器。Hermes 优先使用 wheel，但某些平台/架构组合可能没有对应 wheel。

**【解决方案】**

1. **Ubuntu/Debian**：
   ```bash
   sudo apt update
   sudo apt install build-essential python3-dev libffi-dev
   ```

2. **Fedora/RHEL**：
   ```bash
   sudo dnf install gcc gcc-c++ make python3-devel libffi-devel
   ```

3. **Arch Linux**：
   ```bash
   sudo pacman -S base-devel python libffi
   ```

4. **macOS**：
   ```bash
   xcode-select --install
   # 或使用 Homebrew
   brew install libffi
   ```

5. **Windows**：安装 Visual Studio Build Tools（见 [8.3.3 节](#833-node-pty-编译失败)）。

6. Docker 镜像已预装完整编译工具链，不会出现此问题。

### 8.4.2 Python.h 找不到

**【症状】**

- 编译错误：`fatal error: Python.h: No such file or directory`。
- 安装 `cryptography`、`pydantic-core` 等包时失败。

**【原因】**

系统只安装了 Python 运行时，未安装 Python 开发头文件（`python3-dev` / `python3-devel`）。

**【解决方案】**

```bash
# Ubuntu/Debian
sudo apt install python3-dev

# Fedora
sudo dnf install python3-devel

# Arch
sudo pacman -S python

# Termux
pkg install python
```

若使用 uv 管理的 Python，其自带的发行版通常包含头文件，无需额外安装。

### 8.4.3 libolm-dev 缺失（Matrix E2EE）

**【症状】**

- 安装 `[matrix]` extra 时 `python-olm` 编译失败。
- 错误信息包含 `olm/olm.h: No such file or directory`、`pkg-config not found`。
- Windows/macOS 上即使安装了 libolm 也可能构建失败。

**【原因】**

Matrix 端到端加密依赖 `mautrix[encryption]` → `python-olm`，后者需要系统安装 `libolm` 开发库。`python-olm` 仅提供 Linux wheel，在 Windows 和现代 macOS 上没有原生构建路径。

项目 `[all]` extra **故意不包含** matrix 依赖（pyproject.toml:336-341 注释），正是因为这个跨平台问题。Docker 镜像内预装了 `libolm-dev` 所以可用。

**【解决方案】**

1. **Linux（Ubuntu/Debian）**：
   ```bash
   sudo apt install libolm-dev cmake build-essential
   pip install 'hermes-agent[matrix]'
   ```

2. **Fedora**：
   ```bash
   sudo dnf install libolm-devel cmake
   ```

3. **macOS**：
   ```bash
   brew install libolm cmake
   ```
   但若 `python-olm` 仍无 wheel，可能需要从源码编译，过程较复杂。建议需要 Matrix 功能时使用 Docker 部署。

4. **Windows**：原生不支持 Matrix E2EE。建议：
   - 使用 Docker 运行 Hermes（Docker 镜像已内置 Matrix 支持）；
   - 或在 WSL2 中安装。

5. **Termux/Android**：Matrix E2EE 被明确排除（没有可用的构建路径），使用 `[termux]` 或 `[termux-all]` extra 即可。

### 8.4.4 Rust 编译错误

**【症状】**

- 安装 `pydantic-core`、`cryptography`（部分版本）、`tokenizers` 等包时触发 cargo 构建。
- 错误信息包含 `error[EXXXX]`、`failed to run custom build command`、`linker 'cc' not found`、`maturin failed`。
- 编译时间极长（数分钟到数十分钟）后失败。

**【原因】**

当目标平台没有预编译 wheel 时，包含 Rust 扩展的 Python 包会尝试从源码构建，需要 Rust 工具链（rustc + cargo）。触发场景：

- 使用了不受支持的 Python 版本（如 3.14，见 [8.2.1 节](#821-python-314-不被支持)）。
- 在非主流架构上安装（如 ARMv7、某些 MUSL 环境）。
- Termux 环境（Bionic libc 不满足 manylinux 标签）。

**【解决方案】**

1. **优先使用预编译 wheel**：确保 Python 版本在 `3.11`–`3.13` 之间，且平台是主流的 x86_64/aarch64 Linux、macOS 或 Windows。

2. **安装 Rust 工具链**（若必须从源码构建）：
   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source "$HOME/.cargo/env"
   ```
   Termux：`pkg install rust`。

3. **Termux 用户**使用精简安装 profile：
   ```bash
   pip install 'hermes-agent[termux]'
   ```
   不要尝试安装 `[voice]`（faster-whisper）等包含重型原生依赖的 extra，ctranslate2 在 Termux 上不可用。

4. 若 Rust 编译因内存不足被杀（OOM），增加交换空间或使用预编译 wheel。

---

## 8.5 权限问题

### 8.5.1 sudo 使用注意事项

**【症状】**

- 使用 `sudo` 运行安装脚本后，`~/.hermes/` 下的文件归 root 所有。
- 普通用户运行 `hermes` 时报 `PermissionError`。
- `hermes doctor` 显示配置文件不可写。

**【原因】**

Hermes 的设计原则是**不需要 root 权限**安装和运行。安装脚本仅在安装可选系统包（ripgrep、ffmpeg）时才请求 sudo，Hermes 本身的代码、虚拟环境、数据都安装在用户目录下。使用 `sudo` 运行整个安装脚本会导致：

- `~/.hermes/` 目录被 root 创建，普通用户无法写入。
- `uv` 管理的 Python 安装到 `/root/.local/share/uv`，其他用户无法访问。
- Docker 卷挂载时 UID 不匹配。

**【解决方案】**

1. **不要以 root 运行安装脚本**（除非确实要做系统级 FHS 安装）：
   ```bash
   # 正确
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   # 错误
   sudo curl -fsSL ... | sudo bash
   ```

2. **修复已有权限问题**：
   ```bash
   sudo chown -R "$USER:$USER" ~/.hermes
   ```

3. **Linux root 用户的 FHS 安装**（仅在你明确需要时）：
   以 root 运行安装脚本时，脚本会自动采用 FHS 布局：代码安装到 `/usr/local/lib/hermes-agent`，命令链接到 `/usr/local/bin/hermes`，数据仍在 `/root/.hermes`。这适用于 Docker 容器等单用户环境。

4. Docker 中通过 `HERMES_UID`/`HERMES_GID` 环境变量控制文件所有权（见 [8.7.1 节](#871-卷挂载权限问题)）。

### 8.5.2 EACCES 权限拒绝

**【症状】**

- 运行时报 `PermissionError: [Errno 13] Permission denied`。
- npm 安装时 `EACCES`。
- 无法写入 `~/.hermes/`、`~/.hermes/logs/agent.log` 或虚拟环境目录。
- Windows 上 `WinError 5`（Access is denied）。

**【原因】**

1. 文件或目录被 root（或其他用户）拥有。
2. 之前用 sudo 运行过 Hermes 或安装脚本。
3. Windows 上文件被其他进程锁定（如杀毒软件、另一个 Hermes 实例）。
4. 磁盘满或只读挂载。

**【解决方案】**

1. **修复所有权**（Linux/macOS）：
   ```bash
   sudo chown -R "$USER":"$(id -gn)" ~/.hermes
   chmod -R u+rw ~/.hermes
   ```

2. **检查磁盘空间**：
   ```bash
   df -h ~/.hermes
   ```

3. **Windows**：
   - 关闭可能锁定文件的程序（编辑器、终端、杀毒软件实时扫描）。
   - 以当前用户（非管理员）运行 PowerShell。
   - 检查文件夹属性，确保未设为只读。

4. **npm EACCES** 见 [8.3.2 节](#832-npm-权限问题eacces)。

5. Windows 日志轮转失败（`WinError 32`）已由 `concurrent-log-handler` 自动处理；若仍出现，重启所有 Hermes 进程后重试。

### 8.5.3 Docker 权限问题

**【症状】**

- 容器内创建的文件在宿主机上显示为 UID `10000` 或 `root`。
- `hermes` 命令无法写入 `/opt/data`。
- `docker exec` 运行 `hermes` 后生成的配置文件 root 所有，网关服务无法读取。

**【原因】**

Docker 容器内默认以 `hermes` 用户（UID 10000）运行，而宿主机用户的 UID 通常是 1000。若不匹配，容器内写入挂载卷的文件在宿主机上无法直接读写。此外，`docker exec` 默认以 root 身份进入，直接运行 `hermes` 会以 root 创建文件。

**【解决方案】**

1. **启动时指定 UID/GID**（docker-compose.yml 已内置支持）：
   ```bash
   HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
   ```
   容器的 `stage2-hook.sh` 会在启动时通过 `usermod`/`groupmod` 将内部 hermes 用户重映射到指定的 UID/GID。

2. **使用特权降级 shim**：镜像内置了 `/opt/hermes/bin/hermes` shim，当以 root 执行 `docker exec hermes ...` 时，会自动通过 `s6-setuidgid hermes` 降级到 hermes 用户。若需以 root 执行（如调试），设置：
   ```bash
   docker exec -e HERMES_DOCKER_EXEC_AS_ROOT=1 <container> hermes ...
   ```

3. **修复已有文件所有权**：
   ```bash
   sudo chown -R $(id -u):$(id -g) ~/.hermes
   ```

4. 不要以 `--user root` 长期运行容器，这会绕过所有权限设计。

---

## 8.6 Windows 特有问题

### 8.6.1 CRLF 行尾符问题

**【症状】**

- Shell 脚本（`.sh`）在 WSL/Linux 容器中运行报 `bad interpreter: /bin/bash^M: no such file or directory`。
- Python 脚本报 `SyntaxError` 或编码错误。
- Docker 构建时脚本报错。

**【原因】**

Windows 上 Git 默认可能将文本文件检出为 CRLF（`\r\n`）行尾，而 Linux/macOS 期望 LF（`\n`）。项目根目录有 `.gitattributes` 进行规范化，但本地 Git 配置可能覆盖它。

**【解决方案】**

1. **配置 Git 使用 LF**：
   ```bash
   git config --global core.autocrlf input
   # 或完全禁用转换
   git config --global core.autocrlf false
   ```

2. **重新检出文件**：
   ```bash
   cd ~/.hermes/hermes-agent
   git rm --cached -r .
   git reset --hard
   ```

3. **WSL 用户**：建议在 WSL 文件系统内（`~/` 而非 `/mnt/c/`）克隆仓库，避免跨文件系统的行尾和权限问题。

4. PowerShell 安装脚本（`install.ps1`）不受此影响，因为它是原生 Windows 脚本。

### 8.6.2 长路径限制

**【症状】**

- 安装或运行时报 `Path too long`、`文件名或扩展名太长`。
- `node_modules` 深层目录的文件无法访问或删除。
- 用户文件夹名含空格、点号或重音字符（如 `C:\Users\First Last\`、`C:\Users\Stone.ZEN8\`、`C:\Users\Rubén\`）时出现"路径不存在"错误。

**【原因】**

1. Windows 默认限制路径长度为 260 字符（`MAX_PATH`），`node_modules` 的嵌套依赖极易超出。
2. Windows 为含空格/点号/重音字符的配置文件夹生成 8.3 短路径别名（如 `FIRST~1.LAS`），PowerShell 的 FileSystem provider 在处理这些别名时有 bug，会报"对象不存在"。

安装脚本 `install.ps1` 包含大量逻辑（约 200 行）来自动规范化 8.3 短路径为长路径，但仍有边缘情况。

**【解决方案】**

1. **启用 Windows 长路径支持**（推荐，Windows 10 1607+）：
   - 以管理员身份运行 PowerShell：
     ```powershell
     New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem" `
       -Name "LongPathsEnabled" -Value 1 -PropertyType DWORD -Force
     ```
   - 重启电脑。

2. **缩短安装路径**：将 Hermes 安装到较短路径，如 `C:\hermes\`：
   ```powershell
   $env:HERMES_HOME = "C:\hermes"
   .\install.ps1
   ```

3. **避免用户文件夹名含特殊字符**：若当前 Windows 用户名含空格、点号或非 ASCII 字符，建议：
   - 创建一个纯 ASCII 的新 Windows 用户账户用于开发；或
   - 设置 `HERMES_HOME` 到不含特殊字符的路径（如 `C:\hermes`）。

4. **验证路径解析**：安装脚本提供诊断参数：
   ```powershell
   .\install.ps1 -ShowResolvedPaths
   ```
   会以 JSON 输出实际解析的路径，便于排查短路径问题。

### 8.6.3 pywin32 DLL 加载失败

**【症状】**

- `import win32security` 或 `import win32file` 报 `ImportError: DLL load failed`。
- SSH 远程运行时功能异常。
- 日志轮转失败（`concurrent-log-handler` 依赖 pywin32）。

**【原因】**

Windows 上 Hermes 依赖 `pywin32`（pyproject.toml:117）用于桌面 SSH 运行时和跨进程日志文件锁。pywin32 的 DLL 有时注册不正确，特别是在使用虚拟环境或多 Python 版本时。

**【解决方案】**

1. **重新安装 pywin32**：
   ```powershell
   uv pip install --force-reinstall pywin32
   ```

2. **运行 pywin32 的后安装脚本**：
   ```powershell
   python .venv\Scripts\pywin32_postinstall.py -install
   ```

3. **确认使用的是正确的 Python 架构**（64 位 Python 配 64 位 pywin32）：
   ```powershell
   python -c "import platform; print(platform.architecture())"
   ```

4. 若仍失败，安装 [Microsoft Visual C++ Redistributable](https://learn.microsoft.com/en-us/cpp/windows/latest-supported-vc-redist)。

### 8.6.4 杀毒软件拦截

**【症状】**

- 安装过程中 `.exe`、`.dll` 文件被隔离或删除。
- `uv.exe`、`node.exe`、`python.exe` 被标记为可疑。
- Playwright Chromium 下载后无法运行。
- 安装突然中断且无明确错误信息。

**【原因】**

部分杀毒软件（特别是 Windows Defender、360、火绒等）的启发式扫描会误判：

- uv 下载的 Python 解释器二进制。
- Node.js 和 npm 全局包。
- Playwright 下载的 Chromium 可执行文件（无数字签名的开源浏览器二进制）。
- `node-pty` 等原生模块编译产物。

**【解决方案】**

1. **将 Hermes 目录加入杀毒软件白名单**：
   - Windows Defender：设置 → 病毒和威胁防护 → 管理设置 → 排除项 → 添加文件夹
   - 添加 `%LOCALAPPDATA%\hermes\`（或自定义的 `HERMES_HOME`）。

2. **临时禁用实时防护**进行安装，安装完成后重新启用。

3. **企业环境**：若杀毒软件由组策略管理，联系 IT 部门添加白名单。

4. 若 Chromium 被拦截，可手动指定系统浏览器：
   ```powershell
   # 在 .env 中设置
   AGENT_BROWSER_EXECUTABLE_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
   ```

5. 安装后运行 `hermes doctor` 确认 agent-browser 和 Chromium 状态正常。

### 8.6.5 PowerShell 执行策略

**【症状】**

- 运行 `.\install.ps1` 报 `无法加载文件 ... 因为在此系统上禁止运行脚本`。
- 错误信息包含 `ExecutionPolicy`、`UnauthorizedAccess`、`running scripts is disabled`。
- `irm ... | iex` 一行命令也失败。

**【原因】**

Windows PowerShell 默认执行策略为 `Restricted`，不允许运行任何脚本。PowerShell 5.1 的此策略比 PowerShell 7+ 更严格。

**【解决方案】**

1. **为当前用户设置执行策略**（推荐，无需管理员）：
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```
   这允许本地脚本运行，远程脚本需要数字签名。

2. **仅为本次会话绕过**（不修改系统设置）：
   ```powershell
   powershell -ExecutionPolicy Bypass -File .\install.ps1
   ```

3. **官方一行命令已使用 Bypass**：
   ```powershell
   iex (irm https://hermes-agent.nousresearch.com/install.ps1)
   ```
   `irm` 获取脚本内容后通过 `iex` 执行，不经过文件执行策略检查。若仍失败，可能是更严格的组策略限制。

4. **使用 PowerShell 7**（`pwsh`）：从 [Microsoft Store](https://aka.ms/powershell) 或 GitHub 安装，默认执行策略更宽松。安装脚本内部会自动选择可用的 PowerShell 主机来运行 uv 安装器。

5. **Constrained Language Mode**：若处于企业锁定环境，PowerShell 可能运行在约束语言模式下，阻止 `Add-Type` 等调用。安装脚本的长路径解析功能会降级，但核心安装仍可能成功。若完全无法运行，请联系 IT 部门或使用 Docker/WSL 安装。

---

## 8.7 Docker 特有问题

### 8.7.1 卷挂载权限问题

**【症状】**

- 容器日志显示 `Permission denied: '/opt/data/...'`。
- 容器内无法创建或修改 `~/.hermes` 中的文件。
- 宿主机上 `~/.hermes/` 中出现 UID 10000 的文件。
- `hermes doctor` 在容器内报配置文件不可写。

**【原因】**

容器内 Hermes 以 `hermes` 用户运行，默认 UID 10000。当宿主机 `~/.hermes` 挂载到 `/opt/data` 时，若宿主机用户 UID 不是 10000，则权限不匹配。`docker-compose.yml` 支持通过 `HERMES_UID`/`HERMES_GID` 环境变量在启动时重映射 UID。

**【解决方案】**

1. **使用 docker compose 时指定 UID**（推荐）：
   ```bash
   HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
   ```
   `stage2-hook.sh` 会在容器启动时执行 `usermod -u $HERMES_UID hermes` 和 `groupmod -g $HERMES_GID hermes`，然后 `chown` 数据卷。

2. **使用 docker run 时**：
   ```bash
   docker run -d \
     -e HERMES_UID=$(id -u) \
     -e HERMES_GID=$(id -g) \
     -v ~/.hermes:/opt/data \
     --name hermes \
     hermes-agent gateway run
   ```

3. **修复已存在的权限问题**：
   ```bash
   # 在宿主机上
   sudo chown -R $(id -u):$(id -g) ~/.hermes
   # 然后重启容器
   docker compose restart
   ```

4. **SELinux 系统**（Fedora/RHEL/CentOS）可能需要添加 `:z` 或 `:Z` 标签：
   ```yaml
   volumes:
     - ~/.hermes:/opt/data:z
   ```

5. 不要将 `/opt/data` 挂载到 NFS 等不支持 Unix 权限的文件系统上。

### 8.7.2 网络模式问题

**【症状】**

- 网关服务无法接收消息平台的 webhook。
- 浏览器工具无法访问宿主机上的服务。
- 使用 `network_mode: host` 时端口冲突。
- 仪表盘无法从宿主机访问。

**【原因】**

`docker-compose.yml` 默认使用 `network_mode: host`（docker-compose.yml:35），这在 Linux 上让容器直接使用宿主机网络命名空间，但在 macOS/Windows 上 Docker Desktop 的 host 网络支持有限。此外，仪表盘默认绑定 `127.0.0.1`，从容器外不可访问。

**【解决方案】**

1. **Linux 上使用 host 网络**（默认配置）：网关和仪表盘直接使用宿主机端口，无需端口映射。

2. **macOS/Windows**：Docker Desktop 的 `network_mode: host` 行为不同。改用桥接网络+端口映射：
   ```yaml
   services:
     gateway:
       ports:
         - "9119:9119"
         # 根据需要映射其他端口
   ```
   移除 `network_mode: host`。

3. **远程访问仪表盘**：默认仪表盘仅监听 `127.0.0.1`。安全的远程访问方式是 SSH 隧道：
   ```bash
   ssh -L 9119:localhost:9119 user@server
   ```
   然后在本地浏览器访问 `http://localhost:9119`。
   **不要**直接绑定 `0.0.0.0` 而不设置认证，这会将含 API Key 的仪表盘暴露到公网。

4. **容器内访问宿主机服务**：
   - Linux host 网络模式下直接用 `localhost`。
   - 桥接模式下用 `host.docker.internal`（Docker Desktop）或宿主机网关 IP。

5. **检查端口占用**：
   ```bash
   ss -tlnp | grep 9119
   # 或
   netstat -tlnp | grep 9119
   ```

### 8.7.3 s6-overlay 启动失败

**【症状】**

- 容器立即退出，日志显示 `s6-overlay-suexec: fatal: can only run as pid 1`。
- 容器卡在启动阶段，服务未运行。
- `cont-init.d` 脚本报错。
- 日志中出现 `rc.init: 91: -g: not found`。

**【原因】**

1. **PID 1 问题**：s6-overlay 的 `/init` 必须作为 PID 1 运行。当容器被其他 init 系统包装（如 `docker run --init`、Fly Machines、Kubernetes）时，`/init` 无法作为 PID 1。
2. **tini 标志转发问题**：旧编排模板可能调用 `/usr/bin/tini -g ...`，而镜像为了向后兼容保留了 tini shim，错误地将 `-g` 等标志传入 s6 的 rc.init。
3. **架构不匹配**：在错误的 CPU 架构上运行镜像（如 arm64 镜像在 amd64 上）。
4. **数据卷权限问题**导致 `stage2-hook.sh` 失败。

**【解决方案】**

1. **使用镜像默认的 ENTRYPOINT**（推荐）：不要覆盖 `entrypoint`，让 `entrypoint-dispatch.sh` 自动处理：
   - 当镜像拥有 PID 1 时，exec `/init`（完整 s6 监督树）。
   - 当外部已有 PID 1 时（`--init`、某些调度器），回退到直接运行 `stage2-hook.sh` + `main-wrapper.sh`。
   ```bash
   # 正确
   docker run hermes-agent gateway run
   # 错误（手动覆盖 entrypoint）
   docker run --entrypoint /bin/bash hermes-agent
   ```

2. **不要使用 `docker run --init`** 与 Hermes 镜像一起使用，这会让 tini 占据 PID 1。镜像已内置 s6-overlay 来处理僵尸进程。

3. **检查架构匹配**：
   ```bash
   docker inspect hermes-agent | grep Architecture
   uname -m
   ```
   确保两者一致（`amd64`/`x86_64` 或 `arm64`/`aarch64`）。

4. **查看详细启动日志**：
   ```bash
   docker logs hermes 2>&1 | head -100
   ```

5. **调试 cont-init 脚本**：
   ```bash
   docker run --rm -it hermes-agent /bin/bash
   # 在容器内手动运行
   /opt/hermes/docker/stage2-hook.sh
   ```

6. 若 `rc.init: -g: not found` 出现，说明编排模板在调用旧的 tini 入口并传递了 tini 参数。更新编排配置使用默认 ENTRYPOINT，或移除命令中的 tini 标志。

### 8.7.4 容器内无法更新

**【症状】**

- 在容器内运行 `hermes update` 报只读文件系统错误（`EROFS`）。
- 懒加载安装（lazy install）的包在容器重建后丢失。
- 修改了 `/opt/hermes/` 下的文件但重启后恢复原状。

**【原因】**

Docker 镜像设计为**不可变基础设施**：

- `/opt/hermes`（代码目录）在镜像构建时设为 root 所有、只读（`go-w` 权限，Dockerfile:286）。
- 运行时设置了 `HERMES_DISABLE_LAZY_INSTALLS=1`（Dockerfile:380），防止懒加载安装修改只读的 venv。
- 可选后端的 SDK 被重定向到 `/opt/data/lazy-packages`（Dockerfile:393），该目录在持久卷上。
- 更新 Hermes 应通过拉取新镜像而非容器内更新。

**【解决方案】**

1. **通过拉取新镜像更新**（推荐）：
   ```bash
   docker compose pull
   docker compose up -d
   ```
   或：
   ```bash
   docker pull hermes-agent:latest
   docker stop hermes && docker rm hermes
   docker run ... hermes-agent gateway run
   ```

2. **懒加载包持久化**：可选后端（如 Firecrawl、Exa、Feishu SDK）会安装到 `/opt/data/lazy-packages`，该目录在挂载卷上，容器重建后保留。若包因 Python 版本升级失效，删除该目录让其重装：
   ```bash
   rm -rf ~/.hermes/lazy-packages
   docker compose restart
   ```

3. **不要在容器内运行 `hermes update`**：这不会持久化，且可能因只读文件系统失败。

4. **自定义构建**：若需要修改代码，基于镜像构建自定义 Dockerfile：
   ```dockerfile
   FROM hermes-agent
   USER root
   # 你的自定义修改
   USER hermes
   ```

5. **开发模式**：若需要在容器内开发，将源码目录挂载到 `/opt/hermes` 并使用可写镜像层，但这不是生产部署方式。

---

## 8.8 启动问题

### 8.8.1 命令找不到（command not found）

**【症状】**

- 终端输入 `hermes` 报 `command not found`、`不是内部或外部命令`。
- 安装成功但新开终端后命令不可用。
- `hermes doctor` 报 `~/.local/bin/hermes` 不存在或符号链接损坏。

**【原因】**

1. 命令链接目录（`~/.local/bin`、`/usr/local/bin` 或 Windows 的 `%LOCALAPPDATA%\hermes\bin`）不在 PATH 中。
2. 符号链接指向的虚拟环境入口已被删除或移动。
3. Shell 配置文件（`.bashrc`、`.zshrc`）未被重新加载。
4. Windows 上 User PATH 未在新终端中生效。
5. 多 Profile 安装时使用了非默认 Profile。

**【解决方案】**

1. **重新加载 Shell 配置**：
   ```bash
   source ~/.bashrc   # 或 ~/.zshrc
   ```
   Windows 用户需打开**新的** PowerShell 窗口（User PATH 变更不会在已有窗口中生效）。

2. **检查 PATH**：
   ```bash
   echo $PATH | tr ':' '\n' | grep -E '\.local/bin|hermes'
   ```
   若 `~/.local/bin` 不在 PATH 中：
   ```bash
   echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **检查符号链接**：
   ```bash
   ls -la ~/.local/bin/hermes
   # 应指向 ~/.hermes/hermes-agent/.venv/bin/hermes
   ```
   若链接损坏，重建：
   ```bash
   ln -sf ~/.hermes/hermes-agent/.venv/bin/hermes ~/.local/bin/hermes
   ```
   或运行：
   ```bash
   hermes doctor --fix
   ```
   doctor 会自动检测并修复符号链接（doctor.py:1891-1910）。

4. **Windows 检查 User PATH**：
   ```powershell
   [Environment]::GetEnvironmentVariable("Path", "User")
   ```
   应包含 `%LOCALAPPDATA%\hermes\bin`。若缺失，重新运行安装脚本或手动添加。

5. **直接使用虚拟环境中的命令**：
   ```bash
   ~/.hermes/hermes-agent/.venv/bin/hermes --version
   ```

6. **FHS 安装**（root 用户）：命令在 `/usr/local/bin/hermes`，通常默认在 PATH 中。

7. **多 Profile**：若使用 `hermes -p <name>` 创建了命名 Profile，命令仍为 `hermes`，但数据目录不同。

### 8.8.2 模块导入错误（ModuleNotFoundError / ImportError）

**【症状】**

- 启动报 `ModuleNotFoundError: No module named 'hermes_cli'`、`No module named 'openai'`。
- `ImportError` 指向不相关的包版本冲突。
- 在某些目录下能运行，在其他目录下不能。
- `hermes --version` 能运行，但执行具体命令时崩溃。

**【原因】**

1. **PYTHONPATH 污染**：外部设置了 `PYTHONPATH` 环境变量，导致 Python 导入了其他位置的同名模块。安装脚本会主动清除 `PYTHONPATH` 和 `PYTHONHOME`（install.sh:22-29），但手动运行时可能存在。
2. **虚拟环境未激活**或激活了错误的 venv。
3. **editable install 损坏**：`pip install -e .` 创建的 egg-link 指向了已移动的源码目录。
4. **依赖缺失**：安装时使用了 `--no-deps` 或安装中断。
5. **Conda 环境干扰**。

**【解决方案】**

1. **清除环境污染**：
   ```bash
   unset PYTHONPATH
   unset PYTHONHOME
   conda deactivate 2>/dev/null
   ```

2. **确认在正确的虚拟环境中**：
   ```bash
   which python
   # 应指向 ~/.hermes/hermes-agent/.venv/bin/python
   python -c "import hermes_cli; print(hermes_cli.__file__)"
   ```

3. **重新安装依赖**：
   ```bash
   cd ~/.hermes/hermes-agent
   uv sync --extra all
   uv pip install -e .
   ```

4. **检查 editable install**：
   ```bash
   ls -la .venv/lib/python*/site-packages/hermes-agent.egg-link
   cat .venv/lib/python*/site-packages/hermes-agent.egg-link
   # 应指向项目根目录
   ```

5. **运行 doctor 诊断**：
   ```bash
   hermes doctor
   ```
   "Required Packages"一节会检查 openai、rich、dotenv、yaml、httpx 等核心包是否可导入。

6. **重建虚拟环境**（终极手段）：
   ```bash
   cd ~/.hermes/hermes-agent
   rm -rf .venv
   uv venv --python 3.13
   uv sync --extra all
   uv pip install -e .
   ```

### 8.8.3 段错误（Segmentation Fault）

**【症状】**

- 启动或对话时程序直接崩溃，终端显示 `Segmentation fault (core dumped)`。
- 没有 Python traceback，进程异常退出。
- 在非主线程中调用 OpenAI Responses API 时必现。

**【原因】**

已知的段错误原因：

1. **pydantic-core 2.41.5 的 bug**：该版本在非主线程中执行 OpenAI SDK 的 Responses API 资源时会段错误。Hermes 已将 pydantic 固定到 `2.13.4`（pyproject.toml:55），该版本依赖 pydantic-core 2.46.4 修复了此问题。若你的环境中存在旧版本，说明依赖未正确更新。
2. **SQLite 版本问题**：某些发行版的 SQLite 存在 WAL-reset bug，可能导致崩溃。
3. **原生扩展 ABI 不匹配**：混用了不同 Python 版本编译的 .so 文件。

**【解决方案】**

1. **升级 pydantic 和 pydantic-core**：
   ```bash
   uv pip install --upgrade pydantic==2.13.4
   # 验证
   python -c "import pydantic_core; print(pydantic_core.__version__)"
   # 应 >= 2.46.4
   ```

2. **检查 SQLite 版本**：
   ```bash
   python -c "import sqlite3; print(sqlite3.sqlite_version)"
   ```
   若版本低于 3.51.3（或 3.50.7 / 3.44.6 的修复版本），doctor 会发出 WAL-reset bug 警告。Docker 镜像已编译固定版本的 SQLite 3.53.4（Dockerfile:7）。
   - Linux：升级系统 SQLite 或使用 uv 管理的 Python（自带更新版本）。
   - Docker：拉取最新镜像。

3. **重新安装原生扩展**：
   ```bash
   uv pip install --force-reinstall pydantic-core cryptography
   ```

4. **获取 core dump 进行调试**：
   ```bash
   ulimit -c unlimited
   hermes 2>&1 | tee crash.log
   ```

5. 若段错误持续，运行 `hermes doctor` 检查环境，并在 GitHub Issue 中附上 doctor 输出和崩溃日志。

### 8.8.4 端口占用

**【症状】**

- 启动仪表盘或网关时报 `Address already in use`、`EADDRINUSE`、`Only one usage of each socket address`。
- Web UI 无法访问。
- API 服务器启动失败。

**【原因】**

Hermes 仪表盘默认使用 9119 端口（见 docker-compose.yml:76 的 SSH 隧道示例）。若该端口被其他进程占用（另一个 Hermes 实例、其他 Web 服务），则启动失败。网关的消息平台 webhook 也可能占用端口（如 Teams 默认 3978）。

**【解决方案】**

1. **查找占用端口的进程**：
   ```bash
   # Linux/macOS
   ss -tlnp | grep 9119
   lsof -i :9119
   ```
   ```powershell
   # Windows
   netstat -ano | findstr :9119
   tasklist /FI "PID eq <PID>"
   ```

2. **终止占用进程**：
   ```bash
   kill <PID>
   # 或强制终止
   kill -9 <PID>
   ```
   ```powershell
   Stop-Process -Id <PID> -Force
   ```

3. **若占用进程是另一个 Hermes 实例**，先停止它：
   ```bash
   hermes gateway stop
   # 或
   docker compose down
   ```

4. **更换仪表盘端口**：
   ```bash
   hermes dashboard --port 9120
   ```

5. **检查是否有僵尸网关进程**：
   ```bash
   ps aux | grep -i hermes
   ```
   `hermes doctor` 会检查网关节令状态（Linux 上检查 systemd linger，容器内检查 s6 服务状态）。

6. Windows 上若端口处于 `TIME_WAIT` 状态，等待几秒后重试，或重启终端。

---

## 8.9 日志查看与诊断方法

### 8.9.1 日志文件位置

所有 Hermes 日志存放在 `$HERMES_HOME/logs/` 目录下：

| 日志文件 | 用途 |
|---|---|
| `agent.log` | 主代理日志，包含所有会话活动、工具调用、模型交互 |
| `errors.log` | 仅 ERROR 及以上级别，适合快速排查问题 |
| `gateway.log` | 网关服务日志（消息平台收发、webhook、后台运行） |
| `gui.log` | Dashboard / Web UI / PTY / WebSocket 日志 |
| `desktop.log` | Electron 桌面应用启动和后端日志（仅桌面版） |
| `mcp-stderr.log` | MCP 子进程的标准错误输出，每个服务器有会话标记 |

- **Linux/macOS**：`~/.hermes/logs/`
- **Windows**：`%LOCALAPPDATA%\hermes\logs\`
- **Docker**：容器内 `/opt/data/logs/`，映射到宿主机 `~/.hermes/logs/`
- **自定义 HERMES_HOME**：`$HERMES_HOME/logs/`

### 8.9.2 使用 hermes logs 命令

Hermes 提供了内置的日志查看工具（hermes_cli/logs.py），支持过滤和实时跟踪：

```bash
# 查看最近 50 行 agent.log（默认）
hermes logs

# 实时跟踪日志
hermes logs -f

# 查看错误日志最近 100 行
hermes logs errors -n 100

# 查看网关日志并实时跟踪
hermes logs gateway -f

# 查看 GUI 日志
hermes logs gui -f

# 按日志级别过滤（DEBUG/INFO/WARNING/ERROR/CRITICAL）
hermes logs --level WARNING

# 按会话 ID 过滤
hermes logs --session abc123

# 按组件过滤（logger 名称前缀）
hermes logs --component tools
hermes logs --component gateway

# 查看最近 1 小时的日志
hermes logs --since 1h

# 组合使用：最近 30 分钟的工具错误，实时跟踪
hermes logs -f --since 30m --level ERROR --component tools
```

### 8.9.3 使用 hermes doctor 诊断

`hermes doctor` 是首选的环境诊断工具，检查范围包括（hermes_cli/doctor.py）：

| 检查项 | 说明 |
|---|---|
| 安全公告 | 检测已知的恶意/漏洞包版本（如 mistralai 2.4.6 蠕虫事件） |
| MCP 服务器安全 | 检查配置的 MCP stdio 命令是否可疑 |
| Python 环境 | 版本、虚拟环境、SQLite 版本及 WAL-reset 漏洞 |
| SSL/CA 证书 | certifi CA 包是否完整可用 |
| 必需包 | openai、rich、dotenv、yaml、httpx 等是否可导入 |
| 配置文件 | `.env`、`config.yaml` 是否存在、版本是否最新、键是否有效 |
| 模型/提供商 | provider 是否有效、API Key 是否配置、OAuth 登录状态 |
| 目录结构 | cron/sessions/logs/skills/memories 等子目录 |
| SQLite 数据库 | state.db 完整性、FTS 索引健康、WAL 文件大小、schema 版本 |
| 网关服务 | systemd linger 状态（Linux）、s6 监督状态（Docker） |
| 命令安装 | 符号链接是否正确、PATH 是否包含命令目录 |
| 外部工具 | git、ripgrep、docker、Node.js、agent-browser、Chromium |
| npm 审计 | Node 依赖的已知漏洞 |
| API 连通性 | 各模型提供商端点的实际 HTTP 连通性测试 |

**自动修复**：

```bash
# 仅诊断，不修改
hermes doctor

# 诊断并自动修复可修复的问题
hermes doctor --fix
```

`--fix` 可自动修复：

- 损坏的 CA 证书（强制重装 certifi）
- 缺失的配置文件和目录
- 过时的配置版本（自动迁移）
- 陈旧的根级配置键（迁移到 model 段）
- 陈旧的 `HERMES_MAX_ITERATIONS` 环境变量幽灵
- 损坏的符号链接
- 过大的 WAL 文件（执行 checkpoint）
- 损坏的 FTS 索引（重建 state.db 的 FTS）
- 空的 SOUL.md 模板

**确认安全公告**：当 doctor 报告安全公告后，按指引处理（卸载问题包、轮换凭据），然后确认：
```bash
hermes doctor --ack <advisory-id>
```

### 8.9.4 其他诊断命令

```bash
# 查看完整版本信息和更新状态
hermes version

# 查看当前状态（网关、会话、配置摘要）
hermes status

# 导出完整调试信息（用于提交 Issue）
hermes dump

# 查看配置（含来源和默认值）
hermes config show

# 验证配置文件语法
hermes config validate
```

### 8.9.5 提交 Issue 时应收集的信息

当在 GitHub 提交问题时，请附上：

1. `hermes doctor` 的完整输出。
2. `hermes version` 的输出。
3. 相关日志的最近 200 行：`hermes logs errors -n 200`。
4. 操作系统和版本：`uname -a`（Linux/macOS）或 `winver`（Windows）。
5. Python 版本：`python --version`。
6. Node.js 版本：`node --version`。
7. 安装方式：官方脚本 / 手动 / Docker / Nix。
8. 复现步骤和预期行为。

> **注意**：日志中可能包含 API Key 和敏感信息。提交前请检查并脱敏。`hermes_cli/redact.py` 模块会自动脱敏部分内容，但手动检查更安全。

---

## 8.10 完全卸载与干净重装

### 8.10.1 使用内置卸载命令

Hermes 提供了官方卸载器（hermes_cli/uninstall.py），支持两种模式：

**保留数据（推荐）**：删除代码但保留配置、会话、日志和 API Key，便于以后重装：
```bash
hermes uninstall
# 选择选项 1: Keep data
```

**完全卸载**：删除所有内容，包括配置、会话、日志、凭据：
```bash
hermes uninstall
# 选择选项 2: Full uninstall
```

**非交互式卸载**（脚本/自动化场景）：
```bash
# 保留数据，无需确认
hermes uninstall --yes

# 完全删除，无需确认
hermes uninstall --yes --full
```

**预览卸载操作（dry run）**：
```bash
hermes uninstall --dry-run
```
这会列出将要删除/修改的内容，但不实际执行任何操作。

### 8.10.2 卸载器执行的操作

`hermes uninstall` 按以下顺序执行（uninstall.py:756-905）：

1. **停止网关服务**：
   - Linux：停止并禁用 systemd 用户/系统服务，`daemon-reload`。
   - macOS：`launchctl unload` 并删除 plist。
   - Windows：停止 Scheduled Task 和启动项，终止 detached pythonw 进程。
   - Docker：停止 s6 监督的服务。
   - 终止所有独立的 `hermes gateway run` 进程。

2. **清理 PATH 条目**：
   - Linux/macOS：从 `.bashrc`、`.bash_profile`、`.profile`、`.zshrc`、`.zprofile` 中移除 Hermes PATH 行。
   - Windows：从注册表 `HKCU\Environment` 的 User PATH 中移除 `%LOCALAPPDATA%\hermes\*` 条目。

3. **移除命令包装器**：
   - 删除 `~/.local/bin/hermes`、`~/.local/bin/hermes-acp`、`~/.local/bin/hermes-agent`。
   - 删除 `/usr/local/bin/hermes`（FHS 安装）。
   - Windows：删除 `%LOCALAPPDATA%\hermes\bin\` 下的命令。

4. **移除 Node 符号链接**：
   - 删除 `~/.local/bin/`（或 `/usr/local/bin/`、`$PREFIX/bin`）中指向 Hermes 托管 Node 的 `node`、`npm`、`npx` 符号链接。
   - **不会**删除用户通过 nvm/fnm 等其他方式安装的 Node（仅删除指向 `~/.hermes/node/` 的符号链接）。

5. **移除桌面 GUI 产物**：
   - 删除构建的渲染进程、Electron 打包产物、`node_modules` 中的 GUI 部分。
   - 删除 Electron userData 目录（在 HERMES_HOME 外）。

6. **删除代码目录**：
   - 删除 `~/.hermes/hermes-agent/`（或 `/usr/local/lib/hermes-agent/`）。

7. **Windows 专属清理**：
   - 删除 PortableGit（`%LOCALAPPDATA%\hermes\git\`，约 200MB）。
   - 删除托管 Node（`%LOCALAPPDATA%\hermes\node\`）。
   - 删除 gateway-service 目录。
   - 删除 User 环境变量 `HERMES_HOME` 和 `HERMES_GIT_BASH_PATH`。

8. **完全卸载模式额外执行**：
   - 删除整个 `$HERMES_HOME`（含 `.env`、`config.yaml`、`sessions/`、`logs/`、`cron/`、`skills/`、`state.db` 等）。
   - 若有命名 Profile，交互式询问是否一并删除每个 Profile 的网关服务和数据目录。

### 8.10.3 手动完全卸载

若 `hermes uninstall` 因环境损坏无法运行，可手动执行以下步骤。

**Linux/macOS**：

```bash
# 1. 停止网关
hermes gateway stop 2>/dev/null
pkill -f "hermes.*gateway" 2>/dev/null

# 2. 删除代码和虚拟环境
rm -rf ~/.hermes/hermes-agent
# FHS 安装还需：
sudo rm -rf /usr/local/lib/hermes-agent
sudo rm -f /usr/local/bin/hermes /usr/local/bin/hermes-acp /usr/local/bin/hermes-agent

# 3. 删除命令链接和 Node 符号链接
rm -f ~/.local/bin/hermes ~/.local/bin/hermes-acp ~/.local/bin/hermes-agent
# 仅删除指向 ~/.hermes/node 的符号链接，不要盲目删除 node/npm/npx
for f in node npm npx; do
  link="$HOME/.local/bin/$f"
  if [ -L "$link" ] && [[ "$(readlink "$link")" == *".hermes/node"* ]]; then
    rm -f "$link"
  fi
done

# 4. 清理 Shell 配置中的 PATH（手动编辑）
# 删除 ~/.bashrc、~/.zshrc 等中包含 "hermes" 的 PATH 行

# 5. （可选）删除所有数据
rm -rf ~/.hermes

# 6. 停止并禁用 systemd 服务（如果有）
systemctl --user stop hermes-gateway 2>/dev/null
systemctl --user disable hermes-gateway 2>/dev/null
rm -f ~/.config/systemd/user/hermes-gateway.service
systemctl --user daemon-reload
```

**Windows (PowerShell)**：

```powershell
# 1. 停止网关和相关进程
Get-Process python,pythonw,node -ErrorAction SilentlyContinue |
  Where-Object { $_.Path -like "*hermes*" } |
  Stop-Process -Force

# 2. 删除 Scheduled Task（如果存在）
schtasks /Delete /TN "Hermes Gateway" /F 2>$null

# 3. 删除代码和工具
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes\hermes-agent"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes\git"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes\node"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes\gateway-service"
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes\bin"

# 4. 清理 User PATH（注册表）
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$entries = $userPath -split ";" | Where-Object { $_ -notlike "*hermes*" }
[Environment]::SetEnvironmentVariable("Path", ($entries -join ";"), "User")

# 5. 删除环境变量
[Environment]::SetEnvironmentVariable("HERMES_HOME", $null, "User")
[Environment]::SetEnvironmentVariable("HERMES_GIT_BASH_PATH", $null, "User")

# 6. （可选）删除所有数据
Remove-Item -Recurse -Force "$env:LOCALAPPDATA\hermes"

# 7. 删除启动项
Remove-Item "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\Hermes*" -ErrorAction SilentlyContinue
```

**Docker**：

```bash
# 停止并删除容器
docker compose down
# 或
docker stop hermes hermes-dashboard
docker rm hermes hermes-dashboard

# 删除镜像
docker rmi hermes-agent

# （可选）删除数据
rm -rf ~/.hermes
```

### 8.10.4 干净重装步骤

当遇到无法解决的问题，想要从零开始时：

1. **备份重要数据**（可选）：
   ```bash
   cp -r ~/.hermes ~/.hermes.backup
   # 备份的关键内容：.env（API Key）、config.yaml、sessions/、skills/
   ```

2. **完全卸载**：
   ```bash
   hermes uninstall --yes --full
   ```
   若卸载命令本身无法运行，按 [8.10.3 节](#8103-手动完全卸载) 手动操作。

3. **验证残留已清理**：
   ```bash
   which hermes          # 应无输出
   ls ~/.hermes 2>&1     # 应提示不存在
   ls ~/.local/bin/hermes 2>&1
   ```

4. **重启终端**（确保 PATH 已更新）。

5. **全新安装**：
   ```bash
   # Linux/macOS
   curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
   ```
   ```powershell
   # Windows
   iex (irm https://hermes-agent.nousresearch.com/install.ps1)
   ```

6. **恢复配置**（若有备份）：
   ```bash
   cp ~/.hermes.backup/.env ~/.hermes/
   cp ~/.hermes.backup/config.yaml ~/.hermes/
   # 按需恢复 sessions/、skills/ 等
   ```

7. **验证安装**：
   ```bash
   hermes --version
   hermes doctor
   ```

8. **Docker 用户干净重装**：
   ```bash
   docker compose down
   docker pull hermes-agent:latest
   # 如需清空数据：sudo rm -rf ~/.hermes
   HERMES_UID=$(id -u) HERMES_GID=$(id -g) docker compose up -d
   docker logs hermes -f
   ```

> **提示**：大多数问题不需要完全重装。优先尝试 `hermes doctor --fix`、重建虚拟环境（见 [8.8.2 节](#882-模块导入错误modulenotfounderror--importerror)）或更新到最新版本（`hermes update`）。完全重装是最后手段。
