#!/bin/bash
# DevContainer Win11 - Build Script (bash for WSL/Git Bash)
# Usage: bash scripts/build.sh [--cn] [--tag <tag>] [--no-cache] [--fast]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

TAG="devcontainer-win11:latest"
CN_MIRRORS=""
NO_CACHE=""
VERIFY_MODE="standard"
PYTHON_VERSION="3.14"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --cn|-cn) CN_MIRRORS="--cn"; shift ;;
        --tag|-t) TAG="$2"; shift 2 ;;
        --no-cache) NO_CACHE="--no-cache"; shift ;;
        --fast) VERIFY_MODE="fast"; shift ;;
        --python) PYTHON_VERSION="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --cn              Use China mirrors (tuna for conda, aliyun for pip)"
            echo "  --tag, -t TAG     Image tag (default: devcontainer-win11:latest)"
            echo "  --no-cache        Build without cache"
            echo "  --fast            Fast verification mode (essential checks only)"
            echo "  --python VER      Python version (default: 3.14 free-threading)"
            echo "  --help, -h        Show this help"
            exit 0
            ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo ""
echo "============================================================"
echo "  DevContainer Win11 - Build Script (bash/WSL)"
echo "  Project root: $PROJECT_ROOT"
echo "  Tag: $TAG"
echo "  CN mirrors: ${CN_MIRRORS:+yes}"
echo "  Verify mode: $VERIFY_MODE"
echo "  Python: $PYTHON_VERSION (free-threading cp314t)"
echo "============================================================"
echo ""

# Check if powershell.exe is available (for Windows hosts)
if command -v powershell.exe &>/dev/null; then
    echo "[INFO] Detected Windows environment, using PowerShell build script..."
    cd "$PROJECT_ROOT"
    exec powershell.exe -ExecutionPolicy Bypass -File "./scripts/build.ps1" `
        -Tag "$TAG" `
        $CN_MIRRORS `
        $NO_CACHE `
        -VerifyMode "$VERIFY_MODE" `
        -PythonVersion "$PYTHON_VERSION"
elif command -v pwsh &>/dev/null; then
    echo "[INFO] Detected PowerShell Core, using pwsh..."
    cd "$PROJECT_ROOT"
    exec pwsh -ExecutionPolicy Bypass -File "./scripts/build.ps1" `
        -Tag "$TAG" `
        $CN_MIRRORS `
        $NO_CACHE `
        -VerifyMode "$VERIFY_MODE" `
        -PythonVersion "$PYTHON_VERSION"
else
    echo "[INFO] No PowerShell detected, running docker build directly..."

    BUILD_ARGS=(build -t "$TAG")

    if [[ -n "$CN_MIRRORS" ]]; then
        BUILD_ARGS+=(--build-arg CONDA_MIRROR=tuna --build-arg PIP_MIRROR=aliyun)
        echo "[INFO] Using China mirrors: conda=tuna, pip=aliyun"
    fi

    if [[ -n "$NO_CACHE" ]]; then
        BUILD_ARGS+=(--no-cache)
    fi

    BUILD_ARGS+=(--build-arg "PYTHON_VERSION=$PYTHON_VERSION")
    BUILD_ARGS+=(--build-arg "BUILD_VERIFY_MODE=$VERIFY_MODE")
    BUILD_ARGS+=("$PROJECT_ROOT")

    BUILD_START=$(date +%s)
    docker "${BUILD_ARGS[@]}"
    BUILD_END=$(date +%s)
    DURATION=$((BUILD_END - BUILD_START))

    echo ""
    echo "============================================================"
    echo "  Build completed in $((DURATION/60))m $((DURATION%60))s"
    echo "  To start: powershell.exe -File scripts/start.ps1"
    echo "============================================================"
fi
