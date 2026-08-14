#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

CONDA_BLD_DIR="$CONDA_PREFIX/conda-bld"
_PKG_PATH=$(ls -t "$CONDA_BLD_DIR"/linux-64/caffe-ffi-*.conda 2>/dev/null | head -1)
echo "Package: $_PKG_PATH"
echo ""

echo "=== Trying conda install with verbose output ==="
conda install -y -n caffe-ffi --use-local --force-reinstall "$_PKG_PATH" 2>&1
echo ""
echo "=== After install ==="
SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")
ls -la "$SP_DIR/caffe_ffi/" 2>/dev/null | head -20 || echo "  Still not found"
echo ""
conda list -n caffe-ffi caffe-ffi 2>/dev/null
