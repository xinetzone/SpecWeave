#!/bin/bash
# =============================================================================
# PyTorch Base Image Build Script
# =============================================================================
# Reference: https://pytorch.org/get-started/locally/
#
# Usage: ./build.sh [OPTIONS]
#
# Options:
#   --gpu                 Build GPU version (CUDA 12.6)
#   --cuda VER            CUDA version (default: 12.6, options: 12.6/13.0/13.2)
#   --offline             Build using local packages in offline/ directory
#   --prepare-offline     Download offline resources without building
#   --torch-version VER   PyTorch version (default: 2.13.0)
#   --python-version VER  Python version (default: 3.14, supported: 3.10-3.14)
#   --tag NAME            Custom image tag
#   --no-cache            Disable Docker build cache
#   --no-verify           Skip post-build verification
#   --quiet, -q           Suppress banner output in container
#   --verbose, -v         Enable verbose debug logging
#   --no-log-file         Don't save build log to file (logs/ directory)
#   --help, -h            Show this help message
#
# Offline mode:
#   Place files in offline/ before building with --offline:
#     offline/miniconda/Miniconda3-latest-Linux-x86_64.sh
#     offline/wheels/torch-*.whl
#     offline/wheels/torchvision-*.whl
#     offline/wheels/torchaudio-*.whl (optional)
#     offline/conda-pkgs/*  (conda package tarballs, optional)
#
#   Or use --prepare-offline to auto-download these resources.
# =============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# =============================================================================
# Step 1: Define logging functions FIRST (before any output/redirection)
# =============================================================================
LOG_LEVEL="${LOG_LEVEL:-INFO}"
VERBOSE=0
BUILD_START_TS=$(date '+%Y%m%d-%H%M%S')
BUILD_START_HUMAN=$(date '+%Y-%m-%d %H:%M:%S')
SCRIPT_START_TIME=$(date +%s)
LOG_FILE_ACTIVE=1
LAST_ACTION="initializing"

log_info() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[INFO]  ${timestamp} | $*"
}

log_warn() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[WARN]  ${timestamp} | $*" >&2
}

log_error() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[ERROR] ${timestamp} | $*" >&2
}

log_debug() {
    if [ "$VERBOSE" = "1" ] || [ "$LOG_LEVEL" = "DEBUG" ]; then
        local timestamp
        timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        echo "[DEBUG] ${timestamp} | $*"
    fi
}

log_phase() {
    echo ""
    echo "============================================================"
    echo "  PHASE: $*"
    echo "============================================================"
    LAST_ACTION="phase: $*"
}

log_branch() {
    log_info "[BRANCH] >>> Entering: $*"
}

log_cmd() {
    log_info "[CMD] $*"
}

log_result() {
    log_info "[RESULT] $*"
}

mark_action() {
    LAST_ACTION="$*"
    log_debug "[MARK] Last action set to: $*"
}

# =============================================================================
# Step 2: Initialize log file and redirect output
# =============================================================================

# Try to create logs/ directory, fallback to temp dir if fails
init_log_file() {
    local log_dir="${SCRIPT_DIR}/logs"
    local log_filename="build-${BUILD_START_TS}.log"
    local log_path=""

    if mkdir -p "$log_dir" 2>/dev/null; then
        log_path="${log_dir}/${log_filename}"
    elif [ -n "${TEMP:-}" ] && mkdir -p "$TEMP" 2>/dev/null; then
        log_path="${TEMP}/pytorch-base-build-${BUILD_START_TS}.log"
    elif [ -n "${TMP:-}" ] && mkdir -p "$TMP" 2>/dev/null; then
        log_path="${TMP}/pytorch-base-build-${BUILD_START_TS}.log"
    elif mkdir -p /tmp 2>/dev/null; then
        log_path="/tmp/pytorch-base-build-${BUILD_START_TS}.log"
    else
        log_path="./build-${BUILD_START_TS}.log"
    fi

    echo "$log_path"
}

LOG_FILE=$(init_log_file)
export LOG_FILE

# Redirect stdout and stderr to tee (terminal + log file)
exec > >(tee -a "$LOG_FILE") 2>&1

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  PyTorch Base Image Build Log                               ║"
echo "╠══════════════════════════════════════════════════════════════╣"
printf "║  Start time : %-46s ║\n" "$BUILD_START_HUMAN"
printf "║  Log file   : %-46s ║\n" "$LOG_FILE"
printf "║  Script dir : %-46s ║\n" "$SCRIPT_DIR"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Save original arguments for rerun message in error handler
ORIG_ARGS="$*"
mark_action "script initialization"

# =============================================================================
# Error handler - trap errors and log FULL context to file
# =============================================================================
on_error() {
    local line_no=$1
    local cmd=$2
    local error_ts
    error_ts=$(date '+%Y-%m-%d %H:%M:%S')

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                    ❌ BUILD FAILED!                          ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    log_error "Build FAILED at ${error_ts}"
    log_error "  Failed line  : ${line_no}"
    log_error "  Last action  : ${LAST_ACTION}"
    log_error "  Failed cmd   : ${cmd}"
    local _elapsed=$(( $(date +%s) - ${SCRIPT_START_TIME:-$(date +%s)} ))
    log_error "  Elapsed time : $(printf '%dm%ds' $((_elapsed / 60)) $((_elapsed % 60)))"
    echo ""
    log_error "════════════════════ Build Configuration ════════════════════"
    log_error "  Script dir  : ${SCRIPT_DIR}"
    log_error "  Image tag   : ${IMAGE_TAG:-<not yet determined>}"
    log_error "  Dockerfile  : ${DOCKERFILE}"
    log_error "  USE_GPU     : ${USE_GPU:-?}"
    log_error "  OFFLINE_MODE: ${OFFLINE_MODE:-?}"
    log_error "  NO_CACHE    : ${NO_CACHE:-?}"
    log_error "  QUIET       : ${QUIET:-?}"
    log_error "  Python ver  : ${PYTHON_VERSION:-?}"
    log_error "  PyTorch ver : ${PYTORCH_VERSION:-?}"
    log_error "  CUDA ver    : ${CUDA_VERSION:-?}"
    log_error "  Base image  : ${BASE_IMAGE:-?}"
    echo ""
    log_error "════════════════════ System Environment ═════════════════════"
    log_error "  OS          : $(uname -a 2>/dev/null || echo 'unknown')"
    log_error "  Docker ver  : $(docker --version 2>/dev/null || echo 'unavailable')"
    log_error "  Disk space  : $(df -h . 2>/dev/null | tail -1 | awk '{print "Available: "$4", Used: "$5}' || echo 'unknown')"
    log_error "  Memory      : $(free -h 2>/dev/null | grep Mem | awk '{print "Total: "$2", Available: "$7}' || echo 'unknown')"
    log_error "  Docker info : $(docker info --format '{{.ServerVersion}}' 2>/dev/null || echo 'daemon not reachable')"
    echo ""
    log_error "════════════════════ Debugging Tips ════════════════════════"
    log_error "  Complete log: ${LOG_FILE}"
    log_error "  Manual debug: docker run -it --rm ${IMAGE_TAG:-<image-name>} /bin/bash"
    log_error "  Rerun build : $0 $ORIG_ARGS"
    echo ""

    # Write error footer to log file
    {
        echo ""
        echo "═══════════════════════════════════════════════════════════════"
        echo "  BUILD FAILED at ${error_ts}"
        echo "  Log file: ${LOG_FILE}"
        echo "═══════════════════════════════════════════════════════════════"
        echo ""
    } >> "$LOG_FILE" 2>/dev/null || true

    # Flush any pending output
    sync 2>/dev/null || true
}
trap 'on_error ${LINENO} "$BASH_COMMAND"' ERR

# =============================================================================
# Default values (per pytorch.org/get-started/locally/)
# =============================================================================
log_info "Initializing build script (script dir: ${SCRIPT_DIR})"

USE_GPU=0
OFFLINE_MODE=0
PREPARE_OFFLINE=0
PYTORCH_VERSION="2.13.0"
PYTHON_VERSION="3.14"
CUDA_VERSION="12.6"
CUSTOM_TAG=""
NO_CACHE=0
NO_VERIFY=0
QUIET=0
NO_LOG_FILE=0
DOCKERFILE="Dockerfile"
OFFLINE_DIR="${SCRIPT_DIR}/offline"
BASE_IMAGE="ubuntu:26.04"

log_debug "Default config initialized:"
log_debug "  PYTORCH_VERSION=${PYTORCH_VERSION}"
log_debug "  PYTHON_VERSION=${PYTHON_VERSION}"
log_debug "  CUDA_VERSION=${CUDA_VERSION}"
log_debug "  BASE_IMAGE=${BASE_IMAGE}"

# =============================================================================
# Parse arguments
# =============================================================================
log_info "Parsing command line arguments: $*"

while [[ $# -gt 0 ]]; do
    log_debug "Processing argument: '$1'"
    case "$1" in
        --gpu)
            log_branch "GPU mode enabled (--gpu)"
            USE_GPU=1
            shift
            ;;
        --cuda)
            CUDA_VERSION="$2"
            log_info "CUDA version set to: ${CUDA_VERSION} (--cuda)"
            shift 2
            ;;
        --offline)
            log_branch "Offline mode enabled (--offline)"
            OFFLINE_MODE=1
            shift
            ;;
        --prepare-offline)
            log_branch "Prepare offline resources mode (--prepare-offline)"
            PREPARE_OFFLINE=1
            shift
            ;;
        --torch-version)
            PYTORCH_VERSION="$2"
            log_info "PyTorch version set to: ${PYTORCH_VERSION} (--torch-version)"
            shift 2
            ;;
        --python-version)
            PYTHON_VERSION="$2"
            log_info "Python version set to: ${PYTHON_VERSION} (--python-version)"
            shift 2
            ;;
        --tag)
            CUSTOM_TAG="$2"
            log_info "Custom image tag: ${CUSTOM_TAG} (--tag)"
            shift 2
            ;;
        --no-cache)
            log_branch "Docker build cache disabled (--no-cache)"
            NO_CACHE=1
            shift
            ;;
        --no-verify)
            log_branch "Post-build verification skipped (--no-verify)"
            NO_VERIFY=1
            shift
            ;;
        --quiet|-q)
            log_info "Quiet mode enabled (--quiet/-q)"
            QUIET=1
            shift
            ;;
        --verbose|-v)
            log_info "Verbose mode enabled (--verbose/-v)"
            VERBOSE=1
            shift
            ;;
        --no-log-file)
            log_branch "Log file disabled (--no-log-file)"
            NO_LOG_FILE=1
            shift
            ;;
        --help|-h)
            echo "PyTorch Base Image Build Script"
            echo "Reference: https://pytorch.org/get-started/locally/"
            echo ""
            echo "Usage: ./build.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --gpu                 Build GPU version (default: CPU only)"
            echo "  --cuda VER            CUDA version (default: ${CUDA_VERSION}, options: 12.6/13.0/13.2)"
            echo "  --offline             Build using local packages in offline/ directory"
            echo "  --prepare-offline     Download offline resources without building"
            echo "  --torch-version VER   PyTorch version (default: ${PYTORCH_VERSION})"
            echo "  --python-version VER  Python version (default: ${PYTHON_VERSION}, supported: 3.10-3.14)"
            echo "  --tag NAME            Custom image tag"
            echo "  --no-cache            Disable Docker build cache"
            echo "  --no-verify           Skip post-build verification"
            echo "  --verbose, -v         Enable verbose debug logging"
            echo "  --no-log-file         Don't save build log to logs/ directory"
            echo "  --help, -h            Show this help message"
            echo ""
            echo "Offline directories:"
            echo "  offline/miniconda/    Miniconda installer script"
            echo "  offline/wheels/       pip wheel files (torch, torchvision, etc.)"
            echo "  offline/conda-pkgs/   conda package cache (optional)"
            exit 0
            ;;
        *)
            log_error "Unknown option: '$1'"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

log_info "Argument parsing complete"

# =============================================================================
# Determine architecture
# =============================================================================
log_phase "Environment Detection"

detect_arch() {
    local arch
    arch=$(uname -m)
    log_debug "Raw machine architecture: ${arch}"
    case "$arch" in
        x86_64|amd64)
            log_result "Architecture detected: x86_64 (amd64)"
            echo "x86_64"
            ;;
        aarch64|arm64)
            log_result "Architecture detected: aarch64 (arm64)"
            echo "aarch64"
            ;;
        *)
            log_error "Unsupported architecture: ${arch}"
            exit 1
            ;;
    esac
}
ARCH=$(detect_arch)

# =============================================================================
# Validate CUDA version
# =============================================================================
log_info "Validating CUDA version: ${CUDA_VERSION}"
case "${CUDA_VERSION}" in
    12.6|13.0|13.2)
        log_debug "CUDA version ${CUDA_VERSION} is officially supported per pytorch.org"
        ;;
    *)
        log_warn "CUDA version ${CUDA_VERSION} not in officially supported list (12.6/13.0/13.2)"
        log_warn "Build may fail if the version doesn't exist on download.pytorch.org"
        ;;
esac

# =============================================================================
# Determine image tag and CUDA index suffix
# =============================================================================
CUDA_INDEX_SUFFIX="${CUDA_VERSION//./}"
log_debug "CUDA index suffix: cu${CUDA_INDEX_SUFFIX}"

if [ "$USE_GPU" = "1" ]; then
    log_branch "GPU/CPU: GPU variant selected (CUDA ${CUDA_VERSION}, index suffix: ${CUDA_INDEX_SUFFIX})"
    VARIANT="gpu-cu${CUDA_INDEX_SUFFIX}"
else
    log_branch "GPU/CPU: CPU-only variant selected"
    VARIANT="cpu"
fi

if [ -n "$CUSTOM_TAG" ]; then
    log_branch "Using custom image tag (overrides auto-generated tag)"
    IMAGE_TAG="$CUSTOM_TAG"
else
    IMAGE_TAG="pytorch-base:${PYTORCH_VERSION}-py${PYTHON_VERSION}-${VARIANT}"
    log_debug "Auto-generated image tag: ${IMAGE_TAG}"
fi

log_result "Final image tag: ${IMAGE_TAG}"
log_result "PyTorch pip index: $( [ "$USE_GPU" = "1" ] && echo "https://download.pytorch.org/whl/cu${CUDA_INDEX_SUFFIX}" || echo "https://download.pytorch.org/whl/cpu" )"

# =============================================================================
# Prepare offline resources
# =============================================================================
prepare_offline_resources() {
    log_phase "Preparing Offline Resources"
    log_info "Offline directory: ${OFFLINE_DIR}"
    log_info "Target architecture: ${ARCH}"
    log_info "GPU mode: ${USE_GPU} (CUDA index: cu${CUDA_INDEX_SUFFIX})"

    log_debug "Creating offline subdirectories..."
    mkdir -p "${OFFLINE_DIR}/miniconda" "${OFFLINE_DIR}/wheels" "${OFFLINE_DIR}/conda-pkgs"
    log_info "Directories ready: miniconda/, wheels/, conda-pkgs/"

    # Download Miniconda installer
    local miniconda_file="${OFFLINE_DIR}/miniconda/Miniconda3-latest-Linux-${ARCH}.sh"
    log_info "Checking Miniconda installer: ${miniconda_file}"
    if [ -f "$miniconda_file" ] && [ -s "$miniconda_file" ]; then
        log_result "Miniconda installer already exists: $(basename "$miniconda_file") ($(du -h "$miniconda_file" | cut -f1))"
    else
        log_branch "Miniconda installer not found or empty, starting download (with fallback)..."

        log_cmd "wget --tries=5 --timeout=120 --waitretry=5 (TUNA mirror)..."
        local download_ok=0
        if wget --tries=5 --timeout=120 --waitretry=5 \
            "https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-latest-Linux-${ARCH}.sh" \
            -O "$miniconda_file" 2>&1; then
            download_ok=1
            log_result "Miniconda downloaded from TUNA mirror: $(du -h "$miniconda_file" | cut -f1)"
        else
            log_warn "TUNA mirror download failed, falling back to official repo..."
            log_cmd "wget --tries=5 --timeout=120 --waitretry=5 (official repo)..."
            if wget --tries=5 --timeout=120 --waitretry=5 \
                "https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-${ARCH}.sh" \
                -O "$miniconda_file" 2>&1; then
                download_ok=1
                log_result "Miniconda downloaded from official repo: $(du -h "$miniconda_file" | cut -f1)"
            else
                log_error "Failed to download Miniconda from both mirrors!"
                return 1
            fi
        fi
    fi

    # Verify downloaded file
    if [ -f "$miniconda_file" ] && [ -s "$miniconda_file" ]; then
        local file_size
        file_size=$(stat -c%s "$miniconda_file" 2>/dev/null || wc -c < "$miniconda_file")
        log_debug "Miniconda file size: ${file_size} bytes"
        if [ "$file_size" -lt 10000000 ]; then
            log_warn "Miniconda file seems too small (${file_size} bytes, expected >10MB), download may be corrupted"
        fi
    fi

    # Determine PyTorch index URL
    local torch_index
    if [ "$USE_GPU" = "1" ]; then
        torch_index="https://download.pytorch.org/whl/cu${CUDA_INDEX_SUFFIX}"
        log_branch "Using GPU PyTorch index: ${torch_index}"
    else
        torch_index="https://download.pytorch.org/whl/cpu"
        log_branch "Using CPU PyTorch index: ${torch_index}"
    fi

    log_info "Downloading PyTorch ${PYTORCH_VERSION} wheels (torch + torchvision; torchaudio optional per official guide)..."

    # Try pip download with fallback
    log_cmd "pip download --dest wheels/ torch==${PYTORCH_VERSION} torchvision (from PyTorch index)..."
    local pip_ok=0
    if pip download --dest "${OFFLINE_DIR}/wheels" \
        --index-url "$torch_index" \
        "torch==${PYTORCH_VERSION}" \
        "torchvision" 2>&1; then
        pip_ok=1
        log_result "PyTorch wheels downloaded from official PyTorch index"
    else
        log_warn "pip download from PyTorch index failed, trying Aliyun mirror..."
        if pip download --dest "${OFFLINE_DIR}/wheels" \
            -i https://mirrors.aliyun.com/pypi/simple/ \
            "torch==${PYTORCH_VERSION}" \
            "torchvision" 2>&1; then
            pip_ok=1
            log_result "PyTorch wheels downloaded from Aliyun mirror (may be CPU-only; check carefully!)"
            log_warn "Wheels from Aliyun mirror may be CPU-only; for GPU builds, please download manually from:"
            log_warn "  ${torch_index}"
        else
            log_warn "Auto-download of wheels failed. Please manually download from:"
            log_warn "  ${torch_index}"
            log_warn "  and place .whl files in offline/wheels/"
        fi
    fi

    log_info "Downloading additional pip packages (numpy, setuptools, wheel, pip)..."
    log_cmd "pip download numpy setuptools wheel pip (from Aliyun mirror)..."
    pip download --dest "${OFFLINE_DIR}/wheels" \
        -i https://mirrors.aliyun.com/pypi/simple/ \
        numpy setuptools wheel pip 2>/dev/null || {
        log_warn "Some additional packages failed to download (non-critical)"
    }

    echo ""
    echo "============================================================"
    echo "  Offline resources prepared in: ${OFFLINE_DIR}/"
    echo "============================================================"
    echo ""

    local wheel_count
    wheel_count=$(ls "${OFFLINE_DIR}/wheels/"*.whl 2>/dev/null | wc -l)
    echo "  Wheel files (${wheel_count} total):"
    if [ "$wheel_count" -gt 0 ]; then
        ls -lh "${OFFLINE_DIR}/wheels/"*.whl 2>/dev/null | awk '{print "    " $NF " (" $5 ")"}'
    else
        echo "    (none - download failed or in progress)"
    fi
    echo ""

    local miniconda_size
    if [ -f "$miniconda_file" ]; then
        miniconda_size=$(du -h "$miniconda_file" | cut -f1)
    else
        miniconda_size="MISSING"
    fi
    echo "  Miniconda installer: ${miniconda_size}"
    echo ""

    echo "  You can now build with: ./build.sh --offline"
    echo ""
    log_result "Offline resource preparation complete"
}

if [ "$PREPARE_OFFLINE" = "1" ]; then
    log_branch "Prepare-only mode: will download resources then exit (no Docker build)"
    prepare_offline_resources
    log_info "Prepare-only mode completed, exiting"
    exit 0
fi

# =============================================================================
# Validate offline mode
# =============================================================================
if [ "$OFFLINE_MODE" = "1" ]; then
    log_phase "Offline Resource Validation"
    log_info "Offline mode ENABLED - checking local resource availability..."
    echo ""

    local_miniconda=$(ls "${OFFLINE_DIR}/miniconda/"Miniconda3-*-Linux-${ARCH}.sh 2>/dev/null | head -1 || true)
    has_wheels=0
    has_conda_pkgs=0

    log_info "Checking Miniconda installer..."
    if [ -n "$local_miniconda" ] && [ -s "$local_miniconda" ]; then
        log_result "[OK] Miniconda installer found: $(basename "$local_miniconda") ($(du -h "$local_miniconda" | cut -f1))"
    else
        log_warn "[WARN] Miniconda installer NOT found in offline/miniconda/"
        log_warn "       Will fall back to online download during Docker build (may fail if no network)"
    fi

    log_info "Checking PyTorch wheel files..."
    if ls "${OFFLINE_DIR}/wheels/"torch-*.whl &>/dev/null 2>&1; then
        has_wheels=1
        wheel_count=$(ls "${OFFLINE_DIR}/wheels/"*.whl 2>/dev/null | wc -l)
        log_result "[OK] Wheel files found: ${wheel_count} files in offline/wheels/"
        log_debug "Wheel list:"
        ls -1 "${OFFLINE_DIR}/wheels/"*.whl 2>/dev/null | while read -r w; do
            log_debug "    - $(basename "$w")"
        done
    else
        log_warn "[INFO] No torch wheel files in offline/wheels/"
        log_warn "       Docker build will attempt network download of PyTorch"
    fi

    log_info "Checking conda package cache..."
    if [ -n "$(ls -A "${OFFLINE_DIR}/conda-pkgs/" 2>/dev/null | grep -v '^\.gitkeep$')" ]; then
        has_conda_pkgs=1
        local conda_pkg_count
        conda_pkg_count=$(ls "${OFFLINE_DIR}/conda-pkgs/"*.tar.bz2 2>/dev/null | wc -l)
        log_result "[OK] Conda packages found: ${conda_pkg_count} packages in offline/conda-pkgs/"
    else
        log_info "[INFO] No conda packages in offline/conda-pkgs/"
        log_info "       Will download from network during build (conda fallback only)"
    fi

    # Summary
    echo ""
    log_info "Offline resource summary:"
    log_info "  Miniconda : $([ -n "$local_miniconda" ] && [ -s "$local_miniconda" ] && echo 'AVAILABLE' || echo 'MISSING (will download)')"
    log_info "  Wheels    : $([ "$has_wheels" = "1" ] && echo 'AVAILABLE' || echo 'MISSING (will download)')"
    log_info "  Conda pkgs: $([ "$has_conda_pkgs" = "1" ] && echo 'AVAILABLE' || echo 'empty (will download)')"
    echo ""
fi

# =============================================================================
# Check Docker availability
# =============================================================================
log_phase "Prerequisite Checks"

log_info "Checking Docker availability..."
if ! command -v docker &>/dev/null; then
    log_error "Docker is not installed or not in PATH!"
    log_error "Please install Docker Desktop or Docker Engine first:"
    log_error "  - Docker Desktop: https://www.docker.com/products/docker-desktop/"
    log_error "  - Linux: follow https://docs.docker.com/engine/install/"
    exit 1
fi

DOCKER_VERSION=$(docker --version 2>&1)
log_result "Docker found: ${DOCKER_VERSION}"

log_info "Checking Docker daemon connectivity..."
if ! docker info &>/dev/null; then
    log_error "Cannot connect to Docker daemon!"
    log_error "Please ensure Docker is running (start Docker Desktop or docker service)"
    exit 1
fi
log_result "Docker daemon is reachable"

log_info "Checking Dockerfile exists..."
if [ ! -f "${SCRIPT_DIR}/${DOCKERFILE}" ]; then
    log_error "Dockerfile not found at: ${SCRIPT_DIR}/${DOCKERFILE}"
    exit 1
fi
log_result "Dockerfile found: ${SCRIPT_DIR}/${DOCKERFILE}"

# =============================================================================
# Enable Docker BuildKit
# =============================================================================
log_info "Enabling Docker BuildKit for faster builds with cache mounts..."
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1
log_debug "DOCKER_BUILDKIT=${DOCKER_BUILDKIT}"
log_debug "COMPOSE_DOCKER_CLI_BUILD=1"

# =============================================================================
# Build configuration summary
# =============================================================================
echo ""
echo "============================================================"
echo "  Building PyTorch Base Image (per pytorch.org)"
echo "============================================================"
echo ""
echo "  [CONFIG] Image tag      : ${IMAGE_TAG}"
echo "  [CONFIG] Base image     : ${BASE_IMAGE}"
echo "  [CONFIG] Dockerfile     : ${DOCKERFILE}"
echo "  [CONFIG] Architecture   : ${ARCH}"
echo "  [CONFIG] Python version : ${PYTHON_VERSION} (supported range: 3.10-3.14)"
echo "  [CONFIG] PyTorch        : ${PYTORCH_VERSION}"
echo "  [CONFIG] Compute        : $([ "$USE_GPU" = "1" ] && echo "CUDA ${CUDA_VERSION}" || echo "CPU only")"
echo "  [CONFIG] PyTorch index  : $( [ "$USE_GPU" = "1" ] && echo "cu${CUDA_INDEX_SUFFIX}" || echo "cpu" )"
echo "  [CONFIG] Offline mode   : $([ "$OFFLINE_MODE" = "1" ] && echo "Yes" || echo "No")"
echo "  [CONFIG] No-cache       : $([ "$NO_CACHE" = "1" ] && echo "Yes" || echo "No")"
echo "  [CONFIG] Skip verify    : $([ "$NO_VERIFY" = "1" ] && echo "Yes" || echo "No")"
echo "  [CONFIG] Quiet mode     : $([ "$QUIET" = "1" ] && echo "Yes" || echo "No")"
echo "  [CONFIG] BuildKit       : Enabled"
echo "  [CONFIG] Build context  : ${SCRIPT_DIR}"
echo "  [CONFIG] Log file       : ${LOG_FILE}"
echo ""
echo "============================================================"
echo ""

mark_action "docker build argument assembly"

# =============================================================================
# Prepare build arguments
# =============================================================================
log_info "Assembling Docker build arguments..."

BUILD_ARGS=(
    --build-arg "BASE_IMAGE=${BASE_IMAGE}"
    --build-arg "USE_GPU=${USE_GPU}"
    --build-arg "PYTHON_VERSION=${PYTHON_VERSION}"
    --build-arg "PYTORCH_VERSION=${PYTORCH_VERSION}"
    --build-arg "CUDA_VERSION=${CUDA_VERSION}"
)
log_debug "Base build args:"
log_debug "  BASE_IMAGE=${BASE_IMAGE}"
log_debug "  USE_GPU=${USE_GPU}"
log_debug "  PYTHON_VERSION=${PYTHON_VERSION}"
log_debug "  PYTORCH_VERSION=${PYTORCH_VERSION}"
log_debug "  CUDA_VERSION=${CUDA_VERSION}"

if [ "$NO_CACHE" = "1" ]; then
    log_branch "Adding --no-cache flag (incremental rebuild from scratch)"
    BUILD_ARGS+=(--no-cache)
else
    log_debug "Using cached layers (use --no-cache to disable)"
fi

if [ "$QUIET" = "1" ]; then
    log_branch "Adding QUIET=1 build arg (container will not show startup banner)"
    BUILD_ARGS+=(--build-arg "QUIET=1")
fi

log_debug "Final BUILD_ARGS: ${BUILD_ARGS[*]}"

# =============================================================================
# Build the image
# =============================================================================
log_phase "Docker Build Execution"
mark_action "executing docker build"
log_info "Executing docker build..."
log_cmd "docker build -t ${IMAGE_TAG} -f ${DOCKERFILE} [build-args] ${SCRIPT_DIR}"
echo ""

BUILD_START_TIME=$(date +%s)
log_info "Docker build started at: $(date '+%Y-%m-%d %H:%M:%S')"

docker build \
    -t "${IMAGE_TAG}" \
    -f "${DOCKERFILE}" \
    "${BUILD_ARGS[@]}" \
    "${SCRIPT_DIR}"

BUILD_END_TIME=$(date +%s)
BUILD_DURATION=$((BUILD_END_TIME - BUILD_START_TIME))
BUILD_MIN=$((BUILD_DURATION / 60))
BUILD_SEC=$((BUILD_DURATION % 60))

echo ""
log_result "Docker build completed successfully!"
log_result "Build duration: ${BUILD_MIN}m ${BUILD_SEC}s"
log_result "Image built: ${IMAGE_TAG}"

# =============================================================================
# Post-build verification (per official guide verification steps)
# =============================================================================
if [ "$NO_VERIFY" = "0" ]; then
    log_phase "Post-build Verification"
    log_info "Running official PyTorch verification tests:"
    log_info "  Test 1: Python version check"
    log_info "  Test 2: PyTorch import"
    log_info "  Test 3: PyTorch version match"
    log_info "  Test 4: torchvision import"
    log_info "  Test 5: numpy import"
    log_info "  Test 6: Tensor operation (torch.rand(5,3) per official guide)"
    log_info "  Test 7: CUDA availability check"
    log_info "  Test 8: Default user is ai (non-root)"
    log_info "  Test 9: sudo works without password"
    log_info "  Test 10: Python path points to conda env"
    log_info "  Test 11: Chinese locale is zh_CN.UTF-8"
    log_info "  Test 12: conda command available"
    log_info "  Test 13: pytorch conda env exists"
    echo ""

    VERIFY_PASS=0
    VERIFY_FAIL=0
    VERIFY_START=$(date +%s)

    run_test() {
        local desc="$1"
        local cmd="$2"
        local test_output
        local test_rc=0

        printf "  [TEST] %-50s " "$desc"
        log_debug "Running test: $desc"
        log_debug "Command: $cmd"

        set +e
        test_output=$(eval "$cmd" 2>&1)
        test_rc=$?
        set -e

        if [ $test_rc -eq 0 ]; then
            echo "PASS"
            VERIFY_PASS=$((VERIFY_PASS + 1))
            log_debug "Test PASSED: $desc"
        else
            echo "FAIL"
            VERIFY_FAIL=$((VERIFY_FAIL + 1))
            log_error "Test FAILED: $desc (exit code: ${test_rc})"
            log_error "  Command output: ${test_output}"
        fi
    }

    log_branch "Verifying Python environment..."
    run_test "Python version is ${PYTHON_VERSION}" \
        "docker run --rm ${IMAGE_TAG} python -c 'import sys; assert sys.version_info[:2] == tuple(map(int, \"${PYTHON_VERSION}\".split(\".\"))), f\"Expected Python ${PYTHON_VERSION}, got {sys.version}\"'"

    run_test "PyTorch import" \
        "docker run --rm ${IMAGE_TAG} python -c 'import torch; print(f\"PyTorch {torch.__version__}\")'"

    run_test "PyTorch version is ${PYTORCH_VERSION}" \
        "docker run --rm ${IMAGE_TAG} python -c 'import torch; assert torch.__version__.startswith(\"${PYTORCH_VERSION}\"), f\"Expected PyTorch ${PYTORCH_VERSION}, got {torch.__version__}\"'"

    run_test "torchvision import" \
        "docker run --rm ${IMAGE_TAG} python -c 'import torchvision; print(f\"torchvision {torchvision.__version__}\")'"

    run_test "numpy import" \
        "docker run --rm ${IMAGE_TAG} python -c 'import numpy; print(f\"numpy {numpy.__version__}\")'"

    log_branch "Verifying tensor operations (per official guide: x = torch.rand(5,3))..."
    run_test "Tensor operation (per official guide)" \
        "docker run --rm ${IMAGE_TAG} python -c 'import torch; x=torch.rand(5,3); print(x); assert x.shape==(5,3), f\"Expected shape (5,3), got {x.shape}\"'"

    log_branch "Verifying CUDA availability..."
    if [ "$USE_GPU" = "1" ]; then
        log_info "GPU build: checking CUDA is available (requires --gpus all)"
        run_test "CUDA availability check" \
            "docker run --rm --gpus all ${IMAGE_TAG} python -c 'import torch; assert torch.cuda.is_available(), \"CUDA not available despite GPU build\"; print(f\"CUDA devices: {torch.cuda.device_count()}\")'"
    else
        log_info "CPU build: confirming CUDA is NOT available"
        run_test "CPU only (CUDA not available)" \
            "docker run --rm ${IMAGE_TAG} python -c 'import torch; assert not torch.cuda.is_available(), \"CUDA unexpectedly available in CPU build\"'"
    fi

    log_branch "Verifying security and user configuration..."
    run_test "Default user is ai (non-root)" \
        "docker run --rm ${IMAGE_TAG} whoami | grep -q ai"

    run_test "sudo works without password" \
        "docker run --rm ${IMAGE_TAG} sudo -n whoami | grep -q root"

    log_branch "Verifying environment configuration..."
    run_test "which python points to conda env" \
        "docker run --rm ${IMAGE_TAG} which python | grep -q '/opt/conda/envs/pytorch/bin/python'"

    run_test "Chinese locale is zh_CN.UTF-8" \
        "docker run --rm ${IMAGE_TAG} locale | grep -q 'LANG=zh_CN.UTF-8'"

    run_test "conda command is available" \
        "docker run --rm ${IMAGE_TAG} conda --version"

    run_test "conda env pytorch exists" \
        "docker run --rm ${IMAGE_TAG} conda env list | grep -q pytorch"

    VERIFY_END=$(date +%s)
    VERIFY_DURATION=$((VERIFY_END - VERIFY_START))

    echo ""
    echo "  ============================================================"
    echo "  Results: ${VERIFY_PASS} passed, ${VERIFY_FAIL} failed (${VERIFY_DURATION}s)"
    echo "  ============================================================"

    if [ "$VERIFY_FAIL" -gt 0 ]; then
        log_error "${VERIFY_FAIL} verification test(s) FAILED!"
        log_error "Check the FAIL entries above for details."
        log_error "You can manually debug with: docker run -it --rm ${IMAGE_TAG} /bin/bash"
        exit 1
    fi

    log_result "All ${VERIFY_PASS} verification tests PASSED!"
else
    log_info "Verification skipped (--no-verify flag is set)"
fi

# =============================================================================
# Usage hints
# =============================================================================
echo ""
echo "============================================================"
echo "  Build Complete!"
echo "============================================================"
echo ""
echo "  Image: ${IMAGE_TAG}"
echo ""
echo "  Quick start commands:"
echo ""
echo "  # Official verification (per pytorch.org):"
echo "    docker run --rm ${IMAGE_TAG} python -c \"import torch; x = torch.rand(5, 3); print(x); print('PyTorch', torch.__version__)\""
echo ""
echo "  # Quick version check:"
echo "    docker run --rm ${IMAGE_TAG} python -c \"import torch; print(torch.__version__)\""
echo ""
echo "  # Interactive shell:"
echo "    docker run -it --rm ${IMAGE_TAG}"
echo ""
echo "  # View build metadata:"
echo "    docker run --rm ${IMAGE_TAG} cat /etc/pytorch-base-build-info"
echo ""
echo "  # Use as base image in other Dockerfiles:"
echo "    FROM ${IMAGE_TAG}"
echo ""
if [ "$USE_GPU" = "1" ]; then
echo "  # GPU run (requires nvidia-docker2 / NVIDIA Container Toolkit):"
echo "    docker run --rm --gpus all ${IMAGE_TAG} python -c \"import torch; print('CUDA available:', torch.cuda.is_available())\""
echo ""
fi

# =============================================================================
# Finalize: write success footer and handle log file
# =============================================================================
SCRIPT_END_TIME=$(date +%s)
TOTAL_DURATION=$((SCRIPT_END_TIME - SCRIPT_START_TIME))
TOTAL_MIN=$((TOTAL_DURATION / 60))
TOTAL_SEC=$((TOTAL_DURATION % 60))

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    ✅ BUILD SUCCEEDED!                       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
log_result "Total build time: ${TOTAL_MIN}m ${TOTAL_SEC}s"
log_result "Image: ${IMAGE_TAG}"

# Write success footer to log
{
    echo ""
    echo "═══════════════════════════════════════════════════════════════"
    echo "  BUILD SUCCEEDED at $(date '+%Y-%m-%d %H:%M:%S')"
    echo "  Total time : ${TOTAL_MIN}m ${TOTAL_SEC}s"
    echo "  Image      : ${IMAGE_TAG}"
    echo "  Log file   : ${LOG_FILE}"
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
} >> "$LOG_FILE" 2>/dev/null || true

# Handle --no-log-file: delete log on success (errors always keep the log)
if [ "$NO_LOG_FILE" = "1" ]; then
    log_info "Log file will be removed (--no-log-file specified)"
    rm -f "$LOG_FILE" 2>/dev/null || true
else
    log_result "Build log saved to: ${LOG_FILE}"
fi

sync 2>/dev/null || true
log_result "Build script finished successfully at $(date '+%Y-%m-%d %H:%M:%S')"
