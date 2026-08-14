#!/bin/bash
# Diagnostic check for S2/S3 advancement environment
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== Python ==="
python --version
echo "=== grpc_tools ==="
python -c "import grpc_tools; print('grpc_tools OK')" 2>&1 || echo "grpc_tools MISSING"
echo "=== caffe_ffi import ==="
python -c "import caffe_ffi; print('caffe_ffi', caffe_ffi.__version__)" 2>&1 || echo "caffe_ffi MISSING"
echo "=== gen_proto.py present ==="
ls -la /SpecWeave/projects/xuanspace/libs/caffe-ffi/scripts/gen_proto.py 2>&1
echo "=== editable-install.sh present ==="
ls -la /SpecWeave/apps/docker-images/caffe-ffi-jupyter/scripts/editable-install.sh 2>&1
echo "=== proto output dir ==="
ls -la /SpecWeave/projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/caffe/proto/ 2>&1
echo "=== done ==="