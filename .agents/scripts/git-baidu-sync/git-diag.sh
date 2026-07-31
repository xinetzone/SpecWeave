#!/usr/bin/env bash
# git-diag.sh - Git 百度网盘同步一键诊断脚本
# 收集诊断信息并生成结构化报告
# source 作为库使用，或直接执行

# 注意：诊断脚本本身不应因某个检查失败而退出，应继续收集信息
# 因此不使用 set -e，而是手动处理每个命令的错误

set -uo pipefail

DIAG_VERSION="1.0.0"
DIAG_COLOR_ENABLED=1
DIAG_START_TIME=$(date +%s)
DIAG_ERRORS=0
DIAG_WARNINGS=0
DIAG_INFOS=0
DIAG_OKS=0
DIAG_LOG_LINES=()
DIAG_SUGGESTIONS=()

DIAG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIAG_LOCK_UTILS_LOADED=0
DIAG_CONFLICTS_LOADED=0

if [ -t 1 ]; then
    DIAG_COLOR_ENABLED=1
else
    DIAG_COLOR_ENABLED=0
fi

# 加载依赖库（容错）
if [ -f "$DIAG_SCRIPT_DIR/lock-utils.sh" ]; then
    # shellcheck source=lock-utils.sh
    # 注意：lock-utils.sh 使用 set -euo pipefail，我们在子shell中加载避免影响
    # 或者直接source但临时调整设置
    _diag_old_opts=$(set +o)
    set +e
    source "$DIAG_SCRIPT_DIR/lock-utils.sh" 2>/dev/null || true
    eval "$_diag_old_opts"
    DIAG_LOCK_UTILS_LOADED=1
fi

if [ -f "$DIAG_SCRIPT_DIR/check-conflicts.sh" ]; then
    _diag_old_opts=$(set +o)
    set +e
    source "$DIAG_SCRIPT_DIR/check-conflicts.sh" 2>/dev/null || true
    eval "$_diag_old_opts"
    DIAG_CONFLICTS_LOADED=1
fi

_diag_colorize() {
    local color="$1"
    local text="$2"
    if [ "$DIAG_COLOR_ENABLED" -eq 1 ]; then
        local code=""
        case "$color" in
            red)     code="31" ;;
            green)   code="32" ;;
            yellow)  code="33" ;;
            blue)    code="34" ;;
            magenta) code="35" ;;
            cyan)    code="36" ;;
            darkcyan) code="36;1" ;;
            gray)    code="90" ;;
            darkgray) code="90" ;;
            darkyellow) code="33;1" ;;
            darkred) code="31;1" ;;
            white)   code="0" ;;
            *)       code="0" ;;
        esac
        printf '\033[%sm%s\033[0m\n' "$code" "$text"
    else
        echo "$text"
    fi
    DIAG_LOG_LINES+=("$text")
}

_diag_write() {
    local status="$1"
    local name="$2"
    local detail="${3:-}"
    local prefix text
    local color="white"

    case "$status" in
        OK)
            prefix="[OK]  "
            color="green"
            DIAG_OKS=$((DIAG_OKS + 1))
            ;;
        WARN)
            prefix="[WARN]"
            color="yellow"
            DIAG_WARNINGS=$((DIAG_WARNINGS + 1))
            ;;
        ERR)
            prefix="[ERR] "
            color="red"
            DIAG_ERRORS=$((DIAG_ERRORS + 1))
            ;;
        INFO)
            prefix="[INFO]"
            color="cyan"
            DIAG_INFOS=$((DIAG_INFOS + 1))
            ;;
    esac

    if [ -n "$detail" ]; then
        text="$prefix $name - $detail"
    else
        text="$prefix $name"
    fi

    if [ "$DIAG_COLOR_ENABLED" -eq 1 ]; then
        local pcode=""
        case "$status" in
            OK) pcode="32" ;;
            WARN) pcode="33" ;;
            ERR) pcode="31" ;;
            INFO) pcode="36" ;;
        esac
        printf '\033[%sm%s\033[0m' "$pcode" "$prefix"
        if [ -n "$detail" ]; then
            printf ' %s - %s\n' "$name" "$detail"
        else
            printf ' %s\n' "$name"
        fi
    else
        echo "$text"
    fi
    DIAG_LOG_LINES+=("$text")
}

_diag_section() {
    local title="$1"
    local line="========================================"
    _diag_colorize darkcyan ""
    _diag_colorize darkcyan "$line"
    _diag_colorize darkcyan "  $title"
    _diag_colorize darkcyan "$line"
}

_diag_suggest() {
    DIAG_SUGGESTIONS+=("$1")
}

_diag_invoke_git() {
    local workdir="${1:-}"
    shift
    if [ -n "$workdir" ] && [ "$workdir" != "." ]; then
        git -C "$workdir" "$@" 2>&1
        return $?
    else
        git "$@" 2>&1
        return $?
    fi
}

_diag_resolve_path() {
    local p="$1"
    if [[ "$p" = /* ]]; then
        (cd "$p" 2>/dev/null && pwd) || echo "$p"
    else
        (cd "$(pwd)" && cd "$p" 2>/dev/null && pwd) || echo "$(pwd)/$p"
    fi
}

_diag_detect_os() {
    local uname_out
    uname_out="$(uname -s 2>/dev/null || echo unknown)"
    case "$uname_out" in
        Linux*)                     echo "linux" ;;
        Darwin*)                    echo "macos" ;;
        CYGWIN*|MINGW*|MSYS*)       echo "win" ;;
        *)                          echo "unknown" ;;
    esac
}

_diag_get_repo_name() {
    local repo_path="$1"
    local remote_url="${2:-}"
    if [ -n "$remote_url" ]; then
        if [[ "$remote_url" =~ /([^/]+)\.git/*$ ]]; then
            echo "${BASH_REMATCH[1]}"
            return 0
        fi
    fi
    basename "$repo_path"
}

_diag_infer_sync_root() {
    local repo_path="$1"
    local rm_name="$2"
    local __out_var="$3"
    local remote_url
    remote_url=$(_diag_invoke_git "$repo_path" remote get-url "$rm_name" 2>/dev/null | head -1 | sed 's/[[:space:]]*$//')
    eval "$__out_var=\"$remote_url\""

    if [ -n "$remote_url" ] && [ -d "$remote_url" ]; then
        local bare_dir
        bare_dir="$(_diag_resolve_path "$remote_url")"
        local bare_name
        bare_name="$(basename "$bare_dir")"
        if [[ "$bare_name" == *.git ]]; then
            local repos_dir
            repos_dir="$(dirname "$bare_dir")"
            dirname "$repos_dir"
            return 0
        fi
    fi
    return 1
}

_diag_check_environment() {
    _diag_section "1. 基本环境信息"

    local git_ver
    if git_ver=$(git --version 2>&1); then
        _diag_write OK "Git版本" "$git_ver"
    else
        _diag_write ERR "Git版本" "无法执行git命令，请确认Git已安装并在PATH中"
        _diag_suggest "安装Git: https://git-scm.com/downloads"
    fi

    local os_type
    os_type="$(_diag_detect_os)"
    local os_desc="$os_type"
    case "$os_type" in
        linux) os_desc="Linux $(uname -r)" ;;
        macos) os_desc="macOS $(sw_vers -productVersion 2>/dev/null || echo unknown)" ;;
        win) os_desc="Windows" ;;
    esac
    _diag_write INFO "操作系统" "$os_desc"
    _diag_write INFO "脚本版本" "git-diag v$DIAG_VERSION"
    _diag_write INFO "诊断时间" "$(date '+%Y-%m-%d %H:%M:%S')"
}

_diag_check_repo_status() {
    local repo_path="$1"
    _diag_section "2. 仓库状态"

    if ! _diag_invoke_git "$repo_path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        _diag_write ERR "Git仓库检查" "'$repo_path' 不是有效的Git工作仓库"
        _diag_suggest "使用 cd 命令进入正确的工作仓库目录，或使用 --repo-path 参数指定仓库路径"
        return 1
    fi
    _diag_write OK "Git仓库" "有效的工作仓库"

    local repo_root
    repo_root="$(_diag_invoke_git "$repo_path" rev-parse --show-toplevel 2>/dev/null | head -1)"
    [ -n "$repo_root" ] && _diag_write INFO "仓库根目录" "$repo_root"

    local branch
    branch="$(_diag_invoke_git "$repo_path" rev-parse --abbrev-ref HEAD 2>/dev/null | head -1)"
    if [ -n "$branch" ] && [ "$branch" != "HEAD" ]; then
        _diag_write OK "当前分支" "$branch"
    else
        _diag_write WARN "当前分支" "无法获取当前分支（可能在detached HEAD状态）"
    fi

    local status_output
    status_output="$(_diag_invoke_git "$repo_path" status --porcelain 2>&1)"
    local status_exit=$?
    if [ $status_exit -ne 0 ]; then
        _diag_write ERR "工作区状态" "git status 执行失败"
    else
        local dirty_count
        dirty_count=$(echo "$status_output" | grep -c '[^[:space:]]' 2>/dev/null || echo 0)
        if [ "$dirty_count" -eq 0 ]; then
            _diag_write OK "工作区状态" "工作区干净 (clean)"
        else
            _diag_write WARN "工作区状态" "dirty：$dirty_count个更改"
            if [ "$dirty_count" -le 10 ]; then
                echo "$status_output" | head -10 | while IFS= read -r line; do
                    [ -n "$line" ] && _diag_colorize darkgray "       $line"
                done
            fi
            _diag_suggest "工作区有未提交更改，建议执行 git stash 或 git commit 后再操作"
        fi
    fi

    local head_hash
    head_hash="$(_diag_invoke_git "$repo_path" rev-parse HEAD 2>/dev/null | head -1)"
    if [ -n "$head_hash" ]; then
        _diag_write INFO "本地HEAD" "$head_hash"
    else
        _diag_write WARN "本地HEAD" "无法获取HEAD（可能没有提交）"
    fi

    return 0
}

_diag_check_remote() {
    local repo_path="$1"
    local rm_name="$2"
    local __out_var="$3"

    _diag_section "3. Remote配置"

    local remote_v
    remote_v="$(_diag_invoke_git "$repo_path" remote -v 2>&1)"
    if [ -z "$remote_v" ]; then
        _diag_write ERR "Remote列表" "未配置任何remote"
        _diag_suggest "添加baidu remote: git remote add baidu <SyncRoot>/repos/<repo>.git"
        eval "$__out_var=\"\""
        return 1
    fi

    echo "$remote_v" | while IFS= read -r line; do
        _diag_colorize gray "    $line"
    done

    if ! echo "$remote_v" | grep -q "^$rm_name	\|^$rm_name "; then
        _diag_write ERR "'$rm_name' remote" "不存在"
        _diag_suggest "添加baidu remote: git remote add $rm_name <SyncRoot>/repos/<repo>.git"
        eval "$__out_var=\"\""
        return 1
    fi
    _diag_write OK "'$rm_name' remote" "已配置"

    local remote_url
    remote_url="$(_diag_invoke_git "$repo_path" remote get-url "$rm_name" 2>/dev/null | head -1 | sed 's/[[:space:]]*$//')"
    eval "$__out_var=\"$remote_url\""

    if [ -z "$remote_url" ]; then
        _diag_write ERR "Remote URL" "无法获取remote URL"
        return 1
    fi

    _diag_write INFO "Remote URL" "$remote_url"

    if [[ "$remote_url" =~ ^[a-z]+:// ]] || [[ "$remote_url" =~ ^git@ ]]; then
        _diag_write WARN "Remote路径" "这是一个网络URL，不是本地路径（本方案使用本地网盘路径）"
        _diag_suggest "baidu remote应指向网盘本地同步目录，例如: ~/BaiduSync/git-sync/repos/myrepo.git"
    fi

    if [ -d "$remote_url" ]; then
        if [ -f "$remote_url/HEAD" ] && [ -d "$remote_url/objects" ] && [ -d "$remote_url/refs" ]; then
            _diag_write OK "裸仓库路径" "路径存在且结构有效"
        else
            _diag_write ERR "裸仓库路径" "路径存在但不是有效的Git裸仓库（缺少HEAD/objects/refs）"
            _diag_suggest "检查路径是否正确，或重新初始化裸仓库"
        fi
    else
        _diag_write ERR "裸仓库路径" "路径不存在或不可访问: $remote_url"
        _diag_suggest "检查路径是否正确，网盘是否已同步完成，SyncRoot位置是否正确"
    fi

    if [[ "$remote_url" =~ [[:space:]] ]]; then
        _diag_write WARN "路径空格" "裸仓库路径包含空格，可能导致某些脚本问题（已加引号处理）"
    fi

    if [ -n "$remote_url" ] && [ -d "$remote_url" ]; then
        return 0
    else
        return 1
    fi
}

_diag_check_sync_root() {
    local sroot="$1"
    _diag_section "4. 网盘同步根目录结构"

    if [ -z "$sroot" ]; then
        _diag_write WARN "SyncRoot" "无法自动推断SyncRoot，部分检查将跳过"
        _diag_suggest "使用 --sync-root 参数指定网盘同步根目录路径"
        return 1
    fi

    local resolved_root
    resolved_root="$(_diag_resolve_path "$sroot")"
    _diag_write INFO "SyncRoot路径" "$resolved_root"

    if [ ! -d "$resolved_root" ]; then
        _diag_write ERR "SyncRoot目录" "目录不存在"
        _diag_suggest "确认SyncRoot路径正确，网盘客户端正在运行且已同步"
        return 1
    fi
    _diag_write OK "SyncRoot目录" "目录存在"

    local expected_dirs=("repos" "locks" "backups" "logs" "meta" "tmp")
    local missing=()
    for d in "${expected_dirs[@]}"; do
        if [ ! -d "$resolved_root/$d" ]; then
            missing+=("$d")
        fi
    done

    if [ ${#missing[@]} -eq 0 ]; then
        _diag_write OK "SyncRoot结构" "6个子目录全部存在 (repos/locks/backups/logs/meta/tmp)"
    else
        _diag_write WARN "SyncRoot结构" "缺少子目录: ${missing[*]}"
        _diag_suggest "运行 init-sync-dir.sh 初始化/修复同步目录结构"
    fi

    return 0
}

_diag_check_lock() {
    local sroot="$1"
    local repo_name="$2"
    _diag_section "5. 锁状态"

    if [ -z "$sroot" ] || [ "$DIAG_LOCK_UTILS_LOADED" -ne 1 ]; then
        _diag_write INFO "锁检查" "跳过（SyncRoot未指定或lock-utils未加载）"
        return
    fi

    set +e
    _lock_init "$sroot" 2>/dev/null
    local lock_init_ok=$?
    set -euo pipefail
    if [ $lock_init_ok -ne 0 ]; then
        _diag_write ERR "锁初始化" "_lock_init失败"
        return
    fi

    local lockfile
    lockfile="$(_lock_get_lockfile_path "$repo_name" 2>/dev/null || echo "")"
    if [ -z "$lockfile" ] || [ ! -f "$lockfile" ]; then
        _diag_write OK "锁状态" "无锁（仓库可用）"
        return
    fi

    _diag_write WARN "锁文件" "存在: $lockfile"

    local holder_device holder_pid holder_op holder_ts holder_host
    holder_device="$(_lock_read_json_field "$lockfile" device_id 2>/dev/null || echo "?")"
    holder_pid="$(_lock_read_json_field "$lockfile" pid 2>/dev/null || echo "?")"
    holder_op="$(_lock_read_json_field "$lockfile" operation 2>/dev/null || echo "?")"
    holder_ts="$(_lock_read_json_field "$lockfile" acquired_at 2>/dev/null || echo "?")"
    holder_host="$(_lock_read_json_field "$lockfile" hostname 2>/dev/null || echo "?")"

    _diag_colorize darkyellow "    持有者 device_id: $holder_device"
    _diag_colorize darkyellow "    持有者 hostname: $holder_host"
    _diag_colorize darkyellow "    持有者 pid: $holder_pid"
    _diag_colorize darkyellow "    操作类型: $holder_op"
    _diag_colorize darkyellow "    获取时间: $holder_ts"

    local is_timed_out=0
    if _lock_is_timeout_lock "$lockfile" 2>/dev/null; then
        is_timed_out=1
    fi

    local my_device_id="${_LOCK_UTILS_DEVICE_ID:-}"
    if [ -n "$my_device_id" ] && [ "$holder_device" = "$my_device_id" ]; then
        local pid_alive=0
        if [ -n "$holder_pid" ] && [ "$holder_pid" != "?" ]; then
            if kill -0 "$holder_pid" 2>/dev/null || [ -d "/proc/$holder_pid" ]; then
                pid_alive=1
            fi
        fi
        if [ $pid_alive -eq 1 ]; then
            if [ "$holder_pid" = "$$" ]; then
                _diag_write INFO "锁持有状态" "被当前进程持有（重入）"
            else
                _diag_write WARN "锁持有状态" "被本设备其他进程持有（pid=$holder_pid）"
                _diag_suggest "等待该进程完成，或确认进程已退出后重试"
            fi
        else
            _diag_write WARN "锁持有状态" "本设备残留锁（pid=$holder_pid 不存在）"
            _diag_suggest "可以安全清理此残留锁: rm -f '$lockfile'"
        fi
    elif [ $is_timed_out -eq 1 ]; then
        local timeout_mins="${LOCK_DEFAULT_TIMEOUT_MINUTES:-30}"
        _diag_write WARN "锁持有状态" "超时锁（已持有超过${timeout_mins}分钟）"
        _diag_suggest "确认持有者设备已离线/崩溃后，使用 force-unlock.sh 强制释放锁"
    else
        _diag_write ERR "锁持有状态" "被其他设备持有，请勿操作！"
        _diag_suggest "等待持有设备 $holder_host 完成操作；如确认持有者已离线且超时，使用 force-unlock.sh"
    fi
}

_diag_check_conflicts_and_temp() {
    local sroot="$1"
    local repo_name="$2"
    local remote_url="$3"
    _diag_section "6. 冲突文件与临时文件"

    local bare_repo=""
    if [ -n "$remote_url" ] && [ -d "$remote_url" ]; then
        bare_repo="$(_diag_resolve_path "$remote_url")"
    elif [ -n "$sroot" ] && [ -n "$repo_name" ]; then
        bare_repo="$(_diag_resolve_path "$sroot")/repos/${repo_name}.git"
    fi

    if [ -z "$bare_repo" ] || [ ! -d "$bare_repo" ]; then
        _diag_write INFO "冲突扫描" "裸仓库不可访问，跳过"
        return
    fi

    local temp_count=0
    local temp_sample=()
    local tmp_f
    for pattern in "*.tmp" "*.pack-tmp" "*.part" "*.temp" "*.downloading"; do
        while IFS= read -r -d '' tmp_f; do
            temp_count=$((temp_count + 1))
            [ ${#temp_sample[@]} -lt 5 ] && temp_sample+=("${tmp_f#$bare_repo/}")
        done < <(find "$bare_repo" -name "$pattern" -type f -print0 2>/dev/null)
    done
    while IFS= read -r -d '' tmp_f; do
        temp_count=$((temp_count + 1))
        [ ${#temp_sample[@]} -lt 5 ] && temp_sample+=("${tmp_f#$bare_repo/}")
    done < <(find "$bare_repo" -name "tmp_pack_*" -type f -print0 2>/dev/null)

    while IFS= read -r -d '' stray_lock; do
        local rel="${stray_lock#$bare_repo/}"
        if [[ "$rel" != locks/* ]] && [[ "$(basename "$stray_lock")" != "HEAD.lock" ]] && [[ ! "$(basename "$stray_lock")" =~ ^pack-.+\.lock$ ]]; then
            temp_count=$((temp_count + 1))
            [ ${#temp_sample[@]} -lt 5 ] && temp_sample+=("$rel")
        fi
    done < <(find "$bare_repo" -name "*.lock" -type f -print0 2>/dev/null)

    if [ "$temp_count" -eq 0 ]; then
        _diag_write OK "临时文件检测" "未发现.tmp/.pack-tmp等半同步文件"
    else
        _diag_write ERR "临时文件检测" "发现$temp_count个临时文件"
        for s in "${temp_sample[@]}"; do
            _diag_colorize darkred "    $s"
        done
        [ "$temp_count" -gt 5 ] && _diag_colorize darkred "    ... 等 $temp_count 个"
        _diag_suggest "确认所有设备无Git/网盘操作后，运行 check-conflicts.sh -AutoClean 清理临时文件，或等待网盘同步完成"
    fi

    if [ "$DIAG_CONFLICTS_LOADED" -eq 1 ]; then
        set +e
        local scan_output
        scan_output="$(_conflicts_scan_simple "$bare_repo" 2>&1)"
        local scan_ok=$?
        set -euo pipefail

        local critical=0 warn=0 info=0
        critical=$(echo "$scan_output" | grep -c "CRITICAL" 2>/dev/null || echo 0)
        warn=$(echo "$scan_output" | grep -c "WARNING" 2>/dev/null || echo 0)
        info=$(echo "$scan_output" | grep -c "INFO" 2>/dev/null || echo 0)

        if [ "$critical" -gt 0 ]; then
            _diag_write ERR "冲突副本扫描" "发现$critical个严重冲突！（objects/pack/HEAD/packed-refs级别）"
            _diag_suggest "🛑 严重！仓库可能已损坏，立即停止所有操作，从最近的.bundle备份恢复"
        elif [ "$warn" -gt 0 ]; then
            _diag_write WARN "冲突副本扫描" "发现$warn个警告级冲突"
            _diag_suggest "确认无操作后人工检查并处理refs/config等冲突文件，参考故障排查手册场景15"
        elif [ "$info" -gt 0 ]; then
            _diag_write INFO "冲突副本扫描" "发现$info个可清理的临时/无害冲突文件"
        else
            _diag_write OK "冲突副本扫描" "未发现冲突文件"
        fi
    fi
}

_conflicts_scan_simple() {
    local bare="$1"
    local critical=0
    local warning=0
    local info=0
    local f rel class

    while IFS= read -r -d '' f; do
        rel="${f#$bare/}"
        local bname
        bname="$(basename "$f")"
        if [[ "$bname" =~ \([0-9]+\)(\.[^.]*)?$ ]] || [[ "$bname" == *冲突* ]] || [[ "$bname" == *"来自"* ]]; then
            local rel_lower
            rel_lower="$(echo "$rel" | tr '[:upper:]' '[:lower:]')"
            if [[ "$rel_lower" == objects/pack/* ]] || \
               [[ "$rel_lower" =~ ^objects/[0-9a-f]{2}/ ]] || \
               [[ "$bname" == HEAD* ]] || \
               [[ "$bname" == packed-refs* ]]; then
                echo "CRITICAL: $rel"
                critical=$((critical+1))
            else
                echo "WARNING: $rel"
                warning=$((warning+1))
            fi
        elif [[ "$bname" =~ \.(tmp|temp|pack-tmp)$ ]] || [[ "$bname" == tmp_pack_* ]]; then
            echo "INFO: $rel"
            info=$((info+1))
        fi
    done < <(find "$bare" -type f -print0 2>/dev/null)

    return 0
}

_diag_check_head_diff() {
    local repo_path="$1"
    local bare_repo_path="$2"
    _diag_section "7. HEAD对比（本地 vs 网盘裸仓库）"

    local local_head
    local_head="$(_diag_invoke_git "$repo_path" rev-parse HEAD 2>/dev/null | head -1)"
    if [ -z "$local_head" ]; then
        _diag_write WARN "本地HEAD" "无法获取（可能无提交）"
        return
    fi

    if [ -z "$bare_repo_path" ] || [ ! -d "$bare_repo_path" ]; then
        _diag_write WARN "远程HEAD" "裸仓库不可访问，无法对比"
        _diag_write INFO "本地HEAD" "$local_head"
        return
    fi

    local bare_head
    bare_head="$(git -C "$bare_repo_path" rev-parse HEAD 2>/dev/null | head -1)"
    if [ -z "$bare_head" ]; then
        _diag_write WARN "远程HEAD" "无法获取（裸仓库可能为空或损坏）"
        _diag_write INFO "本地HEAD" "$local_head"
        return
    fi

    _diag_write INFO "本地HEAD" "$local_head"
    _diag_write INFO "远程HEAD" "$bare_head"

    if [ "$local_head" = "$bare_head" ]; then
        _diag_write OK "HEAD一致性" "本地与远程一致 (${local_head:0:7})"
        return
    fi

    local mb
    mb="$(git -C "$repo_path" merge-base "$local_head" "$bare_head" 2>/dev/null | head -1)"
    if [ -n "$mb" ]; then
        if [ "$mb" = "$bare_head" ]; then
            local ahead
            ahead="$(git -C "$repo_path" rev-list --count "$bare_head..$local_head" 2>/dev/null || echo "?")"
            _diag_write INFO "HEAD差异" "本地领先远程 $ahead 个提交（有未push的提交）"
            _diag_suggest "执行 git-sync-push 推送本地提交到远程"
        elif [ "$mb" = "$local_head" ]; then
            local behind
            behind="$(git -C "$repo_path" rev-list --count "$local_head..$bare_head" 2>/dev/null || echo "?")"
            _diag_write WARN "HEAD差异" "本地落后远程 $behind 个提交（需要先pull）"
            _diag_suggest "执行 git-sync-pull 拉取远程最新提交"
        else
            _diag_write ERR "HEAD差异" "本地与远程已分叉（diverged）！本地=${local_head:0:7} 远程=${bare_head:0:7}"
            _diag_suggest "参考故障排查手册场景20处理分叉：git stash → git fetch → git rebase baidu/main 或 git merge baidu/main"
        fi
    else
        _diag_write ERR "HEAD差异" "无共同祖先（unrelated histories），本地与远程可能是不同仓库"
        _diag_suggest "确认remote路径正确；如确是首次拉取，使用 git pull baidu main --allow-unrelated-histories（参考场景9）"
    fi
}

_diag_check_objects() {
    local repo_path="$1"
    local do_full="$2"
    _diag_section "8. Git对象计数"

    local count_output
    count_output="$(_diag_invoke_git "$repo_path" count-objects -v 2>&1)"
    local count_exit=$?
    if [ $count_exit -ne 0 ]; then
        _diag_write WARN "对象计数" "git count-objects 执行失败"
        return
    fi

    local loose=0 packs=0 loose_size=0
    loose=$(echo "$count_output" | grep '^count: ' | awk '{print $2}' || echo 0)
    packs=$(echo "$count_output" | grep '^packs: ' | awk '{print $2}' || echo 0)
    loose_size=$(echo "$count_output" | grep '^size: ' | awk '{print $2}' || echo 0)

    local loose_size_kb
    loose_size_kb=$(awk "BEGIN {printf \"%.1f\", $loose_size/1024}")

    if [ "$loose" -ge 10000 ]; then
        _diag_write ERR "松散对象" "$loose 个（超过10000，必须执行git gc）"
        _diag_suggest "执行 git gc --aggressive --prune=now 优化仓库（确认无其他设备操作后）"
    elif [ "$loose" -ge 6700 ]; then
        _diag_write WARN "松散对象" "$loose 个（超过6700，建议执行git gc）"
        _diag_suggest "可运行 git gc 优化仓库性能"
    else
        _diag_write OK "松散对象" "$loose 个 ($loose_size_kb KB)"
    fi

    _diag_write INFO "Pack文件" "$packs 个"

    if [ "$do_full" = "1" ] && [ "$packs" -gt 1 ]; then
        _diag_write WARN "Pack文件数量" "$packs 个pack文件（超过1个），git gc会合并pack"
    fi
}

_diag_check_backup() {
    local sroot="$1"
    local repo_name="$2"
    _diag_section "9. 备份状态（仅Full模式）"

    if [ -z "$sroot" ] || [ -z "$repo_name" ]; then
        _diag_write INFO "备份检查" "跳过（SyncRoot/RepoName未知）"
        return
    fi

    local resolved_root
    resolved_root="$(_diag_resolve_path "$sroot")"
    local backup_dir="$resolved_root/backups/$repo_name"

    if [ ! -d "$backup_dir" ]; then
        _diag_write ERR "备份目录" "备份目录不存在"
        _diag_suggest "执行一次 git-sync-push 会自动创建备份，或运行 git-backup.sh 手动创建"
        return
    fi

    local bundle_count latest_bundle
    latest_bundle=$(ls -t "$backup_dir"/*.bundle 2>/dev/null | head -1)
    bundle_count=$(ls "$backup_dir"/*.bundle 2>/dev/null | wc -l | tr -d ' ')

    if [ -z "$latest_bundle" ] || [ ! -f "$latest_bundle" ]; then
        _diag_write ERR "备份文件" "未找到任何.bundle备份文件"
        _diag_suggest "运行 git-backup.sh 创建备份"
        return
    fi

    local bundle_name size_mb age_days
    bundle_name=$(basename "$latest_bundle")
    size_mb=$(awk "BEGIN {printf \"%.2f\", $(stat -c%s "$latest_bundle" 2>/dev/null || stat -f%z "$latest_bundle" 2>/dev/null || echo 0)/1024/1024}")
    local mtime
    mtime=$(stat -c%Y "$latest_bundle" 2>/dev/null || stat -f%m "$latest_bundle" 2>/dev/null || echo "$(date +%s)")
    age_days=$(( (DIAG_START_TIME - mtime) / 86400 ))

    _diag_write INFO "最新备份" "$bundle_name ($size_mb MB, ${age_days}天前)"
    _diag_write INFO "备份总数" "$bundle_count 个备份"

    if [ "$age_days" -gt 30 ]; then
        _diag_write ERR "备份时效" "最新备份是${age_days}天前（超过30天），必须立即备份！"
        _diag_suggest "运行 git-sync-push 或 git-backup.sh 创建新备份"
    elif [ "$age_days" -gt 7 ]; then
        _diag_write WARN "备份时效" "最新备份是${age_days}天前（超过7天），建议备份"
    else
        _diag_write OK "备份时效" "备份较新（${age_days}天内）"
    fi
}

_diag_check_recent_logs() {
    local sroot="$1"
    _diag_section "10. 最近日志"

    if [ -z "$sroot" ]; then
        _diag_write INFO "日志" "SyncRoot未知，跳过"
        return
    fi

    local resolved_root
    resolved_root="$(_diag_resolve_path "$sroot")"
    local logs_dir="$resolved_root/logs"

    if [ ! -d "$logs_dir" ]; then
        _diag_write INFO "日志目录" "logs目录不存在"
        return
    fi

    local count=0
    while IFS= read -r log_f; do
        [ -z "$log_f" ] && continue
        local lname lsize_kb age_min age_str
        lname=$(basename "$log_f")
        local lbytes
        lbytes=$(stat -c%s "$log_f" 2>/dev/null || stat -f%z "$log_f" 2>/dev/null || echo 0)
        lsize_kb=$(awk "BEGIN {printf \"%.1f\", $lbytes/1024}")
        local lmtime
        lmtime=$(stat -c%Y "$log_f" 2>/dev/null || stat -f%m "$log_f" 2>/dev/null || echo "$DIAG_START_TIME")
        age_min=$(( (DIAG_START_TIME - lmtime) / 60 ))
        if [ "$age_min" -lt 60 ]; then
            age_str="${age_min}分钟前"
        elif [ $((age_min / 60)) -lt 24 ]; then
            age_str="$((age_min / 60))小时前"
        else
            age_str="$((age_min / 1440))天前"
        fi
        _diag_colorize darkgray "    $lname - $lsize_kb KB - $age_str"
        count=$((count + 1))
        [ $count -ge 3 ] && break
    done < <(ls -t "$logs_dir"/* 2>/dev/null)

    if [ $count -eq 0 ]; then
        _diag_write INFO "日志文件" "未找到日志文件"
    else
        _diag_write INFO "最近日志文件" "$count 个"
    fi
}

_diag_check_config() {
    local repo_path="$1"
    _diag_section "11. Git配置检查"

    local os_type
    os_type="$(_diag_detect_os)"
    local issues=()

    local autocrlf
    autocrlf="$(_diag_invoke_git "$repo_path" config --get core.autocrlf 2>/dev/null | head -1)"
    if [ -z "$autocrlf" ]; then
        autocrlf="$(git config --global --get core.autocrlf 2>/dev/null | head -1 || echo "")"
    fi
    local expected_crlf
    if [ "$os_type" = "win" ]; then
        expected_crlf="true"
    else
        expected_crlf="input"
    fi
    if [ "$autocrlf" != "$expected_crlf" ]; then
        issues+=("core.autocrlf=$autocrlf (推荐$expected_crlf)")
    fi

    if [ "$os_type" != "win" ]; then
        local filemode
        filemode="$(_diag_invoke_git "$repo_path" config --get core.filemode 2>/dev/null | head -1)"
        if [ -z "$filemode" ]; then
            filemode="$(git config --global --get core.filemode 2>/dev/null | head -1 || echo "")"
        fi
        if [ "$filemode" != "false" ]; then
            issues+=("core.filemode=$filemode (推荐false，避免跨平台权限误报)")
        fi
    fi

    local quotepath
    quotepath="$(_diag_invoke_git "$repo_path" config --get core.quotepath 2>/dev/null | head -1)"
    if [ -z "$quotepath" ]; then
        quotepath="$(git config --global --get core.quotepath 2>/dev/null | head -1 || echo "")"
    fi
    if [ "$quotepath" != "false" ]; then
        issues+=("core.quotepath=$quotepath (推荐false以正确显示中文文件名)")
    fi

    local gcauto
    gcauto="$(_diag_invoke_git "$repo_path" config --get gc.auto 2>/dev/null | head -1)"
    if [ -z "$gcauto" ]; then
        gcauto="$(git config --global --get gc.auto 2>/dev/null | head -1 || echo "")"
    fi
    if [ "$gcauto" != "6700" ]; then
        issues+=("gc.auto=$gcauto (推荐6700)")
    fi

    if [ ${#issues[@]} -eq 0 ]; then
        _diag_write OK "Git配置" "关键配置符合推荐值"
    else
        _diag_write WARN "Git配置" "${#issues[@]}项配置可优化："
        for issue in "${issues[@]}"; do
            _diag_colorize darkyellow "    - $issue"
        done
        _diag_suggest "运行 setup-git-config.sh 自动配置推荐Git设置"
    fi
}

_diag_summary() {
    local end_time elapsed elapsed_str
    end_time=$(date +%s)
    elapsed=$((end_time - DIAG_START_TIME))
    elapsed_str=$(awk "BEGIN {printf \"%.1f\", $elapsed}")

    _diag_section "诊断总结"

    local total=$((DIAG_OKS + DIAG_WARNINGS + DIAG_ERRORS + DIAG_INFOS))
    _diag_colorize white "  总检查项: $total"
    _diag_colorize green "  [OK]  正常: $DIAG_OKS"
    _diag_colorize cyan "  [INFO] 提示: $DIAG_INFOS"
    _diag_colorize yellow "  [WARN] 警告: $DIAG_WARNINGS"
    _diag_colorize red "  [ERR]  错误: $DIAG_ERRORS"
    _diag_colorize gray "  耗时: ${elapsed_str}秒"
    _diag_colorize white ""

    if [ "$DIAG_ERRORS" -gt 0 ]; then
        _diag_colorize red "🛑 发现 $DIAG_ERRORS 个错误，必须修复后再执行push/pull！"
    elif [ "$DIAG_WARNINGS" -gt 0 ]; then
        _diag_colorize yellow "⚠️  发现 $DIAG_WARNINGS 个警告，建议关注和处理。"
    else
        _diag_colorize green "✅ 所有检查通过，仓库状态良好。"
    fi

    if [ ${#DIAG_SUGGESTIONS[@]} -gt 0 ]; then
        _diag_colorize cyan ""
        _diag_colorize cyan "推荐操作:"
        local idx=1
        for s in "${DIAG_SUGGESTIONS[@]}"; do
            _diag_colorize white "  $idx. $s"
            idx=$((idx + 1))
        done
    fi

    _diag_colorize darkgray ""
    _diag_colorize darkgray "提示: 详细故障排查方法参考 10-troubleshooting.md"
    _diag_colorize white ""
}

_diag_save_output() {
    local sroot="$1"
    local repo_name="$2"

    local logs_dir=""
    if [ -n "$sroot" ]; then
        logs_dir="$(_diag_resolve_path "$sroot")/logs"
    else
        logs_dir="$DIAG_SCRIPT_DIR/../../logs"
    fi
    logs_dir="$(cd "$logs_dir" 2>/dev/null && pwd || mkdir -p "$logs_dir" 2>/dev/null && cd "$logs_dir" && pwd || echo "/tmp")"
    mkdir -p "$logs_dir" 2>/dev/null || logs_dir="/tmp"

    local timestamp suffix outfile
    timestamp=$(date +%Y%m%d-%H%M%S)
    if [ -n "$repo_name" ]; then suffix="-$repo_name"; else suffix=""; fi
    outfile="$logs_dir/diag-$timestamp$suffix.txt"

    {
        echo "========================================"
        echo "  git-diag 诊断报告"
        echo "  生成时间: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "  脚本版本: v$DIAG_VERSION"
        echo "========================================"
        echo ""
        for line in "${DIAG_LOG_LINES[@]}"; do
            echo "$line"
        done
    } > "$outfile"

    _diag_colorize cyan "诊断报告已保存到: $outfile"
}

_diag_show_usage() {
    cat <<EOF
git-diag.sh - Git 百度网盘同步一键诊断脚本 v$DIAG_VERSION

用法:
  ./git-diag.sh [选项]

选项:
  --repo-path <path>   本地工作仓库路径（默认当前目录 .）
  --sync-root <path>   网盘同步根目录（可从remote自动推断）
  --remote-name <name> Git remote名称（默认 baidu）
  --full               完整诊断模式（增加备份检查等）
  --output             将诊断报告保存到文件
  --no-color           禁用彩色输出
  -h, --help           显示此帮助

输出标记:
  [OK]   正常项，无需处理
  [WARN] 警告项，建议关注
  [ERR]  错误项，必须修复后才能继续操作
  [INFO] 提示信息，供参考

示例:
  # 快速诊断当前仓库
  ./git-diag.sh

  # 完整诊断并保存报告
  ./git-diag.sh --full --output

  # 指定仓库路径和SyncRoot
  ./git-diag.sh --repo-path ~/projects/myrepo --sync-root ~/BaiduSync/git-sync
EOF
}

# 如果直接执行（不是被source）
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    REPO_PATH="."
    SYNC_ROOT=""
    REMOTE_NAME="baidu"
    FULL_MODE=0
    SAVE_OUTPUT=0

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --repo-path)
                REPO_PATH="$2"
                shift 2
                ;;
            --sync-root)
                SYNC_ROOT="$2"
                shift 2
                ;;
            --remote-name)
                REMOTE_NAME="$2"
                shift 2
                ;;
            --full)
                FULL_MODE=1
                shift
                ;;
            --output)
                SAVE_OUTPUT=1
                shift
                ;;
            --no-color)
                DIAG_COLOR_ENABLED=0
                shift
                ;;
            -h|--help)
                _diag_show_usage
                exit 0
                ;;
            *)
                echo "未知参数: $1" >&2
                _diag_show_usage >&2
                exit 2
                ;;
        esac
    done

    RESOLVED_REPO="$(_diag_resolve_path "$REPO_PATH")"
    REMOTE_URL=""

    if [ -z "$SYNC_ROOT" ]; then
        set +e
        INFERRED_SYNC="$(_diag_infer_sync_root "$RESOLVED_REPO" "$REMOTE_NAME" REMOTE_URL 2>/dev/null)"
        set -euo pipefail
        if [ -n "$INFERRED_SYNC" ] && [ -d "$INFERRED_SYNC" ]; then
            SYNC_ROOT="$INFERRED_SYNC"
        fi
    else
        set +e
        REMOTE_URL="$(git -C "$RESOLVED_REPO" remote get-url "$REMOTE_NAME" 2>/dev/null | head -1 | sed 's/[[:space:]]*$//')"
        set -euo pipefail
    fi

    REPO_NAME="$(_diag_get_repo_name "$RESOLVED_REPO" "$REMOTE_URL")"

    _diag_colorize magenta ""
    _diag_colorize magenta "========================================"
    _diag_colorize magenta "  git-diag v$DIAG_VERSION - 一键诊断"
    _diag_colorize magenta "========================================"
    if [ $FULL_MODE -eq 1 ]; then mode_str="full"; else mode_str="quick"; fi
    _diag_colorize gray "  仓库路径: $RESOLVED_REPO"
    if [ -n "$SYNC_ROOT" ]; then _diag_colorize gray "  SyncRoot: $SYNC_ROOT"; else _diag_colorize darkgray "  SyncRoot: <未指定，将尝试自动推断>"; fi
    _diag_colorize gray "  Remote:   $REMOTE_NAME"
    [ -n "$REMOTE_URL" ] && _diag_colorize gray "  RemoteURL: $REMOTE_URL"
    _diag_colorize gray "  模式:     $mode_str"
    _diag_colorize magenta "========================================"
    _diag_colorize magenta ""

    _diag_check_environment
    _diag_check_repo_status "$RESOLVED_REPO" || true
    _diag_check_remote "$RESOLVED_REPO" "$REMOTE_NAME" REMOTE_URL || true

    BARE_PATH=""
    if [ -n "$REMOTE_URL" ] && [ -d "$REMOTE_URL" ]; then
        BARE_PATH="$REMOTE_URL"
    elif [ -n "$SYNC_ROOT" ]; then
        BARE_PATH="$(_diag_resolve_path "$SYNC_ROOT")/repos/${REPO_NAME}.git"
    fi

    _diag_check_sync_root "$SYNC_ROOT" || true
    _diag_check_lock "$SYNC_ROOT" "$REPO_NAME" || true
    _diag_check_conflicts_and_temp "$SYNC_ROOT" "$REPO_NAME" "$REMOTE_URL" || true
    _diag_check_head_diff "$RESOLVED_REPO" "$BARE_PATH" || true
    _diag_check_objects "$RESOLVED_REPO" $FULL_MODE || true
    if [ $FULL_MODE -eq 1 ]; then
        _diag_check_backup "$SYNC_ROOT" "$REPO_NAME" || true
    fi
    _diag_check_recent_logs "$SYNC_ROOT" || true
    _diag_check_config "$RESOLVED_REPO" || true

    _diag_summary

    if [ $SAVE_OUTPUT -eq 1 ]; then
        _diag_save_output "$SYNC_ROOT" "$REPO_NAME"
    fi

    if [ "$DIAG_ERRORS" -gt 0 ]; then
        exit 1
    fi
    exit 0
fi
