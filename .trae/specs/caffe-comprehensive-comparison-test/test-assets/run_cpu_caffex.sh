#!/bin/bash
# 在 origin-runtime 容器中运行 CPU 占用率测量（较长采样窗口）
set -e
SRC=/tmp/assets
docker run --rm \
  -v /mnt/d/spaces/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets:${SRC} \
  -e PYTHONPATH=/workspace/caffex/python \
  -e LD_LIBRARY_PATH=/workspace/caffex/build/lib:/usr/lib/x86_64-linux-gnu \
  caffe-cpu:origin-runtime bash -lc \
  "python3 ${SRC}/cpu_monitor.py ${SRC}/benchmark_ops.py /tmp/cpu_caffex.json 800 >/dev/null 2>&1; echo '=== RESULT ==='; cat /tmp/cpu_caffex.json; cp /tmp/cpu_caffex.json ${SRC}/results/cpu_caffex.json"