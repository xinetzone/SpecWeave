# Blob COW Bug 修复 - Verification Checklist

## 代码修改检查

- [x] **CP-1**: blob.hpp cpu_mutable_data() COW条件已从`use_count() > 1`改为`use_count() > 2`（line 216）
- [x] **CP-2**: blob.hpp cpu_mutable_diff() COW逻辑已有IsCOWEnabled()运行时开关保护（ODR安全设计，无编译宏）
- [x] **CP-3**: blob.hpp cpu_mutable_diff() COW条件已有`IsCOWEnabled()`检查
- [x] **CP-4**: blob.hpp cpu_mutable_diff() COW阈值已从`use_count() > 1`改为`use_count() > 2`（line 272）
- [x] **CP-5**: blob.cpp mutable_data_tensor() COW条件已从`use_count() > 1`改为`use_count() > 2`（line 215）
- [x] **CP-6**: blob.cpp mutable_diff_tensor() COW条件已有`IsCOWEnabled()`检查
- [x] **CP-7**: blob.cpp mutable_diff_tensor() COW阈值已从`use_count() > 1`改为`use_count() > 2`（line 263）
- [x] **CP-8**: blob.hpp DataRefCount()已移除`numel() > 0`条件（仅检查defined()，line 380-381）
- [x] **CP-9**: blob.hpp DiffRefCount()已移除`numel() > 0`条件（仅检查defined()，line 384-385）
- [x] **CP-10**: 4处COW条件完全一致（IsCOWEnabled + defined + use_count>2）
- [x] **CP-11**: COW逻辑使用运行时开关（SetCOWEnabled/IsCOWEnabled），ODR安全，无编译宏保护内联函数
- [x] **CP-12**: UnshareData/UnshareDiff保持原语义（use_count>1即克隆），未被修改
- [x] **CP-13**: ShareDiff shape同步已实现（shape不匹配时Reshape，line 327-341 in blob.cpp）
- [x] **CP-14**: 文档注释已更新，正确描述use_count>2阈值和N=1 in-place语义

## 测试验证检查（待执行）

- [ ] **TP-1**: 编译成功无警告/错误
- [ ] **TP-2**: N=1两方共享场景测试通过（in-place修改可见）
- [ ] **TP-3**: N=2三方共享场景测试通过（COW隔离正确）
- [ ] **TP-4**: Owner三方共享mutable触发COW测试通过
- [ ] **TP-5**: 没有弱化其他现有测试的断言

## 功能验证检查（待执行）

- [ ] **FV-1**: N=1两方共享（ShareData后use_count=2）时cpu_mutable_data()不触发COW
- [ ] **FV-2**: N=1两方共享时修改b的数据在a中立即可见（in-place直通）
- [ ] **FV-3**: N=2三方共享（use_count=3）时cpu_mutable_data()触发COW获得私有副本
- [ ] **FV-4**: COW后修改私有副本不影响其他共享者（数据隔离）
- [ ] **FV-5**: 所有者在三方共享时mutable也触发COW（对称性）
- [ ] **FV-6**: DataRefCount对于空tensor（defined但numel=0）返回正确use_count而非0
- [ ] **FV-7**: ShareDiffWithDifferentShapes测试通过（shape正确跟随）
- [ ] **FV-8**: UnshareData/UnshareDiff在use_count=2时仍正确触发克隆（显式API）

## 端到端验证检查（待执行）

- [ ] **E2E-1**: ZeroCopyTest.ShareDataMutationVisibleToBoth通过
- [ ] **E2E-2**: ZeroCopyTest.ShareDataMultipleTimesIdempotent通过
- [ ] **E2E-3**: ShareDataRefCount.ShareDataAfterCOW通过
- [ ] **E2E-4**: ShareDataRefCount.OldTensorReleasedAfterShare通过
- [ ] **E2E-5**: ZeroCopyTest.SplitN2COWTriggerOnMutableData通过
- [ ] **E2E-6**: ZeroCopyTest.ShareDataAndDiffFromDifferentSources通过
- [ ] **E2E-7**: COWApiTest.DataRefCountZeroWhenUndefined通过
- [ ] **E2E-8**: ShareDiffRefCount.ShareDiffWithDifferentShapes通过
- [ ] **E2E-9**: SliceLayerZeroCopyTest.SingleOutputGradientPassthrough通过
- [ ] **E2E-10**: OwnerCOWTest.OwnerMutableDataTriggersCOWWhenShared通过

## 无回归验证检查（待执行）

- [ ] **NR-1**: test_blob_zerocopy中所有其他测试（非COW相关）仍然通过
- [ ] **NR-2**: 其他caffe-ffi测试套件（layer测试等）全部通过
- [ ] **NR-3**: N=1 SliceLayer的Forward/Backward zero-copy正常工作
- [ ] **NR-4**: 内存分配追踪（CPUMemAlloc）没有显示泄漏
