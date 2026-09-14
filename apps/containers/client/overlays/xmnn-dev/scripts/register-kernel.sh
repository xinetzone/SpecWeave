#!/bin/bash
# ==============================================================================
# register-kernel.sh — 注册 xmnn-dev Jupyter 内核（叠加镜像构建期执行一次）
#
# 双 ABI 背景（2026-09-14 实证）：
#   - Jupyter 服务在 main env（/opt/conda/envs/main/bin/jupyter，cp314t）；
#   - Nuitka/xmnn/tvm 工具链与 wheel ABI 是 cp314 GIL，故内核 argv 固定
#     /opt/conda/bin/python（base env）；
#   - 内核 env 携带源码 PYTHONPATH/TVM_LIBRARY_PATH/LD_LIBRARY_PATH，Notebook
#     直接调试 /workspace 下挂载的 npu_tvm/npuusertools 源码。
#
# 注册位置：main env 的 sys.prefix 共享 kernelspec 目录（root 与 devuser 均可见）。
# ==============================================================================
set -euo pipefail

CONDA_PYTHON=/opt/conda/bin/python
JUPYTER_BIN=/opt/conda/envs/main/bin/jupyter
KERNEL_NAME=xmnn-dev
KERNEL_DIR=/opt/conda/envs/main/share/jupyter/kernels/${KERNEL_NAME}

echo "[kernel] interpreter (cp314 GIL ABI): ${CONDA_PYTHON}"
"${CONDA_PYTHON}" --version

mkdir -p "${KERNEL_DIR}"
cat > "${KERNEL_DIR}/kernel.json" <<'JSON'
{
 "argv": [
  "/opt/conda/bin/python",
  "-m",
  "ipykernel_launcher",
  "-f",
  "{connection_file}"
 ],
 "display_name": "Python 3.14 (xmnn dev)",
 "language": "python",
 "env": {
  "PATH": "/opt/conda/bin:/opt/conda/envs/main/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
  "PYTHONPATH": "/workspace/npu_tvm/python:/workspace/npu_tvm/vta/python:/workspace/npuusertools",
  "TVM_LIBRARY_PATH": "/workspace/npu_tvm/build",
  "LD_LIBRARY_PATH": "/workspace/npu_tvm/build:/workspace/npu_tvm/build/vta:/opt/conda/envs/main/lib",
  "NPU_TOOLS_ROOT": "/workspace",
  "XMNN_TOOLS_ROOT": "/workspace/npuusertools"
 }
}
JSON
chmod -R a+rX /opt/conda/envs/main/share/jupyter/kernels

echo "[kernel] registered at ${KERNEL_DIR}/kernel.json"
echo "[kernel] visibility check (root):"
"${JUPYTER_BIN}" kernelspec list | grep "${KERNEL_NAME}"
echo "[kernel] visibility check (devuser):"
su -s /bin/bash devuser -c "'${JUPYTER_BIN}' kernelspec list" | grep "${KERNEL_NAME}"
echo "[OK] ${KERNEL_NAME} kernel visible to both root and devuser"
