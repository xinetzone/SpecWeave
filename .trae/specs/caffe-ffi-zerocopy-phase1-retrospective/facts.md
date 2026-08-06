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

---

## Phase 2 COW 实现维度（2026-07-31 追加）

### 文件变更

**F43**: [blob.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/blob.hpp#L119-L178) 新增 `cpu_mutable_data()` 和 `cpu_mutable_diff()` 方法，包含 COW 触发逻辑：当 `use_count() > 1` 时克隆张量并输出 `[COW]` 日志。

**F44**: [blob.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/blob.hpp#L232-L254) 新增 COW 查询方法：`IsDataShared()`、`IsDiffShared()`、`DataRefCount()`、`DiffRefCount()`、`UnshareData()`、`UnshareDiff()`、`mutable_data_tensor()`、`mutable_diff_tensor()`。

**F45**: [blob.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/blob.hpp#L24-L38) 新增运行期 COW 开关声明：`SetCOWEnabled(bool)` 和 `IsCOWEnabled()`，使用 `std::atomic<bool>` 实现线程安全。

**F46**: [blob.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/blob.cpp) 新增 `CloneTensor()` 辅助函数（单一 COW memcpy 点），实现 `UnshareData()`、`UnshareDiff()`、`mutable_data_tensor()`、`mutable_diff_tensor()` 和运行期 COW 开关逻辑。

**F47**: [blob.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/blob.cpp) 非 const 版本的 `cpu_data()` 和 `cpu_diff()` 被移除，所有写操作调用点迁移到 `cpu_mutable_data()`/`cpu_mutable_diff()`。

**F48**: [_caffe_ffi.cc](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/_caffe_ffi.cc) 新增 COW API 方法的 FFI 绑定注册：`IsDataShared()`、`DataRefCount()`、`UnshareData()`、`mutable_data_tensor()` 及其 diff 版本。

**F49**: [split_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/split_layer.cpp) N≥2 路径从 memcpy 改为 `ShareData()`/`ShareDiff()` 零拷贝共享，Forward_cpu() 日志添加 `[SPLIT-PERF]` 标签。

**F50**: [split_layer.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/layers/split_layer.hpp) 更新文档注释，反映 N≥2 COW 优化的零拷贝语义。

**F51**: [Options.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/Options.cmake#L12) 新增 `CAFFE_FFI_ENABLE_COW` CMake 选项，默认值为 ON。

**F52**: [TargetBuild.cmake](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/cmake/TargetBuild.cmake#L54-L60) 集成编译期 COW 开关：`CAFFE_FFI_ENABLE_COW=ON` 时定义 `CAFFE_FFI_ENABLE_COW` 编译宏，OFF 时跳过所有 COW 代码编译。

**F53**: [check_tvm_ffi_traits.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/scripts/check_tvm_ffi_traits.py) 创建 TypeTraits 预检脚本（300行），commit `384f4da`。

**F54**: [check_windows_dll.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/scripts/check_windows_dll.py) 创建 Windows DLL 自检脚本，commit `9d98c48`。

### 测试结果

**F55**: [test_blob_zerocopy.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/cpp/test_blob_zerocopy.cpp) C++ COW 单元测试共 20 个测试用例（10 个 COWApiTest + 6 个 COWTest + 4 个 ShareDataRefCount），覆盖 IsDataShared/DataRefCount/UnshareData/mutable_data_tensor/COW 写隔离/三向共享等场景。

**F56**: [test_cow.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/test_cow.py) Python COW 测试共 22 个测试用例（TestBlobCOWApi 12 个 + TestSplitCOWBehavior 10 个），覆盖 N=1/N=2/N=4 Split COW 隔离、const 访问不触发、in-place ReLU 触发 COW 等场景。

**F57**: [conftest.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/conftest.py) 新增 `cow_snapshot()` 辅助函数和 `_write_cow_csv_row()` CSV 扩展方法，COW 指标列（cow_events/cow_bytes/cow_saved_bytes）已加入性能日志。

**F58**: [conftest.py](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/python/conftest.py) P2B 测试类注册表新增 `TestBlobCOWApi` 和 `TestSplitCOWBehavior`。

### 设计文档

**F59**: `SPLIT_COW_PHASE2_DESIGN_DRAFT.md` 包含 9 个章节共 405 行，涵盖 COW 核心机制、API 变更、预期内存节省（N≥2 场景最高 87.5%）、4 阶段 16 步实施里程碑、编译期和运行期回退策略。

**F60**: Phase 2 COW 实现遵循 A1→A7→A2→A3→A4→A9→A6→A5→A8 顺序，共 9 个任务全部完成，涉及 3 个 commits（`384f4da`、`09d2bcf`、`9d98c48`）。
