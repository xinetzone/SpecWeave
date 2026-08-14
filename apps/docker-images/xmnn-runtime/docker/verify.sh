#!/bin/bash
set -euo pipefail

IMAGE="${1:?Usage: $0 <image:tag>}"

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

PASS=0
FAIL=0

pass() { echo -e "  ${GREEN}[PASS]${NC} $1"; PASS=$((PASS+1)); }
fail() { echo -e "  ${RED}[FAIL]${NC} $1"; FAIL=$((FAIL+1)); }

echo "============================================"
echo "Docker Red Lines Verification"
echo "Image: $IMAGE"
echo "============================================"
echo ""

# ---- R1: ldd 零 not found ----
echo "R1: ldd check (no missing dependencies)..."
TMPDIR=$(mktemp -d)
cat > "$TMPDIR/r1.py" << 'PYEOF'
import subprocess, sys, glob, site
sp = site.getsitepackages()[0]
missing = []
so_files = glob.glob(f"{sp}/**/*.so", recursive=True)
so_files += [f for f in glob.glob(f"{sp}/**/*.so.*", recursive=True) if '.so' in f]
for so in so_files:
    try:
        r = subprocess.run(["ldd", so], capture_output=True, text=True, timeout=10)
        for line in r.stdout.splitlines():
            if "not found" in line:
                missing.append(f"{so.split('/')[-1]}: {line.strip()}")
    except: pass
if missing:
    for m in missing: print(f"  {m}", file=sys.stderr)
    sys.exit(1)
print(f"  Checked {len(so_files)} .so files")
PYEOF
if docker run --rm -v "$TMPDIR:/tmp/test:ro" "$IMAGE" python /tmp/test/r1.py 2>/dev/null; then
    pass "R1: No missing shared library dependencies"
else
    fail "R1: Missing dependencies detected"
fi
rm -rf "$TMPDIR"

# ---- R2: 核心模块 import ----
echo "R2: Core module imports..."
TMPDIR=$(mktemp -d)
cat > "$TMPDIR/r2.py" << 'PYEOF'
import sys, importlib
modules = ["tvm", "vta", "xmnn"]
failed = []
for m in modules:
    try:
        importlib.import_module(m)
        print(f"  [OK] import {m}")
    except ImportError as e:
        failed.append(f"{m}: {e}")
if failed:
    for f in failed: print(f, file=sys.stderr)
    sys.exit(1)
PYEOF
if docker run --rm -v "$TMPDIR:/tmp/test:ro" "$IMAGE" python /tmp/test/r2.py 2>/dev/null; then
    pass "R2: All core modules (tvm, vta, xmnn) import successfully"
else
    fail "R2: Some core modules failed to import"
fi
rm -rf "$TMPDIR"

# ---- R3: 功能测试 ----
echo "R3: Functional test (TVM TE compute)..."
TMPDIR=$(mktemp -d)
cat > "$TMPDIR/r3.py" << 'PYEOF'
import sys
try:
    import tvm
    from tvm import te
    import numpy as np
    n = te.var("n")
    A = te.placeholder((n,), name="A")
    B = te.compute((n,), lambda i: A[i] * 2.0, name="B")
    s = te.create_schedule(B.op)
    mod = tvm.build(s, [A, B], "llvm")
    ctx = tvm.cpu(0)
    a = tvm.nd.array(np.array([1.0, 2.0, 3.0], dtype="float32"), ctx)
    b = tvm.nd.array(np.zeros(3, dtype="float32"), ctx)
    mod(a, b)
    result = b.numpy().tolist()
    expected = [2.0, 4.0, 6.0]
    assert result == expected, f"Expected {expected}, got {result}"
    print(f"  TE compute: [1,2,3] * 2 = {result}")
except Exception as e:
    print(f"FAIL: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc()
    sys.exit(1)
PYEOF
if docker run --rm -v "$TMPDIR:/tmp/test:ro" "$IMAGE" python /tmp/test/r3.py 2>/dev/null; then
    pass "R3: TVM TE functional compute test passed"
else
    fail "R3: Functional test failed"
fi
rm -rf "$TMPDIR"

# ---- R4: 非root用户运行 ----
echo "R4: Non-root user execution..."
TMPDIR=$(mktemp -d)
chmod 777 "$TMPDIR"
cat > "$TMPDIR/r4.py" << 'PYEOF'
import os, sys
if os.getuid() == 0:
    print("Still running as root!", file=sys.stderr)
    sys.exit(1)
with open("/workspace/_test_write", "w") as f:
    f.write("ok")
os.remove("/workspace/_test_write")
print(f"  Running as uid={os.getuid()}, write test OK")
PYEOF
if docker run --rm -u 1000:1000 -v "$TMPDIR:/workspace" -v "$TMPDIR:/tmp/test:ro" "$IMAGE" python /tmp/test/r4.py 2>/dev/null; then
    pass "R4: Non-root user can run and write to /workspace"
else
    fail "R4: Non-root execution failed"
fi
rm -rf "$TMPDIR"

# ---- R5: pip check ----
echo "R5: pip check (no dependency conflicts)..."
if docker run --rm "$IMAGE" pip check 2>&1 | grep -q "No broken requirements"; then
    pass "R5: No broken requirements (pip check)"
else
    PIP_OUT=$(docker run --rm "$IMAGE" pip check 2>&1 || true)
    if echo "$PIP_OUT" | grep -q "No broken requirements"; then
        pass "R5: No broken requirements (pip check)"
    else
        echo "  pip check output: $PIP_OUT"
        fail "R5: pip check found issues"
    fi
fi

# ---- 汇总 ----
echo ""
echo "============================================"
echo -e "Result: ${GREEN}${PASS} passed${NC}, ${RED}${FAIL} failed${NC}"
echo "============================================"

if [ $FAIL -gt 0 ]; then
    exit 1
fi
