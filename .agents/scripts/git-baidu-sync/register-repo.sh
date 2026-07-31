#!/usr/bin/env bash
set -euo pipefail

REPO_PATH='.'
SYNC_ROOT=''
REPO_NAME=''
REMOTE_NAME='baidu'
SKIP_GC=0
AGGRESSIVE_GC=0
FORCE=0

COLOR_SUCCESS='\033[0;32m'
COLOR_STEP='\033[0;36m'
COLOR_WARNING='\033[0;33m'
COLOR_ERROR='\033[0;31m'
COLOR_INFO='\033[0;37m'
COLOR_HEADER='\033[0;35m'
COLOR_PROMPT='\033[0;37m'
COLOR_RESET='\033[0m'

print_msg() {
    local msg="$1"
    local color="$2"
    local prefix="${3:-}"
    if [ -n "$prefix" ]; then
        echo -e "${color}[${prefix}] ${msg}${COLOR_RESET}"
    else
        echo -e "${color}${msg}${COLOR_RESET}"
    fi
}

print_step() {
    local num="$1"
    local title="$2"
    echo ""
    print_msg "=== 步骤 ${num}: ${title} ===" "$COLOR_HEADER"
}

show_help() {
    echo "用法: $0 [选项] -SyncRoot <网盘同步根路径>"
    echo ""
    echo "选项:"
    echo "  -RepoPath <路径>     本地工作仓库路径（默认当前目录）"
    echo "  -SyncRoot <路径>     网盘同步根目录（必需）"
    echo "  -RepoName <名称>     仓库名称（默认取目录名）"
    echo "  -RemoteName <名称>   Remote 名称（默认 baidu）"
    echo "  -SkipGC              跳过 GC 步骤"
    echo "  -AggressiveGC        使用 aggressive GC（首次初始化推荐）"
    echo "  -Force               强制覆盖已存在的裸仓库"
    echo "  -h, --help           显示此帮助"
    echo ""
    echo "示例:"
    echo "  $0 -SyncRoot ~/BaiduSync/git-sync"
    echo "  $0 -RepoPath ~/projects/myapp -SyncRoot ~/BaiduSync/git-sync -AggressiveGC"
}

while [ $# -gt 0 ]; do
    case "$1" in
        -RepoPath)
            if [ $# -lt 2 ]; then echo "错误: -RepoPath 需要参数" >&2; exit 1; fi
            REPO_PATH="$2"; shift 2 ;;
        -RepoPath=*)
            REPO_PATH="${1#-RepoPath=}"; shift ;;
        -SyncRoot)
            if [ $# -lt 2 ]; then echo "错误: -SyncRoot 需要参数" >&2; exit 1; fi
            SYNC_ROOT="$2"; shift 2 ;;
        -SyncRoot=*)
            SYNC_ROOT="${1#-SyncRoot=}"; shift ;;
        -RepoName)
            if [ $# -lt 2 ]; then echo "错误: -RepoName 需要参数" >&2; exit 1; fi
            REPO_NAME="$2"; shift 2 ;;
        -RepoName=*)
            REPO_NAME="${1#-RepoName=}"; shift ;;
        -RemoteName)
            if [ $# -lt 2 ]; then echo "错误: -RemoteName 需要参数" >&2; exit 1; fi
            REMOTE_NAME="$2"; shift 2 ;;
        -RemoteName=*)
            REMOTE_NAME="${1#-RemoteName=}"; shift ;;
        -SkipGC|--skip-gc)
            SKIP_GC=1; shift ;;
        -AggressiveGC|--aggressive-gc)
            AGGRESSIVE_GC=1; shift ;;
        -Force|--force)
            FORCE=1; shift ;;
        -h|--help)
            show_help; exit 0 ;;
        *)
            echo "未知参数: $1" >&2; show_help; exit 1 ;;
    esac
done

if [ -z "$SYNC_ROOT" ]; then
    echo "错误: 必须指定 -SyncRoot 参数" >&2
    show_help
    exit 1
fi

resolve_path() {
    local p="$1"
    if [ -d "$p" ]; then
        (cd "$p" && pwd)
    elif [ -d "$(dirname "$p")" ]; then
        echo "$(cd "$(dirname "$p")" && pwd)/$(basename "$p")"
    else
        echo "$p"
    fi
}

REPO_PATH=$(resolve_path "$REPO_PATH")
SYNC_ROOT=$(resolve_path "$SYNC_ROOT")

if [ -z "$REPO_NAME" ]; then
    REPO_NAME=$(basename "$REPO_PATH")
fi

BARE_REPO="${SYNC_ROOT}/repos/${REPO_NAME}.git"
BACKUP_DIR="${SYNC_ROOT}/backups/${REPO_NAME}"

echo ""
print_msg '=========================================' "$COLOR_HEADER"
print_msg '  百度网盘 Git 仓库注册工具（首台设备）' "$COLOR_HEADER"
print_msg '=========================================' "$COLOR_HEADER"
echo ""
print_msg "本地仓库路径: $REPO_PATH" "$COLOR_INFO"
print_msg "网盘同步根目录: $SYNC_ROOT" "$COLOR_INFO"
print_msg "仓库名称: $REPO_NAME" "$COLOR_INFO"
print_msg "裸仓库路径: $BARE_REPO" "$COLOR_INFO"
print_msg "Remote 名称: $REMOTE_NAME" "$COLOR_INFO"
echo ""

print_step 0 '前置检查'

for dir in "repos" "backups" "meta"; do
    if [ ! -d "${SYNC_ROOT}/${dir}" ]; then
        print_msg "目录不存在: ${SYNC_ROOT}/${dir}" "$COLOR_ERROR" 'ERR'
        print_msg '请先执行 init-sync-dir.sh 初始化同步目录' "$COLOR_WARNING" 'HINT'
        exit 1
    fi
done
print_msg '同步目录结构验证通过' "$COLOR_SUCCESS" 'OK'

if ! git -C "$REPO_PATH" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    print_msg "不是有效的 Git 工作仓库: $REPO_PATH" "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg '本地 Git 仓库验证通过' "$COLOR_SUCCESS" 'OK'

if ! git --version >/dev/null 2>&1; then
    print_msg '未检测到 Git，请先安装 Git' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg "Git 版本: $(git --version)" "$COLOR_INFO" 'OK'

if [ -d "$BARE_REPO" ]; then
    if [ "$FORCE" -eq 1 ]; then
        print_msg "裸仓库已存在，-Force 已指定，将覆盖: $BARE_REPO" "$COLOR_WARNING" 'WARN'
        rm -rf "$BARE_REPO"
    else
        print_msg "裸仓库已存在: $BARE_REPO" "$COLOR_WARNING" 'WARN'
        read -r -p '是否删除并重新创建？(y/N) ' ans
        if [ "$ans" = 'y' ] || [ "$ans" = 'Y' ]; then
            rm -rf "$BARE_REPO"
            print_msg '已删除旧裸仓库' "$COLOR_SUCCESS" 'DEL'
        else
            print_msg '用户取消操作' "$COLOR_WARNING" 'ABORT'
            exit 0
        fi
    fi
fi

print_step 1 '本地仓库健康检查 (git fsck --full --strict)'

fsck_output=$(git -C "$REPO_PATH" fsck --full --strict 2>&1) || {
    print_msg 'git fsck 执行失败：' "$COLOR_ERROR" 'ERR'
    echo "$fsck_output"
    exit 1
}

has_errors=0
while IFS= read -r line; do
    if echo "$line" | grep -qE '^error:|^fatal:|missing blob|missing tree|missing commit'; then
        has_errors=1
        echo -e "${COLOR_ERROR}${line}${COLOR_RESET}"
    fi
done <<< "$fsck_output"

if [ "$has_errors" -eq 1 ]; then
    print_msg '本地仓库存在错误，请修复后重试' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg '本地仓库健康检查通过' "$COLOR_SUCCESS" 'OK'

if [ "$SKIP_GC" -eq 0 ]; then
    print_step 2 '本地 GC 优化'

    gc_args=('gc')
    if [ "$AGGRESSIVE_GC" -eq 1 ]; then
        print_msg '使用 --aggressive 模式（首次初始化推荐，耗时较长）' "$COLOR_INFO"
        gc_args+=('--aggressive' '--prune=now')
    else
        print_msg '使用常规 GC 模式（使用 -AggressiveGC 启用深度优化）' "$COLOR_INFO"
    fi

    print_msg '执行 GC，请稍候...' "$COLOR_INFO"
    if gc_output=$(git -C "$REPO_PATH" "${gc_args[@]}" 2>&1); then
        echo "$gc_output" | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done
        print_msg 'GC 完成' "$COLOR_SUCCESS" 'OK'
    else
        print_msg 'GC 过程出现警告（非致命错误，继续）：' "$COLOR_WARNING" 'WARN'
        echo "$gc_output" | while IFS= read -r line; do echo -e "${COLOR_WARNING}${line}${COLOR_RESET}"; done
    fi
else
    print_step 2 '本地 GC 优化（已跳过 -SkipGC）'
    print_msg 'GC 已跳过' "$COLOR_WARNING" 'SKIP'
fi

print_step 3 '创建裸仓库到网盘 (git clone --no-local --bare)'

print_msg "目标: $BARE_REPO" "$COLOR_INFO"
if clone_output=$(git -C "$REPO_PATH" clone --no-local --bare . "$BARE_REPO" 2>&1); then
    echo "$clone_output" | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done
    print_msg '裸仓库创建成功' "$COLOR_SUCCESS" 'OK'
else
    print_msg '裸仓库创建失败：' "$COLOR_ERROR" 'ERR'
    echo "$clone_output"
    exit 1
fi

bare_check=$(git -C "$BARE_REPO" rev-parse --is-bare-repository 2>/dev/null || echo 'false')
if [ "$bare_check" != 'true' ]; then
    print_msg '错误：创建的仓库不是裸仓库' "$COLOR_ERROR" 'ERR'
    exit 1
fi
print_msg '裸仓库验证通过' "$COLOR_SUCCESS" 'OK'

print_step 4 '裸仓库跨平台安全配置'

git -C "$BARE_REPO" config --local core.filemode false
print_msg 'core.filemode = false (忽略 Unix 权限位)' "$COLOR_SUCCESS" 'SET'

git -C "$BARE_REPO" config --local core.symlinks false
print_msg 'core.symlinks = false (不创建符号链接)' "$COLOR_SUCCESS" 'SET'

git -C "$BARE_REPO" config --local core.ignorecase true
print_msg 'core.ignorecase = true (大小写不敏感)' "$COLOR_SUCCESS" 'SET'

git -C "$BARE_REPO" config --local gc.auto 6700
print_msg 'gc.auto = 6700 (自动 GC 阈值)' "$COLOR_SUCCESS" 'SET'

git -C "$BARE_REPO" config --local gc.autopacklimit 1
print_msg 'gc.autopacklimit = 1 (保持最少 pack 文件)' "$COLOR_SUCCESS" 'SET'

git -C "$BARE_REPO" config --local core.preloadindex true
print_msg 'core.preloadindex = true (并行预加载索引)' "$COLOR_SUCCESS" 'SET'

if bare_fsck=$(git -C "$BARE_REPO" fsck --full 2>&1); then
    print_msg '裸仓库健康检查通过' "$COLOR_SUCCESS" 'OK'
else
    print_msg '裸仓库健康检查发现问题：' "$COLOR_WARNING" 'WARN'
    echo "$bare_fsck" | while IFS= read -r line; do echo -e "${COLOR_WARNING}${line}${COLOR_RESET}"; done
fi

print_step 5 '为本地仓库添加 remote'

existing_remotes=()
while IFS= read -r r; do
    [ -n "$r" ] && existing_remotes+=("$r")
done < <(git -C "$REPO_PATH" remote 2>/dev/null || true)

remote_exists=0
for r in "${existing_remotes[@]}"; do
    if [ "$r" = "$REMOTE_NAME" ]; then
        remote_exists=1
        break
    fi
done

if [ "$remote_exists" -eq 1 ]; then
    if [ "$FORCE" -eq 1 ]; then
        print_msg "Remote '$REMOTE_NAME' 已存在，-Force 已指定，将更新URL" "$COLOR_WARNING" 'WARN'
        git -C "$REPO_PATH" remote set-url "$REMOTE_NAME" "$BARE_REPO"
    else
        print_msg "Remote '$REMOTE_NAME' 已存在" "$COLOR_WARNING" 'WARN'
        read -r -p '是否更新URL？(y/N) ' ans
        if [ "$ans" = 'y' ] || [ "$ans" = 'Y' ]; then
            git -C "$REPO_PATH" remote set-url "$REMOTE_NAME" "$BARE_REPO"
        else
            print_msg '跳过 remote 添加' "$COLOR_WARNING" 'SKIP'
        fi
    fi
else
    git -C "$REPO_PATH" remote add "$REMOTE_NAME" "$BARE_REPO"
    print_msg "已添加 remote '$REMOTE_NAME' -> $BARE_REPO" "$COLOR_SUCCESS" 'ADD'
fi

echo ""
print_msg '当前 remote 列表：' "$COLOR_INFO"
git -C "$REPO_PATH" remote -v | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done

print_step 6 '推送所有分支和标签'

print_msg "推送所有分支到 $REMOTE_NAME ..." "$COLOR_INFO"
if push_branches=$(git -C "$REPO_PATH" push "$REMOTE_NAME" --all 2>&1); then
    echo "$push_branches" | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done
    print_msg '分支推送完成' "$COLOR_SUCCESS" 'OK'
else
    print_msg '分支推送失败：' "$COLOR_ERROR" 'ERR'
    echo "$push_branches"
    exit 1
fi

echo ""
print_msg "推送所有标签到 $REMOTE_NAME ..." "$COLOR_INFO"
if push_tags=$(git -C "$REPO_PATH" push "$REMOTE_NAME" --tags 2>&1); then
    echo "$push_tags" | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done
    print_msg '标签推送完成' "$COLOR_SUCCESS" 'OK'
else
    print_msg '标签推送失败：' "$COLOR_ERROR" 'ERR'
    echo "$push_tags"
    exit 1
fi

print_step 7 '等待网盘同步'

print_msg '================================================' "$COLOR_WARNING"
print_msg '  重要：请等待百度网盘完成文件同步！' "$COLOR_WARNING"
print_msg '  检查：' "$COLOR_WARNING"
print_msg '  1. 百度网盘客户端显示同步完成（无上传中文件）' "$COLOR_WARNING"
print_msg '  2. 裸仓库目录大小连续1分钟无变化' "$COLOR_WARNING"
print_msg '  3. 目录中无 .tmp/.lock/downloading 等临时文件' "$COLOR_WARNING"
print_msg '================================================' "$COLOR_WARNING"
echo ""

temp_count=$(find "$BARE_REPO" -name '*.tmp' -o -name '*.lock' -o -name '*downloading*' -o -name '*.part' -o -name '*.temp' 2>/dev/null | wc -l)
if [ "$temp_count" -gt 0 ]; then
    print_msg '检测到临时文件（网盘可能正在同步）：' "$COLOR_WARNING" 'WARN'
    find "$BARE_REPO" -name '*.tmp' -o -name '*.lock' -o -name '*downloading*' -o -name '*.part' -o -name '*.temp' 2>/dev/null | head -5 | while IFS= read -r f; do
        echo "  - $(basename "$f")"
    done
else
    print_msg '未检测到临时文件' "$COLOR_INFO" 'INFO'
fi

echo ""
read -r -p '确认网盘同步完成后，按回车键继续创建备份...'

print_step 8 '创建初始 bundle 备份'

mkdir -p "$BACKUP_DIR"
if [ ! -d "$BACKUP_DIR" ]; then
    print_msg "创建备份目录失败: $BACKUP_DIR" "$COLOR_ERROR" 'ERR'
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
BUNDLE_PATH="${BACKUP_DIR}/${TIMESTAMP}.bundle"

print_msg "创建 bundle: $BUNDLE_PATH" "$COLOR_INFO"
if bundle_output=$(git -C "$BARE_REPO" bundle create "$BUNDLE_PATH" --all 2>&1); then
    echo "$bundle_output" | while IFS= read -r line; do echo -e "${COLOR_INFO}${line}${COLOR_RESET}"; done

    if verify_output=$(git -C "$BARE_REPO" bundle verify "$BUNDLE_PATH" 2>&1); then
        print_msg 'Bundle 验证通过' "$COLOR_SUCCESS" 'OK'
    else
        print_msg 'Bundle 验证警告：' "$COLOR_WARNING" 'WARN'
        echo "$verify_output" | while IFS= read -r line; do echo -e "${COLOR_WARNING}${line}${COLOR_RESET}"; done
    fi
else
    print_msg 'Bundle 创建失败：' "$COLOR_ERROR" 'ERR'
    echo "$bundle_output"
    exit 1
fi

bundle_size=$(du -h "$BUNDLE_PATH" | cut -f1)
print_msg "Bundle 大小: $bundle_size" "$COLOR_INFO" 'INFO'

echo ""
print_msg '=========================================' "$COLOR_SUCCESS"
print_msg '  仓库注册完成！' "$COLOR_SUCCESS"
print_msg '=========================================' "$COLOR_SUCCESS"
echo ""
print_msg "仓库名: $REPO_NAME" "$COLOR_SUCCESS"
print_msg "裸仓库: $BARE_REPO" "$COLOR_SUCCESS"
print_msg "Remote: $REMOTE_NAME" "$COLOR_SUCCESS"
print_msg "备份: $BUNDLE_PATH" "$COLOR_SUCCESS"
echo ""
print_msg '后续步骤：' "$COLOR_HEADER"
print_msg '1. 等待网盘完全同步后再在其他设备操作' "$COLOR_INFO"
print_msg "2. 新设备使用 clone-repo.sh -RepoName $REPO_NAME -SyncRoot <sync-root> 克隆" "$COLOR_INFO"
print_msg "3. 日常推送使用: git push $REMOTE_NAME" "$COLOR_INFO"
echo ""
