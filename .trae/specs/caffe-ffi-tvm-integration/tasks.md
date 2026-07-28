# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Implementation Plan

> **最近更新**: 2026-07-29
> **当前状态**: ✅ M1-M4核心功能全部完成并原子提交归档（含TVM FFI最佳实践优化+中文文档+模式萃取+caffe-slim迁移草案+测试标记修复）；M5 Conda配置文件已完善，C++测试/ASan待编译环境
> **测试结果**: pytest 83 passed, 19 skipped（纯Python模式，C++扩展未编译时全部skip）；C++模式历史最佳：101 passed, 1 skipped（MSVC Release构建验证）
> **编译验证**: cmake + MSVC Release build，零编译错误零新增警告
> **性能验证**: zero_copy_vs_copy_demo.py实测10M float32元素零拷贝加速3749×（恒定~4µs访问延迟），指针一致性+写后读回验证通过
> **关键成果**: 20个Layer全部实现、双类模式重构、零拷贝Tensor、@register_object绑定消除monkey patch、三层日志架构、Doxygen注释、错误处理增强、性能基准报告（中文）、caffe-slim零拷贝改造草案、4个可复用模式萃取、Conda环境配置完善（environment.yml+conda_build.bat/sh）、4个Conventional Commits原子提交归档（49文件+4245/-935行）

---

## [x] Task 1: 项目目录骨架与构建系统初始化
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成
- **Description**:
  - 创建 caffe-ffi 目录结构：include/caffe_ffi/, src/caffe_ffi/, python/caffe_ffi/, proto/, tests/, examples/
  - 编写顶层 CMakeLists.txt，配置 C++17、tvm-ffi（本地开发add_subdirectory fallback，生产环境find_package）、Protobuf 7.0+、BLAS条件编译、DLL复制
  - 编写 pyproject.toml（scikit-build-core，Python >= 3.14，protobuf >= 7.0.0，numpy >= 2.3，apache-tvm-ffi）
  - 配置 protobuf 代码生成（C++ + Python），Windows DLL 自动复制
  - 预生成 caffe_pb2.py 提交仓库
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Deliverables**: CMakeLists.txt, pyproject.toml
- **Post-optimization notes**: CMakeLists.txt已更新支持find_package(tvm_ffi CONFIG REQUIRED)，tvm_ffi_configure_target()已调用；本地开发保留add_subdirectory fallback自动检测tvm-ffi源码目录

## [x] Task 2: Proto 定义与代码生成集成
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - 复用 caffe-slim 精简版 caffe.proto（保留所有20个Layer所需的Parameter消息）
  - CMake protoc 自定义命令生成 .pb.cc/.pb.h 和 caffe_pb2.py
  - 生成目录 build/caffe_proto_gen/，Python 文件复制到 python/caffe_ffi/
  - 预生成 caffe_pb2.py 提交仓库，开箱即用
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Deliverables**: caffe.proto, caffe_pb2.py

## [x] Task 3: 核心类型定义与 TVM FFI 对象系统集成（双类模式优化完成）
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成（optimization阶段双类模式重构完成）
- **Description**:
  - common.hpp：typedef（BlobArray/LayerArray）、using namespace tvm::ffi仅在caffe_ffi命名空间内
  - fill.hpp：caffe_set_fp32/caffe_copy_fp32/caffe_cpu_axpby_fp32 纯 C++ 实现
  - log.hpp：三层日志架构C++核心层（RAII Logger + 编译期门控 + 6级日志 + 组件标签）
  - math_utils.hpp：CPU BLAS条件编译（有BLAS用cblas，无BLAS纯C++ fallback）
  - blob.hpp/cpp：**BlobObj+Blob双类模式**，Tensor(DLPack)存储data/diff，CPUMemAlloc，data_tensor()/diff_tensor()直接返回Tensor，Reshape(Shape)零拷贝，FromProto/ToProto/Update，完整生命周期日志，Doxygen注释，TVM_FFI_ICHECK参数校验
  - layer.hpp/cpp：**LayerObj+Layer双类模式**，NVI接口（SetUp→LayerSetUp→Reshape→Forward），Array<Blob> blobs_容器，name()方法，完整生命周期日志，Doxygen注释
  - net.hpp/cpp：**NetObj+Net双类模式**，Map<String,int64_t>名称索引，Array<Layer>/Array<Blob>容器，CopyTrainedLayersFrom权重加载，Forward返回Map<String,Blob>，完整DAG日志，Doxygen注释
  - layer_factory.hpp：LayerRegistry工厂适配双类模式，REGISTER_LAYER_CLASS宏
  - _caffe_ffi.cc：13个TVM_FFI_DLL_EXPORT_TYPED_FUNC导出（Version/NewBlob/NewBlobFromShape/NewNetFromProtoString/NewNetFromFile/LayerTypeList/SetLogLevel/GetLogLevel/TotalAllocatedBytes/LiveBlobCount/GetBacktrace/BlobDataTensor/BlobDiffTensor/BlobUpdate）
- **Acceptance Criteria Addressed**: AC-2, AC-8, AC-12
- **Deliverables**: blob.hpp/cpp, layer.hpp/cpp, net.hpp/cpp, log.hpp, common.hpp, fill.hpp, math_utils.hpp, layer_factory.hpp, _caffe_ffi.cc

## [x] Task 4: Layer 基类与注册工厂
- **Priority**: high
- **Depends On**: Task 3
- **Status**: ✅ 已完成（optimization阶段适配双类模式）
- **Description**:
  - LayerObj继承Object，TVM_FFI_DECLARE_OBJECT_INFO（_type_child_slots=20，支持20个子类）
  - Layer继承ObjectRef，TVM_FFI_DEFINE_OBJECT_REF_METHODS
  - LayerRegistry工厂（std::unordered_map），REGISTER_LAYER_CLASS宏通过TVM_FFI_STATIC_INIT_BLOCK注册
  - Layer使用caffe::LayerParameter protobuf配置
  - param.hpp/param.cpp：LayerParameter处理（Blob从BlobProto复制参数）
  - 全部20个Layer子类正确继承LayerObj，均添加三层日志
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Deliverables**: layer.hpp, layer_factory.hpp

## [x] Task 5: Net 计算图实现（双类模式+容器统一完成）
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成（optimization阶段完成双类重构+Map容器统一）
- **Description**:
  - NetObj+Net双类模式
  - 内部容器统一为TVM FFI类型：layers_(Array<Layer>)、blobs_(Array<Blob>)、blobs_names_index_(Map<String,int64_t>)
  - DAG拓扑构建：AppendTop/AppendBottom管理available_blobs和blob_back_pointer
  - 顺序Forward执行：reshape→Forward_cpu→loss计算
  - blobs_array/layers_array/input_blobs_array/output_blobs_array返回Array FFI桥接
  - blob_by_name/layer_by_name/has_blob/has_layer查询接口
  - CopyTrainedLayersFrom：按层名匹配加载blobs权重
  - Forward未知输入blob名抛出异常并列出可用blob名
  - 13个全局FFI函数通过TVM_FFI_DLL_EXPORT_TYPED_FUNC导出
- **Acceptance Criteria Addressed**: AC-4, AC-8
- **Deliverables**: net.hpp, net.cpp
- **Post-optimization notes**: 内部容器已从std::vector/std::map迁移到Array/Map；Forward返回Map<String,Blob>

## [x] Task 6: 第一批基础 Layer（Input/ReLU/InnerProduct/Softmax/Flatten）
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成
- **Description**:
  - InputLayer：设置输入Blob形状，支持多top、多shape
  - ReLULayer：max(0,x)激活，支持negative_slope和in-place
  - InnerProductLayer：全连接层，bias_term/transpose/axis参数，纯C++三重循环矩阵乘法（BLAS fallback已集成）
  - SoftmaxLayer：softmax归一化
  - FlattenLayer：展平张量（axis/end_axis参数）
  - 每个Layer通过REGISTER_LAYER_CLASS注册，均添加三层日志（LayerSetUp参数/Reshape shape/Forward计算维度）
- **Acceptance Criteria Addressed**: AC-7a
- **Deliverables**: input_layer.cpp, relu_layer.cpp, inner_product_layer.cpp, softmax_layer.cpp, flatten_layer.cpp
- **Test Requirements (verified)**:
  - ReLU: 正值不变，负值置零，negative_slope缩放，in-place ✅
  - InnerProduct: 矩阵乘法+bias正确，权重从BlobProto加载 ✅
  - Softmax: 输出概率和为1，全零→均匀分布 ✅
  - Flatten: 形状展平正确（包括end_axis=-1）✅
  - MLP端到端: Input→FC→ReLU→FC→Softmax推理正确，C++输出与numpy手动计算一致 ✅

## [x] Task 7: 第二批计算密集 Layer（Convolution/Pooling/BatchNorm/Scale/Bias/Accuracy/SoftmaxWithLoss）
- **Priority**: high
- **Depends On**: Task 15 (BLAS 集成)
- **Status**: ✅ 已完成
- **Description**:
  - BLAS条件编译：caffe_cpu_gemm/cblas_sgemm、caffe_cpu_gemv（有BLAS用cblas，无BLAS用纯C++ fallback）
  - im2col/col2im float版本已实现
  - ConvolutionLayer：im2col + gemm卷积（num_output/kernel_size/stride/pad/group/dilation/bias_term）
  - PoolingLayer：Max和Average池化（kernel_size/stride/pad/global_pooling/CEIL/FLOOR round_mode）
  - BatchNormLayer：均值/方差归一化（use_global_stats/moving_average_fraction/eps）
  - ScaleLayer：scale + bias（axis/num_axes/bias_term）
  - BiasLayer：广播偏置加法
  - SoftmaxWithLossLayer：推理模式只跑Softmax前向
  - AccuracyLayer：top-k精度计算（ignore_label支持）
  - 所有Layer均添加三层日志
- **Acceptance Criteria Addressed**: AC-7b
- **Deliverables**: conv_layer.cpp, pooling_layer.cpp, batch_norm_layer.cpp, scale_layer.cpp, bias_layer.cpp, accuracy_layer.cpp, softmax_loss_layer.cpp
- **Test Requirements (verified)**:
  - Convolution前向输出与numpy参考一致 ✅（纯Python+C++验证）
  - Pooling最大/平均计算正确 ✅
  - Softmax输出和为1 ✅
  - BatchNorm + Scale组合输出正确 ✅
  - Accuracy计算正确 ✅

## [x] Task 8: 第三批常用 Layer（激活/拼接/形状变换）
- **Priority**: medium
- **Depends On**: Task 6
- **Status**: ✅ 已完成
- **Description**:
  - SigmoidLayer：1/(1+exp(-x))
  - TanHLayer：(exp(x)-exp(-x))/(exp(x)+exp(-x))
  - PReLULayer：参数化ReLU（channel_shared/slope_filler）
  - ELULayer：指数线性单元（alpha参数）
  - DropoutLayer：推理模式恒等映射
  - ConcatLayer：沿指定维度拼接（concat_dim/axis参数）
  - EltwiseLayer：逐元素操作（PROD/SUM/MAX + coeff）
  - ReshapeLayer：形状变换（dim/axis/num_axes，-1推断维度）
  - 所有Layer均添加三层日志
- **Acceptance Criteria Addressed**: AC-7c
- **Deliverables**: sigmoid_layer.cpp, tanh_layer.cpp, prelu_layer.cpp, elu_layer.cpp, dropout_layer.cpp, concat_layer.cpp, eltwise_layer.cpp, reshape_layer.cpp
- **Test Requirements (verified)**:
  - Sigmoid/TanH输出范围正确 ✅
  - Concat沿axis=1/0正确拼接 ✅
  - Eltwise加/乘/最大操作正确 ✅
  - Reshape正确变换形状且不改变数据 ✅

## [x] Task 9: TVM FFI Python 绑定与 numpy 互操作（@register_object重构完成）
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Status**: ✅ 已完成（optimization阶段@register_object重构，消除monkey patch）
- **Description**:
  - src/caffe_ffi/_caffe_ffi.cc：FFI绑定入口，使用TVM_FFI_DLL_EXPORT_TYPED_FUNC导出13个全局函数
  - python/caffe_ffi/_ffi_api.py：LIB加载（load_lib_module）、init_ffi_api、TYPE_CHECKING存根、register_object导入
  - python/caffe_ffi/_core.py：**@register_object（@_reg）装饰器定义Blob/Layer/Net类**，方法统一定义在类体内，_native_method()辅助函数通过__tvm_ffi_type_info__访问C++方法，_is_native只读property检测模式，Python-only fallback兼容
  - python/caffe_ffi/blob.py/layer.py/net.py：从~200行monkey-patch代码简化为~5行重新导出（from ._core import Blob/Layer/Net）
  - python/caffe_ffi/__init__.py：包入口
  - python/caffe_ffi/io.py：prototxt/caffemodel加载工具（修复_is_native只读property赋值问题）
  - python/caffe_ffi/classifier.py：Classifier高层分类器
  - 利用DLPack实现numpy零拷贝互操作（from_dlpack/to_dlpack）
  - 完整类型注解支持IDE类型提示
- **Acceptance Criteria Addressed**: AC-5, AC-8
- **Deliverables**: _caffe_ffi.cc, _ffi_api.py, _core.py, blob.py, layer.py, net.py, io.py, classifier.py
- **Post-optimization notes**: 完全消除monkey patch和_add_python_wrappers；blob.py/net.py/layer.py代码量减少约43%

## [x] Task 10: caffemodel 权重加载与端到端真实模型验证
- **Priority**: high
- **Depends On**: Task 9
- **Status**: ✅ 已完成（C++端到端MLP验证通过；真实模型推理待C++编译后执行）
- **Description**:
  - prototxt文本解析（TextFormat.Parse → NetParameter）✅
  - caffemodel二进制加载（ParseFromIstream → NetParameter → CopyTrainedLayersFrom）✅
  - Net::CopyTrainedLayersFrom：按层名称匹配加载blobs权重，支持float/double_data兼容
  - Python net.copy_from()：FFI模式调用C++ CopyTrainedLayersFrom，纯Python模式用protobuf读取并复制
  - ReadNetParamsFromBinaryFile/ReadNetParamsFromTextFile全局函数已实现
- **Acceptance Criteria Addressed**: AC-4
- **Deliverables**: 更新的net.hpp, net.cpp, net.py, blob.cpp
- **Test Requirements (verified)**:
  - read_net_from_binary + copy_from正确加载权重 ✅（纯Python+C++验证）
  - numpy输入→前向→numpy输出全链路无错误 ✅
  - MLP端到端C++推理数值与numpy手动计算完全一致 ✅
- **Remaining**: 端到端真实模型（LeNet/MNIST）精度验证待完整环境执行

## [x] Task 11: Python 测试框架与基础测试
- **Priority**: high
- **Depends On**: Task 9
- **Status**: ✅ 已完成（C++模式101 passed, 1 skipped；纯Python模式83 passed, 19 skipped）
- **Description**:
  - tests/conftest.py：require_cpp_extension marker、fixtures、内存泄漏检测
  - tests/test_blob.py：Blob单元测试（35个测试），TestBlobMemoryCounters添加@require_cpp_extension标记修复纯Python模式下误报失败
  - tests/test_layers.py：Layer单元测试（45个测试）
  - tests/test_net.py：Net单元测试（21个测试，1个Python-only reference测试跳过）
  - examples/create_and_run_mlp.py：端到端MLP示例
  - examples/benchmark_performance.py：性能基准测试
  - C++ tests/test_dlopen.cpp：动态库加载测试
- **Acceptance Criteria Addressed**: AC-7, AC-10
- **Deliverables**: test_blob.py, test_layers.py, test_net.py, conftest.py, benchmark_performance.py, zero_copy_vs_copy_demo.py
- **Test Results**: 
  - C++模式（MSVC Release编译）：101 passed, 1 skipped in 36.16s
  - 纯Python模式（无C++扩展）：83 passed, 19 skipped, 0 failed in 2.16s
- **Post-optimization notes**: zero_copy_vs_copy_demo.py修复is_native_mode检测bug（改用_ff_api.is_available()），实测性能数据：1K→1.1×、1M→175×、10M→3749×加速比；零拷贝访问恒定~4µs，指针一致性+写后读回验证全部通过；修复TestBlobMemoryCounters缺少@require_cpp_extension标记问题（原7个测试在纯Python模式下失败，现正确skip）

## [ ] Task 12: C++ 单元测试框架（ctest）
- **Priority**: medium
- **Depends On**: Task 7
- **Status**: ⬜ 待开始
- **Description**:
  - 配置CMake ctest（enable_testing + add_test）
  - 编写tests/test_blob.cpp：Blob Reshape/引用计数
  - 编写tests/test_layers.cpp：Layer前向计算（与numpy参考对比）
  - 编写tests/test_net.cpp：Net初始化/前向/DAG构建
- **Acceptance Criteria Addressed**: AC-11
- **Test Requirements**:
  - `programmatic` TR-12.1: `ctest --test-dir build`所有测试通过
  - `programmatic` TR-12.2: Blob/Layer/Net C++测试覆盖核心路径

## [~] Task 13: Conda 环境配置完善
- **Priority**: medium
- **Depends On**: Task 8
- **Status**: 🔄 配置文件已完善，完整环境验证待执行
- **Description**:
  - environment.yml：移除m2w64-gcc（MinGW不适合MSVC项目），使用cxx-compiler自动选择平台编译器
  - environment.yml：添加国内镜像源注释（清华/阿里云），channel_priority: strict
  - environment.yml：BLAS依赖精简为libopenblas（CMake find_package自动检测）
  - environment.yml：添加ruff linter、apache-tvm-ffi通过pip安装（版本>=0.3.0）
  - environment.yml：tvm-ffi本地开发路径改为注释说明（默认从PyPI安装）
  - conda_build.bat（Windows）：三阶段构建（CMake Configure→Ninja Build→pip editable install）+ 自动运行pytest + KMP_DUPLICATE_LIB_OK
  - conda_build.sh（Linux/macOS）：同样三阶段构建 + 自动检测CPU线程数 -jN + 运行pytest
  - 验证conda env create + build在干净环境中通过（待有完整MSVC/conda环境时执行）
- **Acceptance Criteria Addressed**: AC-15
- **Deliverables**: environment.yml（完善版）, conda_build.bat, conda_build.sh
- **Remaining**: conda env create端到端验证待有完整编译环境时执行

## [x] Task 14: 基础文档与使用说明（optimization阶段完成Doxygen+性能报告）
- **Priority**: medium
- **Depends On**: Task 9
- **Status**: ✅ 已完成
- **Description**:
  - README.md：项目介绍、构建步骤、快速开始示例、支持层列表、项目结构
  - examples/create_and_run_mlp.py：可运行示例
  - examples/benchmark_performance.py：全场景性能基准测试
  - examples/zero_copy_vs_copy_demo.py：零拷贝vs拷贝性能对比Demo（1K-10M floats，指针一致性+写后读回验证）
  - Doxygen注释：覆盖blob.hpp/layer.hpp/net.hpp核心公共API
  - docs/OPTIMIZATION_REPORT.md：优化报告中文完整版（8大优化领域、性能数据、代码统计、API兼容性、三层日志架构图、后续建议）
  - docs/TEAM_SHARING_SUMMARY.md：团队分享总结
  - docs/FFI_ZEROCOPY_REFACTOR_CHECKLIST.md：跨模块零拷贝改造优先级清单（P0/P1/P2）
  - docs/caffe_slim_zerocopy_refactor_draft.md：caffe-slim模块零拷贝改造完整代码草案（C++ ffi_log.hpp + _caffe.cpp重构 + Python绑定 + 8类日志标签 + 全局内存计数器）
  - docs/FFI_ZEROCOPY_PATTERN_EXTRACTION.md：FFI零拷贝桥接可复用模式萃取（4个模式：DLPack零拷贝桥接/写入安全门/三层日志可观测性/双类对象模型，含P0-P2迁移检查清单和反模式警示）
- **Acceptance Criteria Addressed**: AC-9
- **Deliverables**: README.md, OPTIMIZATION_REPORT.md(中文), TEAM_SHARING_SUMMARY.md, FFI_ZEROCOPY_REFACTOR_CHECKLIST.md, caffe_slim_zerocopy_refactor_draft.md, FFI_ZEROCOPY_PATTERN_EXTRACTION.md
- **Post-optimization notes**: OPTIMIZATION_REPORT.md完成中文翻译；caffe_slim_zerocopy_refactor_draft.md提供了caffe-slim模块从memcpy到零拷贝的完整改造路径，包含写入零拷贝（zero_copy参数+set_cpu_data()）和8类结构化日志标签设计；FFI_ZEROCOPY_PATTERN_EXTRACTION.md萃取的4个模式可直接用于npu-ffi/demo-ffi等其他FFI模块的零拷贝改造

## [x] Task 15: BLAS 集成与性能优化
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成（条件编译+im2col/col2im；BLAS路径性能待完整BLAS环境基准测试）
- **Description**:
  - math_utils.hpp：BLAS条件编译（CAFFE_USE_BLAS宏），有BLAS时使用cblas_sgemm/cblas_sgemv/cblas_sdot，否则使用纯C++ fallback
  - caffe_cpu_gemm_fp32/caffe_cpu_gemv_fp32/caffe_cpu_strided_dot_fp32已实现
  - im2col_cpu/col2im_cpu float版本已实现
  - caffe_axpy_fp32/caffe_scal_fp32/caffe_cpu_axpby_fp32等BLAS辅助函数已实现
  - CMakeLists.txt：find_package(BLAS)逻辑，找到BLAS时自动添加CAFFE_USE_BLAS定义
- **Acceptance Criteria Addressed**: NFR-1, AC-13
- **Deliverables**: math_utils.hpp, fill.hpp
- **Test Requirements (verified)**:
  - im2col输出与numpy参考一致 ✅（通过ConvolutionLayer间接验证）
  - 纯C++ fallback路径正常工作 ✅（MSVC Release编译验证）
- **Remaining**: BLAS路径性能基准对比（需完整BLAS环境）

## [x] Task 16: tvm-ffi 依赖方式迁移（add_subdirectory → find_package）
- **Priority**: medium
- **Depends On**: None
- **Status**: ✅ 已完成（optimization阶段）
- **Description**:
  - CMakeLists.txt采用双模式：本地开发时若tvm-ffi源码目录存在（`../../tvm-ffi/CMakeLists.txt`），使用add_subdirectory fallback；否则使用find_package(tvm_ffi CONFIG REQUIRED)
  - 对_caffe_ffi目标调用tvm_ffi_configure_target()
  - DLL复制逻辑正确处理tvm_ffi相关DLL
  - pyproject.toml中apache-tvm-ffi依赖版本兼容
- **Acceptance Criteria Addressed**: AC-12
- **Test Requirements (verified)**:
  - MSVC Release编译成功 ✅
  - import caffe_ffi正常，pytest全部通过 ✅
- **Notes**: 本地开发保留add_subdirectory fallback是合理的工程实践，避免开发者必须先安装tvm-ffi包；CI/生产环境使用find_package

## [ ] Task 17: 内存管理与稳定性验证（ASan）
- **Priority**: medium
- **Depends On**: Task 7, Task 11
- **Status**: ⬜ 待开始（内存计数器已实现，ASan验证待执行）
- **Description**:
  - total_allocated_bytes()和live_blob_count()内存计数器已实现 ✅
  - benchmark_performance.py中内存泄漏检测已验证（GC后内存回到基线）✅
  - 使用AddressSanitizer（-fsanitize=address）编译运行测试
  - 验证ObjectPtr引用计数在Net销毁时正确释放
  - 边界情况测试：空网络、单Layer网络、异常prototxt、大Batch Size
- **Acceptance Criteria Addressed**: AC-14
- **Notes**: 内存计数器和benchmark验证表明无明显泄漏，但ASan正式验证待Linux/GCC环境执行

---

## 任务依赖关系图

```
Task 1 (骨架/构建) ─→ Task 2 (Proto) ─┐
                  └→ Task 3 (核心类型/双类模式✅) ─→ Task 4 (Layer基类✅) ─→ Task 5 (Net✅)
                                              │                     │
                                              ├→ Task 6 (第一批Layer✅) ─┐
                                              │                           │
                                              └→ Task 15 (BLAS✅) ─→ Task 7 (第二批Layer✅)
                                                               │
                                              Task 8 (第三批Layer✅) ──┘
                                                                 │
                           Task 9 (Python绑定@register_object✅) ←─┘
                              │
                              ├→ Task 10 (caffemodel加载✅)
                              ├→ Task 11 (Python测试: 101 passed✅)
                              ├→ Task 14 (文档/Doxygen/报告✅)
                              ├→ Task 16 (find_package迁移✅)
                              │
                              └→ Task 12 (C++测试⬜) → Task 17 (ASan稳定性⬜)
                              
                              Task 13 (Conda完善⬜)
```

## 里程碑

| 里程碑 | 包含任务 | 状态 |
|--------|---------|------|
| **M1: 核心骨架可运行** | Task 1-6, 9, 11, 14 | ✅ 已完成（MLP推理可运行） |
| **M2: BLAS+卷积池化** | Task 15, 7 | ✅ 已完成（BLAS+im2col+Conv/Pool/BN/Scale/Bias/Accuracy/SoftmaxWithLoss） |
| **M3: 完整推理能力** | Task 8, 10 | ✅ 已完成（20个Layer，caffemodel权重加载，101 passed） |
| **M4: TVM FFI最佳实践** | Task 3/5/9/16（双类模式+零拷贝+@register_object+find_package）+日志+Doxygen+性能 | ✅ 已完成（optimization spec全部任务完成，性能报告已生成） |
| **M5: 生产就绪** | Task 12, 13, 17 | 🔄 Conda配置已完善；C++ ctest/ASan待编译环境 |
