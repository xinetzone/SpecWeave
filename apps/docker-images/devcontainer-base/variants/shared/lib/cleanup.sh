#!/usr/bin/env bash
# =============================================================================
# cleanup.sh — 统一清理模块（激进清理减小镜像体积，安全排除计时器目录）
#
# 提供分层清理函数：pycache → conda/pip cache → apt → tmp → binaries → all
# 关键安全保证：cleanup_tmp 显式排除 /root/.variant-timers/ 计时器目录
#
# 依赖：logging.sh（variant_log_* 函数）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_CLEANUP_LOADED:-}" ]] && return 0
_VARIANT_CLEANUP_LOADED=1

# 计时器目录（必须排除，不能被清理删除）
_VARIANT_TIMER_DIR="/root/.variant-timers"

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
# cleanup_apt: 清理APT缓存
# ---------------------------------------------------------------------------
cleanup_apt() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] APT cache                             │"
    echo "└─────────────────────────────────────────────────┘"

    apt-get clean -y 2>/dev/null || true
    rm -rf /var/lib/apt/lists/* 2>/dev/null || true

    variant_log_ok "APT cache cleaned"
}

# ---------------------------------------------------------------------------
# cleanup_tmp: 安全清理临时目录，显式排除计时器目录
# ---------------------------------------------------------------------------
cleanup_tmp() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] /tmp and /var/tmp (safe mode)         │"
    echo "│ NOTE: ${_VARIANT_TIMER_DIR} EXCLUDED (timer data)  │"
    echo "└─────────────────────────────────────────────────┘"

    # 清理/tmp，但先排除计时器目录
    if [[ -d "${_VARIANT_TIMER_DIR}" ]]; then
        # 临时移动计时器目录到安全位置
        local tmp_timer_backup="/tmp/.variant-timers-backup-$$"
        mv "${_VARIANT_TIMER_DIR}" "${tmp_timer_backup}" 2>/dev/null || true

        rm -rf /tmp/* /tmp/.* 2>/dev/null || true
        rm -rf /var/tmp/* /var/tmp/.* 2>/dev/null || true

        # 恢复计时器目录
        mkdir -p "$(dirname "${_VARIANT_TIMER_DIR}")"
        mv "${tmp_timer_backup}" "${_VARIANT_TIMER_DIR}" 2>/dev/null || true
    else
        # 计时器目录不存在，直接清理
        rm -rf /tmp/* /tmp/.* 2>/dev/null || true
        rm -rf /var/tmp/* /var/tmp/.* 2>/dev/null || true
    fi

    variant_log_ok "tmp directories cleaned (timer dir preserved)"
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
