#!/usr/bin/env bash
# =============================================================================
# scripts/docker-size-compare.sh — Docker 镜像体积对比工具
#
# 功能：
#   1. snapshot 模式：采集镜像体积指标并保存为 JSON 快照
#   2. compare 模式：对比两个镜像（或快照 vs 镜像）的体积差异
#   3. auto 模式：快照当前镜像 → 等待用户重建 → 自动对比
#
# 用法：
#   # 采集当前镜像快照（优化前）
#   bash scripts/docker-size-compare.sh --snapshot --image devcontainer-base:conda-libmamba-ft
#
#   # 对比两个镜像
#   bash scripts/docker-size-compare.sh --old devcontainer-base:before --new devcontainer-base:after
#
#   # 对比快照文件与当前镜像
#   bash scripts/docker-size-compare.sh --old snapshots/size-before.json --new devcontainer-base:conda-libmamba-ft
#
#   # 自动模式：快照 → 等待重建 → 对比
#   bash scripts/docker-size-compare.sh --auto
#
#   # 输出 JSON 格式
#   bash scripts/docker-size-compare.sh --old OLD --new NEW --json
#
# 输出：人类可读表格 + 可选 JSON
# 指标：总体积、目录级分解、层分解、conda/pip包数、优化目标专项统计
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── 加载统一日志库 ──
if [ -f "${SCRIPT_DIR}/lib/logging.sh" ]; then
    source "${SCRIPT_DIR}/lib/logging.sh"
    LOG_SERVICE="docker-size-compare"
else
    # Fallback minimal logging
    _HAS_TTY=false; [ -t 1 ] && _HAS_TTY=true
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
    CYAN='\033[0;36m'; BOLD='\033[1m'; GRAY='\033[0;90m'; NC='\033[0m'
    $_HAS_TTY || { RED=''; GREEN=''; YELLOW=''; CYAN=''; BOLD=''; GRAY=''; NC=''; }
    log_step()  { echo ""; echo -e "${BOLD}${CYAN}━━━ $* ━━━${NC}"; echo ""; }
    log_ok()    { echo -e "  ${GREEN}✔${NC} $*"; }
    log_warn()  { echo -e "  ${YELLOW}⚠${NC} $*"; }
    log_error() { echo -e "  ${RED}✘${NC} $*"; }
    log_fatal() { echo -e "  ${RED}💀${NC} $*"; exit 1; }
    log_info()  { echo -e "     $*"; }
    log_debug() { [ "${DEBUG:-0}" = "1" ] && echo -e "  ${GRAY}DBG${NC} $*" || true; }
fi

# ── 默认配置 ──
MODE=""
OLD_IMAGE=""
NEW_IMAGE=""
SNAPSHOT_IMAGE=""
SNAPSHOT_DIR="${PROJECT_DIR}/logs/size-snapshots"
OUTPUT_JSON=""
JSON_OUTPUT=false
DEFAULT_IMAGE="devcontainer-base:conda-libmamba-ft"

# ── 颜色（对比表格用） ──
if [ -t 1 ]; then
    C_GREEN='\033[0;32m'; C_RED='\033[0;31m'; C_BOLD='\033[1m'
    C_CYAN='\033[0;36m'; C_YELLOW='\033[1;33m'; C_GRAY='\033[0;90m'; C_RST='\033[0m'
else
    C_GREEN=''; C_RED=''; C_BOLD=''; C_CYAN=''; C_YELLOW=''; C_GRAY=''; C_RST=''
fi

# ── 临时容器清理 ──
_TEMP_CONTAINERS=()
cleanup_containers() {
    for cid in "${_TEMP_CONTAINERS[@]}"; do
        docker rm -f "$cid" >/dev/null 2>&1 || true
    done
}
trap cleanup_containers EXIT

# ── 用法 ──
usage() {
    cat <<EOF
${C_BOLD}Docker Image Size Compare Tool${C_RST}

Usage: $0 [MODE] [OPTIONS]

Modes (must specify exactly one):
  --snapshot              Collect metrics from an image and save as JSON snapshot
  --compare               Compare two images (or snapshot vs image)
  --auto                  Snapshot current image → wait for rebuild → auto compare

Options:
  --image IMAGE           Image to snapshot (default: ${DEFAULT_IMAGE})
  --old REF               Old image reference (image name or snapshot JSON file)
  --new REF               New image reference (image name or snapshot JSON file)
  --snapshot-dir DIR      Directory for snapshots (default: ${SNAPSHOT_DIR})
  --json                  Also output comparison result as JSON
  -o, --output FILE       Write JSON output to FILE
  -h, --help              Show this help

Examples:
  # 1. Before optimization: snapshot current image
  $0 --snapshot --image devcontainer-base:conda-libmamba-ft

  # 2. After rebuild: compare snapshot with new image
  $0 --compare --old logs/size-snapshots/size-*.json --new devcontainer-base:conda-libmamba-ft

  # 3. One-liner: compare two tagged images
  $0 --compare --old devcontainer-base:before --new devcontainer-base:after

  # 4. Auto mode (snapshot, wait, compare)
  $0 --auto --image devcontainer-base:conda-libmamba-ft
EOF
}

# ── 参数解析 ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --snapshot) MODE="snapshot"; shift ;;
        --compare)  MODE="compare"; shift ;;
        --auto)     MODE="auto"; shift ;;
        --image)    SNAPSHOT_IMAGE="$2"; shift 2 ;;
        --old)      OLD_IMAGE="$2"; shift 2 ;;
        --new)      NEW_IMAGE="$2"; shift 2 ;;
        --snapshot-dir) SNAPSHOT_DIR="$2"; shift 2 ;;
        --json)     JSON_OUTPUT=true; shift ;;
        -o|--output) OUTPUT_JSON="$2"; shift 2 ;;
        -h|--help)  usage; exit 0 ;;
        *)          log_error "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ -z "$MODE" ]; then
    # Auto-detect mode from args
    if [ -n "$OLD_IMAGE" ] && [ -n "$NEW_IMAGE" ]; then
        MODE="compare"
    elif [ -n "$SNAPSHOT_IMAGE" ]; then
        MODE="snapshot"
    else
        log_error "Must specify a mode (--snapshot, --compare, --auto) or use --old/--new"
        usage
        exit 1
    fi
fi

# =============================================================================
# 工具函数
# =============================================================================

# 将 docker images 的 Size 字段转为 MB（整数）
size_to_mb() {
    local size_str="$1"
    local num unit
    # Handle empty/zero cases
    [ -z "$size_str" ] && { echo "0"; return; }
    echo "$size_str" | grep -qE '^0B?$' && { echo "0"; return; }
    num=$(echo "$size_str" | grep -oE '[0-9.]+' | head -1)
    unit=$(echo "$size_str" | grep -oE '[A-Za-z]+' | head -1 | tr '[:upper:]' '[:lower:]')
    [ -z "$num" ] && { echo "0"; return; }
    case "$unit" in
        gb|g) echo "$num * 1024" | bc 2>/dev/null | cut -d. -f1 ;;
        mb|m) echo "$num" | cut -d. -f1 ;;
        kb|k) echo "scale=0; $num / 1024" | bc 2>/dev/null ;;
        b|"") echo "0" ;;
        *)    echo "$num" | cut -d. -f1 ;;  # assume MB if unknown
    esac
}

# 格式化 MB 为人类可读
format_mb() {
    local mb="$1"
    if [ "$mb" -ge 1024 ]; then
        echo "$(echo "scale=2; $mb / 1024" | bc) GB"
    else
        echo "${mb} MB"
    fi
}

# 格式化差异：+/-X MB (-Y%)
format_diff() {
    local old_mb="$1" new_mb="$2"
    local diff_mb=$((new_mb - old_mb))
    local pct=""
    if [ "$old_mb" -gt 0 ]; then
        pct=$(echo "scale=1; ($diff_mb * 100) / $old_mb" | bc)
    fi
    local abs_diff=${diff_mb#-}
    if [ "$diff_mb" -lt 0 ]; then
        echo -e "${C_GREEN}-$(format_mb $abs_diff) (${pct}%)${C_RST}"
    elif [ "$diff_mb" -gt 0 ]; then
        echo -e "${C_RED}+$(format_mb $abs_diff) (+${pct}%)${C_RST}"
    else
        echo -e "${C_GRAY}0 MB (0%)${C_RST}"
    fi
}

# 启动临时容器（覆盖 entrypoint，避免启动服务）
start_temp_container() {
    local image="$1"
    local cid
    # Use --entrypoint "" so we can run a plain command; override both entrypoint and cmd
    # to avoid the container's tini+entrypoint.sh from starting services
    cid=$(docker create --entrypoint "" "$image" tail -f /dev/null 2>/dev/null)
    if [ -z "$cid" ]; then
        log_error "Failed to create container from image: $image"
        return 1
    fi
    _TEMP_CONTAINERS+=("$cid")
    docker start "$cid" >/dev/null 2>&1
    # Wait for container to be running
    local waited=0
    while [ $waited -lt 10 ]; do
        local state
        state=$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null)
        if [ "$state" = "running" ]; then break; fi
        sleep 1; waited=$((waited + 1))
    done
    echo "$cid"
}

# 在容器内执行命令（带超时）
container_exec() {
    local cid="$1"; shift
    timeout 60 docker exec "$cid" "$@" 2>/dev/null || echo "N/A"
}

# 在容器内用 bash 执行命令（支持管道/find等）
container_sh() {
    local cid="$1"; shift
    timeout 60 docker exec "$cid" /bin/bash -c "$*" 2>/dev/null || echo "N/A"
}

# =============================================================================
# 指标采集
# =============================================================================

collect_metrics() {
    local image="$1"
    local label="$2"

    log_step "采集镜像指标: $image"

    # ── 预检：镜像存在 ──
    if ! docker image inspect "$image" >/dev/null 2>&1; then
        log_fatal "镜像不存在: $image"
    fi

    # ── 元数据 ──
    local img_id created size_str virtual_size
    img_id=$(docker image inspect -f '{{.Id}}' "$image" | cut -d: -f2 | cut -c1-12)
    created=$(docker image inspect -f '{{.Created}}' "$image" | cut -d. -f1 | tr 'T' ' ')
    size_str=$(docker images --format '{{.Size}}' "$image" | head -1)
    virtual_size=$(size_to_mb "$size_str")

    log_info "Image ID:  $img_id"
    log_info "Created:   $created"
    log_info "Size:      $size_str (${virtual_size} MB)"

    # ── 启动临时容器 ──
    log_info "Starting temporary container for deep inspection..."
    local cid
    cid=$(start_temp_container "$image")
    if [ -z "$cid" ]; then
        log_warn "Cannot start container; collecting docker-level metrics only"
        # Output minimal JSON
        cat <<JSONEOF
{
  "label": "$label",
  "image": "$image",
  "image_id": "$img_id",
  "created": "$created",
  "total_size_mb": $virtual_size,
  "total_size_str": "$size_str",
  "layers": [],
  "dirs": {},
  "conda": {},
  "optimization_targets": {},
  "error": "container_start_failed"
}
JSONEOF
        return 0
    fi
    log_ok "Container started: ${cid:0:12}"

    # ── 层分解 ──
    log_info "Collecting layer breakdown..."
    local layers_json="["
    local first=true
    while IFS='|' read -r l_size l_created_by; do
        [ "$first" = true ] && first=false || layers_json+=","
        local l_mb
        l_mb=$(size_to_mb "$l_size")
        # Escape quotes in created_by
        local l_cb
        l_cb=$(echo "$l_created_by" | sed 's/"/\\"/g' | head -c 120)
        layers_json+="{\"size_mb\":$l_mb,\"created_by\":\"$l_cb\"}"
    done < <(docker history --no-trunc --format '{{.Size}}|{{.CreatedBy}}' "$image" 2>/dev/null | tail -n +2)
    layers_json+="]"

    # ── 目录级分解 ──
    log_info "Collecting directory sizes..."
    local dirs_json="{"
    local dirs=(
        "/opt/conda"
        "/opt/conda/envs/main"
        "/opt/conda/pkgs"
        "/usr"
        "/usr/lib"
        "/usr/lib/x86_64-linux-gnu"
        "/usr/bin"
        "/usr/share"
        "/var"
        "/var/lib"
        "/var/cache"
        "/lib"
        "/bin"
        "/sbin"
        "/etc"
        "/opt"
    )
    first=true
    for dir in "${dirs[@]}"; do
        local dir_size
        dir_size=$(container_sh "$cid" "du -sm '$dir' 2>/dev/null | cut -f1")
        if [ "$dir_size" = "N/A" ] || [ -z "$dir_size" ]; then dir_size=0; fi
        [ "$first" = true ] && first=false || dirs_json+=","
        dirs_json+="\"$dir\":$dir_size"
    done
    # Also check for podman
    local podman_size=0
    if container_sh "$cid" "which podman" | grep -q "/"; then
        podman_size=$(container_sh "$cid" "du -sm /usr/bin/podman /usr/lib/crun /usr/bin/conmon /usr/libexec/podman 2>/dev/null | awk '{s+=\$1} END {print s}'")
        [ "$podman_size" = "N/A" ] && podman_size=0
    fi
    dirs_json+=",\"__podman_binary\":$podman_size"
    dirs_json+="}"

    # ── Conda 信息 ──
    log_info "Collecting conda/pip package info..."
    local conda_base_pkgs=0 conda_main_pkgs=0 pip_base_pkgs=0 pip_main_pkgs=0
    local conda_base_size=0 conda_main_size=0

    # Conda packages
    conda_base_pkgs=$(container_sh "$cid" "conda list -n base --json 2>/dev/null | grep -c '\"name\"'")
    [ "$conda_base_pkgs" = "N/A" ] && conda_base_pkgs=0
    conda_main_pkgs=$(container_sh "$cid" "conda list -n main --json 2>/dev/null | grep -c '\"name\"'")
    [ "$conda_main_pkgs" = "N/A" ] && conda_main_pkgs=0

    # Pip packages
    pip_base_pkgs=$(container_sh "$cid" "/opt/conda/bin/pip list 2>/dev/null | wc -l")
    [ "$pip_base_pkgs" = "N/A" ] && pip_base_pkgs=0
    pip_base_pkgs=$((pip_base_pkgs > 2 ? pip_base_pkgs - 2 : 0))  # subtract header lines
    pip_main_pkgs=$(container_sh "$cid" "/opt/conda/envs/main/bin/pip list 2>/dev/null | wc -l")
    [ "$pip_main_pkgs" = "N/A" ] && pip_main_pkgs=0
    pip_main_pkgs=$((pip_main_pkgs > 2 ? pip_main_pkgs - 2 : 0))

    # Conda env sizes
    conda_base_size=$(container_sh "$cid" "du -sm /opt/conda 2>/dev/null | cut -f1")
    [ "$conda_base_size" = "N/A" ] && conda_base_size=0
    conda_main_size=$(container_sh "$cid" "du -sm /opt/conda/envs/main 2>/dev/null | cut -f1")
    [ "$conda_main_size" = "N/A" ] && conda_main_size=0

    # nbclassic check
    local has_nbclassic="false"
    if container_sh "$cid" "conda list -n base 2>/dev/null | grep -q nbclassic"; then
        has_nbclassic="true"
    fi
    if container_sh "$cid" "conda list -n main 2>/dev/null | grep -q nbclassic"; then
        has_nbclassic="true"
    fi

    # Podman installed?
    local has_podman="false"
    if container_sh "$cid" "which podman 2>/dev/null" | grep -q "/"; then
        has_podman="true"
    fi

    # ── 优化目标专项统计 ──
    log_info "Collecting optimization target stats..."

    # Static libraries (.a files)
    local static_lib_count=0 static_lib_size=0
    static_lib_count=$(container_sh "$cid" "find /opt/conda /usr/lib /lib -name '*.a' -type f 2>/dev/null | wc -l")
    [ "$static_lib_count" = "N/A" ] && static_lib_count=0
    static_lib_size=$(container_sh "$cid" "find /opt/conda /usr/lib /lib -name '*.a' -type f -exec du -cm {} + 2>/dev/null | tail -1 | cut -f1")
    [ "$static_lib_size" = "N/A" ] && static_lib_size=0

    # Test directories
    local test_dir_size=0
    test_dir_size=$(container_sh "$cid" "find /opt/conda -type d \( -name tests -o -name testing \) -path '*/site-packages/*' -prune -exec du -sm {} + 2>/dev/null | awk '{s+=\$1} END {print s}'")
    [ "$test_dir_size" = "N/A" ] && test_dir_size=0

    # __pycache__
    local pycache_size=0
    pycache_size=$(container_sh "$cid" "find /opt/conda -type d -name __pycache__ -exec du -sm {} + 2>/dev/null | awk '{s+=\$1} END {print s}'")
    [ "$pycache_size" = "N/A" ] && pycache_size=0

    # .pyc files
    local pyc_count=0
    pyc_count=$(container_sh "$cid" "find /opt/conda -name '*.pyc' -type f 2>/dev/null | wc -l")
    [ "$pyc_count" = "N/A" ] && pyc_count=0

    # Locale files
    local locale_size=0
    locale_size=$(container_sh "$cid" "du -sm /usr/lib/locale /opt/conda/lib/locale /opt/conda/envs/main/lib/locale 2>/dev/null | awk '{s+=\$1} END {print s}'")
    [ "$locale_size" = "N/A" ] && locale_size=0

    # Zoneinfo
    local zoneinfo_size=0
    zoneinfo_size=$(container_sh "$cid" "du -sm /usr/share/zoneinfo /opt/conda/share/zoneinfo 2>/dev/null | awk '{s+=\$1} END {print s}'")
    [ "$zoneinfo_size" = "N/A" ] && zoneinfo_size=0

    # Terminfo
    local terminfo_size=0
    terminfo_size=$(container_sh "$cid" "du -sm /usr/share/terminfo /lib/terminfo 2>/dev/null | awk '{s+=\$1} END {print s}'")
    [ "$terminfo_size" = "N/A" ] && terminfo_size=0

    # Conda package cache
    local conda_pkgs_size=0
    conda_pkgs_size=$(container_sh "$cid" "du -sm /opt/conda/pkgs 2>/dev/null | cut -f1")
    [ "$conda_pkgs_size" = "N/A" ] && conda_pkgs_size=0

    # Conda index cache
    local conda_cache_size=0
    conda_cache_size=$(container_sh "$cid" "du -sm /opt/conda/pkgs/cache 2>/dev/null | cut -f1")
    [ "$conda_cache_size" = "N/A" ] && conda_cache_size=0

    # APT lists cache
    local apt_lists_size=0
    apt_lists_size=$(container_sh "$cid" "du -sm /var/lib/apt/lists 2>/dev/null | cut -f1")
    [ "$apt_lists_size" = "N/A" ] && apt_lists_size=0

    # man pages / doc
    local man_doc_size=0
    man_doc_size=$(container_sh "$cid" "du -sm /usr/share/man /usr/share/doc /usr/share/info 2>/dev/null | awk '{s+=\$1} END {print s}'")
    [ "$man_doc_size" = "N/A" ] && man_doc_size=0

    # ── 输出 JSON ──
    local ts
    ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    cat <<JSONEOF
{
  "label": "$label",
  "image": "$image",
  "image_id": "$img_id",
  "created": "$created",
  "collected_at": "$ts",
  "total_size_mb": $virtual_size,
  "total_size_str": "$size_str",
  "layers": $layers_json,
  "dirs": $dirs_json,
  "conda": {
    "base_packages": $conda_base_pkgs,
    "main_packages": $conda_main_pkgs,
    "pip_base_packages": $pip_base_pkgs,
    "pip_main_packages": $pip_main_pkgs,
    "base_env_mb": $conda_base_size,
    "main_env_mb": $conda_main_size,
    "has_nbclassic": $has_nbclassic,
    "has_podman": $has_podman
  },
  "optimization_targets": {
    "static_lib_count": $static_lib_count,
    "static_lib_mb": $static_lib_size,
    "test_dirs_mb": $test_dir_size,
    "pycache_mb": $pycache_size,
    "pyc_count": $pyc_count,
    "locale_mb": $locale_size,
    "zoneinfo_mb": $zoneinfo_size,
    "terminfo_mb": $terminfo_size,
    "conda_pkgs_cache_mb": $conda_pkgs_size,
    "conda_index_cache_mb": $conda_cache_size,
    "apt_lists_mb": $apt_lists_size,
    "man_doc_mb": $man_doc_size,
    "podman_binary_mb": $podman_size
  }
}
JSONEOF
}

# =============================================================================
# 快照模式
# =============================================================================
do_snapshot() {
    local image="${SNAPSHOT_IMAGE:-$DEFAULT_IMAGE}"
    mkdir -p "$SNAPSHOT_DIR"
    local ts
    ts=$(date +%Y%m%d-%H%M%S)
    local snapshot_file="${SNAPSHOT_DIR}/size-${ts}.json"

    log_step "Snapshot Mode"
    log_info "Image:    $image"
    log_info "Snapshot: $snapshot_file"
    echo ""

    local metrics
    metrics=$(collect_metrics "$image" "before-optimization")
    echo "$metrics" > "$snapshot_file"

    echo ""
    log_ok "Snapshot saved: $snapshot_file"
    echo ""

    # Quick summary
    local total_mb
    total_mb=$(echo "$metrics" | grep '"total_size_mb"' | grep -oE '[0-9]+')
    log_info "Total image size: $(format_mb "$total_mb")"
    log_info "Use this command after rebuild to compare:"
    echo ""
    echo "  bash scripts/docker-size-compare.sh --compare \\"
    echo "    --old $snapshot_file \\"
    echo "    --new $image"
    echo ""
}

# =============================================================================
# 对比模式
# =============================================================================
load_ref() {
    local ref="$1"
    local label="$2"
    if [ -f "$ref" ]; then
        # It's a snapshot file
        if ! echo "$ref" | grep -q '\.json$'; then
            log_fatal "Snapshot file must be .json: $ref"
        fi
        cat "$ref"
    else
        # Treat as image name
        collect_metrics "$ref" "$label"
    fi
}

do_compare() {
    if [ -z "$OLD_IMAGE" ] || [ -z "$NEW_IMAGE" ]; then
        log_fatal "Compare mode requires --old and --new arguments"
    fi

    log_step "Compare Mode"
    log_info "Old: $OLD_IMAGE"
    log_info "New: $NEW_IMAGE"
    echo ""

    # Load metrics
    local old_json new_json
    old_json=$(load_ref "$OLD_IMAGE" "old")
    new_json=$(load_ref "$NEW_IMAGE" "new")

    # Parse key values using grep/sed (no jq dependency)
    extract_val() {
        local json="$1" key="$2"
        echo "$json" | grep "\"$key\"" | head -1 | sed 's/.*: *//' | tr -d ', "'
    }

    local old_total new_total
    old_total=$(extract_val "$old_json" "total_size_mb")
    new_total=$(extract_val "$new_json" "total_size_mb")

    local old_id new_id old_created new_created
    old_id=$(extract_val "$old_json" "image_id")
    new_id=$(extract_val "$new_json" "image_id")
    old_created=$(extract_val "$old_json" "created")
    new_created=$(extract_val "$new_json" "created")
    local old_label new_label
    old_label=$(extract_val "$old_json" "label")
    new_label=$(extract_val "$new_json" "label")

    local old_has_podman new_has_podman old_has_nbclassic new_has_nbclassic
    old_has_podman=$(extract_val "$old_json" "has_podman")
    new_has_podman=$(extract_val "$new_json" "has_podman")
    old_has_nbclassic=$(extract_val "$old_json" "has_nbclassic")
    new_has_nbclassic=$(extract_val "$new_json" "has_nbclassic")

    # ── 打印对比报告 ──
    echo ""
    echo -e "${C_BOLD}╔══════════════════════════════════════════════════════════════╗${C_RST}"
    echo -e "${C_BOLD}║           Docker Image Size Comparison Report               ║${C_RST}"
    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"
    printf "${C_BOLD}║${C_RST}  %-20s  %-22s → %-22s ║\n" "" "OLD ($old_label)" "NEW ($new_label)"
    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"

    # Metadata
    printf "${C_BOLD}║${C_RST}  %-18s  %-22s | %-22s ║\n" "Image ID" "$old_id" "$new_id"
    printf "${C_BOLD}║${C_RST}  %-18s  %-22s | %-22s ║\n" "Created" "$old_created" "$new_created"

    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"

    # ── 总体积 ──
    local diff_mb=$((new_total - old_total))
    local saved_mb=$((old_total - new_total))
    local saved_pct="0"
    if [ "$old_total" -gt 0 ]; then
        saved_pct=$(echo "scale=1; ($saved_mb * 100) / $old_total" | bc)
    fi

    if [ "$diff_mb" -lt 0 ]; then
        printf "${C_BOLD}║${C_RST}  ${C_GREEN}%-18s${C_RST}  ${C_BOLD}%-22s${C_RST} ${C_GREEN}%-24s${C_RST} ║\n" \
            "TOTAL SIZE" "$(format_mb $old_total)" "$(format_mb $new_total)"
        printf "${C_BOLD}║${C_RST}  ${C_GREEN}%-18s${C_RST}  ${C_GREEN}%-50s${C_RST} ║\n" \
            "SAVED" "$(format_mb $saved_mb) (${saved_pct}% reduction) 🎉"
    elif [ "$diff_mb" -gt 0 ]; then
        printf "${C_BOLD}║${C_RST}  %-18s  ${C_BOLD}%-22s${C_RST} ${C_RED}%-24s${C_RST} ║\n" \
            "TOTAL SIZE" "$(format_mb $old_total)" "$(format_mb $new_total)"
        printf "${C_BOLD}║${C_RST}  ${C_RED}%-18s${C_RST}  ${C_RED}%-50s${C_RST} ║\n" \
            "INCREASED" "+$(format_mb $diff_mb) (+${saved_pct#-}%)"
    else
        printf "${C_BOLD}║${C_RST}  %-18s  %-22s = %-22s ║\n" \
            "TOTAL SIZE" "$(format_mb $old_total)" "$(format_mb $new_total)"
        printf "${C_BOLD}║${C_RST}  %-18s  %-50s ║\n" "CHANGE" "No change"
    fi

    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"

    # ── 目录级对比 ──
    printf "${C_BOLD}║${C_RST}  ${C_BOLD}%-18s  %-12s %-10s   %-12s %-10s ║\n" "Directory" "Old" "Diff" "New" "Diff"
    echo -e "${C_BOLD}║${C_RST}  ────────────────────────────────────────────────────────── ║"

    local key_dirs=("/opt/conda" "/opt/conda/envs/main" "/opt/conda/pkgs" "/usr" "/usr/lib" "/usr/share" "/var" "/lib")
    for dir in "${key_dirs[@]}"; do
        local old_d new_d
        old_d=$(echo "$old_json" | grep "\"$dir\":" | grep -oE '[0-9]+' | head -1)
        new_d=$(echo "$new_json" | grep "\"$dir\":" | grep -oE '[0-9]+' | head -1)
        [ -z "$old_d" ] && old_d=0
        [ -z "$new_d" ] && new_d=0
        local d_diff=$((new_d - old_d))
        local diff_str
        if [ "$d_diff" -lt 0 ]; then
            diff_str="${C_GREEN}$(format_mb $((-d_diff))) ↓${C_RST}"
        elif [ "$d_diff" -gt 0 ]; then
            diff_str="${C_RED}$(format_mb $d_diff) ↑${C_RST}"
        else
            diff_str="${C_GRAY}0${C_RST}"
        fi
        printf "${C_BOLD}║${C_RST}  %-18s  %-12s %b   %-12s ║\n" "$dir" "$(format_mb $old_d)" "$diff_str" "$(format_mb $new_d)"
    done

    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"

    # ── 优化目标对比 ──
    printf "${C_BOLD}║${C_RST}  ${C_BOLD}%-28s  %8s → %-8s  %s\n" "Optimization Target" "Old" "New" "Change"
    echo -e "${C_BOLD}║${C_RST}  ────────────────────────────────────────────────────────── ║"

    print_opt_row() {
        local key="$1" name="$2" unit="$3"
        local old_v new_v
        old_v=$(echo "$old_json" | grep "\"$key\":" | grep -oE '[0-9]+' | head -1)
        new_v=$(echo "$new_json" | grep "\"$key\":" | grep -oE '[0-9]+' | head -1)
        [ -z "$old_v" ] && old_v=0
        [ -z "$new_v" ] && new_v=0
        local v_diff=$((new_v - old_v))
        local diff_str
        if [ "$v_diff" -lt 0 ]; then
            if [ "$unit" = "MB" ]; then
                diff_str="${C_GREEN}-$(format_mb $((-v_diff)))${C_RST}"
            else
                diff_str="${C_GREEN}-$((-v_diff))${C_RST}"
            fi
        elif [ "$v_diff" -gt 0 ]; then
            if [ "$unit" = "MB" ]; then
                diff_str="${C_RED}+$(format_mb $v_diff)${C_RST}"
            else
                diff_str="${C_RED}+$v_diff${C_RST}"
            fi
        else
            diff_str="${C_GRAY}0${C_RST}"
        fi
        local suffix=""
        [ "$unit" = "MB" ] && suffix=" MB"
        printf "${C_BOLD}║${C_RST}  %-28s  %6d%s → %-6d%s  %b\n" \
            "$name" "$old_v" "$suffix" "$new_v" "$suffix" "$diff_str"
    }

    print_opt_row "static_lib_mb" "Static libraries (.a)" "MB"
    print_opt_row "static_lib_count" "Static lib files" "count"
    print_opt_row "test_dirs_mb" "Test directories" "MB"
    print_opt_row "pycache_mb" "__pycache__" "MB"
    print_opt_row "pyc_count" ".pyc files" "count"
    print_opt_row "locale_mb" "Locale files" "MB"
    print_opt_row "zoneinfo_mb" "Zoneinfo (tzdata)" "MB"
    print_opt_row "terminfo_mb" "Terminfo" "MB"
    print_opt_row "conda_pkgs_cache_mb" "Conda pkgs cache" "MB"
    print_opt_row "apt_lists_mb" "APT lists" "MB"
    print_opt_row "man_doc_mb" "Man pages / docs" "MB"
    print_opt_row "podman_binary_mb" "Podman binaries" "MB"

    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"

    # ── 功能标志对比 ──
    printf "${C_BOLD}║${C_RST}  ${C_BOLD}%-28s  %-12s → %-12s ║\n" "Feature Flag" "Old" "New"
    echo -e "${C_BOLD}║${C_RST}  ────────────────────────────────────────────────────────── ║"
    printf "${C_BOLD}║${C_RST}  %-28s  %-12s → %-12s ║\n" "Podman installed" "$old_has_podman" "$new_has_podman"
    printf "${C_BOLD}║${C_RST}  %-28s  %-12s → %-12s ║\n" "nbclassic installed" "$old_has_nbclassic" "$new_has_nbclassic"

    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"

    # ── Conda 包对比 ──
    local old_base_pkgs new_base_pkgs old_main_pkgs new_main_pkgs
    old_base_pkgs=$(extract_val "$old_json" "base_packages")
    new_base_pkgs=$(extract_val "$new_json" "base_packages")
    old_main_pkgs=$(extract_val "$old_json" "main_packages")
    new_main_pkgs=$(extract_val "$new_json" "main_packages")
    local old_pip_base new_pip_base old_pip_main new_pip_main
    old_pip_base=$(extract_val "$old_json" "pip_base_packages")
    new_pip_base=$(extract_val "$new_json" "pip_base_packages")
    old_pip_main=$(extract_val "$old_json" "pip_main_packages")
    new_pip_main=$(extract_val "$new_json" "pip_main_packages")

    printf "${C_BOLD}║${C_RST}  ${C_BOLD}%-28s  %-12s → %-12s ║\n" "Package Count" "Old" "New"
    echo -e "${C_BOLD}║${C_RST}  ────────────────────────────────────────────────────────── ║"
    printf "${C_BOLD}║${C_RST}  %-28s  %-12s → %-12s ║\n" "Conda base env" "$old_base_pkgs" "$new_base_pkgs"
    printf "${C_BOLD}║${C_RST}  %-28s  %-12s → %-12s ║\n" "Conda main env" "$old_main_pkgs" "$new_main_pkgs"
    printf "${C_BOLD}║${C_RST}  %-28s  %-12s → %-12s ║\n" "Pip base env" "$old_pip_base" "$new_pip_base"
    printf "${C_BOLD}║${C_RST}  %-28s  %-12s → %-12s ║\n" "Pip main env" "$old_pip_main" "$new_pip_main"

    echo -e "${C_BOLD}╚══════════════════════════════════════════════════════════════╝${C_RST}"
    echo ""

    # ── 优化效果总结 ──
    if [ "$diff_mb" -lt 0 ]; then
        echo -e "${C_BOLD}${C_GREEN}✅ Optimization Result: Saved $(format_mb $saved_mb) (${saved_pct}% reduction)${C_RST}"
    elif [ "$diff_mb" -gt 0 ]; then
        echo -e "${C_BOLD}${C_RED}⚠️  Image size increased by $(format_mb $diff_mb)${C_RST}"
    else
        echo -e "${C_BOLD}No size change detected${C_RST}"
    fi
    echo ""

    # ── JSON 输出 ──
    if [ "$JSON_OUTPUT" = true ] || [ -n "$OUTPUT_JSON" ]; then
        local compare_ts
        compare_ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
        local json_result
        json_result=$(cat <<JSONEOF
{
  "type": "size_comparison",
  "compared_at": "$compare_ts",
  "old": $old_json,
  "new": $new_json,
  "summary": {
    "old_total_mb": $old_total,
    "new_total_mb": $new_total,
    "diff_mb": $diff_mb,
    "saved_mb": $saved_mb,
    "saved_pct": $saved_pct,
    "podman_removed": $( [ "$old_has_podman" = "true" ] && [ "$new_has_podman" = "false" ] && echo "true" || echo "false"),
    "nbclassic_removed": $( [ "$old_has_nbclassic" = "true" ] && [ "$new_has_nbclassic" = "false" ] && echo "true" || echo "false")
  }
}
JSONEOF
)
        if [ -n "$OUTPUT_JSON" ]; then
            mkdir -p "$(dirname "$OUTPUT_JSON")"
            echo "$json_result" > "$OUTPUT_JSON"
            log_ok "JSON report saved: $OUTPUT_JSON"
        else
            echo "$json_result"
        fi
    fi
}

# =============================================================================
# 自动模式
# =============================================================================
do_auto() {
    local image="${SNAPSHOT_IMAGE:-$DEFAULT_IMAGE}"
    mkdir -p "$SNAPSHOT_DIR"
    local ts
    ts=$(date +%Y%m%d-%H%M%S)
    local snapshot_file="${SNAPSHOT_DIR}/size-before-${ts}.json"

    log_step "Auto Mode: Snapshot → Wait for Rebuild → Compare"
    echo ""
    log_info "Step 1: Taking 'before' snapshot of $image..."
    echo ""

    local old_json
    old_json=$(collect_metrics "$image" "before")
    echo "$old_json" > "$snapshot_file"
    local old_total
    old_total=$(echo "$old_json" | grep '"total_size_mb"' | grep -oE '[0-9]+')

    echo ""
    log_ok "Before snapshot: $(format_mb $old_total)"
    log_ok "Snapshot saved: $snapshot_file"
    echo ""

    echo -e "${C_BOLD}╔══════════════════════════════════════════════════════════════╗${C_RST}"
    echo -e "${C_BOLD}║  ${C_YELLOW}READY FOR REBUILD${C_RST}${C_BOLD}                                         ║${C_RST}"
    echo -e "${C_BOLD}╠══════════════════════════════════════════════════════════════╣${C_RST}"
    echo -e "${C_BOLD}║${C_RST}  Now run your build command in another terminal:           ║"
    echo -e "${C_BOLD}║${C_RST}  ${C_CYAN}bash scripts/build.sh${C_RST}                                               ║"
    echo -e "${C_BOLD}║${C_RST}                                                              ║"
    echo -e "${C_BOLD}║${C_RST}  After the build completes, press Enter to continue...     ║"
    echo -e "${C_BOLD}╚══════════════════════════════════════════════════════════════╝${C_RST}"
    echo ""

    # Check if image still exists and has same ID (not yet rebuilt)
    local old_image_id
    old_image_id=$(echo "$old_json" | grep '"image_id"' | sed 's/.*: *"//;s/".*//')

    echo -n "  Waiting... (press Enter after rebuild)"
    read -r

    # Verify image exists and was rebuilt
    if ! docker image inspect "$image" >/dev/null 2>&1; then
        log_fatal "Image $image not found after rebuild. Did the build fail?"
    fi

    local new_image_id
    new_image_id=$(docker image inspect -f '{{.Id}}' "$image" | cut -d: -f2 | cut -c1-12)

    echo ""
    if [ "$new_image_id" = "$old_image_id" ]; then
        log_warn "Image ID unchanged ($new_image_id). The image may not have been rebuilt."
        echo -n "  Continue anyway? [y/N] "
        read -r answer
        if [ "$answer" != "y" ] && [ "$answer" != "Y" ]; then
            log_info "Aborted."
            exit 0
        fi
    else
        log_ok "Image rebuilt! Old ID: $old_image_id → New ID: $new_image_id"
    fi
    echo ""

    # Save as old/new for compare
    OLD_IMAGE="$snapshot_file"
    NEW_IMAGE="$image"
    do_compare
}

# =============================================================================
# Main
# =============================================================================
case "$MODE" in
    snapshot) do_snapshot ;;
    compare)  do_compare ;;
    auto)     do_auto ;;
    *)        usage; exit 1 ;;
esac
