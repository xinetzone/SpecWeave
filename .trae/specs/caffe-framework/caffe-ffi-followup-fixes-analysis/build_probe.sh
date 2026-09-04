#!/bin/bash
# 探测 caffe-ffi 构建环境
set +e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi
echo "=== pwd: $(pwd) ==="
echo "--- build dirs ---"
ls -d build* 2>/dev/null || echo "(no build dir)"
echo "--- cmake/ninja ---"
which cmake ninja 2>/dev/null
echo "--- compiler ---"
which g++ 2>/dev/null; g++ --version 2>/dev/null | head -1
echo "--- tvm-ffi source ---"
ls /SpecWeave/projects/xuanspace/vendor/tvm-ffi/pyproject.toml 2>/dev/null && echo "tvm-ffi src present" || echo "tvm-ffi src MISSING"
echo "--- pip list frozen (key) ---"
pip list 2>/dev/null | grep -iE "scikit-build|cmake|ninja|grpc|protobuf|tvm-ffi|caffe-ffi" | head -20
echo "--- net.cpp fix present? ---"
grep -c "FromProto" src/caffe_ffi/net.cpp