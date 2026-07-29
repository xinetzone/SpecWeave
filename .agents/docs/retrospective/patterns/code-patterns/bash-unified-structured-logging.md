---
id: "bash-unified-structured-logging"
title: "Bash脚本统一结构化日志库模式"
type: "code-pattern"
date: "2026-07-29"
maturity: "L2-validated"
source: "retrospective-caffe-ffi-wsl-tooling-20260729"
related_patterns: ["dual-channel-tiered-logging", "core-entry-structured-logging", "script-json-output-contract", "cli-json-pipeline"]
tags: ["bash", "logging", "observability", "monitoring", "json-lines", "shell-scripting", "structured-output"]
---

# Bash脚本统一结构化日志库模式

## 问题

Bash Shell脚本传统上使用`echo`输出面向人类的文本日志，但在自动化场景下面临矛盾需求：

1. **人类可读**：开发者在终端执行时需要带颜色的、简洁的文本输出
2. **机器可解析**：CI/CD流水线、监控平台需要结构化数据（JSON）来判断成功/失败、采集指标
3. **多脚本统一**：项目中多个脚本各自定义`RED/GREEN/NC`颜色变量和echo格式，输出不一致
4. **指标与事件**：仅有文本日志不足以支撑监控，需要数值指标（metric）和生命周期事件（event）

Bash生态没有Python `logging`模块那样的标准日志框架，导致每个项目都重复造轮子。

## 解决方案

创建独立的 `lib/logging.sh` 日志库文件，所有脚本通过 `source` 加载，提供统一的双格式（text/json）、三类输出（log/metric/event）的日志API。

### 核心设计

```
┌─────────────────────────────────────────────────┐
│              lib/logging.sh                     │
├─────────────────────────────────────────────────┤
│  配置层：LOG_FORMAT / LOG_LEVEL / LOG_SERVICE   │
│  颜色层：_CLR_* (仅text模式，tty检测自动禁用)    │
├─────────────────────────────────────────────────┤
│  输出原语：                                      │
│  ├─ log_debug / log_info / log_ok / log_warn   │
│  ├─ log_error / log_fail / log_fatal / log_step │
│  ├─ log_metric(name, value, unit)              │
│  ├─ log_event(name, key=value...)              │
│  └─ log_summary(pass, fail, total, dur, status)│
├─────────────────────────────────────────────────┤
│  上下文：log_set_field(key, val) → _LOG_FIELD_* │
│  输出目标：stdout(text) + JSONL文件 + 可选stdout │
└─────────────────────────────────────────────────┘
```

## 代码

### 日志库骨架（lib/logging.sh）

```bash
#!/bin/bash
# lib/logging.sh — 统一结构化日志库

LOG_FORMAT="${LOG_FORMAT:-text}"        # text | json
LOG_LEVEL="${LOG_LEVEL:-INFO}"         # DEBUG|INFO|WARN|ERROR|FATAL
LOG_SERVICE="${LOG_SERVICE:-unknown}"
LOG_JSON_OUTPUT="${LOG_JSON_OUTPUT:-/tmp/events.jsonl}"
LOG_JSON_STDOUT="${LOG_JSON_STDOUT:-0}"

# 颜色定义（非tty自动禁用）
if [ -t 1 ] || [ "${LOG_FORCE_COLOR:-0}" = "1" ]; then
    _CLR_RESET='\033[0m'; _CLR_RED='\033[0;31m'; _CLR_GREEN='\033[0;32m'
    _CLR_YELLOW='\033[1;33m'; _CLR_BLUE='\033[0;34m'; _CLR_CYAN='\033[0;36m'
    _CLR_GRAY='\033[0;90m'; _CLR_BOLD='\033[1m'
else
    _CLR_RESET='' _CLR_RED='' _CLR_GREEN='' _CLR_YELLOW=''
    _CLR_BLUE='' _CLR_CYAN='' _CLR_GRAY='' _CLR_BOLD=''
fi

# 级别数值化
_log_level_num() {
    case "${1^^}" in
        DEBUG) echo 0 ;; INFO|OK|STEP) echo 1 ;; WARN) echo 2 ;;
        ERROR|FAIL) echo 3 ;; FATAL) echo 4 ;; *) echo 1 ;;
    esac
}

# 核心输出函数（内部）
_log_emit() {
    local level="$1"; shift; local message="$*"
    local ts; ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

    # 级别过滤
    [ "$(_log_level_num "$level")" -lt "$(_log_level_num "$LOG_LEVEL")" ] && return 0

    # JSON输出（始终写入文件，可选stdout）
    if [ "$LOG_FORMAT" = "json" ] || [ "$LOG_JSON_STDOUT" = "1" ]; then
        local json="\"ts\":\"$ts\",\"level\":\"${level^^}\",\"service\":\"$LOG_SERVICE\",\"message\":\"${message//\"/\\\"}\""
        # 附加上下文字段
        for fv in $(set | grep '^_LOG_FIELD_' | cut -d= -f1); do
            local fk="${fv#_LOG_FIELD_}"; eval "local fvv=\$$fv"
            json="$json,\"${fk}\":\"${fvv//\"/\\\"}\""
        done
        echo "{$json}" >> "$LOG_JSON_OUTPUT"
        [ "$LOG_JSON_STDOUT" = "1" ] && echo "{$json}"
    fi

    # Text输出
    if [ "$LOG_FORMAT" != "json" ] || [ "$LOG_JSON_STDOUT" = "1" ]; then
        local color; case "${level^^}" in
            DEBUG) color="$_CLR_GRAY" ;; INFO|OK) color="$_CLR_GREEN" ;;
            WARN) color="$_CLR_YELLOW" ;; ERROR|FAIL|FATAL) color="$_CLR_RED" ;;
            STEP) color="$_CLR_BOLD$_CLR_BLUE" ;;
        esac
        if [ "${level^^}" = "STEP" ]; then
            echo ""; echo -e "${_CLR_BOLD}${color}━━━ ${message} ━━━${_CLR_RESET}"; echo ""
        else
            local tag; case "${level^^}" in
                OK) tag="✔" ;; FAIL) tag="✘" ;; INFO) tag="INFO" ;;
                WARN) tag="WARN" ;; ERROR) tag="ERR" ;; DEBUG) tag="DBG" ;;
            esac
            printf "  %b%s%b %s\n" "$color" "$tag" "$_CLR_RESET" "$message"
        fi
    fi
}

# 公共API
log_debug() { _log_emit DEBUG "$@"; }
log_info()  { _log_emit INFO "$@"; }
log_ok()    { _log_emit OK "$@"; }
log_warn()  { _log_emit WARN "$@"; }
log_error() { _log_emit ERROR "$@"; }
log_fail()  { _log_emit FAIL "$@"; }
log_fatal() { _log_emit FATAL "$@"; exit 1; }
log_step()  { _log_emit STEP "$@"; }

# 数值指标
log_metric() {
    local name="$1" value="$2" unit="${3:-}"
    local ts; ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local line="{\"ts\":\"$ts\",\"type\":\"metric\",\"service\":\"$LOG_SERVICE\",\"metric\":\"$name\",\"value\":$value,\"unit\":\"$unit\"}"
    echo "$line" >> "$LOG_JSON_OUTPUT"
    [ "$LOG_JSON_STDOUT" = "1" ] && echo "$line"
    [ "$LOG_FORMAT" != "json" ] && [ "$LOG_JSON_STDOUT" != "1" ] && _log_emit INFO "METRIC $name=$value $unit"
}

# 生命周期事件
log_event() {
    local event="$1"; shift
    local ts; ts=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    local kv=""; for p in "$@"; do kv="$kv,\"${p%%=*}\":\"${p#*=}\""; done
    local line="{\"ts\":\"$ts\",\"type\":\"event\",\"service\":\"$LOG_SERVICE\",\"event\":\"$event\"$kv}"
    echo "$line" >> "$LOG_JSON_OUTPUT"
    [ "$LOG_JSON_STDOUT" = "1" ] && echo "$line"
    [ "$LOG_FORMAT" != "json" ] && [ "$LOG_JSON_STDOUT" != "1" ] && _log_emit INFO "EVENT $event $*"
}

# 上下文设置
log_set_field() { export "_LOG_FIELD_${1}=${2}"; }
```

### 在脚本中使用

```bash
#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="my-deploy-script"

# 参数解析中提取日志参数
while [[ $# -gt 0 ]]; do
    case "$1" in
        --log-format=*) LOG_FORMAT="${1#*=}"; shift ;;
        --log-level=*)  LOG_LEVEL="${1#*=}"; shift ;;
        --log-json)     LOG_JSON_STDOUT=1; shift ;;
        # ... 其他参数
        -h|--help) usage; exit 0 ;;
        *) shift ;;
    esac
done

# 记录启动上下文
log_set_field "container" "$CONTAINER_NAME"
log_event "deploy_start" "version=$VERSION"

# 分阶段输出
log_step "阶段 1/3: 环境检查"
log_info "Docker 引擎可用"
log_ok "所有前置条件满足"

# 记录指标
BUILD_START=$(date +%s)
# ... 构建过程 ...
BUILD_DURATION=$(($(date +%s) - BUILD_START))
log_metric "build_duration_seconds" "$BUILD_DURATION" "seconds"

# 完成事件
log_event "deploy_complete" "status=success" "duration=${BUILD_DURATION}s"
log_summary "$PASS" "$FAIL" "$TOTAL" "$DURATION" "success"
```

### 监控平台接入示例

```bash
# JSON Lines输出，供Filebeat/Fluentd采集
bash scripts/deploy.sh --cn --log-format=json

# 提取关键指标
cat /tmp/caffe-ffi-events.jsonl | jq 'select(.type=="metric")'
cat /tmp/caffe-ffi-events.jsonl | jq 'select(.event=="deploy_complete") | .status'
```

## 反模式

- ❌ **每个脚本自定义颜色变量**：`RED='\033[0;31m'` 在每个脚本中重复定义
- ❌ **裸echo输出**：`echo "构建成功"` 没有级别、没有结构化字段
- ❌ **用echo做"分隔符"但无事件记录**：`echo "=== 阶段1 ===" ` 在JSON模式下无法解析
- ❌ **不同脚本的成功/失败判断不一致**：一个脚本exit 0代表成功，另一个用grep返回值
- ❌ **日志输出到stderr但不说明**：导致CI捕获混乱
- ❌ **颜色码硬编码在非tty环境**：重定向到文件时产生乱码

## 与现有模式的关系

| 模式 | 语言 | 焦点 | 区别 |
|------|------|------|------|
| dual-channel-tiered-logging | Python | 控制台/文件双Handler，不同级别 | Python特有，Handler级粒度控制 |
| core-entry-structured-logging | Python | 函数入口/出口的黄金三要素(shape/range/duration) | Python特有，调试追踪粒度 |
| script-json-output-contract | 通用 | `--json` 标志的最小契约(ok/error) | 本模式更完整：metric/event/summary |
| cli-json-pipeline | 通用 | CLI命令间JSON管道传递 | 本模式关注日志而非数据传递 |
| **本模式** | **Bash** | **全脚本统一日志抽象层，text+json双格式** | **Bash生态特有，填补空白** |
