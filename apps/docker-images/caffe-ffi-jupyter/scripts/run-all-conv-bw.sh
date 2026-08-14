#!/bin/bash
# WSL entry: Run ALL Conv backward tests (25 tests) with perf tracking
# Delegates to wsl-run-conv-bw.sh
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SCRIPT_DIR/wsl-run-conv-bw.sh"
