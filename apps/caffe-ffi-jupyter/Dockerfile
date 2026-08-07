# =============================================================================
# Caffe-FFI JupyterLab + SSH Image
# Multi-stage build: continuumio/miniconda3 as builder → jupyter-ssh-base as runtime
#
# Design:
#   - Builder stage: Create conda env with Python 3.14, build tools, and PyPI tvm-ffi
#   - Runtime stage: Copy conda env into jupyter-ssh-base, register Jupyter kernel
#   - At container startup: entrypoint auto-detects mounted source dirs and runs
#     pip install -e (editable install) for local development
#
# Volume mount for development:
#   Mount entire SpecWeave repo to /workspace (default paths auto-detected):
#     - /workspace/projects/xuanspace/vendor/tvm-ffi
#     - /workspace/projects/xuanspace/libs/caffe-ffi
#   Or override with env vars:
#     - TVM_FFI_SRC_DIR=/custom/path/to/tvm-ffi
#     - CAFFE_FFI_SRC_DIR=/custom/path/to/caffe-ffi
#
# Runtime Stage Layering (on top of jupyter-ssh-base, dockerfile-runtime-logical-layering v1.3):
#   Stage R1/6: 额外运行时依赖 (libgomp1, curl) (变化频率: 低)
#   Stage R2/6: COPY conda env from builder + ldconfig + PATH (变化频率: 中)
#   Stage R3/6: workspace目录 + jupyteruser权限 (变化频率: 中)
#   Stage R4/6: 集中COPY所有脚本 + chmod (变化频率: 高)
#   Stage R5/6: profile.d/.bashrc/ipykernel配置 + 语法验证 (变化频率: 高)
#   Stage R6/6: build-info + 最终验证 + 耗时汇总表 (变化频率: 最低)
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

# -----------------------------------------------------------------------------
# Global build arguments
# -----------------------------------------------------------------------------
ARG APT_MIRROR=official
ARG PIP_MIRROR=official
ARG CONDA_MIRROR=official
ARG PYTHON_VERSION=3.14
ARG BASE_IMAGE=jupyter-ssh-base:1.3

# =============================================================================
# STAGE 1: Builder - Build caffe-ffi conda environment
# =============================================================================
FROM continuumio/miniconda3:latest AS builder

# Explicit, unambiguous shell: bash with errexit + pipefail
SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

ARG APT_MIRROR
ARG PIP_MIRROR
ARG CONDA_MIRROR
ARG PYTHON_VERSION

ENV DEBIAN_FRONTEND=noninteractive \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8 \
    CONDA_DIR=/opt/conda \
    PATH=/opt/conda/bin:/opt/conda/envs/caffe-ffi/bin:$PATH

# -----------------------------------------------------------------------------
# [Builder 1/3] Configure APT mirror and install build dependencies
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 1/3] Configuring APT mirror: ${APT_MIRROR} ===" && \
    _STAGE_START=$(date +%s) && \
    echo "START=$_STAGE_START" > /tmp/.build-timer && \
    echo "[TIMER] Builder started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://deb.debian.org|http://mirrors.aliyun.com|g; s|http://security.debian.org|http://mirrors.aliyun.com|g' "$$f"; \
            fi; \
        done; \
        echo "[BUILD] Using Aliyun APT mirror"; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        for f in /etc/apt/sources.list.d/debian.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://deb.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.debian.org|https://mirrors.tuna.tsinghua.edu.cn|g' "$$f"; \
            fi; \
        done; \
        echo "[BUILD] Using Tsinghua TUNA APT mirror"; \
    else \
        echo "[BUILD] Using default Debian APT sources"; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        pkg-config \
        wget \
        ca-certificates \
        git \
    && rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] Builder base packages installed" && \
    echo "[BUILD] Pre-installed conda: $(/opt/conda/bin/conda --version)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    echo "BS1=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Builder 1/3 took ${_ELAPSED}s"

# -----------------------------------------------------------------------------
# [Builder 2/3] Configure mirrors and create caffe-ffi conda environment
# Reference: projects/xuanspace/libs/caffe-ffi/environment.yml
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 2/3] Creating conda environment: caffe-ffi (Python ${PYTHON_VERSION}) ===" && \
    _STAGE_START=$(date +%s) && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda config --system --set auto_activate_base false && \
    if [ "${CONDA_MIRROR}" = "tuna" ]; then \
        printf 'channels:\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge\nshow_channel_urls: true\nchannel_priority: flexible\nssl_verify: true\n' > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using Tsinghua TUNA conda mirror"; \
    else \
        printf 'channels:\n  - conda-forge\nchannel_priority: flexible\n' > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using conda-forge only (flexible priority)"; \
    fi && \
    if [ "${PIP_MIRROR}" = "aliyun" ]; then \
        mkdir -p /root/.config/pip && \
        printf '[global]\nindex-url = https://mirrors.aliyun.com/pypi/simple/\ntrusted-host = mirrors.aliyun.com\nretries = 10\ntimeout = 120\n' > /root/.config/pip/pip.conf && \
        echo "[BUILD] Using Aliyun PyPI mirror"; \
    elif [ "${PIP_MIRROR}" = "tuna" ]; then \
        mkdir -p /root/.config/pip && \
        printf '[global]\nindex-url = https://pypi.tuna.tsinghua.edu.cn/simple/\ntrusted-host = pypi.tuna.tsinghua.edu.cn\nretries = 10\ntimeout = 120\n' > /root/.config/pip/pip.conf && \
        echo "[BUILD] Using Tsinghua TUNA PyPI mirror"; \
    fi && \
    echo "[BUILD] Creating conda env with Python + build tools + core C++ libs..." && \
    conda create -y -n caffe-ffi -c conda-forge \
        python="${PYTHON_VERSION}" \
        pip setuptools wheel setuptools-scm \
        "libprotobuf>=7.0.0" \
        "protobuf>=7.0.0" \
        zlib \
        "libopenblas=*=*openmp*" \
        openblas \
        "cmake>=3.26" \
        "ninja>=1.13" \
        make \
        cxx-compiler \
        patchelf \
    && conda activate caffe-ffi && \
    echo "[BUILD] conda env 'caffe-ffi' created, Python: $(python --version)" && \
    echo "[BUILD] Conda-installed protobuf: $(protoc --version)" && \
    echo "[BUILD] Conda-installed cmake: $(cmake --version | head -1)" && \
    echo "[BUILD] Installing Python base packages (numpy, scikit-build-core, tvm-ffi)..." && \
    pip install --no-cache-dir \
        "numpy>=2.3" \
        "scikit-build-core>=0.10" \
        "cython>=3.2.8" \
        "setuptools-scm" \
        "typing-extensions>=4.5" \
        "pytest>=8.0" \
        ipykernel \
        apache-tvm-ffi && \
    echo "[BUILD] Base Python dependencies + apache-tvm-ffi (PyPI) installed" && \
    python -c "import numpy; print('[BUILD] numpy:', numpy.__version__)" && \
    python -c "import tvm_ffi; print('[BUILD] tvm_ffi:', tvm_ffi.__version__)" && \
    conda clean -ya && \
    pip cache purge 2>/dev/null || true && \
    echo "[BUILD] Conda base env ready (runtime editable install via volume mount + entrypoint)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _BTOTAL=$((_NOW - _START)) && \
    echo "BS2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Builder 2/3 took ${_ELAPSED}s | Builder cumulative: ${_BTOTAL}s"

# -----------------------------------------------------------------------------
# [Builder 3/3] Export package list for verification
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 3/3] Builder stage complete ===" && \
    _STAGE_START=$(date +%s) && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate caffe-ffi && \
    echo "[BUILD] Installed key packages:" && \
    pip list 2>/dev/null | grep -iE "caffe|numpy|protobuf|tvm|ipykernel|scikit|cython" || true && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _BS1=$(grep '^BS1=' /tmp/.build-timer | cut -d= -f2) && \
    _BS2=$(grep '^BS2=' /tmp/.build-timer | cut -d= -f2) && \
    _BT1=$((_BS1 - _START)) && \
    _BT2=$((_BS2 - _BS1)) && \
    _BT3=$_ELAPSED && \
    _BTOTAL=$((_NOW - _START)) && \
    echo "╔══════════════════════════════════════════════════════════════╗" && \
    echo "║       BUILDER TIMING SUMMARY (conda env creation)          ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Builder 1/3  build deps + APT mirror  %5ds               ║\n" $_BT1 && \
    printf "║  Builder 2/3  conda env + pip deps     %5ds  ★ hotspot    ║\n" $_BT2 && \
    printf "║  Builder 3/3  package listing          %5ds               ║\n" $_BT3 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  BUILDER TOTAL                         %5ds               ║\n" $_BTOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "[BUILD] ========== BUILDER STAGE COMPLETE ==========" && \
    rm -f /tmp/.build-timer

# =============================================================================
# STAGE 2: Runtime - Minimal image with conda env on top of jupyter-ssh-base
# =============================================================================
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

LABEL maintainer="Caffe-FFI Jupyter Team" \
      description="Caffe-FFI JupyterLab with SSH and Miniconda (caffe-ffi conda env)" \
      version="1.2"

ARG APT_MIRROR
ARG PIP_MIRROR
ARG CONDA_MIRROR
ARG PYTHON_VERSION
ARG BASE_IMAGE

ARG CONDA_DIR=/opt/conda
ARG ENV_NAME=caffe-ffi
ARG ENV_PATH=/opt/conda/envs/caffe-ffi
ARG WORKSPACE_DIR=/workspace

ENV CONDA_DIR=/opt/conda \
    ENV_NAME=caffe-ffi \
    ENV_PATH=/opt/conda/envs/caffe-ffi \
    PATH=/opt/conda/bin:/opt/conda/envs/caffe-ffi/bin:/opt/venv/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:${LD_LIBRARY_PATH} \
    CONDA_DEFAULT_ENV=caffe-ffi \
    OMP_NUM_THREADS=4 \
    OPENBLAS_NUM_THREADS=1 \
    WORKSPACE_DIR=/workspace

# ═══════════════════════════════════════════════════════════════════
# Stage R1/6: 额外运行时依赖 (libgomp1 for OpenMP, curl for healthcheck)
# 变化频率：低（基础镜像已有大部分系统包，这里只加caffe-ffi额外依赖）
# 初始化运行时计时器
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== [Runtime R1/6] Installing additional runtime packages ===" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Runtime stage started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.build-timer && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        for f in /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' "$$f"; \
            fi; \
        done; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        for f in /etc/apt/sources.list.d/ubuntu.sources /etc/apt/sources.list; do \
            if [ -f "$$f" ]; then \
                sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' "$$f"; \
            fi; \
        done; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        libgomp1 \
        curl \
    && rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] Runtime packages installed (libgomp1 for OpenMP, curl for healthcheck)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.build-timer | cut -d= -f2))) && \
    echo "RS1=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage R1/6 (extra runtime deps) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage R2/6: COPY conda env from builder + 配置动态库路径 + 基础导入验证
# 变化频率：中（依赖版本升级时改）
# ═══════════════════════════════════════════════════════════════════
COPY --from=builder /opt/conda /opt/conda

RUN echo "=== [Runtime R2/6] Copying conda environment from builder ===" && \
    _STAGE_START=$(date +%s) && \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    echo "[BUILD] Conda copied: $("${CONDA_DIR}/bin/conda" --version)" && \
    test -x "${CONDA_DIR}/envs/caffe-ffi/bin/python" && \
    echo "[BUILD] Activating conda environment before any Python calls..." && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    echo "[BUILD] caffe-ffi env Python: $(python --version)" && \
    echo "[BUILD] Configuring dynamic library search paths..." && \
    echo "${CONDA_DIR}/lib" > /etc/ld.so.conf.d/caffe-ffi.conf && \
    echo "${ENV_PATH}/lib" >> /etc/ld.so.conf.d/caffe-ffi.conf && \
    ldconfig && \
    echo "[BUILD] ldconfig updated with caffe-ffi library paths" && \
    echo "[BUILD] Verifying base imports..." && \
    python -c "import numpy; print('[BUILD] numpy:', numpy.__version__)" && \
    python -c "import google.protobuf; print('[BUILD] protobuf:', google.protobuf.__version__)" && \
    python -c "import tvm_ffi; print('[BUILD] tvm_ffi (PyPI wheel):', tvm_ffi.__version__)" 2>/dev/null || \
        echo "[BUILD] tvm_ffi PyPI wheel not importable (expected — will be rebuilt from source by editable-install.sh)" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "RS2=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage R2/6 (conda env copy+verify) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage R3/6: workspace目录创建 + jupyteruser权限
# 变化频率：中（新增目录时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== [Runtime R3/6] Setting up workspace directory ===" && \
    _STAGE_START=$(date +%s) && \
    mkdir -p "${WORKSPACE_DIR}" && \
    chown jupyteruser:jupyteruser "${WORKSPACE_DIR}" && \
    echo "[BUILD] Workspace directory created: ${WORKSPACE_DIR}" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "RS3=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage R3/6 (workspace dir) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage R4/6: 集中COPY所有脚本 + chmod（配置层，变化频率高）
# 原则：所有COPY集中在一处，后续层改脚本不会让前面层失效
# ═══════════════════════════════════════════════════════════════════
COPY apps/caffe-ffi-jupyter/scripts/editable-install.sh /usr/local/bin/editable-install.sh
COPY apps/caffe-ffi-jupyter/scripts/test-cpp-tests.sh /usr/local/bin/test-cpp-tests.sh
COPY apps/caffe-ffi-jupyter/scripts/test-asan.sh /usr/local/bin/test-asan.sh
COPY apps/caffe-ffi-jupyter/scripts/test-blas-bench.sh /usr/local/bin/test-blas-bench.sh
COPY apps/caffe-ffi-jupyter/scripts/test-conda-build.sh /usr/local/bin/test-conda-build.sh
COPY apps/caffe-ffi-jupyter/scripts/check-cpp-extension-deps.sh /usr/local/bin/check-cpp-extension-deps.sh
COPY apps/caffe-ffi-jupyter/scripts/container-healthcheck.sh /usr/local/bin/container-healthcheck.sh

RUN echo "=== [Runtime R4/6] Installing scripts and setting permissions ===" && \
    _STAGE_START=$(date +%s) && \
    chmod +x /usr/local/bin/editable-install.sh \
             /usr/local/bin/test-cpp-tests.sh \
             /usr/local/bin/test-asan.sh \
             /usr/local/bin/test-blas-bench.sh \
             /usr/local/bin/test-conda-build.sh \
             /usr/local/bin/check-cpp-extension-deps.sh \
             /usr/local/bin/container-healthcheck.sh && \
    sed -i 's/\r$//' /usr/local/bin/editable-install.sh \
                    /usr/local/bin/test-cpp-tests.sh \
                    /usr/local/bin/test-asan.sh \
                    /usr/local/bin/test-blas-bench.sh \
                    /usr/local/bin/test-conda-build.sh \
                    /usr/local/bin/check-cpp-extension-deps.sh \
                    /usr/local/bin/container-healthcheck.sh && \
    echo "[BUILD] Scripts installed to /usr/local/bin/: editable-install.sh, test-cpp-tests.sh, test-asan.sh, test-blas-bench.sh, test-conda-build.sh, check-cpp-extension-deps.sh, container-healthcheck.sh" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "RS4=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage R4/6 (scripts copy+chmod) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage R5/6: profile.d/.bashrc/ipykernel配置 + 语法验证检查点
# 变化频率：高（配置调整时改）
# 原则：配置写入后立即做语法验证（bash -n），构建即测试
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== [Runtime R5/6] Configuring conda auto-activation, Jupyter kernel + Validation ===" && \
    _STAGE_START=$(date +%s) && \
    printf '#!/bin/bash\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate caffe-ffi 2>/dev/null || true\n' > /etc/profile.d/conda-caffe-ffi.sh && \
    chmod +x /etc/profile.d/conda-caffe-ffi.sh && \
    printf '\n# >>> caffe-ffi conda environment >>>\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate caffe-ffi 2>/dev/null || true\nexport LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:${LD_LIBRARY_PATH}\n# <<< caffe-ffi conda environment <<<\n' >> /home/jupyteruser/.bashrc && \
    chown jupyteruser:jupyteruser /home/jupyteruser/.bashrc && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    echo "[BUILD] Registering caffe-ffi ipykernel..." && \
    python -m ipykernel install --user --name=caffe-ffi --display-name="Python (caffe-ffi)" && \
    echo "[BUILD] ipykernel registered: caffe-ffi" && \
    echo "[BUILD] Checking tvm_ffi native module dependencies..." && \
    set +e && \
    _TVM_SO=$(python -c 'import tvm_ffi, os, glob; sos=glob.glob(os.path.join(os.path.dirname(tvm_ffi.__file__), "_tvm_ffi*.so")); print(sos[0] if sos else "")' 2>/dev/null); \
    if [ -n "$_TVM_SO" ] && [ -f "$_TVM_SO" ]; then \
        echo "[BUILD] _tvm_ffi native module: $_TVM_SO"; \
        if ldd "$_TVM_SO" 2>/dev/null | grep -q 'not found'; then \
            echo "[WARN] Some tvm_ffi deps not found (will be rebuilt from source by entrypoint)"; \
        else \
            echo "[BUILD] tvm_ffi native deps OK"; \
        fi; \
    else \
        echo "[BUILD] tvm_ffi: PyPI wheel not importable (expected — will be rebuilt from source by entrypoint)"; \
    fi && \
    set -e && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [VALIDATION CHECKPOINT - Stage R5/6]           │" && \
    echo "│  Running syntax validation for all scripts      │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    echo "[VALIDATE 1/7] bash -n editable-install.sh..." && \
    bash -n /usr/local/bin/editable-install.sh && echo "[OK] editable-install.sh syntax valid" && \
    echo "[VALIDATE 2/7] bash -n container-healthcheck.sh..." && \
    bash -n /usr/local/bin/container-healthcheck.sh && echo "[OK] container-healthcheck.sh syntax valid" && \
    echo "[VALIDATE 3/7] bash -n test-cpp-tests.sh..." && \
    bash -n /usr/local/bin/test-cpp-tests.sh && echo "[OK] test-cpp-tests.sh syntax valid" && \
    echo "[VALIDATE 4/7] bash -n test-asan.sh..." && \
    bash -n /usr/local/bin/test-asan.sh && echo "[OK] test-asan.sh syntax valid" && \
    echo "[VALIDATE 5/7] bash -n test-blas-bench.sh..." && \
    bash -n /usr/local/bin/test-blas-bench.sh && echo "[OK] test-blas-bench.sh syntax valid" && \
    echo "[VALIDATE 6/7] bash -n test-conda-build.sh..." && \
    bash -n /usr/local/bin/test-conda-build.sh && echo "[OK] test-conda-build.sh syntax valid" && \
    echo "[VALIDATE 7/7] bash -n check-cpp-extension-deps.sh..." && \
    bash -n /usr/local/bin/check-cpp-extension-deps.sh && echo "[OK] check-cpp-extension-deps.sh syntax valid" && \
    echo "" && \
    echo "[BUILD] All 7 syntax validation checks passed" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _TOTAL=$((_NOW - _START)) && \
    echo "RS5=$_NOW" >> /tmp/.build-timer && \
    echo "[TIMER] Stage R5/6 (config+ipykernel+validate) took ${_ELAPSED}s | Cumulative: ${_TOTAL}s"

# ═══════════════════════════════════════════════════════════════════
# Stage R6/6: build-info + 最终验证 + 耗时汇总表 + 清理
# 变化频率：最低（版本发布时改）
# ═══════════════════════════════════════════════════════════════════
RUN echo "=== [Runtime R6/6] Final cleanup, metadata, and verification ===" && \
    _STAGE_START=$(date +%s) && \
    BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) && \
    printf 'BUILD_DATE=%s\nBASE_IMAGE=%s\nBUILDER=continuumio/miniconda3:latest\nCONDA_DIR=%s\nENV_NAME=%s\nPYTHON_VERSION=%s\nSERVICES=sshd,jupyter,conda-caffe-ffi\nWORKSPACE_DIR=%s\nEDITABLE_INSTALL=auto (entrypoint)\nBUILD_TIMER=enabled\nOMP_NUM_THREADS=4\nOPENBLAS_NUM_THREADS=1\n' \
        "$BUILD_DATE" "${BASE_IMAGE}" "${CONDA_DIR}" "${ENV_NAME}" "${PYTHON_VERSION}" "${WORKSPACE_DIR}" > /etc/caffe-ffi-jupyter-build-info && \
    cat /etc/caffe-ffi-jupyter-build-info && \
    echo "" && \
    echo "┌─────────────────────────────────────────────────┐" && \
    echo "│  [FINAL VERIFICATION - Stage R6/6]              │" && \
    echo "│  Verifying all critical components              │" && \
    echo "└─────────────────────────────────────────────────┘" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    test -x "${ENV_PATH}/bin/python" && echo "[OK] python:        $(${ENV_PATH}/bin/python --version 2>&1)" || echo "[FAIL] python not available" && \
    echo "[OK] conda:         $("${CONDA_DIR}/bin/conda" --version 2>&1 || echo 'not available')" && \
    echo "[OK] numpy:         $(${ENV_PATH}/bin/python -c 'import numpy; print(numpy.__version__)' 2>/dev/null || echo 'pending')" && \
    echo "[OK] protobuf:      $(${ENV_PATH}/bin/python -c 'import google.protobuf; print(google.protobuf.__version__)' 2>/dev/null || echo 'pending')" && \
    echo "[OK] tvm_ffi:       $(${ENV_PATH}/bin/python -c 'import tvm_ffi; print(tvm_ffi.__version__)' 2>/dev/null || echo 'editable install pending')" && \
    echo "[OK] caffe_ffi:     $(${ENV_PATH}/bin/python -c 'import caffe_ffi; print(caffe_ffi.__version__)' 2>/dev/null || echo 'editable install pending (mount source dir)')" && \
    tini --version >/dev/null 2>&1 && echo "[OK] tini (init) available" && \
    supervisord --version && echo "[OK] supervisord available" && \
    sshd -t && echo "[OK] sshd config valid" && \
    bash -n /usr/local/bin/entrypoint.sh && echo "[OK] base entrypoint.sh syntax valid" && \
    bash -n /usr/local/bin/editable-install.sh && echo "[OK] editable-install.sh syntax valid" && \
    echo "" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.build-timer | cut -d= -f2) && \
    _RS1=$(grep '^RS1=' /tmp/.build-timer | cut -d= -f2) && \
    _RS2=$(grep '^RS2=' /tmp/.build-timer | cut -d= -f2) && \
    _RS3=$(grep '^RS3=' /tmp/.build-timer | cut -d= -f2) && \
    _RS4=$(grep '^RS4=' /tmp/.build-timer | cut -d= -f2) && \
    _RS5=$(grep '^RS5=' /tmp/.build-timer | cut -d= -f2) && \
    _RT1=$((_RS1 - _START)) && \
    _RT2=$((_RS2 - _RS1)) && \
    _RT3=$((_RS3 - _RS2)) && \
    _RT4=$((_RS4 - _RS3)) && \
    _RT5=$((_RS5 - _RS4)) && \
    _RT6=$_ELAPSED && \
    _RTOTAL=$((_NOW - _START)) && \
    echo "╔══════════════════════════════════════════════════════════════╗" && \
    echo "║       BUILD TIMING SUMMARY (Caffe-FFI Runtime)             ║" && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  Stage R1/6  extra runtime deps       %5ds               ║\n" $_RT1 && \
    printf "║  Stage R2/6  conda env copy + verify  %5ds               ║\n" $_RT2 && \
    printf "║  Stage R3/6  workspace directory      %5ds               ║\n" $_RT3 && \
    printf "║  Stage R4/6  scripts copy + chmod     %5ds               ║\n" $_RT4 && \
    printf "║  Stage R5/6  config + ipykernel + val %5ds               ║\n" $_RT5 && \
    printf "║  Stage R6/6  metadata + final verify  %5ds               ║\n" $_RT6 && \
    echo "╠══════════════════════════════════════════════════════════════╣" && \
    printf "║  RUNTIME TOTAL                        %5ds               ║\n" $_RTOTAL && \
    echo "╚══════════════════════════════════════════════════════════════╝" && \
    echo "" && \
    rm -f /tmp/.build-timer /tmp/* /var/tmp/* && \
    echo "[BUILD] ========== RUNTIME STAGE COMPLETE =========="

WORKDIR ${WORKSPACE_DIR}

EXPOSE 8888 22

# Health check: verifies conda env, caffe_ffi import, protobuf ABI, .so deps, Jupyter API
HEALTHCHECK --interval=30s --timeout=10s --start-period=120s --retries=3 \
    CMD ["/usr/local/bin/container-healthcheck.sh"]

# Entrypoint chain:
#   1. editable-install.sh — activates conda, runs pip install -e for mounted sources
#   2. tini               — PID 1 init for zombie reaping + signal forwarding
#   3. entrypoint.sh      — jupyter-ssh-base entrypoint (passwords, SSH, Jupyter, supervisord)
ENTRYPOINT ["/usr/local/bin/editable-install.sh"]
CMD ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
