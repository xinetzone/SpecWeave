---
id: "caffe-ffi-tvm-integration"
title: "Caffe-FFI: TVM FFI 原生 Caffe 实现"
status: "in_progress"
progress: "5/14 tasks completed (core skeleton + 5 layers working)"
---

# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Product Requirement Document

## Overview
- **Summary**: 在 `projects/xuanspace/vendor/caffe/caffe-ffi` 目录下创建一个以 TVM FFI 为核心基础设施的 Caffe 深度学习框架 CPU 推理版本。该实现深度整合 TVM FFI 的对象系统、容器库、反射注册和内存管理机制，替代传统 Caffe 的 STL 容器和 Boost.Python/pybind11 绑定，提供现代化、跨语言、高性能的推理框架。
- **Purpose**: 解决传统 Caffe 依赖重（Boost/GFlags/GLog等）、Python 绑定脆弱、数据结构不现代的问题，利用 TVM FFI 的通用跨语言 FFI 基础设施，构建一个轻量、高效、易于扩展和维护的 Caffe 推理版本。
- **Target Users**: 深度学习推理工程师、需要在 Python 3.14+ 环境部署 Caffe 模型的开发者、对框架底层实现感兴趣的研究者。
- **Current Status**: 项目骨架已搭建完成，核心类型系统（Blob/Layer/Net）已实现，5个基础Layer（Input/ReLU/InnerProduct/Softmax/Flatten）已可用，Python numpy/DLPack 互操作层已完成，端到端 MLP 推理可运行。

## Goals
- ✅ 基于 TVM FFI 对象系统（Object/ObjectPtr/ObjectRef）重构 Caffe 核心抽象
- ✅ 使用 TVM FFI 容器（Array/Shape/Tensor/String）替代 STL 容器实现参数和 Blob 数据存储
- ✅ 利用 TVM FFI 反射系统（refl::ObjectDef/GlobalDef）实现 Python 自动绑定
- ✅ 通过 TVM FFI Tensor (DLPack) 实现 Blob 数据存储，支持零拷贝 numpy 互操作
- ✅ 采用 CMake + Ninja + scikit-build-core 构建系统，支持 Conda 环境
- ✅ 要求 Python 3.14+、protobuf >= 7.0.0，CPU-only 推理优先
- ✅ 提供完整的构建文档和使用说明（README.md）
- 🔄 支持核心推理 Layer 实现（第一批5个已完成，卷积/池化/归一化等待实现）
- 🔄 BLAS 集成优化计算密集型算子（当前使用纯 C++ 循环实现）
- ⬜ C++ 单元测试框架（ctest 集成）
- ⬜ 内存管理验证（ASan/valgrind）

## Non-Goals (Out of Scope)
- CUDA/GPU 支持（第一阶段仅 CPU，GPU 可作为未来扩展）
- 完整的训练功能（Solver 训练流程仅保留接口，推理优先）
- 与原始 BVLC Caffe 的完全 API 兼容（API 已现代化调整）
- 支持所有 Caffe Layer（第一阶段仅实现核心推理常用层）
- LMDB/LevelDB/HDF5 等数据格式支持（可作为后续扩展）
- 多 GPU 分布式训练/推理
- add_subdirectory 方式引入 tvm-ffi（应使用 `find_package(tvm_ffi CONFIG REQUIRED)` 依赖已安装的 apache-tvm-ffi 包，避免 DLL 冲突）

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
| Object/ObjectPtr | 引用计数对象系统 + RTTI | Blob/Layer/Net 基类 |
| Shape/ShapeView | 引用计数形状容器 | Blob 维度表示 |
| Tensor (DLPack) | DLPack 兼容张量 | Blob data_/diff_ 数据存储 |
| Array | 引用计数动态数组 | blobs_array/layers_array 等 FFI 桥接 |
| String | SSO 小字符串优化 | FFI 字符串桥接 |
| make_object | 统一对象分配 | Blob/Layer/Net 创建 |
| reflection::ObjectDef | 反射注册自动绑定 | extension.cc 中 Blob/Layer/Net 注册 |
| reflection::GlobalDef | 全局函数注册 | net_from_param/net_from_param_file/layer_list |
| TVM_FFI_DECLARE_OBJECT_INFO | 类型信息声明 | Blob(_FINAL)/Layer/Net 类型声明 |
| TVM_FFI_STATIC_INIT_BLOCK | 静态初始化注册 | Layer 注册器、反射注册 |
| TVM_FFI_CHECK/THROW | 错误处理 | Layer 参数校验、网络初始化检查 |

### 已完成的核心实现
- **Blob**: 使用 tvm::ffi::Tensor 存储 data/diff，CPUMemAlloc 自定义分配器（malloc/free），支持 Reshape/FromProto/ToProto，通过 DLPack 实现 numpy 零拷贝
- **Layer**: 继承 tvm::ffi::Object，NVI 生命周期（SetUp→LayerSetUp→Reshape→Forward_cpu），LayerRegistry 工厂模式，REGISTER_LAYER_CLASS 宏通过 TVM_FFI_STATIC_INIT_BLOCK 注册，使用 caffe::LayerParameter protobuf 配置
- **Net**: 继承 tvm::ffi::Object，从 prototxt 文件或 NetParameter 二进制初始化，DAG 拓扑构建（AppendTop/AppendBottom），顺序 Forward 执行，提供 blobs/layers 的 tvm::ffi::Array 桥接
- **Python 层**: monkey-patch 方式为 FFI 对象添加 numpy 便捷方法（data/diff/from_numpy/to_numpy/shape/ndim/size/fill/zero/copy_from），Net 添加 forward(input_dict)/forward_all/blobs_dict/layers_dict/__getitem__/__contains__
- **IO**: read_net/read_net_prototxt/read_net_prototxt_binary/read_net_from_prototxt/read_net_from_binary，支持 prototxt 文本和 caffemodel 二进制解析
- **Classifier**: 高层分类器接口，支持 mean/input_scale/raw_scale/channel_swap 预处理，oversample 预测
- **已实现 Layers**: InputLayer, ReLULayer（含 negative_slope）, InnerProductLayer（含 bias/transpose/axis）, SoftmaxLayer, FlattenLayer
- **测试**: Python pytest 测试框架（test_blob.py/test_layers.py/test_net.py），C++ test_dlopen 测试
- **构建**: CMake 配置 protobuf 代码生成（C++ + Python）、DLL 复制（Windows）、scikit-build-core wheel 打包
- **示例**: create_and_run_mlp.py 端到端 MLP 示例（手动权重设置 + 手动计算验证）

## Functional Requirements

### 已实现 ✅
- **FR-1**: 核心 Blob 张量类，继承 tvm::ffi::Object，使用 Tensor(DLPack) 存储 data/diff 双缓冲
- **FR-2**: Layer 基类，继承 tvm::ffi::Object，通过 LayerRegistry+REGISTER_LAYER_CLASS 宏注册工厂
- **FR-3**: Net 计算图类，管理 Layer DAG 拓扑、Blob 创建、前向执行
- **FR-4**: 使用 tvm::ffi::Shape 替代 std::vector 表示形状
- **FR-6**: 通过 tvm::ffi::reflection 系统自动导出 Python 绑定，Python 层通过 monkey-patch 增强 numpy 互操作
- **FR-7**: 使用 tvm::ffi::make_object 统一对象创建，自定义 CPUMemAlloc 分配器
- **FR-8**: Protobuf >= 7.0.0 用于解析 .prototxt 和 .caffemodel
- **FR-9a**: 第一批核心 Layer（Input/ReLU/InnerProduct/Softmax/Flatten）已实现并测试通过
- **FR-10**: Python 包 caffe_ffi 提供高层 API：Net 加载、Blob numpy 访问、前向推理、Classifier
- **FR-11**: CMake 构建系统集成 tvm-ffi（当前 add_subdirectory，需改为 find_package）
- **FR-12**: scikit-build-core 配置构建 Python wheel
- **FR-14b**: Python 单元测试（pytest）已覆盖 Blob/Layer/Net

### 待实现 ⬜
- **FR-5**: Net 内部使用 tvm::ffi::Map 管理 Blob 索引（当前使用 std::map）
- **FR-9b**: 第二批核心 Layer（计算密集型）：
  - ConvolutionLayer（im2col + BLAS gemm）
  - PoolingLayer（Max/Average）
  - BatchNormLayer + ScaleLayer + BiasLayer
- **FR-9c**: 第三批常用 Layer：
  - SigmoidLayer, TanHLayer, PReLULayer, ELULayer
  - DropoutLayer（推理模式恒等映射）
  - ConcatLayer, EltwiseLayer, ReshapeLayer
  - SoftmaxWithLossLayer, AccuracyLayer（推理兼容）
- **FR-13**: Conda 环境支持（environment.yml 已存在，需验证完整性）
- **FR-14a**: C++ 单元测试（ctest 集成，目前仅有 test_dlopen）
- **FR-15**: 完善文档（更多 Layer 的使用说明、模型迁移指南）
- **BLAS 集成**: OpenBLAS/MKL/cblas 用于 Convolution 和 InnerProduct 的矩阵乘法加速（当前纯 C++ 循环）
- **im2col 实现**: 卷积 im2col 变换
- **tvm-ffi 依赖方式**: 从 add_subdirectory 切换为 find_package(tvm_ffi CONFIG REQUIRED)，依赖已安装的 apache-tvm-ffi 包
- **caffemodel 权重加载**: 验证从二进制 caffemodel 加载预训练权重的完整流程

## Non-Functional Requirements

- **NFR-1**: 性能：BLAS 集成后卷积/全连接性能不低于 caffe-slim 的 CPU 版本
- **NFR-2**: 构建：CMake 配置时间 < 30秒，增量编译速度与 caffe-slim 相当
- **NFR-3**: 兼容性：支持 Linux (x86_64/aarch64) 和 Windows (MSVC)；当前 Windows 需手动配置 DLL 路径
- **NFR-4**: 代码质量：C++17 标准，无编译警告（-Wall -Wextra 或 MSVC /W3）
- **NFR-5**: 依赖最小化：核心依赖 tvm-ffi(apache-tvm-ffi)、Protobuf >= 7.0.0、BLAS（待集成）、Threads、absl、utf8_range
- **NFR-6**: Python 版本：严格 >= 3.14
- **NFR-7**: 模块化：核心组件解耦，Layer 实现可独立添加/移除（通过 layers/ 目录 + REGISTER_LAYER_CLASS 宏）
- **NFR-8**: 文档：构建文档、API 文档、使用示例完整（README.md 已完成基础文档）
- **NFR-9**: DLL 部署：Windows 下自动复制 tvm_ffi/protobuf/absl/utf8_range DLL 到包目录

## Constraints

- **Technical**:
  - C++17 标准（与 tvm-ffi 一致）
  - CMake >= 3.26
  - Python >= 3.14
  - protobuf >= 7.0.0（需 absl + utf8_range 依赖）
  - Ninja 构建生成器
  - scikit-build-core >= 0.10 用于 Python 包构建
  - TVM FFI 作为已安装包依赖（find_package），而非 add_subdirectory
  - CPU-only（第一阶段不涉及 CUDA）
  - BLAS 库需要（OpenBLAS 或 MKL）用于卷积和全连接加速
  - Windows 开发环境需设置 `KMP_DUPLICATE_LIB_OK=TRUE`（OpenMP 多副本共存）
  - Python 侧可编辑安装需显式 add_dll_directory 处理 DLL 加载
- **Business**:
  - 代码位于 xuanspace vendor 目录下的 caffe/caffe-ffi
  - 参考 caffe-slim 的 Layer 实现逻辑
  - 为后续 GPU 扩展保留接口（Forward_gpu 虚函数）
- **Dependencies**:
  - apache-tvm-ffi（已安装包，find_package）
  - Protobuf >= 7.0.0 + absl + utf8_range
  - BLAS (OpenBLAS/MKL/cblas)
  - CMake + Ninja
  - scikit-build-core（Python 构建）
  - numpy >= 2.3（Python 端）
  - pytest（运行时依赖，tvm.testing 传递依赖）

## Assumptions

- tvm-ffi 已作为 apache-tvm-ffi 包安装到 Conda 环境中
- Conda 环境可安装 Python 3.14 和 protobuf 7.0.0
- caffe-slim 的 Layer 计算逻辑可复用，但接口需要适配 tvm-ffi 对象系统
- BLAS 库在 Conda 环境中通过 libopenblas 或 mkl 提供
- caffe.proto 保持与原始 Caffe 兼容以支持现有模型文件
- 预生成的 caffe_pb2.py 提交仓库，开箱即用，不依赖用户安装 protoc

## Acceptance Criteria

### ✅ 已达成
- **AC-1**: 项目骨架与构建系统 — CMakeLists.txt 存在，可配置编译，scikit-build-core 可构建 wheel，pip install -e . 可用
- **AC-2**: Blob 张量类基于 tvm::ffi::Object — Blob 继承 Object，使用 Tensor 存储，Reshape/cpu_data/cpu_diff/data_tensor 正常工作
- **AC-3**: Layer 注册通过 LayerRegistry — REGISTER_LAYER_CLASS 宏正常注册，CreateLayer 可动态创建实例
- **AC-4a**: Net 基础前向推理 — 从 prototxt 字符串加载网络并执行 Forward，MLP  pipeline 测试通过
- **AC-5**: Python 绑定自动导出 — import caffe_ffi 正常，Blob/Net/Layer 在 Python 端可访问，numpy 互操作正常
- **AC-6**: Python 3.14 + protobuf 7.0.0 兼容性 — 导入和 protobuf 解析正常工作
- **AC-7a**: 第一批 Layer 正确性 — Input/ReLU/InnerProduct/Softmax/Flatten 单测通过，MLP 集成测试通过
- **AC-9**: 文档完整性 — README.md 包含构建步骤、使用示例、API 说明

### 待达成 ⬜
- **AC-4b**: Net 从 .caffemodel 二进制文件加载预训练权重并推理
- **AC-7b**: Convolution/Pooling/BatchNorm 等计算密集 Layer 正确性，BLAS 加速验证
- **AC-7c**: 第三批常用 Layer（Sigmoid/TanH/Concat/Eltwise/Dropout/Reshape 等）正确性
- **AC-8**: Conda 环境从 environment.yml 创建并完整构建通过
- **AC-10**: 内存管理正确性（ASan 无泄漏，引用计数正确）
- **AC-11**: C++ ctest 单元测试通过
- **AC-12**: tvm-ffi 使用 find_package 而非 add_subdirectory
- **AC-13**: BLAS 集成后 Convolution/InnerProduct 性能与 caffe-slim 相当

## Open Questions (Resolved & Remaining)

### 已解决
- [x] tvm-ffi container/Tensor 是否可直接用于 Blob 数据存储？→ 是的，使用 Tensor::FromNDAlloc + 自定义 CPUMemAlloc，通过 DLPack 实现零拷贝 numpy 访问
- [x] protobuf 7.0.0 的 C++ API 是否可用？→ 可用，需要同时链接 absl 和 utf8_range
- [x] 是否需要提供 caffe.proto 的自定义版本？→ 复用 caffe-slim 精简版 caffe.proto（保留核心推理消息）
- [x] Python 包名是否确定为 caffe_ffi？→ 是
- [x] 模型序列化（.caffemodel）格式？→ 使用标准 protobuf 二进制格式，通过 ParseFromString 加载

### 待解决
- [ ] Conda 配方是使用 conda-build 还是仅提供 environment.yml？→ 当前仅有 environment.yml
- [ ] InnerProduct/Convolution 的 BLAS 后端选择 OpenBLAS 还是 MKL？是否支持 cblas 作为备选？
- [ ] PoolingLayer 是否需要支持全局池化和 ROI Pooling？（第一阶段仅 Max/Average 即可）
- [ ] 是否需要提供从 caffemodel 到 numpy 权重字典的导出工具？
