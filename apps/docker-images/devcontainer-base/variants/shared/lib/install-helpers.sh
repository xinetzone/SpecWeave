#!/usr/bin/env bash
# =============================================================================
# install-helpers.sh — 包安装辅助模块（apt/conda/pip分组安装）
#
# 提供 apt_install_group / conda_install_group / pip_install_group 函数，
# 带结构化日志、计时、错误诊断功能。
#
# 依赖：logging.sh（variant_log_* 函数）
# 不修改 shell errexit/nounset 选项，只临时切换 set +e
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_INSTALL_HELPERS_LOADED:-}" ]] && return 0
_VARIANT_INSTALL_HELPERS_LOADED=1

# ---------------------------------------------------------------------------
# apt_install_group: 分组安装APT系统包
# 用法: apt_install_group <description> <packages...>
# 注意：需要先配置好APT镜像源并执行apt-get update
# ---------------------------------------------------------------------------
apt_install_group() {
    local description="$1"
    shift
    local packages=("$@")

    if [[ ${#packages[@]} -eq 0 ]]; then
        variant_log_info "No apt packages to install for: ${description}"
        return 0
    fi

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [APT INSTALL] ${description}"
    echo "│ PKGS: ${packages[*]}"
    echo "└─────────────────────────────────────────────────┘"

    local g_start g_end g_elapsed rc
    g_start=$(date +%s)

    local saved_opts="$-"
    set +e
    apt-get install -y --no-install-recommends -qq "${packages[@]}" 2>&1
    rc=$?
    if [[ "${saved_opts}" == *e* ]]; then
        set -e
    fi

    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))

    if [[ ${rc} -eq 0 ]]; then
        variant_log_ok "APT: ${description} installed in ${g_elapsed}s"
        echo ""
        return 0
    else
        variant_log_error "APT: ${description} failed after ${g_elapsed}s (exit code: ${rc})"
        exit ${rc}
    fi
}

# ---------------------------------------------------------------------------
# conda_install_group: 分组安装conda包
# 用法: conda_install_group <group_name> <description> <packages...>
# ---------------------------------------------------------------------------
conda_install_group() {
    local group_name="$1"
    local description="$2"
    shift 2
    local packages=("$@")

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONDA INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    echo "│ PKGS: ${packages[*]}"
    echo "└─────────────────────────────────────────────────┘"

    local g_start g_end g_elapsed rc
    g_start=$(date +%s)

    # 临时关闭errexit以捕获返回码
    local saved_opts="$-"
    set +e
    conda install -y --override-channels -c conda-forge "${packages[@]}" 2>&1
    rc=$?
    # 恢复errexit（如果之前是开启的）
    if [[ "${saved_opts}" == *e* ]]; then
        set -e
    fi

    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))

    if [[ ${rc} -eq 0 ]]; then
        variant_log_ok "${group_name} installed in ${g_elapsed}s"
        echo "[CHECK] Installed package versions:"
        # 提取包名（去掉版本约束）用于grep
        local pkg_pattern
        pkg_pattern=$(printf '%s\n' "${packages[@]}" | sed 's/[>=<].*//g' | tr '\n' '|' | sed 's/|$//')
        conda list 2>/dev/null | grep -iE "${pkg_pattern}" | head -20 || true
        echo ""
        return 0
    else
        variant_log_error "${group_name} failed after ${g_elapsed}s (exit code: ${rc})"
        echo "[DIAG] conda list for conflict diagnosis:"
        local pkg_pattern
        pkg_pattern=$(printf '%s\n' "${packages[@]}" | sed 's/[>=<].*//g' | tr '\n' '|' | sed 's/|$//')
        conda list 2>/dev/null | grep -iE "${pkg_pattern}" | head -30 || true
        exit ${rc}
    fi
}

# ---------------------------------------------------------------------------
# pip_install_group: 分组安装pip包
# 用法: pip_install_group [--index-url <url>] <group_name> <description> <packages...>
# ---------------------------------------------------------------------------
pip_install_group() {
    local index_url=""

    # 解析可选的 --index-url 参数
    if [[ "$1" == "--index-url" ]]; then
        index_url="$2"
        shift 2
    fi

    local group_name="$1"
    local description="$2"
    shift 2
    local packages=("$@")

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PIP INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    if [[ -n "${index_url}" ]]; then
        echo "│ Index-URL: ${index_url}"
    fi
    echo "│ PKGS: ${packages[*]}"
    echo "└─────────────────────────────────────────────────┘"

    local g_start g_end g_elapsed rc
    g_start=$(date +%s)

    # 构建pip命令参数
    local pip_args=(install --no-cache-dir)
    if [[ -n "${index_url}" ]]; then
        pip_args+=(--index-url "${index_url}")
    fi
    pip_args+=("${packages[@]}")

    # 临时关闭errexit以捕获返回码
    local saved_opts="$-"
    set +e
    pip "${pip_args[@]}" 2>&1
    rc=$?
    # 恢复errexit（如果之前是开启的）
    if [[ "${saved_opts}" == *e* ]]; then
        set -e
    fi

    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))

    if [[ ${rc} -eq 0 ]]; then
        variant_log_ok "${group_name} installed in ${g_elapsed}s"
        echo "[CHECK] pip check (dependency consistency):"
        pip check 2>&1 || echo "[WARN] pip check reported issues (may be expected during incremental installs)"
        echo ""
        return 0
    else
        variant_log_error "${group_name} failed after ${g_elapsed}s (exit code: ${rc})"
        echo "[DIAG] pip list for conflict diagnosis (relevant packages):"
        local pkg_pattern
        pkg_pattern=$(printf '%s\n' "${packages[@]}" | sed 's/[>=<=\[].*//g' | tr '\n' '|' | sed 's/|$//')
        pip list 2>/dev/null | grep -iE "${pkg_pattern}" | head -30 || true
        exit ${rc}
    fi
}

# ---------------------------------------------------------------------------
# 辅助函数：激活conda main环境（在变体构建中常用）
# ---------------------------------------------------------------------------
variant_activate_main_env() {
    variant_log_info "Activating conda main environment..."
    # shellcheck source=/dev/null
    source /opt/conda/etc/profile.d/conda.sh
    conda activate main
    variant_log_ok "main environment activated"
    echo "  - conda env: ${CONDA_DEFAULT_ENV}"
    echo "  - python: $(python --version 2>&1)"
    echo "  - python path: $(which python)"
    echo ""
}
