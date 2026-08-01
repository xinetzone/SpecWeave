# Blob COW Bug 修复 - Implementation Plan

> **注**：经过对抗性审查（V阶段），COW 语义已从最初的"Owner use_count>1 / Borrower use_count>2"演变为**对称阈值 + Identity Share 标志**方案。所有任务已完成并通过全量测试验证。

## [x] Task 1: 修复Blob COW条件 — 最终方案：对称阈值 + Identity Share
- **Priority**: high
- **Depends On**: None
- **Description**:
  - ✅ **COW阈值统一为 `use_count() > 1`（对称）**：data路径和diff路径、Owner和Borrower都使用相同阈值
  - ✅ **新增 `identity_share_data_`/`identity_share_diff_` 标志**：用于N=1 Split/Slice场景的in-place直通
  - ✅ **新增 `ShareDataIdentity()`/`ShareDiffIdentity()` 方法**：设置identity标志，绕过COW检查
  - ✅ **COW条件更新**：检查 `!identity_share_data_` / `!identity_share_diff_` 标志
  - ✅ **DataRefCount()/DiffRefCount()**：零元素tensor返回0（非defined或numel()==0）
  - ✅ **Reshape/Unshare/SetShapeOnly/懒分配路径**重置identity标志
- **Files Changed**:
  - `include/caffe_ffi/blob.hpp`
  - `src/caffe_ffi/blob.cpp`
- **Acceptance Criteria Addressed**: AC-1, AC-2, AC-3, AC-5, AC-6
- **Status**: ✅ 已完成

## [x] Task 2: Split/Slice层N=1使用Identity Share
- **Priority**: high
- **Depends On**: Task 1
- **Description**:
  - ✅ `split_layer.cpp` Forward_cpu(): N=1时使用 `ShareDataIdentity()`/`ShareDiffIdentity()`
  - ✅ `split_layer.cpp` Backward_cpu(): identity mode下先检查 `SharesDiffWith()`，跳过不必要的copy
  - ✅ `slice_layer.cpp`: N=1时同样使用Identity share
- **Files Changed**:
  - `src/caffe_ffi/layers/split_layer.cpp`
  - `src/caffe_ffi/layers/slice_layer.cpp`
- **Acceptance Criteria Addressed**: AC-7
- **Status**: ✅ 已完成

## [x] Task 3: 更新测试用例适配新语义
- **Priority**: high
- **Depends On**: Task 1, Task 2
- **Description**:
  - ✅ **`ShareDataMutationVisibleToBoth`**: 区分identity模式（in-place）和COW模式（isolation）
  - ✅ **`ShareDataMakesPointersEqual`/`ShareDiffMakesDiffPointersEqual`**: 读共享值使用`cpu_data()`/`cpu_diff()`而非`cpu_mutable_data()`，避免误触发COW
  - ✅ **`IdentityShareDataNoCOWInPlace`**（原TwoWayShareNoCOWInPlace）: 使用`ShareDataIdentity()`测试N=1 in-place直通
  - ✅ **`OwnerMutableDiffCOWWithSingleBorrower`**: 使用`ShareDiffIdentity()`进行N=1测试
  - ✅ **COW对称测试**: 添加data路径和diff路径的对称COW测试
- **Files Changed**:
  - `tests/cpp/test_blob_zerocopy.cpp`
- **Acceptance Criteria Addressed**: AC-9, AC-10
- **Status**: ✅ 已完成

## [x] Task 4: 修复InnerProduct层filler缺失（对抗性审查发现）
- **Priority**: high
- **Depends On**: 无（独立发现）
- **Description**:
  - ✅ **问题根因**：`InnerProductLayer::LayerSetUp()` 创建权重和偏置blob后，未应用prototxt中指定的`weight_filler`和`bias_filler`，导致权重为未初始化值（全0），网络输出恒为0
  - ✅ **修复**：添加filler应用逻辑，支持`constant`类型filler
    - `weight_filler { type: "constant" value: 1.0 }` → 权重全1
    - `bias_filler { type: "constant" value: 0.0 }` → 偏置全0
    - 其他filler类型（xavier/gaussian/msra）临时使用1.0并打印警告
  - ✅ 添加 `#include "caffe/proto/caffe.pb.h"` 以访问FillerParameter
- **Files Changed**:
  - `src/caffe_ffi/layers/inner_product_layer.cpp`
- **Acceptance Criteria Addressed**: AC-8（数值正确性）
- **Status**: ✅ 已完成

## [x] Task 5: 编译并运行全量测试验证修复
- **Priority**: high
- **Depends On**: Task 1-4
- **Description**:
  - ✅ 在 Docker 容器 `caffe-ffi-jupyter:latest`（conda 环境，gcc 14.3.0, cmake 4.4.0, ninja 1.13）中重新编译
  - ✅ 使用 `apps/caffe-ffi-jupyter/scripts/test-cpp-tests.sh` 脚本构建并运行
  - ✅ 构建目录在 Docker 卷 `/workspace/caffe-ffi-cpp-build`（Linux FS，避免NTFS性能问题）
- **Test Results**（2026-08-01）:
  - ✅ TR-5.1: C++ 测试 **242/242 通过**（0失败）
  - ✅ TR-5.2: Python 测试 **66/66 通过**（0失败）
  - ✅ TR-5.3: OwnerCOWTest 4/4 通过（OwnerMutableData/Diff COW对称验证）
  - ✅ TR-5.4: InsertSplitsTest.ForwardCorrectnessTwoConsumer 通过（fc1输出=4.0）
  - ✅ TR-5.5: InsertSplitsTest.ForwardCorrectnessInplaceSplit 通过（fc1输出=12.0）
  - ✅ TR-5.6: COWTest.IdentityShareDataNoCOWInPlace 通过（N=1 in-place直通）
  - ✅ TR-5.7: COWTest.COWModeThreeWayShareIsolatesBranches 通过（N≥2 COW隔离）
  - ✅ TR-5.8: SplitLayerZeroCopyTest 7/7 通过
  - ✅ TR-5.9: SliceLayerZeroCopyTest 7/7 通过
  - ✅ TR-5.10: ZeroCopyTest 16/16 通过
- **Status**: ✅ 已完成（308个测试全部通过，0失败）

## 变更文件清单

| 文件 | 变更类型 | 说明 |
|------|---------|------|
| [blob.hpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/include/caffe_ffi/blob.hpp) | 修改 | 添加identity标志、对称COW条件、Identity方法声明、RefCount修正 |
| [blob.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/blob.cpp) | 修改 | 实现对称COW逻辑、Identity方法、标志重置 |
| [split_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/split_layer.cpp) | 修改 | N=1使用Identity share，Backward检查SharesDiffWith |
| [slice_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/slice_layer.cpp) | 修改 | N=1使用Identity share |
| [inner_product_layer.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/src/caffe_ffi/layers/inner_product_layer.cpp) | 修改 | 添加filler应用逻辑（weight_filler/bias_filler） |
| [test_blob_zerocopy.cpp](file:///d:/spaces/SpecWeave/projects/xuanspace/libs/caffe-ffi/tests/cpp/test_blob_zerocopy.cpp) | 修改 | 更新测试用例适配新语义 |

## 后续建议（非阻塞）

1. **其他层filler排查**：Convolution等带权重层可能也存在类似filler缺失问题，建议后续排查
2. **filler完整实现**：xavier/gaussian/msra等filler类型当前使用constant 1.0临时替代，需实现正确的初始化算法
3. **编译警告清理**：当前有61个编译警告，可在后续迭代中清理
