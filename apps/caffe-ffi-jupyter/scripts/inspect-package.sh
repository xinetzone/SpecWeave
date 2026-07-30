#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")

echo "=== Step 1: Clean editable residuals manually ==="
echo "Before cleanup:"
ls -la "$SP_DIR"/_editable_*.pth 2>/dev/null || echo "  (none)"
for pth in "$SP_DIR"/_editable_skbc_*.pth; do
    if [ -f "$pth" ]; then
        base=$(basename "$pth" .pth)
        rm -f "$SP_DIR/${base}.py" 2>/dev/null
        rm -f "$pth"
        echo "  Removed: $pth and ${base}.py"
    fi
done
echo "After cleanup:"
ls -la "$SP_DIR"/_editable_*.pth 2>/dev/null || echo "  (none - clean)"
echo ""

echo "=== Step 2: Find and list the built conda package ==="
CONDA_BLD="/opt/conda/envs/caffe-ffi/conda-bld/linux-64"
ls -la "$CONDA_BLD"/caffe-ffi-*.conda 2>/dev/null || echo "  No .conda package found"
ls -la "$CONDA_BLD"/caffe-ffi-*.tar.bz2 2>/dev/null || echo "  No .tar.bz2 package found"
echo ""

echo "=== Step 3: Extract and inspect conda package contents ==="
_PKG=$(ls -t "$CONDA_BLD"/caffe-ffi-*.conda 2>/dev/null | head -1)
if [ -n "$_PKG" ]; then
    echo "Package: $_PKG"
    echo "Package size: $(du -h "$_PKG" | cut -f1)"
    echo ""
    echo "Contents (Python files and .so):"
    # .conda is a zip file containing pkg-meta.tar and pkg.tar.zst
    mkdir -p /tmp/conda-inspect
    cd /tmp/conda-inspect
    # Extract the pkg-*.tar.zst from the zip
    unzip -o "$_PKG" -d /tmp/conda-inspect/ 2>/dev/null
    # Find and extract the actual package tarball
    PKG_TAR=$(ls /tmp/conda-inspect/pkg-*.tar.zst 2>/dev/null | head -1)
    if [ -n "$PKG_TAR" ]; then
        tar --zstd -tf "$PKG_TAR" | grep -E '\.(py|so)$|caffe_ffi/' | sort
    else
        echo "  Could not find pkg tarball, listing all files:"
        tar tf /tmp/conda-inspect/*.tar* 2>/dev/null | grep -E '\.(py|so)$|caffe_ffi/' | sort
    fi
    cd /
    rm -rf /tmp/conda-inspect
fi
echo ""

echo "=== Step 4: Check pip editable install and uninstall ==="
pip uninstall -y caffe-ffi apache-tvm-ffi 2>/dev/null || true
echo "pip list after uninstall:"
pip list 2>/dev/null | grep -i caffe || echo "  (caffe-ffi not in pip list)"
echo ""

echo "=== Step 5: List all files in site-packages/caffe_ffi/ ==="
echo "Files currently in $SP_DIR/caffe_ffi/:"
find "$SP_DIR/caffe_ffi/" -type f 2>/dev/null | sort
echo ""

echo "=== Step 6: List source python/caffe_ffi/ for comparison ==="
SRC_PY="/SpecWeave/projects/xuanspace/libs/caffe-ffi/python/caffe_ffi"
echo "Source files in $SRC_PY:"
find "$SRC_PY" -type f -not -name '*.pyc' -not -path '*__pycache__*' -not -name '*.modified' 2>/dev/null | sort
