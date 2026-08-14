# Conv GEMM 调度优化 - Changelog

> **日期**: 2026-08-06
> **目标**: 将 ResNet50 单张推理延迟从 405ms 降至 ≤200ms（端到端 2× 加速），消除 OpenBLAS 线程过订阅警告
> **结果**: mean=138.4ms（2.93× 加速），零失败（2109 passed），OpenBLAS 零警告

---

## 性能对比

| 配置 | mean 延迟 | 加速比 | 相对 caffex |
|------|-----------|--------|-------------|
| 原始（pthreads BLAS + 过订阅） | 1637ms | — | 6.0× 慢 |
| 仅修复 OpenBLAS（baseline） | 405ms | baseline | 1.49× 慢 |
| **全部优化后** | **138.4ms** | **2.93×** | **0.51×（快约2×）** |

---

## Commits

### Commit 1: `e321ecd` (xuanspace)

**类型**: `perf(caffe-ffi)` — Release模式条件编译PERF统计代码，ResNet50延迟2.93x加速

**核心改动**:

1. **新增 `CAFFE_FFI_ENABLE_PERF_LOG` 编译选项**（[Options.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/Options.cmake#L9)）
   - 默认 OFF（生产推理），设为 ON 时启用逐层计时/统计/PERF 日志
   - [CompilerConfig.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/CompilerConfig.cmake#L77-L80) 添加预处理宏条件传递

2. **28个层文件 PERF 统计代码条件编译**
   - 覆盖：absval, batch_norm, bias, concat, conv, crop, deconv, dropout, eltwise, elu, hinge, inner_product, instance_norm, l2_norm, leaky_relu, lrn, margin_ranking, pooling, prelu, relu, scale, sigmoid, slice, softmax, softmax_loss, softplus, softsign, split, tanh
   - 包裹内容：`high_resolution_clock::now()` 计时、主循环内 `std::min/std::max` 统计、范数计算、`[*-PERF]` 日志输出
   - 消除 O(N) min/max 遍历对 SIMD 自动向量化的阻塞（贡献~30%性能提升）

3. **Conv OpenMP 分块策略调优**（[conv_layer.cpp#L88](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp#L88)）
   - `kMinChunk` 从 32 降至 8：conv1(64ch) 从2线程→4线程满载
   - 修复 serial fallback 路径 `n * bottom_dim_` 整数溢出（改用 `int64_t`）

**文件变更**: 31 files changed, +643/-209

---

### Commit 2: `fc422c5e` (SpecWeave)

**类型**: `perf(caffe-ffi-jupyter)` — 集成OpenBLAS openmp变体和Release编译优化，支撑Conv GEMM 2.93x加速

**核心改动**:

1. **Dockerfile** ([Dockerfile#L110-L177](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/Dockerfile#L110-L177))
   - builder 阶段：`libopenblas` → `libopenblas=*=*openmp*`（openmp 变体替代 pthreads 变体）
   - Runtime 阶段：默认 `OMP_NUM_THREADS=4`、`OPENBLAS_NUM_THREADS=1`

2. **editable-install.sh** ([editable-install.sh#L218-L220](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/scripts/editable-install.sh#L218-L220))
   - 添加 `-DCAFFE_FFI_ENABLE_PERF_LOG=OFF`
   - 添加 `-DCAFFE_FFI_ENABLE_DEBUG_LOG=OFF`
   - 添加 `-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -ffast-math -fno-finite-math-only`

3. **新增 `rebuild-openblas-openmp.sh`**
   - 一键修复脚本：conda 替换 openmp 变体 + 源码编译 `USE_OPENMP=1` 双方案
   - 用于现有容器/环境中不重新构建镜像时修复线程冲突

4. **xuanspace 子模块指针更新至 `e321ecd`**

**文件变更**: 4 files changed, +420/-2

---

### Commit 3: `013155de` (SpecWeave)

**类型**: `docs(conv-gemm)` — 更新gap分析报告，新增Conv GEMM优化spec和总结报告

**核心改动**:

1. [gap_analysis_report.md](../caffex-vs-caffe-ffi-gap-analysis/gap_analysis_report.md): 新增第十一章「Conv GEMM调度优化实施」
2. `.trae/specs/conv-gemm-optimization/` 新增 spec 文档集：
   - `spec.md` — PRD（目标≤200ms）与验收标准
   - `tasks.md` — 8项任务分解与基准/回归测试结果
   - `checklist.md` — 28项检查点追踪
   - `summary-report.md` — 项目总结（性能对比+关键改动+可复用模式+P2遗留事项）

**文件变更**: 5 files changed, +802/-10

---

## Post-Fix: 后续修复（AlexNet + PERF测试兼容性）

### 修复1：AlexNet protobuf 解析错误

**根因**：`urllib.request.urlretrieve` 下载大文件时网络中断导致文件截断
- 本地文件：95MB vs 服务器 Content-Length：233MB（bvlc_alexnet.caffemodel）
- 截断的二进制 protobuf 文件触发 `DecodeError: Wire format was corrupt`

**修复**：
- [utils.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/networks/utils.py) `_download_model()` 添加：
  - HEAD 请求探测服务器 Content-Length
  - 本地文件大小校验（小于期望值则删除重下）
  - 3次自动重试（指数退避）
  - 同时修复 resnet101.caffemodel 截断问题（本地仅162字节）

### 修复2：PERF 日志测试 Release 模式兼容性

**问题**：8个 `test_phase3_log_aggregation.py` 测试断言 `[SPLIT-PERF]` 日志输出，Release 模式 PERF_LOG=OFF 时无输出导致失败

**修复**：
- [test_phase3_log_aggregation.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/test_phase3_log_aggregation.py) 添加：
  - `_perf_log_enabled()` 运行时检测（fd级stdout重定向捕获C++输出）
  - `@skipif_no_perf_log` 装饰器自动跳过 PERF 依赖测试
  - 4个功能正确性测试始终运行（不受影响）

---

## 验证结果

| 测试类别 | 通过 | 失败 | 跳过 |
|----------|------|------|------|
| 所有层 backward 梯度检查 | 545 | 0 | 0 |
| 网络级端到端测试（含AlexNet） | 209 | 0 | 0 |
| pytest 核心测试（非ops/） | 2109 | 0 | 11 |

---

## 可复用模式

1. **生产/调试双模式条件编译**：CMake option → CompilerConfig 宏传递 → `#ifdef` 包裹，避免运行时开关的优化阻塞
2. **OpenBLAS + OpenMP 共存**：openmp 变体 + `OPENBLAS_NUM_THREADS=1` + `OMP_NUM_THREADS=N`
3. **OpenMP 通道分块**：`kMinChunk ≤ min_channels / num_threads`，保证所有线程有工作
4. **模型下载完整性校验**：HEAD 探测 Content-Length + 本地大小校验 + 自动重试
