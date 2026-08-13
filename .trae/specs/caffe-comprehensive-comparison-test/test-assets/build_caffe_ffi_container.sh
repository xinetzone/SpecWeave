#!/bin/bash
# 在 caffe-ffi-jupyter 镜像中编译最新版 tvm-ffi + caffe-ffi（命名容器持久化）
# 关键：同时挂载 tvm-ffi 与 caffe-ffi 源码，让 editable-install.sh 从源码编译
# 用法: bash build_caffe_ffi_container.sh
set -e
IMG="caffe-ffi-jupyter:latest"
CTN="caffe-ffi-build"
# WSL 路径
TVM_FFI_SRC="/mnt/d/spaces/SpecWeave/projects/xuanspace/vendor/tvm-ffi"
CAFFE_FFI_SRC="/mnt/d/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi"

# 清理旧容器
docker rm -f "${CTN}" 2>/dev/null || true

echo "=== 启动构建容器（默认 entrypoint 触发 editable-install）==="
docker run -d --name "${CTN}" \
  -v "${TVM_FFI_SRC}:/workspace/projects/xuanspace/vendor/tvm-ffi" \
  -v "${CAFFE_FFI_SRC}:/workspace/projects/xuanspace/libs/caffe-ffi" \
  "${IMG}" bash -c "sleep infinity"

echo "=== 等待 editable-install 编译完成 ==="
for i in $(seq 1 60); do
    if docker exec "${CTN}" bash -lc 'source /opt/conda/etc/profile.d/conda.sh && conda activate caffe-ffi && python -c "import caffe_ffi; print(caffe_ffi.__version__)"' 2>/dev/null | grep -qE '^[0-9]'; then
        echo "编译完成 (第 ${i} 次检查)"
        break
    fi
    sleep 5
done

echo "=== 验证 tvm_ffi 与 caffe_ffi ==="
docker exec "${CTN}" bash -lc '
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
python - <<PY
import tvm_ffi
print("tvm_ffi:", tvm_ffi.__version__)
print("tvm_ffi file:", tvm_ffi.__file__)
import caffe_ffi
print("caffe_ffi:", caffe_ffi.__version__)
print("native:", caffe_ffi._ffi_api.is_available())
print("file:", caffe_ffi.__file__)
PY
'

echo "=== 构建容器就绪: ${CTN} ==="