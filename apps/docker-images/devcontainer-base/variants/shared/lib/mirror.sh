#!/usr/bin/env bash
# =============================================================================
# mirror.sh — 统一镜像源配置模块（conda/pip/APT）
#
# 提供 variant_configure_mirrors 函数，自动读取 CONDA_MIRROR/PIP_MIRROR/APT_MIRROR
# 环境变量配置对应镜像源，包含性能优化参数。
#
# 依赖：logging.sh（variant_log_* 函数）
# 不修改 shell errexit/nounset 选项
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_MIRROR_LOADED:-}" ]] && return 0
_VARIANT_MIRROR_LOADED=1

# ---------------------------------------------------------------------------
# 内部函数：配置 conda 镜像源
# ---------------------------------------------------------------------------
_variant_configure_conda_mirror() {
    local mirror="${CONDA_MIRROR:-official}"
    local conda_dir="${CONDA_DIR:-/opt/conda}"
    local condarc="${conda_dir}/.condarc"

    variant_log_info "Configuring conda mirror: ${mirror}"

    local conda_url
    case "${mirror}" in
        official)
            variant_log_info "Using official conda-forge mirror"
            conda_url="conda-forge"
            ;;
        tuna)
            variant_log_info "Using TUNA (Tsinghua) conda mirror"
            conda_url="https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/"
            ;;
        aliyun)
            variant_log_info "Using Aliyun conda mirror"
            conda_url="https://mirrors.aliyun.com/anaconda/cloud/conda-forge/"
            ;;
        bfsu)
            variant_log_info "Using BFSU (Beijing Foreign Studies University) conda mirror"
            conda_url="https://mirrors.bfsu.edu.cn/anaconda/cloud/conda-forge/"
            ;;
        *)
            variant_log_error "Unknown CONDA_MIRROR value: ${mirror}. Valid values: official/tuna/aliyun/bfsu"
            return 1
            ;;
    esac

    # 写入 .condarc，包含性能优化参数（按Task 1验收标准要求）
    cat > "${condarc}" <<EOF
channels:
  - ${conda_url}
channel_priority: strict
show_channel_urls: false

# ── Network tuning ──
remote_connect_timeout_secs: 30
remote_read_timeout_secs: 300
remote_max_retries: 5
remote_backoff_factor: 3
ssl_verify: true

# ── Parallel threads ──
repodata_threads: 8
execute_threads: 8

# ── Solver ──
solver: libmamba
EOF

    variant_log_ok "conda mirror configured: ${mirror} -> ${conda_url}"
    return 0
}

# ---------------------------------------------------------------------------
# 内部函数：配置 pip 镜像源
# ---------------------------------------------------------------------------
_variant_configure_pip_mirror() {
    local mirror="${PIP_MIRROR:-official}"
    local pip_index_url

    variant_log_info "Configuring pip mirror: ${mirror}"

    case "${mirror}" in
        official)
            variant_log_info "Using official PyPI mirror"
            pip_index_url="https://pypi.org/simple"
            ;;
        tuna)
            variant_log_info "Using TUNA (Tsinghua) PyPI mirror"
            pip_index_url="https://pypi.tuna.tsinghua.edu.cn/simple"
            ;;
        aliyun)
            variant_log_info "Using Aliyun PyPI mirror"
            pip_index_url="https://mirrors.aliyun.com/pypi/simple"
            ;;
        *)
            variant_log_error "Unknown PIP_MIRROR value: ${mirror}. Valid values: official/tuna/aliyun"
            return 1
            ;;
    esac

    # 配置 root 用户 pip
    local root_pip_dir="/root/.pip"
    mkdir -p "${root_pip_dir}"
    cat > "${root_pip_dir}/pip.conf" <<EOF
[global]
index-url = ${pip_index_url}
trusted-host = $(echo "${pip_index_url}" | sed -e 's|^[^/]*//||' -e 's|/.*$||')
timeout = 120
EOF

    # 配置 devuser 用户 pip（如存在）
    if id -u devuser >/dev/null 2>&1; then
        local devuser_pip_dir="/home/devuser/.pip"
        mkdir -p "${devuser_pip_dir}"
        cat > "${devuser_pip_dir}/pip.conf" <<EOF
[global]
index-url = ${pip_index_url}
trusted-host = $(echo "${pip_index_url}" | sed -e 's|^[^/]*//||' -e 's|/.*$||')
timeout = 120
EOF
        chown -R devuser:devuser "${devuser_pip_dir}"
        variant_log_ok "pip mirror configured for root + devuser: ${mirror}"
    else
        variant_log_ok "pip mirror configured for root: ${mirror}"
    fi

    return 0
}

# ---------------------------------------------------------------------------
# 内部函数：配置 APT 镜像源
# ---------------------------------------------------------------------------
_variant_configure_apt_mirror() {
    local mirror="${APT_MIRROR:-official}"
    local sources_list="/etc/apt/sources.list"
    local sources_list_d="/etc/apt/sources.list.d"

    variant_log_info "Configuring APT mirror: ${mirror}"

    # 检测 Debian/Ubuntu 版本（简化处理，默认Debian bookworm）
    local debian_codename
    if [[ -f /etc/os-release ]]; then
        # shellcheck source=/dev/null
        . /etc/os-release
        debian_codename="${VERSION_CODENAME:-bookworm}"
    else
        debian_codename="bookworm"
    fi

    case "${mirror}" in
        official)
            variant_log_info "Using official Debian APT mirror"
            cat > "${sources_list}" <<EOF
deb http://deb.debian.org/debian ${debian_codename} main contrib non-free non-free-firmware
deb http://deb.debian.org/debian ${debian_codename}-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security ${debian_codename}-security main contrib non-free non-free-firmware
EOF
            ;;
        tuna)
            variant_log_info "Using TUNA (Tsinghua) Debian APT mirror"
            cat > "${sources_list}" <<EOF
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${debian_codename} main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian/ ${debian_codename}-updates main contrib non-free non-free-firmware
deb https://mirrors.tuna.tsinghua.edu.cn/debian-security/ ${debian_codename}-security main contrib non-free non-free-firmware
EOF
            ;;
        aliyun)
            variant_log_info "Using Aliyun Debian APT mirror"
            cat > "${sources_list}" <<EOF
deb https://mirrors.aliyun.com/debian/ ${debian_codename} main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian/ ${debian_codename}-updates main contrib non-free non-free-firmware
deb https://mirrors.aliyun.com/debian-security/ ${debian_codename}-security main contrib non-free non-free-firmware
EOF
            ;;
        *)
            variant_log_error "Unknown APT_MIRROR value: ${mirror}. Valid values: official/tuna/aliyun"
            return 1
            ;;
    esac

    # 清理可能存在的第三方源（可选，只清理我们创建的，不碰已有）
    variant_log_ok "APT mirror configured: ${mirror} (${debian_codename})"
    return 0
}

# ---------------------------------------------------------------------------
# 主函数：配置所有镜像源（conda + pip + APT）
# ---------------------------------------------------------------------------
variant_configure_mirrors() {
    variant_stage_header "Mirror Configuration"

    local rc=0

    _variant_configure_conda_mirror || rc=$?
    _variant_configure_pip_mirror || rc=$?
    _variant_configure_apt_mirror || rc=$?

    if [[ ${rc} -eq 0 ]]; then
        variant_log_ok "All mirrors configured successfully"
    else
        variant_log_error "Mirror configuration completed with errors (rc=${rc})"
    fi

    return ${rc}
}
