#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:/opt/conda/bin:$PATH"

SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")

echo "=== After conda install, checking site-packages ==="
echo "SP_DIR: $SP_DIR"
echo ""

echo "=== caffe_ffi directory ==="
ls -la "$SP_DIR/caffe_ffi/" 2>/dev/null || echo "  caffe_ffi/ NOT FOUND in site-packages"
echo ""

echo "=== caffe_ffi dist-info ==="
ls -la "$SP_DIR"/caffe_ffi-*.dist-info/ 2>/dev/null || echo "  dist-info NOT FOUND"
echo ""

echo "=== conda list caffe-ffi ==="
conda list -n caffe-ffi caffe-ffi 2>/dev/null
echo ""

echo "=== pip show caffe-ffi ==="
pip show caffe-ffi 2>/dev/null || echo "  Not in pip"
echo ""

echo "=== Check if conda actually installed files ==="
find "$CONDA_PREFIX" -name "caffe_ffi" -type d 2>/dev/null
echo ""

echo "=== Python sys.path ==="
python -c "import sys; print('\n'.join(sys.path))"
echo ""

echo "=== Try direct import with full path check ==="
python -c "
import sys, os
sp = None
for p in sys.path:
    if 'site-packages' in p:
        sp = p
        break
if sp:
    print('site-packages:', sp)
    print('contents:', os.listdir(sp)[:30])
else:
    print('No site-packages in sys.path')
"
