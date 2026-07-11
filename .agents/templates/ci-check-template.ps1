# CI/CD Pipeline Check Script (Windows PowerShell Template)
# Usage: powershell -ExecutionPolicy Bypass -File .agents/scripts/ci-check-template.ps1
#
# CUSTOMIZATION NOTES:
# 1. Adjust $root path calculation to match your project structure
# 2. Comment out gates that don't apply to your project
# 3. Update $totalSteps count when adding/removing gates
# 4. Adjust thresholds (e.g., --threshold 60 for hardcode check)
# 5. Add project-specific checks following the same pattern

$ErrorActionPreference = "Stop"

# ==============================================================================
# Encoding Safety: Force UTF-8 output, compatible with PowerShell 5 and 7
# ==============================================================================
cmd /c chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
if ($PSVersionTable.PSVersion.Major -ge 7) {
    $PSDefaultParameterValues['*:Encoding'] = 'utf8'
}

# ==============================================================================
# Path Configuration (CUSTOMIZE THIS FOR YOUR PROJECT)
# ==============================================================================
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$agentsDir = Split-Path -Parent $scriptDir
$root = Split-Path -Parent $agentsDir
# If your .agents directory is at a different level, adjust the above lines.
# Example for projects where scripts live in scripts/ directly (no .agents dir):
# $root = Split-Path -Parent $scriptDir

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CI/CD Pipeline Check (Template)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "PowerShell version: $($PSVersionTable.PSVersion)" -ForegroundColor Gray
Write-Host "Console encoding: $([Console]::OutputEncoding.WebName)" -ForegroundColor Gray
Write-Host "Project root: $root" -ForegroundColor Gray
Write-Host ""

# ==============================================================================
# Total Steps Count (UPDATE WHEN ADDING/REMOVING GATES)
# ==============================================================================
$totalSteps = 8

# ==============================================================================
# Gate 1/8: Repo Compliance Checks 🔴 FAIL
# Covers: gitignore rules, vendor directory, Mermaid syntax, filename conventions, roles
# ==============================================================================
Write-Host "[1/$totalSteps] Repo compliance checks (gitignore+vendor+mermaid+filename+roles)..." -ForegroundColor Yellow
# CUSTOMIZE: Replace with your compliance check script, or remove if not needed
python "$root\.agents\scripts\repo-check.py" all
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: repo compliance check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# Gate 2/8: Link Validity Check 🔴 FAIL
# Verifies all local Markdown links point to existing files
# ==============================================================================
Write-Host "[2/$totalSteps] Check links..." -ForegroundColor Yellow
# CUSTOMIZE: Add --path <dir> to check specific directory only
# CUSTOMIZE: Add --check-external to also verify external URLs
python "$root\.agents\scripts\check-links.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: link check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# Gate 3/8: Spec Consistency Check 🟡 WARN (non-blocking)
# Verifies spec.md / tasks.md / checklist.md are consistent
# ==============================================================================
Write-Host "[3/$totalSteps] Check spec consistency..." -ForegroundColor Yellow
# CUSTOMIZE: Replace with your spec validation script, or remove if not using SpecWeave
python "$root\.agents\scripts\spec-tool.py" check
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: spec consistency check has warnings (non-blocking)" -ForegroundColor Yellow
}
Write-Host ""

# ==============================================================================
# Gate 4/8: Pattern Maturity Check 🔴 FAIL
# Ensures reusable patterns meet minimum quality standards
# ==============================================================================
Write-Host "[4/$totalSteps] Check pattern maturity..." -ForegroundColor Yellow
# CUSTOMIZE: Remove if your project doesn't use pattern-based knowledge management
python "$root\.agents\scripts\pattern-maturity.py" check
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: pattern maturity check failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# Gate 5/8: Documentation Auto-Generation 🔴 FAIL
# Generates nav tables, dashboards, app indexes (WRITE OPERATION - idempotent)
# ==============================================================================
Write-Host "[5/$totalSteps] Generate docs (nav+dashboard+apps)..." -ForegroundColor Yellow
# CUSTOMIZE: Replace with your doc generation script, or remove if not needed
# NOTE: This step MODIFIES FILES in marked regions only (safe, idempotent)
python "$root\.agents\scripts\docgen.py" all
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: doc generation failed" -ForegroundColor Red
    exit 1
}
Write-Host "  PASS" -ForegroundColor Green
Write-Host ""

# ==============================================================================
# Gate 6/8: Cross-File Duplication Detection 🟡 WARN (non-blocking)
# Detects code duplication across scripts to encourage shared library extraction
# ==============================================================================
Write-Host "[6/$totalSteps] Check script duplication..." -ForegroundColor Yellow
# CUSTOMIZE: Add --path <dir> to check specific directory, or remove if not needed
python "$root\.agents\scripts\check-duplication.py"
if ($LASTEXITCODE -ne 0) {
    Write-Host "WARN: cross-file duplication detected, consider extracting to shared lib/" -ForegroundColor Yellow
}
else {
    Write-Host "  PASS" -ForegroundColor Green
}
Write-Host ""

# ==============================================================================
# Gate 7/8: Stage Guardrail Log Compliance 🔴 FAIL
# Checks stage guardrail logs for violations (strict mode, zero tolerance)
# ==============================================================================
Write-Host "[7/$totalSteps] Check stage guardrail logs..." -ForegroundColor Yellow
$sgLogFile = $env:STAGE_GUARDRAIL_LOG
if (-not $sgLogFile) {
    # Auto-detect latest log file if not specified via env var
    $logsDir = Join-Path $root ".agents\logs"
    if (Test-Path $logsDir) {
        $latestLog = Get-ChildItem -Path $logsDir -Filter "*.log" | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($latestLog) {
            $sgLogFile = $latestLog.FullName
        }
    }
}
if ($sgLogFile -and (Test-Path $sgLogFile)) {
    # CUSTOMIZE: Remove --strict for lenient mode, or remove entire gate if not needed
    python "$root\.agents\scripts\check-stage-guardrails.py" --log-file $sgLogFile --strict
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: stage guardrail log violations found (strict mode)" -ForegroundColor Red
        exit 1
    }
    Write-Host "  PASS" -ForegroundColor Green
}
else {
    Write-Host "  SKIP (no log file found, set STAGE_GUARDRAIL_LOG env var)" -ForegroundColor DarkGray
}
Write-Host ""

# ==============================================================================
# Gate 8/8: Stage Guardrail Dashboard Generation 🟡 WARN (non-blocking)
# Generates visual HTML dashboard of guardrail compliance
# ==============================================================================
Write-Host "[8/$totalSteps] Generate stage guardrail dashboard..." -ForegroundColor Yellow
$logsDir = Join-Path $root ".agents\logs"
if (Test-Path $logsDir) {
    $logFiles = Get-ChildItem -Path $logsDir -Filter "*.log" -ErrorAction SilentlyContinue
    if ($logFiles -and $logFiles.Count -gt 0) {
        python "$root\.agents\scripts\generate-sg-dashboard.py"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "WARN: SG dashboard generation failed (non-blocking)" -ForegroundColor Yellow
        }
        else {
            Write-Host "  PASS (dashboard: .agents/reports/sg-dashboard.html)" -ForegroundColor Green
        }
    }
    else {
        Write-Host "  SKIP (no log files in .agents/logs/)" -ForegroundColor DarkGray
    }
}
else {
    Write-Host "  SKIP (logs directory does not exist)" -ForegroundColor DarkGray
}
Write-Host ""

# ==============================================================================
# OPTIONAL EXTENSION GATES (uncomment to enable)
# ==============================================================================

# --- Extension A: RACI Compliance Check ---
# $totalSteps++  # Remember to increment total steps!
# Write-Host "[9/$totalSteps] Check RACI compliance..." -ForegroundColor Yellow
# python "$root\.agents\scripts\check-raci-compliance.py" --path "$root\.agents\rules"
# python "$root\.agents\scripts\check-raci-compliance.py" --path "$root\.agents\commands"
# if ($LASTEXITCODE -ne 0) { exit 1 }
# Write-Host "  PASS" -ForegroundColor Green
# Write-Host ""

# --- Extension B: Hardcoded Values Detection ---
# $totalSteps++
# Write-Host "[10/$totalSteps] Check hardcoded values..." -ForegroundColor Yellow
# python "$root\.agents\scripts\check-hardcode.py" --path "$root\.agents\scripts" --threshold 60
# if ($LASTEXITCODE -ne 0) { exit 1 }
# Write-Host "  PASS" -ForegroundColor Green
# Write-Host ""

# --- Extension C: File Size Thresholds ---
# $totalSteps++
# Write-Host "[11/$totalSteps] Check file size thresholds..." -ForegroundColor Yellow
# python "$root\.agents\scripts\check-file-size.py" --warn-only
# Write-Host ""

# --- Extension D: Directory README Existence ---
# $totalSteps++
# Write-Host "[12/$totalSteps] Check directory README existence..." -ForegroundColor Yellow
# python "$root\.agents\scripts\generate-readme.py" --check
# if ($LASTEXITCODE -ne 0) { exit 1 }
# Write-Host "  PASS" -ForegroundColor Green
# Write-Host ""

# --- Extension E: Skill Quality Scoring ---
# $totalSteps++
# Write-Host "[13/$totalSteps] Check Skill quality..." -ForegroundColor Yellow
# python "$root\.agents\scripts\check-skill-quality.py" --threshold 70
# if ($LASTEXITCODE -ne 0) { exit 1 }
# Write-Host "  PASS" -ForegroundColor Green
# Write-Host ""

# --- Extension F: Version Ripple Check ---
# $totalSteps++
# Write-Host "[14/$totalSteps] Check version ripple..." -ForegroundColor Yellow
# python "$root\.agents\scripts\check-version-ripple.py" --root "$root\docs" --bootstrap
# if ($LASTEXITCODE -ne 0) { exit 1 }
# Write-Host "  PASS" -ForegroundColor Green
# Write-Host ""

# ==============================================================================
# Final Result
# ==============================================================================
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All checks passed" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
