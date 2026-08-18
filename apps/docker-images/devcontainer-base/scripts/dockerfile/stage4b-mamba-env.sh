#!/bin/bash
# =============================================================================
# Stage 4b/4c: mamba create main 环境 (Python ${PYTHON_VERSION} ${PYTHON_BUILD} + Jupyter)
# 变化频率：中（Python/Jupyter版本升级时改），但这是最高耗时层，P2缓存保护核心
# 关键设计：使用mamba CLI单次solve，合并create+install减少solver运行次数
# =============================================================================
set -e

# 防止Python在mamba安装后脚本中生成.pyc文件
export PYTHONDONTWRITEBYTECODE=1

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

# ── Step 2: 同层清理不需要的文件（用mamba remove会导致依赖级联，改为手动删除文件） ──
echo "[CLEAN] Removing tk/tcl Tkinter files manually (tk is a Python dep, can't mamba-remove)..."
rm -rf /opt/conda/envs/main/lib/tk8.6 /opt/conda/envs/main/lib/tcl8.6 2>/dev/null || true
rm -rf /opt/conda/envs/main/lib/tcl8 /opt/conda/envs/main/lib/tk8 2>/dev/null || true
rm -f /opt/conda/envs/main/lib/libtk8.6.so /opt/conda/envs/main/lib/libtcl8.6.so 2>/dev/null || true
rm -f /opt/conda/envs/main/bin/tclsh* /opt/conda/envs/main/bin/wish* 2>/dev/null || true
echo "[CLEAN] Removing nbclassic files (legacy Notebook v6 frontend)..."
find /opt/conda/envs/main/lib/python3.*/site-packages -type d -name "nbclassic*" -exec rm -rf {} + 2>/dev/null || true
rm -f /opt/conda/envs/main/bin/jupyter-nbclassic 2>/dev/null || true
echo "[OK] Unnecessary packages removed from main env (same layer)"

# ── Step 3: 删除pandoc-server/pandoc-lua（pandoc CLI够用）+ 删除测试套件 ──
echo "[CLEAN] Removing pandoc-server and pandoc-lua binaries..."
rm -f /opt/conda/envs/main/bin/pandoc-server /opt/conda/envs/main/bin/pandoc-lua 2>/dev/null || true
echo "[CLEAN] Removing test directories from main env..."
find /opt/conda/envs/main/lib/python3.*/test -type d -name test -prune -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/lib/python3.*/site-packages -type d -name tests -prune -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/share/jupyter -path "*/staging/node_modules" -prune -exec rm -rf {} + 2>/dev/null || true
echo "[OK] Unused binaries and test dirs removed"

# ── Step 4: 清理.pyc文件（包删除后清理） ──
echo "[CLEAN] Removing .pyc/__pycache__ from main + base env..."
find /opt/conda/envs/main -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
find /opt/conda/envs/main -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "${CONDA_DIR}" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
find "${CONDA_DIR}" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
echo "[OK] .pyc files cleaned"

# ── Step 5: Strip main env二进制文件（同层strip，避免COW，必须在所有包操作之后） ──
echo "[STRIP] Stripping main env executables and .so libraries (same-layer, no COW)..."
# Main Python binary and other executables (use --strip-unneeded to preserve dynamic symbols for C extensions)
find /opt/conda/envs/main/bin -type f -executable \
    ! -name "*.py" ! -name "*.sh" ! -name "*.rb" ! -name "*.pl" \
    -exec strip --strip-unneeded {} \; 2>/dev/null || true
# Shared libraries
find /opt/conda/envs/main/lib -name "*.so*" -type f \
    -exec strip --strip-unneeded {} \; 2>/dev/null || true
# Node.js binaries
if [ -f /opt/conda/envs/main/bin/node ]; then
    strip --strip-all /opt/conda/envs/main/bin/node 2>/dev/null || true
fi
echo "[OK] main env binaries stripped"

# ── 设置main env权限（同层，避免COW） ──
echo "[PERM] Setting permissions on main env..."
chown -R root:root /opt/conda/envs/main 2>/dev/null || true
chmod -R a+rX /opt/conda/envs/main 2>/dev/null || true
find /opt/conda/envs/main/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Main env permissions set (same-layer)"

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "[TIMER] Stage 4b/4c (mamba create main env) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"
echo '[OK] Stage 4b complete'
