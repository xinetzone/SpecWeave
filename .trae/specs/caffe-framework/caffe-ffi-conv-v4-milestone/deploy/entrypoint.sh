#!/bin/bash
# =============================================================================
# caffe-ffi 生产部署入口脚本
#
# 功能：
#   1. 依据 DEPLOY_PROFILE 设置 OpenMP 双层并行隔离配置（见技术总结 §6 三 Profile）
#   2. 环境变量自检：打印关键变量实际值，非最优配置输出 WARNING（技术总结 §3.3）
#   3. 支持两种执行模式：
#      - 默认：exec 用户传入的命令（推理服务 / bash / 其他）
#      - --healthcheck：容器健康检查（验证 caffe_ffi 可导入 + 配置正确）
#
# 用法：
#   docker run ... caffe-ffi-prod:latest                              # 进入 bash
#   docker run ... -e DEPLOY_PROFILE=latency caffe-ffi-prod:latest \
#       python /app/serve.py --model /app/models/model.caffemodel     # 启动推理服务
#
# 环境变量契约（技术总结 §3，禁止在 Python 内 os.environ 覆盖）：
#   OPENBLAS_NUM_THREADS 必须 =1（小 GEMM 场景 3-11x 退化）
#   不设置 OMP_PROC_BIND（混合 P/E 核让 OS 调度）
# =============================================================================
set -euo pipefail

# ── 激活 conda 环境 ──
source /opt/conda/etc/profile.d/conda.sh 2>/dev/null || true
conda activate caffe-ffi 2>/dev/null || true

PYTHON="${CONDA_PREFIX:+$CONDA_PREFIX/bin/}python"
[ -x "$PYTHON" ] || PYTHON=$(command -v python)

# =============================================================================
# 1. Profile 配置（技术总结 §6 生产部署 Profile 表）
#    A latency     延迟敏感：OMP=4, BLAS=1, PASSIVE, static
#    B throughput  吞吐优先：OMP=8, BLAS=1, ACTIVE,  static
#    C general     通用均衡：OMP=4, BLAS=1, PASSIVE
# 用户可通过环境变量显式覆盖（-e OMP_NUM_THREADS=2 优先于 Profile 默认值）
# =============================================================================
PROFILE="${DEPLOY_PROFILE:-general}"
case "$PROFILE" in
    latency)
        export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
        export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
        export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-PASSIVE}"
        export OMP_SCHEDULE="${OMP_SCHEDULE:-static}"
        ;;
    throughput)
        export OMP_NUM_THREADS="${OMP_NUM_THREADS:-8}"
        export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
        export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-ACTIVE}"
        export OMP_SCHEDULE="${OMP_SCHEDULE:-static}"
        ;;
    general)
        export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
        export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
        export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-PASSIVE}"
        ;;
    *)
        echo "WARNING: 未知 DEPLOY_PROFILE='${PROFILE}'，回退到 general" >&2
        export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
        export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
        export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-PASSIVE}"
        ;;
esac

# 全局强制项（不因 Profile 变化）
export KMP_DUPLICATE_LIB_OK="${KMP_DUPLICATE_LIB_OK:-TRUE}"
export PYTHONUNBUFFERED="${PYTHONUNBUFFERED:-1}"
export GLOG_minloglevel="${GLOG_minloglevel:-2}"

# =============================================================================
# 2. 环境变量自检（技术总结 §6 容器部署要点 + §7 禁用项清单）
# =============================================================================
check_env() {
    echo "=== caffe-ffi 运行时环境 (Profile=${PROFILE}) ==="
    echo "  OMP_NUM_THREADS      = ${OMP_NUM_THREADS}"
    echo "  OPENBLAS_NUM_THREADS = ${OPENBLAS_NUM_THREADS}"
    echo "  OMP_WAIT_POLICY      = ${OMP_WAIT_POLICY:-<unset>}"
    echo "  OMP_SCHEDULE         = ${OMP_SCHEDULE:-<unset>}"
    echo "  OMP_PROC_BIND        = ${OMP_PROC_BIND:-<unset>} (应保持未设置)"
    echo "  KMP_DUPLICATE_LIB_OK = ${KMP_DUPLICATE_LIB_OK}"
    echo "  TZ                   = ${TZ:-<unset>}"

    local warn=0
    # 禁用项检查（技术总结 §7）
    if [ -n "${OPENBLAS_NUM_THREADS:-}" ] && [ "${OPENBLAS_NUM_THREADS}" -gt 1 ]; then
        echo "  [WARN] OPENBLAS_NUM_THREADS>1 会导致小 GEMM 3-11x 退化，应设为 1" >&2; warn=1
    fi
    if [ -n "${OMP_PROC_BIND:-}" ]; then
        echo "  [WARN] OMP_PROC_BIND 在混合 P/E 核架构上可能钉死线程到 E-core，应取消设置" >&2; warn=1
    fi
    if [ "${PROFILE}" = "latency" ] && [ "${OMP_WAIT_POLICY:-}" = "ACTIVE" ]; then
        echo "  [WARN] 延迟敏感场景应使用 PASSIVE，ACTIVE 自旋浪费 CPU 核心" >&2; warn=1
    fi
    if [ "${OMP_SCHEDULE:-}" = "runtime" ]; then
        echo "  [WARN] OMP_SCHEDULE=runtime 依赖用户环境变量，行为不可预测，应避免" >&2; warn=1
    fi
    if [ "$warn" -eq 0 ]; then
        echo "  [OK] 环境变量配置符合生产最佳实践"
    fi

    # 验证 caffe_ffi 可导入
    if [ -n "$PYTHON" ] && KMP_DUPLICATE_LIB_OK=TRUE "$PYTHON" -c "import caffe_ffi" 2>/dev/null; then
        VER=$(KMP_DUPLICATE_LIB_OK=TRUE "$PYTHON" -c "import caffe_ffi; print(caffe_ffi.__version__)" 2>/dev/null || echo "?")
        echo "  [OK] caffe_ffi v${VER} importable"
    else
        echo "  [ERROR] caffe_ffi 导入失败，请检查 conda 环境/共享库" >&2
        return 1
    fi
    return 0
}

# =============================================================================
# 3. 执行模式分派
# =============================================================================
if [ "${1:-}" = "--healthcheck" ]; then
    if check_env >/dev/null 2>&1; then
        echo "HEALTHY: caffe_ffi=${VER:-?}, profile=${PROFILE}, omp=${OMP_NUM_THREADS}, blas=${OPENBLAS_NUM_THREADS}"
        exit 0
    fi
    echo "UNHEALTHY: caffe_ffi 环境检查失败" >&2
    exit 1
fi

# 正常启动：打印环境自检 + exec 用户命令
check_env || echo "WARNING: 环境自检未完全通过，继续启动" >&2

if [ "$#" -eq 0 ]; then
    echo "=== 未提供启动命令，进入交互式 shell ==="
    exec bash
fi

echo "=== 启动命令: $* ==="
exec "$@"