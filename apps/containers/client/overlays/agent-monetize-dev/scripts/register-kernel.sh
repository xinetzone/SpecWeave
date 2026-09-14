#!/bin/bash
# ==============================================================================
# register-kernel.sh — 注册 agent-monetize-dev Jupyter 内核（构建期执行一次）
#
# apache-tvm-ffi wheel 仅 cp314 GIL：内核 argv 固定 /opt/conda/bin/python
# （base env），Jupyter 服务在 main env 由 supervisord 运行。
# 内核 env 携带源码 PYTHONPATH 与 tvm_ffi 的 LD_LIBRARY_PATH。
# root 与 devuser 均可见（写 main env sys-prefix 共享 kernels 目录）。
# ==============================================================================
set -euo pipefail

CONDA_PYTHON=/opt/conda/bin/python
JUPYTER_BIN=/opt/conda/envs/main/bin/jupyter
KERNEL_NAME=agent-monetize-dev
KERNEL_DIR=/opt/conda/envs/main/share/jupyter/kernels/${KERNEL_NAME}

echo "[kernel] ${CONDA_PYTHON} (base cp314 GIL; apache-tvm-ffi ABI)"
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
 "display_name": "Python 3.14 (agent-monetize dev)",
 "language": "python",
 "env": {
  "PATH": "/opt/conda/bin:/opt/conda/envs/main/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin",
  "PYTHONPATH": "/workspace/agent-monetize/src",
  "LD_LIBRARY_PATH": "/opt/conda/lib/python3.14/site-packages/tvm_ffi/lib:/opt/conda/envs/main/lib"
 }
}
JSON
chmod -R a+rX /opt/conda/envs/main/share/jupyter/kernels
echo "[kernel] registered at ${KERNEL_DIR}/kernel.json"

echo "[kernel] visibility check (root):"
"${JUPYTER_BIN}" kernelspec list | grep "${KERNEL_NAME}"
echo "[kernel] visibility check (devuser):"
su -s /bin/bash devuser -c "'${JUPYTER_BIN}' kernelspec list | grep '${KERNEL_NAME}'"
echo "[OK] ${KERNEL_NAME} kernel visible to both root and devuser"
