# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Implementation Plan

> **进度概览**: 核心骨架、类型系统、5个基础 Layer、Python 绑定和 numpy 互操作已完成；BLAS 集成、卷积/池化/归一化 Layer、C++ 单元测试、find_package 迁移待完成。

---

## [x] Task 1: 项目目录骨架与构建系统初始化
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成
- **Description**:
  - 创建 caffe-ffi 目录结构：include/caffe_ffi/, src/caffe_ffi/, python/caffe_ffi/, proto/, tests/, examples/
  - 编写顶层 CMakeLists.txt，配置 C++17、tvm-ffi（add_subdirectory）、Protobuf 7.0+、BLAS 占位、DLL 复制
  - 编写 pyproject.toml（scikit-build-core，Python >= 3.14，protobuf >= 7.0.0，numpy >= 2.3，apache-tvm-ffi）
  - 配置 protobuf 代码生成（C++ + Python），Windows DLL 自动复制
  - 预生成 caffe_pb2.py 提交仓库
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Deliverables**: [CMakeLists.txt](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/CMakeLists.txt), [pyproject.toml](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/pyproject.toml)
- **Notes**: tvm-ffi 当前通过 add_subdirectory("../../tvm-ffi" tvm-ffi EXCLUDE_FROM_ALL) 引入，Task 16 需切换为 find_package

## [x] Task 2: Proto 定义与代码生成集成
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - 复用 caffe-slim 精简版 caffe.proto（保留 BlobProto/LayerParameter/NetParameter/InnerProductParameter/ReLUParameter/SoftmaxParameter/FlattenParameter/InputParameter）
  - CMake protoc 自定义命令生成 .pb.cc/.pb.h 和 caffe_pb2.py
  - 生成目录 build/caffe_proto_gen/，Python 文件复制到 python/caffe_ffi/
  - 预生成 caffe_pb2.py 提交仓库，开箱即用
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Deliverables**: [caffe.proto](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/proto/caffe/proto/caffe.proto), [caffe_pb2.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/python/caffe_ffi/caffe_pb2.py)

## [x] Task 3: 核心类型定义与 TVM FFI 对象系统集成
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - common.hpp：typedef（BlobVec/LayerVec/BlobArray/LayerArray）、using namespace tvm::ffi
  - fill.hpp：caffe_set_fp32/caffe_copy_fp32/caffe_cpu_axpby_fp32 纯 C++ 实现
  - math_utils.hpp：CPU 计算工具函数占位
  - blob.hpp/cpp：Blob 继承 Object，Tensor(DLPack) 存储 data/diff，CPUMemAlloc 分配器，Reshape/cpu_data/cpu_diff/FromProto/ToProto/get_data/set_data
  - shape.hpp：使用 tvm::ffi::Shape/ShapeView（无需自定义包装层）
- **Acceptance Criteria Addressed**: AC-2, AC-10
- **Deliverables**: [blob.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/include/caffe_ffi/blob.hpp), [blob.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/blob.cpp)

## [x] Task 4: Layer 基类与注册工厂
- **Priority**: high
- **Depends On**: Task 3
- **Status**: ✅ 已完成
- **Description**:
  - layer.hpp：Layer 继承 Object，NVI 接口（SetUp→LayerSetUp→Reshape→Forward），TVM_FFI_DECLARE_OBJECT_INFO（_type_child_slots = 8）
  - layer_factory.hpp：LayerRegistry 工厂（std::unordered_map），REGISTER_LAYER_CLASS 宏通过 TVM_FFI_STATIC_INIT_BLOCK 注册
  - Layer 使用 caffe::LayerParameter protobuf 配置（blobs_/param_propagate_down_/loss_）
  - param.hpp/param.cpp：LayerParameter 处理（Blob 从 BlobProto 复制参数）
- **Acceptance Criteria Addressed**: AC-3
- **Deliverables**: [layer.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/include/caffe_ffi/layer.hpp), [layer_factory.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/include/caffe_ffi/layer_factory.hpp)

## [x] Task 5: Net 计算图实现
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成
- **Description**:
  - net.hpp/cpp：Net 继承 Object，从 prototxt 文件或 NetParameter 二进制初始化
  - DAG 拓扑构建：AppendTop/AppendBottom 管理 available_blobs 和 blob_back_pointer
  - 顺序 Forward 执行：reshape→Forward_cpu→loss 计算
  - blobs_array/layers_array/input_blobs_array/output_blobs_array 提供 tvm::ffi::Array FFI 桥接
  - blob_by_name/layer_by_name/has_blob/has_layer 查询接口
  - 全局 FFI 函数：net_from_param, net_from_param_file, layer_list（通过 reflection::GlobalDef 注册）
- **Acceptance Criteria Addressed**: AC-4a
- **Deliverables**: [net.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/include/caffe_ffi/net.hpp), [net.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/net.cpp)
- **Notes**: 内部 blobs_names_index_ 使用 std::map，待迁移为 tvm::ffi::Map（FR-5）

## [x] Task 6: 第一批基础 Layer（Input/ReLU/InnerProduct/Softmax/Flatten）
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成
- **Description**:
  - InputLayer：设置输入 Blob 形状，支持多 top、多 shape
  - ReLULayer：max(0,x) 激活，支持 negative_slope 和 in-place
  - InnerProductLayer：全连接层，bias_term/transpose/axis 参数，纯 C++ 三重循环矩阵乘法
  - SoftmaxLayer：softmax 归一化（全零输入→均匀分布，输出和为 1）
  - FlattenLayer：展平张量（axis/end_axis 参数）
  - 每个 Layer 通过 REGISTER_LAYER_CLASS 注册
- **Acceptance Criteria Addressed**: AC-7a
- **Deliverables**: [input_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/layers/input_layer.cpp), [relu_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/layers/relu_layer.cpp), [inner_product_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/layers/inner_product_layer.cpp), [softmax_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/layers/softmax_layer.cpp), [flatten_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/layers/flatten_layer.cpp)
- **Test Requirements (verified)**:
  - ReLU: 正值不变，负值置零，negative_slope 缩放，in-place ✅
  - InnerProduct: 矩阵乘法+bias 正确，权重从 BlobProto 加载 ✅
  - Softmax: 输出概率和为1，全零→均匀分布 ✅
  - Flatten: 形状展平正确（包括 end_axis=-1）✅
  - MLP 端到端: Input→FC→ReLU→FC→Softmax 推理正确 ✅

## [ ] Task 7: 第二批计算密集 Layer（Convolution/Pooling/BatchNorm）
- **Priority**: high
- **Depends On**: Task 15 (BLAS 集成)
- **Status**: ⬜ 待开始
- **Description**:
  - 实现 math_utils.hpp：基于 BLAS 的 caffe_cpu_gemm/cblas_sgemm、caffe_cpu_gemv、caffe_axpy/caffe_scal
  - 实现 im2col/col2im（参考 caffe-slim）
  - 实现 ConvolutionLayer：im2col + BLAS gemm 卷积（num_output/kernel_size/stride/pad/group/dilation/bias_term）
  - 实现 PoolingLayer：Max 和 Average 池化（kernel_size/stride/pad/global_pooling）
  - 实现 BatchNormLayer：均值/方差归一化（use_global_stats/moving_average_fraction/eps）
  - 实现 ScaleLayer：scale + bias（axis/num_axes/bias_term）
  - 实现 BiasLayer：广播偏置加法
  - 实现 SoftmaxWithLossLayer：推理模式只跑 Softmax 前向
  - 实现 AccuracyLayer：top-k 精度计算
- **Acceptance Criteria Addressed**: AC-7b
- **Test Requirements**:
  - `programmatic` TR-7.1: Convolution 前向输出与 caffe-slim 参考一致（误差 < 1e-5）
  - `programmatic` TR-7.2: Pooling 最大/平均计算正确
  - `programmatic` TR-7.3: InnerProduct 使用 BLAS gemm 替代三重循环，结果一致
  - `programmatic` TR-7.4: Softmax 输出和为 1
  - `programmatic` TR-7.5: BatchNorm + Scale 组合输出正确
  - `programmatic` TR-7.6: Accuracy 计算正确

## [ ] Task 8: 第三批常用 Layer（激活/拼接/形状变换）
- **Priority**: medium
- **Depends On**: Task 6
- **Status**: ⬜ 待开始
- **Description**:
  - SigmoidLayer：1/(1+exp(-x))
  - TanHLayer：(exp(x)-exp(-x))/(exp(x)+exp(-x))
  - PReLULayer：参数化 ReLU（channel_shared/slope_filler）
  - ELULayer：指数线性单元（alpha 参数）
  - DropoutLayer：推理模式恒等映射
  - ConcatLayer：沿指定维度拼接（concat_dim 参数）
  - EltwiseLayer：逐元素操作（PROD/SUM/MAX + coeff）
  - ReshapeLayer：形状变换（dim/axis/num_axes，-1 推断维度）
- **Acceptance Criteria Addressed**: AC-7c
- **Test Requirements**:
  - `programmatic` TR-8.1: Sigmoid/TanH 输出范围正确
  - `programmatic` TR-8.2: Concat 沿 axis=1/0 正确拼接
  - `programmatic` TR-8.3: Eltwise 加/乘/最大操作正确
  - `programmatic` TR-8.4: Reshape 正确变换形状且不改变数据

## [x] Task 9: TVM FFI Python 绑定与 numpy 互操作
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Status**: ✅ 已完成
- **Description**:
  - src/caffe_ffi/extension.cc：FFI 绑定入口，使用 reflection::ObjectDef 注册 Blob/Layer/Net，reflection::GlobalDef 注册 net_from_param/net_from_param_file/layer_list
  - python/caffe_ffi/_ffi_api.py：LIB 加载（load_lib_module）、init_ffi_api、TYPE_CHECKING 存根、register_object 绑定 Blob/Layer/Net
  - python/caffe_ffi/blob.py：monkey-patch numpy 互操作方法（data/diff/from_numpy/to_numpy/shape/ndim/size/fill/zero/copy_from/__repr__）
  - python/caffe_ffi/net.py：monkey-patch 高级 API（forward/forward_all/blobs_dict/layers_dict/__getitem__/__contains__/__repr__/__iter__）
  - python/caffe_ffi/layer.py：Layer monkey-patch（type 属性）
  - python/caffe_ffi/__init__.py：包入口，导入并应用 monkey-patch
  - python/caffe_ffi/io.py：prototxt/caffemodel 加载工具（read_net/read_net_prototxt/read_net_prototxt_binary/read_net_from_prototxt/read_net_from_binary）
  - python/caffe_ffi/classifier.py：Classifier 高层分类器（mean/input_scale/raw_scale/channel_swap/oversample/predict）
  - 利用 DLPack 实现 numpy 零拷贝互操作（to_numpy→from_dlpack, from_numpy→from_numpy→dlpack→Tensor::FromDLPack）
- **Acceptance Criteria Addressed**: AC-5
- **Deliverables**: [extension.cc](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/src/caffe_ffi/extension.cc), [_ffi_api.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/python/caffe_ffi/_ffi_api.py), [blob.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/python/caffe_ffi/blob.py), [net.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/python/caffe_ffi/net.py), [io.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/python/caffe_ffi/io.py)

## [ ] Task 10: caffemodel 权重加载与端到端真实模型验证
- **Priority**: high
- **Depends On**: Task 9
- **Status**: 🔄 部分完成（prototxt 文本加载 ✅，二进制 caffemodel 权重加载待验证）
- **Description**:
  - prototxt 文本解析（TextFormat.Parse → NetParameter）→ 已通过 read_net_from_prototxt 实现
  - caffemodel 二进制加载（SerializeToString → C++ ParseFromArray → CopyTrainedLayersFromBinaryProto）→ IO 函数已存在，需端到端验证
  - 从预训练 caffemodel 加载权重到 Layer blobs_
  - 创建端到端测试：加载真实预训练模型（如 LeNet），输入测试图片，验证推理结果
- **Acceptance Criteria Addressed**: AC-4b
- **Test Requirements**:
  - `programmatic` TR-10.1: read_net_from_binary 加载 .caffemodel 后 Layer blobs_ 数据正确
  - `programmatic` TR-10.2: 加载 LeNet 模型后 MNIST 推理精度 > 95%
  - `programmatic` TR-10.3: numpy 输入→前向→numpy 输出全链路无错误

## [x] Task 11: Python 测试框架与基础测试
- **Priority**: high
- **Depends On**: Task 9
- **Status**: ✅ 已完成（Python pytest 框架和基础测试）
- **Description**:
  - tests/conftest.py：require_cpp_extension marker、mlp_net fixture（手动权重设置）
  - tests/test_blob.py：Blob 单元测试（reshape/from_numpy/to_numpy/data/diff/fill/zero/copy_from/repr）
  - tests/test_layers.py：Layer 单元测试（Input/ReLU/InnerProduct/Softmax/Flatten 各单测）
  - tests/test_net.py：Net 单元测试（prototxt/construct/forward/access/KeyError）
  - tests/test_pure_python.py：无 C++ 扩展的纯 Python 测试
  - examples/create_and_run_mlp.py：端到端 MLP 示例（手动权重+手动计算验证）
  - C++ tests/test_dlopen.cpp：动态库加载测试
- **Acceptance Criteria Addressed**: AC-7a（部分）
- **Deliverables**: [test_blob.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/tests/test_blob.py), [test_layers.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/tests/test_layers.py), [test_net.py](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/tests/test_net.py)
- **Remaining**: C++ ctest 单元测试框架、与 caffe-slim 数值一致性对比、真实模型端到端测试

## [ ] Task 12: C++ 单元测试框架（ctest）
- **Priority**: medium
- **Depends On**: Task 7（计算密集 Layer 完成后）
- **Status**: ⬜ 待开始
- **Description**:
  - 配置 CMake ctest（enable_testing + add_test）
  - 编写 tests/test_blob.cpp：Blob Reshape/cpu_data/引用计数
  - 编写 tests/test_layers.cpp：Layer 前向计算（与 caffe-slim 对比）
  - 编写 tests/test_net.cpp：Net 初始化/前向/DAG 构建
  - 可选：使用 Catch2 或 doctest 轻量测试框架
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `programmatic` TR-12.1: `ctest --test-dir build` 所有测试通过
  - `programmatic` TR-12.2: Blob/Layer/Net C++ 测试覆盖核心路径

## [ ] Task 13: Conda 环境配置完善
- **Priority**: medium
- **Depends On**: Task 8
- **Status**: 🔄 部分完成（文件存在，待完善）
- **Description**:
  - 完善 environment.yml：
    - 配置北外 conda-forge 镜像（mirrors.bfsu.edu.cn）
    - 清空 default_channels
    - 添加 openblas 或 mkl BLAS 依赖
    - 添加 libopenblas/cblas 头文件和库
  - 验证 conda env create + build 在干净环境中通过
  - Windows DLL 路径配置文档
- **Acceptance Criteria Addressed**: AC-8
- **Deliverables**: [environment.yml](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/environment.yml), [conda_build.sh](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/conda_build.sh)
- **Test Requirements**:
  - `programmatic` TR-13.1: `conda env create -f environment.yml` 成功
  - `programmatic` TR-13.2: conda_build.sh 编译通过，pytest 全部通过

## [x] Task 14: 基础文档与使用说明
- **Priority**: medium
- **Depends On**: Task 9
- **Status**: ✅ 已完成（基础版）
- **Description**:
  - README.md：项目介绍、构建步骤（Conda+手动）、快速开始示例、支持层列表、项目结构
  - examples/create_and_run_mlp.py：可运行示例
  - conda_build.sh/conda_build.bat：一键构建脚本
- **Acceptance Criteria Addressed**: AC-9
- **Deliverables**: [README.md](file:///d:/spaces/SpecWeave/projects/xuanspace/vendor/caffe/caffe-ffi/README.md)
- **Remaining**: BLAS 配置文档、Windows DLL 路径配置、模型迁移指南

## [ ] Task 15: BLAS 集成与性能优化
- **Priority**: high
- **Depends On**: None（可与 Task 7 并行，Task 7 依赖此任务）
- **Status**: ⬜ 待开始
- **Description**:
  - CMakeLists.txt 中 find_package(BLAS) 或 find_package(OpenBLAS) 查找 BLAS 库
  - 实现 math_utils.hpp BLAS 后端：caffe_cpu_gemm（cblas_sgemm）、caffe_cpu_gemv（cblas_sgemv）、caffe_axpy/caffe_scal
  - 修改 InnerProductLayer Forward_cpu 使用 caffe_cpu_gemm 替代手动三重循环
  - 实现 im2col/col2im（参考 caffe-slim src/caffe/util/im2col.cpp）
  - 性能基准测试：对比纯循环 vs BLAS，对比 caffe-slim
- **Acceptance Criteria Addressed**: NFR-1, AC-13
- **Test Requirements**:
  - `programmatic` TR-15.1: BLAS 集成后 InnerProduct 输出与纯循环版本一致（误差 < 1e-5）
  - `programmatic` TR-15.2: im2col 输出与 caffe-slim 一致
  - `programmatic` TR-15.3: 大矩阵乘法 BLAS 比纯循环快 > 5x

## [ ] Task 16: tvm-ffi 依赖方式迁移（add_subdirectory → find_package）
- **Priority**: medium
- **Depends On**: None
- **Status**: ⬜ 待开始
- **Description**:
  - 删除 CMakeLists.txt 中 add_subdirectory("../../tvm-ffi" tvm-ffi EXCLUDE_FROM_ALL)
  - 替换为 find_package(tvm_ffi CONFIG REQUIRED)
  - 链接 tvm::ffi_shared（或对应 target 名称）
  - 验证 DLL 复制逻辑正确（tvm_ffi_shared DLL 需复制到包目录）
  - 确保 pyproject.toml 中 apache-tvm-ffi 依赖版本兼容
- **Acceptance Criteria Addressed**: AC-12, Non-Goal（避免 add_subdirectory）
- **Test Requirements**:
  - `programmatic` TR-16.1: 在独立 Conda 环境（仅安装 apache-tvm-ffi 包）中 cmake + build 成功
  - `programmatic` TR-16.2: pip install -e . 成功，import caffe_ffi 正常
  - `programmatic` TR-16.3: pytest 全部通过

## [ ] Task 17: 内存管理与稳定性验证
- **Priority**: medium
- **Depends On**: Task 7, Task 11
- **Status**: ⬜ 待开始
- **Description**:
  - 使用 AddressSanitizer（-fsanitize=address）编译运行测试
  - 验证 tvm::ffi ObjectPtr 引用计数在 Net 销毁时正确释放所有 Blob/Layer
  - 多次创建/销毁 Net 验证无内存累积
  - 边界情况测试：空网络、单 Layer 网络、异常 prototxt、大 Batch Size
  - 验证 CPUMemAlloc 与 Tensor::FromNDAlloc 的正确交互
- **Acceptance Criteria Addressed**: AC-10
- **Test Requirements**:
  - `programmatic` TR-17.1: ASan 编译运行无内存泄漏报告
  - `programmatic` TR-17.2: 循环创建销毁 Net 100 次后内存稳定
  - `programmatic` TR-17.3: Batch Size 256 推理无崩溃
  - `programmatic` TR-17.4: 异常输入（空字符串/错误prototxt）优雅报错不崩溃

---

## 任务依赖关系图

```
Task 1 (骨架/构建) ─→ Task 2 (Proto) ─┐
                  └→ Task 3 (核心类型) ─→ Task 4 (Layer基类) ─→ Task 5 (Net)
                                              │                     │
                                              ├→ Task 6 (第一批Layer: ✅) ─┐
                                              │                           │
                                              └→ Task 15 (BLAS) ─→ Task 7 (第二批Layer)
                                                               │
                                              Task 8 (第三批Layer) ──┘
                                                                 │
                           Task 9 (Python绑定: ✅) ←─────────────┘
                              │
                              ├→ Task 10 (caffemodel加载: 🔄)
                              ├→ Task 11 (Python测试: ✅)
                              ├→ Task 14 (文档: ✅)
                              │
Task 16 (find_package迁移)    │
Task 13 (Conda完善: 🔄)       │
                              └→ Task 12 (C++测试) → Task 17 (稳定性验证)
```

## 里程碑

| 里程碑 | 包含任务 | 状态 |
|--------|---------|------|
| **M1: 核心骨架可运行** | Task 1-6, 9, 11, 14 | ✅ 已完成（MLP 推理可运行） |
| **M2: BLAS+卷积池化** | Task 15, 7 | ⬜ 待开始 |
| **M3: 完整推理能力** | Task 8, 10 | ⬜ 待开始 |
| **M4: 生产就绪** | Task 12, 13, 16, 17 | ⬜ 待开始 |
