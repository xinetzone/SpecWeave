#!/bin/bash
# caffe-ffi 网络模型测试（ResNet50/MobileNetV2/AlexNet/InceptionV1）
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:$PATH"
export KMP_DUPLICATE_LIB_OK=TRUE

NET_ROOT="/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/networks"
cd "$NET_ROOT"

echo "=== 网络模型测试 (networks) ==="
python -m pytest -p no:cacheprovider \
  -q --tb=short --no-header 2>&1 | tail -60
echo "NET_EXIT=${PIPESTATUS[0]}"