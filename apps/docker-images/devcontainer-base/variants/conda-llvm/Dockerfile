# syntax=docker/dockerfile:1.7-labs
# =============================================================================
# DevContainer Base - Conda LLVM Variant Dockerfile
# Project: SpecWeave Full-featured Development Container - LLVM/Clang Toolchain
# Base: devcontainer-base:${BASE_TAG} (Ubuntu 26.04 + SSH + Docker DinD + Podman + Jupyter + Miniforge3 conda-forge)
# Toolchain: LLVM ${LLVM_VERSION} + Clang + CMake + Ninja + Make via conda-forge
# Install target: conda **main** environment (Python 3.14t free-threading, default user env)
# PATH priority: /opt/conda/envs/main/bin first (LLVM/clang/cmake/ninja + Python/Jupyter)
# Python/Jupyter: runs from conda main environment (/opt/conda/envs/main, Python 3.14.6 ft)
#
# Build: docker build -f variants/conda-llvm/Dockerfile -t devcontainer-base:conda-llvm-latest .
# CN:    docker build -f variants/conda-llvm/Dockerfile \
#          --build-arg APT_MIRROR=aliyun --build-arg CONDA_MIRROR=bfsu --build-arg PIP_MIRROR=aliyun \
#          -t devcontainer-base:conda-llvm-latest .
# Run:   docker run -d --privileged -p 2222:22 -p 2375:2375 -p 8888:8888 \
#          -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \
#          -v $(pwd)/workspace:/workspace -v docker-data:/var/lib/docker \
#          devcontainer-base:conda-llvm-latest
# Verify: docker run --rm devcontainer-base:conda-llvm-latest llvm-config --version
#
# Variant Stage Layering (additional 4 layers on top of base image 7 stages):
#   Stage 1/4: PATH verification (main env first) + timer initialization
#   Stage 2/4: Install LLVM/clang/cmake/ninja/make into **main** env + aggressive cleanup
#   Stage 3/4: Symlinks + permissions + verification in main env
#   Stage 4/4: build-info + final cleanup + verification + timing summary
#
# Build Timing: 每个Stage结束时输出 [TIMER] 本阶段耗时+累计耗时，最终输出汇总表
# =============================================================================

ARG BASE_TAG=latest
ARG APT_MIRROR=official
ARG CONDA_MIRROR=bfsu
ARG PIP_MIRROR=aliyun
ARG LLVM_VERSION=22.1.8

FROM devcontainer-base:${BASE_TAG}

# 重新声明 ARG：FROM 之前的 ARG 只在构建解析 FROM 时生效，不会自动带入
# 后续阶段。若不在 FROM 后重新声明，Stage 4 写入 build-info 时 ${BASE_TAG}
# 会退化为空值，导致 BASE_IMAGE=devcontainer-base:（缺失标签）。
ARG BASE_TAG
ARG APT_MIRROR
ARG CONDA_MIRROR
ARG PIP_MIRROR
ARG LLVM_VERSION

LABEL maintainer="SpecWeave"
LABEL description="DevContainer variant with LLVM/Clang/CMake/Ninja toolchain in conda main env (Python 3.14t)"
LABEL variant="conda-llvm"
LABEL llvm.version="${LLVM_VERSION}"
LABEL conda.env="main (Python 3.14 free-threading)"

ENV CONDA_DIR=/opt/conda \
    LLVM_VERSION=${LLVM_VERSION} \
    CONDA_DEFAULT_ENV=main

# main env bin first (LLVM/clang/cmake/ninja + Python 3.14t/Jupyter), then base conda bin
ENV PATH=/opt/conda/envs/main/bin:/opt/conda/bin:${PATH}

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
    echo "# LLVM_VERSION=${LLVM_VERSION}, CONDA_MIRROR=${CONDA_MIRROR}, INSTALL_ENV=main" && \
    echo "########################################################################" && \
    echo "" && \
    _STAGE_START=$(date +%s) && \
    echo "[TIMER] Conda-LLVM variant build started at $(date -u +%Y-%m-%dT%H:%M:%SZ)" && \
    echo "START=$_STAGE_START" > /tmp/.llvm-variant-build-timer && \
    echo "[BUILD] Verifying base conda installation..." && \
    echo "  - conda path: $(which conda 2>/dev/null || echo '/opt/conda/bin/conda')" && \
    /opt/conda/bin/conda --version && \
    echo "  - conda envs available:" && \
    /opt/conda/bin/conda env list && \
    echo "  - PATH: $PATH" && \
    echo "" && \
    echo "[INFO] Base image verification:" && \
    echo "  - devuser exists: $(id devuser 2>&1 | head -1)" && \
    echo "  - /opt/conda exists: $(test -d /opt/conda && echo 'yes' || echo 'no')" && \
    echo "  - main env exists: $(test -d /opt/conda/envs/main && echo 'yes' || echo 'no')" && \
    echo "  - main env python (expected 3.14t): $(test -x /opt/conda/envs/main/bin/python && /opt/conda/envs/main/bin/python --version 2>&1 || echo 'NOT FOUND')" && \
    echo "  - PATH starts with main env bin: $(echo $PATH | grep -q '^/opt/conda/envs/main/bin' && echo 'yes' || echo 'checking...')" && \
    _NOW=$(date +%s) && \
    _ELAPSED=$((_NOW - _STAGE_START)) && \
    _TOTAL=$((_NOW - $(grep '^START=' /tmp/.llvm-variant-build-timer | cut -d= -f2))) && \
    echo "LLVS1=$_NOW" >> /tmp/.llvm-variant-build-timer && \
    echo "[TIMER] Stage 1/4 (config+init) took ${_ELAPSED}s | LLVM variant cumulative: ${_TOTAL}s" && \
    echo '[OK] Stage 1 complete'

# ═══════════════════════════════════════════════════════════════════
# Stage 2/4 (追加层2): 通过 conda-forge 安装 LLVM/clang/cmake/ninja/make + 激进清理
# 变化频率：低（LLVM版本升级时改）
# 原则：在 main 环境（Python 3.14t free-threading，默认用户环境）安装；
#       版本锁定到 ${LLVM_VERSION}；
#       使用 BuildKit cache 挂载 /opt/conda/pkgs 加速重复构建；
#       安装后进行激进清理：strip二进制、移除静态库、清理缓存
# ═══════════════════════════════════════════════════════════════════
RUN --mount=type=cache,target=/opt/conda/pkgs,sharing=locked \
    <<'STAGE2_EOF'
set -e
echo ""
echo "########################################################################"
echo "# [CONDA-LLVM VARIANT STAGE 2/4] Install LLVM Toolchain via conda-forge"
echo "# Packages: llvmdev, clangdev, clang, lld, cmake, ninja, make, libgcc, libstdcxx-ng"
echo "# Excluded: lldb (no cp314t build; would force python GIL swap)"
echo "# Version: all LLVM packages @ ${LLVM_VERSION}"
echo "# Target env: main (Python 3.14t free-threading, default user env)"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
echo "[ACTION] Sourcing conda.sh and activating main environment (default user env)..."
source /opt/conda/etc/profile.d/conda.sh
conda activate main
echo "[OK] main environment activated"
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo "  - python: $(python --version 2>&1)"
echo "  - python path: $(which python)"
echo ""

echo "[ACTION] Configuring conda mirror based on CONDA_MIRROR=${CONDA_MIRROR}..."
case "${CONDA_MIRROR}" in
    bfsu)
        echo "[INFO] Using BFSU (Beijing Foreign Studies University) mirror"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.bfsu.edu.cn/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.bfsu.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 300' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > /opt/conda/.condarc
        ;;
    tuna)
        echo "[INFO] Using Tsinghua TUNA mirror"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 300' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > /opt/conda/.condarc
        ;;
    aliyun)
        echo "[INFO] Using Aliyun mirror"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'default_channels_alias: https://mirrors.aliyun.com/anaconda/cloud' \
            'custom_channels:' \
            '  conda-forge: https://mirrors.aliyun.com/anaconda/cloud' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 300' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > /opt/conda/.condarc
        ;;
    *)
        echo "[INFO] Using official conda-forge channels (no mirror)"
        printf '%s\n' \
            'channels:' \
            '  - conda-forge' \
            'show_channel_urls: true' \
            'channel_priority: strict' \
            'ssl_verify: true' \
            'auto_activate_base: false' \
            'remote_connect_timeout_secs: 30' \
            'remote_read_timeout_secs: 300' \
            'remote_max_retries: 5' \
            'remote_backoff_factor: 3' \
            'repodata_threads: 8' \
            'execute_threads: 8' \
            'solver: libmamba' \
            > /opt/conda/.condarc
        ;;
esac
echo "[OK] .condarc configured:"
cat /opt/conda/.condarc
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

# NOTE: lldb is intentionally EXCLUDED. Its python bindings have no cp314t
# (free-threading) build on conda-forge, so installing it makes the solver
# silently swap python from *_cp314t (nogil) to *_cp314 + python-gil (GIL).
# python is explicitly pinned to the cp314t build as a regression guard;
# if a future package forces the GIL build, the solve will FAIL here instead.
conda_install_group "G1: LLVM Core (pinned ${LLVM_VERSION})" \
    "llvmdev/clangdev/clang/lld pinned; python locked to free-threading build" \
    "llvmdev=${LLVM_VERSION}" \
    "clangdev=${LLVM_VERSION}" \
    "clang=${LLVM_VERSION}" \
    "lld=${LLVM_VERSION}" \
    "python=*=*cp314t"

conda_install_group "G2: Build Tools (latest)" \
    "cmake/ninja/make build system tools" \
    cmake ninja make

# G3: GCC runtime libs required by the conda-forge clang linker
# (x86_64-conda-linux-gnu-ld needs -lgcc / -lstdc++ to link C/C++ binaries;
#  without them every user compilation fails with "cannot find -lgcc")
conda_install_group "G3: GCC Runtime (for clang linking)" \
    "libgcc/libstdcxx runtime libraries" \
    libgcc libstdcxx-ng

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [GUARD] free-threading python integrity check   │"
echo "└─────────────────────────────────────────────────┘"
PY_BUILD=$(conda list python 2>/dev/null | grep '^python ' | awk '{print $3}')
echo "  - python build string: ${PY_BUILD}"
case "$PY_BUILD" in
    *cp314t*) echo "[OK] python is free-threading (cp314t) build" ;;
    *) echo "[FATAL] python lost free-threading build (got: ${PY_BUILD})"
       echo "        A package in G1-G3 forced the GIL build - check the solver transaction above."
       exit 1 ;;
esac
GIL_STATE=$(python -c "import sys; print(sys._is_gil_enabled())" 2>&1)
echo "  - sys._is_gil_enabled(): ${GIL_STATE}"
if [ "$GIL_STATE" = "False" ]; then
    echo "[OK] GIL is disabled - nogil runtime active"
else
    echo "[FATAL] GIL is enabled - free-threading is NOT active"
    exit 1
fi

echo ""
echo "┌─────────────────────────────────────────────────┐"
echo "│ [VERIFY] Installed toolchain versions           │"
echo "└─────────────────────────────────────────────────┘"
echo "  - llvmdev: $(conda list llvmdev 2>/dev/null | grep '^llvmdev' | awk '{print $2}')"
echo "  - clang: $(conda list clang 2>/dev/null | grep '^clang ' | awk '{print $2}')"
echo "  - lld: $(conda list lld 2>/dev/null | grep '^lld ' | awk '{print $2}')"
echo "  - lldb: EXCLUDED (no cp314t build; would force python GIL swap)"
echo "  - cmake: $(cmake --version 2>&1 | head -1 | awk '{print $3}')"
echo "  - ninja: $(ninja --version 2>&1)"
echo "  - make: $(make --version 2>&1 | head -1 | awk '{print $3}')"
echo "  - llvm-config: $(llvm-config --version 2>&1)"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│ [CLEANUP] Aggressive post-install cleanup       │"
echo "└─────────────────────────────────────────────────┘"
echo "[ACTION] Stripping binaries in conda env bin dirs..."
find /opt/conda/envs/main/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
find /opt/conda/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
echo "[OK] Binary stripping complete"
echo ""
echo "[ACTION] Removing static libraries (.a) - preserving libgcc*/libstdc++ needed by the linker..."
find /opt/conda/envs/main/lib -name "*.a" ! -name "libgcc*" ! -name "libstdc++*" -delete 2>/dev/null || true
find /opt/conda/lib -name "*.a" ! -name "libgcc*" ! -name "libstdc++*" -delete 2>/dev/null || true
echo "[OK] Static libraries removed (gcc runtime libs preserved)"
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
conda activate main
echo "[ACTION] Verifying LLVM binaries are in PATH (main env)..."
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo "  - which llvm-config: $(which llvm-config 2>/dev/null || echo 'NOT FOUND (checking alternatives)')"
echo "  - which clang: $(which clang 2>/dev/null || echo 'NOT FOUND')"
echo "  - which clang++: $(which clang++ 2>/dev/null || echo 'NOT FOUND')"
echo ""
echo "[ACTION] Creating llvm-config symlink if needed..."
if ! command -v llvm-config >/dev/null 2>&1; then
    echo "[INFO] llvm-config not directly in PATH, searching for alternatives..."
    LLVM_CONFIG_BIN=$(find /opt/conda/envs/main/bin /opt/conda/bin -name 'llvm-config*' -type f 2>/dev/null | head -1)
    if [ -n "$LLVM_CONFIG_BIN" ]; then
        echo "[INFO] Found: $LLVM_CONFIG_BIN, creating symlink..."
        ln -sf "$LLVM_CONFIG_BIN" /opt/conda/envs/main/bin/llvm-config
        echo "[OK] llvm-config symlink created in main env bin"
    else
        echo "[WARN] Could not find llvm-config binary"
    fi
else
    echo "[OK] llvm-config already available at $(which llvm-config)"
fi
echo ""
echo "[ACTION] Ensuring LLVM tools are accessible via PATH priority..."
# main env bin is already in PATH via conda activation and /etc/environment,
# ensure all critical tools have execute permission
chmod a+x /opt/conda/envs/main/bin/llvm* /opt/conda/envs/main/bin/clang* /opt/conda/envs/main/bin/lld* 2>/dev/null || true
echo "[OK] Tool permissions set"
echo ""
echo "[ACTION] Updating conda-init.sh to ensure main env is default..."
# conda-init.sh already activates main, no need for separate conda-llvm-init.sh
# but we keep backward compatibility
printf '%s\n' \
    '#!/bin/bash' \
    '# =============================================================================' \
    '# Conda-LLVM Initialization Script for DevContainer' \
    '# LLVM/clang/cmake/ninja toolchain is installed in conda main environment' \
    '# (Python 3.14t free-threading), which is the default user environment.' \
    '# This script ensures main environment is activated on login.' \
    '# =============================================================================' \
    '' \
    'if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then' \
    '    source "/opt/conda/etc/profile.d/conda.sh"' \
    '    conda activate main 2>/dev/null || conda activate base 2>/dev/null || true' \
    'fi' \
    '' \
    > /etc/profile.d/conda-llvm-init.sh
chmod +x /etc/profile.d/conda-llvm-init.sh
echo "[OK] /etc/profile.d/conda-llvm-init.sh updated (main env first)"
echo ""
echo "[ACTION] Ensuring /opt/conda permissions for devuser..."
chown -R root:root /opt/conda
chmod -R a+rX /opt/conda
find /opt/conda/envs/main/bin -type f -executable -exec chmod a+x {} \; 2>/dev/null || true
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
RUN <<'STAGE4_EOF'
echo ""
echo "########################################################################"
echo "# [CONDA-LLVM VARIANT STAGE 4/4] Final Metadata, Cleanup, Verification"
echo "########################################################################"
echo ""
_STAGE_START=$(date +%s)
# Disable pipefail: version commands piped to `head` (e.g. jupyter --version)
# hit SIGPIPE and exit with code 120 (Python BrokenPipeError), which would
# abort the build under `set -e -o pipefail` despite being benign.
set +o pipefail
echo "[ACTION] Activating conda main environment for Stage 4..."
source /opt/conda/etc/profile.d/conda.sh
conda activate main
echo "  - conda env: $CONDA_DEFAULT_ENV"
echo "  - python: $(python --version 2>&1)"
echo "  - which llvm-config: $(which llvm-config 2>&1)"
echo ""

echo "[ACTION] Writing build metadata to /etc/devcontainer-variant-conda-llvm-build-info..."
LLVM_ACTUAL_VERSION=$(llvm-config --version 2>&1 | head -1)
CLANG_ACTUAL_VERSION=$(clang --version 2>&1 | head -1 | awk '{print $3}')
CMAKE_ACTUAL_VERSION=$(cmake --version 2>&1 | head -1 | awk '{print $3}')
NINJA_ACTUAL_VERSION=$(ninja --version 2>&1)
CONDA_VERSION=$(/opt/conda/bin/conda --version 2>&1 | awk '{print $2}')
PYTHON_ACTUAL_VERSION=$(python --version 2>&1 | awk '{print $2}')
JUPYTER_ACTUAL_VERSION=$(jupyter --version 2>&1 | head -1 | awk '{print $3}')

cat > /etc/devcontainer-variant-conda-llvm-build-info <<EOF_INFO
BUILD_DATE=$(date -u +%Y-%m-%dT%H:%M:%SZ)
VARIANT=conda-llvm
BASE_IMAGE=devcontainer-base:${BASE_TAG}
LLVM_VERSION_REQUESTED=${LLVM_VERSION}
LLVM_VERSION_ACTUAL=${LLVM_ACTUAL_VERSION}
CLANG_VERSION_ACTUAL=${CLANG_ACTUAL_VERSION}
CMAKE_VERSION_ACTUAL=${CMAKE_ACTUAL_VERSION}
NINJA_VERSION_ACTUAL=${NINJA_ACTUAL_VERSION}
CONDA_VERSION=${CONDA_VERSION}
PYTHON_VERSION_ACTUAL=${PYTHON_ACTUAL_VERSION}
PYTHON_BUILD=$(python -c "import sys; print('free-threading nogil active' if not sys._is_gil_enabled() else 'GIL enabled REGRESSION')" 2>&1)
JUPYTER_VERSION_ACTUAL=${JUPYTER_ACTUAL_VERSION}
PYTHON_ENV=conda-main
CONDA_DIR=/opt/conda
CONDA_ENV=main
CONDA_MIRROR=${CONDA_MIRROR}
PIP_MIRROR=${PIP_MIRROR}
APT_MIRROR=${APT_MIRROR}
INSTALL_ENV=main (default user env)
PATH_PRIORITY=conda-main-bin-first
ACTIVATION_SCRIPT=/etc/profile.d/conda-init.sh (main env)
SERVICES_PRESERVED=sshd,dockerd,podman,jupyter,supervisord
PACKAGES_INSTALLED=llvmdev,clangdev,clang,lld,cmake,ninja,make,libgcc,libstdcxx-ng
PACKAGES_EXCLUDED=lldb(no cp314t build,forces python GIL swap)
BUILD_TIMER=enabled
EOF_INFO

echo "[OK] Build metadata written:"
cat /etc/devcontainer-variant-conda-llvm-build-info
echo ""

echo "[ACTION] Running final cleanup..."
pip cache purge 2>/dev/null || true
apt-get clean 2>/dev/null || true
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*
echo "[OK] Cleanup complete (pip cache purge, apt clean, tmp)"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [VALIDATION CHECKPOINT - Stage 4/4]           │"
echo "│  Running final toolchain + service verification │"
echo "└─────────────────────────────────────────────────┘"
echo ""

echo "[VALIDATE 1/9] bash -n /etc/profile.d/conda-llvm-init.sh..."
bash -n /etc/profile.d/conda-llvm-init.sh && echo "[OK] conda-llvm-init.sh bash syntax valid"

echo "[VALIDATE 2/9] llvm-config available and version matches..."
test -x "$(which llvm-config)" && echo "[OK] llvm-config executable"
llvm-config --version

echo "[VALIDATE 3/9] clang/clang++ available..."
test -x "$(which clang)" && echo "[OK] clang executable"
clang --version | head -2
test -x "$(which clang++)" && echo "[OK] clang++ executable"

echo "[VALIDATE 4/9] cmake available..."
test -x "$(which cmake)" && echo "[OK] cmake executable"
cmake --version | head -1

echo "[VALIDATE 5/9] ninja available..."
test -x "$(which ninja)" && echo "[OK] ninja executable"
ninja --version

echo "[VALIDATE 6/9] make available..."
test -x "$(which make)" && echo "[OK] make executable"
make --version | head -1

echo "[VALIDATE 7/9] Python/Jupyter from conda main environment (default user env)..."
test -x /opt/conda/envs/main/bin/python && echo "[OK] /opt/conda/envs/main/bin/python exists"
/opt/conda/envs/main/bin/python --version
test -x /opt/conda/envs/main/bin/jupyter && echo "[OK] /opt/conda/envs/main/bin/jupyter exists"
/opt/conda/envs/main/bin/jupyter --version 2>&1 | head -2

echo "[VALIDATE 8/9] Core services (docker, supervisord) still present..."
docker --version 2>&1
supervisord --version 2>&1
echo "[OK] Core services preserved"

echo "[VALIDATE 9/9] devuser can access LLVM tools..."
su - devuser -c "source /opt/conda/etc/profile.d/conda.sh && conda activate main && llvm-config --version && clang --version | head -1" && echo "[OK] devuser can access LLVM toolchain"

echo ""
echo "[VALIDATE] All validation checks completed"
echo ""

echo "┌─────────────────────────────────────────────────┐"
echo "│  [FINAL VERIFICATION - HELLO WORLD COMPILE]     │"
echo "│  Testing clang compilation of a simple C++ file │"
echo "└─────────────────────────────────────────────────┘"
echo '#include <iostream>' > /tmp/hello.cpp
echo 'int main() { std::cout << "Hello from LLVM/Clang!\n"; return 0; }' >> /tmp/hello.cpp
clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello -stdlib=libstdc++ 2>&1 || clang++ --std=c++17 /tmp/hello.cpp -o /tmp/hello 2>&1
/tmp/hello
rm -f /tmp/hello.cpp /tmp/hello
echo "[OK] C++ compilation test passed"
echo ""

_NOW=$(date +%s)
_ELAPSED=$((_NOW - _STAGE_START))
_START=$(grep '^START=' /tmp/.llvm-variant-build-timer | cut -d= -f2)
_LLVS1=$(grep '^LLVS1=' /tmp/.llvm-variant-build-timer | cut -d= -f2)
_LLVS2=$(grep '^LLVS2=' /tmp/.llvm-variant-build-timer | cut -d= -f2)
_LLVS3=$(grep '^LLVS3=' /tmp/.llvm-variant-build-timer | cut -d= -f2)
_LVT1=$((_LLVS1 - _START))
_LVT2=$((_LLVS2 - _LLVS1))
_LVT3=$((_LLVS3 - _LLVS2))
_LVT4=$_ELAPSED
_LVTOTAL=$((_NOW - _START))

echo "[TIMER] Stage 4/4 (metadata+final verify) took ${_ELAPSED}s | LLVM variant cumulative: ${_LVTOTAL}s"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║   BUILD TIMING SUMMARY (Conda-LLVM Variant - 4 Add Stages) ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Stage 1/4  path verification + init  %5ds               ║\n" $_LVT1
printf "║  Stage 2/4  LLVM toolchain + cleanup  %5ds               ║\n" $_LVT2
printf "║  Stage 3/4  symlinks+init script      %5ds               ║\n" $_LVT3
printf "║  Stage 4/4  metadata+final verify     %5ds               ║\n" $_LVT4
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  CONDA-LLVM VARIANT TOTAL (add-on)    %5ds               ║\n" $_LVTOTAL
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

rm -f /tmp/.llvm-variant-build-timer
echo "########################################################################"
echo "# CONDA-LLVM VARIANT BUILD COMPLETE!"
echo "# LLVM/Clang ${LLVM_VERSION} + CMake + Ninja + Make installed in conda main env"
echo "# PATH priority: /opt/conda/envs/main/bin first (LLVM tools + Python 3.14t)"
echo "# Default environment: main (Python 3.14 free-threading + Jupyter)"
echo "#"
echo "# Verify with: llvm-config --version && clang --version && cmake --version"
echo "########################################################################"
echo ""
STAGE4_EOF
