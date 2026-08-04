---
id: "caffe-ffi-tvm-integration"
title: "Caffe-FFI: TVM FFI 原生 Caffe 实现"
status: "in-progress"
progress: "M1-M9里程碑：M1-M6(v0.1.0基础完成)、M7(v1.1.0 COW零拷贝共享+内存追踪+562测试)、M8(v1.2.0 InsertSplits图变换+25层+P3-C Transformer)、M9(P3训练支持阶段完成：Backward已实现19类层892个测试，LeNet on MNIST端到端训练97.95%精度，CI流水线三平台含COW_PHASE3宏，C¹拐点防护，测试基础设施16.2x性能优化)；全量测试1646 passed/1 skipped；P3-B/C/D/E四阶段全部闭环，P3-E验收报告+P3总复盘+P4路线图已生成；GitHub Actions CI覆盖Linux/macOS/Windows三平台"
last_updated: "2026-08-04"
---

# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Product Requirement Document

## Overview
- **Summary**: 在 `projects/xuanspace/libs/caffe-ffi` 目录下创建一个以 TVM FFI 为核心基础设施的 Caffe 深度学习框架（从vendor/caffe/caffe-ffi萃取迁移为独立第一方项目）。该实现深度整合 TVM FFI 的对象系统、容器库、反射注册和内存管理机制，替代传统 Caffe 的 STL 容器和 Boost.Python/pybind11 绑定，提供现代化、跨语言、高性能的推理与训练框架。项目已完成M1-M6基础功能、M7 COW零拷贝共享机制、M8 InsertSplits图变换、M9(P3) Backward反向传播与LeNet端到端训练，当前处于P4（性能优化/更多层支持/应用示例）规划阶段。
- **Purpose**: 解决传统 Caffe 依赖重（Boost/GFlags/GLog等）、Python 绑定脆弱、数据结构不现代的问题，利用 TVM FFI 的通用跨语言 FFI 基础设施，构建一个轻量、高效、易于扩展和维护的 Caffe 推理与训练版本，支持零拷贝张量共享、写时复制（COW）内存安全、自动计算图变换（InsertSplits）。
- **Target Users**: 深度学习推理/训练工程师、需要在 Python 3.14+ 环境部署和微调 Caffe 模型的开发者、对框架底层实现感兴趣的研究者。
- **Current Status**: 🔄 **M1-M9：M1-M9全部完成，P4（优化/扩展）规划中**。
  - **M1-M6 (v0.1.0, 2026-07-29~30)**：20个Layer全部实现、TVM FFI最佳实践两阶段优化（双类模式/零拷贝/@register_object/三层日志 + 反射系统补全52方法/DLL边界修复）、MSVC Release编译通过、C++单元测试40/40通过、Docker开发环境(caffe-ffi-jupyter)、Docker Linux Python 3.14.6验证C++40/40+Python65/65全部通过。**CMake原子化重构（10个模块化cmake文件）由独立项目萃取迁移产出，2026-08-04在WSL docker验证通过**（详见 [MILESTONE_SUMMARY_CMake_REFACTOR_WSL_REGRESSION_20260804](../../../projects/xuanspace/libs/caffe-ffi/docs/summaries/MILESTONE_SUMMARY_CMake_REFACTOR_WSL_REGRESSION_20260804.md)）。
  - **M7 (v1.1.0, 2026-07-30)**：Copy-on-Write (COW) 零拷贝张量共享机制（ShareData/ShareDiff/Unshare/IsShared/RefCount/mutable_*自动COW克隆）、内存生命周期追踪工具(caffe_ffi.tools.memory)、21个COW测试用例、修复_tensor_to_numpy引用循环泄漏、Reshape COW失效修复、Docker Linux 561/562测试通过。
  - **M8 (v1.2.0, 2026-07-31)**：InsertSplits自动图变换（多消费方自动插入Split层）、18个边界情况测试、扩展至25个Layer（新增Crop/Deconv/LRN/Slice/Split）、P3-C Transformer测试套件(13个测试)、Sigmoid饱和精度修复（float32次正规数）、核心层诊断日志增强、InsertSplits算法文档、测试指南文档。
  - **M9 (P3阶段, 2026-08-01~2026-08-04 完成)**：Backward反向传播支持——**19类层Backward全部实现并验证（892个测试）**、LeNet on MNIST端到端训练(test acc **97.95%**)、P3-B/C/D/E四阶段闭环、P3-E验收报告+P3总复盘+P4路线图、GitHub Actions CI流水线(Linux/macOS/Windows三平台+Debug/Release+C++测试+ruff lint+C¹静态检查+COW_PHASE3宏)、测试基础设施性能优化(16.2x加速)、SetShapeOnly零拷贝reshape API、numpy RNN/LSTM参考实现、perf_monitor性能监控基础设施。

## Goals
- ✅ 基于 TVM FFI 对象系统（Object/ObjectPtr/ObjectRef）重构 Caffe 核心抽象（双类模式XxxObj+Xxx）
- ✅ 使用 TVM FFI 容器（Array/Shape/Tensor/String/Map）替代 STL 容器实现参数和 Blob 数据存储
- ✅ 利用 TVM FFI 反射系统实现 Python @register_object 自动绑定，消除 monkey patch
- ✅ 通过 TVM FFI Tensor (DLPack) 实现 Blob 数据存储，支持零拷贝 numpy 互操作
- ✅ Copy-on-Write (COW) 机制：O(1)张量共享、写时自动克隆、引用计数追踪、内存生命周期工具
- ✅ InsertSplits自动图变换：多消费方Blob自动插入Split层，18种边界情况覆盖，与原生Caffe行为对齐
- ✅ 采用 CMake + Ninja + scikit-build-core 构建系统，支持 Conda 环境
- ✅ 要求 Python 3.14+、protobuf >= 7.0.0，CPU-only 推理优先，训练支持进行中
- ✅ 支持25个Layer：Input/ReLU/InnerProduct/Softmax/Flatten/Conv/Pooling/BatchNorm/Scale/Bias/Sigmoid/TanH/PReLU/ELU/Dropout/Concat/Eltwise/Reshape/SoftmaxWithLoss/Accuracy/Crop/Deconv/LRN/Slice/Split
- ✅ BLAS 条件编译集成（有BLAS用cblas，无BLAS用纯C++ fallback），im2col/col2im实现
- ✅ caffemodel权重加载（CopyTrainedLayersFrom）
- ✅ 三层日志架构、Doxygen注释、错误处理增强、性能基准测试
- ✅ C++ header-only轻量测试框架（~100行0依赖），C++测试覆盖Blob/Net/NeuronLayers/InsertSplits/ObjectPtr迁移/Deconv/ZeroCopy/符号导出
- ✅ Windows DLL边界问题根治、Protobuf跨DLL隔离、Python MRO反射查找修复
- ✅ 独立项目萃取迁移完成：从vendor/caffe/caffe-ffi迁移到projects/xuanspace/libs/caffe-ffi
- ✅ Docker开发环境apps/caffe-ffi-jupyter（基于jupyter-ssh-base，SSH+Jupyter双服务）
- ✅ GitHub Actions CI流水线：Linux/macOS/Windows三矩阵、Release/Debug双构建、C++/Python测试、ruff lint、wheel构建、C¹拐点静态检查
- ✅ 测试基础设施性能优化：分层GC、CSV缓冲、perf_trace优化、C++日志抑制，16.2x加速
- ✅ C¹拐点防护：avoid_c1_discontinuity helper函数、ELU/PReLU/LeakyReLU数值梯度稳定性
- ✅ SetShapeOnly API：零拷贝形状修改（不重新分配内存）
- ✅ perf_monitor性能监控基础设施
- ✅ **M9(P3训练支持)已完成**：Backward反向传播完整实现与验证——19类层892个测试，核心层(InnerProduct/BN/SoftmaxWithLoss/激活/Conv/Pooling/结构层)梯度已验证，LeNet on MNIST端到端训练97.95%精度
- ✅ 核心层Backward完整测试覆盖（P0: Conv/Pooling; P1: SoftmaxWithLoss/Split; P2: 其余层）——19类层892测试全部通过
- ✅ 内存管理ASan验证 — 已完成（2026-08-04，ASan 构建 1647 passed / 0 内存安全错误，发现并修复 in-place InnerProduct 堆越界读）
- 🔄 BLAS路径性能基准验证 — 待完整BLAS环境
- ✅ 端到端真实模型推理+微调测试（LeNet/MNIST精度97.95%）— 已完成
- ⬜ RNN/LSTM层实现（proto定义+RecurrentLayer，numpy参考实现已就绪）
- ⬜ Solver训练流程（SGD/Adam等优化器）
- ⬜ v0.2.0(Beta)：40+层、三平台CI全覆盖、性能benchmark体系
- 🔄 **P4（优化/扩展）规划中**：性能优化（BLAS后端/多线程/COW推广）、能力扩展（更多激活/归一化/损失层/训练模式Dropout）、工程化（训练API封装/模型序列化/应用示例/文档完善）

## Non-Goals (Out of Scope)
- CUDA/GPU 支持（第一阶段仅 CPU，GPU 可作为未来扩展）
- 完整的分布式训练（多GPU/多节点）
- 与原始 BVLC Caffe 的完全 API 兼容（API 已现代化调整）
- LMDB/LevelDB/HDF5 等数据格式支持（可作为后续扩展）

## Background & Context

### 现有参考实现
1. **caffe-slim** (`projects/xuanspace/vendor/caffe/caffe-slim`):
   - 已裁剪为 CPU-only，使用 tvm-ffi 替代 Boost.Python 做绑定
   - 但核心数据结构仍使用 STL 容器，tvm-ffi 仅用于绑定层
   - 提供了 CMake 构建配置和大量 Layer 实现参考（75+ 个 Layer）

2. **tvm-ffi** (`projects/xuanspace/vendor/tvm-ffi`):
   - 提供 Object 引用计数对象系统、Array/Map/String/Shape/Tensor 容器
   - PackedFunc 类型擦除函数接口、Any 万能值类型
   - reflection 系统（ObjectDef/OverloadObjectDef/GlobalDef）自动 Python 绑定
   - memory.h 统一内存管理、make_object 对象分配
   - Tensor (DLPack) 张量容器，支持 DLPack 零拷贝互操作
   - C ABI 兼容，自动 Python 绑定生成

### TVM FFI 核心能力（已集成验证）
| 组件 | 功能 | caffe-ffi 中的使用 |
|------|------|-------------------|
| Object/ObjectPtr | 引用计数对象系统 + RTTI | BlobObj/LayerObj/NetObj 基类 |
| Shape/ShapeView | 引用计数形状容器 | Blob 维度表示 |
| Tensor (DLPack) | DLPack 兼容张量 | Blob data_tensor_/diff_tensor_ 数据存储（零拷贝numpy互操作+COW共享） |
| Array | 引用计数动态数组 | blobs/layers 容器、LayerTypeList等 |
| Map | 引用计数有序映射 | Net blob名称索引 |
| String | SSO 小字符串优化 | FFI 字符串桥接（替代std::string） |
| make_object | 统一对象分配 | Blob/Layer/Net 创建 |
| @register_object | 反射注册自动绑定 | Python端Blob/Layer/Net类定义 |
| GlobalDef/TVM_FFI_DLL_EXPORT_TYPED_FUNC | 全局函数注册 | 工厂/工具/日志/内存/COW相关函数导出 |
| TVM_FFI_DECLARE_OBJECT_INFO | 类型信息声明 | Blob(_FINAL)/Layer/Net 类型声明 |
| TVM_FFI_ICHECK/THROW | 错误处理 | 参数校验、网络初始化检查（含上下文信息） |
| TVM_FFI_STATIC_INIT_BLOCK | 静态初始化注册 | Layer 注册器、反射注册 |

### 版本演进历史

#### v0.1.0 (M1-M6, 2026-07-29~30) — 基础功能里程碑
- 20个Layer全部实现
- 双类模式重构、零拷贝Tensor、@register_object绑定
- 三层日志架构、Doxygen注释、错误处理增强
- 反射系统52方法完整注册（Blob 28 + Layer 8 + Net 16）
- Windows DLL边界根治、Protobuf跨DLL隔离、Python MRO修复
- C++ header-only测试框架（40个测试）
- Docker开发环境(caffe-ffi-jupyter)
- Docker Linux Python 3.14.6验证：C++40/40+Python65/65通过
- 性能基准：零拷贝~4µs访问，10M元素加速3749×

#### v1.1.0 (M7, 2026-07-30) — COW零拷贝共享里程碑
- Copy-on-Write机制完整实现：
  - `ShareData`/`ShareDiff`: O(1)零拷贝张量共享
  - `UnshareData`/`UnshareDiff`: 显式深拷贝
  - `IsDataShared`/`IsDiffShared`: 共享状态查询
  - `DataRefCount`/`DiffRefCount`: 引用计数查询
  - `mutable_data_tensor()`/`mutable_diff_tensor()`: 写时自动COW克隆
- 内存生命周期追踪工具(`caffe_ffi.tools.memory`)：BlobRef/tracked_blob/blob_snapshot/mem_check
- 内存压力测试：500次create/fill/destroy循环零泄漏
- 修复_tensor_to_numpy引用循环泄漏（_blob_ref挂载到numpy ctypes数组而非LP_c_float指针）
- Reshape COW失效修复（仅当shape变化时才清除共享标记）
- 21个COW测试用例
- Docker Linux验证：561/562测试通过

#### v1.2.0 (M8, 2026-07-31) — 图变换与扩展里程碑
- InsertSplits自动图变换Pass：
  - 多消费方Blob自动插入Split层
  - 命名约定与原生Caffe完全对齐
  - 18个边界情况测试（零消费死端、单消费不拆分、in-place ReLU多消费、级联拆分、幂等性、Inception嵌套、多外部输入等）
  - 外部输入split顺序修复（按输入声明顺序而非反向消费顺序）
- 扩展至25个Layer：新增Crop/Deconv/LRN/Slice/Split
- P3-C Transformer测试套件：位置编码、缩放点积注意力、多头投影、Transformer Encoder Block（13个测试）
- Sigmoid饱和精度修复：float32次正规数处理（sigmoid(-88)≈6e-39非精确0、x≥17精确1.0）
- 核心层诊断日志增强（shape mismatch详细错误信息）
- InsertSplits Pass 2b详细日志（外部输入split移动前后层顺序）
- 文档：INSERT_SPLITS_GRAPH_TRANSFORM.md算法参考、TESTING_GUIDELINES.md测试指南

#### M9 (P3, 2026-08-01~2026-08-04 完成) — 训练支持里程碑
- **Backward反向传播**（19类层全部实现并验证，892个测试）：
  - 激活函数：ReLU/Sigmoid/TanH/PReLU/ELU（含C¹拐点防护）
  - 核心层：InnerProduct（梯度解析验证通过，23个测试）、BatchNorm（实现+测试）、SoftmaxWithLoss（测试完成）
  - 卷积/池化：Conv/Pooling（数值验证完成）
  - 结构层：Split/Slice/Crop/Deconv/LRN/Scale/Bias/Concat/Eltwise/Reshape/Flatten（完整验证）
  - [ACTIVATION-PERF]调试日志：diff_in/diff_out/time结构化输出
- **端到端训练**：LeNet on MNIST 训练 test acc **97.95%**（loss 2.32→0.04，-98.3%），证明19类层Backward组合后梯度流正确
- **P3-B/C/D/E四阶段闭环**：P3-E验收报告、P3阶段总复盘、P4路线图已生成
- **31个失败测试修复**：28个Blob对象协议问题（net.Forward()→net.forward()）+ 3个构建缺宏问题（CAFFE_FFI_ENABLE_COW_PHASE3）
- **CI回归基线修复**：ci.yml构建矩阵/cpp-tests/nightly三处添加-DCAFFE_FFI_ENABLE_COW_PHASE3=ON
- **C¹拐点防护**：
  - `avoid_c1_discontinuity` helper函数：将|x-kink|<margin*h的点推离拐点
  - 支持多拐点、幂等安全
  - CI静态检查（check_c1_kink_protection.py）：正则检测ELU(α≠1)/PReLU/LeakyReLU(negative_slope>0)三类C¹不连续激活是否使用helper或豁免注释
  - ELU拐点稳定性专项测试(test_elu_kink_stability.py)
- **GitHub Actions CI流水线**：
  - 三平台矩阵：Linux(Ubuntu)/macOS/Windows
  - 双构建类型：Release/Debug
  - C++测试(Linux only)、Python全量测试、激活Backward专项测试
  - [ACTIVATION-PERF]日志验证（Debug build）
  - wheel构建与上传(Linux Release)
  - ruff lint + format检查
  - C¹拐点防护静态检查
  - InsertSplits DAG仿真交叉验证（零依赖Python参考实现）
  - ccache编译加速
- **测试基础设施性能优化**（P3-B 134s→8.27s，16.2x加速）：
  - 分层GC策略：quick/full/off三档，默认quick仅gen0
  - perf_trace优化：采样间隔调整、RSS线程可选
  - CSV缓冲：20行批量flush，减少I/O syscall
  - C++ InsertSplits日志抑制（Release模式）
  - 最佳实践文档：test-infra-performance-optimization.md
- **SetShapeOnly API**：零拷贝形状修改（不重新分配内存）
- **perf_monitor**：性能监控基础设施
- **numpy参考实现**：_numpy_bn_reference.py(BatchNorm)、_numpy_rnn_reference.py(RNN/LSTM，8个自测试通过)
- **构建兼容性修复**：Protobuf版本/编译器flag兼容、跨机器构建设置指南
- **COW Phase 2/3设计**：Split层COW集成、SetShapeOnly与COW协同
- **全量测试结果**：1646 passed, 1 skipped, 0 failures（Docker Linux + 本地py314验证）

#### P4 (规划中) — 优化与扩展
- **性能优化**：全量层性能基准、GEMM加速（BLAS/MKL后端）、多线程并行（OpenMP）、COW全量应用
- **能力扩展**：更多激活层（LeakyReLU/GELU/Softplus）、更多归一化层（GroupNorm/LayerNorm/InstanceNorm）、更多损失层（Hinge/Euclidean/Multi-Logistic）、训练模式Dropout
- **工程化**：训练API封装（Trainer/Solver）、模型序列化（.caffemodel兼容）、更多应用示例（ResNet/分类/回归）、文档完善
- **里程碑**：M1性能基线+GEMM加速、M2多线程+内存优化、M3能力扩展、M4工程化
- **详细路线图**：[P4 阶段路线图](p4-roadmap.md)（P4-1~12 任务分解、依赖、风险与 DoD）

### 已实现的核心功能
- **Blob**: 双类模式(BlobObj+Blob)，Tensor(DLPack)存储data/diff，COW零拷贝共享，CPUMemAlloc自定义分配器，支持Reshape/SetShapeOnly/FromProto/ToProto/Update/ShareData/ShareDiff/Unshare/IsShared/RefCount/mutable_*，通过DLPack实现numpy零拷贝互操作，内存生命周期追踪
- **Layer**: 双类模式(LayerObj+Layer)，NVI生命周期（SetUp→LayerSetUp→Reshape→Forward→Backward），LayerRegistry工厂模式，REGISTER_LAYER_CLASS宏，Array<Blob> blobs_容器，name()方法，25个Layer实现
- **Net**: 双类模式(NetObj+Net)，从prototxt/NetParameter初始化，DAG拓扑构建+InsertSplits自动变换，顺序Forward+Backward，Map<String,int64_t>名称索引，CopyTrainedLayersFrom权重加载，ShareData自动共享机制
- **25个Layer全部实现**:
  - 基础(5): Input/ReLU/InnerProduct/Softmax/Flatten
  - 计算密集(7): Conv/Pooling/BatchNorm/Scale/Bias/Accuracy/SoftmaxWithLoss
  - 激活/操作(8): Sigmoid/TanH/PReLU/ELU/Dropout/Concat/Eltwise/Reshape
  - 扩展(5): Crop/Deconv/LRN/Slice/Split
- **Python层**: @register_object装饰器定义Blob/Layer/Net，_native_method()辅助函数，blob.py/layer.py/net.py简化重新导出，_is_native只读property，COW感知的mutable_*方法，backward()方法
- **IO**: read_net/read_net_prototxt/read_net_prototxt_binary/read_net_from_prototxt/read_net_from_binary/net_param_from_string/net_from_param
- **Classifier**: 高层分类器接口（mean/input_scale/raw_scale/channel_swap/oversample/predict）
- **三层日志架构**: C++log.hpp(RAII Logger+编译期门控+6级日志+组件标签)、FFI桥接(SetLogLevel/GetLogLevel)、Python配置层，[ACTIVATION-PERF]Backward性能日志
- **错误处理**: TVM_FFI_ICHECK参数校验，错误信息含Blob ID/层名/文件名/shape mismatch详情
- **BLAS集成**: 条件编译CAFFE_USE_BLAS，有BLAS用cblas_sgemm/gemv，无BLAS用纯C++ fallback；im2col/col2im已实现
- **COW机制**: ShareData/ShareDiff/Unshare/IsShared/RefCount/mutable_*自动克隆、内存追踪工具
- **InsertSplits**: 自动图变换Pass、18边界情况测试、与原生Caffe对齐
- **CMake构建**: 10个模块化CMake文件（Tests/WindowsDllCopy/TargetBuild/ProtoCompile/Options/Install/DetectOpenBLAS/DetectBLAS/Dependencies/CompilerConfig）、find_package(tvm_ffi CONFIG REQUIRED)默认、本地开发add_subdirectory fallback、tvm_ffi_configure_target()、Windows DLL精细复制
- **CI/CD**: GitHub Actions三平台流水线、ccache加速、wheel构建
- **测试**: C++ header-only框架（含高精度耗时统计+Per-suite汇总+Top 5 slowest）、Python pytest（561/562通过）、测试基础设施16.2x性能优化、C¹拐点防护检查
- **性能基准**: 零拷贝恒定~4µs访问、10M元素加速3749×、COW O(1)共享、P3-B测试16.2x加速
- **文档**: 性能报告(中文)、COW迁移报告、InsertSplits算法文档、测试指南、构建兼容性报告、测试基础设施性能优化最佳实践、多个回溯报告

## Functional Requirements

### 已实现 ✅
- **FR-1**: 核心 Blob 张量类，双类模式BlobObj+Blob，Tensor(DLPack)存储data/diff双缓冲，COW零拷贝共享
- **FR-2**: Layer 基类，双类模式LayerObj+Layer，通过LayerRegistry+REGISTER_LAYER_CLASS宏注册工厂，Forward+Backward双生命周期
- **FR-3**: Net 计算图类，双类模式NetObj+Net，管理Layer DAG拓扑+InsertSplits自动变换、Blob创建、前向+反向执行
- **FR-4**: 使用 tvm::ffi::Shape 替代 std::vector 表示形状，Blob.Reshape接受Shape参数，SetShapeOnly零拷贝形状修改
- **FR-5**: Net 内部使用 tvm::ffi::Map 管理 Blob 名称索引
- **FR-6**: 通过 tvm::ffi 反射系统 + @register_object 自动导出 Python 绑定，消除monkey patch
- **FR-7**: 使用 tvm::ffi::make_object 统一对象创建，自定义 CPUMemAlloc 分配器
- **FR-8**: Protobuf >= 7.0.0 用于解析 .prototxt 和 .caffemodel
- **FR-9**: 全部25个Layer实现（20基础+5扩展）
- **FR-10**: Python 包 caffe_ffi 提供高层 API：Net加载、Blob numpy零拷贝访问、Forward/Backward推理训练、Classifier
- **FR-11**: CMake 构建系统模块化（9个.cmake文件），支持find_package(tvm_ffi CONFIG REQUIRED)
- **FR-12**: scikit-build-core 配置构建 Python wheel
- **FR-13**: BLAS条件编译集成，im2col/col2im实现
- **FR-14**: Python 单元测试（pytest）覆盖Blob/Layer/Net/COW/InsertSplits/Backward/复杂拓扑/Transformer/边界情况
- **FR-15**: 三层日志架构+C++核心+FFI桥接+Python配置，[ACTIVATION-PERF]Backward性能日志
- **FR-16**: Doxygen注释覆盖核心公共API
- **FR-17**: 错误处理增强（TVM_FFI_ICHECK+上下文信息+shape mismatch诊断）
- **FR-18**: C++ header-only轻量测试框架（0依赖），含高精度耗时统计+Per-suite汇总+Top 5 slowest报告
- **FR-19**: Windows DLL边界问题根治：LayerRegistry单例移至.cpp实现，Protobuf解析在DLL内隔离
- **FR-20**: Python MRO反射查找修复：派生类可正确访问基类注册的方法
- **FR-21**: Docker开发环境（apps/caffe-ffi-jupyter）：基于jupyter-ssh-base，双阶段构建，SSH+Jupyter双服务
- **FR-22**: 工程化工具链：统一结构化日志库（Bash+PowerShell）、WSL一键部署、诊断脚本
- **FR-23**: CAFFE_FFI_DISABLE_BACKTRACE环境变量支持
- **FR-24**: **COW零拷贝共享机制**：ShareData/ShareDiff/Unshare/IsShared/RefCount/mutable_*自动克隆、CAFFE_FFI_ENABLE_COW环境变量、内存追踪工具
- **FR-25**: **InsertSplits自动图变换**：多消费方Blob自动插入Split层、18边界情况测试、与原生Caffe行为对齐、viz_insert_splits.py可视化验证
- **FR-26**: **Backward反向传播**：19类层Backward_cpu实现，Net::backward()逆序执行，892个测试验证
- **FR-27**: **C¹拐点防护**：avoid_c1_discontinuity helper、CI静态检查、ELU拐点稳定性测试
- **FR-28**: **GitHub Actions CI**：Linux/macOS/Windows三平台、Release/Debug、C++/Python测试、lint、wheel构建、COW_PHASE3宏
- **FR-29**: **SetShapeOnly API**：零拷贝形状修改（不重新分配内存）
- **FR-30**: **perf_monitor性能监控**基础设施
- **FR-31**: **测试基础设施性能优化**：分层GC、CSV缓冲、perf_trace采样优化

### 已完成 ✅
- **FR-32**: Backward梯度完整数值验证：Conv/Pooling/SoftmaxWithLoss等19类层Backward与numpy参考对比
- **FR-33**: 训练循环最小可用：LeNet/MNIST端到端训练验证，test acc 97.95%

### 待后续补充 ⬜
- InnerProduct/Conv使用BLAS gemm的性能基准验证
- RNN/LSTM层C++实现（numpy参考已就绪）
- Solver优化器（SGD/Adam等）
- 更多层支持（GELU/GroupNorm/LayerNorm等）
- 训练API封装（Trainer/Solver）与模型序列化

## Non-Functional Requirements

- ✅ **NFR-1**: 性能：零拷贝Tensor访问恒定~3-6µs，COW共享O(1)，MLP Forward~0.5ms，P3-B测试16.2x加速
- ✅ **NFR-2**: 构建：MSVC Release/GCC 14/Clang编译成功，零错误零新增警告
- ✅ **NFR-3**: 兼容性：Windows (MSVC 2026)、Linux (x86_64, GCC 14.3.0 Docker/Python 3.14.6)、macOS 已验证（CI三平台）
- ✅ **NFR-4**: 代码质量：C++17 标准，无编译新增警告，ruff lint/format通过
- ✅ **NFR-5**: 依赖最小化：核心依赖 tvm-ffi(apache-tvm-ffi)、Protobuf >= 7.0.0、numpy、pytest
- ✅ **NFR-6**: Python 版本：严格 >= 3.14（CI Python 3.14验证通过）
- ✅ **NFR-7**: 模块化：Layer实现可独立添加/移除（layers/目录 + REGISTER_LAYER_CLASS宏）
- ✅ **NFR-8**: 文档：README.md + 多份性能/设计/回溯报告 + Doxygen注释 + 测试指南
- ✅ **NFR-9**: DLL部署：Windows下自动复制tvm_ffi/protobuf/absl/utf8_range DLL到包目录
- ✅ **NFR-10**: CI/CD：GitHub Actions三平台流水线，含C++/Python测试、lint、wheel构建
- ✅ **NFR-11**: 数值稳定性：C¹拐点防护、饱和区精确相等断言、ULP阈值规范

## Constraints

- **Technical**:
  - C++17 标准（与 tvm-ffi 一致）
  - CMake >= 3.26
  - Python >= 3.14
  - protobuf >= 7.0.0（需 absl + utf8_range 依赖）
  - Ninja 构建生成器
  - scikit-build-core >= 0.10 用于 Python 包构建
  - TVM FFI 优先find_package，本地开发可fallback到add_subdirectory
  - CPU-only（第一阶段不涉及 CUDA）
  - BLAS库可选（OpenBLAS/MKL/cblas），有BLAS加速，无BLAS纯C++ fallback
  - Windows开发环境需设置`KMP_DUPLICATE_LIB_OK=TRUE`
  - COW机制通过CAFFE_FFI_ENABLE_COW环境变量控制（默认ON）
  - C¹拐点防护：CI流水线必须包含check_c1_kink_protection.py静态检查
- **Business**:
  - 代码位于 projects/xuanspace/libs/caffe-ffi（独立第一方项目）
  - 参考 caffe-slim 的 Layer 实现逻辑
  - 为后续 GPU 扩展保留接口（Forward_gpu/Backward_gpu 虚函数）
  - Docker开发环境位于 apps/caffe-ffi-jupyter，基于jupyter-ssh-base
  - WSL/Docker为推荐开发和构建环境
  - GitHub Actions CI为规范验证环境
- **Dependencies**:
  - apache-tvm-ffi > 0.1.12（已安装包，find_package）
  - Protobuf >= 7.0.0 + absl + utf8_range
  - BLAS (OpenBLAS/MKL/cblas) — 可选
  - CMake + Ninja
  - scikit-build-core（Python 构建）
  - numpy >= 2.3（Python 端）
  - pytest（运行时依赖）
  - ruff（开发/lint依赖）

## Assumptions (验证结果)
- ✅ tvm-ffi 可通过apache-tvm-ffi pip包安装，`python -m tvm_ffi.config --cmakedir`可用
- ✅ Conda 环境可安装 Python 3.14 和 protobuf 7.0.0+
- ✅ caffe-slim 的 Layer 计算逻辑可复用并适配tvm-ffi对象系统
- ✅ caffe.proto 保持与原始 Caffe 兼容以支持现有模型文件
- ✅ 预生成的 caffe_pb2.py 提交仓库，开箱即用
- ✅ Python-only fallback模式正常工作
- ✅ COW机制在in-place ReLU、Split多消费方等复杂场景下正确工作
- ✅ InsertSplits与原生Caffe行为完全对齐（18边界情况验证）
- ✅ 19类Layer的Backward实现可在Python 3.14/GCC 14环境编译通过（892个测试验证）

## Acceptance Criteria

### ✅ 已达成
- **AC-1**: 项目骨架与构建系统 — CMakeLists.txt + 9个模块化.cmake，可配置编译，scikit-build-core可构建wheel
- **AC-2**: Blob张量类基于TVM FFI双类模式+COW — BlobObj+Blob，Tensor存储，Reshape/SetShapeOnly/COW共享，零拷贝numpy互操作
- **AC-3**: Layer注册通过LayerRegistry — REGISTER_LAYER_CLASS宏正常注册，CreateLayer可动态创建25种Layer实例
- **AC-4**: Net基础前向+caffemodel加载+InsertSplits — 从prototxt加载、CopyTrainedLayersFrom、Forward、自动图变换
- **AC-5**: Python @register_object绑定 — import caffe_ffi正常，Blob/Layer/Net通过@_reg装饰器定义，无monkey patch
- **AC-6**: Python 3.14 + protobuf 7.0.0兼容性 — CI三平台+Docker验证通过
- **AC-7**: 全部25个Layer Forward正确性 — 单测通过，MLP/Transformer集成测试通过
- **AC-8**: TVM FFI最佳实践优化完成 — 双类模式、零拷贝、@register_object、三层日志、COW、InsertSplits
- **AC-9**: 文档完整性 — README.md + 多份技术报告 + Doxygen注释 + 测试指南
- **AC-10**: Python测试通过 — Docker Linux 561/562通过（1 skipped），CI三平台验证
- **AC-11**: C++ ctest单元测试通过 — header-only框架，覆盖Blob/Net/Neuron/InsertSplits/Deconv/ZeroCopy/符号导出
- **AC-12**: CMake支持find_package(tvm_ffi CONFIG REQUIRED)
- **AC-17**: 独立项目萃取迁移完成 — vendor→libs/caffe-ffi，标准结构对齐npu-ffi
- **AC-18**: Docker开发环境完成 — apps/caffe-ffi-jupyter基于jupyter-ssh-base，SSH+Jupyter双服务
- **AC-19**: Docker Linux验证通过 — 561/562测试通过
- **AC-24**: COW机制验证通过 — 21个测试、内存压力测试零泄漏、in-place场景正确
- **AC-25**: InsertSplits验证通过 — 18个边界情况测试、与原生Caffe对齐、DAG仿真交叉验证
- **AC-27**: C¹拐点防护验证通过 — avoid_c1_discontinuity helper、CI静态检查、ELU稳定性测试
- **AC-28**: GitHub Actions CI三平台通过 — Linux/macOS/Windows、Release/Debug、C++/Python/lint/wheel、COW_PHASE3宏

### ✅ 已达成
- **AC-26**: Backward梯度正确性 — 19类层Backward全部验证通过（892个测试）
- **AC-33**: 端到端训练最小可用 — LeNet/MNIST训练精度97.95%验证通过
- **AC-16**: 端到端真实模型推理+训练（LeNet/MNIST>95%精度）— 97.95%达成

### 待后续达成 ⬜
- **AC-13**: BLAS集成后Convolution/InnerProduct性能基准
- **AC-14**: 内存管理ASan验证
- **AC-RNN**: RNN/LSTM层实现
- **AC-Solver**: Solver优化器实现

## Open Questions (Resolved & Remaining)

### 已解决
- [x] tvm-ffi container/Tensor是否可直接用于Blob数据存储？→ 是的，Tensor::FromNDAlloc+CPUMemAlloc，DLPack零拷贝
- [x] protobuf 7.0.0的C++ API是否可用？→ 可用，需同时链接absl和utf8_range
- [x] 是否需要提供caffe.proto自定义版本？→ 复用caffe-slim精简版
- [x] Python包名确定为caffe_ffi？→ 是
- [x] 模型序列化格式？→ 标准protobuf二进制，CopyTrainedLayersFrom加载
- [x] Python绑定使用@c_class还是@register_object？→ @register_object(@_reg)标准模式
- [x] 是否保留纯Python fallback？→ 是，自动检测C++扩展可用性
- [x] 双类模式重构是否兼容现有继承体系？→ Layer使用TVM_FFI_DECLARE_OBJECT_INFO，_type_child_slots=25支持所有子类
- [x] CMake是否必须完全移除add_subdirectory？→ 本地开发保留fallback，优先find_package
- [x] COW机制如何与in-place操作共存？→ Reshape不清空共享标记（除非shape变化）、mutable_*自动克隆
- [x] InsertSplits如何处理多外部输入？→ 先收集所有外部输入split，在position 0批量插入
- [x] C¹不连续激活函数的数值梯度如何稳定？→ avoid_c1_discontinuity推离拐点+CI静态检查
- [x] 测试基础设施性能瓶颈在哪？→ 不在业务逻辑（Net创建0.5ms），而在观测基础设施（GC/线程/IO）——分层GC+缓冲优化16.2x
- [x] net.Forward()与net.forward()返回类型差异？→ 大写Forward返回Blob对象，小写forward返回numpy数组，测试需统一用forward或用to_numpy()兼容
- [x] Conv/Pooling Backward能否通过数值验证？→ 已通过，19类层Backward全部892个测试验证
- [x] LeNet/MNIST端到端训练能否达标？→ 已达97.95%精度，损失2.32→0.04

### 待解决
- [ ] Conv/Pooling Backward的BLAS后端在Linux环境下的性能验证
- [ ] 是否需要提供从caffemodel到numpy权重字典的导出工具？
- [ ] RNN/LSTM的proto定义是否需要扩展？
- [ ] P4阶段性能优化优先级（BLAS后端/多线程/COW推广）如何排序？
