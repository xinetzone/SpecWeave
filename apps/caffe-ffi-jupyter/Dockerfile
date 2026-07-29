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
    && rm -rf /var/lib/apt/lists/* && \
    echo "[BUILD] Runtime packages installed (libgomp1 for OpenMP)"

# -----------------------------------------------------------------------------
# [Runtime 2/5] Copy Miniconda + caffe-ffi environment from builder
# -----------------------------------------------------------------------------
COPY --from=builder /opt/conda /opt/conda

RUN echo "=== [Runtime 2/5] Copying conda environment from builder ===" && \
    "${CONDA_DIR}/bin/conda" config --system --set auto_activate_base false && \
    echo "[BUILD] Conda copied: $("${CONDA_DIR}/bin/conda" --version)" && \
    test -x "${CONDA_DIR}/envs/caffe-ffi/bin/python" && \
    echo "[BUILD] caffe-ffi env Python: $("${CONDA_DIR}/envs/caffe-ffi/bin/python" --version)" && \
    echo "[BUILD] Configuring dynamic library search paths..." && \
    source "${CONDA_DIR}/etc/profile.d/conda.sh" && conda activate caffe-ffi && \
    echo "${ENV_PATH}/lib" > /etc/ld.so.conf.d/caffe-ffi.conf && \
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

# Create editable-install entrypoint inline (avoids COPY from build context,
# works reliably across WSL/Windows cross-filesystem build contexts)
COPY <<'EOENTRY' /usr/local/bin/editable-install.sh
#!/bin/bash
set -e

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[editable-install]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[editable-install]${NC} $*"; }
log_error() { echo -e "${RED}[editable-install]${NC} $*" >&2; }
log_step()  { echo -e "${CYAN}[editable-install]${NC} $*"; }

# ── Activate conda environment ──
log_step "Activating conda environment: caffe-ffi"
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
log_info "Python: $(python --version)"

# ── Editable install helper ──
# Usage: do_editable_install <name> <src_dir> [extra_cmake_args]
# Returns 0 if usable (editable OK OR pre-installed OK), 1 only on hard failure.
do_editable_install() {
    local name="$1"
    local src_dir="$2"
    local extra_cmake_args="${3:-}"
    local editable_ok=0

    if [ ! -d "$src_dir" ]; then
        log_info "$name: source directory not found ($src_dir) — using pre-installed version"
        return 0
    fi
    if [ ! -f "$src_dir/pyproject.toml" ] && [ ! -f "$src_dir/setup.py" ]; then
        log_warn "$name: $src_dir exists but no pyproject.toml/setup.py found — skipping"
        return 0
    fi

    # Determine package import name
    local pkg_name="$name"
    [ "$name" = "tvm-ffi" ] && pkg_name="tvm_ffi"
    [ "$name" = "caffe-ffi" ] && pkg_name="caffe_ffi"

    # Get currently installed version as fallback for setuptools-scm (handles
    # git-submodule / detached checkout scenarios where .git metadata is absent)
    local pre_version=""
    pre_version=$(python -c "import ${pkg_name}; print(${pkg_name}.__version__)" 2>/dev/null || echo "")
    if [ -n "$pre_version" ]; then
        export SETUPTOOLS_SCM_PRETEND_VERSION="$pre_version"
        log_info "$name: pre-installed version $pre_version — using as setuptools-scm fallback"
    fi

    log_step "$name: performing editable install from $src_dir ..."
    local pip_status=0
    if [ -n "$extra_cmake_args" ]; then
        SKBUILD_CMAKE_ARGS="$extra_cmake_args" pip install --no-cache-dir --no-build-isolation -e "$src_dir" 2>&1 | tail -25 || pip_status=$?
    else
        pip install --no-cache-dir --no-build-isolation -e "$src_dir" 2>&1 | tail -25 || pip_status=$?
    fi

    if [ $pip_status -ne 0 ]; then
        log_warn "$name: editable install failed (exit $pip_status) — keeping pre-installed version"
        unset SETUPTOOLS_SCM_PRETEND_VERSION
        return 0
    fi

    # Verify the install is actually pointing to the source directory
    local installed_file
    installed_file=$(python -c "import ${pkg_name}, os; print(os.path.dirname(${pkg_name}.__file__))" 2>/dev/null || echo "")
    if [ -n "$installed_file" ] && echo "$installed_file" | grep -q "^${src_dir}"; then
        log_info "$name: editable install OK ($(python -c "import ${pkg_name}; print(${pkg_name}.__version__)" 2>/dev/null))"
        editable_ok=1
    else
        log_warn "$name: pip reported success but package not from source dir (still using pre-installed at: $installed_file)"
    fi

    unset SETUPTOOLS_SCM_PRETEND_VERSION
    return 0
}

# ── Determine source directories ──
# Auto-detect source root: check /SpecWeave (docker-compose default), /workspace,
# or use WORKSPACE_DIR env var. Override with TVM_FFI_SRC_DIR / CAFFE_FFI_SRC_DIR.
SRC_ROOT=""
for candidate in "${WORKSPACE_DIR:-}" /SpecWeave /workspace; do
    if [ -z "$candidate" ]; then continue; fi
    if [ -d "$candidate/projects/xuanspace/vendor/tvm-ffi" ] || [ -d "$candidate/tvm-ffi" ]; then
        SRC_ROOT="$candidate"
        break
    fi
done
if [ -z "$SRC_ROOT" ]; then
    SRC_ROOT="${WORKSPACE_DIR:-/workspace}"
fi
log_info "Source root: $SRC_ROOT"

TVM_FFI_SRC_DIR="${TVM_FFI_SRC_DIR:-${SRC_ROOT}/projects/xuanspace/vendor/tvm-ffi}"
CAFFE_FFI_SRC_DIR="${CAFFE_FFI_SRC_DIR:-${SRC_ROOT}/projects/xuanspace/libs/caffe-ffi}"

# Fallback: flat layout (individual dirs mounted directly under source root)
if [ ! -d "$TVM_FFI_SRC_DIR" ] && [ -d "${SRC_ROOT}/tvm-ffi" ]; then
    TVM_FFI_SRC_DIR="${SRC_ROOT}/tvm-ffi"
fi
if [ ! -d "$CAFFE_FFI_SRC_DIR" ] && [ -d "${SRC_ROOT}/caffe-ffi" ]; then
    CAFFE_FFI_SRC_DIR="${SRC_ROOT}/caffe-ffi"
fi

# ── Fix CRLF line endings in source files (Windows/WSL mount issue) ──
# When source is mounted from Windows/NTFS, shell scripts and autotools
# configure files may have CRLF (\r\n) line endings that break Linux builds.
# Convert all text files under critical 3rdparty/ and build directories to LF.
fix_crlf() {
    local dir="$1"
    if [ ! -d "$dir" ]; then return 0; fi
    local count=0
    # Fix known autotools scripts and build files by extension pattern
    while IFS= read -r -d '' f; do
        if grep -q $'\r' "$f" 2>/dev/null; then
            sed -i 's/\r$//' "$f"
            count=$((count + 1))
        fi
    done < <(find "$dir" -type f \( -name 'configure' -o -name 'config.sub' -o -name 'config.guess' \
        -o -name 'install-sh' -o -name 'missing' -o -name 'depcomp' -o -name 'compile' \
        -o -name 'ltmain.sh' -o -name '*.sh' -o -name '*.ac' -o -name '*.am' \
        -o -name '*.in' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \) -print0 2>/dev/null)
    # Also scan 3rdparty directories more broadly for any files with CRLF (autotools
    # helper scripts may not have standard extensions)
    if [ -d "$dir/3rdparty" ]; then
        while IFS= read -r -d '' f; do
            if grep -q $'\r' "$f" 2>/dev/null; then
                sed -i 's/\r$//' "$f"
                count=$((count + 1))
            fi
        done < <(find "$dir/3rdparty" -type f -text -print0 2>/dev/null)
    fi
    if [ $count -gt 0 ]; then
        log_info "Fixed CRLF→LF in $count file(s) under $dir"
    fi
}
fix_crlf "$TVM_FFI_SRC_DIR"
fix_crlf "$CAFFE_FFI_SRC_DIR"

# ── tvm-ffi: standard pip -e install ──
do_editable_install "tvm-ffi" "$TVM_FFI_SRC_DIR"

# ── caffe-ffi: scikit-build-core CMake project with RPATH ──
# Resolve tvm-ffi cmake config dir (works for both editable and pre-installed)
TVM_FFI_CMAKE_DIR="$(python -c 'import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))' 2>/dev/null || echo '')"
CAFFE_FFI_CMAKE_ARGS="-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON;-DCMAKE_BUILD_RPATH_USE_ORIGIN=ON;-DCMAKE_SKIP_BUILD_RPATH=OFF;-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON"
if [ -n "$TVM_FFI_CMAKE_DIR" ]; then
    CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS};-Dcaffe-ffi_DIR=${TVM_FFI_CMAKE_DIR}"
    log_info "caffe-ffi: using tvm-ffi cmake dir: $TVM_FFI_CMAKE_DIR"
fi
CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS};-DCMAKE_PREFIX_PATH=$CONDA_PREFIX;-DCAFFE_FFI_BUILD_TESTS=OFF"
do_editable_install "caffe-ffi" "$CAFFE_FFI_SRC_DIR" "$CAFFE_FFI_CMAKE_ARGS"

# ── Update ldconfig for newly built .so files (root only) ──
if [ "$(id -u)" -eq 0 ]; then
    log_step "Updating dynamic linker cache (ldconfig)..."
    echo "${CONDA_PREFIX}/lib" > /etc/ld.so.conf.d/caffe-ffi.conf
    for src_dir in "$TVM_FFI_SRC_DIR" "$CAFFE_FFI_SRC_DIR"; do
        if [ -d "$src_dir/build" ]; then
            find "$src_dir/build" -name "*.so*" -type f -exec dirname {} \; 2>/dev/null | sort -u >> /etc/ld.so.conf.d/caffe-ffi.conf
        fi
    done
    ldconfig 2>/dev/null || true
    log_info "ldconfig updated"
else
    log_info "Not running as root — skipping ldconfig (set LD_LIBRARY_PATH if needed)"
fi

# ── Verify imports ──
log_step "Verifying imports..."
python -c "import numpy;            print('  numpy:      ', numpy.__version__)"
python -c "import google.protobuf;  print('  protobuf:   ', google.protobuf.__version__)"
if python -c "import tvm_ffi;        print('  tvm_ffi:    ', tvm_ffi.__version__)" 2>/dev/null; then
    :
else
    log_warn "tvm_ffi import failed — check installation"
fi
if python -c "import caffe_ffi;      print('  caffe_ffi:  ', caffe_ffi.__version__)" 2>/dev/null; then
    _SO=$(python -c "import caffe_ffi, os; print(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi.so'))" 2>/dev/null || find "$CAFFE_FFI_SRC_DIR/build" -name '_caffe_ffi.so' -type f 2>/dev/null | head -1)
    if [ -n "$_SO" ] && [ -f "$_SO" ]; then
        if ldd "$_SO" 2>/dev/null | grep -q 'not found'; then
            log_warn "_caffe_ffi.so has unresolved deps:"
            ldd "$_SO" | grep 'not found'
        else
            log_info "_caffe_ffi.so dependencies resolved"
        fi
    fi
else
    log_warn "caffe_ffi not imported — mount source to ${CAFFE_FFI_SRC_DIR} to enable editable install"
fi

log_info "Editable install phase complete. Starting service..."
echo "=========================================================================="
exec "$@"
EOENTRY
RUN chmod +x /usr/local/bin/editable-install.sh && \
    echo "[BUILD] editable-install.sh entrypoint installed"

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

# Entrypoint chain:
#   1. editable-install.sh — activates conda, runs pip install -e for mounted sources
#   2. tini               — PID 1 init for zombie reaping + signal forwarding
#   3. entrypoint.sh      — jupyter-ssh-base entrypoint (passwords, SSH, Jupyter, supervisord)
ENTRYPOINT ["/usr/local/bin/editable-install.sh"]
CMD ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]
