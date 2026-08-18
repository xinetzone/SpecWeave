# Stage 5: Install Docker CLI + Compose Plugin (DooD mode - client only, connects to host daemon via named pipe)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "[BUILD] Installing Docker CLI (DooD mode - client only)..."

# We only install Docker CLI binaries, no daemon
# Docker CLI on Windows is distributed as a zip archive
$dockerVersion = "27.4.1"
$dockerZipUrl = "https://download.docker.com/win/static/stable/x86_64/docker-$dockerVersion.zip"
$dockerZipPath = "C:\temp\docker.zip"
$dockerExtractPath = "C:\temp\docker-extract"
$dockerInstallPath = "C:\Program Files\Docker"

Write-Host "[INFO] Downloading Docker CLI v$dockerVersion (static binary)..."
Invoke-WebRequest -Uri $dockerZipUrl -OutFile $dockerZipPath -UseBasicParsing
Write-Host "[OK] Docker CLI zip downloaded"

Write-Host "[INFO] Extracting Docker CLI..."
New-Item -ItemType Directory -Path $dockerExtractPath -Force | Out-Null
Expand-Archive -Path $dockerZipPath -DestinationPath $dockerExtractPath -Force
Write-Host "[OK] Docker CLI extracted"

# Install docker.exe and docker-compose plugin
New-Item -ItemType Directory -Path $dockerInstallPath -Force | Out-Null
New-Item -ItemType Directory -Path "$dockerInstallPath\cli-plugins" -Force | Out-Null

Copy-Item "$dockerExtractPath\docker\docker.exe" -Destination "$dockerInstallPath\docker.exe" -Force
Write-Host "[OK] docker.exe installed to $dockerInstallPath"

# Docker Compose v2 is a CLI plugin
$composeVersion = "2.32.1"
$composeUrl = "https://github.com/docker/compose/releases/download/v$composeVersion/docker-compose-windows-x86_64.exe"
$composePath = "$dockerInstallPath\cli-plugins\docker-compose.exe"

Write-Host "[INFO] Downloading Docker Compose v$composeVersion..."
Invoke-WebRequest -Uri $composeUrl -OutFile $composePath -UseBasicParsing
Write-Host "[OK] Docker Compose plugin installed"

# Add Docker to system PATH
$dockerBinPath = $dockerInstallPath
$machinePath = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
if ($machinePath -notlike "*$dockerInstallPath*") {
    [Environment]::SetEnvironmentVariable('PATH', "$dockerBinPath;$machinePath", 'Machine')
    $env:PATH = "$dockerBinPath;$env:PATH"
}

# Configure Docker CLI to connect to host via named pipe (DooD mode)
# On Windows, the default named pipe path is npipe:////./pipe/docker_engine
# We set DOCKER_HOST env var so docker CLI knows where to connect
Write-Host "[BUILD] Configuring Docker CLI for DooD mode (host named pipe)..."
[Environment]::SetEnvironmentVariable('DOCKER_HOST', 'npipe:////./pipe/docker_engine', 'Machine')
$env:DOCKER_HOST = 'npipe:////./pipe/docker_engine'

# Create .docker directory with config.json (for future use)
$dockerConfigDir = "C:\ProgramData\Docker\config"
New-Item -ItemType Directory -Path $dockerConfigDir -Force | Out-Null
$dockerConfig = @{
    "credsStore" = ""
    "stackOrchestrator" = "compose"
} | ConvertTo-Json
Set-Content -Path "$dockerConfigDir\config.json" -Value $dockerConfig -Encoding UTF8

# Cleanup
Remove-Item $dockerZipPath -Force -ErrorAction SilentlyContinue
Remove-Item $dockerExtractPath -Recurse -Force -ErrorAction SilentlyContinue

# Verify Docker CLI
Write-Host "[INFO] Verifying Docker CLI installation..."
$dockerVer = & "$dockerInstallPath\docker.exe" --version 2>&1
Write-Host "  - $dockerVer"
$composeVer = & "$dockerInstallPath\docker.exe" compose version 2>&1
Write-Host "  - $composeVer"

Write-Host ""
Write-Host "[INFO] Docker DooD configuration:"
Write-Host "  - Mode: DooD (Docker-out-of-Docker)"
Write-Host "  - DOCKER_HOST: npipe:////./pipe/docker_engine"
Write-Host "  - Usage: Mount //./pipe/docker_engine when running: -v //./pipe/docker_engine://./pipe/docker_engine"
Write-Host ""

Write-Host "[OK] Stage 5: Docker CLI + Compose Plugin (DooD mode) installed successfully"
