#!/usr/bin/env bash
# git-backup.sh - Git Bundle 备份工具 (Bash)

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
COLOR_PROMPT='\033[0;37m'
COLOR_NC='\033[0m'

REPO_PATH='.'
SYNC_ROOT=''
REMOTE_NAME=''
OUTPUT=''
VERIFY=1
NOTE=''
PRUNE=0
LIST=0

print_usage() {
    cat <<USAGE
用法: $(basename "$0") [选项] [仓库路径]

选项:
  -RepoPath <path>      本地工作仓库路径（默认.）
  -SyncRoot <path>      网盘根路径（可从git remote自动推断）
  -RemoteName <name>    remote名（默认baidu，可从git config读取）
  -Output <path>        自定义bundle输出路径（不指定则按backups/<repo>/<timestamp>.bundle规则）
  -Verify <0|1>         创建后验证bundle完整性（默认1=开启，0=关闭）
  -Note <备注>          备份备注（记录备份原因）
  -Prune <天数>         清理超过指定天数的旧备份（0=不清理，默认0）
  -List                 列出已有备份，不创建新备份
  -h, --help            显示此帮助
USAGE
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        -RepoPath) REPO_PATH="$2"; shift 2 ;;
        -SyncRoot) SYNC_ROOT="$2"; shift 2 ;;
        -RemoteName) REMOTE_NAME="$2"; shift 2 ;;
        -Output) OUTPUT="$2"; shift 2 ;;
        -Verify) VERIFY="$2"; shift 2 ;;
        -Note) NOTE="$2"; shift 2 ;;
        -Prune) PRUNE="$2"; shift 2 ;;
        -List) LIST=1; shift ;;
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

format_file_size() {
    local size_bytes="$1"
    if [ "$size_bytes" -ge 1073741824 ]; then
        echo "$(awk "BEGIN {printf \"%.2f GB\", $size_bytes/1073741824}")"
    elif [ "$size_bytes" -ge 1048576 ]; then
        echo "$(awk "BEGIN {printf \"%.2f MB\", $size_bytes/1048576}")"
    elif [ "$size_bytes" -ge 1024 ]; then
        echo "$(awk "BEGIN {printf \"%.2f KB\", $size_bytes/1024}")"
    else
        echo "$size_bytes bytes"
    fi
}

get_file_size() {
    local f="$1"
    if stat -c%s "$f" 2>/dev/null; then
        return 0
    elif stat -f%z "$f" 2>/dev/null; then
        return 0
    fi
    echo 0
}

get_file_mtime() {
    local f="$1"
    if stat -c%Y "$f" 2>/dev/null; then
        return 0
    elif stat -f%m "$f" 2>/dev/null; then
        return 0
    fi
    echo 0
}

get_bundle_stats() {
    local bundle_path="$1"
    local commit_count=0
    local tag_count=0
    local branch_count=0
    local size=0
    local verified=0

    if [ -f "$bundle_path" ]; then
        size=$(get_file_size "$bundle_path")
    fi

    if git bundle verify "$bundle_path" >/dev/null 2>&1; then
        verified=1
    fi

    local heads
    heads=$(git bundle list-heads "$bundle_path" 2>/dev/null || true)
    if [ -n "$heads" ]; then
        branch_count=$(echo "$heads" | grep -c 'refs/heads/' || true)
        tag_count=$(echo "$heads" | grep -c 'refs/tags/' || true)
    fi

    local temp_clone_dir
    temp_clone_dir="${TMPDIR:-/tmp}/git-bundle-stats-$$-$RANDOM"
    if git clone --bare --quiet "$bundle_path" "$temp_clone_dir" 2>/dev/null; then
        local count
        count=$(git -C "$temp_clone_dir" rev-list --all --count 2>/dev/null || echo 0)
        commit_count="$count"
        rm -rf "$temp_clone_dir"
    fi

    echo "$commit_count|$tag_count|$branch_count|$size|$verified"
}

show_backup_list() {
    local backup_dir="$1"

    if [ ! -d "$backup_dir" ]; then
        msg_warn "备份目录不存在: $backup_dir"
        return
    fi

    local bundles
    bundles=$(find "$backup_dir" -maxdepth 1 -name '*.bundle' -type f -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null || true)

    if [ -z "$bundles" ]; then
        msg_info "备份目录中没有 bundle 文件"
        return
    fi

    echo ""
    msg_header "=== 备份列表: $backup_dir ==="
    echo ""
    printf '%-4s %-25s %-10s %-16s %-8s %s\n' '#' '文件名' '大小' '创建时间' '验证' '备注'
    echo "------------------------------------------------------------------------------------------"

    local idx=1
    local b
    while IFS= read -r b; do
        [ -z "$b" ] && continue
        [ ! -f "$b" ] && continue
        local bname
        bname=$(basename "$b")
        local bsize bmtime
        bsize=$(get_file_size "$b")
        bsize_str=$(format_file_size "$bsize")
        bmtime=$(date -r "$b" '+%Y-%m-%d %H:%M' 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M" "$b" 2>/dev/null || echo "unknown")

        local note_file="${b%.bundle}.note"
        local note_content=""
        if [ -f "$note_file" ]; then
            note_content=$(head -1 "$note_file" 2>/dev/null | cut -f2- || true)
            note_content=$(echo "$note_content" | sed 's/^[[:space:]]*//' | cut -c1-25)
        fi

        local verify_str verify_color
        if git bundle verify "$b" >/dev/null 2>&1; then
            verify_str="通过"
            verify_color="$COLOR_SUCCESS"
        else
            verify_str="失败"
            verify_color="$COLOR_ERROR"
        fi

        printf '%-4s %-25s %-10s %-16s' "$idx" "$bname" "$bsize_str" "$bmtime"
        echo -ne " ${verify_color}${verify_str}${COLOR_NC} "
        echo "$note_content"

        idx=$((idx + 1))
    done <<< "$bundles"

    echo ""
    local count
    count=$(echo "$bundles" | grep -c '.' || true)
    msg_info "共 $count 个备份文件"
}

echo ""
msg_header "========================================="
msg_header "  Git Bundle 备份工具"
msg_header "========================================="
echo ""

REPO_PATH=$(resolve_fullpath "$REPO_PATH")

is_git_repo=0
if git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    result=$(git -C "$REPO_PATH" rev-parse --is-inside-work-tree 2>/dev/null || echo "false")
    if [ "$result" = "true" ]; then
        is_git_repo=1
    fi
fi
if [ "$is_git_repo" -ne 1 ]; then
    msg_error "不是有效的 Git 工作仓库: $REPO_PATH"
    exit 1
fi
msg_info "本地仓库: $REPO_PATH"

cd "$REPO_PATH"

if [ -z "$REMOTE_NAME" ]; then
    REMOTE_NAME=$(git config baidu-sync.remote 2>/dev/null || echo "")
    if [ -z "$REMOTE_NAME" ]; then
        REMOTE_NAME="baidu"
    fi
fi

remote_url=""
if remote_get_url=$(git remote get-url "$REMOTE_NAME" 2>/dev/null); then
    remote_url=$(echo "$remote_get_url" | head -1)
fi

if [ -z "$SYNC_ROOT" ]; then
    if [ -n "$remote_url" ] && [ -d "$remote_url" ]; then
        bare_git_dir="$remote_url"
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

repo_name=$(get_repo_name "$REPO_PATH" "$remote_url")
backup_dir="${SYNC_ROOT}/backups/${repo_name}"

lockfile_path="${SYNC_ROOT}/locks/${repo_name}.lock.json"
if [ -f "$lockfile_path" ]; then
    msg_warn "警告: 仓库 $repo_name 当前有锁持有，备份操作是只读的但可能遇到不一致状态"
    holder_op="$(_lock_read_json_field "$lockfile_path" "operation")"
    holder_host="$(_lock_read_json_field "$lockfile_path" "hostname")"
    holder_ts="$(_lock_read_json_field "$lockfile_path" "acquired_at")"
    msg_warn "  持有者: $holder_host (op=$holder_op, since=$holder_ts)"
    echo ""
fi

msg_info "SyncRoot: $SYNC_ROOT"
msg_info "仓库名: $repo_name"
msg_info "Remote: $REMOTE_NAME -> $remote_url"
msg_info "备份目录: $backup_dir"
echo ""

if [ "$LIST" -eq 1 ]; then
    show_backup_list "$backup_dir"
    exit 0
fi

if [ "$PRUNE" -gt 0 ]; then
    msg_step "1" "清理超过 $PRUNE 天的旧备份"
    if [ ! -d "$backup_dir" ]; then
        msg_info "备份目录不存在，无需清理"
    else
        cutoff_epoch=$(date -d "-$PRUNE days" +%s 2>/dev/null || date -v-"${PRUNE}"d +%s 2>/dev/null || echo "")
        if [ -z "$cutoff_epoch" ]; then
            msg_warn "无法计算截止日期，跳过清理"
        else
            old_bundles=()
            while IFS= read -r -d '' f; do
                bname=$(basename "$f")
                if [[ "$bname" == *"永久"* ]] || [[ "$bname" == *"keep"* ]] || [[ "$bname" == *"monthly"* ]]; then
                    continue
                fi
                fmtime=$(get_file_mtime "$f")
                if [ "$fmtime" -lt "$cutoff_epoch" ]; then
                    old_bundles+=("$f")
                fi
            done < <(find "$backup_dir" -maxdepth 1 -name '*.bundle' -type f -print0 2>/dev/null)

            if [ ${#old_bundles[@]} -eq 0 ]; then
                msg_info "没有超过 $PRUNE 天的旧备份需要清理"
            else
                echo ""
                msg_warn "以下 ${#old_bundles[@]} 个备份文件将被删除（超过 $PRUNE 天）："
                for b in "${old_bundles[@]}"; do
                    bsize=$(get_file_size "$b")
                    bsize_str=$(format_file_size "$bsize")
                    bdate=$(date -r "$b" '+%Y-%m-%d' 2>/dev/null || echo "unknown")
                    echo "  - $(basename "$b") ($bsize_str, 创建于 $bdate)"
                done
                echo ""
                echo -ne "${COLOR_PROMPT}确认删除？(输入 YES 继续，其他输入取消): ${COLOR_NC}"
                read -r confirm
                if [ "$confirm" = "YES" ]; then
                    for b in "${old_bundles[@]}"; do
                        note_file="${b%.bundle}.note"
                        rm -f "$b"
                        [ -f "$note_file" ] && rm -f "$note_file"
                    done
                    msg_success "已删除 ${#old_bundles[@]} 个旧备份文件"
                else
                    msg_info "用户取消，不执行删除"
                fi
            fi
        fi
    fi
    echo ""
fi

msg_step "2" "确定备份输出路径"
timestamp=$(date '+%Y%m%d-%H%M%S')
if [ -n "$OUTPUT" ]; then
    bundle_path="$OUTPUT"
    bundle_dir=$(dirname "$bundle_path")
    if [ -n "$bundle_dir" ] && [ ! -d "$bundle_dir" ]; then
        mkdir -p "$bundle_dir"
    fi
else
    mkdir -p "$backup_dir"
    bundle_path="${backup_dir}/${timestamp}.bundle"
fi
msg_info "Bundle 输出路径: $bundle_path"

msg_step "3" "执行 git bundle create --all"
if [ -f "$bundle_path" ]; then
    msg_warn "文件已存在，将覆盖: $bundle_path"
fi
if ! git bundle create "$bundle_path" --all; then
    msg_error "Bundle 创建失败"
    [ -f "$bundle_path" ] && rm -f "$bundle_path"
    exit 1
fi
msg_success "Bundle 创建完成"

if [ "$VERIFY" -eq 1 ]; then
    msg_step "4" "验证 Bundle 完整性"
    if git bundle verify "$bundle_path"; then
        msg_success "Bundle 验证通过"
    else
        msg_error "Bundle 验证失败"
        exit 1
    fi
else
    msg_warn "已跳过验证（-Verify 0）"
fi

msg_step "5" "统计备份信息"
stats=$(get_bundle_stats "$bundle_path")
IFS='|' read -r commit_count tag_count branch_count size verified <<< "$stats"
size_str=$(format_file_size "$size")
msg_info "备份大小: $size_str"
msg_info "提交数: $commit_count"
msg_info "分支数: $branch_count"
msg_info "标签数: $tag_count"
if [ "$verified" -eq 1 ]; then
    msg_success "验证状态: 通过"
else
    msg_error "验证状态: 未通过"
fi

if [ -n "$NOTE" ]; then
    msg_step "6" "写入备份备注"
    note_path="${bundle_path%.bundle}.note"
    note_time=$(date '+%Y-%m-%d %H:%M:%S')
    printf '%s\t%s\n' "$note_time" "$NOTE" > "$note_path"
    msg_success "备注已写入: $note_path"
    msg_info "备注内容: $NOTE"
fi

echo ""
msg_success "========================================="
msg_success "  备份完成！"
msg_success "========================================="
echo ""
msg_success "Bundle: $bundle_path"
msg_success "大小: $size_str"
msg_success "Commits: $commit_count"
msg_success "Tags: $tag_count"
if [ -n "$NOTE" ]; then
    msg_success "备注: $NOTE"
fi
echo ""
