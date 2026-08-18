#!/bin/bash
# =============================================================================
# Stage 4b/4c: mamba create main 环境 (Python ${PYTHON_VERSION} ${PYTHON_BUILD} + Jupyter)
# 变化频率：中（Python/Jupyter版本升级时改），但这是最高耗时层，P2缓存保护核心
# 关键设计：使用mamba CLI单次solve，合并create+install减少solver运行次数
# =============================================================================
set -e

echo "=== Stage 4b/4c: Create 'main' env with Python ${PYTHON_VERSION} ${PYTHON_BUILD} + Jupyter ==="
_STAGE_START=$(date +%s)

. "${CONDA_DIR}/etc/profile.d/conda.sh"

# ── Step 1: 一次性创建main环境（Python cp314t + pip + Jupyter生态，单次solver求解） ──
# 优化：使用mamba CLI直接调用libmamba（比conda --solver=libmamba少Python层开销）；
#       合并create+install为单次mamba create（减少一次solver运行）；
#       8线程并行下载+解压（repodata_threads/execute_threads=8在.condarc中配置）
echo "[INFO] Creating 'main' env with Python ${PYTHON_VERSION} ${PYTHON_BUILD} + Jupyter (single mamba solve)..."
_mamba_start=$(date +%s)
mamba create -y -n main -c conda-forge --override-channels -q \
    "python=${PYTHON_VERSION}=*_${PYTHON_BUILD}" \
    pip \
    "jupyterlab>=4.4" \
    "notebook>=7.3" \
    ipykernel \
    nbconvert \
    jupyter_server 2>&1
_mamba_elapsed=$(($(date +%s) - _mamba_start))
echo "[OK] main env created in ${_mamba_elapsed}s with Python $(/opt/conda/envs/main/bin/python --version 2>&1 | awk '{print $2}')"
echo "[OK] Jupyter ecosystem installed: $(/opt/conda/envs/main/bin/jupyter --version 2>&1 | head -1)"

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "[TIMER] Stage 4b/4c (mamba create main env) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"
echo '[OK] Stage 4b complete'
