#!/bin/bash
# =============================================================================
# lib/logging.sh — 统一结构化日志库（通用版 v2）
# 提供人类可读(text) + 机器可解析(JSON Lines)双格式日志，适配自动化监控平台
#
# 用法 (在脚本开头):
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/lib/logging.sh"
#   LOG_SERVICE="my-service"
#   LOG_JSON_OUTPUT="/tmp/my-service-events.jsonl"  # 可选
#
# 支持参数（环境变量或 --log-format=/--log-level=/--log-json 命令行）:
#   LOG_FORMAT:       "text"(默认) | "json"(纯JSON Lines输出)
#   LOG_LEVEL:        DEBUG < INFO < WARN < ERROR < FATAL (默认 INFO)
#   LOG_JSON_STDOUT:  设为1时 JSON 同时输出到 stdout
#
# 公共 API:
#   log_debug "msg" | log_info "msg" | log_ok "msg" | log_warn "msg"
#   log_error "msg" | log_fail "msg" | log_fatal "msg"(退出1) | log_step "msg"
#   log_metric <name> <value> [unit]              # 数值指标
#   log_event <name> [key=value ...]              # 生命周期事件
#   log_summary <pass> <fail> <total> <dur> <status>  # 结果摘要
#   log_set_stage <stage> [step_num step_total]   # 阶段上下文
#   log_set_field <key> <value>                   # 持久化上下文字段
#   eval "$(log_parse_args "$@")"                 # 解析日志参数并重置 $@
# =============================================================================

# ── 默认配置（调用方可在 source 后覆盖） ──
LOG_FORMAT="${LOG_FORMAT:-text}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_SERVICE="${LOG_SERVICE:-bash-script}"
LOG_JSON_OUTPUT="${LOG_JSON_OUTPUT:-/tmp/${LOG_SERVICE}-events.jsonl}"

# ── 颜色（仅 TTY 或强制模式） ──
if [ -t 1 ] || [ "${LOG_FORCE_COLOR:-0}" = "1" ]; then
    _CLR_RESET='\033[0m'; _CLR_RED='\033[0;31m'; _CLR_GREEN='\033[0;32m'
    _CLR_YELLOW='\033[1;33m'; _CLR_BLUE='\033[0;34m'; _CLR_CYAN='\033[0;36m'
    _CLR_GRAY='\033[0;90m'; _CLR_BOLD='\033[1m'
else
    _CLR_RESET='' _CLR_RED='' _CLR_GREEN='' _CLR_YELLOW=''
    _CLR_BLUE='' _CLR_CYAN='' _CLR_GRAY='' _CLR_BOLD=''
fi

_log_level_num() {
    case "${1^^}" in
        DEBUG) echo 0 ;; INFO|OK|STEP) echo 1 ;; WARN) echo 2 ;;
        ERROR|FAIL) echo 3 ;; FATAL) echo 4 ;; *) echo 1 ;;
    esac
}
_log_is_enabled() {
    [ "$(_log_level_num "$1")" -ge "$(_log_level_num "$LOG_LEVEL")" ]
}
_log_ts() { date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u; }
_log_ensure_dir() { local d; d="$(dirname "$LOG_JSON_OUTPUT")"; [ -d "$d" ] || mkdir -p "$d" 2>/dev/null || true; }

# ── 上下文字段 ──
LOG_STAGE=""; LOG_STEP_NUM=""; LOG_STEP_TOTAL=""
log_set_stage() { LOG_STAGE="$1"; [ $# -ge 3 ] && { LOG_STEP_NUM="$2"; LOG_STEP_TOTAL="$3"; }; }
log_set_field() { export "_LOG_FIELD_${1}=${2}"; }

# ── 核心输出 ──
_log_emit() {
    local level="$1"; shift; local message="$*"
    _log_is_enabled "$level" || return 0
    local ts stage sn st
    ts=$(_log_ts); stage="${LOG_STAGE:-}"; sn="${LOG_STEP_NUM:-}"; st="${LOG_STEP_TOTAL:-}"

    if [ "$LOG_FORMAT" = "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local em="${message//\"/\\\"}"
        local jf="\"ts\":\"$ts\",\"level\":\"${level,,}\",\"service\":\"$LOG_SERVICE\",\"message\":\"$em\""
        [ -n "$stage" ] && jf="$jf,\"stage\":\"$stage\""
        [ -n "$sn" ] && jf="$jf,\"step\":$sn"
        [ -n "$st" ] && jf="$jf,\"step_total\":$st"
        local fv fk fval
        for fv in $(set 2>/dev/null | grep '^_LOG_FIELD_' | cut -d= -f1); do
            fk="${fv#_LOG_FIELD_}"; eval "fval=\$$fv"
            jf="$jf,\"${fk}\":\"${fval//\"/\\\"}\""
        done
        _log_ensure_dir
        echo "{$jf}" >> "$LOG_JSON_OUTPUT"
        [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "{$jf}"
    fi

    if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local color tag sp=""
        case "${level^^}" in
            DEBUG) color="$_CLR_GRAY"; tag="DBG" ;;
            INFO)  color="$_CLR_GREEN"; tag="INFO" ;;
            OK)    color="$_CLR_GREEN"; tag="✔" ;;
            WARN)  color="$_CLR_YELLOW"; tag="WARN" ;;
            ERROR|FAIL) color="$_CLR_RED"; tag="ERR" ;;
            FATAL) color="$_CLR_RED"; tag="✘" ;;
            STEP)  color="$_CLR_BOLD$_CLR_BLUE"; tag="" ;;
            *)     color="$_CLR_RESET"; tag="${level^^}" ;;
        esac
        [ -n "$stage" ] && sp="[${stage}]"
        [ -n "$sn" ] && [ -n "$st" ] && sp="$sp[$sn/$st]"
        if [ "${level^^}" = "STEP" ]; then
            echo ""; echo -e "${_CLR_BOLD}${color}━━━ ${message} ━━━${_CLR_RESET}"; echo ""
        else
            printf "  %b%s%b %b%s%b %s\n" "$color" "$tag" "$_CLR_RESET" "$_CLR_GRAY" "$sp" "$_CLR_RESET" "$message"
        fi
    fi
}

# ── 公共 API ──
log_debug() { _log_emit DEBUG "$@"; }
log_info()  { _log_emit INFO "$@"; }
log_ok()    { _log_emit OK "$@"; }
log_warn()  { _log_emit WARN "$@"; }
log_error() { _log_emit ERROR "$@"; }
log_fail()  { _log_emit FAIL "$@"; }
log_fatal() { _log_emit FATAL "$@"; exit 1; }
log_step()  { _log_emit STEP "$@"; }

log_metric() {
    local name="$1" value="$2" unit="${3:-}" ts
    ts=$(_log_ts); _log_ensure_dir
    local jl="{\"ts\":\"$ts\",\"type\":\"metric\",\"service\":\"$LOG_SERVICE\",\"metric\":\"$name\",\"value\":$value,\"unit\":\"$unit\"}"
    echo "$jl" >> "$LOG_JSON_OUTPUT"
    if [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then echo "$jl"
    elif [ "$LOG_FORMAT" != "json" ]; then _log_emit INFO "METRIC $name=$value $unit"; fi
}

log_event() {
    local event="$1"; shift; local ts kvs="" kv
    ts=$(_log_ts)
    for kv in "$@"; do kvs="$kvs,\"${kv%%=*}\":\"${kv#*=}\""; done
    _log_ensure_dir
    local jl="{\"ts\":\"$ts\",\"type\":\"event\",\"service\":\"$LOG_SERVICE\",\"event\":\"$event\"${kvs}}"
    echo "$jl" >> "$LOG_JSON_OUTPUT"
    if [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then echo "$jl"
    elif [ "$LOG_FORMAT" != "json" ]; then _log_emit INFO "EVENT $event $*"; fi
}

log_summary() {
    local pass="$1" fail="$2" total="$3" dur="$4" status="$5" ts
    ts=$(_log_ts); _log_ensure_dir
    local jl="{\"ts\":\"$ts\",\"type\":\"summary\",\"service\":\"$LOG_SERVICE\",\"passed\":$pass,\"failed\":$fail,\"total\":$total,\"duration_seconds\":$dur,\"status\":\"$status\"}"
    echo "$jl" >> "$LOG_JSON_OUTPUT"
    if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        echo ""
        echo -e "${_CLR_BOLD}┌─────────────────────────────────────────┐${_CLR_RESET}"
        echo -e "${_CLR_BOLD}│            结果汇总                      │${_CLR_RESET}"
        echo -e "${_CLR_BOLD}├─────────────────────────────────────────┤${_CLR_RESET}"
        if [ "$status" = "success" ] || [ "$fail" -eq 0 ]; then
            echo -e "${_CLR_BOLD}│${_CLR_RESET}  状态: ${_CLR_GREEN}PASS${_CLR_RESET}"
        else
            echo -e "${_CLR_BOLD}│${_CLR_RESET}  状态: ${_CLR_RED}FAIL${_CLR_RESET}"
        fi
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  通过: ${_CLR_GREEN}${pass}${_CLR_RESET} 项"
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  失败: ${_CLR_RED}${fail}${_CLR_RESET} 项"
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  总计: ${total} 项"
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  耗时: ${dur}s"
        echo -e "${_CLR_BOLD}└─────────────────────────────────────────┘${_CLR_RESET}"
        echo ""
    fi
}

log_parse_args() {
    local args=()
    for arg in "$@"; do
        case "$arg" in
            --log-format=*)      echo "LOG_FORMAT='${arg#*=}';" ;;
            --log-level=*)       echo "LOG_LEVEL='${arg#*=}';" ;;
            --log-json)          echo "LOG_JSON_STDOUT=1;" ;;
            --log-json-output=*) echo "LOG_JSON_OUTPUT='${arg#*=}';" ;;
            --log-service=*)     echo "LOG_SERVICE='${arg#*=}';" ;;
            *)                   args+=("$arg") ;;
        esac
    done
    printf 'set -- '; printf '%q ' "${args[@]}"; echo ""
}
