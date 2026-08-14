#!/bin/bash
export KMP_DUPLICATE_LIB_OK=TRUE
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python

python << 'PYEOF'
import numpy as np
from caffe_ffi import Net
import textwrap

def _make_pool_prototxt(input_dims, kernel_size, stride=None, pad=0, pool="MAX"):
    dims_str = " ".join(str(d) for d in input_dims)
    ks_str = f"kernel_size: {kernel_size}"
    stride_str = f"\n    stride: {stride}" if stride is not None else ""
    pad_str = f"\n    pad: {pad}" if pad != 0 else ""
    return textwrap.dedent(f"""
        name: "test_pool_bw"
        input: "data"
        input_dim: {input_dims[0]}
        input_dim: {input_dims[1]}
        input_dim: {input_dims[2]}
        input_dim: {input_dims[3]}
        layer {{
          name: "pool"
          type: "Pooling"
          bottom: "data"
          top: "pool"
          pooling_param {{
            pool: {pool}
            {ks_str}{stride_str}{pad_str}
          }}
        }}
    """)

print("="*60)
print("Pooling output shape comparison (kernel=3, stride=2, pad=0, AVE)")
print("="*60)
for (H, W) in [(4,5), (5,5), (4,4), (3,3), (6,6)]:
    proto = _make_pool_prototxt((1,1,H,W), kernel_size=3, stride=2, pad=0, pool="AVE")
    net = Net(proto)
    x = np.zeros((1,1,H,W), dtype=np.float32)
    out = net.forward({"data": x})
    Ho_floor = (H-3)//2 + 1
    Wo_floor = (W-3)//2 + 1
    Ho_ceil = int(np.ceil((H-3)/2)) + 1
    Wo_ceil = int(np.ceil((W-3)/2)) + 1
    actual = out["pool"].shape[2:]
    print(f"  Input ({H},{W}): C++={actual}, floor=({Ho_floor},{Wo_floor}), ceil=({Ho_ceil},{Wo_ceil})")
PYEOF
