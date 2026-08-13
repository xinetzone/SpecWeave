#!/bin/bash
# 在 caffe-ffi conda 环境中运行 build_and_bench_v6.sh
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== 激活 conda 环境: caffe-ffi ($(which python)) ==="
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-PASSIVE}"
export KMP_DUPLICATE_LIB_OK=TRUE
cd /SpecWeave/.trae/specs/caffe-ffi-conv-v4-milestone/
bash /SpecWeave/.trae/specs/caffe-ffi-conv-v4-milestone/build_and_bench_v6.sh