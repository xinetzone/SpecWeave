#!/bin/bash
# 检查 caffe-ffi 容器的 matplotlib 可用性
set +e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
python -c "import matplotlib; print('matplotlib', matplotlib.__version__)" 2>&1 | tail -3
python -c "import sys; print('py', sys.version.split()[0])" 2>&1
echo "DONE"