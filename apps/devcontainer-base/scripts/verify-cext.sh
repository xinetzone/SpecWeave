#!/bin/bash
# =============================================================================
# scripts/verify-cext.sh — C Extension ABI 兼容性验证脚本
# =============================================================================
# 用途：
#   1. 在 Dockerfile Stage 4/7 内验证 C 扩展正常加载（构建时验证）
#   2. 在 build.sh 冒烟测试中验证容器内 C 扩展兼容性（运行时验证）
#   3. 独立脚本：docker exec <container> /scripts/verify-cext.sh 手动检查
#
# 验证项：
#   - brotli C 扩展加载（已知非ft-safe，会打印GIL警告但功能正常）
#   - cffi C 扩展加载
#   - _sqlite3 内置 C 扩展
#   - _ssl 内置 C 扩展
#   - zlib C 扩展
#   - json 内置模块（纯Python，对照）
#   - libgcc 版本一致性检查（可选）
#
# 退出码：
#   0 - 所有验证通过
#   1 - 有C扩展加载失败
# =============================================================================
set -euo pipefail

# Ensure conda is in PATH (Dockerfile ENV sets PATH but exec may not have it)
export PATH="/opt/conda/bin:/opt/conda/envs/main/bin:$PATH"

PYTHON="${PYTHON:-/opt/conda/envs/main/bin/python}"
VERBOSE="${VERBOSE:-0}"
FAIL_COUNT=0
PASS_COUNT=0

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RESET='\033[0m'

if [ ! -t 1 ]; then
    RED=''; GREEN=''; YELLOW=''; RESET=''
fi

log_pass() { PASS_COUNT=$((PASS_COUNT+1)); echo -e "  ${GREEN}✔${RESET} $1"; }
log_fail() { FAIL_COUNT=$((FAIL_COUNT+1)); echo -e "  ${RED}✘${RESET} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${RESET} $1"; }
log_info() { echo "  $1"; }

echo "═══════════════════════════════════════════════════"
echo "  C Extension ABI Compatibility Verification"
echo "═══════════════════════════════════════════════════"

# Check Python exists
if [ ! -x "$PYTHON" ]; then
    log_fail "Python not found at $PYTHON"
    exit 1
fi

PY_VER=$("$PYTHON" -c 'import sys; print(sys.version.split()[0])' 2>&1)
log_info "Python: $PY_VER ($PYTHON)"

# Check free-threading build type
FT_BUILD=$("$PYTHON" -c 'import sysconfig; print("yes" if sysconfig.get_config_var("Py_GIL_DISABLED") else "no")' 2>&1)
if [ "$FT_BUILD" = "yes" ]; then
    log_info "Build type: cp314t (free-threading, GIL disabled by default)"
else
    log_info "Build type: cp314 (standard, GIL always enabled)"
fi

echo ""
echo "─── C Extension Load Tests ───"

# Test 1: brotli (pre-installed, non-ft-safe - prints GIL warning)
if "$PYTHON" -c "
import brotli
data = b'test' * 100
c = brotli.compress(data)
d = brotli.decompress(c)
assert d == data, 'roundtrip failed'
" 2>/dev/null; then
    log_pass "brotli: compress/decompress roundtrip OK"
else
    log_fail "brotli: FAILED to load or function correctly"
fi

# Test 2: cffi (pre-installed)
if "$PYTHON" -c "
import cffi
ffi = cffi.FFI()
ffi.cdef('int printf(const char *format, ...);')
C = ffi.dlopen(None)
" 2>/dev/null; then
    log_pass "cffi: C FFI interface OK"
else
    log_fail "cffi: FAILED"
fi

# Test 3: _sqlite3 (built-in C extension)
if "$PYTHON" -c "
import sqlite3
conn = sqlite3.connect(':memory:')
conn.execute('CREATE TABLE t (id INTEGER)')
conn.execute('INSERT INTO t VALUES (1)')
r = conn.execute('SELECT * FROM t').fetchone()
assert r == (1,), f'expected (1,), got {r}'
conn.close()
" 2>/dev/null; then
    log_pass "_sqlite3: built-in C ext OK"
else
    log_fail "_sqlite3: FAILED"
fi

# Test 4: _ssl (built-in C extension)
if "$PYTHON" -c "
import ssl
ctx = ssl.create_default_context()
assert ctx.protocol == ssl.PROTOCOL_TLS_CLIENT, 'SSL context creation failed'
" 2>/dev/null; then
    log_pass "_ssl: built-in C ext OK"
else
    log_fail "_ssl: FAILED"
fi

# Test 5: zlib (built-in C extension)
if "$PYTHON" -c "
import zlib
data = b'hello world' * 50
c = zlib.compress(data)
d = zlib.decompress(c)
assert d == data
" 2>/dev/null; then
    log_pass "zlib: built-in C ext OK"
else
    log_fail "zlib: FAILED"
fi

# Test 6: hashlib (built-in C extension with OpenSSL)
if "$PYTHON" -c "
import hashlib
h = hashlib.sha256(b'test').hexdigest()
assert len(h) == 64, f'expected 64 hex chars, got {len(h)}'
" 2>/dev/null; then
    log_pass "hashlib: built-in C ext OK"
else
    log_fail "hashlib: FAILED"
fi

# Test 7: json (pure Python, baseline)
if "$PYTHON" -c "
import json
d = {'key': 'value', 'num': 42}
s = json.dumps(d)
assert json.loads(s) == d
" 2>/dev/null; then
    log_pass "json: pure Python baseline OK"
else
    log_fail "json: FAILED"
fi

# Test 8: ipykernel C extensions (if installed)
if "$PYTHON" -c "import ipykernel" 2>/dev/null; then
    log_pass "ipykernel: import OK (Jupyter kernel)"
else
    log_warn "ipykernel: not found (not installed in this env)"
fi

echo ""
echo "─── ABI Consistency Checks ───"

# Check SOABI consistency
SOABI=$("$PYTHON" -c 'import sysconfig; print(sysconfig.get_config_var("SOABI") or "unknown")' 2>&1)
log_info "SOABI: $SOABI"

if [ "$FT_BUILD" = "yes" ]; then
    if echo "$SOABI" | grep -q "cpython-314t"; then
        log_pass "SOABI matches free-threading build (cpython-314t)"
    else
        log_fail "SOABI mismatch: expected cpython-314t for ft build, got $SOABI"
    fi
fi

# Check for cp314 vs cp314t mixing in conda packages
if command -v conda &>/dev/null; then
    CONDA_ENV="${CONDA_ENV:-main}"
    if conda list -n "$CONDA_ENV" 2>/dev/null | grep -q "cp314[^t]"; then
        # Check for packages that explicitly target cp314 (not cp314t)
        MIXED_PKGS=$(conda list -n "$CONDA_ENV" 2>/dev/null | grep "cp314-" | grep -v "cp314t" || true)
        if [ -n "$MIXED_PKGS" ]; then
            log_warn "Potential ABI mixing detected (cp314 packages in cp314t env):"
            echo "$MIXED_PKGS" | while IFS= read -r line; do
                echo "    $line"
            done
        else
            log_pass "No cp314/cp314t ABI mixing detected in conda packages"
        fi
    else
        log_pass "No cp314/cp314t ABI mixing detected in conda packages"
    fi
fi

# Check defaults channel
if command -v conda &>/dev/null; then
    if conda config --show channels 2>/dev/null | grep -qE "^\s*-\s+defaults\s*$"; then
        log_warn "defaults channel detected! This may cause cp314/cp314t ABI conflicts."
        log_warn "  conda-forge only is recommended for free-threading builds."
    else
        log_pass "No defaults channel (conda-forge only - safe for ft builds)"
    fi
fi

echo ""
echo "═══════════════════════════════════════════════════"
if [ "$FAIL_COUNT" -eq 0 ]; then
    echo -e "  ${GREEN}RESULT: PASS${RESET} ($PASS_COUNT checks passed)"
    echo "═══════════════════════════════════════════════════"
    exit 0
else
    echo -e "  ${RED}RESULT: FAIL${RESET} ($FAIL_COUNT failed, $PASS_COUNT passed)"
    echo "═══════════════════════════════════════════════════"
    exit 1
fi
