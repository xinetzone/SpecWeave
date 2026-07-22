#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Compress WSL2 virtual disk (ext4.vhdx) to reclaim unused space
.DESCRIPTION
    This script will:
    1. Run fstrim inside WSL to mark unused blocks
    2. Shutdown WSL completely
    3. Compact the VHDX file using Hyper-V module or diskpart (fallback)
    Must be run as Administrator.
.PARAMETER VhdxPath
    Path to ext4.vhdx file. Default: D:\WSL\Ubuntu\ext4.vhdx
.PARAMETER DistroName
    WSL distribution name. Default: Ubuntu-24.04
.PARAMETER SkipFstrim
    Skip the fstrim step (if WSL won't boot)
.EXAMPLE
    .\compress-wsl-vhdx.ps1
    Compress with default settings
.EXAMPLE
    .\compress-wsl-vhdx.ps1 -VhdxPath "D:\WSL\Ubuntu\ext4.vhdx" -DistroName "Ubuntu-24.04"
.NOTES
    Author: SpecWeave
    Requires: Administrator PowerShell, WSL2
#>

param(
    [string]$VhdxPath = "D:\WSL\Ubuntu\ext4.vhdx",
    [string]$DistroName = "Ubuntu-24.04",
    [switch]$SkipFstrim
)

$ErrorActionPreference = 'Stop'

function Format-Size {
    param([long]$Bytes)
    if ($Bytes -ge 1GB) { return "$([math]::Round($Bytes/1GB,2)) GB" }
    if ($Bytes -ge 1MB) { return "$([math]::Round($Bytes/1MB,2)) MB" }
    return "$Bytes B"
}

function Test-Admin {
    $current = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($current)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  WSL VHDX Compression Tool" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if (-not (Test-Admin)) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host "Please right-click PowerShell and select 'Run as Administrator', then re-run this script." -ForegroundColor Yellow
    exit 1
}

if (-not (Test-Path $VhdxPath)) {
    Write-Host "ERROR: VHDX file not found: $VhdxPath" -ForegroundColor Red
    Write-Host "Use -VhdxPath to specify the correct path." -ForegroundColor Yellow
    exit 1
}

$beforeSize = (Get-Item $VhdxPath).Length
Write-Host "[Info] Target VHDX: $VhdxPath" -ForegroundColor White
Write-Host "[Info] Current size: $(Format-Size $beforeSize)" -ForegroundColor White
Write-Host ""

if (-not $SkipFstrim) {
    Write-Host "[Step 1/4] Running fstrim inside WSL to mark free blocks..." -ForegroundColor Yellow
    
    try {
        wsl -d $DistroName -- fstrim -av 2>&1 | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
        Write-Host "  fstrim completed" -ForegroundColor Green
    }
    catch {
        Write-Host "  WARNING: fstrim failed, continuing anyway..." -ForegroundColor Yellow
        Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor DarkYellow
    }
    Write-Host ""
}
else {
    Write-Host "[Step 1/4] Skipping fstrim (per -SkipFstrim)" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "[Step 2/4] Shutting down WSL..." -ForegroundColor Yellow
try {
    wsl --shutdown
    Start-Sleep -Seconds 3
    Write-Host "  WSL shut down successfully" -ForegroundColor Green
}
catch {
    Write-Host "  WARNING: WSL shutdown had issues: $($_.Exception.Message)" -ForegroundColor Yellow
}
Write-Host ""

Write-Host "[Step 3/4] Compacting VHDX..." -ForegroundColor Yellow

$hypervAvailable = $false
try {
    Import-Module Hyper-V -ErrorAction Stop
    $hypervAvailable = $true
    Write-Host "  Using Hyper-V Optimize-VHD..." -ForegroundColor Gray
}
catch {
    Write-Host "  Hyper-V module not available, using diskpart fallback..." -ForegroundColor Gray
}

if ($hypervAvailable) {
    try {
        Write-Host "  Mounting VHDX in read-only mode..." -ForegroundColor Gray
        Mount-VHD -Path $VhdxPath -ReadOnly -ErrorAction Stop
        
        Write-Host "  Optimizing VHDX (this may take several minutes)..." -ForegroundColor Yellow
        Optimize-VHD -Path $VhdxPath -Mode Full -ErrorAction Stop
        
        Write-Host "  Dismounting VHDX..." -ForegroundColor Gray
        Dismount-VHD -Path $VhdxPath -ErrorAction Stop
        
        Write-Host "  VHDX optimization completed" -ForegroundColor Green
    }
    catch {
        Write-Host "  Hyper-V method failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "  Trying diskpart fallback..." -ForegroundColor Yellow
        
        try {
            Dismount-VHD -Path $VhdxPath -ErrorAction SilentlyContinue
        }
        catch {}
        
        $hypervAvailable = $false
    }
}

if (-not $hypervAvailable) {
    $diskpartScript = @"
select vdisk file="$VhdxPath"
attach vdisk readonly
compact vdisk
detach vdisk
exit
"@
    $scriptPath = Join-Path $env:TEMP "wsl-compact-diskpart.txt"
    $diskpartScript | Out-File -FilePath $scriptPath -Encoding ASCII -Force
    
    Write-Host "  Running diskpart (this may take several minutes)..." -ForegroundColor Yellow
    Write-Host "  Do NOT close this window while diskpart is working!" -ForegroundColor DarkYellow
    
    $diskpartOutput = & diskpart /s $scriptPath 2>&1
    $diskpartOutput | ForEach-Object { 
        if ($_ -match '%') { Write-Host "  $_" -ForegroundColor Gray }
    }
    
    Remove-Item $scriptPath -Force -ErrorAction SilentlyContinue
    Write-Host "  diskpart completed" -ForegroundColor Green
}

Write-Host ""

Write-Host "[Step 4/4] Calculating results..." -ForegroundColor Yellow
Start-Sleep -Seconds 2

$afterSize = (Get-Item $VhdxPath).Length
$savings = $beforeSize - $afterSize
$savingsPercent = if ($beforeSize -gt 0) { [math]::Round($savings / $beforeSize * 100, 1) } else { 0 }

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Compression Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Before:  $(Format-Size $beforeSize)" -ForegroundColor White
Write-Host "  After:   $(Format-Size $afterSize)" -ForegroundColor Green
Write-Host "  Saved:   $(Format-Size $savings) ($savingsPercent%)" -ForegroundColor $(if ($savings -gt 0) { 'Green' } else { 'Yellow' })
Write-Host ""

try {
    $drive = Get-PSDrive -Name D -ErrorAction SilentlyContinue
    if ($drive) {
        $freeGB = [math]::Round($drive.Free / 1GB, 2)
        Write-Host "  D: drive free space now: $freeGB GB" -ForegroundColor White
    }
}
catch {}

Write-Host ""
Write-Host "Tips:" -ForegroundColor Yellow
Write-Host "  1. You can now start WSL normally (wsl or open your Linux terminal)" -ForegroundColor Gray
Write-Host "  2. To prevent future bloat, run fstrim regularly inside WSL:" -ForegroundColor Gray
Write-Host "     sudo fstrim -av" -ForegroundColor DarkGray
Write-Host "  3. If compression didn't save much space, the VHDX was already compact" -ForegroundColor Gray
Write-Host ""
