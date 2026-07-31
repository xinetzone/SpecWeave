#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCK_UTILS="${SCRIPT_DIR}/lock-utils.sh"

if [ ! -f "$LOCK_UTILS" ]; then
    echo "[ERROR] 找不到锁函数库: $LOCK_UTILS" >&2
    exit 2
fi

source "$LOCK_UTILS"

usage() {
    cat <<'EOF'
用法: force-unlock.sh -RepoName <repo> -SyncRoot <path> [-Force]

强制释放指定仓库的锁（危险操作）。

参数:
  -RepoName <repo>    仓库名称（必填）
  -SyncRoot <path>    同步空间根目录（必填）
  -Force              跳过交互确认（危险）
  -h, --help          显示此帮助

环境变量:
  GIT_SYNC_LOCK_TIMEOUT    锁超时分钟数（默认30）

示例:
  force-unlock.sh -RepoName my-project -SyncRoot ~/BaiduSync/git-sync
  force-unlock.sh -RepoName my-project -SyncRoot ~/BaiduSync/git-sync -Force
EOF
}

REPO_NAME=""
SYNC_ROOT=""
ASSUME_YES=""

while [ $# -gt 0 ]; do
    case "$1" in
        -RepoName)
            REPO_NAME="$2"
            shift 2
            ;;
        -SyncRoot)
            SYNC_ROOT="$2"
            shift 2
            ;;
        -Force)
            ASSUME_YES="--yes"
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            echo "[ERROR] 未知参数: $1" >&2
            usage
            exit 2
            ;;
    esac
done

if [ -z "$REPO_NAME" ]; then
    echo "[ERROR] 必须指定 -RepoName 参数" >&2
    echo "" >&2
    usage
    exit 2
fi

if [ -z "$SYNC_ROOT" ]; then
    if [ -n "${GIT_SYNC_ROOT:-}" ]; then
        SYNC_ROOT="$GIT_SYNC_ROOT"
        echo "[INFO] 使用环境变量 GIT_SYNC_ROOT=$SYNC_ROOT"
    else
        echo "[ERROR] 必须指定 -SyncRoot 参数或设置 GIT_SYNC_ROOT 环境变量" >&2
        echo "" >&2
        usage
        exit 2
    fi
fi

if ! lock_init "$SYNC_ROOT"; then
    echo "[ERROR] 锁系统初始化失败" >&2
    exit 2
fi

echo ""
echo "=== 当前锁状态 ==="
lock_check "$REPO_NAME" || true
echo ""

if lock_force_release "$REPO_NAME" "$ASSUME_YES"; then
    echo ""
    echo "[SUCCESS] 强制解锁完成: $REPO_NAME"
    exit 0
else
    echo ""
    echo "[CANCELLED/FAILED] 强制解锁未执行或失败"
    exit 1
fi
