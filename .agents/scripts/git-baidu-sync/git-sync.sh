#!/usr/bin/env bash
# git-sync.sh - Git 网盘同步 一体化 Sync 工具 (Bash)

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PULL_SCRIPT="$SCRIPT_DIR/git-sync-pull.sh"
PUSH_SCRIPT="$SCRIPT_DIR/git-sync-push.sh"

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
FORCE=0
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
  -NoWait               push后不等待同步完成
  -NoBackup             不自动创建bundle备份
  -Force                pull时忽略锁警告
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
        -Force) FORCE=1; shift ;;
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
msg_step()    { echo -e "${COLOR_STEP}$*${COLOR_NC}"; }
msg_header()  { echo -e "${COLOR_HEADER}$*${COLOR_NC}"; }

resolve_fullpath() {
    local p="$1"
    if [[ "$p" = /* ]]; then
        echo "$p"
    else
        echo "$(cd "$p" 2>/dev/null && pwd || echo "$(pwd)/$p")"
    fi
}

echo ""
msg_header '========================================='
msg_header '  Git 网盘同步 - 一体化 Sync 工具'
msg_header '========================================='
echo ""

REPO_PATH=$(resolve_fullpath "$REPO_PATH")

if ! git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    msg_error "不是有效的 Git 工作仓库: $REPO_PATH"
    exit 1
fi

PULL_ARGS=(-RepoPath "$REPO_PATH")
if [[ -n "$SYNC_ROOT" ]]; then
    PULL_ARGS+=(-SyncRoot "$SYNC_ROOT")
fi
if [[ -n "$REMOTE_NAME" ]]; then
    PULL_ARGS+=(-RemoteName "$REMOTE_NAME")
fi
if [[ $FORCE -eq 1 ]]; then
    PULL_ARGS+=(-Force)
fi

SYNC_ROOT_RESOLVED=""
REMOTE_NAME_RESOLVED=""
REMOTE_URL=""

cd "$REPO_PATH"

if [[ -z "$REMOTE_NAME" ]]; then
    REMOTE_NAME=$(git config baidu-sync.remote 2>/dev/null || true)
    if [[ -z "$REMOTE_NAME" ]]; then
        REMOTE_NAME="baidu"
    fi
fi
REMOTE_NAME_RESOLVED="$REMOTE_NAME"

if remote_url_output=$(git remote get-url "$REMOTE_NAME" 2>/dev/null); then
    REMOTE_URL=$(echo "$remote_url_output" | head -1)
fi

if [[ -z "$SYNC_ROOT" ]]; then
    if [[ -n "$REMOTE_URL" && -d "$REMOTE_URL" ]]; then
        bare_git_dir="$REMOTE_URL"
        SYNC_ROOT=$(dirname "$(dirname "$bare_git_dir")")
    fi
fi
if [[ -n "$SYNC_ROOT" ]]; then
    SYNC_ROOT_RESOLVED=$(resolve_fullpath "$SYNC_ROOT")
fi

if [[ -z "$SYNC_ROOT_RESOLVED" ]]; then
    msg_error "无法自动推断 SyncRoot，请使用 -SyncRoot 参数指定"
    exit 1
fi

msg_info "本地仓库: $REPO_PATH"
msg_info "SyncRoot: $SYNC_ROOT_RESOLVED"
msg_info "Remote: $REMOTE_NAME_RESOLVED"
echo ""

REPO_NAME=$(basename "$REPO_PATH")
if [[ -n "$REMOTE_URL" ]]; then
    basename_url=$(basename "$REMOTE_URL" .git)
    if [[ -n "$basename_url" && "$basename_url" != "/" ]]; then
        REPO_NAME="$basename_url"
    fi
fi

SYNC_ERRORS=()
PULL_STATUS="UNKNOWN"
PULL_EXIT_CODE=0
PUSH_STATUS="SKIPPED"
PUSH_EXIT_CODE=0

msg_step ">>> 阶段 1/2: 执行 Pull"
echo ""
set +e
"$PULL_SCRIPT" "${PULL_ARGS[@]}"
PULL_EXIT_CODE=$?
set -e

if [[ $PULL_EXIT_CODE -eq 0 ]]; then
    PULL_STATUS="SUCCESS"
else
    PULL_STATUS="FAILED(exit=$PULL_EXIT_CODE)"
fi

current_branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
remote_branch="${REMOTE_NAME_RESOLVED}/${current_branch}"

BEHIND_COUNT=0
AHEAD_COUNT=0
if [[ -n "$current_branch" ]]; then
    if behind_log=$(git log "HEAD..$remote_branch" --oneline 2>/dev/null); then
        BEHIND_COUNT=$(echo "$behind_log" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
    fi
    if ahead_log=$(git log "$remote_branch..HEAD" --oneline 2>/dev/null); then
        AHEAD_COUNT=$(echo "$ahead_log" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
    fi
fi

PUSH_NEEDED=0
if [[ $AHEAD_COUNT -gt 0 && $PULL_EXIT_CODE -eq 0 ]]; then
    echo ""
    msg_info "检测到 $AHEAD_COUNT 个本地提交待推送"
    PUSH_NEEDED=1
elif [[ $AHEAD_COUNT -gt 0 && $PULL_EXIT_CODE -ne 0 ]]; then
    echo ""
    msg_warn "Pull 失败，跳过 Push（请先解决 pull 问题）"
    PUSH_STATUS="SKIPPED (pull failed)"
fi

if [[ $PUSH_NEEDED -eq 1 ]]; then
    echo ""
    msg_step ">>> 阶段 2/2: 执行 Push"
    echo ""

    PUSH_ARGS=(-RepoPath "$REPO_PATH" -SyncRoot "$SYNC_ROOT_RESOLVED" -RemoteName "$REMOTE_NAME_RESOLVED")
    if [[ $NO_WAIT -eq 1 ]]; then
        PUSH_ARGS+=(-NoWait)
    fi
    if [[ $NO_BACKUP -eq 1 ]]; then
        PUSH_ARGS+=(-NoBackup)
    fi
    PUSH_ARGS+=(-Timeout "$TIMEOUT" -PollInterval "$POLL_INTERVAL" -StableCount "$STABLE_COUNT")

    set +e
    "$PUSH_SCRIPT" "${PUSH_ARGS[@]}"
    PUSH_EXIT_CODE=$?
    set -e

    if [[ $PUSH_EXIT_CODE -eq 0 ]]; then
        PUSH_STATUS="SUCCESS"
    else
        PUSH_STATUS="FAILED(exit=$PUSH_EXIT_CODE)"
    fi
else
    echo ""
    msg_step ">>> 阶段 2/2: 无需 Push"
fi

FINAL_AHEAD=0
FINAL_BEHIND=0
if current_branch2=$(git rev-parse --abbrev-ref HEAD 2>/dev/null); then
    remote_branch2="${REMOTE_NAME_RESOLVED}/${current_branch2}"
    if ahead_log2=$(git log "$remote_branch2..HEAD" --oneline 2>/dev/null); then
        FINAL_AHEAD=$(echo "$ahead_log2" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
    fi
    if behind_log2=$(git log "HEAD..$remote_branch2" --oneline 2>/dev/null); then
        FINAL_BEHIND=$(echo "$behind_log2" | grep -c '^[a-f0-9]' 2>/dev/null || echo 0)
    fi
fi
FINAL_LOCAL_HEAD=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
FINAL_REMOTE_HEAD="N/A"
if [[ -n "$current_branch2" ]]; then
    FINAL_REMOTE_HEAD=$(git rev-parse --short "$remote_branch2" 2>/dev/null || echo "N/A")
fi

echo ""
msg_header '========================================='
msg_header '  同步摘要'
msg_header '========================================='
echo ""
msg_info "仓库:      $REPO_NAME"
msg_info "本地 HEAD: $FINAL_LOCAL_HEAD"
msg_info "远程 HEAD: $FINAL_REMOTE_HEAD"
echo ""
if [[ "$PULL_STATUS" == "SUCCESS" ]]; then
    echo -e "Pull:      ${COLOR_SUCCESS}${PULL_STATUS}${COLOR_NC}"
else
    echo -e "Pull:      ${COLOR_ERROR}${PULL_STATUS}${COLOR_NC}"
fi
if [[ "$PUSH_STATUS" == "SUCCESS" || "$PUSH_STATUS" == "SKIPPED" || "$PUSH_STATUS" == SKIPPED* ]]; then
    if [[ "$PUSH_STATUS" == "SUCCESS" ]]; then
        echo -e "Push:      ${COLOR_SUCCESS}${PUSH_STATUS}${COLOR_NC}"
    else
        echo -e "Push:      ${COLOR_INFO}${PUSH_STATUS}${COLOR_NC}"
    fi
else
    echo -e "Push:      ${COLOR_ERROR}${PUSH_STATUS}${COLOR_NC}"
fi
echo ""
msg_info "领先: $FINAL_AHEAD commits | 落后: $FINAL_BEHIND commits"
echo ""

HAS_ERRORS=0
if [[ $PULL_EXIT_CODE -ne 0 || $PUSH_EXIT_CODE -ne 0 ]]; then
    HAS_ERRORS=1
fi

if [[ $HAS_ERRORS -eq 1 ]]; then
    msg_error '同步过程中遇到问题：'
    [[ $PULL_EXIT_CODE -ne 0 ]] && echo -e "  ${COLOR_ERROR}- Pull 失败 (exit code: $PULL_EXIT_CODE)${COLOR_NC}"
    [[ $PUSH_EXIT_CODE -ne 0 ]] && echo -e "  ${COLOR_ERROR}- Push 失败 (exit code: $PUSH_EXIT_CODE)${COLOR_NC}"
    echo ""
    msg_header '下一步建议：'
    msg_info '1. 检查错误信息，解决冲突或网络问题'
    msg_info '2. 非快进情况参考 05-daily-sync-workflow.md 第7节处理'
    msg_info '3. 修复后重新执行 git-sync'
    echo ""
    exit 1
fi

if [[ $FINAL_BEHIND -gt 0 || $FINAL_AHEAD -gt 0 ]]; then
    [[ $FINAL_BEHIND -gt 0 ]] && msg_warn "注意：远程仍领先 $FINAL_BEHIND 个提交（pull可能未完成）"
    [[ $FINAL_AHEAD -gt 0 ]] && msg_warn "注意：本地仍领先 $FINAL_AHEAD 个提交（push可能未完成）"
    echo ""
else
    msg_success '同步完成！本地与远程完全一致。'
    echo ""
fi
