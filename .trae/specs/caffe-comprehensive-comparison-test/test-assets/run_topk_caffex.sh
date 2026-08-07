#!/bin/bash
# 在 origin-runtime 容器中运行 Top-K 分类一致性分析（caffex）
set -e
SRC=/tmp/assets
docker run --rm \
  -v /mnt/d/spaces/SpecWeave/.trae/specs/caffe-comprehensive-comparison-test/test-assets:${SRC} \
  -e PYTHONPATH=/workspace/caffex/python \
  -e LD_LIBRARY_PATH=/workspace/caffex/build/lib:/usr/lib/x86_64-linux-gnu \
  -e NET_NAME=${NET_NAME:-inceptionv1} \
  caffe-cpu:origin-runtime bash -lc \
  "python3 ${SRC}/topk_analysis.py ${SRC}/models ${SRC}/results/topk_input.npy /tmp/topk_caffex.json caffex >/dev/null 2>&1; echo '=== RESULT ==='; cat /tmp/topk_caffex.json; cp /tmp/topk_caffex.json ${SRC}/results/topk_caffex.json"