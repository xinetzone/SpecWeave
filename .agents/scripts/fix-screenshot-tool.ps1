#Requires -Version 5.1
# PWSH7-EXEMPT: Windows system maintenance script, intentionally compatible with Windows PowerShell 5.1

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

# Cooldown lock: prevent event-storm from triggering concurrent fixes
$LockFile    = Join-Path $env:TEMP 'screenshot-fix.lock'
$LockSeconds = 300

#region Output helpers
function Write-Info {
    param([string]$m)
    Write-Host $m
}
function Write-Ok {
    param([string]$m)
    Write-Host $m -ForegroundColor Green
}
function Write-Warn {
    param([string]$m)
    Write-Host $m -ForegroundColor Yellow
}
function Write-Err {
    param([string]$m)
    Write-Host $m -ForegroundColor Red
}
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
                Write-Warn ("[Cooldown] Last fix was {0}s ago (<{1}s), skipping to avoid event storm." -f [int]$age.TotalSeconds, $LockSeconds)
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
    Write-Head "Recent AppModel-Runtime 208/216 errors for $PackageName"
    $errs = Get-WinEvent -LogName $runtimeLog -MaxEvents 200 -ErrorAction SilentlyContinue |
        Where-Object { $_.Id -in $errorIds -and $_.Message -match [regex]::Escape($PackageName) } |
        Select-Object -First 10
    if (-not $errs) {
        Write-Ok "No 208/216 errors found for $PackageName."
        return
    }
    foreach ($e in $errs) {
        $msg = $e.Message -replace "`r|`n", ' '
        if ($msg.Length -gt 160) { $msg = $msg.Substring(0, 160) + '...' }
        Write-Err ("[{0}] (Id {1}) {2}" -f $e.TimeCreated, $e.Id, $msg)
    }
}

function Get-AppRuntimeErrors {
    param([datetime]$Since = [datetime]::MinValue)
    Get-WinEvent -LogName $runtimeLog -MaxEvents 500 -ErrorAction SilentlyContinue |
        Where-Object { $_.TimeCreated -gt $Since -and $_.Id -in $errorIds -and $_.Message -match [regex]::Escape($PackageName) }
}

function Repair-PackageRuntime {
    param([bool]$Launch = $true)

    if (-not (Test-CoolDown)) { return $true }
    Acquire-CoolDown

    $pkg = Get-AppxPackage -Name $PackageName -ErrorAction SilentlyContinue
    if (-not $pkg) {
        Write-Err "Package $PackageName not found. Reinstall Snipping Tool from Microsoft Store."
        return $false
    }
    Write-Ok ("Found: {0} (Status: {1})" -f $pkg.PackageFullName, $pkg.Status)

    Write-Info "Checking for running Screenshot Tool processes..."
    $installPrefix = $pkg.InstallLocation.TrimEnd('\')
    $running = Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.ExecutablePath -and $_.ExecutablePath.StartsWith($installPrefix, [System.StringComparison]::OrdinalIgnoreCase) }
    if ($running) {
        Write-Warn ("Detected {0} running Screenshot Tool process(es), closing before re-registration..." -f @($running).Count)
        foreach ($rp in $running) {
            Write-Warn ("  Killing: {0} (PID {1})" -f $rp.Name, $rp.ProcessId)
            Stop-Process -Id $rp.ProcessId -Force -ErrorAction SilentlyContinue
        }
        Start-Sleep -Seconds 1
    }
    else {
        Write-Ok "No running Screenshot Tool processes."
    }

    Write-Info "Re-registering Appx package..."
    try {
        $manifest = Join-Path $pkg.InstallLocation 'AppXManifest.xml'
        Add-AppxPackage -DisableDevelopmentMode -Register $manifest -ErrorAction Stop
        Write-Ok "Re-registration succeeded."
    }
    catch {
        Write-Err ("Re-registration failed: {0}" -f $_.Exception.Message)
        return $false
    }

    Write-Info "Verifying fix..."
    $before = (Get-Date).AddMinutes(-1)
    if ($Launch) {
        Start-Process -FilePath "explorer.exe" -ArgumentList "ms-screenclip:" -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 4
        Write-Info "Triggered launch, waiting 4s for new errors..."
    }

    $newErrs = Get-AppRuntimeErrors -Since $before
    if ($newErrs) {
        Write-Warn "Errors detected after repair:"
        Show-AppErrorLog
        return $false
    }
    return $true
}

function Install-EventWatcher {
    param([string]$TaskName = 'FixScreenshotToolEventWatcher')

    # Admin check
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    $isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Err "Administrator privileges required to register the event-driven watcher."
        Write-Err "Please run PowerShell as Administrator and execute:"
        Write-Err ('  powershell -NoProfile -ExecutionPolicy Bypass -File "{0}" -InstallEventWatcher' -f $PSCommandPath)
        return $false
    }

    $scriptFullPath = $PSCommandPath
    if (-not $scriptFullPath) {
        try {
            $scriptFullPath = (Resolve-Path $MyInvocation.InvocationName -ErrorAction Stop).Path
        } catch {
            Write-Err "Could not resolve script path."
            return $false
        }
    }
    if (-not (Test-Path $scriptFullPath)) {
        Write-Err "Script path not found."
        return $false
    }

    $tr      = 'powershell.exe -NoProfile -ExecutionPolicy Bypass -File "' + $scriptFullPath + '"'
    $channel = 'Microsoft-Windows-AppModel-Runtime/Admin'
    $xpath   = '*[System[(EventID=208 or EventID=216)]]'

    Write-Head ("Registering event-driven watcher: " + $TaskName)
    Write-Info ("Script : " + $scriptFullPath)
    Write-Info ("Channel: " + $channel)
    Write-Info ("XPath  : " + $xpath)
    Write-Info ("Action : " + $tr)
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
    Write-Info ("Running: schtasks " + ($schtaskArgs -join ' '))
    & schtasks @schtaskArgs
    $rc = $LASTEXITCODE

    if ($rc -ne 0) {
        Write-Err ("schtasks registration failed (exit code " + $rc + ").")
        return $false
    }

    Write-Ok ""
    Write-Ok ("Event-driven watcher registered: " + $TaskName)
    Write-Ok "Trigger : AppModel-Runtime events 208/216 fire instant self-heal"
    Write-Ok "Resident: NO process kept alive (event-driven, crash-proof)"
    Write-Ok "Cooldown: 5 minutes between fixes to prevent event storms"
    Write-Info ""
    Write-Info "Management commands:"
    Write-Info ("  Query : schtasks /Query /TN " + $TaskName + " /V /FO LIST")
    Write-Info ("  Run   : schtasks /Run   /TN " + $TaskName)
    Write-Info ("  Delete: schtasks /Delete /TN " + $TaskName + " /F")
    Write-Info ""
    Write-Info "You may also remove the legacy polling task (if present):"
    Write-Info "  schtasks /Delete /TN FixScreenshotToolWatch /F"
    return $true
}

Write-Head "Windows Screenshot Tool Fix Utility"

if ($InstallEventWatcher) {
    $ok = Install-EventWatcher
    if ($ok) {
        Write-Ok "Event-driven watcher is ready."
        exit 0
    }
    else {
        Write-Err "Event-driven watcher registration failed."
        exit 1
    }
}

if ($ShowErrorLog) {
    Show-AppErrorLog
    exit 0
}

if ($Watch) {
    Write-Head ("Watch mode: checking every {0}s for 208/216 errors" -f $WatchIntervalSeconds)
    Write-Info "Press Ctrl+C to stop."
    while ($true) {
        $since = (Get-Date).AddSeconds(-$WatchIntervalSeconds)
        $errs  = Get-AppRuntimeErrors -Since $since
        $ts    = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
        if ($errs) {
            Write-Warn ("[{0}] Detected {1} runtime error(s), running auto-repair..." -f $ts, @($errs).Count)
            $ok = Repair-PackageRuntime -Launch (-not $NoLaunch)
            if ($ok) {
                Write-Ok ("[{0}] Self-heal succeeded." -f $ts)
            }
            else {
                Write-Err ("[{0}] Self-heal failed." -f $ts)
            }
        }
        else {
            Write-Info ("[{0}] No errors detected." -f $ts)
        }
        Start-Sleep -Seconds $WatchIntervalSeconds
    }
    exit 0
}

# Single-fix mode
$ok = Repair-PackageRuntime -Launch (-not $NoLaunch)
if ($ok) {
    Write-Head "Repair Complete"
    Write-Ok "Screenshot Tool re-registered successfully; no new 208/216 errors after launch."
    Write-Info "Press Win+Shift+S or launch Snipping Tool from Start Menu to confirm."
    exit 0
}
else {
    Write-Err "Repair did not fully succeed. See messages above."
    exit 1
}
