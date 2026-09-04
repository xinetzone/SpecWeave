#!/bin/bash
# ──────────────────────────────────────────────────────────────────────
# caffe-ffi Conv层 v4 优化：一键编译 + 基准测试脚本
# ──────────────────────────────────────────────────────────────────────
# 并行策略：沿输出通道(M)维度分块并行
#   - 最小分块 32 通道（保证 OpenBLAS SGEMM 效率）
#   - 每个线程处理一个通道块：GEMM+Bias 融合（消除中间屏障）
#   - 自适应线程数：num_chunks = min(max_threads, M/32)
#   - im2col 单线程执行（内存绑定，<5%计算量）
# 推荐环境变量（本脚本自动导出）：
#   - OMP_NUM_THREADS=4        （最优性价比，可通过环境变量覆盖）
#   - OPENBLAS_NUM_THREADS=1   （BLAS单线程，避免过度订阅）
#   - OMP_WAIT_POLICY=PASSIVE  （等待线程让出CPU，避免自旋浪费）
#   - KMP_DUPLICATE_LIB_OK=TRUE（避免OpenMP运行时冲突）
#   - 不设置 OMP_PROC_BIND     （混合P/E核CPU上OS调度更优）
# ──────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAFFE_FFI_DIR="/SpecWeave/projects/xuanspace/libs/caffe-ffi"

# ── 全局环境变量（关键：确保所有子进程继承正确配置）──
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-PASSIVE}"
export KMP_DUPLICATE_LIB_OK=TRUE
export GLOG_minloglevel="${GLOG_minloglevel:-2}"

echo "============================================"
echo " caffe-ffi Conv层 v4 优化：编译+基准测试"
echo "============================================"
echo " 环境配置："
echo "   OMP_NUM_THREADS      = $OMP_NUM_THREADS"
echo "   OPENBLAS_NUM_THREADS = $OPENBLAS_NUM_THREADS"
echo "   OMP_WAIT_POLICY      = $OMP_WAIT_POLICY"
echo "   OMP_PROC_BIND        = ${OMP_PROC_BIND:-<not set, OS default>}"
echo "============================================"

# ── Step 1: 编译 ──
echo ""
echo "[1/5] 编译 caffe-ffi (Conv v4)..."
cd "$CAFFE_FFI_DIR/build"
cmake --build . -j$(nproc) 2>&1 | tail -5
cp python/caffe_ffi/_caffe_ffi.so ../python/caffe_ffi/_caffe_ffi.so
echo "  ✓ 编译完成"

# ── Step 2: 下载ResNet-101 prototxt（如果不存在）──
echo ""
echo "[2/5] 检查模型文件..."
if [ ! -f /root/.caffe_test_data/models/resnet101.prototxt ]; then
    echo "  下载 ResNet-101 prototxt..."
    curl -sL -o /root/.caffe_test_data/models/resnet101.prototxt \
        "https://raw.githubusercontent.com/KaimingHe/deep-residual-networks/master/prototxt/ResNet-101-deploy.prototxt"
fi
echo "  ✓ 模型文件就绪 (ResNet-50, InceptionV1, ResNet-101)"

# ── Step 3: 正确性验证 ──
echo ""
echo "[3/5] 正确性验证 (OMP=1 vs OMP=4, batch=1)..."
python3 "$SCRIPT_DIR/bench_v5_extreme.py" --correctness-only 2>&1
echo "  ✓ 正确性验证完成"

# ── Step 4: 推荐配置快速测试 ──
echo ""
echo "[4/5] 推荐配置快速测试 (OMP=$OMP_NUM_THREADS, BLAS=$OPENBLAS_NUM_THREADS, batch=1)..."
python3 -c "
import os, time, numpy as np, caffe_ffi

models = [
    ('ResNet-50', '/root/.caffe_test_data/models/resnet50.prototxt',
     '/root/.caffe_test_data/models/resnet50.caffemodel', [103.939,116.779,123.68]),
    ('InceptionV1', '/root/.caffe_test_data/models/inceptionv1.prototxt',
     '/root/.caffe_test_data/models/inceptionv1.caffemodel', [104.,117.,123.]),
    ('ResNet-101', '/root/.caffe_test_data/models/resnet101.prototxt',
     None, [103.939,116.779,123.68]),
]

for model_name, proto, model, mean in models:
    net = caffe_ffi.read_net(proto, model)
    inp = net.blob_by_name('data')
    data = np.random.rand(1,3,224,224).astype(np.float32)
    data -= np.array(mean,dtype=np.float32).reshape(1,3,1,1)
    inp.data = data
    for _ in range(5): net.forward()
    t0=time.perf_counter()
    for _ in range(15): net.forward()
    t1=time.perf_counter()
    avg = (t1-t0)/15*1000
    print(f'  {model_name:12s}: {avg:7.1f} ms/image, {1000/avg:6.2f} FPS')
"
echo "  ✓ 推荐配置测试完成"

# ── Step 5: 完整batch=1 vs batch=16极端对比测试 ──
echo ""
echo "[5/5] 运行 batch=1 vs batch=16 极端对比测试..."
python3 "$SCRIPT_DIR/bench_v5_extreme.py" 2>&1
echo ""
echo "============================================"
echo " 编译和测试完成！"
echo ""
echo " 最佳配置建议："
echo "   export OMP_NUM_THREADS=4"
echo "   export OPENBLAS_NUM_THREADS=1"
echo "   export OMP_WAIT_POLICY=PASSIVE"
echo "   # 不要设置 OMP_PROC_BIND（混合P/E核让OS调度）"
echo "============================================"
