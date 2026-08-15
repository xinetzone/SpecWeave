#Requires -Version 5.1
<#
.SYNOPSIS
    PyTorch Base Docker 镜像构建 PowerShell 包装器
.DESCRIPTION
    从 Windows PowerShell/CMD 直接调用，自动通过 wsl.exe 执行 WSL 内的构建脚本。
    支持 text/json 双格式日志输出，与 bash 脚本统一的结构化日志契约。
.PARAMETER Cpu
    构建 CPU-only 版本（默认构建 GPU 版本）
.PARAMETER Cuda
    CUDA 版本（默认: 12.6，可选: 12.6/12.8/13.0）
.PARAMETER Offline
    使用 offline/ 目录下的本地包构建
.PARAMETER PrepareOffline
    仅下载离线资源，不执行构建
.PARAMETER TorchVersion
    PyTorch 版本（默认: 2.13.0）
.PARAMETER PythonVersion
    Python 版本（默认: 3.14.6，精确 patch 版本）
.PARAMETER Tag
    自定义镜像标签
.PARAMETER NoCache
    禁用 Docker 构建缓存
.PARAMETER NoVerify
    跳过构建后验证
.PARAMETER Quiet
    抑制容器内横幅输出
.PARAMETER Verbose
    启用详细调试日志
.PARAMETER NoLogFile
    不保存构建日志到 logs/ 目录
.PARAMETER LogFormat
    结构化日志格式: text (默认) 或 json
.PARAMETER LogLevel
    结构化日志级别: DEBUG/INFO/WARN/ERROR
.PARAMETER LogJson
    同时输出 JSON Lines 事件到 stdout
.PARAMETER LogJsonOutput
    JSON 日志输出文件路径（默认: $env:TEMP\pytorch-base-events.jsonl）
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测 Ubuntu）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\build.ps1
    # 默认 GPU 版本构建（CUDA 12.6）
.EXAMPLE
    .\build.ps1 -Cpu
    # 构建 CPU 版本
.EXAMPLE
    .\build.ps1 -Cuda 13.0
.EXAMPLE
    .\build.ps1 -LogFormat json -LogJson
    # JSON 格式输出（供监控平台采集）
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$Cpu,
    [ValidateSet("12.6", "12.8", "13.0")]
    [string]$Cuda = "12.6",
    [switch]$Offline,
    [switch]$PrepareOffline,
    [string]$TorchVersion = "2.13.0",
    [string]$PythonVersion = "3.14.6",
    [string]$Tag = "",
    [switch]$NoCache,
    [switch]$NoVerify,
    [switch]$Quiet,
    [switch]$Verbose,
    [switch]$NoLogFile,
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
$LogService = "pytorch-base-build-ps"
if (-not $LogJsonOutput) {
    $LogJsonOutput = Join-Path $env:TEMP "pytorch-base-events.jsonl"
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
$buildType = if ($Cpu) { "cpu" } else { "gpu" }
$LogFields["build_type"] = $buildType
$LogFields["cuda_version"] = $Cuda
$LogFields["python_version"] = $PythonVersion
$LogFields["pytorch_version"] = $TorchVersion
Write-JsonEvent -Event "ps_build_start" -Fields @{
    offline = "$($Offline.IsPresent)"
    prepare_offline = "$($PrepareOffline.IsPresent)"
    no_cache = "$($NoCache.IsPresent)"
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
$appDir = $scriptDir

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
$bashArgs = @()
if ($Cpu) { $bashArgs += "--cpu" }
if ($Cuda -ne "12.6") { $bashArgs += "--cuda"; $bashArgs += $Cuda }
if ($Offline) { $bashArgs += "--offline" }
if ($PrepareOffline) { $bashArgs += "--prepare-offline" }
if ($TorchVersion -ne "2.13.0") { $bashArgs += "--torch-version"; $bashArgs += $TorchVersion }
if ($PythonVersion -ne "3.14.6") { $bashArgs += "--python-version"; $bashArgs += $PythonVersion }
if ($Tag) { $bashArgs += "--tag"; $bashArgs += $Tag }
if ($NoCache) { $bashArgs += "--no-cache" }
if ($NoVerify) { $bashArgs += "--no-verify" }
if ($Quiet) { $bashArgs += "--quiet" }
if ($Verbose) { $bashArgs += "--verbose" }
if ($NoLogFile) { $bashArgs += "--no-log-file" }
if ($LogFormat -ne "text") { $bashArgs += "--log-format=$LogFormat" }
if ($LogLevel -ne "INFO") { $bashArgs += "--log-level=$LogLevel" }
if ($LogJson) { $bashArgs += "--log-json" }

# ── 6. 执行构建 ──
Write-StepOut "开始构建 PyTorch Base 镜像"
Write-Info "构建类型: $(if ($Cpu) { 'CPU' } else { 'GPU (CUDA ' + $Cuda + ')' })"
Write-Info "调用 WSL: bash build.sh $($bashArgs -join ' ')"
if ($LogFormat -eq "text" -or $LogJson) { Write-Host "" }

$startTime = Get-Date
wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash build.sh $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

Write-JsonMetric -Name "ps_build_duration_seconds" -Value $duration -Unit "seconds"

if ($LogFormat -eq "text" -or $LogJson) { Write-Host "" }

if ($exitCode -eq 0) {
    Write-StepOut "构建成功"
    Write-OkOut "总耗时: $duration 秒"
    Write-JsonEvent -Event "ps_build_complete" -Fields @{ status="success"; duration="$duration"; exit_code=0; build_type=$buildType }
    Write-JsonMetric -Name "ps_build_exit_code" -Value 0
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "构建日志保存于: logs/ 目录" -ForegroundColor Cyan
        Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
    }
} else {
    Write-StepOut "构建失败"
    Write-ErrOut "退出码: $exitCode"
    Write-ErrOut "耗时: $duration 秒"
    Write-JsonEvent -Event "ps_build_complete" -Fields @{ status="failed"; duration="$duration"; exit_code=$exitCode; build_type=$buildType }
    Write-JsonMetric -Name "ps_build_exit_code" -Value $exitCode
    if ($LogFormat -eq "text" -or $LogJson) {
        Write-Host ""
        Write-Host "故障排查：" -ForegroundColor Yellow
        Write-Host "  1. 查看 logs/ 目录下的完整构建日志"
        Write-Host "  2. 检查 Docker daemon 是否正常运行"
        Write-Host "  3. 网络问题可检查镜像源配置"
        Write-Host "  4. 离线构建请先使用 -PrepareOffline 下载资源"
        Write-Host ""
        Write-Host "JSON 事件日志: $LogJsonOutput" -ForegroundColor Gray
    }
}

exit $exitCode
