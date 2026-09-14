#!/bin/bash
# ==============================================================================
# verify-wheel.sh — xmnn wheel 隔离验证（10 项）
#
# 与移植源的关键差异：验证在**临时 venv**（--system-site-packages）中进行，
# wheel 以 --no-deps --force-reinstall 装入 venv，结束即删除——base env 的源码
# 调试链路（PYTHONPATH=/workspace/...）零污染。
#
# 用法：
#   bash verify-wheel.sh [wheel 路径]
#   默认取 $DIST_DIR（/workspace/dist）下最新的 xmnn-*.whl
#
# 检查项：
#   1-3. import tvm / vta / xmnn
#   4.   _libs 目录（libtvm.so + libLLVM + 依赖库清单）
#   4b.  RPATH $ORIGIN（libtvm 自身必须带，其余库统计展示）
#   5.   干净环境 ctypes RTLD_GLOBAL 加载 libtvm.so
#   6.   tvm.build('llvm') 向量数值断言
#   7.   relay/std/prelude.rly 数据
#   8.   xmnn_bootstrap.pth 生效
#   9.   xmnn 数据三目录（autolibs/tools_cpp/fonts）
# 任一检查失败都计入 FAIL 并继续跑完全部项（不被 set -e 中止）；FAIL>0 → exit 1。
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DIST_DIR="${DIST_DIR:-/workspace/dist}"
BASE_PYTHON=/opt/conda/bin/python
VENV=/tmp/xmnn-verify-venv

# 干净环境：不继承任何指向源码树/build 树/conda lib 的路径。
# compose 为「源码调试态」注入了 PYTHONPATH=/workspace/npu_tvm/... 与
# TVM_LIBRARY_PATH=/workspace/npu_tvm/build；验证 wheel 自包含性时二者会让
# venv 重新命中挂载源码而非 wheel（tvm.__file__ 落回源码树），必须显式剥离，
# 让 venv python 只从 venv site-packages + wheel 自带 _libs（RPATH $ORIGIN、
# bootstrap .pth）解析——这正是交付给客户机的无源码环境语义。
unset LD_LIBRARY_PATH 2>/dev/null || true
unset PYTHONPATH 2>/dev/null || true
unset TVM_LIBRARY_PATH 2>/dev/null || true
export PATH="/opt/conda/bin:${PATH:-}"

WHL="${1:-$(ls -t "$DIST_DIR"/xmnn-*.whl 2>/dev/null | head -1 || true)}"
if [ -z "$WHL" ] || [ ! -f "$WHL" ]; then
    echo "❌ 未找到 wheel：$WHL"
    echo "   先执行 inv xmnn.wheel（默认产物目录 $DIST_DIR）"
    exit 1
fi

# ── TTY 颜色 ───────────────────────────────────────────────────────────
if [ -t 1 ]; then
    _GRN='\033[0;32m' _RED='\033[0;31m'
    _PASS="✅ PASS" _FAIL="❌ FAIL"
else
    _GRN='' _RED=''
    _PASS="PASS" _FAIL="FAIL"
fi

# ── 临时 venv 生命周期（结束必清理，任何退出路径都删）────────────────────
cleanup_venv() {
    rm -rf "$VENV"
}
trap cleanup_venv EXIT

echo "=========================================="
echo "  XMNN Wheel Verification (isolated venv)"
echo "=========================================="
echo "Python: $($BASE_PYTHON --version)"
echo "Wheel:  $WHL ($(du -h "$WHL" | cut -f1))"
echo ""

"$BASE_PYTHON" -m venv --system-site-packages "$VENV"
VENV_PY="$VENV/bin/python"
# 不升级 pip（基底 pip 可用即可），--no-deps 因为 19 依赖已在 base env
echo "=== Install wheel into isolated venv (--no-deps, deps from base env) ==="
"$VENV_PY" -m pip install --no-deps --force-reinstall "$WHL" 2>&1 | tail -5
echo ""

PASS=0
FAIL=0

# check <name> <command...>：捕获输出，失败计入 FAIL 但不中止脚本
check() {
    local name="$1"
    shift
    echo "─── Test: $name"
    if output=$("$@" 2>&1); then
        echo "$output"
        echo -e "${_GRN}${_PASS}${_RST}: $name"
        PASS=$((PASS+1))
    else
        echo "$output"
        echo -e "${_RED}${_FAIL}${_RST}: $name"
        FAIL=$((FAIL+1))
    fi
    echo ""
}

check "1. import tvm" "$VENV_PY" -c "import tvm; print('  tvm version:', tvm.__version__)"
check "2. import vta" "$VENV_PY" -c "import vta; print('  vta imported OK')"
check "3. import xmnn" "$VENV_PY" -c "
import xmnn
mods = [x for x in dir(xmnn) if not x.startswith('_')]
print('  xmnn modules:', mods[:15])
"
check "4. _libs directory check" "$VENV_PY" -c "
import os, tvm
libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), '../_libs'))
print('  _libs dir:', libs_dir)
assert os.path.isdir(libs_dir), '_libs directory not found'
files = sorted(os.listdir(libs_dir))
print('  Files:')
for f in files:
    fp = os.path.join(libs_dir, f)
    sz = os.path.getsize(fp)
    is_link = os.path.islink(fp)
    print(f'    {f} ({sz/1024/1024:.1f} MB){\" [symlink]\" if is_link else \"\"}')
assert 'libtvm.so' in files, 'libtvm.so missing!'
assert any('libLLVM' in f for f in files), 'libLLVM missing!'
print('  _libs directory OK; entries:', len(files))
"
check "4b. RPATH validation (libs use \$ORIGIN)" "$VENV_PY" -c "
import os, subprocess, tvm, glob
libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), '../_libs'))
print('  Checking RPATH for libs in:', libs_dir)

def get_rpath(path):
    try:
        result = subprocess.run(['readelf', '-d', path], capture_output=True, text=True, timeout=10)
        for line in result.stdout.split('\n'):
            if 'RPATH' in line or 'RUNPATH' in line:
                parts = line.split('[')
                if len(parts) >= 2:
                    return parts[1].split(']')[0]
        return None
    except Exception as e:
        return f'error: {e}'

# libtvm.so 自身必须带 \$ORIGIN（自包含硬要求）
libtvm = os.path.join(libs_dir, 'libtvm.so')
assert os.path.exists(libtvm), 'libtvm.so missing'
rpath = get_rpath(libtvm)
print(f'    libtvm.so RPATH: {rpath}')
assert rpath and '\$ORIGIN' in rpath, f'libtvm.so RPATH not \$ORIGIN: {rpath}'
print('    libtvm.so RPATH OK (\$ORIGIN)')

# 其余库统计展示（cp -L 单副本安装，patchelf 已统一设置）
rpath_ok = 0
rpath_warn = 0
for lib in sorted(glob.glob(os.path.join(libs_dir, '*.so*'))):
    if os.path.islink(lib) or os.path.basename(lib) == 'libtvm.so':
        continue
    r = get_rpath(lib)
    if r and '\$ORIGIN' in r:
        rpath_ok += 1
    else:
        rpath_warn += 1
        if rpath_warn <= 3:
            print(f'    WARNING: {os.path.basename(lib)} RPATH={r}')
print(f'  RPATH summary: {rpath_ok} other libs with \$ORIGIN, {rpath_warn} without (informational)')
print('  RPATH validation complete')
"
check "5. libtvm.so loading (clean environment, no LD_LIBRARY_PATH)" "$VENV_PY" -c "
import ctypes, os, tvm
libs_dir = os.path.normpath(os.path.join(os.path.dirname(tvm.__file__), '../_libs'))
libtvm = os.path.join(libs_dir, 'libtvm.so')
print('  Loading:', libtvm)
ctypes.CDLL(libtvm, mode=ctypes.RTLD_GLOBAL)
print('  libtvm.so loaded OK')
"
check "6. tvm.build(llvm) compute" "$VENV_PY" -c "
import tvm
from tvm import te
import numpy as np
n = 1024
A = te.placeholder((n,), name='A', dtype='float32')
B = te.compute((n,), lambda i: A[i] * 2.0, name='B')
s = te.create_schedule(B.op)
print('  Building with llvm target...')
f = tvm.build(s, [A, B], 'llvm', name='vec_double')
print('  Build OK, entry:', f.entry_name)
ctx = tvm.cpu(0)
a = tvm.nd.array(np.random.uniform(size=n).astype('float32'), ctx)
b = tvm.nd.array(np.zeros(n, dtype='float32'), ctx)
f(a, b)
np.testing.assert_allclose(b.asnumpy(), a.asnumpy() * 2.0, rtol=1e-5)
print('  Compute verification passed (A[i]*2 == B[i])')
"
check "7. relay/std data files" "$VENV_PY" -c "
import os, tvm
std_dir = os.path.join(os.path.dirname(tvm.__file__), 'relay', 'std')
print('  relay/std:', std_dir)
assert os.path.isdir(std_dir), 'relay/std missing'
files = os.listdir(std_dir)
for f in sorted(files):
    print('   ', f)
assert 'prelude.rly' in files, 'prelude.rly missing!'
print('  relay/std data OK')
"
check "8. bootstrap .pth file" "$VENV_PY" -c "
import os, site, sys
pth_found = False
for sp in site.getsitepackages():
    pth = os.path.join(sp, 'xmnn_bootstrap.pth')
    if os.path.exists(pth):
        print('  Found:', pth)
        pth_found = True
        break
for sp in sys.path:
    pth = os.path.join(sp, 'xmnn_bootstrap.pth')
    if os.path.exists(pth):
        print('  Found (sys.path):', pth)
        pth_found = True
        break
assert pth_found, 'xmnn_bootstrap.pth not found!'
print('  .pth bootstrap OK')
"
check "9. xmnn data directories (autolibs/tools_cpp/fonts)" "$VENV_PY" -c "
import os, xmnn
if hasattr(xmnn, '__path__'):
    xmnn_dir = xmnn.__path__[0]
else:
    xmnn_dir = os.path.dirname(xmnn.__file__)
print('  xmnn package dir:', xmnn_dir)

required = ['autolibs', 'tools_cpp', 'fonts']
missing = []
for name in required:
    d = os.path.join(xmnn_dir, name)
    if os.path.isdir(d):
        print(f'    {name}/: {len(os.listdir(d))} entries')
    else:
        missing.append(name)
        print(f'    {name}/: MISSING')

assert not missing, f'Missing directories: {missing}'
print('  xmnn data directories OK')
"

echo "=========================================="
echo "  SUMMARY: $PASS passed, $FAIL failed"
echo "  (venv $VENV will be removed automatically; base env untouched)"
echo "=========================================="

if [ "$FAIL" -gt 0 ]; then
    echo -e "${_RED}SOME TESTS FAILED!"
    exit 1
else
    echo -e "${_GRN}  🎉 ALL TESTS PASSED!"
    exit 0
fi
