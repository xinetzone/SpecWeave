#!/bin/bash
# =============================================================================
# TEMPLATE: lib/logging.sh — Bash 统一结构化日志库
# =============================================================================
# 功能：提供人类可读(text) + 机器可解析(json)双格式日志输出
#       支持级别过滤、数值指标(metric)、生命周期事件(event)、结果摘要(summary)
#       适配自动化监控平台（Prometheus/Grafana/ELK/Filebeat/Fluentd）
#
# 复用方法：
#   1. 将本文件复制到你的项目 scripts/lib/logging.sh
#   2. 修改默认 LOG_SERVICE 和 LOG_JSON_OUTPUT 路径
#   3. 在你的脚本中 source 加载（见下方使用示例）
#
# 使用示例：
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/lib/logging.sh"
#   LOG_SERVICE="my-service"
#
#   log_set_field "container" "$CONTAINER_NAME"
#   log_event "service_start" "version=1.0.0"
#   log_step "阶段 1/3: 环境检查"
#   log_info "检查完成"
#   log_metric "build_duration" 42 "seconds"
#   log_event "service_complete" "status=success"
#   log_summary "$PASS" "$FAIL" "$TOTAL" "$DURATION" "success"
# =============================================================================

# ── 日志格式配置（可通过环境变量或参数覆盖） ──
LOG_FORMAT="${LOG_FORMAT:-text}"                         # text | json
LOG_LEVEL="${LOG_LEVEL:-INFO}"                           # DEBUG < INFO < WARN < ERROR < FATAL
LOG_SERVICE="${LOG_SERVICE:-my-service}"                 # 服务标识，用于日志溯源
LOG_JSON_OUTPUT="${LOG_JSON_OUTPUT:-/tmp/events.jsonl}"  # JSON 事件日志文件路径
LOG_JSON_STDOUT="${LOG_JSON_STDOUT:-0}"                  # 1=JSON同时输出到stdout

# ── 颜色定义（非tty自动禁用，避免重定向到文件产生乱码） ──
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
        INFO|OK|STEP) echo 1 ;;
        WARN)  echo 2 ;;
        ERROR|FAIL) echo 3 ;;
        FATAL) echo 4 ;;
        *)     echo 1 ;;
    esac
}

_log_is_enabled() {
    [ "$(_log_level_num "$1")" -ge "$(_log_level_num "$LOG_LEVEL")" ]
}

_log_ts() {
    date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u
}

# ── 上下文字段（自动附加到JSON日志） ──
LOG_STAGE=""
LOG_STEP_NUM=""
LOG_STEP_TOTAL=""

log_set_stage() {
    LOG_STAGE="$1"
    if [ $# -ge 3 ]; then LOG_STEP_NUM="$2"; LOG_STEP_TOTAL="$3"; fi
}

log_set_field() {
    # 设置自定义键值对，自动附加到每条JSON日志
    # 用法: log_set_field <key> <value>
    export "_LOG_FIELD_${1}=${2}"
}

# ── 核心日志输出函数（内部） ──
_log_emit() {
    local level="$1"; shift; local message="$*"
    local ts; ts=$(_log_ts)
    _log_is_enabled "$level" || return 0

    # ── JSON Lines 输出 ──
    if [ "$LOG_FORMAT" = "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local json="\"ts\":\"$ts\",\"level\":\"${level^^}\",\"service\":\"$LOG_SERVICE\",\"message\":\"${message//\"/\\\"}\""
        [ -n "$LOG_STAGE" ] && json="$json,\"stage\":\"$LOG_STAGE\""
        [ -n "$LOG_STEP_NUM" ] && json="$json,\"step\":$LOG_STEP_NUM"
        [ -n "$LOG_STEP_TOTAL" ] && json="$json,\"step_total\":$LOG_STEP_TOTAL"
        # 附加自定义字段
        for fv in $(set 2>/dev/null | grep '^_LOG_FIELD_' | cut -d= -f1); do
            local fk="${fv#_LOG_FIELD_}"
            eval "local fvv=\$$fv"
            json="$json,\"${fk}\":\"${fvv//\"/\\\"}\""
        done
        echo "{$json}" >> "$LOG_JSON_OUTPUT"
        [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "{$json}"
    fi

    # ── Text 人类可读输出 ──
    if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        local color
        case "${level^^}" in
            DEBUG) color="$_CLR_GRAY" ;;
            INFO|OK) color="$_CLR_GREEN" ;;
            WARN) color="$_CLR_YELLOW" ;;
            ERROR|FAIL|FATAL) color="$_CLR_RED" ;;
            STEP) color="$_CLR_BOLD$_CLR_BLUE" ;;
        esac
        local spref=""; [ -n "$LOG_STAGE" ] && spref="[${LOG_STAGE}]"
        [ -n "$LOG_STEP_NUM" ] && [ -n "$LOG_STEP_TOTAL" ] && spref="$spref[$LOG_STEP_NUM/$LOG_STEP_TOTAL]"
        if [ "${level^^}" = "STEP" ]; then
            echo ""; echo -e "${_CLR_BOLD}${color}━━━ ${message} ━━━${_CLR_RESET}"; echo ""
        else
            local tag; case "${level^^}" in
                OK) tag="✔" ;; FAIL) tag="✘" ;; INFO) tag="INFO" ;;
                WARN) tag="WARN" ;; ERROR) tag="ERR" ;; DEBUG) tag="DBG" ;; *) tag="${level^^}" ;;
            esac
            printf "  %b%s%b %b%s%b %s\n" "$color" "$tag" "$_CLR_RESET" "$_CLR_GRAY" "$spref" "$_CLR_RESET" "$message"
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

# ── 数值指标（监控平台聚合用） ──
log_metric() {
    # 用法: log_metric <metric_name> <numeric_value> [unit]
    # 示例: log_metric "build_duration" 42 "seconds"
    local name="$1" value="$2" unit="${3:-}"
    local ts; ts=$(_log_ts)
    local line="{\"ts\":\"$ts\",\"type\":\"metric\",\"service\":\"$LOG_SERVICE\",\"metric\":\"$name\",\"value\":$value,\"unit\":\"$unit\"}"
    echo "$line" >> "$LOG_JSON_OUTPUT"
    [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "$line"
    [ "$LOG_FORMAT" != "json" ] && [ "${LOG_JSON_STDOUT:-0}" != "1" ] && _log_emit INFO "METRIC $name=$value $unit"
}

# ── 生命周期事件 ──
log_event() {
    # 用法: log_event <event_name> [key=value ...]
    # 示例: log_event "deploy_start" "version=1.0" "env=prod"
    local event="$1"; shift
    local ts; ts=$(_log_ts)
    local kv=""
    for p in "$@"; do kv="$kv,\"${p%%=*}\":\"${p#*=}\""; done
    local line="{\"ts\":\"$ts\",\"type\":\"event\",\"service\":\"$LOG_SERVICE\",\"event\":\"$event\"$kv}"
    echo "$line" >> "$LOG_JSON_OUTPUT"
    [ "${LOG_JSON_STDOUT:-0}" = "1" ] && echo "$line"
    [ "$LOG_FORMAT" != "json" ] && [ "${LOG_JSON_STDOUT:-0}" != "1" ] && _log_emit INFO "EVENT $event $*"
}

# ── 结果摘要 ──
log_summary() {
    # 用法: log_summary <pass_count> <fail_count> <total_count> <duration_seconds> <status>
    # 示例: log_summary 8 0 8 280 "success"
    local pass="$1" fail="$2" total="$3" duration="$4" status="$5"
    local ts; ts=$(_log_ts)
    local line="{\"ts\":\"$ts\",\"type\":\"summary\",\"service\":\"$LOG_SERVICE\",\"passed\":$pass,\"failed\":$fail,\"total\":$total,\"duration_seconds\":$duration,\"status\":\"$status\"}"
    echo "$line" >> "$LOG_JSON_OUTPUT"
    if [ "$LOG_FORMAT" != "json" ] || [ "${LOG_JSON_STDOUT:-0}" = "1" ]; then
        echo ""
        echo -e "${_CLR_BOLD}┌─────────────────────────────────────────┐${_CLR_RESET}"
        echo -e "${_CLR_BOLD}│              执行结果汇总                │${_CLR_RESET}"
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

# ── 参数解析辅助 ──
log_parse_args() {
    # 在脚本参数解析前调用: eval "$(log_parse_args "$@")"
    # 自动提取 --log-format/--log-level/--log-json/--log-service/--log-json-output
    # 并将剩余参数通过 set -- 重置
    local args=()
    for arg in "$@"; do
        case "$arg" in
            --log-format=*)     echo "LOG_FORMAT='${arg#*=}';" ;;
            --log-level=*)      echo "LOG_LEVEL='${arg#*=}';" ;;
            --log-json)         echo "LOG_JSON_STDOUT=1;" ;;
            --log-json-output=*) echo "LOG_JSON_OUTPUT='${arg#*=}';" ;;
            --log-service=*)    echo "LOG_SERVICE='${arg#*=}';" ;;
            *) args+=("$arg") ;;
        esac
    done
    printf 'set -- '
    printf '%q ' "${args[@]}"
    echo ""
}
