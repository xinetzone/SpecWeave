# check-conflicts.ps1 - Git 网盘同步冲突检测 PowerShell 模块
# dot-source 使用作为库，或直接执行作为独立命令行工具
# 与 check-conflicts.sh 功能等价

$script:ConflictsVersion = "1.0.0"
$script:ConflictsSyncRoot = ""
$script:ConflictsColorEnabled = $true

function Conflicts-Colorize {
    param(
        [string]$Text,
        [string]$Color = "White"
    )
    if ($script:ConflictsColorEnabled) {
        Write-Host $Text -ForegroundColor $Color
    }
    else {
        Write-Host $Text
    }
}

function Conflicts-Err {
    param([string]$Message)
    Conflicts-Colorize "[conflicts ERROR] $Message" "Red"
}

function Conflicts-Warn {
    param([string]$Message)
    Conflicts-Colorize "[conflicts WARN] $Message" "Yellow"
}

function Conflicts-Info {
    param([string]$Message)
    Conflicts-Colorize "[conflicts] $Message" "Gray"
}

function Conflicts-Critical {
    param([string]$Message)
    Conflicts-Colorize "[conflicts CRITICAL] $Message" "Red"
}

function Conflicts-IsConflictFilename {
    param([string]$Filename)

    if ($Filename -match '\s\(\d+\)(\.[^.]*)?$') { return $true }
    if ($Filename -match '冲突') { return $true }
    if ($Filename -match '\s\(来自\s') { return $true }
    if ($Filename -match '冲突副本') { return $true }

    return $false
}

function Conflicts-IsTemporaryFile {
    param([string]$Filename)

    if ($Filename -match '\.(tmp|temp|pack-tmp)$') { return $true }
    if ($Filename -like 'tmp_pack_*') { return $true }

    return $false
}

function Conflicts-IsLockFile {
    param([string]$Filename)

    if ($Filename -match '\.lock$') { return $true }
    return $false
}

function Conflicts-IsHexString {
    param(
        [string]$Str,
        [int]$Length
    )
    if ($Str.Length -ne $Length) { return $false }
    return $Str -match "^[0-9a-fA-F]{$Length}$"
}

function Conflicts-Classify {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string]$RepoRoot = ""
    )

    $filename = Split-Path $FilePath -Leaf
    $dirPath = Split-Path $FilePath -Parent
    $relPath = $FilePath
    if ($RepoRoot -and $FilePath.StartsWith($RepoRoot)) {
        $relPath = $FilePath.Substring($RepoRoot.Length).TrimStart('\', '/')
    }
    $relPath = $relPath -replace '\\', '/'

    $isConflict = Conflicts-IsConflictFilename -Filename $filename
    $isTmp = Conflicts-IsTemporaryFile -Filename $filename
    $isLock = Conflicts-IsLockFile -Filename $filename

    if ($isConflict) {
        $relLower = $relPath.ToLower()

        if ($relLower -like 'objects/pack/*') {
            return "critical"
        }
        if ($relLower -match '^objects/[0-9a-f]{2}/') {
            $nameNoExt = [System.IO.Path]::GetFileNameWithoutExtension($filename)
            $baseName = $filename
            if ($filename -match '^(.+?)\s*\(\d+\)') { $baseName = $Matches[1] }
            if ($baseName -match '^([0-9a-fA-F]{38})') {
                if (-not (Conflicts-IsHexString -Str $Matches[1] -Length 38)) {
                    return "critical"
                }
            }
            else {
                return "critical"
            }
        }
        if ($filename -like 'HEAD*' -and ($relLower -eq 'head' -or $relLower -like 'head (*')) {
            return "critical"
        }
        if ($filename -like 'packed-refs*') {
            return "critical"
        }

        if ($relLower -like 'refs/*') {
            return "warning"
        }
        if ($relLower -eq 'config' -or $filename -like 'config (*') {
            return "warning"
        }
        if ($relLower -like 'hooks/*') {
            return "warning"
        }

        return "warning"
    }

    if ($isTmp) {
        return "info"
    }

    if ($isLock) {
        $isInLocksDir = $relPath.ToLower() -like 'locks/*'
        if ($isInLocksDir) {
            return "normal"
        }
        return "warning"
    }

    if ($relLower -like 'logs/*' -and (Conflicts-IsConflictFilename -Filename $filename -or $isTmp)) {
        return "info"
    }

    $relLower2 = $relPath.ToLower()
    if ($relLower2 -match '^objects/[0-9a-f]{2}/') {
        $objName = $filename
        if (-not (Conflicts-IsHexString -Str $objName -Length 38)) {
            if ($objName -match '^([0-9a-fA-F]{38})') {
                return "warning"
            }
            if ($objName -eq 'info' -or $objName -eq 'pack') {
                return "normal"
            }
            return "warning"
        }
    }
    if ($relLower2 -like 'objects/pack/*') {
        if ($filename -match '^pack-([0-9a-fA-F]{40})\.(pack|idx|keep|rev)$') {
            return "normal"
        }
        if ($filename -eq 'pack' -or $filename -eq 'info') {
            return "normal"
        }
        return "warning"
    }

    return "normal"
}

function Conflicts-FormatFileSize {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return "{0:N2} GB" -f ($Bytes / 1GB) }
    if ($Bytes -ge 1MB) { return "{0:N2} MB" -f ($Bytes / 1MB) }
    if ($Bytes -ge 1KB) { return "{0:N2} KB" -f ($Bytes / 1KB) }
    return "$Bytes B"
}

function Conflicts-GetFileInfo {
    param([string]$FilePath)

    if (-not (Test-Path $FilePath -PathType Leaf)) {
        return $null
    }

    try {
        $item = Get-Item $FilePath -ErrorAction Stop
        return [PSCustomObject]@{
            Path         = $FilePath
            Name         = $item.Name
            Size         = $item.Length
            SizeReadable = Conflicts-FormatFileSize -Bytes $item.Length
            ModifiedTime = $item.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
            Classification = "normal"
            Suggestion   = ""
        }
    }
    catch {
        return $null
    }
}

function Conflicts-GetSuggestion {
    param([string]$Classification)

    switch ($Classification) {
        "critical" { return "🛑 严重！立即停止同步，从备份恢复仓库，不要手动删除" }
        "warning" { return "⚠️ 警告：确认无Git进程后人工检查处理" }
        "info" { return "ℹ️ 提示：可安全清理的临时文件或无害冲突副本" }
        default { return "" }
    }
}

function Conflicts-Scan {
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$BareRepoPath
    )

    if (-not (Test-Path $BareRepoPath -PathType Container)) {
        Conflicts-Err "裸仓库路径不存在: $BareRepoPath"
        return $null
    }

    $repoItem = Get-Item $BareRepoPath -ErrorAction SilentlyContinue
    if (-not $repoItem) {
        Conflicts-Err "无法访问仓库路径: $BareRepoPath"
        return $null
    }

    $repoFullPath = $repoItem.FullName.TrimEnd('\', '/')
    $results = [System.Collections.ArrayList]::new()
    $totalScanned = 0

    Conflicts-Info "开始扫描裸仓库: $repoFullPath"

    try {
        $files = Get-ChildItem -Path $repoFullPath -Recurse -File -ErrorAction Stop
        foreach ($file in $files) {
            $totalScanned++
            $class = Conflicts-Classify -FilePath $file.FullName -RepoRoot $repoFullPath
            if ($class -ne "normal") {
                $info = [PSCustomObject]@{
                    Path           = $file.FullName
                    RelativePath   = $file.FullName.Substring($repoFullPath.Length).TrimStart('\', '/')
                    Name           = $file.Name
                    Size           = $file.Length
                    SizeReadable   = Conflicts-FormatFileSize -Bytes $file.Length
                    ModifiedTime   = $file.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
                    Classification = $class
                    Suggestion     = Conflicts-GetSuggestion -Classification $class
                }
                [void]$results.Add($info)
            }
        }
    }
    catch {
        Conflicts-Warn "扫描过程中遇到错误: $_"
    }

    $critical = @($results | Where-Object { $_.Classification -eq "critical" })
    $warnings = @($results | Where-Object { $_.Classification -eq "warning" })
    $infos = @($results | Where-Object { $_.Classification -eq "info" })

    return [PSCustomObject]@{
        RepoPath        = $repoFullPath
        TotalScanned    = $totalScanned
        TotalConflicts  = $results.Count
        CriticalCount   = $critical.Count
        WarningCount    = $warnings.Count
        InfoCount       = $infos.Count
        CriticalFiles   = $critical
        WarningFiles    = $warnings
        InfoFiles       = $infos
        AllFiles        = $results.ToArray()
        HasCritical     = ($critical.Count -gt 0)
    }
}

function Conflicts-ScanSyncRoot {
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$SyncRootPath
    )

    if (-not (Test-Path $SyncRootPath -PathType Container)) {
        Conflicts-Err "同步根目录不存在: $SyncRootPath"
        return $null
    }

    $reposDir = Join-Path $SyncRootPath "repos"
    if (-not (Test-Path $reposDir -PathType Container)) {
        Conflicts-Err "repos 目录不存在: $reposDir"
        return $null
    }

    $allResults = [System.Collections.ArrayList]::new()
    $totalCritical = 0
    $totalWarnings = 0
    $totalInfos = 0
    $totalScanned = 0

    $repos = Get-ChildItem -Path $reposDir -Directory -Filter "*.git" -ErrorAction SilentlyContinue
    foreach ($repo in $repos) {
        $result = Conflicts-Scan -BareRepoPath $repo.FullName
        if ($result) {
            [void]$allResults.Add($result)
            $totalCritical += $result.CriticalCount
            $totalWarnings += $result.WarningCount
            $totalInfos += $result.InfoCount
            $totalScanned += $result.TotalScanned
        }
    }

    return [PSCustomObject]@{
        SyncRoot        = $SyncRootPath
        ReposScanned    = $allResults.Count
        TotalScanned    = $totalScanned
        TotalCritical   = $totalCritical
        TotalWarnings   = $totalWarnings
        TotalInfos      = $totalInfos
        TotalConflicts  = $totalCritical + $totalWarnings + $totalInfos
        RepoResults     = $allResults.ToArray()
        HasCritical     = ($totalCritical -gt 0)
    }
}

function Conflicts-GenerateReport {
    param(
        [Parameter(Mandatory = $true)]
        [object]$ScanResult
    )

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Git 网盘同步冲突检测报告" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan

    if ($ScanResult.PSObject.Properties.Name -contains "RepoResults") {
        Write-Host "  同步根目录: $($ScanResult.SyncRoot)"
        Write-Host "  扫描仓库数: $($ScanResult.ReposScanned)"
    }
    else {
        Write-Host "  仓库路径:   $($ScanResult.RepoPath)"
    }
    Write-Host "  扫描文件数: $($ScanResult.TotalScanned)"
    Write-Host "  冲突文件数: $($ScanResult.TotalConflicts)"
    Write-Host "    严重(CRITICAL): $($ScanResult.CriticalCount)" -ForegroundColor $(if ($ScanResult.CriticalCount -gt 0) { "Red" } else { "Green" })
    Write-Host "    警告(WARNING):  $($ScanResult.WarningCount)" -ForegroundColor $(if ($ScanResult.WarningCount -gt 0) { "Yellow" } else { "Gray" })
    Write-Host "    提示(INFO):     $($ScanResult.InfoCount)" -ForegroundColor $(if ($ScanResult.InfoCount -gt 0) { "Blue" } else { "Gray" })
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""

    $processSingleRepo = {
        param($result)
        if ($result.CriticalCount -gt 0) {
            Write-Host "--- 🔴 严重冲突 (CRITICAL) - 必须处理 ---" -ForegroundColor Red
            foreach ($f in $result.CriticalFiles) {
                Write-Host "  [CRITICAL] $($f.RelativePath)" -ForegroundColor Red
                Write-Host "    大小: $($f.SizeReadable)  修改时间: $($f.ModifiedTime)" -ForegroundColor DarkRed
                Write-Host "    建议: $($f.Suggestion)" -ForegroundColor DarkRed
                Write-Host ""
            }
        }

        if ($result.WarningCount -gt 0) {
            Write-Host "--- 🟡 警告 (WARNING) - 需要检查 ---" -ForegroundColor Yellow
            foreach ($f in $result.WarningFiles) {
                Write-Host "  [WARNING]  $($f.RelativePath)" -ForegroundColor Yellow
                Write-Host "    大小: $($f.SizeReadable)  修改时间: $($f.ModifiedTime)" -ForegroundColor DarkYellow
                Write-Host "    建议: $($f.Suggestion)" -ForegroundColor DarkYellow
                Write-Host ""
            }
        }

        if ($result.InfoCount -gt 0) {
            Write-Host "--- 🔵 提示 (INFO) - 可清理 ---" -ForegroundColor Blue
            foreach ($f in $result.InfoFiles) {
                Write-Host "  [INFO]     $($f.RelativePath)" -ForegroundColor Blue
                Write-Host "    大小: $($f.SizeReadable)  修改时间: $($f.ModifiedTime)" -ForegroundColor DarkBlue
                Write-Host "    建议: $($f.Suggestion)" -ForegroundColor DarkBlue
                Write-Host ""
            }
        }
    }

    if ($ScanResult.PSObject.Properties.Name -contains "RepoResults") {
        foreach ($repoResult in $ScanResult.RepoResults) {
            if ($repoResult.TotalConflicts -gt 0) {
                Write-Host ""
                Write-Host ">>> 仓库: $(Split-Path $repoResult.RepoPath -Leaf)" -ForegroundColor Magenta
                & $processSingleRepo $repoResult
            }
        }
    }
    else {
        & $processSingleRepo $ScanResult
    }

    if ($ScanResult.HasCritical) {
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "  🛑 发现严重冲突！检测结果为失败状态。" -ForegroundColor Red
        Write-Host "  请立即停止同步操作，从备份恢复仓库。" -ForegroundColor Red
        Write-Host "  不要尝试自动清理 objects/pack/ 下的冲突文件！" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
    }
    elseif ($ScanResult.TotalConflicts -eq 0) {
        Write-Host "  ✅ 未发现冲突文件，仓库状态正常。" -ForegroundColor Green
    }
    else {
        Write-Host "  ⚠️  发现非严重冲突，建议检查后处理。" -ForegroundColor Yellow
    }
    Write-Host ""
}

function Conflicts-EnsureLogDir {
    param([string]$SyncRoot)

    $logsDir = $null
    if ($SyncRoot) {
        $logsDir = Join-Path $SyncRoot "logs"
    }
    else {
        $logsDir = Join-Path $PSScriptRoot "..\..\logs"
    }
    $logsDir = [System.IO.Path]::GetFullPath($logsDir)
    if (-not (Test-Path $logsDir)) {
        try {
            New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
        }
        catch {
            $logsDir = $env:TEMP
        }
    }
    return $logsDir
}

function Conflicts-BackupFileList {
    param(
        [string[]]$FilePaths,
        [string]$LogDir
    )

    $timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
    $logFile = Join-Path $LogDir "cleanup-$timestamp.log"
    $lines = @(
        "# Cleanup log created at $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
        "# Files to be deleted:",
        ""
    )
    $lines += $FilePaths
    $lines | Set-Content -Path $logFile -Encoding UTF8
    return $logFile
}

function Conflicts-CanAutoClean {
    param([object]$FileInfo)

    if ($FileInfo.Classification -eq "info") {
        if ($FileInfo.Name -match '\.(tmp|temp|pack-tmp)$') { return $true }
        if ($FileInfo.Name -like 'tmp_pack_*') { return $true }
    }
    if ($FileInfo.Name -match '\.lock$') {
        $relLower = $FileInfo.RelativePath.ToLower()
        if ($relLower -notlike 'locks/*') {
            return $true
        }
    }
    return $false
}

function Conflicts-Clean {
    param(
        [Parameter(Mandatory = $true)]
        [object]$ScanResult,
        [switch]$AutoClean,
        [string]$SyncRoot = ""
    )

    if ($ScanResult.HasCritical) {
        Conflicts-Err "存在严重冲突，禁止清理！请先从备份恢复。"
        return $false
    }

    $allToProcess = @($ScanResult.AllFiles)
    if ($allToProcess.Count -eq 0) {
        Conflicts-Info "没有需要清理的文件。"
        return $true
    }

    $logsDir = Conflicts-EnsureLogDir -SyncRoot $SyncRoot
    $deleted = 0
    $skipped = 0

    foreach ($fileInfo in $allToProcess) {
        $shouldDelete = $false

        if ($AutoClean) {
            if (Conflicts-CanAutoClean -FileInfo $fileInfo) {
                $shouldDelete = $true
                Conflicts-Info "[AutoClean] 将删除: $($fileInfo.RelativePath)"
            }
            else {
                Conflicts-Info "[AutoClean] 跳过: $($fileInfo.RelativePath)"
                $skipped++
                continue
            }
        }
        else {
            Write-Host ""
            Write-Host "文件: $($fileInfo.RelativePath)" -ForegroundColor $(if ($fileInfo.Classification -eq "warning") { "Yellow" } else { "Blue" })
            Write-Host "  类型: $($fileInfo.Classification)"
            Write-Host "  大小: $($fileInfo.SizeReadable)  修改时间: $($fileInfo.ModifiedTime)"
            Write-Host "  建议: $($fileInfo.Suggestion)"
            $answer = Read-Host "  确认删除此文件？(y/N)"
            if ($answer -eq 'y' -or $answer -eq 'Y') {
                $shouldDelete = $true
            }
            else {
                $skipped++
                continue
            }
        }

        if ($shouldDelete -and (Test-Path $fileInfo.Path -PathType Leaf)) {
            try {
                Remove-Item $fileInfo.Path -Force -ErrorAction Stop
                $deleted++
                Conflicts-Info "已删除: $($fileInfo.RelativePath)"
            }
            catch {
                Conflicts-Warn "删除失败 $($fileInfo.RelativePath): $_"
            }
        }
    }

    $backupPaths = $allToProcess | Where-Object { Test-Path $_.Path -PathType Leaf } | ForEach-Object { $_.Path }
    if ($backupPaths.Count -gt 0) {
        $logFile = Conflicts-BackupFileList -FilePaths $allToProcess.Path -LogDir $logsDir
        Conflicts-Info "清理日志已保存到: $logFile"
    }

    Write-Host ""
    Write-Host "清理完成: 已删除 $deleted 个文件，跳过 $skipped 个文件。"

    if ($deleted -gt 0) {
        $repoPath = ""
        if ($ScanResult.PSObject.Properties.Name -contains "RepoPath") {
            $repoPath = $ScanResult.RepoPath
        }
        if ($repoPath -and (Test-Path $repoPath -PathType Container)) {
            Conflicts-Info "建议执行 git fsck --full 验证仓库完整性。"
        }
    }

    return $true
}

function Conflicts-Init {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true, Position = 0)]
        [string]$SyncRoot
    )

    if (-not (Test-Path $SyncRoot -PathType Container)) {
        Conflicts-Err "同步根目录不存在: $SyncRoot"
        return $false
    }

    $script:ConflictsSyncRoot = $SyncRoot
    Conflicts-Info "冲突检测系统初始化完成 (sync_root=$SyncRoot)"
    return $true
}

function Conflicts-ShowUsage {
    Write-Host @"
check-conflicts.ps1 - Git 网盘同步冲突检测工具 v$($script:ConflictsVersion)

用法:
  .\check-conflicts.ps1 [选项]

选项（独立执行时）:
  -SyncRoot <路径>    网盘同步根目录（必须与-RepoName或-All合用）
  -RepoName <名称>    扫描指定仓库名（SyncRoot下repos/<name>.git）
  -Path <路径>        直接指定裸仓库路径扫描
  -All                扫描SyncRoot下所有仓库
  -Clean              交互式清理模式，逐个询问是否删除
  -AutoClean          自动清理明确安全的临时文件(.tmp/.pack-tmp等)
  -NoColor            禁用彩色输出

作为库使用（dot-source）:
  . .\check-conflicts.ps1

  Conflicts-Init <SyncRoot>              # 初始化
  Conflicts-Classify <FilePath> [Repo]   # 分类单个文件(normal/critical/warning/info)
  Conflicts-Scan <BareRepoPath>          # 扫描单个裸仓库，返回结果对象
  Conflicts-ScanSyncRoot <SyncRoot>      # 扫描同步空间所有仓库
  Conflicts-GenerateReport <Result>      # 生成可读报告
  Conflicts-Clean <Result> [-AutoClean]  # 清理冲突文件

退出码:
  0 = 无冲突或仅提示/警告
  1 = 发现严重冲突
  2 = 参数错误/执行错误

示例:
  # 扫描单个仓库
  .\check-conflicts.ps1 -Path D:\git-sync\repos\myproject.git

  # 扫描所有仓库
  .\check-conflicts.ps1 -All -SyncRoot D:\BaiduSync\git-sync

  # 交互式清理
  .\check-conflicts.ps1 -RepoName myproject -SyncRoot D:\git-sync -Clean

  # 自动清理临时文件
  .\check-conflicts.ps1 -All -SyncRoot D:\git-sync -AutoClean
"@
}

$script:ConflictsIsRunningDirectly = $false
if ($MyInvocation.InvocationName -ne '.' -and $MyInvocation.InvocationName -ne '&') {
    $script:ConflictsIsRunningDirectly = $true
}
elseif ($MyInvocation.MyCommand.Path -eq $PSCommandPath) {
    $line = $MyInvocation.Line
    if ($line -notmatch '\.\s+.*check-conflicts\.ps1') {
        $script:ConflictsIsRunningDirectly = $true
    }
}

if ($script:ConflictsIsRunningDirectly) {
    $paramSyncRoot = ""
    $paramRepoName = ""
    $paramPath = ""
    $paramAll = $false
    $paramClean = $false
    $paramAutoClean = $false
    $paramNoColor = $false

    for ($i = 0; $i -lt $args.Count; $i++) {
        switch -Regex ($args[$i]) {
            '^-SyncRoot$' { $i++; if ($i -lt $args.Count) { $paramSyncRoot = $args[$i] } }
            '^-RepoName$' { $i++; if ($i -lt $args.Count) { $paramRepoName = $args[$i] } }
            '^-Path$' { $i++; if ($i -lt $args.Count) { $paramPath = $args[$i] } }
            '^-All$' { $paramAll = $true }
            '^-Clean$' { $paramClean = $true }
            '^-AutoClean$' { $paramAutoClean = $true }
            '^-NoColor$' { $paramNoColor = $true; $script:ConflictsColorEnabled = $false }
            '^--?h(elp)?$' { Conflicts-ShowUsage; exit 0 }
            default { }
        }
    }

    if ($paramNoColor) {
        $script:ConflictsColorEnabled = $false
    }

    $hasTarget = $false
    $scanResult = $null

    if ($paramPath) {
        $hasTarget = $true
        $scanResult = Conflicts-Scan -BareRepoPath $paramPath
    }
    elseif ($paramAll -and $paramSyncRoot) {
        $hasTarget = $true
        $scanResult = Conflicts-ScanSyncRoot -SyncRootPath $paramSyncRoot
    }
    elseif ($paramRepoName -and $paramSyncRoot) {
        $hasTarget = $true
        $repoPath = Join-Path (Join-Path $paramSyncRoot "repos") "$paramRepoName.git"
        $scanResult = Conflicts-Scan -BareRepoPath $repoPath
    }

    if (-not $hasTarget) {
        Conflicts-ShowUsage
        exit 2
    }

    if (-not $scanResult) {
        Conflicts-Err "扫描失败，请检查路径是否正确。"
        exit 2
    }

    Conflicts-GenerateReport -ScanResult $scanResult

    if ($paramClean -or $paramAutoClean) {
        Write-Host ""
        if ($paramAutoClean) {
            Conflicts-Info "=== AutoClean 模式：仅清理明确安全的临时文件 ==="
        }
        else {
            Conflicts-Info "=== Clean 模式：交互式清理 ==="
        }
        Conflicts-Clean -ScanResult $scanResult -AutoClean:$paramAutoClean -SyncRoot $paramSyncRoot
    }

    if ($scanResult.HasCritical) {
        exit 1
    }
    exit 0
}
