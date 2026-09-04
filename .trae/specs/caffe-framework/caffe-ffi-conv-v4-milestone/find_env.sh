#!/bin/bash
echo "=== /opt/venv python ==="
/opt/venv/bin/python -c "import sys; print(sys.executable)"
/opt/venv/bin/python -c "import numpy; print('numpy', numpy.__version__)" 2>&1 | head -2
/opt/venv/bin/python -c "import caffe_ffi; print('caffe_ffi', caffe_ffi.__version__)" 2>&1 | head -2
echo "=== conda envs ==="
ls /opt/conda/envs/ 2>/dev/null
echo "=== find caffe_ffi ==="
find / -name "caffe_ffi*" -maxdepth 6 2>/dev/null | head -10
echo "=== find read_net ==="
find / -path "*/caffe_ffi*" -name "*.py" 2>/dev/null | head -10