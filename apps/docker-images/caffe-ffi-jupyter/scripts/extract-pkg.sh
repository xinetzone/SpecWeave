#!/bin/bash
set -e
CONDA_BLD="/opt/conda/envs/caffe-ffi/conda-bld/linux-64"
_PKG=$(ls -t "$CONDA_BLD"/caffe-ffi-*.conda 2>/dev/null | head -1)
echo "Package: $_PKG"
echo ""

mkdir -p /tmp/pkg-inspect
cd /tmp/pkg-inspect
rm -rf *

# .conda format: zip containing metadata.tar.zst and pkg.tar.zst
echo "=== Extracting .conda (zip) ==="
unzip -o "$_PKG"
echo ""
echo "=== Files in zip ==="
ls -la
echo ""

echo "=== Extracting pkg.tar.zst ==="
tar --zstd -xf pkg-*.tar.zst
echo ""

echo "=== Full package tree ==="
find . -type f | sort
echo ""

echo "=== caffe_ffi directory contents ==="
find . -path '*/caffe_ffi/*' -type f | sort
echo ""

echo "=== Checking for missing files ==="
echo "Expected files (from source):"
for f in __init__.py _core.py _ffi_api.py blob.py io.py layer.py net.py caffe_pb2.py; do
    found=$(find . -name "$f" -path '*/caffe_ffi/*' 2>/dev/null | head -1)
    if [ -n "$found" ]; then
        echo "  [OK] $f -> $found"
    else
        echo "  [MISSING] $f"
    fi
done
echo ""
echo "Checking for caffe/ subdirectory:"
find . -path '*/caffe_ffi/caffe/*' -type f | sort || echo "  [MISSING] caffe/ subdir"
echo ""
echo "Checking for tools/ subdirectory:"
find . -path '*/caffe_ffi/tools/*' -type f | sort || echo "  [MISSING] tools/ subdir"
echo ""
echo "Checking for _caffe_ffi.so:"
find . -name '_caffe_ffi*.so' -type f
