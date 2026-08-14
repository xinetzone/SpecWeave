#!/usr/bin/env bash
# scripts/ft-benchmark.sh — 接口兼容薄委托（实际实现在 ft_benchmark.py）
#
# 保留原因：镜像内 /usr/local/bin/ft-benchmark.sh 是 v2.2 起的用户可见入口；
# 核心逻辑（解析/阈值/JSONL 日志）已迁移至同目录 ft_benchmark.py（可 import 复用）。
#
# 用法（与历史版本一致）：
#   ./scripts/ft-benchmark.sh --image devcontainer-base:conda-llvm-latest --quick
#   ./scripts/ft-benchmark.sh --full --json
#   ./scripts/ft-benchmark.sh --local --range 200000
# 新增能力：--local（本机解释器）、--json（结构化输出）
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PY="${FT_BENCHMARK_PYTHON:-python3}"
exec "$PY" "$SCRIPT_DIR/ft_benchmark.py" "$@"
