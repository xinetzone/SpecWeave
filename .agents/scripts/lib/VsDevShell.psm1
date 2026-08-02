# VsDevShell.psm1 - Generic Visual Studio discovery and DevShell loading module
#
# Provides multi-strategy VS installation discovery and robust DevShell environment
# loading with automatic PATH length recovery (cmd.exe 8191-char limit workaround).
#
# Usable by any project needing MSVC toolchain: C/C++ builds, Nuitka, CMake, Rust, etc.
#
# Usage:
#   Import-Module "$PSScriptRoot/VsDevShell.psm1"
#   $vsPath = Find-VisualStudio                    # auto-find best VS with C++ tools
#   $vsPath = Find-VisualStudio -RequireComponent "Microsoft.Component.MSBuild"
#   Enter-MsvcDevShell -VsInstallPath $vsPath      # load MSVC env with PATH auto-recovery
#
# Design principles:
# - No project-specific coupling (no language-specific env management, no build-system assumptions)
# - All strategies are fallbacks: vswhere → dir-scan → env vars
# - Failures in one strategy never block others
# - Caller controls what PATH entries to preserve after DevShell load

Set-StrictMode -Version Latest

# ── VS Version Utilities ─────────────────────────────────────────────────

function Convert-VsVersionDirToNumber {
    <#
    .SYNOPSIS
        Converts a VS version directory name to a comparable numeric version.
    .DESCRIPTION
        Year-based directories (e.g. "2022") map to internal VS major versions.
        Numeric directories (e.g. "18" for VS 18 / 2026 Insiders) used directly.
    #>
    param([string]$VersionDirName)
    $yearMap = @{ "2022" = 17; "2019" = 16; "2017" = 15; "2015" = 14; "2013" = 12 }
    if ($yearMap.ContainsKey($VersionDirName)) { return $yearMap[$VersionDirName] }
    if ($VersionDirName -match '^(\d+)$') { return [int]$Matches[1] }
    return 0
}

function Get-VsEditionPriority {
    <#
    .SYNOPSIS
        Returns a priority score for a VS edition name (higher = preferred).
    .DESCRIPTION
        Priority order: Insiders/Canary (4) > Preview (3) > Enterprise (2) > Professional (1) > Community/BuildTools (0).
        Returns -1 for unknown editions.
    #>
    param([string]$EditionName)
    $en = $EditionName.ToLower()
    if ($en -match 'insiders|canary') { return 4 }
    if ($en -match 'preview') { return 3 }
    if ($en -match 'enterprise') { return 2 }
    if ($en -match 'professional') { return 1 }
    if ($en -match 'community|buildtools') { return 0 }
    return -1
}

# ── Visual Studio Installation Discovery ─────────────────────────────────

function Find-VisualStudio {
    <#
    .SYNOPSIS
        Finds Visual Studio installation using multiple strategies, preferring newest version
        and Insiders/Preview editions.
    .DESCRIPTION
        Multi-strategy discovery (all strategies run, results deduplicated):
        1. vswhere.exe (official method) - with JSON parsing for full version/edition info
        2. Directory scan of Program Files (handles Insiders/Preview not in vswhere)
        3. Environment variables (VSINSTALLDIR, VCToolsInstallDir)

        Candidates are validated by DevShell.dll presence and sorted by:
        version number (descending) → edition priority (descending) → path.
    .PARAMETER Hint
        Explicit VS installation path to use (skips auto-discovery).
    .PARAMETER RequireComponent
        vswhere -requires component ID. Defaults to VC.Tools.x86.x64 (C++ toolchain).
        Pass empty string to find any VS installation regardless of components.
        Common values:
          "Microsoft.VisualStudio.Component.VC.Tools.x86.x64"  (C++ compiler, default)
          "Microsoft.Component.MSBuild"                          (MSBuild only)
          ""                                                     (any VS install)
    .PARAMETER VerboseLog
        Write detailed discovery logs to host (DarkGray color, [VS] prefix).
    #>
    param(
        [string]$Hint = "",
        [string]$RequireComponent = "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
        [switch]$VerboseLog
    )

    function Write-D { param([string]$Msg) if ($VerboseLog) { Write-Host "  [VS] $Msg" -ForegroundColor DarkGray } }

    if ($Hint) {
        $devShell = [IO.Path]::Combine($Hint, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
        if (Test-Path $devShell) {
            Write-D "Using explicit Hint: $Hint"
            return (Resolve-Path $Hint).Path
        }
        throw "DevShell.dll not found in '$Hint'. Is this a valid VS installation?"
    }

    $candidates = [System.Collections.Generic.List[object]]::new()
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    function Add-Candidate {
        param([string]$Path, [string]$Source, [string]$VersionDir = "", [string]$EditionName = "", [int]$VersionNum = 0)
        $devShell = [IO.Path]::Combine($Path, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
        if (-not (Test-Path $devShell)) {
            Write-D "    Skip $Path (no DevShell.dll)"
            return
        }
        $fullPath = (Resolve-Path $Path).Path
        if ($seen.Add($fullPath)) {
            if (-not $VersionDir -or -not $EditionName) {
                $rel = $fullPath -replace [regex]::Escape("Microsoft Visual Studio\"), ""
                $parts = $rel.Split([char]'\', [char]'/')
                if (-not $VersionDir -and $parts.Count -ge 1) { $VersionDir = $parts[0] }
                if (-not $EditionName -and $parts.Count -ge 2) { $EditionName = $parts[1] }
            }
            if ($VersionNum -eq 0) {
                $VersionNum = Convert-VsVersionDirToNumber -VersionDirName $VersionDir
            }
            $edPriority = Get-VsEditionPriority -EditionName $EditionName
            $candidates.Add([pscustomobject]@{
                Path = $fullPath; Source = $Source; VersionDir = $VersionDir
                Edition = $EditionName; VersionNum = $VersionNum; EdPriority = $edPriority
            }) | Out-Null
            Write-D "    ADD v$VersionNum [$EditionName] via $Source at $fullPath"
        } else {
            Write-D "    DEDUP $Path (already found via other strategy)"
        }
    }

    # Strategy 1: vswhere.exe - get ALL installations with full version/edition info
    Write-D "Strategy 1: vswhere.exe"
    foreach ($pfName in @("ProgramFiles(x86)", "ProgramFiles")) {
        $pf = [Environment]::GetEnvironmentVariable($pfName)
        if (-not $pf) { continue }
        $vw = [IO.Path]::Combine($pf, "Microsoft Visual Studio", "Installer", "vswhere.exe")
        if (-not (Test-Path $vw)) { Write-D "  vswhere not found at $vw"; continue }
        Write-D "  vswhere at $vw"
        # Run with required component AND without (to find all installs; required component filters in)
        $reqList = if ($RequireComponent) { @($RequireComponent, "") } else { @("") }
        foreach ($req in $reqList) {
            $vwArgs = @("-products", "*", "-format", "json", "-prerelease")
            if ($req) { $vwArgs = @("-products", "*", "-requires", $req, "-format", "json", "-prerelease") }
            $vwJson = & $vw @vwArgs 2>$null
            if (-not $vwJson) { continue }
            try {
                $installs = $vwJson | ConvertFrom-Json -ErrorAction SilentlyContinue
                foreach ($inst in $installs) {
                    if (-not $inst.installationPath) { continue }
                    $vsPath = $inst.installationPath.Trim()
                    if (-not (Test-Path $vsPath)) { continue }
                    $verNum = 0
                    if ($inst.installationVersion -match '^(\d+)') {
                        $verNum = [int]$Matches[1]
                    }
                    $edition = ""
                    if ($inst.channelId -match 'Insiders|Canary') {
                        $edition = "Insiders"
                    } elseif ($inst.channelId -match 'Preview') {
                        $edition = "Preview"
                    } elseif ($inst.displayName -match 'Enterprise') {
                        $edition = "Enterprise"
                    } elseif ($inst.displayName -match 'Professional') {
                        $edition = "Professional"
                    } elseif ($inst.displayName -match 'Community|Build\s*Tools') {
                        $edition = "Community"
                    } elseif ($inst.productId) {
                        if ($inst.productId -match '\.(\w+)$') { $edition = $Matches[1] }
                    }
                    Add-Candidate -Path $vsPath -Source "vswhere" -VersionNum $verNum -EditionName $edition
                    Write-D "  vswhere found: v$verNum [$edition] at $vsPath"
                }
            } catch {
                Write-Warning "vswhere JSON parse failed: $_"
                Write-Host "  [VS] Falling back to vswhere -latest method..." -ForegroundColor DarkYellow
                $vwArgsFallback = @("-latest", "-products", "*", "-property", "installationPath")
                if ($req) { $vwArgsFallback = @("-latest", "-products", "*", "-requires", $req, "-property", "installationPath") }
                $vsPath = & $vw @vwArgsFallback 2>$null | Select-Object -First 1
                if ($vsPath) {
                    $trimmed = $vsPath.Trim()
                    if ($trimmed) {
                        Write-Host "  [VS] vswhere fallback found: $trimmed" -ForegroundColor DarkGray
                        Add-Candidate -Path $trimmed -Source "vswhere-fallback"
                    }
                }
            }
        }
    }

    # Strategy 2: Directory scan of Program Files
    Write-D "Strategy 2: Directory scan"
    foreach ($pfName in @("ProgramFiles", "ProgramFiles(x86)")) {
        $pf = [Environment]::GetEnvironmentVariable($pfName)
        if (-not $pf) { continue }
        $vsBase = Join-Path $pf "Microsoft Visual Studio"
        if (-not (Test-Path $vsBase)) { continue }
        Write-D "  Scanning $vsBase"
        $versionDirs = Get-ChildItem $vsBase -Directory -ErrorAction SilentlyContinue
        foreach ($versionDir in $versionDirs) {
            Write-D "    Version dir: $($versionDir.Name)"
            $foundInVersion = $false
            foreach ($editionDir in (Get-ChildItem $versionDir.FullName -Directory -ErrorAction SilentlyContinue)) {
                $devShell = [IO.Path]::Combine($editionDir.FullName, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
                if (Test-Path $devShell) {
                    Add-Candidate -Path $editionDir.FullName -Source "dir-scan" -VersionDir $versionDir.Name -EditionName $editionDir.Name
                    Write-D "      $($editionDir.Name): valid DevShell"
                    $foundInVersion = $true
                }
            }
            if (-not $foundInVersion) {
                $devShell = [IO.Path]::Combine($versionDir.FullName, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
                if (Test-Path $devShell) {
                    Add-Candidate -Path $versionDir.FullName -Source "dir-scan" -VersionDir $versionDir.Name -EditionName $versionDir.Name
                    Write-D "      (self): valid DevShell"
                }
            }
        }
    }

    # Strategy 3: Environment variables
    Write-D "Strategy 3: Environment variables"
    foreach ($envVar in @("VSINSTALLDIR", "VCToolsInstallDir")) {
        $ev = [Environment]::GetEnvironmentVariable($envVar)
        if (-not $ev) { continue }
        Write-D "  $envVar = $ev"
        $vsDir = if ($envVar -eq "VCToolsInstallDir") {
            Split-Path (Split-Path (Split-Path $ev -Parent) -Parent) -Parent
        } else {
            $ev.TrimEnd('\', '/')
        }
        if ($vsDir) { Add-Candidate -Path $vsDir -Source "env:$envVar" }
    }

    if ($candidates.Count -eq 0) {
        $compDesc = if ($RequireComponent) { " with component '$RequireComponent'" } else { "" }
        throw "No Visual Studio installation${compDesc} with DevShell found. Use -VsPath to specify it explicitly."
    }

    # Sort by: VersionNum DESC → EdPriority DESC → Path (stable)
    $sorted = $candidates | Sort-Object -Property @{Expression={$_.VersionNum};Descending=$true}, @{Expression={$_.EdPriority};Descending=$true}, Path

    if ($VerboseLog) {
        Write-D "Found $($candidates.Count) VS installation(s):"
        for ($i = 0; $i -lt $sorted.Count; $i++) {
            $c = $sorted[$i]
            $marker = if ($i -eq 0) { "→" } else { " " }
            Write-D "  $marker v$($c.VersionNum) [$($c.Edition)] (pri=$($c.EdPriority)) via $($c.Source): $($c.Path)"
        }
    }

    $best = $sorted[0]
    Write-Host "  Using Visual Studio v$($best.VersionNum) [$($best.Edition)]: $($best.Path)" -ForegroundColor Cyan
    return $best.Path
}

# ── MSVC DevShell Loading with PATH Auto-Recovery ────────────────────────

function Enter-MsvcDevShell {
    <#
    .SYNOPSIS
        Loads MSVC build environment via Visual Studio DevShell, with automatic PATH trimming.
    .DESCRIPTION
        On Windows, Enter-VsDevShell invokes cmd.exe internally which has an 8191-char
        command-line limit. When PATH exceeds this, VsDevCmd.bat fails with "输入行太长"
        (input line too long) but does NOT throw a terminating error — it prints the
        message and returns, leaving env vars in a partially-corrupted state.

        This function:
        1. Attempts DevShell load with current PATH
        2. Captures stderr to detect "input line too long" error (Chinese + English)
        3. Verifies cl.exe is available after loading
        4. On failure, saves VS-related env vars, trims PATH to system essentials, retries
        5. After successful load, caller is responsible for prepending language runtime/tool paths
    .PARAMETER VsInstallPath
        Path to Visual Studio installation (from Find-VisualStudio).
    .PARAMETER Arch
        Target architecture (default amd64).
    .PARAMETER VerifyCommand
        Command name to verify exists after DevShell load (default "cl").
        Use "msbuild" for MSBuild-only scenarios.
    #>
    param(
        [string]$VsInstallPath,
        [string]$Arch = "amd64",
        [string]$VerifyCommand = "cl"
    )

    $systemRoot = $env:SystemRoot
    $devShellDll = [IO.Path]::Combine($VsInstallPath, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
    Import-Module $devShellDll

    function Try-LoadDevShell {
        param([string]$VsPath, [string]$TargetArch, [string]$VerifyCmd)
        $output = Enter-VsDevShell -VsInstallPath $VsPath -SkipAutomaticLocation -DevCmdArguments "-arch=$TargetArch -host_arch=$TargetArch" 2>&1
        foreach ($o in $output) {
            if ($o -is [System.Management.Automation.ErrorRecord]) {
                $msg = $o.ToString()
                if ($msg -match "输入行太长|input line is too long|command line|too long") {
                    throw "PATH_TOO_LONG"
                }
            }
        }
        $cmd = Get-Command $VerifyCmd -ErrorAction SilentlyContinue
        if (-not $cmd) {
            throw "COMMAND_NOT_FOUND_AFTER_DEVSHELL:$VerifyCmd"
        }
    }

    function Get-MinimalSystemPath {
        $parts = [System.Collections.Generic.List[string]]::new()
        $parts.Add([IO.Path]::Combine($systemRoot, "System32"))
        $parts.Add($systemRoot)
        $parts.Add([IO.Path]::Combine($systemRoot, "System32", "Wbem"))
        $parts.Add([IO.Path]::Combine($systemRoot, "System32", "WindowsPowerShell", "v1.0"))
        $pwshCmd = Get-Command pwsh -ErrorAction SilentlyContinue
        if ($pwshCmd -and $pwshCmd.Source) {
            $pwshDir = Split-Path $pwshCmd.Source -Parent
            if ($pwshDir) { $parts.Add($pwshDir) }
        }
        return ($parts | Select-Object -Unique) -join ";"
    }

    # Save env vars that DevShell modifies (for rollback on retry)
    $vsEnvVars = @("PATH", "LIB", "INCLUDE", "LIBPATH", "DevEnvDir", "VCINSTALLDIR", "VSINSTALLDIR")
    $savedEnv = @{}
    foreach ($ev in $vsEnvVars) {
        $savedEnv[$ev] = [Environment]::GetEnvironmentVariable($ev)
    }

    $fullPath = $env:PATH

    try {
        Try-LoadDevShell -VsPath $VsInstallPath -TargetArch $Arch -VerifyCmd $VerifyCommand
        Write-Host "  DevShell loaded with full PATH ($($fullPath.Length) chars)" -ForegroundColor Green
    } catch {
        Write-Host "  DevShell failed with full PATH ($($fullPath.Length) chars): $($_.Exception.Message)" -ForegroundColor DarkYellow
        Write-Host "  Restoring env and retrying with trimmed PATH..." -ForegroundColor DarkYellow
        foreach ($ev in $vsEnvVars) {
            if ($null -eq $savedEnv[$ev]) {
                [Environment]::SetEnvironmentVariable($ev, $null)
            } else {
                [Environment]::SetEnvironmentVariable($ev, $savedEnv[$ev])
            }
        }
        $env:PATH = Get-MinimalSystemPath
        try {
            Try-LoadDevShell -VsPath $VsInstallPath -TargetArch $Arch -VerifyCmd $VerifyCommand
            Write-Host "  DevShell loaded with trimmed PATH ($($env:PATH.Length) chars)" -ForegroundColor Green
        } catch {
            throw "Failed to load MSVC DevShell after PATH trim. $($_.Exception.Message)"
        }
    }
}

# ── Module Exports ───────────────────────────────────────────────────────

Export-ModuleMember -Function @(
    "Convert-VsVersionDirToNumber",
    "Get-VsEditionPriority",
    "Find-VisualStudio",
    "Enter-MsvcDevShell"
)
