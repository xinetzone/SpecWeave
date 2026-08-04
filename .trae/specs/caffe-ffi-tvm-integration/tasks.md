# Caffe-FFI: 基于 TVM FFI 的 Caffe 深度学习框架 - Implementation Plan

> **最近更新**: 2026-08-04
> **当前状态**: ✅ M1-M9全部完成，P4（优化/扩展）规划中
> **版本进展**:
>   - v0.1.0 (M1-M6): 20层、Docker、独立项目 — 已完成
>   - v1.1.0 (M7): COW零拷贝共享、内存追踪、562测试 — 已完成
>   - v1.2.0 (M8): InsertSplits图变换、25层、P3-C Transformer — 已完成
>   - M9 (P3): Backward 19类层892测试、LeNet/MNIST训练97.95%、CI三平台、P3-B/C/D/E四阶段闭环 — 已完成
> **测试结果**: 
>   - 全量测试: 1646 passed, 1 skipped, 0 failures
>   - Docker Linux Python 3.14.6: 1646 passed/1 skipped
>   - GitHub Actions CI: Linux/macOS/Windows三平台验证通过（含COW_PHASE3宏）
>   - C++测试: header-only框架，覆盖Blob/Net/NeuronLayers/InsertSplits/Deconv/ZeroCopy/符号导出
> **性能验证**:
>   - 零拷贝恒定~4µs访问，10M元素加速3749×
>   - COW共享O(1)
>   - P3-B测试套件134s→8.27s（16.2x加速，通过分层GC/CSV缓冲/日志抑制）
>   - LeNet on MNIST训练test acc 97.95%（loss 2.32→0.04）
> **关键成果**:
>   - M1-M6: 20层、双类模式、零拷贝、@register_object、三层日志、反射52方法、DLL边界修复、C++测试40/40、Docker环境
>   - M7: COW机制(Share/Unshare/IsShared/RefCount/mutable_*自动克隆)、内存追踪工具、21个COW测试、引用循环泄漏修复
>   - M8: InsertSplits 18边界测试、25层(+Crop/Deconv/LRN/Slice/Split)、P3-C Transformer 13测试、Sigmoid饱和精度修复、InsertSplits算法文档
>   - M9: Backward 19类层892测试、LeNet/MNIST训练97.95%、C¹拐点防护、CI三平台(含COW_PHASE3宏)、SetShapeOnly API、perf_monitor、numpy RNN参考实现、P3-E验收报告+P3总复盘+P4路线图

---

## [x] Task 1: 项目目录骨架与构建系统初始化
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成
- **Description**:
  - 创建 caffe-ffi 目录结构：include/caffe_ffi/, src/caffe_ffi/, python/caffe_ffi/, proto/, tests/, examples/
  - 编写顶层 CMakeLists.txt，配置 C++17、tvm-ffi（本地开发add_subdirectory fallback，生产环境find_package）、Protobuf 7.0+、BLAS条件编译、DLL复制
  - 编写 pyproject.toml（scikit-build-core，Python >= 3.14，protobuf >= 7.0.0，numpy >= 2.3，apache-tvm-ffi > 0.1.12）
  - 配置 protobuf 代码生成（C++ + Python），Windows DLL 自动复制
  - 预生成 caffe_pb2.py 提交仓库
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Deliverables**: CMakeLists.txt, pyproject.toml
- **Post-optimization notes**: CMake已原子化为9个模块(cmake/*.cmake)，默认find_package(tvm_ffi CONFIG REQUIRED)

## [x] Task 2: Proto 定义与代码生成集成
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - 复用 caffe-slim 精简版 caffe.proto（保留所有25个Layer所需的Parameter消息，新增Crop/Deconv/LRN/Slice/Split参数）
  - CMake protoc 自定义命令生成 .pb.cc/.pb.h 和 caffe_pb2.py
  - 生成目录 build/caffe_proto_gen/，Python 文件复制到 python/caffe_ffi/
  - 预生成 caffe_pb2.py 提交仓库，开箱即用
- **Acceptance Criteria Addressed**: AC-1, AC-6
- **Deliverables**: caffe.proto, caffe_pb2.py

## [x] Task 3: 核心类型定义与 TVM FFI 对象系统集成（双类模式+COW）
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - common.hpp：typedef（BlobArray/LayerArray）、using namespace tvm::ffi仅在caffe_ffi命名空间内
  - fill.hpp：caffe_set_fp32/caffe_copy_fp32/caffe_cpu_axpby_fp32 纯 C++ 实现
  - log.hpp：三层日志架构C++核心层（RAII Logger + 编译期门控 + 6级日志 + 组件标签）+ [ACTIVATION-PERF] Backward性能日志
  - math_utils.hpp：CPU BLAS条件编译（有BLAS用cblas，无BLAS纯C++ fallback）
  - perf_monitor.hpp：性能监控基础设施
  - blob.hpp/cpp：**BlobObj+Blob双类模式**，Tensor(DLPack)存储data/diff，**COW零拷贝共享机制**，CPUMemAlloc，data_tensor()/diff_tensor()/mutable_*()，Reshape/SetShapeOnly/FromProto/ToProto/Update/ShareData/ShareDiff/Unshare/IsShared/RefCount，完整生命周期日志
  - layer.hpp/cpp：**LayerObj+Layer双类模式**，NVI接口（SetUp→LayerSetUp→Reshape→Forward→Backward），Array<Blob> blobs_容器，name()方法
  - net.hpp/cpp：**NetObj+Net双类模式**，Map<String,int64_t>名称索引，Array<Layer>/Array<Blob>容器，CopyTrainedLayersFrom权重加载，InsertSplits自动图变换，Forward/Backward顺序/逆序执行
  - layer_factory.hpp/cpp：LayerRegistry工厂，REGISTER_LAYER_CLASS宏，Windows DLL单例修复
  - _caffe_ffi.cc：反射系统注册+COW/内存/Backward相关FFI函数导出
- **Acceptance Criteria Addressed**: AC-2, AC-8, AC-12, AC-24, AC-29
- **Deliverables**: blob.hpp/cpp, layer.hpp/cpp, net.hpp/cpp, log.hpp, perf_monitor.hpp, common.hpp, fill.hpp, math_utils.hpp, layer_factory.hpp, _caffe_ffi.cc

## [x] Task 4: Layer 基类与注册工厂
- **Priority**: high
- **Depends On**: Task 3
- **Status**: ✅ 已完成
- **Description**:
  - LayerObj继承Object，TVM_FFI_DECLARE_OBJECT_INFO（_type_child_slots=25，支持25个子类）
  - Layer继承ObjectRef，TVM_FFI_DEFINE_OBJECT_REF_METHODS
  - LayerRegistry工厂（std::unordered_map），REGISTER_LAYER_CLASS宏通过TVM_FFI_STATIC_INIT_BLOCK注册
  - Layer使用caffe::LayerParameter protobuf配置
  - param.hpp/param.cpp：LayerParameter处理
  - 全部25个Layer子类正确继承LayerObj，均添加三层日志
- **Acceptance Criteria Addressed**: AC-3, AC-7
- **Deliverables**: layer.hpp, layer_factory.hpp

## [x] Task 5: Net 计算图实现（双类模式+InsertSplits+Backward）
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成
- **Description**:
  - NetObj+Net双类模式
  - 内部容器统一为TVM FFI类型：layers_(Array<Layer>)、blobs_(Array<Blob>)、blobs_names_index_(Map<String,int64_t>)
  - DAG拓扑构建：AppendTop/AppendBottom管理available_blobs和blob_back_pointer
  - **InsertSplits自动图变换Pass**：多消费方Blob自动插入Split层，命名与原生Caffe对齐
  - 顺序Forward执行：reshape→Forward_cpu→loss计算
  - **逆序Backward执行**：Backward_cpu逆序传播梯度
  - blobs_array/layers_array/input_blobs_array/output_blobs_array返回Array FFI桥接
  - blob_by_name/layer_by_name/has_blob/has_layer查询接口
  - CopyTrainedLayersFrom：按层名匹配加载blobs权重
  - ShareData自动共享机制
- **Acceptance Criteria Addressed**: AC-4, AC-8, AC-25, AC-26
- **Deliverables**: net.hpp, net.cpp

## [x] Task 6: 第一批基础 Layer（Input/ReLU/InnerProduct/Softmax/Flatten）
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成
- **Description**:
  - InputLayer：设置输入Blob形状，支持多top、多shape
  - ReLULayer：max(0,x)激活，支持negative_slope和in-place，Backward实现+C¹拐点防护
  - InnerProductLayer：全连接层，bias_term/transpose/axis参数，Forward+Backward（梯度解析验证通过，23个测试）
  - SoftmaxLayer：softmax归一化
  - FlattenLayer：展平张量（axis/end_axis参数）
- **Acceptance Criteria Addressed**: AC-7a, AC-26
- **Deliverables**: input_layer.cpp, relu_layer.cpp, inner_product_layer.cpp, softmax_layer.cpp, flatten_layer.cpp

## [x] Task 7: 第二批计算密集 Layer（Convolution/Pooling/BatchNorm/Scale/Bias/Accuracy/SoftmaxWithLoss）
- **Priority**: high
- **Depends On**: Task 15 (BLAS 集成)
- **Status**: ✅ 已完成（Forward已验证；Backward待完整数值验证）
- **Description**:
  - BLAS条件编译：caffe_cpu_gemm/cblas_sgemm、caffe_cpu_gemv
  - im2col/col2im float版本已实现
  - ConvolutionLayer：im2col + gemm卷积，Forward+Backward代码已有
  - PoolingLayer：Max和Average池化，Forward+Backward代码已有
  - BatchNormLayer：均值/方差归一化，Forward+Backward实现+测试
  - ScaleLayer：scale + bias，Forward+Backward代码已有
  - BiasLayer：广播偏置加法
  - SoftmaxWithLossLayer：推理模式前向+Backward测试完成
  - AccuracyLayer：top-k精度计算
- **Acceptance Criteria Addressed**: AC-7b, AC-26
- **Deliverables**: conv_layer.cpp, pooling_layer.cpp, batch_norm_layer.cpp, scale_layer.cpp, bias_layer.cpp, accuracy_layer.cpp, softmax_loss_layer.cpp

## [x] Task 8: 第三批常用 Layer（激活/拼接/形状变换）
- **Priority**: medium
- **Depends On**: Task 6
- **Status**: ✅ 已完成
- **Description**:
  - SigmoidLayer：1/(1+exp(-x))，Forward+Backward+C¹饱和精度修复
  - TanHLayer：tanh激活，Forward+Backward
  - PReLULayer：参数化ReLU，Forward+Backward+C¹拐点防护
  - ELULayer：指数线性单元，Forward+Backward+C¹拐点防护+稳定性专项测试
  - DropoutLayer：推理模式恒等映射
  - ConcatLayer：沿指定维度拼接
  - EltwiseLayer：逐元素操作（PROD/SUM/MAX + coeff）
  - ReshapeLayer：形状变换
- **Acceptance Criteria Addressed**: AC-7c, AC-26, AC-27
- **Deliverables**: sigmoid_layer.cpp, tanh_layer.cpp, prelu_layer.cpp, elu_layer.cpp, dropout_layer.cpp, concat_layer.cpp, eltwise_layer.cpp, reshape_layer.cpp

## [x] Task 8b: 第四批扩展 Layer（Crop/Deconv/LRN/Slice/Split）
- **Priority**: medium
- **Depends On**: Task 7, Task 8
- **Status**: ✅ 已完成（v1.2.0/M8）
- **Description**:
  - CropLayer：裁剪层（Forward+Backward）
  - DeconvolutionLayer：反卷积层（Forward+Backward）
  - LRNLayer：局部响应归一化（Forward+Backward）
  - SliceLayer：切片层（Forward+Backward）
  - SplitLayer：拆分层（Forward+Backward，COW ShareData零拷贝共享）
  - 所有层均添加三层日志
  - C++测试覆盖DeconvLayer
- **Acceptance Criteria Addressed**: AC-7d, AC-24, AC-26
- **Deliverables**: crop_layer.cpp, deconv_layer.cpp, lrn_layer.cpp, slice_layer.cpp, split_layer.cpp

## [x] Task 9: TVM FFI Python 绑定与 numpy 互操作（@register_object+COW感知）
- **Priority**: high
- **Depends On**: Task 5, Task 6
- **Status**: ✅ 已完成
- **Description**:
  - _core.py：@register_object装饰器定义Blob/Layer/Net类，COW感知mutable_*方法，backward()方法
  - blob.py/layer.py/net.py：简化重新导出
  - 利用DLPack实现numpy零拷贝互操作（from_dlpack/to_dlpack）
  - COW：mutable_data()/mutable_diff()触发自动COW克隆
  - caffe_ffi.tools.memory：BlobRef/tracked_blob/blob_snapshot/mem_check内存追踪工具
- **Acceptance Criteria Addressed**: AC-5, AC-8, AC-24
- **Deliverables**: _caffe_ffi.cc, _ffi_api.py, _core.py, blob.py, layer.py, net.py, io.py, classifier.py, tools/memory.py

## [x] Task 10: caffemodel 权重加载与端到端验证
- **Priority**: high
- **Depends On**: Task 9
- **Status**: ✅ 已完成（Forward；训练端到端待完成）
- **Description**:
  - prototxt文本解析、caffemodel二进制加载
  - Net::CopyTrainedLayersFrom：按层名称匹配加载blobs权重
  - Python net.copy_from()：FFI模式调用C++
- **Acceptance Criteria Addressed**: AC-4
- **Deliverables**: 更新的net.hpp, net.cpp, net.py, blob.cpp

## [x] Task 11: Python 测试框架与测试套件（含Backward+性能优化）
- **Priority**: high
- **Depends On**: Task 9
- **Status**: ✅ 已完成（561/562 passed；测试基础设施16.2x加速）
- **Description**:
  - conftest.py：require_cpp_extension marker、fixtures、内存泄漏检测、**分层GC策略(quick/full/off)**
  - test_blob.py：Blob单元测试
  - test_layers.py：Layer Forward单元测试
  - test_net.py：Net单元测试
  - test_cow.py：COW机制21个测试
  - test_insert_splits.py：InsertSplits 18个边界测试
  - test_inner_product_backward.py：InnerProduct Backward 23个测试（解析梯度+数值检查）
  - test_batch_norm_backward.py：BatchNorm Backward测试
  - test_activation_backward.py：激活函数Backward测试（C¹拐点防护）
  - test_elu_kink_stability.py：ELU拐点稳定性专项测试
  - test_complex_topologies.py/test_split_topologies.py：复杂拓扑测试
  - test_p3a_conv_pool_bn.py/test_p3b_eltwise_scale.py/test_p3c_activations_ip.py/test_p3c_transformer.py/test_p3d_slice_crop_deconv_lrn.py：P3阶段测试套件
  - test_phase3_*.py：Phase 3特性测试
  - test_extreme_boundaries.py/test_extreme_inputs.py：边界情况测试
  - **测试基础设施性能优化**：分层GC、CSV 20行批量flush、perf_trace采样调整、C++日志抑制 — P3-B 134s→8.27s（16.2x）
- **Acceptance Criteria Addressed**: AC-7, AC-10, AC-27, AC-31
- **Test Results**: Docker Linux 561/562 passed (1 skipped), 0 failures

## [x] Task 12: C++ 单元测试框架
- **Priority**: medium
- **Depends On**: Task 7
- **Status**: ✅ 已完成（扩展覆盖多个模块）
- **Description**:
  - header-only轻量C++测试框架（test_harness.hpp），高精度耗时统计、Per-suite汇总、Top 5 slowest报告
  - test_blob.cpp/test_blob_zerocopy.cpp：Blob测试+零拷贝测试
  - test_net.cpp：Net测试
  - test_neuron_layers.cpp：神经元层测试
  - test_insert_splits.cpp：InsertSplits测试
  - test_deconv_layer.cpp：反卷积层测试
  - test_objectptr_migration.cpp：ObjectPtr迁移测试
  - test_symbol_export.cpp：符号导出测试
  - CMake配置caffe_ffi_tests可执行目标
- **Acceptance Criteria Addressed**: AC-11
- **Deliverables**: test_harness.hpp + 8个测试文件

## [x] Task 13: Conda 环境配置完善
- **Priority**: medium
- **Depends On**: Task 8
- **Status**: ✅ 已完成
- **Description**:
  - environment.yml：Python 3.14、cmake、ninja、protobuf、libopenblas、pytest、ruff、pip依赖
  - conda_build.bat/sh：三阶段构建脚本
  - Docker环境作为黄金标准验证环境
- **Acceptance Criteria Addressed**: AC-15
- **Deliverables**: environment.yml, conda_build.bat, conda_build.sh

## [x] Task 14: 基础文档与使用说明
- **Priority**: medium
- **Depends On**: Task 9
- **Status**: ✅ 已完成（大量扩展）
- **Description**:
  - README.md：项目介绍、Docker快速开始、本地安装、Windows开发指南、构建失败L0→L1→L2分层排查
  - docs/performance/：P0/P1/P2B/Phase2性能报告
  - docs/design/：COW设计、InsertSplits算法、SetShapeOnly API、零拷贝模式萃取
  - docs/plans/：激活性能监控规格、Backward日志计划、InsertSplits图变换
  - docs/retrospectives/：6份回溯报告（COW迁移、构建修复、SoftmaxLoss Backward、Split COW Phase3、零拷贝Phase1、内存日志）
  - docs/setup/：构建验证报告、跨机器构建设置、Protobuf兼容、WSL2设置
  - docs/summaries/：构建修复总结、产品简报、任务执行总结、团队分享
  - docs/testing/：TESTING_GUIDELINES.md测试指南
  - docs/checklists/：COW边界清单、零拷贝重构清单、零拷贝入门清单
  - test-infra-performance-optimization.md：测试基础设施性能优化最佳实践（已入知识库）
- **Acceptance Criteria Addressed**: AC-9
- **Deliverables**: README.md + 20+份技术文档

## [x] Task 15: BLAS 集成与性能优化
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成（条件编译+im2col/col2im；BLAS路径性能待基准）
- **Description**:
  - math_utils.hpp：BLAS条件编译（CAFFE_USE_BLAS宏）
  - caffe_cpu_gemm/gemv/strided_dot/axpy/scal/axpby已实现
  - im2col_cpu/col2im_cpu float版本已实现
  - CMakeLists.txt：find_package(BLAS)逻辑，DetectBLAS.cmake/DetectOpenBLAS.cmake模块
- **Acceptance Criteria Addressed**: NFR-1, AC-13
- **Remaining**: BLAS路径性能基准对比（需完整BLAS环境）

## [x] Task 16: tvm-ffi 依赖方式迁移（add_subdirectory → find_package）
- **Priority**: medium
- **Depends On**: None
- **Status**: ✅ 已完成
- **Description**:
  - Dependencies.cmake默认find_package(tvm_ffi CONFIG REQUIRED)，CAFFE_FFI_TVM_FFI_DIR选项指定本地路径
  - tvm_ffi_configure_target()调用
  - 禁止使用Find<Name>.cmake命名（使用Detect<Name>.cmake）
- **Acceptance Criteria Addressed**: AC-12

## [x] Task 17: 内存管理与COW机制（M7）
- **Priority**: high
- **Depends On**: Task 3, Task 11
- **Status**: ✅ 已完成（v1.1.0, 2026-07-30）
- **Description**:
  - COW核心API：ShareData/ShareDiff/UnshareData/UnshareDiff/IsDataShared/IsDiffShared/DataRefCount/DiffRefCount
  - mutable_data_tensor()/mutable_diff_tensor()：写时自动COW克隆
  - data_shared_/diff_shared_标志位精确追踪共享状态
  - CAFFE_FFI_ENABLE_COW/CAFFE_FFI_ENABLE_COW_PHASE3环境变量
  - Reshape() COW失效修复（仅shape变化时清除共享标记）
  - _tensor_to_numpy引用循环泄漏修复（_blob_ref挂载到numpy ctypes数组）
  - 内存生命周期追踪工具：caffe_ffi.tools.memory（BlobRef/tracked_blob/blob_snapshot/mem_check）
  - 内存压力测试：500次create/fill/destroy循环零泄漏
  - 21个COW测试用例（API/拓扑/snapshot/refcount/forward场景）
- **Acceptance Criteria Addressed**: AC-24
- **Test Results**: 21/21 COW tests passed, 500-cycle stress test zero leak

## [ ] Task 17b: ASan内存管理验证
- **Priority**: medium
- **Depends On**: Task 17
- **Status**: ⬜ 待开始（内存计数器已实现，ASan正式验证待Linux/GCC环境）
- **Description**:
  - total_allocated_bytes()/live_blob_count()内存计数器已实现
  - 使用AddressSanitizer（-fsanitize=address）编译运行测试
  - 验证ObjectPtr引用计数在Net销毁时正确释放
  - COW引用计数正确性验证
- **Acceptance Criteria Addressed**: AC-14
- **Notes**: 内存计数器和压力测试表明无明显泄漏，ASan正式验证待执行

## [x] Task 18: M6-独立项目萃取迁移（vendor→libs）
- **Priority**: high
- **Depends On**: Task 12, Task 16
- **Status**: ✅ 已完成 (2026-07-30)
- **Description**:
  - 完整迁移vendor/caffe/caffe-ffi到projects/xuanspace/libs/caffe-ffi
  - 标准项目结构对齐libs/npu-ffi
  - CMake原子化重构（9个模块化.cmake文件）
  - CMakePresets.json、scripts/dev.sh/dev.ps1、conda.recipe/
  - AGENTS.md、LICENSE(BSD-2-Clause)、CHANGELOG.md
- **Acceptance Criteria Addressed**: AC-17

## [x] Task 19: M6-Docker开发环境创建（apps/caffe-ffi-jupyter）
- **Priority**: high
- **Depends On**: Task 18
- **Status**: ✅ 已完成
- **Description**:
  - apps/caffe-ffi-jupyter基于jupyter-ssh-base，双阶段builder+runtime
  - SSH+Jupyter双服务保留
  - RPATH+ldconfig+LD_LIBRARY_PATH三重共享库路径保障
  - scripts/build.sh（支持--cn国内源）、docker-compose.yml、README.md
- **Acceptance Criteria Addressed**: AC-18

## [x] Task 20: M6-工程化工具链
- **Priority**: high
- **Depends On**: Task 19
- **Status**: ✅ 已完成
- **Description**:
  - 统一结构化日志库（Bash+PowerShell双版本）
  - WSL一键部署脚本wsl-deploy.sh/deploy.ps1
  - 环境诊断脚本diagnose.sh/diagnose.ps1
  - WSL-DEPLOY-GUIDE.md部署指南
  - 跨项目可复用模式沉淀
- **Acceptance Criteria Addressed**: AC-18

## [x] Task 21: M6-测试脚本增强与Docker环境验证
- **Priority**: high
- **Depends On**: Task 19, Task 20
- **Status**: ✅ 已完成
- **Description**:
  - C++测试框架增强：高精度耗时统计、Per-suite汇总、Top 5 slowest
  - Python TimingTestResult/TimingTextTestRunner耗时统计
  - test-cpp-tests.sh集成C++/Python测试
  - CAFFE_FFI_DISABLE_BACKTRACE环境变量
  - Docker Linux Python 3.14.6验证：C++40/40+Python65/65通过（当时数据；现已扩展到561/562）
- **Acceptance Criteria Addressed**: AC-19

## [x] Task 22: M8-InsertSplits自动图变换（v1.2.0）
- **Priority**: high
- **Depends On**: Task 5
- **Status**: ✅ 已完成 (2026-07-31)
- **Description**:
  - InsertSplits Pass实现：多消费方Blob自动插入Split层
  - 命名约定与原生Caffe完全对齐（split named after last producer）
  - 18个边界情况测试（零消费死端、单消费不拆分、in-place ReLU多消费、级联拆分、幂等性、Split→Concat→Split Inception嵌套、多外部输入顺序、空网络、3+消费者、loss_weight隐式消费、混合Input+param.input()）
  - 外部输入split顺序修复：先收集所有外部输入split，在position 0批量插入
  - viz_insert_splits.py：DAG仿真+可视化+--verify交叉验证（零依赖Python参考实现）
  - tests/protos/：9个真实网络拓扑fixture（mlp_basic/mlp_branch/triple_inplace/cascading_splits/deep_supervision/multi_head/multi_input_splits/inception_like/resnet_skip）
  - Pass 2b详细日志（外部输入split移动前后层顺序）
  - 文档：INSERT_SPLITS_GRAPH_TRANSFORM.md算法参考（passes/命名/边界/调试）
- **Acceptance Criteria Addressed**: AC-25
- **Test Results**: 18/18 edge case tests passed, 9 fixture networks verified, DAG simulation cross-validated

## [x] Task 23: M9-C¹拐点防护与数值稳定性
- **Priority**: high
- **Depends On**: Task 8
- **Status**: ✅ 已完成
- **Description**:
  - avoid_c1_discontinuity helper函数：将|x-kink|<margin*h的点推离拐点margin*h距离
  - 支持多拐点、幂等安全
  - CI静态检查脚本check_c1_kink_protection.py：正则检测ELU(α≠1)/PReLU/LeakyReLU(negative_slope>0)三类C¹不连续激活
  - 正则修复：`(?<![a-zA-Z0-9])`替代`\b`以支持下划线前缀辅助函数
  - 检测要求：数值梯度测试必须调用avoid_c1_discontinuity或添加`# c1-kink-ok`豁免注释
  - ELU拐点稳定性专项测试test_elu_kink_stability.py
  - Sigmoid饱和精度修复：subnormal处理（sigmoid(-88)≈6e-39非精确0、x≥17精确1.0）、NaN/Inf防护
  - 饱和区精确相等断言模式（float32-saturation-exact-equality）
  - ULP饱和阈值表：tanh|x|≥9.010914、sigmoid正饱和x≥16.635532、负饱和x≤-88.72284
  - piecewise-c1-kink-numerical-gradient模式沉淀：类型A(C¹连续C²不连续)rtol=5e-3，类型B(C¹不连续)必须推离拐点
- **Acceptance Criteria Addressed**: AC-27, NFR-11
- **Deliverables**: avoid_c1_discontinuity helper, check_c1_kink_protection.py, test_elu_kink_stability.py

## [x] Task 24: M9-GitHub Actions CI流水线
- **Priority**: high
- **Depends On**: Task 12, Task 23
- **Status**: ✅ 已完成
- **Description**:
  - 三平台矩阵：Linux(Ubuntu)/macOS/Windows
  - 双构建类型：Release/Debug
  - C++测试(Linux only)：ctest执行
  - Python全量测试：pytest tests/python/
  - 激活Backward专项测试：test_activation_backward.py
  - [ACTIVATION-PERF]日志验证（Debug build only）：验证ReLU/TanH/ELU/Sigmoid的diff_in/diff_out/time结构化输出
  - wheel构建与上传（Linux Release）
  - ruff lint + format检查
  - C¹拐点防护静态检查
  - InsertSplits DAG仿真交叉验证（built-in cases + real-network fixtures，零依赖运行在build前）
  - ccache编译加速（Linux/macOS）
  - CAFFE_USE_BLAS=OFF（纯C++ fallback，避免OpenBLAS依赖）
  - KMP_DUPLICATE_LIB_OK=TRUE（Windows OpenMP兼容）
- **Acceptance Criteria Addressed**: AC-28, NFR-10
- **Deliverables**: .github/workflows/ci.yml

## [x] Task 25: M9-测试基础设施性能优化
- **Priority**: medium
- **Depends On**: Task 11
- **Status**: ✅ 已完成（P3-B 134s→8.27s，16.2x加速）
- **Description**:
  - **分层GC策略**：quick/full/off三档，默认quick仅gc.collect(0)，避免3轮full gen0+1+2（~150ms/次）
  - **perf_trace优化**：采样间隔调整、RSS内存采样线程可选、减少GC调用频率
  - **CSV缓冲**：20行批量flush，减少I/O syscall
  - **C++日志抑制**：Release模式下InsertSplits等冗余日志抑制
  - **性能根因发现**：微基准测试揭示瓶颈不在业务逻辑（Net创建0.5ms），而在观测基础设施（GC/线程/IO）
  - 最佳实践文档test-infra-performance-optimization.md入知识库
- **Acceptance Criteria Addressed**: AC-31, NFR-1
- **Deliverables**: 优化后的conftest.py、test-infra-performance-optimization.md
- **Performance Results**: P3-B test suite 134s → 8.27s (16.2x speedup)

## [x] Task 26: M9-SetShapeOnly API与perf_monitor
- **Priority**: medium
- **Depends On**: Task 3
- **Status**: ✅ 已完成
- **Description**:
  - SetShapeOnly API：零拷贝形状修改（不重新分配内存），适用于shape已知不变仅调整元数据的场景
  - test_ffi_set_shape_only.py：SetShapeOnly测试
  - test_phase3_set_shape_only.py：Phase 3 SetShapeOnly验证
  - perf_monitor.hpp：性能监控基础设施
  - SETSHAPEONLY_API_DESIGN.md设计文档
- **Acceptance Criteria Addressed**: AC-29, AC-30
- **Deliverables**: SetShapeOnly API, perf_monitor.hpp, SETSHAPEONLY_API_DESIGN.md

## [x] Task 27: M9-numpy参考实现
- **Priority**: medium
- **Depends On**: Task 6, Task 7
- **Status**: ✅ 已完成
- **Description**:
  - _numpy_bn_reference.py：BatchNorm numpy参考实现（用于Backward梯度验证）
  - _numpy_rnn_reference.py：RNN/LSTM numpy前向参考实现（rnn_forward/lstm_forward/权重打包解包工具函数），8个自测试通过
  - caffe_test_helpers.py：测试辅助函数
- **Acceptance Criteria Addressed**: AC-26
- **Deliverables**: _numpy_bn_reference.py, _numpy_rnn_reference.py, caffe_test_helpers.py

## [x] Task 28: M9-Backward梯度完整验证（P3核心）
- **Priority**: high
- **Depends On**: Task 5, Task 6, Task 7, Task 8, Task 8b, Task 23, Task 27
- **Status**: ✅ 已完成（2026-08-04，19类层892个测试通过）
- **Description**:
  - P0已完成：激活函数(ReLU/Sigmoid/TanH/PReLU/ELU)梯度+C¹拐点防护、InnerProduct梯度解析验证(23测试)、BatchNorm梯度测试、SoftmaxWithLoss梯度测试
  - P0已完成：Convolution Backward、Pooling Backward（数值验证完成）
  - P1已完成：Split Backward、Slice/Crop/Deconv/LRN/Scale/Bias Backward（完整验证）
  - P2已完成：Concat/Eltwise/Reshape/Flatten Backward（完整验证）
  - numpy参考对比：中心有限差分+解析梯度验证
  - [ACTIVATION-PERF]日志结构验证
  - 31个失败测试修复（28个Blob对象协议 + 3个构建缺宏）
- **Acceptance Criteria Addressed**: AC-26
- **Deliverables**: test_*_backward.py系列测试文件（19个）
- **Test Results**: 19类层Backward全部验证通过，892个测试，0失败

## [x] Task 29: M9-端到端训练最小可用
- **Priority**: high
- **Depends On**: Task 28
- **Status**: ✅ 已完成（2026-08-04，LeNet on MNIST test acc 97.95%）
- **Description**:
  - 简单SGD更新（权重data -= lr * diff）
  - LeNet/MNIST端到端训练验证（examples/lenet_mnist_train.py）
  - 训练精度目标：>95% → 实测97.95%
  - 可选：Solver框架基础接口（P4规划）
- **Acceptance Criteria Addressed**: AC-33, AC-16
- **Test Results**: LeNet on MNIST test acc 97.95%，loss 2.32→0.04（-98.3%），无NaN

## [ ] Task 30: RNN/LSTM层实现（远期）
- **Priority**: low
- **Depends On**: Task 28
- **Status**: ⬜ 待开始
- **Description**:
  - caffe.proto扩展RecurrentParameter
  - RecurrentLayer实现（~1350行C++，参考caffe-slim/caffe）
  - LSTMUnit/LSTMLayer
  - RNNLayer
  - numpy参考实现已就绪（_numpy_rnn_reference.py）
  - 工作量预估：15-20工作日（原估7-12天严重低估）
  - 建议：若仅需前向推理，短期可用numpy纯Python方案
- **Acceptance Criteria Addressed**: AC-RNN

## [ ] Task 31: P4-性能优化（BLAS后端/多线程/COW推广）
- **Priority**: medium
- **Depends On**: Task 29
- **Status**: ⬜ 待开始
- **Description**:
  - BLAS后端：复用/接通OpenBLAS路径，完成Conv/InnerProduct gemm性能基准对比
  - 多线程：OpenMP并行化卷积/池化/全连接等计算密集层
  - COW推广：将COW零拷贝共享推广到更多层与场景（如Split/Concat后端）
  - 性能基准体系：建立P0/P1/P2分层benchmark，量化优化收益
- **Acceptance Criteria Addressed**: NFR-1, AC-13

## [ ] Task 32: P4-能力扩展（更多激活/归一化/损失层）
- **Priority**: medium
- **Depends On**: Task 29
- **Status**: ⬜ 待开始
- **Description**:
  - 更多激活层：LeakyReLU/Softplus/Softsign/绝对值等
  - 更多归一化层：L2Norm/InstanceNorm等
  - 更多损失层：MarginRanking/Hinge等
  - 训练模式Dropout：训练/测试双模式行为
  - 目标：向40+层（v0.2.0 Beta）演进
- **Acceptance Criteria Addressed**: AC-7d

## [ ] Task 33: P4-训练工程化（训练API封装/模型序列化/应用示例）
- **Priority**: medium
- **Depends On**: Task 29
- **Status**: ⬜ 待开始
- **Description**:
  - Solver优化器框架：SGD/Adam等，封装训练循环
  - 训练API封装：fit/step/learning rate调度
  - 模型序列化：训练后权重保存/加载（caffemodel格式）
  - 应用示例：ImageNet/v1模型微调、分类器训练示例
  - 文档完善：训练指南、API参考
- **Acceptance Criteria Addressed**: AC-33, AC-16

---

## 任务依赖关系图

```
Task 1 (骨架/构建) ─→ Task 2 (Proto) ─┐
                  └→ Task 3 (核心类型/双类+COW✅) ─→ Task 4 (Layer基类✅) ─→ Task 5 (Net+InsertSplits+Backward✅)
                                              │                     │
                                              ├→ Task 6 (第一批Layer✅) ─┐
                                              │                           │
                                              └→ Task 15 (BLAS✅) ─→ Task 7 (第二批Layer✅)
                                                               │
                                              Task 8 (第三批Layer✅) ──┐
                                              Task 8b (第四批扩展Layer✅)─┘
                                                                 │
                           Task 9 (Python绑定+COW✅) ←─┘
                              │
                              ├→ Task 10 (caffemodel加载✅)
                              ├→ Task 11 (Python测试+性能优化✅: 561/562 passed, 16.2x加速)
                              ├→ Task 14 (文档✅: 20+份)
                              ├→ Task 16 (find_package迁移✅)
                              ├→ Task 17 (COW机制✅: v1.1.0) ─→ Task 17b (ASan⬜)
                              │
                              └→ Task 12 (C++测试✅: 8个测试文件) ─→ Task 18 (M6-独立迁移✅)
                                 │
                                 └────────────────────────────→ Task 19 (Docker环境✅)
                                                                          │
                                                          Task 20 (工程化工具✅) ←─┘
                                                                 │
                                                                 └→ Task 21 (测试增强+Docker验证✅)
                                                                          │
                                                                          ├→ Task 22 (M8-InsertSplits✅: v1.2.0, 18边界测试)
                                                                          │
                              Task 13 (Conda配置✅)                        │
                                                                          ├→ Task 23 (M9-C¹拐点防护✅)
                                                                          ├→ Task 24 (M9-CI流水线✅: 三平台)
                                                                          ├→ Task 25 (M9-测试性能优化✅: 16.2x)
                                                                          ├→ Task 26 (M9-SetShapeOnly/perf_monitor✅)
                                                                          ├→ Task 27 (M9-numpy参考实现✅)
                                                                          │
                                                                          └→ Task 28 (M9-Backward验证✅: 19类层892测试)
                                                                                   │
                                                                                   └→ Task 29 (端到端训练✅: LeNet 97.95%) ─→ Task 30 (RNN/LSTM⬜)
                                                                                              │
                                                                                              └→ Task 31 (P4性能优化⬜)
                                                                                              └→ Task 32 (P4能力扩展⬜)
                                                                                              └→ Task 33 (P4训练工程化⬜)
```

## 里程碑

| 里程碑 | 包含任务 | 状态 |
|--------|---------|------|
| **M1: 核心骨架可运行** | Task 1-6, 9, 11, 14 | ✅ 已完成 |
| **M2: BLAS+卷积池化** | Task 15, 7 | ✅ 已完成 |
| **M3: 完整推理能力** | Task 8, 10 | ✅ 已完成（20层，101 passed） |
| **M4: TVM FFI最佳实践** | Task 3/5/9/16（双类+零拷贝+@register_object+find_package）+日志+Doxygen | ✅ 已完成 |
| **M5: 生产就绪基础** | Task 12, 13 | ✅ C++测试已完成；Conda配置已完成；ASan待执行 |
| **M6: 独立项目+Docker环境** | Task 18, 19, 20, 21 | ✅ 已完成（vendor→libs迁移、Docker、工具链、验证） |
| **M7: COW零拷贝共享** | Task 17, 9(COW部分) | ✅ 已完成（v1.1.0：COW机制+内存追踪+21测试+562测试通过） |
| **M8: 图变换+层扩展** | Task 8b, 22, 23(部分) | ✅ 已完成（v1.2.0：InsertSplits+25层+Transformer+精度修复） |
| **M9: P3训练支持** | Task 23(C¹防护), 24(CI), 25(性能优化), 26(SetShapeOnly), 27(numpy参考), 28(Backward验证), 29(训练) | ✅ 已完成：Backward 19类层892测试、LeNet/MNIST训练97.95%、CI三平台、P3-B/C/D/E四阶段闭环 |
| **P4: 优化/扩展** | Task 31(性能优化), 32(能力扩展), 33(训练工程化) | ⬜ 规划中：BLAS后端/多线程/COW推广、更多层、训练API封装/模型序列化 |
