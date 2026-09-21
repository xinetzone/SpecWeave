#!/usr/bin/env bash
# xmnn-dev 可选 torch 安装层（Containerfile.xmnn-dev Layer 2.5）
#
# 由 TORCH_FLAVOR 驱动（白名单，invoke 侧 resolve_build_args 已先校验）：
#   ""      不装（默认）——镜像保持零 torch，体积与离线契约完全不变
#   cpu     CPU wheel（torch.version.cuda is None）
#   cu130   CUDA 13.0 wheel（torch.version.cuda is not None）
#
# 为什么固定 download.pytorch.org/whl/<flavor> 索引：PyPI（含 tuna/aliyun
# 镜像）上的 torch 默认是 CUDA 变体，会连带拉入 nvidia-cuda-*/cudnn/nccl
# 十余个共数 GB 的包；显式索引是唯一能确定性拿到目标形态的方式。
#
# 为什么 cu130 而不是 cu128/cu129：实测（2026-09-20）download.pytorch.org
# 各索引下 cp314 可用版本为 cpu→2.14.0、cu130→2.14.0、cu129→2.13.0、
# cu128→2.11.0。cu130 是唯一能与其他形态同 pin 2.14.0 的 CUDA 索引。
#
# 为什么装进 base env（/opt/conda）而非 main env：C13 双 ABI 不可互换——
# torch 的 wheel tag 是 cp314-cp314，只能落在 base env（GIL 版）；main env
# 是 cp314t free-threading，ABI 不匹配。与客户交付栈（offline-delivery 应用
# 的交付包 products/ 目录）同一条先例。
#
# 形态落盘 /opt/xmnn-torch-flavor 供构建期守卫 §8 断言（守卫读不到 LABEL）。
set -euo pipefail

PY=/opt/conda/bin/python
MARKER=/opt/xmnn-torch-flavor
TORCH_VERSION="${TORCH_VERSION:-2.14.0}"
FLAVOR="${TORCH_FLAVOR:-}"

case "${FLAVOR}" in
  "")
    echo "[xmnn] torch: skipped (TORCH_FLAVOR 为空 —— 默认镜像不含 torch)"
    ;;
  cpu|cu130)
    echo "[xmnn] torch: 从 download.pytorch.org/whl/${FLAVOR} 安装 torch==${TORCH_VERSION}"
    "${PY}" -m pip install --no-cache-dir \
      --index-url "https://download.pytorch.org/whl/${FLAVOR}" \
      "torch==${TORCH_VERSION}"
    rm -rf /root/.cache/pip
    "${PY}" -c 'import torch; print("[xmnn] torch", torch.__version__, "cuda=", torch.version.cuda)'
    ;;
  *)
    echo "[xmnn] ERROR: TORCH_FLAVOR 必须为空|cpu|cu130，实际为 '${FLAVOR}'" >&2
    exit 1
    ;;
esac

printf '%s' "${FLAVOR}" > "${MARKER}"
echo "[xmnn] torch flavor marker: ${MARKER}='${FLAVOR}'"
