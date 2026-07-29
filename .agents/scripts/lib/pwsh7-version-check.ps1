#Requires -Version 5.1
# ==============================================================================
# SpecWeave PowerShell 7 版本校验库（可复用共享模块）
# ==============================================================================
# 检测当前运行环境是否为 PowerShell 7.4+ (pwsh7)。
# 兼容 Windows PowerShell 5.1（用于显示错误）和 PowerShell 7+。
# 不使用 pwsh7 专属语法（??、?:、??= 等）。
#
# 使用方法：
#   . "$PSScriptRoot/pwsh7-version-check.ps1"     # 在同目录 lib 脚本中
#   . "$PSScriptRoot/../lib/pwsh7-version-check.ps1"  # 在 scripts/ 目录脚本中
#
# 提供函数：
#   Test-Pwsh7Version [-PassThru]   # 检测是否满足 pwsh7.4+ 要求
#   Show-Pwsh7VersionError          # 显示友好错误信息并 exit 1
#   Test-Pwsh7Requirement           # Test-Pwsh7Version 的别名（向后兼容）
#   Show-Pwsh7RequirementError      # Show-Pwsh7VersionError 的别名（向后兼容）
#
# 幂等安全：多次 dot-source 不会重复定义函数或产生副作用。
# ==============================================================================

# 幂等守卫：已加载则跳过
if (Get-Variable -Name 'Pwsh7VersionCheckLoaded' -Scope Script -ErrorAction SilentlyContinue) {
    return
}
$script:Pwsh7VersionCheckLoaded = $true

function Test-Pwsh7Version {
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

function Show-Pwsh7VersionError {
    [CmdletBinding()]
    param()

    $checkResult = Test-Pwsh7Version -PassThru

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
    $supported = Test-Pwsh7Version
    if (-not $supported) {
        Show-Pwsh7VersionError
    }
}

# ==============================================================================
# 向后兼容别名（wrapper 函数，确保旧脚本中使用的旧名称仍然有效）
# ==============================================================================
function Test-Pwsh7Requirement {
    [CmdletBinding()]
    param([switch]$PassThru)
    Test-Pwsh7Version @PSBoundParameters
}

function Show-Pwsh7RequirementError {
    [CmdletBinding()]
    param()
    Show-Pwsh7VersionError
}
