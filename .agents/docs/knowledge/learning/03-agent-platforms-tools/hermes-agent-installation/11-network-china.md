---
title: "Hermes Agent 安装方案 - 国内网络环境优化指南"
chapter: 11
source:
  - external/libs/hermes-agent/pyproject.toml
  - external/libs/hermes-agent/package.json
  - external/libs/hermes-agent/.npmrc
  - external/libs/hermes-agent/.nvmrc
  - external/libs/hermes-agent/.python-version
  - external/libs/hermes-agent/Dockerfile
  - external/libs/hermes-agent/docker-compose.yml
  - external/libs/hermes-agent/.env.example
  - external/libs/hermes-agent/scripts/install.sh
  - external/libs/hermes-agent/scripts/install.ps1
---

# 11. 国内网络环境优化指南

本章面向位于中国大陆网络环境下的用户，汇总 Hermes Agent 安装与运行过程中涉及的所有境外资源的镜像加速方案。Hermes Agent 的安装链路需要访问 GitHub（源码克隆）、PyPI（Python 包）、npm registry（Node 包）、nodejs.org（Node 二进制）、Playwright CDN（浏览器二进制）、Docker Hub（容器镜像）、Hugging Face（模型文件）以及境外模型 API 端点；在不做任何优化时，上述任一环节都可能导致安装中断或速度极慢。

> **镜像地址验证日期**：2026-08-10。镜像源可用性会随时间变化，若遇到某个地址失效，请切换到本章列出的备用地址，或通过该镜像站的官方状态页确认。第三方公益镜像可能存在同步延迟、带宽限制或停止服务的风险，生产环境建议优先使用云厂商提供的内网镜像或自建镜像。

> **安全提示**：第三方镜像站由不同组织或个人维护，存在缓存延迟、内容篡改或停止服务的风险。安装 Python/Node 包时，`uv` 与 `npm` 均会校验包的哈希值（uv.lock / package-lock.json），可在很大程度上防止篡改；但仍建议避免在镜像站输入任何账号密码，敏感操作（推送代码、登录 API）走官方通道。

---

## 11.1 PyPI 镜像源配置

Hermes Agent 的 Python 依赖数量较多（核心依赖约 30 个，含 `cryptography`、`pydantic`、`Pillow` 等带原生扩展的包），且使用 `uv` 进行依赖解析与安装。配置 PyPI 镜像可显著提升 `uv sync` 的速度与稳定性。

### 11.1.1 可用 PyPI 镜像源列表

以下镜像均为 `pypi.org/simple` 的完整镜像，支持 PEP 503 简单索引 API，验证日期 2026-08-10：

| 镜像站 | 索引 URL | 同步频率 | 说明 |
|---|---|---|---|
| 清华大学 TUNA | `https://pypi.tuna.tsinghua.edu.cn/simple` | 5 分钟 | 最常用，带宽充足，推荐首选 |
| 北京外国语大学 BFSU | `https://mirrors.bfsu.edu.cn/pypi/web/simple` | 5 分钟 | 由 TUNA 协会维护，与 TUNA 同源 |
| 阿里云 | `https://mirrors.aliyun.com/pypi/simple/` | 15 分钟 | 企业级稳定，末尾需带斜杠 |
| 中国科学技术大学 USTC | `https://pypi.mirrors.ustc.edu.cn/simple/` | 实时 | 同步及时，推荐 |
| 腾讯云 | `https://mirrors.cloud.tencent.com/pypi/simple` | 10 分钟 | 腾讯云内网访问更佳 |
| 华为云 | `https://mirrors.huaweicloud.com/repository/pypi/simple` | 15 分钟 | 华为云内网访问更佳 |

> **选择建议**：教育网用户优先 TUNA/BFSU/USTC；云服务器用户优先对应云厂商镜像（内网流量免费且速度最快）；普通宽带用户任选其一，建议 TUNA 或阿里云。

### 11.1.2 pip 全局配置（pip.conf / pip.ini）

若使用 `pip`（Termux 路径或手动 venv 安装时使用），可通过配置文件永久设置镜像源。

**Linux / macOS**：编辑 `~/.pip/pip.conf`（或 `~/.config/pip/pip.conf`）：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

[install]
trusted-host = pypi.tuna.tsinghua.edu.cn
```

**Windows**：编辑 `%APPDATA%\pip\pip.ini`（即 `C:\Users\<用户名>\AppData\Roaming\pip\pip.ini`）：

```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

也可通过命令行直接设置：

```bash
# Linux / macOS
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple

# Windows PowerShell
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 11.1.3 项目级 pip 配置

在项目根目录创建 `pip.conf`（Linux/macOS）或 `pip.ini`（Windows），仅对该项目生效：

```ini
[global]
index-url = https://mirrors.aliyun.com/pypi/simple/
```

或在项目中使用 `requirements.txt` 时通过 `-i` 参数临时指定：

```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 11.1.4 uv 专用配置

Hermes Agent 在非 Termux 平台统一使用 `uv` 管理 Python 依赖，pip 配置不会自动被 uv 读取。uv 的镜像配置方式详见 [11.2 节](#112-uv-包管理器镜像配置)。若使用 `uv pip` 子命令（uv 的 pip 兼容接口），uv 会同时识别 `UV_INDEX_URL`、`UV_DEFAULT_INDEX` 以及标准的 `uv.toml`/`pyproject.toml` 配置。

---

## 11.2 uv 包管理器镜像配置

uv 是 Hermes Agent 的核心包管理器（见 [1.6 节](01-environment.md#16-uv-包管理器)），由 Astral 用 Rust 编写。uv 不读取 pip 的 `pip.conf`，而是使用自己的配置体系：环境变量、`uv.toml` 或 `pyproject.toml` 中的 `[tool.uv]` 表。

### 11.2.1 环境变量方式（推荐用于安装脚本）

uv 提供两个与索引相关的环境变量：

| 环境变量 | 作用 | 对应命令行参数 |
|---|---|---|
| `UV_DEFAULT_INDEX` | 设置**默认索引**，替换官方 PyPI | `--default-index` |
| `UV_INDEX` | 添加**额外索引**（可多个，空格分隔），PyPI 仍作为兜底 | `--index` |
| `UV_INDEX_URL` | pip 兼容变量，等价于 `UV_DEFAULT_INDEX` | `--index-url` |
| `UV_HTTP_TIMEOUT` | HTTP 超时时间（秒），网络慢时可调大 | `--http-timeout` |

**临时使用**（当前终端会话）：

```bash
# Linux / macOS
export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
export UV_HTTP_TIMEOUT=300

# Windows PowerShell
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
$env:UV_HTTP_TIMEOUT = "300"
```

设置后再执行安装脚本或 `uv sync`，所有 Python 包都会从镜像站下载。

**永久生效**（写入 shell 配置）：

```bash
# Linux / macOS（Bash）
echo 'export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple' >> ~/.bashrc
echo 'export UV_HTTP_TIMEOUT=300' >> ~/.bashrc
source ~/.bashrc

# Linux / macOS（Zsh）
echo 'export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple' >> ~/.zshrc
source ~/.zshrc
```

```powershell
# Windows PowerShell（永久写入用户环境变量）
[Environment]::SetEnvironmentVariable("UV_DEFAULT_INDEX", "https://pypi.tuna.tsinghua.edu.cn/simple", "User")
[Environment]::SetEnvironmentVariable("UV_HTTP_TIMEOUT", "300", "User")
```

> **注意**：Hermes 官方安装脚本会设置 `UV_NO_CONFIG=1`（见 [1.6.2 节](01-environment.md#162-安装方式)），以避免在 `sudo -u` 场景下读取到错误用户的配置。因此在运行官方安装脚本时，**环境变量方式是最可靠的镜像传递途径**——配置文件可能被 `UV_NO_CONFIG` 忽略，但环境变量始终生效。

### 11.2.2 uv.toml 配置文件（全局/项目级）

uv 支持 `uv.toml` 配置文件，结构为顶层 TOML 表（不带 `[tool.uv]` 前缀）。

**全局配置（用户级）**：

| 平台 | 路径 |
|---|---|
| Linux | `~/.config/uv/uv.toml` |
| macOS | `~/.config/uv/uv.toml` |
| Windows | `%APPDATA%\uv\uv.toml` |

创建或编辑该文件，将默认索引设为清华镜像：

```toml
[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

若需要同时配置多个索引（例如主用清华、备用阿里云）：

```toml
[[index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true

[[index]]
url = "https://mirrors.aliyun.com/pypi/simple/"
```

uv 会按索引定义顺序查询，默认索引（`default = true`）始终作为最低优先级的兜底。

**项目级配置**：在项目根目录创建 `uv.toml`，内容与全局配置相同，仅对该项目生效。`uv.toml` 的优先级高于 `pyproject.toml` 中的 `[tool.uv]` 表。

### 11.2.3 pyproject.toml 方式

也可在项目的 `pyproject.toml` 中配置（Hermes Agent 仓库本身未设置镜像，你可以在自己的项目或 fork 中添加）：

```toml
[[tool.uv.index]]
url = "https://pypi.tuna.tsinghua.edu.cn/simple"
default = true
```

> **不建议直接修改 Hermes Agent 仓库的 `pyproject.toml`** 添加镜像——这会导致 `uv.lock` 哈希校验失败或与上游产生合并冲突。请优先使用环境变量或用户级 `uv.toml`。

### 11.2.4 配置优先级

uv 的配置生效顺序（从高到低）为：

1. 命令行参数（`--default-index`、`--index`）
2. 环境变量（`UV_DEFAULT_INDEX`、`UV_INDEX`）
3. 项目级 `uv.toml`
4. 项目级 `pyproject.toml` 的 `[tool.uv]` 表
5. 用户级 `uv.toml`
6. 系统级 `/etc/uv/uv.toml`

环境变量优先级高于配置文件，因此在运行安装脚本时设置 `UV_DEFAULT_INDEX` 可以覆盖任何已存在的配置。

---

## 11.3 npm 镜像源配置

Hermes Agent 的 Node 侧依赖包括 `agent-browser`、`@streamdown/math`、Playwright、Electron（桌面版）以及 TUI/Web 前端构建依赖。npm 默认从 `registry.npmjs.org` 下载，国内访问速度慢。

### 11.3.1 可用 npm 镜像源

| 镜像站 | Registry URL | 说明 |
|---|---|---|
| 淘宝 npmmirror | `https://registry.npmmirror.com` | 最常用，同步频率高，旧域名 `registry.npm.taobao.org` 已于 2022 年停用 |
| 腾讯云 | `https://mirrors.cloud.tencent.com/npm/` | 腾讯云内网访问更佳 |
| 华为云 | `https://mirrors.huaweicloud.com/repository/npm/` | 华为云内网访问更佳 |

> 旧的 `https://registry.npm.taobao.org` 已于 2022 年停止解析，请务必使用新域名 `registry.npmmirror.com`。

### 11.3.2 命令行设置（npm config set）

```bash
# 设置全局默认镜像
npm config set registry https://registry.npmmirror.com

# 验证配置
npm config get registry

# 恢复官方源
npm config delete registry
```

### 11.3.3 .npmrc 配置文件

**全局配置**：

| 平台 | 路径 |
|---|---|
| Linux / macOS | `~/.npmrc` |
| Windows | `%USERPROFILE%\.npmrc`（即 `C:\Users\<用户名>\.npmrc`） |

编辑该文件：

```ini
registry=https://registry.npmmirror.com
```

**项目级配置**：在项目根目录创建 `.npmrc`，仅对该项目生效：

```ini
registry=https://registry.npmmirror.com
```

> **注意**：Hermes Agent 仓库根目录已有一份 `.npmrc`（见 `external/libs/hermes-agent/.npmrc`），其中配置了 `engine-strict`、`min-release-age` 等供应链安全策略，但**没有**设置 `registry`。你在项目根目录追加 `registry=...` 是安全的，但不要删除或修改已有的安全策略项。若不想改动仓库文件，使用全局 `~/.npmrc` 或环境变量即可。

### 11.3.4 环境变量方式

```bash
# Linux / macOS
export npm_config_registry=https://registry.npmmirror.com

# Windows PowerShell
$env:npm_config_registry = "https://registry.npmmirror.com"
```

也可在单次安装时临时指定：

```bash
npm install --registry=https://registry.npmmirror.com
```

### 11.3.5 作用域包（Scoped Packages）镜像

某些包需要单独配置镜像，例如 `@playwright/test` 的浏览器下载地址（见 [11.6 节](#116-playwright-浏览器下载镜像)）。可在 `.npmrc` 中按作用域配置：

```ini
registry=https://registry.npmmirror.com
@playwright/test:registry=https://registry.npmmirror.com
```

---

## 11.4 Node.js 版本管理镜像

Hermes Agent 要求 Node.js `>=22.22.0`（见 [1.5 节](01-environment.md#15-nodejs-版本要求)），官方推荐使用 Node 26。若系统自带 Node 版本不足，官方安装脚本会自动下载托管的 Node.js；若你手动使用 nvm/fnm 等版本管理器，配置国内镜像可加速 Node 二进制下载。

### 11.4.1 可用 Node.js 二进制镜像

| 镜像站 | 镜像 URL | 说明 |
|---|---|---|
| 淘宝 npmmirror | `https://npmmirror.com/mirrors/node/` | 同步及时，最常用 |
| 阿里云 | `https://mirrors.aliyun.com/nodejs-release/` | 企业级稳定 |
| 清华大学 TUNA | `https://mirrors.tuna.tsinghua.edu.cn/nodejs-release/` | 教育网优先 |
| 北外 BFSU | `https://mirrors.bfsu.edu.cn/nodejs-release/` | 与 TUNA 同源 |
| 中科大 USTC | `https://mirrors.ustc.edu.cn/node/` | 实时同步 |

### 11.4.2 nvm（Linux / macOS）

nvm 通过 `NVM_NODEJS_ORG_MIRROR` 环境变量指定下载源：

```bash
# 写入 ~/.bashrc 或 ~/.zshrc 永久生效
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node/

# 然后正常安装
nvm install 22
nvm install 26
nvm use 22
```

也可在安装 nvm 时就指定镜像：

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.0/install.sh | NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node/ bash
```

### 11.4.3 nvm-windows（Windows）

nvm-windows 的配置文件位于 `%APPDATA%\nvm\settings.txt`（或 nvm 安装目录下的 `settings.txt`），添加或修改：

```ini
node_mirror: https://npmmirror.com/mirrors/node/
npm_mirror: https://npmmirror.com/mirrors/npm/
```

然后以管理员身份运行：

```powershell
nvm install 22.22.0
nvm use 22.22.0
```

### 11.4.4 nvs

nvs 通过 `nvs remote` 命令添加远程源：

```bash
# 添加国内镜像
nvs remote node https://mirrors.bfsu.edu.cn/nodejs-release/

# 使用该源安装
nvs add node/22
nvs use node/22
```

### 11.4.5 fnm（跨平台，Rust 实现）

fnm 的环境变量为 `FNM_NODE_DIST_MIRROR`（注意不是 `FNM_MIRROR`）：

```bash
# Linux / macOS
export FNM_NODE_DIST_MIRROR=https://npmmirror.com/mirrors/node/
eval "$(fnm env --use-on-cd --shell bash)"

fnm install 22
fnm install 26
fnm use 22
```

```powershell
# Windows PowerShell（永久写入用户环境变量）
[Environment]::SetEnvironmentVariable("FNM_NODE_DIST_MIRROR", "https://npmmirror.com/mirrors/node/", "User")
fnm env --use-on-cd --shell powershell | Out-String | Invoke-Expression
fnm install 22
```

> 该环境变量名称来自 fnm 官方文档（`--node-dist-mirror` 参数对应 `FNM_NODE_DIST_MIRROR`），旧版教程中出现的 `FNM_MIRROR` 不是 fnm 识别的变量名。

### 11.4.6 n（Linux / macOS）

`n` 版本管理器通过 `NODE_MIRROR` 环境变量指定镜像：

```bash
export NODE_MIRROR=https://npmmirror.com/mirrors/node/
n 22
n 26
```

### 11.4.7 Volta

Volta 通过 `hooks.json` 配置镜像路径：

**Linux / macOS**：编辑 `~/.volta/hooks.json`

**Windows**：编辑 `%LOCALAPPDATA%\Volta\hooks.json`

```json
{
  "node": {
    "index": {
      "template": "https://mirrors.ustc.edu.cn/node/index.json"
    },
    "distro": {
      "template": "https://mirrors.ustc.edu.cn/node/v{{version}}/{{filename}}"
    }
  }
}
```

配置后正常执行 `volta install node@22` 即可。

---

## 11.5 GitHub 访问加速

Hermes Agent 的源码托管在 GitHub（`github.com/NousResearch/hermes-agent`），安装脚本需要 `git clone` 仓库，Dockerfile 还会从 GitHub Releases 下载 s6-overlay 等二进制。GitHub 在国内访问不稳定，可通过以下方式加速。

### 11.5.1 文件下载加速（Release / Raw / Archive）

对于 GitHub 上的单个文件、Release 附件或源码压缩包，可在原始 URL 前添加代理前缀。以下文件加速代理在 2026-08-10 验证可用：

| 代理服务 | 前缀 URL | 用法示例 |
|---|---|---|
| ghproxy | `https://ghproxy.net/` | `https://ghproxy.net/https://github.com/user/repo/archive/refs/heads/main.zip` |
| gh-proxy | `https://gh-proxy.com/` | `https://gh-proxy.com/https://github.com/user/repo/releases/download/v1.0/file.tar.gz` |
| moeyy | `https://moeyy.cn/gh-proxy/` | `https://moeyy.cn/gh-proxy/https://raw.githubusercontent.com/user/repo/main/file` |
| akams | `https://github.akams.cn/` | 支持 API、Git Clone、Releases、Raw 等 |

使用方式：将完整的 GitHub URL（以 `https://github.com/...` 开头）拼接到代理前缀之后。

### 11.5.2 仓库克隆加速（域名替换）

对于 `git clone`，可将 `github.com` 替换为镜像站域名：

| 镜像站 | 克隆地址格式 | 说明 |
|---|---|---|
| gitclone | `https://gitclone.com/github.com/<user>/<repo>.git` | 提供缓存克隆，适合大仓库 |
| bgithub | `https://bgithub.xyz/<user>/<repo>.git` | 直接替换域名，支持浏览与克隆 |
| kkgithub | `https://kkgithub.com/<user>/<repo>.git` | 直接替换域名 |

示例：

```bash
# 官方地址（可能慢）
git clone https://github.com/NousResearch/hermes-agent.git

# 通过 gitclone 加速
git clone https://gitclone.com/github.com/NousResearch/hermes-agent.git

# 通过 bgithub 加速
git clone https://bgithub.xyz/NousResearch/hermes-agent.git
```

> **克隆后必须改回官方远程地址**，以便后续 `hermes update` 能正常拉取更新：
> ```bash
> cd hermes-agent
> git remote set-url origin https://github.com/NousResearch/hermes-agent.git
> ```

### 11.5.3 全局 Git insteadOf 配置

若希望所有 `github.com` 的克隆自动走镜像，可配置 Git 的 URL 重写：

```bash
# 方式一：走 ghproxy 代理（适合 Release 文件）
git config --global url."https://ghproxy.net/https://github.com/".insteadOf "https://github.com/"

# 方式二：走 bgithub 镜像（适合仓库克隆）
git config --global url."https://bgithub.xyz/".insteadOf "https://github.com/"
```

取消配置：

```bash
git config --global --unset url."https://bgithub.xyz/".insteadOf
```

> **警告**：全局 `insteadOf` 会影响所有 GitHub 仓库的克隆与拉取，包括私有仓库。若需要推送代码或访问私有仓库，请不要使用全局重写，或在推送时手动指定 `git push https://github.com/user/repo.git`。

### 11.5.4 修改 hosts 文件

通过获取 GitHub 相关域名的真实 IP 并写入 hosts 文件，可绕过 DNS 污染。IP 地址会变化，建议使用自动更新工具：

- **GitHub520**：`https://raw.githubusercontent.com/521xueweihan/GitHub520/main/hosts`（本身也需代理访问，可通过 `https://ghproxy.net/` 前缀获取）
- **SwitchHosts**（跨平台 GUI 工具）：配置定时从上述 URL 同步 hosts

手动编辑 hosts 文件：

| 平台 | 路径 |
|---|---|
| Linux / macOS | `/etc/hosts` |
| Windows | `C:\Windows\System32\drivers\etc\hosts` |

添加示例（IP 需替换为当前可用 IP）：

```
140.82.114.4 github.com
185.199.108.133 raw.githubusercontent.com
```

编辑后刷新 DNS 缓存：

```bash
# Linux
sudo systemd-resolve --flush-caches

# macOS
sudo dscacheutil -flushcache

# Windows
ipconfig /flushdns
```

### 11.5.5 SSH 替代 HTTPS

若本地已配置 SSH 密钥并能通过 SSH 连接 GitHub（22 端口），使用 SSH 协议克隆通常比 HTTPS 更稳定：

```bash
git clone git@github.com:NousResearch/hermes-agent.git
```

若 22 端口被阻断，可使用 GitHub 的 443 端口 SSH 服务。在 `~/.ssh/config` 中添加：

```ssh-config
Host github.com
  HostName ssh.github.com
  Port 443
  User git
```

测试连通性：

```bash
ssh -T git@github.com
```

### 11.5.6 Gitee / GitCode 镜像

对于热门开源项目，Gitee（码云）和 GitCode（CSDN）常有官方或社区镜像。Hermes Agent 在 Gitee/GitCode 上可能存在社区镜像，但**非官方维护，可能不同步**，使用前请确认最新提交时间：

```bash
# GitCode 镜像（若存在）
git clone https://gitcode.com/mirrors/hermes-agent.git
```

> 镜像克隆后同样需要 `git remote set-url origin` 改回官方地址以接收更新。

---

## 11.6 Playwright 浏览器下载镜像

Hermes Agent 的浏览器工具依赖 Playwright 自带的 Chromium（见 Dockerfile:201 的 `npx playwright install --with-deps chromium`）。Playwright 安装 npm 包后，还需单独下载浏览器二进制文件（约 150 MB），默认从 `storage.googleapis.com` 和 GitHub Releases 下载，国内常超时。

### 11.6.1 PLAYWRIGHT_DOWNLOAD_HOST 环境变量

设置该环境变量可将浏览器下载源重定向到 npmmirror 镜像：

```bash
# Linux / macOS
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# Windows PowerShell
$env:PLAYWRIGHT_DOWNLOAD_HOST = "https://npmmirror.com/mirrors/playwright"
```

然后执行浏览器安装：

```bash
npx playwright install chromium
```

在 Hermes Agent 中，浏览器安装由安装脚本自动触发，因此在运行安装脚本**之前**导出该环境变量即可让安装过程使用镜像。

### 11.6.2 持久化配置

**项目级 `.npmrc`**（在项目根目录）：

```ini
playwright_download_host=https://npmmirror.com/mirrors/playwright
```

**环境变量持久化**：

```bash
# Linux / macOS
echo 'export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright' >> ~/.bashrc

# Windows PowerShell（永久）
[Environment]::SetEnvironmentVariable("PLAYWRIGHT_DOWNLOAD_HOST", "https://npmmirror.com/mirrors/playwright", "User")
```

### 11.6.3 Docker 构建时配置

在自建 Hermes Agent Docker 镜像时，通过 `--build-arg` 或 Dockerfile `ENV` 传入：

```dockerfile
ENV PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright
RUN npx playwright install --with-deps chromium
```

或构建时传入：

```bash
docker build \
  --build-arg PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright \
  -t hermes-agent .
```

### 11.6.4 自定义浏览器存储路径

默认情况下 Playwright 将浏览器存放在：

| 平台 | 路径 |
|---|---|
| Linux | `~/.cache/ms-playwright/` |
| macOS | `~/Library/Caches/ms-playwright/` |
| Windows | `%USERPROFILE%\AppData\Local\ms-playwright\` |

可通过 `PLAYWRIGHT_BROWSERS_PATH` 环境变量自定义：

```bash
export PLAYWRIGHT_BROWSERS_PATH=$HOME/.playwright-browsers
```

Hermes Agent 的官方 Docker 镜像将其固定为 `/opt/hermes/.playwright`（见 Dockerfile:62），以确保浏览器文件不被数据卷覆盖。

### 11.6.5 完全跳过浏览器下载

若你不需要浏览器工具（无 GUI 服务器、仅使用 CLI），可在安装时跳过 Playwright 浏览器下载：

```bash
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1
npm install
```

后续需要时再执行 `npx playwright install chromium`（届时记得配置镜像）。

---

## 11.7 Docker 镜像加速

Hermes Agent 提供官方 Docker 镜像（见 [第 5 章](05-install-docker.md)），Dockerfile 构建过程中还会拉取 `debian:13.4`、`node:26-bookworm-slim`、`ghcr.io/astral-sh/uv:...` 等基础镜像。Docker Hub 在国内访问受限，需配置 registry mirror。

> **重要提示（2024–2026 年变更）**：2024 年 6 月起，上海交大、中科大、南京大学等高校的 Docker Hub 镜像因监管要求相继下架；Docker 官方中国区镜像 `registry.docker-cn.com`、网易 `hub-mirror.c.163.com`、七牛云等也已停止服务。以下列表为 2026-08-10 仍可访问的镜像，但公益镜像稳定性不保证，建议配置多个作为备份。

### 11.7.1 可用 Docker Hub 镜像加速地址

| 镜像站 | 地址 | 说明 |
|---|---|---|
| 毫秒镜像 | `https://docker.1ms.run` | CDN 加速，推荐首选 |
| DaoCloud | `https://docker.m.daocloud.io` | 老牌企业镜像，白名单管理，可能限流 |
| 1Panel | `https://docker.1panel.live` | 限中国地区访问 |
| 耗子面板 | `https://hub.rat.dev` | 依托毫秒镜像 |
| Docker Proxy | `https://dockerproxy.net` | 由 ghproxy 团队提供 |
| 轩辕镜像 | `https://docker.xuanyuan.me` | 社区维护 |
| 腾讯云（内网） | `https://mirror.ccs.tencentyun.com` | **仅腾讯云服务器内网可用**，公网不可达 |
| 阿里云（个人） | `https://<your-id>.mirror.aliyuncs.com` | 需登录 [阿里云容器镜像服务](https://cr.console.aliyun.com/) 获取专属地址 |

### 11.7.2 配置 daemon.json

编辑 Docker 的 `daemon.json` 文件：

| 平台 | 路径 |
|---|---|
| Linux | `/etc/docker/daemon.json` |
| Windows（Docker Desktop） | 设置 → Docker Engine 中编辑 JSON |
| macOS（Docker Desktop） | 设置 → Docker Engine 中编辑 JSON |

```json
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev",
    "https://dockerproxy.net"
  ]
}
```

配置后重启 Docker：

```bash
# Linux
sudo systemctl daemon-reload
sudo systemctl restart docker

# Docker Desktop（Windows / macOS）：点击 GUI 中的 "Apply & Restart"
```

验证配置是否生效：

```bash
docker info
```

在输出中查找 `Registry Mirrors` 段落，应列出你配置的地址。

### 11.7.3 拉取测试

```bash
docker pull debian:13.4
docker pull node:26-bookworm-slim
```

若某个镜像站返回 `403` 或 `manifest unknown`，说明该站未缓存该镜像或已限流，Docker 会自动尝试列表中的下一个地址。

### 11.7.4 GHCR（GitHub Container Registry）加速

Hermes Agent 的 uv 基础镜像托管在 GHCR（`ghcr.io/astral-sh/uv`）。GHCR 不受 Docker Hub 镜像加速影响，但可通过以下方式处理：

- DaoCloud 镜像站支持 GHCR 代理：`docker.m.daocloud.io/ghcr.io/astral-sh/uv:...`
- Docker Proxy 也支持 GHCR：`dockerproxy.net/ghcr.io/...`

示例：

```bash
docker pull docker.m.daocloud.io/ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie
```

拉取后可重新打标签以匹配 Dockerfile 中的引用：

```bash
docker tag docker.m.daocloud.io/ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie \
  ghcr.io/astral-sh/uv:0.11.6-python3.13-trixie
```

### 11.7.5 docker-compose 代理配置

若使用 `docker compose` 构建或拉取镜像，`daemon.json` 中的 mirror 配置会自动生效，无需额外设置。若需要在构建时访问宿主机代理（用于 `apt`、`pip`、`npm` 等），可在 `docker-compose.yml` 或构建参数中传入：

```yaml
services:
  gateway:
    build:
      context: .
      args:
        HTTP_PROXY: http://host.docker.internal:7890
        HTTPS_PROXY: http://host.docker.internal:7890
```

---

## 11.8 Hugging Face 模型下载镜像

Hermes Agent 的可选功能会下载模型文件：本地语音转写（faster-whisper）、唤醒词（openWakeWord）等通过 `huggingface_hub` 从 Hugging Face 下载模型。Hugging Face 在国内访问不稳定。

### 11.8.1 HF_ENDPOINT 环境变量

设置 `HF_ENDPOINT` 为国内镜像 `hf-mirror.com`：

```bash
# Linux / macOS
export HF_ENDPOINT=https://hf-mirror.com

# Windows PowerShell
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

该环境变量被 `huggingface_hub` Python 库和 `transformers`、`datasets` 等库官方识别，会自动将所有下载请求重定向到镜像站。

### 11.8.2 持久化配置

```bash
# Linux / macOS（Bash）
echo 'export HF_ENDPOINT=https://hf-mirror.com' >> ~/.bashrc
source ~/.bashrc

# Windows PowerShell（永久）
[Environment]::SetEnvironmentVariable("HF_ENDPOINT", "https://hf-mirror.com", "User")
```

也可写入 Hermes Agent 的 `~/.hermes/.env` 文件（Linux/macOS）或 `%LOCALAPPDATA%\hermes\.env`（Windows）：

```dotenv
HF_ENDPOINT=https://hf-mirror.com
```

### 11.8.3 加速下载（hf_transfer）

对于大模型文件（数百 MB 至数 GB），可启用 `hf_transfer` 多线程下载加速：

```bash
uv pip install hf_transfer
export HF_HUB_ENABLE_HF_TRANSFER=1
```

> `hf_transfer` 使用多线程分块下载，速度更快但错误提示不够友好；若下载失败，可临时关闭该变量后重试。

### 11.8.4 使用 modelscope（魔搭社区）替代

国内用户也可使用阿里魔搭社区（ModelScope）下载模型，它托管了大量 Hugging Face 模型的镜像：

```bash
uv pip install modelscope
```

```python
from modelscope import snapshot_download
model_dir = snapshot_download('pengzhendong/faster-whisper-base')
```

---

## 11.9 模型 API 国内可访问替代方案

Hermes Agent 默认通过境外模型 API（OpenAI、Anthropic、OpenRouter、Fireworks 等）进行推理。这些 API 在中国大陆可能无法直接访问。Hermes Agent 已内置对多家国内模型提供商的支持，可在 `.env` 中直接配置。

### 11.9.1 国内模型提供商一览

以下提供商验证日期 2026-08-10。"Hermes 原生支持"列表示 Hermes Agent 是否内置了该提供商的专用适配器（有专用适配器时使用对应 Key 变量即可，无需手动设置 base URL）：

| 提供商 | 代表模型 | 国内 API Base URL | Hermes 原生支持 | Key 获取地址 |
|---|---|---|---|---|
| DeepSeek | DeepSeek-V3、DeepSeek-R1、deepseek-v4 | `https://api.deepseek.com/v1` | ✅ `DEEPSEEK_API_KEY` | https://platform.deepseek.com |
| 智谱 GLM | GLM-4-Plus、GLM-4.5、GLM-5、GLM-5.2 | `https://open.bigmodel.cn/api/paas/v4/` | ✅ `GLM_API_KEY` | https://open.bigmodel.cn |
| 月之暗面 Kimi | kimi-k2、moonshot-v1 | `https://api.moonshot.cn/v1` | ✅ `KIMI_CN_API_KEY` | https://platform.moonshot.cn |
| 阿里通义千问 | Qwen3、Qwen-Max | `https://dashscope.aliyuncs.com/compatible-mode/v1` | ✅ `DASHSCOPE_API_KEY` | https://dashscope.console.aliyun.com |
| MiniMax（国内） | MiniMax-M1、abab6.5 | `https://api.minimaxi.com/anthropic` 或 `/v1` | ✅ `MINIMAX_CN_API_KEY` | https://www.minimaxi.com |
| 小米 MiMo | mimo-v2-pro、mimo-v2-flash | `https://api.xiaomimimo.com/v1` | ✅ `XIAOMI_API_KEY` | https://platform.xiaomimimo.com |
| 腾讯 TokenHub |混元、DeepSeek 等托管模型 | `https://tokenhub.tencentmaas.com/v1` | ✅ `TOKENHUB_API_KEY` | https://tokenhub.tencentmaas.com |
| 字节豆包（火山方舟） | Doubao-1.5-pro、Doubao-Seed | `https://ark.cn-beijing.volces.com/api/v3` | ❌ 需用 `OPENAI_BASE_URL` | https://console.volcengine.com/ark |
| 百度千帆 | ERNIE-4.5、ERNIE-X1 | `https://qianfan.baidubce.com/v2` | ❌ 需用 `OPENAI_BASE_URL` | https://console.bce.baidu.com/qianfan |
| 讯飞星火 | Spark-4.0、Spark-X1 | `https://spark-api-open.xf-yun.com/v1` | ❌ 需用 `OPENAI_BASE_URL` | https://xinghuo.xfyun.cn |
| 腾讯混元 | hunyuan-turbos、hunyuan-large | `https://api.hunyuan.cloud.tencent.com/v1` | ❌ 需用 `OPENAI_BASE_URL` | https://console.cloud.tencent.com/hunyuan |

### 11.9.2 在 Hermes Agent 中配置

Hermes Agent 支持两种配置方式：使用专用提供商字段，或通过 OpenAI 兼容接口配置任意提供商。

**方式一：使用内置的专用提供商字段（推荐）**

编辑 `~/.hermes/.env`（Windows 为 `%LOCALAPPDATA%\hermes\.env`），以下示例可按需取消注释：

```dotenv
# === DeepSeek（OpenAI 兼容，base_url 已内置） ===
DEEPSEEK_API_KEY=sk-your-deepseek-key
# 如需自定义端点可设置：DEEPSEEK_BASE_URL=https://api.deepseek.com/v1

# === 智谱 GLM ===
# 国际版默认 https://api.z.ai/api/paas/v4；国内用户须覆盖为 open.bigmodel.cn
GLM_API_KEY=your-zhipu-key
GLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4/

# === 月之暗面 Kimi（国内版） ===
# KIMI_CN_API_KEY 对应的国内端点 https://api.moonshot.cn/v1 已硬编码，无需再设 KIMI_BASE_URL
KIMI_CN_API_KEY=your-moonshot-cn-key

# === 阿里通义千问（DashScope） ===
# 国际版默认 dashscope-intl.aliyuncs.com；国内用户须覆盖为 dashscope.aliyuncs.com
DASHSCOPE_API_KEY=sk-your-dashscope-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1

# === MiniMax（国内版） ===
# 默认走 Anthropic 兼容端点 https://api.minimaxi.com/anthropic；
# 如需 OpenAI 兼容格式，可覆盖为 /v1
MINIMAX_CN_API_KEY=your-minimax-cn-key
# MINIMAX_CN_BASE_URL=https://api.minimaxi.com/v1

# === 小米 MiMo ===
XIAOMI_API_KEY=your-xiaomi-key
# XIAOMI_BASE_URL=https://api.xiaomimimo.com/v1

# === 腾讯 TokenHub ===
# TOKENHUB_API_KEY=your-tencent-tokenhub-key
# TOKENHUB_BASE_URL=https://tokenhub.tencentmaas.com/v1
```

> 以上字段及默认端点均来自 Hermes Agent 源码中的提供商注册表（`hermes_cli/auth.py` 的 `PROVIDER_CONFIGS`）与 `.env.example`。Kimi、MiniMax 区分国际版与国内版 Key，国内用户应使用 `KIMI_CN_API_KEY` / `MINIMAX_CN_API_KEY`；智谱与通义千问的默认端点为国际版，国内用户须通过 `GLM_BASE_URL` / `DASHSCOPE_BASE_URL` 覆盖为国内端点。

配置后通过交互式向导选择模型：

```bash
hermes setup
# 或直接设置默认提供商
hermes config set model.provider deepseek
hermes config set model.default deepseek-chat
```

**方式二：通过 OpenAI 兼容接口配置其他提供商**

对于 Hermes 未内置专用适配器的提供商（字节豆包、百度千帆、讯飞星火、腾讯混元等），使用 `OPENAI_API_KEY` + `OPENAI_BASE_URL` 指向该提供商的 OpenAI 兼容端点：

```dotenv
# === 字节豆包（火山方舟 Ark） ===
OPENAI_API_KEY=your-volcengine-api-key
OPENAI_BASE_URL=https://ark.cn-beijing.volces.com/api/v3
# 模型名使用接入点 ID（ep-xxxxxxxx）或模型名 doubao-seed-1-6-250615

# === 百度千帆 ===
# OPENAI_API_KEY=your-qianfan-api-key
# OPENAI_BASE_URL=https://qianfan.baidubce.com/v2
# 模型名示例：ernie-4.5-turbo-128k、ernie-x1-8k-preview

# === 讯飞星火 ===
# OPENAI_API_KEY=your-xunfei-api-key
# OPENAI_BASE_URL=https://spark-api-open.xf-yun.com/v1
# 模型名示例：generalv3.5、4.0Ultra

# === 腾讯混元 ===
# OPENAI_API_KEY=your-hunyuan-api-key
# OPENAI_BASE_URL=https://api.hunyuan.cloud.tencent.com/v1
# 模型名示例：hunyuan-turbos-latest、hunyuan-large
```

> **注意**：使用 `OPENAI_BASE_URL` 时，Hermes 会将该端点当作 OpenAI API 调用。确保提供商的接口与 OpenAI `/chat/completions` 格式兼容（以上列出的提供商均已兼容）。`OPENAI_BASE_URL` 末尾不要加 `/chat/completions`，只填到 `/v1`（豆包 Ark 为 `/api/v3`）。这种方式下模型提供商在 Hermes 中显示为 `openai`，但实际请求会发往你配置的端点。

### 11.9.3 通过 OpenRouter 等聚合平台中转

若仍希望使用境外模型（Claude、GPT-4 等）但无法直连，可通过支持国内访问的聚合平台中转：

- **OpenRouter**（`https://openrouter.ai`）：聚合数百种模型，国内可通过 `OPENROUTER_API_KEY` 配置，但域名本身在国内可能需要代理。
- **国内中转站**：存在大量第三方 OpenAI 中转服务，可通过 `OPENAI_BASE_URL` 配置，但**安全性无法保证**，API Key 和对话内容会经过中转服务器，请勿用于敏感场景。

### 11.9.4 本地模型（Ollama / vLLM）

完全离线的方案是在本地运行开源模型，通过 OpenAI 兼容接口提供服务：

```dotenv
# 本地 Ollama（默认端口 11434）
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
# 模型名示例：qwen3:14b、deepseek-r1:14b、llama3.1:8b
```

```dotenv
# 本地 vLLM / llama.cpp / Xinference 等
OPENAI_API_KEY=local
OPENAI_BASE_URL=http://localhost:8000/v1
```

本地模型无需访问境外 API，但需要足够的 GPU/内存资源（详见 [1.2 节](01-environment.md#12-硬件要求)）。

---

## 11.10 完整的国内安装示例

本节给出一个从零开始、所有环节均走国内镜像的完整安装流程，以 Linux/macOS 为主，Windows PowerShell 的差异会单独标注。

### 11.10.1 第一步：系统依赖准备

**Linux（Ubuntu / Debian）**：

```bash
sudo apt update
sudo apt install -y git curl xz-utils ca-certificates
```

**macOS**：

```bash
xcode-select --install
# 若已安装 Homebrew
brew install git curl
```

**Windows**：以当前用户身份打开 PowerShell（无需管理员），无需预装 Git（安装脚本会自动下载 MinGit）。

### 11.10.2 第二步：导出所有镜像环境变量

在终端中执行（Linux/macOS）：

```bash
# === uv / PyPI 镜像 ===
export UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
export UV_HTTP_TIMEOUT=300

# === npm 镜像 ===
export npm_config_registry=https://registry.npmmirror.com

# === Node.js 二进制镜像（若需手动安装 Node） ===
export NVM_NODEJS_ORG_MIRROR=https://npmmirror.com/mirrors/node/
# fnm 用户使用：
# export FNM_NODE_DIST_MIRROR=https://npmmirror.com/mirrors/node/

# === Playwright 浏览器镜像 ===
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright

# === Hugging Face 模型镜像 ===
export HF_ENDPOINT=https://hf-mirror.com
```

Windows PowerShell：

```powershell
# === uv / PyPI 镜像 ===
$env:UV_DEFAULT_INDEX = "https://pypi.tuna.tsinghua.edu.cn/simple"
$env:UV_HTTP_TIMEOUT = "300"

# === npm 镜像 ===
$env:npm_config_registry = "https://registry.npmmirror.com"

# === Playwright 浏览器镜像 ===
$env:PLAYWRIGHT_DOWNLOAD_HOST = "https://npmmirror.com/mirrors/playwright"

# === Hugging Face 模型镜像 ===
$env:HF_ENDPOINT = "https://hf-mirror.com"
```

> **持久化建议**：将上述 `export` 语句追加到 `~/.bashrc` 或 `~/.zshrc`，Windows 用户通过 `[Environment]::SetEnvironmentVariable(..., "User")` 写入用户环境变量，这样后续运行 `hermes update` 也会自动使用镜像。

### 11.10.3 第三步：配置 Docker 镜像加速（仅 Docker 安装方式）

若计划使用 Docker 部署，先按 [11.7 节](#117-docker-镜像加速) 配置 `/etc/docker/daemon.json` 并重启 Docker：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<'EOF'
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.m.daocloud.io",
    "https://docker.1panel.live",
    "https://hub.rat.dev"
  ]
}
EOF
sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 11.10.4 第四步：配置 Git 以加速克隆（可选）

若直连 GitHub 速度尚可，可跳过此步。否则配置全局 URL 重写：

```bash
# 使用 bgithub 镜像加速克隆
git config --global url."https://bgithub.xyz/".insteadOf "https://github.com/"
```

> 安装完成后，建议改回官方地址以便接收更新：
> ```bash
> git config --global --unset url."https://bgithub.xyz/".insteadOf
> ```

### 11.10.5 第五步：运行安装脚本

**Linux / macOS / WSL2**：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash
```

若 `hermes-agent.nousresearch.com` 本身无法访问，可通过 GitHub 代理获取脚本：

```bash
curl -fsSL https://ghproxy.net/https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
```

**Windows PowerShell**：

```powershell
iex (irm https://hermes-agent.nousresearch.com/install.ps1)
```

若官方域名不可达，通过代理获取：

```powershell
$script = (Invoke-WebRequest -Uri "https://ghproxy.net/https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.ps1").Content
Invoke-Expression $script
```

安装脚本会自动完成：下载托管 uv → 下载 Python 3.11（走 PyPI 镜像）→ 克隆源码 → `uv sync` 安装 Python 依赖 → 安装 Node.js → `npm install`（走 npm 镜像）→ `npx playwright install`（走 Playwright 镜像）。

### 11.10.6 第六步：配置国内模型 API

安装完成后，复制 `.env.example` 为 `.env` 并编辑：

```bash
# Linux / macOS
cp ~/.hermes/hermes-agent/.env.example ~/.hermes/.env
nano ~/.hermes/.env
```

```powershell
# Windows PowerShell
Copy-Item "$env:LOCALAPPDATA\hermes\hermes-agent\.env.example" "$env:LOCALAPPDATA\hermes\.env"
notepad "$env:LOCALAPPDATA\hermes\.env"
```

至少配置一个国内模型提供商的 API Key（参考 [11.9 节](#119-模型-api-国内可访问替代方案)）。以 DeepSeek 为例：

```dotenv
DEEPSEEK_API_KEY=sk-your-deepseek-key
```

或使用阿里通义千问（需覆盖默认国际端点）：

```dotenv
DASHSCOPE_API_KEY=sk-your-dashscope-key
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

### 11.10.7 第七步：验证安装

```bash
# 打开新终端，确认命令可用
hermes --version

# 运行环境诊断
hermes doctor

# 启动交互式设置（选择模型、配置工具）
hermes setup
```

`hermes doctor` 的 "API Connectivity" 部分会测试你配置的模型端点是否可达。若显示绿色对勾，说明国内 API 配置成功。

### 11.10.8 第八步：基础对话测试

```bash
hermes
```

在 TUI 中发送一条测试消息，例如"你好，请用一句话介绍你自己"。若能正常收到回复，说明全链路（Python 依赖 → Node 工具 → 模型 API）均已正常工作。

### 11.10.9 全流程镜像配置速查表

为方便查阅，以下汇总了各环节的镜像环境变量及推荐值：

| 环节 | 环境变量 / 配置 | 推荐值 |
|---|---|---|
| Python 包（uv） | `UV_DEFAULT_INDEX` | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| Python 包（pip） | `pip.conf` 的 `index-url` | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| Node 包 | `npm_config_registry` / `.npmrc` | `https://registry.npmmirror.com` |
| Node 二进制（nvm） | `NVM_NODEJS_ORG_MIRROR` | `https://npmmirror.com/mirrors/node/` |
| Node 二进制（fnm） | `FNM_NODE_DIST_MIRROR` | `https://npmmirror.com/mirrors/node/` |
| Playwright 浏览器 | `PLAYWRIGHT_DOWNLOAD_HOST` | `https://npmmirror.com/mirrors/playwright` |
| Docker Hub | `daemon.json` 的 `registry-mirrors` | `https://docker.1ms.run` 等 |
| Hugging Face 模型 | `HF_ENDPOINT` | `https://hf-mirror.com` |
| GitHub 文件下载 | URL 前缀 | `https://ghproxy.net/` |
| 模型 API（DeepSeek） | `DEEPSEEK_API_KEY` | 国内直连，无需代理 |
| 模型 API（通义千问） | `DASHSCOPE_API_KEY` + `DASHSCOPE_BASE_URL` | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

---

## 11.11 镜像故障排查与回滚

### 11.11.1 镜像同步延迟

国内镜像同步官方源通常有 5–15 分钟延迟。若 `uv sync` 或 `npm install` 报 `Package not found`（某包刚发布不到半小时），可临时切回官方源：

```bash
# uv 临时使用官方源
UV_DEFAULT_INDEX=https://pypi.org/simple uv sync

# npm 临时使用官方源
npm install --registry=https://registry.npmjs.org
```

Hermes Agent 的核心依赖均精确锁定（`pyproject.toml` 中使用 `==X.Y.Z`），且 `uv.lock` 已固定哈希，因此同步延迟对已发布版本的安装影响很小。

### 11.11.2 镜像证书错误

若遇到 `SSL: CERTIFICATE_VERIFY_FAILED`，通常是企业代理进行了 HTTPS 中间人拦截，或镜像站证书异常。排查方法见 [8.1.3 节](08-troubleshooting.md#813-npm-安装失败) 中的 TLS 证书问题处理。

### 11.11.3 回滚到官方源

如需恢复所有官方源，按以下操作：

```bash
# 清除 uv 环境变量
unset UV_DEFAULT_INDEX
# 或删除 ~/.config/uv/uv.toml 中的 [[index]] 配置

# 清除 npm 镜像
npm config delete registry
# 或删除 ~/.npmrc 中的 registry 行

# 清除 Git insteadOf
git config --global --unset url."https://bgithub.xyz/".insteadOf

# 清除 Playwright 镜像
unset PLAYWRIGHT_DOWNLOAD_HOST

# 清除 Hugging Face 镜像
unset HF_ENDPOINT
```

Windows PowerShell 中使用 `[Environment]::SetEnvironmentVariable("VAR", $null, "User")` 删除持久化的环境变量（或在"系统属性 → 环境变量"中手动删除）。

### 11.11.4 验证当前生效的镜像配置

```bash
# 查看 uv 索引配置
uv config --help 2>/dev/null || cat ~/.config/uv/uv.toml 2>/dev/null
echo "UV_DEFAULT_INDEX=$UV_DEFAULT_INDEX"

# 查看 npm 当前 registry
npm config get registry

# 查看 Docker mirror
docker info 2>/dev/null | grep -A5 "Registry Mirrors"

# 查看 Git URL 重写
git config --global --get-regexp 'url\..*\.insteadof'

# 查看 Playwright / HF 配置
echo "PLAYWRIGHT_DOWNLOAD_HOST=$PLAYWRIGHT_DOWNLOAD_HOST"
echo "HF_ENDPOINT=$HF_ENDPOINT"
```

完成本章配置后，Hermes Agent 在国内网络环境下的安装与运行应不再依赖任何境外直连（模型 API 除外，已通过国内提供商替代）。如仍遇到网络问题，结合 [第 8 章](08-troubleshooting.md#81-网络问题) 的网络问题排查流程定位具体环节。
