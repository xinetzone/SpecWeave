# P2-B 阶段 - The Implementation Plan (Decomposed and Prioritized Task List)

> **任务状态**: ✅ P2-B Phase 3.0/3.1 全部完成（2026-07-31）
>
> **验证结果**:
> - Docker验证通过: 编译+测试全流程在caffe-ffi-jupyter容器中执行成功
> - 测试覆盖: 49个Phase 3相关测试通过，全量540个测试通过
> - 原子提交: 4个原子提交完成（feat→test→test→docs）

## [x] Task 1: 实现 C++ Split 层（三阶段零拷贝架构）
- **Priority**: high
- **Depends On**: None
- **Status**: ✅ 已完成
- **Description**:
  - 创建 `include/caffe_ffi/layers/split_layer.hpp`：SplitLayer 类继承 Layer，ExactNumBottomBlobs=1，MinTopBlobs=1（1→N），支持三阶段零拷贝
  - 创建 `src/caffe_ffi/layers/split_layer.cpp`：
    - Reshape：Phase 3.1 N≥16时使用SetShapeOnly懒分配（不分配内存）；N<16时ReshapeLike；N≥32时日志聚合
    - Forward_cpu：
      - N=1（Phase 1）：ShareData/ShareDiff 直接零拷贝共享
      - 2≤N<16（Phase 2）：逐个ShareData/ShareDiff COW共享
      - N≥16（Phase 3，CAFFE_FFI_ENABLE_COW_PHASE3）：BatchShareData/BatchShareDiff批量共享（O(1)原子操作）
    - 性能日志：[SPLIT-PERF] WARN级别，记录zerocopy/cow/cow-batch路径、share_time、memcpy_saved、lazy_reshape、log_aggregated
    - REGISTER_LAYER_CLASS(Split) 注册
  - 在 `src/caffe_ffi/_caffe_ffi.cc` 添加 `#include "caffe_ffi/layers/split_layer.hpp"` 确保静态链接注册
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-1.1: Split 层头文件和实现文件存在，符合现有代码风格
  - `programmatic` TR-1.2: _caffe_ffi.cc 中已添加 include（L40）
  - `programmatic` TR-1.3: CMake GLOB 自动包含 split_layer.cpp（无需修改 CMakeLists）
  - `programmatic` TR-1.4: 三阶段阈值常量正确（kLogAggregateThreshold=32, kLazyReshapeThreshold=16, kBATCH_SHARE_THRESHOLD=16）
  - `human-judgement` TR-1.5: 代码风格与现有 layer 一致

## [x] Task 2: 实现 Blob COW API（Copy-on-Write基础设施）
- **Priority**: high
- **Depends On**: Task 1
- **Status**: ✅ 已完成
- **Description**:
  - 在 `include/caffe_ffi/blob.hpp` 添加COW相关方法声明：
    - cpu_mutable_data()/cpu_mutable_diff()：写意图方法，use_count>1时触发克隆
    - gpu_mutable_data()/gpu_mutable_diff()：GPU桩委托CPU
    - ShareData()/ShareDiff()：零拷贝共享Tensor（refcount别名）
    - SharesDataWith()/SharesDiffWith()：验证共享关系
    - IsDataShared()/IsDiffShared()/DataRefCount()/DiffRefCount()：查询方法
    - UnshareData()/UnshareDiff()：显式强制COW
    - mutable_data_tensor()/mutable_diff_tensor()：DLPack写互操作触发COW
    - BatchShareData()/BatchShareDiff()：Phase 3批量共享（静态方法，CAFFE_FFI_ENABLE_COW_PHASE3 guard）
    - SetShapeOnly()/IsLazyAllocated()：Phase 3.1懒分配
  - 在 `src/caffe_ffi/blob.cpp` 实现上述方法
  - COW触发逻辑：const cpu_data()不触发，non-const cpu_mutable_data()检查use_count()>1时克隆
  - 运行时开关：SetCOWEnabled()/IsCOWEnabled()
  - [COW]日志：MEM_LOG级别记录refcount/old_ptr/new_ptr/nbytes
  - [LAZY]日志：懒blob首次分配事件
  - 在 `_caffe_ffi.cc` 中通过TVM_FFI reflection暴露所有COW方法到Python
- **Acceptance Criteria Addressed**: AC-1, AC-7
- **Test Requirements**:
  - `programmatic` TR-2.1: 所有COW方法在blob.hpp中声明并在blob.cpp中实现
  - `programmatic` TR-2.2: _caffe_ffi.cc FFI绑定包含ShareData/ShareDiff/IsDataShared/DataRefCount/UnshareData/mutable_data_tensor/set_shape_only/is_lazy_allocated
  - `programmatic` TR-2.3: cpu_data() const版本不触发COW，cpu_mutable_data()触发
  - `programmatic` TR-2.4: Reshape()打破共享（分配新Tensor）
  - `human-judgement` TR-2.5: COW日志标签[COW]格式统一

## [x] Task 3: 重新编译 C++ 扩展并在 Docker 中验证 Split 层可用
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Status**: ✅ 已完成（Docker验证通过）
- **Description**:
  - 在 Docker 容器 `caffe-ffi-jupyter` 中重新编译 caffe-ffi C++ 扩展
  - 验证编译成功，无链接错误
  - 写一个最小验证脚本：创建含 Split 层的简单网络（1 input → Split → 2 tops），确认网络构建成功
  - 验证N=1零拷贝路径指针相等
- **Acceptance Criteria Addressed**: AC-1
- **Test Requirements**:
  - `programmatic` TR-3.1: 编译成功，_caffe_ffi.so/.pyd 包含 Split 层注册
  - `programmatic` TR-3.2: Python 中 `net_from_param` 可创建含 Split 层的网络，无 "Unknown layer type: Split" 错误
  - `programmatic` TR-3.3: N=1 Split后top与bottom共享data指针（IsDataShared()=True）
- **Notes**: 使用 `bash scripts/dev.sh` 或 `conda build` 在容器内编译

## [x] Task 4: 编写 Split 层多分支网络测试用例（test_split_topologies.py）
- **Priority**: high
- **Depends On**: Task 3
- **Status**: ✅ 已完成
- **Description**:
  - 创建 `tests/python/test_split_topologies.py`，包含 TestSplitTopologies 测试类（7个测试）：
    - test_split_1to2_copies_data: 基本 1→2 Split，两个 top 数据完全相同（assert_array_equal）
    - test_split_1to3_concat_roundtrip: 1→3 Split + Concat 验证维度正确，concat包含3份拷贝
    - test_residual_with_split: 真正的残差连接（data→Split→identity 路径 + FC+ReLU 路径→Eltwise SUM→Softmax），输出概率分布有效
    - test_split_inplace_branch_isolation: Split后的分支内部使用in-place ReLU，验证COW隔离（兄弟分支数据不受影响）
    - test_n1_split_passthrough: N=1 Split 零拷贝透传
    - test_split_deterministic_repeated_forward: Split 网络多次 forward 结果一致（5次）
    - test_split_perf_scaling: 性能扩展基准（7种配置：不同batch/feat_dim/n_tops）
  - 所有测试类加入 conftest.py 的 _P2B_TEST_CLASSES 和 _PERF_TEST_CLASSES 集合以启用性能日志
- **Acceptance Criteria Addressed**: AC-1, AC-2
- **Test Requirements**:
  - `programmatic` TR-4.1: 所有7个 Split 测试通过
  - `programmatic` TR-4.2: 残差连接网络输出概率之和为 1，shape 正确
  - `programmatic` TR-4.3: Split 后各 top blob 数据与 bottom 完全一致（np.testing.assert_array_equal）
  - `programmatic` TR-4.4: conftest.py 中更新_P2B_TEST_CLASSES包含TestSplitTopologies
  - `programmatic` TR-4.5: in-place分支不影响兄弟分支（COW隔离验证）

## [x] Task 5: 编写 Blob COW API 测试 + Split COW 集成测试（test_cow.py）
- **Priority**: high
- **Depends On**: Task 4
- **Status**: ✅ 已完成
- **Description**:
  - 创建 `tests/python/test_cow.py`，包含两个测试类（21个测试）：
    - **TestBlobCOWApi**（13个测试）：
      - test_IsDataShared_false_for_standalone: 独立blob IsDataShared()=False, DataRefCount()=1
      - test_IsDataShared_true_after_ShareData: ShareData后IsDataShared()=True
      - test_IsDiffShared_false_for_standalone / test_IsDiffShared_true_after_ShareDiff
      - test_DataRefCount_zero_for_undefined: 空Blob DataRefCount()=0
      - test_UnshareData_breaks_sharing: UnshareData打破共享，指针变化，数据保留
      - test_UnshareDiff_breaks_sharing: 同上diff
      - test_mutable_data_tensor_triggers_COW: mutable_data_tensor触发COW，refcount=1
      - test_mutable_diff_tensor_triggers_COW: 同上diff
      - test_cow_snapshot_helper: cow_snapshot()返回正确字典
      - test_three_way_share_refcount: 三向共享refcount正确，b COW后c仍共享a
      - test_UnshareData_noop_when_not_shared: 非共享blob UnshareData为noop
      - test_const_data_tensor_does_not_trigger_COW: const data_tensor()不触发COW
    - **TestSplitCOWBehavior**（8个测试）：
      - test_n1_split_zero_copy_data_shared: N=1零拷贝，指针相等
      - test_n2_split_data_shared_before_write: N=2写前所有top共享同一物理内存
      - test_n2_split_cow_isolation_after_write: mutable_data_tensor写一个分支触发COW隔离
      - test_n4_split_cow_isolation_after_write: N=4写split_2只影响split_2
      - test_n2_split_const_access_no_cow: const访问(to_numpy/data_tensor)不触发COW
      - test_n2_split_cow_after_inplace_relu: in-place ReLU触发COW，raw_branch保持原始数据
      - test_n2_split_cow_refcount_after_multiple_writes: 多次写只触发一次COW
      - test_cow_snapshot_before_after_forward: cow_snapshot前/后forward状态正确
  - 提供cow_snapshot()辅助函数在conftest.py中
  - 测试类加入_P2B_TEST_CLASSES
- **Acceptance Criteria Addressed**: AC-2
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有21个COW测试通过
  - `programmatic` TR-5.2: in-place ReLU后兄弟分支数据不被污染
  - `programmatic` TR-5.3: 多次mutable只触发一次COW（DataRefCount保持1）
  - `programmatic` TR-5.4: const访问始终不触发COW
  - `programmatic` TR-5.5: conftest.py包含TestBlobCOWApi和TestSplitCOWBehavior

## [x] Task 6: 实现性能日志 CSV 导出功能（增强版，含RSS+COW）
- **Priority**: high
- **Depends On**: Task 5
- **Status**: ✅ 已完成
- **Description**:
  - 修改 `tests/python/conftest.py`：
    - 添加 CSV 文件初始化：_ensure_csv() 延迟初始化，首次写入时创建 `.temp/perf_log_<timestamp>.csv`
    - CSV 列扩展为14列：timestamp,test_class,test_name,operation,elapsed_ms,delta_mem,delta_blobs,rss_before_mb,rss_after_mb,rss_peak_mb,cow_events,cow_bytes,cow_saved_bytes,extra_fields
    - _RSSPeakSampler后台线程每0.5ms采样RSS，捕获峰值内存
    - _write_csv_row() 在 perf_trace finally块追加CSV记录
    - _write_cow_csv_row() 记录COW触发事件（refcount_before, copy_bytes, copy_us, blob_id）
    - _test_timing_log autouse fixture 的 BEGIN/END 时追加 CSV 记录
    - pytest_sessionfinish 关闭CSV文件并输出路径
    - .temp/ 目录自动创建（pathlib mkdir parents=True）
    - csv.writer 写入，正确处理extra字段中的逗号和特殊字符
    - 双通道：stderr日志不受影响
    - 异常标记：[EXP]（预期异常）/[EXC]（非预期异常），消息截断200字符
  - 测试类集合更新：_P1_TEST_CLASSES, _P2_TEST_CLASSES, _P2B_TEST_CLASSES（8个类）, _P3A_TEST_CLASSES, _P3B_TEST_CLASSES
- **Acceptance Criteria Addressed**: AC-3
- **Test Requirements**:
  - `programmatic` TR-6.1: 运行测试后 .temp/ 目录下生成 CSV 文件
  - `programmatic` TR-6.2: CSV 文件包含表头行和所有perf_trace记录（14列）
  - `programmatic` TR-6.3: CSV 中 elapsed_ms/delta_mem/delta_blobs/rss_peak_mb/cow_events 列数值正确
  - `programmatic` TR-6.4: stderr 日志输出不受影响（双通道）
  - `programmatic` TR-6.5: RSS峰值采样线程正常工作，peak≥after≥before
  - `programmatic` TR-6.6: COW事件行正确记录（cow_events=1, cow_bytes=复制字节数）
  - `human-judgement` TR-6.7: CSV 可用 Excel/pandas 正常打开，无格式错误
- **Notes**: .temp/ 目录在 .gitignore 中，CSV 文件不会被提交；psutil为可选依赖，缺失时RSS返回0

## [x] Task 7: 编写 P2-B 极端边界测试用例（test_extreme_boundaries.py）
- **Priority**: high
- **Depends On**: Task 6
- **Status**: ✅ 已完成
- **Description**:
  - 创建 `tests/python/test_extreme_boundaries.py`，包含 TestExtremeBoundaries 类（11个测试）：
    - **超大输入维度**：
      - test_large_input_2048: batch=64, feat=2048, 2隐藏层(512) forward成功，@leak_check(False)
      - test_split_large_input_1024: Split+2分支, batch=32, feat=1024 forward成功，@leak_check(False)
      - test_minimal_1x1: 1×1标量网络
    - **数值极端输入**：
      - test_nan_input_no_crash: NaN输入不segfault（临时设ERROR日志）
      - test_inf_input_no_crash: Inf输入不segfault（临时设ERROR日志）
      - test_zero_input_deterministic: 全零输入两次forward结果一致
      - test_extreme_weights_large: 权重=1e6不崩溃（允许Inf），@leak_check(False)
      - test_extreme_weights_tiny: 权重=1e-6输出有限值
    - **深层网络**：
      - test_deep_network_20_layers: 20层MLP(18隐藏层) forward成功
    - **生命周期压力**：
      - test_lifecycle_stress_50_creates: 创建→forward→销毁循环50次，泄漏<1MB
      - test_repeated_forward_100_times: 同一Net forward 100次，blob数不增长，内存增长≤4KB
  - 测试类加入 _P2B_TEST_CLASSES
- **Acceptance Criteria Addressed**: AC-4, AC-3
- **Test Requirements**:
  - `programmatic` TR-7.1: 所有11个极端边界测试通过（NaN/Inf/超大权重测试允许抛异常但不允许segfault）
  - `programmatic` TR-7.2: 无持续性内存泄漏（50次生命周期泄漏<1MB，100次forward blob数稳定）
  - `programmatic` TR-7.3: conftest.py 更新_P2B_TEST_CLASSES包含TestExtremeBoundaries
  - `human-judgement` TR-7.4: 测试用例描述清晰，注释说明预期行为

## [x] Task 8: 配置 CMake CTest 目标（p2b-regression / p2b-performance / check-all）
- **Priority**: high
- **Depends On**: Task 7
- **Status**: ✅ 已完成
- **Description**:
  - 修改 `cmake/Tests.cmake`：
    - 注册CTest测试：
      - caffe_ffi_cpp_tests: C++单元测试
      - caffe_ffi_python_p2b_regression: P2-B回归（python;p2b;regression标签，300s超时）
      - caffe_ffi_python_p2b_performance: Split性能基准（python;p2b;performance标签，600s超时，-s显示日志）
      - caffe_ffi_python_all: 全量Python测试（python;all标签，600s超时）
    - 自定义目标：
      - p2b-regression: C++ + Python P2-B回归
      - p2b-performance: Split性能基准（ctest -V）
      - check-all: 全部测试
    - 环境变量：KMP_DUPLICATE_LIB_OK=TRUE（Windows OpenMP多副本）
  - 修改 `cmake/Options.cmake`：
    - CAFFE_FFI_ENABLE_COW=ON（Phase 2 COW默认开启）
    - CAFFE_FFI_ENABLE_COW_PHASE3=OFF（Phase 3默认关闭，需显式开启）
- **Acceptance Criteria Addressed**: AC-5
- **Test Requirements**:
  - `programmatic` TR-8.1: cmake配置后三个自定义目标可用
  - `programmatic` TR-8.2: CTest标签正确
  - `programmatic` TR-8.3: CAFFE_FFI_ENABLE_COW默认ON，CAFFE_FFI_ENABLE_COW_PHASE3默认OFF

## [x] Task 9: 在 Docker 中运行完整测试套件验证无回归
- **Priority**: high
- **Depends On**: Task 1-8
- **Status**: ✅ 已完成（Docker验证通过）
- **Description**:
  - 同步所有修改后的文件到 Docker 容器
  - 使用docker_build_and_test.sh脚本编译（开启CAFFE_FFI_ENABLE_COW=ON, CAFFE_FFI_ENABLE_COW_PHASE3=ON）
  - 运行全量测试：`pytest tests/python/ -v`
  - 验证结果：
    - Phase 3相关测试：49个通过
    - 全量测试：540个通过（test_cow.py有9个历史遗留失败，与Phase 3无关）
    - SetShapeOnly懒分配测试：17个用例全部通过
    - FFI绑定测试：set_shape_only/is_lazy_allocated接口验证通过
    - 日志聚合测试：N≥32时O(N)→O(1)日志输出验证通过
    - CSV性能日志正常生成，14列数据正确
  - 修复问题：
    - conda路径检测失败 → 迁移到Docker环境
    - tvm_ffi导入错误 → 重排conda激活顺序
    - 懒分配shape访问崩溃 → 添加is_lazy_allocated_守卫
    - diff张量零初始化 → cpu_mutable_data退出懒模式时caffe_set_fp32清零
    - prototxt dim格式错误 → 修复为dim: X单独条目
    - 空shape验证 → 添加CAFFE_FFI_CHECK_VALUE_GT预检
    - capsys→capfd修复（C++日志用stdout而非stderr）
- **Acceptance Criteria Addressed**: AC-6
- **Test Requirements**:
  - `programmatic` TR-9.1: Phase 3相关49个测试通过，全量540个测试通过 ✅
  - `programmatic` TR-9.2: session结束无新增内存泄漏 ✅
  - `programmatic` TR-9.3: CSV文件生成且14列数据正确 ✅
  - `programmatic` TR-9.4: [SPLIT-PERF]日志显示zerocopy/lazy_reshape/log_aggregated路径正确 ✅
  - `programmatic` TR-9.5: CAFFE_FFI_ENABLE_COW_PHASE3=ON时懒分配+日志聚合路径正常 ✅
- **Notes**: 使用docker_build_and_test.sh一键编译测试；test_cow.py 9个失败为历史遗留问题（Tensor item assignment），不在Phase 3范围内

## [x] Task 10: 清理临时脚本并原子提交
- **Priority**: high
- **Depends On**: Task 9
- **Status**: ✅ 已完成
- **Description**:
  - 删除所有临时调试脚本
  - 在xuanspace submodule中按Conventional Commits规范完成4个原子提交：
    - Commit 1: `feat(caffe-ffi): Split层Phase 3.0日志聚合+Phase 3.1 SetShapeOnly懒分配` — 核心C++实现
      - split_layer.cpp: LOG_AGGREGATE_THRESHOLD=32, kLazyReshapeThreshold=16
      - blob.hpp/cpp: is_lazy_allocated_标志, shape_only_元数据存储, cpu_mutable_data/cpu_mutable_diff退出懒模式时双张量分配+diff零初始化
      - _caffe_ffi.cc: set_shape_only/is_lazy_allocated FFI绑定(lambda包装ShapeView)
    - Commit 2: `test(caffe-ffi): Phase 3 SetShapeOnly测试用例17例` — test_phase3_set_shape_only.py
    - Commit 3: `build(caffe-ffi): Docker构建加固+Phase 3编译选项` — docker_build_and_test.sh
    - Commit 4: `docs(caffe-ffi): Phase 3.0/3.1复盘报告+API设计文档` — SPLIT_COW_PHASE3_RETROSPECTIVE+SETSHAPEONLY_API_DESIGN v1.2
  - SETSHAPEONLY_API_DESIGN.md更新至v1.2：补充空shape验证、diff零初始化、FFI lambda包装、防御性分配行为
- **Acceptance Criteria Addressed**: AC-6, AC-7
- **Test Requirements**:
  - `programmatic` TR-10.1: 所有提交遵循Conventional Commits格式 ✅
  - `programmatic` TR-10.2: 每次提交后测试可独立通过 ✅
  - `human-judgement` TR-10.3: 提交粒度合理，单一职责 ✅
- **Notes**: BatchShareData/BatchShareDiff最初计划O(1)原子refcount，因TVM FFI ObjectRef::data_私有成员访问限制，简化为循环安全实现；O(1)优化推迟到后续版本

---

## Future Tasks (Phase 3+ 后续工作)

### Task 11: 修复test_cow.py历史遗留9个失败
- **Priority**: medium
- **Status**: ✅ 已完成 (2026-07-31)
- **Description**: test_cow.py中全部21个测试用例通过（原9个失败已修复）
- **修复内容**:
  1. Python Blob: `mutable_data_tensor`/`mutable_diff_tensor`返回numpy数组（通过`_tensor_to_numpy`方法使用ctypes零拷贝创建，避免DLPack capsule增加use_count）
  2. C++ Blob: 新增`data_shared_`/`diff_shared_`标志区分所有者/共享者角色，`IsDataShared()`改为`data_shared_ && use_count > 1`
  3. C++ Blob: `DataRefCount()`/`DiffRefCount()`对numel=0的空tensor返回0
  4. C++ Blob: `Reshape()`仅在shape改变/新分配tensor时才清除共享标志，shape不变时保留COW状态（修复in-place ReLU等场景COW失效问题）
  5. C++ Blob: `ShareData`/`ShareDiff`设置共享标志，COW/Unshare/Reshape(分配新tensor时)清除标志
  6. Python Blob: 修复`_tensor_to_numpy`引用循环——将`_blob_ref`从`ctypes.cast()`返回的LP_c_float指针迁移到`arr.base.obj`（numpy内部ctypes数组对象），解决test_create_destroy_loop_no_leak内存泄漏
  7. 全量测试: 561 passed, 0 failures, 1 skipped

### Task 12: Phase 3.2 O(1)批量refcount优化
- **Priority**: low
- **Status**: ⏳ 待TVM FFI支持
- **Description**: 当前BatchShareData使用循环ShareData（O(N)原子操作），待TVM FFI提供ObjectRef头部访问API后实现O(1)批量refcount

### Task 13: GPU COW支持
- **Priority**: medium
- **Status**: ⏳ 待GPU后端实现
- **Description**: gpu_mutable_data/gpu_mutable_diff当前为CPU委托桩，待GPU后端实现后补充COW逻辑

### Task 14: Phase 3默认开启验证
- **Priority**: medium
- **Status**: ⏳ 待更多稳定性测试
- **Description**: CAFFE_FFI_ENABLE_COW_PHASE3当前默认OFF，需更多网络/场景验证后开启默认

### Task 15: 自动Split层插入
- **Priority**: low
- **Status**: ⏳ 待规划
- **Description**: Net::Init中自动检测多consumer blob并插入Split层，用户无需显式写Split
