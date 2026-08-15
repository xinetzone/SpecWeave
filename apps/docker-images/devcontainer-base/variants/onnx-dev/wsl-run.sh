#!/usr/bin/env bash
# WSL 入口脚本：从 Windows 调用时自动 cd 到脚本目录并执行 start-dev.sh
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "[wsl-run] PWD=$(pwd)" >&2
echo "[wsl-run] ARGS=$*" >&2
# 先简单测试 docker 是否能直接运行
echo "[wsl-run] Testing direct docker command..." >&2
docker run --rm -i -e WORKSPACE_CHOWN_MODE=named-only -v "$SCRIPT_DIR:/workspace" -w /workspace devcontainer-base:onnx-dev-latest echo "direct docker works!"
echo "[wsl-run] Now running start-dev.sh..." >&2
exec bash -x ./start-dev.sh "$@"
