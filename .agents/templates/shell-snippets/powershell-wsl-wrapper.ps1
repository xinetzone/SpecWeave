#Requires -Version 5.1
<#
.SYNOPSIS
    TEMPLATE: PowerShell→WSL 跨Shell脚本包装器
.DESCRIPTION
    通用模板：从 Windows PowerShell/CMD 直接调用 wsl.exe 执行 WSL 内的 bash 脚本。
    自动完成：wsl检测 → 发行版选择 → 路径转换 → 环境预检 → 参数透传 → 执行 → 退出码传递。

    复用方法：
    1. 将本文件复制为你的项目包装器（如 deploy.ps1）
    2. 修改 $BashScript 为实际bash脚本路径
    3. 在 param() 中添加你的业务参数
    4. 在 $bashArgs 映射块中添加参数透传逻辑
    5. 自定义环境预检部分（Docker/Node/Python等）
    6. 自定义成功/失败输出信息

.PARAMETER LogFormat
    日志格式: text (默认) | json
.PARAMETER LogLevel
    日志级别: DEBUG|INFO|WARN|ERROR
.PARAMETER LogJson
    JSON 同时输出到 stdout
.PARAMETER Distribution
    WSL 发行版名称（默认自动检测 Ubuntu）
.PARAMETER Help
    显示帮助
.EXAMPLE
    .\wrapper.ps1
    # 默认执行
.EXAMPLE
    .\wrapper.ps1 -LogFormat json
    # JSON 格式输出（供监控采集）
.NOTES
    前置条件：WSL2 + 目标Linux发行版已安装
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    # ── 日志参数（通用，保留） ──
    [ValidateSet("text", "json")]
    [string]$LogFormat = "text",
    [ValidateSet("DEBUG", "INFO", "WARN", "ERROR")]
    [string]$LogLevel = "INFO",
    [switch]$LogJson,
    [string]$Distribution = "",
    [switch]$Help,

    # ── TODO: 在这里添加你的业务参数 ──
    # [switch]$MyFlag,
    # [string]$MyOption = "default",
    # [int]$MyPort = 8080,
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

# ── 颜色输出工具（可自定义） ──
function Write-Info { param([string]$Msg) Write-Host "[INFO]  $Msg" -ForegroundColor Green }
function Write-Warn { param([string]$Msg) Write-Host "[WARN]  $Msg" -ForegroundColor Yellow }
function Write-Err  { param([string]$Msg) Write-Host "[ERROR] $Msg" -ForegroundColor Red }
function Write-Ok   { param([string]$Msg) Write-Host "  OK   $Msg" -ForegroundColor Green }
function Write-Step { param([string]$Msg) Write-Host "`n=== $Msg ===" -ForegroundColor Cyan }

# ── TODO: 配置区（根据项目修改） ──
$BashScript = "scripts/my-script.sh"  # 相对于脚本所在目录的父目录（app dir）
$BashScriptDir = $false  # 如果bash脚本在scripts/下则为$true；如果bash脚本在app根目录则为$false
$InstallHint = "请参考项目部署文档安装所需环境"  # 环境缺失时的提示信息
# ── END 配置区 ──

# ── 1. 检测 wsl.exe ──
Write-Step "WSL 环境检测"
$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Write-Err "wsl.exe 未找到！请先安装 WSL2："
    Write-Err "  以管理员身份运行 PowerShell，执行："
    Write-Err "  wsl --install -d Ubuntu-24.04"
    Write-Err "  安装后重启计算机。"
    exit 1
}
Write-Ok "wsl.exe 可用"

# ── 2. 检测/选择 WSL 发行版 ──
$wslList = wsl.exe --list --verbose 2>&1
if ($LASTEXITCODE -ne 0 -or -not $wslList) {
    Write-Err "WSL 未正确安装或没有可用的发行版。"
    Write-Err "请执行: wsl --install -d Ubuntu-24.04"
    exit 1
}

if (-not $Distribution) {
    # 自动检测 Ubuntu 发行版（优先 24.04/26.04）
    $ubuntuDistros = $wslList | Where-Object { $_ -match 'Ubuntu' } | ForEach-Object {
        if ($_ -match '^\s*(\*?\s*)?(Ubuntu[\w.-]*)\s+') { $matches[2].Trim() }
    }
    if ($ubuntuDistros) {
        $Distribution = $ubuntuDistros[0]
        Write-Info "自动检测到 WSL 发行版: $Distribution"
    } else {
        $firstDistro = ($wslList | Select-String '^\s*\*?\s*(\S+)\s' | Select-Object -First 1)
        if ($firstDistro) {
            $Distribution = $firstDistro.Matches.Groups[1].Value.Trim('*').Trim()
            Write-Warn "未检测到 Ubuntu，使用发行版: $Distribution"
        } else {
            Write-Err "未找到可用的 WSL 发行版"; exit 1
        }
    }
}
Write-Ok "使用 WSL 发行版: $Distribution"

# ── 3. 路径转换：Windows → WSL ──
Write-Step "路径转换"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if ($BashScriptDir) {
    $appDir = Split-Path -Parent $scriptDir  # scripts/的父目录=app目录
} else {
    $appDir = $scriptDir  # bash脚本就在scripts/同级
}

function Convert-ToWslPath {
    param([string]$WindowsPath)
    # D:\spaces\project → /mnt/d/spaces/project
    $fullPath = [System.IO.Path]::GetFullPath($WindowsPath)
    $drive = $fullPath.Substring(0, 1).ToLower()
    $rest = $fullPath.Substring(2).Replace('\', '/')
    return "/mnt/$drive$rest"
}

$wslAppDir = Convert-ToWslPath $appDir
Write-Info "WSL 工作目录: $wslAppDir"

# ── 4. 环境预检（TODO: 根据项目需要自定义） ──
# 以下是Docker预检示例，可替换为Node/Python/Java等其他环境检测
Write-Step "环境预检测"

# 示例1：检测命令是否存在
$cmdCheck = wsl.exe -d $Distribution bash -c "which docker 2>/dev/null && echo OK || echo MISSING" 2>&1
if ($cmdCheck -match 'MISSING') {
    Write-Err "WSL 中所需命令不可用！"
    Write-Err $InstallHint
    exit 1
}
Write-Ok "命令可用"

# 示例2：检测服务是否运行（如Docker daemon）
# $svcCheck = wsl.exe -d $Distribution bash -c "docker info >/dev/null 2>&1 && echo OK || echo DOWN" 2>&1
# if ($svcCheck -match 'DOWN') {
#     Write-Err "服务未运行！"
#     Write-Err "请启动对应服务后重试"
#     exit 1
# }
# Write-Ok "服务运行中"

# ── 5. 参数映射：PowerShell → bash ──
$bashArgs = @()

# ── 日志参数（通用，保留） ──
if ($LogFormat -ne "text") { $bashArgs += "--log-format=$LogFormat" }
if ($LogLevel -ne "INFO")  { $bashArgs += "--log-level=$LogLevel" }
if ($LogJson)              { $bashArgs += "--log-json" }

# ── TODO: 在这里添加你的业务参数映射 ──
# if ($MyFlag)               { $bashArgs += "--my-flag" }
# if ($MyOption -ne "default") { $bashArgs += "--my-option"; $bashArgs += $MyOption }
# if ($MyPort -ne 8080)      { $bashArgs += "--my-port"; $bashArgs += "$MyPort" }

# ── 6. 执行 ──
Write-Step "开始执行"
$startTime = Get-Date
wsl.exe -d $Distribution --cd "$wslAppDir" bash -c "bash $BashScript $($bashArgs -join ' ')"
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

# ── 7. 结果输出（TODO: 自定义成功/失败信息） ──
Write-Host ""
if ($exitCode -eq 0) {
    Write-Step "执行成功"
    Write-Ok "总耗时: $duration 秒"
    # TODO: 添加成功后的连接信息/输出路径等
    # Write-Host "访问地址: http://localhost:8080" -ForegroundColor Cyan
} else {
    Write-Step "执行失败"
    Write-Err "退出码: $exitCode"
    Write-Err "耗时: $duration 秒"
    Write-Host ""
    Write-Host "故障排查：" -ForegroundColor Yellow
    # TODO: 添加排查指引
    # Write-Host "  1. 查看日志: ..."
    # Write-Host "  2. 诊断脚本: ..."
}

exit $exitCode
