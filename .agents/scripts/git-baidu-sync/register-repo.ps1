[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [string]$RepoPath = '.',

    [Parameter(Mandatory = $true)]
    [string]$SyncRoot,

    [Parameter()]
    [string]$RepoName = '',

    [Parameter()]
    [string]$RemoteName = 'baidu',

    [switch]$SkipGC,

    [switch]$AggressiveGC,

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

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-ColorMessage '  百度网盘 Git 仓库注册工具（首台设备）' -Color $ColorHeader
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-Host ''

$RepoPath = Resolve-FullPath $RepoPath
$SyncRoot = Resolve-FullPath $SyncRoot

if (-not $RepoName) {
    $RepoName = Split-Path -Path $RepoPath -Leaf
}

$BareRepoPath = Join-Path $SyncRoot "repos\${RepoName}.git"
$BackupDir = Join-Path $SyncRoot "backups\${RepoName}"

Write-ColorMessage "本地仓库路径: $RepoPath" -Color $ColorInfo
Write-ColorMessage "网盘同步根目录: $SyncRoot" -Color $ColorInfo
Write-ColorMessage "仓库名称: $RepoName" -Color $ColorInfo
Write-ColorMessage "裸仓库路径: $BareRepoPath" -Color $ColorInfo
Write-ColorMessage "Remote 名称: $RemoteName" -Color $ColorInfo
Write-Host ''

Write-Step -Number 0 -Title '前置检查'

$dirsToCheck = @(
    (Join-Path $SyncRoot 'repos'),
    (Join-Path $SyncRoot 'backups'),
    (Join-Path $SyncRoot 'meta')
)
foreach ($dir in $dirsToCheck) {
    if (-not (Test-Path -Path $dir -PathType Container)) {
        Write-ColorMessage "目录不存在: $dir" -Color $ColorError -Prefix 'ERR'
        Write-ColorMessage '请先执行 init-sync-dir.ps1 初始化同步目录' -Color $ColorWarning -Prefix 'HINT'
        exit 1
    }
}
Write-ColorMessage '同步目录结构验证通过' -Color $ColorSuccess -Prefix 'OK'

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
Write-ColorMessage '本地 Git 仓库验证通过' -Color $ColorSuccess -Prefix 'OK'

try {
    $null = & git --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
}
catch {
    Write-ColorMessage '未检测到 Git，请先安装 Git' -Color $ColorError -Prefix 'ERR'
    exit 1
}
Write-ColorMessage ('Git 版本: ' + (& git --version)) -Color $ColorInfo -Prefix 'OK'

if (Test-Path -Path $BareRepoPath) {
    if ($Force) {
        Write-ColorMessage "裸仓库已存在，-Force 已指定，将覆盖: $BareRepoPath" -Color $ColorWarning -Prefix 'WARN'
        Remove-Item -Path $BareRepoPath -Recurse -Force
    }
    else {
        Write-ColorMessage "裸仓库已存在: $BareRepoPath" -Color $ColorWarning -Prefix 'WARN'
        $answer = Read-Host '是否删除并重新创建？(y/N)'
        if ($answer -eq 'y' -or $answer -eq 'Y') {
            Remove-Item -Path $BareRepoPath -Recurse -Force
            Write-ColorMessage '已删除旧裸仓库' -Color $ColorSuccess -Prefix 'DEL'
        }
        else {
            Write-ColorMessage '用户取消操作' -Color $ColorWarning -Prefix 'ABORT'
            exit 0
        }
    }
}

Write-Step -Number 1 -Title '本地仓库健康检查 (git fsck --full --strict)'

Push-Location $RepoPath
try {
    $fsckResult = Invoke-GitCommand -Arguments @('fsck', '--full', '--strict')
    if ($fsckResult.Success) {
        $hasErrors = $false
        foreach ($line in $fsckResult.Output) {
            if ($line -match '^error:|^fatal:|missing blob|missing tree|missing commit') {
                $hasErrors = $true
                Write-Host $line -ForegroundColor $ColorError
            }
        }
        if ($hasErrors) {
            Write-ColorMessage '本地仓库存在错误，请修复后重试' -Color $ColorError -Prefix 'ERR'
            exit 1
        }
        Write-ColorMessage '本地仓库健康检查通过' -Color $ColorSuccess -Prefix 'OK'
    }
    else {
        Write-ColorMessage 'git fsck 执行失败：' -Color $ColorError -Prefix 'ERR'
        $fsckResult.Output | ForEach-Object { Write-Host $_ }
        exit 1
    }
}
finally {
    Pop-Location
}

if (-not $SkipGC) {
    Write-Step -Number 2 -Title '本地 GC 优化'

    Push-Location $RepoPath
    try {
        $gcArgs = @('gc')
        if ($AggressiveGC) {
            Write-ColorMessage '使用 --aggressive 模式（首次初始化推荐，耗时较长）' -Color $ColorInfo
            $gcArgs += '--aggressive'
            $gcArgs += '--prune=now'
        }
        else {
            Write-ColorMessage '使用常规 GC 模式（使用 -AggressiveGC 启用深度优化）' -Color $ColorInfo
        }

        Write-ColorMessage '执行 GC，请稍候...' -Color $ColorInfo
        $gcResult = Invoke-GitCommand -Arguments $gcArgs
        if ($gcResult.Success) {
            $gcResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
            Write-ColorMessage 'GC 完成' -Color $ColorSuccess -Prefix 'OK'
        }
        else {
            Write-ColorMessage 'GC 过程出现警告（非致命错误，继续）：' -Color $ColorWarning -Prefix 'WARN'
            $gcResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorWarning }
        }
    }
    finally {
        Pop-Location
    }
}
else {
    Write-Step -Number 2 -Title '本地 GC 优化（已跳过 -SkipGC）'
    Write-ColorMessage 'GC 已跳过' -Color $ColorWarning -Prefix 'SKIP'
}

Write-Step -Number 3 -Title '创建裸仓库到网盘 (git clone --no-local --bare)'

Write-ColorMessage "目标: $BareRepoPath" -Color $ColorInfo
Push-Location $RepoPath
try {
    $cloneResult = Invoke-GitCommand -Arguments @('clone', '--no-local', '--bare', '.', $BareRepoPath)
    if ($cloneResult.Success) {
        $cloneResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
        Write-ColorMessage '裸仓库创建成功' -Color $ColorSuccess -Prefix 'OK'
    }
    else {
        Write-ColorMessage '裸仓库创建失败：' -Color $ColorError -Prefix 'ERR'
        $cloneResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        exit 1
    }
}
finally {
    Pop-Location
}

$bareCheck = & git -C $BareRepoPath rev-parse --is-bare-repository 2>$null
if ($bareCheck -ne 'true') {
    Write-ColorMessage '错误：创建的仓库不是裸仓库' -Color $ColorError -Prefix 'ERR'
    exit 1
}
Write-ColorMessage '裸仓库验证通过' -Color $ColorSuccess -Prefix 'OK'

Write-Step -Number 4 -Title '裸仓库跨平台安全配置'

$bareConfigs = @(
    @{ Key = 'core.filemode'; Value = 'false'; Desc = '忽略 Unix 权限位' },
    @{ Key = 'core.symlinks'; Value = 'false'; Desc = '不创建符号链接' },
    @{ Key = 'core.ignorecase'; Value = 'true'; Desc = '大小写不敏感' },
    @{ Key = 'gc.auto'; Value = '6700'; Desc = '自动 GC 阈值' },
    @{ Key = 'gc.autopacklimit'; Value = '1'; Desc = '保持最少 pack 文件' },
    @{ Key = 'core.preloadindex'; Value = 'true'; Desc = '并行预加载索引' }
)

foreach ($cfg in $bareConfigs) {
    $null = & git -C $BareRepoPath config --local $cfg.Key $cfg.Value 2>$null
    Write-ColorMessage ("{0} = {1} ({2})" -f $cfg.Key, $cfg.Value, $cfg.Desc) -Color $ColorSuccess -Prefix 'SET'
}

Push-Location $BareRepoPath
try {
    $bareFsck = Invoke-GitCommand -Arguments @('fsck', '--full')
    if ($bareFsck.Success) {
        Write-ColorMessage '裸仓库健康检查通过' -Color $ColorSuccess -Prefix 'OK'
    }
    else {
        Write-ColorMessage '裸仓库健康检查发现问题：' -Color $ColorWarning -Prefix 'WARN'
        $bareFsck.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorWarning }
    }
}
finally {
    Pop-Location
}

Write-Step -Number 5 -Title '为本地仓库添加 remote'

Push-Location $RepoPath
try {
    $existingRemotes = @()
    $remoteResult = Invoke-GitCommand -Arguments @('remote')
    if ($remoteResult.Success) {
        $existingRemotes = @($remoteResult.Output | Where-Object { $_ -ne '' })
    }

    if ($existingRemotes -contains $RemoteName) {
        if ($Force) {
            Write-ColorMessage "Remote '$RemoteName' 已存在，-Force 已指定，将更新URL" -Color $ColorWarning -Prefix 'WARN'
            $null = & git remote set-url $RemoteName $BareRepoPath
        }
        else {
            Write-ColorMessage "Remote '$RemoteName' 已存在" -Color $ColorWarning -Prefix 'WARN'
            $ans = Read-Host '是否更新URL？(y/N)'
            if ($ans -eq 'y' -or $ans -eq 'Y') {
                $null = & git remote set-url $RemoteName $BareRepoPath
            }
            else {
                Write-ColorMessage '跳过 remote 添加' -Color $ColorWarning -Prefix 'SKIP'
            }
        }
    }
    else {
        $null = & git remote add $RemoteName $BareRepoPath
        Write-ColorMessage "已添加 remote '$RemoteName' -> $BareRepoPath" -Color $ColorSuccess -Prefix 'ADD'
    }

    Write-Host ''
    Write-ColorMessage '当前 remote 列表：' -Color $ColorInfo
    & git remote -v | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
}
finally {
    Pop-Location
}

Write-Step -Number 6 -Title '推送所有分支和标签'

Push-Location $RepoPath
try {
    Write-ColorMessage "推送所有分支到 $RemoteName ..." -Color $ColorInfo
    $pushBranches = Invoke-GitCommand -Arguments @('push', $RemoteName, '--all')
    if ($pushBranches.Success) {
        $pushBranches.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
        Write-ColorMessage '分支推送完成' -Color $ColorSuccess -Prefix 'OK'
    }
    else {
        Write-ColorMessage '分支推送失败：' -Color $ColorError -Prefix 'ERR'
        $pushBranches.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        exit 1
    }

    Write-Host ''
    Write-ColorMessage "推送所有标签到 $RemoteName ..." -Color $ColorInfo
    $pushTags = Invoke-GitCommand -Arguments @('push', $RemoteName, '--tags')
    if ($pushTags.Success) {
        $pushTags.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
        Write-ColorMessage '标签推送完成' -Color $ColorSuccess -Prefix 'OK'
    }
    else {
        Write-ColorMessage '标签推送失败：' -Color $ColorError -Prefix 'ERR'
        $pushTags.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        exit 1
    }
}
finally {
    Pop-Location
}

Write-Step -Number 7 -Title '等待网盘同步'

Write-ColorMessage '================================================' -Color $ColorWarning
Write-ColorMessage '  重要：请等待百度网盘完成文件同步！' -Color $ColorWarning
Write-ColorMessage '  检查：' -Color $ColorWarning
Write-ColorMessage '  1. 百度网盘客户端显示同步完成（无上传中文件）' -Color $ColorWarning
Write-ColorMessage '  2. 裸仓库目录大小连续1分钟无变化' -Color $ColorWarning
Write-ColorMessage '  3. 目录中无 .tmp/.lock/downloading 等临时文件' -Color $ColorWarning
Write-ColorMessage '================================================' -Color $ColorWarning
Write-Host ''

$tempFiles = Get-ChildItem -Path $BareRepoPath -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match '\.tmp$|\.lock$|downloading$|\.part$|\.temp$'
}
if ($tempFiles) {
    Write-ColorMessage '检测到临时文件（网盘可能正在同步）：' -Color $ColorWarning -Prefix 'WARN'
    $tempFiles | Select-Object -First 5 | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor $ColorWarning }
}
else {
    Write-ColorMessage '未检测到临时文件' -Color $ColorInfo -Prefix 'INFO'
}

Write-Host ''
Read-Host '确认网盘同步完成后，按回车键继续创建备份...'

Write-Step -Number 8 -Title '创建初始 bundle 备份'

if (-not (Test-Path -Path $BackupDir -PathType Container)) {
    New-Item -Path $BackupDir -ItemType Directory -Force | Out-Null
    Write-ColorMessage "已创建备份目录: $BackupDir" -Color $ColorSuccess -Prefix 'CREATE'
}

$Timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$BundlePath = Join-Path $BackupDir "${Timestamp}.bundle"

Write-ColorMessage "创建 bundle: $BundlePath" -Color $ColorInfo
Push-Location $BareRepoPath
try {
    $bundleResult = Invoke-GitCommand -Arguments @('bundle', 'create', $BundlePath, '--all')
    if ($bundleResult.Success) {
        $bundleResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }

        $verifyResult = Invoke-GitCommand -Arguments @('bundle', 'verify', $BundlePath)
        if ($verifyResult.Success) {
            Write-ColorMessage 'Bundle 验证通过' -Color $ColorSuccess -Prefix 'OK'
        }
        else {
            Write-ColorMessage 'Bundle 验证警告：' -Color $ColorWarning -Prefix 'WARN'
            $verifyResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorWarning }
        }
    }
    else {
        Write-ColorMessage 'Bundle 创建失败：' -Color $ColorError -Prefix 'ERR'
        $bundleResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
        exit 1
    }
}
finally {
    Pop-Location
}

$bundleSize = (Get-Item $BundlePath).Length
$bundleSizeMB = [math]::Round($bundleSize / 1MB, 2)
Write-ColorMessage ("Bundle 大小: {0} MB" -f $bundleSizeMB) -Color $ColorInfo -Prefix 'INFO'

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorSuccess
Write-ColorMessage '  仓库注册完成！' -Color $ColorSuccess
Write-ColorMessage '=========================================' -Color $ColorSuccess
Write-Host ''
Write-ColorMessage "仓库名: $RepoName" -Color $ColorSuccess
Write-ColorMessage "裸仓库: $BareRepoPath" -Color $ColorSuccess
Write-ColorMessage "Remote: $RemoteName" -Color $ColorSuccess
Write-ColorMessage "备份: $BundlePath" -Color $ColorSuccess
Write-Host ''
Write-ColorMessage '后续步骤：' -Color $ColorHeader
Write-ColorMessage '1. 等待网盘完全同步后再在其他设备操作' -Color $ColorInfo
Write-ColorMessage "2. 新设备使用 clone-repo.ps1 -RepoName $RepoName -SyncRoot <sync-root> 克隆" -Color $ColorInfo
Write-ColorMessage "3. 日常推送使用: git push $RemoteName" -Color $ColorInfo
Write-Host ''
