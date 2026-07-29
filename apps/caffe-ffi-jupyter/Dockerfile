# =============================================================================
# Caffe-FFI Jupyter - Dockerfile
# Project: SpecWeave Caffe-FFI Development Environment
# Base: jupyter-ssh-base:1.1 (SSH + Jupyter Notebook + supervisord + jupyteruser)
# Added: Miniconda3 + Python 3.14 + caffe-ffi + Jupyter kernel
#
# Build:  (from SpecWeave root)
#   DOCKER_BUILDKIT=1 docker build -f apps/caffe-ffi-jupyter/Dockerfile \
#     -t caffe-ffi-jupyter:latest .
# CN:
#   DOCKER_BUILDKIT=1 docker build -f apps/caffe-ffi-jupyter/Dockerfile \
#     --build-arg APT_MIRROR=aliyun --build-arg PIP_MIRROR=aliyun \
#     --build-arg CONDA_MIRROR=tuna \
#     -t caffe-ffi-jupyter:latest .
# Run:
#   docker run -d -p 2222:22 -p 8888:8888 \
#     -e USER_PASSWORD=changeme -e JUPYTER_TOKEN=mysecret \
#     -v $(pwd)/workspace:/workspace --name caffe-ffi caffe-ffi-jupyter:latest
# =============================================================================

ARG BASE_IMAGE=jupyter-ssh-base:1.1
ARG APT_MIRROR=official
ARG PIP_MIRROR=official
ARG CONDA_MIRROR=official
ARG PYTHON_VERSION=3.14

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install build deps + Miniconda + compile caffe-ffi
# -----------------------------------------------------------------------------
FROM ${BASE_IMAGE} AS builder

ARG APT_MIRROR
ARG PIP_MIRROR
ARG CONDA_MIRROR
ARG PYTHON_VERSION

USER root
ENV DEBIAN_FRONTEND=noninteractive

# -----------------------------------------------------------------------------
# [Builder 1] Configure APT mirror and install build dependencies
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 1/5] Configuring APT mirror: ${APT_MIRROR} ===" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[BUILD] Using Aliyun APT mirror"; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || true; \
        echo "[BUILD] Using Tsinghua TUNA APT mirror"; \
    else \
        echo "[BUILD] Using official APT sources"; \
    fi && \
    echo "[BUILD] Installing build dependencies..." && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        ninja-build \
        libopenblas-dev \
        libprotobuf-dev \
        protobuf-compiler \
        wget \
        bzip2 \
        ca-certificates \
    && echo "[BUILD] Build dependencies installed" && \
    rm -rf /var/lib/apt/lists/*

# -----------------------------------------------------------------------------
# [Builder 2] Install Miniconda3
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 2/5] Installing Miniconda3 ===" && \
    ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then MINICONDA_ARCH="x86_64"; \
    elif [ "$ARCH" = "aarch64" ]; then MINICONDA_ARCH="aarch64"; \
    else echo "[ERROR] Unsupported architecture: $ARCH"; exit 1; fi && \
    CONDA_DIR=/opt/conda && \
    echo "[BUILD] Downloading Miniconda3 for Linux-${MINICONDA_ARCH}..." && \
    if [ "${CONDA_MIRROR}" = "tuna" ]; then \
        wget --tries=5 --timeout=120 --waitretry=5 \
            "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-${MINICONDA_ARCH}.sh" \
            -O /tmp/miniconda.sh || { \
            echo "[WARN] TUNA mirror failed, trying official..."; \
            wget --tries=5 --timeout=120 --waitretry=5 \
                "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${MINICONDA_ARCH}.sh" \
                -O /tmp/miniconda.sh; \
        }; \
    else \
        wget --tries=5 --timeout=120 --waitretry=5 \
            "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${MINICONDA_ARCH}.sh" \
            -O /tmp/miniconda.sh; \
    fi && \
    bash /tmp/miniconda.sh -b -p "${CONDA_DIR}" && \
    rm -f /tmp/miniconda.sh && \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    "${CONDA_DIR}/bin/conda" init bash && \
    echo "[BUILD] Miniconda3 installed to ${CONDA_DIR}" && \
    "${CONDA_DIR}/bin/conda" --version

# -----------------------------------------------------------------------------
# [Builder 3] Configure conda/pip mirrors and create caffe-ffi environment
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 3/5] Creating conda environment: caffe-ffi (Python ${PYTHON_VERSION}) ===" && \
    CONDA_DIR=/opt/conda && \
    if [ "${CONDA_MIRROR}" = "tuna" ]; then \
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            '  - defaults' \
            'show_channel_urls: true' \
            'default_channels:' \
            '  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main' \
            '  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            > "${CONDA_DIR}/.condarc" && \
        echo "[BUILD] Using Tsinghua TUNA conda mirror"; \
    fi && \
    if [ "${PIP_MIRROR}" = "aliyun" ]; then \
        mkdir -p /root/.config/pip && \
        printf '%s\n' \
            '[global]' \
            'index-url = https://mirrors.aliyun.com/pypi/simple/' \
            'trusted-host = mirrors.aliyun.com' \
            'retries = 10' \
            'timeout = 120' \
            > /root/.config/pip/pip.conf && \
        echo "[BUILD] Using Aliyun PyPI mirror"; \
    elif [ "${PIP_MIRROR}" = "tuna" ]; then \
        mkdir -p /root/.config/pip && \
        printf '%s\n' \
            '[global]' \
            'index-url = https://pypi.tuna.tsinghua.edu.cn/simple/' \
            'trusted-host = pypi.tuna.tsinghua.edu.cn' \
            'retries = 10' \
            'timeout = 120' \
            > /root/.config/pip/pip.conf && \
        echo "[BUILD] Using Tsinghua TUNA PyPI mirror"; \
    fi && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda create -y -n caffe-ffi python="${PYTHON_VERSION}" pip setuptools wheel numpy && \
    conda activate caffe-ffi && \
    echo "[BUILD] conda env 'caffe-ffi' created, Python: $(python --version)" && \
    pip install --no-cache-dir \
        "numpy>=2.3" \
        "protobuf>=7" \
        scikit-build-core \
        ninja \
        cmake \
        pytest \
        ipykernel \
        apache-tvm-ffi && \
    echo "[BUILD] Python dependencies installed" && \
    python -c "import tvm_ffi; print('[BUILD] tvm_ffi available:', tvm_ffi.__version__)" 2>/dev/null || \
    python -c "import tvm.ffi; print('[BUILD] tvm.ffi available')" 2>/dev/null || \
    echo "[BUILD] tvm_ffi installed (import name may vary)" && \
    conda clean -ya && \
    pip cache purge 2>/dev/null || true

# -----------------------------------------------------------------------------
# [Builder 4] Copy and build caffe-ffi
# -----------------------------------------------------------------------------
COPY projects/xuanspace/libs/caffe-ffi/ /tmp/caffe-ffi/

RUN echo "=== [Builder 4/5] Building caffe-ffi from source ===" && \
    CONDA_DIR=/opt/conda && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate caffe-ffi && \
    echo "[BUILD] caffe-ffi source files:" && \
    ls -la /tmp/caffe-ffi/ && \
    echo "[BUILD] Python executable (for cmake): $(which python)" && \
    echo "[BUILD] Python include dir: $(python -c 'import sysconfig; print(sysconfig.get_path(\"include\"))')" && \
    echo "[BUILD] Python lib dir: $(python -c 'import sysconfig; print(sysconfig.get_config_var(\"LIBDIR\"))')" && \
    echo "[BUILD] tvm-ffi location:" && \
    python -c "import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))" && \
    echo "[BUILD] Installing caffe-ffi (--no-build-isolation, CMake + Ninja, RPATH enabled)..." && \
    SKBUILD_CMAKE_ARGS="-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON;-DCMAKE_BUILD_RPATH_USE_ORIGIN=ON;-DCMAKE_SKIP_BUILD_RPATH=OFF" \
    pip install --no-cache-dir --no-build-isolation -v /tmp/caffe-ffi/ 2>&1 | tail -40 && \
    echo "[BUILD] caffe-ffi installed successfully" && \
    echo "[BUILD] Verifying ipykernel availability..." && \
    python -c "import ipykernel; print('[BUILD] ipykernel available, version:', ipykernel.__version__)" && \
    echo "[BUILD] Verifying caffe-ffi import..." && \
    python -c "import caffe_ffi; print('[BUILD] caffe_ffi imported successfully')" && \
    echo "[BUILD] Checking _caffe_ffi.so shared library dependencies..." && \
    _CAFFE_FFI_SO=$(python -c "import caffe_ffi; import os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi.so'))") && \
    echo "[BUILD] _caffe_ffi.so at: $_CAFFE_FFI_SO" && \
    ldd "$_CAFFE_FFI_SO" && \
    echo "[BUILD] All shared library dependencies resolved" && \
    rm -rf /tmp/caffe-ffi && \
    conda clean -ya && \
    pip cache purge 2>/dev/null || true && \
    echo "[BUILD] Build artifacts cleaned"

# -----------------------------------------------------------------------------
# [Builder 5] Export conda environment list for verification
# -----------------------------------------------------------------------------
RUN echo "=== [Builder 5/5] Builder stage complete ===" && \
    CONDA_DIR=/opt/conda && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && \
    conda activate caffe-ffi && \
    echo "[BUILD] Installed packages:" && \
    pip list 2>/dev/null | grep -iE "caffe|numpy|protobuf|tvm|ipykernel|scikit" && \
    echo "[BUILD] Jupyter kernels:" && \
    jupyter kernelspec list 2>/dev/null && \
    echo "[BUILD] ========== BUILDER STAGE COMPLETE =========="

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Final image with Miniconda + caffe-ffi, no build toolchain
# -----------------------------------------------------------------------------
FROM ${BASE_IMAGE}

ARG APT_MIRROR
ARG PYTHON_VERSION

LABEL maintainer="SpecWeave"
LABEL description="Caffe-FFI development environment based on jupyter-ssh-base"
LABEL version="0.1.0"

USER root
ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV ENV_NAME=caffe-ffi
ENV ENV_PATH=/opt/conda/envs/caffe-ffi
ENV PATH=/opt/conda/envs/caffe-ffi/bin:/opt/conda/bin:/opt/venv/bin:${PATH}
ENV LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:${LD_LIBRARY_PATH}

# -----------------------------------------------------------------------------
# [Runtime 1] Install minimal runtime packages (no build toolchain)
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 1/4] Installing runtime packages ===" && \
    if [ "${APT_MIRROR}" = "aliyun" ]; then \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|http://mirrors.aliyun.com|g; s|http://security.ubuntu.com|http://mirrors.aliyun.com|g' /etc/apt/sources.list 2>/dev/null || true; \
    elif [ "${APT_MIRROR}" = "tuna" ]; then \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list.d/ubuntu.sources 2>/dev/null || \
        sed -i 's|http://archive.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g; s|http://security.ubuntu.com|https://mirrors.tuna.tsinghua.edu.cn|g' /etc/apt/sources.list 2>/dev/null || true; \
    fi && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        libopenblas0 \
        libgomp1 \
        libprotobuf-dev \
    && rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] Runtime packages installed (libopenblas0, libgomp1, libprotobuf-dev)"

# -----------------------------------------------------------------------------
# [Runtime 2] Copy Miniconda + caffe-ffi environment from builder
# -----------------------------------------------------------------------------
COPY --from=builder /opt/conda /opt/conda

RUN echo "=== [Runtime 2/4] Copying conda environment from builder ===" && \
    CONDA_DIR=/opt/conda && \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    echo "[BUILD] Conda copied:" && \
    "${CONDA_DIR}/bin/conda" --version && \
    ls "${CONDA_DIR}/envs/caffe-ffi/bin/python" && \
    "${CONDA_DIR}/envs/caffe-ffi/bin/python" --version && \
    echo "[BUILD] caffe-ffi env Python available" && \
    echo "[BUILD] Configuring dynamic library search paths..." && \
    bash -c "source ${CONDA_DIR}/etc/profile.d/conda.sh && conda activate caffe-ffi && \
        TVM_FFI_DIR=\$(python -c 'import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))') && \
        CAFFE_FFI_DIR=\$(python -c 'import caffe_ffi, os; print(os.path.dirname(caffe_ffi.__file__))') && \
        echo \"[BUILD] tvm_ffi dir: \$TVM_FFI_DIR\" && \
        echo \"[BUILD] caffe_ffi dir: \$CAFFE_FFI_DIR\" && \
        echo \"${ENV_PATH}/lib\" > /etc/ld.so.conf.d/caffe-ffi.conf && \
        echo \"\$TVM_FFI_DIR\" >> /etc/ld.so.conf.d/caffe-ffi.conf && \
        echo \"\$CAFFE_FFI_DIR\" >> /etc/ld.so.conf.d/caffe-ffi.conf && \
        ldconfig && \
        echo '[BUILD] ldconfig updated with caffe-ffi library paths'" && \
    echo "[BUILD] Jupyter kernelspec:" && \
    ls /usr/local/share/jupyter/kernels/ 2>/dev/null || ls /opt/venv/share/jupyter/kernels/ 2>/dev/null || echo "[BUILD] Kernels in user dir"

# -----------------------------------------------------------------------------
# [Runtime 3] Configure conda auto-activation for jupyteruser + Jupyter kernel
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 3/4] Configuring conda auto-activation and Jupyter kernel ===" && \
    CONDA_DIR=/opt/conda && \
    printf '%s\n' \
        '#!/bin/bash' \
        'source /opt/conda/etc/profile.d/conda.sh' \
        'conda activate caffe-ffi 2>/dev/null || true' \
        > /etc/profile.d/conda-caffe-ffi.sh && \
    chmod +x /etc/profile.d/conda-caffe-ffi.sh && \
    echo "[BUILD] /etc/profile.d/conda-caffe-ffi.sh created for login shell activation" && \
    echo "" >> /home/jupyteruser/.bashrc && \
    echo "# >>> caffe-ffi conda environment >>>" >> /home/jupyteruser/.bashrc && \
    echo "source ${CONDA_DIR}/etc/profile.d/conda.sh" >> /home/jupyteruser/.bashrc && \
    echo "conda activate caffe-ffi 2>/dev/null || true" >> /home/jupyteruser/.bashrc && \
    echo "export LD_LIBRARY_PATH=/opt/conda/envs/caffe-ffi/lib:\${LD_LIBRARY_PATH}" >> /home/jupyteruser/.bashrc && \
    echo "# <<< caffe-ffi conda environment <<<" >> /home/jupyteruser/.bashrc && \
    chown jupyteruser:jupyteruser /home/jupyteruser/.bashrc && \
    echo "[BUILD] jupyteruser .bashrc configured with conda activation + LD_LIBRARY_PATH" && \
    bash -lc "source ${CONDA_DIR}/etc/profile.d/conda.sh && conda activate caffe-ffi && \
        python -m ipykernel install --name caffe-ffi --display-name 'Python 3.14 (caffe-ffi)' --prefix=/usr/local" && \
    echo "[BUILD] Jupyter kernel 'caffe-ffi' registered to /usr/local/share/jupyter/kernels/" && \
    echo "[BUILD] Verifying caffe-ffi import in login shell..." && \
    bash -lc "source ${CONDA_DIR}/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c 'import caffe_ffi; print(\"[BUILD] caffe_ffi import OK\")'" && \
    echo "[BUILD] Checking _caffe_ffi.so runtime dependencies..." && \
    bash -lc "source ${CONDA_DIR}/etc/profile.d/conda.sh && conda activate caffe-ffi && \
        _SO=\$(python -c 'import caffe_ffi,os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), \"_caffe_ffi.so\"))') && \
        echo \"[BUILD] _caffe_ffi.so: \$_SO\" && \
        ldd \"\$_SO\" && \
        if ldd \"\$_SO\" 2>&1 | grep -q 'not found'; then echo '[FAIL] Unresolved shared libraries detected!'; ldd \"\$_SO\" | grep 'not found'; exit 1; \
        else echo '[BUILD] All shared libraries resolved'; fi" && \
    echo "[BUILD] Jupyter kernels:" && \
    bash -lc "jupyter kernelspec list"

# -----------------------------------------------------------------------------
# [Runtime 4] Final cleanup and metadata
# -----------------------------------------------------------------------------
RUN echo "=== [Runtime 4/4] Final cleanup ===" && \
    echo "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" > /etc/caffe-ffi-jupyter-build-info && \
    echo "BASE_IMAGE=jupyter-ssh-base:1.1" >> /etc/caffe-ffi-jupyter-build-info && \
    echo "CONDA_DIR=/opt/conda" >> /etc/caffe-ffi-jupyter-build-info && \
    echo "ENV_NAME=caffe-ffi" >> /etc/caffe-ffi-jupyter-build-info && \
    echo "PYTHON_VERSION=${PYTHON_VERSION}" >> /etc/caffe-ffi-jupyter-build-info && \
    echo "SERVICES=sshd,jupyter,conda-caffe-ffi" >> /etc/caffe-ffi-jupyter-build-info && \
    cat /etc/caffe-ffi-jupyter-build-info && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    echo "" && \
    echo "[BUILD] ========== BUILD COMPLETE ==========" && \
    echo ""

# -----------------------------------------------------------------------------
# Runtime configuration - inherit from jupyter-ssh-base
# (WORKDIR /workspace, EXPOSE 22 8888, ENTRYPOINT via tini+entrypoint.sh, HEALTHCHECK)
# USER is inherited as root; entrypoint.sh handles privilege drop to jupyteruser
# -----------------------------------------------------------------------------
WORKDIR /workspace
