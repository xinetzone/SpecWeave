# Caffe-FFI 验证检查清单

> **更新日期**: 2026-08-03
> **验证状态**: 🔄 M1-M8全部完成，M9(P3 Backward训练支持)进行中
> **版本进展**:
>   - v0.1.0 (M1-M6): 20层、Docker、独立项目 — ✅ 完成
>   - v1.1.0 (M7): COW零拷贝共享、内存追踪、562测试 — ✅ 完成
>   - v1.2.0 (M8): InsertSplits图变换、25层、P3-C Transformer — ✅ 完成
>   - M9 (P3): Backward 16层实现、CI三平台、C¹拐点防护、测试16.2x优化 — 🔄 进行中
> **测试结果**:
>   - Docker Linux Python 3.14.6: 561/562 tests passed (1 skipped), 0 failures
>   - GitHub Actions CI: Linux/macOS/Windows三平台验证通过
>   - C++测试: 8个测试文件覆盖Blob/Net/Neuron/InsertSplits/Deconv/ZeroCopy/ObjectPtr/符号导出
> **性能验证**:
>   - 零拷贝恒定~4µs访问，10M元素加速3749×
>   - COW共享O(1)
>   - P3-B测试套件134s→8.27s（16.2x加速）

## 构建系统验证
- [x] CMakeLists.txt 存在且正确配置 C++17 标准
- [x] CMake原子化为9个模块化.cmake文件（CompilerConfig/Dependencies/DetectBLAS/DetectOpenBLAS/Install/Options/ProtoCompile/TargetBuild/Tests/WindowsDllCopy）
- [x] tvm-ffi 支持find_package(tvm_ffi CONFIG REQUIRED)（CAFFE_FFI_TVM_FFI_DIR选项指定本地路径）
- [x] CMakeLists.txt调用tvm_ffi_configure_target(_caffe_ffi)
- [x] 禁止使用Find<Name>.cmake命名（使用Detect<Name>.cmake避免与CMake内置冲突）
- [x] Protobuf >= 7.0.0 正确查找（find_package(Protobuf CONFIG REQUIRED)，版本检查）
- [x] BLAS 库条件编译（DetectBLAS.cmake/DetectOpenBLAS.cmake，CAFFE_USE_BLAS宏；纯C++ fallback）
- [x] CMake 配置无错误无警告
- [x] Ninja/GCC 14/Clang/MSVC Release编译成功
- [x] pyproject.toml 配置 scikit-build-core 构建后端
- [x] pyproject.toml 声明 requires-python >= 3.14
- [x] pyproject.toml 声明 protobuf >= 7.0.0 和 numpy >= 2.3 依赖
- [x] pyproject.toml 声明 apache-tvm-ffi > 0.1.12 依赖
- [x] pyproject.toml 声明 pytest 为运行时依赖
- [x] Windows 下自动复制 protobuf/absl/utf8_range/tvm_ffi DLL 到包目录（WindowsDllCopy.cmake 8个精细复制函数）
- [x] CMakePresets.json 存在（default/debug/developer预设）
- [x] scripts/dev.sh(Linux/WSL) 和 scripts/dev.ps1(Windows) 开发脚本存在
- [x] conda.recipe/ 打包配置存在

## TVM FFI 双类模式+COW集成验证
- [x] BlobObj 类继承自 tvm::ffi::Object，使用 TVM_FFI_DECLARE_OBJECT_INFO_FINAL
- [x] Blob 类继承自 tvm::ffi::ObjectRef，使用 TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE
- [x] Blob 通过 tvm::ffi::make_object 创建实例
- [x] Blob 通过 ObjectPtr<Blob> 管理生命周期
- [x] Blob 使用 tvm::ffi::Tensor (DLPack) 存储 data/diff 数据
- [x] Blob.data_tensor()/diff_tensor() 直接返回Tensor
- [x] **Blob.COW零拷贝共享**: ShareData()/ShareDiff() O(1)共享
- [x] **Blob.COW自动克隆**: mutable_data_tensor()/mutable_diff_tensor()写时自动克隆
- [x] **Blob.COW状态查询**: IsDataShared()/IsDiffShared()/DataRefCount()/DiffRefCount()
- [x] **Blob.COW显式断连**: UnshareData()/UnshareDiff()
- [x] **Blob.COW标志追踪**: data_shared_/diff_shared_精确追踪（不依赖refcount）
- [x] **Blob.SetShapeOnly**: 零拷贝形状修改API（不重新分配内存）
- [x] Shape 使用 tvm::ffi::Shape/ShapeView 实现
- [x] LayerObj 类继承自 tvm::ffi::Object，使用 TVM_FFI_DECLARE_OBJECT_INFO（非final，_type_child_slots=25）
- [x] Layer 类继承自 tvm::ffi::ObjectRef，使用 TVM_FFI_DEFINE_OBJECT_REF_METHODS
- [x] Layer 注册表使用 LayerRegistry + REGISTER_LAYER_CLASS 宏 + TVM_FFI_STATIC_INIT_BLOCK
- [x] Layer NVI生命周期包含Forward+Backward双阶段
- [x] NetObj 类继承自 tvm::ffi::Object，使用 TVM_FFI_DECLARE_OBJECT_INFO_FINAL
- [x] Net 类继承自 tvm::ffi::ObjectRef，使用 TVM_FFI_DEFINE_OBJECT_REF_METHODS_NOTNULLABLE
- [x] Net 使用 Array<Layer> 存储 layers_，Array<Blob> 存储 blobs_
- [x] Net 使用 Map<String, int64_t> 存储名称索引
- [x] Net Forward 返回 Map<String, Blob>
- [x] **Net Backward**: 逆序执行Backward_cpu传播梯度
- [x] **Net InsertSplits**: 自动图变换Pass，多消费方Blob自动插入Split层
- [x] 内存分配使用 tvm::ffi::Tensor::FromNDAlloc + 自定义 CPUMemAlloc
- [x] 使用 TVM_FFI_DLL_EXPORT_TYPED_FUNC 导出全局函数（含COW/内存/Backward相关）
- [x] `using namespace tvm::ffi` 仅在 namespace caffe_ffi 内部使用
- [x] 反射系统完整注册
- [x] Windows DLL边界问题修复：LayerRegistry::Registry()唯一实现移至layer_factory.cpp
- [x] Protobuf跨DLL解析隔离：ReadNetParamsFromTextString/File在DLL内实现
- [x] Python MRO反射查找修复：_native_method()遍历__mro__查找基类方法
- [x] _tensor_to_numpy引用循环修复：_blob_ref挂载到numpy ctypes数组(arr.base.obj)

## COW零拷贝共享验证（M7）
- [x] ShareData()/ShareDiff() 实现O(1)张量共享（引用计数+1）
- [x] UnshareData()/UnshareDiff() 实现显式深拷贝断开共享
- [x] IsDataShared()/IsDiffShared() 正确返回 data_shared_ && use_count > 1
- [x] DataRefCount()/DiffRefCount() 对undefined/empty tensor返回0
- [x] mutable_data_tensor()/mutable_diff_tensor() 在共享时自动COW克隆
- [x] mutable_*() 返回numpy数组（ctypes零拷贝），支持arr[i,j]=val语法
- [x] Reshape() 不无条件清除共享标记——仅当shape实际变化时清除
- [x] CAFFE_FFI_ENABLE_COW 环境变量运行时控制COW启用
- [x] CAFFE_FFI_ENABLE_COW_PHASE3 环境变量控制Phase 3 COW特性
- [x] in-place ReLU + COW 场景正确工作（Reshape不清空标记）
- [x] caffe_ffi.tools.memory 内存追踪工具存在（BlobRef/tracked_blob/blob_snapshot/mem_check）
- [x] test_create_destroy_loop_no_leak: 500次create/fill/destroy零泄漏
- [x] test_reshape_loop_no_leak: 500次reshape循环零泄漏
- [x] 21个COW测试用例全部通过（API/拓扑/snapshot/refcount/forward场景）
- [x] SplitLayer Forward 使用ShareData()零拷贝共享

## Proto 集成验证
- [x] proto/caffe/proto/caffe.proto 包含25个Layer所需的核心消息类型（含Crop/Deconv/LRN/Slice/Split参数）
- [x] CMake 中 protoc 自定义命令正确生成 .pb.cc/.pb.h
- [x] C++ 代码可正常 include 生成的 caffe.pb.h
- [x] CMake 中 protoc 自动生成 caffe_pb2.py 并复制到 python/caffe_ffi/
- [x] Python protobuf 7.x 可正常解析 prototxt 文本
- [x] Python protobuf 7.x 可正常解析 caffemodel 二进制
- [x] 预生成的 caffe_pb2.py 提交仓库

## 核心功能验证
- [x] Blob 支持 Reshape(Shape) 形状调整（含负维度ICHECK校验）
- [x] Blob 支持 SetShapeOnly() 零拷贝形状调整
- [x] Blob data/diff 双缓冲正常工作（独立 Tensor）
- [x] Blob FromProto/ToProto 正确序列化/反序列化
- [x] Blob Update() 正确执行data -= diff
- [x] Blob ShareData()/ShareDiff()/Unshare()/IsShared()/RefCount() COW API完整
- [x] Layer SetUp() 正确执行 CheckBlobCounts→LayerSetUp→Reshape→SetLossWeights
- [x] Layer Forward() 执行 Reshape→Forward_cpu→loss 计算
- [x] Layer Backward() 执行 Backward_cpu 梯度计算（16个Layer已实现）
- [x] Layer 工厂可通过类型名创建25种Layer实例
- [x] Layer.name() 方法可用
- [x] Net 从 NetParameter 正确初始化（Init 方法）
- [x] Net 从 prototxt 文件正确初始化
- [x] Net 正确构建 DAG（AppendTop/AppendBottom）
- [x] Net InsertSplits 自动插入Split层处理多消费方
- [x] Net Forward() 按顺序执行所有 Layer
- [x] Net Backward() 逆序执行所有 Layer 的 Backward
- [x] Net blob_by_name/layer_by_name 正确查找
- [x] Net blobs_array/layers_array/input_blobs_array/output_blobs_array 返回 Array
- [x] Net CopyTrainedLayersFrom 从 caffemodel 二进制文件加载预训练权重
- [x] Forward未知输入blob名抛出异常并列出可用blob名
- [x] Backward未知输出blob名抛出异常
- [x] total_allocated_bytes()/live_blob_count()内存计数器正确工作
- [x] perf_monitor 性能监控基础设施存在

## InsertSplits 图变换验证（M8）
- [x] InsertSplits Pass 正确插入Split层处理多消费方Blob
- [x] Split层命名与原生Caffe完全对齐（named after last producer）
- [x] 零消费死端Blob处理正确
- [x] 单消费Blob不插入Split
- [x] in-place ReLU多消费场景正确（split named after last producer）
- [x] loss_weight作为隐式消费方处理正确
- [x] 级联拆分（fan-out after fan-out）正确
- [x] 幂等性：显式Split不重复插入
- [x] in-place + split后Forward正确性
- [x] 多外部输入排序正确（按输入声明顺序而非反向消费顺序）
- [x] 线性链零拆分正确
- [x] 双重in-place链正确
- [x] 混合Input层+param.input()外部输入正确
- [x] Split→Concat→Split Inception式嵌套拓扑正确
- [x] 多独立Split位置验证正确
- [x] 空网络（零层）鲁棒性
- [x] Input层3+消费者正确
- [x] loss_weight+多下游消费者正确
- [x] 未知bottom blob引用错误路径正确
- [x] viz_insert_splits.py DAG仿真+可视化+--verify交叉验证
- [x] 9个真实网络拓扑fixture验证通过（mlp_basic/mlp_branch/triple_inplace/cascading_splits/deep_supervision/multi_head/multi_input_splits/inception_like/resnet_skip）
- [x] Pass 2b详细日志（外部输入split移动前后层顺序）
- [x] INSERT_SPLITS_GRAPH_TRANSFORM.md算法文档存在

## Layer 实现验证（全部25个）

### 第一批（5个，基础）
- [x] InputLayer 正确设置输入 Blob 形状（支持多 top、多 shape）
- [x] ReLULayer 正确计算 max(0,x) 和 negative_slope，支持in-place，**Backward实现+C¹拐点防护**
- [x] InnerProductLayer 矩阵乘法正确（bias_term/transpose/axis），**Backward梯度解析验证通过(23个测试)**
- [x] SoftmaxLayer 输出概率和为1，全零输入→均匀分布
- [x] FlattenLayer 正确展平张量（axis/end_axis 参数）

### 第二批（7个，计算密集）
- [x] ConvolutionLayer im2col + gemm 实现，**Forward+Backward代码已有（Backward待数值验证）**
- [x] PoolingLayer 最大池化结果正确（MAX + global_pooling + CEIL/FLOOR），**Forward+Backward代码已有（Backward待数值验证）**
- [x] PoolingLayer 平均池化结果正确（AVE + pad排除计数），**Forward+Backward代码已有**
- [x] BatchNormLayer 归一化计算正确，**Backward实现+测试**
- [x] ScaleLayer 缩放平移正确，**Backward代码已有（待完整验证）**
- [x] BiasLayer 偏置加法正确（广播机制），**Backward代码已有（待完整验证）**
- [x] AccuracyLayer top-k 精度计算正确（ignore_label支持）
- [x] SoftmaxWithLossLayer 推理模式前向兼容，**Backward测试完成**

### 第三批（8个，激活/操作）
- [x] SigmoidLayer 输出在 (0,1) 范围，**Backward+C¹饱和精度修复(subnormal处理)**
- [x] TanHLayer 输出在 (-1,1) 范围，**Backward实现**
- [x] PReLULayer 参数化 ReLU，**Backward+C¹拐点防护**
- [x] ELULayer 指数线性单元（alpha 参数），**Backward+C¹拐点防护+稳定性专项测试**
- [x] DropoutLayer 推理模式恒等映射
- [x] ConcatLayer 沿指定维度正确拼接
- [x] EltwiseLayer 逐元素加/乘/最大操作正确
- [x] ReshapeLayer 正确变换形状（dim=0复制/dim=-1推断，不改变数据）

### 第四批（5个，扩展层）
- [x] CropLayer 裁剪实现，**Forward+Backward代码已有**
- [x] DeconvolutionLayer 反卷积实现，**Forward+Backward，C++测试覆盖**
- [x] LRNLayer 局部响应归一化，**Forward+Backward代码已有**
- [x] SliceLayer 切片实现，**Forward+Backward代码已有**
- [x] SplitLayer 拆分实现，**Forward使用ShareData()零拷贝，Backward梯度累加**

### 激活函数Backward C¹拐点防护
- [x] avoid_c1_discontinuity helper函数：将|x-kink|<margin*h的点推离拐点
- [x] helper支持多拐点、幂等安全
- [x] LeakyReLU(negative_slope>0)使用helper或`# c1-kink-ok`豁免
- [x] PReLU使用helper或豁免
- [x] ELU(α≠1)使用helper或豁免
- [x] check_c1_kink_protection.py CI静态检查脚本存在
- [x] 正则`(?<![a-zA-Z0-9])`支持下划线前缀辅助函数
- [x] test_elu_kink_stability.py ELU拐点稳定性专项测试
- [x] 饱和区精确相等断言模式（float32-saturation-exact-equality）
- [x] ULP饱和阈值表：tanh|x|≥9.010914、sigmoid正饱和x≥16.635532、负饱和x≤-88.72284
- [x] piecewise-c1-kink-numerical-gradient模式：类型A(C¹连续C²不连续)rtol=5e-3，类型B(C¹不连续)必须推离拐点

### 所有Layer日志验证
- [x] 全部25个Layer均添加三层日志
- [x] 激活函数Backward添加[ACTIVATION-PERF]结构化日志（diff_in/diff_out/time）
- [x] 核心文件blob.cpp/net.cpp/layer.cpp日志完整

### MLP/Transformer集成测试
- [x] MLP（Input→FC→ReLU→FC→Softmax）端到端通过
- [x] C++输出与numpy手动计算完全一致（误差<1e-5）
- [x] Transformer位置编码测试通过
- [x] 缩放点积注意力测试通过
- [x] 多头投影测试通过
- [x] Transformer Encoder Block前向正确性通过（13个测试）

## Python 绑定验证
- [x] Python 中 import caffe_ffi 无错误
- [x] _caffe_ffi 共享库正确加载
- [x] caffe_ffi.Net/Blob/Layer 使用@register_object（@_reg）装饰器定义
- [x] 无_add_python_wrappers monkey patch代码
- [x] net.forward() 执行前向推理并返回输出字典
- [x] **net.backward()** 执行反向传播（接受输出梯度字典）
- [x] net.forward(input_dict) 支持通过 numpy 数组设置输入
- [x] Blob 数据可通过 numpy 数组零拷贝访问（DLPack）
- [x] Blob COW感知mutable_data()/mutable_diff()写时自动克隆
- [x] Blob.shape/ndim/size 属性
- [x] Blob.from_numpy(arr)/Blob.to_numpy() numpy 互操作
- [x] Blob.data/Blob.diff 属性读写（零拷贝）
- [x] Blob.fill(value)/Blob.zero()/Blob.copy_from(other) 便捷方法
- [x] **Blob ShareData/ShareDiff/Unshare/IsShared/RefCount COW API在Python层可用**
- [x] prototxt/caffemodel 通过io模块加载
- [x] net.copy_from(trained_filename) 加载 caffemodel 权重
- [x] Classifier 高级分类器接口
- [x] _native_method() 辅助函数正确访问C++注册方法（MRO遍历）
- [x] _is_native 只读property自动检测C++扩展可用性
- [x] Python-only fallback模式正常工作
- [x] caffe_ffi.tools.memory 内存追踪工具可用

## 三层日志+Backward性能日志验证
- [x] C++核心层（log.hpp）：RAII Logger类+编译期门控+6级日志+组件标签
- [x] FFI桥接层：SetLogLevel/GetLogLevel全局函数导出
- [x] Python配置层：统一日志级别控制
- [x] 默认日志级别(WARN)无冗余输出
- [x] **[ACTIVATION-PERF]日志**：Backward时输出diff_in/diff_out/time结构化信息
- [x] Debug build [ACTIVATION-PERF]日志CI验证（ReLU/TanH/ELU/Sigmoid）

## 错误处理验证
- [x] 无效shape（负维度）抛出TVM_FFI_ICHECK异常，包含Blob ID
- [x] 不存在的blob名称抛出明确异常，列出可用blob名
- [x] Layer错误信息包含层名和层类型
- [x] shape mismatch包含详细诊断信息（维度对比）
- [x] 文件打开失败抛出包含文件路径的IO错误
- [x] prototxt解析失败抛出明确错误信息
- [x] Python端能正确捕获C++抛出的异常

## GitHub Actions CI验证（M9）
- [x] .github/workflows/ci.yml 存在
- [x] 三平台矩阵：Linux(Ubuntu)/macOS/Windows
- [x] 双构建类型：Release/Debug
- [x] Python版本：3.14
- [x] C++测试（Linux only）：cmake配置+build+ctest
- [x] Python全量测试：pytest tests/python/
- [x] 激活Backward专项测试：test_activation_backward.py
- [x] [ACTIVATION-PERF]日志验证（Debug build only）
- [x] wheel构建与上传（Linux Release）
- [x] ruff lint检查通过
- [x] ruff format检查通过
- [x] C¹拐点防护静态检查：check_c1_kink_protection.py
- [x] InsertSplits DAG仿真交叉验证（built-in cases，零依赖运行在build前）
- [x] InsertSplits DAG仿真交叉验证（real-network fixtures）
- [x] ccache编译加速（Linux/macOS）
- [x] CAFFE_USE_BLAS=OFF（纯C++ fallback，避免CI OpenBLAS依赖）
- [x] KMP_DUPLICATE_LIB_OK=TRUE（Windows OpenMP兼容）
- [x] concurrency配置取消同PR/branch的in-flight runs
- [x] fail-fast: false 允许其他平台继续测试

## 测试验证
- [x] Python pytest 框架配置（conftest.py、fixtures、markers）
- [x] **分层GC策略**：quick/full/off三档，默认quick仅gc.collect(0)（性能优化）
- [x] conftest.py内存泄漏检测（GC后检查内存回到基线）
- [x] Python测试文件数量：30+个测试文件
- [x] test_blob.py：Blob单元测试
- [x] test_layers.py：Layer Forward单元测试
- [x] test_net.py：Net单元测试
- [x] test_cow.py：COW机制21个测试
- [x] test_insert_splits.py：InsertSplits 18个边界测试
- [x] test_inner_product_backward.py：InnerProduct Backward 23个测试（解析梯度+数值检查）
- [x] test_batch_norm_backward.py：BatchNorm Backward测试
- [x] test_activation_backward.py：激活函数Backward测试（C¹拐点防护）
- [x] test_elu_kink_stability.py：ELU拐点稳定性专项测试
- [x] test_complex_topologies.py：复杂拓扑测试
- [x] test_split_topologies.py：Split拓扑测试
- [x] test_p3a_conv_pool_bn.py：P3-A Conv/Pool/BN测试
- [x] test_p3b_eltwise_scale.py：P3-B Eltwise/Scale测试
- [x] test_p3c_activations_ip.py：P3-C 激活/InnerProduct测试
- [x] test_p3c_transformer.py：P3-C Transformer测试（13个测试）
- [x] test_p3d_slice_crop_deconv_lrn.py：P3-D Slice/Crop/Deconv/LRN测试
- [x] test_phase3_log_aggregation.py：Phase 3日志聚合测试
- [x] test_phase3_set_shape_only.py：Phase 3 SetShapeOnly测试
- [x] test_ffi_set_shape_only.py：SetShapeOnly API测试
- [x] test_extreme_boundaries.py：边界情况测试
- [x] test_extreme_inputs.py：极端输入测试
- [x] test_p2b_regression.py：P2-B回归测试
- [x] test_cow_regression.py：COW回归测试
- [x] test_split_concat_bench.py：Split/Concat性能测试
- [x] _numpy_bn_reference.py：BatchNorm numpy参考实现
- [x] _numpy_rnn_reference.py：RNN/LSTM numpy参考实现（8个自测试通过）
- [x] caffe_test_helpers.py：测试辅助函数
- [x] pytest Docker Linux结果：561/562 passed (1 skipped), 0 failures
- [x] C++ header-only轻量测试框架实现（test_harness.hpp）
- [x] C++测试核心宏实现：TEST/EXPECT_EQ/EXPECT_NE/EXPECT_TRUE/EXPECT_FALSE/EXPECT_NEAR
- [x] C++测试增强：高精度耗时统计+Per-suite汇总+Top 5 slowest报告
- [x] C++测试文件（8个）：
  - [x] test_blob.cpp：Blob基础测试
  - [x] test_blob_zerocopy.cpp：Blob零拷贝测试
  - [x] test_net.cpp：Net测试
  - [x] test_neuron_layers.cpp：神经元层测试
  - [x] test_insert_splits.cpp：InsertSplits测试
  - [x] test_deconv_layer.cpp：Deconv层测试
  - [x] test_objectptr_migration.cpp：ObjectPtr迁移测试
  - [x] test_symbol_export.cpp：符号导出测试
- [x] CMake配置caffe_ffi_tests可执行目标

## 测试基础设施性能优化验证（M9）
- [x] 分层GC策略实现（quick/full/off三档）
- [x] 默认quick模式仅执行gc.collect(0)（gen0 only）
- [x] perf_trace采样间隔调整，减少GC调用频率
- [x] RSS内存采样线程可选/按需启用
- [x] CSV输出20行批量flush，减少I/O syscall
- [x] C++ InsertSplits日志在Release模式下抑制
- [x] P3-B测试套件性能：134s → 8.27s（16.2x加速）
- [x] 微基准验证：Net创建0.5ms（非瓶颈），瓶颈在GC/线程/IO
- [x] test-infra-performance-optimization.md最佳实践文档入库

## 性能基准验证
- [x] 性能基准测试脚本可运行
- [x] data_tensor零拷贝访问恒定~4µs（不随张量大小增长）
- [x] 10M float32元素零拷贝比拷贝快**3749×**
- [x] COW ShareData/ShareDiff O(1)共享
- [x] Blob空构造~0.08ms（O(1)）
- [x] MLP Forward (784→256→10, bs=1) avg 0.50ms
- [x] 零拷贝内存共享验证通过（指针一致性+写后读验证）
- [x] 内存管理计数器精确，GC后内存回到基线
- [x] P3-B测试16.2x加速验证
- [ ] BLAS路径性能基准对比（需完整BLAS环境）

## BLAS 验证
- [x] math_utils.hpp 中 caffe_cpu_gemm 使用条件编译
- [x] math_utils.hpp 中 caffe_cpu_gemv 使用条件编译
- [x] caffe_axpy/caffe_scal/caffe_cpu_axpby 等辅助函数已实现
- [x] ConvolutionLayer im2col/col2im 已实现
- [x] ConvolutionLayer Forward 使用 gemm（纯C++ fallback可用）
- [x] 纯C++ fallback路径MSVC/GCC/Clang编译通过
- [x] DetectBLAS.cmake/DetectOpenBLAS.cmake 自动从conda环境检测
- [ ] InnerProductLayer/ConvLayer BLAS gemm性能验证（待BLAS环境）

## Conda 环境验证
- [x] environment.yml 存在
- [x] environment.yml 指定 Python>=3.14
- [x] environment.yml 包含 cmake>=3.26、ninja>=1.13、cxx-compiler
- [x] environment.yml 包含 libprotobuf>=7.0.0 和 protobuf>=7.0.0
- [x] environment.yml 包含 libopenblas（BLAS库）
- [x] environment.yml 包含 pytest>=8.0、ruff linter
- [x] environment.yml pip段包含scikit-build-core、numpy>=2.3、apache-tvm-ffi>0.1.12
- [x] conda_build.bat 存在（Windows三阶段构建脚本）
- [x] conda_build.sh 存在（Linux/macOS三阶段构建脚本）
- [x] Docker环境作为黄金标准验证环境（GCC 14.3.0稳定版）

## 文档验证
- [x] README.md 存在且包含项目介绍、Docker快速开始、本地安装
- [x] README.md 包含Windows开发指南
- [x] README.md 包含构建失败L0→L1→L2分层排查法
- [x] README.md 包含Docker作为规范构建环境的方法论引用
- [x] 可运行示例代码（examples/create_and_run_mlp.py）
- [x] 性能基准示例
- [x] 核心公共API（Blob/Layer/Net）有Doxygen注释
- [x] docs/performance/：P0/P1/P2B/Phase2性能报告
- [x] docs/design/：COW设计、InsertSplits算法、SetShapeOnly API、零拷贝模式萃取
- [x] docs/plans/：激活性能监控规格、Backward日志计划、InsertSplits图变换
- [x] docs/retrospectives/：6份回溯报告（COW迁移、构建修复、SoftmaxLoss Backward、Split COW Phase3、零拷贝Phase1、内存日志）
- [x] docs/setup/：构建验证报告、跨机器构建设置、Protobuf兼容、WSL2设置
- [x] docs/summaries/：构建修复总结、产品简报、任务执行总结、团队分享
- [x] docs/testing/TESTING_GUIDELINES.md：测试指南（prototxt构建、浮点断言、反模式）
- [x] docs/checklists/：COW边界清单、零拷贝重构清单、零拷贝入门清单
- [x] test-infra-performance-optimization.md：测试基础设施性能优化最佳实践（知识库）
- [x] CHANGELOG.md 记录版本历史（v0.1.0/v1.1.0/v1.2.0）
- [x] 代码已按Conventional Commits规范原子提交

## 代码质量验证
- [x] C++ 代码使用 C++17 标准
- [x] GCC 14/Clang/MSVC Release编译零错误零新增警告
- [x] 跨平台编译支持（MSVC/GCC/Clang条件编译）
- [x] 目录结构清晰，Layer头文件和实现分离
- [x] 不依赖 Boost/GFlags/GLog（仅tvm-ffi+protobuf+absl）
- [x] CMake支持find_package(tvm_ffi CONFIG REQUIRED)
- [x] 使用TVM_FFI_ICHECK/THROW进行错误处理
- [x] 无commented-out死代码
- [x] Python绑定代码量大幅减少（消除monkey patch）
- [x] ruff lint通过（CI检查）
- [x] ruff format通过（CI检查）
- [x] 9个模块化CMake文件零代码重复
- [x] 临时文件必须放在.temp/目录（.gitignore忽略）

## M6: 独立项目萃取迁移验证（vendor→libs/caffe-ffi）
- [x] 完整迁移vendor/caffe/caffe-ffi到projects/xuanspace/libs/caffe-ffi
- [x] 项目结构为独立项目标准布局（对齐libs/npu-ffi）
- [x] CMake构建系统独立化：Dependencies.cmake默认find_package
- [x] 添加标准项目配置文件：CMakePresets.json、scripts/dev.sh/dev.ps1、conda.recipe/
- [x] pyproject.toml完善sdist配置、requires-python=">=3.14"
- [x] 创建项目AGENTS.md、.agents/README.md、.temp/.gitkeep
- [x] 修复.gitignore精确路径忽略
- [x] 创建LICENSE(BSD-2-Clause)
- [x] 创建CHANGELOG.md初始版本
- [x] README.md包含WSL开发指南、Docker环境说明

## M6: Docker开发环境验证（apps/caffe-ffi-jupyter）
- [x] apps/caffe-ffi-jupyter目录遵循apps区域规范
- [x] Dockerfile基于jupyter-ssh-base
- [x] Dockerfile双阶段构建：builder + runtime
- [x] builder阶段编译caffe-ffi（pip install --no-build-isolation）
- [x] runtime阶段仅复制conda环境，注册Jupyter内核，配置SSH
- [x] RPATH配置正确（三重共享库路径保障）
- [x] 保留SSH+Jupyter双服务配置
- [x] scripts/build.sh支持--cn国内镜像源
- [x] docker-compose.yml端口映射+volume+healthcheck
- [x] Docker环境规格：GCC 14.3.0/Python 3.14/CMake 4.4.1/Ninja 1.13.2/Protobuf 35.1/numpy 2.5.1

## M6: 工程化工具链验证
- [x] scripts/lib/logging.sh（Bash）统一结构化日志库
- [x] scripts/lib/logging.ps1（PowerShell）统一结构化日志库
- [x] 日志库支持INFO/WARN/ERROR/DEBUG四级日志
- [x] 日志库支持text/json双输出格式
- [x] scripts/wsl-deploy.sh WSL一键部署脚本
- [x] scripts/deploy.ps1 Windows PowerShell部署脚本
- [x] scripts/diagnose.sh/diagnose.ps1环境诊断脚本
- [x] WSL-DEPLOY-GUIDE.md部署指南

## numpy参考实现验证（M9）
- [x] _numpy_bn_reference.py：BatchNorm Forward/Backward numpy参考
- [x] _numpy_rnn_reference.py：RNN/LSTM numpy前向参考
- [x] rnn_forward/lstm_forward函数正确
- [x] 权重打包/解包工具函数存在
- [x] _numpy_rnn_reference.py 8个自测试通过
- [x] 可用于C++ Backward梯度数值对比验证

## Backward梯度验证进度（M9，P3核心，🔄进行中）
- [x] ReLU Backward梯度正确
- [x] Sigmoid Backward梯度正确（含饱和区处理）
- [x] TanH Backward梯度正确
- [x] PReLU Backward梯度正确（含C¹拐点防护）
- [x] ELU Backward梯度正确（含C¹拐点防护+稳定性测试）
- [x] InnerProduct Backward梯度正确（23个测试，解析梯度+中心有限差分验证）
- [x] BatchNorm Backward梯度正确（测试完成）
- [x] SoftmaxWithLoss Backward梯度正确（测试完成）
- [ ] Convolution Backward梯度数值验证（代码已有，需numpy参考对比）
- [ ] Pooling Backward梯度数值验证（代码已有，需numpy参考对比）
- [ ] Split Backward梯度完整验证
- [ ] Slice/Crop/Deconv/LRN Backward完整验证
- [ ] Scale/Bias Backward完整验证
- [ ] Concat/Eltwise/Reshape/Flatten Backward实现与验证
- [ ] Dropout/Accuracy/Input Backward（通常为恒等/零梯度）
- [ ] 端到端LeNet/MNIST训练>95%精度

## 待完成项
- [ ] ASan内存管理正式验证（Linux/GCC环境）
- [ ] BLAS路径性能基准对比
- [ ] Conv/Pooling Backward数值验证（P0）
- [ ] 端到端训练最小可用（SGD+LeNet/MNIST）
- [ ] RNN/LSTM层C++实现
- [ ] Solver优化器框架
