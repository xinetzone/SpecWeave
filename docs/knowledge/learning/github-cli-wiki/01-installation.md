---
id: github-cli-wiki-01-installation
title: "安装与配置指南"
source: "https://cli.github.com/manual/gh_auth_login"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "installation", "authentication", "configuration", "setup"]
---

# 安装与配置指南

本章介绍 GitHub CLI（`gh`）在各主流操作系统上的安装方法、认证流程、Shell 补全配置以及环境变量设置。

## 1. 版本检查

安装完成后，首先验证 `gh` 是否安装成功以及版本信息：

```bash
gh --version
```

输出示例：

```
gh version 2.60.0 (2026-01-15)
https://github.com/cli/cli/releases/latest
```

> **提示**：如果输出中不包含版本号，说明 `gh` 未正确安装或 PATH 环境变量未配置，请回到对应平台的安装步骤重新检查。

## 2. Windows 安装

### 2.1 WinGet（推荐）

```powershell
winget install --id GitHub.cli
```

或指定版本：

```powershell
winget install --id GitHub.cli --version 2.60.0
```

### 2.2 Scoop

```powershell
scoop bucket add main
scoop install gh
```

### 2.3 MSI 安装包

从 [GitHub CLI 发布页面](https://github.com/cli/cli/releases/latest) 下载 `.msi` 安装包：

- **64 位**：`gh_<version>_windows_amd64.msi`
- **32 位**：`gh_<version>_windows_386.msi`
- **ARM64**：`gh_<version>_windows_arm64.msi`

下载后双击安装包，按照向导完成安装。安装完成后，建议重新打开终端以使 PATH 环境变量生效。

## 3. macOS 安装

### 3.1 Homebrew（推荐）

```bash
brew install gh
```

升级到最新版本：

```bash
brew upgrade gh
```

### 3.2 MacPorts

```bash
sudo port install gh
```

## 4. Linux 安装

### 4.1 Debian/Ubuntu（apt）

```bash
(type -p wget >/dev/null || sudo apt-get install wget -y) \
&& sudo mkdir -p -m 755 /etc/apt/keyrings \
&& out=$(mktemp) && wget -nv -O$out https://cli.github.com/packages/githubcli-archive-keyring.gpg \
&& cat $out | sudo tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
&& sudo chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
&& echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
&& sudo apt update \
&& sudo apt install gh -y
```

### 4.2 Fedora/RHEL（dnf）

```bash
sudo dnf install 'dnf-command(config-manager)'
sudo dnf config-manager --add-repo https://cli.github.com/packages/rpm/gh-cli.repo
sudo dnf install gh
```

### 4.3 Arch Linux（pacman）

```bash
sudo pacman -S github-cli
```

### 4.4 openSUSE（zypper）

```bash
sudo zypper addrepo https://cli.github.com/packages/rpm/gh-cli.repo
sudo zypper ref
sudo zypper install gh
```

### 4.5 通用方案：预编译二进制

从 [GitHub CLI 发布页面](https://github.com/cli/cli/releases/latest) 下载对应架构的 `.tar.gz` 包，解压后将 `gh` 可执行文件放入 `PATH`：

```bash
tar -xzf gh_<version>_linux_amd64.tar.gz
sudo cp gh_<version>_linux_amd64/bin/gh /usr/local/bin/
```

## 5. 认证登录

`gh` 需要认证后才能访问 GitHub 上的仓库。使用 `gh auth login` 完成首次认证。

### 5.1 交互式登录

```bash
gh auth login
```

交互式流程会依次提示以下问题：

```
? What account do you want to log into?  [Use arrows to move, type to filter]
> GitHub.com
  GitHub Enterprise Server

? What is your preferred protocol for Git operations?  [Use arrows to move, type to filter]
> HTTPS
  SSH

? How would you like to authenticate GitHub CLI?  [Use arrows to move, type to filter]
> Login with a web browser
  Paste an authentication token
```

### 5.2 Web 浏览器认证流程（推荐）

选择 `Login with a web browser` 后：

1. 终端会显示一个 8 位验证码，同时自动打开浏览器
2. 在浏览器中登录 GitHub 账号（如已登录则跳过）
3. 输入终端显示的验证码
4. 授权 GitHub CLI 访问你的账号
5. 终端提示 `✓ Logged in as <username>`，认证完成

```bash
gh auth login
```

输出示例：

```
! First copy your one-time code: ABCD-1234
Press Enter to open github.com in your browser...
✓ Authentication complete.
- gh config set -h github.com git_protocol https
✓ Configured git protocol
✓ Logged in as octocat
```

### 5.3 Token 认证

选择 `Paste an authentication token`，然后在 GitHub 上生成 Personal Access Token（PAT）：

1. 访问 [GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)](https://github.com/settings/tokens)
2. 点击 "Generate new token (classic)"
3. 勾选所需权限（至少需要 `repo`、`read:org`、`workflow` 权限）
4. 生成并复制 Token
5. 回到终端粘贴 Token

```bash
gh auth login
```

输出示例：

```
? Paste an authentication token: ****************************************
- gh config set -h github.com git_protocol https
✓ Configured git protocol
✓ Logged in as octocat
```

### 5.4 SSH 协议认证

如果选择 SSH 协议，`gh` 会自动检测已有的 SSH 密钥或引导创建新密钥：

```bash
gh auth login -p ssh
```

流程：

1. 自动检测 `~/.ssh/id_rsa.pub`、`~/.ssh/id_ed25519.pub` 等现有密钥
2. 若无可用密钥，提示创建新的 SSH 密钥对
3. `gh` 自动将公钥上传到你的 GitHub 账号
4. 终端确认 SSH 连接成功

### 5.5 非交互式登录（CI/CD）

在自动化环境中，通过环境变量传入 Token 进行非交互式认证：

```bash
echo "$GH_TOKEN" | gh auth login --with-token
```

或直接设置环境变量，`gh` 会自动读取：

```bash
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

## 6. 认证状态验证

随时检查当前认证状态：

```bash
gh auth status
```

输出示例（已登录）：

```
github.com
  ✓ Logged in to github.com as octocat (~/.config/gh/hosts.yml)
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: ghp_********************
  ✓ Token scopes: gist, read:org, repo, workflow
```

输出示例（未登录）：

```
github.com
  X Not logged in to github.com
```

### 6.1 查看所有认证主机的状态

```bash
gh auth status --hostname github.com
```

### 6.2 查看 Token 详情

```bash
gh auth token
```

### 6.3 登出

```bash
gh auth logout
```

按提示选择要登出的账号即可。

## 7. Shell 补全配置

`gh` 支持主流 Shell 的自动补全，提升命令行操作效率。

### 7.1 Bash

```bash
gh completion -s bash | sudo tee /etc/bash_completion.d/gh
```

或追加到用户级配置（WSL / macOS 默认使用 `~/.bash_profile` 或 `~/.bashrc`）：

```bash
echo 'eval "$(gh completion -s bash)"' >> ~/.bashrc
source ~/.bashrc
```

### 7.2 Zsh

```bash
echo 'eval "$(gh completion -s zsh)"' >> ~/.zshrc
source ~/.zshrc
```

如果使用 Oh My Zsh，也可将补全文件放入补全目录：

```bash
gh completion -s zsh > "${fpath[1]}/_gh"
```

### 7.3 Fish

```bash
gh completion -s fish > ~/.config/fish/completions/gh.fish
```

### 7.4 PowerShell

```powershell
gh completion -s powershell | Out-String | Invoke-Expression
```

如需持久化，将补全脚本添加到 PowerShell 配置文件 (`$PROFILE`)：

```powershell
gh completion -s powershell >> $PROFILE
```

重新打开 PowerShell 窗口后生效。

## 8. 配置管理

`gh config` 用于管理 `gh` 的全局配置项。配置以 `hostname` 为维度存储，默认存储在 `~/.config/gh/config.yml`。

### 8.1 查看当前配置

```bash
gh config list
```

输出示例：

```
git_protocol=https
editor=vim
prompt=enabled
pager=less
```

### 8.2 设置 Git 协议

```bash
gh config set git_protocol ssh
```

可选值：`https`、`ssh`。

### 8.3 设置默认编辑器

```bash
gh config set editor "code --wait"
```

当 `gh` 需要打开编辑器时（如 `gh pr create` 编写 PR 描述），将使用此编辑器。常用编辑器配置：

| 编辑器 | 配置值 |
|-------|-------|
| VS Code | `code --wait` |
| Vim | `vim` |
| Nano | `nano` |
| Sublime Text | `subl -w` |
| Notepad++ | `"C:\Program Files\Notepad++\notepad++.exe" -multiInst -notabbar -nosession -noPlugin` |

### 8.4 设置 HTTP 代理

```bash
gh config set http_proxy http://proxy.example.com:8080
```

### 8.5 设置默认分页器

```bash
gh config set pager "less -R"
```

若想禁用分页器：

```bash
gh config set pager cat
```

### 8.6 重置配置项

```bash
gh config set git_protocol ""
```

将配置项设为空字符串即恢复默认值。

## 9. GitHub Enterprise Server 配置

`gh` 同时支持 GitHub.com 和 GitHub Enterprise Server（GHES）。

### 9.1 登录到 GHES

使用 `--hostname` 参数指定企业实例地址：

```bash
gh auth login --hostname github.example.com
```

或通过环境变量指定：

```bash
export GH_HOST=github.example.com
gh auth login
```

### 9.2 多账号管理

`gh` 可以同时登录多个 GitHub 账号（包括 GitHub.com 和 GHES），配置以 hostname 为维度独立存储。

```bash
# 登录 GitHub.com 个人账号
gh auth login --hostname github.com

# 登录企业 GitHub
gh auth login --hostname github.example.com
```

查看所有已登录的主机：

```bash
gh auth status
```

输出示例：

```
github.com
  ✓ Logged in to github.com as personal-user (~/.config/gh/hosts.yml)
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: ghp_********************

github.example.com
  ✓ Logged in to github.example.com as work-user (~/.config/gh/hosts.yml)
  ✓ Git operations for github.example.com configured to use https protocol.
  ✓ Token: ghp_********************
```

### 9.3 企业环境变量

针对 GHES 环境，使用专门的 Token 环境变量：

```bash
export GH_ENTERPRISE_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
```

## 10. 环境变量

`gh` 支持以下环境变量，用于覆盖默认行为和配置：

| 环境变量 | 用途 | 示例 |
|---------|------|------|
| `GH_TOKEN` | GitHub 认证 Token（优先于 `GITHUB_TOKEN`） | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `GITHUB_TOKEN` | GitHub 认证 Token（`GH_TOKEN` 未设置时生效） | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `GH_HOST` | 默认 GitHub 主机名 | `github.com` 或 `github.example.com` |
| `GH_ENTERPRISE_TOKEN` | GitHub Enterprise Server 专用 Token | `ghp_xxxxxxxxxxxxxxxxxxxx` |
| `GH_REPO` | 默认仓库（格式：`owner/repo`） | `octocat/Hello-World` |
| `GH_NO_UPDATE_NOTIFIER` | 设为任意值禁用更新通知 | `true` |
| `GH_CONFIG_DIR` | 覆盖默认配置目录 | `/path/to/gh/config` |
| `GH_PAGER` | 分页器命令（覆盖 `gh config` 中的设置） | `less -R` |
| `GH_EDITOR` | 编辑器命令（覆盖 `gh config` 中的设置） | `code --wait` |
| `GH_PROMPT_DISABLED` | 设为任意值禁用交互式提示 | `true` |
| `GH_DEBUG` | 开启调试日志（API 请求/响应详情） | `api` |
| `GH_PATH` | `gh` 可执行文件搜索路径 | `/usr/local/bin/gh` |

### 10.1 常用环境变量设置示例

```bash
# 设置认证 Token
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 设置默认仓库，后续命令无需指定 --repo
export GH_REPO=octocat/Hello-World

# 开启 API 调试模式
export GH_DEBUG=api

# 设置默认编辑器
export GH_EDITOR="code --wait"
```

> **注意**：`GH_TOKEN` 的优先级高于 `GITHUB_TOKEN`。当两者同时设置时，`gh` 使用 `GH_TOKEN`。`GITHUB_TOKEN` 主要用于与 GitHub Actions 的兼容。

### 10.2 GitHub Actions 中的 Token

在 GitHub Actions 工作流中，`GITHUB_TOKEN` 会被自动注入，无需额外配置：

```yaml
steps:
  - name: Checkout
    uses: actions/checkout@v4
  - name: Create Issue
    run: gh issue create --title "CI Failure" --body "Workflow failed on ${{ github.sha }}"
    env:
      GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

- ← [返回目录](README.md) | [下一章：基础命令全览](02-basic-commands.md) →