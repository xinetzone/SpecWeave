#Requires -Version 5.1
<#
.SYNOPSIS
    Caffe-FFI 容器故障诊断 PowerShell 包装器
.DESCRIPTION
    从 Windows PowerShell 直接调用 wsl.exe 执行容器诊断和自动修复。
.PARAMETER Container
    容器名称（默认: caffe-ffi-jupyter）
.PARAMETER FixProtobuf
    尝试自动修复 protobuf 版本冲突
.PARAMETER FixLdPath
    尝试自动修复共享库路径问题
.PARAMETER FixAll
    执行所有自动修复
.PARAMETER Dump
    导出完整诊断信息到文件
.PARAMETER LogFormat
    日志格式: text (默认) | json
.PARAMETER LogLevel
    日志级别: DEBUG|INFO|WARN|ERROR
.PARAMETER LogJson
    JSON 同时输出到 stdout
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\diagnose.ps1
    # 默认诊断
.EXAMPLE
    .\diagnose.ps1 -FixAll
    # 诊断并自动修复所有问题
.EXAMPLE
    .\diagnose.ps1 -FixProtobuf
    # 仅修复 protobuf 问题
#>

[CmdletBinding()]
param(
    [string]$Container = "caffe-ffi-jupyter",
    [switch]$FixProtobuf,
    [switch]$FixLdPath,
    [switch]$FixAll,
    [switch]$Dump,
    [ValidateSet("text", "json")]
    [string]$LogFormat = "text",
    [ValidateSet("DEBUG", "INFO", "WARN", "ERROR")]
    [string]$LogLevel = "INFO",
    [switch]$LogJson,
    [string]$Distribution = "",
    [switch]$Help
)

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

function Write-Info { param([string]$Msg) Write-Host "[INFO]  $Msg" -ForegroundColor Green }
function Write-Warn { param([string]$Msg) Write-Host "[WARN]  $Msg" -ForegroundColor Yellow }
function Write-Err  { param([string]$Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red }
function Write-Step { param([string]$Msg) Write-Host "`n=== $Msg ===" -ForegroundColor Cyan }

# 检测 WSL
$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Write-Err "wsl.exe 未找到！请先安装 WSL2。"
    exit 1
}

# 自动检测发行版
if (-not $Distribution) {
    $wslList = wsl.exe --list --verbose 2>&1
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' } | ForEach-Object {
        if ($_ -match '^\s*(\*?\s*)?(Ubuntu[\w.-]*)\s+') { $matches[2].Trim() }
    }
    if ($ubuntuDistros) {
        $Distribution = $ubuntuDistros[0]
    } else {
        Write-Err "未找到 Ubuntu WSL 发行版"
        exit 1
    }
}

Write-Info "使用 WSL 发行版: $Distribution"
Write-Info "目标容器: $Container"

# 检查 Docker
$dockerCheck = wsl.exe -d $Distribution bash -c "docker --version >/dev/null 2>&1 && echo OK || echo MISSING" 2>&1
if ($dockerCheck -notmatch 'OK') {
    Write-Err "WSL 中 Docker 不可用"
    exit 1
}

# 构建参数
$bashArgs = @("--container", $Container)
if ($FixProtobuf) { $bashArgs += "--fix-protobuf" }
if ($FixLdPath) { $bashArgs += "--fix-ldpath" }
if ($FixAll) { $bashArgs += "--fix-all" }
if ($Dump) { $bashArgs += "--dump" }
if ($LogFormat -ne "text") { $bashArgs += "--log-format=$LogFormat" }
if ($LogLevel -ne "INFO") { $bashArgs += "--log-level=$LogLevel" }
if ($LogJson) { $bashArgs += "--log-json" }

# 获取脚本目录
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
function Convert-ToWslPath {
    param([string]$WindowsPath)
    $fullPath = [System.IO.Path]::GetFullPath($WindowsPath)
    $drive = $fullPath.Substring(0, 1).ToLower()
    $rest = $fullPath.Substring(2).Replace('\', '/')
    return "/mnt/$drive$rest"
}
$wslScriptDir = Convert-ToWslPath $scriptDir
$wslAppDir = Split-Path -Parent $wslScriptDir

Write-Step "开始诊断"

wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash scripts/diagnose.sh $($bashArgs -join ' ')"
exit $LASTEXITCODE
