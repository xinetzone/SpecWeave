#!/bin/bash
# caffex (origin-runtime) 环境检查
set +e
echo "=== TIME: $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== python ==="
which python3 python
python3 --version 2>&1
echo "=== caffe import ==="
python3 -c "import caffe; print('caffe', getattr(caffe,'__version__','?'), caffe.__file__)" 2>&1 | tail -5
echo "=== numpy ==="
python3 -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | tail -3
echo "=== protobuf ==="
python3 -c "import google.protobuf; print('protobuf', google.protobuf.__version__)" 2>&1 | tail -3
echo "=== workspace listing ==="
ls /workspace 2>&1 | head -20
echo "=== /workspace/caffex ==="
ls /workspace/caffex 2>&1 | head -20
echo "=== /workspace/caffex/python ==="
ls /workspace/caffex/python 2>&1 | head -20
echo "DONE_CAFFEX_CHECK"