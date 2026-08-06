#!/usr/bin/env bash
# check-conflicts.sh - Git 网盘同步冲突检测 Bash 函数库
# 被其他脚本 source 使用作为库，或直接执行作为独立命令行工具
# 与 check-conflicts.ps1 功能等价

set -euo pipefail

CONFLICTS_VERSION="1.0.0"
_CONFLICTS_SYNC_ROOT=""
_CONFLICTS_COLOR_ENABLED=1

if [ -t 1 ]; then
    _CONFLICTS_COLOR_ENABLED=1
else
    _CONFLICTS_COLOR_ENABLED=0
fi

_conflicts_color() {
    local color="$1"
    local text="$2"
    if [ "$_CONFLICTS_COLOR_ENABLED" -eq 1 ]; then
        local code=""
        case "$color" in
            red)     code="31" ;;
            green)   code="32" ;;
            yellow)  code="33" ;;
            blue)    code="34" ;;
            magenta) code="35" ;;
            cyan)    code="36" ;;
            gray)    code="90" ;;
            darkred) code="31;1" ;;
            *)       code="0" ;;
        esac
        printf '\033[%sm%s\033[0m\n' "$code" "$text"
    else
        echo "$text"
    fi
}

conflicts_err() {
    _conflicts_color red "[conflicts ERROR] $*" >&2
}

conflicts_warn() {
    _conflicts_color yellow "[conflicts WARN] $*"
}

conflicts_info() {
    _conflicts_color gray "[conflicts] $*"
}

conflicts_critical() {
    _conflicts_color red "[conflicts CRITICAL] $*"
}

conflicts_is_conflict_filename() {
    local filename="$1"
    if [[ "$filename" =~ \([0-9]+\)(\.[^.]*)?$ ]]; then return 0; fi
    if [[ "$filename" == *冲突* ]]; then return 0; fi
    if [[ "$filename" == *"来自"* ]]; then return 0; fi
    if [[ "$filename" == *冲突副本* ]]; then return 0; fi
    return 1
}

conflicts_is_temporary_file() {
    local filename="$1"
    if [[ "$filename" =~ \.(tmp|temp|pack-tmp)$ ]]; then return 0; fi
    if [[ "$filename" == tmp_pack_* ]]; then return 0; fi
    return 1
}

conflicts_is_lock_file() {
    local filename="$1"
    if [[ "$filename" =~ \.lock$ ]]; then return 0; fi
    return 1
}

conflicts_is_hex_string() {
    local str="$1"
    local len="$2"
    if [ "${#str}" -ne "$len" ]; then return 1; fi
    if [[ "$str" =~ ^[0-9a-fA-F]{$len}$ ]]; then return 0; fi
    return 1
}

conflicts_classify() {
    local file_path="$1"
    local repo_root="${2:-}"

    local filename
    filename="$(basename "$file_path")"
    local rel_path="$file_path"
    if [ -n "$repo_root" ]; then
        rel_path="${file_path#$repo_root}"
        rel_path="${rel_path#/}"
        rel_path="${rel_path#\\}"
    fi
    rel_path="${rel_path//\\//}"
    local rel_lower
    rel_lower="$(echo "$rel_path" | tr '[:upper:]' '[:lower:]')"

    local is_conflict=0
    local is_tmp=0
    local is_lock=0

    if conflicts_is_conflict_filename "$filename"; then is_conflict=1; fi
    if conflicts_is_temporary_file "$filename"; then is_tmp=1; fi
    if conflicts_is_lock_file "$filename"; then is_lock=1; fi

    if [ "$is_conflict" -eq 1 ]; then
        if [[ "$rel_lower" == objects/pack/* ]]; then
            echo "critical"
            return 0
        fi
        if [[ "$rel_lower" =~ ^objects/[0-9a-f]{2}/ ]]; then
            local obj_name="$filename"
            local base_name="$filename"
            if [[ "$filename" =~ ^(.+)[[:space:]]*\([0-9]+\) ]]; then
                base_name="${BASH_REMATCH[1]}"
            fi
            if [[ "$base_name" =~ ^([0-9a-fA-F]{38}) ]]; then
                local hex_part="${BASH_REMATCH[1]}"
                if ! conflicts_is_hex_string "$hex_part" 38; then
                    echo "critical"
                    return 0
                fi
            else
                echo "critical"
                return 0
            fi
        fi
        if [[ "$filename" == HEAD* ]] && { [[ "$rel_lower" == "head" ]] || [[ "$rel_lower" == head\ * ]]; }; then
            echo "critical"
            return 0
        fi
        if [[ "$filename" == packed-refs* ]]; then
            echo "critical"
            return 0
        fi
        if [[ "$rel_lower" == refs/* ]]; then
            echo "warning"
            return 0
        fi
        if [[ "$rel_lower" == "config" ]] || [[ "$filename" == config\ * ]]; then
            echo "warning"
            return 0
        fi
        if [[ "$rel_lower" == hooks/* ]]; then
            echo "warning"
            return 0
        fi
        echo "warning"
        return 0
    fi

    if [ "$is_tmp" -eq 1 ]; then
        echo "info"
        return 0
    fi

    if [ "$is_lock" -eq 1 ]; then
        local in_locks_dir=0
        if [[ "$rel_lower" == locks/* ]]; then in_locks_dir=1; fi
        if [ "$in_locks_dir" -eq 1 ]; then
            echo "normal"
            return 0
        fi
        echo "warning"
        return 0
    fi

    if [[ "$rel_lower" == logs/* ]] && { conflicts_is_conflict_filename "$filename" || [ "$is_tmp" -eq 1 ]; }; then
        echo "info"
        return 0
    fi

    if [[ "$rel_lower" =~ ^objects/[0-9a-f]{2}/ ]]; then
        local obj_name2="$filename"
        if ! conflicts_is_hex_string "$obj_name2" 38; then
            if [[ "$obj_name2" =~ ^([0-9a-fA-F]{38}) ]]; then
                echo "warning"
                return 0
            fi
            if [ "$obj_name2" = "info" ] || [ "$obj_name2" = "pack" ]; then
                echo "normal"
                return 0
            fi
            echo "warning"
            return 0
        fi
    fi
    if [[ "$rel_lower" == objects/pack/* ]]; then
        if [[ "$filename" =~ ^pack-([0-9a-fA-F]{40})\.(pack|idx|keep|rev)$ ]]; then
            echo "normal"
            return 0
        fi
        if [ "$filename" = "pack" ] || [ "$filename" = "info" ]; then
            echo "normal"
            return 0
        fi
        echo "warning"
        return 0
    fi

    echo "normal"
    return 0
}

conflicts_format_file_size() {
    local bytes="$1"
    if [ "$bytes" -ge 1073741824 ]; then
        awk "BEGIN {printf \"%.2f GB\", $bytes/1073741824}"
    elif [ "$bytes" -ge 1048576 ]; then
        awk "BEGIN {printf \"%.2f MB\", $bytes/1048576}"
    elif [ "$bytes" -ge 1024 ]; then
        awk "BEGIN {printf \"%.2f KB\", $bytes/1024}"
    else
        echo "${bytes} B"
    fi
}

conflicts_get_suggestion() {
    local class="$1"
    case "$class" in
        critical) echo "🛑 严重！立即停止同步，从备份恢复仓库，不要手动删除" ;;
        warning)  echo "⚠️ 警告：确认无Git进程后人工检查处理" ;;
        info)     echo "ℹ️ 提示：可安全清理的临时文件或无害冲突副本" ;;
        *)        echo "" ;;
    esac
}

conflicts_scan() {
    local bare_repo_path="$1"
    if [ ! -d "$bare_repo_path" ]; then
        conflicts_err "裸仓库路径不存在: $bare_repo_path"
        return 1
    fi

    local repo_full_path
    repo_full_path="$(cd "$bare_repo_path" && pwd)"
    local total_scanned=0
    local critical_count=0
    local warning_count=0
    local info_count=0
    local critical_files=""
    local warning_files=""
    local info_files=""
    local all_files=""

    conflicts_info "开始扫描裸仓库: $repo_full_path"

    while IFS= read -r -d '' file; do
        total_scanned=$((total_scanned + 1))
        local class
        class="$(conflicts_classify "$file" "$repo_full_path")"
        if [ "$class" != "normal" ]; then
            local filename relname fsize fsize_human ftime
            filename="$(basename "$file")"
            relname="${file#$repo_full_path}"
            relname="${relname#/}"
            relname="${relname#\\}"
            fsize="$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null || echo 0)"
            fsize_human="$(conflicts_format_file_size "$fsize")"
            ftime="$(date -r "$file" "+%Y-%m-%d %H:%M:%S" 2>/dev/null || stat -c%y "$file" 2>/dev/null | cut -d. -f1 | tr 'T' ' ')"
            local suggestion
            suggestion="$(conflicts_get_suggestion "$class")"
            local entry="$class|$file|$relname|$filename|$fsize|$fsize_human|$ftime|$suggestion"

            case "$class" in
                critical)
                    critical_count=$((critical_count + 1))
                    if [ -z "$critical_files" ]; then
                        critical_files="$entry"
                    else
                        critical_files="$critical_files"$'\n'"$entry"
                    fi
                    ;;
                warning)
                    warning_count=$((warning_count + 1))
                    if [ -z "$warning_files" ]; then
                        warning_files="$entry"
                    else
                        warning_files="$warning_files"$'\n'"$entry"
                    fi
                    ;;
                info)
                    info_count=$((info_count + 1))
                    if [ -z "$info_files" ]; then
                        info_files="$entry"
                    else
                        info_files="$info_files"$'\n'"$entry"
                    fi
                    ;;
            esac
            if [ -z "$all_files" ]; then
                all_files="$entry"
            else
                all_files="$all_files"$'\n'"$entry"
            fi
        fi
    done < <(find "$repo_full_path" -type f -print0 2>/dev/null)

    local total_conflicts=$((critical_count + warning_count + info_count))
    local has_critical=0
    if [ "$critical_count" -gt 0 ]; then has_critical=1; fi

    CONFLICTS_SCAN_RESULT_REPO="$repo_full_path"
    CONFLICTS_SCAN_RESULT_TOTAL="$total_scanned"
    CONFLICTS_SCAN_RESULT_CONFLICTS="$total_conflicts"
    CONFLICTS_SCAN_RESULT_CRITICAL="$critical_count"
    CONFLICTS_SCAN_RESULT_WARNING="$warning_count"
    CONFLICTS_SCAN_RESULT_INFO="$info_count"
    CONFLICTS_SCAN_RESULT_HAS_CRITICAL="$has_critical"
    CONFLICTS_SCAN_RESULT_CRITICAL_FILES="$critical_files"
    CONFLICTS_SCAN_RESULT_WARNING_FILES="$warning_files"
    CONFLICTS_SCAN_RESULT_INFO_FILES="$info_files"
    CONFLICTS_SCAN_RESULT_ALL_FILES="$all_files"

    if [ "$has_critical" -eq 1 ]; then
        return 1
    fi
    return 0
}

_conflicts_print_entry() {
    local entry="$1"
    local prefix="$2"
    local color="$3"
    local IFS='|'
    read -r class fpath relname fname fsize fsize_hum ftime suggestion <<< "$entry"
    _conflicts_color "$color" "  [$prefix] $relname"
    _conflicts_color "dark$color" "    大小: $fsize_hum  修改时间: $ftime"
    _conflicts_color "dark$color" "    建议: $suggestion"
    echo ""
}

conflicts_generate_report() {
    local mode="${1:-single}"
    local sync_root="${2:-}"

    echo ""
    _conflicts_color cyan "========================================"
    _conflicts_color cyan "  Git 网盘同步冲突检测报告"
    _conflicts_color cyan "========================================"

    if [ "$mode" = "multi" ]; then
        echo "  同步根目录: $sync_root"
        echo "  扫描仓库数: $_CONFLICTS_MULTI_REPOS"
        echo "  扫描文件数: $_CONFLICTS_MULTI_TOTAL"
        echo "  冲突文件数: $_CONFLICTS_MULTI_CONFLICTS"
        _conflicts_color "$( [ "$_CONFLICTS_MULTI_CRITICAL" -gt 0 ] && echo red || echo green )" "    严重(CRITICAL): $_CONFLICTS_MULTI_CRITICAL"
        _conflicts_color "$( [ "$_CONFLICTS_MULTI_WARNING" -gt 0 ] && echo yellow || echo gray )" "    警告(WARNING):  $_CONFLICTS_MULTI_WARNING"
        _conflicts_color "$( [ "$_CONFLICTS_MULTI_INFO" -gt 0 ] && echo blue || echo gray )" "    提示(INFO):     $_CONFLICTS_MULTI_INFO"
    else
        echo "  仓库路径:   $CONFLICTS_SCAN_RESULT_REPO"
        echo "  扫描文件数: $CONFLICTS_SCAN_RESULT_TOTAL"
        echo "  冲突文件数: $CONFLICTS_SCAN_RESULT_CONFLICTS"
        _conflicts_color "$( [ "$CONFLICTS_SCAN_RESULT_CRITICAL" -gt 0 ] && echo red || echo green )" "    严重(CRITICAL): $CONFLICTS_SCAN_RESULT_CRITICAL"
        _conflicts_color "$( [ "$CONFLICTS_SCAN_RESULT_WARNING" -gt 0 ] && echo yellow || echo gray )" "    警告(WARNING):  $CONFLICTS_SCAN_RESULT_WARNING"
        _conflicts_color "$( [ "$CONFLICTS_SCAN_RESULT_INFO" -gt 0 ] && echo blue || echo gray )" "    提示(INFO):     $CONFLICTS_SCAN_RESULT_INFO"
    fi
    _conflicts_color cyan "========================================"
    echo ""

    if [ "$mode" = "multi" ]; then
        local idx=0
        while [ $idx -lt ${#_CONFLICTS_MULTI_REPO_PATHS[@]} ]; do
            local rpath="${_CONFLICTS_MULTI_REPO_PATHS[$idx]}"
            local rcrit="${_CONFLICTS_MULTI_REPO_CRIT[$idx]}"
            local rwarn="${_CONFLICTS_MULTI_REPO_WARN[$idx]}"
            local rinfo="${_CONFLICTS_MULTI_REPO_INFO[$idx]}"
            local rtotal=$((rcrit + rwarn + rinfo))
            if [ "$rtotal" -gt 0 ]; then
                echo ""
                _conflicts_color magenta ">>> 仓库: $(basename "$rpath")"
                if [ "$rcrit" -gt 0 ]; then
                    _conflicts_color red "--- 🔴 严重冲突 (CRITICAL) - 必须处理 ---"
                    local cf="${_CONFLICTS_MULTI_REPO_CRIT_FILES[$idx]}"
                    while IFS= read -r line; do
                        [ -n "$line" ] && _conflicts_print_entry "$line" "CRITICAL" "red"
                    done <<< "$cf"
                fi
                if [ "$rwarn" -gt 0 ]; then
                    _conflicts_color yellow "--- 🟡 警告 (WARNING) - 需要检查 ---"
                    local wf="${_CONFLICTS_MULTI_REPO_WARN_FILES[$idx]}"
                    while IFS= read -r line; do
                        [ -n "$line" ] && _conflicts_print_entry "$line" "WARNING" "yellow"
                    done <<< "$wf"
                fi
                if [ "$rinfo" -gt 0 ]; then
                    _conflicts_color blue "--- 🔵 提示 (INFO) - 可清理 ---"
                    local inf="${_CONFLICTS_MULTI_REPO_INFO_FILES[$idx]}"
                    while IFS= read -r line; do
                        [ -n "$line" ] && _conflicts_print_entry "$line" "INFO" "blue"
                    done <<< "$inf"
                fi
            fi
            idx=$((idx + 1))
        done
    else
        if [ "$CONFLICTS_SCAN_RESULT_CRITICAL" -gt 0 ]; then
            _conflicts_color red "--- 🔴 严重冲突 (CRITICAL) - 必须处理 ---"
            while IFS= read -r line; do
                [ -n "$line" ] && _conflicts_print_entry "$line" "CRITICAL" "red"
            done <<< "$CONFLICTS_SCAN_RESULT_CRITICAL_FILES"
        fi
        if [ "$CONFLICTS_SCAN_RESULT_WARNING" -gt 0 ]; then
            _conflicts_color yellow "--- 🟡 警告 (WARNING) - 需要检查 ---"
            while IFS= read -r line; do
                [ -n "$line" ] && _conflicts_print_entry "$line" "WARNING" "yellow"
            done <<< "$CONFLICTS_SCAN_RESULT_WARNING_FILES"
        fi
        if [ "$CONFLICTS_SCAN_RESULT_INFO" -gt 0 ]; then
            _conflicts_color blue "--- 🔵 提示 (INFO) - 可清理 ---"
            while IFS= read -r line; do
                [ -n "$line" ] && _conflicts_print_entry "$line" "INFO" "blue"
            done <<< "$CONFLICTS_SCAN_RESULT_INFO_FILES"
        fi
    fi

    local has_crit=0
    local total_conf=0
    if [ "$mode" = "multi" ]; then
        has_crit=$_CONFLICTS_MULTI_HAS_CRITICAL
        total_conf=$_CONFLICTS_MULTI_CONFLICTS
    else
        has_crit=$CONFLICTS_SCAN_RESULT_HAS_CRITICAL
        total_conf=$CONFLICTS_SCAN_RESULT_CONFLICTS
    fi

    if [ "$has_crit" -eq 1 ]; then
        _conflicts_color red "========================================"
        _conflicts_color red "  🛑 发现严重冲突！检测结果为失败状态。"
        _conflicts_color red "  请立即停止同步操作，从备份恢复仓库。"
        _conflicts_color red "  不要尝试自动清理 objects/pack/ 下的冲突文件！"
        _conflicts_color red "========================================"
    elif [ "$total_conf" -eq 0 ]; then
        _conflicts_color green "  ✅ 未发现冲突文件，仓库状态正常。"
    else
        _conflicts_color yellow "  ⚠️  发现非严重冲突，建议检查后处理。"
    fi
    echo ""
}

conflicts_scan_sync_root() {
    local sync_root="$1"
    if [ ! -d "$sync_root" ]; then
        conflicts_err "同步根目录不存在: $sync_root"
        return 1
    fi
    local repos_dir="$sync_root/repos"
    if [ ! -d "$repos_dir" ]; then
        conflicts_err "repos 目录不存在: $repos_dir"
        return 1
    fi

    _CONFLICTS_MULTI_REPOS=0
    _CONFLICTS_MULTI_TOTAL=0
    _CONFLICTS_MULTI_CRITICAL=0
    _CONFLICTS_MULTI_WARNING=0
    _CONFLICTS_MULTI_INFO=0
    _CONFLICTS_MULTI_CONFLICTS=0
    _CONFLICTS_MULTI_HAS_CRITICAL=0
    _CONFLICTS_MULTI_REPO_PATHS=()
    _CONFLICTS_MULTI_REPO_CRIT=()
    _CONFLICTS_MULTI_REPO_WARN=()
    _CONFLICTS_MULTI_REPO_INFO=()
    _CONFLICTS_MULTI_REPO_CRIT_FILES=()
    _CONFLICTS_MULTI_REPO_WARN_FILES=()
    _CONFLICTS_MULTI_REPO_INFO_FILES=()
    _CONFLICTS_MULTI_REPO_ALL_FILES=()

    local ret=0
    for repo_dir in "$repos_dir"/*.git; do
        [ -d "$repo_dir" ] || continue
        _CONFLICTS_MULTI_REPOS=$((_CONFLICTS_MULTI_REPOS + 1))
        conflicts_scan "$repo_dir" || ret=1
        _CONFLICTS_MULTI_TOTAL=$((_CONFLICTS_MULTI_TOTAL + CONFLICTS_SCAN_RESULT_TOTAL))
        _CONFLICTS_MULTI_CRITICAL=$((_CONFLICTS_MULTI_CRITICAL + CONFLICTS_SCAN_RESULT_CRITICAL))
        _CONFLICTS_MULTI_WARNING=$((_CONFLICTS_MULTI_WARNING + CONFLICTS_SCAN_RESULT_WARNING))
        _CONFLICTS_MULTI_INFO=$((_CONFLICTS_MULTI_INFO + CONFLICTS_SCAN_RESULT_INFO))
        _CONFLICTS_MULTI_CONFLICTS=$((_CONFLICTS_MULTI_CONFLICTS + CONFLICTS_SCAN_RESULT_CONFLICTS))
        if [ "${CONFLICTS_SCAN_RESULT_HAS_CRITICAL}" -eq 1 ]; then
            _CONFLICTS_MULTI_HAS_CRITICAL=1
        fi
        _CONFLICTS_MULTI_REPO_PATHS+=("$CONFLICTS_SCAN_RESULT_REPO")
        _CONFLICTS_MULTI_REPO_CRIT+=("$CONFLICTS_SCAN_RESULT_CRITICAL")
        _CONFLICTS_MULTI_REPO_WARN+=("$CONFLICTS_SCAN_RESULT_WARNING")
        _CONFLICTS_MULTI_REPO_INFO+=("$CONFLICTS_SCAN_RESULT_INFO")
        _CONFLICTS_MULTI_REPO_CRIT_FILES+=("$CONFLICTS_SCAN_RESULT_CRITICAL_FILES")
        _CONFLICTS_MULTI_REPO_WARN_FILES+=("$CONFLICTS_SCAN_RESULT_WARNING_FILES")
        _CONFLICTS_MULTI_REPO_INFO_FILES+=("$CONFLICTS_SCAN_RESULT_INFO_FILES")
        _CONFLICTS_MULTI_REPO_ALL_FILES+=("$CONFLICTS_SCAN_RESULT_ALL_FILES")
    done

    _CONFLICTS_MULTI_SYNC_ROOT="$sync_root"
    return $ret
}

_conflicts_ensure_log_dir() {
    local sync_root="${1:-}"
    local logs_dir=""
    if [ -n "$sync_root" ]; then
        logs_dir="$sync_root/logs"
    else
        logs_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)/logs"
    fi
    mkdir -p "$logs_dir" 2>/dev/null || logs_dir="$TMPDIR"
    mkdir -p "$logs_dir" 2>/dev/null || logs_dir="/tmp"
    echo "$logs_dir"
}

_conflicts_can_autoclean() {
    local entry="$1"
    local IFS='|'
    read -r class fpath relname fname fsize fsize_hum ftime suggestion <<< "$entry"
    if [ "$class" = "info" ]; then
        if [[ "$fname" =~ \.(tmp|temp|pack-tmp)$ ]]; then return 0; fi
        if [[ "$fname" == tmp_pack_* ]]; then return 0; fi
    fi
    if [[ "$fname" =~ \.lock$ ]]; then
        local rel_lower
        rel_lower="$(echo "$relname" | tr '[:upper:]' '[:lower:]')"
        if [[ "$rel_lower" != locks/* ]]; then return 0; fi
    fi
    return 1
}

conflicts_clean() {
    local mode="${1:-single}"
    local auto_clean="${2:-0}"
    local sync_root="${3:-}"

    local has_crit=0
    local all_files=""
    if [ "$mode" = "multi" ]; then
        has_crit=$_CONFLICTS_MULTI_HAS_CRITICAL
        local idx=0
        while [ $idx -lt ${#_CONFLICTS_MULTI_REPO_PATHS[@]} ]; do
            local af="${_CONFLICTS_MULTI_REPO_ALL_FILES[$idx]}"
            if [ -n "$af" ]; then
                if [ -z "$all_files" ]; then all_files="$af"; else all_files="$all_files"$'\n'"$af"; fi
            fi
            idx=$((idx + 1))
        done
    else
        has_crit=$CONFLICTS_SCAN_RESULT_HAS_CRITICAL
        all_files="$CONFLICTS_SCAN_RESULT_ALL_FILES"
    fi

    if [ "$has_crit" -eq 1 ]; then
        conflicts_err "存在严重冲突，禁止清理！请先从备份恢复。"
        return 1
    fi

    if [ -z "$all_files" ]; then
        conflicts_info "没有需要清理的文件。"
        return 0
    fi

    local logs_dir
    logs_dir="$(_conflicts_ensure_log_dir "$sync_root")"
    local deleted=0
    local skipped=0
    local backup_list=""

    echo ""
    if [ "$auto_clean" -eq 1 ]; then
        conflicts_info "=== AutoClean 模式：仅清理明确安全的临时文件 ==="
    else
        conflicts_info "=== Clean 模式：交互式清理 ==="
    fi

    while IFS= read -r entry; do
        [ -z "$entry" ] && continue
        local IFS='|'
        read -r class fpath relname fname fsize fsize_hum ftime suggestion <<< "$entry"
        local should_delete=0

        if [ "$auto_clean" -eq 1 ]; then
            if _conflicts_can_autoclean "$entry"; then
                should_delete=1
                conflicts_info "[AutoClean] 将删除: $relname"
            else
                conflicts_info "[AutoClean] 跳过: $relname"
                skipped=$((skipped + 1))
                continue
            fi
        else
            echo ""
            local ec="yellow"
            [ "$class" = "info" ] && ec="blue"
            _conflicts_color "$ec" "文件: $relname"
            echo "  类型: $class"
            echo "  大小: $fsize_hum  修改时间: $ftime"
            echo "  建议: $suggestion"
            printf "  确认删除此文件？(y/N) "
            local answer=""
            read -r answer
            if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
                should_delete=1
            else
                skipped=$((skipped + 1))
                continue
            fi
        fi

        if [ "$should_delete" -eq 1 ] && [ -f "$fpath" ]; then
            if [ -z "$backup_list" ]; then
                backup_list="$fpath"
            else
                backup_list="$backup_list"$'\n'"$fpath"
            fi
            if rm -f "$fpath" 2>/dev/null; then
                deleted=$((deleted + 1))
                conflicts_info "已删除: $relname"
            else
                conflicts_warn "删除失败: $relname"
            fi
        fi
    done <<< "$all_files"

    if [ -n "$backup_list" ]; then
        local ts
        ts="$(date +%Y%m%d-%H%M%S)"
        local log_file="$logs_dir/cleanup-$ts.log"
        {
            echo "# Cleanup log created at $(date '+%Y-%m-%d %H:%M:%S')"
            echo "# Files deleted:"
            echo ""
            echo "$backup_list"
        } > "$log_file"
        conflicts_info "清理日志已保存到: $log_file"
    fi

    echo ""
    echo "清理完成: 已删除 $deleted 个文件，跳过 $skipped 个文件。"

    if [ "$deleted" -gt 0 ]; then
        conflicts_info "建议执行 git fsck --full 验证仓库完整性。"
    fi
    return 0
}

conflicts_init() {
    local sync_root="$1"
    if [ ! -d "$sync_root" ]; then
        conflicts_err "同步根目录不存在: $sync_root"
        return 1
    fi
    _CONFLICTS_SYNC_ROOT="$sync_root"
    conflicts_info "冲突检测系统初始化完成 (sync_root=$sync_root)"
    return 0
}

_conflicts_show_usage() {
    cat <<EOF
check-conflicts.sh - Git 网盘同步冲突检测工具 v$CONFLICTS_VERSION

用法:
  ./check-conflicts.sh [选项]

选项（独立执行时）:
  -SyncRoot <路径>    网盘同步根目录（必须与-RepoName或-All合用）
  -RepoName <名称>    扫描指定仓库名（SyncRoot下repos/<name>.git）
  -Path <路径>        直接指定裸仓库路径扫描
  -All                扫描SyncRoot下所有仓库
  -Clean              交互式清理模式，逐个询问是否删除
  -AutoClean          自动清理明确安全的临时文件(.tmp/.pack-tmp等)
  -NoColor            禁用彩色输出
  -h, --help          显示此帮助

作为库使用（source）:
  source /path/to/check-conflicts.sh

  conflicts_init <sync_root>                  # 初始化
  conflicts_classify <file_path> [repo_root]  # 分类(normal/critical/warning/info)
  conflicts_scan <bare_repo_path>             # 扫描单个裸仓库
  conflicts_scan_sync_root <sync_root>        # 扫描同步空间所有仓库
  conflicts_generate_report [mode] [root]     # 生成报告(mode=single/multi)
  conflicts_clean [mode] [autoclean] [root]   # 清理冲突

退出码:
  0 = 无冲突或仅提示/警告
  1 = 发现严重冲突
  2 = 参数错误/执行错误

示例:
  # 扫描单个仓库
  ./check-conflicts.sh -Path /path/to/repos/myproject.git

  # 扫描所有仓库
  ./check-conflicts.sh -All -SyncRoot /path/to/sync

  # 交互式清理
  ./check-conflicts.sh -RepoName myproject -SyncRoot /path/to/sync -Clean

  # 自动清理临时文件
  ./check-conflicts.sh -All -SyncRoot /path/to/sync -AutoClean
EOF
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    PARAM_SYNC_ROOT=""
    PARAM_REPO_NAME=""
    PARAM_PATH=""
    PARAM_ALL=0
    PARAM_CLEAN=0
    PARAM_AUTO_CLEAN=0

    while [ $# -gt 0 ]; do
        case "$1" in
            -SyncRoot) shift; PARAM_SYNC_ROOT="${1:-}" ;;
            -RepoName) shift; PARAM_REPO_NAME="${1:-}" ;;
            -Path) shift; PARAM_PATH="${1:-}" ;;
            -All) PARAM_ALL=1 ;;
            -Clean) PARAM_CLEAN=1 ;;
            -AutoClean) PARAM_AUTO_CLEAN=1 ;;
            -NoColor) _CONFLICTS_COLOR_ENABLED=0 ;;
            -h|--help) _conflicts_show_usage; exit 0 ;;
            *) ;;
        esac
        shift || true
    done

    HAS_TARGET=0
    SCAN_MODE="single"
    SCAN_RETVAL=0

    if [ -n "$PARAM_PATH" ]; then
        HAS_TARGET=1
        conflicts_scan "$PARAM_PATH" || SCAN_RETVAL=1
    elif [ "$PARAM_ALL" -eq 1 ] && [ -n "$PARAM_SYNC_ROOT" ]; then
        HAS_TARGET=1
        SCAN_MODE="multi"
        conflicts_scan_sync_root "$PARAM_SYNC_ROOT" || SCAN_RETVAL=1
    elif [ -n "$PARAM_REPO_NAME" ] && [ -n "$PARAM_SYNC_ROOT" ]; then
        HAS_TARGET=1
        REPO_PATH="$PARAM_SYNC_ROOT/repos/$PARAM_REPO_NAME.git"
        conflicts_scan "$REPO_PATH" || SCAN_RETVAL=1
    fi

    if [ "$HAS_TARGET" -eq 0 ]; then
        _conflicts_show_usage
        exit 2
    fi

    conflicts_generate_report "$SCAN_MODE" "$PARAM_SYNC_ROOT"

    if [ "$PARAM_CLEAN" -eq 1 ] || [ "$PARAM_AUTO_CLEAN" -eq 1 ]; then
        AC=0
        [ "$PARAM_AUTO_CLEAN" -eq 1 ] && AC=1
        conflicts_clean "$SCAN_MODE" "$AC" "$PARAM_SYNC_ROOT" || true
    fi

    if [ "$SCAN_RETVAL" -ne 0 ]; then
        exit 1
    fi
    exit 0
fi
