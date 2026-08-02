# NativeBuild.psm1 - Shared module for native C++ extension build scripts
# Provides auto-discovery of project directories and conda environments.
# VS discovery/DevShell loading delegated to VsDevShell.psm1 (re-exported for backward compat).
#
# Usage (dot-source):
#   Import-Module "$PSScriptRoot/../lib/NativeBuild.psm1"
#   $projectDir = Find-NativeProject -ProjectName "caffe-ffi"
#   $condaPrefix = Find-CondaEnvPython -MinVersion 3.14
#   $vsPath = Find-VisualStudio

Set-StrictMode -Version Latest

# Re-export generic utility functions from shared modules
Import-Module (Join-Path $PSScriptRoot "VsDevShell.psm1")
Import-Module (Join-Path $PSScriptRoot "PathPattern.psm1")

# ── Path Resolution Helpers (re-exported from PathPattern) ───────────────
# Resolve-PathPattern is imported from PathPattern.psm1

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
    .PARAMETER VerboseLog
        Write detailed discovery logs to host.
    #>
    param(
        [string]$Hint = "",
        [double]$MinVersion = 3.14,
        [string]$NamePattern = "",
        [switch]$VerboseLog
    )

    function Write-C { param([string]$Msg) if ($VerboseLog) { Write-Host "  [CONDA] $Msg" -ForegroundColor DarkGray } }

    Write-C "Find-CondaEnvPython start: Hint='$Hint' MinVersion=$MinVersion NamePattern='$NamePattern'"

    if ($Hint) {
        Write-C "Branch: explicit Hint provided, trying as direct path first"
        # Check as direct path
        $pyCandidates = [System.Collections.Generic.List[string]]::new()
        $pyCandidates.Add((Join-Path $Hint "python.exe"))
        $pyCandidates.Add([IO.Path]::Combine($Hint, "Scripts", "python.exe"))
        foreach ($pyPath in $pyCandidates) {
            Write-C "  Checking path candidate: $pyPath"
            if (Test-Path $pyPath) {
                $ver = Get-PythonVersion -PythonExe $pyPath
                Write-C "  Found python.exe, version=$ver"
                if ($ver -ge $MinVersion) {
                    Write-C "  Version OK, returning (Resolve-Path): $(Split-Path $pyPath)"
                    return (Resolve-Path (Split-Path $pyPath)).Path
                }
                Write-Warning "Conda env at $Hint has Python $ver, need >= $MinVersion"
            } else {
                Write-C "  Not found: $pyPath"
            }
        }
        # Check as env name across all conda roots
        Write-C "Branch: Hint not a direct path, searching as env name across conda roots"
        $roots = Get-CondaRoots
        Write-C "  Found $($roots.Count) conda root(s)"
        foreach ($cr in $roots) {
            Write-C "  Checking root: $cr"
            $envPath = [IO.Path]::Combine($cr, "envs", $Hint)
            $envPy = Join-Path $envPath "python.exe"
            Write-C "    Trying env: $envPy"
            if (Test-Path $envPy) {
                $ver = Get-PythonVersion -PythonExe $envPy
                Write-C "    Found python.exe, version=$ver"
                if ($ver -ge $MinVersion) {
                    Write-C "    Version OK, returning: $envPath"
                    return (Resolve-Path $envPath).Path
                }
            }
            if ($Hint -eq "base" -and (Test-Path (Join-Path $cr "python.exe"))) {
                $ver = Get-PythonVersion -PythonExe (Join-Path $cr "python.exe")
                Write-C "    Checking base env at $cr, version=$ver"
                if ($ver -ge $MinVersion) {
                    Write-C "    Base env version OK, returning: $cr"
                    return (Resolve-Path $cr).Path
                }
            }
        }
        throw "Conda environment '$Hint' not found or does not have Python $MinVersion+. Specify the full path."
    }

    # Currently activated conda env - only use if it matches name pattern (if specified) AND version
    if ($env:CONDA_PREFIX) {
        Write-C "Branch: CONDA_PREFIX is set: $env:CONDA_PREFIX"
        $curPy = Join-Path $env:CONDA_PREFIX "python.exe"
        if (Test-Path $curPy) {
            $ver = Get-PythonVersion -PythonExe $curPy
            $curName = Split-Path $env:CONDA_PREFIX -Leaf
            $nameMatches = -not $NamePattern -or $curName -match $NamePattern
            Write-C "  Active env name='$curName' version=$ver nameMatches=$nameMatches"
            if ($ver -ge $MinVersion -and $nameMatches) {
                Write-Host "  Using active conda env: $env:CONDA_PREFIX" -ForegroundColor Cyan
                return $env:CONDA_PREFIX
            }
            if ($ver -ge $MinVersion) {
                Write-Host "  Active conda env has Python $ver but name doesn't match pattern '$NamePattern', searching..." -ForegroundColor DarkYellow
            } else {
                Write-Host "  Active conda env has Python $ver (need >= $MinVersion), searching..." -ForegroundColor DarkYellow
            }
        } else {
            Write-C "  CONDA_PREFIX set but python.exe not found at $curPy"
        }
    } else {
        Write-C "Branch: no active CONDA_PREFIX, proceeding to full search"
    }

    # Search all conda roots
    Write-C "Branch: full search across all conda roots"
    $candidates = [System.Collections.Generic.List[object]]::new()
    $roots = Get-CondaRoots
    Write-C "  Found $($roots.Count) conda root(s) to scan"
    foreach ($cr in $roots) {
        Write-C "  Scanning root: $cr"
        # Check base env
        $basePy = Join-Path $cr "python.exe"
        if (Test-Path $basePy) {
            $ver = Get-PythonVersion -PythonExe $basePy
            $baseName = Split-Path $cr -Leaf
            $nameMatch = if ($NamePattern) { $baseName -match $NamePattern } else { $false }
            if ($ver -ge $MinVersion) {
                Write-C "    Base env: name='$baseName' version=$ver nameMatch=$nameMatch → ADD"
                $candidates.Add([pscustomobject]@{
                    Path = $cr
                    Name = $baseName
                    Version = $ver
                    IsNameMatch = $nameMatch
                })
            } else {
                Write-C "    Base env: version=$ver < $MinVersion → SKIP"
            }
        }
        $envsDir = Join-Path $cr "envs"
        if (Test-Path $envsDir) {
            $envDirs = Get-ChildItem $envsDir -Directory -ErrorAction SilentlyContinue
            Write-C "    envs/ dir: $($envDirs.Count) subdirectories"
            foreach ($envDir in $envDirs) {
                $pyPath = Join-Path $envDir.FullName "python.exe"
                if (Test-Path $pyPath) {
                    $ver = Get-PythonVersion -PythonExe $pyPath
                    $nameMatch = if ($NamePattern) { $envDir.Name -match $NamePattern } else { $false }
                    if ($ver -ge $MinVersion) {
                        Write-C "      env '$($envDir.Name)': version=$ver nameMatch=$nameMatch → ADD"
                        $candidates.Add([pscustomobject]@{
                            Path = $envDir.FullName
                            Name = $envDir.Name
                            Version = $ver
                            IsNameMatch = $nameMatch
                        })
                    } else {
                        Write-C "      env '$($envDir.Name)': version=$ver < $MinVersion → SKIP"
                    }
                }
            }
        } else {
            Write-C "    No envs/ subdirectory"
        }
    }

    Write-C "  Total candidates collected: $($candidates.Count)"
    if ($candidates.Count -eq 0) {
        throw "No conda environment with Python $MinVersion+ found. Activate one or use -CondaEnv to specify."
    }

    # Sort: name match first (DESC), then version (DESC) to prefer newest matching version
    $sorted = $candidates | Sort-Object -Property @{Expression={$_.IsNameMatch};Descending=$true}, @{Expression={$_.Version};Descending=$true}, Name
    if ($VerboseLog) {
        Write-C "  Sorted candidates (best first):"
        for ($i = 0; $i -lt $sorted.Count; $i++) {
            $c = $sorted[$i]
            $marker = if ($i -eq 0) { "→" } else { " " }
            $matchTag = if ($c.IsNameMatch) { " [NAME-MATCH]" } else { "" }
            Write-C "    $marker $($c.Name) v$($c.Version)$matchTag at $($c.Path)"
        }
    }
    $best = $sorted[0]
    $matchDesc = if ($best.IsNameMatch) { " (name match)" } else { "" }
    Write-Host "  Found Python $($best.Version)+ env: $($best.Name) ($($best.Path))$matchDesc" -ForegroundColor Cyan
    return $best.Path
}

# ── Module Exports ───────────────────────────────────────────────────────
# VS functions (Find-VisualStudio, Enter-MsvcDevShell, Convert-VsVersionDirToNumber, Get-VsEditionPriority)
# are re-exported from VsDevShell.psm1

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
