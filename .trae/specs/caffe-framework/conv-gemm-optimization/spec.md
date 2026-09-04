# Conv GEMM 调度优化（降低 caffex↔caffe-ffi 性能差距） - Product Requirement Document

## Overview
- **Summary**: 针对 Hub 模型实测中发现的 caffe-ffi 相对 caffex 几何平均 18.9× 性能差距，通过编译优化、BLAS 配置固化、Conv 层 OpenMP 调度策略调优、调试开销编译期消除四个层面优化，目标将 ResNet50 单 batch 推理延迟从当前 ~405ms（固定线程）降低至 ≤120ms（~3.4× 加速），向 caffex 基线 ~21ms 靠近。
- **Purpose**: 当前 caffe-ffi 虽然功能完整、精度正确，但推理性能远低于经典 Caffe（caffex），主要瓶颈在于：(1) Forward 中无条件执行的统计循环造成 O(N) 额外开销；(2) Docker 镜像未固定 OpenBLAS openmp 变体导致过订阅风险；(3) OpenMP 分块策略对小通道层粒度过粗导致并行度不足；(4) 编译时缺少 native arch 优化。
- **Target Users**: caffe-ffi 用户、推理服务开发者、性能基准测试人员。

## Goals
- **G1**: 消除 Conv 层 Forward 中无条件的 min/max/norm 统计循环开销（编译期开关，release 构建默认关闭）
- **G2**: Dockerfile 固化 OpenBLAS openmp 变体，彻底消除过订阅警告（无需手动 post-install）
- **G3**: 优化 Conv 层 OpenMP 分块策略，降低 kMinChunk 阈值并增加 N（batch）维度并行支持，提升 ResNet50 早期层并行度
- **G4**: 添加编译优化 flags（-march=native / -ftree-vectorize），确保 im2col 等辅助函数向量化
- **G5**: 在容器 entrypoint/环境中配置合理的默认线程数，避免用户手动调优
- **G6**: ResNet50 单 batch 推理延迟（固定最优线程配置）较优化前加速 ≥2×

## Non-Goals (Out of Scope)
- **NG1**: 不引入 cuDNN/GPU 支持（保持 CPU-only）
- **NG2**: 不实现 Winograd 卷积（需要复杂的算法切换，属于更长期优化）
- **NG3**: 不替换 BLAS 实现为 MKL（保持 OpenBLAS 开源路线）
- **NG4**: 不修改 caffex 代码（caffex 是 vendor 基线，禁止修改）
- **NG5**: 不优化 backward 路径（本次仅聚焦推理前向性能）
- **NG6**: 不修改 pooling、ReLU、BN 等非卷积层性能

## Background & Context
- 实测环境：caffe-ffi-jupyter Docker 容器，CPU 为容器分配的核心（通常 4-8 核），OpenBLAS 0.3.34 openmp 变体（已手动修复）。
- 当前状态：
  - Conv 层已有 OpenMP 并行（按输出通道 M 分块，kMinChunk=32）
  - GEMM 调用 cblas_sgemm（OpenBLAS），BLAS 单线程 + OpenMP 多线程模式
  - 修复前（pthreads BLAS）有线程过订阅警告；修复后无警告但性能仍有差距
  - 固定线程配置 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=4 时 ResNet50 mean=405ms
  - caffex 基线 ResNet50 约 21ms（几何平均 18.9× 差距）
- 已发现的具体代码瓶颈：
  1. **统计循环开销**（[conv_layer.cpp#L162-L181](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp#L162-L181)）：每次 Forward 无条件遍历 top_count（输出元素数）和 weight_count（权重元素数）计算 min/max/norm，这在 caffex 中不存在。对 ResNet50 conv5_x 层，单次遍历处理数十万到数百万元素。
  2. **计时开销**（[conv_layer.cpp#L42-L43](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp#L42-L43) + L183-L184）：high_resolution_clock 每次 forward 启停。
  3. **OpenMP kMinChunk=32 过保守**（[conv_layer.cpp#L86](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/conv_layer.cpp#L86)）：ResNet50 的 conv1(64ch)、res2a/b/c(64ch)、res3a(128ch) 只能分 2-4 chunks，当 OMP_NUM_THREADS=4-8 时大量核心空闲。
  4. **im2col 标量三重循环**（[math_utils.hpp#L177-L210](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/math_utils.hpp#L177-L210)）：无向量化、无 OpenMP、逐元素 pad 检查，效率低。
  5. **Dockerfile 未固定 openmp BLAS**（[Dockerfile#L110](file:///d:/spaces/SpecWeave/apps/caffe-ffi-jupyter/Dockerfile#L110)）：builder 阶段 `conda install libopenblas` 默认 pthreads 变体。
  6. **CAFFE_FFI_ENABLE_DEBUG_LOG=ON**（[Options.cmake#L8](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/Options.cmake#L8)）：Release 构建仍启用 debug log 编译路径。
  7. **无默认线程配置**：容器启动时未设置 OMP_NUM_THREADS/OPENBLAS_NUM_THREADS，用户不知道最优配置。

## Functional Requirements
- **FR-1**: 在 caffe-ffi Options.cmake 中新增 `CAFFE_FFI_ENABLE_PERF_LOG` 选项（默认 OFF for Release），条件编译 conv_layer.cpp 中的统计循环、clock 计时、[CONV-PERF] INFO 日志
- **FR-2**: 修改 Dockerfile，builder 阶段 conda install 时显式指定 `libopenblas=*=*openmp*`，确保镜像默认使用 openmp 变体
- **FR-3**: 调整 Conv Forward OpenMP 分块策略：将 kMinChunk 从 32 降低到 8（或动态计算），并在 N>1 时支持 batch 维度并行
- **FR-4**: 在 CompilerConfig.cmake 中为 GCC/Clang Release 构建添加 `-march=native`（或 conda 安全的 `-mtune=generic -msse4.2 -mavx -mavx2 -mfma`），确保向量化
- **FR-5**: 在 editable-install.sh 中添加编译优化参数（-DCAFFE_FFI_ENABLE_PERF_LOG=OFF -DCMAKE_CXX_FLAGS_RELEASE 添加 -O3 等），并为 Release 构建关闭 CAFFE_FFI_ENABLE_DEBUG_LOG
- **FR-6**: 在容器环境（bashrc/entrypoint）中设置默认线程变量：`OMP_NUM_THREADS=$(nproc)` `OPENBLAS_NUM_THREADS=1`，用户可覆盖
- **FR-7**: 优化 im2col_fp32：移除内层边界检查（分块处理 padding 区域），添加 `#pragma omp simd` 提示

## Non-Functional Requirements
- **NFR-1（性能）**: ResNet50 单 batch 推理延迟（warmup=10, measure=50, OPENBLAS_NUM_THREADS=1, OMP_NUM_THREADS=容器核心数）mean ≤ 200ms（加速 ≥2× from 405ms），目标 ≤120ms
- **NFR-2（精度）**: 优化后 Top-5 预测类别与优化前完全一致，max_abs_error ≤ 1e-5（float32 精度范围内）
- **NFR-3（稳定性）**: 无 OpenBLAS 过订阅警告，无段错误，无 NaN/Inf 输出
- **NFR-4（可调试性）**: 设置 CAFFE_FFI_ENABLE_PERF_LOG=ON 时保留原有 [CONV-PERF] 日志和统计功能
- **NFR-5（构建时间）**: 编译时间增加不超过 30%（向量化和 -march=native 可能增加编译时间，但可接受）
- **NFR-6（镜像大小）**: Docker 镜像大小增加不超过 50MB（仅 BLAS 变体替换，无新依赖）

## Constraints
- **Technical**:
  - caffe-ffi 代码位于 `projects/xuanspace/libs/caffe-ffi/`（第一方子项目 submodule），需通过子项目开发流程修改
  - apps/caffe-ffi-jupyter（Dockerfile、scripts）位于主权区，可直接修改
  - CPU-only 平台，无 GPU 加速
  - 必须使用 OpenBLAS（conda-forge），不引入 MKL
  - Python 3.14、C++17、scikit-build-core 构建系统
- **Business**:
  - 优化后必须通过现有全部精度测试（pytest tests/python）
  - Docker 镜像构建不能破坏现有 Jupyter/SSH 功能
- **Dependencies**:
  - OpenBLAS openmp 变体（已在运行中容器验证可用）
  - GCC 支持 OpenMP 和 AVX2（容器内 cxx-compiler 已满足）

## Assumptions
- **A1**: 容器 CPU 支持 AVX2/FMA（现代 x86_64 服务器/桌面 CPU 均支持，conda-forge OpenBLAS DYNAMIC_ARCH 内核会自动选择）
- **A2**: caffex 性能基线（~21ms）使用的是系统 OpenBLAS（apt 安装的 libopenblas-dev），其编译选项包含 -O3 -march=native
- **A3**: 统计循环和计时开销是当前主要性能瓶颈之一（预计贡献 30-50% 额外延迟）
- **A4**: OpenMP 分块策略优化可带来 20-40% 并行效率提升
- **A5**: 用户接受在 Dockerfile 中固定 openmp 变体（不再默认 pthreads）

## Acceptance Criteria

### AC-1: 性能统计循环编译期消除
- **Given**: caffe-ffi 以 Release 模式构建且 CAFFE_FFI_ENABLE_PERF_LOG=OFF（默认）
- **When**: 执行 ResNet50 前向推理
- **Then**: conv_layer.cpp 中的 min/max/norm 统计循环和 high_resolution_clock 计时不生成代码（可通过 objdump/nm 验证或性能加速比验证）
- **Verification**: `programmatic`
- **Notes**: 设置 CAFFE_FFI_ENABLE_PERF_LOG=ON 时功能完整保留

### AC-2: Docker 镜像默认 OpenBLAS openmp 变体
- **Given**: 使用优化后的 Dockerfile 重新构建镜像
- **When**: 容器启动后执行 `conda list libopenblas`
- **Then**: 输出中 libopenblas build string 包含 `openmp`（如 `openmp_hd680484_0`），无过订阅警告
- **Verification**: `programmatic`

### AC-3: OpenMP 分块策略优化生效
- **Given**: OMP_NUM_THREADS=4, OPENBLAS_NUM_THREADS=1
- **When**: 运行 ResNet50 conv1（64 输出通道）前向
- **Then**: 实际使用的 OpenMP 线程数 ≥3（原策略只使用 2 线程）
- **Verification**: `programmatic`

### AC-4: ResNet50 性能加速 ≥2×
- **Given**: warmup=10 次, measure=50 次, 最优线程配置
- **When**: 运行 ResNet50 推理基准测试
- **Then**: mean 延迟 ≤ 200ms（较优化前 405ms 加速 ≥2×）
- **Verification**: `programmatic`

### AC-5: 精度不变
- **Given**: 优化前后使用相同权重（ResNet50 pretrained）
- **When**: 运行 Top-5 预测对比
- **Then**: 优化前后 Top-5 类别完全一致，max_abs_error ≤ 1e-5
- **Verification**: `programmatic`

### AC-6: 无过订阅警告
- **Given**: 默认线程配置（不设置任何 OPENBLAS/OMP 环境变量）
- **When**: 运行 ResNet50 推理并捕获 stderr
- **Then**: 输出中不包含 "BLAS : Program is Terminated. Because you tried to use multithreaded BLAS with multithreaded OpenMP" 或 "OpenBLAS Warning" 等过订阅警告
- **Verification**: `programmatic`

### AC-7: 默认线程配置合理
- **Given**: 全新容器启动，用户不设置任何 OMP/OPENBLAS 环境变量
- **When**: 运行 ResNet50 推理
- **Then**: 自动使用物理核心数（OMP_NUM_THREADS）且 BLAS 单线程，性能接近手动调优的最优配置
- **Verification**: `programmatic`

### AC-8: PERF_LOG 开关工作正常
- **Given**: 设置 CAFFE_FFI_ENABLE_PERF_LOG=ON 重新编译
- **When**: 运行推理
- **Then**: stderr 输出包含 `[CONV-PERF]` 日志行，包含每层的 min/max/norm 和 time 信息
- **Verification**: `programmatic`

## Open Questions
- [ ] **Q1**: caffe-ffi 的 editable-install 中如何区分 Release vs RelWithDebInfo 构建？当前 pyproject.toml 设置 cmake.build-type=Release，但用户可能以 Debug 模式开发。PERF_LOG 默认值是否应与 build type 关联（Release 默认 OFF，Debug 默认 ON）？
- [ ] **Q2**: `-march=native` 在 conda 环境中是否安全？conda-forge 包通常使用 `-mtune=generic` 以保证跨机器兼容。是否应使用更保守的 `-mavx2 -mfma -msse4.2` 替代 `-march=native`？
- [ ] **Q3**: im2col 优化（添加 omp simd、分块边界处理）的投入产出比如何？是否应放入 P2 阶段，先验证统计循环消除+OpenMP调优的效果？
- [ ] **Q4**: batch 维度（N）并行是否会引入线程同步开销？当 N=1 时（ResNet50 测试场景）不应启用；当 N>1 时才启用。需要确认实现复杂度。
