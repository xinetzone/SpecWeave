#Requires -Version 5.1
# PWSH7-EXEMPT: Windows 系统维护脚本，有意兼容 Windows PowerShell 5.1，无需 pwsh7

<#
.SYNOPSIS
    Fix Windows Screenshot Tool (ScreenSketch / Snipping Tool) startup errors.
.DESCRIPTION
    Single-fix mode (default): Re-register ScreenSketch package and verify.
    Event-watcher mode (-InstallEventWatcher): Register a scheduled task that
    auto-fires on AppModel-Runtime 208/216 events (root-cause fix for recurring
    breakage caused by system cleanup tools corrupting UWP runtime registration).
    Watch mode (-Watch): Legacy polling loop (kept for compatibility).
.PARAMETER PackageName
    Appx package name, default "Microsoft.ScreenSketch".
.PARAMETER NoLaunch
    Skip launch verification after re-registration.
.PARAMETER ShowErrorLog
    Show recent AppModel-Runtime 208/216 errors for the package and exit.
.PARAMETER Watch
    Legacy polling watch-dog mode (runs in a loop).
.PARAMETER WatchIntervalSeconds
    Polling interval in seconds for -Watch mode, default 60.
.PARAMETER InstallEventWatcher
    Register an event-driven scheduled task (SYSTEM, ONEVENT trigger) that fires
    automatically on AppModel-Runtime 208/216 events. Requires admin. This is the
    preferred root-cause fix over -Watch (which depends on a resident process).
.EXAMPLE
    .\fix-screenshot-tool.ps1
    Single fix: re-register and verify.
.EXAMPLE
    .\fix-screenshot-tool.ps1 -InstallEventWatcher
    Register event-driven auto-heal (admin required).
.NOTES
    2026-08-10 Initial version.
    2026-08-15 Added -Watch polling mode.
    2026-08-25 Added -InstallEventWatcher (event-driven, no resident process).
#>

param(
    [string]$PackageName = 'Microsoft.ScreenSketch',
    [switch]$NoLaunch,
    [switch]$ShowErrorLog,
    [switch]$Watch,
    [int]$WatchIntervalSeconds = 60,
    [switch]$InstallEventWatcher
)

$ErrorActionPreference = 'Continue'

try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$runtimeLog = 'Microsoft-Windows-AppModel-Runtime/Admin'
$errorIds   = @(208, 216)

$script:lastFixTime = [datetime]::MinValue
$script:consecutiveFailures = 0
$script:nextRetryAfter = [datetime]::MinValue

# Cooldown lock: prevent event-storm from triggering concurrent fixes
$LockFile    = Join-Path $env:TEMP 'screenshot-fix.lock'
$LockSeconds = 300

#region Output helpers
function Write-Info { param([string]$m) Write-Host $m }
function Write-Ok   { param([string]$m) Write-Host $m -ForegroundColor Green }
function Write-Warn { param([string]$m) Write-Host $m -ForegroundColor Yellow }
function Write-Err  { param([string]$m) Write-Host $m -ForegroundColor Red }
function Write-Head {
    param([string]$m)
    Write-Host ""
    Write-Host "===== $m =====" -ForegroundColor Cyan
    Write-Host ""
}
#endregion

#region Cooldown lock (prevents event-storm)
function Test-CoolDown {
    if (Test-Path $LockFile) {
        try {
            $ts  = (Get-Item $LockFile).LastWriteTime
            $age = (Get-Date) - $ts
            if ($age.TotalSeconds -lt $LockSeconds) {
                Write-Warn ("[冷却] 距上次修复仅 {0}s（<{1}s），跳过以避免事件风暴。" -f [int]$age.TotalSeconds, $LockSeconds)
                return $false
            }
        } catch {}
    }
    return $true
}
function Acquire-CoolDown {
    try {
        Set-Content -Path $LockFile -Value ((Get-Date).ToString('s')) -Encoding ASCII -Force -ErrorAction SilentlyContinue
    } catch {}
}
#endregion

function Show-AppErrorLog {
    Write-Head "截图工具最近错误日志 (AppModel-Runtime, Id 208/216)"
    $events = Get-WinEventInternal -MaxEvents 200
    if ($null -eq $events) {
        Write-Warn "无法读取事件日志 $runtimeLog（可能需要管理员权限或日志通道未启用）"
        return
    }
    $errs = $events |
        Where-Object { $_.Id -in $errorIds -and $_.Message -match [regex]::Escape($PackageName) } |
        Select-Object -First 10
    if (-not $errs) {
        Write-Ok "未发现 $PackageName 的 208/216 错误。"
        return
    }
    foreach ($e in $errs) {
        $msg = $e.Message -replace "`r|`n", ' '
        if ($msg.Length -gt 160) { $msg = $msg.Substring(0, 160) + '...' }
        Write-Err ("[{0}] (Id {1}) {2}" -f $e.TimeCreated, $e.Id, $msg)
    }
}

function Get-WinEventInternal {
    param([int]$MaxEvents = 500)
    try {
        $events = Get-WinEvent -FilterHashtable @{ LogName = $runtimeLog; Id = $errorIds } -MaxEvents $MaxEvents -ErrorAction Stop
        if ($null -eq $events) { return @() }
        return $events
    }
    catch [System.Eventing.Reader.EventLogNotFoundException] {
        return $null
    }
    catch {
        if ($_.Exception.Message -match 'No events were found|找不到|没有匹配') {
            return @()
        }
        try {
            $events = Get-WinEvent -LogName $runtimeLog -MaxEvents $MaxEvents -ErrorAction Stop |
                Where-Object { $_.Id -in $errorIds }
            if ($null -eq $events) { return @() }
            return $events
        }
        catch {
            return $null
        }
    }
}

function Get-AppRuntimeErrors {
    param([datetime]$Since = [datetime]::MinValue)
    $events = Get-WinEventInternal -MaxEvents 500
    if ($null -eq $events) { return @() }
    return @($events | Where-Object {
        $_.TimeCreated -gt $Since -and
        $_.TimeCreated -gt $script:lastFixTime -and
        $_.Message -match [regex]::Escape($PackageName)
    })
}

function Repair-PackageRuntime {
    param([bool]$Launch = $true)

    if (-not (Test-CoolDown)) { return $true }
    Acquire-CoolDown

    $pkg = Get-AppxPackage -Name $PackageName -ErrorAction SilentlyContinue
    if (-not $pkg) {
        Write-Err "未找到包 $PackageName，请从 Microsoft Store 重新安装截图工具。"
        return $false
    }
    Write-Ok ("找到: {0} (状态: {1})" -f $pkg.PackageFullName, $pkg.Status)

    Write-Info "检查是否有正在运行的截图工具进程..."
    $installPrefix = $pkg.InstallLocation.TrimEnd('\') + '\'
    $running = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($installPrefix, [System.StringComparison]::OrdinalIgnoreCase) }
    if ($running) {
        Write-Warn ("检测到 {0} 个正在运行的截图工具进程，重新注册前先关闭..." -f @($running).Count)
        foreach ($rp in $running) {
            Write-Warn ("  终止: {0} (PID {1})" -f $rp.Name, $rp.ProcessId)
            Stop-Process -Id $rp.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
    }
    else {
        Write-Ok "没有正在运行的截图工具进程。"
    }

    Write-Info "正在重新注册 Appx 包..."
    try {
        $manifest = Join-Path $pkg.InstallLocation 'AppXManifest.xml'
        Add-AppxPackage -DisableDevelopmentMode -Register $manifest -ErrorAction Stop
        Write-Ok "重新注册成功。"
    }
    catch {
        Write-Err ("重新注册失败: {0}" -f $_.Exception.Message)
        return $false
    }

    Write-Info "验证修复结果..."
    $beforeLaunch = Get-Date
    if ($Launch) {
        Start-Process -FilePath "explorer.exe" -ArgumentList "ms-screenclip:" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 4
        Write-Info "已触发启动，等待 4s 观察新错误..."
    }

    $newErrs = Get-AppRuntimeErrors -Since $beforeLaunch
    if ($newErrs) {
        Write-Warn "修复后检测到错误："
        Show-AppErrorLog
        return $false
    }
    $script:lastFixTime = Get-Date
    return $true
}

function Install-EventWatcher {
    param([string]$TaskName = 'FixScreenshotToolEventWatcher')

    # Admin check
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Err "注册事件驱动监视器需要管理员权限。"
        Write-Err "请以管理员身份运行 PowerShell 并执行："
        Write-Err ('  powershell -NoProfile -ExecutionPolicy Bypass -File "{0}" -InstallEventWatcher' -f $PSCommandPath)
        return $false
    }

    $scriptFullPath = $PSCommandPath
    if (-not $scriptFullPath) {
        try {
            $scriptFullPath = (Resolve-Path $MyInvocation.InvocationName -ErrorAction Stop).Path
        } catch {
            Write-Err "无法解析脚本路径。"
            return $false
        }
    }
    if (-not (Test-Path $scriptFullPath)) {
        Write-Err "脚本路径不存在。"
        return $false
    }

    $tr      = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $scriptFullPath + '"'
    $channel = 'Microsoft-Windows-AppModel-Runtime/Admin'
    $xpath   = '*[System[(EventID=208 or EventID=216)]]'

    Write-Head ("注册事件驱动监视器: " + $TaskName)
    Write-Info ("脚本  : " + $scriptFullPath)
    Write-Info ("通道  : " + $channel)
    Write-Info ("XPath : " + $xpath)
    Write-Info ("动作  : " + $tr)
    Write-Info ""

    # Remove old task if exists
    schtasks /Delete /TN $TaskName /F 2>&1 | Out-Null

    # Create event-triggered task via schtasks (avoids PS CIM version-compat issues)
    $schtaskArgs = @(
        '/Create', '/TN', $TaskName,
        '/TR', $tr,
        '/SC', 'ONEVENT',
        '/EC', $channel,
        '/MO', $xpath,
        '/RL', 'HIGHEST',
        '/RU', 'SYSTEM',
        '/F'
    )
    Write-Info ("运行: schtasks " + ($schtaskArgs -join ' '))
    & schtasks @schtaskArgs
    $rc = $LASTEXITCODE

    if ($rc -ne 0) {
        Write-Err ("schtasks 注册失败（退出码 " + $rc + "）。")
        return $false
    }

    Write-Ok ""
    Write-Ok ("事件驱动监视器已注册: " + $TaskName)
    Write-Ok "触发器: AppModel-Runtime 208/216 事件即时自愈"
    Write-Ok "驻留  : 无需常驻进程（事件驱动，抗崩溃）"
    Write-Ok "冷却  : 修复间隔 5 分钟，防止事件风暴"
    Write-Info ""
    Write-Info "管理命令："
    Write-Info ("  查询: schtasks /Query /TN " + $TaskName + " /V /FO LIST")
    Write-Info ("  运行: schtasks /Run   /TN " + $TaskName)
    Write-Info ("  删除: schtasks /Delete /TN " + $TaskName + " /F")
    Write-Info ""
    Write-Info "也可以删除旧的轮询任务（如果存在）："
    Write-Info "  schtasks /Delete /TN FixScreenshotToolWatch /F"
    return $true
}

Write-Head "Windows 截图工具修复工具"

if ($InstallEventWatcher) {
    $ok = Install-EventWatcher
    if ($ok) {
        Write-Ok "事件驱动监视器已就绪。"
        exit 0
    }
    else {
        Write-Err "事件驱动监视器注册失败。"
        exit 1
    }
}

if ($ShowErrorLog) {
    Show-AppErrorLog
    exit 0
}

if ($Watch) {
    Write-Head ("监视模式：每 {0}s 检查一次 208/216 错误" -f $WatchIntervalSeconds)
    Write-Info "按 Ctrl+C 停止。"
    while ($true) {
        $now = Get-Date
        $since = $now.AddSeconds(-$WatchIntervalSeconds)
        $ts = $now.ToString('yyyy-MM-dd HH:mm:ss')
        $errs = Get-AppRuntimeErrors -Since $since
        if ($errs) {
            if ($now -lt $script:nextRetryAfter) {
                $waitSec = [int]($script:nextRetryAfter - $now).TotalSeconds
                Write-Warn "[$ts] 连续失败 $script:consecutiveFailures 次，退避中，${waitSec}s 后重试..."
                Start-Sleep -Seconds ([Math]::Min($waitSec, $WatchIntervalSeconds))
                continue
            }
            Write-Warn "[$ts] 检测到 $PackageName 运行时错误 $(@($errs).Count) 条，执行自动修复..."
            $ok = Repair-PackageRuntime -Launch (-not $NoLaunch)
            if ($ok) {
                Write-Ok "[$ts] 自愈成功，截图工具已恢复。"
                $script:consecutiveFailures = 0
                $script:nextRetryAfter = [datetime]::MinValue
            }
            else {
                $script:consecutiveFailures++
                $backoff = [Math]::Min($WatchIntervalSeconds * [Math]::Pow(2, $script:consecutiveFailures - 1), 3600)
                $script:nextRetryAfter = (Get-Date).AddSeconds($backoff)
                Write-Err "[$ts] 自愈失败（连续 $script:consecutiveFailures 次），${backoff}s 后重试。建议手动重装截图工具。"
            }
        }
        else {
            if ($script:consecutiveFailures -gt 0) {
                Write-Ok "[$ts] 恢复正常，重置失败计数。"
                $script:consecutiveFailures = 0
                $script:nextRetryAfter = [datetime]::MinValue
            }
            Write-Info "[$ts] 未检测到错误，继续监视..."
        }
        Start-Sleep -Seconds $WatchIntervalSeconds
    }
    exit 0
}

# Single-fix mode
$ok = Repair-PackageRuntime -Launch (-not $NoLaunch)
if ($ok) {
    Write-Head "修复完成"
    Write-Ok "截图工具已成功重新注册；启动后未发现新的 208/216 错误。"
    Write-Info "按 Win+Shift+S 或从开始菜单启动截图工具确认。"
    exit 0
}
else {
    Write-Err "修复未完全成功，请参阅上方消息。"
    exit 1
}
