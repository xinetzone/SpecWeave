#Requires -Version 5.1
<#
.SYNOPSIS
    PowerShell 统一结构化日志库片段
.DESCRIPTION
    提供与 bash lib/logging.sh 统一的 JSON Lines 日志输出契约。
    支持：text/json 双格式、级别过滤、metric/event 结构化字段、上下文持久字段。
    输出 JSON Schema：
      { ts, level, service, type?, message?, metric?, value?, unit?, event?, ...context_fields }
.NOTES
    用法：在脚本头部 source 本片段（或直接内嵌），设置 $LogService，然后使用 Log-* 函数。
    兼容 PowerShell 5.1+，无需外部依赖。
.EXAMPLE
    # 脚本头部集成示例
    . "$PSScriptRoot/lib/logging.ps1"  # 或直接内嵌此片段
    $LogService = "my-app"
    Log-Info "启动中..."
    Log-Event -Event "deploy_start" -Fields @{ version="1.0" }
    Log-Metric -Name "duration_seconds" -Value 42.5 -Unit "seconds"
#>

#Requires -Version 5.1

# ── 默认配置（调用方可覆盖） ──
if (-not $LogService)     { $LogService = "ps-script" }
if (-not $LogFormat)      { $LogFormat = "text" }       # text | json
if (-not $LogLevel)       { $LogLevel = "INFO" }        # DEBUG|INFO|WARN|ERROR
if (-not $LogJson)        { $LogJson = $false }         # 是否同时输出 JSON 到 stdout
if (-not $LogJsonOutput)  { $LogJsonOutput = "" }       # JSONL 文件路径（空则不写文件）
if (-not $LogFields)      { $LogFields = @{} }          # 持久上下文字段（hashtable）

# ── 级别映射 ──
$script:LogLevelMap = @{ DEBUG = 0; INFO = 1; WARN = 2; ERROR = 3 }

# ==============================================================================
# 版本校验（自包含，兼容 PS5.1/pwsh7.4+）
# ==============================================================================
function Test-Pwsh7Requirement {
    [CmdletBinding()]
    param([switch]$PassThru)
    $isCore = $false; $currentVersion = $null; $edition = 'Desktop'; $versionOk = $false
    if ($PSVersionTable.ContainsKey('PSEdition')) { $edition = $PSVersionTable.PSEdition }
    $isCore = ($edition -eq 'Core')
    if ($PSVersionTable.ContainsKey('PSVersion')) { $currentVersion = $PSVersionTable.PSVersion }
    if ($isCore -and $null -ne $currentVersion) {
        $majorOk = ($currentVersion.Major -gt 7)
        $minorOk = ($currentVersion.Major -eq 7 -and $currentVersion.Minor -ge 4)
        $versionOk = ($majorOk -or $minorOk)
    }
    $result = [PSCustomObject]@{
        IsCore = $isCore; PSEdition = $edition; PSVersion = $currentVersion
        VersionOk = $versionOk; IsSupported = ($isCore -and $versionOk)
    }
    if ($PassThru) { return $result }
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
    Write-Host "  当前 PSEdition : $($checkResult.PSEdition)" -ForegroundColor Yellow
    Write-Host "  当前 PSVersion : $($checkResult.PSVersion)" -ForegroundColor Yellow
    Write-Host "  需要 PowerShell 7.4+。安装：winget install Microsoft.PowerShell" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Requirement)) { Show-Pwsh7RequirementError }
}

# ── 工具函数 ──
function Get-LogTimestamp {
    return [DateTime]::UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
}

function Write-LogLine {
    param(
        [string]$Level = "INFO",
        [string]$Message = "",
        [string]$Type = "",
        [hashtable]$Extra = @{}
    )

    # 级别过滤
    $msgLevel = if ($script:LogLevelMap.ContainsKey($Level)) { $script:LogLevelMap[$Level] } else { 1 }
    $curLevel = if ($script:LogLevelMap.ContainsKey($LogLevel)) { $script:LogLevelMap[$LogLevel] } else { 1 }
    if ($msgLevel -lt $curLevel) { return }

    # 构建 JSON 对象
    $obj = [ordered]@{
        ts      = Get-LogTimestamp
        level   = $Level.ToLower()
        service = $LogService
    }
    if ($Type)                { $obj.type    = $Type }
    if ($Message)             { $obj.message = $Message }
    foreach ($k in $LogFields.Keys) { $obj[$k] = $LogFields[$k] }
    foreach ($k in $Extra.Keys)     { $obj[$k] = $Extra[$k] }

    $jsonLine = $obj | ConvertTo-Json -Compress -Depth 10

    # 追加到 JSONL 文件
    if ($LogJsonOutput) {
        $dir = Split-Path -Parent $LogJsonOutput
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir -Force | Out-Null }
        [System.IO.File]::AppendAllText($LogJsonOutput, $jsonLine + "`n", [System.Text.UTF8Encoding]::new($false))
    }

    # stdout JSON 输出
    if ($LogJson -or $LogFormat -eq "json") {
        Write-Host $jsonLine
    }

    # text 模式彩色输出（json 模式下仅在 -LogJson 开关时重复输出 text）
    if ($LogFormat -eq "text") {
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
            default  { "[$(($Level + ' ').Substring(0,5).TrimEnd())]" }
        }
        Write-Host "$prefix $Message" -ForegroundColor $color
    }
}

# ── 级别函数 ──
function Log-Debug { param([string]$Msg) Write-LogLine -Level "DEBUG" -Message $Msg }
function Log-Info  { param([string]$Msg) Write-LogLine -Level "INFO"  -Message $Msg }
function Log-Warn  { param([string]$Msg) Write-LogLine -Level "WARN"  -Message $Msg }
function Log-Error { param([string]$Msg) Write-LogLine -Level "ERROR" -Message $Msg }
function Log-Ok    { param([string]$Msg) Write-LogLine -Level "INFO"  -Message "OK: $Msg" }
function Log-Step  {
    param([string]$Msg)
    if ($LogFormat -eq "text") { Write-Host ""; Write-Host "=== $Msg ===" -ForegroundColor Cyan }
    Write-LogLine -Level "INFO" -Message "STEP: $Msg"
}

# ── Metric（数值指标） ──
function Log-Metric {
    param(
        [Parameter(Mandatory)][string]$Name,
        [Parameter(Mandatory)][double]$Value,
        [string]$Unit = ""
    )
    Write-LogLine -Type "metric" -Extra ([ordered]@{ metric = $Name; value = $Value; unit = $Unit })
}

# ── Event（生命周期事件） ──
function Log-Event {
    param(
        [Parameter(Mandatory)][string]$Event,
        [hashtable]$Fields = @{}
    )
    $extra = [ordered]@{ event = $Event }
    foreach ($k in $Fields.Keys) { $extra[$k] = $Fields[$k] }
    Write-LogLine -Type "event" -Extra $extra
}

# ── 解析标准日志参数（--log-format, --log-level, --log-json） ──
# 用法：在 param() 块后调用 Initialize-Logging $args，
# 或手动在 param() 中声明 $LogFormat/$LogLevel/$LogJson 并设置默认值。
function Initialize-Logging {
    param(
        [string]$ServiceName = "",
        [string]$DefaultJsonOutput = ""
    )
    if ($ServiceName) { $script:LogService = $ServiceName }
    if ($DefaultJsonOutput -and -not $LogJsonOutput) { $script:LogJsonOutput = $DefaultJsonOutput }
}

# ── 参数解析辅助（从脚本 args 中提取 --log-format, --log-level, --log-json） ──
# 在脚本中调用：$LogFormat,$LogLevel,$LogJson,$remainingArgs = Parse-LogArgs $args
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
