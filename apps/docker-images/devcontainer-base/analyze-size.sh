#!/bin/bash
echo "=== IS CUDA PYTHON PACKAGE USED BY TORCH? ==="
python -c "import torch; print(torch.__version__)" 2>&1
echo "Check if cuda package is imported:"
python -c "import sys; mods_before = set(sys.modules.keys()); import torch; new_mods = [m for m in sys.modules if m.startswith('cuda') and m not in mods_before]; print('cuda modules loaded:', new_mods)" 2>&1

echo ""
echo "=== DOES TRITON IMPORT USE PTXAS? ==="
grep -r "ptxas" /opt/conda/envs/main/lib/python3.14t/site-packages/triton/backends/nvidia/ --include="*.py" 2>/dev/null | head -5

echo ""
echo "=== DOES TORCH DLOPEN cusolverMg? ==="
grep -r "cusolverMg\|cusolvermg" /opt/conda/envs/main/lib/python3.14t/site-packages/torch/ --include="*.py" 2>/dev/null | head -5
grep -r "cusolverMg\|nvperf\|nvrtc\.alt" /opt/conda/envs/main/lib/python3.14t/site-packages/torch/lib/ 2>/dev/null | strings | head -10

echo ""
echo "=== CHECK STRIP SMALLER TORCH LIBS ==="
for f in /opt/conda/envs/main/lib/python3.14t/site-packages/torch/lib/libtorch_nvshmem.so /opt/conda/envs/main/lib/python3.14t/site-packages/torch/lib/libc10.so /opt/conda/envs/main/lib/python3.14t/site-packages/torch/lib/libc10_cuda.so; do
  cp "$f" /tmp/test_small.so
  before=$(ls -lh /tmp/test_small.so | awk '{print $5}')
  strip --strip-unneeded /tmp/test_small.so 2>/dev/null
  after=$(ls -lh /tmp/test_small.so | awk '{print $5}')
  echo "$(basename $f): $before -> $after"
  rm -f /tmp/test_small.so
done

echo ""
echo "=== TOTAL SIZE OF ALL .so FILES IN SITE-PACKAGES ==="
find /opt/conda/envs/main/lib/python3.14t/site-packages -name "*.so*" -not -type l -exec du -ch {} + 2>/dev/null | tail -1
