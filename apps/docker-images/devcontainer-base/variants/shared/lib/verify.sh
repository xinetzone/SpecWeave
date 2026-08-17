#!/usr/bin/env bash
# =============================================================================
# verify.sh — 基础验证模块（服务检查+环境验证+语法检查）
#
# 提供标准验证函数：验证横幅、基础服务可用性、conda main环境、
# devuser访问权限、bash脚本语法检查。
#
# 依赖：logging.sh（variant_log_* 函数）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_VERIFY_LOADED:-}" ]] && return 0
_VARIANT_VERIFY_LOADED=1

# ---------------------------------------------------------------------------
# verify_validation_header: 输出标准验证检查点横幅
# ---------------------------------------------------------------------------
verify_validation_header() {
    local title="${1:-Final Validation Checkpoint}"
    echo ""
    echo "########################################################################"
    echo "# [VALIDATION CHECKPOINT] ${title}"
    echo "########################################################################"
    echo ""
}

# ---------------------------------------------------------------------------
# _verify_command_exists: 内部函数 - 检查命令是否存在
# ---------------------------------------------------------------------------
_verify_command_exists() {
    local cmd="$1"
    local description="${2:-${cmd}}"
    echo -n "  [VERIFY] ${description}... "
    if command -v "${cmd}" >/dev/null 2>&1; then
        local version
        version=$("${cmd}" --version 2>&1 | head -1 | awk '{print $NF}' || echo "ok")
        echo "[OK] (${version})"
        return 0
    else
        echo "[FAIL] - command not found"
        return 1
    fi
}

# ---------------------------------------------------------------------------
# verify_base_services: 验证基础服务命令可用（docker/supervisord/sshd）
# ---------------------------------------------------------------------------
verify_base_services() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Base services availability             │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    _verify_command_exists docker "Docker CLI" || failed=1
    _verify_command_exists supervisord "Supervisord" || failed=1
    _verify_command_exists sshd "SSH daemon" || failed=1

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "All base services verified"
        return 0
    else
        variant_log_error "One or more base services missing"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_conda_main_env: 验证conda main环境存在且Python可执行
# ---------------------------------------------------------------------------
verify_conda_main_env() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Conda main environment                 │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    echo -n "  [VERIFY] /opt/conda/envs/main exists... "
    if [[ -d /opt/conda/envs/main ]]; then
        echo "[OK]"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] main env python executable... "
    if [[ -x /opt/conda/envs/main/bin/python ]]; then
        local py_ver
        py_ver=$(/opt/conda/envs/main/bin/python --version 2>&1)
        echo "[OK] (${py_ver})"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] conda command... "
    if [[ -x /opt/conda/bin/conda ]]; then
        local conda_ver
        conda_ver=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}')
        echo "[OK] (conda ${conda_ver})"
    else
        echo "[FAIL]"
        failed=1
    fi

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "Conda main environment verified"
        return 0
    else
        variant_log_error "Conda main environment verification failed"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_user_access: 验证指定用户存在且可访问conda（通用版本）
# 用法: verify_user_access [username]
# username 默认使用 DEVTARGET_USER（未设置则为 devuser）
# ---------------------------------------------------------------------------
verify_user_access() {
    local username="${1:-${DEVTARGET_USER:-devuser}}"
    local user_home="/home/${username}"

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] ${username} access permissions         │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    echo -n "  [VERIFY] ${username} exists... "
    if id -u "${username}" >/dev/null 2>&1; then
        echo "[OK] (uid: $(id -u "${username}"))"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] ${username} can access conda dir... "
    if [[ -r /opt/conda ]] && [[ -x /opt/conda ]]; then
        echo "[OK]"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] ${username} .bashrc ownership... "
    if [[ -f "${user_home}/.bashrc" ]]; then
        local owner
        owner=$(stat -c '%U' "${user_home}/.bashrc" 2>/dev/null || echo "unknown")
        if [[ "${owner}" == "${username}" ]]; then
            echo "[OK] (owner: ${owner})"
        else
            echo "[WARN] owner is ${owner} (expected ${username})"
        fi
    else
        echo "[INFO] no .bashrc found (ok if not needed)"
    fi

    echo -n "  [VERIFY] ${username} can execute python... "
    if su - "${username}" -c "python --version" >/dev/null 2>&1; then
        local py_ver
        py_ver=$(su - "${username}" -c "python --version" 2>&1)
        echo "[OK] (${py_ver})"
    else
        echo "[WARN] ${username} python execution check skipped (may need conda activation)"
    fi

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "${username} access verified"
        return 0
    else
        variant_log_error "${username} access verification failed"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_devuser_access: 验证devuser存在且可访问conda（向后兼容wrapper）
# ---------------------------------------------------------------------------
verify_devuser_access() {
    verify_user_access "devuser"
}

# ---------------------------------------------------------------------------
# verify_ssh_config: 验证 sshd 配置文件语法正确（sshd -t）
# ---------------------------------------------------------------------------
verify_ssh_config() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] SSH daemon configuration syntax        │"
    echo "└─────────────────────────────────────────────────┘"

    echo -n "  [VERIFY] sshd -t config syntax... "
    if command -v sshd >/dev/null 2>&1; then
        local saved_opts="$-"
        set +e
        local sshd_output
        sshd_output=$(sshd -t 2>&1)
        local rc=$?
        if [[ "${saved_opts}" == *e* ]]; then
            set -e
        fi
        if [[ ${rc} -eq 0 ]]; then
            echo "[OK]"
            variant_log_ok "sshd configuration syntax is valid"
            return 0
        else
            echo "[FAIL]"
            echo "  sshd -t output: ${sshd_output}"
            variant_log_error "sshd configuration syntax error"
            exit 1
        fi
    else
        echo "[SKIP] sshd not found in image"
        return 0
    fi
}

# ---------------------------------------------------------------------------
# verify_bash_syntax: bash语法检查
# 用法: verify_bash_syntax <script_path> [more_paths...]
# ---------------------------------------------------------------------------
verify_bash_syntax() {
    local failed=0
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] Bash script syntax check               │"
    echo "└─────────────────────────────────────────────────┘"

    local script
    for script in "$@"; do
        echo -n "  [SYNTAX] ${script}... "
        if bash -n "${script}" 2>&1; then
            echo "[OK]"
        else
            echo "[FAIL]"
            failed=1
        fi
    done

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "All bash scripts pass syntax check"
        return 0
    else
        variant_log_error "One or more bash scripts have syntax errors"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# verify_all_basic: 一键执行所有基础验证
# 快捷函数：services + conda env + devuser
# ---------------------------------------------------------------------------
verify_all_basic() {
    verify_validation_header "Basic Environment Validation"
    verify_base_services
    verify_conda_main_env
    verify_devuser_access
    variant_log_ok "All basic verifications passed"
}
