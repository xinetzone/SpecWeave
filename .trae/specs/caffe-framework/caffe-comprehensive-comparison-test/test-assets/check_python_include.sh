#!/bin/bash
# 检查 conda python 头文件 + 用 conda python 重新配置
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== which python ==="
which python
python --version
echo "=== conda python include ==="
python -c "import sysconfig; print('include:', sysconfig.get_paths()['include'])"
ls "$CONDA_PREFIX/include/python3.14/" 2>&1 | head -5
echo "=== /opt/venv python ==="
/opt/venv/bin/python3.14 --version 2>&1
/opt/venv/bin/python3.14 -c "import sysconfig; print('include:', sysconfig.get_paths()['include'])" 2>&1
echo "=== PATH ==="
echo "$PATH" | tr ':' '\n' | head -10