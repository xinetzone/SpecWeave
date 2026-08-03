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
# =============================================================================

# -----------------------------------------------------------------------------
# Global build arguments
# -----------------------------------------------------------------------------
ARG APT_MIRROR=official
ARG PIP_MIRROR=official
ARG CONDA_MIRROR=official
ARG PYTHON_VERSION=3.14
ARG BASE_IMAGE=jupyter-ssh-base:1.1

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
    echo "[BUILD] Pre-installed conda: $(/opt/conda/bin/conda --version)"

# -----------------------------------------------------------------------------
# [Builder 2/3] Configure mirrors and create caffe-ffi conda environment
# Reference: projects/xuanspace/libs/caffe-ffi/environment.yml
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 2/3] Creating conda environment: caffe-ffi (Python ${PYTHON_VERSION}) ===" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda config --system --set auto_activate_base false && \
    if [ "${CONDA_MIRROR}" = "tuna" ]; then \
        printf 'channels:\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r\n  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main\nshow_channel_urls: true\nchannel_priority: strict\nssl_verify: true\n' > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using Tsinghua TUNA conda mirror"; \
    else \
        printf 'channels:\n  - conda-forge\n  - defaults\nchannel_priority: strict\n' > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using default conda channels (conda-forge + defaults)"; \
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
        libopenblas \
        "cmake>=3.26" \
        "ninja>=1.13" \
        make \
        cxx-compiler \
        "conda-build>=3.28" \
        conda-verify \
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
    echo "[BUILD] Conda base env ready (runtime editable install via volume mount + entrypoint)"

# -----------------------------------------------------------------------------
# [Builder 3/3] Export package list for verification
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 3/3] Builder stage complete ===" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate caffe-ffi && \
    echo "[BUILD] Installed key packages:" && \
    pip list 2>/dev/null | grep -iE "caffe|numpy|protobuf|tvm|ipykernel|scikit|cython" || true && \
    echo "[BUILD] ========== BUILDER STAGE COMPLETE =========="

# =============================================================================
# STAGE 2: Runtime - Minimal image with conda env on top of jupyter-ssh-base
# =============================================================================
FROM ${BASE_IMAGE}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

LABEL maintainer="Caffe-FFI Jupyter Team" \
      description="Caffe-FFI JupyterLab with SSH and Miniconda (caffe-ffi conda env)"

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
    WORKSPACE_DIR=/workspace

# -----------------------------------------------------------------------------
# [Runtime 1/5] Install minimal runtime dependencies
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 1/5] Installing runtime packages ===" && \
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
    echo "[BUILD] Runtime packages installed (libgomp1 for OpenMP, curl for healthcheck)"

# -----------------------------------------------------------------------------
# [Runtime 2/5] Copy Miniconda + caffe-ffi environment from builder
# -----------------------------------------------------------------------------
COPY --from=builder /opt/conda /opt/conda

RUN echo "=== [Runtime 2/5] Copying conda environment from builder ===" && \
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
    python -c "import tvm_ffi; print('[BUILD] tvm_ffi:', tvm_ffi.__version__)"

# -----------------------------------------------------------------------------
# [Runtime 3/5] Setup workspace directory + editable-install entrypoint
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 3/5] Setting up workspace directory ===" && \
    mkdir -p "${WORKSPACE_DIR}" && \
    chown jupyteruser:jupyteruser "${WORKSPACE_DIR}" && \
    echo "[BUILD] Workspace directory created: ${WORKSPACE_DIR}"

# Copy editable-install entrypoint from scripts directory
COPY apps/caffe-ffi-jupyter/scripts/editable-install.sh /usr/local/bin/editable-install.sh
RUN chmod +x /usr/local/bin/editable-install.sh && \
    sed -i 's/\r$//' /usr/local/bin/editable-install.sh && \
    echo "[BUILD] editable-install.sh entrypoint installed (external script)"

# -----------------------------------------------------------------------------
# Copy C++ unit test / ASan / BLAS / Conda-build verification scripts into image
# -----------------------------------------------------------------------------
COPY apps/caffe-ffi-jupyter/scripts/test-cpp-tests.sh /usr/local/bin/test-cpp-tests.sh
COPY apps/caffe-ffi-jupyter/scripts/test-asan.sh /usr/local/bin/test-asan.sh
COPY apps/caffe-ffi-jupyter/scripts/test-blas-bench.sh /usr/local/bin/test-blas-bench.sh
COPY apps/caffe-ffi-jupyter/scripts/test-conda-build.sh /usr/local/bin/test-conda-build.sh
COPY apps/caffe-ffi-jupyter/scripts/check-cpp-extension-deps.sh /usr/local/bin/check-cpp-extension-deps.sh
COPY apps/caffe-ffi-jupyter/scripts/container-healthcheck.sh /usr/local/bin/container-healthcheck.sh
RUN chmod +x /usr/local/bin/test-cpp-tests.sh /usr/local/bin/test-asan.sh /usr/local/bin/test-blas-bench.sh /usr/local/bin/test-conda-build.sh /usr/local/bin/check-cpp-extension-deps.sh /usr/local/bin/container-healthcheck.sh && \
    sed -i 's/\r$//' /usr/local/bin/test-cpp-tests.sh /usr/local/bin/test-asan.sh /usr/local/bin/test-blas-bench.sh /usr/local/bin/test-conda-build.sh /usr/local/bin/check-cpp-extension-deps.sh /usr/local/bin/container-healthcheck.sh && \
    echo "[BUILD] scripts installed to /usr/local/bin/: test-cpp-tests.sh, test-asan.sh, test-blas-bench.sh, test-conda-build.sh, check-cpp-extension-deps.sh, container-healthcheck.sh"

# -----------------------------------------------------------------------------
# [Runtime 4/5] Configure conda auto-activation and Jupyter kernel
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 4/5] Configuring conda auto-activation and Jupyter kernel ===" && \
    printf '#!/bin/bash\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate caffe-ffi 2>/dev/null || true\n' > /etc/profile.d/conda-caffe-ffi.sh && \
    chmod +x /etc/profile.d/conda-caffe-ffi.sh && \
    printf '\n# >>> caffe-ffi conda environment >>>\nsource /opt/conda/etc/profile.d/conda.sh\nconda activate caffe-ffi 2>/dev/null || true\nexport LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:${LD_LIBRARY_PATH}\n# <<< caffe-ffi conda environment <<<\n' >> /home/jupyteruser/.bashrc && \
    chown jupyteruser:jupyteruser /home/jupyteruser/.bashrc && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    echo "[BUILD] Registering caffe-ffi ipykernel..." && \
    python -m ipykernel install --user --name=caffe-ffi --display-name="Python (caffe-ffi)" && \
    echo "[BUILD] ipykernel registered: caffe-ffi" && \
    echo "[BUILD] Checking tvm_ffi native module dependencies..." && \
    _TVM_SO=$(python -c 'import tvm_ffi, os, glob; sos=glob.glob(os.path.join(os.path.dirname(tvm_ffi.__file__), "_tvm_ffi*.so")); print(sos[0] if sos else "")' 2>/dev/null || true) && \
    if [ -n "$_TVM_SO" ] && [ -f "$_TVM_SO" ]; then \
        echo "[BUILD] _tvm_ffi native module: $_TVM_SO"; \
        if ldd "$_TVM_SO" 2>/dev/null | grep -q 'not found'; then \
            echo "[WARN] Some tvm_ffi deps not found (may need LD_LIBRARY_PATH)"; \
            ldd "$_TVM_SO" | grep 'not found'; \
        else \
            echo "[BUILD] tvm_ffi native deps OK"; \
        fi; \
    else \
        echo "[BUILD] tvm_ffi: pure Python or no native .so found (expected for PyPI wheel)"; \
    fi

# -----------------------------------------------------------------------------
# [Runtime 5/5] Final cleanup and metadata
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 5/5] Final cleanup ===" && \
    BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ) && \
    printf 'BUILD_DATE=%s\nBASE_IMAGE=%s\nBUILDER=continuumio/miniconda3:latest\nCONDA_DIR=/opt/conda\nENV_NAME=caffe-ffi\nPYTHON_VERSION=%s\nSERVICES=sshd,jupyter,conda-caffe-ffi\nWORKSPACE_DIR=%s\nEDITABLE_INSTALL=auto (entrypoint)\n' "$BUILD_DATE" "${BASE_IMAGE}" "${PYTHON_VERSION}" "${WORKSPACE_DIR}" > /etc/caffe-ffi-jupyter-build-info && \
    cat /etc/caffe-ffi-jupyter-build-info && \
    echo "[BUILD] Final verification:" && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    echo "  python:        $(python --version)" && \
    echo "  conda:         $(conda --version)" && \
    echo "  numpy:         $(python -c 'import numpy; print(numpy.__version__)')" && \
    echo "  protobuf:      $(python -c 'import google.protobuf; print(google.protobuf.__version__)')" && \
    echo "  tvm_ffi:       $(python -c 'import tvm_ffi; print(tvm_ffi.__version__)' 2>/dev/null || echo 'editable install pending')" && \
    echo "  caffe_ffi:     $(python -c 'import caffe_ffi; print(caffe_ffi.__version__)' 2>/dev/null || echo 'editable install pending (mount source dir)')" && \
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
