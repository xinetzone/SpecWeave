# OpenMP 性能分析与 Conv 层 GEMM 并行优化方案

## 一、4/16 线程性能下降根因分析

### 1.1 现象回顾

| OMP_NUM_THREADS | 平均延迟 | FPS | 加速比 |
|-----------------|----------|-----|--------|
| 1（基线） | 3116ms | 0.32 | 1.00x |
| **2** | **1366ms** | **0.73** | **2.28x** ✅ |
| 4 | 2498ms | 0.40 | 1.25x ⚠️ |
| 8 | 1414ms | 0.71 | 2.22x |
| 16 | 2739ms | 0.37 | 1.16x ❌ |

### 1.2 根本原因：双层嵌套并行导致线程过订阅（Oversubscription）

通过 `ldd _caffe_ffi.so` 和 `nm -D` 检查发现关键事实：

```
libopenblas.so.0 => /opt/conda/envs/caffe-ffi/lib/libopenblas.so.0
         U cblas_sgemm    # 未定义符号，运行时从 OpenBLAS 动态链接
```

**`_caffe_ffi.so` 编译时链接了 OpenBLAS，Conv 层的 GEMM 调用走的是 OpenBLAS 的 `cblas_sgemm`（多线程实现），而非纯 C 单线程 fallback。**

这导致了**双层嵌套并行**：

```
┌─────────────────────────────────────────────────────┐
│  InceptionV1 Forward                                │
│  ┌───────────────────────────────────────────────┐  │
│  │  Conv 层（占90%+计算时间）                     │  │
│  │  forward_cpu_gemm → cblas_sgemm               │  │
│  │  └── OpenBLAS 内部线程池（自动使用 OMP_NUM_THREADS 个线程）  │
│  │      └── 每个 GEMM 调用开 BLAS_threads 个线程 │  │
│  └───────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────┐  │
│  │  Pooling/Eltwise 层                           │  │
│  │  #pragma omp parallel for → OpenMP 线程池     │  │
│  │  └── 开 OMP_NUM_THREADS 个线程并行           │  │
│  └───────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

**OpenBLAS 默认行为**：当未设置 `OPENBLAS_NUM_THREADS` 时，OpenBLAS 读取 `OMP_NUM_THREADS` 作为自身线程数。

因此实际线程数：

| OMP_NUM_THREADS | OpenBLAS 线程 | OpenMP 线程 | 总活跃线程 | 过订阅倍数 |
|-----------------|--------------|------------|-----------|-----------|
| 1 | 1 | 0（Pooling串行） | 1 | 0x（基线） |
| 2 | 2 | 2（仅Pooling/Eltwise） | 4 | 4/16 = 0.25x（轻度过订阅） |
| 4 | 4 | 4 | 8-16 | 1x |
| 8 | 8 | 8 | 16+ | 1x+ |
| 16 | 16 | 16 | 32+ | 2x（严重过订阅） |

### 1.3 其他加剧因素

1. **混合架构（Intel Core Ultra 9 285H = Arrow Lake-H）**：
   - 6 P-cores（性能核）+ 8 E-cores（能效核）+ 2 LPE-cores（低功耗E核）
   - Docker/WSL 中显示为 16 个逻辑 CPU，但性能异构
   - OpenMP `schedule(static)` 默认平均分配，P-core 任务早早完成后等待 E-core → 负载不均衡
   - 当线程数 > P-core 数（6）时，线程被调度到 E-core，频率更低，拖慢整体

2. **col_buffer_ 共享竞争**：
   - `BaseConvolutionLayer` 的 `col_buffer_` 是单个成员 Blob，im2col 写入其中
   - 若多 Conv 层或同一 batch 内多样本并行，存在共享写入冲突
   - 当前代码在 batch 维度（n 循环）是串行的，所以 col_buffer_ 本身没有竞争，但 OpenBLAS 的多线程可能与 OpenMP 线程在同一核心上争抢 L1/L2 缓存

3. **线程创建/销毁开销**：
   - 每次进入 `#pragma omp parallel` 区域有 fork/join 开销
   - Pooling 层在 2 线程时计算量大到足以摊销 fork 开销，4+ 线程时开销占比增大

### 1.4 线程绑定策略建议

**推荐方案：BLAS 单线程 + OpenMP 批量并行**（避免嵌套并行）：

```bash
# 最佳实践：BLAS 单线程，由 OpenMP 在 batch×group 维度统一调度
export OPENBLAS_NUM_THREADS=1   # OpenBLAS 单线程
export OMP_NUM_THREADS=2        # OpenMP 总线程数（匹配 P-core 数量）
export OMP_PROC_BIND=close      # 线程绑定到就近核心，不迁移
export OMP_PLACES=cores         # 绑定粒度为物理核心（非 HT 逻辑核）
```

或**替代方案：BLAS 多线程 + OpenMP 串行**（BLAS 负责所有并行）：

```bash
export OPENBLAS_NUM_THREADS=6   # OpenBLAS 使用 6 线程（匹配 P-cores）
export OMP_NUM_THREADS=1        # 我们的 OpenMP 区域串行，由 BLAS 并行
```

### 1.5 推荐线程配置（针对 Core Ultra 9 285H）

| 场景 | OPENBLAS_NUM_THREADS | OMP_NUM_THREADS | 说明 |
|------|---------------------|-----------------|------|
| 低延迟（推理） | 1 | 2-4 | OpenMP并行batch，BLAS串行，最佳延迟 |
| 高吞吐（批量） | 4-6 | 1 | BLAS并行GEMM，最佳吞吐量 |
| 训练（前向+反向） | 1 | 4-6 | 统一OpenMP调度，控制总线程数 |

---

## 二、Conv 层 GEMM OpenMP 并行化代码示例

### 2.1 优化策略：批量维度并行 + BLAS 单线程

核心思路：
1. **设置 `OPENBLAS_NUM_THREADS=1`**：GEMM 单线程执行，消除嵌套并行
2. **外层并行 batch×group**：在 Conv 层的 `(n, g)` 维度上 OpenMP 并行
3. **线程私有 col_buffer**：每个线程有独立的 im2col 缓冲区，消除共享竞争
4. **im2col+GEMM 作为单个并行任务**：减少 fork/join 次数

### 2.2 代码实现

将以下代码替换 [conv_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp) 中的 `Forward_cpu` 函数，并在 `base_conv_layer.cpp` 中提供线程安全的 im2col+GEMM 接口：

```cpp
// ======== base_conv_layer.hpp 新增：线程安全的 im2col+GEMM 批量执行 ========

#include <vector>

#ifdef CAFFE_USE_OPENMP
#include <omp.h>
#endif

// 线程私有 col_buffer 结构：避免共享 col_buffer_ 的写入竞争
struct ThreadColBuffer {
  Blob buffer;
  std::vector<int64_t> col_shape;
  bool initialized = false;

  void ensure_shape(const std::vector<int64_t>& shape) {
    if (!initialized || col_shape != shape) {
      buffer.Reshape(shape);
      col_shape = shape;
      initialized = true;
    }
  }
};

// 每个线程的 TLS（Thread-Local Storage）col_buffer
#ifdef CAFFE_USE_OPENMP
inline thread_local ThreadColBuffer tls_col_buffer;
#endif
```

```cpp
// ======== base_conv_layer.cpp 修改：forward_cpu_gemm 支持外部位移和col_buffer ========

// 新增重载：支持指定输入/输出位移和外部 col_buffer（供并行调用）
void BaseConvolutionLayer::forward_cpu_gemm_parallel(
    const float* input, const float* weights, float* output,
    float* col_buffer_ptr, int output_offset) {
  const float* col_buff = input;
  if (!is_1x1_) {
    // 写入线程私有 col_buffer，而非共享的 col_buffer_
    im2col_cpu(input, conv_in_channels_, conv_input_h(), conv_input_w(),
               kernel_h_, kernel_w_, pad_h_, pad_w_, stride_h_, stride_w_,
               dilation_h_, dilation_w_, col_buffer_ptr);
    col_buff = col_buffer_ptr;
  }
  for (int g = 0; g < group_; ++g) {
    caffe_cpu_gemm(false, false, conv_out_channels_ / group_,
                   conv_out_spatial_dim_, kernel_dim_, 1.F,
                   weights + weight_offset_ * g,
                   col_buff + col_offset_ * g,
                   0.F, output + output_offset + output_offset_ * g);
  }
}
```

```cpp
// ======== conv_layer.cpp 重写 Forward_cpu（OpenMP 并行版本）========

void ConvolutionLayer::Forward_cpu(const std::vector<Blob*>& bottom,
                                    const std::vector<Blob*>& top) {
  const float* weight = this->blobs_[0]->cpu_data();
  const float* bottom_data = bottom[0]->cpu_data();
  float* top_data = top[0]->cpu_mutable_data();
  const int M = conv_out_channels_ / group_;
  const int K = kernel_dim_;
  const int64_t top_count = top[0]->count();
  const int64_t weight_count = this->blobs_[0]->count();

  using clock = std::chrono::high_resolution_clock;
  auto t_total_start = clock::now();

  // ── 统计量准备（串行初始化，并行中原子更新） ──
  float out_min = std::numeric_limits<float>::max();
  float out_max = -std::numeric_limits<float>::max();
  double t_gemm_us = 0, t_bias_us = 0;

  // 预计算 col_buffer 大小：[kernel_dim_ * group_, conv_out_spatial_dim_]
  const int64_t col_buffer_size = static_cast<int64_t>(kernel_dim_) * group_ * conv_out_spatial_dim_;

  // ── OpenMP 并行：沿 batch(n) 维度并行 ──
  // 策略：
  //   1. 每个线程独立处理一个或多个样本的 im2col+GEMM，无写冲突
  //   2. 使用 schedule(dynamic) 做负载均衡（不同层计算量可能不同）
  //   3. reduction 处理 min/max 和时间统计
  //   4. BLAS 设置为单线程（OPENBLAS_NUM_THREADS=1），避免嵌套并行
#ifdef CAFFE_USE_OPENMP
  #pragma omp parallel reduction(min:out_min) reduction(max:out_max) \
                       reduction(+:t_gemm_us,t_bias_us)
  {
    // 分配线程私有 col_buffer（每个线程一次分配，复用）
    tls_col_buffer.ensure_shape(
        {kernel_dim_ * group_, output_h_, output_w_});
    float* my_col = tls_col_buffer.buffer.cpu_mutable_data();

    #pragma omp for schedule(dynamic, 1)
    for (int n = 0; n < num_; ++n) {
      const float* input = bottom_data + n * bottom_dim_;
      float* output = top_data + n * top_dim_;

      auto t_gemm_start = clock::now();
      forward_cpu_gemm_parallel(input, weight, output, my_col, 0);
      auto t_gemm_end = clock::now();
      t_gemm_us += std::chrono::duration<double, std::micro>(
          t_gemm_end - t_gemm_start).count();

      if (bias_term_) {
        auto t_bias_start = clock::now();
        const float* bias = this->blobs_[1]->cpu_data();
        forward_cpu_bias(output, bias);
        auto t_bias_end = clock::now();
        t_bias_us += std::chrono::duration<double, std::micro>(
            t_bias_end - t_bias_start).count();
      }
    }
  }
#else
  // 串行回退（无 OpenMP）
  for (int n = 0; n < num_; ++n) {
    const float* input = bottom_data + n * bottom_dim_;
    float* output = top_data + n * top_dim_;

    auto t_gemm_start = clock::now();
    forward_cpu_gemm(input, weight, output);
    auto t_gemm_end = clock::now();
    t_gemm_us += std::chrono::duration<double, std::micro>(
        t_gemm_end - t_gemm_start).count();

    if (bias_term_) {
      auto t_bias_start = clock::now();
      const float* bias = this->blobs_[1]->cpu_data();
      forward_cpu_bias(output, bias);
      auto t_bias_end = clock::now();
      t_bias_us += std::chrono::duration<double, std::micro>(
          t_bias_end - t_bias_start).count();
    }
  }

  // 串行统计
  for (int64_t i = 0; i < top_count; ++i) {
    out_min = std::min(out_min, top_data[i]);
    out_max = std::max(out_max, top_data[i]);
  }
#endif

  // ── 权重/偏置统计（串行，计算量极小） ──
  float w_min = std::numeric_limits<float>::max();
  float w_max = -std::numeric_limits<float>::max();
  double w_norm_sq = 0.0;
  for (int64_t i = 0; i < weight_count; ++i) {
    float w = weight[i];
    w_min = std::min(w_min, w);
    w_max = std::max(w_max, w);
    w_norm_sq += static_cast<double>(w) * static_cast<double>(w);
  }
  float w_norm = static_cast<float>(std::sqrt(w_norm_sq));

  float b_min = std::numeric_limits<float>::max();
  float b_max = -std::numeric_limits<float>::max();
  if (bias_term_) {
    int64_t bias_count = this->blobs_[1]->count();
    const float* bias_data = this->blobs_[1]->cpu_data();
    for (int64_t i = 0; i < bias_count; ++i) {
      b_min = std::min(b_min, bias_data[i]);
      b_max = std::max(b_max, bias_data[i]);
    }
  }

  // ── 输出统计（OpenMP 下需要单线程扫描 top_data 得到全局 min/max） ──
#ifdef CAFFE_USE_OPENMP
  {
    out_min = std::numeric_limits<float>::max();
    out_max = -std::numeric_limits<float>::max();
    for (int64_t i = 0; i < top_count; ++i) {
      out_min = std::min(out_min, top_data[i]);
      out_max = std::max(out_max, top_data[i]);
    }
  }
#endif

  auto t_total_end = clock::now();
  double total_us = std::chrono::duration<double, std::micro>(
      t_total_end - t_total_start).count();

  CAFFE_FFI_LOG_INFO() << "[CONV-PERF] " << this->name()
                       << " Convolution forward: num=" << num_
                       << " group=" << group_
                       << " M=" << M << " N=" << conv_out_spatial_dim_ << " K=" << K
                       << " kernel=[" << kernel_h_ << "," << kernel_w_ << "]"
                       << " stride=[" << stride_h_ << "," << stride_w_ << "]"
                       << " is_1x1=" << is_1x1_
                       << " bias_term=" << bias_term_
                       << " out=[" << out_min << ", " << out_max << "]"
                       << " w=[" << w_min << ", " << w_max << "]"
                       << " w_norm=" << w_norm
                       << (bias_term_ ? " b=[" + std::to_string(b_min) + ", " + std::to_string(b_max) + "]" : "")
                       << " t_gemm=" << t_gemm_us << "us"
                       << (bias_term_ ? " t_bias=" + std::to_string(t_bias_us) + "us" : "")
                       << " time=" << total_us << "us";
}
```

### 2.3 关键设计决策

| 决策 | 原因 |
|------|------|
| **BLAS 单线程（OPENBLAS_NUM_THREADS=1）** | 消除双层嵌套并行，避免过订阅；GEMM 单次调用变快（无 BLAS 线程 fork 开销），由外层 OpenMP 提供并行 |
| **沿 batch(n) 维度并行** | 每个样本的 im2col+GEMM 独立，输出写不同的内存区域（`top_data + n*top_dim_`），无写竞争 |
| **`schedule(dynamic, 1)`** | 动态调度适合不同计算量的层（如不同 kernel size 的 Conv），块大小为 1 实现最细粒度负载均衡 |
| **`thread_local` col_buffer** | 每个线程有独立的 im2col 暂存区，消除 `col_buffer_` 共享写入竞争；首次访问分配，后续复用 |
| **reduction 聚合统计量** | `min/max/sum` 通过 OpenMP reduction 自动聚合，避免手动加锁 |
| **全局 min/max 串行扫描** | top_data 的 min/max 在并行后做一次完整扫描（O(N)，开销远小于 GEMM） |
| **`OMP_PROC_BIND=close`** | 线程绑定到固定核心，避免 OS 跨核迁移导致 L1/L2 cache miss |

### 2.4 进一步优化方向（进阶）

1. **im2col 并行化**：当前 im2col 在每个线程内串行执行，可以进一步在 channel×kernel_h×kernel_w 维度并行（但通常 im2col 是内存带宽绑定，多线程收益有限）
2. **GEMM micro-kernel 优化**：单线程 GEMM 可使用 SIMD（AVX2/AVX-512）手写 micro-kernel 或集成 sgemm 实现（如 libxsmm），比纯 C triple-loop 快 5-10x
3. **Winograd 卷积**：3×3 卷积使用 Winograd F(4×4,3×3) 算法，减少 2.25x 乘法次数
4. **间接卷积（Indirect Conv）**：跳过 im2col 的数据重排，通过 offset 数组直接访问原始输入，减少内存占用和带宽
5. **NCHWc 布局**：对 channels 做 micro-packing（如 c=8/16），提升 SIMD 利用率

### 2.5 编译与运行配置

```bash
# CMake: 确保 BLAS 链接但 OpenBLAS 使用单线程
export CAFFE_FFI_CMAKE_ARGS="-DCAFFE_USE_OPENMP=ON -DCAFFE_FFI_ENABLE_COW_PHASE3=ON"
python -m pip install -e . --no-build-isolation

# 运行时环境变量（推荐配置）
export OPENBLAS_NUM_THREADS=1    # BLAS 单线程
export OMP_NUM_THREADS=2         # OpenMP 2-4 线程（匹配 P-core 数）
export OMP_PROC_BIND=close       # 就近绑定核心
export OMP_PLACES=cores          # 绑定到物理核心
export KMP_DUPLICATE_LIB_OK=TRUE # 允许多 OpenMP 运行时共存
```

---

## 三、预期性能提升估算

基于 InceptionV1 的 Conv 层分布（约 57 个 Conv 层，占总计算量 >90%）：

| 配置 | 预期延迟 | 预期 FPS | 相对基线 |
|------|----------|---------|---------|
| 基线（1线程，BLAS多线程） | 3116ms | 0.32 | 1.00x |
| **Conv OpenMP + BLAS单线程，2线程** | **~800-1000ms** | **1.0-1.2** | **~3.5x** |
| Conv OpenMP + BLAS单线程，4线程 | ~600-800ms | 1.2-1.7 | ~4-5x |
| Conv OpenMP + SIMD GEMM，4线程 | ~200-400ms | 2.5-5.0 | ~10-15x |

注：以上为估算值，实际加速比取决于 batch size、内存带宽和具体 GEMM 实现效率。
