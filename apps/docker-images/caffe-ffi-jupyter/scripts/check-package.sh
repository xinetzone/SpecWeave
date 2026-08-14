#!/bin/bash
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

echo "=== Python site-packages location ==="
python -c "import site; print(site.getsitepackages()[0])"
SP_DIR=$(python -c "import site; print(site.getsitepackages()[0])")
echo ""

echo "=== caffe_ffi package directory listing ==="
ls -la "$SP_DIR/caffe_ffi/" 2>/dev/null || echo "caffe_ffi not found in site-packages"
echo ""

echo "=== Check for _editable_*.pth files ==="
ls -la "$SP_DIR"/_editable_*.pth 2>/dev/null || echo "No editable .pth files found"
ls -la "$SP_DIR"/__editable__*.pth 2>/dev/null || echo "No __editable__.pth files found"
echo ""

echo "=== Try importing caffe_ffi and check caffe_pb2 ==="
python -c "
try:
    import caffe_ffi
    print('caffe_ffi imported from:', caffe_ffi.__file__)
    import os
    pkg_dir = os.path.dirname(caffe_ffi.__file__)
    print('Package dir contents:', sorted(os.listdir(pkg_dir)))
    print()
    print('Checking for caffe_pb2...')
    caffe_pb2_path = os.path.join(pkg_dir, 'caffe_pb2.py')
    print('  caffe_pb2.py exists:', os.path.exists(caffe_pb2_path))
    if os.path.exists(caffe_pb2_path):
        print('  caffe_pb2.py size:', os.path.getsize(caffe_pb2_path), 'bytes')
except Exception as e:
    print('Import error:', type(e).__name__, str(e))
    import traceback
    traceback.print_exc()
"
echo ""

echo "=== Check pip list for caffe-ffi ==="
pip list 2>/dev/null | grep -i caffe
echo ""

echo "=== Check conda list for caffe-ffi ==="
conda list -n caffe-ffi 2>/dev/null | grep -i caffe
