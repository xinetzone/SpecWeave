#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VARIANTS_DIR="$(dirname "$SCRIPT_DIR")"
PROJECT_DIR="$(dirname "$VARIANTS_DIR")"

source "${VARIANTS_DIR}/shared/lib/logging.sh"
LOG_SERVICE="build-conda-llvm"
LOG_JSON_OUTPUT="/tmp/build-conda-llvm-events.jsonl"

OFFICIAL_MIRROR=false
NO_CACHE=""
TAG="latest"
SKIP_BUILD=false
VARIANT="conda-llvm"
DEP_VARIANT="conda"

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

One-click build and verify conda-llvm variant.

Options:
  --official           Use official mirrors (default: China mirrors)
  --no-cache           Disable Docker build cache
  --tag TAG            Image tag suffix (default: latest)
  --skip-build         Skip build, only run tests
  -h, --help           Show this help message

Examples:
  $0                           # Build conda-llvm with China mirrors
  $0 --official                # Build with official mirrors
  $0 --no-cache -t dev         # Build without cache, tag as dev
  $0 --skip-build              # Only run tests on existing image
EOF
}

check_docker() {
    log_step "Checking Docker availability"
    if ! docker info >/dev/null 2>&1; then
        log_fatal "Docker daemon is not running or not accessible"
    fi
    log_ok "Docker is available"
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
        log_error "Please build base image first:"
        log_error "  cd ${PROJECT_DIR} && bash scripts/build.sh --tag ${TAG}"
        if [ "$OFFICIAL_MIRROR" = false ]; then
            log_error "  or with China mirrors: bash scripts/build.sh --cn --tag ${TAG}"
        fi
        return 1
    fi
    log_ok "Base image exists: ${base_image}"
    echo ""
    return 0
}

check_conda_image() {
    local conda_image="devcontainer-base:${DEP_VARIANT}-${TAG}"
    log_step "Checking conda variant image: ${conda_image}"
    if ! image_exists "$conda_image"; then
        log_warn "Conda variant image not found, will build first"
        echo ""
        return 1
    fi
    log_ok "Conda variant image exists: ${conda_image}"
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
    echo ""
    
    bash "$build_script" "${build_args[@]}"
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
        
        echo "┌─────────────────────────────────────────────────┐"
        echo "│  BUILD SUCCESSFUL                               │"
        echo "├─────────────────────────────────────────────────┤"
        printf "│  Image:    %-37s│\n" "$image"
        printf "│  Size:     %-37s│\n" "$image_size"
        printf "│  Tag:      %-37s│\n" "$TAG"
        printf "│  Duration: %-37s│\n" "${total_duration}s"
        echo "└─────────────────────────────────────────────────┘"
        echo ""
        
        log_info "Quick verification:"
        echo ""
        docker run --rm "$image" llvm-config --version 2>&1 | head -1 | sed 's/^/  llvm-config: /'
        docker run --rm "$image" clang++ --version 2>&1 | head -1 | sed 's/^/  clang++:     /'
        echo ""
        
        return 0
    else
        echo "┌─────────────────────────────────────────────────┐"
        echo "│  BUILD FAILED                                   │"
        echo "└─────────────────────────────────────────────────┘"
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
echo "║       Conda-LLVM Variant One-Click Build Script             ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_info "Tag:              ${TAG}"
log_info "Mirror source:    $([ "$OFFICIAL_MIRROR" = true ] && echo 'official' || echo 'China (aliyun/tuna)')"
log_info "No cache:         $([ -n "$NO_CACHE" ] && echo 'yes' || echo 'no')"
log_info "Skip build:       ${SKIP_BUILD}"
echo ""

check_docker

if [ "$SKIP_BUILD" = false ]; then
    check_base_image || exit 1
    
    if ! check_conda_image; then
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
