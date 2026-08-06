﻿# ==============================================================================
# Line Ending Normalization Script (One-Click Fix) — PowerShell Edition
# ==============================================================================
# Fix CRLF/LF line endings across the main repo and all git submodules.
# Handles the root cause of Docker/Linux build failures caused by Windows CRLF
# in autotools scripts (configure, config.sub, *.ac, *.am, *.in, etc.).
#
# Usage:
#   .\.agents\scripts\normalize-eol.ps1                        # dry-run everything
#   .\.agents\scripts\normalize-eol.ps1 -Commit                # commit main repo only
#   .\.agents\scripts\normalize-eol.ps1 -FixSubmodules         # also patch submodules
#   .\.agents\scripts\normalize-eol.ps1 -FixSubmodules -Commit
#   .\.agents\scripts\normalize-eol.ps1 -FixSubmodules -IncludeVendor
#
# Parameters:
#   -Commit          Commit changes in the main repo (default: dry-run)
#   -FixSubmodules   Add missing autotools rules to submodule .gitattributes
#                    and run renormalize there too (default: report only)
#   -IncludeVendor   Also process vendor/ third-party submodules (default:
#                    only projects/ first-party submodules)
#   -NoRecursive     Only process direct submodules, skip nested submodules
#   -Help            Show this help
# ==============================================================================

#Requires -Version 5.1

[CmdletBinding()]
param(
    [switch]$Commit,
    [switch]$FixSubmodules,
    [switch]$IncludeVendor,
    [switch]$NoRecursive,
    [switch]$Help
)

# ── Encoding setup ──
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'

if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Detailed
    exit 0
}

# ── Locate repo root ──
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$AgentsDir = Split-Path -Parent $ScriptDir
$Root = Split-Path -Parent $AgentsDir
Set-Location $Root

# ── Determine mode ──
$DryRun = -not $Commit

# ── Idempotent autotools CRLF fix block ──
$MarkerStart = '# >>> normalize-eol autotools-crlf-fix >>>'
$MarkerEnd   = '# <<< normalize-eol autotools-crlf-fix <<<'
$AutotoolsBlock = @'
# >>> normalize-eol autotools-crlf-fix >>>
# Added by normalize-eol.ps1 — prevents CRLF in autotools/configure scripts
# from breaking Linux/macOS/container builds. Idempotent: safe to re-run.
configure     text eol=lf
config.sub    text eol=lf
config.guess  text eol=lf
install-sh    text eol=lf
ltmain.sh     text eol=lf
missing       text eol=lf
depcomp       text eol=lf
compile       text eol=lf
mkinstalldirs text eol=lf
*.sh          text eol=lf
*.bash        text eol=lf
*.ac          text eol=lf
*.am          text eol=lf
*.in          text eol=lf
*.cmake       text eol=lf
CMakeLists.txt text eol=lf
Makefile      text eol=lf
*.mk          text eol=lf
# Windows-native scripts must keep CRLF (overrides global eol=lf)
*.ps1         text eol=crlf
*.bat         text eol=crlf
*.cmd         text eol=crlf
# <<< normalize-eol autotools-crlf-fix <<<
'@

# ── Color helpers ──
function Write-Banner {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  Line Ending Normalization (One-Click)" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    $mode = if ($DryRun) { "DRY RUN" } else { "COMMIT" }
    $smMode = if ($FixSubmodules) { "fix" } else { "report only" }
    $vMode = if ($IncludeVendor) { "included" } else { "skipped" }
    Write-Host "Mode: $mode  |  Submodules: $smMode  |  Vendor: $vMode" -ForegroundColor Gray
    Write-Host "Root: $Root" -ForegroundColor Gray
    Write-Host ""
}

function Write-Step($msg)    { Write-Host "[Step] $msg" -ForegroundColor Yellow }
function Write-Phase($msg)   { Write-Host ""; Write-Host "[Phase] $msg" -ForegroundColor White }
function Write-Ok($msg)      { Write-Host "  OK  $msg" -ForegroundColor Green }
function Write-Err($msg)     { Write-Host "  ERROR: $msg" -ForegroundColor Red }
function Write-Warn($msg)    { Write-Host "  WARN  $msg" -ForegroundColor DarkYellow }
function Write-Info($msg)    { Write-Host "  $msg" -ForegroundColor Gray }

function Test-AutotoolsBlock($gaPath) {
    if (-not (Test-Path $gaPath)) { return $false }
    return (Select-String -Path $gaPath -Pattern ([regex]::Escape($MarkerStart)) -Quiet)
}

function Test-AutotoolsRule($gaPath) {
    if (-not (Test-Path $gaPath)) { return $false }
    # Check if "configure" has a text/eol rule
    return (Select-String -Path $gaPath -Pattern '^configure\s' -Quiet)
}

function Count-CrlfInGitObject($gitRef) {
    # Count CR characters in a git blob (HEAD:path or :path)
    try {
        $content = git show $gitRef 2>$null
        if (-not $content) { return 0 }
        $crCount = 0
        foreach ($line in $content) {
            foreach ($c in $line.ToCharArray()) {
                if ($c -eq "`r") { $crCount++ }
            }
        }
        return $crCount
    } catch {
        return 0
    }
}

function Normalize-Repo {
    param(
        [string]$RepoPath,
        [string]$RepoLabel,
        [switch]$IsMainRepo
    )

    $result = @{
        Path        = $RepoPath
        Label       = $RepoLabel
        StagedCount = 0
        CrlfToLf    = 0
        LfToCrlf    = 0
        Other       = 0
        Patched     = $false
        PatchedMsg  = ""
        Clean       = $false
    }

    Push-Location $RepoPath

    $gaFile = Join-Path $RepoPath ".gitattributes"
    $needPatch = $false

    if (-not (Test-Path $gaFile)) {
        $needPatch = $true
    } elseif (-not (Test-AutotoolsBlock $gaFile) -and -not (Test-AutotoolsRule $gaFile)) {
        $needPatch = $true
    }

    if ($needPatch -and $FixSubmodules) {
        if (-not (Test-Path $gaFile)) {
            Write-Host "    -> Creating .gitattributes with autotools rules" -ForegroundColor Yellow
            "* text=auto eol=lf`n" | Out-File -FilePath $gaFile -Encoding utf8NoBOM -NoNewline
            Add-Content -Path $gaFile -Value "`n$AutotoolsBlock" -Encoding utf8NoBOM
        } else {
            Write-Host "    -> Appending autotools-crlf-fix block to .gitattributes" -ForegroundColor Yellow
            Add-Content -Path $gaFile -Value "`n$AutotoolsBlock" -Encoding utf8NoBOM
        }
        git add .gitattributes 2>$null | Out-Null
        $result.Patched = $true
        $result.PatchedMsg = "patched .gitattributes"
    } elseif ($needPatch) {
        if (-not (Test-Path $gaFile)) {
            $result.PatchedMsg = "missing .gitattributes (use -FixSubmodules to create)"
        } else {
            $result.PatchedMsg = "missing autotools rules (use -FixSubmodules to add)"
        }
    }

    # Run renormalize
    git add --renormalize . 2>$null | Out-Null

    # Collect staged files
    $stagedFiles = @(git diff --cached --name-only 2>$null)
    $stagedFiles = @($stagedFiles | Where-Object { $_ -ne "" })
    $result.StagedCount = $stagedFiles.Count

    # Count CRLF/LF changes (only for small repos to avoid slowness)
    if ($result.StagedCount -gt 0 -and $result.StagedCount -le 200) {
        foreach ($f in $stagedFiles) {
            if (Test-Path $f -PathType Leaf) {
                $beforeCrlf = Count-CrlfInGitObject "HEAD:$f"
                $afterCrlf = Count-CrlfInGitObject ":$f"
                if ($beforeCrlf -gt 0 -and $afterCrlf -eq 0) {
                    $result.CrlfToLf++
                } elseif ($beforeCrlf -eq 0 -and $afterCrlf -gt 0) {
                    $result.LfToCrlf++
                } else {
                    $result.Other++
                }
            }
        }
    } elseif ($result.StagedCount -gt 200) {
        $result.Other = $result.StagedCount
    }

    Pop-Location

    if ($result.StagedCount -eq 0 -and [string]::IsNullOrEmpty($result.PatchedMsg)) {
        $result.Clean = $true
    }

    return $result
}

function Format-RepoResult($result, $indent = "") {
    $label = $result.Label
    if ($result.Clean) {
        Write-Host "$indent" -NoNewline
        Write-Host [char]0x2713 -ForegroundColor Green -NoNewline
        Write-Host " $label — clean" -ForegroundColor Green
        return
    }

    Write-Host "$indent" -NoNewline
    Write-Host [char]0x25CF -ForegroundColor Yellow -NoNewline
    Write-Host " $label"

    if (-not [string]::IsNullOrEmpty($result.PatchedMsg)) {
        if ($result.Patched) {
            Write-Host "$indent  " -NoNewline
            Write-Host [char]0x270E -ForegroundColor Green -NoNewline
            Write-Host " $($result.PatchedMsg)"
        } else {
            Write-Host "$indent  " -NoNewline
            Write-Host "!" -ForegroundColor Yellow -NoNewline
            Write-Host " $($result.PatchedMsg)" -ForegroundColor Yellow
        }
    }

    if ($result.StagedCount -gt 0) {
        Write-Host "$indent  " -NoNewline
        Write-Host "$($result.StagedCount) file(s) changed" -ForegroundColor White
        $details = @()
        if ($result.CrlfToLf -gt 0) { $details += "CRLF->LF:$($result.CrlfToLf)" }
        if ($result.LfToCrlf -gt 0) { $details += "LF->CRLF:$($result.LfToCrlf)" }
        if ($result.Other -gt 0) { $details += "other:$($result.Other)" }
        Write-Host "$indent  $($details -join ' ')" -ForegroundColor Gray
    }
}

# ==============================================================================
# PHASE 1: Banner & Main Repository
# ==============================================================================
Write-Banner

Write-Phase "Phase 1: Main Repository"
Write-Step "[1/3] Verifying git repository..."
$gitDir = git rev-parse --git-dir 2>$null
if (-not $gitDir) {
    Write-Err "Not a git repository"
    exit 1
}
$remote = git remote get-url origin 2>$null
if (-not $remote) { $remote = "local repo" }
Write-Ok "— $remote"
Write-Host ""

Write-Step "[2/3] Checking .gitattributes..."
$mainGa = Join-Path $Root ".gitattributes"
if (-not (Test-Path $mainGa)) {
    Write-Err ".gitattributes not found at repo root"
    Write-Warn "Create .gitattributes first before running this script"
    exit 1
}
$gaLines = (Get-Content $mainGa).Count
Write-Ok "— $gaLines lines"
Write-Host ""

Write-Step "[3/3] Running git add --renormalize . and collecting changes..."
$mainResult = Normalize-Repo -RepoPath $Root -RepoLabel "SpecWeave (main)" -IsMainRepo
Write-Ok "Done"
Write-Host ""

# ==============================================================================
# PHASE 2: Submodules
# ==============================================================================
Write-Phase "Phase 2: Submodules"

$allSubmodules = @()
$smStatusOutput = git submodule status --recursive 2>$null
foreach ($line in $smStatusOutput) {
    if ([string]::IsNullOrWhiteSpace($line)) { continue }
    # Skip uninitialized (starts with '-')
    if ($line.StartsWith('-')) { continue }
    # Extract path (second field)
    $parts = $line.TrimStart() -split '\s+'
    if ($parts.Count -lt 2) { continue }
    $smRelPath = $parts[1]

    # Filter top-level vendor/ unless -IncludeVendor
    if (-not $IncludeVendor -and $smRelPath.StartsWith("vendor/")) { continue }

    # If -NoRecursive, skip nested (more than one path separator)
    if ($NoRecursive) {
        $slashCount = ([char[]]$smRelPath | Where-Object { $_ -eq '/' }).Count
        if ($slashCount -gt 1) { continue }
    }

    $allSubmodules += (Join-Path $Root $smRelPath)
}

$smResults = @()
$smNeedsCommit = @()

if ($allSubmodules.Count -eq 0) {
    Write-Info "No submodules found."
} else {
    Write-Host "  Scanning $($allSubmodules.Count) submodule(s)..." -ForegroundColor Yellow
    Write-Host ""

    foreach ($smAbs in $allSubmodules) {
        $smRelPath = $smAbs.Substring($Root.Length + 1)

        # Classify
        $smType = "nested"
        if ($smRelPath.StartsWith("projects/")) { $smType = "first-party" }
        elseif ($smRelPath.StartsWith("vendor/")) { $smType = "third-party" }

        # Check if initialized
        $smGitPath = Join-Path $smAbs ".git"
        if (-not (Test-Path $smGitPath)) {
            Write-Host "  - $smRelPath — not initialized (skip)" -ForegroundColor Gray
            continue
        }

        Write-Host "  Working in: $smAbs" -ForegroundColor Gray
        $smResult = Normalize-Repo -RepoPath $smAbs -RepoLabel "$smRelPath ($smType)"
        $smResults += ,@($smRelPath, $smResult)

        if (-not $smResult.Clean) {
            $smNeedsCommit += $smRelPath
        }
    }
    Write-Host ""
}

# ==============================================================================
# PHASE 3: Summary & Commit
# ==============================================================================
Write-Phase "Phase 3: Summary"
Write-Host ""

Format-RepoResult $mainResult
Write-Host ""

if ($allSubmodules.Count -gt 0) {
    Write-Host "── Submodules ──" -ForegroundColor Gray
    foreach ($smEntry in $smResults) {
        $smRelPath = $smEntry[0]
        $smResult = $smEntry[1]
        $smAbs = Join-Path $Root $smRelPath

        # Skip uninitialized in display
        $smGitPath = Join-Path $smAbs ".git"
        if (-not (Test-Path $smGitPath)) {
            Write-Host "  - $smRelPath — not initialized" -ForegroundColor Gray
            continue
        }

        Format-RepoResult $smResult "  "
    }
    Write-Host ""
}

# ── Commit or dry-run message ──
if (-not $mainResult.Clean -and $Commit) {
    Write-Host "Committing main repo changes..." -ForegroundColor Yellow

    $commitMsg = @"
chore(git): normalize line endings across repo and submodules

Normalize line endings to conform to .gitattributes rules.
Key fixes:
- Autotools scripts (configure, config.sub, *.ac, *.am, *.in) -> LF
- Shell scripts, Python, C/C++, CMake, Makefiles -> LF
- PowerShell/Batch files -> CRLF
- Binary files marked as binary (no conversion)
- Submodule .gitattributes patched with autotools-crlf-fix block (where applicable)

Generated by: .agents/scripts/normalize-eol.ps1 -Commit
"@

    git commit -m $commitMsg
    $sha = git rev-parse --short HEAD
    Write-Ok "Committed as $sha"
    Write-Host ""
} elseif (-not $mainResult.Clean -and $DryRun) {
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "DRY RUN — no changes committed" -ForegroundColor DarkYellow
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To commit main repo changes:"
    Write-Host "  .\.agents\scripts\normalize-eol.ps1 -Commit" -ForegroundColor White
    Write-Host ""
    if ($smNeedsCommit.Count -gt 0) {
        Write-Host "Submodules with pending changes (need manual commit + push):" -ForegroundColor Yellow
        foreach ($sm in $smNeedsCommit) {
            Write-Host "  cd $sm; git add -A; git commit -m 'chore(git): fix CRLF line endings'; git push"
        }
        Write-Host ""
        if (-not $FixSubmodules) {
            Write-Host "To also patch submodule .gitattributes and renormalize:"
            Write-Host "  .\.agents\scripts\normalize-eol.ps1 -FixSubmodules" -ForegroundColor White
            Write-Host ""
        }
    }
    Write-Host "To undo ALL staging (main repo + submodules):" -ForegroundColor Gray
    Write-Host "  git submodule foreach --recursive 'git reset HEAD 2>`$null || true'"
    Write-Host "  git reset HEAD"
    Write-Host ""
    exit 0
}

# ── Final message ──
Write-Host "========================================" -ForegroundColor Cyan
if ($mainResult.Clean -and $smNeedsCommit.Count -eq 0) {
    Write-Host "All line endings are already correct — nothing to fix!" -ForegroundColor Green
} else {
    Write-Host "Main repo normalization complete." -ForegroundColor Green
    if ($smNeedsCommit.Count -gt 0) {
        Write-Host ""
        Write-Host "WARNING: Submodules with pending changes (need manual commit + push):" -ForegroundColor Yellow
        foreach ($sm in $smNeedsCommit) {
            Write-Host "  cd $sm" -ForegroundColor White
            Write-Host "  git add -A; git commit -m 'chore(git): fix CRLF line endings for autotools'; git push"
        }
        Write-Host ""
        Write-Host "After pushing submodules, return to main repo and update gitlinks:" -ForegroundColor Gray
        $smList = $smNeedsCommit -join ' '
        Write-Host "  git add $smList"
        Write-Host "  git commit -m 'chore(git): update submodules after CRLF normalization'"
    }
}
Write-Host "========================================" -ForegroundColor Cyan
