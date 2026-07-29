---
id: github-cli-wiki-06-faq-troubleshooting
title: "常见问题与排错指南"
source: "https://cli.github.com/manual/"
date: "2026-07-24"
category: "learning"
tags: ["github-cli", "gh", "faq", "troubleshooting", "debug", "error-handling", "authentication", "network"]
---

# 常见问题与排错指南

本章汇总 GitHub CLI（`gh`）最常见的 12 个问题及其解决方案，涵盖认证失败、网络代理、版本升级、SSH 密钥、API 限流、权限问题、Shell 补全、安装故障、企业版连接、Token 作用域等场景。每个问题包含问题描述、错误症状、根本原因和逐步解决方案。

> **建议**：遇到问题时，先按 [第 13 节排错方法论](#13-排错方法论) 快速诊断，再定位到具体问题的解决方案。

---

## 1. 认证失败：Token 过期或权限不足

### 1.1 问题描述

执行 `gh` 命令时提示认证失败，通常表现为 Token 已过期或权限范围不足。

### 1.2 错误症状

```bash
$ gh repo list
To get started with GitHub CLI, please run: gh auth login
Alternatively, populate the GH_TOKEN environment variable with a GitHub personal access token.

$ gh auth status
github.com
  X Not logged in to github.com
```

或：

```bash
$ gh api /user/repos
gh: HTTP 401: Bad credentials (https://api.github.com/user/repos)
```

### 1.3 根本原因

- Personal Access Token（PAT）已过期（经典 Token 有有效期限制）
- Token 权限范围不足（缺少 `repo`、`read:org` 等必要权限）
- Token 被手动撤销
- 配置文件 `~/.config/gh/hosts.yml` 中的 Token 已损坏

### 1.4 解决方案

#### 方案一：刷新 Token（推荐）

```bash
# 刷新当前认证凭证
gh auth refresh
```

`gh auth refresh` 会引导你重新认证，同时保留原有配置。执行后按提示选择认证方式，如果是 Web 方式，会自动打开浏览器完成 OAuth 流程。

如需刷新特定权限范围的 Token：

```bash
# 刷新并指定 Token 所需权限范围
gh auth refresh --scopes "repo,read:org,workflow"
```

#### 方案二：重新登录

```bash
# 完全重新登录
gh auth login
```

交互式流程会引导你重新完成认证。如果之前登录过，建议先登出：

```bash
gh auth logout
gh auth login
```

#### 方案三：通过环境变量设置 Token

```bash
# 生成新的 PAT 后，通过环境变量设置
export GH_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx

# 验证
gh auth status
```

> **Token 生成地址**：[GitHub Settings → Personal access tokens](https://github.com/settings/tokens)。确保勾选 `repo`、`read:org`、`workflow` 权限。

---

## 2. 认证失败：`gh auth status` 显示未登录

### 2.1 问题描述

执行任意 `gh` 命令均提示未登录，`gh auth status` 显示 `Not logged in`。

### 2.2 错误症状

```bash
$ gh auth status
github.com
  X Not logged in to github.com
```

### 2.3 根本原因

- 从未执行过 `gh auth login`
- 配置文件 `~/.config/gh/hosts.yml` 不存在或为空
- 环境变量 `GH_TOKEN` 或 `GITHUB_TOKEN` 未设置

### 2.4 解决方案

```bash
# 执行交互式登录
gh auth login
```

按提示依次选择：

1. **登录目标**：`GitHub.com`（或 `GitHub Enterprise Server`）
2. **Git 协议**：`HTTPS`（推荐）或 `SSH`
3. **认证方式**：`Login with a web browser`（推荐）或 `Paste an authentication token`

认证完成后，验证状态：

```bash
gh auth status
```

期望输出：

```
github.com
  ✓ Logged in to github.com as <your-username> (~/.config/gh/hosts.yml)
  ✓ Git operations for github.com configured to use https protocol.
  ✓ Token: ghp_********************
  ✓ Token scopes: gist, read:org, repo, workflow
```

> **提示**：如果需要在自动化脚本中登录，参考 [安装与配置指南](01-installation.md) 中非交互式登录一节。

---

## 3. 网络代理问题：HTTP_PROXY / HTTPS_PROXY 配置

### 3.1 问题描述

在企业网络环境或使用代理时，`gh` 无法连接到 GitHub API 服务器。

### 3.2 错误症状

```bash
$ gh repo list
gh: unable to connect to github.com: connect: connection timed out
```

或：

```bash
$ gh api /user
gh: HTTP 403: connection refused (https://api.github.com/user)
```

### 3.3 根本原因

- 网络环境需要通过 HTTP/HTTPS 代理访问外网
- 代理地址或端口配置错误
- 代理需要认证但未提供凭据

### 3.4 解决方案

#### 方案一：通过 `gh config` 设置代理

```bash
# 设置 HTTP 代理
gh config set http_proxy http://proxy.example.com:8080

# 设置 HTTPS 代理
gh config set https_proxy http://proxy.example.com:8080

# 验证配置
gh config list
```

#### 方案二：通过环境变量设置代理

```bash
# Linux / macOS
export HTTP_PROXY=http://proxy.example.com:8080
export HTTPS_PROXY=http://proxy.example.com:8080

# Windows PowerShell
$env:HTTP_PROXY = "http://proxy.example.com:8080"
$env:HTTPS_PROXY = "http://proxy.example.com:8080"
```

#### 方案三：带认证的代理

```bash
# 代理需要用户名/密码认证
export HTTP_PROXY=http://username:password@proxy.example.com:8080
export HTTPS_PROXY=http://username:password@proxy.example.com:8080

# 或使用 gh config
gh config set http_proxy http://username:password@proxy.example.com:8080
```

#### 方案四：取消代理

```bash
# 如果之前配置了错误的代理，取消设置
gh config set http_proxy ""
gh config set https_proxy ""

# 或取消环境变量
unset HTTP_PROXY
unset HTTPS_PROXY
```

> **注意**：`gh` 同时支持大写和小写的环境变量名（`HTTP_PROXY` / `http_proxy`），但建议统一使用大写以避免兼容性问题。

---

## 4. 版本升级：旧版本问题

### 4.1 问题描述

使用的 `gh` 版本过旧，导致某些命令不可用或行为异常，或者遇到已知 Bug。

### 4.2 错误症状

```bash
$ gh pr create --draft
unknown flag: --draft

$ gh --version
gh version 2.14.0 (2022-01-01)
```

### 4.3 根本原因

- `gh` 版本过旧，不支持新功能
- 旧版本存在已知 Bug，在新版本中已修复
- 通过系统包管理器安装的版本滞后于官方发布

### 4.4 解决方案

#### 检查当前版本

```bash
gh --version
```

#### 方案一：`gh upgrade` 命令（v2.62+ 支持）

```bash
# 直接在命令行中升级
gh upgrade
```

> **注意**：`gh upgrade` 仅在通过官方安装脚本或 MSI 安装的版本中可用。通过 Homebrew、WinGet、apt 等包管理器安装的版本不适用此命令。

#### 方案二：Homebrew（macOS / Linux）

```bash
brew upgrade gh
```

#### 方案三：WinGet（Windows）

```powershell
winget upgrade --id GitHub.cli
```

#### 方案四：Scoop（Windows）

```powershell
scoop update gh
```

#### 方案五：apt（Debian/Ubuntu）

```bash
sudo apt update
sudo apt upgrade gh
```

#### 方案六：手动下载安装

从 [GitHub CLI 发布页面](https://github.com/cli/cli/releases/latest) 下载最新版本，覆盖安装。

---

## 5. SSH 密钥问题：`Permission denied (publickey)`

### 5.1 问题描述

使用 SSH 协议执行 Git 操作时，服务器拒绝连接，提示公钥认证失败。

### 5.2 错误症状

```bash
$ gh repo clone owner/repo
Cloning into 'repo'...
Permission denied (publickey).
fatal: Could not read from remote repository.

Please make sure you have the correct access rights
and the repository exists.
```

### 5.3 根本原因

- 本地 SSH 密钥未添加到 GitHub 账号
- SSH 密钥文件权限不正确
- 本地 `~/.ssh/config` 配置错误
- `gh` 配置的 Git 协议为 SSH 但本地无有效密钥

### 5.4 解决方案

#### 方案一：使用 `gh auth login` 自动配置 SSH

```bash
# 重新登录并选择 SSH 协议
gh auth login --git-protocol ssh
```

`gh` 会自动检测现有 SSH 密钥，如果找到则上传到 GitHub；如果未找到，则引导生成新密钥并上传。

#### 方案二：手动添加 SSH 密钥

```bash
# 使用 gh ssh-key add 命令添加 SSH 密钥
gh ssh-key add ~/.ssh/id_ed25519.pub --title "My Work Laptop"
```

#### 方案三：生成并上传新 SSH 密钥

```bash
# 生成 Ed25519 密钥（推荐）
ssh-keygen -t ed25519 -C "your_email@example.com"

# 将公钥上传到 GitHub
gh ssh-key add ~/.ssh/id_ed25519.pub --title "Generated by gh CLI"
```

#### 方案四：临时切换到 HTTPS 协议

```bash
# 如果 SSH 暂时无法解决，可以切换到 HTTPS 协议
gh config set git_protocol https

# 重新克隆
gh repo clone owner/repo
```

#### 方案五：验证 SSH 连接

```bash
# 测试 SSH 连接
ssh -T git@github.com

# 期望输出
# Hi <username>! You've successfully authenticated, but GitHub does not provide shell access.
```

如果测试失败，检查：

1. 密钥是否已添加到 SSH Agent：`ssh-add -l`
2. 密钥文件权限：`chmod 600 ~/.ssh/id_ed25519`
3. `~/.ssh/config` 是否正确配置：

```
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_ed25519
```

---

## 6. API 速率限制：`gh api` 返回 403

### 6.1 问题描述

调用 `gh api` 或批量操作时收到 403 响应，提示 API 速率限制已耗尽。

### 6.2 错误症状

```bash
$ gh api /repos/owner/repo/releases
gh: HTTP 403: API rate limit exceeded for user IP. (https://api.github.com/repos/owner/repo/releases)

$ gh api /rate_limit
{
  "resources": {
    "core": {
      "limit": 60,
      "remaining": 0,
      "reset": 1690000000
    }
  }
}
```

### 6.3 根本原因

GitHub API 对未认证请求有严格的速率限制——每小时仅 60 次。已认证请求的限额为每小时 5,000 次。当 `gh` 未正确认证或 Token 无效时，请求会回退到未认证的限额。

### 6.4 解决方案

#### 步骤 1：确认认证状态

```bash
gh auth status
```

如果显示 `Not logged in`，需要先登录：

```bash
gh auth login
```

#### 步骤 2：查看当前速率限制

```bash
# 查看当前速率限制详情
gh api /rate_limit --jq '.rate'
```

或查看完整信息：

```bash
gh api /rate_limit
```

#### 步骤 3：对比认证 vs 未认证限额

| 状态 | 每小时限额 | 适用场景 |
|------|-----------|----------|
| 未认证 | 60 次 / 小时 | 仅按 IP 地址计数 |
| 已认证（PAT） | 5,000 次 / 小时 | 按用户计数 |
| GitHub Actions（GITHUB_TOKEN） | 1,000 次 / 小时 | 按仓库计数 |
| GitHub Enterprise Cloud | 15,000 次 / 小时 | 企业用户 |

#### 步骤 4：等待限额重置

```bash
# 查看重置时间（Unix 时间戳）
gh api /rate_limit --jq '.rate.reset'

# 转换为可读时间
date -d @$(gh api /rate_limit --jq '.rate.reset')
```

> **提示**：如果频繁触发限额，考虑使用 `gh api` 的 `--cache` 参数缓存响应（v2.64+），或使用 GraphQL 查询合并多个 REST 请求。

---

## 7. `gh repo clone` 权限拒绝：私有仓库访问

### 7.1 问题描述

尝试克隆私有仓库时提示权限不足，即使已通过 `gh auth login` 登录。

### 7.2 错误症状

```bash
$ gh repo clone owner/private-repo
Cloning into 'private-repo'...
remote: Repository not found.
fatal: repository 'https://github.com/owner/private-repo.git/' not found
```

或：

```bash
$ gh repo clone owner/private-repo
gh: HTTP 404: Not Found (https://api.github.com/repos/owner/private-repo)
```

### 7.3 根本原因

- Token 缺少 `repo` 权限范围，无法访问私有仓库
- Token 是 fine-grained PAT，但未授权该特定仓库
- 账号本身没有该仓库的访问权限（非协作者）

### 7.4 解决方案

#### 步骤 1：检查 Token 权限范围

```bash
gh auth status
```

查看输出中的 `Token scopes` 行，确认是否包含 `repo`：

```
✓ Token scopes: gist, read:org, repo, workflow
```

#### 步骤 2：如果缺少 `repo` 权限，刷新 Token

```bash
# 刷新 Token 并添加 repo 权限范围
gh auth refresh --scopes "repo,read:org,workflow"
```

#### 步骤 3：如果使用 fine-grained PAT

Fine-grained（细粒度）PAT 需要明确授权到具体仓库，检查步骤：

1. 访问 [GitHub Settings → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. 确认 Token 的 `Repository access` 是否包含目标仓库
3. 如果仅授权了部分仓库，需要编辑 Token 添加目标仓库

```bash
# 重新登录，使用新的 fine-grained PAT
gh auth login --with-token
```

#### 步骤 4：确认账号有仓库访问权限

```bash
# 在浏览器中确认是否可以访问仓库
gh repo view owner/private-repo --web
```

如果浏览器中也无法访问，说明你的 GitHub 账号没有该仓库的访问权限，需要联系仓库管理员添加协作者权限。

---

## 8. `gh pr create` 推送失败：无推送权限

### 8.1 问题描述

创建 PR 时，`gh pr create` 提示无法推送分支到远程仓库，通常因为对目标仓库没有写入权限。

### 8.2 错误症状

```bash
$ gh pr create --title "feat: 新功能"
remote: Permission to owner/repo.git denied to <username>.
fatal: unable to access 'https://github.com/owner/repo.git/': The requested URL returned error: 403

To https://github.com/owner/repo.git
 ! [remote rejected] feature/my-change -> feature/my-change (permission denied)
```

### 8.3 根本原因

- 对目标仓库没有写入权限（非协作者）
- 目标仓库是组织仓库，且限制了向仓库直接推送的权限
- 分支保护规则阻止了向该分支的推送

### 8.4 解决方案

#### 方案一：Fork 工作流（推荐）

对于非协作者仓库，使用 Fork 工作流：

```bash
# 1. Fork 目标仓库
gh repo fork owner/repo --clone

# 2. 在 Fork 仓库中创建特性分支
cd repo
git checkout -b feature/my-change

# 3. 提交代码并推送
git add .
git commit -m "feat: 新功能"
git push -u origin feature/my-change

# 4. 向上游提交 PR（注意 --head 指定 Fork 仓库的分支）
gh pr create \
  --title "feat: 新功能" \
  --body "详细描述变更内容" \
  --base main \
  --head "your-username:feature/my-change"
```

#### 方案二：申请仓库写入权限

如果你是协作者但尚未获得写入权限，联系仓库管理员在 `Settings → Collaborators` 中添加你的账号。

#### 方案三：检查分支保护规则

如果是因为分支保护规则阻止推送：

```bash
# 确认目标分支的保护规则
gh api /repos/owner/repo/branches/main/protection
```

如果分支被保护，可能需要：
- 通过 PR 方式提交变更（而非直接推送）
- 确保分支名称符合命名规范
- 获取必要的审查批准

---

## 9. Shell 补全不生效

### 9.1 问题描述

按照 [安装与配置指南](01-installation.md) 配置了 Shell 补全，但输入 `gh` 后按 Tab 键没有补全提示。

### 9.2 错误症状

```bash
$ gh pr <Tab>
# 没有任何补全提示，或显示文件列表而非命令列表
```

### 9.3 根本原因

- 补全脚本未正确加载到当前 Shell 会话
- 补全脚本安装路径不正确
- 使用了不兼容的 Shell 版本
- 配置文件（`.bashrc` / `.zshrc`）中有语法错误导致补全加载失败

### 9.4 解决方案

#### Bash

```bash
# 1. 确认补全脚本能正常生成
gh completion -s bash

# 2. 将补全脚本添加到 .bashrc
echo 'eval "$(gh completion -s bash)"' >> ~/.bashrc

# 3. 重新加载配置
source ~/.bashrc

# 4. 验证
gh <Tab>
```

> **注意**：WSL 和 Git Bash 环境可能需要使用 `~/.bash_profile` 而非 `~/.bashrc`。

#### Zsh

```bash
# 1. 确认补全脚本能正常生成
gh completion -s zsh

# 2. 将补全脚本添加到 .zshrc
echo 'eval "$(gh completion -s zsh)"' >> ~/.zshrc

# 3. 重新加载配置
source ~/.zshrc

# 4. 验证
gh <Tab>
```

如果使用 Oh My Zsh，也可以将补全放入补全目录：

```bash
gh completion -s zsh > "${fpath[1]}/_gh"
```

#### Fish

```bash
# 确保补全目录存在
mkdir -p ~/.config/fish/completions

# 生成补全脚本
gh completion -s fish > ~/.config/fish/completions/gh.fish

# 重新加载 Shell
exec fish
```

#### PowerShell

```powershell
# 将补全脚本添加到 PowerShell 配置文件
gh completion -s powershell | Out-File -Append -FilePath $PROFILE

# 重新加载配置
. $PROFILE

# 验证
gh <Tab>
```

#### 通用检查清单

1. **确认 `gh` 可执行**：`gh --version`
2. **确认补全脚本生成正常**：`gh completion -s <你的shell>`
3. **确认配置文件已加载**：重新打开终端或执行 `source` 命令
4. **确认无语法错误**：检查 `~/.bashrc` 或 `~/.zshrc` 是否有语法错误

---

## 10. `gh` 命令未找到：PATH 问题

### 10.1 问题描述

安装 `gh` 后，在终端中输入 `gh` 提示命令未找到。

### 10.2 错误症状

```bash
$ gh --version
bash: gh: command not found
```

```powershell
PS C:\> gh --version
gh: The term 'gh' is not recognized as a name of a cmdlet, function, script file, or executable program.
```

### 10.3 根本原因

- `gh` 可执行文件所在目录不在 `PATH` 环境变量中
- 安装后未重新打开终端，环境变量未生效
- 安装过程被中断，`gh` 未能正确安装
- 在 Windows 上，MSI 安装后需要重启终端

### 10.4 解决方案

#### 步骤 1：确认 `gh` 是否已安装

**Windows**：

```powershell
# 检查常见安装路径
Get-Command gh -ErrorAction SilentlyContinue
Test-Path "C:\Program Files\GitHub CLI\gh.exe"
Test-Path "$env:LOCALAPPDATA\Programs\GitHub CLI\gh.exe"
```

**macOS / Linux**：

```bash
# 检查常见安装路径
which gh
ls /usr/local/bin/gh
ls /opt/homebrew/bin/gh  # macOS Apple Silicon
```

#### 步骤 2：手动添加到 PATH

**Windows**：

```powershell
# 临时添加到当前会话
$env:Path += ";C:\Program Files\GitHub CLI"

# 永久添加（需要管理员权限）
[Environment]::SetEnvironmentVariable(
    "Path",
    [Environment]::GetEnvironmentVariable("Path", "User") + ";C:\Program Files\GitHub CLI",
    "User"
)
```

**macOS / Linux**：

```bash
# 临时添加到当前会话
export PATH="/usr/local/bin:$PATH"

# 永久添加到 .bashrc 或 .zshrc
echo 'export PATH="/usr/local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

#### 步骤 3：重新安装

如果 `gh` 可执行文件根本不存在，重新安装：

```bash
# macOS
brew install gh

# Windows
winget install --id GitHub.cli

# Linux (Debian/Ubuntu)
sudo apt install gh
```

> **提示**：安装完成后，务必重新打开终端窗口，使 PATH 环境变量生效。

---

## 11. GitHub Enterprise Server 连接问题

### 11.1 问题描述

连接 GitHub Enterprise Server（GHES）时，出现主机名无法解析、SSL 证书错误或认证失败等问题。

### 11.2 错误症状

```bash
$ gh auth login --hostname github.internal.example.com
error dialing host: lookup github.internal.example.com: no such host

$ gh api /user --hostname github.internal.example.com
gh: HTTP 401: x509: certificate signed by unknown authority
```

### 11.3 根本原因

- GHES 主机名无法解析（DNS 配置问题）
- GHES 使用自签名 SSL 证书，客户端不信任该证书
- 未使用 `--hostname` 参数或 `GH_HOST` 环境变量指定 GHES 地址
- 企业网络环境需要 VPN 或内网访问

### 11.4 解决方案

#### 方案一：确认主机名可解析

```bash
# 测试主机名解析
nslookup github.internal.example.com

# 或
ping github.internal.example.com

# 如果无法解析，检查 VPN 连接或 DNS 配置
```

#### 方案二：登录时指定正确的主机名

```bash
# 使用 --hostname 参数指定企业实例地址
gh auth login --hostname github.internal.example.com
```

或通过环境变量：

```bash
export GH_HOST=github.internal.example.com
gh auth login
```

#### 方案三：处理自签名 SSL 证书

如果 GHES 使用自签名证书，需要将证书添加到系统信任链：

**Linux**：

```bash
# 下载企业证书
openssl s_client -connect github.internal.example.com:443 -showcerts </dev/null 2>/dev/null | \
  openssl x509 -outform PEM > /tmp/github-enterprise.crt

# 添加到系统信任链
sudo cp /tmp/github-enterprise.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**Windows**：

```powershell
# 导入证书到受信任的根证书颁发机构
Import-Certificate -FilePath "C:\path\to\github-enterprise.crt" -CertStoreLocation "Cert:\LocalMachine\Root"
```

**macOS**：

```bash
# 添加到钥匙串
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain github-enterprise.crt
```

#### 方案四：使用环境变量跳过 SSL 验证（不推荐）

```bash
# 仅在开发/测试环境使用，生产环境必须配置正确的证书
export GH_INSECURE=1
```

> **警告**：`GH_INSECURE` 会跳过 SSL 证书验证，存在安全风险。仅在无法配置证书的临时测试场景使用，生产环境必须配置正确的证书。

#### 方案五：多账号管理

```bash
# 同时登录 GitHub.com 和 GHES
gh auth login --hostname github.com
gh auth login --hostname github.internal.example.com

# 查看所有已登录主机
gh auth status

# 针对不同主机执行命令
gh repo list --hostname github.internal.example.com
```

---

## 12. `gh auth login --with-token` 作用域问题

### 12.1 问题描述

使用 `gh auth login --with-token` 传入 Token 后，某些命令提示权限不足，尽管 Token 本身有效。

### 12.2 错误症状

```bash
$ echo "github_pat_xxxxxxxxxxxx" | gh auth login --with-token
✓ Logged in as username

$ gh issue list
gh: HTTP 403: Resource not accessible by integration (https://api.github.com/repos/owner/repo/issues)
```

### 12.3 根本原因

- 使用了 **fine-grained PAT**（细粒度个人访问令牌），但该 Token 的作用域或仓库权限不足
- Fine-grained PAT 需要明确指定可访问的仓库列表和权限范围
- 细粒度 Token 的 `--with-token` 行为与经典 PAT 不同

### 12.4 解决方案

#### 经典 PAT vs Fine-grained PAT 对比

| 特性 | 经典 PAT（Classic） | 细粒度 PAT（Fine-grained） |
|------|-------------------|--------------------------|
| 权限范围 | 宽泛的 scope（`repo`、`workflow` 等） | 精确的权限（`Contents: Read`、`Issues: Write` 等） |
| 仓库范围 | 所有仓库 | 指定仓库列表 |
| 有效期 | 最长 7 天（或永不过期，不推荐） | 最长 1 年 |
| 适用场景 | 个人开发、脚本工具 | 组织级安全策略、最小权限原则 |

#### 方案一：使用经典 PAT（推荐用于 `gh` CLI）

```bash
# 1. 在 GitHub 上生成经典 PAT
# 访问：https://github.com/settings/tokens
# 勾选：repo, read:org, workflow, gist

# 2. 使用 Token 登录
echo "ghp_xxxxxxxxxxxxxxxxxxxx" | gh auth login --with-token

# 3. 验证
gh auth status
```

#### 方案二：正确配置 Fine-grained PAT

如果必须使用 fine-grained PAT，确保正确配置：

1. 访问 [GitHub Settings → Fine-grained tokens](https://github.com/settings/tokens?type=beta)
2. 创建新 Token 时：
   - **Resource owner**：选择你的个人账号或组织
   - **Repository access**：选择 `All repositories` 或手动指定目标仓库
   - **Permissions**：添加以下权限：
     - `Contents: Read and write`
     - `Issues: Read and write`
     - `Pull requests: Read and write`
     - `Metadata: Read`（自动包含）
     - `Workflows: Read and write`（如需 CI/CD）

```bash
# 使用 fine-grained PAT 登录
echo "github_pat_xxxxxxxxxxxx" | gh auth login --with-token
```

#### 方案三：检查当前 Token 类型和权限

```bash
# 查看 Token 权限范围
gh auth status

# 测试 Token 是否有效
gh api /user

# 测试特定权限
gh api /repos/owner/repo/issues
```

如果 Token 权限不足，重新生成 Token 并重新登录：

```bash
gh auth logout
gh auth login --with-token
```

---

## 13. 排错方法论

当遇到 `gh` 相关问题时，按照以下四步流程系统性地诊断和定位问题。

### 13.1 第一步：检查版本

```bash
# 确认 gh 版本
gh --version

# 确认是否是最新版本（对比 GitHub Releases）
# https://github.com/cli/cli/releases/latest
```

如果版本过旧（超过 6 个月），先升级到最新版本（参见 [第 4 节](#4-版本升级旧版本问题)）。

### 13.2 第二步：检查认证

```bash
# 检查认证状态
gh auth status

# 检查 Token 详情
gh auth token

# 测试 API 连通性
gh api /user
```

关注以下信息：
- 是否已登录（`Logged in` vs `Not logged in`）
- Token 权限范围（`Token scopes`）
- 是否有多个主机登录

### 13.3 第三步：检查配置

```bash
# 查看所有配置
gh config list

# 检查 Git 协议
gh config get git_protocol

# 检查代理设置
gh config get http_proxy

# 检查认证配置文件
cat ~/.config/gh/hosts.yml
```

关注以下配置：
- `git_protocol`：`https` 还是 `ssh`
- `http_proxy`：代理是否配置正确
- `hosts.yml`：是否存在且格式正确

### 13.4 第四步：检查环境

```bash
# 检查环境变量
env | grep -i gh
env | grep -i proxy
env | grep -i github

# 检查网络连通性
curl -I https://api.github.com

# 检查 SSH 连接（如果使用 SSH 协议）
ssh -T git@github.com

# 开启调试模式（查看详细请求/响应日志）
export GH_DEBUG=api
gh repo list
unset GH_DEBUG
```

环境变量对照表：

| 环境变量 | 预期值 | 排查时关注 |
|---------|-------|-----------|
| `GH_TOKEN` | `ghp_...` 或 `github_pat_...` | 是否设置、是否过期 |
| `GITHUB_TOKEN` | 仅在 Actions 中设置 | 是否与 `GH_TOKEN` 冲突 |
| `GH_HOST` | 主机名 | 是否指向正确的 GitHub 实例 |
| `GH_DEBUG` | `api` | 调试时启用，排查后关闭 |
| `HTTP_PROXY` / `HTTPS_PROXY` | 代理地址 | 端口、协议是否正确 |
| `NO_PROXY` | 排除的域名 | 是否误排除了 `api.github.com` |

### 13.5 快速诊断决策树

```mermaid
graph TD
    Start[遇到 gh 问题] --> A{gh 命令是否可执行?}
    A -->|否| B["[问题 10](#10-gh-命令未找到-path-问题): PATH 配置"]
    A -->|是| C{gh auth status 是否正常?}
    C -->|未登录| D["[问题 2](#2-认证失败gh-auth-status-显示未登录): 执行 gh auth login"]
    C -->|Token 异常| E{"错误类型?"}
    E -->|401/403| F["[问题 1](#1-认证失败token-过期或权限不足): Token 过期/权限不足"]
    E -->|速率限制| G["[问题 6](#6-api-速率限制gh-api-返回-403): API 限流"]
    C -->|正常| H{网络是否可达?}
    H -->|代理问题| I["[问题 3](#3-网络代理问题http_proxy-https_proxy-配置): 代理配置"]
    H -->|企业版| J["[问题 11](#11-github-enterprise-server-连接问题): GHES 连接"]
    H -->|正常| K{具体操作失败?}
    K -->|git clone 失败| L{"使用什么协议?"}
    L -->|SSH| M["[问题 5](#5-ssh-密钥问题permission-denied-publickey): SSH 密钥"]
    L -->|HTTPS| N["[问题 7](#7-gh-repo-clone-权限拒绝私有仓库访问): 仓库权限"]
    K -->|PR 操作失败| O["[问题 8](#8-gh-pr-create-推送失败无推送权限): 推送权限"]
    K -->|补全不生效| P["[问题 9](#9-shell-补全不生效): Shell 补全"]
    K -->|Token 作用域| Q["[问题 12](#12-gh-auth-login---with-token-作用域问题): Token 类型"]
    K -->|版本问题| R["[问题 4](#4-版本升级旧版本问题): 版本升级"]
```

---

## 14. 相关资源

- [安装与配置指南](01-installation.md) — 安装 `gh` 并完成认证
- [基础命令指南](02-basic-commands.md) — 核心命令参考
- [PR 工作流指南](03-pr-workflow.md) — 完整 PR 操作流程
- [GitHub CLI 官方文档](https://cli.github.com/manual/) — 完整命令参考
- [GitHub 官方文档 - 认证](https://docs.github.com/en/authentication) — Token 管理与安全最佳实践
- [GitHub 官方文档 - API 速率限制](https://docs.github.com/en/rest/using-the-rest-api/rate-limits-for-the-rest-api) — 速率限制详解
- [GitHub 官方文档 - SSH 密钥](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) — SSH 连接配置