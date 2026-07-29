#!/bin/bash
# =============================================================================
# lib/logging.sh — 统一结构化日志库（通用版）
# 提供人类可读(text) + 机器可解析(JSON Lines)双格式日志，适配自动化监控平台
#
# 用法 (在脚本开头):
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/lib/logging.sh"   # 或根据实际路径调整
#   LOG_SERVICE="my-service"               # 必须设置服务名
#
# 支持参数: LOG_FORMAT(text|json), LOG_LEVEL(DEBUG|INFO|WARN|ERROR),
#           LOG_JSON_STDOUT=1 同时输出JSON到stdout
#
# 公共 API: log_debug/info/ok/warn/error/fail/fatal/step,
#           log_metric <name> <value> [unit], log_event <name> [key=value ...],
#           log_set_stage, log_set_field, log_summary, log_parse_args
# =============================================================================

LOG_FORMAT="${LOG_FORMAT:-text}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_SERVICE="${LOG_SERVICE:-bash-script}"
LOG_JSON_OUTPUT="${LOG_JSON_OUTPUT:-/tmp/${LOG_SERVICE}-events.jsonl}"

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

LOG_STAGE=""; LOG_STEP_NUM=""; LOG_STEP_TOTAL=""
log_set_stage() { LOG_STAGE="$1"; [ $# -ge 3 ] && { LOG_STEP_NUM="$2"; LOG_STEP_TOTAL="$3"; }; }
log_set_field() { export "_LOG_FIELD_${1}=${2}"; }

_log_emit() {
    local level="$1"; shift; local message="$*"
    _log_is_enabled "$level" || return 0
    local ts stage step_num step_total
    ts=$(_log_ts); stage="${LOG_STAGE:-}"; step_num="${LOG_STEP_NUM:-}"; step_total="${LOG_STEP_TOTAL:-}"

    if [ "$LOG_FORMAT" = "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local escaped_msg="${message//\"/\\\"}"
        local json_fields="\"ts\":\"$ts\",\"level\":\"${level,,}\",\"service\":\"$LOG_SERVICE\",\"message\":\"$escaped_msg\""
        [ -n "$stage" ] && json_fields="$json_fields,\"stage\":\"$stage\""
        [ -n "$step_num" ] && json_fields="$json_fields,\"step\":$step_num"
        [ -n "$step_total" ] && json_fields="$json_fields,\"step_total\":$step_total"
        local fv fk fval
        for fv in $(set 2>/dev/null | grep '^_LOG_FIELD_' | cut -d= -f1); do
            fk="${fv#_LOG_FIELD_}"; eval "fval=\$$fv"
            json_fields="$json_fields,\"${fk}\":\"${fval//\"/\\\"}\""
        done
        local jl="{$json_fields}"
        local jd; jd="$(dirname "$LOG_JSON_OUTPUT")"; [ -d "$jd" ] || mkdir -p "$jd" 2>/dev/null || true
        echo "$jl" >> "$LOG_JSON_OUTPUT"
        [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "$jl"
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
        [ -n "$step_num" ] && [ -n "$step_total" ] && sp="$sp[$step_num/$step_total]"
        if [ "${level^^}" = "STEP" ]; then
            echo ""; echo -e "${_CLR_BOLD}${color}━━━ ${message} ━━━${_CLR_RESET}"; echo ""
        else
            printf "  %b%s%b %b%s%b %s\n" "$color" "$tag" "$_CLR_RESET" "$_CLR_GRAY" "$sp" "$_CLR_RESET" "$message"
        fi
    fi
}

_log_debug() { _log_emit DEBUG "$@"; }
_log_info()  { _log_emit INFO "$@"; }
_log_ok()    { _log_emit OK "$@"; }
_log_warn()  { _log_emit WARN "$@"; }
_log_error() { _log_emit ERROR "$@"; }
_log_fail()  { _log_emit FAIL "$@"; }
_log_fatal() { _log_emit FATAL "$@"; exit 1; }
_log_step()  { _log_emit STEP "$@"; }

log_metric() {
    local name="$1" value="$2" unit="${3:-}" ts jd
    ts=$(_log_ts)
    local jl="{\"ts\":\"$ts\",\"type\":\"metric\",\"service\":\"$LOG_SERVICE\",\"metric\":\"$name\",\"value\":$value,\"unit\":\"$unit\"}"
    jd="$(dirname "$LOG_JSON_OUTPUT")"; [ -d "$jd" ] || mkdir -p "$jd" 2>/dev/null || true
    echo "$jl" >> "$LOG_JSON_OUTPUT"
    if [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then echo "$jl"
    elif [ "$LOG_FORMAT" != "json" ]; then _log_info "METRIC $name=$value $unit"; fi
}

log_event() {
    local event="$1"; shift; local ts kvs="" jd kv
    ts=$(_log_ts)
    for kv in "$@"; do kvs="$kvs,\"${kv%%=*}\":\"${kv#*=}\""; done
    local jl="{\"ts\":\"$ts\",\"type\":\"event\",\"service\":\"$LOG_SERVICE\",\"event\":\"$event\"${kvs}}"
    jd="$(dirname "$LOG_JSON_OUTPUT")"; [ -d "$jd" ] || mkdir -p "$jd" 2>/dev/null || true
    echo "$jl" >> "$LOG_JSON_OUTPUT"
    if [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then echo "$jl"
    elif [ "$LOG_FORMAT" != "json" ]; then _log_info "EVENT $event $*"; fi
}

log_summary() {
    local ts jd
    ts=$(_log_ts)
    local jl="{\"ts\":\"$ts\",\"type\":\"summary\",\"service\":\"$LOG_SERVICE\"}"
    jd="$(dirname "$LOG_JSON_OUTPUT")"; [ -d "$jd" ] || mkdir -p "$jd" 2>/dev/null || true
    echo "$jl" >> "$LOG_JSON_OUTPUT"
    [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "$jl"
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
    if [ ${#args[@]} -eq 0 ]; then
        echo "set --"
    else
        printf 'set -- '; printf '%q ' "${args[@]}"; echo ""
    fi
}
