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

    [switch]$Force,

    [Parameter()]
    [int]$Timeout = 600,

    [Parameter()]
    [int]$PollInterval = 2,

    [Parameter()]
    [int]$StableCount = 5
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

$ColorSuccess = 'Green'
$ColorStep = 'Cyan'
$ColorWarning = 'Yellow'
$ColorError = 'Red'
$ColorInfo = 'Gray'
$ColorHeader = 'Magenta'

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PullScript = Join-Path $ScriptDir 'git-sync-pull.ps1'
$PushScript = Join-Path $ScriptDir 'git-sync-push.ps1'

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

function Resolve-FullPath {
    param([string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
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

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-ColorMessage '  Git 网盘同步 - 一体化 Sync 工具' -Color $ColorHeader
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

$pullArgs = @('-RepoPath', $RepoPath)
if ($SyncRoot) { $pullArgs += @('-SyncRoot', $SyncRoot) }
if ($RemoteName) { $pullArgs += @('-RemoteName', $RemoteName) }
if ($Force) { $pullArgs += '-Force' }

$syncRootResolved = $null
$remoteNameResolved = $null
Push-Location $RepoPath
try {
    if (-not $RemoteName) {
        try { $RemoteName = (& git config baidu-sync.remote 2>$null) } catch {}
        if (-not $RemoteName) { $RemoteName = 'baidu' }
    }
    $remoteNameResolved = $RemoteName

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
    }
    if ($SyncRoot) {
        $syncRootResolved = Resolve-FullPath $SyncRoot
    }
}
finally {
    Pop-Location
}

if (-not $syncRootResolved) {
    Write-ColorMessage '无法自动推断 SyncRoot，请使用 -SyncRoot 参数指定' -Color $ColorError -Prefix 'ERR'
    exit 1
}

Write-ColorMessage "本地仓库: $RepoPath" -Color $ColorInfo
Write-ColorMessage "SyncRoot: $syncRootResolved" -Color $ColorInfo
Write-ColorMessage "Remote: $remoteNameResolved" -Color $ColorInfo
Write-Host ''

$repoName = Split-Path -Path $RepoPath -Leaf
if ($remoteUrl) {
    if ($remoteUrl -match '/([^/]+)\.git/?$' -or $remoteUrl -match '\\([^\\]+)\.git\\?$') {
        $repoName = $Matches[1]
    }
}

$syncErrors = @()
$pullStatus = 'UNKNOWN'
$pulledCommits = 0
$pushStatus = 'SKIPPED'
$pushedCommits = 0

Write-ColorMessage '>>> 阶段 1/2: 执行 Pull' -Color $ColorStep
Write-Host ''
$pullExitCode = 0
try {
    & $PullScript @pullArgs
    $pullExitCode = $LASTEXITCODE
}
catch {
    $pullExitCode = 1
    $syncErrors += "Pull 异常: $_"
}

if ($pullExitCode -eq 0) {
    $pullStatus = 'SUCCESS'
}
else {
    $pullStatus = "FAILED(exit=$pullExitCode)"
}

Push-Location $RepoPath
try {
    $currentBranch = (Invoke-GitCommand -Arguments @('rev-parse', '--abbrev-ref', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1
    $remoteBranch = "$remoteNameResolved/$currentBranch"

    $behindCount = 0
    $aheadCount = 0
    try {
        $behindLog = Invoke-GitCommand -Arguments @('log', "HEAD..$remoteBranch", '--oneline')
        if ($behindLog.Success) { $behindCount = @($behindLog.Output | Where-Object { $_ -match '\S' }).Count }
    }
    catch {}
    try {
        $aheadLog = Invoke-GitCommand -Arguments @('log', "$remoteBranch..HEAD", '--oneline')
        if ($aheadLog.Success) { $aheadCount = @($aheadLog.Output | Where-Object { $_ -match '\S' }).Count }
    }
    catch {}

    $localHead = (Invoke-GitCommand -Arguments @('rev-parse', '--short', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1
    $remoteHead = 'N/A'
    try {
        $remoteHead = (Invoke-GitCommand -Arguments @('rev-parse', '--short', $remoteBranch)).Output | Where-Object { $_ } | Select-Object -First 1
    }
    catch {}
}
finally {
    Pop-Location
}

$pushNeeded = $false
if ($aheadCount -gt 0 -and $pullExitCode -eq 0) {
    Write-Host ''
    Write-ColorMessage "检测到 $aheadCount 个本地提交待推送" -Color $ColorInfo
    $pushNeeded = $true
}
elseif ($aheadCount -gt 0 -and $pullExitCode -ne 0) {
    Write-Host ''
    Write-ColorMessage "Pull 失败，跳过 Push（请先解决 pull 问题）" -Color $ColorWarning -Prefix 'WARN'
    $pushStatus = 'SKIPPED (pull failed)'
}

if ($pushNeeded) {
    Write-Host ''
    Write-ColorMessage '>>> 阶段 2/2: 执行 Push' -Color $ColorStep
    Write-Host ''

    $pushArgs = @('-RepoPath', $RepoPath, '-SyncRoot', $syncRootResolved, '-RemoteName', $remoteNameResolved)
    if ($NoWait) { $pushArgs += '-NoWait' }
    if ($NoBackup) { $pushArgs += '-NoBackup' }
    $pushArgs += @('-Timeout', $Timeout, '-PollInterval', $PollInterval, '-StableCount', $StableCount)

    $pushExitCode = 0
    try {
        & $PushScript @pushArgs
        $pushExitCode = $LASTEXITCODE
    }
    catch {
        $pushExitCode = 1
        $syncErrors += "Push 异常: $_"
    }

    if ($pushExitCode -eq 0) {
        $pushStatus = 'SUCCESS'
        $pushedCommits = $aheadCount
    }
    else {
        $pushStatus = "FAILED(exit=$pushExitCode)"
    }
}
else {
    Write-Host ''
    Write-ColorMessage '>>> 阶段 2/2: 无需 Push' -Color $ColorStep
}

Push-Location $RepoPath
try {
    $finalAhead = 0
    $finalBehind = 0
    try {
        $currentBranch2 = (Invoke-GitCommand -Arguments @('rev-parse', '--abbrev-ref', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1
        $remoteBranch2 = "$remoteNameResolved/$currentBranch2"
        $aheadLog2 = Invoke-GitCommand -Arguments @('log', "$remoteBranch2..HEAD", '--oneline')
        if ($aheadLog2.Success) { $finalAhead = @($aheadLog2.Output | Where-Object { $_ -match '\S' }).Count }
        $behindLog2 = Invoke-GitCommand -Arguments @('log', "HEAD..$remoteBranch2", '--oneline')
        if ($behindLog2.Success) { $finalBehind = @($behindLog2.Output | Where-Object { $_ -match '\S' }).Count }
    }
    catch {}

    $finalLocalHead = (Invoke-GitCommand -Arguments @('rev-parse', '--short', 'HEAD')).Output | Where-Object { $_ } | Select-Object -First 1
    $finalRemoteHead = 'N/A'
    try {
        $finalRemoteHead = (Invoke-GitCommand -Arguments @('rev-parse', '--short', $remoteBranch2)).Output | Where-Object { $_ } | Select-Object -First 1
    }
    catch {}
}
finally {
    Pop-Location
}

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-ColorMessage '  同步摘要' -Color $ColorHeader
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-Host ''
Write-ColorMessage "仓库:      $repoName" -Color $ColorInfo
Write-ColorMessage "本地 HEAD: $finalLocalHead" -Color $ColorInfo
Write-ColorMessage "远程 HEAD: $finalRemoteHead" -Color $ColorInfo
Write-Host ''
Write-Host -NoNewline "Pull:      "; if ($pullStatus -eq 'SUCCESS') { Write-Host $pullStatus -ForegroundColor $ColorSuccess } else { Write-Host $pullStatus -ForegroundColor $ColorError }
Write-Host -NoNewline "Push:      "; if ($pushStatus -eq 'SUCCESS' -or $pushStatus -eq 'SKIPPED') { Write-Host $pushStatus -ForegroundColor $(if ($pushStatus -eq 'SUCCESS') { $ColorSuccess } else { $ColorInfo }) } else { Write-Host $pushStatus -ForegroundColor $ColorError }
Write-Host ''
Write-ColorMessage "领先: $finalAhead commits | 落后: $finalBehind commits" -Color $ColorInfo
Write-Host ''

if ($syncErrors.Count -gt 0) {
    Write-ColorMessage '同步过程中遇到以下问题：' -Color $ColorError -Prefix 'ERR'
    foreach ($err in $syncErrors) {
        Write-Host "  - $err" -ForegroundColor $ColorError
    }
    Write-Host ''
    Write-ColorMessage '下一步建议：' -Color $ColorHeader
    Write-ColorMessage '1. 检查错误信息，解决冲突或网络问题' -Color $ColorInfo
    Write-ColorMessage '2. 非快进情况参考 05-daily-sync-workflow.md 第7节处理' -Color $ColorInfo
    Write-ColorMessage '3. 修复后重新执行 git-sync' -Color $ColorInfo
    Write-Host ''
    exit 1
}

if ($finalBehind -gt 0 -or $finalAhead -gt 0) {
    if ($finalBehind -gt 0) {
        Write-ColorMessage "注意：远程仍领先 $finalBehind 个提交（pull可能未完成）" -Color $ColorWarning -Prefix 'WARN'
    }
    if ($finalAhead -gt 0) {
        Write-ColorMessage "注意：本地仍领先 $finalAhead 个提交（push可能未完成）" -Color $ColorWarning -Prefix 'WARN'
    }
    Write-Host ''
}
else {
    Write-ColorMessage '同步完成！本地与远程完全一致。' -Color $ColorSuccess
    Write-Host ''
}
