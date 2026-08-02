# NativeBuild.psm1 - Shared module for native C++ extension build scripts
# Provides auto-discovery of project directories, conda environments, and Visual Studio installations.
#
# Usage (dot-source):
#   Import-Module "$PSScriptRoot/../lib/NativeBuild.psm1"
#   $projectDir = Find-NativeProject -ProjectName "caffe-ffi"
#   $condaPrefix = Find-CondaEnvPython -MinVersion 3.14
#   $vsPath = Find-VisualStudio

Set-StrictMode -Version Latest

# ── Path Resolution Helpers ──────────────────────────────────────────────

function Resolve-PathPattern {
    <#
    .SYNOPSIS
        Resolves a relative path pattern (with * wildcards) against a base directory.
    .DESCRIPTION
        Walks segment by segment; '*' matches any single directory level.
    #>
    param(
        [string]$BaseDir,
        [string[]]$Segments
    )
    $current = @($BaseDir)
    foreach ($seg in $Segments) {
        $next = [System.Collections.Generic.List[string]]::new()
        foreach ($dir in $current) {
            if ($seg -eq "*") {
                foreach ($d in (Get-ChildItem -Path $dir -Directory -ErrorAction SilentlyContinue)) {
                    $next.Add($d.FullName)
                }
            } else {
                $candidate = Join-Path $dir $seg
                if (Test-Path $candidate -PathType Container) {
                    $next.Add($candidate)
                }
            }
        }
        $current = $next.ToArray()
        if ($current.Count -eq 0) { return @() }
    }
    return $current
}

function Test-NativeProject {
    <#
    .SYNOPSIS
        Tests whether a directory contains a scikit-build-core based native extension project.
    .PARAMETER Dir
        Directory to check.
    .PARAMETER ProjectName
        If specified, requires pyproject.toml to contain `name = "<ProjectName>"`.
        If "*", accepts any project name.
    #>
    param(
        [string]$Dir,
        [string]$ProjectName = "*"
    )
    $toml = Join-Path $Dir "pyproject.toml"
    if (-not (Test-Path $toml)) { return $false }

    # Must use scikit-build-core or setuptools with CMake
    $content = Get-Content $toml -Raw -ErrorAction SilentlyContinue
    if (-not $content) { return $false }
    if ($content -notmatch 'scikit-build|cmake') { return $false }

    if ($ProjectName -and $ProjectName -ne "*") {
        if ($content -notmatch ('name\s*=\s*"' + [regex]::Escape($ProjectName) + '"')) {
            return $false
        }
    }
    return $true
}

# ── Project Directory Discovery ──────────────────────────────────────────

function Find-NativeProject {
    <#
    .SYNOPSIS
        Finds a native extension project directory by auto-discovery or explicit hint.
    .PARAMETER Hint
        Explicit path to try first.
    .PARAMETER ProjectName
        Project name to match in pyproject.toml. "*" matches any native project.
    .PARAMETER ScriptDir
        Directory of the calling script (for upward search). Auto-detected if not provided.
    #>
    param(
        [string]$Hint = "",
        [string]$ProjectName = "*",
        [string]$ScriptDir = ""
    )

    if ($Hint -and (Test-NativeProject -Dir $Hint -ProjectName $ProjectName)) {
        return (Resolve-Path $Hint).Path
    }

    # Collect search roots: walk up from script location + current directory
    if (-not $ScriptDir) { $ScriptDir = $PSScriptRoot }
    $searchRoots = [System.Collections.Generic.List[string]]::new()
    if ($ScriptDir) {
        $dir = $ScriptDir
        for ($i = 0; $i -lt 10; $i++) {
            $searchRoots.Add($dir)
            if (Test-Path (Join-Path $dir "AGENTS.md")) { break }
            $parent = Split-Path $dir -Parent
            if (-not $parent -or $parent -eq $dir) { break }
            $dir = $parent
        }
    }
    $searchRoots.Add((Get-Location).Path)

    # Search patterns (segment arrays, * = wildcard for any single directory level)
    $patterns = [System.Collections.Generic.List[string[]]]::new()
    $patterns.Add(@())                                                           # root itself
    $patterns.Add(@("libs", "*"))                                                # <root>/libs/*
    $patterns.Add(@("apps", "*"))                                                # <root>/apps/*
    $patterns.Add(@("projects", "*", "libs", "*"))                               # <root>/projects/*/libs/*
    $patterns.Add(@("projects", "*", "*", "libs", "*"))                          # <root>/projects/*/*/libs/*
    $patterns.Add(@("projects", "*"))                                            # <root>/projects/*
    $patterns.Add(@("external", "*"))                                            # <root>/external/*
    $patterns.Add(@("external", "*", "libs", "*"))                               # <root>/external/*/libs/*

    # If a specific project name is given, also try direct name match
    if ($ProjectName -and $ProjectName -ne "*") {
        $patterns.Insert(0, @($ProjectName))                                     # <root>/<ProjectName>
        $patterns.Insert(1, @("libs", $ProjectName))                             # <root>/libs/<ProjectName>
        $patterns.Insert(2, @("apps", $ProjectName))                             # <root>/apps/<ProjectName>
    }

    foreach ($root in $searchRoots) {
        foreach ($pattern in $patterns) {
            if ($pattern.Count -eq 0) {
                if (Test-NativeProject -Dir $root -ProjectName $ProjectName) { return $root }
                continue
            }
            $matched = Resolve-PathPattern -BaseDir $root -Segments $pattern
            foreach ($m in $matched) {
                if (Test-NativeProject -Dir $m -ProjectName $ProjectName) { return $m }
            }
        }
    }

    $nameDesc = if ($ProjectName -and $ProjectName -ne "*") { " '$ProjectName'" } else { "" }
    throw "Cannot find native extension project${nameDesc}. Use -ProjectDir to specify it explicitly."
}

# ── Python Version Helpers ───────────────────────────────────────────────

function Get-PythonVersion {
    <# .SYNOPSIS Gets Python version as double (e.g. 3.14). Returns 0 if exe not found. #>
    param([string]$PythonExe)
    if (-not $PythonExe -or -not (Test-Path $PythonExe)) { return 0.0 }
    try {
        $verStr = & $PythonExe --version 2>&1
        if ($verStr -match "(\d+)\.(\d+)") {
            return [double]"$($Matches[1]).$($Matches[2])"
        }
    } catch { }
    return 0.0
}

# ── Conda Environment Discovery ──────────────────────────────────────────

function Get-CondaRootFromEnv {
    <# .SYNOPSIS Walks up from an env path to find the conda root. #>
    param([string]$EnvPath)
    if ((Test-Path (Join-Path $EnvPath "python.exe")) -and (Test-Path (Join-Path $EnvPath "conda-meta"))) {
        return $EnvPath
    }
    $parent = Split-Path $EnvPath -Parent
    if ($parent) {
        $grandparent = Split-Path $parent -Parent
        if ($grandparent -and (Test-Path (Join-Path $grandparent "conda-meta"))) {
            return $grandparent
        }
        if ((Test-Path (Join-Path $parent "conda-meta")) -and (Test-Path (Join-Path $parent "python.exe"))) {
            return $parent
        }
    }
    return $null
}

function Get-CondaRoots {
    <#
    .SYNOPSIS
        Discovers all conda/mamba/miniforge installation roots without hardcoded paths.
    .DESCRIPTION
        Searches in order:
        1. Environment variable directories (USERPROFILE, LOCALAPPDATA, etc.)
        2. All fixed drives (top-level and Users\<username>-level installations)
        3. PATH (where.exe conda)
        4. CONDA_PREFIX env var (currently activated env)
        5. ~/.conda/environments.txt
    #>
    $roots = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    $distNames = @("anaconda3", "miniconda3", "miniforge3", "mambaforge", "miniconda", "anaconda")

    # 1. Environment variables
    $baseDirs = [System.Collections.Generic.List[string]]::new()
    foreach ($ev in @("USERPROFILE", "LOCALAPPDATA", "APPDATA", "ProgramData", "ProgramFiles", "ProgramFiles(x86)")) {
        $v = [Environment]::GetEnvironmentVariable($ev)
        if ($v) { $baseDirs.Add($v) }
    }
    if ($env:HOMEDRIVE -and $env:HOMEPATH) {
        $baseDirs.Add($env:HOMEDRIVE + $env:HOMEPATH)
    }
    foreach ($base in $baseDirs) {
        foreach ($name in $distNames) {
            $candidate = Join-Path $base $name
            if (Test-Path $candidate) { [void]$roots.Add($candidate) }
        }
    }

    # 2. All fixed drives
    $drives = [System.IO.DriveInfo]::GetDrives() | Where-Object {
        $_.DriveType -eq [System.IO.DriveType]::Fixed -and $_.IsReady
    }
    $username = $env:USERNAME
    foreach ($drive in $drives) {
        $driveRoot = $drive.RootDirectory.FullName
        foreach ($name in $distNames) {
            $candidate = Join-Path $driveRoot $name
            if (Test-Path $candidate) { [void]$roots.Add($candidate) }
        }
        if ($username) {
            $usersDir = Join-Path $driveRoot "Users"
            if (Test-Path $usersDir) {
                $userHome = Join-Path $usersDir $username
                if (Test-Path $userHome) {
                    foreach ($name in $distNames) {
                        $candidate = Join-Path $userHome $name
                        if (Test-Path $candidate) { [void]$roots.Add($candidate) }
                    }
                }
            }
        }
    }

    # 3. where.exe conda
    $whereConda = & where.exe conda 2>$null
    foreach ($cPath in $whereConda) {
        if (-not $cPath) { continue }
        $cPath = $cPath.Trim()
        if (-not (Test-Path $cPath)) { continue }
        $condaDir = Split-Path $cPath -Parent
        $candidate = Split-Path $condaDir -Parent
        if ($candidate -and (Test-Path (Join-Path $candidate "conda-meta"))) {
            [void]$roots.Add($candidate)
        } elseif ((Test-Path (Join-Path $condaDir "conda-meta"))) {
            [void]$roots.Add($condaDir)
        }
    }

    # 4. CONDA_PREFIX
    if ($env:CONDA_PREFIX) {
        $rootFromPrefix = Get-CondaRootFromEnv -EnvPath $env:CONDA_PREFIX
        if ($rootFromPrefix) { [void]$roots.Add($rootFromPrefix) }
    }

    # 5. ~/.conda/environments.txt
    if ($env:USERPROFILE) {
        $envTxt = Join-Path $env:USERPROFILE ".conda" "environments.txt"
        if (Test-Path $envTxt) {
            foreach ($line in (Get-Content $envTxt -ErrorAction SilentlyContinue)) {
                $line = $line.Trim()
                if (-not $line -or $line.StartsWith("#")) { continue }
                if (Test-Path $line) {
                    $rootFromTxt = Get-CondaRootFromEnv -EnvPath $line
                    if ($rootFromTxt) { [void]$roots.Add($rootFromTxt) }
                }
            }
        }
    }

    return @($roots)
}

function Find-CondaEnvPython {
    <#
    .SYNOPSIS
        Finds a conda environment with Python >= MinVersion.
    .PARAMETER Hint
        Environment name (e.g. "py314") or direct path.
    .PARAMETER MinVersion
        Minimum Python version as double (default 3.14).
    .PARAMETER NamePattern
        Regex pattern to prefer environment names matching this (e.g. "314|py314").
    #>
    param(
        [string]$Hint = "",
        [double]$MinVersion = 3.14,
        [string]$NamePattern = ""
    )

    if ($Hint) {
        # Check as direct path
        $pyCandidates = [System.Collections.Generic.List[string]]::new()
        $pyCandidates.Add((Join-Path $Hint "python.exe"))
        $pyCandidates.Add([IO.Path]::Combine($Hint, "Scripts", "python.exe"))
        foreach ($pyPath in $pyCandidates) {
            if (Test-Path $pyPath) {
                $ver = Get-PythonVersion -PythonExe $pyPath
                if ($ver -ge $MinVersion) {
                    return (Resolve-Path (Split-Path $pyPath)).Path
                }
                Write-Warning "Conda env at $Hint has Python $ver, need >= $MinVersion"
            }
        }
        # Check as env name across all conda roots
        foreach ($cr in (Get-CondaRoots)) {
            $envPath = [IO.Path]::Combine($cr, "envs", $Hint)
            if (Test-Path (Join-Path $envPath "python.exe")) {
                $ver = Get-PythonVersion -PythonExe (Join-Path $envPath "python.exe")
                if ($ver -ge $MinVersion) {
                    return (Resolve-Path $envPath).Path
                }
            }
            if ($Hint -eq "base" -and (Test-Path (Join-Path $cr "python.exe"))) {
                $ver = Get-PythonVersion -PythonExe (Join-Path $cr "python.exe")
                if ($ver -ge $MinVersion) {
                    return (Resolve-Path $cr).Path
                }
            }
        }
        throw "Conda environment '$Hint' not found or does not have Python $MinVersion+. Specify the full path."
    }

    # Currently activated conda env
    if ($env:CONDA_PREFIX) {
        $curPy = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path $curPy) {
            $ver = Get-PythonVersion -PythonExe $curPy
            if ($ver -ge $MinVersion) {
                Write-Host "  Using active conda env: $env:CONDA_PREFIX"
                return $env:CONDA_PREFIX
            }
            Write-Host "  Active conda env has Python $ver (need >= $MinVersion), searching..."
        }
    }

    # Search all conda roots
    $candidates = [System.Collections.Generic.List[string]]::new()
    foreach ($cr in (Get-CondaRoots)) {
        if (Test-Path (Join-Path $cr "python.exe")) {
            $candidates.Add($cr)
        }
        $envsDir = Join-Path $cr "envs"
        if (Test-Path $envsDir) {
            foreach ($envDir in (Get-ChildItem $envsDir -Directory -ErrorAction SilentlyContinue)) {
                if (Test-Path (Join-Path $envDir.FullName "python.exe")) {
                    $candidates.Add($envDir.FullName)
                }
            }
        }
    }

    $fallback = $null
    foreach ($cand in $candidates) {
        $ver = Get-PythonVersion -PythonExe (Join-Path $cand "python.exe")
        if ($ver -ge $MinVersion) {
            $name = Split-Path $cand -Leaf
            if ($NamePattern -and $name -match $NamePattern) {
                Write-Host "  Found Python $MinVersion+ env: $name ($cand)"
                return $cand
            }
            if (-not $fallback) { $fallback = $cand }
        }
    }
    if ($fallback) {
        $name = Split-Path $fallback -Leaf
        Write-Host "  Found Python $MinVersion+ env: $name ($fallback)"
        return $fallback
    }

    throw "No conda environment with Python $MinVersion+ found. Activate one or use -CondaEnv to specify."
}

# ── Visual Studio Discovery ──────────────────────────────────────────────

function Convert-VsVersionDirToNumber {
    <# .SYNOPSIS Converts a VS version directory name to a comparable numeric version. #>
    param([string]$VersionDirName)
    # Year-based directories (e.g. "2022") map to internal VS major versions
    $yearMap = @{ "2022" = 17; "2019" = 16; "2017" = 15; "2015" = 14; "2013" = 12 }
    if ($yearMap.ContainsKey($VersionDirName)) { return $yearMap[$VersionDirName] }
    # Numeric directories (e.g. "18" for VS 18 / 2026 Insiders) used directly
    if ($VersionDirName -match '^(\d+)$') { return [int]$Matches[1] }
    return 0
}

function Get-VsEditionPriority {
    <# .SYNOPSIS Returns a priority score for a VS edition name (higher = preferred). #>
    param([string]$EditionName)
    $en = $EditionName.ToLower()
    if ($en -match 'insiders|canary') { return 4 }      # Bleeding edge
    if ($en -match 'preview') { return 3 }              # Preview channel
    if ($en -match 'enterprise') { return 2 }           # Enterprise (most features)
    if ($en -match 'professional') { return 1 }         # Professional
    if ($en -match 'community|buildtools') { return 0 } # Community/Build Tools
    return -1
}

function Find-VisualStudio {
    <#
    .SYNOPSIS
        Finds Visual Studio installation with C++ tools, preferring the newest version
        and Insiders/Preview editions.
    .DESCRIPTION
        Multi-strategy discovery:
        1. vswhere.exe (official method) - requires VC.Tools.x86.x64 component
        2. Directory scan of Program Files (handles Insiders/Preview editions not registered with vswhere)
        3. Environment variables (VSINSTALLDIR, VCToolsInstallDir)

        All valid candidates (those with DevShell.dll) are collected across strategies,
        then sorted by: version number (descending) → edition priority (descending).
        This ensures VS 2026 Insiders (v18) is selected over VS 2022 (v17) even when both exist.
    .PARAMETER Hint
        Explicit VS installation path to use.
    .PARAMETER VerboseLog
        Write detailed discovery logs to host.
    #>
    param(
        [string]$Hint = "",
        [switch]$VerboseLog
    )

    function Write-D { param([string]$Msg) if ($VerboseLog) { Write-Host "  [VS] $Msg" } }

    if ($Hint) {
        $devShell = [IO.Path]::Combine($Hint, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
        if (Test-Path $devShell) {
            Write-D "Using explicit Hint: $Hint"
            return (Resolve-Path $Hint).Path
        }
        throw "DevShell.dll not found in '$Hint'. Is this a valid VS installation?"
    }

    # Collect all valid candidates across strategies
    $candidates = [System.Collections.Generic.List[object]]::new()
    $seen = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)

    function Add-Candidate {
        param([string]$Path, [string]$Source, [string]$VersionDir = "", [string]$EditionName = "")
        $devShell = [IO.Path]::Combine($Path, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
        if (-not (Test-Path $devShell)) { return }
        $fullPath = (Resolve-Path $Path).Path
        if ($seen.Add($fullPath)) {
            # Extract version/edition from path if not provided
            if (-not $VersionDir -or -not $EditionName) {
                $rel = $fullPath -replace [regex]::Escape("Microsoft Visual Studio\"), ""
                $parts = $rel.Split([char]'\', [char]'/')
                if (-not $VersionDir -and $parts.Count -ge 1) { $VersionDir = $parts[0] }
                if (-not $EditionName -and $parts.Count -ge 2) { $EditionName = $parts[1] }
            }
            $verNum = Convert-VsVersionDirToNumber -VersionDirName $VersionDir
            $edPriority = Get-VsEditionPriority -EditionName $EditionName
            $candidates.Add([pscustomobject]@{
                Path = $fullPath; Source = $Source; VersionDir = $VersionDir
                Edition = $EditionName; VersionNum = $verNum; EdPriority = $edPriority
            }) | Out-Null
        }
    }

    # Strategy 1: vswhere.exe
    Write-D "Strategy 1: vswhere.exe"
    foreach ($pfName in @("ProgramFiles(x86)", "ProgramFiles")) {
        $pf = [Environment]::GetEnvironmentVariable($pfName)
        if (-not $pf) { continue }
        $vw = [IO.Path]::Combine($pf, "Microsoft Visual Studio", "Installer", "vswhere.exe")
        if (-not (Test-Path $vw)) { Write-D "  vswhere not found at $vw"; continue }
        Write-D "  vswhere at $vw"
        foreach ($req in @("Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "")) {
            $vwArgs = @("-latest", "-products", "*", "-property", "installationPath")
            if ($req) { $vwArgs = @("-latest", "-products", "*", "-requires", $req, "-property", "installationPath") }
            $vsPath = & $vw @vwArgs 2>$null | Select-Object -First 1
            if ($vsPath) {
                $trimmed = $vsPath.Trim()
                if ($trimmed) { Add-Candidate -Path $trimmed -Source "vswhere" }
            }
        }
    }

    # Strategy 2: Directory scan
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
            # Version dir itself might be an edition (e.g. "18/Insiders")
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
        throw "No Visual Studio installation with DevShell found. Use -VsPath to specify it explicitly."
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

# ── MSVC DevShell Loading ────────────────────────────────────────────────

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
        2. Captures stderr to detect the "input line too long" error (Chinese + English)
        3. Verifies cl.exe is actually available after loading
        4. On failure, saves all VS-related env vars, trims PATH to system essentials, retries
        5. After successful load, conda paths are prepended by the caller
    .PARAMETER VsInstallPath
        Path to Visual Studio installation.
    .PARAMETER Arch
        Target architecture (default amd64).
    #>
    param(
        [string]$VsInstallPath,
        [string]$Arch = "amd64"
    )

    $systemRoot = $env:SystemRoot
    $devShellDll = [IO.Path]::Combine($VsInstallPath, "Common7", "Tools", "Microsoft.VisualStudio.DevShell.dll")
    Import-Module $devShellDll

    # Internal helper: attempt DevShell load and verify cl.exe exists
    function Try-LoadDevShell {
        param([string]$VsPath, [string]$TargetArch)
        $output = Enter-VsDevShell -VsInstallPath $VsPath -SkipAutomaticLocation -DevCmdArguments "-arch=$TargetArch -host_arch=$TargetArch" 2>&1
        foreach ($o in $output) {
            if ($o -is [System.Management.Automation.ErrorRecord]) {
                $msg = $o.ToString()
                if ($msg -match "输入行太长|input line is too long|command line|too long") {
                    throw "PATH_TOO_LONG"
                }
            }
        }
        $clCmd = Get-Command cl -ErrorAction SilentlyContinue
        if (-not $clCmd) {
            throw "CL_NOT_FOUND_AFTER_DEVSHELL"
        }
    }

    # Build minimal system PATH (cmd.exe + PowerShell + core system tools)
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
        Try-LoadDevShell -VsPath $VsInstallPath -TargetArch $Arch
        Write-Host "  DevShell loaded with full PATH ($($fullPath.Length) chars)"
    } catch {
        Write-Host "  DevShell failed with full PATH ($($fullPath.Length) chars): $($_.Exception.Message)"
        Write-Host "  Restoring env and retrying with trimmed PATH..."
        # Rollback env vars to pre-DevShell state
        foreach ($ev in $vsEnvVars) {
            if ($null -eq $savedEnv[$ev]) {
                [Environment]::SetEnvironmentVariable($ev, $null)
            } else {
                [Environment]::SetEnvironmentVariable($ev, $savedEnv[$ev])
            }
        }
        $env:PATH = Get-MinimalSystemPath
        try {
            Try-LoadDevShell -VsPath $VsInstallPath -TargetArch $Arch
            Write-Host "  DevShell loaded with trimmed PATH ($($env:PATH.Length) chars)"
        } catch {
            throw "Failed to load MSVC DevShell after PATH trim. $($_.Exception.Message)"
        }
    }
}

Export-ModuleMember -Function @(
    "Resolve-PathPattern",
    "Test-NativeProject",
    "Find-NativeProject",
    "Get-PythonVersion",
    "Get-CondaRootFromEnv",
    "Get-CondaRoots",
    "Find-CondaEnvPython",
    "Find-VisualStudio",
    "Enter-MsvcDevShell",
    "Convert-VsVersionDirToNumber",
    "Get-VsEditionPriority"
)
