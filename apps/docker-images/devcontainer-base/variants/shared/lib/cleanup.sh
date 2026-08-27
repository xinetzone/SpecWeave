#!/usr/bin/env bash
# =============================================================================
# cleanup.sh — 统一清理模块（激进清理减小镜像体积，基于 safe_cleanup 安全原语）
#
# 提供分层清理函数：pycache → conda/pip cache → apt → tmp → binaries → all
# 安全保证：基于 safe_cleanup.sh 的 T∩D=∅ 隔离原则，自动防止备份自毁类 bug
#
# 依赖：logging.sh（variant_log_* 函数）、safe_cleanup.sh（安全清理原语）
# =============================================================================

# 防止重复 source
[[ -n "${_VARIANT_CLEANUP_LOADED:-}" ]] && return 0
_VARIANT_CLEANUP_LOADED=1

# 计时器目录（必须排除，不能被清理删除）
_VARIANT_TIMER_DIR="/root/.variant-timers"

# 确保 safe_cleanup 已加载（框架已按依赖顺序加载，此处为独立source时的兜底）
if [[ -z "${_SAFE_CLEANUP_LOADED:-}" ]]; then
    _CLEANUP_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    # shellcheck source=./safe_cleanup.sh
    source "${_CLEANUP_LIB_DIR}/safe_cleanup.sh"
fi

# ---------------------------------------------------------------------------
# cleanup_pycache: 删除Python缓存文件
# ---------------------------------------------------------------------------
cleanup_pycache() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] Python __pycache__ and .pyc files    │"
    echo "└─────────────────────────────────────────────────┘"

    find /opt/conda -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find /opt/conda -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
    # 清理用户目录下的缓存
    if id -u devuser >/dev/null 2>&1; then
        find /home/devuser -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
        find /home/devuser -type f \( -name "*.pyc" -o -name "*.pyo" \) -delete 2>/dev/null || true
    fi

    variant_log_ok "Python cache removed"
}

# ---------------------------------------------------------------------------
# cleanup_conda_pip_cache: 清理conda和pip缓存
# ---------------------------------------------------------------------------
cleanup_conda_pip_cache() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] conda and pip cache                   │"
    echo "└─────────────────────────────────────────────────┘"

    conda clean -yafq 2>/dev/null || true
    pip cache purge 2>/dev/null || true

    variant_log_ok "conda + pip cache cleaned"
}

# ---------------------------------------------------------------------------
# cleanup_apt: 清理APT缓存（使用 safe_cleanup_dir 安全清理 lists 目录）
# ---------------------------------------------------------------------------
cleanup_apt() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] APT cache                             │"
    echo "└─────────────────────────────────────────────────┘"

    apt-get clean -y 2>/dev/null || true
    # 使用 safe_cleanup_dir 替代 rm -rf /var/lib/apt/lists/* —— 根目录护栏+隐藏文件自动清理
    safe_cleanup_dir /var/lib/apt/lists

    variant_log_ok "APT cache cleaned"
}

# ---------------------------------------------------------------------------
# cleanup_tmp: 安全清理临时目录
#
# 安全策略：
#   1. _VARIANT_TIMER_DIR=/root/.variant-timers 天然在 /tmp、/var/tmp 之外
#   2. 启动时断言：验证计时器目录不在清理目标内（防御未来路径变更）
#   3. 使用 safe_cleanup_dir 白名单清理，无需 mv-aside（零备份自毁风险）
# ---------------------------------------------------------------------------
cleanup_tmp() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] /tmp and /var/tmp (safe mode)         │"
    echo "│ NOTE: ${_VARIANT_TIMER_DIR} EXCLUDED (timer data)  │"
    echo "└─────────────────────────────────────────────────┘"

    # 防御性断言：计时器目录必须在 /tmp 和 /var/tmp 之外（T∩D=∅不变量）
    # 如果未来有人把 _VARIANT_TIMER_DIR 改到 /tmp 下，这里会立刻报错阻止清理
    local _assert_failed=0
    for _tmp_target in /tmp /var/tmp; do
        if safe_is_subpath "${_VARIANT_TIMER_DIR}" "${_tmp_target}"; then
            echo "[CLEANUP][ERROR] Timer dir INSIDE cleanup target! This violates T∩D=∅ invariant." >&2
            echo "[CLEANUP][ERROR]   timer: ${_VARIANT_TIMER_DIR}" >&2
            echo "[CLEANUP][ERROR]   target: ${_tmp_target}" >&2
            echo "[CLEANUP][ERROR]   Use safe_cleanup_move_aside() or move timer dir outside /tmp." >&2
            _assert_failed=1
        fi
    done

    if [[ $_assert_failed -eq 1 ]]; then
        echo "[CLEANUP][WARN] Aborting tmp cleanup due to safety violation. Timer data must be preserved." >&2
        return 1
    fi

    # 计时器目录在 /root/，天然隔离——直接安全清理 /tmp 和 /var/tmp
    # safe_cleanup_dir 自动处理隐藏文件、根目录护栏、非阻塞容错
    safe_cleanup_dir /tmp
    safe_cleanup_dir /var/tmp

    variant_log_ok "tmp directories cleaned (timer dir preserved via safe_cleanup)"
}

# ---------------------------------------------------------------------------
# cleanup_binaries: 激进二进制清理（strip bin + .so + 删除非必要静态库）
# 注意：
#   - 保留 GCC 运行时静态库（libgcc*/libstdc++*）和 sysroot 系统静态库（libc/libm等）
#   - 同时 strip bin/ 和 lib/*.so*（共享库 strip 可省 ~50-100MB）
#   - 使用 -x 限制在同一文件系统，避免进入 /proc /sys 等
# ---------------------------------------------------------------------------
cleanup_binaries() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] Binary strip + static libs removal   │"
    echo "│ NOTE: libgcc*/libstdc++*/sysroot *.a PRESERVED  │"
    echo "└─────────────────────────────────────────────────┘"

    # Strip 可执行文件（bin/ 目录）
    echo "[ACTION] Stripping ELF binaries in bin dirs..."
    find /opt/conda/envs/main/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
    find /opt/conda/bin -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
    echo "[OK] Binary stripping complete"
    echo ""

    # Strip 共享库（.so 文件）—— 这是原来缺失的，约省 50-100MB
    echo "[ACTION] Stripping shared libraries (.so*)..."
    local _so_before _so_after
    _so_before=$(du -sb /opt/conda/envs/main/lib 2>/dev/null | awk '{print $1}')
    find /opt/conda/envs/main/lib -maxdepth 1 -name "*.so*" -type f -exec strip --strip-unneeded {} \; 2>/dev/null || true
    find /opt/conda/envs/main/lib -name "*.so*" -type f -exec strip --strip-unneeded {} \; 2>/dev/null || true
    _so_after=$(du -sb /opt/conda/envs/main/lib 2>/dev/null | awk '{print $1}')
    echo "[OK] Shared libraries stripped (saved ~$(( (_so_before - _so_after) / 1024 / 1024 ))MB)"
    echo ""

    # 删除静态库，但保留编译器/链接器必需的：
    #   - GCC 运行时（libgcc*, libstdc++*）在 lib/gcc/ 下
    #   - sysroot 系统库（libc.a, libm.a, libmvec.a 等）在 x86_64-conda-linux-gnu/sysroot/ 下
    #   - numpy C 扩展头文件库（libnpymath.a, libnpyrandom.a）用于构建 Python C 扩展
    echo "[ACTION] Removing non-essential static libraries (.a)..."
    find /opt/conda/envs/main -name "*.a" -type f \
        ! -path "*/gcc/*" \
        ! -path "*/sysroot/*" \
        ! -name "libnpymath.a" \
        ! -name "libnpyrandom.a" \
        -delete 2>/dev/null || true
    echo "[OK] Non-essential static libraries removed"
}

# ---------------------------------------------------------------------------
# cleanup_llvm_devtools: 移除非必需的 LLVM/Clang 开发工具
#
# 保留核心工具：clang, clang++, clang-format, clang-tidy, clangd,
#   clang-include-cleaner (clangd依赖), clang-offload-bundler (OpenMP offload),
#   lld/ld.lld, llvm-config, llvm-ar, llvm-nm, llvm-objdump, llvm-objcopy,
#   llvm-readelf, llvm-readobj, llvm-size, llvm-strings, llvm-strip,
#   llvm-symbolizer, llvm-cov, llvm-profdata, llvm-dwarfdump, llvm-ranlib,
#   llvm-cxxfilt, llvm-addr2line, pandoc (nbconvert依赖), cpack (CMake打包)
# 移除非核心：llvm-exegesis, ccmake, 跨平台链接器, tblgen,
#   重构工具, Windows/macOS 交叉工具
# ---------------------------------------------------------------------------
cleanup_llvm_devtools() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] LLVM/Clang dev tools (non-essential) │"
    echo "│ NOTE: clang/clang++/lld/cmake/ninja/ccache KEPT │"
    echo "│ KEPT: pandoc, clang-tidy, clangd, cpack, headers│"
    echo "└─────────────────────────────────────────────────┘"

    local _conda_bin="/opt/conda/envs/main/bin"
    local _saved=0
    local _sz

    # Helper: delete and track size (handles dangling symlinks)
    _del() {
        local f="$_conda_bin/$1"
        if [ -e "$f" ] || [ -L "$f" ]; then
            _sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
            rm -f "$f"
            _saved=$((_saved + _sz))
        fi
    }

    # === 大体积优先 ===
    # pandoc KEPT: Jupyter nbconvert export to PDF/DOCX depends on it
    _del "llvm-exegesis-22"                                                            # 71M - CPU benchmarking (compiler dev only)
    _del "ccmake"                                                                      # ~16M - CMake curses TUI (useless in containers)
    # cpack KEPT: CI/CD packaging (DEB/RPM/NSIS generation)
    _del "wasm-ld";           _del "ld64.lld";       _del "lld-link"               # 21M - cross-platform linkers (specialized targets)
    _del "llvm-tblgen-22";    _del "clang-tblgen-22"                                    # ~6M - .td code generators (LLVM dev only)
    _del "llvm-pdbutil-22"                                                             # ~1M - Windows PDB tool

    # === Clang 重构/代码转换工具（专业场景，通用开发不需要）===
    # clang-include-cleaner KEPT: clangd uses it for include diagnostics
    # clang-offload-bundler KEPT: OpenMP target offloading uses it
    for _tool in clang-doc clang-doc-22 clang-include-fixer clang-include-fixer-22 \
                 clang-pseudo clang-pseudo-22 clang-rename clang-rename-22 \
                 clang-refactor clang-refactor-22 clang-apply-replacements \
                 clang-apply-replacements-22 clang-change-namespace clang-change-namespace-22 \
                 clang-move clang-move-22 clang-reorder-fields clang-reorder-fields-22 \
                 clang-query clang-query-22 clang-extdef-mapping clang-extdef-mapping-22 \
                 clang-installapi clang-installapi-22 \
                 clang-repl clang-repl-22 diagtool; do
        _del "$_tool"
    done

    # === Windows/macOS 交叉编译工具 ===
    for _tool in llvm-cvtres-22 llvm-rc-22 llvm-windres-22 llvm-dlltool-22 \
                 llvm-lib-22 llvm-mt-22 llvm-otool-22 llvm-bitcode-strip-22 \
                 llvm-lipo-22 llvm-libtool-darwin-22 llvm-ifs-22; do
        _del "$_tool"
    done

    # === LLVM 高级分析/调试工具（非常用）===
    for _tool in llvm-mca-22 llvm-xray-22 llvm-reduce-22 llvm-jitlink-22 \
                 llvm-dwarfutil-22 llvm-remarkutil-22 llvm-profgen-22 \
                 llvm-sim-22 llvm-cgdata-22 llvm-tli-checker-22; do
        _del "$_tool"
    done

    # === 清理无版本号的别名（如有）===
    for _tool in llvm-exegesis llvm-pdbutil llvm-cvtres llvm-rc llvm-windres \
                 llvm-dlltool llvm-lib llvm-mt llvm-otool llvm-bitcode-strip \
                 llvm-lipo llvm-libtool-darwin llvm-ifs llvm-mca llvm-xray \
                 llvm-reduce llvm-jitlink llvm-dwarfutil llvm-remarkutil \
                 llvm-profgen llvm-sim llvm-cgdata llvm-tli-checker \
                 clang-doc clang-include-fixer clang-pseudo clang-rename \
                 clang-refactor clang-apply-replacements clang-change-namespace \
                 clang-move clang-reorder-fields clang-query clang-extdef-mapping \
                 clang-installapi clang-repl; do
        _del "$_tool"
    done

    # === 删除 libexec/llvm（LLVM 内部构建工具，21M）===
    if [ -d "/opt/conda/envs/main/libexec/llvm" ]; then
        _sz=$(du -sb "/opt/conda/envs/main/libexec/llvm" 2>/dev/null | awk '{print $1}')
        rm -rf "/opt/conda/envs/main/libexec/llvm"
        _saved=$((_saved + _sz))
    fi

    echo "[OK] Non-essential dev tools removed (~$((_saved / 1024 / 1024))MB saved)"
}

# ---------------------------------------------------------------------------
# cleanup_dev_headers: LLVM/Clang 开发头文件保留
# 保留原因：
#   - LLVM/Clang headers: TVM、MLIR、LLVM Pass 开发编译链接时必需
#   - clang-tidy headers: clang-tidy 插件开发需要
#   - cmake/llvm,cmake/clang,cmake/lld: find_package(LLVM) 等 CMake 集成需要
# C/C++ 标准库头文件在 lib/gcc/.../include 和 sysroot 中，不受影响。
# ---------------------------------------------------------------------------
cleanup_dev_headers() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [INFO] LLVM/Clang development headers KEPT      │"
    echo "│ Reason: TVM/MLIR/LLVM Pass dev need these       │"
    echo "│ stdlib headers in gcc/sysroot are unaffected    │"
    echo "└─────────────────────────────────────────────────┘"
    # KEPT: /opt/conda/envs/main/include/llvm{-c}
    # KEPT: /opt/conda/envs/main/include/clang{-c,-tidy}
    # KEPT: /opt/conda/envs/main/lib/cmake/{llvm,clang,lld}
}

# ---------------------------------------------------------------------------
# cleanup_torch_dev: PyTorch/CUDA 专属激进清理（torch-dev 变体专用）
#
# 清理项（R1: 第一轮 180MB + R2: 第二轮 ~160MB）：
#   R1:
#   1. nvidia/cu13 中的 libnvrtc.alt*（109MB）— CUDA 备用NVRTC，ldd确认无引用
#   2. nvidia/cu13 中的 libnvperf_*（36MB）— Nsight性能分析库，非运行时必需
#   3. nvidia/nvshmem 中的设备端bitcode和静态库（33MB）— 编译时用，运行时不需要
#   4. triton/backends/amd（2.7MB）— AMD GPU后端，N卡镜像不需要
#   R2 (第二轮，基于DT_NEEDED硬依赖分析):
#   5. libcusolverMg.so.12（100MB）— 多GPU分布式求解器，非DT_NEEDED，dlopen延迟加载
#   6. libcudnn_engines_runtime_compiled.so.9（29MB）— JIT引擎，precompiled已覆盖标准场景
#   7. NVSHMEM IB/MPI bootstrap/transport插件（~4MB）— InfiniBand/HPC专用，WSL2不用
#   8. 小型CUDA工具库（nvblas/checkpoint/pcsamplingutil ~3MB）
#   9. torch/bin/protoc*（10MB）— protobuf编译器，构建时工具
#  10. torchgen/（2.4MB）— PyTorch代码生成器，源码构建时用
#  11. strip triton CUDA工具链（ptxas/nvdisasm等，预计10-20MB）
#
# 保留的硬依赖（DT_NEEDED，删除将导致import torch失败）：
#   libcusparseLt.so.0（224MB）— libtorch_cuda.so 硬链接
#   libnccl.so.2（186MB）— libtorch_cuda.so 硬链接
#   libnvshmem_host.so.3（38MB）— libtorch_nvshmem.so → libtorch_cuda.so 硬依赖
#   libcublasLt/libcublas/libcufft/libcusparse/libcusolver/libcurand/libnvJitLink/libcudnn等 — 核心CUDA库
#
# 注意：必须在 pip install torch 同一层调用，否则 CoW 会导致旧文件残留。
# ---------------------------------------------------------------------------
cleanup_torch_dev() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] PyTorch/CUDA specific slimming (R1+R2) │"
    echo "│ R1: nvrtc.alt + nvperf + nvshmem-bitcode + amd   │"
    echo "│ R2: cusolverMg + cudnn-jit + nvshmem-plugins     │"
    echo "│     + build-tools + triton-bin-strip             │"
    echo "└─────────────────────────────────────────────────┘"

    local _saved=0
    local _sz
    local _sp="/opt/conda/envs/main/lib/python3.14t/site-packages"

    _del_torch() {
        local f="$_sp/$1"
        if [ -e "$f" ] || [ -L "$f" ]; then
            _sz=$(stat -c%s "$f" 2>/dev/null || echo 0)
            rm -f "$f" 2>/dev/null || true
            _saved=$((_saved + _sz))
            echo "  [DEL] $1 ($(( _sz / 1024 / 1024 ))MB)"
        fi
    }

    _del_dir_torch() {
        local d="$_sp/$1"
        if [ -d "$d" ]; then
            _sz=$(du -sb "$d" 2>/dev/null | awk '{print $1}')
            rm -rf "$d" 2>/dev/null || true
            _saved=$((_saved + _sz))
            echo "  [DEL-DIR] $1/ ($(( _sz / 1024 / 1024 ))MB)"
        fi
    }

    # ═══ R1: 冗余/可选 CUDA 库 ═══
    # libnvrtc.alt*: NVIDIA 备用NVRTC构建（用于非标准环境），torch/triton均不引用
    _del_torch "nvidia/cu13/lib/libnvrtc.alt.so.13"
    _del_torch "nvidia/cu13/lib/libnvrtc-builtins.alt.so.13.0"

    # libnvperf_*: Nsight Compute 性能分析库，torch运行时不链接
    _del_torch "nvidia/cu13/lib/libnvperf_host.so"
    _del_torch "nvidia/cu13/lib/libnvperf_target.so"

    # NVSHMEM 设备端编译产物（运行时不需要）
    _del_torch "nvidia/nvshmem/lib/libnvshmem_device.bc"
    _del_torch "nvidia/nvshmem/lib/libnvshmem_device.a"

    # Triton AMD 后端（N卡镜像不需要）
    _del_dir_torch "triton/backends/amd"

    # ═══ R2: DT_NEEDED验证后可安全删除的项 ═══
    # libcusolverMg.so.12: 多GPU分布式线性代数求解器（100MB）
    # readelf验证：无任何torch .so对其DT_NEEDED，仅多卡collective时dlopen
    _del_torch "nvidia/cu13/lib/libcusolverMg.so.12"

    # libcudnn_engines_runtime_compiled.so.9: cuDNN JIT编译引擎（29MB）
    # precompiled引擎(235MB)覆盖标准shape; JIT路径为非典型config fallback
    _del_torch "nvidia/cudnn/lib/libcudnn_engines_runtime_compiled.so.9"

    # NVSHMEM bootstrap plugins — HPC集群专用，WSL2/消费级GPU无InfiniBand/MPI
    _del_torch "nvidia/nvshmem/lib/nvshmem_bootstrap_mpi.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_bootstrap_pmi.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_bootstrap_pmi2.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_bootstrap_pmix.so.3"
    # NVSHMEM transport plugins — InfiniBand transports (ibdevx/ibgda/ibrc/libfabric)
    _del_torch "nvidia/nvshmem/lib/nvshmem_transport_ibdevx.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_transport_ibgda.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_transport_ibrc.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_transport_libfabric.so.3"
    _del_torch "nvidia/nvshmem/lib/nvshmem_transport_ucx.so.3"
    # 保留: nvshmem_bootstrap_shmem.so(14KB) + nvshmem_bootstrap_uid.so(60KB) — 本地共享内存必需

    # 小型CUDA工具库（非运行时必需）
    _del_torch "nvidia/cu13/lib/libnvblas.so.13"        # NVBLAS: drop-in BLAS, 737KB
    _del_torch "nvidia/cu13/lib/libcheckpoint.so"       # checkpoint utility, 1.4MB
    _del_torch "nvidia/cu13/lib/libpcsamplingutil.so"   # PC sampling profiler, 703KB

    # ═══ 构建时工具（运行时不需要）═══
    # protoc: protobuf编译器（10MB），torch自带，运行时ONNX导出使用Python protobuf库
    _del_torch "torch/bin/protoc"
    _del_torch "torch/bin/protoc-3.13.0.0"

    # torchgen/ (2.4MB) — 保留！torch.utils._python_dispatch 运行时 import torchgen，删除导致 ModuleNotFoundError

    # ═══ Strip Triton CUDA工具链二进制（cleanup_binaries未覆盖site-packages/bin）═══
    echo "[ACTION] Stripping Triton CUDA toolchain binaries..."
    local _tb_before _tb_after
    _tb_before=$(du -sb "$_sp/triton/backends/nvidia/bin" 2>/dev/null | awk '{print $1}')
    find "$_sp/triton/backends/nvidia/bin" -type f -executable -exec strip --strip-unneeded {} \; 2>/dev/null || true
    _tb_after=$(du -sb "$_sp/triton/backends/nvidia/bin" 2>/dev/null | awk '{print $1}')
    local _tb_saved=$(( (_tb_before - _tb_after) / 1024 / 1024 ))
    if [ "$_tb_saved" -gt 0 ]; then
        _saved=$((_saved + _tb_before - _tb_after))
        echo "  [STRIP] triton/backends/nvidia/bin/ (saved ~${_tb_saved}MB)"
    fi

    echo "[OK] PyTorch/CUDA cleanup complete (saved ~$((_saved / 1024 / 1024))MB)"
}

# ---------------------------------------------------------------------------
# cleanup_post_tests: smoke tests 后的清理
# smoke tests 会导入模块（产生 __pycache__）和创建临时文件，需要清理。
# 必须在所有验证/测试命令之后、层结束之前调用。
# ---------------------------------------------------------------------------
cleanup_post_tests() {
    echo ""
    echo "┌─────────────────────────────────────────────────┐"
    echo "│ [CLEANUP] Post-verification cleanup (pycache)  │"
    echo "└─────────────────────────────────────────────────┘"
    cleanup_pycache
    # Clean test artifacts in tmp
    rm -rf /tmp/hello* /tmp/test_* /tmp/mlp* /tmp/tiny* /tmp/cmake_test /tmp/*.onnx 2>/dev/null || true
    variant_log_ok "Post-test cleanup complete"
}

# ---------------------------------------------------------------------------
# cleanup_all: 一键执行标准清理（pycache + conda/pip + apt + tmp，不含binaries）
# ---------------------------------------------------------------------------
cleanup_all() {
    variant_stage_header "Post-Install Cleanup"
    cleanup_pycache
    cleanup_conda_pip_cache
    cleanup_apt
    cleanup_tmp
    variant_log_ok "All standard cleanup completed"
}

# ---------------------------------------------------------------------------
# cleanup_all_aggressive: 激进清理（所有标准清理 + binaries strip + llvm dev tools + dev headers）
# ---------------------------------------------------------------------------
cleanup_all_aggressive() {
    variant_stage_header "Aggressive Post-Install Cleanup"
    cleanup_pycache
    cleanup_binaries
    cleanup_llvm_devtools
    cleanup_dev_headers
    cleanup_conda_pip_cache
    cleanup_apt
    cleanup_tmp
    variant_log_ok "All aggressive cleanup completed"
}
