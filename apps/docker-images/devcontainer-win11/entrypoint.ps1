# DevContainer Win11 - Entrypoint Script
# Equivalent to Linux entrypoint.sh, manages service startup and configuration
#
# Services managed:
#   - sshd (OpenSSH Server on port 22)
#   - JupyterLab (on port 8888 via conda main env)
#
# Environment variables:
#   USER_PASSWORD   - Password for devuser (default: auto-generated random)
#   JUPYTER_TOKEN   - Jupyter token (default: auto-generated random)
#   JUPYTER_PASSWORD - Jupyter password (optional, takes precedence over token)
#   JUPYTER_PORT    - Jupyter port (default: 8888)
#   ENABLE_SSH      - Enable SSH (default: yes)
#   ENABLE_JUPYTER  - Enable Jupyter (default: yes)
#   GRANT_SUDO      - Grant admin privileges (not applicable on Windows, ignored)
#   Py_GIL_DISABLED - Set to 1 for free-threading Python (already set system-wide)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ── Logging functions ──
function Write-Info { param([string]$Message) Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [INFO]  $Message" }
function Write-Warn { param([string]$Message) Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [WARN]  $Message" -ForegroundColor Yellow }
function Write-Error { param([string]$Message) Write-Host "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] [ERROR] $Message" -ForegroundColor Red }

# ── Banner ──
function Show-Banner {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  DevContainer Win11 starting..."
    Write-Host "  Time: $(Get-Date)"
    Write-Host "  Host: $env:COMPUTERNAME"
    Write-Host "  OS: Windows Server Core (LTSC2022 / Win11 kernel)"
    Write-Host "  Python: Free-threading (cp314t) via Miniforge3 conda-forge"
    Write-Host "============================================================"
    Write-Host ""
}

# ── System diagnostics ──
function Show-Diagnostics {
    Write-Info "========== System Diagnostics =========="
    Write-Info "Timezone: $((Get-TimeZone).Id) (now: $(Get-Date))"
    Write-Info "User: whoami = $(whoami)"
    Write-Info "Non-root user: devuser"

    $pyVer = & "C:\conda\envs\main\python.exe" --version 2>&1
    Write-Info "Python: $pyVer"

    $condaVer = & "C:\conda\Scripts\conda.exe" --version 2>&1
    Write-Info "Conda: $condaVer"

    $ftEnv = [Environment]::GetEnvironmentVariable('Py_GIL_DISABLED', 'Machine')
    Write-Info "Py_GIL_DISABLED (system): $ftEnv"

    $dockerVer = & "C:\Program Files\Docker\docker.exe" --version 2>&1
    Write-Info "Docker CLI: $dockerVer"

    Write-Info "Enabled services:"
    Write-Info "  SSH:      ${env:ENABLE_SSH:-yes}"
    Write-Info "  Jupyter:  ${env:ENABLE_JUPYTER:-yes}"
    Write-Info "  Docker:   DooD (host named pipe, no daemon)"

    $buildInfoPath = "C:\ProgramData\devcontainer\build-info"
    if (Test-Path $buildInfoPath) {
        Write-Info "Build info:"
        Get-Content $buildInfoPath | ForEach-Object { Write-Info "  $_" }
    }
    Write-Info "========================================"
    Write-Host ""
}

# ── Password generation ──
function New-RandomPassword {
    param([int]$Length = 16)
    $chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+'
    $rng = [System.Security.Cryptography.RandomNumberGenerator]::Create()
    $bytes = New-Object byte[] $Length
    $rng.GetBytes($bytes)
    $result = ""
    for ($i = 0; $i -lt $Length; $i++) {
        $result += $chars[$bytes[$i] % $chars.Length]
    }
    return $result
}

# ── Setup user password ──
function Set-UserPassword {
    param([string]$UserName = "devuser")

    Write-Info "[Config] Setting user password for $UserName..."

    if ($env:USER_PASSWORD) {
        $password = ConvertTo-SecureString $env:USER_PASSWORD -AsPlainText -Force
        $generated = $false
    } else {
        $passwordPlain = New-RandomPassword -Length 16
        $password = ConvertTo-SecureString $passwordPlain -AsPlainText -Force
        $env:USER_PASSWORD = $passwordPlain
        $generated = $true
    }

    try {
        $existingUser = Get-LocalUser -Name $UserName -ErrorAction SilentlyContinue
        if ($existingUser) {
            Set-LocalUser -Name $UserName -Password $password
            Write-Info "[OK] Password set for $UserName"
        } else {
            New-LocalUser -Name $UserName -Password $password -Description "DevContainer user" -PasswordNeverExpires | Out-Null
            Write-Info "[OK] User $UserName created with password"
        }
    } catch {
        Write-Warn "Failed to set password: $_"
    }

    if ($generated) {
        Write-Host ""
        Write-Host "    ************************************************"
        Write-Host "    * [IMPORTANT] devuser password: $($env:USER_PASSWORD)"
        Write-Host "    * SSH login: ssh devuser@<host> -p <port>"
        Write-Host "    ************************************************"
        Write-Host ""
    }
}

# ── Setup SSH ──
function Start-SshService {
    if ("${env:ENABLE_SSH:-yes}" -ne "yes") {
        Write-Info "[SSH] SSH disabled (ENABLE_SSH != yes)"
        return
    }

    Write-Info "[SSH] Configuring and starting sshd..."

    # Generate host keys if missing
    $keyGen = "C:\Windows\System32\OpenSSH\ssh-keygen.exe"
    if (Test-Path $keyGen) {
        & $keyGen -A 2>&1 | ForEach-Object { Write-Host "  $_" }
    }

    # Set correct permissions on sshd_config and host keys
    $sshDir = "C:\ProgramData\ssh"
    if (Test-Path $sshDir) {
        icacls $sshDir /grant "SYSTEM:(OI)(CI)F" /C 2>$null | Out-Null
        icacls $sshDir /grant "Administrators:(OI)(CI)F" /C 2>$null | Out-Null
    }

    # Start sshd service
    try {
        $sshdService = Get-Service -Name sshd -ErrorAction SilentlyContinue
        if ($sshdService) {
            if ($sshdService.Status -ne 'Running') {
                Start-Service -Name sshd
                Write-Info "[OK] sshd service started"
            } else {
                Write-Info "[OK] sshd service already running"
            }
        } else {
            Write-Warn "sshd service not found"
        }
    } catch {
        Write-Warn "Failed to start sshd: $_"
        # Try starting sshd directly
        $sshdExe = "C:\Windows\System32\OpenSSH\sshd.exe"
        if (Test-Path $sshdExe) {
            Start-Process -FilePath $sshdExe -WindowStyle Hidden
            Write-Info "[OK] sshd started directly"
        }
    }

    # Open SSH port in firewall (in case Windows Firewall is active)
    try {
        if (-not (Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue)) {
            New-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -DisplayName "OpenSSH Server (sshd)" -Enabled True -Direction Inbound -Protocol TCP -Action Allow -LocalPort 22 -ErrorAction SilentlyContinue | Out-Null
            Write-Info "[OK] Firewall rule added for SSH port 22"
        }
    } catch {
        Write-Warn "Firewall rule setup skipped (may be running in container): $_"
    }
}

# ── Setup Jupyter ──
function Start-JupyterService {
    if ("${env:ENABLE_JUPYTER:-yes}" -ne "yes") {
        Write-Info "[Jupyter] Jupyter disabled (ENABLE_JUPYTER != yes)"
        return
    }

    Write-Info "[Jupyter] Configuring and starting JupyterLab..."

    $jupyterPort = "${env:JUPYTER_PORT:-8888}"
    $jupyterToken = if ($env:JUPYTER_TOKEN) { $env:JUPYTER_TOKEN } else { New-RandomPassword -Length 32 }
    $env:JUPYTER_TOKEN = $jupyterToken

    $jupyterDir = "C:\workspace"
    if (-not (Test-Path $jupyterDir)) {
        New-Item -ItemType Directory -Path $jupyterDir -Force | Out-Null
    }

    $jupyterConfigDir = "C:\Users\devuser\.jupyter"
    New-Item -ItemType Directory -Path $jupyterConfigDir -Force | Out-Null

    $jupyterConfig = @"
c = get_config()
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = $jupyterPort
c.ServerApp.open_browser = False
c.ServerApp.root_dir = r'$jupyterDir'
c.ServerApp.allow_root = False
c.ServerApp.allow_origin = '${env:JUPYTER_ALLOW_ORIGIN:-*}'
c.ServerApp.allow_credentials = True
c.ServerApp.token = '$jupyterToken'
c.ServerApp.password = ''
c.IdentityProvider.token = '$jupyterToken'
"@

    if ($env:JUPYTER_PASSWORD) {
        Write-Info "[Jupyter] Setting Jupyter password from JUPYTER_PASSWORD env var..."
        $pythonExe = "C:\conda\envs\main\python.exe"
        $passwordHash = & $pythonExe -c "from jupyter_server.auth import passwd; print(passwd('$($env:JUPYTER_PASSWORD)'))" 2>&1
        $jupyterConfig += @"

c.ServerApp.password = '$passwordHash'
c.ServerApp.token = ''
c.IdentityProvider.token = ''
"@
    }

    $jupyterConfigPath = Join-Path $jupyterConfigDir "jupyter_server_config.py"
    Set-Content -Path $jupyterConfigPath -Value $jupyterConfig -Encoding UTF8

    # Set permissions for devuser
    icacls $jupyterConfigDir /grant "devuser:(OI)(CI)F" /T /C 2>$null | Out-Null

    # Start Jupyter as devuser using Start-Process
    $pythonExe = "C:\conda\envs\main\python.exe"
    $jupyterCmd = "$pythonExe -m jupyterlab --config=$jupyterConfigPath"

    Write-Info "[Jupyter] Starting JupyterLab on port $jupyterPort (as devuser)..."
    $jupyterLog = "C:\ProgramData\devcontainer\jupyter.log"

    # Create scheduled job or start as background process
    $proc = Start-Process -FilePath $pythonExe `
        -ArgumentList "-m", "jupyterlab", "--config=$jupyterConfigPath" `
        -WorkingDirectory $jupyterDir `
        -RedirectStandardOutput $jupyterLog `
        -RedirectStandardError "$jupyterLog.err" `
        -WindowStyle Hidden `
        -PassThru `
        -ErrorAction SilentlyContinue

    if ($proc) {
        Write-Info "[OK] JupyterLab started (PID: $($proc.Id))"
    } else {
        Write-Warn "Failed to start JupyterLab in background, trying direct..."
        # Fallback: start directly
        Start-Process -FilePath $pythonExe -ArgumentList "-m", "jupyterlab", "--config=$jupyterConfigPath" -WindowStyle Hidden -ErrorAction SilentlyContinue
    }
}

# ── Setup SSH keys ──
function Install-SshKeys {
    Write-Info "[SSH] Setting up SSH authorized_keys..."

    $sshDir = "C:\Users\devuser\.ssh"
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null

    if ($env:SSH_PUBLIC_KEY) {
        $authKeysPath = Join-Path $sshDir "authorized_keys"
        Add-Content -Path $authKeysPath -Value $env:SSH_PUBLIC_KEY
        icacls $authKeysPath /grant "devuser:F" /C 2>$null | Out-Null
        $keyCount = (Get-Content $authKeysPath -ErrorAction SilentlyContinue | Measure-Object).Count
        Write-Info "[OK] SSH public key added (count: $keyCount)"
    } else {
        Write-Info "[SSH] No SSH_PUBLIC_KEY set, password auth only"
    }

    icacls $sshDir /grant "devuser:(OI)(CI)F" /T /C 2>$null | Out-Null
}

# ── Ready banner ──
function Show-ReadyBanner {
    Write-Host ""
    Write-Host "============================================================"
    Write-Host "  Container ready!"
    Write-Host ""
    Write-Host "  User: devuser"
    Write-Host ""

    if ("${env:ENABLE_SSH:-yes}" -eq "yes") {
        Write-Host "  SSH access:"
        Write-Host "    ssh devuser@<host> -p <mapped-port>"
        Write-Host "    Password: $($env:USER_PASSWORD)"
        Write-Host ""
    }

    Write-Host "  Docker access:"
    Write-Host "    Mode: DooD (host Docker via named pipe)"
    Write-Host "    Usage: docker ps (via host daemon)"
    Write-Host ""

    if ("${env:ENABLE_JUPYTER:-yes}" -eq "yes") {
        Write-Host "  Jupyter access:"
        Write-Host "    URL: http://<host>:<mapped-port>/"
        if ($env:JUPYTER_PASSWORD) {
            Write-Host "    Password: (use JUPYTER_PASSWORD you set)"
        } else {
            Write-Host "    Token: $($env:JUPYTER_TOKEN)"
        }
        Write-Host ""
    }

    Write-Host "  Working directory: C:\workspace (mount volumes here)"
    Write-Host "  Python: free-threading (cp314t), Py_GIL_DISABLED=1"
    Write-Host "============================================================"
    Write-Host ""
}

# ── Command mode: if arguments passed, execute them ──
if ($args.Count -gt 0) {
    Write-Info "Command mode detected: '$($args -join ' ')' - skipping service startup"
    Show-Diagnostics
    # Execute the command
    & $args[0] $args[1..($args.Count-1)]
    exit $LASTEXITCODE
}

# ── Main startup flow ──
Show-Banner
Show-Diagnostics
Set-UserPassword -UserName "devuser"
Install-SshKeys
Start-SshService
Start-JupyterService

# Wait a moment for services to initialize
Start-Sleep -Seconds 3

Show-ReadyBanner

# ── Keep container running and monitor services ──
Write-Info "Entrypoint initialized, monitoring services..."
try {
    while ($true) {
        Start-Sleep -Seconds 30

        # Check sshd
        $sshd = Get-Process -Name sshd -ErrorAction SilentlyContinue
        if (-not $sshd -and "${env:ENABLE_SSH:-yes}" -eq "yes") {
            Write-Warn "sshd not running, attempting restart..."
            Start-Service sshd -ErrorAction SilentlyContinue
        }

        # Check jupyter
        $jupyterProc = Get-Process -Name python -ErrorAction SilentlyContinue | Where-Object { $_.CommandLine -like "*jupyter*" } | Select-Object -First 1
        if (-not $jupyterProc -and "${env:ENABLE_JUPYTER:-yes}" -eq "yes") {
            Write-Warn "Jupyter not detected (may still be starting or running as different process)"
        }
    }
} catch {
    Write-Error "Container interrupted: $_"
    exit 1
}
