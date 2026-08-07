#!/bin/bash
# 环境状态检查脚本：在容器内运行，输出 caffe_ffi / caffex 可用性
set +e
echo "=== TIME: $(date '+%Y-%m-%d %H:%M:%S') ==="
echo "=== which python ==="
which python python3 2>&1

echo "=== conda envs ==="
source /opt/conda/etc/profile.d/conda.sh 2>/dev/null
conda env list 2>&1

echo "=== try caffe-ffi import (env caffe-ffi) ==="
conda activate caffe-ffi 2>/dev/null
python -c "import sys; print('python', sys.version.split()[0])" 2>&1
python -c "import caffe_ffi as c; print('caffe_ffi', getattr(c,'__version__','?'))" 2>&1 | tail -5
python -c "import caffe_ffi, os, glob; p=os.path.dirname(caffe_ffi.__file__); print('caffe_ffi_dir', p); print('so', glob.glob(os.path.join(p,'_caffe_ffi*.so')))" 2>&1 | tail -5

echo "=== try caffex (caffe) ==="
python -c "import caffe; print('caffe', caffe.__version__, caffe.__file__)" 2>&1 | tail -5

echo "=== whoami / workspace ==="
whoami
ls /workspace 2>&1 | head
echo "DONE_STATE_CHECK"