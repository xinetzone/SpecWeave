#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/../lib"

source "${LIB_DIR}/logging.sh"
source "${LIB_DIR}/install-helpers.sh"

echo "=== 验证函数存在 ==="
for fn in conda_install_group pip_install_group variant_activate_main_env; do
    if declare -F "$fn" >/dev/null 2>&1; then
        echo "[OK] $fn 已定义"
    else
        echo "[FAIL] $fn 缺失"
        exit 1
    fi
done

echo ""
echo "=== 所有install相关函数 ==="
declare -F | grep -i -E 'conda_install|pip_install|activate' || true

echo ""
echo "=== 加载保护变量检查 ==="
echo "_VARIANT_INSTALL_HELPERS_LOADED=${_VARIANT_INSTALL_HELPERS_LOADED}"

echo ""
echo "=== 重复source测试 ==="
source "${LIB_DIR}/install-helpers.sh"
echo "[OK] 重复source无报错"

echo ""
echo "[OK] 所有验证通过"
