#Requires -Version 5.1
<#
.SYNOPSIS
    One-click restore: Docker image cache to WSL2 distro
.DESCRIPTION
    After WSL reset, restores dev environment from .docker-cache image tar.gz.
    Idempotent: skips already-completed steps.
    Flow: Install Ubuntu -> Install Podman -> Load image -> Export rootfs -> Import WSL -> Configure user -> Verify
.NOTES
    Usage: powershell -ExecutionPolicy Bypass -File restore-wsl-from-cache.ps1
    Prerequisite: WSL2 enabled (wsl --version works)
    Part of docker-wsl-bridge-cmd skill tooling.
#>

[CmdletBinding()]
param(
    [string]$DistroName      = "devcontainer-base",
    [string]$WorkspaceDistro = "Ubuntu",
    [string]$CacheDir        = "",
    [string]$ImageFile       = "",
    [string]$InstallDir      = "",
    [string]$ProjectRoot     = "",
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Auto-detect project root (script is in .agents/scripts/, project root is 2 levels up)
if (-not $ProjectRoot) {
    $ProjectRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
}
# Normalize path
$ProjectRoot = (Resolve-Path $ProjectRoot -ErrorAction SilentlyContinue).Path
if (-not $ProjectRoot) {
    # Fallback: use working directory
    $ProjectRoot = (Get-Location).Path
}

# Defaults (auto-detected from project root)
if (-not $CacheDir)   { $CacheDir   = Join-Path $ProjectRoot ".docker-cache" }
if (-not $ImageFile)  { $ImageFile  = Join-Path $CacheDir "images\devcontainer-base_latest.tar.gz" }
if (-not $InstallDir) { $InstallDir = "D:\WSL\$DistroName" }
$rootfsLocal   = Join-Path $CacheDir "$DistroName-rootfs.tar.gz"

# Derive WSL mount path from Windows CacheDir
# e.g. D:\spaces\SpecWeave\.docker-cache -> /mnt/d/spaces/SpecWeave/.docker-cache
$drive = $CacheDir.Substring(0,1).ToLower()
$rest  = $CacheDir.Substring(2) -replace '\\','/'
$WslMountRoot = "/mnt/$drive$rest"
$wslImageTar  = "$WslMountRoot/images/devcontainer-base_latest.tar.gz"
$wslRootfsOut = "$WslMountRoot/$DistroName-rootfs.tar.gz"

# Helper functions
function Step($msg)     { Write-Host "`n[STEP] $msg" -ForegroundColor Cyan }
function Ok($msg)       { Write-Host "  [OK] $msg" -ForegroundColor Green }
function Skip($msg)     { Write-Host "  [SKIP] $msg" -ForegroundColor DarkGray }
function Warn($msg)     { Write-Host "  [WARN] $msg" -ForegroundColor Yellow }
function Fail($msg)     { Write-Host "  [FAIL] $msg" -ForegroundColor Red; exit 1 }

function WslBash($distro, $cmd) {
    $result = wsl -d $distro -u root -- bash -c $cmd 2>&1
    if ($LASTEXITCODE -ne 0) {
        Warn "WSL command had errors: $cmd"
        Write-Host "  $result" -ForegroundColor DarkYellow
    }
    return $result
}

# ==================== STEP 0: Pre-checks ====================
Step "0/6 Pre-checks"

$wslVer = wsl --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Fail "WSL2 not enabled. Run: wsl --install and reboot first"
}
Ok "WSL2 is available"

if (-not (Test-Path $ImageFile)) {
    Fail "Image file not found: $ImageFile`nRun docker-cache-cmd save first"
}
$imageSizeMB = [math]::Round((Get-Item $ImageFile).Length / 1MB, 1)
Ok "Image file exists ($imageSizeMB MB): $ImageFile"
Write-Host "  Project root: $ProjectRoot" -ForegroundColor DarkGray
Write-Host "  Cache dir:    $CacheDir" -ForegroundColor DarkGray

# ==================== STEP 1: Check Ubuntu WSL ====================
Step "1/6 Check workspace WSL distro"

$distros = @(wsl -l -q 2>&1 | ForEach-Object { $_.Trim() } | Where-Object { $_ -ne "" })
$ubuntuInstalled = ($distros -contains $WorkspaceDistro) -or ($distros -contains "Ubuntu")

if (-not $ubuntuInstalled) {
    Write-Host "  Installing Ubuntu..." -ForegroundColor Yellow
    wsl --install -d Ubuntu
    Write-Host ""
    Write-Host "  [ATTENTION] Ubuntu installed. Please:" -ForegroundColor Yellow
    Write-Host "    1. Restart terminal" -ForegroundColor Yellow
    Write-Host "    2. Launch Ubuntu and set username/password" -ForegroundColor Yellow
    Write-Host "    3. Re-run this script" -ForegroundColor Yellow
    exit 0
}
Ok "Ubuntu is installed"

# Wake Ubuntu if stopped
$ubuntuLine = wsl -l -v 2>&1 | Select-String "Ubuntu"
if ($ubuntuLine -match "Stopped") {
    wsl -d Ubuntu -u root -- echo "wake" | Out-Null
    Start-Sleep -Seconds 1
}
Ok "Ubuntu is running"

# ==================== STEP 2: Install Podman ====================
Step "2/6 Check Podman"

$podmanCheck = (WslBash "Ubuntu" "which podman 2>/dev/null && podman --version || echo NOT_INSTALLED") | Select-Object -Last 1
if ($podmanCheck -match "NOT_INSTALLED") {
    Write-Host "  Installing Podman (1-2 min)..." -ForegroundColor Yellow
    wsl -d Ubuntu -u root -- bash -c "apt-get update -qq && apt-get install -y -qq podman" 2>&1 | Select-Object -Last 3
    $podmanVer = (WslBash "Ubuntu" "podman --version") | Select-Object -Last 1
    Ok "Podman installed: $podmanVer"
} else {
    Ok "Podman available: $podmanCheck"
}

# ==================== STEP 3: Load image -> Export rootfs ====================
Step "3/6 Convert image to rootfs"

if ((Test-Path $rootfsLocal) -and -not $Force) {
    $rootfsSizeMB = [math]::Round((Get-Item $rootfsLocal).Length / 1MB, 1)
    Skip "rootfs already exists ($rootfsSizeMB MB), use -Force to re-export"
} else {
    Write-Host "  Loading image into Podman..." -ForegroundColor Yellow
    WslBash "Ubuntu" "podman load -i '$wslImageTar'" | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }

    Write-Host "  Exporting rootfs (gzip -1, 3-5 min)..." -ForegroundColor Yellow

    # Detect image name (handle <none> tags)
    $imageName = (wsl -d Ubuntu -u root -- bash -c "podman images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' | head -1" 2>&1 | Select-Object -Last 1).Trim()
    if (-not $imageName) {
        $imageId = (wsl -d Ubuntu -u root -- bash -c "podman images -q | head -1" 2>&1 | Select-Object -Last 1).Trim()
        wsl -d Ubuntu -u root -- bash -c "podman tag $imageId $DistroName`:latest"
        $imageName = "$DistroName:latest"
    }
    Write-Host "  Using image: $imageName" -ForegroundColor DarkGray

    # Clean up stale container, create, export, cleanup
    wsl -d Ubuntu -u root -- bash -c "podman rm -f wsl-export 2>/dev/null" | Out-Null
    wsl -d Ubuntu -u root -- bash -c "podman create --name wsl-export '$imageName'" 2>&1 | Select-Object -Last 3 | ForEach-Object { Write-Host "  $_" -ForegroundColor DarkGray }
    wsl -d Ubuntu -u root -- bash -c "podman export wsl-export | gzip -1 > '$wslRootfsOut'"
    wsl -d Ubuntu -u root -- bash -c "podman rm wsl-export" | Out-Null

    if (-not (Test-Path $rootfsLocal)) {
        Fail "rootfs export failed: $rootfsLocal not generated"
    }
    $rootfsSizeMB = [math]::Round((Get-Item $rootfsLocal).Length / 1MB, 1)
    Ok "rootfs exported ($rootfsSizeMB MB)"
}

# ==================== STEP 4: Import WSL ====================
Step "4/6 Import WSL distro"

$distroExists = @(wsl -l -q 2>&1 | ForEach-Object { $_.Trim() } | Where-Object { $_ -eq $DistroName }).Count -gt 0
if ($distroExists -and -not $Force) {
    Skip "Distro $DistroName already exists, use -Force to re-import"
} else {
    if ($distroExists -and $Force) {
        Write-Host "  Existing distro found, force removing..." -ForegroundColor Yellow
        wsl --unregister $DistroName
        Remove-Item -Recurse -Force $InstallDir -ErrorAction SilentlyContinue
        Start-Sleep -Seconds 2
    }

    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    Ok "Install dir: $InstallDir"

    Write-Host "  Importing WSL2 (1-2 min)..." -ForegroundColor Yellow
    wsl --import $DistroName $InstallDir $rootfsLocal --version 2
    if ($LASTEXITCODE -ne 0) {
        Fail "WSL import failed"
    }
    Ok "WSL distro imported"
}

# ==================== STEP 5: Configure default user ====================
Step "5/6 Configure default user and environment"

# Detect default user: check wsl.conf first, then common names, then parse passwd
$defaultUser = ""

# Check existing wsl.conf
$wslConf = (wsl -d $DistroName -u root -- cat /etc/wsl.conf 2>&1 | Select-Object -Last 5) -join "`n"
if ($wslConf -match '(?m)^default=(\S+)') {
    $candidate = $Matches[1].Trim()
    $exists = (wsl -d $DistroName -u root -- id -u $candidate 2>&1 | Select-Object -Last 1).Trim()
    if ($exists -match '^\d+$') {
        $defaultUser = $candidate
    }
}

# Try common dev user names (devcontainer convention)
if (-not $defaultUser) {
    foreach ($candidate in @("devuser", "vscode", "developer", "ubuntu", "user")) {
        $uid = (wsl -d $DistroName -u root -- id -u $candidate 2>&1 | Select-Object -Last 1).Trim()
        if ($uid -match '^\d+$' -and [int]$uid -ge 1000) {
            $defaultUser = $candidate
            break
        }
    }
}

# Fallback: first user with UID>=1000 in passwd
if (-not $defaultUser) {
    $passwdContent = wsl -d $DistroName -u root -- cat /etc/passwd 2>&1
    foreach ($line in $passwdContent) {
        if ($line -match '^([^:]+):[^:]*:(\d+):') {
            $uid = [int]$Matches[2]
            if ($uid -ge 1000 -and $uid -lt 65534) {
                $defaultUser = $Matches[1]
                break
            }
        }
    }
}

if (-not $defaultUser) {
    Warn "No regular user found, falling back to root"
    $defaultUser = "root"
} else {
    Ok "Detected user: $defaultUser"
}

# Detect systemd
wsl -d $DistroName -u root -- test -f /usr/lib/systemd/systemd 2>$null
$systemdVal = if ($LASTEXITCODE -eq 0) { "true" } else { "false" }
wsl -d $DistroName -u root -- sh -c "printf '[user]\ndefault=$defaultUser\n[boot]\nsystemd=$systemdVal\n' > /etc/wsl.conf"
Ok "wsl.conf written (default=$defaultUser, systemd=$systemdVal)"

# Configure conda global activation (detect conda path)
$condaPath = ""
foreach ($p in @("/opt/conda", "/root/miniconda3", "/root/anaconda3")) {
    wsl -d $DistroName -u root -- test -f "$p/etc/profile.d/conda.sh" 2>$null
    if ($LASTEXITCODE -eq 0) { $condaPath = $p; break }
}
if (-not $condaPath) {
    $homeDirs = @(wsl -d $DistroName -u root -- ls -d /home/*/miniconda3 /home/*/anaconda3 2>$null)
    foreach ($d in $homeDirs) {
        $d = $d.Trim()
        if ($d) {
            wsl -d $DistroName -u root -- test -f "$d/etc/profile.d/conda.sh" 2>$null
            if ($LASTEXITCODE -eq 0) { $condaPath = $d; break }
        }
    }
}
if ($condaPath) {
    wsl -d $DistroName -u root -- bash -c "echo '. $condaPath/etc/profile.d/conda.sh && conda activate base' > /etc/profile.d/conda.sh"
    Ok "Conda global activation configured: $condaPath"
}

# Terminate to apply config
wsl --terminate $DistroName
Start-Sleep -Seconds 1
Ok "Distro restarted"

# ==================== STEP 6: Smoke Test ====================
Step "6/6 Smoke test"

$allPassed = $true

# Test 1: Startup
$r = (wsl -d $DistroName -- bash -l -c "echo OK" 2>&1 | Select-Object -Last 1).Trim()
if ($r -eq "OK") { Ok "Startup: OK" } else { Warn "Startup: got '$r'"; $allPassed = $false }

# Test 2: User
$r = (wsl -d $DistroName -- bash -l -c "whoami" 2>&1 | Select-Object -Last 1).Trim()
if ($r -eq $defaultUser) { Ok "User: $r" } else { Warn "User: expected '$defaultUser', got '$r'"; $allPassed = $false }

# Test 3: Writable
$r = (wsl -d $DistroName -- bash -l -c "touch /tmp/_t && rm /tmp/_t && echo WRITABLE" 2>&1 | Select-Object -Last 1).Trim()
if ($r -eq "WRITABLE") { Ok "Writable: OK" } else { Warn "Writable: got '$r'"; $allPassed = $false }

# Test 4: Windows drive mount
$driveLetter = $ProjectRoot.Substring(0,1).ToLower()
$r = (wsl -d $DistroName -- bash -l -c "ls /mnt/$driveLetter/ > /dev/null 2>&1 && echo DRIVE-MOUNT || echo NO-DRIVE" 2>&1 | Select-Object -Last 1).Trim()
if ($r -eq "DRIVE-MOUNT") { Ok "Drive mount: /mnt/$driveLetter accessible" } else { Warn "Drive /mnt/$driveLetter not accessible"; $allPassed = $false }

# Test 5: Python version
$pyVer = (wsl -d $DistroName -- bash -l -c "python3 --version 2>&1 || echo NO_PYTHON" 2>&1 | Select-Object -Last 1).Trim()
if ($pyVer -match "Python") { Ok "Python: $pyVer" } else { Write-Host "  [INFO] Python not detected (may be a base image)" -ForegroundColor DarkGray }

# ==================== DONE ====================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
if ($allPassed) {
    Write-Host "  Restore complete!" -ForegroundColor Green
} else {
    Write-Host "  Restore completed with warnings" -ForegroundColor Yellow
}
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Commands:" -ForegroundColor White
Write-Host "    wsl -d $DistroName              # Enter dev environment"
Write-Host "    wsl --terminate $DistroName     # Stop distro"
Write-Host "    wsl --unregister $DistroName    # DELETE distro (irreversible!)"
Write-Host ""
