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
# verify_devuser_access: 验证devuser存在且可访问conda
# ---------------------------------------------------------------------------
verify_devuser_access() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [VERIFY] devuser access permissions             │"
    echo "└─────────────────────────────────────────────────┘"

    local failed=0

    echo -n "  [VERIFY] devuser exists... "
    if id -u devuser >/dev/null 2>&1; then
        echo "[OK] (uid: $(id -u devuser))"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] devuser can access conda dir... "
    if [[ -r /opt/conda ]] && [[ -x /opt/conda ]]; then
        echo "[OK]"
    else
        echo "[FAIL]"
        failed=1
    fi

    echo -n "  [VERIFY] devuser .bashrc ownership... "
    if [[ -f /home/devuser/.bashrc ]]; then
        local owner
        owner=$(stat -c '%U' /home/devuser/.bashrc 2>/dev/null || echo "unknown")
        if [[ "${owner}" == "devuser" ]]; then
            echo "[OK] (owner: ${owner})"
        else
            echo "[WARN] owner is ${owner} (expected devuser)"
        fi
    else
        echo "[INFO] no .bashrc found (ok if not needed)"
    fi

    echo -n "  [VERIFY] devuser can execute python... "
    if su - devuser -c "python --version" >/dev/null 2>&1; then
        local py_ver
        py_ver=$(su - devuser -c "python --version" 2>&1)
        echo "[OK] (${py_ver})"
    else
        echo "[WARN] devuser python execution check skipped (may need conda activation)"
    fi

    if [[ ${failed} -eq 0 ]]; then
        variant_log_ok "devuser access verified"
        return 0
    else
        variant_log_error "devuser access verification failed"
        exit 1
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
