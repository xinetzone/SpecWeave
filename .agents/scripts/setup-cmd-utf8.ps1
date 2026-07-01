#Requires -Version 5.1
[CmdletBinding(SupportsShouldProcess=$true, ConfirmImpact='Medium')]
param(
    [switch]$SystemLevel,
    [switch]$Undo
)

$ErrorActionPreference = 'Stop'

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

$MarkerStart = ':: >>> SpecWeave CMD UTF-8 >>>'
$MarkerEnd = ':: <<< SpecWeave CMD UTF-8 <<<'
$Utf8Command = '@chcp 65001>nul'

if ($SystemLevel) {
    $RegPath = 'HKLM:\Software\Microsoft\Command Processor'
    $ScopeDesc = '系统级(HKLM)'
}
else {
    $RegPath = 'HKCU:\Software\Microsoft\Command Processor'
    $ScopeDesc = '用户级(HKCU)'
}
$ValueName = 'AutoRun'

function Get-CurrentAutoRun {
    if (Test-Path $RegPath) {
        $item = Get-ItemProperty -Path $RegPath -Name $ValueName -ErrorAction SilentlyContinue
        if ($null -ne $item -and $null -ne $item.$ValueName) {
            return $item.$ValueName
        }
    }
    return $null
}

function Set-AutoRunValue {
    param([string]$Value)

    if (-not (Test-Path $RegPath)) {
        if ($PSCmdlet.ShouldProcess($RegPath, '创建注册表项')) {
            New-Item -Path $RegPath -Force | Out-Null
        }
    }

    if ($null -eq $Value -or $Value -eq '') {
        if ($PSCmdlet.ShouldProcess("$RegPath\$ValueName", '删除注册表值')) {
            Remove-ItemProperty -Path $RegPath -Name $ValueName -ErrorAction SilentlyContinue
        }
    }
    else {
        if ($PSCmdlet.ShouldProcess("$RegPath\$ValueName", '设置注册表值')) {
            Set-ItemProperty -Path $RegPath -Name $ValueName -Value $Value -Type String
        }
    }
}

function Test-AlreadyConfigured {
    param([string]$Current)
    return $Current -and $Current.Contains($MarkerStart) -and $Current.Contains($MarkerEnd)
}

function Add-Utf8Config {
    param([string]$Current)

    if (Test-AlreadyConfigured -Current $Current) {
        return $Current
    }

    $block = "$MarkerStart&$Utf8Command&$MarkerEnd"

    if ($null -eq $Current -or $Current.Trim() -eq '') {
        return $block
    }
    else {
        return "$Current&$block"
    }
}

function Remove-Utf8Config {
    param([string]$Current)

    if (-not (Test-AlreadyConfigured -Current $Current)) {
        return $Current
    }

    $pattern = [regex]::Escape($MarkerStart) + '.*?' + [regex]::Escape($MarkerEnd)
    $result = [regex]::Replace($Current, $pattern, '', 'Singleline')

    $result = $result -replace '&+', '&'
    $result = $result.Trim('&').Trim()

    return $result
}

Write-Host '========================================' -ForegroundColor Cyan
Write-Host 'SpecWeave CMD UTF-8 配置工具' -ForegroundColor Cyan
Write-Host '========================================' -ForegroundColor Cyan
Write-Host "配置范围: $ScopeDesc" -ForegroundColor Gray
Write-Host "注册表路径: $RegPath" -ForegroundColor Gray
Write-Host ''

$currentValue = Get-CurrentAutoRun
if ($null -ne $currentValue -and $currentValue -ne '') {
    Write-Host '当前 AutoRun 值:' -ForegroundColor Yellow
    Write-Host "  $currentValue" -ForegroundColor Gray
}
else {
    Write-Host '当前无 AutoRun 配置' -ForegroundColor Yellow
}
Write-Host ''

if ($Undo) {
    Write-Host '[操作] 恢复原始配置（卸载UTF-8自动设置）' -ForegroundColor Yellow

    if (-not (Test-AlreadyConfigured -Current $currentValue)) {
        Write-Host '未检测到 SpecWeave 配置，无需操作' -ForegroundColor Green
        exit 0
    }

    $newValue = Remove-Utf8Config -Current $currentValue

    Write-Host '将修改为:' -ForegroundColor Yellow
    if ($null -eq $newValue -or $newValue -eq '') {
        Write-Host '  (删除AutoRun值)' -ForegroundColor Gray
    }
    else {
        Write-Host "  $newValue" -ForegroundColor Gray
    }
    Write-Host ''

    if ($PSCmdlet.ShouldProcess("$RegPath\$ValueName", '恢复原始配置')) {
        Set-AutoRunValue -Value $newValue
        Write-Host '已恢复原始配置' -ForegroundColor Green
        Write-Host ''
        Write-Host '请重启 CMD 使更改生效' -ForegroundColor Cyan
    }
}
else {
    if ($SystemLevel) {
        $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
        if (-not $isAdmin) {
            Write-Host '警告: 系统级配置需要管理员权限' -ForegroundColor Red
            Write-Host '请以管理员身份重新运行 PowerShell 后再执行此脚本' -ForegroundColor Red
            if (-not $WhatIfPreference) {
                exit 1
            }
        }
    }

    Write-Host '[操作] 添加UTF-8自动配置（chcp 65001）' -ForegroundColor Yellow

    if (Test-AlreadyConfigured -Current $currentValue) {
        Write-Host '已检测到 SpecWeave 配置，无需重复安装' -ForegroundColor Green
        exit 0
    }

    $newValue = Add-Utf8Config -Current $currentValue

    Write-Host '将设置为:' -ForegroundColor Yellow
    Write-Host "  $newValue" -ForegroundColor Gray
    Write-Host ''

    if ($PSCmdlet.ShouldProcess("$RegPath\$ValueName", '添加UTF-8配置')) {
        Set-AutoRunValue -Value $newValue
        Write-Host '配置已成功写入' -ForegroundColor Green
        Write-Host ''
        Write-Host '请重启 CMD 使更改生效' -ForegroundColor Cyan
        Write-Host '提示: 新打开的 CMD 窗口将自动使用 UTF-8 编码(65001)' -ForegroundColor Gray
        $undoCmd = '.\setup-cmd-utf8.ps1 -Undo'
        if ($SystemLevel) {
            $undoCmd = $undoCmd + ' -SystemLevel'
        }
        Write-Host "卸载: $undoCmd" -ForegroundColor DarkGray
    }
}

Write-Host ''
Write-Host '========================================' -ForegroundColor Cyan
