#!/usr/bin/env bash
# =============================================================================
# docs.sh — 文档部署模块
#
# 将文档复制到容器内 /opt/docs/ 目录并设置正确权限，使所有用户可读。
#
# 依赖：logging.sh（variant_log_* 函数）
# 不修改 shell errexit/nounset 选项
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_DOCS_LOADED:-}" ]] && return 0
_VARIANT_DOCS_LOADED=1

# ---------------------------------------------------------------------------
# variant_deploy_docs: 部署文档到容器内 /opt/docs/
# 用法: variant_deploy_docs <src_path> [dest_subdir]
#
# 参数:
#   src_path     - 源路径（文件或目录，相对于构建上下文，需提前 COPY 到镜像内）
#   dest_subdir  - 目标子目录（可选，默认放到 /opt/docs/ 根目录）
#
# 自动创建目标目录，复制后设置 chmod -R a+rX（所有用户可读，目录可遍历）。
#
# 示例（在 Dockerfile 中使用）:
#   COPY docs/ /tmp/docs/
#   RUN <<'S_DOCS'
#   source /usr/local/share/variant-framework/variant-framework.sh
#   variant_deploy_docs "/tmp/docs" "project-docs"
#   rm -rf /tmp/docs
#   S_DOCS
# ---------------------------------------------------------------------------
variant_deploy_docs() {
    local src_path="$1"
    local dest_subdir="${2:-}"

    local dest_dir="/opt/docs"
    if [[ -n "${dest_subdir}" ]]; then
        dest_dir="${dest_dir}/${dest_subdir}"
    fi

    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [DEPLOY DOCS]"
    echo "│ Source: ${src_path}"
    echo "│ Dest:   ${dest_dir}"
    echo "└─────────────────────────────────────────────────┘"

    # 检查源路径存在
    if [[ ! -e "${src_path}" ]]; then
        variant_log_error "Source path '${src_path}' does not exist"
        return 1
    fi

    # 创建目标目录
    mkdir -p "${dest_dir}"

    # 复制文档
    if [[ -d "${src_path}" ]]; then
        # 目录：复制内容
        cp -a "${src_path}/." "${dest_dir}/"
        variant_log_info "Directory copied: ${src_path} → ${dest_dir}"
    else
        # 文件：直接复制
        cp -a "${src_path}" "${dest_dir}/"
        variant_log_info "File copied: ${src_path} → ${dest_dir}"
    fi

    # 设置权限：所有用户可读，目录可遍历
    chmod -R a+rX "${dest_dir}"

    # 如果目标用户存在，设置所有者（可选）
    local target_user="${DEVTARGET_USER:-devuser}"
    if id "${target_user}" &>/dev/null; then
        local target_group
        target_group=$(id -gn "${target_user}" 2>/dev/null || echo "${target_user}")
        chown -R "root:${target_group}" "${dest_dir}" 2>/dev/null || true
    fi

    variant_log_ok "Docs deployed to ${dest_dir}"
    echo ""
}
