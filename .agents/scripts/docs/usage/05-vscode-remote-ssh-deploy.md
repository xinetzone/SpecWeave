---
id: "scripts-usage-vscode-remote-ssh-deploy"
title: "VS Code Remote-SSH 下载慢/卡住问题解决指南"
source: "deploy-vscode-server.ps1实战沉淀"
---
# VS Code Remote-SSH 下载慢/卡住问题解决指南

本文档系统梳理 VS Code Remote-SSH 连接 Linux 服务器时 "Downloading and installing remote server" 下载卡住问题的根因、多种解决方案与排障方法。

---

## 一、问题现象

使用 VS Code Remote-SSH 扩展连接远端 Linux 服务器时，VS Code 需要在远端下载并安装 VS Code Server。在国内网络环境下，这一过程经常出现以下问题：

| 现象 | 典型表现 |
|------|---------|
| **下载卡住** | 进度条长时间停留在 0% 或某个百分比不动 |
| **下载超时** | 等待数分钟后提示 "Could not fetch remote environment" 或连接失败 |
| **反复重试** | 每次连接都重新下载，始终无法完成 |
| **版本不匹配** | 下载完成后提示版本与本地 VS Code 不一致，要求重新下载 |

**根本原因**：VS Code 默认从 Microsoft CDN（`update.code.visualstudio.com`）下载 server 包，国内访问该 CDN 速度极慢或超时。VS Code 版本更新频繁（约每月一个版本），每次更新后都需要重新下载对应版本的 server 包。

---

## 二、解决方案速查表

根据使用场景选择合适方案：

| 方案 | 适用场景 | 难度 | 耗时 | 是否一劳永逸 |
|------|---------|------|------|-------------|
| [方案A：修改设置](#方案a修改设置让远端自动下载) | 远端服务器能访问外网但速度一般 | ⭐ | 1分钟 | ❌ 每次更新需重新设置 |
| [方案B：自动化脚本](#方案b自动化脚本推荐) | 远端无法访问外网/下载极慢，需快速部署 | ⭐⭐ | 2-5分钟 | ✅ 每次VS Code更新后运行一次 |
| [方案C：手动部署](#方案c手动部署) | 不想用脚本，需要完全控制每一步 | ⭐⭐⭐ | 5-15分钟 | ❌ 需手动操作 |
| [方案D：配置代理](#方案d配置代理) | 远端有可用代理服务器 | ⭐⭐ | 5分钟 | ✅ 配置后自动生效 |

---

## 三、方案A：修改设置（让远端自动下载）

最简单的方案——让 VS Code 从本地下载 server 包再传输到远端，避免远端直接访问 Microsoft CDN。

### 操作步骤

1. 在 VS Code 中按 `Ctrl+Shift+P`（macOS: `Cmd+Shift+P`）打开命令面板
2. 输入 `Preferences: Open User Settings (JSON)` 打开用户设置 JSON
3. 添加以下配置：

```json
{
    "remote.SSH.localServerDownload": "always"
}
```

4. 保存后重新连接 Remote-SSH

### 原理

- `remote.SSH.localServerDownload` 控制 server 包的下载位置
- `"always"` 表示始终在**本地**下载，再通过 SCP 上传到远端
- `"auto"`（默认值）会让 VS Code 自行判断，通常选择在远端下载导致卡住
- `"off"` 表示始终在远端下载（最慢，不推荐国内用户使用）

### 局限性

- 本地下载速度取决于访问 Microsoft CDN 的速度
- 如果本地也无法快速访问 CDN，此方案效果有限
- VS Code 更新后仍需等待传输过程
- 传输过程没有详细进度，难以判断是否卡住

---

## 四、方案B：自动化脚本（推荐）

使用 [`deploy-vscode-server.ps1`](../../deploy-vscode-server.ps1) 脚本一键完成：自动检测 VS Code 版本 → 本地快速下载 server 包 → SCP 上传 → 远端解压安装 → 验证。脚本内置详细进度日志，可精确定位传输卡住的位置。

### 前提条件

| 条件 | 说明 |
|------|------|
| 操作系统 | Windows 10 1809+ 或 Windows 11（自带 OpenSSH 客户端） |
| PowerShell | PowerShell 5.1 或 PowerShell 7+ |
| SSH 连通性 | 本地能通过 `ssh` 连接到远端服务器（密钥免密或密码登录均可） |
| 本地网络 | 本地能访问 `update.code.visualstudio.com`（浏览器下载或代理均可） |

### 快速使用

**基本用法**（自动检测所有参数）：

```powershell
.\.agents\scripts\deploy-vscode-server.ps1 -Server <服务器IP> -User <用户名>
```

> **注意**：`-Host` 也是 `-Server` 的别名，两者等效。之前文档中使用 `-Host` 的命令均可正常工作。

**示例**：

```powershell
# 连接 root@10.16.11.3，默认端口22
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.3 -User root

# 自定义端口
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.3 -User myuser -Port 2222

# 指定架构（自动检测失败时使用）
.\.agents\scripts\deploy-vscode-server.ps1 -Server server.example.com -User dev -Arch arm64

# 手动指定 Commit ID（自动检测失败时使用）
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.3 -User root -CommitId abc123def456...

# 强制重新安装（远端已有但损坏时使用）
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.3 -User root -Force

# 保留本地下载的压缩包（方便手动上传到多台服务器）
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.3 -User root -KeepArchive
```

### 参数说明

| 参数 | 必需 | 默认值 | 说明 |
|------|------|--------|------|
| `-Server`（别名 `-Host`） | ✅ | - | 远端服务器 IP 或域名 |
| `-User` | ✅ | - | SSH 登录用户名 |
| `-Port` | ❌ | 22 | SSH 端口 |
| `-Arch` | ❌ | 自动检测 | 远端架构：`x64` / `arm64` / `armhf` |
| `-CommitId` | ❌ | 自动检测 | VS Code Commit ID（40位十六进制） |
| `-KeepArchive` | ❌ | False | 保留本地下载的压缩包不清理 |
| `-Force` | ❌ | False | 强制重新安装，即使远端已存在 |

### 执行流程

脚本自动执行以下 6 个步骤，每步都有明确的日志输出：

```
[STEP] 前置环境检查
[STEP] 检测 VS Code Commit ID       ← 从本地 product.json 或 code --version 获取
[STEP] 检测远端服务器架构           ← SSH uname -m 自动识别 x64/arm64/armhf
[STEP] 下载 VS Code Server          ← 本地下载，支持缓存
[STEP] 上传 VS Code Server 到远端   ← SCP 上传，带实时进度日志
[STEP] 远端解压安装                 ← bash 脚本自动解压+权限设置+验证
```

### SCP 传输进度日志解读

脚本在 SCP 上传阶段提供详细进度信息，方便判断是否卡住：

```
[INFO] SCP 上传详情：
  本地文件: C:\Users\xxx\AppData\Local\Temp\vscode-server-deploy\vscode-server-linux-x64-xxx.tar.gz
  文件大小: 58.23 MB (61059832 bytes)
  目标路径: root@10.16.11.3:/tmp/vscode-server-deploy-xxx/vscode-server.tar.gz

  [14:23:01] 开始传输...
  [4s] 正在建立连接/认证（文件尚未开始传输）...        ← 正常：连接建立中
  [12.0s] 已传输: 12.56MB / 58.23MB (21.6%) | 速度: 1046.7KB/s | 剩余约: 44s
  [22.1s] 已传输: 28.45MB / 58.23MB (48.9%) | 速度: 1287.3KB/s | 剩余约: 23s
  [32.3s] 已传输: 45.12MB / 58.23MB (77.5%) | 速度: 1396.8KB/s | 剩余约: 9s
  ✓ 文件大小校验通过（本地 58.23MB = 远端 58.23MB）
  传输耗时: 38.2秒 | 平均速度: 1.52MB/s
```

**正常状态**：每 10 秒左右会看到进度更新，速度和剩余时间在合理范围内。

**异常状态判断**：

| 日志表现 | 可能原因 | 处理方式 |
|---------|---------|---------|
| 超过 20 秒仍停留在"正在建立连接/认证" | SSH 密码认证卡住（脚本无法交互输入密码） | 配置 SSH 密钥免密登录，或手动输一次密码后密钥会被记住 |
| 超过 40 秒未收到任何数据（脚本自动终止） | 网络不通/SSH 连接被防火墙拦截 | 手动执行 `ssh -p 22 user@host` 测试连通性 |
| 传输中途速度归零不再增长 | 网络中断/SSH 保活超时 | 检查网络稳定性，考虑使用 `rsync --partial` 断点续传 |
| 文件大小不一致警告 | SCP 传输不完整 | 使用 `-Force` 参数重新运行 |

### 远端安装日志解读

远端安装通过 bash 脚本执行，每步带时间戳：

```
[remote][14:24:05] ========== VS Code Server 安装开始 ==========
[remote][14:24:05] 步骤1/5: 环境检查
[remote][14:24:05]   ✓ 磁盘空间充足
[remote][14:24:05]   ✓ 必要命令齐全
[remote][14:24:06]   ✓ 压缩包文件存在
[remote][14:24:06]   ✓ 压缩包完整性校验通过
[remote][14:24:06] 步骤2/5: 创建安装目录
[remote][14:24:06] 步骤3/5: 解压 VS Code Server（预计 5-30 秒）...
[remote][14:24:12]   ✓ 解压完成（耗时 6 秒，文件数: 482，解压后大小: 212M）
[remote][14:24:12] 步骤4/5: 设置执行权限
[remote][14:24:12]   ✓ node 可执行权限已设置
[remote][14:24:12]   ✓ code-server 可执行权限已设置
[remote][14:24:12] 步骤5/5: 清理临时文件
[remote][14:24:13] ========== VS Code Server 安装成功 ==========
```

---

## 五、方案C：手动部署

如果不想使用脚本，可以按以下步骤手动操作。适合需要完全掌控每一步或排障时使用。

### 步骤1：获取本地 VS Code Commit ID

**方法一：VS Code 界面**

1. 打开 VS Code → 帮助(H) → 关于(A)
2. 找到"提交"字段，复制后面的 40 位十六进制字符串

**方法二：命令行**

```powershell
code --version
```

输出第二行即为 Commit ID。

**方法三：直接读文件**

```powershell
# 用户安装版
Get-Content "$env:LOCALAPPDATA\Programs\Microsoft VS Code\product.json" | ConvertFrom-Json | Select-Object -ExpandProperty commit
```

### 步骤2：获取远端架构

SSH 到远端执行：

```bash
uname -m
```

输出对应关系：

| uname -m 输出 | VS Code 架构参数 |
|--------------|----------------|
| `x86_64` | `x64` |
| `aarch64` | `arm64` |
| `armv7l` / `armv6l` | `armhf` |
| `armv8l` | `arm64` |

### 步骤3：下载 Server 包

在本地浏览器或使用下载工具访问：

```
https://update.code.visualstudio.com/commit:<COMMIT_ID>/server-linux-<ARCH>/stable
```

替换 `<COMMIT_ID>` 为步骤1获取的ID，`<ARCH>` 为 `x64`/`arm64`/`armhf`。

例如：`https://update.code.visualstudio.com/commit:e7e037c17b42bae6e52dca395f4a4b0bb9ea0934/server-linux-x64/stable`

下载得到一个 `.tar.gz` 文件，约 50-80 MB。

### 步骤4：上传到远端

```powershell
scp -P 22 <本地下载的文件路径> <user>@<host>:/tmp/vscode-server.tar.gz
```

### 步骤5：远端解压安装

SSH 登录到远端，执行：

```bash
# 设置变量（替换为你的 COMMIT_ID）
COMMIT=<你的commit-id>

# 创建安装目录
mkdir -p ~/.vscode-server/bin/$COMMIT

# 解压
cd ~/.vscode-server/bin/$COMMIT
tar -xzf /tmp/vscode-server.tar.gz --strip-components=1

# 设置执行权限
chmod +x node bin/code-server bin/*

# 清理临时文件
rm -f /tmp/vscode-server.tar.gz

# 验证
ls -la ~/.vscode-server/bin/$COMMIT/bin/code-server
```

如果输出了 code-server 文件信息且有可执行权限（`x`），则安装成功。

### 步骤6：VS Code 连接

回到 VS Code，重新连接 Remote-SSH，将直接启动 server 而不再下载。

---

## 六、方案D：配置代理

如果远端服务器有可用的 HTTP/HTTPS 代理，可以让 VS Code Remote-SSH 通过代理下载 server 包。

### 方法1：SSH 配置文件中设置环境变量

编辑本地 `~/.ssh/config`（Windows: `C:\Users\<用户名>\.ssh\config`）：

```
Host my-server
    HostName 10.16.11.3
    User root
    Port 22
    SetEnv HTTP_PROXY=http://proxy.example.com:7890
    SetEnv HTTPS_PROXY=http://proxy.example.com:7890
```

> **注意**：`SetEnv` 需要远端 sshd 配置 `AcceptEnv` 允许，且 OpenSSH 7.8+ 才支持。

### 方法2：远端环境变量

在远端 `~/.bashrc` 或 `~/.profile` 中添加：

```bash
export http_proxy=http://proxy.example.com:7890
export https_proxy=http://proxy.example.com:7890
export no_proxy=localhost,127.0.0.1,10.*,192.168.*
```

然后重新连接 VS Code Remote-SSH。

---

## 七、排障指南

### 问题1：SCP 传输卡住不动

**症状**：脚本显示"开始传输..."后长时间无进度更新。

**排查步骤**：

1. 先手动测试 SSH 连接是否正常：
   ```powershell
   ssh -p 22 <user>@<host>
   ```
   如果需要输入密码，说明密钥认证未配置。建议配置 SSH 密钥免密登录：
   ```powershell
   # 生成密钥（如果没有，一路回车即可）
   ssh-keygen -t ed25519
   
   # 上传公钥到远端（Windows 10 21H2+ / Windows 11 自带 ssh-copy-id）
   ssh-copy-id -p 22 <user>@<host>
   
   # 如果没有 ssh-copy-id 命令，手动执行：
   type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -p 22 <user>@<host> "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
   ```

2. 如果 SSH 连接正常但 SCP 仍卡住，检查是否有防火墙限制 SCP 带宽或连接。

3. 使用脚本时注意观察日志：6秒提示"正在建立连接/认证"是正常的；超过20秒会给出警告；超过40秒自动终止并输出排障提示。

4. 如果网络极差，使用 `-KeepArchive` 保留本地下载文件，手动用 WinSCP 等支持断点续传的工具上传。

### 问题2：远端安装失败——磁盘空间不足

**症状**：远端日志显示 `[remote][ERROR] 磁盘空间不足！`。

**解决**：

```bash
# 查看磁盘使用情况
df -h ~

# 查看旧版本 VS Code Server 占用空间
du -sh ~/.vscode-server/

# 清理旧版本（保留当前使用的版本）
ls ~/.vscode-server/bin/
# 删除不需要的旧版本目录
rm -rf ~/.vscode-server/bin/<旧commit-id>
```

VS Code Server 每个版本约 200-300MB，长期积累可能占用数 GB 空间。可定期清理。

### 问题3：压缩包损坏

**症状**：远端日志显示 `压缩包损坏或不完整！gzip 校验失败`。

**原因**：SCP 传输过程中网络中断，文件不完整。

**解决**：使用 `-Force` 参数重新运行脚本，会重新下载和上传：

```powershell
.\.agents\scripts\deploy-vscode-server.ps1 -Server <host> -User <user> -Force
```

### 问题4：版本不匹配

**症状**：脚本提示"远端已安装"但 VS Code 仍尝试下载。

**原因**：本地 VS Code 已更新，Commit ID 变了，远端旧版本不再匹配。

**解决**：VS Code 更新后重新运行脚本即可（脚本自动检测新的 Commit ID）。

### 问题5：ARM 架构服务器

**症状**：自动检测架构失败，或下载的包无法在远端运行。

**解决**：先 SSH 到远端确认架构：
```bash
uname -m
```
然后用 `-Arch` 参数手动指定：
```powershell
# 树莓派等 ARMv7 设备
.\.agents\scripts\deploy-vscode-server.ps1 -Server <host> -User <user> -Arch armhf

# ARMv8/Apple Silicon 等 64 位 ARM 设备
.\.agents\scripts\deploy-vscode-server.ps1 -Server <host> -User <user> -Arch arm64
```

### 问题6：Commit ID 自动检测失败

**症状**：脚本提示"无法自动检测 VS Code Commit ID"。

**解决**：通过 VS Code 菜单手动获取：帮助 → 关于 → 提交，然后使用 `-CommitId` 参数：

```powershell
.\.agents\scripts\deploy-vscode-server.ps1 -Server <host> -User <user> -CommitId <40位commit-id>
```

---

## 八、常见问题（FAQ）

**Q：脚本支持 macOS/Linux 本地运行吗？**
A：当前脚本为 PowerShell 脚本，主要面向 Windows 用户。macOS/Linux 用户可参考"方案C：手动部署"步骤操作，或将脚本逻辑翻译为 bash 脚本。

**Q：VS Code 更新后需要重新运行吗？**
A：是的。VS Code 每次更新都会有新的 Commit ID，需要重新下载对应版本的 server 包。脚本会自动检测，直接重新运行即可（会跳过已安装的检查）。

**Q：可以一次部署到多台服务器吗？**
A：可以。使用 `-KeepArchive` 参数保留本地下载文件，然后依次对每台服务器运行脚本（第二次起会使用缓存，跳过下载步骤）：

```powershell
# 第一次：下载并部署到服务器A
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.3 -User root -KeepArchive
# 第二次：直接部署到服务器B（跳过下载）
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.4 -User root -KeepArchive
# 第三次：部署到服务器C
.\.agents\scripts\deploy-vscode-server.ps1 -Server 10.16.11.5 -User root
# 最后一次不加 -KeepArchive，自动清理临时文件
```

**Q：支持 VSCodium 等 VS Code 衍生版本吗？**
A：脚本支持从 VSCodium 的安装路径自动检测 Commit ID，但 VSCodium 的 server 包下载地址不同（使用 `github.com/VSCodium/vscodium` 的 release 地址，而非 Microsoft CDN）。对于 VSCodium 用户，建议手动下载对应 release 包后参考"方案C：手动部署"操作，或直接在 VSCodium 设置中使用 `remote.SSH.localServerDownload: always`。

**Q：WSL（Windows Subsystem for Linux）环境下如何使用？**
A：WSL 有两种场景：
- **在 WSL 中使用 VS Code Remote-WSL 连接**：这是本地连接，不需要本脚本，VS Code 会自动处理。
- **在 Windows 上通过 VS Code Remote-SSH 连接远端 Linux**：直接在 Windows PowerShell 中运行本脚本即可。
- **在 WSL 中运行 VS Code 并通过 SSH 连接远端**：需要在 WSL 内也有 ssh/scp 命令，将脚本复制到 WSL 文件系统中（需改为 bash 脚本），或直接用"方案C：手动部署"。

**Q：为什么不使用 rsync 代替 SCP？**
A：SCP 在 Windows 上开箱即用（OpenSSH 自带），无需额外安装。rsync 在 Windows 上需要额外安装（如通过 Cygwin/MSYS2）。如果网络极差需要断点续传，可以先用 `-KeepArchive` 下载到本地，再用支持断点续传的工具手动上传。

**Q：连接 VS Code Insiders 版本怎么办？**
A：脚本已自动检测 VS Code Insiders 的安装路径并使用 Microsoft CDN 下载（Insiders 版本使用相同的 CDN）。如果检测失败，使用 `-CommitId` 手动指定即可。注意：VSCodium 虽然能自动检测 Commit ID，但其 server 包下载地址不同，详见上方 VSCodium 相关 FAQ。

**Q：远端 server 安装位置在哪里？**
A：默认安装在 `~/.vscode-server/bin/<commit-id>/`。脚本和手动操作都遵循 VS Code 的标准目录结构，不会与 VS Code 的自动管理逻辑冲突。
