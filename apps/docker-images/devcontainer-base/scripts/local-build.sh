#!/bin/bash
# =============================================================================
# DevContainer Local CI Build Script (WSL2/Linux)
# =============================================================================
# One-click local build that mirrors CI pipeline stages, with:
#   - Automatic WSL2 detection + Windows→WSL path mapping
#   - Docker Engine + Buildx auto-install/start in WSL2
#   - Optional native-WSL filesystem copy for 2-3x faster builds
#   - Full CI-equivalent build chain (base → conda → conda-llvm → onnx-pytorch → onnx-quantized)
#   - Structured logging + diagnostics collection on failure
#   - Lint checks (bash -n + Dockerfile structure validation)
#
# Usage (from Windows PowerShell):
#   wsl -d Ubuntu-26.04 -- bash /mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/scripts/local-build.sh [OPTIONS]
#
# Usage (from WSL2/Linux):
#   bash scripts/local-build.sh [OPTIONS]
#
# Options:
#   --cn                  Use China mirrors (aliyun apt + aliyun pip + tuna conda)
#   --official            Use official mirrors (default for CI, default for this script: cn)
#   --no-cache            Disable Docker build cache
#   --tag TAG             Image tag suffix (default: latest)
#   --variant VARIANT     Build specific variant (conda/conda-llvm/onnx-pytorch/onnx-quantized/all)
#                         default: all (full chain)
#   --native-fs           Copy project to WSL2 native filesystem (~) for faster IO
#   --skip-docker-setup   Skip Docker daemon check/setup (use if Docker already running)
#   --skip-lint           Skip pre-build lint checks
#   --logs-dir DIR        Directory for build logs (default: /tmp/devcontainer-local-build)
#   -h, --help            Show this help message
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# ── Load shared logging library ──
if [ -f "${PROJECT_DIR}/scripts/lib/logging.sh" ]; then
    source "${PROJECT_DIR}/scripts/lib/logging.sh"
else
    # Fallback minimal logging if lib not found
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
    log_step()  { echo -e "${CYAN}▶ $*${NC}"; }
    log_ok()    { echo -e "${GREEN}  ✅ $*${NC}"; }
    log_warn()  { echo -e "${YELLOW}  ⚠️  $*${NC}"; }
    log_error() { echo -e "${RED}  ❌ $*${NC}"; }
    log_fatal() { echo -e "${RED}  💀 $*${NC}"; exit 1; }
    log_info()  { echo -e "     $*"; }
fi

LOG_SERVICE="local-ci-build"

# ── Default configuration ──
OFFICIAL_MIRROR=false
NO_CACHE=""
TAG="latest"
VARIANT="all"
NATIVE_FS=false
SKIP_DOCKER_SETUP=false
SKIP_LINT=false
LOGS_DIR="/tmp/devcontainer-local-build-$(date +%Y%m%d-%H%M%S)"
BUILD_CONTEXT="$PROJECT_DIR"
WSL_DISTRO=""
IS_WSL2=false
MIRROR_FLAG="--cn"

# ── Color setup ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'

usage() {
    cat << EOF
${BOLD}DevContainer Local CI Build Script${NC}

Usage: $0 [OPTIONS]

Builds devcontainer-base images locally, mirroring CI pipeline stages.
Handles WSL2 detection, Docker setup, and path mapping automatically.

${BOLD}Options:${NC}
  --cn                  Use China mirrors (aliyun apt + aliyun pip + tuna conda) [default]
  --official            Use official mirrors
  --no-cache            Disable Docker build cache
  --tag TAG             Image tag suffix (default: latest)
  --variant VARIANT     Variant to build: conda, conda-llvm, onnx-pytorch, onnx-quantized, all [default: all]
  --native-fs           Copy project to WSL2 native filesystem for faster Docker builds
                        (recommended when project is on /mnt/<drive>/ cross-mount)
  --skip-docker-setup   Skip Docker daemon auto-check/setup
  --skip-lint           Skip pre-build lint checks
  --logs-dir DIR        Custom directory for build logs
  -h, --help            Show this help message

${BOLD}Examples:${NC}
  # Full build with China mirrors (WSL2, project on /mnt/d/)
  $0 --cn

  # Build only onnx-pytorch variant with cache, native FS for speed
  $0 --variant onnx-pytorch --native-fs

  # Full build with official mirrors (like CI)
  $0 --official --variant all

  # From Windows PowerShell:
  wsl -d Ubuntu-26.04 -- bash /mnt/d/spaces/SpecWeave/apps/docker-images/devcontainer-base/scripts/local-build.sh --cn --native-fs

${BOLD}WSL2 Notes:${NC}
  - Docker is auto-installed/started if not available
  - Buildx plugin is auto-installed if missing
  - Cross-FS builds (/mnt/d/) are 2-3x slower; use --native-fs for speed
  - Logs are saved to ${LOGS_DIR} by default
EOF
}

# ── Parse arguments ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --cn)
            OFFICIAL_MIRROR=false
            MIRROR_FLAG="--cn"
            shift
            ;;
        --official)
            OFFICIAL_MIRROR=true
            MIRROR_FLAG=""
            shift
            ;;
        --no-cache)
            NO_CACHE="--no-cache"
            shift
            ;;
        --tag)
            if [ -z "$2" ]; then log_fatal "--tag requires TAG argument"; fi
            TAG="$2"
            shift 2
            ;;
        --variant)
            if [ -z "$2" ]; then log_fatal "--variant requires VARIANT argument"; fi
            VARIANT="$2"
            shift 2
            ;;
        --native-fs)
            NATIVE_FS=true
            shift
            ;;
        --skip-docker-setup)
            SKIP_DOCKER_SETUP=true
            shift
            ;;
        --skip-lint)
            SKIP_LINT=true
            shift
            ;;
        --logs-dir)
            if [ -z "$2" ]; then log_fatal "--logs-dir requires DIR argument"; fi
            LOGS_DIR="$2"
            shift 2
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

# ══════════════════════════════════════════════════════════════════════════════
# Phase 0: Environment Detection & Setup
# ══════════════════════════════════════════════════════════════════════════════

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     DevContainer Local CI Build                            ║"
echo "║     Mirroring: base → conda → conda-llvm → onnx-pytorch → onnx-quantized ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

mkdir -p "$LOGS_DIR"
log_info "Logs directory: ${LOGS_DIR}"
echo ""

# ── Detect WSL2 ──
detect_wsl2() {
    log_step "Detecting execution environment"

    if grep -qi microsoft /proc/version 2>/dev/null; then
        IS_WSL2=true
        WSL_DISTRO="$(grep -i microsoft /proc/version 2>/dev/null | head -1 || echo 'WSL2')"
        log_ok "Running in WSL2 environment"
        log_info "Kernel: $(uname -r)"
    elif [ "$(uname -s)" = "Linux" ]; then
        IS_WSL2=false
        log_ok "Running in native Linux environment"
    else
        log_fatal "This script requires Linux or WSL2. Detected: $(uname -s)"
    fi
}

# ── Detect cross-FS path and optionally copy to native FS ──
setup_build_context() {
    log_step "Setting up build context"

    # Check if we're on a cross-mount (/mnt/<drive>/)
    if echo "$PROJECT_DIR" | grep -q "^/mnt/[a-zA-Z]/"; then
        CROSS_FS=true
        log_warn "Project is on WSL2 cross-mount (cross-FS IO is 2-3x slower)"
        log_info "Path: $PROJECT_DIR"

        if $NATIVE_FS; then
            NATIVE_DIR="$HOME/devcontainer-build-$(date +%Y%m%d-%H%M%S)"
            log_step "Copying project to WSL2 native filesystem: $NATIVE_DIR"
            cp -r "$PROJECT_DIR" "$NATIVE_DIR"
            BUILD_CONTEXT="$NATIVE_DIR"
            log_ok "Copied to native filesystem: $NATIVE_DIR"
            log_info "Build context: $BUILD_CONTEXT"
        else
            log_warn "Building on cross-mount. Use --native-fs for faster builds."
            BUILD_CONTEXT="$PROJECT_DIR"
        fi
    else
        CROSS_FS=false
        BUILD_CONTEXT="$PROJECT_DIR"
        log_ok "Project is on native Linux filesystem"
    fi

    echo ""
}

# ── Setup Docker in WSL2 ──
setup_docker() {
    if $SKIP_DOCKER_SETUP; then
        log_step "Skipping Docker setup (--skip-docker-setup)"
        if docker info >/dev/null 2>&1; then
            log_ok "Docker is accessible"
        else
            log_fatal "Docker not accessible even with --skip-docker-setup"
        fi
        echo ""
        return
    fi

    log_step "Checking Docker environment"

    # Check if docker command exists
    if ! command -v docker >/dev/null 2>&1; then
        log_warn "Docker not installed, installing..."

        if command -v apt-get >/dev/null 2>&1; then
            log_info "Installing docker.io via apt..."
            sudo apt-get update -qq
            sudo apt-get install -y -qq docker.io curl
            log_ok "Docker installed"
        else
            log_fatal "Cannot auto-install Docker (no apt-get). Please install Docker manually."
        fi
    else
        log_ok "Docker command available: $(docker --version 2>&1 | head -1)"
    fi

    # Start Docker daemon if not running
    if ! docker info >/dev/null 2>&1; then
        log_warn "Docker daemon not running, starting..."

        # Try systemd first
        if command -v systemctl >/dev/null 2>&1 && sudo systemctl status docker >/dev/null 2>&1; then
            sudo systemctl start docker
            sleep 3
        else
            # Start dockerd in background
            sudo dockerd >/tmp/dockerd.log 2>&1 &
            log_info "Waiting for Docker daemon to start..."
            for i in $(seq 1 15); do
                if docker info >/dev/null 2>&1; then break; fi
                sleep 2
            done
        fi

        if docker info >/dev/null 2>&1; then
            log_ok "Docker daemon started"
        else
            log_fatal "Failed to start Docker daemon. Check /tmp/dockerd.log"
        fi
    else
        log_ok "Docker daemon is running"
    fi

    # Fix socket permissions for non-root
    if ! docker info >/dev/null 2>&1; then
        log_warn "Fixing Docker socket permissions..."
        sudo chmod 666 /var/run/docker.sock 2>/dev/null || true
        sleep 1
    fi

    # Check/install Buildx
    if ! docker buildx version >/dev/null 2>&1; then
        log_warn "Docker Buildx not found, installing..."

        # Determine architecture
        ARCH=$(uname -m)
        case "$ARCH" in
            x86_64) BUILDX_ARCH="amd64" ;;
            aarch64) BUILDX_ARCH="arm64" ;;
            *) log_fatal "Unsupported architecture for buildx: $ARCH" ;;
        esac

        BUILDX_VER=$(curl -s https://api.github.com/repos/docker/buildx/releases/latest 2>/dev/null | grep tag_name | cut -d'"' -f4 || echo "v0.36.1")
        BUILDX_URL="https://github.com/docker/buildx/releases/download/${BUILDX_VER}/buildx-${BUILDX_VER}.linux-${BUILDX_ARCH}"

        log_info "Downloading buildx ${BUILDX_VER} for ${BUILDX_ARCH}..."
        sudo mkdir -p /usr/libexec/docker/cli-plugins
        curl -sLo /tmp/docker-buildx "$BUILDX_URL"
        chmod +x /tmp/docker-buildx
        sudo mv /tmp/docker-buildx /usr/libexec/docker/cli-plugins/docker-buildx

        if docker buildx version >/dev/null 2>&1; then
            log_ok "Buildx installed: $(docker buildx version 2>&1 | head -1)"
        else
            log_warn "Buildx installation may have failed, will try DOCKER_BUILDKIT=0 fallback"
        fi
    else
        log_ok "Docker Buildx available: $(docker buildx version 2>&1 | head -1)"
    fi

    # Docker info summary
    echo ""
    log_info "Docker server version: $(docker version --format '{{.Server.Version}}' 2>/dev/null || echo 'unknown')"
    log_info "Storage driver:       $(docker info --format '{{.Driver}}' 2>/dev/null || echo 'unknown')"
    log_info "Total memory:         $(docker info --format '{{.MemTotal}}' 2>/dev/null | numfmt --to=iec 2>/dev/null || echo 'unknown')"
    echo ""
}

# ── Lint checks ──
run_lint() {
    if $SKIP_LINT; then
        log_step "Skipping lint checks (--skip-lint)"
        echo ""
        return
    fi

    log_step "Running pre-build lint checks"
    local fail_count=0
    local pass_count=0

    # Bash syntax check
    log_info "Bash script syntax check..."
    while IFS= read -r -d '' script; do
        if bash -n "$script" 2>&1; then
            pass_count=$((pass_count + 1))
        else
            log_error "Syntax error in: $script"
            fail_count=$((fail_count + 1))
        fi
    done < <(find "$BUILD_CONTEXT/scripts" "$BUILD_CONTEXT/variants/scripts" -name "*.sh" -type f -print0 2>/dev/null)
    log_info "Bash scripts: $pass_count passed, $fail_count failed"

    # Dockerfile structure check (simplified)
    log_info "Dockerfile structure check..."
    local df_count=0
    local df_fail=0
    for dockerfile in "$BUILD_CONTEXT/Dockerfile" "$BUILD_CONTEXT"/variants/*/Dockerfile; do
        [ -f "$dockerfile" ] || continue
        df_count=$((df_count + 1))
        ok=true
        grep -q "^# syntax=" "$dockerfile" || { log_warn "Missing # syntax= in $dockerfile"; ok=false; }
        grep -q "^SHELL" "$dockerfile" || { log_warn "Missing SHELL in $dockerfile"; ok=false; }
        $ok || df_fail=$((df_fail + 1))
    done
    log_info "Dockerfiles: $df_count checked, $df_fail with warnings"

    if [ $fail_count -gt 0 ]; then
        log_fatal "Lint checks failed with $fail_count errors"
    fi
    log_ok "Lint checks passed"
    echo ""
}

# ══════════════════════════════════════════════════════════════════════════════
# Phase 1-4: Build pipeline (mirrors CI stages)
# ══════════════════════════════════════════════════════════════════════════════

run_build_stage() {
    local stage_name="$1"
    local stage_num="$2"
    local total_stages="$3"
    local build_cmd="$4"
    local log_file="$5"

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    printf "║  STAGE %d/%d: %-46s ║\n" "$stage_num" "$total_stages" "$stage_name"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    log_info "Command: $build_cmd"
    log_info "Start: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""

    local stage_start
    stage_start=$(date +%s)

    set +e
    (cd "$BUILD_CONTEXT" && eval "$build_cmd") 2>&1 | tee "$log_file"
    local exit_code=${PIPESTATUS[0]}
    set -e

    local stage_end
    stage_end=$(date +%s)
    local duration=$((stage_end - stage_start))

    echo ""
    if [ $exit_code -eq 0 ]; then
        log_ok "Stage ${stage_num}/${total_stages} PASSED (${duration}s)"
    else
        log_error "Stage ${stage_num}/${total_stages} FAILED after ${duration}s (exit code: $exit_code)"
        log_error "See log: $log_file"
    fi
    log_info "End: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
    echo ""

    return $exit_code
}

collect_local_diagnostics() {
    local failed_stage="$1"
    local diag_dir="${LOGS_DIR}/diagnostics"
    mkdir -p "$diag_dir"

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║  LOCAL DIAGNOSTICS (failure in: ${failed_stage})"
    echo "║  Saving to: ${diag_dir}"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    # Mirror CI's 10-dimension diagnostics
    {
        echo "=== Local Build Diagnostics ==="
        echo "Failure stage: ${failed_stage}"
        echo "Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
        echo "Project: ${BUILD_CONTEXT}"
        echo "Tag: ${TAG}"
        echo ""
    } > "$diag_dir/00-summary.txt"

    # System state
    {
        echo "=== System State ==="
        date -u
        echo ""
        echo "--- Uptime & Load ---"
        uptime
        echo ""
        echo "--- Memory ---"
        free -h
        echo ""
        echo "--- Disk ---"
        df -h
        echo ""
        echo "--- CPU ---"
        nproc
        cat /proc/cpuinfo | grep "model name" | head -1
    } > "$diag_dir/01-system.txt" 2>&1

    # Docker state
    {
        echo "=== Docker State ==="
        docker version 2>&1
        echo ""
        docker info 2>&1
        echo ""
        echo "--- Docker images ---"
        docker images -a --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" 2>&1 | head -20
        echo ""
        echo "--- Docker ps -a ---"
        docker ps -a 2>&1 | head -20
    } > "$diag_dir/02-docker.txt" 2>&1

    # Docker daemon log (WSL2)
    if $IS_WSL2; then
        sudo journalctl -u docker --no-pager -n 100 2>/dev/null > "$diag_dir/03-dockerd.log" || true
    fi

    # Build cache
    {
        echo "=== Build Cache ==="
        docker system df -v 2>&1 || true
        echo ""
        docker buildx du --verbose 2>&1 | head -50 || echo "buildx du not available"
    } > "$diag_dir/04-build-cache.txt" 2>&1

    # Error extraction from logs
    {
        echo "=== Error Patterns in Build Logs ==="
        for logfile in "$LOGS_DIR"/*.log; do
            [ -f "$logfile" ] || continue
            echo ""
            echo "--- $(basename "$logfile") ---"
            grep -inE "error:|fatal|failed|cannot|denied|permission denied|not found|no space|timeout|killed|OOM|out of memory" "$logfile" 2>/dev/null | tail -20 || echo "  (no error patterns found)"
        done
    } > "$diag_dir/05-errors.txt" 2>&1

    echo "Diagnostics saved to: $diag_dir"
    echo ""
    ls -la "$diag_dir/"
    echo ""
    log_error "Build failed. Check the log files and diagnostics above."
    log_info "To analyze diagnostics, use: python3 scripts/analyze-diagnostics.py ${diag_dir}"
}

# ══════════════════════════════════════════════════════════════════════════════
# Main Execution
# ══════════════════════════════════════════════════════════════════════════════

TOTAL_START=$(date +%s)

detect_wsl2
setup_build_context
setup_docker
run_lint

# ── Determine build plan ──
declare -a STAGES=()
declare -a STAGE_CMDS=()
declare -a STAGE_LOGS=()

stage_idx=0

# Always build base first (all variants depend on base, either directly or transitively)
if [ "$VARIANT" = "all" ] || [ "$VARIANT" = "base" ] || [ "$VARIANT" = "conda" ] || [ "$VARIANT" = "conda-llvm" ] || [ "$VARIANT" = "onnx-pytorch" ] || [ "$VARIANT" = "onnx-quantized" ]; then
    STAGES+=("base")
    STAGE_CMDS+=("bash scripts/build.sh --tag ${TAG} ${MIRROR_FLAG} ${NO_CACHE}")
    STAGE_LOGS+=("${LOGS_DIR}/01-base-build.log")
fi

if [ "$VARIANT" = "all" ] || [ "$VARIANT" = "conda" ] || [ "$VARIANT" = "conda-llvm" ] || [ "$VARIANT" = "onnx-pytorch" ] || [ "$VARIANT" = "onnx-quantized" ]; then
    STAGES+=("conda")
    STAGE_CMDS+=("bash variants/build.sh --variant conda --tag ${TAG} ${MIRROR_FLAG} ${NO_CACHE}")
    STAGE_LOGS+=("${LOGS_DIR}/02-conda-build.log")
fi

if [ "$VARIANT" = "all" ] || [ "$VARIANT" = "conda-llvm" ] || [ "$VARIANT" = "onnx-pytorch" ] || [ "$VARIANT" = "onnx-quantized" ]; then
    STAGES+=("conda-llvm")
    STAGE_CMDS+=("bash variants/build.sh --variant conda-llvm --tag ${TAG} ${MIRROR_FLAG} ${NO_CACHE}")
    STAGE_LOGS+=("${LOGS_DIR}/03-conda-llvm-build.log")
fi

if [ "$VARIANT" = "all" ] || [ "$VARIANT" = "onnx-pytorch" ] || [ "$VARIANT" = "onnx-quantized" ]; then
    STAGES+=("onnx-pytorch")
    STAGE_CMDS+=("bash variants/build.sh --variant onnx-pytorch --tag ${TAG} ${MIRROR_FLAG} ${NO_CACHE}")
    STAGE_LOGS+=("${LOGS_DIR}/04-onnx-pytorch-build.log")
fi

if [ "$VARIANT" = "all" ] || [ "$VARIANT" = "onnx-quantized" ]; then
    STAGES+=("onnx-quantized")
    STAGE_CMDS+=("bash variants/build.sh --variant onnx-quantized --tag ${TAG} ${MIRROR_FLAG} ${NO_CACHE}")
    STAGE_LOGS+=("${LOGS_DIR}/05-onnx-quantized-build.log")
fi

TOTAL_STAGES=${#STAGES[@]}
if [ $TOTAL_STAGES -eq 0 ]; then
    log_fatal "No stages to build. Check --variant value: $VARIANT"
fi

log_step "Build plan"
log_info "Variant(s):  ${STAGES[*]}"
log_info "Tag:         ${TAG}"
log_info "Mirror:      $($OFFICIAL_MIRROR && echo 'official' || echo 'China (cn)')"
log_info "No cache:    $([ -n "$NO_CACHE" ] && echo 'yes' || echo 'no')"
log_info "Native FS:   $NATIVE_FS"
log_info "Build context: ${BUILD_CONTEXT}"
log_info "Logs dir:    ${LOGS_DIR}"
echo ""

# ── Execute build stages ──
BUILD_FAILED=false
FAILED_STAGE=""

for i in "${!STAGES[@]}"; do
    stage_num=$((i + 1))
    if ! run_build_stage "${STAGES[$i]}" "$stage_num" "$TOTAL_STAGES" "${STAGE_CMDS[$i]}" "${STAGE_LOGS[$i]}"; then
        BUILD_FAILED=true
        FAILED_STAGE="${STAGES[$i]}"
        break
    fi
done

# ── Collect diagnostics on failure ──
if $BUILD_FAILED; then
    collect_local_diagnostics "$FAILED_STAGE"
    exit 1
fi

# ── Final summary ──
TOTAL_END=$(date +%s)
TOTAL_DURATION=$((TOTAL_END - TOTAL_START))

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    BUILD SUCCESSFUL                         ║"
echo "╠══════════════════════════════════════════════════════════════╣"

for i in "${!STAGES[@]}"; do
    image="devcontainer-base:${STAGES[$i]}-${TAG}"
    if [ "${STAGES[$i]}" = "base" ]; then
        image="devcontainer-base:${TAG}"
    fi
    size=$(docker images --format '{{.Size}}' "$image" 2>/dev/null | head -1 || echo "N/A")
    printf "║  %-15s %-12s %-30s ║\n" "${STAGES[$i]}" "$size" "$image"
done

echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Total duration: %-43s ║\n" "${TOTAL_DURATION}s"
printf "║  Logs: %-52s ║\n" "${LOGS_DIR}"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Quick verification
log_step "Quick verification"
final_image="devcontainer-base:${VARIANT}-${TAG}"
if [ "$VARIANT" = "all" ]; then
    final_image="devcontainer-base:onnx-quantized-${TAG}"
fi
echo ""
log_info "Verifying final image: $final_image"
if [ "$VARIANT" = "onnx-quantized" ] || [ "$VARIANT" = "all" ]; then
    docker run --rm "$final_image" /opt/conda/bin/python -c "
import torch, onnx, onnxruntime
print(f'  PyTorch:      {torch.__version__}')
print(f'  ONNX:         {onnx.__version__}')
print(f'  ONNX Runtime: {onnxruntime.__version__}')
print(f'  CUDA avail:   {torch.cuda.is_available()}')
from onnxruntime.quantization import quantize_dynamic, QuantType
print(f'  Quantization: available')
try:
    import neural_compressor
    print(f'  Neural Compressor: {neural_compressor.__version__} (optional)')
except ImportError:
    print(f'  Neural Compressor: not installed (optional)')
" 2>&1 | grep -v "^\[" | sed 's/^/  /' || log_warn "Quick verification failed"
else
    docker run --rm "$final_image" /opt/conda/bin/python -c "
import torch, onnx, onnxruntime
print(f'  PyTorch:      {torch.__version__}')
print(f'  ONNX:         {onnx.__version__}')
print(f'  ONNX Runtime: {onnxruntime.__version__}')
print(f'  CUDA avail:   {torch.cuda.is_available()}')
" 2>&1 | grep -v "^\[" | sed 's/^/  /' || log_warn "Quick verification failed (image may not have conda/python)"
fi
echo ""

# Cleanup native FS copy if used
if $NATIVE_FS && [ -n "$NATIVE_DIR" ] && [ -d "$NATIVE_DIR" ]; then
    log_info "Native FS build directory: $NATIVE_DIR"
    log_info "To clean up: rm -rf $NATIVE_DIR"
    echo ""
fi

log_ok "Local CI build complete!"
