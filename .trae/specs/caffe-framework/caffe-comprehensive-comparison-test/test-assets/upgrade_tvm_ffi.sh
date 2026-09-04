#!/bin/bash
# 在 caffe-ffi-jupyter 镜像内升级 tvm_ffi 并触发 editable-install 编译
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== 当前 tvm_ffi ==="
pip show apache-tvm-ffi 2>/dev/null | grep -E 'Name|Version' || echo "(not installed)"
echo "=== 升级 tvm_ffi > 0.1.12 ==="
pip install -i https://mirrors.aliyun.com/pypi/simple/ "apache-tvm-ffi>0.1.12" 2>&1 | tail -5
echo "=== 升级后版本 ==="
python -c "import tvm_ffi; print('tvm_ffi:', tvm_ffi.__version__)"