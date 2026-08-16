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
# 用法: pip_install_group [--index-url <url>] [--verbose] <group_name> <description> <packages...>
#
# --verbose: 启用详细日志模式（适用于源码编译场景）
#   - 安装前：输出Python版本/ABI、pip版本、CC/CXX编译器、Rust版本（如有）
#   - 安装中：使用 pip -v 显示详细输出（wheel检测/编译进度）
#   - 安装后：逐个包import验证并打印版本号
# ---------------------------------------------------------------------------
pip_install_group() {
    local index_url=""
    local verbose=false

    # 解析可选参数
    while [[ $# -gt 0 ]]; do
        case "$1" in
            --index-url)
                index_url="$2"
                shift 2
                ;;
            --verbose)
                verbose=true
                shift
                ;;
            *)
                break
                ;;
        esac
    done

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
    if [[ "${verbose}" == "true" ]]; then
        echo "│ Mode: VERBOSE (source-build diagnostics enabled)"
    fi
    echo "│ PKGS: ${packages[*]}"
    echo "└─────────────────────────────────────────────────┘"

    # ── VERBOSE模式：安装前环境诊断 ──
    if [[ "${verbose}" == "true" ]]; then
        echo "[DIAG] Pre-install environment diagnostics:"
        echo "  - Python: $(python --version 2>&1) ($(which python))"
        python -c "import sysconfig; print(f'  - Python ABI: {sysconfig.get_config_var(\"SOABI\")}')" 2>/dev/null || echo "  - Python ABI: (unable to detect)"
        echo "  - pip: $(pip --version 2>&1 | awk '{print $2}')"
        if [[ -n "${CC:-}" ]]; then
            echo "  - CC: ${CC} ($(${CC} --version 2>&1 | head -1))"
        else
            echo "  - CC: (not set, defaulting to cc/gcc)"
        fi
        if [[ -n "${CXX:-}" ]]; then
            echo "  - CXX: ${CXX} ($(${CXX} --version 2>&1 | head -1))"
        else
            echo "  - CXX: (not set, defaulting to c++/g++)"
        fi
        if command -v rustc &>/dev/null; then
            echo "  - Rust: $(rustc --version 2>&1)"
            echo "  - Cargo: $(cargo --version 2>&1)"
        else
            echo "  - Rust: (not installed - source builds requiring Rust will fail)"
        fi
        echo ""
    fi

    local g_start g_end g_elapsed rc
    g_start=$(date +%s)

    # 构建pip命令参数
    local pip_args=(install --no-cache-dir)
    if [[ -n "${index_url}" ]]; then
        pip_args+=(--index-url "${index_url}")
    fi
    if [[ "${verbose}" == "true" ]]; then
        pip_args+=(-v)
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

        # ── VERBOSE模式：逐个包验证import和版本 ──
        if [[ "${verbose}" == "true" ]]; then
            echo "[VERIFY] Per-package import verification:"
            local pkg_mod
            for pkg in "${packages[@]}"; do
                # 去掉版本约束和extras，得到纯包名
                local pkg_clean
                pkg_clean=$(echo "${pkg}" | sed 's/[>=<=\[].*//g' | tr '[:upper:]' '[:lower:]' | tr '-' '_')
                # 尝试常见的模块名变体（pip包名可能与import名不同）
                local mod_found=false
                for mod_name in "${pkg_clean}" "$(echo ${pkg_clean} | tr '_' '.')"; do
                    if python -c "import ${mod_name}" 2>/dev/null; then
                        local ver
                        ver=$(python -c "import ${mod_name}; print(getattr(${mod_name}, '__version__', 'installed'))" 2>/dev/null || echo "installed")
                        echo "  - [OK] ${pkg} → import ${mod_name} (version: ${ver})"
                        mod_found=true
                        break
                    fi
                done
                if [[ "${mod_found}" == "false" ]]; then
                    # 尝试常见映射：PyMuPDF→fitz, scikit-learn→sklearn, etc.
                    case "${pkg_clean}" in
                        pymupdf)
                            python -c "import fitz; print(f'  - [OK] ${pkg} → import fitz (version: {fitz.__version__})')" 2>/dev/null && mod_found=true ;;
                        scikit_learn)
                            python -c "import sklearn; print(f'  - [OK] ${pkg} → import sklearn (version: {sklearn.__version__})')" 2>/dev/null && mod_found=true ;;
                        beautifulsoup4)
                            python -c "import bs4; print(f'  - [OK] ${pkg} → import bs4 (version: {bs4.__version__})')" 2>/dev/null && mod_found=true ;;
                        opencv_python*)
                            python -c "import cv2; print(f'  - [OK] ${pkg} → import cv2 (version: {cv2.__version__})')" 2>/dev/null && mod_found=true ;;
                        pillow)
                            python -c "import PIL; print(f'  - [OK] ${pkg} → import PIL (version: {PIL.__version__})')" 2>/dev/null && mod_found=true ;;
                        sentence_transformers|sentence-transformers)
                            python -c "import sentence_transformers; print(f'  - [OK] sentence-transformers → import sentence_transformers (version: {sentence_transformers.__version__})')" 2>/dev/null && mod_found=true ;;
                        open_clip_torch)
                            python -c "import open_clip; print(f'  - [OK] open_clip_torch → import open_clip (version: {open_clip.__version__})')" 2>/dev/null && mod_found=true ;;
                        onnx2torch)
                            python -c "import onnx2torch; print(f'  - [OK] onnx2torch → import onnx2torch (version: {getattr(onnx2torch, \"__version__\", \"installed\")})')" 2>/dev/null && mod_found=true ;;
                    esac
                fi
                if [[ "${mod_found}" == "false" ]]; then
                    echo "  - [WARN] ${pkg}: unable to auto-verify import (module name may differ)"
                fi
            done
            echo ""
        fi

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
        echo "[DIAG] Build environment snapshot:"
        echo "  Python: $(python --version 2>&1)"
        echo "  CC: ${CC:-not set}"
        echo "  CXX: ${CXX:-not set}"
        command -v rustc &>/dev/null && echo "  Rust: $(rustc --version 2>&1)"
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

# ---------------------------------------------------------------------------
# 辅助函数：激活conda base环境（ai-dev等需要在base安装包的变体）
# ---------------------------------------------------------------------------
variant_activate_base_env() {
    variant_log_info "Activating conda base environment..."
    # shellcheck source=/dev/null
    source /opt/conda/etc/profile.d/conda.sh
    conda activate base
    export PIP_USER=0
    variant_log_ok "base environment activated (PIP_USER=0 for build-time)"
    echo "  - conda env: ${CONDA_DEFAULT_ENV}"
    echo "  - python: $(python --version 2>&1)"
    echo "  - python path: $(which python)"
    echo ""
}
