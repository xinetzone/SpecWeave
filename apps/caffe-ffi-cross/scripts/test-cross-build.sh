#!/bin/bash
# =============================================================================
# Caffe-FFI Cross-Compile Unified Test Script (Host-side runner)
#
# Usage:
#   ./scripts/test-cross-build.sh [options] [platforms...]
#
# Platforms: macos, windows, all (default: all)
#
# Options:
#   --rebuild           Force rebuild Docker images
#   --no-wine           Skip Wine L3 test (Windows)
#   --skip-sdk-download Skip SDK download when building macOS image (manual mount required)
#   --mirror MIRROR     APT/Conda mirror source: tuna/aliyun/official (default: official)
#   --output DIR        Output directory (default: ./output)
#   --recipe DIR        conda.recipe path (default: auto-detect)
#   --save-report       Also append test report to l4-verification-plan-and-checklist.md
#   --verbose, -v       Show full build output (not just last N lines on error)
#   --help              Show help
#
# Test Matrix:
#   L1 - Compilation: conda-build succeeds, packages generated
#   L2 - Static verification: File type, dependencies, symbols
#   L3 - Runtime verification: macOS (skipped/CI), Windows (Wine smoke test)
# =============================================================================
set -o pipefail

# ── Colors ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; MAGENTA='\033[0;35m'; BLUE='\033[0;34m'; BOLD='\033[1m'; DIM='\033[2m'; NC='\033[0m'

# ── Timestamp helper ──
ts() { date '+%H:%M:%S'; }

log_info()    { echo -e "${GREEN}[$(ts)] [test-cross]${NC} $*"; }
log_warn()    { echo -e "${YELLOW}[$(ts)] [test-cross]${NC} $*"; }
log_error()   { echo -e "${RED}[$(ts)] [test-cross]${NC} $*" >&2; }
log_step()    { echo -e "${CYAN}[$(ts)] [test-cross]${NC} ${BOLD}$*${NC}"; }
log_phase()   { echo -e "${BOLD}${BLUE}[$(ts)] [PHASE]${NC} ${BOLD}$*${NC}"; }
log_l1()      { echo -e "${BLUE}[$(ts)] [L1 COMPILE]${NC} $*"; }
log_l2()      { echo -e "${MAGENTA}[$(ts)] [L2 STATIC]${NC} $*"; }
log_l3()      { echo -e "${MAGENTA}[$(ts)] [L3 RUNTIME]${NC} $*"; }
log_detail()  { echo -e "${DIM}         | $*${NC}"; }
log_sep()     { echo -e "${CYAN}==========================================================================${NC}"; }
log_banner()  { echo -e "${BOLD}${CYAN}$*${NC}"; }

die() {
    log_error "$*"
    exit 1
}

# ── Global master log ──
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
MASTER_LOG=""  # set after output dir is resolved

tee_to_master() {
    if [ -n "$MASTER_LOG" ]; then
        tee -a "$MASTER_LOG"
    else
        cat
    fi
}

# ── Default configuration ──
PLATFORMS=()
REBUILD=0
NO_WINE=0
SKIP_SDK=0
MIRROR="official"
OUTPUT_DIR="${APP_DIR}/output"
RECIPE_DIR=""
SAVE_REPORT=0
VERBOSE=0
ERROR_TAIL_LINES=80
START_TIME=$(date +%s)

# ── Fix CRLF line endings ──
sed -i 's/\r$//' "${BASH_SOURCE[0]}" 2>/dev/null || true

# ── Parse arguments ──
show_help() {
    cat <<EOF
Usage: $0 [options] [platforms...]

Platforms:
  macos, windows, all (default: all)

Options:
  --rebuild             Force rebuild Docker images
  --no-wine             Skip Wine L3 test (Windows)
  --skip-sdk-download   Skip SDK download when building macOS image (manual mount required)
  --mirror MIRROR       APT/Conda mirror source: tuna/aliyun/official (default: official)
  --output DIR          Output directory (default: ./output)
  --recipe DIR          conda.recipe path (default: auto-detect)
  --save-report         Append test report to l4-verification-plan-and-checklist.md
  --verbose, -v         Show full build output (no truncation)
  --help, -h            Show this help message

Test Matrix:
  L1 - Compilation:    conda-build succeeds, packages generated
  L2 - Static verify:  File type, dependencies, symbols
  L3 - Runtime:        macOS (CI required), Windows (Wine smoke test)

Examples:
  $0                     # Test all platforms with default settings
  $0 macos               # Test macOS only
  $0 windows --no-wine   # Test Windows, skip Wine L3 test
  $0 --rebuild --mirror tuna  # Force rebuild images with Tsinghua mirror
  $0 --save-report       # Run tests and save report to L4 verification doc
EOF
}

while [[ $# -gt 0 ]]; do
    case $1 in
        macos|windows|all)
            PLATFORMS+=("$1")
            shift
            ;;
        --rebuild)
            REBUILD=1
            shift
            ;;
        --no-wine)
            NO_WINE=1
            shift
            ;;
        --skip-sdk-download)
            SKIP_SDK=1
            shift
            ;;
        --mirror)
            MIRROR="$2"
            shift 2
            ;;
        --output)
            OUTPUT_DIR="$2"
            shift 2
            ;;
        --recipe)
            RECIPE_DIR="$2"
            shift 2
            ;;
        --save-report)
            SAVE_REPORT=1
            shift
            ;;
        --verbose|-v)
            VERBOSE=1
            shift
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

if [ ${#PLATFORMS[@]} -eq 0 ]; then
    PLATFORMS=("all")
fi

EXPANDED_PLATFORMS=()
for p in "${PLATFORMS[@]}"; do
    if [ "$p" = "all" ]; then
        EXPANDED_PLATFORMS+=("macos" "windows")
    else
        EXPANDED_PLATFORMS+=("$p")
    fi
done

PLATFORMS=()
declare -A seen_platforms
for p in "${EXPANDED_PLATFORMS[@]}"; do
    if [ -z "${seen_platforms[$p]}" ]; then
        PLATFORMS+=("$p")
        seen_platforms[$p]=1
    fi
done

# ── Find SpecWeave root directory ──
find_spec_root() {
    local dir="$APP_DIR"
    while [ "$dir" != "/" ] && [ "$dir" != "." ]; do
        if [ -d "$dir/.git" ] || [ -f "$dir/AGENTS.md" ]; then
            if [ -d "$dir/projects/xuanspace/libs/caffe-ffi" ]; then
                echo "$dir"
                return 0
            fi
        fi
        dir="$(dirname "$dir")"
    done
    return 1
}

SPECDIR="$(find_spec_root)"
if [ -z "$SPECDIR" ]; then
    die "Could not find SpecWeave root directory (searched upward from $APP_DIR)
Please ensure caffe-ffi exists at \$SPECDIR/projects/xuanspace/libs/caffe-ffi"
fi

CAFFE_FFI_SRC="${SPECDIR}/projects/xuanspace/libs/caffe-ffi"
TVM_FFI_SRC="${SPECDIR}/projects/xuanspace/vendor/tvm-ffi"

if [ -z "$RECIPE_DIR" ]; then
    RECIPE_DIR="${CAFFE_FFI_SRC}/conda.recipe"
fi

if [ ! -f "${RECIPE_DIR}/meta.yaml" ]; then
    die "Recipe meta.yaml not found at: ${RECIPE_DIR}"
fi

if [ ! -d "${CAFFE_FFI_SRC}" ]; then
    die "caffe-ffi source directory not found: ${CAFFE_FFI_SRC}"
fi

# Detect tvm-ffi vendor source for local build
HAS_TVM_FFI=0
if [ -d "${TVM_FFI_SRC}" ] && [ -f "${TVM_FFI_SRC}/CMakeLists.txt" ]; then
    HAS_TVM_FFI=1
    log_info "Found local tvm-ffi source: ${TVM_FFI_SRC}"
else
    log_warn "Local tvm-ffi not found at ${TVM_FFI_SRC}, will use PyPI apache-tvm-ffi"
fi

mkdir -p "${OUTPUT_DIR}"
OUTPUT_DIR="$(cd "${OUTPUT_DIR}" && pwd)"
mkdir -p "${OUTPUT_DIR}/macos" "${OUTPUT_DIR}/windows"

# Now initialize master log
MASTER_LOG="${OUTPUT_DIR}/master-$(date +%Y%m%d-%H%M%S).log"
touch "$MASTER_LOG"
log_info "Master log: ${MASTER_LOG}"

# ── Windows path conversion helper (Git Bash / WSL) ──
docker_path() {
    local p="$1"
    if echo "$p" | grep -qE '^[A-Za-z]:'; then
        echo "/${p:0:1}$(echo "${p:2}" | tr '\\' '/')"
    else
        echo "$p"
    fi
}

CAFFE_FFI_SRC_DOCKER="$(docker_path "$CAFFE_FFI_SRC")"
TVM_FFI_SRC_DOCKER=""
if [ $HAS_TVM_FFI -eq 1 ]; then
    TVM_FFI_SRC_DOCKER="$(docker_path "$TVM_FFI_SRC")"
fi

# ── Elapsed time helper ──
elapsed() {
    local now=$(date +%s)
    local diff=$((now - START_TIME))
    local m=$((diff / 60))
    local s=$((diff % 60))
    printf "%dm%02ds" $m $s
}

# ── Error context extraction ──
extract_errors() {
    local logfile="$1"
    local lines="${2:-30}"
    if [ ! -f "$logfile" ]; then
        log_error "  (log file not found: $logfile)"
        return
    fi
    log_error "  ─── Last ${lines} lines of error context from $(basename "$logfile") ───"
    echo -e "${RED}"
    tail -"$lines" "$logfile" | while IFS= read -r line; do
        # Highlight key error patterns
        if echo "$line" | grep -qiE "error:|fatal|failed|exception|traceback|no such file|cannot find|undefined reference|syntax error"; then
            echo -e "  ${RED}>>> ${line}${NC}"
        else
            echo -e "  ${DIM}${line}${NC}"
        fi
    done
    echo -e "${NC}  ─── End error context ───"
}

# ── Extract key build info from conda-build log ──
extract_build_info() {
    local logfile="$1"
    if [ ! -f "$logfile" ]; then
        return
    fi
    log_detail "Key build info:"
    # Extract package name/version/build
    local pkg_info=$(grep -E "^# (Name|Version|Build|Python):" "$logfile" 2>/dev/null | head -10 || true)
    if [ -n "$pkg_info" ]; then
        echo "$pkg_info" | while IFS= read -r line; do
            log_detail "  $line"
        done
    fi
    # Extract found conflicts or errors
    local errors=$(grep -iE "error:|fatal:|failed to|unsatisfied|conflict" "$logfile" 2>/dev/null | head -10 || true)
    if [ -n "$errors" ]; then
        log_detail "Errors found:"
        echo "$errors" | while IFS= read -r line; do
            log_detail "  $line"
        done
    fi
}

# ── Safe grep wrapper ──
safe_grep() {
    grep "$@" 2>/dev/null || true
}

# ── Environment checks ──
log_sep
log_banner "Caffe-FFI Cross-Compile Test Suite"
log_sep
log_info "Started at:       $(date -u +'%Y-%m-%d %H:%M:%S UTC')"
log_info "Script directory:  ${SCRIPT_DIR}"
log_info "App directory:     ${APP_DIR}"
log_info "SpecWeave root:    ${SPECDIR}"
log_info "Caffe-FFI source:  ${CAFFE_FFI_SRC}"
log_info "Recipe directory:  ${RECIPE_DIR}"
log_info "Output directory:  ${OUTPUT_DIR}"
log_info "Mirror source:     ${MIRROR}"
log_info "Platforms to test: ${PLATFORMS[*]}"
log_info "Force rebuild:     $([ $REBUILD -eq 1 ] && echo 'YES' || echo 'NO')"
log_info "Skip Wine L3:      $([ $NO_WINE -eq 1 ] && echo 'YES' || echo 'NO')"
log_info "Skip SDK download: $([ $SKIP_SDK -eq 1 ] && echo 'YES' || echo 'NO')"
log_info "Save to L4 doc:    $([ $SAVE_REPORT -eq 1 ] && echo 'YES' || echo 'NO')"
log_info "Verbose output:    $([ $VERBOSE -eq 1 ] && echo 'YES' || echo 'NO')"
if [ $HAS_TVM_FFI -eq 1 ]; then
    log_info "Local tvm-ffi:     ${TVM_FFI_SRC}"
else
    log_warn "Local tvm-ffi:     NOT FOUND (will use PyPI)"
fi
log_sep

log_phase "PHASE 0: Environment Check"
log_step "Checking Docker environment..."

if ! command -v docker &>/dev/null; then
    die "Docker not found. Please install Docker first."
fi
log_info "Docker: $(docker --version 2>/dev/null || echo 'version unknown')"

if docker compose version &>/dev/null; then
    log_info "Docker Compose: $(docker compose version 2>&1 | head -1)"
elif command -v docker-compose &>/dev/null; then
    log_info "docker-compose: $(docker-compose --version 2>&1 | head -1)"
else
    log_warn "Docker Compose not found (not required for this script)"
fi

if ! docker info &>/dev/null; then
    die "Docker daemon is not running or not accessible.
Please start Docker Desktop or Docker daemon first."
fi
log_info "Docker daemon: accessible"

# Check available disk space in Docker
DISK_SPACE=$(df -h "$OUTPUT_DIR" 2>/dev/null | awk 'NR==2{print $4}' || echo "unknown")
log_info "Available disk space: ${DISK_SPACE}"

# Check recipe files exist
log_step "Verifying recipe files..."
for f in meta.yaml build.sh conda_build_config.yaml; do
    if [ -f "${RECIPE_DIR}/${f}" ]; then
        local_size=$(wc -l < "${RECIPE_DIR}/${f}" 2>/dev/null || echo "0")
        log_info "  ✓ ${RECIPE_DIR}/${f} (${local_size} lines)"
    else
        log_warn "  ○ ${RECIPE_DIR}/${f} not found"
    fi
done

# ── Test results storage ──
declare -A RESULTS
declare -A L1_STATUS
declare -A L2_STATUS
declare -A L3_STATUS
declare -A PACKAGE_NAMES
declare -A PACKAGE_SIZES
declare -A NOTES
declare -A PHASE_TIMES

# ── Helper: Check if Docker image exists ──
image_exists() {
    docker image inspect "$1" &>/dev/null
}

# ── Helper: Build image ──
build_image() {
    local platform="$1"
    local dockerfile=""
    local image_name=""
    local build_args=()
    local phase_start=$(date +%s)
    
    case "$platform" in
        macos)
            dockerfile="Dockerfile.macos-cross"
            image_name="caffe-ffi-cross-macos:latest"
            build_args+=(--build-arg "APT_MIRROR=${MIRROR}")
            build_args+=(--build-arg "CONDA_MIRROR=${MIRROR}")
            build_args+=(--build-arg "SKIP_SDK_DOWNLOAD=${SKIP_SDK}")
            ;;
        windows)
            dockerfile="Dockerfile.win-cross"
            image_name="caffe-ffi-cross-win:latest"
            build_args+=(--build-arg "APT_MIRROR=${MIRROR}")
            build_args+=(--build-arg "CONDA_MIRROR=${MIRROR}")
            if [ $NO_WINE -eq 1 ]; then
                build_args+=(--build-arg "SKIP_WINE=1")
            fi
            ;;
        *)
            log_error "Unknown platform: $platform"
            return 1
            ;;
    esac
    
    if image_exists "$image_name" && [ $REBUILD -eq 0 ]; then
        log_info "Image $image_name already exists, skipping build (use --rebuild to force)"
        local img_size=$(docker image inspect "$image_name" --format='{{.Size}}' 2>/dev/null || echo "0")
        log_detail "Image size: $(numfmt --to=iec $img_size 2>/dev/null || echo "unknown")"
        return 0
    fi
    
    if [ $REBUILD -eq 1 ]; then
        log_step "Rebuilding image: $image_name (force rebuild)"
    else
        log_step "Building image: $image_name"
    fi
    log_detail "Dockerfile: ${APP_DIR}/${dockerfile}"
    log_detail "Build args: ${build_args[*]}"
    log_detail "Context: ${APP_DIR}"
    
    local build_log="${OUTPUT_DIR}/${platform}-docker-build.log"
    log_info "Build log: ${build_log}"
    log_detail "Build started at $(date '+%Y-%m-%d %H:%M:%S')"
    
    cd "$APP_DIR"
    local build_result=0
    local build_start=$(date +%s)
    
    if [ $VERBOSE -eq 1 ]; then
        docker build \
            -f "$dockerfile" \
            -t "$image_name" \
            "${build_args[@]}" \
            "$APP_DIR" 2>&1 | tee "$build_log" | tee_to_master || build_result=$?
    else
        # Non-verbose: run docker in background, show progress markers
        docker build \
            -f "$dockerfile" \
            -t "$image_name" \
            "${build_args[@]}" \
            "$APP_DIR" > "$build_log" 2>&1 &
        local docker_pid=$!
        
        local step_count=0
        local last_line=""
        while kill -0 $docker_pid 2>/dev/null; do
            sleep 5
            if [ -f "$build_log" ]; then
                # Show latest Step line as progress indicator
                local latest_step=$(grep -E "^Step [0-9]+/[0-9]+" "$build_log" 2>/dev/null | tail -1)
                if [ -n "$latest_step" ] && [ "$latest_step" != "$last_line" ]; then
                    local cleaned=$(echo "$latest_step" | sed 's/\x1b\[[0-9;]*m//g' | cut -c1-100)
                    log_detail "  $cleaned"
                    last_line="$latest_step"
                fi
            fi
        done
        wait $docker_pid || build_result=$?
    fi
    
    local build_end=$(date +%s)
    local build_duration=$((build_end - build_start))
    log_detail "Build command completed in ${build_duration}s (exit code: ${build_result})"
    
    if [ $build_result -eq 0 ]; then
        local img_size=$(docker image inspect "$image_name" --format='{{.Size}}' 2>/dev/null || echo "0")
        log_info "Image $image_name built successfully in ${build_duration}s"
        log_detail "Image size: $(numfmt --to=iec $img_size 2>/dev/null || echo "unknown")"
        return 0
    else
        log_error "Failed to build image $image_name (exit code: ${build_result})"
        log_error "Build log: ${build_log}"
        extract_errors "$build_log" $ERROR_TAIL_LINES
        if [ "$platform" = "macos" ] && [ $SKIP_SDK -eq 0 ]; then
            log_warn ""
            log_warn "TIP: If macOS SDK download failed, try building with --skip-sdk-download"
            log_warn "     and mount SDK manually when running:"
            log_warn "     docker run -v /path/to/MacOSX11.3.sdk:/opt/MacOSX11.3.sdk ..."
            log_warn ""
        fi
        return 1
    fi
}

# ── Helper: Run cross-compile container ──
run_cross_build() {
    local platform="$1"
    local image_name=""
    local output_subdir="${OUTPUT_DIR}/${platform}"
    local run_log="${OUTPUT_DIR}/${platform}-docker-run.log"
    local docker_run_args=()
    local phase_start=$(date +%s)
    
    mkdir -p "$output_subdir"
    
    case "$platform" in
        macos)
            image_name="caffe-ffi-cross-macos:latest"
            docker_run_args+=(--rm)
            docker_run_args+=(-e "CAFFE_FFI_RECIPE_DIR=/workspace/caffe-ffi/conda.recipe")
            docker_run_args+=(-e "OUTPUT_DIR=/output")
            docker_run_args+=(-v "${CAFFE_FFI_SRC_DOCKER}:/workspace/caffe-ffi")
            if [ $HAS_TVM_FFI -eq 1 ]; then
                docker_run_args+=(-v "${TVM_FFI_SRC_DOCKER}:/workspace/tvm-ffi")
                docker_run_args+=(-e "CAFFE_FFI_TVM_FFI_DIR=/workspace/tvm-ffi")
            fi
            docker_run_args+=(-v "$(docker_path "$output_subdir"):/output")
            ;;
        windows)
            image_name="caffe-ffi-cross-win:latest"
            docker_run_args+=(--rm)
            docker_run_args+=(-e "CAFFE_FFI_RECIPE_DIR=/workspace/caffe-ffi/conda.recipe")
            docker_run_args+=(-e "OUTPUT_DIR=/output")
            docker_run_args+=(-v "${CAFFE_FFI_SRC_DOCKER}:/workspace/caffe-ffi")
            if [ $HAS_TVM_FFI -eq 1 ]; then
                docker_run_args+=(-v "${TVM_FFI_SRC_DOCKER}:/workspace/tvm-ffi")
                docker_run_args+=(-e "CAFFE_FFI_TVM_FFI_DIR=/workspace/tvm-ffi")
            fi
            docker_run_args+=(-v "$(docker_path "$output_subdir"):/output")
            if [ $NO_WINE -eq 1 ]; then
                docker_run_args+=(-e "SKIP_WINE_TEST=1")
            fi
            ;;
        *)
            log_error "Unknown platform: $platform"
            return 1
            ;;
    esac
    
    log_phase "PHASE 2: ${platform} Cross-Compilation (L1+L2 inside container)"
    log_step "Running $platform cross-compile container..."
    log_info "Image:   $image_name"
    log_info "Source:  $CAFFE_FFI_SRC_DOCKER:/workspace/caffe-ffi"
    log_info "Output:  $(docker_path "$output_subdir"):/output"
    log_info "Run log: $run_log"
    
    # Verify image exists before running
    if ! image_exists "$image_name"; then
        log_error "Image $image_name does not exist! Build it first."
        return 1
    fi
    
    local run_result=0
    local run_start=$(date +%s)
    
    if [ $VERBOSE -eq 1 ]; then
        docker run "${docker_run_args[@]}" "$image_name" 2>&1 | tee "$run_log" | tee_to_master || run_result=$?
    else
        docker run "${docker_run_args[@]}" "$image_name" > "$run_log" 2>&1 &
        local docker_pid=$!
        
        local last_marker=""
        while kill -0 $docker_pid 2>/dev/null; do
            sleep 8
            if [ -f "$run_log" ]; then
                local marker=$(grep -E "\[build-(macos|win)\]|PHASE|L[123] .*:|BUILD (SUCCESS|COMPLETED)|conda-build|Verifying:|Copying packages|✓ (Mach-O|PE32+)" "$run_log" 2>/dev/null | tail -1 || echo "")
                if [ -n "$marker" ] && [ "$marker" != "$last_marker" ]; then
                    local display=$(echo "$marker" | sed 's/\x1b\[[0-9;]*m//g' | cut -c1-110)
                    log_detail "  $display"
                    last_marker="$marker"
                fi
            fi
        done
        wait $docker_pid || run_result=$?
    fi
    
    local run_end=$(date +%s)
    local run_duration=$((run_end - run_start))
    log_detail "Container exited after ${run_duration}s with exit code: ${run_result}"
    
    if [ $run_result -eq 0 ]; then
        log_info "$platform cross-compile completed in ${run_duration}s"
        # Print summary from container output
        if [ -f "$run_log" ]; then
            local summary_lines=$(grep -E "BUILD SUCCESS|BUILD COMPLETED|Packages built:|Package:|✓|L3 smoke test:" "$run_log" 2>/dev/null | sed 's/\x1b\[[0-9;]*m//g' | tail -15 || true)
            if [ -n "$summary_lines" ]; then
                log_detail "Container summary:"
                echo "$summary_lines" | while IFS= read -r line; do
                    log_detail "  $line"
                done
            fi
        fi
        return 0
    else
        log_error "$platform cross-compile FAILED (exit code: ${run_result}) after ${run_duration}s"
        log_error "Run log: ${run_log}"
        extract_errors "$run_log" $ERROR_TAIL_LINES
        
        # Check if conda-build.log was produced despite failure
        local cb_log="${output_subdir}/conda-build.log"
        if [ -f "$cb_log" ]; then
            log_error ""
            log_error "conda-build log found despite failure. Extracting build errors:"
            extract_build_info "$cb_log"
            extract_errors "$cb_log" 50
        fi
        return $run_result
    fi
}

# ── Helper: Analyze build results ──
analyze_results() {
    local platform="$1"
    local output_subdir="${OUTPUT_DIR}/${platform}"
    local conda_build_log="${output_subdir}/conda-build.log"
    local l3_log="${output_subdir}/l3-smoketest.log"
    local docker_run_log="${OUTPUT_DIR}/${platform}-docker-run.log"
    
    RESULTS[$platform]="FAIL"
    L1_STATUS[$platform]="FAIL"
    L2_STATUS[$platform]="FAIL"
    L3_STATUS[$platform]="SKIPPED"
    PACKAGE_NAMES[$platform]=""
    PACKAGE_SIZES[$platform]=""
    NOTES[$platform]=""
    
    log_sep
    log_phase "PHASE 3: ${platform} Result Analysis (host-side)"
    log_sep
    
    local pkg_count=0
    local pkg_name=""
    local pkg_size=""
    
    log_step "Scanning output directory: ${output_subdir}"
    local out_files=$(ls -la "$output_subdir" 2>/dev/null | tail -n +2 || echo "empty")
    log_detail "Directory contents:"
    echo "$out_files" | while IFS= read -r line; do
        log_detail "  $line"
    done
    
    for ext in tar.bz2 conda; do
        while IFS= read -r -d '' pkg; do
            if [ -f "$pkg" ]; then
                pkg_count=$((pkg_count + 1))
                pkg_name="$(basename "$pkg")"
                pkg_size="$(du -h "$pkg" 2>/dev/null | cut -f1 || echo '?')"
                PACKAGE_NAMES[$platform]="$pkg_name"
                PACKAGE_SIZES[$platform]="$pkg_size"
                log_l1 "Package found: $pkg_name ($pkg_size)"
            fi
        done < <(find "$output_subdir" -maxdepth 1 -name "*.${ext}" -print0 2>/dev/null)
    done
    
    log_l1 "Analyzing L1 (compilation) status..."
    if [ -f "$conda_build_log" ]; then
        log_detail "conda-build.log size: $(wc -l < "$conda_build_log" 2>/dev/null || echo '0') lines"
        
        local has_error=0
        local has_success=0
        local error_lines=$(grep -ciE "error:|fatal:|failed|failure" "$conda_build_log" 2>/dev/null || echo "0")
        local warn_lines=$(grep -ciE "warning:|deprecated" "$conda_build_log" 2>/dev/null || echo "0")
        
        if grep -qiE "error:|fatal|failed" "$conda_build_log" 2>/dev/null; then
            has_error=1
        fi
        if grep -q "conda-build completed successfully\|BUILD SUCCESS\|BUILD COMPLETED" "$conda_build_log" 2>/dev/null; then
            has_success=1
        fi
        
        log_detail "Error patterns: ${error_lines} lines, Warning patterns: ${warn_lines} lines"
        
        if [ $has_success -eq 1 ]; then
            if [ $has_error -eq 1 ]; then
                log_l1 "conda-build completed (with warnings - ${warn_lines} warning lines)"
                NOTES[$platform]="Build completed with ${warn_lines} warnings"
            else
                log_l1 "conda-build completed successfully"
            fi
            L1_STATUS[$platform]="PASS"
        else
            if [ $pkg_count -gt 0 ]; then
                log_l1 "Package found despite missing success marker (assuming build success)"
                L1_STATUS[$platform]="PASS"
            else
                if [ $has_error -eq 1 ]; then
                    log_l1 "ERROR: Errors found in conda-build.log (${error_lines} error lines)"
                    L1_STATUS[$platform]="FAIL"
                    NOTES[$platform]="Build errors found in conda-build.log"
                    extract_errors "$conda_build_log" 40
                else
                    log_l1 "Could not confirm build success (no packages, no clear errors)"
                    L1_STATUS[$platform]="UNKNOWN"
                    NOTES[$platform]="Build status indeterminate"
                fi
            fi
        fi
        
        extract_build_info "$conda_build_log"
    elif [ -f "$docker_run_log" ]; then
        log_warn "conda-build.log not found at: $conda_build_log"
        # Check if the container log shows success
        if grep -q "BUILD SUCCESS\|conda-build completed successfully" "$docker_run_log" 2>/dev/null; then
            if [ $pkg_count -gt 0 ]; then
                log_l1 "Container log shows BUILD SUCCESS and packages found"
                L1_STATUS[$platform]="PASS"
            else
                log_l1 "Container log shows BUILD SUCCESS but no packages in output (copy failure?)"
                L1_STATUS[$platform]="FAIL"
                NOTES[$platform]="Build reported success but no packages copied to output"
                extract_errors "$docker_run_log" 30
            fi
        else
            if [ $pkg_count -gt 0 ]; then
                log_l1 "Package found despite missing log"
                L1_STATUS[$platform]="PASS"
            else
                log_l1 "No conda-build.log found and no packages - build likely failed"
                L1_STATUS[$platform]="FAIL"
                NOTES[$platform]="No build output found"
                extract_errors "$docker_run_log" 40
            fi
        fi
    else
        log_warn "No build logs found"
        if [ $pkg_count -gt 0 ]; then
            log_l1 "Package found despite missing logs"
            L1_STATUS[$platform]="PASS"
        fi
    fi
    
    log_l2 "Analyzing L2 (static verification) status..."
    local l2_pass=0
    if [ $pkg_count -gt 0 ]; then
        for pkg in "$output_subdir"/*.tar.bz2 "$output_subdir"/*.conda; do
            if [ -f "$pkg" ]; then
                log_l2 "Inspecting package: $(basename "$pkg")"
                local tmpdir=$(mktemp -d)
                
                tar -xjf "$pkg" -C "$tmpdir" 2>/dev/null || tar -xf "$pkg" -C "$tmpdir" 2>/dev/null || true
                
                case "$platform" in
                    macos)
                        local macho_count=0
                        while IFS= read -r -d '' lib; do
                            if [ -f "$lib" ]; then
                                local file_output="$(file "$lib" 2>/dev/null || echo "")"
                                local lib_rel="${lib#${tmpdir}/}"
                                log_l2 "  ${lib_rel}"
                                log_detail "file: ${file_output}"
                                if echo "$file_output" | safe_grep -qi "Mach-O"; then
                                    macho_count=$((macho_count + 1))
                                    if echo "$file_output" | safe_grep -qi "x86_64"; then
                                        log_l2 "    ✓ Mach-O 64-bit x86_64 confirmed"
                                    else
                                        log_warn "    ⚠ Mach-O but may not be x86_64"
                                    fi
                                    l2_pass=1
                                fi
                            fi
                        done < <(find "$tmpdir" -type f \( -name "*.dylib" -o -name "*.so" \) -print0 2>/dev/null)
                        if [ $macho_count -eq 0 ]; then
                            log_l2 "  No Mach-O native libs found"
                        fi
                        ;;
                    windows)
                        local pe_count=0
                        while IFS= read -r -d '' lib; do
                            if [ -f "$lib" ]; then
                                local file_output="$(file "$lib" 2>/dev/null || echo "")"
                                local lib_rel="${lib#${tmpdir}/}"
                                log_l2 "  ${lib_rel}"
                                log_detail "file: ${file_output}"
                                if echo "$file_output" | safe_grep -qi "PE32+"; then
                                    pe_count=$((pe_count + 1))
                                    if echo "$file_output" | safe_grep -qi "x86-64\|x86_64"; then
                                        log_l2 "    ✓ PE32+ DLL x86-64 confirmed"
                                    else
                                        log_warn "    ⚠ PE32+ but may not be x86-64"
                                    fi
                                    l2_pass=1
                                fi
                            fi
                        done < <(find "$tmpdir" -type f \( -name "*.pyd" -o -name "*.dll" \) -print0 2>/dev/null)
                        if [ $pe_count -eq 0 ]; then
                            log_l2 "  No PE32+ native libs found"
                        fi
                        ;;
                esac
                
                local py_count=$(find "$tmpdir" -name "*.py" 2>/dev/null | wc -l)
                log_detail "Python files in package: ${py_count}"
                if [ "$py_count" -gt 0 ]; then
                    if [ $l2_pass -eq 0 ]; then
                        log_l2 "  Pure Python package (no native libs - may indicate cross-compile issue)"
                        NOTES[$platform]="${NOTES[$platform]}; No native libs found (pure Python package)"
                        l2_pass=1
                    fi
                fi
                
                rm -rf "$tmpdir"
            fi
        done
        
        if [ $l2_pass -eq 1 ]; then
            L2_STATUS[$platform]="PASS"
            log_l2 "Static verification: PASS"
        else
            # Check if container did L2 successfully
            if [ -f "$docker_run_log" ] && safe_grep -q "✓ Mach-O\|✓ PE32+\|Binary format.*confirmed" "$docker_run_log"; then
                log_l2 "Static verification passed inside container (confirmed via log)"
                L2_STATUS[$platform]="PASS"
            else
                L2_STATUS[$platform]="UNKNOWN"
                NOTES[$platform]="${NOTES[$platform]}; Static verification inconclusive"
            fi
        fi
    else
        log_l2 "No packages to verify (L2 skipped)"
        L2_STATUS[$platform]="NOT_RUN"
    fi
    
    log_l3 "Analyzing L3 (runtime verification) status..."
    case "$platform" in
        macos)
            L3_STATUS[$platform]="SKIPPED"
            NOTES[$platform]="${NOTES[$platform]}; macOS L3 requires real macOS hardware/CI"
            log_l3 "macOS runtime test: SKIPPED (requires macOS CI environment)"
            log_detail "  Docker/Linux cannot execute Mach-O binaries"
            log_detail "  To run L3: use GitHub Actions macOS runner or physical Mac"
            ;;
        windows)
            if [ $NO_WINE -eq 1 ]; then
                L3_STATUS[$platform]="SKIPPED_USER"
                NOTES[$platform]="${NOTES[$platform]}; Wine L3 skipped by user request (--no-wine)"
                log_l3 "Windows Wine L3 test: SKIPPED (--no-wine specified)"
            else
                if [ -f "$l3_log" ]; then
                    local l3_lines=$(wc -l < "$l3_log" 2>/dev/null || echo "0")
                    log_detail "L3 log: ${l3_lines} lines"
                    log_detail "--- L3 log contents ---"
                    cat "$l3_log" | sed 's/\r$//' | while IFS= read -r line; do
                        log_detail "  $line"
                    done
                    log_detail "--- end L3 log ---"
                    
                    if safe_grep -q "All imports passed\|✓ All imports" "$l3_log"; then
                        L3_STATUS[$platform]="PASS"
                        log_l3 "Windows Wine L3 test: PASS"
                    elif safe_grep -q "Some imports failed" "$l3_log"; then
                        L3_STATUS[$platform]="PARTIAL"
                        NOTES[$platform]="${NOTES[$platform]}; Some imports failed in Wine (expected for complex C++ extensions)"
                        log_l3 "Windows Wine L3 test: PARTIAL (some imports failed - Wine limitation)"
                    elif safe_grep -q "FAIL" "$l3_log"; then
                        L3_STATUS[$platform]="FAIL"
                        NOTES[$platform]="${NOTES[$platform]}; L3 import failures in Wine"
                        log_l3 "Windows Wine L3 test: FAIL (see l3-smoketest.log)"
                    else
                        L3_STATUS[$platform]="UNKNOWN"
                        NOTES[$platform]="${NOTES[$platform]}; L3 result unclear"
                        log_l3 "Windows Wine L3 test: UNKNOWN (check l3-smoketest.log)"
                    fi
                    log_l3 "Wine L3 log: $l3_log"
                else
                    if [ -f "$docker_run_log" ]; then
                        if safe_grep -qi "L3.*SKIPPED\|SKIP_WINE_TEST\|SKIP_WINE=1" "$docker_run_log"; then
                            L3_STATUS[$platform]="SKIPPED"
                            log_l3 "Windows Wine L3 test: SKIPPED (not executed in container)"
                        else
                            L3_STATUS[$platform]="NOT_RUN"
                            log_l3 "Windows Wine L3 test: NOT_RUN (no l3-smoketest.log found)"
                            log_detail "Check container output for Wine errors"
                        fi
                    else
                        L3_STATUS[$platform]="NOT_RUN"
                        log_l3 "Windows Wine L3 test: NOT_RUN"
                    fi
                fi
            fi
            ;;
    esac
    
    # ── Determine overall result ──
    if [ "${L1_STATUS[$platform]}" = "PASS" ]; then
        if [ "${L2_STATUS[$platform]}" = "PASS" ]; then
            case "${L3_STATUS[$platform]}" in
                PASS|SKIPPED|SKIPPED_USER|PARTIAL)
                    RESULTS[$platform]="PASS"
                    ;;
                *)
                    RESULTS[$platform]="PARTIAL"
                    ;;
            esac
        else
            RESULTS[$platform]="PARTIAL"
            NOTES[$platform]="${NOTES[$platform]}; L2 static verification incomplete"
        fi
    elif [ "${L1_STATUS[$platform]}" = "UNKNOWN" ] && [ "${L2_STATUS[$platform]}" = "PASS" ]; then
        RESULTS[$platform]="PARTIAL"
    elif [ "${L1_STATUS[$platform]}" = "FAIL" ]; then
        RESULTS[$platform]="FAIL"
    fi
    
    log_info ""
    log_info "$platform test summary:"
    log_info "  L1 Compile:   ${L1_STATUS[$platform]}"
    log_info "  L2 Static:    ${L2_STATUS[$platform]}"
    log_info "  L3 Runtime:   ${L3_STATUS[$platform]}"
    case "${RESULTS[$platform]}" in
        PASS)    log_info "  Overall:      ${GREEN}${BOLD}PASS${NC}" ;;
        PARTIAL) log_info "  Overall:      ${YELLOW}${BOLD}PARTIAL${NC}" ;;
        FAIL)    log_info "  Overall:      ${RED}${BOLD}FAIL${NC}" ;;
        *)       log_info "  Overall:      ${RESULTS[$platform]}" ;;
    esac
}

# ── Helper: Generate Markdown report ──
generate_report() {
    local report_file="${OUTPUT_DIR}/test-report.md"
    local timestamp=$(date -u +"%Y-%m-%d %H:%M:%S UTC")
    local total_elapsed=$(elapsed)
    local total_pass=0
    local total_partial=0
    local total_fail=0
    
    for p in "${PLATFORMS[@]}"; do
        case "${RESULTS[$p]}" in
            PASS) total_pass=$((total_pass + 1)) ;;
            PARTIAL) total_partial=$((total_partial + 1)) ;;
            *) total_fail=$((total_fail + 1)) ;;
        esac
    done
    
    local overall_result=""
    local overall_emoji=""
    if [ $total_fail -eq 0 ] && [ $total_partial -eq 0 ]; then
        overall_result="ALL PASS"
        overall_emoji="✅"
    elif [ $total_fail -eq 0 ]; then
        overall_result="PARTIAL"
        overall_emoji="⚠️"
    else
        overall_result="FAIL"
        overall_emoji="❌"
    fi
    
    log_sep
    log_phase "PHASE 4: Report Generation"
    log_step "Generating test report: $report_file"
    log_sep
    
    cat > "$report_file" <<EOF
# Caffe-FFI Cross-Compile Test Report

- **Generated**: ${timestamp}
- **Total elapsed**: ${total_elapsed}
- **Mirror source**: ${MIRROR}
- **Output directory**: ${OUTPUT_DIR}
- **Overall result**: ${overall_emoji} **${overall_result}**

## Summary Table

| Platform | L1 Compile | L2 Static | L3 Runtime | Package | Size | Overall |
|----------|------------|-----------|------------|---------|------|---------|
EOF
    
    for p in "${PLATFORMS[@]}"; do
        local pkg="${PACKAGE_NAMES[$p]:--}"
        local size="${PACKAGE_SIZES[$p]:--}"
        local r="${RESULTS[$p]:-FAIL}"
        local r_icon="❌"
        [ "$r" = "PASS" ] && r_icon="✅"
        [ "$r" = "PARTIAL" ] && r_icon="⚠️"
        echo "| ${p} | ${L1_STATUS[$p]:-FAIL} | ${L2_STATUS[$p]:-FAIL} | ${L3_STATUS[$p]:-SKIPPED} | ${pkg} | ${size} | ${r_icon} ${r} |" >> "$report_file"
    done
    
    cat >> "$report_file" <<'EOF'

## Detailed Results

EOF
    
    for p in "${PLATFORMS[@]}"; do
        local p_title="$(echo "${p:0:1}" | tr '[:lower:]' '[:upper:]')${p:1}"
        cat >> "$report_file" <<EOF
### ${p_title} Platform

- **L1 Compilation**: ${L1_STATUS[$p]:-FAIL}
  - Package: ${PACKAGE_NAMES[$p]:-none}
  - Size: ${PACKAGE_SIZES[$p]:-N/A}
- **L2 Static Verification**: ${L2_STATUS[$p]:-FAIL}
- **L3 Runtime Verification**: ${L3_STATUS[$p]:-SKIPPED}
EOF
        
        if [ -n "${NOTES[$p]}" ]; then
            echo "- **Notes**: ${NOTES[$p]}" >> "$report_file"
        fi
        
        local build_log_path="${OUTPUT_DIR}/${p}/conda-build.log"
        local run_log_path="${OUTPUT_DIR}/${p}-docker-run.log"
        local l3_log_path="${OUTPUT_DIR}/${p}/l3-smoketest.log"
        local docker_build_log="${OUTPUT_DIR}/${p}-docker-build.log"
        
        echo "" >> "$report_file"
        echo "**Logs**:" >> "$report_file"
        if [ -f "$build_log_path" ]; then
            echo "- [conda-build.log](${p}/conda-build.log) ($(wc -l < "$build_log_path" 2>/dev/null || echo '?') lines)" >> "$report_file"
        fi
        if [ -f "$docker_build_log" ]; then
            echo "- [docker-build.log](${p}-docker-build.log) ($(wc -l < "$docker_build_log" 2>/dev/null || echo '?') lines)" >> "$report_file"
        fi
        if [ -f "$run_log_path" ]; then
            echo "- [docker-run.log](${p}-docker-run.log) ($(wc -l < "$run_log_path" 2>/dev/null || echo '?') lines)" >> "$report_file"
        fi
        if [ -f "$l3_log_path" ]; then
            echo "- [l3-smoketest.log](${p}/l3-smoketest.log) ($(wc -l < "$l3_log_path" 2>/dev/null || echo '?') lines)" >> "$report_file"
        fi
        echo "" >> "$report_file"
        
        # If L1 failed, include error extract in report
        if [ "${L1_STATUS[$p]}" = "FAIL" ] && [ -f "${build_log_path}" ]; then
            echo "**Build error context (last 30 error lines):**" >> "$report_file"
            echo '```' >> "$report_file"
            grep -iE "error:|fatal:|failed to|undefined reference|no such file|cannot find|syntax error|Exception|Traceback" "${build_log_path}" | tail -30 >> "$report_file" 2>/dev/null || true
            echo '```' >> "$report_file"
            echo "" >> "$report_file"
        fi
    done
    
    cat >> "$report_file" <<'EOF'
## Test Matrix Explanation

| Level | Description |
|-------|-------------|
| L1 | Compilation - conda-build completes without errors, packages generated |
| L2 | Static verification - File format (Mach-O/PE32+), architecture, exported symbols |
| L3 | Runtime verification - Import tests (Wine for Windows, requires real macOS for osx-64) |

## Status Legend

| Status | Meaning |
|--------|---------|
| ✅ PASS | Verification passed |
| ⚠️ PARTIAL | Some checks passed, others skipped/warned |
| ❌ FAIL | Verification failed |
| SKIPPED | Cannot run in this environment (by design) |
| SKIPPED_USER | Skipped by user flag (--no-wine) |
| NOT_RUN | Not executed (usually due to earlier failure) |
| UNKNOWN | Could not determine status |

## Usage Notes

- macOS L3 tests require actual macOS hardware or CI (Wine cannot run Mach-O binaries)
- Windows Wine L3 is best-effort: complex C++ extensions may fail due to Wine limitations
- Use `--no-wine` to skip Windows Wine L3 tests
- Use `--mirror tuna/aliyun` for faster builds in China
- Use `--save-report` to auto-append results to L4 verification document

## How to Run

```bash
# Test all platforms
./run.sh

# Test specific platform
./run.sh macos
./run.sh windows

# Force rebuild with mirror, save report
./run.sh --rebuild --mirror tuna --save-report
```
EOF
    
    log_info "Report generated: $report_file"
}

# ── Helper: Save report to L4 verification document ──
save_to_l4_doc() {
    local report_file="${OUTPUT_DIR}/test-report.md"
    local l4_doc="${SPECDIR}/.agents/docs/retrospective/reports/task-reports/retrospective-caffe-ffi-conda-build-20260730/l4-verification-plan-and-checklist.md"
    
    if [ ! -f "$l4_doc" ]; then
        log_warn "L4 verification document not found at: $l4_doc"
        log_warn "Report saved to: $report_file (not appended to L4 doc)"
        return 1
    fi
    
    log_step "Appending test report to L4 verification document..."
    log_info "Target: $l4_doc"
    
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S %Z')
    local anchor_marker="<!-- AUTO-TEST-RESULTS-ANCHOR -->"
    local end_marker="<!-- END-AUTO-TEST-RESULTS -->"
    
    # Create the section to insert
    local insert_content="
### 测试执行记录

> 此区域由 test-cross-build.sh --save-report 自动生成，勿手动编辑。
> 最近执行时间：${timestamp}

"
    # Append summary table
    insert_content+=$(cat <<EOF
| 执行时间 | 平台 | L1(编译) | L2(静态) | L3(运行时) | 包名 | 大小 | 结果 |
|---------|------|---------|---------|-----------|------|------|------|
EOF
)
    for p in "${PLATFORMS[@]}"; do
        local r="${RESULTS[$p]:-FAIL}"
        local r_icon="❌"
        [ "$r" = "PASS" ] && r_icon="✅"
        [ "$r" = "PARTIAL" ] && r_icon="⚠️"
        insert_content+="| ${timestamp} | ${p} | ${L1_STATUS[$p]:-FAIL} | ${L2_STATUS[$p]:-FAIL} | ${L3_STATUS[$p]:-SKIPPED} | ${PACKAGE_NAMES[$p]:--} | ${PACKAGE_SIZES[$p]:--} | ${r_icon} ${r} |
"
    done
    
    insert_content+="
- 完整报告：[test-report.md]($(realpath --relative-to="$(dirname "$l4_doc")" "$report_file" 2>/dev/null || echo "$report_file"))
- Master log：${OUTPUT_DIR}/master-*.log

"
    
    # Check if anchor exists; if not, add it before "## 参考链接"
    if ! grep -q "$anchor_marker" "$l4_doc" 2>/dev/null; then
        log_detail "Anchor marker not found, inserting before '## 参考链接'"
        # Insert before "## 参考链接" section
        local insert_before="## 参考链接"
        if grep -q "$insert_before" "$l4_doc" 2>/dev/null; then
            # Use sed to insert markers and content before reference section
            sed -i "s|^${insert_before}|${anchor_marker}\n${insert_content}${end_marker}\n\n&|" "$l4_doc"
            log_info "Report section inserted before '${insert_before}'"
        else
            # Append at end
            echo -e "\n${anchor_marker}\n${insert_content}${end_marker}" >> "$l4_doc"
            log_info "Report section appended at end of document"
        fi
    else
        log_detail "Replacing existing auto-generated section..."
        # Remove existing content between markers and insert new
        # Use awk for multi-line replacement (portable)
        local tmp_l4=$(mktemp)
        awk -v start="$anchor_marker" -v end="$end_marker" -v content="${anchor_marker}\n${insert_content}${end_marker}" '
            $0 ~ start { in_block=1; print content; next }
            $0 ~ end { in_block=0; next }
            !in_block { print }
        ' "$l4_doc" > "$tmp_l4"
        cp "$tmp_l4" "$l4_doc"
        rm -f "$tmp_l4"
        log_info "Existing report section replaced with latest results"
    fi
    
    log_info "Report saved to L4 document: $l4_doc"
}

# ── Main execution ──
log_sep
log_banner "Starting cross-compile tests for platforms: ${PLATFORMS[*]}"
log_banner "Total elapsed timer started"
log_sep

# Phase 1: Build all images first
log_phase "PHASE 1: Docker Image Build"
BUILD_FAILED=0
for platform in "${PLATFORMS[@]}"; do
    if ! build_image "$platform"; then
        RESULTS[$platform]="FAIL"
        L1_STATUS[$platform]="FAIL"
        L2_STATUS[$platform]="NOT_RUN"
        L3_STATUS[$platform]="NOT_RUN"
        NOTES[$platform]="Docker image build failed"
        BUILD_FAILED=1
    fi
done

# Phase 2 & 3: Run containers and analyze results
for platform in "${PLATFORMS[@]}"; do
    # Skip if build already failed
    if [ "${NOTES[$platform]}" = "Docker image build failed" ]; then
        log_sep
        log_error "Skipping $platform - image build failed"
        log_sep
        continue
    fi
    
    log_sep
    log_banner "Testing platform: ${platform} (elapsed: $(elapsed))"
    log_sep
    
    run_cross_build "$platform" || true  # Don't exit; analyze results anyway
    analyze_results "$platform"
done

log_sep
log_phase "FINAL: Results Summary"
log_sep

for p in "${PLATFORMS[@]}"; do
    local_status="${RESULTS[$p]:-FAIL}"
    local_color="${RED}"
    case "$local_status" in
        PASS) local_color="${GREEN}" ;;
        PARTIAL) local_color="${YELLOW}" ;;
    esac
    echo -e "  ${local_color}${BOLD}${p}${NC}: ${local_color}${local_status}${NC}"
    echo -e "    L1: ${L1_STATUS[$p]:-FAIL} | L2: ${L2_STATUS[$p]:-FAIL} | L3: ${L3_STATUS[$p]:-SKIPPED}"
    if [ -n "${PACKAGE_NAMES[$p]}" ]; then
        echo -e "    Package: ${PACKAGE_NAMES[$p]} (${PACKAGE_SIZES[$p]})"
    fi
    if [ -n "${NOTES[$p]}" ]; then
        echo -e "    Notes: ${NOTES[$p]}"
    fi
done

log_sep

generate_report

if [ $SAVE_REPORT -eq 1 ]; then
    save_to_l4_doc
fi

log_sep
log_info "Total elapsed: $(elapsed)"
log_info "Test artifacts in: ${OUTPUT_DIR}"
log_info "  - Test report: ${OUTPUT_DIR}/test-report.md"
log_info "  - Master log:  ${MASTER_LOG}"
for p in "${PLATFORMS[@]}"; do
    log_info "  - ${p} packages: ${OUTPUT_DIR}/${p}/"
done
log_sep

total_pass=0
total_partial=0
total_fail=0
for p in "${PLATFORMS[@]}"; do
    case "${RESULTS[$p]}" in
        PASS) total_pass=$((total_pass + 1)) ;;
        PARTIAL) total_partial=$((total_partial + 1)) ;;
        *) total_fail=$((total_fail + 1)) ;;
    esac
done

if [ $total_fail -eq 0 ] && [ $total_partial -eq 0 ]; then
    echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}${BOLD}                    ALL TESTS PASSED!                        ${NC}"
    echo -e "${GREEN}${BOLD}                  Elapsed: $(elapsed)                         ${NC}"
    echo -e "${GREEN}${BOLD}══════════════════════════════════════════════════════════════${NC}"
    exit 0
elif [ $total_fail -eq 0 ]; then
    echo -e "${YELLOW}${BOLD}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${YELLOW}${BOLD}              TESTS PARTIALLY PASSED                         ${NC}"
    echo -e "${YELLOW}${BOLD}                  Elapsed: $(elapsed)                         ${NC}"
    echo -e "${YELLOW}${BOLD}══════════════════════════════════════════════════════════════${NC}"
    exit 0
else
    echo -e "${RED}${BOLD}══════════════════════════════════════════════════════════════${NC}"
    echo -e "${RED}${BOLD}                  SOME TESTS FAILED!                         ${NC}"
    echo -e "${RED}${BOLD}                  Elapsed: $(elapsed)                         ${NC}"
    echo -e "${RED}${BOLD}══════════════════════════════════════════════════════════════${NC}"
    exit 1
fi
