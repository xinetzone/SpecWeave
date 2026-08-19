# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Conda LLVM Variant
# Description: LLVM/Clang/CMake/Ninja in conda main env (Python 3.14t free-threading)
# Base: devcontainer-base:${BASE_TAG}
# Build (CN): docker build -f variants/conda-llvm/Dockerfile \
#   --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=bfsu --build-arg PIP_MIRROR=aliyun \
#   -t devcontainer-base:conda-llvm-latest .
# Verify: docker run --rm devcontainer-base:conda-llvm-latest llvm-config --version
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=bfsu
ARG PIP_MIRROR=aliyun
ARG LLVM_VERSION=22.1.8
ARG CCACHE_MAXSIZE=5G

FROM devcontainer-base:${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG LLVM_VERSION
ARG CCACHE_MAXSIZE

LABEL maintainer="SpecWeave"
LABEL description="DevContainer with LLVM/Clang/CMake/Ninja/ccache in conda main env (Python 3.14t ft)"
LABEL variant="conda-llvm"
LABEL llvm.version="${LLVM_VERSION}"
LABEL ccache.enabled="true"

ENV CONDA_DIR=/opt/conda \
    LLVM_VERSION=${LLVM_VERSION} \
    CONDA_DEFAULT_ENV=main \
    CCACHE_DIR=/ccache \
    CCACHE_MAXSIZE=${CCACHE_MAXSIZE} \
    CCACHE_COMPILERCHECK=content \
    CCACHE_SLOPPINESS=pch_defines,time_macros,include_file_mtime,include_file_ctime \
    CCACHE_NOHASHDIR=true \
    CCACHE_COMPRESS=1 \
    CCACHE_COMPRESSLEVEL=6
# ccache masquerade dir is prepended to PATH so clang/clang++ auto-wraps ccache
ENV PATH=/opt/conda/envs/main/lib/ccache/bin:/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

COPY shared/lib/ /usr/local/share/variant-framework/
COPY shared/scripts/conda-mirror-setup.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/conda-mirror-setup.sh

# ── Stage 1-2/5: Framework init + mirrors ──────────────────────────
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    <<'S12'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_start "conda-llvm"
variant_timer_stage 1 "Init + mirror configuration"
/opt/conda/bin/conda --version
test -d /opt/conda/envs/main && variant_log_ok "main env exists"
/opt/conda/envs/main/bin/python --version
variant_configure_mirrors
S12

# ── Stage 3/5: LLVM toolchain + ccache installation ───────────────
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    --mount=type=cache,target=/ccache,sharing=locked \
    <<'S3'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "LLVM toolchain + ccache installation"
variant_activate_main_env

# NOTE: lldb excluded - no cp314t build, installing it forces GIL swap.
# python=*=*cp314t guards against this regression.
conda_install_group "G1: LLVM Core (pinned ${LLVM_VERSION})" \
    "llvmdev/clangdev/clang/lld @ ${LLVM_VERSION}; python locked to cp314t" \
    "llvmdev=${LLVM_VERSION}" "clangdev=${LLVM_VERSION}" \
    "clang=${LLVM_VERSION}" "lld=${LLVM_VERSION}" "python=*=*cp314t"
conda_install_group "G2: Build Tools" "cmake/ninja/make/ccache" cmake ninja make ccache
conda_install_group "G3: GCC Runtime" "libgcc/libstdcxx for clang linking" libgcc libstdcxx-ng

assert_python_cp314t
assert_free_threading

echo "  llvm-config: $(llvm-config --version 2>&1)"
echo "  clang:       $(clang --version 2>&1 | head -1)"
echo "  cmake:       $(cmake --version 2>&1 | head -1)"
echo "  ninja:       $(ninja --version 2>&1)"
echo "  ccache:      $(ccache --version 2>&1 | head -1)"

# ── ccache masquerade setup: symlink compilers to ccache ──
# ccache auto-detects the real compiler from argv[0] basename when invoked
# via a symlink named after the compiler (clang/clang++/gcc/g++/etc.)
CCACHE_MASQ_DIR="/opt/conda/envs/main/lib/ccache/bin"
mkdir -p "$CCACHE_MASQ_DIR"
for compiler in clang clang++ cc c++ gcc g++; do
    ln -sf "$(which ccache)" "${CCACHE_MASQ_DIR}/${compiler}"
done
variant_log_ok "ccache masquerade symlinks created at ${CCACHE_MASQ_DIR}"

# Initialize ccache config and show stats
mkdir -p /ccache
ccache --set-config=max_size="${CCACHE_MAXSIZE}"
ccache --set-config=compiler_check=content
ccache -z 2>/dev/null || true
ccache -s 2>&1 | head -8

cleanup_all_aggressive
ensure_conda_permissions   # ⭐ fix /opt/conda perms IN the install layer — prevents CoW bloat in later layers
S3

# ── Stage 4/5: Symlinks + init script + ccache dir + lightweight perms ──
# NOTE: ensure_all_permissions() is intentionally NOT called here — it does
# chown -R + chmod -R on /opt/conda (2.2GB), which triggers Docker copy-on-write
# and duplicates the entire conda tree into this layer. Bulk conda perms are
# already fixed in S3 (same layer as install) for zero-cost permission setting.
RUN <<'S4'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Symlinks + init script + ccache dir"
variant_activate_main_env

if ! command -v llvm-config >/dev/null 2>&1; then
    LLVM_CONFIG_BIN=$(find /opt/conda/envs/main/bin /opt/conda/bin -name 'llvm-config*' -type f 2>/dev/null | head -1)
    [ -n "$LLVM_CONFIG_BIN" ] && ln -sf "$LLVM_CONFIG_BIN" /opt/conda/envs/main/bin/llvm-config
fi
chmod a+x /opt/conda/envs/main/bin/llvm* /opt/conda/envs/main/bin/clang* /opt/conda/envs/main/bin/lld* 2>/dev/null || true

cat > /etc/profile.d/conda-llvm-init.sh <<'INIT'
#!/bin/bash
if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
    source "/opt/conda/etc/profile.d/conda.sh"
    conda activate main 2>/dev/null || conda activate base 2>/dev/null || true
fi
INIT
chmod +x /etc/profile.d/conda-llvm-init.sh

# ── ccache cache directory permissions ──
# /ccache must be writable by all users (devuser/ai/root) for runtime compilation
mkdir -p /ccache
chmod 1777 /ccache
variant_log_ok "ccache directory /ccache ready (mode 1777, max_size=${CCACHE_MAXSIZE})"

# Lightweight perms only — no recursive chmod on /opt/conda (done in S3)
ensure_user_bashrc
ensure_profile_d_executable
llvm-config --version 2>&1 | head -1
S4

# ── Stage 5/5: Build metadata + verification + post-test cleanup ──
# NOTE: cleanup_post_tests runs AFTER verification because tests import modules
# (which creates __pycache__) and write tmp files; cleaning before tests wastes
# the cleanup as tests regenerate pycache.
RUN --mount=type=cache,target=/ccache,sharing=locked \
    <<'S5'
set +o pipefail
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 4 "Final metadata + verification + post-test cleanup"
variant_activate_main_env

variant_write_build_info "conda-llvm" "${BASE_TAG}" \
    "VARIANT_DESCRIPTION=LLVM/Clang/CMake/Ninja/ccache in conda main env (Python 3.14t ft)" \
    "LLVM_VERSION_REQUESTED=${LLVM_VERSION}" \
    "LLVM_VERSION_ACTUAL=$(llvm-config --version 2>&1 | head -1)" \
    "CLANG_VERSION_ACTUAL=$(clang --version 2>&1 | head -1 | awk '{print $3}')" \
    "CMAKE_VERSION_ACTUAL=$(cmake --version 2>&1 | head -1 | awk '{print $3}')" \
    "NINJA_VERSION_ACTUAL=$(ninja --version 2>&1)" \
    "CCACHE_VERSION_ACTUAL=$(ccache --version 2>&1 | head -1 | awk '{print $3}')" \
    "CCACHE_DIR=${CCACHE_DIR}" \
    "CCACHE_MAXSIZE=${CCACHE_MAXSIZE}" \
    "CCACHE_MASQUERADE_DIR=/opt/conda/envs/main/lib/ccache/bin" \
    "PACKAGES_INSTALLED=llvmdev,clangdev,clang,lld,cmake,ninja,make,ccache,libgcc,libstdcxx-ng" \
    "PACKAGES_EXCLUDED=lldb(no cp314t,forces GIL swap)" \
    "ACTIVATION_SCRIPT=/etc/profile.d/conda-llvm-init.sh" \
    "SLIMMING=cleanup_all_aggressive+CoW-optimized-layer-order"

verify_bash_syntax /etc/profile.d/conda-llvm-init.sh

verify_validation_header "Toolchain + Service Verification"
for cmd in llvm-config clang clang++ cmake ninja make ccache; do
    echo -n "  [VERIFY] ${cmd}... "
    command -v "$cmd" >/dev/null 2>&1 && { "$cmd" --version 2>&1 | head -1; echo "  [OK]"; } || { echo "[FAIL]"; exit 1; }
done
test -x /opt/conda/envs/main/bin/python && echo "  [OK] main env python: $(/opt/conda/envs/main/bin/python --version 2>&1)"
verify_base_services

echo -n "  [VERIFY] devuser LLVM access... "
su - devuser -c "source /opt/conda/etc/profile.d/conda.sh && conda activate main && llvm-config --version" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

# ── ccache verification ──
echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [CCACHE VERIFICATION]"
echo "└─────────────────────────────────────────────────┘"

# Verify ccache masquerade: clang should resolve through masquerade dir first
echo -n "  [VERIFY] ccache masquerade PATH precedence... "
CLANG_RESOLVED=$(which clang)
if [[ "$CLANG_RESOLVED" == *"/lib/ccache/bin/clang" ]]; then
    echo "[OK] (clang -> ${CLANG_RESOLVED})"
else
    echo "[WARN] clang resolves to ${CLANG_RESOLVED} (masquerade not first in PATH, ccache explicit invocation still works)"
fi

# Verify ccache wraps compiler correctly (direct ccache invocation)
echo -n "  [VERIFY] ccache compiler wrapping... "
ccache clang --version >/dev/null 2>&1 && echo "[OK]" || { echo "[FAIL]"; exit 1; }

# Reset ccache stats before compile test
ccache -z >/dev/null 2>&1

# C++ Hello World compile test (ccache will cache this)
echo '#include <iostream>' > /tmp/hello.cpp
echo 'int main() { std::cout << "Hello from LLVM/Clang+ccache!\n"; return 0; }' >> /tmp/hello.cpp
clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello -stdlib=libstdc++ 2>&1 || clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello 2>&1
/tmp/hello && rm -f /tmp/hello.cpp /tmp/hello
variant_log_ok "C++ Hello World test passed (compiled via ccache masquerade)"

# Show ccache stats after compile
echo "  [CCACHE STATS] after first compile:"
ccache -s 2>&1 | grep -E "cache hit|cache miss|called for|compile failed" | sed 's/^/    /'

# Verify devuser can use ccache
echo -n "  [VERIFY] devuser ccache access... "
su - devuser -c "ccache --version >/dev/null 2>&1 && ccache -s >/dev/null 2>&1" \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

echo -n "  [VERIFY] ccache dir writable by all (mode 1777)... "
if [[ "$(stat -c '%a' /ccache 2>/dev/null)" == "1777" ]] || [[ "$(stat -c '%a' /ccache 2>/dev/null)" == "777" ]]; then
    echo "[OK]"
else
    echo "[WARN] /ccache permissions: $(stat -c '%a' /ccache 2>/dev/null || echo 'unknown')"
fi

assert_python_cp314t
assert_free_threading

# ── Post-test cleanup: remove __pycache__ generated by imports, tmp test files ──
cleanup_post_tests

variant_timer_summary "conda-llvm Variant"
echo ""
echo "########################################################################"
echo "# CONDA-LLVM BUILD COMPLETE - LLVM/Clang ${LLVM_VERSION} + ccache in conda main"
echo "# ccache dir: /ccache (mount with -v ccache:/ccache for runtime persistence)"
echo "########################################################################"
S5
