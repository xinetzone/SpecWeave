#Requires -Version 5.1
# PWSH7-EXEMPT: Windows 系统维护脚本，有意兼容 Windows PowerShell 5.1，无需 pwsh7

<#
.SYNOPSIS
    修复 Windows 截图工具（ScreenSketch / Snipping Tool）启动报错。
.DESCRIPTION
    单次修复模式（默认）：重新注册 ScreenSketch 应用包并验证修复结果。
    守护模式（-Watch）：循环监视 AppModel-Runtime 事件日志中的 208/216 错误，
    一旦检测到 ScreenSketch 相关错误自动执行重注册（自愈），无需人工干预。

    故障背景：截图工具反复出现 AppModel-Runtime 事件 ID 208/216，错误码 0x80070002
    （配置 AppX 运行时进程失败）。主要破坏源为第三方系统清理/优化软件
    （如 Windows优化大师）清理 UWP 包缓存导致运行时注册损坏。
    本脚本既提供手动修复，也提供守护自愈，作为复发兜底。

.PARAMETER PackageName
    要修复的应用包名称，默认 "Microsoft.ScreenSketch"。
.PARAMETER NoLaunch
    重注册后不触发启动验证（仅重注册并检查事件日志）。
.PARAMETER ShowErrorLog
    仅展示最近截图工具相关的 AppModel-Runtime 错误事件后退出，不执行修复。
.PARAMETER Watch
    以守护模式运行：按 WatchIntervalSeconds 间隔循环检查 208/216 错误，
    检测到即自动重注册，循环往复直至手动停止（Ctrl+C）。
.PARAMETER WatchIntervalSeconds
    守护模式检查间隔秒数，默认 60。
.EXAMPLE
    .\fix-screenshot-tool.ps1
    单次修复：重新注册截图工具并验证启动。
.EXAMPLE
    .\fix-screenshot-tool.ps1 -ShowErrorLog
    只查看当前截图工具相关的错误日志。
.EXAMPLE
    .\fix-screenshot-tool.ps1 -Watch -WatchIntervalSeconds 60
    守护模式：每 60 秒检查一次，发现 208/216 错误即自动修复。
.NOTES
    依据 2026-08-10 项目 memory「故障排查与修复方案」沉淀，复发时可直接复用本脚本。
    2026-08-15 增强：新增 -Watch 守护自愈模式（应对清理软件反复破坏）。
    守护模式建议配合计划任务开机自启：
      schtasks /Create /TN "FixScreenshotToolWatch" /TR "powershell -NoProfile -ExecutionPolicy Bypass -File \"<本脚本绝对路径>\" -Watch" /SC ONLOGON /RL HIGHEST /F
#>

param(
    [string]$PackageName = 'Microsoft.ScreenSketch',
    [switch]$NoLaunch,
    [switch]$ShowErrorLog,
    [switch]$Watch,
    [int]$WatchIntervalSeconds = 60
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

# 获取指定时间点之后、与目标包相关的 208/216 错误
function Get-AppRuntimeErrors {
    param([datetime]$Since = [datetime]::MinValue)
    Get-WinEvent -LogName $runtimeLog -MaxEvents 500 -ErrorAction SilentlyContinue |
        Where-Object { $_.TimeCreated -gt $Since -and $_.Id -in $errorIds -and $_.Message -match [regex]::Escape($PackageName) }
}

# 执行一次完整修复：关进程 -> 重注册 -> 验证。成功返回 $true。
function Repair-PackageRuntime {
    param([bool]$Launch = $true)

    $pkg = Get-AppxPackage -Name $PackageName -ErrorAction SilentlyContinue
    if (-not $pkg) {
        Write-Err "未找到应用包 $PackageName，可能已被卸载。请先在 Microsoft Store 重新安装截图工具。"
        return $false
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

    Write-Info "重新注册应用包（修复损坏的运行时注册）..."
    try {
        Add-AppxPackage -DisableDevelopmentMode -Register "$($pkg.InstallLocation)\AppXManifest.xml" -ErrorAction Stop
        Write-Ok "重新注册成功"
    }
    catch {
        Write-Err "重新注册失败: $($_.Exception.Message)"
        return $false
    }

    Write-Info "验证修复结果..."
    $before = (Get-Date).AddMinutes(-1)
    if ($Launch) {
        Start-Process -FilePath "explorer.exe" -ArgumentList "ms-screenclip:" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 4
        Write-Info "已触发启动，等待 4 秒检查是否产生新错误..."
    }

    $newErrs = Get-AppRuntimeErrors -Since $before
    if ($newErrs) {
        Write-Warn "修复后仍检测到错误事件："
        Show-AppErrorLog
        return $false
    }
    return $true
}

Write-Head "Windows 截图工具修复工具"

if ($ShowErrorLog) {
    Show-AppErrorLog
    exit 0
}

if ($Watch) {
    Write-Head "守护模式启动：每 $WatchIntervalSeconds 秒检查 208/216 错误，检测到即自动修复"
    Write-Info "按 Ctrl+C 停止。"
    while ($true) {
        $since = (Get-Date).AddSeconds(-$WatchIntervalSeconds)
        $errs = Get-AppRuntimeErrors -Since $since
        $ts = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        if ($errs) {
            Write-Warn "[$ts] 检测到 $PackageName 运行时错误 $(@($errs).Count) 条，执行自动修复..."
            $ok = Repair-PackageRuntime -Launch (-not $NoLaunch)
            if ($ok) {
                Write-Ok "[$ts] 自愈成功，截图工具已恢复。"
            }
            else {
                Write-Err "[$ts] 自愈失败，请手动运行本脚本排查（建议先重装截图工具）。"
            }
        }
        else {
            Write-Info "[$ts] 未检测到错误，继续监视..."
        }
        Start-Sleep -Seconds $WatchIntervalSeconds
    }
    exit 0
}

# 单次修复模式
$ok = Repair-PackageRuntime -Launch (-not $NoLaunch)
if ($ok) {
    Write-Head "修复完成"
    Write-Ok "截图工具已重新注册，且启动后未产生新的 208/216 错误。"
    Write-Info "请按 Win+Shift+S 或从开始菜单打开截图工具确认可用。"
    exit 0
}
else {
    Write-Err "修复未完全成功，请按上述提示处理。"
    exit 1
}
