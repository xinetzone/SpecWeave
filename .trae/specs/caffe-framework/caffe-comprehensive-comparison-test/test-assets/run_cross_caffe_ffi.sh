#!/bin/bash
# 在 caffe-ffi 容器中运行跨实现算子对比
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:$PATH"
export KMP_DUPLICATE_LIB_OK=TRUE
cd /tmp
python /tmp/cross_ops.py /tmp/cross_ops all 2>&1 | tail -40