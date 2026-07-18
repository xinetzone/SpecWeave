#Requires -Version 5.1
<#
.SYNOPSIS
    SpecWeave Windows终端UTF-8环境一键配置脚本
.DESCRIPTION
    引导用户完成Windows终端UTF-8编码的完整配置，包括：
    - 当前会话编码设置
    - 用户级持久化配置（环境变量 + PowerShell Profile）
    - CMD AutoRun配置
    - Git编码配置（可选）
    - Windows系统级UTF-8 Beta支持提示
.PARAMETER Scope
    配置范围: Session(仅当前会话) / User(用户级,推荐) / System(系统级,需管理员)
.PARAMETER NonInteractive
    非交互模式,自动执行所有推荐配置
.PARAMETER WhatIf
    预览模式,显示将要执行的操作但不实际修改
.PARAMETER SkipGit
    跳过Git编码配置
.PARAMETER SkipVerify
    跳过最后验证
.EXAMPLE
    .\setup-utf8-env.ps1
    交互模式运行,引导用户选择配置范围
.EXAMPLE
    .\setup-utf8-env.ps1 -Scope User -WhatIf
    预览用户级配置将要执行的操作
.EXAMPLE
    .\setup-utf8-env.ps1 -NonInteractive
    非交互模式,自动执行推荐的用户级配置
.NOTES
    编码: UTF-8 BOM + CRLF
    兼容: PowerShell 5.1 / 7.x
#>
[CmdletBinding(SupportsShouldProcess=$true)]
param(
    [ValidateSet('Session', 'User', 'System')]
    [string]$Scope,
    [switch]$NonInteractive,
    [switch]$SkipGit,
    [switch]$SkipVerify
)

$ErrorActionPreference = 'Continue'

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $scriptPath }
# 脚本位于 .agents/scripts/ 下，项目根目录为两级父目录
$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptDir)
$scriptsDir = $scriptDir

$checkEncodingPath = Join-Path $scriptsDir 'check-encoding.ps1'
$installProfilePath = Join-Path $scriptsDir 'Install-Profile.ps1'
$setupCmdUtf8Path = Join-Path $scriptsDir 'setup-cmd-utf8.ps1'
$verifyEncodingPath = Join-Path $scriptsDir 'verify-encoding.ps1'

# sitecustomize.py 现位于 .agents/scripts/，需将其加入 PYTHONPATH 才能被 Python 自动加载
$pythonPathEntry = $scriptsDir

function Test-IsAdmin {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Test-IsWindowsTerminal {
    return $env:WT_SESSION -ne $null
}

function Test-IsTraeIDE {
    return $env:TERM_PROGRAM -eq 'Trae' -or $env:VSCODE_PID -ne $null
}

function Set-CurrentSessionEncoding {
    param([bool]$WhatIfMode)

    Write-Host ''
    Write-Host '[配置] 设置当前会话编码...' -ForegroundColor Cyan

    if ($WhatIfMode) {
        Write-Host '  [WhatIf] 将设置当前会话环境变量:' -ForegroundColor DarkGray
        Write-Host "    `$env:PYTHONIOENCODING = 'utf-8'" -ForegroundColor DarkGray
        Write-Host "    `$env:PYTHONUTF8 = '1'" -ForegroundColor DarkGray
        Write-Host "    `$env:PYTHONPATH 将追加: $pythonPathEntry (用于sitecustomize.py自动加载)" -ForegroundColor DarkGray
        Write-Host '  [WhatIf] 将执行: chcp 65001' -ForegroundColor DarkGray
        Write-Host '  [WhatIf] 将设置控制台编码为UTF-8' -ForegroundColor DarkGray
    } else {
        $env:PYTHONIOENCODING = 'utf-8'
        $env:PYTHONUTF8 = '1'
        # 将 .agents/scripts/ 加入 PYTHONPATH，确保 Python 启动时自动加载 sitecustomize.py
        if ($env:PYTHONPATH) {
            if ($env:PYTHONPATH -notlike "*$pythonPathEntry*") {
                $env:PYTHONPATH = "$env:PYTHONPATH;$pythonPathEntry"
            }
        } else {
            $env:PYTHONPATH = $pythonPathEntry
        }
        chcp 65001 > $null 2>&1
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        [Console]::InputEncoding = [System.Text.Encoding]::UTF8
        $OutputEncoding = [System.Text.Encoding]::UTF8
        if ($PSVersionTable.PSVersion.Major -ge 7) {
            $PSDefaultParameterValues['*:Encoding'] = 'utf8'
        }
        Write-Host '  [完成] 当前会话编码已设置为UTF-8' -ForegroundColor Green
    }
}

function Set-PersistentEnvironmentVariables {
    param(
        [System.EnvironmentVariableTarget]$Target,
        [bool]$WhatIfMode
    )

    $targetDesc = switch ($Target) {
        'User' { '用户级(HKCU)' }
        'Machine' { '系统级(HKLM)' }
    }

    Write-Host ''
    Write-Host "[配置] 设置$targetDesc环境变量..." -ForegroundColor Cyan

    $vars = @(
        @{ Name = 'PYTHONIOENCODING'; Value = 'utf-8' },
        @{ Name = 'PYTHONUTF8'; Value = '1' }
    )

    foreach ($var in $vars) {
        $current = [Environment]::GetEnvironmentVariable($var.Name, $Target)
        if ($current -eq $var.Value) {
            Write-Host "  [跳过] $($var.Name) 已设置为 '$($var.Value)'" -ForegroundColor Yellow
            continue
        }

        if ($WhatIfMode) {
            Write-Host "  [WhatIf] 将设置 [Environment]::SetEnvironmentVariable('$($var.Name)', '$($var.Value)', '$Target')" -ForegroundColor DarkGray
        } else {
            [Environment]::SetEnvironmentVariable($var.Name, $var.Value, $Target)
            Write-Host "  [完成] 已设置 $($var.Name) = '$($var.Value)'" -ForegroundColor Green
        }
    }

    # 持久化 PYTHONPATH：确保 sitecustomize.py 在新终端中也能被 Python 自动加载
    $currentPythonPath = [Environment]::GetEnvironmentVariable('PYTHONPATH', $Target)
    if ($currentPythonPath -and ($currentPythonPath -split ';' -contains $pythonPathEntry)) {
        Write-Host "  [跳过] PYTHONPATH 已包含 '$pythonPathEntry'" -ForegroundColor Yellow
    } else {
        $newPythonPath = if ($currentPythonPath) { "$currentPythonPath;$pythonPathEntry" } else { $pythonPathEntry }
        if ($WhatIfMode) {
            Write-Host "  [WhatIf] 将设置 PYTHONPATH = '$newPythonPath'" -ForegroundColor DarkGray
        } else {
            [Environment]::SetEnvironmentVariable('PYTHONPATH', $newPythonPath, $Target)
            Write-Host "  [完成] 已将 '$pythonPathEntry' 追加到 PYTHONPATH" -ForegroundColor Green
        }
    }
}

function Invoke-ProfileInstallation {
    param([bool]$WhatIfMode)

    Write-Host ''
    Write-Host '[配置] 安装PowerShell Profile...' -ForegroundColor Cyan

    if (-not (Test-Path -LiteralPath $installProfilePath)) {
        Write-Host "  [警告] 未找到Install-Profile.ps1: $installProfilePath" -ForegroundColor Yellow
        return
    }

    if ($WhatIfMode) {
        Write-Host "  [WhatIf] 将执行: & '$installProfilePath'" -ForegroundColor DarkGray
    } else {
        & $installProfilePath
    }
}

function Invoke-CmdUtf8Setup {
    param(
        [bool]$SystemLevel,
        [bool]$WhatIfMode
    )

    Write-Host ''
    Write-Host '[配置] 设置CMD AutoRun UTF-8...' -ForegroundColor Cyan

    if (-not (Test-Path -LiteralPath $setupCmdUtf8Path)) {
        Write-Host "  [警告] 未找到setup-cmd-utf8.ps1: $setupCmdUtf8Path" -ForegroundColor Yellow
        return
    }

    $cmdParams = @{}
    if ($SystemLevel) { $cmdParams['SystemLevel'] = $true }
    if ($WhatIfMode) { $cmdParams['WhatIf'] = $true }

    & $setupCmdUtf8Path @cmdParams
}

function Set-GitEncoding {
    param([bool]$WhatIfMode)

    Write-Host ''
    Write-Host '[配置] Git编码配置...' -ForegroundColor Cyan

    $gitCmd = Get-Command git -ErrorAction SilentlyContinue
    if (-not $gitCmd) {
        Write-Host '  [跳过] 未检测到Git' -ForegroundColor Yellow
        return
    }

    $gitConfigs = @(
        @{ Key = 'i18n.commitencoding'; Value = 'utf-8' },
        @{ Key = 'i18n.logoutputencoding'; Value = 'utf-8' },
        @{ Key = 'core.quotepath'; Value = 'false' }
    )

    foreach ($cfg in $gitConfigs) {
        $current = git config --global --get $cfg.Key 2>$null
        if ($current -eq $cfg.Value) {
            Write-Host "  [跳过] git config --global $($cfg.Key) 已设置为 '$($cfg.Value)'" -ForegroundColor Yellow
            continue
        }

        if ($WhatIfMode) {
            Write-Host "  [WhatIf] 将执行: git config --global $($cfg.Key) '$($cfg.Value)'" -ForegroundColor DarkGray
        } else {
            git config --global $cfg.Key $cfg.Value
            Write-Host "  [完成] 已设置 git config --global $($cfg.Key) = '$($cfg.Value)'" -ForegroundColor Green
        }
    }
}

function Show-SystemUtf8BetaTip {
    Write-Host ''
    Write-Host '[提示] Windows系统级UTF-8 Beta支持 (可选)' -ForegroundColor Cyan
    Write-Host '  如需启用系统级UTF-8支持(Beta),请按以下步骤操作:' -ForegroundColor White
    Write-Host '  1. 按 Win+R 输入 intl.cpl 回车' -ForegroundColor Gray
    Write-Host '  2. 切换到"管理"选项卡' -ForegroundColor Gray
    Write-Host '  3. 点击"更改系统区域设置"' -ForegroundColor Gray
    Write-Host '  4. 勾选"Beta: 使用Unicode UTF-8提供全球语言支持"' -ForegroundColor Gray
    Write-Host '  5. 重启计算机生效' -ForegroundColor Gray
    Write-Host '  注意: 此设置可能影响某些旧程序的兼容性,请谨慎启用' -ForegroundColor Yellow
}

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  SpecWeave UTF-8 环境配置工具' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host "PowerShell版本: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
Write-Host "项目根目录: $projectRoot" -ForegroundColor Gray
Write-Host ''

if (Test-IsWindowsTerminal) {
    Write-Host '[检测] 当前运行在 Windows Terminal' -ForegroundColor Green
}
if (Test-IsTraeIDE) {
    Write-Host '[检测] 当前运行在 Trae IDE / VS Code 终端' -ForegroundColor Green
}

Write-Host ''
Write-Host '[步骤1/8] 运行编码诊断...' -ForegroundColor Cyan
if (-not (Test-Path -LiteralPath $checkEncodingPath)) {
    Write-Host "  [错误] 未找到诊断脚本: $checkEncodingPath" -ForegroundColor Red
    exit 1
}

$diagResult = & $checkEncodingPath -Json 2>$null | ConvertFrom-Json -ErrorAction SilentlyContinue
& $checkEncodingPath

if ($diagResult) {
    Write-Host ''
    Write-Host '[诊断摘要]' -ForegroundColor White
    $scoreColor = if ($diagResult.summary.health_score -ge 90) { 'Green' } elseif ($diagResult.summary.health_score -ge 70) { 'Yellow' } else { 'Red' }
    Write-Host "  健康评分: $($diagResult.summary.health_score)%" -ForegroundColor $scoreColor
    Write-Host "  通过: $($diagResult.summary.pass), 警告: $($diagResult.summary.warnings), 错误: $($diagResult.summary.errors)" -ForegroundColor Gray
}

$selectedScope = $Scope
if (-not $selectedScope -and -not $NonInteractive) {
    Write-Host ''
    Write-Host '[步骤2/8] 选择配置范围:' -ForegroundColor Cyan
    Write-Host '  [1] 仅当前会话 (立即生效,不持久化)' -ForegroundColor White
    Write-Host '  [2] 用户级配置 (推荐,持久化到用户环境变量和Profile,无需管理员)' -ForegroundColor Green
    Write-Host '  [3] 系统级配置 (需要管理员权限,影响所有用户)' -ForegroundColor Yellow
    Write-Host '  [0] 取消' -ForegroundColor Gray
    Write-Host ''

    $choice = Read-Host '请选择 [0-3] (默认2)'
    if (-not $choice) { $choice = '2' }

    switch ($choice) {
        '0' { Write-Host '已取消配置' -ForegroundColor Yellow; exit 0 }
        '1' { $selectedScope = 'Session' }
        '2' { $selectedScope = 'User' }
        '3' { $selectedScope = 'System' }
        default { Write-Host '无效选择,使用默认(User)' -ForegroundColor Yellow; $selectedScope = 'User' }
    }
} elseif ($NonInteractive -and -not $selectedScope) {
    $selectedScope = 'User'
    Write-Host "[非交互模式] 自动选择推荐配置范围: User" -ForegroundColor Cyan
}

if (-not $selectedScope) {
    $selectedScope = 'User'
}

Write-Host ''
$scopeColor = if ($selectedScope -eq 'User') { 'Green' } elseif ($selectedScope -eq 'System') { 'Yellow' } else { 'White' }
Write-Host "[配置范围] $selectedScope" -ForegroundColor $scopeColor

if ($selectedScope -eq 'System') {
    $isAdmin = Test-IsAdmin
    if (-not $isAdmin) {
        Write-Host ''
        Write-Host '[错误] 系统级配置需要管理员权限!' -ForegroundColor Red
        Write-Host '请以管理员身份重新运行PowerShell后再执行此脚本' -ForegroundColor Red
        if (-not $WhatIfPreference -and -not $WhatIf) {
            exit 1
        } else {
            Write-Host '[WhatIf] 预览模式下继续...' -ForegroundColor Yellow
        }
    }
}

$whatIfMode = $WhatIfPreference.IsPresent -or $WhatIf
if ($whatIfMode) {
    Write-Host ''
    Write-Host '========================================' -ForegroundColor DarkYellow
    Write-Host '  [WhatIf] 预览模式 - 不会实际修改' -ForegroundColor DarkYellow
    Write-Host '========================================' -ForegroundColor DarkYellow
}

Write-Host ''
Write-Host '[步骤3/8] 配置当前会话编码...' -ForegroundColor Cyan
Set-CurrentSessionEncoding -WhatIfMode $whatIfMode

$envTarget = $null
if ($selectedScope -eq 'User') {
    $envTarget = [System.EnvironmentVariableTarget]::User
} elseif ($selectedScope -eq 'System') {
    $envTarget = [System.EnvironmentVariableTarget]::Machine
}

if ($envTarget) {
    Write-Host ''
    Write-Host '[步骤4/8] 配置持久化环境变量...' -ForegroundColor Cyan
    Set-PersistentEnvironmentVariables -Target $envTarget -WhatIfMode $whatIfMode

    Write-Host ''
    Write-Host '[步骤5/8] 安装PowerShell Profile...' -ForegroundColor Cyan
    Invoke-ProfileInstallation -WhatIfMode $whatIfMode

    Write-Host ''
    Write-Host '[步骤6/8] 配置CMD AutoRun...' -ForegroundColor Cyan
    $sysLevel = ($selectedScope -eq 'System')
    Invoke-CmdUtf8Setup -SystemLevel $sysLevel -WhatIfMode $whatIfMode
} else {
    Write-Host ''
    Write-Host '[步骤4-6/8] Session模式跳过持久化配置' -ForegroundColor Yellow
}

$doGitConfig = -not $SkipGit
if ($doGitConfig -and -not $NonInteractive -and -not $whatIfMode) {
    Write-Host ''
    $gitChoice = Read-Host '[步骤7/8] 是否配置Git编码? [Y/n] (默认Y)'
    if ($gitChoice -match '^[Nn]') {
        $doGitConfig = $false
        Write-Host '  跳过Git配置' -ForegroundColor Yellow
    }
}

if ($doGitConfig) {
    Set-GitEncoding -WhatIfMode $whatIfMode
} else {
    Write-Host ''
    Write-Host '[步骤7/8] 跳过Git配置' -ForegroundColor Yellow
}

Show-SystemUtf8BetaTip

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
Write-Host '  配置完成!' -ForegroundColor Green
Write-Host '========================================' -ForegroundColor Cyan
Write-Host ''
Write-Host '[生效方式]' -ForegroundColor White
if ($selectedScope -eq 'Session') {
    Write-Host '  配置仅在当前会话生效' -ForegroundColor Gray
} else {
    Write-Host '  1. 立即在当前会话生效: . $PROFILE' -ForegroundColor Gray
    Write-Host '  2. 或重启终端使所有配置生效' -ForegroundColor Gray
}
Write-Host ''

if (-not $SkipVerify) {
    Write-Host '[步骤8/8] 验证配置...' -ForegroundColor Cyan
    if (Test-Path -LiteralPath $verifyEncodingPath) {
        & $verifyEncodingPath
    } else {
        Write-Host "  [警告] 未找到验证脚本: $verifyEncodingPath" -ForegroundColor Yellow
    }
}

if ($whatIfMode) {
    Write-Host ''
    Write-Host '========================================' -ForegroundColor DarkYellow
    Write-Host '  [WhatIf] 预览结束 - 以上操作未实际执行' -ForegroundColor DarkYellow
    Write-Host '  去掉 -WhatIf 参数后运行以实际应用配置' -ForegroundColor DarkYellow
    Write-Host '========================================' -ForegroundColor DarkYellow
}

exit 0
