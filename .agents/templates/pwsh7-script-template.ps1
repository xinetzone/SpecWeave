# ==============================================================================
# SpecWeave 项目标准 PowerShell 7 脚本模板
# ==============================================================================
# 使用说明：
#   1. 复制本模板到目标位置，重命名为你的脚本名称
#   2. 修改 .SYNOPSIS/.DESCRIPTION 等帮助文档
#   3. 根据需要删除或修改示例参数、辅助函数
#   4. 在"主流程开始"区域编写你的业务逻辑
#   5. 版本校验代码为自包含，无需依赖外部 lib 文件
#   6. #Requires 声明为 5.1 是为了让 PowerShell 5.1 能启动并显示友好错误，
#      实际运行要求为 PowerShell 7.4+，版本不符会由自包含检测代码拦截
# ==============================================================================

#Requires -Version 5.1

<#
.SYNOPSIS
    脚本功能简述（请替换此描述）
.DESCRIPTION
    脚本详细功能说明（请替换此描述）。
    本脚本遵循 SpecWeave PowerShell 7 脚本规范，包含：
    - 自包含版本校验
    - UTF-8 编码强制
    - 结构化日志输出
    - 标准错误处理
.PARAMETER Path
    示例参数：目标路径（根据实际需求修改或删除）
.PARAMETER Verbose
    启用详细输出（CmdletBinding 内置支持）
.EXAMPLE
    pwsh -File .\your-script.ps1
    基础用法示例
.EXAMPLE
    pwsh -File .\your-script.ps1 -Path "C:\target" -Verbose
    带参数和详细输出的用法示例
.NOTES
    SpecWeave 标准脚本模板 v1.0
    兼容 PowerShell 7.4+
#>

[CmdletBinding()]
param(
    [Parameter(Mandatory = $false, HelpMessage = "示例参数：目标路径")]
    [string]$Path = $PWD.Path,

    [Parameter(Mandatory = $false, HelpMessage = "示例开关参数")]
    [switch]$DryRun
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

# ==============================================================================
# 全局错误处理设置
# ==============================================================================
$ErrorActionPreference = "Stop"

# ==============================================================================
# UTF-8 编码设置（强制控制台输出编码为 UTF-8）
# ==============================================================================
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
[Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
$OutputEncoding = [Console]::OutputEncoding
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

# ==============================================================================
# 辅助函数区域
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

# ==============================================================================
# 主流程开始
# ==============================================================================

Write-Step "脚本启动"
Write-Info "PowerShell 版本: $($PSVersionTable.PSVersion)"
Write-Info "控制台编码: $([Console]::OutputEncoding.WebName)"
Write-Info "工作目录: $Path"
if ($DryRun) {
    Write-WarnOut "DryRun 模式已启用，不会执行实际修改操作"
}

# TODO: 在此处编写你的业务逻辑
Write-Host ""
Write-Info "在此处添加你的脚本逻辑..."
Write-Host ""

# ==============================================================================
# 主流程结束
# ==============================================================================

Write-Step "执行完成"
Write-Info "脚本执行完毕"
exit 0
