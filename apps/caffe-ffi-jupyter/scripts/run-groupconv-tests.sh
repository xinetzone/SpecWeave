#!/bin/bash
# WSL entry: Run GroupConv backward tests only (10 tests)
# Delegates to wsl-run-conv-bw.sh with -k filter
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
bash "$SCRIPT_DIR/wsl-run-conv-bw.sh" "TestConvBackwardGroups"
