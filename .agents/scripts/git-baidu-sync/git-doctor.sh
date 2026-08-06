#!/usr/bin/env bash
# git-doctor.sh - Git 网盘同步健康检查 Bash 工具/库
# 被其他脚本 source 使用作为库，或直接执行作为独立命令行工具
# 与 git-doctor.ps1 功能等价

set -euo pipefail

DOCTOR_VERSION="1.0.0"
_DOCTOR_COLOR_ENABLED=1

if [ -t 1 ]; then
    _DOCTOR_COLOR_ENABLED=1
else
    _DOCTOR_COLOR_ENABLED=0
fi

_DOCTOR_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
_DOCTOR_LOCK_UTILS_LOADED=0
_DOCTOR_CONFLICTS_LOADED=0

# shellcheck source=lock-utils.sh
source "$_DOCTOR_SCRIPT_DIR/lock-utils.sh"
# shellcheck source=check-conflicts.sh
source "$_DOCTOR_SCRIPT_DIR/check-conflicts.sh"
_DOCTOR_LOCK_UTILS_LOADED=1
_DOCTOR_CONFLICTS_LOADED=1

DOCTOR_MIN_GIT_VERSION="2.30.0"
DOCTOR_LOOSE_OBJ_WARN=6700
DOCTOR_LOOSE_OBJ_ERR=10000
DOCTOR_MAX_PACK_FILES=1
DOCTOR_BACKUP_WARN_DAYS=7
DOCTOR_BACKUP_ERR_DAYS=30
DOCTOR_DISK_WARN_GB=5
DOCTOR_DISK_ERR_GB=1

_DOCTOR_RESULTS=()
_DOCTOR_NAMES=()
_DOCTOR_DETAILS=()
_DOCTOR_OK_COUNT=0
_DOCTOR_WARN_COUNT=0
_DOCTOR_ERR_COUNT=0
_DOCTOR_INFO_COUNT=0

_doctor_color() {
    local color="$1"
    local text="$2"
    if [ "$_DOCTOR_COLOR_ENABLED" -eq 1 ]; then
        local code=""
        case "$color" in
            red)     code="31" ;;
            green)   code="32" ;;
            yellow)  code="33" ;;
            blue)    code="34" ;;
            magenta) code="35" ;;
            cyan)    code="36" ;;
            gray)    code="90" ;;
            white)   code="0" ;;
            *)       code="0" ;;
        esac
        printf '\033[%sm%s\033[0m' "$code" "$text"
    else
        printf '%s' "$text"
    fi
}

_doctor_write_check() {
    local status="$1"
    local name="$2"
    local detail="${3:-}"

    local prefix color
    case "$status" in
        OK)
            prefix="[OK]  "; color="green" ;;
        WARN)
            prefix="[WARN]"; color="yellow" ;;
        ERR)
            prefix="[ERR] "; color="red" ;;
        INFO)
            prefix="[INFO]"; color="cyan" ;;
        *)
            prefix="[????]"; color="white" ;;
    esac

    _doctor_color "$color" "$prefix"
    if [ -n "$detail" ]; then
        printf ' %s - %s\n' "$name" "$detail"
    else
        printf ' %s\n' "$name"
    fi
}

_doctor_add_result() {
    local status="$1"
    local name="$2"
    local detail="${3:-}"
    _DOCTOR_RESULTS+=("$status")
    _DOCTOR_NAMES+=("$name")
    _DOCTOR_DETAILS+=("$detail")
    case "$status" in
        OK)   _DOCTOR_OK_COUNT=$((_DOCTOR_OK_COUNT + 1)) ;;
        WARN) _DOCTOR_WARN_COUNT=$((_DOCTOR_WARN_COUNT + 1)) ;;
        ERR)  _DOCTOR_ERR_COUNT=$((_DOCTOR_ERR_COUNT + 1)) ;;
        INFO) _DOCTOR_INFO_COUNT=$((_DOCTOR_INFO_COUNT + 1)) ;;
    esac
}

_doctor_git() {
    git "$@" 2>&1
    return $?
}

_doctor_resolve_fullpath() {
    local p="$1"
    if [[ "$p" = /* ]]; then
        echo "$p"
    else
        echo "$(cd "$p" 2>/dev/null && pwd || echo "$(pwd)/$p")"
    fi
}

_doctor_version_compare() {
    local v1="$1"
    local v2="$2"
    if [ "$(printf '%s\n' "$v1" "$v2" | sort -V | head -n1)" = "$v2" ]; then
        return 0
    else
        return 1
    fi
}

_doctor_detect_os() {
    local uname_out
    uname_out="$(uname -s 2>/dev/null || echo unknown)"
    case "$uname_out" in
        Linux*)                     echo "linux" ;;
        Darwin*)                    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*|MINGW32*|MINGW64*) echo "win" ;;
        *)                          echo "unknown" ;;
    esac
}

_doctor_get_repo_name() {
    local repo_path="$1"
    local remote_url="${2:-}"
    if [ -n "$remote_url" ]; then
        local bn
        bn="$(basename "$remote_url" .git)"
        if [ -n "$bn" ] && [ "$bn" != "/" ]; then
            echo "$bn"
            return 0
        fi
    fi
    basename "$repo_path"
}

_doctor_infer_sync_root() {
    local repo_path="$1"
    local remote_name="$2"
    local __remote_url_var="$3"

    local remote_url=""
    remote_url="$(git -C "$repo_path" remote get-url "$remote_name" 2>/dev/null || true)"
    remote_url="$(echo "$remote_url" | head -1)"

    if [ -n "$__remote_url_var" ]; then
        eval "$__remote_url_var=\"\$remote_url\""
    fi

    if [ -n "$remote_url" ] && [ -d "$remote_url" ]; then
        local bare_dir
        bare_dir="$(_doctor_resolve_fullpath "$remote_url")"
        local bare_basename
        bare_basename="$(basename "$bare_dir")"
        if [[ "$bare_basename" == *.git ]]; then
            local repos_dir sync_root
            repos_dir="$(dirname "$bare_dir")"
            sync_root="$(dirname "$repos_dir")"
            echo "$sync_root"
            return 0
        fi
    fi
    return 1
}

_doctor_check_git_version() {
    local version_output
    if ! version_output="$(_doctor_git --version)"; then
        _doctor_add_result "ERR" "Git版本" "无法执行git命令，请确认Git已安装"
        return
    fi
    local version_line
    version_line="$(echo "$version_output" | head -1)"
    if [[ "$version_line" =~ git\ version\ ([0-9]+\.[0-9]+\.[0-9]+) ]]; then
        local ver="${BASH_REMATCH[1]}"
        if _doctor_version_compare "$ver" "$DOCTOR_MIN_GIT_VERSION"; then
            _doctor_add_result "OK" "Git版本" "$ver (≥ $DOCTOR_MIN_GIT_VERSION)"
        else
            _doctor_add_result "ERR" "Git版本" "$ver < $DOCTOR_MIN_GIT_VERSION，请升级Git"
        fi
    else
        _doctor_add_result "WARN" "Git版本" "无法解析版本: $version_line"
    fi
}

_doctor_check_repo_valid() {
    local repo_path="$1"
    if git -C "$repo_path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        _doctor_add_result "OK" "仓库有效性" "有效的Git工作仓库"
    else
        _doctor_add_result "ERR" "仓库有效性" "不是有效的Git工作仓库"
    fi
}

_doctor_check_worktree() {
    local repo_path="$1"
    local status_output
    if ! status_output="$(_doctor_git -C "$repo_path" status --porcelain)"; then
        _doctor_add_result "ERR" "工作区状态" "git status执行失败"
        return
    fi
    local dirty_count
    dirty_count="$(echo "$status_output" | grep -c '\S' 2>/dev/null || echo 0)"
    dirty_count="${dirty_count:-0}"
    if [ "$dirty_count" -eq 0 ]; then
        _doctor_add_result "OK" "工作区状态" "工作区干净"
    else
        _doctor_add_result "WARN" "工作区状态" "有$dirty_count个未提交的更改"
    fi
}

_doctor_check_temp_files() {
    local bare_repo="$1"
    if [ ! -d "$bare_repo" ]; then
        _doctor_add_result "ERR" "半同步检测" "裸仓库路径不存在: $bare_repo"
        return
    fi
    local tmp_list=""
    local f
    while IFS= read -r -d '' f; do
        tmp_list="${tmp_list}${f}"$'\n'
    done < <(find "$bare_repo" \( -name '*.tmp' -o -name '*.pack-tmp' -o -name '*.part' -o -name '*.temp' -o -name '*.downloading' -o -name 'tmp_pack_*' \) -type f -print0 2>/dev/null)

    while IFS= read -r -d '' f; do
        local bname
        bname="$(basename "$f")"
        local age_mins
        age_mins=$(( ($(date +%s) - $(stat -c%Y "$f" 2>/dev/null || stat -f%m "$f" 2>/dev/null || echo 0)) / 60 ))
        if [ "$age_mins" -gt 10 ]; then
            tmp_list="${tmp_list}${f}"$'\n'
        fi
    done < <(find "$bare_repo" -name '*.keep' -type f -print0 2>/dev/null)

    while IFS= read -r -d '' f; do
        local bname
        bname="$(basename "$f")"
        if [ "$bname" != "HEAD.lock" ] && ! [[ "$bname" =~ ^pack-.+\.lock$ ]]; then
            tmp_list="${tmp_list}${f}"$'\n'
        fi
    done < <(find "$bare_repo" -name '*.lock' -type f -print0 2>/dev/null)

    local tmp_count
    tmp_count="$(echo "$tmp_list" | grep -c '\S' 2>/dev/null || echo 0)"
    tmp_count="${tmp_count:-0}"
    if [ "$tmp_count" -eq 0 ]; then
        _doctor_add_result "OK" "半同步检测" "未发现临时文件"
        return
    fi
    local names=""
    local n=0
    while IFS= read -r f; do
        [ -z "$f" ] && continue
        names="$names$(basename "$f"), "
        n=$((n + 1))
        [ "$n" -ge 3 ] && break
    done <<< "$tmp_list"
    names="${names%, }"
    local more=""
    if [ "$tmp_count" -gt 3 ]; then
        more=" 等${tmp_count}个"
    fi
    _doctor_add_result "ERR" "半同步检测" "发现临时文件: ${names}${more}"
}

_doctor_check_conflicts() {
    local bare_repo="$1"
    if [ ! -d "$bare_repo" ]; then
        _doctor_add_result "ERR" "冲突副本" "裸仓库路径不存在"
        return
    fi

    local critical=0 warning=0 info=0
    local scanned=0
    while IFS= read -r -d '' f; do
        scanned=$((scanned + 1))
        local rel="${f#$bare_repo}"
        rel="${rel#/}"
        local class
        class="$(conflicts_classify "$f" "$bare_repo" 2>/dev/null || echo normal)"
        case "$class" in
            critical) critical=$((critical + 1)) ;;
            warning)  warning=$((warning + 1)) ;;
            info)     info=$((info + 1)) ;;
        esac
    done < <(find "$bare_repo" -type f -print0 2>/dev/null)

    if [ "$critical" -gt 0 ]; then
        _doctor_add_result "ERR" "冲突副本" "发现${critical}个严重冲突！必须从备份恢复"
        return
    fi
    if [ "$warning" -gt 0 ]; then
        _doctor_add_result "WARN" "冲突副本" "发现${warning}个警告级冲突，建议检查"
        return
    fi
    if [ "$info" -gt 0 ]; then
        _doctor_add_result "INFO" "冲突副本" "发现${info}个临时文件/无害冲突"
        return
    fi
    _doctor_add_result "OK" "冲突副本" "未发现冲突文件"
}

_doctor_check_lock() {
    local sync_root="$1"
    local repo_name="$2"
    lock_init "$sync_root" >/dev/null 2>&1 || true

    local lockfile="${sync_root}/locks/${repo_name}.lock.json"
    if [ ! -f "$lockfile" ]; then
        _doctor_add_result "OK" "锁状态" "无锁（可用）"
        return
    fi

    local my_device_id="${_LOCK_UTILS_DEVICE_ID:-}"
    local holder_device holder_pid holder_ts
    holder_device="$(_lock_read_json_field "$lockfile" "device_id" 2>/dev/null || echo "")"

    _lock_ensure_device_id 2>/dev/null || true
    my_device_id="${_LOCK_UTILS_DEVICE_ID:-}"

    if _lock_is_timeout_lock "$lockfile"; then
        _doctor_add_result "ERR" "锁状态" "超时锁，需要清理"
        return
    fi

    if [ -n "$my_device_id" ] && [ "$holder_device" = "$my_device_id" ]; then
        holder_pid="$(_lock_read_json_field "$lockfile" "pid" 2>/dev/null || echo "")"
        if [ -n "$holder_pid" ] && _lock_pid_exists "$holder_pid" 2>/dev/null; then
            _doctor_add_result "INFO" "锁状态" "被本设备持有"
            return
        fi
        _doctor_add_result "ERR" "锁状态" "本设备残留锁（进程已退出）"
        return
    fi

    _doctor_add_result "WARN" "锁状态" "被其他设备持有，请等待"
}

_doctor_check_head() {
    local repo_path="$1"
    local bare_repo="$2"

    local local_head
    if ! local_head="$(_doctor_git -C "$repo_path" rev-parse HEAD 2>/dev/null)"; then
        _doctor_add_result "WARN" "HEAD对比" "无法获取本地HEAD（可能无提交）"
        return
    fi
    local_head="$(echo "$local_head" | head -1 | tr -d '[:space:]')"

    if [ ! -d "$bare_repo" ]; then
        _doctor_add_result "WARN" "HEAD对比" "裸仓库不存在，无法对比"
        return
    fi

    local bare_head
    if ! bare_head="$(_doctor_git -C "$bare_repo" rev-parse HEAD 2>/dev/null)"; then
        _doctor_add_result "WARN" "HEAD对比" "无法获取裸仓库HEAD（裸仓库可能为空）"
        return
    fi
    bare_head="$(echo "$bare_head" | head -1 | tr -d '[:space:]')"

    if [ "$local_head" = "$bare_head" ]; then
        _doctor_add_result "OK" "HEAD对比" "本地与裸仓库一致 (${local_head:0:7})"
        return
    fi

    local mb
    mb="$(git -C "$repo_path" merge-base "$local_head" "$bare_head" 2>/dev/null || echo "")"
    mb="$(echo "$mb" | head -1 | tr -d '[:space:]')"
    if [ -n "$mb" ]; then
        if [ "$mb" = "$bare_head" ]; then
            local ahead
            ahead="$(git -C "$repo_path" rev-list --count "$bare_head..$local_head" 2>/dev/null || echo "?")"
            _doctor_add_result "INFO" "HEAD对比" "本地领先远程 ${ahead} 个提交（有未push提交）"
            return
        fi
        if [ "$mb" = "$local_head" ]; then
            local behind
            behind="$(git -C "$repo_path" rev-list --count "$local_head..$bare_head" 2>/dev/null || echo "?")"
            _doctor_add_result "WARN" "HEAD对比" "本地落后远程 ${behind} 个提交，需要先pull"
            return
        fi
    fi
    _doctor_add_result "ERR" "HEAD对比" "本地与裸仓库HEAD不一致（已分歧），本地=${local_head:0:7} 远程=${bare_head:0:7}"
}

_doctor_check_loose_objects() {
    local repo_path="$1"
    local count_output
    count_output="$(_doctor_git -C "$repo_path" count-objects -v 2>/dev/null)" || {
        _doctor_add_result "WARN" "松散对象" "count-objects执行失败"
        return
    }
    local loose=0 packs=0
    loose="$(echo "$count_output" | grep '^count:' | awk '{print $2}' | head -1)"
    packs="$(echo "$count_output" | grep '^packs:' | awk '{print $2}' | head -1)"
    loose="${loose:-0}"
    packs="${packs:-0}"

    if [ "$loose" -ge "$DOCTOR_LOOSE_OBJ_ERR" ]; then
        _doctor_add_result "ERR" "松散对象" "松散对象 ${loose} 个，超过 ${DOCTOR_LOOSE_OBJ_ERR}，必须GC"
        return
    fi
    if [ "$loose" -ge "$DOCTOR_LOOSE_OBJ_WARN" ]; then
        _doctor_add_result "WARN" "松散对象" "松散对象 ${loose} 个，超过 ${DOCTOR_LOOSE_OBJ_WARN}，建议GC"
        return
    fi
    _doctor_add_result "OK" "松散对象" "${loose} 个松散对象，${packs} 个pack文件"
}

_doctor_check_pack_files() {
    local repo_path="$1"
    local git_dir
    git_dir="$(git -C "$repo_path" rev-parse --git-dir 2>/dev/null || echo "")"
    if [ -z "$git_dir" ]; then
        _doctor_add_result "WARN" "Pack文件" "无法定位git目录"
        return
    fi
    if [[ "$git_dir" != /* ]]; then
        git_dir="$repo_path/$git_dir"
    fi
    local pack_dir="$git_dir/objects/pack"
    if [ ! -d "$pack_dir" ]; then
        _doctor_add_result "OK" "Pack文件" "pack目录不存在（新仓库）"
        return
    fi
    local pack_count
    pack_count="$(find "$pack_dir" -maxdepth 1 -name '*.pack' -type f 2>/dev/null | wc -l)"
    pack_count="${pack_count:-0}"
    if [ "$pack_count" -gt "$DOCTOR_MAX_PACK_FILES" ]; then
        _doctor_add_result "WARN" "Pack文件" "${pack_count} 个pack文件（超过${DOCTOR_MAX_PACK_FILES}），建议GC优化"
        return
    fi
    _doctor_add_result "OK" "Pack文件" "${pack_count} 个pack文件"
}

_doctor_check_fsck() {
    local bare_repo="$1"
    if [ ! -d "$bare_repo" ]; then
        _doctor_add_result "ERR" "Fsck完整性" "裸仓库不存在"
        return
    fi
    local fsck_output
    set +e
    fsck_output="$(git -C "$bare_repo" fsck --full --strict 2>&1)"
    local fsck_exit=$?
    set -e

    local errors=0 dangling=0
    while IFS= read -r line; do
        if [[ "$line" =~ ^(error|missing|broken) ]]; then
            errors=$((errors + 1))
        elif [[ "$line" =~ ^dangling ]]; then
            dangling=$((dangling + 1))
        fi
    done <<< "$fsck_output"

    if [ "$errors" -gt 0 ]; then
        local sample
        sample="$(echo "$fsck_output" | grep -E '^(error|missing|broken)' | head -2 | tr '\n' '; ')"
        _doctor_add_result "ERR" "Fsck完整性" "发现${errors}个错误: ${sample}"
        return
    fi
    if [ "$dangling" -gt 0 ]; then
        _doctor_add_result "INFO" "Fsck完整性" "通过，有${dangling}个悬挂对象（无害）"
        return
    fi
    _doctor_add_result "OK" "Fsck完整性" "通过，无错误"
}

_doctor_check_backup() {
    local sync_root="$1"
    local repo_name="$2"
    local backup_dir="${sync_root}/backups/${repo_name}"
    if [ ! -d "$backup_dir" ]; then
        _doctor_add_result "ERR" "备份健康" "备份目录不存在，无任何备份"
        return
    fi
    local latest_bundle
    latest_bundle="$(find "$backup_dir" -maxdepth 1 -name '*.bundle' -type f -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | awk '{print $2}')"
    if [ -z "$latest_bundle" ]; then
        latest_bundle="$(ls -t "$backup_dir"/*.bundle 2>/dev/null | head -1)"
    fi
    if [ -z "$latest_bundle" ] || [ ! -f "$latest_bundle" ]; then
        _doctor_add_result "ERR" "备份健康" "未找到任何.bundle备份文件"
        return
    fi
    local bundle_mtime now age_days
    bundle_mtime="$(stat -c%Y "$latest_bundle" 2>/dev/null || stat -f%m "$latest_bundle" 2>/dev/null || echo 0)"
    now="$(date +%s)"
    age_days=$(( (now - bundle_mtime) / 86400 ))
    local bname
    bname="$(basename "$latest_bundle")"
    if [ "$age_days" -gt "$DOCTOR_BACKUP_ERR_DAYS" ]; then
        _doctor_add_result "ERR" "备份健康" "最新备份是${age_days}天前（超过${DOCTOR_BACKUP_ERR_DAYS}天），必须立即备份"
        return
    fi
    if [ "$age_days" -gt "$DOCTOR_BACKUP_WARN_DAYS" ]; then
        _doctor_add_result "WARN" "备份健康" "最新备份是${age_days}天前（超过${DOCTOR_BACKUP_WARN_DAYS}天），建议备份"
        return
    fi
    _doctor_add_result "OK" "备份健康" "最新备份 ${bname}，${age_days}天前"
}

_doctor_check_config() {
    local repo_path="$1"
    local os
    os="$(_doctor_detect_os)"
    local issues=""

    local autocrlf
    autocrlf="$(git -C "$repo_path" config --get core.autocrlf 2>/dev/null || git config --global --get core.autocrlf 2>/dev/null || echo "")"
    local expected_autocrlf="input"
    if [ "$os" = "win" ]; then expected_autocrlf="true"; fi
    if [ "$autocrlf" != "$expected_autocrlf" ]; then
        issues="${issues}core.autocrlf=${autocrlf}(推荐${expected_autocrlf}); "
    fi

    local gc_auto
    gc_auto="$(git -C "$repo_path" config --get gc.auto 2>/dev/null || git config --global --get gc.auto 2>/dev/null || echo "")"
    if [ "$gc_auto" != "6700" ]; then
        issues="${issues}gc.auto=${gc_auto}(推荐6700); "
    fi

    local gc_autopack
    gc_autopack="$(git -C "$repo_path" config --get gc.autopacklimit 2>/dev/null || git config --global --get gc.autopacklimit 2>/dev/null || echo "")"
    if [ "$gc_autopack" != "1" ]; then
        issues="${issues}gc.autopacklimit=${gc_autopack}(推荐1); "
    fi

    if [ "$os" = "win" ]; then
        local longpaths
        longpaths="$(git -C "$repo_path" config --get core.longpaths 2>/dev/null || git config --global --get core.longpaths 2>/dev/null || echo "")"
        if [ "$longpaths" != "true" ]; then
            issues="${issues}core.longpaths=${longpaths}(推荐true); "
        fi
    fi

    if [ -n "$issues" ]; then
        issues="${issues%; }"
        _doctor_add_result "WARN" "配置检查" "$issues"
        return
    fi
    _doctor_add_result "OK" "配置检查" "关键配置符合推荐值"
}

_doctor_check_disk_space() {
    local sync_root="$1"
    if [ ! -d "$sync_root" ]; then
        _doctor_add_result "WARN" "磁盘空间" "SyncRoot不存在，无法检查"
        return
    fi
    local free_kb free_gb
    free_kb="$(df -k "$sync_root" 2>/dev/null | awk 'NR==2 {print $4}' || echo 0)"
    free_kb="${free_kb:-0}"
    free_gb=$((free_kb / 1024 / 1024))

    if [ "$free_gb" -lt "$DOCTOR_DISK_ERR_GB" ]; then
        _doctor_add_result "ERR" "磁盘空间" "可用空间 ${free_gb}GB（不足${DOCTOR_DISK_ERR_GB}GB）"
        return
    fi
    if [ "$free_gb" -lt "$DOCTOR_DISK_WARN_GB" ]; then
        _doctor_add_result "WARN" "磁盘空间" "可用空间 ${free_gb}GB（不足${DOCTOR_DISK_WARN_GB}GB）"
        return
    fi
    _doctor_add_result "OK" "磁盘空间" "可用空间 ${free_gb}GB"
}

_doctor_print_results() {
    local i
    for i in "${!_DOCTOR_RESULTS[@]}"; do
        _doctor_write_check "${_DOCTOR_RESULTS[$i]}" "${_DOCTOR_NAMES[$i]}" "${_DOCTOR_DETAILS[$i]}"
    done
}

_doctor_reset_results() {
    _DOCTOR_RESULTS=()
    _DOCTOR_NAMES=()
    _DOCTOR_DETAILS=()
    _DOCTOR_OK_COUNT=0
    _DOCTOR_WARN_COUNT=0
    _DOCTOR_ERR_COUNT=0
    _DOCTOR_INFO_COUNT=0
}

_doctor_fix_temp_files() {
    local bare_repo="$1"
    if [ ! -d "$bare_repo" ]; then return 1; fi
    echo ""
    echo "=== 自动修复：清理临时文件 ==="
    _doctor_color "yellow" "⚠️  请确认没有Git进程正在操作此仓库！"
    echo ""
    echo -n "确认清理临时文件？(YES/no): "
    read -r confirm
    if [ "$confirm" != "YES" ]; then echo "跳过"; return 1; fi

    local deleted=0
    local f
    while IFS= read -r -d '' f; do
        rm -f "$f" && _doctor_color "green" "  已删除: $(basename "$f")" && echo "" && deleted=$((deleted + 1))
    done < <(find "$bare_repo" \( -name '*.tmp' -o -name '*.pack-tmp' -o -name '*.part' -o -name '*.temp' -o -name '*.downloading' -o -name 'tmp_pack_*' \) -type f -print0 2>/dev/null)

    while IFS= read -r -d '' f; do
        local bname
        bname="$(basename "$f")"
        if [ "$bname" != "HEAD.lock" ] && ! [[ "$bname" =~ ^pack-.+\.lock$ ]]; then
            rm -f "$f" && _doctor_color "green" "  已删除: $bname" && echo "" && deleted=$((deleted + 1))
        fi
    done < <(find "$bare_repo" -name '*.lock' -type f -print0 2>/dev/null)

    echo "清理完成: 删除 $deleted 个临时文件"
    [ "$deleted" -gt 0 ]
}

_doctor_fix_gc() {
    local repo_path="$1"
    echo ""
    echo "=== 自动修复：执行 git gc ==="
    _doctor_color "yellow" "⚠️  GC会重写pack文件，请确认没有其他设备/进程在操作！"
    echo ""
    echo -n "确认执行 git gc？(YES/no): "
    read -r confirm
    if [ "$confirm" != "YES" ]; then echo "跳过"; return 1; fi
    git -C "$repo_path" gc --aggressive --prune=now
    return $?
}

_doctor_fix_backup() {
    local repo_path="$1"
    local sync_root="$2"
    local repo_name="$3"
    echo ""
    echo "=== 自动修复：创建新备份 ==="
    local backup_dir="${sync_root}/backups/${repo_name}"
    mkdir -p "$backup_dir"
    local timestamp
    timestamp="$(date +%Y%m%d-%H%M%S)"
    local bundle_file="${backup_dir}/${repo_name}-${timestamp}.bundle"
    echo -n "确认创建备份到 $bundle_file？(YES/no): "
    read -r confirm
    if [ "$confirm" != "YES" ]; then echo "跳过"; return 1; fi
    if git -C "$repo_path" bundle create "$bundle_file" --all; then
        _doctor_color "green" "备份已创建: $bundle_file"
        echo ""
        return 0
    fi
    _doctor_color "red" "备份创建失败"
    echo ""
    return 1
}

git_doctor_check() {
    local repo_path="${1:-.}"
    local mode="${2:-quick}"
    local sync_root="${3:-}"
    local remote_name="${4:-baidu}"

    _doctor_reset_results
    repo_path="$(_doctor_resolve_fullpath "$repo_path")"

    local remote_url=""
    if [ -z "$sync_root" ]; then
        if ! sync_root="$(_doctor_infer_sync_root "$repo_path" "$remote_name" "remote_url")"; then
            echo ""
            _doctor_add_result "ERR" "SyncRoot推断" "无法自动推断SyncRoot，请指定SyncRoot参数"
            _doctor_print_results
            return 1
        fi
    else
        sync_root="$(_doctor_resolve_fullpath "$sync_root")"
        remote_url="$(git -C "$repo_path" remote get-url "$remote_name" 2>/dev/null | head -1 || echo "")"
    fi

    local repo_name
    repo_name="$(_doctor_get_repo_name "$repo_path" "$remote_url")"
    local bare_repo="${sync_root}/repos/${repo_name}.git"

    echo ""
    _doctor_color "magenta" "========================================"
    echo ""
    _doctor_color "magenta" "  git-doctor v${DOCTOR_VERSION} - 健康检查"
    echo ""
    _doctor_color "magenta" "========================================"
    echo ""
    echo "  仓库路径:   $repo_path"
    echo "  SyncRoot:   $sync_root"
    echo "  Remote:     $remote_name -> $remote_url"
    echo "  裸仓库:     $bare_repo"
    echo "  模式:       $mode"
    _doctor_color "magenta" "========================================"
    echo ""

    _doctor_check_git_version
    _doctor_check_repo_valid "$repo_path"
    _doctor_check_worktree "$repo_path"
    _doctor_check_temp_files "$bare_repo"
    _doctor_check_conflicts "$bare_repo"
    _doctor_check_lock "$sync_root" "$repo_name"
    _doctor_check_head "$repo_path" "$bare_repo"
    _doctor_check_loose_objects "$repo_path"

    if [ "$mode" = "full" ]; then
        _doctor_check_pack_files "$repo_path"
        _doctor_check_fsck "$bare_repo"
        _doctor_check_backup "$sync_root" "$repo_name"
        _doctor_check_config "$repo_path"
        _doctor_check_disk_space "$sync_root"
    fi

    echo ""
    _doctor_print_results

    local total=$((_DOCTOR_OK_COUNT + _DOCTOR_WARN_COUNT + _DOCTOR_ERR_COUNT + _DOCTOR_INFO_COUNT))
    echo ""
    _doctor_color "magenta" "========================================"
    echo ""
    _doctor_color "magenta" "  汇总: $total 个检查项"
    echo ""
    _doctor_color "green" "  绿色 [OK]:   $_DOCTOR_OK_COUNT"
    echo ""
    _doctor_color "cyan" "  蓝色 [INFO]: $_DOCTOR_INFO_COUNT"
    echo ""
    _doctor_color "yellow" "  黄色 [WARN]: $_DOCTOR_WARN_COUNT"
    echo ""
    _doctor_color "red" "  红色 [ERR]:  $_DOCTOR_ERR_COUNT"
    echo ""
    _doctor_color "magenta" "========================================"
    echo ""

    if [ "$_DOCTOR_ERR_COUNT" -gt 0 ]; then
        echo ""
        _doctor_color "red" "🛑 发现错误，请修复后再操作。"
        echo ""
        return 1
    elif [ "$_DOCTOR_WARN_COUNT" -gt 0 ]; then
        echo ""
        _doctor_color "yellow" "⚠️  存在警告，建议关注。"
        echo ""
        return 0
    else
        echo ""
        _doctor_color "green" "✅ 所有检查通过。"
        echo ""
        return 0
    fi
}

_doctor_show_usage() {
    cat <<USAGE
git-doctor.sh - Git 网盘同步健康检查工具 v${DOCTOR_VERSION}

用法:
  ./git-doctor.sh [选项]

选项（独立执行时）:
  -RepoPath <path>    本地工作仓库路径（默认 .）
  -SyncRoot <path>    网盘同步根目录（可从 remote 自动推断）
  -RemoteName <name>  Git remote 名称（默认 baidu）
  -Mode <quick|full>  检查模式: quick(默认) / full
  -All                检查 SyncRoot 下所有仓库
  -Fix                自动修复可安全修复的问题（需交互确认）
  -h, --help          显示此帮助

作为库使用（source）:
  source /path/to/git-doctor.sh

  git_doctor_check <repo_path> <mode> [sync_root] [remote_name]
  # 返回 0 = 无错误（可能有警告），1 = 有错误

退出码:
  0 = 无错误（可能有警告）
  1 = 存在错误，应阻止 push

检查项 (quick):
  Git版本、仓库有效性、工作区状态、半同步/临时文件、冲突副本、
  锁状态、HEAD对比、松散对象计数

检查项 (full，quick基础上增加):
  Pack文件数、fsck完整性、备份健康、配置检查、磁盘空间

示例:
  # 快速检查当前仓库
  ./git-doctor.sh

  # 全面检查
  ./git-doctor.sh -Mode full

  # 检查并自动修复
  ./git-doctor.sh -Mode full -Fix

  # 检查所有仓库
  ./git-doctor.sh -All -SyncRoot ~/BaiduSync/git-sync
USAGE
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    REPO_PATH="."
    SYNC_ROOT=""
    REMOTE_NAME=""
    MODE="quick"
    DO_ALL=0
    DO_FIX=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -RepoPath)   REPO_PATH="$2"; shift 2 ;;
            -SyncRoot)   SYNC_ROOT="$2"; shift 2 ;;
            -RemoteName) REMOTE_NAME="$2"; shift 2 ;;
            -Mode)       MODE="$2"; shift 2 ;;
            -All)        DO_ALL=1; shift ;;
            -Fix)        DO_FIX=1; shift ;;
            -h|--help)   _doctor_show_usage; exit 0 ;;
            -*) echo "未知选项: $1" >&2; _doctor_show_usage; exit 2 ;;
            *) REPO_PATH="$1"; shift ;;
        esac
    done

    if [ -z "$REMOTE_NAME" ]; then REMOTE_NAME="baidu"; fi

    if [ "$DO_ALL" -eq 1 ]; then
        if [ -z "$SYNC_ROOT" ]; then
            echo "错误: -All 模式需要指定 -SyncRoot" >&2
            _doctor_show_usage
            exit 2
        fi
        SYNC_ROOT="$(_doctor_resolve_fullpath "$SYNC_ROOT")"
        repos_dir="${SYNC_ROOT}/repos"
        if [ ! -d "$repos_dir" ]; then
            echo "错误: repos 目录不存在: $repos_dir" >&2
            exit 2
        fi
        total_err=0
        total_warn=0
        repos_checked=0
        for bare in "$repos_dir"/*.git; do
            [ -d "$bare" ] || continue
            bname="$(basename "$bare" .git)"
            echo ""
            echo ""
            _doctor_color "magenta" ">>>>>>>>>> 仓库: ${bname}.git <<<<<<<<<<"
            echo ""
            set +e
            git_doctor_check "$REPO_PATH" "$MODE" "$SYNC_ROOT" "$REMOTE_NAME"
            local rc=$?
            set -e
            total_err=$((total_err + _DOCTOR_ERR_COUNT))
            total_warn=$((total_warn + _DOCTOR_WARN_COUNT))
            repos_checked=$((repos_checked + 1))
        done
        echo ""
        _doctor_color "magenta" "========================================"
        echo ""
        _doctor_color "magenta" "  全部仓库汇总: 检查 $repos_checked 个仓库"
        echo ""
        _doctor_color "magenta" "  总错误: $total_err, 总警告: $total_warn"
        echo ""
        _doctor_color "magenta" "========================================"
        echo ""
        if [ "$total_err" -gt 0 ]; then exit 1; else exit 0; fi
    fi

    set +e
    git_doctor_check "$REPO_PATH" "$MODE" "$SYNC_ROOT" "$REMOTE_NAME"
    doctor_rc=$?
    set -e

    if [ "$DO_FIX" -eq 1 ]; then
        fixed=0
        _doctor_reset_results

        if [ -z "$SYNC_ROOT" ]; then
            remote_url=""
            SYNC_ROOT="$(_doctor_infer_sync_root "$REPO_PATH" "$REMOTE_NAME" "remote_url" || echo "")"
        fi
        if [ -n "$SYNC_ROOT" ]; then
            SYNC_ROOT="$(_doctor_resolve_fullpath "$SYNC_ROOT")"
            remote_url="${remote_url:-$(git -C "$REPO_PATH" remote get-url "$REMOTE_NAME" 2>/dev/null | head -1 || echo "")}"
            repo_name="$(_doctor_get_repo_name "$REPO_PATH" "$remote_url")"
            bare_repo="${SYNC_ROOT}/repos/${repo_name}.git"

            if _doctor_fix_temp_files "$bare_repo"; then fixed=1; fi

            _doctor_check_loose_objects "$REPO_PATH"
            for i in "${!_DOCTOR_RESULTS[@]}"; do
                if [ "${_DOCTOR_NAMES[$i]}" = "松散对象" ] && { [ "${_DOCTOR_RESULTS[$i]}" = "ERR" ] || [ "${_DOCTOR_RESULTS[$i]}" = "WARN" ]; }; then
                    if _doctor_fix_gc "$REPO_PATH"; then fixed=1; fi
                    break
                fi
            done

            _doctor_reset_results
            _doctor_check_backup "$SYNC_ROOT" "$repo_name"
            for i in "${!_DOCTOR_RESULTS[@]}"; do
                if [ "${_DOCTOR_NAMES[$i]}" = "备份健康" ] && [ "${_DOCTOR_RESULTS[$i]}" = "ERR" ]; then
                    if _doctor_fix_backup "$REPO_PATH" "$SYNC_ROOT" "$repo_name"; then fixed=1; fi
                    break
                fi
            done
        fi

        if [ "$fixed" -eq 1 ]; then
            echo ""
            _doctor_color "green" "自动修复完成，建议重新运行 git-doctor 验证。"
            echo ""
        fi
    fi

    exit "$doctor_rc"
fi
