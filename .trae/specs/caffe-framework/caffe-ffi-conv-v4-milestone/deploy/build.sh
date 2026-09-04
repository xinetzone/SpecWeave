#!/bin/bash
# =============================================================================
# build.sh — caffe-ffi 生产镜像构建脚本
#
# 功能：
#   1. 基于 deploy/Dockerfile 构建生产镜像（多阶段：builder 编译 → runtime 精简）
#   2. 支持国内镜像源（apt/pip/conda）与部署 Profile
#   3. 构建后打印运行提示与验证命令
#
# 用法：
#   bash deploy/build.sh                       # 构建 caffe-ffi-prod:latest
#   bash deploy/build.sh --cn                  # 国内镜像源构建
#   bash deploy/build.sh --profile latency     # 延迟敏感 Profile
#   bash deploy/build.sh --verify              # 构建后验证
#
# 注意：需在 SpecWeave 根目录执行（Dockerfile 依赖根目录相对路径 COPY 源码）
# =============================================================================
set -euo pipefail

# ── 路径定位 ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# 假设脚本位于 .trae/specs/<spec>/deploy/，向上回溯到 SpecWeave 根目录（4 级）
# deploy -> <spec> -> specs -> .trae -> 根目录
CONTEXT_DIR="$(cd "${SCRIPT_DIR}/../../../../" && pwd)"
DOCKERFILE="${SCRIPT_DIR}/Dockerfile"

# 若上下文无 AGENTS.md，提示在根目录执行
if [ ! -f "${CONTEXT_DIR}/AGENTS.md" ]; then
    echo "WARNING: 未在 SpecWeave 根目录检测到 AGENTS.md，当前上下文: ${CONTEXT_DIR}" >&2
    echo "请确认在 SpecWeave 根目录执行本脚本" >&2
fi

# ── 默认参数 ──
IMAGE_NAME="${IMAGE_NAME:-caffe-ffi-prod}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
APT_MIRROR="${APT_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"
CONDA_MIRROR="${CONDA_MIRROR:-official}"
PYTHON_VERSION="${PYTHON_VERSION:-3.14}"
DEPLOY_PROFILE="${DEPLOY_PROFILE:-general}"
NO_CACHE=""
VERIFY=false

usage() {
    cat << EOF
caffe-ffi 生产镜像构建脚本

用法: bash deploy/build.sh [选项]

选项:
  -t, --tag TAG            镜像标签（默认: latest）
  -n, --name NAME          镜像名称（默认: caffe-ffi-prod）
  -p, --profile PROFILE    部署 Profile: latency|throughput|general（默认: general）
      --python-version VER Conda 环境 Python 版本（默认: 3.14）
      --no-cache           禁用 Docker 构建缓存
      --cn                 使用国内镜像（apt:aliyun, pip:aliyun, conda:tuna）
      --apt-mirror MIRROR  APT 镜像源: official|aliyun|tuna（默认: official）
      --pip-mirror MIRROR  PyPI 镜像源: official|aliyun|tuna（默认: official）
      --conda-mirror M     Conda 镜像源: official|tuna（默认: official）
      --verify             构建后启动容器验证
  -h, --help               显示帮助

示例:
  bash deploy/build.sh                          # 通用 Profile
  bash deploy/build.sh --cn --profile latency   # 国内镜像 + 延迟敏感
  bash deploy/build.sh --verify                 # 构建并验证
EOF
}

# ── 参数解析 ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag) IMAGE_TAG="$2"; shift 2 ;;
        -n|--name) IMAGE_NAME="$2"; shift 2 ;;
        -p|--profile) DEPLOY_PROFILE="$2"; shift 2 ;;
        --python-version) PYTHON_VERSION="$2"; shift 2 ;;
        --no-cache) NO_CACHE="--no-cache"; shift ;;
        --cn) APT_MIRROR="aliyun"; PIP_MIRROR="aliyun"; CONDA_MIRROR="tuna"; shift ;;
        --apt-mirror) APT_MIRROR="$2"; shift 2 ;;
        --pip-mirror) PIP_MIRROR="$2"; shift 2 ;;
        --conda-mirror) CONDA_MIRROR="$2"; shift 2 ;;
        --verify) VERIFY=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "未知选项: $1" >&2; usage; exit 1 ;;
    esac
done

FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"

echo "=== caffe-ffi 生产镜像构建 ==="
echo "  镜像:       ${FULL_IMAGE}"
echo "  Profile:    ${DEPLOY_PROFILE}"
echo "  Python:     ${PYTHON_VERSION}"
echo "  APT 镜像:   ${APT_MIRROR}"
echo "  PyPI 镜像:  ${PIP_MIRROR}"
echo "  Conda 镜像: ${CONDA_MIRROR}"
echo "  上下文:     ${CONTEXT_DIR}"
echo "  Dockerfile: ${DOCKERFILE}"

# ── 前置检查：源码存在性 ──
if [ ! -f "${CONTEXT_DIR}/projects/xuanspace/vendor/tvm-ffi/CMakeLists.txt" ]; then
    echo "ERROR: tvm-ffi 源码未找到。请初始化 xuanspace 子模块:" >&2
    echo "  cd ${CONTEXT_DIR} && git submodule update --init projects/xuanspace" >&2
    exit 1
fi
if [ ! -f "${CONTEXT_DIR}/projects/xuanspace/libs/caffe-ffi/CMakeLists.txt" ]; then
    echo "ERROR: caffe-ffi 源码未找到: ${CONTEXT_DIR}/projects/xuanspace/libs/caffe-ffi" >&2
    exit 1
fi

# ── 构建 ──
cd "${CONTEXT_DIR}"
DOCKER_BUILDKIT=1 docker build \
    ${NO_CACHE} \
    -f "${DOCKERFILE}" \
    --build-arg APT_MIRROR="${APT_MIRROR}" \
    --build-arg PIP_MIRROR="${PIP_MIRROR}" \
    --build-arg CONDA_MIRROR="${CONDA_MIRROR}" \
    --build-arg PYTHON_VERSION="${PYTHON_VERSION}" \
    --build-arg DEPLOY_PROFILE="${DEPLOY_PROFILE}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${FULL_IMAGE}" \
    .

echo ""
echo "=== 构建完成: ${FULL_IMAGE} ==="
echo "镜像大小: $(docker images --format '{{.Size}}' "${FULL_IMAGE}" | head -1)"

# ── 运行提示 ──
echo ""
echo "=== 快速启动 ==="
echo "  # 交互式 shell（默认）"
echo "  # 注意: --cpuset-cpus 绑定 P-core 需按 NUMA/P-E 拓扑实测确认，避免误绑 E-core"
echo "  docker run -it --rm --cpus=4 \\"
echo "    -e DEPLOY_PROFILE=${DEPLOY_PROFILE} \\"
echo "    -v /path/to/models:/app/models:ro \\"
echo "    ${FULL_IMAGE}"
echo ""
echo "  # 启动推理服务（延迟敏感 Profile）"
echo "  docker run -d --name caffe-ffi-prod --restart=unless-stopped \\"
echo "    --cpus=4 --memory=4g \\"
echo "    -e DEPLOY_PROFILE=latency \\"
echo "    -e OMP_NUM_THREADS=4 -e OPENBLAS_NUM_THREADS=1 -e OMP_WAIT_POLICY=PASSIVE \\"
echo "    -v /path/to/models:/app/models:ro \\"
echo "    -v /path/to/config:/app/config:ro \\"
echo "    -p 8080:8080 \\"
echo "    ${FULL_IMAGE} python /app/serve.py --model /app/models/model.caffemodel"
echo ""
echo "  # 验证环境"
echo "  docker exec caffe-ffi-prod bash -lc 'python -c \"import caffe_ffi; print(caffe_ffi.__version__)\"'"
echo "  docker exec caffe-ffi-prod bash -lc 'printenv | grep -E \"OMP|OPENBLAS|KMP\"'"

# ── 构建后验证 ──
if $VERIFY; then
    echo ""
    echo "=== 构建后验证 ==="
    VERIFY_CTN="verify-caffe-ffi-prod-$(date +%s)"
    if docker run -d --name "$VERIFY_CTN" --cpus=4 -e DEPLOY_PROFILE="${DEPLOY_PROFILE}" "$FULL_IMAGE" sleep 30; then
        sleep 5
        echo "--- 健康检查状态 ---"
        docker inspect --format '{{.State.Health.Status}}' "$VERIFY_CTN" 2>/dev/null || echo "(healthcheck 状态未就绪)"
        echo "--- caffe_ffi 导入 ---"
        docker exec "$VERIFY_CTN" bash -lc 'KMP_DUPLICATE_LIB_OK=TRUE python -c "import caffe_ffi; print(\"caffe_ffi\", caffe_ffi.__version__, \"available\", caffe_ffi.is_available())"'
        echo "--- 环境变量 ---"
        docker exec "$VERIFY_CTN" bash -lc 'printenv | grep -E "^(OMP|OPENBLAS|KMP|TZ|DEPLOY_PROFILE)="'
        docker rm -f "$VERIFY_CTN" >/dev/null 2>&1
        echo "验证完成，验证容器已清理"
    else
        echo "ERROR: 验证容器启动失败" >&2
        exit 1
    fi
fi