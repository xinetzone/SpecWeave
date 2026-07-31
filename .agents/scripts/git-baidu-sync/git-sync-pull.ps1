[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$RepoPath = '.',

    [Parameter()]
    [string]$SyncRoot = '',

    [Parameter()]
    [string]$RemoteName = '',

    [switch]$Force
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
Write-ColorMessage '  Git 网盘同步 - Pull 工具' -Color $ColorHeader
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

    Write-ColorMessage "SyncRoot: $SyncRoot" -Color $ColorInfo
    Write-ColorMessage "仓库名: $repoName" -Color $ColorInfo
    Write-ColorMessage "裸仓库: $bareRepoPath" -Color $ColorInfo
    Write-ColorMessage "Remote: $RemoteName -> $remoteUrl" -Color $ColorInfo
    Write-Host ''

    Write-Step -Number 1 -Title '锁状态检查（只读检测，不获取写锁）'
    $lockfilePath = Lock-GetLockfilePath -RepoName $repoName
    $lockHeld = $false
    $holderInfo = $null
    if (Test-Path $lockfilePath -PathType Leaf) {
        $lockHeld = $true
        $holderDevice = Lock-ReadJsonField -FilePath $lockfilePath -Field 'device_id'
        $holderHost = Lock-ReadJsonField -FilePath $lockfilePath -Field 'hostname'
        $holderPid = Lock-ReadJsonField -FilePath $lockfilePath -Field 'pid'
        $holderOp = Lock-ReadJsonField -FilePath $lockfilePath -Field 'operation'
        $holderTs = Lock-ReadJsonField -FilePath $lockfilePath -Field 'acquired_at'

        $isTimeout = Lock-IsTimeoutLock -Lockfile $lockfilePath
        Lock-EnsureDeviceId
        $myDeviceId = $script:LockUtilsDeviceId
        $isSelf = ($holderDevice -eq $myDeviceId)

        Write-ColorMessage '检测到活跃锁：' -Color $ColorWarning -Prefix 'WARN'
        Write-Host "  device_id: $holderDevice" -ForegroundColor $ColorWarning
        Write-Host "  hostname:  $holderHost" -ForegroundColor $ColorWarning
        Write-Host "  pid:       $holderPid" -ForegroundColor $ColorWarning
        Write-Host "  operation: $holderOp" -ForegroundColor $ColorWarning
        Write-Host "  since:     $holderTs" -ForegroundColor $ColorWarning

        if ($isTimeout) {
            Write-ColorMessage '锁已超时，可安全继续' -Color $ColorWarning -Prefix 'WARN'
            $lockHeld = $false
        }
        elseif (-not $Force) {
            if ($isSelf) {
                Write-ColorMessage '这是本设备持有的锁' -Color $ColorInfo
            }
            else {
                Write-Host ''
                Write-ColorMessage '其他设备正在 push，此时 pull 可能得到不完整状态！' -Color $ColorError -Prefix 'WARN'
                $answer = Read-Host '是否继续 pull？(y/N)'
                if ($answer -ne 'y' -and $answer -ne 'Y') {
                    Write-ColorMessage '用户取消 pull' -Color $ColorWarning -Prefix 'ABORT'
                    exit 0
                }
            }
        }
        else {
            Write-ColorMessage '-Force 已指定，忽略锁警告继续 pull' -Color $ColorWarning -Prefix 'WARN'
        }
    }
    else {
        Write-ColorMessage '无活跃写锁，安全' -Color $ColorSuccess -Prefix 'OK'
    }

    Write-Step -Number 2 -Title '冲突副本检测'
    if (-not (Test-Path $bareRepoPath -PathType Container)) {
        Write-ColorMessage "裸仓库不存在: $bareRepoPath" -Color $ColorError -Prefix 'ERR'
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

    Write-Step -Number 3 -Title '半同步状态检测'
    $tempFiles = Test-TempFiles -BareRepoPath $bareRepoPath
    if ($tempFiles.Count -gt 0) {
        Write-ColorMessage "检测到 $($tempFiles.Count) 个临时文件（网盘可能正在同步）：" -Color $ColorWarning -Prefix 'WARN'
        $tempFiles | Select-Object -First 10 | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor $ColorWarning }
        if (-not $Force) {
            $answer = Read-Host '临时文件可能表示同步未完成，是否继续？(y/N)'
            if ($answer -ne 'y' -and $answer -ne 'Y') {
                Write-ColorMessage '用户取消 pull' -Color $ColorWarning -Prefix 'ABORT'
                exit 0
            }
        }
    }
    else {
        Write-ColorMessage '未检测到临时文件' -Color $ColorSuccess -Prefix 'OK'
    }

    Write-Step -Number 4 -Title '执行 git fetch'
    $fetchResult = Invoke-GitCommand -Arguments @('fetch', $RemoteName)
    if (-not $fetchResult.Success) {
        Write-ColorMessage 'git fetch 失败：' -Color $ColorError -Prefix 'ERR'
        $fetchResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        exit 1
    }
    $fetchResult.Output | ForEach-Object { if ($_ -match '\S') { Write-Host $_ -ForegroundColor $ColorInfo } }
    Write-ColorMessage 'Fetch 完成' -Color $ColorSuccess -Prefix 'OK'

    Write-Step -Number 5 -Title '对比本地与远程差异'
    $currentBranch = (Invoke-GitCommand -Arguments @('rev-parse', '--abbrev-ref', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1
    if (-not $currentBranch) {
        Write-ColorMessage '无法确定当前分支，detached HEAD 状态？' -Color $ColorError -Prefix 'ERR'
        exit 1
    }
    $remoteBranch = "$RemoteName/$currentBranch"

    $behindCount = 0
    $aheadCount = 0

    try {
        $behindLog = Invoke-GitCommand -Arguments @('log', "HEAD..$remoteBranch", '--oneline')
        if ($behindLog.Success) {
            $behindCount = @($behindLog.Output | Where-Object { $_ -match '\S' }).Count
        }
    }
    catch { $behindCount = 0 }

    try {
        $aheadLog = Invoke-GitCommand -Arguments @('log', "$remoteBranch..HEAD", '--oneline')
        if ($aheadLog.Success) {
            $aheadCount = @($aheadLog.Output | Where-Object { $_ -match '\S' }).Count
        }
    }
    catch { $aheadCount = 0 }

    Write-ColorMessage "当前分支: $currentBranch" -Color $ColorInfo
    Write-ColorMessage "远程分支: $remoteBranch" -Color $ColorInfo
    Write-ColorMessage "远程领先: $behindCount commits" -Color $ColorInfo
    Write-ColorMessage "本地领先: $aheadCount commits" -Color $ColorInfo

    $pulledCount = 0
    $filesChanged = 0
    $pullStatus = 'UPTODATE'
    $errorMsg = ''

    if ($behindCount -gt 0 -and $aheadCount -gt 0) {
        Write-Step -Number 6 -Title '非快进状态（双方都有新提交）'
        Write-ColorMessage '=========================================' -Color $ColorError
        Write-ColorMessage '  错误：非快进更新（non-fast-forward）' -Color $ColorError
        Write-ColorMessage '=========================================' -Color $ColorError
        Write-Host ''
        Write-ColorMessage "远程有 $behindCount 个新提交，本地有 $aheadCount 个新提交。" -Color $ColorError
        Write-Host ''
        Write-ColorMessage '处理方案：' -Color $ColorHeader
        Write-ColorMessage '  推荐：git rebase（保持线性历史）' -Color $ColorInfo
        Write-Host "    git fetch $RemoteName" -ForegroundColor White
        Write-Host "    git rebase $remoteBranch" -ForegroundColor White
        Write-Host "    # 解决冲突后 git add <files>; git rebase --continue" -ForegroundColor Gray
        Write-Host "    # 然后执行 git-sync-push" -ForegroundColor Gray
        Write-Host ''
        Write-ColorMessage '  备选：git merge（保留合并历史）' -Color $ColorInfo
        Write-Host "    git fetch $RemoteName" -ForegroundColor White
        Write-Host "    git merge $remoteBranch" -ForegroundColor White
        Write-Host "    # 解决冲突后 git commit" -ForegroundColor Gray
        Write-Host ''
        $pullStatus = 'NONFF'
        $errorMsg = "non-fast-forward: behind=$behindCount,ahead=$aheadCount"
    }
    elseif ($behindCount -gt 0) {
        Write-Step -Number 6 -Title "执行快进 pull ($behindCount commits)"
        $localHeadBefore = (Invoke-GitCommand -Arguments @('rev-parse', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1

        $pullResult = Invoke-GitCommand -Arguments @('pull', '--ff-only', $RemoteName)
        if (-not $pullResult.Success) {
            Write-ColorMessage 'git pull --ff-only 失败：' -Color $ColorError -Prefix 'ERR'
            $pullResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
            $pullStatus = 'FAIL'
            $errorMsg = 'pull_failed'
        }
        else {
            $pullResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
            $localHeadAfter = (Invoke-GitCommand -Arguments @('rev-parse', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1

            try {
                $diffStat = Invoke-GitCommand -Arguments @('diff', '--stat', $localHeadBefore, $localHeadAfter)
                if ($diffStat.Success) {
                    $diffLines = @($diffStat.Output | Where-Object { $_ -match '\S' })
                    if ($diffLines.Count -gt 0) {
                        $summaryLine = $diffLines[-1]
                        if ($summaryLine -match '(\d+) files? changed') {
                            $filesChanged = [int]$Matches[1]
                        }
                    }
                }
            }
            catch {}
            $pulledCount = $behindCount
            $pullStatus = 'SUCCESS'
            Write-ColorMessage "Pull 完成，更新了 $filesChanged 个文件" -Color $ColorSuccess -Prefix 'OK'
        }
    }
    elseif ($aheadCount -gt 0) {
        Write-Step -Number 6 -Title '本地有领先提交'
        Write-ColorMessage "本地有 $aheadCount 个提交尚未 push，建议先执行 git-sync-push 推送" -Color $ColorWarning -Prefix 'HINT'
        $pullStatus = 'AHEAD'
    }
    else {
        Write-Step -Number 6 -Title '已是最新状态'
        Write-ColorMessage '本地与远程同步，无需 pull' -Color $ColorSuccess -Prefix 'OK'
        $pullStatus = 'UPTODATE'
    }

    Write-Step -Number 7 -Title '记录日志'
    $extraParts = @()
    if ($pullStatus -eq 'SUCCESS') {
        $extraParts += "commits=$pulledCount"
        $extraParts += "files_changed=$filesChanged"
        $logResult = 'SUCCESS'
    }
    elseif ($pullStatus -eq 'NONFF') {
        $extraParts += $errorMsg
        $logResult = 'FAILURE'
    }
    elseif ($pullStatus -eq 'FAIL') {
        $extraParts += $errorMsg
        $logResult = 'FAILURE'
    }
    else {
        $extraParts += "behind=$behindCount,ahead=$aheadCount"
        $logResult = 'SUCCESS'
    }
    $extraInfo = $extraParts -join ','
    Write-SyncLog -SyncRoot $SyncRoot -Operation 'PULL' -RepoName $repoName -Result $logResult -ExtraInfo $extraInfo
    Write-ColorMessage '日志已写入' -Color $ColorSuccess -Prefix 'OK'

    Write-Host ''
    if ($pullStatus -eq 'SUCCESS' -or $pullStatus -eq 'UPTODATE' -or $pullStatus -eq 'AHEAD') {
        Write-ColorMessage '=========================================' -Color $ColorSuccess
        Write-ColorMessage '  Pull 完成！' -Color $ColorSuccess
        Write-ColorMessage '=========================================' -Color $ColorSuccess
    }
    else {
        Write-ColorMessage '=========================================' -Color $ColorError
        Write-ColorMessage '  Pull 需要手动干预' -Color $ColorError
        Write-ColorMessage '=========================================' -Color $ColorError
    }
    Write-Host ''
    Write-ColorMessage "仓库: $repoName" -Color $(if ($pullStatus -eq 'NONFF' -or $pullStatus -eq 'FAIL') { $ColorError } else { $ColorSuccess })
    Write-ColorMessage "状态: $pullStatus" -Color $(if ($pullStatus -eq 'NONFF' -or $pullStatus -eq 'FAIL') { $ColorError } else { $ColorSuccess })
    if ($pullStatus -eq 'SUCCESS') {
        Write-ColorMessage "拉取 commits: $pulledCount" -Color $ColorSuccess
        Write-ColorMessage "更新文件: $filesChanged" -Color $ColorSuccess
    }
    elseif ($pullStatus -eq 'AHEAD') {
        Write-ColorMessage "本地领先: $aheadCount commits（建议 push）" -Color $ColorWarning
    }
    elseif ($pullStatus -eq 'NONFF') {
        Write-ColorMessage "远程领先: $behindCount, 本地领先: $aheadCount" -Color $ColorError
    }
    Write-Host ''

    if ($pullStatus -eq 'NONFF' -or $pullStatus -eq 'FAIL') {
        exit 1
    }
}
finally {
    Pop-Location
}
