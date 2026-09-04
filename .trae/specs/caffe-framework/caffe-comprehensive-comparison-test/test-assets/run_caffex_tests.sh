#!/bin/bash
# caffex (origin-runtime 镜像) 网络功能测试
set -e
export GLOG_minloglevel=2
export PYTHONPATH=/workspace/caffex/python
export LD_LIBRARY_PATH=/workspace/caffex/build/lib:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}

echo "=== 环境确认 ==="
python3 -c "import caffe; print('  caffe:', caffe.__file__)"
python3 -c "import numpy; print('  numpy:', numpy.__version__)" 2>&1 || pip install numpy --quiet
echo "=== 安装 pytest ==="
pip install pytest --quiet 2>&1 | tail -3 || python3 -m pip install pytest --quiet 2>&1 | tail -3
echo "=== 运行 caffex 网络测试 ==="
cd /workspace/tests/networks
ls -la
python3 -m pytest -q --tb=short --no-header 2>&1 | tail -60
echo "NET_EXIT=${PIPESTATUS[0]}"