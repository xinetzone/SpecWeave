#!/usr/bin/env bash
# git-sync-pull.sh - Git 网盘同步 Pull 工具 (Bash)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lock-utils.sh
source "$SCRIPT_DIR/lock-utils.sh"

COLOR_SUCCESS='\033[0;32m'
COLOR_STEP='\033[0;36m'
COLOR_WARNING='\033[0;33m'
COLOR_ERROR='\033[0;31m'
COLOR_INFO='\033[0;37m'
COLOR_HEADER='\033[0;35m'
COLOR_NC='\033[0m'

REPO_PATH='.'
SYNC_ROOT=''
REMOTE_NAME=''
FORCE=0

print_usage() {
    cat <<USAGE
用法: $(basename "$0") [选项] [仓库路径]

选项:
  -RepoPath <path>      本地工作仓库路径（默认.）
  -SyncRoot <path>      网盘根路径（必填，或从git config推断）
  -RemoteName <name>    remote名（默认baidu，可从git config读取）
  -Force                忽略锁警告强行pull
  -h, --help            显示此帮助
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -RepoPath) REPO_PATH="$2"; shift 2 ;;
        -SyncRoot) SYNC_ROOT="$2"; shift 2 ;;
        -RemoteName) REMOTE_NAME="$2"; shift 2 ;;
        -Force) FORCE=1; shift ;;
        -h|--help) print_usage; exit 0 ;;
        -*) echo "未知选项: $1" >&2; print_usage; exit 1 ;;
        *) REPO_PATH="$1"; shift ;;
    esac
done

msg_info()    { echo -e "${COLOR_INFO}[INFO] $*${COLOR_NC}"; }
msg_success() { echo -e "${COLOR_SUCCESS}[OK] $*${COLOR_NC}"; }
msg_warn()    { echo -e "${COLOR_WARNING}[WARN] $*${COLOR_NC}"; }
msg_error()   { echo -e "${COLOR_ERROR}[ERR] $*${COLOR_NC}" >&2; }
msg_step()    { echo -e ""; echo -e "${COLOR_HEADER}=== 步骤 $* ===${COLOR_NC}"; }
msg_header()  { echo -e "${COLOR_HEADER}$*${COLOR_NC}"; }

resolve_fullpath() {
    local p="$1"
    if [[ "$p" = /* ]]; then
        echo "$p"
    else
        echo "$(cd "$p" 2>/dev/null && pwd || echo "$(pwd)/$p")"
    fi
}

get_repo_name() {
    local repo_path="$1"
    local remote_url="$2"
    if [[ -n "$remote_url" ]]; then
        local basename_url
        basename_url="$(basename "$remote_url" .git)"
        if [[ -n "$basename_url" && "$basename_url" != "/" ]]; then
            echo "$basename_url"
            return 0
        fi
    fi
    basename "$repo_path"
}

test_conflict_copies() {
    local bare_repo="$1"
    local conflicts=()
    local pattern
    for pattern in '* (*)*' '* (冲突版本)*' '* (来自*)*'; do
        while IFS= read -r -d '' f; do
            conflicts+=("$f")
        done < <(find "$bare_repo" -name "$pattern" -print0 2>/dev/null)
    done
    if [[ ${#conflicts[@]} -gt 0 ]]; then
        printf '%s\n' "${conflicts[@]}"
        return 0
    fi
    return 1
}

test_temp_files() {
    local bare_repo="$1"
    local temps=()
    local f
    while IFS= read -r -d '' f; do
        local bname
        bname="$(basename "$f")"
        if [[ "$bname" != "HEAD.lock" && ! "$bname" =~ ^pack-.+\.lock$ ]]; then
            temps+=("$f")
        fi
    done < <(find "$bare_repo" \( -name '*.tmp' -o -name '*.pack-tmp' -o -name '*.lock' -o -name '*.part' -o -name '*.temp' -o -name '*.downloading' \) -type f -print0 2>/dev/null)
    if [[ ${#temps[@]} -gt 0 ]]; then
        printf '%s\n' "${temps[@]}"
        return 0
    fi
    return 1
}

write_sync_log() {
    local sync_root="$1"
    local operation="$2"
    local repo_name="$3"
    local result="$4"
    local extra_info="$5"

    local logs_dir="${sync_root}/logs"
    mkdir -p "$logs_dir"
    local date_str
    date_str=$(date +%Y%m%d)
    local log_file="${logs_dir}/sync-${date_str}.log"
    local timestamp
    timestamp=$(_lock_get_iso8601)
    _lock_ensure_device_id
    local device_id="$_LOCK_UTILS_DEVICE_ID"
    printf '%s\t%s\t%s\t%s\t%s\t%s\n' "$timestamp" "$device_id" "$operation" "$repo_name" "$result" "$extra_info" >> "$log_file"
}

echo ""
msg_header '========================================='
msg_header '  Git 网盘同步 - Pull 工具'
msg_header '========================================='
echo ""

REPO_PATH=$(resolve_fullpath "$REPO_PATH")

if ! git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    msg_error "不是有效的 Git 工作仓库: $REPO_PATH"
    exit 1
fi
msg_info "本地仓库: $REPO_PATH"

cd "$REPO_PATH"

if [[ -z "$REMOTE_NAME" ]]; then
    REMOTE_NAME=$(git config baidu-sync.remote 2>/dev/null || true)
    if [[ -z "$REMOTE_NAME" ]]; then
        REMOTE_NAME="baidu"
    fi
fi

REMOTE_URL=""
if remote_url_output=$(git remote get-url "$REMOTE_NAME" 2>/dev/null); then
    REMOTE_URL=$(echo "$remote_url_output" | head -1)
fi

if [[ -z "$SYNC_ROOT" ]]; then
    if [[ -n "$REMOTE_URL" && -d "$REMOTE_URL" ]]; then
        bare_git_dir="$REMOTE_URL"
        SYNC_ROOT=$(dirname "$(dirname "$bare_git_dir")")
    else
        msg_error "无法自动推断 SyncRoot，请使用 -SyncRoot 参数指定"
        exit 1
    fi
fi
SYNC_ROOT=$(resolve_fullpath "$SYNC_ROOT")

if ! lock_init "$SYNC_ROOT"; then
    msg_error "锁系统初始化失败"
    exit 1
fi

REPO_NAME=$(get_repo_name "$REPO_PATH" "$REMOTE_URL")
BARE_REPO_PATH="${SYNC_ROOT}/repos/${REPO_NAME}.git"

msg_info "SyncRoot: $SYNC_ROOT"
msg_info "仓库名: $REPO_NAME"
msg_info "裸仓库: $BARE_REPO_PATH"
msg_info "Remote: $REMOTE_NAME -> $REMOTE_URL"
echo ""

msg_step "1: 锁状态检查（只读检测，不获取写锁）"
LOCKFILE_PATH=$(_lock_get_lockfile_path "$REPO_NAME")
LOCK_HELD=0
if [[ -f "$LOCKFILE_PATH" ]]; then
    HOLDER_DEVICE=$(_lock_read_json_field "$LOCKFILE_PATH" "device_id")
    HOLDER_HOST=$(_lock_read_json_field "$LOCKFILE_PATH" "hostname")
    HOLDER_PID=$(_lock_read_json_field "$LOCKFILE_PATH" "pid")
    HOLDER_OP=$(_lock_read_json_field "$LOCKFILE_PATH" "operation")
    HOLDER_TS=$(_lock_read_json_field "$LOCKFILE_PATH" "acquired_at")

    IS_TIMEOUT=0
    if _lock_is_timeout_lock "$LOCKFILE_PATH"; then
        IS_TIMEOUT=1
    fi
    _lock_ensure_device_id 2>/dev/null || true
    MY_DEVICE_ID="${_LOCK_UTILS_DEVICE_ID:-}"
    IS_SELF=0
    if [[ -n "$MY_DEVICE_ID" && "$HOLDER_DEVICE" == "$MY_DEVICE_ID" ]]; then
        IS_SELF=1
    fi

    msg_warn "检测到活跃锁："
    echo "  device_id: $HOLDER_DEVICE"
    echo "  hostname:  $HOLDER_HOST"
    echo "  pid:       $HOLDER_PID"
    echo "  operation: $HOLDER_OP"
    echo "  since:     $HOLDER_TS"

    if [[ $IS_TIMEOUT -eq 1 ]]; then
        msg_warn "锁已超时，可安全继续"
        LOCK_HELD=0
    elif [[ $FORCE -eq 0 ]]; then
        if [[ $IS_SELF -eq 1 ]]; then
            msg_info "这是本设备持有的锁"
        else
            echo ""
            msg_error "其他设备正在 push，此时 pull 可能得到不完整状态！"
            read -r -p "是否继续 pull？(y/N) " answer
            if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
                msg_warn "用户取消 pull"
                exit 0
            fi
        fi
    else
        msg_warn "-Force 已指定，忽略锁警告继续 pull"
    fi
else
    msg_success "无活跃写锁，安全"
fi

msg_step "2: 冲突副本检测"
if [[ ! -d "$BARE_REPO_PATH" ]]; then
    msg_error "裸仓库不存在: $BARE_REPO_PATH"
    exit 1
fi
conflict_output=$(test_conflict_copies "$BARE_REPO_PATH" 2>/dev/null) || true
if [[ -n "$conflict_output" ]]; then
    conflict_count=$(echo "$conflict_output" | wc -l)
    msg_error "检测到 $conflict_count 个冲突副本文件："
    echo "$conflict_output" | head -10 | while IFS= read -r f; do
        [[ -n "$f" ]] && echo "  - $f" >&2
    done
    msg_warn "请手动清理冲突文件后重试"
    exit 1
fi
msg_success "未检测到冲突副本"

msg_step "3: 半同步状态检测"
temp_output=$(test_temp_files "$BARE_REPO_PATH" 2>/dev/null) || true
if [[ -n "$temp_output" ]]; then
    temp_count=$(echo "$temp_output" | wc -l)
    msg_warn "检测到 $temp_count 个临时文件（网盘可能正在同步）："
    echo "$temp_output" | head -10 | while IFS= read -r f; do
        [[ -n "$f" ]] && echo "  - $(basename "$f")" >&2
    done
    if [[ $FORCE -eq 0 ]]; then
        read -r -p "临时文件可能表示同步未完成，是否继续？(y/N) " answer
        if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
            msg_warn "用户取消 pull"
            exit 0
        fi
    fi
else
    msg_success "未检测到临时文件"
fi

msg_step "4: 执行 git fetch"
fetch_output=$(git fetch "$REMOTE_NAME" 2>&1)
fetch_ret=$?
if [[ $fetch_ret -ne 0 ]]; then
    msg_error "git fetch 失败："
    echo "$fetch_output" >&2
    exit 1
fi
echo "$fetch_output" | grep -v '^$' || true
msg_success "Fetch 完成"

msg_step "5: 对比本地与远程差异"
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [[ -z "$current_branch" ]]; then
    msg_error "无法确定当前分支，detached HEAD 状态？"
    exit 1
fi
remote_branch="${REMOTE_NAME}/${current_branch}"

BEHIND_COUNT=0
AHEAD_COUNT=0

if behind_log=$(git log "HEAD..$remote_branch" --oneline 2>/dev/null); then
    BEHIND_COUNT=$(echo "$behind_log" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
fi
if ahead_log=$(git log "$remote_branch..HEAD" --oneline 2>/dev/null); then
    AHEAD_COUNT=$(echo "$ahead_log" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
fi

msg_info "当前分支: $current_branch"
msg_info "远程分支: $remote_branch"
msg_info "远程领先: $BEHIND_COUNT commits"
msg_info "本地领先: $AHEAD_COUNT commits"

PULLED_COUNT=0
FILES_CHANGED=0
PULL_STATUS="UPTODATE"
ERROR_MSG=""

if [[ $BEHIND_COUNT -gt 0 && $AHEAD_COUNT -gt 0 ]]; then
    msg_step "6: 非快进状态（双方都有新提交）"
    msg_error '========================================='
    msg_error '  错误：非快进更新（non-fast-forward）'
    msg_error '========================================='
    echo ""
    msg_error "远程有 $BEHIND_COUNT 个新提交，本地有 $AHEAD_COUNT 个新提交。"
    echo ""
    msg_header '处理方案：'
    msg_info '  推荐：git rebase（保持线性历史）'
    echo "    git fetch $REMOTE_NAME"
    echo "    git rebase $remote_branch"
    echo "    # 解决冲突后 git add <files>; git rebase --continue"
    echo "    # 然后执行 git-sync-push"
    echo ""
    msg_info '  备选：git merge（保留合并历史）'
    echo "    git fetch $REMOTE_NAME"
    echo "    git merge $remote_branch"
    echo "    # 解决冲突后 git commit"
    echo ""
    PULL_STATUS="NONFF"
    ERROR_MSG="non-fast-forward: behind=$BEHIND_COUNT,ahead=$AHEAD_COUNT"
elif [[ $BEHIND_COUNT -gt 0 ]]; then
    msg_step "6: 执行快进 pull ($BEHIND_COUNT commits)"
    local_head_before=$(git rev-parse HEAD 2>/dev/null)

    pull_output=$(git pull --ff-only "$REMOTE_NAME" 2>&1)
    pull_ret=$?
    if [[ $pull_ret -ne 0 ]]; then
        msg_error "git pull --ff-only 失败："
        echo "$pull_output" >&2
        PULL_STATUS="FAIL"
        ERROR_MSG="pull_failed"
    else
        echo "$pull_output"
        local_head_after=$(git rev-parse HEAD 2>/dev/null)

        if diff_stat=$(git diff --stat "$local_head_before" "$local_head_after" 2>/dev/null); then
            summary_line=$(echo "$diff_stat" | tail -1)
            if [[ "$summary_line" =~ ([0-9]+)\ files?\ changed ]]; then
                FILES_CHANGED=${BASH_REMATCH[1]}
            fi
        fi
        PULLED_COUNT=$BEHIND_COUNT
        PULL_STATUS="SUCCESS"
        msg_success "Pull 完成，更新了 $FILES_CHANGED 个文件"
    fi
elif [[ $AHEAD_COUNT -gt 0 ]]; then
    msg_step "6: 本地有领先提交"
    msg_warn "本地有 $AHEAD_COUNT 个提交尚未 push，建议先执行 git-sync-push 推送"
    PULL_STATUS="AHEAD"
else
    msg_step "6: 已是最新状态"
    msg_success "本地与远程同步，无需 pull"
    PULL_STATUS="UPTODATE"
fi

msg_step "7: 记录日志"
EXTRA_PARTS=()
if [[ "$PULL_STATUS" == "SUCCESS" ]]; then
    EXTRA_PARTS+=("commits=$PULLED_COUNT")
    EXTRA_PARTS+=("files_changed=$FILES_CHANGED")
    LOG_RESULT="SUCCESS"
elif [[ "$PULL_STATUS" == "NONFF" ]]; then
    EXTRA_PARTS+=("$ERROR_MSG")
    LOG_RESULT="FAILURE"
elif [[ "$PULL_STATUS" == "FAIL" ]]; then
    EXTRA_PARTS+=("$ERROR_MSG")
    LOG_RESULT="FAILURE"
else
    EXTRA_PARTS+=("behind=$BEHIND_COUNT,ahead=$AHEAD_COUNT")
    LOG_RESULT="SUCCESS"
fi
EXTRA_INFO=$(IFS=,; echo "${EXTRA_PARTS[*]}")
write_sync_log "$SYNC_ROOT" "PULL" "$REPO_NAME" "$LOG_RESULT" "$EXTRA_INFO"
msg_success "日志已写入"

echo ""
if [[ "$PULL_STATUS" == "SUCCESS" || "$PULL_STATUS" == "UPTODATE" || "$PULL_STATUS" == "AHEAD" ]]; then
    msg_success '========================================='
    msg_success '  Pull 完成！'
    msg_success '========================================='
else
    msg_error '========================================='
    msg_error '  Pull 需要手动干预'
    msg_error '========================================='
fi
echo ""
if [[ "$PULL_STATUS" == "NONFF" || "$PULL_STATUS" == "FAIL" ]]; then
    echo -e "${COLOR_ERROR}仓库: $REPO_NAME${COLOR_NC}"
    echo -e "${COLOR_ERROR}状态: $PULL_STATUS${COLOR_NC}"
else
    echo -e "${COLOR_SUCCESS}仓库: $REPO_NAME${COLOR_NC}"
    echo -e "${COLOR_SUCCESS}状态: $PULL_STATUS${COLOR_NC}"
fi
if [[ "$PULL_STATUS" == "SUCCESS" ]]; then
    echo -e "${COLOR_SUCCESS}拉取 commits: $PULLED_COUNT${COLOR_NC}"
    echo -e "${COLOR_SUCCESS}更新文件: $FILES_CHANGED${COLOR_NC}"
elif [[ "$PULL_STATUS" == "AHEAD" ]]; then
    echo -e "${COLOR_WARNING}本地领先: $AHEAD_COUNT commits（建议 push）${COLOR_NC}"
elif [[ "$PULL_STATUS" == "NONFF" ]]; then
    echo -e "${COLOR_ERROR}远程领先: $BEHIND_COUNT, 本地领先: $AHEAD_COUNT${COLOR_NC}"
fi
echo ""

if [[ "$PULL_STATUS" == "NONFF" || "$PULL_STATUS" == "FAIL" ]]; then
    exit 1
fi
