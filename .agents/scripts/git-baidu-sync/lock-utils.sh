#!/usr/bin/env bash
# lock-utils.sh - Git 网盘同步锁机制 Bash 函数库
# 被其他脚本 source 使用，不直接执行（直接执行显示用法）

LOCK_UTILS_VERSION="1.0.0"
LOCK_DEFAULT_TIMEOUT_MINUTES=30

_LOCK_UTILS_DEVICE_ID=""
_LOCK_UTILS_SYNC_ROOT=""
_LOCK_UTILS_DEVICE_CACHE_LOADED=0

_lock_err() {
    echo "[lock-utils ERROR] $*" >&2
}

_lock_warn() {
    echo "[lock-utils WARN] $*" >&2
}

_lock_info() {
    echo "[lock-utils] $*"
}

_lock_detect_os() {
    local uname_out
    uname_out="$(uname -s 2>/dev/null || echo unknown)"
    case "$uname_out" in
        Linux*)                     echo "linux" ;;
        Darwin*)                    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) echo "win" ;;
        *)                          echo "unknown" ;;
    esac
}

_lock_get_hostname() {
    local hn
    hn="$(hostname 2>/dev/null || cat /etc/hostname 2>/dev/null || echo unknown-host)"
    hn="${hn//[^a-zA-Z0-9_-]/}"
    [ -z "$hn" ] && hn="unknown-host"
    echo "$hn"
}

_lock_get_pid() {
    echo $$
}

_lock_get_iso8601() {
    if date -u +%Y-%m-%dT%H:%M:%S%z 2>/dev/null | grep -qE '[+-][0-9]{4}$'; then
        date +%Y-%m-%dT%H:%M:%S%z | sed 's/\([+-][0-9][0-9]\)\([0-9][0-9]\)$/\1:\2/'
    elif date -Iseconds 2>/dev/null | grep -qE '[+-][0-9]{2}:[0-9]{2}$'; then
        date -Iseconds
    else
        local epoch
        epoch="$(date +%s)"
        date -u -d "@$epoch" +%Y-%m-%dT%H:%M:%SZ
    fi
}

_lock_iso8601_to_epoch() {
    local iso="$1"
    if [ -z "$iso" ]; then
        echo 0
        return 1
    fi

    local iso_clean="${iso%Z}"
    iso_clean="${iso_clean// /T}"

    if [[ "$iso_clean" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}([+-][0-9]{2}:?[0-9]{2})?$ ]]; then
        if date -u -d "$iso" +%s 2>/dev/null; then
            return 0
        fi
        local tz_part="${iso_clean##*[+-]}"
        local base_part="${iso_clean%[+-]*}"
        local tz_offset=0

        if [ "$base_part" != "$iso_clean" ]; then
            local sign="+"
            [[ "$iso_clean" == *-* ]] && [[ "${iso_clean:10:1}" == "T" ]] && sign="-"
            local tz_hour="${tz_part:0:2}"
            local tz_min="${tz_part:3:2}"
            tz_offset=$(( (10#$tz_hour * 60 + 10#$tz_min) * 60 ))
            [ "$sign" = "-" ] && tz_offset=$((-tz_offset))
        fi

        if [ "${iso_clean: -1}" = "Z" ] || [[ "$iso_clean" =~ [+-]00:?00$ ]]; then
            date -u -d "${base_part}Z" +%s 2>/dev/null && return 0
        fi

        local epoch_utc
        if epoch_utc="$(date -u -d "${base_part}UTC" +%s 2>/dev/null)"; then
            echo $((epoch_utc - tz_offset))
            return 0
        fi
    fi

    local try_epoch
    if try_epoch="$(date -d "$iso" +%s 2>/dev/null)"; then
        echo "$try_epoch"
        return 0
    fi
    if try_epoch="$(date -u -d "$iso" +%s 2>/dev/null)"; then
        echo "$try_epoch"
        return 0
    fi

    echo 0
    return 1
}

_lock_get_now_epoch() {
    date +%s
}

_lock_pid_exists() {
    local pid="$1"
    [ -z "$pid" ] && return 1
    if kill -0 "$pid" 2>/dev/null; then
        return 0
    fi
    [ -d "/proc/$pid" ] && return 0
    return 1
}

_lock_get_device_cache_path() {
    if [ -n "$_LOCK_UTILS_SYNC_ROOT" ] && [ -d "$_LOCK_UTILS_SYNC_ROOT/meta" ]; then
        echo "$_LOCK_UTILS_SYNC_ROOT/meta/devices.json"
    else
        echo "$HOME/.git-baidu-sync-device-id"
    fi
}

_lock_extract_device_id_from_cache() {
    local cache_file="$1"
    local my_hostname="$2"
    local my_os="$3"

    if [ ! -f "$cache_file" ]; then
        return 1
    fi

    if [[ "$cache_file" == *devices.json ]]; then
        command -v jq >/dev/null 2>&1 || return 1
        local existing_id
        existing_id="$(jq -r --arg hn "$my_hostname" --arg os "$my_os" '.devices[]? | select(.hostname == $hn and .os == $os) | .id' "$cache_file" 2>/dev/null | head -1)"
        if [ -n "$existing_id" ] && [ "$existing_id" != "null" ]; then
            echo "$existing_id"
            return 0
        fi
        return 1
    fi

    local content
    content="$(cat "$cache_file" 2>/dev/null)"
    if [[ "$content" =~ ^[a-z0-9-]+-(win|macos|linux|unknown)-[0-9]+$ ]]; then
        echo "$content"
        return 0
    fi
    return 1
}

_lock_save_device_id() {
    local device_id="$1"
    local cache_file="$2"

    if [[ "$cache_file" == *devices.json ]]; then
        if [ ! -f "$cache_file" ]; then
            mkdir -p "$(dirname "$cache_file")"
            printf '{\n  "devices": []\n}\n' > "$cache_file"
        fi
        if command -v jq >/dev/null 2>&1; then
            local my_hostname my_os ts
            my_hostname="$(_lock_get_hostname)"
            my_os="$(_lock_detect_os)"
            ts="$(_lock_get_iso8601)"
            local tmp
            tmp="$(mktemp)"
            jq --arg id "$device_id" \
               --arg hn "$my_hostname" \
               --arg os "$my_os" \
               --arg ts "$ts" \
               '.devices += [{"id": $id, "hostname": $hn, "os": $os, "registered_at": $ts, "last_seen": $ts}]' \
               "$cache_file" > "$tmp" && mv "$tmp" "$cache_file"
            return 0
        fi
    fi

    mkdir -p "$(dirname "$cache_file")"
    printf '%s\n' "$device_id" > "$cache_file"
    chmod 600 "$cache_file" 2>/dev/null || true
}

_lock_generate_device_id() {
    local hostname="$1"
    local os_type="$2"
    local seq=1
    local candidate
    local cache_file="$(_lock_get_device_cache_path)"

    if [ -f "$cache_file" ] && [[ "$cache_file" != *devices.json ]]; then
        local existing
        existing="$(cat "$cache_file" 2>/dev/null)"
        if [[ "$existing" =~ ^${hostname//\./\\.}-${os_type}-([0-9]+)$ ]]; then
            seq=$((10#${BASH_REMATCH[1]}))
        fi
    fi

    candidate="${hostname}-${os_type}-$(printf '%02d' $seq)"
    echo "$candidate"
}

_lock_ensure_device_id() {
    if [ "$_LOCK_UTILS_DEVICE_CACHE_LOADED" = "1" ] && [ -n "$_LOCK_UTILS_DEVICE_ID" ]; then
        return 0
    fi

    local my_hostname my_os
    my_hostname="$(_lock_get_hostname)"
    my_os="$(_lock_detect_os)"
    local cache_file="$(_lock_get_device_cache_path)"

    local cached_id
    if cached_id="$(_lock_extract_device_id_from_cache "$cache_file" "$my_hostname" "$my_os")"; then
        _LOCK_UTILS_DEVICE_ID="$cached_id"
        _LOCK_UTILS_DEVICE_CACHE_LOADED=1
        return 0
    fi

    _LOCK_UTILS_DEVICE_ID="$(_lock_generate_device_id "$my_hostname" "$my_os")"
    _lock_save_device_id "$_LOCK_UTILS_DEVICE_ID" "$cache_file" 2>/dev/null || true
    _LOCK_UTILS_DEVICE_CACHE_LOADED=1
}

_lock_get_timeout_minutes() {
    if [ -n "${GIT_SYNC_LOCK_TIMEOUT:-}" ] && [[ "$GIT_SYNC_LOCK_TIMEOUT" =~ ^[0-9]+$ ]]; then
        echo "$GIT_SYNC_LOCK_TIMEOUT"
    else
        echo "$LOCK_DEFAULT_TIMEOUT_MINUTES"
    fi
}

_lock_get_lockfile_path() {
    local repo_name="$1"
    if [ -z "$_LOCK_UTILS_SYNC_ROOT" ]; then
        _lock_err "SYNC_ROOT 未初始化，请先调用 lock_init"
        return 1
    fi
    echo "${_LOCK_UTILS_SYNC_ROOT}/locks/${repo_name}.lock.json"
}

_lock_read_json_field() {
    local file="$1"
    local field="$2"
    if command -v jq >/dev/null 2>&1; then
        jq -r ".$field // empty" "$file" 2>/dev/null
    else
        grep -oP "\"${field}\"\s*:\s*\"?\K[^,}\"]+" "$file" 2>/dev/null | head -1
    fi
}

_lock_is_timeout_lock() {
    local lockfile="$1"
    local acquired_at
    acquired_at="$(_lock_read_json_field "$lockfile" "acquired_at")"
    if [ -z "$acquired_at" ]; then
        return 0
    fi
    local lock_epoch now_epoch diff_mins timeout_mins
    lock_epoch="$(_lock_iso8601_to_epoch "$acquired_at")"
    now_epoch="$(_lock_get_now_epoch)"
    timeout_mins="$(_lock_get_timeout_minutes)"
    diff_mins=$(( (now_epoch - lock_epoch) / 60 ))
    if [ "$diff_mins" -ge "$timeout_mins" ]; then
        return 0
    fi
    return 1
}

_lock_build_lock_json() {
    local operation="$1"
    local device_id="$2"
    local pid="$3"
    local hostname="$4"
    local ts
    ts="$(_lock_get_iso8601)"

    if command -v jq >/dev/null 2>&1; then
        jq -n \
            --arg did "$device_id" \
            --argjson pid "$pid" \
            --arg ts "$ts" \
            --arg op "$operation" \
            --arg hn "$hostname" \
            --arg ver "$LOCK_UTILS_VERSION" \
            '{device_id: $did, pid: $pid, acquired_at: $ts, operation: $op, hostname: $hn, script_version: $ver}'
    else
        cat <<EOF
{
  "device_id": "${device_id}",
  "pid": ${pid},
  "acquired_at": "${ts}",
  "operation": "${operation}",
  "hostname": "${hostname}",
  "script_version": "${LOCK_UTILS_VERSION}"
}
EOF
    fi
}

lock_init() {
    if [ $# -lt 1 ]; then
        _lock_err "用法: lock_init <sync_root>"
        return 2
    fi
    local sync_root="$1"
    if [ ! -d "$sync_root" ]; then
        _lock_err "同步根目录不存在: $sync_root"
        return 2
    fi
    _LOCK_UTILS_SYNC_ROOT="$sync_root"
    _LOCK_UTILS_DEVICE_CACHE_LOADED=0
    _LOCK_UTILS_DEVICE_ID=""
    _lock_ensure_device_id
    local locks_dir="${sync_root}/locks"
    if [ ! -d "$locks_dir" ]; then
        mkdir -p "$locks_dir" 2>/dev/null || {
            _lock_err "无法创建 locks 目录: $locks_dir"
            return 2
        }
    fi
    _lock_info "锁系统初始化完成 (device_id=$_LOCK_UTILS_DEVICE_ID, sync_root=$_LOCK_UTILS_SYNC_ROOT)"
    return 0
}

lock_acquire() {
    if [ $# -lt 2 ]; then
        _lock_err "用法: lock_acquire <repo_name> <operation>"
        return 2
    fi
    local repo_name="$1"
    local operation="$2"
    _lock_ensure_device_id

    local lockfile
    lockfile="$(_lock_get_lockfile_path "$repo_name")" || return 2

    local my_device_id="$(_lock_get_hostname)-$(_lock_detect_os)"
    _lock_ensure_device_id
    my_device_id="$_LOCK_UTILS_DEVICE_ID"
    local my_pid="$(_lock_get_pid)"
    local my_hostname="$(_lock_get_hostname)"

    for retry in 1 2 3; do
        if [ -f "$lockfile" ]; then
            local holder_device holder_pid holder_op holder_ts holder_host
            holder_device="$(_lock_read_json_field "$lockfile" "device_id")"
            holder_pid="$(_lock_read_json_field "$lockfile" "pid")"
            holder_op="$(_lock_read_json_field "$lockfile" "operation")"
            holder_ts="$(_lock_read_json_field "$lockfile" "acquired_at")"
            holder_host="$(_lock_read_json_field "$lockfile" "hostname")"

            if [ "$holder_device" = "$my_device_id" ]; then
                if [ -n "$holder_pid" ] && _lock_pid_exists "$holder_pid"; then
                    if [ "$holder_pid" = "$my_pid" ]; then
                        _lock_info "锁已被当前进程持有，重入成功"
                        return 0
                    fi
                    _lock_err "仓库 $repo_name 已被本设备其他进程持有 (pid=$holder_pid, op=$holder_op, since=$holder_ts)"
                    return 1
                fi
                _lock_warn "发现本设备残留锁 (pid=$holder_pid 已不存在)，自动清理"
                rm -f "$lockfile"
            elif _lock_is_timeout_lock "$lockfile"; then
                _lock_warn "========================================"
                _lock_warn "发现超时锁，自动清理："
                _lock_warn "  仓库: $repo_name"
                _lock_warn "  持有者 device_id: $holder_device"
                _lock_warn "  持有者 hostname: $holder_host"
                _lock_warn "  持有者 pid: $holder_pid"
                _lock_warn "  操作: $holder_op"
                _lock_warn "  获取时间: $holder_ts"
                _lock_warn "========================================"
                rm -f "$lockfile"
            else
                _lock_err "仓库 $repo_name 已被其他设备持有锁"
                _lock_err "  device_id: $holder_device"
                _lock_err "  hostname: $holder_host"
                _lock_err "  pid: $holder_pid"
                _lock_err "  operation: $holder_op"
                _lock_err "  acquired_at: $holder_ts"
                _lock_err "请等待持有者完成或确认超时后使用 force-unlock"
                return 1
            fi
        fi

        local lock_json
        lock_json="$(_lock_build_lock_json "$operation" "$my_device_id" "$my_pid" "$my_hostname")"

        (
            set -o noclobber
            printf '%s\n' "$lock_json" > "$lockfile"
        ) 2>/dev/null
        local create_ret=$?

        if [ $create_ret -eq 0 ] && [ -f "$lockfile" ]; then
            _lock_info "已获取锁: $repo_name (op=$operation, pid=$my_pid)"
            return 0
        fi

        if [ $retry -lt 3 ]; then
            _lock_info "获取锁时遇到竞态，重试 ($retry/3)..."
            sleep 0.2
        fi
    done

    _lock_err "获取锁失败（多次重试后仍失败，可能存在并发竞争）"
    return 1
}

lock_release() {
    if [ $# -lt 1 ]; then
        _lock_err "用法: lock_release <repo_name>"
        return 2
    fi
    local repo_name="$1"
    _lock_ensure_device_id

    local lockfile
    lockfile="$(_lock_get_lockfile_path "$repo_name")" || return 2

    if [ ! -f "$lockfile" ]; then
        _lock_warn "释放锁时文件不存在: $lockfile（可能已被超时清理）"
        return 0
    fi

    local holder_device holder_pid
    holder_device="$(_lock_read_json_field "$lockfile" "device_id")"
    holder_pid="$(_lock_read_json_field "$lockfile" "pid")"
    local my_device_id="$_LOCK_UTILS_DEVICE_ID"

    if [ "$holder_device" != "$my_device_id" ]; then
        _lock_err "拒绝释放他人的锁！"
        _lock_err "  持有者: $holder_device"
        _lock_err "  本设备: $my_device_id"
        _lock_err "如需强制释放，请使用 lock_force_release 或 force-unlock 工具"
        return 1
    fi

    local my_pid="$(_lock_get_pid)"
    if [ -n "$holder_pid" ] && [ "$holder_pid" != "$my_pid" ] && _lock_pid_exists "$holder_pid"; then
        _lock_warn "释放同设备不同进程的锁 (holder_pid=$holder_pid, my_pid=$my_pid)"
    fi

    rm -f "$lockfile"
    if [ -f "$lockfile" ]; then
        _lock_err "删除锁文件失败: $lockfile"
        return 1
    fi
    _lock_info "已释放锁: $repo_name"
    return 0
}

lock_check() {
    if [ $# -lt 1 ]; then
        _lock_err "用法: lock_check <repo_name>"
        return 2
    fi
    local repo_name="$1"

    local lockfile
    lockfile="$(_lock_get_lockfile_path "$repo_name")" || return 2

    if [ ! -f "$lockfile" ]; then
        echo "无锁（可用）"
        return 0
    fi

    local holder_device holder_pid holder_op holder_ts holder_host holder_ver
    holder_device="$(_lock_read_json_field "$lockfile" "device_id")"
    holder_pid="$(_lock_read_json_field "$lockfile" "pid")"
    holder_op="$(_lock_read_json_field "$lockfile" "operation")"
    holder_ts="$(_lock_read_json_field "$lockfile" "acquired_at")"
    holder_host="$(_lock_read_json_field "$lockfile" "hostname")"
    holder_ver="$(_lock_read_json_field "$lockfile" "script_version")"

    echo "=== 锁状态: $repo_name ==="
    echo "  device_id:     $holder_device"
    echo "  hostname:      $holder_host"
    echo "  pid:           $holder_pid"
    echo "  operation:     $holder_op"
    echo "  acquired_at:   $holder_ts"
    echo "  script_version: $holder_ver"

    _lock_ensure_device_id 2>/dev/null || true
    local my_device_id="${_LOCK_UTILS_DEVICE_ID:-}"
    local now_epoch lock_epoch diff_mins
    now_epoch="$(_lock_get_now_epoch)"
    lock_epoch="$(_lock_iso8601_to_epoch "$holder_ts")"
    if [ "$lock_epoch" -gt 0 ]; then
        diff_mins=$(( (now_epoch - lock_epoch) / 60 ))
        echo "  已持有:       ${diff_mins} 分钟"
    fi

    local timeout_mins="$(_lock_get_timeout_minutes)"
    echo "  超时阈值:     ${timeout_mins} 分钟"

    if _lock_is_timeout_lock "$lockfile"; then
        echo "状态: 超时（可安全清理或重新获取）"
        return 3
    fi

    if [ -n "$my_device_id" ] && [ "$holder_device" = "$my_device_id" ]; then
        if [ -n "$holder_pid" ] && _lock_pid_exists "$holder_pid"; then
            echo "状态: 被本设备持有"
            return 1
        else
            echo "状态: 本设备残留锁（进程已退出，视同超时）"
            return 3
        fi
    fi

    echo "状态: 被其他设备持有"
    return 2
}

lock_get_holder_info() {
    if [ $# -lt 1 ]; then
        _lock_err "用法: lock_get_holder_info <repo_name>"
        return 2
    fi
    local repo_name="$1"
    local lockfile
    lockfile="$(_lock_get_lockfile_path "$repo_name")" || return 2

    if [ ! -f "$lockfile" ]; then
        echo "{}"
        return 0
    fi
    cat "$lockfile"
    return 0
}

lock_force_release() {
    if [ $# -lt 1 ]; then
        _lock_err "用法: lock_force_release <repo_name> [assume_yes]"
        return 2
    fi
    local repo_name="$1"
    local assume_yes="${2:-}"

    local lockfile
    lockfile="$(_lock_get_lockfile_path "$repo_name")" || return 2

    if [ ! -f "$lockfile" ]; then
        _lock_info "锁不存在，无需强制释放: $repo_name"
        return 0
    fi

    local holder_device holder_pid holder_op holder_ts holder_host
    holder_device="$(_lock_read_json_field "$lockfile" "device_id")"
    holder_pid="$(_lock_read_json_field "$lockfile" "pid")"
    holder_op="$(_lock_read_json_field "$lockfile" "operation")"
    holder_ts="$(_lock_read_json_field "$lockfile" "acquired_at")"
    holder_host="$(_lock_read_json_field "$lockfile" "hostname")"

    _lock_ensure_device_id 2>/dev/null || true
    local my_device_id="${_LOCK_UTILS_DEVICE_ID:-}"
    local now_epoch lock_epoch diff_mins=0
    now_epoch="$(_lock_get_now_epoch)"
    lock_epoch="$(_lock_iso8601_to_epoch "$holder_ts")"
    [ "$lock_epoch" -gt 0 ] && diff_mins=$(( (now_epoch - lock_epoch) / 60 ))

    echo "" >&2
    echo "========================================" >&2
    echo "  ⚠️  强制解锁警告（DANGER）" >&2
    echo "========================================" >&2
    echo "  仓库:          $repo_name" >&2
    echo "  持有者device:  $holder_device" >&2
    echo "  持有者host:    $holder_host" >&2
    echo "  持有者pid:     $holder_pid" >&2
    echo "  操作类型:      $holder_op" >&2
    echo "  获取时间:      $holder_ts" >&2
    echo "  已持有时长:    ${diff_mins} 分钟" >&2
    echo "" >&2

    if [ -n "$my_device_id" ] && [ "$holder_device" = "$my_device_id" ]; then
        echo "  提示: 这是本设备持有的锁" >&2
    else
        echo "  ⚠️  警告: 这是 OTHER DEVICE 持有的锁！" >&2
        echo "     强制释放可能导致并发 push 和仓库损坏！" >&2
        echo "     请确认持有者设备确实已离线/崩溃且不再操作！" >&2
    fi
    echo "" >&2

    if [ "$assume_yes" != "--yes" ] && [ "$assume_yes" != "-y" ] && [ "$assume_yes" != "force" ]; then
        echo -n "确认强制释放？(输入 YES 继续，其他输入取消): " >&2
        read -r confirm
        if [ "$confirm" != "YES" ]; then
            _lock_info "用户取消操作"
            return 1
        fi
    fi

    _lock_warn "执行强制释放锁: $lockfile"
    rm -f "$lockfile"
    if [ -f "$lockfile" ]; then
        _lock_err "强制释放失败（无法删除锁文件）"
        return 1
    fi
    _lock_warn "锁已强制释放。请等待网盘同步完成后再操作。"
    echo "" >&2
    _lock_info "强制释放完成: $repo_name"
    return 0
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    cat <<'USAGE'
lock-utils.sh - Git 网盘同步锁机制 Bash 函数库

本文件是函数库，应被其他脚本 source 使用，不直接执行。

用法（在其他脚本中）:
  source /path/to/lock-utils.sh

  lock_init <sync_root>              # 初始化锁系统（必须先调用）
  lock_acquire <repo_name> <op>      # 原子获取锁（返回0成功/1失败/2参数错误）
  lock_release <repo_name>           # 释放锁
  lock_check <repo_name>             # 检查锁状态（返回0无锁/1自己持有/2他人持有/3超时）
  lock_get_holder_info <repo_name>   # 输出锁持有者JSON
  lock_force_release <repo> [-y]     # 强制释放锁（需交互确认）

环境变量:
  GIT_SYNC_LOCK_TIMEOUT    锁超时分钟数（默认30）
USAGE
    exit 0
fi
