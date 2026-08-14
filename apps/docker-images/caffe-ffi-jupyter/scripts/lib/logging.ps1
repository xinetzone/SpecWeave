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
      . "$PSScriptRoot/lib/logging.ps1"
      $LogService = "my-service"
      # 可选：$LogFormat = "json"; $LogJson = $true
      Log-Info "Hello"
      Log-Event -Event "start"
      Log-Metric -Name "duration" -Value 1.5 -Unit "s"
#>

# ── 避免重复加载 ──
if ($script:__LOGGING_PS1_LOADED) { return }
$script:__LOGGING_PS1_LOADED = $true

# ── 内部常量（script 域，外部不可修改） ──
$script:LogLevelMap = @{ DEBUG = 0; INFO = 1; OK = 1; WARN = 2; ERROR = 3 }
$script:LogTagWidth = 8

# ── 默认配置（无 scope 前缀，dot-source 后在调用方域创建，调用方可直接覆盖） ──
if (-not (Get-Variable -Name LogService -ErrorAction SilentlyContinue)) {
    $LogService = "ps-script"
}
if (-not (Get-Variable -Name LogFormat -ErrorAction SilentlyContinue)) {
    $LogFormat = "text"
}
if (-not (Get-Variable -Name LogLevel -ErrorAction SilentlyContinue)) {
    $LogLevel = "INFO"
}
if (-not (Get-Variable -Name LogJson -ErrorAction SilentlyContinue)) {
    $LogJson = $false
}
if (-not (Get-Variable -Name LogJsonOutput -ErrorAction SilentlyContinue)) {
    $LogJsonOutput = ""
}
if (-not (Get-Variable -Name LogFields -ErrorAction SilentlyContinue)) {
    $LogFields = @{}
}

# ── 版本校验：引用共享库 ──
. "$PSScriptRoot/pwsh7-version-check.ps1"
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Version)) { Show-Pwsh7VersionError }
}

function script:Get-LogTimestamp {
    [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function script:Format-LogTag {
    param([string]$Tag)
    $bracketed = "[$Tag]"
    return $bracketed.PadRight($script:LogTagWidth)
}

function script:Write-LogLine {
    param(
        [string]$Level = "INFO",
        [string]$Message = "",
        [string]$Type = "",
        [string]$Tag = "",
        [string]$Color = "",
        [hashtable]$Extra = @{}
    )

    # 级别过滤（使用 dynamic scoping 从调用链查找 $LogLevel）
    $msgLevel = if ($script:LogLevelMap.ContainsKey($Level)) { $script:LogLevelMap[$Level] } else { 1 }
    $curLevel = if ($script:LogLevelMap.ContainsKey($LogLevel)) { $script:LogLevelMap[$LogLevel] } else { 1 }
    if ($msgLevel -lt $curLevel) { return }

    # JSON 日志中 OK 级别映射为 info
    $jsonLevel = if ($Level -eq "OK") { "info" } else { $Level.ToLower() }

    $obj = [ordered]@{
        ts      = Get-LogTimestamp
        level   = $jsonLevel
        service = $LogService
    }
    if ($Type)    { $obj.type = $Type }
    if ($Message) { $obj.message = $Message }
    foreach ($k in $LogFields.Keys) { $obj[$k] = $LogFields[$k] }
    foreach ($k in $Extra.Keys)       { $obj[$k] = $Extra[$k] }

    $jsonLine = $obj | ConvertTo-Json -Compress -Depth 10

    if ($LogJsonOutput) {
        $dir = Split-Path -Parent $LogJsonOutput
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        [System.IO.File]::AppendAllText($LogJsonOutput, $jsonLine + "`n", [System.Text.UTF8Encoding]::new($false))
    }

    if ($LogJson -or $LogFormat -eq "json") {
        Write-Host $jsonLine
    }

    if ($LogFormat -eq "text") {
        if (-not $Color) {
            $Color = switch ($Level) {
                "DEBUG" { "Gray" }
                "INFO"  { "Green" }
                "OK"    { "Green" }
                "WARN"  { "Yellow" }
                "ERROR" { "Red" }
                default { "White" }
            }
        }

        if (-not $Tag) {
            $Tag = switch ($Type) {
                "metric" { "METRIC" }
                "event"  { "EVENT" }
                default  { $Level }
            }
        }

        $prefix = Format-LogTag $Tag
        Write-Host "$prefix $Message" -ForegroundColor $Color
    }
}

# ── 导出函数到调用者作用域（无 scope 前缀，dot-source 后在调用方域可见） ──
function Log-Debug { param([string]$Msg) Write-LogLine -Level "DEBUG" -Message $Msg }
function Log-Info  { param([string]$Msg) Write-LogLine -Level "INFO"  -Message $Msg }
function Log-Ok    { param([string]$Msg) Write-LogLine -Level "OK"    -Message $Msg -Tag "OK" }
function Log-Warn  { param([string]$Msg) Write-LogLine -Level "WARN"  -Message $Msg }
function Log-Error { param([string]$Msg) Write-LogLine -Level "ERROR" -Message $Msg }

function Log-Step {
    param([string]$Msg)
    if ($LogFormat -eq "text") {
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
    Write-LogLine -Level "INFO" -Type "metric" -Extra ([ordered]@{ metric = $Name; value = $Value; unit = $Unit })
}

function Log-Event {
    param(
        [Parameter(Mandatory)][string]$Event,
        [hashtable]$Fields = @{}
    )
    $extra = [ordered]@{ event = $Event }
    foreach ($k in $Fields.Keys) { $extra[$k] = $Fields[$k] }
    Write-LogLine -Level "INFO" -Type "event" -Extra $extra
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
