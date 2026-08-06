# Conv GEMM 调度优化项目总结报告

> **日期**：2026-08-06
> **目标**：将 ResNet50 单张推理延迟从 405ms 降至 ≤200ms（端到端 2× 加速），消除 OpenBLAS 线程过订阅警告
> **验证环境**：WSL2 Ubuntu-24.04 + Docker Desktop, OMP_NUM_THREADS=4, OPENBLAS_NUM_THREADS=1

---

## 一、性能对比

### 1.1 核心指标

| 配置 | mean 延迟 | 相对优化前 | 相对 caffex |
|------|-----------|-----------|-------------|
| caffe-ffi（原始，pthreads BLAS + 过订阅） | 1637ms | 4.04× 慢 | 6.0× 慢 |
| caffe-ffi（仅修复 OpenBLAS openmp，无编译优化） | 405ms | **baseline** | 1.49× 慢 |
| **caffe-ffi（全部优化后）** | **138.4ms** | **2.93× 加速** | **0.51×（快约2×）** |
| caffex（C++原生，Hub基准） | 272.0ms | — | 1.0× |

### 1.2 详细基准数据（30 iters, 10 warmup）

| 统计量 | 值 |
|--------|-----|
| mean | 138.4ms |
| median | 118.2ms |
| std | 52.8ms |
| min | 103.7ms |
| max | 266.9ms |
| p5 | 104.3ms |
| p25 | 110.9ms |
| p75 | 144.4ms |
| p95 | 217.0ms |

### 1.3 正确性验证

| 验证项 | 结果 |
|--------|------|
| OpenBLAS 线程过订阅警告 | ✅ 零警告 |
| 输出 sum=1.0（softmax 概率分布） | ✅ 1.000000 |
| NaN/Inf 检测 | ✅ 无 |
| 确定性（两次独立加载+推理） | ✅ max_abs_error=0.00e+00 |
| PERF 日志（Release模式） | ✅ 0 行输出 |
| libopenblas 变体 | ✅ openmp_hd680484_0 |

### 1.4 单元测试回归

| 测试类别 | 通过 | 失败 | 跳过 | 说明 |
|----------|------|------|------|------|
| 所有层 backward 梯度检查 | 545 | 0 | 0 | 29个修改层全部覆盖 |
| 网络级端到端测试 | 209 | 0 | 0 | AlexNet已修复（模型下载截断问题） |
| pytest 核心测试（非ops/） | 2109 | 0 | 11 | 8个PERF日志测试Release模式自动跳过 |

**修复记录**：
- ✅ AlexNet protobuf 错误：根因是 `urllib.request.urlretrieve` 下载大文件时网络中断导致截断（本地95MB vs 服务器233MB），改进 `_download_model()` 添加 Content-Length 校验和自动重试
- ✅ PERF 日志测试 Release 兼容：添加运行时 PERF_LOG 检测（通过 fd 级 stdout 捕获判断），8个 PERF 依赖测试在 Release 模式下自动跳过，4个功能正确性测试始终运行
- ops/ 目录 29个文件：预存在 `from utils import L` ImportError（非本次优化引入）

---

## 二、关键改动点

### 2.1 改动概览

| 仓库 | 文件数 | 新增行 | 删除行 |
|------|--------|--------|--------|
| projects/xuanspace（caffe-ffi 核心+测试工具） | 33 | +700 | -220 |
| SpecWeave（apps/caffe-ffi-jupyter） | 3 | +420 | -2 |
| SpecWeave（spec 文档） | 4 | 新增 | — |

### 2.2 五项优化措施

#### 优化1：Dockerfile 固定 OpenBLAS openmp 变体

**文件**：[Dockerfile](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/Dockerfile#L110-L177)

- builder 阶段 conda 安装锁定 `libopenblas=*=*openmp*`
- Runtime 阶段设置默认环境变量：`OMP_NUM_THREADS=4`、`OPENBLAS_NUM_THREADS=1`
- **解决问题**：conda-forge 默认的 pthreads 变体与 GOMP/libgomp 运行时冲突，导致线程过订阅

#### 优化2：Release 编译优化 flags

**文件**：[editable-install.sh](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/scripts/editable-install.sh#L218-L220)

```bash
-DCAFFE_FFI_ENABLE_PERF_LOG=OFF
-DCAFFE_FFI_ENABLE_DEBUG_LOG=OFF
-DCMAKE_CXX_FLAGS_RELEASE=-O3 -DNDEBUG -ffast-math -fno-finite-math-only
```

- `-O3`：最高优化级别（循环展开、向量化、内联）
- `-ffast-math`：放宽 IEEE 浮点合规，允许 GCC 激进 SIMD 优化
- `-fno-finite-math-only`：保留 NaN/Inf 检查的同时启用 fast-math

#### 优化3：新增 CAFFE_FFI_ENABLE_PERF_LOG 编译选项

**文件**：
- [Options.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/Options.cmake#L9)：新增 option，默认 OFF
- [CompilerConfig.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/CompilerConfig.cmake#L77-L80)：条件添加预处理器宏

**设计**：
- 默认 OFF（生产推理）：零开销
- 设为 ON（调试分析）：启用逐层计时、统计、PERF 日志
- 与 CAFFE_FFI_ENABLE_DEBUG_LOG 解耦

#### 优化4：所有层 PERF 统计代码条件编译（28个层文件）

**覆盖层**：absval, batch_norm, bias, concat, conv, crop, deconv, dropout, eltwise, elu, hinge, inner_product, instance_norm, l2_norm, leaky_relu, lrn, margin_ranking, pooling, prelu, relu, scale, sigmoid, slice, softmax, softmax_loss, softplus, softsign, split, tanh

**包裹内容**：
- `std::chrono::high_resolution_clock::now()` 计时调用
- 主循环内逐元素 `std::min/std::max` 统计（最大性能杀手——阻止编译器自动向量化）
- 范数计算、字符串格式化、`[*-PERF]` 日志输出

**关键发现**：最初仅修复 conv_layer.cpp 后基准测试仍发现 `[SPLIT-PERF]`/`[BN-PERF]`/`[POOL-PERF]` 等日志，说明所有层都需要条件编译。

#### 优化5：Conv OpenMP 分块策略调优

**文件**：[conv_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp#L88)

- `kMinChunk` 从 32 降至 **8**：
  - conv1（64ch）：64/32=2 chunks → 仅2线程工作（旧）；64/8=8 → 4线程满载（新）
  - 大层（2048ch）：2048/8=256 → min(4,256)=4 → 效率不受影响
- 修复 serial fallback 路径 `n * bottom_dim_` 整数溢出（改用 `int64_t`）

---

## 三、性能提升归因分析

| 优化措施 | 估计贡献 | 依据 |
|----------|----------|------|
| -O3 -ffast-math 编译优化 | ~40% | SIMD 向量化、循环展开、内联对 GEMM 和逐元素操作收益最大 |
| 移除 PERF/DEBUG 统计循环 | ~30% | 消除 O(N) min/max 遍历，释放编译器自动向量化能力 |
| kMinChunk=8 通道分块调优 | ~20% | conv1 等小通道层从2线程→4线程满载 |
| OpenBLAS openmp 变体 | ~10% | 消除线程过订阅，固定线程配置减少调度开销 |

---

## 四、可复用模式沉淀

### 模式1：生产/调试双模式条件编译

**触发场景**：推理引擎包含性能统计、调试日志、范数计算等开发辅助代码，Release 构建需零开销。

**核心步骤**：
1. CMake 添加 option（默认 OFF）
2. CompilerConfig 根据 option 添加 `target_compile_definitions`
3. 源文件中用 `#ifdef MACRO` 包裹调试/统计代码
4. editable-install.sh/build 脚本显式设置 `-DMACRO=OFF`

**反模式**：在运行时用 `if (enable_perf)` 开关——即使分支不执行，函数调用、循环结构仍阻止编译器优化。

### 模式2：OpenBLAS + OpenMP 共存配置

**触发场景**：使用 OpenBLAS 的项目同时使用 OpenMP 做外层并行。

**核心步骤**：
1. 安装 openmp 变体（`libopenblas=*=*openmp*`），禁用 pthreads 变体
2. 设置 `OPENBLAS_NUM_THREADS=1`（BLAS 单线程，避免内层并行）
3. 设置 `OMP_NUM_THREADS=N`（外层 OpenMP 做任务并行）
4. 可选：`OMP_PROC_BIND=close OMP_PLACES=cores` 绑定线程到核心

### 模式3：OpenMP 通道分块大小调优

**触发场景**：对卷积层输出通道做 OpenMP 并行时，需平衡负载均衡和 GEMM 效率。

**核心原则**：`kMinChunk ≤ min_channels / num_threads`，保证所有线程都有工作；同时不小于 GEMM 最佳粒度（≥8即可）。

---

## 五、遗留事项（P2）

> 已完成：#5 PERF_LOG测试标记、AlexNet模型下载截断修复

| # | 方向 | 优先级 | 预期收益 | 复杂度 |
|---|------|--------|----------|--------|
| 1 | 完整 docker build 验证 | **P0** | 确保从零构建可用，CI/CD可靠 | 中 |
| 2 | caffex 公平对比（同4线程配置） | P1 | 验证性能声明的准确性 | 低 |
| 3 | ops/ 测试修复（29个ImportError） | P1 | 消除测试盲区，防止回归 | 中 |
| 4 | batch>1 维度并行 | P2 | 服务端批量推理场景 | 高 |
| 5 | im2col OpenMP并行化 | P3 | ResNet50多为1×1卷积，收益有限 | 中 |

**优先级建议**：
1. **#1 完整 docker build**：当前 Dockerfile 修改后未做端到端重建验证，新用户/CI按文档构建可能失败
2. **#2 caffex 公平对比**：当前138.4ms vs caffex 272ms 的对比存在变量不匹配（caffex线程配置未知），需在相同4线程下验证
3. **#3 ops/ 测试修复**：29个测试文件静默失败（ImportError），可能掩盖算子层回归
4. **#4 batch>1 并行**：面向服务端场景，当前单张推理目标已达成
5. **#5 im2col 并行**：ResNet50 中 3×3/7×7 卷积占比小，预期收益<5%
