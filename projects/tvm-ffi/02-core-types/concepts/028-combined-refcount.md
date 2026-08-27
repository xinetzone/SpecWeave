---
type: Concept
title: "视角028：组合引用计数"
description: "深入分析 TVMFFIObject 的 64 位组合引用计数机制，强引用（低32位）与弱引用（高32位）的原子打包操作、两阶段删除协议、CAS 弱提升循环，以及在 NPU 异构计算环境中的适配建议。"
tags:
  - core-types
  - reference-counting
  - weak-ptr
  - atomic
  - memory-management
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-013, F-019, F-086
  - code:
    - include/tvm/ffi/c_api.h
    - include/tvm/ffi/object.h
---

# 视角028：组合引用计数

## 概述

TVM FFI 使用 64 位组合引用计数管理堆对象生命周期。`TVMFFIObject.combined_ref_count` 字段将强引用计数和弱引用计数打包到单个原子变量中：低 32 位为强引用计数，高 32 位为弱引用计数。这种设计使得增加强引用或弱引用都只需一次原子加法，同时支持两阶段删除协议——强引用归零调用析构函数，弱引用归零释放内存。

## 组合计数布局

### 位域划分

```
 63                      32 31                       0
+-------------------------+-------------------------+
|    弱引用计数 (32位)     |    强引用计数 (32位)     |
+-------------------------+-------------------------+
```

### 关键常量

定义在 `object.h:62-68`：

```cpp
constexpr uint64_t kCombinedRefCountWeakOne = static_cast<uint64_t>(1) << 32;   // 0x100000000
constexpr uint64_t kCombinedRefCountStrongOne = 1;                              // 0x000000001
constexpr uint64_t kCombinedRefCountBothOne = kCombinedRefCountWeakOne |
                                              kCombinedRefCountStrongOne;      // 0x100000001
constexpr uint64_t kCombinedRefCountMaskUInt32 = (static_cast<uint64_t>(1) << 32) - 1; // 0xFFFFFFFF
```

### 初始状态

新对象通过 `make_object` 创建后，`combined_ref_count = kCombinedRefCountBothOne`，即强=1、弱=1。弱引用从 1 开始是因为对象自身持有一个隐式弱引用，保证在强引用全部释放后、弱引用释放前，对象头（包含 `combined_ref_count` 本身）仍然有效。

## 强引用操作

### IncRef

`Object::IncRef()`（`object.h:245-252`）原子递增强引用计数：

```cpp
void IncRef() {
#ifdef _MSC_VER
  _InterlockedIncrement64(
      reinterpret_cast<volatile __int64*>(&header_.combined_ref_count));
#else
  __atomic_fetch_add(&(header_.combined_ref_count), 1, __ATOMIC_RELAXED);
#endif
}
```

递增步长为 `kCombinedRefCountStrongOne`（即 1），只影响低 32 位，高 32 位（弱引用计数）不变。使用 `__ATOMIC_RELAXED` 内存序，因为递增操作不需要与其他内存访问建立 happens-before 关系——只要原子性即可。

### DecRef

`Object::DecRef()`（`object.h:300-363`）是引用计数系统最复杂的操作，处理三种情况：

#### 情况1：强=1 且 弱=1（BothOne 快速路径）

```cpp
uint64_t count_before_sub = __atomic_fetch_sub(
    &(header_.combined_ref_count),
    kCombinedRefCountStrongOne, __ATOMIC_RELEASE);
if (count_before_sub == kCombinedRefCountBothOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskBoth);
  }
}
```

当递减前强=1、弱=1时，递减后两者都归零。这是最常见的情况（对象只有一个所有者），通过一次原子减法和一次 deleter 调用完成析构和内存释放。

#### 情况2：强=1 但 弱>1（两阶段删除）

```cpp
else if ((count_before_sub & kCombinedRefCountMaskUInt32) ==
         kCombinedRefCountStrongOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskStrong);
  }
  if (__atomic_fetch_sub(&(header_.combined_ref_count),
                         kCombinedRefCountWeakOne, __ATOMIC_RELEASE) ==
      kCombinedRefCountWeakOne) {
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    if (header_.deleter != nullptr) {
      header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskWeak);
    }
  }
}
```

当强引用归零但仍有弱引用时：
1. 调用 deleter 并传入 `Strong` 标志，执行 C++ 析构函数（释放资源，但不释放内存）。
2. 递减隐式弱引用（初始的那个弱引用）。
3. 如果弱引用也归零（只剩隐式弱引用），再次调用 deleter 并传入 `Weak` 标志，释放内存。
4. 如果还有其他弱引用（来自 `WeakObjectPtr`），内存保留，直到最后一个弱引用释放。

#### 情况3：强>1（普通递减）

如果递减前强引用计数 > 1，仅递减，不触发删除。其他强引用持有者仍然保证对象存活。

### use_count

`Object::use_count()`（`object.h:190-201`）返回当前强引用计数：

```cpp
uint64_t use_count() const {
  return __atomic_load_n(&(header_.combined_ref_count), __ATOMIC_RELAXED) &
         kCombinedRefCountMaskUInt32;
}
```

使用 `__ATOMIC_RELAXED` 加载并掩码提取低 32 位。注意此值可能在多线程环境中立即过时，仅用于调试和 COW 优化提示。

## 弱引用操作

### IncWeakRef

`Object::IncWeakRef()`（`object.h:289-297`）递增高 32 位：

```cpp
void IncWeakRef() {
  __atomic_fetch_add(&(header_.combined_ref_count),
                     kCombinedRefCountWeakOne, __ATOMIC_RELAXED);
}
```

步长为 `0x100000000`，不影响低 32 位。

### DecWeakRef

`Object::DecWeakRef()`（`object.h:366-381`）递减弱引用计数，归零时释放内存：

```cpp
void DecWeakRef() {
  if (__atomic_fetch_sub(&(header_.combined_ref_count),
                         kCombinedRefCountWeakOne, __ATOMIC_RELEASE) ==
      kCombinedRefCountWeakOne) {
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    if (header_.deleter != nullptr) {
      header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskWeak);
    }
  }
}
```

### TryPromoteWeakPtr

`Object::TryPromoteWeakPtr()`（`object.h:258-286`）使用 CAS（Compare-And-Swap）循环尝试将弱引用提升为强引用：

```cpp
bool TryPromoteWeakPtr() {
  uint64_t old_count = __atomic_load_n(
      &(header_.combined_ref_count), __ATOMIC_RELAXED);
  while ((old_count & kCombinedRefCountMaskUInt32) != 0) {
    uint64_t new_count = old_count + kCombinedRefCountStrongOne;
    if (__atomic_compare_exchange_n(
            &(header_.combined_ref_count), &old_count, new_count, true,
            __ATOMIC_ACQ_REL, __ATOMIC_RELAXED)) {
      return true;
    }
  }
  return false;
}
```

CAS 循环是必要的，因为：
1. 两个线程可能同时尝试提升同一个弱引用。
2. 在加载计数和 CAS 之间，另一个线程可能释放了最后一个强引用，导致对象进入析构阶段。
3. CAS 确保只有一个线程成功提升，且如果强引用已归零（对象正在析构），提升失败。

如果强引用计数为 0（低 32 位为 0），循环不执行，返回 false，表示对象已死亡。

## WeakObjectPtr 的实现

`WeakObjectPtr<T>`（`object.h:647-777`）利用上述原语实现弱引用：

### lock()

```cpp
ObjectPtr<T> lock() const {
  if (data_ != nullptr && data_->TryPromoteWeakPtr()) {
    return ObjectPtr<T>(data_);
  }
  return ObjectPtr<T>(nullptr);
}
```

尝试提升弱引用。成功则返回强引用 `ObjectPtr`，失败返回空指针。

### 析构

```cpp
~WeakObjectPtr() {
  if (data_ != nullptr) data_->DecWeakRef();
}
```

析构时递减弱引用计数。

### expired()

```cpp
bool expired() const {
  return data_ == nullptr || data_->use_count() == 0;
}
```

检查对象是否已过期（强引用归零）。注意这是一个瞬时状态，在多线程环境中 `expired()` 返回 false 不保证后续 `lock()` 成功。

## 内存序分析

组合引用计数使用了多种内存序：

- **IncRef/IncWeakRef**：`RELAXED`。递增不需要同步其他内存访问，因为获取引用的线程已经通过其他方式（如从已有引用拷贝）获得了对象的可见性。
- **DecRef 的 fetch_sub**：`RELEASE`。确保当前线程对对象的所有写入对执行 deleter 的线程可见。
- **deleter 前的 fence**：`ACQUIRE`。与 RELEASE 配对，确保 deleter 看到所有前置写入。
- **TryPromoteWeakPtr 的 CAS**：`ACQ_REL`。成功提升时获取对象可见性，失败时无需特殊语义。

这种精心设计的内存序方案在 x86（TSO 强内存模型）上几乎无额外开销，在 ARM/POWER（弱内存模型）上保证正确性。

## NPU建议

在 NPU（神经网络处理单元）等异构计算环境中使用 TVM FFI 引用计数时，需考虑以下适配建议：

### 1. 原子操作的设备端限制

NPU 设备端（如 Ascend NPU 的 Device 侧代码）通常不支持或效率极低地支持 64 位原子 CAS 操作。建议：
- **引用计数操作集中在 Host 端**：NPU kernel 内部不操作 `combined_ref_count`，张量对象的引用计数由 Host 端 runtime 管理。
- **使用句柄而非裸指针**：NPU kernel 通过整数句柄引用对象，Host 端维护句柄到对象的映射，避免设备端直接访问对象头。
- **批量引用计数**：如果 NPU 调度需要异步持有对象引用，在提交任务前由 Host 端批量 IncRef，任务完成后批量 DecRef，避免在中断或 DMA 回调中执行原子操作。

### 2. 弱引用的 NPU 场景

NPU 编译缓存和 kernel 缓存适合使用弱引用：
- 编译后的 kernel 对象可以被 `WeakObjectPtr` 持有，当没有强引用时自动析构释放 Device 内存。
- `TryPromoteWeakPtr` 的 CAS 循环应始终在 Host 端执行，不涉及 NPU 设备。
- NPU 内存池可以利用两阶段删除特性：强删除阶段释放 Device 端显存（通过 deleter 的 Strong 标志），弱删除阶段释放 Host 端对象内存。

### 3. 内存序与 NPU DMA

当 NPU 通过 DMA 异步访问对象数据时：
- DecRef 的 RELEASE 语义应与 DMA 完成同步。在提交 DMA 前 IncRef，在 DMA 完成回调中 DecRef。
- 不要在 DMA 进行中让强引用归零——deleter 可能在 DMA 完成前释放底层存储。
- 对于 NPU 张量对象，建议在 deleter 的 Strong 阶段调用 `rtStreamSynchronize` 或等价操作，确保所有挂起的 NPU 操作完成后再释放显存。

### 4. 跨 PE 引用计数

在多 NPU PE（Processing Element）环境中：
- 避免多个 PE 原子竞争同一个 `combined_ref_count`，这会导致缓存行颠簸和 PCIe 流量。
- 采用"归属 PE"策略：对象由创建它的 PE 管理引用计数，其他 PE 通过消息传递请求增减引用，由归属 PE 串行化原子操作。
- 对于只读共享对象（如编译后的模型权重），可以使用分布式引用计数或显式生命周期管理，避免高频跨 PE 原子操作。

### 5. 实时性考量

NPU 推理任务通常有严格的延迟要求。引用计数的 DecRef 可能触发 deleter（包括内存释放和 NPU 资源回收），引入不确定延迟：
- 在热路径（推理执行期间）避免最后一个引用释放。
- 使用后台线程执行 DecRef 和 deleter，将延迟移出关键路径。
- 对象池化结合引用计数，使 deleter 将对象归还池而非真正释放，避免 `malloc`/`free` 的不确定延迟。

## 设计分析

组合引用计数的设计体现了多个高级技术：

1. **单字打包**：强/弱引用打包到一个 64 位原子变量，IncRef/DecRef 仅需一次原子操作，比双计数器方案减少一半原子开销。
2. **两阶段删除**：强删除调用析构函数但保留内存，使弱引用可以安全检测对象存活状态而不解引用已析构对象；弱删除最终释放内存。
3. **隐式弱引用**：对象创建时弱引用从 1 开始，这个"自弱引用"确保强引用归零后对象头仍然有效，允许弱引用安全检查 `use_count()`。
4. **CAS 提升循环**：处理弱提升与强释放的竞态条件，是无锁编程的经典模式。
5. **内存序优化**：RELAXED/RELEASE/ACQUIRE 的分层使用在正确性和性能间取得平衡。
6. **快速路径优化**：`BothOne` 快速路径处理最常见的单所有者场景，仅一次原子减法加一次 deleter 调用。

## 相关概念

- [027 TVMFFIObject 对象头](027-object-header.md)：combined_ref_count 的存储位置
- [031 Deleter 析构机制](031-deleter.md)：两阶段删除的详细分析
- [030 ObjectRef 包装器](030-object-ref-wrapper.md)：ObjectPtr 中的 IncRef/DecRef
- [018 Any 拥有语义](018-any-owning.md)：Any 如何通过阈值判断触发引用计数
