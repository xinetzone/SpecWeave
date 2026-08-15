#!/usr/bin/env bash
# =============================================================================
# permissions.sh — 统一权限设置模块
#
# 提供conda目录权限修复、可执行权限设置、devuser bashrc权限等函数。
#
# 依赖：logging.sh（variant_log_* 函数）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_PERMISSIONS_LOADED:-}" ]] && return 0
_VARIANT_PERMISSIONS_LOADED=1

# ---------------------------------------------------------------------------
# ensure_conda_permissions: 修复conda目录权限，确保所有用户可读+可执行
# 关键：chown root:root防止pip/conda安装后文件属主错误
#      chmod -R a+rX确保递归只读+目录可遍历，不改变已有可执行位
# ---------------------------------------------------------------------------
ensure_conda_permissions() {
    local conda_dir="${1:-/opt/conda}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PERM] Fixing conda directory permissions       │"
    echo "│ path: ${conda_dir}"
    echo "└─────────────────────────────────────────────────┘"

    echo "[ACTION] chown -R root:root ${conda_dir}..."
    chown -R root:root "${conda_dir}" 2>/dev/null || true
    echo "[OK] Ownership set to root:root"

    echo "[ACTION] chmod -R a+rX ${conda_dir}..."
    chmod -R a+rX "${conda_dir}" 2>/dev/null || true
    echo "[OK] Read/traverse permissions for all users"

    # 确保bin目录下的二进制有可执行位
    echo "[ACTION] Ensuring executable bit on bin directories..."
    find "${conda_dir}/bin" -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
    if [[ -d "${conda_dir}/envs/main/bin" ]]; then
        find "${conda_dir}/envs/main/bin" -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
    fi
    echo "[OK] Executable bits set on bin files"

    variant_log_ok "Conda permissions fixed"
}

# ---------------------------------------------------------------------------
# ensure_executable_permissions: 确保指定路径下文件有可执行权限
# 用法: ensure_executable_permissions <path> [more_paths...]
# 对所有普通文件添加可执行位（如果它被标记为可执行或在bin目录下）
# ---------------------------------------------------------------------------
ensure_executable_permissions() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PERM] Ensuring executable permissions          │"
    echo "└─────────────────────────────────────────────────┘"

    local path
    for path in "$@"; do
        echo "[ACTION] Processing: ${path}"
        if [[ -f "${path}" ]]; then
            chmod a+x "${path}" 2>/dev/null || true
            echo "  -> single file: chmod a+x"
        elif [[ -d "${path}" ]]; then
            find "${path}" -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
            echo "  -> directory: find +x on executable files"
        else
            echo "  -> [WARN] path not found, skipping"
        fi
    done

    variant_log_ok "Executable permissions set"
}

# ---------------------------------------------------------------------------
# ensure_devuser_bashrc: 确保devuser拥有自己的.bashrc
# ---------------------------------------------------------------------------
ensure_devuser_bashrc() {
    local bashrc_path="${1:-/home/devuser/.bashrc}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PERM] Fixing devuser .bashrc ownership         │"
    echo "└─────────────────────────────────────────────────┘"

    if [[ -f "${bashrc_path}" ]]; then
        chown devuser:devuser "${bashrc_path}" 2>/dev/null || true
        echo "[OK] ${bashrc_path} owned by devuser:devuser"
    else
        echo "[INFO] ${bashrc_path} not found, skipping"
    fi

    # 确保devuser主目录权限正确
    if [[ -d /home/devuser ]]; then
        chown devuser:devuser /home/devuser 2>/dev/null || true
        echo "[OK] /home/devuser owned by devuser:devuser"
    fi

    variant_log_ok "devuser permissions fixed"
}

# ---------------------------------------------------------------------------
# ensure_profile_d_executable: 确保/etc/profile.d/下所有脚本可执行
# ---------------------------------------------------------------------------
ensure_profile_d_executable() {
    local profile_dir="${1:-/etc/profile.d}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PERM] Ensuring /etc/profile.d scripts executable│"
    echo "└─────────────────────────────────────────────────┘"

    if [[ -d "${profile_dir}" ]]; then
        chmod +x "${profile_dir}"/*.sh 2>/dev/null || true
        local count
        count=$(find "${profile_dir}" -name "*.sh" -type f | wc -l)
        echo "[OK] ${count} scripts in ${profile_dir} made executable"
    else
        echo "[INFO] ${profile_dir} not found, skipping"
    fi
}

# ---------------------------------------------------------------------------
# ensure_all_permissions: 一键执行所有权限修复
# ---------------------------------------------------------------------------
ensure_all_permissions() {
    variant_stage_header "Permission Fixes"
    ensure_conda_permissions
    ensure_devuser_bashrc
    ensure_profile_d_executable
    variant_log_ok "All permissions fixed"
}
