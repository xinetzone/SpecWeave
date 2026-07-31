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
        Diag-Write -Status ERR -Name "Git仓库检查" -Detail "'$Repo