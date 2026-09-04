#!/usr/bin/env bash
# Pre-check: verify container can access mounted models and python/tvm/xmnn work
set -euo pipefail
echo "=== /workspace/models/debug ==="
ls /workspace/models/debug
echo "=== caffe_demo ==="
ls /workspace/models/debug/caffe_demo
echo "=== palmDet ==="
ls /workspace/models/debug/palmDet
echo "=== python ==="
which python
python --version
echo "=== import tvm/xmnn ==="
python -c "import importlib.metadata as m; import tvm, xmnn; print('tvm', tvm.__version__, '| xmnn', m.version('xmnn'))"
echo "=== xmnn api check ==="
python -c "import xmnn.accuracy_api as a; print('accuracy_api OK', [f for f in dir(a) if 'accuracy' in f.lower()])"
echo "PRECHECK_PASS"
