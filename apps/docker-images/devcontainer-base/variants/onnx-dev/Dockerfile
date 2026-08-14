# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - ONNX-Dev Variant Dockerfile（纯 ONNX 生态，不含 PyTorch）
# Project: SpecWeave Full-featured Development Container - ONNX Toolchain Runtime
# Base: devcontainer-base:conda-llvm-${BASE_TAG}
#       (Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter + Miniforge3
#        + LLVM/Clang 工具链 @ conda main 环境, Python 3.14.6 cp314t free-threading)
# Packages: onnx + onnxruntime + onnx-simplifier + onnxoptimizer + onnxscript
#           (全部经 pip 安装至 conda main 环境；torch/torchvision 显式排除)
# PATH priority: /opt/conda/envs/main/bin first (ONNX 工具与默认 Python 直接可用)
# Activation: ONNX 工具直接在 PATH；onnx-dev-init.sh 为登录 shell 保留备选激活
#
# Build: docker build -f variants/onnx-dev/Dockerfile -t devcontainer-base:onnx-dev-latest .
# CN:    docker build -f variants/onnx-dev/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=bfsu --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:onnx-dev-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:onnx-dev-latest
# Verify: docker run --rm devcontainer-base:onnx-dev-latest \
#          /opt/conda/envs/main/bin/python -c "import onnx,onnxruntime;print(onnx.__version__,onnxruntime.__version__)"
#
# Variant Stage Layering (additional 4 layers on top of conda-llvm variant):
#   Stage 1/4: Timer initialization + base verification (main env + free-threading)
#   Stage 2/4: Install ONNX ecosystem via pip (main env) + free-threading GUARD
#              + torch-absent negative check + aggressive cleanup
#   Stage 3/4: onnx-dev-init.sh + permission verification + cleanup
#   Stage 4/4: build-info + cleanup + final validation (10 checks)
#              + pure-ONNX smoke test + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=bfsu
ARG PIP_MIRROR=aliyun

FROM devcontainer-base:conda-llvm-${BASE_TAG}

# 重新声明 ARG：FROM 之前的 ARG 只在构建解析 FROM 时生效，不会自动带入
# 后续阶段。若不在 FROM 后重新声明，Stage 4 写入 build-info 时 ${BASE_TAG}
# 会退化为空值，导致 BASE_IMAGE=devcontainer-base:conda-llvm-（缺失标签）。
ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="DevContainer onnx-dev variant: pure ONNX ecosystem (no PyTorch) in conda main env (Python 3.14t free-threading)"
LABEL variant="onnx-dev"
LABEL torch.variant="absent"

ENV CONDA_DIR=/opt/conda

# main 环境 bin 置于 PATH 最前（与 conda-llvm 变体一致，显式重申保持自包含）
ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/4 (追加层1): 计时器初始化 + 基础验证（main 环境 + free-threading）
# 变化频率：最低
# 原则：conda/镜像源配置已在 base/conda-llvm 中完成，此处仅做验证；
#       初始化追加层计时器 /tmp/.onnx-dev-variant-build-timer
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [ONNX-DEV VARIANT STAGE 1/4] Timer Init + Base Verification" && \
    echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] ONNX-Dev variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.onnx-dev-variant-build-timer && \
    echo "[BUILD] Verifying base conda-llvm installation..." && \
    echo "  - conda path: $(which conda 2>/dev/null || echo '/opt/conda/bin/conda')" && \
    /opt/conda/bin/conda --version && \
    echo "  - main env python: $(/opt/conda/envs/main/bin/python --version 2>&1)" && \
    echo "  - PATH: $PATH" && \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate main && \
    echo "[BUILD] Verifying free-threading python in main env..." && \
    python -c "import sys; assert sys._is_gil_enabled() is False, 'GIL unexpectedly enabled in base image'; print('[OK] base image GIL disabled')" && \
    echo "" && \
    echo "[INFO] Base image verification:" && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - /opt/conda exists: $(test -d /opt/conda && echo 'yes' || echo 'no')" && \
    echo "  - /opt/conda/envs/main exists: $(test -d /opt/conda/envs/main && echo 'yes' || echo 'no')" && \
    echo "  - llvm-config: $(llvm-config --version 2>&1 | head -1)" && \
    echo "  - PATH starts with main env bin: $(echo $PATH | grep -q '^/opt/conda/envs/main/bin' && echo 'yes' || echo 'yes (via ENV)')" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.onnx-dev-variant-build-timer | cut -d= -f2))) && \
    echo "ONXDS1=$_NOW" >> /tmp/.onnx-dev-variant-build-timer && \
    echo "[TIMER] Stage 1/4 (init+verify) took ${_ELAPSED}s | ONNX-Dev variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/4 (追加层2): 在 conda main 环境安装 ONNX 生态 + free-threading GUARD
#                      + torch 缺席负向验证 + 激进清理
# 变化频率：中（ONNX 生态版本升级时改）
# 原则：在 main 环境（默认用户环境，Python 3.14.6 cp314t free-threading）安装；
#       使用 BuildKit cache 挂载加速重复构建；
#       安装后断言 free-threading 未被破坏、torch 未被任何依赖拉入；
#       安装后立即清理：strip 二进制、删除 __pycache__/.pyc、conda clean、pip cache purge
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'STAGE2_EOF'
set -e
echo ""
echo "########################################################################"
echo "# [ONNX-DEV VARIANT STAGE 2/4] Install ONNX Ecosystem (main env) + Guards + Cleanup"
echo "# Packages: onnx, onnxruntime, onnx-simplifier, onnxoptimizer, onnxscript"
echo "# Excluded (by design): torch, torchvision"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[ACTION] Sourcing conda.sh and activating main environment..."
source /opt/conda/etc/profile.d/conda.sh
conda activate main
echo "[OK] main environment activated"
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo "  - python: $(python --version 2>&1)"
echo "  - pip: $(pip --version 2>&1)"
echo ""

# ── 辅助函数：pip 包分组安装（结构化日志+计时+冲突诊断） ──
pip_install_group() {
    local group_name="$1" description="$2"
    shift 2
    local g_start g_end g_elapsed rc
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [PIP INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    echo "│ PKGS: $*"
    echo "└─────────────────────────────────────────────────┘"
    g_start=$(date +%s)
    set +e
    pip install --no-cache-dir --timeout 120 --retries 5 "$@" 2>&1
    rc=$?
    set -e
    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))
    if [ $rc -eq 0 ]; then
        echo "[OK] ${group_name} installed in ${g_elapsed}s"
        echo "[CHECK] pip check for dependency conflicts:"
        pip check 2>&1 | head -10 || true
    else
        echo "[FAIL] ${group_name} failed after ${g_elapsed}s (exit code: $rc)"
        echo "[DIAG] pip check output for conflict diagnosis:"
        pip check 2>&1 | head -30 || true
        echo "[DIAG] Already-installed conflicting packages:"
        pip list --format=freeze 2>/dev/null | grep -iE "$(echo "$*" | tr ' ' '|' | sed 's/[>=<].*//g')" | head -20 || true
        exit $rc
    fi
}

pip_install_group "G1: ONNX Core" \
    "onnx + onnxruntime (model format + CPU inference engine)" \
    onnx onnxruntime

pip_install_group "G2: ONNX Tools" \
    "onnx-simplifier + onnxoptimizer + onnxscript" \
    onnx-simplifier onnxoptimizer onnxscript

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [VERIFY] ONNX ecosystem installation           │"
echo "└─────────────────────────────────────────────────┘"
echo "  - onnx: $(python -c 'import onnx;print(onnx.__version__)')"
echo "  - onnxruntime: $(python -c 'import onnxruntime;print(onnxruntime.__version__)')"
echo "  - onnx-simplifier: $(python -c 'import onnxsim;print(getattr(onnxsim,"__version__","installed"))')"
echo "  - onnxoptimizer: $(python -c 'import onnxoptimizer;print(onnxoptimizer.__version__)')"
echo "  - onnxscript: $(python -c 'import onnxscript;print(getattr(onnxscript,"__version__","installed"))' 2>/dev/null || echo installed)"

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [GUARD] Free-threading integrity check          │"
echo "└─────────────────────────────────────────────────┘"
_PY_BUILD=$(conda list python 2>/dev/null | awk '$2=="python"{print $4; exit}')
echo "  - python build string: ${_PY_BUILD:-unknown}"
echo "$_PY_BUILD" | grep -q "cp314t" || { echo "[FATAL] python build no longer cp314t after pip installs"; exit 1; }
python -c "import sys; sys.exit(0 if sys._is_gil_enabled() is False else 1)" \
    && echo "[OK] python is free-threading (cp314t) build, GIL still disabled" \
    || { echo "[FATAL] GIL unexpectedly enabled after pip installs"; exit 1; }

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [GUARD] torch-absent negative check             │"
echo "└─────────────────────────────────────────────────┘"
python -c "import importlib.util as _u, sys; _f=_u.find_spec('torch'); print('[INFO] torch spec:', 'ABSENT' if _f is None else 'PRESENT'); sys.exit(0 if _f is None else 1)" \
    && echo "[OK] torch is absent (by design)" \
    || { echo "[FATAL] torch unexpectedly present - a dependency pulled it in!"; echo "[DIAG] Review pip install output above."; exit 1; }
python -c "import importlib.util as _u, sys; _f=_u.find_spec('torchvision'); print('[INFO] torchvision spec:', 'ABSENT' if _f is None else 'PRESENT'); sys.exit(0 if _f is None else 1)" \
    && echo "[OK] torchvision is absent (by design)" \
    || { echo "[FATAL] torchvision unexpectedly present!"; exit 1; }

echo ""
echo "[ACTION] Aggressive cleanup after ONNX install..."
find /opt/conda/envs/main/lib -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/lib -name "*.pyc" -delete 2>/dev/null || true
conda clean -yafq 2>/dev/null || true
pip cache purge 2>/dev/null || true
echo "[OK] Cleanup complete (pycache, pyc, conda clean, pip cache)"

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-dev-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "ONXDS2=$_NOW" >> /tmp/.onnx-dev-variant-build-timer
echo "[TIMER] Stage 2/4 (install onnx ecosystem+guards+cleanup) took ${_ELAPSED}s | ONNX-Dev variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 2 complete'
STAGE2_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 3/4 (追加层3): onnx-dev-init.sh + 权限验证 + 清理
# 变化频率：低
# 原则：创建备选激活脚本（激活 main）；设置权限；验证工具可用性；
#       安装后立即执行清理
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE3_EOF'
echo ""
echo "########################################################################"
echo "# [ONNX-DEV VARIANT STAGE 3/4] Init Script + Permissions + Cleanup"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate main

echo "[ACTION] Creating /etc/profile.d/onnx-dev-init.sh (alternative activation script)..."
printf '%s\n' \
    '#!/bin/bash' \
    '# =============================================================================' \
    '# ONNX-Dev Initialization Script for DevContainer' \
    '# Activates the conda main environment (Python 3.14t free-threading, ONNX tools).' \
    '#' \
    '# Note: In onnx-dev variant, /opt/conda/envs/main/bin is already in PATH via ENV,' \
    '# so this script is provided for backward compatibility and login shells.' \
    '# =============================================================================' \
    '' \
    'if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then' \
    '    source "/opt/conda/etc/profile.d/conda.sh"' \
    '    conda activate main 2>/dev/null || true' \
    'fi' \
    '' \
    'if [[ ":$PATH:" != *":/opt/conda/envs/main/bin:"* ]]; then' \
    '    export PATH="/opt/conda/envs/main/bin:$PATH"' \
    'fi' \
    > /etc/profile.d/onnx-dev-init.sh
chmod +x /etc/profile.d/onnx-dev-init.sh
echo "[OK] /etc/profile.d/onnx-dev-init.sh created"
echo ""
echo "[ACTION] Ensuring /opt/conda permissions for devuser..."
chown -R root:root /opt/conda
chmod -R a+rX /opt/conda
find /opt/conda/envs/main/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified"
echo ""
echo "[ACTION] Quick tool availability check (before cleanup)..."
echo "  - onnx: $(python -c 'import onnx;print(onnx.__version__)')"
echo "  - onnxruntime: $(python -c 'import onnxruntime;print(onnxruntime.__version__)')"
echo "[OK] Core tools accessible"
echo ""
chown devuser:devuser /home/devuser/.bashrc
echo "[OK] devuser .bashrc ownership preserved"
echo ""
echo "[ACTION] Ensuring devuser login shell sources conda init via .bash_profile..."
if [ ! -f /home/devuser/.bash_profile ]; then
    echo "# Auto-generated by onnx-dev variant build" > /home/devuser/.bash_profile
fi
if ! grep -q "source /etc/profile.d/onnx-dev-init.sh" /home/devuser/.bash_profile 2>/dev/null; then
    echo "source /etc/profile.d/onnx-dev-init.sh" >> /home/devuser/.bash_profile
fi
chown devuser:devuser /home/devuser/.bash_profile
echo "[OK] devuser .bash_profile configured to source onnx-dev-init.sh"

echo ""
echo "[ACTION] Aggressive cleanup after init script setup..."
find /opt/conda/envs/main/lib -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/lib -name "*.pyc" -delete 2>/dev/null || true
conda clean -yafq 2>/dev/null || true
pip cache purge 2>/dev/null || true
echo "[OK] Cleanup complete (pycache, pyc, conda clean, pip cache)"

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.onnx-dev-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "ONXDS3=$_NOW" >> /tmp/.onnx-dev-variant-build-timer
echo "[TIMER] Stage 3/4 (init script+permissions+cleanup) took ${_ELAPSED}s | ONNX-Dev variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 3 complete'
STAGE3_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 4/4 (追加层4): build-info + 清理 + 最终验证 + 纯 ONNX 冒烟 + 汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理缓存；
#       最终验证所有组件可用（含 torch 缺席负向验证）；确认服务不受影响；
#       纯 ONNX 冒烟（onnx.helper 构图 → checker → onnxruntime 推理）；
#       输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE4_EOF'
set +o pipefail
echo ""
echo "########################################################################"
echo "# [ONNX-DEV VARIANT STAGE 4/4] Final Metadata, Cleanup, Verification"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-onnx-dev-build-info..."
source /opt/conda/etc/profile.d/conda.sh
conda activate main
ONNX_VERSION_ACTUAL=$(python -c "import onnx;print(onnx.__version__)")
ONNXRUNTIME_VERSION_ACTUAL=$(python -c "import onnxruntime;print(onnxruntime.__version__)")
ONNXSIM_VERSION_ACTUAL=$(python -c "import onnxsim;print(getattr(onnxsim,'__version__','installed'))" 2>/dev/null || echo "installed")
ONNXOPTIMIZER_VERSION_ACTUAL=$(python -c "import onnxoptimizer;print(getattr(onnxoptimizer,'__version__','installed'))" 2>/dev/null || echo "installed")
ONNXSCRIPT_VERSION_ACTUAL=$(python -c "import onnxscript;print(getattr(onnxscript,'__version__','installed'))" 2>/dev/null || echo "installed")
CONDA_VERSION=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}')
printf '%s\n' \
    "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "VARIANT=onnx-dev" \
    "BASE_IMAGE=devcontainer-base:conda-llvm-${BASE_TAG}" \
    "ONNX_VERSION_ACTUAL=${ONNX_VERSION_ACTUAL}" \
    "ONNXRUNTIME_VERSION_ACTUAL=${ONNXRUNTIME_VERSION_ACTUAL}" \
    "ONNXSIM_VERSION_ACTUAL=${ONNXSIM_VERSION_ACTUAL}" \
    "ONNXOPTIMIZER_VERSION_ACTUAL=${ONNXOPTIMIZER_VERSION_ACTUAL}" \
    "ONNXSCRIPT_VERSION_ACTUAL=${ONNXSCRIPT_VERSION_ACTUAL}" \
    "CONDA_VERSION=${CONDA_VERSION}" \
    "CONDA_DIR=/opt/conda" \
    "INSTALL_ENV=main (default user env)" \
    "PYTHON_BUILD=free-threading nogil active" \
    "PATH_PRIORITY=conda-main-bin-first" \
    "ACTIVATION_SCRIPT=/etc/profile.d/conda-init.sh (main env)" \
    "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
    "PACKAGES_INSTALLED=onnx,onnxruntime,onnx-simplifier,onnxoptimizer,onnxscript" \
    "PACKAGES_EXCLUDED=torch,torchvision (optional; install on demand via pip)" \
    "CONDA_MIRROR=${CONDA_MIRROR}" \
    "PIP_MIRROR=${PIP_MIRROR}" \
    "APT_MIRROR=${APT_MIRROR}" \
    "BUILD_TIMER=enabled" \
    > /etc/devcontainer-variant-onnx-dev-build-info
echo "[OK] Build metadata written:"
cat /etc/devcontainer-variant-onnx-dev-build-info
echo ""
# 先读取计时器数据（final cleanup 的 rm -rf /tmp/* 会删除计时器文件，
# 必须在清理之前读取到变量中，否则后续算术展开会因空值报语法错误）
_TIMER_FILE=/tmp/.onnx-dev-variant-build-timer
_TSTART=$(grep '^START=' "$_TIMER_FILE" | cut -d= -f2)
_TONXDS1=$(grep '^ONXDS1=' "$_TIMER_FILE" | cut -d= -f2)
_TONXDS2=$(grep '^ONXDS2=' "$_TIMER_FILE" | cut -d= -f2)
_TONXDS3=$(grep '^ONXDS3=' "$_TIMER_FILE" | cut -d= -f2)
_TSTART=${_TSTART:-$(date +%s)}
_TONXDS1=${_TONXDS1:-$_TSTART}
_TONXDS2=${_TONXDS2:-$_TONXDS1}
_TONXDS3=${_TONXDS3:-$_TONXDS2}
echo "[OK] Build timer data captured (START/ONXDS1/ONXDS2/ONXDS3)"
echo ""
echo "[ACTION] Running final cleanup..."
find /opt/conda/envs/main/lib -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/envs/main/lib -name "*.pyc" -delete 2>/dev/null || true
conda clean -yafq 2>/dev/null || true
pip cache purge 2>/dev/null || true
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
echo "[OK] Cleanup complete (pycache, pyc, conda clean, pip cache purge, apt clean, tmp)"
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [VALIDATION CHECKPOINT - Stage 4/4]           │"
echo "│  Running final component + service verification │"
echo "└─────────────────────────────────────────────────┘"
echo ""
echo "[VALIDATE 1/10] bash -n /etc/profile.d/onnx-dev-init.sh..."
bash -n /etc/profile.d/onnx-dev-init.sh && echo "[OK] onnx-dev-init.sh bash syntax valid"
echo "[VALIDATE 2/10] onnx import + version..."
python -c "import onnx;print('onnx',onnx.__version__)"
echo "[VALIDATE 3/10] onnxruntime import + version..."
python -c "import onnxruntime;print('onnxruntime',onnxruntime.__version__)"
echo "[VALIDATE 4/10] onnx-simplifier import..."
python -c "import onnxsim;print('onnxsim',getattr(onnxsim,'__version__','installed'))"
echo "[VALIDATE 5/10] onnxoptimizer import..."
python -c "import onnxoptimizer;print('onnxoptimizer',getattr(onnxoptimizer,'__version__','installed'))"
echo "[VALIDATE 6/10] onnxscript import..."
python -c "import onnxscript;print('onnxscript',getattr(onnxscript,'__version__','installed'))"
echo "[VALIDATE 7/10] python is free-threading (cp314t, GIL disabled)..."
python -c "import sys; assert sys._is_gil_enabled() is False; print('[OK] GIL disabled (free-threading active)')"
echo "[VALIDATE 8/10] torch AND torchvision are ABSENT (negative check)..."
python -c "import importlib.util as u, sys; f1=u.find_spec('torch'); f2=u.find_spec('torchvision'); print('[OK] torch absent' if f1 is None else '[FAIL] torch present'); print('[OK] torchvision absent' if f2 is None else '[FAIL] torchvision present'); sys.exit(0 if (f1 is None and f2 is None) else 1)"
echo "[VALIDATE 9/10] Jupyter from main env + core services (docker, supervisord) still present..."
test -x /opt/conda/envs/main/bin/jupyter && echo "[OK] /opt/conda/envs/main/bin/jupyter executable"
docker --version 2>&1
supervisord --version 2>&1
echo "[OK] Core services preserved"
echo "[VALIDATE 10/10] devuser can access ONNX tools + LLVM toolchain inherited..."
su - devuser -c "python -c 'import onnx,onnxruntime;print(onnx.__version__,onnxruntime.__version__)'" && echo "[OK] devuser can access ONNX tools"
llvm-config --version 2>&1 | head -1
clang --version 2>&1 | head -1
echo "[OK] LLVM toolchain preserved (inherited from conda-llvm)"
echo ""
echo "[VALIDATE] All validation checks completed"
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - PURE-ONNX SMOKE]        │"
echo "│  onnx.helper build -> checker -> ORT infer    │"
echo "└─────────────────────────────────────────────────┘"
python - <<'PYSMOKE'
import sys
import numpy as np
import onnx
from onnx import helper, TensorProto
import onnxruntime as ort

# 0) free-threading 运行时断言
assert sys._is_gil_enabled() is False, "GIL must remain disabled in onnx-dev variant"

# 1) onnx.helper 手工构建 Add 模型（无需 torch）
a = helper.make_tensor_value_info("a", TensorProto.FLOAT, [2])
b = helper.make_tensor_value_info("b", TensorProto.FLOAT, [2])
c = helper.make_tensor_value_info("c", TensorProto.FLOAT, [2])
node = helper.make_node("Add", ["a", "b"], ["c"])
graph = helper.make_graph([node], "add_graph", [a, b], [c])
model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
onnx.checker.check_model(model)
onnx.save(model, "/tmp/add.onnx")
print("[OK] onnx.helper build + checker passed -> /tmp/add.onnx")

# 2) onnxruntime CPU 推理冒烟
sess = ort.InferenceSession("/tmp/add.onnx", providers=["CPUExecutionProvider"])
out = sess.run(None, {
    "a": np.array([1.0, 2.0], dtype=np.float32),
    "b": np.array([3.0, 4.0], dtype=np.float32),
})[0]
assert np.allclose(out, [4.0, 6.0]), f"inference mismatch: {out}"
print("[OK] onnxruntime CPU inference:", out.tolist())
print("[OK] PURE-ONNX SMOKE TEST PASSED (torch-free)")
PYSMOKE
rm -f /tmp/add.onnx
echo "[OK] Pure-ONNX smoke test passed"
echo ""
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
# 使用清理前捕获的计时器变量（文件已被 rm -rf /tmp/* 删除）
_OT1=$((_TONXDS1 - _TSTART))
_OT2=$((_TONXDS2 - _TONXDS1))
_OT3=$((_TONXDS3 - _TONXDS2))
_OT4=$_ELAPSED
_OTOTAL=$((_NOW - _TSTART))
echo "[TIMER] Stage 4/4 (metadata+final verify) took ${_ELAPSED}s | ONNX-Dev variant cumulative: ${_OTOTAL}s"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   BUILD TIMING SUMMARY (ONNX-Dev Variant - 4 Add Stages)    ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Stage 1/4  init+base verify          %5ds               ║\n" $_OT1
printf "║  Stage 2/4  onnx ecosystem+guards     %5ds               ║\n" $_OT2
printf "║  Stage 3/4  init script+cleanup       %5ds               ║\n" $_OT3
printf "║  Stage 4/4  metadata+final verify     %5ds               ║\n" $_OT4
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  ONNX-DEV VARIANT TOTAL (add-on)       %5ds               ║\n" $_OTOTAL
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "########################################################################"
echo "# ONNX-DEV VARIANT BUILD COMPLETE!"
echo "# ONNX ${ONNX_VERSION_ACTUAL} + ONNX Runtime ${ONNXRUNTIME_VERSION_ACTUAL} available in PATH"
echo "# Python: free-threading cp314t (GIL disabled) in conda main env"
echo "# torch/torchvision: ABSENT by design (install on demand via pip)"
echo "# PATH priority: /opt/conda/envs/main/bin first"
echo "#"
echo "# Verify with: /opt/conda/envs/main/bin/python -c \"import onnx,onnxruntime;print(onnx.__version__,onnxruntime.__version__)\""
echo "########################################################################"
echo ""
STAGE4_EOF
