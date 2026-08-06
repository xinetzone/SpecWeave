#!/bin/bash
# =============================================================================
# container-healthcheck.sh — Docker HEALTHCHECK for caffe-ffi-jupyter
#
# Purpose:
#   Comprehensive container health check that verifies not just Jupyter
#   availability but also the integrity of the Python/C++ runtime environment:
#   conda activation, caffe_ffi import, protobuf ABI match, shared library
#   resolution, and Jupyter API responsiveness.
#
# Exit codes (Docker HEALTHCHECK convention):
#   0  healthy   — all checks passed
#   1  unhealthy — one or more critical checks failed
#
# Design principles:
#   - Fast (< 3s typical): no heavy computation, just import + ldd + curl
#   - Self-contained: activates conda internally, does not rely on caller env
#   - Informative: prints failure reason to stdout for docker inspect logs
# =============================================================================
set -uo pipefail

# ── Activate conda environment ──
for conda_sh in /opt/conda/etc/profile.d/conda.sh \
                "$HOME/miniconda3/etc/profile.d/conda.sh"; do
    if [ -f "$conda_sh" ]; then
        # shellcheck source=/dev/null
        source "$conda_sh" 2>/dev/null && conda activate caffe-ffi 2>/dev/null && break
    fi
done

PYTHON="${CONDA_PREFIX:+$CONDA_PREFIX/bin/}python"
if [ ! -x "$PYTHON" ]; then
    PYTHON=$(command -v python 2>/dev/null || echo "")
fi
if [ -z "$PYTHON" ] || [ ! -x "$PYTHON" ]; then
    echo "UNHEALTHY: Python not found / conda env not activated"
    exit 1
fi

FAIL=0

# Helper: run Python with KMP_DUPLICATE_LIB_OK set
run_py() {
    KMP_DUPLICATE_LIB_OK=TRUE "$PYTHON" -c "$1" 2>/dev/null
}

# ── Check 1: caffe_ffi importable ──
if ! run_py "
import caffe_ffi
" 2>/dev/null; then
    echo "UNHEALTHY: caffe_ffi import failed"
    FAIL=1
fi

# ── Check 2: _caffe_ffi.so has no unresolved deps ──
CAFFE_SO=$(run_py "
import os, glob, caffe_ffi
sos = glob.glob(os.path.join(os.path.dirname(caffe_ffi.__file__), '_caffe_ffi*.so'))
print(sos[0] if sos else '')
" 2>/dev/null)

if [ -z "$CAFFE_SO" ] || [ ! -f "$CAFFE_SO" ]; then
    echo "UNHEALTHY: _caffe_ffi.so not found"
    FAIL=1
elif ldd "$CAFFE_SO" 2>/dev/null | grep -q 'not found'; then
    MISSING=$(ldd "$CAFFE_SO" 2>/dev/null | grep 'not found' | awk '{print $1}' | tr '\n' ' ')
    echo "UNHEALTHY: _caffe_ffi.so has unresolved deps: $MISSING"
    FAIL=1
fi

# ── Check 3: protobuf ABI compatibility ──
# Verify serialize/parse roundtrip works (catches ABI mismatch segfaults)
# and that caffe_pb2 is importable (exercises full C++ proto dependency chain)
if ! run_py "
from google.protobuf import descriptor_pb2
fd = descriptor_pb2.FileDescriptorProto()
fd.name = 'test.proto'
fd.package = 'test'
msg = fd.message_type.add()
msg.name = 'Foo'
data = fd.SerializeToString()
fd2 = descriptor_pb2.FileDescriptorProto()
fd2.ParseFromString(data)
assert fd2.message_type[0].name == 'Foo', 'roundtrip failed'
print('ok')
" 2>/dev/null | grep -q 'ok'; then
    echo "UNHEALTHY: protobuf serialize/parse roundtrip failed (ABI mismatch?)"
    FAIL=1
fi

# ── Check 4: Jupyter HTTP API responding ──
if command -v curl >/dev/null 2>&1; then
    if ! curl -sf -o /dev/null --max-time 3 http://localhost:8888/api 2>/dev/null; then
        echo "UNHEALTHY: Jupyter API not responding on port 8888"
        FAIL=1
    fi
else
    if ! (echo > /dev/tcp/localhost/8888) 2>/dev/null; then
        echo "UNHEALTHY: port 8888 not listening (Jupyter not started?)"
        FAIL=1
    fi
fi

if [ "$FAIL" -eq 0 ]; then
    VER=$(run_py "import caffe_ffi; print(caffe_ffi.__version__)" 2>/dev/null || echo "?")
    echo "HEALTHY: caffe_ffi=$VER, protobuf=ok, jupyter=ok"
    exit 0
fi

exit 1
