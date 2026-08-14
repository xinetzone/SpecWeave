#Requires -Version 5.1
<#
.SYNOPSIS
    Jupyter-SSH-Base Docker 镜像构建 PowerShell 包装器
.DESCRIPTION
    从 Windows PowerShell/CMD 直接调用，自动通过 wsl.exe 执行 WSL 内的构建脚本。
    支持 text/json 双格式日志输出，与 bash 脚本统一的结构化日志契约。
.PARAMETER Tag
    镜像标签（默认: 1.1）
.PARAMETER Name
    镜像名称（默认: jupyter-ssh-base）
.PARAMETER Registry
    Registry 前缀（如 your-registry.com）
.PARAMETER NoCache
    禁用 Docker 构建缓存
.PARAMETER CN
    使用国内镜像源（apt: aliyun, pip: aliyun）
.PARAMETER AptMirror
    APT 镜像源: official|aliyun|tuna（默认: official）
.PARAMETER PipMirror
    PyPI 镜像源: official|aliyun|tuna（默认: official）
.PARAMETER Verify
    构建后运行嵌入式验证
.PARAMETER VerifyOnly
    仅验证已有镜像（跳过构建）
.PARAMETER LogFormat
    日志格式: text (默认) | json
.PARAMETER LogLevel
    日志级别: DEBUG|INFO|WARN|ERROR
.PARAMETER LogJson
    JSON 同时输出到 stdout
.PARAMETER LogJsonOutput
    JSON 日志输出文件路径（默认: $env:TEMP\jupyter-ssh-base-events.jsonl）
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测 Ubuntu）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\build.ps1 -CN
    # 国内用户一键构建
.EXAMPLE
    .\build.ps1 -Tag latest -Verify
    # 构建 latest 标签并验证
.EXAMPLE
    .\build.ps1 -LogFormat json -LogJson
    # JSON 格式输出（供监控平台采集）
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [string]$Tag = "1.1",
    [string]$Name = "jupyter-ssh-base",
    [string]$Registry = "",
    [switch]$NoCache,
    [switch]$CN,
    [ValidateSet("official", "aliyun", "tuna")]
    [string]$AptMirror = "official",
    [ValidateSet("official", "aliyun", "tuna")]
    [string]$PipMirror = "official",
    [switch]$Verify,
    [switch]$VerifyOnly,
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

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

# ── 日志配置 ──
$LogService = "jupyter-ssh-build-ps"
if (-not $LogJsonOutput) {
    $LogJsonOutput = Join-Path $env:TEMP "jupyter-ssh-base-events.jsonl"
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

function Write-JsonMetric {
    param([string]$Name, [double]$Value, [string]$Unit = "")
    $extra = [ordered]@{ metric = $Name; value = $Value; unit = $Unit }
    Write-JsonLog -Type "metric" -Extra $extra
}

function Write-JsonEvent {
    param([string]$Event, [hashtable]$Fields = @{})
    $extra = [ordered]@{ event = $Event }
    foreach ($k in $Fields.Keys) { $extra[$k] = $Fields[$k] }
    Write-JsonLog -Type "event" -Extra $extra
}

function Write-Info {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host "[INFO]  $Msg" -ForegroundColor Green
    }
    Write-JsonLog -Level "INFO" -Message $Msg
}
function Write-WarnOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host "[WARN]  $Msg" -ForegroundColor Yellow
    }
    Write-JsonLog -Level "WARN" -Message $Msg
}
function Write-ErrOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host "[ERROR] $Msg" -ForegroundColor Red
    }
    Write-JsonLog -Level "ERROR" -Message $Msg
}
function Write-OkOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host "  OK   $Msg" -ForegroundColor Green
    }
    Write-JsonLog -Level "INFO" -Message "OK: $Msg"
}
function Write-StepOut {
    param([string]$Msg)
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "=== $Msg ===" -ForegroundColor Cyan
    }
    Write-JsonLog -Level "INFO" -Message "STEP: $Msg"
}

# ── 启动事件 ──
$buildStart = Get-Date
$fullImage = if ($Registry) { "${Registry}/${Name}:${Tag}" } else { "${Name}:${Tag}" }
$LogFields["image"] = $fullImage
Write-JsonEvent -Event "ps_build_start" -Fields @{
    cn_mirrors = "$($CN.IsPresent)"
    no_cache = "$($NoCache.IsPresent)"
    verify = "$($Verify.IsPresent -or $VerifyOnly.IsPresent)"
    log_format = $LogFormat
}

# ── 1. 检测 wsl.exe ──
Write-StepOut "WSL 环境检测"

$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Write-ErrOut "wsl.exe 未找到！请先安装 WSL2：wsl --install -d Ubuntu-24.04"
    Write-JsonEvent -Event "ps_build_error" -Fields @{ phase="precheck"; error="wsl_not_found" }
    exit 1
}
Write-OkOut "wsl.exe 可用"

# ── 2. 检测 WSL 发行版 ──
# wsl.exe 输出 UTF-16 LE，需清理 NUL 字符和空行
$wslListRaw = wsl.exe --list --verbose 2>&1
$wslList = @($wslListRaw | ForEach-Object { ($_ -replace "`0", "").Trim() } | Where-Object { $_ -and $_ -notmatch '^NAME\s+STATE' })
if ($LASTEXITCODE -ne 0 -or -not $wslList) {
    Write-ErrOut "WSL 未正确安装或没有可用的发行版。请执行: wsl --install -d Ubuntu-24.04"
    Write-JsonEvent -Event "ps_build_error" -Fields @{ phase="precheck"; error="no_distro" }
    exit 1
}

if (-not $Distribution) {
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' } | ForEach-Object {
        $cleaned = $_ -replace '^\*?\s*', ''
        if ($cleaned -match '^([^\s]+)') { $matches[1] }
    }
    if ($ubuntuDistros.Count -gt 0) {
        $Distribution = $ubuntuDistros[0]
        Write-Info "自动检测到 WSL 发行版: $Distribution"
    } else {
        $firstLine = $wslList | Select-Object -First 1
        if ($firstLine) {
            $Distribution = ($firstLine -replace '^\*?\s*', '') -split '\s+' | Select-Object -First 1
            Write-WarnOut "未检测到 Ubuntu，使用发行版: $Distribution"
        } else {
            Write-ErrOut "未找到可用的 WSL 发行版"
            Write-JsonEvent -Event "ps_build_error" -Fields @{ phase="precheck"; error="distro_not_found" }
            exit 1
        }
    }
}
$LogFields["distribution"] = $Distribution
Write-OkOut "使用 WSL 发行版: $Distribution"

# ── 3. 路径转换 ──
Write-StepOut "路径转换"

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
Write-Info "WSL 工作目录: $wslAppDir"

# ── 4. Docker 预检测 ──
Write-StepOut "Docker 环境预检测"

$dockerCheck = wsl.exe -d $Distribution bash -c "docker --version 2>/dev/null && echo 'DOCKER_OK' || echo 'DOCKER_MISSING'" 2>&1
if ($dockerCheck -match 'DOCKER_MISSING') {
    Write-ErrOut "WSL ($Distribution) 中 Docker 不可用！请安装 Docker Desktop 或原生 Docker。"
    Write-JsonEvent -Event "ps_build_error" -Fields @{ phase="precheck"; error="docker_missing" }
    exit 1
}
$dockerVer = ($dockerCheck | Select-String 'Docker version [\d.]+').Matches.Value
Write-OkOut "Docker 可用: $dockerVer"

$daemonCheck = wsl.exe -d $Distribution bash -c "docker info >/dev/null 2>&1 && echo 'DAEMON_OK' || echo 'DAEMON_DOWN'" 2>&1
if ($daemonCheck -match 'DAEMON_DOWN') {
    Write-ErrOut "Docker daemon 未运行！请启动 Docker Desktop 或执行 sudo systemctl start docker"
    Write-JsonEvent -Event "ps_build_error" -Fields @{ phase="precheck"; error="docker_daemon_down" }
    exit 1
}
Write-OkOut "Docker daemon 运行中"

# ── 5. 构建参数 ──
if ($CN) { $AptMirror = "aliyun"; $PipMirror = "aliyun" }

$bashArgs = @()
if ($Tag -ne "1.1") { $bashArgs += "--tag"; $bashArgs += $Tag }
if ($Name -ne "jupyter-ssh-base") { $bashArgs += "--name"; $bashArgs += $Name }
if ($Registry) { $bashArgs += "--registry"; $bashArgs += $Registry }
if ($NoCache) { $bashArgs += "--no-cache" }
if ($AptMirror -ne "official") { $bashArgs += "--apt-mirror"; $bashArgs += $AptMirror }
if ($PipMirror -ne "official") { $bashArgs += "--pip-mirror"; $bashArgs += $PipMirror }
if ($Verify) { $bashArgs += "--verify" }
if ($VerifyOnly) { $bashArgs += "--verify-only" }
if ($VerbosePreference -eq 'Continue' -or $PSBoundParameters['Verbose']) { $bashArgs += "--verbose" }
if ($LogFormat -ne "text") { $bashArgs += "--log-format=$LogFormat" }
if ($LogLevel -ne "INFO") { $bashArgs += "--log-level=$LogLevel" }
if ($LogJson) { $bashArgs += "--log-json" }

# ── 6. 执行构建 ──
Write-StepOut "开始构建镜像"
Write-Info "目标镜像: $fullImage"
Write-Info "调用 WSL: bash scripts/build.sh $($bashArgs -join ' ')"
if ($LogFormat -eq "text" -or $LogJson) { Write-Host "" }

$startTime = Get-Date
wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash scripts/build.sh $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

Write-JsonMetric -Name "ps_build_duration_seconds" -Value $duration -Unit "seconds"

if ($LogFormat -eq "text" -or $LogJson) { Write-Host "" }

if ($exitCode -eq 0) {
    Write-StepOut "构建成功"
    Write-OkOut "总耗时: $duration 秒"
    Write-JsonEvent -Event "ps_build_complete" -Fields @{ status="success"; duration="$duration"; exit_code=0; image=$fullImage }
    Write-JsonMetric -Name "ps_build_exit_code" -Value 0
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "镜像信息：" -ForegroundColor Cyan
        wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "docker images $fullImage --format 'table {{.Repository}}\t{{.Tag}}\t{{.Size}}'"
        Write-Host ""
        Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
    }
} else {
    Write-StepOut "构建失败"
    Write-ErrOut "退出码: $exitCode"
    Write-ErrOut "耗时: $duration 秒"
    Write-JsonEvent -Event "ps_build_complete" -Fields @{ status="failed"; duration="$duration"; exit_code=$exitCode; image=$fullImage }
    Write-JsonMetric -Name "ps_build_exit_code" -Value $exitCode
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "故障排查：" -ForegroundColor Yellow
        Write-Host "  1. 查看构建日志确认错误位置"
        Write-Host "  2. 检查 Docker daemon 是否正常运行"
        Write-Host "  3. 网络问题可尝试添加 -CN 参数使用国内镜像"
        Write-Host ""
        Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
    }
}

exit $exitCode
