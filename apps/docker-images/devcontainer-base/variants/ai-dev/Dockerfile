# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - AI Dev Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - AI/ML/NLP Full-Stack
# Base: devcontainer-base:onnx-quantized-${BASE_TAG} (pure ONNX quantization toolkit, main env free-threading, no PyTorch)
# Ecosystem: 50+ Python packages covering NLP, data, viz, document, web, database
# Jupyter: JupyterLab >=4.4 + notebook >=7.3, generic "Python 3 (AI Dev)" kernel
# PATH priority: /opt/conda/bin first (AI tools directly available in base conda env)
#
# Build: docker build -f variants/ai-dev/Dockerfile -t devcontainer-base:ai-dev-latest .
# CN:    docker build -f variants/ai-dev/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:ai-dev-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:ai-dev-latest
# Verify: docker run --rm devcontainer-base:ai-dev-latest \
#          /opt/conda/bin/python -c "import transformers,datasets,fastapi,pandas;print('ai-dev OK')"
#
# Variant Stage Layering (3 additional layers on top of onnx-quantized variant):
#   Stage 1/3: Base verification + timer initialization
#   Stage 2/3: Install full AI/ML/NLP Python ecosystem (50+ packages)
#   Stage 3/3: Jupyter kernel + build-info + cleanup + validation + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun

FROM devcontainer-base:onnx-quantized-${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR

LABEL maintainer="SpecWeave"
LABEL description="DevContainer ai-dev variant: full AI/ML/NLP Python ecosystem (50+ packages), JupyterLab 4.x, generic AI kernel"
LABEL variant="ai-dev"
LABEL ecosystem="nlp,transformers,data-science,document-processing,web-api,database"

ENV CONDA_DIR=/opt/conda

ENV PATH=/opt/conda/bin:${PATH}

ENV OMP_NUM_THREADS=4
ENV OPENBLAS_NUM_THREADS=1
ENV OMP_WAIT_POLICY=PASSIVE
ENV KMP_DUPLICATE_LIB_OK=TRUE

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/3 (追加层1): 基础验证 + 计时器初始化
# 变化频率：最低
# 原则：验证 onnx-quantized 基础组件；初始化追加层计时器
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE1_EOF'
echo ""
echo "########################################################################"
echo "# [AI-DEV VARIANT STAGE 1/3] Base Verification + Timer Init"
echo "# CONDA_MIRROR=${CONDA_MIRROR}, PIP_MIRROR=${PIP_MIRROR}"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[TIMER] AI-Dev variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "START=$_STAGE_START" > /tmp/.ai-dev-variant-build-timer
echo "[BUILD] Verifying base onnx-quantized installation..."
echo "  - torch: $(/opt/conda/envs/main/bin/python -c 'import torch;print(torch.__version__)' 2>/dev/null || echo 'not found (by design)')"
echo "  - onnx: $(/opt/conda/envs/main/bin/python -c 'import onnx;print(onnx.__version__)' 2>/dev/null || echo 'not found')"
echo "  - onnxruntime: $(/opt/conda/envs/main/bin/python -c 'import onnxruntime;print(onnxruntime.__version__)' 2>/dev/null || echo 'not found')"
echo "  - quantization: $(/opt/conda/envs/main/bin/python -c 'from onnxruntime.quantization import quantize_dynamic;print("available")' 2>/dev/null || echo 'not found')"
echo "  - conda: $(/opt/conda/bin/conda --version 2>&1 | head -1)"
echo "  - python: $(python --version 2>&1)"
echo "  - PATH: $PATH"
echo ""
echo "[BUILD] Verifying devuser + services preserved..."
echo "  - devuser exists: $(id devuser 2>&1 | head -1)"
echo "  - /opt/conda exists: $(test -d /opt/conda && echo 'yes' || echo 'no')"
echo "  - /opt/venv removed: $(test ! -d /opt/venv && echo 'yes' || echo 'no')"
echo "  - docker: $(docker --version 2>&1 | head -1)"
echo "  - supervisord: $(supervisord --version 2>&1 | head -1)"
echo ""
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_TOTAL=$((_NOW - $(grep '^START=' /tmp/.ai-dev-variant-build-timer | cut -d= -f2)))
echo "AIS1=$_NOW" >> /tmp/.ai-dev-variant-build-timer
echo "[TIMER] Stage 1/3 (base verify+init) took ${_ELAPSED}s | AI-Dev variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 1 complete'
STAGE1_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 2/3 (追加层2): 安装完整 AI/ML/NLP Python 生态系统
# 变化频率：中（包版本升级时改）
# 原则：在 base conda 环境安装全部 Python 包；构建期 PIP_USER=0
#       确保写入 /opt/conda（root属主，全局可读）；使用 BuildKit cache 加速
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/root/.cache/pip,sharing=locked \
    <<'STAGE2_EOF'
echo ""
echo "########################################################################"
echo "# [AI-DEV VARIANT STAGE 2/3] Install Full AI/ML/NLP Ecosystem"
echo "# Packages (50+): build tools, NLP/transformers, data, viz, document,"
echo "#                 web/API, database clients, utilities"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate base
echo "[OK] base environment activated"
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo ""

echo "[ACTION] Setting PIP_USER=0 for build-time (write to /opt/conda)..."
export PIP_USER=0

if [ "${PIP_MIRROR}" = "aliyun" ]; then
    pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
    pip config set global.trusted-host mirrors.aliyun.com
    echo "[CONFIG] Using Aliyun PyPI mirror"
elif [ "${PIP_MIRROR}" = "tuna" ]; then
    pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
    pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
    echo "[CONFIG] Using TUNA PyPI mirror"
fi

echo "[ACTION] Upgrading pip/setuptools/wheel..."
pip install --no-cache-dir --timeout 120 --retries 5 --upgrade pip setuptools wheel
echo "[OK] pip/setuptools/wheel upgraded"
echo "  - pip: $(pip --version 2>&1 | awk '{print $2}')"
echo "  - setuptools: $(python -c 'import setuptools;print(setuptools.__version__)' 2>/dev/null || echo unknown)"
echo "  - wheel: $(python -c 'import wheel;print(wheel.__version__)' 2>/dev/null || echo unknown)"
echo ""

# ── Helper: install a package group with structured logging ──
# Usage: pip_install_group "GROUP NAME" "description" pkg1 "pkg2>=1.0" ...
pip_install_group() {
    local group_name="$1" description="$2"
    shift 2
    local g_start g_end g_elapsed rc
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [INSTALL] ${group_name}"
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

pip_install_group "G1: Build Tools" "scikit-build-core, nuitka, invoke, build" \
    scikit-build-core nuitka invoke build

pip_install_group "G2: Core Utilities" "decorator, attrs, cloudpickle, typing_extensions, pytest, psutil" \
    decorator attrs cloudpickle typing_extensions pytest psutil

pip_install_group "G3: Jupyter Ecosystem" "ipython, ipykernel, jupyterlab>=4.4, notebook>=7.3" \
    ipython ipykernel "jupyterlab>=4.4" "notebook>=7.3"

pip_install_group "G4: Data Processing" "pyarrow, pandas, scikit-learn, natsort (numpy/scipy pulled as deps)" \
    pyarrow pandas scikit-learn natsort

pip_install_group "G5: NLP/Transformers" "datasets, transformers, sentencepiece, sentence-transformers, evaluate, tiktoken, onnx2torch" \
    datasets transformers sentencepiece sentence-transformers evaluate tiktoken onnx2torch

pip_install_group "G6: Visualization/CLI" "matplotlib, seaborn, wordcloud, tabulate, tqdm, colorama, rich" \
    matplotlib seaborn wordcloud tabulate tqdm colorama rich

pip_install_group "G7: AI/ML Utilities" "einops, open_clip_torch, numba (llvmlite pulled as dep)" \
    einops open_clip_torch numba

pip_install_group "G8: Audio Processing" "librosa (soundfile, audioread, resampy pulled as deps)" \
    librosa

pip_install_group "G9: Chinese NLP" "jieba, nltk, pypinyin" \
    jieba nltk pypinyin

pip_install_group "G10: Document Processing" "PyMuPDF, EbookLib, beautifulsoup4, openpyxl" \
    PyMuPDF EbookLib beautifulsoup4 openpyxl

pip_install_group "G11: Web/API Stack" "pydantic, fastapi, uvicorn, httpx>=0.28" \
    pydantic fastapi uvicorn "httpx>=0.28"

pip_install_group "G12: Serialization/Config" "toml, typer, xmltodict, pyyaml" \
    toml typer xmltodict pyyaml

pip_install_group "G13: Database Clients" "psycopg2-binary, pymongo, elasticsearch, minio" \
    psycopg2-binary pymongo elasticsearch minio

pip_install_group "G14: Developer Tools" "icecream" \
    icecream

echo ""
echo "[ACTION] Setting permissions for devuser..."
find /opt/conda/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified (bin executables only)"

echo ""
echo "[ACTION] Aggressive binary size optimization..."
find /opt/conda/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
find /opt/conda/lib -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/lib -name "*.pyc" -delete 2>/dev/null || true
echo "[OK] Binaries stripped and __pycache__/.pyc removed"

echo ""
echo "[ACTION] Cleaning caches..."
conda clean -ya -q 2>/dev/null || true
pip cache purge 2>/dev/null || true
echo "[OK] Caches cleaned"

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [FINAL CHECK] Dependency consistency (pip check)│"
echo "└─────────────────────────────────────────────────┘"
pip check 2>&1 || echo "[WARN] pip check reported issues (see above)"
echo ""

echo "[INFO] Installed package versions (conda base):"
python -c "
import importlib
packages = [
    ('torch', 'torch'), ('onnx', 'onnx'), ('onnxruntime', 'onnxruntime'),
    ('transformers', 'transformers'), ('datasets', 'datasets'),
    ('sentence_transformers', 'sentence-transformers'), ('evaluate', 'evaluate'),
    ('fastapi', 'fastapi'), ('uvicorn', 'uvicorn'), ('pydantic', 'pydantic'),
    ('pandas', 'pandas'), ('pyarrow', 'pyarrow'), ('sklearn', 'scikit-learn'),
    ('scipy', 'scipy'), ('numpy', 'numpy'),
    ('matplotlib', 'matplotlib'), ('seaborn', 'seaborn'),
    ('jieba', 'jieba'), ('nltk', 'nltk'), ('fitz', 'PyMuPDF'), ('openpyxl', 'openpyxl'),
    ('psycopg2', 'psycopg2-binary'), ('pymongo', 'pymongo'),
    ('elasticsearch', 'elasticsearch'), ('minio', 'minio'),
    ('nuitka', 'nuitka'), ('pytest', 'pytest'), ('rich', 'rich'),
    ('typer', 'typer'), ('httpx', 'httpx'), ('numba', 'numba'),
    ('einops', 'einops'), ('librosa', 'librosa'),
]
for mod, name in packages:
    try:
        m = importlib.import_module(mod)
        ver = getattr(m, '__version__', 'installed')
        print(f'  - {name}: {ver}')
    except ImportError:
        print(f'  - {name}: NOT FOUND')
"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.ai-dev-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "AIS2=$_NOW" >> /tmp/.ai-dev-variant-build-timer
echo "[TIMER] Stage 2/3 (install AI/ML/NLP ecosystem) took ${_ELAPSED}s | AI-Dev variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 2 complete'
STAGE2_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 3/3 (追加层3): Jupyter内核 + build-info + 清理 + 验证 + 汇总
# 变化频率：最低
# 原则：注册通用AI Jupyter内核；写入build-info；运行时恢复PIP_USER=1；
#       [VALIDATION CHECKPOINT]；输出 BUILD TIMING SUMMARY 表
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE3_EOF'
echo ""
echo "########################################################################"
echo "# [AI-DEV VARIANT STAGE 3/3] Jupyter Kernel + Metadata + Validation"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate base

echo "[ACTION] Registering generic 'Python 3 (AI Dev)' Jupyter kernel..."
mkdir -p /opt/conda/envs/main/share/jupyter/kernels/ai-dev

cat > /opt/kernels-ai-dev.json <<'KERNEL'
{
 "display_name": "Python 3 (AI Dev)",
 "language": "python",
 "argv": [
  "/opt/conda/bin/python",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "env": {
  "PATH": "/opt/conda/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
  "OMP_NUM_THREADS": "4",
  "KMP_DUPLICATE_LIB_OK": "TRUE"
 }
}
KERNEL

cp /opt/kernels-ai-dev.json /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json
rm -f /opt/kernels-ai-dev.json

AI_GROUP=$(id -g devuser)
chown -R devuser:${AI_GROUP} /opt/conda/envs/main/share/jupyter/kernels/ai-dev
chmod 644 /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json
echo "[OK] ai-dev kernel registered at /opt/conda/envs/main/share/jupyter/kernels/ai-dev (main env jupyter service)"
echo "[KERNEL] display_name: Python 3 (AI Dev)"
echo "[KERNEL] python: /opt/conda/bin/python"
echo ""

echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-ai-dev-build-info..."
TRANSFORMERS_VER=$(python -c "import transformers;print(transformers.__version__)" 2>/dev/null || echo "unknown")
DATASETS_VER=$(python -c "import datasets;print(datasets.__version__)" 2>/dev/null || echo "unknown")
FASTAPI_VER=$(python -c "import fastapi;print(fastapi.__version__)" 2>/dev/null || echo "unknown")
PANDAS_VER=$(python -c "import pandas;print(pandas.__version__)" 2>/dev/null || echo "unknown")
PYTORCH_VER=$(python -c "import torch;print(torch.__version__)" 2>/dev/null || echo "unknown")
ONNX_VER=$(python -c "import onnx;print(onnx.__version__)" 2>/dev/null || echo "unknown")
ORT_VER=$(python -c "import onnxruntime;print(onnxruntime.__version__)" 2>/dev/null || echo "unknown")
JUPYTERLAB_VER=$(/opt/conda/envs/main/bin/jupyter lab --version 2>/dev/null || echo "unknown")
NOTEBOOK_VER=$(/opt/conda/envs/main/bin/jupyter notebook --version 2>/dev/null || echo "unknown")
PYTHON_VER=$(python --version 2>&1 | awk '{print $2}')
printf '%s\n' \
    "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    "VARIANT=ai-dev" \
    "VARIANT_DESCRIPTION=Full AI/ML/NLP Python ecosystem with JupyterLab 4.x and generic AI kernel" \
    "BASE_IMAGE=devcontainer-base:onnx-quantized-${BASE_TAG}" \
    "PYTHON_VERSION=${PYTHON_VER}" \
    "PYTORCH_VERSION=${PYTORCH_VER}" \
    "ONNX_VERSION=${ONNX_VER}" \
    "ONNXRUNTIME_VERSION=${ORT_VER}" \
    "TRANSFORMERS_VERSION=${TRANSFORMERS_VER}" \
    "DATASETS_VERSION=${DATASETS_VER}" \
    "FASTAPI_VERSION=${FASTAPI_VER}" \
    "PANDAS_VERSION=${PANDAS_VER}" \
    "JUPYTERLAB_VERSION=${JUPYTERLAB_VER}" \
    "NOTEBOOK_VERSION=${NOTEBOOK_VER}" \
    "CONDA_DIR=/opt/conda" \
    "CONDA_MIRROR=${CONDA_MIRROR}" \
    "PIP_MIRROR=${PIP_MIRROR}" \
    "APT_MIRROR=${APT_MIRROR}" \
    "INSTALL_ENV=base" \
    "PATH_PRIORITY=conda-bin-first" \
    "PYTHON_ENV=conda-base" \
    "JUPYTER_KERNEL=ai-dev (Python 3 AI Dev, /opt/conda/bin/python)" \
    "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
    "PACKAGES_COUNT=50+" \
    "OPENMP_CONFIG=OMP_NUM_THREADS=4,KMP_DUPLICATE_LIB_OK=TRUE" \
    "BUILD_TIMER=enabled" \
    > /etc/devcontainer-variant-ai-dev-build-info
echo "[OK] Build metadata written:"
cat /etc/devcontainer-variant-ai-dev-build-info
echo ""

echo "[ACTION] Running cleanup..."
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
find /opt/conda/lib -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
find /opt/conda/lib -name "*.pyc" -delete 2>/dev/null || true
echo "[OK] Cleanup complete"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [VALIDATION CHECKPOINT - Stage 3/3]           │"
echo "│  Running service + ecosystem validation        │"
echo "└─────────────────────────────────────────────────┘"
echo ""
echo "[VALIDATE 1/8] Core AI/ML/NLP package imports..."
python -c "import transformers, datasets, sentence_transformers, evaluate; print('[OK] NLP stack imports')"
python -c "import fastapi, uvicorn, pydantic, httpx; print('[OK] Web/API stack imports')"
python -c "import pandas, pyarrow, sklearn; print('[OK] Data stack imports')"
python -c "import matplotlib, seaborn, rich, typer; print('[OK] Viz/CLI stack imports')"
python -c "import jieba, nltk, pypinyin; print('[OK] Chinese NLP imports')"
python -c "import fitz, bs4, openpyxl; print('[OK] Document processing imports')"
python -c "import psycopg2, pymongo, elasticsearch, minio; print('[OK] Database clients imports')"
python -c "import nuitka, pytest, psutil, icecream; print('[OK] Build/dev tools imports')"

echo "[VALIDATE 2/8] Conda environment verified..."
test -d /opt/conda && test -x /opt/conda/bin/python && echo "[OK] /opt/conda verified"
test ! -d /opt/venv && echo "[OK] /opt/venv does not exist (removed)"
/opt/conda/bin/python --version

echo "[VALIDATE 3/8] JupyterLab >=4.4 in main env (/opt/conda/envs/main)..."
/opt/conda/envs/main/bin/jupyter lab --version
_JL_VER=$(/opt/conda/envs/main/bin/jupyter lab --version 2>/dev/null | head -1)
_JL_MAJOR=$(echo "$_JL_VER" | cut -d. -f1)
_JL_MINOR=$(echo "$_JL_VER" | cut -d. -f2)
if [ "$_JL_MAJOR" -gt 4 ] || { [ "$_JL_MAJOR" -eq 4 ] && [ "$_JL_MINOR" -ge 4 ]; }; then
    echo "[OK] JupyterLab $_JL_VER meets >=4.4 requirement"
else
    echo "[WARN] JupyterLab $_JL_VER may not meet >=4.4 requirement"
fi

echo "[VALIDATE 4/8] Core services (docker, supervisord) preserved..."
docker --version 2>&1
supervisord --version 2>&1
echo "[OK] Core services preserved"

echo "[VALIDATE 5/8] devuser can access AI/ML packages..."
su - devuser -c "/opt/conda/bin/python -c 'import transformers, pandas, fastapi; print(\"packages accessible\")'" && echo "[OK] devuser can access AI/ML packages"

echo "[VALIDATE 6/8] onnx-quantized inheritance (quantization API, main env)..."
/opt/conda/envs/main/bin/python -c "from onnxruntime.quantization import quantize_dynamic, QuantType, quantize_static, CalibrationDataReader; print('[OK] quantization API inherited')"

echo "[VALIDATE 6.5/8] Architecture guards (GIL state)..."
echo "  - base env GIL enabled: $(/opt/conda/bin/python -c 'import sys;print("yes" if sys._is_gil_enabled() is True else "NO")')"
echo "  - main env GIL disabled: $(/opt/conda/envs/main/bin/python -c 'import sys;print("yes" if sys._is_gil_enabled() is False else "NO")')"
/opt/conda/bin/python -c "import sys; assert sys._is_gil_enabled() is True, 'base env must be standard build (GIL enabled)'"
/opt/conda/envs/main/bin/python -c "import sys; assert sys._is_gil_enabled() is False, 'main env must be free-threading (GIL disabled)'"
echo "[OK] GIL state guards passed"

echo "[VALIDATE 7/8] Jupyter kernel registered (main env jupyter)..."
test -f /opt/conda/envs/main/share/jupyter/kernels/ai-dev/kernel.json && echo "[OK] ai-dev kernel in /opt/conda/envs/main/share/jupyter/kernels"
/opt/conda/envs/main/bin/jupyter kernelspec list 2>/dev/null | grep -q ai-dev && echo "[OK] kernel visible to Jupyter (main env service)"

echo "[VALIDATE 8/8] PATH and environment..."
echo "  PATH: $PATH"
echo "  OMP_NUM_THREADS: $OMP_NUM_THREADS"
echo "  KMP_DUPLICATE_LIB_OK: $KMP_DUPLICATE_LIB_OK"
test "$(which python)" = "/opt/conda/bin/python" && echo "[OK] conda python is default" || echo "[INFO] default python: $(which python)"
echo ""
echo "[VALIDATE] All validation checks completed"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.ai-dev-variant-build-timer | cut -d= -f2)
_AIS1=$(grep '^AIS1=' /tmp/.ai-dev-variant-build-timer | cut -d= -f2)
_AIS2=$(grep '^AIS2=' /tmp/.ai-dev-variant-build-timer | cut -d= -f2)
_AT1=$((_AIS1 - _START))
_AT2=$((_AIS2 - _AIS1))
_AT3=$_ELAPSED
_ATOTAL=$((_NOW - _START))
echo "[TIMER] Stage 3/3 (kernel+metadata+validation) took ${_ELAPSED}s | AI-Dev variant cumulative: ${_ATOTAL}s"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  BUILD TIMING SUMMARY (AI-Dev Variant - 3 Add Stages)       ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Stage 1/3  base verification         %5ds               ║\n" $_AT1
printf "║  Stage 2/3  install AI/ML ecosystem   %5ds               ║\n" $_AT2
printf "║  Stage 3/3  kernel+metadata+validate  %5ds               ║\n" $_AT3
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  AI-DEV VARIANT TOTAL (add-on)        %5ds               ║\n" $_ATOTAL
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
rm -f /tmp/.ai-dev-variant-build-timer
echo "########################################################################"
echo "# AI-DEV VARIANT BUILD COMPLETE!"
echo "# Full AI/ML/NLP Python ecosystem (50+ packages)"
echo "# JupyterLab >=4.4 + Python 3 (AI Dev) kernel"
echo "#"
echo "# Quick start:"
echo "#   import transformers, datasets, fastapi, pandas"
echo "#   jupyter lab --allow-root  (or via supervisord)"
echo "########################################################################"
echo ""
STAGE3_EOF

# ── Runtime environment (no layers) ──
ENV PIP_USER=1
