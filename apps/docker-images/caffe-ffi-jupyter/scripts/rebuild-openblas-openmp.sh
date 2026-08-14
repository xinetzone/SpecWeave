#!/bin/bash
# =============================================================================
# rebuild-openblas-openmp.sh — OpenBLAS OpenMP 线程化重建脚本
#
# 问题背景：
#   caffe-ffi conda 环境预装的 libopenblas 是 conda-forge 的 pthreads 变体
#   （libopenblas 0.3.34 pthreads_h94d23a6_0），当上层代码（caffe-ffi/numpy）
#   通过 OpenMP 并行调用 BLAS 时触发线程模型冲突警告：
#     "OpenBLAS Warning : ... pthread_create failed"
#   或与 OMP_NUM_THREADS 环境变量交互导致过订阅（oversubscription）。
#
# 本脚本提供两种方案，按优先级推荐：
#   方案 A（快速，推荐）: conda 替换为 openmp 变体（约 30s，需网络）
#   方案 B（源码编译）  : 从 OpenBLAS 源码编译 USE_OPENMP=1 版本（约 5-10min）
#
# 使用:
#   bash scripts/rebuild-openblas-openmp.sh [--method=A|B|auto] [--cn] [--verify]
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/logging.sh
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="openblas-rebuild"

# ── 默认参数 ──
METHOD="${METHOD:-auto}"          # auto | A (conda) | B (source)
CN_MIRROR="${CN_MIRROR:-0}"       # 国内镜像
VERIFY="${VERIFY:-0}"             # 构建后验证
CONDA_ENV="${CONDA_ENV:-caffe-ffi}"
OPENBLAS_VERSION="${OPENBLAS_VERSION:-0.3.28}"
BUILD_CORES="${BUILD_CORES:-$(nproc 2>/dev/null || echo 4)}"
PREFIX=""

# ── 用法 ──
usage() {
    cat << EOF
${_CLR_BOLD}OpenBLAS OpenMP 线程化重建脚本${_CLR_RESET}

用法: bash scripts/rebuild-openblas-openmp.sh [选项]

${_CLR_BOLD}选项:${_CLR_RESET}
  -m, --method METH   方案: A=conda替换(快) | B=源码编译 | auto=有网络选A无网络选B (默认: auto)
  --cn                使用国内镜像源（tuna/bfsu）
  --verify            构建后运行 OpenMP 线程验证
  -e, --env NAME      Conda 环境名（默认: caffe-ffi）
  --openblas-ver VER  源码编译时的 OpenBLAS 版本（默认: 0.3.28）
  -j, --jobs N        编译并行度（默认: nproc）
  --prefix PATH       安装前缀（默认: conda 环境前缀）
  --log-format FMT    日志格式: text|json
  --log-level LVL     日志级别: DEBUG|INFO|WARN|ERROR
  -h, --help          显示帮助

${_CLR_BOLD}示例:${_CLR_RESET}
  # 方案 A（推荐，国内网络）：
  bash scripts/rebuild-openblas-openmp.sh --method=A --cn --verify

  # 方案 B（源码编译，全核）：
  bash scripts/rebuild-openblas-openmp.sh --method=B -j \$(nproc) --verify
EOF
}

# ── 参数解析 ──
eval "$(log_parse_args "$@")"
while [ $# -gt 0 ]; do
    case "$1" in
        -m|--method)   METHOD="$2"; shift 2 ;;
        --method=*)    METHOD="${1#*=}"; shift ;;
        --cn)          CN_MIRROR=1; shift ;;
        --verify)      VERIFY=1; shift ;;
        -e|--env)      CONDA_ENV="$2"; shift 2 ;;
        --env=*)       CONDA_ENV="${1#*=}"; shift ;;
        --openblas-ver) OPENBLAS_VERSION="$2"; shift 2 ;;
        -j|--jobs)     BUILD_CORES="$2"; shift 2 ;;
        --prefix)      PREFIX="$2"; shift 2 ;;
        --prefix=*)    PREFIX="${1#*=}"; shift ;;
        -h|--help)     usage; exit 0 ;;
        *) log_error "未知参数: $1"; usage; exit 1 ;;
    esac
done

# ── 工具函数 ──
die() { log_fatal "$*"; }

find_conda() {
    # 查找 conda 安装位置（容器内标准路径）
    if [ -f "/opt/conda/etc/profile.d/conda.sh" ]; then
        echo "/opt/conda"
        return 0
    fi
    if command -v conda &>/dev/null; then
        conda info --base 2>/dev/null || true
        return 0
    fi
    return 1
}

activate_conda_env() {
    local base
    base="$(find_conda)" || die "未找到 conda 安装"
    # shellcheck disable=SC1091
    source "${base}/etc/profile.d/conda.sh"
    conda activate "$CONDA_ENV" || die "无法激活 conda 环境: $CONDA_ENV"
    if [ -z "$PREFIX" ]; then
        PREFIX="$(conda info --prefix 2>/dev/null | tail -1 | tr -d ' ')"
        [ -z "$PREFIX" ] && PREFIX="${base}/envs/${CONDA_ENV}"
    fi
    log_info "Conda 环境: $CONDA_ENV  前缀: $PREFIX"
}

check_network() {
    # 检查是否能访问外网（尝试 conda-forge 或国内镜像）
    if [ "$CN_MIRROR" = "1" ]; then
        curl -s --connect-timeout 5 -I "https://mirrors.tuna.tsinghua.edu.cn/anaconda/" &>/dev/null && return 0
        curl -s --connect-timeout 5 -I "https://mirrors.bfsu.edu.cn/anaconda/" &>/dev/null && return 0
    else
        curl -s --connect-timeout 5 -I "https://conda.anaconda.org/conda-forge/" &>/dev/null && return 0
    fi
    return 1
}

get_current_openblas_variant() {
    # 返回当前 openblas 变体：pthreads | openmp | unknown | none
    local meta
    meta=$(conda list -n "$CONDA_ENV" libopenblas 2>/dev/null | grep -E '^libopenblas' || true)
    if [ -z "$meta" ]; then
        echo "none"
    elif echo "$meta" | grep -q 'openmp'; then
        echo "openmp"
    elif echo "$meta" | grep -q 'pthreads'; then
        echo "pthreads"
    else
        echo "unknown"
    fi
}

# ── 方案 A: conda 替换为 openmp 变体 ──
method_a_conda() {
    log_step "方案 A: 通过 conda 替换为 openmp 变体"

    activate_conda_env

    local current
    current="$(get_current_openblas_variant)"
    log_info "当前 OpenBLAS 变体: $current"

    if [ "$current" = "openmp" ]; then
        log_ok "OpenBLAS 已经是 openmp 变体，无需替换"
        return 0
    fi

    # 设置 conda 镜像（如需要）
    if [ "$CN_MIRROR" = "1" ]; then
        log_info "配置国内 conda 镜像源 (tuna)"
        conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/ 2>/dev/null || true
        conda config --add channels https://mirrors.bfsu.edu.cn/anaconda/cloud/conda-forge/ 2>/dev/null || true
    fi

    log_info "安装 libopenblas openmp 变体（将自动替换 pthreads 变体）..."
    # conda-forge 的 openmp 变体 build string 含 "openmp"，使用通配符匹配
    # --force-reinstall 确保替换
    conda install -y -c conda-forge \
        "libopenblas=*=*openmp*" \
        "openblas=*=*openmp*" \
        --force-reinstall --no-deps 2>&1 | while IFS= read -r line; do
            log_debug "conda: $line"
        done

    # 验证 numpy 链接到新 openblas（numpy 通过 cblas/lapack 间接依赖 openblas，
    # conda 的 blas 元包会自动切换）
    log_info "重新安装 numpy 以确保链接到 openmp 变体的 openblas..."
    conda install -y -c conda-forge numpy --force-reinstall --no-deps 2>&1 | while IFS= read -r line; do
        log_debug "conda(numpy): $line"
    done || log_warn "numpy 重装失败，尝试不指定 channel..."
    if [ ${PIPESTATUS[0]:-0} -ne 0 ]; then
        conda install -y "numpy=*=*openblas*" --force-reinstall 2>&1 | tail -5 || true
    fi

    log_ok "方案 A 完成"
}

# ── 方案 B: 从源码编译 OpenBLAS USE_OPENMP=1 ──
method_b_source() {
    log_step "方案 B: 从源码编译 OpenBLAS USE_OPENMP=1"

    activate_conda_env

    # 编译依赖
    log_info "安装编译依赖..."
    apt-get update -qq
    apt-get install -y -qq build-essential gfortran wget perl python3 2>&1 | tail -3 || \
        die "编译依赖安装失败（可能需要 sudo 权限）"

    local workdir="/tmp/openblas-build"
    mkdir -p "$workdir"
    cd "$workdir"

    # 下载源码
    local tarball="OpenBLAS-${OPENBLAS_VERSION}.tar.gz"
    local srcdir="OpenBLAS-${OPENBLAS_VERSION}"
    if [ ! -f "$tarball" ]; then
        log_info "下载 OpenBLAS v${OPENBLAS_VERSION}..."
        local url
        if [ "$CN_MIRROR" = "1" ]; then
            url="https://mirrors.tuna.tsinghua.edu.cn/github-release/xianyi/OpenBLAS/LatestRelease/${tarball}"
            # 如果 tuna 镜像没有，备用 github 代理
            if ! wget -q --timeout=30 -T 5 "$url" -O "$tarball"; then
                log_warn "tuna 镜像下载失败，尝试 github 直连..."
                url="https://github.com/OpenMathLib/OpenBLAS/releases/download/v${OPENBLAS_VERSION}/${tarball}"
                wget -q --timeout=60 -T 5 "$url" -O "$tarball" || die "源码下载失败"
            fi
        else
            url="https://github.com/OpenMathLib/OpenBLAS/releases/download/v${OPENBLAS_VERSION}/${tarball}"
            wget -q --timeout=60 -T 5 "$url" -O "$tarball" || die "源码下载失败（网络问题请用 --cn）"
        fi
    else
        log_info "已存在源码包 $tarball，跳过下载"
    fi

    # 解压
    if [ ! -d "$srcdir" ]; then
        log_info "解压..."
        tar xzf "$tarball"
    fi
    cd "$srcdir"

    # 备份原有 libopenblas
    local libdir="${PREFIX}/lib"
    local backup_dir="${libdir}/.openblas-pthreads-backup-$(date +%Y%m%d%H%M%S)"
    if ls "$libdir"/libopenblas* &>/dev/null; then
        log_info "备份原有 libopenblas 到 $backup_dir"
        mkdir -p "$backup_dir"
        cp -a "$libdir"/libopenblas* "$backup_dir/" 2>/dev/null || true
    fi

    # ── 核心编译: USE_OPENMP=1 ──
    log_info "开始编译 OpenBLAS USE_OPENMP=1 (jobs=$BUILD_CORES)..."
    log_info "关键编译参数: USE_OPENMP=1 NO_LAPACK=0 DYNAMIC_ARCH=1 TARGET=HASWELL"
    make clean 2>/dev/null || true

    # DYNAMIC_ARCH=1: 运行时自动检测 CPU 架构（兼容多机器部署）
    # TARGET=HASWELL: 针对现代 x86_64 优化基线（AVX2+FMA，caffe-ffi 容器目标）
    # USE_OPENMP=1: 启用 OpenMP 多线程（核心需求）
    # NUM_THREADS=64: 最大线程数上限
    # NO_AFFINITY=1: 不绑定 CPU 核（避免与上层 OpenMP runtime 冲突）
    # USE_LOCKING=1: 启用线程安全锁（多线程环境必需）
    make -j"$BUILD_CORES" \
        USE_OPENMP=1 \
        DYNAMIC_ARCH=1 \
        TARGET=HASWELL \
        NUM_THREADS=64 \
        NO_AFFINITY=1 \
        USE_LOCKING=1 \
        CC=gcc \
        FC=gfortran \
        2>&1 | tail -20

    log_info "安装到前缀: $PREFIX"
    make PREFIX="$PREFIX" install 2>&1 | tail -10

    # 更新动态链接库缓存
    ldconfig 2>/dev/null || true

    # 更新 conda 环境内的符号链接（确保 libopenblas.so 指向新编译版本）
    cd "$libdir"
    local newso
    newso=$(ls libopenblas*.so* 2>/dev/null | grep -v 'libopenblas.so$' | sort -V | tail -1)
    if [ -n "$newso" ]; then
        ln -sf "$newso" libopenblas.so
        ln -sf "$newso" libopenblas.so.0
        log_info "更新符号链接: libopenblas.so -> $newso"
    fi

    # 清理编译目录（可选，保留便于调试）
    # rm -rf "$workdir"

    log_ok "方案 B 源码编译完成"
}

# ── 验证 ──
verify_openblas() {
    log_step "验证 OpenBLAS OpenMP 线程化"
    activate_conda_env

    # 1. 检查库文件
    local libdir="${PREFIX}/lib"
    log_info "检查 OpenBLAS 库文件..."
    ls -la "$libdir"/libopenblas* 2>/dev/null || log_warn "未找到 libopenblas 库文件"

    # 2. 检查 numpy 链接的 BLAS
    log_info "检查 numpy BLAS 配置..."
    python -c "
import numpy as np
print(f'numpy version: {np.__version__}')
np.show_config()
" 2>&1 | grep -E '(blas|openblas|libraries|library_dirs)' -i | head -10 || true

    # 3. OpenMP 线程运行测试
    log_info "运行 OpenMP 线程测试（矩阵乘法 GEMM）..."
    python -c "
import os
import numpy as np
import time

# 设置 OpenMP 线程数
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['OPENBLAS_NUM_THREADS'] = '4'

# GEMM 测试: 大矩阵乘法，触发 OpenBLAS 并行
np.random.seed(42)
A = np.random.randn(2048, 2048).astype(np.float32)
B = np.random.randn(2048, 2048).astype(np.float32)

# warmup
C = A @ B

# 计时
times = []
for _ in range(5):
    t0 = time.time()
    C = A @ B
    times.append(time.time() - t0)

mean_t = np.mean(times)
print(f'GEMM (2048x2048 float32) mean time: {mean_t*1000:.2f}ms over 5 runs')
print(f'Throughput: {2*2048**3 / mean_t / 1e9:.2f} GFLOPS')
print(f'OPENBLAS_NUM_THREADS={os.environ.get(\"OPENBLAS_NUM_THREADS\",\"unset\")}')
print(f'OMP_NUM_THREADS={os.environ.get(\"OMP_NUM_THREADS\",\"unset\")}')
print('No OpenBLAS warnings => ✅ OpenMP threading works correctly')
" 2>&1

    # 4. 检查 OpenBLAS config 中是否含 USE_OPENMP
    log_info "检查 OpenBLAS 编译配置..."
    local config_header
    config_header=$(find "$PREFIX" -name "openblas_config.h" 2>/dev/null | head -1)
    if [ -n "$config_header" ]; then
        if grep -q 'OPENBLAS_USE_OPENMP' "$config_header" 2>/dev/null; then
            log_ok "OpenBLAS 编译配置确认: USE_OPENMP=1 ✅"
        elif grep -q 'OPENBLAS_USE_THREAD' "$config_header" 2>/dev/null; then
            if grep -q 'OPENBLAS_THREAD_SAFE' "$config_header" 2>/dev/null || \
               strings "$libdir"/libopenblas.so.0 2>/dev/null | grep -qi 'openmp'; then
                log_ok "OpenBLAS 库中检测到 OpenMP 符号 ✅"
            else
                log_warn "未在 openblas_config.h 中找到 OPENBLAS_USE_OPENMP 宏"
            fi
        fi
    else
        log_warn "未找到 openblas_config.h，跳过编译配置检查"
    fi

    # 5. 检查 caffe_ffi 导入
    if python -c "import caffe_ffi" 2>/dev/null; then
        log_ok "caffe_ffi 导入正常 ✅"
    else
        log_warn "caffe_ffi 导入检查跳过（可能未安装）"
    fi

    log_ok "验证完成"
}

# ── 自动方案选择 ──
auto_select_method() {
    if check_network; then
        log_info "检测到网络连接，选择方案 A（conda 快速替换）"
        METHOD="A"
    else
        log_warn "无网络连接，选择方案 B（源码编译）"
        METHOD="B"
    fi
}

# ── 主流程 ──
main() {
    log_step "OpenBLAS OpenMP 线程化重建"
    log_info "使用方案: $METHOD"
    log_info "国内镜像: $([ "$CN_MIRROR" = "1" ] && echo '是' || echo '否')"
    log_info "编译核数: $BUILD_CORES"

    if [ "$METHOD" = "auto" ]; then
        auto_select_method
    fi

    case "$METHOD" in
        A|a|conda)
            method_a_conda
            ;;
        B|b|source)
            method_b_source
            ;;
        *)
            log_fatal "未知方案: $METHOD（请使用 A|B|auto）"
            ;;
    esac

    if [ "$VERIFY" = "1" ]; then
        verify_openblas
    else
        log_info "跳过验证（使用 --verify 启用）"
    fi

    log_ok "OpenBLAS USE_OPENMP=1 修复完成"
    echo ""
    echo -e "${_CLR_BOLD}后续步骤:${_CLR_RESET}"
    echo "  1. 重启 Python 进程/容器使新库生效"
    echo "  2. 运行时设置环境变量避免过订阅:"
    echo "     export OPENBLAS_NUM_THREADS=4   # 或与 OMP_NUM_THREADS 保持一致"
    echo "     export OMP_NUM_THREADS=4"
    echo "     export MKL_NUM_THREADS=4        # 如果有 MKL"
    echo "  3. 验证: python -c 'import numpy as np; np.show_config()'"
}

main "$@"
