#!/bin/bash
# Verify the regenerated pb2 contains the 4 new param fields
set -e
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi
python - <<'PYEOF'
import sys
sys.path.insert(0, "python")
from caffe_ffi.caffe.proto import caffe_pb2
lp = caffe_pb2.LayerParameter()
for name in ["l2_norm_param", "instance_norm_param", "margin_ranking_param", "hinge_param"]:
    ok = hasattr(lp, name)
    print(name, "PRESENT" if ok else "MISSING")
    assert ok, name + " MISSING"
# Roundtrip
lp.l2_norm_param.axis = 1
lp.l2_norm_param.eps = 1e-5
lp.instance_norm_param.affine = True
lp.instance_norm_param.eps = 1e-5
lp.margin_ranking_param.margin = 1.0
lp.margin_ranking_param.sign = 1
lp.hinge_param.norm = caffe_pb2.HingeParameter.L1
lp.hinge_param.axis = 1
data = lp.SerializeToString()
lp2 = caffe_pb2.LayerParameter()
lp2.ParseFromString(data)
assert lp2.l2_norm_param.axis == 1
assert lp2.instance_norm_param.affine is True
assert lp2.margin_ranking_param.margin == 1.0
assert lp2.hinge_param.norm == caffe_pb2.HingeParameter.L1
print("Serialization roundtrip OK")
PYEOF