#!/bin/bash
# =============================================================================
# Build script for caffe-ffi-cross-macos Docker image
# Usage: ./build.sh [--mirror tuna|aliyun|official] [--skip-sdk]
# =============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

MIRROR="official"
SKIP_SDK=0
IMAGE_NAME="caffe-ffi-cross-macos:latest"

while [[ $# -gt 0 ]]; do
    case $1 in
        --mirror)
            MIRROR="$2"
            shift 2
            ;;
        --skip-sdk)
            SKIP_SDK=1
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [--mirror tuna|aliyun|official] [--skip-sdk]"
            echo ""
            echo "Options:"
            echo "  --mirror    Set mirror source (default: official)"
            echo "  --skip-sdk  Skip macOS SDK download (mount manually at runtime)"
            echo "  --help      Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "Building caffe-ffi-cross-macos Docker image"
echo "============================================================"
echo "Mirror:     $MIRROR"
echo "Skip SDK:   $SKIP_SDK"
echo "Image name: $IMAGE_NAME"
echo "Context:    $SCRIPT_DIR"
echo "============================================================"

BUILD_ARGS=(
    --build-arg "APT_MIRROR=$MIRROR"
    --build-arg "CONDA_MIRROR=$MIRROR"
    --build-arg "SKIP_SDK_DOWNLOAD=$SKIP_SDK"
)

docker build \
    -f Dockerfile.macos-cross \
    -t "$IMAGE_NAME" \
    "${BUILD_ARGS[@]}" \
    "$SCRIPT_DIR"

echo ""
echo "============================================================"
echo "Build complete: $IMAGE_NAME"
echo "============================================================"
echo ""
echo "To run the build (mount caffe-ffi source and output dir):"
echo "  docker run --rm \\"
echo "    -v /path/to/caffe-ffi:/workspace/caffe-ffi \\"
echo "    -v \$(pwd)/output:/output \\"
echo "    $IMAGE_NAME"
echo ""
if [ $SKIP_SDK -eq 1 ]; then
    echo "NOTE: SKIP_SDK_DOWNLOAD=1 - mount SDK when running:"
    echo "  docker run --rm \\"
    echo "    -v /path/to/MacOSX11.3.sdk:/opt/MacOSX11.3.sdk \\"
    echo "    -v /path/to/caffe-ffi:/workspace/caffe-ffi \\"
    echo "    -v \$(pwd)/output:/output \\"
    echo "    $IMAGE_NAME"
fi
