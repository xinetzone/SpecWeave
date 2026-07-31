# git-diag.ps1 - Git 百度网盘同步一键诊断脚本
# 收集诊断信息并生成结构化报告
# dot-source 作为库使用，或直接执行

[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$RepoPath = '.',

    [Parameter()]
    [string]$SyncRoot = '',

    [Parameter()]
    [string]$RemoteName = 'baidu',

    [Parameter()]
    [switch]$Full,

    [Parameter()]
    [switch]$Output,

    [Parameter()]
    [switch]$NoColor
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Continue'

$script:DiagVersion = '1.0.0'
$script:DiagColorEnabled = -not $NoColor
$script:DiagStartTime = Get-Date
$script:DiagErrors = 0
$script:DiagWarnings = 0
$script:DiagInfos = 0
$script:DiagOks = 0
$script:DiagLogLines = [System.Collections.ArrayList]::new()
$script:DiagSuggestions = [System.Collections.ArrayList]::new()

$script:DiagScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$script:DiagLockUtilsLoaded = $false
$script:DiagConflictsLoaded = $false

try {
    . (Join-Path $script:DiagScriptDir 'lock-utils.ps1')
    $script:DiagLockUtilsLoaded = $true
}
catch {
    Write-Warning "无法加载 lock-utils.ps1: $_"
}

try {
    . (Join-Path $script:DiagScriptDir 'check-conflicts.ps1')
    $script:DiagConflictsLoaded = $true
}
catch {
    Write-Warning "无法加载 check-conflicts.ps1: $_"
}

function Diag-Colorize {
    param(
        [string]$Text,
        [string]$Color = 'White'
    )
    if ($script:DiagColorEnabled) {
        Write-Host $Text -ForegroundColor $Color
    }
    else {
        Write-Host $Text
    }
    [void]$script:DiagLogLines.Add($Text)
}

function Diag-Write {
    param(
        [ValidateSet('OK', 'WARN', 'ERR', 'INFO')]
        [string]$Status,
        [string]$Name,
        [string]$Detail = ''
    )

    $prefixMap = @{
        'OK'   = @{ Text = '[OK]  '; Color = 'Green' }
        'WARN' = @{ Text = '[WARN]'; Color = 'Yellow' }
        'ERR'  = @{ Text = '[ERR] '; Color = 'Red' }
        'INFO' = @{ Text = '[INFO]'; Color = 'Cyan' }
    }

    $p = $prefixMap[$Status]
    Write-Host $p.Text -NoNewline -ForegroundColor $p.Color
    $detailStr = if ($Detail) { " - $Detail" } else { '' }
    Write-Host " $Name$detailStr"
    [void]$script:DiagLogLines.Add("$($p.Text) $Name$detailStr")

    switch ($Status) {
        'OK' { $script:DiagOks++ }
        'WARN' { $script:DiagWarnings++ }
        'ERR' { $script:DiagErrors++ }
        'INFO' { $script:DiagInfos++ }
    }
}

function Diag-Section {
    param([string]$Title)
    $line = "========================================"
    Diag-Colorize "`n$line" 'DarkCyan'
    Diag-Colorize "  $Title" 'DarkCyan'
    Diag-Colorize "$line" 'DarkCyan'
}

function Diag-Suggest {
    param([string]$Suggestion)
    [void]$script:DiagSuggestions.Add($Suggestion)
}

function Diag-InvokeGit {
    param(
        [string[]]$Arguments,
        [string]$WorkingDirectory = '.'
    )
    try {
        $output = & git @Arguments 2>&1
        $exitCode = $LASTEXITCODE
        return @{
            Output = $output
            ExitCode = $exitCode
            Success = ($exitCode -eq 0)
        }
    }
    catch {
        return @{
            Output = @()
            ExitCode = -1
            Success = $false
            Error = $_
        }
    }
}

function Diag-ResolveFullPath {
    param([string]$Path)
    try {
        if ([System.IO.Path]::IsPathRooted($Path)) {
            return [System.IO.Path]::GetFullPath($Path)
        }
        return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
    }
    catch {
        return $Path
    }
}

function Diag-DetectOS {
    if ($IsWindows) { return 'win' }
    if ($IsMacOS) { return 'macos' }
    if ($IsLinux) { return 'linux' }
    if ($env:OS -eq 'Windows_NT') { return 'win' }
    return 'unknown'
}

function Diag-GetRepoName {
    param(
        [string]$RepoPath,
        [string]$RemoteUrl
    )
    if ($RemoteUrl) {
        if ($RemoteUrl -match '/([^/]+)\.git/?$') { return $Matches[1] }
        if ($RemoteUrl -match '\\([^\\]+)\.git\\?$') { return $Matches[1] }
    }
    try {
        return Split-Path -Path $RepoPath -Leaf
    }
    catch {
        return 'unknown'
    }
}

function Diag-InferSyncRoot {
    param(
        [string]$RepoPath,
        [string]$RmName,
        [ref]$OutRemoteUrl
    )
    $remoteUrl = $null
    try {
        $r = Diag-InvokeGit -Arguments @('remote', 'get-url', $RmName) -WorkingDirectory $RepoPath
        if ($r.Success) {
            $firstLine = $r.Output | Where-Object { $_ -and $_.ToString().Trim() } | Select-Object -First 1
            if ($firstLine) { $remoteUrl = $firstLine.ToString().Trim() }
        }
    }
    catch {}
    $OutRemoteUrl.Value = $remoteUrl

    if ($remoteUrl -and (Test-Path $remoteUrl -PathType Container)) {
        try {
            $bareDir = Diag-ResolveFullPath $remoteUrl
            if ((Split-Path $bareDir -Leaf) -like '*.git') {
                $reposDir = Split-Path -Parent $bareDir
                return Split-Path -Parent $reposDir
            }
        }
        catch {}
    }
    return $null
}

function Diag-CheckEnvironment {
    Diag-Section "1. 基本环境信息"

    $gitVerRes = Diag-InvokeGit -Arguments @('--version')
    if ($gitVerRes.Success) {
        $gitVer = ($gitVerRes.Output | Select-Object -First 1).ToString().Trim()
        Diag-Write -Status OK -Name "Git版本" -Detail $gitVer
    }
    else {
        Diag-Write -Status ERR -Name "Git版本" -Detail "无法执行git命令，请确认Git已安装并在PATH中"
        Diag-Suggest "安装Git: https://git-scm.com/downloads"
    }

    $os = Diag-DetectOS
    $osDesc = switch ($os) {
        'win' { "Windows $([System.Environment]::OSVersion.VersionString)" }
        'macos' { "macOS $(sw_vers -productVersion 2>$null)" }
        'linux' { "Linux $(uname -r 2>$null)" }
        default { "Unknown" }
    }
    Diag-Write -Status INFO -Name "操作系统" -Detail $osDesc
    Diag-Write -Status INFO -Name "脚本版本" -Detail "git-diag v$($script:DiagVersion)"

    $timeStr = $script:DiagStartTime.ToString("yyyy-MM-dd HH:mm:ss")
    Diag-Write -Status INFO -Name "诊断时间" -Detail $timeStr
}

function Diag-CheckRepoStatus {
    param([string]$RepoPath)

    Diag-Section "2. 仓库状态"

    $isGitRes = Diag-InvokeGit -Arguments @('rev-parse', '--is-inside-work-tree') -WorkingDirectory $RepoPath
    if (-not $isGitRes.Success) {
        Diag-Write -Status ERR -Name "Git仓库检查" -Detail "'$RepoPath' 不是有效的Git工作仓库"
        Diag-Suggest "使用 cd 命令进入正确的工作仓库目录，或使用 -RepoPath 参数指定仓库路径"
        return $false
    }
    Diag-Write -Status OK -Name "Git仓库" -Detail "有效的工作仓库"

    $revParseRes = Diag-InvokeGit -Arguments @('rev-parse', '--show-toplevel') -WorkingDirectory $RepoPath
    $repoRoot = $RepoPath
    if ($revParseRes.Success) {
        $repoRoot = ($revParseRes.Output | Select-Object -First 1).ToString().Trim()
        Diag-Write -Status INFO -Name "仓库根目录" -Detail $repoRoot
    }

    $branchRes = Diag-InvokeGit -Arguments @('rev-parse', '--abbrev-ref', 'HEAD') -WorkingDirectory $RepoPath
    if ($branchRes.Success) {
        $branch = ($branchRes.Output | Select-Object -First 1).ToString().Trim()
        Diag-Write -Status OK -Name "当前分支" -Detail $branch
    }
    else {
        Diag-Write -Status WARN -Name "当前分支" -Detail "无法获取当前分支（可能在detached HEAD状态）"
    }

    $statusRes = Diag-InvokeGit -Arguments @('status', '--porcelain') -WorkingDirectory $RepoPath
    if (-not $statusRes.Success) {
        Diag-Write -Status ERR -Name "工作区状态" -Detail "git status 执行失败"
    }
    else {
        $dirty = @($statusRes.Output | Where-Object { $_ -match '\S' })
        if ($dirty.Count -eq 0) {
            Diag-Write -Status OK -Name "工作区状态" -Detail "工作区干净 (clean)"
        }
        else {
            $staged = @($dirty | Where-Object { $_.ToString().Substring(0, 1) -match '[MADRC]' })
            $unstaged = @($dirty | Where-Object { $_.ToString().Substring(1, 1) -match '[MADRC]' })
            Diag-Write -Status WARN -Name "工作区状态" -Detail "dirty：$($dirty.Count)个更改（暂存$($staged.Count)个，未暂存$($unstaged.Count)个）"
            if ($dirty.Count -le 10) {
                foreach ($f in $dirty) {
                    Diag-Colorize "       $f" 'DarkGray'
                }
            }
            Diag-Suggest "工作区有未提交更改，建议执行 git stash 或 git commit 后再操作"
        }
    }

    $headRes = Diag-InvokeGit -Arguments @('rev-parse', 'HEAD') -WorkingDirectory $RepoPath
    if ($headRes.Success) {
        $headHash = ($headRes.Output | Select-Object -First 1).ToString().Trim()
        Diag-Write -Status INFO -Name "本地HEAD" -Detail $headHash
    }
    else {
        Diag-Write -Status WARN -Name "本地HEAD" -Detail "无法获取HEAD（可能没有提交）"
    }

    return $true
}

function Diag-CheckRemote {
    param(
        [string]$RepoPath,
        [string]$RmName,
        [ref]$OutRemoteUrl
    )

    Diag-Section "3. Remote配置"

    $remoteVRes = Diag-InvokeGit -Arguments @('remote', '-v') -WorkingDirectory $RepoPath
    if (-not $remoteVRes.Success -or -not $remoteVRes.Output) {
        Diag-Write -Status ERR -Name "Remote列表" -Detail "未配置任何remote"
        Diag-Suggest "添加baidu remote: git remote add baidu <SyncRoot>/repos/<repo>.git"
        $OutRemoteUrl.Value = $null
        return $false
    }

    foreach ($line in $remoteVRes.Output) {
        Diag-Colorize "    $line" 'Gray'
    }

    $baiduExists = @($remoteVRes.Output | Where-Object { $_ -match "^$RmName\s" }).Count -gt 0
    if (-not $baiduExists) {
        Diag-Write -Status ERR -Name "'$RmName' remote" -Detail "不存在"
        Diag-Suggest "添加baidu remote: git remote add $RmName <SyncRoot>/repos/<repo>.git"
        $OutRemoteUrl.Value = $null
        return $false
    }
    Diag-Write -Status OK -Name "'$RmName' remote" -Detail "已配置"

    $urlRes = Diag-InvokeGit -Arguments @('remote', 'get-url', $RmName) -WorkingDirectory $RepoPath
    $remoteUrl = $null
    if ($urlRes.Success) {
        $remoteUrl = ($urlRes.Output | Where-Object { $_ -match '\S' } | Select-Object -First 1).ToString().Trim()
        $OutRemoteUrl.Value = $remoteUrl
    }

    if (-not $remoteUrl) {
        Diag-Write -Status ERR -Name "Remote URL" -Detail "无法获取remote URL"
        return $false
    }

    Diag-Write -Status INFO -Name "Remote URL" -Detail $remoteUrl

    if ($remoteUrl -match '^\w+://|^git@') {
        Diag-Write -Status WARN -Name "Remote路径" -Detail "这是一个网络URL，不是本地路径（本方案使用本地网盘路径）"
        Diag-Suggest "baidu remote应指向网盘本地同步目录，例如: D:\BaiduSync\git-sync\repos\myrepo.git"
    }

    if (Test-Path $remoteUrl -PathType Container) {
        $headFile = Join-Path $remoteUrl "HEAD"
        $objDir = Join-Path $remoteUrl "objects"
        $refsDir = Join-Path $remoteUrl "refs"
        if ((Test-Path $headFile) -and (Test-Path $objDir) -and (Test-Path $refsDir)) {
            Diag-Write -Status OK -Name "裸仓库路径" -Detail "路径存在且结构有效"
        }
        else {
            Diag-Write -Status ERR -Name "裸仓库路径" -Detail "路径存在但不是有效的Git裸仓库（缺少HEAD/objects/refs）"
            Diag-Suggest "检查路径是否正确，或重新初始化裸仓库"
        }
    }
    else {
        Diag-Write -Status ERR -Name "裸仓库路径" -Detail "路径不存在或不可访问: $remoteUrl"
        Diag-Suggest "检查路径是否正确，网盘是否已同步完成，SyncRoot位置是否正确"
    }

    if ($remoteUrl -match ' ') {
        Diag-Write -Status WARN -Name "路径空格" -Detail "裸仓库路径包含空格，这可能导致某些脚本出现问题（但已在引号中处理）"
    }

    return ($remoteUrl -and (Test-Path $remoteUrl -PathType Container))
}

function Diag-CheckSyncRoot {
    param([string]$SRoot)

    Diag-Section "4. 网盘同步根目录结构"

    if (-not $SRoot) {
        Diag-Write -Status WARN -Name "SyncRoot" -Detail "无法自动推断SyncRoot，部分检查将跳过"
        Diag-Suggest "使用 -SyncRoot 参数指定网盘同步根目录路径"
        return $false
    }

    $sroot = Diag-ResolveFullPath $SRoot
    Diag-Write -Status INFO -Name "SyncRoot路径" -Detail $sroot

    if (-not (Test-Path $sroot -PathType Container)) {
        Diag-Write -Status ERR -Name "SyncRoot目录" -Detail "目录不存在"
        Diag-Suggest "确认SyncRoot路径正确，网盘客户端正在运行且已同步"
        return $false
    }
    Diag-Write -Status OK -Name "SyncRoot目录" -Detail "目录存在"

    $expectedDirs = @('repos', 'locks', 'backups', 'logs', 'meta', 'tmp')
    $missingDirs = @()
    foreach ($d in $expectedDirs) {
        $fullD = Join-Path $sroot $d
        if (-not (Test-Path $fullD -PathType Container)) {
            $missingDirs += $d
        }
    }

    if ($missingDirs.Count -eq 0) {
        Diag-Write -Status OK -Name "SyncRoot结构" -Detail "6个子目录全部存在 (repos/locks/backups/logs/meta/tmp)"
    }
    else {
        Diag-Write -Status WARN -Name "SyncRoot结构" -Detail "缺少子目录: $($missingDirs -join ', ')"
        Diag-Suggest "运行 init-sync-dir.ps1 初始化/修复同步目录结构"
    }

    return $true
}

function Diag-CheckLock {
    param(
        [string]$SRoot,
        [string]$RepoName
    )

    Diag-Section "5. 锁状态"

    if (-not $SRoot -or -not $script:DiagLockUtilsLoaded) {
        Diag-Write -Status INFO -Name "锁检查" -Detail "跳过（SyncRoot未指定或lock-utils未加载）"
        return
    }

    try {
        Lock-Init -SyncRoot $SRoot | Out-Null
    }
    catch {
        Diag-Write -Status ERR -Name "锁初始化" -Detail "Lock-Init失败: $_"
        return
    }

    $lockfile = Lock-GetLockfilePath -RepoName $RepoName
    if (-not $lockfile -or -not (Test-Path $lockfile -PathType Leaf)) {
        Diag-Write -Status OK -Name "锁状态" -Detail "无锁（仓库可用）"
        return
    }

    try {
        $holderDevice = Lock-ReadJsonField -FilePath $lockfile -Field "device_id"
        $holderPid = Lock-ReadJsonField -FilePath $lockfile -Field "pid"
        $holderOp = Lock-ReadJsonField -FilePath $lockfile -Field "operation"
        $holderTs = Lock-ReadJsonField -FilePath $lockfile -Field "acquired_at"
        $holderHost = Lock-ReadJsonField -FilePath $lockfile -Field "hostname"

        Diag-Write -Status WARN -Name "锁文件" -Detail "存在: $lockfile"
        Diag-Colorize "    持有者 device_id: $holderDevice" 'DarkYellow'
        Diag-Colorize "    持有者 hostname: $holderHost" 'DarkYellow'
        Diag-Colorize "    持有者 pid: $holderPid" 'DarkYellow'
        Diag-Colorize "    操作类型: $holderOp" 'DarkYellow'
        Diag-Colorize "    获取时间: $holderTs" 'DarkYellow'

        $myDeviceId = $script:LockUtilsDeviceId
        $isTimedOut = Lock-IsTimeoutLock -Lockfile $lockfile
        $lockAge = 0
        $lockEpoch = Lock-Iso8601ToEpoch -IsoString $holderTs
        $nowEpoch = Lock-GetNowEpoch
        if ($lockEpoch -gt 0) {
            $lockAge = [math]::Floor(($nowEpoch - $lockEpoch) / 60)
            Diag-Colorize "    已持有: $lockAge 分钟" 'DarkYellow'
        }

        if ($myDeviceId -and $holderDevice -eq $myDeviceId) {
            $holderPidInt = 0
            [int]::TryParse($holderPid, [ref]$holderPidInt) | Out-Null
            $pidAlive = $false
            if ($holderPidInt -gt 0) {
                try { $pidAlive = (Get-Process -Id $holderPidInt -ErrorAction SilentlyContinue) -ne $null } catch { $pidAlive = $false }
            }
            if ($pidAlive) {
                if ($holderPidInt -eq $PID) {
                    Diag-Write -Status INFO -Name "锁持有状态" -Detail "被当前进程持有（重入）"
                }
                else {
                    Diag-Write -Status WARN -Name "锁持有状态" -Detail "被本设备其他进程持有（pid=$holderPidInt）"
                    Diag-Suggest "等待该进程完成，或确认进程已退出后重试"
                }
            }
            else {
                Diag-Write -Status WARN -Name "锁持有状态" -Detail "本设备残留锁（pid=$holderPidInt 不存在）"
                Diag-Suggest "可以安全清理此残留锁: Remove-Item '$lockfile' -Force"
            }
        }
        elseif ($isTimedOut) {
            Diag-Write -Status WARN -Name "锁持有状态" -Detail "超时锁（已持有超过$(Lock-GetTimeoutMinutes)分钟）"
            Diag-Suggest "确认持有者设备已离线/崩溃后，使用 force-unlock.ps1 强制释放锁"
        }
        else {
            Diag-Write -Status ERR -Name "锁持有状态" -Detail "被其他设备持有，请勿操作！"
            Diag-Suggest "等待持有设备 $holderHost 完成操作；如确认持有者已离线且超时，使用 force-unlock.ps1"
        }
    }
    catch {
        Diag-Write -Status ERR -Name "锁读取" -Detail "读取锁文件失败: $_"
    }
}

function Diag-CheckConflictsAndTemp {
    param(
        [string]$SRoot,
        [string]$RepoName,
        [string]$RemoteUrl
    )

    Diag-Section "6. 冲突文件与临时文件"

    $bareRepo = $null
    if ($RemoteUrl -and (Test-Path $RemoteUrl -PathType Container)) {
        $bareRepo = Di