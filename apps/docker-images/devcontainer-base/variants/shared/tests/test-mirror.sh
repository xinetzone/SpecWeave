#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LIB_DIR="${SCRIPT_DIR}/../lib"

# 测试临时目录
TEST_DIR="/tmp/test-mirror-$$"
mkdir -p "${TEST_DIR}"
mkdir -p "${TEST_DIR}/conda"
mkdir -p "${TEST_DIR}/home/devuser/.pip"

# source依赖
source "${LIB_DIR}/logging.sh"
source "${LIB_DIR}/mirror.sh"

PASS=0
FAIL=0

check() {
    local desc="$1"
    local cond="$2"
    if eval "${cond}"; then
        echo "[PASS] ${desc}"
        PASS=$((PASS+1))
    else
        echo "[FAIL] ${desc}"
        FAIL=$((FAIL+1))
    fi
}

echo "========================================"
echo "测试1: official conda mirror"
echo "========================================"
export CONDA_DIR="${TEST_DIR}/conda"
export CONDA_MIRROR=official
_variant_configure_conda_mirror
echo "--- .condarc 内容 ---"
cat "${CONDA_DIR}/.condarc"
echo ""
check "official: conda-forge channel" "grep -q 'conda-forge' ${CONDA_DIR}/.condarc"
check "official: repodata_threads=8" "grep -q 'repodata_threads: 8' ${CONDA_DIR}/.condarc"
check "official: execute_threads=8" "grep -q 'execute_threads: 8' ${CONDA_DIR}/.condarc"
check "official: solver=libmamba" "grep -q 'solver: libmamba' ${CONDA_DIR}/.condarc"
check "official: remote_read_timeout_secs=300" "grep -q 'remote_read_timeout_secs: 300' ${CONDA_DIR}/.condarc"

echo ""
echo "========================================"
echo "测试2: tuna conda mirror"
echo "========================================"
export CONDA_MIRROR=tuna
_variant_configure_conda_mirror
echo "--- .condarc 内容 ---"
cat "${CONDA_DIR}/.condarc"
echo ""
check "tuna: tuna.tsinghua URL" "grep -q 'tuna.tsinghua.edu.cn' ${CONDA_DIR}/.condarc"
check "tuna: 所有性能参数存在" "grep -q 'remote_max_retries: 5' ${CONDA_DIR}/.condarc && grep -q 'remote_backoff_factor: 3' ${CONDA_DIR}/.condarc"

echo ""
echo "========================================"
echo "测试3: aliyun conda mirror"
echo "========================================"
export CONDA_MIRROR=aliyun
_variant_configure_conda_mirror
echo "--- .condarc 内容 ---"
cat "${CONDA_DIR}/.condarc"
echo ""
check "aliyun: aliyun URL" "grep -q 'mirrors.aliyun.com' ${CONDA_DIR}/.condarc"

echo ""
echo "========================================"
echo "测试4: bfsu conda mirror"
echo "========================================"
export CONDA_MIRROR=bfsu
_variant_configure_conda_mirror
echo "--- .condarc 内容 ---"
cat "${CONDA_DIR}/.condarc"
echo ""
check "bfsu: bfsu.edu.cn URL" "grep -q 'mirrors.bfsu.edu.cn' ${CONDA_DIR}/.condarc"

echo ""
echo "========================================"
echo "测试5: 无效镜像源返回错误"
echo "========================================"
export CONDA_MIRROR=invalid
if _variant_configure_conda_mirror 2>/dev/null; then
    check "invalid mirror: 返回错误码" "false"
else
    check "invalid mirror: 返回错误码" "true"
fi

echo ""
echo "========================================"
echo "测试6: pip mirror 配置"
echo "========================================"
# 创建devuser用户用于测试（如果不存在不影响）
export PIP_MIRROR=tuna
HOME_BAK="$HOME"
export HOME="${TEST_DIR}/home"
mkdir -p /root/.pip 2>/dev/null || true
_variant_configure_pip_mirror || true
echo ""

echo ""
echo "========================================"
echo "测试总结"
echo "========================================"
echo "PASS: ${PASS}"
echo "FAIL: ${FAIL}"

# 清理
rm -rf "${TEST_DIR}"

if [[ ${FAIL} -gt 0 ]]; then
    exit 1
fi
exit 0
