#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$VARIANTS_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="build-onnx-pytorch"
LOG_JSON_OUTPUT="/tmp/build-onnx-pytorch-events.jsonl"

OFFICIAL_MIRROR=false
NO_CACHE=""
TAG="latest"
SKIP_BUILD=false
VARIANT="onnx-pytorch"
DEP_VARIANT="conda-llvm"
DEP_DEP_VARIANT="conda"

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

One-click build and verify onnx-pytorch variant (WSL2/Linux environment).

Build dependency chain:
  devcontainer-base:latest → conda → conda-llvm → onnx-pytorch
  (script will auto-build dependencies if missing)

Options:
  --official           Use official mirrors (default: China mirrors)
  --no-cache           Disable Docker build cache
  --tag TAG            Image tag suffix (default: latest)
  --skip-build         Skip build, only run tests
  -h, --help           Show this help message

Examples:
  $0                           # Build onnx-pytorch with China mirrors (WSL2/Linux)
  $0 --official                # Build with official mirrors
  $0 --no-cache --tag dev      # Build without cache, tag as dev
  $0 --skip-build              # Only run tests on existing image

Prerequisites:
  - WSL2 (Ubuntu 22.04+/24.04+) or native Linux
  - Docker daemon running (docker info works)
  - Base image devcontainer-base:${TAG} already built
    (build via: cd ${PROJECT_DIR} && bash scripts/build.sh --cn --tag ${TAG})
EOF
}

check_environment() {
    log_step "Checking execution environment"
    
    # 检查是否在WSL或Linux
    if grep -qi microsoft /proc/version 2>/dev/null; then
        log_ok "Running in WSL2 environment"
    elif [ "$(uname -s)" = "Linux" ]; then
        log_ok "Running in native Linux environment"
    else
        log_warn "Not running in Linux/WSL2 environment (detected: $(uname -s))"
        log_warn "This script is intended for WSL2/Linux. Docker build may fail on other OS."
    fi
    
    # 检查Docker
    if ! docker info >/dev/null 2>&1; then
        log_fatal "Docker daemon is not running or not accessible. Please start Docker first."
    fi
    log_ok "Docker is available"
    
    # 检查BuildKit支持
    if docker buildx version >/dev/null 2>&1; then
        log_ok "Docker Buildx available (BuildKit enabled)"
    else
        log_warn "Docker Buildx not detected. BuildKit features may not work."
    fi
    
    echo ""
}

image_exists() {
    local image="$1"
    docker images --format '{{.Repository}}:{{.Tag}}' | grep -q "^${image}$"
}

check_base_image() {
    local base_image="devcontainer-base:${TAG}"
    log_step "Checking base image: ${base_image}"
    if ! image_exists "$base_image"; then
        log_error "Base image not found: ${base_image}"
        log_error "Please build base image first (from project root directory):"
        log_error "  cd ${PROJECT_DIR}"
        if [ "$OFFICIAL_MIRROR" = false ]; then
            log_error "  bash scripts/build.sh --cn --tag ${TAG}"
        else
            log_error "  bash scripts/build.sh --tag ${TAG}"
        fi
        return 1
    fi
    log_ok "Base image exists: ${base_image}"
    echo ""
    return 0
}

check_variant_image() {
    local variant="$1"
    local variant_image="devcontainer-base:${variant}-${TAG}"
    log_step "Checking ${variant} variant image: ${variant_image}"
    if ! image_exists "$variant_image"; then
        log_warn "${variant} variant image not found, will build first"
        echo ""
        return 1
    fi
    log_ok "${variant} variant image exists: ${variant_image}"
    echo ""
    return 0
}

build_variant_image() {
    local variant="$1"
    local build_script="${VARIANTS_DIR}/build.sh"
    local -a build_args=(--variant "$variant" --tag "$TAG")
    
    if [ "$OFFICIAL_MIRROR" = false ]; then
        build_args+=(--cn)
    fi
    
    if [ -n "$NO_CACHE" ]; then
        build_args+=(--no-cache)
    fi
    
    log_step "Building variant: ${variant}"
    log_info "Command: bash ${build_script} ${build_args[*]}"
    log_info "Build context: ${PROJECT_DIR}"
    echo ""
    
    (cd "$PROJECT_DIR" && bash "$build_script" "${build_args[@]}")
}

run_tests() {
    local test_script="${SCRIPT_DIR}/test-${VARIANT}.sh"
    local image="devcontainer-base:${VARIANT}-${TAG}"
    
    log_step "Running unit tests on: ${image}"
    
    if [ ! -f "$test_script" ]; then
        log_warn "Test script not found: ${test_script}, skipping tests"
        return 0
    fi
    
    echo ""
    bash "$test_script" --tag "$TAG"
}

print_final_report() {
    local image="devcontainer-base:${VARIANT}-${TAG}"
    local build_end=$(date +%s)
    local total_duration=$((build_end - BUILD_START_TIME))
    
    echo ""
    log_step "Build Report"
    echo ""
    
    if image_exists "$image"; then
        local image_size
        image_size=$(docker images --format '{{.Size}}' "$image" | head -1)
        
        echo "┌─────────────────────────────────────────────────────────────┐"
        echo "│  BUILD SUCCESSFUL                                           │"
        echo "├─────────────────────────────────────────────────────────────┤"
        printf "│  Image:    %-49s│\n" "$image"
        printf "│  Size:     %-49s│\n" "$image_size"
        printf "│  Tag:      %-49s│\n" "$TAG"
        printf "│  Duration: %-49s│\n" "${total_duration}s"
        echo "└─────────────────────────────────────────────────────────────┘"
        echo ""
        
        log_info "Quick verification (PyTorch + ONNX versions):"
        echo ""
        docker run --rm "$image" /opt/conda/bin/python -c "import torch,onnx,onnxruntime;print('  torch     :', torch.__version__);print('  onnx      :', onnx.__version__);print('  onnxruntime:', onnxruntime.__version__);print('  cuda avail:', torch.cuda.is_available())" 2>&1 | grep -v "^\[" | sed 's/^/  /'
        echo ""
        
        log_info "Quick start command:"
        echo ""
        echo "  docker run -d --privileged -p 2222:22 -p 8888:8888 \\"
        echo "    -e USER_PASSWORD=pass -e JUPYTER_TOKEN=mysecret -e GRANT_SUDO=yes \\"
        echo "    -v \$(pwd)/workspace:/workspace \\"
        echo "    ${image}"
        echo ""
        
        return 0
    else
        echo "┌─────────────────────────────────────────────────────────────┐"
        echo "│  BUILD FAILED                                               │"
        echo "└─────────────────────────────────────────────────────────────┘"
        echo ""
        return 1
    fi
}

while [[ $# -gt 0 ]]; do
    case "$1" in
        --official)
            OFFICIAL_MIRROR=true
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --tag)
            if [ -z "$2" ]; then
                log_error "--tag requires a TAG argument"
                usage
                exit 1
            fi
            TAG="$2"
            shift 2
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

BUILD_START_TIME=$(date +%s)

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     ONNX-PyTorch Variant One-Click Build Script (WSL2)      ║"
echo "║     PyTorch CPU + ONNX Runtime Deep Learning Runtime        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_info "Tag:              ${TAG}"
log_info "Mirror source:    $([ "$OFFICIAL_MIRROR" = true ] && echo 'official' || echo 'China (aliyun/tuna)')"
log_info "No cache:         $([ -n "$NO_CACHE" ] && echo 'yes' || echo 'no')"
log_info "Skip build:       ${SKIP_BUILD}"
log_info "Dependency chain: base → conda → conda-llvm → onnx-pytorch"
echo ""

check_environment

if [ "$SKIP_BUILD" = false ]; then
    check_base_image || exit 1
    
    # 按依赖链顺序检查并构建
    if ! check_variant_image "$DEP_DEP_VARIANT"; then
        build_variant_image "$DEP_DEP_VARIANT" || exit 1
    fi
    
    if ! check_variant_image "$DEP_VARIANT"; then
        build_variant_image "$DEP_VARIANT" || exit 1
    fi
    
    build_variant_image "$VARIANT" || exit 1
else
    log_step "Skipping build (--skip-build specified)"
    local target_image="devcontainer-base:${VARIANT}-${TAG}"
    if ! image_exists "$target_image"; then
        log_fatal "Image not found: ${target_image}, cannot run tests"
    fi
    log_ok "Image exists: ${target_image}"
    echo ""
fi

run_tests
print_final_report
