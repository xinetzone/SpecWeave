#!/bin/bash
# Quick caffe-ffi environment check inside Docker container
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi

echo "=== Python Version ==="
python --version

echo ""
echo "=== caffe-ffi Import Check ==="
python -c "
import caffe_ffi
print('caffe_ffi version:', caffe_ffi.__version__)
from caffe_ffi import _ffi_api
print('C++ extension available:', _ffi_api.is_available())
"

echo ""
echo "=== Key Package Versions ==="
python -c "
import numpy;        print('numpy:       ', numpy.__version__)
import google.protobuf; print('protobuf:    ', google.protobuf.__version__)
import pytest;       print('pytest:      ', pytest.__version__)
import tvm_ffi;      print('tvm_ffi:     ', tvm_ffi.__version__)
"

echo ""
echo "=== Test directory contents ==="
ls -la tests/python/ | head -20

echo ""
echo "=== Check existing perf CSV logs ==="
ls -la tests/python/.temp/perf_log_*.csv 2>/dev/null || echo "(no existing perf logs)"

echo ""
echo "=== Environment check complete ==="
