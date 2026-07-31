[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$RepoPath = '.',

    [Parameter()]
    [string]$SyncRoot = '',

    [Parameter()]
    [string]$RemoteName = '',

    [switch]$NoWait,

    [switch]$NoBackup,

    [Parameter()]
    [int]$Timeout = 600,

    [Parameter()]
    [int]$PollInterval = 2,

    [Parameter()]
    [int]$StableCount = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$ColorSuccess = 'Green'
$ColorStep = 'Cyan'
$ColorWarning = 'Yellow'
$ColorError = 'Red'
$ColorInfo = 'Gray'
$ColorHeader = 'Magenta'
$ColorPrompt = 'White'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. (Join-Path $ScriptDir 'lock-utils.ps1')

function Write-ColorMessage {
    param(
        [string]$Message,
        [string]$Color = 'White',
        [string]$Prefix = ''
    )
    if ($Prefix) {
        Write-Host "[$Prefix] " -NoNewline -ForegroundColor $Color
    }
    Write-Host $Message -ForegroundColor $Color
}

function Write-Step {
    param(
        [int]$Number,
        [string]$Title
    )
    Write-Host ''
    Write-ColorMessage "=== 步骤 ${Number}: ${Title} ===" -Color $ColorHeader
}

function Invoke-GitCommand {
    param(
        [string[]]$Arguments,
        [string]$WorkingDirectory = '.'
    )
    $output = & git @Arguments 2>&1
    $exitCode = $LASTEXITCODE
    return @{
        Output = $output
        ExitCode = $exitCode
        Success = ($exitCode -eq 0)
    }
}

function Resolve-FullPath {
    param([string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

function Convert-ToGitPath {
    param([string]$Path)
    return $Path -replace '\\', '/'
}

function Get-RepoName {
    param(
        [string]$RepoPath,
        [string]$RemoteName,
        [string]$RemoteUrl
    )
    if ($RemoteUrl) {
        if ($RemoteUrl -match '/([^/]+)\.git/?$') {
            return $Matches[1]
        }
        if ($RemoteUrl -match '\\([^\\]+)\.git\\?$') {
            return $Matches[1]
        }
    }
    return Split-Path -Path $RepoPath -Leaf
}

function Test-ConflictCopies {
    param([string]$BareRepoPath)
    $conflictPatterns = @(
        '* (*)*',
        '* (冲突版本)*',
        '* (来自*)*'
    )
    $conflicts = @()
    foreach ($pattern in $conflictPatterns) {
        $found = Get-ChildItem -Path $BareRepoPath -Recurse -Filter $pattern -ErrorAction SilentlyContinue
        if ($found) {
            $conflicts += $found
        }
    }
    return $conflicts
}

function Test-TempFiles {
    param([string]$BareRepoPath)
    $tempPatterns = @('*.tmp', '*.pack-tmp', '*.lock', '*.part', '*.temp', '*.downloading')
    $temps = @()
    foreach ($pattern in $tempPatterns) {
        $found = Get-ChildItem -Path $BareRepoPath -Recurse -Filter $pattern -ErrorAction SilentlyContinue |
            Where-Object { $_.Name -ne 'HEAD.lock' -and $_.Name -notmatch '^pack-.+\.lock$' }
        if ($found) {
            $temps += $found
        }
    }
    return $temps
}

function Get-BareRepoStats {
    param([string]$BareRepoPath)
    if (-not (Test-Path $BareRepoPath -PathType Container)) {
        return $null
    }
    $allFiles = Get-ChildItem -Path $BareRepoPath -Recurse -File -ErrorAction SilentlyContinue
    $totalSize = 0
    $latestMtime = [DateTime]::MinValue
    $packCount = 0
    foreach ($f in $allFiles) {
        $totalSize += $f.Length
        if ($f.LastWriteTime -gt $latestMtime) {
            $latestMtime = $f.LastWriteTime
        }
        if ($f.DirectoryName -match 'objects[\\/]pack$' -and $f.Extension -eq '.pack') {
            $packCount++
        }
    }
    return @{
        TotalSize = $totalSize
        FileCount = $allFiles.Count
        LatestMtime = $latestMtime
        PackCount = $packCount
    }
}

function Wait-ForSync {
    param(
        [string]$BareRepoPath,
        [int]$TimeoutSec,
        [int]$PollSec,
        [int]$StableTimes
    )

    Write-ColorMessage "等待网盘同步完成（超时 ${TimeoutSec}s，轮询 ${PollSec}s，稳定 ${StableTimes}次）..." -Color $ColorInfo

    $startTime = Get-Date
    $stableHits = 0
    $lastStats = $null
    $spinner = @('|', '/', '-', '\')
    $spinnerIdx = 0

    while ($true) {
        $elapsed = (Get-Date) - $startTime
        if ($elapsed.TotalSeconds -ge $TimeoutSec) {
            Write-Host ''
            Write-ColorMessage "等待超时（${TimeoutSec}s），push 已成功但网盘可能未完全同步" -Color $ColorWarning -Prefix 'WARN'
            Write-ColorMessage '请手动确认网盘同步状态后再在其他设备操作' -Color $ColorWarning
            return @{ Success = $false; Timeout = $true; WaitSeconds = [int]$elapsed.TotalSeconds }
        }

        $tempFiles = Test-TempFiles -BareRepoPath $BareRepoPath
        if ($tempFiles) {
            $stableHits = 0
            Write-Host "`r[$($spinner[$spinnerIdx])] 等待中... 已等待 $([int]$elapsed.TotalSeconds)s, 检测到临时文件: $($tempFiles[0].Name)   " -NoNewline
        }
        else {
            $currentStats = Get-BareRepoStats -BareRepoPath $BareRepoPath
            if ($null -eq $currentStats) {
                Write-Host "`r[$($spinner[$spinnerIdx])] 等待中... 已等待 $([int]$elapsed.TotalSeconds)s, 裸仓库未就绪   " -NoNewline
                $stableHits = 0
            }
            else {
                $statsStr = "size=$($currentStats.TotalSize), files=$($currentStats.FileCount), packs=$($currentStats.PackCount)"
                if ($lastStats -and
                    $lastStats.TotalSize -eq $currentStats.TotalSize -and
                    $lastStats.FileCount -eq $currentStats.FileCount -and
                    $lastStats.PackCount -eq $currentStats.PackCount -and
                    ([math]::Abs(($currentStats.LatestMtime - $lastStats.LatestMtime).TotalSeconds) -lt $PollSec)) {
                    $stableHits++
                    Write-Host "`r[$($spinner[$spinnerIdx])] 等待中... 已等待 $([int]$elapsed.TotalSeconds)s, 稳定 $stableHits/$StableTimes 次 ($statsStr)   " -NoNewline
                    if ($stableHits -ge $StableTimes) {
                        Write-Host ''
                        Write-ColorMessage "网盘同步已稳定（连续 ${StableTimes} 次检测一致）" -Color $ColorSuccess -Prefix 'OK'
                        return @{ Success = $true; Timeout = $false; WaitSeconds = [int]$elapsed.TotalSeconds }
                    }
                }
                else {
                    $stableHits = 0
                    Write-Host "`r[$($spinner[$spinnerIdx])] 等待中... 已等待 $([int]$elapsed.TotalSeconds)s, 同步中 ($statsStr)   " -NoNewline
                }
                $lastStats = $currentStats
            }
        }

        $spinnerIdx = ($spinnerIdx + 1) % $spinner.Length
        Start-Sleep -Seconds $PollSec
    }
}

function Write-SyncLog {
    param(
        [string]$SyncRoot,
        [string]$Operation,
        [string]$RepoName,
        [string]$Result,
        [string]$ExtraInfo
    )
    $logsDir = Join-Path $SyncRoot 'logs'
    if (-not (Test-Path $logsDir -PathType Container)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }
    $dateStr = Get-Date -Format 'yyyyMMdd'
    $logFile = Join-Path $logsDir "sync-$dateStr.log"
    $timestamp = Lock-GetIso8601
    Lock-EnsureDeviceId
    $deviceId = $script:LockUtilsDeviceId
    $line = "$timestamp`t$deviceId`t$Operation`t$RepoName`t$Result`t$ExtraInfo"
    Add-Content -Path $logFile -Value $line -Encoding UTF8
}

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-ColorMessage '  Git 网盘同步 - Push 工具' -Color $ColorHeader
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-Host ''

$RepoPath = Resolve-FullPath $RepoPath

$isGitRepo = $false
try {
    $result = Invoke-GitCommand -Arguments @('rev-parse', '--is-inside-work-tree') -WorkingDirectory $RepoPath
    if ($result.Success -and $result.Output -match 'true') {
        $isGitRepo = $true
    }
}
catch {}
if (-not $isGitRepo) {
    Write-ColorMessage "不是有效的 Git 工作仓库: $RepoPath" -Color $ColorError -Prefix 'ERR'
    exit 1
}
Write-ColorMessage "本地仓库: $RepoPath" -Color $ColorInfo

Push-Location $RepoPath
try {
    if (-not $RemoteName) {
        try {
            $RemoteName = (& git config baidu-sync.remote 2>$null)
        }
        catch {}
        if (-not $RemoteName) {
            $RemoteName = 'baidu'
        }
    }

    $remoteUrl = $null
    try {
        $remoteResult = Invoke-GitCommand -Arguments @('remote', 'get-url', $RemoteName)
        if ($remoteResult.Success) {
            $remoteUrl = ($remoteResult.Output | Where-Object { $_ } | Select-Object -First 1)
        }
    }
    catch {}

    if (-not $SyncRoot) {
        if ($remoteUrl -and (Test-Path $remoteUrl -PathType Container)) {
            $bareGitDir = $remoteUrl
            $SyncRoot = Split-Path -Parent (Split-Path -Parent $bareGitDir)
        }
        else {
            Write-ColorMessage '无法自动推断 SyncRoot，请使用 -SyncRoot 参数指定' -Color $ColorError -Prefix 'ERR'
            exit 1
        }
    }
    $SyncRoot = Resolve-FullPath $SyncRoot

    if (-not (Lock-Init -SyncRoot $SyncRoot)) {
        Write-ColorMessage '锁系统初始化失败' -Color $ColorError -Prefix 'ERR'
        exit 1
    }

    $repoName = Get-RepoName -RepoPath $RepoPath -RemoteName $RemoteName -RemoteUrl $remoteUrl
    $bareRepoPath = Join-Path $SyncRoot "repos\$repoName.git"
    $backupDir = Join-Path $SyncRoot "backups\$repoName"

    Write-ColorMessage "SyncRoot: $SyncRoot" -Color $ColorInfo
    Write-ColorMessage "仓库名: $repoName" -Color $ColorInfo
    Write-ColorMessage "裸仓库: $bareRepoPath" -Color $ColorInfo
    Write-ColorMessage "Remote: $RemoteName -> $remoteUrl" -Color $ColorInfo
    Write-Host ''

    Write-Step -Number 1 -Title '检查工作区状态'
    $statusResult = Invoke-GitCommand -Arguments @('status', '--porcelain')
    if (-not $statusResult.Success) {
        Write-ColorMessage 'git status 执行失败' -Color $ColorError -Prefix 'ERR'
        $statusResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        exit 1
    }
    $dirtyFiles = @($statusResult.Output | Where-Object { $_ -match '\S' })
    if ($dirtyFiles.Count -gt 0) {
        Write-ColorMessage '工作区不干净，请先提交或 stash 所有更改：' -Color $ColorError -Prefix 'ERR'
        $dirtyFiles | ForEach-Object { Write-Host "  $_" -ForegroundColor $ColorError }
        exit 1
    }
    Write-ColorMessage '工作区干净' -Color $ColorSuccess -Prefix 'OK'

    Write-Step -Number 2 -Title '检查本地未推送提交'
    $aheadCount = 0
    try {
        $upstreamResult = Invoke-GitCommand -Arguments @('rev-parse', '--abbrev-ref', '--symbolic-full-name', '@{u}')
        if ($upstreamResult.Success) {
            $logResult = Invoke-GitCommand -Arguments @('log', '@{u}..HEAD', '--oneline')
            if ($logResult.Success) {
                $aheadCount = @($logResult.Output | Where-Object { $_ -match '\S' }).Count
            }
        }
    }
    catch {
        try {
            $branchResult = Invoke-GitCommand -Arguments @('rev-parse', '--abbrev-ref', 'HEAD')
            if ($branchResult.Success) {
                $branchName = ($branchResult.Output | Where-Object { $_ } | Select-Object -First 1)
                $remoteBranch = "$RemoteName/$branchName"
                $logResult = Invoke-GitCommand -Arguments @('log', "$remoteBranch..HEAD", '--oneline')
                if ($logResult.Success) {
                    $aheadCount = @($logResult.Output | Where-Object { $_ -match '\S' }).Count
                }
            }
        }
        catch {}
    }

    if ($aheadCount -eq 0) {
        Write-ColorMessage '本地没有未推送的提交，无需 push' -Color $ColorInfo -Prefix 'INFO'
        exit 0
    }
    Write-ColorMessage "本地有 $aheadCount 个提交待推送" -Color $ColorInfo

    Write-Step -Number 3 -Title '冲突副本检测'
    if (-not (Test-Path $bareRepoPath -PathType Container)) {
        Write-ColorMessage "裸仓库不存在: $bareRepoPath" -Color $ColorError -Prefix 'ERR'
        Write-ColorMessage '请先使用 register-repo.ps1 注册仓库' -Color $ColorWarning
        exit 1
    }
    $conflicts = Test-ConflictCopies -BareRepoPath $bareRepoPath
    if ($conflicts.Count -gt 0) {
        Write-ColorMessage "检测到 $($conflicts.Count) 个冲突副本文件：" -Color $ColorError -Prefix 'ERR'
        $conflicts | Select-Object -First 10 | ForEach-Object { Write-Host "  - $($_.FullName)" -ForegroundColor $ColorError }
        Write-ColorMessage '请手动清理冲突文件后重试' -Color $ColorWarning
        exit 1
    }
    Write-ColorMessage '未检测到冲突副本' -Color $ColorSuccess -Prefix 'OK'

    Write-Step -Number 4 -Title '获取写锁'
    if (-not (Lock-Acquire -RepoName $repoName -Operation 'push')) {
        Write-ColorMessage '获取锁失败，push 中止' -Color $ColorError -Prefix 'ERR'
        exit 1
    }
    $lockAcquired = $true

    try {
        Write-Step -Number 5 -Title '检查网盘裸仓库临时文件'
        $tempFiles = Test-TempFiles -BareRepoPath $bareRepoPath
        if ($tempFiles.Count -gt 0) {
            Write-ColorMessage "检测到 $($tempFiles.Count) 个临时文件（网盘可能正在同步）：" -Color $ColorError -Prefix 'ERR'
            $tempFiles | Select-Object -First 10 | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor $ColorError }
            Write-ColorMessage '请等待网盘同步完成后重试' -Color $ColorWarning
            exit 1
        }
        Write-ColorMessage '未检测到临时文件' -Color $ColorSuccess -Prefix 'OK'

        Write-Step -Number 6 -Title '推送所有分支'
        $pushAllResult = Invoke-GitCommand -Arguments @('push', $RemoteName, '--all')
        if (-not $pushAllResult.Success) {
            Write-ColorMessage '分支推送失败：' -Color $ColorError -Prefix 'ERR'
            $pushAllResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
            exit 1
        }
        $pushAllResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
        Write-ColorMessage '分支推送完成' -Color $ColorSuccess -Prefix 'OK'

        Write-Step -Number 7 -Title '推送所有标签'
        $pushTagsResult = Invoke-GitCommand -Arguments @('push', $RemoteName, '--tags')
        if (-not $pushTagsResult.Success) {
            Write-ColorMessage '标签推送失败：' -Color $ColorWarning -Prefix 'WARN'
            $pushTagsResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorWarning }
        }
        else {
            $pushTagsResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
            Write-ColorMessage '标签推送完成' -Color $ColorSuccess -Prefix 'OK'
        }

        $bundlePath = $null
        if (-not $NoBackup) {
            Write-Step -Number 8 -Title '创建 bundle 备份'
            if (-not (Test-Path $backupDir -PathType Container)) {
                New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
            }
            $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
            $bundlePath = Join-Path $backupDir "$timestamp.bundle"

            Write-ColorMessage "创建 bundle: $bundlePath" -Color $ColorInfo
            $bundleResult = Invoke-GitCommand -Arguments @('bundle', 'create', $bundlePath, '--all')
            if ($bundleResult.Success) {
                $verifyResult = Invoke-GitCommand -Arguments @('bundle', 'verify', $bundlePath)
                if ($verifyResult.Success) {
                    Write-ColorMessage 'Bundle 验证通过' -Color $ColorSuccess -Prefix 'OK'
                }
                else {
                    Write-ColorMessage 'Bundle 验证警告：' -Color $ColorWarning -Prefix 'WARN'
                    $verifyResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorWarning }
                }
            }
            else {
                Write-ColorMessage 'Bundle 创建失败：' -Color $ColorWarning -Prefix 'WARN'
                $bundleResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorWarning }
                $bundlePath = $null
            }
        }
        else {
            Write-ColorMessage '已跳过备份（-NoBackup）' -Color $ColorWarning -Prefix 'SKIP'
        }

        $waitResult = $null
        if (-not $NoWait) {
            Write-Step -Number 9 -Title '等待网盘同步'
            $waitResult = Wait-ForSync -BareRepoPath $bareRepoPath -TimeoutSec $Timeout -PollSec $PollInterval -StableTimes $StableCount
        }
        else {
            Write-ColorMessage '已跳过等待（-NoWait）' -Color $ColorWarning -Prefix 'SKIP'
            $waitResult = @{ Success = $true; Timeout = $false; WaitSeconds = 0 }
        }

        Write-Step -Number 10 -Title '记录日志'
        $extraParts = @("commits=$aheadCount")
        if ($waitResult) {
            $extraParts += "wait=$($waitResult.WaitSeconds)s"
            if ($waitResult.Timeout) {
                $extraParts += 'timeout=true'
            }
        }
        if ($bundlePath) {
            $extraParts += "backup=$(Split-Path $bundlePath -Leaf)"
        }
        $extraInfo = $extraParts -join ','
        $logResult = 'SUCCESS'
        if ($waitResult -and $waitResult.Timeout) {
            $logResult = 'WARNING'
        }
        Write-SyncLog -SyncRoot $SyncRoot -Operation 'PUSH' -RepoName $repoName -Result $logResult -ExtraInfo $extraInfo
        Write-ColorMessage '日志已写入' -Color $ColorSuccess -Prefix 'OK'
    }
    finally {
        if ($lockAcquired) {
            Lock-Release -RepoName $repoName | Out-Null
        }
    }

    Write-Host ''
    Write-ColorMessage '=========================================' -Color $ColorSuccess
    Write-ColorMessage '  Push 完成！' -Color $ColorSuccess
    Write-ColorMessage '=========================================' -Color $ColorSuccess
    Write-Host ''
    Write-ColorMessage "仓库: $repoName" -Color $ColorSuccess
    Write-ColorMessage "推送 commits: $aheadCount" -Color $ColorSuccess
    if ($waitResult) {
        Write-ColorMessage "同步等待: $($waitResult.WaitSeconds)s" -Color $ColorSuccess
    }
    if ($bundlePath) {
        $bundleSize = (Get-Item $bundlePath -ErrorAction SilentlyContinue).Length
        if ($bundleSize) {
            $bundleSizeMB = [math]::Round($bundleSize / 1MB, 2)
            Write-ColorMessage "备份: $bundlePath ($bundleSizeMB MB)" -Color $ColorSuccess
        }
        else {
            Write-ColorMessage "备份: $bundlePath" -Color $ColorSuccess
        }
    }
    if ($waitResult -and $waitResult.Timeout) {
        Write-Host ''
        Write-ColorMessage '注意：等待超时，请确认网盘同步状态后再在其他设备操作' -Color $ColorWarning -Prefix 'WARN'
    }
    Write-Host ''
}
finally {
    Pop-Location
}
