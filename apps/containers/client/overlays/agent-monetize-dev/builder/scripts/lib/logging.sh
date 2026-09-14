#!/usr/bin/env bash
# ==============================================================================
# xmnn-dev 共享构建日志函数库（vendor 自包含，禁止跨目录引用外部 chaos 工程）
#
# 用法：在构建脚本中 source 本文件：
#
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/lib/logging.sh"
#   LOG_FILE=/dev/null          # 直接输出到容器 stdout（podman-compose exec 捕获）
#   log_set_error_help '...'    # 可选：自定义排查帮助
#   log_enable_trap             # 启用 ERR trap
#
# 提供：log_info/log_ok/log_warn/log_error/log_step/log_section/
#       log_header/log_footer/log_banner/log_gray/log_kv/log_ts
# ==============================================================================

# ── 防止重复 source ──────────────────────────────────────────────────
if [ -n "${_LOGGING_SH_LOADED:-}" ]; then
    return 0
fi
_LOGGING_SH_LOADED=1

# ── 颜色定义（TTY 检测，非 TTY 自动降级）──────────────────────────────
if [ -t 1 ]; then
    CLR_RESET='\033[0m'
    CLR_RED='\033[0;31m'
    CLR_GREEN='\033[0;32m'
    CLR_YELLOW='\033[1;33m'
    CLR_BLUE='\033[0;34m'
    CLR_CYAN='\033[0;36m'
    CLR_MAGENTA='\033[0;35m'
    CLR_BOLD='\033[1m'
    CLR_GRAY='\033[0;90m'
    CLR_BG_RED='\033[41m'
else
    CLR_RESET='' CLR_RED='' CLR_GREEN='' CLR_YELLOW='' CLR_BLUE=''
    CLR_CYAN='' CLR_MAGENTA='' CLR_BOLD='' CLR_GRAY='' CLR_BG_RED=''
fi

# LOG_FILE 未设置时兜底为 /dev/null（脚本可只 source 不初始化）
LOG_FILE="${LOG_FILE:-/dev/null}"

log_info()    { echo -e "${CLR_GREEN}ℹ️${CLR_RESET}  $*" | tee -a "$LOG_FILE"; }
log_ok()      { echo -e "${CLR_GREEN}✅${CLR_RESET}  $*" | tee -a "$LOG_FILE"; }
log_warn()    { echo -e "${CLR_YELLOW}⚠️${CLR_RESET}  $*" | tee -a "$LOG_FILE"; }
log_error()   { echo -e "${CLR_RED}❌${CLR_RESET}  $*" | tee -a "$LOG_FILE"; }
log_step()    { echo "" | tee -a "$LOG_FILE"; echo -e "${CLR_BOLD}${CLR_BLUE}━━━ $* ━━━${CLR_RESET}" | tee -a "$LOG_FILE"; echo "" | tee -a "$LOG_FILE"; }
log_section() { echo "" | tee -a "$LOG_FILE"; echo -e "${CLR_BOLD}${CLR_CYAN}── $* ──${CLR_RESET}" | tee -a "$LOG_FILE"; }
log_header()  { echo "" | tee -a "$LOG_FILE"; echo -e "${CLR_BOLD}${CLR_CYAN}╔══════════════════════════════════════════════════════════════╗${CLR_RESET}" | tee -a "$LOG_FILE"; }
log_footer()  { echo -e "${CLR_BOLD}${CLR_CYAN}╚══════════════════════════════════════════════════════════════╝${CLR_RESET}" | tee -a "$LOG_FILE"; echo "" | tee -a "$LOG_FILE"; }
log_banner()  { echo -e "${CLR_BOLD}${CLR_MAGENTA}$*${CLR_RESET}" | tee -a "$LOG_FILE"; }
log_gray()    { echo -e "${CLR_GRAY}$*${CLR_RESET}" | tee -a "$LOG_FILE"; }
log_kv()      { printf "${CLR_CYAN}  %-22s${CLR_RESET} %s\n" "$1" "$2" | tee -a "$LOG_FILE"; }
log_ts()      { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

# ── 自定义错误帮助内容（通过 log_set_error_help 设置）────────────────
_LOG_ERROR_HELP_TEXT=""

log_set_error_help() {
    _LOG_ERROR_HELP_TEXT="$1"
}

# ── 错误处理：捕获 ERR ──────────────────────────────────────────────
on_error() {
    local exit_code=$?
    local line_no=${1:-unknown}
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CLR_BG_RED}${CLR_BOLD}                                                    ${CLR_RESET}" | tee -a "$LOG_FILE"
    echo -e "${CLR_BG_RED}${CLR_BOLD}  ❌  构 建 失 败！(exit code: ${exit_code}, line: ${line_no})       ${CLR_RESET}" | tee -a "$LOG_FILE"
    echo -e "${CLR_BG_RED}${CLR_BOLD}                                                    ${CLR_RESET}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"

    log_banner "🔍 排查建议："
    if [ -n "$_LOG_ERROR_HELP_TEXT" ]; then
        echo -e "$_LOG_ERROR_HELP_TEXT" | tee -a "$LOG_FILE"
    else
        cat <<'HELP' | tee -a "$LOG_FILE"
  1. 查看上方输出最后报错位置，定位失败阶段：
     - pip 安装失败     → 镜像源/依赖冲突（尝试 --pip-mirror tuna|aliyun）
     - clang++ 编译失败 → tvm-ffi 头/库缺失？查 -I/-L 与 apache-tvm-ffi 安装
     - wheel 打包失败   → 检查 pyproject.toml 与 build 模块（python -m build）
  2. 资源不足（Killed / out of memory）：暂停其他 WSL 负载后重试（单 .cc 编译开销很小）
  3. 前置缺失：score_opportunity.cc 不存在 → 确认 MONETIZE_SRC_PATH 挂载；
     原生 .so 尚未编译不影响 wheel（.so 不入 wheel），需要原生打分再 inv monetize.build-native
HELP
    fi

    exit $exit_code
}

# ── 启用 ERR trap ───────────────────────────────────────────────────
log_enable_trap() {
    trap 'on_error $LINENO' ERR
}
