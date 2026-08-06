#!/bin/bash
# 运行跨实现算子精度对比分析（compare_ops.py）
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
export KMP_DUPLICATE_LIB_OK=TRUE
export PATH="$CONDA_PREFIX/bin:$PATH"

ASSETS=/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets
echo "=== numpy check ==="
python -c "import numpy; print('numpy', numpy.__version__)" 2>&1 || { echo "installing numpy..."; conda install -y numpy 2>&1 | tail -3; }
python -c "import numpy; print('numpy', numpy.__version__)"
echo "=== run compare_ops ==="
python "$ASSETS/compare_ops.py" 2>&1
echo "DONE_COMPARE"