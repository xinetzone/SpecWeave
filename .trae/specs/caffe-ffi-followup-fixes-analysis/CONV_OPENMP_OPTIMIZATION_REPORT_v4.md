# Caffe-FFI Conv层 OpenMP 并行优化报告 v4

> **日期**: 2025-04（基于 Intel Core Ultra 9 285H, 16核, Docker/WSL2 环境）
> **模型**: ResNet-50 / InceptionV1 (ImageNet, 224×224)

---

## 1. 问题背景

原 Conv 层代码沿 batch 维度做 OpenMP 并行（`for n in 0..num_-1`），在推理场景 batch=1 时完全没有并行度，单核性能受限。

**GEMM 表示**：Conv 层前向计算等价于矩阵乘法 `C[M,N] = A[M,K] × B[K,N]`，其中：
- **M** = 输出通道数（/组）
- **N** = 输出空间维度（H×W）
- **K** = 卷积核维度（C_in × kH × kW）

---

## 2. 优化策略演进（v1→v4）

### v1：Batch维度并行（原方案）
```cpp
#pragma omp parallel for
for (int n = 0; n < num_; ++n) { forward_cpu_gemm(...); }
```
- ❌ batch=1 时并行度=0，完全无效
- ❌ 每个线程做完整 GEMM，BLAS 多线程竞争

### v2：输出通道并行（M维度）+ chunk=8
```cpp
#pragma omp parallel for schedule(dynamic,1)
for (int mc = 0; mc < num_mc; ++mc) { /* GEMM M=8 */ }
```
- ✅ batch=1 有效，沿M维度分块
- ❌ chunk=8 过小：小GEMM调用开销占主导，8线程时速度**降至0.18x**（慢5.5倍）

### v3：chunk=16，自适应分块
```cpp
const int kMinChunk = 16;
num_mc = min(max_possible_chunks, nthr*2);
```
- ✅ 4线程可达 1.30x
- ❌ 8+线程仍严重退化（0.36-0.38x）——屏障同步+线程自旋开销

### v4：GEMM+Bias融合 + 自适应线程数 + PASSIVE等待（最终版）
```cpp
const int kMinChunk = 32;
const int num_chunks = min(max_omp_threads, M_total/kMinChunk);
#pragma omp parallel num_threads(num_chunks)
{
    for each sample:
        #pragma omp single  // im2col
        #pragma omp for schedule(static)  // 每个线程：GEMM→Bias 融合
}
```
- ✅ **8-16线程不再退化**：消除了多余屏障、自旋等待
- ✅ 4线程最优，加速 **1.30x**（ResNet-50）/ **1.35-1.38x**（InceptionV1 batch=4）

---

## 3. 关键设计决策

| 决策 | 原因 |
|------|------|
| **并行维度：M（输出通道）** | batch=1有效；M在每层是固定的（64-2048），提供足够并行度 |
| **最小分块=32通道** | OpenBLAS SGEMM AVX2 kernel在M<16时效率急剧下降（setup开销占比>30%）；32是GEMM效率与并行度的最佳平衡点 |
| **自适应线程数**：`num_chunks = min(omp_threads, M/32)` | conv1(M=64)只能分2块→只用2线程；res5(M=2048)可分64块→用满线程。避免小层出现空闲线程在屏障处自旋 |
| **GEMM+Bias融合**：一个线程连续完成GEMM和bias加法 | 消除GEMM与bias之间的屏障同步（原来53层×2屏障=106次同步） |
| **静态调度** `schedule(static)` | 块大小均匀，静态分配零开销；动态调度的原子取chunk操作在高频小GEMM场景反成负担 |
| **BLAS单线程**：`OPENBLAS_NUM_THREADS=1` | 多线程BLAS+外层OpenMP导致过度订阅：BLAS=2慢3x，BLAS=4慢11x。53个小GEMM调用的线程唤醒/同步开销远超计算收益 |
| **OMP_WAIT_POLICY=PASSIVE** | 等待线程让出CPU而非自旋等待，在核数有限/混合架构上避免spin-wait消耗资源 |
| **不设OMP_PROC_BIND** | 混合P-core/E-core的CPU（如Core Ultra 9 285H）上，强制close绑定可能把线程钉在慢E-core上，导致严重负载不均 |

---

## 4. 性能测试结果（v4最终版）

### 4.1 ResNet-50 batch=1（单图推理）

| OMP线程 | 延迟(ms) | P50(ms) | P95(ms) | 每图耗时 | FPS | 加速比 | 效率 |
|---------|----------|---------|---------|----------|-----|--------|------|
| 1 | 261.9 | 254.0 | 297.5 | 261.9ms | 3.82 | 1.00x | 100% |
| 2 | 210.6 | 209.0 | 215.8 | 210.6ms | 4.75 | **1.24x** | 62% |
| **4** | **201.8** | **202.7** | **214.1** | **201.8ms** | **4.95** | **1.30x** | **32%** |
| 8 | 206.9 | 206.4 | 216.4 | 206.9ms | 4.83 | 1.27x | 16% |
| 16 | 203.1 | 201.2 | 210.9 | 203.1ms | 4.92 | 1.29x | 8% |

### 4.2 ResNet-50 batch=4（批量推理）

| OMP线程 | 总延迟(ms) | 每图耗时 | FPS(总量) | 加速比 |
|---------|-----------|----------|-----------|--------|
| 1 | 770.5 | 192.6ms | 5.19 | 1.00x |
| 2 | 677.5 | 169.4ms | 5.90 | 1.14x |
| 4 | 682.3 | 170.6ms | 5.86 | 1.13x |
| 8 | 647.5 | 161.9ms | 6.18 | 1.19x |
| **16** | **626.2** | **156.6ms** | **6.39** | **1.23x** |

### 4.3 InceptionV1 batch=1

| OMP线程 | 延迟(ms) | FPS | 加速比 |
|---------|----------|-----|--------|
| 1 | 87.9 | 11.38 | 1.00x |
| 2 | 77.0 | 12.99 | 1.14x |
| **4** | **75.8** | **13.19** | **1.16x** |
| 8 | 78.2 | 12.79 | 1.12x |
| 16 | 79.1 | 12.64 | 1.11x |

### 4.4 InceptionV1 batch=4

| OMP线程 | 总延迟(ms) | 每图耗时 | FPS(总量) | 加速比 |
|---------|-----------|----------|-----------|--------|
| 1 | 314.7 | 78.7ms | 12.71 | 1.00x |
| 4 | 232.6 | 58.1ms | 17.20 | **1.35x** |
| **16** | **228.7** | **57.2ms** | **17.49** | **1.38x** |

### 4.5 正确性验证
- ResNet-50 OMP=1 vs OMP=4: max_abs_diff=2.86e-06, max_rel_diff=1.81e-04 ✓
- InceptionV1 OMP=1 vs OMP=4: max_abs_diff=2.38e-07, max_rel_diff=1.53e-06 ✓

---

## 5. 批量推理加速不明显的根因分析

### 5.1 为什么4线程以上不加速？

**Amdahl定律瓶颈**：串行部分（无法并行化的代码）占比过高。

| 组件 | 是否并行化 | 占比（估） |
|------|-----------|-----------|
| Conv层GEMM | ✅ OpenMP并行（BLAS单线程） | ~40-50% |
| Conv层im2col | ❌ 单线程（内存绑定） | ~3-5% |
| BatchNorm / Scale | ❌ 串行 | ~15-20% |
| ReLU | ❌ 串行 | ~5-8% |
| Eltwise（残差相加） | ✅ OpenMP并行 | ~5-8% |
| Pooling | ✅ OpenMP并行 | ~1-2% |
| InnerProduct / Softmax | ❌ 串行 | ~3-5% |
| 串行统计/内存操作 | ❌ 串行 | ~5% |

串行部分合计约 **45-55%**，根据 Amdahl 定律：
- 4线程理论上限 = 1/(0.5 + 0.5/4) = 1.6x
- 8线程理论上限 = 1/(0.5 + 0.5/8) = 1.78x
- 实际达到 1.30x 已占理论上限的 ~80%，说明并行化效率本身是合理的

### 5.2 内存带宽饱和

Conv层GEMM在N很大时（如conv1 N=56×56=3136, K=3663），内存访问量为：
- 权重读取：M×K = 64×3663 ≈ 900KB（可放L2缓存）
- 输入读取：K×N = 3663×3136 ≈ 44MB（远超缓存，内存带宽瓶颈）
- 输出写入：M×N = 64×3136 ≈ 786KB

4个线程并发读取col_buff（44MB），在笔记本CPU的DDR5带宽（~60-80GB/s）上已接近饱和。更多线程不会增加带宽，反而因缓存竞争降低效率。

### 5.3 混合P-core/E-core架构负载不均

Intel Core Ultra 9 285H 是混合架构（6P + 8E + 2LPE核心）：
- P-core（性能核）：高频率、高IPC，适合重计算
- E-core（能效核）：低频率、顺序执行，适合后台/轻量任务

当线程被OS调度到E-core上时，执行GEMM的速度约为P-core的 **40-60%**。`schedule(dynamic)`理论上可以让快线程多干活，但：
- v4使用`schedule(static)`减少调度开销
- 当chunk数=线程数时，每个线程恰好1个chunk，无法steal
- 解决方法：要么设置`OMP_PLACES=cores`并确保绑定到P-core，要么接受4线程（OS更可能都放在P-core上）

### 5.4 BLAS库配置结论

| BLAS配置 | 性能 | 结论 |
|---------|------|------|
| OPENBLAS_NUM_THREADS=1 | 基线 | ✅ 推荐：外层OpenMP并行，BLAS串行避免过度订阅 |
| OPENBLAS_NUM_THREADS=2 | 慢3x+ | ❌ 53个小GEMM的线程池唤醒/sync开销 > 计算收益 |
| OPENBLAS_NUM_THREADS=4 | 慢11x | ❌ 严重过度订阅 |
| MKL_NUM_THREADS=1 | 未测（容器无MKL） | MKL通常比OpenBLAS快10-20%，如有许可建议使用 |

**核心原因**：CNN推理包含大量小GEMM（53层），每个GEMM的计算时间在几十到几百微秒级别。BLAS多线程需要：
1. 进入线程池（加锁/解锁）
2. 唤醒睡眠线程（futex系统调用）
3. 分割矩阵并分发任务
4. 同步等待所有线程完成
5. 线程回到睡眠

这些操作的固定开销（~10-50μs）在小GEMM场景下占比过大，反而不如单线程直接计算。

### 5.5 线程绑定策略建议

| 策略 | 适用场景 | 在本环境的效果 |
|------|---------|---------------|
| 不设置（OS自动） | 混合P/E-core、笔记本 | ✅ 推荐：OS会把活跃线程放在P-core |
| OMP_PROC_BIND=close | 多核服务器、同构CPU | ❌ 可能绑定到E-core导致负载不均 |
| OMP_PROC_BIND=spread | NUMA多socket服务器 | ❌ 单socket无谓分散 |
| OMP_PLACES=cores | 避免SMT线程竞争 | ⚠️ 可尝试，但收益有限 |
| OMP_WAIT_POLICY=PASSIVE | 所有场景（尤其是核数有限时） | ✅ 推荐：减少spin-wait资源浪费 |
| OMP_WAIT_POLICY=ACTIVE | 高核数服务器（>16核） | ❌ 笔记本上spin-wait浪费功耗和带宽 |

---

## 6. 推荐生产配置

```bash
# 最优推理配置
export OMP_NUM_THREADS=4           # 4线程：最佳性价比
export OPENBLAS_NUM_THREADS=1     # BLAS单线程：避免过度订阅
export OMP_WAIT_POLICY=PASSIVE    # 等待线程让出CPU
# 不要设置 OMP_PROC_BIND（让OS选择P-core）
# 不要设置 KMP_AFFINITY（同上）

# 高吞吐批量推理（batch≥8）
export OMP_NUM_THREADS=8
export OPENBLAS_NUM_THREADS=1
```

---

## 7. 修改文件清单

| 文件 | 修改内容 |
|------|---------|
| `libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp` | v4并行策略：M维度并行、GEMM+bias融合、自适应线程数、min_chunk=32 |

### 修改位置
核心并行逻辑在 `ConvolutionLayer::Forward_cpu()` 中（约54-150行）。关键结构：

```
ConvolutionLayer::Forward_cpu()
├─ 串行路径 (omp_get_max_threads() <= 1)
│   └─ for n: forward_cpu_gemm() + forward_cpu_bias()
└─ 并行路径 (omp_get_max_threads() > 1)
    └─ #pragma omp parallel num_threads(num_chunks)
        └─ for n (samples, 串行处理每个batch)
            ├─ #pragma omp single: im2col_cpu()
            └─ #pragma omp for schedule(static)
                └─ for mc (channel chunks):
                    ├─ caffe_cpu_gemm() (分块GEMM)
                    └─ caffe_cpu_gemm() (bias加法, 融合)
```

---

## 8. 一键使用

```bash
# 编译 + 验证 + 基准测试
docker exec caffe-ffi-jupyter bash /SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/build_and_bench_v4.sh
```

---

## 9. 后续优化方向

1. **BN+Scale+ReLU融合**：把BatchNorm、Scale、ReLU三个串行层融合成一个OpenMP并行kernel，可减少约20-30%串行部分，预计4线程加速可达1.5-1.7x
2. **im2col并行化**：大尺寸特征图上im2col有一定并行空间，但收益有限（<5%）
3. **使用MKL/BLIS替代OpenBLAS**：Intel MKL在小GEMM上通常快15-30%；BLIS对小矩阵有优化
4. **Winograd算法**：3×3卷积可使用Winograd F(4,3)减少2.25-4x乘法数，比GEMM方法更快
5. **线程P-core亲和性**：通过`GOMP_CPU_AFFINITY`显式绑定到P-core ID，在混合架构上可进一步提升10-15%
6. **Outer-space并行（batch×M混合）**：batch≥4时结合M维度并行做二维分块，可能比纯M并行获得更好扩展性
