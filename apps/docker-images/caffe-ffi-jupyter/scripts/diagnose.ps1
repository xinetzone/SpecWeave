#Requires -Version 7.0
<#
.SYNOPSIS
    Caffe-FFI 容器故障诊断 PowerShell 包装器
.DESCRIPTION
    从 Windows PowerShell 直接调用 wsl.exe 执行容器诊断和自动修复。
    支持 text/json 双格式日志输出，与 bash 脚本统一的结构化日志契约。
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
.PARAMETER LogJsonOutput
    JSON 日志输出文件路径（默认: $env:TEMP\caffe-ffi-events.jsonl）
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\diagnose.ps1
    # 默认诊断
.EXAMPLE
    .\diagnose.ps1 -FixAll -LogFormat json
    # 诊断并自动修复，JSON格式输出
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
    [string]$LogJsonOutput = "",
    [string]$Distribution = "",
    [switch]$Help
)

# ── 加载共享库（common.ps1 自动加载 pwsh7-version-check 和 logging） ──
. "$PSScriptRoot/lib/common.ps1"

# ── 版本校验 ──
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Version)) { Show-Pwsh7VersionError }
}

if ($Help) { Get-Help $MyInvocation.MyCommand.Path -Full; exit 0 }

# ── 日志配置 ──
$LogService = "caffe-ffi-diagnose-ps"
if (-not $LogJsonOutput) {
    $LogJsonOutput = Join-Path $env:TEMP "caffe-ffi-events.jsonl"
}
$LogJson = $LogJson.IsPresent
$LogFields = @{}

# ── 启动 ──
$LogFields["container"] = $Container
Log-Event -Event "ps_diagnose_start" -Fields @{
    fix_protobuf = "$($FixProtobuf.IsPresent)"
    fix_ldpath = "$($FixLdPath.IsPresent)"
    fix_all = "$($FixAll.IsPresent)"
}

# ── 1. 检测 WSL ──
Log-Step "WSL 环境检测"
$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Log-Error "wsl.exe 未找到！请先安装 WSL2。"
    Log-Event -Event "ps_diagnose_error" -Fields @{ phase="precheck"; error="wsl_not_found" }
    exit 1
}

if (-not $Distribution) {
    $wslListRaw = wsl.exe --list --verbose 2>&1
    $wslList = @($wslListRaw | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ -and $_ -notmatch '^NAME\s+STATE' })
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' } | ForEach-Object {
        $cleaned = $_ -replace '^\*?\s*', ''
        if ($cleaned -match '^([^\s]+)') { $matches[1] }
    }
    if ($ubuntuDistros.Count -gt 0) {
        $Distribution = $ubuntuDistros[0]
    } else {
        Log-Error "未找到 Ubuntu WSL 发行版"
        Log-Event -Event "ps_diagnose_error" -Fields @{ phase="precheck"; error="distro_not_found" }
        exit 1
    }
}
$LogFields["distribution"] = $Distribution
Log-Info "使用 WSL 发行版: $Distribution"
Log-Info "目标容器: $Container"

# ── 2. Docker 检测 ──
$dockerCheck = wsl.exe -d $Distribution bash -c "docker --version >/dev/null 2>&1 && echo OK || echo MISSING" 2>&1
if ($dockerCheck -notmatch 'OK') {
    Log-Error "WSL 中 Docker 不可用"
    Log-Event -Event "ps_diagnose_error" -Fields @{ phase="precheck"; error="docker_missing" }
    exit 1
}
Log-Ok "Docker 可用"

# ── 3. 参数映射 ──
$bashArgs = @("--container", $Container)
if ($FixProtobuf) { $bashArgs += "--fix-protobuf" }
if ($FixLdPath)   { $bashArgs += "--fix-ldpath" }
if ($FixAll)      { $bashArgs += "--fix-all" }
if ($Dump)        { $bashArgs += "--dump" }
if ($LogFormat -ne "text") { $bashArgs += "--log-format=$LogFormat" }
if ($LogLevel -ne "INFO")  { $bashArgs += "--log-level=$LogLevel" }
if ($LogJson)              { $bashArgs += "--log-json" }

# ── 4. 执行 ──
Log-Step "开始诊断"
$startTime = Get-Date

$scriptDir = Get-ScriptDirectory
$appDir = Split-Path -Parent $scriptDir
$wslAppDir = Convert-WindowsPathToWsl $appDir

wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash scripts/diagnose.sh $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

Log-Event -Event "ps_diagnose_complete" -Fields @{
    status = $(if ($exitCode -eq 0) { "success" } else { "failed" })
    duration = "$duration"
    exit_code = $exitCode
}

if ($LogFormat -eq "text" -or $LogJson) {
    Write-Host ""
    Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
}

exit $exitCode
