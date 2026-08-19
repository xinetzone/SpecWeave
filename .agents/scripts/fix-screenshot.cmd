@echo off
chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

REM ============================================================
REM  Windows Screenshot Tool One-Click Fix
REM  Double-click to run - Auto UAC elevation - Pauses on completion
REM  Can be copied to desktop / any location
REM  Uses fix-screenshot-tool.ps1 if present in same directory,
REM  otherwise uses built-in minimal fix logic.
REM ============================================================

REM --- UAC auto-elevation ---
net session >nul 2>&1
if !errorLevel! neq 0 (
    echo [INFO] Requesting administrator privileges...
    powershell -NoProfile -Command "Start-Process -FilePath '%~f0' -Verb RunAs -WorkingDirectory '%~dp0'"
    exit /b
)

cd /d "%~dp0"

echo.
echo ========================================================
echo   Windows Screenshot Tool One-Click Fix
echo   Snipping Tool / ScreenSketch Repair
echo ========================================================
echo.

set "PS_SCRIPT=%~dp0fix-screenshot-tool.ps1"
set "RC=0"

if exist "!PS_SCRIPT!" (
    echo [INFO] Using full-featured repair script...
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -File "!PS_SCRIPT!"
    set "RC=!errorLevel!"
) else (
    echo [INFO] Using built-in repair logic...
    echo.
    powershell -NoProfile -ExecutionPolicy Bypass -Command "$pkg=Get-AppxPackage -Name 'Microsoft.ScreenSketch' -ErrorAction SilentlyContinue; if(-not $pkg){$pkg=Get-AppxPackage -Name 'Microsoft.SnippingTool' -ErrorAction SilentlyContinue}; if(-not $pkg){Write-Host '[FAIL] Package not found. Reinstall from Microsoft Store.' -ForegroundColor Red; exit 1}; $m=Join-Path $pkg.InstallLocation 'AppXManifest.xml'; if(-not(Test-Path $m)){Write-Host '[FAIL] Manifest missing. Reinstall from Microsoft Store.' -ForegroundColor Red; exit 1}; Write-Host '[STEP] Closing running instances...' -ForegroundColor Cyan; $pfx=$pkg.InstallLocation.TrimEnd('\'); $procs=Get-CimInstance Win32_Process -ErrorAction SilentlyContinue | Where-Object {$_.ExecutablePath -and $_.ExecutablePath.StartsWith($pfx,[System.StringComparison]::OrdinalIgnoreCase)}; if($procs){$procs | ForEach-Object {Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue}; Start-Sleep 1; Write-Host '[OK] Processes closed.' -ForegroundColor Green} else {Write-Host '[OK] No running instances.' -ForegroundColor Green}; Write-Host '[STEP] Re-registering package...' -ForegroundColor Cyan; try {Add-AppxPackage -DisableDevelopmentMode -Register $m -ErrorAction Stop; Write-Host '[OK] Re-registration succeeded.' -ForegroundColor Green} catch {Write-Host ('[FAIL] '+$_.Exception.Message) -ForegroundColor Red; exit 1}; Write-Host '[STEP] Verifying...' -ForegroundColor Cyan; $t0=(Get-Date).AddMinutes(-1); Start-Process -FilePath 'explorer.exe' -ArgumentList 'ms-screenclip:' -ErrorAction SilentlyContinue; Start-Sleep 5; $errs=Get-WinEvent -LogName 'Microsoft-Windows-AppModel-Runtime/Admin' -MaxEvents 50 -ErrorAction SilentlyContinue | Where-Object {$_.TimeCreated -gt $t0 -and $_.Id -in @(208,216) -and $_.Message -match 'ScreenSketch|SnippingTool'}; if($errs){Write-Host '[WARN] Errors detected after fix.' -ForegroundColor Yellow; exit 1} else {Write-Host '[OK] Verified - no errors!' -ForegroundColor Green}; exit 0"
    set "RC=!errorLevel!"
)

echo.
echo ========================================================
if "!RC!" equ "0" (
    echo   [SUCCESS] Repair completed!
    echo   Press Win+Shift+S to test screenshot.
) else (
    echo   [FAILED] Repair did not fully succeed.
    echo   Please reinstall Snipping Tool from Microsoft Store.
)
echo ========================================================
echo.
pause
endlocal
exit /b !RC!
