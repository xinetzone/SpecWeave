#!/bin/bash
# =============================================================================
# clean-pycache.sh - Python缓存文件自动化清理工具
# 用途：防止 __pycache__/.pyc/.pyo 文件导致的隐蔽体积膨胀
# 适用场景：
#   1. Docker构建时同层清理（P7原则：文件创建层内完成清理）
#   2. 容器运行时定期清理（cron/entrypoint钩子）
#   3. CI/CD验证镜像无Python缓存残留
# 用法：
#   clean-pycache.sh [OPTIONS] [DIR...]     # 清理指定目录（默认: /opt/conda /usr）
#   clean-pycache.sh --check [DIR...]       # 检查模式：发现缓存则退出非零
#   clean-pycache.sh --stats [DIR...]       # 统计模式：显示缓存大小但不删除
#   source clean-pycache.sh && clean_pycache [DIR...]  # 作为库函数source
# 选项：
#   -q, --quiet    静默模式，只输出错误
#   -v, --verbose  详细模式，输出每个删除的文件
#   --check        检查模式：只检测不删除，有缓存则exit 1
#   --stats        统计模式：报告缓存数量和大小，不删除
#   -h, --help     显示帮助
# =============================================================================
set -euo pipefail

# ── 颜色定义（非TTY时自动禁用） ──
if [ -t 1 ] && [ -z "${NO_COLOR:-}" ]; then
    _C_GREEN='\033[0;32m'
    _C_YELLOW='\033[0;33m'
    _C_RED='\033[0;31m'
    _C_BOLD='\033[1m'
    _C_RST='\033[0m'
else
    _C_GREEN=''
    _C_YELLOW=''
    _C_RED=''
    _C_BOLD=''
    _C_RST=''
fi

# ── 默认清理目录（Docker镜像中的Python路径） ──
_DEFAULT_DIRS=(
    "/opt/conda"
    "/usr/lib/python3"
    "/usr/local/lib/python3"
)

# ── 日志函数 ──
_log_info()  { [ "${_QUIET:-0}" != "1" ] && echo -e "${_C_GREEN}[clean-pycache]${_C_RST} $*" >&2 || true; }
_log_warn()  { echo -e "${_C_YELLOW}[clean-pycache] WARN:${_C_RST} $*" >&2 || true; }
_log_error() { echo -e "${_C_RED}[clean-pycache] ERROR:${_C_RST} $*" >&2 || true; }
_log_verbose(){ [ "${_VERBOSE:-0}" = "1" ] && echo -e "[clean-pycache] $*" >&2 || true; }

# ── 核心清理函数（可被source调用） ──
# 用法: clean_pycache [dir1 dir2 ...]
# 环境变量: CLEAN_PYCACHE_DRYRUN=1 仅统计不删除
clean_pycache() {
    local target_dirs=("${@:-${_DEFAULT_DIRS[@]}}")
    local total_pyc=0
    local total_pycache=0
    local total_size=0
    local dir_count=0

    for d in "${target_dirs[@]}"; do
        if [ ! -d "$d" ]; then
            _log_verbose "Skip non-existent directory: $d"
            continue
        fi
        dir_count=$((dir_count + 1))
        _log_verbose "Scanning: $d"

        # 统计.pyc/.pyo文件
        local pyc_count
        pyc_count=$(find "$d" -type f \( -name "*.pyc" -o -name "*.pyo" \) 2>/dev/null | wc -l)
        total_pyc=$((total_pyc + pyc_count))

        # 统计__pycache__目录
        local pycache_count
        pycache_count=$(find "$d" -type d -name __pycache__ 2>/dev/null | wc -l)
        total_pycache=$((total_pycache + pycache_count))

        # 计算缓存大小
        local cache_size
        cache_size=$(find "$d" -type d -name __pycache__ -exec du -sb {} + 2>/dev/null | awk '{sum+=$1} END {print sum+0}')
        total_size=$((total_size + cache_size))

        # 非dry-run模式下执行删除
        if [ "${CLEAN_PYCACHE_DRYRUN:-0}" != "1" ] && [ "${_CHECK_MODE:-0}" != "1" ]; then
            # 删除 .pyc/.pyo 文件
            if [ "$pyc_count" -gt 0 ]; then
                find "$d" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
                _log_verbose "  Deleted $pyc_count .pyc/.pyo files in $d"
            fi
            # 删除 __pycache__ 目录
            if [ "$pycache_count" -gt 0 ]; then
                find "$d" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
                _log_verbose "  Deleted $pycache_count __pycache__ directories in $d"
            fi
        fi
    done

    # 格式化大小显示
    local size_display
    if [ "$total_size" -gt 1048576 ]; then
        size_display="$(awk "BEGIN {printf \"%.1f MB\", $total_size/1048576}")"
    elif [ "$total_size" -gt 1024 ]; then
        size_display="$(awk "BEGIN {printf \"%.1f KB\", $total_size/1024}")"
    else
        size_display="${total_size} B"
    fi

    # 输出结果
    if [ "${_STATS_MODE:-0}" = "1" ]; then
        echo "Python cache statistics across ${dir_count} director(ies):"
        echo "  .pyc/.pyo files: ${total_pyc}"
        echo "  __pycache__ dirs: ${total_pycache}"
        echo "  Total size:       ${size_display}"
    elif [ "${_CHECK_MODE:-0}" = "1" ]; then
        if [ "$total_pyc" -gt 0 ] || [ "$total_pycache" -gt 0 ]; then
            _log_error "Python cache found! .pyc/.pyo: ${total_pyc}, __pycache__: ${total_pycache}, size: ${size_display}"
            return 1
        else
            _log_info "No Python cache found (clean across ${dir_count} director(ies))"
            return 0
        fi
    else
        if [ "$total_pyc" -gt 0 ] || [ "$total_pycache" -gt 0 ]; then
            _log_info "Cleaned ${total_pyc} .pyc/.pyo files + ${total_pycache} __pycache__ dirs (${size_display}) from ${dir_count} director(ies)"
        else
            _log_verbose "No Python cache found in ${dir_count} director(ies)"
        fi
    fi
    return 0
}

# ── 显示帮助 ──
_usage() {
    cat << 'EOF'
Usage: clean-pycache.sh [OPTIONS] [DIR...]

Remove Python cache files (__pycache__, .pyc, .pyo) to prevent hidden volume bloat.

Options:
  -q, --quiet    Quiet mode: only errors
  -v, --verbose  Verbose mode: show each deleted file
  --check        Check mode: exit 1 if cache found (do not delete)
  --stats        Stats mode: report cache counts/sizes without deleting
  -h, --help     Show this help

If no DIR is specified, cleans default Python paths:
  /opt/conda, /usr/lib/python3*, /usr/local/lib/python3*

Examples:
  clean-pycache.sh                          # Clean default paths
  clean-pycache.sh /opt/conda/envs/main     # Clean specific directory
  clean-pycache.sh --check                  # CI: verify no cache remains
  clean-pycache.sh --stats /opt/conda       # Report cache size without deleting
  clean-pycache.sh -q /opt/conda /usr       # Quiet cleanup of multiple dirs

Library usage (source this script):
  source clean-pycache.sh
  clean_pycache [DIR...]           # Function accepts same arguments
  CLEAN_PYCACHE_DRYRUN=1 clean_pycache DIR...  # Dry run / stats
EOF
}

# ── 主入口（当脚本被直接执行时，而非被source时） ──
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    _QUIET=0
    _VERBOSE=0
    _CHECK_MODE=0
    _STATS_MODE=0
    _DIRS=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -q|--quiet) _QUIET=1; shift ;;
            -v|--verbose) _VERBOSE=1; shift ;;
            --check) _CHECK_MODE=1; shift ;;
            --stats) _STATS_MODE=1; shift ;;
            -h|--help) _usage; exit 0 ;;
            -*)
                _log_error "Unknown option: $1"
                _usage
                exit 1
                ;;
            *)
                _DIRS+=("$1")
                shift
                ;;
        esac
    done

    if [ ${#_DIRS[@]} -eq 0 ]; then
        # 动态扩展默认目录中的通配符
        _EXPANDED_DIRS=()
        for _pat in "${_DEFAULT_DIRS[@]}"; do
            # 检查是否包含通配符
            if [[ "$_pat" == *"*"* ]]; then
                for _d in $_pat; do
                    [ -d "$_d" ] && _EXPANDED_DIRS+=("$_d")
                done
            else
                [ -d "$_pat" ] && _EXPANDED_DIRS+=("$_pat")
            fi
        done
        _DIRS=("${_EXPANDED_DIRS[@]}")
    fi

    if [ ${#_DIRS[@]} -eq 0 ]; then
        _log_warn "No valid directories to process"
        exit 0
    fi

    clean_pycache "${_DIRS[@]}"
    exit $?
fi
