#Requires -Version 5.1
# ==============================================================================
# SpecWeave PowerShell 通用工具库 (utils.ps1)
# ==============================================================================
# 提供通用辅助函数：路径解析、环境检测、结构化日志输出、条件执行等。
# 遵循 SpecWeave PowerShell 7 脚本规范：
#   - dot-source 共享版本校验库 pwsh7-version-check.ps1（不重复定义版本校验函数）
#   - UTF-8 编码强制
#   - 结构化日志输出
#   - 不使用 pwsh7 专属语法（??、?:、??=、ForEach-Object -Parallel 等）
#
# 依赖：pwsh7-version-check.ps1（同目录）
# 使用方法：
#   . "$PSScriptRoot/../lib/utils.ps1"
# ==============================================================================

# 引入共享版本校验库（幂等安全，多次 dot-source 不会重复定义）
. "$PSScriptRoot/pwsh7-version-check.ps1"

# 直接运行时执行版本校验（dot-source 时由调用方负责）
if ($MyInvocation.InvocationName -ne '.') {
    if (-not (Test-Pwsh7Version)) {
        Show-Pwsh7VersionError
    }
}

# ==============================================================================
# UTF-8 编码设置（库加载时即生效）
# ==============================================================================
try { chcp 65001 > $null 2>&1 } catch {}
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
$global:OutputEncoding = [Console]::OutputEncoding
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

$ErrorActionPreference = "Stop"

# ==============================================================================
# 结构化日志函数
# ==============================================================================

<#
.SYNOPSIS
    输出信息级日志（绿色）
#>
function Write-Info {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

<#
.SYNOPSIS
    输出警告级日志（黄色）
#>
function Write-WarnOut {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )
    Write-Host "[WARN] $Message" -ForegroundColor Yellow
}

<#
.SYNOPSIS
    输出错误级日志（红色）
#>
function Write-ErrOut {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

<#
.SYNOPSIS
    输出步骤标题（青色分隔线）
#>
function Write-Step {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Title
    )
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  $Title" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
}

<#
.SYNOPSIS
    输出成功消息（绿色）
#>
function Write-Success {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message
    )
    Write-Host "[OK] $Message" -ForegroundColor Green
}

<#
.SYNOPSIS
    输出失败消息（红色），可选退出
#>
function Write-Fail {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,
        [switch]$Exit
    )
    Write-Host "[FAIL] $Message" -ForegroundColor Red
    if ($Exit) {
        exit 1
    }
}

# ==============================================================================
# 路径工具函数
# ==============================================================================

<#
.SYNOPSIS
    解析项目根目录（向上查找含 .agents/ 目录的路径）
#>
function Resolve-ProjectRoot {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $false)]
        [string]$StartPath = $PSScriptRoot
    )

    $current = Resolve-Path -LiteralPath $StartPath -ErrorAction SilentlyContinue
    if (-not $current) {
        $current = (Get-Location).Path
    }

    while ($current) {
        if (Test-Path -LiteralPath (Join-Path $current '.agents') -PathType Container) {
            return $current
        }
        $parent = Split-Path -Parent $current
        if ($parent -eq $current) { break }
        $current = $parent
    }

    return (Get-Location).Path
}

<#
.SYNOPSIS
    将相对路径解析为绝对路径（相对于指定基路径）
#>
function Resolve-RelativePath {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path,
        [Parameter(Mandatory = $false)]
        [string]$BasePath = $PWD.Path
    )

    if ([System.IO.Path]::IsPathRooted($Path)) {
        return $Path
    }
    return [System.IO.Path]::GetFullPath((Join-Path $BasePath $Path))
}

<#
.SYNOPSIS
    确保目录存在，不存在则创建
#>
function Ensure-Directory {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )
    if (-not (Test-Path -LiteralPath $Path -PathType Container)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
    }
    return (Resolve-Path -LiteralPath $Path).Path
}

# ==============================================================================
# 环境检测函数
# ==============================================================================

<#
.SYNOPSIS
    检测是否在 Windows 平台
#>
function Test-WindowsPlatform {
    [CmdletBinding()]
    param()
    if ($PSVersionTable.PSVersion.Major -ge 6) {
        return $IsWindows
    }
    return (-not (Test-Path variable:IsWindows)) -or $IsWindows
}

<#
.SYNOPSIS
    检测是否在 WSL 环境中
#>
function Test-WslEnvironment {
    [CmdletBinding()]
    param()
    if (Test-WindowsPlatform) { return $false }
    if (Test-Path /proc/version) {
        $version = Get-Content /proc/version -Raw -ErrorAction SilentlyContinue
        if ($version -and $version -match 'microsoft|wsl|WSL') {
            return $true
        }
    }
    return $false
}

<#
.SYNOPSIS
    检测是否在 CI 环境中（常见 CI 环境变量）
#>
function Test-CiEnvironment {
    [CmdletBinding()]
    param()
    $ciVars = @('CI','GITHUB_ACTIONS','GITLAB_CI','JENKINS_URL','TF_BUILD','APPVEYOR','TRAVIS','CIRCLECI')
    foreach ($var in $ciVars) {
        if ([Environment]::GetEnvironmentVariable($var)) {
            return $true
        }
    }
    return $false
}

<#
.SYNOPSIS
    获取当前 PowerShell 版本信息摘要
#>
function Get-PwshInfo {
    [CmdletBinding()]
    param()
    return [PSCustomObject]@{
        PSEdition       = $PSVersionTable.PSEdition
        PSVersion       = $PSVersionTable.PSVersion
        IsCore          = ($PSVersionTable.PSEdition -eq 'Core')
        IsPwsh7         = (Test-Pwsh7Version)
        Platform        = if (Test-WindowsPlatform) { 'Windows' } elseif (Test-WslEnvironment) { 'WSL' } else { 'Unix' }
        IsCI            = (Test-CiEnvironment)
        Encoding        = [Console]::OutputEncoding.WebName
    }
}

# ==============================================================================
# 条件执行与安全工具
# ==============================================================================

<#
.SYNOPSIS
    DryRun 模式包装器：如果启用 DryRun 则跳过实际操作只输出计划
#>
function Invoke-SafeCommand {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$ScriptBlock,
        [Parameter(Mandatory = $false)]
        [string]$Description = "",
        [switch]$DryRun
    )
    if ($DryRun) {
        Write-WarnOut "[DRY-RUN] $Description"
        return
    }
    if ($Description) {
        Write-Info $Description
    }
    & $ScriptBlock
}

<#
.SYNOPSIS
    带重试的命令执行
#>
function Invoke-WithRetry {
    [CmdletBinding()]
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$ScriptBlock,
        [Parameter(Mandatory = $false)]
        [int]$MaxRetries = 3,
        [Parameter(Mandatory = $false)]
        [int]$RetryDelaySeconds = 2,
        [Parameter(Mandatory = $false)]
        [string]$Description = "命令"
    )

    $attempt = 0
    while ($attempt -lt $MaxRetries) {
        $attempt++
        try {
            Write-Info "[$Description] 尝试 $attempt/$MaxRetries"
            $result = & $ScriptBlock
            return $result
        }
        catch {
            if ($attempt -ge $MaxRetries) {
                Write-ErrOut "[$Description] 所有 $MaxRetries 次尝试均失败：$_"
                throw
            }
            Write-WarnOut "[$Description] 第 $attempt 次失败：$_.${RetryDelaySeconds}秒后重试..."
            Start-Sleep -Seconds $RetryDelaySeconds
        }
    }
}

# ==============================================================================
# 库加载完成提示（仅在直接运行时显示）
# ==============================================================================
if ($MyInvocation.InvocationName -ne '.') {
    Write-Step "utils.ps1 工具库"
    $info = Get-PwshInfo
    Write-Info "PSEdition   : $($info.PSEdition)"
    Write-Info "PSVersion   : $($info.PSVersion)"
    Write-Info "Platform    : $($info.Platform)"
    Write-Info "Encoding    : $($info.Encoding)"
    Write-Info "IsCI        : $($info.IsCI)"
    Write-Host ""
    Write-Info "可用函数："
    Write-Host "  日志：Write-Info, Write-WarnOut, Write-ErrOut, Write-Step, Write-Success, Write-Fail" -ForegroundColor Gray
    Write-Host "  路径：Resolve-ProjectRoot, Resolve-RelativePath, Ensure-Directory" -ForegroundColor Gray
    Write-Host "  环境：Test-WindowsPlatform, Test-WslEnvironment, Test-CiEnvironment, Get-PwshInfo" -ForegroundColor Gray
    Write-Host "  执行：Invoke-SafeCommand (DryRun), Invoke-WithRetry" -ForegroundColor Gray
    Write-Host ""
}
