#Requires -Version 5.1
<#
.SYNOPSIS
    PowerShell 统一结构化日志库
.DESCRIPTION
    与 lib/logging.sh 同源的 JSON Lines 日志输出，支持 text/json 双格式、级别过滤、
    metric/event 结构化字段、上下文持久字段。可被 .ps1 脚本 dot-source 加载。
    输出 JSON Schema（与 bash 版统一）：
      { ts, level, service, type?, message?, metric?, value?, unit?, event?, ...context_fields }
.NOTES
    用法（在调用脚本中）：
      $LoggingLibDir = Split-Path -Parent $MyInvocation.MyCommand.Path
      . "$LoggingLibDir/lib/logging.ps1"
      $LogService = "my-service"
      # 可选：$LogFormat = "json"; $LogJson = $true
      Log-Info "Hello"
      Log-Event -Event "start"
      Log-Metric -Name "duration" -Value 1.5 -Unit "s"
#>

#Requires -Version 5.1

# ── 避免重复加载 ──
if ($script:__LOGGING_PS1_LOADED) { return }
$script:__LOGGING_PS1_LOADED = $true

# ── 默认配置（调用方可在 dot-source 后覆盖） ──
if (-not (Get-Variable -Name LogService -Scope Script -ErrorAction SilentlyContinue)) {
    $script:LogService = "ps-script"
}
if (-not (Get-Variable -Name LogFormat -Scope Script -ErrorAction SilentlyContinue)) {
    $script:LogFormat = "text"
}
if (-not (Get-Variable -Name LogLevel -Scope Script -ErrorAction SilentlyContinue)) {
    $script:LogLevel = "INFO"
}
if (-not (Get-Variable -Name LogJson -Scope Script -ErrorAction SilentlyContinue)) {
    $script:LogJson = $false
}
if (-not (Get-Variable -Name LogJsonOutput -Scope Script -ErrorAction SilentlyContinue)) {
    $script:LogJsonOutput = ""
}
if (-not (Get-Variable -Name LogFields -Scope Script -ErrorAction SilentlyContinue)) {
    $script:LogFields = @{}
}

$script:LogLevelMap = @{ DEBUG = 0; INFO = 1; WARN = 2; ERROR = 3 }

# 版本校验：引用共享库
. "$PSScriptRoot/pwsh7-version-check.ps1"
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Requirement)) { Show-Pwsh7RequirementError }
}

function script:Get-LogTimestamp {
    [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function script:Write-LogLine {
    param(
        [string]$Level = "INFO",
        [string]$Message = "",
        [string]$Type = "",
        [hashtable]$Extra = @{}
    )

    $msgLevel = if ($script:LogLevelMap.ContainsKey($Level)) { $script:LogLevelMap[$Level] } else { 1 }
    $curLevel = if ($script:LogLevelMap.ContainsKey($script:LogLevel)) { $script:LogLevelMap[$script:LogLevel] } else { 1 }
    if ($msgLevel -lt $curLevel) { return }

    $obj = [ordered]@{
        ts      = Get-LogTimestamp
        level   = $Level.ToLower()
        service = $script:LogService
    }
    if ($Type)    { $obj.type = $Type }
    if ($Message) { $obj.message = $Message }
    foreach ($k in $script:LogFields.Keys) { $obj[$k] = $script:LogFields[$k] }
    foreach ($k in $Extra.Keys)           { $obj[$k] = $Extra[$k] }

    $jsonLine = $obj | ConvertTo-Json -Compress -Depth 10

    if ($script:LogJsonOutput) {
        $dir = Split-Path -Parent $script:LogJsonOutput
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        [System.IO.File]::AppendAllText($script:LogJsonOutput, $jsonLine + "`n", [System.Text.UTF8Encoding]::new($false))
    }

    if ($script:LogJson -or $script:LogFormat -eq "json") {
        Write-Host $jsonLine
    }

    if ($script:LogFormat -eq "text") {
        $color = switch ($Level) {
            "DEBUG" { "Gray" }
            "INFO"  { "Green" }
            "WARN"  { "Yellow" }
            "ERROR" { "Red" }
            default { "White" }
        }
        $prefix = switch ($Type) {
            "metric" { "[METRIC]" }
            "event"  { "[EVENT] " }
            default  { "[$(($Level + ' ').Substring(0, [Math]::Min(5, $Level.Length + 1)).TrimEnd())]" }
        }
        Write-Host "$prefix $Message" -ForegroundColor $color
    }
}

# ── 导出函数到调用者作用域 ──
function Log-Debug { param([string]$Msg) Write-LogLine -Level "DEBUG" -Message $Msg }
function Log-Info  { param([string]$Msg) Write-LogLine -Level "INFO"  -Message $Msg }
function Log-Warn  { param([string]$Msg) Write-LogLine -Level "WARN"  -Message $Msg }
function Log-Error { param([string]$Msg) Write-LogLine -Level "ERROR" -Message $Msg }
function Log-Ok    { param([string]$Msg) Write-LogLine -Level "INFO"  -Message "OK: $Msg" }
function Log-Step {
    param([string]$Msg)
    if ($script:LogFormat -eq "text") {
        Write-Host ""
        Write-Host "=== $Msg ===" -ForegroundColor Cyan
    }
    Write-LogLine -Level "INFO" -Message "STEP: $Msg"
}

function Log-Metric {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][double]$Value,
        [string]$Unit = ""
    )
    Write-LogLine -Type "metric" -Extra ([ordered]@{ metric = $Name; value = $Value; unit = $Unit })
}

function Log-Event {
    param(
        [Parameter(Mandatory)][string]$Event,
        [hashtable]$Fields = @{}
    )
    $extra = [ordered]@{ event = $Event }
    foreach ($k in $Fields.Keys) { $extra[$k] = $Fields[$k] }
    Write-LogLine -Type "event" -Extra $extra
}

# ── 参数解析：从 $args 中提取 --log-format, --log-level, --log-json ──
function Parse-LogArgs {
    param([string[]]$Arguments)
    $fmt = "text"; $lvl = "INFO"; $json = $false; $remain = @()
    foreach ($arg in $Arguments) {
        switch -Regex ($arg) {
            '^--log-format=(.+)$' { $fmt = $Matches[1] }
            '^--log-level=(.+)$'  { $lvl = $Matches[1].ToUpper() }
            '^--log-json$'        { $json = $true }
            default               { $remain += $arg }
        }
    }
    return @($fmt, $lvl, $json, $remain)
}
