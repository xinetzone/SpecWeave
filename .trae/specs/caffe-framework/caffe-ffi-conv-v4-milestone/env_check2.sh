#!/bin/bash
# 确认 caffe-ffi conda 环境的依赖完整性
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== python ==="
python --version
which python
echo "=== deps ==="
python -c "import numpy; print('numpy', numpy.__version__)" 2>&1
python -c "import caffe_ffi; print('caffe_ffi', caffe_ffi.__file__)" 2>&1
echo "=== model files ==="
ls -la /root/.caffe_test_data/models/ 2>&1 | head -20
ls -la /root/.caffe_test_data/models/sdk/ 2>&1
echo "=== read_net test ==="
python -c "import caffe_ffi; print([x for x in dir(caffe_ffi) if not x.startswith('_')])" 2>&1