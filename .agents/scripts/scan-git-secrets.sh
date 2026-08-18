#!/usr/bin/env bash
# =============================================================================
# scan-git-secrets.sh — 全仓库 Git 敏感文件审计脚本
# =============================================================================
# 扫描整个项目（含 submodule），确认是否有敏感文件/内容被意外提交到 git。
#
# 检测维度：
#   1. 已跟踪的敏感文件名（.env*, id_rsa, *.pem, credentials 等）
#   2. 已跟踪文件中的敏感内容（硬编码密钥/密码/令牌）
#   3. 工作区中存在但未被跟踪且未被忽略的敏感文件（提醒级别）
#   4. Git 历史中的敏感文件（--history 选项，慢速）
#
# 用法：
#   bash .agents/scripts/scan-git-secrets.sh              # 扫描根仓库
#   bash .agents/scripts/scan-git-secrets.sh --all        # 包含所有 submodule
#   bash .agents/scripts/scan-git-secrets.sh --history    # 额外扫描 git 历史
#
# 退出码：0=干净 1=发现已跟踪泄露 2=仅提醒级别问题
# =============================================================================

set -uo pipefail

# ─── 颜色 ──────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'
BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

header()  { echo -e "\n${BLUE}── $* ──${NC}"; }
ok()      { echo -e "  ${GREEN}[OK]${NC} $*"; }
warn()    { echo -e "  ${YELLOW}[WARN]${NC} $*"; }
fail()    { echo -e "  ${RED}[FAIL]${NC} $*"; }
section() { echo -e "\n${BOLD}${BLUE}════ $* ════${NC}"; }

# ─── 参数解析 ─────────────────────────────────────────────────────────────
SCAN_SUBMODULES=false
SCAN_HISTORY=false
while [[ $# -gt 0 ]]; do
    case "$1" in
        --all|-a)     SCAN_SUBMODULES=true; shift ;;
        --history|-H) SCAN_HISTORY=true; shift ;;
        --help|-h)
            sed -n '2,20p' "$0"; exit 0 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

# ─── 定位项目根 ────────────────────────────────────────────────────────────
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

# ─── 计数器（临时文件避免子shell问题）─────────────────────────────────────
CF="$(mktemp)"
trap 'rm -f "$CF" "$CF".*' EXIT
init_cf() {
    cat > "$CF" <<'EOF'
repos=0
p1=0
p2=0
p3=0
p4=0
files=0
EOF
}
inc() {
    local k="$1" n="${2:-1}"
    local cur
    cur="$(grep "^${k}=" "$CF" | cut -d= -f2)"
    grep -v "^${k}=" "$CF" > "$CF.tmp"
    echo "${k}=$((cur + n))" >> "$CF.tmp"
    mv "$CF.tmp" "$CF"
}
cnt() { grep "^$1=" "$CF" | cut -d= -f2; }

# ─── 文件名模式 ────────────────────────────────────────────────────────────
HIGH_RISK_GLOBS=(
    '.env' '.env.local' '.env.dev' '.env.prod' '.env.production'
    '.env.staging' '.env.development' '.env.test'
    'id_rsa' 'id_ed25519' 'id_ecdsa' 'id_dsa'
    '*.pem' '*.key' '*.p12' '*.pfx' '*.jks' '*.keystore'
    '*.ovpn' '*.htpasswd' '*.sec' '.netrc' '_netrc' '.npmrc'
    'credentials' 'credentials.json' '*.credentials'
    'secrets.json' 'secrets.yaml' 'secrets.yml' 'secrets.toml'
    'service-account*.json'
    '*_rsa' '*_dsa' '*_ed25519' '*_ecdsa'
    '.dockercfg' 'docker-compose.override.yml'
)
WHITELIST_GLOBS=(
    '*.example' '*.sample' '*.template' '*.dist' '*.pub'
)

# glob→grep -E 正则（匹配路径末段）
g2re() {
    local g="$1"
    g="${g//./\.}"; g="${g//\?/[^/]}"; g="${g//\*/[^/]*}"
    echo "(^|/)$g\$"
}

is_whitelisted() {
    local base="${1##*/}"
    for w in "${WHITELIST_GLOBS[@]}"; do
        # shellcheck disable=SC2254
        case "$base" in $w) return 0;; esac
    done
    # 排除.example/.sample等结尾的通用白名单
    case "$base" in
        *.example|*.sample|*.template|*.dist|*.pub) return 0;;
    esac
    return 1
}

# 检查值是否是占位符/非硬编码值（安全）
is_safe_value() {
    local v="$1"
    # 去引号
    v="${v#\"}"; v="${v%\"}"; v="${v#\'}"; v="${v%\'}"; v="${v#\`}"; v="${v%\`}"
    # 去首尾空白
    v="$(echo "$v" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    # 空值
    [[ -z "$v" ]] && return 0
    # shell/python 变量引用/命令替换（动态值，非硬编码）
    [[ "$v" == \${* ]] && return 0
    [[ "$v" == \$[A-Za-z_]* ]] && return 0
    # 值任意位置含shell命令替换 $(...) 或反引号 `...`
    if echo "$v" | grep -qE '\$\(|`'; then
        return 0
    fi
    # 含shell变量引用（$VAR/$0/$1等）
    if echo "$v" | grep -qE '\$\{?[A-Za-z_][A-Za-z0-9_]*\}?|\$[0-9@#?!*$_-]'; then
        return 0
    fi
    [[ "$v" == os.* ]] && return 0
    [[ "$v" == *os.environ* ]] && return 0
    [[ "$v" == *os.getenv* ]] && return 0
    # 占位符 <...>
    [[ "$v" == \<*\> ]] && return 0
    # 全星号/全点/全横线
    [[ "$v" =~ ^[*.:/_-]+$ ]] && return 0
    # 含中文字符（文档注释，不是密钥）
    if echo "$v" | grep -qP '[\x{4e00}-\x{9fff}]' 2>/dev/null; then
        return 0
    fi
    # 明显的示例值（xx结尾、含xxx、含example/demo/placeholder）
    local vl
    vl="$(echo "$v" | tr '[:upper:]' '[:lower:]')"
    # 精确匹配已知占位符单词
    case "$vl" in
        xxx|changeme|password|placeholder|none|null|todo|fixme|example|sample|test|demo|dummy|mock|empty|secret|default|true|false|yes|no|0|1) return 0;;
    esac
    [[ "$vl" == your* ]] && return 0
    [[ "$vl" == *example* ]] && return 0
    [[ "$vl" == *placeholder* ]] && return 0
    [[ "$vl" == *changeme* ]] && return 0
    [[ "$vl" == xxxxx* ]] && return 0
    [[ "$vl" == *xxxx ]] && return 0
    # 值长度小于8（太短不可能是有效密钥）
    [[ ${#v} -lt 8 ]] && return 0
    # 以单/双引号包裹的短字符串（如 "one-api"、"dev123"）可能是配置项名而非密钥
    # 但密码可能很短... 交给键名白名单处理
    return 1
}

# 检查键名是否是非敏感的配置键（不应报警）
is_safe_key() {
    local k="$1"
    local kl
    kl="$(echo "$k" | tr '[:upper:]' '[:lower:]')"
    # 密码/密钥相关的长度/策略/过期/正则/URL类配置
    case "$kl" in
        *password*length*|*password*policy*|*password*expir*|*password*iter*|*password*hash*) return 0;;
        *token*expir*|*token*expiry*|*token*length*|*refreshtoken*expir*) return 0;;
        *secret*length*|*key*length*|*key*rotation*|*key*expir*) return 0;;
        *auth*url*|*oauth*url*|*token*url*) return 0;;
        *regex*|*pattern*|*re_*) return 0;;
        max_password_length|refresh_token_expiry_days|access_token_expiry_minutes) return 0;;
    esac
    return 1
}

# =============================================================================
# 内容扫描核心：用 awk 解析 git grep 输出，智能过滤误报
# =============================================================================
scan_content_in_repo() {
    local pfx="$1"
    local hits_file="$2"

    # KEY=value 模式（grep -nE，输出 filename:lineno:line）
    # 排除二进制文件、排除.example文件（白名单）
    for pat_file_pattern in '*.py' '*.js' '*.ts' '*.tsx' '*.jsx' '*.sh' '*.bash' '*.ps1' '*.bat' '*.env' '*.json' '*.yaml' '*.yml' '*.toml' '*.ini' '*.cfg' '*.conf' '*.tf' 'Dockerfile*' '.env*'; do
        git grep -n -E '^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*(PASSWORD|PASSWD|PWD|TOKEN|SECRET|PRIVATE_KEY|PUBLIC_KEY|API_KEY|ACCESS_KEY|CREDENTIAL|CONNECTION_STRING|DB_PASS|DATABASE_URL|MONGO_URI|REDIS_URL|MYSQL_PWD|PGPASSWORD|JWT_SECRET|SIGNING_KEY|ENCRYPTION_KEY|WEBHOOK_SECRET)[A-Za-z0-9_]*[[:space:]]*[=:][[:space:]]*[^#[:space:]]' -- "$pat_file_pattern" 2>/dev/null || true
    done | grep -v '^Binary file' \
      | grep -v '\.example:' \
      | grep -v '\.sample:' \
      | grep -v '\.dist:' \
      | while IFS= read -r line; do
        # 用awk解析filename:lineno:content（content可含冒号）
        fname="${line%%:*}"
        rest="${line#*:}"
        lineno="${rest%%:*}"
        content="${rest#*:}"

        # 跳过注释行
        trimmed="${content#"${content%%[![:space:]]*}"}"
        case "$trimmed" in
            \#*|//*|/\**|--*) continue;;
        esac

        # 提取键名
        key="$(echo "$content" | sed -n 's/^[[:space:]]*\([A-Za-z_][A-Za-z0-9_]*\)[[:space:]]*[=:].*/\1/p')"
        [[ -z "$key" ]] && continue

        # 检查键名是否安全（非敏感配置键）
        if is_safe_key "$key"; then continue; fi

        # 提取值
        val="$(echo "$content" | sed -n 's/^[[:space:]]*[A-Za-z_][A-Za-z0-9_]*[[:space:]]*[=:][[:space:]]*//p' | sed 's/[[:space:]]*#.*//;s/[[:space:]]*\\$//;s/[[:space:]]*$//')"
        # 去除值末尾可能的注释
        val="$(echo "$val" | sed 's/[[:space:]]*#.*//')"

        # 检查值是否安全/占位符
        if is_safe_value "$val"; then continue; fi

        # 显示值脱敏
        local dv label
        if [[ ${#val} -gt 8 ]]; then
            dv="${val:0:2}***${val: -2}"
        else
            dv="***"
        fi
        # DEFAULT_开头的键是默认配置值；apps/docker-images/下的镜像构建脚本中的PASSWORD/TOKEN也是公开默认值
        local is_default=false
        if [[ "$key" == DEFAULT_* ]]; then
            is_default=true
        elif [[ "$fname" == apps/docker-images/* ]] && [[ "$key" =~ (PASSWORD|TOKEN|SECRET) ]]; then
            # Docker镜像构建脚本中的默认开发密码/token是设计公开的
            local vtest="$val"
            vtest="${vtest#\"}"; vtest="${vtest%\"}"; vtest="${vtest#\'}"; vtest="${vtest%\'}"
            # 值是简单的字母数字连字符组合（弱密码/默认值），长度<20
            if [[ ${#vtest} -lt 20 ]] && echo "$vtest" | grep -qE '^[a-zA-Z0-9_-]+$'; then
                is_default=true
            fi
        fi
        if $is_default; then
            label="DEFAULT_VALUE"
        else
            label="HARDCODED"
        fi
        echo "${fname}:${lineno}:${pfx}${fname}:${lineno}:${label} ${key} = ${dv}"
    done >> "$hits_file"

    # 私钥PEM头（任何文件都检测）
    git grep -n -E '-----BEGIN[[:space:]](RSA[[:space:]]|EC[[:space:]]|DSA[[:space:]]|OPENSSH[[:space:]]|PGP[[:space:]])?PRIVATE[[:space:]]KEY-----' 2>/dev/null \
        | grep -v '^Binary file' \
        | grep -v '\.example:' \
        | while IFS= read -r line; do
        fname="${line%%:*}"; rest="${line#*:}"; lineno="${rest%%:*}"
        echo "${fname}:${lineno}:${pfx}${fname}:${lineno}:CRITICAL: PRIVATE KEY BLOCK"
    done >> "$hits_file"

    # AWS Access Key ID（排除AWS官方示例key: AKIAIOSFODNN7EXAMPLE 和以EXAMPLE结尾的示例key）
    git grep -n -E 'AKIA[0-9A-Z]{16}' 2>/dev/null \
        | grep -v '^Binary file' \
        | grep -v '\.example:' \
        | grep -v 'EXAMPLE' \
        | while IFS= read -r line; do
        fname="${line%%:*}"; rest="${line#*:}"; lineno="${rest%%:*}"
        echo "${fname}:${lineno}:${pfx}${fname}:${lineno}:HIGH: AWS Access Key ID"
    done >> "$hits_file"

    # GitHub PAT (classic)
    git grep -n -E 'gh[pousr]_[A-Za-z0-9_]{36,}' 2>/dev/null \
        | grep -v '^Binary file' \
        | grep -v '\.example:' \
        | while IFS= read -r line; do
        fname="${line%%:*}"; rest="${line#*:}"; lineno="${rest%%:*}"
        echo "${fname}:${lineno}:${pfx}${fname}:${lineno}:HIGH: GitHub Personal Access Token"
    done >> "$hits_file"
}

# =============================================================================
# 扫描单个仓库
# =============================================================================
scan_repo() {
    local repo_path="$1" repo_name="$2" is_sub="${3:-false}"
    inc repos 1
    local pfx=""
    $is_sub && pfx="  [sub] "

    section "Scanning: $repo_name"
    cd "$repo_path" || { fail "Cannot enter $repo_path"; return; }

    local tracked_list
    tracked_list="$(git ls-files 2>/dev/null)"
    local total_files
    total_files="$(echo "$tracked_list" | wc -l)"
    inc files "$total_files"

    # ─── Phase 1: 已跟踪敏感文件名 ──────────────────────────────────────
    header "Phase 1: Tracked sensitive filenames"
    local p1=0
    for g in "${HIGH_RISK_GLOBS[@]}"; do
        while IFS= read -r f; do
            [[ -z "$f" ]] && continue
            is_whitelisted "$f" && continue
            fail "${pfx}HIGH: $f  (sensitive file tracked by git!)"
            echo "       → Fix: git rm --cached $f && git commit"
            p1=$((p1 + 1))
        done < <(echo "$tracked_list" | grep -E -- "$(g2re "$g")" || true)
    done
    # config/settings 类文件（中风险）—— 这里只列特别危险的命名，不包含普通config.json
    for mg in 'secrets.json' 'secrets.yaml' 'secrets.yml' 'secrets.toml' 'credentials.json'; do
        while IFS= read -r f; do
            [[ -z "$f" ]] && continue
            is_whitelisted "$f" && continue
            warn "${pfx}MEDIUM: $f  (credential file tracked — verify contents)"
            p1=$((p1 + 1))
        done < <(echo "$tracked_list" | grep -E -- "$(g2re "$mg")" || true)
    done
    [[ $p1 -eq 0 ]] && ok "No sensitive filenames tracked"
    inc p1 $p1

    # ─── Phase 2: 已跟踪文件中的敏感内容 ────────────────────────────────
    header "Phase 2: Sensitive content in tracked files"
    local p2=0
    local hits
    hits="$(mktemp)"
    scan_content_in_repo "$pfx" "$hits"
    if [[ -s "$hits" ]]; then
        # 去重
        sort -u "$hits" -o "$hits"
        local total_hits
        total_hits=$(wc -l < "$hits")
        p2=0
        while IFS= read -r hit; do
            msg="${hit#*:*:}"
            # DEFAULT_VALUE 类是默认配置值（如Docker镜像默认密码），降级为WARN
            if [[ "$msg" == *"DEFAULT_VALUE"* ]]; then
                warn "$msg  (default value — verify it is intentional)"
            else
                fail "$msg"
                p2=$((p2 + 1))
            fi
        done < "$hits"
        local default_count=$((total_hits - p2))
        [[ $default_count -gt 0 ]] && echo -e "  ${DIM}(${default_count} default config values listed above — expected in Docker/image build scripts)${NC}"
    fi
    rm -f "$hits"
    [[ $p2 -eq 0 ]] && ok "No hardcoded secrets found in tracked files"
    inc p2 $p2

    # ─── Phase 3: 工作区敏感文件（未跟踪） ──────────────────────────────
    header "Phase 3: Untracked sensitive files"
    local p3=0
    # 合并为扩展正则（用于grep -E，匹配basename）
    local name_ere='(/|^)(\.env(\..*)?|.*\.env|\.envrc|id_(rsa|ed25519|ecdsa).*|.*\.(pem|key|p12|pfx|pkcs12)|\.secrets|secrets\..*|.*_secrets?\..*|.*\.secret|credentials.*|.*credentials.*|.*\.local\.(json|yaml|yml|py|js|ts|toml))$'
    # 3a. 未跟踪且未忽略的敏感文件（危险！）
    while IFS= read -r uf; do
        [[ -z "$uf" ]] && continue
        is_whitelisted "$uf" && continue
        warn "${pfx}Untracked & NOT ignored: $uf  (add to .gitignore!)"
        p3=$((p3 + 1))
    done < <(git ls-files --others --exclude-standard 2>/dev/null | grep -E -- "$name_ere" || true)
    # 3b. 被忽略的敏感文件（确认已被.gitignore保护）—— 最多显示20个避免刷屏
    local ignored_count=0
    while IFS= read -r uf; do
        [[ -z "$uf" ]] && continue
        is_whitelisted "$uf" && continue
        ok "${pfx}Ignored (good): $uf"
        ignored_count=$((ignored_count + 1))
    done < <(git ls-files --others --ignored --exclude-standard 2>/dev/null | grep -E -- "$name_ere" | head -20 || true)
    if [[ $ignored_count -eq 20 ]]; then
        echo -e "  ${DIM}(... more ignored sensitive files exist, .gitignore is working)${NC}"
    fi

    # 检查根目录常见敏感文件
    for known in .env .env.local .env.dev .env.prod id_rsa id_ed25519; do
        if [[ -f "$known" ]] && ! git ls-files --error-unmatch "$known" >/dev/null 2>&1; then
            is_whitelisted "$known" && continue
            if git check-ignore -q "$known" 2>/dev/null; then
                : # already reported above if in ls-files --others
            else
                warn "${pfx}Untracked & NOT ignored: $known"
                p3=$((p3 + 1))
            fi
        fi
    done
    inc p3 $p3

    # ─── Phase 4: Git 历史 ─────────────────────────────────────────────
    if $SCAN_HISTORY; then
        header "Phase 4: Git history scan (slow)"
        local p4=0
        # 4a. 历史中出现过的敏感文件名
        local pathspec_args=()
        for g in "${HIGH_RISK_GLOBS[@]}"; do
            pathspec_args+=(":(glob)$g")
        done
        local hist_file_hits
        hist_file_hits="$(mktemp)"
        git log --all --full-history --pretty=format:"%h|%ad|%s" --date=short -- "${pathspec_args[@]}" 2>/dev/null \
            | grep -v '^$' | head -30 > "$hist_file_hits" || true
        if [[ -s "$hist_file_hits" ]]; then
            echo -e "  ${YELLOW}Sensitive filenames found in history:${NC}"
            while IFS='|' read -r hash date subj; do
                [[ -z "$hash" ]] && continue
                warn "${pfx}[$date] $hash  $subj"
            done < "$hist_file_hits"
            p4=$(wc -l < "$hist_file_hits")
        fi
        rm -f "$hist_file_hits"

        # 4b. 历史中出现过的硬编码密钥内容（通过 git log -p 扫描diff）
        local hist_content_hits
        hist_content_hits="$(mktemp)"
        echo -e "  ${DIM}Scanning git log patches for secrets (this may take a while)...${NC}"
        # 严格匹配：私钥PEM头必须在行首（diff行以+/-开头后紧跟PEM头，而非在句子/正则中间）
        git log --all --full-history -p 2>/dev/null \
            | grep -nE '^[+-][[:space:]]*-----BEGIN[[:space:]](RSA[[:space:]]|EC[[:space:]]|DSA[[:space:]]|OPENSSH[[:space:]]|PGP[[:space:]])?PRIVATE[[:space:]]KEY-----' \
            | grep -v 'EXAMPLE' | head -40 > "$hist_content_hits" || true
        # AWS Key / GitHub PAT（在行的diff添加行中）
        git log --all --full-history -p 2>/dev/null \
            | grep -nE '^\+[^+].*(AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9_]{36,})' \
            | grep -v 'EXAMPLE' | grep -v 'nosec' | head -40 >> "$hist_content_hits" || true
        if [[ -s "$hist_content_hits" ]]; then
            # 去重
            sort -u "$hist_content_hits" -o "$hist_content_hits"
            local cc=0
            echo -e "  ${RED}${BOLD}Potential secrets found in git history diffs:${NC}"
            while IFS= read -r hitline; do
                local content="${hitline#*:}"
                # 过滤含中文的行（文档/注释中讨论密钥，不是真实密钥）
                if echo "$content" | grep -qP '[\x{4e00}-\x{9fff}]' 2>/dev/null; then continue; fi
                # 过滤 nosec 标记行
                echo "$content" | grep -q 'nosec' && continue
                # 过滤源代码中的正则表达式定义（r"..." 或包含正则元字符 .* 等）
                if echo "$content" | grep -qE '\(r"|re\.compile|pattern|PATTERN|REGEX'; then continue; fi
                # 脱敏显示
                local masked="$content"
                local trimmed="${content#"${content%%[!+-[:space:]]*}"}"
                trimmed="${trimmed#"${trimmed%%[![:space:]]*}"}"
                if [[ ${#trimmed} -gt 20 ]]; then
                    masked="${trimmed:0:10}***${trimmed: -10}"
                else
                    masked="$trimmed"
                fi
                fail "${pfx}$masked"
                cc=$((cc + 1))
            done < "$hist_content_hits"
            p4=$((p4 + cc))
        fi
        rm -f "$hist_content_hits"

        # 4c. 历史中.env文件中的敏感赋值（快速扫描）
        local env_hist_hits
        env_hist_hits="$(mktemp)"
        git log --all --full-history -p -- '*.env' '.env*' 2>/dev/null \
            | grep -nE '^\+[^+].*(PASSWORD|TOKEN|SECRET|API_KEY|ACCESS_KEY|PRIVATE_KEY)[A-Za-z0-9_]*[[:space:]]*=[[:space:]]*[^#[:space:]]+' \
            | grep -vE '=\s*("?\$\{|="?your|="?xxx|="?changeme|="?example|="?placeholder|="?<|="?none|="?null|="?test|="?demo|=\s*$)' \
            | grep -v 'EXAMPLE' | grep -v 'nosec' | head -30 > "$env_hist_hits" || true
        if [[ -s "$env_hist_hits" ]]; then
            local ec=0
            echo -e "  ${YELLOW}Sensitive key=value assignments in .env file history:${NC}"
            while IFS= read -r hitline; do
                local content="${hitline#*:}"
                content="${content#"+"}"
                content="$(echo "$content" | sed 's/^[[:space:]]*//')"
                # 含中文跳过
                if echo "$content" | grep -qP '[\x{4e00}-\x{9fff}]' 2>/dev/null; then continue; fi
                # 脱敏值
                local key="${content%%=*}"
                local val="${content#*=}"
                val="$(echo "$val" | sed 's/^[[:space:]]*//;s/"//g;s/'\''//g')"
                # 检查值是否安全
                if is_safe_value "$val"; then continue; fi
                local dv
                if [[ ${#val} -gt 6 ]]; then
                    dv="${val:0:2}***${val: -2}"
                else
                    dv="***"
                fi
                warn "${pfx}$key = $dv"
                ec=$((ec + 1))
            done < "$env_hist_hits"
            p4=$((p4 + ec))
            [[ $ec -eq 0 ]] && ok "No hardcoded secrets in .env history"
        fi
        rm -f "$env_hist_hits"

        [[ $p4 -eq 0 ]] && ok "No sensitive files or content in history"
        inc p4 $p4
    fi

    # ─── Submodules ────────────────────────────────────────────────────
    if $SCAN_SUBMODULES; then
        header "Submodules"
        while IFS= read -r sm_line; do
            [[ -z "$sm_line" ]] && continue
            local sm_path
            sm_path="$(echo "$sm_line" | awk '{print $2}')"
            [[ -z "$sm_path" ]] && continue
            local sm_sha
            sm_sha="$(echo "$sm_line" | awk '{print $1}')"
            [[ "$sm_sha" == -* ]] && continue
            if [[ -d "$repo_path/$sm_path/.git" ]] || [[ -f "$repo_path/$sm_path/.git" ]]; then
                ( scan_repo "$repo_path/$sm_path" "$repo_name/$sm_path" true )
            fi
        done < <(git submodule status 2>/dev/null || true)
    fi
}

# =============================================================================
# 主入口
# =============================================================================
init_cf

section "Git Secrets Scanner"
echo "  Root: $PROJECT_ROOT"
echo "  Submodules: $SCAN_SUBMODULES"
echo "  History: $SCAN_HISTORY"

scan_repo "$PROJECT_ROOT" "$(basename "$PROJECT_ROOT")" false

# ─── 汇总 ──────────────────────────────────────────────────────────────────
section "Summary"
echo ""
echo "  Repositories scanned: $(cnt repos)"
echo "  Files in index: $(cnt files)"
echo ""
TP1=$(cnt p1); TP2=$(cnt p2); TP3=$(cnt p3); TP4=$(cnt p4)
CRIT=$((TP1 + TP2))

if [[ $CRIT -gt 0 ]]; then
    echo -e "  ${RED}${BOLD}❌ CRITICAL: $CRIT sensitive issue(s) TRACKED in git!${NC}"
    echo -e "  ${RED}     Sensitive filenames: $TP1${NC}"
    echo -e "  ${RED}     Hardcoded secrets in content: $TP2${NC}"
fi
if [[ $TP4 -gt 0 ]]; then
    echo -e "  ${RED}${BOLD}❌ HISTORY: $TP4 issue(s) in git history!${NC}"
fi
if [[ $TP3 -gt 0 ]]; then
    echo -e "  ${YELLOW}⚠ WARNING: $TP3 untracked sensitive file(s) not in .gitignore${NC}"
fi

if [[ $CRIT -eq 0 ]] && [[ $TP4 -eq 0 ]] && [[ $TP3 -eq 0 ]]; then
    echo -e "  ${GREEN}${BOLD}✅ Clean! No sensitive files or hardcoded secrets tracked in git.${NC}"
    exit 0
fi

echo ""
echo -e "  ${BOLD}Recommended actions:${NC}"
[[ $TP1 -gt 0 ]] && echo "   1. git rm --cached <file>   (untrack sensitive files)"
[[ $TP2 -gt 0 ]] && echo "   2. ROTATE all exposed keys/tokens/passwords immediately!"
[[ $TP4 -gt 0 ]] && echo "   3. Purge history with git-filter-repo or BFG Repo-Cleaner"
echo "   4. Add patterns to .gitignore"
echo "   5. Commit fixes (force-push if history was rewritten)"

if [[ $CRIT -gt 0 ]] || [[ $TP4 -gt 0 ]]; then
    exit 1
fi
exit 2
