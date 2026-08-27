#!/usr/bin/env pwsh
#Requires -Version 7.0
<#
.SYNOPSIS
    jpman — PowerShell 7 CLI for jupyter-podman-rootless container management.

.DESCRIPTION
    Zero-dependency PowerShell 7 CLI that manages the jupyter-podman-rootless
    container via WSL interop. Container lifecycle commands are delegated to the
    bash jpman inside the WSL distro; wsl-export/wsl-verify are implemented
    natively in PowerShell for direct wsl.exe access.

.NOTES
    Quick start (from project root in PowerShell 7):
      pwsh -File bin/jpman.ps1 start
      pwsh -File bin/jpman.ps1 wsl-export
      # Or: .\bin\jpman.ps1 start (after Set-ExecutionPolicy)

.LINK
    https://github.com/xinetzone/SpecWeave/tree/main/apps/containers/jupyter-podman-rootless
#>
[CmdletBinding()]
param(
    [Parameter(Position=0, ValueFromRemainingArguments=$true)]
    [string[]]$Arguments
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

# ---------------------------------------------------------------------------
# Auto-locate project root (script lives in <project>/bin/jpman.ps1)
# ---------------------------------------------------------------------------
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# ---------------------------------------------------------------------------
# Load .env file if present
# ---------------------------------------------------------------------------
function Import-EnvFile {
    param([string]$Path)
    if (-not (Test-Path $Path)) { return }
    foreach ($line in Get-Content $Path) {
        if ($line -match '^\s*#' -or $line -match '^\s*$') { continue }
        if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
            $name = $Matches[1]
            $value = $Matches[2].Trim('"', "'")
            if (-not (Get-Item -Path "env:$name" -ErrorAction SilentlyContinue)) {
                Set-Item -Path "env:$name" -Value $value
            }
        }
    }
}

Import-EnvFile (Join-Path $ProjectRoot '.env')

# ---------------------------------------------------------------------------
# Default configuration (overridable via env vars or .env)
# ---------------------------------------------------------------------------
$ContainerName  = if ($env:JUPYTER_CONTAINER_NAME) { $env:JUPYTER_CONTAINER_NAME } else { 'jupyter-chaos-test' }
$Image          = if ($env:JUPYTER_IMAGE)          { $env:JUPYTER_IMAGE }          else { 'localhost/jupyter-podman-rootless:latest' }
$SshPort        = if ($env:JUPYTER_SSH_PORT)       { [int]$env:JUPYTER_SSH_PORT }   else { 2222 }
$JupyterPort    = if ($env:JUPYTER_PORT)           { [int]$env:JUPYTER_PORT }       else { 8888 }
$Password       = if ($env:JUPYTER_PASSWORD)       { $env:JUPYTER_PASSWORD }        else { 'devpass123' }
$Token          = if ($env:JUPYTER_TOKEN)          { $env:JUPYTER_TOKEN }           else { 'chaostest2026' }
$Workspace      = if ($env:JUPYTER_WORKSPACE)      { $env:JUPYTER_WORKSPACE }       else { Split-Path -Parent (Split-Path -Parent (Split-Path -Parent $ProjectRoot)) }
$CacheDir       = Join-Path $ProjectRoot '.image-cache'
$WslCacheDir    = Join-Path $ProjectRoot '.wsl-cache'
$WslDistro      = if ($env:JUPYTER_WSL_DISTRO)       { $env:JUPYTER_WSL_DISTRO }       else { 'Ubuntu' }
$WslTargetDistro= if ($env:JUPYTER_WSL_TARGET_DISTRO) { $env:JUPYTER_WSL_TARGET_DISTRO } else { 'jupyter-podman-rootless' }
$WslInstallDir  = if ($env:JUPYTER_WSL_INSTALL_DIR)   { $env:JUPYTER_WSL_INSTALL_DIR }   else { '' }
$WslDefaultUser = if ($env:JUPYTER_WSL_DEFAULT_USER)  { $env:JUPYTER_WSL_DEFAULT_USER }  else { 'devuser' }
$CondaPath      = if ($env:JUPYTER_CONDA_PATH)        { $env:JUPYTER_CONDA_PATH }        else { '/opt/conda' }
$CondaEnvName   = if ($env:JUPYTER_CONDA_ENV)         { $env:JUPYTER_CONDA_ENV }         else { 'main' }
$CondaEnvBin    = "$CondaPath/envs/$CondaEnvName/bin"

# ---------------------------------------------------------------------------
# Colors (using PSStyle for pwsh native ANSI support)
# ---------------------------------------------------------------------------
if ($Host.UI.SupportsVirtualTerminal -or $env:WT_SESSION -or $env:TERM_PROGRAM) {
    $Reset  = $PSStyle.Reset
    $Green  = $PSStyle.Foreground.Green
    $Yellow = $PSStyle.Foreground.Yellow
    $Red    = $PSStyle.Foreground.Red
    $Cyan   = $PSStyle.Foreground.Cyan
    $Bold   = $PSStyle.Bold
} else {
    $Reset = $Green = $Yellow = $Red = $Cyan = $Bold = ''
}

function Write-Info  { param([string]$Msg) Write-Host "${Green}[INFO]${Reset}  $Msg" }
function Write-Warn  { param([string]$Msg) Write-Host "${Yellow}[WARN]${Reset}  $Msg" }
function Write-Err   { param([string]$Msg) Write-Host "${Red}[ERROR]${Reset} $Msg" -ForegroundColor Red }
function Die        { param([string]$Msg) Write-Err $Msg; exit 1 }

# ---------------------------------------------------------------------------
# WSL helper functions
# ---------------------------------------------------------------------------
function Get-WslExe {
    $wsl = Get-Command wsl.exe -ErrorAction SilentlyContinue
    if (-not $wsl) {
        $candidate = Join-Path $env:SystemRoot 'System32\wsl.exe'
        if (Test-Path $candidate) { return $candidate }
        Die 'wsl.exe not found. Ensure WSL2 is installed (wsl --install).'
    }
    return $wsl.Source
}

function ConvertTo-WslPath {
    param([Parameter(Mandatory)][string]$WinPath)
    # Normalize to full path and convert backslashes to forward slashes for wslpath
    # (wsl.exe on Windows mangles backslashes when passing args to WSL)
    $fullPath = [System.IO.Path]::GetFullPath($WinPath)
    $unixStylePath = $fullPath -replace '\\','/'

    # Try wslpath via WSL first
    try {
        $result = & (Get-WslExe) -d $WslDistro -- wslpath -u $unixStylePath 2>$null
        if ($LASTEXITCODE -eq 0 -and $result) { return ($result -join "`n").Trim() }
    } catch {}
    # Manual fallback
    $drive = $fullPath.Substring(0,1).ToLower()
    $rest = $fullPath.Substring(2) -replace '\\','/'
    return "/mnt/$drive$rest"
}

function ConvertFrom-WslPath {
    param([Parameter(Mandatory)][string]$WslPath)
    try {
        $result = & (Get-WslExe) -d $WslDistro -- wslpath -w $WslPath 2>$null
        if ($LASTEXITCODE -eq 0 -and $result) { return ($result -join "`n").Trim() }
    } catch {}
    # Manual fallback: /mnt/d/path -> D:\path
    if ($WslPath -match '^/mnt/([a-z])/(.*)$') {
        $drive = $Matches[1].ToUpper()
        $rest = $Matches[2] -replace '/','\'
        return "$drive`:\$rest"
    }
    return $WslPath
}

function Test-WslDistro {
    param([Parameter(Mandatory)][string]$Name)
    $wsl = Get-WslExe
    # wsl.exe -l -q outputs UTF-16 LE with null bytes; decode properly in pwsh
    $output = & $wsl -l -q 2>$null
    if ($LASTEXITCODE -ne 0) { return $false }
    $lines = ($output -join "`n") -replace "`0",'' -split "`n" | ForEach-Object { $_.Trim() }
    foreach ($line in $lines) {
        if ($line -ieq $Name) { return $true }
    }
    return $false
}

function Stop-WslDistro {
    param([Parameter(Mandatory)][string]$Name)
    $wsl = Get-WslExe
    & $wsl --terminate $Name 2>$null | Out-Null
    Start-Sleep -Seconds 1
}

function Invoke-WslCommand {
    param(
        [string]$Distro,
        [string]$User,
        [Parameter(Mandatory)][string]$Command,
        [switch]$LoginShell
    )
    $wsl = Get-WslExe
    $wslArgs = @()
    if ($Distro) { $wslArgs += '-d'; $wslArgs += $Distro }
    if ($User)   { $wslArgs += '-u'; $wslArgs += $User }
    $wslArgs += '--'
    # Wrap command in a subshell to isolate `set -e` effects, then append an
    # exit-code echo. The subshell ensures that even if the inner command uses
    # `set -e` and fails, the parent bash process continues to the echo so we
    # always capture the true exit code.
    $shellExe = if ($LoginShell) { 'bash' } else { 'bash' }
    $shellFlag = if ($LoginShell) { '-l' } else { '' }
    # Use single-quote for the marker in bash to avoid any expansion issues.
    # PowerShell escaping: "" -> " inside double-quoted string; `$ -> literal $
    $wrappedCommand = "( $Command ); echo JP_EXIT_MARKER:`$?"
    if ($LoginShell) {
        $wslArgs += $shellExe; $wslArgs += $shellFlag; $wslArgs += '-c'; $wslArgs += $wrappedCommand
    } else {
        $wslArgs += $shellExe; $wslArgs += '-c'; $wslArgs += $wrappedCommand
    }
    $prevEap = $ErrorActionPreference
    $prevNativeEap = if (Get-Variable -Name PSNativeCommandUseErrorActionPreference -ErrorAction SilentlyContinue) { $PSNativeCommandUseErrorActionPreference } else { $null }
    $ErrorActionPreference = 'Continue'
    if ($null -ne $prevNativeEap) { $PSNativeCommandUseErrorActionPreference = $false }
    $output = & $wsl @wslArgs 2>&1
    $ErrorActionPreference = $prevEap
    if ($null -ne $prevNativeEap) { $PSNativeCommandUseErrorActionPreference = $prevNativeEap }

    # Parse the exit code marker from the end of output
    $rc = 1
    $outputText = ($output | ForEach-Object { $_.ToString() }) -join "`n"
    if ($outputText -match 'JP_EXIT_MARKER:(\d+)') {
        $rc = [int]$Matches[1]
        # Remove the marker line from output so it doesn't pollute display
        $cleanOutput = $outputText -replace 'JP_EXIT_MARKER:\d+\s*', ''
        if ($cleanOutput.Trim()) { Write-Host $cleanOutput.TrimEnd() }
    } else {
        # No marker found — show raw output
        Write-Host $outputText
    }
    return $rc
}

function Invoke-WslCommandOutput {
    param(
        [string]$Distro,
        [string]$User,
        [Parameter(Mandatory)][string]$Command,
        [switch]$LoginShell
    )
    $wsl = Get-WslExe
    $wslArgs = @()
    if ($Distro) { $wslArgs += '-d'; $wslArgs += $Distro }
    if ($User)   { $wslArgs += '-u'; $wslArgs += $User }
    $wslArgs += '--'
    if ($LoginShell) {
        $wslArgs += 'bash'; $wslArgs += '-l'; $wslArgs += '-c'; $wslArgs += $Command
    } else {
        $wslArgs += 'bash'; $wslArgs += '-c'; $wslArgs += $Command
    }
    $prevEap = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    $output = & $wsl @wslArgs 2>$null
    $ErrorActionPreference = $prevEap
    return ($output -join "`n").Trim()
}

# ---------------------------------------------------------------------------
# Command: wsl-export (native PowerShell implementation)
# ---------------------------------------------------------------------------
function Invoke-WslExport {
    param(
        [string]$DistroName = $WslTargetDistro,
        [string]$InstallDir = '',
        [switch]$Force
    )

    if (-not $InstallDir) {
        $InstallDir = Join-Path $WslCacheDir $DistroName
    }

    $wsl = Get-WslExe

    # Check for cached image
    $latestLink = Join-Path $CacheDir 'jupyter-podman-rootless-latest.tar.gz'
    $cachedArchive = ''
    if (Test-Path $latestLink) {
        $cachedArchive = $latestLink
    } else {
        $archives = Get-ChildItem -Path $CacheDir -Filter 'jupyter-podman-rootless-*.tar.gz' -ErrorAction SilentlyContinue |
            Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($archives) { $cachedArchive = $archives.FullName }
    }

    if (-not $cachedArchive -or -not (Test-Path $cachedArchive)) {
        Die "No cached image found. Run 'jpman save' first (inside WSL), or build the image."
    }

    Write-Info "Using cached image: $cachedArchive"

    # Check if distro already exists
    if (Test-WslDistro $DistroName) {
        if ($Force) {
            Write-Warn "Distro '$DistroName' already exists, unregistering due to --force..."
            & $wsl --unregister $DistroName 2>$null | Out-Null
            Start-Sleep -Seconds 2
        } else {
            Die "WSL distro '$DistroName' already exists. Use -Force to overwrite (will unregister first), or unregister manually: wsl --unregister $DistroName"
        }
    }

    # Determine rootfs output path
    $rootfsOut = Join-Path $WslCacheDir "$DistroName-rootfs.tar.gz"
    $rootfsOutWsl = ConvertTo-WslPath $rootfsOut
    $rootfsOutDirWsl = Split-Path $rootfsOutWsl -Parent
    $cachedArchiveWsl = ConvertTo-WslPath $cachedArchive
    $installDirWin = $InstallDir

    # Ensure output directory exists on Windows side (avoids WSL drvfs mkdir issues)
    if (-not (Test-Path $WslCacheDir)) {
        New-Item -ItemType Directory -Path $WslCacheDir -Force | Out-Null
    }

    # Step 1-2: Load image and export rootfs via Podman (in WSL)
    if (-not (Test-Path $rootfsOut) -or $Force) {
        Write-Info 'Step 1/5: Loading image into Podman...'
        # Try rootful first (avoids UID/GID mapping issues); fall back to rootless
        $podmanUser = 'root'
        $rc = Invoke-WslCommand -Distro $WslDistro -User 'root' -Command "gunzip -c '$cachedArchiveWsl' | podman load"
        if ($rc -ne 0) {
            Write-Warn 'rootful podman failed, trying rootless...'
            $podmanUser = ''
            $rc = Invoke-WslCommand -Distro $WslDistro -Command "gunzip -c '$cachedArchiveWsl' | podman load"
            if ($rc -ne 0) { Die 'Failed to load image into Podman (tried both root and rootless).' }
        }

        Write-Info 'Step 2/5: Creating container and exporting flat rootfs (gzip -1)...'

        # Detect image tag (use same user context as load)
        $imageTag = Invoke-WslCommandOutput -Distro $WslDistro -User $podmanUser -Command "podman images --format '{{.Repository}}:{{.Tag}}' | grep -v '<none>' | head -1"
        if (-not $imageTag) {
            $imageId = Invoke-WslCommandOutput -Distro $WslDistro -User $podmanUser -Command 'podman images -q | head -1'
            if ($imageId) {
                Invoke-WslCommand -Distro $WslDistro -User $podmanUser -Command "podman tag '$imageId' '$Image'" | Out-Null
                $imageTag = $Image
            }
        }
        if (-not $imageTag) { Die 'Could not determine image tag after podman load.' }
        Write-Info "  Image tag: $imageTag (running as $(if($podmanUser){'root'}else{'current user'}))"

        # Create temp container and export
        $tmpContainer = "wsl-export-$(Get-Random -Maximum 99999)"
        $exportCmd = @"
set -e
podman rm -f '$tmpContainer' >/dev/null 2>&1 || true
podman create --name '$tmpContainer' '$imageTag' >/dev/null
mkdir -p '$rootfsOutDirWsl'
podman export '$tmpContainer' | gzip -1 > '$rootfsOutWsl'
podman rm '$tmpContainer' >/dev/null
"@
        $rc = Invoke-WslCommand -Distro $WslDistro -User $podmanUser -Command $exportCmd
        if ($rc -ne 0) {
            # Cleanup on failure
            Invoke-WslCommand -Distro $WslDistro -User $podmanUser -Command "podman rm -f '$tmpContainer' >/dev/null 2>&1 || true" | Out-Null
            Die "Failed to export rootfs from container."
        }

        $rootfsSize = (Get-Item $rootfsOut).Length / 1MB
        Write-Info ('  RootFS exported: {0:N1} MB' -f $rootfsSize)
    } else {
        Write-Info "RootFS already exists, skipping export (use -Force to rebuild): $rootfsOut"
    }

    # Step 3: Import into WSL
    Write-Info "Step 3/5: Importing into WSL2 at $installDirWin..."
    New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
    $rc = & $wsl --import $DistroName $InstallDir $rootfsOut --version 2 2>&1
    if ($LASTEXITCODE -ne 0) { Die "Failed to import into WSL2: $rc" }

    # Step 4: Configure wsl.conf and conda
    Write-Info 'Step 4/5: Configuring wsl.conf and Conda activation...'

    $wslConf = @"
[user]
default=$WslDefaultUser

[boot]
systemd=false

[automount]
enabled=true
mountFsTab=true
options="metadata,umask=0022,fmask=0011,dmask=0000"

[network]
generateHosts=true
generateResolvConf=true
"@

    # Write wsl.conf via temp file approach
    $tempWslConf = Join-Path $env:TEMP "jpman-wslconf-$(Get-Random).tmp"
    Set-Content -Path $tempWslConf -Value $wslConf -NoNewline -Encoding Ascii
    $tempWslConfWsl = ConvertTo-WslPath $tempWslConf
    Invoke-WslCommand -Distro $DistroName -User 'root' -Command "cp '$tempWslConfWsl' /etc/wsl.conf && chmod 644 /etc/wsl.conf && echo 'wsl.conf written'" | Out-Null
    Remove-Item $tempWslConf -ErrorAction SilentlyContinue

    # Configure conda activation — activate the 'main' env (cp314t free-threading + Jupyter)
    $condaCheck = Invoke-WslCommandOutput -Distro $DistroName -User 'root' -Command "test -f '$CondaPath/etc/profile.d/conda.sh' && echo OK || echo MISSING"
    $mainEnvCheck = Invoke-WslCommandOutput -Distro $DistroName -User 'root' -Command "test -d '$CondaPath/envs/$CondaEnvName' && echo OK || echo MISSING"
    if ($condaCheck -eq 'OK') {
        $activateEnv = if ($mainEnvCheck -eq 'OK') { $CondaEnvName } else { 'base' }
        $condaSh = ". '$CondaPath/etc/profile.d/conda.sh'`nconda activate $activateEnv`n"
        $tempCondaSh = Join-Path $env:TEMP "jpman-conda-$(Get-Random).tmp"
        Set-Content -Path $tempCondaSh -Value $condaSh -NoNewline -Encoding Ascii
        $tempCondaShWsl = ConvertTo-WslPath $tempCondaSh
        Invoke-WslCommand -Distro $DistroName -User 'root' -Command "cp '$tempCondaShWsl' /etc/profile.d/conda.sh && chmod +x /etc/profile.d/conda.sh && echo 'Conda activation configured ($activateEnv)'" | Out-Null
        Remove-Item $tempCondaSh -ErrorAction SilentlyContinue
    } else {
        Write-Warn "Conda init script not found at $CondaPath, skipping conda configuration."
    }

    # Step 5: Terminate to apply config
    Write-Info 'Step 5/5: Restarting WSL distro to apply configuration...'
    Stop-WslDistro $DistroName
    Start-Sleep -Seconds 2

    # Verify default user
    $verifiedUser = Invoke-WslCommandOutput -Distro $DistroName -Command 'whoami' -LoginShell
    if ($verifiedUser -ne $WslDefaultUser) {
        Write-Warn "Default user may not be set correctly (got: '$verifiedUser', expected: '$WslDefaultUser')."
        Write-Warn 'Try: wsl --shutdown then retry. Or manually check /etc/wsl.conf.'
    } else {
        Write-Info "Default user verified: $verifiedUser"
    }

    # Run smoke test
    Write-Host ''
    Write-Info 'Running quick verification...'
    Invoke-WslVerify -DistroName $DistroName | Out-Null

    Write-Host ''
    Write-Info '✅ WSL export complete!'
    Write-Host ''
    Write-Host "  Enter environment:  wsl -d $DistroName"
    Write-Host "  Run JupyterLab:     wsl -d $DistroName -- jupyter lab --no-browser --ip=0.0.0.0"
    Write-Host "  Start SSH+Jupyter:  wsl -d $DistroName -u root -- supervisord -c /etc/supervisor/supervisord.conf"
    Write-Host "  Unregister:         wsl --unregister $DistroName"
    Write-Host ''
}

# ---------------------------------------------------------------------------
# Command: wsl-verify (native PowerShell implementation)
# ---------------------------------------------------------------------------
function Invoke-WslVerify {
    param([string]$DistroName = $WslTargetDistro)

    if (-not (Test-WslDistro $DistroName)) {
        Die "WSL distro '$DistroName' does not exist."
    }

    Write-Host ''
    Write-Host "${Bold}${Cyan}🔍 WSL Distro Verification: $DistroName${Reset}"
    Write-Host ''

    $script:_check_pass = 0
    $script:_check_fail = 0

    function Invoke-Check {
        param(
            [Parameter(Mandatory)][string]$Name,
            [Parameter(Mandatory)][string]$Command,
            [string]$Expect = '.+',
            [switch]$SkipOnFail
        )
        Write-Host -NoNewline "  [$Name] "
        try {
            $result = Invoke-WslCommandOutput -Distro $DistroName -Command $Command -LoginShell
            $rc = $LASTEXITCODE
        } catch {
            $result = $_.Exception.Message
            $rc = 1
        }
        $firstLine = ($result -split "`n")[0]
        if ($rc -eq 0 -and $result -match $Expect) {
            Write-Host "${Green}✅ PASS${Reset}"
            Write-Host "      → $firstLine"
            $script:_check_pass++
        } else {
            Write-Host "${Red}❌ FAIL${Reset}"
            Write-Host "      → $result"
            $script:_check_fail++
        }
    }

    Write-Host "${Bold}  Basic Environment${Reset}"
    Invoke-Check 'Startup'   'echo OK' 'OK'
    Invoke-Check 'User'      'whoami' "^$WslDefaultUser`$"
    Invoke-Check 'Writable'  'touch /tmp/test && rm /tmp/test && echo WRITABLE' 'WRITABLE'
    Invoke-Check 'Home dir'  'echo $HOME' "/home/$WslDefaultUser"

    Write-Host "${Bold}  Drive Mounts${Reset}"
    $cMount = Invoke-WslCommand -Distro $DistroName -Command 'ls /mnt/c/ >/dev/null 2>&1' -LoginShell
    if ($cMount -eq 0) {
        Invoke-Check 'C: drive' 'ls /mnt/c/ >/dev/null && echo C-MOUNT-OK' 'C-MOUNT-OK'
    } else {
        Write-Host "  [C: drive]  ${Yellow}⚠️  SKIP (C: not mounted)${Reset}"
    }
    $dMount = Invoke-WslCommand -Distro $DistroName -Command 'ls /mnt/d/ >/dev/null 2>&1' -LoginShell
    if ($dMount -eq 0) {
        Invoke-Check 'D: drive' 'ls /mnt/d/ >/dev/null && echo D-MOUNT-OK' 'D-MOUNT-OK'
    } else {
        Write-Host "  [D: drive]  ${Yellow}⚠️  SKIP (D: not mounted)${Reset}"
    }

    Write-Host "${Bold}  Python/Conda Environment${Reset}"
    Invoke-Check 'Conda'      'conda --version 2>&1' 'conda'
    Invoke-Check 'Python'     'python --version 2>&1' 'Python 3\.14'
    $condaEnvBinEscaped = [regex]::Escape($CondaEnvBin)
    Invoke-Check 'Python path' 'which python' $condaEnvBinEscaped
    Invoke-Check 'Pip'        'pip --version 2>&1' 'pip'

    # Free-threading check (uses temp file to avoid quote-escaping hell across pwsh→wsl→sh→python)
    Write-Host -NoNewline '  [Free-thread] '
    $ftPyCode = @'
import sys
print(sys._is_gil_enabled() if hasattr(sys, "_is_gil_enabled") else True)
'@
    $ftTmp = Join-Path $env:TEMP "jpman-ftcheck-$(Get-Random).py"
    Set-Content -Path $ftTmp -Value $ftPyCode -Encoding Ascii -NoNewline
    $ftTmpWsl = ConvertTo-WslPath $ftTmp
    $ftResult = Invoke-WslCommandOutput -Distro $DistroName -Command "python '$ftTmpWsl'" -LoginShell
    Remove-Item $ftTmp -ErrorAction SilentlyContinue
    if ($ftResult -eq 'False') {
        Write-Host "${Green}✅ PASS${Reset}"
        Write-Host '      → GIL disabled (free-threading active)'
        $script:_check_pass++
    } else {
        Write-Host "${Red}❌ FAIL${Reset}"
        Write-Host "      → $ftResult"
        $script:_check_fail++
    }

    Write-Host "${Bold}  Jupyter & Tools${Reset}"
    Invoke-Check 'JupyterLab' 'jupyter lab --version 2>&1 | tail -1' '^[0-9]'
    Invoke-Check 'Git'        'git --version 2>&1' 'git version'
    Invoke-Check 'Bash'       'bash --version 2>&1 | head -1' 'GNU bash'
    Invoke-Check 'Locale'     'locale 2>/dev/null | grep LANG= | head -1' 'zh_CN\.UTF-8|en_US\.UTF-8'

    Write-Host ''
    Write-Host "${Bold}  Results: ${Green}$script:_check_pass passed${Reset}, ${Red}$script:_check_fail failed${Reset}"
    Write-Host ''

    return ($script:_check_fail -eq 0)
}

# ---------------------------------------------------------------------------
# Command: help
# ---------------------------------------------------------------------------
function Show-Help {
    Write-Host @'

==============================================================================
 jpman — Zero-dependency CLI for jupyter-podman-rootless container management
==============================================================================

 Quick start (from project root):
   pwsh bin/jpman.ps1 start
   pwsh bin/jpman.ps1 wsl-export

 Usage (PowerShell 7):
   pwsh -File bin/jpman.ps1 <command>

 Commands:
   start       Start container (idempotent; creates if not exists)
   stop        Stop and remove container
   restart     Stop then start
   status      Show container status
   shell       Enter container shell (devuser by default, --root for root)
   logs        View container logs (-f for follow)
   exec CMD    Execute command in container (devuser)
   root CMD    Execute command in container (root)
   info        Show access info (URL, credentials, ports)
   url         Print Jupyter Lab URL (for quick copy-paste)
   save        Save image to .image-cache/ for backup
   load        Load image from .image-cache/
   rebuild     Incremental rebuild (config changes only, <10s)
   rebuild-all Full rebuild from Containerfile (slow, needs network)
   wsl-export  Export image cache as WSL2 distro (one-click convert)
                -DistroName <name>  Target distro name (default: jupyter-podman-rootless)
                -InstallDir <path>  WSL install directory (default: .wsl-cache/<name>)
                -Force              Overwrite existing distro
   wsl-verify  Verify WSL2 distro environment (Smoke Test)
                -DistroName <name>  Distro to verify (default: jupyter-podman-rootless)
   keepalive   Start WSL keepalive process
   install     Install bash jpman symlink in WSL ~/.local/bin
   help        Show this help message

 All defaults can be overridden via environment variables or a .env file
 in the project root. Variable names use JUPYTER_* prefix.

==============================================================================
'@
}

# ---------------------------------------------------------------------------
# Main dispatch
# ---------------------------------------------------------------------------
function Main {
    if (-not $Arguments -or $Arguments.Count -eq 0) {
        Show-Help
        exit 0
    }

    $cmd = $Arguments[0]
    $cmdArgs = @($Arguments | Select-Object -Skip 1)

    switch -Regex ($cmd) {
        # Native PowerShell commands
        '^(wsl-export)$' {
            $distroName = $WslTargetDistro
            $installDir = $WslInstallDir
            $force = $false

            for ($i = 0; $i -lt $cmdArgs.Count; $i++) {
                switch ($cmdArgs[$i]) {
                    '--distro-name' { $distroName = $cmdArgs[++$i] }
                    '-n'            { $distroName = $cmdArgs[++$i] }
                    '--install-dir' { $installDir = $cmdArgs[++$i] }
                    '-d'            { $installDir = $cmdArgs[++$i] }
                    '--force'       { $force = $true }
                    '-f'            { $force = $true }
                    '-Force'        { $force = $true }
                    default         { Write-Warn "Unknown option: $($cmdArgs[$i])" }
                }
            }
            Invoke-WslExport -DistroName $distroName -InstallDir $installDir -Force:$force
            exit 0
        }

        '^(wsl-verify)$' {
            $distroName = $WslTargetDistro
            for ($i = 0; $i -lt $cmdArgs.Count; $i++) {
                switch ($cmdArgs[$i]) {
                    '--distro-name' { $distroName = $cmdArgs[++$i] }
                    '-n'            { $distroName = $cmdArgs[++$i] }
                }
            }
            $ok = Invoke-WslVerify -DistroName $distroName
            exit ($(if ($ok) { 0 } else { 1 }))
        }

        '^(help|-h|--help)$' {
            Show-Help
            exit 0
        }

        # All other commands delegate to bash jpman inside WSL
        default {
            $bashJpman = ConvertTo-WslPath (Join-Path $ScriptDir 'jpman')
            $argList = @($cmd) + $cmdArgs
            $argStr = $argList -join ' '

            # Check if JUPYTER_WSL_DISTRO is set; if so use that distro, otherwise use default
            $targetDistro = if ($env:JUPYTER_WSL_DISTRO) { $env:JUPYTER_WSL_DISTRO } else { '' }

            $wsl = Get-WslExe
            $wslArgs = @()
            if ($targetDistro) { $wslArgs += '-d'; $wslArgs += $targetDistro }
            $wslArgs += '--'; $wslArgs += 'bash'; $wslArgs += $bashJpman
            $wslArgs += $argList

            & $wsl @wslArgs
            exit $LASTEXITCODE
        }
    }
}

Main
