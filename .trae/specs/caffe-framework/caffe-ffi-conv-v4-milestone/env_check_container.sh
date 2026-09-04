#!/bin/bash
# 检测容器内正确的 Python 环境
echo "=== which python ==="
which python python3 2>&1
echo "=== conda envs ==="
ls /opt/conda/envs 2>/dev/null
echo "=== conda python ==="
ls -la /opt/conda/bin/python* 2>/dev/null
echo "=== find _caffe_ffi.so ==="
find / -name "_caffe_ffi.so" 2>/dev/null | head
echo "=== find numpy ==="
find / -name "numpy" -maxdepth 6 -type d 2>/dev/null | head
echo "=== python version ==="
python --version 2>&1
python3 --version 2>&1