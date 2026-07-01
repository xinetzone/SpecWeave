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

# 1. Repo compliance checks (gitignore + vendor + mermaid + filename + roles)
echo -e "${YELLOW}[1/8] Repo compliance checks (gitignore+vendor+mermaid+filename+roles)...${NC}"
python3 "$ROOT/.agents/scripts/repo-check.py" all
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 2. Check links
echo -e "${YELLOW}[2/8] Check links...${NC}"
python3 "$ROOT/.agents/scripts/check-links.py"
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 3. Check spec consistency
echo -e "${YELLOW}[3/8] Check spec consistency...${NC}"
python3 "$ROOT/.agents/scripts/spec-tool.py" check || echo -e "  ${YELLOW}WARN: spec consistency check has warnings${NC}"
echo ""

# 4. Check pattern maturity (CI mode)
echo -e "${YELLOW}[4/8] Check pattern maturity...${NC}"
python3 "$ROOT/.agents/scripts/pattern-maturity.py" check
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 5. Generate docs (nav + dashboard + apps)
echo -e "${YELLOW}[5/8] Generate docs (nav+dashboard+apps)...${NC}"
python3 "$ROOT/.agents/scripts/docgen.py" all
echo -e "  ${GREEN}PASS${NC}"
echo ""

# 6. Check PowerShell pipe safety
echo -e "${YELLOW}[6/9] Check PowerShell pipe safety...${NC}"
if python3 "$ROOT/.agents/scripts/check-powershell-pipe-safety.py"; then
    true
else
    echo -e "  ${YELLOW}WARN: PowerShell pipe safety check failed unexpectedly${NC}"
fi
echo ""

# 7. Check script duplication
echo -e "${YELLOW}[7/9] Check script duplication...${NC}"
if python3 "$ROOT/.agents/scripts/check-duplication.py"; then
    echo -e "  ${GREEN}PASS${NC}"
else
    echo -e "  ${YELLOW}WARN: cross-file duplication detected, consider extracting to lib/${NC}"
    echo -e "  ${YELLOW}  Ref: .agents/scripts/lib/README.md${NC}"
fi
echo ""

# 8. Stage guardrail log check (strict mode)
echo -e "${YELLOW}[8/9] Check stage guardrail logs...${NC}"
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

# 9. Generate SG dashboard
echo -e "${YELLOW}[9/9] Generate stage guardrail dashboard...${NC}"
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
