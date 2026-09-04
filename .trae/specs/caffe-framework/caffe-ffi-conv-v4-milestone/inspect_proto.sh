#!/bin/bash
echo "=== head ==="
head -30 /root/.caffe_test_data/models/resnet101.prototxt
echo "=== conv count ==="
grep -c 'name: "conv' /root/.caffe_test_data/models/resnet101.prototxt
echo "=== res count ==="
grep -c 'name: "res' /root/.caffe_test_data/models/resnet101.prototxt
echo "=== last layers ==="
grep -E 'name:|type:|top:' /root/.caffe_test_data/models/resnet101.prototxt | tail -20
echo "=== input dims ==="
grep -E 'input:|input_dim:' /root/.caffe_test_data/models/resnet101.prototxt | head -10
echo "=== host network test ==="
timeout 15 python3 -c "import socket; s=socket.create_connection(('dl.caffe.berkeleyvision.org',80),timeout=10); s.close(); print('host reachable')" 2>&1 || echo "host not reachable"