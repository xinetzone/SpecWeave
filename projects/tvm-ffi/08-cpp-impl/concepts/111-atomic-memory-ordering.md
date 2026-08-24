---
type: Concept
title: "视角111：原子内存序"
description: "解析 TVM FFI 对象系统的原子内存序设计：combined_ref_count 64位合并计数、IncRef 使用 __ATOMIC_RELAXED、DecRef 使用 __ATOMIC_RELEASE + __atomic_thread_fence(__ATOMIC_ACQUIRE)、TryPromoteWeakPtr 使用 CAS __ATOMIC_ACQ_REL，以及 MSVC 与 GCC/Clang 的平台差异。"
tags:
  - cpp-impl
  - atomic
  - memory-order
  - reference-counting
  - thread-safety
  - npu
generated: 2026-08-23
verified: true
status: stable
sources:
  - facts: F-013, F-019, F-105, F-106, F-122, F-123
  - code:
    - include/tvm/ffi/object.h
    - include/tvm/ffi/c_api.h
    - src/ffi/object.cc
    - 3rdparty/libbacktrace/internal.h
---

# 视角111：原子内存序

## 概述

TVM FFI 的对象生命周期管理建立在精细的原子内存序选择之上。`Object` 类将强引用计数和弱引用计数合并为一个 64 位原子变量 `combined_ref_count`，使用不同的内存序语义处理引用计数的增加、减少和弱引用提升。设计的核心原则是：**增加引用使用 Relaxed 序（无同步开销），减少引用使用 Release 序（保证析构前的写入可见），实际析构前插入 Acquire 栅栏（保证获取所有已释放引用的写入）**。这种分层内存序在保证线程安全的同时最小化了原子操作的性能开销。

## combined_ref_count 合并计数

`TVMFFIObject` 结构体（`c_api.h:86-90`）包含 `type_index_`（int32_t）和 `refcount_`（int32_t）。但 C++ 层的 `Object` 类（`object.h:127-138`）使用更复杂的 `combined_ref_count` 字段，将强引用计数和弱引用计数打包到一个 64 位变量中：

```cpp
Object() {
  header_.combined_ref_count = 0;
  header_.type_index = 0;
  header_.__padding = 0;
  header_.__ensure_align = 0;
}
```

合并计数的关键常量包括：
- `kCombinedRefCountStrongOne`：强引用计数的增量单位
- `kCombinedRefCountWeakOne`：弱引用计数的增量单位
- `kCombinedRefCountBothOne`：强+弱各为1的合并值
- `kCombinedRefCountMaskUInt32`：低32位掩码，用于提取强引用计数

强引用计数和弱引用计数分别占据 64 位变量的不同位段，可以通过一次原子操作同时修改两者，也可以通过位掩码单独读取其中之一。

## IncRef：Relaxed 原子加

`IncRef()` 方法（`object.h:245-252`）增加强引用计数：

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

GCC/Clang 下使用 `__atomic_fetch_add` with `__ATOMIC_RELAXED`，MSVC 下使用 `_InterlockedIncrement64`（隐含全屏障）。选择 Relaxed 序的原因是：增加引用计数不需要与其他线程建立 happens-before 关系——只要对象已经存活（调用者已持有引用），原子递增本身保证计数的原子性即可，不需要内存同步。

`IncWeakRef()`（`object.h:289-297`）同样使用 `__ATOMIC_RELAXED`，因为弱引用增加也不涉及对象数据的访问同步。

## use_count：Relaxed 加载

`use_count()` 方法（`object.h:189-200`）读取强引用计数：

```cpp
uint64_t use_count() const {
#ifdef _MSC_VER
  return ((reinterpret_cast<const volatile uint64_t*>(
             &header_.combined_ref_count))[0]) &
         kCombinedRefCountMaskUInt32;
#else
  return __atomic_load_n(&(header_.combined_ref_count), __ATOMIC_RELAXED) &
         kCombinedRefCountMaskUInt32;
#endif
}
```

注释说明"only need relaxed load of counters"（`object.h:190`）——读取引用计数仅用于调试或 `unique()` 判断，不需要建立同步关系。

## DecRef：Release-Acquire 协议

`DecRef()` 方法（`object.h:300-363`）是内存序设计最精妙的部分。GCC/Clang 实现分为三个阶段：

### 阶段一：Release 原子减

```cpp
uint64_t count_before_sub = __atomic_fetch_sub(
    &(header_.combined_ref_count),
    kCombinedRefCountStrongOne,
    __ATOMIC_RELEASE);
```

使用 `__ATOMIC_RELEASE` 确保当前线程在 `DecRef` 之前对对象数据的所有写入，对后续执行 Acquire 的线程可见。这是"释放"语义——当引用计数降至零时，其他线程必须能看到该对象的完整状态。

### 阶段二：快路径——两个计数同时归零

```cpp
if (count_before_sub == kCombinedRefCountBothOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskBoth);
  }
}
```

当强引用和弱引用都为1时，这次递减使两者同时归零。在调用 deleter 之前插入 `__atomic_thread_fence(__ATOMIC_ACQUIRE)`，与其他线程的 Release 操作配对，确保当前线程能看到所有已释放引用的写入。然后调用 deleter 同时销毁对象和内存。

### 阶段三：慢路径——强引用归零但弱引用存活

```cpp
else if ((count_before_sub & kCombinedRefCountMaskUInt32) ==
         kCombinedRefCountStrongOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskStrong);
  }
  if (__atomic_fetch_sub(&(header_.combined_ref_count),
                         kCombinedRefCountWeakOne,
                         __ATOMIC_RELEASE) == kCombinedRefCountWeakOne) {
    __atomic_thread_fence(__ATOMIC_ACQUIRE);
    if (header_.deleter != nullptr) {
      header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskWeak);
    }
  }
}
```

强引用归零时先调用 Strong deleter 执行对象析构（但不释放内存），然后递减弱引用计数。如果弱引用也归零，再次通过 Release-Acquire 协议调用 Weak deleter 释放内存。两阶段删除确保持有弱引用的线程仍可安全访问对象头（但不能访问对象数据）。

MSVC 实现（`object.h:301-330`）使用 `_InterlockedDecrement64` 和 `_InlineInterlockedAdd64`，这些函数隐含全屏障。注释说明"full barrier is implicit in InterlockedDecrement"（`object.h:311`）和"full barrier is implicit in InterlockedAdd"（`object.h:317`）。

## TryPromoteWeakPtr：CAS 循环

`TryPromoteWeakPtr()`（`object.h:258-286`）尝试将弱引用提升为强引用，使用比较并交换（CAS）循环：

```cpp
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
```

CAS 成功使用 `__ATOMIC_ACQ_REL`（同时具有 Acquire 和 Release 语义），失败使用 `__ATOMIC_RELAXED`。注释解释了 CAS 的必要性（`object.h:275-277`）："must do CAS to ensure that we are the only one that increases the reference count, avoid condition when two threads tries to promote weak to strong at same time or when strong deletion happens between the load and the CAS"。

## DecWeakRef：弱引用释放

`DecWeakRef()`（`object.h:366-384`）在弱引用归零时释放内存：

```cpp
if (__atomic_fetch_sub(&(header_.combined_ref_count),
                       kCombinedRefCountWeakOne,
                       __ATOMIC_RELEASE) == kCombinedRefCountWeakOne) {
  __atomic_thread_fence(__ATOMIC_ACQUIRE);
  if (header_.deleter != nullptr) {
    header_.deleter(&(this->header_), kTVMFFIObjectDeleterFlagBitMaskWeak);
  }
}
```

与 `DecRef` 的慢路径相同的 Release-Acquire 协议。

## 第三方 libbacktrace 的原子使用

FFI 内嵌的 libbacktrace 库（`3rdparty/libbacktrace/internal.h:87-96`）也使用类似的原子原语：

```cpp
#define backtrace_atomic_load_pointer(p) \
    __atomic_load_n((p), __ATOMIC_ACQUIRE)
#define backtrace_atomic_store_pointer(p, v) \
    __atomic_store_n((p), (v), __ATOMIC_RELEASE)
```

这些用于回溯数据的延迟初始化，使用标准的 Acquire-Release 配对。

## NPU建议

在 NPU（神经网络处理单元）等异构计算环境中，原子内存序的设计需要特别考虑：

1. **Relaxed 序的适用性**：NPU 侧的引用计数操作如果仅涉及计数原子性而不涉及设备内存同步，可以继续使用 `__ATOMIC_RELAXED`。但如果引用计数保护的是设备端资源（如 NPU 内存句柄、命令队列），需要评估是否需要更强的内存序来保证主机-设备间的可见性。

2. **Release-Acquire 在设备侧的映射**：NPU 编译器和运行时可能不直接支持 C++ 原子内存序。建议在 NPU 绑定层将 `__ATOMIC_RELEASE`/`__ATOMIC_ACQUIRE` 映射到设备侧的 fence/barrier 指令（如 `__threadfence_system()` 或等效的 NPU 同步原语），确保析构前的写入对设备可见。

3. **合并计数的优势**：`combined_ref_count` 将强/弱计数打包为单个 64 位原子变量的设计在 NPU 场景下尤为有利——设备端原子操作通常比主机端更昂贵，单次 64 位原子操作比两次 32 位操作效率更高。

4. **Deleter 的设备同步**：当 deleter 释放 NPU 内存时，Acquire 栅栏应确保所有待处理的 NPU 命令已完成。建议在 deleter 中插入设备端同步（如 stream synchronize）后再释放内存，避免设备仍在访问已释放的资源。

5. **弱引用的设备端限制**：NPU 侧通常不建议使用弱引用，因为弱引用提升的 CAS 循环在设备端可能导致活锁或性能问题。建议设备端只使用强引用。

6. **无锁算法的可移植性**：如果 NPU 工具链不支持 `__atomic_compare_exchange_n`，需要为 `TryPromoteWeakPtr` 提供基于设备侧自旋锁的替代实现。

## 设计分析

TVM FFI 的原子内存序设计体现了对 C++ 内存模型的深刻理解。Relaxed-Release-Acquire 的分层选择精确匹配了引用计数各操作的同步需求：IncRef 只需要原子性（多个线程同时递增计数不丢失），不需要顺序同步；DecRef 需要 Release 来保证析构前的写入可见；deleter 前的 Acquire 栅栏确保看到所有 Release 的写入。这种设计比全屏障（seq_cst）性能更好，比完全不同步更安全。64 位合并计数设计将强/弱引用的更新合并为单次原子操作，减少了原子操作次数，也使得两阶段删除（先析构对象数据，后释放内存）的实现更加简洁。MSVC 与 GCC/Clang 的平台分支确保了在不同编译器下的正确行为，同时在支持精细内存序的平台上获得最优性能。

## 相关概念

- [112 Arena 分配器](112-arena-allocator.md)：与引用计数互补的内存管理策略
- [013 内存所有权模型](/01-architecture/concepts/013-memory-ownership-model.md)：引用计数与对象生命周期
- [046 TLS 错误传播](/03-functions/concepts/046-tls-error-propagation.md)：线程局部存储与线程安全
- [110 Unsafe 操作](110-unsafe-operations.md)：ObjectUnsafe 中的原子引用计数操作
