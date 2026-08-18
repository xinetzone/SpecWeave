#!/usr/bin/env bash
# =============================================================================
# cleanup.sh — 统一清理模块（激进清理减小镜像体积，基于 safe_cleanup 安全原语）
#
# 提供分层清理函数：pycache → conda/pip cache → apt → tmp → binaries → all
# 安全保证：基于 safe_cleanup.sh 的 T∩D=∅ 隔离原则，自动防止备份自毁类 bug
#
# 依赖：logging.sh（variant_log_* 函数）、safe_cleanup.sh（安全清理原语）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_CLEANUP_LOADED:-}" ]] && return 0
_VARIANT_CLEANUP_LOADED=1

# 计时器目录（必须排除，不能被清理删除）
_VARIANT_TIMER_DIR="/root/.variant-timers"

# 确保 safe_cleanup 已加载（框架已按依赖顺序加载，此处为独立source时的兜底）
if [[ -z "${_SAFE_CLEANUP_LOADED:-}" ]]; then
    _CLEANUP_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck source=./safe_cleanup.sh
    source "${_CLEANUP_LIB_DIR}/safe_cleanup.sh"
fi

# ---------------------------------------------------------------------------
# cleanup_pycache: 删除Python缓存文件
# ---------------------------------------------------------------------------
cleanup_pycache() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] Python __pycache__ and .pyc files    │"
    echo "└─────────────────────────────────────────────────┘"

    find /opt/conda -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find /opt/conda -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
    # 清理用户目录下的缓存
    if id -u devuser >/dev/null 2>&1; then
        find /home/devuser -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find /home/devuser -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
    fi

    variant_log_ok "Python cache removed"
}

# ---------------------------------------------------------------------------
# cleanup_conda_pip_cache: 清理conda和pip缓存
# ---------------------------------------------------------------------------
cleanup_conda_pip_cache() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] conda and pip cache                   │"
    echo "└─────────────────────────────────────────────────┘"

    conda clean -yafq 2>/dev/null || true
    pip cache purge 2>/dev/null || true

    variant_log_ok "conda + pip cache cleaned"
}

# ---------------------------------------------------------------------------
# cleanup_apt: 清理APT缓存（使用 safe_cleanup_dir 安全清理 lists 目录）
# ---------------------------------------------------------------------------
cleanup_apt() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] APT cache                             │"
    echo "└─────────────────────────────────────────────────┘"

    apt-get clean -y 2>/dev/null || true
    # 使用 safe_cleanup_dir 替代 rm -rf /var/lib/apt/lists/* —— 根目录护栏+隐藏文件自动清理
    safe_cleanup_dir /var/lib/apt/lists

    variant_log_ok "APT cache cleaned"
}

# ---------------------------------------------------------------------------
# cleanup_tmp: 安全清理临时目录
#
# 安全策略：
#   1. _VARIANT_TIMER_DIR=/root/.variant-timers 天然在 /tmp、/var/tmp 之外
#   2. 启动时断言：验证计时器目录不在清理目标内（防御未来路径变更）
#   3. 使用 safe_cleanup_dir 白名单清理，无需 mv-aside（零备份自毁风险）
# ---------------------------------------------------------------------------
cleanup_tmp() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] /tmp and /var/tmp (safe mode)         │"
    echo "│ NOTE: ${_VARIANT_TIMER_DIR} EXCLUDED (timer data)  │"
    echo "└─────────────────────────────────────────────────┘"

    # 防御性断言：计时器目录必须在 /tmp 和 /var/tmp 之外（T∩D=∅不变量）
    # 如果未来有人把 _VARIANT_TIMER_DIR 改到 /tmp 下，这里会立刻报错阻止清理
    local _assert_failed=0
    for _tmp_target in /tmp /var/tmp; do
        if safe_is_subpath "${_VARIANT_TIMER_DIR}" "${_tmp_target}"; then
            echo "[CLEANUP][ERROR] Timer dir INSIDE cleanup target! This violates T∩D=∅ invariant." >&2
            echo "[CLEANUP][ERROR]   timer: ${_VARIANT_TIMER_DIR}" >&2
            echo "[CLEANUP][ERROR]   target: ${_tmp_target}" >&2
            echo "[CLEANUP][ERROR]   Use safe_cleanup_move_aside() or move timer dir outside /tmp." >&2
            _assert_failed=1
        fi
    done

    if [[ $_assert_failed -eq 1 ]]; then
        echo "[CLEANUP][WARN] Aborting tmp cleanup due to safety violation. Timer data must be preserved." >&2
        return 1
    fi

    # 计时器目录在 /root/，天然隔离——直接安全清理 /tmp 和 /var/tmp
    # safe_cleanup_dir 自动处理隐藏文件、根目录护栏、非阻塞容错
    safe_cleanup_dir /tmp
    safe_cleanup_dir /var/tmp

    variant_log_ok "tmp directories cleaned (timer dir preserved via safe_cleanup)"
}

# ---------------------------------------------------------------------------
# cleanup_binaries: 激进二进制清理（strip + 删除静态库）
# 注意：保留libgcc和libstdc++（clang链接需要）
# ---------------------------------------------------------------------------
cleanup_binaries() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] Binary strip + static libs removal   │"
    echo "│ NOTE: libgcc*/libstdc++* PRESERVED (linker needs)│"
    echo "└─────────────────────────────────────────────────┘"

    # Strip可执行文件
    echo "[ACTION] Stripping binaries in conda env bin dirs..."
    find /opt/conda/envs/main/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
    find /opt/conda/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
    echo "[OK] Binary stripping complete"
    echo ""

    # 删除静态库，但保留GCC运行时库
    echo "[ACTION] Removing static libraries (.a) - preserving libgcc*/libstdc++..."
    find /opt/conda/envs/main/lib -name "*.a" ! -name "libgcc*" ! -name "libstdc++*" -delete 2>/dev/null || true
    find /opt/conda/lib -name "*.a" ! -name "libgcc*" ! -name "libstdc++*" -delete 2>/dev/null || true
    echo "[OK] Static libraries removed"
}

# ---------------------------------------------------------------------------
# cleanup_all: 一键执行完整清理（pycache + conda/pip + apt + tmp，不含binaries）
# 注意：默认不包含cleanup_binaries，因为strip可能破坏调试符号，需要时显式调用
# ---------------------------------------------------------------------------
cleanup_all() {
    variant_stage_header "Post-Install Cleanup"
    cleanup_pycache
    cleanup_conda_pip_cache
    cleanup_apt
    cleanup_tmp
    variant_log_ok "All standard cleanup completed"
}

# ---------------------------------------------------------------------------
# cleanup_all_aggressive: 激进清理（所有清理 + binaries strip）
# ---------------------------------------------------------------------------
cleanup_all_aggressive() {
    variant_stage_header "Aggressive Post-Install Cleanup"
    cleanup_pycache
    cleanup_binaries
    cleanup_conda_pip_cache
    cleanup_apt
    cleanup_tmp
    variant_log_ok "All aggressive cleanup completed"
}
