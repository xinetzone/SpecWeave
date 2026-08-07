#!/usr/bin/env python3
# 生成跨实现共享的固定输入（0-255 uint8，seed=42）
import os, sys
import numpy as np
out = sys.argv[1] if len(sys.argv) > 1 else "/tmp/topk_input.npy"
rng = np.random.RandomState(42)
data = rng.randint(0, 256, size=(1, 3, 224, 224)).astype(np.uint8)
np.save(out, data)
print("saved", out, data.shape)