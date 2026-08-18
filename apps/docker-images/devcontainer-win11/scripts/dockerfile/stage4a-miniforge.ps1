# Stage 4a: Install Miniforge3 + configure .condarc
param(
    [string]$CondaMirror = "official"
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

Write-Host "[BUILD] Miniforge3 installation starting..."
Write-Host "[BUILD] Conda mirror: $CondaMirror"

$miniforgeUrl = "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Windows-x86_64.exe"
$installerPath = "C:\temp\miniforge-installer.exe"

Write-Host "[INFO] Downloading Miniforge3 latest from GitHub..."
Invoke-WebRequest -Uri $miniforgeUrl -OutFile $installerPath -UseBasicParsing
Write-Host "[OK] Miniforge installer downloaded"

Write-Host "[INFO] Silently installing Miniforge3 to C:\conda..."
# Miniforge silent install: /InstallationType=JustMe /RegisterPython=0 /S /D=C:\conda
# Note: /S for silent, /D specifies install directory (must be last arg, no quotes around path)
$installArgs = @('/InstallationType=JustMe', '/RegisterPython=0', '/S', '/D=C:\conda')
$proc = Start-Process -FilePath $installerPath -ArgumentList $installArgs -Wait -PassThru -NoNewWindow
if ($proc.ExitCode -ne 0) {
    Write-Error "Miniforge installation failed with exit code $($proc.ExitCode)"
}
Write-Host "[OK] Miniforge3 installed to C:\conda"

Remove-Item $installerPath -Force -ErrorAction SilentlyContinue

# Configure .condarc
Write-Host "[BUILD] Configuring .condarc (conda-forge channel)..."
$condarcPath = "C:\conda\.condarc"
$condarcBase = @"
channels:
  - conda-forge
channel_priority: strict
show_channel_urls: true
solver: libmamba
auto_activate_base: false
"@

if ($CondaMirror -eq "tuna" -or $CondaMirror -eq "bfsu") {
    $mirrorUrl = if ($CondaMirror -eq "tuna") {
        "https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud"
    } else {
        "https://mirrors.bfsu.edu.cn/anaconda/cloud"
    }
    $condarcWithMirror = @"
channels:
  - conda-forge
channel_priority: strict
show_channel_urls: true
solver: libmamba
auto_activate_base: false
default_channels:
  - $mirrorUrl/conda-forge/
custom_channels:
  conda-forge: $mirrorUrl/conda-forge/
"@
    Set-Content -Path $condarcPath -Value $condarcWithMirror -Encoding UTF8
    Write-Host "[BUILD] Using $CondaMirror conda mirror: $mirrorUrl"
} else {
    Set-Content -Path $condarcPath -Value $condarcBase -Encoding UTF8
    Write-Host "[BUILD] Using official conda-forge channels"
}

# Add conda to PATH
$condaBinPath = "C:\conda;C:\conda\Scripts;C:\conda\Library\bin"
$machinePath = [Environment]::GetEnvironmentVariable('PATH', 'Machine')
if ($machinePath -notlike "*C:\conda*") {
    [Environment]::SetEnvironmentVariable('PATH', "$condaBinPath;$machinePath", 'Machine')
    $env:PATH = "$condaBinPath;$env:PATH"
}
Write-Host "[OK] Conda added to system PATH"

# Initialize conda for PowerShell
Write-Host "[INFO] Initializing conda for PowerShell..."
& "C:\conda\Scripts\conda.exe" init powershell 2>&1 | ForEach-Object { Write-Host "  $_" }
Write-Host "[OK] conda init completed"

# Verify conda
Write-Host "[INFO] Verifying conda installation..."
$condaVersion = & "C:\conda\Scripts\conda.exe" --version 2>&1
Write-Host "  - conda: $condaVersion"

Write-Host "[OK] Stage 4a: Miniforge3 installed and configured successfully"
