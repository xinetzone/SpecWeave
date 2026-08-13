#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── 加载统一日志库 ──
source "${SCRIPT_DIR}/lib/logging.sh"
LOG_SERVICE="devcontainer-build"
LOG_JSON_OUTPUT="/tmp/devcontainer-base-events.jsonl"

IMAGE_NAME="${IMAGE_NAME:-devcontainer-base}"
IMAGE_TAG="${IMAGE_TAG:-conda-libmamba}"
REGISTRY="${REGISTRY:-}"
NO_CACHE=""
APT_MIRROR="${APT_MIRROR:-official}"
PIP_MIRROR="${PIP_MIRROR:-official}"
DOCKER_MIRROR="${DOCKER_MIRROR:-official}"
CONDA_MIRROR="${CONDA_MIRROR:-official}"
VERIFY=false
VERIFY_ONLY=false
QUICK_TEST=true
NETWORK_HOST="${NETWORK_HOST:-false}"

# ── 构建日志文件 ──
BUILD_TS="$(date +%Y%m%d-%H%M%S)"
BUILD_LOG_DIR="${PROJECT_DIR}/logs/builds"
BUILD_LOG_FILE="${BUILD_LOG_DIR}/build-${BUILD_TS}.log"
mkdir -p "$BUILD_LOG_DIR"

usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build the devcontainer-base Docker image.

Options:
  -t, --tag TAG          Image tag (default: 1.0)
  -n, --name NAME        Image name (default: devcontainer-base)
  -r, --registry REG     Registry prefix (e.g., your-registry.com)
  --no-cache             Disable Docker build cache
  --cn                   Use China mirrors (aliyun apt/pip/docker + tuna conda)
  --apt-mirror MIRROR    APT mirror: official|aliyun|tuna (default: official)
  --pip-mirror MIRROR    PyPI mirror: official|aliyun|tuna (default: official)
  --docker-mirror MIRROR Docker CE mirror: official|aliyun (default: official)
  --conda-mirror MIRROR  Conda mirror: official|tuna|aliyun (default: official)
  --verify               Run embedded verification after build
  --verify-only           Only verify existing image (skip build)
  --no-quick-test         Skip quick Python/libmamba smoke test after build
  --network-host          Use --network=host for docker build (helpful for network issues)
  --log-format=FMT       Log format: text (default) | json
  --log-level=LEVEL      Log level: DEBUG|INFO|WARN|ERROR (default: INFO)
  --log-json             Also output JSON to stdout
  -h, --help              Show this help message

Environment variables (overridden by CLI args):
  IMAGE_NAME, IMAGE_TAG, REGISTRY, APT_MIRROR, PIP_MIRROR, NETWORK_HOST

Examples:
  $0                                         # Build conda-libmamba with official mirrors
  $0 --tag latest --cn                       # Build :latest with China mirrors
  $0 --no-cache -t dev                       # Build without cache, tag as dev
  $0 --network-host --cn                     # Build with host network + China mirrors
  $0 --verify                                # Build and run full verification
  $0 --verify-only --tag conda-libmamba      # Verify existing image only
  $0 --no-quick-test                         # Build without smoke test
  $0 --log-format=json --log-json            # JSON output for monitoring

Docker modes:
  DinD (Docker-in-Docker): Requires --privileged flag for fully isolated Docker daemon
  DooD (Docker-out-of-Docker): Mount host /var/run/docker.sock without --privileged
EOF
}

# ── 解析日志参数 ──
eval "$(log_parse_args "$@")"

while [[ $# -gt 0 ]]; do
    case "$1" in
        -t|--tag) IMAGE_TAG="$2"; shift 2 ;;
        -n|--name) IMAGE_NAME="$2"; shift 2 ;;
        -r|--registry) REGISTRY="$2"; shift 2 ;;
        --no-cache) NO_CACHE="--no-cache"; shift ;;
        --cn) APT_MIRROR="aliyun"; PIP_MIRROR="aliyun"; DOCKER_MIRROR="aliyun"; CONDA_MIRROR="tuna"; shift ;;
        --apt-mirror) APT_MIRROR="$2"; shift 2 ;;
        --pip-mirror) PIP_MIRROR="$2"; shift 2 ;;
        --docker-mirror) DOCKER_MIRROR="$2"; shift 2 ;;
        --conda-mirror) CONDA_MIRROR="$2"; shift 2 ;;
        --verify) VERIFY=true; shift ;;
        --verify-only) VERIFY_ONLY=true; VERIFY=true; shift ;;
        --no-quick-test) QUICK_TEST=false; shift ;;
        --network-host) NETWORK_HOST=true; shift ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

if [ -n "$REGISTRY" ]; then
    FULL_IMAGE="${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
else
    FULL_IMAGE="${IMAGE_NAME}:${IMAGE_TAG}"
fi

cd "$PROJECT_DIR"

# ── 加载 .env 文件（如果存在） ──
if [ -f "$PROJECT_DIR/.env" ]; then
    log_info "Loading build environment from .env file..."
    set -a
    # shellcheck source=/dev/null
    source "$PROJECT_DIR/.env"
    set +a
fi

# ── 设置上下文字段 ──
log_set_field "image" "$FULL_IMAGE"
log_set_field "apt_mirror" "$APT_MIRROR"
log_set_field "pip_mirror" "$PIP_MIRROR"
log_set_field "docker_mirror" "$DOCKER_MIRROR"
log_set_field "conda_mirror" "$CONDA_MIRROR"
log_set_field "network_host" "$NETWORK_HOST"

# ── 错误处理 ──
_cleanup_on_error() {
    local exit_code=$?
    local line_no=${1:-0}
    if [ $exit_code -ne 0 ]; then
        echo ""
        log_error "Build failed with exit code ${exit_code} at line ${line_no}"
        log_error "Build log saved to: ${BUILD_LOG_FILE}"
        log_error "Last 30 lines of build output:"
        echo "────────────────────────────────────────"
        tail -n 30 "$BUILD_LOG_FILE" 2>/dev/null || true
        echo "────────────────────────────────────────"
        log_error "Tip: Check the full log above for error details."
        log_error "     If network-related, try: --network-host --cn"
        log_error "     If cache-related, try: --no-cache"
    fi
}
trap '_cleanup_on_error $LINENO' ERR

# ── 构建前预检 ──
preflight_checks() {
    log_step "Pre-flight Checks"
    local checks_ok=0
    local checks_fail=0

    # Check 1: Docker daemon
    log_info "[1/6] Checking Docker daemon..."
    if docker info >/dev/null 2>&1; then
        local docker_ver
        docker_ver=$(docker --version 2>/dev/null | awk '{print $3}' | tr -d ',')
        log_ok "  Docker is running (version: ${docker_ver})"
        checks_ok=$((checks_ok + 1))
    else
        log_fail "  Docker daemon is not running. Please start Docker first."
        checks_fail=$((checks_fail + 1))
    fi

    # Check 2: BuildKit support
    log_info "[2/6] Checking BuildKit support..."
    if docker buildx version >/dev/null 2>&1; then
        local buildx_ver
        buildx_ver=$(docker buildx version 2>/dev/null | awk '{print $2}')
        log_ok "  buildx available (version: ${buildx_ver})"
        checks_ok=$((checks_ok + 1))
    else
        log_warn "  buildx not found; falling back to legacy builder"
        checks_ok=$((checks_ok + 1))
    fi

    # Check 3: Disk space
    log_info "[3/6] Checking disk space..."
    local available_kb
    available_kb=$(df -k "$PROJECT_DIR" | tail -1 | awk '{print $4}')
    local available_gb=$((available_kb / 1024 / 1024))
    if [ "$available_gb" -ge 10 ]; then
        log_ok "  Disk space: ${available_gb}GB available (>= 10GB recommended)"
        checks_ok=$((checks_ok + 1))
    elif [ "$available_gb" -ge 5 ]; then
        log_warn "  Disk space: ${available_gb}GB available (>= 10GB recommended, builds may fail)"
        checks_ok=$((checks_ok + 1))
    else
        log_fail "  Disk space: only ${available_gb}GB available (need >= 10GB for a full build)"
        checks_fail=$((checks_fail + 1))
    fi

    # Check 4: Dockerfile exists
    log_info "[4/6] Checking Dockerfile..."
    if [ -f "$PROJECT_DIR/Dockerfile" ]; then
        local df_size
        df_size=$(wc -c < "$PROJECT_DIR/Dockerfile")
        log_ok "  Dockerfile found (size: ${df_size} bytes)"
        checks_ok=$((checks_ok + 1))
    else
        log_fail "  Dockerfile not found in ${PROJECT_DIR}"
        checks_fail=$((checks_fail + 1))
    fi

    # Check 5: Local Miniconda cache
    log_info "[5/6] Checking local Miniconda cache..."
    local miniconda_cache="$PROJECT_DIR/.cache/Miniconda3-latest-Linux-x86_64.sh"
    if [ -f "$miniconda_cache" ]; then
        local cache_size
        cache_size=$(du -h "$miniconda_cache" | cut -f1)
        log_ok "  Miniconda installer cached (${cache_size}) - will skip download"
        checks_ok=$((checks_ok + 1))
    else
        log_warn "  Miniconda installer not cached (will download during build)"
        checks_ok=$((checks_ok + 1))
    fi

    # Check 6: Build args summary
    log_info "[6/6] Build configuration summary:"
    printf "    %-20s %s\n" "Image:" "${FULL_IMAGE}"
    printf "    %-20s %s\n" "APT mirror:" "${APT_MIRROR}"
    printf "    %-20s %s\n" "PyPI mirror:" "${PIP_MIRROR}"
    printf "    %-20s %s\n" "Docker CE mirror:" "${DOCKER_MIRROR}"
    printf "    %-20s %s\n" "Conda mirror:" "${CONDA_MIRROR}"
    printf "    %-20s %s\n" "Network mode:" "$([ "$NETWORK_HOST" = true ] && echo 'host' || echo 'bridge')"
    printf "    %-20s %s\n" "Cache:" "$([ -n "$NO_CACHE" ] && echo 'disabled' || echo 'enabled')"
    printf "    %-20s %s\n" "Quick test:" "$([ "$QUICK_TEST" = true ] && echo 'yes' || echo 'no')"
    printf "    %-20s %s\n" "Full verify:" "$([ "$VERIFY" = true ] && echo 'yes' || echo 'no')"
    printf "    %-20s %s\n" "Log file:" "${BUILD_LOG_FILE}"
    checks_ok=$((checks_ok + 1))

    echo ""
    if [ "$checks_fail" -gt 0 ]; then
        log_fail "Pre-flight checks failed (${checks_fail} error(s)). Please fix and retry."
        exit 1
    fi
    log_ok "Pre-flight checks passed (${checks_ok}/6 checks OK)"
    echo ""
}

# ── 快速冒烟测试：Python 3.14 + libmamba ──
quick_smoke_test() {
    log_step "Quick Smoke Test: Python 3.14 + libmamba"

    local test_container="smoke-${IMAGE_NAME}-$(date +%s)"
    local test_passed=0
    local test_failed=0

    log_info "Starting test container (network=host)..."
    if ! docker run -d --network=host --name "$test_container" "$FULL_IMAGE" tail -f /dev/null >/dev/null 2>&1; then
        log_fail "Failed to start test container"
        return 1
    fi

    # Wait for container to be ready
    sleep 3

    run_test() {
        local name="$1"; shift
        log_info "  Testing: ${name}..."
        if docker exec "$test_container" "$@" >/dev/null 2>&1; then
            log_ok "    ${name}: PASS"
            test_passed=$((test_passed + 1))
        else
            local output
            output=$(docker exec "$test_container" "$@" 2>&1 || true)
            log_fail "    ${name}: FAIL"
            log_error "    Output: ${output}"
            test_failed=$((test_failed + 1))
        fi
    }

    # 1. Python version check
    log_info "  Testing: Python 3.14..."
    local py_ver
    py_ver=$(docker exec "$test_container" python --version 2>&1)
    if echo "$py_ver" | grep -q "Python 3\.14"; then
        log_ok "    Python version: ${py_ver} - PASS"
        test_passed=$((test_passed + 1))
    else
        log_fail "    Python version: ${py_ver} - FAIL (expected 3.14.x)"
        test_failed=$((test_failed + 1))
    fi

    # 2. Conda version
    run_test "Conda available" conda --version

    # 3. libmamba solver
    log_info "  Testing: libmamba solver..."
    local solver
    solver=$(docker exec "$test_container" conda config --show solver 2>&1 | grep "solver:" | awk '{print $2}')
    if [ "$solver" = "libmamba" ]; then
        log_ok "    Default solver: libmamba - PASS"
        test_passed=$((test_passed + 1))
    else
        log_fail "    Default solver: ${solver} - FAIL (expected libmamba)"
        test_failed=$((test_failed + 1))
    fi

    # 4. conda-forge channel only (no defaults)
    log_info "  Testing: channels (conda-forge only)..."
    local channels
    channels=$(docker exec "$test_container" conda config --show channels 2>&1)
    if echo "$channels" | grep -q "conda-forge" && ! echo "$channels" | grep -qE "^\s*-\s+defaults"; then
        log_ok "    Channels: conda-forge only - PASS"
        test_passed=$((test_passed + 1))
    else
        log_fail "    Channels: unexpected config - FAIL"
        log_error "    Output: ${channels}"
        test_failed=$((test_failed + 1))
    fi

    # 5. pip available
    run_test "pip available" pip --version

    # 6. Python can import standard modules
    run_test "Python imports (os, sys, json)" python -c "import os, sys, json; print('ok')"

    # 7. Conda can solve a package (dry-run, with timeout to avoid hanging)
    log_info "  Testing: conda solve (dry-run, timeout=30s)..."
    if timeout 30 docker exec "$test_container" conda install -y --dry-run tinycss2 >/dev/null 2>&1; then
        log_ok "    Conda solve with libmamba: PASS"
        test_passed=$((test_passed + 1))
    else
        log_warn "    Conda solve: WARN (timeout/network issue in test env, non-blocking)"
        test_passed=$((test_passed + 1))
    fi

    # Cleanup
    docker rm -f "$test_container" >/dev/null 2>&1

    echo ""
    log_summary "$test_passed" "$test_failed" "$((test_passed + test_failed))" 0 "$([ $test_failed -eq 0 ] && echo success || echo failed)"

    if [ "$test_failed" -gt 0 ]; then
        return 1
    fi
    return 0
}

# ------------------------------------------------------------------------------
# 嵌入式验证
# ------------------------------------------------------------------------------
verify_image() {
    log_step "Verifying ${FULL_IMAGE}"

    local verify_container="verify-${IMAGE_NAME}-$(date +%s)"
    local verify_result=0

    if ! docker run -d --privileged --name "$verify_container" \
        -e USER_PASSWORD=verifypass \
        -e JUPYTER_TOKEN=verifytoken \
        -e ENABLE_DOCKER=yes \
        -p 0:22 -p 0:8888 \
        "$FULL_IMAGE"; then
        log_error "Failed to start verification container"
        return 1
    fi

    log_info "Waiting for services to start (Docker daemon needs extra time)..."
    sleep 25

    log_info "Running healthcheck..."
    docker exec "$verify_container" /usr/local/bin/healthcheck.sh || verify_result=1

    log_info "Verifying Docker daemon (DinD mode)..."
    if docker exec "$verify_container" docker info >/dev/null 2>&1; then
        log_ok "Docker daemon is running"
    else
        log_error "Docker daemon not responding"
        verify_result=1
    fi

    log_info "Verifying Jupyter API..."
    docker exec "$verify_container" curl -sf http://localhost:8888/api >/dev/null || {
        log_error "Jupyter API not responding"
        verify_result=1
    }

    docker rm -f "$verify_container" >/dev/null 2>&1

    if [ "$verify_result" -eq 0 ]; then
        log_ok "All verification checks passed"
    else
        log_fail "Verification failed!"
        exit 1
    fi
}

if $VERIFY_ONLY; then
    log_event "verify_only_start" "image=$FULL_IMAGE"
    verify_image
    log_event "verify_only_complete" "status=success"
    exit 0
fi

# ── 构建前预检 ──
preflight_checks

# ── 构建 ──
log_step "Building ${FULL_IMAGE}"
log_info "Build log will be saved to: ${BUILD_LOG_FILE}"
echo ""

BUILD_START=$(date +%s)
log_event "build_start" "image=$FULL_IMAGE" "apt_mirror=$APT_MIRROR" "pip_mirror=$PIP_MIRROR" "conda_mirror=$CONDA_MIRROR"

# ── 构建网络参数 ──
NETWORK_ARG=""
if [ "$NETWORK_HOST" = true ]; then
    NETWORK_ARG="--network=host"
    log_info "Using --network=host for build"
fi

# ── 执行构建（plain progress + tee到日志文件） ──
log_info "Starting docker build (progress=plain, output to console + log file)..."
echo ""

set +e  # 暂时关闭set -e以便我们自己处理错误
DOCKER_BUILDKIT=1 docker build \
    ${NO_CACHE} \
    ${NETWORK_ARG} \
    --progress=plain \
    --build-arg APT_MIRROR="${APT_MIRROR}" \
    --build-arg PIP_MIRROR="${PIP_MIRROR}" \
    --build-arg DOCKER_MIRROR="${DOCKER_MIRROR}" \
    --build-arg CONDA_MIRROR="${CONDA_MIRROR}" \
    --build-arg BUILDKIT_INLINE_CACHE=1 \
    -t "${FULL_IMAGE}" \
    . 2>&1 | tee "$BUILD_LOG_FILE"
BUILD_EXIT_CODE=${PIPESTATUS[0]}
set -e

if [ "$BUILD_EXIT_CODE" -ne 0 ]; then
    echo ""
    log_error "Docker build failed with exit code ${BUILD_EXIT_CODE}"
    log_error "Build log: ${BUILD_LOG_FILE}"
    log_error "Last 50 lines of build output:"
    echo "────────────────────────────────────────"
    tail -n 50 "$BUILD_LOG_FILE"
    echo "────────────────────────────────────────"
    log_error "Troubleshooting tips:"
    log_error "  - Network issues: retry with --network-host --cn"
    log_error "  - Cache issues: retry with --no-cache"
    log_error "  - Disk space: free up space and retry"
    log_event "build_failed" "image=$FULL_IMAGE" "exit_code=$BUILD_EXIT_CODE"
    exit "$BUILD_EXIT_CODE"
fi

BUILD_END=$(date +%s)
BUILD_DURATION=$((BUILD_END - BUILD_START))
log_metric "build_duration_seconds" "$BUILD_DURATION" "seconds"

echo ""
log_ok "Build complete: ${FULL_IMAGE}"
IMAGE_SIZE=$(docker images --format '{{.Size}}' "${FULL_IMAGE}" | head -1)
log_info "Image size: ${IMAGE_SIZE}"
log_metric "image_size_mb" "$(echo "$IMAGE_SIZE" | grep -oE '[0-9.]+' | head -1)" "mb"
log_info "Build log saved to: ${BUILD_LOG_FILE}"

# ── 解析Dockerfile内部的BUILD TIMER（如果有） ──
echo ""
if grep -q "BUILD TIMING SUMMARY" "$BUILD_LOG_FILE" 2>/dev/null; then
    log_info "Build stage timing (from Dockerfile internal timer):"
    sed -n '/BUILD TIMING SUMMARY/,/RUNTIME TOTAL/p' "$BUILD_LOG_FILE" | while IFS= read -r line; do
        printf "    %s\n" "$line"
    done
fi

echo ""
log_info "═══════════════════════════════════════════════════════════"
log_info "Quick start (DinD mode - fully isolated Docker):"
echo "  docker run -d --privileged -p 2222:22 -p 8888:8888 \\"
echo "    -v \$(pwd)/workspace:/workspace \\"
echo "    -e USER_PASSWORD=mypassword -e JUPYTER_TOKEN=mysecret \\"
echo "    -e ENABLE_DOCKER=yes ${FULL_IMAGE}"
echo ""
log_info "Quick start (DooD mode - uses host Docker, no --privileged):"
echo "  docker run -d -p 2222:22 -p 8888:8888 \\"
echo "    -v \$(pwd)/workspace:/workspace \\"
echo "    -v /var/run/docker.sock:/var/run/docker.sock:ro \\"
echo "    -e USER_PASSWORD=mypassword -e JUPYTER_TOKEN=mysecret \\"
echo "    -e ENABLE_DOCKER=yes ${FULL_IMAGE}"
echo ""
log_info "SSH access:"
echo "  ssh -p 2222 devuser@localhost"
echo ""
log_info "Jupyter access:"
echo "  http://localhost:8888/?token=mysecret"
echo ""
log_info "Note: DinD mode requires --privileged for the nested Docker daemon."
log_info "      Use DooD mode if you only need access to the host's Docker."
echo ""
if [ -n "$REGISTRY" ]; then
    log_info "To push:"
    echo "  docker push ${FULL_IMAGE}"
fi
log_info "═══════════════════════════════════════════════════════════"

log_event "build_complete" "image=$FULL_IMAGE" "duration=$BUILD_DURATION" "status=success"

# ── 快速冒烟测试 ──
if $QUICK_TEST; then
    echo ""
    if quick_smoke_test; then
        log_ok "Quick smoke test passed!"
    else
        log_fail "Quick smoke test found issues!"
        exit 1
    fi
fi

if $VERIFY; then
    verify_image
fi
