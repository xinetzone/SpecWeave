#!/bin/bash
# 环境预检：验证 caffe-ffi-jupyter 镜像内 native 扩展可用性
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "Python: $(python --version)"
python - <<'PY'
import caffe_ffi
print("caffe_ffi version:", caffe_ffi.__version__)
print("native available:", caffe_ffi._ffi_api.is_available())
print("file:", caffe_ffi.__file__)
PY