#!/bin/bash
# =============================================================================
# Stage 4c/4c: pip镜像配置 + Jupyter kernel注册 + free-threading验证
# 变化频率：中高（pip配置、验证逻辑调整时改）；此层修改不触发4a/4b重跑
# 关键改进：SOABI动态检测，不再硬编码cp314t，Python版本升级无需修改验证逻辑
# =============================================================================
set -e

# 防止pip/jupyter/python验证过程中生成.pyc文件
export PYTHONDONTWRITEBYTECODE=1

echo "=== Stage 4c/4c: pip mirrors + kernel registration + free-threading verify ==="
_STAGE_START=$(date +%s)

. "${CONDA_DIR}/etc/profile.d/conda.sh"

# ── 配置 PyPI 镜像（root + base + main 环境，devuser 在 Stage 5/7 创建后配置） ──
echo "[ACTION] Configuring pip mirrors..."
mkdir -p /root/.config/pip
case "${PIP_MIRROR}" in
    aliyun)
        echo "[INFO] Configuring pip for Aliyun mirror"
        PIP_INDEX_URL="https://mirrors.aliyun.com/pypi/simple/"
        PIP_TRUSTED_HOST="mirrors.aliyun.com"
        ;;
    tuna)
        echo "[INFO] Configuring pip for Tsinghua TUNA mirror"
        PIP_INDEX_URL="https://pypi.tuna.tsinghua.edu.cn/simple/"
        PIP_TRUSTED_HOST="pypi.tuna.tsinghua.edu.cn"
        ;;
    *)
        echo "[INFO] Configuring pip for official PyPI"
        PIP_INDEX_URL="https://pypi.org/simple/"
        PIP_TRUSTED_HOST=""
        ;;
esac
# 写入 root 全局 pip.conf
printf '%s\n' \
    '[global]' \
    "index-url = ${PIP_INDEX_URL}" \
    "retries = 5" \
    "timeout = 60" \
    > /root/.config/pip/pip.conf
if [ -n "${PIP_TRUSTED_HOST}" ]; then
    printf '%s\n' "trusted-host = ${PIP_TRUSTED_HOST}" >> /root/.config/pip/pip.conf
fi
# 配置 conda base 环境 pip
if [ "${PIP_MIRROR}" = "aliyun" ]; then
    "${CONDA_DIR}/bin/pip" config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    "${CONDA_DIR}/bin/pip" config set global.trusted-host mirrors.aliyun.com
elif [ "${PIP_MIRROR}" = "tuna" ]; then
    "${CONDA_DIR}/bin/pip" config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    "${CONDA_DIR}/bin/pip" config set global.trusted-host pypi.tuna.tsinghua.edu.cn
fi
# 配置 main 环境 pip
/opt/conda/envs/main/bin/pip config set global.index-url "${PIP_INDEX_URL}"
if [ -n "${PIP_TRUSTED_HOST}" ]; then
    /opt/conda/envs/main/bin/pip config set global.trusted-host "${PIP_TRUSTED_HOST}"
fi
echo "[OK] pip mirrors configured (root + base + main; devuser will be configured in Stage 5/7)"
# 将 PIP 配置变量导出到临时文件，供 Stage 5/7 使用
echo "PIP_INDEX_URL=${PIP_INDEX_URL}" > /tmp/pip-config.env
echo "PIP_TRUSTED_HOST=${PIP_TRUSTED_HOST}" >> /tmp/pip-config.env

# ── 注册main环境为Jupyter默认kernel（动态获取Python版本显示名） ──
_MAIN_PY_VER=$(/opt/conda/envs/main/bin/python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
/opt/conda/envs/main/bin/python -m ipykernel install --name main --display-name "Python ${_MAIN_PY_VER} (free-threading)" --prefix=/opt/conda/envs/main 2>&1
echo "[OK] Jupyter kernel registered: Python ${_MAIN_PY_VER} (free-threading)"

# ── 验证free-threading构建（动态SOABI检测，适配未来Python版本） ──
/opt/conda/envs/main/bin/python -c "
import sys, sysconfig
ft = sysconfig.get_config_var('Py_GIL_DISABLED')
soabi = sysconfig.get_config_var('SOABI') or ''
assert ft == 1, f'Expected free-threading build, got Py_GIL_DISABLED={ft}'
assert 't' in soabi, f'Expected free-threading SOABI (containing t suffix), got {soabi}'
py_ver = '.'.join(map(str, sys.version_info[:2]))
print(f'[OK] Free-threading verified: Python {sys.version.split()[0]}, SOABI={soabi}, GIL disabled by default')
"

# ── main环境激活将在 Stage 5/7 通过 conda-init.sh 统一配置 ──
echo "[INFO] main environment activation will be configured via conda-init.sh in Stage 5/7"

# ── 验证安装 ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [VERIFY] Conda + Python (main env) + Jupyter   │"
echo "└─────────────────────────────────────────────────┘"
"${CONDA_DIR}/bin/conda" --version
/opt/conda/envs/main/bin/python --version
/opt/conda/envs/main/bin/jupyter --version
echo "  - conda dir: ${CONDA_DIR}"
echo "  - main env python: /opt/conda/envs/main/bin/python"
echo "  - main env jupyter: $(/opt/conda/envs/main/bin/jupyter --version 2>&1 | head -1)"
echo "  - default solver: libmamba"

# ── Conda缓存清理（同层） ──
echo "[CLEAN] Cleaning conda caches..."
conda clean -y -a -f -q 2>/dev/null || true
# 只设置stage4c新增文件的权限（kernel注册文件），不递归chmod整个/opt/conda（避免COW）
chmod -R a+rX /opt/conda/envs/main/share/jupyter/kernels 2>/dev/null || true
echo "[OK] Conda caches cleaned (same-layer)"

# ── 清理pip/jupyter/验证过程中可能生成的.pyc文件（最后清理） ──
echo "[CLEAN] Removing .pyc/__pycache__ after all operations..."
find /opt/conda/envs/main -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
find /opt/conda/envs/main -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find "${CONDA_DIR}" -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
find "${CONDA_DIR}" -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
echo "[OK] .pyc files cleaned in same layer as stage4c"

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "S4=$_NOW" >> /tmp/.build-timer
echo "[TIMER] Stage 4/7 (conda+libmamba+jupyter) sub-stages total: see 4a/4b/4c above | Cumulative: ${_TOTAL}s"
echo '[OK] Stage 4 complete'
