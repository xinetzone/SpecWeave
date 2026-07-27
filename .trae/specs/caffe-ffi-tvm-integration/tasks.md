# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Implementation Plan

## [ ] Task 1: 项目目录骨架与构建系统初始化
- **Priority**: high
- **Depends On**: None
- **Description**:
  - 创建 caffe-ffi 目录结构：include/caffe_ffi/, src/, python/caffe_ffi/, proto/, tests/
  - 编写顶层 CMakeLists.txt，配置 C++17、tvm-ffi 子目录引用、Protobuf 查找、BLAS 查找
  - 编写 pyproject.toml（scikit-build-core 配置，Python >= 3.14，protobuf >= 7.0.0 依赖）
  - 参考 caffe-slim 的 CMakeLists.txt 和 pycaffe/pyproject.toml
  - 设置 TVM_FFI_USE_LIBBACKTRACE=OFF 等必要选项
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: `cmake -B build -G Ninja` 成功配置，无错误
  - `programmatic` TR-1.2: `cmake --build build` 能编译空项目骨架
  - `programmatic` TR-1.3: `pip install -e .`（在 pyproject.toml 配置正确后）能启动 scikit-build-core 构建
- **Notes**: tvm-ffi 通过 add_subdirectory("../../tvm-ffi" tvm-ffi EXCLUDE_FROM_ALL) 引入，参考 caffe-slim 第24-28行

## [ ] Task 2: Proto 定义与代码生成集成
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 复制/适配 caffe-slim 的 caffe.proto 到 proto/caffe.proto（保留核心推理相关消息）
  - 在 CMakeLists.txt 中添加 protoc 自定义命令，生成 .pb.cc/.pb.h
  - 确保生成的代码与 protobuf 7.0.0 兼容（检查 API 变化）
  - 配置生成目录为 build/caffe_proto_gen/
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Test Requirements**:
  - `programmatic` TR-2.1: CMake 配置时自动检测 protoc
  - `programmatic` TR-2.2: 构建时生成 caffe.pb.h/caffe.pb.cc 到正确目录
  - `programmatic` TR-2.3: 生成的 proto 代码可被 C++ 代码正常 include 和链接

## [ ] Task 3: 核心类型定义与 TVM FFI 对象系统集成
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - 创建 include/caffe_ffi/common.hpp：前向声明、typedef、使用 tvm::ffi 命名空间的类型别名
  - 创建 include/caffe_ffi/shape.hpp：基于 tvm::ffi::Array<int64_t> 的 Shape 类型（替代 std::vector<int>）
  - 创建 include/caffe_ffi/blob.hpp：Blob 类继承 tvm::ffi::Object，使用 TVM_FFI_DECLARE_OBJECT_INFO_FINAL 宏
  - 定义 Blob 内部存储：使用 tvm::ffi::Tensor 或自定义的共享内存块（需调研决定）
  - 实现 Blob 核心方法：Reshape(), cpu_data(), cpu_diff(), shape(), count()
  - 使用 tvm::ffi::make_object 创建 Blob 实例
  - 创建 include/caffe_ffi/syncedmem.hpp（简化版，CPU-only，使用 tvm::ffi 内存分配）
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Test Requirements**:
  - `programmatic` TR-3.1: Blob 可通过 make_object<Blob>() 创建
  - `programmatic` TR-3.2: Blob->Reshape(N,C,H,W) 正确设置形状和分配内存
  - `programmatic` TR-3.3: Blob->cpu_data() 返回有效指针，数据可读写
  - `programmatic` TR-3.4: ObjectPtr<Blob> 引用计数正确，无内存泄漏
  - `programmatic` TR-3.5: Shape 使用 tvm::ffi::Array 存储维度，可转换为 vector

## [ ] Task 4: Layer 基类与 PackedFunc 注册工厂
- **Priority**: high
- **Depends On**: Task 3
- **Description**:
  - 创建 include/caffe_ffi/layer.hpp：Layer 基类继承 tvm::ffi::Object
  - 定义 Layer 核心接口：SetUp(), Forward(), Forward_gpu()（空实现/存根）, type(), layer_param()
  - 使用 tvm::ffi::Map<String, tvm::ffi::Any> 存储 LayerParameter（或使用 proto 对象）
  - 创建 include/caffe_ffi/layer_factory.hpp：基于 tvm::ffi::Function/PackedFunc 的全局注册表
  - 定义 REGISTER_LAYER_CLASS 宏，通过 tvm::ffi::Registry 注册工厂函数
  - 创建 src/layer.cpp 和 src/layer_factory.cpp 实现
  - 创建简单测试 Layer（如 InputLayer、ReLULayer 骨架）验证注册机制
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-4.1: Layer 子类可通过 REGISTER_LAYER_CLASS 宏注册
  - `programmatic` TR-4.2: LayerRegistry::CreateLayer("ReLU") 可通过工厂创建 Layer 实例
  - `programmatic` TR-4.3: Layer 实例通过 ObjectPtr<Layer> 管理生命周期
  - `programmatic` TR-4.4: SetUp() 方法可接收 Blob 向量并进行形状推断

## [ ] Task 5: Net 计算图实现
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 创建 include/caffe_ffi/net.hpp：Net 类继承 tvm::ffi::Object
  - 实现 Net 核心功能：
    - 从 NetParameter (protobuf) 或 tvm::ffi::Map 解析网络结构
    - 构建 Layer DAG，拓扑排序
    - 管理中间 Blob 的内存分配（使用 tvm::ffi 容器）
    - Forward() 按拓扑序执行所有 Layer 的 Forward
    - blob_by_name()/layer_by_name() 访问接口
  - 使用 tvm::ffi::Array<ObjectPtr<Layer>> 存储 layers_
  - 使用 tvm::ffi::Map<String, ObjectPtr<Blob>> 存储 blobs_
  - 实现 Init() 方法进行网络初始化
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-5.1: Net 可从简单的 NetParameter 初始化
  - `programmatic` TR-5.2: Net 正确构建 DAG 并拓扑排序
  - `programmatic` TR-5.3: Forward() 顺序调用各 Layer 的 Forward
  - `programmatic` TR-5.4: 中间 Blob 内存正确分配和共享

## [ ] Task 6: 核心 Layer 实现（第一批 - 基础算子）
- **Priority**: high
- **Depends On**: Task 4
- **Description**:
  - 实现 InputLayer：直接从外部输入填充 Blob
  - 实现 ReLULayer：激活函数，max(0, x)
  - 实现 SigmoidLayer、TanHLayer：S形激活
  - 实现 DropoutLayer：推理模式下恒等映射
  - 实现 FlattenLayer/ReshapeLayer：形状变换
  - 实现 ConcatLayer：沿通道维度拼接 Blob
  - 实现 EltwiseLayer：逐元素操作（加/乘/最大）
  - 每个 Layer 继承 Layer 基类，使用 REGISTER_LAYER_CLASS 注册
  - 从 caffe-slim/src/caffe/layers/ 迁移计算逻辑，适配新接口
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-6.1: ReLU 对已知输入输出正确结果（如全部正值不变，负值置零）
  - `programmatic` TR-6.2: Concat 正确拼接多个 Blob
  - `programmatic` TR-6.3: Reshape/Flatten 正确变换形状且不改变数据
  - `programmatic` TR-6.4: 每个 Layer 的 SetUp 正确推断输出形状

## [ ] Task 7: 核心 Layer 实现（第二批 - 计算密集算子）
- **Priority**: high
- **Depends On**: Task 6
- **Description**:
  - 实现 ConvolutionLayer：卷积运算，使用 BLAS（im2col + gemm）
  - 实现 PoolingLayer：最大池化和平均池化
  - 实现 InnerProductLayer（全连接层）：矩阵乘法
  - 实现 SoftmaxLayer：softmax 激活
  - 实现 BatchNormLayer + ScaleLayer + BiasLayer：归一化组合
  - 实现 SoftmaxWithLossLayer、AccuracyLayer：推理兼容（仅前向）
  - 迁移 caffe-slim 的 im2col 实现和 BLAS 调用逻辑
  - 使用 tvm::ffi 的容器管理参数 Blob（权重）
- **Acceptance Criteria Addressed**: AC-7
- **Test Requirements**:
  - `programmatic` TR-7.1: Convolution 前向输出与 caffe-slim 参考一致
  - `programmatic` TR-7.2: Pooling 最大/平均计算正确
  - `programmatic` TR-7.3: InnerProduct 矩阵乘法正确
  - `programmatic` TR-7.4: Softmax 输出和为 1，最大值位置正确
  - `programmatic` TR-7.5: BatchNorm + Scale 组合输出正确

## [ ] Task 8: C++ 核心库构建整合
- **Priority**: high
- **Depends On**: Task 5, Task 7
- **Description**:
  - 将所有核心 .cpp 文件整合到 CMakeLists.txt 的 caffe_ffi_core 静态库
  - 配置正确的 include 路径、编译定义（CPU_ONLY）、链接库
  - 处理 MSVC 和 GCC/Clang 的编译选项差异
  - 生成 _caffe_ffi 共享库用于 Python 绑定（使用 whole-archive 链接 core）
  - 确保 tvm_ffi::shared 和 protobuf、BLAS 正确链接
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-8.1: caffe_ffi_core 静态库编译无错误无警告
  - `programmatic` TR-8.2: _caffe_ffi 共享库成功链接，所有符号解析
  - `programmatic` TR-8.3: Linux 和 Windows 均成功构建（或至少 Linux 先通过）

## [ ] Task 9: TVM FFI Python 绑定导出
- **Priority**: high
- **Depends On**: Task 8
- **Description**:
  - 创建 src/caffe_ffi/_caffe_ffi.cpp：tvm-ffi 绑定入口
  - 使用 TVM_FFI_REGISTER_GLOBAL 注册关键函数：Net_Create, Net_Forward, Blob_data, 等
  - 使用 TVM_FFI_REGISTER_OBJECT 宏为 Blob、Layer、Net 注册 RTTI 信息
  - 确保 ObjectPtr 类型可在 Python 端自动转换
  - 创建 python/caffe_ffi/__init__.py：高层 Python API
  - 创建 python/caffe_ffi/_net.py：Net Python 包装类
  - 创建 python/caffe_ffi/_blob.py：Blob Python 包装类
  - 创建 python/caffe_ffi/io.py：.prototxt/.caffemodel 加载工具
  - 利用 tvm-ffi 自动桥接，不使用 pybind11/Boost.Python/Cython
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-9.1: Python 中 `import caffe_ffi` 无错误
  - `programmatic` TR-9.2: 可通过 caffe_ffi.Net 加载网络
  - `programmatic` TR-9.3: net.forward() 返回结果字典
  - `programmatic` TR-9.4: Blob 数据可通过 numpy 数组访问（零拷贝优先）
  - `human-judgement` TR-9.5: Python API 设计符合直觉，使用方式类似原生 Caffe

## [ ] Task 10: Python IO 与 protobuf 集成
- **Priority**: high
- **Depends On**: Task 9
- **Description**:
  - 确保 Python protobuf 7.0.0 可用（检查生成的 caffe_pb2.py 兼容性）
  - 实现 prototxt 解析：读取文本格式 .prototxt 为 NetParameter
  - 实现 caffemodel 加载：读取二进制 .caffemodel 为 NetParameter，填充参数 Blob
  - 在 Python 和 C++ 层之间传递 protobuf 对象（序列化为 bytes 或使用 tvm::ffi::Bytes）
  - 参考 caffe-slim 的 protos/caffe_pb2.py 和 caffeproto/caffe_utils.py
- **Acceptance Criteria Addressed**: AC-4, AC-6
- **Test Requirements**:
  - `programmatic` TR-10.1: Python 中可解析简单的 .prototxt 字符串
  - `programmatic` TR-10.2: caffemodel 二进制文件可加载并填充权重
  - `programmatic` TR-10.3: protobuf 7.0.0 无 DeprecationWarning
  - `programmatic` TR-10.4: 加载后网络可执行 Forward

## [ ] Task 11: 端到端推理验证
- **Priority**: high
- **Depends On**: Task 10
- **Description**:
  - 创建简单测试网络（如 LeNet 的最小版本或单层 Conv+ReLU+FC 网络）
  - 准备测试权重文件（随机初始化即可）
  - 编写 C++ 测试用例 tests/test_net.cpp：验证前向执行
  - 编写 Python 测试 tests/test_inference.py：验证端到端推理
  - 对比 caffe-slim 相同网络的前向输出，确保数值一致性（误差在 1e-5 以内）
  - 添加 tests/test_blob.py、tests/test_layers.py 等单元测试
- **Acceptance Criteria Addressed**: AC-4, AC-7
- **Test Requirements**:
  - `programmatic` TR-11.1: 简单网络（Conv+ReLU+Pool+FC+Softmax）可完成 Forward
  - `programmatic` TR-11.2: C++ 单元测试全部通过
  - `programmatic` TR-11.3: Python 单元测试全部通过
  - `programmatic` TR-11.4: 与 caffe-slim 参考输出数值一致（误差 < 1e-5）

## [ ] Task 12: Conda 环境配置
- **Priority**: medium
- **Depends On**: Task 8
- **Description**:
  - 创建 conda/environment.yml：定义 Python 3.14、cmake、ninja、protobuf、openblas、numpy 等依赖
  - 配置北外 conda-forge 镜像（mirrors.bfsu.edu.cn）
  - 创建 conda/build.sh：Conda 环境下的构建脚本
  - 参考 caffe-slim/docker/local/conda/ 配置
  - 确保 default_channels 清空，仅使用 conda-forge
- **Acceptance Criteria Addressed**: AC-8
- **Test Requirements**:
  - `programmatic` TR-12.1: `conda env create -f conda/environment.yml` 成功创建环境
  - `programmatic` TR-12.2: 在该环境中可成功编译 caffe-ffi
  - `programmatic` TR-12.3: Python 导入和推理测试通过

## [ ] Task 13: 文档与使用说明
- **Priority**: medium
- **Depends On**: Task 11, Task 12
- **Description**:
  - 创建 README.md：项目介绍、依赖、构建步骤、使用示例
  - 创建 BUILD.md：详细构建指南（Conda/Docker/原生）
  - 创建 docs/ 目录（可选）：API 文档说明
  - 提供 examples/mnist/ 或 examples/simple/ 示例
  - 说明与 caffe-slim、原始 Caffe 的差异和迁移指南
  - 参考 caffe-slim 的 BATCH_INFERENCE_GUIDE.md
- **Acceptance Criteria Addressed**: AC-9
- **Test Requirements**:
  - `human-judgement` TR-13.1: README 包含完整的构建和快速开始步骤
  - `human-judgement` TR-13.2: 新开发者可按文档在 30 分钟内完成首次构建
  - `programmatic` TR-13.3: 示例代码可运行并得到预期输出

## [ ] Task 14: 内存管理与稳定性验证
- **Priority**: medium
- **Depends On**: Task 11
- **Description**:
  - 使用 AddressSanitizer（-fsanitize=address）编译运行测试，检查内存泄漏和越界
  - 验证 tvm::ffi 引用计数在 Net 销毁时正确释放所有 Blob 和 Layer
  - 多次创建/销毁 Net 验证无内存累积
  - 检查线程安全性（如必要，添加基本线程安全保证）
  - 边界情况测试：空网络、单 Layer 网络、大 Batch Size
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-14.1: ASan 编译运行测试无内存泄漏报告
  - `programmatic` TR-14.2: 循环创建销毁 Net 100 次后内存稳定
  - `programmatic` TR-14.3: 大 Batch Size（如 256）推理无崩溃
