#Requires -Version 5.1
<#
.SYNOPSIS
    dind-ssh Management Script for Windows (PowerShell)
.DESCRIPTION
    Supports both Docker Desktop and wslc.exe (WSL Containers preview) runtimes.
    Run from project root: .\scripts\dind.ps1 <command> [options]
.PARAMETER Command
    check-env, build, run, stop, ssh, logs, status, exec, clean, help
.EXAMPLE
    .\scripts\dind.ps1 check-env
    .\scripts\dind.ps1 build
    .\scripts\dind.ps1 run --port 2222 --password test123
    .\scripts\dind.ps1 run --runtime wslc --port 2223 --password test123
    .\scripts\dind.ps1 ssh root
    .\scripts\dind.ps1 exec docker ps
#>

param(
    [Parameter(Position=0)]
    [string]$Command = "help",

    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"
$ProjectDir = Split-Path -Parent $PSScriptRoot
$ImageName = "dind-ssh"
$ContainerName = "dind-test"
$DefaultSshPort = 2222
$Runtime = ""
$SshPort = $DefaultSshPort
$RootPassword = ""
$SshKey = ""
$ExtraArgs = @()

$WslcPath = "$env:ProgramFiles\WSL\wslc.exe"
if (-not (Test-Path $WslcPath)) {
    $WslcPath = "wslc.exe"
}

function Write-Info($msg)  { Write-Host "[INFO]  $msg" -ForegroundColor Blue }
function Write-Ok($msg)    { Write-Host "[OK]    $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "[WARN]  $msg" -ForegroundColor Yellow }
function Write-Err($msg)   { Write-Host "[ERROR] $msg" -ForegroundColor Red }
function Write-Cmd($msg)   { Write-Host "[CMD]   $msg" -ForegroundColor Cyan }

function Invoke-Cmd {
    param([string]$Exe, [string[]]$CmdArgs)
    Write-Cmd "$Exe $($CmdArgs -join ' ')"
    & $Exe @CmdArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code $LASTEXITCODE"
    }
}

function Detect-Runtime {
    if ($script:Runtime -eq "docker" -or $script:Runtime -eq "wslc") {
        return
    }

    $dockerAvailable = $false
    try {
        $null = docker info 2>&1
        if ($LASTEXITCODE -eq 0) { $dockerAvailable = $true }
    } catch {}

    $wslcAvailable = $false
    try {
        $null = & $WslcPath --version 2>&1
        if ($LASTEXITCODE -eq 0) { $wslcAvailable = $true }
    } catch {}

    if ($dockerAvailable) {
        $script:Runtime = "docker"
    } elseif ($wslcAvailable) {
        $script:Runtime = "wslc"
    } else {
        Write-Err "No container runtime available (Docker Desktop or wslc.exe)."
        Write-Info "Install options:"
        Write-Info "  1) Docker Desktop: https://www.docker.com/products/docker-desktop/"
        Write-Info "  2) wslc.exe (preview): run 'wsl --update' in PowerShell as Administrator"
        exit 1
    }
    Write-Info "Detected runtime: $($script:Runtime)"
}

function Parse-Args {
    $passthrough = @()
    $i = 0
    while ($i -lt $RemainingArgs.Count) {
        $arg = $RemainingArgs[$i]
        if ($arg -match '^--runtime=(.+)$') {
            $script:Runtime = $Matches[1]
        } elseif ($arg -eq '--runtime' -and $i+1 -lt $RemainingArgs.Count) {
            $script:Runtime = $RemainingArgs[$i+1]; $i++
        } elseif ($arg -match '^--port=(\d+)$') {
            $script:SshPort = [int]$Matches[1]
        } elseif ($arg -eq '--port' -and $i+1 -lt $RemainingArgs.Count) {
            $script:SshPort = [int]$RemainingArgs[$i+1]; $i++
        } elseif ($arg -match '^--name=(.+)$') {
            $script:ContainerName = $Matches[1]
        } elseif ($arg -eq '--name' -and $i+1 -lt $RemainingArgs.Count) {
            $script:ContainerName = $RemainingArgs[$i+1]; $i++
        } elseif ($arg -match '^--password=(.+)$') {
            $script:RootPassword = $Matches[1]
        } elseif ($arg -eq '--password' -and $i+1 -lt $RemainingArgs.Count) {
            $script:RootPassword = $RemainingArgs[$i+1]; $i++
        } elseif ($arg -match '^--ssh-key=(.+)$') {
            $script:SshKey = $Matches[1]
        } elseif ($arg -eq '--ssh-key' -and $i+1 -lt $RemainingArgs.Count) {
            $script:SshKey = $RemainingArgs[$i+1]; $i++
        } else {
            $passthrough += $arg
        }
        $i++
    }
    $script:ExtraArgs = $passthrough
}

function Show-Help {
    Write-Host @"
dind-ssh Management Script (PowerShell/wslc)

Usage: .\scripts\dind.ps1 <command> [options]

Commands:
  check-env     Run environment detection
  build         Build the container image
  run           Start the container (default port 2222)
  stop          Stop and remove the container
  ssh [user]    SSH into the container (default: root)
  logs          View container logs
  status        Show container status
  exec <cmd>    Execute command in container
  clean         Remove container and image
  help          Show this help

Options:
  --runtime=<docker|wslc|auto>  Force runtime (default: auto-detect)
  --port=<port>                 SSH port mapping (default: 2222)
  --name=<name>                 Container name (default: dind-test)
  --password=<pwd>              Root password (default: auto-generated)
  --ssh-key=<key>               SSH public key for auth

Examples:
  .\scripts\dind.ps1 check-env
  .\scripts\dind.ps1 build
  .\scripts\dind.ps1 run --port 2222 --password MySecret123
  .\scripts\dind.ps1 run --runtime wslc --port 2223 --password test123
  .\scripts\dind.ps1 ssh ai
  .\scripts\dind.ps1 exec docker ps

Note: wslc mode is SSH-only (nested dockerd may not start without --privileged).
      Use -e DIND_SKIP_DOCKER=1 automatically applied in wslc run.
"@
}

function Cmd-CheckEnv {
    Write-Host "============================================================"
    Write-Host "  dind-ssh Environment Checker (Windows)"
    Write-Host "  Project: $ProjectDir"
    Write-Host "  Time:    $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    Write-Host "============================================================"
    Write-Host ""

    Write-Info "========== OS Detection =========="
    Write-Ok "Windows detected: $([System.Environment]::OSVersion.VersionString)"
    Write-Host ""

    Write-Info "========== Docker Detection =========="
    try {
        $null = docker --version 2>&1
        if ($LASTEXITCODE -eq 0) {
            $dv = docker --version
            Write-Ok "Docker CLI found: $dv"
            try {
                $null = docker info 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Ok "Docker daemon reachable"
                } else {
                    Write-Warn "Docker daemon not reachable"
                }
            } catch { Write-Warn "Docker daemon not reachable" }
        } else {
            Write-Warn "Docker CLI not found"
        }
    } catch {
        Write-Warn "Docker CLI not found"
    }
    Write-Host ""

    Write-Info "========== WSLC (wslc.exe) Detection =========="
    if (Test-Path $WslcPath) {
        $wv = & $WslcPath --version 2>&1 | Select-Object -First 1
        Write-Ok "wslc.exe found: $wv"
        Write-Warn "  NOTE: wslc is PREVIEW - API may change"
        Write-Warn "  NOTE: Limited network support; DinD may not work (privileged)"
    } else {
        Write-Warn "wslc.exe not found (update WSL: wsl --update)"
    }
    Write-Host ""

    Write-Info "========== Summary =========="
    $dockerOk = $false
    $wslcOk = (Test-Path $WslcPath)
    try { $null = docker info 2>&1; if ($LASTEXITCODE -eq 0) { $dockerOk = $true } } catch {}

    if ($dockerOk) {
        Write-Ok "Docker: AVAILABLE (recommended for full DinD)"
    } else {
        Write-Warn "Docker: NOT AVAILABLE"
    }
    if ($wslcOk) {
        Write-Ok "wslc: AVAILABLE (SSH-only mode, DinD limited)"
    } else {
        Write-Warn "wslc: NOT AVAILABLE"
    }

    if ($dockerOk -or $wslcOk) {
        Write-Ok "========================================"
        Write-Ok "Environment ready!"
        Write-Ok "========================================"
    } else {
        Write-Err "========================================"
        Write-Err "Environment NOT ready"
        Write-Err "========================================"
    }
    Write-Host ""
}

function Cmd-Build {
    Detect-Runtime
    Push-Location $ProjectDir
    try {
        Write-Info "Building image '$ImageName' using runtime: $Runtime"
        switch ($Runtime) {
            "docker" {
                Invoke-Cmd "docker" @("build", "-t", $ImageName, "-f", "Containerfile", ".")
            }
            "wslc" {
                Write-Warn "wslc.exe build - note: wslc build may have limited Containerfile compatibility"
                Invoke-Cmd $WslcPath @("build", "-t", $ImageName, "-f", "Containerfile", ".")
            }
        }
        Write-Ok "Build complete!"
    } finally {
        Pop-Location
    }
}

function Cmd-Run {
    Detect-Runtime
    Push-Location $ProjectDir
    try {
        Write-Info "Starting container '$ContainerName' using runtime: $Runtime"

        $envArgs = @()
        $portArgs = @()
        $volArgs = @()
        $privArgs = @()

        if ($RootPassword) { $envArgs += "-e", "ROOT_PASSWORD=$RootPassword" }
        if ($SshKey) { $envArgs += "-e", "SSH_PUBLIC_KEY=$SshKey" }

        switch ($Runtime) {
            "docker" {
                $portArgs = "-p", "${SshPort}:22"
                $volArgs = "-v", "dind-data:/var/lib/docker"
                $privArgs = "--privileged"

                $existing = docker ps -a --format '{{.Names}}' 2>&1 | Where-Object { $_ -eq $ContainerName }
                if ($existing) {
                    Write-Warn "Container '$ContainerName' already exists, stopping first..."
                    docker rm -f $ContainerName 2>&1 | Out-Null
                }

                $runArgs = @("run", "-d") + $privArgs + $portArgs + $volArgs + $envArgs + @("--name", $ContainerName, $ImageName)
                Invoke-Cmd "docker" $runArgs
                Write-Info "Waiting for container to start..."
                Start-Sleep -Seconds 3
                Write-Ok "Container started!"
            }
            "wslc" {
                Write-Warn "wslc mode: DinD functionality may be limited (no --privileged support)"
                Write-Warn "wslc mode: primarily for SSH access; nested dockerd will be skipped"

                $envArgs += "-e", "DIND_SKIP_DOCKER=1"
                $portArgs = "--publish", "${SshPort}:22"

                $existing = & $WslcPath list 2>&1 | Select-String $ContainerName
                if ($existing) {
                    Write-Warn "Container '$ContainerName' already exists, stopping first..."
                    & $WslcPath rm -f $ContainerName 2>&1 | Out-Null
                }

                $runArgs = @("run", "-d") + $portArgs + $envArgs + @("--name", $ContainerName, $ImageName)
                Write-Cmd "$WslcPath $($runArgs -join ' ')"
                & $WslcPath @runArgs
                if ($LASTEXITCODE -ne 0) {
                    Write-Err "wslc run failed. Ensure WSL2 is up to date (wsl --update)"
                    exit 1
                }
                Write-Info "Waiting for container to start..."
                Start-Sleep -Seconds 5
                Write-Ok "Container started in wslc mode (SSH-only)!"
            }
        }
        Write-Host ""
        Write-Info "SSH connection: ssh -p ${SshPort} root@localhost"
        Write-Info "To view logs: .\scripts\dind.ps1 logs"
        Write-Info "To SSH:      .\scripts\dind.ps1 ssh"
    } finally {
        Pop-Location
    }
}

function Cmd-Stop {
    Detect-Runtime
    Write-Info "Stopping container '$ContainerName'..."
    switch ($Runtime) {
        "docker" { docker rm -f $ContainerName 2>&1 | Out-Null }
        "wslc"   { & $WslcPath rm -f $ContainerName 2>&1 | Out-Null }
    }
    Write-Ok "Container stopped"
}

function Cmd-Logs {
    Detect-Runtime
    switch ($Runtime) {
        "docker" { docker logs -f $ContainerName }
        "wslc"   { & $WslcPath logs -f $ContainerName }
    }
}

function Cmd-Status {
    Detect-Runtime
    Write-Host "=========================================="
    Write-Host "  dind-ssh Status"
    Write-Host "=========================================="
    Write-Host ""
    Write-Info "Runtime: $Runtime"
    Write-Host ""
    switch ($Runtime) {
        "docker" {
            $exists = docker ps -a --format '{{.Names}}' 2>&1 | Where-Object { $_ -eq $ContainerName }
            if ($exists) {
                $state = docker inspect -f '{{.State.Status}}' $ContainerName 2>&1
                Write-Ok "Container '$ContainerName': $state"
                docker ps --filter "name=$ContainerName" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>&1
            } else {
                Write-Warn "Container '$ContainerName': not created"
            }
            Write-Host ""
            docker images $ImageName --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}" 2>&1
        }
        "wslc" {
            $list = & $WslcPath ps -a 2>&1
            if ($list | Select-String $ContainerName) {
                Write-Ok "Container '$ContainerName': exists"
                $list | Select-String $ContainerName
            } else {
                Write-Warn "Container '$ContainerName': not created"
            }
            Write-Host ""
            & $WslcPath images 2>&1 | Select-String $ImageName
        }
    }
    Write-Host ""
}

function Cmd-Ssh {
    Detect-Runtime
    $sshUser = "root"
    if ($ExtraArgs.Count -gt 0) { $sshUser = $ExtraArgs[0] }
    $sshPort = $script:SshPort
    Write-Info "Connecting via SSH as ${sshUser} on port ${sshPort}..."

    switch ($Runtime) {
        "docker" {
            $rootPwd = docker logs $ContainerName 2>&1 | Select-String 'Root password: (\S+)' | Select-Object -Last 1
            if ($rootPwd -and $sshUser -eq "root") {
                $pwd = $rootPwd.Matches.Groups[1].Value
                Write-Info "Root password (from logs): $pwd"
            }
        }
    }
    Write-Cmd "ssh -p ${sshPort} -o StrictHostKeyChecking=no ${sshUser}@localhost"
    ssh -p $sshPort -o StrictHostKeyChecking=no "${sshUser}@localhost"
}

function Cmd-Exec {
    Detect-Runtime
    if ($ExtraArgs.Count -eq 0) {
        Write-Err "No command specified for exec"
        exit 1
    }
    $execCmd = $ExtraArgs -join " "
    switch ($Runtime) {
        "docker" {
            Write-Cmd "docker exec -it $ContainerName $execCmd"
            docker exec -it $ContainerName @ExtraArgs
        }
        "wslc" {
            Write-Cmd "wslc.exe exec -it $ContainerName $execCmd"
            & $WslcPath exec -it $ContainerName @ExtraArgs
        }
    }
}

function Cmd-Clean {
    Detect-Runtime
    Write-Warn "Cleaning up container and image..."
    switch ($Runtime) {
        "docker" {
            docker rm -f $ContainerName 2>&1 | Out-Null
            docker rmi $ImageName 2>&1 | Out-Null
        }
        "wslc" {
            & $WslcPath rm -f $ContainerName 2>&1 | Out-Null
            & $WslcPath rmi $ImageName 2>&1 | Out-Null
        }
    }
    Write-Ok "Cleanup complete"
}

Parse-Args

switch ($Command.ToLower()) {
    "check-env" { Cmd-CheckEnv }
    "build"     { Cmd-Build }
    "run"       { Cmd-Run }
    "stop"      { Cmd-Stop }
    "ssh"       { Cmd-Ssh }
    "logs"      { Cmd-Logs }
    "status"    { Cmd-Status }
    "exec"      { Cmd-Exec }
    "clean"     { Cmd-Clean }
    default     { Show-Help }
}
