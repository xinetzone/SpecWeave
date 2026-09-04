#!/bin/bash
PY=/opt/conda/envs/caffe-ffi/bin/python
echo "=== conda caffe-ffi python ==="
$PY -c "import sys; print(sys.executable)"
$PY -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | head -2
$PY -c "import caffe_ffi; print('caffe_ffi', caffe_ffi.__version__)" 2>&1 | head -2
$PY -c "import caffe_ffi; print('read_net' in dir(caffe_ffi), 'has read_net')" 2>&1 | head -2