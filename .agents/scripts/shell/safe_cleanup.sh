#!/usr/bin/env bash
# =============================================================================
# lib/safe_cleanup.sh — 安全清理函数库（基于 destruction-protection-isolation 模式）
#
# 核心不变量：备份/保护数据必须位于删除作用域目录树之外（T ∩ D = ∅）
#
# 用法 (在脚本开头 source):
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   source "${SCRIPT_DIR}/safe_cleanup.sh"
#
# 公共 API:
#   safe_cleanup_dir <target_dir> [preserve_path ...]
#       优先方案：find 白名单原地删除，不移动文件，零备份风险
#
#   safe_cleanup_move_aside <target_dir> <backup_parent_dir> [preserve_path ...]
#       兜底方案：移开保护文件→清理→恢复，自动验证备份位置在删除域外
#
#   safe_assert_isolated <backup_path> <target_dir>
#       防御性断言：验证 backup_path 不在 target_dir 目录树内
#       违反时输出错误并返回 1（非fatal，调用方决定是否退出）
#
#   safe_is_subpath <child> <parent>
#       判断 child 是否在 parent 目录树内（解析 symlink 后），返回 0/1
#
#   safe_mktemp_outside <target_dir> <prefix>
#       在 target_dir 之外创建临时文件/目录（默认 /tmp 或 mktemp 默认位置）
#       用法: tmpfile=$(safe_mktemp_outside "/path/to/clean" "myapp-")
#
# 设计原则：
#   1. 所有清理操作非阻塞：失败时输出 WARN 但不退出（配合 set -e 安全）
#   2. 默认 find 白名单优先于 mv-aside/restore（无备份即无自毁风险）
#   3. 所有路径操作先 realpath 解析 symlink，防止 bind mount/symlink 绕过检查
#   4. 隐藏文件（.*）也会被清理，不需要额外加 /target/.* 参数
# =============================================================================

# 防止重复 source
[[ -n "${_SAFE_CLEANUP_LOADED:-}" ]] && return 0
_SAFE_CLEANUP_LOADED=1

# ---------------------------------------------------------------------------
# 内部工具函数
# ---------------------------------------------------------------------------

# 获取真实路径（兼容无 realpath 的系统，用 readlink -f 兜底）
_safe_realpath() {
    local p="$1"
    if command -v realpath >/dev/null 2>&1; then
        realpath "$p" 2>/dev/null || echo "$p"
    elif command -v readlink >/dev/null 2>&1; then
        readlink -f "$p" 2>/dev/null || echo "$p"
    else
        # 最简兜底：cd + pwd
        if [ -d "$p" ]; then
            (cd "$p" && pwd) 2>/dev/null || echo "$p"
        else
            echo "$p"
        fi
    fi
}

# 规范化路径末尾（去掉尾部 /，确保 /tmp ≠ /tmp/ 比较一致）
_safe_normpath() {
    local p="$1"
    # 去掉尾部斜杠（除非是根目录 /）
    while [ "${p: -1}" = "/" ] && [ "$p" != "/" ]; do
        p="${p%/}"
    done
    echo "$p"
}

# ---------------------------------------------------------------------------
# 公共 API
# ---------------------------------------------------------------------------

# 判断 child 是否在 parent 目录树内（返回 0=是，1=否）
# 解析 symlink 后比较真实路径，防止符号链接绕过检查
safe_is_subpath() {
    local child parent child_real parent_real
    child="$(_safe_normpath "$(_safe_realpath "$1")")"
    parent="$(_safe_normpath "$(_safe_realpath "$2")")"

    # 根目录包含一切
    [ "$parent" = "/" ] && return 0

    # child 本身就是 parent
    [ "$child" = "$parent" ] && return 0

    # child 以 parent/ 开头
    case "$child/" in
        "$parent/"*) return 0 ;;
    esac

    return 1
}

# 断言 backup_path 不在 target_dir 目录树内
# 违反时输出 WARN 到 stderr，返回 1（不 fatal exit，调用方决定）
safe_assert_isolated() {
    local backup_path="$1"
    local target_dir="$2"

    if safe_is_subpath "$backup_path" "$target_dir"; then
        local b_real t_real
        b_real="$(_safe_realpath "$backup_path")"
        t_real="$(_safe_realpath "$target_dir")"
        echo "[SAFE_CLEANUP][ERROR] Backup path INSIDE cleanup target! This violates T∩D=∅ invariant." >&2
        echo "[SAFE_CLEANUP][ERROR]   backup: $backup_path -> $b_real" >&2
        echo "[SAFE_CLEANUP][ERROR]   target: $target_dir -> $t_real" >&2
        echo "[SAFE_CLEANUP][ERROR]   Move backup OUTSIDE the cleanup directory before proceeding." >&2
        return 1
    fi
    return 0
}

# 在 target_dir 之外创建安全临时文件
# 用法: my_tmp=$(safe_mktemp_outside "/tmp" "myapp-")
#       或: my_tmpdir=$(safe_mktemp_outside "/tmp" "myapp-" -d)
safe_mktemp_outside() {
    local target_dir="$1"
    local prefix="$2"
    local extra_args="${3:-}"

    # 优先使用 /root（容器环境）或 $HOME 作为临时目录（确保不在 target_dir 内）
    local tmp_base=""
    for candidate in "${SAFE_TMPDIR:-}" /root "$HOME" /var/tmp /tmp; do
        if [ -n "$candidate" ] && [ -d "$candidate" ] && [ -w "$candidate" ]; then
            if ! safe_is_subpath "$candidate" "$target_dir"; then
                tmp_base="$candidate"
                break
            fi
        fi
    done

    if [ -z "$tmp_base" ]; then
        echo "[SAFE_CLEANUP][ERROR] Cannot find temp directory outside target: $target_dir" >&2
        return 1
    fi

    mktemp ${extra_args} "${tmp_base}/${prefix}XXXXXX" 2>/dev/null
}

# ---------------------------------------------------------------------------
# 方案A（优先）：find 白名单原地删除
# 不需要 mv-aside/restore，零备份自毁风险
# ---------------------------------------------------------------------------
safe_cleanup_dir() {
    local target_dir="$1"
    shift

    if [ ! -d "$target_dir" ]; then
        echo "[SAFE_CLEANUP][WARN] Target directory does not exist: $target_dir" >&2
        return 0
    fi

    local t_real
    t_real="$(_safe_realpath "$target_dir")"

    # 禁止清理根目录（安全护栏）
    if [ "$t_real" = "/" ] || [ "$t_real" = "" ]; then
        echo "[SAFE_CLEANUP][ERROR] Refusing to clean root directory: $target_dir" >&2
        return 1
    fi

    # 构建 find 的排除参数
    local find_prune_args=()
    local preserve_path p_real p_base
    if [ $# -gt 0 ]; then
        for preserve_path in "$@"; do
            if [ -e "$preserve_path" ]; then
                p_real="$(_safe_realpath "$preserve_path")"
                p_base="$(basename "$p_real")"
                # 只排除 target_dir 直接子节点（-maxdepth 1 下的名称匹配）
                find_prune_args+=( -name "$p_base" -prune -o )
            else
                # 路径不存在，尝试 basename 匹配（可能还没创建）
                p_base="$(basename "$preserve_path")"
                find_prune_args+=( -name "$p_base" -prune -o )
            fi
        done
    fi

    # 执行清理：先清理非隐藏文件+目录，再清理隐藏文件（避免 . 和 ..）
    # -mindepth 1 防止删除 target_dir 本身
    # -maxdepth 1 只清理直接子项（非递归，递归用其他方法）
    if [ ${#find_prune_args[@]} -eq 0 ]; then
        # 无保留项：清理所有直接子项（包括隐藏文件）
        find "$t_real" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true
    else
        # 有保留项：prune 排除后删除
        find "$t_real" -mindepth 1 -maxdepth 1 \
            "${find_prune_args[@]}" \
            -exec rm -rf {} + 2>/dev/null || true
    fi

    return 0
}

# ---------------------------------------------------------------------------
# 方案B（兜底）：移开→清理→恢复
# 当保护数据必须保留在清理后的目录中（如状态文件、计时器），无法用简单排除时使用
# 自动验证备份位置在删除域外（T ∩ D = ∅ 断言）
# ---------------------------------------------------------------------------
safe_cleanup_move_aside() {
    local target_dir="$1"
    local backup_parent_dir="$2"
    shift 2

    if [ ! -d "$target_dir" ]; then
        echo "[SAFE_CLEANUP][WARN] Target directory does not exist: $target_dir" >&2
        return 0
    fi

    local t_real bp_real
    t_real="$(_safe_realpath "$target_dir")"
    bp_real="$(_safe_realpath "$backup_parent_dir")"

    # 安全护栏：禁止清理根目录
    if [ "$t_real" = "/" ] || [ "$t_real" = "" ]; then
        echo "[SAFE_CLEANUP][ERROR] Refusing to clean root directory: $target_dir" >&2
        return 1
    fi

    # 关键断言：backup_parent_dir 必须在 target_dir 之外（T ∩ D = ∅）
    if ! safe_assert_isolated "$bp_real" "$t_real"; then
        echo "[SAFE_CLEANUP][HINT] Try using /root, \$HOME, or /var/backups as backup parent." >&2
        return 1
    fi

    # 创建备份父目录（如果不存在）
    mkdir -p "$bp_real" 2>/dev/null || true

    # 记录备份映射（原路径→备份路径），用于恢复
    local -a _backup_pairs=()
    local preserve_path p_real p_base backup_path
    local restore_failed=0

    # Phase 1: 移开保护文件/目录
    if [ $# -gt 0 ]; then
        for preserve_path in "$@"; do
            if [ -e "$preserve_path" ]; then
                p_real="$(_safe_realpath "$preserve_path")"
                p_base="$(basename "$p_real")"
                backup_path="${bp_real}/.safe-cleanup-backup-${p_base}-$$"

                # 双重检查：单个备份路径也不在 target_dir 内
                if ! safe_assert_isolated "$backup_path" "$t_real"; then
                    echo "[SAFE_CLEANUP][ERROR] Aborting: backup path for '$p_base' is inside target" >&2
                    # 回滚已移开的文件
                    _safe_cleanup_restore "${_backup_pairs[@]}"
                    return 1
                fi

                if mv "$p_real" "$backup_path" 2>/dev/null; then
                    _backup_pairs+=( "$backup_path" "$p_real" )
                else
                    echo "[SAFE_CLEANUP][WARN] Failed to move aside: $preserve_path" >&2
                fi
            fi
        done
    fi

    # Phase 2: 清理目标目录所有内容（包括隐藏文件）
    find "$t_real" -mindepth 1 -maxdepth 1 -exec rm -rf {} + 2>/dev/null || true

    # Phase 3: 恢复保护文件/目录
    if [ ${#_backup_pairs[@]} -gt 0 ]; then
        restore_failed=0
        _safe_cleanup_restore "${_backup_pairs[@]}" || restore_failed=$?
    fi

    if [ $restore_failed -ne 0 ]; then
        echo "[SAFE_CLEANUP][WARN] Some items failed to restore (check above)" >&2
        return 1
    fi

    return 0
}

# 内部函数：从备份恢复（供 safe_cleanup_move_aside 使用）
_safe_cleanup_restore() {
    local failed=0
    local src dst
    # 参数是成对的: src1 dst1 src2 dst2 ...
    while [ $# -ge 2 ]; do
        src="$1"
        dst="$2"
        shift 2

        if [ -e "$src" ]; then
            # 确保目标父目录存在
            mkdir -p "$(dirname "$dst")" 2>/dev/null || true
            if mv "$src" "$dst" 2>/dev/null; then
                : # 恢复成功
            else
                echo "[SAFE_CLEANUP][WARN] Failed to restore: $src -> $dst" >&2
                failed=1
            fi
        else
            echo "[SAFE_CLEANUP][WARN] Backup missing, cannot restore: $src" >&2
            failed=1
        fi
    done
    return $failed
}
