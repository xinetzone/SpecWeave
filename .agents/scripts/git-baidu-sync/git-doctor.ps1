# git-doctor.ps1 - Git 网盘同步健康检查 PowerShell 工具/库
# dot-source 使用作为库，或直接执行作为独立命令行工具
# 与 git-doctor.sh 功能等价

[CmdletBinding(DefaultParameterSetName = 'Single')]
param(
    [Parameter(Position = 0, ParameterSetName = 'Single')]
    [string]$RepoPath = '.',

    [Parameter(ParameterSetName = 'Single')]
    [Parameter(ParameterSetName = 'All')]
    [string]$SyncRoot = '',

    [Parameter(ParameterSetName = 'Single')]
    [Parameter(ParameterSetName = 'All')]
    [string]$RemoteName = '',

    [Parameter(ParameterSetName = 'Single')]
    [Parameter(ParameterSetName = 'All')]
    [ValidateSet('quick', 'full')]
    [string]$Mode = 'quick',

    [Parameter(ParameterSetName = 'All')]
    [switch]$All,

    [Parameter(ParameterSetName = 'Single')]
    [Parameter(ParameterSetName = 'All')]
    [switch]$Fix,

    [Parameter(ParameterSetName = 'Single')]
    [Parameter(ParameterSetName = 'All')]
    [switch]$NoColor
)

Set-StrictMode -Version Latest

$script:DoctorVersion = '1.0.0'
$script:DoctorColorEnabled = -not $NoColor

$script:DoctorScriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
$script:DoctorLockUtilsLoaded = $false
$script:DoctorConflictsLoaded = $false

. (Join-Path $script:DoctorScriptDir 'lock-utils.ps1')
. (Join-Path $script:DoctorScriptDir 'check-conflicts.ps1')
$script:DoctorLockUtilsLoaded = $true
$script:DoctorConflictsLoaded = $true

$script:DoctorMinGitVersion = [version]'2.30.0'
$script:DoctorLooseObjWarnThreshold = 6700
$script:DoctorLooseObjErrThreshold = 10000
$script:DoctorMaxPackFiles = 1
$script:DoctorBackupWarnDays = 7
$script:DoctorBackupErrDays = 30
$script:DoctorDiskWarnGB = 5
$script:DoctorDiskErrGB = 1

enum CheckStatus {
    OK
    WARN
    ERR
    INFO
}

function Doctor-Colorize {
    param(
        [string]$Text,
        [string]$Color = 'White'
    )
    if ($script:DoctorColorEnabled) {
        Write-Host $Text -ForegroundColor $Color
    }
    else {
        Write-Host $Text
    }
}

function Doctor-WriteCheck {
    param(
        [CheckStatus]$Status,
        [string]$Name,
        [string]$Detail = ''
    )

    $prefix = switch ($Status) {
        ([CheckStatus]::OK)   { @{ Text = '[OK]  '; Color = 'Green' } }
        ([CheckStatus]::WARN) { @{ Text = '[WARN]'; Color = 'Yellow' } }
        ([CheckStatus]::ERR)  { @{ Text = '[ERR] '; Color = 'Red' } }
        ([CheckStatus]::INFO) { @{ Text = '[INFO]'; Color = 'Cyan' } }
    }

    Write-Host $prefix.Text -NoNewline -ForegroundColor $prefix.Color
    $detailStr = if ($Detail) { " - $Detail" } else { '' }
    Write-Host " $Name$detailStr"
}

function Doctor-InvokeGit {
    param(
        [string[]]$Arguments,
        [string]$WorkingDirectory = '.'
    )
    $output = & git @Arguments 2>&1
    return @{
        Output = $output
        ExitCode = $LASTEXITCODE
        Success = ($LASTEXITCODE -eq 0)
    }
}

function Doctor-ResolveFullPath {
    param([string]$Path)
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

function Doctor-CompareVersion {
    param([version]$V1, [version]$V2)
    return $V1.CompareTo($V2)
}

function Doctor-GetRepoName {
    param(
        [string]$RepoPath,
        [string]$RemoteUrl
    )
    if ($RemoteUrl) {
        if ($RemoteUrl -match '/([^/]+)\.git/?$') { return $Matches[1] }
        if ($RemoteUrl -match '\\([^\\]+)\.git\\?$') { return $Matches[1] }
    }
    return Split-Path -Path $RepoPath -Leaf
}

function Doctor-InferSyncRoot {
    param(
        [string]$RepoPath,
        [string]$RemoteName,
        [ref]$OutRemoteUrl
    )
    $remoteUrl = $null
    try {
        $result = Doctor-InvokeGit -Arguments @('remote', 'get-url', $RemoteName) -WorkingDirectory $RepoPath
        if ($result.Success) {
            $remoteUrl = ($result.Output | Where-Object { $_ -and $_.ToString().Trim() } | Select-Object -First 1)
            if ($remoteUrl) { $remoteUrl = $remoteUrl.ToString().Trim() }
        }
    }
    catch {}
    $OutRemoteUrl.Value = $remoteUrl

    if ($remoteUrl -and (Test-Path $remoteUrl -PathType Container)) {
        $bareDir = Doctor-ResolveFullPath $remoteUrl
        if ((Split-Path $bareDir -Leaf) -like '*.git') {
            $reposDir = Split-Path -Parent $bareDir
            return Split-Path -Parent $reposDir
        }
    }
    return $null
}

function Doctor-DetectOS {
    if ($IsWindows) { return 'win' }
    if ($IsMacOS) { return 'macos' }
    if ($IsLinux) { return 'linux' }
    if ($env:OS -eq 'Windows_NT') { return 'win' }
    return 'unknown'
}

function Doctor-CheckGitVersion {
    $result = Doctor-InvokeGit -Arguments @('--version')
    if (-not $result.Success) {
        return @{ Status = [CheckStatus]::ERR; Name = 'Git版本'; Detail = '无法执行git命令，请确认Git已安装' }
    }
    $versionLine = ($result.Output | Select-Object -First 1).ToString()
    if ($versionLine -match 'git version (\d+\.\d+\.\d+)') {
        $ver = [version]$Matches[1]
        if (Doctor-CompareVersion $ver $script:DoctorMinGitVersion -ge 0) {
            return @{ Status = [CheckStatus]::OK; Name = 'Git版本'; Detail = "$ver (≥ $($script:DoctorMinGitVersion))" }
        }
        else {
            return @{ Status = [CheckStatus]::ERR; Name = 'Git版本'; Detail = "$ver < $($script:DoctorMinGitVersion)，请升级Git" }
        }
    }
    return @{ Status = [CheckStatus]::WARN; Name = 'Git版本'; Detail = "无法解析版本: $versionLine" }
}

function Doctor-CheckRepoValid {
    param([string]$RepoPath)
    $result = Doctor-InvokeGit -Arguments @('rev-parse', '--is-inside-work-tree') -WorkingDirectory $RepoPath
    if ($result.Success) {
        return @{ Status = [CheckStatus]::OK; Name = '仓库有效性'; Detail = '有效的Git工作仓库' }
    }
    return @{ Status = [CheckStatus]::ERR; Name = '仓库有效性'; Detail = '不是有效的Git工作仓库' }
}

function Doctor-CheckWorktree {
    param([string]$RepoPath)
    $result = Doctor-InvokeGit -Arguments @('status', '--porcelain') -WorkingDirectory $RepoPath
    if (-not $result.Success) {
        return @{ Status = [CheckStatus]::ERR; Name = '工作区状态'; Detail = 'git status执行失败' }
    }
    $dirty = @($result.Output | Where-Object { $_ -match '\S' })
    if ($dirty.Count -eq 0) {
        return @{ Status = [CheckStatus]::OK; Name = '工作区状态'; Detail = '工作区干净' }
    }
    return @{ Status = [CheckStatus]::WARN; Name = '工作区状态'; Detail = "有$($dirty.Count)个未提交的更改" }
}

function Doctor-CheckTempFiles {
    param([string]$BareRepoPath)
    if (-not (Test-Path $BareRepoPath -PathType Container)) {
        return @{ Status = [CheckStatus]::ERR; Name = '半同步检测'; Detail = "裸仓库路径不存在: $BareRepoPath" }
    }
    $tempPatterns = @('*.tmp', '*.pack-tmp', '*.part', '*.temp', '*.downloading')
    $tempFiles = @()
    foreach ($pattern in $tempPatterns) {
        $found = Get-ChildItem -Path $BareRepoPath -Recurse -Filter $pattern -File -ErrorAction SilentlyContinue
        if ($found) { $tempFiles += $found }
    }
    $tmpPackFiles = Get-ChildItem -Path $BareRepoPath -Recurse -Filter 'tmp_pack_*' -File -ErrorAction SilentlyContinue
    if ($tmpPackFiles) { $tempFiles += $tmpPackFiles }

    $keepFiles = Get-ChildItem -Path $BareRepoPath -Recurse -Filter '*.keep' -File -ErrorAction SilentlyContinue
    if ($keepFiles) {
        foreach ($kf in $keepFiles) {
            $age = (Get-Date) - $kf.LastWriteTime
            if ($age.TotalMinutes -gt 10) {
                $tempFiles += $kf
            }
        }
    }

    $strayLocks = @()
    $allLocks = Get-ChildItem -Path $BareRepoPath -Recurse -Filter '*.lock' -File -ErrorAction SilentlyContinue
    foreach ($lock in $allLocks) {
        $bname = $lock.Name
        if ($bname -ne 'HEAD.lock' -and $bname -notmatch '^pack-.+\.lock$') {
            $strayLocks += $lock
        }
    }
    if ($strayLocks) { $tempFiles += $strayLocks }

    if ($tempFiles.Count -eq 0) {
        return @{ Status = [CheckStatus]::OK; Name = '半同步检测'; Detail = '未发现临时文件' }
    }
    $names = ($tempFiles | Select-Object -First 3 -ExpandProperty Name) -join ', '
    $more = if ($tempFiles.Count -gt 3) { " 等$($tempFiles.Count)个" } else { '' }
    return @{ Status = [CheckStatus]::ERR; Name = '半同步检测'; Detail = "发现临时文件: $names$more" }
}

function Doctor-CheckConflicts {
    param([string]$BareRepoPath)
    if (-not (Test-Path $BareRepoPath -PathType Container)) {
        return @{ Status = [CheckStatus]::ERR; Name = '冲突副本'; Detail = '裸仓库路径不存在' }
    }
    $scanResult = Conflicts-Scan -BareRepoPath $BareRepoPath
    if (-not $scanResult) {
        return @{ Status = [CheckStatus]::ERR; Name = '冲突副本'; Detail = '扫描失败' }
    }
    if ($scanResult.HasCritical) {
        return @{ Status = [CheckStatus]::ERR; Name = '冲突副本'; Detail = "发现$($scanResult.CriticalCount)个严重冲突！必须从备份恢复" }
    }
    if ($scanResult.WarningCount -gt 0) {
        return @{ Status = [CheckStatus]::WARN; Name = '冲突副本'; Detail = "发现$($scanResult.WarningCount)个警告级冲突，建议检查" }
    }
    if ($scanResult.InfoCount -gt 0) {
        return @{ Status = [CheckStatus]::INFO; Name = '冲突副本'; Detail = "发现$($scanResult.InfoCount)个临时文件/无害冲突" }
    }
    return @{ Status = [CheckStatus]::OK; Name = '冲突副本'; Detail = '未发现冲突文件' }
}

function Doctor-CheckLock {
    param(
        [string]$SyncRoot,
        [string]$RepoName
    )
    Lock-Init -SyncRoot $SyncRoot | Out-Null
    $lockCode = Lock-Check -RepoName $RepoName
    switch ($lockCode) {
        0 { return @{ Status = [CheckStatus]::OK; Name = '锁状态'; Detail = '无锁（可用）' } }
        1 { return @{ Status = [CheckStatus]::INFO; Name = '锁状态'; Detail = '被本设备持有' } }
        2 { return @{ Status = [CheckStatus]::WARN; Name = '锁状态'; Detail = '被其他设备持有，请等待' } }
        3 { return @{ Status = [CheckStatus]::ERR; Name = '锁状态'; Detail = '超时锁，需要清理' } }
        default { return @{ Status = [CheckStatus]::WARN; Name = '锁状态'; Detail = '锁状态未知' } }
    }
}

function Doctor-CheckHead {
    param(
        [string]$RepoPath,
        [string]$BareRepoPath
    )
    $localResult = Doctor-InvokeGit -Arguments @('rev-parse', 'HEAD') -WorkingDirectory $RepoPath
    if (-not $localResult.Success) {
        return @{ Status = [CheckStatus]::WARN; Name = 'HEAD对比'; Detail = '无法获取本地HEAD（可能无提交）' }
    }
    $localHead = ($localResult.Output | Select-Object -First 1).ToString().Trim()

    if (-not (Test-Path $BareRepoPath -PathType Container)) {
        return @{ Status = [CheckStatus]::WARN; Name = 'HEAD对比'; Detail = '裸仓库不存在，无法对比' }
    }
    $bareResult = Doctor-InvokeGit -Arguments @('-C', $BareRepoPath, 'rev-parse', 'HEAD')
    if (-not $bareResult.Success) {
        $bareVer = Doctor-InvokeGit -Arguments @('--version')
        if ($bareVer.Success -and ($bareVer.Output | Select-Object -First 1) -match 'git version (\d+)\.(\d+)') {
            return @{ Status = [CheckStatus]::WARN; Name = 'HEAD对比'; Detail = '无法获取裸仓库HEAD（裸仓库可能为空）' }
        }
        return @{ Status = [CheckStatus]::WARN; Name = 'HEAD对比'; Detail = '无法获取裸仓库HEAD' }
    }
    $bareHead = ($bareResult.Output | Select-Object -First 1).ToString().Trim()

    if ($localHead -eq $bareHead) {
        return @{ Status = [CheckStatus]::OK; Name = 'HEAD对比'; Detail = "本地与裸仓库一致 ($($localHead.Substring(0,7)))" }
    }

    $mergeBase = Doctor-InvokeGit -Arguments @('-C', $RepoPath, 'merge-base', $localHead, $bareHead)
    if ($mergeBase.Success) {
        $mb = ($mergeBase.Output | Select-Object -First 1).ToString().Trim()
        if ($mb -eq $bareHead) {
            $countResult = Doctor-InvokeGit -Arguments @('-C', $RepoPath, 'rev-list', '--count', "$bareHead..$localHead")
            $ahead = if ($countResult.Success) { ($countResult.Output | Select-Object -First 1).ToString().Trim() } else { '?' }
            return @{ Status = [CheckStatus]::INFO; Name = 'HEAD对比'; Detail = "本地领先远程 $ahead 个提交（有未push提交）" }
        }
        if ($mb -eq $localHead) {
            $countResult = Doctor-InvokeGit -Arguments @('-C', $RepoPath, 'rev-list', '--count', "$localHead..$bareHead")
            $behind = if ($countResult.Success) { ($countResult.Output | Select-Object -First 1).ToString().Trim() } else { '?' }
            return @{ Status = [CheckStatus]::WARN; Name = 'HEAD对比'; Detail = "本地落后远程 $behind 个提交，需要先pull" }
        }
    }
    return @{ Status = [CheckStatus]::ERR; Name = 'HEAD对比'; Detail = "本地与裸仓库HEAD不一致（已分歧），本地=$($localHead.Substring(0,7)) 远程=$($bareHead.Substring(0,7))" }
}

function Doctor-CheckLooseObjects {
    param([string]$RepoPath)
    $result = Doctor-InvokeGit -Arguments @('count-objects', '-v') -WorkingDirectory $RepoPath
    if (-not $result.Success) {
        return @{ Status = [CheckStatus]::WARN; Name = '松散对象'; Detail = 'count-objects执行失败' }
    }
    $loose = 0
    $packs = 0
    foreach ($line in $result.Output) {
        $s = $line.ToString()
        if ($s -match '^count: (\d+)') { $loose = [int]$Matches[1] }
        if ($s -match '^packs: (\d+)') { $packs = [int]$Matches[1] }
    }

    if ($loose -ge $script:DoctorLooseObjErrThreshold) {
        return @{ Status = [CheckStatus]::ERR; Name = '松散对象'; Detail = "松散对象 $loose 个，超过 $($script:DoctorLooseObjErrThreshold)，必须GC" }
    }
    if ($loose -ge $script:DoctorLooseObjWarnThreshold) {
        return @{ Status = [CheckStatus]::WARN; Name = '松散对象'; Detail = "松散对象 $loose 个，超过 $($script:DoctorLooseObjWarnThreshold)，建议GC" }
    }
    return @{ Status = [CheckStatus]::OK; Name = '松散对象'; Detail = "$loose 个松散对象，$packs 个pack文件" }
}

function Doctor-CheckPackFiles {
    param([string]$RepoPath)
    $gitDir = $null
    $result = Doctor-InvokeGit -Arguments @('rev-parse', '--git-path', 'objects/pack') -WorkingDirectory $RepoPath
    if ($result.Success) {
        $packRel = ($result.Output | Select-Object -First 1).ToString().Trim()
        $gitCommonDir = Doctor-InvokeGit -Arguments @('rev-parse', '--git-common-dir') -WorkingDirectory $RepoPath
        if ($gitCommonDir.Success) {
            $gDir = ($gitCommonDir.Output | Select-Object -First 1).ToString().Trim()
            $gitDir = if ([System.IO.Path]::IsPathRooted($gDir)) { $gDir } else { Join-Path $RepoPath $gDir }
        }
    }
    if (-not $gitDir) {
        $gitDirResult = Doctor-InvokeGit -Arguments @('rev-parse', '--git-dir') -WorkingDirectory $RepoPath
        if ($gitDirResult.Success) {
            $gDir = ($gitDirResult.Output | Select-Object -First 1).ToString().Trim()
            $gitDir = if ([System.IO.Path]::IsPathRooted($gDir)) { $gDir } else { Join-Path $RepoPath $gDir }
        }
    }
    if (-not $gitDir) {
        return @{ Status = [CheckStatus]::WARN; Name = 'Pack文件'; Detail = '无法定位pack目录' }
    }
    $packDir = Join-Path $gitDir 'objects\pack'
    if (-not (Test-Path $packDir -PathType Container)) {
        return @{ Status = [CheckStatus]::OK; Name = 'Pack文件'; Detail = 'pack目录不存在（新仓库）' }
    }
    $packFiles = Get-ChildItem -Path $packDir -Filter '*.pack' -File -ErrorAction SilentlyContinue
    $packCount = if ($packFiles) { $packFiles.Count } else { 0 }
    if ($packCount -gt $script:DoctorMaxPackFiles) {
        return @{ Status = [CheckStatus]::WARN; Name = 'Pack文件'; Detail = "$packCount 个pack文件（超过$script:DoctorMaxPackFiles），建议GC优化" }
    }
    return @{ Status = [CheckStatus]::OK; Name = 'Pack文件'; Detail = "$packCount 个pack文件" }
}

function Doctor-CheckFsck {
    param([string]$BareRepoPath)
    if (-not (Test-Path $BareRepoPath -PathType Container)) {
        return @{ Status = [CheckStatus]::ERR; Name = 'Fsck完整性'; Detail = '裸仓库不存在' }
    }
    $fsckOutput = & git -C $BareRepoPath fsck --full --strict 2>&1
    $fsckExit = $LASTEXITCODE
    $errors = @()
    $dangling = @()
    foreach ($line in $fsckOutput) {
        $s = $line.ToString()
        if ($s -match '^(error|missing|broken)') { $errors += $s }
        elseif ($s -match '^dangling') { $dangling += $s }
    }
    if ($errors.Count -gt 0) {
        $sample = ($errors | Select-Object -First 2) -join '; '
        return @{ Status = [CheckStatus]::ERR; Name = 'Fsck完整性'; Detail = "发现$($errors.Count)个错误: $sample" }
    }
    if ($dangling.Count -gt 0) {
        return @{ Status = [CheckStatus]::INFO; Name = 'Fsck完整性'; Detail = "通过，有$($dangling.Count)个悬挂对象（无害）" }
    }
    return @{ Status = [CheckStatus]::OK; Name = 'Fsck完整性'; Detail = '通过，无错误' }
}

function Doctor-CheckBackup {
    param(
        [string]$SyncRoot,
        [string]$RepoName
    )
    $backupDir = Join-Path $SyncRoot "backups\$RepoName"
    if (-not (Test-Path $backupDir -PathType Container)) {
        return @{ Status = [CheckStatus]::ERR; Name = '备份健康'; Detail = '备份目录不存在，无任何备份' }
    }
    $bundles = Get-ChildItem -Path $backupDir -Filter '*.bundle' -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
    if (-not $bundles -or $bundles.Count -eq 0) {
        return @{ Status = [CheckStatus]::ERR; Name = '备份健康'; Detail = '未找到任何.bundle备份文件' }
    }
    $latest = $bundles[0]
    $age = (Get-Date) - $latest.LastWriteTime
    if ($age.TotalDays -gt $script:DoctorBackupErrDays) {
        return @{ Status = [CheckStatus]::ERR; Name = '备份健康'; Detail = "最新备份是$([int]$age.TotalDays)天前（超过$($script:DoctorBackupErrDays)天），必须立即备份" }
    }
    if ($age.TotalDays -gt $script:DoctorBackupWarnDays) {
        return @{ Status = [CheckStatus]::WARN; Name = '备份健康'; Detail = "最新备份是$([int]$age.TotalDays)天前（超过$($script:DoctorBackupWarnDays)天），建议备份" }
    }
    return @{ Status = [CheckStatus]::OK; Name = '备份健康'; Detail = "最新备份 $($latest.Name)，$([int]$age.TotalDays)天前" }
}

function Doctor-CheckConfig {
    param([string]$RepoPath)
    $os = Doctor-DetectOS
    $issues = @()
    $autocrlfResult = Doctor-InvokeGit -Arguments @('config', '--get', 'core.autocrlf') -WorkingDirectory $RepoPath
    if (-not $autocrlfResult.Success -or -not (($autocrlfResult.Output | Select-Object -First 1) -match '\S')) {
        $autocrlfResult = Doctor-InvokeGit -Arguments @('config', '--global', '--get', 'core.autocrlf')
    }
    $autocrlf = if ($autocrlfResult.Success) { (($autocrlfResult.Output | Select-Object -First 1).ToString().Trim()) } else { '' }
    $expectedAutocrlf = if ($os -eq 'win') { 'true' } else { 'input' }
    if ($autocrlf -ne $expectedAutocrlf) {
        $issues += "core.autocrlf=$autocrlf (推荐$expectedAutocrlf)"
    }

    $gcAutoResult = Doctor-InvokeGit -Arguments @('config', '--get', 'gc.auto') -WorkingDirectory $RepoPath
    if (-not $gcAutoResult.Success -or -not (($gcAutoResult.Output | Select-Object -First 1) -match '\S')) {
        $gcAutoResult = Doctor-InvokeGit -Arguments @('config', '--global', '--get', 'gc.auto')
    }
    $gcAuto = if ($gcAutoResult.Success) { (($gcAutoResult.Output | Select-Object -First 1).ToString().Trim()) } else { '' }
    if ($gcAuto -ne '6700') {
        $issues += "gc.auto=$gcAuto (推荐6700)"
    }

    $gcAutoPackResult = Doctor-InvokeGit -Arguments @('config', '--get', 'gc.autopacklimit') -WorkingDirectory $RepoPath
    if (-not $gcAutoPackResult.Success -or -not (($gcAutoPackResult.Output | Select-Object -First 1) -match '\S')) {
        $gcAutoPackResult = Doctor-InvokeGit -Arguments @('config', '--global', '--get', 'gc.autopacklimit')
    }
    $gcAutoPack = if ($gcAutoPackResult.Success) { (($gcAutoPackResult.Output | Select-Object -First 1).ToString().Trim()) } else { '' }
    if ($gcAutoPack -ne '1') {
        $issues += "gc.autopacklimit=$gcAutoPack (推荐1)"
    }

    if ($os -eq 'win') {
        $longpathsResult = Doctor-InvokeGit -Arguments @('config', '--get', 'core.longpaths') -WorkingDirectory $RepoPath
        if (-not $longpathsResult.Success -or -not (($longpathsResult.Output | Select-Object -First 1) -match '\S')) {
            $longpathsResult = Doctor-InvokeGit -Arguments @('config', '--global', '--get', 'core.longpaths')
        }
        $longpaths = if ($longpathsResult.Success) { (($longpathsResult.Output | Select-Object -First 1).ToString().Trim()) } else { '' }
        if ($longpaths -ne 'true') {
            $issues += "core.longpaths=$longpaths (推荐true)"
        }
    }

    if ($issues.Count -gt 0) {
        return @{ Status = [CheckStatus]::WARN; Name = '配置检查'; Detail = ($issues -join '; ') }
    }
    return @{ Status = [CheckStatus]::OK; Name = '配置检查'; Detail = '关键配置符合推荐值' }
}

function Doctor-CheckDiskSpace {
    param([string]$SyncRoot)
    if (-not (Test-Path $SyncRoot -PathType Container)) {
        return @{ Status = [CheckStatus]::WARN; Name = '磁盘空间'; Detail = 'SyncRoot不存在，无法检查' }
    }
    try {
        $drive = Get-Item $SyncRoot | ForEach-Object { $_.PSDrive }
        if (-not $drive) {
            $root = [System.IO.Path]::GetPathRoot($SyncRoot)
            $drive = Get-PSDrive -Name ($root.TrimEnd(':\')) -ErrorAction Stop
        }
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        if ($freeGB -lt $script:DoctorDiskErrGB) {
            return @{ Status = [CheckStatus]::ERR; Name = '磁盘空间'; Detail = "可用空间 ${freeGB}GB（不足$($script:DoctorDiskErrGB)GB）" }
        }
        if ($freeGB -lt $script:DoctorDiskWarnGB) {
            return @{ Status = [CheckStatus]::WARN; Name = '磁盘空间'; Detail = "可用空间 ${freeGB}GB（不足$($script:DoctorDiskWarnGB)GB）" }
        }
        return @{ Status = [CheckStatus]::OK; Name = '磁盘空间'; Detail = "可用空间 ${freeGB}GB" }
    }
    catch {
        return @{ Status = [CheckStatus]::WARN; Name = '磁盘空间'; Detail = "无法检查: $_" }
    }
}

function Doctor-FixTempFiles {
    param([string]$BareRepoPath)
    if (-not (Test-Path $BareRepoPath -PathType Container)) { return $false }
    Write-Host ''
    Write-Host '=== 自动修复：清理临时文件 ===' -ForegroundColor Yellow
    Write-Host '⚠️  请确认没有Git进程正在操作此仓库！' -ForegroundColor Yellow
    $confirm = Read-Host '确认清理临时文件？(YES/no)'
    if ($confirm -ne 'YES') { Write-Host '跳过'; return $false }

    $toDelete = @()
    foreach ($pattern in @('*.tmp', '*.pack-tmp', '*.part', '*.temp', '*.downloading', 'tmp_pack_*')) {
        $found = Get-ChildItem -Path $BareRepoPath -Recurse -Filter $pattern -File -ErrorAction SilentlyContinue
        if ($found) { $toDelete += $found }
    }
    foreach ($lock in (Get-ChildItem -Path $BareRepoPath -Recurse -Filter '*.lock' -File -ErrorAction SilentlyContinue)) {
        $bname = $lock.Name
        if ($bname -ne 'HEAD.lock' -and $bname -notmatch '^pack-.+\.lock$') {
            $toDelete += $lock
        }
    }

    $deleted = 0
    foreach ($f in $toDelete) {
        try {
            Remove-Item $f.FullName -Force -ErrorAction Stop
            Write-Host "  已删除: $($f.Name)" -ForegroundColor Green
            $deleted++
        }
        catch {
            Write-Host "  删除失败: $($f.Name) - $_" -ForegroundColor Red
        }
    }
    Write-Host "清理完成: 删除 $deleted 个临时文件"
    return $deleted -gt 0
}

function Doctor-FixGC {
    param([string]$RepoPath)
    Write-Host ''
    Write-Host '=== 自动修复：执行 git gc ===' -ForegroundColor Yellow
    Write-Host '⚠️  GC会重写pack文件，请确认没有其他设备/进程在操作！' -ForegroundColor Yellow
    $confirm = Read-Host '确认执行 git gc？(YES/no)'
    if ($confirm -ne 'YES') { Write-Host '跳过'; return $false }
    & git -C $RepoPath gc --aggressive --prune=now
    return ($LASTEXITCODE -eq 0)
}

function Doctor-FixBackup {
    param(
        [string]$RepoPath,
        [string]$SyncRoot,
        [string]$RepoName
    )
    Write-Host ''
    Write-Host '=== 自动修复：创建新备份 ===' -ForegroundColor Yellow
    $backupDir = Join-Path $SyncRoot "backups\$RepoName"
    if (-not (Test-Path $backupDir)) {
        New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    }
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    $bundleFile = Join-Path $backupDir "$RepoName-$timestamp.bundle"
    $confirm = Read-Host "确认创建备份到 $bundleFile？(YES/no)"
    if ($confirm -ne 'YES') { Write-Host '跳过'; return $false }
    & git -C $RepoPath bundle create $bundleFile --all
    if ($LASTEXITCODE -eq 0) {
        Write-Host "备份已创建: $bundleFile" -ForegroundColor Green
        return $true
    }
    Write-Host '备份创建失败' -ForegroundColor Red
    return $false
}

function Doctor-RunChecks {
    param(
        [string]$RepoPath,
        [string]$SyncRoot,
        [string]$RemoteName,
        [string]$Mode
    )

    $results = @()
    $RepoPath = Doctor-ResolveFullPath $RepoPath

    $remoteUrl = $null
    if (-not $SyncRoot) {
        $SyncRoot = Doctor-InferSyncRoot -RepoPath $RepoPath -RemoteName $RemoteName -OutRemoteUrl ([ref]$remoteUrl)
        if (-not $SyncRoot) {
            Write-Host ''
            Doctor-WriteCheck -Status ([CheckStatus]::ERR) -Name 'SyncRoot推断' -Detail '无法自动推断SyncRoot，请使用-SyncRoot参数指定'
            return @{ Checks = @(@{ Status = [CheckStatus]::ERR; Name = 'SyncRoot'; Detail = '无法推断' }); HasErrors = $true }
        }
    }
    else {
        $SyncRoot = Doctor-ResolveFullPath $SyncRoot
        try {
            $r = Doctor-InvokeGit -Arguments @('remote', 'get-url', $RemoteName) -WorkingDirectory $RepoPath
            if ($r.Success) { $remoteUrl = ($r.Output | Where-Object { $_ -match '\S' } | Select-Object -First 1).ToString().Trim() }
        }
        catch {}
    }

    if (-not $RemoteName) { $RemoteName = 'baidu' }
    $repoName = Doctor-GetRepoName -RepoPath $RepoPath -RemoteUrl $remoteUrl
    $bareRepoPath = Join-Path $SyncRoot "repos\$repoName.git"

    Write-Host ''
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  git-doctor v$($script:DoctorVersion) - 健康检查" -ForegroundColor Magenta
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  仓库路径:   $RepoPath"
    Write-Host "  SyncRoot:   $SyncRoot"
    Write-Host "  Remote:     $RemoteName -> $remoteUrl"
    Write-Host "  裸仓库:     $bareRepoPath"
    Write-Host "  模式:       $Mode"
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host ''

    $results += Doctor-CheckGitVersion
    $results += Doctor-CheckRepoValid -RepoPath $RepoPath
    $results += Doctor-CheckWorktree -RepoPath $RepoPath
    $results += Doctor-CheckTempFiles -BareRepoPath $bareRepoPath
    $results += Doctor-CheckConflicts -BareRepoPath $bareRepoPath
    $results += Doctor-CheckLock -SyncRoot $SyncRoot -RepoName $repoName
    $results += Doctor-CheckHead -RepoPath $RepoPath -BareRepoPath $bareRepoPath

    $looseResult = Doctor-CheckLooseObjects -RepoPath $RepoPath
    $results += $looseResult

    if ($Mode -eq 'full') {
        $results += Doctor-CheckPackFiles -RepoPath $RepoPath
        $results += Doctor-CheckFsck -BareRepoPath $bareRepoPath
        $results += Doctor-CheckBackup -SyncRoot $SyncRoot -RepoName $repoName
        $results += Doctor-CheckConfig -RepoPath $RepoPath
        $results += Doctor-CheckDiskSpace -SyncRoot $SyncRoot
    }

    Write-Host ''
    foreach ($r in $results) {
        Doctor-WriteCheck -Status $r.Status -Name $r.Name -Detail $r.Detail
    }

    $okCount = @($results | Where-Object { $_.Status -eq [CheckStatus]::OK }).Count
    $warnCount = @($results | Where-Object { $_.Status -eq [CheckStatus]::WARN }).Count
    $errCount = @($results | Where-Object { $_.Status -eq [CheckStatus]::ERR }).Count
    $infoCount = @($results | Where-Object { $_.Status -eq [CheckStatus]::INFO }).Count
    $total = $results.Count

    Write-Host ''
    Write-Host "========================================" -ForegroundColor Magenta
    Write-Host "  汇总: $total 个检查项" -ForegroundColor Magenta
    Write-Host "  绿色 [OK]:   $okCount" -ForegroundColor Green
    Write-Host "  蓝色 [INFO]: $infoCount" -ForegroundColor Cyan
    Write-Host "  黄色 [WARN]: $warnCount" -ForegroundColor Yellow
    Write-Host "  红色 [ERR]:  $errCount" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Magenta

    if ($errCount -gt 0) {
        Write-Host ''
        Write-Host '🛑 发现错误，请修复后再操作。' -ForegroundColor Red
    }
    elseif ($warnCount -gt 0) {
        Write-Host ''
        Write-Host '⚠️  存在警告，建议关注。' -ForegroundColor Yellow
    }
    else {
        Write-Host ''
        Write-Host '✅ 所有检查通过。' -ForegroundColor Green
    }
    Write-Host ''

    return @{
        Checks = $results
        Total = $total
        Ok = $okCount
        Warn = $warnCount
        Err = $errCount
        Info = $infoCount
        HasErrors = ($errCount -gt 0)
        RepoName = $repoName
        BareRepoPath = $bareRepoPath
        SyncRoot = $SyncRoot
        RepoPath = $RepoPath
        RemoteUrl = $remoteUrl
        LooseStatus = $looseResult
    }
}

function Doctor-ShowUsage {
    Write-Host @"
git-doctor.ps1 - Git 网盘同步健康检查工具 v$($script:DoctorVersion)

用法:
  .\git-doctor.ps1 [选项]

选项（独立执行时）:
  -RepoPath <path>    本地工作仓库路径（默认 .）
  -SyncRoot <path>    网盘同步根目录（可从 remote 自动推断）
  -RemoteName <name>  Git remote 名称（默认 baidu）
  -Mode <quick|full>  检查模式: quick(默认) / full
  -All                检查 SyncRoot 下所有仓库
  -Fix                自动修复可安全修复的问题（需交互确认）
  -NoColor            禁用彩色输出
  -h, --help          显示此帮助

作为库使用（dot-source）:
  . .\git-doctor.ps1

  Doctor-RunChecks <RepoPath> <SyncRoot> <RemoteName> <Mode>
  # 返回结果对象，包含 Checks/Total/Ok/Warn/Err/HasErrors 等属性

退出码:
  0 = 无错误（可能有警告）
  1 = 存在错误，应阻止 push

检查项 (quick):
  Git版本、仓库有效性、工作区状态、半同步/临时文件、冲突副本、
  锁状态、HEAD对比、松散对象计数

检查项 (full，quick基础上增加):
  Pack文件数、fsck完整性、备份健康、配置检查、磁盘空间

示例:
  # 快速检查当前仓库
  .\git-doctor.ps1

  # 全面检查
  .\git-doctor.ps1 -Mode full

  # 检查并自动修复
  .\git-doctor.ps1 -Mode full -Fix

  # 检查所有仓库
  .\git-doctor.ps1 -All -SyncRoot D:\BaiduSync\git-sync
"@
}

$script:DoctorIsRunningDirectly = $false
if ($MyInvocation.InvocationName -ne '.' -and $MyInvocation.InvocationName -ne '&') {
    $script:DoctorIsRunningDirectly = $true
}
elseif ($MyInvocation.MyCommand.Path -eq $PSCommandPath) {
    $line = $MyInvocation.Line
    if ($line -notmatch '\.\s+.*git-doctor\.ps1') {
        $script:DoctorIsRunningDirectly = $true
    }
}

if ($script:DoctorIsRunningDirectly) {
    foreach ($arg in $args) {
        switch -Regex ($arg) {
            '^--?h(elp)?$' { Doctor-ShowUsage; exit 0 }
            default { }
        }
    }

    if (-not $RemoteName) { $RemoteName = 'baidu' }

    if ($All) {
        if (-not $SyncRoot) {
            Write-Host '错误: -All 模式需要指定 -SyncRoot' -ForegroundColor Red
            Doctor-ShowUsage
            exit 2
        }
        $SyncRoot = Doctor-ResolveFullPath $SyncRoot
        $reposDir = Join-Path $SyncRoot 'repos'
        if (-not (Test-Path $reposDir -PathType Container)) {
            Write-Host "错误: repos 目录不存在: $reposDir" -ForegroundColor Red
            exit 2
        }
        $totalErr = 0
        $totalWarn = 0
        $reposChecked = 0
        $bareRepos = Get-ChildItem -Path $reposDir -Directory -Filter '*.git' -ErrorAction SilentlyContinue
        foreach ($bare in $bareRepos) {
            Write-Host "`n`n>>>>>>>>>> 仓库: $($bare.Name) <<<<<<<<<<" -ForegroundColor Magenta
            $r = Doctor-RunChecks -RepoPath $RepoPath -SyncRoot $SyncRoot -RemoteName $RemoteName -Mode $Mode
            $totalErr += $r.Err
            $totalWarn += $r.Warn
            $reposChecked++
        }
        Write-Host "`n========================================" -ForegroundColor Magenta
        Write-Host "  全部仓库汇总: 检查 $reposChecked 个仓库" -ForegroundColor Magenta
        Write-Host "  总错误: $totalErr, 总警告: $totalWarn" -ForegroundColor Magenta
        Write-Host "========================================" -ForegroundColor Magenta
        if ($totalErr -gt 0) { exit 1 } else { exit 0 }
    }

    $result = Doctor-RunChecks -RepoPath $RepoPath -SyncRoot $SyncRoot -RemoteName $RemoteName -Mode $Mode

    if ($Fix) {
        $fixed = $false
        if ($result.HasErrors -or $result.Warn -gt 0) {
            $tempFix = Doctor-FixTempFiles -BareRepoPath $result.BareRepoPath
            if ($tempFix) { $fixed = $true }

            if ($result.LooseStatus.Status -eq [CheckStatus]::ERR -or $result.LooseStatus.Status -eq [CheckStatus]::WARN) {
                $gcFix = Doctor-FixGC -RepoPath $result.RepoPath
                if ($gcFix) { $fixed = $true }
            }

            $backupResult = Doctor-CheckBackup -SyncRoot $result.SyncRoot -RepoName $result.RepoName
            if ($backupResult.Status -eq [CheckStatus]::ERR) {
                $bkFix = Doctor-FixBackup -RepoPath $result.RepoPath -SyncRoot $result.SyncRoot -RepoName $result.RepoName
                if ($bkFix) { $fixed = $true }
            }
        }
        if ($fixed) {
            Write-Host ''
            Write-Host '自动修复完成，建议重新运行 git-doctor 验证。' -ForegroundColor Green
        }
    }

    if ($result.HasErrors) {
        exit 1
    }
    exit 0
}
