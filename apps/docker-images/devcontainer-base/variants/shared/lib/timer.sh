#!/bin/bash
# =============================================================================
# lib/timer.sh — 变体构建计时器模块
#
# 提供统一的构建阶段计时功能，修复"清理 /tmp /var/tmp 删除计时器文件"的已知bug
# 计时器文件存储在 /root/.variant-timers/ 目录（不会被激进清理）
#
# 用法 (在 RUN heredoc 开头 source variant-framework.sh 后):
#   variant_timer_start "variant-name"
#   ... 阶段1工作 ...
#   variant_timer_stage 1 "mirror config + verify"
#   ... 阶段2工作 ...
#   variant_timer_stage 2 "package install"
#   ...
#   variant_timer_summary "Variant Name"
#
# 输出格式与现有变体完全兼容：
#   [TIMER] <variant> variant build started at <timestamp>
#   [TIMER] Stage X/Y <desc> took Ns | Variant cumulative: Ms
#   BUILD TIMING SUMMARY 表格（╔═╗║╠╣╚╝ 边框）
# =============================================================================

_VARIANT_TIMER_DIR="/root/.variant-timers"

# 确保计时器目录存在
_variant_timer_ensure_dir() {
    if [ ! -d "$_VARIANT_TIMER_DIR" ]; then
        mkdir -p "$_VARIANT_TIMER_DIR"
    fi
}

# 获取计时器文件路径
_variant_timer_file() {
    local variant_name="$1"
    echo "${_VARIANT_TIMER_DIR}/.${variant_name}-build-timer"
}

# 初始化计时器
# 用法: variant_timer_start <variant_name>
variant_timer_start() {
    local variant_name="$1"
    local now
    now=$(date +%s)
    local iso_ts
    iso_ts=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    _variant_timer_ensure_dir

    local timer_file
    timer_file=$(_variant_timer_file "$variant_name")

    # 写入计时器初始数据
    cat > "$timer_file" <<EOF
START_TIME=${now}
VARIANT_NAME=${variant_name}
STAGE_COUNT=0
EOF

    echo "[TIMER] ${variant_name} variant build started at ${iso_ts}"
}

# 安全获取单个值（取最后一个匹配，清理换行符）
_variant_timer_get_val() {
    local key="$1"
    local file="$2"
    grep "^${key}=" "$file" | tail -1 | cut -d= -f2 | tr -d '\r\n'
}

# 记录一个阶段完成
# 用法: variant_timer_stage <stage_num> <description>
variant_timer_stage() {
    local stage_num="$1"
    shift
    local desc="$*"
    local now
    now=$(date +%s)

    # 需要在调用者上下文中知道 variant_name — 从环境变量或最近计时器文件获取
    # 为简化使用，自动检测最近的计时器文件
    local timer_file
    timer_file=$(ls -t "${_VARIANT_TIMER_DIR}"/.*-build-timer 2>/dev/null | head -1)

    if [ -z "$timer_file" ] || [ ! -f "$timer_file" ]; then
        echo "[ERROR] variant_timer_stage called before variant_timer_start" >&2
        return 1
    fi

    # 读取开始时间
    local start_time
    start_time=$(_variant_timer_get_val "START_TIME" "$timer_file")
    local stage_count
    stage_count=$(_variant_timer_get_val "STAGE_COUNT" "$timer_file")
    stage_count=$((stage_count + 1))

    # 计算时间差
    local stage_elapsed
    local cumulative

    if [ "$stage_count" -eq 1 ]; then
        stage_elapsed=$((now - start_time))
    else
        # 读取上一阶段的时间
        local prev_stage_key="STAGE_$((stage_count - 1))_TIME"
        local prev_stage_time
        prev_stage_time=$(_variant_timer_get_val "$prev_stage_key" "$timer_file")
        stage_elapsed=$((now - prev_stage_time))
    fi
    cumulative=$((now - start_time))

    # 先移除旧的STAGE_COUNT，再写入新阶段数据和新的STAGE_COUNT
    grep -v '^STAGE_COUNT=' "$timer_file" > "${timer_file}.tmp" && mv "${timer_file}.tmp" "$timer_file"
    {
        echo "STAGE_${stage_count}_DESC=${desc}"
        echo "STAGE_${stage_count}_TIME=${now}"
        echo "STAGE_COUNT=${stage_count}"
    } >> "$timer_file"

    local variant_name
    variant_name=$(_variant_timer_get_val "VARIANT_NAME" "$timer_file")

    echo "[TIMER] Stage ${stage_num} (${desc}) took ${stage_elapsed}s | ${variant_name} cumulative: ${cumulative}s"
}

# 输出构建计时汇总表
# 用法: variant_timer_summary [display_title]
# display_title 可选，默认使用 VARIANT_NAME
variant_timer_summary() {
    local display_title="${1:-}"

    local timer_file
    timer_file=$(ls -t "${_VARIANT_TIMER_DIR}"/.*-build-timer 2>/dev/null | head -1)

    if [ -z "$timer_file" ] || [ ! -f "$timer_file" ]; then
        echo "[WARN] No timer data found, skipping summary" >&2
        return 0
    fi

    # 读取数据
    local start_time
    start_time=$(_variant_timer_get_val "START_TIME" "$timer_file")
    local variant_name
    variant_name=$(_variant_timer_get_val "VARIANT_NAME" "$timer_file")
    local stage_count
    stage_count=$(_variant_timer_get_val "STAGE_COUNT" "$timer_file")
    local end_time
    end_time=$(date +%s)
    local total_elapsed
    total_elapsed=$((end_time - start_time))

    if [ -z "$display_title" ]; then
        display_title="${variant_name} Variant - ${stage_count} Stages"
    fi

    # 计算每个阶段的耗时
    local stage_times=()
    local stage_descs=()
    local prev_time="$start_time"

    for i in $(seq 1 "$stage_count"); do
        local desc_key="STAGE_${i}_DESC"
        local time_key="STAGE_${i}_TIME"
        local desc
        desc=$(_variant_timer_get_val "$desc_key" "$timer_file")
        local stage_time
        stage_time=$(_variant_timer_get_val "$time_key" "$timer_file")
        local elapsed=$((stage_time - prev_time))
        stage_times+=("$elapsed")
        stage_descs+=("$desc")
        prev_time="$stage_time"
    done

    # 如果最后一个阶段结束时间到现在还有时间，算到最后一个阶段
    # （允许在 summary 前执行清理等工作，时间会计入最后一个阶段）
    local last_elapsed=$((end_time - prev_time))
    if [ "$last_elapsed" -gt 0 ] && [ "$stage_count" -gt 0 ]; then
        stage_times[$((stage_count - 1))]=$((stage_times[$((stage_count - 1))] + last_elapsed))
    fi

    # 输出汇总表（与现有变体格式完全一致）
    echo "╔══════════════════════════════════════════════════════════════╗"
    printf "║  BUILD TIMING SUMMARY (%-35s)  ║\n" "$display_title"
    echo "╠══════════════════════════════════════════════════════════════╣"

    local total_label="${variant_name^^} VARIANT TOTAL (add-on)"

    for i in $(seq 0 $((stage_count - 1))); do
        local stage_num=$((i + 1))
        local stage_label="Stage ${stage_num}/${stage_count}"
        local desc="${stage_descs[$i]}"
        local elapsed="${stage_times[$i]}"
        # 截断描述以适配宽度，与原始格式一致
        local formatted_desc
        formatted_desc=$(printf "%-28s" "$desc" | cut -c1-28)
        printf "║  %-9s %-28s  %5ds               ║\n" "$stage_label" "$formatted_desc" "$elapsed"
    done

    echo "╠══════════════════════════════════════════════════════════════╣"
    printf "║  %-38s  %5ds               ║\n" "$total_label" "$total_elapsed"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # 清理计时器文件
    rm -f "$timer_file"
}
