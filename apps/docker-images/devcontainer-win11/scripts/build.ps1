# DevContainer Win11 - Build Script (PowerShell)
# Usage: .\scripts\build.ps1 [-Tag <tag>] [-Cn] [-NoCache] [-VerifyMode <mode>]

param(
    [string]$Tag = "devcontainer-win11:latest",
    [switch]$Cn,
    [switch]$NoCache,
    [ValidateSet("standard", "fast", "off")]
    [string]$VerifyMode = "standard",
    [string]$PythonVersion = "3.14"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

Write-Host ""
Write-Host "============================================================"
Write-Host "  DevContainer Win11 - Build Script"
Write-Host "  Project root: $projectRoot"
Write-Host "  Tag: $Tag"
Write-Host "  CN mirrors: $($Cn.IsPresent)"
Write-Host "  Verify mode: $VerifyMode"
Write-Host "  Python version: $PythonVersion (free-threading cp314t)"
Write-Host "============================================================"
Write-Host ""

# Check Docker is available
try {
    $dockerVer = docker --version 2>&1
    Write-Host "[INFO] Docker: $dockerVer"
} catch {
    Write-Error "Docker not found! Please ensure Docker Desktop is installed and running."
    exit 1
}

# Check Windows container mode
$osType = docker info --format '{{.OSType}}' 2>&1
if ($osType -ne "windows") {
    Write-Warning "Docker is not in Windows container mode!"
    Write-Warning "Please switch Docker Desktop to Windows containers before building."
    Write-Warning "Right-click Docker tray icon -> Switch to Windows containers..."
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Build arguments
$buildArgs = @(
    "build",
    "-t", $Tag,
    "--build-arg", "PYTHON_VERSION=$PythonVersion",
    "--build-arg", "BUILD_VERIFY_MODE=$VerifyMode"
)

if ($Cn) {
    $buildArgs += @(
        "--build-arg", "CONDA_MIRROR=tuna",
        "--build-arg", "PIP_MIRROR=aliyun"
    )
    Write-Host "[INFO] Using China mirrors: conda=tuna, pip=aliyun"
}

if ($NoCache) {
    $buildArgs += "--no-cache"
    Write-Host "[INFO] No-cache mode enabled"
}

$buildArgs += $projectRoot

Write-Host "[INFO] Starting Docker build..."
Write-Host ""

$buildStart = Get-Date
& docker @buildArgs
$buildExit = $LASTEXITCODE

$buildEnd = Get-Date
$buildDuration = [int]($buildEnd - $buildStart).TotalSeconds

Write-Host ""
if ($buildExit -eq 0) {
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "  BUILD SUCCESS!" -ForegroundColor Green
    Write-Host "  Tag: $Tag" -ForegroundColor Green
    Write-Host "  Duration: $([math]::Floor($buildDuration/60))m $($buildDuration%60)s" -ForegroundColor Green
    Write-Host ""
    Write-Host "  To run:" -ForegroundColor Green
    Write-Host "    .\scripts\start.ps1" -ForegroundColor White
    Write-Host "============================================================" -ForegroundColor Green
} else {
    Write-Host "============================================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED (exit code $buildExit)" -ForegroundColor Red
    Write-Host "  Duration: $([math]::Floor($buildDuration/60))m $($buildDuration%60)s" -ForegroundColor Red
    Write-Host "============================================================" -ForegroundColor Red
    exit $buildExit
}
