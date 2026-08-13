#Requires -Version 5.1
# PWSH7-EXEMPT: Windows 系统维护脚本，有意兼容 Windows PowerShell 5.1，无需 pwsh7

<#
.SYNOPSIS
    修复 Windows 截图工具（ScreenSketch / Snipping Tool）启动报错。
.DESCRIPTION
    当截图工具启动时报错无法启动（AppModel-Runtime 事件 ID 208/216，错误码 0x80070002，
    配置 AppX 运行时进程失败）时，本脚本通过重新注册 ScreenSketch 应用包进行修复，
    并自动验证修复结果（触发启动 + 检查事件日志是否产生新的 208/216 错误）。
.PARAMETER PackageName
    要修复的应用包名称，默认 "Microsoft.ScreenSketch"。
.PARAMETER NoLaunch
    重注册后不触发启动验证（仅重注册并检查事件日志）。
.PARAMETER ShowErrorLog
    仅展示最近截图工具相关的 AppModel-Runtime 错误事件后退出，不执行修复。
.EXAMPLE
    .\fix-screenshot-tool.ps1
    重新注册截图工具并验证启动。
.EXAMPLE
    .\fix-screenshot-tool.ps1 -ShowErrorLog
    只查看当前截图工具相关的错误日志。
.EXAMPLE
    .\fix-screenshot-tool.ps1 -NoLaunch
    只重新注册，不自动启动应用。
.NOTES
    依据 2026-08-10 项目 memory「故障排查与修复方案」沉淀，复发时可直接复用本脚本。
#>

param(
    [string]$PackageName = 'Microsoft.ScreenSketch',
    [switch]$NoLaunch,
    [switch]$ShowErrorLog
)

$ErrorActionPreference = 'Continue'

# 确保中文输出在 PowerShell 5.1 控制台正确显示
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$runtimeLog = 'Microsoft-Windows-AppModel-Runtime/Admin'
$errorIds    = @(208, 216)

function Write-Info { param([string]$m) Write-Host $m }
function Write-Ok   { param([string]$m) Write-Host $m -ForegroundColor Green }
function Write-Warn { param([string]$m) Write-Host $m -ForegroundColor Yellow }
function Write-Err  { param([string]$m) Write-Host $m -ForegroundColor Red }
function Write-Head { param([string]$m) Write-Host ""; Write-Host "===== $m =====" -ForegroundColor Cyan; Write-Host "" }

function Show-AppErrorLog {
    Write-Head "截图工具最近错误日志 (AppModel-Runtime, Id 208/216)"
    $errs = Get-WinEvent -LogName $runtimeLog -MaxEvents 200 -ErrorAction SilentlyContinue |
        Where-Object { $_.Id -in $errorIds -and $_.Message -match [regex]::Escape($PackageName) } |
        Select-Object -First 10
    if (-not $errs) {
        Write-Ok "未发现 $PackageName 相关的 208/216 错误事件"
        return
    }
    foreach ($e in $errs) {
        $msg = $e.Message -replace "`r|`n", ' '
        if ($msg.Length -gt 160) { $msg = $msg.Substring(0, 160) + '...' }
        Write-Err "[$($e.TimeCreated)] (Id $($e.Id)) $msg"
    }
}

Write-Head "Windows 截图工具修复工具"

if ($ShowErrorLog) {
    Show-AppErrorLog
    exit 0
}

Write-Info "[1/3] 检查应用包 $PackageName ..."
$pkg = Get-AppxPackage -Name $PackageName -ErrorAction SilentlyContinue
if (-not $pkg) {
    Write-Err "未找到应用包 $PackageName，可能已被卸载。请先在 Microsoft Store 重新安装截图工具。"
    exit 1
}
Write-Ok "已找到: $($pkg.PackageFullName) (Status: $($pkg.Status))"

Write-Info "检查是否有正在运行的截图工具进程..."
$installPrefix = $pkg.InstallLocation.TrimEnd('\')
$running = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
    Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($installPrefix, [System.StringComparison]::OrdinalIgnoreCase) }
if ($running) {
    Write-Warn "检测到 $(@($running).Count) 个截图工具进程在运行，将先关闭以便重新注册（不影响已保存的截图）。"
    foreach ($rp in $running) {
        Write-Warn "  关闭进程: $($rp.Name) (PID $($rp.ProcessId))"
        Stop-Process -Id $rp.ProcessId -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 1
}
else {
    Write-Ok "无运行中的截图工具进程"
}

Write-Info "[2/3] 重新注册应用包（修复损坏的运行时注册）..."
try {
    Add-AppxPackage -DisableDevelopmentMode -Register "$($pkg.InstallLocation)\AppXManifest.xml" -ErrorAction Stop
    Write-Ok "重新注册成功"
}
catch {
    Write-Err "重新注册失败: $($_.Exception.Message)"
    exit 1
}

Write-Info "[3/3] 验证修复结果..."
$before = (Get-Date).AddMinutes(-1)
if (-not $NoLaunch) {
    Start-Process -FilePath "explorer.exe" -ArgumentList "ms-screenclip:" -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 4
    Write-Info "已触发启动，等待 4 秒检查是否产生新错误..."
}

$newErrs = Get-WinEvent -LogName $runtimeLog -MaxEvents 200 -ErrorAction SilentlyContinue |
    Where-Object { $_.TimeCreated -gt $before -and $_.Id -in $errorIds -and $_.Message -match [regex]::Escape($PackageName) }
if ($newErrs) {
    Write-Warn "修复后仍检测到错误事件，请按 Win+Shift+S 手动测试："
    Show-AppErrorLog
    exit 1
}

Write-Head "修复完成"
Write-Ok "截图工具已重新注册，且启动后未产生新的 208/216 错误。"
Write-Info "请按 Win+Shift+S 或从开始菜单打开截图工具确认可用。"
