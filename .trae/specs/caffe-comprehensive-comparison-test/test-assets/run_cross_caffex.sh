#!/bin/bash
# 在 caffex (origin-runtime) 容器内运行 cross_ops，输出直接写回挂载的 results 目录
set -e
export GLOG_minloglevel=2
export PYTHONPATH=/workspace/caffex/python
export LD_LIBRARY_PATH=/workspace/caffex/build/lib:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}

ASSETS=/tmp/assets
python3 "$ASSETS/cross_ops.py" "$ASSETS/results" all 2>&1 | grep -E '\] |结果已保存'
echo "--- ls results ---"
ls -la "$ASSETS/results/cross_ops_caffex.json"
echo "DONE"