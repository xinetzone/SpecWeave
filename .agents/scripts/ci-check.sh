#!/bin/bash
# CI/CD pipeline check script
# Usage: bash ci-check.sh

set -e

# 编码安全设置：强制使用UTF-8 locale
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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(dirname "$SCRIPT_DIR")"
ROOT="$(dirname "$AGENTS_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[1;30m'
NC='\033[0m'

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}CI/CD Pipeline Check${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GRAY}LANG: $LANG${NC}"
echo -e "${GRAY}LC_ALL: $LC_ALL${NC}"
echo -e "${GRAY}PYTHONIOENCODING: $PYTHONIOENCODING${NC}"
echo ""

TOTAL=11

# 1. Repo compliance checks (gitignore + vendor + mermaid + filename + roles)
echo -e "${YELLOW}[1/$TOTAL] Repo compliance checks (gitignore+vendor+mermaid+filename+roles)...${NC}"
python3 "$ROOT/.agents/scripts/repo-check.py" all
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 2. Check links
echo -e "${YELLOW}[2/$TOTAL] Check links...${NC}"
python3 "$ROOT/.agents/scripts/check-links.py"
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 3. Check RACI compliance (A唯一性/R≠A分离/角色列完整性)
echo -e "${YELLOW}[3/$TOTAL] Check RACI compliance in rules/commands...${NC}"
RACI_EXIT=0
python3 "$ROOT/.agents/scripts/check-raci-compliance.py" --path "$ROOT/.agents/rules" || RACI_EXIT=$?
python3 "$ROOT/.agents/scripts/check-raci-compliance.py" --path "$ROOT/.agents/commands" || RACI_EXIT2=$?
if [ "$RACI_EXIT" -ne 0 ] || [ "${RACI_EXIT2:-0}" -ne 0 ]; then
    echo -e "  ${RED}ERROR: RACI compliance check found errors (double-A, missing-A, or self-approval)${NC}"
    exit 1
fi
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 4. Check hardcode (8类硬编码AST检测)
echo -e "${YELLOW}[4/$TOTAL] Check hardcoded values in Python scripts...${NC}"
python3 "$ROOT/.agents/scripts/check-hardcode.py" --path "$ROOT/.agents/scripts" --threshold 60
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 5. Check spec consistency
echo -e "${YELLOW}[5/$TOTAL] Check spec consistency...${NC}"
python3 "$ROOT/.agents/scripts/spec-tool.py" check || echo -e "  ${YELLOW}WARN: spec consistency check has warnings${NC}"
echo ""

# 6. Check pattern maturity (CI mode)
echo -e "${YELLOW}[6/$TOTAL] Check pattern maturity...${NC}"
python3 "$ROOT/.agents/scripts/pattern-maturity.py" check
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 7. Generate docs (nav + dashboard + apps)
echo -e "${YELLOW}[7/$TOTAL] Generate docs (nav+dashboard+apps)...${NC}"
python3 "$ROOT/.agents/scripts/docgen.py" all
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 8. Check PowerShell pipe safety
echo -e "${YELLOW}[8/$TOTAL] Check PowerShell pipe safety...${NC}"
if python3 "$ROOT/.agents/scripts/check-powershell-pipe-safety.py"; then
    true
else
    echo -e "  ${YELLOW}WARN: PowerShell pipe safety check failed unexpectedly${NC}"
fi
echo ""

# 9. Check script duplication
echo -e "${YELLOW}[9/$TOTAL] Check script duplication...${NC}"
if python3 "$ROOT/.agents/scripts/check-duplication.py"; then
    echo -e "  ${GREEN}PASS${NC}"
else
    echo -e "  ${YELLOW}WARN: cross-file duplication detected, consider extracting to lib/${NC}"
    echo -e "  ${YELLOW}  Ref: .agents/scripts/lib/README.md${NC}"
fi
echo ""

# 10. Stage guardrail log check (strict mode)
echo -e "${YELLOW}[10/$TOTAL] Check stage guardrail logs...${NC}"
SG_LOG_FILE="${STAGE_GUARDRAIL_LOG:-}"
if [ -z "$SG_LOG_FILE" ]; then
    LOGS_DIR="$ROOT/.agents/logs"
    if [ -d "$LOGS_DIR" ]; then
        LATEST_LOG=$(ls -t "$LOGS_DIR"/*.log 2>/dev/null | head -1)
        if [ -n "$LATEST_LOG" ] && [ -f "$LATEST_LOG" ]; then
            SG_LOG_FILE="$LATEST_LOG"
        fi
    fi
fi
if [ -n "$SG_LOG_FILE" ] && [ -f "$SG_LOG_FILE" ]; then
    python3 "$ROOT/.agents/scripts/check-stage-guardrails.py" --log-file "$SG_LOG_FILE" --strict
    echo -e "  ${GREEN}PASS${NC}"
else
    echo -e "  ${GRAY}SKIP (no log file found, set STAGE_GUARDRAIL_LOG env var)${NC}"
fi
echo ""

# 11. Generate SG dashboard
echo -e "${YELLOW}[11/$TOTAL] Generate stage guardrail dashboard...${NC}"
LOGS_DIR="$ROOT/.agents/logs"
if [ -d "$LOGS_DIR" ] && ls "$LOGS_DIR"/*.log >/dev/null 2>&1; then
    if python3 "$ROOT/.agents/scripts/generate-sg-dashboard.py"; then
        echo -e "  ${GREEN}PASS (dashboard: .agents/reports/sg-dashboard.html)${NC}"
    else
        echo -e "  ${YELLOW}WARN: SG dashboard generation failed (non-blocking)${NC}"
    fi
else
    echo -e "  ${GRAY}SKIP (no log files in .agents/logs/)${NC}"
fi
echo ""

echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}All checks passed${NC}"
echo -e "${CYAN}========================================${NC}"
