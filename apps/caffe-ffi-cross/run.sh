#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
sed -i 's/\r$//' "${BASH_SOURCE[0]}" 2>/dev/null || true
sed -i 's/\r$//' "$SCRIPT_DIR/scripts/test-cross-build.sh" 2>/dev/null || true
exec "$SCRIPT_DIR/scripts/test-cross-build.sh" "$@"
