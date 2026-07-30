# R阶段 - 客观事实清单

> G1质量门：纯客观描述，无因果推断词

## 时间线维度

**F01**: Phase 1零拷贝优化工作在2026年7月31日前完成开发与验证。

**F02**: 会话开始时用户提出三项任务：运行Windows一键回归测试脚本、查看P2-B性能日志CSV、规划Phase 2 COW优化方案草稿。

**F03**: C++单元测试文件test_blob_zerocopy.cpp被创建用于验证零拷贝功能。

**F04**: Phase 2 COW设计草稿文档SPLIT_COW_PHASE2_DESIGN_DRAFT.md已完成，包含9个章节共405行。

## 文件变更维度

**F05**: [blob.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/blob.hpp#L126-L129) 新增4个方法声明：`ShareData(const Blob* other)`、`ShareDiff(const Blob* other)`、`SharesDataWith(const Blob* other) const`、`SharesDiffWith(const Blob* other) const`。

**F06**: [blob.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/blob.cpp#L143-L170) 实现ShareData()方法，包含CAFFE_FFI_CHECK_TYPE参数校验和CAFFE_FFI_MEM_LOG日志输出，日志标签为`[ZEROCOPY]`。

**F07**: [blob.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/blob.cpp#L143-L170) ShareData()方法核心实现为`data_tensor_ = other->data_tensor_;`，直接赋值TVM FFI Tensor。

**F08**: [split_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/split_layer.cpp#L88-L111) Forward_cpu()新增num_top==1分支，调用top[0]->ShareData(bottom[0])和top[0]->ShareDiff(bottom[0])。

**F09**: [split_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/split_layer.cpp#L100-L106) Forward_cpu() N=1路径输出[SPLIT-PERF]日志，字段包含count、shared_bytes、share_time、data_ptr_equal、was_already_shared、memcpy_saved。

**F10**: [split_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/split_layer.cpp#L74-L163) Forward_cpu() N≥2路径保留原有memcpy实现，输出包含total_copied、total_memcpy_time、avg_per_copy、throughput等字段的[SPLIT-PERF]日志。

**F11**: _caffe_ffi.cc中Blob方法FFI注册使用lambda包装，将ObjectPtr<Blob>参数转换为原始指针传入内部方法（如`[](Blob* self, const ObjectPtr<Blob>& other) { self->ShareData(other.get()); }`）。

**F12**: common.hpp中曾添加ObjectPtr<T>的TypeTraits特化，后续被移除。

**F13**: [_ffi_api.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/python/caffe_ffi/_ffi_api.py) _setup_windows_dll_paths()方法的dll_dirs列表新增`prefix / "Lib" / "site-packages" / "tvm_ffi" / "lib"`路径。

**F14**: .temp/clean_build_test.cmd中PATH环境变量新增`%CONDA_ENV%\Lib\site-packages\tvm_ffi\lib`目录，并设置`KMP_DUPLICATE_LIB_OK=TRUE`。

**F15**: test_blob_zerocopy.cpp测试用例使用make_object<Blob>()创建Blob对象，调用ShareData()时传入.get()原始指针。

**F16**: CMakeLists.txt中设置`set(CMAKE_UNITY_BUILD OFF CACHE BOOL "Unity build" FORCE)`。

**F17**: CMake注册了三个Python CTest标签：`caffe_ffi_python_p2b_regression`（标签python;p2b;regression）、`caffe_ffi_python_p2b_performance`（标签python;p2b;performance）、`caffe_ffi_python_all`（标签python;all）。

**F18**: CMake注册了三个自定义构建目标：p2b-regression、p2b-performance、check-all。

## 编译与运行时事件维度

**F19**: 编译过程中出现`storage_enabled_v<ObjectPtr<Blob>>`求值为false的编译报错。

**F20**: 编译过程中出现`other.defined()`调用报错，ObjectPtr类型无defined()方法。

**F21**: 编译过程中出现`TypeSchemaImpl<caffe_ffi::Blob>`实例化失败的SFINAE冲突报错。

**F22**: SplitLayer编译阶段出现参数类型不匹配：将原始指针bottom[0]（Blob*类型）传入期望const ObjectPtr<Blob>&参数的ShareData()方法。

**F23**: Windows运行时出现_caffe_ffi.dll加载失败，系统提示缺少tvm_ffi.dll依赖。

**F24**: Windows运行时出现OpenMP运行时库多副本冲突提示。

**F25**: CMake Unity Build模式下出现Array<ObjectPtr<Blob>>模板实例化顺序相关的编译报错。

**F26**: Python测试执行时系统Python 3.13被优先调用，而非conda环境Python 3.14。

## 修复记录维度

**F27**: common.hpp中自定义的ObjectPtr<T> TypeTraits特化被移除，代码使用vendor tvm-ffi v0.1.13rc3内置的TypeTraits实现。

**F28**: Blob::ShareData()/ShareDiff()/SharesDataWith()/SharesDiffWith()方法签名从`const ObjectPtr<Blob>&`改为`const Blob*`。

**F29**: null检查方式从`other.defined()`改为`other != nullptr`。

**F30**: Python FFI初始化和构建脚本中添加tvm_ffi/lib目录到DLL搜索路径。

**F31**: Windows构建脚本和运行环境设置KMP_DUPLICATE_LIB_OK=TRUE环境变量。

**F32**: CMake Unity Build被禁用（CMAKE_UNITY_BUILD=OFF）。

**F33**: clean_build_test.cmd在MSVC vcvars初始化后重新prepend conda环境路径到PATH前面。

## 测试结果维度

**F34**: C++单元测试test_blob_zerocopy.cpp共14个测试用例全部通过。

**F35**: Python P2-B回归测试共29项测试全部通过。

**F36**: test_blob_zerocopy.cpp包含ShareDataMakesPointersEqual测试用例，验证ShareData后两个Blob的data指针指向同一地址。

**F37**: test_blob_zerocopy.cpp包含引用计数相关测试，验证共享Tensor的引用计数行为。

**F38**: test_blob_zerocopy.cpp包含ReshapeBreaksSharing测试用例，验证Reshape()后共享关系断开。

## 性能数据维度

**F39**: CSV性能日志记录N=1 Split场景Δmem=-64B（内存增量为负，表示节省）。

**F40**: Blob::ShareData()日志记录old_data_ptr、new_data_ptr、shape、nbytes字段。

**F41**: Split::Forward N=1路径share_time计时单位为微秒（μs）。

**F42**: Split::Forward N=1路径memcpy_saved字段值等于copy_bytes_per_top，即单次memcpy的数据量。
