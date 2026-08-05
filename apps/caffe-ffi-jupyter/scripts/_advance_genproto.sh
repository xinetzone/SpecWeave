#!/bin/bash
# Install grpc_tools and regenerate caffe_pb2.py from updated proto
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
echo "=== Installing grpc_tools ==="
pip install grpcio-tools 2>&1 | tail -5
echo "=== Regenerating pb2 ==="
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi
python scripts/gen_proto.py 2>&1
echo "=== Verify new messages present ==="
python -c "
from caffe_ffi.caffe.proto import caffe_pb2
for name in ['l2_norm_param','instance_norm_param','margin_ranking_param','hinge_param']:
    assert hasattr(caffe_pb2.LayerParameter(), name), name + ' MISSING'
print('All 4 new param fields present in LayerParameter')
lp = caffe_pb2.LayerParameter()
lp.l2_norm_param.axis = 1
lp.l2_norm_param.eps = 1e-5
lp.instance_norm_param.affine = True
lp.margin_ranking_param.margin = 1.0
lp.hinge_param.norm = caffe_pb2.HingeParameter.L1
print('Serialization roundtrip OK')
" 2>&1
echo "=== done ==="