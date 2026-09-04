# Blob COW（写时复制）Bug 修复 - Product Requirement Document

## Overview
- **Summary**: 修复 caffe-ffi Blob 类中 Copy-On-Write (COW) 逻辑的多个bug，导致零拷贝/COW相关测试失败。核心问题是COW触发阈值错误（`use_count > 1`应为`use_count > 2`），导致N=1单输出场景下零拷贝in-place通路被错误断开；同时存在DataRefCount/DiffRefCount API错误等问题。
- **Purpose**: 确保COW语义正确——use_count=2（两方共享，N=1场景）时mutable访问不复制（直通in-place）；use_count≥3（多方共享，N≥2场景）时mutable访问触发私有副本；修复RefCount API等相关bug。
- **Target Users**: caffe-ffi库开发者、使用Blob零拷贝优化的Layer实现者。

## Goals
- ✅ **已完成**：修复COW触发阈值：将所有4处COW条件从`use_count > 1`改为`use_count > 2`
- ✅ **已完成**：统一data和diff路径的COW逻辑（对称化：都有IsCOWEnabled()检查）
- ✅ **已完成**：修复DataRefCount()/DiffRefCount()在空tensor时错误返回0的bug（移除numel()>0条件）
- ✅ **已完成（代码已具备）**：cpu_mutable_diff() COW检查已受IsCOWEnabled()运行时开关保护
- ✅ **已完成（代码已具备）**：修复ShareDiff后data/diff shape不一致问题（Reshape同步）
- ⏳ **待执行**：更新6个使用旧语义的测试用例（两方共享期待COW→三方共享）
- **待验证**：确保所有COW相关测试通过，无回归

## Non-Goals (Out of Scope)
- 不重构Blob类整体架构
- 不修改COW之外的其他功能（GPU支持、序列化等）
- 不改变UnshareData/UnshareDiff显式COW API语义（仍use_count>1即执行）
- 不改变data_shared_/diff_shared_标志的使用方式
- 不恢复编译宏COW开关（当前运行时开关设计是ODR安全的正确选择）

## Background & Context
Blob使用TVM FFI intrusive reference counting实现COW零拷贝优化：
- `ShareData(other)` / `ShareDiff(other)`：零拷贝共享tensor指针（ObjectPtr赋值，引用计数+1）
- `cpu_mutable_data()` / `cpu_mutable_diff()`：返回可写指针；如多方共享则复制（COW）

**COW架构说明（运行时开关设计）**：
COW逻辑**始终编译进**代码，通过运行时开关`SetCOWEnabled()/IsCOWEnabled()`控制，而非编译宏。这是为了防止ODR（One Definition Rule）违规——当public头文件中的内联函数被可能不一致定义的预处理器宏保护时会引发此问题。CMake选项`CAFFE_FFI_ENABLE_COW`保留用于设置运行时开关的初始默认状态。

**正确COW语义模型（对称模型）**：
| use_count | 场景 | mutable行为 | 原因 |
|-----------|------|-------------|------|
| 1 | 独占 | 直接返回，不复制 | 无共享者 |
| 2 | 两方共享（N=1 Slice单输出） | 不复制，in-place直通 | 一对一修改等价于直接修改源 |
| ≥3 | 多方共享（N≥2 Slice多输出） | COW克隆，获得私有副本 | 避免修改污染其他共享者 |

**显式Unshare API语义**：
`UnshareData()/UnshareDiff()`保持`use_count>1`即执行克隆的语义——因为它们代表显式"强制断开共享"的请求。

### 已修复的4处COW条件位置
| 文件 | 行号 | 方法 | 修复前条件 | 修复后条件 | 状态 |
|------|------|------|-----------|-----------|------|
| blob.hpp | 216 | cpu_mutable_data() | `IsCOWEnabled() && data_tensor_.defined() && use_count>1` | `IsCOWEnabled() && data_tensor_.defined() && use_count>2` | ✅ 已修复 |
| blob.hpp | 272 | cpu_mutable_diff() | `IsCOWEnabled() && diff_tensor_.defined() && use_count>1` | `IsCOWEnabled() && diff_tensor_.defined() && use_count>2` | ✅ 已修复（原有IsCOWEnabled已具备） |
| blob.cpp | 215 | mutable_data_tensor() | `IsCOWEnabled() && data_tensor_.defined() && use_count>1` | `IsCOWEnabled() && data_tensor_.defined() && use_count>2` | ✅ 已修复 |
| blob.cpp | 263 | mutable_diff_tensor() | `IsCOWEnabled() && diff_tensor_.defined() && use_count>1` | `IsCOWEnabled() && diff_tensor_.defined() && use_count>2` | ✅ 已修复（原有IsCOWEnabled已具备） |

### 已修复的其他问题
- ✅ DataRefCount()/DiffRefCount()：移除`numel() > 0`条件，tensor.defined()即返回use_count()
- ✅ ShareDiff() shape同步：代码已实现shape不匹配时调用Reshape()同步data shape
- ✅ 文档注释：更新了COW语义说明，正确描述use_count>2阈值和N=1 in-place语义

### 需要验证的测试
- N=1 in-place修改可见性
- N=2场景COW触发
- DataRefCount空tensor返回值
- ShareDiff后shape一致性
- 所有测试无回归

## Functional Requirements
- **FR-1** ✅: COW触发阈值修正：4处COW条件统一为`IsCOWEnabled() && tensor.defined() && tensor.use_count() > 2`
- **FR-2** ✅: cpu_mutable_diff() COW逻辑与cpu_mutable_data()对称：运行时IsCOWEnabled()开关保护
- **FR-3** ✅: mutable_diff_tensor()已有IsCOWEnabled()检查，与mutable_data_tensor()对称
- **FR-4** ✅: DataRefCount()/DiffRefCount()修正：tensor.defined()即返回use_count()，移除`numel() > 0`条件
- **FR-5** ✅: ShareDiff()后保持data/diff shape一致性（Reshape同步，代码已实现）
- **FR-6** ✅: UnshareData()/UnshareDiff()保持原语义不变（use_count>1即执行克隆）
- **FR-7** ⏳: 更新6个使用旧COW语义的测试用例（两方共享期待COW→三方共享）
- **FR-8** ⏳: 添加N=1两方共享in-place直通的正向测试用例
- **FR-9** ⏳: 验证所有测试场景正确覆盖两方直通、三方COW的语义

## Non-Functional Requirements
- **NFR-1**: 只读访问路径（cpu_data/cpu_diff）零额外开销
- **NFR-2**: N=1场景mutable访问零拷贝（无内存分配和memcpy）
- **NFR-3**: 修复不引入内存泄漏（CPUMemAlloc追踪正确）
- **NFR-4**: 所有现有通过测试保持通过无回归

## Constraints
- **Technical**: C++17, TVM FFI Object系统, intrusive reference counting
- **Build**: 运行时COW开关（SetCOWEnabled/IsCOWEnabled），CAFFE_FFI_ENABLE_COW编译宏仅设置初始默认值
- **Code Style**: 遵循现有Blob代码风格，使用CAFFE_FFI_MEM_LOG记录COW事件
- **API Compatibility**: 不改变公共API签名，只修正内部逻辑

## Assumptions
- use_count()是原子读操作，性能开销可忽略
- TVM FFI ObjectPtr引用计数正确反映所有共享者数量（包括owner自身）
- CloneTensor（blob.cpp匿名namespace）和手动NewCPUTensor+memcpy（blob.hpp内联）功能等价
- ShareData/ShareDiff在正常Layer中总是成对从同一源调用（data/diff shape天然一致）
- UnshareData/UnshareDiff是显式"强制断开"API，任何共享状态（use_count>1）都应执行

## Acceptance Criteria

### AC-1: N=1两方共享不触发COW（零拷贝直通）
- **Given**: Blob a（所有者）和b（借用者），执行b->ShareData(a)，此时use_count=2
- **When**: 调用b->cpu_mutable_data()写入值99
- **Then**: 不触发COW（指针不变），a->cpu_data()[0] == 99立即可见
- **Verification**: `programmatic`

### AC-2: N>=2多方共享触发COW（正确隔离）
- **Given**: Blob a、b、c，b->ShareData(a), c->ShareData(a)，此时use_count=3
- **When**: 调用b->cpu_mutable_data()写入值888
- **Then**: 触发COW（指针变化），b获得私有副本；a和c仍共享原tensor，看不到888
- **Verification**: `programmatic`

### AC-3: 所有者在多方共享时mutable也触发COW
- **Given**: Blob owner创建数据，borrower1/2->ShareData(owner)，use_count=3
- **When**: owner->cpu_mutable_data()
- **Then**: 触发COW，owner获得新私有副本；borrower1/2保留旧数据且仍互相共享
- **Verification**: `programmatic`

### AC-4: DataRefCount/DiffRefCount空tensor正确
- **Given**: Blob有已定义但numel=0的tensor
- **When**: 调用DataRefCount()
- **Then**: 返回tensor.use_count()（至少1），不返回0
- **Verification**: `programmatic`

### AC-5: data/diff COW逻辑对称
- **Given**: COW启用
- **When**: 检查cpu_mutable_data vs cpu_mutable_diff、mutable_data_tensor vs mutable_diff_tensor
- **Then**: 四者COW条件完全一致（IsCOWEnabled+defined+use_count>2）
- **Verification**: `programmatic` + `human-judgment`

### AC-6: ShareDiff后shape一致
- **Given**: Blob a{2,3,4}（24元素），b{8}（8元素），b->ShareDiff(a)
- **When**: 检查b->num_axes()、b->count()
- **Then**: num_axes()==3, count()==24，data和diff shape一致
- **Verification**: `programmatic`

### AC-7: UnshareData/UnshareDiff显式API不变
- **Given**: Blob a和b两方共享（use_count=2）
- **When**: 调用b->UnshareData()
- **Then**: 仍然执行克隆（显式请求），b获得私有副本
- **Verification**: `programmatic`

### AC-8: 所有测试通过无回归
- **Given**: 完整test_blob_zerocopy测试套件
- **When**: 运行所有测试
- **Then**: 全部通过
- **Verification**: `programmatic`

### AC-9: 两方共享（use_count=2）不触发COW（N=1 in-place直通）
- **Given**: Blob a和b两方共享（b->ShareData(a)），use_count=2
- **When**: 调用b->cpu_mutable_data()写入值
- **Then**: 不触发COW（指针不变），a的数据立即可见（in-place修改）
- **Verification**: `programmatic`

### AC-10: 旧语义测试用例已更新为三方共享场景
- **Given**: 以下6个测试用例原先使用两方共享期待COW
  - ZeroCopyTest.ShareDataMutationVisibleToBoth
  - COWApiTest.MutableDataTensorTriggersCOW
  - COWApiTest.MutableDiffTensorTriggersCOW
  - COWApiTest.COWWriteIsolation
  - ShareDataRefCount.ShareDataAfterCOW（两处两方COW）
  - ZeroCopyTest.ShareDataAndDiffFromDifferentSources（data路径COW）
- **When**: 检查这些测试用例
- **Then**: 全部更新为三方共享场景（添加第三个共享者c），验证use_count=3时COW正确触发
- **Verification**: `programmatic` + `human-judgment`

## Open Questions
- [x] ShareDiffWithDifferentShapes中data tensor shape同步方案：采用方案A——ShareDiff时shape不匹配则Reshape（代码已实现此方案，与ShareData行为对称）
