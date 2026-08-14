#!/bin/bash
# Run ALL Conv backward tests in Docker with enhanced logging + performance tracking
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi

CAFFE_FFI_DIR=/SpecWeave/projects/xuanspace/libs/caffe-ffi
cd "$CAFFE_FFI_DIR"

echo "=== 1. Ensure .so is in place ==="
BUILD_SO="build/python/caffe_ffi/_caffe_ffi.so"
PYTHON_SO="python/caffe_ffi/_caffe_ffi.so"
if [ -f "$BUILD_SO" ]; then
    cp "$BUILD_SO" "$PYTHON_SO"
fi
python -c "from caffe_ffi import _ffi_api; print('cpp_available:', _ffi_api.is_available())"

echo ""
echo "=== 2. Clean old perf CSV ==="
rm -f tests/python/.temp/perf_log_*.csv

echo ""
echo "=== 3. Run ALL Conv backward tests (with enhanced logging) ==="
cd tests/python
export CAFFE_FFI_PERF_GC_MODE=quick
export CAFFE_FFI_CPP_LOG_LEVEL=4
export CAFFE_FFI_LEAKCHECK_GC=quick
export KMP_DUPLICATE_LIB_OK=TRUE
export PYTHONUNBUFFERED=1
python -m pytest test_conv_backward.py -v --tb=long 2>&1 || true

echo ""
echo "=== 4. Performance analysis ==="
python3 << 'PYEOF'
import csv, glob, os
from pathlib import Path

temp_dir = Path("/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/.temp")
files = sorted(glob.glob(str(temp_dir / "perf_log_*.csv")), key=os.path.getmtime, reverse=True)
if not files:
    print("No perf CSV found!")
    exit(0)

csv_file = files[0]
print(f"Analyzing: {csv_file} ({os.path.getsize(csv_file)} bytes)")
print()

rows = []
with open(csv_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

if not rows:
    print("Empty CSV!")
    exit(0)

# Per-test total time (END entries only)
end_rows = [r for r in rows if r.get('operation') == 'END']
test_times = {}
for r in end_rows:
    key = f"{r.get('test_class', '')}::{r.get('test_name', '')}"
    elapsed = float(r.get('elapsed_ms', 0))
    test_times[key] = elapsed

sorted_tests = sorted(test_times.items(), key=lambda x: x[1], reverse=True)
total_end = sum(test_times.values())
print(f"Total test entries: {len(end_rows)}/{len(rows)}")
print(f"\nTop 15 slowest tests:")
print("-" * 110)
print(f"{'#':>3} | {'Test':90s} | {'Time(ms)':>10s}")
print("-" * 110)
for i, (name, t) in enumerate(sorted_tests[:15]):
    print(f"{i+1:3d} | {name[:90]:90s} | {t:10.2f}")
print(f"\nTotal traced time: {total_end:.2f} ms ({total_end/1000:.3f} s)")

# Time by class
print()
print("Time by test class:")
print("-" * 60)
class_times = {}
for r in end_rows:
    cls = r.get('test_class', 'unknown')
    class_times[cls] = class_times.get(cls, 0) + float(r.get('elapsed_ms', 0))
for cls, t in sorted(class_times.items(), key=lambda x: x[1], reverse=True):
    pct = 100 * t / total_end if total_end > 0 else 0
    print(f"  {cls:40s}: {t:10.2f} ms ({pct:5.1f}%)")
PYEOF

echo ""
echo "=== Done ==="
