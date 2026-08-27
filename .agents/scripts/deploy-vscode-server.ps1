<#
.SYNOPSIS
    自动下载 VS Code Server 并通过 SCP 部署到远端 Linux 服务器
.DESCRIPTION
    解决 VS Code Remote-SSH "Downloading and installing remote server" 下载慢/卡住的问题。
    自动检测本地 VS Code commit ID，下载对应 server 包，SCP 上传到远端并解压安装。
    前提：本地已配置 SSH 密钥免密登录远端，或远端接受手动输入密码。
.PARAMETER Server
    远端服务器地址（IP 或域名），也可用别名 -Host
.PARAMETER User
    SSH 用户名
.PARAMETER Port
    SSH 端口，默认 22
.PARAMETER Arch
    远端架构（x64/arm64/armhf），默认自动通过 uname -m 检测
.PARAMETER CommitId
    指定 VS Code commit ID，默认自动从本地 VS Code 安装目录读取
.PARAMETER KeepArchive
    保留本地下载的压缩包，不自动清理
.PARAMETER Force
    强制重新安装，即使远端已存在相同 commit 的 server
.EXAMPLE
    .\deploy-vscode-server.ps1 -Server 10.16.11.3 -User root
.EXAMPLE
    .\deploy-vscode-server.ps1 -Server 10.16.11.3 -User myuser -Port 2222
.EXAMPLE
    .\deploy-vscode-server.ps1 -Host server.example.com -User dev -Arch arm64 -CommitId abc123def456
.NOTES
    Author: SpecWeave Agent
    Version: 1.0.1
    Requires: PowerShell 5+，本地已安装 ssh/scp（Windows 10 1809+ 自带）
    Changelog: v1.0.1 - 修复 -Host 参数名与 PowerShell 内置 $Host 只读变量冲突的问题，重命名为 -Server（保留 -Host 别名兼容）
#>

param(
    [Parameter(Mandatory = $true, HelpMessage = "远端服务器地址")]
    [Alias("Host")]
    [string]$Server,

    [Parameter(Mandatory = $true, HelpMessage = "SSH 用户名")]
    [string]$User,

    [int]$Port = 22,

    [ValidateSet("x64", "arm64", "armhf", "")]
    [string]$Arch = "",

    [string]$CommitId = "",

    [switch]$KeepArchive,

    [switch]$Force
)

$ErrorActionPreference = "Stop"
$ProgressPreference = 'SilentlyContinue'

# ============================================================
# 辅助函数
# ============================================================

function Write-Step {
    param([string]$Message)
    Write-Host "[STEP] $Message" -ForegroundColor Cyan
}

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warn {
    param([string]$Message)
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

function Write-Fail {
    param([string]$Message)
    Write-Host "[FAIL] $Message" -ForegroundColor Red
}

function Test-Command {
    param([string]$Name)
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    return ($null -ne $cmd)
}

# ============================================================
# 0. 前置检查
# ============================================================

Write-Step "前置环境检查"

if (-not (Test-Command "ssh")) {
    Write-Fail "未找到 ssh 命令。请确保 Windows 10 1809+ 已启用 OpenSSH 客户端，或安装 Git Bash/WSL。"
    exit 1
}

if (-not (Test-Command "scp")) {
    Write-Fail "未找到 scp 命令。请确保 Windows 10 1809+ 已启用 OpenSSH 客户端。"
    exit 1
}

$sshTarget = "${User}@${Server}"
$sshCommonArgs = @(
    "-p", "$Port",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=10"
)

# 测试 SSH 连通性
Write-Info "测试 SSH 连接: $sshTarget"
$testResult = (& ssh @sshCommonArgs $sshTarget "echo SSH_OK" 2>&1) | Out-String
if ($LASTEXITCODE -ne 0 -or $testResult -notmatch "SSH_OK") {
    Write-Fail "SSH 连接失败。请检查：1)服务器地址和用户名正确  2)SSH密钥已配置或密码正确  3)网络可达"
    Write-Host "  详细错误: $testResult" -ForegroundColor Gray
    exit 1
}
Write-Info "SSH 连接正常"

# ============================================================
# 1. 自动检测 VS Code Commit ID
# ============================================================

Write-Step "检测 VS Code Commit ID"

if (-not $CommitId) {
    # 按优先级尝试所有常见安装路径
    $possiblePaths = @(
        # 用户安装（User setup）—— 最常见
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code\product.json",
        # 系统安装（Machine-wide）
        "${env:ProgramFiles}\Microsoft VS Code\product.json",
        "${env:ProgramFiles(x86)}\Microsoft VS Code\product.json",
        # Insiders
        "$env:LOCALAPPDATA\Programs\Microsoft VS Code Insiders\product.json",
        "${env:ProgramFiles}\Microsoft VS Code Insiders\product.json",
        # Scoop
        "$env:USERPROFILE\scoop\apps\vscode\current\product.json",
        # VSCodium
        "$env:LOCALAPPDATA\Programs\VSCodium\product.json",
        "${env:ProgramFiles}\VSCodium\product.json"
    )

    foreach ($path in $possiblePaths) {
        if ($path -and (Test-Path $path)) {
            try {
                $product = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($product.commit) {
                    $CommitId = $product.commit
                    Write-Info "从 $(Split-Path (Split-Path $path) -Leaf) 检测到 Commit ID: $CommitId"
                    Write-Host "  路径: $path" -ForegroundColor Gray
                    break
                }
            } catch {
                # 跳过无法解析的文件
            }
        }
    }

    # 额外尝试：通过 code 命令读取版本
    if (-not $CommitId -and (Test-Command "code")) {
        try {
            $versionOutput = & code --version 2>$null
            if ($versionOutput -and $versionOutput.Count -ge 2) {
                $CommitId = $versionOutput[1].Trim()
                Write-Info "通过 'code --version' 检测到 Commit ID: $CommitId"
            }
        } catch {
            # 忽略失败
        }
    }

    if (-not $CommitId) {
        Write-Fail "无法自动检测 VS Code Commit ID。"
        Write-Host ""
        Write-Host "  解决方法：" -ForegroundColor Yellow
        Write-Host "  1. 打开 VS Code → 帮助(H) → 关于(A)，找到 '提交' 或 'Commit' 后的40位十六进制字符串" -ForegroundColor White
        Write-Host "  2. 使用 -CommitId 参数手动指定，例如：" -ForegroundColor White
        Write-Host "     .\deploy-vscode-server.ps1 -Server $Server -User $User -CommitId <你的commit-id>" -ForegroundColor White
        exit 1
    }
} else {
    Write-Info "使用指定的 Commit ID: $CommitId"
}

# 验证 Commit ID 格式（应为40位十六进制）
if ($CommitId -notmatch '^[0-9a-f]{40}$') {
    Write-Warn "Commit ID 格式可能不正确（期望40位十六进制），继续执行..."
}

# ============================================================
# 2. 检测远端服务器架构
# ============================================================

Write-Step "检测远端服务器架构"

if (-not $Arch) {
    Write-Info "通过 SSH 检测远端架构..."
    $remoteArch = (& ssh @sshCommonArgs $sshTarget "uname -m" 2>&1) | Out-String
    $remoteArch = $remoteArch.Trim()

    switch -Wildcard ($remoteArch) {
        "x86_64"  { $Arch = "x64" }
        "aarch64" { $Arch = "arm64" }
        "armv7l"  { $Arch = "armhf" }
        "armv8l"  { $Arch = "arm64" }
        "armv6l"  { $Arch = "armhf" }
        default {
            Write-Fail "未知的远端架构: '$remoteArch'"
            Write-Host "  请手动指定 -Arch 参数（x64/arm64/armhf）" -ForegroundColor Yellow
            exit 1
        }
    }
    Write-Info "远端架构: $Arch (uname -m = $remoteArch)"
} else {
    Write-Info "使用指定的架构: $Arch"
}

# 架构到下载文件名映射
$archToFile = @{
    "x64"   = "server-linux-x64"
    "arm64" = "server-linux-arm64"
    "armhf" = "server-linux-armhf"
}
$serverFileName = $archToFile[$Arch]
$downloadUrl = "https://update.code.visualstudio.com/commit:${CommitId}/${serverFileName}/stable"
$archiveFileName = "vscode-server-linux-${Arch}-${CommitId}.tar.gz"
$tempDir = Join-Path $env:TEMP "vscode-server-deploy"
$localArchivePath = Join-Path $tempDir $archiveFileName

# ============================================================
# 3. 检查远端是否已安装
# ============================================================

if (-not $Force) {
    Write-Step "检查远端是否已安装此版本"
    $remoteCheck = (& ssh @sshCommonArgs $sshTarget "test -f `$HOME/.vscode-server/bin/${CommitId}/bin/code-server && echo EXISTS || echo NOT_EXISTS" 2>&1) | Out-String
    if ($remoteCheck -match "EXISTS") {
        Write-Info "远端已安装 commit $CommitId 的 VS Code Server，无需重复安装。"
        Write-Info "如需强制重装，请使用 -Force 参数。"
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "  远端已就绪，可直接在 VS Code 中连接。" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        exit 0
    }
}

# ============================================================
# 4. 下载 VS Code Server
# ============================================================

Write-Step "下载 VS Code Server"
Write-Host "  URL: $downloadUrl" -ForegroundColor Gray
Write-Host "  架构: $Arch" -ForegroundColor Gray

New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

if ((Test-Path $localArchivePath) -and (-not $Force)) {
    $cachedSize = (Get-Item $localArchivePath).Length
    if ($cachedSize -gt 1MB) {
        Write-Info "发现本地缓存文件 ($([math]::Round($cachedSize / 1MB, 2)) MB)，跳过下载"
        Write-Host "  路径: $localArchivePath" -ForegroundColor Gray
    } else {
        Write-Warn "缓存文件过小（可能损坏），重新下载..."
        Remove-Item $localArchivePath -Force
    }
}

if (-not (Test-Path $localArchivePath)) {
    try {
        Write-Info "开始下载（约 50-80 MB，请耐心等待）..."
        Invoke-WebRequest -Uri $downloadUrl -OutFile $localArchivePath -UseBasicParsing
    } catch {
        Write-Fail "下载失败: $($_.Exception.Message)"
        Write-Host ""
        Write-Host "  可能原因：" -ForegroundColor Yellow
        Write-Host "  1. 本地网络无法访问 Microsoft CDN（update.code.visualstudio.com）" -ForegroundColor White
        Write-Host "  2. Commit ID 不正确" -ForegroundColor White
        Write-Host "  3. VS Code 版本已更新，请重新获取 Commit ID" -ForegroundColor White
        Write-Host ""
        Write-Host "  替代方案：在浏览器中手动下载以下 URL，然后保存到：" -ForegroundColor Yellow
        Write-Host "  $localArchivePath" -ForegroundColor White
        Write-Host "  然后重新运行本脚本，将自动使用缓存文件。" -ForegroundColor White
        Remove-Item $localArchivePath -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

$downloadSize = (Get-Item $localArchivePath).Length
if ($downloadSize -lt 1MB) {
    Write-Fail "下载文件大小异常（$([math]::Round($downloadSize / 1KB, 2)) KB），可能是错误页面而非安装包。"
    Write-Host "  请在浏览器中访问下载URL确认：$downloadUrl" -ForegroundColor Yellow
    Remove-Item $localArchivePath -Force
    exit 1
}

Write-Info "下载完成，文件大小: $([math]::Round($downloadSize / 1MB, 2)) MB"

# ============================================================
# 5. 上传并在远端安装
# ============================================================

Write-Step "上传 VS Code Server 到远端"

$remoteTmpDir = "/tmp/vscode-server-deploy-${CommitId}"
$localFileSize = (Get-Item $localArchivePath).Length
$localFileSizeMB = [math]::Round($localFileSize / 1MB, 2)

# 在远端创建临时目录
Write-Host "  准备远端临时目录: $remoteTmpDir" -ForegroundColor DarkGray
$mkdirResult = (& ssh @sshCommonArgs $sshTarget "mkdir -p $remoteTmpDir && echo MKDIR_OK" 2>&1) | Out-String
if ($mkdirResult -notmatch "MKDIR_OK") {
    Write-Warn "远端临时目录创建可能失败，继续尝试..."
    Write-Host "  输出: $mkdirResult" -ForegroundColor Gray
}

# 检查远端可用磁盘空间（使用 -k 以KB为单位，兼容BusyBox/BSD df，在awk中转换为MB）
$diskInfo = (& ssh @sshCommonArgs $sshTarget "df -k /tmp 2>/dev/null | tail -1 | awk '{print int(`$4/1024)}'" 2>&1) | Out-String
$diskInfo = $diskInfo.Trim()
$diskAvailMB = 0
[int]::TryParse($diskInfo, [ref]$diskAvailMB) | Out-Null
if ($diskAvailMB -gt 0) {
    Write-Host "  远端 /tmp 可用空间: ${diskAvailMB}MB（需要约 $([math]::Round($localFileSizeMB * 3, 0))MB）" -ForegroundColor DarkGray
} else {
    Write-Host "  远端磁盘空间检查跳过（df 命令不可用或输出异常）" -ForegroundColor DarkGray
}

# ---- SCP 上传压缩包（带进度轮询）----
Write-Host ""
Write-Info "SCP 上传详情："
Write-Host "  本地文件: $localArchivePath" -ForegroundColor White
Write-Host "  文件大小: $localFileSizeMB MB ($localFileSize bytes)" -ForegroundColor White
Write-Host "  目标路径: ${sshTarget}:${remoteTmpDir}/vscode-server.tar.gz" -ForegroundColor White
Write-Host "  SSH 端口: $Port" -ForegroundColor White
Write-Host ""

$remoteArchivePath = "${remoteTmpDir}/vscode-server.tar.gz"
$scpStdErrLog = Join-Path $tempDir "scp-stderr.log"
$scpArgs = @(
    "-P", "$Port",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=15",
    "-o", "ServerAliveInterval=30",
    "-o", "ServerAliveCountMax=6",
    "`"$localArchivePath`"",
    "`"${sshTarget}:${remoteArchivePath}`""
)

# 轮询用的 SSH 参数（更短超时，避免轮询本身卡住）
$pollSshArgs = @(
    "-p", "$Port",
    "-o", "StrictHostKeyChecking=accept-new",
    "-o", "ConnectTimeout=5",
    "-o", "BatchMode=yes"
)

$scpStartTime = Get-Date
Write-Host "  [$($scpStartTime.ToString('HH:mm:ss'))] 开始传输..." -ForegroundColor Cyan

# 清空旧的 stderr 日志
if (Test-Path $scpStdErrLog) { Remove-Item $scpStdErrLog -Force }

# 启动 SCP 进程（stderr 重定向到日志文件用于排障；进度通过 SSH 轮询远端文件大小显示）
$scpProc = Start-Process -FilePath "scp" -ArgumentList $scpArgs -NoNewWindow -PassThru -RedirectStandardError $scpStdErrLog

# ---- 进度轮询配置 ----
$pollIntervalSec = 2
$connectPhase = $true
$prevRemoteSize = 0
$stallCount = 0
$stallThreshold = 5         # 连续 5 次轮询（10秒）无增长 → 警告
$stallCriticalThreshold = 15 # 连续 15 次轮询（30秒）无增长 → 严重警告
$lastReportedPct = -1
$lastReportTime = $scpStartTime
$lastSCPErrPos = 0           # 跟踪 SCP stderr 文件读取位置
$maxConnectWaitSec = 40      # 连接阶段最大等待时间（秒）
$barWidth = 30               # 进度条宽度

while (-not $scpProc.HasExited) {
    Start-Sleep -Seconds $pollIntervalSec
    $elapsed = (Get-Date) - $scpStartTime
    $elapsedSec = [math]::Round($elapsed.TotalSeconds, 1)

    # ---- 实时读取 SCP stderr 新内容（非错误行可能包含连接状态信息）----
    if (Test-Path $scpStdErrLog) {
        $errContent = Get-Content $scpStdErrLog -Raw -ErrorAction SilentlyContinue
        if ($errContent -and $errContent.Length -gt $lastSCPErrPos) {
            $newContent = $errContent.Substring($lastSCPErrPos)
            $lastSCPErrPos = $errContent.Length
            # 过滤掉 SCP 原生进度条（包含 \r 的行），只显示有意义的状态消息
            $newLines = $newContent -split "`n" | Where-Object {
                $_.Trim() -ne "" -and $_ -notmatch "\r" -and $_ -notmatch "^\s*$" -and $_ -notmatch "ETA\s*$" -and $_ -notmatch "^\s*\d+%"
            }
            foreach ($line in $newLines) {
                $trimmed = $line.Trim()
                if ($trimmed -match "Permission denied|Connection refused|Connection timed out|No route to host|Connection reset|lost connection|Host key verification failed") {
                    Write-Host "  [SCP] $trimmed" -ForegroundColor Red
                } elseif ($trimmed -match "Warning|warning") {
                    Write-Host "  [SCP] $trimmed" -ForegroundColor Yellow
                } elseif ($trimmed -match "Connected|connected|Authentication|authenticated|Sending|receiving") {
                    Write-Host "  [SCP] $trimmed" -ForegroundColor DarkGray
                }
            }
        }
    }

    # ---- SSH 轮询远端文件大小 ----
    $remoteSizeStr = (& ssh @pollSshArgs $sshTarget "stat -c %s $remoteArchivePath 2>/dev/null || echo 0" 2>$null) | Out-String
    $remoteSizeStr = $remoteSizeStr.Trim()
    [int64]$remoteSize = 0
    [int64]::TryParse($remoteSizeStr, [ref]$remoteSize) | Out-Null

    # ---- 连接阶段处理（文件大小为0）----
    if ($remoteSize -le 0) {
        if (-not $connectPhase) {
            # 文件曾经有数据但现在stat返回0，可能是瞬时错误，继续
        }
        # 分级提示连接阶段状态
        switch ([math]::Floor($elapsed.TotalSeconds)) {
            4 { Write-Host "  [${elapsedSec}s] 正在建立SSH连接/认证中...（如配置了密码认证，请检查是否需要手动输入）" -ForegroundColor DarkYellow }
            10 {
                Write-Warn "等待 $([math]::Round($elapsed.TotalSeconds))秒仍未开始数据传输"
                Write-Host "  可能原因：" -ForegroundColor Yellow
                Write-Host "  1. SSH 密钥认证未配置，SCP 卡在密码输入（脚本无法交互输入密码）" -ForegroundColor White
                Write-Host "  2. 首次连接需要确认主机指纹（脚本已设置 StrictHostKeyChecking=accept-new 应该能自动接受）" -ForegroundColor White
                Write-Host "  3. 网络延迟高/丢包严重，TCP 连接建立缓慢" -ForegroundColor White
                Write-Host "  建议排障：手动执行 ssh -p $Port $sshTarget 测试登录是否正常" -ForegroundColor White
            }
            20 {
                Write-Host "  [${elapsedSec}s] ⏳ 连接阶段持续较长时间，可能存在网络或认证问题..." -ForegroundColor Yellow
            }
        }
        if ($elapsed.TotalSeconds -ge $maxConnectWaitSec) {
            Write-Fail "连接超时（$([math]::Round($elapsed.TotalSeconds))秒未收到数据），终止SCP进程"
            Stop-Process -Id $scpProc.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
            Write-Host ""
            Write-Host "  排障步骤：" -ForegroundColor Yellow
            Write-Host "  1. 手动测试SSH: ssh -v -p $Port $sshTarget" -ForegroundColor White
            Write-Host "  2. 如需要密码，配置密钥免密：" -ForegroundColor White
            Write-Host "     ssh-keygen -t ed25519  # 生成密钥（已有则跳过）" -ForegroundColor Gray
            Write-Host "     type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh -p $Port $sshTarget `"mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys`"" -ForegroundColor Gray
            Write-Host "  3. 若网络极差，使用 -KeepArchive 保存文件后手动用 WinSCP 上传" -ForegroundColor White
            if (Test-Path $scpStdErrLog) {
                $scpErrText = Get-Content $scpStdErrLog -Raw -ErrorAction SilentlyContinue
                if ($scpErrText) {
                    Write-Host ""
                    Write-Host "  SCP 错误日志（最后10行）:" -ForegroundColor Yellow
                    $scpErrText -split "`n" | Select-Object -Last 10 | ForEach-Object {
                        Write-Host "    $_" -ForegroundColor Gray
                    }
                }
            }
            exit 1
        }
        continue
    }

    # ---- 数据传输阶段 ----
    if ($connectPhase) {
        $connectPhase = $false
        Write-Host "  [${elapsedSec}s] ✓ 连接建立，开始传输数据..." -ForegroundColor Green
        $lastReportTime = Get-Date
        $lastReportedPct = 0
        $prevRemoteSize = 0
    }

    $pct = [math]::Min([math]::Round(($remoteSize / $localFileSize) * 100, 1), 100.0)

    # ---- 停滞检测（字节数无增长）----
    if ($remoteSize -eq $prevRemoteSize) {
        $stallCount++
    } else {
        if ($stallCount -ge $stallThreshold) {
            Write-Host "  [${elapsedSec}s] ✓ 传输恢复（停滞了 $($stallCount * $pollIntervalSec)秒后继续）" -ForegroundColor Green
        }
        $stallCount = 0
    }

    $stallSec = $stallCount * $pollIntervalSec

    # ---- 进度汇报逻辑 ----
    # 每 5% 汇报一次，或每 8 秒，或检测到停滞时
    $pctMilestone = [math]::Floor($pct / 5) * 5
    $shouldReport = ($pctMilestone -gt $lastReportedPct) -or
                    (((Get-Date) - $lastReportTime).TotalSeconds -ge 8) -or
                    ($stallCount -eq $stallThreshold) -or
                    ($stallCount -eq $stallCriticalThreshold)

    if ($shouldReport) {
        $lastReportedPct = $pctMilestone
        $lastReportTime = Get-Date

        # 平均速度
        $avgSpeedKBs = if ($elapsed.TotalSeconds -gt 0) { [math]::Round($remoteSize / 1KB / $elapsed.TotalSeconds, 1) } else { 0 }
        # 瞬时速度（本次轮询间隔内的增量）
        $bytesDelta = $remoteSize - $prevRemoteSize
        $instSpeedKBs = [math]::Round($bytesDelta / 1KB / $pollIntervalSec, 1)
        # ETA（基于瞬时速度，更能反映当前网络状况）
        $remainingBytes = $localFileSize - $remoteSize
        $eta = "?"
        if ($instSpeedKBs -gt 10) {
            $etaSec = [math]::Round($remainingBytes / 1KB / $instSpeedKBs, 0)
            $eta = if ($etaSec -gt 60) { "$([math]::Floor($etaSec/60))分$($etaSec%60)秒" } else { "${etaSec}秒" }
        } elseif ($avgSpeedKBs -gt 10) {
            $etaSec = [math]::Round($remainingBytes / 1KB / $avgSpeedKBs, 0)
            $eta = "${etaSec}秒(均速)"
        }

        # 进度条
        $filledCount = [math]::Round($pct / 100 * $barWidth)
        $bar = "[" + ("█" * $filledCount) + ("░" * ($barWidth - $filledCount)) + "]"

        # 状态标识
        $statusIcon = " "
        $statusColor = [ConsoleColor]::DarkCyan
        if ($stallCount -ge $stallCriticalThreshold) {
            $statusIcon = "⚠"
            $statusColor = [ConsoleColor]::Red
        } elseif ($stallCount -ge $stallThreshold) {
            $statusIcon = "⏳"
            $statusColor = [ConsoleColor]::Yellow
        }

        $transferredMB = [math]::Round($remoteSize / 1MB, 2)
        Write-Host "  [${elapsedSec}s] ${statusIcon}${bar} ${transferredMB}MB/${localFileSizeMB}MB (${pct}%) | 瞬时: ${instSpeedKBs}KB/s | 均速: ${avgSpeedKBs}KB/s | 剩余: ${eta}" -ForegroundColor $statusColor

        # 停滞警告
        if ($stallCount -eq $stallThreshold) {
            Write-Host "  [${elapsedSec}s] ⚠ 传输已停滞 $stallSec 秒（字节数无增长），可能是网络波动，继续等待..." -ForegroundColor Yellow
        } elseif ($stallCount -eq $stallCriticalThreshold) {
            Write-Warn "传输已停滞 $stallSec 秒（$($stallCount)次轮询无字节增长）！"
            Write-Host "  可能原因：网络临时中断、SSH保活超时、远端磁盘IO阻塞" -ForegroundColor Yellow
            Write-Host "  将继续等待，若SCP进程退出则自动报错。如长时间无响应可按 Ctrl+C 终止" -ForegroundColor Yellow
        }
    }

    $prevRemoteSize = $remoteSize
}

# ---- SCP 进程已退出，汇总结果 ----
$scpExitCode = $scpProc.ExitCode
$scpElapsed = (Get-Date) - $scpStartTime
$scpElapsedStr = if ($scpElapsed.TotalMinutes -ge 1) { "$([math]::Round($scpElapsed.TotalMinutes,2))分钟" } else { "$([math]::Round($scpElapsed.TotalSeconds,1))秒" }

# 读取完整 SCP stderr 日志
$scpStdErrContent = ""
if (Test-Path $scpStdErrLog) {
    $scpStdErrContent = Get-Content $scpStdErrLog -Raw -ErrorAction SilentlyContinue
}

if ($scpExitCode -ne 0) {
    Write-Host ""
    Write-Fail "SCP 上传失败（退出码: $scpExitCode，耗时: $scpElapsedStr）"
    if ($scpStdErrContent) {
        Write-Host "  SCP 错误输出:" -ForegroundColor Yellow
        $scpStdErrContent -split "`n" | Where-Object { $_.Trim() -ne "" } | ForEach-Object {
            Write-Host "    $_" -ForegroundColor Gray
        }
    }
    Write-Host ""
    Write-Host "  排障建议：" -ForegroundColor Yellow
    Write-Host "  1. 测试SSH连通性: ssh -v -p $Port $sshTarget" -ForegroundColor White
    Write-Host "  2. 检查远端磁盘空间: ssh -p $Port $sshTarget df -h /tmp" -ForegroundColor White
    Write-Host "  3. 检查远端目录权限: ssh -p $Port $sshTarget ls -la /tmp/" -ForegroundColor White
    Write-Host "  4. 手动执行SCP查看详细错误:" -ForegroundColor White
    Write-Host "     scp -v -P $Port -o ConnectTimeout=15 `"$localArchivePath`" ${sshTarget}:/tmp/" -ForegroundColor Gray
    exit 1
}

# ---- 验证远端文件大小 ----
Write-Host ""
Write-Info "SCP 传输完成，验证远端文件完整性..."
$verifyStart = Get-Date
$remoteFinalSize = (& ssh @sshCommonArgs $sshTarget "stat -c %s $remoteArchivePath 2>/dev/null || echo 0" 2>$null) | Out-String
$remoteFinalSize = $remoteFinalSize.Trim()
[int64]$remoteFinalSizeNum = 0
[int64]::TryParse($remoteFinalSize, [ref]$remoteFinalSizeNum) | Out-Null
$remoteFinalSizeMB = [math]::Round($remoteFinalSizeNum / 1MB, 2)
$verifyElapsed = (Get-Date) - $verifyStart

# 计算传输速率
$avgSpeed = if ($scpElapsed.TotalSeconds -gt 0) { [math]::Round($localFileSize / 1MB / $scpElapsed.TotalSeconds, 2) } else { 0 }

if ($remoteFinalSizeNum -eq $localFileSize) {
    Write-Host "  ✓ 文件大小校验通过（本地 ${localFileSizeMB}MB = 远端 ${remoteFinalSizeMB}MB）" -ForegroundColor Green
} elseif ($remoteFinalSizeNum -gt 0 -and [math]::Abs($remoteFinalSizeNum - $localFileSize) -lt 1024) {
    Write-Host "  ✓ 文件大小基本一致（微小差异 $([math]::Abs($remoteFinalSizeNum - $localFileSize)) bytes，可接受）" -ForegroundColor Green
} elseif ($remoteFinalSizeNum -gt 0) {
    Write-Warn "文件大小不一致！本地: ${localFileSizeMB}MB ($localFileSize bytes), 远端: ${remoteFinalSizeMB}MB ($remoteFinalSizeNum bytes)"
    Write-Host "  差异: $([math]::Round(($remoteFinalSizeNum - $localFileSize) / 1KB, 2)) KB，传输可能不完整" -ForegroundColor Yellow
    Write-Host "  将尝试继续安装，如果失败请使用 -Force 参数重新运行" -ForegroundColor Yellow
} else {
    Write-Fail "远端文件不存在或为空，上传可能失败"
    Write-Host "  验证耗时: $([math]::Round($verifyElapsed.TotalMilliseconds))ms" -ForegroundColor Gray
    if ($scpStdErrContent) {
        Write-Host "  SCP日志最后5行:" -ForegroundColor Yellow
        $scpStdErrContent -split "`n" | Select-Object -Last 5 | ForEach-Object { Write-Host "    $_" -ForegroundColor Gray }
    }
    exit 1
}

Write-Host "  传输耗时: $scpElapsedStr | 平均速度: ${avgSpeed}MB/s | 验证耗时: $([math]::Round($verifyElapsed.TotalMilliseconds))ms" -ForegroundColor DarkGray

# ---- 生成远端安装 bash 脚本 ----
Write-Host ""
Write-Step "远端解压安装"

$bashInstallScript = @'
#!/bin/bash
set -e
set -o pipefail

# ---- 错误陷阱：任何命令失败时输出详细错误信息 ----
trap 'echo "[remote][ERROR] 第 $LINENO 行命令失败: $BASH_COMMAND (退出码: $?)" >&2; exit 1' ERR

# ---- 函数：带时间戳的日志（输出到stdout和stderr，stderr不缓冲，确保实时可见）----
log() {
    local ts
    ts=$(date '+%H:%M:%S')
    echo "[remote][${ts}] $1"
    echo "[remote][${ts}] $1" >&2
}

COMMIT="__COMMIT__"
ARCHIVE="__ARCHIVE__"
INSTALL_DIR="$HOME/.vscode-server/bin/$COMMIT"
TMP_DIR="__TMP_DIR__"

log "========== VS Code Server 安装开始 =========="
log "Commit ID : $COMMIT"
log "压缩包路径: $ARCHIVE"
log "安装目录  : $INSTALL_DIR"
log "临时目录  : $TMP_DIR"

# ---- 步骤1: 环境检查 ----
log "步骤1/5: 环境检查"

# 检查磁盘空间
AVAIL_KB=$(df -k "$HOME" 2>/dev/null | tail -1 | awk '{print $4}')
AVAIL_MB=$((AVAIL_KB / 1024))
ARCHIVE_SIZE=$(stat -c %s "$ARCHIVE" 2>/dev/null || echo 0)
ARCHIVE_MB=$((ARCHIVE_SIZE / 1024 / 1024))
REQUIRED_MB=300
log "  可用磁盘空间: ${AVAIL_MB}MB, 压缩包大小: ${ARCHIVE_MB}MB, 建议可用空间: ${REQUIRED_MB}MB+"
if [ "$AVAIL_MB" -lt "$REQUIRED_MB" ] 2>/dev/null; then
    echo "[remote][ERROR] 磁盘空间不足！可用 ${AVAIL_MB}MB，需要至少 ${REQUIRED_MB}MB" >&2
    echo "[remote][ERROR] 请运行: df -h ~ 查看详情，清理空间后重试" >&2
    exit 2
fi
log "  ✓ 磁盘空间充足"

# 检查必要命令
for cmd in tar mkdir chmod rm stat; do
    if ! command -v $cmd &>/dev/null; then
        echo "[remote][ERROR] 必要命令 $cmd 不存在，请先安装" >&2
        exit 3
    fi
done
log "  ✓ 必要命令齐全"

# 检查压缩包是否存在
if [ ! -f "$ARCHIVE" ]; then
    echo "[remote][ERROR] 压缩包不存在: $ARCHIVE" >&2
    echo "[remote][ERROR] SCP 上传可能失败，请检查网络后重试" >&2
    exit 4
fi
log "  ✓ 压缩包文件存在"

# 检查压缩包完整性（gzip 校验）
log "  校验压缩包完整性（gzip -t）..."
if ! gzip -t "$ARCHIVE" 2>/dev/null; then
    echo "[remote][ERROR] 压缩包损坏或不完整！gzip 校验失败" >&2
    echo "[remote][ERROR] 可能是SCP传输中断，请使用 -Force 参数重新运行部署脚本" >&2
    exit 5
fi
log "  ✓ 压缩包完整性校验通过"

# ---- 步骤2: 创建安装目录 ----
log "步骤2/5: 创建安装目录"
mkdir -p "$INSTALL_DIR"
log "  ✓ 目录已就绪: $INSTALL_DIR"

# ---- 步骤3: 解压（带进度）----
log "步骤3/5: 解压 VS Code Server..."
EXTRACT_START=$(date +%s)
cd "$INSTALL_DIR"

# 使用 tar checkpoint 显示解压进度（GNU tar 支持；BusyBox tar 则静默解压）
if tar --version 2>/dev/null | grep -qi "GNU"; then
    # GNU tar: 每 50 个文件条目输出一个检查点，提供心跳显示解压仍在进行
    log "  (GNU tar 检测到，启用解压心跳提示)"
    tar -xzf "$ARCHIVE" --strip-components=1 \
        --checkpoint=50 \
        --checkpoint-action="echo=[remote]  ...解压中(第 %s 检查点)" \
        2>&1 || {
            echo "[remote][ERROR] tar 解压失败！" >&2
            exit 6
        }
else
    # BusyBox/其他 tar: 不支持 checkpoint，静默解压但加进度提示
    log "  (非GNU tar，静默解压中，请耐心等待...)"
    tar -xzf "$ARCHIVE" --strip-components=1 || {
        echo "[remote][ERROR] tar 解压失败！" >&2
        exit 6
    }
fi

EXTRACT_END=$(date +%s)
EXTRACT_TIME=$((EXTRACT_END - EXTRACT_START))
log "  解压完成，正在统计文件信息..."
FILE_COUNT=$(find "$INSTALL_DIR" -type f 2>/dev/null | wc -l)
DIR_SIZE=$(du -sh "$INSTALL_DIR" 2>/dev/null | cut -f1)
log "  ✓ 解压完成（耗时 ${EXTRACT_TIME} 秒，文件数: ${FILE_COUNT}，解压后大小: ${DIR_SIZE}）"

# ---- 步骤4: 设置执行权限 ----
log "步骤4/5: 设置执行权限"
if [ -f "$INSTALL_DIR/node" ]; then
    chmod +x "$INSTALL_DIR/node"
    log "  ✓ node 可执行权限已设置"
else
    log "  ⚠ 未找到 node 文件，可能是服务器包结构变化"
fi
if [ -f "$INSTALL_DIR/bin/code-server" ]; then
    chmod +x "$INSTALL_DIR/bin/code-server"
    log "  ✓ code-server 可执行权限已设置"
else
    echo "[remote][ERROR] 未找到 bin/code-server，解压可能不完整" >&2
    echo "[remote][ERROR] 可能是架构不匹配或版本问题，请确认 -Arch 参数" >&2
    exit 7
fi
# 对 bin/ 目录下所有文件设为可执行
chmod +x "$INSTALL_DIR/bin/"* 2>/dev/null || true
log "  ✓ bin/ 目录权限设置完成"

# ---- 步骤5: 清理临时文件 ----
log "步骤5/5: 清理临时文件"
rm -rf "$TMP_DIR"
log "  ✓ 临时文件已清理"

# ---- 完成 ----
log "========== VS Code Server 安装成功 =========="
echo "[remote] INSTALL_OK"
'@

# 替换占位符（PowerShell 变量替换，避免 here-string 中 $ 转义问题）
$bashInstallScript = $bashInstallScript.Replace("__COMMIT__", $CommitId)
$bashInstallScript = $bashInstallScript.Replace("__ARCHIVE__", $remoteArchivePath)
$bashInstallScript = $bashInstallScript.Replace("__TMP_DIR__", $remoteTmpDir)

$localBashScript = Join-Path $tempDir "install-vscode-server.sh"
# 使用 BOM-less UTF-8 写入 bash 脚本，避免 Linux 端因 BOM 导致 shebang 解析失败
[System.IO.File]::WriteAllText($localBashScript, $bashInstallScript, [System.Text.UTF8Encoding]::new($false))

# 上传安装脚本
Write-Host "  上传安装脚本..." -ForegroundColor DarkGray
$scriptUploadStart = Get-Date
$scriptStdErrLog = Join-Path $tempDir "scp-script-stderr.log"
& scp -P $Port -o "StrictHostKeyChecking=accept-new" -o "ConnectTimeout=10" "`"$localBashScript`"" "`"${sshTarget}:${remoteTmpDir}/install.sh`"" 2>$scriptStdErrLog
$scriptUploadElapsed = (Get-Date) - $scriptUploadStart
if ($LASTEXITCODE -ne 0) {
    Write-Fail "安装脚本上传失败。"
    if (Test-Path $scriptStdErrLog) {
        Write-Host "  错误: $(Get-Content $scriptStdErrLog -Raw)" -ForegroundColor Gray
    }
    exit 1
}
Write-Host "  ✓ 安装脚本已上传（耗时 $([math]::Round($scriptUploadElapsed.TotalMilliseconds))ms）" -ForegroundColor DarkGray

# ---- 执行远端安装（流式输出，实时显示日志）----
Write-Host ""
Write-Info "执行远端安装脚本..."
Write-Host "  ──────────── 远端安装日志开始 ────────────" -ForegroundColor DarkCyan
$installStart = Get-Date
$installLogFile = Join-Path $tempDir "remote-install.log"

# 使用 Tee-Object 将 SSH 输出实时显示到控制台同时保存到日志文件
# 注意：Tee-Object 会逐行处理输出，实现流式显示
& ssh @sshCommonArgs $sshTarget "bash ${remoteTmpDir}/install.sh" 2>&1 | Tee-Object -FilePath $installLogFile
$installExitCode = $LASTEXITCODE
$installElapsed = (Get-Date) - $installStart
Write-Host "  ──────────── 远端安装日志结束 ────────────" -ForegroundColor DarkCyan
Write-Host "  远端执行耗时: $([math]::Round($installElapsed.TotalSeconds,1))秒" -ForegroundColor DarkGray

# 读取完整日志用于错误分析
$installResult = if (Test-Path $installLogFile) { Get-Content $installLogFile -Raw -ErrorAction SilentlyContinue } else { "" }

if ($installExitCode -ne 0) {
    Write-Host ""
    Write-Fail "远端安装失败（退出码: $installExitCode，耗时: $([math]::Round($installElapsed.TotalSeconds,1))秒）"
    Write-Host ""

    # 根据退出码给出精准排障建议
    switch ($installExitCode) {
        2 { Write-Host "  → 退出码2：磁盘空间不足，请清理后重试" -ForegroundColor White; Write-Host "    诊断命令: ssh -p $Port $sshTarget 'df -h ~ && du -sh ~/.vscode-server/ 2>/dev/null'" -ForegroundColor Gray }
        3 { Write-Host "  → 退出码3：必要命令缺失，请安装 tar/gzip/coreutils" -ForegroundColor White }
        4 { Write-Host "  → 退出码4：压缩包不存在，SCP上传可能失败" -ForegroundColor White; Write-Host "    诊断命令: ssh -p $Port $sshTarget ls -la $remoteArchivePath" -ForegroundColor Gray }
        5 { Write-Host "  → 退出码5：压缩包损坏（gzip校验失败），请使用 -Force 重新运行" -ForegroundColor White }
        6 { Write-Host "  → 退出码6：tar解压失败，可能是磁盘满或包格式错误" -ForegroundColor White }
        7 { Write-Host "  → 退出码7：解压结构异常，可能是版本架构不匹配" -ForegroundColor White; Write-Host "    请确认 -Arch 参数（x64/arm64/armhf）与远端架构一致" -ForegroundColor Gray }
        128 { Write-Host "  → 脚本被信号中断（可能是SSH连接断开）" -ForegroundColor White }
        default {
            Write-Host "  根据日志排查：" -ForegroundColor Yellow
            if ($installResult -match "磁盘空间不足") {
                Write-Host "  → 磁盘空间不足，请清理后重试：ssh -p $Port $sshTarget 'df -h ~ && du -sh ~/.vscode-server/ 2>/dev/null'" -ForegroundColor White
            }
            if ($installResult -match "压缩包损坏" -or $installResult -match "gzip") {
                Write-Host "  → 压缩包损坏，请使用 -Force 参数重新运行（会重新下载和上传）" -ForegroundColor White
            }
            if ($installResult -match "code-server" -and $installResult -match "不存在") {
                Write-Host "  → 解压结构异常，可能是版本架构不匹配，请确认 -Arch 参数正确" -ForegroundColor White
            }
            if ($installResult -notmatch "磁盘|压缩包|code-server|tar|command|解压失败") {
                Write-Host "  → 请将上方完整日志发给AI助手或团队同事协助排查" -ForegroundColor White
                Write-Host "  手动登录调试: ssh -p $Port $sshTarget" -ForegroundColor White
            }
        }
    }
    exit 1
}

# 验证安装
Write-Host ""
Write-Info "安装后验证..."
$verifyStart = Get-Date
$verifyResult = (& ssh @sshCommonArgs $sshTarget "test -x `$HOME/.vscode-server/bin/${CommitId}/bin/code-server && echo VERIFY_OK || echo VERIFY_FAIL" 2>&1) | Out-String
$verifyElapsed = (Get-Date) - $verifyStart

if ($verifyResult -notmatch "VERIFY_OK") {
    Write-Fail "安装验证失败：code-server 不存在或不可执行。"
    Write-Host "  请手动检查: ssh -p $Port $sshTarget ls -la ~/.vscode-server/bin/${CommitId}/bin/" -ForegroundColor Yellow
    exit 1
}

# 额外验证：获取版本信息
$serverInfo = (& ssh @sshCommonArgs $sshTarget "ls -la `$HOME/.vscode-server/bin/${CommitId}/bin/code-server && du -sh `$HOME/.vscode-server/bin/${CommitId}/" 2>&1) | Out-String
Write-Host "  ✓ code-server 存在且可执行（验证耗时 $([math]::Round($verifyElapsed.TotalMilliseconds))ms）" -ForegroundColor Green
Write-Host "  远端安装信息:" -ForegroundColor DarkGray
Write-Host ($serverInfo -split "`n" | ForEach-Object { "    $_" }) -ForegroundColor Gray

# ============================================================
# 6. 清理本地临时文件
# ============================================================

if (-not $KeepArchive) {
    Remove-Item -Recurse -Force $tempDir -ErrorAction SilentlyContinue
    Write-Info "本地临时文件已清理"
} else {
    Write-Info "本地文件保留在: $tempDir"
}

# ============================================================
# 输出结果
# ============================================================

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "  VS Code Server 部署成功！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Commit ID : $CommitId" -ForegroundColor White
Write-Host "  架构      : $Arch" -ForegroundColor White
Write-Host "  目标      : $sshTarget" -ForegroundColor White
Write-Host "  安装路径  : ~/.vscode-server/bin/$CommitId/" -ForegroundColor White
Write-Host ""
Write-Host "  下一步操作：" -ForegroundColor Yellow
Write-Host "  1. 回到 VS Code" -ForegroundColor White
Write-Host "  2. 关闭当前卡住的 Remote-SSH 连接窗口" -ForegroundColor White
Write-Host "  3. 重新连接 $Server" -ForegroundColor White
Write-Host "  4. VS Code 将检测到 Server 已安装，直接启动" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
