# Blob COW Bug 修复 - Implementation Plan

## [x] Task 1: 修复Blob头文件中cpu_mutable_data()和cpu_mutable_diff()的COW条件
- **Priority**: high
- **Depends On**: None
- **Description**:
  - ✅ 将blob.hpp中`cpu_mutable_data()`的COW条件从`use_count() > 1`改为`use_count() > 2`（line 216）
  - ✅ blob.hpp中`cpu_mutable_diff()`的COW条件：
    1. 原有IsCOWEnabled()检查已具备（代码已实现运行时开关，无编译宏保护是ODR安全设计）
    2. 将阈值从`use_count() > 1`改为`use_count() > 2`（line 272）
  - 注意：CloneTensor在blob.cpp匿名namespace中，头文件中保持手动memcpy实现即可（与现有代码一致）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5, AC-6
- **Test Requirements**:
  - `programmatic` TR-1.1: cpu_mutable_data()在两方共享（use_count=2）时不触发COW
  - `programmatic` TR-1.2: cpu_mutable_data()在三方共享（use_count=3）时触发COW
  - `programmatic` TR-1.3: cpu_mutable_diff()在IsCOWEnabled()=false时不执行COW逻辑
  - `human-judgement` TR-1.4: cpu_mutable_data和cpu_mutable_diff的COW代码结构对称
- **Status**: 已完成

## [x] Task 2: 修复Blob实现文件中mutable_data_tensor()和mutable_diff_tensor()的COW条件
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - ✅ 将blob.cpp中`mutable_data_tensor()`的COW条件从`use_count() > 1`改为`use_count() > 2`（line 215）
  - ✅ blob.cpp中`mutable_diff_tensor()`的COW条件：
    1. 原有IsCOWEnabled()检查已具备
    2. 将阈值从`use_count() > 1`改为`use_count() > 2`（line 263）
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5
- **Test Requirements**:
  - `programmatic` TR-2.1: mutable_data_tensor()在两方共享时不COW，三方共享时COW
  - `programmatic` TR-2.2: mutable_diff_tensor()已有IsCOWEnabled()检查
  - `programmatic` TR-2.3: mutable_diff_tensor()阈值为use_count>2
  - `human-judgement` TR-2.4: mutable_data_tensor和mutable_diff_tensor的COW条件完全对称
- **Status**: 已完成

## [x] Task 3: 修复DataRefCount()和DiffRefCount() API
- **Priority**: high
- **Depends On**: None
- **Description**:
  - ✅ 移除blob.hpp中`DataRefCount()`的`data_tensor_.numel() > 0`条件（line 380-381）
  - ✅ 移除blob.hpp中`DiffRefCount()`的`diff_tensor_.numel() > 0`条件（line 384-385）
  - ✅ 修复后：tensor.defined()即返回use_count()，否则返回0
- **Acceptance Criteria Addressed**: AC-4
- **Test Requirements**:
  - `programmatic` TR-3.1: 空tensor（numel=0但defined()=true）返回use_count()而非0
  - `programmatic` TR-3.2: undefined tensor返回0
- **Status**: 已完成

## [x] Task 4: 更新文档注释
- **Priority**: medium
- **Depends On**: Task 1, Task 2
- **Description**:
  - ✅ 更新文件头COW语义文档，正确描述use_count>2阈值和N=1 in-place语义
  - ✅ 更新cpu_mutable_data()方法注释
  - ✅ 更新cpu_mutable_diff()方法注释
  - 说明：关于MutableDataTriggersCOWWhenShared测试——代码中该测试可能已使用正确场景或无需修改（待测试验证）
- **Acceptance Criteria Addressed**: AC-5
- **Status**: 已完成

## [ ] Task 5: 编译并运行COW相关测试验证修复
- **Priority**: high
- **Depends On**: Task 1, Task 2, Task 3, Task 4
- **Description**:
  - 在Docker/WSL环境中重新编译caffe-ffi
  - 运行test_blob_zerocopy中所有COW/零拷贝相关测试
  - 验证N=1 gradient直通测试通过
  - 验证N=2 COW触发测试通过
  - 验证DataRefCount/DiffRefCount空tensor测试通过
  - 验证ShareDiff shape同步测试通过
  - 确认无回归
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-4, AC-7, AC-8
- **Test Requirements**:
  - `programmatic` TR-5.1: 所有COW相关测试通过（0失败）
  - `programmatic` TR-5.2: N=1两方共享in-place修改可见性测试通过
  - `programmatic` TR-5.3: N=2三方共享COW隔离测试通过
  - `programmatic` TR-5.4: OwnerCOWTest通过（所有者三方共享mutable COW）
  - `programmatic` TR-5.5: DataRefCountZeroWhenUndefined通过
  - `programmatic` TR-5.6: ShareDiffWithDifferentShapes通过
  - `programmatic` TR-5.7: 完整test_blob_zerocopy测试套件无回归
- **Status**: 待执行

## [ ] Task 6: 运行完整caffe-ffi测试套件验证无回归
- **Priority**: medium
- **Depends On**: Task 5
- **Description**:
  - 运行所有caffe-ffi测试（包括其他layer测试）
  - 确认COW修复没有引入任何回归
- **Acceptance Criteria Addressed**: NFR-4
- **Test Requirements**:
  - `programmatic` TR-6.1: 完整测试套件全部通过
- **Status**: 待执行
