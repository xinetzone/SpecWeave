#!/bin/bash
# CI/CD Pipeline Check Script (Linux/Mac Bash Template)
# Usage: bash .agents/scripts/ci-check-template.sh
#
# CUSTOMIZATION NOTES:
# 1. Adjust ROOT path calculation to match your project structure
# 2. Comment out gates that don't apply to your project
# 3. Update TOTAL count when adding/removing gates
# 4. Adjust thresholds (e.g., --threshold 60 for hardcode check)
# 5. Add project-specific checks following the same pattern

set -e

# ==============================================================================
# Encoding Safety: Force UTF-8 locale
# ==============================================================================
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
if ! locale 2>/dev/null | grep -q 'UTF-8\|utf8'; then
    echo "WARNING: UTF-8 locale not detected, attempting to set..."
    for candidate in en_US.UTF-8 C.UTF-8 en_GB.UTF-8; do
        if locale -a 2>/dev/null | grep -qi "$candidate"; then
            export LANG="$candidate"
            export LC_ALL="$candidate"
            break
        fi
    done
fi
export PYTHONIOENCODING=utf-8
export PYTHONUTF8=1

# ==============================================================================
# Path Configuration (CUSTOMIZE THIS FOR YOUR PROJECT)
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(dirname "$SCRIPT_DIR")"
ROOT="$(dirname "$AGENTS_DIR")"
# If your .agents directory is at a different level, adjust the above lines.
# Example for projects where scripts live in scripts/ directly (no .agents dir):
# ROOT="$(dirname "$SCRIPT_DIR")"

# ==============================================================================
# Color Output
# ==============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[1;30m'
DARKGRAY='\033[1;30m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}CI/CD Pipeline Check (Template)${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GRAY}LANG: $LANG${NC}"
echo -e "${GRAY}LC_ALL: $LC_ALL${NC}"
echo -e "${GRAY}PYTHONIOENCODING: $PYTHONIOENCODING${NC}"
echo -e "${GRAY}Project root: $ROOT${NC}"
echo ""

# ==============================================================================
# Total Steps Count (UPDATE WHEN ADDING/REMOVING GATES)
# ==============================================================================
TOTAL=8

# ==============================================================================
# Gate 1/8: Repo Compliance Checks 🔴 FAIL
# Covers: gitignore rules, vendor directory, Mermaid syntax, filename conventions, roles
# ==============================================================================
echo -e "${YELLOW}[1/$TOTAL] Repo compliance checks (gitignore+vendor+mermaid+filename+roles)...${NC}"
# CUSTOMIZE: Replace with your compliance check script, or remove if not needed
python3 "$ROOT/.agents/scripts/repo-check.py" all
echo -e "  ${GREEN}PASS${NC}"
echo ""

# ==============================================================================
# Gate 2/8: Link Validity Check 🔴 FAIL
# Verifies all local Markdown links point to existing files
# ==============================================================================
echo -e "${YELLOW}[2/$TOTAL] Check links...${NC}"
# CUSTOMIZE: Add --path <dir> to check specific directory only
# CUSTOMIZE: Add --check-external to also verify external URLs
python3 "$ROOT/.agents/scripts/check-links.py"
echo -e "  ${GREEN}PASS${NC}"
echo ""

# ==============================================================================
# Gate 3/8: Spec Consistency Check 🟡 WARN (non-blocking)
# Verifies spec.md / tasks.md / checklist.md are consistent
# ==============================================================================
echo -e "${YELLOW}[3/$TOTAL] Check spec consistency...${NC}"
# CUSTOMIZE: Replace with your spec validation script, or remove if not using SpecWeave
python3 "$ROOT/.agents/scripts/spec-tool.py" check || echo -e "  ${YELLOW}WARN: spec consistency check has warnings (non-blocking)${NC}"
echo ""

# ==============================================================================
# Gate 4/8: Pattern Maturity Check 🔴 FAIL
# Ensures reusable patterns meet minimum quality standards
# ==============================================================================
echo -e "${YELLOW}[4/$TOTAL] Check pattern maturity...${NC}"
# CUSTOMIZE: Remove if your project doesn't use pattern-based knowledge management
python3 "$ROOT/.agents/scripts/pattern-maturity.py" check
echo -e "  ${GREEN}PASS${NC}"
echo ""

# ==============================================================================
# Gate 5/8: Documentation Auto-Generation 🔴 FAIL
# Generates nav tables, dashboards, app indexes (WRITE OPERATION - idempotent)
# ==============================================================================
echo -e "${YELLOW}[5/$TOTAL] Generate docs (nav+dashboard+apps)...${NC}"
# CUSTOMIZE: Replace with your doc generation script, or remove if not needed
# NOTE: This step MODIFIES FILES in marked regions only (safe, idempotent)
python3 "$ROOT/.agents/scripts/docgen.py" all
echo -e "  ${GREEN}PASS${NC}"
echo ""

# ==============================================================================
# Gate 6/8: Cross-File Duplication Detection 🟡 WARN (non-blocking)
# Detects code duplication across scripts to encourage shared library extraction
# ==============================================================================
echo -e "${YELLOW}[6/$TOTAL] Check script duplication...${NC}"
# CUSTOMIZE: Add --path <dir> to check specific directory, or remove if not needed
if python3 "$ROOT/.agents/scripts/check-duplication.py"; then
    echo -e "  ${GREEN}PASS${NC}"
else
    echo -e "  ${YELLOW}WARN: cross-file duplication detected, consider extracting to shared lib/${NC}"
fi
echo ""

# ==============================================================================
# Gate 7/8: Stage Guardrail Log Compliance 🔴 FAIL
# Checks stage guardrail logs for violations (strict mode, zero tolerance)
# ==============================================================================
echo -e "${YELLOW}[7/$TOTAL] Check stage guardrail logs...${NC}"
SG_LOG_FILE="${STAGE_GUARDRAIL_LOG:-}"
if [ -z "$SG_LOG_FILE" ]; then
    # Auto-detect latest log file if not specified via env var
    LOGS_DIR="$ROOT/.agents/logs"
    if [ -d "$LOGS_DIR" ]; then
        LATEST_LOG=$(ls -t "$LOGS_DIR"/*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
            SG_LOG_FILE="$LATEST_LOG"
        fi
    fi
fi
if [ -n "$SG_LOG_FILE" ] && [ -f "$SG_LOG_FILE" ]; then
    # CUSTOMIZE: Remove --strict for lenient mode, or remove entire gate if not needed
    python3 "$ROOT/.agents/scripts/check-stage-guardrails.py" --log-file "$SG_LOG_FILE" --strict
    echo -e "  ${GREEN}PASS${NC}"
else
    echo -e "  ${DARKGRAY}SKIP (no log file found, set STAGE_GUARDRAIL_LOG env var)${NC}"
fi
echo ""

# ==============================================================================
# Gate 8/8: Stage Guardrail Dashboard Generation 🟡 WARN (non-blocking)
# Generates visual HTML dashboard of guardrail compliance
# ==============================================================================
echo -e "${YELLOW}[8/$TOTAL] Generate stage guardrail dashboard...${NC}"
LOGS_DIR="$ROOT/.agents/logs"
if [ -d "$LOGS_DIR" ] && ls "$LOGS_DIR"/*.log >/dev/null 2>&1; then
    if python3 "$ROOT/.agents/scripts/generate-sg-dashboard.py"; then
        echo -e "  ${GREEN}PASS (dashboard: .agents/reports/sg-dashboard.html)${NC}"
    else
        echo -e "  ${YELLOW}WARN: SG dashboard generation failed (non-blocking)${NC}"
    fi
else
    echo -e "  ${DARKGRAY}SKIP (no log files in .agents/logs/)${NC}"
fi
echo ""

# ==============================================================================
# OPTIONAL EXTENSION GATES (uncomment to enable)
# ==============================================================================

# --- Extension A: RACI Compliance Check ---
# TOTAL=$((TOTAL + 1))  # Remember to increment total steps!
# echo -e "${YELLOW}[9/$TOTAL] Check RACI compliance...${NC}"
# python3 "$ROOT/.agents/scripts/check-raci-compliance.py" --path "$ROOT/.agents/rules" || exit 1
# python3 "$ROOT/.agents/scripts/check-raci-compliance.py" --path "$ROOT/.agents/commands" || exit 1
# echo -e "  ${GREEN}PASS${NC}"
# echo ""

# --- Extension B: Hardcoded Values Detection ---
# TOTAL=$((TOTAL + 1))
# echo -e "${YELLOW}[10/$TOTAL] Check hardcoded values...${NC}"
# python3 "$ROOT/.agents/scripts/check-hardcode.py" --path "$ROOT/.agents/scripts" --threshold 60 || exit 1
# echo -e "  ${GREEN}PASS${NC}"
# echo ""

# --- Extension C: File Size Thresholds ---
# TOTAL=$((TOTAL + 1))
# echo -e "${YELLOW}[11/$TOTAL] Check file size thresholds...${NC}"
# python3 "$ROOT/.agents/scripts/check-file-size.py" --warn-only || echo -e "  ${YELLOW}WARN: file size issues found${NC}"
# echo ""

# --- Extension D: Directory README Existence ---
# TOTAL=$((TOTAL + 1))
# echo -e "${YELLOW}[12/$TOTAL] Check directory README existence...${NC}"
# python3 "$ROOT/.agents/scripts/generate-readme.py" --check || exit 1
# echo -e "  ${GREEN}PASS${NC}"
# echo ""

# --- Extension E: Skill Quality Scoring ---
# TOTAL=$((TOTAL + 1))
# echo -e "${YELLOW}[13/$TOTAL] Check Skill quality...${NC}"
# python3 "$ROOT/.agents/scripts/check-skill-quality.py" --threshold 70 || exit 1
# echo -e "  ${GREEN}PASS${NC}"
# echo ""

# --- Extension F: Version Ripple Check ---
# TOTAL=$((TOTAL + 1))
# echo -e "${YELLOW}[14/$TOTAL] Check version ripple...${NC}"
# python3 "$ROOT/.agents/scripts/check-version-ripple.py" --root "$ROOT/docs" --bootstrap || exit 1
# echo -e "  ${GREEN}PASS${NC}"
# echo ""

# ==============================================================================
# Final Result
# ==============================================================================
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}All checks passed${NC}"
echo -e "${CYAN}========================================${NC}"
