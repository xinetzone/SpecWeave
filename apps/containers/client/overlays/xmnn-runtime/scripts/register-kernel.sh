#!/bin/bash
# ==============================================================================
# register-kernel.sh — 注册 xmnn-runtime Jupyter 内核（叠加镜像构建期执行一次）
#
# 与 xmnn-dev 内核的差异：
#   - argv 同为 /opt/conda/bin/python（wheel 是 cp314 GIL ABI，main env 是
#     cp314t，不能互换）；
#   - env 只保留 PATH：wheel 已装入 base env 的 site-packages，_libs 以
#     RPATH=$ORIGIN 自解析，**不注入**任何 /workspace 源码 PYTHONPATH /
#     TVM_LIBRARY_PATH / LD_LIBRARY_PATH——交付语义是无源码的干净运行时。
#
# 注册位置：main env 的 sys.prefix 共享 kernelspec 目录（root 与 devuser
# 均可见，与 xmnn-dev 注册脚本同位置实证）。
# ==============================================================================
set -euo pipefail

CONDA_PYTHON=/opt/conda/bin/python
JUPYTER_BIN=/opt/conda/envs/main/bin/jupyter
KERNEL_NAME=xmnn-runtime
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
 "display_name": "Python 3.14 (xmnn runtime)",
 "language": "python",
 "env": {
  "PATH": "/opt/conda/bin:/opt/conda/envs/main/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
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
