#!/usr/bin/env bash
# xmnn-runtime 内置 torch 层（Containerfile.xmnn-runtime Layer 1）
#
# 由 TORCH_FLAVOR 驱动（白名单，bin/relpack 侧已先校验）：
#   cpu    默认 —— CPU wheel（torch.version.cuda is None），与 2026-09-16 起的
#          内置 CPU 层语义逐字等价（镜像体积/离线契约不变）；
#   cu130  CUDA 13.0 wheel（torch.version.cuda is not None），运行期须靠交付
#          骨架把 GPU 设备透传进来才能用上；
#   ""     不装。本产品**不可达**（product.env 的 TORCH_DEFAULT="cpu"，空值一律
#          回落 cpu），保留分支仅为与 xmnn-dev 脚本同构 + 防御绕过 bin/relpack 的直调。
#
# 为什么索引由**形态推导**而不是独立 ARG：PyPI（含 tuna/aliyun 镜像）上的
# torch 默认是 CUDA 变体，会连带拉入 nvidia-cuda-*/cudnn/nccl 十余个共数 GB
# 的包，故必须固定 download.pytorch.org/whl/<flavor>；把索引写成第二个 ARG
# 就制造了「形态 vs 索引」两处事实源（同 C15 纪律），故由白名单形态推导。
#
# 为什么 cu130 而不是 cu128/cu129：实测（2026-09-20）download.pytorch.org
# 各索引下 cp314 可用版本为 cpu→2.14.0、cu130→2.14.0、cu129→2.13.0、
# cu128→2.11.0。cu130 是唯一能与其他形态同 pin 2.14.0 的 CUDA 索引。
#
# 为什么装进 base env（/opt/conda）：wheel tag 是 cp314-cp314，只能落在
# base env（GIL 版）；main env 是 cp314t free-threading，ABI 不匹配。
#
# 为什么 cu130 **不**随带 nvcc（对照 xmnn-dev 的 C25）：本栈是交付运行时，
# §4 P0 明确禁止 LLVM/Clang/Nuitka/gcc/gdb 等编译器工具链。CUDA 版 torch
# 足以跑 GPU 张量与 torch.jit 推理；需要 nvcc 编译 CUDA 内核 / TVM CUDA
# codegen 的场景请回 xmnn-dev 栈（其 cu130 形态经 C25 提供 nvcc 13.4.92）。
#
# 形态落盘 /opt/xmnnrt-torch-flavor 供构建期守卫 §10 断言（守卫读不到 LABEL）。
set -euo pipefail

PY=/opt/conda/bin/python
MARKER=/opt/xmnnrt-torch-flavor
TORCH_VERSION="${TORCH_VERSION:-2.14.0}"
FLAVOR="${TORCH_FLAVOR:-cpu}"

case "${FLAVOR}" in
  "")
    echo "[xmnnrt] torch: skipped (TORCH_FLAVOR 为空 —— 镜像不含 torch)"
    ;;
  cpu|cu130)
    echo "[xmnnrt] torch: 从 download.pytorch.org/whl/${FLAVOR} 安装 torch==${TORCH_VERSION}"
    "${PY}" -m pip install --no-cache-dir \
      --index-url "https://download.pytorch.org/whl/${FLAVOR}" \
      "torch==${TORCH_VERSION}"
    rm -rf /root/.cache/pip
    "${PY}" -c 'import torch; print("[xmnnrt] torch", torch.__version__, "cuda=", torch.version.cuda)'
    ;;
  *)
    echo "[xmnnrt] ERROR: TORCH_FLAVOR 必须为空|cpu|cu130，实际为 '${FLAVOR}'" >&2
    exit 1
    ;;
esac

printf '%s' "${FLAVOR}" > "${MARKER}"
echo "[xmnnrt] torch flavor marker: ${MARKER}='${FLAVOR}'"