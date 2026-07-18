#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

PS1_CONTENT = r'''# Path Migration CI Check Script (Windows PowerShell)
param(
    [switch]$ScanOnly,
    [switch]$DryRun,
    [switch]$Execute,
    [Parameter(Mandatory=$true)][string]$OldPath,
    [Parameter(Mandatory=$true)][string]$NewPath,
    [string]$MigrationName = "path-migration",
    [switch]$AutoCommit,
    [switch]$Verbose,
    [switch]$Help
)

$ErrorActionPreference = "Stop"
cmd /c chcp 65001 > $null
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"
if ($PSVersionTable.PSVersion.Major -ge 7) { $PSDefaultParameterValues["*:Encoding"] = "utf8" }

$R="Red";$G="Green";$Y="Yellow";$C="Cyan";$Gr="Gray";$W="White"

if ($Help) {
    Write-Host "Path Migration CI Check" -ForegroundColor $W
    Write-Host "Modes: -ScanOnly (default PR check) | -DryRun | -Execute" -ForegroundColor $W
    Write-Host "Required: -OldPath <old> -NewPath <new>" -ForegroundColor $W
    Write-Host "Options: -MigrationName <name> -AutoCommit -Verbose" -ForegroundColor $W
    Write-Host "Exit: 0=pass 1=fail 2=env-error" -ForegroundColor $W
    exit 0
}

if (-not ($ScanOnly -or $DryRun -or $Execute)) { $ScanOnly = $true }
$modeCount = @($ScanOnly,$DryRun,$Execute) | Where-Object { $_ } | Measure-Object | Select-Object -ExpandProperty Count
if ($modeCount -gt 1) { Write-Host "ERROR: Only one mode allowed" -ForegroundColor $R; exit 2 }

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent (Split-Path -Parent $scriptDir)
$templatePy = Join-Path $root ".agents\scripts\templates\path-migration-template.py"
$tempPy = Join-Path $env:TEMP ("pmig-"+(Get-Date -Format "yyyyMMdd-HHmmss")+".py")

Write-Host "========================================" -ForegroundColor $C
Write-Host "Path Migration CI Check" -ForegroundColor $C
Write-Host "========================================" -ForegroundColor $C
Write-Host -NoNewline "Mode: " -ForegroundColor $Gr
if ($ScanOnly) { Write-Host "SCAN ONLY (PR Check)" -ForegroundColor $Y }
elseif ($DryRun) { Write-Host "DRY RUN (Preview)" -ForegroundColor $Y }
else { Write-Host "EXECUTE (Live)" -ForegroundColor $R }
Write-Host "Old Path: $OldPath" -ForegroundColor $Gr
Write-Host "New Path: $NewPath" -ForegroundColor $Gr
Write-Host "Project Root: $root" -ForegroundColor $Gr
Write-Host ""

$totalSteps = 5
$startTime = Get-Date
$fileCount = 0
$matchCount = 0

function Write-Step($n, $msg) { Write-Host "[$n/$totalSteps] $msg" -ForegroundColor $Y }
function Write-Pass($msg="PASS") { Write-Host "  $msg" -ForegroundColor $G }
function Write-Fail($msg="FAIL") { Write-Host "  $msg" -ForegroundColor $R }
function Write-Info($msg) { Write-Host "  $msg" -ForegroundColor $Gr }

Write-Step 1 "Environment check..."
$py = $null
foreach ($c in "python","python3","py") {
    try {
        $null = & $c --version 2>&1
        if ($LASTEXITCODE -eq 0) { $py = $c; break }
    } catch {}
}
if (-not $py) { Write-Fail "ERROR: Python not found in PATH"; exit 2 }
$pyVer = & $py --version 2>&1
Write-Info "Python: $pyVer"
if (-not (Test-Path $templatePy)) { Write-Fail "ERROR: Template not found: $templatePy"; exit 2 }
Write-Info "Template: $templatePy"
Write-Pass
Write-Host ""

Write-Step 2 "Parameter validation..."
if ([string]::IsNullOrWhiteSpace($OldPath)) { Write-Fail "ERROR: -OldPath is required"; exit 2 }
if ([string]::IsNullOrWhiteSpace($NewPath)) { Write-Fail "ERROR: -NewPath is required"; exit 2 }
if ($OldPath -eq $NewPath) { Write-Fail "ERROR: OldPath and NewPath must differ"; exit 2 }
$oldFull = Join-Path $root $OldPath
if (-not (Test-Path $oldFull)) { Write-Info "Note: Old path not on disk (scanning file contents only)" }
else { Write-Info "Old path exists on disk" }
Write-Pass
Write-Host ""

Write-Step 3 "Preparing script and executing scan..."
$tc = Get-Content -Path $templatePy -Raw -Encoding UTF8
$rootEsc = $root
$tc = $tc -replace '(?m)^OLD_PATH = .*$', "OLD_PATH = '$OldPath'"
$tc = $tc -replace '(?m)^NEW_PATH = .*$', "NEW_PATH = '$NewPath'"
$tc = $tc -replace '(?m)^MIGRATION_NAME = .*$', "MIGRATION_NAME = '$MigrationName'"
$tc = $tc -replace '(?m)^PROJECT_ROOT = .*$', "PROJECT_ROOT = Path(r'$rootEsc')"
Set-Content -Path $tempPy -Value $tc -Encoding UTF8
Write-Info "Temp script created"

$pa = @()
if ($ScanOnly) { $pa += "--scan-only" }
if ($DryRun) { $pa += "--dry-run" }
if (-not $AutoCommit -and $Execute) { $pa += "--no-commit" }
if ($Verbose) { $pa += "-v" }

Write-Info "Running Python migration script..."
Write-Host ""
$out = & $py $tempPy $pa 2>&1
$ec = $LASTEXITCODE
$out | ForEach-Object { Write-Host "  $_" -ForegroundColor $Gr }
Write-Host ""

Write-Step 4 "Analyzing results..."
foreach ($l in $out) {
    if ($l -match "去重后唯一文件:\s*(\d+)") { $fileCount = [int]$Matches[1] }
    if ($l -match "匹配引用总数:\s*(\d+)") { $matchCount = [int]$Matches[1] }
}
Write-Info "Files with old path: $fileCount"
Write-Info "Total matches: $matchCount"
Write-Pass "Scan phase complete"
Write-Host ""

Write-Step 5 "Gate decision..."
$endTime = Get-Date
$dur = [math]::Round(($endTime - $startTime).TotalSeconds, 2)
$xc = 0
$st = ""
$sc = $G

if ($ScanOnly) {
    if ($fileCount -gt 0 -or $matchCount -gt 0) {
        Write-Fail "FAIL: Found $fileCount files containing $matchCount old path references"
        $xc = 1
        $st = "FAILED - Old path remnants detected (blocking CI)"
        $sc = $R
    } else {
        Write-Pass "PASS: No old path remnants found"
        $xc = 0
        $st = "PASSED - No remnants"
        $sc = $G
    }
} elseif ($DryRun) {
    Write-Pass "DRY RUN completed - no changes made"
    Write-Info "Would affect approximately $fileCount files"
    $xc = 0
    $st = "DRY RUN - Preview complete"
    $sc = $Y
} else {
    if ($ec -eq 0) {
        Write-Pass "Migration executed successfully"
        if ($AutoCommit) { Write-Info "Changes auto-committed" }
        $xc = 0
        $st = "SUCCESS - Migration complete"
        $sc = $G
    } else {
        Write-Fail "FAIL: Migration script exited with code $ec"
        $xc = 1
        $st = "FAILED - Migration error (exit $ec)"
        $sc = $R
    }
}

if (Test-Path $tempPy) { Remove-Item -Path $tempPy -Force -ErrorAction SilentlyContinue }
Write-Host ""

Write-Host "========================================" -ForegroundColor $C
Write-Host "Summary" -ForegroundColor $C
Write-Host "========================================" -ForegroundColor $C
Write-Host -NoNewline "Status: " -ForegroundColor $Gr
Write-Host $st -ForegroundColor $sc
Write-Host "Old Path: $OldPath" -ForegroundColor $Gr
Write-Host "New Path: $NewPath" -ForegroundColor $Gr
Write-Host "Files affected: $fileCount" -ForegroundColor $Gr
Write-Host "Matches found: $matchCount" -ForegroundColor $Gr
Write-Host "Duration: ${dur}s" -ForegroundColor $Gr
Write-Host "========================================" -ForegroundColor $C
exit $xc
'''

SH_CONTENT = r'''#!/bin/bash
# Path Migration CI Check Script (Linux/Mac Bash)
set -e

export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
if ! locale 2>/dev/null | grep -q 'UTF-8\|utf8'; then
    echo "WARNING: UTF-8 locale not detected, attempting to set..."
    for cand in en_US.UTF-8 C.UTF-8 en_GB.UTF-8; do
        if locale -a 2>/dev/null | grep -qi "$cand"; then
            export LANG="$cand"
            export LC_ALL="$cand"
            break
        fi
    done
fi
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[1;30m'
WHITE='\033[1;37m'
NC='\033[0m'

SCAN_ONLY=true
DRY_RUN=false
EXECUTE=false
OLD_PATH=""
NEW_PATH=""
MIGRATION_NAME="path-migration"
AUTO_COMMIT=false
VERBOSE=false

show_help() {
    echo -e "${WHITE}Path Migration CI Check${NC}"
    echo -e "${WHITE}Modes: --scan-only (default) | --dry-run | --execute${NC}"
    echo -e "${WHITE}Required: --old-path <old> --new-path <new>${NC}"
    echo -e "${WHITE}Options: --migration-name <name> --auto-commit --verbose --help${NC}"
    echo -e "${WHITE}Exit: 0=pass 1=fail 2=env-error${NC}"
    exit 0
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --scan-only) SCAN_ONLY=true; shift ;;
        --dry-run) DRY_RUN=true; SCAN_ONLY=false; shift ;;
        --execute) EXECUTE=true; SCAN_ONLY=false; shift ;;
        --old-path) OLD_PATH="$2"; shift 2 ;;
        --new-path) NEW_PATH="$2"; shift 2 ;;
        --migration-name) MIGRATION_NAME="$2"; shift 2 ;;
        --auto-commit) AUTO_COMMIT=true; shift ;;
        --verbose|-v) VERBOSE=true; shift ;;
        --help|-h) show_help ;;
        *) echo -e "${RED}ERROR: Unknown option: $1${NC}"; exit 2 ;;
    esac
done

mode_count=0
if $SCAN_ONLY; then mode_count=$((mode_count+1)); fi
if $DRY_RUN; then mode_count=$((mode_count+1)); fi
if $EXECUTE; then mode_count=$((mode_count+1)); fi
if [ "$mode_count" -gt 1 ]; then
    echo -e "${RED}ERROR: Only one mode allowed${NC}"
    exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(dirname "$SCRIPT_DIR")"
ROOT="$(dirname "$AGENTS_DIR")"
TEMPLATE_PY="$ROOT/.agents/scripts/templates/path-migration-template.py"
TEMP_PY="$(mktemp -t pmig-XXXXXX.py)"

cleanup() {
    rm -f "$TEMP_PY" 2>/dev/null || true
}
trap cleanup EXIT

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Path Migration CI Check${NC}"
echo -e "${CYAN}========================================${NC}"
echo -ne "${GRAY}Mode: ${NC}"
if $SCAN_ONLY; then echo -e "${YELLOW}SCAN ONLY (PR Check)${NC}"
elif $DRY_RUN; then echo -e "${YELLOW}DRY RUN (Preview)${NC}"
else echo -e "${RED}EXECUTE (Live)${NC}"; fi
echo -e "${GRAY}Old Path: $OLD_PATH${NC}"
echo -e "${GRAY}New Path: $NEW_PATH${NC}"
echo -e "${GRAY}Project Root: $ROOT${NC}"
echo ""

TOTAL=5
START_TIME=$(date +%s)
FILE_COUNT=0
MATCH_COUNT=0

step() { echo -e "${YELLOW}[$1/$TOTAL] $2${NC}"; }
pass() { echo -e "  ${GREEN}${1:-PASS}${NC}"; }
fail() { echo -e "  ${RED}${1:-FAIL}${NC}"; }
info() { echo -e "  ${GRAY}$1${NC}"; }

step 1 "Environment check..."
PY=""
for c in python3 python; do
    if command -v "$c" >/dev/null 2>&1; then
        if "$c" --version >/dev/null 2>&1; then PY="$c"; break; fi
    fi
done
if [ -z "$PY" ]; then fail "ERROR: Python not found in PATH"; exit 2; fi
info "Python: $($PY --version 2>&1)"
if [ ! -f "$TEMPLATE_PY" ]; then fail "ERROR: Template not found: $TEMPLATE_PY"; exit 2; fi
info "Template: $TEMPLATE_PY"
pass
echo ""

step 2 "Parameter validation..."
if [ -z "$OLD_PATH" ] || [ -z "$NEW_PATH" ]; then fail "ERROR: --old-path and --new-path are required"; exit 2; fi
if [ "$OLD_PATH" = "$NEW_PATH" ]; then fail "ERROR: Old path and new path must differ"; exit 2; fi
pass
echo ""

step 3 "Preparing script and executing scan..."
OLD_PATH_ESC=$(printf '%s' "$OLD_PATH" | sed "s/'/\\\\'/g")
NEW_PATH_ESC=$(printf '%s' "$NEW_PATH" | sed "s/'/\\\\'/g")
MIG_NAME_ESC=$(printf '%s' "$MIGRATION_NAME" | sed "s/'/\\\\'/g")
ROOT_ESC=$(printf '%s' "$ROOT" | sed 's/\\/\\\\/g')

sed -e "s|^OLD_PATH = .*|OLD_PATH = '$OLD_PATH_ESC'|" \
    -e "s|^NEW_PATH = .*|NEW_PATH = '$NEW_PATH_ESC'|" \
    -e "s|^MIGRATION_NAME = .*|MIGRATION_NAME = '$MIG_NAME_ESC'|" \
    -e "s|^PROJECT_ROOT = .*|PROJECT_ROOT = Path(r'$ROOT_ESC')|" \
    "$TEMPLATE_PY" > "$TEMP_PY"
info "Temp script created"

PY_ARGS=()
if $SCAN_ONLY; then PY_ARGS+=("--scan-only"); fi
if $DRY_RUN; then PY_ARGS+=("--dry-run"); fi
if ! $AUTO_COMMIT && $EXECUTE; then PY_ARGS+=("--no-commit"); fi
if $VERBOSE; then PY_ARGS+=("-v"); fi

info "Running Python migration script..."
echo ""
set +e
mapfile -t OUTPUT < <("$PY" "$TEMP_PY" "${PY_ARGS[@]}" 2>&1)
EC=$?
set -e
for line in "${OUTPUT[@]}"; do echo -e "  ${GRAY}${line}${NC}"; done
echo ""

step 4 "Analyzing results..."
for line in "${OUTPUT[@]}"; do
    if [[ "$line" =~ 去重后唯一文件:\ *([0-9]+) ]]; then FILE_COUNT="${BASH_REMATCH[1]}"; fi
    if [[ "$line" =~ 匹配引用总数:\ *([0-9]+) ]]; then MATCH_COUNT="${BASH_REMATCH[1]}"; fi
done
info "Files with old path: $FILE_COUNT"
info "Total matches: $MATCH_COUNT"
pass "Scan phase complete"
echo ""

step 5 "Gate decision..."
END_TIME=$(date +%s)
DUR=$((END_TIME - START_TIME))
XC=0
ST=""
SC="$GREEN"

if $SCAN_ONLY; then
    if [ "$FILE_COUNT" -gt 0 ] || [ "$MATCH_COUNT" -gt 0 ]; then
        fail "FAIL: Found $FILE_COUNT files containing $MATCH_COUNT old path references"
        XC=1
        ST="FAILED - Old path remnants detected (blocking CI)"
        SC="$RED"
    else
        pass "PASS: No old path remnants found"
        XC=0
        ST="PASSED - No remnants"
        SC="$GREEN"
    fi
elif $DRY_RUN; then
    pass "DRY RUN completed - no changes made"
    info "Would affect approximately $FILE_COUNT files"
    XC=0
    ST="DRY RUN - Preview complete"
    SC="$YELLOW"
else
    if [ "$EC" -eq 0 ]; then
        pass "Migration executed successfully"
        if $AUTO_COMMIT; then info "Changes auto-committed"; fi
        XC=0
        ST="SUCCESS - Migration complete"
        SC="$GREEN"
    else
        fail "FAIL: Migration script exited with code $EC"
        XC=1
        ST="FAILED - Migration error (exit $EC)"
        SC="$RED"
    fi
fi

echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}Summary${NC}"
echo -e "${CYAN}========================================${NC}"
echo -ne "${GRAY}Status: ${NC}"
echo -e "${SC}${ST}${NC}"
echo -e "${GRAY}Old Path: $OLD_PATH${NC}"
echo -e "${GRAY}New Path: $NEW_PATH${NC}"
echo -e "${GRAY}Files affected: $FILE_COUNT${NC}"
echo -e "${GRAY}Matches found: $MATCH_COUNT${NC}"
echo -e "${GRAY}Duration: ${DUR}s${NC}"
echo -e "${CYAN}========================================${NC}"
exit $XC
'''

script_dir = os.path.dirname(os.path.abspath(__file__))

ps1_path = os.path.join(script_dir, "path-migration-ci.ps1")
with open(ps1_path, "w", encoding="utf-8") as f:
    f.write(PS1_CONTENT)
print(f"Created: {ps1_path}")

sh_path = os.path.join(script_dir, "path-migration-ci.sh")
with open(sh_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(SH_CONTENT)
print(f"Created: {sh_path}")
