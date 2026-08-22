<#
.SYNOPSIS
    自动下载 Trae (trae-cn) 远端服务端并通过 SCP 部署到远端 Linux 服务器
.DESCRIPTION
    作为 "remote.SSH.preferLocalDownload" 失效时的兜底方案，解决 Trae Remote-SSH
    卡在 "Downloading and installing remote server"、或报 2001/2002 错误的问题。
    从 Trae 输出面板读取 DISTRO_COMMIT 与下载链接，本地下载 trae 服务端包，
    SCP 上传到远端并解压到 ~/.trae-cn-server（自动处理组件命名 trae-cn-server/trae-server）。
    前提：本地已配置 SSH 密钥免密登录远端，或远端接受手动输入密码。

    ⚠ Trae 与 VS Code 的远端组件不同：组件名为 trae-cn-server（国内）/ trae-server（国际），
      数据目录为 ~/.trae-cn-server，下载源为字节 CDN（非 Microsoft CDN）。

.PARAMETER Server
    远端服务器地址（IP 或域名），也可用别名 -Host
.PARAMETER User
    SSH 用户名
.PARAMETER Port
    SSH 端口，默认 22
.PARAMETER Arch
    远端架构（x64/arm64/armhf），默认自动通过 uname -m 检测
.PARAMETER CommitId
    Trae 远端服务端 DISTRO_COMMIT（40位十六进制）。不指定则尝试从本地 Trae 安装目录读取，
    若仍无法确定，请从 Trae 输出面板日志中的 "DISTRO_COMMIT" 行复制。
.PARAMETER DownloadUrl
    Trae 远端服务端下载链接。优先从 Trae 输出面板的报错链接或 "SERVER_DOWNLOAD_PREFIX"
    拼接结果中复制（整链，含文件名）。若不指定且本地无缓存，将提示手动下载并保存到本地缓存路径后重跑。
.PARAMETER ServerDataDir
    Trae 远端数据目录，默认 "~/.trae-cn-server"（国际版/旧版可能为 "~/.trae-server"）
.PARAMETER BinDir
    远端 bin 子目录精确名，默认与 CommitId 相同。若 Trae 客户端期望
    "stable-<commit>-debian10" 这类格式，请从输出面板 install.sh 的 SERVER_DIR 行复制后指定。
.PARAMETER ServerAppName
    服务端组件名，默认 "trae-cn-server"（旧版/国际版可能为 "trae-server"）
.PARAMETER KeepArchive
    保留本地下载的压缩包，不自动清理
.PARAMETER Force
    强制重新安装，即使远端已存在相同 commit 的服务端
.PARAMETER MaxRetries
    下载/SCP 上传失败时的最大重试次数，默认 3。网络类错误（超时/连接重置/断开）才会重试，
    认证失败、主机不可达等持续性问题不会重试。
.PARAMETER RetryDelaySeconds
    重试基础退避间隔（秒），默认 5。实际等待为指数退避：第 N 次重试等待 RetryDelaySeconds * 2^(N-1) 秒。
.PARAMETER ScpStallTimeoutSeconds
    SCP 上传停滞检测阈值（秒），默认 60。若传输字节数在该时长内无增长，则主动中止 scp 进程并重试。
.EXAMPLE
    .\deploy-trae-server.ps1 -Server 10.16.11.3 -User root -CommitId <DISTRO_COMMIT> -DownloadUrl <下载链接>
.EXAMPLE
    .\deploy-trae-server.ps1 -Server 10.16.11.3 -User myuser -Port 2222 -Arch arm64
.EXAMPLE
    .\deploy-trae-server.ps1 -Host server.example.com -User dev -ServerDataDir "~/.trae-server" -ServerAppName "trae-server"
.EXAMPLE
    .\deploy-trae-server.ps1 -Server 10.16.11.3 -User root -CommitId <DISTRO_COMMIT> -DownloadUrl <下载链接> -MaxRetries 5 -RetryDelaySeconds 3 -ScpStallTimeoutSeconds 90
.NOTES
    Author: SpecWeave Agent
    Version: 1.1.0
    Requires: PowerShell 5+，本地已安装 ssh/scp（Windows 10 1809+ 自带）
    Changelog: v1.0.0 - 基于 deploy-vscode-server.ps1 改造，适配 trae-cn 远端服务端（组件名/目录/CDN 差异）
               v1.1.0 - 新增下载/SCP 上传自动重试机制（指数退避 + 可重试错误识别 + 停滞超时中止）
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

    [string]$DownloadUrl = "",

    [string]$ServerDataDir = "~/.trae-cn-server",

    [string]$BinDir = "",

    [string]$ServerAppName = "trae-cn-server",

    [switch]$KeepArchive,

    [switch]$Force,

    [int]$MaxRetries = 3,

    [int]$RetryDelaySeconds = 5,

    [int]$ScpStallTimeoutSeconds = 60
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

function Test-RetryableError {
    param([string]$Message)
    # 判断错误是否值得重试：网络波动类可重试，认证/配置/主机不可达等持续性问题不重试
    if ([string]::IsNullOrWhiteSpace($Message)) {
        return $true   # 无错误信息时默认可重试
    }
    # 非网络原因（重试无意义），匹配顺序优先
    $nonRetryable = @(
        "Permission denied", "No such file or directory",
        "Host key verification failed", "No route to host",
        "Connection refused", "Could not resolve hostname",
        "Authentication failed"
    )
    # 网络波动类（可重试）
    $retryable = @(
        "timed out", "Connection timed out", "Connection reset",
        "reset by peer", "lost connection", "Connection closed",
        "Network is unreachable", "Broken pipe",
        "Software caused connection abort", "Connection aborted",
        "Connection to .* closed by remote host"
    )
    foreach ($p in $nonRetryable) {
        if ($Message -match $p) { return $false }
    }
    foreach ($p in $retryable) {
        if ($Message -match $p) { return $true }
    }
    return $true   # 未命中明确分类，默认保守重试
}

function Get-BackoffDelay {
    param([int]$Attempt, [int]$BaseSeconds)
    # 指数退避：第 N 次重试等待 BaseSeconds * 2^(N-1) 秒
    $delay = $BaseSeconds * [math]::Pow(2, $Attempt - 1)
    return [int]$delay
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
# 1. 确定 Trae 远端服务端 Commit ID（DISTRO_COMMIT）
# ============================================================

Write-Step "确定 Trae 服务端 Commit ID (DISTRO_COMMIT)"

if (-not $CommitId) {
    # 按优先级尝试 Trae 常见安装路径（product.json 中的 commit 字段）
    $possiblePaths = @(
        # 用户安装（User setup）—— 最常见
        "$env:LOCALAPPDATA\Programs\Trae\resources\app\product.json",
        "$env:LOCALAPPDATA\Programs\Trae CN\resources\app\product.json",
        "$env:LOCALAPPDATA\Programs\Trae Chinese\resources\app\product.json",
        # 系统安装（Machine-wide）
        "${env:ProgramFiles}\Trae\resources\app\product.json",
        "${env:ProgramFiles(x86)}\Trae\resources\app\product.json",
        # Scoop
        "$env:USERPROFILE\scoop\apps\trae\current\product.json"
    )

    foreach ($path in $possiblePaths) {
        if ($path -and (Test-Path $path)) {
            try {
                $product = Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json
                if ($product.commit) {
                    $CommitId = $product.commit
                    Write-Info "从 Trae 安装目录检测到 commit: $CommitId"
                    Write-Host "  路径: $path" -ForegroundColor Gray
                    Write-Warn "注意：Trae 远端服务端的 DISTRO_COMMIT 可能与本地 commit 不一致，若连接后仍提示下载，请用 -CommitId 手动指定输出面板中的 DISTRO_COMMIT。"
                    break
                }
            } catch {
                # 跳过无法解析的文件
            }
        }
    }

    if (-not $CommitId) {
        Write-Fail "无法自动检测 Trae 服务端 Commit ID。"
        Write-Host ""
        Write-Host "  获取方法（Trae 远端服务端 DISTRO_COMMIT 最可靠）：" -ForegroundColor Yellow
        Write-Host "  1. 在 Trae 中发起一次 SSH 连接（卡住也无妨）" -ForegroundColor White
        Write-Host "  2. 打开「输出」面板，选择 Remote-SSH 日志" -ForegroundColor White
        Write-Host "  3. 找到以 DISTRO_COMMIT= 开头的行，复制后面的40位十六进制字符串" -ForegroundColor White
        Write-Host "  4. 使用 -CommitId 参数手动指定，例如：" -ForegroundColor White
        Write-Host "     .\deploy-trae-server.ps1 -Server $Server -User $User -CommitId <你的DISTRO_COMMIT>" -ForegroundColor White
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

# 架构到下载文件标识映射（用于提示与 fallback，trae 通常以整链下载）
$archToFile = @{
    "x64"   = "linux-x64"
    "arm64" = "linux-arm64"
    "armhf" = "linux-armhf"
}
$archSegment = $archToFile[$Arch]
$archiveFileName = "trae-server-linux-${Arch}-${CommitId}.tar.gz"
$tempDir = Join-Path $env:TEMP "trae-server-deploy"
$localArchivePath = Join-Path $tempDir $archiveFileName

# 下载 URL：优先使用用户提供的 -DownloadUrl（Trae 从字节 CDN 下载，整链含文件名）
$downloadUrl = $DownloadUrl

# 安装路径相关变量（组件名 / 数据目录 / bin 子目录）
$binDirName = if ($BinDir) { $BinDir } else { $CommitId }
$remoteInstallDir = "${ServerDataDir}/bin/${binDirName}"

# ============================================================
# 3. 检查远端是否已安装
# ============================================================

if (-not $Force) {
    Write-Step "检查远端是否已安装此版本"
    $remoteCheck = (& ssh @sshCommonArgs $sshTarget "test -f ${remoteInstallDir}/bin/${ServerAppName} -o -f ${remoteInstallDir}/bin/trae-server -o -f ${remoteInstallDir}/bin/trae-cn-server && echo EXISTS || echo NOT_EXISTS" 2>&1) | Out-String
    if ($remoteCheck -match "EXISTS") {
        Write-Info "远端已安装 commit $CommitId 的 Trae 服务端（${ServerAppName}），无需重复安装。"
        Write-Info "如需强制重装，请使用 -Force 参数。"
        Write-Host ""
        Write-Host "==========================================" -ForegroundColor Green
        Write-Host "  远端已就绪，可直接在 Trae 中连接。" -ForegroundColor Green
        Write-Host "==========================================" -ForegroundColor Green
        exit 0
    }
}

# ============================================================
# 4. 下载 Trae 服务端
# ============================================================

Write-Step "下载 Trae 服务端"

New-Item -ItemType Directory -Force -Path $tempDir | Out-Null

# 若本地已有有效缓存，则跳过下载
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

# 下载 URL 缺失处理
if (-not $downloadUrl -and -not (Test-Path $localArchivePath)) {
    Write-Fail "缺少下载链接（-DownloadUrl）。Trae 服务端包从字节 CDN 下载，无法仅凭 commit 可靠构造 URL。"
    Write-Host ""
    Write-Host "  获取下载链接的方法：" -ForegroundColor Yellow
    Write-Host "  1. 在 Trae 中发起一次 SSH 连接（卡住也无妨）" -ForegroundColor White
    Write-Host "  2. 打开「输出」面板选择 Remote-SSH 日志" -ForegroundColor White
    Write-Host "  3. 找到 'SERVER_DOWNLOAD_PREFIX' 行，复制完整下载链接（含文件名）" -ForegroundColor White
    Write-Host "     或复制报错中 'Error downloading server from ...' 后的完整 URL" -ForegroundColor White
    Write-Host "  4. 用 -DownloadUrl 参数传入，例如：" -ForegroundColor White
    Write-Host "     .\deploy-trae-server.ps1 -Server $Server -User $User -CommitId $CommitId -DownloadUrl <下载链接>" -ForegroundColor White
    Write-Host ""
    Write-Host "  也可先用浏览器/其他工具手动下载该包，保存为下面路径后重新运行本脚本（将自动使用缓存）：" -ForegroundColor Yellow
    Write-Host "  $localArchivePath" -ForegroundColor White
    exit 1
}

if (-not (Test-Path $localArchivePath)) {
    Write-Host "  URL: $downloadUrl" -ForegroundColor Gray
    Write-Host "  架构: $Arch" -ForegroundColor Gray

    $downloadOk = $false
    $downloadErrMsg = ""
    $downloadRetryable = $true

    for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
        if ($attempt -gt 1) {
            $wait = Get-BackoffDelay -Attempt ($attempt - 1) -BaseSeconds $RetryDelaySeconds
            Write-Warn "下载失败，指数退避等待 ${wait} 秒后第 ${attempt}/${MaxRetries} 次重试..."
            Start-Sleep -Seconds $wait
        }
        try {
            Write-Info "开始下载（Trae 服务端包约 50-100 MB，请耐心等待）... [尝试 ${attempt}/${MaxRetries}]"
            Invoke-WebRequest -Uri $downloadUrl -OutFile $localArchivePath -UseBasicParsing

            # 下载后立即做大小合法性初检，太小说明拿到的是错误页
            $downloadedSize = (Get-Item $localArchivePath).Length
            if ($downloadedSize -lt 1MB) {
                throw "下载文件异常小（$([math]::Round($downloadedSize / 1KB, 2)) KB），可能是错误页面或下载不完整"
            }
            $downloadOk = $true
            break
        } catch {
            $downloadErrMsg = $_.Exception.Message
            $downloadRetryable = Test-RetryableError $downloadErrMsg
            Write-Fail "第 ${attempt}/${MaxRetries} 次下载失败: $downloadErrMsg"
            if (-not $downloadRetryable) {
                Write-Host "  该错误属于非网络原因，停止重试" -ForegroundColor Yellow
                break
            }
            Remove-Item $localArchivePath -Force -ErrorAction SilentlyContinue
        }
    }

    if (-not $downloadOk) {
        Write-Fail "下载失败（已尝试 ${attempt}/${MaxRetries} 次）: $downloadErrMsg"
        Write-Host ""
        Write-Host "  可能原因：" -ForegroundColor Yellow
        Write-Host "  1. 本地网络无法访问字节 CDN（lf-cdn.trae.ai 等）或对应镜像源" -ForegroundColor White
        Write-Host "  2. 下载链接已过期或版本已更新" -ForegroundColor White
        Write-Host "  3. Distro_Commit 不正确，导致路径 404" -ForegroundColor White
        Write-Host ""
        Write-Host "  替代方案：换成国内可访问的镜像（如 VSCodium GitHub release 对应用/release 包的 trae 镜像），" -ForegroundColor Yellow
        Write-Host "  手动下载后保存到：$localArchivePath，再重新运行本脚本。" -ForegroundColor White
        Remove-Item $localArchivePath -Force -ErrorAction SilentlyContinue
        exit 1
    }
}

$downloadSize = (Get-Item $localArchivePath).Length
if ($downloadSize -lt 1MB) {
    Write-Fail "下载文件大小异常（$([math]::Round($downloadSize / 1KB, 2)) KB），可能是错误页面而非安装包。"
    Write-Host "  请在浏览器中访问下载 URL 确认：$downloadUrl" -ForegroundColor Yellow
    Remove-Item $localArchivePath -Force
    exit 1
}

Write-Info "下载完成，文件大小: $([math]::Round($downloadSize / 1MB, 2)) MB"

# ============================================================
# 5. 上传并在远端安装
# ============================================================

$remoteTmpDir = "/tmp/trae-server-deploy-${CommitId}"
$localFileSize = (Get-Item $localArchivePath).Length
$localFileSizeMB = [math]::Round($localFileSize / 1MB, 2)

# 在远端创建临时目录（重试前只执行一次）
Write-Step "准备远端临时目录"
Write-Host "  临时目录: $remoteTmpDir" -ForegroundColor DarkGray
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

$remoteArchivePath = "${remoteTmpDir}/trae-server.tar.gz"

# ============================================================
# Invoke-ScpUpload：单次 SCP 上传（带进度轮询、停滞检测）
# 返回结果对象：Success / ErrorMessage / Retryable / ExitCode
# ============================================================
function Invoke-ScpUpload {
    param(
        [string]$LocalPath,
        [string]$RemotePath,
        [string]$SshTarget,
        [int]$Port,
        [string]$TempDir,
        [int64]$LocalFileSize,
        [double]$LocalFileSizeMB,
        [int]$ScpStallTimeoutSeconds
    )

    $scpStdErrLog = Join-Path $TempDir "scp-stderr.log"
    $scpArgs = @(
        "-P", "$Port",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=15",
        "-o", "ServerAliveInterval=30",
        "-o", "ServerAliveCountMax=6",
        "`"$LocalPath`"",
        "`"${SshTarget}:${RemotePath}`""
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
    $stallThreshold = 5          # 连续 5 次轮询（10秒）无增长 → 警告
    $stallCriticalThreshold = 15 # 连续 15 次轮询（30秒）无增长 → 严重警告
    $stallAbortThreshold = [math]::Max($stallCriticalThreshold, [int][math]::Floor($ScpStallTimeoutSeconds / $pollIntervalSec))
    $lastReportedPct = -1
    $lastReportTime = $scpStartTime
    $lastSCPErrPos = 0           # 跟踪 SCP stderr 文件读取位置
    $maxConnectWaitSec = 40      # 连接阶段最大等待时间（秒）
    $barWidth = 30               # 进度条宽度
    $abortRequested = $false
    $abortReason = ""

    while (-not $scpProc.HasExited -and -not $abortRequested) {
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
        $remoteSizeStr = (& ssh @pollSshArgs $SshTarget "stat -c %s $RemotePath 2>/dev/null || echo 0" 2>$null) | Out-String
        $remoteSizeStr = $remoteSizeStr.Trim()
        [int64]$remoteSize = 0
        [int64]::TryParse($remoteSizeStr, [ref]$remoteSize) | Out-Null

        # ---- 连接阶段处理（文件大小为0）----
        if ($remoteSize -le 0) {
            # 分级提示连接阶段状态
            switch ([math]::Floor($elapsed.TotalSeconds)) {
                4 { Write-Host "  [${elapsedSec}s] 正在建立SSH连接/认证中...（如配置了密码认证，请检查是否需要手动输入）" -ForegroundColor DarkYellow }
                10 {
                    Write-Warn "等待 $([math]::Round($elapsed.TotalSeconds))秒仍未开始数据传输"
                    Write-Host "  可能原因：" -ForegroundColor Yellow
                    Write-Host "  1. SSH 密钥认证未配置，SCP 卡在密码输入（脚本无法交互输入密码）" -ForegroundColor White
                    Write-Host "  2. 首次连接需要确认主机指纹（脚本已设置 StrictHostKeyChecking=accept-new 应该能自动接受）" -ForegroundColor White
                    Write-Host "  3. 网络延迟高/丢包严重，TCP 连接建立缓慢" -ForegroundColor White
                    Write-Host "  建议排障：手动执行 ssh -p $Port $SshTarget 测试登录是否正常" -ForegroundColor White
                }
                20 {
                    Write-Host "  [${elapsedSec}s] ⏳ 连接阶段持续较长时间，可能存在网络或认证问题..." -ForegroundColor Yellow
                }
            }
            if ($elapsed.TotalSeconds -ge $maxConnectWaitSec) {
                $abortRequested = $true
                $abortReason = "连接超时（$([math]::Round($elapsed.TotalSeconds))秒未开始传输数据）"
                Stop-Process -Id $scpProc.Id -Force -ErrorAction SilentlyContinue
                Start-Sleep -Milliseconds 500
                break
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

        $pct = [math]::Min([math]::Round(($remoteSize / $LocalFileSize) * 100, 1), 100.0)

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

        # ---- 停滞超时自动中止（触发外层重试）----
        if ($stallCount -ge $stallAbortThreshold) {
            $abortRequested = $true
            $abortReason = "传输停滞 $stallSec 秒（超过阈值 $ScpStallTimeoutSeconds 秒），判定为网络中断"
            Stop-Process -Id $scpProc.Id -Force -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 500
            break
        }

        # ---- 进度汇报逻辑（每 5% 或每 8 秒或停滞时）----
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
            $remainingBytes = $LocalFileSize - $remoteSize
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
            Write-Host "  [${elapsedSec}s] ${statusIcon}${bar} ${transferredMB}MB/${LocalFileSizeMB}MB (${pct}%) | 瞬时: ${instSpeedKBs}KB/s | 均速: ${avgSpeedKBs}KB/s | 剩余: ${eta}" -ForegroundColor $statusColor

            # 停滞警告
            if ($stallCount -eq $stallThreshold) {
                Write-Host "  [${elapsedSec}s] ⚠ 传输已停滞 $stallSec 秒（字节数无增长），可能是网络波动，继续等待..." -ForegroundColor Yellow
            } elseif ($stallCount -eq $stallCriticalThreshold) {
                Write-Warn "传输已停滞 $stallSec 秒（$($stallCount)次轮询无字节增长）！"
                Write-Host "  若超过 $ScpStallTimeoutSeconds 秒仍未恢复，将自动中止并重试" -ForegroundColor Yellow
            }
        }

        $prevRemoteSize = $remoteSize
    }

    # 若因停滞/连接超时被主动中止，直接判定为可重试失败
    if ($abortRequested) {
        return @{ Success = $false; ErrorMessage = $abortReason; Retryable = $true; ExitCode = -1 }
    }

    # ---- SCP 进程已退出，汇总结果 ----
    $scpExitCode = $scpProc.ExitCode
    $scpElapsed = (Get-Date) - $scpStartTime
    $scpElapsedStr = if ($scpElapsed.TotalMinutes -ge 1) { "$([math]::Round($scpElapsed.TotalMinutes,2))分钟" } else { "$([math]::Round($scpElapsed.TotalSeconds,1))秒" }

    $scpStdErrContent = ""
    if (Test-Path $scpStdErrLog) {
        $scpStdErrContent = Get-Content $scpStdErrLog -Raw -ErrorAction SilentlyContinue
    }

    if ($scpExitCode -ne 0) {
        $retryable = Test-RetryableError $scpStdErrContent
        if ($scpStdErrContent) {
            Write-Host "  SCP 错误输出:" -ForegroundColor Yellow
            $scpStdErrContent -split "`n" | Where-Object { $_.Trim() -ne "" } | ForEach-Object {
                Write-Host "    $_" -ForegroundColor Gray
            }
        }
        return @{ Success = $false; ErrorMessage = "SCP 进程退出码 $scpExitCode（耗时 $scpElapsedStr）"; Retryable = $retryable; ExitCode = $scpExitCode }
    }

    # ---- 验证远端文件大小 ----
    Write-Host ""
    Write-Info "SCP 传输完成，验证远端文件完整性..."
    $remoteFinalSize = (& ssh @pollSshArgs $SshTarget "stat -c %s $RemotePath 2>/dev/null || echo 0" 2>$null) | Out-String
    $remoteFinalSize = $remoteFinalSize.Trim()
    [int64]$remoteFinalSizeNum = 0
    [int64]::TryParse($remoteFinalSize, [ref]$remoteFinalSizeNum) | Out-Null
    $remoteFinalSizeMB = [math]::Round($remoteFinalSizeNum / 1MB, 2)

    $avgSpeed = if ($scpElapsed.TotalSeconds -gt 0) { [math]::Round($LocalFileSize / 1MB / $scpElapsed.TotalSeconds, 2) } else { 0 }

    if ($remoteFinalSizeNum -eq $LocalFileSize) {
        Write-Host "  ✓ 文件大小校验通过（本地 ${LocalFileSizeMB}MB = 远端 ${remoteFinalSizeMB}MB）" -ForegroundColor Green
    } elseif ($remoteFinalSizeNum -gt 0 -and [math]::Abs($remoteFinalSizeNum - $LocalFileSize) -lt 1024) {
        Write-Host "  ✓ 文件大小基本一致（微小差异 $([math]::Abs($remoteFinalSizeNum - $LocalFileSize)) bytes，可接受）" -ForegroundColor Green
    } elseif ($remoteFinalSizeNum -gt 0) {
        Write-Warn "文件大小不一致！本地: ${LocalFileSizeMB}MB, 远端: ${remoteFinalSizeMB}MB，传输可能不完整"
        return @{ Success = $false; ErrorMessage = "文件大小不一致（本地 $LocalFileSize 字节 vs 远端 $remoteFinalSizeNum 字节）"; Retryable = $true; ExitCode = -2 }
    } else {
        return @{ Success = $false; ErrorMessage = "远端文件不存在或为空，上传可能失败"; Retryable = $true; ExitCode = -3 }
    }

    Write-Host "  传输耗时: $scpElapsedStr | 平均速度: ${avgSpeed}MB/s" -ForegroundColor DarkGray
    return @{ Success = $true; ErrorMessage = ""; Retryable = $false; ExitCode = 0 }
}

# ---- SCP 上传（带自动重试，抵御网络波动）----
$scpSuccess = $false
$lastScpResult = $null

for ($attempt = 1; $attempt -le $MaxRetries; $attempt++) {
    Write-Step "上传 Trae 服务端到远端 (第 ${attempt}/${MaxRetries} 次尝试)"
    Write-Host "  本地文件: $localArchivePath" -ForegroundColor White
    Write-Host "  文件大小: $localFileSizeMB MB ($localFileSize bytes)" -ForegroundColor White
    Write-Host "  目标路径: ${sshTarget}:${remoteArchivePath}" -ForegroundColor White
    Write-Host "  SSH 端口: $Port" -ForegroundColor White
    Write-Host ""

    if ($attempt -gt 1) {
        $wait = Get-BackoffDelay -Attempt ($attempt - 1) -BaseSeconds $RetryDelaySeconds
        Write-Warn "指数退避等待 ${wait} 秒后重试..."
        Start-Sleep -Seconds $wait
    }

    $lastScpResult = Invoke-ScpUpload -LocalPath $localArchivePath -RemotePath $remoteArchivePath -SshTarget $sshTarget -Port $Port -TempDir $tempDir -LocalFileSize $localFileSize -LocalFileSizeMB $localFileSizeMB -ScpStallTimeoutSeconds $ScpStallTimeoutSeconds

    if ($lastScpResult.Success) {
        $scpSuccess = $true
        break
    }

    Write-Fail "第 ${attempt}/${MaxRetries} 次上传失败：$($lastScpResult.ErrorMessage)"

    if (-not $lastScpResult.Retryable) {
        Write-Host "  该错误属于非网络原因（如认证失败、主机不可达、文件不存在），重试无意义，停止。" -ForegroundColor Yellow
        break
    }
    if ($attempt -ge $MaxRetries) {
        Write-Host "  已达到最大重试次数。" -ForegroundColor Yellow
    }
}

if (-not $scpSuccess) {
    Write-Host ""
    Write-Fail "SCP 上传失败（已尝试 ${attempt}/${MaxRetries} 次）。"
    Write-Host "  最后一次错误: $($lastScpResult.ErrorMessage)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  排障建议：" -ForegroundColor Yellow
    Write-Host "  1. 测试SSH连通性: ssh -v -p $Port $sshTarget" -ForegroundColor White
    Write-Host "  2. 检查远端磁盘空间: ssh -p $Port $sshTarget df -h /tmp" -ForegroundColor White
    Write-Host "  3. 若网络持续不稳定，使用 -KeepArchive 保留本地文件后手动用 WinSCP/rsync 上传到 ${remoteArchivePath}" -ForegroundColor White
    Write-Host "  4. 可通过 -MaxRetries N -RetryDelaySeconds N -ScpStallTimeoutSeconds N 调整重试策略" -ForegroundColor White
    exit 1
}

Write-Info "SCP 上传成功。"

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
SERVER_DATA_DIR="__SERVER_DATA_DIR__"
BIN_DIR="__BIN_DIR__"
SERVER_APP_NAME="__SERVER_APP_NAME__"
INSTALL_DIR="$SERVER_DATA_DIR/bin/$BIN_DIR"
TMP_DIR="__TMP_DIR__"

log "========== Trae 服务端安装开始 =========="
log "Commit ID  : $COMMIT"
log "组件名     : $SERVER_APP_NAME"
log "压缩包路径 : $ARCHIVE"
log "安装目录   : $INSTALL_DIR"
log "临时目录   : $TMP_DIR"

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
log "步骤3/5: 解压 Trae 服务端..."
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

# ---- 步骤4: 组件命名对齐 + 设置执行权限 ----
log "步骤4/5: 组件命名对齐并设置执行权限"

# 部分 Trae 版本解压产物名与客户端期望的 SERVER_APP_NAME 不一致，需对齐
if [ ! -f "$INSTALL_DIR/bin/$SERVER_APP_NAME" ]; then
    for candidate in trae-cn-server trae-server code-server; do
        if [ -f "$INSTALL_DIR/bin/$candidate" ]; then
            mv "$INSTALL_DIR/bin/$candidate" "$INSTALL_DIR/bin/$SERVER_APP_NAME"
            log "  ✓ 组件重命名: $candidate → $SERVER_APP_NAME"
            break
        fi
    done
fi

if [ -f "$INSTALL_DIR/node" ]; then
    chmod +x "$INSTALL_DIR/node"
    log "  ✓ node 可执行权限已设置"
else
    log "  ⚠ 未找到 node 文件，可能是服务端包结构变化"
fi

if [ -f "$INSTALL_DIR/bin/$SERVER_APP_NAME" ]; then
    chmod +x "$INSTALL_DIR/bin/$SERVER_APP_NAME"
    log "  ✓ $SERVER_APP_NAME 可执行权限已设置"
else
    echo "[remote][ERROR] 未找到 bin/$SERVER_APP_NAME，解压可能不完整或组件名不匹配" >&2
    echo "[remote][ERROR] 请检查远端解压目录: ls -la $INSTALL_DIR/bin/" >&2
    echo "[remote][ERROR] 若组件名不同，请用 -ServerAppName 参数指定正确名称" >&2
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
log "========== Trae 服务端安装成功 =========="
echo "[remote] INSTALL_OK"
'@

# 替换占位符（PowerShell 变量替换，避免 here-string 中 $ 转义问题）
# 将 server data dir 的前导 ~ 转换为 bash 可展开的 $HOME，避免赋值语句中 ~ 不被展开
$serverDataDirBash = $ServerDataDir
if ($serverDataDirBash -like '~*') {
    $serverDataDirBash = '$HOME' + $serverDataDirBash.Substring(1)
}
$bashInstallScript = $bashInstallScript.Replace("__COMMIT__", $CommitId)
$bashInstallScript = $bashInstallScript.Replace("__ARCHIVE__", $remoteArchivePath)
$bashInstallScript = $bashInstallScript.Replace("__SERVER_DATA_DIR__", $serverDataDirBash)
$bashInstallScript = $bashInstallScript.Replace("__BIN_DIR__", $binDirName)
$bashInstallScript = $bashInstallScript.Replace("__SERVER_APP_NAME__", $ServerAppName)
$bashInstallScript = $bashInstallScript.Replace("__TMP_DIR__", $remoteTmpDir)

$localBashScript = Join-Path $tempDir "install-trae-server.sh"
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
        2 { Write-Host "  → 退出码2：磁盘空间不足，请清理后重试" -ForegroundColor White; Write-Host "    诊断命令: ssh -p $Port $sshTarget 'df -h ~ && du -sh ${ServerDataDir}/ 2>/dev/null'" -ForegroundColor Gray }
        3 { Write-Host "  → 退出码3：必要命令缺失，请安装 tar/gzip/coreutils" -ForegroundColor White }
        4 { Write-Host "  → 退出码4：压缩包不存在，SCP上传可能失败" -ForegroundColor White; Write-Host "    诊断命令: ssh -p $Port $sshTarget ls -la $remoteArchivePath" -ForegroundColor Gray }
        5 { Write-Host "  → 退出码5：压缩包损坏（gzip校验失败），请使用 -Force 重新运行" -ForegroundColor White }
        6 { Write-Host "  → 退出码6：tar解压失败，可能是磁盘满或包格式错误" -ForegroundColor White }
        7 { Write-Host "  → 退出码7：解压结构异常，可能是版本架构不匹配" -ForegroundColor White; Write-Host "    请确认 -Arch 参数（x64/arm64/armhf）与远端架构一致" -ForegroundColor Gray }
        128 { Write-Host "  → 脚本被信号中断（可能是SSH连接断开）" -ForegroundColor White }
        default {
            Write-Host "  根据日志排查：" -ForegroundColor Yellow
            if ($installResult -match "磁盘空间不足") {
                Write-Host "  → 磁盘空间不足，请清理后重试：ssh -p $Port $sshTarget 'df -h ~ && du -sh ${ServerDataDir}/ 2>/dev/null'" -ForegroundColor White
            }
            if ($installResult -match "压缩包损坏" -or $installResult -match "gzip") {
                Write-Host "  → 压缩包损坏，请使用 -Force 参数重新运行（会重新下载和上传）" -ForegroundColor White
            }
            if ($installResult -match "trae-cn-server|trae-server" -and $installResult -match "不存在") {
                Write-Host "  → 解压结构异常，可能是版本架构不匹配，请确认 -Arch 参数正确" -ForegroundColor White
            }
            if ($installResult -notmatch "磁盘|压缩包|trae-cn-server|trae-server|tar|command|解压失败") {
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
$verifyResult = (& ssh @sshCommonArgs $sshTarget "test -x ${remoteInstallDir}/bin/${ServerAppName} && echo VERIFY_OK || echo VERIFY_FAIL" 2>&1) | Out-String
$verifyElapsed = (Get-Date) - $verifyStart

if ($verifyResult -notmatch "VERIFY_OK") {
    Write-Fail "安装验证失败：${ServerAppName} 不存在或不可执行。"
    Write-Host "  请手动检查: ssh -p $Port $sshTarget ls -la ${remoteInstallDir}/bin/" -ForegroundColor Yellow
    exit 1
}

# 额外验证：获取版本信息
$serverInfo = (& ssh @sshCommonArgs $sshTarget "ls -la ${remoteInstallDir}/bin/${ServerAppName} && du -sh ${remoteInstallDir}/" 2>&1) | Out-String
Write-Host "  ✓ ${ServerAppName} 存在且可执行（验证耗时 $([math]::Round($verifyElapsed.TotalMilliseconds))ms）" -ForegroundColor Green
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
Write-Host "  Trae 服务端部署成功！" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host "  Commit ID    : $CommitId" -ForegroundColor White
Write-Host "  组件名       : $ServerAppName" -ForegroundColor White
Write-Host "  架构         : $Arch" -ForegroundColor White
Write-Host "  目标         : $sshTarget" -ForegroundColor White
Write-Host "  安装路径     : ${ServerDataDir}/bin/${binDirName}/" -ForegroundColor White
Write-Host ""
Write-Host "  下一步操作：" -ForegroundColor Yellow
Write-Host "  1. 回到 Trae (trae-cn)" -ForegroundColor White
Write-Host "  2. 关闭当前卡住的 Remote-SSH 连接窗口" -ForegroundColor White
Write-Host "  3. 重新连接 $Server" -ForegroundColor White
Write-Host "  4. Trae 将检测到服务端已安装，直接启动" -ForegroundColor White
Write-Host "============================================" -ForegroundColor Green
