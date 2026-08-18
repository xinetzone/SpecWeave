#!/usr/bin/env bash
# =============================================================================
# mirror.sh — 统一镜像源配置模块（conda/pip/APT）
#
# 提供 variant_configure_mirrors 函数，自动读取 CONDA_MIRROR/PIP_MIRROR/APT_MIRROR
# 环境变量配置对应镜像源，包含性能优化参数。
#
# 依赖：logging.sh（variant_log_* 函数）
# 不修改 shell errexit/nounset 选项
# 环境变量：
#   CONDA_DIR       - conda安装目录（默认/opt/conda）
#   DEVTARGET_USER  - dev用户名（默认devuser）
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

    # 写入 .condarc，包含性能优化参数
    cat > "${condarc}" <<EOF
channels:
  - ${conda_url}
channel_priority: strict
show_channel_urls: false
auto_activate_base: false
ssl_verify: true

# ── Network tuning ──
remote_connect_timeout_secs: 30
remote_read_timeout_secs: 300
remote_max_retries: 5
remote_backoff_factor: 3

# ── Parallel threads ──
repodata_threads: 8
execute_threads: 8

# ── Solver ──
solver: libmamba
EOF

    echo "[INFO] .condarc written to ${condarc}:"
    cat "${condarc}"
    echo ""

    variant_log_ok "conda mirror configured: ${mirror}"
    return 0
}

# ---------------------------------------------------------------------------
# 内部函数：配置 pip 镜像源
# ---------------------------------------------------------------------------
_variant_configure_pip_mirror() {
    local mirror="${PIP_MIRROR:-official}"
    local devuser="${DEVTARGET_USER:-devuser}"
    local pip_index_url
    local pip_trusted_host

    variant_log_info "Configuring pip mirror: ${mirror}"

    case "${mirror}" in
        official)
            variant_log_info "Using official PyPI mirror"
            pip_index_url="https://pypi.org/simple"
            pip_trusted_host=""
            ;;
        tuna)
            variant_log_info "Using TUNA (Tsinghua) PyPI mirror"
            pip_index_url="https://pypi.tuna.tsinghua.edu.cn/simple"
            pip_trusted_host="pypi.tuna.tsinghua.edu.cn"
            ;;
        aliyun)
            variant_log_info "Using Aliyun PyPI mirror"
            pip_index_url="https://mirrors.aliyun.com/pypi/simple"
            pip_trusted_host="mirrors.aliyun.com"
            ;;
        bfsu)
            variant_log_info "Using BFSU PyPI mirror"
            pip_index_url="https://mirrors.bfsu.edu.cn/pypi/simple"
            pip_trusted_host="mirrors.bfsu.edu.cn"
            ;;
        *)
            variant_log_error "Unknown PIP_MIRROR value: ${mirror}. Valid values: official/tuna/aliyun/bfsu"
            return 1
            ;;
    esac

    _write_pip_conf() {
        local pip_dir="$1"
        mkdir -p "${pip_dir}"
        cat > "${pip_dir}/pip.conf" <<EOF
[global]
index-url = ${pip_index_url}
timeout = 120
retries = 5
EOF
        if [[ -n "${pip_trusted_host}" ]]; then
            echo "trusted-host = ${pip_trusted_host}" >> "${pip_dir}/pip.conf"
        fi
    }

    # 配置 root 用户 pip（兼容.pip和.config/pip两个位置）
    _write_pip_conf "/root/.pip"
    _write_pip_conf "/root/.config/pip"

    # 配置目标用户 pip（如存在）
    if id -u "${devuser}" >/dev/null 2>&1; then
        _write_pip_conf "/home/${devuser}/.pip"
        _write_pip_conf "/home/${devuser}/.config/pip"
        chown -R "${devuser}:${devuser}" "/home/${devuser}/.pip" "/home/${devuser}/.config/pip" 2>/dev/null || true
        variant_log_ok "pip mirror configured for root + ${devuser}: ${mirror}"
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

    # 如果APT_MIRROR为空或official，且已有系统默认配置，则不修改
    if [[ "${mirror}" == "official" ]] && [[ -f "${sources_list}" ]] && [[ -s "${sources_list}" ]]; then
        variant_log_info "APT mirror: using existing system sources (official default)"
        return 0
    fi

    variant_log_info "Configuring APT mirror: ${mirror}"

    # 检测 Debian/Ubuntu 版本
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
