[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$RepoName,

    [Parameter(Mandatory = $true)]
    [string]$SyncRoot,

    [Parameter(Position = 0)]
    [string]$TargetPath = '',

    [Parameter()]
    [string]$RemoteName = 'baidu',

    [switch]$RenameOriginToBaidu,

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
    if ([string]::IsNullOrEmpty($Path)) { return '' }
    if ([System.IO.Path]::IsPathRooted($Path)) {
        return [System.IO.Path]::GetFullPath($Path)
    }
    return [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $Path))
}

function Get-DeviceId {
    $os = if ($IsWindows -or $env:OS -eq 'Windows_NT') { 'win' }
    elseif ($IsMacOS) { 'mac' }
    elseif ($IsLinux) { 'linux' }
    else { 'unknown' }

    $hostname = $env:COMPUTERNAME
    if ([string]::IsNullOrEmpty($hostname)) { $hostname = hostname 2>$null }
    if ([string]::IsNullOrEmpty($hostname)) { $hostname = 'device' }

    $hostnameClean = $hostname.ToLower() -replace '[^a-z0-9-]', '-'
    return "$os-$hostnameClean"
}

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-ColorMessage '  百度网盘 Git 仓库克隆工具（新设备）' -Color $ColorHeader
Write-ColorMessage '=========================================' -Color $ColorHeader
Write-Host ''

$SyncRoot = Resolve-FullPath $SyncRoot
$BareRepoPath = Join-Path $SyncRoot "repos\${RepoName}.git"
$DevicesJson = Join-Path $SyncRoot "meta\devices.json"

if ([string]::IsNullOrEmpty($TargetPath)) {
    $TargetPath = Join-Path (Get-Location) $RepoName
}
$TargetPath = Resolve-FullPath $TargetPath

Write-ColorMessage "仓库名称: $RepoName" -Color $ColorInfo
Write-ColorMessage "网盘同步根目录: $SyncRoot" -Color $ColorInfo
Write-ColorMessage "裸仓库路径: $BareRepoPath" -Color $ColorInfo
Write-ColorMessage "本地目标路径: $TargetPath" -Color $ColorInfo
Write-Host ''

Write-Step -Number 0 -Title '前置检查'

if (-not (Test-Path -Path (Join-Path $SyncRoot 'repos') -PathType Container)) {
    Write-ColorMessage "同步目录不存在或未初始化: $SyncRoot" -Color $ColorError -Prefix 'ERR'
    Write-ColorMessage '请先执行 init-sync-dir.ps1 初始化同步目录，并等待网盘完成首次全量同步' -Color $ColorWarning -Prefix 'HINT'
    exit 1
}
Write-ColorMessage '同步目录验证通过' -Color $ColorSuccess -Prefix 'OK'

if (-not (Test-Path -Path $BareRepoPath -PathType Container)) {
    Write-ColorMessage "裸仓库不存在: $BareRepoPath" -Color $ColorError -Prefix 'ERR'
    Write-ColorMessage '请确认：' -Color $ColorWarning -Prefix 'HINT'
    Write-ColorMessage '  1. 网盘已完成首次全量同步' -Color $ColorWarning
    Write-ColorMessage '  2. RepoName 参数正确' -Color $ColorWarning
    Write-ColorMessage "  3. repos/ 目录下能看到 $RepoName.git 文件夹" -Color $ColorWarning
    exit 1
}
Write-ColorMessage '裸仓库目录存在' -Color $ColorSuccess -Prefix 'OK'

try {
    $null = & git --version 2>$null
    if ($LASTEXITCODE -ne 0) { throw }
}
catch {
    Write-ColorMessage '未检测到 Git，请先安装 Git' -Color $ColorError -Prefix 'ERR'
    exit 1
}
Write-ColorMessage ('Git 版本: ' + (& git --version)) -Color $ColorInfo -Prefix 'OK'

if ((Test-Path -Path $TargetPath) -and -not $Force) {
    $targetItems = Get-ChildItem -Path $TargetPath -ErrorAction SilentlyContinue
    if ($targetItems -and $targetItems.Count -gt 0) {
        Write-ColorMessage "目标路径已存在且非空: $TargetPath" -Color $ColorWarning -Prefix 'WARN'
        $ans = Read-Host '是否继续？可能覆盖文件 (y/N)'
        if ($ans -ne 'y' -and $ans -ne 'Y') {
            Write-ColorMessage '用户取消操作' -Color $ColorWarning -Prefix 'ABORT'
            exit 0
        }
    }
}

Write-Step -Number 1 -Title '检测临时文件（确认网盘同步完成）'

$tempFiles = @(Get-ChildItem -Path $BareRepoPath -Recurse -ErrorAction SilentlyContinue | Where-Object {
    $_.Name -match '\.tmp$|\.lock$|downloading$|\.part$|\.temp$|\.crdownload$|\.!ut$'
})

if ($tempFiles.Count -gt 0) {
    Write-ColorMessage "检测到 $($tempFiles.Count) 个临时文件（网盘可能还在同步）：" -Color $ColorWarning -Prefix 'WARN'
    $tempFiles | Select-Object -First 10 | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor $ColorWarning }
    Write-Host ''
    Write-ColorMessage '临时文件可能意味着网盘尚未完成同步，克隆可能导致仓库损坏！' -Color $ColorError -Prefix 'DANGER'

    if ($Force) {
        Write-ColorMessage '-Force 已指定，继续执行（不推荐）' -Color $ColorWarning -Prefix 'WARN'
    }
    else {
        $ans = Read-Host '是否继续？强烈建议等待同步完成 (y/N)'
        if ($ans -ne 'y' -and $ans -ne 'Y') {
            Write-ColorMessage '用户取消操作，请等待网盘同步完成后重试' -Color $ColorWarning -Prefix 'ABORT'
            exit 0
        }
    }
}
else {
    Write-ColorMessage '未检测到临时文件，同步可能已完成' -Color $ColorSuccess -Prefix 'OK'
}

$packDir = Join-Path $BareRepoPath 'objects\pack'
if (-not (Test-Path -Path $packDir -PathType Container)) {
    Write-ColorMessage "pack 目录不存在: $packDir" -Color $ColorError -Prefix 'ERR'
    Write-ColorMessage '裸仓库可能不完整，请等待网盘同步完成' -Color $ColorWarning -Prefix 'HINT'
    exit 1
}

$packFiles = @(Get-ChildItem -Path $packDir -Filter '*.pack' -ErrorAction SilentlyContinue)
if ($packFiles.Count -eq 0) {
    Write-ColorMessage '未找到 pack 文件，裸仓库可能不完整' -Color $ColorError -Prefix 'ERR'
    exit 1
}
foreach ($pf in $packFiles) {
    if ($pf.Length -eq 0) {
        Write-ColorMessage "pack 文件大小为 0: $($pf.FullName)" -Color $ColorError -Prefix 'ERR'
        exit 1
    }
}
Write-ColorMessage "找到 $($packFiles.Count) 个 pack 文件" -Color $ColorSuccess -Prefix 'OK'

Write-Step -Number 2 -Title '裸仓库健康检查 (git fsck --full)'

Write-ColorMessage '执行 fsck，请稍候...' -Color $ColorInfo
Push-Location $BareRepoPath
try {
    $fsckResult = Invoke-GitCommand -Arguments @('fsck', '--full')
    $hasFsckErrors = $false
    foreach ($line in $fsckResult.Output) {
        if ($line -match '^error:|^fatal:|missing blob|missing tree|missing commit') {
            $hasFsckErrors = $true
            Write-Host $line -ForegroundColor $ColorError
        }
    }
    if ($hasFsckErrors -or -not $fsckResult.Success) {
        Write-ColorMessage '裸仓库健康检查失败！可能是网盘同步未完成或仓库损坏。' -Color $ColorError -Prefix 'ERR'
        Write-ColorMessage '建议：等待网盘继续同步后重试，或检查首台设备是否正确注册。' -Color $ColorWarning -Prefix 'HINT'
        exit 1
    }
    Write-ColorMessage '裸仓库健康检查通过' -Color $ColorSuccess -Prefix 'OK'
}
finally {
    Pop-Location
}

Write-Step -Number 3 -Title '克隆仓库到本地'

if (Test-Path -Path $TargetPath) {
    if ((Get-ChildItem -Path $TargetPath -ErrorAction SilentlyContinue | Measure-Object).Count -gt 0) {
        if ($Force) {
            Write-ColorMessage "目标目录非空，-Force 已指定，删除后重新克隆: $TargetPath" -Color $ColorWarning -Prefix 'WARN'
            Remove-Item -Path $TargetPath -Recurse -Force
        }
    }
}

Write-ColorMessage "克隆 $BareRepoPath -> $TargetPath" -Color $ColorInfo
$cloneResult = Invoke-GitCommand -Arguments @('clone', $BareRepoPath, $TargetPath)
if (-not $cloneResult.Success) {
    Write-ColorMessage '克隆失败：' -Color $ColorError -Prefix 'ERR'
    $cloneResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorError }
    exit 1
}
$cloneResult.Output | ForEach-Object { Write-Host $_ -ForegroundColor $ColorInfo }
Write-ColorMessage '克隆完成' -Color $ColorSuccess -Prefix 'OK'

Write-Step -Number 4 -Title '验证克隆结果'

Push-Location $TargetPath
try {
    $isWorkTree = & git rev-parse --is-inside-work-tree 2>$null
    if ($isWorkTree -ne 'true') {
        Write-ColorMessage '错误：克隆结果不是有效的工作仓库' -Color $ColorError -Prefix 'ERR'
        exit 1
    }
    Write-ColorMessage '工作仓库验证通过' -Color $ColorSuccess -Prefix 'OK'

    if ($RenameOriginToBaidu) {
        $remotes = @()
        $remoteList = & git remote 2>$null
        if ($remoteList) { $remotes = @($remoteList -split "`n" | Where-Object { $_ -ne '' }) }
        if ($remotes -contains 'origin' -and -not ($remotes -contains $RemoteName)) {
            & git remote rename origin $RemoteName 2>$null
            Write-ColorMessage "已将 remote 'origin' 重命名为 '$RemoteName'" -Color $ColorSuccess -Prefix 'RENAME'
        }
    }

    Write-Host ''
    Write-ColorMessage '=== 克隆摘要 ===' -Color $ColorHeader

    Write-ColorMessage '最新提交：' -Color $ColorInfo
    $logResult = & git log --oneline -5 2>$null
    $logResult | Select-Object -First 5 | ForEach-Object { Write-Host "  $_" -ForegroundColor $ColorInfo }

    $branchCount = (& git branch -a 2>$null | Measure-Object).Count
    Write-ColorMessage "分支数量: $branchCount" -Color $ColorInfo

    $tagCount = (& git tag 2>$null | Measure-Object).Count
    Write-ColorMessage "标签数量: $tagCount" -Color $ColorInfo

    Write-Host ''
    Write-ColorMessage 'Remote 配置：' -Color $ColorInfo
    & git remote -v | ForEach-Object { Write-Host "  $_" -ForegroundColor $ColorInfo }

    $status = & git status --short 2>$null
    if ($status) {
        Write-Host ''
        Write-ColorMessage '注意：工作区有未提交变更（可能是换行符差异）：' -Color $ColorWarning -Prefix 'WARN'
        $status | Select-Object -First 10 | ForEach-Object { Write-Host "  $_" -ForegroundColor $ColorWarning }
    }
    else {
        Write-ColorMessage '工作区状态：干净' -Color $ColorSuccess -Prefix 'OK'
    }
}
finally {
    Pop-Location
}

Write-Step -Number 5 -Title '配置本地跨平台设置'

Push-Location $TargetPath
try {
    $os = if ($IsWindows -or $env:OS -eq 'Windows_NT') { 'windows' }
    elseif ($IsMacOS) { 'macos' }
    elseif ($IsLinux) { 'linux' }
    else { 'unknown' }

    if ($os -eq 'windows') {
        & git config --local core.autocrlf true 2>$null
        & git config --local core.fscache true 2>$null
        & git config --local core.longpaths true 2>$null
    }
    else {
        & git config --local core.autocrlf input 2>$null
    }

    & git config --local core.preloadindex true 2>$null
    & git config --local gc.auto 6700 2>$null
    & git config --local gc.autopacklimit 1 2>$null

    Write-ColorMessage '本地跨平台配置已设置' -Color $ColorSuccess -Prefix 'OK'

    $gitattributes = Join-Path $TargetPath '.gitattributes'
    if (-not (Test-Path -Path $gitattributes -PathType Leaf)) {
        Write-ColorMessage '仓库中未找到 .gitattributes' -Color $ColorInfo -Prefix 'INFO'
        Write-ColorMessage '建议运行 setup-git-config.ps1 -Attributes 生成跨平台换行符配置' -Color $ColorWarning -Prefix 'HINT'
    }
    else {
        Write-ColorMessage '.gitattributes 已存在' -Color $ColorSuccess -Prefix 'OK'
    }
}
finally {
    Pop-Location
}

Write-Step -Number 6 -Title '注册设备到 meta/devices.json'

$deviceId = Get-DeviceId
$deviceName = Read-Host "请输入设备可读名称（如：工作笔记本）"
if ([string]::IsNullOrWhiteSpace($deviceName)) {
    $deviceName = $deviceId
}

$deviceOs = if ($IsWindows -or $env:OS -eq 'Windows_NT') { 'windows' }
elseif ($IsMacOS) { 'macos' }
elseif ($IsLinux) { 'linux' }
else { 'unknown' }

$hostname = $env:COMPUTERNAME
if ([string]::IsNullOrEmpty($hostname)) { $hostname = hostname 2>$null }
if ([string]::IsNullOrEmpty($hostname)) { $hostname = 'unknown' }

$now = Get-Date -Format 'yyyy-MM-ddTHH:mm:ssK'

$devicesDir = Split-Path -Path $DevicesJson -Parent
if (-not (Test-Path -Path $devicesDir -PathType Container)) {
    New-Item -Path $devicesDir -ItemType Directory -Force | Out-Null
}

$devicesData = @{ devices = @() }
if (Test-Path -Path $DevicesJson -PathType Leaf) {
    try {
        $existing = Get-Content -Path $DevicesJson -Raw -Encoding UTF8 | ConvertFrom-Json
        if ($existing -and $existing.devices) {
            $devicesData.devices = @($existing.devices)
        }
    }
    catch {
        Write-ColorMessage '现有 devices.json 解析失败，将创建新文件' -Color $ColorWarning -Prefix 'WARN'
    }
}

$existingDevice = $devicesData.devices | Where-Object { $_.id -eq $deviceId }
if ($existingDevice) {
    Write-ColorMessage "设备已注册: $deviceId" -Color $ColorExists -Prefix 'EXISTS'
    $existingDevice.last_seen = $now
    $existingDevice.sync_root = $SyncRoot
}
else {
    $newDevice = @{
        id = $deviceId
        name = $deviceName
        os = $deviceOs
        hostname = $hostname
        registered_at = $now
        last_seen = $now
        sync_root = $SyncRoot
    }
    $devicesData.devices = @($devicesData.devices) + @($newDevice)
    Write-ColorMessage "新设备已注册: $deviceId ($deviceName)" -Color $ColorSuccess -Prefix 'REGISTER'
}

$devicesData | ConvertTo-Json -Depth 10 | Set-Content -Path $DevicesJson -Encoding UTF8
Write-ColorMessage "设备信息已写入: $DevicesJson" -Color $ColorSuccess -Prefix 'OK'

Write-Host ''
Write-ColorMessage '=========================================' -Color $ColorSuccess
Write-ColorMessage '  仓库克隆完成！' -Color $ColorSuccess
Write-ColorMessage '=========================================' -Color $ColorSuccess
Write-Host ''
Write-ColorMessage "仓库名: $RepoName" -Color $ColorSuccess
Write-ColorMessage "本地路径: $TargetPath" -Color $ColorSuccess
Write-ColorMessage "设备 ID: $deviceId" -Color $ColorSuccess
Write-Host ''
Write-ColorMessage '后续步骤：' -Color $ColorHeader
Write-ColorMessage "1. cd $TargetPath" -Color $ColorInfo
Write-ColorMessage "2. 检查 git status 是否干净" -Color $ColorInfo
Write-ColorMessage '3. 如有 .gitattributes 变更，执行 git add --renormalize .' -Color $ColorInfo
Write-ColorMessage "4. 日常推送: git push ${RemoteName}" -Color $ColorInfo
Write-Host ''
