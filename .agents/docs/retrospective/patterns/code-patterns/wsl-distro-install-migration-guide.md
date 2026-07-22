---
title: WSL 发行版安装、迁移与配置速查手册
version: 1.0
date: 2026-07-22
tags: [WSL, Windows, 环境配置, Ubuntu, 迁移, 离线安装]
source: "WSL Ubuntu 26.04 安装与迁移实践"
---

# WSL 发行版安装、迁移与配置速查手册

> 适用于 Windows 10/11 + WSL2 环境。包含三个核心操作模式：**离线手动安装**、**安全迁移**、**默认用户配置修复**。

---

## 前置检查清单

在执行任何WSL操作前，先确认环境状态：

```powershell
# 检查WSL版本和运行状态
wsl --status
wsl --version

# 列出已安装发行版
wsl -l -v

# 列出在线可用发行版（确认网络时使用）
wsl --list --online
```

| 检查项 | 预期结果 | 异常处理 |
|--------|---------|---------|
| WSL版本 | ≥ 2.0 | `wsl --update` 更新 |
| 默认版本 | WSL2 | `wsl --set-default-version 2` |
| 虚拟化已启用 | 无报错 | BIOS中启用虚拟化，启用"虚拟机平台"Windows功能 |

---

## 模式一：WSL发行版离线手动安装

### 触发场景

- `wsl --install -d <Distro>` 网络超时（`WININET_E_TIMEOUT`）
- GitHub raw域名无法访问
- 需要自定义安装位置到非系统盘（避免占满C盘）
- 需要批量/自动化安装

### 核心步骤

#### Step 1：下载发行版镜像

**Ubuntu 镜像源**（按优先级尝试）：

| 发行版 | 主源 | 备用源 |
|--------|------|--------|
| Ubuntu 26.04 | `https://apt.releases.ubuntu.com/26.04/ubuntu-26.04-wsl-amd64.wsl` | `https://cdimage.ubuntu.com/releases/resolute/release/` |
| Ubuntu 24.04 | `https://apt.releases.ubuntu.com/24.04/ubuntu-24.04-wsl-amd64.wsl` | `https://cdimage.ubuntu.com/releases/noble/release/` |
| Ubuntu 22.04 | `https://apt.releases.ubuntu.com/22.04/ubuntu-22.04-wsl-amd64.wsl` | `https://cdimage.ubuntu.com/releases/jammy/release/` |

**PowerShell 7 下载命令**（自动跳过证书验证问题）：

```powershell
$version = "26.04"
$url = "https://apt.releases.ubuntu.com/$version/ubuntu-$version-wsl-amd64.wsl"
$downloadDir = "D:\Downloads"
$file = "$downloadDir\ubuntu-$version-wsl-amd64.wsl"

# 确保目录存在
if (-not (Test-Path $downloadDir)) { New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null }

# 下载（跳过证书验证）
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $file -SkipCertificateCheck

# 验证下载
$sizeMB = [math]::Round((Get-Item $file).Length / 1MB, 2)
Write-Host "下载完成: $sizeMB MB"
if ($sizeMB -lt 100) {
    Write-Warning "文件过小（<100MB），可能是错误页面，请检查！"
    # 检查文件头确认格式
    $bytes = [System.IO.File]::ReadAllBytes($file)
    $header = [System.BitConverter]::ToString($bytes[0..1])
    Write-Host "文件头: $header (1F-8B = gzip tar, 正确)"
}
```

> ⚠️ **文件格式确认**：WSL官方镜像本质是gzip压缩的tar包（文件头`1F-8B`），不是ZIP/APPX格式，无需解压，直接导入即可。

#### Step 2：导入到目标位置

```powershell
$distroName = "Ubuntu-26.04"
$installDir = "D:\WSL\$distroName"  # 推荐安装到非系统盘
$wslFile = "D:\Downloads\ubuntu-26.04-wsl-amd64.wsl"

# 创建目标目录
if (-not (Test-Path $installDir)) { New-Item -ItemType Directory -Path $installDir -Force | Out-Null }

# 导入（WSL2）
wsl --import $distroName $installDir $wslFile --version 2

# 验证
wsl -l -v
```

#### Step 3：创建用户并配置默认登录

导入后默认以root用户登录，需要创建普通用户：

```powershell
$distroName = "Ubuntu-26.04"
$username = "xin"  # 修改为你的用户名

# 创建用户、添加sudo权限、配置免密sudo
wsl -d $distroName -u root -- bash -c @"
useradd -m -s /bin/bash $username
usermod -aG sudo $username
echo '$username ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/$username
chmod 0440 /etc/sudoers.d/$username

# 配置wsl.conf（默认用户 + systemd）
cat > /etc/wsl.conf << 'WSLCONF'
[user]
default = $username

[boot]
systemd = true

[network]
generateResolvConf = true
WSLCONF
echo '用户配置完成'
"@

# 重启发行版使配置生效
wsl --terminate $distroName
Start-Sleep -Seconds 2

# 验证默认用户
wsl -d $distroName -- whoami  # 应显示 $username 而非 root
wsl -d $distroName -- lsb_release -a  # 验证系统版本
```

#### 一键安装脚本模板

```powershell
# 用法：.\install-wsl-ubuntu.ps1 -Version 26.04 -Username xin -InstallDir D:\WSL
param(
    [string]$Version = "26.04",
    [string]$Username = "xin",
    [string]$InstallDir = "D:\WSL"
)

$ErrorActionPreference = "Stop"
$distroName = "Ubuntu-$Version"
$targetDir = "$InstallDir\$distroName"
$wslFile = "$env:TEMP\ubuntu-$Version-wsl-amd64.wsl"

# 下载
Write-Host "[1/4] 下载 Ubuntu $Version WSL镜像..."
$url = "https://apt.releases.ubuntu.com/$Version/ubuntu-$Version-wsl-amd64.wsl"
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri $url -OutFile $wslFile -SkipCertificateCheck

# 导入
Write-Host "[2/4] 导入到 $targetDir..."
if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir -Force | Out-Null }
wsl --import $distroName $targetDir $wslFile --version 2

# 配置用户
Write-Host "[3/4] 配置用户 $Username..."
wsl -d $distroName -u root -- bash -c "useradd -m -s /bin/bash $Username; usermod -aG sudo $Username; echo '$Username ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/$Username; chmod 0440 /etc/sudoers.d/$Username; printf '[user]\ndefault = %s\n\n[boot]\nsystemd = true\n' '$Username' > /etc/wsl.conf"

# 重启验证
Write-Host "[4/4] 重启并验证..."
wsl --terminate $distroName
Start-Sleep -Seconds 2
$currentUser = wsl -d $distroName -- whoami
Write-Host "安装完成！当前用户: $currentUser"

# 清理下载文件
Remove-Item $wslFile -Force
```

### ❌ 反模式

| 错误做法 | 后果 | 正确做法 |
|---------|------|---------|
| `curl.exe -k` 下载不检查文件大小 | 可能下载到HTML错误页面（281字节的404页面） | 下载后检查文件大小 > 100MB，检查文件头 |
| 导入后不验证默认用户 | 每次启动都是root，权限混乱 | 导入后立即执行 `whoami` 验证 |
| 安装到 `C:\Users\<name>\AppData\Local\...` | 占满C盘系统空间 | 安装到D:\WSL\等非系统盘 |
| 使用 `ubuntu config --default-user` | 仅适用于Microsoft Store版，import版无此命令 | 通过 `/etc/wsl.conf` 配置 |
| 导入后不terminate直接测试用户 | wsl.conf配置不生效 | 必须 `wsl --terminate` 重启发行版 |

---

## 模式二：WSL发行版安全迁移（零数据丢失）

### 触发场景

- 需要将WSL从C盘/临时目录迁移到其他位置（如D:\WSL）
- 需要备份WSL发行版（导出为tar归档）
- 需要复制WSL环境到另一台机器
- C盘空间不足需要迁移到非系统盘

### 核心步骤

#### Step 1：停止发行版

```powershell
$distroName = "Ubuntu-26.04"

# 确保发行版完全停止
wsl --terminate $distroName
Start-Sleep -Seconds 3

# 确认状态为 Stopped
wsl -l -v
```

#### Step 2：导出完整文件系统

```powershell
$distroName = "Ubuntu-26.04"
$backupDir = "D:\WSL-Backup"
$backupFile = "$backupDir\$distroName-backup-$(Get-Date -Format 'yyyyMMdd').tar"

# 创建备份目录
if (-not (Test-Path $backupDir)) { New-Item -ItemType Directory -Path $backupDir -Force | Out-Null }

# 导出（可能需要几分钟，取决于使用空间大小）
Write-Host "正在导出 $distroName ..."
$ProgressPreference = 'SilentlyContinue'
wsl --export $distroName $backupFile

# 验证导出文件
$sizeGB = [math]::Round((Get-Item $backupFile).Length / 1GB, 2)
Write-Host "导出完成: $sizeGB GB -> $backupFile"

# ⚠️ 关键：确认导出文件存在且大小合理后，再进行下一步！
if (-not (Test-Path $backupFile) -or (Get-Item $backupFile).Length -lt 100MB) {
    Write-Error "导出失败，请检查后重试"
    exit 1
}
```

> 📦 **导出文件大小参考**：约等于WSL内实际使用空间的1~1.3倍（未压缩tar）。已使用1.3GB的系统导出约1.2~1.6GB是正常的。

#### Step 3：注销原发行版

```powershell
$distroName = "Ubuntu-26.04"

# ⚠️ 警告：这将删除原位置的所有数据！确保已成功导出tar后再执行！
wsl --unregister $distroName

# 确认已注销
wsl -l -v
```

#### Step 4：在新位置导入

```powershell
$distroName = "Ubuntu-26.04"
$newDir = "D:\WSL\$distroName"
$backupFile = "D:\WSL-Backup\$distroName-backup-20260722.tar"

# 创建新目录
if (-not (Test-Path $newDir)) { New-Item -ItemType Directory -Path $newDir -Force | Out-Null }

# 导入到新位置
Write-Host "正在导入到 $newDir ..."
wsl --import $distroName $newDir $backupFile --version 2
```

#### Step 5：验证迁移结果

```powershell
$distroName = "Ubuntu-26.04"

# 检查发行版状态
wsl -l -v

# 验证默认用户（配置已保留在tar中，无需重新设置）
$user = wsl -d $distroName -- whoami
Write-Host "默认用户: $user"

# 验证系统版本
wsl -d $distroName -- lsb_release -a

# 验证文件完整性（检查关键目录/文件是否存在）
wsl -d $distroName -- bash -c "ls -la /home/ && echo '---' && ls /etc/wsl.conf && echo 'wsl.conf存在'"
```

#### Step 6：清理备份文件（确认无误后）

```powershell
# 确认迁移成功后，可删除备份tar释放空间
Remove-Item "D:\WSL-Backup\Ubuntu-26.04-backup-20260722.tar" -Force
```

#### 一键迁移脚本模板

```powershell
# 用法：.\move-wsl-distro.ps1 -DistroName Ubuntu-26.04 -TargetDir D:\WSL\Ubuntu-26.04
param(
    [Parameter(Mandatory=$true)][string]$DistroName,
    [Parameter(Mandatory=$true)][string]$TargetDir,
    [string]$BackupDir = "D:\WSL-Backup"
)

$ErrorActionPreference = "Stop"
$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$backupFile = "$BackupDir\$DistroName-move-$timestamp.tar"

Write-Host "=== WSL发行版迁移工具 ==="
Write-Host "发行版: $DistroName"
Write-Host "目标位置: $TargetDir"
Write-Host "备份文件: $backupFile"
Write-Host ""

# Step 1: 停止
Write-Host "[1/5] 停止发行版..."
wsl --terminate $DistroName
Start-Sleep -Seconds 3

# Step 2: 导出
Write-Host "[2/5] 导出（可能需要几分钟）..."
if (-not (Test-Path $BackupDir)) { New-Item -ItemType Directory -Path $BackupDir -Force | Out-Null }
$ProgressPreference = 'SilentlyContinue'
wsl --export $DistroName $backupFile
$sizeGB = [math]::Round((Get-Item $backupFile).Length / 1GB, 2)
Write-Host "导出完成: $sizeGB GB"

# Step 3: 验证导出
if ((Get-Item $backupFile).Length -lt 100MB) {
    Write-Error "导出文件过小（<100MB），迁移中止"
    exit 1
}

# Step 4: 注销+导入
Write-Host "[3/5] 注销原发行版..."
wsl --unregister $DistroName

Write-Host "[4/5] 导入到新位置..."
if (-not (Test-Path $TargetDir)) { New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null }
wsl --import $DistroName $TargetDir $backupFile --version 2

# Step 5: 验证
Write-Host "[5/5] 验证..."
Start-Sleep -Seconds 2
$user = wsl -d $DistroName -- whoami
$ver = wsl -d $DistroName -- lsb_release -rs
Write-Host ""
Write-Host "✅ 迁移完成！"
Write-Host "   用户: $user"
Write-Host "   版本: Ubuntu $ver"
Write-Host "   位置: $TargetDir"
Write-Host ""
Write-Host "确认无误后可删除备份文件: $backupFile"
```

### ❌ 反模式

| 错误做法 | 后果 | 正确做法 |
|---------|------|---------|
| 直接移动ext4.vhdx文件 | WSL注册表路径不更新，发行版无法启动（HCS_E_CONNECTION_TIMEOUT） | 使用export→unregister→import流程 |
| 未export就unregister | 数据永久丢失，无法恢复 | 必须先export并验证文件存在再unregister |
| 迁移后不验证直接使用 | 默认用户可能变为root，配置丢失 | 迁移后立即验证whoami和关键文件 |
| 导出后立即删除原目录 | import失败时无法回滚 | 先验证import成功，再删除备份 |
| 在U盘/移动硬盘上运行WSL | I/O速度慢，可能启动超时（HCS_E_CONNECTION_TIMEOUT） | 迁移到本地固定磁盘，避免移动存储 |

---

## 模式三：WSL默认用户配置修复

### 触发场景

- `wsl --import` 导入后默认以root登录
- 从备份恢复后需要切换回普通用户
- 需要创建新的默认用户
- 默认用户配置丢失/错乱

### 核心步骤

#### Step 1：确认当前状态

```powershell
$distroName = "Ubuntu-26.04"

# 检查当前默认用户
wsl -d $distroName -- whoami  # 如果显示 root，需要修复
```

#### Step 2：以root身份配置用户

```powershell
$distroName = "Ubuntu-26.04"
$username = "xin"

# 如果用户已存在，直接配置；如果不存在，先创建
wsl -d $distroName -u root -- bash -c @"
# 检查用户是否存在
if id -u $username >/dev/null 2>&1; then
    echo '用户 $username 已存在'
else
    echo '创建用户 $username ...'
    useradd -m -s /bin/bash $username
fi

# 添加sudo权限
usermod -aG sudo $username

# 配置免密sudo（可选，方便开发使用）
echo '$username ALL=(ALL) NOPASSWD:ALL' > /etc/sudoers.d/$username
chmod 0440 /etc/sudoers.d/$username

# 配置wsl.conf（这是import版唯一有效的默认用户设置方式！）
cat > /etc/wsl.conf << 'WSLCONF'
[user]
default = $username

[boot]
systemd = true

[network]
generateResolvConf = true
WSLCONF

echo '配置完成'
cat /etc/wsl.conf
"@
```

#### Step 3：重启发行版使配置生效

```powershell
$distroName = "Ubuntu-26.04"

# ⚠️ 必须在PowerShell中terminate，在WSL内部重启无效！
wsl --terminate $distroName
Start-Sleep -Seconds 2
```

#### Step 4：验证

```powershell
$distroName = "Ubuntu-26.04"

# 验证默认用户
$currentUser = wsl -d $distroName -- whoami
Write-Host "默认用户: $currentUser"

if ($currentUser -eq "root") {
    Write-Warning "仍然是root用户，请检查wsl.conf配置"
    wsl -d $distroName -- cat /etc/wsl.conf
} else {
    Write-Host "✅ 默认用户配置成功！"
}
```

### ❌ 反模式

| 错误做法 | 后果 | 正确做法 |
|---------|------|---------|
| 配置wsl.conf后不terminate | 配置不生效，仍以root登录 | 必须在PowerShell执行 `wsl --terminate` |
| 忘记将用户加入sudo组 | 无法执行apt、docker等管理员操作 | `usermod -aG sudo <username>` |
| 使用 `ubuntu config --default-user` | Store版专属命令，import版不存在此命令 | 使用 `/etc/wsl.conf` 的 `[user] default=` |
| 直接修改 `/etc/passwd` | 不持久，可能引发其他问题 | 通过wsl.conf配置 |
| sudoers文件权限不是0440 | sudo拒绝读取该文件，导致无法sudo | `chmod 0440 /etc/sudoers.d/<username>` |

---

## 常见问题排查（Troubleshooting）

### Q1: `wsl --install` 报 WININET_E_TIMEOUT

**原因**：无法访问 raw.githubusercontent.com 获取发行版列表。

**解决**：使用模式一的**离线手动安装**方式，直接下载.wsl文件导入。

### Q2: 下载时证书错误（RemoteCertificateNameMismatch）

**原因**：apt.releases.ubuntu.com 的TLS证书SNI配置问题。

**解决**：
```powershell
# 使用PowerShell 7的 -SkipCertificateCheck 参数
Invoke-WebRequest -Uri $url -OutFile $file -SkipCertificateCheck

# 下载后务必检查文件大小！
```

### Q3: 导入后启动报 HCS_E_CONNECTION_TIMEOUT

**可能原因**：
1. 发行版在U盘/移动硬盘上 → 迁移到本地固定磁盘
2. `.wslconfig` 启用了不兼容的网络特性 → 检查 `C:\Users\<name>\.wslconfig`，暂时注释掉 `mirrored`/`dnsTunneling` 等新特性
3. ext4.vhdx损坏 → 从备份重新导入

### Q4: `wsl: Failed to start the systemd user session` 警告

**原因**：systemd用户会话启动失败（通常是因为刚创建用户，用户服务未完全初始化）。

**影响**：不影响正常使用，可以忽略。

**排查**（可选）：
```bash
journalctl --user -b  # 查看用户会话日志
```

### Q5: 如何设置默认发行版？

```powershell
# 设置默认启动发行版
wsl --set-default Ubuntu-26.04

# 查看当前默认（带*号的）
wsl -l -v
```

### Q6: 如何删除WSL发行版？

```powershell
# 警告：这会删除该发行版的所有数据！
wsl --unregister <DistroName>

# 确认已删除
wsl -l -v
```

### Q7: 如何压缩WSL虚拟磁盘（释放空间）？

当WSL内删除大量文件后，Windows上的ext4.vhdx不会自动缩小。参考项目脚本：
[compress-wsl-vhdx.ps1](file:///d:/spaces/SpecWeave/.agents/scripts/compress-wsl-vhdx.ps1)

---

## 快速参考：常用命令速查表

```powershell
# === 发行版管理 ===
wsl -l -v                          # 列出所有发行版
wsl --list --online                # 列出在线可用发行版
wsl --install -d <Distro>          # 在线安装
wsl --import <Name> <Dir> <File>   # 离线导入
wsl --unregister <Name>            # 删除发行版（⚠️数据丢失）
wsl --export <Name> <File.tar>     # 导出备份
wsl --terminate <Name>             # 停止发行版
wsl --set-default <Name>           # 设置默认发行版
wsl --set-version <Name> 2         # 转换为WSL2
wsl -d <Name>                      # 启动指定发行版
wsl -d <Name> -u root              # 以root用户启动
wsl -d <Name> -- <Command>         # 在发行版内执行命令

# === 系统信息（在WSL内） ===
lsb_release -a                     # 查看Ubuntu版本
uname -a                           # 查看内核版本
whoami                             # 查看当前用户
df -h                              # 查看磁盘使用
cat /etc/wsl.conf                  # 查看WSL配置
```

---

## 参考资料

- [WSL官方文档 - 基本命令](https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands)
- [WSL官方文档 - 导入导出](https://learn.microsoft.com/zh-cn/windows/wsl/basic-commands#import-and-export-a-distribution)
- [Ubuntu WSL镜像下载](https://apt.releases.ubuntu.com/)
- 实践来源：[WSL Ubuntu 26.04安装与迁移复盘报告](../reports/environment-setup/retrospective-wsl-ubuntu2604-install-migration-20260722/README.md)

<!-- changelog -->
- 2026-07-22 | feat | 初始版本，包含3个核心模式：离线安装、安全迁移、默认用户配置修复，基于Ubuntu 26.04安装实践萃取
