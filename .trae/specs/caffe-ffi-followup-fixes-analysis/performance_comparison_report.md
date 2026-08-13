# InceptionV1 Forward 性能对比报告 — Conv 层 OpenMP 并行优化

**日期**: 2026-08-05
**优化内容**: Conv 层 batch 维度 OpenMP 并行 + 线程绑定策略 + OpenBLAS 线程配置
**测试模型**: InceptionV1 (BVLC GoogLeNet), batch=1, 输入 1×3×224×224
**硬件**: Intel Core Ultra 9 285H (Arrow Lake-H), Docker 容器 (caffe-ffi-jupyter)

---

## 一、性能对比（batch=1, 单图推理）

### 1.1 优化前 vs 优化后（完整端到端）

| 配置 | OpenBLAS线程 | OMP线程 | 平均延迟 | FPS | 相对原始基线 |
|------|-------------|---------|----------|-----|-------------|
| **优化前（无BLAS，无OpenMP）** | 0 (纯C) | 1 | ~3116ms | ~0.32 | 1.00x |
| **优化前（无BLAS，Pooling/Eltwise OpenMP=2）** | 0 (纯C) | 2 | ~1366ms | ~0.73 | 2.28x |
| **优化后（OpenBLAS正常链接，BLAS=1 OMP=1）** | 1 | 1 | 100ms | 10.00 | **31x** |
| **优化后（BLAS=1, OMP=2）** | 1 | 2 | **86ms** | **11.60** | **36x** |
| **优化后（BLAS=4, OMP=1）** | 4 | 1 | **86ms** | **11.57** | **36x** |
| 优化后（BLAS=1, OMP=4） | 1 | 4 | 91ms | 11.05 | 34x |
| 优化后（BLAS=1, OMP=8） | 1 | 8 | 87ms | 11.52 | 36x |
| 优化后（BLAS=4, OMP=2） | 4 | 2 | 87ms | 11.49 | 36x |
| 优化后（BLAS=6, OMP=1） | 6 | 1 | 108ms | 9.29 | 29x |
| 优化后（BLAS=2, OMP=2） | 2 | 2 | 99ms | 10.09 | 31x |

### 1.2 关键发现

1. **最大加速来自 OpenBLAS 正确链接**：之前 CMake 未正确检测到 OpenBLAS，GEMM 使用纯 C triple-loop 实现（~3s），正确链接 OpenBLAS 后延迟降至 ~100ms（**31x 基础加速**）
2. **多线程配置最佳点在 86ms**：BLAS=1+OMP=2 和 BLAS=4+OMP=1 均达到最佳，两种策略等效（约 11.6 FPS）
3. **4/16 线程性能下降的根因**：双层嵌套并行过订阅（OpenBLAS 默认读取 OMP_NUM_THREADS 创建内部线程池 + 我们的 OpenMP 区域再次创建线程），导致实际线程数远超物理核心数
4. **BLAS=6 反而变慢**：Core Ultra 9 285H 有 6 个 P-core，但 OpenBLAS 6 线程在 WSL2/Docker 环境中调度效率下降（E-core 干扰 + 缓存争用）
5. **线程绑定有效**：`OMP_PROC_BIND=close` + `OMP_PLACES=cores` 减少线程迁移开销

### 1.3 批量推理（batch>1）性能

| Batch Size | OMP=1 BLAS=1 | OMP=2 BLAS=1 | 加速比 | 最大输出误差 |
|-----------|-------------|-------------|--------|------------|
| 1 | 97ms | 91ms | 1.08x | 0.0 |
| 2 | 160ms | 169ms | 0.95x | 0.0 |
| 4 | 407ms | 359ms | **1.14x** | 0.0 |

Conv 层 batch 并行化在 batch≥4 时展现 1.14x 加速，batch=2 时由于线程 fork/join 开销抵消了并行收益。正确性完全一致（max_diff=0.0）。

---

## 二、根因分析：4/16 线程性能下降

**核心问题：OpenBLAS 与 OpenMP 双层嵌套并行导致线程过订阅**

```
caffe-ffi.so 链接了 libopenblas.so.0
  ├── OpenBLAS cblas_sgemm() 创建内部线程池（大小 = OMP_NUM_THREADS）
  └── 我们的 #pragma omp parallel for 创建外部线程池（大小 = OMP_NUM_THREADS）
      
当 OMP_NUM_THREADS=16 时：
  总活跃线程 ≈ 16(BLAS) × 16(OpenMP) = 256 个 → 严重过订阅
  即使 OMP_NUM_THREADS=4：
  总活跃线程 ≈ 4(BLAS) × 4(OpenMP) = 16 个 → 16核机器刚好满载但有争用
```

**其他加剧因素**：
- Core Ultra 9 285H 混合架构（6P+8E+2LPE）：线程调度到 E-core 时频率下降
- 共享 `col_buffer_` 竞争：多 Conv 层调用共享 im2col 缓冲区
- `schedule(static)` 默认平均分配导致 P-core/E-core 负载不均衡

---

## 三、推荐线程配置

| 使用场景 | OPENBLAS_NUM_THREADS | OMP_NUM_THREADS | 预期延迟 | 说明 |
|---------|---------------------|-----------------|---------|------|
| 单图低延迟推理（默认） | 1 | 2 | ~86ms | 最佳延迟，OpenMP统一调度 |
| 单图高吞吐推理 | 4 | 1 | ~86ms | BLAS并行GEMM，等效性能 |
| 批量推理（batch≥4） | 1 | 2-4 | 见batch测试 | Conv batch并行 + BLAS串行 |
| 训练（前向+反向） | 1 | 4 | 待测 | 统一OpenMP调度避免嵌套 |

**环境变量一键设置**：
```bash
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=2
export OMP_PROC_BIND=close
export OMP_PLACES=cores
export KMP_DUPLICATE_LIB_OK=TRUE
```

---

## 四、代码修改清单

### 4.1 新增文件
- [build_and_bench.sh](file:///d:/spaces/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/build_and_bench.sh) — 一键编译+性能测试脚本
- [bench_inceptionv1.py](file:///d:/spaces/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/bench_inceptionv1.py) — Python性能基准测试脚本
- [openmp-perf-analysis-and-conv-optimization.md](file:///d:/spaces/SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/openmp-perf-analysis-and-conv-optimization.md) — 详细技术分析文档

### 4.2 修改文件
- [base_conv_layer.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/layers/base_conv_layer.hpp#L167-L171) — 新增 `forward_cpu_gemm_ext()` 声明（线程安全版本，接受外部 col_buffer 指针）
- [base_conv_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/base_conv_layer.cpp#L220-L240) — 实现 `forward_cpu_gemm_ext()`
- [conv_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp#L24-L157) — Forward_cpu 添加 OpenMP batch 并行（`#pragma omp parallel for schedule(dynamic,1)` + 线程私有 col_buffer）

### 4.3 并行策略要点
1. **沿 batch(n) 维度并行**：每个样本独立计算 im2col+GEMM+Bias，输出写不同内存区域，无写竞争
2. **线程私有 col_buffer**：`std::vector<float> thread_col_buf` 在 parallel 区域内声明，每个线程独立分配，消除 `col_buffer_` 共享竞争
3. **`schedule(dynamic,1)`**：动态调度，块大小为1，适配不同计算量的 Conv 层
4. **1x1 Conv 走原路径**：1x1 卷积不需要 im2col，直接调用 `forward_cpu_gemm`（不使用 col_buffer）
5. **BLAS=1 避免嵌套**：外部设置 `OPENBLAS_NUM_THREADS=1`，GEMM 单线程执行，由 OpenMP 提供外层并行

---

## 五、一键运行方式

```bash
# 进入容器并执行
docker exec -it caffe-ffi-jupyter bash /SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/build_and_bench.sh

# 或手动分步执行：
# 1. 设置环境变量
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 OMP_PROC_BIND=close OMP_PLACES=cores KMP_DUPLICATE_LIB_OK=TRUE
# 2. 重新编译
cd /SpecWeave/projects/xuanspace/libs/caffe-ffi && rm -rf build/ && SKBUILD_CMAKE_ARGS="-DCAFFE_USE_OPENMP=ON" pip install --no-cache-dir --no-build-isolation -e .
# 3. 运行性能测试
python /SpecWeave/.trae/specs/caffe-ffi-followup-fixes-analysis/bench_inceptionv1.py \
  --proto /root/.caffe_test_data/models/inceptionv1.prototxt \
  --model /root/.caffe_test_data/models/inceptionv1.caffemodel \
  --warmup 3 --iters 10 --threads "1,2,4" --blas-threads 1
```
