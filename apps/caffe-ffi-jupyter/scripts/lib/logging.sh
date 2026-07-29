#!/bin/bash
# =============================================================================
# lib/logging.sh — 统一结构化日志库
# 提供人类可读+机器可解析的日志输出，适配自动化监控平台
# 用法: source "$(dirname "$0")/lib/logging.sh"
# =============================================================================

# ── 日志格式配置 ──
# LOG_FORMAT: "text" (默认, 人类可读) | "json" (JSON Lines, 适合监控采集)
# LOG_LEVEL: DEBUG < INFO < WARN < ERROR < FATAL (默认 INFO)
LOG_FORMAT="${LOG_FORMAT:-text}"
LOG_LEVEL="${LOG_LEVEL:-INFO}"
LOG_SERVICE="${LOG_SERVICE:-caffe-ffi-deploy}"
LOG_JSON_OUTPUT="${LOG_JSON_OUTPUT:-/tmp/caffe-ffi-events.jsonl}"

# ── 颜色定义（仅 text 模式使用） ──
if [ -t 1 ] || [ "${LOG_FORCE_COLOR:-0}" = "1" ]; then
    _CLR_RESET='\033[0m'
    _CLR_RED='\033[0;31m'
    _CLR_GREEN='\033[0;32m'
    _CLR_YELLOW='\033[1;33m'
    _CLR_BLUE='\033[0;34m'
    _CLR_CYAN='\033[0;36m'
    _CLR_GRAY='\033[0;90m'
    _CLR_BOLD='\033[1m'
else
    _CLR_RESET='' _CLR_RED='' _CLR_GREEN='' _CLR_YELLOW=''
    _CLR_BLUE='' _CLR_CYAN='' _CLR_GRAY='' _CLR_BOLD=''
fi

# ── 内部工具函数 ──
_log_level_num() {
    case "${1^^}" in
        DEBUG) echo 0 ;;
        INFO)  echo 1 ;;
        OK)    echo 1 ;;  # OK 同 INFO 级别
        WARN)  echo 2 ;;
        ERROR) echo 3 ;;
        FAIL)  echo 3 ;;  # FAIL 同 ERROR 级别
        FATAL) echo 4 ;;
        STEP)  echo 1 ;;  # STEP 同 INFO 级别
        *)     echo 1 ;;
    esac
}

_log_is_enabled() {
    local level_num
    level_num=$(_log_level_num "$1")
    local current_num
    current_num=$(_log_level_num "$LOG_LEVEL")
    [ "$level_num" -ge "$current_num" ]
}

_log_ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u
}

# ── 结构化字段设置 ──
# 当前阶段/步骤，用于日志上下文追踪
LOG_STAGE=""
LOG_STEP_NUM=""
LOG_STEP_TOTAL=""

log_set_stage() {
    LOG_STAGE="$1"
    if [ $# -ge 3 ]; then
        LOG_STEP_NUM="$2"
        LOG_STEP_TOTAL="$3"
    fi
}

log_set_field() {
    # 设置额外键值对，会附加到 JSON 日志中
    # 用法: log_set_field key value
    local key="$1"
    local value="$2"
    export "_LOG_FIELD_${key}=${value}"
}

# ── 核心日志输出函数 ──
_log_emit() {
    local level="$1"
    shift
    local message="$*"
    local ts
    ts=$(_log_ts)
    local stage="${LOG_STAGE:-}"
    local step_num="${LOG_STEP_NUM:-}"
    local step_total="${LOG_STEP_TOTAL:-}"

    # 级别过滤
    _log_is_enabled "$level" || return 0

    # JSON Lines 输出（写入 _LOG_JSON_OUTPUT 文件，同时可选择输出到 stdout）
    if [ "$LOG_FORMAT" = "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local json_fields="\"ts\":\"$ts\",\"level\":\"${level^^}\",\"service\":\"$LOG_SERVICE\",\"message\":\"${message//\"/\\\"}\""
        [ -n "$stage" ] && json_fields="$json_fields,\"stage\":\"$stage\""
        [ -n "$step_num" ] && json_fields="$json_fields,\"step\":$step_num"
        [ -n "$step_total" ] && json_fields="$json_fields,\"step_total\":$step_total"
        # 附加自定义字段
        local field_var field_key field_val
        for field_var in $(set | grep '^_LOG_FIELD_' | cut -d= -f1); do
            field_key="${field_var#_LOG_FIELD_}"
            eval "field_val=\$$field_var"
            json_fields="$json_fields,\"${field_key}\":\"${field_val//\"/\\\"}\""
        done
        echo "{$json_fields}" >> "$LOG_JSON_OUTPUT"
        if [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
            echo "{$json_fields}"
        fi
    fi

    # Text 模式输出到 stdout（默认）
    if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local color=""
        case "${level^^}" in
            DEBUG) color="$_CLR_GRAY" ;;
            INFO)  color="$_CLR_GREEN" ;;
            OK)    color="$_CLR_GREEN" ;;
            WARN)  color="$_CLR_YELLOW" ;;
            ERROR|FAIL|FATAL) color="$_CLR_RED" ;;
            STEP)  color="$_CLR_BOLD$_CLR_BLUE" ;;
        esac

        local prefix=""
        local stage_prefix=""
        [ -n "$stage" ] && stage_prefix="[${stage}]"
        if [ -n "$step_num" ] && [ -n "$step_total" ]; then
            stage_prefix="$stage_prefix[$step_num/$step_total]"
        fi

        if [ "${level^^}" = "STEP" ]; then
            echo ""
            echo -e "${_CLR_BOLD}${color}━━━ ${message} ━━━${_CLR_RESET}"
            echo ""
        else
            local tag
            case "${level^^}" in
                OK)    tag="✔" ;;
                FAIL)  tag="✘" ;;
                INFO)  tag="INFO" ;;
                WARN)  tag="WARN" ;;
                ERROR) tag="ERR" ;;
                DEBUG) tag="DBG" ;;
                *)     tag="${level^^}" ;;
            esac
            printf "  %b%s%b %b%s%b %s\n" "$color" "$tag" "$_CLR_RESET" "$_CLR_GRAY" "$stage_prefix" "$_CLR_RESET" "$message"
        fi
    fi
}

# ── 公共日志 API ──
log_debug() { _log_emit DEBUG "$@"; }
log_info()  { _log_emit INFO "$@"; }
log_ok()    { _log_emit OK "$@"; }
log_warn()  { _log_emit WARN "$@"; }
log_error() { _log_emit ERROR "$@"; }
log_fail()  { _log_emit FAIL "$@"; }
log_fatal() { _log_emit FATAL "$@"; exit 1; }
log_step()  { _log_emit STEP "$@"; }

# ── 指标/事件输出（用于监控平台聚合） ──
log_metric() {
    # 输出数值指标: log_metric <name> <value> [unit]
    local name="$1" value="$2" unit="${3:-}"
    local ts
    ts=$(_log_ts)
    local metric_line=""
    if [ "$LOG_FORMAT" = "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        metric_line="{\"ts\":\"$ts\",\"type\":\"metric\",\"service\":\"$LOG_SERVICE\",\"metric\":\"$name\",\"value\":$value,\"unit\":\"$unit\"}"
        echo "$metric_line" >> "$LOG_JSON_OUTPUT"
        [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "$metric_line"
    else
        _log_emit INFO "METRIC $name=$value $unit"
    fi
}

log_event() {
    # 输出生命周期事件: log_event <event_name> [key=value ...]
    local event="$1"; shift
    local ts
    ts=$(_log_ts)
    local kv_str=""
    for kv in "$@"; do
        kv_str="$kv_str,\"${kv%%=*}\":\"${kv#*=}\""
    done
    local event_line="{\"ts\":\"$ts\",\"type\":\"event\",\"service\":\"$LOG_SERVICE\",\"event\":\"$event\"${kv_str}}"
    echo "$event_line" >> "$LOG_JSON_OUTPUT"
    if [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        echo "$event_line"
    else
        _log_emit INFO "EVENT $event $*"
    fi
}

# ── 结果摘要输出 ──
log_summary() {
    # 输出最终结果摘要，监控平台可解析此格式
    local pass="$1" fail="$2" total="$3" duration="$4" status="$5"
    local ts
    ts=$(_log_ts)
    local summary_line="{\"ts\":\"$ts\",\"type\":\"summary\",\"service\":\"$LOG_SERVICE\",\"passed\":$pass,\"failed\":$fail,\"total\":$total,\"duration_seconds\":$duration,\"status\":\"$status\"}"
    echo "$summary_line" >> "$LOG_JSON_OUTPUT"

    if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        echo ""
        echo -e "${_CLR_BOLD}┌─────────────────────────────────────────┐${_CLR_RESET}"
        echo -e "${_CLR_BOLD}│       部署验证结果汇总                   │${_CLR_RESET}"
        echo -e "${_CLR_BOLD}├─────────────────────────────────────────┤${_CLR_RESET}"
        if [ "$status" = "success" ] || [ "$fail" -eq 0 ]; then
            echo -e "${_CLR_BOLD}│${_CLR_RESET}  状态: ${_CLR_GREEN}PASS${_CLR_RESET}"
        else
            echo -e "${_CLR_BOLD}│${_CLR_RESET}  状态: ${_CLR_RED}FAIL${_CLR_RESET}"
        fi
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  通过: ${_CLR_GREEN}${pass}${_CLR_RESET} 项"
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  失败: ${_CLR_RED}${fail}${_CLR_RESET} 项"
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  总计: ${total} 项"
        echo -e "${_CLR_BOLD}│${_CLR_RESET}  耗时: ${duration}s"
        echo -e "${_CLR_BOLD}└─────────────────────────────────────────┘${_CLR_RESET}"
        echo ""
    fi
}

# ── 参数解析辅助：从命令行中提取日志相关参数 ──
log_parse_args() {
    # 在脚本中调用: eval "$(log_parse_args "$@")" 来提取 --log-format/--log-level/--log-json
    local args=()
    for arg in "$@"; do
        case "$arg" in
            --log-format=*)
                echo "LOG_FORMAT='${arg#*=}';"
                ;;
            --log-level=*)
                echo "LOG_LEVEL='${arg#*=}';"
                ;;
            --log-json)
                echo "LOG_JSON_STDOUT=1;"
                ;;
            --log-json-output=*)
                echo "LOG_JSON_OUTPUT='${arg#*=}';"
                ;;
            --log-service=*)
                echo "LOG_SERVICE='${arg#*=}';"
                ;;
            *)
                args+=("$arg")
                ;;
        esac
    done
    # 输出剩余参数（用于 set -- 重置位置参数）
    printf 'set -- '
    printf '%q ' "${args[@]}"
    echo ""
}
