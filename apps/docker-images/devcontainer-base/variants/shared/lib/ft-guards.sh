#!/bin/bash
# =============================================================================
# ft-guards.sh — free-threading 完整性守卫与包断言模块
#
# 提供 free-threading Python 构建检查、GIL状态验证、包存在/缺席守卫函数。
# 所有断言失败时输出清晰错误信息并 exit 1。
#
# 依赖：logging.sh（variant_log_* 函数）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_FT_GUARDS_LOADED:-}" ]] && return 0
_VARIANT_FT_GUARDS_LOADED=1

# ---------------------------------------------------------------------------
# assert_python_cp314t: 验证Python是cp314t（free-threading）构建
# ---------------------------------------------------------------------------
assert_python_cp314t() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [GUARD] python cp314t free-threading build check"
    echo "└─────────────────────────────────────────────────┘"

    local py_build
    py_build=$(conda list python 2>/dev/null | grep '^python ' | awk '{print $3}')
    echo "  - python build string: ${py_build}"

    case "${py_build}" in
        *cp314t*)
            variant_log_ok "python is free-threading (cp314t) build"
            return 0
            ;;
        *)
            variant_log_error "python lost free-threading build (got: ${py_build})"
            echo "        A package forced the GIL build - check the solver transaction above."
            exit 1
            ;;
    esac
}

# ---------------------------------------------------------------------------
# assert_free_threading: 验证GIL已禁用（free-threading运行时激活）
# ---------------------------------------------------------------------------
assert_free_threading() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [GUARD] free-threading runtime (GIL disabled)   │"
    echo "└─────────────────────────────────────────────────┘"

    local gil_state
    gil_state=$(python -c "import sys; print(sys._is_gil_enabled())" 2>&1)
    echo "  - sys._is_gil_enabled(): ${gil_state}"

    if [[ "${gil_state}" == "False" ]]; then
        variant_log_ok "GIL is disabled - nogil runtime active"
        return 0
    else
        variant_log_error "GIL is enabled - free-threading is NOT active"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# assert_package_present: 正向守卫 - 验证包可导入
# 用法: assert_package_present <pkg_name> [friendly_name]
# ---------------------------------------------------------------------------
assert_package_present() {
    local pkg_name="$1"
    local friendly_name="${2:-${pkg_name}}"

    echo -n "  [ASSERT] ${friendly_name} import... "
    if python -c "import ${pkg_name}" 2>/dev/null; then
        echo "[OK]"
        return 0
    else
        echo "[FAIL]"
        variant_log_error "Package '${friendly_name}' (import '${pkg_name}') is NOT importable"
        exit 1
    fi
}

# ---------------------------------------------------------------------------
# assert_package_absent: 负向守卫 - 验证包不可导入
# 用法: assert_package_absent <pkg_name> [friendly_name]
# 用于验证torch等包确实未安装（如onnx-dev变体）
# ---------------------------------------------------------------------------
assert_package_absent() {
    local pkg_name="$1"
    local friendly_name="${2:-${pkg_name}}"

    echo -n "  [ASSERT] ${friendly_name} should be absent... "
    if python -c "import ${pkg_name}" 2>/dev/null; then
        echo "[PRESENT - FAIL]"
        variant_log_error "Package '${friendly_name}' (import '${pkg_name}') SHOULD be absent but IS importable"
        exit 1
    else
        echo "[ABSENT - OK]"
        return 0
    fi
}

# ---------------------------------------------------------------------------
# variant_ft_guard_all: 一键执行所有free-threading基础守卫
# 快捷函数：同时检查cp314t构建 + GIL disabled
# ---------------------------------------------------------------------------
variant_ft_guard_all() {
    variant_stage_header "Free-Threading Integrity Guards"
    assert_python_cp314t
    assert_free_threading
    variant_log_ok "All free-threading guards passed"
}
