#!/bin/bash
export KMP_DUPLICATE_LIB_OK=TRUE
source /opt/conda/etc/profile.d/conda.sh
conda activate caffe-ffi
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python

python << 'PYEOF'
import numpy as np

def pool_out_size(H, W, kH, kW, sH, sW, pH, pW, ceil_mode=False):
    if ceil_mode:
        Ho = int(np.ceil(float(H + 2*pH - kH)/sH)) + 1
        Wo = int(np.ceil(float(W + 2*pW - kW)/sW)) + 1
    else:
        Ho = int(np.floor(float(H + 2*pH - kH)/sH)) + 1
        Wo = int(np.floor(float(W + 2*pW - kW)/sW)) + 1
    if pH > 0 or pW > 0:
        if (Ho-1)*sH >= H + pH: Ho -= 1
        if (Wo-1)*sW >= W + pW: Wo -= 1
    return Ho, Wo

def pooling_backward_np(dy, x, kernel_size, stride=None, pad=0,
                        pool_type='MAX', ceil_mode=False, global_pooling=False):
    N, C, H, W = x.shape
    if global_pooling:
        kH, kW = H, W
        stride_h, stride_w = 1, 1
        pad_h, pad_w = 0, 0
    else:
        if isinstance(kernel_size, int):
            kH = kW = kernel_size
        else:
            kH, kW = kernel_size
        if stride is None:
            stride = kernel_size
        if isinstance(stride, int):
            stride_h = stride_w = stride
        else:
            stride_h, stride_w = stride
        if isinstance(pad, int):
            pad_h = pad_w = pad
        else:
            pad_h, pad_w = pad

    Ho, Wo = pool_out_size(H, W, kH, kW, stride_h, stride_w, pad_h, pad_w, ceil_mode)
    print(f"  H_out={Ho}, W_out={Wo}")
    
    dx = np.zeros_like(x, dtype=np.float64)
    dy64 = dy.astype(np.float64)
    x64 = x.astype(np.float64)

    for n in range(N):
        for c in range(C):
            for ph in range(Ho):
                for pw in range(Wo):
                    hstart = ph * stride_h - pad_h
                    wstart = pw * stride_w - pad_w
                    hend = min(hstart + kH, H)
                    wend = min(wstart + kW, W)
                    hstart = max(hstart, 0)
                    wstart = max(wstart, 0)
                    if hend <= hstart or wend <= wstart:
                        continue
                    pool_size = (hend - hstart) * (wend - wstart)
                    dyi = dy64[n, c, ph, pw]
                    print(f"  window ph={ph},pw={pw}: h=[{hstart},{hend}), w=[{wstart},{wend}), pool_size={pool_size}, dy={dyi}")
                    if pool_type == 'AVE':
                        scale = dyi / pool_size if pool_size > 0 else 0.0
                        dx[n, c, hstart:hend, wstart:wend] += scale
    return dx.astype(np.float32)

# 失败测试用例：NCHW=(1,1,4,5), kernel=3, stride=2, pad=0, AVE
# C++ CEIL模式输出是(2,2)，而非floor的(1,2)
N, C, H, W = 1, 1, 4, 5
x = np.zeros((N, C, H, W), dtype=np.float32)
print("=== CEIL mode (C++ default) ===")
# dy for CEIL: (2,2) output
dy_ceil = np.array([[[[9.0, 9.0], [9.0, 9.0]]]], dtype=np.float32)
print(f"dy shape: {dy_ceil.shape}")
dx_ceil = pooling_backward_np(dy_ceil, x, kernel_size=3, stride=2, pad=0, pool_type='AVE', ceil_mode=True)
print(f"dx shape: {dx_ceil.shape}")
print("dx:")
print(dx_ceil[0,0])
print()

# 验证重叠区域
print("Overlap check for CEIL mode with dy=9 for all windows:")
print("  (0:3,0:3) → only ph=0,pw=0 → 9/9=1.0")
print("  (0:3,2:5) → ph=0,pw=1 → 9/9=1.0")  
print("  (2:4,0:3) → ph=1,pw=0 → 9/(2*3)=9/6=1.5")
print("  (2:4,2:5) → ph=1,pw=1 → 9/(2*3)=1.5")
print("  overlap (0:3,2:3): ph=0,pw=1 only? No, (2:3,2:3) also gets ph=1,pw=1 → 1.0+1.5=2.5")
PYEOF
