#!/usr/bin/env bash
# =============================================================================
# secure-gitignore.sh — 自动配置 .gitignore 防止敏感配置误提交
# =============================================================================
# 功能：
#   1. 将敏感文件模式添加到 .gitignore（幂等，支持重复执行）
#   2. 检测已被 git 跟踪的敏感文件并发出警告
#   3. 扫描 .env 文件中的敏感键名（PASSWORD/TOKEN/SECRET/KEY 等）
#   4. --check 模式用于 CI 门禁（发现问题返回非零退出码）
#
# 用法：
#   bash scripts/secure-gitignore.sh          # 配置 .gitignore
#   bash scripts/secure-gitignore.sh --check  # CI 检查模式（不修改文件）
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
GITIGNORE="${PROJECT_DIR}/.gitignore"
CHECK_MODE=false

# ─── 颜色输出 ────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

ok()   { echo -e "  ${GREEN}[OK]${NC} $*"; }
warn() { echo -e "  ${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "  ${RED}[FAIL]${NC} $*"; }
info() { echo -e "  ${BLUE}[INFO]${NC} $*"; }
header() { echo -e "\n${BOLD}── $* ──${NC}"; }

# ─── 参数解析 ────────────────────────────────────────────────────────────────
for arg in "$@"; do
    case "$arg" in
        --check|-c) CHECK_MODE=true ;;
        --help|-h)
            echo "Usage: $0 [--check]"
            echo "  --check    CI check mode (read-only, exit non-zero on issues)"
            exit 0
            ;;
        *)
            echo "Unknown option: $arg"
            exit 1
            ;;
    esac
done

cd "$PROJECT_DIR"

# ─── 敏感文件/目录模式定义 ───────────────────────────────────────────────────
# 格式：每行一个 gitignore pattern
# 注意：顺序重要 - 先忽略，再用 ! 排除白名单
SENSITIVE_PATTERNS=$(cat <<'PATTERNS'
# ─── Environment files (contain passwords, tokens, keys) ───
.env
.env.dev
.env.local
.env.*.local
.env.*.bak
.env.*.old
.env.prod
.env.staging
.env.production
.env.development.local

# ─── SSH private keys & credentials ───
*.pem
*.key
id_rsa
id_rsa.*
id_ed25519
id_ed25519.*
id_ecdsa
id_ecdsa.*
*.sec
credentials
*.credentials

# ─── Docker/container secrets ───
docker-compose.override.yml
docker-compose.*.local.yml

# ─── White-list: safe files that SHOULD be tracked ───
!*.pub
!*.pem.example
!*.key.example
!.env.example
!.env.dev.example
!.env.ide.example
PATTERNS
)

# 标记区域起止（幂等性保障）
MARKER_START="# >>> security-secrets (auto-managed by scripts/secure-gitignore.sh) >>>"
MARKER_END="# <<< security-secrets (auto-managed) <<<"

# ─── 敏感键名关键词（不要求完整键名匹配，键名包含任一关键词即视为敏感）───
# 注意：不要在关键词中加前缀（如用PUBLIC_KEY而非SSH_PUBLIC_KEY），避免正则前缀贪婪吞掉前缀后不匹配
SENSITIVE_KEY_WORDS='PASSWORD|TOKEN|SECRET|PRIVATE_KEY|PUBLIC_KEY|API_KEY|ACCESS_KEY|AUTH|CREDENTIAL'
# 匹配: KEY=value 行（KEY含敏感词），不匹配注释(#开头)、URL参数(?token=)
SENSITIVE_KEY_REGEX="^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*(${SENSITIVE_KEY_WORDS})[A-Za-z0-9_]*[[:space:]]*="
ISSUES_FOUND=0

# =============================================================================
# Step 1: 检查 .gitignore 是否存在
# =============================================================================
header "Step 1: Checking .gitignore"

if [ ! -f "$GITIGNORE" ]; then
    if $CHECK_MODE; then
        fail ".gitignore not found at $GITIGNORE"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        info "Creating .gitignore"
        touch "$GITIGNORE"
    fi
else
    ok ".gitignore exists"
fi

# =============================================================================
# Step 2: 更新 .gitignore（非check模式）
# =============================================================================
header "Step 2: Managing .gitignore security section"

update_gitignore() {
    local tmpfile
    tmpfile=$(mktemp)

    # 如果已有标记区域，删除旧区域内容（使用awk按固定字符串匹配，避免正则转义问题）
    if grep -qF "${MARKER_START}" "$GITIGNORE" 2>/dev/null; then
        awk -v start="${MARKER_START}" -v end="${MARKER_END}" '
            $0 == start { skip=1; next }
            $0 == end { skip=0; next }
            !skip { print }
        ' "$GITIGNORE" > "$tmpfile"
        info "Replacing existing security section"
    else
        cp "$GITIGNORE" "$tmpfile"
        # 确保文件末尾有换行
        [ -s "$tmpfile" ] && [ "$(tail -c1 "$tmpfile" | wc -l)" -eq 0 ] && echo "" >> "$tmpfile"
        info "Adding new security section"
    fi

    # 写入新的标记区域
    cat >> "$tmpfile" <<SECTION
${MARKER_START}
${SENSITIVE_PATTERNS}
${MARKER_END}
SECTION

    # 备份原文件
    cp "$GITIGNORE" "${GITIGNORE}.bak.$(date +%Y%m%d%H%M%S)" 2>/dev/null || true

    mv "$tmpfile" "$GITIGNORE"
    ok ".gitignore security section updated"
}

check_gitignore() {
    local missing=0
    # 提取所有应该忽略的模式（排除注释和空行和白名单）
    while IFS= read -r pattern; do
        # 跳过空行、注释、白名单
        [[ -z "$pattern" || "$pattern" =~ ^# || "$pattern" =~ ^! ]] && continue
        # 清理模式中的空白
        pattern=$(echo "$pattern" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        [[ -z "$pattern" ]] && continue

        # 检查模式是否在.gitignore中
        # 用grep -F检查精确匹配（不使用正则，避免特殊字符问题）
        if ! grep -qF -- "$pattern" "$GITIGNORE" 2>/dev/null; then
            fail "Missing pattern in .gitignore: $pattern"
            missing=$((missing + 1))
        fi
    done <<< "$SENSITIVE_PATTERNS"

    if [ "$missing" -eq 0 ]; then
        ok "All required patterns present in .gitignore"
    else
        ISSUES_FOUND=$((ISSUES_FOUND + missing))
    fi
}

if $CHECK_MODE; then
    check_gitignore
else
    update_gitignore
fi

# =============================================================================
# Step 3: 检测已被 git 跟踪的敏感文件
# =============================================================================
header "Step 3: Checking for already-tracked sensitive files"

check_tracked_files() {
    local tracked_found=0

    # 检查是否在git仓库中
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        info "Not inside a git repository, skipping tracked-files check"
        return
    fi

    # 检查常见敏感文件是否已被跟踪
    local sensitive_files=(
        ".env"
        ".env.dev"
        ".env.local"
        ".env.prod"
        "*.pem"
        "id_rsa"
        "id_ed25519"
    )

    for pattern in "${sensitive_files[@]}"; do
        # 用git ls-files查找匹配pattern的已跟踪文件
        while IFS= read -r tracked; do
            [ -z "$tracked" ] && continue
            # 跳过白名单文件
            case "$tracked" in
                *.pub|*.example|*.example.*) continue ;;
            esac
            if $CHECK_MODE; then
                fail "Sensitive file is tracked by git: $tracked (run 'git rm --cached $tracked' to untrack)"
                tracked_found=$((tracked_found + 1))
            else
                warn "Sensitive file is tracked by git: $tracked"
                warn "  → Run: git rm --cached $tracked  (then commit)"
            fi
        done < <(git ls-files -- "$pattern" 2>/dev/null || true)
    done

    # 也检查所有可能包含敏感键名的已跟踪.env类文件
    while IFS= read -r envfile; do
        [ -z "$envfile" ] && continue
        # 跳过example文件
        [[ "$envfile" == *.example ]] && continue
        if grep -qE "$SENSITIVE_KEY_REGEX" "$envfile" 2>/dev/null; then
            if $CHECK_MODE; then
                fail "Tracked env file contains sensitive keys: $envfile"
                tracked_found=$((tracked_found + 1))
            else
                warn "Tracked env file contains sensitive keys: $envfile"
                warn "  → If this is a template, move keys to .env.dev"
            fi
        fi
    done < <(git ls-files -- '.env*' 2>/dev/null || true)

    if [ "$tracked_found" -eq 0 ]; then
        ok "No sensitive files tracked by git"
    else
        ISSUES_FOUND=$((ISSUES_FOUND + tracked_found))
    fi
}

check_tracked_files

# =============================================================================
# Step 4: 扫描 .env 文件中的敏感配置
# =============================================================================
header "Step 4: Scanning .env files for sensitive keys"

scan_env_files() {
    local env_files_scanned=0
    local env_issues=0

    for envfile in .env .env.dev .env.local; do
        if [ -f "$envfile" ]; then
            env_files_scanned=$((env_files_scanned + 1))
            local sensitive_count
            sensitive_count=$(grep -cE "$SENSITIVE_KEY_REGEX" "$envfile" 2>/dev/null || echo 0)
            if [ "$sensitive_count" -gt 0 ]; then
                info "$envfile contains $sensitive_count sensitive key(s):"
                grep -nE "$SENSITIVE_KEY_REGEX" "$envfile" 2>/dev/null | while IFS=: read -r lineno line; do
                    # 只显示键名，隐藏值
                    local key
                    key=$(echo "$line" | sed 's/=.*//' | sed 's/^[[:space:]]*//')
                    echo -e "    ${YELLOW}Line $lineno${NC}: $key = ***"
                done
                env_issues=$((env_issues + sensitive_count))
            fi
        fi
    done

    if [ "$env_files_scanned" -gt 0 ]; then
        ok "Scanned $env_files_scanned .env file(s)"
        if [ "$env_issues" -gt 0 ]; then
            if $CHECK_MODE; then
                warn "$env_issues sensitive key(s) found in .env files (this is expected, ensure .gitignore covers them)"
            else
                info "$env_issues sensitive key(s) found — make sure these files are in .gitignore"
            fi
        fi
    else
        info "No local .env files found to scan"
    fi
}

scan_env_files

# =============================================================================
# Step 5: 验证 .gitignore 模式实际生效（用 git check-ignore）
# =============================================================================
header "Step 5: Verifying .gitignore patterns are effective"

verify_ignore_patterns() {
    if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        info "Not inside a git repository, skipping pattern verification"
        return
    fi

    local test_files=(".env" ".env.dev" ".env.local" "id_rsa" "test.pem" "secret.key")
    local not_ignored=0
    local created_files=()

    for tf in "${test_files[@]}"; do
        local test_path="${PROJECT_DIR}/${tf}"
        # 只在文件不存在时创建测试文件，避免误删真实文件
        local existed=true
        if [ ! -e "$test_path" ]; then
            touch "$test_path" 2>/dev/null || true
            created_files+=("$test_path")
            existed=false
        fi
        if git check-ignore -q "$test_path" 2>/dev/null; then
            ok "Pattern effective: $tf → ignored"
        else
            case "$tf" in
                *.pub|*.example) ;;
                *)
                    fail "File NOT ignored by git: $tf (check .gitignore syntax)"
                    not_ignored=$((not_ignored + 1))
                    ;;
            esac
        fi
    done

    # 只清理我们创建的临时文件，不动已存在的真实文件
    for cf in "${created_files[@]}"; do
        rm -f "$cf" 2>/dev/null || true
    done

    # 验证白名单文件不被忽略（使用不会冲突的临时文件名）
    local whitelist_test="${PROJECT_DIR}/.__gitignore_test_whitelist__.pub"
    touch "$whitelist_test" 2>/dev/null || true
    if git check-ignore -q "$whitelist_test" 2>/dev/null; then
        fail "Public key (*.pub) should NOT be ignored but is"
        whitelist_ok=false
    else
        ok "Whitelist effective: *.pub → NOT ignored (safe to commit)"
    fi
    rm -f "$whitelist_test" 2>/dev/null || true

    if [ "$not_ignored" -gt 0 ]; then
        ISSUES_FOUND=$((ISSUES_FOUND + not_ignored))
    fi
}

verify_ignore_patterns

# =============================================================================
# 总结
# =============================================================================
header "Summary"

if $CHECK_MODE; then
    if [ "$ISSUES_FOUND" -gt 0 ]; then
        echo -e "\n  ${RED}${BOLD}❌ $ISSUES_FOUND issue(s) found — fix before committing!${NC}"
        echo ""
        echo "  Quick fix:"
        echo "    bash scripts/secure-gitignore.sh"
        echo "    git rm --cached <sensitive-file>  # for any tracked sensitive files"
        echo ""
        exit 1
    else
        echo -e "\n  ${GREEN}${BOLD}✅ All security checks passed!${NC}"
        exit 0
    fi
else
    if [ "$ISSUES_FOUND" -gt 0 ]; then
        echo -e "\n  ${YELLOW}${BOLD}⚠️  $ISSUES_FOUND warning(s) — review above, then commit .gitignore changes${NC}"
    else
        echo -e "\n  ${GREEN}${BOLD}✅ .gitignore security configuration complete!${NC}"
    fi
    echo ""
    echo "  Next steps if sensitive files are tracked:"
    echo "    git rm --cached .env.dev    # untrack (file stays on disk)"
    echo "    git add .gitignore"
    echo "    git commit -m 'security: add sensitive files to .gitignore'"
    echo ""
    exit 0
fi
