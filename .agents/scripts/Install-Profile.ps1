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
[CmdletBinding()]
param(
    [switch]$Uninstall
)

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
