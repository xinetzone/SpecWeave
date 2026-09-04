#!/bin/bash
# 在 WSL 中运行 caffe-ffi 环境预检（挂载 caffe-ffi 源码触发 editable-install 编译）
# 用法: bash run_check_in_wsl.sh  (在 WSL 中执行)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)"
CHECK_SH="${SCRIPT_DIR}/check_caffe_ffi.sh"
# 源码目录（Windows 路径 → WSL /mnt/d 路径）
CAFFE_FFI_SRC="/mnt/d/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi"
echo "check script: ${CHECK_SH}"
echo "caffe-ffi src: ${CAFFE_FFI_SRC}"
docker run --rm \
  -v "${CHECK_SH}:/tmp/check.sh" \
  -v "${CAFFE_FFI_SRC}:/workspace/projects/xuanspace/libs/caffe-ffi" \
  caffe-ffi-jupyter:latest bash /tmp/check.sh