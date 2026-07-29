#Requires -Version 5.1
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

#Requires -Version 5.1

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

# ==============================================================================
# 版本校验（自包含，不依赖外部 lib 文件）
# 兼容 Windows PowerShell 5.1 和 PowerShell 7.4+
# 注意：版本检测逻辑在 param() 之后立即执行
# ==============================================================================
function Test-Pwsh7Requirement {
    [CmdletBinding()]
    param(
        [switch]$PassThru
    )

    $isCore = $false
    $currentVersion = $null
    $edition = 'Desktop'
    $versionOk = $false

    if ($PSVersionTable.ContainsKey('PSEdition')) {
        $edition = $PSVersionTable.PSEdition
    }
    $isCore = ($edition -eq 'Core')

    if ($PSVersionTable.ContainsKey('PSVersion')) {
        $currentVersion = $PSVersionTable.PSVersion
    }

    if ($isCore -and $null -ne $currentVersion) {
        $majorOk = ($currentVersion.Major -gt 7)
        $minorOk = ($currentVersion.Major -eq 7 -and $currentVersion.Minor -ge 4)
        $versionOk = ($majorOk -or $minorOk)
    }

    $result = [PSCustomObject]@{
        IsCore      = $isCore
        PSEdition   = $edition
        PSVersion   = $currentVersion
        VersionOk   = $versionOk
        IsSupported = ($isCore -and $versionOk)
    }

    if ($PassThru) {
        return $result
    }

    return $result.IsSupported
}

function Show-Pwsh7RequirementError {
    [CmdletBinding()]
    param()

    $checkResult = Test-Pwsh7Requirement -PassThru

    Write-Host ""
    Write-Host "========================================" -ForegroundColor Red
    Write-Host "  错误：PowerShell 版本不支持" -ForegroundColor Red
    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""

    Write-Host "  当前 PowerShell 信息：" -ForegroundColor Yellow
    Write-Host "    PSEdition : $($checkResult.PSEdition)"
    Write-Host "    PSVersion : $($checkResult.PSVersion)"
    Write-Host ""

    Write-Host "  问题说明：" -ForegroundColor Yellow
    Write-Host "    本脚本需要 PowerShell 7.4 或更高版本（pwsh7）。"
    Write-Host "    当前运行的是旧版本或不兼容版本。"
    Write-Host ""

    Write-Host "  安装命令：" -ForegroundColor Yellow
    Write-Host "    winget install Microsoft.PowerShell"
    Write-Host ""

    Write-Host "  文档提示：" -ForegroundColor Yellow
    Write-Host "    请参考项目 ONBOARDING.md 配置开发环境。"
    Write-Host ""

    Write-Host "========================================" -ForegroundColor Red
    Write-Host ""

    exit 1
}

if ($MyInvocation.InvocationName -ne '.') {
    $supported = Test-Pwsh7Requirement
    if (-not $supported) {
        Show-Pwsh7RequirementError
    }
}

if ($Help) { Get-Help $MyInvocation.MyCommand.Path -Full; exit 0 }

# ── 日志配置 ──
$LogService = "caffe-ffi-diagnose-ps"
if (-not $LogJsonOutput) {
    $LogJsonOutput = Join-Path $env:TEMP "caffe-ffi-events.jsonl"
}
$LogFields = @{}

function Get-Timestamp {
    return [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-JsonLog {
    param(
        [string]$Level = "INFO",
        [string]$Message = "",
        [string]$Type = "",
        [hashtable]$Extra = @{}
    )
    $levelMap = @{ DEBUG=0; INFO=1; WARN=2; ERROR=3 }
    $msgLevel = if ($levelMap.ContainsKey($Level)) { $levelMap[$Level] } else { 1 }
    $curLevel = if ($levelMap.ContainsKey($LogLevel)) { $levelMap[$LogLevel] } else { 1 }
    if ($msgLevel -lt $curLevel) { return }

    $obj = [ordered]@{
        ts = Get-Timestamp
        level = $Level.ToLower()
        service = $LogService
    }
    if ($Type) { $obj.type = $Type }
    if ($Message) { $obj.message = $Message }
    foreach ($k in $LogFields.Keys) { $obj[$k] = $LogFields[$k] }
    foreach ($k in $Extra.Keys) { $obj[$k] = $Extra[$k] }

    $json = $obj | ConvertTo-Json -Compress -Depth 5
    [System.IO.File]::AppendAllText($LogJsonOutput, $json + "`n", [System.Text.UTF8Encoding]::new($false))
    if ($LogJson) { Write-Host $json }
}

function Write-JsonEvent {
    param([string]$Event, [hashtable]$Fields = @{})
    $extra = [ordered]@{ event = $Event }
    foreach ($k in $Fields.Keys) { $extra[$k] = $Fields[$k] }
    Write-JsonLog -Type "event" -Extra $extra
}

function Write-Info {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) { Write-Host "[INFO]  $Msg" -ForegroundColor Green }
    Write-JsonLog -Level "INFO" -Message $Msg
}
function Write-WarnOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) { Write-Host "[WARN]  $Msg" -ForegroundColor Yellow }
    Write-JsonLog -Level "WARN" -Message $Msg
}
function Write-ErrOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) { Write-Host "[ERROR] $Msg" -ForegroundColor Red }
    Write-JsonLog -Level "ERROR" -Message $Msg
}
function Write-OkOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) { Write-Host "  OK   $Msg" -ForegroundColor Green }
    Write-JsonLog -Level "INFO" -Message "OK: $Msg"
}
function Write-StepOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) { Write-Host ""; Write-Host "=== $Msg ===" -ForegroundColor Cyan }
    Write-JsonLog -Level "INFO" -Message "STEP: $Msg"
}

# ── 启动 ──
$LogFields["container"] = $Container
Write-JsonEvent -Event "ps_diagnose_start" -Fields @{
    fix_protobuf = "$($FixProtobuf.IsPresent)"
    fix_ldpath = "$($FixLdPath.IsPresent)"
    fix_all = "$($FixAll.IsPresent)"
}

# ── 1. 检测 WSL ──
Write-StepOut "WSL 环境检测"
$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Write-ErrOut "wsl.exe 未找到！请先安装 WSL2。"
    Write-JsonEvent -Event "ps_diagnose_error" -Fields @{ phase="precheck"; error="wsl_not_found" }
    exit 1
}

if (-not $Distribution) {
    # wsl.exe 输出 UTF-16 LE，需清理 NUL 字符和空行
    $wslListRaw = wsl.exe --list --verbose 2>&1
    $wslList = @($wslListRaw | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ -and $_ -notmatch '^NAME\s+STATE' })
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' } | ForEach-Object {
        $cleaned = $_ -replace '^\*?\s*', ''
        if ($cleaned -match '^([^\s]+)') { $matches[1] }
    }
    if ($ubuntuDistros.Count -gt 0) {
        $Distribution = $ubuntuDistros[0]
    } else {
        Write-ErrOut "未找到 Ubuntu WSL 发行版"
        Write-JsonEvent -Event "ps_diagnose_error" -Fields @{ phase="precheck"; error="distro_not_found" }
        exit 1
    }
}
$LogFields["distribution"] = $Distribution
Write-Info "使用 WSL 发行版: $Distribution"
Write-Info "目标容器: $Container"

# ── 2. Docker 检测 ──
$dockerCheck = wsl.exe -d $Distribution bash -c "docker --version >/dev/null 2>&1 && echo OK || echo MISSING" 2>&1
if ($dockerCheck -notmatch 'OK') {
    Write-ErrOut "WSL 中 Docker 不可用"
    Write-JsonEvent -Event "ps_diagnose_error" -Fields @{ phase="precheck"; error="docker_missing" }
    exit 1
}
Write-OkOut "Docker 可用"

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
Write-StepOut "开始诊断"
$startTime = Get-Date

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appDir = Split-Path -Parent $scriptDir
function Convert-ToWslPath {
    param([string]$WindowsPath)
    $fullPath = [System.IO.Path]::GetFullPath($WindowsPath)
    $drive = $fullPath.Substring(0, 1).ToLower()
    $rest = $fullPath.Substring(2).Replace('\', '/')
    return "/mnt/$drive$rest"
}
$wslAppDir = Convert-ToWslPath $appDir

wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash scripts/diagnose.sh $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

Write-JsonEvent -Event "ps_diagnose_complete" -Fields @{
    status = $(if ($exitCode -eq 0) { "success" } else { "failed" })
    duration = "$duration"
    exit_code = $exitCode
}

if ($LogFormat -eq "text" -or $LogJson) {
    Write-Host ""
    Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
}

exit $exitCode
