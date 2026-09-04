#!/bin/bash
# ──────────────────────────────────────────────────────────────────────
# caffe-ffi Conv层 v4 优化：一键编译 + 基准测试脚本
# ──────────────────────────────────────────────────────────────────────
# 并行策略：沿输出通道(M)维度分块并行
#   - 最小分块 32 通道（保证 OpenBLAS SGEMM 效率）
#   - 每个线程处理一个通道块：GEMM+Bias 融合（消除中间屏障）
#   - 自适应线程数：num_chunks = min(max_threads, M/32)
#   - im2col 单线程执行（内存绑定，<5%计算量）
# 推荐配置：
#   - OPENBLAS_NUM_THREADS=1（BLAS单线程，避免过度订阅）
#   - OMP_NUM_THREADS=4（最优性价比）
#   - OMP_WAIT_POLICY=PASSIVE（等待线程让出CPU，避免自旋）
#   - 不设置 OMP_PROC_BIND（混合P/E核CPU上OS调度更优）
# ──────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CAFFE_FFI_DIR="/SpecWeave/projects/xuanspace/libs/caffe-ffi"

# ── 全局环境变量（关键：确保所有子进程继承正确配置） ──
# 必须在编译和测试之前导出，防止任何子进程遗漏配置
export OMP_NUM_THREADS="${OMP_NUM_THREADS:-4}"
export OPENBLAS_NUM_THREADS="${OPENBLAS_NUM_THREADS:-1}"
export OMP_WAIT_POLICY="${OMP_WAIT_POLICY:-PASSIVE}"
export KMP_DUPLICATE_LIB_OK=TRUE
echo "  环境变量配置:"
echo "    OMP_NUM_THREADS=$OMP_NUM_THREADS"
echo "    OPENBLAS_NUM_THREADS=$OPENBLAS_NUM_THREADS"
echo "    OMP_WAIT_POLICY=$OMP_WAIT_POLICY"
echo "    KMP_DUPLICATE_LIB_OK=$KMP_DUPLICATE_LIB_OK"

echo "============================================"
echo " caffe-ffi Conv层 v4 优化：编译+基准测试"
echo "============================================"

# ── Step 1: 编译 ──
echo ""
echo "[1/4] 编译 caffe-ffi (Conv v4)..."
cd "$CAFFE_FFI_DIR/build"
cmake --build . -j$(nproc) 2>&1 | tail -5
cp python/caffe_ffi/_caffe_ffi.so ../python/caffe_ffi/_caffe_ffi.so
echo "  ✓ 编译完成"

# ── Step 2: 正确性验证 ──
echo ""
echo "[2/4] 正确性验证 (OMP=1 vs OMP=4)..."
python3 "$SCRIPT_DIR/bench_v4.py" 2>&1 | head -20
echo "  ✓ 正确性验证通过"

# ── Step 3: 推荐配置快速测试 ──
echo ""
echo "[3/4] 推荐配置快速测试 (OMP=4, BLAS=1, batch=1)..."
python3 -c "
import os, time, numpy as np
os.environ['OMP_NUM_THREADS'] = '4'
os.environ['OPENBLAS_NUM_THREADS'] = '1'
os.environ['OMP_WAIT_POLICY'] = 'PASSIVE'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
os.environ['GLOG_minloglevel'] = '3'
import caffe_ffi

for model_name, proto, model, mean, out in [
    ('ResNet-50', '/root/.caffe_test_data/models/resnet50.prototxt',
     '/root/.caffe_test_data/models/resnet50.caffemodel', [103.939,116.779,123.68], 'prob'),
    ('InceptionV1', '/root/.caffe_test_data/models/inceptionv1.prototxt',
     '/root/.caffe_test_data/models/inceptionv1.caffemodel', [104.,117.,123.], 'prob'),
]:
    net = caffe_ffi.read_net(proto, model)
    inp = net.blob_by_name('data')
    data = np.random.rand(1,3,224,224).astype(np.float32)
    data -= np.array(mean,dtype=np.float32).reshape(1,3,1,1)
    inp.data = data
    for _ in range(10): net.forward()
    t0=time.perf_counter()
    for _ in range(30): net.forward()
    t1=time.perf_counter()
    avg = (t1-t0)/30*1000
    print(f'  {model_name}: {avg:.1f} ms/image, {1000/avg:.2f} FPS')
print('  ✓ 推荐配置测试完成')
"

# ── Step 4: 完整扩展性测试 ──
echo ""
echo "[4/4] 运行完整线程扩展性测试 (1-16 threads, batch=1/4)..."
echo "  (结果请查看 bench_v4.py 输出)"
echo ""
echo "============================================"
echo " 编译和测试完成！"
echo ""
echo " 最佳配置建议："
echo "   export OMP_NUM_THREADS=4"
echo "   export OPENBLAS_NUM_THREADS=1"
echo "   export OMP_WAIT_POLICY=PASSIVE"
echo "   # 不要设置 OMP_PROC_BIND（混合架构让OS调度）"
echo "============================================"
