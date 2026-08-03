#!/bin/bash
set -e

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
log_info()  { echo -e "${GREEN}[editable-install]${NC} $*"; }
log_warn()  { echo -e "${YELLOW}[editable-install]${NC} $*"; }
log_error() { echo -e "${RED}[editable-install]${NC} $*" >&2; }
log_step()  { echo -e "${CYAN}[editable-install]${NC} $*"; }

export KMP_DUPLICATE_LIB_OK=TRUE

# ── Activate conda environment ──
log_step "Activating conda environment: caffe-ffi"
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
log_info "Python: $(python --version)"

# ── Pre-build environment fixes ──
# Fix libopenblas.so symlink (conda only ships libopenblas.so.0, but cmake looks for .so)
if [ -d "$CONDA_PREFIX/lib" ]; then
    if [ ! -f "$CONDA_PREFIX/lib/libopenblas.so" ] && [ -f "$CONDA_PREFIX/lib/libopenblas.so.0" ]; then
        ln -sf libopenblas.so.0 "$CONDA_PREFIX/lib/libopenblas.so"
        log_info "Created libopenblas.so -> libopenblas.so.0 symlink"
    fi
fi

# ── Editable install helper ──
# Usage: do_editable_install <name> <src_dir> [extra_cmake_args]
# Returns 0 if usable (editable OK OR pre-installed OK OR already installed), 1 only on hard failure.
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

    # ── Check if already installed from source directory (skip rebuild) ──
    local installed_file=""
    installed_file=$(python -c "import ${pkg_name}, os; print(os.path.dirname(${pkg_name}.__file__))" 2>/dev/null || echo "")
    if [ -n "$installed_file" ] && echo "$installed_file" | grep -q "^${src_dir}"; then
        # Package is already in editable mode from this source dir — check .so deps
        local so_file=""
        so_file=$(python -c "import ${pkg_name}, os, glob; sos=glob.glob(os.path.join(os.path.dirname(${pkg_name}.__file__), '_${pkg_name}*.so')); print(sos[0] if sos else '')" 2>/dev/null || echo "")
        local needs_rebuild=0
        if [ -n "$so_file" ] && [ -f "$so_file" ]; then
            if ldd "$so_file" 2>/dev/null | grep -q 'not found'; then
                log_warn "$name: editable install exists but .so has unresolved deps — rebuilding"
                needs_rebuild=1
            else
                local ver
                ver=$(python -c "import ${pkg_name}; print(${pkg_name}.__version__)" 2>/dev/null || echo "?")
                log_info "$name: already installed from source ($ver) — skipping rebuild"
                return 0
            fi
        else
            log_info "$name: editable install exists but no .so found — rebuilding"
            needs_rebuild=1
        fi
        if [ $needs_rebuild -eq 0 ]; then
            return 0
        fi
    fi

    # Get currently installed version as fallback for setuptools-scm (handles
    # git-submodule / detached checkout scenarios where .git metadata is absent)
    local pre_version=""
    pre_version=$(python -c "import ${pkg_name}; print(${pkg_name}.__version__)" 2>/dev/null || echo "")
    if [ -n "$pre_version" ]; then
        export SETUPTOOLS_SCM_PRETEND_VERSION="$pre_version"
        log_info "$name: pre-installed version $pre_version — using as setuptools-scm fallback"
    fi

    # Clean stale CMake cache from previous failed builds (Windows mount issue)
    if [ -d "$src_dir/build" ]; then
        if [ -f "$src_dir/build/CMakeCache.txt" ]; then
            # Check if cache references paths that no longer exist
            if grep -q "CMAKE_CACHEFILE_DIR" "$src_dir/build/CMakeCache.txt" 2>/dev/null; then
                local cached_dir
                cached_dir=$(grep "CMAKE_CACHEFILE_DIR" "$src_dir/build/CMakeCache.txt" | head -1 | cut -d'=' -f2)
                if [ -n "$cached_dir" ] && [ ! -d "$cached_dir" ]; then
                    log_warn "$name: stale build cache found (dir: $cached_dir not found) — cleaning"
                    rm -rf "$src_dir/build"
                fi
            fi
        fi
    fi

    log_step "$name: performing editable install from $src_dir ..."
    local pip_status=0
    if [ -n "$extra_cmake_args" ]; then
        SKBUILD_CMAKE_ARGS="$extra_cmake_args" pip install --no-cache-dir --no-build-isolation -e "$src_dir" 2>&1 | tail -25 || pip_status=$?
    else
        pip install --no-cache-dir --no-build-isolation -e "$src_dir" 2>&1 | tail -25 || pip_status=$?
    fi

    if [ $pip_status -ne 0 ]; then
        # Retry once after cleaning build directory
        log_warn "$name: first build attempt failed (exit $pip_status) — cleaning build dir and retrying..."
        rm -rf "$src_dir/build"
        pip_status=0
        if [ -n "$extra_cmake_args" ]; then
            SKBUILD_CMAKE_ARGS="$extra_cmake_args" pip install --no-cache-dir --no-build-isolation -e "$src_dir" 2>&1 | tail -25 || pip_status=$?
        else
            pip install --no-cache-dir --no-build-isolation -e "$src_dir" 2>&1 | tail -25 || pip_status=$?
        fi
    fi

    if [ $pip_status -ne 0 ]; then
        log_warn "$name: editable install failed after retry (exit $pip_status) — keeping pre-installed version"
        unset SETUPTOOLS_SCM_PRETEND_VERSION
        return 0
    fi

    # Verify the install is actually pointing to the source directory
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
    while IFS= read -r -d '' f; do
        if grep -q $'\r' "$f" 2>/dev/null; then
            sed -i 's/\r$//' "$f"
            count=$((count + 1))
        fi
    done < <(find "$dir" -type f \( -name 'configure' -o -name 'config.sub' -o -name 'config.guess' \
        -o -name 'install-sh' -o -name 'missing' -o -name 'depcomp' -o -name 'compile' \
        -o -name 'ltmain.sh' -o -name '*.sh' -o -name '*.ac' -o -name '*.am' \
        -o -name '*.in' -o -name '*.cmake' -o -name 'CMakeLists.txt' -o -name '*.py' \) -print0 2>/dev/null)
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

# ── tvm-ffi: install with libbacktrace disabled (avoids build failures) ──
TVM_FFI_CMAKE_ARGS="-DTVM_FFI_USE_LIBBACKTRACE=OFF"
do_editable_install "tvm-ffi" "$TVM_FFI_SRC_DIR" "$TVM_FFI_CMAKE_ARGS"

# ── caffe-ffi: scikit-build-core CMake project with RPATH + backtrace disabled ──
TVM_FFI_CMAKE_DIR="$(python -c 'import tvm_ffi, os; print(os.path.dirname(tvm_ffi.__file__))' 2>/dev/null || echo '')"
CAFFE_FFI_CMAKE_ARGS="-DCMAKE_INSTALL_RPATH_USE_LINK_PATH=ON;-DCMAKE_BUILD_RPATH_USE_ORIGIN=ON;-DCMAKE_SKIP_BUILD_RPATH=OFF;-DCMAKE_BUILD_WITH_INSTALL_RPATH=ON"
CAFFE_FFI_CMAKE_ARGS="${CAFFE_FFI_CMAKE_ARGS};-DCAFFE_FFI_ENABLE_BACKTRACE=OFF"
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
