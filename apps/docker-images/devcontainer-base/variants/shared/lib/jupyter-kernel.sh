#!/usr/bin/env bash
# =============================================================================
# jupyter-kernel.sh — Jupyter 自定义内核注册模块
#
# 提供通用的 Jupyter 自定义内核注册能力：自动检测存在的 Jupyter 数据路径
# （/opt/venv、/opt/conda base、/opt/conda main），在所有存在的位置
# 同步注册内核，支持自定义 Python 路径和额外环境变量。
#
# 依赖：logging.sh（variant_log_* 函数）
# 依赖：user-management.sh（DEVTARGET_USER 变量）
# 不修改 shell errexit/nounset 选项
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_JUPYTER_KERNEL_LOADED:-}" ]] && return 0
_VARIANT_JUPYTER_KERNEL_LOADED=1

# 默认 Jupyter 数据路径列表（按优先级排序）
_VARIANT_JUPYTER_PATHS=(
    "/opt/venv/share/jupyter"
    "/opt/conda/share/jupyter"
    "/opt/conda/envs/main/share/jupyter"
)

# ---------------------------------------------------------------------------
# 内部辅助：检测存在的 Jupyter 数据路径
# 输出到 stdout，每行一个路径
# ---------------------------------------------------------------------------
_detect_jupyter_paths() {
    local detected=()
    for jpath in "${_VARIANT_JUPYTER_PATHS[@]}"; do
        if [[ -d "${jpath}" ]]; then
            detected+=("${jpath}")
        fi
    done
    printf '%s\n' "${detected[@]}"
}

# ---------------------------------------------------------------------------
# 内部辅助：生成 kernel.json 内容
# 用法: _write_kernel_json <python_path> <display_name> [extra_env...]
# ---------------------------------------------------------------------------
_write_kernel_json() {
    local python_path="$1"
    local display_name="$2"
    shift 2
    local extra_env=("$@")

    # 构建 env 字段
    local env_json=""
    local default_path="/opt/venv/bin:/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

    # 检查是否有 PATH 覆盖
    local has_custom_path=false
    local custom_path="${default_path}"
    local env_entries=()

    for env_var in "${extra_env[@]}"; do
        local key="${env_var%%=*}"
        local val="${env_var#*=}"
        if [[ "${key}" == "PATH" ]]; then
            has_custom_path=true
            custom_path="${val}"
        else
            env_entries+=("\"${key}\": \"${val}\"")
        fi
    done

    # PATH 总是需要的
    env_entries=("\"PATH\": \"${custom_path}\"" "${env_entries[@]}")

    # 拼接 env JSON
    if [[ ${#env_entries[@]} -gt 0 ]]; then
        env_json=$(IFS=,; echo "${env_entries[*]}")
    fi

    # 输出 kernel.json
    cat <<EOF
{
  "argv": ["${python_path}", "-m", "ipykernel_launcher", "-f", "{connection_file}"],
  "display_name": "${display_name}",
  "language": "python",
  "metadata": {"debugger": true},
  "env": {${env_json}}
}
EOF
}

# ---------------------------------------------------------------------------
# variant_register_jupyter_kernel: 注册自定义 Jupyter 内核
# 用法: variant_register_jupyter_kernel <kernel_name> <display_name> <python_path> [extra_env...]
#
# 参数:
#   kernel_name    - 内核目录名（如 npu、pytorch、ai-dev、custom）
#   display_name   - Jupyter UI 中显示的名称（如 "Python 3 (NPU Dev)"）
#   python_path    - 内核使用的 Python 解释器绝对路径
#   extra_env...   - 额外环境变量（0或多个，格式 KEY=VALUE）
#
# 自动检测所有存在的 Jupyter 路径并同步注册，路径不存在则跳过。
#
# 示例:
#   variant_register_jupyter_kernel "npu" "Python 3 (NPU Dev)" "/opt/conda/bin/python" \
#       "PYTHONPATH=/workspace/npu_tvm/python:/workspace/npuusertools" \
#       "OMP_NUM_THREADS=4"
# ---------------------------------------------------------------------------
variant_register_jupyter_kernel() {
    local kernel_name="$1"
    local display_name="$2"
    local python_path="$3"
    shift 3
    local extra_env=("$@")

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [REGISTER JUPYTER KERNEL] ${kernel_name}"
    echo "│ Display: ${display_name}"
    echo "│ Python:  ${python_path}"
    if [[ ${#extra_env[@]} -gt 0 ]]; then
        echo "│ Env:     ${extra_env[*]}"
    fi
    echo "└─────────────────────────────────────────────────┘"

    # 检测存在的 Jupyter 路径
    local jupyter_paths=()
    while IFS= read -r path; do
        [[ -n "${path}" ]] && jupyter_paths+=("${path}")
    done < <(_detect_jupyter_paths)

    if [[ ${#jupyter_paths[@]} -eq 0 ]]; then
        variant_log_info "No Jupyter data directories found, kernel registration skipped"
        echo ""
        return 0
    fi

    variant_log_info "Detected ${#jupyter_paths[@]} Jupyter path(s):"
    for jpath in "${jupyter_paths[@]}"; do
        echo "  - ${jpath}"
    done

    local target_user="${DEVTARGET_USER:-devuser}"
    local target_group
    target_group=$(id -gn "${target_user}" 2>/dev/null || echo "${target_user}")
    local registered=0

    for jpath in "${jupyter_paths[@]}"; do
        local kernel_dir="${jpath}/kernels/${kernel_name}"

        mkdir -p "${kernel_dir}"

        # 写入 kernel.json
        _write_kernel_json "${python_path}" "${display_name}" "${extra_env[@]}" > "${kernel_dir}/kernel.json"

        # 设置权限
        chown -R "${target_user}:${target_group}" "${kernel_dir}" 2>/dev/null || true
        chmod 755 "${kernel_dir}"
        chmod 644 "${kernel_dir}/kernel.json"

        variant_log_ok "Kernel '${kernel_name}' registered at ${kernel_dir}"
        registered=$((registered + 1))
    done

    echo ""
    variant_log_ok "Jupyter kernel '${kernel_name}' registered to ${registered} location(s)"
    echo ""
}

# ---------------------------------------------------------------------------
# verify_jupyter_kernel: 验证 Jupyter 内核已注册
# 用法: verify_jupyter_kernel <kernel_name> [jupyter_base_path]
#
# 如果指定 jupyter_base_path，则只检查该路径；否则检查所有默认路径。
# ---------------------------------------------------------------------------
verify_jupyter_kernel() {
    local kernel_name="$1"
    local jupyter_base_path="${2:-}"

    local paths_to_check=()
    if [[ -n "${jupyter_base_path}" ]]; then
        paths_to_check=("${jupyter_base_path}")
    else
        while IFS= read -r path; do
            [[ -n "${path}" ]] && paths_to_check+=("${path}")
        done < <(_detect_jupyter_paths)
    fi

    local found=0
    for jpath in "${paths_to_check[@]}"; do
        local kernel_json="${jpath}/kernels/${kernel_name}/kernel.json"
        if [[ -f "${kernel_json}" ]]; then
            echo "[PASS] Jupyter kernel '${kernel_name}' found at ${kernel_json}"
            found=$((found + 1))
        fi
    done

    if [[ ${found} -eq 0 ]]; then
        echo "[FAIL] Jupyter kernel '${kernel_name}' not found in any expected location"
        return 1
    fi

    echo "[OK] Jupyter kernel '${kernel_name}' verified (${found} location(s))"
    return 0
}
