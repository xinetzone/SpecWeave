#!/bin/bash
# 在 caffex (origin-runtime) 环境运行跨实现算子对比
set -e
export GLOG_minloglevel=2
export PYTHONPATH=/workspace/caffex/python
export LD_LIBRARY_PATH=/workspace/caffex/build/lib:/usr/lib/x86_64-linux-gnu:${LD_LIBRARY_PATH:-}
cd /tmp
python3 /tmp/cross_ops.py /tmp/cross_ops all 2>&1 | tail -40