#Requires -Version 5.1
<#
.SYNOPSIS
    安装/卸载 SpecWeave 项目PowerShell Profile到用户Profile。
.DESCRIPTION
    将项目profile.ps1的点源加载命令写入用户PowerShell Profile，
    使每次启动PowerShell时自动加载UTF-8编码环境设置。
.PARAMETER Uninstall
    移除项目profile的加载配置。
.EXAMPLE
    .\.agents\scripts\Install-Profile.ps1
    安装项目profile到用户PowerShell Profile。
.EXAMPLE
    .\.agents\scripts\Install-Profile.ps1 -Uninstall
    卸载项目profile，从用户Profile中移除加载配置。
.NOTES
    编码: UTF-8 BOM + CRLF
    兼容: PowerShell 5.1 / 7.x
#>

#Requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$Uninstall
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

$ErrorActionPreference = 'Stop'

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path -Parent $scriptPath
$projectProfilePath = Join-Path $scriptDir 'profile.ps1'
$resolvedProjectProfile = (Resolve-Path -LiteralPath $projectProfilePath -ErrorAction SilentlyContinue).Path

if (-not $resolvedProjectProfile) {
    Write-Error "无法找到项目profile.ps1: $projectProfilePath"
    exit 1
}

$markerStart = '# >>> SpecWeave Profile >>>'
$markerEnd = '# <<< SpecWeave Profile <<<'

$userProfilePath = $PROFILE
$userProfileDir = Split-Path -Parent $userProfilePath

if (-not (Test-Path -LiteralPath $userProfileDir)) {
    New-Item -ItemType Directory -Path $userProfileDir -Force | Out-Null
    Write-Host "[创建] 用户Profile目录: $userProfileDir" -ForegroundColor Cyan
}

$profileContent = ''
if (Test-Path -LiteralPath $userProfilePath) {
    $profileContent = Get-Content -LiteralPath $userProfilePath -Raw -Encoding UTF8
    if ($null -eq $profileContent) {
        $profileContent = ''
    }
}

$markerPattern = [regex]::Escape($markerStart) + '[\s\S]*?' + [regex]::Escape($markerEnd)
$hasSpecWeaveBlock = [regex]::IsMatch($profileContent, $markerPattern)

if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $userProfilePath) -or -not $hasSpecWeaveBlock) {
        Write-Host "[信息] 未检测到SpecWeave Profile配置，无需卸载。" -ForegroundColor Yellow
    } else {
        $newContent = [regex]::Replace($profileContent, $markerPattern + '\r?\n?', '')
        $newContent = $newContent.TrimEnd() + "`r`n"
        [System.IO.File]::WriteAllText($userProfilePath, $newContent, [System.Text.UTF8Encoding]::new($true))
        Write-Host "[卸载] 已从用户Profile中移除SpecWeave配置。" -ForegroundColor Green
        Write-Host "  Profile路径: $userProfilePath"
    }
} else {
    $dotSourceLine = ". '$resolvedProjectProfile'"
    $specWeaveBlock = "$markerStart`r`n$dotSourceLine`r`n$markerEnd"

    if ($hasSpecWeaveBlock) {
        $newContent = [regex]::Replace($profileContent, $markerPattern, $specWeaveBlock)
        [System.IO.File]::WriteAllText($userProfilePath, $newContent, [System.Text.UTF8Encoding]::new($true))
        Write-Host "[更新] 已更新用户Profile中的SpecWeave配置。" -ForegroundColor Green
    } else {
        if ($profileContent.Length -gt 0) {
            $profileContent = $profileContent.TrimEnd("`r", "`n") + "`r`n"
        }
        $newContent = $profileContent + $specWeaveBlock + "`r`n"
        [System.IO.File]::WriteAllText($userProfilePath, $newContent, [System.Text.UTF8Encoding]::new($true))
        Write-Host "[安装] 已将SpecWeave Profile配置添加到用户Profile。" -ForegroundColor Green
    }
    Write-Host "  项目Profile: $resolvedProjectProfile"
    Write-Host "  用户Profile: $userProfilePath"
}

Write-Host ""
if ($Uninstall) {
    Write-Host "提示: 重启PowerShell后卸载生效。" -ForegroundColor Yellow
} else {
    Write-Host "提示: 重启PowerShell后自动加载UTF-8编码环境。" -ForegroundColor Yellow
    Write-Host "      或执行以下命令立即生效: . '$resolvedProjectProfile'" -ForegroundColor DarkGray
}
