#!/bin/bash
# caffe-ffi 功能测试运行器（容器内执行）
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export PATH="$CONDA_PREFIX/bin:$PATH"
export KMP_DUPLICATE_LIB_OK=TRUE

TEST_ROOT="/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python"
cd "$TEST_ROOT"

echo "=== 环境确认 ==="
python -c "import caffe_ffi; print('  caffe_ffi:', caffe_ffi.__version__); print('  native:', caffe_ffi._ffi_api.is_available())"
python -c "import tvm_ffi; print('  tvm_ffi:', tvm_ffi.__version__)"
python -c "import numpy, google.protobuf; print('  numpy:', numpy.__version__, '| protobuf:', google.protobuf.__version__)"
echo "  pytest: $(python -m pytest --version | head -1)"
echo "=============================================="

echo ""
echo "=== 运行完整功能测试套件（排除性能/slow） ==="
python -m pytest -p no:cacheprovider \
  --ignore=ops \
  -m "not slow and not performance" \
  -q \
  --tb=short \
  --no-header 2>&1 | tail -80
echo "PYTEST_EXIT=${PIPESTATUS[0]}"