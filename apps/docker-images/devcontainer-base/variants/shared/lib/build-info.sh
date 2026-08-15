#!/usr/bin/env bash
# =============================================================================
# build-info.sh — 变体构建信息写入模块
#
# 提供 variant_write_build_info 函数，统一写入构建元数据到 /etc/，
# 自动填充通用字段，支持变体特有扩展字段。
#
# 依赖：logging.sh（variant_log_* 函数）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_BUILD_INFO_LOADED:-}" ]] && return 0
_VARIANT_BUILD_INFO_LOADED=1

# ---------------------------------------------------------------------------
# _variant_get_build_timer_total: 从计时器文件获取总构建耗时
# ---------------------------------------------------------------------------
_variant_get_build_timer_total() {
    local variant_name="$1"
    local timer_file="/root/.variant-timers/${variant_name}.timer"

    if [[ -f "${timer_file}" ]]; then
        local start_time
        start_time=$(grep '^START_TIME=' "${timer_file}" | cut -d= -f2)
        if [[ -n "${start_time}" ]]; then
            local now
            now=$(date +%s)
            echo "$((now - start_time))"
            return 0
        fi
    fi
    echo "unknown"
    return 1
}

# ---------------------------------------------------------------------------
# _variant_check_service_preserved: 检查基础服务命令是否可用
# ---------------------------------------------------------------------------
_variant_check_service_preserved() {
    local service="$1"
    if command -v "${service}" >/dev/null 2>&1; then
        echo "yes"
    else
        echo "no"
    fi
}

# ---------------------------------------------------------------------------
# variant_write_build_info: 写入变体构建信息
# 用法: variant_write_build_info <variant_name> <base_image> [key=value ...]
# ---------------------------------------------------------------------------
variant_write_build_info() {
    local variant_name="$1"
    local base_image="$2"
    shift 2

    local info_file="/etc/devcontainer-variant-${variant_name}-build-info"

    variant_stage_header "Build Metadata"
    echo "[ACTION] Writing build metadata to ${info_file}..."

    # 自动检测基础信息
    local build_date
    build_date=$(date -u +%Y-%m-%dT%H:%M:%SZ)

    local conda_mirror="${CONDA_MIRROR:-unknown}"
    local pip_mirror="${PIP_MIRROR:-unknown}"
    local apt_mirror="${APT_MIRROR:-unknown}"

    local build_timer
    build_timer=$(_variant_get_build_timer_total "${variant_name}")

    local docker_preserved
    docker_preserved=$(_variant_check_service_preserved docker)
    local supervisord_preserved
    supervisord_preserved=$(_variant_check_service_preserved supervisord)
    local sshd_preserved
    sshd_preserved=$(_variant_check_service_preserved sshd)
    local jupyter_preserved
    jupyter_preserved=$(_variant_check_service_preserved jupyter)

    # 检测Python版本和free-threading状态
    local python_version="unknown"
    local python_build="unknown"
    if command -v python >/dev/null 2>&1; then
        python_version=$(python --version 2>&1 | awk '{print $2}')
        python_build=$(python -c "import sys; print('free-threading nogil active' if not sys._is_gil_enabled() else 'GIL enabled')" 2>&1 || echo "unknown")
    fi

    local conda_version="unknown"
    if [[ -x /opt/conda/bin/conda ]]; then
        conda_version=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}')
    fi

    # 写入文件
    cat > "${info_file}" <<EOF
BUILD_DATE=${build_date}
VARIANT=${variant_name}
BASE_IMAGE=${base_image}
CONDA_VERSION=${conda_version}
PYTHON_VERSION=${python_version}
PYTHON_BUILD=${python_build}
CONDA_DIR=/opt/conda
CONDA_ENV=main
CONDA_MIRROR=${conda_mirror}
PIP_MIRROR=${pip_mirror}
APT_MIRROR=${apt_mirror}
SERVICES_PRESERVED=docker:${docker_preserved}, supervisord:${supervisord_preserved}, sshd:${sshd_preserved}, jupyter:${jupyter_preserved}
BUILD_TIMER=${build_timer}s
EOF

    # 追加变体特有字段
    local kv
    for kv in "$@"; do
        if [[ "${kv}" == *=* ]]; then
            echo "${kv}" >> "${info_file}"
        else
            variant_log_warn "Ignoring invalid extra field (not key=value): ${kv}"
        fi
    done

    echo ""
    echo "--- Build Info Contents ---"
    cat "${info_file}"
    echo "--- End Build Info ---"
    echo ""
    variant_log_ok "Build info written successfully to ${info_file}"
}
