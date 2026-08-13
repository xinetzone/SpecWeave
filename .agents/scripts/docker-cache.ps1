#Requires -Version 5.1
param(
    [string]$Action = "load",
    [string]$Image = "xmnn-whl-builder:latest",
    [switch]$All,
    [switch]$Help
)

$ErrorActionPreference = "Stop"

if ($Help) {
    Write-Host "Usage: docker-cache.ps1 [load|save|list|doctor] [image-name] [-All]"
    exit 0
}

$wslExe = Get-Command wsl.exe -ErrorAction SilentlyContinue
if (-not $wslExe) {
    Write-Host "ERROR: wsl.exe not found" -ForegroundColor Red
    exit 1
}

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentsDir = Split-Path -Parent $scriptDir
$projectRoot = Split-Path -Parent $agentsDir

$drive = $projectRoot.Substring(0, 1).ToLower()
$wslProjectRoot = "/mnt/$drive" + $projectRoot.Substring(2).Replace('\', '/')

if ($Action -eq "list" -or $Action -eq "doctor") {
    $wslCmd = "cd '$wslProjectRoot' && bash .agents/scripts/docker-cache $Action"
} elseif ($All) {
    $wslCmd = "cd '$wslProjectRoot' && bash .agents/scripts/docker-cache $Action --all"
} else {
    $wslCmd = "cd '$wslProjectRoot' && bash .agents/scripts/docker-cache $Action '$Image'"
}

Write-Host ""
Write-Host "Docker Cache - Action: $Action" -ForegroundColor Cyan
Write-Host ""

$startTime = Get-Date
wsl.exe bash -c $wslCmd
$exitCode = $LASTEXITCODE
$duration = [math]::Round(((Get-Date) - $startTime).TotalSeconds)

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "OK: Operation completed in $duration seconds" -ForegroundColor Green
} else {
    Write-Host "ERROR: Operation failed with exit code $exitCode" -ForegroundColor Red
}

exit $exitCode
