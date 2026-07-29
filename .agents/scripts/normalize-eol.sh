#!/bin/bash
# =============================================================================
# Line Ending Normalization Script (One-Click Fix)
# =============================================================================
# Fix CRLF/LF line endings across the main repo and all git submodules.
# Handles the root cause of Docker/Linux build failures caused by Windows CRLF
# in autotools scripts (configure, config.sub, *.ac, *.am, *.in, etc.).
#
# Usage:
#   bash .agents/scripts/normalize-eol.sh                       # dry-run everything
#   bash .agents/scripts/normalize-eol.sh --commit              # commit main repo only
#   bash .agents/scripts/normalize-eol.sh --fix-submodules      # also patch submodule .gitattributes
#   bash .agents/scripts/normalize-eol.sh --fix-submodules --commit
#   bash .agents/scripts/normalize-eol.sh --fix-submodules --include-vendor
#
# Options:
#   --commit           Commit changes in the main repo (default: dry-run)
#   --fix-submodules   Add missing autotools rules to submodule .gitattributes
#                      and run renormalize there too (default: report only)
#   --include-vendor   Also process vendor/ third-party submodules (default:
#                      only projects/ first-party submodules)
#   --no-recursive     Only process direct submodules, skip nested submodules
#   -h, --help         Show this help
#
# What it does:
#   Phase 1: Main repo — verify .gitattributes, renormalize, optionally commit
#   Phase 2: Submodules — scan recursively, check .gitattributes for autotools
#            rules, report missing ones; with --fix-submodules, patch and
#            renormalize (idempotent marker block prevents double-insertion)
#   Phase 3: Summary — list all repos that need commit/push
# =============================================================================

set -euo pipefail

# Locale: fallback gracefully if en_US.UTF-8 not available (WSL minimal)
if locale -a 2>/dev/null | grep -qi 'en_us\.utf'; then
    export LANG="${LANG:-en_US.UTF-8}"
    export LC_ALL="${LC_ALL:-en_US.UTF-8}"
elif locale -a 2>/dev/null | grep -qi 'c\.utf'; then
    export LANG="${LANG:-C.UTF-8}"
    export LC_ALL="${LC_ALL:-C.UTF-8}"
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$(dirname "$SCRIPT_DIR")"
ROOT="$(dirname "$AGENTS_DIR")"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[1;30m'
WHITE='\033[1;37m'
BOLD='\033[1m'
NC='\033[0m'

# ── Flags ──
COMMIT=false
FIX_SUBMODULES=false
INCLUDE_VENDOR=false
RECURSIVE=true

for arg in "$@"; do
    case "$arg" in
        --commit)           COMMIT=true ;;
        --fix-submodules)   FIX_SUBMODULES=true ;;
        --include-vendor)   INCLUDE_VENDOR=true ;;
        --no-recursive)     RECURSIVE=false ;;
        --help|-h)
            sed -n '2,/^# ====/{ /^# ====/q; s/^# \?//; p; }' "$0"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown argument: $arg${NC}"
            echo "Run 'bash .agents/scripts/normalize-eol.sh --help' for usage."
            exit 1
            ;;
    esac
done

DRY_RUN=true
if $COMMIT; then DRY_RUN=false; fi

cd "$ROOT"

# =============================================================================
# Idempotent autotools CRLF fix block (appended to submodule .gitattributes)
# =============================================================================
AUTOTOOLS_BLOCK_START='# >>> normalize-eol autotools-crlf-fix >>>'
AUTOTOOLS_BLOCK_END='# <<< normalize-eol autotools-crlf-fix <<<'
AUTOTOOLS_BLOCK=$(cat <<'BLOCK'
# >>> normalize-eol autotools-crlf-fix >>>
# Added by normalize-eol.sh — prevents CRLF in autotools/configure scripts
# from breaking Linux/macOS/container builds. Idempotent: safe to re-run.
# Remove this block if your project has more specific rules.
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
BLOCK
)

# =============================================================================
# Utility functions
# =============================================================================

count_crlf() {
    local content
    content=$(cat 2>/dev/null) || true
    if [ -z "$content" ]; then echo 0; return; fi
    echo "$content" | tr -cd '\r' | wc -c | tr -d '[:space:]'
}

is_num() {
    case "$1" in ''|*[!0-9]*) return 1 ;; esac
    return 0
}

has_autotools_block() {
    # Check if .gitattributes already has our marker block
    local ga_file="$1"
    [ -f "$ga_file" ] && grep -qF "$AUTOTOOLS_BLOCK_START" "$ga_file" 2>/dev/null
}

has_autotools_rule() {
    # Check if .gitattributes has at least a rule for "configure" (the #1 offender)
    local ga_file="$1"
    if [ ! -f "$ga_file" ]; then return 1; fi
    # Match "configure" as a pattern (whole word, before "text" or "eol")
    grep -qE '^configure[[:space:]]' "$ga_file" 2>/dev/null
}

normalize_repo() {
    local repo_path="$1"
    local repo_label="$2"
    local -n result_ref="$3"  # associative array to return results

    echo -e "${GRAY}  Working in: $repo_path${NC}"
    pushd "$repo_path" >/dev/null

    # Count CRLF→LF changes after renormalize
    local crlf_to_lf=0
    local lf_to_crlf=0
    local other=0
    local staged_count=0
    local patched=false
    local patched_msg=""

    # Check if .gitattributes exists and needs patching
    local ga_file="$repo_path/.gitattributes"
    local need_patch=false
    if [ ! -f "$ga_file" ]; then
        need_patch=true
    elif ! has_autotools_block "$ga_file" && ! has_autotools_rule "$ga_file"; then
        need_patch=true
    fi

    if $need_patch && $FIX_SUBMODULES; then
        if [ ! -f "$ga_file" ]; then
            echo -e "    ${YELLOW}→ Creating .gitattributes with autotools rules${NC}"
            echo "* text=auto eol=lf" > "$ga_file"
            echo "" >> "$ga_file"
            echo "$AUTOTOOLS_BLOCK" >> "$ga_file"
        else
            echo -e "    ${YELLOW}→ Appending autotools-crlf-fix block to existing .gitattributes${NC}"
            echo "" >> "$ga_file"
            echo "$AUTOTOOLS_BLOCK" >> "$ga_file"
        fi
        git add .gitattributes 2>/dev/null || true
        patched=true
        patched_msg="patched .gitattributes"
    elif $need_patch; then
        # Dry-run: just report
        if [ ! -f "$ga_file" ]; then
            patched_msg="missing .gitattributes (use --fix-submodules to create)"
        else
            patched_msg="missing autotools rules (use --fix-submodules to add)"
        fi
    fi

    # Run renormalize. Optimization: in dry-run mode for submodules that aren't
    # being patched, skip the expensive renormalize — we only need to report
    # that .gitattributes is missing, not enumerate every CRLF file.
    local skip_renorm=false
    if $DRY_RUN && ! $FIX_SUBMODULES && [ "$repo_label" != "SpecWeave (main)" ]; then
        skip_renorm=true
    fi
    if ! $skip_renorm; then
        git add --renormalize . 2>/dev/null || true
    fi

    # Collect staged files
    local staged_files
    staged_files=$(git diff --cached --name-only 2>/dev/null)
    staged_count=$(echo "$staged_files" | grep -c . 2>/dev/null || echo "0")
    staged_count=$(echo "$staged_count" | tr -d '[:space:]')
    is_num "$staged_count" || staged_count=0

    # Count CRLF/LF changes
    if [ "$staged_count" -gt 0 ]; then
        for f in $staged_files; do
            if [ -f "$f" ]; then
                local before_crlf after_crlf
                before_crlf=$(git show "HEAD:$f" 2>/dev/null | count_crlf)
                after_crlf=$(git show ":$f" 2>/dev/null | count_crlf)
                is_num "$before_crlf" || before_crlf=0
                is_num "$after_crlf"  || after_crlf=0
                if [ "$before_crlf" -gt 0 ] && [ "$after_crlf" -eq 0 ]; then
                    crlf_to_lf=$((crlf_to_lf + 1))
                elif [ "$before_crlf" -eq 0 ] && [ "$after_crlf" -gt 0 ]; then
                    lf_to_crlf=$((lf_to_crlf + 1))
                else
                    other=$((other + 1))
                fi
            fi
        done
    fi

    popd >/dev/null

    # Return results via nameref
    result_ref["path"]="$repo_path"
    result_ref["label"]="$repo_label"
    result_ref["staged_count"]="$staged_count"
    result_ref["crlf_to_lf"]="$crlf_to_lf"
    result_ref["lf_to_crlf"]="$lf_to_crlf"
    result_ref["other"]="$other"
    result_ref["patched"]="$patched"
    result_ref["patched_msg"]="$patched_msg"
    result_ref["clean"]=false
    if [ "$staged_count" -eq 0 ] && [ -z "$patched_msg" ]; then
        result_ref["clean"]=true
    fi
}

print_repo_result() {
    local -n rr="$1"
    local indent="${2:-}"
    local label="${rr[label]}"
    local sc="${rr[staged_count]}"
    local c2l="${rr[crlf_to_lf]}"
    local l2c="${rr[lf_to_crlf]}"
    local oth="${rr[other]}"
    local patched="${rr[patched]}"
    local pmsg="${rr[patched_msg]}"

    if "${rr[clean]}"; then
        echo -e "${indent}${GREEN}✓${NC} $label — ${GREEN}clean${NC}"
        return
    fi

    echo -e "${indent}${YELLOW}●${NC} $label"
    if [ -n "$pmsg" ]; then
        if $patched; then
            echo -e "${indent}  ${GREEN}✎${NC} $pmsg"
        else
            echo -e "${indent}  ${YELLOW}⚠${NC} $pmsg"
        fi
    fi
    if [ "$sc" -gt 0 ]; then
        echo -e "${indent}  ${WHITE}$sc file(s) changed${NC}"
        local details=""
        [ "$c2l" -gt 0 ] && details="${details}CRLF→LF:$c2l "
        [ "$l2c" -gt 0 ] && details="${details}LF→CRLF:$l2c "
        [ "$oth" -gt 0 ] && details="${details}other:$oth"
        echo -e "${indent}  ${GRAY}$details${NC}"
    fi
}

# =============================================================================
# PHASE 1: Banner & main repo
# =============================================================================

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Line Ending Normalization (One-Click)${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GRAY}Mode: $($DRY_RUN && echo 'DRY RUN' || echo 'COMMIT')  |  Submodules: $($FIX_SUBMODULES && echo 'fix' || echo 'report only')  |  Vendor: $($INCLUDE_VENDOR && echo 'included' || echo 'skipped')${NC}"
echo -e "${GRAY}Root: $ROOT${NC}"
echo ""

# ── Step 1: Verify git repo ──
echo -e "${WHITE}[Phase 1] Main Repository${NC}"
echo -e "${YELLOW}[1/4] Verifying git repository...${NC}"
if ! git rev-parse --git-dir >/dev/null 2>&1; then
    echo -e "  ${RED}ERROR: Not a git repository${NC}"
    exit 1
fi
echo -e "  ${GREEN}OK${NC} — $(git remote get-url origin 2>/dev/null || echo 'local repo')"
echo ""

# ── Step 2: Verify .gitattributes ──
echo -e "${YELLOW}[2/4] Checking .gitattributes...${NC}"
GITATTRIBUTES="$ROOT/.gitattributes"
if [ ! -f "$GITATTRIBUTES" ]; then
    echo -e "  ${RED}ERROR: .gitattributes not found at repo root${NC}"
    echo -e "  ${YELLOW}Create .gitattributes first before running this script${NC}"
    exit 1
fi
LINE_COUNT=$(wc -l < "$GITATTRIBUTES" | tr -d '[:space:]')
echo -e "  ${GREEN}OK${NC} — $LINE_COUNT lines"
echo ""

# ── Step 3 & 4: Renormalize and collect results ──
echo -e "${YELLOW}[3/4] Running git add --renormalize . and collecting changes...${NC}"
declare -A MAIN_RESULT
normalize_repo "$ROOT" "SpecWeave (main)" MAIN_RESULT
echo -e "  ${GREEN}Done${NC}"
echo ""

# =============================================================================
# PHASE 2: Submodules
# =============================================================================
echo -e "${WHITE}[Phase 2] Submodules${NC}"

# Discover all submodules (direct + nested) using `git submodule status --recursive`
# Output format: <status><sha> <path> (<describe>)
#   status: '+' if checked out different commit, '-' if not initialized, ' ' if clean, 'U' merge conflicts
ALL_SUBMODULES=()
while IFS= read -r line; do
    [ -z "$line" ] && continue
    # Skip uninitialized submodules (start with '-')
    case "$line" in
        -*) continue ;;
    esac
    # Extract path (second field)
    sm_path=$(echo "$line" | awk '{print $2}')
    [ -z "$sm_path" ] && continue

    # Filter vendor/ (top-level) unless --include-vendor
    # Nested vendor/ under projects/ (e.g. projects/xuanspace/vendor/tvm-ffi) is first-party territory
    if ! $INCLUDE_VENDOR && [[ "$sm_path" == vendor/* ]]; then
        continue
    fi

    # If --no-recursive, skip nested submodules (contain more than one slash segment after a known submodule)
    # Simple heuristic: direct submodules have exactly one path component (no slash)
    # Actually, better: with --no-recursive, only include paths that are direct children
    if ! $RECURSIVE; then
        # Count slashes; direct submodules have exactly one path separator
        slash_count=$(echo "$sm_path" | tr -cd '/' | wc -c | tr -d '[:space:]')
        if [ "$slash_count" -gt 1 ]; then
            continue
        fi
    fi

    ALL_SUBMODULES+=("$ROOT/$sm_path")
done < <(git submodule status --recursive 2>/dev/null || true)
TOTAL_SUBMODULES=${#ALL_SUBMODULES[@]}
SUBMODULE_RESULTS=()
SUBMODULE_NEEDS_COMMIT=()

if [ "$TOTAL_SUBMODULES" -eq 0 ]; then
    echo -e "  ${GRAY}No submodules found.${NC}"
else
    echo -e "${YELLOW}  Scanning $TOTAL_SUBMODULES submodule(s)...${NC}"
    echo ""

    for sm_abs in "${ALL_SUBMODULES[@]}"; do
        # Convert to relative path for labeling and classification
        rel_path="${sm_abs#$ROOT/}"
        sm_label="$rel_path"

        # Classify type based on top-level directory
        sm_type="nested"
        case "$rel_path" in
            projects/*)
                sm_type="first-party"
                ;;
            vendor/*)
                sm_type="third-party"
                ;;
        esac

        # Skip uninitialized submodules
        if [ ! -d "$sm_abs/.git" ] && [ ! -f "$sm_abs/.git" ]; then
            echo -e "  ${GRAY}⊘ $sm_label — not initialized (skip)${NC}"
            continue
        fi

        declare -A SM_RESULT
        normalize_repo "$sm_abs" "$sm_label ($sm_type)" SM_RESULT
        SUBMODULE_RESULTS+=("$sm_label")

        # Store results in global vars using eval trick (sanitize key for shell variable names)
        key=$(echo "$rel_path" | sed 's/[^a-zA-Z0-9]/_/g')
        eval "SM_${key}_staged_count=${SM_RESULT[staged_count]}"
        eval "SM_${key}_crlf_to_lf=${SM_RESULT[crlf_to_lf]}"
        eval "SM_${key}_lf_to_crlf=${SM_RESULT[lf_to_crlf]}"
        eval "SM_${key}_other=${SM_RESULT[other]}"
        eval "SM_${key}_patched=${SM_RESULT[patched]}"
        eval "SM_${key}_patched_msg='${SM_RESULT[patched_msg]}'"
        eval "SM_${key}_clean=${SM_RESULT[clean]}"

        if ! ${SM_RESULT[clean]}; then
            SUBMODULE_NEEDS_COMMIT+=("$rel_path")
        fi
    done

    echo ""
fi

# =============================================================================
# PHASE 3: Summary & commit
# =============================================================================
echo -e "${WHITE}[Phase 3] Summary${NC}"
echo ""

# Print main repo result
print_repo_result MAIN_RESULT
echo ""

# Print submodule results
if [ "$TOTAL_SUBMODULES" -gt 0 ]; then
    echo -e "${GRAY}── Submodules ──${NC}"
    for sm_abs in "${ALL_SUBMODULES[@]}"; do
        rel_path="${sm_abs#$ROOT/}"
        key=$(echo "$rel_path" | sed 's/[^a-zA-Z0-9]/_/g')

        # Skip uninitialized
        if [ ! -d "$sm_abs/.git" ] && [ ! -f "$sm_abs/.git" ]; then
            echo -e "  ${GRAY}⊘ $rel_path — not initialized${NC}"
            continue
        fi

        # Reconstruct result
        declare -A SR
        SR["label"]="$rel_path"
        eval "SR[staged_count]=\$SM_${key}_staged_count"
        eval "SR[crlf_to_lf]=\$SM_${key}_crlf_to_lf"
        eval "SR[lf_to_crlf]=\$SM_${key}_lf_to_crlf"
        eval "SR[other]=\$SM_${key}_other"
        eval "SR[patched]=\$SM_${key}_patched"
        eval "SR_pm=\$SM_${key}_patched_msg"
        SR["patched_msg"]="$SR_pm"
        eval "SR[clean]=\$SM_${key}_clean"

        print_repo_result SR "  "
    done
    echo ""
fi

# ── Commit main repo if requested ──
MAIN_STAGED=${MAIN_RESULT[staged_count]}
MAIN_CLEAN=${MAIN_RESULT[clean]}

if ! $MAIN_CLEAN && $COMMIT; then
    echo -e "${YELLOW}Committing main repo changes...${NC}"

    COMMIT_MSG="chore(git): normalize line endings across repo and submodules

Normalize line endings to conform to .gitattributes rules.
Key fixes:
- Autotools scripts (configure, config.sub, *.ac, *.am, *.in) → LF
- Shell scripts, Python, C/C++, CMake, Makefiles → LF
- PowerShell/Batch files → CRLF
- Binary files marked as binary (no conversion)
- Submodule .gitattributes patched with autotools-crlf-fix block (where applicable)

Generated by: .agents/scripts/normalize-eol.sh --commit"

    git commit -m "$COMMIT_MSG"
    echo -e "  ${GREEN}Committed as $(git rev-parse --short HEAD)${NC}"
    echo ""
elif ! $MAIN_CLEAN && $DRY_RUN; then
    echo -e "${CYAN}========================================${NC}"
    echo -e "${YELLOW}DRY RUN — no changes committed${NC}"
    echo -e "${CYAN}========================================${NC}"
    echo ""
    echo -e "To commit main repo changes:"
    echo -e "  ${BOLD}bash .agents/scripts/normalize-eol.sh --commit${NC}"
    echo ""
    if [ ${#SUBMODULE_NEEDS_COMMIT[@]} -gt 0 ]; then
        echo -e "${YELLOW}Submodules with pending changes (need manual commit + push):${NC}"
        for sm in "${SUBMODULE_NEEDS_COMMIT[@]}"; do
            echo -e "  cd $sm && git add -A && git commit -m \"chore(git): fix CRLF line endings\" && git push"
        done
        echo ""
        if ! $FIX_SUBMODULES; then
            echo -e "To also patch submodule .gitattributes and renormalize:"
            echo -e "  ${BOLD}bash .agents/scripts/normalize-eol.sh --fix-submodules${NC}"
            echo ""
        fi
    fi
    echo -e "${GRAY}To undo ALL staging (main repo + submodules):${NC}"
    echo -e "  git submodule foreach --recursive 'git reset HEAD 2>/dev/null || true'"
    echo -e "  git reset HEAD"
    echo ""
    exit 0
fi

# ── Final success message (after commit) ──
echo -e "${CYAN}========================================${NC}"
if $MAIN_CLEAN && [ ${#SUBMODULE_NEEDS_COMMIT[@]} -eq 0 ]; then
    echo -e "${GREEN}All line endings are already correct — nothing to fix!${NC}"
else
    echo -e "${GREEN}Main repo normalization complete.${NC}"
    if [ ${#SUBMODULE_NEEDS_COMMIT[@]} -gt 0 ]; then
        echo ""
        echo -e "${YELLOW}⚠ Submodules with pending changes (need manual commit + push):${NC}"
        for sm in "${SUBMODULE_NEEDS_COMMIT[@]}"; do
            echo -e "  ${BOLD}cd $sm${NC}"
            echo -e "  git add -A && git commit -m \"chore(git): fix CRLF line endings for autotools\" && git push"
        done
        echo ""
        echo -e "${GRAY}After pushing submodules, return to main repo and update gitlinks:${NC}"
        echo -e "  git add ${SUBMODULE_NEEDS_COMMIT[*]}"
        echo -e "  git commit -m \"chore(git): update submodules after CRLF normalization\""
    fi
fi
echo -e "${CYAN}========================================${NC}"
