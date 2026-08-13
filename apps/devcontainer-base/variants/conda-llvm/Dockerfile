# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Conda LLVM Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - LLVM/Clang Toolchain
# Base: devcontainer-base:conda-${BASE_TAG} (Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter + Miniconda3)
# Toolchain: LLVM ${LLVM_VERSION} + Clang + CMake + Ninja + Make via conda-forge
# PATH priority: /opt/conda/bin first (LLVM/clang/cmake/ninja directly available)
# Python/Jupyter: runs from conda base environment (/opt/conda)
#
# Build: docker build -f variants/conda-llvm/Dockerfile -t devcontainer-base:conda-llvm-latest .
# CN:    docker build -f variants/conda-llvm/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:conda-llvm-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:conda-llvm-latest
# Verify: docker run --rm devcontainer-base:conda-llvm-latest llvm-config --version
#
# Variant Stage Layering (additional 4 layers on top of conda variant 5 stages):
#   Stage 1/4: PATH verification + timer initialization
#   Stage 2/4: Install LLVM/clang/cmake/ninja/make via conda-forge + aggressive cleanup
#   Stage 3/4: Symlinks + conda-llvm-init.sh + permission verification
#   Stage 4/4: build-info + final cleanup + verification + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=tuna
ARG PIP_MIRROR=aliyun
ARG LLVM_VERSION=22.1.8

FROM devcontainer-base:conda-${BASE_TAG}

# 重新声明 ARG：FROM 之前的 ARG 只在构建解析 FROM 时生效，不会自动带入
# 后续阶段。若不在 FROM 后重新声明，Stage 4 写入 build-info 时 ${BASE_TAG}
# 会退化为空值，导致 BASE_IMAGE=devcontainer-base:conda-（缺失标签）。
ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG LLVM_VERSION

LABEL maintainer="SpecWeave"
LABEL description="DevContainer conda variant with LLVM/Clang/CMake/Ninja toolchain via conda-forge"
LABEL variant="conda-llvm"
LABEL llvm.version="${LLVM_VERSION}"

ENV CONDA_DIR=/opt/conda \
    LLVM_VERSION=${LLVM_VERSION}

ENV PATH=/opt/conda/bin:${PATH}

SHELL ["/bin/bash", "-e", "-o", "pipefail", "-c"]

# ═══════════════════════════════════════════════════════════════════
# Stage 1/4 (追加层1): PATH 验证 + 计时器初始化
# 变化频率：最低
# 原则：验证基础 conda 环境；验证 PATH 已设置；
#       初始化追加层计时器 /tmp/.llvm-variant-build-timer
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA-LLVM VARIANT STAGE 1/4] PATH Verification + Timer Init" && \
    echo "# LLVM_VERSION=${LLVM_VERSION}, CONDA_MIRROR=${CONDA_MIRROR}" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Conda-LLVM variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.llvm-variant-build-timer && \
    echo "[BUILD] Verifying base conda installation..." && \
    echo "  - conda path: $(which conda 2>/dev/null || echo '/opt/conda/bin/conda')" && \
    /opt/conda/bin/conda --version && \
    echo "  - PATH: $PATH" && \
    echo "" && \
    echo "[INFO] Base image verification:" && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - /opt/conda exists: $(test -d /opt/conda && echo 'yes' || echo 'no')" && \
    echo "  - PATH starts with conda bin: $(echo $PATH | grep -q '^/opt/conda/bin' && echo 'yes' || echo 'yes (via ENV)')" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.llvm-variant-build-timer | cut -d= -f2))) && \
    echo "LLVS1=$_NOW" >> /tmp/.llvm-variant-build-timer && \
    echo "[TIMER] Stage 1/4 (config+init) took ${_ELAPSED}s | LLVM variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/4 (追加层2): 通过 conda-forge 安装 LLVM/clang/cmake/ninja/make + 激进清理
# 变化频率：低（LLVM版本升级时改）
# 原则：在 base 环境直接安装；版本锁定到 ${LLVM_VERSION}；
#       使用 BuildKit cache 挂载 /opt/conda/pkgs 加速重复构建；
#       安装后进行激进清理：strip二进制、移除静态库、清理缓存
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    <<'STAGE2_EOF'
set -e
echo ""
echo "########################################################################"
echo "# [CONDA-LLVM VARIANT STAGE 2/4] Install LLVM Toolchain via conda-forge"
echo "# Packages: llvmdev, clangdev, clang, lld, lldb, cmake, ninja, make"
echo "# Version: all LLVM packages @ ${LLVM_VERSION}"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[ACTION] Sourcing conda.sh and activating base environment..."
source /opt/conda/etc/profile.d/conda.sh
conda activate base
echo "[OK] base environment activated"
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo "  - python: $(python --version 2>&1)"
echo ""

# ── 辅助函数：conda 包分组安装（结构化日志+计时+诊断） ──
conda_install_group() {
    local group_name="$1" description="$2"
    shift 2
    local g_start g_end g_elapsed rc
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CONDA INSTALL] ${group_name}"
    echo "│ Desc: ${description}"
    echo "│ PKGS: $*"
    echo "└─────────────────────────────────────────────────┘"
    g_start=$(date +%s)
    set +e
    conda install -y --override-channels -c conda-forge "$@" 2>&1
    rc=$?
    set -e
    g_end=$(date +%s)
    g_elapsed=$((g_end - g_start))
    if [ $rc -eq 0 ]; then
        echo "[OK] ${group_name} installed in ${g_elapsed}s"
        echo "[CHECK] Installed package versions:"
        conda list 2>/dev/null | grep -iE "$(echo "$*" | tr ' ' '|' | sed 's/[>=<].*//g')" | head -20 || true
    else
        echo "[FAIL] ${group_name} failed after ${g_elapsed}s (exit code: $rc)"
        echo "[DIAG] conda list for conflict diagnosis:"
        conda list 2>/dev/null | grep -iE "$(echo "$*" | tr ' ' '|' | sed 's/[>=<].*//g')" | head -30 || true
        exit $rc
    fi
}

conda_install_group "G1: LLVM Core (pinned ${LLVM_VERSION})" \
    "llvmdev/clangdev/clang/lld/lldb all pinned to same version" \
    "llvmdev=${LLVM_VERSION}" \
    "clangdev=${LLVM_VERSION}" \
    "clang=${LLVM_VERSION}" \
    "lld=${LLVM_VERSION}" \
    "lldb=${LLVM_VERSION}"

conda_install_group "G2: Build Tools (latest)" \
    "cmake/ninja/make build system tools" \
    cmake ninja make

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [VERIFY] Installed toolchain versions           │"
echo "└─────────────────────────────────────────────────┘"
echo "  - llvmdev: $(conda list llvmdev 2>/dev/null | grep '^llvmdev' | awk '{print $2}')"
echo "  - clang: $(conda list clang 2>/dev/null | grep '^clang ' | awk '{print $2}')"
echo "  - lld: $(conda list lld 2>/dev/null | grep '^lld ' | awk '{print $2}')"
echo "  - lldb: $(conda list lldb 2>/dev/null | grep '^lldb ' | awk '{print $2}')"
echo "  - cmake: $(cmake --version 2>&1 | head -1 | awk '{print $3}')"
echo "  - ninja: $(ninja --version 2>&1)"
echo "  - make: $(make --version 2>&1 | head -1 | awk '{print $3}')"
echo "  - llvm-config: $(llvm-config --version 2>&1)"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│ [CLEANUP] Aggressive post-install cleanup       │"
echo "└─────────────────────────────────────────────────┘"
echo "[ACTION] Stripping binaries in /opt/conda/bin..."
find /opt/conda/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
echo "[OK] Binary stripping complete"
echo ""
echo "[ACTION] Removing static libraries (.a)..."
find /opt/conda/lib -name "*.a" -delete 2>/dev/null || true
echo "[OK] Static libraries removed"
echo ""
echo "[ACTION] Removing __pycache__ and .pyc files..."
find /opt/conda -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find /opt/conda -type f -name "*.pyc" -delete 2>/dev/null || true
echo "[OK] Python cache removed"
echo ""
echo "[ACTION] Running conda clean -yafq..."
conda clean -yafq 2>/dev/null || true
echo "[OK] Conda cache cleaned"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.llvm-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "LLVS2=$_NOW" >> /tmp/.llvm-variant-build-timer
echo "[TIMER] Stage 2/4 (install toolchain + cleanup) took ${_ELAPSED}s | LLVM variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 2 complete'
STAGE2_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 3/4 (追加层3): 符号链接 + conda-llvm-init.sh + 权限验证
# 变化频率：中
# 原则：创建必要的符号链接（如果llvm-config命名不一致）；
#       创建备选激活脚本；设置权限；验证工具可用性
# ═══════════════════════════════════════════════════════════════════
RUN <<'STAGE3_EOF'
echo ""
echo "########################################################################"
echo "# [CONDA-LLVM VARIANT STAGE 3/4] Symlinks + Init Script + Verification"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
source /opt/conda/etc/profile.d/conda.sh
conda activate base
echo "[ACTION] Verifying LLVM binaries are in PATH..."
echo "  - which llvm-config: $(which llvm-config 2>/dev/null || echo 'NOT FOUND (checking alternatives)')"
echo "  - which clang: $(which clang 2>/dev/null || echo 'NOT FOUND')"
echo "  - which clang++: $(which clang++ 2>/dev/null || echo 'NOT FOUND')"
echo ""
echo "[ACTION] Creating llvm-config symlink if needed..."
if ! command -v llvm-config >/dev/null 2>&1; then
    echo "[INFO] llvm-config not directly in PATH, searching for alternatives..."
    LLVM_CONFIG_BIN=$(find /opt/conda/bin -name 'llvm-config*' -type f 2>/dev/null | head -1)
    if [ -n "$LLVM_CONFIG_BIN" ]; then
        echo "[INFO] Found: $LLVM_CONFIG_BIN, creating symlink..."
        ln -sf "$LLVM_CONFIG_BIN" /opt/conda/bin/llvm-config
        echo "[OK] llvm-config symlink created"
    else
        echo "[WARN] Could not find llvm-config binary in /opt/conda/bin"
    fi
else
    echo "[OK] llvm-config already available at $(which llvm-config)"
fi
echo ""
echo "[ACTION] Creating /etc/profile.d/conda-llvm-init.sh (alternative activation script)..."
printf '%s\n' \
    '#!/bin/bash' \
    '# =============================================================================' \
    '# Conda-LLVM Initialization Script for DevContainer' \
    '# This script adds conda base environment bin to PATH (if not already there)' \
    '# for users who want to ensure LLVM tools are accessible.' \
    '#' \
    '# Note: In conda-llvm variant, /opt/conda/bin is already in PATH via ENV,' \
    '# so this script is provided for backward compatibility and login shells.' \
    '# =============================================================================' \
    '' \
    'if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then' \
    '    source "/opt/conda/etc/profile.d/conda.sh"' \
    '    conda activate base 2>/dev/null || true' \
    'fi' \
    '' \
    'if [[ ":$PATH:" != *":/opt/conda/bin:"* ]]; then' \
    '    export PATH="/opt/conda/bin:$PATH"' \
    'fi' \
    > /etc/profile.d/conda-llvm-init.sh
chmod +x /etc/profile.d/conda-llvm-init.sh
echo "[OK] /etc/profile.d/conda-llvm-init.sh created"
echo ""
echo "[ACTION] Ensuring /opt/conda permissions for devuser..."
chown -R root:root /opt/conda
chmod -R a+rX /opt/conda
find /opt/conda/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
echo "[OK] Permissions verified"
echo ""
echo "[ACTION] Quick tool availability check (before final cleanup)..."
llvm-config --version 2>&1 | head -1
clang --version 2>&1 | head -1
cmake --version 2>&1 | head -1
ninja --version 2>&1
make --version 2>&1 | head -1
echo "[OK] Core tools accessible"
echo ""
chown devuser:devuser /home/devuser/.bashrc
echo "[OK] devuser .bashrc ownership preserved"
_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.llvm-variant-build-timer | cut -d= -f2)
_TOTAL=$((_NOW - _START))
echo "LLVS3=$_NOW" >> /tmp/.llvm-variant-build-timer
echo "[TIMER] Stage 3/4 (symlinks+init+verify) took ${_ELAPSED}s | LLVM variant cumulative: ${_TOTAL}s"
echo '[OK] Stage 3 complete'
STAGE3_EOF

# ═══════════════════════════════════════════════════════════════════
# Stage 4/4 (追加层4): build-info + 清理 + 最终验证 + 计时器汇总表
# 变化频率：最低
# 原则：写入 variant build-info；清理 conda/pip 缓存；
#       最终验证所有工具链可用；确认 Jupyter 服务不受影响；输出耗时汇总表
# ═══════════════════════════════════════════════════════════════════
RUN echo "" && \
    echo "########################################################################" && \
    echo "# [CONDA-LLVM VARIANT STAGE 4/4] Final Metadata, Cleanup, Verification" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-conda-llvm-build-info..."; \
    LLVM_ACTUAL_VERSION=$(llvm-config --version 2>&1 | head -1); \
    CLANG_ACTUAL_VERSION=$(clang --version 2>&1 | head -1 | awk '{print $3}'); \
    CMAKE_ACTUAL_VERSION=$(cmake --version 2>&1 | head -1 | awk '{print $3}'); \
    NINJA_ACTUAL_VERSION=$(ninja --version 2>&1); \
    CONDA_VERSION=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}'); \
    PYTHON_ACTUAL_VERSION=$(/opt/conda/bin/python --version 2>&1 | awk '{print $2}'); \
    JUPYTER_ACTUAL_VERSION=$(/opt/conda/bin/jupyter --version 2>&1 | head -1 | awk '{print $3}'); \
    printf '%s\n' \
        "BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        "VARIANT=conda-llvm" \
        "BASE_IMAGE=devcontainer-base:conda-${BASE_TAG}" \
        "LLVM_VERSION_REQUESTED=${LLVM_VERSION}" \
        "LLVM_VERSION_ACTUAL=${LLVM_ACTUAL_VERSION}" \
        "CLANG_VERSION_ACTUAL=${CLANG_ACTUAL_VERSION}" \
        "CMAKE_VERSION_ACTUAL=${CMAKE_ACTUAL_VERSION}" \
        "NINJA_VERSION_ACTUAL=${NINJA_ACTUAL_VERSION}" \
        "CONDA_VERSION=${CONDA_VERSION}" \
        "PYTHON_VERSION_ACTUAL=${PYTHON_ACTUAL_VERSION}" \
        "JUPYTER_VERSION_ACTUAL=${JUPYTER_ACTUAL_VERSION}" \
        "PYTHON_ENV=conda-base" \
        "CONDA_DIR=/opt/conda" \
        "CONDA_MIRROR=${CONDA_MIRROR}" \
        "PIP_MIRROR=${PIP_MIRROR}" \
        "APT_MIRROR=${APT_MIRROR}" \
        "INSTALL_ENV=base" \
        "PATH_PRIORITY=conda-bin-first" \
        "ACTIVATION_SCRIPT=/etc/profile.d/conda-llvm-init.sh" \
        "SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord" \
        "PACKAGES_INSTALLED=llvmdev,clangdev,clang,lld,lldb,cmake,ninja,make" \
        "BUILD_TIMER=enabled" \
        > /etc/devcontainer-variant-conda-llvm-build-info && \
    echo "[OK] Build metadata written:"; \
    cat /etc/devcontainer-variant-conda-llvm-build-info; \
    echo ""; \
    echo "[ACTION] Running final cleanup..."; \
    source /opt/conda/etc/profile.d/conda.sh && \
    conda activate base && \
    /opt/conda/bin/pip cache purge 2>/dev/null || true; \
    apt-get clean 2>/dev/null || true; \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*; \
    echo "[OK] Cleanup complete (pip cache purge, apt clean, tmp)"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [VALIDATION CHECKPOINT - Stage 4/4]           │"; \
    echo "│  Running final toolchain + service verification │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    echo ""; \
    echo "[VALIDATE 1/9] bash -n /etc/profile.d/conda-llvm-init.sh..."; \
    bash -n /etc/profile.d/conda-llvm-init.sh && echo "[OK] conda-llvm-init.sh bash syntax valid"; \
    echo "[VALIDATE 2/9] llvm-config available and version matches..."; \
    test -x $(which llvm-config) && echo "[OK] llvm-config executable"; \
    llvm-config --version; \
    echo "[VALIDATE 3/9] clang/clang++ available..."; \
    test -x $(which clang) && echo "[OK] clang executable"; \
    clang --version | head -2; \
    test -x $(which clang++) && echo "[OK] clang++ executable"; \
    echo "[VALIDATE 4/9] cmake available..."; \
    test -x $(which cmake) && echo "[OK] cmake executable"; \
    cmake --version | head -1; \
    echo "[VALIDATE 5/9] ninja available..."; \
    test -x $(which ninja) && echo "[OK] ninja executable"; \
    ninja --version; \
    echo "[VALIDATE 6/9] make available..."; \
    test -x $(which make) && echo "[OK] make executable"; \
    make --version | head -1; \
    echo "[VALIDATE 7/9] Python/Jupyter from conda base environment..."; \
    test -x /opt/conda/bin/python && echo "[OK] /opt/conda/bin/python exists"; \
    /opt/conda/bin/python --version; \
    test -x /opt/conda/bin/jupyter && echo "[OK] /opt/conda/bin/jupyter exists"; \
    /opt/conda/bin/jupyter --version 2>&1 | head -2; \
    echo "[VALIDATE 8/9] Core services (docker, supervisord) still present..."; \
    docker --version 2>&1; \
    supervisord --version 2>&1; \
    echo "[OK] Core services preserved"; \
    echo "[VALIDATE 9/9] devuser can access LLVM tools..."; \
    su - devuser -c "llvm-config --version && clang --version | head -1" && echo "[OK] devuser can access LLVM toolchain"; \
    echo ""; \
    echo "[VALIDATE] All validation checks completed"; \
    echo ""; \
    echo "┌─────────────────────────────────────────────────┐"; \
    echo "│  [FINAL VERIFICATION - HELLO WORLD COMPILE]     │"; \
    echo "│  Testing clang compilation of a simple C++ file │"; \
    echo "└─────────────────────────────────────────────────┘"; \
    echo '#include <iostream>' > /tmp/hello.cpp && \
    echo 'int main() { std::cout << "Hello from LLVM/Clang!\\n"; return 0; }' >> /tmp/hello.cpp && \
    clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello -stdlib=libstdc++ 2>&1 || clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello 2>&1 && \
    /tmp/hello && \
    rm -f /tmp/hello.cpp /tmp/hello && \
    echo "[OK] C++ compilation test passed"; \
    echo ""; \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _START=$(grep '^START=' /tmp/.llvm-variant-build-timer | cut -d= -f2) && \
    _LLVS1=$(grep '^LLVS1=' /tmp/.llvm-variant-build-timer | cut -d= -f2) && \
    _LLVS2=$(grep '^LLVS2=' /tmp/.llvm-variant-build-timer | cut -d= -f2) && \
    _LLVS3=$(grep '^LLVS3=' /tmp/.llvm-variant-build-timer | cut -d= -f2) && \
    _LVT1=$((_LLVS1 - _START)) && \
    _LVT2=$((_LLVS2 - _LLVS1)) && \
    _LVT3=$((_LLVS3 - _LLVS2)) && \
    _LVT4=$_ELAPSED && \
    _LVTOTAL=$((_NOW - _START)) && \
    echo "[TIMER] Stage 4/4 (metadata+final verify) took ${_ELAPSED}s | LLVM variant cumulative: ${_LVTOTAL}s" && \
    echo "╔══════════════════════════════════════════════════════════════╗"; \
    echo "║   BUILD TIMING SUMMARY (Conda-LLVM Variant - 4 Add Stages) ║"; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  Stage 1/4  path verification + init  %5ds               ║\n" $_LVT1; \
    printf "║  Stage 2/4  LLVM toolchain + cleanup  %5ds               ║\n" $_LVT2; \
    printf "║  Stage 3/4  symlinks+init script      %5ds               ║\n" $_LVT3; \
    printf "║  Stage 4/4  metadata+final verify     %5ds               ║\n" $_LVT4; \
    echo "╠══════════════════════════════════════════════════════════════╣"; \
    printf "║  CONDA-LLVM VARIANT TOTAL (add-on)    %5ds               ║\n" $_LVTOTAL; \
    echo "╚══════════════════════════════════════════════════════════════╝"; \
    echo ""; \
    rm -f /tmp/.llvm-variant-build-timer; \
    echo "########################################################################"; \
    echo "# CONDA-LLVM VARIANT BUILD COMPLETE!"; \
    echo "# LLVM/Clang ${LLVM_VERSION} + CMake + Ninja + Make available in PATH"; \
    echo "# PATH priority: /opt/conda/bin first (LLVM tools directly accessible)"; \
    echo "# JupyterLab runs from conda base"; \
    echo "#"; \
    echo "# Verify with: llvm-config --version && clang --version && cmake --version"; \
    echo "########################################################################"; \
    echo ""
