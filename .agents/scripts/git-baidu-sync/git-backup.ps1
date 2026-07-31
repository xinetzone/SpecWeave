[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$RepoPath = '.',

    [Parameter()]
    [string]$SyncRoot = '',

    [Parameter()]
    [string]$RemoteName = '',

    [Parameter()]
    [string]$Output = '',

    [Parameter()]
    [bool]$Verify = $true,

    [Parameter()]
    [string]$Note = '',

    [Parameter()]
    [int]$Prune = 0,

    [switch]$List
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

function Format-FileSize {
    param([long]$SizeBytes)
    if ($SizeBytes -ge 1GB) {
        return "$([math]::Round($SizeBytes / 1GB, 2)) GB"
    }
    elseif ($SizeBytes -ge 1MB) {
        return "$([math]::Round($SizeBytes / 1MB, 2)) MB"
    }
    elseif ($SizeBytes -ge 1KB) {
        return "$([math]::Round($SizeBytes / 1KB, 2)) KB"
    }
    else {
        return "$SizeBytes bytes"
    }
}

function Get-BundleStats {
    param([string]$BundlePath)
    $stats = @{
        CommitCount = 0
        TagCount = 0
        BranchCount = 0
        Size = 0
        Verified = $false
    }

    if (Test-Path $BundlePath -PathType Leaf) {
        $stats.Size = (Get-Item $BundlePath).Length
    }

    $verifyResult = Invoke-GitCommand -Arguments @('bundle', 'verify', $BundlePath)
    $stats.Verified = $verifyResult.Success

    $headsResult = Invoke-GitCommand -Arguments @('bundle', 'list-heads', $BundlePath)
    if ($headsResult.Success) {
        $heads = @($headsResult.Output | Where-Object { $_ -match '\S' })
        $stats.BranchCount = @($heads | Where-Object { $_ -match 'refs/heads/' }).Count
        $stats.TagCount = @($heads | Where-Object { $_ -match 'refs/tags/' }).Count
    }

    $tempCloneDir = Join-Path $env:TEMP "git-bundle-stats-$(Get-Random)"
    try {
        $cloneResult = Invoke-GitCommand -Arguments @('clone', '--bare', '--quiet', $BundlePath, $tempCloneDir)
        if ($cloneResult.Success) {
            $countResult = Invoke-GitCommand -Arguments @('rev-list', '--all', '--count') -WorkingDirectory $tempCloneDir
            if ($countResult.Success) {
                $countStr = ($countResult.Output | Where-Object { $_ -match '\S' } | Select-Object -First 1)
                $stats.CommitCount = [int]$countStr
            }
        }
    }
    catch {}
    finally {
        if (Test-Path $tempCloneDir) {
            Remove-Item -Recurse -Force $tempCloneDir -ErrorAction SilentlyContinue
        }
    }

    return $stats
}

function Show-BackupList {
    param([string]$BackupDir)

    if (-not (Test-Path $BackupDir -PathType Container)) {
        Write-ColorMessage "备份目录不存在: $BackupDir" -Color $ColorWarning -Prefix 'WARN'
        return
    }

    $bundles = Get-ChildItem -Path $BackupDir -Filter '*.bundle' -File | Sort-Object LastWriteTime -Descending

    if ($bundles.Count -eq 0) {
        Write-ColorMessage "备份目录中没有 bundle 文件" -Color $ColorInfo -Prefix 'INFO'
        return
    }

    Write-Host ''
    Write-ColorMessage "=== 备份列表: $BackupDir ===" -Color $ColorHeader
    Write-Host ''
    Write-Host ("{0,-6} {1,-25} {2,-10} {3,-15} {4,-8} {5}" -f '#', '文件名', '大小', '创建时间', '验证', '备注')
    Write-Host ('-' * 90)

    $idx = 1
    foreach ($b in $bundles) {
        $noteFile = Join-Path $BackupDir ($b.BaseName + '.note')
        $noteContent = ''
        if (Test-Path $noteFile -PathType Leaf) {
            $noteContent = (Get-Content $noteFile -Raw -Encoding UTF8).Trim()
            if ($noteContent.Length -gt 25) {
                $noteContent = $noteContent.Substring(0, 22) + '...'
            }
        }

        $verifyResult = Invoke-GitCommand -Arguments @('bundle', 'verify', $b.FullName)
        $verifyStr = if ($verifyResult.Success) { '✅ 通过' } else { '❌ 失败' }
        $verifyColor = if ($verifyResult.Success) { $ColorSuccess } else { $ColorError }

        $sizeStr = Format-FileSize -SizeBytes $b.Length

        Write-Host ("{0,-6} {1,-25} {2,-10} {3,-15} " -f $idx, $b.Name, $sizeStr, $b.LastWriteTime.ToString('yyyy-MM-dd HH:mm')) -NoNewline
        Write-Host $verifyStr -ForegroundColor $verifyColor -NoNewline
        Write-Host (" {0}" -f $noteContent)
        $idx++
    }

    Write-Host ''
    Write-ColorMessage "共 $($bundles.Count) 个备份文件" -Color $ColorInfo
}

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-ColorMessage '  Git Bundle 备份工具' -Color $ColorHeader
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
    $backupDir = Join-Path $SyncRoot "backups\$repoName"

    $lockfilePath = Join-Path $SyncRoot "locks\$repoName.lock.json"
    if (Test-Path $lockfilePath -PathType Leaf) {
        Write-ColorMessage "警告: 仓库 $repoName 当前有锁持有，备份操作是只读的但可能遇到不一致状态" -Color $ColorWarning -Prefix 'WARN'
        $holderOp = Lock-ReadJsonField -FilePath $lockfilePath -Field 'operation'
        $holderHost = Lock-ReadJsonField -FilePath $lockfilePath -Field 'hostname'
        $holderTs = Lock-ReadJsonField -FilePath $lockfilePath -Field 'acquired_at'
        Write-ColorMessage "  持有者: $holderHost (op=$holderOp, since=$holderTs)" -Color $ColorWarning
        Write-Host ''
    }

    Write-ColorMessage "SyncRoot: $SyncRoot" -Color $ColorInfo
    Write-ColorMessage "仓库名: $repoName" -Color $ColorInfo
    Write-ColorMessage "Remote: $RemoteName -> $remoteUrl" -Color $ColorInfo
    Write-ColorMessage "备份目录: $backupDir" -Color $ColorInfo
    Write-Host ''

    if ($List) {
        Show-BackupList -BackupDir $backupDir
        exit 0
    }

    if ($Prune -gt 0) {
        Write-Step -Number 1 -Title "清理超过 $Prune 天的旧备份"
        if (-not (Test-Path $backupDir -PathType Container)) {
            Write-ColorMessage '备份目录不存在，无需清理' -Color $ColorInfo -Prefix 'INFO'
        }
        else {
            $cutoffDate = (Get-Date).AddDays(-$Prune)
            $keepPatterns = @('*永久*', '*keep*', '*monthly*')
            $oldBundles = Get-ChildItem -Path $backupDir -Filter '*.bundle' -File |
                Where-Object {
                    $_.LastWriteTime -lt $cutoffDate -and
                    -not ($keepPatterns | Where-Object { $_.Name -like $_ })
                }

            if ($oldBundles.Count -eq 0) {
                Write-ColorMessage "没有超过 $Prune 天的旧备份需要清理" -Color $ColorInfo -Prefix 'INFO'
            }
            else {
                Write-Host ''
                Write-ColorMessage "以下 $($oldBundles.Count) 个备份文件将被删除（超过 $Prune 天）：" -Color $ColorWarning
                foreach ($b in $oldBundles) {
                    $sizeStr = Format-FileSize -SizeBytes $b.Length
                    Write-Host "  - $($b.Name) ($sizeStr, 创建于 $($b.LastWriteTime.ToString('yyyy-MM-dd')))"
                }
                Write-Host ''
                Write-Host "确认删除？(输入 YES 继续，其他输入取消): " -NoNewline -ForegroundColor $ColorPrompt
                $confirm = Read-Host
                if ($confirm -eq 'YES') {
                    foreach ($b in $oldBundles) {
                        $noteFile = Join-Path $backupDir ($b.BaseName + '.note')
                        Remove-Item $b.FullName -Force -ErrorAction SilentlyContinue
                        if (Test-Path $noteFile) {
                            Remove-Item $noteFile -Force -ErrorAction SilentlyContinue
                        }
                    }
                    Write-ColorMessage "已删除 $($oldBundles.Count) 个旧备份文件" -Color $ColorSuccess -Prefix 'OK'
                }
                else {
                    Write-ColorMessage '用户取消，不执行删除' -Color $ColorInfo -Prefix 'INFO'
                }
            }
        }
        Write-Host ''
    }

    Write-Step -Number 2 -Title '确定备份输出路径'
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    if ($Output) {
        $bundlePath = $Output
        $bundleDir = Split-Path -Parent $bundlePath
        if ($bundleDir -and -not (Test-Path $bundleDir -PathType Container)) {
            New-Item -ItemType Directory -Path $bundleDir -Force | Out-Null
        }
    }
    else {
        if (-not (Test-Path $backupDir -PathType Container)) {
            New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
        }
        $bundlePath = Join-Path $backupDir "$timestamp.bundle"
    }
    Write-ColorMessage "Bundle 输出路径: $bundlePath" -Color $ColorInfo

    Write-Step -Number 3 -Title '执行 git bundle create --all'
    if (Test-Path $bundlePath -PathType Leaf) {
        Write-ColorMessage "文件已存在，将覆盖: $bundlePath" -Color $ColorWarning -Prefix 'WARN'
    }
    $bundleResult = Invoke-GitCommand -Arguments @('bundle', 'create', $bundlePath, '--all')
    if (-not $bundleResult.Success) {
        Write-ColorMessage 'Bundle 创建失败：' -Color $ColorError -Prefix 'ERR'
        $bundleResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        if (Test-Path $bundlePath) {
            Remove-Item $bundlePath -Force -ErrorAction SilentlyContinue
        }
        exit 1
    }
    $bundleResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
    Write-ColorMessage 'Bundle 创建完成' -Color $ColorSuccess -Prefix 'OK'

    if ($Verify) {
        Write-Step -Number 4 -Title '验证 Bundle 完整性'
        $verifyResult = Invoke-GitCommand -Arguments @('bundle', 'verify', $bundlePath)
        if ($verifyResult.Success) {
            Write-ColorMessage 'Bundle 验证通过' -Color $ColorSuccess -Prefix 'OK'
        }
        else {
            Write-ColorMessage 'Bundle 验证失败：' -Color $ColorError -Prefix 'ERR'
            $verifyResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
            exit 1
        }
    }
    else {
        Write-ColorMessage '已跳过验证（-Verify:$false）' -Color $ColorWarning -Prefix 'SKIP'
    }

    Write-Step -Number 5 -Title '统计备份信息'
    $stats = Get-BundleStats -BundlePath $bundlePath
    $sizeStr = Format-FileSize -SizeBytes $stats.Size
    Write-ColorMessage "备份大小: $sizeStr" -Color $ColorInfo
    Write-ColorMessage "提交数: $($stats.CommitCount)" -Color $ColorInfo
    Write-ColorMessage "分支数: $($stats.BranchCount)" -Color $ColorInfo
    Write-ColorMessage "标签数: $($stats.TagCount)" -Color $ColorInfo
    if ($stats.Verified) {
        Write-ColorMessage '验证状态: 通过' -Color $ColorSuccess -Prefix 'OK'
    }
    else {
        Write-ColorMessage '验证状态: 未通过' -Color $ColorError -Prefix 'ERR'
    }

    if ($Note) {
        Write-Step -Number 6 -Title '写入备份备注'
        $notePath = [System.IO.Path]::ChangeExtension($bundlePath, '.note')
        $noteContent = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`t$Note"
        Set-Content -Path $notePath -Value $noteContent -Encoding UTF8
        Write-ColorMessage "备注已写入: $notePath" -Color $ColorSuccess -Prefix 'OK'
        Write-ColorMessage "备注内容: $Note" -Color $ColorInfo
    }

    Write-Host ''
    Write-ColorMessage '=========================================' -Color $ColorSuccess
    Write-ColorMessage '  备份完成！' -Color $ColorSuccess
    Write-ColorMessage '=========================================' -Color $ColorSuccess
    Write-Host ''
    Write-ColorMessage "Bundle: $bundlePath" -Color $ColorSuccess
    Write-ColorMessage "大小: $sizeStr" -Color $ColorSuccess
    Write-ColorMessage "Commits: $($stats.CommitCount)" -Color $ColorSuccess
    Write-ColorMessage "Tags: $($stats.TagCount)" -Color $ColorSuccess
    if ($Note) {
        Write-ColorMessage "备注: $Note" -Color $ColorSuccess
    }
    Write-Host ''
}
finally {
    Pop-Location
}
