#!/bin/bash
# Path Migration CI Check Script (Linux/Mac Bash)
# Usage: bash .agents/scripts/path-migration-ci.sh --old-path <old> --new-path <new> [options]
#
# Based on path-migration-template.py four-layer logging pattern.
# Default: scan-only mode (PR gate). Fails CI if residual references found.

set -e

# ==============================================================================
# Encoding Safety
# ==============================================================================
export LANG="${LANG:-en_US.UTF-8}"
export LC_ALL="${LC_ALL:-en_US.UTF-8}"
if ! locale 2>/dev/null | grep -q 'UTF-8\|utf8'; then
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
# Color Output
# ==============================================================================
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[1;30m'
NC='\033[0m'

# ==============================================================================
# Default values
# ==============================================================================
OLD_PATH=""
NEW_PATH=""
MIGRATION_NAME=""
MODE="scan-only"
AUTO_COMMIT=false
THRESHOLD=0

# ==============================================================================
# Usage
# ==============================================================================
usage() {
    cat <<EOF
Usage: $0 --old-path <old> --new-path <new> [options]

Required:
  --old-path <path>       Old path to migrate from
  --new-path <path>       New path to migrate to

Modes (default: --scan-only):
  --scan-only             Scan only, fail if residual refs found (CI gate)
  --dry-run               Preview migration without modifying
  --execute               Execute migration (use with caution)

Options:
  --migration-name <name> Migration name for commit message
  --auto-commit           Auto commit after migration (with --execute)
  --threshold <n>         Max allowed residual refs (default: 0, --scan-only only)
  --verbose, -v           Enable DEBUG level logging
  --help, -h              Show this help

Examples:
  $0 --old-path "docs/old" --new-path ".agents/docs/new"
  $0 --old-path "docs/old" --new-path ".agents/docs/new" --dry-run
  $0 --old-path "docs/old" --new-path ".agents/docs/new" --execute --auto-commit
  $0 --old-path "docs/old" --new-path ".agents/docs/new" --scan-only --threshold 5
EOF
    exit 0
}

# ==============================================================================
# Parse arguments
# ==============================================================================
while [[ $# -gt 0 ]]; do
    case "$1" in
        --old-path) OLD_PATH="$2"; shift 2 ;;
        --new-path) NEW_PATH="$2"; shift 2 ;;
        --migration-name) MIGRATION_NAME="$2"; shift 2 ;;
        --scan-only) MODE="scan-only"; shift ;;
        --dry-run) MODE="dry-run"; shift ;;
        --execute) MODE="execute"; shift ;;
        --auto-commit) AUTO_COMMIT=true; shift ;;
        --threshold) THRESHOLD="$2"; shift 2 ;;
        --verbose|-v) VERBOSE_FLAG="-v"; shift ;;
        --help|-h) usage ;;
        *) echo -e "${RED}Unknown option: $1${NC}"; usage; exit 2 ;;
    esac
done

# ==============================================================================
# Validate required params
# ==============================================================================
if [[ -z "$OLD_PATH" ]]; then
    echo -e "${RED}ERROR: --old-path is required${NC}"
    usage
    exit 2
fi
if [[ -z "$NEW_PATH" ]]; then
    echo -e "${RED}ERROR: --new-path is required${NC}"
    usage
    exit 2
fi

# Auto-generate migration name
if [[ -z "$MIGRATION_NAME" ]]; then
    MIGRATION_NAME="path-migration-$(date +%Y%m%d%H%M%S)"
fi

# ==============================================================================
# Path Configuration
# ==============================================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(dirname "$SCRIPT_DIR")"
ROOT="$(dirname "$AGENTS_DIR")"
TEMPLATE_SCRIPT="$AGENTS_DIR/scripts/templates/path-migration-template.py"
TEMP_SCRIPT="$(mktemp /tmp/path-migration-ci.XXXXXX.py)"

# ==============================================================================
# Header
# ==============================================================================
TOTAL_STEPS=5
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Path Migration CI Check${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GRAY}Old path:     $OLD_PATH${NC}"
echo -e "${GRAY}New path:     $NEW_PATH${NC}"
echo -e "${GRAY}Migration:    $MIGRATION_NAME${NC}"
echo -e "${GRAY}Mode:         $MODE${NC}"
echo -e "${GRAY}Threshold:    $THRESHOLD${NC}"
echo -e "${GRAY}Project root: $ROOT${NC}"
echo ""

# ==============================================================================
# [1/5] Environment Check
# ==============================================================================
echo -e "${YELLOW}[1/$TOTAL_STEPS] Environment check...${NC}"

PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}  FAIL: Python not found in PATH${NC}"
    exit 2
fi
echo -e "${GRAY}  Python: $($PYTHON_CMD --version 2>&1)${NC}"

if [[ ! -f "$TEMPLATE_SCRIPT" ]]; then
    echo -e "${RED}  FAIL: Template not found: $TEMPLATE_SCRIPT${NC}"
    exit 2
fi
echo -e "${GRAY}  Template: $TEMPLATE_SCRIPT${NC}"

if [[ ! -f "$ROOT/AGENTS.md" ]]; then
    echo -e "${RED}  FAIL: Project root invalid: $ROOT${NC}"
    exit 2
fi
echo -e "${GRAY}  Project root verified${NC}"
echo -e "${GREEN}  PASS${NC}"

# ==============================================================================
# [2/5] Prepare migration script (inject config)
# ==============================================================================
echo -e "${YELLOW}[2/$TOTAL_STEPS] Prepare migration script...${NC}"

sed -e "s|^OLD_PATH = .*|OLD_PATH = \"$OLD_PATH\"|" \
    -e "s|^NEW_PATH = .*|NEW_PATH = \"$NEW_PATH\"|" \
    -e "s|^MIGRATION_NAME = .*|MIGRATION_NAME = \"$MIGRATION_NAME\"|" \
    "$TEMPLATE_SCRIPT" > "$TEMP_SCRIPT"

echo -e "${GRAY}  Config injected into: $TEMP_SCRIPT${NC}"
echo -e "${GREEN}  PASS${NC}"

# ==============================================================================
# [3/5] Execute scan / migration
# ==============================================================================
case "$MODE" in
    scan-only)
        echo -e "${YELLOW}[3/$TOTAL_STEPS] Execute scan (scan-only)...${NC}"
        SCAN_ARGS="--scan-only"
        ;;
    dry-run)
        echo -e "${YELLOW}[3/$TOTAL_STEPS] Execute scan (dry-run)...${NC}"
        SCAN_ARGS="--dry-run"
        ;;
    execute)
        echo -e "${YELLOW}[3/$TOTAL_STEPS] Execute migration...${NC}"
        SCAN_ARGS=""
        if [[ "$AUTO_COMMIT" != "true" ]]; then
            SCAN_ARGS="--no-commit"
        fi
        ;;
esac

SCAN_START=$(date +%s)
SCAN_OUTPUT=$($PYTHON_CMD "$TEMP_SCRIPT" $SCAN_ARGS $VERBOSE_FLAG 2>&1)
SCAN_EXIT=$?
SCAN_END=$(date +%s)
SCAN_DURATION=$((SCAN_END - SCAN_START))

echo -e "${GRAY}  Duration: ${SCAN_DURATION}s${NC}"
echo -e "${GRAY}  Exit code: $SCAN_EXIT${NC}"

# ==============================================================================
# [4/5] Parse results
# ==============================================================================
echo -e "${YELLOW}[4/$TOTAL_STEPS] Parse results...${NC}"

MATCHED_FILES=0
MATCHED_REFS=0
SCAN_SUCCESS=true

if echo "$SCAN_OUTPUT" | grep -q '去重后唯一文件'; then
    MATCHED_FILES=$(echo "$SCAN_OUTPUT" | grep '去重后唯一文件' | grep -oP '\d+')
fi
if echo "$SCAN_OUTPUT" | grep -q '匹配引用总数'; then
    MATCHED_REFS=$(echo "$SCAN_OUTPUT" | grep '匹配引用总数' | grep -oP '\d+')
fi

if echo "$SCAN_OUTPUT" | grep -q '迁移完成\|扫描完成'; then
    SCAN_SUCCESS=true
elif [[ $SCAN_EXIT -ne 0 ]]; then
    SCAN_SUCCESS=false
fi

echo -e "${CYAN}  Matched files: $MATCHED_FILES${NC}"
echo -e "${CYAN}  Matched refs: $MATCHED_REFS${NC}"

# ==============================================================================
# [5/5] Gate decision
# ==============================================================================
echo -e "${YELLOW}[5/$TOTAL_STEPS] Gate decision...${NC}"

if [[ "$MODE" == "scan-only" ]]; then
    if [[ $MATCHED_FILES -gt $THRESHOLD ]]; then
        echo -e "${RED}  FAIL: $MATCHED_FILES files with residual refs (threshold: $THRESHOLD)${NC}"
        echo -e "${GRAY}  To preview: $0 --old-path '$OLD_PATH' --new-path '$NEW_PATH' --dry-run${NC}"
        echo -e "${GRAY}  To execute: $0 --old-path '$OLD_PATH' --new-path '$NEW_PATH' --execute --auto-commit${NC}"
        exit 1
    else
        echo -e "${GREEN}  PASS: No residual refs (threshold: $THRESHOLD)${NC}"
    fi
elif [[ "$MODE" == "dry-run" ]]; then
    if $SCAN_SUCCESS; then
        echo -e "${GREEN}  DRY-RUN: Would modify $MATCHED_FILES files${NC}"
    else
        echo -e "${RED}  DRY-RUN failed (exit: $SCAN_EXIT)${NC}"
    fi
else
    if $SCAN_SUCCESS; then
        echo -e "${GREEN}  Migration executed successfully${NC}"
    else
        echo -e "${RED}  Migration failed (exit: $SCAN_EXIT)${NC}"
        exit 1
    fi
fi

# ==============================================================================
# Summary
# ==============================================================================
echo ""
echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Summary${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GRAY}Mode:              $MODE${NC}"
echo -e "${GRAY}Matched files:     $MATCHED_FILES${NC}"
echo -e "${GRAY}Matched refs:      $MATCHED_REFS${NC}"
echo -e "${GRAY}Duration:          ${SCAN_DURATION}s${NC}"
if $SCAN_SUCCESS; then
    echo -e "${GREEN}Result:            PASS${NC}"
else
    echo -e "${RED}Result:            FAIL${NC}"
fi

# Cleanup
rm -f "$TEMP_SCRIPT"

exit 0