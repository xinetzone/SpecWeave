#!/usr/bin/env bash
# git-sync-push.sh - Git 网盘同步 Push 工具 (Bash)

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
NO_WAIT=0
NO_BACKUP=0
TIMEOUT=600
POLL_INTERVAL=2
STABLE_COUNT=5

print_usage() {
    cat <<USAGE
用法: $(basename "$0") [选项] [仓库路径]

选项:
  -RepoPath <path>      本地工作仓库路径（默认.）
  -SyncRoot <path>      网盘根路径（必填，或从git config推断）
  -RemoteName <name>    remote名（默认baidu，可从git config读取）
  -NoWait               push后不等待同步完成（高级用户）
  -NoBackup             不自动创建bundle备份
  -Timeout <seconds>    等待超时（默认600秒）
  -PollInterval <sec>   轮询间隔（默认2秒）
  -StableCount <n>      稳定次数阈值（默认5次）
  -h, --help            显示此帮助
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -RepoPath) REPO_PATH="$2"; shift 2 ;;
        -SyncRoot) SYNC_ROOT="$2"; shift 2 ;;
        -RemoteName) REMOTE_NAME="$2"; shift 2 ;;
        -NoWait) NO_WAIT=1; shift ;;
        -NoBackup) NO_BACKUP=1; shift ;;
        -Timeout) TIMEOUT="$2"; shift 2 ;;
        -PollInterval) POLL_INTERVAL="$2"; shift 2 ;;
        -StableCount) STABLE_COUNT="$2"; shift 2 ;;
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

get_bare_repo_stats() {
    local bare_repo="$1"
    if [[ ! -d "$bare_repo" ]]; then
        return 1
    fi
    local total_size=0
    local file_count=0
    local latest_mtime=0
    local pack_count=0
    local f mtime
    while IFS= read -r -d '' f; do
        file_count=$((file_count + 1))
        local sz
        sz=$(stat -c%s "$f" 2>/dev/null || stat -f%z "$f" 2>/dev/null || echo 0)
        total_size=$((total_size + sz))
        mtime=$(stat -c%Y "$f" 2>/dev/null || stat -f%m "$f" 2>/dev/null || echo 0)
        if [[ $mtime -gt $latest_mtime ]]; then
            latest_mtime=$mtime
        fi
        local dir
        dir="$(dirname "$f")"
        local bname
        bname="$(basename "$f")"
        if [[ "$(basename "$dir")" == "pack" && "$(basename "$(dirname "$dir")")" == "objects" && "${bname##*.}" == "pack" ]]; then
            pack_count=$((pack_count + 1))
        fi
    done < <(find "$bare_repo" -type f -print0 2>/dev/null)
    echo "$total_size|$file_count|$latest_mtime|$pack_count"
}

wait_for_sync() {
    local bare_repo="$1"
    local timeout_sec="$2"
    local poll_sec="$3"
    local stable_times="$4"

    msg_info "等待网盘同步完成（超时 ${timeout_sec}s，轮询 ${poll_sec}s，稳定 ${stable_times}次）..."

    local start_ts
    start_ts=$(date +%s)
    local stable_hits=0
    local last_size=0 last_files=0 last_mtime=0 last_packs=-1
    local spinner=('|' '/' '-' '\')
    local spinner_idx=0
    local wait_status="success"
    local wait_secs=0

    while true; do
        local now_ts
        now_ts=$(date +%s)
        local elapsed=$((now_ts - start_ts))
        wait_secs=$elapsed
        if [[ $elapsed -ge $timeout_sec ]]; then
            echo ""
            msg_warn "等待超时（${timeout_sec}s），push 已成功但网盘可能未完全同步"
            msg_warn "请手动确认网盘同步状态后再在其他设备操作"
            wait_status="timeout"
            echo "$wait_status|$wait_secs"
            return 0
        fi

        local temp_list
        if temp_list=$(test_temp_files "$bare_repo"); then
            stable_hits=0
            local first_temp
            first_temp=$(echo "$temp_list" | head -1)
            printf "\r[%s] 等待中... 已等待 %ds, 检测到临时文件: %s   " "${spinner[$spinner_idx]}" "$elapsed" "$(basename "$first_temp")"
        else
            local stats
            if stats=$(get_bare_repo_stats "$bare_repo"); then
                local cur_size cur_files cur_mtime cur_packs
                IFS='|' read -r cur_size cur_files cur_mtime cur_packs <<< "$stats"
                local stats_str="size=$cur_size, files=$cur_files, packs=$cur_packs"
                if [[ $last_packs -ge 0 ]] && \
                   [[ $cur_size -eq $last_size ]] && \
                   [[ $cur_files -eq $last_files ]] && \
                   [[ $cur_packs -eq $last_packs ]] && \
                   [[ $((cur_mtime - last_mtime)) -lt $poll_sec ]] && \
                   [[ $((last_mtime - cur_mtime)) -lt $poll_sec ]]; then
                    stable_hits=$((stable_hits + 1))
                    printf "\r[%s] 等待中... 已等待 %ds, 稳定 %d/%d 次 (%s)   " "${spinner[$spinner_idx]}" "$elapsed" "$stable_hits" "$stable_times" "$stats_str"
                    if [[ $stable_hits -ge $stable_times ]]; then
                        echo ""
                        msg_success "网盘同步已稳定（连续 ${stable_times} 次检测一致）"
                        echo "$wait_status|$wait_secs"
                        return 0
                    fi
                else
                    stable_hits=0
                    printf "\r[%s] 等待中... 已等待 %ds, 同步中 (%s)   " "${spinner[$spinner_idx]}" "$elapsed" "$stats_str"
                fi
                last_size=$cur_size
                last_files=$cur_files
                last_mtime=$cur_mtime
                last_packs=$cur_packs
            else
                stable_hits=0
                printf "\r[%s] 等待中... 已等待 %ds, 裸仓库未就绪   " "${spinner[$spinner_idx]}" "$elapsed"
            fi
        fi

        spinner_idx=$(((spinner_idx + 1) % 4))
        sleep "$poll_sec"
    done
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
msg_header '  Git 网盘同步 - Push 工具'
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
BACKUP_DIR="${SYNC_ROOT}/backups/${REPO_NAME}"

msg_info "SyncRoot: $SYNC_ROOT"
msg_info "仓库名: $REPO_NAME"
msg_info "裸仓库: $BARE_REPO_PATH"
msg_info "Remote: $REMOTE_NAME -> $REMOTE_URL"
echo ""

msg_step "1: 检查工作区状态"
status_output=$(git status --porcelain 2>&1) || {
    msg_error "git status 执行失败"
    echo "$status_output" >&2
    exit 1
}
if [[ -n "$(echo "$status_output" | grep -c '[^[:space:]]' 2>/dev/null || echo 0)" ]] && [[ -n "$status_output" ]]; then
    msg_error "工作区不干净，请先提交或 stash 所有更改："
    echo "$status_output" | while IFS= read -r line; do
        [[ -n "$line" ]] && echo "  $line" >&2
    done
    exit 1
fi
msg_success "工作区干净"

msg_step "2: 检查本地未推送提交"
AHEAD_COUNT=0
current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
if [[ -n "$current_branch" ]]; then
    if upstream=$(git rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null); then
        log_output=$(git log '@{u}..HEAD' --oneline 2>/dev/null || true)
        AHEAD_COUNT=$(echo "$log_output" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
    else
        remote_branch="${REMOTE_NAME}/${current_branch}"
        log_output=$(git log "$remote_branch..HEAD" --oneline 2>/dev/null || true)
        AHEAD_COUNT=$(echo "$log_output" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
    fi
fi

if [[ $AHEAD_COUNT -eq 0 ]]; then
    msg_info "本地没有未推送的提交，无需 push"
    exit 0
fi
msg_info "本地有 $AHEAD_COUNT 个提交待推送"

msg_step "3: 冲突副本检测"
if [[ ! -d "$BARE_REPO_PATH" ]]; then
    msg_error "裸仓库不存在: $BARE_REPO_PATH"
    msg_warn "请先使用 register-repo.sh 注册仓库"
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

msg_step "4: 获取写锁"
if ! lock_acquire "$REPO_NAME" "push"; then
    msg_error "获取锁失败，push 中止"
    exit 1
fi
LOCK_ACQUIRED=1

cleanup() {
    if [[ $LOCK_ACQUIRED -eq 1 ]]; then
        lock_release "$REPO_NAME" >/dev/null 2>&1 || true
    fi
}
trap cleanup EXIT

msg_step "5: 检查网盘裸仓库临时文件"
temp_output=$(test_temp_files "$BARE_REPO_PATH" 2>/dev/null) || true
if [[ -n "$temp_output" ]]; then
    temp_count=$(echo "$temp_output" | wc -l)
    msg_error "检测到 $temp_count 个临时文件（网盘可能正在同步）："
    echo "$temp_output" | head -10 | while IFS= read -r f; do
        [[ -n "$f" ]] && echo "  - $(basename "$f")" >&2
    done
    msg_warn "请等待网盘同步完成后重试"
    exit 1
fi
msg_success "未检测到临时文件"

msg_step "6: 推送所有分支"
push_all_output=$(git push "$REMOTE_NAME" --all 2>&1)
push_all_ret=$?
if [[ $push_all_ret -ne 0 ]]; then
    msg_error "分支推送失败："
    echo "$push_all_output" >&2
    exit 1
fi
echo "$push_all_output"
msg_success "分支推送完成"

msg_step "7: 推送所有标签"
push_tags_output=$(git push "$REMOTE_NAME" --tags 2>&1)
push_tags_ret=$?
if [[ $push_tags_ret -ne 0 ]]; then
    msg_warn "标签推送失败："
    echo "$push_tags_output"
else
    echo "$push_tags_output"
    msg_success "标签推送完成"
fi

BUNDLE_PATH=""
if [[ $NO_BACKUP -eq 0 ]]; then
    msg_step "8: 创建 bundle 备份"
    mkdir -p "$BACKUP_DIR"
    timestamp=$(date +%Y%m%d-%H%M%S)
    BUNDLE_PATH="${BACKUP_DIR}/${timestamp}.bundle"

    msg_info "创建 bundle: $BUNDLE_PATH"
    bundle_output=$(git bundle create "$BUNDLE_PATH" --all 2>&1)
    bundle_ret=$?
    if [[ $bundle_ret -eq 0 ]]; then
        verify_output=$(git bundle verify "$BUNDLE_PATH" 2>&1)
        verify_ret=$?
        if [[ $verify_ret -eq 0 ]]; then
            msg_success "Bundle 验证通过"
        else
            msg_warn "Bundle 验证警告："
            echo "$verify_output"
        fi
    else
        msg_warn "Bundle 创建失败："
        echo "$bundle_output"
        BUNDLE_PATH=""
    fi
else
    msg_warn "已跳过备份（-NoBackup）"
fi

WAIT_RESULT=""
WAIT_STATUS="success"
WAIT_SECS=0
if [[ $NO_WAIT -eq 0 ]]; then
    msg_step "9: 等待网盘同步"
    wait_output=$(wait_for_sync "$BARE_REPO_PATH" "$TIMEOUT" "$POLL_INTERVAL" "$STABLE_COUNT")
    IFS='|' read -r WAIT_STATUS WAIT_SECS <<< "$wait_output"
else
    msg_warn "已跳过等待（-NoWait）"
    WAIT_STATUS="success"
    WAIT_SECS=0
fi

msg_step "10: 记录日志"
EXTRA_PARTS=("commits=$AHEAD_COUNT")
EXTRA_PARTS+=("wait=${WAIT_SECS}s")
if [[ "$WAIT_STATUS" == "timeout" ]]; then
    EXTRA_PARTS+=("timeout=true")
fi
if [[ -n "$BUNDLE_PATH" ]]; then
    EXTRA_PARTS+=("backup=$(basename "$BUNDLE_PATH")")
fi
EXTRA_INFO=$(IFS=,; echo "${EXTRA_PARTS[*]}")
LOG_RESULT="SUCCESS"
if [[ "$WAIT_STATUS" == "timeout" ]]; then
    LOG_RESULT="WARNING"
fi
write_sync_log "$SYNC_ROOT" "PUSH" "$REPO_NAME" "$LOG_RESULT" "$EXTRA_INFO"
msg_success "日志已写入"

echo ""
msg_header '========================================='
msg_header '  Push 完成！'
msg_header '========================================='
echo ""
echo -e "${COLOR_SUCCESS}仓库: $REPO_NAME${COLOR_NC}"
echo -e "${COLOR_SUCCESS}推送 commits: $AHEAD_COUNT${COLOR_NC}"
echo -e "${COLOR_SUCCESS}同步等待: ${WAIT_SECS}s${COLOR_NC}"
if [[ -n "$BUNDLE_PATH" ]]; then
    if [[ -f "$BUNDLE_PATH" ]]; then
        bundle_size=$(stat -c%s "$BUNDLE_PATH" 2>/dev/null || stat -f%z "$BUNDLE_PATH" 2>/dev/null || echo 0)
        bundle_size_mb=$(echo "scale=2; $bundle_size / 1048576" | bc 2>/dev/null || echo "?")
        echo -e "${COLOR_SUCCESS}备份: $BUNDLE_PATH (${bundle_size_mb} MB)${COLOR_NC}"
    else
        echo -e "${COLOR_SUCCESS}备份: $BUNDLE_PATH${COLOR_NC}"
    fi
fi
if [[ "$WAIT_STATUS" == "timeout" ]]; then
    echo ""
    msg_warn "注意：等待超时，请确认网盘同步状态后再在其他设备操作"
fi
echo ""
