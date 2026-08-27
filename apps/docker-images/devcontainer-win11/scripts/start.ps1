# DevContainer Win11 - Start Script (PowerShell)
# Usage: .\scripts\start.ps1 [-Tag <tag>] [-SshPort <port>] [-JupyterPort <port>] [-Password <pass>] [-Token <token>]

param(
    [string]$Tag = "devcontainer-win11:latest",
    [int]$SshPort = 2222,
    [int]$JupyterPort = 8888,
    [string]$Password = "",
    [string]$Token = "",
    [string]$Workspace = "",
    [switch]$Detached
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$containerName = "devcontainer-win11"

if (-not $Workspace) {
    $Workspace = Join-Path $projectRoot "workspace"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  DevContainer Win11 - Start Script"
Write-Host "  Image: $Tag"
Write-Host "  SSH port: $SshPort -> 22"
Write-Host "  Jupyter port: $JupyterPort -> 8888"
Write-Host "  Workspace: $Workspace"
Write-Host "  Container name: $containerName"
Write-Host "============================================================"
Write-Host ""

# Ensure workspace directory exists
if (-not (Test-Path $Workspace)) {
    New-Item -ItemType Directory -Path $Workspace -Force | Out-Null
    Write-Host "[INFO] Created workspace directory: $Workspace"
}

# Generate password/token if not provided
if (-not $Password) {
    $Password = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 16 | ForEach-Object { [char]$_ })
    Write-Host "[INFO] Generated random devuser password"
}
if (-not $Token) {
    $Token = -join ((48..57) + (65..90) + (97..122) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
    Write-Host "[INFO] Generated random Jupyter token"
}

# Stop and remove existing container with same name
$existing = docker ps -a --filter "name=$containerName" --format '{{.Names}}' 2>$null
if ($existing -eq $containerName) {
    Write-Host "[INFO] Removing existing container '$containerName'..."
    docker rm -f $containerName 2>$null | Out-Null
}

# Prepare docker run arguments
$dockerArgs = @(
    "run",
    "-d",
    "--name", $containerName,
    "-p", "${SshPort}:22",
    "-p", "${JupyterPort}:8888",
    "-e", "USER_PASSWORD=$Password",
    "-e", "JUPYTER_TOKEN=$Token",
    "--restart", "unless-stopped"
)

# Mount Docker named pipe for DooD (if available)
$dockerPipe = "\\.\pipe\docker_engine"
if (Test-Path $dockerPipe) {
    $dockerArgs += @("-v", "//./pipe/docker_engine://./pipe/docker_engine")
    Write-Host "[INFO] Docker named pipe mounted (DooD mode enabled)"
} else {
    Write-Host "[WARN] Docker named pipe not found - Docker CLI won't connect to host"
}

# Mount workspace
$dockerArgs += @("-v", "${Workspace}:C:\workspace")

$dockerArgs += $Tag

Write-Host "[INFO] Starting container..."
$containerId = & docker @dockerArgs 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to start container: $containerId"
    exit 1
}

Write-Host "[OK] Container started: $containerId"
Write-Host ""

# Wait for container to be healthy
Write-Host "[INFO] Waiting for services to start (this may take 10-30 seconds)..."
$maxWait = 60
$waited = 0
$healthy = $false
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 5
    $waited += 5

    $status = docker inspect --format='{{.State.Status}}' $containerName 2>$null
    if ($status -ne "running") {
        Write-Host "[INFO] Container status: $status"
        if ($status -eq "exited") {
            Write-Error "Container exited unexpectedly! Check logs: docker logs $containerName"
            exit 1
        }
        continue
    }

    # Check health
    $health = docker inspect --format='{{.State.Health.Status}}' $containerName 2>$null
    if ($health -eq "healthy") {
        $healthy = $true
        break
    }

    Write-Host "  Waiting... ($waited/$maxWait s, health=$health)"
}

Write-Host ""
Write-Host "============================================================"
Write-Host "  Container ready!" -ForegroundColor Green
Write-Host ""
Write-Host "  SSH access:"
Write-Host "    ssh devuser@localhost -p $SshPort"
Write-Host "    Password: $Password"
Write-Host ""
Write-Host "  Jupyter access:"
Write-Host "    URL: http://localhost:$JupyterPort/"
Write-Host "    Token: $Token"
Write-Host ""
Write-Host "  Docker access:"
if (Test-Path $dockerPipe) {
    Write-Host "    Mode: DooD (host Docker)"
    Write-Host "    Usage: docker exec $containerName docker ps"
} else {
    Write-Host "    Mode: CLI only (DooD pipe not mounted)"
}
Write-Host ""
Write-Host "  Workspace: $Workspace (mounted to C:\workspace)"
Write-Host "  Python: free-threading (cp314t), Py_GIL_DISABLED=1"
Write-Host ""
Write-Host "  Useful commands:"
Write-Host "    docker logs -f $containerName   # View logs"
Write-Host "    docker exec -it $containerName pwsh  # Interactive shell"
Write-Host "    docker stop $containerName      # Stop container"
Write-Host "============================================================"
Write-Host ""
