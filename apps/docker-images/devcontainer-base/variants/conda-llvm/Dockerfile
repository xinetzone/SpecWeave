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

FROM devcontainer-base:${BASE_TAG}

ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG LLVM_VERSION

LABEL maintainer="SpecWeave"
LABEL description="DevContainer with LLVM/Clang/CMake/Ninja in conda main env (Python 3.14t ft)"
LABEL variant="conda-llvm"
LABEL llvm.version="${LLVM_VERSION}"

ENV CONDA_DIR=/opt/conda \
    LLVM_VERSION=${LLVM_VERSION} \
    CONDA_DEFAULT_ENV=main
ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

COPY variants/shared/lib/ /usr/local/share/variant-framework/
COPY variants/shared/scripts/conda-mirror-setup.sh /usr/local/bin/
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

# ── Stage 3/5: LLVM toolchain installation ─────────────────────────
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    <<'S3'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 2 "LLVM toolchain installation"
variant_activate_main_env

# NOTE: lldb excluded - no cp314t build, installing it forces GIL swap.
# python=*=*cp314t guards against this regression.
conda_install_group "G1: LLVM Core (pinned ${LLVM_VERSION})" \
    "llvmdev/clangdev/clang/lld @ ${LLVM_VERSION}; python locked to cp314t" \
    "llvmdev=${LLVM_VERSION}" "clangdev=${LLVM_VERSION}" \
    "clang=${LLVM_VERSION}" "lld=${LLVM_VERSION}" "python=*=*cp314t"
conda_install_group "G2: Build Tools" "cmake/ninja/make" cmake ninja make
conda_install_group "G3: GCC Runtime" "libgcc/libstdcxx for clang linking" libgcc libstdcxx-ng

assert_python_cp314t
assert_free_threading

echo "  llvm-config: $(llvm-config --version 2>&1)"
echo "  clang:       $(clang --version 2>&1 | head -1)"
echo "  cmake:       $(cmake --version 2>&1 | head -1)"
echo "  ninja:       $(ninja --version 2>&1)"

cleanup_binaries
cleanup_pycache
cleanup_conda_pip_cache
S3

# ── Stage 4/5: Symlinks + init script + permissions ────────────────
RUN <<'S4'
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 3 "Symlinks + init script + permissions"
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

ensure_all_permissions
llvm-config --version 2>&1 | head -1
S4

# ── Stage 5/5: Build metadata + cleanup + verification ─────────────
RUN <<'S5'
set +o pipefail
source /usr/local/share/variant-framework/variant-framework.sh
variant_timer_stage 4 "Final metadata + cleanup + verification"
variant_activate_main_env

variant_write_build_info "conda-llvm" "${BASE_TAG}" \
    "VARIANT_DESCRIPTION=LLVM/Clang/CMake/Ninja in conda main env (Python 3.14t ft)" \
    "LLVM_VERSION_REQUESTED=${LLVM_VERSION}" \
    "LLVM_VERSION_ACTUAL=$(llvm-config --version 2>&1 | head -1)" \
    "CLANG_VERSION_ACTUAL=$(clang --version 2>&1 | head -1 | awk '{print $3}')" \
    "CMAKE_VERSION_ACTUAL=$(cmake --version 2>&1 | head -1 | awk '{print $3}')" \
    "NINJA_VERSION_ACTUAL=$(ninja --version 2>&1)" \
    "PACKAGES_INSTALLED=llvmdev,clangdev,clang,lld,cmake,ninja,make,libgcc,libstdcxx-ng" \
    "PACKAGES_EXCLUDED=lldb(no cp314t,forces GIL swap)" \
    "ACTIVATION_SCRIPT=/etc/profile.d/conda-llvm-init.sh"

cleanup_all
verify_bash_syntax /etc/profile.d/conda-llvm-init.sh

verify_validation_header "Toolchain + Service Verification"
for cmd in llvm-config clang clang++ cmake ninja make; do
    echo -n "  [VERIFY] ${cmd}... "
    command -v "$cmd" >/dev/null 2>&1 && { "$cmd" --version 2>&1 | head -1; echo "  [OK]"; } || { echo "[FAIL]"; exit 1; }
done
test -x /opt/conda/envs/main/bin/python && echo "  [OK] main env python: $(/opt/conda/envs/main/bin/python --version 2>&1)"
verify_base_services

echo -n "  [VERIFY] devuser LLVM access... "
su - devuser -c "source /opt/conda/etc/profile.d/conda.sh && conda activate main && llvm-config --version" >/dev/null 2>&1 \
    && echo "[OK]" || { echo "[FAIL]"; exit 1; }

assert_python_cp314t
assert_free_threading

# C++ Hello World compile test
echo '#include <iostream>' > /tmp/hello.cpp
echo 'int main() { std::cout << "Hello from LLVM/Clang!\n"; return 0; }' >> /tmp/hello.cpp
clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello -stdlib=libstdc++ 2>&1 || clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello 2>&1
/tmp/hello && rm -f /tmp/hello.cpp /tmp/hello
variant_log_ok "C++ Hello World test passed"

variant_timer_summary "conda-llvm Variant"
echo ""
echo "########################################################################"
echo "# CONDA-LLVM BUILD COMPLETE - LLVM/Clang ${LLVM_VERSION} in conda main"
echo "########################################################################"
S5
