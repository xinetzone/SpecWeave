import numpy as np
from caffe_ffi import Net
import textwrap

def _make_pool_prototxt(input_dims, kernel_size, stride=None, pad=0, pool='MAX'):
    dims_str = " ".join(str(d) for d in input_dims)
    if isinstance(kernel_size, int):
        ks_str = f"kernel_size: {kernel_size}"
    if stride is None:
        stride_str = ""
    elif isinstance(stride, int):
        stride_str = f"\n    stride: {stride}"
    pad_str = ""
    if isinstance(pad, int) and pad != 0:
        pad_str = f"\n    pad: {pad}"
    return textwrap.dedent(f"""\
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

# 测试用例中的配置：NCHW=(1,1,4,5), kernel=3, stride=2, pad=0, AVE
N, C, H, W = 1, 1, 4, 5
proto = _make_pool_prototxt((N,C,H,W), kernel_size=3, stride=2, pad=0, pool='AVE')
net = Net(proto)
x = np.zeros((N, C, H, W), dtype=np.float32)
out = net.forward({"data": x})
print("="*60)
print(f"Input shape: {x.shape}")
print(f"Pool output shape: {out['pool'].shape}")
print(f"Expected (numpy floor mode): H_out=floor(({H}-3)/2)+1={(H-3)//2+1}, W_out=floor(({W}-3)/2)+1={(W-3)//2+1}")
print("="*60)

# 测试几种输入尺寸
for (H, W) in [(4,5), (5,5), (4,4), (3,3), (6,6)]:
    proto = _make_pool_prototxt((1,1,H,W), kernel_size=3, stride=2, pad=0, pool='AVE')
    net = Net(proto)
    x = np.zeros((1,1,H,W), dtype=np.float32)
    out = net.forward({"data": x})
    Ho_floor = (H-3)//2 + 1
    Wo_floor = (W-3)//2 + 1
    Ho_ceil = int(np.ceil((H-3)/2)) + 1
    Wo_ceil = int(np.ceil((W-3)/2)) + 1
    print(f"Input ({H},{W}): C++ output {out['pool'].shape[2:]}, floor=({Ho_floor},{Wo_floor}), ceil=({Ho_ceil},{Wo_ceil})")
