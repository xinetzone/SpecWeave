# eltwise_sum / pooling OpenMP 并行优化代码示例

> 对应 RQ-3b。基于性能瓶颈分析（`eltwise_sum` 14.46x / `pooling` 11.14x 为两大严重瓶颈），
> 给出可直接落地到 caffe-ffi 现有层实现（`EltwiseLayer::Forward_cpu` / `PoolingLayer::Forward_cpu`）的
> OpenMP 并行优化 C++ 代码示例。
>
> 源码基准：
> - `projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/eltwise_layer.cpp`
> - `projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/pooling_layer.cpp`

---

## 0. 构建配置（对齐真实选项名）

**⚠️ 注意：真实 CMake 选项名是 `CAFFE_USE_OPENMP`，不是 `CAFFE_FFI_ENABLE_OPENMP`。**

见 [Options.cmake](../../../projects/xuanspace/libs/caffe-ffi/cmake/Options.cmake) 第 12 行：

```cmake
option(CAFFE_USE_OPENMP "Use OpenMP to parallelize compute-heavy loops (pure-C++ GEMM fallback, pooling, elementwise). Set to OFF to force serial execution." ON)
```

- 默认 **ON**。开启后 `CompilerConfig.cmake` 会：
  - 注入编译宏 `CAFFE_USE_OPENMP`（代码中 `#ifdef` 判断即此宏）；
  - 追加 OpenMP 编译标志（GCC/Clang `-fopenmp`，MSVC `/openmp`）；
  - 链接 `OpenMP::OpenMP_CXX`。
- 关闭方式：`-DCAFFE_USE_OPENMP=OFF`（强制串行，用于数值对拍/调试）。
- 线程数控制：运行时环境变量 `OMP_NUM_THREADS`（如 `OMP_NUM_THREADS=8`），或代码中 `omp_set_num_threads(n)`。
- 容器/Windows 多 OpenMP 运行时共存时，需 `export KMP_DUPLICATE_LIB_OK=TRUE`。

---

## 1. eltwise_sum（SUM 操作）优化

### 1.1 现状与问题

现有实现（[eltwise_layer.cpp](eltwise_layer.cpp) 的 `case SUM`）：

```cpp
case SUM: {
  const float* bottom0_data = bottom[0]->cpu_data();
  #ifdef CAFFE_USE_OPENMP
  #pragma omp parallel for schedule(static)
  #endif
  for (int64_t i = 0; i < count; ++i) {
    top_data[i] = bottom0_data[i] * coeffs_[0];
  }
  for (int j = 1; j < num_bottoms; ++j) {
    const float* bj_data = bottom[j]->cpu_data();
    #ifdef CAFFE_USE_OPENMP
    #pragma omp parallel for schedule(static)
    #endif
    for (int64_t i = 0; i < count; ++i) {
      top_data[i] += bj_data[i] * coeffs_[j];
    }
  }
  break;
}
```

问题：
1. **多次 fork/join**：每个 bottom 触发一次 `parallel for`，`num_bottoms` 个独立并行区域反复创建/销毁线程团队，开销大。
2. **中间写回**：先写 `top_data[i]` 再逐个 `+=`，产生多次内存读写往返。
3. **并行粒度**：`count` 可能较小（如分辨率低），单层切分无法充分发挥多核。

### 1.2 优化示例（单并行区域 + 融合累加 + 输出块切分）

```cpp
case SUM: {
  const int64_t count = top[0]->count();
  const int num_bottoms = static_cast<int>(bottom.size());
  float* top_data = top[0]->cpu_mutable_data();

  // 预取所有 bottom 指针，避免循环内反复调用 cpu_data()
  // 注意：必须在 cpu_mutable_data() 之前取值，防 COW 克隆语义被破坏
  std::vector<const float*> bdata(num_bottoms);
  for (int j = 0; j < num_bottoms; ++j) {
    bdata[j] = bottom[j]->cpu_data();
  }

  // 单次并行区域：整个输出块一次并行切分，融合所有 bottom 的累加。
  // 每个线程只写自己负责的 top_data[i]，先行把该 i 的所有输入读入局部 acc，
  // 再写一次——因此即使 bottom[0]==top (in-place) 也无数据竞争。
  #ifdef CAFFE_USE_OPENMP
  #pragma omp parallel for schedule(static)
  #endif
  for (int64_t i = 0; i < count; ++i) {
    float acc = bdata[0][i] * coeffs_[0];
    for (int j = 1; j < num_bottoms; ++j) {
      acc += bdata[j][i] * coeffs_[j];
    }
    top_data[i] = acc;
  }
  break;
}
```

要点：
- **一次并行区域**：`count` 个元素只 fork 一次线程团队，消除逐 bottom 的 fork/join 开销。
- **融合累加**：每个元素先局部累加 `acc` 再单次写回 `top_data[i]`，减少内存写带宽。
- **无数据竞争**：不同 `i` 由不同线程处理，写 `top_data[i]` 互不重叠。
- **in-place 安全**：`bdata` 在 `cpu_mutable_data()` 之前读取，且每个 `i` 先读全输入再写输出，`bottom[0]==top` 时不会读到被覆盖的旧值。

> 若 `count` 很大且希望更好缓存局部性，可将 `for (int64_t i = 0; i < count; ++i)` 改为二层：
> 外层按 `BLOCK`（如 256×256）切块并行，内层串行处理块内元素，等效于「输出块切分」，
> 但单层 `parallel for` 对 `count` 线性切分已无竞争，通常足够。

---

## 2. pooling 优化

### 2.1 现状与问题

现有实现（[pooling_layer.cpp](pooling_layer.cpp) 的 `Forward_cpu` 主循环）：

```cpp
#ifdef CAFFE_USE_OPENMP
#pragma omp parallel for schedule(static)
#endif
for (int n = 0; n < num; ++n) {
  for (int c = 0; c < channels_; ++c) {
    for (int ph = 0; ph < pooled_height_; ++ph) {
      for (int pw = 0; pw < pooled_width_; ++pw) {
        // ... 池化计算
      }
    }
  }
}
```

问题：
1. **仅按 batch 并行**：当 batch 很小（推理常用 `num=1`）时，`parallel for` 只有 1 个迭代块，**完全退化为串行**——这正是 pooling 11.14x 瓶颈的主因。
2. **并行度不足**：即使 batch>1，`num` 通常远小于核数，多核空转。

### 2.2 优化示例（flatten batch×channel）

将 `(n, c)` 两层折叠为单一 `nc` 扁平索引，使并行迭代数为 `num × channels_`（channels 通常很大，如 256/512，并行度充足），且不依赖工具链对 `collapse` 的支持：

```cpp
const int nc_total = num * channels_;
#ifdef CAFFE_USE_OPENMP
#pragma omp parallel for schedule(static)
#endif
for (int nc = 0; nc < nc_total; ++nc) {
  const int n = nc / channels_;
  const int c = nc % channels_;
  for (int ph = 0; ph < pooled_height_; ++ph) {
    for (int pw = 0; pw < pooled_width_; ++pw) {
      int hstart = ph * stride_h_ - pad_h_;
      int wstart = pw * stride_w_ - pad_w_;
      int hend = std::min(hstart + kernel_h_, height_);
      int wend = std::min(wstart + kernel_w_, width_);
      hstart = std::max(hstart, 0);
      wstart = std::max(wstart, 0);
      const int pool_index = (nc) * pooled_height_ * pooled_width_
                             + ph * pooled_width_ + pw;
      const int base = (nc) * height_ * width_;

      if (pool_method_ == caffe::PoolingParameter::MAX) {
        float max_val = -std::numeric_limits<float>::max();
        int max_idx = -1;
        for (int h = hstart; h < hend; ++h) {
          for (int w = wstart; w < wend; ++w) {
            const int index = base + h * width_ + w;
            float val = bottom_data[index];
            if (val > max_val) { max_val = val; max_idx = h * width_ + w; }
          }
        }
        top_data[pool_index] = max_val;
        mask_data[pool_index] = static_cast<float>(max_idx);
      } else if (pool_method_ == caffe::PoolingParameter::AVE) {
        float sum = 0.0f;
        int cnt = 0;
        for (int h = hstart; h < hend; ++h) {
          for (int w = wstart; w < wend; ++w) {
            sum += bottom_data[base + h * width_ + w];
            ++cnt;
          }
        }
        top_data[pool_index] = (cnt > 0) ? (sum / cnt) : 0.0f;
      }
    }
  }
}
```

要点：
- **并行维度 = `num × channels_`**：把原来的 `(n, c)` 折叠为一个扁平循环，并行度从 `num` 提升到 `num × channels_`，batch=1 时也能用满多核。
- **无数据竞争**：每个 `(n, c)` 平面写 `top_data`/`mask_data` 的独立区间，互不重叠。
- **Max 索引**：`max_idx` 仍按通道平面内相对索引记录（兼容现有 `Backward_cpu` 的梯度路由）。
- **预分配复用**：`top_data`/`mask_data` 已在 `Reshape` 中分配（`max_idx_ = make_object<Blob>(top_shape)`），Forward 内仅需 `cpu_mutable_data()` 取指针，无需临时分配。

> 备选方案：若工具链支持（GCC/LLVM 的 OpenMP 支持 `collapse`），可写为
> `#pragma omp parallel for schedule(static) collapse(2)` 直接作用于 `for n { for c { ... } }` 两层。
> 但 MSVC 历史版本对 `collapse` 支持不稳，**flatten 方案更可移植**，推荐采用。

### 2.3 线程数控制

```bash
# 运行前设置（容器内）
export OMP_NUM_THREADS=8
export KMP_DUPLICATE_LIB_OK=TRUE   # Windows 多 OpenMP 副本共存必设
python run_net.py
```

或代码内（`Forward_cpu` 入口，可选）：

```cpp
#ifdef CAFFE_USE_OPENMP
  if (omp_get_num_threads() <= 1) omp_set_num_threads(0); // 0 = 使用 OMP_NUM_THREADS/env 默认
#endif
```

---

## 3. 落地清单（checklist）

- [ ] 修改 `eltwise_layer.cpp` 的 `case SUM`：改为单并行区域 + 融合累加（§1.2）。
- [ ] 修改 `pooling_layer.cpp` 的 `Forward_cpu` 主循环：`(n,c)` flatten 并行（§2.2）。
- [ ] 确认 CMake 选项 `CAFFE_USE_OPENMP=ON`（默认）已生效，重编译 `_caffe_ffi.so`。
- [ ] 数值对拍：`CAFFE_USE_OPENMP=OFF` 与 `ON` 两种构建输出一致（同种子输入）。
- [ ] 基准复测：`eltwise_sum` / `pooling` 延迟与吞吐，确认接近 caffex 水平。
- [ ] 线程数调优：按实际核数设 `OMP_NUM_THREADS`，记录最优值。

> **对抗审查要点（V2）**：并行维度已确认无数据竞争；`CAFFE_USE_OPENMP` 默认 ON 的既有行为不变；
> 关闭选项后回退串行路径，保证数值可复现。