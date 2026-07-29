---
id: "caffe-ffi-tvm-integration"
title: "Caffe-FFI: TVM FFI 原生 Caffe 实现"
status: "completed"
progress: "M1-M6里程碑全部完成：核心功能+TVM FFI最佳实践+P1反射系统补全+DLL边界修复+C++40/Python101测试通过+独立项目萃取迁移+Docker开发环境(caffe-ffi-jupyter)；Docker Linux Python 3.14.6环境验证：C++40/40+Python65/65全部通过，含Per-suite耗时统计和Top 5 slowest报告；WSL/Docker一键部署脚本完成，SSH+Jupyter双服务保留；零拷贝10M元素加速3749x，FFI调用开销1-2µs"
last_updated: "2026-07-30"
---

# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Product Requirement Document

## Overview
- **Summary**: 在 `projects/xuanspace/libs/caffe-ffi` 目录下创建一个以 TVM FFI 为核心基础设施的 Caffe 深度学习框架 CPU 推理版本（从vendor/caffe/caffe-ffi萃取迁移为独立第一方项目）。该实现深度整合 TVM FFI 的对象系统、容器库、反射注册和内存管理机制，替代传统 Caffe 的 STL 容器和 Boost.Python/pybind11 绑定，提供现代化、跨语言、高性能的推理框架。后续通过 TVM FFI 最佳实践优化阶段（caffe-ffi-optimization spec），完成双类模式重构、零拷贝Tensor、@register_object绑定、三层日志架构、Doxygen注释、错误处理增强等改进，并构建Docker开发环境（apps/caffe-ffi-jupyter）。
- **Purpose**: 解决传统 Caffe 依赖重（Boost/GFlags/GLog等）、Python 绑定脆弱、数据结构不现代的问题，利用 TVM FFI 的通用跨语言 FFI 基础设施，构建一个轻量、高效、易于扩展和维护的 Caffe 推理版本。
- **Target Users**: 深度学习推理工程师、需要在 Python 3.14+ 环境部署 Caffe 模型的开发者、对框架底层实现感兴趣的研究者。
- **Current Status**: ✅ **M1-M6全部完成**。核心骨架搭建完成，20个Layer全部实现，TVM FFI最佳实践两阶段优化完成（P0双类模式/零拷贝/@register_object/三层日志 + P1反射系统补全52方法/DLL边界修复/C++单元测试40个/Protobuf跨DLL隔离/Python MRO修复），MSVC Release编译通过，C++单元测试40/40通过，C++模式pytest 101个测试通过（纯Python模式83 passed, 19 skipped, 0 failed），MLP端到端验证成功，性能基准测试完成：FFI调用开销1-2µs，零拷贝访问恒定~4µs，10M float32元素零拷贝比拷贝快**3749×**（1M元素场景15×加速）。caffe-slim零拷贝改造代码草案（含8类内存日志标签）已生成，FFI零拷贝桥接模式已萃取为4个可复用模式，P1优化萃取4个Windows DLL开发模式。C++ header-only轻量测试框架（~100行0依赖）实现，40个C++测试覆盖Blob 22个+Net 18个核心场景。Windows DLL边界问题根治：LayerRegistry单例移至.cpp实现，Protobuf解析在DLL内隔离。反射系统完整补全：Blob(28)+Layer(8)+Net(16)共52个公共方法注册，所有方法带docstring，C++为唯一可信源。Python MRO反射查找修复，派生类可访问基类方法。独立项目萃取迁移完成：从`vendor/caffe/caffe-ffi`迁移到`projects/xuanspace/libs/caffe-ffi`，CMake构建系统独立化（find_package(tvm_ffi CONFIG REQUIRED)默认模式），标准项目结构对齐npu-ffi。Docker开发环境`apps/caffe-ffi-jupyter`基于jupyter-ssh-base构建完成：双阶段builder+runtime构建，Python 3.14+ Miniconda环境，保留SSH+Jupyter双服务，editable源码挂载，RPATH+ldconfig+LD_LIBRARY_PATH三重共享库路径保障，test-cpp-tests.sh集成C++/Python单元测试执行，统一结构化日志库（Bash+PowerShell双版本），WSL一键部署脚本wsl-deploy.sh/deploy.ps1，环境诊断脚本diagnose.sh/diagnose.ps1，WSL-DEPLOY-GUIDE.md部署指南。Docker Linux Python 3.14.6环境完整验证：C++单元测试40/40通过（含Per-suite耗时统计和Top 5 slowest报告），Python单元测试test_python_api.py 65/65通过（含耗时统计），CAFFE_FFI_DISABLE_BACKTRACE环境变量解决Python unittest兼容性问题。

## Goals
- ✅ 基于 TVM FFI 对象系统（Object/ObjectPtr/ObjectRef）重构 Caffe 核心抽象（双类模式XxxObj+Xxx）
- ✅ 使用 TVM FFI 容器（Array/Shape/Tensor/String/Map）替代 STL 容器实现参数和 Blob 数据存储
- ✅ 利用 TVM FFI 反射系统实现 Python @register_object 自动绑定，消除 monkey patch
- ✅ 通过 TVM FFI Tensor (DLPack) 实现 Blob 数据存储，支持零拷贝 numpy 互操作
- ✅ 采用 CMake + Ninja + scikit-build-core 构建系统，支持 Conda 环境
- ✅ 要求 Python 3.14+、protobuf >= 7.0.0，CPU-only 推理优先
- ✅ 支持20个核心推理Layer（Input/ReLU/InnerProduct/Softmax/Flatten/Conv/Pooling/BatchNorm/Scale/Bias/Sigmoid/TanH/PReLU/ELU/Dropout/Concat/Eltwise/Reshape/SoftmaxWithLoss/Accuracy）
- ✅ BLAS 条件编译集成（有BLAS用cblas，无BLAS用纯C++ fallback），im2col/col2im实现
- ✅ caffemodel权重加载（CopyTrainedLayersFrom）
- ✅ caffe-ffi-optimization阶段完成：三层日志架构、Doxygen注释、错误处理增强、性能基准测试
- ✅ Conda环境配置完善：environment.yml修正编译器/BLAS依赖，添加镜像源注释，创建conda_build.bat/sh三阶段构建脚本
- ✅ C++ 单元测试框架（header-only轻量框架，0依赖）：40个测试用例（Blob 22个+Net 18个），不依赖gtest
- ✅ Windows DLL边界问题根治：LayerRegistry单例移至.cpp实现，解决跨DLL双实例问题
- ✅ 反射系统完整补全：Blob(28方法)+Layer(8方法)+Net(16方法)=52个公共方法注册到反射系统
- ✅ Protobuf跨DLL解析隔离：DLL内提供ReadNetParamsFromTextString/File，消除跨DLL静态初始化崩溃
- ✅ Python MRO反射查找修复：派生类（如ReLULayer）可正确访问基类Layer注册的方法
- ✅ 七概念方法论（R→I→E→C→A→F→V）应用于优化过程，生成10章结构化任务执行总结报告
- ✅ **M6: 独立项目萃取迁移**：从vendor/caffe/caffe-ffi萃取为独立第一方项目libs/caffe-ffi
- ✅ **Docker开发环境**：apps/caffe-ffi-jupyter基于jupyter-ssh-base，SSH+Jupyter双服务，Python 3.14+
- ✅ **Docker Linux验证**：Python 3.14.6环境，C++40测试+Python65测试全部通过，含耗时统计
- ✅ **工程化工具链**：统一结构化日志库、WSL一键部署脚本、诊断脚本、部署指南文档
- 🔄 内存管理ASan验证 — 待Linux/GCC环境
- 🔄 BLAS路径性能基准验证 — 待完整BLAS环境
- 🔄 端到端真实模型推理测试（LeNet/MNIST精度）— 待数据集准备

## Non-Goals (Out of Scope)
- CUDA/GPU 支持（第一阶段仅 CPU，GPU 可作为未来扩展）
- 完整的训练功能（Solver 训练流程仅保留接口，推理优先）
- 与原始 BVLC Caffe 的完全 API 兼容（API 已现代化调整）
- LMDB/LevelDB/HDF5 等数据格式支持（可作为后续扩展）
- 多 GPU 分布式训练/推理

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
| Tensor (DLPack) | DLPack 兼容张量 | Blob data_tensor_/diff_tensor_ 数据存储（零拷贝numpy互操作） |
| Array | 引用计数动态数组 | blobs/layers 容器、LayerTypeList等 |
| Map | 引用计数有序映射 | Net blob名称索引 |
| String | SSO 小字符串优化 | FFI 字符串桥接（替代std::string） |
| make_object | 统一对象分配 | Blob/Layer/Net 创建 |
| @register_object | 反射注册自动绑定 | Python端Blob/Layer/Net类定义 |
| GlobalDef/TVM_FFI_DLL_EXPORT_TYPED_FUNC | 全局函数注册 | 14个工厂/工具/日志函数导出 |
| TVM_FFI_DECLARE_OBJECT_INFO | 类型信息声明 | Blob(_FINAL)/Layer/Net 类型声明 |
| TVM_FFI_ICHECK/THROW | 错误处理 | 参数校验、网络初始化检查（含上下文信息） |
| TVM_FFI_STATIC_INIT_BLOCK | 静态初始化注册 | Layer 注册器、反射注册 |

### 已完成的核心实现（含optimization阶段改进）
- **Blob**: 双类模式(BlobObj+Blob)，使用tvm::ffi::Tensor存储data/diff，CPUMemAlloc自定义分配器，支持Reshape/FromProto/ToProto/Update，通过DLPack实现numpy零拷贝互操作，data_tensor()/diff_tensor()直接返回Tensor
- **Layer**: 双类模式(LayerObj+Layer)，NVI生命周期（SetUp→LayerSetUp→Reshape→Forward_cpu），LayerRegistry工厂模式，REGISTER_LAYER_CLASS宏，Array<Blob> blobs_容器，新增name()方法
- **Net**: 双类模式(NetObj+Net)，从prototxt/NetParameter初始化，DAG拓扑构建，顺序Forward，Map<String,int64_t>名称索引，CopyTrainedLayersFrom权重加载
- **20个Layer全部实现**: Input/ReLU/InnerProduct/Softmax/Flatten/Conv(im2col+gemm)/Pooling(Max/Ave)/BatchNorm/Scale/Bias/Sigmoid/TanH/PReLU/ELU/Dropout/Concat/Eltwise/Reshape/SoftmaxWithLoss/Accuracy
- **Python层**: @register_object装饰器定义Blob/Layer/Net，_native_method()辅助函数通过__tvm_ffi_type_info__访问C++方法，blob.py/layer.py/net.py简化为重新导出，_is_native只读property检测模式
- **IO**: read_net/read_net_prototxt/read_net_prototxt_binary/read_net_from_prototxt/read_net_from_binary/net_param_from_string/net_from_param
- **Classifier**: 高层分类器接口（mean/input_scale/raw_scale/channel_swap/oversample/predict）
- **三层日志架构**: C++log.hpp(RAII Logger+编译期门控+6级日志+组件标签)、FFI桥接(SetLogLevel/GetLogLevel)、Python配置层(统一级别控制)，所有20个Layer和核心文件日志覆盖
- **错误处理**: TVM_FFI_ICHECK参数校验，错误信息含Blob ID/层名/文件名等上下文
- **BLAS集成**: 条件编译CAFFE_USE_BLAS，有BLAS用cblas_sgemm/gemv，无BLAS用纯C++ fallback；im2col/col2im已实现
- **CMake构建**: 支持find_package(tvm_ffi CONFIG REQUIRED)，本地开发保留add_subdirectory fallback，tvm_ffi_configure_target()
- **测试**: MSVC环境Python pytest 101个测试通过（1 skipped），Docker Linux Python 3.14.6环境test_python_api.py 65个测试通过；C++ header-only轻量测试框架40/40通过（MSVC和Docker Linux均验证），含高精度耗时统计和Top 5 slowest报告
- **性能基准**: examples/benchmark_performance.py + examples/zero_copy_vs_copy_demo.py（含is_native_mode API修复），零拷贝恒定~4µs访问，实测10M元素加速3749×，OPTIMIZATION_REPORT.md完整中文版本
- **M6独立项目迁移**: 从vendor/caffe/caffe-ffi萃取为独立第一方项目libs/caffe-ffi，标准结构对齐npu-ffi，CMake构建系统独立化（find_package默认）
- **Docker开发环境**: apps/caffe-ffi-jupyter基于jupyter-ssh-base，双阶段builder+runtime构建，SSH+Jupyter双服务，Python 3.14+ Miniconda环境，RPATH+ldconfig+LD_LIBRARY_PATH三重共享库路径保障
- **工程化工具链**: 统一结构化日志库（Bash+PowerShell双版本）、WSL一键部署脚本wsl-deploy.sh/deploy.ps1、环境诊断脚本diagnose.sh/diagnose.ps1、WSL-DEPLOY-GUIDE.md部署指南
- **CAFFE_FFI_DISABLE_BACKTRACE**: 环境变量支持，Python环境下禁用backtrace防止unittest segfault
- **文档**: Doxygen注释覆盖核心公共API，README.md+OPTIMIZATION_REPORT.md（中文）+TEAM_SHARING_SUMMARY.md+FFI_ZEROCOPY_REFACTOR_CHECKLIST.md
- **跨模块迁移**: caffe_slim_zerocopy_refactor_draft.md（caffe-slim零拷贝改造完整代码草案，含三层日志头文件、写入零拷贝、8类日志标签、全局内存计数器）
- **模式萃取**: FFI_ZEROCOPY_PATTERN_EXTRACTION.md（4个可复用模式：DLPack零拷贝桥接/写入安全门/三层日志可观测性/双类对象模型，含P0-P2迁移检查清单和反模式警示）
- **原子提交归档**: 3个Conventional Commits原子提交（核心代码→文档→示例），共46文件 +4128/-915行

## Functional Requirements

### 已实现 ✅
- **FR-1**: 核心 Blob 张量类，双类模式BlobObj+Blob，使用 Tensor(DLPack) 存储 data/diff 双缓冲
- **FR-2**: Layer 基类，双类模式LayerObj+Layer，通过 LayerRegistry+REGISTER_LAYER_CLASS 宏注册工厂
- **FR-3**: Net 计算图类，双类模式NetObj+Net，管理 Layer DAG 拓扑、Blob 创建、前向执行
- **FR-4**: 使用 tvm::ffi::Shape 替代 std::vector 表示形状，Blob.Reshape接受Shape参数
- **FR-5**: Net 内部使用 tvm::ffi::Map 管理 Blob 名称索引
- **FR-6**: 通过 tvm::ffi 反射系统 + @register_object 自动导出 Python 绑定，消除monkey patch
- **FR-7**: 使用 tvm::ffi::make_object 统一对象创建，自定义 CPUMemAlloc 分配器
- **FR-8**: Protobuf >= 7.0.0 用于解析 .prototxt 和 .caffemodel
- **FR-9**: 全部20个核心推理Layer实现：
  - 第一批(5): Input/ReLU/InnerProduct/Softmax/Flatten
  - 第二批(7): Convolution/Pooling/BatchNorm/Scale/Bias/Accuracy/SoftmaxWithLoss
  - 第三批(8): Sigmoid/TanH/PReLU/ELU/Dropout/Concat/Eltwise/Reshape
- **FR-10**: Python 包 caffe_ffi 提供高层 API：Net 加载、Blob numpy零拷贝访问、前向推理、Classifier
- **FR-11**: CMake 构建系统支持find_package(tvm_ffi)（本地开发保留add_subdirectory fallback）
- **FR-12**: scikit-build-core 配置构建 Python wheel
- **FR-13**: BLAS条件编译集成，im2col/col2im实现
- **FR-14**: Python 单元测试（pytest）已覆盖 Blob/Layer/Net（MSVC: 101 passed, 1 skipped；Docker Linux Python 3.14.6: test_python_api.py 65 passed）
- **FR-15**: 三层日志架构全面应用（C++核心+FFI桥接+Python配置）
- **FR-16**: Doxygen注释覆盖核心公共API
- **FR-17**: 错误处理增强（TVM_FFI_ICHECK+上下文信息）
- **FR-18**: C++ 单元测试框架（header-only轻量框架，0依赖）：40个测试用例（Blob 22个+Net 18个），不依赖gtest，40/40通过（MSVC和Docker Linux均验证）；测试框架增强：高精度耗时统计、Per-suite耗时汇总、Top 5 slowest报告
- **FR-19**: Windows DLL边界问题根治：LayerRegistry单例移至.cpp实现，Protobuf解析在DLL内隔离
- **FR-20**: Python MRO反射查找修复：派生类可正确访问基类注册的方法
- **FR-21**: Docker开发环境（apps/caffe-ffi-jupyter）：基于jupyter-ssh-base，双阶段builder+runtime构建，保留SSH+Jupyter双服务，Python 3.14+ Miniconda环境，RPATH+ldconfig+LD_LIBRARY_PATH三重共享库路径保障
- **FR-22**: 工程化工具链：统一结构化日志库（Bash+PowerShell双版本）、WSL一键部署脚本、环境诊断脚本、部署指南文档
- **FR-23**: CAFFE_FFI_DISABLE_BACKTRACE环境变量支持：Python环境下禁用backtrace防止unittest segfault

### 待后续补充 ⬜
- ASan内存管理验证
- InnerProduct/Conv使用BLAS gemm的性能基准验证（当前fallback可用，BLAS路径待编译验证）
- 端到端真实模型推理测试（如LeNet/MNIST精度验证）

## Non-Functional Requirements

- ✅ **NFR-1**: 性能：零拷贝Tensor访问恒定~3-6µs，MLP Forward~0.5ms（BLAS集成后卷积/全连接性能待进一步基准测试）
- ✅ **NFR-2**: 构建：MSVC Release编译成功，零错误零新增警告
- ✅ **NFR-3**: 兼容性：Windows (MSVC) 已验证；Linux (x86_64, Docker Python 3.14.6 conda环境) 已验证；aarch64待验证
- ✅ **NFR-4**: 代码质量：C++17 标准，无编译新增警告
- ✅ **NFR-5**: 依赖最小化：核心依赖 tvm-ffi(apache-tvm-ffi)、Protobuf >= 7.0.0、numpy
- ✅ **NFR-6**: Python 版本：严格 >= 3.14（MSVC py314 conda环境和Docker Linux Python 3.14.6 conda环境均验证通过）
- ✅ **NFR-7**: 模块化：Layer实现可独立添加/移除（layers/目录 + REGISTER_LAYER_CLASS宏）
- ✅ **NFR-8**: 文档：README.md + OPTIMIZATION_REPORT.md + Doxygen注释
- ✅ **NFR-9**: DLL部署：Windows下自动复制tvm_ffi/protobuf/absl/utf8_range DLL到包目录

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
  - Windows开发环境需设置`KMP_DUPLICATE_LIB_OK=TRUE`（OpenMP多副本共存）
- **Business**:
  - 代码位于 xuanspace libs 目录下的 caffe-ffi（独立第一方项目，从vendor/caffe/caffe-ffi萃取迁移）
  - 参考 caffe-slim 的 Layer 实现逻辑
  - 为后续 GPU 扩展保留接口（Forward_gpu 虚函数）
  - Docker开发环境位于 apps/caffe-ffi-jupyter，基于jupyter-ssh-base
  - WSL为推荐开发和构建环境（Windows下直接编译不推荐）
- **Dependencies**:
  - apache-tvm-ffi（已安装包，find_package）
  - Protobuf >= 7.0.0 + absl + utf8_range
  - BLAS (OpenBLAS/MKL/cblas) — 可选
  - CMake + Ninja
  - scikit-build-core（Python 构建）
  - numpy >= 2.3（Python 端）
  - pytest（运行时依赖）

## Assumptions (验证结果)
- ✅ tvm-ffi 可通过apache-tvm-ffi pip包安装，`python -m tvm_ffi.config --cmakedir`可用
- ✅ Conda 环境可安装 Python 3.14 和 protobuf 7.0.0（py314环境验证）
- ✅ caffe-slim 的 Layer 计算逻辑可复用并适配tvm-ffi对象系统
- ✅ caffe.proto 保持与原始 Caffe 兼容以支持现有模型文件
- ✅ 预生成的 caffe_pb2.py 提交仓库，开箱即用
- ✅ Python-only fallback模式正常工作（@_reg在无tvm_ffi时退化为空装饰器）

## Acceptance Criteria

### ✅ 已达成
- **AC-1**: 项目骨架与构建系统 — CMakeLists.txt 存在，可配置编译，scikit-build-core 可构建 wheel
- **AC-2**: Blob 张量类基于TVM FFI双类模式 — BlobObj+Blob，Tensor存储，Reshape/data_tensor/零拷贝numpy互操作正常
- **AC-3**: Layer 注册通过 LayerRegistry — REGISTER_LAYER_CLASS 宏正常注册，CreateLayer 可动态创建20种Layer实例
- **AC-4**: Net 基础前向推理 + caffemodel加载 — 从prototxt字符串/文件加载网络，CopyTrainedLayersFrom加载权重，Forward执行
- **AC-5**: Python @register_object绑定 — import caffe_ffi 正常，Blob/Layer/Net 通过@_reg装饰器定义，无monkey patch，numpy零拷贝互操作
- **AC-6**: Python 3.14 + protobuf 7.0.0 兼容性 — MSVC py314 conda环境和Docker Linux Python 3.14.6 conda环境均验证通过，导入和protobuf解析正常
- **AC-7**: 全部20个Layer正确性 — 单测通过，MLP集成测试通过，C++端到端数值验证一致
- **AC-8**: TVM FFI最佳实践优化完成 — 双类模式、零拷贝Tensor、@register_object、三层日志、Doxygen注释、错误处理增强
- **AC-9**: 文档完整性 — README.md + OPTIMIZATION_REPORT.md + Doxygen注释 + CHANGELOG.md + WSL-DEPLOY-GUIDE.md
- **AC-10**: 测试通过 — MSVC环境pytest 101 passed, 1 skipped；Docker Linux Python 3.14.6环境test_python_api.py 65 passed；C++/Python测试均包含Per-suite耗时统计和Top 5 slowest报告
- **AC-11**: C++ ctest单元测试通过 — header-only轻量框架，40/40 tests passed（Blob 22个+Net 18个），MSVC和Docker Linux均验证
- **AC-12**: CMake支持find_package(tvm_ffi CONFIG REQUIRED)
- **AC-17**: 独立项目萃取迁移完成 — 从vendor/caffe/caffe-ffi迁移到libs/caffe-ffi，标准结构对齐npu-ffi
- **AC-18**: Docker开发环境完成 — apps/caffe-ffi-jupyter基于jupyter-ssh-base，SSH+Jupyter双服务保留
- **AC-19**: Docker Linux Python 3.14.6验证通过 — C++40/40测试+Python65/65测试全部通过，含耗时统计输出

### 待后续达成 ⬜
- **AC-13**: BLAS集成后Convolution/InnerProduct性能基准（当前纯C++ fallback可用）
- **AC-14**: 内存管理ASan验证
- **AC-15**: Conda环境一键构建验证
- **AC-16**: 端到端真实模型推理（如LeNet/MNIST>95%精度）

## Open Questions (Resolved & Remaining)

### 已解决
- [x] tvm-ffi container/Tensor 是否可直接用于 Blob 数据存储？→ 是的，使用 Tensor::FromNDAlloc + 自定义 CPUMemAlloc，通过 DLPack 实现零拷贝 numpy 访问
- [x] protobuf 7.0.0 的 C++ API 是否可用？→ 可用，需要同时链接 absl 和 utf8_range
- [x] 是否需要提供 caffe.proto 的自定义版本？→ 复用 caffe-slim 精简版 caffe.proto
- [x] Python 包名是否确定为 caffe_ffi？→ 是
- [x] 模型序列化（.caffemodel）格式？→ 使用标准 protobuf 二进制格式，CopyTrainedLayersFrom加载
- [x] Python绑定使用@c_class还是@register_object？→ 使用@register_object（@_reg装饰器），这是TVM FFI标准模式
- [x] 是否保留纯Python fallback？→ 是，保留Python-only模式，自动检测C++扩展可用性
- [x] 双类模式重构是否兼容现有继承体系？→ Layer使用TVM_FFI_DECLARE_OBJECT_INFO（非final），_type_child_slots=20支持所有子类
- [x] CMake是否必须完全移除add_subdirectory？→ 本地开发保留fallback（当tvm-ffi源码目录存在时），优先find_package

### 待解决
- [ ] Conda配方是使用conda-build还是仅提供environment.yml？→ 当前仅有environment.yml，待完善
- [ ] InnerProduct/Convolution的BLAS后端在MSVC环境下的性能验证（需完整BLAS环境）
- [ ] 是否需要提供从caffemodel到numpy权重字典的导出工具？
